# Capturas determinísticas nas jornadas de navegador

## Purpose and success

Issue #35: as capturas PNG das sete jornadas de navegador (`tests/browser*.py`)
deixaram de ser determinísticas. Rodando a `main` sem mudança duas vezes, 19 das
186 capturas saíram com pixels diferentes. Isso tira o valor da prova "a
aparência não mudou", usada nos lotes de refatoração: uma regressão real fica
escondida no ruído.

Depois deste trabalho:

- cinco rodadas seguidas das sete jornadas, sem nenhuma mudança de código entre
  elas, produzem capturas com os mesmos pixels decodificados, em todas;
- as jornadas abrem um navegador de versão fixa, que não muda sozinho com
  atualização do sistema;
- a captura e a comparação de pixels viram uma ferramenta versionada e testada,
  em vez de scripts soltos em `.agent/tmp/`, que já se perderam uma vez;
- a documentação diz como preparar o navegador e como rodar a comparação.

As asserções das jornadas não mudam: as mudanças em `tests/browser*.py` se
limitam à abertura do navegador.

## Definitions

- **Jornada**: um `tests/browser*.py`. O `npm run check:task` descobre os arquivos
  pelo nome `browser*.py` (`scripts/check-task.mjs:8-13`) e roda cada um. Um módulo
  auxiliar em `tests/` **não pode** começar com `browser`, senão vira jornada.
- **Captura**: PNG que a jornada grava em `.agent/tmp/<pasta>/`. Há dois tipos:
  só o canvas (`page.locator("canvas:visible").screenshot(...)`) e página inteira
  (`page.screenshot(..., full_page=True)`).
- **Rodada**: as sete jornadas, uma depois da outra, com as capturas copiadas para
  uma pasta própria.
- **Capturas instáveis**: as que mudam de pixel entre rodadas da mesma árvore.

## Context and limits

Fatos medidos no planejamento, em 20/11/2026, na `main` `1ef70ba`:

- As sete jornadas abrem o Chrome do sistema:
  `chromium.launch(executable_path="/usr/bin/google-chrome", headless=False,
  args=["--no-sandbox", "--headless=new"])`, repetido em nove lugares:
  `tests/browser.py:793`, `tests/browser_boss.py:226`,
  `tests/browser_controls.py:618`, `tests/browser_meteor.py:46`,
  `tests/browser_stage.py:391`, `tests/browser_subchief.py:223`,
  `tests/browser_weapons.py:634` e `:647`. A versão instalada é a
  `Google Chrome 158.0.8127.36`, que se atualiza pelo gerenciador de pacotes. Foi
  assim que ela mudou entre 16/11 (186 capturas estáveis, lote da UI) e 19/11 (19
  instáveis, R6).
- Playwright 1.65.2 e Pillow 12.1.1 instalados em `~/.local` com Python 3.14.4,
  **sem versão fixada no repositório**. O Chromium que vem com o Playwright
  1.65.2 é o `159.0.8154.6` (`driver/package/browsers.json`), e ele **não** está
  baixado (`~/.cache/ms-playwright` não existe).
- As 19 instáveis do R6 (`.agent/tmp/debt-fixtures/b0-unstable.txt`) são todas de
  página inteira: 15 da aplicação (`credits-text-browser/*`, `application-*`,
  `app-*`) e 4 da fixture `weapons.kf` (`keyboard-game-*-1200`, `layout-*`). A
  diferença ampliada é antialiasing nas setas e nos cantos arredondados do
  `GameControls`. Nenhuma captura só do canvas oscilou.
- Ferramentas do R6, não versionadas, em `.agent/tmp/debt-fixtures/tools/`:
  `journeys.sh` (rodada) e `pixels.py`, `variants.py` e `noise.py` (comparação).
  ❗️ `journeys.sh` apaga toda pasta de `.agent/tmp/` que não seja
  `debt-fixtures`; não reutilizar assim.
- As jornadas não rodam na CI (`.github/workflows/kof-ci-and-pages.yml` só roda os
  testes Kof e o Pages).
- `docs/desenvolvimento.pt_BR.md:515-538` e `docs/desenvolvimento.md:539-562`
  ("Verificar o navegador") pedem Chrome em `/usr/bin/google-chrome` e "sessão
  gráfica", o que já não é verdade com `--headless=new`.
- `.agent/tmp/` está em `.git/info/exclude` nesta máquina (local).

### Limites

- Não mudar `src/`, os `tests/*.kf`, `kof-mut.json` nem os scripts dos sensores.
- Em `tests/browser*.py`, mudar só a abertura do navegador. Nenhuma asserção,
  clique, espera, viewport ou nome de captura muda.
- Não trocar a captura de página inteira por captura só do canvas. Isso muda o
  que a evidência mostra e precisa de decisão do usuário (ver Risks).
