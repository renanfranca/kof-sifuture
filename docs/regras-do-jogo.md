# Regras do jogo

[Voltar à apresentação do projeto](../README.md) ·
[Como jogar](jogar.md) ·
[Desenvolvimento e verificação](desenvolvimento.md)

Este guia explica o comportamento entregue e as diferenças aprovadas em
relação ao original. A [especificação do port](../.agent/specifications/port-sifuture-to-kof.md)
conserva os requisitos da v1 e os ciclos ainda pendentes.

## Mundo lógico e passo

O **mundo lógico** é o espaço de coordenadas em que o jogo calcula posições e
colisões: 176 × 220 unidades. Um **passo** é uma atualização da simulação,
programada a cada 30 ms. O tamanho da janela não redefine esse mundo.
A nave avança cinco unidades por passo em cada eixo ativo, com limite
superior `y = 30`; os limites direito e inferior consideram seu tamanho.

Em [Rules.kf](../src/main/kof/sifuture/game/Rules.kf#L4):

```kof
static final Int STEP_MS = 30
static final Int WORLD_WIDTH = 176
static final Int WORLD_HEIGHT = 220
```

Esses valores separam tempo e espaço: mover uma vez aplica a velocidade de
cinco unidades; esperar um segundo não é uma instrução direta de movimento.
O limite superior e a velocidade são nomeados por `HEADER_HEIGHT` e
`SHIP_SPEED` no mesmo arquivo. O relógio chama a atualização e depois o desenho, conforme o
[guia de desenvolvimento](desenvolvimento.md#modelo-desenho-e-controles).
Redesenhar apenas consulta o estado e não acelera animações. Pausar congela
os contadores, incluindo fundo, itens, tiros e efeitos.

## Fase

A **fase** é o percurso da tentativa, representado por um marcador que vai
da posição 5 à 176. O primeiro encontro prolongado entra em 88 e avança o
marcador para 89; o último entra em 146 e avança o marcador para 147.
Combate e explosão desses
inimigos suspendem o avanço da trilha. Fora deles, a miniatura avança uma
posição a cada dez passos. A duração total depende do combate.

A posição é derivada em [Game.stagePosition](../src/main/kof/sifuture/game/Game.kf#L324):

```kof
var position = 5 + stageSteps / 10
if (position > Rules.WORLD_WIDTH) { return Rules.WORLD_WIDTH }
return position
```

`steps` conta atualizações da partida; `stageSteps` conta o avanço da trilha e
o incremento histórico da entrada. Durante combate e explosão, apenas o
primeiro continua. Calcular a posição evita guardar outra cópia que teria de
ser sincronizada. O [training de estado duplicado](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/anti-patterns/duplicate-state.md#L73)
orienta:

> If a value can be derived from another, derive it (method or function).

Após o término do último encontro, faltam 290 passos para o encerramento. A pausa
congela todos esses relógios.

## Pontuação e vidas

A **pontuação**, chamada `score` no código, acumula os prêmios da tentativa.
**Vidas** são as oportunidades restantes: a nave começa com três, e uma vida
é retirada ao terminar sua explosão. O estado **normal** da nave permite
colisões; durante o reinício ela pisca e fica invulnerável.

Uma colisão da nave com obstáculos concede cinco pontos uma única vez no passo,
mesmo quando vários estão sobrepostos. Cada obstáculo sobreposto inicia sua
animação. A explosão da nave dura dez quadros de três passos; o reinício tem
15 alternâncias de três passos.

A ordem da atualização considera o estado antes e depois de avançar a nave:
o estado anterior decide a tentativa de disparo; o estado depois decide as
colisões. No 45º passo de reinício a nave já pode colidir, mas só volta a
tentar o tiro normal no passo seguinte. Veja [Game.step](../src/main/kof/sifuture/game/Game.kf#L233):

```kof
var normalBefore = ship.phase == ShipPhase.Normal
var livesBefore = ship.lives
ship.advance()
if (ship.lives < livesBefore) { weapons.loseOnDeath() }
```

Mais adiante, na [mesma atualização](../src/main/kof/sifuture/game/Game.kf#L244):

```kof
if (normalBefore) { weapons.attemptFire(ship) }
```

`normalBefore` conserva a condição que valia no início do passo. A transição
para normal dentro de `ship.advance()` não altera retroativamente essa condição.

## Coleta e evolução

**Coleta** é o contato de uma nave normal com um item disponível. Há sempre
um coração de **evolução**, que melhora o armamento, e um de vida, que
acrescenta uma vida. O de evolução percorre os cinco quadros `iten`; o de vida
pulsa pelos onze quadros `life`, avançando e voltando. Cada coleta concede dez
pontos uma única vez, mostra três quadros de efeito e depois relança o item.
O piscar inicial e a explosão não permitem coleta. Vidas podem ultrapassar três.

| Coletas de evolução | Armamento |
| --- | --- |
| Nenhuma | Laser básico, um ativo por vez. |
| Primeira | Laser animado; um lançamento por tentativa e até três em circulação. |
| Segunda | Acrescenta o blaster no gatilho de seis ciclos do laser. |
| Terceira | Mantém o laser e aumenta a frequência do blaster. |
| Seguintes | Guardam cargas de especial, mantendo a terceira evolução. |

A regra está em [Game.kf](../src/main/kof/sifuture/game/Game.kf#L248):

```kof
if (item.collect(ship)) {
    score = score + 10
    if (item.kind == ItemKind.Life) { ship.lives = ship.lives + 1 }
    else { weapons.evolve() }
}
```

`collect` retorna verdadeiro somente na primeira coleta. Assim, o prêmio e o
benefício são concedidos juntos uma vez. `ship.lives + 1` não limita a vida a
três; os percursos registrados observaram a passagem de 3 para 4 em JVM, JS
e Chrome, conforme [background-items-weapons.md](../.agent/validation/background-items-weapons.md).

Essa escrita altera um campo de uma classe mutável. O [training de classes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/language/classes.md#L11)
orienta:

> For **mutable state**, use fields + `constructor(...)`

O [Learn Kof, Classes and Objects](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/07-classes-and-objects.md#L65)
ensina:

> To **mutate**, use explicit public fields:

Aqui, `ship.lives` é o dado que muda. O guia de desenvolvimento explica como
as [classes do modelo](desenvolvimento.md#classes-e-estados-em-kof) expressam
essa intenção sem duplicar estado.

## Armas e perda de evolução

O laser tenta disparar a cada 13 passos normais. O blaster suporta dois
impactos; cada um dos três feixes do especial suporta dez. Na segunda
evolução, o blaster usa o gatilho histórico de seis tentativas de laser;
na terceira, sua frequência aumenta. `Weapons` concentra nível, cargas,
cadência e projéteis.

Na morte, perde-se uma carga guardada ou, sem carga, um nível de tiro, até o
básico. Em [Weapons.loseOnDeath](../src/main/kof/sifuture/game/Weapons.kf#L26):

```kof
loseOnDeath() {
    if (charges > 0) { charges = charges - 1 }
    else if (level > 0) { level = level - 1 }
}
```

Os ramos são exclusivos: ter carga preserva o nível naquele evento. Os
projéteis já lançados continuam seus movimentos e efeitos. Com zero vidas,
a nave deixa de criar disparos durante o encerramento; lasers, blaster e especial
existentes terminam normalmente. Concluir a fase com vidas mantém os disparos
visuais. O [guia de jogo](jogar.md#especial) concentra os comandos e a
disponibilidade do especial.

## Meteoros

Há seis meteoros horizontais, com índices preservados, e dois verticais que
entram quando a posição da fase ultrapassa 30. Os verticais descem uma unidade
por passo e mostram três quadros de impacto, um passo por quadro. O par
relança quando ambos ficam inativos e ambos os chefes estão inativos. Os que
já foram lançados terminam o percurso durante o combate.

As colisões conservam a ordem nave → laser → blaster → especial, com prêmio
único por meteoro. O impacto de laser mostra `laser03.png` por um passo;
meteoros horizontais atingidos continuam avançando uma unidade por passo
durante três quadros de dois passos. Consulte a ordem em
[Game.step](../src/main/kof/sifuture/game/Game.kf#L285) e os percursos
[browser_meteor.py](../tests/browser_meteor.py) e
[browser_stage.py](../tests/browser_stage.py).

Os verticais reiniciam entre −153 e 0 na criação ou após impacto; depois de
sair pelo fundo, usam a faixa histórica de −171 até 0, mantendo a espera pelo
par. As regressões estão em [ship-meteor-reset.md](../.agent/validation/ship-meteor-reset.md).

## Subchefe

O **subchefe** é o inimigo do primeiro encontro prolongado. Tem resistência 30, deslocamento de uma unidade por eixo e três
tiros próprios, com tentativa a cada 12 passos normais. Laser retira uma
unidade; blaster aplica sua resistência restante. O especial conserva os
marcadores históricos de seis passos, incluindo reaplicação quando outro
feixe inicia contato. Contato corporal explode uma nave normal; durante o
reinício invulnerável, não altera nenhuma das duas entidades, exceção explícita
ao original.

`lifeTime` é um contador de duração usado para escolher o prêmio; no subchefe
avança a cada 36 passos normais e não representa segundos. O golpe fatal dá
600, 300 ou 150 pontos para `lifeTime` ≤30, ≤60 ou >60. Os dez quadros de
explosão duram três passos cada. Os itens recorrentes não são duplicados nem
reposicionados pelo prêmio.

[Subchief.reward](../src/main/kof/sifuture/game/Subchief.kf#L62) expressa as faixas:

```kof
reward(): Int {
    if (lifeTime <= 30) { return 600 }
    if (lifeTime <= 60) { return 300 }
    return 150
}
```

O primeiro limite que aceita o contador determina o prêmio. Portanto, 30 dá
600 e 31 passa à faixa de 300. [browser_subchief.py](../tests/browser_subchief.py)
verifica encontro, tiros, especial, explosão, pausa, retomada e nova partida
com modelo, desenho e controles reais em 320/1200 pixels.

## Boss final

O **boss final** é o chefe do último encontro. Tem resistência 100 e cinco níveis de ataques, com intervalos normais
de 13/31/31/24/24 passos. Contatos não fatais de armas evoluem o ataque abaixo
de 80/70/45/20; os limites exatos não evoluem. Contato corporal não evolui o
armamento e exige o estado normal do boss. O especial inimigo prepara seis
quadros de três passos e só se move e colide no quadro 6. Fúria usa `bos1.png`;
frenesi alterna `bos.png`, `bos1.png` e `bos2.png` a cada quatro passos.

O prêmio é 1650/1100/550/275 para `lifeTime` ≤30/≤60/≤120/>120. O golpe fatal
preserva o movimento, interrompe disparos e o incremento desse relógio e
inicia a explosão: quadro 0 por um passo, demais por três, término no passo 28.
Meteoros absorvidos não causam dano nem pontos. Reinício invulnerável não
causa contato corporal, exceção aprovada ao original.

[Boss.reward](../src/main/kof/sifuture/game/Boss.kf#L72) define esses prêmios:

```kof
reward(): Int {
    if (lifeTime <= 30) { return 1650 }
    if (lifeTime <= 60) { return 1100 }
    if (lifeTime <= 120) { return 550 }
    return 275
}
```

Os limites escolhem a recompensa uma vez no golpe fatal;
[browser_boss.py](../tests/browser_boss.py) verifica entrada, fases, tiros,
contatos, indicadores, explosão, pausa, redesenhos, encerramento e repetição com
a mesma semente em 320/1200 pixels. Os quatorze assets adicionados nesse ciclo
são cópias byte a byte dos históricos, conforme o
[aceite do boss](../.agent/validation/stage-hud-result.md).

## HUD

**HUD** é o conjunto de indicadores sobre a cena. Usa os sprites históricos
sem transformação: trilha, miniatura conforme uma, duas ou três vidas ou mais,
pontuação à direita, contador de vidas abaixo e ícone de especial em `(50, 21)`.
Os indicadores são desenhados depois das entidades para permanecerem visíveis
sobre os feixes. O mundo continua 176 × 220 e a nave conserva o limite `y = 30`.
O [renderizador](../src/main/kof/sifuture/GameView.kf) consulta o modelo;
o [aceite de fase e resultado](../.agent/validation/stage-hud-result.md)
registra as comparações de sprites.

## Resultado

O **resultado** encerra a tentativa quando a fase termina ou a última vida
é perdida. A pontuação definitiva é preservada; a contagem exibida começa
em zero. Cada passo acrescenta cinco pontos, limitado ao total exato.
A avaliação aparece apenas ao terminar:

| Pontuação | Índice da avaliação |
| --- | --- |
| Menor que 1500 | 0 |
| 1500 a 2199 | 1 |
| 2200 a 3299 | 2 |
| 3300 ou mais | 3 |

Em [Game.resultIndex](../src/main/kof/sifuture/game/Game.kf#L331):

```kof
if (score < Rules.RESULT_GOOD) { return 0 }
if (score < Rules.RESULT_GREAT) { return 1 }
if (score < Rules.RESULT_BEST) { return 2 }
return 3
```

Como os limites são estritos, exatamente 1500 pertence à segunda faixa e
exatamente 2200 à terceira. Isso corrige os casos históricos sem mensagem
nessas fronteiras. Pontuação zero já começa com a contagem concluída.
Os [dois comandos do resultado](jogar.md#começar-uma-partida) permitem concluir
a contagem e depois retornar ao menu, sem confirmação dupla por Enter mantido.

Durante o resultado, fundo, meteoros, itens, chefes, tiros automáticos visuais
e efeitos continuam. Colisões, coleta e comandos da nave ficam encerrados;
vidas, nível, cargas e posição da fase permanecem estáveis. A explosão
pendente termina sem nova perda de vida e fica oculta, sem tentar desenhar
o quadro de índice 10. Pontuação e avaliação ficam centralizadas sobre a cena.

## Diferenças aprovadas e correções históricas

Além dos controles modernos e das fronteiras de pontuação, a
[especificação](../.agent/specifications/port-sifuture-to-kof.md#historical-gameplay)
aprova o sprite `Middle2.png` somente enquanto a direção horizontal efetiva
é direita. Soltar restaura `Middle.png` no próximo passo, inclusive com
movimento vertical. Pausa, resultado e perda de foco limpam comandos e
restauram o quadro normal. O histórico conservava o quadro de propulsão
depois da soltura.

As exceções de contato corporal durante reinício invulnerável estão nos
ciclos aprovados de subchefe e boss. Os controles com arrasto que conserva
a seta inicial são o contrato atual; não representam toda a v1 futura.

Os três grupos do especial usam `e0`–`e2`, `e3`–`e5` e `e6`–`e8`,
respectivamente laranja, azul claro e azul escuro. O histórico
[AirShipEspecialShoot.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/AirShipEspecialShoot.java)
tentava carregar `especial0`–`especial8` e usava índices 3–8 em vetores de
três posições para as cores azuis. A cena Kof usa os arquivos existentes
agrupados por cor, corrigindo o carregamento sem substituir os desenhos.
[NOTICE](../NOTICE) continua aplicável; a
[documentação das fontes](../fonts/README.md) concentra a tipografia atual.

## Fontes e limites das provas

Os trechos Kof acima são excertos do código existente. Sua execução pertence
às revisões registradas, não a exemplos novos apresentados como executados.
[GameJourney.kf](../src/test/kof/sifuture/game/GameJourney.kf) exercita as regras
em JVM e JS. Os scripts de navegador usam os mesmos componentes reais e
posições determinísticas para observar os pixels, o tempo e as interações.
O [guia de desenvolvimento](desenvolvimento.md#o-que-as-verificações-demonstram)
relaciona comandos, revisões e ambientes.

As regras históricas foram consultadas em
[AirShip.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/AirShip.java),
[AirShipAllShoots.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/AirShipAllShoots.java),
[Meteor.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/Meteor.java),
[MeteorArray.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/MeteorArray.java)
e [GameCanvas.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/GameCanvas.java).
O [vídeo histórico](https://youtu.be/1xMKYEy7Jqw?si=oF48Zq7EeNTLTb3J) governa
a comparação visual ainda pendente. Testes determinísticos não a substituem,
nem demonstram execução gráfica em JVM/Native ou aceite em Android físico.
