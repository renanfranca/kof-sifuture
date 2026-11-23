# Prova real do Stop com o check novo e captura estável da soltura do Especial

## Purpose and success

Duas pendências pequenas e independentes, num mesmo lote:

1. **Prova real do Stop depois do PR #45.** O PR #45 trocou o tier de tipos do
   Stop (`scripts/stop-verdict.mjs`) pelo check normal do projeto, mas só foi
   provado com uma chamada direta e payload sintético. Depois deste trabalho há
   uma prova por callback real do Codex: um módulo de produção com erro de tipo
   num subpacote que nada importa faz o Stop devolver o turno com
   `types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN`, e o
   mesmo módulo sem o erro deixa terminar.
2. **Issue #42.** A captura `special-key-release/released-320.png`
   (`tests/browser_weapons.py:611`) às vezes sai com a imagem do quadro anterior.
   Depois deste trabalho, as capturas de jornada não dependem de qual quadro o
   navegador já pintou, e uma medição repetida mostra zero capturas atrasadas.

## Context and limits

Fatos medidos no planejamento, em 22/11/2026, `main` `3c709c2`:

- Hooks: `.codex/hooks.json` aponta para `scripts/stop-sensor.mjs` (Stop, 300 s).
  O tier de tipos roda `python3 scripts/kof_project.py check --target jvm|js`,
  cuja entrada importa cada pasta de produção (PR #45). O desenho do Stop e suas
  travas (`stop_hook_active`, deduplicação, teto de três) estão em
  `.agent/execplans/codex-sensor-hooks.md` e em `docs/desenvolvimento.pt_BR.md`,
  seção dos hooks. O M3 desse plano provou o Stop por `codex exec`, sessão nova,
  `< /dev/null`, com evidência em `.agent/tmp/codex-sensor-hooks/m3/` e o log da
  sessão em `.sensors/ledger/<sessão>.stop.log`.
- Lição registrada no plano dos hooks: um prompt de `codex exec` nunca pode ser
  aberto como "termine"; ele diz exatamente o que fazer.
- Issue #42: o trecho é

      page.keyboard.up("1")
      assert special.is_disabled()
      assert special_presentation(special) == presentation
      page.screenshot(path=str(release_evidence / f"released-{width}.png"), full_page=True)

  O estado do DOM já está certo quando a captura começa.
- Evidência guardada em `.agent/tmp/debt-fixtures/*/png/special-key-release/`,
  de 19/11: em sete rodadas `released-320.png` tem MD5 `d923ac3f…`; na rodada
  `m1old-b` tem `6ce84de9…`, **o mesmo MD5 do `held-320.png` de oito rodadas**.
  Ou seja, a captura atrasada é a imagem do quadro de antes do `keyboard.up`. Não
  é um desenho novo e parcial.
- Todas as jornadas instalam o relógio falso do Playwright
  (`page.clock.install` e `page.clock.pause_at`, por exemplo
  `tests/browser_weapons.py:86-87`) e avançam o tempo com
  `page.clock.run_for(steps * 30)` (`advance`). No Playwright 1.65.2 instalado
  (`~/.local/lib/python3.14/site-packages/playwright/driver/package/lib/coreBundle.js`),
  o relógio falso substitui também `requestAnimationFrame`
  (`requestAnimationFrame: (callback) => clock.addTimer({ type: "AnimationFrame" …`).
  **Consequência: o caminho proposto na issue (dois `requestAnimationFrame` via
  `page.evaluate`) não resolve.** Com o relógio parado, o callback só roda
  quando a jornada avança o tempo, e avançar o tempo muda o estado do jogo (a
  recarga do Especial, por exemplo).
- Há 62 chamadas `page.screenshot` em `tests/*.py`. `tests/journey_browser.py`
  é o módulo comum das jornadas (`launch`, `SeededBrowser`).
- `scripts/journey_pixels.py capture <pasta>` roda todas as jornadas e copia as
  capturas; `compare <pastas…>` compara os pixels RGB e sai com 1 se alguma
  captura comum diferir (`unstable`).
- Testes: `tests/test_journey_browser.py` cobre o módulo comum, rodado por
  `python3 -m unittest discover -s tests -p 'test_*.py'`.

### Limites

- Não mudar `src/`, os testes Kof, as fixtures `tests/*.kf`, `kof-mut.json`, os
  limites dos sensores, `.codex/hooks.json` nem os scripts dos hooks. A parte 1
  só observa e registra.
- Não mudar o que cada jornada assere nem quando captura: a correção muda só como
  a captura espera a pintura.
- Probes no checkout só durante a parte 1, removidos ao fim dela e nunca
  commitados.

## Decisions

**Mudança de direção em 22/11/2026, decidida pelo usuário depois do M3:** as
capturas das jornadas são evidência para pessoas olharem, não teste. O que
importa na tela já é conferido por asserções explícitas nas jornadas
(`sprite_matches`, `background_matches`, caixas, opacidade, texto). Perseguir
pixels idênticos entre rodadas é lutar contra o navegador (semente, raster,
quadro atrasado, `:hover`), não contra o código do projeto. Consequências: o
ajudante `settled_screenshot` e as 56 trocas nas jornadas foram descartados
sem commit; `scripts/journey_pixels.py` fica como ferramenta manual de
diagnóstico, sem promessa de estabilidade, e a documentação deixa de exigir
"cinco rodadas com `unstable=0`" ao atualizar o Playwright; a #42 é fechada
sem correção, com essa explicação. As decisões abaixo sobre a parte 2 ficam
como histórico do que foi tentado.


**Parte 1 roda só no contexto `codex exec`.** O PR #45 mudou o comando interno do
tier de tipos, não o payload nem o manifesto. O payload e a entrega já foram
provados nos três contextos no M0 e no M3 do plano dos hooks. Uma sessão real
por `codex exec`, rodada pelo executor, basta para provar o caminho novo.

**Parte 2: esperar a pintura sem o relógio da página.** A correção fica num
ajudante de `tests/journey_browser.py`, usado pelas capturas de jornada. A
técnica não pode depender de `requestAnimationFrame`, `setTimeout` nem de outro
timer da página, porque o relógio falso os controla. A escolha da técnica fica
para o M2, depois do diagnóstico do M1. Candidatas, nesta ordem de preferência:

- (a) capturar até duas imagens seguidas saírem iguais, com teto de tentativas e
  erro claro ao estourar;
- (b) um mecanismo do navegador, fora do relógio falso, que espere um quadro
  novo, por exemplo pelo CDP. Só vale se o M1 mostrar que funciona com o relógio
  parado.

Se o M1 refutar o diagnóstico (a captura atrasada não é o quadro anterior),
**parar e me consultar** antes do M2.

**O ajudante cobre todas as capturas, não só a `released-320`.** O padrão
"evento e logo depois captura" se repete nas jornadas, e uma regra só é mais
simples que trocar casos isolados.

## Risks

- A taxa observada é baixa (1 em 21 rodadas inteiras). Por isso o M1 mede com uma
  repetição dirigida do passo, e não só com rodadas inteiras.
- A opção (a) pode deixar as jornadas mais lentas. Medir o tempo de
  `npm run check:task` antes e depois e registrar.
- Na parte 1, o worktree vai ter a branch e o plano ainda não commitados. Como o
  agente edita o probe, o escopo do Stop é ledger ∩ sujos, e o tipo checa o
  projeto inteiro. Registrar o escopo observado.

## Milestones

### M0. Prova real do Stop por `codex exec` (parte 1)

Antes de qualquer mudança da parte 2. Uma sessão nova, Luna `high`, com
`< /dev/null`. Anotar o instante de início e o `session_id`.

1. Primeiro prompt, literal:
   "Crie src/main/kof/sifuture/probe/Probe.kf com exatamente estas linhas:
   `package sifuture.probe`, uma linha vazia, `probe() {`, `    Int x = \"texto\"`,
   `}`. Não rode nenhum check nem teste. Se um hook devolver o turno com
   achados, copie literalmente a primeira linha que começa com STOP SENSORS e a
   linha de ERROR na sua resposta, e depois pare sem corrigir nada."
2. Esperado: Stop com `stop_hook_active=false` e `answer=block`;
   `lint PASS · dup PASS · gitleaks PASS · types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN`;
   `src/main/kof/sifuture/probe/Probe.kf:4:5: ERROR SEM021`; o Stop seguinte
   (`stop_hook_active=true`) só reporta. Distingue: antes do PR #45, sem a
   entrada própria do Stop, o mesmo arquivo dava `types:jvm PASS`.
3. `codex exec resume` com o prompt literal:
   "Troque a linha `Int x = \"texto\"` por `Int x = 7` em
   src/main/kof/sifuture/probe/Probe.kf. Não rode nenhum check nem teste."
4. Esperado: `answer=continue`, os sete passos PASS. Distingue: separa "o check
   vê o módulo" de "o Stop reprova qualquer arquivo novo".
5. Remover `src/main/kof/sifuture/probe/` e conferir `git status` sem `probe`.

Evidência: o `.stop.log` da sessão e as saídas do `codex exec`, copiados para
`.agent/tmp/stop-callback-and-release-capture/m0/`. Se o Stop não disparar ou os
hooks aparecerem como não aprovados, parar e me avisar. A aprovação em `/hooks` é
minha.

### M1. Diagnóstico da captura atrasada (parte 2)

Um script descartável em `.agent/tmp/stop-callback-and-release-capture/m1/`
repete, na mesma página e com o mesmo relógio falso da jornada, o passo
`keyboard.down("1")` → `advance` → captura (held) → `keyboard.up("1")` → captura
(released) → `advance(page, 170)`, pelo menos 200 vezes por largura (320 e
1200). Para cada repetição, registrar se a captura `released` é igual, em pixels,
à `held` da mesma repetição.

Esperado, pela evidência guardada: algumas `released` iguais à `held` (captura
atrasada). Registrar a taxa. Se nenhuma sair atrasada em 200 repetições,
aumentar para 1.000. Se ainda assim nenhuma sair, registrar e me consultar.

Também medir, no mesmo script, se a candidata (b) funciona com o relógio parado.
A candidata (a) se mede no M2.

### M2. Ajudante de captura, por TDD (parte 2)

- Teste em `tests/test_journey_browser.py` para o ajudante, pelo comportamento
  observável. Com uma página falsa cujas capturas devolvem uma sequência de
  imagens, o ajudante só grava quando a imagem estabiliza, e falha com mensagem
  clara quando não estabiliza dentro do teto. O teste fica vermelho antes do
  ajudante existir. Se a técnica escolhida for a (b), adaptar o teste ao
  contrato dela.
- Ajudante em `tests/journey_browser.py`. Trocar as chamadas `page.screenshot`
  de captura de evidência nas jornadas por ele, sem mudar argumentos, caminhos
  nem a ordem das asserções.
- Repetir o script do M1 usando o ajudante: **zero** `released` iguais à `held`
  no mesmo número de repetições. Distingue: no M1, o mesmo script com
  `page.screenshot` direto tinha capturas atrasadas.

### M3. Rodadas inteiras, documentação e registros

- Oito rodadas `python3 scripts/journey_pixels.py capture .agent/tmp/stop-callback-and-release-capture/runs/<n>`
  (n de 1 a 8), depois `compare` das oito. Esperado: todas as jornadas com
  `exit=0`, `only_some=0` e `unstable=0`.
- Documentação: o trecho de determinismo das jornadas em
  `docs/desenvolvimento.pt_BR.md` e `docs/desenvolvimento.md` (procurar onde o PR
  #41 descreveu semente e `--disable-partial-raster`) passa a citar a espera pela
  pintura e o motivo de não usar `requestAnimationFrame`.
- Registro em `.agent/validation/stop-callback-and-release-capture.md`, com M0, a
  taxa do M1 antes e depois, as oito rodadas, os tempos e o aceite A1 a A6.
  Entrada no `EXECPLAN.md`. O PR fecha a #42 (`Closes #42`).

## Progress

- [x] M0. Prova real do Stop por `codex exec` (22/11/2026). Sessão
  `01a20546-b4d3-7952-94ad-28c82d98cd0e`, Luna `high`, `codex-cli 0.171.0`.
  Primeiro Stop 22:01:16Z `stop_hook_active=false answer=block` com
  `lint PASS · dup PASS · gitleaks PASS · types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN`
  e `src/main/kof/sifuture/probe/Probe.kf:4:5: ERROR SEM021`; o seguinte
  (`true`) só reportou. Depois de `Int x = 7`, 22:02:01Z `answer=continue` com
  os sete PASS. Probe removido. Evidência em
  `.agent/tmp/stop-callback-and-release-capture/m0/`.
- [x] M1. Diagnóstico confirmado. Com `page.screenshot` direto, 200 repetições
  por largura: `released` igual à `held` em 57/200 (320) e 33/200 (1200). Com
  duas capturas iguais seguidas (protótipo): 0/200 e 0/200, um único resultado
  por largura. A candidata (b) não foi medida, porque a (a) bastou.
- [x] M2. Feito e depois descartado. `settled_screenshot` em
  `tests/journey_browser.py` com dois testes, 56 capturas trocadas; o script do
  M1 com o ajudante deu 0/200 e 0/200.
- [x] M3. Oito rodadas com o ajudante: todas `exit=0`, `common=186`,
  `only_some=0`, mas `unstable=1`: `credits-text-browser/pause-1200.png`
  (`tests/browser.py:307`), só no botão ↑ (56x56 em 536,288, até 18 níveis):
  `:hover` em 3 rodadas, sem `:hover` em 5; nas rodadas de 19/11, sempre com
  `:hover`. Uma linha do tempo de 1,5 s na captura mostra o estado parado em
  cada rodada: não é quadro atrasado. O `:hover` vem do `tap()` no ↑ no início
  de `menu_navigation`, e o Chromium o recalcula em tempo real, fora do relógio
  falso; mais capturas deram mais tempo para isso. Com isso o usuário decidiu a
  mudança de direção (Decisions). Entregue: documentação nas duas línguas
  dizendo que as capturas são evidência e que `journey_pixels.py` é
  diagnóstico manual; registro do M0 e da tentativa em
  `.agent/validation/stop-callback-and-release-capture.md`; entrada no
  `EXECPLAN.md`.

## Validation

Critérios de aceite. "Verificação" é o planejado; o observado vai para
`.agent/validation/stop-callback-and-release-capture.md`.

| # | Fonte | Contexto → ação → resultado esperado | Verificação | Evidência esperada |
| --- | --- | --- | --- | --- |
| A1 | PR #45, Decisions dos hooks | sessão real `codex exec` cria um módulo com erro de tipo num subpacote novo → Stop `answer=block` com `types:* FAIL`, `tests:* NOT RUN` e `Probe.kf:4:5: ERROR SEM021` no caminho completo. Distingue: antes do #45 o tipo dava PASS | M0, passos 1 e 2 | `.stop.log` e saída do `codex exec` |
| A2 | mesmo | mesmo módulo sem erro → `answer=continue`, sete PASS | M0, passos 3 e 4 | `.stop.log` |
| A3 | issue #42 | a captura atrasada é o quadro anterior: no passo repetido, `released` igual à `held` numa taxa maior que zero, com `page.screenshot` direto | M1 | taxa e contagem |
| A4 (descartado) | issue #42 | com o ajudante, o mesmo passo repetido dá zero `released` iguais à `held`. Distingue: A3 mostrou que o script detecta o atraso | M2 | contagem |
| A5 (descartado) | issue #42 | oito rodadas inteiras: `only_some=0`, `unstable=0`, todas `exit=0` | M3 | saída do `compare` e `summary.txt` |
| A6 | Limites e mudança de direção | `git diff --name-only main` só com este plano, o registro, `EXECPLAN.md` e os dois `docs/desenvolvimento*.md`; nada de `probe` no `git status` | `git diff --name-only main`; ler o diff das jornadas | lista e trecho do diff no registro |

Validação final, nesta ordem. O commit só acontece se todos passarem:

    python3 -m unittest discover -s tests -p 'test_*.py'
    npm run test:sensors
    npm run check
    npm run check:task
    git diff --check

Esperado: todos com exit 0; `CHECK: PASS` com mutação SKIP (nada de produção
muda); `CHECK:TASK: PASS` com as sete jornadas. Registrar o tempo do
`check:task` e comparar com o de antes do M2.

Obrigações do executor antes de entregar:

- Conferir de novo cada expectativa contra a fonte citada (issue #42, a evidência
  em `.agent/tmp/debt-fixtures/`, o relógio do Playwright instalado e o desenho
  do Stop), separado de conferir se o teste a demonstra.
- Para cada critério de A1 a A6, registrar o comando, o resultado observado e
  onde está a evidência. Suíte verde sozinha não prova cada critério.
- Registrar qualquer critério não verificado ou falha, sem apresentá-los como
  atendidos.
