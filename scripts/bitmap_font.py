import argparse
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def generate(output, source=ROOT / "fonts/bitmap.json"):
    data = json.loads(source.read_text())
    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    lines = ["package sifuture", "", "import kof.ui.*", "import sifuture.BitmapFont", "import sifuture.BitmapGlyph", "", "class BitmapFonts {"]
    for name, font in data["fonts"].items():
        lines.extend([f"    static {name}(): BitmapFont {{", "        return BitmapFont(listOf("])
        entries = []
        for g in font["glyphs"]:
            mask = g["mask"]
            image = Image.new("RGBA", (len(mask[0]), len(mask)))
            for y, row in enumerate(mask):
                for x, bit in enumerate(row):
                    if bit == "#":
                        image.putpixel((x, y), (*font["color"], 255))
            image.save(assets / g["asset"], optimize=False, compress_level=9)
            character = json.dumps(g["character"], ensure_ascii=False)
            entries.append(f'            BitmapGlyph({character}, Image("assets/{g["asset"]}"), {g["advance"]}, {g["left"]}, {g["top"]})')
        lines.append(",\n".join(entries) + "))")
        lines.extend(["    }", ""])
    lines.append("}")
    target = output / "src/main/kof/sifuture/BitmapFonts.kf"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT)
    parser.add_argument("--source", type=Path, default=ROOT / "fonts/bitmap.json")
    args = parser.parse_args()
    generate(args.output, args.source)
