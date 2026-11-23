# Aceite: prova real do Stop e capturas das jornadas como evidência

Plano: [`.agent/execplans/stop-callback-and-release-capture.md`](../execplans/stop-callback-and-release-capture.md).
Issue #42. Execução em 22/11/2026, a partir de `main` `3c709c2`. Evidência local
(não versionada) em `.agent/tmp/stop-callback-and-release-capture/`.

## Parte 1: Stop com o check novo, por callback real do Codex

`codex exec -m gpt-6-luna -c model_reasoning_effort="high" -C <repo> "<prompt>" < /dev/null`,
`codex-cli 0.171.0`, sessão nova `01a20546-b4d3-7952-94ad-28c82d98cd0e`,
retomada com `codex exec … resume <sessão> "<prompt>"`. Prompts literais no M0
do plano.

Trecho de `.sensors/ledger/01a20546-b4d3-7952-94ad-28c82d98cd0e.stop.log`:

```text
2026-11-22T22:01:16.173Z stop_hook_active=false answer=block
STOP SENSORS: lint PASS · dup PASS · gitleaks PASS · types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN
2026-11-22T22:01:24.811Z stop_hook_active=true answer=continue
STOP SENSORS: lint PASS · dup PASS · gitleaks PASS · types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN
2026-11-22T22:02:01.555Z stop_hook_active=false answer=continue
STOP SENSORS: lint PASS · dup PASS · gitleaks PASS · types:jvm PASS · types:js PASS · tests:jvm PASS · tests:js PASS
```

A resposta do agente no primeiro turno copiou
`src/main/kof/sifuture/probe/Probe.kf:4:5: ERROR SEM021: type mismatch: cannot assign String to 'x: Int'`.
O ledger da sessão tinha só `src/main/kof/sifuture/probe/Probe.kf`. O probe foi
removido em seguida; `git status` sem `probe`.

## Parte 2: issue #42

**Diagnóstico confirmado.** Um script descartável repetiu, em cenas novas da
jornada de armas, `keyboard.down("1")` → `advance` → captura → `keyboard.up("1")`
→ captura, 200 vezes por largura. Com `page.screenshot` direto, a captura da
soltura saiu igual, em pixels, à da tecla mantida em 57/200 (320 px) e 33/200
(1200 px). A captura atrasada é o quadro anterior. As rodadas guardadas de 19/11
já mostravam isso: o `released-320.png` destoante tinha o MD5 do `held-320.png`.

**O caminho da issue não serve.** No Playwright 1.65.2 instalado, o relógio
falso também substitui `requestAnimationFrame`; com o relógio parado das
jornadas, esperar um quadro de animação não termina.

**Tentativa, depois descartada.** Um ajudante que só grava quando duas capturas
seguidas saem iguais zerou o atraso no mesmo script (0/200 e 0/200). Nas oito
rodadas inteiras com ele, todas `exit=0`, `common=186`, `only_some=0`, mas
`unstable=1`: `credits-text-browser/pause-1200.png`. A diferença fica só no
botão ↑, em `:hover` em 3 rodadas e sem `:hover` em 5. O `:hover` vem de um
`tap()` no ↑ no começo de `menu_navigation`, e o Chromium o recalcula em tempo
real, fora do relógio falso.

**Decisão do usuário.** As capturas são evidência para pessoas olharem, não
teste. O visual que importa já é conferido por asserções explícitas nas
jornadas. O ajudante foi descartado sem commit, `scripts/journey_pixels.py` fica
como diagnóstico manual sem promessa, e a #42 é fechada sem correção.

## Critérios

| # | Resultado | Evidência |
| --- | --- | --- |
| A1 | Atendido: `answer=block`, `types:* FAIL`, `tests:* NOT RUN`, erro no caminho completo | log acima |
| A2 | Atendido: `answer=continue`, sete PASS | log acima |
| A3 | Atendido: 57/200 e 33/200 capturas atrasadas | parte 2 |
| A4 | Atendido pelo ajudante (0/200 e 0/200), mas o ajudante foi descartado | parte 2 |
| A5 | **Não atendido**: `unstable=1` (`pause-1200.png`); critério retirado pela mudança de direção | parte 2 |
| A6 | Atendido | validação final |

## Validação final

| Comando | Resultado |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | OK, exit 0 |
| `npm run test:sensors` | 72 de 72, exit 0 |
| `npm run check` | `CHECK: PASS`, `docs:sensor` PASS, mutação SKIP (nada de produção mudou), exit 0 |
| `npm run check:task` | sete jornadas PASS, `CHECK:TASK: PASS`, exit 0, 233 s |
| `git diff --check` | exit 0 |

A6: `git diff --name-only main` lista só `EXECPLAN.md`,
`docs/desenvolvimento.md` e `docs/desenvolvimento.pt_BR.md`; os novos são este
plano e este registro. Nenhum arquivo em `tests/`, `src/`, `scripts/` ou
`.codex/`; nada de `probe`.
