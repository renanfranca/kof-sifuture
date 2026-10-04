import argparse
from contextlib import contextmanager
from datetime import datetime
import io
from pathlib import Path
import re
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".agent/tmp/background-items-weapons"
sys.path.insert(0, str(ROOT / "scripts"))
from kof_project import served_build


def canvas_image(page):
    return Image.open(io.BytesIO(page.locator("canvas").screenshot())).convert("RGB")


def sprite_matches(actual, name, x, y):
    sprite = Image.open(ROOT / "assets" / name).convert("RGBA")
    samples = [(px, py, sprite.getpixel((px, py))[:3])
               for py in range(sprite.height) for px in range(sprite.width)
               if sprite.getpixel((px, py))[3] == 255 and 0 <= x + px < 176 and 0 <= y + py < 220][::3]
    assert samples, name
    matches = sum(actual.getpixel((x + px, y + py)) == rgb for px, py, rgb in samples)
    assert matches >= len(samples) * 0.9, (name, x, y, matches, len(samples))


def translucent_blaster_matches(actual, x, y, offset):
    sprite = Image.open(ROOT / "assets/ylwBlaster07.png").convert("RGBA")
    background = Image.open(ROOT / "assets/background.png").convert("RGB")
    samples = 0
    for py in range(15):
        for px in range(sprite.width):
            rgba = sprite.getpixel((px, py))
            if rgba[3] == 0:
                continue
            under = background.getpixel(((x + px + offset) % 60, (y + py - 30) % 60))
            expected = tuple(round(rgba[c] * rgba[3] / 255 + under[c] * (1 - rgba[3] / 255)) for c in range(3))
            observed = actual.getpixel((x + px, y + py))
            assert all(abs(a - b) <= 1 for a, b in zip(observed, expected)), (observed, expected)
            samples += 1
    assert samples > 50


def background_matches(actual, offset):
    sprite = Image.open(ROOT / "assets/background.png").convert("RGB")
    for y in range(42, 50):
        for x in range(176):
            assert actual.getpixel((x, y)) == sprite.getpixel(((x + offset) % 60, y - 30))


def status(page):
    return {key: int(value) for key, value in re.findall(r"(lives|level|charges|x|steps):(\d+)",
                                                       page.locator("#test-status").inner_text())}


def advance(page, steps=1):
    page.clock.run_for(steps * 30)


def collect(page, count=5):
    for _ in range(count):
        page.get_by_role("button", name="Collect evolution", exact=True).click()
    advance(page)


@contextmanager
def scene(browser, url, width=800):
    context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
    try:
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        advance(page)
        yield page
        assert not errors, errors
    finally:
        context.close()


def items_background_and_life(browser, url):
    with scene(browser, url) as page:
        actual = canvas_image(page)
        background_matches(actual, 5)
        sprite_matches(actual, "iten0.png", 99, 50)
        sprite_matches(actual, "life0.png", 129, 150)
        advance(page)
        actual = canvas_image(page)
        sprite_matches(actual, "iten1.png", 98, 50)
        sprite_matches(actual, "life1.png", 128, 150)
        advance(page, 18)
        sprite_matches(canvas_image(page), "life10.png", 110, 150)
        advance(page, 2)
        sprite_matches(canvas_image(page), "life9.png", 108, 150)
        advance(page, 18)
        sprite_matches(canvas_image(page), "life0.png", 90, 150)
        before = canvas_image(page).crop((0, 0, 176, 30)).tobytes()
        page.get_by_role("button", name="Collect life", exact=True).click()
        sprite_matches(canvas_image(page), "effect0.png", 49, 84)
        advance(page, 2)
        sprite_matches(canvas_image(page), "effect1.png", 47, 84)
        advance(page, 2)
        sprite_matches(canvas_image(page), "effect2.png", 45, 84)
        assert status(page)["lives"] == 4
        assert canvas_image(page).crop((0, 0, 176, 30)).tobytes() != before
        advance(page, 2)
        assert status(page)["lives"] == 4
        page.get_by_role("button", name="Pausar", exact=True).click()
        frozen = canvas_image(page).tobytes()
        steps = status(page)["steps"]
        advance(page, 20)
        assert canvas_image(page).tobytes() == frozen and status(page)["steps"] == steps
        for _ in range(3):
            page.get_by_role("button", name="Repaint", exact=True).click()
        assert canvas_image(page).tobytes() == frozen
    print("PASS background tiling, item animation, three collection frames, lives 3 to 4 and paused redraw")