- Não desinstalar nem alterar o Chrome do sistema.

## Decisions

**Chromium do Playwright, com versão fixada no repositório (usuário, 20/11).**
As jornadas passam a abrir o Chromium que vem com o Playwright, no modo headless
novo, sem `executable_path`. Um arquivo `tests/requirements-browser.txt` fixa
`playwright==1.65.2` e `pillow==12.1.1`; como cada versão do Playwright traz
uma versão própria do Chromium, fixar o Playwright fixa o navegador. A preparação
passa a ser `python3 -m pip install --user -r tests/requirements-browser.txt` e
`python3 -m playwright install chromium`. Alternativa descartada: continuar no
Chrome do sistema, que muda sem aviso. Consequência: um Chromium de cerca de
150 MB em `~/.cache/ms-playwright`; atualizar o Playwright passa a ser uma
mudança deliberada, que exige uma rodada nova de estabilidade.

**Abertura do navegador num lugar só.** Um módulo `tests/journey_browser.py`
(nome que não começa com `browser`) exporta a função que abre o navegador com as
opções decididas aqui, e as nove chamadas passam a usá-la. Assim as opções de
renderização ficam numa linha só.

**Rodada e comparação versionadas.** `scripts/journey_pixels.py`, com dois
subcomandos:

- `capture <destino>`: roda as sete jornadas descobertas como no `check:task`,
  registra o exit de cada uma e a versão do navegador, e copia as capturas
  geradas nessa rodada para `<destino>/png/`, mantendo o caminho relativo. Só pode
  apagar as pastas de evidência que as jornadas escrevem, nunca outras pastas de
  `.agent/tmp/`.
- `compare <rodada> <rodada> [...]`: compara os pixels RGB decodificados (Pillow),
  por nome de captura, entre duas ou mais rodadas, e imprime
  `runs=N common=N only_some=N unstable=N` e o nome de cada captura instável ou
  ausente; sai com código diferente de 0 se `unstable` ou `only_some` não for 0.

Testes de comportamento em `tests/test_journey_pixels.py` (descobertos pelo
`unittest discover -s tests -p 'test_*.py'`), com PNGs pequenos gerados no
próprio teste: rodadas idênticas → 0 e exit 0; um pixel diferente numa rodada →
aquela captura listada como instável e exit diferente de 0; uma captura ausente
numa rodada → listada em `only_some`; mesmo conteúdo com tamanho diferente →
instável. O `capture` é provado pelas rodadas reais do M2 a M4.

**Semente fixa nas jornadas (usuário, 20/11, opção 1 após o M3).** O
`launch` devolve o navegador embrulhado (`SeededBrowser`): cada `new_page` e
`new_context` recebe um script de inicialização que troca
`crypto.getRandomValues` por um gerador com semente fixa. Alternativas
descartadas: excluir as capturas da aplicação da prova, ou entregar com o A1 não
atendido. Consequência: nas jornadas, o jogo normal joga sempre a mesma partida;
as jornadas continuam mudando só a linha de abertura. Testado em
`tests/test_journey_browser.py`.

## Risks

- **O Chromium do Playwright também oscila.** É possível. Por isso o M3 é um
  protótipo de opções de renderização. Se nenhuma combinação chegar a 0
  instáveis, **parar antes do commit** e reportar ao usuário as capturas que
  sobram e as opções testadas. A saída seguinte (captura só do canvas, ou
  tolerância) é decisão dele.
- **Asserções que comparam pixels com sprites mudam de resultado no navegador
  novo** (por exemplo `bitmap` e `sprite` de `tests/browser_stage.py`, e
  `tests/browser_meteor.py:20`). Se uma jornada falhar no Chromium do Playwright,
  parar e reportar com a captura e a diferença; não ajustar a asserção.
- **Carga da máquina.** Não rodar KofMut nem outro trabalho pesado durante as
  rodadas.

## Prototypes

Hipótese do M3: com o Chromium fixo, um conjunto pequeno de opções de linha de
comando torna as capturas de página inteira estáveis. Candidatas, a testar
sozinhas e depois combinadas, nesta ordem: `--disable-gpu`,
`--force-color-profile=srgb`, `--disable-lcd-text`,
`--font-render-hinting=none`, `--disable-partial-raster`,
`--disable-skia-runtime-opts`. Critério de sucesso: três rodadas seguidas com
`unstable=0`. Escolher o menor conjunto que atinge o critério e registrar a
tabela "opções → instáveis" no aceite.

## Milestones

### M0. Linha de base atual

