"""Exercise the generated KofJS game in Chrome with observable waits."""

import argparse
import base64
import io
from datetime import datetime
import sys
from contextlib import nullcontext
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from kof_project import served_build
from browser_stage import sprite

def keyboard_hint(page, visible):
    hint = page.locator("#game-keyboard-hint")
    assert hint.count() == 1
    assert hint.is_visible() == visible
    overlay = page.locator("#game-keyboard")
    name = "Ativar teclado do jogo" if visible else "Teclado ativo"
    assert page.get_by_role("button", name=name, exact=True).get_attribute("id") == "game-keyboard"
    assert overlay.is_visible() and not overlay.is_disabled()
    canvas = page.locator("canvas:visible")
    rendered = Image.open(io.BytesIO(canvas.screenshot(scale="css"))).convert("RGB").crop((12, 88, 164, 108))
    pixels = base64.b64decode(canvas.evaluate("n => n.toDataURL().split(',')[1]"))
    underlying = Image.open(io.BytesIO(pixels)).convert("RGB").crop((12, 88, 164, 108))
    if visible:
        style = hint.evaluate("n => { const s = getComputedStyle(n); return [s.fontFamily, s.fontSize, s.lineHeight, s.backgroundColor, s.color, s.pointerEvents]; }")
        assert style == ["sans-serif", "14px", "20px", "rgb(18, 18, 18)", "rgb(238, 238, 238)", "none"], style
        box, area = hint.bounding_box(), canvas.bounding_box()
        assert (box["x"] - area["x"], box["y"] - area["y"], box["width"], box["height"]) == (12, 88, 152, 20), box
        assert sum(pixel == (18, 18, 18) for pixel in rendered.getdata()) > 1000
        assert sum(all(channel > 180 for channel in pixel) for pixel in rendered.getdata()) > 50
        assert ImageChops.difference(rendered, underlying).getbbox() is not None
        point = {"x": box["x"] + box["width"] / 2, "y": box["y"] + box["height"] / 2}
        assert page.evaluate("p => document.elementFromPoint(p.x, p.y).id", point) == "game-keyboard"
        return point
    assert ImageChops.difference(rendered, underlying).getbbox() is None


