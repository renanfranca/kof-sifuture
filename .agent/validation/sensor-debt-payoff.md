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
