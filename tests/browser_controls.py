import argparse
from contextlib import contextmanager
from datetime import datetime
import io
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from kof_project import served_build

SHIP = Image.open(ROOT / "assets/Middle.png").convert("RGBA")
SHIP_RIGHT = Image.open(ROOT / "assets/Middle2.png").convert("RGBA")
SAMPLES = [(x, y, SHIP.getpixel((x, y))[:3]) for y in range(20) for x in range(50)
           if SHIP.getpixel((x, y))[3] == 255][::7]
JET_SAMPLES = [(x, y, SHIP_RIGHT.getpixel((x, y))[:3]) for y in range(20) for x in range(50)
               if SHIP.getpixel((x, y))[3] == 0 and SHIP_RIGHT.getpixel((x, y))[3] == 255][::3]


def ship_observation(page):
    canvas = Image.open(io.BytesIO(page.locator("canvas").screenshot())).convert("RGB")
    candidates = []
    for left in range(127):
        matches = sum(canvas.getpixel((left + x, 100 + y)) == rgb for x, y, rgb in SAMPLES)
        candidates.append(matches)
    best = max(candidates)
    if best < len(SAMPLES) * 0.9:
        return None, None
    x = candidates.index(best)
    jets = sum(canvas.getpixel((x + px, 100 + py)) == rgb for px, py, rgb in JET_SAMPLES)
    return x, jets >= len(JET_SAMPLES) * 0.9


def ship_x(page):
    return ship_observation(page)[0]


@contextmanager
def control_page(browser, url, *, touch=False):
    context = browser.new_context(viewport={"width": 800, "height": 600}, has_touch=touch, is_mobile=touch)
    try:
        page = context.new_page()
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        page.clock.run_for(30)
        assert ship_observation(page) == (40, False)
        cycles = 1

        def run(steps):
            nonlocal cycles
            cycles += steps
            assert cycles <= 40
            page.clock.run_for(steps * 30)

        yield page, run
    finally:
        context.close()


def keyboard_origin_and_release(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        page.get_by_role("button", name="Pausar").focus()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (40, False)

        overlay.focus()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (40, False)

        page.get_by_role("button", name="Pausar").focus()
        page.keyboard.up("ArrowRight")
        overlay.focus()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, True)

        page.keyboard.up("ArrowRight")
        run(3)
        assert ship_observation(page) == (60, False)


def opposing_arrows(browser, url):
    with control_page(browser, url) as (page, run):
        page.get_by_role("button", name="Ativar teclado do jogo").click()
        page.keyboard.down("ArrowRight")
        run(3)
        assert ship_observation(page) == (55, True)

        page.keyboard.down("ArrowLeft")
        run(2)
        assert ship_observation(page) == (45, False)

        page.keyboard.up("ArrowLeft")
        run(2)
        assert ship_observation(page) == (55, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (55, False)


def tab_keeps_lost_release_blocked(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.click()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, True)

        page.mouse.click(500, 500)
        run(4)
        assert ship_observation(page) == (60, False)

        page.keyboard.up("ArrowRight")
        page.keyboard.press("Tab")
        assert overlay.evaluate("node => document.activeElement === node")
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, False)

        page.keyboard.up("ArrowRight")
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (80, False)


def click_rearms_held_arrow(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.click()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, True)

        page.mouse.click(500, 500)
        run(4)
        assert ship_observation(page) == (60, False)

        overlay.click()
        run(4)
        assert ship_observation(page) == (60, False)

        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (80, False)


