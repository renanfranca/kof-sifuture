"""WORKAROUND for the current Kof CLI's single source root discovery.

Prepare one manifest-free, disposable source tree for each compiler invocation.
The canonical application and test sources remain in separate project trees.
"""

import argparse
import contextlib
import json
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


def _source_walk_error(exc):
    raise exc


def _copy_sources(source, destination):
    if not source.is_dir():
        raise PreparationError(f"source directory is missing: {source}")
    try:
        paths = []
        for directory, _, names in os.walk(source, onerror=_source_walk_error):
            paths.extend(Path(directory) / name for name in names if name.endswith(".kf"))
        if not paths:
            raise PreparationError(f"no Kof sources in {source}")
    except OSError as exc:
        raise PreparationError(f"cannot read Kof sources: {exc}") from exc
    for path in sorted(paths):
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(path, target)
        except OSError as exc:
            raise PreparationError(f"cannot read Kof source {path}: {exc}") from exc


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


def _check_report(output, code):
    try:
        report = json.loads(output)
    except (ValueError, TypeError) as exc:
        raise PreparationError("Kof check returned invalid JSON") from exc
    if not isinstance(report, dict) or type(report.get("success")) is not bool:
        raise PreparationError("Kof check requires an object with boolean success")
    for name, minimum in (("filesChecked", 1), ("errorCount", 0)):
        value = report.get(name)
        if type(value) is not int or value < minimum or value > 2147483647:
            raise PreparationError(f"Kof check has invalid {name}")
    diagnostics = report.get("diagnostics")
    if not isinstance(diagnostics, list):
        raise PreparationError("Kof check requires diagnostics array")
    for item in diagnostics:
        if not isinstance(item, dict):
            raise PreparationError("Kof check has invalid diagnostic")
        for name in ("code", "file", "severity", "message"):
            if not isinstance(item.get(name), str):
                raise PreparationError(f"Kof check diagnostic has invalid {name}")
        if item["severity"] not in ("ERROR", "WARNING", "NOTE", "INFO"):
            raise PreparationError("Kof check diagnostic has invalid severity")
        for name in ("line", "column", "length"):
            if type(item.get(name)) is not int or item[name] < 0:
                raise PreparationError(f"Kof check diagnostic has invalid {name}")
    errors = sum(item["severity"] == "ERROR" for item in diagnostics)
    if errors != report["errorCount"]:
        raise PreparationError("Kof check errorCount contradicts diagnostics")
    if report["success"]:
        if code != 0 or errors:
            raise PreparationError("Kof check success contradicts exit or errors")
    elif code != 1 or errors == 0:
        raise PreparationError("Kof check rejection requires exit 1 and positive ERROR diagnostics")
    return report


def check(*, target="jvm", json_output=False, kof=None, root=ROOT):
    with prepared_sources(root=root) as source:
        try:
            result = subprocess.run([str(kof_executable(kof)), "check", str(source / "Main.kf"),
                                     "--target", target, "--json"], capture_output=True, text=True, check=False)
        except OSError as exc:
            raise PreparationError(f"cannot run Kof: {exc}") from exc
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        report = _check_report(result.stdout, result.returncode)
        if json_output:
            print(result.stdout, end="")
        else:
            for item in report["diagnostics"]:
                print(f'{item["file"]}:{item["line"]}:{item["column"]}: {item["severity"]} '
                      f'{item["code"]}: {item["message"]}')
            if report["success"]:
                print(f'checked {report["filesChecked"]} entry file(s), including resolved imports')
        return result.returncode


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
    for name in ("build", "test", "check"):
        sub = commands.add_parser(name)
        sub.add_argument("--kof", dest="sub_kof")
        if name == "build":
            sub.add_argument("--output", required=True)
        else:
            sub.add_argument("--target", choices=("jvm", "js"), default="jvm")
            if name == "test":
                sub.add_argument("--suite")
            else:
                sub.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            return build(args.output, kof=args.sub_kof or args.kof)
        if args.command == "check":
            return check(target=args.target, json_output=args.json, kof=args.sub_kof or args.kof)
        return test(target=args.target, suite=args.suite, kof=args.sub_kof or args.kof)
    except PreparationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
