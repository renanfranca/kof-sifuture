from datetime import datetime
import io
import re
import sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from kof_project import served_build

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
EVIDENCE = ROOT / ".agent/tmp/stage-browser"


def bitmap(page):
    return Image.open(io.BytesIO(page.locator("canvas").screenshot())).convert("RGB")


def sprite(page, name, x, y, *, occluded=()):
    actual = bitmap(page)
    expected = Image.open(ASSETS / name).convert("RGBA")
    samples = 0
    for py in range(expected.height):
        for px in range(expected.width):
            rgba = expected.getpixel((px, py))
            if any(left <= x + px < right and top <= y + py < bottom
                   for left, top, right, bottom in occluded):
                continue
            if rgba[3] != 255 or not (0 <= x + px < 176 and 0 <= y + py < 220):
                continue
            assert actual.getpixel((x + px, y + py)) == rgba[:3], (name, x + px, y + py)
            samples += 1
    assert samples > 0, name


def state(page):
    return {key: int(value) for key, value in re.findall(r"(\w+):(\d+)",
                                                        page.locator("#stage-status").inner_text())}


def advance(page, steps=1):
    page.clock.run_for(steps * 30)


def open_scene(browser, url, width):
    page = browser.new_page(viewport={"width": width, "height": 1000}, has_touch=True)
    page.clock.install(time=datetime(2026, 1, 1))
    page.clock.pause_at(datetime(2026, 1, 1))
    page.goto(url)
    advance(page)
    return page


def hud_and_pause(page, width):
    sprite(page, "StageBeginer.png", 0, 0)
    sprite(page, "3lives.png", 5, 9, occluded=((0, 0, 8, 30),))
    sprite(page, "score.png", 88, 7)
    for name, x in (("1.png", 112), ("5.png", 128), ("0.png", 144), ("0.png", 160)):
        sprite(page, name, x, 0)
    sprite(page, "2lives.png", 146, 21)
    sprite(page, "x.png", 140, 21, occluded=((146, 21, 176, 42),))
    sprite(page, "3.png", 126, 21, occluded=((140, 21, 176, 42),))
    sprite(page, "especialActivated1.png", 50, 21)
    for label, name in (("One life", "1lives.png"), ("Two lives", "2lives.png"),
                        ("Four lives", "3lives.png")):
        page.get_by_role("button", name=label, exact=True).click()
        sprite(page, name, 5, 9, occluded=((0, 0, 8, 30),))
    advance(page, 8)
    assert state(page)["steps"] == 9 and state(page)["position"] == 5
    advance(page)
    assert state(page)["position"] == 6
    sprite(page, "3lives.png", 6, 9, occluded=((0, 0, 8, 30),))
    page.get_by_role("button", name="Pausar", exact=True).click()
    frozen = bitmap(page).tobytes()
    before = state(page)
    advance(page, 20)
    assert state(page) == before and bitmap(page).tobytes() == frozen
    for _ in range(3):
        page.get_by_role("button", name="Repaint", exact=True).click()
    assert state(page) == before and bitmap(page).tobytes() == frozen
    page.get_by_role("button", name="Continuar", exact=True).click()
    advance(page)
    assert state(page)["steps"] == 11
    page.locator("canvas").screenshot(path=str(EVIDENCE / f"hud-{width}.png"))


def right_input_clearing(page, width):
    for action in ("Pausar", "Repaint"):
        page.get_by_role("button", name="Prepare right finish", exact=True).click()
        page.get_by_role("button", name="Ativar teclado do jogo").click()
        page.keyboard.down("ArrowRight")
        advance(page)
        sprite(page, "Middle2.png", 45, 150)
        page.get_by_role("button", name=action, exact=True).click()
        sprite(page, "Middle.png", 45, 150)
        page.keyboard.up("ArrowRight")
        advance(page)
        assert state(page)["shipX"] == 45
        sprite(page, "Middle.png", 45, 150)
        page.locator("canvas").screenshot(path=str(EVIDENCE / f"right-cleared-{action}-{width}.png"))


