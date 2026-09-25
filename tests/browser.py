"""Exercise the generated KofJS game in Chrome with observable waits."""

import io
import sys
import time
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

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


url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8766/"
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        executable_path="/usr/bin/google-chrome", headless=False,
        args=["--no-sandbox", "--headless=new"]
    )
    page = browser.new_page(viewport={"width": 800, "height": 600})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(url)
    page.locator("input").click()
    page.keyboard.press("Enter")
    wait_for(lambda: "Setas" in page.locator(".kof-label").inner_text(), page)
    stable = 0
    deadline = time.monotonic() + 5
    while stable < 5 and time.monotonic() < deadline:
        stable = stable + 1 if ship_x(page) is not None else 0
        page.wait_for_timeout(40)
    assert stable == 5, "ship did not settle after its initial blink"
    wait_for(lambda: ship_x(page) is not None, page)
    initial = ship_x(page)
    page.keyboard.down("ArrowRight")
    moving = wait_for(lambda: (x if x is not None and x > initial else None)
                      if (x := ship_x(page)) is not None else None, page)
    wait_for(lambda: ship_observation(page)[1] is True, page)
    page.keyboard.up("ArrowRight")
    wait_for(lambda: ship_observation(page)[1] is False, page)
    wait_for(lambda: ship_x(page) is not None, page)
    released = ship_x(page)
    page.wait_for_timeout(150)
    assert ship_x(page) == released and released >= moving
    assert ship_observation(page)[1] is False, "release did not restore Middle.png"

    page.keyboard.down("ArrowRight")
    page.keyboard.down("ArrowLeft")
    wait_for(lambda: (view[0] is not None and view[0] < released and view[1] is False)
             if (view := ship_observation(page)) else False, page)
    page.keyboard.up("ArrowLeft")
    wait_for(lambda: (view[0] is not None and view[1] is True)
             if (view := ship_observation(page)) else False, page)
    page.keyboard.up("ArrowRight")
    wait_for(lambda: ship_observation(page)[1] is False, page)

    clock = page.context.new_cdp_session(page)
    result_deadline = time.monotonic() + 30
    while "Resultado" not in page.locator(".kof-label").inner_text():
        assert time.monotonic() < result_deadline, "three-life result did not appear"
        clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 120000})
        page.wait_for_timeout(300)
    page.wait_for_timeout(100)
    assert "Resultado" in page.locator(".kof-label").inner_text()
    page.keyboard.press("Enter")
    clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 1000})
    wait_for(lambda: "Menu" in page.locator(".kof-label").inner_text(), page)
    assert not errors, errors
    print("PASS menu, arrow sprites/opposites/release, three lives, persistent result, Enter/menu")
    browser.close()
