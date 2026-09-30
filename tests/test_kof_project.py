"""Behavior checks for the temporary source-root WORKAROUND."""

import contextlib
import io
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import kof_project as project

KOF = "/home/renanfranca/projects/kof/bin/kof"


class KofProjectTest(unittest.TestCase):
    def setUp(self):
        self.space = tempfile.TemporaryDirectory(prefix="sifuture-project-test-")
        self.addCleanup(self.space.cleanup)
        self.root = Path(self.space.name) / "project"
        shutil.copytree(project.MAIN, self.root / "src/main/kof")
        shutil.copytree(project.TEST, self.root / "src/test/kof")
        shutil.copytree(project.ASSETS, self.root / "assets")
        (self.root / "kof.toml").write_text('[project]\nname = "sifuture"\n')

    def fake_kof(self, code=0, artifacts=False):
        path = Path(self.space.name) / "fake-kof"
        path.write_text("#!/usr/bin/env python3\n"
                        "import pathlib, sys\n"
                        f"code = {code}\n"
                        f"artifacts = {artifacts}\n"
                        "if artifacts and sys.argv[1] == 'build':\n"
                        "    out = pathlib.Path(sys.argv[sys.argv.index('--output') + 1])\n"
                        "    out.mkdir(parents=True, exist_ok=True)\n"
                        "    (out / 'index.html').write_text('new')\n"
                        "    (out / 'Default.mjs').write_text('new')\n"
                        "sys.exit(code)\n")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def test_prepared_sources_are_byte_copies_and_isolate_suite(self):
        suite = self.root / "src/test/kof/sifuture/game/GameJourney.kf"
        with project.prepared_sources(suite=suite, root=self.root) as source:
            self.assertFalse((source / "kof.toml").exists())
            self.assertEqual((source / "Main.kf").read_text(), "import sifuture.game.GameJourney\n")
            self.assertEqual((source / "sifuture/game/GameJourney.kf").read_bytes(), suite.read_bytes())
            for original in (self.root / "src/main/kof").rglob("*.kf"):
                self.assertEqual((source / original.relative_to(self.root / "src/main/kof")).read_bytes(), original.read_bytes())
            prepared = source
        self.assertFalse(prepared.exists())

    def test_real_cli_observes_source_update_and_suite_isolation(self):
        suite = self.root / "src/test/kof/sifuture/game/GameJourney.kf"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(project.test(kof=KOF, root=self.root), 0)
        failing = suite.parent / "Failure.kf"
        failing.write_text('package sifuture.game\nimport sifuture.game.*\ntest "deliberate failure" { assert(false) }\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(project.test(kof=KOF, root=self.root, suite="sifuture/game/GameJourney.kf"), 0)
            self.assertNotEqual(project.test(kof=KOF, root=self.root), 0)
        failing.unlink()
        rules = self.root / "src/main/kof/sifuture/game/Rules.kf"
        rules.write_text(rules.read_text().replace('SHIP_SPEED = 5', 'SHIP_SPEED = 4'))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertNotEqual(project.test(kof=KOF, root=self.root), 0)
        rules.write_text(rules.read_text().replace('SHIP_SPEED = 4', 'SHIP_SPEED = 5'))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(project.test(kof=KOF, root=self.root), 0)

    def test_rejects_missing_outside_and_empty_suite(self):
        for suite in ("missing.kf", "../outside.kf", "/tmp/outside.kf"):
            with self.assertRaises(project.PreparationError):
                project.test(kof=KOF, root=self.root, suite=suite)
        shutil.rmtree(self.root / "src/test/kof")
        with self.assertRaisesRegex(project.PreparationError, "no Kof suites"):
            project.test(kof=KOF, root=self.root)

    def test_rejects_ancestral_manifest_and_cleans_temp(self):
        with tempfile.TemporaryDirectory(dir=self.root) as inside:
            with patch.dict(os.environ, {"TMPDIR": inside}):
                tempfile.tempdir = None
                try:
                    with self.assertRaisesRegex(project.PreparationError, "TMPDIR"):
                        with project.prepared_sources(root=self.root):
                            pass
                    self.assertEqual(list(Path(inside).iterdir()), [])
                finally:
                    tempfile.tempdir = None

    def test_build_requires_fresh_artifacts_and_preserves_other_files(self):
        output = Path(self.space.name) / "web"
        output.mkdir()
        (output / "index.html").write_text("old")
        (output / "keep.txt").write_text("keep")
        with self.assertRaisesRegex(project.PreparationError, "required artifacts"):
            project.build(output, kof=self.fake_kof())
        self.assertEqual((output / "index.html").read_text(), "old")
        self.assertEqual(project.build(output, kof=self.fake_kof(artifacts=True)), 0)
        self.assertEqual((output / "index.html").read_text(), "new")
        self.assertEqual((output / "keep.txt").read_text(), "keep")
        self.assertEqual(project.build(output, kof=self.fake_kof(code=7, artifacts=True)), 7)

    def test_kof_precedence(self):
        with patch.dict(os.environ, {"KOF": "environment"}):
            self.assertEqual(project.kof_executable("argument"), "argument")
            self.assertEqual(project.kof_executable(), "environment")

    def test_first_suite_failure_code_is_retained(self):
        suites = self.root / "src/test/kof/sifuture/game"
        (suites / "A.kf").write_text('test "a" { assert(false) }\n')
        (suites / "B.kf").write_text('test "b" { assert(false) }\n')
        fake = Path(self.space.name) / "exit-by-suite"
        fake.write_text("#!/usr/bin/env python3\n"
                        "import pathlib, sys\n"
                        "source = pathlib.Path(sys.argv[2]).parent\n"
                        "if (source / 'sifuture/game/A.kf').exists(): sys.exit(7)\n"
                        "if (source / 'sifuture/game/B.kf').exists(): sys.exit(9)\n"
                        "sys.exit(0)\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(project.test(kof=fake, root=self.root), 7)

    def test_real_compile_failure_does_not_publish(self):
        main = self.root / "src/main/kof/sifuture/Main.kf"
        main.write_text(main.read_text() + "\ninvalid syntax @@@\n")
        output = Path(self.space.name) / "failed-web"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertNotEqual(project.build(output, kof=KOF, root=self.root), 0)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
