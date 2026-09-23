# Port SiFuture to Kof

- **Status:** Approved specification; implementation has not started.
- **Source:** The SiFuture port handoff and the approved proposal in the Codex task.
- **Port repository:** `/home/renanfranca/projects/kof-sifuture`.
- **Historical game:** `/home/renanfranca/projects/sifuture`.
- **Kof reference:** `/home/renanfranca/projects/kof`.

## Purpose and acceptance boundary

Port the Java ME game SiFuture to Kof while preserving its rules and recognizable presentation. The graphical v1 MUST run in a browser through KofJS and on Android through KofJS in a WebView. A successful Android build alone is insufficient: the game MUST also run in an emulator or on a device. JVM and Native are portability research targets with their actual limitations recorded; graphical UI on those targets is not a v1 acceptance requirement. KofScript is outside this port.

All application code MUST be real Kof. The port MUST use existing Kof capabilities first. It MUST NOT introduce a separate application framework, a JavaScript/CSS/DOM implementation layer, handwritten JavaScript or CSS, or edits to generated `.mjs` files. Target-specific realization inside Kof itself remains a separate Kof maintainer decision, not an application workaround.

The web version MUST NOT be called complete while any mandatory presentation, input, lifecycle, or music behavior below is unavailable. An unrelated implementation slice MAY continue while one slice is blocked.

## Sources of truth