1. `git status --porcelain --untracked-files=all` só com este plano.
2. Registrar `google-chrome --version`, a versão do Playwright e a do Pillow.
3. Com o Chrome do sistema e o código da `main`, três rodadas seguidas (com o
   `journeys.sh` do R6 adaptado para não apagar outras pastas, ou já com o
   `capture` do M1, se ele vier antes). Comparar.

Esperado: 7/7 exit 0 nas três; quantidade de instáveis registrada (o R6 viu 19
em duas rodadas). É a prova "antes".

### M1. Ferramenta versionada

TDD dos casos de `compare` listados em Decisions, depois o `capture`.

Validação:

    python3 -m unittest tests.test_journey_pixels -v
    python3 -m unittest discover -s tests -p 'test_*.py'

Esperado: os testes novos passam, e cada um falhou antes pela asserção.

### M2. Chromium do Playwright

1. Criar `tests/requirements-browser.txt`; instalar com ele e
   `python3 -m playwright install chromium`.
2. Criar `tests/journey_browser.py` e trocar as nove aberturas, sem opção de
   renderização ainda (só o equivalente ao modo atual, headless novo).
3. `python3 scripts/journey_pixels.py capture` três vezes e `compare` das três.

Esperado: 7/7 exit 0 em cada rodada; a versão do navegador registrada é a
`159.0.8154.6`; quantidade de instáveis registrada. Se for 0, o M3 só confirma.

### M3. Opções de renderização

O protótipo descrito em Prototypes, se o M2 tiver instáveis. Ao fim, as opções
escolhidas ficam em `tests/journey_browser.py`.

### M4. Prova final, documentação e registros

1. Cinco rodadas seguidas com a árvore final; `compare` das cinco.
2. `docs/desenvolvimento.pt_BR.md` e `docs/desenvolvimento.md`, seção "Verificar
   o navegador" (em inglês, "Check the browser"): preparação com `tests/requirements-browser.txt` e
   `python3 -m playwright install chromium`; remover a exigência de
   `/usr/bin/google-chrome` e de sessão gráfica; como rodar
   `scripts/journey_pixels.py capture` e `compare`; e que atualizar o Playwright
   exige uma prova nova de estabilidade. As duas línguas com o mesmo conteúdo.
3. Registro em `.agent/validation/journey-determinism.md`: versões, linha de base
   do M0, resultado do M2, tabela do protótipo, as cinco rodadas finais e o aceite
   A1 a A6 com o observado. Entrada nova no `EXECPLAN.md` com link para este plano
   e para o registro. Atualizar o `Progress` deste plano.
4. Validação final.

## Progress

- [x] M1 (feito antes do M0, como o M0 permite). `compare` com quatro testes de
  comportamento em `tests/test_journey_pixels.py`, cada um vermelho antes pela
  asserção; `capture` copia só os PNGs de `.agent/tmp/` modificados depois do
  início da rodada e não apaga nada; a versão do navegador vem de
  `tests/journey_browser.py`. `unittest discover`: OK.
- [x] M0 (20/11, Chrome 158.0.8127.36, jornadas da `main`): 3 rodadas, 7/7 exit 0,
  186 capturas em cada; `compare`: `unstable=28`.
- [x] M2 (20/11, Chromium 159.0.8154.6, `channel="chromium"`, headless novo): 3
  rodadas, 7/7 exit 0, 186 capturas; `unstable=31`. `pip install --user` falha
  nesta máquina por PEP 668 (pacotes já estavam nas versões fixadas).
- [ ] M3. **Interrompido antes do commit (regra de Risks).** Tabela, 3 rodadas
  por linha, todas 7/7 exit 0 e 186 capturas:

  | Opções além de `--no-sandbox` | instáveis | ruído de raster |
  | --- | --- | --- |
  | nenhuma (M2) | 31 | 19 |
  | as seis do Prototypes | 11 | 0 |
  | `--disable-gpu` | 27 | 14 |
  | `--disable-partial-raster --disable-skia-runtime-opts` | 11 | 0 |
  | `--disable-partial-raster` | 12 | 0 |
  | `--disable-partial-raster --js-flags=--random-seed=1` | 15 | 0, mais 1 corrida |

  `--disable-partial-raster` ficou em `tests/journey_browser.py`. As instáveis que
  sobram não são raster: ver Lessons learned.
- [x] M3 retomado com a decisão da semente: `SeededBrowser` em
  `tests/journey_browser.py`, teste em `tests/test_journey_browser.py` (vermelho
  pela asserção antes, verde depois).
- [x] M4, itens 1 a 3: cinco rodadas finais com `runs=5 common=186 only_some=0
  unstable=0`, 7/7 exit 0 e `browser=159.0.8154.6` em todas; docs nas duas
  línguas; `.agent/validation/journey-determinism.md` e entrada no `EXECPLAN.md`.
