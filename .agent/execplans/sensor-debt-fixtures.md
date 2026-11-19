# R6: dívida dos sensores nas fixtures de navegador

## Purpose and success

As cinco fixtures Kof de navegador (`tests/boss.kf`, `tests/stage.kf`,
`tests/subchief.kf`, `tests/weapons.kf` e `tests/meteor-motion.kf`) são os
programas que as jornadas Playwright (`tests/browser*.py`) abrem no Chrome para
colocar o jogo num cenário e ler o estado. Hoje elas concentram os únicos 14
achados de lint do repositório. Este plano é o R6 do plano mestre "Pagamento da
dívida dos sensores antes do M3": dividir cada fixture por intenção, sem mudar o
que a jornada vê.

Sucesso, observável:

- `npm run sensors:debt` imprime `SENSOR lint: PASS (0 findings)` e
  `SENSOR dup: PASS (0 findings)` sobre todos os arquivos Kof do repositório;
- as sete jornadas passam e cada captura PNG tem os mesmos pixels decodificados
  que a linha de base tirada da `main` antes de qualquer edição;
- só os cinco arquivos acima mudam no código; produção, suítes Kof,
  `tests/controls.kf` e `tests/*.py` ficam intactos.

## Definitions

- **Fixture**: um `tests/*.kf` com `main()` que monta `Game`, `GameView`,
  `GameControls`, um rótulo de estado e botões de cenário. A jornada clica nos
  botões pelo nome exato e lê o rótulo por `id`.
- **Rótulo de estado**: o `Label` com `setId("boss-status")`,
  `"stage-status"`, `"subchief-status"` ou `"test-status"`, cujo texto é uma
  sequência `chave:valor`. As jornadas o leem com a regex `(\w+):(-?\d+)`
  (por exemplo `tests/browser_boss.py:17`).
- **Linha de base de pixels (B0)**: as capturas PNG das sete jornadas rodadas na
  `main` antes da primeira edição, guardadas à parte para comparar no fim.

## Context and limits

Linha de base medida no planejamento, em 19/11/2026, na `main` `91d8e49`, com
`bash -lic 'npm run sensors:debt'` (o Maven vem do SDKMAN e só existe em shell
de login):

| Arquivo | Linha | Unidade | Regra | Medido | Limite |
| --- | --- | --- | --- | --- | --- |
| `tests/boss.kf` | 25 | `refresh` | `high-complexity` | 17 | 10 |
| `tests/boss.kf` | 25 | `refresh` | `too-many-statements` | 38 | 17 |
| `tests/boss.kf` | 51 | `main` | `long-function` | 143 | 25 |
| `tests/boss.kf` | 51 | `main` | `too-many-statements` | 32 | 17 |
| `tests/meteor-motion.kf` | 4 | `main` | `long-function` | 29 | 25 |
| `tests/stage.kf` | 6 | `main` | `long-function` | 158 | 25 |
| `tests/stage.kf` | 6 | `main` | `too-many-statements` | 42 | 17 |
| `tests/stage.kf` | 71 | lambda de "Defeat effects" | `too-many-statements` | 18 | 17 |
| `tests/subchief.kf` | 20 | `prepareBoundary` | `too-many-statements` | 19 | 17 |
| `tests/subchief.kf` | 38 | `main` | `long-function` | 147 | 25 |
| `tests/subchief.kf` | 38 | `main` | `too-many-statements` | 39 | 17 |
| `tests/subchief.kf` | 186 | `refresh` | `too-many-statements` | 25 | 17 |
| `tests/weapons.kf` | 6 | `main` | `long-function` | 75 | 25 |
| `tests/weapons.kf` | 6 | `main` | `too-many-statements` | 36 | 17 |

`SENSOR dup: PASS (0 findings)`: o CPD não analisa código de teste (decisão 6 de
07/11 no `EXECPLAN.md`). `tests/controls.kf` não tem achado e não muda.

