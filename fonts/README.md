# Fonte bitmap SiFuture

Os menus usam letras brancas com serifas em tamanho nominal de 14 px, baseadas em Liberation Serif Bold. Os créditos usam tamanho nominal de 9 px, Liberation Serif Regular como referência e RGB(0,128,255). Os PNGs históricos continuam intactos.

A referência veio dos arquivos `LiberationSerif-Bold.ttf` e `LiberationSerif-Regular.ttf` instalados em `/usr/share/fonts/truetype/liberation/`. Os SHA-256 estão em `bitmap.json`. O pacote local atribui a fonte à Red Hat, copyright 2007, e informa a origem <https://pagure.io/liberation-fonts/>. Esta versão local usa GPL v2 com as exceções da licença Liberation; não se presume a licença de versões posteriores. O texto do pacote está em [LIBERATION-LICENSE.txt](LIBERATION-LICENSE.txt), e a GPL v2 completa em [GPL-2.txt](GPL-2.txt). Os arquivos TTF não são redistribuídos aqui. As fontes bitmap derivadas usam nomes SiFuture, sem renomear ou modificar os arquivos de referência.

`bitmap.json` é a entrada canônica editável. Cada caractere tem máscara (`#` opaco, `.` transparente), avanço horizontal inteiro e deslocamentos `left`/`top` em relação à posição do caractere e à baseline. Espaços usam um PNG transparente de 1 × 1 e preservam seu avanço. O repertório cobre os textos atuais, o alfabeto minúsculo completo dos créditos e `?` para caracteres sem desenho.

As máscaras iniciais foram obtidas com Pillow, FreeType e limiar 128 sobre a rasterização em tamanho final, sem redimensionamento. Essa etapa já está materializada nas máscaras; a reprodução não depende dos TTF ou da versão do rasterizador. Para editar, altere as máscaras ou métricas e execute:

```bash
python3 scripts/bitmap_font.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

O gerador reproduz os PNGs diretamente em `assets/` e as métricas em `BitmapFonts.kf`. `--output DIRETÓRIO` permite comparar uma geração isolada; `--source ARQUIVO` permite usar outro arquivo de máscaras. O teste compara os bytes regenerados no ambiente local, cada pixel com a máscara, cores, alturas, avanços e limites das linhas.

`BitmapFont.measure(text)` soma os mesmos avanços que `draw(canvas, text, x, baseline)` usa para posicionar as imagens. Não há kerning ou escala fracionária. O nome completo mede 123 px e o e-mail literal `renan.andradefranca@gmail.com` mede 114 px; os cinco textos dos créditos ficam dentro de 130 px. Baselines locais: 8/18 px no primeiro bloco, 8/18/28 px no segundo. Imagens são criadas uma vez pelo `GameView`, e cada desenho usa coordenadas inteiras.
