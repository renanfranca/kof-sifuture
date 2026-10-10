# Texto dos créditos e menus

[English](README.md) | [Português (Brasil) — pt-BR](README.pt_BR.md)

Créditos, menu principal e pausa usam a fonte padrão `10px sans-serif` do Canvas do navegador com transformação de escala `1.6`, resultando em tamanho efetivo de 16 px. O desenho compartilhado em `GameView.drawText` usa `save`, `setFill`, `transform`, `fillText` e `restore`: a escala e a cor temporárias não alteram sprites ou desenhos seguintes. A suavização é realizada pelo navegador; a família sans-serif concreta depende do ambiente.

Os créditos têm superfície exclusiva de 262 × 260 px, fundo #121212, margens de 12 px e linhas separadas por 24 px. Todos os textos usam RGB(0,128,255), inclusive `renan.andradefranca@gmail.com`, inteiro em uma linha. O nome ocupa “Renan Meneses” e “de Andrade Franca”. Os blocos começam em y40/136, com linhas de base locais16/40/64.

Menus usam branco, x48 e linha de base `y da opção + 14`, preservando áreas de toque128 × 19 px e a nave indicadora. O canvas do jogo permanece176 × 220 px. A animação dos créditos chega a x12 no passo55, espera 200 passos de30ms e move blocos de72px até saírem completamente. O passo476 fica vazio; o passo477 abre o menu.

A antiga composição por glifos PNG, seu gerador e suas métricas deixaram de ter consumidores. Imagens históricas, números do HUD e NOTICE são preservados. Os textos de licença [LIBERATION-LICENSE.txt](LIBERATION-LICENSE.txt) e [GPL-2.txt](GPL-2.txt) permanecem como registro da referência Liberation Serif usada pela antiga fonte; não descrevem a sans-serif atual do navegador.

`python3 tests/browser.py` verifica texto, tamanho efetivo, cor, limites, áreas de toque, restauração do Canvas e animação, em Chrome nas larguras320/1200px e densidades1/2, com zoom100%. Capturas e inspeção visual do agente são registradas separadamente da aprovação visual do usuário em `.agent/validation/controls-guide.md`.
