"""WORKAROUND for the current Kof CLI's single source root discovery.

Prepare one manifest-free, disposable source tree for each compiler invocation.
The canonical application and test sources remain in separate project trees.
"""

import argparse
import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "src/main/kof"
TEST = ROOT / "src/test/kof"
ASSETS = ROOT / "assets"


class PreparationError(RuntimeError):
    pass


def kof_executable(override=None):
    return override or os.environ.get("KOF") or shutil.which("kof") or "kof"


def _check_temporary_root(directory, project):
    directory = directory.resolve()
    project = project.resolve()
    if directory == project or project in directory.parents:
        raise PreparationError("temporary source is inside the project; set TMPDIR outside the project")
    if any((ancestor / "kof.toml").exists() for ancestor in (directory, *directory.parents)):
        raise PreparationError("temporary source has an ancestral kof.toml; set TMPDIR outside a Kof project")


def _copy_sources(source, destination):
    for path in sorted(source.rglob("*.kf")):
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


@contextlib.contextmanager
def prepared_sources(*, suite=None, fixture=None, model_only=False, root=ROOT):
    """Yield a fresh source tree; copy source bytes and write a root entry."""
    root = Path(root).resolve()
    with tempfile.TemporaryDirectory(prefix="sifuture-kof-") as name:
        source = Path(name) / "source"
        source.mkdir()
        _check_temporary_root(source, root)
        main = root / "src/main/kof"
        if model_only:
            _copy_sources(main / "sifuture/game", source / "sifuture/game")
        else:
            _copy_sources(main, source)
        if suite is not None:
            suite = Path(suite).resolve()
            tests = (root / "src/test/kof").resolve()
            if tests not in suite.parents or suite.suffix != ".kf" or not suite.is_file():
                raise PreparationError(f"suite must be an existing .kf file under {tests}: {suite}")
            relative = suite.relative_to(tests)
            target = source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(suite, target)
            entry = f"import {'.'.join(relative.with_suffix('').parts)}\n"
        elif fixture is not None:
            shutil.copyfile(fixture, source / "Main.kf")
            entry = None
        else:
            entry = "import sifuture.*\n"
        if entry is not None:
            (source / "Main.kf").write_text(entry)
        yield source


def _run(command):
    try:
        return subprocess.run(command, check=False).returncode
    except OSError as exc:
        raise PreparationError(f"cannot run Kof: {exc}") from exc


def _publish(source, output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.rglob("*")):
        if path.is_file():
            target = output / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def build(output, *, kof=None, root=ROOT, fixture=None, model_only=False, assets=None):
    """Compile into a fresh output and publish only after required files exist."""
    root = Path(root).resolve()
    with prepared_sources(fixture=fixture, model_only=model_only, root=root) as source:
        with tempfile.TemporaryDirectory(prefix="sifuture-output-") as name:
            web = Path(name) / "web"
            code = _run([str(kof_executable(kof)), "build", str(source), "--target", "js", "--output", str(web)])
            if code:
                return code
            missing = [item for item in ("index.html", "Default.mjs") if not (web / item).is_file()]
            if missing:
                raise PreparationError(f"Kof build returned success without required artifacts: {', '.join(missing)}")
            _publish(web, output)
            if assets is None:
                assets = (root / "assets").glob("*")
            destination = Path(output) / "assets"
            destination.mkdir(exist_ok=True)
            for asset in assets:
                shutil.copyfile(asset, destination / Path(asset).name)
            return 0


def test(*, target="jvm", suite=None, kof=None, root=ROOT):
    root = Path(root).resolve()
    tests = (root / "src/test/kof").resolve()
    if suite:
        selected = (tests / suite).resolve()
        if tests not in selected.parents or selected.suffix != ".kf" or not selected.is_file():
            raise PreparationError(f"suite must be an existing .kf file under {tests}: {suite}")
        suites = [selected]
    else:
        suites = sorted(tests.rglob("*.kf"))
    if not suites:
        raise PreparationError(f"no Kof suites in {tests}")
    first_failure = 0
    for path in suites:
        print(f"Suite: {path.relative_to(tests)}", flush=True)
        with prepared_sources(suite=path, root=root) as source:
            code = _run([str(kof_executable(kof)), "test", str(source / "Main.kf"), "--target", target])
            if code and not first_failure:
                first_failure = code
    return first_failure


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format, *_args):
        pass


@contextlib.contextmanager
def served_build(*, kof=None, fixture=None, model_only=False, assets=None):
    with tempfile.TemporaryDirectory(prefix="sifuture-browser-") as name:
        web = Path(name) / "web"
        code = build(web, kof=kof, fixture=fixture, model_only=model_only, assets=assets)
        if code:
            raise PreparationError(f"Kof build failed with exit status {code}")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(web)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}/"
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kof", help="Kof executable (also accepted after subcommand)")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "test"):
        sub = commands.add_parser(name)
        sub.add_argument("--kof", dest="sub_kof")
        if name == "build":
            sub.add_argument("--output", required=True)
        else:
            sub.add_argument("--target", choices=("jvm", "js"), default="jvm")
            sub.add_argument("--suite")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            return build(args.output, kof=args.sub_kof or args.kof)
        return test(target=args.target, suite=args.suite, kof=args.sub_kof or args.kof)
    except PreparationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
