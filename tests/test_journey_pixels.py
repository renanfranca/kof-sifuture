"""Behavior checks for comparing browser journey captures between runs."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

TOOL = Path(__file__).resolve().parents[1] / "scripts/journey_pixels.py"


class JourneyPixelsCompareTest(unittest.TestCase):
    def setUp(self):
        self.space = tempfile.TemporaryDirectory(prefix="sifuture-pixels-test-")
        self.addCleanup(self.space.cleanup)

    def run_with(self, name, captures):
        run = Path(self.space.name) / name
        for capture, (size, color) in captures.items():
            path = run / "png" / capture
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", size, color).save(path)
        return run

    def compare(self, *runs):
        return subprocess.run([sys.executable, str(TOOL), "compare", *map(str, runs)],
                              capture_output=True, text=True)

    def test_identical_runs_have_no_unstable_capture(self):
        captures = {"stage/hud.png": ((4, 3), "red"), "app.png": ((2, 2), "blue")}
        first = self.run_with("first", captures)
        second = self.run_with("second", captures)

        result = self.compare(first, second)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["runs=2 common=2 only_some=0 unstable=0"])

    def test_one_different_pixel_marks_that_capture_unstable(self):
        first = self.run_with("first", {"stage/hud.png": ((4, 3), "red"), "app.png": ((2, 2), "blue")})
        second = self.run_with("second", {"stage/hud.png": ((4, 3), "red"), "app.png": ((2, 2), "blue")})
        image = Image.open(second / "png/app.png")
        image.putpixel((1, 1), (0, 0, 254))
        image.save(second / "png/app.png")

        result = self.compare(first, second)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(),
                         ["runs=2 common=2 only_some=0 unstable=1", "unstable app.png"])

    def test_capture_missing_from_one_run_is_listed_as_only_some(self):
        first = self.run_with("first", {"stage/hud.png": ((4, 3), "red"), "app.png": ((2, 2), "blue")})
        second = self.run_with("second", {"stage/hud.png": ((4, 3), "red"), "app.png": ((2, 2), "blue")})
        third = self.run_with("third", {"stage/hud.png": ((4, 3), "red")})

        result = self.compare(first, second, third)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(),
                         ["runs=3 common=1 only_some=1 unstable=0", "only_some app.png"])

    def test_same_pixels_in_a_different_size_mark_the_capture_unstable(self):
        first = self.run_with("first", {"app.png": ((2, 3), "blue")})
        second = self.run_with("second", {"app.png": ((3, 2), "blue")})

        result = self.compare(first, second)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(),
                         ["runs=2 common=1 only_some=0 unstable=1", "unstable app.png"])
