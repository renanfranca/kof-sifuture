# Prova prática: Kof 0.7.0 testa a UI do SiFuture no navegador a partir de um `.kf`?

Data: 2026-11-07. Somente investigação. Sem worktree, sem subagentes, sem commit nem push.
Original `/home/renanfranca/projects/kof-sifuture` em `e6703db` (branch `sensor-debt-payoff`), não alterado.
Toda execução numa cópia `rsync` em `/tmp/kof-browser-probe.nHw4du` (sem `.git`, `node_modules`, `.agent/tmp`,
`scripts/kof-sensors/target`), fora de pastas com ponto por causa de KofLang/Kof4j#999. Cópia apagada no fim.

## Resposta curta

| Pergunta | Resultado | Como |
|---|---|---|
| P1 `--tag browser` + `kof-test.kofmd` | **Sim**, com ressalva | `browser provider: playwright 1.65.0 (Version 1.65.0)`; **bug**: com caminho nu `shot.kf` o manifesto é ignorado |
| P2 tecla, clique, espera | **Não existe no 0.7.0** | `interact`/`flow`/`assertOn` → `SEM015 Undefined function`; nenhum outro pacote ou comando |
| P3 foto de cena preparada | **Sim**, o Kof faz tudo sozinho | `kof build` via `shell.run` + `withServer` + `app.serveDir` + `browserScreenshot`; 14,5 a 26 s por execução |
| P4 determinismo + mutante | **Sim só com cena parada** | `boss.kf` original: fotos diferentes (14 111 px). Variante parada: 0 px, bytes iguais; mutantes mudam 949 e 883 px; mutante morto num `.kf` com `cmp` |

## Ambiente (executado)

```
$ kof version
kof 0.7.0                                   exit=0
binário: ~/.local/share/kof/kof-0.7.0-linux-x86_64 (VERSION = 0.7.0)
$ google-chrome --version
Google Chrome 155.0.8059.39
node v24.16.0, npm 11.13.0
```

Fontes lidas: AGENTS.md do SiFuture; `kof/training/README.md`; `training/tooling/cli.md`;
`kof/docs/testing-platform.md` §6.1–6.5; `CmdTest.java:125-175` e `:510-529` (`providerProbe`);
`testbrowser.kf`; `KofTestManifest.java`; `testweb.kf`; `docs/stdlib/stdlib-web.md` (`serveDir`).

Atenção à versão: o checkout `/home/renanfranca/projects/kof` está em `22a111f56`
(`kof-0.5.0-beta…-3154`), sem tag 0.7. A autoridade usada foi o jar instalado:

```
$ unzip -p lib/kof.jar dev/kof/testbrowser.kf | diff - kof-compiler/src/main/resources/dev/kof/testbrowser.kf && echo SAME_AS_CHECKOUT
SAME_AS_CHECKOUT
pacotes virtuais no jar: pagination pairs test testbrowser testdb testweb web
```

## P1. Gate do provider (executado)

`kof-test.kofmd`:
```
provider: playwright
version: 1.65.0
```
`shot.kf`:
```kof
import kof.test.browser

test "chrome renders a data page", "browser" {
    var dom = browserContent("data:text/html,<p id=x>ola</p>")
    assert(dom.contains("ola"))
}
```
Provider: pela decisão do usuário, `npm i --no-save playwright@1.65.0` dentro da cópia, porque sem TTY
o `npx` do probe assume `--yes` e baixaria em `~/.npm/_npx`. Antes: `npx --no-install playwright --version` → `Version 1.65.0`, exit 0.

```
$ kof test shot.kf --tag browser          # SEM manifesto (contraprova)
test: browser tests require a provider declared in kof-test.kofmd (add 'provider: playwright' + 'version: <x>') — 0 of 1 files ran
exit=1

$ kof test shot.kf --tag browser          # COM manifesto, caminho nu
test: browser tests require a provider declared in kof-test.kofmd (...) — 0 of 1 files ran
exit=1                                     <- BUG

$ kof test ./shot.kf --tag browser        # COM manifesto
browser provider: playwright 1.65.0 (Version 1.65.0)
SUITE ./shot.kf (1 tests)
kof test: tag 'browser' (1 of 1)
PASS chrome renders a data page
1 passed, 0 failed
levels: e2e: 1 passed / 0 failed
exit=0
(caminho absoluto: idem, wall=8.19s; modo diretório `kof test .`: idem, exit=0)
```

**Bug do Kof 0.7.0 (inferido do código, confirmado na execução):** `CmdTest.java:137` faz
`KofTestManifest.load(dirMode ? src : src.getParent())`. Para o caminho relativo `shot.kf`,
`getParent()` é `null`, e `load(null)` devolve vazio. A mensagem manda declarar um provider que já está
declarado. Contorno: `./arquivo.kf`, caminho absoluto ou diretório. Vale reportar no Kof4j.

