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

O [training de UI](../../../kof/training/idioms/ui.md) orienta a composição por imagem:

```kof
c.drawImage(logo, 5, 5)
```

Trecho de [BitmapFont.kf](../../src/main/kof/sifuture/BitmapFont.kf):

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