def right_held_result(page, width):
    page.get_by_role("button", name="Prepare right finish", exact=True).click()
    page.get_by_role("button", name="Ativar teclado do jogo").click()
    page.keyboard.down("ArrowRight")
    advance(page)
    assert state(page)["shipX"] == 45
    sprite(page, "Middle2.png", 45, 150)
    advance(page)
    assert page.get_by_role("button", name="Concluir contagem", exact=True).count() == 1
    assert state(page)["shipX"] == 50 and state(page)["shipY"] == 150
    sprite(page, "Middle.png", 50, 150)
    page.locator("canvas").screenshot(path=str(EVIDENCE / f"right-result-entry-{width}.png"))
    page.keyboard.up("ArrowRight")
    for expected in (5, 10, 15, 17):
        advance(page)
        assert state(page)["displayed"] == expected
        assert state(page)["shipX"] == 50 and state(page)["shipY"] == 150
        sprite(page, "Middle.png", 50, 150)
    assert state(page)["steps"] == 1710 and state(page)["score"] == 17
    page.locator("canvas").screenshot(path=str(EVIDENCE / f"right-result-release-{width}.png"))


def moving_result(page, width):
    page.get_by_role("button", name="Finish stage", exact=True).click()
    assert page.get_by_role("button", name="Concluir contagem", exact=True).count() == 1
    sprite(page, "score1.png", 53, 86)
    sprite(page, "0.png", 106, 86)
    initial = state(page)
    initial_pixels = bitmap(page).tobytes()
    for _ in range(3):
        page.get_by_role("button", name="Repaint", exact=True).click()
    assert state(page) == initial and bitmap(page).tobytes() == initial_pixels
    advance(page)
    assert state(page)["displayed"] == 5 and state(page)["explosion"] == 30
    sprite(page, "5.png", 106, 86)
    assert bitmap(page).tobytes() != initial_pixels
    page.get_by_role("button", name="Ativar teclado do jogo").click()
    page.keyboard.down("ArrowRight")
    page.keyboard.down("1")
    page.keyboard.up("1")
    page.keyboard.up("ArrowRight")
    page.keyboard.down("Enter")
    page.keyboard.down("Enter")
    assert page.get_by_role("button", name="Voltar ao menu", exact=True).count() == 1
    sprite(page, "score1.png", 45, 86)
    sprite(page, "1.png", 98, 86)
    sprite(page, "7.png", 114, 86)
    sprite(page, "result0.png", 31, 113)
    advance(page, 20)
    final = state(page)
    assert final["score"] == 17 and final["displayed"] == 17 and final["steps"] == 1710
    assert final["lives"] == initial["lives"] and final["charges"] == 2 and final["level"] == 3
    assert final["position"] == 176 and final["explosion"] == 30
    assert page.get_by_role("button", name="Voltar ao menu", exact=True).count() == 1
    page.locator("canvas").screenshot(path=str(EVIDENCE / f"result-{width}.png"))
    page.keyboard.up("Enter")
    page.keyboard.press("Enter")
    assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1
    page.get_by_role("button", name="Zero result", exact=True).click()
    assert page.get_by_role("button", name="Voltar ao menu", exact=True).count() == 1
    sprite(page, "0.png", 106, 86)
    page.get_by_role("button", name="Voltar ao menu", exact=True).tap()
    assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1


def natural_count_and_touch(page):
    page.get_by_role("button", name="Finish stage", exact=True).click()
    for expected in (5, 10, 15, 17):
        advance(page)
        assert state(page)["displayed"] == expected
    assert page.get_by_role("button", name="Voltar ao menu", exact=True).count() == 1
    page.get_by_role("button", name="Voltar ao menu", exact=True).tap()
    page.get_by_role("button", name="Finish stage", exact=True).click()
    page.get_by_role("button", name="Concluir contagem", exact=True).tap()
    assert page.get_by_role("button", name="Voltar ao menu", exact=True).count() == 1
    page.get_by_role("button", name="Voltar ao menu", exact=True).tap()
    assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1


def native_confirmation(page):
    page.get_by_role("button", name="Finish stage", exact=True).click()
    action = page.locator("#game-action")
    action.focus()
    page.keyboard.down("Enter")
    page.keyboard.down("Enter")
    assert action.inner_text() == "Voltar ao menu"
    advance(page, 10)
    assert action.inner_text() == "Voltar ao menu"
    page.keyboard.up("Enter")
    page.keyboard.press("Enter")
    assert action.inner_text() == "Novo Jogo"