def weapon_frames(browser, url):
    with scene(browser, url) as page:
        collect(page, 1)
        remaining = 13 - status(page)["steps"]
        advance(page, remaining)
        page.get_by_role("button", name="Move ship down", exact=True).click()
        sprite_matches(canvas_image(page), "laser00.png", 60, 108)
        advance(page)
        sprite_matches(canvas_image(page), "laser00.png", 65, 108)
        advance(page)
        sprite_matches(canvas_image(page), "laser01.png", 70, 108)
        advance(page, 2)
        sprite_matches(canvas_image(page), "laser02.png", 80, 108)
    with scene(browser, url) as page:
        page.get_by_role("button", name="Blaster scene", exact=True).click()
        sprite_matches(canvas_image(page), "ylwBlaster00.png", 40, 100)
        for name, x in (("ylwBlaster00.png", 45), ("ylwBlaster01.png", 50),
                        ("ylwBlaster02.png", 55), ("ylwBlaster03.png", 58), ("ylwBlaster08.png", 63)):
            advance(page)
            sprite_matches(canvas_image(page), name, x, 100)
        page.get_by_role("button", name="Blaster impact", exact=True).click()
        page.get_by_role("button", name="Blaster impact", exact=True).click()
        sprite_matches(canvas_image(page), "ylwBlaster04.png", 73, 100)
        for name, x, y in (("ylwBlaster05.png", 75, 86), ("ylwBlaster06.png", 77, 85)):
            advance(page)
            sprite_matches(canvas_image(page), name, x, y)
        advance(page)
        translucent_blaster_matches(canvas_image(page), 80, 85, status(page)["steps"] * 5 % 60)
    with scene(browser, url) as page:
        collect(page, 5)
        sprite_matches(canvas_image(page), "especialActivated1.png", 50, 21)
        page.get_by_role("button", name="Especial", exact=True).click()
        page.get_by_role("button", name="Blaster scene", exact=True).click()
        advance(page, 54)
        sprite_matches(canvas_image(page), "e3.png", 5, 94)
        advance(page, 16)
        sprite_matches(canvas_image(page), "e0.png", -288, 40)
        sprite_matches(canvas_image(page), "e6.png", -288, 160)
    with scene(browser, url) as page:
        collect(page, 5)
        page.get_by_role("button", name="Especial", exact=True).click()
        page.get_by_role("button", name="Special impact", exact=True).click()
        sprite_matches(canvas_image(page), "e4.png", 6, 94)
        for _ in range(9):
            page.get_by_role("button", name="Special impact", exact=True).click()
        advance(page, 3)
        sprite_matches(canvas_image(page), "e5.png", 6, 94)
    for button, hit_frame, death_frame, y in (("Orange impact", "e1.png", "e2.png", 40),
                                             ("Dark impact", "e7.png", "e8.png", 160)):
        with scene(browser, url) as page:
            collect(page, 5)
            page.get_by_role("button", name="Especial", exact=True).click()
            page.get_by_role("button", name=button, exact=True).click()
            sprite_matches(canvas_image(page), hit_frame, 5, y)
            for _ in range(9):
                page.get_by_role("button", name=button, exact=True).click()
            advance(page, 3)
            sprite_matches(canvas_image(page), death_frame, 5, y)
    print("PASS animated laser, blaster launch/impact and all special colors with hit/death frames")


