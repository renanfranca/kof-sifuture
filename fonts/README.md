<a id="texto-dos-créditos-e-menus"></a>

# Credits and menu text

[English](README.md) | [Português (Brasil) — pt-BR](README.pt_BR.md)

Credits, the main menu, and pause screen use the browser Canvas default
`10px sans-serif` font with a `1.6` scale transform, for an effective size of
16 px. Shared drawing in `GameView.drawText` uses `save`, `setFill`,
`transform`, `fillText`, and `restore`: temporary scale and color do not affect
subsequent sprites or drawing. The browser performs smoothing; the concrete
sans-serif family depends on the environment.

Credits use a dedicated 262 × 260 px surface, #121212 background, 12 px
margins, and 24 px line spacing. All text uses RGB(0,128,255), including
`renan.andradefranca@gmail.com` on one line. The name is split as “Renan
Meneses” and “de Andrade Franca”. Blocks begin at y40/136, with local
baselines 16/40/64.

Menus use white text at x48 and a baseline of `option y + 14`, preserving
128 × 19 px touch areas and the ship indicator. The game canvas remains
176 × 220 px. The credits animation reaches x12 at step55, waits 200 steps of
30ms, and moves blocks by72px until they have fully left the screen. Step476
is empty; step477 opens the menu.

The former composition from PNG glyphs, its generator, and its metrics no
longer have consumers. Historical images, HUD numbers, and NOTICE are
preserved. The license texts [LIBERATION-LICENSE.txt](LIBERATION-LICENSE.txt)
and [GPL-2.txt](GPL-2.txt) remain as records for Liberation Serif used by the
old font; they do not describe the browser's current sans-serif.

`python3 tests/browser.py` checks text, effective size, color, bounds, touch
areas, Canvas restoration, and animation in Chrome at widths 320/1200px and
densities 1/2, with 100% zoom. Captures and the agent's visual inspection are
recorded separately from the user's visual approval in
[controls-guide.md](../.agent/validation/controls-guide.md).
