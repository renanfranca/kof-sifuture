import assert from 'node:assert/strict';
import { chmodSync, existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { test } from 'node:test';

import { aProject, git, runSensorWith, writeInto } from './project.mjs';

const nodeStub = (name) => `import { appendFileSync } from 'node:fs';\nappendFileSync('calls.log', '${name}\\n');\nprocess.exitCode = Number(process.env['FAIL_${name.replace(/\W/g, '_')}'] ?? 0);\n`;

const kofProjectStub = `import os, sys
step = 'kof_project ' + ' '.join(a for a in sys.argv[1:] if not a.startswith('--kof'))
open('calls.log', 'a').write(step + '\\n')
fixture = sys.argv[sys.argv.index('--fixture') + 1] if '--fixture' in sys.argv else None
key = 'FAIL_fixture_' + os.path.basename(fixture)[:-3] if fixture else 'FAIL_' + '_'.join(sys.argv[1:4:2])
sys.exit(int(os.environ.get(key, '0')))
`;

const kofTestsStub = `import { appendFileSync } from 'node:fs';
const target = process.argv[process.argv.indexOf('--target') + 1];
appendFileSync('calls.log', \`kof-tests --target \${target}\\n\`);
process.exitCode = Number(process.env[\`FAIL_test_\${target}\`] ?? 0);
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
    'scripts/kof-tests.mjs': kofTestsStub,
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
    'kof-tests --target jvm',
    'kof-tests --target js',
    'lint',
    'dup',
    'docs',
  ]);
  assert.match(report.out, /\n {2}mutation +SKIP \(no production Kof file changed against main\)\n/);
  assert.match(report.out, /\nCHECK: PASS\n$/);
});

function withFixtures(root, ...names) {
  names.forEach((name) => writeInto(root, `tests/${name}`, 'main() {\n}\n'));
  git(root, 'add', '-A');
  git(root, 'commit', '-q', '-m', 'fixtures');
  return root;
}

test('check type-checks every browser fixture in name order after types:js and before the python tests', () => {
  const root = withFixtures(aCheckedProject(), 'b.kf', 'a.kf');

  const report = runSensorWith(process.env, 'check.mjs', root);

  assert.equal(report.code, 0, report.out + report.err);
  assert.deepEqual(calls(root).slice(1, 6), [
    'kof_project check --target jvm --json',
    'kof_project check --target js --json',
    'kof_project check --target js --json --fixture tests/a.kf',
    'kof_project check --target js --json --fixture tests/b.kf',
    'unittest',
  ]);
  assert.match(report.out, /\n {2}types:fixtures +PASS\n/);
  assert.match(report.out, /\nCHECK: PASS\n$/);
});

test('the first browser fixture that fails type checking stops check and names the fixture', () => {
  const root = withFixtures(aCheckedProject(), 'a.kf', 'b.kf');

  const report = runSensorWith({ ...process.env, FAIL_fixture_a: '1' }, 'check.mjs', root);

  assert.equal(report.code, 1);
  assert.equal(calls(root).at(-1), 'kof_project check --target js --json --fixture tests/a.kf');
  assert.match(report.out, /\n {2}types:fixtures +FAIL \(tests\/a\.kf: exit 1\)\n/);
  for (const step of ['python tests', 'kof tests:jvm', 'kof tests:js', 'lint:sensor', 'dup:sensor', 'docs:sensor', 'mutation']) {
    assert.match(report.out, new RegExp(`\\n  ${step} +NOT RUN \\(an earlier step failed\\)\\n`), step);
  }
  assert.match(report.out, /\nCHECK: FAIL at types:fixtures\n$/);
});

test('check without browser fixtures skips the fixture type check and goes on', () => {
  const root = aCheckedProject();

  const report = runSensorWith(process.env, 'check.mjs', root);

  assert.equal(report.code, 0, report.out + report.err);
  assert.ok(!calls(root).some((call) => call.includes('--fixture')));
  assert.match(report.out, /\n {2}types:fixtures +SKIP \(no browser fixture in tests\)\n/);
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
  assert.equal(calls(root).at(-1), 'kof-tests --target jvm');
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

  assert.deepEqual(survivedCalls.slice(-3), ['kof-mut run', '["src/main/kof/Game.kf"]', 'config kof-mut.json']);
  assert.equal(survived.code, 1);
  assert.match(survived.out, /\n {2}mutation +FAIL \(KofMut exit 1: at least one mutant survived\)\n/);
  assert.equal(killed.code, 0, killed.out);
  assert.match(killed.out, /\n {2}mutation +PASS\n/);
});

const reportingKofMut = `#!/usr/bin/env node
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const argument = (name) => process.argv[process.argv.indexOf(name) + 1];
const dir = path.join(argument('--report-dir'), 'run');
const file = path.join(dir, 'report.json');
const received = {
  runId: argument('--run-id'),
  scope: [...new Set(JSON.parse(readFileSync(argument('--files'), 'utf8')))].sort(),
  discardedCandidates: [],
};

function reportText(text) {
  try {
    const report = { ...received, ...JSON.parse(text) };
    for (const field of (process.env.KOF_MUT_OMIT ?? '').split(',')) delete report[field];
    return JSON.stringify(report);
  } catch {
    return text;
  }
}

mkdirSync(dir, { recursive: true });
writeFileSync(file, reportText(process.env.KOF_MUT_REPORT ?? '{}'));
const announce = (announced) => process.stdout.write(\`reportPath=\${JSON.stringify(announced)}\\n\`);
const announcements = {
  once: () => announce(file),
  twice: () => { announce(file); announce(file); },
  missing: () => announce(path.join(dir, 'absent.json')),
  relative: () => announce(path.relative(process.env.KOF_MUT_RELATIVE_FROM, file)),
  none: () => {},
};
announcements[process.env.KOF_MUT_ANNOUNCE ?? 'once']();
process.exitCode = Number(process.env.KOF_MUT_EXIT ?? 0);
`;

function withReportingKofMut(root) {
  const env = withKofMutStub(root);
  writeInto(root, 'stub-bin/kof-mut', reportingKofMut);
  return env;
}

function checkWithKofMutReport(report, overrides = {}, production = { 'src/main/kof/Game.kf': 'main() {\n    println(1)\n}\n' }) {
  const root = aCheckedProject();
  Object.entries(production).forEach(([name, content]) => writeInto(root, name, content));
  const env = { ...withReportingKofMut(root), KOF_MUT_EXIT: '3', KOF_MUT_REPORT: JSON.stringify(report), ...overrides };
  return runSensorWith(env, 'check.mjs', root);
}

test('KofMut no_mutants without limitations skips mutation without failing check', () => {
  const report = checkWithKofMutReport({ status: 'no_mutants', limitations: [] });

  assert.match(report.out, /\n {2}mutation +SKIP \(KofMut no_mutants: no applicable mutants\)\n/);
  assert.match(report.out, /\nCHECK: PASS\n$/);
  assert.equal(report.code, 0);
});

test('KofMut no_mutants from discarded candidates still skips mutation and shows how many were discarded', () => {
  const discarded = [{ id: 'a' }, { id: 'b' }, { id: 'c' }];

  const report = checkWithKofMutReport({ status: 'no_mutants', limitations: [], discardedCandidates: discarded });

  assert.match(report.out, /\n {2}mutation +SKIP \(KofMut no_mutants: no applicable mutants, 3 discarded\)\n/);
  assert.match(report.out, /\nCHECK: PASS\n$/);
  assert.equal(report.code, 0);
});

test('a KofMut report from another run never skips mutation', () => {
  const report = checkWithKofMutReport({ status: 'no_mutants', limitations: [], runId: '6f1c2a54-0b8e-4c1e-9d3a-2b7e5f4a9c10' });

  assert.match(report.out, /\n {2}mutation +FAIL \(KofMut exit 3 report is not from this run: runId [^\n]+; quality not approved\)\n/);
  assert.match(report.out, /\nCHECK: FAIL at mutation\n$/);
  assert.equal(report.code, 1);
});

test('a KofMut report skips mutation only when its scope is the requested sorted scope', () => {
  const twoFiles = { 'src/main/kof/A.kf': 'main() {\n}\n', 'src/main/kof/B.kf': 'main() {\n}\n' };
  const reportWithScope = (scope) => checkWithKofMutReport({ status: 'no_mutants', limitations: [], scope }, {}, twoFiles);

  const sorted = reportWithScope(['src/main/kof/A.kf', 'src/main/kof/B.kf']);
  const missingOne = reportWithScope(['src/main/kof/A.kf']);
  const empty = reportWithScope([]);

  assert.match(sorted.out, /\n {2}mutation +SKIP \(KofMut no_mutants: no applicable mutants\)\n/);
  assert.equal(sorted.code, 0);
  for (const [name, report] of Object.entries({ missingOne, empty })) {
    assert.match(report.out, /\n {2}mutation +FAIL \(KofMut exit 3 report is not from this run: scope [^\n]+; quality not approved\)\n/, name);
    assert.equal(report.code, 1, name);
  }
});

test('a relative reportPath fails mutation as unreadable even when the file exists there', () => {
  const report = checkWithKofMutReport({ status: 'no_mutants', limitations: [] }, { KOF_MUT_ANNOUNCE: 'relative', KOF_MUT_RELATIVE_FROM: process.cwd() });

  const announced = JSON.parse(report.out.match(/^reportPath=(.+)$/m)[1]);
  assert.ok(!path.isAbsolute(announced), announced);
  assert.ok(existsSync(announced), announced);
  assert.match(report.out, /\n {2}mutation +FAIL \(KofMut exit 3 report unreadable: reportPath is not absolute; quality not approved\)\n/);
  assert.equal(report.code, 1);
});

test('KofMut incomplete still fails check and shows its limitation', () => {
  const limitation = 'src/main/kof/Game.kf: Unsupported AST node: X';

  const report = checkWithKofMutReport({ status: 'incomplete', limitations: [limitation] });

  assert.match(report.out, /\n {2}mutation +FAIL \(KofMut incomplete: src\/main\/kof\/Game\.kf: Unsupported AST node: X; quality not approved\)\n/);
  assert.match(report.out, /\nCHECK: FAIL at mutation\n$/);
  assert.equal(report.code, 1);
});

test('KofMut no_scope still fails check even without limitations', () => {
  const report = checkWithKofMutReport({ status: 'no_scope', limitations: [] });

  assert.match(report.out, /\n {2}mutation +FAIL \(KofMut no_scope; quality not approved\)\n/);
  assert.equal(report.code, 1);
});

test('a KofMut report that contradicts exit 3 never skips mutation', () => {
  const limited = checkWithKofMutReport({ status: 'no_mutants', limitations: ['src/main/kof/Game.kf: Unsupported AST node: X'] });
  const complete = checkWithKofMutReport({ status: 'complete', limitations: [] });

  assert.match(limited.out, /\n {2}mutation +FAIL \(KofMut exit 3 contradicts report: no_mutants with limitations; quality not approved\)\n/);
  assert.equal(limited.code, 1);
  assert.match(complete.out, /\n {2}mutation +FAIL \(KofMut exit 3 contradicts report: complete; quality not approved\)\n/);
  assert.equal(complete.code, 1);
});

test('an unusable KofMut report on exit 3 fails mutation as unreadable, never as SKIP', () => {
  const noMutants = { status: 'no_mutants', limitations: [] };
  const cases = {
    'no reportPath line': checkWithKofMutReport(noMutants, { KOF_MUT_ANNOUNCE: 'none' }),
    'two reportPath lines': checkWithKofMutReport(noMutants, { KOF_MUT_ANNOUNCE: 'twice' }),
    'announced path missing': checkWithKofMutReport(noMutants, { KOF_MUT_ANNOUNCE: 'missing' }),
    'invalid JSON': checkWithKofMutReport(noMutants, { KOF_MUT_REPORT: '{"status":' }),
    'limitations not an array': checkWithKofMutReport({ status: 'no_mutants' }),
    'discardedCandidates missing': checkWithKofMutReport(noMutants, { KOF_MUT_OMIT: 'discardedCandidates' }),
    'discardedCandidates not an array': checkWithKofMutReport({ ...noMutants, discardedCandidates: 'none' }),
  };

  for (const [name, report] of Object.entries(cases)) {
    assert.match(report.out, /\n {2}mutation +FAIL \(KofMut exit 3 report unreadable: [^\n]+; quality not approved\)\n/, name);
    assert.equal(report.code, 1, name);
  }
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
