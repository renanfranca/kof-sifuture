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

## R5 e R4, lote 1: arquivos pequenos (11/11)

Branch `refactor/sensor-debt-batch-1`, a partir de `2c2e532`; validado na árvore
de trabalho antes do commit e entregue pelo PR #28 (`eb73913`). Handoff:
`2026-11-10_sensor-debt-r4-r5-batch-1.md`. Ordem: `BossWeapons`, `Credits`,
`Meteor`, `SubchiefShot`, `Item`, `BossSpecial`, `BossShot`. Kof 0.7.0.

### Método do RED

Cada teste novo foi escrito com o produto ainda correto, então ele nasce verde. O
RED foi observado aplicando **um mutante por vez** no arquivo (pela linha e
coluna do relatório A1), rodando a suíte inteira na JVM e restaurando o arquivo.
Depois, o KofMut só nos arquivos do lote confirmou cada mutante como morto. Em
todos os casos abaixo, o RED esperado (o teste nomeado falha por asserção) foi o
observado, e nenhum outro teste falhou além dos listados.

### Sobreviventes por arquivo

| Arquivo | Antes (A1) | Depois | Equivalentes |
| --- | --- | --- | --- |
| `BossWeapons` | 1 | 0 (29/29 mortos) | 0 |
| `Credits` | 2 | 0 (11/11 mortos) | 2 eliminados por refatoração |
| `Meteor` | 4 | 0 (26/26 mortos) | 2 eliminados por refatoração |
| `SubchiefShot` | 11 | 0 (10/10 mortos) | 2 deixaram de existir |
| `Item` | 12 | 0 (23/23 mortos) | 2 deixaram de existir |
| `BossSpecial` | 12 | 0 (15/15 mortos) | 0 |
| `BossShot` | 14 | 0 (16/16 mortos) | 1 eliminado por refatoração |
| `ShipContact` (novo) | não existia | 0 (11/11 mortos) | 0 |
| **Total** | **56** | **0** | **0** (5 eliminados) |