The [historical video](https://youtu.be/1xMKYEy7Jqw?si=oF48Zq7EeNTLTb3J) governs observable appearance, composition, and pacing. The historical source and bytecode govern rules, coordinates, and state transitions. The explicit changes in this specification take precedence over either historical source. The historical JAR MUST NOT be run in an emulator as an oracle. Scale, margins, and modern controls need not match the video frame by frame.

For Kof capability claims, inspect the current implementation, then tests, documentation, and training, in that order. Distinguish implemented behavior from future plans and from untested hypotheses. Follow the Kof repository's `AGENTS.md`, `docs/development/DECISIONS.md` (particularly `D-UI-SCOPE` and `D-KOF-FIRST`), development index, future index, and relevant training when the work is performed.

Kof `main` is the moving integration baseline. Each compilation, runtime observation, and gap dossier MUST record the Kof version and full commit SHA actually tested. An update to `main` MUST trigger a repeat of affected validation before a previous result is reused; it does not automatically invalidate unrelated evidence. The planning snapshot was `0.4.10-beta` at `ebd11a1af42b525c583c28ab444e060fae8a9c6a` on 2026-09-23, not a version pin.

## Game and presentation contract

### Historical gameplay

- The game MUST preserve the historical stage progression, ship movement, automatic normal fire, special attack, enemies, meteors, items, collisions, scoring, lives, sub-boss, final boss, and result flow, including their historical balance unless an explicit change appears here. The historical source and bytecode settle ambiguous rules. The normal shot MUST be automatic, as indicated by `airship.fire()` in the historical update path; no manual or configurable normal-fire mode is required.
- The simulation MUST use a fixed **176 × 220 logical-unit** world, corresponding to the MOTOKRZR K1. It MUST NOT treat the current viewport size as the game world.
- Item, sub-boss, and final boss MUST retain the historical right-side initial coordinate **220** (logical height); horizontal meteors MUST use logical width **176**. The apparent width/height inconsistency is deliberate for this port.
- Normal play MUST use a variable random seed. Test entry points MUST allow an injected seed so meteor, item, and enemy sequences can be reproduced. The seed mechanism need not become a player-facing option.
- Result messages MUST cover scores `< 1500`, `1500–2199`, `2200–3299`, and `>= 3300`, respectively. This explicitly fixes the historical missing-message cases at 1500 and 2200.
- Historical TODOs concerning the interval between enemy shots and resetting keys on entry to pause are outside scope. The input-clearing rules under lifecycle events below still apply.

### Rendering and loop

- Simulation MUST advance in fixed **30 ms** logical steps, with update and rendering separated. Rendering frequency MAY differ from update frequency. After a stall, suspension, focus loss, or resize, the game MUST NOT execute an unbounded burst of delayed steps.
- The application MUST fill the available viewport without requesting browser fullscreen. The portrait game composition MUST remain centered and playable on wide desktop or landscape screens. The game canvas MUST be above the controls; controls MUST NOT cover the playable area.
- Presentation MUST preserve the 176 × 220 world with an integer display scale and crisp, unsmoothed sprites. Acceptance is based on those observable properties on the tested browser and Android displays, not on a prescribed DPR, backing-bitmap formula, or unapproved Kof API.
- On focus loss or resize, the application MUST clear active inputs, pause simulation and music, recalculate presentation, and require an explicit **Continue** action before simulation resumes. Paused time MUST NOT be replayed as catch-up simulation.

### Input

- Arrow keys MUST move the ship; key `1` MUST attempt the special attack; Enter MUST confirm menu/result actions and toggle pause during play. WASD is not supported.
- Touch MUST provide one eight-direction movement region, including diagonals. Sliding within it MUST update direction and releasing it MUST stop movement. Multitouch MUST allow movement together with a special press or pause press. The special control MUST make one attempt per press and MUST NOT repeat while held. A dedicated pause control is required.
- Menu options MUST support direct touch. Direction and confirmation controls MUST remain usable for menu navigation. Touch controls MUST use a new, unobtrusive visual treatment rather than historical sprites.

### Screens and transitions

- Credits MUST appear once when the application opens. Enter or touch MUST skip them. They MUST NOT recur within the same running application instance.
- The initial menu MUST offer **New Game**, **Controls**, and **Options**. **Load Game** MUST be hidden in v1. Controls MUST open a functional explanation of both keyboard and touch input. Options MUST offer Music on/off.
- Pause MUST use a dedicated screen with **Continue**, **Restart**, **Music on/off**, and **Main Menu**. Restart MUST begin the stage from its initial state. Main Menu MUST end the current attempt.
- The result screen MUST remain until Enter or a touch on **Continue**. That action MUST return to the main menu ready for a new game.

### Music

The historical MIDI files are a requested addition to the preserved Java ME source, which does not implement playback of those tracks. They are nevertheless mandatory v1 behavior:

- `FASE.MID` MUST loop during normal-stage play. At the start of the final boss, it MUST stop and `BOSS.MID` MUST start from the beginning.
- Pause MUST preserve the active track's position; Continue MUST resume it from that position. Restart MUST stop the current track and start `FASE.MID` from the beginning. Main Menu MUST stop the game track. The result screen MUST be silent.
- Music MUST be on by default at the start of each application run. The preference MUST exist only for that run and MUST NOT be saved in browser storage. Switching music off MUST stop the track; switching it back on MUST start the track appropriate to the current game state from the beginning. V1 has no volume control.
- The actual `FASE.MID` and `BOSS.MID` files MUST be used to prove the required behavior in a browser and Android WebView. No MIDI API name, signature, format conversion, or fallback is specified in advance.

## Assets and distribution decision

The port MUST include the historical sprites and MIDIs in its **public** repository. The project owner explicitly chose this despite the identified rights uncertainty and accepted that risk. This choice is a project distribution decision, **not** evidence of a license or authorization.

The historical repository's `NOTICE` says that the images come from other games and that the MIDI authors and licenses have not been identified; those assets are excluded from the Apache 2.0 license that covers the author's code. The port MUST preserve a clear distinction between code licensing and the unknown rights of these third-party assets. It MUST NOT claim ownership, Apache 2.0 coverage, permission to redistribute, or free reuse for the original assets without new evidence. This specification does not settle the rights question.

## Kof portability and gap process

The current evidence is a feasibility snapshot, not proof that all required behavior can be implemented:

| Area | Observed Kof state at the planning snapshot | Required proof or outcome |
| --- | --- | --- |
| Drawing | KofJS `Canvas(w, h)` creates a DOM canvas with width and height and offers drawing, text, transform, and `drawImage`. | Render the historical sprites and all required scenes at integer scale on actual browser and Android displays. |
| Viewport and pixel clarity | No public viewport/resize contract, display/backing-size separation, DPR adaptation, explicit image-smoothing control, or automatic integer-scale policy was found. | Measure whether current Kof composition can meet resizing, centering, integer scale, and crispness; file a gap only if it cannot. |
| Input | Widget `Event` exposes key/value/global x/y/type/target/relatedTarget. The shared widget `.on(...)` does not include `Canvas`; no pointer identity/capture model was found. | Prove keyboard and full touch behavior, including sliding, release, simultaneous contacts, and focus/resize cleanup, in Kof. |
| Audio | `kof.ui.Audio(url)` is browser-format-dependent media; `kof.media.Audio.openWav` is not KofJS MIDI playback, and the non-JVM `kof.media` family reports `MEDIA001` where applicable. | Test the real MIDI files and every required music transition in KofJS and Android. |
| Targets | KofJS has real DOM rendering and Android uses KofJS in a WebView. JVM/Native UI behavior is limited; `D-UI-SCOPE` does not require their graphical UI rules in v1. | Run the graphical acceptance matrix on browser and Android; record JVM/Native findings honestly without treating graphical UI absence there as a v1 failure. |

Before requesting a Kof change, the implementer MUST verify that the need is legitimate in Kof terms, construct a **valid Kof** reproducer, identify the existing Kof contract and idiom, attempt composition with current capabilities, and measure the behavior on affected targets. A blocked slice MUST produce a dossier containing the reproducer, Kof version and SHA, commands and environment, expected and actual behavior, target matrix, composition attempts, and observable acceptance criteria. Classify it using `D-KOF-FIRST` as an internal bug, target divergence, real gap, or unsupported external expectation. Browser Canvas or JavaScript behavior alone is not an oracle for Kof.

Only the blocked slice MUST stop while its dossier is resolved. Any proposed Kof surface, including names, signatures, semantics, target policy, and whether it belongs in core, stdlib/platform, an official package, ecosystem, or interop, remains for the Kof maintainer's later decision under rule 6 and the Simplicity Law. The port MUST NOT silently emulate a missing capability with handwritten host code or declare target parity that has not been demonstrated.

## Acceptance evidence

1. **Historical fidelity:** Compare credits, menu, stage opening, sub-boss, final boss, and result against observable milestones in the historical video. Verify rules, coordinates, state transitions, and automatic fire against source and bytecode. Do not execute the historical JAR in an emulator. Differences explicitly permitted above, including modern controls and the score-boundary fix, are recorded rather than treated as failures.
2. **Deterministic game tests:** With an injected seed, repeat meteor, item, and enemy behavior. Exercise stage and boss progression, collision and score/life outcomes, restart, and result boundaries at 1499, 1500, 2199, 2200, 3299, and 3300.
3. **Presentation and lifecycle:** On browser and Android displays of differing dimensions and density, verify the fixed logical world, integer scaling, sprite clarity, centered landscape/wide layout, controls below the game, and no fullscreen request. Verify focus loss and resize clear input, pause game and music, recalculate layout, and require explicit Continue without catch-up steps.
4. **Input and navigation:** Exercise all eight touch directions, drag changes, release, simultaneous movement and special/pause, one special attempt per press, keyboard mapping, direct touch menu selection, credits skip, Controls, Options, pause actions, and result exit.
5. **Music:** With both original MIDIs, verify normal-stage loop, boss transition, pause-position retention, restart, menu/result silence, default-on behavior, and same-run toggle behavior in a real browser and Android WebView.
6. **Target evidence:** Compile every Kof snippet used as a portability reproducer. Build and execute the browser version; build the Android artifact and run it on an emulator or device. Record Kof SHA, commands, environments, and results. Report JVM/Native research findings and diagnostics separately. A build, generated output, or speculative API is not a substitute for observed v1 behavior.

## Explicit limits

This specification does not require a JVM/Native graphical port, KofScript support, WASD, Load Game, persistent options, volume control, frame-for-frame visual matching, the historical enemy-shot TODO, or a manual normal-fire option. It does not authorize predefining a new Kof API, bypassing Kof with handwritten web code, or claiming the historical assets are licensed. No Kof port implementation or compiled Kof snippet existed when this specification was approved.
