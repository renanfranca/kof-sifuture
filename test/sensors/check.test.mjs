import assert from 'node:assert/strict';
import { chmodSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { test } from 'node:test';

import { aProject, git, runSensorWith, writeInto } from './project.mjs';

const nodeStub = (name) => `import { appendFileSync } from 'node:fs';\nappendFileSync('calls.log', '${name}\\n');\nprocess.exitCode = Number(process.env['FAIL_${name.replace(/\W/g, '_')}'] ?? 0);\n`;

const kofProjectStub = `import os, sys
step = 'kof_project ' + ' '.join(a for a in sys.argv[1:] if not a.startswith('--kof'))
open('calls.log', 'a').write(step + '\\n')
sys.exit(int(os.environ.get('FAIL_' + '_'.join(sys.argv[1:4:2]), '0')))
`;

const unittestStub = `import unittest
class Stub(unittest.TestCase):
    def test_logs(self):
        open('calls.log', 'a').write('unittest\\n')
`;

function aCheckedProject() {
  const root = aProject({
    'scripts/gitleaks-sensor.mjs': nodeStub('secret'),
    'scripts/lint-sensor.mjs': nodeStub('lint'),
    'scripts/dup-sensor.mjs': nodeStub('dup'),
    'scripts/docs-sensor.mjs': nodeStub('docs'),
    'scripts/kof_project.py': kofProjectStub,
    'tests/test_stub.py': unittestStub,
    'src/main/kof/Game.kf': 'main() {\n}\n',
    '.gitignore': 'calls.log\n__pycache__/\n',
  });
  git(root, 'commit', '-q', '-m', 'base');
  return root;
}

function calls(root) {
  return readFileSync(path.join(root, 'calls.log'), 'utf8').trim().split('\n');
}

test('check runs the cheap and expensive steps in order and skips mutation when no production Kof file changed', () => {
  const root = aCheckedProject();

  const report = runSensorWith(process.env, 'check.mjs', root);

  assert.equal(report.code, 0, report.out + report.err);
  assert.deepEqual(calls(root), [
    'secret',
    'kof_project check --target jvm --json',
    'kof_project check --target js --json',
    'unittest',
    'kof_project test --target jvm',
    'kof_project test --target js',
    'lint',
    'dup',
    'docs',
  ]);
  assert.match(report.out, /\n {2}mutation +SKIP \(no production Kof file changed against main\)\n/);
  assert.match(report.out, /\nCHECK: PASS\n$/);
});

function withKofMutStub(root) {
  const bin = path.join(root, 'stub-bin');
  writeInto(root, 'stub-bin/kof-mut', `#!/bin/sh\necho "kof-mut $*" >> "${path.join(root, 'calls.log')}"\nexit \${KOF_MUT_EXIT:-0}\n`);
  chmodSync(path.join(bin, 'kof-mut'), 0o755);
  return { ...process.env, PATH: `${bin}${path.delimiter}${process.env.PATH}` };
}

test('a red Kof test run stops check before lint, dup, docs and mutation, even with production changes', () => {
  const root = aCheckedProject();
  writeInto(root, 'src/main/kof/Game.kf', 'main() {\n    println(1)\n}\n');
  const env = { ...withKofMutStub(root), FAIL_test_jvm: '1' };

  const report = runSensorWith(env, 'check.mjs', root);

  assert.equal(report.code, 1);
  assert.equal(calls(root).at(-1), 'kof_project test --target jvm');
  assert.ok(!calls(root).some((call) => call.startsWith('kof-mut')), 'mutation must not run on a red baseline');
  for (const step of ['kof tests:js', 'lint:sensor', 'dup:sensor', 'docs:sensor', 'mutation']) {
    assert.match(report.out, new RegExp(`\\n  ${step} +NOT RUN \\(an earlier step failed\\)\\n`), step);
  }
  assert.match(report.out, /\nCHECK: FAIL at kof tests:jvm\n$/);
});

function withScopeEchoingKofMut(root) {
  const env = withKofMutStub(root);
  writeInto(
    root,
    'stub-bin/kof-mut',
    `#!/bin/sh\nlog="${path.join(root, 'calls.log')}"\necho "kof-mut $1" >> "$log"\nwhile [ $# -gt 0 ]; do\n  case "$1" in\n    --files) cat "$2" >> "$log"; echo >> "$log";;\n    --config) echo "config $2" >> "$log";;\n  esac\n  shift\ndone\nexit \${KOF_MUT_EXIT:-0}\n`,
  );
  return env;
}

test('mutation runs on changed production Kof files and its verdict decides check', () => {
  const root = aCheckedProject();
  writeInto(root, 'src/main/kof/Game.kf', 'main() {\n    println(1)\n}\n');
  writeInto(root, 'src/test/kof/GameTest.kf', 'test "t" {\n    assert(true)\n}\n');
  const env = withScopeEchoingKofMut(root);

  const survived = runSensorWith({ ...env, KOF_MUT_EXIT: '1' }, 'check.mjs', root);
  const survivedCalls = calls(root);
  const killed = runSensorWith({ ...env, KOF_MUT_EXIT: '0' }, 'check.mjs', root);
  const incomplete = runSensorWith({ ...env, KOF_MUT_EXIT: '3' }, 'check.mjs', root);

  assert.deepEqual(survivedCalls.slice(-3), ['kof-mut run', '["src/main/kof/Game.kf"]', 'config kof-mut.json']);
  assert.equal(survived.code, 1);
  assert.match(survived.out, /\n {2}mutation +FAIL \(KofMut exit 1: at least one mutant survived\)\n/);
  assert.equal(killed.code, 0, killed.out);
  assert.match(killed.out, /\n {2}mutation +PASS\n/);
  assert.equal(incomplete.code, 1);
  assert.match(incomplete.out, /\n {2}mutation +FAIL \(KofMut exit 3: incomplete, no_scope or no_mutants; quality not approved\)\n/);
});

const browserStub = (name) => `import os, sys\nopen('calls.log', 'a').write('${name}\\n')\nsys.exit(0)\n`;

test('check task adds every browser journey after check, and skips them when check fails', () => {
  const root = aCheckedProject();
  writeInto(root, 'tests/browser.py', browserStub('browser'));
  writeInto(root, 'tests/browser_meteor.py', browserStub('browser_meteor'));
  git(root, 'add', '-A');
  git(root, 'commit', '-q', '-m', 'journeys');

  const passing = runSensorWith(process.env, 'check-task.mjs', root);
  const passingCalls = calls(root);
  const failing = runSensorWith({ ...process.env, FAIL_lint: '1' }, 'check-task.mjs', root);

  assert.equal(passing.code, 0, passing.out + passing.err);
  assert.deepEqual(passingCalls.slice(-5), ['lint', 'dup', 'docs', 'browser', 'browser_meteor']);
  assert.match(passing.out, /\nCHECK:TASK: PASS\n$/);
  assert.equal(failing.code, 1);
  assert.match(failing.out, /\n {2}browser:browser_meteor +NOT RUN \(an earlier step failed\)\n/);
  assert.match(failing.out, /\nCHECK:TASK: FAIL at lint:sensor\n$/);
});

test('check reports a sensor that skipped as SKIP with its reason, not as PASS', () => {
  const root = aCheckedProject();
  writeInto(root, 'scripts/lint-sensor.mjs', `${nodeStub('lint')}process.stdout.write('SENSOR lint: SKIP (no Kof files changed against main)\\n');\n`);

  const report = runSensorWith(process.env, 'check.mjs', root);

  assert.equal(report.code, 0, report.out + report.err);
  assert.match(report.out, /\n {2}lint:sensor +SKIP \(no Kof files changed against main\)\n/);
  assert.match(report.out, /\n {2}dup:sensor +PASS\n/);
});
