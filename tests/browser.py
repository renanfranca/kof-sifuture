"""Exercise the generated KofJS game in Chrome with observable waits."""

import argparse
from datetime import datetime
import sys
from contextlib import nullcontext
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from kof_project import served_build

def wait_for(predicate, page, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        page.wait_for_timeout(40)
    raise AssertionError("observable condition did not appear")


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
                startup_context = browser.new_context(viewport={"width": 800, "height": 600})
                startup_page = startup_context.new_page()
                startup_page.clock.install(time=datetime(2026, 1, 1))
                startup_page.clock.pause_at(datetime(2026, 1, 1))
                startup_page.goto(url)
                assert startup_page.get_by_role("button", name="Novo Jogo").count() == 1
                for label in ("↖", "↑", "↗", "←", "→", "↙", "↓", "↘"):
                    assert startup_page.get_by_role("button", name=label, exact=True).is_disabled()
                startup_context.close()
                page = browser.new_page(viewport={"width": 800, "height": 600})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(url)
                page.get_by_role("button", name="Novo Jogo").focus()
                page.keyboard.down("Enter")
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.keyboard.up("Enter")
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
                action = page.locator("#game-action")
                overlay.focus()
                page.keyboard.down("Space")
                action.focus()
                page.keyboard.up("Space")
                page.wait_for_timeout(90)
                assert page.get_by_role("button", name="Pausar").count() == 1
                action.focus()
                page.keyboard.down("Enter")
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.keyboard.up("Enter")
                page.keyboard.press("Enter")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.keyboard.press("Space")
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.keyboard.press("Space")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.keyboard.press("Space")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.keyboard.down("Enter")
                page.wait_for_timeout(90)
                assert page.get_by_role("button", name="Pausar").count() == 1
                page.keyboard.up("Enter")
                page.get_by_role("button", name="Pausar").dispatch_event("pointerdown")
                page.get_by_role("button", name="Pausar").dispatch_event("pointercancel")
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.get_by_role("button", name="Continuar").click()
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.keyboard.up("Enter")
                overlay.focus()
                page.keyboard.press("Enter")
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.keyboard.press("Enter")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.get_by_role("button", name="Pausar").click()
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.get_by_role("button", name="Continuar").click()
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                overlay.focus()
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                page.mouse.click(500, 500)
                page.keyboard.up("Enter")
                overlay.click()
                page.keyboard.down("Enter")
                page.wait_for_timeout(90)
                assert page.get_by_role("button", name="Continuar").count() == 1
                page.keyboard.up("Enter")
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.keyboard.up("Enter")
                action = page.locator("#game-action")
                action.focus()
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Continuar").count() == 1, page)
                action_box = action.bounding_box()
                page.mouse.move(action_box["x"] + action_box["width"] / 2, action_box["y"] + action_box["height"] / 2)
                page.mouse.down()
                page.keyboard.down("Enter")
                page.wait_for_timeout(90)
                assert page.get_by_role("button", name="Continuar").count() == 1
                page.mouse.up()
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.keyboard.up("Enter")
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
                page.get_by_role("button", name="Voltar ao menu").focus()
                page.keyboard.down("Enter")
                page.keyboard.down("Enter")
                page.keyboard.up("Enter")
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
                print("PASS menu, Enter and Space, conservative confirmation, pause, result and menu in Chrome")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
