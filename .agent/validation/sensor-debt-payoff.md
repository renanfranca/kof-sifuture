# Pagamento da dívida dos sensores antes do M3

Branch `sensor-debt-payoff`, criada em 05/11/2026 a partir da `main`
`f4af07a9e703f0ef30f90eb6b42f254c627429bd` (contém `6b17e1c`). Kof
`kof 0.7.0` do PATH; KofMut 0.1.0, imagem `b5401898d74f`; 0.6.4 em
`~/.local/share/kof/kof-0.6.4-linux-x86_64`. Evidência bruta local, opcional,
em `.agent/tmp/debt-*/`.

## R0. Linha de base

| Medida | Comando | Resultado |
| --- | --- | --- |
| SHA | `git rev-parse HEAD` | `f4af07a9e703f0ef30f90eb6b42f254c627429bd` |
| Doctor | `npm run sensors:doctor` | todas as ferramentas e comandos `ok`, sem MISSING |
| Dívida | `npm run sensors:debt` | `SENSORS DEBT (report only, 31 Kof files)`; `SENSOR lint: FAIL (415 findings)`; `SENSOR dup: FAIL (23 findings)`, `31 files expected, 31 tokenized`; exit 0 |
| Casos JVM | `python3 scripts/kof_project.py test --target jvm --kof kof` | 1 suíte (`sifuture/game/GameJourney.kf`), `0 failed of 114 tests`, 3,5 s |
| Casos JS | idem `--target js` | `0 failed of 114 tests`, 6,3 s |
| Tipos | `kof_project.py check --target jvm\|js --json` | `success:true`, `errorCount:0` nos dois |
| Python | `python3 -m unittest discover -s tests -p 'test_*.py'` | `Ran 16 tests`, OK |
| Build | `kof_project.py build --output <tmp>` | exit 0; 113 arquivos: `Default.mjs`, `Default.mjs.map`, `index.html`, `kof-runtime.mjs`, `kof-runtime-io.mjs` e 108 em `assets/` |
| Jornadas | `tests/browser*.py`, duas execuções seguidas | 7/7 exit 0 nas duas; 186 PNG em cada; comparação de pixels decodificados (RGBA): `common=186 only_a=0 only_b=0 pixel_diff=0` |

### Dívida por área e regra (`sensors:debt`)

| Regra | `src/main/kof` | `src/test/kof` | outros (`tests/*.kf`) |
| --- | ---: | ---: | ---: |
| `looping-test` | | 207 | |
| `branching-test` | | 52 | |
| `high-complexity` | 18 | 38 | 1 |
| `unnamed-arrange` | | 28 | |
| `deep-nesting` | 12 | 8 | |
| `long-file` | 4 | 1 | 3 |
| `long-function` | 10 | | 5 |
| `too-many-statements` | 18 | | 8 |
| `too-many-parameters` | 2 | | |

Grupos CPD (`duplicated-code`), 23: 16 dentro de `GameJourney.kf`; 3 na
produção (`Boss.kf:114`↔`Subchief.kf:91`, `Game.kf:208`↔`Game.kf:269`,
`BossShot.kf:25`↔`SubchiefShot.kf:14`); 3 entre fixtures
(`tests/stage.kf:159`↔`tests/subchief.kf:180`, `tests/boss.kf:14`↔`tests/subchief.kf:14`,
`tests/boss.kf:138`↔`tests/subchief.kf:97`); e 1 entre produção e fixture,
`src/main/kof/sifuture/Main.kf:11`↔`tests/controls.kf:18` (51 tokens, 10 linhas),
que o plano não lista no R4 nem no R6.

Achados de lint por arquivo: `GameJourney.kf` 334; `Game.kf` 13;
`GameControls.kf` 12; `GameView.kf` 9; `Weapons.kf` 7; `tests/subchief.kf` 5;
`tests/boss.kf` 5; `Ship.kf` 4; `Meteor.kf` 4; `tests/stage.kf` 4;
`Subchief.kf` 5; `BossWeapons.kf` 3; `Boss.kf` 2; `ControlsGuide.kf` 2;
`tests/weapons.kf` 2; e 1 em `tests/meteor-motion.kf`, `SpecialBeam.kf`,
`Item.kf` e `Blaster.kf`.

### Jornadas e capturas

As capturas ficam em `credits-text-browser` (62), `subchief-browser` (50),
`stage-browser` (34), `boss-browser` (24), `background-items-weapons` (8),
`special-key-release` (6) e `sifuture-controls` (2). Lacuna: o
`browser_meteor.py` compara o canvas em memória e não grava captura; para ele,
o A5 fica só nas asserções da jornada.

### KofMut sobre toda a produção

Comando (a receita do `check`, com o escopo trocado pelos 20 `.kf` de
`src/main/kof`):
`kof-mut run --project . --files <20 arquivos> --config kof-mut.json --report-dir <tmp> --run-id <uuid>`.
Início 10:03:41, fim 12:51:40 (2h47min58s de parede, `durationMs` 10076224),
exit **3**, `status: incomplete`, baseline `passed`.

`candidates=1167 killed=678 survived=489 compileError=0 timeout=0 testError=0 pending=0`.
Sobreviventes por operador: boundary 129, arithmetic 99, logical 91, boolean 87,
equality 83.

| Arquivo | Candidatos | Mortos | Sobreviventes |
| --- | ---: | ---: | ---: |
| `GameControls.kf` | 118 | 0 | 118 |
| `GameView.kf` | 75 | 0 | 75 |
| `game/SpecialBeam.kf` | 101 | 49 | 52 |
| `game/Game.kf` | 188 | 146 | 42 |
| `game/Weapons.kf` | 139 | 97 | 42 |
| `game/Boss.kf` | 101 | 71 | 30 |
| `game/Subchief.kf` | 71 | 53 | 18 |
| `game/Blaster.kf` | 40 | 23 | 17 |
| `game/Shot.kf` | 48 | 31 | 17 |
| `game/Ship.kf` | 55 | 39 | 16 |
| `game/BossShot.kf` | 34 | 20 | 14 |
| `game/BossSpecial.kf` | 31 | 19 | 12 |
| `game/Item.kf` | 39 | 27 | 12 |
| `game/SubchiefShot.kf` | 26 | 15 | 11 |
| `ControlsGuide.kf` | 6 | 0 | 6 |
| `game/Meteor.kf` | 41 | 37 | 4 |
| `game/Credits.kf` | 14 | 12 | 2 |
| `game/BossWeapons.kf` | 29 | 28 | 1 |
| `game/Background.kf` | 1 | 1 | 0 |
| `game/MenuEntrance.kf` | 7 | 7 | 0 |
| `game/Rules.kf` | 3 | 3 | 0 |
| `Main.kf`, `game/Lasers.kf`, `game/State.kf` | 0 | 0 | 0 |

