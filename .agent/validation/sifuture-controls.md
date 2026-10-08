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

Gate inicial concluído no SHA `45b49487f242f7addd5243c800b7e9716c7474ad`, checkout limpo, 10/10 selecionados/executados, 0 bloqueados, duração 173,54 s. A revisão estrutural terminou sem refactor adicional. O gate final repetirá todos os dez comandos sobre o commit documental antes da criação do PR; seu SHA/resultado e os links de CI serão preservados no ledger e na descrição do PR. Inventário confirmado: duas suítes Kof, seis percursos Chrome, unittest Python e contrato CI local; CI Resolve verified Kof/JVM/JS. Sonar, mutation testing e Habit não configurados, portanto excluídos, sem atribuir resultado passed. Android físico permanece pendente mesmo após todos os gates automáticos.


### Comandos do gate inicial (todos exit 0)

| Comando | Resultado |
|---|---|
| `python3 scripts/kof_project.py test --target jvm` | 85 testes, 0 falhas |
| `python3 scripts/kof_project.py test --target js` | 85 testes, 0 falhas |
| `python3 tests/browser.py` | Percurso/contrato PASS |
| `python3 tests/browser_controls.py` | Percurso/contrato PASS |
| `python3 tests/browser_meteor.py` | Percurso/contrato PASS |
| `python3 tests/browser_weapons.py` | Percurso/contrato PASS |
| `python3 tests/browser_stage.py` | Percurso/contrato PASS |
| `python3 tests/browser_subchief.py` | Percurso/contrato PASS |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | 8 testes OK; erros de parser são previstos pelo teste de fonte inválida |
| `PATH=/tmp/kof-ci-tools:$PATH bash tests/ci-contract.sh` | Percurso/contrato PASS |

Trechos do executor e dos percursos:

```text
0 failed of 85 tests
Ran 8 tests in 13.703s
OK
PASS midpoint combat, three shots, invulnerability, real special controls, ten explosion sprites, resumed track, defeat and new game
PASS Chrome 139.0.7258.154 at 320 and 1200 pixels; pause and repaint preserve simulation
```

O [workflow configurado](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml) tem Resolve verified Kof e Kof tests (jvm/js) selecionados. Build/Publish Pages dependem de push em main, portanto não constituem aceite deste PR e nenhuma publicação é alegada. Links específicos de execução só existirão após o push/PR e serão associados à entrega.

### Revisão estrutural e limites

Revisão no mesmo contexto da implementação, protegida pelas suítes e pelo checkpoint no navegador. Classificação **No action** para os pontos revisados: a ordenação de pressões é o protocolo aprovado; deduplicação antecede efeitos e a limpeza inicial ocorre somente na primeira pressão. Pad, memória de teclado e entrada efetiva da nave têm lifecycles distintos; não há novo flag ativo derivado. Game continua fora da camada DOM; Direction elimina a conversão de zonas. Ship conserva prioridade e imagem, sem regra de combate transferida aos controles. Capturas de direção nas lambdas são fixas por botão; runtime/browser demonstram despacho real. Styles e geometria permanecem na montagem; os testes observam comportamento, pixels/eventos e dimensões, sem adicionar seams de produção apenas para testes. Os quatro ramos para cada dispositivo mantêm leitura e escrita locais; abstrair agora aumentaria escopo sem risco demonstrado. Sem defeito ou risco estrutural acionável encontrado no delta/contratos adjacentes; nenhuma revisão independente foi realizada.

Nenhuma falha persistente observada. As únicas falhas intencionais deste ciclo foram os REDs descritos e fixtures negativas de infraestrutura. As quatro diagonais e opostos foram comprovados por execução nos dois alvos e Chrome; compilação isolada não é usada como prova de runtime. Os JSON de eventos e capturas em `.agent/tmp/sifuture-controls/` são suporte opcional; o resumo de critérios permanece compreensível sem eles. O exclude local contém `/.agent/tmp/` exatamente uma vez.

Aceite de conforto e combate no Chrome de Android físico **continua pendente**. Não foram testados dedos múltiplos no mesmo botão, versão atual do Chrome Android, WebView/APK, navegador móvel de outro fornecedor, música ou chefe final. Essas ausências não são passes nem mudanças de escopo. A velocidade, dificuldade e regras de combate permanecem as anteriores.


### Gate final e primeira execução de CI

Gate final concluído sobre `e358df6444e90158c96efc9e8b1f96f73682c5ca`: 10/10 checks exit 0, 0 bloqueados, 183,89 s; JVM/JS 85/85, seis percursos Chrome, infraestrutura 8/8 e contrato CI. Todos os critérios automatizados continuam atendidos; Android físico continua pendente.

