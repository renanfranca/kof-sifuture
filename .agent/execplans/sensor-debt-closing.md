# R7: fechamento da dívida dos sensores

## Purpose and success

O plano mestre "Pagamento da dívida dos sensores antes do M3" foi executado em
lotes mesclados um a um (PRs #28 a #31, #33 e #34). Cada lote provou lint, CPD e
mutação só nos arquivos que tocou. Este plano é o R7: provar, numa só rodada e
sobre o repositório inteiro, que a dívida está paga, e registrar o fechamento
para liberar o M3 (hooks reais no Codex CLI).

Sucesso, observável:

- `npm run sensors:debt` com lint e CPD em `PASS (0 findings)` sobre todos os
  arquivos Kof;
- o KofMut sobre **toda** a produção (`src/main/kof`, 44 arquivos) termina
  `complete`, com todo candidato morto, 0 sobreviventes e 0 timeouts;
- `npm run check` e `npm run check:task` passam no Kof 0.7.0;
- testes Kof JVM e JS e `scripts/kof-sensors/test` passam também no Kof 0.6.4,
  a versão mínima que `docs/desenvolvimento.pt_BR.md:97` promete;
- o `EXECPLAN.md` marca o R7 e o plano mestre como concluídos.

Nenhum código de produção, teste ou script muda. Só registros.

## Context and limits

Estado em 19/11/2026, `main` `06eab3d`, medido no planejamento:

- `bash -lic 'npm run sensors:debt'`: `82 Kof files`, `SENSOR lint: PASS (0
  findings)`, `SENSOR dup: PASS (0 findings)`.
- `git ls-files 'src/main/kof/*.kf' | wc -l`: 44.
- `kof` do `PATH` é o 0.7.0 (`readlink -f ~/.local/bin/kof` termina em
  `kof-0.7.0-linux-x86_64/bin/kof`). O 0.8.0 está em `~/.local/share/kof/` e não
  foi testado com o KofMut; não usar.
- `kof-mut` instalado em `~/.local/bin/kof-mut` a partir de `kof-mut` `6338a56`
  e verificado com `scripts/kof-sensors/verify-kofmut` (fixture `detected` morta,
  `survived` sobrevivente). O suporte a `enum` do KofMut já está mesclado
  (`kof-mut` PR #3); cinco arquivos de produção declaram `enum`.
- O Kof 0.6.4 **não está instalado**. A distribuição oficial é o asset
  `kof-0.6.4-linux-x86_64.tar.gz` do release `kof-0.6.4-linux-x86_64` em
  `KofLang/Kof4j`, com digest
  `sha256:c1ffdaa9222237f9e0ed254d88683306d75c0280f3163fc9a35187ca3d01f136`
  (388.067.995 bytes).
- `mvn` (3.10.1) e Java 25 vêm do SDKMAN e só existem em shell de login: todo
  comando que chama sensores ou Maven roda com `bash -lic '…'`.
- Gitleaks 8.30.1 está em `~/.local/bin` (instalado no R6, exigido pelo `check`).

Por que o `npm run check` não serve como prova de mutação aqui: o passo
`mutation` só muta a produção alterada contra a `main`
(`scripts/check.mjs:56-64`). Numa branch de registros, o resultado esperado é
`SKIP (no production Kof file changed against main)`. A prova de produção
inteira é a rodada direta do KofMut no M1.

Tamanho esperado da rodada: os lotes registraram 164, 265, 119 e 166 candidatos
(seções A1 de `.agent/validation/sensor-debt-payoff.md`), mais o lote 1 e o
piloto do `ControlsGuide`. Estimativa: de 900 a 1000 candidatos, de 2 a 3 horas
com `maxParallelMutants: 1` (`kof-mut.json`) e entre 7 e 10 segundos por
candidato. Cada candidato tem `commandTimeoutMs: 30000`; máquina carregada
produz timeouts falsos (o lote 2 registrou load 22 com jornadas em paralelo).

Problema conhecido e fora deste escopo: as capturas de página inteira das
jornadas não são determinísticas no Chrome 158 (issue #35). O `check:task` valida
por asserções e não é afetado; este plano não usa comparação de pixels.

### Limites

- Não mudar nada em `src/`, `tests/`, `scripts/`, `kof-mut.json`, `kof.toml`,
  `docs/` nem `.github/`.
- Não editar as cópias arquivadas em `.agent/sensor-plans/`.
- Não trocar o link `~/.local/bin/kof`; o 0.6.4 entra só por `KOF=…` e
  `KOF_JAR`/`-Dkof.jar` quando o comando pedir.
- Evidência em `.agent/tmp/debt-closing/`. Confirmar que `.agent/tmp/` está em
  `.git/info/exclude` (o R6 acrescentou); se não estiver, acrescentar.

## Risks

- **Sobrevivente na produção inteira.** Possível se um lote posterior mudou um
  arquivo já provado (por exemplo `Overlap.kf` e `Course.kf`, criados no lote 3)
  sem rodar o KofMut nele de novo. Se aparecer, **parar antes do commit**:
  registrar cada mutante (`id`, arquivo, linha, substituto) no aceite e reportar.
  Corrigir exige TDD e é decisão do usuário.
- **Timeout falso por carga.** Não rodar jornadas, builds nem outro KofMut
  durante o M1. Se houver timeout, rodar de novo só os arquivos afetados com a
  máquina ociosa e registrar as duas rodadas.
- **Download do 0.6.4 corrompido ou diferente.** Conferir o SHA-256 do arquivo
  baixado contra o digest acima antes de extrair; se divergir, parar.

## Milestones

### M0. Ambiente

1. `git status --porcelain --untracked-files=all` só com este plano;
   `.agent/tmp/` em `.git/info/exclude`.
2. Instalar o 0.6.4 ao lado do 0.7.0:

        mkdir -p .agent/tmp/debt-closing/kof064
        gh release download kof-0.6.4-linux-x86_64 -R KofLang/Kof4j \
          --pattern 'kof-0.6.4-linux-x86_64.tar.gz' --dir .agent/tmp/debt-closing/kof064
        sha256sum .agent/tmp/debt-closing/kof064/kof-0.6.4-linux-x86_64.tar.gz
        tar -xzf .agent/tmp/debt-closing/kof064/kof-0.6.4-linux-x86_64.tar.gz -C ~/.local/share/kof/

   Esperado: o SHA-256 é `c1ffdaa9…f136`; existe
   `~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof` e
   `~/.local/share/kof/kof-0.6.4-linux-x86_64/lib/kof.jar`. Se o tar extrair com
   outro nome de pasta, registrar o caminho real e usá-lo nos comandos seguintes.
3. `readlink -f ~/.local/bin/kof` continua no 0.7.0; `which kof-mut` resolve.
4. `bash -lic 'npm run sensors:debt' > .agent/tmp/debt-closing/m0-debt.txt` e
   ler: lint e dup `PASS (0 findings)`, `82 Kof files`.

### M1. KofMut em toda a produção

    git ls-files 'src/main/kof/*.kf' | python3 -c 'import json,sys; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))' > .agent/tmp/debt-closing/scope.json
    kof-mut run --project . --files .agent/tmp/debt-closing/scope.json \
      --config kof-mut.json --report-dir .agent/tmp/debt-closing/m1 \
      --run-id "$(uuidgen)" > .agent/tmp/debt-closing/m1.log 2>&1

Rodar com a máquina ociosa e anotar início e fim. Ler o `reportPath=` do log e,
no relatório JSON: `status`, limitações, `counts` (candidatos, executados, mortos,
sobreviventes, timeouts, erros, pendentes) e `discardedCandidates`. Montar uma
tabela por arquivo (candidatos e mortos).

Esperado: exit 0, `complete`, 0 limitações, `killed == candidates`, 0
sobreviventes, 0 timeouts, 44 arquivos no escopo. Se não, ver Risks.

### M2. Kof 0.6.4

Com `K=~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof`:

    KOF=$K node scripts/kof-tests.mjs --target jvm
    KOF=$K node scripts/kof-tests.mjs --target js
    bash -lic "KOF=$K scripts/kof-sensors/test"

Esperado: `0 failed of 409 tests` nos dois alvos (409 é a contagem desde o lote
da UI; se for outra, conferir com a do 0.7.0 no M3 e registrar), e o
`scripts/kof-sensors/test` com exit 0. Registrar a versão de cada execução
(`$K` e o `lib/kof.jar` usado; ver `scripts/kof-sensors/README.md`).

### M3. Validação no 0.7.0 e registros

1. Validação final (seção Validation).
2. Nova seção "R7, fechamento (data)" em
   `.agent/validation/sensor-debt-payoff.md`: ambiente (versões de Kof, KofMut
   com id da imagem, Chrome, Maven), tabela por arquivo do M1, resultados do M2,
   aceite A1 a A6 com o observado e um resumo da dívida inteira (achados de lint e
   CPD, sobreviventes e casos de teste do R0 até aqui, a partir das seções já
   registradas).
3. `EXECPLAN.md`, seção "Pagamento da dívida dos sensores antes do M3": marcar
   `- [x] R7` com uma linha de resumo e link para este plano, e registrar que o
   plano mestre está concluído e que o próximo marco é o M3. Citar a issue #35
   como pendência conhecida.
4. Atualizar o `Progress` deste plano.

## Progress

- [x] M0. Ambiente (0.6.4 instalado e conferido, dívida 0). SHA-256 e tamanho
  conferem; `~/.local/share/kof/kof-0.6.4-linux-x86_64` (`kof version`: 0.6.4);
  `~/.local/bin/kof` segue no 0.7.0; `sensors:debt`: 82 arquivos, lint e dup
  `PASS (0 findings)` (`m0-debt.txt`).
- [x] M1. KofMut em toda a produção (19/11, 21:16 a 21:58, 41min50s):
  `complete`, 44 arquivos, 802 candidatos, 802 mortos, 0 sobreviventes, 0
  timeouts, 0 limitações, 0 descartes. Desvio aprovado pelo usuário: rodou com
  `maxParallelMutants: 4` numa cópia temporária da config
  (`.agent/tmp/debt-closing/kof-mut-par4.json`), em vez de 1; a primeira rodada
  com 1 foi interrompida aos 10 min. Load chegou a 24,5 em 32 núcleos, sem
  timeout.
- [x] M2. Kof 0.6.4: JVM e JS com `0 failed of 409 tests`;
  `scripts/kof-sensors/test` exit 0 (42 testes, `BUILD SUCCESS`).
- [x] M3. Validação final e registros: `unittest`, `test:sensors`,
  `sensors:debt`, `check`, `check:task` e `git diff --check` com exit 0; seção
  "R7, fechamento" no aceite e R7 marcado no `EXECPLAN.md`.

## Validation

Critérios de aceite. A coluna "Verificação" é o planejado; o observado vai para o
aceite.

| # | Fonte | Contexto → ação → resultado esperado | Verificação | Evidência esperada |
| --- | --- | --- | --- | --- |
| A1 | plano mestre, R7 e A3 | `main` com os seis lotes → `sensors:debt` → lint e dup `PASS (0 findings)`, `N Kof files` igual a `git ls-files '*.kf' \| wc -l` | **ler a saída**: o comando sai 0 mesmo com achados; `UNAVAILABLE` (sem `mvn`) não é PASS | `m0-debt.txt`, `final-debt.txt` |
| A2 | plano mestre, R7 e A4 | produção inteira → KofMut → `complete`, `killed == candidates`, 0 sobreviventes, 0 timeouts, 0 limitações. Distingue: só a rodada conjunta vê um arquivo que mudou depois do lote que o provou | M1 | relatório JSON e tabela por arquivo |
| A3 | `scripts/check.mjs` | `npm run check` → `CHECK: PASS`; `mutation` em SKIP é esperado (nada de produção mudou contra a `main`), coberto pela A2 | validação final | saída do `check` |
| A4 | plano mestre, R7 | `npm run check:task` → `CHECK:TASK: PASS`, `kof tests` JVM e JS e as sete jornadas `browser:*` em PASS | validação final | saída do `check:task` |
| A5 | `docs/desenvolvimento.pt_BR.md:97` e plano mestre, R7 | Kof 0.6.4 → testes JVM e JS e `scripts/kof-sensors/test` → `0 failed of N tests` com o mesmo N do 0.7.0, e exit 0. Distingue: um recurso do 0.7.0 usado por engano compila no 0.7.0 e falha no 0.6.4 | M2 | logs com o caminho do `kof` usado |
| A6 | Limites | `git diff --name-only main` lista só este plano, `EXECPLAN.md` e `.agent/validation/sensor-debt-payoff.md`; `git status --porcelain --untracked-files=all` sem `.agent/tmp/` | rodar | lista no aceite |

Validação final, nesta ordem, com o `kof` 0.7.0 do `PATH`. O commit só acontece
se todos passarem:

    python3 -m unittest discover -s tests -p 'test_*.py'
    bash -lic 'npm run test:sensors'
    bash -lic 'npm run sensors:debt'
    bash -lic 'npm run check'
    bash -lic 'npm run check:task'
    git diff --check

Esperado:

- todos com exit 0;
- `sensors:debt` com lint e dup em `PASS (0 findings)` (ler a saída);
- `npm run check` com `CHECK: PASS`;
- `npm run check:task` com `CHECK:TASK: PASS`;
- a seção de registros entra depois da validação (só texto); rodar de novo
  `bash -lic 'npm run docs:sensor'` e `git diff --check` sobre ela.

Obrigações do executor antes de entregar:

- Conferir de novo cada expectativa contra a fonte citada, separado de conferir
  se o comando a demonstra.
- Para cada critério de A1 a A6, registrar no aceite o comando, o resultado
  observado e onde está a evidência. Suíte verde sozinha não prova cada critério.
- Registrar antes da entrega qualquer critério não verificado ou falha, sem
  apresentá-los como atendidos. Sobrevivente ou timeout no M1 interrompe a entrega
  antes do commit (ver Risks).