## P2. Interação (executado)

O que `kof.test.browser` exporta no 0.7.0 (do jar): só `chromeBinary()`, `browserContent(url)` (Chrome
`--dump-dom`) e `browserScreenshot(url, path)` (Chrome `--screenshot --window-size=1280,800`).
`CompilerTestBrowser.class` só injeta `/dev/kof/testbrowser.kf` no `import kof.test.browser`.

```
$ kof check ./interact.kf --json     # interact("http://127.0.0.1:1/", "css=#game-keyboard", "press=ArrowLeft")
{"success":false,...,"diagnostics":[{"code":"SEM015",...,"line":5,"column":5,"severity":"ERROR","message":"Undefined function: 'interact'"}]}
exit=1
$ kof check ./flow.kf --json         # flow("chromium", url, listOf("css=#game-keyboard :: press=ArrowLeft", "css=#boss-status :: text"))
... "code":"SEM015" ... "message":"Undefined function: 'flow'"          exit=1
$ kof check ./assertOn.kf --json     # assertOn(url, "css=#boss-status", "visible")
... "code":"SEM015" ... "message":"Undefined function: 'assertOn'"      exit=1
$ kof check ./browserPress.kf --json # browser.press("ArrowLeft")
... "code":"SEM011",...,"line":4,"column":13,... "message":"Undefined variable or type: 'browser'"   exit=1
(`kof test … --tag browser` de cada um: o mesmo diagnóstico, "0 passed, 1 failed", exit=1)
```

Observação lateral: para as três funções, o diagnóstico aponta a linha 5 (o `assert`), não a linha 4 da chamada.

Busca por alternativa:
- A lista de comandos do `kof` 0.7.0 (impressa por `kof help`, que responde "unknown: help" e mostra o
  uso) não tem nenhum comando de navegador.
- O jar não tem outro host de teste além de `CompilerTestBrowser/TestDb/TestWeb/Testing`. Nenhuma classe
  de compiler/cli contém `assertOn`/`interact`.
- Essas faces existem só no Java `PlaywrightLibProvider` (SPI sem consumidor Kof). O testing-platform
  §6.5 confirma: "The Kof-facing wiring of THESE faces is the missing middle".
- ❗️ `import kof.browser`, `kof.test.e2e`, `kof.test.ui`, `kof.ui.test`, `kof.playwright`: **todos passam no
  `kof check` sem diagnóstico**, mesmo sem existirem. Um import aceito não prova que o pacote existe.

Conclusão P2: no Kof 0.7.0 um `.kf` não aperta tecla, não clica e não espera elemento. A prova de tecla não
foi executada porque não há o que provar (decisão do usuário: não fazer shell out para Python).

## P3. Foto da cena preparada (executado)

**Quem serve: o próprio Kof.** `kof.test.web.withServer(app, port, body)` sobe `web.app()` com
`app.serveDir("/", webDir)`, espera a porta e fecha no `finally`. O build JS também foi disparado de
dentro do `.kf` via `shell.run`, reproduzindo `scripts/kof_project.py prepared_sources/build`.

```kof
import kof.test.browser
import kof.test.web

Void step(String command, List<String> args) {
    var r = shell.run(command, args)
    if (!shell.ok(r)) { throw command + " failed: " + r.stderr }
}

test "boss scene screenshot run1", "browser" {
    var source = "$P/jssrc-run1"
    var webDir = "$P/out/web-run1"
    var shot = "$P/out/shot-run1.png"
    var t0 = time.now()
    step("rm", listOf("-rf", source, webDir))
    step("mkdir", listOf("-p", source))
    step("cp", listOf("-r", "$SRC/src/main/kof/.", source))
    step("cp", listOf("$SRC/tests/boss.kf", source + "/Main.kf"))
    step("kof", listOf("build", source, "--target", "js", "--output", webDir))
    step("cp", listOf("-r", "$SRC/assets", webDir + "/assets"))
    var t1 = time.now()
    var app = web.app()
    app.serveDir("/", webDir)
    var t2 = time.now()
    var t3 = time.now()
    withServer(app, 18765, (base: String) -> {
        t2 = time.now()
        browserScreenshot(base + "/index.html", shot)
        t3 = time.now()
    })
    println("timing build=" + (t1 - t0) + "ms serve=" + (t2 - t1) + "ms capture=" + (t3 - t2) + "ms")
    assert(shell.ok(shell.run("test", listOf("-s", shot))))
}
```

