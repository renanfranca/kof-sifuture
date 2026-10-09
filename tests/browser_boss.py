from datetime import datetime
import hashlib
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from kof_project import served_build
from browser_stage import bitmap, sprite

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".agent/tmp/boss-browser"


def state(page):
    return {key: int(value) for key, value in re.findall(
        r"(\w+):(-?\d+)", page.locator("#boss-status").inner_text())}


def advance(page, steps=1):
    page.clock.run_for(steps * 30)


def button(page, name):
    page.get_by_role("button", name=name, exact=True).click()


def redraws(page):
    before = state(page)
    pixels = bitmap(page).tobytes()
    for _ in range(3):
        button(page, "Repaint")
    assert state(page) == before and bitmap(page).tobytes() == pixels


def freeze(page):
    button(page, "Pausar")
    before = state(page)
    pixels = bitmap(page).tobytes()
    advance(page, 20)
    assert state(page) == before and bitmap(page).tobytes() == pixels
    button(page, "Continuar")


def boss_sprite(page):
    s = state(page)
    name = ("bos.png", "bos1.png", "bos2.png")[s["sprite"]]
    sprite(page, name, s["x"], s["y"])


def journey(page, width):
    assert state(page)["position"] == 145 and state(page)["phase"] == 0
    advance(page)
    assert state(page)["position"] == 147 and state(page)["phase"] == 1
    advance(page, 10)
    assert state(page)["position"] == 147
    freeze(page)
    redraws(page)

    button(page, "Encounter")
    advance(page)
    assert state(page)["x"] == 121 and state(page)["y"] == 101
    boss_sprite(page)
    page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"normal-{width}.png"))
    for label, phase, hp in (("Fury", 2, 44), ("Frenzy", 3, 19)):
        button(page, label)
        advance(page)
        assert state(page)["phase"] == phase and state(page)["hp"] == hp
        advance(page)
        boss_sprite(page)
        page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"{label.lower()}-{width}.png"))
        redraws(page)
        freeze(page)
    advance(page, 3)
    assert state(page)["sprite"] == 1
    boss_sprite(page)
    advance(page, 4)
    assert state(page)["sprite"] == 2
    boss_sprite(page)

    button(page, "Shots")
    advance(page)
    s = state(page)
    assert s["shots"] == 1 and s["shotX"] == 151 and s["shotFrame"] == 0
    sprite(page, "shoot0.png", 151, 101, occluded=((165, 101, 205, 152),))
    advance(page, 2)
    s = state(page)
    assert s["shotFrame"] == 1
    sprite(page, "shoot1.png", s["shotX"], s["shotY"], occluded=((165, s["y"], 205, s["y"] + 51),))
    advance(page, 2)
    s = state(page)
    assert s["shotFrame"] == 2
    sprite(page, "shoot2.png", s["shotX"], s["shotY"], occluded=((165, s["y"], 205, s["y"] + 51),))
    page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"shots-{width}.png"))
    advance(page, 27)
    assert state(page)["shots"] == 2

    button(page, "Boss special")
    advance(page)
    start_x = state(page)["specialX"]
    for step in range(18):
        frame = step // 3
        s = state(page)
        assert s["special"] == 1 and s["specialFrame"] == frame and s["specialX"] == start_x
        sprite(page, f"esp{frame}.png", s["specialX"], s["specialY"],
               occluded=((s["x"], s["y"], s["x"] + 40, s["y"] + 51),))
        redraws(page)
        advance(page)
    s = state(page)
    assert s["specialFrame"] == 6 and s["specialX"] == start_x
    sprite(page, "esp6.png", s["specialX"], s["specialY"],
           occluded=((s["x"], s["y"], s["x"] + 40, s["y"] + 51),))
    page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"special-{width}.png"))
    freeze(page)
    advance(page)
    assert state(page)["specialX"] == start_x - 10

    button(page, "Body contact")
    advance(page)
    assert state(page)["shipExplosion"] == 1 and state(page)["hp"] == 79 and state(page)["level"] == 0
    button(page, "Invulnerable contact")
    advance(page)
    assert state(page)["shipExplosion"] == 0 and state(page)["hp"] == 100
    for label, x in (("New shot", 78), ("Moving shot", 47)):
        button(page, label)
        advance(page)
        assert state(page)["shipExplosion"] == 0 and state(page)["shotX"] == x
        redraws(page)
        advance(page)
        assert state(page)["shipExplosion"] == 1 and state(page)["shots"] == 0
        sprite(page, "explosion0.png", 40 if label == "New shot" else 0, 100)
    button(page, "Reused shot")
    advance(page)
    assert state(page)["shipExplosion"] == 1 and state(page)["shots"] == 2 and state(page)["shotX"] == 78
    redraws(page)
    button(page, "Special boundary")
    assert state(page)["specialFrame"] == 5
    advance(page)
    assert state(page)["specialFrame"] == 6 and state(page)["shipExplosion"] == 0
    advance(page)
    assert state(page)["shipExplosion"] == 1 and state(page)["special"] == 0
    sprite(page, "explosion0.png", 0, 100)
    button(page, "Absorbed meteors")
    advance(page)
    assert state(page)["meteorHit"] == 1 and state(page)["meteorX"] == 120
    assert state(page)["score"] == 0 and state(page)["hp"] == 100
    page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"absorbed-{width}.png"))
    button(page, "Player special")
    page.locator("#game-keyboard").click()
    page.keyboard.down("1")
    page.keyboard.down("1")
    advance(page, 40)
    page.keyboard.up("1")
    assert state(page)["charges"] == 1 and state(page)["hp"] < 100

    button(page, "Fatal laser")
    advance(page)
    s = state(page)
    assert s["score"] == 1650 and s["lifetime"] == 30 and s["normalSteps"] == 35
    assert s["clock"] == 12 and s["shots"] == 0 and s["explosionSteps"] == 0
    assert s["explosionX"] == 121 and s["explosionY"] == 101
    sprite(page, "explosion0.png", 121, 101, occluded=((125, 100, 130, 125),))
    for digit, x in (("1", 112), ("6", 128), ("5", 144), ("0", 160)):
        sprite(page, digit + ".png", x, 0)
    redraws(page)
    page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"explosion0-{width}.png"))
    offsets = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 25, 28, 31, 34, 37, 40, 45, 50, 55, 60, 65)
    for step, offset in enumerate(offsets, 1):
        advance(page)
        s = state(page)
        frame = 1 + (step - 1) // 3
        assert s["explosionSteps"] == step and s["explosionFrame"] == frame
        assert s["explosionX"] == 121 - offset and s["position"] == 147 and s["score"] == 1650
        sprite(page, f"explosion{frame}.png", 121 - offset, 101)
        if step in (1, 25, 27):
            page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"explosion-step{step}-{width}.png"))
            freeze(page)
            redraws(page)
    advance(page)
    assert state(page)["phase"] == 0 and state(page)["shots"] == 0 and state(page)["special"] == 0
    advance(page, 289)
    assert state(page)["position"] == 175 and state(page)["result"] == 0
    advance(page)
    assert state(page)["position"] == 176 and state(page)["result"] == 1 and state(page)["lives"] == 3
    advance(page, 13)
    assert state(page)["playerShots"] > 0
    button(page, "Concluir contagem")
    advance(page)
    assert state(page)["displayed"] == 1650
    button(page, "Voltar ao menu")
    button(page, "Novo Jogo")
    advance(page)
    assert state(page)["phase"] == 0 and state(page)["hp"] == 100 and state(page)["level"] == 0

    button(page, "Defeat")
    advance(page)
    assert state(page)["result"] == 1 and state(page)["score"] == 17 and state(page)["lives"] == 0
    x = state(page)["x"]
    advance(page, 80)
    assert state(page)["hp"] == 1 and state(page)["score"] == 17 and state(page)["lives"] == 0
    assert state(page)["playerShots"] == 0 and state(page)["x"] != x
    redraws(page)
    page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"defeat-{width}.png"))

    button(page, "Complete journey")
    s = state(page)
    assert s["result"] == 1 and s["position"] == 176 and s["phase"] == 0
    button(page, "Complete journey")
    assert state(page) == s
    page.locator("canvas:visible").screenshot(path=str(EVIDENCE / f"result-{width}.png"))
    print(f"PASS boss entry, phases, shots, special, damage, 28-step explosion, pause, result and seeded replay at {width}px; {s['steps']} steps, score {s['score']}")


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    names = ["bos", "bos1", "bos2"] + [f"shoot{i}" for i in range(4)] + [f"esp{i}" for i in range(7)]
    for name in names:
        actual = (ROOT / "assets" / f"{name}.png").read_bytes()
        historical = (Path("/home/renanfranca/projects/sifuture/res") / f"{name}.png").read_bytes()
        assert actual == historical, name
    (EVIDENCE / "asset-sha256.txt").write_text("\n".join(
        f"{hashlib.sha256((ROOT / 'assets' / (name + '.png')).read_bytes()).hexdigest()}  {name}.png" for name in names) + "\n")
    with served_build(fixture=ROOT / "tests/boss.kf") as url:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=False,
                                        args=["--no-sandbox", "--headless=new"])
            try:
                print("Chrome", browser.version)
                for width in (320, 1200):
                    page = browser.new_page(viewport={"width": width, "height": 1100}, has_touch=True)
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.clock.install(time=datetime(2026, 1, 1))
                    page.clock.pause_at(datetime(2026, 1, 1))
                    page.goto(url)
                    journey(page, width)
                    assert not errors, errors
                    page.close()
            finally:
                browser.close()


if __name__ == "__main__":
    main()
