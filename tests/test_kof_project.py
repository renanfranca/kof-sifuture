"""Behavior checks for the temporary source-root WORKAROUND."""

import contextlib
import io
import json
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


class KofProjectTest(unittest.TestCase):
    def setUp(self):
        self.space = tempfile.TemporaryDirectory(prefix="sifuture-project-test-")
        self.addCleanup(self.space.cleanup)
        self.root = Path(self.space.name) / "project"
        shutil.copytree(project.MAIN, self.root / "src/main/kof")
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

    def test_prepared_sources_are_byte_copies_without_manifest(self):
        with project.prepared_sources(root=self.root) as source:
            self.assertFalse((source / "kof.toml").exists())
            self.assertEqual((source / "Main.kf").read_text(), "import sifuture.*\n")
            for original in (self.root / "src/main/kof").rglob("*.kf"):
                self.assertEqual((source / original.relative_to(self.root / "src/main/kof")).read_bytes(), original.read_bytes())
            prepared = source
        self.assertFalse(prepared.exists())

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
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("KOF", None)
            self.assertEqual(project.kof_executable(), shutil.which("kof"))

    def test_real_compile_failure_does_not_publish(self):
        main = self.root / "src/main/kof/sifuture/Main.kf"
        main.write_text(main.read_text() + "\ninvalid syntax @@@\n")
        output = Path(self.space.name) / "failed-web"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertNotEqual(project.build(output, root=self.root), 0)
        self.assertFalse(output.exists())

    def test_fixture_check_reports_import_missing_only_from_the_fixture_entry(self):
        fixture = Path(self.space.name) / "guide.kf"
        fixture.write_text("import sifuture.ControlsGuide\nimport kof.ui.*\n\n"
                           "main() {\n    var guide = ControlsGuide()\n    println(guide.discardClick)\n}\n")
        guide = self.root / "src/main/kof/sifuture/ControlsGuide.kf"
        guide.write_text(guide.read_text().replace("import sifuture.GuideDisclosure\n", ""))

        with contextlib.redirect_stdout(io.StringIO()) as fixture_output:
            fixture_code = project.check(target="js", json_output=True, root=self.root, fixture=fixture)
        with contextlib.redirect_stdout(io.StringIO()):
            wildcard_code = project.check(target="js", json_output=True, root=self.root)

        self.assertNotEqual(fixture_code, 0)
        errors = [item for item in json.loads(fixture_output.getvalue())["diagnostics"] if item["severity"] == "ERROR"]
        self.assertTrue(any("GuideDisclosure" in item["message"] for item in errors))
        self.assertEqual(wildcard_code, 0)

    def test_fixture_check_accepts_a_browser_fixture_of_the_complete_game(self):
        fixture = Path(self.space.name) / "boss.kf"
        shutil.copyfile(project.ROOT / "tests/boss.kf", fixture)

        with contextlib.redirect_stdout(io.StringIO()):
            code = project.check(target="js", json_output=True, root=self.root, fixture=fixture)

        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