Os 4 de `Meteor.kf` são os do plano: `5:19 true -> false`, `13:21 false -> true`,
`85:17 >= -> >`, `86:75 <= -> <`.

Limitações (8): `Unsupported AST node: dev.kof.compiler.EnumDeclarationNode` em
`Boss.kf`, `Item.kf`, `MenuEntrance.kf`, `Subchief.kf` e quatro vezes em
`State.kf`. No KofMut, qualquer limitação torna a execução `incomplete`
(`kof-mut/src/main/kof/kofmut/Run.kf:116`), e o `check` reprova o exit 3
(`scripts/mutation-step.mjs`). Portanto, um escopo que contenha qualquer
desses cinco arquivos sai com exit 3 mesmo sem sobreviventes.

`GameControls.kf`, `GameView.kf` e `ControlsGuide.kf` importam `kof.ui.*` e
não têm nenhum mutante morto: a suíte importa só `sifuture.game.*`, o
`testCommand` do KofMut é JVM, e no JVM a renderização do `kof.ui` usa handles
sem efeito (`kof/training/language/ui.md:57-61`). Quem verifica essa camada são
as jornadas de navegador, que o KofMut não executa.

Relatório JSON e lista de sobreviventes (local): `.agent/tmp/debt-r0/kofmut-r0-report.json`,
`.agent/tmp/debt-r0/survivors-r0.txt`.

Estado do R0: medido; parado no ponto de parada 4.

## Decisões de 07/11

Ponto de parada 4 respondido pelo usuário em 07/11/2026; a lista completa está
no `EXECPLAN.md` ("Decisões de 07/11"). Exceção de regra aprovada pelo usuário
(fonte: usuário, 07/11): no código de teste (`src/test/kof/` e `tests/`),
`long-file` vale 1000 linhas não vazias e o CPD não analisa esses arquivos. A
produção continua com 150 e CPD de 50 tokens; os limites por função não mudam.

## S. Sensores com a exceção aprovada

RED esperado antes de cada mudança, observado igual:

| Teste novo (`FindingsTest`) | RED esperado | RED observado | GREEN |
| --- | --- | --- | --- |
| `testCodeLongFileIsReportedAboveOneThousandLinesAndNotAtOneThousand` | o arquivo de teste com 1000 linhas recebe `long-file` (limite ainda 150) | `but was: <[src/test/kof/AboveLimit.kf, src/test/kof/AtLimit.kf, tests/fixture.kf]>` | limite 1000 para `src/test/kof/` e `tests/` (`Findings.java`, `testCode`) |
| `duplicationLeavesTestCodeOutAndStillReportsProductionClones` | o CPD ainda espera os arquivos de teste | `but was: <[src/test/kof/Journey.kf, tests/fixture.kf, src/main/kof/First.kf, src/main/kof/Second.kf]>` | só caminhos que não são de teste vão ao CPD |

O teste existente `longFileIsReportedAboveOneHundredFiftyLinesAndNotAtOneHundredFifty`
continua provando 150/151 na produção, e `duplicationReportsAFiftyTokenFiveLineCloneWithRelativeLocations`
continua provando o clone de produção. Juntos, cobrem os dois lados das duas
fronteiras: desligar a regra ou subir o limite da produção reprovaria.

| Verificação | Comando | Resultado |
| --- | --- | --- |
| Sensores 0.7.0 | `scripts/kof-sensors/test` | `Tests run: 42, Failures: 0` (eram 40) |
| Sensores 0.6.4 | `KOF=<0.6.4> scripts/kof-sensors/test` | `Tests run: 42, Failures: 0` |
| Node 0.7.0 e 0.6.4 | `node --test test/sensors/*.test.mjs` | 21/21 nas duas |
| Caminho público, só teste | `scripts/kof-sensors/run --findings . src/test/kof/sifuture/game/GameJourney.kf` | `success: true`; CPD `expected: []`, `tokenized: []`, sem falha; `long-file` 2719 com limite 1000 |
| Docs | `npm run docs:sensor` | `SENSOR docs: PASS (0 findings)` |
| Python | `python3 -m unittest discover -s tests -p 'test_*.py'` | `Ran 16 tests`, OK |
| Kof | `kof_project.py test --target jvm\|js` | `0 failed of 114 tests` nos dois |
| Espaços | `git diff --check` | exit 0 |

`npm run sensors:debt` depois (saída lida; exit 0 sempre): `SENSORS DEBT (report only, 31 Kof files)`;
`SENSOR lint: FAIL (412 findings)` (eram 415: saíram os 3 `long-file` das fixtures);
`SENSOR dup: FAIL (3 findings)`, `24 files expected, 24 tokenized` (31 menos os 7
arquivos de teste). Os 3 grupos restantes são os da produção: `Boss.kf:114`,
`Game.kf:208`, `BossShot.kf:25`. O `long-file` do `GameJourney.kf` (2719 > 1000)
fica até o R1. Saída em `.agent/tmp/debt-s/sensors-debt.txt`.

Arquivos alterados: `scripts/kof-sensors/src/main/java/sifuture/sensors/Findings.java`,
`FindingsTest.java`, `SENSORS.md`. Não houve mudança em `scripts/*.mjs`,
`package.json` nem nos guias.

## P. Probe do ponto de parada 1 (07/11)

