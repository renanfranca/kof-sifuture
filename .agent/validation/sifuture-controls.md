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
