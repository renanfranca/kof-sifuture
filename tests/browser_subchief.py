from datetime import datetime
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from kof_project import served_build
from browser_stage import bitmap, sprite

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".agent/tmp/subchief-browser"


def state(page):
    return {key: int(value) for key, value in re.findall(
        r"(\w+):(-?\d+)", page.locator("#subchief-status").inner_text())}


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


def journey(page, width):
    assert state(page)["position"] == 87 and state(page)["normal"] == 0
    advance(page)
    assert state(page)["position"] == 89 and state(page)["normal"] == 1
    advance(page, 10)
    assert state(page)["position"] == 89 and state(page)["steps"] == 840
    freeze(page)
    redraws(page)

    button(page, "Encounter")
    advance(page)
    sprite(page, "subchief.png", 121, 100)
    page.locator("canvas").screenshot(path=str(EVIDENCE / f"combat-{width}.png"))
    redraws(page)
    button(page, "Shots")
    advance(page)
    assert state(page)["shots"] == 1 and state(page)["shotX"] == 154
    sprite(page, "laser0.png", 154, 113, occluded=((165, 100, 193, 126),))
    freeze(page)
    advance(page)
    assert state(page)["shotX"] == 150
    advance(page, 11)
    assert state(page)["shots"] == 2
    advance(page, 12)
    assert state(page)["shots"] == 3 and state(page)["lifetime"] == 1
    redraws(page)

    button(page, "Body contact")
    advance(page)
    assert state(page)["shipExplosion"] == 1 and state(page)["hp"] == 29
    button(page, "Invulnerable contact")
    advance(page)
    assert state(page)["shipExplosion"] == 0 and state(page)["hp"] == 30

    button(page, "Prepare special")
    button(page, "Ativar teclado do jogo")
    page.keyboard.down("1")
    page.keyboard.down("1")
    assert page.get_by_role("button", name="Especial", exact=True).count() == 1
    advance(page, 36)
    assert state(page)["charges"] == 1 and state(page)["blueLives"] < 10 and state(page)["hp"] < 30
    sprite(page, "especialActivated1.png", 50, 21)
    page.locator("canvas").screenshot(path=str(EVIDENCE / f"special-hud-{width}.png"))
    page.keyboard.up("1")
    freeze(page)
    redraws(page)

    button(page, "Fatal laser")
    advance(page)
    assert state(page)["score"] == 600 and state(page)["explosion"] == 1
    assert state(page)["frame"] == 0 and state(page)["position"] == 89
    offsets = (0, 1, 4, 7, 10, 16, 22, 31, 40, 55)
    for frame, offset in enumerate(offsets):
        if frame:
            advance(page, 3)
        assert state(page)["frame"] == frame and state(page)["explosionX"] == 121 - offset
        assert state(page)["position"] == 89 and state(page)["score"] == 600
        occluded = ((121, 100, 161, 130),) if frame == 0 else ()
        sprite(page, f"explosion{frame}.png", 121 - offset, 100, occluded=occluded)
        redraws(page)
        if frame == 4:
            freeze(page)
        page.locator("canvas").screenshot(path=str(EVIDENCE / f"explosion-{frame}-{width}.png"))
    advance(page, 3)
    assert state(page)["normal"] == 0 and state(page)["explosion"] == 0
    advance(page, 10)
    assert state(page)["position"] == 90 and state(page)["score"] == 600

    button(page, "Defeat encounter")
    advance(page)
    assert state(page)["result"] == 1 and state(page)["lives"] == 0
    x = state(page)["x"]
    advance(page, 20)
    assert state(page)["x"] != x and state(page)["score"] == 17
    assert state(page)["hp"] == 1 and state(page)["lives"] == 0 and state(page)["position"] == 89
    redraws(page)
    button(page, "Voltar ao menu")
    button(page, "Novo Jogo")
    advance(page)
    assert state(page)["hp"] == 30 and state(page)["position"] == 5
    assert state(page)["normal"] == 0 and state(page)["shots"] == 0 and state(page)["score"] == 0

    button(page, "Complete journey")
    assert state(page)["result"] == 1 and state(page)["position"] == 176
    assert state(page)["steps"] > 1710 and state(page)["normal"] == 0
    total = state(page)["score"]
    print(f"PASS full seeded encounter journey at {width}px: {state(page)['steps']} steps, score {total}, position 176")
    button(page, "Concluir contagem")
    advance(page)
    assert state(page)["displayed"] == total
    button(page, "Voltar ao menu")


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with served_build(fixture=ROOT / "tests/subchief.kf") as url, served_build() as app_url:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=False,
                                        args=["--no-sandbox", "--headless=new"])
            try:
                for width in (320, 1200):
                    page = browser.new_page(viewport={"width": width, "height": 1000}, has_touch=True)
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.clock.install(time=datetime(2026, 1, 1))
                    page.clock.pause_at(datetime(2026, 1, 1))
                    page.goto(url)
                    journey(page, width)
                    assert not errors, errors
                    page.close()
                    app = browser.new_page(viewport={"width": width, "height": 1000})
                    app.clock.install(time=datetime(2026, 1, 1))
                    app.clock.pause_at(datetime(2026, 1, 1))
                    app.goto(app_url)
                    button(app, "Novo Jogo")
                    advance(app, 10)
                    app.screenshot(path=str(EVIDENCE / f"app-{width}.png"))
                    app.close()
                print("PASS midpoint combat, three shots, invulnerability, real special controls, ten explosion sprites, resumed track, defeat and new game")
                print(f"PASS Chrome {browser.version} at 320 and 1200 pixels; pause and repaint preserve simulation")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