Como o lint conta (fonte: `.agent/validation/sensor-calibration.md`, tabela de
métricas, e o relatório do próprio sensor):

- `long-function` (25 linhas): conta da declaração ao fim do corpo **incluindo as
  linhas dos corpos locais**. Uma lambda de várias linhas dentro do `main` soma
  todas as suas linhas ao `main`.
- `too-many-statements` (17) e `high-complexity` (10): os corpos locais **não**
  contribuem ao pai; cada lambda tem conta própria (por isso a lambda de
  `tests/stage.kf:71` aparece sozinha).
- Parâmetros: até 4. Profundidade: até 3.
- Em `tests/`, `long-file` vale 1000 linhas não vazias (`TestRules`/`Findings`,
  `TEST_CODE_FILE_LINES = 1000`).

Consequência prática: um botão só cabe no `main` ou numa função de montagem se a
lambda for de uma linha, chamando uma função `prepare…` com nome de intenção e o
`refresh`.

Quem usa cada fixture:

| Fixture | Jornada | Rótulo |
| --- | --- | --- |
| `tests/boss.kf` | `tests/browser_boss.py` | `#boss-status` |
| `tests/stage.kf` | `tests/browser_stage.py` | `#stage-status` |
| `tests/subchief.kf` | `tests/browser_subchief.py` | `#subchief-status` |
| `tests/weapons.kf` | `tests/browser_weapons.py` e `tests/browser.py` (cena de resultado) | `#test-status` |
| `tests/meteor-motion.kf` | `tests/browser_meteor.py` | rótulo sem `id`, texto `impact:…`/`respawn:…` |

O passo `types:fixtures` do `npm run check` compila cada `tests/*.kf` no alvo JS
(`scripts/check.mjs:39-53`). O `npm run check:task` roda as sete jornadas
(`scripts/check-task.mjs:8-13`).

### Limites

- Não mudar nada em `src/`, `tests/*.py`, `tests/controls.kf`, `scripts/` nem
  `kof-mut.json`.
- Não mudar limite de lint, nem suprimir achado.
- Contrato de cada fixture que precisa ficar igual, byte a byte quando for texto:
  título e tamanho da janela; ordem e texto de cada botão; `id` e texto de cada
  rótulo (mesmas chaves, na mesma ordem, com os mesmos valores); semente de cada
  `game.start(…)`; ordem das atribuições que dependem uma da outra (por exemplo,
  em "Shots" do chefe, `weapons.level = 1`, `evolve()`, `level = 1` de novo);
  intervalo do relógio (`Rules.STEP_MS`, ou `30` no `meteor-motion`) e o que ele
  faz a cada passo; e o estado inicial antes do primeiro clique.
- Evidência bruta em `.agent/tmp/debt-fixtures/`. `.agent/tmp/` **não** está no
  `.gitignore`, e as jornadas também gravam PNG em `.agent/tmp/*-browser/`. Ver
  "Decisions".

## Decisions

