# Aceite: capturas determinísticas nas jornadas de navegador

Plano: [`.agent/execplans/journey-determinism.md`](../execplans/journey-determinism.md).
Issue #35. Branch `fix/35-journey-determinism`, a partir de `1ef70ba`. Execução
em 20/11/2026.

## Versões

- Chrome do sistema (só no M0): `Google Chrome 158.0.8127.36`.
- Chromium do Playwright: `159.0.8154.6`, aberto com `channel="chromium"`
  (headless novo). Playwright 1.65.2, Pillow 12.1.1, Python 3.14.4.
- `python3 -m pip install --user -r tests/requirements-browser.txt` falha nesta
  máquina por PEP 668; os pacotes já estavam nas versões fixadas. A documentação
  indica ambiente virtual ou `--break-system-packages`.

## Rodadas

Todas as rodadas abaixo: 7/7 jornadas com exit 0 e 186 capturas.

| Etapa | Navegador e opções além de `--no-sandbox` | Rodadas | `compare` |
| --- | --- | --- | --- |
| M0, jornadas da `main` | Chrome 158, `--headless=new` | 3 | `unstable=28` |
| M2 | Chromium 159, nenhuma | 3 | `unstable=31` |
| M3 | as seis do Prototypes | 3 | `unstable=11` (0 de raster) |
| M3 | `--disable-gpu` | 3 | `unstable=27` |
| M3 | `--disable-partial-raster --disable-skia-runtime-opts` | 3 | `unstable=11` (0 de raster) |
| M3 | `--disable-partial-raster` | 3 | `unstable=12` (0 de raster) |
| M3 | `--disable-partial-raster --js-flags=--random-seed=1` | 3 | `unstable=15` (semente sem efeito; 1 corrida) |
| Final | `--disable-partial-raster` e semente fixa (`SeededBrowser`) | 5 | `runs=5 common=186 only_some=0 unstable=0` |

Causas das instáveis antes da árvore final:

1. Ruído de raster (diferença de 1 a 2 níveis em até 64 pixels): some com
   `--disable-partial-raster`.
2. Semente aleatória da partida (até 255 em centenas de pixels):
   `keyboard-retained-*`, `application-*` e `app-*`. `Game.kf:87` chama
   `random.int`, que no navegador usa `crypto.getRandomValues`
   (`kofRandByte` em `kof-runtime.mjs`). Resolvida pela semente fixa por página
   em `tests/journey_browser.py`, decisão do usuário após o M3.
3. Corrida de tempo: `special-key-release/released-320.png` saiu uma vez com a
   borda do botão "Especial" desenhada (rodada 3 do protótipo com a semente do
   V8). Não reapareceu nas cinco rodadas finais; fica como risco residual.

## Critérios

| # | Comando | Resultado observado | Evidência |
| --- | --- | --- | --- |
| A1 | cinco `capture` e `compare` das cinco | `runs=5 common=186 only_some=0 unstable=0`; no M0, a mesma comparação com três rodadas deu `unstable=28` | tabela acima |
| A2 | `summary.txt` de cada rodada; `npm run check:task` | 7/7 exit 0 em todas as rodadas; `check:task` na validação final abaixo | tabela acima |
| A3 | `summary.txt`; `grep -rn google-chrome tests/` | `browser=159.0.8154.6` nas cinco rodadas finais; `grep` vazio | — |
| A4 | `git diff main -- 'tests/browser*.py'` | só as nove aberturas trocadas por `launch(...)` e uma linha `from journey_browser import launch` por arquivo; nenhuma asserção, espera ou captura mudou | diff |
| A5 | `python3 -m unittest discover -s tests -p 'test_*.py'` | quatro testes do `compare`, cada um vermelho antes pela asserção; mais `test_every_page_draws_the_same_random_sequence`, vermelho antes por `Lists differ` | `tests/test_journey_pixels.py`, `tests/test_journey_browser.py` |
| A6 | `git diff --name-only main`; `git status --porcelain --untracked-files=all` | a lista do plano, mais `tests/test_journey_browser.py`, que veio com a decisão da semente; nada de `.agent/tmp/` | — |

## Validação final

Na `main` `9a8c1f0` (depois do #37): `python3 -m unittest discover -s tests -p
'test_*.py'` OK, 20 testes; `npm run test:sensors` 39 pass, 0 fail; `npm run
check` `CHECK: PASS` (`mutation` em SKIP, sem produção alterada); `npm run
check:task` `CHECK:TASK: PASS`, com as sete jornadas em PASS no Chromium do
Playwright; `git diff --check` exit 0.
