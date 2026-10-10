<a id="como-jogar"></a>

# How to play

[English](jogar.md) | [Português (Brasil) — pt-BR](jogar.pt_BR.md)

[Back to the project overview](../README.md) ·
[Game rules](regras-do-jogo.md) ·
[Build a local version](desenvolvimento.md#build-and-open-the-app) ·
[Site updates](ci-e-publicacao.md#site-updates)

<a id="começar-uma-partida"></a>

## Start a game

**[Play SiFuture](https://renanfranca.github.io/kof-sifuture/)**

1. On the opening screen, click or tap **“Pular créditos” (Skip credits)**. You can also tap the credits area, or press Tab until a control is focused and then press Enter.
2. In the menu, click or tap **“Novo Jogo” (New Game)**. With a keyboard, release Enter and press it again on **Confirmar (Enter)** while New Game is selected. Up/Down changes the selection; the ship marks the current option.
3. Move the ship with the keyboard arrows or hold the directional pad below the game. The control used in the menu already has keyboard focus for play.
4. To pause, press Enter or activate **Pausar** (Pause). Choose **Continuar** (Continue), then press a direction again to move.
5. When the session ends, **Concluir contagem** (Finish count) immediately shows the final score. Confirm **Voltar ao menu** (Back to menu) to return.

Normal shots fire automatically. To learn all controls first, open **Controles** (Controls) from the menu. **Voltar** (Back) returns with Controls selected; select New Game to begin. **Mais detalhes** (More details) starts closed, changes to **Menos detalhes** (Fewer details) when opened, and closes on the next entry. Opening details does not start the game.

The labels match the [in-game controls guide](../src/main/kof/sifuture/ControlsGuide.kf#L26):

```kof
listOf("Setas", "Mover a nave na partida"),
listOf("↑ / ↓", "Escolher uma opção nos menus"),
listOf("Enter", "Confirmar nos menus; pausar na partida"),
listOf("1", "Usar o especial quando disponível")))
```

Enter confirms the action for the current screen. Releasing and pressing it
again separates the intent to open the menu from the next intent to start a
game.

<a id="créditos-e-menus"></a>

## Credits and menus

Credits appear once per application instance. You can wait for the animation
or skip it. Holding Enter skips only to the menu; it does not start a game.
Returning from Controls, pause, or results does not replay the credits.

Up/Down selects one option per press and stops at the ends of the list. Enter
or **Confirmar (Enter)** activates the current selection. Tabbing to Confirm
keeps that selection; click and Space also confirm. Click or tap an option's
name to activate it. Options have accessible names; the ship indicates the
selection and no rectangle follows the lines. Selection and confirmation are
available while the ship is still entering the menu.

<a id="teclado-e-foco"></a>

## Keyboard and focus

**Focus** is the control that receives keyboard input. On the opening screen,
press Tab or click a control to focus it. When starting or resuming from a
menu, focus lets the arrow keys and **1** work on the main button or on the
option that retains focus. The game area can also receive keyboard input by
clicking it or tabbing to it.

| Input | Action |
| --- | --- |
| Arrows during play | Move the ship. Directions on different axes form a diagonal. |
| Up/Down in menus | Select one option per press. |
| Enter in the game area, main button, or focus-retaining option | Performs the screen's main action once per press. Pauses during play. |
| Space | Activates the focused functional button. It does not confirm a focus-retaining option outside its original screen. |
| **1** in the game area, main button, or focus-retaining option | Attempts the special attack. |
| **1**, Enter, or Space on the Special button | Attempts the special attack. |
| Tab / Shift+Tab | Move through controls forward / backward. |

A neutral 1-pixel outline around the game indicates focus on the game area or
a focus-retaining option; external buttons have their own outline. A retained
option outside its original screen is given the accessible name **Teclado do
jogo** (Game keyboard); its name returns when the original screen returns.
Losing focus ends this retention and clears keyboard movement while preserving
a directional pad that is still held. Losing focus does not pause the game in
this slice.

The game must observe Enter being released on one of its controls before it
can confirm again. Click and Space on the main button continue to work while
Enter is held. Controls observe the keyboard only within their control tree,
meaning the game's controls and their internal elements; they do not capture
keys elsewhere on the page. WASD is not a game command.

<a id="toque-mouse-e-direções-combinadas"></a>

## Touch, mouse, and combined directions

The four arrows are below the game in a cross, with empty center and corners.
Each button is 56 × 56 pixels. Hold Right and Up for a diagonal. For opposing
directions, the most recently pressed one wins; releasing it restores the
other direction if it is still held. Releasing one arrow preserves the other;
releasing the last one stops movement.

With a mouse, leaving an arrow ends that press; returning without pressing
does not resume it. With touch, dragging keeps the initial arrow until release
or cancellation: sliding to another arrow does not change direction during
that gesture. The directional pad is disabled outside a game.

While any directional pad arrow is held, it has priority over the keyboard.
After releasing the pad, a keyboard arrow that was already held does not take
over by itself: release and press it again. Demonstrated multitouch uses
separate fingers on separate buttons; it does not cover several fingers on
the same button.

<a id="pausa-reinício-e-retorno"></a>

## Pause, restart, and return

| Pause option | Result |
| --- | --- |
| **Continuar** (Continue) | Keeps the game and all its counters; new presses are required to move. |
| **Reiniciar** (Restart) | Starts over with the ship at its initial position, three lives, zero score, the beginning of the stage, the basic weapon, no charges, and inactive bosses. |
| **Menu principal** (Main Menu) | Ends the attempt and selects New Game in the menu. |

Pause freezes the simulation, including shots, meteors, items, and animations.
New Game after abandoning or finishing starts a clean attempt. Options and
Music remain planned for the audio cycle.

<a id="especial"></a>

## Special attack

The special attack fires three beams and consumes one charge. After reaching
the third weapon upgrade, further upgrade-item pickups store charges; the
[item collection rules](regras-do-jogo.md#collection-and-upgrades) explain
this progression.

The **Especial** (Special) button is to the right of the game area and is
56 × 220 pixels. Its word is centered vertically and reads from top to bottom.
Its top and bottom align with the game, with a 16-pixel gap. Press it with a
mouse or touch, or press **1** while the game has focus. Enter and Space on the
button also attempt the shot. Two fingers can hold a diagonal while a third
tries the special attack.

Holding a key or button does not repeat the shot. A rejected attempt does
not remain pending: release and press again. The special attack is unavailable
without a charge, while another special is in progress, during pause, or when
the ship is not in its normal state. The header icon appears while any charge
remains, including during temporary unavailability, and does not show the
count.

Focus is retained so the game can observe a release: if the Special button is
focused and **1**, Enter, or Space remains held, the button may remain enabled
to receive events, with opacity `0.5` while unavailable. This does not permit
another shot. The final release or leaving the button applies availability
immediately. If the beams end before release and a charge remains, opacity
returns to `1`, but another attempt still requires release and a new press.

Releasing **1**, Enter, or Space on any game control clears the special
attack's lock. Releasing outside preserves it. The [regression record](../.agent/validation/special-key-release.md)
contains checks for focus, simultaneous keys, and key release.

<a id="recuperar-comandos-depois-de-sair-dos-controles"></a>

## Recover input after leaving the controls

The game remembers keys it observed as pressed. If a key is released outside
the controls, that memory can continue to block a new press.

| Situation | How to recover |
| --- | --- |
| Right was released outside; return by clicking the game area | The click rearms arrows only and does not move by itself. The next Right press can move immediately. |
| Right was released outside; return with Tab | Tab preserves the memory. Release Right inside the controls, then press again. |
| Enter was released outside; return by clicking the game area | The click preserves Enter's lock. Release Enter inside the controls, then press again. |
| An arrow was pressed on another control; return with Tab | Release the arrow inside the controls before pressing it again to move. |
| The directional pad was released while a keyboard arrow was held | Release and press the keyboard arrow again. |

These cases preserve the contract in the [delivered-slice specification](../.agent/specifications/port-sifuture-to-kof.md#implemented-browser-slice-issue-3):

> A pointer press on the canvas overlay clears remembered arrow presses and effective keyboard movement without ending any held pad direction.

In other words, pressing the game area with a pointer clears remembered
keyboard arrows without ending a held directional pad input. This clearing
applies to arrows; Enter's shared lock depends on its own release. The model
implements the clearing in [Game.rearmKeyboard](../src/main/kof/sifuture/game/Game.kf#L50):

```kof
rearmKeyboard() {
    heldLeft = false
    heldRight = false
    heldUp = false
    heldDown = false
    if (!padPressed()) { ship.clearInput() }
}
```

The four fields represent only arrow keys. `padPressed()` prevents clearing
the keyboard from interrupting a directional pad that is still held.

<a id="android-e-limites-do-aceite"></a>

## Android acceptance limits

In the examined 320-pixel viewport, the window is 296 pixels wide. The game
area remains 176 × 220; the set with Special is 248 pixels wide, and the
cross is 168 × 168, with no gap between arrows.

Automated journeys checked diagonals, opposing directions, dragging, release,
cancellation, pause, and two fingers on the directional pad with a third on
Special. The [controls record](../.agent/validation/sifuture-controls.md)
distinguishes revisions: the `cedf4875abe101d8fd85012dbfb30ef20bf5406c`
gate records seven complete journeys in Chrome 155.0.8059.39; touch is
simulated through CDP, the browser automation interface.

Comfort, finger reach, and a miniboss fight on a physical Android device
still require manual acceptance. The [APK attempt](../.agent/validation/android-apk-blockers.md)
on 2026-10-06 failed without producing an artifact. Opening a narrow browser
window on a computer does not prove that the game was installed or run on
Android.

To reproduce automated checks, use the [development guide](desenvolvimento.md#check-the-browser).
The [publishing guide](ci-e-publicacao.md#published-revision-evidence) explains
how to associate the public experience with the delivered revision.
