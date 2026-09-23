"""Browser exercise for the KofJS slice; requires Playwright, Pillow and Chrome."""

import io
import sys
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright


def ship_crop(page):
    picture = Image.open(io.BytesIO(page.locator("canvas").screenshot())).convert("RGB")
    return picture.crop((0, 100, 126, 106))


url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8766/"
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        executable_path="/usr/bin/google-chrome",
        headless=False,
        args=["--no-sandbox", "--headless=new"],
    )
    page = browser.new_page(viewport={"width": 800, "height": 600})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(url)
    page.locator("input").click()
    page.keyboard.press("Enter")
    page.wait_for_timeout(90)
    assert "Setas" in page.locator(".kof-label").inner_text()
    initial = ship_crop(page)
    page.keyboard.down("ArrowRight")
    page.wait_for_timeout(180)
    moving = ship_crop(page)
    page.keyboard.up("ArrowRight")
    page.wait_for_timeout(120)
    released = ship_crop(page)
    assert ImageChops.difference(initial, moving).getbbox() is not None
    assert ImageChops.difference(moving, released).getbbox() is None

    clock = page.context.new_cdp_session(page)
    for _ in range(4):
        if "Resultado" in page.locator(".kof-label").inner_text():
            break
        clock.send("Emulation.setVirtualTimePolicy", {"policy": "advance", "budget": 120000})
        for _ in range(100):
            page.wait_for_timeout(50)
            if "Resultado" in page.locator(".kof-label").inner_text():
                break
    assert "Resultado" in page.locator(".kof-label").inner_text()
    page.wait_for_timeout(100)
    assert "Resultado" in page.locator(".kof-label").inner_text()
    page.keyboard.press("Enter")
    assert "Menu" in page.locator(".kof-label").inner_text()
    assert not errors, errors
    print("PASS menu, arrows/release, three lives, persistent result, Enter/menu")
    browser.close()