```
$ /usr/bin/time -f 'wall=%es' kof test ./shot-run1.kf --tag browser
browser provider: playwright 1.65.0 (Version 1.65.0)
kof web connection error: connection closed before headers
timing build=3890ms serve=689ms capture=2520ms
PASS boss scene screenshot run1
time: 16302ms total
wall=18.19s   exit=0
```
PNG 1280×800, 44 455 bytes. Inspeção visual: canvas com chefe, nave, laser e estrelas, e `#boss-status` com
`steps:17` (o jogo andou 17 passos antes da captura). O canvas tem 411 cores, então não é uma imagem vazia.

Tropeços durante a escrita (registrados porque custam tempo a quem for adotar):
- `(String base) -> {}` dá `PARSE012`. A sintaxe certa é `(base: String) -> {}` (`training/language/syntax.md:198`).
- `var t2 = 0` e depois `t2 = time.now()` dão `SEM012 cannot assign Long to Int`.
- ❗️ Uma variável local chamada `web` sombreia o módulo `web`: o `kof check` aceita, e em execução sai
  `java.lang.NoSuchMethodError: 'java.lang.String java.lang.String.app()'`. É uma lacuna de diagnóstico do Kof.
- O aviso `kof web connection error: connection closed before headers` aparece às vezes e não derruba o teste.

Tempos por execução (build JS + servir + captura; o wall inclui JVM do `kof test` + probe `npx`):

| execução | build | servir | captura | `kof test` | wall |
|---|---|---|---|---|---|
| run1 (boss.kf) | 3890 | 689 | 2520 | 16 302 | 18,19 s |
| run2 (boss.kf) | 3556 | 486 | 1517 | 13 874 | 15,89 s |
| v1 (virtual-time) | 3740 | 431 | 2865 | — | 17,17 s |
| v2 (virtual-time) | 3832 | 736 | 3435 | — | 19,54 s |
| s1 (parada) | 4387 | 695 | 7350 | — | 26,18 s |
| s2 (parada) | 3419 | 511 | 6171 | — | 22,37 s |
| m-bg (mutante) | 4637 | 678 | 1942 | — | 19,22 s |
| m-boss (mutante) | 4293 | 494 | 1553 | — | 18,33 s |
| k-orig (cmp, PASS) | 4147 | 387 | 1300 | 12 867 | 14,50 s |
| k-mut (cmp, FAIL) | 3466 | 614 | 1476 | 14 262 | 15,87 s |

(ms quando não indicado; a captura varia de 1,3 a 7,4 s sem causa identificada.)

## P4. Determinismo e mutante (executado)

Comparação por pixels decodificados (PIL `convert("RGB")`, `ImageChops.difference`, contagem de pixels
≠ 0, canvas em `(40,63)-(216,283)`):

```
boss.kf original, run1 × run2 (browserScreenshot):
size=(1280, 800) identical=False diffPixels=14111 canvasDiffPixels=2210 bbox=(33, 97, 293, 676)
boss.kf original, v1 × v2 (chrome --virtual-time-budget=1500 via shell.run):
size=(1280, 800) identical=False diffPixels=13919 canvasDiffPixels=1947 bbox=(33, 97, 293, 676)
```
Diagnóstico com `--dump-dom` (servidor `python3 -m http.server`, só para medir): `budget=none steps:14`,
`1500 → 65 e 63`, `5000 → 201 e 178`. **Com a fixture como está, a foto não é reprodutível**:
`time.interval` + `game.step()` avança um número variável de passos, e o Kof não tem controle de relógio
(o Python usa `page.clock.install/pause_at/run_for`).

**Desvio declarado:** variante só na cópia, `tests/boss-still.kf`, igual a `boss.kf` exceto:
```
192c192,193
<     time.interval(Rules.STEP_MS, () -> { game.step(); refresh(game, drawing, controls, status) })
---
>     prepareBoss(game)
>     time.interval(Rules.STEP_MS, () -> { refresh(game, drawing, controls, status) })
```
(cena "Encounter" parada; o intervalo só redesenha, para as imagens assíncronas aparecerem.)

```
s1 × s2:      identical=True diffPixels=0 canvasDiffPixels=0 bbox=None canvasColors=330
sha256:       s1 = s2 = 0c1bd33ffd2a6318…   (bytes do PNG também iguais)
status:       position:147:steps:0:phase:1:x:120:y:100:...
```

