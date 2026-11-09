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
`actions/setup-node`. Pendente: a CI real, que só roda num PR para a `main` ou num
push na `main`. O push da branch `sensor-debt-payoff` não dispara o workflow.
