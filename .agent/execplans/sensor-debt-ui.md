# Dívida dos sensores, lote da UI: `GameControls` e `GameView`

## Purpose and success

O `npm run check` muta todo arquivo de produção alterado contra a `main`, e um
mutante sobrevivente reprova. `GameControls.kf` e `GameView.kf` são os últimos
arquivos de produção com dívida: juntos têm 193 sobreviventes, nenhum morto, e 21
achados de lint. Enquanto isso durar, qualquer mudança na tela ou nos controles
trava o `check`.

Hoje nenhum mutante deles morre porque o KofMut roda os testes na JVM, e na JVM o
`kof.ui` não faz nada: desenho, estilo e texto de botão são stubs vazios
(`/home/renanfranca/projects/kof/docs/bugs-and-gaps/KOFUI-AUDIT.md`: "JVM stub
(source): `jvm/JvmRuntimeUi.java` (no-op; Bool=int 0/1; String getter →
`return ""`)" e "JVM no-op (UI008) is a documented design decision"). Um teste não
vê que imagem foi desenhada, onde, nem que estilo um botão recebeu.

A solução decidida pelo usuário em 13/11 é o padrão *Humble Object*: toda decisão
sai para classes Kof puras, testáveis na JVM, e os dois arquivos ficam só
executando o que elas decidem. Nenhuma regra ou medidor muda.

Sucesso:
- o KofMut em todo arquivo de produção alterado sai com 0 sobreviventes;
- `npm run lint:sensor` nesses arquivos dá 0 achados;
- o `npm run check` passa, com o passo `mutation` rodando de verdade (sem SKIP);
- o jogo se comporta e aparece igual: as sete jornadas de navegador passam e as
  capturas não mudam nenhum pixel.

## Definitions

- **Casca (Humble Object):** a parte que só fala com o `kof.ui`. Ela não decide
  nada: recebe uma decisão já tomada e chama `drawImage`, `setStyle`,
  `setDisabled` ou atribui `text`. Exemplo: `canvas.drawImage(imageOf(s), s.x, s.y)`
  para cada item de uma lista pronta.
- **Cena:** a lista do que desenhar num quadro, montada por código Kof puro a
  partir do `Game`. Cada item diz o tipo de imagem, o quadro, `x` e `y`, ou um
  texto com posição e cor. Exemplo: o impacto do laser vira um item
  `LaserImpact` em `(s.x + 5, s.y)`; um teste confere esses números.

## Context and limits

Plano mestre: `/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md`.
Leia as "Regras invioláveis" dele antes de começar. Elas valem aqui:
- o jogo não muda de comportamento nem de aparência;
- a contagem de casos só sobe;
- nenhum limite, regra ou medidor muda;
- não há supressão;
- na produção, uma refatoração por vez, com os testes verdes.

Lotes anteriores, todos na `main` (`30b47b2`): lotes 1 a 4, PRs #28 a #31. O
método, a automação de RED (`.agent/tmp/debt-batch4/tools/redcheck.py`), a
comparação de pixels (`debt-tools/journeys.sh` e `debt-tools/pixels.py` contra
`debt-r0/journeys-1/png`) e os registros estão em
`.agent/validation/sensor-debt-payoff.md`. Leia antes a seção
"Piloto da UI: `ControlsGuide` (10/11)": ela é a receita deste lote
(`ControlsGuide` delegou o estado para `GuideDisclosure` e ganhou métodos
nomeados, como `clicked()`, chamados pelos handlers e testados em
`src/test/kof/sifuture/ControlsGuideJourney.kf`). O mesmo piloto mostrou duas
armadilhas:
- na JVM, o texto de botão sempre lê vazio. Só estado Kof comum serve de prova;
- o build JS do app só segue `import`. Classe nova sem `import` explícito no
  arquivo que a usa passa nos testes e quebra o `browser` (`SEM011`).

Linha de base, medida no planejamento em 13/11 na `main` `30b47b2`:

| Arquivo | Linhas não vazias | A1 | Lint |
| --- | --- | --- | --- |
| `GameControls.kf` | 391 (limite 150) | 118 sobreviventes, 0 mortos | 12: `long-file`; construtor (`:73`) `long-function` e `too-many-statements`; `keyboardSurface` (`:157`) `too-many-statements`; `menuOption` (`:232`) `too-many-parameters`; `keyChanged` (`:297`, complexidade 33) `long-function`, `high-complexity`, `deep-nesting` e `too-many-statements`; `update` (`:355`) `long-function`, `high-complexity` e `too-many-statements` |
| `GameView.kf` | 223 (limite 150) | 75 sobreviventes, 0 mortos | 9: `long-file`; construtor (`:41`) `long-function` e `too-many-statements`; `render` (`:77`, complexidade 43) `long-function`, `high-complexity`, `deep-nesting` e `too-many-statements`; `drawText` (`:182`) `too-many-parameters`; `drawHud` (`:190`) `too-many-statements` |

Nenhum dos dois está em grupo de CPD. Os sobreviventes vêm de
`.agent/tmp/debt-a1/kofmut-a1-report.json`.

Onde ficam as decisões hoje:
- **`GameControls`:** `keyChanged` (teclas `1`, espaço, Enter e setas; presas;
  cliques a descartar), `keyboardReceiver`, `optionAvailable`, `optionTarget`,
  `activateOption`, `activateAction`, as flags de foco e de tecla presa nos
  handlers (`:122-149`, `:186-189`, `:236-250`), `updateSpecial` (estilo e
  `setDisabled` pelo especial disponível e pelo foco), `setOptionStyle`,
  `updateSurfaceFocus` e `update` (que botão fica desabilitado, que texto o botão
  de ação mostra, que arranjo vale em cada tela).
- **`GameView`:** `render` (o que aparece em cada tela; quadro de cada sprite;
  deslocamentos como o `+ 5` do impacto do laser e o `- 14`/`- 15` do blaster; o
  pisca da nave reiniciando), `drawHud` (vidas, posição no estágio, placar,
  ícone do especial), `drawResult` (centro do placar final e a imagem do
  resultado), `numberWidth`, `drawNumber`, `drawCreditBlock` e `drawMenuLabel`.

### Limites

- **Contrato público que fica igual:** quem usa os dois arquivos é o `Main.kf` e
  as fixtures `tests/controls.kf`, `tests/boss.kf`, `tests/weapons.kf`,
  `tests/stage.kf` e `tests/subchief.kf`:
  - `GameView(Canvas)`, `creditsCanvas` e `render(Game)`;
  - `GameControls(Game, GameView, Canvas)`, `root` e `update()`.
- **O DOM fica igual:** os mesmos `id`s (`game-keyboard`, `game-action`,
  `game-special`, `game-new`, `game-controls`, `game-continue`, `game-restart`,
  `game-menu`, `game-details`, `game-help`, `controls-heading`), os mesmos textos e
  os mesmos estilos em cada estado. `tests/browser.py` e as capturas verificam
  isso. `tests/browser.py` não muda.
- **Arquivos que podem mudar:** `GameControls.kf`, `GameView.kf` e arquivos novos
  em `src/main/kof/sifuture/`. `ControlsGuide.kf` e `GuideDisclosure.kf` só mudam
  se uma regra do `GameControls` for para eles, continuando com 0 sobreviventes.
  `Main.kf`, `src/main/kof/sifuture/game/` e as fixtures `tests/*.kf` não mudam.
  Se alguma regra exigir, pare e mostre.
- **Testes novos** vão em arquivos novos por assunto, em `src/test/kof/sifuture/`.
  Observe a cena e o estado das classes puras, não os stubs do `kof.ui`.
- **Classe, enum, função ou arquivo novo:** importe explicitamente onde usar, nos
  arquivos de produção e nos testes.
- **Sobrecarga:** use `this.` ao chamar uma sobrecarga de dentro da classe
  (`SEM015` no lote 3).
- **`kof.math.min` com uma constante `static final`** direto como argumento dá
  `SEM025`. Passe a constante antes por uma variável local tipada.
- **Desempenho:** a cena é montada a cada quadro (`Rules.STEP_MS` = 30). Ela não
  pode criar listas de imagens nem objetos `Image` por quadro; só itens pequenos
  com números. Se a cena criar mais de cerca de 100 itens por quadro, registre o
  número no aceite.
- **Sem comentários** em código, testes ou fixtures (`AGENTS.md`).

## Decisions

**Cena testável em vez de exclusão (usuário, 13/11).** As decisões de desenho e de
controle saem para código Kof puro. `GameView` e `GameControls` viram casca.
Alternativas descartadas: excluir o `GameView` da mutação, que exigiria uma
exceção nova à regra "nenhum medidor muda" e deixaria as coordenadas protegidas só
pelas capturas; e o híbrido, que exigiria a mesma exceção. Consequência: posições
de HUD e quadros de sprite passam a ter teste, e mudar a posição de um item na
tela exige atualizar um teste.

**Um lote só (usuário, 13/11).** `GameControls` e `GameView` entram no mesmo plano e
no mesmo PR.

**Ordem R4 e R5 neste lote.** Nos lotes 1 a 4, o R5 vinha antes do R4: primeiro os
testes, depois a refatoração. Aqui isso não é possível, porque nenhum teste
enxerga a casca. A ordem passa a ser:
1. criar a classe pura por TDD (`tdd-behavior-autonomous-quiet`), com testes do
   comportamento que ela decide;
2. trocar a casca para usá-la, uma decisão por vez;
3. provar que nada mudou na tela com as jornadas e a comparação de pixels, no fim
   de cada milestone e não só no fim do lote.

O RED de cada teste se observa na classe pura: aplique o mutante nela, veja o
teste nomeado falhar por asserção e restaure.

**Equivalentes.** Mesma regra dos lotes anteriores. Antes de chamar um mutante de
equivalente, procure uma refatoração que preserve o comportamento e tire o
operador redundante. Só quando ela não existir, anote a prova e **pare antes do
commit**. Um mutante que sobra na casca e só seria visto pelo `kof.ui` não é
equivalente: a decisão dele precisa sair para a classe pura.

### Descobertas na execução (16/11)

- **Kof 0.7.3 no `PATH`.** O `kof` instalado passou a ser o 0.7.3 (14/11), e o
  KofMut recusa a preparação com ele (`JSN006: json.decode expected an array but
  the payload is a number`, exit 2). Todo comando do lote roda com
  `PATH=$HOME/.local/share/kof/kof-0.7.0-linux-x86_64/bin:$PATH`, o mesmo Kof
  dos lotes 1 a 4. Sem isso, o passo `mutation` do `npm run check` falha.
  Às 10:34 o usuário voltou o link `~/.local/bin/kof` para o 0.7.0; a validação
  final usa o `PATH` normal.
- **Sem `record`.** O KofMut trata `record` como sintaxe não percorrida e marca
  limitação (sem `complete`). As classes puras usam `class` com construtor.
- **`Style` só aceita literal** (`SEM077`). A casca cria os estilos uma vez
  (`ControlStyles`) e escolhe entre eles por um `Bool` decidido em Kof puro;
  `if (flag)` sem operador não gera candidato.
- **Laços sem mutante de laço infinito.** `numberWidth`/`drawNumber` viraram
  `value.toString().length * 16` e `split("")`; fundo e trilha do HUD usam
  contador `i++` (o KofMut não muta `++`) com quantidade fixa: 4×4 ladrilhos e
  10 trechos de trilha. O `<` original nunca chegava à igualdade, então o
  mutante `<=` seria equivalente. A única diferença na cena é um ladrilho de
  fundo a mais em x ≥ 176 quando o deslocamento é 0, fora da tela (176 px).
- **`ControlKeys` recebe o `ControlsGuide`** para marcar e limpar o descarte do
  clique e alternar os detalhes, como o `GameControls` fazia. O guia roda na JVM
  (os testes do piloto já o constroem).

## Milestones

### M0. Medir a linha de base

```bash
mkdir -p .agent/tmp/debt-ui
printf '%s\n' '["src/main/kof/sifuture/GameControls.kf", "src/main/kof/sifuture/GameView.kf"]' > .agent/tmp/debt-ui/mut-scope.json
uptime
kof-mut run --project . --files .agent/tmp/debt-ui/mut-scope.json \
  --config kof-mut.json --report-dir .agent/tmp/debt-ui/m0 --run-id "$(uuidgen)"
```

Registre no aceite os candidatos, mortos e sobreviventes por arquivo, comparados
com o A1, e a contagem de casos de partida em JVM e JS. Rode também as sete
jornadas e guarde as capturas como referência do lote. Elas precisam ser iguais
às do R0 (`debt-r0/journeys-1/png`) antes de qualquer mudança.

### M1. `GameView`: cena testável

1. Por TDD, uma cena pura que, dado um `Game`, devolve o que desenhar em cada tela:
   créditos, menu, controles, jogo, pausa e resultado. Ela cobre cada decisão
   listada em "Onde ficam as decisões hoje", inclusive o HUD, o placar com seus
   dígitos (`numberWidth`, `drawNumber`), as imagens do resultado e os textos dos
   menus e dos créditos com posição e cor.
2. O `GameView` passa a percorrer a cena e desenhar. Ele guarda as imagens e
   mapeia cada tipo e quadro para uma `Image`. O carregamento das imagens pode
   sair para outra classe se o construtor continuar acima do lint.
3. Depois de cada troca na casca, rode a suíte JVM e JS. No fim do M1, rode as
   sete jornadas e a comparação de pixels: `pixel_diff=0`.
4. `npm run lint:sensor` nos arquivos do M1: 0. KofMut nos arquivos do M1: 0
   sobreviventes, e a casca sem candidatos que só o `kof.ui` veria.

### M2. `GameControls`: decisões puras

1. Por TDD, as classes puras para:
   - roteamento de teclas: tecla `1`, espaço, Enter e setas; o que fica preso;
     que clique será descartado; que alvo recebe o teclado; que ação acontece
     (confirmar, especial, alternar o guia, mover);
   - foco: superfície, botão de ação, especial e opção de menu;
   - arranjo de cada tela: que botões ficam desabilitados, que opções aparecem ou
     ficam retidas com o texto "Teclado do jogo", o texto do botão de ação, o
     estado do especial (disponível ou não, com ou sem foco) e o arranjo de
     créditos, controles ou jogo.
2. Os handlers do `GameControls` passam a chamar métodos nomeados dessas classes,
   como o `clicked()` do piloto, e a casca aplica estilos e textos pelo que elas
   decidem. Os estilos podem ir para uma classe própria se o arquivo continuar
   acima do limite.
3. Depois de cada troca, a suíte JVM e JS. No fim do M2, as sete jornadas e a
   comparação de pixels: `pixel_diff=0`.
4. Lint 0 e KofMut 0 nos arquivos do M2.

### M3. Registros e validação final

- Uma seção nova "R5 e R4, lote da UI" em `.agent/validation/sensor-debt-payoff.md`,
  com:
  - o M0;
  - sobreviventes antes e depois, por arquivo;
  - para cada sobrevivente do M0, para onde a decisão foi e o teste que mata o
    mutante correspondente;
  - as refatorações que tiraram equivalentes, com a prova;
  - a divisão final entre casca e classes puras;
  - o número de itens da cena por quadro nas telas de jogo;
  - o tempo gasto.
- Uma linha no `EXECPLAN.md` da raiz e o progresso do plano mestre: a UI deixa de
  ser pendência. Sobram o R6 (fixtures) e o R7 (fechamento).

## Progress

- [x] M0 (16/11, 09:44 a 10:23). KofMut com Kof 0.7.0: 193 candidatos, 0 mortos,
  193 sobreviventes (118 + 75), `complete`; os mesmos 193 do A1. Casos de partida:
  323 em JVM e JS, no 0.7.0 e no 0.6.4. Jornadas: 7/7, 186 PNG, `pixel_diff=0`
  contra o R0 (`.agent/tmp/debt-ui/m0-journeys`).
- [x] M1. Cena em `Sheet`, `Scene`, `Scenes`, `WorldScene` e `HudScene`;
  `GameView` só percorre a cena (0 candidatos). KofMut prévio: 63/63 mortos.
  Lint 0. Jornadas da árvore só com o M1: 7/7, `pixel_diff=0`.
- [x] M2. `ControlKeys`, `KeyRouting` e `MenuChoice` decidem; `GameControls`,
  `ControlStyles`, `DirectionPad`, `SpecialButton` e `MenuOption` só aplicam (0
  candidatos). Lint 0. KofMut final nos 14 arquivos (10:25 a 10:52): 166/166
  mortos, `complete`. Jornadas com M1 e M2: 7/7, `pixel_diff=0`.
- [x] M3. Seção "R5 e R4, lote da UI" no aceite, linha no `EXECPLAN.md` e
  progresso do plano mestre. Validação final (10:53 a 11:48): `unittest`,
  `test:sensors`, `check` (`mutation` 166/166) e `check:task` (sete jornadas
  PASS) com exit 0; `git diff --check` limpo. Desvio do A2: 2 dos 86 testes novos
  não matam mutante (cobrem `discardOptionClick = ""`; o KofMut não muta
  strings).

## Validation

Critérios de aceite. A coluna "Verificação" é o planejado; registre o observado no
aceite.

| # | Contexto, ação e resultado esperado | Verificação |
| --- | --- | --- |
| A1 | KofMut em todo arquivo de produção alterado, depois do M2: `candidates = killed`, 0 sobreviventes, 0 timeouts, `status` `complete` | comando do M0 com a lista de `git diff --name-only main -- src/main` e os novos, outro `--report-dir`; registrar os números |
| A2 | Cada teste novo descreve uma decisão observável (quadro, posição, texto, estado de foco ou tecla, arranjo) e mata ao menos um mutante nomeado da classe pura, falhando por asserção | tabela mutante e teste no aceite |
| A3 | Nenhum equivalente fica anotado. Se sobrar um, ele tem prova e a entrega para antes do commit | seção de equivalentes do aceite |
| A4 | `npm run lint:sensor -- <arquivos de produção alterados e novos>` dá `PASS (0 findings)`, e o mesmo vale para todo arquivo de teste novo | rodar |
| A5 | `npm run dup:sensor` com o diff contra a `main`: 0 achados | rodar |
| A6 | Só arquivos permitidos mudam: `git diff --name-only main` não lista `Main.kf`, `src/main/kof/sifuture/game/`, `tests/*.kf` nem `tests/browser.py` | rodar |
| A7 | O contrato público fica igual: `Main.kf` e as fixtures compilam sem mudança | `npm run check` com `types` e `types:fixtures` PASS |
| A8 | A contagem de casos sobe em relação ao M0, em JVM e JS, no 0.7.0 e no 0.6.4 | `node scripts/kof-tests.mjs --target jvm` e `--target js`, depois com `KOF=~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof` |
| A9 | Comportamento e aparência iguais: as sete jornadas passam e as capturas ficam iguais às do R0 pixel a pixel, no fim do M1, no fim do M2 e na validação final | `debt-tools/journeys.sh`, `debt-tools/pixels.py` e `npm run check:task` |
| A10 | `npm run check` mostra `mutation  PASS`, com os arquivos alterados no escopo, e `CHECK: PASS` | validação final |

Validação final, nesta ordem. O commit só acontece se todos passarem:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
npm run test:sensors
npm run check
npm run check:task
git diff --check
```

Esperado:
- todos com exit 0;
- `npm run check` com `mutation  PASS`, e não SKIP;
- `npm run check:task` com as sete jornadas em PASS.

Obrigações do executor antes de entregar:
- Conferir de novo, pelo código atual e pelo relatório do M0, se cada expectativa
  está certa. Isso é separado de conferir se os testes a demonstram. Em especial:
  um teste da cena que só repete a conta da produção não prova nada. O valor
  esperado vem do jogo como ele aparece hoje: das capturas do R0 ou do código da
  `main` lido à mão.
- Para cada critério de A1 a A10, registrar no aceite o comando, o resultado
  observado e onde está a evidência. Uma suíte verde sozinha não prova cada
  critério.
- Registrar antes da entrega qualquer critério não verificado, cobertura que faltou
  ou falha, sem apresentá-los como atendidos.
