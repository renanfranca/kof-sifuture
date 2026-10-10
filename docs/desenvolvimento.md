<a id="desenvolvimento"></a>

# Development

[English](desenvolvimento.md) | [Português (Brasil) — pt-BR](desenvolvimento.pt_BR.md)

[Back to the project overview](../README.md) ·
[How to play](jogar.md) ·
[Expected behavior](regras-do-jogo.md) ·
[CI and publishing](ci-e-publicacao.md)

This guide covers requirements, local commands, and how temporary source
preparation works. Run the recipes from the SiFuture checkout root.

<a id="requisitos"></a>

## Requirements

Use Python 3 and a Kof installation available on `PATH`. Check it with:

```bash
kof version
```

The environment examined on 2026-10-09 reports `kof 0.5.0-beta`, Linux
x86_64, Eclipse Adoptium 25.0.4.1, and an embedded JDK. The version identifies
the distribution; it does not identify its source commit by itself. The Kof
checkout consulted for language sources is
`317d9f6b1c3e27032cc955a05f859f6c627d9338`; we do not assume this SHA is
metadata for the installation on `PATH`. Previous results remain in
[EXECPLAN.md](../EXECPLAN.md) and the validation records.

The [installation training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/distribution/install.md#L13)
describes the package:

> The official package contains: compiler, CLI, runtime, stdlib, tooling, editor
> support, embedded OpenJDK and documentation.

The official package includes the JVM required by its launcher. A Kof source
checkout is useful for consulting implementation and documentation; it is not
required to compile this game. To obtain and verify the same distribution used
by a CI run, follow the [reproduction recipe](ci-e-publicacao.md#reproduce-a-distribution).

<a id="compilador-escolhido"></a>

## Choosing a compiler

`--kof CAMINHO` takes precedence over the `KOF` environment variable, followed
by `kof` from `PATH`. The [canonical script](../scripts/kof_project.py#L30)
expresses that order:

```python
def kof_executable(override=None):
    return override or os.environ.get("KOF") or shutil.which("kof") or "kof"
```

The first available value wins. Pass `--kof /path/to/kof` to `build` or
`test` to select it explicitly. If `KOF` is still set from an earlier
procedure, run `unset KOF` to return to the `PATH` version.

<a id="compilar-e-abrir-a-aplicação"></a>

## Build and open the app

`build --output` takes the directory for the completed site:

```bash
python3 scripts/kof_project.py build --output /tmp/sifuture-game
python3 -m http.server 8766 --directory /tmp/sifuture-game
```

After a successful build, visit `http://127.0.0.1:8766/`. An HTTP server is
needed because the page loads JS modules and sprites from `assets/`. Stop it
with `Ctrl+C`. Use the [gameplay journey](jogar.md#start-a-game) to check the
opening, movement, pause, and return flow.

[Learn Kof JS](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/37-kofjs.md#L54)
describes the output:

> `kof build --target=js` generates `index.html` + modules: serve the
> folder as a static web application (any HTTP server).

The wrapper produces that set and copies the game's assets. A successful
compile does not prove graphical presentation or browser controls; those are
separate checks.

<a id="executar-os-testes-de-regras"></a>

## Run the rules tests

A **suite** is a file containing test cases that exercise behavior. Canonical
Kof suites live in `src/test/kof`; currently
[GameJourney.kf](../src/test/kof/sifuture/game/GameJourney.kf) uses the real
implementation in `src/main/kof`.

```bash
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 scripts/kof_project.py test --target jvm --suite sifuture/game/GameJourney.kf
```

At examined revision `e38f5e0ccb98bfd443a0d57833b6be0b6bed6aee`, each full
run should report 114 passing tests. That count belongs to that revision;
additional cases can increase it. Text and geometry are checked in the
browser. `--suite` selects a file relative to the test root. Without it, the
wrapper recursively finds `.kf` files and runs them in path order, using a new
temporary tree for each suite. A failure does not stop later suites; the
command returns the first failure observed. In
[scripts/kof_project.py](../scripts/kof_project.py#L146):

```python
first_failure = 0
for path in suites:
    print(f"Suite: {path.relative_to(tests)}", flush=True)
    with prepared_sources(suite=path, root=root) as source:
        code = _run([str(kof_executable(kof)), "test", str(source / "Main.kf"), "--target", target])
        if code and not first_failure:
            first_failure = code
return first_failure
```

Each call uses the official runner. [Learn Kof: Testing](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/23-testing.md#L42)
teaches:

> Each test runs **in isolation** (one failing does not interrupt the others).

That rule applies to cases within one Kof invocation; the Python loop also
keeps files independent. The [CLI training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/tooling/cli.md)
documents `kof test` and `--target`; the wrapper prepares sources before
calling that tool.

**Preserved teaching experiment:** temporarily change `SHIP_SPEED` from `5`
to `4` in a validation copy of `Rules.kf`, observe the movement test fail,
then restore `5`. [EXECPLAN.md](../EXECPLAN.md) records this type of proof;
this guide does not claim that the experiment was rerun. A controlled change
that makes the test fail demonstrates that the test observes the expected
speed, beyond merely accepting a process that exits without error.

<a id="raiz-de-fontes-e-workaround"></a>

## Source root and workaround

A **workaround** is a temporary detour around a tool limitation. A **source
root** is the directory from which packages and imports locate files. This
project keeps the app in `src/main/kof`, tests in `src/test/kof`, and
[kof.toml](../kof.toml) at the root with `name = "sifuture"`.

[Learn Kof: Packages and Modules](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/19-packages-and-modules.md#L25)
shows file and directory imports. The [module reference](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/docs/language-reference/modules.md#L18)
defines:

> Kof's "module" is the **root directory** passed to the compiler (module root),
> used to expand directory imports.

So `import sifuture.game.GameJourney` finds the suite relative to the prepared
root; the suite itself imports `sifuture.game.*` to reach the rules.

**Build/source-root WORKAROUND:** with the examined 0.5.0-beta installation,
project commands prepare a disposable tree outside the checkout and without
an ancestor `kof.toml`. They copy canonical source bytes, generate a small
import entry, and invoke the official CLI. The build includes only the app,
with entry `import sifuture.*`. Each suite receives the app and only its own
test file, with a specific entry. The tree is removed after the command,
including on failure. There is no need to prepare sources or assets by hand.

The wrapper checks for `index.html` and `Default.mjs` before copying output
and assets to `--output`. In [build](../scripts/kof_project.py#L109):

```python
if code:
    return code
missing = [item for item in ("index.html", "Default.mjs") if not (web / item).is_file()]
if missing:
    raise PreparationError(f"Kof build returned success without required artifacts: {', '.join(missing)}")
_publish(web, output)
```

This catches a zero exit status without compiled output. The [workaround
training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/anti-patterns/runtime-workarounds.md#L9)
explains why this preparation is not a language rule:

> The detour is legitimate — but it is **not an idiom**.

The [source investigation](../.agent/specifications/reorganizar-fontes-e-testes-kof.md)
preserves reproducers run on JVM/JS. In that snapshot's distribution, a direct
build could report `no .kf/.kof files found`, return zero, and produce no
module. Tests with an unsuitable root failed with `PKG004`; an unresolved
import showed `PKG006`. These are tool results from that revision, not syntax
restrictions on packages.

<a id="diagnosticar-tmpdir"></a>

### Diagnose TMPDIR

If an error mentions `TMPDIR` or an ancestor `kof.toml`, choose a temporary
directory outside any Kof project and retry. The [script](../scripts/kof_project.py#L34)
refuses preparation inside the project or beneath an ancestor manifest:

```python
if directory == project or project in directory.parents:
    raise PreparationError("temporary source is inside the project; set TMPDIR outside the project")
if any((ancestor / "kof.toml").exists() for ancestor in (directory, *directory.parents)):
    raise PreparationError("temporary source has an ancestral kof.toml; set TMPDIR outside a Kof project")
```

A manifest above the prepared tree can change which root resolves imports.
Preparing in a checkout subdirectory does not provide the same conditions as
an external tree.

<a id="evolução-da-issue-kof-708"></a>

### Kof issue #708 status

[Kof issue #708](https://github.com/KofLang/Kof4j/issues/708) is closed. Its
history records `moduleRoot`, test-root, and explicit no-source-failure fixes
in `lab`, followed by a two-root interface. Decision
[D-CLI-SOURCE-ROOTS](https://github.com/KofLang/Kof4j/blob/0e6a02f23d295d89e2ce4975b6d8b177240f5222/docs/development/DECISIONS.md#L4528)
in commit `0e6a02f23d295d89e2ce4975b6d8b177240f5222` says:

> **State:** DECIDED (maintainer) + IMPLEMENTED (30/09) — tracker `#708` (case `renanfranca`/SiFuture #2).

The [upstream test](https://github.com/KofLang/Kof4j/blob/0e6a02f23d295d89e2ce4975b6d8b177240f5222/kof-cli/src/test/java/dev/kof/cli/TwoRootsCliE2ETest.java#L45)
declares this in its test project manifest:

```toml
[sources]
app = "src/main/kof"
test = "src/test/kof"
```

This excerpt is from upstream test configuration, not configuration already
applied to SiFuture. The test calls `kof build`/`kof test` without a positional
argument and verifies JVM, Native, and JS targets. That upstream test was
consulted, not run in this documentation update. The consulted local Kof
checkout remains at `317d9f6`; it did not have the newer object, which was
read from the fixed public revision above.

The game's current manifest still does not declare `[sources]`. These recipes
keep the preparation proven with the examined installation. Migrating this
flow requires checking a distribution with the new support and validating
builds, tests, and browser entry points before removing the wrapper; this
documentation update does not perform that migration. Checking produced
artifacts remains necessary after any compiler update.

<a id="modelo-desenho-e-controles"></a>

## Model, drawing, and controls

The **model** is the state and rules that change on each logical step.
**Drawing** reads that state to present the scene. **Controls** translate
player input into model commands. In [Main.kf](../src/main/kof/sifuture/Main.kf#L15):

```kof
time.interval(Rules.STEP_MS, () -> {
    game.step()
    drawing.render(game)
    controls.update()
})
```

`step()` advances state before `render()`. Redrawing without `step()` does not
advance the game. `Event.key()` and `Event.target()` distinguish the key and
its source in the control tree; styles and widgets are created once and
reused. Current geometry and focus rules are in the [gameplay guide](jogar.md);
[typography](../fonts/README.md) has its own owner.

The [UI training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/language/ui.md#L73)
and [Learn Kof: UI](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/35-kof-ui.md#L5)
define the drawing target:

> On the other targets the
> handles are no-ops — the program runs without rendering.

In JS, [kofUiCanvasNew](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/js/JsRuntimeUiWidgets.java#L384)
creates the surface:

```javascript
export function kofUiCanvasNew(w, h) {
    if (typeof document === "undefined") return -1;
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
```

This JavaScript excerpt is Kof runtime code, not hand-written application
code. It requires a browser document. The [JVM implementation](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/jvm/JvmRuntimeUi.java#L472)
returns only an identifier from the same constructor:

```java
public static int kof_ui_canvas_new(int width, int height) {
    return 1;
}
```

The [Native implementation](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/runtime/RuntimeUi.java#L536)
also returns a handle without creating a surface. Decision
[D-UI-SCOPE](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/docs/development/DECISIONS.md#L1675)
defines this scope. Compiling or testing rules on JVM/JS does not demonstrate
a graphical window on the other targets.

<a id="organização-do-código"></a>

## Code organization

| Path | Responsibility |
| --- | --- |
| [Main.kf](../src/main/kof/sifuture/Main.kf) | Creates the window and schedules the clock. |
| [Game.kf](../src/main/kof/sifuture/game/Game.kf) | Coordinates each logical step, screens, collisions, stage, and score. |
| [Ship.kf](../src/main/kof/sifuture/game/Ship.kf) | Movement, explosion, restart, and ship frame. |
| [Weapons.kf](../src/main/kof/sifuture/game/Weapons.kf) | Level, charges, rate, and projectiles; Lasers, Shot, and other classes own their states. |
| [Meteor.kf](../src/main/kof/sifuture/game/Meteor.kf) | Meteor positions, counters, movement, and frames. |
| [Rules.kf](../src/main/kof/sifuture/game/Rules.kf) | Limits, durations, intervals, and initial random range. |
| [State.kf](../src/main/kof/sifuture/game/State.kf) | Screen types, states, and directions. |
| [GameView.kf](../src/main/kof/sifuture/GameView.kf) | Draws screens by reading the model. |
| [GameControls.kf](../src/main/kof/sifuture/GameControls.kf) and [ControlsGuide.kf](../src/main/kof/sifuture/ControlsGuide.kf) | Build controls, focus, and the in-game guide. |

<a id="entrada-no-menu-e-apresentação-do-guia"></a>

### Menu entry and guide presentation

Each real arrival at the menu creates a new animated ship entrance. It starts
at `x = -30`, moves forward ten units per logical step with thrust, then brakes
backward by three to `x = 18`. The normal sprite begins during braking.
Remaining in the menu or redrawing does not restart the sequence; selecting
and confirming remain possible during entry. Returning from Controls keeps the
selection; pause and results return with New Game selected. In
[MenuEntrance.advance](../src/main/kof/sifuture/game/MenuEntrance.kf#L12):

```kof
if (phase == MenuEntrancePhase.Entry) {
    if (x < 80) { x = x + 10; return }
    x = x + 10
    phase = MenuEntrancePhase.Braking
}
x = x - 3
if (x <= 18) { finish() }
```

Only updates advance these values. The [typography guide](../fonts/README.md)
owns text, colors, margins, and credits animation, including its six-second
wait and the empty frame before the menu.

The [Controls panel](../src/main/kof/sifuture/ControlsGuide.kf#L19) is 248
pixels wide, with 16-pixel internal margins and 216 pixels of content,
14-pixel sans-serif text, 20-pixel line spacing, and 16-pixel headings. Its
44-pixel header replaces the drawing area; the directional pad and Special
are collapsed. The Special section precedes More details. The window follows
its content and has no fixed footer instruction. The [panel commands](jogar.md)
and [presentation evidence](../.agent/validation/controls-guide.md) follow the
same rules; this guide does not duplicate their recipes.

<a id="classes-e-estados-em-kof"></a>

### Classes and states in Kof

A **mutable class** has fields that change during play. An **enum** represents
a closed set of states or directions, allowing values of the same type to be
compared. [State.kf](../src/main/kof/sifuture/game/State.kf#L3) uses, for example:

```kof
enum Screen { Credits, Menu, Controls, Play, Pause, Result }
enum ShipPhase { Normal, Explosion, Restart, Hidden }
enum Direction { Left, Right, Up, Down }
```

`Ship.lastX` and `Ship.lastY` store the most recently pressed direction as a
`Direction`, choosing between opposing arrows. `ship.phase` is an explicit
class field. The [class idiom](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/idioms/classes.md#L45)
teaches fields and constructors for this state; [Learn Kof 07](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/07-classes-and-objects.md#L65)
explains the difference from immutable data.

There is a documentation discrepancy in the consulted snapshot. The [type
training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/language/types.md#L106)
still says:

> Runtime representation: the constant name itself (String-backed).

The [class reference](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/docs/language-reference/classes.md#L149)
says:

> **An enum value is a real instance (D-ENUM207, issue #207)**

[EnumIdentityE2ETest](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/test/java/dev/kof/compiler/EnumIdentityE2ETest.java#L69)
confirms comparisons between values of the same enum. The game's journeys
also exercise these comparisons on JVM and JS; this guide does not teach the
older string description as current behavior.

<a id="semente"></a>

### Seed

A **seed** initializes a pseudo-random number sequence. `Game.start(seed)`
calls `rng.seed(seed)` to repeat games in tests; normal play chooses a
variable seed with `random.int(...)`. **Preserved teaching experiment:**
change the seed passed to `Game.start()` in a test and compare starting
positions; repeating the same seed repeats the sequence. This is guidance,
not a new run claimed here.

<a id="verificar-o-navegador"></a>

## Check the browser

A **fixture** is a test entry that prepares a deterministic situation using
the real model, drawing, and controls.

Install Python Playwright and Pillow. Current scripts open graphical Chrome at
`/usr/bin/google-chrome`; that executable and an available graphical session
are required. Installing only the Playwright package does not guarantee
these conditions.

```bash
python3 tests/browser.py
python3 tests/browser_controls.py
python3 tests/browser_meteor.py
python3 tests/browser_weapons.py
python3 tests/browser_stage.py
python3 tests/browser_subchief.py
python3 tests/browser_boss.py
```

Each script compiles, serves on an available port at `127.0.0.1`, then cleans
up the browser, server, and temporary files. The app and fixtures are Kof. Kof
generates the JavaScript and CSS output. Playwright sends interactions and
Pillow checks sprites.

`python3 tests/browser.py URL` accepts an already served app. Scripts that
offer `--kof CAMINHO` keep that option: `browser.py`, `browser_controls.py`,
`browser_meteor.py`, and `browser_weapons.py`.

| Journey | Coverage |
| --- | --- |
| `browser.py` | Normal app at 320/1200 px: credits, wait/skip/empty frame, menu entry, text, closed/open guide, focus, keyboard, click/touch, and pause; captures at densities 1/2. Defeat, result, and new game use a fixture with three deterministic collisions. |
| `browser_controls.py` | Fresh contexts with 30 ms cycles: position, sprites, four diagonals, opposites, focus, click/Tab, release, and button/contact identity. |
| `browser_meteor.py` | Real-model fixture with one step per click: position and frames of a hit meteor. |
| `browser_weapons.py` | Pixels for items, effects, lasers, blaster, and all nine special frames; life 4, indicator, pause, held keys, rejected attempts, cancellation, and release order. Also opens the normal app. |
| `browser_stage.py` | Route, indicators, sprites, full journey, result, and redraws without advancing. |
| `browser_subchief.py` | Encounter, attacks, special, explosion, pause/resume, and repeat play. |
| `browser_boss.py` | Entry, levels, attacks, contacts, explosion, results, and repeat play. |

Waiting for a spontaneous defeat is not deterministic: life pickups and
upgrades can extend a run. Three prepared collisions let the scripts check
ending and both result confirmations. Redraws without advancement check the
separation between model and presentation.

Python automation can be checked with:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

The local publishing-infrastructure contract is in the [CI guide](ci-e-publicacao.md#local-infrastructure-checks).

<a id="o-que-as-verificações-demonstram"></a>

## What the checks demonstrate

The [controls record](../.agent/validation/sifuture-controls.md) associates
checkpoint `cedf4875abe101d8fd85012dbfb30ef20bf5406c` with a gate of 114 tests
per target, eight Python tests, seven complete browser journeys, and the CI
contract. The journeys exercised JS in Chrome 155.0.8059.39; Vivaldi
8.2.4133.84 had specific presentation and navigation checks, but did not run
all seven journeys. The record also distinguishes the user's manual “Resolved”
report from an automated Windows control.

The [stage records](../.agent/validation/stage-hud-result.md), [weapons](../.agent/validation/background-items-weapons.md), [special-key release](../.agent/validation/special-key-release.md), [sprite restart](../.agent/validation/ship-meteor-reset.md), and [credits and guide](../.agent/validation/controls-guide.md)
preserve earlier evidence and their revisions. Actual publication and the
differences between the remote app and local fixtures are in the [CI guide](ci-e-publicacao.md#published-revision-evidence).

Model tests do not demonstrate graphical UI on JVM/Native. Touch through CDP
does not complete [Android acceptance](jogar.md#android-acceptance-limits).
Comparison with the historical video and human visual approvals still pending
in the relevant records remain separate from agent inspection and automation.

The [validation record for this documentation update](../.agent/validation/documentacao.md)
tracks repeated commands and evidence only consulted. Logs, captures, and
intermediate local files stay in `.agent/tmp/`; tracked summaries contain the
essential results without depending on those files.
