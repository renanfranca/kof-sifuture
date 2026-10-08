# Textos, seleção e guia de controles — 2026-10-07

## Escopo e execução

Plano aprovado: créditos e opções com texto Canvas uniforme, nave indicando a seleção, foco independente, guia curto com detalhes recolhidos, cabeçalho de 44 px e remoção da instrução fixa. Sprites, assets, HUD e mecânicas preservados. Checkout atual, branch `credits-pause-navigation`; base `main` em `2322d90f6d98e1cdd4a9d209efeb216c1182b8e4`. Execução neste chat, `gpt-6.1-sol` / `medium`, papéis e leases em sequência. Validação e revisão compartilham o contexto da implementação.

O [PR #18](https://github.com/renanfranca/kof-sifuture/pull/18) e seus [checks](https://github.com/renanfranca/kof-sifuture/pull/18/checks) são os pontos persistentes de entrega. O [workflow](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml) executará Resolve verified Kof e Kof tests(jvm/js). Build/publicação de Pages dependem de push em main e não são gates do PR.

## Aceite funcional

Durante implementação, os testes foram executados na árvore alterada baseada em `a09bd22821eac6efc9793c8e03e6d851c569ac29`. Esse SHA identifica a base local; não identifica sozinho o conteúdo ainda não comprometido. O executor guarda fingerprint dos arquivos e logs. Os gates completos inicial/final ainda estão pendentes neste checkpoint.

As falhas esperadas que precederam a implementação foram:

```text
assert page.evaluate("creditDraws.length") == 0
AssertionError
assert [t["label"] for t in texts] == ["Novo Jogo", "Controles"], texts
AssertionError
assert back_box["y"] + back_box["height"] <= window_box["y"] + window_box["height"]
AssertionError
```

Os casos especificam saídas observáveis do Canvas, aparência calculada, conteúdo acessível e moldura. Os testes não exigem a existência de helpers ou uma organização específica das fontes. A inspeção acrescentou a ausência de rolagem horizontal nos painéis internos, além do documento.

O percurso `python3 tests/browser.py`, executado no Chrome 139.0.7258.154 em 320/1200 px, passou após implementação. O checkpoint `python3 tests/browser_stage.py` também passou:

```text
PASS pause and lost canvas focus immediately restore Middle.png at both widths
PASS defeat projectiles finish without respawn, effects finish at 1/4/6 steps, and restart restores fire
PASS Chrome 139.0.7258.154 at 320 and 1200 pixels; repaint does not advance simulation
```

O percurso principal comprova os quadros 0/1/36/85/86/87/258/259/260 dos créditos, nave em entrada 0/1/11/12/13/35/36, textos portugueses, escala compartilhada, RGB(0,128,255), restauração do Canvas, seleção limitada e foco neutro de 1 px independente. O guia verifica conteúdo da tabela/lista, dimensões/tipografia, detalhes fechados/abertos/reinicializados, abertura/retorno por Enter/Espaço/clique/toque, repetição de teclas sem transição adicional e opções retidas sem ativação de outra tela.

A soltura deve ser observada nos controles. Tocar a antiga opção depois de abrir o guia compacto pode colocar foco no documento, pois agora há texto nesse ponto. Nesse cenário o teste devolve foco ao receptor antes da soltura, e continua verificando que a antiga opção não confirma outra tela. Não se promete entrada global fora da árvore de controles.

## Regra Kof e realização no alvo

O [training de UI](/home/renanfranca/projects/kof/training/idioms/ui.md:277) orienta:

> `measureText` returns a `Double` (width in px) for text layout.

Em [GameView.kf](/home/renanfranca/projects/kof-sifuture/src/main/kof/sifuture/GameView.kf:180), a mesma escala é passada para os dois blocos:

```kof
var scale = 0.75
if (width * scale > 130.0) { scale = 130.0 / width }
drawCreditBlock(firstLines, credits.x, credits.firstY, scale)
drawCreditBlock(secondLines, credits.x, credits.secondY, scale)
```

`width` é a maior medida entre todas as linhas. Assim, reduzir para 130 px preserva a proporção dos dois blocos; `save`/`restore` isolam a transformação e a cor. O [capítulo Learn Kof sobre UI](/home/renanfranca/projects/kof/learn/35-kof-ui.md:3) estabelece:

> only the JS target draws

Os testes JVM/JS do modelo e os testes de desenho no Chrome têm papéis distintos; compilação sozinha não prova aparência. O registro de Canvas em [KofUi.java](/home/renanfranca/projects/kof/kof-compiler/src/main/java/dev/kof/compiler/KofUi.java:503) oferece `fillText`, `measureText` e `transform`, sem setter de fonte nessa lista. Os menus usam a fonte sans-serif 10 px do contexto e transformação 1.2, com tamanho observado 12.000000476837158px no Chrome. Isso atende aproximadamente 12 px sem adicionar API ao compilador. Para recolher o bitmap usa-se seu `View` pai: Canvas não está na família `isDomWidget` do registro atual, que aceita `setStyle`.

## Aceite visual

A inspeção das capturas em 320/1200 px durante implementação encontrou e corrigiu moldura de altura fixa e rolagem horizontal interna. Créditos, menu, pausa, guia fechado e guia aberto foram inspecionados. O texto dos créditos continua pequeno devido ao limite 130 px e ao mundo 176×220; a escala é uniforme. O guia usa texto claro sobre fundo escuro e o receptor fica no cabeçalho de 44 px. O aceite visual final será registrado após a revisão e o gate inicial, separadamente do aceite funcional.

Evidências opcionais locais: `.agent/tmp/navigation-browser/credits-arrived-{320,1200}.png`, `menu-{320,1200}.png`, `pause-{320,1200}.png`, `controls-closed-{320,1200}.png`, `controls-open-{320,1200}.png` e `controls-open-bottom-{320,1200}.png`; logs/fingerprints em `.agent/tmp/validation/`. Nenhuma dessas imagens é necessária para compreender este resumo.

## Inventário confirmado e limites

O Validador executa localmente 11 comandos: suítes completas JVM/JS, sete percursos de navegador, unittest do wrapper e contrato CI com yq local. Fontes: plano, README, scripts e workflow. Sonar, mutation testing e Habit excluídos por ausência de configuração; não há alegação de pass ou score dessas ferramentas. O Coordenador acompanha os três checks CI e o Revisor aplica revisão estrutural. Committer preserva convenção e hooks normais, sem amend/rebase.

Android físico, outros navegadores, comparação com vídeo histórico e ampliação da v1 permanecem fora deste ciclo. Resultados de CI do ciclo anterior não aprovam este novo conteúdo. CI final e publicação deste ciclo ainda não comprovados neste checkpoint.


## Gate inicial e revisão concluídos

SHA testado: `e1025afc61397ea01a6bb8c40aa61520bd299743`. Checkout limpo durante o gate. Em 263,43 s, 11 checks selecionados e executados, 0 bloqueados, todos com execução e coleta completas. Não houve omissão de checks no resumo. Kof instalado 0.5.0-beta; Java 25.0.2; Node 24.16.0; Chrome 139.0.7258.154; yq 4.54.1.

| Comando local | Resultado observado |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 113 testes; 0 falhas; 1 arquivo executável aprovado |
| `python3 scripts/kof_project.py test --target js` | 113 testes; 0 falhas; 1 arquivo executável aprovado |
| `python3 tests/browser.py` | Créditos, texto, seleção/foco, guia, confirmações, pausa/resultado e retenção aprovados em 320/1200 px |
| `python3 tests/browser_controls.py` | Foco, teclado, cliques, diagonais, opostos, arrasto e cancelamento aprovados |
| `python3 tests/browser_meteor.py` | Movimento, três quadros de impacto e respawn aprovados |
| `python3 tests/browser_weapons.py` | Armas, especial, seis ordens de soltura e disponibilidade aprovados |
| `python3 tests/browser_stage.py` | Fase, HUD, pausa, resultado e nova partida aprovados |
| `python3 tests/browser_subchief.py` | Encontro completo, tiros, contatos, explosão e replay aprovados |
| `python3 tests/browser_boss.py` | Entrada, fases, tiros, especial, explosão de 28 passos, resultado/replay aprovados |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | 8 testes; OK |
| `PATH="$PWD/.agent/tmp/tools:$PATH" bash tests/ci-contract.sh` | Contrato CI aprovado; mocks não representam execução real de GitHub Actions |

Trechos literais dos comandos Kof, um por alvo:

```text
0 failed of 113 tests
```

Trechos literais de `python3 tests/browser.py` no Chrome:

```text
PASS Portuguese Canvas menus at x48/12px, ship selection and independent neutral focus at 320px
PASS Portuguese Canvas menus at x48/12px, ship selection and independent neutral focus at 1200px
PASS compact Controls, 14/16px guide, closed/open/reset details and Enter/Space/click/touch without duplicate transitions at 320px
PASS compact Controls, 14/16px guide, closed/open/reset details and Enter/Space/click/touch without duplicate transitions at 1200px
```

Aceite funcional: aprovado pelo agente sobre esse SHA, com os comandos acima. Isso demonstra o comportamento nos alvos e ambientes descritos; não comprova outros navegadores ou um Android físico.

Aceite visual: aprovado pela inspeção do agente, separadamente, nas capturas de créditos, menu, pausa, guia fechado e guia aberto, incluindo o fim dos detalhes e Voltar, em 320/1200 px. Textos legíveis dentro dos limites escolhidos, nave indicando linhas, contornos neutros, canvas/direcional/Especial recolhidos no guia, sem instrução fixa e sem rolagem horizontal. Detalhes expandidos usam rolagem vertical; a moldura agora acompanha o conteúdo. Nenhuma aprovação visual humana foi presumida.

Revisão estrutural com `refactor-design`: nenhuma correção de produção necessária. Campos de foco/teclas modelam a duração das interações, e `ControlsGuide` mantém conteúdo/expansão fora do domínio. Ordem dos eventos nativos protegida pelos percursos; estilos/widgets construídos uma vez. Recriar duas pequenas listas de créditos é apenas oportunidade de manutenção, sem risco demonstrado; nenhuma cache foi introduzida. Revisão, implementação e validação compartilham contexto.

O gate final repetirá os 11 comandos sobre o commit documental que consolida este aceite; o SHA e resultados finais, além dos três checks CI, serão associados ao [PR #18](https://github.com/renanfranca/kof-sifuture/pull/18) e aos seus [checks persistentes](https://github.com/renanfranca/kof-sifuture/pull/18/checks). O estado e os resultados detalhados permanecem também em `.agent/tmp/controls-guide.workflow.json` e `.agent/tmp/controls-guide-final.json`. Essa associação evita editar fontes versionadas depois do gate e atribuir evidência antiga a uma árvore nova.

Lacunas fora deste aceite: Android físico, outros navegadores, comparação com vídeo histórico e publicação após merge. Neste ponto documental, CI e gate final aguardam execução; o PR registra seu estado posterior. Sonar, mutation testing e Habit continuam excluídos, sem inventar resultado verde. Fontes de produção/assets permanecem iguais ao SHA acima após a revisão.

## Fonte bitmap, margem do guia e retornos — 2026-10-07

Plano: “Mais nitidez, espaço no guia e animação em cada retorno”. Execução no checkout atual e na branch `credits-pause-navigation`, a partir de `3e5c5d4b828eb2e51f2f255f7c286dd13a7fbb1e`, no chat `sifuture-clarity-primary`, `gpt-6.1-sol` / `medium`. Implementação, validação e revisão compartilham contexto. Esta seção complementa o histórico anterior; os resultados antigos não validam esta nova árvore.

Os menus e a pausa usam fonte bitmap branca com serifas, tamanho nominal 14 px e peso Bold. Os créditos usam tamanho nominal 9 px, peso Regular, azul RGB(0,128,255) e texto literal preservado. Cada PNG tem apenas alpha 0/255. Máscaras, métricas e licença da referência local Liberation Serif estão em `fonts/`; o gerador reproduz os assets diretamente em `assets/` e as métricas Kof. O nome completo mede 123 px; `renan.andradefranca@gmail.com`, 114 px. Todas as linhas ficam dentro de 130 px. Baselines locais 8/18 e 8/18/28; imagens criadas uma vez pelo GameView; posicionamento inteiro sem transformação ou redimensionamento pelo renderizador.

O [training de UI](/home/renanfranca/projects/kof/training/idioms/ui.md:287) orienta a composição por imagem:

```kof
c.drawImage(logo, 5, 5)
```

Trecho de [BitmapFont.kf](/home/renanfranca/projects/kof-sifuture/src/main/kof/sifuture/BitmapFont.kf:24):

```kof
var item = glyph(text.substring(i, i + 1))
canvas.drawImage(item.image, cursor + item.left, baseline + item.top)
cursor = cursor + item.advance
```

O avanço define a posição do próximo caractere, e os deslocamentos alinham sua máscara à baseline. `measure` soma os mesmos avanços. Isso evita reduzir texto já desenhado; o desenho usa os pixels de tamanho final. A [referência de módulos local](/home/renanfranca/projects/kof/docs/language-reference/modules.md) orientou imports explícitos nas fixtures. `learn/35-kof-ui.md` distingue modelo e desenho: “only the JS target draws”. A realização atual está em `KofUi.java:522` e `js/JsRuntimeUiWidgets.java:477–483`, que chama `ctx.drawImage(img, x, y)`; o teste `KofJsBrowserE2ETest.java:847` exercita a mesma operação. As provas de pixels são do app JS no Chrome, não da compilação JVM.

O guia tem painel externo preto de 248 px, padding 16 nos quatro lados e conteúdo 216 px. O estilo interno não repete padding. Tabela, listas e parágrafos cabem na coluna; fonte 14, entrelinha 20 e títulos 16 preservados. A seção Especial vem antes de Mais detalhes e está visível com os detalhes fechados. O texto completo sobre carga e disponibilidade continua nos detalhes. Crescimento vertical e retorno por Voltar foram exercitados; não houve rolagem horizontal.

Todas as transições reais ao menu passam pelo mesmo método no modelo; cada uma cria uma nova `MenuEntrance`. Voltar de Controles preserva a seleção, pausa/resultado selecionam Novo Jogo. Permanecer no menu apenas avança o objeto atual. Créditos permanecem exclusivos da abertura; teclado mantido continua bloqueado. A suíte observa o retorno antes do primeiro passo, o primeiro passo, a frenagem, a parada, repetições e confirmação antecipada. O navegador percorre os botões reais, incluindo Concluir contagem antes de Voltar ao menu quando necessário.

### Evidências anteriores ao checkpoint

Os comandos JVM/JS passaram na árvore alterada baseada no SHA acima: 2 testes de medidas bitmap e 114 jornadas do modelo por alvo. O SHA é a base, não uma identificação isolada do conteúdo não comprometido. As falhas esperadas anteriores incluíram dois retornos sem reiniciar a nave, padding ausente, ausência de máscaras/gerador e ausência de chamadas de desenho de glifos.

`python3 tests/browser.py`, app JS/Chrome 139.0.7258.154:

```text
PASS repeated real skip/Controls/pause/result arrivals at -30/-20/80/87/18, repaint and early confirmation at 320px
PASS native glyph pixels, single image load, 16px padding/216px content and closed Special at 320px density2
```

O primeiro desenho x=-30 é observado pela chamada Canvas, pois a nave está fora da imagem. Os passos visíveis são comparados com pixels dos sprites históricos. Créditos são comparados integralmente com composição independente dos PNGs; isso confere ordem, e-mail, cores e alinhamento. O teste de geração confere cada pixel, limite, repertório e bytes regenerados. Medidas Kof também são executadas nos dois alvos.

### Aceite visual separado

Capturas de créditos, menu, pausa e guia fechado/aberto foram produzidas para 320/1200 px e densidades 1/2, no Chrome 139.0.7258.154. A inspeção encontrou menus serifados mais fortes e coerentes com os sprites, crédito azul uniforme, nome/e-mail completos e guia com espaço interno e Especial destacado. Os créditos continuam pequenos no mundo 176×220. Os assets e o bitmap nativo são binários; capturas de densidade 2 apresentam a interpolação de apresentação do Canvas pelo navegador. Não se afirma ausência de filtragem no compositor do navegador ou paridade com um aparelho físico.

Evidências locais opcionais: `.agent/tmp/clarity-browser/{credits,menu,pause,guide,guide-open}-{320,1200}-d{1,2}.png`; `.agent/tmp/sifuture-clarity-*.log`; inventário e coletores `sifuture-clarity.validation.json`/`collectors.json`. Os fatos essenciais estão neste resumo e nos testes versionados. Inspeção automatizada e visual pelo agente; não houve sessão manual humana ou Android físico. Outros navegadores, comparação com vídeo histórico e publicação de Pages continuam fora da evidência local.

Inventário confirmado: 11 comandos locais — JVM/JS, sete percursos Chrome, unittest Python (incluindo reprodução/pixels) e contrato CI. Sonar, mutation runner e Habit sem configuração e excluídos. CI selecionado: Resolve verified Kof, Kof tests(jvm/js). Gates completos do checkpoint e do commit final serão registrados abaixo; a entrega continua no [PR #18](https://github.com/renanfranca/kof-sifuture/pull/18) e seus [checks](https://github.com/renanfranca/kof-sifuture/pull/18/checks).


### Primeira execução integral e ajuste de expectativa

SHA `3829df10ab82175b2b8f823edf0bd86fd098616e`: 11 comandos executados, coleta completa, 1 bloqueado; os outros dez passaram. Tempo 274,24 s. `browser_stage.py::pause_navigation` ainda comparava o sprite parado em x=18 após 20 passos do retorno da pausa. Nesse instante a entrada repetida está em frenagem em x=63. A expectativa foi adaptada conservando os 20 passos, a comparação dos pixels e as verificações de combate/teclas mantidas. Evidência local opcional: `.agent/tmp/validation/20261007T212216-3rxo74lp/summary.json`.

### Gate inicial aprovado e revisão estrutural

SHA testado `d462d7211e457f6d4ee180cb8443fef73f1b2a53`: 11/11 comandos executados, 0 bloqueados, coleta completa, 309,57 s. Kof 0.5.0-beta e Chrome 139.0.7258.154. Resultado por comando:

| Comando | Resultado |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 116 testes, 0 falhas, 2 suítes aprovadas |
| `python3 scripts/kof_project.py test --target js` | 116 testes, 0 falhas, 2 suítes aprovadas |
| `python3 tests/browser.py` | Créditos bitmap, menus, guia, retornos reais repetidos, pixels, foco e densidades 1/2 aprovados |
| `python3 tests/browser_controls.py` | Teclado, foco, contatos, diagonais/opostos e cancelamento aprovados |
| `python3 tests/browser_meteor.py` | Movimento, impactos e respawn aprovados |
| `python3 tests/browser_weapons.py` | Evolução, consumo de carga, disponibilidade e pressão sem repetição aprovados |
| `python3 tests/browser_stage.py` | Fase, HUD, pausa, resultado, reinício e entrada repetida durante bloqueio de tecla aprovados |
| `python3 tests/browser_subchief.py` | Encontro completo, tiros, explosão e replay aprovados |
| `python3 tests/browser_boss.py` | Entrada, fases, especial, explosão, resultado e replay aprovados |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 10 testes OK; pixels/métricas e reprodução incluídos |
| `PATH="$PWD/.agent/tmp/tools:$PATH" bash tests/ci-contract.sh` | Contrato CI aprovado com fixtures; não representa execução real de Actions |

Trechos literais das suítes Kof, em ambos os alvos:

```text
0 failed of 2 tests
0 failed of 114 tests
```

`python3 tests/browser_stage.py`, alvo JS/Chrome:

```text
PASS held right restores Middle.png on result entry and release, frozen ship and exact score at both widths
PASS Chrome 139.0.7258.154 at 320 and 1200 pixels; repaint does not advance simulation
```

As mensagens de sintaxe no unittest são esperadas: `test_real_compile_failure_does_not_publish` injeta `invalid syntax @@@` e verifica rejeição sem publicar output. Não são erros da aplicação aprovada. Evidência local opcional: `.agent/tmp/validation/20261007T212852-lxnh8iwz/summary.json`.

Revisão estrutural concluída no mesmo contexto da implementação. Não houve refactor de produção: transições pertencem ao modelo, fontes ao renderizador, máscaras ao gerador e estilos do painel são separados dos blocos. `measure` deriva a largura; não há cache duplicado. A comparação com a base comprova que assets históricos e arquivos de armas/combate/HUD não foram alterados. A mutabilidade dos glifos é uma oportunidade futura de manutenção, sem uso mutante atual que justifique alteração neste ciclo. Detalhes opcionais em `.agent/tmp/sifuture-clarity.structural-review.md`.

O delta após esta revisão é apenas documentação. O gate final repetirá os mesmos 11 comandos no último commit; seu SHA e resultado serão associados ao [PR #18](https://github.com/renanfranca/kof-sifuture/pull/18) e aos [checks](https://github.com/renanfranca/kof-sifuture/pull/18/checks), sem alegar que CI anterior aprovou este conteúdo. Nenhum merge ou publicação de Pages integra esta execução. Limites visuais e de dispositivo permanecem os registrados acima.


## Fonte normal e legível — ciclo aprovado de 2026-10-07

Este suplemento substitui as dimensões, tipografia e relógios dos créditos dos registros anteriores; os resultados históricos permanecem como histórico. Base da execução: `ab21e65cbb3a7a099b972d5476a995eb4c9aea81`, branch `credits-pause-navigation`, entrega no [PR #18](https://github.com/renanfranca/kof-sifuture/pull/18) e [checks](https://github.com/renanfranca/kof-sifuture/pull/18/checks). Execução, validação e revisão compartilham o mesmo contexto `credits-text-primary`, gpt-6.1-sol/medium.

### Auditoria das expectativas

As escolhas aprovadas são: texto sans-serif suave de16px; créditos exclusivos262 × 260 sobre #121212, margens12, linhas24, RGB(0,128,255) uniforme e e-mail inteiro; nome dividido em duas linhas. Blocos y40/136, baselines locais16/40/64. Entrada x-262 até12 em passos5/30ms, parada por6000ms após chegada, saída1px/30ms com altura72, quadro final vazio. Durante créditos apenas receptor de teclado e Pular créditos. Menus brancos x48/baseline opção+14, zonas128 × 19, nave e espaçamentos preservados. Jogo176 × 220, guia aprovado e APIs Kof preservados.

O passo54 está em x8, o55 chega exatamente a12. Passos56–255 são200 intervalos completos de30ms; passo256 inicia a saída. Passo462 tem y247/-71, passo463 tem y248/-72: o segundo bloco passa da borda superior. Passo474 tem y259/-83 e passo475 y260/-84: o primeiro fica completamente fora. Passo476 permanece Créditos sem texto, passo477 abre Menu. A altura dos blocos determina a saída; a altura do mundo do jogo não governa o relógio dos créditos.

### Auditoria das asserções

`GameJourney` observa `Game.step`, a entrada antes/depois do clamp, espera199/200, primeira saída, ambos os limites e saída para Menu. A primeira execução JVM falhou na expectativa inicial da nova jornada; a implementação corrigiu o relógio. Trecho de `python3 scripts/kof_project.py test --target jvm`:

```text
FAIL credits enter exactly at twelve wait six seconds and leave one empty frame: assertion failed
1 failed of 114 tests
```

`tests/browser.py` observa a aplicação gerada, chamadas de Canvas com transformação e medidas reais, tamanho efetivo16px, cores, limites e áreas de toque. Repetir ArrowLeft redesenha sem avançar o relógio. O primeiro percurso falhou porque a superfície ainda media176 × 220; após criar a superfície exclusiva, o percurso completo passou. Excertos de `python3 tests/browser.py`, JS/Chrome139.0.7258.154:

```text
PASS Portuguese sans-serif menus at x48/16px, ship selection and independent neutral focus at 320px
PASS 16px smooth text, complete credits/email at zoom100%, no bitmap fonts, guide padding/216px and closed Special at 320px density2
```

A escala observada corresponde a16px, com tolerância0,001 para a representação numérica. Os seis textos são comparados literalmente e medidos com o próprio Canvas, com margens12 no quadro parado; todos os cinco rótulos de menu são comparados às zonas128 × 19 e às linhas de base. A cor/transformação do contexto volta a branco/identidade após desenho. Pixels de alfa parcial demonstram suavização no ambiente testado; não fixam um desenho de glifo para todos os sistemas. O quadro476 verifica todas as componentes transparentes do bitmap, além da ausência de chamadas de texto. Zoom100%, densidades1/2, ausência de rolagem horizontal e direcional/Especial ocultos são verificados no navegador. As jornadas existentes preservam Enter/Espaço/toque, seleção/foco, tecla mantida, pausa, guia e resultado. Os sete percursos observam o canvas visível; o segundo canvas oculto dos créditos não substitui a superfície176 × 220 do jogo.

### Regra Kof e evidência do alvo

O [idioma de UI](/home/renanfranca/projects/kof/training/idioms/ui.md:277) orienta:

> `save`/`restore` stack the context state (alpha, transform,
> colors) — without them, an adjustment leaks into all the following drawing.

Em [GameView.kf](../../src/main/kof/sifuture/GameView.kf), o desenho compartilhado aplica:

```kof
target.save()
target.setFill(color)
target.transform(1.6, 0.0, 0.0, 1.6, x * 1.0, baseline * 1.0)
target.fillText(text, 0, 0)
target.restore()
```

A transformação coloca a origem na posição desejada e multiplica a fonte padrão10px por1,6. `restore` recupera o estado anterior; a próxima imagem conserva suas coordenadas. O registro `KofUi.java:516–521`, a implementação `JsRuntimeUiWidgets.java:449–475` e `UiE2ETest.java:672` foram consultados diretamente; os métodos já existem e delegam ao contexto Canvas no navegador. A antiga página `docs/ui/PLAN-CANVAS-WIDGET.md` não enumera todas essas operações, por isso não foi usada como prova de ausência. O [capítulo Learn Kof35](/home/renanfranca/projects/kof/learn/35-kof-ui.md:3) afirma:

> only the JS target draws

Logo, executar as jornadas do modelo em JVM/JS e medir a apresentação no Chrome são evidências complementares. O compilador sozinho não demonstra legibilidade. O corpus consultado inclui `training/language/ui.md`, `training/idioms/ui.md`, classes/controle de fluxo e `training/anti-patterns/fake-idioms.md`; nenhuma API pública do Kof foi alterada.

### Aceite visual e limites

A inspeção inicial do agente encontrou nome e e-mail completos, texto azul uniforme e menus brancos alinhados com a nave. Capturas são geradas em320/1200px e densidades1/2, Chrome139.0.7258.154/zoom100%. Evidência local opcional: `.agent/tmp/credits-text-browser/`, incluindo imagens da página e do canvas. O guia mantém as verificações e as capturas de sua composição aprovada. Inspeção do agente é distinta da aprovação visual do usuário, que permanece pendente. Família sans-serif concreta e rasterização podem variar por sistema; outros navegadores e Android físico não estão demonstrados.

Gerador, classes, JSON de máscaras, PNGs `font-*` e testes de máscaras/medidas da fonte bitmap foram removidos após a migração dos consumidores. Texto e geometria passaram ao percurso real de navegador; não há teste novo imposto por organização interna. Imagens históricas, dígitos do HUD, NOTICE e licenças arquivadas permanecem preservados.

Inventário confirmado: dez comandos locais — suítes JVM/JS, sete percursos Chrome e unittest Python — e três checks CI, Resolve verified Kof e Kof tests(jvm/js). Sonar, Habit e executor de mutação excluídos por ausência de configuração; não se atribui resultado aprovado ou score a ferramentas não executadas. Os gates completos no commit e seus resultados serão registrados após execução.


### Gate inicial aprovado e revisão estrutural

SHA testado: `fbe2029b03b58f5a778d8429442dd9486c57274f`. Checkout limpo durante o gate. Dez comandos selecionados e executados, zero bloqueados, coleta completa; duração272,45s. Kof instalado0.5.0-beta; Chrome139.0.7258.154; larguras320/1200px, densidades1/2 e zoom100%. Resultado observado:

| Comando | Resultado |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 114 testes, zero falhas, uma suíte aprovada |
| `python3 scripts/kof_project.py test --target js` | 114 testes, zero falhas, uma suíte aprovada |
| `python3 tests/browser.py` | Texto16px, créditos completos, dimensões/cores, relógio, quadro vazio, cinco zonas, foco, confirmações e retornos aprovados |
| `python3 tests/browser_controls.py` | Teclado, foco, contatos, diagonais/opostos, arrasto/cancelamento aprovados |
| `python3 tests/browser_meteor.py` | Movimento, três impactos e respawn aprovados |
| `python3 tests/browser_weapons.py` | Armas, especial, seis ordens de soltura e disponibilidade aprovados |
| `python3 tests/browser_stage.py` | Fase, HUD, pausa, resultado, reinício e entrada repetida aprovados |
| `python3 tests/browser_subchief.py` | Encontro completo, tiros, contatos, explosão e replay aprovados |
| `python3 tests/browser_boss.py` | Entrada, fases, especial, explosão, resultado e replay aprovados |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | Oito testes, OK |

Trecho literal das suítes Kof, uma por alvo:

```text
0 failed of 114 tests
1 passed, 0 failed
```

Trecho literal de `python3 tests/browser.py`, JS/Chrome:

```text
PASS credits frames0/1/54/55/254/255/256/462/463/474/475/476/477, six-second hold, text geometry/color/transform isolation and entrance0/1/11/12/13/35/36 at 320px
PASS menu, Enter and Space, conservative confirmation, pause, result and menu in Chrome
```

As mensagens PARSE do unittest são esperadas no caso `test_real_compile_failure_does_not_publish`, que injeta sintaxe inválida e exige rejeição sem publicação. Não representam falha na aplicação. Evidência local opcional do gate: `.agent/tmp/validation/20261008T014051-6u7fx6zr/summary.json`.

Revisão estrutural no mesmo contexto da implementação: nenhuma alteração de produção necessária. Relógio no modelo, texto no renderizador e visibilidade/foco nos controles; os dois canvases e estilos são criados uma vez. O helper recebe todos os dados do desenho e restaura o contexto, sem reter pedido mutável. `exitComplete` distingue o quadro vazio da abertura do menu. A repetição das dimensões fixas nos estilos é uma oportunidade futura, protegida pela geometria independente, sem justificar refactor neste ciclo. O [idioma de UI](/home/renanfranca/projects/kof/training/idioms/ui.md:277) e os anti-patterns `duplicate-state.md`/`unnecessary-abstraction.md` foram novamente consultados. Rubrica e classificações locais opcionais: `.agent/tmp/credits-text.structural-review.md`.

A auditoria de critérios confirmou as escolhas aprovadas; a auditoria de asserções confirmou as observações correspondentes no modelo e na aplicação real. A inspeção visual do agente conferiu os12 recortes de créditos/menu/pausa em320/1200px e densidades1/2, com nome/e-mail completos e nenhuma opção cortada. Não houve aprovação visual humana; essa aceitação continua pendente. Os108 assets históricos comparados à base mantêm seus blobs Git, incluindo números do HUD. Só os glifos gerados foram retirados.

O delta após a revisão contém apenas este registro de aceitação. O gate final repetirá os dez comandos no commit da documentação; seu SHA e resultados serão associados ao [PR #18](https://github.com/renanfranca/kof-sifuture/pull/18) e aos [checks](https://github.com/renanfranca/kof-sifuture/pull/18/checks). Não se usa CI antigo como prova deste conteúdo. Merge e publicação de Pages não foram executados. Limites: aprovação visual do usuário, outros navegadores e Android físico continuam sem verificação.

### Revisão independente do plano — 2026-10-08

SHA revisado e testado: `26631abb604e281222ddf4b17a6a078cc6e744a2`, checkout limpo durante os testes. A revisão comparou o delta desde `ab21e65cbb3a7a099b972d5476a995eb4c9aea81` com o plano aprovado de fonte normal nos créditos e menus. Não encontrou desvios do plano ou regressões nos percursos executados. Esta execução confirma localmente o gate no commit da documentação; não confirma checks remotos, merge ou publicação.

| Comando | Resultado observado nesta revisão |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 114 testes, zero falhas |
| `python3 scripts/kof_project.py test --target js` | 114 testes, zero falhas |
| `python3 tests/browser.py` | Texto, geometria, cores, animação, quadro vazio, navegação e retornos aprovados |
| `python3 tests/browser_controls.py` | Teclado, foco, ponteiros e toque aprovados |
| `python3 tests/browser_meteor.py` | Movimento, impactos e respawn aprovados |
| `python3 tests/browser_weapons.py` | Armas, especial e controles aprovados |
| `python3 tests/browser_stage.py` | Fase, HUD, pausa, resultado e reinício aprovados |
| `python3 tests/browser_subchief.py` | Encontro completo e replay aprovados |
| `python3 tests/browser_boss.py` | Encontro completo e replay aprovados |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | Oito testes, OK |

Trechos literais de `python3 tests/browser.py`, JS/Chrome 139.0.7258.154:

```text
PASS Portuguese sans-serif menus at x48/16px, ship selection and independent neutral focus at 320px
PASS repeated real skip/Controls/pause/result arrivals at -30/-20/80/87/18, repaint and early confirmation at 1200px
PASS 16px smooth text, complete credits/email at zoom100%, no bitmap fonts, guide padding/216px and closed Special at 320px density2
```

As asserções com medidas reais no Canvas verificaram os seis textos dos créditos, os cinco rótulos de menu, tamanho efetivo de 16px, margens de 12px, cores, áreas de toque e restauração do estado de desenho. O percurso passou em larguras de 320/1200px e densidades 1/2 a 100% de zoom. Os limites da animação e o quadro final vazio foram conferidos no modelo e no navegador. A comparação dos assets encontrou apenas a remoção dos 65 glifos gerados; imagens históricas e NOTICE não mudaram. O guia de controles e o modelo de entradas repetidas no menu não tiveram alterações de produção neste delta.

A inspeção visual do agente, por amostragem das capturas de créditos, menu principal e pausa, encontrou nome/e-mail completos e opções sem cortes. As capturas não substituem a aprovação visual do usuário. Outros navegadores e Android físico permanecem sem verificação. Não houve correção no código de produção; a única alteração desta revisão é este registro.

Evidências locais opcionais: `.agent/tmp/review-legible-text-20261008T125732Z/summary.json` e logs `01.log` a `10.log`; capturas renovadas em `.agent/tmp/credits-text-browser/`. Os resultados essenciais estão acima e não dependem desses arquivos locais.

### Merge e publicação verificada — 2026-10-08

Após autorização explícita do usuário, o [PR #18](https://github.com/renanfranca/kof-sifuture/pull/18) foi integrado a `main` às 13:33:15 UTC. SHA integrado, testado no CI e publicado: `e649066885e3b3fd6513bebf8629c29d46f835b3`. A árvore desse merge corresponde à revisão `2a98416a97a4236a551c7247b8f93b6bcadbcbde`, que inclui o registro independente acima.

O [CI do PR](https://github.com/renanfranca/kof-sifuture/actions/runs/37784858795) passou nos três jobs aplicáveis. O [workflow de main](https://github.com/renanfranca/kof-sifuture/actions/runs/37785258372) terminou com sucesso nos cinco jobs: resolução do Kof, testes JVM/JS, construção do site completo e publicação. O passo de publicação foi executado com sucesso, sem ser ignorado. A API do GitHub confirmou o deployment `6937009579`, associado ao SHA integrado:

```json
{"environment_url":"https://renanfranca.github.io/kof-sifuture/","state":"success"}
```

A aplicação publicada em [GitHub Pages](https://renanfranca.github.io/kof-sifuture/) foi verificada com `python3 tests/browser.py https://renanfranca.github.io/kof-sifuture/`, saída 0. Chrome 139.0.7258.154, larguras 320/1200px, densidades 1/2 e zoom 100%. Trechos literais:

```text
PASS Portuguese sans-serif menus at x48/16px, ship selection and independent neutral focus at 320px
PASS 16px smooth text, complete credits/email at zoom100%, no bitmap fonts, guide padding/216px and closed Special at 1200px density2
PASS menu, Enter and Space, conservative confirmation, pause, result and menu in Chrome
```

O percurso verificou créditos, animação, menus, controles e navegação na aplicação pública. O cenário determinístico de resultado usa a fixture `tests/weapons.kf`, compilada e servida localmente pelo mesmo teste; seu resultado não demonstra execução dessa fixture no Pages. Esta checagem de publicação complementa os sete percursos e as suítes completas já registrados acima, sem atribuir uma nova execução pública a todos eles.

O checkout local foi restaurado para `main`, sincronizado com `origin/main` e limpo após o merge. Este registro será entregue em um commit apenas de documentação; a publicação desse commit será acompanhada também. A aprovação visual humana continua pendente; a execução automatizada não a substitui. Evidências locais opcionais: `.agent/tmp/merge-pages-pr-ci.json`, `.agent/tmp/merge-pages-main-ci.json`, `.agent/tmp/merge-pages-deployment-status.json`, `.agent/tmp/merge-pages-live-browser.log` e capturas em `.agent/tmp/credits-text-browser/`.
