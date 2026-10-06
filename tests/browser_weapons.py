import argparse
from contextlib import contextmanager
from datetime import datetime
import io
import itertools
import json
from pathlib import Path
import re
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".agent/tmp/background-items-weapons"
sys.path.insert(0, str(ROOT / "scripts"))
from kof_project import served_build
from browser_controls import TouchContacts


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
    return {key: int(value) for key, value in re.findall(r"(lives|level|charges|x|y|steps):(\d+)",
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
    evidence = []
    for release_order in itertools.permutations(("→", "↑", "Especial")):
        with scene(browser, url) as page:
            collect(page, 5)
            page.get_by_role("button", name="Center ship", exact=True).click()
            page.locator("canvas").scroll_into_view_if_needed()
            advance(page)
            assert (status(page)["x"], status(page)["y"], status(page)["charges"]) == (60, 100, 2)
            touch = TouchContacts(page)
            touch.press("→")
            advance(page)
            assert (status(page)["x"], status(page)["y"]) == (65, 100)
            touch.press("↑")
            advance(page)
            assert (status(page)["x"], status(page)["y"]) == (70, 95)
            touch.press("Especial")
            advance(page)
            assert (status(page)["x"], status(page)["y"], status(page)["charges"]) == (75, 90, 1)
            x, y = 75, 90
            snapshots = []
            for label in release_order:
                touch.release(label)
                advance(page)
                x += 5 if "→" in touch.contacts else 0
                y -= 5 if "↑" in touch.contacts else 0
                observed = status(page)
                assert (observed["x"], observed["y"], observed["charges"]) == (x, y, 1), (release_order, label, observed)
                snapshots.append({"released": label, "x": x, "y": y, "charges": observed["charges"]})
            advance(page, 2)
            assert (status(page)["x"], status(page)["y"], status(page)["charges"]) == (x, y, 1)
            evidence.append({"release_order": release_order, "snapshots": snapshots, "events": touch.events()})
    with scene(browser, url) as page:
        collect(page, 5)
        page.get_by_role("button", name="Center ship", exact=True).click()
        page.locator("canvas").scroll_into_view_if_needed()
        touch = TouchContacts(page)
        touch.press("→", "↑")
        touch.press("Especial")
        advance(page, 2)
        assert (status(page)["x"], status(page)["y"], status(page)["charges"]) == (70, 90, 1)
        touch.cancel()
        advance(page, 170)
        assert (status(page)["x"], status(page)["y"], status(page)["charges"]) == (70, 90, 1)
        touch.press("Especial")
        advance(page)
        assert status(page)["charges"] == 0
        touch.release("Especial")
        evidence.append({"case": "total-cancel-and-new-special", "events": touch.events()})
    destination = ROOT / ".agent/tmp/sifuture-controls"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "special-touch-events.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS diagonal + third-finger special: six release orders, exact pointerup targets/ids, one charge, total cancel and new press")


def special_presentation(special):
    return special.evaluate("""button => {
        const range = document.createRange();
        range.selectNodeContents(button);
        const text = range.getBoundingClientRect();
        const box = button.getBoundingClientRect();
        return {box: {x: box.x, y: box.y, width: box.width, height: box.height},
                writing_mode: getComputedStyle(button).writingMode,
                text: button.textContent, id: button.id,
                text_box: {x: text.x, y: text.y, width: text.width, height: text.height}};
    }""")


def special_touch_extent(browser, url):
    evidence = []
    for width in (320, 1200):
        for region, offset in (("top", 8), ("middle", 110), ("bottom", 212)):
            with scene(browser, url, width) as page:
                collect(page, 5)
                page.locator("canvas").scroll_into_view_if_needed()
                special = page.get_by_role("button", name="Especial", exact=True)
                presentation = special_presentation(special)
                canvas = page.locator("canvas").bounding_box()
                point = {"x": canvas["x"] + 176 + 16 + 28, "y": canvas["y"] + offset}
                assert status(page)["charges"] == 2 and special.is_enabled()
                assert page.evaluate("p => document.elementFromPoint(p.x, p.y).id", point) == "game-special"

                touch = TouchContacts(page)
                touch.press_at({"Especial": (point["x"], point["y"])})
                advance(page)
                assert status(page)["charges"] == 1 and special.is_disabled()
                assert special_presentation(special) == presentation
                advance(page, 3)
                assert status(page)["charges"] == 1
                touch.release("Especial")
                advance(page)
                assert status(page)["charges"] == 1
                page.get_by_role("button", name="Move ship down", exact=True).click()
                advance(page, 49)
                sprite_matches(canvas_image(page), "e3.png", 5, 94)
                assert status(page)["charges"] == 1
                evidence.append({"viewport": width, "region": region, "point": point,
                                 "charges_before": 2, "charges_after": status(page)["charges"],
                                 "presentation": presentation, "events": touch.events()})
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "vertical-touch-extent.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS special touch at top/middle/bottom in 320/1200: actual game-special target, active beams, charges 2 -> 1, held/released without repeat")