def click_rearms_after_external_release(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.click()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, True)

        page.mouse.click(500, 500)
        page.keyboard.up("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, False)

        overlay.click()
        run(4)
        assert ship_observation(page) == (60, False)

        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (80, False)


def mouse_pad_exit_and_cancel(browser, url):
    with control_page(browser, url) as (page, run):
        east = page.get_by_role("button", name="→", exact=True)
        box = east.bounding_box()
        page.mouse.move(box["x"] + 24, box["y"] + 24)
        page.mouse.down()
        run(3)
        assert ship_observation(page) == (55, True)

        page.mouse.move(box["x"] + 150, box["y"] + 24)
        run(3)
        assert ship_observation(page) == (55, False)

        page.mouse.move(box["x"] + 24, box["y"] + 24)
        run(3)
        assert ship_observation(page) == (55, False)
        page.mouse.up()

        east.dispatch_event("pointerdown")
        run(3)
        assert ship_observation(page) == (70, True)

        east.dispatch_event("pointercancel")
        run(3)
        assert ship_observation(page) == (70, False)


def pad_owns_movement(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        east = page.get_by_role("button", name="→", exact=True)
        box = east.bounding_box()
        overlay.click()
        page.keyboard.down("ArrowLeft")
        run(3)
        assert ship_observation(page) == (25, False)

        page.mouse.move(box["x"] + 24, box["y"] + 24)
        page.mouse.down()
        assert east.evaluate("node => document.activeElement === node")
        run(3)
        assert ship_observation(page) == (40, True)

        page.keyboard.down("ArrowUp")
        run(3)
        assert ship_observation(page) == (55, True)

        page.mouse.up()
        run(3)
        assert ship_observation(page) == (55, False)

        page.keyboard.down("ArrowLeft")
        page.keyboard.down("ArrowUp")
        run(3)
        assert ship_observation(page) == (55, False)

        overlay.focus()
        page.keyboard.down("ArrowLeft")
        run(3)
        assert ship_observation(page) == (55, False)
        page.keyboard.up("ArrowLeft")
        page.keyboard.up("ArrowUp")


def touch_pad_drag_release_and_cancel(browser, url):
    with control_page(browser, url, touch=True) as (page, run):
        east = page.get_by_role("button", name="→", exact=True).bounding_box()
        north = page.get_by_role("button", name="↑", exact=True).bounding_box()
        x1, y1 = east["x"] + 24, east["y"] + 24
        x2, y2 = north["x"] + 24, north["y"] + 24
        session = page.context.new_cdp_session(page)

        session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x1, "y": y1, "id": 1}]})
        run(3)
        assert ship_observation(page) == (55, True)

        session.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x2, "y": y2, "id": 1}]})
        run(3)
        assert ship_observation(page) == (70, True)

        session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        run(3)
        assert ship_observation(page) == (70, False)

        session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x1, "y": y1, "id": 2}]})
        run(3)
        assert ship_observation(page) == (85, True)

        session.send("Input.dispatchTouchEvent", {"type": "touchCancel", "touchPoints": []})
        run(3)
        assert ship_observation(page) == (85, False)


def touch_click_rearms_arrow(browser, url):
    with control_page(browser, url, touch=True) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, True)

        page.touchscreen.tap(500, 500)
        page.keyboard.up("ArrowRight")
        run(3)
        assert ship_observation(page) == (60, False)

        overlay.tap()
        run(3)
        assert ship_observation(page) == (60, False)

        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (80, False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kof", help="Kof executable")
    args = parser.parse_args()
    with served_build(kof=args.kof, fixture=ROOT / "tests/controls.kf") as url:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path="/usr/bin/google-chrome", headless=False,
                args=["--no-sandbox", "--headless=new"]
            )
            try:
                keyboard_origin_and_release(browser, url)
                opposing_arrows(browser, url)
                tab_keeps_lost_release_blocked(browser, url)
                click_rearms_held_arrow(browser, url)
                click_rearms_after_external_release(browser, url)
                mouse_pad_exit_and_cancel(browser, url)
                pad_owns_movement(browser, url)
                touch_pad_drag_release_and_cancel(browser, url)
                touch_click_rearms_arrow(browser, url)
            finally:
                browser.close()
    print("PASS isolated keyboard, focus, pointer and touch controls in Chrome")


if __name__ == "__main__":
    main()