Cópia em `/tmp/sifuture-r1-probe-NyRo` (fora de pastas com ponto), já apagada.
Evidência em `.agent/tmp/debt-r1-probe/` (divisão em `split/`, script `split.py`,
saídas, relatório do KofMut). Nada foi aplicado no repositório.

Montagem: `kof.toml` com `[sources] app = "src/main/kof"` e `test = "src/test/kof"`;
`GameJourney.kf` dividido por assunto em 9 arquivos (`Boss` 19 testes, `Controls` 19,
`Subchief` 18, `Meteor` 15, `Weapons` 15, `Menu` 8, `Result` 7, `Stage` 7, `Items` 6;
o maior tem 460 linhas não vazias) e um módulo auxiliar `JourneyScenarios.kf` com os
quatro `prepare…`. O corpo dos testes não mudou.

Achados da montagem:

1. Com `[sources]`, o cabeçalho atual `package sifuture.game` + `import sifuture.game.*`
   falha com `PKG007` (import auto-referente). Sem o import, o pacote de teste não
   enxerga o do app (`SEM015 Undefined function: 'Game'`). Funciona com um import
   por módulo (`import sifuture.game.Game`, …), como o fixture do Kof
   (`kof/kof-cli/src/test/java/dev/kof/cli/TwoRootsCliE2ETest.java:69-70`). É uma
   mudança só de cabeçalho.
2. O módulo auxiliar sem `test` nem `main` aparece como
   `SKIP … JourneyScenarios.kf (no tests, no main)` e não conta como falha; os
   arquivos que usam os helpers precisam de `import sifuture.game.JourneyScenarios`.
3. `kof_project.py check` e `build` continuam funcionando com `[sources]`
   (`success:true`; build com 113 arquivos, igual ao R0).

| Medida | Comando | Resultado |
| --- | --- | --- |
| Casos JVM 0.7.0 | `kof test --target jvm` (3 vezes) | `9 passed, 0 failed, 1 skipped`; soma `0 failed of 114`; 13,3 s, 11,6 s, 11,3 s |
| Casos JS 0.7.0 | `kof test --target js` (3 vezes) | soma `0 failed of 114`; 7,0 s, 7,4 s, 7,1 s |
| Casos 0.6.4 | `<0.6.4> kof test --target jvm\|js` | `0 failed of 114` nos dois; 10,5 s e 6,8 s |
| Entrada única | `kof test entry/AllJourneys.kf --module-root src/test/kof --target jvm` (3 vezes) | `0 failed of 114`; 10,8 s, 11,2 s, 10,8 s |

Lacuna de medição: durante a probe a máquina estava carregada por outros
trabalhos (load average 31 a 35 em 32 núcleos, processos do `kof-mut` e de uma
publicação Node). O wrapper atual, no repositório sem mudança, passou de 3,3 s
para 9,8 a 11,1 s. Os tempos absolutos acima não valem como referência. A
comparação relativa, intercalada sob a mesma carga, vale:

| Montagem (JVM) | Rodada 1 | Rodada 2 |
| --- | ---: | ---: |
| A. Wrapper atual, 1 suíte | 9,9 s | 9,8 s |
| B. `kof test`, 9 arquivos (um programa por arquivo) | 27,8 s | 25,6 s |
| C. Entrada única importando as 9 suítes | 9,2 s | 6,9 s |

KofMut só no `Meteor.kf`, `testCommand` = `kof test --target jvm` (montagem B),
resto do `kof-mut.json` igual (`kof-mut.probe.json`): exit 3, `status: incomplete`,
18m58s; `candidates=41 killed=28 survived=2 timeout=11`. Os 41 `id`s são os mesmos
do R0. **O veredito mudou:** 9 mutantes mortos no R0 e 2 sobreviventes do R0
(`Meteor.kf:2526:>` e `:2647:<`, os limites de `touchesShip`) viraram `Timeout`.
Duração por mutante: mínimo 12,7 s, mediana 32,0 s, máximo 45,5 s (R0: 6,1 / 6,2 /
7,3 s), acima do `commandTimeoutMs` de 30 s. Parte disso é a carga da máquina, mas
a montagem B custa de 2,6 a 2,8 vezes a A sob a mesma carga.

Estado: ponto de parada 1 acionado (o veredito do KofMut mudou). Aguardando a
decisão do usuário. A montagem C não foi medida no KofMut.

## Decisões de 09/11

Ponto de parada 1 respondido pelo usuário em 09/11/2026: 9 arquivos por assunto
com `[sources]`; testes Kof por `scripts/kof-tests.mjs` (entrada temporária gerada
a cada execução); `kof_project.py test` aposentado, com testes Node equivalentes;
sem TypeScript. Lista completa no `EXECPLAN.md` ("Decisões de 09/11").

Decisão adicional do usuário em 09/11, nesta sessão: a entrada temporária fica em
`src/test/kof/KofTestsEntry<aleatório>.kf`, e não em `build/`. Motivo: o Kof 0.6.4
não aceita `--module-root` (`test: unknown or incomplete flag: --module-root`), e
na raiz dos testes o Kof já usa essa pasta como raiz de módulo
(`kof/kof-cli/src/main/java/dev/kof/cli/CmdTest.java`, `dirMode ? src : src.getParent()`).
Probe antes da decisão: entrada em `src/test/kof/` sem `--module-root`, 114/114 em
JVM e JS no 0.6.4 e no 0.7.0.

## E. `scripts/kof-tests.mjs` e aposentadoria do `kof_project.py test` (09/11)

Ponto a verificar primeiro (local da entrada):
- fora do projeto (`/tmp/...`) **não** funciona: o Kof acha o `kof.toml` subindo a
  partir da entrada, e não do diretório atual (`PKG006 import 'sifuture.game.Background' not found`);
- `build/kof-tests-XXXX/` dentro do projeto funcionou no 0.7.0 (114/114, invisível
  ao `git status` com `/build/` ignorado), mas exige `--module-root`, que o 0.6.4 não tem;
