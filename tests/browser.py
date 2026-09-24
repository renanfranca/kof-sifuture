"""Exercise the generated KofJS game in Chrome with observable waits."""

import io
import sys
import time
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

SHIP = Image.open(Path(__file__).resolve().parents[1] / "assets/Middle.png").convert("RGBA")
SAMPLES = [(x, y, SHIP.getpixel((x, y))[:3]) for y in range(20) for x in range(50)
           if SHIP.getpixel((x, y))[3] == 255][::7]


def ship_x(page):
    canvas = Image.open(io.BytesIO(page.locator("canvas").screenshot())).convert("RGB")
    candidates = []
    for left in range(127):
        matches = sum(canvas.getpixel((left + x, 100 + y)) == rgb for x, y, rgb in SAMPLES)
        candidates.append(matches)
    best = max(candidates)
    return candidates.index(best) if best >= len(SAMPLES) * 0.9 else None


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
    initial = ship_x(page)
    page.keyboard.down("ArrowRight")
    moving = wait_for(lambda: (x if x is not None and x > initial else None)
                      if (x := ship_x(page)) is not None else None, page)
    page.keyboard.up("ArrowRight")
    page.wait_for_timeout(120)
    wait_for(lambda: ship_x(page) is not None, page)
    released = ship_x(page)
    page.wait_for_timeout(150)
    assert ship_x(page) == released and released >= moving

    clock = page.context.new_cdp_session(page)
    for _ in range(4):
        if "Resultado" in page.locator(".kof-label").inner_text():
            break
        clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 120000})
        page.wait_for_timeout(300)
    assert "Resultado" in page.locator(".kof-label").inner_text()
    page.wait_for_timeout(100)
    assert "Resultado" in page.locator(".kof-label").inner_text()
    page.keyboard.press("Enter")
    clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 1000})
    wait_for(lambda: "Menu" in page.locator(".kof-label").inner_text(), page)
    assert not errors, errors
    print("PASS menu, arrows/release, three lives, persistent result, Enter/menu")
    browser.close()
