import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import kof_project as project


class CheckBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.space = tempfile.TemporaryDirectory()
        self.addCleanup(self.space.cleanup)
        self.root = Path(self.space.name) / 'project'
        main = self.root / 'src/main/kof/sifuture'
        main.mkdir(parents=True)
        (main / 'Main.kf').write_text('package sifuture\nmain() { println(answer()) }\n')
        (main / 'Answer.kf').write_text('package sifuture\nInt answer() { return 42 }\n')
        self.originals = {p: p.read_bytes() for p in main.glob('*.kf')}

    def fake(self, payload, code):
        path = Path(self.space.name) / 'fake-kof'
        path.write_text('#!/usr/bin/env python3\nimport pathlib,sys\n'
                        f'pathlib.Path({str(Path(self.space.name) / "entry")!r}).write_text(sys.argv[2])\n'
                        f'print({payload!r})\nsys.exit({code})\n')
        path.chmod(0o755)
        return path

    def test_rejects_invalid_evidence_and_removes_temporary_sources(self):
        valid = dict(success=True, filesChecked=1, errorCount=0, diagnostics=[])
        cases = [('not json', 0), ('[]', 0)]
        for key, values in [('success', [1, 'true', None]), ('filesChecked', [0, -1, True, 1.0]),
                            ('errorCount', [-1, True, 0.0]), ('diagnostics', [None, {}, [True]])]:
            for value in values:
                cases.append((json.dumps({**valid, key: value}), 0))
        cases += [(json.dumps(valid), 2), (json.dumps({**valid, 'success': False}), 0),
                  (json.dumps({**valid, 'errorCount': 1}), 0)]
        for payload, code in cases:
            with self.subTest(payload=payload, code=code):
                with self.assertRaises(project.PreparationError):
                    project.check(root=self.root, kof=self.fake(payload, code), json_output=True)
                entry = Path((Path(self.space.name) / 'entry').read_text())
                self.assertFalse(entry.parent.exists())
                for path, original in self.originals.items():
                    self.assertEqual(path.read_bytes(), original)

    def test_preserves_diagnostics_and_checks_schema_and_counts(self):
        diagnostic = dict(code='SEM011', file='sifuture/Answer.kf', line=2, column=1,
                          length=1, severity='ERROR', message='Undefined variable')
        valid = dict(success=False, filesChecked=1, errorCount=1, diagnostics=[diagnostic])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(project.check(root=self.root, kof=self.fake(json.dumps(valid), 1), json_output=True), 1)
        self.assertEqual(json.loads(output.getvalue()), valid)
        for key, value in [('line', True), ('column', -1), ('length', '1'), ('severity', 'unknown'), ('message', None)]:
            payload = {**valid, 'diagnostics': [{**diagnostic, key: value}]}
            with self.subTest(key=key), self.assertRaises(project.PreparationError):
                project.check(root=self.root, kof=self.fake(json.dumps(payload), 1))
        with self.assertRaises(project.PreparationError):
            project.check(root=self.root, kof=self.fake(json.dumps({**valid, 'errorCount': 2}), 1))

    def test_check_cli_enforces_signed_32_bit_counter_bounds(self):
        wrapper = self.root / 'scripts/kof_project.py'
        wrapper.parent.mkdir()
        shutil.copy2(Path(project.__file__), wrapper)
        accepted = dict(success=True, filesChecked=2147483647, errorCount=0, diagnostics=[])
        fake = self.fake(json.dumps(accepted), 0)
        result = subprocess.run([sys.executable, str(wrapper), 'check', '--target', 'jvm', '--json', '--kof', str(fake)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), accepted)

        for key in ('filesChecked', 'errorCount'):
            report = {**accepted, key: 2147483648}
            fake = self.fake(json.dumps(report), 0)
            result = subprocess.run([sys.executable, str(wrapper), 'check', '--target', 'jvm', '--json', '--kof', str(fake)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f'invalid {key}', result.stderr)

    def test_check_cli_rejects_success_false_without_error_diagnostics(self):
        wrapper = self.root / 'scripts/kof_project.py'
        wrapper.parent.mkdir(exist_ok=True)
        shutil.copy2(Path(project.__file__), wrapper)
        rejected_without_errors = dict(success=False, filesChecked=1, errorCount=0, diagnostics=[])
        result = subprocess.run([sys.executable, str(wrapper), 'check', '--target', 'jvm', '--json',
                                 '--kof', str(self.fake(json.dumps(rejected_without_errors), 1))],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('positive ERROR diagnostics', result.stderr)

        diagnostic = dict(code='SEM011', file='Answer.kf', line=1, column=1,
                          length=1, severity='ERROR', message='Undefined variable')
        coherent = dict(success=False, filesChecked=1, errorCount=1, diagnostics=[diagnostic])
        result = subprocess.run([sys.executable, str(wrapper), 'check', '--target', 'jvm', '--json',
                                 '--kof', str(self.fake(json.dumps(coherent), 1))],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout), coherent)

    def test_preserves_all_official_non_error_severities(self):
        for severity in ['WARNING', 'NOTE', 'INFO']:
            data = dict(success=True, filesChecked=1, errorCount=0, diagnostics=[dict(
                code='probe', file='Answer.kf', line=0, column=0, length=0,
                severity=severity, message='original diagnostic')])
            output = io.StringIO()
            with self.subTest(severity=severity), contextlib.redirect_stdout(output):
                self.assertEqual(project.check(root=self.root, kof=self.fake(json.dumps(data), 0), json_output=True), 0)
            self.assertEqual(json.loads(output.getvalue()), data)

    def test_real_wrapper_import_error_restore_on_both_targets(self):
        (self.root / 'scripts').mkdir()
        shutil.copy2(Path(project.__file__), self.root / 'scripts/kof_project.py')
        for target in ['jvm', 'js']:
            def run():
                return subprocess.run([sys.executable, str(self.root / 'scripts/kof_project.py'), 'check',
                                       '--target', target, '--json'], capture_output=True, text=True)
            answer = self.root / 'src/main/kof/sifuture/Answer.kf'
            with self.subTest(target=target):
                good = run()
                self.assertEqual(good.returncode, 0, good.stderr + good.stdout)
                self.assertEqual(json.loads(good.stdout)['filesChecked'], 1)
                answer.write_text('package sifuture\nInt answer() { return missingSensorProbe }\n')
                bad = run()
                self.assertNotEqual(bad.returncode, 0)
                data = json.loads(bad.stdout)
                self.assertTrue(any(d['code'] == 'SEM011' and d['file'].endswith('Answer.kf')
                                    and 'missingSensorProbe' in d['message'] for d in data['diagnostics']), data)
                prepared = Path(data['diagnostics'][0]['file'])
                self.assertFalse(prepared.exists())
                answer.write_bytes(self.originals[answer])
                self.assertEqual(run().returncode, 0)

    def test_read_failure_cannot_approve_and_cleans_up(self):
        outside = Path(self.space.name) / 'temps'
        outside.mkdir()
        with patch.object(tempfile, 'tempdir', str(outside)):
            with patch.object(shutil, 'copyfile', side_effect=PermissionError('probe unreadable')):
                with self.assertRaises(project.PreparationError):
                    project.check(root=self.root, kof=self.fake('{}', 0))
        self.assertEqual(list(outside.iterdir()), [])
        source = self.root / 'src/main/kof'
        shutil.rmtree(source)
        with self.assertRaises(project.PreparationError):
            project.check(root=self.root, kof=self.fake('{}', 0))

    def test_os_denied_source_read_cannot_approve(self):
        path = self.root / 'src/main/kof/sifuture/Answer.kf'
        path.chmod(0)
        try:
            with self.assertRaises(project.PreparationError):
                project.check(root=self.root, kof=self.fake(json.dumps(dict(
                    success=True, filesChecked=1, errorCount=0, diagnostics=[])), 0))
            self.assertFalse((Path(self.space.name) / 'entry').exists())
        finally:
            path.chmod(0o644)
        self.assertEqual(path.read_bytes(), self.originals[path])


if __name__ == '__main__':
    unittest.main()
