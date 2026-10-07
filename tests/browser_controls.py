import argparse
from contextlib import contextmanager
from datetime import datetime
import io
import json
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from kof_project import served_build

TOUCH_EVIDENCE = []

SHIP = Image.open(ROOT / "assets/Middle.png").convert("RGBA")
SHIP_RIGHT = Image.open(ROOT / "assets/Middle2.png").convert("RGBA")
SAMPLES = [(x, y, SHIP.getpixel((x, y))[:3]) for y in range(20) for x in range(50)
           if SHIP.getpixel((x, y))[3] == 255][::7]
JET_SAMPLES = [(x, y, SHIP_RIGHT.getpixel((x, y))[:3]) for y in range(20) for x in range(50)
               if SHIP.getpixel((x, y))[3] == 0 and SHIP_RIGHT.getpixel((x, y))[3] == 255][::3]


def ship_observation(page):
    canvas = Image.open(io.BytesIO(page.locator("canvas").screenshot())).convert("RGB")
    pixels = canvas.load()
    anchor_x, anchor_y, anchor_rgb = SAMPLES[0]
    candidates = []
    for top in range(30, 201):
        for left in range(127):
            if pixels[left + anchor_x, top + anchor_y] != anchor_rgb:
                continue
            matches = sum(pixels[left + x, top + y] == rgb for x, y, rgb in SAMPLES)
            if matches >= len(SAMPLES) * 0.9:
                candidates.append((matches, left, top))
    if not candidates:
        return None, None, None
    _, x, y = max(candidates)
    jets = sum(pixels[x + px, y + py] == rgb for px, py, rgb in JET_SAMPLES)
    return x, y, jets >= len(JET_SAMPLES) * 0.9


def ship_x(page):
    return ship_observation(page)[0]


@contextmanager
def control_page(browser, url, *, touch=False, width=800):
    context = browser.new_context(viewport={"width": width, "height": 700}, has_touch=touch, is_mobile=touch)
    try:
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.clock.install(time=datetime(2026, 1, 1))
        page.clock.pause_at(datetime(2026, 1, 1))
        page.goto(url)
        page.clock.run_for(30)
        assert ship_observation(page) == (60, 100, False)
        cycles = 1

        def run(steps):
            nonlocal cycles
            cycles += steps
            assert cycles <= 40
            page.clock.run_for(steps * 30)

        yield page, run
        assert not errors, errors
    finally:
        context.close()


def keyboard_origin_and_release(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        page.get_by_role("button", name="Pausar").focus()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, 100, False)

        overlay.focus()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (60, 100, False)

        page.get_by_role("button", name="Pausar").focus()
        page.keyboard.up("ArrowRight")
        overlay.focus()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, 100, True)

        page.keyboard.up("ArrowRight")
        run(3)
        assert ship_observation(page) == (80, 100, False)


