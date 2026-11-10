# Aceite: o `check` checa os tipos das fixtures de navegador

Plano: [`.agent/execplans/check-fixture-imports.md`](../execplans/check-fixture-imports.md).
Branch `feat/check-fixture-imports`, a partir de `11891e9`. Kof 0.7.0 (`kof` no
`PATH`) e Kof 0.6.4 para o R4. Execução em 10/11/2026.

## Conferência das expectativas pelas fontes

- `scripts/kof_project.py` `prepared_sources`: sem `fixture`, escreve
  `Main.kf` com `import sifuture.*`; com `fixture`, copia a fixture como
  `Main.kf`. O `check` agora repassa `fixture` a ele, sem outra mudança.
- `served_build` chama `build(..., fixture=...)`, que usa o mesmo
  `prepared_sources(fixture=...)` e `--target js`. Então o `types:fixtures` vê a
  mesma entrada que as jornadas.
- As 6 fixtures `tests/*.kf` importam classes uma a uma (por exemplo
  `tests/boss.kf`: `sifuture.GameControls`, `sifuture.GameView`,
  `sifuture.game.*`). O `GameControls` alcança o `ControlsGuide`, que alcança o
  `GuideDisclosure`.

## Critérios

| # | Comando | Resultado observado | Evidência |
| --- | --- | --- | --- |
| F1 | `python3 -m unittest discover -s tests -p 'test_*.py'`, teste `test_fixture_check_reports_import_missing_only_from_the_fixture_entry` | Com Kof real, numa cópia sem o `import sifuture.GuideDisclosure`: `check(target="js", fixture=...)` diferente de 0 com `GuideDisclosure` num `ERROR`; sem fixture, 0. RED anotado: primeiro `TypeError` (sem o parâmetro); depois, com o parâmetro ignorado de propósito, `AssertionError: 0 == 0`. | `tests/test_kof_project.py` |
| F2 | mesmo comando, teste `test_fixture_check_accepts_a_browser_fixture_of_the_complete_game` | cópia de `tests/boss.kf` como fixture: exit 0 | `tests/test_kof_project.py` |
| F3 | `python3 scripts/kof_project.py check --target js --json --fixture tests/boss.kf` | `{"success":true,...}`, exit 0. Sem `--fixture`, `check --target js` imprime `checked 1 entry file(s)...`, exit 0; os 13 testes Python antigos continuam verdes. | saída do comando |
| P1 | `npm run test:sensors`, teste `check type-checks every browser fixture in name order...` | stub com `tests/b.kf` e `tests/a.kf` criados nessa ordem: chamadas `--fixture tests/a.kf` e depois `tests/b.kf`, entre `check --target js --json` e `unittest`; `types:fixtures  PASS` | `test/sensors/check.test.mjs` |
| P2 | teste `the first browser fixture that fails type checking stops check...` | `FAIL_fixture_a=1`: `types:fixtures  FAIL (tests/a.kf: exit 1)`, última chamada é a fixture `a`, os 7 passos seguintes `NOT RUN`, `CHECK: FAIL at types:fixtures`, exit 1 | `test/sensors/check.test.mjs` |
| P3 | teste `check without browser fixtures skips the fixture type check and goes on` | `types:fixtures  SKIP (no browser fixture in tests)`, nenhuma chamada com `--fixture`, `CHECK: PASS` | `test/sensors/check.test.mjs` |
| P4 | leitura de `scripts/check.mjs` | `browserFixtures` lê `tests/` com `readdirSync`, filtra `.kf` e ordena; não há lista fixa. O P1 usa nomes que só existem no projeto stub. | `scripts/check.mjs` |
| R1 | `npm run check` na árvore real | `types:fixtures  PASS`, `mutation  SKIP (no production Kof file changed against main)`, `CHECK: PASS`, exit 0, 41 s no total | sumário abaixo |
| R2 | `import sifuture.GuideDisclosure` removido do `ControlsGuide.kf`, `npm run check` | `types:jvm  PASS`, `types:js  PASS`, `types:fixtures  FAIL (tests/boss.kf: exit 1)`, JSON com `SEM015 ... 'GuideDisclosure'` e `SEM011` acima do sumário, `CHECK: FAIL at types:fixtures`, exit 1. Depois de `git checkout` do arquivo, `git diff --exit-code -- src/main` exit 0. | sumário e diff abaixo |
| R3 | as 6 checagens do passo, cronometradas uma a uma | 1646, 1581, 1290, 1945, 1832 e 1623 ms; total 9,9 s, dentro de 7 a 15 s | lista abaixo |
| R4 | `python3 scripts/kof_project.py check --target js --json --kof "$KOF" --fixture tests/<x>.kf` com Kof 0.6.4 | as 6 fixtures com `"success":true` e exit 0 | lista abaixo |
| R5 | `npm run docs:sensor` | PASS depois deste registro existir (antes, `broken-link` no `EXECPLAN.md` apontando para ele) | seção "Validação final" |