- local final: `src/test/kof/KofTestsEntry<12 hex>.kf`, sem ponto no caminho,
  ignorado por `/src/test/kof/KofTestsEntry*.kf` no `.gitignore`, pulado pela
  descoberta e apagado num `finally`. O KofMut roda cada mutante numa cópia em
  `/tmp/kofmut-…` (`RunResources.kf:29`), também sem ponto. Uma morte forçada
  (SIGKILL) pode deixar a entrada para trás; ela continua ignorada e não é importada
  (teste "an entry left behind…").

TDD com o skill `tdd-behavior-autonomous-quiet`, testes em
`test/sensors/kof-tests.test.mjs`, pela linha de comando real com o `kof` do PATH:

| Critério | Teste | RED observado | Prova de que distingue |
| --- | --- | --- | --- |
| E1 Descoberta sem lista | `a new test file under src/test/kof runs without editing any list` | `Cannot find module …/scripts/kof-tests.mjs` | soma 1 → 2 ao criar um arquivo em subpacote, sem editar nada |
| E2 Falha propaga | `a failing test fails the run, names the test and still removes the generated entry` | passou de primeira (o E1 já devolvia o exit) | mutantes manuais: `return 0` → falhou; sem `rmSync` → falhou mostrando `KofTestsEntry2894d7d2a363.kf` |
| E3 Zero não é sucesso | `a test root without any Kof test fails with a clear message instead of passing` | mensagem do Kof sem citar a pasta (`no runnable test or program file found`) | pasta vazia e só com auxiliar saem 1 com `kof-tests: no Kof tests ran in src/test/kof` |
| E4 Módulo auxiliar | `a helper module without tests or main is shared by test files in other packages` | passou de primeira (capacidade do Kof) | mutante manual `--module-root` apontando para outra pasta → falhou (versão com `build/`) |
| Local da entrada | `an entry left behind by an interrupted run is neither imported nor counted` | `PKG006 import 'KofTestsEntryInterrupted' not found` | — |
| Fonte atual | `each run compiles the current production sources` | passou de primeira (equivalente Node do teste Python aposentado) | verde → vermelho com `a - b` → verde de novo |

| Critério | Comando | Resultado |
| --- | --- | --- |
| E5 Os 114 casos | `KOF=<0.7.0\|0.6.4> node scripts/kof-tests.mjs --target jvm\|js` | `0 failed of 114 tests` nas quatro combinações; nenhuma entrada sobrando |
| E6 Mutação igual ao R0 | `kof-mut run --files <Meteor.kf> --config kof-mut.json`, `uptime` antes: load 6,35 em 32 núcleos | `complete`; `candidates=41 killed=37 survived=4 timeout=0`; mesmos 41 `id`s com os mesmos status do R0; mediana 8,5 s por mutante; 6m03s (exit 1 = os 4 sobreviventes conhecidos). Uma rodada anterior, com a entrada em `build/`, deu o mesmo, mediana 5,3 s |
| E7 Tempo | intercalado, 3 rodadas, load ~12: wrapper antigo da `HEAD` (1 suíte) × script (9 suítes), JVM | 5,36 × 5,16 s; 5,03 × 5,20 s; 5,07 × 4,86 s |
| E9 Documentado | `docs/desenvolvimento*.md`, "Ponte temporária" | registra a ponte, a troca pela opção nativa do Kof e o risco de estado estático compartilhado; `mystery-guest` com 0 achados (`npm run check`) |
| E10 `check` | `npm run check` | `secret`, `types:jvm/js`, `python tests`, **`kof tests:jvm` e `kof tests:js` PASS pelo script**; `lint:sensor` FAIL com 333 achados, todos das suítes e exatamente a dívida do R0 (207 `looping-test`, 52 `branching-test`, 38 `high-complexity`, 28 `unnamed-arrange`, 8 `deep-nesting`), que é o R2; `dup`, `docs` e mutação NOT RUN. Rodados à parte: `dup:sensor` PASS (0 arquivos de produção mudados), `docs:sensor` PASS |
| E10 Node | `KOF=<0.7.0\|0.6.4> node --test test/sensors/*.test.mjs` | 27/27 nas duas (eram 21) |
| E10 Sensores | `KOF=<0.7.0\|0.6.4> scripts/kof-sensors/test` | 42/0 nas duas |
| E10 Jornadas | `python3 tests/browser*.py` | 7/7 exit 0 (`browser` 55 s, `boss` 27 s, `controls` 28 s, `meteor` 3 s, `stage` 34 s, `subchief` 28 s, `weapons` 80 s); logs em `.agent/tmp/debt-e10/` |
| E10 Contrato da CI | `bash tests/ci-contract.sh` com um `rg` de teste (`grep -Eq`) no PATH, porque o ripgrep não está instalado | exit 0, 28 PASS, inclusive "actual workflow test command discovers nested suites and preserves each target failure". Na `HEAD` também exigia o `rg` (parava na linha 85 sem ele). Mutante manual (script ignorando o exit) → contrato exit 1 |
| E10 Espaços | `git diff --check` | exit 0 |

Pendente: a CI real só roda depois do push, que é do usuário. O passo da CI usa o
Node.js que já vem no `ubuntu-24.04`, sem `setup-node`. O script não depende de
`import.meta.main`; se o Node do runner não tiver `import.meta.dirname`
(`sensor-arguments.mjs`), o passo quebra com erro, e não com PASS falso.

### E8. Testes Python aposentados (16 → 13)

| Teste Python | Para |
| --- | --- |
| `test_prepared_sources_are_byte_copies_and_isolate_suite` | reescrito como `test_prepared_sources_are_byte_copies_without_manifest`: a cópia byte a byte continua para `check` e `build`; a parte da suíte selecionada deixou de existir junto com o parâmetro `suite` |
| `test_real_cli_observes_source_update_and_suite_isolation` | Node `each run compiles the current production sources` (mudança de produção percebida) e `a failing test fails the run…` (falha propagada). O isolamento entre suítes (`--suite` excluindo um arquivo quebrado) não existe mais: todas as suítes rodam num só programa; um arquivo isolado roda com `kof test <arquivo> --module-root src/test/kof` (Kof 0.7.0+) |
| `test_rejects_missing_outside_and_empty_suite` | suíte inexistente ou fora da raiz: a opção `--suite` não existe mais. Pasta vazia: Node `a test root without any Kof test fails…` |
| `test_first_suite_failure_code_is_retained` | não existe mais: um programa, um código de saída. A propagação da falha fica com o Node `a failing test fails the run…` e com o contrato da CI ("preserves each target failure", exit 19) |

