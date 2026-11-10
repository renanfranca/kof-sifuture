# O `check` compila as fixtures de navegador e pega `import` faltando

## Purpose and success

Hoje o `npm run check` pode dizer PASS com o jogo quebrado para as jornadas de
navegador. No piloto do `ControlsGuide` (PR #26), o `ControlsGuide.kf` usou
`GuideDisclosure` sem `import sifuture.GuideDisclosure`. O `check` passou, e só a
jornada `browser:browser` do `check:task`, bem mais lenta, falhou com
`ControlsGuide.kf:9:5: error: Undefined variable or type: 'GuideDisclosure' [SEM011]`
(`.agent/validation/sensor-debt-payoff.md`, seção "Piloto da UI", C3 a C5).

Sucesso: um passo novo e barato do `check`, `types:fixtures`, verifica os tipos de
cada fixture `tests/*.kf` como entrada real, do mesmo jeito que as jornadas montam o
build. Um `import` faltando em qualquer arquivo alcançado por uma fixture reprova o
`check`, e o sumário mostra qual fixture falhou.

## Context and limits

Por que o `check` atual não pega o erro (observado no planejamento, 10/11, Kof 0.7.0):

- `scripts/kof_project.py` `prepared_sources` (linhas 67-83) copia `src/main/kof`
  para uma pasta temporária e escreve uma entrada `Main.kf` com `import sifuture.*`.
  O curinga carrega todas as classes do pacote. Os passos `types:jvm` e `types:js`
  (`scripts/check.mjs:13-14`) checam essa entrada, então uma classe usada sem
  `import` continua visível.
- As jornadas (`tests/browser*.py`) chamam `served_build(fixture=ROOT / "tests/<x>.kf")`,
  que usa a fixture como `Main.kf`. As fixtures importam classes uma a uma: por
  exemplo, `tests/boss.kf` tem `import sifuture.GameControls`, `import sifuture.GameView`
  e `import sifuture.game.*`. Por isso o build da fixture só enxerga o que cada
  arquivo importa.

Prova feita no planejamento, numa cópia em `/tmp`, sem `kof.toml`, com o
`import sifuture.GuideDisclosure` removido do `ControlsGuide.kf`:

| Entrada `Main.kf` | `kof check Main.kf --target js --json` |
| --- | --- |
| `import sifuture.*` (o que o `check` usa hoje) | `"success":true`, exit 0 |
| cópia de `tests/boss.kf` | `"success":false`, `SEM015 ... 'GuideDisclosure'` e `SEM011` em `ControlsGuide.kf`, exit 1 |

Com a árvore atual, sem remoção, as 6 fixtures passam no `kof check --target js`:

| Fixture | Tempo |
| --- | ---: |
| `tests/boss.kf` | 1262 ms |
| `tests/controls.kf` | 1209 ms |
| `tests/meteor-motion.kf` | 973 ms |
| `tests/stage.kf` | 1318 ms |
| `tests/subchief.kf` | 1362 ms |
| `tests/weapons.kf` | 1221 ms |

Total de cerca de 7,3 s, só o `kof check`, sem o custo de iniciar o Python.

Limites:

- **Não mude nenhum arquivo em `src/main/kof`.** O passo `mutation` do `check` muta
  todo arquivo de produção alterado. Os arquivos de UI têm 193 sobreviventes e
  reprovariam o `check`.
- **Não troque o `import sifuture.*` do `prepared_sources`.** O build do app
  (`kof_project.py build`, usado pela CI na publicação) depende dele. Outra prova
  do planejamento mostrou que 18 dos 25 arquivos de produção usam classes irmãs sem
  `import`, por exemplo `Rules` em `Item.kf`. Exigir `import` em cada arquivo
  obrigaria a mexer em quase toda a produção. Isso fica fora deste trabalho.
- O `kof_project.py` continua em Python, pela decisão de 09/11: o Python fica com o
  `check` de tipos e o `build`. Aqui ele só ganha uma opção, `--fixture`, que reusa o
  `prepared_sources(fixture=...)` já existente. A descoberta das fixtures fica no
  Node, como no `scripts/kof-tests.mjs`.
- Sem dependência npm nova. Sem comentários no código, nos testes nem nas fixtures
  (`AGENTS.md`).

## Decisions

- **Só o alvo JS para as fixtures.** As fixtures só existem para o build KofJS das
  jornadas de navegador (`served_build` sempre usa `--target js`). Checá-las na JVM
  dobraria o custo sem nenhuma jornada que use isso.
- **Descoberta sem lista.** O passo usa todo `tests/*.kf` em ordem alfabética. Uma
  fixture nova entra sozinha, como no `kof-tests.mjs`. Sem nenhuma fixture, o passo
  dá SKIP e não aprova nada, como o `mutation` sem arquivos.
- **Para na primeira fixture que falha.** O passo para na primeira falha, como o
  `runSteps` faz entre passos. O sumário diz `FAIL (tests/<x>.kf: exit 1)`. O
  diagnóstico do Kof sai no stdout acima do sumário.

## Milestones

### M1. `kof_project.py check --fixture <arquivo>`

Comportamento: `python3 scripts/kof_project.py check --target js --json --fixture tests/boss.kf`
checa os tipos com a fixture como `Main.kf`. Sem `--fixture`, nada muda e a entrada
continua `import sifuture.*`.

Edições:
- `scripts/kof_project.py`: `check(..., fixture=None)` passa a fixture para o
  `prepared_sources`, e o subcomando `check` aceita `--fixture`.
- `tests/test_kof_project.py`: testes de comportamento. Use o skill
  `tdd-behavior-autonomous-quiet`, com o RED anotado antes.

Critérios:

| # | Contexto, ação e resultado esperado | Verificação planejada |
| --- | --- | --- |
| F1 | Projeto de teste (cópia de `src/main/kof`, como no `setUp`), com uma fixture que importa `sifuture.ControlsGuide` e com o `import sifuture.GuideDisclosure` removido do `ControlsGuide.kf` da cópia. `check(target="js", fixture=...)` retorna diferente de 0, e o JSON lista `GuideDisclosure` num diagnóstico `ERROR`. Na mesma cópia, `check(target="js")` sem fixture retorna 0. A segunda parte mostra que o teste distingue a entrada da fixture da entrada curinga. | teste novo em `tests/test_kof_project.py` com o Kof real, como `test_real_compile_failure_does_not_publish` |
| F2 | Mesma cópia, sem remover nada: `check(target="js", fixture=<cópia de tests/boss.kf>)` retorna 0. | teste novo ou o mesmo teste, com o caso verde |
| F3 | A CLI aceita `--fixture` e repassa ao `check`. Sem `--fixture`, a chamada antiga continua igual. | `python3 scripts/kof_project.py check --target js --json --fixture tests/boss.kf` com exit 0 na árvore real; os testes atuais continuam verdes |

Validação do marco: `python3 -m unittest discover -s tests -p 'test_*.py'`, verde.
Registre a nova contagem de testes Python.

### M2. Passo `types:fixtures` no `check`

Comportamento: o `npm run check` roda, depois de `types:js`, um passo que checa cada
`tests/*.kf` com `kof_project.py check --target js --json --fixture <arquivo>`.

Edições:
- `scripts/check.mjs`: o passo `types:fixtures`. Ele descobre `tests/*.kf` na raiz,
  em ordem, e roda um processo por fixture, parando no primeiro exit diferente de 0.
  - Resultado PASS quando todas passam.
  - `FAIL (<fixture>: exit N)` na primeira que falha.
  - `SKIP (no browser fixture in tests)` sem fixtures.
- `test/sensors/check.test.mjs`:
  - o teste de ordem dos passos (`check runs the cheap and expensive steps in
    order…`) passa a esperar as chamadas `kof_project check --target js --json
    --fixture tests/<x>.kf`, ou a forma que o stub registrar, logo depois de
    `kof_project check --target js --json`;
  - os testes novos abaixo.

Critérios:

| # | Contexto, ação e resultado esperado | Verificação planejada |
| --- | --- | --- |
| P1 | Projeto stub com `tests/a.kf` e `tests/b.kf`: o `check` chama a fixture `a`, depois `b`, as duas depois de `types:js` e antes de `python tests`. A linha do sumário é `types:fixtures  PASS`. | teste novo em `check.test.mjs`, pelo `calls.log` |
| P2 | Projeto stub com `tests/a.kf` e `tests/b.kf`, e o stub falhando para `a`. O sumário diz `types:fixtures  FAIL (tests/a.kf: exit 1)`, a fixture `b` não é chamada, `python tests` e os passos seguintes ficam `NOT RUN` e o `check` sai com exit 1. | teste novo; o stub do `kof_project` precisa de uma variável `FAIL_` que dependa da fixture |
| P3 | Projeto stub sem `tests/*.kf`: o sumário diz `types:fixtures  SKIP (no browser fixture in tests)`, e o `check` continua. | teste novo |
| P4 | Uma fixture nova, `tests/c.kf`, entra sem editar o `check.mjs`. | coberto pelo P1, porque os nomes vêm do disco; confirme que o código não tem lista fixa |

Validação do marco: `npm run test:sensors`, verde.

### M3. Prova no projeto real e documentação

Edições:
- `SENSORS.md:34`: a frase que lista os passos do `check` passa a citar a checagem de
  tipos das fixtures de navegador (`tests/*.kf`, alvo JS), com o motivo em uma frase.
- O registro de aceite em `.agent/validation/check-fixture-imports.md` (novo), com
  as evidências abaixo.
- `EXECPLAN.md` (raiz): uma linha no progresso do pagamento da dívida, apontando
  para este plano.

Critérios:

| # | Contexto, ação e resultado esperado | Verificação planejada |
| --- | --- | --- |
| R1 | Árvore real limpa: o `npm run check` mostra `types:fixtures  PASS` e `CHECK: PASS`. O `mutation` dá SKIP, porque nenhum arquivo de produção mudou. | rodar e registrar as linhas do sumário e o tempo do passo |
| R2 | **A regressão do piloto.** Remova temporariamente a linha `import sifuture.GuideDisclosure` de `src/main/kof/sifuture/ControlsGuide.kf` e rode `npm run check`. Esperado: `types:jvm  PASS`, `types:js  PASS` (o buraco antigo continua visível), `types:fixtures  FAIL (tests/boss.kf: exit 1)`, com `GuideDisclosure` no diagnóstico acima do sumário, e `CHECK: FAIL at types:fixtures`. Desfaça a remoção e confirme com `git diff --exit-code -- src/main` (exit 0). | rodar e registrar as linhas; anexe o diff da remoção e da volta |
| R3 | Custo: o tempo do passo `types:fixtures` no R1 fica perto de 7 a 15 s. Acima de 30 s, pare e mostre os números antes de seguir. | o tempo medido no R1 |
| R4 | Compatibilidade: com `KOF=~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof`, rode `python3 scripts/kof_project.py check --target js --json --kof "$KOF" --fixture tests/<x>.kf` para cada fixture. Todas com exit 0. | registrar os 6 resultados |
| R5 | `npm run docs:sensor` com PASS depois da mudança no `SENSORS.md`. | rodar |

## Progress

- [x] M1. `kof_project.py check --fixture`. Dois testes novos com Kof real
  (F1, F2); testes Python de 13 para 15.
- [x] M2. Passo `types:fixtures` no `check`. Três testes novos (P1 a P3); o teste
  de ordem antigo ficou igual, porque o projeto stub dele não tem fixture e o
  passo dá SKIP (coberto pelo P3). Testes de sensores: 39.
- [x] M3. Prova real, documentação e aceite. R2 reproduziu a falha do piloto;
  R3 em 9,9 s. Aceite em `.agent/validation/check-fixture-imports.md`.

## Validation

Validação final, nesta ordem. O commit só acontece se todos passarem:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
npm run test:sensors
npm run check
npm run check:task
git diff --check
git diff --exit-code main -- src/main
```

Esperado:
- os comandos com exit 0;
- `npm run check` e `npm run check:task` com a linha `types:fixtures  PASS`;
- `check:task` com as sete jornadas em PASS;
- o último comando confirma que a produção não mudou.

Obrigações do executor antes de entregar:

- Conferir de novo se cada expectativa está correta pelas fontes citadas: o
  `prepared_sources`, o `served_build` e as fixtures. Isso é separado de conferir se
  os testes a demonstram.
- Para cada critério (F1 a F3, P1 a P4, R1 a R5), registrar no aceite o comando,
  o resultado observado e onde está a evidência. Uma suíte verde sozinha não prova
  cada critério.
- Registrar critério não verificado, cobertura que faltou ou falha antes da entrega,
  sem apresentá-los como atendidos.
