# Check de tipos sobre todos os módulos de produção

## Purpose and success

Issue #44: o check de tipos do projeto (`python3 scripts/kof_project.py check
--target jvm|js`, usado pelo `npm run check`, pelo `check:task`, pelo
`checkCommand` do KofMut e pelos hooks do Codex) não vê um módulo de produção
que nada importa. Um erro de tipo num subpacote novo passa com exit 0.

Depois deste trabalho:

- com `src/main/kof/sifuture/probe/Probe.kf` contendo só um erro de tipo, o
  check sai com exit 1 e um diagnóstico `ERROR` em `Probe.kf`, em JVM e em JS;
- o mesmo arquivo sem o erro continua dando exit 0;
- o check do projeto atual continua passando, e o check de cada fixture de
  navegador (`--fixture`) continua igual;
- o Stop dos hooks do Codex deixa de precisar da entrada própria
  (`.sensors/ledger/types-entry.kf`), porque o check normal passa a cobrir o
  caso.

## Context and limits

Fatos medidos no planejamento, em 21/11/2026, `main` `5923c7b`:

- `scripts/kof_project.py:67-84`, `prepared_sources`: copia `src/main/kof` para
  uma árvore temporária e, sem `fixture`, escreve `Main.kf` na raiz com uma linha
  só, `import sifuture.*`. `check` (`:161-178`) roda
  `kof check <árvore>/Main.kf --target <alvo> --json`. `build` (`:103`) usa a
  mesma função e a mesma entrada.
- Regra do Kof (`~/projects/kof/docs/language-reference/modules.md`, seção 3.1,
  item 3, "Directory expansion"; checkout `24c99bd31`): `import a.b`, quando
  `a/b/` é uma pasta na raiz do módulo, puxa todos os `.kf` daquela pasta para a
  unidade. Por isso `import sifuture.*` puxa só os arquivos de `sifuture/` e não
  os de `sifuture/<sub>/`. Hoje `sifuture.game` é checado porque arquivos de
  `sifuture/` o importam (por exemplo `src/main/kof/sifuture/Main.kf:3`).
- Pastas com `.kf` hoje: `src/main/kof/sifuture` e
  `src/main/kof/sifuture/game`. Nenhum `.kf` direto em `src/main/kof`. Um único
  `main()`, em `src/main/kof/sifuture/Main.kf:6` (dois `main()` no módulo dariam
  `PKG002`, mesma fonte, seção 3.2).
- Reprodução do M2 do plano dos hooks (`.agent/execplans/codex-sensor-hooks.md`,
  Progress, M2): `Probe.kf` com `Int x = "texto"` deu `checked 1 entry file(s)`
  e exit 0; com uma entrada `import sifuture.*` + `import sifuture.probe.Probe`
  deu `Probe.kf:4:5: ERROR SEM021` e exit 1 em JVM e JS.
- O contorno atual do Stop: `scripts/stop-verdict.mjs:17-34` (`moduleOf`,
  `typeEntry`, `typeCheck`) escreve `.sensors/ledger/types-entry.kf` e passa
  `--fixture` ao `kof_project.py check`. Há também a troca do nome curto do
  diagnóstico (`Probe.kf`) pelo caminho do escopo quando há um único dono
  (testes em `test/sensors/stop-hook.test.mjs`, por exemplo a linha com
  `Probe.kf:4:5: ERROR SEM021`).
- Testes do wrapper: `tests/test_kof_project.py`, com o Kof real do `PATH` e uma
  cópia de `src/main/kof` num projeto temporário (`setUp`). Dois testes já fixam
  o comportamento das fixtures (`test_fixture_check_reports_import_missing_only_from_the_fixture_entry`
  e `test_fixture_check_accepts_a_browser_fixture_of_the_complete_game`).
- Documentação que descreve a entrada: `docs/desenvolvimento.pt_BR.md:333-345`
  e o trecho equivalente de `docs/desenvolvimento.md:343-355`;
  `docs/desenvolvimento.pt_BR.md:154-162` e o equivalente em inglês (Stop dos
  hooks); `SENSORS.md:34-42` (motivo do `types:fixtures`).

### Limites

- Não mudar `build` nem a entrada do build: o app publicado e as jornadas
  continuam compilando a partir de `import sifuture.*`.
- Não mudar o caminho `--fixture`: a fixture continua sendo a entrada inteira.
- Não mudar `.codex/hooks.json`. Ele só aponta para os scripts; mudar o
  manifesto obrigaria o usuário a aprovar os hooks de novo em `/hooks`.
- Não mudar `src/`, os testes Kof, as fixtures, as jornadas, `kof-mut.json` nem
  os limites dos sensores.
- Probes só em projetos temporários dos testes, nunca no checkout.

## Decisions

**Entrada do check com um import por pasta de produção.** Sem `fixture`, o
`check` passa a escrever no `Main.kf` da árvore temporária uma linha
`import <pacote>.*` para cada pasta de `src/main/kof` que tenha `.kf`, em ordem
alfabética (hoje: `import sifuture.*` e `import sifuture.game.*`). A lista vem do
disco a cada execução, então um subpacote novo entra sem ninguém editar nada. O
`build` continua com a entrada atual. Alternativas descartadas: um import por
arquivo (mais linhas, sem ganho, porque a expansão já é por pasta); mudar a
entrada também do build (muda o que o app compila, fora do escopo da issue).

**O Stop dos hooks volta a usar o check normal.** O tier de tipos do Stop deixa
de gerar `types-entry.kf` e chama `kof_project.py check --target <alvo>` sem
`--fixture`. A troca do nome curto do diagnóstico pelo caminho do escopo fica,
se o diagnóstico ainda vier só com o nome do arquivo. Motivo: uma regra só para
"o que o check vê", em vez de duas. Como o manifesto não muda, os hooks
continuam aprovados.

## Risks

- **Pasta de produção com um segundo `main()`** daria `PKG002` no check. Não
  existe hoje. Se aparecer, o check falha com um erro explícito, o que é o
  resultado certo.
- **`.kf` solto na raiz de `src/main/kof`** não entra na lista de imports (o
  pacote vazio é descartado), como já não entrava antes. Não existe hoje.
- **Check mais lento.** A entrada passa a puxar todos os arquivos explicitamente;
  hoje eles já são puxados de forma transitiva, então o custo esperado é o mesmo.
  Medir antes e depois (o planejamento mediu 1,7 s em JVM).

## Milestones

### M1. `check` com todas as pastas de produção, por TDD

Testes novos em `tests/test_kof_project.py`, com o Kof real, no projeto
temporário do `setUp`. O valor esperado vem da issue #44 e da regra de expansão
por pasta do Kof, não do código:

- módulo isolado num subpacote novo, `src/main/kof/sifuture/probe/Probe.kf`
  (`package sifuture.probe`, uma função com `Int x = "texto"`), que nada importa
  → `check(target="jvm")` e `check(target="js")` com exit diferente de 0 e um
  diagnóstico `ERROR` cujo arquivo termina em `Probe.kf`. Este teste precisa
  falhar antes da mudança (hoje dá 0);
- o mesmo `Probe.kf` com `Int x = 7` → exit 0 nos dois alvos. Distingue: uma
  entrada quebrada por outro motivo (import inválido, pasta inexistente)
  falharia aqui também;
- projeto sem mudança → exit 0, como hoje;
- os dois testes de fixture existentes continuam passando sem alteração.

Depois, a implementação em `prepared_sources` ou em `check`, mantendo `build` e
`--fixture` como estão.

Validação:

    python3 -m unittest discover -s tests -p 'test_*.py'
    python3 scripts/kof_project.py check --target jvm
    python3 scripts/kof_project.py check --target js

Esperado: unittest OK; os dois checks do projeto real com exit 0. Registrar o
tempo do check JVM antes e depois.

### M2. Stop dos hooks sem a entrada própria

- `scripts/stop-verdict.mjs`: o tier de tipos chama o check sem `--fixture`;
  remover `typeEntry` e `moduleOf` se nada mais os usar.
- `test/sensors/stop-hook.test.mjs`: ajustar os testes que dependiam da entrada
  própria, sem perder os comportamentos já fixados (tipos falham → testes não
  rodam; diagnóstico com caminho do escopo).
- Conferir, numa cópia temporária do projeto e com uma chamada direta do
  `scripts/stop-sensor.mjs` (payload sintético, registrado assim), que um
  `Probe.kf` com erro de tipo num subpacote novo ainda reprova o tier de tipos e
  que `tests:*` aparecem como `NOT RUN`. Anotar o nome de arquivo que o
  diagnóstico traz.

Validação: `npm run test:sensors`.

### M3. Documentação e registros

- `docs/desenvolvimento.pt_BR.md` e `docs/desenvolvimento.md`: a entrada do check
  importa cada pasta de produção; o build continua com `import sifuture.*`; o
  Stop usa o check normal.
- `SENSORS.md`: ajustar o motivo do `types:fixtures` se o texto deixar de valer
  (o `types:fixtures` continua existindo, porque a fixture é a entrada do build
  das jornadas).
- Registro em `.agent/validation/check-all-production-modules.md`: a reprodução
  antes, os testes novos com o vermelho observado, os tempos e o aceite A1 a A5.
  Entrada no `EXECPLAN.md` com links. O PR deve fechar a #44 (`Closes #44`).

