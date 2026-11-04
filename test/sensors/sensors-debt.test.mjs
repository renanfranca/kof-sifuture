import assert from 'node:assert/strict';
import { test } from 'node:test';

import { aProject, assertKofChecks, git, runSensor } from './project.mjs';

const complex = `Bool old(Int a) {\n    return a > 0${' && a != 1'.repeat(10)}\n}\n`;

test('sensors debt reports findings in files nobody changed, summarised by rule and area, without failing', () => {
  const root = aProject({ 'src/main/kof/Old.kf': complex, 'src/test/kof/OldTest.kf': `test "silent" {\n    println(1)\n}\n` });
  git(root, 'commit', '-q', '-m', 'base');
  assertKofChecks(root, 'src/main/kof/Old.kf');

  const report = runSensor('sensors-debt.mjs', root);

  assert.equal(report.code, 0, report.err);
  assert.match(report.out, /^SENSORS DEBT \(report only, 2 Kof files\)/);
  assert.match(report.out, /src\/main\/kof\/Old\.kf:1:1 ERROR high-complexity/);
  assert.match(report.out, /\n {2}high-complexity +src\/main\/kof +1\n/);
  assert.match(report.out, /SENSOR dup: PASS \(0 findings\)/);
});