Também mudaram: `tests/ci-contract.sh` (o `kof` falso recebe a entrada e o alvo
na nova posição; o módulo esperado passou a `sifuture.game.MenuJourney`) e
`test/sensors/check.test.mjs` (o stub chama `scripts/kof-tests.mjs`).

Links: os 294 links relativos dos registros históricos para o
`GameJourney.kf` (`sensor-calibration.md` 284, `stage-hud-result.md` 8,
`sensors-adoption.md` 2) viraram links permanentes do GitHub para o arquivo em
`f4af07a` (já na `origin/main`, conteúdo idêntico ao dividido). Só o destino do
link mudou; o texto dos registros não. Sem isso, o `docs:sensor` dava FAIL com
294 achados.

## R1. Suíte dividida por assunto (09/11)

`GameJourney.kf` (2719 linhas não vazias) virou 9 arquivos em
`src/test/kof/sifuture/game/` mais o auxiliar `JourneyScenarios.kf` (os quatro
`prepare…`). Testes por arquivo: `Boss` 19, `Controls` 19, `Subchief` 18,
`Meteor` 15, `Weapons` 15, `Menu` 8, `Result` 7, `Stage` 7, `Items` 6. O maior tem
460 linhas não vazias. Só o cabeçalho mudou: `import sifuture.game.*` virou um
import por módulo (o curinga dá `PKG007` com `[sources]`), mais
`import sifuture.game.JourneyScenarios` em `Boss` e `Subchief`.

Prova de movimentação pura: os 118 blocos de nível superior (114 testes e 4
funções) dos novos arquivos são idênticos, byte a byte, aos do arquivo original
(comparação de multiconjunto). Mapa teste → arquivo em
`.agent/tmp/debt-r1/test-to-file.txt`.

A2: soma pelo script 114 em JVM e JS, no 0.7.0 e no 0.6.4 (E5).

## Node.js 24 fixado na CI (09/11)

Pedido do usuário em 09/11, antes do R2: o passo de testes da CI não pode depender
do Node.js da imagem `ubuntu-24.04`. O job `test` de
`.github/workflows/kof-ci-and-pages.yml` ganhou, antes de "Run complete Kof suite",
`actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1` com
`node-version: '24'`. O SHA é o commit da release mais recente, `v7.1.0`
(publicada em 08/10/2026), lido com `gh api repos/actions/setup-node/releases/latest`
e `git/ref/tags/v7.1.0` (tag leve, objeto `commit`). No `action.yml` desse SHA, a
entrada `node-version` existe e o cache automático só liga com `packageManager` no
`package.json`, que este projeto não declara.

`tests/ci-contract.sh` ganhou a verificação "Kof tests run on a pinned Node.js 24":
no job `test`, existe um passo `actions/setup-node@…` antes de "Run complete Kof
suite", com `with` exatamente `{"node-version":"24"}`. A verificação que já existia
exige que todo `uses` seja travado por um SHA de 40 caracteres hexadecimais.

| Etapa | Comando | Resultado |
| --- | --- | --- |
| RED | `bash tests/ci-contract.sh` (com o `rg` de teste), só com a verificação nova | exit 1, logo depois de `PASS documentation PR triggers, independent checks, gating, pins and permissions` |
| GREEN | mesmo comando, com o passo no workflow | exit 0, 29 PASS (eram 28), inclusive `PASS Kof tests run on a pinned Node.js 24` |

`docs/ci-e-publicacao*.md` passou a citar o Node.js 24 instalado pelo
`actions/setup-node`. A CI real só roda num PR para a `main` ou num push na `main`;
o push da branch `sensor-debt-payoff` não dispara o workflow.

### CI real no PR em rascunho (09/11)