def keyboard_edges(browser, url):
    with scene(browser, url) as page:
        collect(page, 5)
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.down("ArrowRight")
        page.keyboard.down("1")
        advance(page, 2)
        assert status(page)["x"] == 50 and status(page)["charges"] == 1
        assert overlay.evaluate("button => button === document.activeElement")
        page.keyboard.up("1")
        page.keyboard.up("ArrowRight")
    for key in ("1", "Enter", "Space"):
        with scene(browser, url) as page:
            collect(page, 5)
            special = page.get_by_role("button", name="Especial", exact=True)
            page.get_by_role("button", name="→", exact=True).focus()
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 2, key
            special.focus()
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 2, key
            page.keyboard.up(key)
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 1, key
            page.keyboard.up(key)
    for key in ("1", "Enter", "Space"):
        with scene(browser, url) as page:
            collect(page, 5)
            special = page.get_by_role("button", name="Especial", exact=True)
            special.focus()
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 1
            assert special.evaluate("button => button === document.activeElement"), key
            assert special.is_enabled(), key
            assert special.evaluate("button => getComputedStyle(button).opacity") == "0.5", key

            page.keyboard.up(key)
            assert special.is_disabled(), key
            advance(page, 170)
            assert special.is_enabled(), key
            assert special.evaluate("button => getComputedStyle(button).opacity") == "1", key
            special.focus()
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 0, key
            page.keyboard.up(key)
    for destination in ("Ativar teclado do jogo", "→"):
        with scene(browser, url) as page:
            collect(page, 5)
            special = page.get_by_role("button", name="Especial", exact=True)
            special.focus()
            page.keyboard.down("Space")
            advance(page)
            assert status(page)["charges"] == 1

            page.get_by_role("button", name=destination, exact=True).focus()
            assert special.is_disabled()
            page.keyboard.up("Space")
            advance(page, 170)
            special.focus()
            page.keyboard.down("Space")
            advance(page)
            assert status(page)["charges"] == 0, destination
            page.keyboard.up("Space")
    with scene(browser, url) as page:
        collect(page, 6)
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.down("1")
        advance(page)
        assert status(page)["charges"] == 2
        page.keyboard.down("1")
        advance(page, 170)
        assert status(page)["charges"] == 2
        page.keyboard.down("1")
        advance(page)
        assert status(page)["charges"] == 2
        page.keyboard.up("1")
        page.keyboard.down("1")
        advance(page)
        assert status(page)["charges"] == 1
        page.keyboard.up("1")
    with scene(browser, url) as page:
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.down("1")
        collect(page, 4)
        overlay.focus()
        page.keyboard.down("1")
        advance(page)
        assert status(page)["charges"] == 1
        page.keyboard.up("1")
        page.keyboard.down("1")
        advance(page)
        assert status(page)["charges"] == 0
        page.keyboard.up("1")
    with scene(browser, url) as page:
        collect(page, 4)
        page.get_by_role("button", name="Make restarting", exact=True).click()
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.down("1")
        advance(page, 45)
        page.keyboard.down("1")
        advance(page)
        assert status(page)["charges"] == 1
        page.keyboard.up("1")
        page.keyboard.down("1")
        advance(page)
        assert status(page)["charges"] == 0
        page.keyboard.up("1")
    for key in ("1", "Enter", "Space"):
        with scene(browser, url) as page:
            collect(page, 5)
            special = page.get_by_role("button", name="Especial", exact=True)
            special.focus()
            page.keyboard.down(key)
            advance(page, 170)
            assert special.evaluate("button => button === document.activeElement"), key
            assert special.is_enabled(), key
            assert special.evaluate("button => getComputedStyle(button).opacity") == "1", key
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 1
            page.keyboard.up(key)
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 0
            page.keyboard.up(key)
    for release_order in (("1", "Enter", "Space"), ("Space", "1", "Enter"), ("Enter", "Space", "1")):
        with scene(browser, url) as page:
            collect(page, 5)
            special = page.get_by_role("button", name="Especial", exact=True)
            special.focus()
            for key in ("1", "Enter", "Space"):
                page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 1
            for key in release_order[:-1]:
                page.keyboard.up(key)
                assert special.is_enabled(), release_order
                assert special.evaluate("button => button === document.activeElement"), release_order
            page.keyboard.up(release_order[-1])
            assert special.is_disabled(), release_order
            advance(page, 170)
            assert status(page)["charges"] == 1, release_order
            special.focus()
            page.keyboard.down(release_order[-1])
            advance(page)
            assert status(page)["charges"] == 0, release_order
            page.keyboard.up(release_order[-1])
    with scene(browser, url) as page:
        collect(page, 5)
        special = page.get_by_role("button", name="Especial", exact=True)
        special.focus()
        page.keyboard.down("1")
        page.keyboard.down("Enter")
        page.keyboard.up("1")
        advance(page, 170)
        assert status(page)["charges"] == 1
        assert special.evaluate("button => button === document.activeElement")
        page.keyboard.down("Enter")
        advance(page)
        assert status(page)["charges"] == 1
        page.keyboard.up("Enter")
        page.keyboard.down("Enter")
        advance(page)
        assert status(page)["charges"] == 0
        page.keyboard.up("Enter")
    for key in ("1", "Enter", "Space"):
        with scene(browser, url) as page:
            collect(page, 5)
            special = page.get_by_role("button", name="Especial", exact=True)
            special.focus()
            page.keyboard.down(key)
            advance(page)
            page.get_by_role("button", name="Repaint", exact=True).focus()
            assert special.is_disabled(), key
            page.keyboard.up(key)
            advance(page, 170)
            special.focus()
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 1, key
            page.keyboard.up(key)
            page.keyboard.down(key)
            advance(page)
            assert status(page)["charges"] == 0, key
            page.keyboard.up(key)
    print("PASS special focus retained until last release, cross-control keyup, simultaneous keys and outside-release lock")
    print("PASS key 1 and button keyboard repeat suppression, no queued attempts and native click deduplication")