**Dividir por intenção com funções `prepare…` e lambdas de uma linha.** Cada
cenário vira uma função de topo com nome do que ele arma (por exemplo
`prepareFury(game)`, `prepareDefeatEffects(game)`, `prepareShipHit(game)`); o
botão chama `prepare…` e depois o `refresh` numa lambda de uma linha. A montagem
dos botões sai do `main` para funções que devolvem as listas, em grupos que caibam
em 25 linhas. Cenários iguais que só mudam um número viram uma função com
parâmetro (os seis "Result N" de `stage.kf` com `prepareResult(game, score)`; o
`prepareBoundary` do subchefe dividido por arma, um `prepare…` por arma).
Contagens repetidas do `refresh` (tiros ativos, fase como número) viram funções
pequenas com nome. Alternativa descartada: uma classe de cenário por fixture,
mais código e sem ganho de leitura numa fixture de teste. Fonte: plano mestre,
R6 ("com as funções `prepare…` divididas por intenção") e R2 ("preparação longa
vira funções `given…`").

**Evidência fora do commit sem mexer no `.gitignore`.** No começo da execução,
acrescentar `.agent/tmp/` a `.git/info/exclude` (local, não versionado). Assim as
PNGs das jornadas e a evidência deste lote não entram no `lc`. Alternativa
descartada: acrescentar ao `.gitignore`, que muda um arquivo fora do escopo.

**Prova de pixels parcial (decidido na execução, 19/11).** A B0 não repetiu
os pixels: com Chrome 158 e a `main` intacta, 19 das 186 capturas mudam entre
rodadas, e rodadas extras do `browser_weapons.py` na `main` mostraram outras
oscilando (`keyboard-game-action-320`, `keyboard-game-continue-320`,
`special-key-release/released-320`). Todas são `page.screenshot` de página
inteira com relógio congelado; a diferença ampliada é antialiasing nas setas e
nos cantos do `GameControls`, que não muda. No lote da UI (16/11) as 186 eram
estáveis, então a mudança é de ambiente. Escolha: comparação estrita nas
capturas que a `main` repete, e as instáveis registradas como lacuna da A3,
cobertas pelas asserções das jornadas (A4) e pelo diff de contrato (A5). As
capturas `application-*`, `credits-text-browser/*` e `app-*` vêm da aplicação
(`served_build()` sem fixture) e não podem mudar com este lote. Alternativa
descartada: desistir da A3 inteira, como previa o risco "Linha de base de
pixels perdida", o que jogaria fora a prova estrita das 167 estáveis.

**Links quebrados nas cópias arquivadas (decidido pelo usuário, 19/11).** O
`docs:sensor` do `npm run check` falhava com 11 `broken-link` em
`.agent/sensor-plans/`, vindos do PR #32 e anteriores a este lote. O usuário
escolheu corrigir neste branch, contra o limite "Não editar as cópias
arquivadas". Só os alvos dos links mudaram: o `EXECPLAN.md` do KofMut aponta
para a versão arquivada no GitHub (`6764595`); o registro do piloto Katacombs,
que não existe mais, virou texto com o caminho original; os links relativos ao
repositório ganharam `../../` ou `../`. O `README.md` da pasta registra a
mudança. Alternativas descartadas: PR separado na `main` e aceitar a falha.

## Risks

- **Mudar o que a jornada vê sem ela acusar.** As jornadas conferem algumas
  chaves, não todo o estado. Uma `prepare…` que esquece uma atribuição (por
  exemplo `game.ship.y = 200` do `prepareBoss`) pode continuar verde e mudar a
  imagem. Controle: comparação de pixels contra a B0 em todas as capturas.
- **Linha de base de pixels perdida.** As ferramentas e as PNGs do R0
  (`.agent/tmp/debt-tools/`, `debt-r0/journeys-1/png`) não existem mais nesta
  máquina. Controle: o M0 gera uma B0 nova na `main` e prova que duas execuções
  seguidas dão os mesmos pixels. Se não der, registrar a lacuna e cair só nas
  asserções das jornadas, sem apresentar A3 como atendido.
- **Ordem de avaliação.** Juntar atribuições numa função pode trocar a ordem de
  efeitos com dependência (`fire`, `evolve`, `impactAt`, `hit`, `step`).
  Controle: mover os blocos inteiros, na mesma ordem.
- **Ambiente.** `mvn` só existe em shell de login: rodar sensores com
  `bash -lic '…'`. O `kof` do `PATH` precisa ser o 0.7.0
  (`readlink -f ~/.local/bin/kof` termina em `kof-0.7.0-linux-x86_64/bin/kof`).
  O 0.8.0 está baixado e não foi testado. Se a versão for outra, parar e
  perguntar.

## Milestones

### M0. Linha de base

Produz a B0 e confirma o ponto de partida.

1. `printf '.agent/tmp/\n' >> .git/info/exclude` se a linha ainda não estiver
   lá; `git status --porcelain --untracked-files=all` deve listar só este plano.
2. `bash -lic 'npm run sensors:debt' > .agent/tmp/debt-fixtures/m0-debt.txt` e
   conferir os 14 achados da tabela acima.
3. Criar `.agent/tmp/debt-fixtures/tools/journeys.sh`, que roda as sete
   `python3 tests/browser*.py` (uma por vez, registrando o exit de cada uma em
   `summary.txt`) e depois copia todo `*.png` de `.agent/tmp/` (fora de
   `debt-fixtures/`) para `<destino>/png/`, preservando o caminho relativo. Criar
   `.agent/tmp/debt-fixtures/tools/pixels.py`, que compara duas pastas `png/`
   pelos pixels RGB decodificados (Pillow) e imprime
   `common=N only_a=N only_b=N pixel_diff=N` e o nome de cada diferença.
4. Rodar `journeys.sh` duas vezes na `main` sem edição: `b0-1` e `b0-2`.
   `pixels.py b0-1/png b0-2/png` deve dar `only_a=0 only_b=0 pixel_diff=0`.

Aceite: 7/7 exit 0 nas duas rodadas, determinismo provado, contagem de PNG
registrada (o lote da UI registrou 186).

### M1. `weapons.kf` e `meteor-motion.kf`

Os dois menores, para firmar o padrão.

- `weapons.kf`: cada lambda de várias linhas vira `prepare…`/função de ação
  (`collectEvolution`, `collectLife`, `showBlaster`, `impactBlaster`, `hitShip`,
  etc., nomes livres desde que digam a intenção); a montagem dos botões sai do
  `main`; o texto de `#test-status` continua idêntico, de preferência numa função
  `statusText(game)`. `impactBeam` fica como está.
- `meteor-motion.kf`: o texto do rótulo e o desenho do impacto saem para funções
  (`motionText(meteor)`, `drawImpact(...)`), e o `main` cai para 25 linhas ou
  menos.

Validação do milestone:

    bash -lic 'npm run lint:sensor -- tests/weapons.kf tests/meteor-motion.kf'
    python3 scripts/kof_project.py check --target js --json --fixture tests/weapons.kf
    python3 scripts/kof_project.py check --target js --json --fixture tests/meteor-motion.kf
    python3 tests/browser_weapons.py
    python3 tests/browser_meteor.py
    python3 tests/browser.py

Esperado: lint `PASS (0 findings)`; os dois `check` com `"success": true`; as três
jornadas com exit 0.

### M2. `stage.kf`

- O `main` só cria jogo, tela, rótulo, janela e relógio; os botões vêm de funções
  de montagem em grupos de até 25 linhas.
- `prepareFinish`, `prepareRightFinish`, `prepareDefeatFlight`,
  `prepareDefeatEffects` (a lambda de 18 statements; dividir pelo que ela arma:
  meteoro com laser, blaster, feixe), `prepareVerticalImpact`, `prepareFullJourney`,
  `prepareResult(game, score)` para os seis "Result N" e o "Zero result" se
  couber (o "Zero result" também zera `ship.lives` e tem `score = 0`, a mesma
  forma).
- O estado inicial do `main` (`start(907)`, `score = 1500`, nave, armas,
  meteoros e itens fora da tela) vai para `prepareOpening(game)`.
- `refresh`, `prepareDefeat`, `bossActive` e `subchiefActive` já estão dentro dos
  limites; só mudam se ajudar.

Validação: lint e `check --fixture` de `tests/stage.kf` como no M1;
`python3 tests/browser_stage.py` com exit 0.

### M3. `subchief.kf`

- `prepareBoundary` dividido por arma (`prepareBoundaryBody`,
  `…Laser`, `…Blaster`, `…Special`, cada um chamando uma parte comum com
  `lifetime`), mantendo os oito botões "Boundary N arma" com os mesmos nomes.
- `refresh` dividido: os sinalizadores 0/1 e as contagens em funções pequenas; o
  texto final continua idêntico, com as mesmas chaves e na mesma ordem.
- O avanço inicial (`start(920)`, `lives = 100`, 829 passos) vira
  `prepareApproach(game)`.
- Botões fora do `main`, como no M2.

Validação: lint e `check --fixture` de `tests/subchief.kf`;
`python3 tests/browser_subchief.py` com exit 0.

### M4. `boss.kf`

- `refresh` com complexidade 17 e 38 statements: a fase como número em
  `phaseCode(phase)`, as contagens de tiros do chefe e do jogador em funções, os
  sinalizadores em funções; texto final idêntico.
- Cada cenário com corpo próprio vira `prepare…` (`prepareFury`, `prepareFrenzy`,
  `prepareShots`, `prepareBossSpecial`, `prepareFatalLaser`, …), mantendo
  `prepareBoss` e `prepareLaser`.
- O estado inicial do `main` (`prepareBoss`, chefe inativo, `stageSteps = 1409`)
  vira `prepareApproach(game)` ou nome equivalente.

Validação: lint e `check --fixture` de `tests/boss.kf`;
`python3 tests/browser_boss.py` com exit 0.

### M5. Comparação final e registros

1. `bash -lic 'npm run sensors:debt'`: ler a saída (o exit é 0 mesmo com achado).
2. `journeys.sh` na árvore final (`final-journeys`) e `pixels.py b0-1/png
   final-journeys/png`.
3. `git diff --name-only main` e `git status --porcelain --untracked-files=all`.
4. Registros: nova seção "R6, fixtures" em
   `.agent/validation/sensor-debt-payoff.md` (tabela de achados antes e depois,
   lista "de → para" das lambdas e funções divididas por fixture, aceite A1 a A7
   com o observado); marcar `- [x] R6` no `EXECPLAN.md` (seção "Pagamento da
   dívida dos sensores antes do M3"), com uma linha de resumo e link para este
   plano; atualizar o `Progress` deste plano. Não editar as cópias arquivadas em
   `.agent/sensor-plans/`.
5. Validação final (seção Validation).

## Progress

- [x] M0. Linha de base e B0 (19/11). 14 achados confirmados. Ambiente
  completado no caminho: Chrome 158.0.8127.36 e Playwright 1.65.2 instalados
  pelo usuário; clone de `renanfranca/sifuture` em `~/projects/sifuture`
  (`50fc40d`, o SHA já registrado), exigido pelo `browser_boss.py:220`. B0 com
  7/7 e 186 PNGs nas duas rodadas, mas **não determinística**: 19 capturas
  diferem entre elas (ver Decisions, "Prova de pixels parcial").
- [x] M1. `weapons.kf` e `meteor-motion.kf`: lint PASS, `check` true, 3/3
  jornadas.
- [x] M2. `stage.kf`: lint PASS, `check` true, jornada exit 0.
- [x] M3. `subchief.kf`: lint PASS, `check` true, jornada exit 0.
- [x] M4. `boss.kf`: lint PASS, `check` true, jornada exit 0.
- [x] M5. Comparação final, registros e validação final. A1, A2, A3
  (parcial: 114/114 capturas estáveis de fixture iguais, 4 instáveis na própria
  `main`), A5 (`contract.diff` vazio) e A6 atendidos; aceite em
  `.agent/validation/sensor-debt-payoff.md` e `- [x] R6` no `EXECPLAN.md`. A
  primeira validação final (11:16) parou por falta do Gitleaks; o usuário pediu
  a instalação (8.30.1 em `~/.local/bin`, checksum conferido) e escolheu
  corrigir os 11 links quebrados de `.agent/sensor-plans/` neste branch (ver
  Decisions). `npm run test:sensors` só passa em shell de login (`mvn`).
  Validação final completa às 19:20–19:25, depois de dois congelamentos da
  máquina: todos exit 0, `CHECK: PASS` e `CHECK:TASK: PASS` com as sete
  jornadas; detalhes na seção "Fechamento do R6" do aceite.

## Validation

Critérios de aceite. A coluna "Verificação" é o planejado; o observado vai para o
aceite em `.agent/validation/sensor-debt-payoff.md`.

| # | Fonte | Contexto → ação → resultado esperado | Verificação | Evidência esperada |
| --- | --- | --- | --- | --- |
| A1 | plano mestre, R6 e A3 | com as cinco fixtures refeitas → `sensors:debt` → `SENSOR lint: PASS (0 findings)`, `SENSOR dup: PASS (0 findings)` e `N Kof files` igual a `git ls-files '*.kf' \| wc -l` | **ler a saída**; o exit 0 não prova nada (`scripts/sensors-debt.mjs` sai 0 com achados) | `final-debt.txt` |
| A2 | `EXECPLAN.md`, decisão 6 de 07/11 | cada fixture → `lint:sensor` só nela → `PASS (0 findings)`, sem limite alterado (`git diff main -- scripts/` vazio) | comandos dos milestones | saída por milestone |
| A3 | plano mestre, A5 | sete jornadas na árvore final → mesmas PNGs da B0 → `common=` igual ao total da B0, `only_a=0 only_b=0 pixel_diff=0` | `journeys.sh` + `pixels.py` contra `b0-1` | `final-journeys/summary.txt`, `pixels.out` |
| A4 | jornadas atuais | cada jornada clica pelos mesmos nomes e lê as mesmas chaves → 7/7 exit 0. Distingue: um botão renomeado faz `get_by_role(..., exact=True)` falhar; uma chave faltando quebra o `state(page)[...]` | `npm run check:task` | sumário com as sete `browser:*` PASS |
| A5 | contrato das fixtures (Limites) | `git diff main -- tests/*.kf` → cada texto de `Button("…")`, `Window("…")`, `window.size`, `setId`, `game.start(…)` e cada chave do rótulo de estado aparece igual e na mesma ordem antes e depois | extrair essas linhas por `grep -o` na `main` e na branch e comparar com `diff`; o `diff` vazio é o resultado esperado | `contract.diff` vazio |
| A6 | Limites | só os cinco `tests/*.kf`, o `EXECPLAN.md`, `.agent/validation/sensor-debt-payoff.md` e este plano mudam | `git diff --name-only main` e `git status --porcelain --untracked-files=all` | lista no aceite |
| A7 | `scripts/check.mjs` | `npm run check` → `types:fixtures` PASS (cada fixture compila no JS), `lint:sensor` PASS, `CHECK: PASS`; `mutation` em SKIP é esperado, porque nenhum arquivo de produção muda | validação final | saída do `check` |

A5 complementa a A3: a comparação de pixels não vê a ordem dos botões fora do
canvas nem chaves do rótulo que nenhuma jornada lê.

Validação final, nesta ordem. O commit só acontece se todos passarem:

    python3 -m unittest discover -s tests -p 'test_*.py'
    npm run test:sensors
    bash -lic 'npm run sensors:debt'
    bash -lic 'npm run check'
    bash -lic 'npm run check:task'
    git diff --check

Esperado:

- todos com exit 0;
- `sensors:debt` com lint e dup em `PASS (0 findings)` (ler a saída);
- `npm run check` com `CHECK: PASS`;
- `npm run check:task` com `CHECK:TASK: PASS` e as sete jornadas em PASS;
- `git status --porcelain --untracked-files=all` sem nada de `.agent/tmp/`.

Obrigações do executor antes de entregar:

- Conferir de novo cada expectativa contra a fonte citada (a fixture na `main`
  `91d8e49` e a jornada que a usa), separado de conferir se os comandos a
  demonstram.
- Para cada critério de A1 a A7, registrar no aceite o comando, o resultado
  observado e onde está a evidência. Suíte verde sozinha não prova cada critério.
- Registrar antes da entrega qualquer critério não verificado, lacuna (por
  exemplo, B0 não determinística) ou falha, sem apresentá-los como atendidos.