def layout_and_indicator(browser, url):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    release_evidence = ROOT / ".agent/tmp/special-key-release"
    release_evidence.mkdir(parents=True, exist_ok=True)
    for width in (320, 1200):
        with scene(browser, url, width) as page:
            special = page.get_by_role("button", name="Especial", exact=True)
            assert special.is_disabled()
            presentation = special_presentation(special)
            box = presentation["box"]
            collect(page, 5)
            assert special.is_enabled()
            assert special_presentation(special) == presentation
            page.locator("#game-keyboard").focus()
            for label in ("↑", "←", "→", "↓", "Especial", "Pausar"):
                page.keyboard.press("Tab")
                assert page.get_by_role("button", name=label, exact=True).evaluate("node => node === document.activeElement"), label
            canvas = page.locator("canvas").bounding_box()
            assert (box["width"], box["height"]) == (56, 220)
            assert presentation["writing_mode"] == "vertical-rl"
            assert presentation["text"] == "Especial" and presentation["id"] == "game-special"
            text = presentation["text_box"]
            assert text["height"] > text["width"] > 0
            for axis, size in (("x", "width"), ("y", "height")):
                assert box[axis] <= text[axis] and text[axis] + text[size] <= box[axis] + box[size]
                assert abs(text[axis] + text[size] / 2 - box[axis] - box[size] / 2) <= 1
            (EVIDENCE / f"vertical-presentation-{width}.json").write_text(json.dumps(presentation, indent=2) + "\n")
            assert abs(box["x"] - canvas["x"] - canvas["width"] - 16) <= 1
            assert abs(box["y"] - canvas["y"]) <= 1
            assert abs(box["y"] + box["height"] - canvas["y"] - canvas["height"]) <= 1
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            sprite_matches(canvas_image(page), "especialActivated1.png", 50, 21)
            page.screenshot(path=str(EVIDENCE / f"layout-{width}.png"), full_page=True)
            special.click()
            advance(page)
            assert status(page)["charges"] == 1 and special.is_disabled()
            assert special_presentation(special) == presentation
            sprite_matches(canvas_image(page), "especialActivated1.png", 50, 21)
            page.get_by_role("button", name="Pausar", exact=True).click()
            assert special_presentation(special) == presentation
            frozen = canvas_image(page).tobytes()
            advance(page, 20)
            assert canvas_image(page).tobytes() == frozen
            sprite_matches(canvas_image(page), "especialActivated1.png", 50, 21)
        with scene(browser, url, width) as page:
            collect(page, 5)
            special = page.get_by_role("button", name="Especial", exact=True)
            special.focus()
            presentation = special_presentation(special)
            box = presentation["box"]
            page.keyboard.down("1")
            advance(page)
            assert special.is_enabled()
            assert special_presentation(special) == presentation
            assert special.evaluate("button => getComputedStyle(button).opacity") == "0.5"
            page.screenshot(path=str(release_evidence / f"held-{width}.png"), full_page=True)
            page.keyboard.up("1")
            assert special.is_disabled()
            assert special_presentation(special) == presentation
            page.screenshot(path=str(release_evidence / f"released-{width}.png"), full_page=True)
            advance(page, 170)
            assert special.is_enabled()
            assert special_presentation(special) == presentation
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
    print("PASS 320/1200: special centered beside canvas, 56x220 vertical text, 16px gap; position retained through availability, firing, held key, release and pause")


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
                special_touch_extent(browser, url)
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