PR em rascunho [#23](https://github.com/renanfranca/kof-sifuture/pull/23), aberto com
`gh pr create --draft --base main --head sensor-debt-payoff` no HEAD `68a579d`.
Run [42675189498](https://github.com/renanfranca/kof-sifuture/actions/runs/42675189498),
evento `pull_request`, conclusão `success`.

| Job | Resultado | Evidência no log |
| --- | --- | --- |
| Resolve verified Kof | success | |
| [Kof tests (jvm)](https://github.com/renanfranca/kof-sifuture/actions/runs/42675189498/job/129355904495) | success | `node-version: 24`, `Found in cache @ /opt/hostedtoolcache/node/24.22.2/x64`, `0 failed of 114 tests` |
| [Kof tests (js)](https://github.com/renanfranca/kof-sifuture/actions/runs/42675189498/job/129355904305) | success | `node-version: 24`, `Found in cache @ /opt/hostedtoolcache/node/24.22.2/x64`, `0 failed of 114 tests` |
| Build complete Pages site | skipped | só roda num push na `main` |
| Publish current main | skipped | só roda num push na `main` |

Os dois jobs de teste rodaram `node scripts/kof-tests.mjs --target <alvo>` com o
Node.js 24.22.2 e contaram 114 casos, o mesmo número local.

## R2. Regras de teste (09/11)

Uma suíte por vez, nesta ordem: Items, Stage, Menu, Result, Meteor, Weapons,
Controls, Subchief, Boss. Depois de cada uma: `node scripts/lint-sensor.mjs <suíte>
src/test/kof/sifuture/game/JourneyScenarios.kf` com `PASS (0 findings)` e
`node scripts/kof-tests.mjs --target jvm` e `--target js` com `0 failed`.

Como cada regra foi tratada:

- laço que prepara o cenário → função com nome abaixo dos testes ou em
  `JourneyScenarios.kf` (`advanceSteps`, `advanceWhilePlaying`, `evolveWeapons`,
  `givenMeteorsAway`, `givenMeteorsAt`, `givenMeteorsAtHeight`, `givenItemsAway`,
  `givenEveryBeamActiveAt`, `advanceThroughExplosion`…);
- laço que confere um estado a cada passo → função `Bool` com nome que avança e
  devolve a conjunção das mesmas condições (`noProjectileAppearsDuring`,
  `laserStaysIdleDuring`, `explodingShipStaysStillWithoutFireDuring`,
  `bossExplosionFollowsHistoricalOffsetsAndHoldsOnPause`…). O teste faz
  `assert(<função>(g, passos))`;
- teste com `if` → um teste por caminho (lista abaixo);
- preparação com mais de 8 instruções antes do primeiro `assert` → função `given…`;
- `high-complexity` nos testes vinha das cadeias `&&` dentro de `assert`; onde
  passava de 10, cada `assert(a && b)` virou `assert(a)` e `assert(b)`. Asserts com
  mensagem não foram divididos.

### Desvio: `testRows` indisponível na entrada única

O plano pede que laços de casos virem `testRows`. Medido em 09/11: dentro de um
módulo importado pela entrada gerada por `scripts/kof-tests.mjs`, a chamada não
compila.

| Kof | Projeto mínimo (`[sources]`, `a/T.kf` com `import kof.test` e `testRows`, entrada `import a.T`) | Resultado |
| --- | --- | --- |
| 0.7.0 | `kof test src/test/kof/E.kf --target jvm` | `T.kf:7:1: error: Undefined function: 'testRows' [SEM015]` |
| 0.6.4 | mesmo comando | mesmo `SEM015` |
| 0.7.0 | entrada com `import kof.test` antes de `import a.T` | compila, mas falha ao rodar: `NoClassDefFoundError: a/T` |
| 0.7.0 | `kof.test.testRows(...)` qualificado | `SEM011 Undefined variable or type: 'kof'` |

O mesmo `testRows` roda num arquivo único (`kof test P.kf`), com falha por linha
(`row 1 [0]: assertion failed`). Não há registro disso em `kof/docs` nem issue
no KofLang/Kof4j. Escolha feita, sem decisão do usuário: os laços de casos
viraram um teste por caso quando o caso tem nome próprio (nível de arma, seed,
borda, arma), ou casos escritos um a um no mesmo teste quando todos verificam a
mesma regra (bordas do laser no chefe e no subchefe, tabela do especial do chefe).

### Contagem de casos (A2)

| Suíte | Antes (R1) | Depois (R2/R3) | Linhas não vazias |
| --- | ---: | ---: | ---: |
| BossJourney | 19 | 43 | 960 |
| ControlsJourney | 19 | 28 | 653 |
| ItemsJourney | 6 | 7 | 131 |
| MenuJourney | 8 | 8 | 304 |
| MeteorJourney | 15 | 23 | 554 |
| ResultJourney | 7 | 12 | 375 |
| StageJourney | 7 | 10 | 211 |
| SubchiefJourney | 18 | 26 | 883 |
| WeaponsJourney | 15 | 15 | 334 |
| **Total** | **114** | **172** | |

`node scripts/kof-tests.mjs --target jvm` e `--target js`: `0 failed of 172 tests`
no Kof 0.7.0 e no 0.6.4 (`KOF=~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof`).
`BossJourney.kf` (960) e `SubchiefJourney.kf` (883) ficaram perto do limite de
1000 linhas não vazias do código de teste.

### Testes divididos (de → para)

#### ItemsJourney
- "evolution collections reach level three then add special charges" →
  - "first three evolution collections raise the level to three without special charges"
  - "evolution collections after level three add special charges"

#### StageJourney
- "vertical contacts preserve ship laser blaster special priority and one reward" →
  - "vertical contact with the ship explodes the ship before any weapon and rewards once"
  - "vertical contact away from the ship hits the laser before blaster and special and rewards once"
  - "vertical contact without ship or laser hits the blaster before special and rewards once"
  - "vertical contact with only the special hits the beam and rewards once"

#### ResultJourney
- "defeat ends explosion without new projectiles or another loss at every weapon level" →
  - "defeat at weapon level 0 ends explosion without new projectiles or another loss"
  - "defeat at weapon level 1 ends explosion without new projectiles or another loss"
  - "defeat at weapon level 2 ends explosion without new projectiles or another loss"
  - "defeat at weapon level 3 ends explosion without new projectiles or another loss"
- "laser blaster and special impacts finish after one four and six result steps" →
  - "laser impact pending at defeat finishes after one result step"
  - "blaster impact pending at defeat finishes after four result steps"
  - "special impact pending at defeat changes sprite at three and finishes after six result steps"

#### MeteorJourney
- "vertical initial and impact resets keep reduced range while bottom exits include both full endpoints" →
  - "vertical meteors start waiting inside the reduced range"
  - "vertical seed 71 resets to x 70 y -103 after impact and exits the bottom to y -171"
  - "vertical seed 142 resets to x 143 y -100 after impact and exits the bottom to y 0"
  - "vertical seed 276 resets to x 8 y -153 after impact and exits the bottom to y -145"
  - "vertical seed 303 resets to x 145 y 0 after impact and exits the bottom to y -84"
  - "vertical resets keep the reduced range while bottom exits include both full endpoints for five hundred seeds"
- "ship meteor contact includes each boundary and excludes adjacent positions" →
  - "ship meteor contact includes the left and right boundaries"
  - "ship meteor contact excludes the positions beside the left and right boundaries"
  - "ship meteor contact includes the top and bottom boundaries"
  - "ship meteor contact excludes the positions beside the top and bottom boundaries"

#### WeaponsJourney
- nenhum teste dividido; o laço com `if` de "explosion completion loses a charge before level exactly once and never below basic" percorria uma sequência de estados do mesmo jogo e virou quatro chamadas de `advanceThroughExplosion` com o nível esperado de cada uma.

#### MenuJourney
- nenhum teste dividido; as três voltas de "repeated controls returns start entry and can leave before braking" viraram três `assert(controlsReturnReplaysEntryUntilReady(g))`.

#### ControlsJourney
- "pause and lost keyboard focus clear right image without changing opposing direction priority" →
  - "lost keyboard focus clears right image without changing opposing direction priority"
  - "pause clears right image without changing opposing direction priority"
- "four pad arrows move by axis and stop on release" →
  - "pad up arrow moves five units up and stops on release"
  - "pad left arrow moves five units left and stops on release"
  - "pad right arrow moves five units right and stops on release"
  - "pad down arrow moves five units down and stops on release"
- "pause holds explosion and restart frames without consuming a life" →
  - "pause holds explosion frames without consuming a life"
  - "pause holds restart frames without consuming a life"
- "four diagonals preserve either held axis in both press and release orders" (16 casos) →
  - "a diagonal pressed horizontal first keeps the vertical axis after the horizontal release and then stops"
  - "a diagonal pressed horizontal first keeps the horizontal axis after the vertical release and then stops"
  - "a diagonal pressed vertical first keeps the vertical axis after the horizontal release and then stops"
  - "a diagonal pressed vertical first keeps the horizontal axis after the vertical release and then stops"
  (cada um com as quatro diagonais)
- "last opposite pad press wins in either axis until its own release" (8 casos) →
  - "releasing the last opposite pad arrow returns to the first arrow on either axis"
  - "releasing the first opposite pad arrow keeps the last arrow on either axis"
  (cada um com os quatro pares)

#### SubchiefJourney
- "subchief blaster spends remaining resistance before meteor contacts" →
  - "subchief blaster spends its one remaining resistance before meteor contacts"
  - "subchief blaster spends its two remaining resistance before meteor contacts"
- "fatal subchief hit rewards once at lifetime boundaries and leaves recurring items in place" (16 casos) →
  - "fatal subchief contact with the ship rewards once at lifetime boundaries and leaves recurring items in place"
  - "fatal subchief contact with a laser rewards once at lifetime boundaries and leaves recurring items in place"
  - "fatal subchief contact with the blaster rewards once at lifetime boundaries and leaves recurring items in place"
  - "fatal subchief contact with the special rewards once at lifetime boundaries and leaves recurring items in place"
  (cada um com os tempos de vida 30, 31, 60 e 61)
- "simultaneous fatal contacts preserve ship laser blaster special precedence" (5 casos, 4 caminhos) →
  - "a one-life subchief falls to the ship before laser blaster or special touch it"
  - "a two-life subchief takes the ship and the laser before blaster or special"
  - "a subchief with three or four lives also spends the blaster before the special"
  - "a five-life subchief needs the special after ship laser and blaster"
- "nonfatal contacts still move fire and increment the lifetime clock at thirty and sixty" →
  - "nonfatal contacts still move fire and increment the lifetime clock at thirty"
  - "nonfatal contacts still move fire and increment the lifetime clock at sixty"

## R3. Preparação compartilhada nas suítes (09/11)

Pela decisão de 07/11 não há meta de CPD nos testes. Foi para `JourneyScenarios.kf`
só a preparação usada por mais de um arquivo: `advanceSteps`, `advanceWhilePlaying`,
`givenNormalShip`, `givenShipAt`, `givenNormalShipWithMeteorsAt`,
`givenVerticalPairInPlay`/`startVerticalPairInPlay`, `givenMeteorsAway`,
`givenMeteorsAt`, `givenMeteorsAtHeight`, `givenItemsAway`, `givenEveryBeamActiveAt`,
`evolveWeapons`, `advanceThroughExplosion`, `noProjectileActive`,
`noProjectileAppearsDuring` e `noSubchiefShotActive`. Os `prepareSubchief`,
`prepareAudit` e `prepareBoss` passaram a usar `givenMeteorsAway` e `givenItemsAway`;
o `prepareFatalContact` usa `givenEveryBeamActiveAt`; seis funções `given…` que
repetiam `Game()`, `start` e nave `Normal` passaram a chamar `givenNormalShip`.

| Verificação | Resultado |
| --- | --- |
| `npm run lint:sensor -- src/test/kof/sifuture/game/*.kf` | `SENSOR lint: PASS (0 findings)` |
| `npm run sensors:debt` | `SENSORS DEBT (report only, 40 Kof files)`; `SENSOR lint: FAIL (78 findings)`, nenhum em `src/test/kof`: 64 na produção (mesmos do R0) e 14 nas fixtures `tests/*.kf` (`high-complexity` 1, `long-function` 5, `too-many-statements` 8, que a decisão de 07/11 manteve); `SENSOR dup: FAIL (3 findings)`, os 3 grupos de produção do R0; `24 files expected, 24 tokenized` |
| `npm run check` | exit 0 |
| `node scripts/kof-tests.mjs` JVM e JS, 0.7.0 e 0.6.4 | `0 failed of 172 tests` nos quatro |
| `git diff e6703db -- src/main` | vazio |

Saída completa em `.agent/tmp/debt-r2/sensors-debt-after-r3.txt`.

## A1. KofMut completo depois do R3 (09/11)

Pré-condições, em `.agent/tmp/debt-a1/`:

| Item | Observado |
| --- | --- |
| `git diff e6703db -- src/main` | 0 linhas |
| HEAD | `68a579d` mais as mudanças não commitadas do R2/R3 (só `src/test/kof`) |
| `uptime` antes | `load average: 8.82, 9.96, 7.64` em 32 núcleos (abaixo da metade) |
| `uptime` depois | `load average: 6.85, 6.00, 5.78` |
| Kof | `kof 0.7.0` |
| Escopo | o mesmo `mut-scope.json` do R0 (24 `.kf` de `src/main/kof`) |

Comando: `kof-mut run --project . --files .agent/tmp/debt-a1/mut-scope.json --config kof-mut.json --report-dir .agent/tmp/debt-a1/kof-mut-reports --run-id <uuid>`.
Início 15:56:31, fim 17:54:32 (1h58min, `durationMs` 7077815; R0 levou 2h48min
com a máquina mais carregada). Exit **1**, `status: complete`, baseline `passed`,
**0 limitações**.

O exit e o status mudaram porque o KofMut instalado mudou entre o R0 e o A1: o
`kof-mut` agora inclui o PR #3 (`7a3df14`, `feat(frontend): traverse enum
declarations`). As 8 limitações `EnumDeclarationNode` do R0 sumiram, e o exit 1
quer dizer "terminou com sobreviventes", não "incompleto". O `toolVersion`
continua `0.1.0` nos dois relatórios. O conjunto de candidatos é o mesmo, então a
comparação pelo `id` vale.

Comparação pelo `id` (`python3 .agent/tmp/debt-a1/compare.py`, saída em
`.agent/tmp/debt-a1/compare.txt`):

| Verificação | R0 | A1 | Resultado |
| --- | ---: | ---: | --- |
| `id`s | 1167 | 1167 | mesmo conjunto |
| Mortos | 678 | 678 | os 678 do R0 continuam mortos |
| Sobreviventes | 489 | 489 | subconjunto (igual) dos do R0 |
| Mortos no R0 e não mortos no A1 | | 0 | |
| Mortos novos no A1 | | 0 | |
| Timeout, erro de compilação, erro de teste | 0 | 0 | |

A1 atendido: nenhum mutante morto no R0 voltou a sobreviver depois do R2 e do R3,
com a produção idêntica. Os testes novos não mataram nenhum mutante a mais, o que
é esperado: o R2 e o R3 só reorganizaram asserções existentes. Relatório:
`.agent/tmp/debt-a1/kofmut-a1-report.json`.

## Piloto da UI: `ControlsGuide` (10/11)

Branch `refactor/ui-pilot-controls-guide`, a partir de `84a5dbf`; validado na
árvore de trabalho antes do commit. Plano:
`.agent/execplans/ui-pilot-controls-guide.md`.

### Probe (M0)

`kof test` direto no arquivo do probe dá `PKG004` (o pacote não confere com a
pasta); o probe rodou por uma entrada em `src/test/kof`, como
`scripts/kof-tests.mjs`. Saída depois de `toggle()` e de `close()`:

```
JVM: text=[] discard=false | text=[] discard=false
JS:  text=[Menos detalhes] discard=false | text=[Mais detalhes] discard=false
```

Na JVM o texto do botão sempre lê vazio; só estado Kof comum mata mutante.

### C1. Mutação

Linha de base em `ControlsGuide.kf`: 6 candidatos, 0 mortos, 172 casos. Depois,
`kof-mut run` com `ControlsGuide.kf` e `GuideDisclosure.kf`: exit 0,
`status: complete`, 6 candidatos, 6 mortos, 0 limitações, Kof 0.7.0. As posições "Depois" vêm da rodada de mutação do `check:task` final, já com `import sifuture.GuideDisclosure` (run `1074013c`): 6 candidatos, 6 mortos.

| Antes | Depois | Teste que mata |
| --- | --- | --- |
| `8:25` `discardClick = false` | morto em `9:25` | clicking the disclosure of a new guide opens its details |
| `10:29` `expanded = false` | deixou de existir (campo saiu do `ControlsGuide`) | ver `GuideDisclosure.kf:4:21` |
| `59:58` reset no clique | morto em `113:44` (`clicked()`) | a click marked for discard keeps details closed and clears the mark |
| `64:74` reset no `pointerdown` | morto em `118:24` (`pointerDown()`) | pressing the pointer on the disclosure clears the discard mark so the next click opens |
| `66:67` reset no `blur` | morto em `122:24` (`blurred()`) | losing focus on the disclosure clears the discard mark so the next click opens |
| `95:20` `expanded = false` em `close()` | deixou de existir | ver `GuideDisclosure.kf:11:20` |
| novo `GuideDisclosure.kf:4:21` | morto | new guide details start closed |
| novo `GuideDisclosure.kf:11:20` | morto | closing open guide details closes them (e mais seis) |

### C2. Casca

0 candidatos nas linhas de handler, estilo e texto do `ControlsGuide` (o KofMut
não muta `!`, strings nem chamadas). Os 4 candidatos restantes do arquivo são os
literais de `discardClick`, todos mortos.

### C3 a C5

| Verificação | Resultado |
| --- | --- |
| `npm run lint:sensor` nos dois arquivos | `PASS (0 findings)` (eram 2) |
| `node scripts/kof-tests.mjs`, 0.7.0, JVM e JS | `0 failed of 181 tests` |
| o mesmo com `KOF` 0.6.4, JVM e JS | `0 failed of 181 tests` |
| `npm run check` | `CHECK: PASS`, mutação PASS (6/6) |
| `npm run check:task` | `CHECK:TASK: PASS`, sete jornadas PASS; `tests/browser.py` sem diff |
| `git diff --exit-code main -- src/main/kof/sifuture/GameControls.kf` | exit 0 |
| `git diff --check` | exit 0 |

A primeira rodada do `check:task` falhou em `browser:browser`:
`ControlsGuide.kf:9:5: error: Undefined variable or type: 'GuideDisclosure'
[SEM011]`. O build JS do app só segue imports, e a suíte Kof não pegou porque o
teste importa as duas classes. Corrigido com `import sifuture.GuideDisclosure` no
`ControlsGuide.kf`; a segunda rodada passou.

TDD: os testes 4 e 6 nasceram verdes (comportamento já coberto pela delegação);
sabotar `close()` derruba os testes 3 e 4. Testes 3 e 9 foram direto ao vermelho
de asserção, sem o de compilação.

### Estimativa para `GameControls` e `GameView` (não medida)

- `GameControls` (118): `==`, `||`, `&&` e `Bool` em `keyChanged`,
  `optionAvailable`, `keyboardReceiver` e nos flags de foco e tecla. São decisões
  testáveis na JVM se saírem dos lambdas; só estilo e `setDisabled` são tela.
  Estimativa: cerca de 90% matáveis, com trabalho bem maior que o do guia.
- `GameView` (75): cerca de 45 são aritmética de coordenadas de `drawImage` (só
  tela). Testáveis: `numberWidth`/`drawNumber` e escolha de quadro e sprite.
  Estimativa: entre um terço e metade.
