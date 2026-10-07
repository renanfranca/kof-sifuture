"""Exercise the generated KofJS game in Chrome with observable waits."""

import argparse
import math
import json
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


FONT_DATA = json.loads((Path(__file__).resolve().parents[1] / "fonts/bitmap.json").read_text())["fonts"]


def record_menu(page):
    page.add_init_script("""
        window.bitmapDraws = [];
        window.menuShips = [];
        window.canvasTexts = [];
        const draw = CanvasRenderingContext2D.prototype.drawImage;
        const clear = CanvasRenderingContext2D.prototype.clearRect;
        const text = CanvasRenderingContext2D.prototype.fillText;
        CanvasRenderingContext2D.prototype.clearRect = function(x, y, w, h) {
            if (w === 176 && h === 220) window.bitmapDraws = [];
            return clear.call(this, x, y, w, h);
        };
        CanvasRenderingContext2D.prototype.drawImage = function(image, x, y, ...rest) {
            const asset = image.src && image.src.split('/').pop();
            if (asset && asset.startsWith('font-')) {
                const m = this.getTransform();
                window.bitmapDraws.push({asset, x, y, rest, matrix: [m.a,m.b,m.c,m.d,m.e,m.f]});
            }
            if (asset && /[23]lives\.png$/.test(asset)) window.menuShips.push([asset, x, y]);
            return draw.call(this, image, x, y, ...rest);
        };
        CanvasRenderingContext2D.prototype.fillText = function(label, x, y, ...rest) {
            window.canvasTexts.push(label);
            return text.call(this, label, x, y, ...rest);
        };
    """)


def bitmap_lines(page, font_name, labels, x, baselines, pixels=False):
    glyphs = {g["character"]: g for g in FONT_DATA[font_name]["glyphs"]}
    expected = []
    for label, baseline in zip(labels, baselines):
        cursor = x
        for c in label:
            glyph = glyphs[c]
            expected.append({"asset": glyph["asset"], "x": cursor + glyph["left"], "y": baseline + glyph["top"],
                             "rest": [], "matrix": [1, 0, 0, 1, 0, 0]})
            cursor += glyph["advance"]
        assert cursor - x <= (130 if font_name == "credits" else 128)
    assert page.evaluate("bitmapDraws") == expected
    assert page.evaluate("canvasTexts") == []
    if pixels:
        observed = page.locator("canvas").evaluate("n => Array.from(n.getContext('2d').getImageData(0,0,176,220).data)")
        from PIL import Image
        composed = Image.new("RGBA", (176, 220))
        for draw in expected:
            glyph = Image.open(Path(__file__).resolve().parents[1] / "assets" / draw["asset"]).convert("RGBA")
            composed.alpha_composite(glyph, (draw["x"], draw["y"]))
        for y in range(220):
            for px in range(176):
                index = 4 * (y * 176 + px)
                assert tuple(observed[index:index+4]) == composed.getpixel((px, y)), (px, y)


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
        bitmap_lines(page, "menu", ["Novo Jogo", "Controles"], 48, [133, 152])
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
        bitmap_lines(page, "menu", ["Continuar", "Reiniciar", "Menu principal"], 48, [93, 112, 131])
        page.get_by_role("button", name="Menu principal", exact=True).focus()
        selected_line(page, "Menu principal", 118)
        sprite(page, "2lives.png", 18, 118)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.close()
        print(f"PASS Portuguese bitmap menus at x48/14px, ship selection and independent neutral focus at {width}px")


