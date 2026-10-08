"""Check the real Game model's hit-meteor steps in a KofJS browser fixture."""

import argparse
import io
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from kof_project import served_build


ROOT = Path(__file__).resolve().parents[1]


def sprite_matches(page, x, frame):
    actual = Image.open(io.BytesIO(page.locator("canvas:visible").screenshot())).convert("RGB")
    expected = Image.open(ROOT / "assets" / f"meteor0C{frame}.png").convert("RGBA")
    samples = [(px, py, expected.getpixel((px, py))[:3])
               for py in range(expected.height) for px in range(expected.width)
               if expected.getpixel((px, py))[3] == 255][::5]
    matching = sum(actual.getpixel((x + px, 80 + py)) == rgb for px, py, rgb in samples)
    return matching >= len(samples) * 0.9


def wait_for_sprite(page, x, frame):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        if sprite_matches(page, x, frame):
            return
        page.wait_for_timeout(30)
    raise AssertionError(f"impact frame {frame} not visible at x={x}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kof", help="Kof executable")
    args = parser.parse_args()
    frames = [ROOT / "assets" / f"meteor0C{frame}.png" for frame in range(3)]
    with served_build(kof=args.kof, fixture=ROOT / "tests/meteor-motion.kf",
                      model_only=True, assets=frames) as url:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path="/usr/bin/google-chrome", headless=False,
                args=["--no-sandbox", "--headless=new"]
            )
            try:
                page = browser.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(url)
                assert page.locator(".kof-label").inner_text() == "impact:100:0"
                wait_for_sprite(page, 100, 0)
                for step in range(1, 6):
                    page.get_by_text("Next step", exact=True).click()
                    x = 100 - step
                    frame = step // 2
                    assert page.locator(".kof-label").inner_text() == f"impact:{x}:{step}"
                    wait_for_sprite(page, x, frame)
                page.get_by_text("Next step", exact=True).click()
                assert page.locator(".kof-label").inner_text().startswith("respawn:")
                assert not errors, errors
            finally:
                browser.close()
    print("PASS moving meteor, three impact frames, and respawn in Chrome")


if __name__ == "__main__":
    main()
