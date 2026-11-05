import assert from 'node:assert/strict';
import { test } from 'node:test';

import { aProject, assertKofChecks, git, runSensor, writeInto } from './project.mjs';

const cloned = `main() {
    var alpha = 101 + 102 + 103 + 104 + 105
    var beta = 201 + 202 + 203 + 204 + 205
    var gamma = 301 + 302 + 303 + 304 + 305
    var delta = 401 + 402 + 403 + 404 + 405
    println(alpha + beta + gamma + delta)
}
`;

test('dup sensor reports a fifty-token five-line clone between changed files, and passes once one copy is gone', () => {
  const root = aProject({ 'README.md': '# base\n' });
  git(root, 'commit', '-q', '-m', 'base');
  writeInto(root, 'src/main/kof/First.kf', cloned);
  writeInto(root, 'src/main/kof/Second.kf', cloned);
  ['First.kf', 'Second.kf'].forEach((name) => assertKofChecks(root, `src/main/kof/${name}`));

  const found = runSensor('dup-sensor.mjs', root);
  writeInto(root, 'src/main/kof/Second.kf', 'main() {\n    println(1)\n}\n');
  const gone = runSensor('dup-sensor.mjs', root);

  assert.equal(found.code, 1, found.err);
  assert.match(found.out, /^SENSOR dup: FAIL \(1 finding\)/);
  assert.match(found.out, /src\/main\/kof\/First\.kf:1 ERROR duplicated-code/);
  assert.match(found.out, /\d+ tokens over 7 lines duplicated at src\/main\/kof\/Second\.kf:1/);
  assert.match(found.out, /DUPLICATED-CODE\n {2}Duplicate Code\./);
  assert.match(found.out, /2 files expected, 2 tokenized/);
  assert.equal(gone.code, 0, gone.err);
  assert.match(gone.out, /^SENSOR dup: PASS \(0 findings\)\n {2}2 files expected, 2 tokenized\n$/);
});

test('dup sensor is unavailable, never passing, when a file in scope could not be tokenized', () => {
  const root = aProject({ 'README.md': '# base\n' });
  git(root, 'commit', '-q', '-m', 'base');
  writeInto(root, 'src/main/kof/Broken.kf', 'main() { println("unterminated }\n');

  const report = runSensor('dup-sensor.mjs', root);

  assert.equal(report.code, 1, report.err);
  assert.match(report.out, /^SENSOR dup: UNAVAILABLE\n/);
  assert.match(report.out, /1 files expected, 0 tokenized/);
  assert.match(report.out, /src\/main\/kof\/Broken\.kf/);
  assert.doesNotMatch(report.out, /PASS/);
});
