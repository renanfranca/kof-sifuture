# Quatro setas independentes — Chrome do Android

## Escopo e ambiente

Plano aprovado de 04/10/2026, incorporado ao EXECPLAN; branch `android-multitouch-controls`, base `origin/main` `567f6d032523fe02a0c45eebdbf345f51d70b600`. Os deltas documentais anteriores foram preservados, sem alteração de conteúdo, em `b99cc62`.

Worker único `primary`, chat `01a108c9-623d-7f10-a9f5-a49eba70b808`, `gpt-6.1-sol`/`medium`, título `sifuture-controls-primary`. Implementação, validação e revisão estrutural compartilham contexto: não são independentes. Kof instalado do PATH `0.5.0-beta`; checkout consultado de Kof `317d9f6b1c3e27032cc955a05f859f6c627d9338` é referência de fontes, sem atribuir seu SHA ao pacote instalado. Linux, Python 3, Playwright/Pillow, Chrome `139.0.7258.154`, viewport 320/1200 para layout; touch via CDP, sem Android físico.

## Conferência das expectativas

Conferência semântica realizada separadamente da leitura das assertions. O plano nesta conversa define quatro botões, eixos combinados, última pressão entre opostos, soltura seletiva, arrasto conservando o contato inicial e teclado sem retomada automática. A regra anterior de recusar uma segunda zona foi deliberadamente substituída; não é regressão a preservar. `Ship.direction()` e `Ship.advance()` já implementam prioridade por `lastX`/`lastY`; Ship e velocidade cinco permaneceram inalterados. Pausa, foco, Enter, `1`, imagem de propulsão e Especial conservam os contratos anteriores da especificação e das jornadas.

Kof: consultados training de classes, UI, CLI, duplicate-state e fake-idioms; referência de classes; Learn Kof 07/23/35; parser de Style, runtime JS de eventos/layout/widgets e testes UiStyleCssE2ETest. A declaração explícita de campos segue o modelo mutável; `padPressed()` deriva a atividade das quatro pressões. `held*` guarda memória física de teclado, `pad*` guarda botões, Ship guarda o movimento efetivo: essas responsabilidades são distintas. A UI usa somente widgets Kof e Style, sem editar saída gerada. A captura implícita é especificada em [W3C Pointer Events 3 §9.4](https://www.w3.org/TR/pointerevents3/#implicit-pointer-capture); sua realização foi demonstrada neste Chrome pelo arrasto e soltura no alvo inicial.

## Critérios e provas observadas durante implementação

Provas desta seção foram executadas sobre o delta de trabalho; o gate de revisão comprometida será registrado abaixo com seu SHA. Logs/capturas são evidência opcional em `.agent/tmp/sifuture-controls*`; o conteúdo essencial consta aqui.

| Critério | Comando / procedimento | Resultado observado |
|---|---|---|
| Diagonal | Suíte GameJourney, JVM/JS; `python3 tests/browser_controls.py` | (60,100) → (65,100) → (70,95) → (75,95) → estável. Matriz de quatro diagonais × duas ordens de pressão × duas de soltura: 16 jornadas, x/y e propulsão. |
| Opostos | Mesma suíte e percurso | Última pressão vence nos dois eixos e ordens; 8 jornadas Chrome. Soltar vencedor retoma o mantido; soltar perdedor conserva vencedor. Middle2 só para direita efetiva. |
| Duplicatas | GameJourney em JVM/JS | Repetir Right depois de Left não muda prioridade. Solturas duplicadas não mudam prioridade nem apagam teclado ao soltar botão não mantido. |
| Simultâneos | `simultaneous_direction_events` no percurso de controles | Eixos distintos combinam. Opostos usam último pointerdown realmente entregue; ordem observada é registrada, sem inferência de ordem física dos dedos. Solturas verificam label e pointerId. |
| Arrasto/cancelamento | `touch_pad_drag_release_and_cancel` no percurso de controles | Arrastar Right sobre Up mantém direita. Outro contato Down combina; soltar Right retém Down. Cancelamento total de dois contatos para ambos; nova pressão funciona. |
| Diagonal + Especial | `python3 tests/browser_weapons.py` | Três contatos em botões distintos; seis permutações de soltura. Cargas 2 → 1, sem repetição; posições x/y refletem somente setas mantidas. Cancelamento total conserva carga 1; novo Especial após os feixes terminaram consome 1 → 0. Alvo e identidade de cada soltura conferidos. |
| Pausa/teclado | GameJourney e percursos controles/armas | Pausa com Right/Up mantidos limpa ambos; continuar fica imóvel; só nova pressão move. Memória do teclado fica separada, sem assumir ao soltar último botão. Regressões de foco, click/Tab, Enter/1/Space continuam. |
| Layout | `cross_layout`, captura e medidas em Chrome 320/1200 | Quatro botões 56×56; cruz 168×168, gap 0, centro/cantos sem botão; Especial 72×64, gap 16, centro vertical; canvas acima; sem scroll horizontal. Capturas inspecionadas. Aplicação/fixtures com controles usam janela 296. |
| Conforto Android | Jogar no Chrome de aparelho real, inclusive subchefe | **PENDENTE**: não há dispositivo físico neste ambiente. Touch simulado não fecha este aceite. |

## Qualidade das observações e TDD

`ship_observation` procura pixels opacos do sprite em todos os x válidos e em y=30..200, compara pelo menos 90% das amostras e observa propulsão separadamente; não restringe y a 100. Posição é observada no canvas real no percurso de controles, com relógio determinístico e contextos novos. A fixture inicia (60,100), nave normal, meteoros em y30; limite de 40 passos mantém os cenários longe de colisões. Armas usa fixture real com preparação explícita de (60,100), y no status e cargas observáveis. TouchContacts registra pointerdown/up/cancel no botão real; release confere label e pointerId do contato inicial. O centro/cantos são conferidos também por hit testing. Cada contexto confere ausência de erros JavaScript.

RED por comportamento (JVM):

```text
FAIL independent pad arrows combine axes and release only their own direction: two held arrows must combine axes
1 failed of 80 tests
FAIL duplicate pad events preserve opposite priority and ignore unheld releases: repeated press must not steal opposite priority
1 failed of 81 tests
```

RED do layout (Chrome):

```text
AssertionError: {'x': 108, 'y': 285, 'width': 48, 'height': 48}
```

GREEN dirigido, mesmo delta em JVM/JS:

```text
0 failed of 85 tests
PASS four touch diagonals in both press/release orders: 16 journeys with x/y, propulsion and exact pointerup target/id
PASS last opposite touch wins in both axes and orders: 8 journeys with resumed/retained movement and propulsion
PASS diagonal + third-finger special: six release orders, exact pointerup targets/ids, one charge, total cancel and new press
```

Fontes de regressão existentes foram adaptadas só onde o contrato aprovado muda: oito zonas viraram quatro direções; teste que recusava segundo oposto agora exige última pressão. Asserções de teclado/foco conservam a sequência, ajustando a posição inicial da fixture de 40 para 60. Não foram adicionados comentários de código. A dificuldade, velocidade e combate não mudaram.

## Gates e entrega

Gates inicial/final sobre commits, revisão estrutural e CI ainda pendentes nesta versão do registro. Inventário confirmado: duas suítes Kof, seis percursos Chrome, unittest Python e contrato CI local; CI Resolve verified Kof/JVM/JS. Sonar, mutation testing e Habit não configurados, portanto excluídos, sem atribuir resultado passed. Android físico permanece pendente mesmo após todos os gates automáticos.