Mutantes manuais em `GameView.kf` (cópia), cada um revertido e conferido com `diff -q` contra o original:
```
100c100  canvas.drawImage(background, x, y)  ->  canvas.drawImage(background, x + 3, y)
  s1 × m-bg:   identical=False diffPixels=949 canvasDiffPixels=949 bbox=(40, 93, 215, 283)   sha 0d746f72…
117c117  ...bossFrames[boss.spriteFrame()], boss.x, boss.y)  ->  ...boss.x + 1, boss.y)
  s1 × m-boss: identical=False diffPixels=883 canvasDiffPixels=883 bbox=(160, 163, 201, 214) sha 9d8ac5e2…
```
Toda a diferença fica dentro do canvas; a do chefe coincide com o sprite em x=120,y=100.

**Mutante morto 100% em Kof:** mesmo teste, mas a asserção final é
`assert(shell.ok(shell.run("cmp", listOf("-s", "$P/out/ref.png", shot))))`, com `ref.png` = s1.
```
original:            PASS boss scene screenshot matches reference k-orig       exit=0   wall=14.50s
boss.x + 1 (117):    FAIL boss scene screenshot matches reference k-mut: assertion failed   exit=1   wall=15.87s
```

## Conclusão

### Executado
- O Kof 0.7.0 roda um teste `.kf` marcado `browser` com o gate do provider playwright (via `./arquivo.kf`).
- Ele faz o build KofJS, serve (`withServer` + `serveDir`) e fotografa (`browserScreenshot`) sem Python.
- Com uma cena **parada**, a foto é reprodutível até no byte, e um mutante de 1 px em `GameView` é morto
  por um `.kf` com `cmp` contra uma referência. Custo medido: **~14,5 a 26 s por mutante por cena** (build
  JS 3,4 a 4,6 s; servir 0,4 a 0,7 s; captura 1,3 a 7,4 s; o resto é JVM do `kof test` + probe `npx`).
- Não há interação (tecla, clique, espera, locator) no 0.7.0.

### Inferido (não executado)
| Alvo | O que dá hoje com Kof puro | O que fica para Python + Playwright |
|---|---|---|
| `GameView` | Mutantes de desenho visíveis numa cena parada: uma fixture parada por cena (chefe, especial, explosão, resultado, menu…), referência PNG por cena. Uma cena não pega mutante de sprite ausente dela (ex.: o chefe `Inactive` em `boss.kf`). | Animação ao longo do tempo (quadros de explosão, avanço de fundo) exige relógio controlado |
| `GameControls` | Só o que aparece na construção: rótulos, estilos e visibilidade iniciais por tela (inclusive via `browserContent` + texto do DOM, mais barato que pixels) | Quase tudo: teclado, foco, pressionar/soltar, `Pausar`, especial (é tratamento de eventos) |
| `ControlsGuide` | Texto e estrutura recolhidos, numa fixture com `game.screen = Screen.Controls` (por DOM ou foto) | `Mais detalhes`/toggle e foco exigem clique ou tecla |

- Custo por mutante = (nº de cenas que o mutante pode afetar) × ~15 a 20 s, porque cada mutante exige um
  build JS novo. Com 10 cenas, ~2,5 a 3,5 min por mutante; em lote, várias cenas poderiam caber num `.kf`
  e num só build se uma fixture expusesse cenas por URL (o `boss.kf` atual usa botões, que o Kof não clica).
- Riscos: as referências PNG valem para esta máquina e este Chrome (155.0.8059.39); outro Chrome, fonte
  ou GPU muda pixels e quebra a referência (provável no CI ubuntu). A captura sem tempo virtual depende
  da cena estar parada. O aviso `kof web connection error` aparece de forma intermitente.
- Para input de verdade hoje: os testes `tests/browser*.py` (Python + Playwright + `page.clock`) seguem
  sendo o único caminho. Pelo Kof, isso depende do "missing middle" do §6.5 (mecanismo (2) recomendado,
  aguardando decisão do mantenedor).

### Achados para reportar ao Kof4j
1. `kof test arquivo.kf --tag browser` ignora `kof-test.kofmd` quando o caminho é relativo sem diretório
   (`CmdTest.java:137`, `src.getParent()` nulo).
2. `import` de pacote inexistente (`kof.browser`, `kof.playwright`…) não gera diagnóstico.
3. Uma variável local `web` sombreia o módulo `web`: o check passa e a execução falha com `NoSuchMethodError`.
4. SEM015 de função inexistente aponta a linha seguinte (o `assert`), não a da chamada.

## Efeitos colaterais e limpeza
- `npm i --no-save playwright@1.65.0` dentro da cópia: o tarball pode ter ido para `~/.npm/_cacache` (cache global do npm).
- `rm -rf /tmp/kof-browser-probe.nHw4du` no fim; `git status --porcelain` do original igual à linha de
  base (5 entradas da outra sessão, antes e depois).