## R1: sumário

```text
CHECK SUMMARY
  secret:sensor   PASS
  types:jvm       PASS
  types:js        PASS
  types:fixtures  PASS
  python tests    PASS
  kof tests:jvm   PASS
  kof tests:js    PASS
  lint:sensor     SKIP (no Kof files changed against main)
  dup:sensor      SKIP (no Kof files changed against main)
  docs:sensor     PASS
  mutation        SKIP (no production Kof file changed against main)
CHECK: PASS
```

## R2: remoção, diagnóstico e volta

```diff
--- a/src/main/kof/sifuture/ControlsGuide.kf
+++ b/src/main/kof/sifuture/ControlsGuide.kf
@@ -1,6 +1,5 @@
 package sifuture

-import sifuture.GuideDisclosure
 import kof.ui.*
```

Diagnóstico (início da linha JSON acima do sumário):

```text
{"success":false,"filesChecked":1,"errorCount":2,"diagnostics":[{"code":"SEM015","file":"ControlsGuide.kf","line":10,"column":5,"length":7,"severity":"ERROR","message":"Undefined function: 'GuideDisclosure'"},{"code":"SEM011","file":"ControlsGuide.kf","line":9,"column":5,"length":15,"severity":"ERROR","message":"Undefined variable or type: 'GuideDisclosure' in field 'detailsState' ...
```

```text
CHECK SUMMARY
  secret:sensor   PASS
  types:jvm       PASS
  types:js        PASS
  types:fixtures  FAIL (tests/boss.kf: exit 1)
  python tests    NOT RUN (an earlier step failed)
  kof tests:jvm   NOT RUN (an earlier step failed)
  kof tests:js    NOT RUN (an earlier step failed)
  lint:sensor     NOT RUN (an earlier step failed)
  dup:sensor      NOT RUN (an earlier step failed)
  docs:sensor     NOT RUN (an earlier step failed)
  mutation        NOT RUN (an earlier step failed)
CHECK: FAIL at types:fixtures
```

Volta: `git checkout -- src/main/kof/sifuture/ControlsGuide.kf`, depois
`git diff --exit-code -- src/main` com exit 0.

## R3 e R4: por fixture

| Fixture | Kof 0.7.0 | Kof 0.6.4 |
| --- | ---: | --- |
| `tests/boss.kf` | 1646 ms, exit 0 | exit 0 |
| `tests/controls.kf` | 1581 ms, exit 0 | exit 0 |
| `tests/meteor-motion.kf` | 1290 ms, exit 0 | exit 0 |
| `tests/stage.kf` | 1945 ms, exit 0 | exit 0 |
| `tests/subchief.kf` | 1832 ms, exit 0 | exit 0 |
| `tests/weapons.kf` | 1623 ms, exit 0 | exit 0 |

## Limites conhecidos

- Só o alvo JS (decisão do plano). Uma falha de tipo que apareça só na JVM a
  partir de uma fixture não é vista; nenhuma jornada usa a JVM.
- O passo para na primeira fixture que falha; as outras só são vistas depois da
  correção.
- O buraco do `import sifuture.*` continua em `types:jvm`, `types:js` e no build
  do app; ele só é pego quando uma fixture alcança o arquivo. Um arquivo de
  produção que nenhuma fixture alcança segue sem essa proteção.
- `kof_project.py check --fixture` com um caminho inexistente sai com traceback
  do Python, não com `error:`. O `check` só passa caminhos que leu do disco.

## Validação final

| Comando | Resultado |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 15 testes, OK, exit 0 |
| `npm run test:sensors` | 39 de 39, exit 0 |
| `npm run check` | `types:fixtures  PASS`, `docs:sensor  PASS`, `CHECK: PASS`, exit 0 |
| `npm run check:task` | `types:fixtures  PASS`, as sete jornadas `browser:*` em PASS, `CHECK:TASK: PASS`, exit 0 |
| `git diff --check` | exit 0 |
| `git diff --exit-code main -- src/main` | exit 0 |
