# SiFuture em Kof: fase, HUD e resultado

Este recorte executa **menu → Novo Jogo → partida → Pausar/Continuar → resultado por fim da fase ou última vida → menu** no navegador. É parte da [especificação do port](.agent/specifications/port-sifuture-to-kof.md), sem representar a versão completa. O mundo lógico mede 176 × 220; cada atualização avança 30 ms. Clique na área desenhada ou use Tab até **Ativar teclado do jogo** obter foco. As setas movem apenas com esse botão em foco. Um clique na área rearma as setas: se a soltura de uma seta ocorreu fora dos controles, a próxima pressão pode mover imediatamente; o clique sozinho não move. Retornar por Tab conserva a memória das setas e pode exigir uma soltura observada antes da próxima pressão. Enter aciona uma vez por pressão quando o foco está na área ou no botão principal; uma nova ação exige que a soltura de Enter seja observada nos controles. Soltar Enter fora e clicar na área não libera esse bloqueio. Clique e Espaço no botão principal continuam funcionando, inclusive enquanto Enter está pressionado. O botão transparente sobre o canvas não executa uma ação ao receber clique. Uma borda azul indica o foco. Perder o foco limpa o movimento do teclado sem pausar automaticamente.

O direcional abaixo do jogo tem oito botões de 48 × 48 pixels. Pressione um para mover, solte ou saia dele com o mouse para parar. Diagonais combinam os dois eixos. Arrastar o dedo mantém a direção original até a soltura ou cancelamento; deslizar não troca de direção neste ciclo. Enquanto o direcional está pressionado, ele tem prioridade sobre as setas. Depois de soltá-lo, uma seta já mantida não assume o movimento sozinha. Setas pressionadas em outros controles são acompanhadas, mas não movem a nave ao retornar ao canvas por Tab; uma soltura observada libera a próxima pressão. Se essa soltura ocorrer fora da árvore de controles, o retorno por Tab conserva o bloqueio até uma soltura observada. Um clique no canvas libera apenas as setas, sem mover a nave por si só. O direcional fica desabilitado fora da partida. A pausa congela a simulação, inclusive tiros, meteoros e contadores; **Continuar** conserva a partida e requer nova pressão para mover. Este recorte implementa a [issue #3](https://github.com/renanfranca/kof-sifuture/issues/3); as necessidades restantes estão relacionadas à [issue #4](https://github.com/renanfranca/kof-sifuture/issues/4).

- **Direita, soltura fora e retorno por clique:** o clique no canvas não move; a primeira nova pressão de Direita move.
- **Direita, soltura fora e retorno por Tab:** a primeira pressão pode continuar bloqueada; solte Direita dentro dos controles e pressione novamente para mover.
- **Enter, soltura fora e retorno por clique:** o clique no canvas conserva o bloqueio de Enter; solte Enter dentro dos controles e pressione novamente para confirmar.

## Fase e resultado

A fase vai da posição 5 à 176, com entrada do subchefe em 88. A entrada avança o marcador para 89; combate e explosão suspendem a trilha. Depois, a miniatura retoma um avanço a cada dez passos. Portanto, a duração depende do combate. A pausa congela todos os relógios e redesenhar apenas consulta o modelo. O chefe final continua pendente.

A posição é derivada em [Game.kf](src/main/kof/sifuture/game/Game.kf):

```kof
var position = 5 + stageSteps / 10
if (position > Rules.WORLD_WIDTH) { return Rules.WORLD_WIDTH }
return position
```

`steps` conta atualizações da partida; `stageSteps` conta o avanço da trilha e o incremento histórico da entrada. Durante combate e explosão, apenas o primeiro continua. A consulta evita guardar outra cópia da posição. O [training de estado duplicado](/home/renanfranca/projects/kof/training/anti-patterns/duplicate-state.md:73) orienta:

> If a value can be derived from another, derive it (method or function).

O subchefe tem resistência 30, deslocamento de uma unidade por eixo e três tiros próprios, com tentativa a cada 12 passos normais. Laser retira uma unidade; blaster aplica sua resistência restante. O especial conserva os marcadores históricos de seis passos, incluindo reaplicação quando outro feixe inicia contato. Contato corporal explode uma nave normal; durante reinício invulnerável, não altera nenhuma das duas entidades, exceção explícita ao original. O golpe fatal dá 600, 300 ou 150 pontos conforme `lifeTime` ≤30, ≤60 ou >60; esse contador avança a cada 36 passos normais, sem representar segundos. Os dez quadros de explosão duram três passos cada. Os itens recorrentes continuam sem duplicação ou reposicionamento por prêmio.

Os seis meteoros horizontais mantêm seus índices. Dois verticais entram quando a posição ultrapassa 30, descem uma unidade por passo e mostram três quadros de impacto, um passo por quadro. O par relança quando ambos ficam inativos e o subchefe está inativo; os já lançados terminam seu percurso durante o combate. As colisões preservam nave → laser → blaster → especial, com prêmio único por meteoro. Os dois corações continuam circulando desde o início; vidas podem ultrapassar três.

O HUD usa os sprites históricos sem transformação: trilha, miniatura conforme uma, duas ou três vidas ou mais, escore à direita, contador de vidas abaixo e indicador de especial em `(50, 21)`. Os indicadores são desenhados depois das entidades para ficarem visíveis sobre os feixes. O mundo continua 176 × 220 e a nave conserva o limite superior `y = 30`.

Ao concluir a fase ou perder a última vida, o escore definitivo fica preservado e a contagem exibida começa em zero. Cada passo acrescenta cinco pontos, limitado ao total exato. A avaliação só aparece ao terminar, nas faixas `<1500`, `1500–2199`, `2200–3299` e `≥3300`. **Concluir contagem** ou Enter mostra o total imediatamente; uma nova confirmação em **Voltar ao menu** retorna ao menu. Escore zero já começa concluído. Segurar Enter não confirma duas vezes.

Durante o resultado, fundo, meteoros, itens, subchefe, tiros automáticos visuais e efeitos continuam. Colisões, coleta e comandos da nave ficam encerrados; vidas, nível, cargas e posição da fase permanecem estáveis. A explosão pendente termina sem nova perda de vida e fica oculta, sem tentar desenhar um quadro de índice 10. Escore e avaliação ficam centralizados sobre a cena.

[GameJourney.kf](src/test/kof/sifuture/game/GameJourney.kf) prova as regras em JVM e JS. [browser_stage.py](tests/browser_stage.py) exercita o modelo, desenho e controles reais no Chrome em 320 e 1200 pixels, com relógio determinístico, comparação de sprites, percurso completo e redesenhos sem avanço. [browser_subchief.py](tests/browser_subchief.py) verifica encontro, tiros, especial, explosão, pausa, retomada e nova partida com os mesmos componentes reais em 320/1200 pixels. O registro de aceite fica em [stage-hud-result.md](.agent/validation/stage-hud-result.md). Música, Android, chefe final, menus completos e reformulação dos controles seguem fora deste ciclo.

A limpeza de comandos também restaura o quadro normal da nave na entrada do resultado, em pausa e na perda de foco do teclado. Os meteoros verticais reiniciam entre −153 e 0 na criação ou após impacto; após sair pelo fundo, usam a faixa histórica de −171 até 0, mantendo a espera pelo par. As regressões e o aceite visual estão em [ship-meteor-reset.md](.agent/validation/ship-meteor-reset.md).

## Coleta e evolução

Há sempre um coração de evolução e um de vida em circulação. Os dois conservam os sprites originais: o coração de evolução percorre os **cinco quadros `iten`**; o coração de vida pulsa pelos **onze quadros `life`, avançando e voltando**. A animação diferencia os itens: evolução melhora os tiros; vida acrescenta uma vida, inclusive acima das três iniciais. Cada coleta concede dez pontos uma única vez e exibe três quadros de efeito antes do relançamento. A nave precisa estar no estado normal para coletar; o piscar inicial e a explosão não permitem coleta.

| Coletas de evolução | Armamento |
| --- | --- |
| Nenhuma | Laser básico, um ativo por vez. |
| Primeira | Laser animado; um lançamento por tentativa e até três em circulação. |
| Segunda | Acrescenta o blaster no gatilho de seis ciclos do laser. |
| Terceira | Mantém o laser e aumenta a frequência do blaster. |
| Seguintes | Guardam cargas de especial, mantendo a terceira evolução. |

O laser tenta disparar a cada 13 passos normais. O blaster suporta dois impactos; cada feixe do especial suporta dez. Na morte, a vida diminui ao terminar a explosão: perde-se uma carga guardada ou, sem carga, um nível de tiro, até o básico. Os projéteis lançados continuam seu movimento e efeitos. A pausa congela também fundo, itens e animações.

O botão **Especial**, de 72 × 64 pixels, fica à direita do direcional, separado por 16 pixels e com o centro do direcional vazio. Pressione-o com mouse ou toque; um segundo dedo pode disparar enquanto o primeiro move a nave. A tecla **1**, com foco no jogo ou no botão Especial, faz a mesma tentativa. Enter e Espaço no botão Especial também o ativam. Segurar a tecla ou o botão não repete o disparo. Uma tentativa recusada não fica pendente para depois: solte e pressione novamente. O botão fica desabilitado sem carga, durante outro especial, na pausa ou quando a nave não está normal. A exceção é **preservar foco até registrar a soltura; depois desabilitar normalmente**: enquanto o Especial estiver focado e alguma tecla de especial continuar mantida, o botão permanece habilitado nativamente, com opacidade `0.5` quando indisponível. Isso permite observar a soltura sem autorizar outro disparo. A última soltura ou a saída do botão reaplica imediatamente a disponibilidade; se os feixes terminarem antes da soltura e ainda houver carga, o botão fica disponível com opacidade `1`, mas outra tentativa exige soltar e pressionar novamente. Soltar **1**, Enter ou Espaço em qualquer controle do jogo libera o bloqueio; soltar fora dos controles conserva-o. Setas + **1** continuam disponíveis com foco na área do jogo. O cabeçalho mostra apenas o ícone original enquanto houver alguma carga, inclusive durante indisponibilidade temporária; não mostra sua quantidade.

A regra de coleta está em [Game.kf](src/main/kof/sifuture/game/Game.kf):

```kof
if (item.collect(ship)) {
    score = score + 10
    if (item.kind == ItemKind.Life) { ship.lives = ship.lives + 1 }
    else { weapons.evolve() }
}
```

`collect` retorna verdadeiro somente na primeira coleta. Por isso os dez pontos e o benefício são concedidos juntos uma vez. `ship.lives + 1` não limita a vida a três; o teste de percurso observa a passagem de 3 para 4 em JVM, JS e Chrome.

O estado mutável segue o [training de classes](/home/renanfranca/projects/kof/training/language/classes.md:11):

> For **mutable state**, use fields + `constructor(...)`

O [Learn Kof, Classes and Objects](/home/renanfranca/projects/kof/learn/07-classes-and-objects.md:65) ensina campos que podem ser alterados diretamente. `Weapons` concentra nível, cargas, cadência e projéteis; `Game.step()` avança o modelo, e `GameView.render()` consulta os quadros. Assim, redesenhar sem avançar a partida não acelera animações. Os testes de pausa e redesenho exercitam esse comportamento no Chrome.

**Correção histórica dos assets:** os três grupos do especial usam `e0`–`e2`, `e3`–`e5` e `e6`–`e8`, respectivamente laranja, azul-claro e azul-escuro. `AirShipEspecialShoot.java` tentava carregar `especial0`–`especial8` e usava índices 3–8 em um vetor de três posições para as cores azuis. A cena Kof usa os arquivos existentes em grupos por cor. Isso corrige o carregamento sem substituir os desenhos; o [NOTICE](NOTICE) continua aplicável.

O percurso [browser_weapons.py](tests/browser_weapons.py) compila a fixture Kof com modelo, desenho e controles reais, injeta posições determinísticas e verifica os pixels dos itens, efeitos, lasers, blaster e nove quadros do especial. Verifica vida 4, indicador, pausa, repetição de teclas, tentativas recusadas, cancelamento de toque e as duas ordens de soltura dos dedos. Também abre a aplicação normal em 320 e 1200 pixels. As regressões de soltura verificam foco preservado para `1`, Enter e Espaço, soltura em outro controle, teclas simultâneas e bloqueio conservado quando a soltura ocorre fora dos controles. Evidências locais ficam em `.agent/tmp/`; os registros versionados de aceite ficam em [background-items-weapons.md](.agent/validation/background-items-weapons.md) e [special-key-release.md](.agent/validation/special-key-release.md).

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

Cada execução da suíte deve mostrar **47 testes aprovados**. As suítes `.kf` em `src/test/kof` são descobertas recursivamente e executadas em ordem de caminho, cada uma em uma árvore temporária nova; falhas não interrompem as suítes seguintes. `--suite` seleciona uma delas, relativa à raiz de testes. `--kof CAMINHO` em cada comando prevalece sobre `KOF`, que prevalece sobre `kof` do PATH. **Experimento:** altere temporariamente `SHIP_SPEED` de `5` para `4` em `Rules.kf`, observe o teste de movimento falhar e restaure `5`.

## Percurso no navegador

[`src/main/kof/sifuture/Main.kf`](src/main/kof/sifuture/Main.kf) cria a janela e avança o relógio. [`src/main/kof/sifuture/GameControls.kf`](src/main/kof/sifuture/GameControls.kf) monta a área de foco, o direcional e o botão principal; usa `Event.key()` e `Event.target()` na árvore de controles para distinguir a origem do teclado. Os estilos da área de foco são criados na montagem e reutilizados. [`src/main/kof/sifuture/GameView.kf`](src/main/kof/sifuture/GameView.kf) desenha cada tela; `GameView.render()` apenas lê o estado, inclusive os quadros dos sprites históricos: `Middle.png` para o quadro normal e `Middle2.png` somente enquanto a direção horizontal efetiva é direita. Soltar a seta restaura `Middle.png` no próximo passo, mesmo com movimento vertical. Esta é uma exceção deliberada ao histórico, que mantinha o quadro de fogo após a soltura. O intervalo chama `step()` e depois `render()`. `Window.size(320, 510)` deixa o canvas exibido exatamente em 176 × 220 pixels no Chrome testado. O resultado permanece até Enter ou o botão **Voltar ao menu**. Uma partida normal recebe uma semente variável de `random.int(...)`; os testes passam semente fixa.

```bash
cd /home/renanfranca/projects/kof-sifuture
python3 scripts/kof_project.py build --output /tmp/sifuture-game
python3 -m http.server 8766 --directory /tmp/sifuture-game
```

Abra `http://127.0.0.1:8766/` no navegador. Clique em **Novo Jogo**, depois use o direcional ou ative o teclado por clique sobre o canvas ou Tab. Pressione Enter para pausar ou continuar, mova a nave com as setas e solte uma delas. Pressione duas direções opostas juntas e observe que a última pressionada vence; ao soltá-la, a outra volta a mover. Observe o piscar inicial, a explosão da nave e o meteoro atingido. Aguarde perder as três vidas; o resultado fica visível até Enter ou **Voltar ao menu** retornar ao menu. **Experimento:** troque a semente de `Game.start()` no teste e compare as posições iniciais dos meteoros; usando a mesma semente novamente, a sequência se repete.

Para repetir a verificação automatizada no Chrome, instale Python Playwright e Pillow e rode os comandos abaixo. Cada teste compila, inicia um servidor em `127.0.0.1` com porta livre e limpa navegador, servidor e temporários. O teste da aplicação aceita uma URL opcional já servida (`python3 tests/browser.py URL`); os quatro aceitam `--kof CAMINHO`:

```bash
python3 tests/browser.py
python3 tests/browser_controls.py
python3 tests/browser_meteor.py
python3 tests/browser_weapons.py
python3 tests/browser_stage.py
```

O primeiro teste abre a aplicação normal e verifica o menu antes do primeiro ciclo, Enter/Espaço, confirmação conservadora e pausa congelada. Para derrota, resultado persistente, retorno ao menu e nova partida, usa a fixture Kof com o mesmo modelo, desenho e controles, provocando três colisões determinísticas. A coleta de vida e a evolução tornam a espera por uma derrota espontânea inadequada como critério de teste. O segundo compila a fixture [`tests/controls.kf`](tests/controls.kf) com o modelo, o desenho e os controles reais. Cada cenário abre um contexto novo no Chrome e avança o relógio em ciclos de 30 ms para verificar por pixels movimento, propulsão, foco, retorno por clique ou Tab, direcional com mouse e touch. O terceiro compila [`tests/meteor-motion.kf`](tests/meteor-motion.kf) com o pacote `sifuture.game` real e usa cliques para avançar exatamente um passo de cada vez no Chrome; verifica posição e quadro do meteoro atingido. Python também prepara build e suítes; Playwright e Pillow são usados apenas nos testes de navegador. A automação pode ser validada com `python3 -m unittest discover -s tests -p 'test_kof_project.py'`. A aplicação e as fixtures visuais são escritas em Kof. O JavaScript e o CSS da saída são gerados por Kof.

## Escopo e fontes

Este ciclo inclui fundo estrelado em movimento, itens de vida e evolução, progressão dos lasers, blaster e especial, seis meteoros horizontais, colisões, direcional de oito zonas e pausa manual com **Continuar**. Dois dedos podem combinar movimento e especial, soltando cada contato separadamente. Continuam pendentes para a v1: créditos, telas de Controles e Opções, opções completas da pausa, deslize que troca direção, reformulação geral dos controles e do multitouch, soltura fora da área, eventos gerais da página, pausa automática, redimensionamento, Android, música, outros inimigos e chefes. O teclado requer foco no botão transparente sobre o canvas, ativado por clique ou Tab.

As regras usadas foram conferidas em `/home/renanfranca/projects/sifuture/src/AirShip.java`, `AirShipAllShoots.java`, `Meteor.java`, `MeteorArray.java` e `GameCanvas.java`. A sintaxe e o estado de Kof foram conferidos em `/home/renanfranca/projects/kof/training/language/syntax.md`, `training/language/types.md`, `training/idioms/classes.md`, `training/anti-patterns/sentinel-values.md`, `learn/07-classes-and-objects.md`, `learn/23-testing.md`, `learn/35-kof-ui.md`, `learn/37-kofjs.md`, `learn/39-stdlib.md`, `docs/language-reference/classes.md`, `docs/ui/PLAN-CANVAS-WIDGET.md`, `docs/development/DECISIONS.md`, implementação e testes do compilador. As aulas pertinentes de frontend e testes em `/home/renanfranca/projects/curso-completo-de-kof/` serviram de guia didático; o curso declara 0.3.7-beta, por isso o comportamento atual foi confirmado nas fontes Kof 0.5.0-beta do SHA acima. Planos de expansão da UI não são tratados como recursos já disponíveis.

Os sprites em `assets/` vêm do jogo histórico. O [NOTICE](NOTICE) distingue o código licenciado dos recursos de terceiros cujos autores e licenças não foram identificados; este repositório não atribui uma licença nova a eles.

## CI Kof e GitHub Pages

O workflow [Kof CI and GitHub Pages](.github/workflows/kof-ci-and-pages.yml) executa em todo **PR destinado a `main`** e todo **push em `main`**, inclusive alterações apenas em documentação ou assets. Os checks **Kof tests (jvm)** e **Kof tests (js)** executam separadamente o comando completo `python3 scripts/kof_project.py test --target ALVO`. A matriz usa `fail-fast: false`: a falha de um alvo não cancela o outro e impede build e publicação. A descoberta recursiva inclui novas suítes aninhadas. Esse CI executa somente as suítes Kof; Python é o wrapper existente. Não instala nem executa testes Python, Playwright, navegadores ou Pillow.

Os testes JS usam o engine embarcado, conforme o [treinamento de alvos Kof](/home/renanfranca/projects/kof/training/reference/targets.md:135):

> ES Modules 2022+ via embedded GraalJS (KofJsRunner) — no Node.js

O [capítulo de testes do Learn Kof](/home/renanfranca/projects/kof/learn/23-testing.md:42) registra:

> Each test runs **in isolation** (one failing does not interrupt the others).

Essa regra trata dos casos dentro de uma invocação Kof. A matriz do workflow preserva adicionalmente a independência entre JVM e JS. Ela não demonstra o funcionamento da interface publicada no navegador.

### Uma distribuição por resolução

[`scripts/kof_ci.sh`](scripts/kof_ci.sh) é um helper Bash com três operações. Requer Bash, `gh` autenticado, `jq`, `curl`, `sha256sum` e `tar`.

- `resolve BUNDLE SHA`: percorre todas as páginas de releases e assets de `KofLang/Kof4j`, exclui `draft: true` e `prerelease: true` e escolhe o arquivo oficial Linux x86_64 de maior `published_at`. Um sufixo `beta` não exclui uma release elegível. Exige seu `SHA256SUMS`, exatamente uma entrada válida para o nome do arquivo, digest correto e tag resolvida até um commit, inclusive tags anotadas. Falhas e ambiguidades encerram a execução sem recorrer a outro compilador.
- `install BUNDLE DIRETORIO SHA`: valida a revisão SiFuture do manifesto, confere novamente checksum e digest, extrai em diretório novo e valida `VERSION`, `kof version` e JVM embarcada. Em Actions, grava `KOF` em `GITHUB_ENV`; localmente, retorna JSON com o caminho do launcher.
- `check-main OWNER/REPOSITORY SHA`: consulta o commit atual de `main` e retorna `fresh: true` ou `false`. Um SHA superado produz diagnóstico explícito e pula a publicação. Falha de API ou resposta inválida retorna erro; nunca autoriza deploy.

A distribuição é completa, conforme o [treinamento de instalação](/home/renanfranca/projects/kof/training/distribution/install.md:13):

> The official package contains: compiler, CLI, runtime, stdlib, tooling, editor
> support, embedded OpenJDK and documentation.

Por isso o CI instala o pacote oficial e exige a JVM embarcada, usando seu launcher por `KOF`. Não usa JAR avulso, compilação do checkout Kof ou cache de compilador. O job produtor transfere o arquivo original, `SHA256SUMS` e `manifest.json` em `kof-RUN_ID-TENTATIVA`. Testes e build baixam o nome recebido pelo output desse produtor e não consultam releases novamente.

O manifesto, logs e resumos registram versão, release e tag, commit completo Kof, ID/nome/URL do arquivo, SHA-256 verificado e SHA completo SiFuture. Todos os checkouts usam explicitamente `github.sha`; em PR, essa é a revisão de merge testada pelo evento. Os logs de cada alvo e do build ficam nos respectivos jobs e em artefatos separados, retidos por 30 dias.

### Publicação e atualização de main

Antes da primeira publicação, habilite **Settings → Pages → Source: GitHub Actions**. O workflow usa `actions/configure-pages` com `enablement: false`: Pages desabilitado faz o deploy falhar e deve ser corrigido nas configurações do repositório. O endereço esperado é [https://renanfranca.github.io/kof-sifuture/](https://renanfranca.github.io/kof-sifuture/).

Somente push em `main`, após ambos os checks aprovados, executa o build existente em diretório novo e vazio. `actions/upload-pages-artifact` recebe a raiz da saída inteira: HTML, módulos, runtimes e assets conservam os caminhos relativos. Não há uma pasta extra `kof-sifuture` dentro do pacote; o prefixo `/kof-sifuture/` pertence à URL de Pages. O [Learn Kof JS](/home/renanfranca/projects/kof/learn/37-kofjs.md:54) descreve esse modelo:

> `kof build --target=js` generates `index.html` + modules: serve the
> folder as a static web application (any HTTP server).

Os jobs comuns têm somente `contents: read`. Apenas o deploy recebe `pages: write` e `id-token: write`, entra no ambiente `github-pages` e expõe a URL publicada. PRs não entram nesse ambiente nem produzem artefato Pages.

O deploy inteiro mantém o grupo fixo `kof-sifuture-pages`, com `cancel-in-progress: false` e `queue: max`. Dentro dele, `check-main` compara o SHA construído com o `main` atual imediatamente antes de `actions/deploy-pages`. A [documentação de concorrência](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency) explica que a fila segue a chegada à exclusividade, que pode diferir da ordem dos commits. Assim, um build antigo concluído depois ou reexecutado pula publicação. Se `main` avançar durante um deploy já iniciado, a exclusividade continua até ele terminar; a publicação nova precisa aguardar e não pode ser substituída ao final pela antiga.

### Diagnóstico, reprodução e reexecução

Consulte primeiro **Resolve verified Kof** para erros de API, seleção, tag e integridade; depois o check do alvo para instalação/testes, **Build complete Pages site** para build e artefato, e **Publish current main** para Pages/freshness/deploy. Falhas anteriores ao deploy preservam o site existente. Falhas de deploy permanecem visíveis; não são registradas como publicação bem-sucedida.

Para reproduzir exatamente uma distribuição selecionada, baixe o artefato `kof-...` indicado pelo job produtor, extraia seu conteúdo para um diretório e use o SHA do manifesto:

```bash
bundle=/caminho/para/bundle
sha=$(jq -r .sifuture_sha "$bundle/manifest.json")
scratch=$(mktemp -d)
installation=$(bash scripts/kof_ci.sh install "$bundle" "$scratch/installation" "$sha")
export KOF=$(jq -r .kof <<< "$installation")
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 scripts/kof_project.py build --output "$scratch/site"
```

Execute esses comandos num checkout desse mesmo SHA. Alternativamente, passe `--kof "$KOF"` aos comandos existentes. Para fazer uma nova resolução local, use `bash scripts/kof_ci.sh resolve "$scratch/bundle" "$(git rev-parse HEAD)"`; o destino ainda não pode existir. A resolução local também exige acesso autenticado de leitura ao GitHub.

**Re-run failed jobs** reutiliza os outputs dos produtores bem-sucedidos, inclusive o nome do bundle ou pacote Pages original; o consumidor não calcula o nome usando sua nova tentativa. **Re-run all jobs** executa uma nova resolução e repete os testes e build com ela. Se os artefatos expiraram, reexecute todos os jobs; não substitua manualmente o compilador. Reexecutar um deploy antigo não restaura um site antigo: a atualização de `main` continua sendo obrigatória.

As verificações locais de infraestrutura ficam em [`tests/ci-contract.sh`](tests/ci-contract.sh), com fixtures JSON e executáveis Bash para as APIs e downloads. Execute `bash tests/ci-contract.sh` com `yq` v4 disponível. Elas não fazem parte do workflow. O [registro de validação](.agent/validation/kof-ci-and-pages.md) distingue simulações locais, execução real do compilador e pendências de produção.

O aceite de produção exige uma execução publicada e verificação manual de carregamento, módulos/runtimes, sprites, início da partida, movimento, pausa/continuação e retorno ao menu. Registre o navegador e o SHA publicado. Enquanto essas evidências não estiverem no registro, a página publicada não está validada.