def opposing_arrows(browser, url):
    with control_page(browser, url) as (page, run):
        page.get_by_role("button", name="Ativar teclado do jogo").click()
        page.keyboard.down("ArrowRight")
        run(3)
        assert ship_observation(page) == (75, 100, True)

        page.keyboard.down("ArrowLeft")
        run(2)
        assert ship_observation(page) == (65, 100, False)

        page.keyboard.up("ArrowLeft")
        run(2)
        assert ship_observation(page) == (75, 100, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (75, 100, False)


def tab_keeps_lost_release_blocked(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.click()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, 100, True)

        page.mouse.click(500, 500)
        run(4)
        assert ship_observation(page) == (80, 100, False)

        page.keyboard.up("ArrowRight")
        page.keyboard.press("Tab")
        assert overlay.evaluate("node => document.activeElement === node")
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, 100, False)

        page.keyboard.up("ArrowRight")
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (100, 100, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (100, 100, False)


def click_rearms_held_arrow(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.click()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, 100, True)

        page.mouse.click(500, 500)
        run(4)
        assert ship_observation(page) == (80, 100, False)

        overlay.click()
        run(4)
        assert ship_observation(page) == (80, 100, False)

        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (100, 100, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (100, 100, False)


def click_rearms_after_external_release(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.click()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, 100, True)

        page.mouse.click(500, 500)
        page.keyboard.up("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, 100, False)

        overlay.click()
        run(4)
        assert ship_observation(page) == (80, 100, False)

        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (100, 100, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (100, 100, False)


def mouse_pad_exit_and_cancel(browser, url):
    with control_page(browser, url) as (page, run):
        east = page.get_by_role("button", name="→", exact=True)
        box = east.bounding_box()
        page.mouse.move(box["x"] + 24, box["y"] + 24)
        page.mouse.down()
        run(3)
        assert ship_observation(page) == (75, 100, True)

        page.mouse.move(box["x"] + 150, box["y"] + 24)
        run(3)
        assert ship_observation(page) == (75, 100, False)

        page.mouse.move(box["x"] + 24, box["y"] + 24)
        run(3)
        assert ship_observation(page) == (75, 100, False)
        page.mouse.up()

        east.dispatch_event("pointerdown")
        run(3)
        assert ship_observation(page) == (90, 100, True)

        east.dispatch_event("pointercancel")
        run(3)
        assert ship_observation(page) == (90, 100, False)


def pad_owns_movement(browser, url):
    with control_page(browser, url) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        east = page.get_by_role("button", name="→", exact=True)
        box = east.bounding_box()
        overlay.click()
        page.keyboard.down("ArrowLeft")
        run(3)
        assert ship_observation(page) == (45, 100, False)

        page.mouse.move(box["x"] + 24, box["y"] + 24)
        page.mouse.down()
        assert east.evaluate("node => document.activeElement === node")
        run(3)
        assert ship_observation(page) == (60, 100, True)

        page.keyboard.down("ArrowUp")
        run(3)
        assert ship_observation(page) == (75, 100, True)

        page.mouse.up()
        run(3)
        assert ship_observation(page) == (75, 100, False)

        page.keyboard.down("ArrowLeft")
        page.keyboard.down("ArrowUp")
        run(3)
        assert ship_observation(page) == (75, 100, False)

        overlay.focus()
        page.keyboard.down("ArrowLeft")
        run(3)
        assert ship_observation(page) == (75, 100, False)
        page.keyboard.up("ArrowLeft")
        page.keyboard.up("ArrowUp")


def touch_pad_drag_release_and_cancel(browser, url):
    with control_page(browser, url, touch=True) as (page, run):
        touch = TouchContacts(page)
        touch.press("→")
        run(1)
        assert ship_observation(page) == (65, 100, True)
        touch.drag("→", "↑")
        run(1)
        assert ship_observation(page) == (70, 100, True)
        touch.press("↓")
        run(1)
        assert ship_observation(page) == (75, 105, True)
        touch.release("→")
        run(1)
        assert ship_observation(page) == (75, 110, False)
        touch.cancel()
        run(1)
        assert ship_observation(page) == (75, 110, False)
        touch.press("←", "↑")
        run(1)
        assert ship_observation(page) == (70, 105, False)
        touch.cancel()
        run(1)
        assert ship_observation(page) == (70, 105, False)
        touch.press("→")
        run(1)
        assert ship_observation(page) == (75, 105, True)
        touch.release("→")
        run(1)
        assert ship_observation(page) == (75, 105, False)
        TOUCH_EVIDENCE.append({"case": "drag-cancel", "events": touch.events()})
    print("PASS captured drag retains its initial arrow, selective release preserves other axis, total cancel permits new press")


def touch_click_rearms_arrow(browser, url):
    with control_page(browser, url, touch=True) as (page, run):
        overlay = page.get_by_role("button", name="Ativar teclado do jogo")
        overlay.focus()
        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (80, 100, True)

        page.touchscreen.tap(500, 500)
        page.keyboard.up("ArrowRight")
        run(3)
        assert ship_observation(page) == (80, 100, False)

        overlay.tap()
        run(3)
        assert ship_observation(page) == (80, 100, False)

        page.keyboard.down("ArrowRight")
        run(4)
        assert ship_observation(page) == (100, 100, True)

        page.keyboard.up("ArrowRight")
        run(2)
        assert ship_observation(page) == (100, 100, False)


class TouchContacts:
    def __init__(self, page):
        self.page = page
        self.session = page.context.new_cdp_session(page)
        self.contacts = {}
        self.next_id = 1
        self.pointer_ids = {}
        page.evaluate("""() => {
            window.controlEvents = [];
            for (const type of ['pointerdown', 'pointerup', 'pointercancel']) {
                document.addEventListener(type, e => {
                    if (e.target.tagName === 'BUTTON') {
                        window.controlEvents.push({type, label: e.target.textContent, id: e.pointerId});
                    }
                }, true);
            }
        }""")

    def events(self):
        return self.page.evaluate("window.controlEvents")

    def press(self, *labels):
        points = {}
        for label in labels:
            box = self.page.get_by_role("button", name=label, exact=True).bounding_box()
            points[label] = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        return self.press_at(points)

    def press_at(self, points):
        before = len(self.events())
        for label, (x, y) in points.items():
            assert label not in self.contacts
            self.contacts[label] = {"x": x, "y": y, "id": self.next_id}
            self.next_id += 1
        self.session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": list(self.contacts.values())})
        received = self.events()[before:]
        assert sorted(e["label"] for e in received if e["type"] == "pointerdown") == sorted(points), received
        for event in received:
            if event["type"] == "pointerdown":
                self.pointer_ids[event["label"]] = event["id"]
        return received

    def release(self, label):
        before = len(self.events())
        point = self.contacts.pop(label)
        self.session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": [point]})
        received = self.events()[before:]
        assert [(e["type"], e["label"], e["id"]) for e in received] == [("pointerup", label, self.pointer_ids.pop(label))], received

    def cancel(self):
        before = len(self.events())
        labels = sorted(self.contacts)
        self.session.send("Input.dispatchTouchEvent", {"type": "touchCancel", "touchPoints": []})
        received = self.events()[before:]
        assert sorted(e["label"] for e in received if e["type"] == "pointercancel") == labels, received
        self.contacts.clear()

    def drag(self, label, destination):
        box = self.page.get_by_role("button", name=destination, exact=True).bounding_box()
        self.contacts[label].update(x=box["x"] + box["width"] / 2, y=box["y"] + box["height"] / 2)
        self.session.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": list(self.contacts.values())})


def touch_on_canvas_axis(browser, url):
    for width in (320, 1200):
        with control_page(browser, url, touch=True, width=width) as (page, run):
            canvas = page.locator("canvas").bounding_box()
            north = page.get_by_role("button", name="↑", exact=True).bounding_box()
            point = (canvas["x"] + canvas["width"] / 2, north["y"] + north["height"] / 2)
            target = page.evaluate("p => document.elementFromPoint(p[0], p[1]).textContent", point)
            assert target == "↑", (width, point, target)

            touch = TouchContacts(page)
            touch.press_at({"↑": point})
            run(1)
            assert ship_observation(page) == (60, 95, False)
            run(1)
            assert ship_observation(page) == (60, 90, False)
            touch.release("↑")
            run(2)
            assert ship_observation(page) == (60, 90, False)
            TOUCH_EVIDENCE.append({"case": "canvas-axis", "viewport": width, "point": point,
                                   "after_one_step": [60, 95], "stopped": [60, 90], "events": touch.events()})
    print("PASS touch on canvas axis at 320/1200: (60,100) -> (60,95), held -> (60,90), release stops")


def touch_diagonals(browser, url):
    cases = (("→", "↑", 5, -5), ("→", "↓", 5, 5), ("←", "↑", -5, -5), ("←", "↓", -5, 5))
    for horizontal, vertical, dx, dy in cases:
        for press_vertical_first in (False, True):
            for release_vertical_first in (False, True):
                with control_page(browser, url, touch=True) as (page, run):
                    touch = TouchContacts(page)
                    first, second = (vertical, horizontal) if press_vertical_first else (horizontal, vertical)
                    touch.press(first)
                    run(1)
                    assert ship_observation(page) == (60 + (0 if press_vertical_first else dx),
                                                       100 + (dy if press_vertical_first else 0), first == "→")
                    touch.press(second)
                    run(1)
                    x = 60 + (dx if press_vertical_first else 2 * dx)
                    y = 100 + (2 * dy if press_vertical_first else dy)
                    assert ship_observation(page) == (x, y, horizontal == "→")
                    released, held = (vertical, horizontal) if release_vertical_first else (horizontal, vertical)
                    touch.release(released)
                    run(1)
                    x += dx if release_vertical_first else 0
                    y += 0 if release_vertical_first else dy
                    assert ship_observation(page) == (x, y, held == "→")
                    touch.release(held)
                    run(1)
                    assert ship_observation(page) == (x, y, False)
                    TOUCH_EVIDENCE.append({"case": "diagonal", "press": [first, second], "release": [released, held],
                                           "stopped": [x, y], "events": touch.events()})
    print("PASS four touch diagonals in both press/release orders: 16 journeys with x/y, propulsion and exact pointerup target/id")


def touch_opposites(browser, url):
    cases = (("→", "←", 5, 0), ("←", "→", -5, 0), ("↑", "↓", 0, -5), ("↓", "↑", 0, 5))
    for first, second, dx, dy in cases:
        for release_winner in (False, True):
            with control_page(browser, url, touch=True) as (page, run):
                touch = TouchContacts(page)
                touch.press(first)
                run(1)
                assert ship_observation(page) == (60 + dx, 100 + dy, first == "→")
                touch.press(second)
                run(1)
                assert ship_observation(page) == (60, 100, second == "→")
                released, held = (second, first) if release_winner else (first, second)
                touch.release(released)
                run(1)
                x, y = (60 + dx, 100 + dy) if release_winner else (60 - dx, 100 - dy)
                assert ship_observation(page) == (x, y, held == "→")
                touch.release(held)
                run(1)
                assert ship_observation(page) == (x, y, False)
                TOUCH_EVIDENCE.append({"case": "opposites", "press": [first, second], "release": [released, held],
                                       "stopped": [x, y], "events": touch.events()})
    print("PASS last opposite touch wins in both axes and orders: 8 journeys with resumed/retained movement and propulsion")


def simultaneous_direction_events(browser, url):
    cases = (("→", "↑"), ("←", "↓"), ("→", "←"), ("↑", "↓"))
    offsets = {"→": (5, 0), "←": (-5, 0), "↑": (0, -5), "↓": (0, 5)}
    for labels in cases:
        with control_page(browser, url, touch=True) as (page, run):
            touch = TouchContacts(page)
            delivered = touch.press(*labels)
            order = [e["label"] for e in delivered if e["type"] == "pointerdown"]
            run(1)
            if set(labels) in ({"→", "←"}, {"↑", "↓"}):
                dx, dy = offsets[order[-1]]
            else:
                dx = sum(offsets[label][0] for label in labels)
                dy = sum(offsets[label][1] for label in labels)
            assert ship_observation(page) == (60 + dx, 100 + dy, dx > 0)
            touch.release(order[-1])
            run(1)
            hx, hy = offsets[order[0]]
            assert ship_observation(page) == (60 + dx + hx, 100 + dy + hy, hx > 0)
            touch.release(order[0])
            run(1)
            assert ship_observation(page) == (60 + dx + hx, 100 + dy + hy, False)
            TOUCH_EVIDENCE.append({"case": "simultaneous", "delivered": order, "events": touch.events()})
    print("PASS simultaneous contacts combine axes or resolve opposites by the browser-delivered event order")


def touch_pause_clears_diagonal(browser, url):
    with control_page(browser, url, touch=True) as (page, run):
        touch = TouchContacts(page)
        touch.press("→", "↑")
        run(1)
        assert ship_observation(page) == (65, 95, True)
        page.get_by_role("button", name="Pausar", exact=True).click()
        run(3)
        assert ship_observation(page) == (65, 95, False)
        page.get_by_role("button", name="Continuar", exact=True).click()
        run(2)
        assert ship_observation(page) == (65, 95, False)
        touch.release("↑")
        touch.release("→")
        run(1)
        assert ship_observation(page) == (65, 95, False)
        touch.press("↓")
        run(1)
        assert ship_observation(page) == (65, 100, False)
        touch.release("↓")
        touch.press("→", "↑")
        run(1)
        page.get_by_role("button", name="Pausar", exact=True).click()
        page.get_by_role("button", name="Menu principal", exact=True).click()
        run(2)
        assert page.get_by_role("button", name="Novo Jogo", exact=True).count() == 1
        assert page.get_by_role("button", name="Pular créditos", exact=True).count() == 0
        page.get_by_role("button", name="Novo Jogo", exact=True).click()
        run(1)
        assert ship_observation(page) == (0, 100, False)
        touch.release("→")
        touch.release("↑")
        run(1)
        assert ship_observation(page) == (0, 100, False)
        TOUCH_EVIDENCE.append({"case": "pause", "events": touch.events()})
    print("PASS pause with two held fingers clears both axes; Continue and Main Menu keep held contacts from moving the resumed or new ship")


def cross_layout(browser, url):
    evidence = ROOT / ".agent/tmp/sifuture-controls"
    evidence.mkdir(parents=True, exist_ok=True)
    for width in (320, 1200):
        with control_page(browser, url, width=width) as (page, run):
            buttons = {label: page.get_by_role("button", name=label, exact=True)
                       for label in ("↑", "←", "→", "↓")}
            for button in buttons.values():
                box = button.bounding_box()
                assert (box["width"], box["height"]) == (56, 56), box
            for label in ("↖", "↗", "↙", "↘"):
                assert page.get_by_role("button", name=label, exact=True).count() == 0
            boxes = {label: button.bounding_box() for label, button in buttons.items()}
            north, west, east, south = (boxes[label] for label in ("↑", "←", "→", "↓"))
            assert north["x"] == south["x"] == west["x"] + 56 == east["x"] - 56
            assert west["y"] == east["y"] == north["y"] + 56 == south["y"] - 56
            assert south["y"] + 56 - north["y"] == east["x"] + 56 - west["x"] == 168
            for row, column in ((0, 0), (0, 2), (1, 1), (2, 0), (2, 2)):
                point = {"x": west["x"] + column * 56 + 28, "y": north["y"] + row * 56 + 28}
                assert page.evaluate("p => document.elementFromPoint(p.x, p.y).tagName", point) != "BUTTON"
            special = page.get_by_role("button", name="Especial", exact=True).bounding_box()
            assert (special["width"], special["height"]) == (56, 220)
            assert page.get_by_role("button", name="Especial", exact=True).evaluate("button => getComputedStyle(button).writingMode") == "vertical-rl"
            canvas = page.locator("canvas").bounding_box()
            assert (canvas["width"], canvas["height"]) == (176, 220)
            canvas_center = canvas["x"] + canvas["width"] / 2
            for label in ("↑", "↓"):
                arrow = boxes[label]
                assert abs(arrow["x"] + arrow["width"] / 2 - canvas_center) <= 1, (width, canvas, arrow)
            assert abs(special["x"] - canvas["x"] - canvas["width"] - 16) <= 1, (canvas, special)
            assert abs(special["y"] - canvas["y"]) <= 1, (canvas, special)
            assert abs(special["y"] + special["height"] - canvas["y"] - canvas["height"]) <= 1, (canvas, special)
            assert abs(special["x"] + special["width"] - canvas["x"] - 248) <= 1
            for box in (*boxes.values(), canvas, special):
                assert 0 <= box["x"] and box["x"] + box["width"] <= width, (width, box)
            assert canvas["y"] + canvas["height"] <= north["y"]
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            geometry = {"viewport": width, "canvas": canvas, "arrows": boxes, "special": special}
            (evidence / f"geometry-{width}.json").write_text(json.dumps(geometry, indent=2) + "\n")
            page.screenshot(path=str(evidence / f"cross-{width}.png"), full_page=True)
    print("PASS 320/1200: up/down aligned with 176x220 canvas; empty 168x168 cross; 56x220 vertical special aligned with canvas, 16px gap, 248px total, no horizontal scroll")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kof", help="Kof executable")
    args = parser.parse_args()
    with served_build(kof=args.kof, fixture=ROOT / "tests/controls.kf") as url:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path="/usr/bin/google-chrome", headless=False,
                args=["--no-sandbox", "--headless=new"]
            )
            try:
                touch_on_canvas_axis(browser, url)
                cross_layout(browser, url)
                touch_diagonals(browser, url)
                touch_opposites(browser, url)
                simultaneous_direction_events(browser, url)
                touch_pause_clears_diagonal(browser, url)
                keyboard_origin_and_release(browser, url)
                opposing_arrows(browser, url)
                tab_keeps_lost_release_blocked(browser, url)
                click_rearms_held_arrow(browser, url)
                click_rearms_after_external_release(browser, url)
                mouse_pad_exit_and_cancel(browser, url)
                pad_owns_movement(browser, url)
                touch_pad_drag_release_and_cancel(browser, url)
                touch_click_rearms_arrow(browser, url)
            finally:
                browser.close()
    (ROOT / ".agent/tmp/sifuture-controls/touch-events.json").write_text(json.dumps(TOUCH_EVIDENCE, indent=2) + "\n")
    print("PASS isolated keyboard, focus, pointer and touch controls in Chrome")


if __name__ == "__main__":
    main()
