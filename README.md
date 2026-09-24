# SiFuture em Kof: primeiro ciclo jogável

Este recorte executa **menu → Novo Jogo → nave, tiros e meteoros → resultado após três vidas → menu** no navegador. É parte da [especificação do port](.agent/specifications/port-sifuture-to-kof.md), sem representar a versão completa. O mundo lógico mede 176 × 220; cada atualização avança 30 ms. Clique no campo **Clique para teclado** para lhe dar foco, depois use **Enter** e as **setas**. Soltar uma seta interrompe o movimento. Se o campo perder foco, clique nele novamente antes de continuar.

## Preparar Kof

As instruções foram verificadas com **Kof 0.4.10-beta**, SHA **`ebd11a1af42b525c583c28ab444e060fae8a9c6a`**. O checkout local de Kof foi compilado antes de executar `bin/kof`:

```bash
cd /home/renanfranca/projects/kof
mvn -q package -DskipTests
mkdir -p lib
cp "kof-cli/target/kof-cli-$(cat VERSION).jar" lib/kof.jar
bin/kof version
```

Se Maven não estiver no PATH, instale ou use uma distribuição local de Maven. O projeto de SiFuture não modifica o código de Kof.

## Etapa 1: cena e eventos

O programa [`probes/ui-input.kf`](probes/ui-input.kf) cria `Window`, `Canvas(176, 220)`, `Image`, `Input` e `Label`. O `time.interval(30, ...)` redesenha o sprite a cada passo. O `Input.on("keydown", ...)` e `Input.on("keyup", ...)` lê `Event.key()`; `Canvas` não oferece `.on(...)` neste SHA. Uma classe com campos `static` mantém o contador entre chamadas da função anônima.

```bash
cd /home/renanfranca/projects/kof-sifuture
/home/renanfranca/projects/kof/bin/kof build probes/ui-input.kf --target js --output /tmp/sifuture-probe
cp -r assets /tmp/sifuture-probe/
python3 -m http.server 8765 --directory /tmp/sifuture-probe
```

Abra `http://127.0.0.1:8765/`, clique no campo, pressione e solte uma seta. **Experimento:** troque `30` por `60` em `time.interval` e observe o contador avançar mais devagar.

## Etapa 2: regras e testes

[`src/Game.kf`](src/Game.kf) guarda o estado sem depender do desenho. `Game.start(seed)` chama `rng.seed(seed)`; `step()` altera posições, tenta disparar um único laser básico a cada 13 passos normais e soma cinco pontos tanto na colisão nave/meteoro quanto em laser/meteoro. As colisões seguem as condições de borda do jogo histórico, inclusive seus limites inclusivos e a assimetria do laser. O impacto mostra `laser03.png` por um passo sem repetir a pontuação. A nave começa invulnerável por 15 alternâncias de três passos. Após uma colisão, a explosão dura 10 quadros de três passos; só então uma vida é perdida e a nave reinicia. O meteoro atingido continua avançando uma unidade por passo enquanto mostra três quadros de dois passos antes de reaparecer. O campo `shipRightFrame` registra o quadro horizontal escolhido pela última seta pressionada; durante o reinício, o desenho usa o quadro normal. `resultIndex()` separa as faixas de pontuação, inclusive 1500 e 2200. Os blocos `test` no mesmo arquivo exercitam o código de produção e não participam da execução normal.

```bash
cd /home/renanfranca/projects/kof-sifuture
/home/renanfranca/projects/kof/bin/kof test src/Game.kf --target jvm
/home/renanfranca/projects/kof/bin/kof test src/Game.kf --target js
```

Cada comando deve mostrar **16 testes aprovados**. **Experimento:** altere temporariamente o incremento de movimento de `5` para `4` em `step()` e observe o teste de limites falhar; restaure `5` depois.

## Etapa 3: percurso no navegador

[`src/Main.kf`](src/Main.kf) liga os eventos à classe `Game` e desenha separadamente cada tela. `GameView.render()` apenas lê o estado, inclusive os quadros dos sprites históricos: `Middle.png` para o quadro normal e `Middle2.png` quando a direção horizontal escolhida é a direita. O intervalo chama `step()` e depois `render()`. `Window.size(210, 340)` deixa o canvas exibido exatamente em 176 × 220 pixels no Chrome testado. O resultado permanece até Enter. Uma partida normal recebe uma semente variável de `random.int(...)`; os testes passam semente fixa.

```bash
cd /home/renanfranca/projects/kof-sifuture
/home/renanfranca/projects/kof/bin/kof build src --target js --output /tmp/sifuture-game
cp -r assets /tmp/sifuture-game/
python3 -m http.server 8766 --directory /tmp/sifuture-game
```

Abra `http://127.0.0.1:8766/` no navegador. Clique no campo de teclado, pressione Enter, mova a nave com as setas e solte uma delas. Pressione duas direções opostas juntas e observe que a última pressionada vence; ao soltá-la, a outra volta a mover. Observe o piscar inicial, a explosão da nave e o meteoro atingido. Aguarde perder as três vidas; o resultado fica visível até Enter voltar ao menu. **Experimento:** troque a semente de `Game.start()` no teste e compare as posições iniciais dos meteoros; usando a mesma semente novamente, a sequência se repete.

Para repetir a verificação automatizada no Chrome, instale Python Playwright e Pillow e rode, com o servidor acima ativo:

```bash
python3 tests/browser.py
python3 tests/browser_meteor.py
```

O primeiro teste abre a página real, confirma movimento, soltura e a troca de sprite com setas opostas, acelera o tempo do navegador até a derrota, confirma a persistência do resultado e volta ao menu. O segundo compila [`tests/meteor-motion.kf`](tests/meteor-motion.kf) com o modelo real e usa cliques para avançar exatamente um passo de cada vez no Chrome; verifica posição e quadro do meteoro atingido. Python e Playwright servem apenas à automação de teste; a aplicação e a prova visual são escritas em Kof. O JavaScript e o CSS da saída são gerados por Kof.

## Escopo e fontes

Este ciclo inclui o tiro normal, seis meteoros horizontais e colisões. Os outros sistemas da especificação, como créditos, telas de Controles e Opções, pausa, toque, Android, música, itens, inimigos e chefes, pertencem a ciclos posteriores. O campo de teclado precisa de um clique para obter foco; veja a [prova e limitação da entrada](docs/kof-input-gap.md).

As regras usadas foram conferidas em `/home/renanfranca/projects/sifuture/src/AirShip.java`, `AirShipAllShoots.java`, `Meteor.java`, `MeteorArray.java` e `GameCanvas.java`. A sintaxe e o estado de Kof foram conferidos em `/home/renanfranca/projects/kof/training/language/syntax.md`, `learn/35-kof-ui.md`, `learn/37-kofjs.md`, `learn/39-stdlib.md`, `docs/ui/PLAN-CANVAS-WIDGET.md`, `docs/development/DECISIONS.md`, implementação e testes do compilador. As aulas pertinentes de frontend e testes em `/home/renanfranca/projects/curso-completo-de-kof/` serviram de guia didático; o curso declara 0.3.7-beta, por isso o comportamento atual foi confirmado nas fontes Kof 0.4.10-beta do SHA acima. Planos de expansão da UI não são tratados como recursos já disponíveis.

Os sprites em `assets/` vêm do jogo histórico. O [NOTICE](NOTICE) distingue o código licenciado dos recursos de terceiros cujos autores e licenças não foram identificados; este repositório não atribui uma licença nova a eles.