def wait_for(predicate, page, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        page.wait_for_timeout(40)
    raise AssertionError("observable condition did not appear")


CREDIT_LABELS = ["Copyright (c) 2006-2007", "Renan Meneses", "de Andrade Franca", "contact:",
                 "renan.andradefranca@gmail.com", "Inc. All rights reserved."]


def record_menu(page):
    page.add_init_script(r"""
        window.menuShips = [];
        window.canvasTexts = [];
        const draw = CanvasRenderingContext2D.prototype.drawImage;
        const clear = CanvasRenderingContext2D.prototype.clearRect;
        const text = CanvasRenderingContext2D.prototype.fillText;
        CanvasRenderingContext2D.prototype.clearRect = function(x, y, w, h) {
            if (w === this.canvas.width && h === this.canvas.height) window.canvasTexts = [];
            return clear.call(this, x, y, w, h);
        };
        CanvasRenderingContext2D.prototype.drawImage = function(image, x, y, ...rest) {
            const asset = image.src && image.src.split('/').pop();
            if (asset && /[23]lives\.png$/.test(asset)) window.menuShips.push([asset, x, y]);
            return draw.call(this, image, x, y, ...rest);
        };
        CanvasRenderingContext2D.prototype.fillText = function(label, x, y, ...rest) {
            const m = this.getTransform();
            const metrics = this.measureText(label);
            window.canvasTexts.push({label, x: m.a*x+m.c*y+m.e, y: m.b*x+m.d*y+m.f,
                size: parseFloat(this.font)*m.a, font: this.font, color: this.fillStyle,
                width: metrics.width*m.a, ascent: metrics.actualBoundingBoxAscent*m.d,
                descent: metrics.actualBoundingBoxDescent*m.d,
                matrix: [m.a,m.b,m.c,m.d,m.e,m.f]});
            return text.call(this, label, x, y, ...rest);
        };
    """)



def record_keyboard(page):
    page.add_init_script(r"""
        window.keyboardEvents = [];
        window.pointerdowns = 0;
        window.shipDraw = null;
        const draw = CanvasRenderingContext2D.prototype.drawImage;
        const clear = CanvasRenderingContext2D.prototype.clearRect;
        CanvasRenderingContext2D.prototype.clearRect = function(...args) {
            if (args[2] === this.canvas.width && args[3] === this.canvas.height) window.shipDraw = null;
            return clear.apply(this, args);
        };
        CanvasRenderingContext2D.prototype.drawImage = function(image, x, y, ...args) {
            const name = image.src && image.src.split('/').pop();
            if (/^Middle2?\.png$/.test(name)) window.shipDraw = {name, x, y};
            return draw.call(this, image, x, y, ...args);
        };
        document.addEventListener('pointerdown', () => window.pointerdowns++);
        for (const type of ['keydown', 'keyup']) {
            document.addEventListener(type, e => window.keyboardEvents.push([type, e.key, e.target.id]));
        }
    """)


def ship_at(page, x, y=100):
    observed = page.evaluate("shipDraw")
    assert observed is not None and (observed["x"], observed["y"]) == (x, y), observed
    sprite(page, observed["name"], x, y)


def tab_to(page, identity, *, reverse=False):
    for _ in range(24):
        if page.evaluate("document.activeElement.id") == identity:
            return
        page.keyboard.press("Shift+Tab" if reverse else "Tab")
    raise AssertionError((identity, page.evaluate("document.activeElement.outerHTML")))


def text_lines(page, labels, x, baselines, color, *, settled=False):
    texts = page.evaluate("canvasTexts")
    assert [t["label"] for t in texts] == labels, texts
    canvas = page.locator("canvas:visible")
    bounds = canvas.bounding_box()
    for text, baseline in zip(texts, baselines):
        assert abs(text["x"] - x) < 0.001 and abs(text["y"] - baseline) < 0.001, text
        assert abs(text["size"] - 16) < 0.001 and text["font"] == "10px sans-serif", text
        assert text["color"] == color, text
        assert abs(text["matrix"][0] - 1.6) < 0.001 and abs(text["matrix"][3] - 1.6) < 0.001, text
        if settled:
            assert text["x"] >= 12 and text["x"] + text["width"] <= bounds["width"] - 12, text
            assert baseline - text["ascent"] >= 12 and baseline + text["descent"] <= bounds["height"] - 12, text
    assert canvas.evaluate("n => {const c=n.getContext('2d'),m=c.getTransform();return [m.a,m.b,m.c,m.d,m.e,m.f,c.fillStyle]}") == [1,0,0,1,0,0,"#ffffff"]


def menu_lines(page, labels, positions):
    text_lines(page, labels, 48, [y + 14 for y in positions], "#ffffff")
    texts = page.evaluate("canvasTexts")
    canvas = page.locator("canvas:visible").bounding_box()
    assert canvas["width"] == 176 and canvas["height"] == 220
    for label, y, text in zip(labels, positions, texts):
        box = page.get_by_role("button", name=label, exact=True).bounding_box()
        assert box["width"] == 128 and box["height"] == 19
        assert box["x"] - canvas["x"] == 48 and box["y"] - canvas["y"] == y
        assert text["width"] <= 128
        assert text["y"] - text["ascent"] >= y and text["y"] + text["descent"] <= y + 19


def selected_line(page, name, y):
    assert page.evaluate("menuShips.slice(-1)[0][2]") == y
    assert page.get_by_role("button", name=name, exact=True).evaluate("n => getComputedStyle(n).outlineStyle") == "none"


def menu_presentation(browser, url):
    for width in (320, 1200):
        page = browser.new_page(viewport={"width": width, "height": 1000})
        record_menu(page)
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        page.get_by_role("button", name="Pular créditos", exact=True).click()
        menu_lines(page, ["Novo Jogo", "Controles"], [120, 139])
        page.clock.run_for(36 * 30)
        page.get_by_role("button", name="Controles", exact=True).focus()
        selected_line(page, "Controles", 139)
        sprite(page, "2lives.png", 18, 139)
        surface = page.locator("#game-keyboard").locator("..")
        assert surface.evaluate("n => [getComputedStyle(n).outlineWidth, getComputedStyle(n).outlineColor]") == ["1px", "rgb(128, 128, 128)"]
        page.get_by_role("button", name="Confirmar (Enter)", exact=True).focus()
        selected_line(page, "Controles", 139)
        assert surface.evaluate("n => getComputedStyle(n).outlineStyle") == "none"
        assert page.locator("#game-action").evaluate("n => getComputedStyle(n).outlineWidth") == "1px"
        page.get_by_role("button", name="Novo Jogo", exact=True).click()
        page.get_by_role("button", name="Pausar", exact=True).click()
        menu_lines(page, ["Continuar", "Reiniciar", "Menu principal"], [80, 99, 118])
        page.get_by_role("button", name="Menu principal", exact=True).focus()
        selected_line(page, "Menu principal", 118)
        sprite(page, "2lives.png", 18, 118)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.close()
        print(f"PASS Portuguese sans-serif menus at x48/16px, ship selection and independent neutral focus at {width}px")


def credits_animation(browser, url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/credits-text-browser"
    evidence.mkdir(parents=True, exist_ok=True)
    for width in (320, 1200):
        page = browser.new_page(viewport={"width": width, "height": 1000})
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        record_menu(page)
        page.goto(url)
        overlay = page.locator("#game-keyboard")
        overlay.focus()
        page.keyboard.press("ArrowLeft")

        def credits(x, y0, y1):
            text_lines(page, CREDIT_LABELS, x, [y0 + 16, y0 + 40, y0 + 64, y1 + 16, y1 + 40, y1 + 64],
                       "#0080ff", settled=(x == 12 and y0 == 40))

        canvas = page.locator("canvas:visible")
        assert canvas.bounding_box()["width"] == 262 and canvas.bounding_box()["height"] == 260
        assert overlay.bounding_box()["width"] == 262 and overlay.bounding_box()["height"] == 260
        assert overlay.locator("..").evaluate("n => getComputedStyle(n).backgroundColor") == "rgb(18, 18, 18)"
        for name in ("↑", "↓", "←", "→", "Especial"):
            assert not page.get_by_role("button", name=name, exact=True).is_visible()
        credits(-262, 40, 136)
        page.clock.run_for(30)
        credits(-257, 40, 136)
        for _ in range(5):
            page.keyboard.press("ArrowLeft")
        credits(-257, 40, 136)
        page.clock.run_for(53 * 30)
        credits(8, 40, 136)
        page.clock.run_for(30)
        credits(12, 40, 136)
        page.screenshot(path=str(evidence / f"credits-arrived-{width}.png"), full_page=True)
        page.clock.run_for(199 * 30)
        credits(12, 40, 136)
        page.keyboard.press("ArrowLeft")
        credits(12, 40, 136)
        page.clock.run_for(30)
        credits(12, 40, 136)
        page.clock.run_for(30)
        credits(12, 41, 135)
        page.clock.run_for(206 * 30)
        credits(12, 247, -71)
        page.clock.run_for(30)
        credits(12, 248, -72)
        page.clock.run_for(11 * 30)
        credits(12, 259, -83)
        page.clock.run_for(30)
        credits(12, 260, -84)
        page.clock.run_for(30)
        assert page.get_by_role("button", name="Pular créditos", exact=True).is_visible()
        assert page.evaluate("canvasTexts") == []
        assert canvas.evaluate("n => Array.from(n.getContext('2d').getImageData(0,0,n.width,n.height).data).every(v=>v===0)")
        page.screenshot(path=str(evidence / f"credits-terminal-{width}.png"), full_page=True)
        page.clock.run_for(30)
        assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1
        assert page.evaluate("menuShips.slice(-1)") == [["3lives.png", -30, 120]]
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
        print(f"PASS credits frames0/1/54/55/254/255/256/462/463/474/475/476/477, six-second hold, text geometry/color/transform isolation and entrance0/1/11/12/13/35/36 at {width}px")


def menu_navigation(browser, url):
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        record_menu(page)
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        overlay = page.locator("#game-keyboard")
        overlay.tap()
        assert page.get_by_role("button", name="Controles", exact=True).count() == 1
        assert page.get_by_role("button", name="Carregar", exact=True).count() == 0
        assert page.get_by_role("button", name="Opções", exact=True).count() == 0
        page.get_by_role("button", name="↓", exact=True).tap()
        page.get_by_role("button", name="↓", exact=True).tap()
        selected_line(page, "Controles", 139)
        page.get_by_role("button", name="↑", exact=True).tap()
        selected_line(page, "Novo Jogo", 120)
        overlay.focus()
        page.keyboard.down("ArrowDown")
        page.keyboard.down("ArrowDown")
        page.keyboard.press("Enter")
        assert page.get_by_role("button", name="Voltar", exact=True).count() == 1
        explanation = page.locator("#game-help")
        assert explanation.is_visible()
        for term in ("Tab", "Enter", "1", "diagonal", "Solte", "Especial"):
            assert term in explanation.inner_text()
        page.screenshot(path=str(Path(__file__).resolve().parents[1] / f".agent/tmp/credits-text-browser/controls-{width}.png"), full_page=True)
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
        page.screenshot(path=str(Path(__file__).resolve().parents[1] / f".agent/tmp/credits-text-browser/pause-{width}.png"), full_page=True)
        page.keyboard.down("ArrowDown")
        page.keyboard.down("ArrowDown")
        selected_line(page, "Reiniciar", 99)
        page.keyboard.up("ArrowDown")
        page.keyboard.press("ArrowDown")
        page.keyboard.press("ArrowDown")
        selected_line(page, "Menu principal", 118)
        page.keyboard.press("ArrowUp")
        page.keyboard.press("ArrowUp")
        page.keyboard.press("ArrowUp")
        selected_line(page, "Continuar", 80)
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
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/credits-text-browser"
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        record_menu(page)
        record_keyboard(page)
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        page.get_by_role("button", name="Pular créditos", exact=True).click()
        for mode in ("Enter", "Space", "click", "touch"):
            controls = page.get_by_role("button", name="Controles", exact=True)
            controls.focus()
            confirm = page.get_by_role("button", name="Confirmar (Enter)", exact=True)
            confirm.focus()
            selected_line(page, "Controles", 139)
            if mode == "touch":
                controls.tap()
            elif mode == "click":
                confirm.click()
            else:
                page.keyboard.press(mode)
            assert page.get_by_role("button", name="Voltar", exact=True).is_visible()
            page.get_by_role("button", name="Voltar", exact=True).click()
            assert page.evaluate("menuShips.slice(-1)[0]") == ["3lives.png", -30, 139]
            page.clock.run_for(35 * 30)
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
                canvas = page.locator("canvas:visible").bounding_box()
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
        for mode in ("Enter", "Space", "click", "touch"):
            entry_context = browser.new_context(viewport={"width": width, "height": 900}, has_touch=True)
            page = entry_context.new_page()
            record_keyboard(page)
            page.clock.install(time=datetime(2026, 1, 1))
            page.clock.pause_at(datetime(2026, 1, 1))
            page.goto(url)
            tab_to(page, "game-action")
            page.keyboard.press("Enter")
            tab_to(page, "game-new")
            page.keyboard.down("ArrowRight")
            target = page.locator("#game-new")
            if mode in ("Enter", "Space"):
                page.keyboard.down(mode)
                page.keyboard.down(mode)
            elif mode == "click":
                target.click()
            else:
                target.tap()
            assert page.get_by_role("button", name="Pausar", exact=True).is_visible()
            assert page.evaluate("document.activeElement.id") == "game-new", mode
            keyboard_hint(page, False)
            assert target.inner_text() == "Teclado do jogo"
            assert page.get_by_role("button", name="Teclado do jogo", exact=True).evaluate("n => n === document.activeElement")
            assert target.evaluate("n => getComputedStyle(n).pointerEvents") == "none"
            assert page.locator("#game-keyboard").locator("..").evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
            if mode in ("Enter", "Space"):
                page.keyboard.up(mode)
            assert page.evaluate("document.activeElement.id") == "game-new"
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 0)
            page.keyboard.up("ArrowRight")
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 30)
            page.keyboard.up("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 30)
            page.keyboard.press("Space")
            assert page.get_by_role("button", name="Pausar", exact=True).is_visible()
            page.keyboard.press("Enter")
            assert page.get_by_role("button", name="Continuar", exact=True).is_visible()
            tab_to(page, "game-continue")
            assert target.evaluate("n => getComputedStyle(n).display") == "none"
            page.keyboard.down("ArrowRight")
            if mode in ("Enter", "Space"):
                page.keyboard.press(mode)
            elif mode == "click":
                page.locator("#game-continue").click()
            else:
                page.locator("#game-continue").tap()
            assert page.evaluate("document.activeElement.id") == "game-continue"
            keyboard_hint(page, False)
            assert page.locator("#game-continue").inner_text() == "Teclado do jogo"
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 30)
            page.keyboard.up("ArrowRight")
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 60)
            page.keyboard.up("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 60)
            page.keyboard.press("Enter")
            assert page.locator("#game-continue").inner_text() == "Continuar"
            tab_to(page, "game-restart")
            page.keyboard.down("ArrowRight")
            if mode in ("Enter", "Space"):
                page.keyboard.press(mode)
            elif mode == "click":
                page.locator("#game-restart").click()
            else:
                page.locator("#game-restart").tap()
            assert page.evaluate("document.activeElement.id") == "game-restart"
            keyboard_hint(page, False)
            assert page.locator("#game-restart").inner_text() == "Teclado do jogo"
            ship_at(page, 0)
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 0)
            page.keyboard.up("ArrowRight")
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 30)
            page.keyboard.up("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 30)
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 60)
            page.keyboard.press("Shift+Tab" if mode in ("Space", "touch") else "Tab")
            page.clock.run_for(180)
            ship_at(page, 60)
            assert page.locator("#game-restart").evaluate("n => getComputedStyle(n).display") == "none"
            if mode in ("Space", "touch"):
                assert page.evaluate("document.activeElement.id") == "game-keyboard"
                assert page.locator("#game-keyboard").locator("..").evaluate("n => getComputedStyle(n).outlineStyle") == "solid"
            else:
                assert page.get_by_role("button", name="↑", exact=True).evaluate("n => document.activeElement === n")
                assert page.locator("#game-keyboard").locator("..").evaluate("n => getComputedStyle(n).outlineStyle") == "none"
            keyboard_hint(page, mode not in ("Space", "touch"))
            tab_to(page, "game-action")
            keyboard_hint(page, False)
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 60)
            page.keyboard.up("ArrowRight")
            page.keyboard.down("ArrowRight")
            page.clock.run_for(180)
            ship_at(page, 90)
            page.keyboard.up("ArrowRight")
            ship_at(page, 90)
            events = page.evaluate("keyboardEvents")
            assert ["keydown", "ArrowRight", "game-new"] in events
            assert ["keydown", "ArrowRight", "game-continue"] in events
            assert ["keydown", "ArrowRight", "game-restart"] in events
            if mode in ("Enter", "Space"):
                assert page.evaluate("pointerdowns") == 0
            else:
                assert page.evaluate("pointerdowns") == 3
            assert page.evaluate("keyboardEvents.filter(e => e[1] === 'ArrowRight').every(e => e[2] !== 'game-keyboard')")
            page.screenshot(path=str(evidence / f"keyboard-retained-{mode}-{width}.png"), full_page=True)
            print(f"PASS retained {mode} option start x0→30, Continue x30→60, Restart x60→0→30, blur/held lock x60, fresh x90; pointerdowns={page.evaluate('pointerdowns')} at {width}px")
            entry_context.close()
        context.close()
        print(f"PASS every menu/pause option via Enter, Confirmar/Space/click and direct touch; retained controls isolated after three held-Enter transitions at {width}px")


