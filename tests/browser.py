"""Exercise the generated KofJS game in Chrome with observable waits."""

import argparse
import io
import sys
from contextlib import nullcontext
import time
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from kof_project import served_build

SHIP = Image.open(Path(__file__).resolve().parents[1] / "assets/Middle.png").convert("RGBA")
SHIP_RIGHT = Image.open(Path(__file__).resolve().parents[1] / "assets/Middle2.png").convert("RGBA")
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


def wait_for(predicate, page, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        page.wait_for_timeout(40)
    raise AssertionError("observable condition did not appear")


def wait_for_ship_x(page):
    """Capture one visible observation, including the valid position x=0."""
    def visible_observation():
        observation = ship_observation(page)
        return observation if observation[0] is not None else None

    return wait_for(visible_observation, page)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", help="already served application URL")
    parser.add_argument("--kof", help="Kof executable")
    args = parser.parse_args()
    server = nullcontext(args.url) if args.url else served_build(kof=args.kof)
    with server as url:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path="/usr/bin/google-chrome", headless=False,
                args=["--no-sandbox", "--headless=new"]
            )
            try:
                page = browser.new_page(viewport={"width": 800, "height": 600})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(url)
                overlay = page.get_by_role("button", name="Ativar teclado do jogo")
                assert page.locator("input").count() == 0
                assert page.locator("canvas").count() == 1
                assert overlay.bounding_box()["width"] == 176
                assert overlay.bounding_box()["height"] == 220
                for label in ("↖", "↑", "↗", "←", "→", "↙", "↓", "↘"):
                    zone = page.get_by_role("button", name=label, exact=True)
                    assert zone.bounding_box()["width"] == 48
                    assert zone.bounding_box()["height"] == 48
                    assert zone.is_disabled()
                page.keyboard.press("Tab")
                assert overlay.evaluate("node => document.activeElement === node")
                assert overlay.evaluate("node => getComputedStyle(node).outlineStyle") == "solid"
                page.keyboard.down("Enter")
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.keyboard.up("Enter")
                page.keyboard.press("Enter")
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.keyboard.press("Enter")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.get_by_role("button", name="Pausar").click()
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.get_by_role("button", name="Continuar").click()
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                stable = 0
                deadline = time.monotonic() + 5
                while stable < 5 and time.monotonic() < deadline:
                    stable = stable + 1 if ship_x(page) is not None else 0
                    page.wait_for_timeout(40)
                assert stable == 5, "ship did not settle after its initial blink"
                overlay.click()
                initial = wait_for_ship_x(page)
                page.keyboard.down("ArrowRight")
                moving = wait_for(lambda: x if (x := ship_x(page)) is not None and x > initial else None, page)
                page.keyboard.up("ArrowRight")
                wait_for(lambda: ship_observation(page)[1] is False, page)
                released = wait_for_ship_x(page)
                page.wait_for_timeout(150)
                assert wait_for_ship_x(page) == released and released >= moving
                page.keyboard.down("ArrowRight")
                page.keyboard.down("ArrowLeft")
                wait_for(lambda: (x := ship_x(page)) is not None and x < released, page)
                page.keyboard.up("ArrowLeft")
                wait_for(lambda: ship_observation(page)[1] is True, page)
                page.keyboard.up("ArrowRight")
                overlay.click()
                before_blur = wait_for_ship_x(page)
                page.keyboard.down("ArrowRight")
                wait_for(lambda: (x := ship_x(page)) is not None and x > before_blur, page)
                page.mouse.click(500, 500)
                page.wait_for_timeout(90)
                blurred = wait_for_ship_x(page)
                page.wait_for_timeout(120)
                assert wait_for_ship_x(page) == blurred
                assert page.get_by_role("button", name="Pausar").count() == 1
                page.keyboard.up("ArrowRight")
                east = page.get_by_role("button", name="→", exact=True)
                box = east.bounding_box()
                page.mouse.move(box["x"] + 24, box["y"] + 24)
                page.mouse.down()
                pad_start = wait_for_ship_x(page)
                wait_for(lambda: (x := ship_x(page)) is not None and x > pad_start, page)
                page.mouse.move(box["x"] + 150, box["y"] + 24)
                page.wait_for_timeout(90)
                left_zone = wait_for_ship_x(page)
                page.wait_for_timeout(120)
                assert wait_for_ship_x(page) == left_zone, "leaving pad should stop movement"
                page.mouse.move(box["x"] + 24, box["y"] + 24)
                page.wait_for_timeout(120)
                assert wait_for_ship_x(page) == left_zone, "reentering without a new press should stay stopped"
                page.mouse.up()
                wait_for(lambda: ship_x(page) is not None, page)
                east.dispatch_event("pointerdown")
                cancelled_start = wait_for_ship_x(page)
                wait_for(lambda: (x := ship_x(page)) is not None and x > cancelled_start, page)
                east.dispatch_event("pointercancel")
                page.wait_for_timeout(90)
                cancelled = wait_for_ship_x(page)
                page.wait_for_timeout(120)
                assert wait_for_ship_x(page) == cancelled
                overlay.click()
                page.keyboard.down("ArrowLeft")
                wait_for(lambda: ship_x(page) is not None, page)
                east.dispatch_event("pointerdown")
                pad_priority_start = wait_for_ship_x(page)
                wait_for(lambda: (x := ship_x(page)) is not None and x > pad_priority_start, page)
                page.keyboard.down("ArrowUp")
                priority_x = wait_for_ship_x(page)
                wait_for(lambda: (x := ship_x(page)) is not None and x > priority_x, page)
                east.dispatch_event("pointerup")
                page.wait_for_timeout(90)
                stopped = wait_for_ship_x(page)
                page.keyboard.down("ArrowLeft")
                page.keyboard.down("ArrowUp")
                page.wait_for_timeout(120)
                assert wait_for_ship_x(page) == stopped, "held keys should not resume after pad release"
                page.keyboard.up("ArrowLeft")
                page.keyboard.up("ArrowUp")
                page.get_by_role("button", name="Pausar").click()
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                paused = page.locator("canvas").screenshot()
                page.wait_for_timeout(160)
                assert page.locator("canvas").screenshot() == paused
                page.get_by_role("button", name="Continuar").click()
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                clock = page.context.new_cdp_session(page)
                result_deadline = time.monotonic() + 30
                while page.get_by_role("button", name="Voltar ao menu").count() == 0:
                    assert time.monotonic() < result_deadline, "three-life result did not appear"
                    clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 120000})
                    page.wait_for_timeout(300)
                result = page.locator("canvas").screenshot()
                page.wait_for_timeout(100)
                assert page.locator("canvas").screenshot() == result
                page.get_by_role("button", name="Voltar ao menu").click()
                clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 1000})
                wait_for(lambda: page.get_by_role("button", name="Novo Jogo").count() == 1, page)
                page.get_by_role("button", name="Novo Jogo").click()
                second_deadline = time.monotonic() + 30
                while page.get_by_role("button", name="Voltar ao menu").count() == 0:
                    assert time.monotonic() < second_deadline, "second game did not reach result"
                    clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 120000})
                    page.wait_for_timeout(300)
                overlay.click()
                page.keyboard.press("Enter")
                clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 1000})
                wait_for(lambda: page.get_by_role("button", name="Novo Jogo").count() == 1, page)
                assert not errors, errors
                touch_context = browser.new_context(viewport={"width": 800, "height": 600}, has_touch=True, is_mobile=True)
                touch_page = touch_context.new_page()
                touch_page.goto(url)
                touch_page.get_by_role("button", name="Novo Jogo").click()
                touch_page.wait_for_timeout(1450)
                wait_for(lambda: ship_x(touch_page) is not None, touch_page)
                east_box = touch_page.get_by_role("button", name="→", exact=True).bounding_box()
                north_box = touch_page.get_by_role("button", name="↑", exact=True).bounding_box()
                session = touch_context.new_cdp_session(touch_page)
                x1, y1 = east_box["x"] + 24, east_box["y"] + 24
                x2, y2 = north_box["x"] + 24, north_box["y"] + 24
                initial_touch = wait_for_ship_x(touch_page)
                session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x1, "y": y1, "id": 1}]})
                wait_for(lambda: (x := ship_x(touch_page)) is not None and x > initial_touch, touch_page)
                session.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x2, "y": y2, "id": 1}]})
                after_drag = wait_for_ship_x(touch_page)
                wait_for(lambda: (x := ship_x(touch_page)) is not None and x > after_drag, touch_page)
                session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
                touch_page.wait_for_timeout(80)
                after_release = wait_for_ship_x(touch_page)
                touch_page.wait_for_timeout(120)
                assert wait_for_ship_x(touch_page) == after_release
                session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x1, "y": y1, "id": 2}]})
                cancel_start = wait_for_ship_x(touch_page)
                wait_for(lambda: (x := ship_x(touch_page)) is not None and x > cancel_start, touch_page)
                session.send("Input.dispatchTouchEvent", {"type": "touchCancel", "touchPoints": []})
                touch_page.wait_for_timeout(90)
                cancelled_touch = wait_for_ship_x(touch_page)
                touch_page.wait_for_timeout(120)
                assert wait_for_ship_x(touch_page) == cancelled_touch
                touch_context.close()
                print("PASS buttons, Enter on four screens, focus/blur, pointer leave/cancel, touch drag/release/cancel, pause, result and menu in Chrome")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
