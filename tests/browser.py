"""Exercise the generated KofJS game in Chrome with observable waits."""

import argparse
import math
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
            window.selectorDraws = [];
            window.creditTexts = [];
            const originalDraw = CanvasRenderingContext2D.prototype.drawImage;
            const originalText = CanvasRenderingContext2D.prototype.fillText;
            CanvasRenderingContext2D.prototype.drawImage = function(image, x, y, ...rest) {
                if (image.src && /copyright[01]\.png$/.test(image.src)) {
                    window.creditDraws.push([image.src.split('/').pop(), x, y]);
                }
                if (image.src && /[23]lives\.png$/.test(image.src)) {window.selectorDraws.push([image.src.split('/').pop(), x, y]);}
                return originalDraw.call(this, image, x, y, ...rest);
            };
            CanvasRenderingContext2D.prototype.fillText = function(text, x, y, ...rest) {
                const m = this.getTransform();
                window.creditTexts.push({text, x, y, color: this.fillStyle,
                    matrix: [m.a, m.b, m.c, m.d, m.e, m.f], width: this.measureText(text).width});
                return originalText.call(this, text, x, y, ...rest);
            };
        """)
        page.goto(url)
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.press("ArrowLeft")

        def credits(x, y0, y1):
            assert page.evaluate("creditDraws.slice(-1)") == [["copyright0.png", x, y0]]
            texts = page.evaluate("creditTexts.slice(-3)")
            assert [t["text"] for t in texts] == ["contact:", "renan.andradefranca@gmail.com", "Inc. All rights reserved."]
            assert [t["y"] for t in texts] == [10, 22, 34]
            scale = min(0.75, 130 / texts[1]["width"])
            for t in texts:
                assert t["x"] == 0 and t["color"] == "#0080ff", t
                assert all(math.isclose(observed, expected, abs_tol=1e-7) for observed, expected in zip(t["matrix"], [scale, 0, 0, scale, x, y1])), t
                assert t["width"] * scale <= 130 + 1e-5
            assert page.evaluate("creditDraws.every(d => d[0] !== 'copyright1.png')")
            assert page.locator("canvas").evaluate("n => {const c=n.getContext('2d'),m=c.getTransform();return [m.a,m.b,m.c,m.d,m.e,m.f,c.fillStyle]}") == [1, 0, 0, 1, 0, 0, "#ffffff"]

        credits(-134, 110, 141)
        page.clock.run_for(30)
        credits(-129, 110, 141)
        for _ in range(5):
            page.keyboard.press("ArrowLeft")
        credits(-129, 110, 141)
        page.clock.run_for(35 * 30)
        credits(46, 110, 141)
        page.screenshot(path=str(evidence / f"credits-arrived-{width}.png"), full_page=True)
        page.locator("canvas").evaluate("n => n.getContext('2d').font = '20px sans-serif'")
        page.keyboard.press("ArrowLeft")
        credits(46, 110, 141)
        assert page.evaluate("creditTexts.slice(-1)[0].matrix[0]") < 0.75
        page.locator("canvas").evaluate("n => n.getContext('2d').font = '10px sans-serif'")
        page.keyboard.press("ArrowLeft")
        credits(46, 110, 141)
        page.clock.run_for(49 * 30)
        credits(46, 110, 141)
        page.clock.run_for(30)
        credits(46, 111, 140)
        page.clock.run_for(30)
        credits(46, 112, 139)
        page.clock.run_for(171 * 30)
        credits(46, 283, -32)
        page.evaluate("creditDraws.length=0;creditTexts.length=0")
        page.clock.run_for(30)
        assert page.get_by_role("button", name="Pular créditos", exact=True).count() == 1
        assert page.evaluate("creditDraws.length + creditTexts.length") == 0
        page.screenshot(path=str(evidence / f"credits-terminal-{width}.png"), full_page=True)
        page.clock.run_for(30)
        assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1
        assert page.evaluate("selectorDraws.slice(-1)") == [["3lives.png", -30, 120]]
        page.clock.run_for(30)
        sprite(page, "3lives.png", -20, 120)
        page.clock.run_for(10 * 30)
        sprite(page, "3lives.png", 80, 120)
        overlay.focus()
        page.keyboard.press("ArrowDown")
        sprite(page, "3lives.png", 80, 139)
        page.keyboard.press("ArrowUp")
        sprite(page, "3lives.png", 80, 120)
        page.screenshot(path=str(evidence / f"menu-jets-{width}.png"), full_page=True)
        page.clock.run_for(30)
        sprite(page, "2lives.png", 87, 120)
        page.clock.run_for(30)
        sprite(page, "2lives.png", 84, 120)
        page.clock.run_for(22 * 30)
        sprite(page, "2lives.png", 18, 120, occluded=((46, 118, 50, 141),))
        page.clock.run_for(30)
        sprite(page, "2lives.png", 18, 120, occluded=((46, 118, 50, 141),))
        page.screenshot(path=str(evidence / f"menu-{width}.png"), full_page=True)
        page.close()
        print(f"PASS credits frames0/1/36/85/86/87/258/259/260, literal contact/transform isolation and entrance0/1/11/12/13/35/36 at {width}px")


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



def confirmation_journeys(browser, url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/navigation-browser"
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        page.get_by_role("button", name="Pular créditos", exact=True).click()
        for mode in ("Enter", "Space", "click", "touch"):
            controls = page.get_by_role("button", name="Controles", exact=True)
            controls.focus()
            confirm = page.get_by_role("button", name="Confirmar (Enter)", exact=True)
            confirm.focus()
            assert controls.evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
            if mode == "touch":
                controls.tap()
            elif mode == "click":
                confirm.click()
            else:
                page.keyboard.press(mode)
            assert page.get_by_role("button", name="Voltar", exact=True).is_visible()
            page.get_by_role("button", name="Voltar", exact=True).click()
            sprite(page, "2lives.png", 18, 139, occluded=((46, 137, 50, 160),))

        for mode in ("Enter", "Space", "click", "touch"):
            page.get_by_role("button", name="Novo Jogo", exact=True).focus()
            confirm = page.get_by_role("button", name="Confirmar (Enter)", exact=True)
            confirm.focus()
            if mode == "touch":
                page.get_by_role("button", name="Novo Jogo", exact=True).tap()
            elif mode == "click":
                confirm.click()
            else:
                page.keyboard.press(mode)
            assert page.get_by_role("button", name="Pausar", exact=True).is_visible()
            for option in ("Continuar", "Reiniciar", "Menu principal"):
                page.get_by_role("button", name="Pausar", exact=True).click()
                target = page.get_by_role("button", name=option, exact=True)
                old_box = target.bounding_box()
                canvas = page.locator("canvas").bounding_box()
                assert old_box["y"] - canvas["y"] == {"Continuar": 80, "Reiniciar": 99, "Menu principal": 118}[option], (option, old_box, canvas)
                target.focus()
                page.get_by_role("button", name="Confirmar (Enter)", exact=True).focus()
                if mode == "touch":
                    target.tap()
                elif mode == "click":
                    page.get_by_role("button", name="Confirmar (Enter)", exact=True).click()
                else:
                    page.keyboard.press(mode)
                assert page.get_by_role("button", name="Pausar" if option != "Menu principal" else "Novo Jogo", exact=True).is_visible()
            page.get_by_role("button", name="Novo Jogo", exact=True).click()
            page.get_by_role("button", name="Pausar", exact=True).click()
            page.get_by_role("button", name="Menu principal", exact=True).click()

        page.screenshot(path=str(evidence / f"confirmation-menu-{width}.png"), full_page=True)
        page.get_by_role("button", name="Novo Jogo", exact=True).click()
        page.get_by_role("button", name="Pausar", exact=True).click()
        page.screenshot(path=str(evidence / f"confirmation-pause-{width}.png"), full_page=True)
        context.close()
        print(f"PASS every menu/pause option via Enter, Confirmar/Space/click and direct touch; retained controls isolated after three held-Enter transitions at {width}px")


def retained_options(browser, url):
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        page.get_by_role("button", name="Pular créditos", exact=True).click()
        for option, held_key in (("Controles", "Enter"), ("Reiniciar", "Enter"), ("Menu principal", "Enter"),
                                 ("Controles", "Space"), ("Reiniciar", "Space"), ("Menu principal", "Space")):
            if option != "Controles":
                page.get_by_role("button", name="Novo Jogo", exact=True).click()
                page.get_by_role("button", name="Pausar", exact=True).click()
            target = page.get_by_role("button", name=option, exact=True)
            target.focus()
            old_box = target.bounding_box()
            page.keyboard.down(held_key)
            expected = "Voltar" if option == "Controles" else "Pausar" if option == "Reiniciar" else "Novo Jogo"
            assert page.get_by_role("button", name=expected, exact=True).is_visible()
            assert target.evaluate("n => getComputedStyle(n).pointerEvents") == "none"
            assert target.bounding_box()["x"] < -1000
            if option == "Menu principal":
                page.keyboard.press("ArrowDown")
                assert page.get_by_role("button", name="Novo Jogo", exact=True).evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
            if held_key == "Enter":
                page.keyboard.press("Space")
            else:
                page.keyboard.down("Space")
            page.touchscreen.tap(old_box["x"] + old_box["width"] / 2, old_box["y"] + 1)
            page.keyboard.down(held_key)
            assert page.get_by_role("button", name=expected, exact=True).is_visible()
            page.keyboard.up(held_key)
            assert not target.is_visible()
            if option == "Controles":
                page.get_by_role("button", name="Voltar", exact=True).focus()
                page.keyboard.press("Space")
                assert page.get_by_role("button", name="Controles", exact=True).is_visible()
                page.get_by_role("button", name="Novo Jogo", exact=True).click()
                page.get_by_role("button", name="Pausar", exact=True).click()
                page.get_by_role("button", name="Menu principal", exact=True).click()
            elif option == "Reiniciar":
                page.get_by_role("button", name="Pausar", exact=True).focus()
                page.keyboard.press("Enter")
                assert page.get_by_role("button", name="Continuar", exact=True).is_visible()
                page.get_by_role("button", name="Menu principal", exact=True).click()
            else:
                page.get_by_role("button", name="Confirmar (Enter)", exact=True).focus()
                page.keyboard.press("Enter")
                assert page.get_by_role("button", name="Pausar", exact=True).is_visible()
                page.get_by_role("button", name="Pausar", exact=True).click()
                page.get_by_role("button", name="Menu principal", exact=True).click()
        context.close()
        print(f"PASS retained options reject Space/Enter/touch after Controls/Restart/Main Menu; releases rearm at {width}px")

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
                retained_options(browser, url)
                confirmation_journeys(browser, url)
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
                overlay.click(position={"x": 10, "y": 10})
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
                overlay.click(position={"x": 10, "y": 10})
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