def contact(button, identity):
    box = button.bounding_box()
    return {"x": box["x"] + box["width"] / 2, "y": box["y"] + box["height"] / 2, "id": identity}


def simultaneous_touch(browser, url):
    for release_special_first in (True, False):
        with scene(browser, url) as page:
            collect(page, 5)
            east = contact(page.get_by_role("button", name="→", exact=True), 1)
            special = contact(page.get_by_role("button", name="Especial", exact=True), 2)
            session = page.context.new_cdp_session(page)
            session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [east]})
            advance(page, 3)
            assert status(page)["x"] == 55
            session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [east, special]})
            advance(page, 3)
            assert status(page)["x"] == 70 and status(page)["charges"] == 1
            ended = [special] if release_special_first else [east]
            session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": ended})
            advance(page, 2)
            expected_x = 80 if release_special_first else 70
            assert status(page)["x"] == expected_x and status(page)["charges"] == 1, (release_special_first, expected_x, status(page))
            session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
            advance(page, 2)
            assert status(page)["x"] == expected_x and status(page)["charges"] == 1, (release_special_first, expected_x, status(page))
    with scene(browser, url) as page:
        collect(page, 5)
        east = contact(page.get_by_role("button", name="→", exact=True), 1)
        special = contact(page.get_by_role("button", name="Especial", exact=True), 2)
        session = page.context.new_cdp_session(page)
        session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [east]})
        session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [east, special]})
        advance(page, 2)
        session.send("Input.dispatchTouchEvent", {"type": "touchCancel", "touchPoints": []})
        advance(page, 170)
        assert status(page)["x"] == 50 and status(page)["charges"] == 1
        special["id"] = 3
        session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [special]})
        advance(page)
        assert status(page)["charges"] == 0
        session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    print("PASS two simultaneous contacts, each release order, touch cancellation and subsequent new press")


