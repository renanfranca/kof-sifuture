<a id="sifuture-em-kof-créditos-navegação-e-combate"></a>

<a id="sifuture-em-kof"></a>

# SiFuture in Kof

[English](README.md) | [Português (Brasil) — pt-BR](README.pt_BR.md)

<a id="por-que-trazer-o-sifuture-para-kof"></a>

## Why bring SiFuture to Kof

I started developing SiFuture in the second half of 2006, when I was in the
fourth semester of my Computer Science bachelor's degree. I had learned
Portugol in class and was beginning to study Turbo Pascal. To create my Java
ME (J2ME) spaceship game, I learned Java directly from Sun's official
documentation. It was my only source for learning the language and building
the game.

That documentation introduced me to Java's promise **“write once, run
anywhere.”** As a beginner, I imagined the game would work in other
environments too. When I finished it on **August 1, 2007**, I was disappointed:
it ran on a phone, but I needed an emulator on my computer. My game did not
run directly on desktop or on the web.

The original motivation is preserved in the [original project's README at
revision `6f59817`](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/README.md#L17):

> That documentation was where I discovered Java's slogan: "Write once, run anywhere".

Now I want to revisit that expectation with Kof: make SiFuture playable in
more environments while preserving its rules and recognizable presentation.
The browser version is already playable. Portability remains a goal that must
be demonstrated separately in each environment.

<a id="percurso-no-navegador"></a>

<a id="jogue-no-navegador"></a>

## Play in your browser

**[Play SiFuture](https://renanfranca.github.io/kof-sifuture/)**

Tap or click **“Pular créditos” (Skip credits)**, then **“Novo Jogo” (New
Game)**. With a keyboard, press Tab to focus a control, press Enter to skip
the credits, then press Enter again to confirm New Game. Move the ship with
the arrow keys or the directional pad below the game. **Controles** (Controls)
in the menu explains the keyboard, touch, and special attack; the [gameplay
guide](docs/jogar.md) walks through the full session.

Each merge into `main` starts the workflow. When tests, the build, and
publishing succeed for the current revision, the workflow updates this same
address. **The URL stays the same; its content is updated.** If a newer
revision has already advanced `main`, publication for the superseded revision
is skipped. See the [CI and publishing guide](docs/ci-e-publicacao.md#site-updates).

<a id="escopo-e-fontes"></a>

<a id="estado-do-projeto"></a>

## Project status

The delivered slice includes credits, a menu with New Game and Controls, a
game session, pause with Continue/Restart/Main Menu, background, items, weapon
upgrades, meteors, miniboss, final boss, indicators, and results. Full v1 is
still open. The [port specification](.agent/specifications/port-sifuture-to-kof.md)
distinguishes those delivered features from the goal:

> Full v1 remains open.

| Environment | Demonstrated result and limit |
| --- | --- |
| Browser | The game is published at the URL above. On 2026-10-09, revision `5609febbc76cc2dd5d0f52c90349dae3ef1f5057` was published, all 113 files were compared, and the menu journey was checked in Chrome 155.0.8059.39 at 320/1200 px, as recorded in the [publication record](.agent/validation/sifuture-controls.md). |
| JVM and JS model | Checkpoint `cedf4875abe101d8fd85012dbfb30ef20bf5406c` records 114 tests per target and seven complete Chrome journeys. These are different kinds of evidence: model tests do not demonstrate graphical rendering or interaction on the JVM. See [verification results and limits](docs/desenvolvimento.md#what-the-checks-demonstrate). |
| Android | A v1 goal, to run on an emulator or device. The 2026-10-06 attempt at revision `8edf5ebbb28391b5e7de5a905513c5e9a55e5ccd`, using Kof 0.5.0-beta, failed with `RNG001` and produced no APK. The SDK was not configured in that environment; see the [blocker record](.agent/validation/android-apk-blockers.md). |
| Graphical JVM and Native | Portability research targets. The specification does not require graphical ports on these targets for v1 acceptance. The cited records contain no graphical acceptance for the game in these environments. |

The [2026-10-09 record](.agent/validation/sifuture-controls.md) contains the
published revision's delivery evidence:

```text
PASS published Pages matches CI artifact: 113 files
```

This result compares files. The same record describes the menu journey in
Chrome; it does not claim that a full game session was played in that
publication based on those 113 files.

<a id="aceite-dos-controles-no-chrome-do-android"></a>

Options/Music, audio with the original MIDI files, automatic pause, adaptive
scaling, input outside the control tree, operation and comfort on a physical
Android device, and visual comparison with the historical video remain open.
Simulated touch in a browser does not complete acceptance on a device. The
[gameplay guide](docs/jogar.md#android-acceptance-limits) explains this limit;
[issue #4](https://github.com/renanfranca/kof-sifuture/issues/4) tracks the
remaining work. Each revision's records retain their own gaps, including
pending human visual approval where applicable.

<a id="documentação"></a>

## Documentation

The public guides are available in English and Brazilian Portuguese. Choose
the path that fits your goal:

| I want to… | Start with… |
| --- | --- |
| Play and learn the controls | [How to play](docs/jogar.md): opening, menus, keyboard, touch, pause, special attack, and input recovery. |
| Understand the game behavior | [Game rules](docs/regras-do-jogo.md): time, stage, score, lives, upgrades, meteors, bosses, and results. |
| Build, test, or contribute | [Development](docs/desenvolvimento.md): requirements, local recipes, code, and the source-root workaround. |
| Follow checks or recover a publication | [CI and publishing](docs/ci-e-publicacao.md): distribution, integrity, site updates, and diagnosis. |

<a id="fase-e-resultado"></a>
<a id="coleta-e-evolução"></a>

The explanations of [stage and results](docs/regras-do-jogo.md#stage) and
[item collection and upgrades](docs/regras-do-jogo.md#collection-and-upgrades)
include the rules, examples, and evidence previously kept here.

<a id="kof-instalado"></a>
<a id="compilar-a-aplicação-com-o-workaround"></a>
<a id="regras-módulos-e-testes"></a>

To contribute, see [Kof installation](docs/desenvolvimento.md#requirements),
[local builds](docs/desenvolvimento.md#build-and-open-the-app), and
[code organization and tests](docs/desenvolvimento.md#code-organization). The
workaround and its diagnostics have a single explanation in that guide.

<a id="ci-kof-e-github-pages"></a>
<a id="uma-distribuição-por-resolução"></a>
<a id="publicação-e-atualização-de-main"></a>
<a id="diagnóstico-reprodução-e-reexecução"></a>

To maintain delivery, see [checks](docs/ci-e-publicacao.md#checks),
[one distribution per resolution](docs/ci-e-publicacao.md#one-distribution-per-resolution),
[site updates](docs/ci-e-publicacao.md#site-updates), and
[diagnosis, reproduction, and reruns](docs/ci-e-publicacao.md#diagnosis-reproduction-and-reruns).

[Typography](fonts/README.md) has its own guide. Specifications,
[EXECPLAN.md](EXECPLAN.md), and [validation records](.agent/validation/)
preserve requirements, decisions, and evidence for their respective revisions.

<a id="projeto-original-e-recursos"></a>

## Original project and resources

The [original SiFuture project](https://github.com/renanfranca/sifuture)
preserves the J2ME game. The [historical video](https://youtu.be/1xMKYEy7Jqw?si=oF48Zq7EeNTLTb3J)
shows its presentation and informs the visual comparison that remains open
for this port.

Code authored by Renan Franca is licensed under the **Apache License 2.0**;
see [LICENSE](LICENSE) and [NOTICE](NOTICE). NOTICE distinguishes this code
from third-party images and MIDI files:

> Essas imagens estão excluídas da Apache License 2.0, inclusive quando
> incorporadas aos arquivos de distribuição .jar.

> Seus títulos originais, autores e licenças não foram identificados. Eles
> estão excluídos da Apache License 2.0.

The first excerpt concerns images; the second concerns MIDI files. This
repository does not assign a new license to these resources or grant rights
to reuse or redistribute them.
