# SiFuture em Kof: primeiro ciclo jogável

Este recorte executa **menu → Novo Jogo → partida → Pausar/Continuar → resultado após três vidas → menu** no navegador. É parte da [especificação do port](.agent/specifications/port-sifuture-to-kof.md), sem representar a versão completa. O mundo lógico mede 176 × 220; cada atualização avança 30 ms. Clique na área desenhada ou use Tab até **Ativar teclado do jogo** obter foco. As setas movem apenas com esse botão em foco. Um clique na área rearma as setas: se a soltura de uma seta ocorreu fora dos controles, a próxima pressão pode mover imediatamente; o clique sozinho não move. Retornar por Tab conserva a memória das setas e pode exigir uma soltura observada antes da próxima pressão. Enter aciona uma vez por pressão quando o foco está na área ou no botão principal; uma nova ação exige que a soltura de Enter seja observada nos controles. Soltar Enter fora e clicar na área não libera esse bloqueio. Clique e Espaço no botão principal continuam funcionando, inclusive enquanto Enter está pressionado. O botão transparente sobre o canvas não executa uma ação ao receber clique. Uma borda azul indica o foco. Perder o foco limpa o movimento do teclado sem pausar automaticamente.

O direcional abaixo do jogo tem oito botões de 48 × 48 pixels. Pressione um para mover, solte ou saia dele com o mouse para parar. Diagonais combinam os dois eixos. Arrastar o dedo mantém a direção original até a soltura ou cancelamento; deslizar não troca de direção neste ciclo. Enquanto o direcional está pressionado, ele tem prioridade sobre as setas. Depois de soltá-lo, uma seta já mantida não assume o movimento sozinha. Setas pressionadas em outros controles são acompanhadas, mas não movem a nave ao retornar ao canvas por Tab; uma soltura observada libera a próxima pressão. Se essa soltura ocorrer fora da árvore de controles, o retorno por Tab conserva o bloqueio até uma soltura observada. Um clique no canvas libera apenas as setas, sem mover a nave por si só. O direcional fica desabilitado fora da partida. A pausa congela a simulação, inclusive tiros, meteoros e contadores; **Continuar** conserva a partida e requer nova pressão para mover. Este recorte implementa a [issue #3](https://github.com/renanfranca/kof-sifuture/issues/3); as necessidades restantes estão relacionadas à [issue #4](https://github.com/renanfranca/kof-sifuture/issues/4).

- **Direita, soltura fora e retorno por clique:** o clique no canvas não move; a primeira nova pressão de Direita move.
- **Direita, soltura fora e retorno por Tab:** a primeira pressão pode continuar bloqueada; solte Direita dentro dos controles e pressione novamente para mover.
- **Enter, soltura fora e retorno por clique:** o clique no canvas conserva o bloqueio de Enter; solte Enter dentro dos controles e pressione novamente para confirmar.

## Kof instalado

Use a instalação de Kof disponível no `PATH`. Confirme que o comando está acessível:

```bash
kof version
```

O build e os testes abaixo passaram com a instalação Linux de **Kof 0.5.0-beta** encontrada no `PATH`. O checkout local do código-fonte de Kof é usado para consultar a implementação e sua documentação, sem ser necessário para compilar o SiFuture. Os resultados anteriores com o checkout no SHA `317d9f6b1c3e27032cc955a05f859f6c627d9338` permanecem no [histórico de validação](EXECPLAN.md).

## Compilar a aplicação com o workaround

Execute estes comandos **na raiz do SiFuture**. `build --output` é o comando para compilar a aplicação deste projeto; passe a ele o diretório onde deseja receber a página pronta:

```bash
cd /home/renanfranca/projects/kof-sifuture
python3 scripts/kof_project.py build --output /tmp/sifuture-game
```

Ao terminar sem erro, abra `/tmp/sifuture-game/index.html` por um servidor HTTP local, pois a página carrega o módulo JS e os sprites de `assets/`:

```bash
python3 -m http.server 8766 --directory /tmp/sifuture-game
```

Visite `http://127.0.0.1:8766/`. Encerre o servidor com `Ctrl+C`. Para usar outra instalação do compilador, passe `--kof /caminho/para/kof` ao comando `build` ou defina `KOF`. A escolha é `--kof`, depois `KOF`, depois `kof` do `PATH`. Se uma sessão de terminal ainda tiver `KOF` definido pelo procedimento antigo, use `unset KOF` para voltar ao `kof` instalado no `PATH`.

**WORKAROUND:** o script copia `src/main/kof` para uma pasta temporária fora do projeto, cria ali uma entrada `import sifuture.*`, chama `kof build ... --target js` e só copia o resultado e os assets para `--output` depois de verificar `index.html` e `Default.mjs`. A pasta de fontes temporárias é removida automaticamente. Não é preciso mover fontes, copiar assets ou criar a entrada manualmente. Se aparecer um erro sobre `TMPDIR` ou `kof.toml` ancestral, configure `TMPDIR` para um diretório temporário fora de qualquer projeto Kof e repita o comando. Os imports de pacote e arquivo usados nessa entrada seguem a [referência de módulos](/home/renanfranca/projects/kof/docs/language-reference/modules.md).

**Estado da [issue Kof #708](https://github.com/KofLang/Kof4j/issues/708):** no branch `lab`, o Kof já corrigiu o encaminhamento de `moduleRoot` na API Java, passou a usar a raiz informada ao executar testes de uma única árvore e passou a falhar explicitamente quando build ou test não encontram fontes. Ainda não há interface no CLI para compilar e testar diretamente com `src/main/kof` e `src/test/kof` juntos. Por isso, a suíte deste jogo, que importa a implementação da outra árvore, ainda precisa da preparação acima. A instalação `kof 0.5.0-beta` usada nesta documentação precede essas correções; a verificação dos artefatos pelo script continua necessária também após a atualização do compilador.

## Regras, módulos e testes

[`src/main/kof/sifuture/game/Game.kf`](src/main/kof/sifuture/game/Game.kf) coordena cada passo lógico. [`src/main/kof/sifuture/game/Ship.kf`](src/main/kof/sifuture/game/Ship.kf) governa movimento, explosão, reinício e imagem da nave; [`src/main/kof/sifuture/game/Lasers.kf`](src/main/kof/sifuture/game/Lasers.kf), [`src/main/kof/sifuture/game/Shot.kf`](src/main/kof/sifuture/game/Shot.kf) e [`src/main/kof/sifuture/game/Meteor.kf`](src/main/kof/sifuture/game/Meteor.kf) governam seus próprios contadores, posições e animações. [`src/main/kof/sifuture/game/Rules.kf`](src/main/kof/sifuture/game/Rules.kf) nomeia limites, durações, intervalos de quadros e o limite usado para sortear a semente. Os limites direito e inferior da nave são calculados pelas dimensões do mundo e da nave. `Game.start(seed)` chama `rng.seed(seed)` para repetir partidas em testes.

A ordem de `step()` preserva uma sutileza: a fase anterior ao passo decide se há movimento e tentativa de disparo; a fase após o avanço da nave decide se há colisão. Assim, no 45º passo de reinício a nave já pode colidir, mas o laser só volta a ser tentado no seguinte. Cada meteoro sobreposto à nave inicia sua animação, enquanto a colisão da nave rende cinco pontos uma única vez. O impacto de laser mostra `laser03.png` por um passo. A explosão dura 10 quadros de três passos; o reinício, 15 alternâncias de três passos. Os meteoros atingidos seguem avançando uma unidade por passo durante três quadros de dois passos.

[`src/main/kof/sifuture/game/State.kf`](src/main/kof/sifuture/game/State.kf) usa enums para a tela, a fase da nave e as direções. `Ship.lastX` e `Ship.lastY` guardam a última direção pressionada como `Direction`, permitindo escolher entre duas setas opostas. Na versão Kof 0.5.0-beta verificada, enums são valores próprios: a [referência de classes](/home/renanfranca/projects/kof/docs/language-reference/classes.md) e os testes do compilador confirmam comparação entre constantes do mesmo enum. `training/language/types.md` ainda os descreve como strings; essa descrição diverge da implementação atual. Um campo mutável como `ship.phase` usa uma classe com campos explícitos, seguindo o [idioma de classes](/home/renanfranca/projects/kof/training/idioms/classes.md). O [manifesto](kof.toml) conserva o nome do projeto na raiz. **WORKAROUND:** o CLI Kof 0.5.0-beta verificado ainda não recebe duas raízes de fontes separadas para esta preparação. [`scripts/kof_project.py`](scripts/kof_project.py) copia os bytes das fontes canônicas para uma árvore temporária sem manifesto ancestral, gera uma entrada de import específica e remove a árvore após cada comando. Essa preparação é infraestrutura provisória do projeto, não uma regra ou um idioma da linguagem. A suíte [`GameJourney.kf`](src/test/kof/sifuture/game/GameJourney.kf) importa `sifuture.game.*` e usa a única implementação das regras em `src/main/kof`. Se `TMPDIR` ficar dentro do projeto ou sob outro `kof.toml`, escolha um diretório temporário externo.

```bash
cd /home/renanfranca/projects/kof-sifuture
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 scripts/kof_project.py test --target jvm --suite sifuture/game/GameJourney.kf
```

Cada execução da suíte deve mostrar **26 testes aprovados**. As suítes `.kf` em `src/test/kof` são descobertas recursivamente e executadas em ordem de caminho, cada uma em uma árvore temporária nova; falhas não interrompem as suítes seguintes. `--suite` seleciona uma delas, relativa à raiz de testes. `--kof CAMINHO` em cada comando prevalece sobre `KOF`, que prevalece sobre `kof` do PATH. **Experimento:** altere temporariamente `SHIP_SPEED` de `5` para `4` em `Rules.kf`, observe o teste de movimento falhar e restaure `5`.

## Percurso no navegador

[`src/main/kof/sifuture/Main.kf`](src/main/kof/sifuture/Main.kf) cria a janela e avança o relógio. [`src/main/kof/sifuture/GameControls.kf`](src/main/kof/sifuture/GameControls.kf) monta a área de foco, o direcional e o botão principal; usa `Event.key()` e `Event.target()` na árvore de controles para distinguir a origem do teclado. Os estilos da área de foco são criados na montagem e reutilizados. [`src/main/kof/sifuture/GameView.kf`](src/main/kof/sifuture/GameView.kf) desenha cada tela; `GameView.render()` apenas lê o estado, inclusive os quadros dos sprites históricos: `Middle.png` para o quadro normal e `Middle2.png` somente enquanto a direção horizontal efetiva é direita. Soltar a seta restaura `Middle.png` no próximo passo, mesmo com movimento vertical. Esta é uma exceção deliberada ao histórico, que mantinha o quadro de fogo após a soltura. O intervalo chama `step()` e depois `render()`. `Window.size(240, 510)` deixa o canvas exibido exatamente em 176 × 220 pixels no Chrome testado. O resultado permanece até Enter ou o botão **Voltar ao menu**. Uma partida normal recebe uma semente variável de `random.int(...)`; os testes passam semente fixa.

```bash
cd /home/renanfranca/projects/kof-sifuture
python3 scripts/kof_project.py build --output /tmp/sifuture-game
python3 -m http.server 8766 --directory /tmp/sifuture-game
```

Abra `http://127.0.0.1:8766/` no navegador. Clique em **Novo Jogo**, depois use o direcional ou ative o teclado por clique sobre o canvas ou Tab. Pressione Enter para pausar ou continuar, mova a nave com as setas e solte uma delas. Pressione duas direções opostas juntas e observe que a última pressionada vence; ao soltá-la, a outra volta a mover. Observe o piscar inicial, a explosão da nave e o meteoro atingido. Aguarde perder as três vidas; o resultado fica visível até Enter ou **Voltar ao menu** retornar ao menu. **Experimento:** troque a semente de `Game.start()` no teste e compare as posições iniciais dos meteoros; usando a mesma semente novamente, a sequência se repete.

Para repetir a verificação automatizada no Chrome, instale Python Playwright e Pillow e rode os comandos abaixo. Cada teste compila, inicia um servidor em `127.0.0.1` com porta livre e limpa navegador, servidor e temporários. O teste principal aceita uma URL opcional já servida (`python3 tests/browser.py URL`); ambos aceitam `--kof CAMINHO`:

```bash
python3 tests/browser.py
python3 tests/browser_meteor.py
```

O primeiro teste abre a página real, exercita os botões, teclado por Tab/Enter/Espaço, recuperação de teclas, direcional com mouse e touch emulado, pausa congelada, derrota, resultado persistente e retorno ao menu. O segundo compila [`tests/meteor-motion.kf`](tests/meteor-motion.kf) com o pacote `sifuture.game` real e usa cliques para avançar exatamente um passo de cada vez no Chrome; verifica posição e quadro do meteoro atingido. Python também prepara build e suítes; Playwright e Pillow são usados apenas nos testes de navegador. A automação pode ser validada com `python3 -m unittest discover -s tests -p 'test_kof_project.py'`. A aplicação e a prova visual são escritas em Kof. O JavaScript e o CSS da saída são gerados por Kof.

## Escopo e fontes

Este ciclo inclui o tiro normal, seis meteoros horizontais, colisões, direcional de oito zonas e pausa manual com **Continuar**. Continuam pendentes para a v1: créditos, telas de Controles e Opções, opções completas da pausa, ataque especial, deslize que troca direção, múltiplos contatos, soltura fora da área, eventos gerais da página, pausa automática, redimensionamento, Android, música, itens, inimigos e chefes. O teclado requer foco no botão transparente sobre o canvas, ativado por clique ou Tab.

As regras usadas foram conferidas em `/home/renanfranca/projects/sifuture/src/AirShip.java`, `AirShipAllShoots.java`, `Meteor.java`, `MeteorArray.java` e `GameCanvas.java`. A sintaxe e o estado de Kof foram conferidos em `/home/renanfranca/projects/kof/training/language/syntax.md`, `training/language/types.md`, `training/idioms/classes.md`, `training/anti-patterns/sentinel-values.md`, `learn/07-classes-and-objects.md`, `learn/23-testing.md`, `learn/35-kof-ui.md`, `learn/37-kofjs.md`, `learn/39-stdlib.md`, `docs/language-reference/classes.md`, `docs/ui/PLAN-CANVAS-WIDGET.md`, `docs/development/DECISIONS.md`, implementação e testes do compilador. As aulas pertinentes de frontend e testes em `/home/renanfranca/projects/curso-completo-de-kof/` serviram de guia didático; o curso declara 0.3.7-beta, por isso o comportamento atual foi confirmado nas fontes Kof 0.5.0-beta do SHA acima. Planos de expansão da UI não são tratados como recursos já disponíveis.

Os sprites em `assets/` vêm do jogo histórico. O [NOTICE](NOTICE) distingue o código licenciado dos recursos de terceiros cujos autores e licenças não foram identificados; este repositório não atribui uma licença nova a eles.
