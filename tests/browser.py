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
from browser_stage import sprite

def wait_for(predicate, page, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        page.wait_for_timeout(40)
    raise AssertionError("observable condition did not appear")


def credits_animation(browser, url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/navigation-browser"
    evidence.mkdir(parents=True, exist_ok=True)
    for width in (320, 1200):
        page = browser.new_page(viewport={"width": width, "height": 1000})
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.add_init_script("""
            window.creditDraws = [];
            const originalDraw = CanvasRenderingContext2D.prototype.drawImage;
            CanvasRenderingContext2D.prototype.drawImage = function(image, x, y, ...rest) {
                if (image.src && /copyright[01]\.png$/.test(image.src)) {
                    window.creditDraws.push([image.src.split('/').pop(), x, y]);
                }
                return originalDraw.call(this, image, x, y, ...rest);
            };
        """)
        page.goto(url)
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.press("ArrowLeft")
        assert page.get_by_role("button", name="Pular créditos", exact=True).count() == 1
        assert page.evaluate("creditDraws.slice(-2)") == [["copyright0.png", -134, 110], ["copyright1.png", -134, 141]]
        page.clock.run_for(30)
        assert page.evaluate("creditDraws.slice(-2)") == [["copyright0.png", -129, 110], ["copyright1.png", -129, 141]]
        for _ in range(5):
            page.keyboard.press("ArrowLeft")
        assert page.evaluate("creditDraws.slice(-2)") == [["copyright0.png", -129, 110], ["copyright1.png", -129, 141]]
        page.clock.run_for(35 * 30)
        sprite(page, "copyright0.png", 46, 110)
        sprite(page, "copyright1.png", 46, 141)
        page.screenshot(path=str(evidence / f"credits-arrived-{width}.png"), full_page=True)
        page.clock.run_for(50 * 30)
        sprite(page, "copyright0.png", 46, 110)
        sprite(page, "copyright1.png", 46, 141)
        page.clock.run_for(30)
        sprite(page, "copyright0.png", 46, 111)
        sprite(page, "copyright1.png", 46, 140)
        page.clock.run_for(50 * 30)
        sprite(page, "copyright0.png", 46, 161)
        sprite(page, "copyright1.png", 46, 90)
        page.screenshot(path=str(evidence / f"credits-exit-{width}.png"), full_page=True)
        page.clock.run_for(122 * 30)
        assert page.get_by_role("button", name="Pular créditos", exact=True).count() == 1
        page.clock.run_for(30)
        assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1
        page.clock.run_for(300)
        sprite(page, "menu0.png", 48, 120)
        sprite(page, "menu1.png", 48, 139)
        page.screenshot(path=str(evidence / f"menu-{width}.png"), full_page=True)
        page.close()
        print(f"PASS historical credits pixels, 30ms steps, redraw purity, fifty-frame wait and natural completion at {width}px")


def menu_navigation(browser, url):
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.tap()
        assert page.get_by_role("button", name="Controles", exact=True).count() == 1
        assert page.get_by_role("button", name="Carregar", exact=True).count() == 0
        assert page.get_by_role("button", name="Opções", exact=True).count() == 0
        page.get_by_role("button", name="↓", exact=True).tap()
        page.get_by_role("button", name="↓", exact=True).tap()
        assert page.get_by_role("button", name="Controles", exact=True).evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
        page.get_by_role("button", name="↑", exact=True).tap()
        assert page.get_by_role("button", name="Novo Jogo", exact=True).evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
        overlay.focus()
        page.keyboard.down("ArrowDown")
        page.keyboard.down("ArrowDown")
        page.keyboard.press("Enter")
        assert page.get_by_role("button", name="Voltar", exact=True).count() == 1
        explanation = page.locator("#game-help")
        assert explanation.is_visible()
        for term in ("Tab", "foco", "Enter", "1", "diagonais", "opostos", "Arrasto", "Soltar", "Especial", "cancelar"):
            assert term in explanation.inner_text()
        page.screenshot(path=str(Path(__file__).resolve().parents[1] / f".agent/tmp/navigation-browser/controls-{width}.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.keyboard.press("Enter")
        assert page.get_by_role("button", name="Controles", exact=True).count() == 1
        page.keyboard.press("Enter")
        assert page.get_by_role("button", name="Voltar", exact=True).count() == 1
        page.keyboard.press("Enter")
        page.keyboard.up("ArrowDown")
        page.keyboard.press("ArrowUp")
        page.keyboard.press("Enter")
        assert page.get_by_role("button", name="Pausar", exact=True).count() == 1
        page.keyboard.press("Enter")
        assert page.get_by_role("button", name="Reiniciar", exact=True).count() == 1
        assert page.get_by_role("button", name="Menu principal", exact=True).count() == 1
        page.screenshot(path=str(Path(__file__).resolve().parents[1] / f".agent/tmp/navigation-browser/pause-{width}.png"), full_page=True)
        page.keyboard.down("ArrowDown")
        page.keyboard.down("ArrowDown")
        assert page.get_by_role("button", name="Reiniciar", exact=True).evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
        page.keyboard.up("ArrowDown")
        page.keyboard.press("ArrowDown")
        page.keyboard.press("ArrowDown")
        assert page.get_by_role("button", name="Menu principal", exact=True).evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
        page.keyboard.press("ArrowUp")
        page.keyboard.press("ArrowUp")
        page.keyboard.press("ArrowUp")
        assert page.get_by_role("button", name="Continuar", exact=True).evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
        page.get_by_role("button", name="Menu principal", exact=True).tap()
        page.clock.run_for(60)
        assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1
        assert page.get_by_role("button", name="Pular créditos", exact=True).count() == 0
        page.get_by_role("button", name="Controles", exact=True).tap()
        page.get_by_role("button", name="Voltar", exact=True).tap()
        page.get_by_role("button", name="Novo Jogo", exact=True).tap()
        assert page.get_by_role("button", name="Pausar", exact=True).count() == 1
        context.close()
        print(f"PASS credits skip, bounded menu, Controls and pause navigation at {width}px")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", help="already served application URL")
    parser.add_argument("--kof", help="Kof executable")
    args = parser.parse_args()
    server = nullcontext(args.url) if args.url else served_build(kof=args.kof)
    with server as url, served_build(kof=args.kof, fixture=Path(__file__).parent / "weapons.kf") as result_url:
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
                assert startup_page.get_by_role("button", name="Pular créditos").count() == 1
                assert startup_page.get_by_role("button", name="Novo Jogo").count() == 0
                startup_page.get_by_role("button", name="Pular créditos").focus()
                startup_page.keyboard.down("Enter")
                startup_page.keyboard.down("Enter")
                startup_page.clock.run_for(30)
                assert startup_page.get_by_role("button", name="Novo Jogo").count() == 1
                assert startup_page.get_by_role("button", name="Pausar").count() == 0
                startup_page.keyboard.up("Enter")
                for label in ("↑", "←", "→", "↓"):
                    assert startup_page.get_by_role("button", name=label, exact=True).is_disabled() == (label in ("←", "→"))
                startup_context.close()
                page = browser.new_page(viewport={"width": 800, "height": 600})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(url)
                page.get_by_role("button", name="Pular créditos").click()
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
                for label in ("↑", "←", "→", "↓"):
                    zone = page.get_by_role("button", name=label, exact=True)
                    assert zone.bounding_box()["width"] == 56
                    assert zone.bounding_box()["height"] == 56
                    assert zone.is_disabled()
                page.keyboard.press("Tab")
                assert overlay.evaluate("node => document.activeElement === node")
                assert overlay.evaluate("node => getComputedStyle(node).outlineStyle") == "solid"
                page.keyboard.down("Enter")
                page.keyboard.down("Enter")
                wait_for(lambda: page.get_by_role("button", name="Novo Jogo").count() == 1, page)
                page.keyboard.up("Enter")
                page.keyboard.press("Enter")
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
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
                page.goto(result_url)
                for life in range(3):
                    page.get_by_role("button", name="Hit ship", exact=True).click()
                wait_for(lambda: page.get_by_role("button", name="Voltar ao menu").count() == 1, page)
                result = page.locator("canvas").screenshot()
                page.wait_for_timeout(100)
                assert page.locator("canvas").screenshot() != result
                page.get_by_role("button", name="Voltar ao menu").focus()
                page.keyboard.down("Enter")
                page.keyboard.down("Enter")
                page.keyboard.up("Enter")
                wait_for(lambda: page.get_by_role("button", name="Novo Jogo").count() == 1, page)
                page.get_by_role("button", name="Novo Jogo").click()
                for life in range(3):
                    page.get_by_role("button", name="Hit ship", exact=True).click()
                wait_for(lambda: page.get_by_role("button", name="Voltar ao menu").count() == 1, page)
                overlay.click()
                page.keyboard.press("Enter")
                wait_for(lambda: page.get_by_role("button", name="Novo Jogo").count() == 1, page)
                assert not errors, errors
                credits_animation(browser, url)
                menu_navigation(browser, url)
                print("PASS menu, Enter and Space, conservative confirmation, pause, result and menu in Chrome")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