def controls_guide(browser, url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/credits-text-browser"
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        page.get_by_role("button", name="Pular créditos", exact=True).click()
        for mode in ("Enter", "Space", "click", "touch"):
            controls = page.get_by_role("button", name="Controles", exact=True)
            if mode in ("Enter", "Space"):
                controls.focus()
                page.keyboard.press(mode)
            elif mode == "click":
                controls.click()
            else:
                controls.tap()
            back = page.get_by_role("button", name="Voltar", exact=True)
            assert back.is_visible()
            guide = page.locator("#game-help")
            assert guide.is_visible()
            assert guide.evaluate("n => [getComputedStyle(n).fontSize, getComputedStyle(n).lineHeight, getComputedStyle(n).fontFamily, getComputedStyle(n).gap]") == ["14px", "20px", "sans-serif", "12px"]
            assert guide.bounding_box()["width"] == 248
            assert guide.evaluate("n => ['paddingTop','paddingRight','paddingBottom','paddingLeft'].map(k => getComputedStyle(n)[k])") == ["16px"] * 4
            assert guide.locator("table").bounding_box()["width"] == 216
            special = guide.locator("#controls-special")
            assert special.is_visible()
            assert special.bounding_box()["width"] == 216
            assert special.get_by_text("Especial", exact=True).is_visible()
            assert special.inner_text() == "Especial\nO botão Especial fica à direita da área de jogo. Quando estiver habilitado, toque nele para lançar três feixes e gastar uma carga. No teclado, use 1 com foco no jogo. Segurar não repete o disparo.\nDepois de atingir a potência máxima da arma, pegar outro item de evolução concede uma carga."
            assert special.bounding_box()["y"] < page.locator("#game-details").bounding_box()["y"]
            window_box = page.locator(".kof-window").bounding_box()
            back_box = back.bounding_box()
            assert back_box["y"] + back_box["height"] <= window_box["y"] + window_box["height"]
            assert page.locator("#controls-heading").bounding_box()["height"] == 44
            assert page.locator("#game-keyboard").bounding_box()["height"] == 44
            assert not page.locator("canvas:visible").is_visible()
            for name in ("↑", "↓", "←", "→", "Especial"):
                assert not page.get_by_role("button", name=name, exact=True).is_visible()
            assert page.get_by_text("Na abertura, use Tab ou clique em um controle. O foco do menu permite jogar sem clicar na área; ela continua disponível por clique ou Tab.", exact=True).is_visible()
            assert guide.locator("th").all_text_contents() == ["Tecla", "Ação"]
            assert guide.locator("td").all_text_contents() == ["Setas", "Mover a nave na partida", "↑ / ↓", "Escolher uma opção nos menus", "Enter", "Confirmar nos menus; pausar na partida", "1", "Usar o especial quando disponível"]
            assert guide.locator("#controls-touch li").all_text_contents() == ["Toque em uma opção do menu para abri-la.", "Segure as setas para mover. Combine duas para fazer diagonal.", "Solte todas as setas para parar.", "Especial: uma tentativa por pressão, quando disponível.", "Pausar: abrir o menu da pausa."]
            for title in ("Teclado", "Toque"):
                assert guide.get_by_text(title, exact=True).evaluate("n => getComputedStyle(n).fontSize") == "16px"
            details = page.locator("#controls-details")
            assert not details.is_visible()
            assert page.get_by_text("Clique no jogo ou use Tab para ativar teclado. Setas movem; Enter age; 1 dispara especial.", exact=True).count() == 0
            if mode == "Enter":
                page.screenshot(path=str(evidence / f"controls-closed-{width}.png"), full_page=True)
            toggle = page.get_by_role("button", name="Mais detalhes", exact=True)
            if mode in ("Enter", "Space"):
                toggle.focus()
                page.keyboard.down(mode)
                page.keyboard.down(mode)
                if mode == "Space":
                    page.keyboard.up(mode)
            elif mode == "click":
                toggle.click()
            else:
                toggle.tap()
            assert details.is_visible()
            assert back.is_visible()
            text = details.inner_text()
            for term in ("opostas", "última", "Arrasto", "cancelamento", "Soltar uma", "prioridade", "disponível", "foco", "Espaço", "Enter/Espaço"):
                assert term in text, (term, text)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert page.evaluate("Array.from(document.querySelectorAll('*')).filter(n => ['auto','scroll'].includes(getComputedStyle(n).overflowX)).every(n => n.scrollWidth <= n.clientWidth)")
            if mode == "Enter":
                page.clock.run_for(90)
                assert details.is_visible()
                page.screenshot(path=str(evidence / f"controls-open-{width}.png"), full_page=True)
                back.scroll_into_view_if_needed()
                assert back.is_visible()
                page.screenshot(path=str(evidence / f"controls-open-bottom-{width}.png"), full_page=True)
                back.focus()
                page.keyboard.down("Enter")
                assert back.is_visible()
                page.keyboard.up("Enter")
            page.get_by_role("button", name="Menos detalhes", exact=True).click()
            assert not details.is_visible()
            page.get_by_role("button", name="Mais detalhes", exact=True).click()
            if mode in ("Enter", "Space"):
                back.focus()
                page.keyboard.press(mode)
            elif mode == "click":
                back.click()
            else:
                back.tap()
            assert page.get_by_role("button", name="Controles", exact=True).is_visible()
            assert page.locator("canvas:visible").is_visible()
            assert page.locator("#game-keyboard").bounding_box()["height"] == 220
            assert not guide.is_visible()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        context.close()
        print(f"PASS compact Controls, 14/16px guide, closed/open/reset details and Enter/Space/click/touch without duplicate transitions at {width}px")


def retained_options(browser, url):
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        record_menu(page)
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        page.get_by_role("button", name="Pular créditos", exact=True).click()
        for option, held_key in (("Controles", "Enter"), ("Reiniciar", "Enter"), ("Menu principal", "Enter"),
                                 ("Controles", "Space"), ("Reiniciar", "Space"), ("Menu principal", "Space")):
            if option != "Controles":
                page.get_by_role("button", name="Novo Jogo", exact=True).click()
                page.get_by_role("button", name="Pausar", exact=True).click()
            target = page.locator({"Controles": "#game-controls", "Reiniciar": "#game-restart", "Menu principal": "#game-menu"}[option])
            target.focus()
            old_box = target.bounding_box()
            page.keyboard.down(held_key)
            expected = "Voltar" if option == "Controles" else "Pausar" if option == "Reiniciar" else "Novo Jogo"
            assert page.get_by_role("button", name=expected, exact=True).is_visible()
            assert target.evaluate("n => document.activeElement === n")
            assert target.evaluate("n => getComputedStyle(n).pointerEvents") == "none"
            assert target.bounding_box()["x"] < -1000
            if option == "Menu principal":
                page.keyboard.press("ArrowDown")
                selected_line(page, "Controles", 139)
            if held_key == "Enter":
                page.keyboard.press("Space")
            else:
                page.keyboard.down("Space")
            page.touchscreen.tap(old_box["x"] + old_box["width"] / 2, old_box["y"] + 1)
            page.keyboard.down(held_key)
            assert page.get_by_role("button", name=expected, exact=True).is_visible()
            if option == "Controles":
                page.locator("#game-keyboard").focus()
            page.keyboard.up(held_key)
            assert not target.is_visible(), (option, held_key, target.bounding_box(), page.locator("#game-action").inner_text())
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
                page.keyboard.press("ArrowUp")
                page.keyboard.press("Enter")
                assert page.get_by_role("button", name="Pausar", exact=True).is_visible()
                page.get_by_role("button", name="Pausar", exact=True).click()
                page.get_by_role("button", name="Menu principal", exact=True).click()
        context.close()
        print(f"PASS retained options reject Space/Enter/touch after Controls/Restart/Main Menu; releases rearm at {width}px")


def repeated_entrances(browser, url, result_url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/credits-text-browser"
    for width in (320, 1200):
        page = browser.new_page(viewport={"width": width, "height": 1000})
        record_menu(page)
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)

        def arrival(selection):
            y = 120 + selection * 19
            assert page.evaluate("menuShips.slice(-1)[0]") == ["3lives.png", -30, y]
            page.locator("#game-keyboard").focus()
            page.keyboard.press("ArrowLeft")
            assert page.evaluate("menuShips.slice(-1)[0]") == ["3lives.png", -30, y]
            page.clock.run_for(30)
            sprite(page, "3lives.png", -20, y)
            page.clock.run_for(10 * 30)
            sprite(page, "3lives.png", 80, y)
            page.clock.run_for(30)
            sprite(page, "2lives.png", 87, y)
            page.clock.run_for(23 * 30)
            sprite(page, "2lives.png", 18, y)
            page.clock.run_for(90)
            assert page.evaluate("menuShips.slice(-1)[0]") == ["2lives.png", 18, y]
            assert page.get_by_role("button", name="Pular créditos", exact=True).count() == 0

        page.get_by_role("button", name="Pular créditos", exact=True).click()
        arrival(0)
        for _ in range(2):
            page.get_by_role("button", name="Controles", exact=True).click()
            page.get_by_role("button", name="Voltar", exact=True).click()
            arrival(1)
            page.get_by_role("button", name="Novo Jogo", exact=True).click()
            page.get_by_role("button", name="Pausar", exact=True).click()
            page.get_by_role("button", name="Menu principal", exact=True).click()
            arrival(0)
        page.get_by_role("button", name="Controles", exact=True).click()
        page.get_by_role("button", name="Voltar", exact=True).click()
        assert page.evaluate("menuShips.slice(-1)[0]") == ["3lives.png", -30, 139]
        page.get_by_role("button", name="Novo Jogo", exact=True).click()
        assert page.get_by_role("button", name="Pausar", exact=True).is_visible()
        page.goto(result_url)
        for _ in range(2):
            for _ in range(3):
                page.get_by_role("button", name="Hit ship", exact=True).click()
            conclude = page.get_by_role("button", name="Concluir contagem", exact=True)
            if conclude.is_visible():
                conclude.click()
            page.get_by_role("button", name="Voltar ao menu", exact=True).click()
            arrival(0)
            page.get_by_role("button", name="Novo Jogo", exact=True).click()
        page.close()
        print(f"PASS repeated real skip/Controls/pause/result arrivals at -30/-20/80/87/18, repaint and early confirmation at {width}px")


def keyboard_hint_presentation(browser, url, result_url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/keyboard-focus"
    evidence.mkdir(parents=True, exist_ok=True)
    for width in (320, 1200):
        for density in (1, 2):
            context = browser.new_context(viewport={"width": width, "height": 900}, device_scale_factor=density)
            page = context.new_page()
            record_keyboard(page)
            page.clock.install(time=datetime(2026, 1, 1))
            page.clock.pause_at(datetime(2026, 1, 1))
            page.goto(url)
            page.wait_for_function("Object.values(window.__kofNodes).filter(n => n.tagName === 'IMG').every(n => n.complete && n.naturalWidth > 0)")
            assert not page.locator("#game-keyboard-hint").is_visible()
            page.locator("#game-action").click()
            assert not page.locator("#game-keyboard-hint").is_visible()
            page.locator("#game-new").click()
            keyboard_hint(page, False)
            initial_bounds = page.locator("canvas:visible").bounding_box()
            action_bounds = page.locator("#game-action").bounding_box()
            for entry in ("click", "Tab"):
                page.mouse.click(2, 2)
                point = keyboard_hint(page, True)
                assert page.locator("canvas:visible").bounding_box() == initial_bounds
                assert page.locator("#game-action").bounding_box() == action_bounds
                page.screenshot(path=str(evidence / f"after-unfocused-{entry}-{width}-d{density}.png"), full_page=True)
                if entry == "click":
                    page.mouse.click(**point)
                else:
                    tab_to(page, "game-keyboard")
                assert page.evaluate("document.activeElement.id") == "game-keyboard"
                keyboard_hint(page, False)
                page.screenshot(path=str(evidence / f"after-focused-{entry}-{width}-d{density}.png"), full_page=True)
                page.keyboard.down("ArrowRight")
                page.clock.run_for(180)
                ship_at(page, 30 if entry == "click" else 60)
                page.keyboard.up("ArrowRight")
            page.locator("#game-action").focus()
            keyboard_hint(page, False)
            page.locator("#game-action").click()
            assert not page.locator("#game-keyboard-hint").is_visible()
            page.locator("#game-menu").click()
            assert not page.locator("#game-keyboard-hint").is_visible()
            page.locator("#game-controls").click()
            assert not page.locator("#game-keyboard-hint").is_visible()
            assert page.locator("#game-keyboard").bounding_box()["height"] == 44
            assert page.evaluate("devicePixelRatio") == density
            assert page.evaluate("visualViewport.scale") == 1
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            context.close()
            print(f"PASS hint pixels/style/hit target, immediate click/Tab focus, x0→30→60, unchanged layout, other screens at {width}px density{density} zoom100%")
    page = browser.new_page()
    page.clock.install(time=datetime(2026, 1, 1))
    page.clock.pause_at(datetime(2026, 1, 1))
    page.goto(result_url)
    for _ in range(3):
        page.get_by_role("button", name="Hit ship", exact=True).click()
    assert not page.locator("#game-keyboard-hint").is_visible()
    page.close()
    print("PASS keyboard hint absent on deterministic result screen")


def density_presentation(browser, url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/credits-text-browser"
    evidence.mkdir(parents=True, exist_ok=True)
    for width in (320, 1200):
        for density in (1, 2):
            context = browser.new_context(viewport={"width": width, "height": 1100}, device_scale_factor=density)
            page = context.new_page()
            record_menu(page)
            page.clock.install(time=datetime(2026, 1, 1))
            page.clock.pause_at(datetime(2026, 1, 1))
            page.goto(url)
            page.wait_for_function("Object.values(window.__kofNodes).filter(n => n.tagName === 'IMG').every(n => n.complete && n.naturalWidth > 0)")
            page.clock.run_for(55 * 30)
            text_lines(page, CREDIT_LABELS, 12, [56, 80, 104, 152, 176, 200], "#0080ff", settled=True)
            assert page.locator("canvas:visible").evaluate("n => {const p=n.getContext('2d').getImageData(0,0,n.width,n.height).data;for(let i=3;i<p.length;i+=4){if(p[i]>0&&p[i]<255)return true;}return false;}")
            assert page.evaluate("devicePixelRatio") == density
            assert page.evaluate("visualViewport.scale") == 1
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path=str(evidence / f"credits-{width}-d{density}.png"), full_page=True)
            page.locator("canvas:visible").screenshot(path=str(evidence / f"credits-canvas-{width}-d{density}.png"))
            page.get_by_role("button", name="Pular créditos", exact=True).click()
            page.clock.run_for(35 * 30)
            menu_lines(page, ["Novo Jogo", "Controles"], [120, 139])
            page.screenshot(path=str(evidence / f"menu-{width}-d{density}.png"), full_page=True)
            page.locator("canvas:visible").screenshot(path=str(evidence / f"menu-canvas-{width}-d{density}.png"))
            page.get_by_role("button", name="Novo Jogo", exact=True).click()
            page.get_by_role("button", name="Pausar", exact=True).click()
            menu_lines(page, ["Continuar", "Reiniciar", "Menu principal"], [80, 99, 118])
            page.screenshot(path=str(evidence / f"pause-{width}-d{density}.png"), full_page=True)
            page.locator("canvas:visible").screenshot(path=str(evidence / f"pause-canvas-{width}-d{density}.png"))
            page.get_by_role("button", name="Menu principal", exact=True).click()
            page.get_by_role("button", name="Controles", exact=True).click()
            guide = page.locator("#game-help")
            bounds = guide.bounding_box()
            child = guide.locator(":scope > :first-child").bounding_box()
            assert child["x"] - bounds["x"] == 16 and child["y"] - bounds["y"] == 16
            assert bounds["width"] - child["width"] == 32
            assert guide.locator("table").bounding_box()["width"] == 216
            assert page.locator("#controls-special").is_visible()
            assert not page.locator("#controls-details").is_visible()
            last = guide.locator(":scope > :nth-child(4)").bounding_box()
            assert abs(bounds["y"] + bounds["height"] - last["y"] - last["height"] - 16) < 0.01
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path=str(evidence / f"guide-{width}-d{density}.png"), full_page=True)
            page.get_by_role("button", name="Mais detalhes", exact=True).click()
            assert page.evaluate("Array.from(document.querySelectorAll('*')).filter(n => ['auto','scroll'].includes(getComputedStyle(n).overflowX)).every(n => n.scrollWidth <= n.clientWidth)")
            page.screenshot(path=str(evidence / f"guide-open-{width}-d{density}.png"), full_page=True)
            page.get_by_role("button", name="Voltar", exact=True).click()
            assert page.evaluate("Object.values(window.__kofNodes).filter(n => n.tagName === 'IMG' && n.src.includes('/font-')).length") == 0
            context.close()
            print(f"PASS 16px smooth text, complete credits/email at zoom100%, no bitmap fonts, guide padding/216px and closed Special at {width}px density{density}")

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
                credits_animation(browser, url)
                menu_presentation(browser, url)
                controls_guide(browser, url)
                retained_options(browser, url)
                confirmation_journeys(browser, url)
                repeated_entrances(browser, url, result_url)
                keyboard_hint_presentation(browser, url, result_url)
                density_presentation(browser, url)
                startup_context.close()
                for width in (320, 1200):
                    context = browser.new_context(viewport={"width": width, "height": 900})
                    startup_page = context.new_page()
                    record_keyboard(startup_page)
                    startup_page.clock.install(time=datetime(2026, 1, 1))
                    startup_page.clock.pause_at(datetime(2026, 1, 1))
                    startup_page.goto(url)
                    assert startup_page.evaluate("document.activeElement.tagName") == "BODY"
                    tab_to(startup_page, "game-action")
                    startup_page.keyboard.down("Enter")
                    startup_page.keyboard.down("Enter")
                    startup_page.clock.run_for(30)
                    assert startup_page.get_by_role("button", name="Novo Jogo").count() == 1
                    assert startup_page.get_by_role("button", name="Pausar").count() == 0
                    startup_page.keyboard.up("Enter")
                    for label in ("↑", "←", "→", "↓"):
                        assert startup_page.get_by_role("button", name=label, exact=True).is_disabled() == (label in ("←", "→"))
                    startup_page.keyboard.press("Enter")
                    assert startup_page.get_by_role("button", name="Pausar").is_visible()
                    assert startup_page.evaluate("document.activeElement.id") == "game-action"
                    sprite(startup_page, "Middle.png", 0, 100)
                    startup_page.keyboard.down("ArrowRight")
                    startup_page.clock.run_for(180)
                    sprite(startup_page, "Middle.png", 30, 100)
                    startup_page.keyboard.up("ArrowRight")
                    startup_page.clock.run_for(180)
                    sprite(startup_page, "Middle.png", 30, 100)
                    assert startup_page.evaluate("pointerdowns") == 0
                    assert startup_page.evaluate("keyboardEvents.filter(e => e[1] === 'ArrowRight')") == [
                        ["keydown", "ArrowRight", "game-action"], ["keyup", "ArrowRight", "game-action"]]
                    context.close()
                    print(f"PASS Tab/held Enter opens only menu; new Enter starts and action arrows move 0→30, release stops, zero pointerdowns at {width}px")
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
                overlay = page.locator("#game-keyboard")
                assert page.locator("input").count() == 0
                assert page.locator("canvas:visible").count() == 1
                assert overlay.bounding_box()["width"] == 262
                assert overlay.bounding_box()["height"] == 260
                for label in ("↑", "←", "→", "↓"):
                    zone = page.get_by_role("button", name=label, exact=True)
                    assert not zone.is_visible()
                page.keyboard.press("Tab")
                assert overlay.evaluate("node => document.activeElement === node")
                assert overlay.locator("..").evaluate("node => getComputedStyle(node).outlineStyle") == "solid"
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
                paused = page.locator("canvas:visible").screenshot()
                page.wait_for_timeout(160)
                assert page.locator("canvas:visible").screenshot() == paused
                page.get_by_role("button", name="Continuar").click()
                wait_for(lambda: page.get_by_role("button", name="Pausar").count() == 1, page)
                page.goto(result_url)
                for life in range(3):
                    page.get_by_role("button", name="Hit ship", exact=True).click()
                wait_for(lambda: page.get_by_role("button", name="Voltar ao menu").count() == 1, page)
                result = page.locator("canvas:visible").screenshot()
                page.wait_for_timeout(100)
                assert page.locator("canvas:visible").screenshot() != result
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
                menu_navigation(browser, url)
                print("PASS menu, Enter and Space, conservative confirmation, pause, result and menu in Chrome")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