def vertical_and_full_journey(page):
    page.get_by_role("button", name="Vertical impact", exact=True).click()
    sprite(page, "meteor0C0.png", 80, 60)
    advance(page)
    sprite(page, "meteor0C1.png", 80, 61)
    advance(page)
    sprite(page, "meteor0C2.png", 80, 62)
    advance(page)
    actual = bitmap(page)
    background = Image.open(ASSETS / "background.png").convert("RGB")
    offset = state(page)["steps"] * 5 % 60
    assert actual.getpixel((85, 65)) == background.getpixel(((85 + offset) % 60, 35))
    page.get_by_role("button", name="Full journey", exact=True).click()
    assert state(page)["steps"] == 1709 and state(page)["position"] == 175
    assert page.get_by_role("button", name="Pausar", exact=True).count() == 1
    advance(page)
    assert state(page)["steps"] == 1710 and state(page)["position"] == 176
    score = state(page)["score"]
    advance(page, 100)
    assert state(page)["steps"] == 1710 and state(page)["score"] == score
    if page.get_by_role("button", name="Concluir contagem", exact=True).count():
        page.get_by_role("button", name="Concluir contagem", exact=True).click()
    assert page.get_by_role("button", name="Voltar ao menu", exact=True).count() == 1


def defeat(page):
    page.get_by_role("button", name="Defeat", exact=True).click()
    assert state(page)["lives"] == 0 and state(page)["explosion"] == 30
    advance(page, 100)
    assert state(page)["lives"] == 0 and state(page)["explosion"] == 30
    assert state(page)["steps"] == 2 and state(page)["score"] == 1500
    assert state(page)["displayed"] == 500
    page.get_by_role("button", name="Concluir contagem", exact=True).click()
    assert page.get_by_role("button", name="Voltar ao menu", exact=True).count() == 1
    page.get_by_role("button", name="Voltar ao menu", exact=True).click()
    assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1


def boundaries(page):
    for total, message, x in ((1499, 0, 31), (1500, 1, 22), (2199, 1, 22),
                              (2200, 2, 54), (3299, 2, 54), (3300, 3, 26)):
        page.get_by_role("button", name=f"Result {total}", exact=True).click()
        page.get_by_role("button", name="Concluir contagem", exact=True).click()
        sprite(page, f"result{message}.png", x, 113)
        advance(page)
        assert state(page)["score"] == total and state(page)["displayed"] == total
        assert state(page)["lives"] == 0 and state(page)["explosion"] == 0
        page.get_by_role("button", name="Voltar ao menu", exact=True).click()
        assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with served_build(fixture=ROOT / "tests/stage.kf") as url, served_build() as app_url:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=False,
                                        args=["--no-sandbox", "--headless=new"])
            try:
                for width in (320, 1200):
                    for journey in (hud_and_pause, moving_result, right_held_result, right_input_clearing):
                        page = open_scene(browser, url, width)
                        errors = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        journey(page, width)
                        assert not errors, errors
                        page.close()
                    for journey in (natural_count_and_touch, native_confirmation, vertical_and_full_journey, boundaries, defeat):
                        page = open_scene(browser, url, width)
                        errors = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        journey(page)
                        assert not errors, errors
                        page.close()
                    page = open_scene(browser, app_url, width)
                    page.get_by_role("button", name="Novo Jogo", exact=True).click()
                    advance(page, 10)
                    sprite(page, "3lives.png", 6, 9, occluded=((0, 0, 8, 30),))
                    assert page.locator("canvas").bounding_box()["width"] == 176
                    page.screenshot(path=str(EVIDENCE / f"app-{width}.png"))
                    page.close()
                print("PASS stage HUD, vertical impacts, full journey, moving result, exact count, boundaries and two confirmations")
                print("PASS held right restores Middle.png on result entry and release, frozen ship and exact score at both widths")
                print("PASS pause and lost canvas focus immediately restore Middle.png at both widths")
                print("PASS Chrome", browser.version, "at 320 and 1200 pixels; repaint does not advance simulation")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