Coluna "Depois" já com a segunda passada (seção "Equivalentes eliminados por
refatoração"); a primeira passada parou em 5 sobreviventes.

Rodadas do KofMut (`kof-mut run --files` só com os arquivos citados), todas
`complete`, 0 limitações, 0 timeout:

| Escopo | Candidatos | Mortos | Sobreviventes | Exit | Duração |
| --- | --- | --- | --- | --- | --- |
| `BossWeapons` | 29 | 29 | 0 | 0 | 301 s |
| `Credits` | 14 | 12 | 2 | 1 | 145 s |
| `Meteor` | 41 | 39 | 2 | 1 | 482 s |
| `SubchiefShot`, `Item`, `BossSpecial`, `BossShot`, `ShipContact` | 77 | 76 | 1 | 1 | 652 s |

### Testes novos e o mutante que cada um mata

Arquivos novos por assunto, sem aumentar `BossJourney.kf` nem
`SubchiefJourney.kf`: `EnemyFireJourney.kf` (ciclo de vida dos tiros do chefe e
do subchefe), `ShipContactJourney.kf` (bordas do contato com a nave) e
`StageDriftJourney.kf` (meteoros e itens à deriva). `JourneyScenarios.kf` ganhou
`givenNormalShipAt`, `advanceSpecial` e `advanceShot`, usados por mais de um
arquivo. Posições "antes" são as do A1.

| Mutante (A1) | Teste que falhou com o mutante |
| --- | --- |
| `BossWeapons 7:25` `false → true` | a new boss arsenal at its third level does not open with the special |
| `Meteor 5:19` `true → false` | a new meteor drifts left at meteor speed; a new meteor turns to its next frame after two steps |
| `Meteor 13:21` `false → true` | a new meteor turns to its next frame after two steps |
| `SubchiefShot 6:19` `false → true` | a new subchief shot cannot hit the ship |
| `SubchiefShot 19:32` `<= → <`, `19:42` `+ → -` | a subchief shot whose top edge is level with the ship bottom hits it |
| `SubchiefShot 19:63` `\|\| → &&` | os dois testes de borda do subchefe que acertam |
| `SubchiefShot 20:17` `+ → -`, `20:21` `>= → >`, `20:50` `+ → -` | a subchief shot whose bottom edge reaches the ship top hits it |
| `SubchiefShot 20:36` `+ → -` | a subchief shot one unit below the ship misses it |
| `SubchiefShot 26:15` `< → <=` | a subchief shot stays in flight until it passes thirty units beyond the left edge |
| `Item 13:22` `false → true` | an item at the ship left edge is collected; an item whose top edge is level with the ship bottom is collected |
| `Item 19:41` `- → +`, `19:63` `- → +` | an item spawned from seed 238 sits on the lowest spawn row |
| `Item 31:15` `>= → >` | an item at the ship left edge is collected |
| `Item 32:32` `<= → <` | an item whose top edge is level with the ship bottom is collected |
| `Item 32:42` `+ → -` | os dois testes de item coletado |
| `Item 32:27`, `33:32` `&& → \|\|`, `33:37` `+ → -` | an item ten units below the ship is not collected |
| `Item 46:22` `< → <=` | an item twenty units beyond the left edge keeps drifting |
| `BossSpecial 7:19` `false → true` | a new boss special fires from below the boss (e mais dois que dependem do especial inativo) |
| `BossSpecial 24:78` `>= → >` | a charged special at the ship left edge hits it |
| `BossSpecial 24:93` `<= → <` | a charged special at the ship right edge hits it |
| `BossSpecial 25:32` `<= → <` | a charged special whose top edge is level with the ship bottom hits it |
| `BossSpecial 26:17`, `26:52` `+ → -` | os testes do especial com a borda de baixo na nave |
| `BossSpecial 26:22` `>= → >` | a charged special whose bottom edge reaches the ship top hits it |
| `BossSpecial 26:42` `<= → <` | a charged special whose bottom edge is level with the ship bottom hits it |
| `BossSpecial 25:27`, `26:32` `&& → \|\|`, `26:37` `+ → -` | a charged special spanning the ship with both edges outside it misses |
| `BossSpecial 33:15` `< → <=` | a boss special stays in flight until it passes forty-eight units beyond the left edge |
| `BossShot 6:19` `false → true` | a new boss shot cannot hit the ship |
| `BossShot 7:21` `false → true` | a boss shot fired before the boss evolves keeps its first sprite; a boss shot already in flight animates from its first sprite once the boss evolves |
| `BossShot 15:41` `< → <=` | an evolved boss shot shows its second sprite after three steps |
| `BossShot 28:77` `<= → <` | a boss shot at the ship right edge hits it |
| `BossShot 29:32` `<= → <` | a boss shot whose top edge is level with the ship bottom hits it |
| `BossShot 30:17`, `30:52` `+ → -` | os testes do tiro com a borda de baixo na nave |
| `BossShot 30:22` `>= → >` | a boss shot whose bottom edge reaches the ship top hits it |
| `BossShot 30:42` `<= → <` | a boss shot whose bottom edge is level with the ship bottom hits it |
| `BossShot 30:37` `+ → -` | a boss shot spanning the ship with both edges outside it misses |
| `BossShot 35:22` `&& → \|\|` | a boss shot already in flight animates from its first sprite once the boss evolves |
| `BossShot 37:15` `< → <=`, `37:33` `false → true` | a boss shot stays in flight until it passes forty units beyond the left edge |

Os testes de valor inicial (`false`/`true` na declaração) usam um objeto recém
construído, porque pelo `Game` o `reset()` sobrescreve o valor (como o A4 previa
para o `Meteor`). O item com semente 238 foi achado por um probe: a semente dá
`y = 203` (a última linha válida) no original e `y ≥ 204` com os dois mutantes,
igual na JVM e no JS.

Comportamento documentado, não alterado: o tiro do chefe (25 de altura) e o
especial (26) **não** acertam a nave quando passam por cima dela com as duas
bordas para fora (`y` de 96 a 99 com a nave em `y = 100`), porque a regra olha só
as bordas. Os testes "spanning the ship" fixam isso.

### Equivalentes eliminados por refatoração (11/11, segunda passada)

A primeira passada deixou 5 sobreviventes equivalentes. Regra nova do handoff
`2026-11-11_sensor-debt-batch-1-equivalents.md`: um equivalente aponta operador
redundante; antes de anotá-lo, procurar uma refatoração que preserve o
comportamento e tire o operador. As quatro existiram. Nenhum mutante foi
suprimido nem pulado, e nenhum teste mudou de expectativa: cada mutante
**deixou de existir** porque o código que o gerava saiu. Skill `refactor-design`,
um item por vez, com check de tipos e testes JVM e JS (212/212) verdes antes e
depois de cada um.

| Equivalente (posição da primeira passada) | Por que era equivalente | Refatoração que o eliminou |
| --- | --- | --- |
| `Credits 19:59` `secondY > -CREDITS_BLOCK_HEIGHT` → `>=` | `firstY + secondY` vale sempre 176 (os dois só mudam juntos, +1 e −1, e nada mais os escreve), então `secondY > -72` equivale a `firstY < 248`, já contido em `firstY < 260` | cláusula `\|\| secondY > -Rules.CREDITS_BLOCK_HEIGHT` removida; `secondY` continua sendo atualizado porque o `GameView` e o `MenuJourney` o leem |
| `Credits 16:19` `x > CREDITS_MARGIN` → `>=` | com `x == CREDITS_MARGIN`, as duas versões deixam `x` igual | `if (x > MARGIN) { x = MARGIN }` depois de `x = x + 5` virou `x = math.min(x + 5, margin)` |
| `Meteor 90:17` `y >= shipY` → `>` e `Meteor 91:75` `y + METEOR_HEIGHT <= shipY + SHIP_HEIGHT` → `<` | a união das duas faixas de borda (`[shipY−18, shipY+20]`) não muda com altura 18 | `touchesShip(Int shipX, Int shipY)` mantém a assinatura e delega ao `ShipContact` (`withinShipWidth` e `edgesWithinShipHeight`), a mesma fórmula; as comparações ficam onde os testes do tiro do chefe e do especial (alturas 25 e 26) as matam |
| `BossShot 34:40` `animationSteps < 5` → `<=` | o único leitor, `spriteFrame()`, devolve 2 para qualquer valor `>= 5` | `&& animationSteps < 5` removido; o contador continua limitado porque o tiro anda 4 por passo, se desativa ao passar de `x < -40` e aí zera o contador, e `fire()` também zera; `BossJourney.kf:1021` (contador 0 depois da limpeza) segue verde |

**Desvios do handoff, com motivo:**

1. **`math.min` com local tipada.** `math.min(x + 5, Rules.CREDITS_MARGIN)` não
   compila: `SEM025 Cannot resolve method 'min' on namespace 'math'`, no 0.7.0 e no
   0.6.4. Probe mínimo fora de pasta com ponto: o typer só resolve `math.min`
   quando o argumento lido de um `static final` passa por uma local com tipo
   explícito (`Int m = Rules.MARGIN` compila; `Rules.MARGIN` direto ou `var m =
   Rules.MARGIN` dão `SEM025`). Contorno igual ao que o `Meteor.relocate()` já usa
   para `rng.int`: `Int margin = Rules.CREDITS_MARGIN`. Lacuna do Kof, candidata a
   issue.
2. **`ShipContact` com `Int` sem passar de 4 parâmetros.** O handoff pedia
   `ShipContact` recebendo `shipX` e `shipY` no lugar de `Ship`, o que dá
   `edgeTouchesShip(x, y, height, shipX, shipY)`, com 5 parâmetros, e
   `too-many-parameters` (limite 4, `SENSORS.md:59`; o mesmo achado da primeira
   passada). O limite não pode mudar. Saída: as comparações foram para
   `withinShipWidth(Int x, Int shipX)` e `edgesWithinShipHeight(Int y, Int height,
   Int shipY)` (com `edgeWithinShipHeight(Int edgeY, Int shipY)`); o
   `edgeTouchesShip(x, y, height, Ship ship)` continua com a mesma assinatura e só
   compõe as duas, então `BossShot`, `BossSpecial`, `SubchiefShot` e `Item` não
   mudaram. O `Meteor` compõe as mesmas duas com `Rules.METEOR_HEIGHT`.

**KofMut nos quatro arquivos alterados** (`kof-mut run --files <scope.json>` com
`BossShot`, `Credits`, `Meteor` e `ShipContact`; load 8,4 em 32 núcleos):
`complete`, 0 limitações, **64 candidatos, 64 mortos, 0 sobreviventes**, 0 timeout,
exit 0, 627 s. Por arquivo: `BossShot` 16/16, `Credits` 11/11, `Meteor` 26/26,
`ShipContact` 11/11. Antes, os mesmos arquivos tinham 84 candidatos e 5
sobreviventes.

Mutantes que deixaram de existir, casados pelo texto da linha, coluna e
substituto (os `id`s são `arquivo:offset:substituto`, e o `import` novo do
`Meteor` desloca todos os offsets dele, então só o `id` exato superestima a
troca: 69 removidos e 49 novos):

- os 5 equivalentes acima (`Credits:341:>=`, `Credits:547:>=`, `Meteor:2575:>`,
  `Meteor:2696:<`, `BossShot:781:<=`);
- mortos que saíram com o código: `BossShot:763:||` e `:820:-` (a linha
  `animationSteps` antiga), `Credits:319:-`, `:513:<=` e `:536:&&`, os 17 do
  `touchesShip` antigo do `Meteor` (`2514` a `2705`) e os 11 do `ShipContact`
  antigo (`96` a `324`).

Mutantes novos, todos mortos: `BossShot:798:-`, `Credits:374:-`, `Credits:506:<=`,
`Meteor:2571:||` e, no `ShipContact`, `121:||`, `222:>`, `231:||`, `236:<`,
`245:-`, `368:&&`, `394:-`, `481:>`, `490:||`, `499:<`, `508:-`. Comparação
feita com os relatórios de `.agent/tmp/debt-batch1/mut-{Credits,Meteor,rest}` e
`.agent/tmp/debt-batch1-equivalents/reports`.

O `Meteor` e o `Credits` antes deixavam 2 equivalentes cada porque a regra estava
escrita com uma condição que nunca decidia nada; o `ShipContact` mata o mesmo
operador porque é usado por formas mais altas que a nave. Isso confirma a regra
nova: neste lote, todo equivalente tinha uma refatoração que o eliminava.

### R4 (uma refatoração por vez, verde a cada passo, JVM e JS)

| Arquivo | Antes | Refatoração | Depois |
| --- | --- | --- | --- |
| `BossWeapons` | 3 achados (`attemptFire`) | `specialDue()`, `fireInterval()`, `fireVolley()` com `fireFreeShot()` e `countTowardSpecial()`, condições originais preservadas | 0 |
| `Meteor` | 4 achados (`advance`) | `advanceImpact()`, `advanceFrames()`, `turnFrame()` | 0 |
| `Item` | 1 achado (`advance`) | `advanceEffect()`, `advanceFrames()`, `turnFrame()`, `swingFrame()` | 0 |
| CPD `BossShot:25` ↔ `SubchiefShot:14` | 1 grupo | `ShipContact.kf`: `edgeTouchesShip(x, y, height, ship)` e `edgeWithinShipHeight`, usados por `BossShot`, `SubchiefShot`, `BossSpecial` e `Item` | `SENSOR dup: PASS (0 findings)` |

Primeira versão com `shipX, shipY` deu `too-many-parameters` (5); virou `Ship
ship` (Preserve Whole Object). Desvio encontrado: sem `import
sifuture.game.ShipContact`, o `check` pelo `Main.kf` passa, mas a suíte pela
entrada única falha com `SEM015 Undefined function: 'edgeTouchesShip'` (mesmo
tipo do `testRows`). Corrigido com o import explícito nos quatro arquivos.

### Contagem de casos (A2)

| Kof | JVM | JS |
| --- | --- | --- |
| 0.7.0 | 181 → 212 | 181 → 212 |
| 0.6.4 | 181 → 212 | 181 → 212 |

### Fechamento do lote

| Verificação | Resultado |
| --- | --- |
| `npm run lint:sensor` em cada arquivo do lote e no `ShipContact.kf` | `PASS (0 findings)` |
| `npm run check` | todos os passos PASS até `dup:sensor` (`7 files expected, 7 tokenized`) e `docs:sensor`; **`mutation` FAIL**: 147 candidatos, 144 mortos, 3 sobreviventes (`Meteor` 2, `BossShot` 1), os equivalentes acima; 1278 s |
| `npm run check:task` | o mesmo FAIL em `mutation`; as jornadas ficaram `NOT RUN`; 1197 s |
| sete jornadas rodadas à parte (`.agent/tmp/debt-tools/journeys.sh`) | 7/7 exit 0; 186 PNG |
| pixels decodificados contra o R0 (`debt-tools/pixels.py`) | `common=186 only_a=0 only_b=0 pixel_diff=0` |
| `git diff --check` | exit 0 |

A primeira passada parou aqui: o `check` reprovava pelos 3 equivalentes da
produção alterada. Fechamento depois da segunda passada (Kof 0.7.0 salvo onde
indicado; evidência em `.agent/tmp/debt-batch1-equivalents/`):

| Verificação | Resultado |
| --- | --- |
| `npm run lint:sensor` em `Credits`, `Meteor`, `BossShot` e `ShipContact` | `PASS (0 findings)` |
| `npm run dup:sensor` | `PASS (0 findings)`, `8 files expected, 8 tokenized` |
| `npm run check` | `CHECK: PASS`, 11 passos PASS; `mutation` PASS (não SKIP): 141 candidatos, 141 mortos, 0 sobreviventes nos 8 arquivos alterados da branch; 1037 s |
| `npm run check:task` | `CHECK:TASK: PASS`, 18 passos PASS, incluindo `mutation` (141/141) e as sete jornadas; 1071 s |
| sete jornadas rodadas à parte (`debt-tools/journeys.sh`) | 7/7 exit 0; 186 PNG |
| pixels decodificados contra o R0 (`debt-r0/journeys-1/png`) | `common=186 only_a=0 only_b=0 pixel_diff=0` |
| casos, 0.7.0 | 212 em JVM e 212 em JS, 0 falhas |
| casos, 0.6.4 | 212 em JVM e 212 em JS, 0 falhas; check de tipos JVM e JS OK |
| `git diff --check` | exit 0 |

### Tempo

De 10:32 a 12:11 (1h39), com uma interrupção curta. Divisão aproximada: R5 e R4
dos sete arquivos, cerca de 37 min; KofMut por arquivo, 26 min (301 + 145 + 482 +
652 s); fechamento (`check`, `check:task`, jornadas duas vezes), cerca de 50 min.

Estimativa para `Ship` ao `SpecialBeam` (A1: 743 candidatos e **234**
sobreviventes; o handoff diz 232, mas a soma da própria lista dá 234): o lote 1
teve 214 candidatos e 56 sobreviventes no A1. A mutação escala com os
candidatos (cerca de 3,5 vezes, perto de 1h30 só de KofMut por arquivo); o trabalho de
testes escala com os sobreviventes (cerca de 4,2 vezes, perto de 2h30); `Game`,
`Weapons` e `SpecialBeam` têm refatorações maiores. Total esperado: 5 a 7 horas
em dois ou três lotes, mais o fechamento de cada um.

## R5 e R4, lote 2: `Shot`, `Blaster`, `Ship` e `SpecialBeam` (12/11)

Branch `refactor/sensor-debt-batch-2`, a partir de `eb73913`. Plano:
`.agent/execplans/sensor-debt-batch-2.md`. Kof 0.7.0, com 0.6.4 onde indicado.
Evidência em `.agent/tmp/debt-batch2/`.

### M0. Linha de base

`kof-mut run --files mut-scope.json` só nos quatro arquivos, das 10:10 às 10:45
(load 9,3 em 32 núcleos): `complete`, 0 limitações, **244 candidatos, 142 mortos,
102 sobreviventes**, 0 timeout, exit 1, 2090 s. Os 102 `id`s são os mesmos do A1
de 09/11: os testes do lote 1 não mataram nenhum deles.

| Arquivo | Candidatos | Sobreviventes no A1 | Sobreviventes no M0 |
| --- | --- | --- | --- |
| `Shot` | 48 | 17 | 17 |
| `Blaster` | 40 | 17 | 17 |
| `Ship` | 55 | 16 | 16 |
| `SpecialBeam` | 101 | 52 | 52 |

### Método

O mesmo do lote 1, automatizado: `tools/redcheck.py` copia o projeto, aplica
**um** sobrevivente do M0 (linha, coluna, original e substituto), roda a suíte
inteira na JVM, guarda os testes que falharam e descarta a cópia. Os testes foram
escritos numa cópia do projeto enquanto o M0 rodava e só vieram para o
repositório depois dele, para não mexer na linha de base. Saídas:
`red-m1.txt` (`Shot` e `Blaster`), `red-m2.txt` (`Ship`) e `red-m3.txt`
(`SpecialBeam`).

Resultado: dos 102 sobreviventes, **79** fazem falhar só testes novos, sempre
por asserção, e nenhum teste antigo falhou. Os outros **23** não fazem nenhum
teste falhar; são os equivalentes da seção seguinte, todos previstos pela leitura
do código antes do RED.

### Testes novos e o mutante que cada um mata

55 testes em três arquivos novos por assunto: `PlayerFireJourney.kf` (voo e
acerto do laser e do blaster), `ShipMotionJourney.kf` (nave parada, fim do
reinício, direção depois do renascimento) e `SpecialBeamJourney.kf` (ciclo do
raio especial e alcance contra meteoro, subchefe e chefe). `givenMeteorAt` foi
para o `JourneyScenarios.kf`, porque dois arquivos o usam. Posições do M0.

| Mutante (M0) | Teste(s) que falharam com o mutante |
| --- | --- |
| `Blaster` `9:19` `false → true` | a new blaster fires from the ship position; a blaster hits a meteor level with its rear; a blaster hits a meteor level with its front; a blaster hits a meteor whose top is level with the blaster bottom; a blaster hits a meteor whose bottom touches the blaster top |
| `Blaster` `27:25` `< → <=` | a blaster shows its second sprite after two steps of flight |
| `Blaster` `28:25` `> → >=` | a blaster shows its fourth sprite after four steps of flight |
| `Blaster` `29:28` `- → +` | a blaster shows its second sprite after two steps of flight; a blaster shows its fourth sprite after four steps of flight |
| `Blaster` `33:43` `>= → >` | a blaster hits a meteor level with its rear |
| `Blaster` `33:55` `<= → <` | a blaster hits a meteor level with its front |
| `Blaster` `34:31` `<= → <` | a blaster hits a meteor whose top is level with the blaster bottom |
| `Blaster` `35:19` `+ → -`, `35:41` `>= → >`, `35:80` `+ → -` | a blaster hits a meteor whose bottom touches the blaster top |
| `Blaster` `35:53` `+ → -` | a blaster misses a meteor below it |
| `Blaster` `43:43` `+ → -` | a blaster slows down during its fourth step of flight |
| `Blaster` `45:39` `+ → -` | a blaster shows its second sprite after two steps of flight; a blaster shows its fourth sprite after four steps of flight; a blaster slows down during its fourth step of flight |
| `Blaster` `46:19` `> → >=` | a blaster stays in flight when it reaches the right edge of the world |
| `Shot` `8:19` `false → true`, `21:43` `- → +` | a new laser shot fires from the middle of the ship nose |
| `Shot` `36:19` `> → >=` | a laser shot stays in flight when it reaches the right edge of the world |
| `Shot` `47:20` `+ → -`, `47:79` `+ → -`, `48:39` `+ → -` | a laser shot whose front enters the lower half of a meteor hits it; a laser shot whose front touches the meteor left edge low on it hits it; a laser shot whose front touches the meteor right edge low on it hits it; a laser shot whose top edge is level with the meteor bottom hits it |
| `Shot` `47:40` `>= → >` | a laser shot whose front touches the meteor left edge low on it hits it |
| `Shot` `47:72` `<= → <` | a laser shot whose front touches the meteor right edge low on it hits it |
| `Shot` `48:32` `<= → <` | a laser shot whose top edge is level with the meteor bottom hits it |
| `Shot` `49:40` `>= → >` | a laser shot whose front touches the meteor left edge high on it hits it |
| `Shot` `49:52` `<= → <` | a laser shot whose tail touches the meteor right edge high on it hits it; a laser shot past the meteor whose bottom edge is level with its middle hits it |
| `Shot` `50:41` `>= → >` | a laser shot whose bottom edge touches the meteor top hits it |
| `Shot` `50:74` `<= → <` | a laser shot past the meteor whose bottom edge is level with its middle hits it |
| `Ship` `10:17` `false → true`, `11:18` `false → true`, `12:15` `false → true`, `13:17` `false → true` | a new ship holds still until a direction is pressed |
| `Ship` `16:23` `false → true` | a new ship that finishes its restart on the result screen faces forward |
| `Ship` `58:30` `false → true` | a ship destroyed while facing right respawns facing forward |
| `Ship` `65:30` `false → true` | a ship finishing its restart while pressing right faces forward on that step |
| `Ship` `74:24` `&& → \|\|` | a ship finishing its restart while pressing right faces forward on that step; a ship destroyed while facing right respawns facing forward |
| `Ship` `87:26` `== → !=`, `88:41` `+ → -` | a restarting ship becomes normal on its forty-fifth result step; a ship destroyed while facing right respawns facing forward |
| `Ship` `89:30` `== → !=` | a restarting ship stays in restart for forty-four result steps |
| `SpecialBeam` `11:19` `false → true` | a new special beam stays put until it is fired |
| `SpecialBeam` `41:53` `- → +` | a special beam hit by a meteor flashes for three steps |
| `SpecialBeam` `42:19` `> → >=` | a special beam stays in flight when it reaches the right edge of the world |
| `SpecialBeam` `47:32` `> → >=` | a special beam destroyed by meteors no longer hits them |
| `SpecialBeam` `47:43` `>= → >` | a special beam hits a meteor level with its rear |
| `SpecialBeam` `47:55` `<= → <` | a special beam hits a meteor level with its front |
| `SpecialBeam` `48:31` `<= → <` | a special beam hits a meteor whose top is level with the beam bottom |
| `SpecialBeam` `48:36` `+ → -` | a special beam hits a meteor whose top is level with the beam bottom; a special beam hits a meteor in the lower half of the beam |
| `SpecialBeam` `48:42` `\|\| → &&` | a special beam hits a meteor whose top is level with the beam bottom; a special beam hits a meteor in the lower half of the beam; a special beam hits a meteor overlapping the beam top; a special beam hits a meteor whose bottom touches the beam top |
| `SpecialBeam` `49:19` `+ → -`, `49:80` `+ → -` | a special beam hits a meteor overlapping the beam top; a special beam hits a meteor whose bottom touches the beam top |
| `SpecialBeam` `49:41` `>= → >` | a special beam hits a meteor whose bottom touches the beam top |
| `SpecialBeam` `49:53` `+ → -` | a special beam misses a meteor below it |
| `SpecialBeam` `54:21` `>= → >` | a special beam reaches a subchief level with its rear |
| `SpecialBeam` `54:26` `&& → \|\|`, `54:48` `&& → \|\|`, `60:16` `false → true` | a special beam does not reach a subchief beyond its front; a special beam does not reach a subchief below it |
| `SpecialBeam` `54:37` `<= → <` | a special beam reaches a subchief level with its front |
| `SpecialBeam` `55:28` `&& → \|\|`, `56:33` `&& → \|\|`, `56:44` `+ → -` | a special beam does not reach a subchief below it |
| `SpecialBeam` `55:39` `<= → <` | a special beam reaches a subchief whose top is level with the beam bottom |
| `SpecialBeam` `55:44` `+ → -` | a special beam reaches a subchief level with its rear; a special beam reaches a subchief level with its front; a special beam reaches a subchief whose top is level with the beam bottom; a special beam reaches a subchief in the lower half of the beam |
| `SpecialBeam` `55:50` `\|\| → &&` | a special beam reaches a subchief level with its rear; a special beam reaches a subchief level with its front; a special beam reaches a subchief whose top is level with the beam bottom; a special beam reaches a subchief in the lower half of the beam; a special beam reaches a subchief overlapping the beam top; a special beam reaches a subchief whose bottom touches the beam top |
| `SpecialBeam` `56:23` `+ → -`, `56:54` `+ → -` | a special beam reaches a subchief overlapping the beam top; a special beam reaches a subchief whose bottom touches the beam top |
| `SpecialBeam` `56:28` `>= → >` | a special beam reaches a subchief whose bottom touches the beam top |
| `SpecialBeam` `65:20` `>= → >` | a special beam reaches a boss level with its rear |
| `SpecialBeam` `65:35` `<= → <` | a special beam reaches a boss level with its front |
| `SpecialBeam` `66:27` `&& → \|\|`, `67:32` `&& → \|\|`, `68:32` `&& → \|\|` | a special beam does not reach a boss below it; a special beam does not reach a boss above it |
| `SpecialBeam` `66:37` `<= → <` | a special beam reaches a boss whose top is level with the beam bottom |
| `SpecialBeam` `66:42` `+ → -` | a special beam reaches a boss level with its rear; a special beam reaches a boss level with its front; a special beam reaches a boss whose top is level with the beam bottom; a special beam reaches a boss in the lower half of the beam |
| `SpecialBeam` `66:48` `\|\| → &&` | a special beam reaches a boss level with its rear; a special beam reaches a boss level with its front; a special beam reaches a boss whose top is level with the beam bottom; a special beam reaches a boss in the lower half of the beam; a special beam reaches a boss whose bottom overlaps the beam; a special beam reaches a boss whose bottom touches the beam top |
| `SpecialBeam` `67:22` `+ → -`, `67:52` `+ → -` | a special beam reaches a boss whose bottom overlaps the beam; a special beam reaches a boss whose bottom touches the beam top |
| `SpecialBeam` `67:27` `>= → >` | a special beam reaches a boss whose bottom touches the beam top |
| `SpecialBeam` `67:42` `+ → -`, `68:42` `+ → -` | a special beam does not reach a boss below it |
| `SpecialBeam` `83:22` `> → >=` | a fired special beam shows its first frame; a special beam hit by a meteor flashes for three steps |

Testes de valor inicial usam um objeto recém construído, como no lote 1. Os
`Bool` iniciais do `Ship` (`left`, `right`, `up`, `down`, `rightFrame`) **não**
eram equivalentes: um `Ship()` novo anda com eles, e o `advanceVisual()` (tela de
resultado) termina o reinício sem zerar `rightFrame`, então a nave que reinicia
ali mostra a direção guardada.

### Equivalentes eliminados por refatoração

Os 23 equivalentes tinham uma refatoração que preserva o comportamento e tira o
operador. Nenhum foi suprimido nem anotado, e nenhum teste mudou de expectativa.
Cada refatoração entrou sozinha, com a suíte verde na JVM e no JS antes da
próxima. As regras de acerto reescritas foram comparadas com as originais ponto a
ponto numa grade de coordenadas (Python, mesma fórmula): 0 diferenças para o
`Shot`, o `Blaster` e as três chamadas do `SpecialBeam`.

| Equivalente (M0) | Por que era equivalente | Refatoração |
| --- | --- | --- |
| `Shot 7:21` `animated = false`, `9:19` `impact = false`, `15:20` `animated = false` no `reset()` | `fire()` sobrescrevia os dois campos, e o `GameView` só os lê com o tiro ativo | `fire()` chama `reset()`; os campos perderam o valor inicial e o construtor chama `reset()`. O `reset()` agora decide o estado do tiro disparado, e os testes de voo matam os seus literais |
| `Shot 48:20` `y >= m.y` → `>` | na borda `y == m.y` a segunda cláusula (borda de baixo) já acerta com a faixa horizontal mais larga | `hitsMeteor` virou `overlaps(m) && (frontInside \|\| bottomInside)`: os retângulos se cruzam e a frente ou a borda de baixo ainda está dentro do meteoro (mesma região) |
| `Blaster 34:19` `m.y >= y` → `>` e `35:75` `m.y + METEOR_HEIGHT <= y + 21` → `<` | as duas faixas de borda se juntam num intervalo só, `[y − 18, y + 21]` | `m.y + Rules.METEOR_HEIGHT >= y && m.y <= y + 21` |
| `Blaster 50:43` `x = x + 4` → `x - 4` | o passo que move 4 é o mesmo que chama `reset()`; o blaster some antes de ser desenhado ou de colidir | linha removida |
| `Ship 25:22` `rightFrame = false` no `reset()` | o `clearInput()` chamado logo depois faz o mesmo | linha removida |
| `Ship 77:15`, `78:15`, `79:15`, `80:15` (limites da tela) | na borda, `if (x < 0) { x = 0 }` e `x <= 0` dão o mesmo `x` | `math.clamp(x, 0, rightBound)` e `math.clamp(y, top, bottom)`, com locais `Int` tipadas (o desvio `SEM025` do lote 1) |
| `SpecialBeam 38:30` `contactSteps > 0` → `>=` e `41:26` `hitSteps > 0` → `>=` | negativo e zero são lidos igual em todo lugar (`> 0`) | `math.max(contactSteps - 1, 0)` e `math.max(hitSteps - 1, 0)` |
| `SpecialBeam 48:19`, `49:75` (meteoro), `55:23`, `56:49` (subchefe), `66:22`, `67:47`, `68:27`, `68:47` (chefe) | "alguma borda do alvo dentro de `[y, y + 32]`" dá o mesmo que o cruzamento de intervalos, porque as faixas das bordas se encostam (no chefe, a borda do meio fecha o buraco entre o topo e a base) | uma regra só, `reaches(left, top, height)`: `left >= x && left <= x + 319 && top + height >= y && top <= y + 32`; `beginsContact` guarda a regra de contato comum ao subchefe e ao chefe |
| `SpecialBeam 78:19` `lives <= 0` → `<` no `hit()` | `deathSteps` vale sempre 0 enquanto o raio está vivo | `deathSteps = 0` sem condição |

O `ShipContact.kf` não mudou: a regra dele é de bordas e vale para formas mais
altas que a nave (o tiro do chefe e o especial do chefe passam por cima sem
acertar), ao contrário da regra do raio.

Detalhe do `Ship`: no passo de explosão o `advance()` não chama mais o
`keepInBounds()`. A nave explodindo não se move, e a posição já veio limitada do
passo anterior ou do renascimento (`x = 5`, `y = 100`). Manter a chamada só
criaria equivalentes novos.

### R4 (lint)

| Arquivo | Antes | Refatoração | Depois |
| --- | --- | --- | --- |
| `Blaster` | `too-many-statements` em `advance` | `advanceFlight()` e `advanceImpact()` | 0 |
| `Ship` | 4 achados em `advance` | `advanceExplosion()`, `loseLife()`, `advanceRestart()`, `steer()`, `keepInBounds()` e `movingLeft/Right/Up/Down()`; `movingRight()` serve ao movimento e à direção do sprite | 0 |
| `SpecialBeam` | `high-complexity` em `beginsBossContact` | `reaches()` e `beginsContact()` | 0 |
| `Shot` | 0 | `overlaps()` | 0 |

`SpecialBeamJourney.kf` deu `looping-test` na primeira versão (um `for` no corpo
do teste); o laço foi para `hitBeam(beam, times)`.

### Sobreviventes por arquivo

| Arquivo | M0 | Depois | Mortos por teste novo | Equivalentes eliminados |
| --- | --- | --- | --- | --- |
| `Shot` | 17 (48 candidatos) | 0 (38/38) | 13 | 4 |
| `Blaster` | 17 (40) | 0 (32/32) | 14 | 3 |
| `Ship` | 16 (55) | 0 (46/46) | 11 | 5 |
| `SpecialBeam` | 52 (101) | 0 (48/48) | 41 | 11 |
| **Total** | **102 (244)** | **0 (164/164)** | **79** | **23** |

Os `id`s do KofMut são `arquivo:offset:substituto`, e as refatorações mudam os
offsets: comparando M0 e A1 pelo `id` exato, 207 saíram, 127 são novos e 37
ficaram iguais.

### Critérios de aceite

| # | Comando | Observado | Evidência |
| --- | --- | --- | --- |
| A1 | `kof-mut run --files mut-scope.json --report-dir .agent/tmp/debt-batch2/a1` | `complete`, 0 limitações, 164 candidatos, 164 mortos, 0 sobreviventes, 0 timeout, exit 0, 1091 s (10:53 a 11:12, load 22 no início por causa das jornadas) | `a1-report.json`, `a1.log` |
| A2 | `tools/redcheck.py` com cada sobrevivente do M0 | 79 mutantes, cada um derrubando só testes novos, sempre por asserção | `red-m1.txt`, `red-m2.txt`, `red-m3.txt`; tabela acima |
| A3 | leitura do código, RED e KofMut final | 23 equivalentes, todos eliminados por refatoração; nenhum anotado | seção de equivalentes |
| A4 | `npm run lint:sensor --` nos quatro arquivos, nos três testes novos e no `JourneyScenarios.kf` | `PASS (0 findings)`; `dup:sensor` `PASS (0 findings)`, `4 files expected, 4 tokenized` | rodado no repositório |
| A5 | `git diff --name-only main -- src/main` | só `Blaster.kf`, `Ship.kf`, `Shot.kf` e `SpecialBeam.kf` | rodado no repositório |
| A6 | `node scripts/kof-tests.mjs --target jvm` e `--target js`, com 0.7.0 e com `KOF=…/kof-0.6.4…/bin/kof` | `0 failed of 267 tests` nos quatro (eram 212); check de tipos JVM e JS no 0.6.4 OK | rodado no repositório |
| A7 | `debt-tools/journeys.sh` e `debt-tools/pixels.py` contra `debt-r0/journeys-1/png` | 7/7 exit 0, 186 PNG; `common=186 only_a=0 only_b=0 pixel_diff=0` | `journeys/summary.txt`, `pixels.out` |
| A8 | validação final do plano | ver "Fechamento do lote" | `final/` |

### Fechamento do lote

Validação final do plano, nesta ordem, de 11:13 a 11:52 (evidência em
`.agent/tmp/debt-batch2/final/`):

| Comando | Resultado |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | exit 0, 15 testes OK |
| `npm run test:sensors` | exit 0, 39 pass, 0 fail |
| `npm run check` | `CHECK: PASS`, 11 passos PASS; `mutation` PASS (não SKIP): 164 candidatos, 164 mortos, 0 sobreviventes nos quatro arquivos; 1022 s |
| `npm run check:task` | `CHECK:TASK: PASS`, `mutation` (164/164) e as sete jornadas PASS; 1279 s |
| `git diff --check` | exit 0 |

Esta seção entrou depois da validação (só texto); `npm run docs:sensor` e
`git diff --check` rodaram de novo sobre ela.

### Tempo

M0 de 10:10 a 10:45 (35 min). Análise dos sobreviventes, testes, RED automatizado
e R4 numa cópia do projeto, de 10:10 a 10:50, em paralelo ao M0. Pré-checagem do
KofMut na cópia (164/164, 24 min) junto com as jornadas (cerca de 5 min); A1 no
repositório de 10:53 a 11:12.

Estimativa para o lote 3 (`Subchief` 18, `Boss` 30 e `Weapons` 42 sobreviventes
no A1) e o lote 4 (`Game`, 42): este lote pagou 102 sobreviventes em cerca de
1h05 até o A1, porque a maior parte dos equivalentes vinha de uma regra
geométrica repetida. O `Weapons` tem a mesma regra de bordas para laser e blaster
contra subchefe e chefe (`hitSubchiefLaser`, `hitBossLaser`, `hitSubchiefBlaster`,
`hitBossBlaster`), então a refatoração tende a seguir o `reaches()` daqui. Lote 3:
cerca de 1h30 mais o fechamento (cerca de 45 min). Lote 4 (`Game`, com
`step()` grande): 2h a 3h, porque o R4 domina.

## R5 e R4, lote 3: `Subchief`, `Boss` e `Weapons` (12/11)

Branch `refactor/sensor-debt-batch-3`, a partir de `2f22f11`. Plano:
`.agent/execplans/sensor-debt-batch-3.md`. Kof 0.7.0, com 0.6.4 onde indicado.
Evidência em `.agent/tmp/debt-batch3/`.

### M0. Linha de base

`kof-mut run --files mut-scope.json` só nos três arquivos, das 12:23 às 12:59
(load 4,6 em 32 núcleos): `complete`, 0 limitações, **311 candidatos, 221
mortos, 90 sobreviventes**, 0 timeout, exit 1, 2158 s. Os 90 `id`s são os mesmos
do A1 de 09/11: os lotes 1 e 2 não mataram nenhum deles.

| Arquivo | Candidatos | Sobreviventes no A1 | Sobreviventes no M0 |
| --- | --- | --- | --- |
| `Subchief` | 71 | 18 | 18 |
| `Boss` | 101 | 30 | 30 |
| `Weapons` | 139 | 42 | 42 |

### Método

O mesmo do lote 2. Os testes e as refatorações foram escritos numa cópia do
projeto enquanto o M0 rodava, e só vieram para o repositório depois dele.
`.agent/tmp/debt-batch2/tools/redcheck.py` aplicou **um** sobrevivente por vez
na cópia (com os testes novos e a produção ainda original), rodou a suíte inteira
na JVM e guardou os testes que falharam. Saída: `red.txt`; lista aplicada:
`specs-m0.json`.

Resultado: dos 90 sobreviventes, **68** fazem falhar só testes novos, sempre por
asserção, e nenhum teste antigo falhou. Os outros **22** não fazem nenhum teste
falhar; são os da seção "Equivalentes eliminados por refatoração", todos
previstos pela leitura do código antes do RED.

Conferências do planejamento:
- achado 1: a tabela de uniões contínuas está certa. As cinco regras marcadas
  "sim" viraram sobreposição de faixas com 0 diferenças na grade (abaixo); as duas
  marcadas "não" ficaram como estavam e ganharam testes que fixam o buraco;
- achado 2: `grep` em `src` e `tests` no começo do R4 confirmou que o `Game`
  (`Game.kf:258-262`) e o `SubchiefJourney.kf:426` só chamam
  `Subchief.damage` e `Weapons.hitSubchief*` como instrução, sem ler o retorno;
- achado 3: `((0 - 1) / 4) % 3` dá 0 em JVM e JS, no 0.7.0 e no 0.6.4 (probe
  `kof test` fora de diretório com ponto, por causa do KofLang/Kof4j#999). A
  divisão inteira trunca para zero, como diz
  `docs/language-reference/expressions.md`, então a guarda `frenzySteps > 0` era
  redundante e saiu;
- achado 4: o passo até o destino virou `stepToward()` em `Course.kf`;
- achado 5: o `long-file` caiu quando as regras de alvo foram para o projétil
  que as aplica (`Shot` e `Blaster`), sem dividir o `Weapons` no meio.
- Achado novo: o `Game.trySpecial()` só chama `weapons.fireSpecial()` depois de
  `canSpecial()`, então a guarda de `fireSpecial` não se alcança pelo jogo. Ela
  continua, porque protege a API do `Weapons`, e o teste no nível do `Weapons`
  mata o `false → true` dela.

### Testes novos e o mutante que cada um mata

43 testes em quatro arquivos novos por assunto: `EnemyBodyContactJourney.kf`
(corpo do subchefe e do chefe contra a nave, chefe absorvendo meteoro),
`EnemyMotionJourney.kf` (passo até o destino, quadro do chefe em frenesi),
`PlayerHitsEnemyJourney.kf` (laser e blaster contra subchefe e chefe) e
`WeaponReadinessJourney.kf` (primeiro blaster no nível dois, especial sem carga).
`givenNormalSubchiefAt` e `givenNormalBossAt` saíram do `SpecialBeamJourney.kf`
para o `JourneyScenarios.kf`, porque três arquivos os usam. Posições do M0.

| Mutante (M0) | Teste(s) que falharam com o mutante |
| --- | --- |
| `Boss` `49:34` `&& → \|\|`, `49:51` `&& → \|\|`, `49:73` `&& → \|\|` | a boss does not absorb a meteor one unit left of it; a boss does not absorb a meteor far above it; a boss does not absorb a meteor one unit below it |
| `Boss` `50:33` `&& → \|\|`, `51:55` `&& → \|\|` | a boss does not absorb a meteor far above it; a boss does not absorb a meteor one unit below it |
| `Boss` `50:45` `<= → <` | a boss absorbs a meteor whose top is level with the boss bottom |
| `Boss` `51:28` `+ → -`, `51:50` `>= → >`, `51:94` `+ → -` | a boss absorbs a meteor whose bottom touches the boss top |
| `Boss` `51:67` `+ → -` | a boss does not absorb a meteor one unit below it |
| `Boss` `57:54` `<= → <` | a ship at the boss right edge touches it |
| `Boss` `57:59` `+ → -` | a ship at the boss right edge touches it; a ship whose top is level with the boss bottom touches it; a ship whose bottom touches the boss top touches it |
| `Boss` `58:27` `&& → \|\|`, `59:47` `&& → \|\|` | a ship far above the boss does not touch it; a ship one unit below the boss does not touch it |
| `Boss` `58:37` `<= → <`, `58:42` `+ → -` | a ship whose top is level with the boss bottom touches it |
| `Boss` `58:48` `\|\| → &&` | a ship whose top is level with the boss bottom touches it; a ship whose bottom touches the boss top touches it |
| `Boss` `59:22` `+ → -`, `59:42` `>= → >`, `59:82` `+ → -` | a ship whose bottom touches the boss top touches it |
| `Boss` `59:57` `+ → -` | a ship one unit below the boss does not touch it |
| `Boss` `89:87` `/ → *` | a frenzy boss still shows its first frame on its third frenzy step |
| `Boss` `116:15` `< → <=`, `117:20` `> → >=` | a boss level with its destination height keeps that height while moving sideways |
| `Subchief` `43:17` `>= → >`, `45:24` `>= → >` | a subchief at the ship left edge whose bottom touches the ship top hits it |
| `Subchief` `43:32` `<= → <` | a subchief at the ship right edge hits it |
| `Subchief` `44:19` `>= → >` | a subchief at the ship right edge hits it; a subchief near the ship right edge whose top is level with the ship top hits it |
| `Subchief` `44:29` `&& → \|\|`, `45:34` `&& → \|\|` | a subchief far below the ship misses it; a subchief whose top is five units above the ship top misses it; a subchief whose top is one unit above the ship top misses it |
| `Subchief` `44:34` `<= → <` | a subchief near the ship right edge whose top is level with the ship bottom hits it |
| `Subchief` `44:44` `+ → -` | a subchief at the ship right edge hits it; a subchief near the ship right edge whose top is level with the ship top hits it; a subchief near the ship right edge whose top crosses the ship middle hits it; a subchief near the ship right edge whose top is level with the ship bottom hits it |
| `Subchief` `45:39` `+ → -` | a subchief whose top is five units above the ship top misses it; a subchief whose top is one unit above the ship top misses it |
| `Subchief` `45:44` `<= → <` | a subchief whose bottom is level with the ship bottom hits it |
| `Subchief` `46:22` `>= → >` | a subchief whose right side touches the ship left edge hits it |
| `Subchief` `47:32` `<= → <` | a subchief left of the ship whose top is level with the ship bottom hits it |
| `Subchief` `93:19` `< → <=`, `94:24` `> → >=` | a subchief level with its destination height keeps that height while moving sideways |
| `Subchief` `95:27` `&& → \|\|` | a subchief that reaches its destination column keeps heading to the same destination |
| `Weapons` `33:59` `> → >=` | second level weapons hold the blaster until the first laser attempt |
| `Weapons` `94:37` `&& → \|\|`, `95:58` `&& → \|\|` | a laser far above the subchief misses it; a laser one unit below the subchief misses it |
| `Weapons` `94:47` `<= → <`, `94:58` `+ → -` | a laser whose top is level with the subchief bottom hits it |
| `Weapons` `94:64` `\|\| → &&` | a laser whose top is level with the subchief bottom hits it; a laser whose bottom touches the subchief top hits it |
| `Weapons` `95:26` `+ → -`, `95:47` `>= → >`, `95:100` `+ → -` | a laser whose bottom touches the subchief top hits it |
| `Weapons` `95:68` `+ → -` | a laser one unit below the subchief misses it |
| `Weapons` `107:21` `>= → >` | a blaster hits a subchief level with its rear |
| `Weapons` `107:45` `<= → <` | a blaster hits a subchief level with its front |
| `Weapons` `108:47` `<= → <` | a blaster hits a subchief whose top is level with the blaster bottom |
| `Weapons` `109:23` `+ → -`, `109:70` `+ → -` | a blaster hits a subchief whose bottom touches the blaster top; a blaster hits a subchief whose bottom is level with the blaster bottom |
| `Weapons` `109:28` `>= → >` | a blaster hits a subchief whose bottom touches the blaster top |
| `Weapons` `109:57` `<= → <` | a blaster hits a subchief whose bottom is level with the blaster bottom |
| `Weapons` `149:51` `\|\| → &&` | an idle blaster resting on the boss does not hurt it |
| `Weapons` `151:35` `&& → \|\|`, `152:40` `&& → \|\|` | a blaster far above the boss misses it; a blaster one unit below the boss misses it |
| `Weapons` `151:48` `<= → <`, `151:58` `+ → -` | a blaster whose top is level with the boss bottom hits it |
| `Weapons` `151:64` `\|\| → &&` | a blaster whose top is level with the boss bottom hits it; a blaster whose bottom touches the boss top hits it |
| `Weapons` `152:25` `+ → -`, `152:30` `>= → >`, `152:68` `+ → -` | a blaster whose bottom touches the boss top hits it |
| `Weapons` `152:53` `+ → -` | a blaster one unit below the boss misses it |
| `Weapons` `174:36` `false → true`, `180:37` `false → true` | weapons without charges fire no special and keep zero charges |

Dois testes não matam nenhum sobrevivente do M0: "a blaster misses a subchief
whose top is four units above the blaster top" e "... one unit above ...". Eles
existem pelo critério A7: fixam o buraco preservado do blaster (abaixo).

### Buracos preservados

| Regra | Buraco | Testes que o fixam |
| --- | --- | --- |
| `Subchief.touchesShip` (corpo do subchefe, 26 de altura, contra a nave, 20) | com `ship.y - 5 <= y <= ship.y - 1` e o subchefe na largura da nave, nenhuma borda dele cai na altura da nave e não há contato | a subchief whose top is five units above the ship top misses it; a subchief whose top is one unit above the ship top misses it |
| `Weapons.hitSubchiefBlaster`, agora `Blaster.hitsSubchief` (subchefe 26 na faixa do blaster, 21) | com `blaster.y - 4 <= chief.y <= blaster.y - 1`, nenhuma borda do subchefe cai na faixa e não há acerto | a blaster misses a subchief whose top is four units above the blaster top; a blaster misses a subchief whose top is one unit above the blaster top |

Corrigi-los muda o jogo e é decisão do usuário, fora deste lote.

### Equivalentes eliminados por refatoração

Os 22 sem falha tinham uma refatoração que preserva o comportamento e tira o
operador. Nenhum foi suprimido nem anotado, e nenhum teste mudou de expectativa.
Cada refatoração entrou sozinha, com a suíte verde na JVM e no JS antes da
próxima. As regras reescritas foram comparadas com as originais ponto a ponto numa
grade de coordenadas (Python, mesma fórmula): 0 diferenças em
`Subchief.touchesShip`, `Boss.absorbMeteors`, `Boss.touchesShip`, laser contra
subchefe e chefe, e blaster contra subchefe e chefe.

| Sobrevivente (M0) | Por que não falhava | Refatoração |
| --- | --- | --- |
| `Subchief 51:53`, `57:20`; `Weapons 90:59`, `102:16`, `106:100`, `114:16`, `122:32` | o `Bool` de `Subchief.damage` e de `Weapons.hitSubchief*` ninguém lia (achado 2); o `fatal` de `hitSubchiefSpecial` também era redundante, porque depois do dano fatal o subchefe está em `Explosion` e `damage` retorna antes de mexer em nada | os quatro passam a não devolver valor, como `Boss.damage` e `Weapons.hitBoss*`; cada raio em contato chama `chief.damage(1)` |
| `Subchief 46:42` `x + 28 <= ship.x + 50` → `<` | com o topo na altura da nave e `x` até `ship.x + 22`, o primeiro ramo já dá contato | `bodyTouches()`: topo na altura da nave com as larguras sobrepostas (`bandsOverlap(x, 28, ship.x, 50)`), ou base na altura da nave com `x` na largura dela (o buraco continua) |
| `Boss 50:28`, `51:89` (meteoro); `58:22`, `59:77` (nave); `Weapons 94:26`, `95:89` (laser no subchefe), `136:26`, `137:88` (laser no chefe), `151:25`, `152:58` (blaster no chefe) | "alguma borda dentro da faixa" dá o mesmo que a sobreposição das faixas quando a união das bordas é contínua (achado 1) | uma regra só, `bandsOverlap(start, length, otherStart, otherLength)` em `Overlap.kf`, usada pelo `Boss`, por `Shot.strikes()`, `Blaster.hitsBoss()` e `Subchief.bodyTouches()` |
| `Boss 89:39` `&& → \|\|`, `89:54` `> → >=` | com `frenzySteps == 0` a conta dá 0 (achado 3), e o `GameView` só desenha o quadro com o chefe vulnerável | a guarda `&& frenzySteps > 0` saiu |
| `Weapons 106:85` `blaster.lives <= 0` → `<` | um blaster ativo com 0 vidas daria dano 0, sem efeito no subchefe | `Blaster.armed()` (`active && lives > 0`), a mesma regra do `hitsMeteor`, cujos testes a matam |
| `Weapons 149:68` `blaster.lives <= 0` → `<` (chefe) | um blaster ativo com 0 vidas daria dano 0; só apareceria pelo `evolveWeapons()` depois de um dano do corpo da nave, que não evolui as armas. Não é equivalente estrito, mas é a mesma regra repetida | também `Blaster.armed()` |

Outras mudanças do R4 que mexem em regra: `Shot.impactAt(left, top)` ao lado de
`impactAt(Meteor)` (chamada com `this.`, porque a sobrecarga sem `this.` deu
`SEM015`); `Blaster.spend()` devolve as vidas e zera; `stepToward(position,
destination)` é `math.clamp(destination, position - 1, position + 1)` (probe em
JVM e JS).

### R4 (lint)

| Arquivo | Antes | Refatoração | Depois |
| --- | --- | --- | --- |
| `Subchief` | 5 achados | `bodyTouches()`; guardas `return` em `advanceExplosion` e `advanceNormal`; `fireShot()`; `stepToward()` | 0 |
| `Boss` | 2 em `advance` | `moveTowardDestination()` e `advanceAttack()`; `bandsOverlap()` | 0 |
| `Weapons` | 7, com `long-file` (174 de 150) | regras de alvo em `Shot.strikes()`, `Blaster.hitsSubchief()`, `Blaster.hitsBoss()`; `laserStrikes()`, `blasterDue()`, `fireLaser()`, `laserHitsMeteor()`, `beamHitsMeteor()` | 0, 140 linhas não vazias |
| `Shot`, `Blaster`, `Course`, `Overlap` | 0 | regras recebidas do `Weapons`, arquivos novos | 0 |

A ordem de prioridade dos acertos não mudou: o laço de fora continua sendo o dos
projéteis, e o de dentro o dos meteoros.

### Sobreviventes por arquivo

| Arquivo | M0 | Depois | Mortos por teste novo | Eliminados por refatoração |
| --- | --- | --- | --- | --- |
| `Subchief` | 18 (71 candidatos) | 0 (36/36) | 15 | 3 |
| `Boss` | 30 (101) | 0 (64/64) | 24 | 6 |
| `Weapons` | 42 (139) | 0 (61/61) | 29 | 13 |
| `Shot` (recebeu regra) | 0 no lote 2 | 0 (46/46) | | |
| `Blaster` (recebeu regra) | 0 no lote 2 | 0 (51/51) | | |
| `Course` (novo) | | 0 (2/2) | | |
| `Overlap` (novo) | | 0 (5/5) | | |
| **Total** | **90 (311)** | **0 (265/265)** | **68** | **22** |

### Critérios de aceite

| # | Comando | Observado | Evidência |
| --- | --- | --- | --- |
| A1 | `kof-mut run --files a1-scope.json --report-dir .agent/tmp/debt-batch3/a1`, com os 5 arquivos de `git diff --name-only main -- src/main` e os 2 novos | `complete`, 0 limitações, 265 candidatos, 265 mortos, 0 sobreviventes, 0 timeout, exit 0, 1502 s (13:10 a 13:35) | `a1-report.json`, `a1.log` |
| A2 | `tools/redcheck.py` com cada sobrevivente do M0 | 68 mutantes, cada um derrubando só testes novos, sempre por asserção; nenhum teste antigo falhou | `red.txt`; tabela acima |
| A3 | leitura do código, RED e KofMut final | 22 sem falha, todos eliminados por refatoração; nenhum anotado | seção de equivalentes |
| A4 | `npm run lint:sensor --` nos 7 arquivos de produção, nos 4 testes novos, no `JourneyScenarios.kf` e no `SpecialBeamJourney.kf` | `PASS (0 findings)` | rodado no repositório |
| A5 | `npm run dup:sensor` (diff contra a `main`) | `PASS (0 findings)`, `7 files expected, 7 tokenized`; o grupo `Boss.kf` ↔ `Subchief.kf` do R0 sumiu | rodado no repositório |
| A6 | `git diff --name-only main -- src/main` | só `Blaster.kf`, `Boss.kf`, `Shot.kf`, `Subchief.kf` e `Weapons.kf`, mais os novos `Course.kf` e `Overlap.kf`; `Game.kf`, `BossWeapons.kf` e a UI não aparecem | rodado no repositório |
| A7 | testes nomeados na seção "Buracos preservados" | os quatro passam; os buracos continuam | suíte |
| A8 | `node scripts/kof-tests.mjs --target jvm` e `--target js`, com 0.7.0 e com `KOF=…/kof-0.6.4…/bin/kof` | `0 failed of 310 tests` nos quatro (eram 267) | rodado no repositório |
| A9 | `debt-tools/journeys.sh` e `debt-tools/pixels.py` contra `debt-r0/journeys-1/png` | 7/7 exit 0, 186 PNG; `common=186 only_a=0 only_b=0 pixel_diff=0` | `journeys/summary.txt`, `pixels.out` |
| A10 | validação final do plano | ver "Fechamento do lote" | `final/` |

### Fechamento do lote

Validação final do plano, nesta ordem, de 13:35 a 14:31 (evidência em
`.agent/tmp/debt-batch3/final/`):

| Comando | Resultado |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | exit 0, 15 testes OK |
| `npm run test:sensors` | exit 0, 39 pass, 0 fail |
| `npm run check` | `CHECK: PASS`, 11 passos PASS; `mutation` PASS (não SKIP): 265 candidatos, 265 mortos, 0 sobreviventes nos 7 arquivos; cerca de 24 min |
| `npm run check:task` | `CHECK:TASK: PASS`, `mutation` (265/265) e as sete jornadas PASS; cerca de 31 min |
| `git diff --check` | exit 0 |

Esta seção entrou depois da validação (só texto); `npm run docs:sensor` e
`git diff --check` rodaram de novo sobre ela.

### Tempo

M0 de 12:23 a 12:59 (36 min). Análise dos sobreviventes, probe da divisão, testes,
RED automatizado e R4 numa cópia do projeto, em paralelo ao M0. Pré-checagem do
KofMut na cópia (265/265, cerca de 24 min) junto com as jornadas; A1 no
repositório de 13:10 a 13:35; validação final de 13:35 a 14:31. Do começo ao A1,
cerca de 1h15, contra a estimativa de 1h30.

Estimativa para o lote 4 (`Game`, 42 sobreviventes no A1): o R4 domina, porque o
`step()` é grande e o `Game` não pode mudar de API para o `GameView` e o
`GameControls`. Cerca de 2h a 3h mais o fechamento (cerca de 1h, com `check` e
`check:task` no fim).