- [x] M4, validação final (20/11, sobre a `main` `9a8c1f0`, depois do #37, que
  trocou os links para repositórios vizinhos por permalinks): `unittest` OK
  (20), `test:sensors` 39/39, `check` PASS, `check:task` PASS com as sete
  jornadas, `git diff --check` exit 0. A primeira tentativa falhou no
  `docs:sensor` só porque esses links não resolviam a partir do worktree.

## Lessons learned

- O plano supunha uma causa só (antialiasing). Há três:
  1. **Ruído de raster** (±1 a 2 níveis, até 64 pixels): resolvido por
     `--disable-partial-raster`.
  2. **Semente aleatória da partida** (diferença até 255 em centenas de pixels):
     `keyboard-retained-*`, `application-*` e `app-*`, capturas da aplicação real
     depois de "Novo Jogo". `Game.kf:87` usa `random.int`, que no navegador chama
     `crypto.getRandomValues` (`kof-runtime.mjs`, `kofRandByte`). Nenhuma opção
     de linha de comando fixa isso; `--js-flags=--random-seed` não tem efeito. Já
     oscilava no Chrome 158 (M0).
  3. **Corrida de tempo rara**: `special-key-release/released-320.png`
     (`tests/browser_weapons.py:611`) saiu uma vez em 21 rodadas com a borda do
     botão "Especial" desenhada; a captura é feita logo após `keyboard.up`.
- A semente foi fixada no próprio `launch` (ver Decisions), sem tocar nas
  jornadas além da abertura.

## Validation

Critérios de aceite. A coluna "Verificação" é o planejado; o observado vai para
`.agent/validation/journey-determinism.md`.

| # | Fonte | Contexto → ação → resultado esperado | Verificação | Evidência esperada |
| --- | --- | --- | --- | --- |
| A1 | issue #35 | árvore final, sem mudança entre rodadas → cinco rodadas → `compare` das cinco com `unstable=0 only_some=0` e o mesmo número de capturas em todas (186, se nenhuma jornada mudou o que grava). Distingue: o M0 mostra a mesma comparação com instáveis no Chrome do sistema | M0 e M4 | saídas do `compare` antes e depois |
| A2 | jornadas atuais | cada rodada → 7/7 exit 0. Distingue: um navegador que desenha diferente quebra as asserções de sprite | `summary` de cada rodada e `npm run check:task` | sumários |
| A3 | Decisions | o navegador aberto é o Chromium do Playwright fixado → a versão registrada pelo `capture` é a `159.0.8154.6` em todas as rodadas; nenhum `tests/*.py` cita `/usr/bin/google-chrome` | sumário do `capture`; `grep -rn google-chrome tests/` vazio | sumário e saída do `grep` |
| A4 | Limites | `git diff main -- 'tests/browser*.py'` só troca as linhas de abertura pelo uso de `tests/journey_browser.py`; nenhuma asserção, espera ou captura muda | ler o diff inteiro | diff no aceite |
| A5 | Decisions | `compare` distingue instável de estável → os testes de comportamento do M1 passam e cada um falhou antes pela asserção | M1 | saída do `unittest` |
| A6 | Limites | `git diff --name-only main` só lista `tests/browser*.py`, `tests/journey_browser.py`, `tests/requirements-browser.txt`, `tests/test_journey_pixels.py`, `scripts/journey_pixels.py`, os dois `docs/desenvolvimento*.md`, `EXECPLAN.md`, `.agent/validation/journey-determinism.md` e este plano; nada de `.agent/tmp/` | `git diff --name-only main` e `git status --porcelain --untracked-files=all` | lista no aceite |

Validação final, nesta ordem. O commit só acontece se todos passarem:

    python3 -m unittest discover -s tests -p 'test_*.py'
    bash -lic 'npm run test:sensors'
    bash -lic 'npm run check'
    bash -lic 'npm run check:task'
    git diff --check

Esperado:

- todos com exit 0;
- `npm run check` com `CHECK: PASS` (`mutation` em SKIP, porque nada de produção
  muda; `docs:sensor` PASS com a documentação nova);
- `npm run check:task` com `CHECK:TASK: PASS` e as sete jornadas em PASS, já no
  Chromium do Playwright.

Obrigações do executor antes de entregar:

- Conferir de novo cada expectativa contra a fonte citada, separado de conferir
  se o comando a demonstra.
- Para cada critério de A1 a A6, registrar o comando, o resultado observado e onde
  está a evidência. Suíte verde sozinha não prova cada critério.
- Registrar antes da entrega qualquer critério não verificado ou falha, sem
  apresentá-los como atendidos. Instáveis que sobrem depois do M3 interrompem a
  entrega antes do commit (ver Risks).
- No relatório final, lembrar que o PR deve fechar a issue #35 (`Closes #35`).
