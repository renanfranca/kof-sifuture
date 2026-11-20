"""Behavior checks for the browser every journey opens."""

import unittest

from playwright.sync_api import sync_playwright

from journey_browser import launch

DRAW = "() => Array.from(crypto.getRandomValues(new Uint8Array(16)))"


class JourneyBrowserTest(unittest.TestCase):
    def test_every_page_draws_the_same_random_sequence(self):
        with sync_playwright() as playwright:
            browser = launch(playwright)
            try:
                first = browser.new_page()
                first.goto("about:blank")
                second = browser.new_context().new_page()
                second.goto("about:blank")

                drawn = [first.evaluate(DRAW), second.evaluate(DRAW)]

                self.assertEqual(drawn[0], drawn[1])
                self.assertNotEqual(drawn[0], [0] * 16)
            finally:
                browser.close()
