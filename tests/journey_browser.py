"""The browser every journey opens, so rendering options live in one place.

Kof's `random.int` draws from `crypto.getRandomValues` in the browser, so every
page gets the same seeded sequence and the same game unfolds in every run.
"""

SEEDED_RANDOM = """
(() => {
    let state = 0x5eed;
    const next = () => {
        state = (state + 0x6d2b79f5) | 0;
        let t = Math.imul(state ^ (state >>> 15), state | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return (t ^ (t >>> 14)) >>> 0;
    };
    crypto.getRandomValues = (array) => {
        const bytes = new Uint8Array(array.buffer, array.byteOffset, array.byteLength);
        for (let index = 0; index < bytes.length; index++) bytes[index] = next() & 255;
        return array;
    };
})();
"""


class SeededBrowser:
    def __init__(self, browser):
        self._browser = browser

    def __getattr__(self, name):
        return getattr(self._browser, name)

    def new_context(self, **options):
        context = self._browser.new_context(**options)
        context.add_init_script(SEEDED_RANDOM)
        return context

    def new_page(self, **options):
        page = self._browser.new_page(**options)
        page.add_init_script(SEEDED_RANDOM)
        return page


def launch(playwright):
    return SeededBrowser(playwright.chromium.launch(channel="chromium", args=["--no-sandbox", "--disable-partial-raster"]))
