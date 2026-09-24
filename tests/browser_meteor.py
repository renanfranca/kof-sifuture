"""Check the real Game model's hit-meteor steps in a KofJS browser fixture."""

import io
import shutil
import subprocess
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
KOF = Path("/home/renanfranca/projects/kof/bin/kof")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format, *_args):
        pass


def sprite_matches(page, x, frame):
    actual = Image.open(io.BytesIO(page.locator("canvas").screenshot())).convert("RGB")
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


with tempfile.TemporaryDirectory(prefix="sifuture-meteor-browser-") as directory:
    temporary = Path(directory)
    source = temporary / "source"
    output = temporary / "web"
    source.mkdir()
    shutil.copy2(ROOT / "src/Game.kf", source / "Game.kf")
    shutil.copy2(ROOT / "tests/meteor-motion.kf", source / "meteor-motion.kf")
    subprocess.run([str(KOF), "build", str(source), "--target", "js", "--output", str(output)], check=True)
    (output / "assets").mkdir()
    for frame in range(3):
        name = f"meteor0C{frame}.png"
        shutil.copy2(ROOT / "assets" / name, output / "assets" / name)

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(output)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path="/usr/bin/google-chrome", headless=False,
                args=["--no-sandbox", "--headless=new"]
            )
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_port}/")
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
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

print("PASS moving meteor, three impact frames, and respawn in Chrome")
