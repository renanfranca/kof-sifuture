import assert from 'node:assert/strict';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { test } from 'node:test';

import { changedThisSession, record } from '../../scripts/session-ledger.mjs';
import { stopAnswer } from '../../scripts/stop-response.mjs';
import { requestedScope, stopTiers, verdictFor } from '../../scripts/stop-verdict.mjs';
import { lastSeen } from '../../scripts/sensor-liveness.mjs';
import { aProject, fireHook, git, writeInto } from './project.mjs';

function committed(files) {
  const root = aProject(files);
  git(root, 'commit', '-q', '-m', 'base');
  return root;
}

test('the Stop scope is what the session recorded and is still changed', () => {
  const root = committed({ 'src/main/kof/A.kf': 'Int a() { return 1 }\n', 'src/main/kof/B.kf': 'Int b() { return 2 }\n' });
  record(root, 'mine', ['src/main/kof/A.kf', 'src/main/kof/B.kf']);
  writeInto(root, 'src/main/kof/A.kf', 'Int a() { return 3 }\n');

  assert.deepEqual(requestedScope(root, 'mine'), ['src/main/kof/A.kf']);
});

test('with nothing recorded, the Stop scope falls back to every change in the worktree', () => {
  const root = committed({ 'README.md': '# probe\n' });
  writeInto(root, 'src/main/kof/C.kf', 'Int c() { return 1 }\n');

  assert.deepEqual(requestedScope(root, 'empty'), ['src/main/kof/C.kf']);
});

test("another session's ledger does not change this session's scope", () => {
  const root = committed({ 'src/main/kof/A.kf': 'Int a() { return 1 }\n', 'src/main/kof/B.kf': 'Int b() { return 2 }\n' });
  record(root, 'session-a', ['src/main/kof/A.kf']);
  record(root, 'session-b', ['src/main/kof/B.kf']);
  writeInto(root, 'src/main/kof/A.kf', 'Int a() { return 3 }\n');
  writeInto(root, 'src/main/kof/B.kf', 'Int b() { return 4 }\n');

  assert.deepEqual(requestedScope(root, 'session-b'), ['src/main/kof/B.kf']);
});

function aRecordingStep(root, name, exitCode, seconds = 0) {
  const log = path.join(root, 'calls.log');
  const script = `require('node:fs').appendFileSync(${JSON.stringify(log)}, ${JSON.stringify(`${name}\n`)}); setTimeout(() => process.exit(${exitCode}), ${seconds * 1000});`;
  return { name, targets: (files) => files, program: process.execPath, args: () => ['-e', script] };
}

function calls(root) {
  try {
    return readFileSync(path.join(root, 'calls.log'), 'utf8').split('\n').filter(Boolean);
  } catch {
    return [];
  }
}

function recordingTiers(root, failing = '') {
  const step = (name) => aRecordingStep(root, name, name === failing ? 1 : 0);
  return { cheap: [step('cheap')], types: [step('types:jvm'), step('types:js')], tests: [step('tests:jvm'), step('tests:js')] };
}

function changedKof() {
  const root = committed({ 'src/main/kof/A.kf': 'Int a() { return 1 }\n' });
  writeInto(root, 'src/main/kof/A.kf', 'Int a() { return 2 }\n');
  return root;
}

test('a cheap failure stops the Stop before the types and the tests', () => {
  const root = changedKof();

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], recordingTiers(root, 'cheap'));

  assert.equal(verdict.passed, false);
  assert.deepEqual(calls(root), ['cheap']);
});

test('a type failure stops the Stop before the tests', () => {
  const root = changedKof();

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], recordingTiers(root, 'types:js'));

  assert.equal(verdict.passed, false);
  assert.deepEqual(calls(root), ['cheap', 'types:jvm', 'types:js']);
  assert.match(verdict.report, /STOP SENSORS: cheap PASS · types:jvm PASS · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN/);
});

test('when everything passes the Stop runs cheap, types and tests in that order', () => {
  const root = changedKof();

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], recordingTiers(root));

  assert.equal(verdict.passed, true);
  assert.deepEqual(calls(root), ['cheap', 'types:jvm', 'types:js', 'tests:jvm', 'tests:js']);
});

function slowTests(root) {
  return { ...recordingTiers(root), tests: [aRecordingStep(root, 'tests:jvm', 0, 2)] };
}

test('tests that outlast the budget fail the Stop with the time they were given', () => {
  const root = changedKof();

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], slowTests(root), { testBudgetMs: 1000 });

  assert.equal(verdict.passed, false);
  assert.match(verdict.report, /tests:jvm FAIL/);
  assert.match(verdict.report, /The Kof tests did not finish within 1s and were stopped\./);
});

