<a id="regras-do-jogo"></a>

# Game rules

[English](regras-do-jogo.md) | [Português (Brasil) — pt-BR](regras-do-jogo.pt_BR.md)

[Back to the project overview](../README.md) ·
[How to play](jogar.md) ·
[Development and verification](desenvolvimento.md)

This guide describes the delivered behavior and approved differences from the
original. The [port specification](../.agent/specifications/port-sifuture-to-kof.md)
keeps the v1 requirements and unfinished cycles.

<a id="mundo-lógico-e-passo"></a>

## Logical world and logical step

The **logical world** is the coordinate space in which the game calculates
positions and collisions: 176 × 220 units. A **logical step** is one simulation
update, scheduled every 30 ms. Window size does not redefine this world. The
ship moves five units per logical step on each active axis, with an upper limit
of `y = 30`; the right and bottom limits account for its size.

In [Rules.kf](../src/main/kof/sifuture/game/Rules.kf#L4):

```kof
static final Int STEP_MS = 30
static final Int WORLD_WIDTH = 176
static final Int WORLD_HEIGHT = 220
```

These values separate time from space: one movement applies five units of
speed; waiting one second is not itself a movement instruction. The upper
limit and speed are named `HEADER_HEIGHT` and `SHIP_SPEED` in the same file.
The clock updates the model and then draws it, as described in the
[development guide](desenvolvimento.md#model-drawing-and-controls). Redrawing
only reads the state and does not speed up animation. Pause freezes counters,
including background, items, shots, and effects.

<a id="fase"></a>

## Stage

The **stage** is the attempt's route, represented by a marker from position 5
to 176. The first extended encounter enters at 88 and advances the marker to
89; the last enters at 146 and advances it to 147. Combat and the explosions
of these enemies suspend route progress. Outside those encounters, the marker
advances one position every ten logical steps. Total duration depends on
combat.

The position is derived in [Game.stagePosition](../src/main/kof/sifuture/game/Game.kf#L324):

```kof
var position = 5 + stageSteps / 10
if (position > Rules.WORLD_WIDTH) { return Rules.WORLD_WIDTH }
return position
```

`steps` counts game updates; `stageSteps` counts route progress and the
historical entry increment. During combat and explosions, only the first
continues. Deriving the position avoids storing a duplicate value that would
need synchronization. The [duplicate-state training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/anti-patterns/duplicate-state.md#L73)
states:

> If a value can be derived from another, derive it (method or function).

After the last encounter ends, 290 logical steps remain before the game ends.
Pause freezes all these clocks.

<a id="pontuação-e-vidas"></a>

## Score and lives

**Score** accumulates the attempt's rewards. **Lives** are the remaining
chances: the ship starts with three, and one is removed when its explosion
ends. The ship's **normal** state permits collisions; during restart it blinks
and is invulnerable.

A ship collision with obstacles grants five points only once in that logical
step, even if several overlap. Each overlapping obstacle starts its own
animation. The ship's explosion lasts ten frames at three logical steps each;
restart has 15 alternations at three steps each.

Update order considers the state before and after advancing the ship: the
previous state decides whether to attempt a shot; the new state decides
collisions. On the 45th restart step the ship can already collide, but it only
attempts a normal shot on the next step. See [Game.step](../src/main/kof/sifuture/game/Game.kf#L233):

```kof
var normalBefore = ship.phase == ShipPhase.Normal
var livesBefore = ship.lives
ship.advance()
if (ship.lives < livesBefore) { weapons.loseOnDeath() }
```

Later in the [same update](../src/main/kof/sifuture/game/Game.kf#L244):

```kof
if (normalBefore) { weapons.attemptFire(ship) }
```

`normalBefore` keeps the condition from the start of the logical step. A
transition to normal inside `ship.advance()` does not change that condition
retroactively.

<a id="coleta-e-evolução"></a>

## Collection and upgrades

**Collection** occurs when a normal ship touches an available item. There is
always one **upgrade** heart, which improves weapons, and one life heart,
which adds a life. The upgrade item cycles through five `iten` frames; the
life item pulses through eleven `life` frames, moving forward and back. Each
pickup grants ten points once, displays three effect frames, then relaunches
the item. Initial blinking and explosion do not allow collection. Lives can
exceed three.

| Upgrade pickups | Weapon |
| --- | --- |
| None | Basic laser, one active at a time. |
| First | Animated laser; one launch per attempt and up to three in flight. |
| Second | Adds the blaster on every sixth laser cycle. |
| Third | Keeps the laser and increases blaster frequency. |
| Further pickups | Store special-attack charges while retaining the third upgrade. |

The rule is in [Game.kf](../src/main/kof/sifuture/game/Game.kf#L248):

```kof
if (item.collect(ship)) {
    score = score + 10
    if (item.kind == ItemKind.Life) { ship.lives = ship.lives + 1 }
    else { weapons.evolve() }
}
```

`collect` returns true only for the first pickup. The reward and benefit are
therefore granted together, once. `ship.lives + 1` does not cap lives at three;
recorded journeys observed a change from 3 to 4 on JVM, JS, and Chrome, as
shown in [background-items-weapons.md](../.agent/validation/background-items-weapons.md).

This assignment changes a field on a mutable class. The [class training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/language/classes.md#L11)
says:

> For **mutable state**, use fields + `constructor(...)`

[Learn Kof: Classes and Objects](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/07-classes-and-objects.md#L65)
teaches:

> To **mutate**, use explicit public fields:

Here, `ship.lives` is the value that changes. The development guide explains
how the model's [classes](desenvolvimento.md#classes-and-states-in-kof)
express this intent without duplicating state.

<a id="armas-e-perda-de-evolução"></a>

## Weapons and lost upgrades

The laser attempts to fire every 13 normal logical steps. The blaster takes
two hits; each of the special attack's three beams takes ten. At the second
upgrade, the blaster uses the historical trigger of every six laser attempts;
at the third, its frequency increases. `Weapons` centralizes level, charges,
rate, and projectiles.

On death, the ship loses one stored charge or, when it has none, one weapon
level down to the basic weapon. In [Weapons.loseOnDeath](../src/main/kof/sifuture/game/Weapons.kf#L26):

```kof
loseOnDeath() {
    if (charges > 0) { charges = charges - 1 }
    else if (level > 0) { level = level - 1 }
}
```

The branches are exclusive: if a charge exists, that event preserves the
weapon level. Already launched projectiles keep moving and applying effects.
When no lives remain, the ship stops creating shots during the ending; existing
lasers, blaster, and special attack finish normally. Shots remain visible when
the stage is completed with lives left. The [gameplay guide](jogar.md#special-attack)
collects the special attack's controls and availability.

<a id="meteoros"></a>

## Meteors

There are six horizontal meteors with preserved indices, and two vertical
ones that enter once the stage position passes 30. Vertical meteors descend
one unit per logical step and show three impact frames, one step per frame.
The pair relaunches when both are inactive and both bosses are inactive.
Meteors already launched finish their route during combat.

Collisions keep the order ship → laser → blaster → special attack, with one
reward per meteor. A laser impact shows `laser03.png` for one logical step;
hit horizontal meteors continue moving one unit per step for three frames of
two steps each. See the order in [Game.step](../src/main/kof/sifuture/game/Game.kf#L285)
and the journeys in [browser_meteor.py](../tests/browser_meteor.py) and
[browser_stage.py](../tests/browser_stage.py).

Vertical meteors reset between −153 and 0 when created or after impact; after
leaving through the bottom, they use the historical range −171 to 0 and keep
the pair wait. Regressions are recorded in [ship-meteor-reset.md](../.agent/validation/ship-meteor-reset.md).

<a id="subchefe"></a>

## Miniboss

The **miniboss** is the enemy in the first extended encounter. It has 30
health, moves one unit per axis, and has three attacks of its own, attempting
one every 12 normal logical steps. A laser removes one health; the blaster
deals damage equal to its remaining resistance. The special attack preserves
historical six-step markers, including reapplication when another beam begins
contact. Body contact explodes a normal ship; during invulnerable restart it
changes neither entity, an explicit exception to the original.

`lifeTime` is a duration counter used to choose the reward; for the miniboss
it advances every 36 normal logical steps and does not represent seconds. The
fatal hit awards 600, 300, or 150 points for `lifeTime` ≤30, ≤60, or >60. Its
ten explosion frames last three logical steps each. Recurring items are not
duplicated or repositioned by the reward.

[Subchief.reward](../src/main/kof/sifuture/game/Subchief.kf#L62) defines the ranges:

```kof
reward(): Int {
    if (lifeTime <= 30) { return 600 }
    if (lifeTime <= 60) { return 300 }
    return 150
}
```

The first matching limit determines the reward. Thus 30 gives 600, while 31
moves to the 300 range. [browser_subchief.py](../tests/browser_subchief.py)
checks the encounter, attacks, special, explosion, pause, resume, and new game
with the real model, drawing, and controls at 320/1200 pixels.

<a id="boss-final"></a>

## Final boss

The **final boss** appears in the last encounter. It has 100 health and five
attack levels, with normal intervals of 13/31/31/24/24 logical steps.
Nonfatal weapon hits advance its attack below 80/70/45/20; exact threshold
values do not advance it. Body contact does not upgrade the weapon and
requires the boss to be in its normal state. Its special attack prepares for
six frames of three steps each, and only moves and collides on frame 6. Fury
uses `bos1.png`; frenzy alternates `bos.png`, `bos1.png`, and `bos2.png` every
four steps.

The reward is 1650/1100/550/275 for `lifeTime` ≤30/≤60/≤120/>120. The fatal
hit preserves movement, stops attacks and increments to that clock, and starts
the explosion: frame 0 for one step, later frames for three, ending at step 28.
Absorbed meteors cause neither damage nor points. Invulnerable restart does
not cause body contact, an approved exception to the original.

[Boss.reward](../src/main/kof/sifuture/game/Boss.kf#L72) defines these rewards:

```kof
reward(): Int {
    if (lifeTime <= 30) { return 1650 }
    if (lifeTime <= 60) { return 1100 }
    if (lifeTime <= 120) { return 550 }
    return 275
}
```

The thresholds choose one reward on the fatal hit. [browser_boss.py](../tests/browser_boss.py)
checks entry, phases, attacks, contacts, indicators, explosion, pause,
redraws, ending, and repeat play with the same seed at 320/1200 pixels. The
fourteen assets added in that cycle are byte-for-byte copies of historical
assets, as recorded in the [boss acceptance record](../.agent/validation/stage-hud-result.md).

## HUD

**HUD** means the indicators drawn over the scene. It uses historical sprites
without transformation: the route, a marker based on one, two, or three or
more lives, score at the right, a life counter below, and the special icon at
`(50, 21)`. Indicators are drawn after entities so they stay visible over
beams. The world remains 176 × 220 and the ship keeps the `y = 30` limit. The
[renderer](../src/main/kof/sifuture/GameView.kf) reads the model; the [stage
and result acceptance record](../.agent/validation/stage-hud-result.md)
contains sprite comparisons.

<a id="resultado"></a>

## Result

The **result** ends an attempt when the stage finishes or the last life is
lost. Final score is preserved; the displayed count starts at zero. Each
logical step adds five points up to the exact total. The rating appears only
when the count ends:

| Score | Rating index |
| --- | --- |
| Below 1500 | 0 |
| 1500 to 2199 | 1 |
| 2200 to 3299 | 2 |
| 3300 or more | 3 |

In [Game.resultIndex](../src/main/kof/sifuture/game/Game.kf#L331):

```kof
if (score < Rules.RESULT_GOOD) { return 0 }
if (score < Rules.RESULT_GREAT) { return 1 }
if (score < Rules.RESULT_BEST) { return 2 }
return 3
```

Because the thresholds are strict, exactly 1500 belongs to the second range
and exactly 2200 to the third. This fixes historical cases with no message at
those boundaries. A zero score starts with the count already complete. The
[two result commands](jogar.md#start-a-game) let the player finish the count
and then return to the menu, without a double confirmation from holding Enter.

During results, the background, meteors, items, bosses, visual automatic shots,
and effects continue. Collisions, collection, and ship commands stop; lives,
level, charges, and stage position remain stable. A pending explosion ends
without another lost life and is hidden without trying to draw frame index 10.
Score and rating are centered over the scene.

<a id="diferenças-aprovadas-e-correções-históricas"></a>

## Approved differences and historical fixes

In addition to modern controls and score boundaries, the [specification](../.agent/specifications/port-sifuture-to-kof.md#historical-gameplay)
approves using `Middle2.png` only while the effective horizontal direction
is right. Releasing restores `Middle.png` on the next logical step, including
while moving vertically. Pause, result, and loss of focus clear commands and
restore the normal frame. The original kept the thrust frame after release.

The approved miniboss and final-boss cycles include the body-contact exceptions
during invulnerable restart. Controls where dragging keeps the initial arrow
are the current contract; they do not represent the full future v1.

The special attack's three groups use `e0`–`e2`, `e3`–`e5`, and `e6`–`e8`,
for orange, light blue, and dark blue. Historical
[AirShipEspecialShoot.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/AirShipEspecialShoot.java)
attempted to load `especial0`–`especial8` and used indices 3–8 in three-item
arrays for the blue colors. The Kof scene uses the existing files grouped by
color, fixing loading without replacing the drawings. [NOTICE](../NOTICE)
still applies; current typography is covered in the [font guide](../fonts/README.md).

<a id="fontes-e-limites-das-provas"></a>

## Sources and limits of evidence

The Kof excerpts above come from existing source code. Their execution belongs
to the recorded revisions; they are not new examples claimed to have been run.
[GameJourney.kf](../src/test/kof/sifuture/game/GameJourney.kf) exercises rules
on JVM and JS. Browser scripts use the same real components and deterministic
positions to observe pixels, timing, and interactions. The [development
guide](desenvolvimento.md#what-the-checks-demonstrate) lists commands,
revisions, and environments.

Historical rules were consulted in [AirShip.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/AirShip.java),
[AirShipAllShoots.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/AirShipAllShoots.java),
[Meteor.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/Meteor.java),
[MeteorArray.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/MeteorArray.java),
and [GameCanvas.java](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/src/GameCanvas.java).
The [historical video](https://youtu.be/1xMKYEy7Jqw?si=oF48Zq7EeNTLTb3J)
guides the visual comparison that remains open. Deterministic tests do not
replace it, and do not demonstrate graphical execution on JVM/Native or
acceptance on a physical Android device.
