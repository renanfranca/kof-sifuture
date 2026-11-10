import assert from 'node:assert/strict';
import { existsSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { test } from 'node:test';

import { aProject, runSensor, writeInto } from './project.mjs';

const manifest = '[project]\nname = "demo"\n\n[sources]\napp = "src/main/kof"\ntest = "src/test/kof"\n';
const calc = 'package demo\n\nInt add(Int a, Int b) {\n    return a + b\n}\n';

function aKofProject(files) {
  return aProject({ 'kof.toml': manifest, 'src/main/kof/demo/Calc.kf': calc, ...files });
}

function executedTests(report) {
  const totals = [...report.out.matchAll(/(\d+) failed of (\d+) tests/g)];
  assert.equal(totals.length, 1, report.out + report.err);
  return Number(totals[0][2]);
}

test('a new test file under src/test/kof runs without editing any list', () => {
  const root = aKofProject({
    'src/test/kof/demo/AddTest.kf': 'package demo\nimport demo.Calc\n\ntest "adds two numbers" {\n    assert(add(2, 3) == 5)\n}\n',
  });
  const before = runSensor('kof-tests.mjs', root, '--target', 'jvm');

  writeInto(root, 'src/test/kof/demo/more/ZeroTest.kf', 'package demo.more\nimport demo.Calc\n\ntest "adds zero" {\n    assert(add(7, 0) == 7)\n}\n');
  const after = runSensor('kof-tests.mjs', root, '--target', 'jvm');

  assert.equal(before.code, 0, before.out + before.err);
  assert.equal(executedTests(before), 1);
  assert.equal(after.code, 0, after.out + after.err);
  assert.equal(executedTests(after), 2);
});

function leftEntries(root) {
  const tests = path.join(root, 'src/test/kof');
  const build = path.join(root, 'build');
  return [
    ...readdirSync(tests).filter((name) => name.startsWith('KofTestsEntry')),
    ...(existsSync(build) ? readdirSync(build) : []),
  ];
}

test('a failing test fails the run, names the test and still removes the generated entry', () => {
  const root = aKofProject({
    'src/test/kof/demo/AddTest.kf': 'package demo\nimport demo.Calc\n\ntest "adds two numbers" {\n    assert(add(2, 3) == 5)\n}\n',
    'src/test/kof/demo/WrongTest.kf': 'package demo\nimport demo.Calc\n\ntest "expects a wrong sum" {\n    assert(add(2, 2) == 5)\n}\n',
  });

  const report = runSensor('kof-tests.mjs', root, '--target', 'jvm');

  assert.notEqual(report.code, 0, report.out + report.err);
  assert.match(report.out + report.err, /expects a wrong sum/);
  assert.deepEqual(leftEntries(root), []);
});

test('a test root without any Kof test fails with a clear message instead of passing', () => {
  const empty = aKofProject({ 'src/test/kof/README.txt': 'no tests yet\n' });
  const helpersOnly = aKofProject({
    'src/test/kof/demo/Scenarios.kf': 'package demo\nimport demo.Calc\n\nInt givenFive() {\n    return add(2, 3)\n}\n',
  });

  const reports = [empty, helpersOnly].map((root) => runSensor('kof-tests.mjs', root, '--target', 'jvm'));

  for (const report of reports) {
    assert.notEqual(report.code, 0, report.out + report.err);
    assert.match(report.err, /no Kof tests ran in src\/test\/kof/);
  }
});

test('a helper module without tests or main is shared by test files in other packages', () => {
  const root = aKofProject({
    'src/test/kof/demo/Scenarios.kf': 'package demo\nimport demo.Calc\n\nInt givenFive() {\n    return add(2, 3)\n}\n',
    'src/test/kof/demo/FiveTest.kf': 'package demo\nimport demo.Scenarios\n\ntest "five from the helper" {\n    assert(givenFive() == 5)\n}\n',
    'src/test/kof/demo/more/TenTest.kf': 'package demo.more\nimport demo.Calc\nimport demo.Scenarios\n\ntest "ten from the helper" {\n    assert(add(givenFive(), 5) == 10)\n}\n',
  });

  const report = runSensor('kof-tests.mjs', root, '--target', 'jvm');

  assert.equal(report.code, 0, report.out + report.err);
  assert.equal(executedTests(report), 2);
});

test('each run compiles the current production sources', () => {
  const root = aKofProject({
    'src/test/kof/demo/AddTest.kf': 'package demo\nimport demo.Calc\n\ntest "adds two numbers" {\n    assert(add(2, 3) == 5)\n}\n',
  });
  const green = runSensor('kof-tests.mjs', root, '--target', 'jvm');

  writeInto(root, 'src/main/kof/demo/Calc.kf', calc.replace('a + b', 'a - b'));
  const broken = runSensor('kof-tests.mjs', root, '--target', 'jvm');
  writeInto(root, 'src/main/kof/demo/Calc.kf', calc);
  const restored = runSensor('kof-tests.mjs', root, '--target', 'jvm');

  assert.equal(green.code, 0, green.out + green.err);
  assert.notEqual(broken.code, 0, broken.out + broken.err);
  assert.match(broken.out + broken.err, /adds two numbers/);
  assert.equal(restored.code, 0, restored.out + restored.err);
});

test('an entry left behind by an interrupted run is neither imported nor counted', () => {
  const root = aKofProject({
    'src/test/kof/demo/AddTest.kf': 'package demo\nimport demo.Calc\n\ntest "adds two numbers" {\n    assert(add(2, 3) == 5)\n}\n',
    'src/test/kof/KofTestsEntryInterrupted.kf': 'import demo.Missing\n',
  });

  const report = runSensor('kof-tests.mjs', root, '--target', 'jvm');

  assert.equal(report.code, 0, report.out + report.err);
  assert.equal(executedTests(report), 1);
});