test('the same tests within a wider budget pass', () => {
  const root = changedKof();

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], slowTests(root), { testBudgetMs: 5000 });

  assert.equal(verdict.passed, true, verdict.report);
});

function aPrintingStep(name, printed) {
  return { name, targets: (files) => files, program: process.execPath, args: () => ['-e', `console.log(${JSON.stringify(printed)}); process.exit(1)`] };
}

test('a failing verdict names each finding by rule and location', () => {
  const root = changedKof();
  const tiers = { ...recordingTiers(root), cheap: [aPrintingStep('lint', 'SENSOR lint: FAIL (1 finding)\n\nsrc/main/kof/A.kf:1:1 ERROR long-function\n  `a` has 26 lines; the limit is 25.')] };

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], tiers);

  assert.deepEqual(verdict.findings, [{ rule: 'long-function', where: 'src/main/kof/A.kf:1:1' }]);
});

test('a type error from the project check is a finding at its location', () => {
  const root = changedKof();
  const tiers = { ...recordingTiers(root), types: [aPrintingStep('types:jvm', 'src/main/kof/A.kf:2:9: ERROR TYPE001: cannot assign String to Int')] };

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], tiers);

  assert.deepEqual(verdict.findings, [{ rule: 'TYPE001', where: 'src/main/kof/A.kf:2:9' }]);
});

const failingOn = (where) => ({ passed: false, outcome: 'fail', report: `STOP SENSORS: lint FAIL\n\n${where} ERROR long-function`, findings: [{ rule: 'long-function', where }] });

test('the Stop pushes back once per set of findings and at most three times per session', () => {
  const root = committed({ 'README.md': '# probe\n' });
  const sequence = ['a.kf:1:1', 'a.kf:1:1', 'b.kf:1:1', 'c.kf:1:1', 'd.kf:1:1'].map(failingOn);

  const answers = sequence.map((verdict) => stopAnswer(root, { session_id: 'loop', stop_hook_active: false }, verdict));

  assert.deepEqual(answers.map((answer) => answer.decision ?? 'reported'), ['block', 'reported', 'block', 'block', 'reported']);
  assert.match(answers[4].systemMessage, /still have findings/);
  assert.match(answers[4].systemMessage, /d\.kf:1:1 ERROR long-function/);
});

test('a Stop that is already continuing after a push back only reports, even a new finding', () => {
  const root = committed({ 'README.md': '# probe\n' });

  const answer = stopAnswer(root, { session_id: 'active', stop_hook_active: true }, failingOn('a.kf:1:1'));

  assert.equal(answer.decision, undefined);
  assert.match(answer.systemMessage, /a\.kf:1:1 ERROR long-function/);
});

test('a passing Stop lets the turn end and says what it checked', () => {
  const root = committed({ 'README.md': '# probe\n' });
  const passing = { passed: true, outcome: 'pass', report: 'STOP SENSORS: lint PASS · types:jvm PASS', findings: [] };

  const answer = stopAnswer(root, { session_id: 'green' }, passing);

  assert.deepEqual(answer, { continue: true, systemMessage: 'STOP SENSORS: lint PASS · types:jvm PASS' });
});

const STOP = 'scripts/stop-sensor.mjs';

test('the Stop hook lets a session that changed nothing finish, says it skipped, and leaves its liveness mark', () => {
  const root = committed({ 'README.md': '# probe\n' });
  const before = Date.now();

  const answer = fireHook(STOP, root, { hook_event_name: 'Stop', session_id: 'idle', stop_hook_active: false });

  assert.equal(answer.code, 0, answer.err);
  assert.deepEqual(JSON.parse(answer.out), { continue: true, systemMessage: 'STOP SENSORS: SKIP (nothing changed in this session)' });
  assert.ok(lastSeen(root, 'Stop') >= before);
});

test('the Stop hook pushes back on a long function the session wrote, before any type check or test runs', () => {
  const root = committed({ 'README.md': '# probe\n' });
  const operands = Array.from({ length: 23 }, (_, i) => `        ${i + 1}${i < 22 ? ' +' : ''}\n`).join('');
  writeInto(root, 'src/main/kof/Probe.kf', `Int counted(Int a) {\n    return a +\n${operands}}\n`);
  record(root, 'writer', ['src/main/kof/Probe.kf']);

  const answer = fireHook(STOP, root, { hook_event_name: 'Stop', session_id: 'writer', stop_hook_active: false });

  const response = JSON.parse(answer.out);
  assert.equal(response.decision, 'block');
  assert.match(response.reason, /STOP SENSORS: lint FAIL · dup PASS · gitleaks PASS · types:jvm NOT RUN · types:js NOT RUN · tests:jvm NOT RUN · tests:js NOT RUN/);
  assert.match(response.reason, /src\/main\/kof\/Probe\.kf:1:1 ERROR long-function/);
});

