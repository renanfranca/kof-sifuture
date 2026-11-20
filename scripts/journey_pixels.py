"""Capture browser journey screenshots and compare their pixels between runs."""

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".agent/tmp"


def journeys():
    return sorted(path for path in (ROOT / "tests").iterdir() if re.fullmatch(r"browser.*\.py", path.name))


def browser_version():
    sys.path.insert(0, str(ROOT / "tests"))
    from journey_browser import launch
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = launch(playwright)
        try:
            return browser.version
        finally:
            browser.close()


def capture(destination):
    destination = destination.resolve()
    if destination.exists():
        sys.exit(f"capture: {destination} already exists")
    destination.mkdir(parents=True)
    summary = [f"browser={browser_version()}"]
    started = time.time()
    failed = False
    for journey in journeys():
        with open(destination / f"{journey.stem}.log", "w") as log:
            code = subprocess.run([sys.executable, str(journey)], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        failed = failed or code != 0
        summary.append(f"{journey.relative_to(ROOT)} exit={code}")
    written = [path for path in EVIDENCE.rglob("*.png")
               if path.stat().st_mtime >= started and not path.is_relative_to(destination)]
    for path in written:
        copy = destination / "png" / path.relative_to(EVIDENCE)
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, copy)
    summary.append(f"png={len(written)}")
    (destination / "summary.txt").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))
    return 1 if failed else 0


def captures(run):
    png = Path(run) / "png"
    return {path.relative_to(png) for path in png.rglob("*.png")}


def pixels(run, name):
    with Image.open(Path(run) / "png" / name) as image:
        return image.size, image.convert("RGB").tobytes()


def compare(runs):
    names = [captures(run) for run in runs]
    common = set.intersection(*names)
    only_some = sorted(set.union(*names) - common)
    unstable = sorted(name for name in common if len({pixels(run, name) for run in runs}) > 1)
    print(f"runs={len(runs)} common={len(common)} only_some={len(only_some)} unstable={len(unstable)}")
    for name in only_some:
        print("only_some", name)
    for name in unstable:
        print("unstable", name)
    return 1 if unstable or only_some else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    captured = commands.add_parser("capture", help="run every browser journey and copy the screenshots it wrote")
    captured.add_argument("destination", type=Path)
    compared = commands.add_parser("compare", help="compare decoded RGB pixels between two or more runs")
    compared.add_argument("runs", nargs="+", type=Path)
    arguments = parser.parse_args(argv)
    if arguments.command == "capture":
        return capture(arguments.destination)
    if len(arguments.runs) < 2:
        parser.error("compare needs at least two runs")
    return compare(arguments.runs)


if __name__ == "__main__":
    sys.exit(main())