## Progress

- [x] M1. `check` com todas as pastas de produção. Três testes novos em
  `tests/test_kof_project.py`; o de erro de tipo ficou vermelho antes (exit 0
  em JVM e JS) e verde depois; os dois de exit 0 pegaram uma entrada quebrada de
  propósito. CLI real com exit 0; JVM 1,63 s → 1,62 s, JS 0,74 s → 0,75 s.
- [x] M2. Stop dos hooks sem a entrada própria. `typeEntry` e `moduleOf`
  removidos; o teste que fixava o conteúdo de `types-entry.kf` virou o contrato
  "o tier de tipos roda o check normal" (vermelho antes, verde depois).
  `test:sensors` 72/72. Chamada direta numa cópia: `types:jvm FAIL · types:js
  FAIL · tests:jvm NOT RUN · tests:js NOT RUN`; o Kof traz só `Probe.kf`, e o
  Stop o troca por `src/main/kof/sifuture/probe/Probe.kf`.
- [x] M3. Documentação, registros e validação final. Guias em português e
  inglês e `SENSORS.md` ajustados; registro em
  `.agent/validation/check-all-production-modules.md` com A1 a A5; entrada no
  `EXECPLAN.md`. Validação final: unittest 23 OK, `test:sensors` 72/72,
  `CHECK: PASS`, `CHECK:TASK: PASS` com as sete jornadas, `git diff --check`
  limpo. Depois do registro, `docs:sensor` PASS e `git diff --check` limpo.

