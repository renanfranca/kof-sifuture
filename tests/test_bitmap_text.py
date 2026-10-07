import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CREDITS = ["Copyright (c) 2006-2007", "Renan Meneses de Andrade Franca", "contact:", "renan.andradefranca@gmail.com", "Inc. All rights reserved."]
MENUS = ["Novo Jogo", "Controles", "Continuar", "Reiniciar", "Menu principal"]


class BitmapTextAcceptance(unittest.TestCase):
    def test_final_size_glyphs_preserve_text_pixels_and_credit_width(self):
        data = json.loads((ROOT / "fonts/bitmap.json").read_text())
        for name, texts, color, size in (("menu", MENUS, (255, 255, 255), 14), ("credits", CREDITS, (0, 128, 255), 9)):
            font = data["fonts"][name]
            self.assertEqual(font["size"], size)
            self.assertEqual(font["color"], list(color))
            glyphs = {g["character"]: g for g in font["glyphs"]}
            for text in texts:
                width = sum(glyphs[c]["advance"] for c in text)
                self.assertLessEqual(width, 130 if name == "credits" else 128)
                for character in text:
                    g = glyphs[character]
                    image = Image.open(ROOT / "assets" / g["asset"]).convert("RGBA")
                    self.assertEqual(image.size, (len(g["mask"][0]), len(g["mask"])))
                    self.assertLessEqual(image.height, size)
                    for y, row in enumerate(g["mask"]):
                        for x, bit in enumerate(row):
                            self.assertEqual(image.getpixel((x, y)), (*color, 255) if bit == "#" else (0, 0, 0, 0))
                    self.assertGreaterEqual(g["advance"], image.width)
            for character in "@.abcdefghijklmnopqrstuvwxyz":
                if name == "credits":
                    self.assertIn(character, glyphs)
                    self.assertTrue(any("#" in row for row in glyphs[character]["mask"]))

    def test_generator_reproduces_assets_and_metrics_from_editable_masks(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, str(ROOT / "scripts/bitmap_font.py"), "--output", directory], check=True)
            generated = Path(directory)
            for path in (ROOT / "assets").glob("font-*.png"):
                self.assertEqual(path.read_bytes(), (generated / "assets" / path.name).read_bytes())
            self.assertEqual((ROOT / "src/main/kof/sifuture/BitmapFonts.kf").read_bytes(), (generated / "src/main/kof/sifuture/BitmapFonts.kf").read_bytes())


if __name__ == "__main__":
    unittest.main()