test('SENSORS=git turns the Stop hook off and says so on stderr', () => {
  const root = committed({ 'README.md': '# probe\n' });
  writeInto(root, 'src/main/kof/Probe.kf', 'Int a() { return 1 }\n');

  const answer = fireHook(STOP, root, { hook_event_name: 'Stop', session_id: 'off' }, { SENSORS: 'git' });

  assert.equal(answer.code, 0);
  assert.equal(answer.out, '');
  assert.match(answer.err, /SENSORS=git/);
});

test('a session id that is not a safe file name stays inside the ledger and is not confused with another', () => {
  const root = committed({ 'README.md': '# probe\n' });

  record(root, '../../escaped', ['a.kf']);
  record(root, '/absolute/other', ['b.kf']);

  assert.equal(readdirSync(path.join(root, '.sensors', 'ledger')).length, 2);
  assert.deepEqual(readdirSync(root).sort(), ['.git', '.sensors', 'README.md']);
  assert.deepEqual(changedThisSession(root, '../../escaped'), ['a.kf']);
  assert.deepEqual(changedThisSession(root, '/absolute/other'), ['b.kf']);
});

test('the type tier runs the normal project check for each target, without an entry of its own', () => {
  const root = committed({ 'src/main/kof/sifuture/probe/Probe.kf': 'package sifuture.probe\n' });
  const changed = ['src/main/kof/sifuture/probe/Probe.kf', 'src/test/kof/sifuture/probe/ProbeJourney.kf'];

  const commands = stopTiers.types.map((step) => [step.name, step.program, ...step.args(changed, root).slice(1)]);

  assert.deepEqual(commands, [
    ['types:jvm', 'python3', 'check', '--target', 'jvm'],
    ['types:js', 'python3', 'check', '--target', 'js'],
  ]);
  assert.ok(stopTiers.types.every((step) => step.args(changed, root)[0].endsWith(path.join('scripts', 'kof_project.py'))));
  assert.equal(existsSync(path.join(root, '.sensors', 'ledger', 'types-entry.kf')), false);
});

test('a type error reported by file name alone is shown at the changed file it belongs to', () => {
  const root = changedKof();
  const tiers = { ...recordingTiers(root), types: [aPrintingStep('types:jvm', "Probe.kf:4:5: ERROR SEM021: type mismatch: cannot assign String to 'x: Int'")] };

  const verdict = verdictFor(root, ['src/main/kof/sifuture/probe/Probe.kf', 'src/main/kof/A.kf'], tiers);

  assert.match(verdict.report, /^src\/main\/kof\/sifuture\/probe\/Probe\.kf:4:5: ERROR SEM021/m);
  assert.deepEqual(verdict.findings, [{ rule: 'SEM021', where: 'src/main/kof/sifuture/probe/Probe.kf:4:5' }]);
});

test('the Stop hook keeps each verdict and answer in the session log, so a run that shows no message can still be read', () => {
  const root = committed({ 'README.md': '# probe\n' });

  fireHook(STOP, root, { hook_event_name: 'Stop', session_id: 'logged', stop_hook_active: false });

  const log = readFileSync(path.join(root, '.sensors', 'ledger', 'logged.stop.log'), 'utf8');
  assert.match(log, /^\d{4}-\d\d-\d\dT[\d:.]+Z stop_hook_active=false answer=continue\nSTOP SENSORS: SKIP \(nothing changed in this session\)\n/);
});

const suiteOutput = [
  'SUITE /tmp/x/src/test/kof/KofTestsEntry6df6f38122a1.kf (3 tests)',
  ...Array.from({ length: 300 }, (_, i) => `PASS passing case number ${i}`),
  'FAIL probe total sums the operands: assertion failed',
  '1 failed of 301 tests',
].join('\n');

test('a failing Kof test is named in the report and the passing ones are left out', () => {
  const root = changedKof();
  const tiers = { ...recordingTiers(root), tests: [aPrintingStep('tests:jvm', suiteOutput)] };

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], tiers);

  assert.match(verdict.report, /FAIL probe total sums the operands: assertion failed/);
  assert.match(verdict.report, /300 passing tests left out/);
  assert.doesNotMatch(verdict.report, /PASS passing case/);
  assert.ok(verdict.report.length < 2000, `report is ${verdict.report.length} characters`);
});

test('the same failing test on both targets is one finding named after the test', () => {
  const root = changedKof();
  const tiers = { ...recordingTiers(root), tests: [aPrintingStep('tests:jvm', suiteOutput), aPrintingStep('tests:js', suiteOutput.replace('6df6f38122a1', '5ce038e89fb5'))] };

  const verdict = verdictFor(root, ['src/main/kof/A.kf'], tiers);

  assert.deepEqual(verdict.findings, [{ rule: 'failing-test', where: 'probe total sums the operands' }]);
});