def layout_and_indicator(browser, url):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    release_evidence = ROOT / ".agent/tmp/special-key-release"
    release_evidence.mkdir(parents=True, exist_ok=True)
    for width in (320, 1200):
        with scene(browser, url, width) as page:
            special = page.get_by_role("button", name="Especial", exact=True)
            assert special.is_disabled()
            collect(page, 5)
            assert special.is_enabled()
            box = special.bounding_box()
            north = page.get_by_role("button", name="↑", exact=True).bounding_box()
            south = page.get_by_role("button", name="↓", exact=True).bounding_box()
            east = page.get_by_role("button", name="→", exact=True).bounding_box()
            assert (box["width"], box["height"]) == (72, 64)
            assert abs(box["x"] - east["x"] - east["width"] - 16) < 1
            assert abs(box["y"] + 32 - (north["y"] + south["y"] + south["height"]) / 2) < 1
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            sprite_matches(canvas_image(page), "especialActivated1.png", 50, 21)
            page.screenshot(path=str(EVIDENCE / f"layout-{width}.png"), full_page=True)
            special.click()
            advance(page)
            assert status(page)["charges"] == 1 and special.is_disabled()
            sprite_matches(canvas_image(page), "especialActivated1.png", 50, 21)
            page.get_by_role("button", name="Pausar", exact=True).click()
            frozen = canvas_image(page).tobytes()
            advance(page, 20)
            assert canvas_image(page).tobytes() == frozen
            sprite_matches(canvas_image(page), "especialActivated1.png", 50, 21)
        with scene(browser, url, width) as page:
            collect(page, 5)
            special = page.get_by_role("button", name="Especial", exact=True)
            special.focus()
            box = special.bounding_box()
            page.keyboard.down("1")
            advance(page)
            assert special.is_enabled()
            assert special.bounding_box() == box
            assert special.evaluate("button => getComputedStyle(button).opacity") == "0.5"
            page.screenshot(path=str(release_evidence / f"held-{width}.png"), full_page=True)
            page.keyboard.up("1")
            assert special.is_disabled()
            assert special.bounding_box() == box
            page.screenshot(path=str(release_evidence / f"released-{width}.png"), full_page=True)
            advance(page, 170)
            assert special.is_enabled()
            assert special.bounding_box() == box
            assert special.evaluate("button => getComputedStyle(button).opacity") == "1"
            page.screenshot(path=str(release_evidence / f"available-{width}.png"), full_page=True)
    with scene(browser, url) as page:
        collect(page, 5)
        page.get_by_role("button", name="Move ship up", exact=True).click()
        before = canvas_image(page).crop((80, 0, 176, 30)).tobytes()
        page.get_by_role("button", name="Especial", exact=True).click()
        advance(page, 100)
        assert canvas_image(page).crop((80, 0, 176, 30)).tobytes() == before
        sprite_matches(canvas_image(page), "StageMiddle.png", 80, 0)
        sprite_matches(canvas_image(page), "especialActivated1.png", 50, 21)
    print("PASS 320px/desktop layout, 72x64 button, 16px separation and retained icon during special/paused state")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kof")
    args = parser.parse_args()
    with served_build(kof=args.kof, fixture=ROOT / "tests/weapons.kf") as url:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/google-chrome", headless=False,
                                                 args=["--no-sandbox", "--headless=new"])
            try:
                items_background_and_life(browser, url)
                weapon_frames(browser, url)
                keyboard_edges(browser, url)
                simultaneous_touch(browser, url)
                layout_and_indicator(browser, url)
            finally:
                browser.close()
    with served_build(kof=args.kof) as url:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/google-chrome", headless=False,
                                                 args=["--no-sandbox", "--headless=new"])
            try:
                for width in (320, 1200):
                    page = browser.new_page(viewport={"width": width, "height": 800})
                    page.clock.install(time=datetime(2026, 1, 1))
                    page.clock.pause_at(datetime(2026, 1, 1))
                    page.goto(url)
                    advance(page)
                    page.get_by_role("button", name="Novo Jogo", exact=True).click()
                    advance(page, 45)
                    assert page.get_by_role("button", name="Especial", exact=True).is_disabled()
                    page.screenshot(path=str(EVIDENCE / f"application-{width}.png"), full_page=True)
                    page.close()
            finally:
                browser.close()
    print("PASS deterministic background, collection, weapon evolution and special journey in Chrome")


if __name__ == "__main__":
    main()
