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
assert guide.evaluate(...) == ["14px", "20px", "sans-serif", "12px"]
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

O [training de UI](/home/renanfranca/projects/kof/training/idioms/ui.md:275) orienta:

> `measureText` returns a `Double` (width in px) for text layout.

Em [GameView.kf](../../src/main/kof/sifuture/GameView.kf), a mesma escala é passada para os dois blocos:

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