def credits_animation(browser, url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/navigation-browser"
    evidence.mkdir(parents=True, exist_ok=True)
    for width in (320, 1200):
        page = browser.new_page(viewport={"width": width, "height": 1000})
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        record_menu(page)
        page.goto(url)
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.press("ArrowLeft")

        def credits(x, y0, y1):
            bitmap_lines(page, "credits", ["Copyright (c) 2006-2007", "Renan Meneses de Andrade Franca", "contact:",
                         "renan.andradefranca@gmail.com", "Inc. All rights reserved."], x,
                         [y0 + 8, y0 + 18, y1 + 8, y1 + 18, y1 + 28], pixels=(x == 46 and y0 == 110))
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
        assert all(d["matrix"] == [1, 0, 0, 1, 0, 0] for d in page.evaluate("bitmapDraws"))
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
        page.evaluate("bitmapDraws.length=0")
        page.clock.run_for(30)
        assert page.get_by_role("button", name="Pular créditos", exact=True).count() == 1
        assert page.evaluate("bitmapDraws.length") == 0
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
        print(f"PASS credits frames0/1/36/85/86/87/258/259/260, literal bitmap contact/pixel equality/transform isolation and entrance0/1/11/12/13/35/36 at {width}px")


def menu_navigation(browser, url):
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        record_menu(page)
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
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/navigation-browser"
    for width in (320, 1200):
        context = browser.new_context(viewport={"width": width, "height": 1000}, has_touch=True)
        page = context.new_page()
        record_menu(page)
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


def controls_guide(browser, url):
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
            assert not page.locator("canvas").is_visible()
            for name in ("↑", "↓", "←", "→", "Especial"):
                assert not page.get_by_role("button", name=name, exact=True).is_visible()
            assert page.get_by_text("Na partida, clique na área do jogo ou use Tab até ‘Ativar teclado do jogo’.", exact=True).is_visible()
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
            assert page.locator("canvas").is_visible()
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
            target = page.get_by_role("button", name=option, exact=True)
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
                selected_line(page, "Novo Jogo", 120)
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
                page.keyboard.press("Enter")
                assert page.get_by_role("button", name="Pausar", exact=True).is_visible()
                page.get_by_role("button", name="Pausar", exact=True).click()
                page.get_by_role("button", name="Menu principal", exact=True).click()
        context.close()
        print(f"PASS retained options reject Space/Enter/touch after Controls/Restart/Main Menu; releases rearm at {width}px")


def repeated_entrances(browser, url, result_url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/navigation-browser"
    for width in (320, 1200):
        page = browser.new_page(viewport={"width": width, "height": 1000})
        record_menu(page)
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)

        def arrival(selection):
            y = 120 + selection * 19
            assert page.evaluate("menuShips.slice(-1)[0]") == ["3lives.png", -30, y]
            page.get_by_role("button", name="Ativar teclado do jogo", exact=True).focus()
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


def density_presentation(browser, url):
    evidence = Path(__file__).resolve().parents[1] / ".agent/tmp/clarity-browser"
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
            page.clock.run_for(36 * 30)
            labels = ["Copyright (c) 2006-2007", "Renan Meneses de Andrade Franca", "contact:", "renan.andradefranca@gmail.com", "Inc. All rights reserved."]
            bitmap_lines(page, "credits", labels, 46, [118,128,149,159,169], pixels=True)
            images = page.evaluate("Object.values(window.__kofNodes).filter(n => n.tagName === 'IMG' && n.src.includes('/font-')).length")
            page.screenshot(path=str(evidence / f"credits-{width}-d{density}.png"), full_page=True)
            page.get_by_role("button", name="Pular créditos", exact=True).click()
            page.clock.run_for(35 * 30)
            bitmap_lines(page, "menu", ["Novo Jogo", "Controles"], 48, [133,152])
            page.screenshot(path=str(evidence / f"menu-{width}-d{density}.png"), full_page=True)
            page.get_by_role("button", name="Novo Jogo", exact=True).click()
            page.get_by_role("button", name="Pausar", exact=True).click()
            bitmap_lines(page, "menu", ["Continuar", "Reiniciar", "Menu principal"], 48, [93,112,131])
            page.screenshot(path=str(evidence / f"pause-{width}-d{density}.png"), full_page=True)
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
            assert page.evaluate("Object.values(window.__kofNodes).filter(n => n.tagName === 'IMG' && n.src.includes('/font-')).length") == images
            context.close()
            print(f"PASS native glyph pixels, single image load, 16px padding/216px content and closed Special at {width}px density{density}")

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
                density_presentation(browser, url)
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
                menu_navigation(browser, url)
                print("PASS menu, Enter and Space, conservative confirmation, pause, result and menu in Chrome")
            finally:
                browser.close()


if __name__ == "__main__":
    main()