## Validation

Critérios de aceite. "Verificação" é o planejado; o observado vai para
`.agent/validation/check-all-production-modules.md`.

| # | Fonte | Contexto → ação → resultado esperado | Verificação | Evidência esperada |
| --- | --- | --- | --- | --- |
| A1 | issue #44 | módulo isolado em subpacote novo, com erro só de tipo → check JVM e JS → exit diferente de 0 e `ERROR` em `Probe.kf`. Distingue: o teste falha antes da mudança, porque hoje dá 0 | teste novo do M1, vermelho antes e verde depois | saída do unittest antes e depois |
| A2 | issue #44 | o mesmo módulo sem erro → exit 0. Distingue: separa "o check vê o módulo" de "a entrada quebrou" | teste novo do M1 | saída do unittest |
| A3 | Limites | fixtures e build inalterados: os dois testes de fixture passam sem edição; `git diff main -- scripts/kof_project.py` não toca `build` nem o caminho `--fixture` | unittest; ler o diff | diff no registro |
| A4 | Decisions | o Stop reprova tipos num subpacote novo sem `types-entry.kf`, e os testes não rodam | M2, `test:sensors` e chamada direta com payload sintético | saídas registradas |
| A5 | Limites | `git diff --name-only main` só lista `scripts/kof_project.py`, `tests/test_kof_project.py`, `scripts/stop-verdict.mjs`, `test/sensors/stop-hook.test.mjs`, os dois `docs/desenvolvimento*.md`, `SENSORS.md` (se mudar), `EXECPLAN.md`, o registro e este plano; `.codex/hooks.json` sem diff | `git diff --name-only main` | lista no registro |

Validação final, nesta ordem. O commit só acontece se todos passarem:

    python3 -m unittest discover -s tests -p 'test_*.py'
    npm run test:sensors
    npm run check
    npm run check:task
    git diff --check

Esperado: todos com exit 0; `check` com `CHECK: PASS` (`types:jvm` e `types:js`
PASS com a entrada nova; `mutation` em SKIP, porque nada de produção muda);
`check:task` com `CHECK:TASK: PASS` e as sete jornadas.

Obrigações do executor antes de entregar:

- Conferir de novo cada expectativa contra a fonte citada (issue #44 e a regra de
  expansão por pasta do Kof em `~/projects/kof`), separado de conferir se o teste
  a demonstra.
- Para cada critério de A1 a A5, registrar o comando, o resultado observado e
  onde está a evidência. Suíte verde sozinha não prova cada critério.
- Registrar qualquer critério não verificado ou falha, sem apresentá-los como
  atendidos.