[PR #12](https://github.com/renanfranca/kof-sifuture/pull/12) aberto, sem merge. [Workflow 37237869943](https://github.com/renanfranca/kof-sifuture/actions/runs/37237869943) concluído com SUCCESS no head acima, testando a revisão de merge do evento conforme o workflow.

- [Publish current main](https://github.com/renanfranca/kof-sifuture/actions/runs/37237869943/job/111540997947): SKIPPED.
- [Build complete Pages site](https://github.com/renanfranca/kof-sifuture/actions/runs/37237869943/job/111540997294): SKIPPED.
- [Kof tests (jvm)](https://github.com/renanfranca/kof-sifuture/actions/runs/37237869943/job/111540917743): SUCCESS.
- [Kof tests (js)](https://github.com/renanfranca/kof-sifuture/actions/runs/37237869943/job/111540917670): SUCCESS.
- [Resolve verified Kof](https://github.com/renanfranca/kof-sifuture/actions/runs/37237869943/job/111540503588): SUCCESS.

As duas suítes CI registraram `0 failed of 85 tests`; Resolve verified Kof validou a distribuição oficial. Build/Publish Pages foram SKIPPED, portanto o PR não publicou o jogo. Este complemento incorpora links disponíveis após o primeiro push; os gates locais serão repetidos sobre o commit documental, com fonte de produção inalterada desde `45b49487f242f7addd5243c800b7e9716c7474ad`. O PR/ledger recebem os resultados finais posteriores sem substituir esta evidência histórica.

### Conferência do planejador após implementação — 04/10/2026

Revisão solicitada pelo usuário contra o plano aprovado nesta conversa, sobre `f106bb46e15c743529d95cb46f65c2a13af7f993`. Checkout inicialmente limpo. Expectativas conferidas separadamente das assertions: a decisão final usa última pressão entre opostos, substituindo a ideia inicial de cancelamento. Comparação com `b99cc62` confirmou que Ship, Rules, Subchief e Weapons não receberam alterações; velocidade e combate foram preservados. Não foi encontrada divergência de implementação com o plano. Esta conferência modifica somente este registro, sem alterar produção ou testes.

Reexecutados os oito comandos previstos pelo plano, todos com exit 0: `python3 scripts/kof_project.py test --target jvm` e `--target js` (85/85 em cada alvo), `python3 tests/browser.py`, `python3 tests/browser_controls.py`, `python3 tests/browser_meteor.py`, `python3 tests/browser_weapons.py`, `python3 tests/browser_stage.py` e `python3 tests/browser_subchief.py`. Os checks de infraestrutura não foram repetidos nesta revisão, pois não houve mudança nessa camada; os gates anteriores permanecem registrados acima. Ambiente: Kof `0.5.0-beta` do PATH, JVM embarcada Eclipse Adoptium `25.0.4.1`, Chrome `139.0.7258.154`, Linux, Playwright/Pillow. Logs desta conferência em `.agent/tmp/controls-plan-review-20261004T222231Z/`, como suporte opcional.

| Critério do plano | Evidência reobtida |
|---|---|
| Pressões independentes e diagonais | Teste com sequência `(60,100) → (65,100) → (70,95) → (75,95) → estável` aprovado em JVM/JS; 16 jornadas Chrome cobrem quatro diagonais e ambas as ordens de pressão/soltura, observando x/y e propulsão. |
| Última pressão entre opostos | Testes JVM/JS e oito jornadas Chrome nos dois eixos; soltura do vencedor retoma o outro, e soltura do perdedor conserva o vencedor. Duplicatas não roubam prioridade nem apagam movimento de teclado. |
| Eventos simultâneos | Quatro casos Chrome usam a ordem de pointerdown efetivamente observada, sem impor ordem física; solturas conferem botão e pointerId do contato iniciado. |
| Arrasto e cancelamento | Arrasto mantém seta inicial; soltura seletiva preserva outro eixo; cancelamento total permite nova pressão. Prova adicional no Chrome cancelou separadamente ↑ e → enquanto a outra seta permanecia mantida, inclusive verificando a soltura posterior duplicada. Essa prova adicional usa pointercancel sintético sobre o botão com outro touch CDP ativo; não demonstra a política de cancelamento de um aparelho físico. |
| Diagonal e Especial | Seis permutações de soltura dos três contatos, uma única carga consumida, cancelamento total e nova pressão aprovados; eventos/identidades e posição/cargas conferidos. |
| Pausa e teclado | Pausa com dois dedos limpa ambos os eixos; continuar e soltar os contatos antigos não reiniciam movimento. Nova pressão funciona. Regressões de foco, click/Tab, Enter, 1 e Espaço passaram. |
| Geometria e apresentação | Capturas 320/1200 inspecionadas; medições e hit testing confirmam quatro botões 56×56, cruz 168×168, centro/cantos vazios, Especial 72×64 com gap 16 e centro vertical, canvas acima e ausência de scroll horizontal. Aplicação e fixtures com controles usam largura 296. |
| Preservação do jogo | Percursos de menu, meteoros, armas, fase e subchefe aprovados; percurso completo do encontro nas duas larguras termina em 4515 passos, escore 350 e posição 176. |
| Conforto no Chrome do Android real | **PENDENTE**, inclusive combate com subchefe. Os testes desktop com touch simulado e a prova sintética não satisfazem este critério. |

Trechos reobtidos dos comandos de suítes e controles:

```text
0 failed of 85 tests
PASS four touch diagonals in both press/release orders: 16 journeys with x/y, propulsion and exact pointerup target/id
PASS last opposite touch wins in both axes and orders: 8 journeys with resumed/retained movement and propulsion
PASS captured drag retains its initial arrow, selective release preserves other axis, total cancel permits new press
```

Em `python3 tests/browser_weapons.py`:

```text
PASS diagonal + third-finger special: six release orders, exact pointerup targets/ids, one charge, total cancel and new press
```

Confirmado por `gh pr view --json number,url,state,headRefOid,baseRefName,statusCheckRollup` e `gh run view 37238676684 --json conclusion,headSha,event,url,jobs`: [PR #12](https://github.com/renanfranca/kof-sifuture/pull/12) aberto no SHA revisado; [CI 37238676684](https://github.com/renanfranca/kof-sifuture/actions/runs/37238676684) SUCCESS no mesmo head. Resolve verified Kof e testes JVM/JS SUCCESS; logs das duas suítes contêm `0 failed of 85 tests`. Build/Publish Pages SKIPPED. Esta conferência não faz merge nem publica os controles. O exclude local contém `/.agent/tmp/` exatamente uma vez e não há arquivos dessa pasta rastreados pelo Git.


### Merge e publicação acompanhados — 04/10/2026

Após autorização explícita do usuário, o [PR #12](https://github.com/renanfranca/kof-sifuture/pull/12) foi integrado por merge em `main`, no SHA `b9ab8dc0116dfc153766073d62aa008b477ae92d`. O comando `gh pr merge 12 --merge --match-head-commit f106bb46e15c743529d95cb46f65c2a13af7f993` vinculou a integração ao head previamente validado. A conferência pendente do planejador acima foi preservada, sem commit adicional.

A [execução de publicação 37241163525](https://github.com/renanfranca/kof-sifuture/actions/runs/37241163525), acionada pelo push de `main`, concluiu SUCCESS sobre esse SHA. Acompanhamento: `gh run watch 37241163525 --interval 20 --exit-status`; estado e logs: `gh run view 37241163525 --json status,conclusion,headSha,event,url,jobs` e `gh run view 37241163525 --log`.

- [Resolve verified Kof](https://github.com/renanfranca/kof-sifuture/actions/runs/37241163525/job/111550004256): SUCCESS.
- [Kof tests (jvm)](https://github.com/renanfranca/kof-sifuture/actions/runs/37241163525/job/111550440483): SUCCESS.
- [Kof tests (js)](https://github.com/renanfranca/kof-sifuture/actions/runs/37241163525/job/111550440548): SUCCESS.
- [Build complete Pages site](https://github.com/renanfranca/kof-sifuture/actions/runs/37241163525/job/111550596230): SUCCESS.
- [Publish current main](https://github.com/renanfranca/kof-sifuture/actions/runs/37241163525/job/111550670039): SUCCESS.

Os logs das duas suítes registraram `0 failed of 85 tests`. O artefato exato foi baixado com `gh run download 37241163525 --name pages-37241163525-1 --dir .agent/tmp/sifuture-controls-pages`. O procedimento local `python3 .agent/tmp/sifuture-controls-pages/check_published.py` comparou SHA-256 de todos os arquivos do artefato com as respostas HTTP 200 do [site publicado](https://renanfranca.github.io/kof-sifuture/), usando o SHA do merge na consulta e desabilitando cache na requisição. Resultado: 95/95 arquivos idênticos.

No Chrome `139.0.7258.154`, o mesmo procedimento abriu o site real em 320 e 1200 px, iniciou Novo Jogo e comprovou por pixels da nave: teclado `(0,100) → (10,100)`; direita `(15,100)`, adição de cima `(20,95)`, soltura de cima `(25,95)` e soltura de direita estável; direita `(30,95)`, adição de esquerda `(25,95)`, soltura de esquerda retomando direita `(30,95)` e soltura final estável. As solturas também conferiram alvo e pointerId. Medições confirmaram quatro setas 56×56 em cruz, Especial 72×64 com gap 16 e centro vertical, canvas acima, ausência de diagonais dedicadas e de rolagem horizontal. Pausa congelou o canvas e continuar retomou o jogo. Nenhum erro JavaScript ou resposta HTTP de erro foi observado.

```text
PASS all live site files match the exact deployed Pages artifact: 95 files
PASS Chrome 139.0.7258.154 live Pages at 320/1200: start, keyboard, four-arrow layout, multitouch diagonal/opposites, pause/resume, no JS or HTTP errors
```

Logs, script, inventário SHA-256, eventos de touch e capturas estão em `.agent/tmp/sifuture-controls-pages/`, apenas como suporte local opcional. Esta prova sobre o site publicado continua usando touch simulado; conforto e combate com subchefe no Android físico permanecem **PENDENTES**.

A ancestralidade da branch foi conferida com `git merge-base --is-ancestor android-multitouch-controls main`. Depois da verificação do Pages, `git push origin --delete android-multitouch-controls` e `git branch -d android-multitouch-controls` removeram somente a branch integrada, remota e local. O checkout foi restabelecido em `main`; `HEAD` e `origin/main` coincidem no SHA do merge. Este registro mantém sua alteração pendente anterior e o complemento de publicação, sem novo commit.


## Alinhamento com o canvas e Especial — 06/10/2026

### Escopo, revisão testada e ambiente

Plano aprovado nesta conversa, incorporado à especificação e ao EXECPLAN. Este ciclo substitui explicitamente a posição anterior de Especial ao lado do direcional; todas as seções anteriores permanecem evidências históricas das revisões que testaram.

Código e provas testados no SHA **`fced14f80d3590736b7a586a2a14871f8a495e1d`**, branch `controls-alignment`, base fixa `42d76fe443edf0dbbb3857cea47824fce7ad59e4`, checkout separado. Worker `primary`, chat `01a11249-dd7e-7530-b57c-32308372ff83`, `gpt-6.1-sol`/`medium`, título `controls-alignment-primary`. Implementação, validação e revisão compartilham contexto; nenhuma revisão independente é alegada.

Chrome **139.0.7258.154**, Linux, Python 3, Playwright/Pillow; viewports 320/1200 e touch via CDP. Kof instalado do PATH `0.5.0-beta`, Eclipse Adoptium `25.0.4.1`, JAR SHA-256 `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`. O pacote local não informa commit; não lhe atribuir o SHA `317d9f6b1c3e27032cc955a05f859f6c627d9338` do checkout Kof consultado. O `yq` preexistente em `/home/renanfranca/projects/kof-sifuture/.agent/tmp/tools` foi usado no contrato CI, sem instalação de ferramenta.

### Expectativas e conceito conferidos

A escolha aprovada centraliza ↑/↓ no canvas, não no conjunto inteiro. Especial usa somente a altura 220 do canvas, não os 396 pixels de canvas/cruz. Gap horizontal mede a borda do canvas, pois a cruz é oito pixels mais estreita. Velocidade continua cinco unidades por passo: de (60,100), Up mantido alcança (60,95), depois (60,90); soltar interrompe.

A composição em [GameControls.kf](../../src/main/kof/sifuture/GameControls.kf:63) expressa essa regra:

```kof
var gameColumn = Column(listOf(surface, pad))
gameColumn.setStyle(Style("width: 176; align-items: center; padding: 0"))
var specialColumn = Column(listOf(special))
specialColumn.setStyle(Style("width: 72; height: 220; justify-content: center; padding: 0"))
var movementControls = Row(listOf(gameColumn, specialColumn))
movementControls.setStyle(Style("width: 264; flex-wrap: nowrap; align-self: center; align-items: flex-start; gap: 16; padding: 0"))
```

`Column` empilha canvas/cruz; `Row` dispõe as duas colunas horizontalmente. A coluna de altura 220 define a referência vertical do Especial, e largura 264/nowrap impede quebra responsiva. [Learn Kof 35](/home/renanfranca/projects/kof/learn/35-kof-ui.md:162) apresenta `Column`/`Row`; [training UI](/home/renanfranca/projects/kof/training/idioms/ui.md:405) registra “the compiler owns the parse (D-UI-STYLE/UI007)”. O parser `KofStyleParser.java:65–88` admite os estilos usados, e o runtime `JsRuntimeUiWidgets.java:246,297` monta os filhos na ordem dada. Não há JavaScript/CSS de aplicação escrito à mão nem alteração de saída gerada. A execução real em KofJS/Chrome, não apenas a compilação, provou a geometria e entrada.

### Resultado por critério no gate inicial

| Critério | Procedimento/assertions | Observação em 320/1200 |
|---|---|---|
| Alinhamento | `cross_layout`, bounding boxes independentes, centros de ↑ e ↓ comparados ao canvas com tolerância ≤1 px | Diferença **0 px** nas duas larguras. Canvas 176×220; setas 56×56. |
| Toque intuitivo | `touch_on_canvas_axis`, x calculado só do canvas, hit target ↑, CDP, pixels da nave e identidade de soltura | (60,100)→(60,95) em um passo; mantido→(60,90); após soltar, dois passos estáveis. |
| Especial | `layout_and_indicator`, gap/centro contra canvas; bounding box completo desde indisponível até habilitado/disparo/pausa e na retenção/soltura/reativação de tecla | 72×64; gap **16 px**; diferença de centros verticais **0 px**; posição inalterada. |
| Espaço | Dimensões/topologia da cruz, hit testing em centro/cantos, bounds de canvas/botões, largura total e scroll; capturas | Cruz 168×168 abaixo do canvas, vazios sem botão; conjunto 264; sem quebra, sobreposição, corte ou scroll horizontal. |
| Regressões | Matrizes existentes de 16 diagonais e 8 opostos, soltura/cancelamento/arrasto, ordem entregue, seis permutações de três contatos, teclado/pausa | Todos passaram; uma carga por Especial. Foco por Tab manteve `overlay, ↑, ←, →, ↓, Especial, Pausar`. |
| Conforto físico | Jogar no Chrome de Android real | **PENDENTE**; touch simulado não encerra esse aceite. |

Medidas observadas pela fixture de controles:

| Viewport | Canvas `(x,y,w,h)` | Centro x canvas/↑/↓ | Especial `(x,y,w,h)` | Centro y canvas/Especial |
|---|---|---|---|---|
| 320 | `(28,57,176,220)` | `116 / 116 / 116` | `(220,135,72,64)` | `167 / 167` |
| 1200 | `(32,63,176,220)` | `120 / 120 / 120` | `(224,141,72,64)` | `173 / 173` |

Inspecionadas capturas `cross-320/1200`, `application-320` e `layout-1200`: disposição correta na fixture e na aplicação real. Capturas/JSON opcionais em `.agent/tmp/sifuture-controls/` e `.agent/tmp/background-items-weapons/`; não são necessários para entender este resumo.

### Qualidade das assertions e TDD

Conferência da força das assertions realizada separadamente das expectativas acima, no mesmo contexto. O teste novo calcula o ponto de toque no canvas, não no centro do botão; verifica o alvo antes da entrada real, depois encontra a nave pelos pixels do sprite e verifica pointerId/alvo da soltura. As expectativas de posição são explícitas. Geometria lê elementos distintos e mantém dimensões exatas; todos os estados do Especial comparam o bounding box completo. Tab observa `document.activeElement`. As regressões existentes continuam sem enfraquecer seus resultados para acomodar o layout.

RED anterior à implementação, `python3 tests/browser_controls.py`:

```text
AssertionError: (320, (160.0, 313.0), '↑←→↓')
```

O ponto atingia o contêiner da cruz, não ↑. Na composição intermediária, o teste também detectou Especial quebrado para baixo: canvas `(72,57,176,220)`, Especial `(124,547,72,64)`. `Row` fixo de 264 sem quebra corrigiu essa geometria. A fixture de armas rola ao clicar em preparação; o teste mostra o canvas antes de iniciar qualquer gesto para que Especial acima da cruz permaneça visível. Não rola durante contatos, não altera IDs ou regras.

Excertos do gate no SHA testado:

```text
PASS touch on canvas axis at 320/1200: (60,100) -> (60,95), held -> (60,90), release stops
PASS 320/1200: up/down aligned with 176x220 canvas; empty 168x168 cross; 72x64 special centered on canvas, 16px gap, 264px total, no horizontal scroll
PASS 320/1200: special centered beside canvas, 72x64, 16px gap; position retained through availability, firing, held key, release and pause
0 failed of 103 tests
Ran 8 tests in 14.664s
OK
```

### Comandos, gate e revisão

Gate inicial: **11/11 selecionados/executados, exit 0, coleta completa, zero bloqueados**, 229,73 s, no SHA `fced14f80d3590736b7a586a2a14871f8a495e1d`.

| Comando | Resultado |
|---|---|
| `python3 scripts/kof_project.py test --target jvm` | 103/103 |
| `python3 scripts/kof_project.py test --target js` | 103/103 |
| `python3 tests/browser_controls.py` | PASS |
| `python3 tests/browser_weapons.py` | PASS |
| `python3 tests/browser.py` | PASS |
| `python3 tests/browser_meteor.py` | PASS |
| `python3 tests/browser_stage.py` | PASS |
| `python3 tests/browser_subchief.py` | PASS |
| `python3 tests/browser_boss.py` | PASS |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | 8/8 OK; diagnósticos da fonte inválida são previstos |
| `PATH="/home/renanfranca/projects/kof-sifuture/.agent/tmp/tools:$PATH" bash tests/ci-contract.sh` | PASS |

Revisão estrutural: **No action**, sem refactor adicional. Novos contêineres são locais à montagem; nenhum campo, evento, ID ou API foi alterado. Ordem de foco e propagação ao root continuam provadas pelo navegador. A geometria pertence à apresentação; regras de movimento/combate e disponibilidade permanecem nas mesmas fontes. Nenhum seam de produção criado só para testes. Styles de disponibilidade conservam dimensões e posição.

Este complemento documental será comprometido antes do gate final, que repete os mesmos onze comandos. Resultado/head final e links específicos de entrega serão associados ao ledger e ao PR após esse gate. O [workflow configurado](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml) seleciona Resolve verified Kof e Kof tests (jvm/js); sua execução ainda não existe neste momento. Build/Publish Pages são condicionais a push em main e ficam SKIPPED no PR. Sonar, Habit e mutation testing não configurados e excluídos; não há score de mutação ou pass dessas ferramentas.

Não há falha persistente dos critérios automatizados. Plano, ledger, inventário, configuração e logs permanecem em `.agent/tmp/`, excluído localmente exatamente uma vez. Conforto no Android físico permanece pendente, sem declarar aceite de APK/WebView ou v1 completa.


### Conferência do planejamento após implementação — 06/10/2026

Conferido o head `2d4e1e867aae2dd26963bc165eafcde78d3f6ab5` da branch `controls-alignment`, [PR #17](https://github.com/renanfranca/kof-sifuture/pull/17), contra o plano aprovado desta conversa. Nenhum desvio funcional identificado. A main local ainda contém o layout anterior; esta conferência foi executada no worktree da implementação. Código e testes coincidem com o primeiro commit funcional; o head acrescenta documentação. Revisão de expectativas e revisão da força das assertions foram realizadas separadamente.

Reexecutados os nove comandos previstos pelo plano, todos com exit 0, usando Kof do PATH `0.5.0-beta` e Chrome `139.0.7258.154` no Linux:

| Comandos | Resultado observado |
|---|---|
| `python3 scripts/kof_project.py test --target jvm` e `--target js` | 103 testes por alvo, zero falhas. |
| `python3 tests/browser_controls.py` | Toque no eixo do canvas, geometria 320/1200, diagonais, opostos, arrasto, cancelamento, foco, teclado e pausa passaram. |
| `python3 tests/browser_weapons.py` | Especial simultâneo, uma carga por pressão, bloqueios de teclado, foco por Tab e posição em todas as disponibilidades passaram. |
| `python3 tests/browser.py`, `python3 tests/browser_meteor.py`, `python3 tests/browser_stage.py`, `python3 tests/browser_subchief.py`, `python3 tests/browser_boss.py` | Cinco percursos de regressão passaram. |

A expectativa principal vem do pedido aprovado: ↑/↓ no eixo do canvas e Especial à direita, sem exigir que o canvas sozinho fique no centro da tela. A especificação do ciclo, `port-sifuture-to-kof.md:25`, registra os mesmos resultados. As provas observam elementos distintos, coordenadas de entrada e pixels da nave; não deduzem a posição do botão a partir do estilo de produção.

| Critério do plano | Prova inspecionada e resultado desta conferência |
|---|---|
| Alinhamento | `cross_layout` em `browser_controls.py:516`: centros x canvas/↑/↓ iguais a 116/116/116 em 320 e 120/120/120 em 1200; diferença 0 px. |
| Toque intuitivo | `touch_on_canvas_axis` em `browser_controls.py:387`: x vem do canvas, hit target é ↑, pressão real leva (60,100)→(60,95)→(60,90); após soltura, dois passos permanecem em (60,90). A soltura também verifica alvo e pointerId. |
| Especial | `layout_and_indicator` em `browser_weapons.py:448`: 72×64, gap 16 e diferença vertical 0 px; bounding box preservado ao habilitar, disparar, pausar, manter/soltar tecla e recuperar disponibilidade. |
| Espaço disponível | Cruz 168×168 com setas 56×56; canvas 176×220; largura conjunta 264; centro/cantos vazios, cruz abaixo do jogo, elementos dentro do viewport e ausência de scroll horizontal. Capturas 320/1200 revisadas. |
| Regressões e interfaces | Diff de produção restrito à montagem de contêineres; callbacks, IDs e interfaces preservados. As matrizes existentes e a sequência por Tab `overlay, ↑, ←, →, ↓, Especial, Pausar` passaram. |

Trechos efetivos dos comandos de controles e armas:

```text
PASS touch on canvas axis at 320/1200: (60,100) -> (60,95), held -> (60,90), release stops
PASS 320/1200: up/down aligned with 176x220 canvas; empty 168x168 cross; 72x64 special centered on canvas, 16px gap, 264px total, no horizontal scroll
PASS 320/1200: special centered beside canvas, 72x64, 16px gap; position retained through availability, firing, held key, release and pause
```

O novo teste distingue o defeito anterior: calcula x pelo canvas, em vez de localizar o centro da seta, e mede o movimento durante a pressão e depois da soltura. A fixture inicia a nave normal em (60,100), afastada dos meteoros; nenhuma colisão impede a consequência esperada. Inspecionadas as capturas recém-geradas `cross-320.png`/`cross-1200.png` e a captura existente da aplicação em 320, correspondente ao mesmo código funcional. A composição usa `Column`/`Row` e `Style`, conforme Learn Kof 35 e o training de UI já citados acima.

O gate final do executor foi também conferido em seu resumo local: 11/11 comandos, todos exit 0, coleta completa, no mesmo head. Os dois checks de infraestrutura não foram repetidos nesta revisão porque essa camada não mudou. Confirmado o [CI 37509126926](https://github.com/renanfranca/kof-sifuture/actions/runs/37509126926) no head exato: Resolve verified Kof, JVM e JS concluíram SUCCESS; Build/Publish Pages ficaram SKIPPED, conforme a condição de execução em main. Não há aceite do site publicado neste ciclo de revisão.

Logs e resultados desta conferência estão em `.agent/tmp/controls-plan-review-20261006T185501Z/`, como suporte opcional; o conteúdo essencial consta neste registro. A exclusão local `/.agent/tmp/` foi conferida exatamente uma vez. Permanecem pendentes conforto no Android físico e os requisitos gerais de v1; os cenários automatizados solicitados estão verificados. Esta conferência altera somente os registros, sem modificar código, criar commit ou integrar o PR.


### Especial vertical na altura inteira do jogo — 06/10/2026

Ciclo integrado testado no SHA `38fa85903db8b0c648d778a6557ebb99b0c0ed2b`, branch `controls-alignment`, sobre base imutável `48ddaa948a58543c9764710fbdb5e606ca178042`. Os aceites anteriores descrevem seus próprios SHAs e foram conservados. Este ciclo substitui Especial 72 × 64 e conjunto 264 por Especial 56 × 220 e conjunto 248, conforme a especificação atualizada. Nenhuma API, callback, ID ou regra de movimento/disparo mudou.

Ambiente: Linux, Kof do PATH `0.5.0-beta`, Chrome `139.0.7258.154`. O gate inicial executou os onze checks, todos com exit 0, coleta completa, sem bloqueios, em 235,55 s. JVM e JS tiveram 103 testes cada, zero falhas. Python executou oito testes, OK; os diagnósticos PARSE pertencem ao teste intencional de compilação inválida (`test_real_compile_failure_does_not_publish`).

Comandos executados:

```bash
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 tests/browser.py
python3 tests/browser_controls.py
python3 tests/browser_meteor.py
python3 tests/browser_weapons.py
python3 tests/browser_stage.py
python3 tests/browser_subchief.py
python3 tests/browser_boss.py
python3 -m unittest discover -s tests -p 'test_kof_project.py'
PATH="/home/renanfranca/projects/kof-sifuture/.agent/tmp/tools:$PATH" bash tests/ci-contract.sh
```

| Critério | Resultado integrado |
|---|---|
| Layout 320/1200 | Canvas 176 × 220; Especial 56 × 220, gap 16, diferenças de topo/base 0 px; conjunto 248, cruz abaixo do canvas, sem sobreposição, corte ou scroll horizontal. |
| Setas | ↑/↓ e canvas têm centro x 124 em 320 e 128 em 1200; diferença 0 px. Setas 56 × 56, cruz 168 × 168, centro/cantos vazios preservados. |
| Texto/acessibilidade | `writing_mode` observado `vertical-rl`, texto inteiro “Especial”, ID `game-special`; localização por papel de botão e nome exato “Especial” continua válida. Retângulo do texto 15 × 49,140625, contido no botão e com diferença de centros 0 px nos dois eixos. Capturas integradas revisadas nas duas larguras. |
| Área de toque | Seis partidas separadas, duas cargas iniciais: topo/meio/base em 320 e 1200 atingem `game-special`; `pointerdown`/`pointerup` preservam alvo e identidade; cada caso termina com uma carga. Manter/soltar não repete; sprite `e3.png` confirma o feixe ativo. |
| Disponibilidade | Retângulo do botão, orientação, texto e retângulo do texto idênticos sem carga, disponível, disparado, pausado, com tecla mantida, após soltura e ao recuperar disponibilidade. Exceção de foco/opacity 0.5 durante tecla mantida preservada. |
| Regressões | Toque no eixo do canvas (60,100)→(60,95)→(60,90), seguido de estabilidade na soltura. Diagonais, opostos, arrasto/cancelamento, solturas independentes, seis ordens de soltura de Especial simultâneo, teclado e pausa passaram. Ordem de Tab continua ↑, ←, →, ↓, Especial, Pausar após o overlay. |

Medidas efetivas `(x,y,w,h)`: em 320, canvas `(36,57,176,220)` e Especial `(228,57,56,220)`; em 1200, canvas `(40,63,176,220)` e Especial `(232,63,56,220)`. Toques em 320: `(256,65)`, `(256,167)`, `(256,269)`; em 1200: `(260,71)`, `(260,173)`, `(260,275)`. Cada caso observou cargas `2 → 1`.

Trechos efetivos de `python3 tests/browser_controls.py` e `python3 tests/browser_weapons.py` no gate inicial:

```text
PASS 320/1200: up/down aligned with 176x220 canvas; empty 168x168 cross; 56x220 vertical special aligned with canvas, 16px gap, 248px total, no horizontal scroll
PASS 320/1200: special centered beside canvas, 56x220 vertical text, 16px gap; position retained through availability, firing, held key, release and pause
PASS special touch at top/middle/bottom in 320/1200: actual game-special target, active beams, charges 2 -> 1, held/released without repeat
```

Auditoria das expectativas: dimensões, orientação, gap e pontos de toque vêm do plano aprovado, independentemente dos estilos de produção. Alinhamento das setas, foco, pausa, regras e duas cargas preparadas vêm dos contratos anteriores. A nova orientação afeta o texto, mantendo o retângulo inteiro como área de toque. A especificação marca explicitamente os requisitos 72 × 64/264 como históricos e superseded.

Auditoria das assertions: tamanho antigo falhou antes da alteração de produção nos dois percursos. Geometria mede canvas e botão distintos; toques são calculados a partir do canvas e constantes do contrato, não do centro do botão. `elementFromPoint` confirma o alvo antes de eventos CDP reais; as provas conferem consumo exato, não repetição, soltura e pixels do feixe. A palavra é observada por Range do DOM, com contenção e centro testados; snapshots de apresentação conferem os estados sem exigir opacidade constante. A nave encobriu parte do feixe na primeira tentativa de assertion de pixels; a preparação existente “Move ship down” foi usada após concluir o toque para retirar essa sobreposição, sem reduzir a tolerância do teste. Os percursos completos de controles e armas passaram após essa correção de observação.

Revisão estrutural com `refactor-design`: **No action**. Alteração de produção limitada a quatro literais `Style`; não acrescenta estado, política de domínio, acoplamento temporal ou interfaces. Os dois estilos são montados uma vez e selecionados pela disponibilidade existente; as provas observam comportamento pelo navegador. Extração adicional não oferece benefício proporcional. Implementação, validação e revisão compartilham este chat; não constituem revisão independente.

Kof consultado: `training/idioms/ui.md:405` — “the compiler owns the parse (D-UI-STYLE/UI007)”; Learn Kof 35:176 descreve validação do `Style` literal e inteiros em px. `KofStyleParser.java:73` inclui `writing-mode` entre as propriedades; a compilação e a execução JS integradas demonstram sua aplicação neste checkout, além da prova isolada anterior.

O complemento documental será comprometido antes do gate final, que repete os mesmos onze checks. Resultados do head final serão associados ao ledger e à descrição do [PR #17](https://github.com/renanfranca/kof-sifuture/pull/17). Links persistentes: [checks atuais do PR](https://github.com/renanfranca/kof-sifuture/pull/17/checks) e [workflow configurado](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml). Resolve verified Kof e Kof tests (jvm/js) são selecionados no CI; Build/Publish Pages só executam em push na main. Sonar, Habit e mutation testing não configurados e excluídos, sem alegar pass dessas ferramentas.

Evidências locais opcionais: `.agent/tmp/validation/20261006T193226-8moxx5m5/`, `.agent/tmp/special-vertical.*`, `.agent/tmp/sifuture-controls/`, `.agent/tmp/background-items-weapons/` e `.agent/tmp/special-key-release/`. Capturas `application-320.png`, `application-1200.png`, layouts e estados revisados; conteúdo essencial acima dispensa esses arquivos. Exclusão local `/.agent/tmp/` conferida exatamente uma vez. Conforto no celular físico permanece pendente até verificação real; este ciclo não encerra o aceite Android/v1.


## Controles e saída da pausa — ciclo de créditos e navegação, 06/10/2026

Gate inicial `50affe515aeeec0f6ee9776a4d774feb8c7cf469`: onze checks com exit0, JVM/JS112/112 e sete jornadas Chrome139.0.7258.154. Touch simulado em320/1200: setas navegam com seleção limitada, Controles/Voltar conserva seleção, e Menu principal com dois dedos mantidos limpa a tentativa. Novo Jogo começa nave(0,100) parada; soltar esses contatos não recupera movimento. Diagonais, opostos, arrasto capturado e especial continuam cobertos. Resultado do percurso:

```text
PASS pause with two held fingers clears both axes; Continue and Main Menu keep held contacts from moving the resumed or new ship
```

Comando: `python3 tests/browser_controls.py`, classes reais da fixture controls.kf. O teste `touch_pause_clears_diagonal` observa sprite/posição antes e depois da soltura na nova tentativa. Gate final e CI serão associados ao mesmo ciclo; [registro por critério, fontes, assertions e limites](stage-hud-result.md#créditos-controles-e-navegação-da-pausa--06102026). Android físico/conforto continuam pendentes. O arquivo mantém os ciclos anteriores como históricos.

Entrega do ciclo: [PR18](https://github.com/renanfranca/kof-sifuture/pull/18), head `b8ceb17123b16cd4ee3b29dc3a7c44677715a632`; gate local final11/11, incluindo browser_controls e abandono com contatos mantidos. [CI37558500360](https://github.com/renanfranca/kof-sifuture/actions/runs/37558500360) Resolve/JVM/JS success,112 testes por alvo. CI demonstra modelo; contatos/foco continuam evidência Chrome local. Detalhes, checksums, merge sintético e links individuais no registro stage-hud-result. Inclusão documental será validada novamente antes da entrega.


### Complemento de confirmação — 07/10/2026

O menu/pausa têm um único Confirmar abaixo da composição; os nomes acessíveis das opções ficam em Buttons transparentes sobre os rótulos do Canvas. Focar Confirmar preserva a seleção. Os callbacks de cada opção validam a tela de origem; durante uma tecla mantida, o foco antigo é conservado fora do viewport com pointer-events:none para receber a soltura sem ativar outra tela. O [registro da fase/HUD/resultado](stage-hud-result.md#complemento--confirmação-entrada-e-contato-07102026) preserva auditorias separadas de expectativa/prova, RED/GREEN, identidade e gates completos. `tests/browser.py::confirmation_journeys` cobre os cinco comandos por quatro modos; `retained_options` cobre Enter/Space mantidos, toque na área anterior e rearme em320/1200. Os percursos anteriores de direcional, especial e pausa continuam parte dos onze checks.
## Investigação: teclado sem clicar na área do jogo — 08/10/2026

Investigação solicitada pelo usuário, com `plan-behavioral-acceptance`: explicar por que as setas funcionam no menu sem clicar no receptor transparente e comprovar se a partida pode dispensar esse clique. Esta execução observa o comportamento atual e uma experiência isolada; não entrega uma alteração de produção.

### Revisões, ambiente e procedimento

Aplicação local testada: `02eb48e55102b5f0cafd85020b77f37da07060fa`. O [deployment 6937190874](https://github.com/renanfranca/kof-sifuture/actions/runs/37786185171/job/113342992632) associa o mesmo SHA ao [site público](https://renanfranca.github.io/kof-sifuture/) e tem estado `success`; o [workflow](https://github.com/renanfranca/kof-sifuture/actions/runs/37786185171) também terminou com sucesso. A API foi consultada nesta investigação. O navegador executou as mesmas observações no build local e no site público.

Chrome `139.0.7258.154`, Playwright, alvo JS, larguras 320/1200 px, altura 900 px, densidade 1. O relógio virtual avança os intervalos reais de 30 ms; os eventos de teclado são enviados pelo navegador. Cada cenário usa um contexto novo. Não se usa `.focus()` para preparar os percursos: o foco chega aos elementos por Tab/Shift+Tab. Um observador conta `pointerdown` e registra alvo de `keydown`/`keyup`; todos os percursos terminaram com zero pressões de ponteiro. Enter pode gerar o clique nativo de um botão, o que não representa um clique de mouse ou toque na área do jogo.

Compilador instalado: Kof `0.5.0-beta`, launcher `/home/renanfranca/.local/share/kof/kof-0.5.0-beta-linux-x86_64/bin/kof`; SHA-256 do JAR `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`. Checkout Kof consultado: `317d9f6b1c3e27032cc955a05f859f6c627d9338`. O JAR não informa o commit de origem em `dev/kof/version.properties`; não se atribui a ele o SHA do checkout consultado. Essa lacuna de proveniência não deve ser apresentada como resolvida.

Comandos concluídos com exit 0:

```bash
python3 .agent/tmp/keyboard-no-click/probe.py
python3 .agent/tmp/keyboard-no-click/probe.py --prototype-only
```

A primeira execução bem-sucedida obteve 28 observações; a segunda repetiu quatro observações do protótipo e acrescentou duas de perda de foco: 30 observações distintas, 34 contando repetições. O script agora inclui os limites de foco também na execução completa. Fontes de produção permaneceram sem alteração, confirmado por `git diff -- src`. Evidência local opcional: `.agent/tmp/keyboard-no-click/`, com script, logs, `results.json`, `summary.txt`, capturas, identidade do compilador e respostas das APIs. As conclusões essenciais estão transcritas abaixo.

### Por que menu e partida diferem

O [contrato atual](../specifications/port-sifuture-to-kof.md:34) limita o movimento ao receptor:

> Arrows move the ship only when they originate at the overlay.

O [training de eventos](../../../kof/training/idioms/ui.md:380) explica a origem:

> `target()` returns the **id** of the node that originated the event

O [Learn Kof 35](../../../kof/learn/35-kof-ui.md:5) delimita a prova visual:

> only the JS target draws

Em [GameControls.kf](../../src/main/kof/sifuture/GameControls.kf:150), o observador pertence à coluna que contém a área, o guia e o botão principal:

```kof
root = Column(listOf(movementControls, guide.root, action))
root.setStyle(rootStyle)
root.on("keydown", (e: Event) -> { this.keyChanged(e.key(), e.target(), true) })
root.on("keyup", (e: Event) -> { this.keyChanged(e.key(), e.target(), false) })
```

O evento nasce no elemento focado e chega ao ancestral pelo DOM. `e.target()` continua identificando o elemento de origem. No runtime consultado, `JsRuntimeUiComponents.java:103` chama `node.addEventListener(type, fn)`, e `JsRuntimeUiEvents.java:31` lê `raw.target.id`. `KofJsBrowserE2ETest.java:1083` verifica `t=campo-main` para a origem do evento. A [especificação W3C de keydown](https://www.w3.org/TR/uievents/#event-type-keydown) estabelece o elemento focado como alvo; sem um elemento focado, usa `body` ou a raiz do documento. Um evento originado no `body` não atravessa a coluna interna dos controles.

Em [GameControls.kf](../../src/main/kof/sifuture/GameControls.kf:319), o filtro decide quais origens podem mover ou navegar:

```kof
var movementAllowed = target == "game-keyboard" || optionAvailable(target) || (target == "game-action" && (game.screen == Screen.Menu || game.screen == Screen.Pause))
```

`game-action` é o mesmo botão que exibe Confirmar no menu e Pausar na partida. O último termo permite as setas nesse botão somente em Menu/Pause. Portanto, o menu pode funcionar porque Confirmar ou uma opção já tem foco; isso não demonstra ausência de foco. Na partida, com foco em Pausar, o último termo fica falso. O filtro pertence à aplicação, não é uma exigência do navegador ou uma regra geral da linguagem Kof.

### Resultados observados

| Contexto e ação real | Resultado no código atual, local e Pages, em 320/1200 px |
| --- | --- |
| Abertura nova, foco em BODY; Enter durante créditos; esperar os 477 passos; Baixo/Enter no menu | Enter não pula créditos; depois a seleção permanece em Novo Jogo, y=120, e a partida não inicia. |
| Tab até o receptor; Enter para pular créditos; Baixo/Enter abre Controles; Enter volta; Cima/Enter inicia; Direita por seis passos | Foco permanece em `game-keyboard`; a nave vai de `(0,100)` a `(30,100)`, sem clique. |
| Soltar Direita; seis passos; Cima por seis passos; soltar; pausar/continuar por Enter; seis passos | Soltar mantém x=30; Cima leva a y=70; pausa/retomada não reinicia movimento. |
| Tab até Pular créditos; Enter; Baixo com foco em Confirmar | Seleção passa de Novo Jogo, y=120, para Controles, y=139, sem clicar no receptor. |
| Cima/Enter inicia com foco ainda em `game-action`; Direita por seis passos | Nave permanece `(0,100)`. |
| Após soltar Direita, Tab até o receptor; nova Direita por seis passos | Nave vai a `(30,100)`, ainda sem clique. |

O deslocamento é comparado a coordenadas literais e conferido pelos pixels opacos de `Middle.png` no canvas real, reutilizando `sprite` de `tests/browser_stage.py`. A imagem inicial é observada antes da seta; seis passos mantêm um quadro visível durante a animação de reinício. O controle negativo usa a mesma nave, capaz de se mover, e a mesma duração. Assim, imobilidade não é confundida com um limite do mundo, explosão, pausa ou falta de atualização.

Trechos literais de `summary.txt`, obtidos de `results.json` pelo comando Python de sumarização, JS/Chrome, site público, 320 px:

```text
pages-320-menu-action-arrows: focus=game-action; action=Confirmar (Enter); selection_y=139; pointerdowns=0
pages-320-play-action-blocked: focus=game-action; action=Pausar; ship_x=0; ship_y=100; pointerdowns=0
pages-320-play-tab-recovery: focus=game-keyboard; action=Pausar; ship_x=30; ship_y=100; pointerdowns=0
```

Essas três observações demonstram a diferença entre telas e que Tab já elimina a necessidade de clicar. O percurso completo por teclado também passou. Nenhuma dessas observações demonstra captura automática de teclas desde BODY.

### Viabilidade experimental e limite encontrado

Uma cópia descartável das fontes, preparada por `prepared_sources()`, recebeu somente esta substituição no filtro: `(target == "game-action" && (game.screen == Screen.Menu || game.screen == Screen.Pause))` por `target == "game-action"`. Essa cópia foi compilada com `kof build ... --target js --output ...` e executada em Chrome. O arquivo experimental e o build ficam em `.agent/tmp/`; não substituem as fontes canônicas.

Com Tab até Pular créditos e dois Enter, a partida iniciou com foco em Pausar. Direita por seis passos levou x=0 a x=30; sua soltura conservou x=30. Isso demonstra viabilidade de continuar jogando com o foco já adquirido no botão principal, sem tocar a área e sem transferir o foco ao receptor.

O limite seguinte também foi verificado: mantendo Direita e usando Shift+Tab para sair de Pausar, a nave continuou até x=60. O `blur` desse botão não limpa movimento, enquanto o `blur` do receptor o limpa. Portanto, a alteração de uma linha não satisfaz o contrato de perda de foco.

```text
prototype-320-action-moving: focus=game-action; action=Pausar; ship_x=30; ship_y=100; pointerdowns=0
prototype-320-action-release: focus=game-action; action=Pausar; ship_x=30; ship_y=100; pointerdowns=0
prototype-320-blur-gap: focus=BUTTON; action=Pausar; ship_x=60; ship_y=100; pointerdowns=0
```

As três observações se repetiram em 1200 px. A marca PASS na sonda do último caso significa que a falha prevista foi reproduzida; não significa aceite do protótipo. A experiência não cobre o Especial com foco em Pausar, saída da árvore, soltura externa, mudanças de aba/janela ou todas as transições de tela. Navegar até Novo Jogo e entrar por uma opção, em vez de Confirmar, também requer prova própria, pois a opção fica oculta na partida e pode devolver o foco a BODY.

### Handoff e lacunas

O [plano existente](../../EXECPLAN.md) recebeu critérios separados de observações para uma eventual mudança. A investigação está concluída. O contrato atual continua sendo receptor por clique ou Tab; extensão para o botão principal e ativação automática desde a abertura são propostas distintas. A pergunta do usuário não foi convertida silenciosamente em autorização para captura global ou em escolha de API de foco que não foi demonstrada no Kof.

Não houve alteração de produção, commit, PR, merge ou publicação nesta investigação. Safari, Firefox, Android físico e captura de teclas com o navegador em segundo plano não foram testados. A suite completa não foi reexecutada: a comprovação usa os percursos focados acima, sem atribuir aos demais testes um resultado novo.
