import assert from 'node:assert/strict';
import { test } from 'node:test';

import { aProject, runSensor, writeInto } from './project.mjs';

const scripts = JSON.stringify({ private: true, type: 'module', scripts: { check: 'node check.mjs' } });

test('docs sensor reports a relative link to a missing file with its location and guide', () => {
  const root = aProject({ 'package.json': scripts, 'README.md': '# Title\n\nSee [the guide](docs/missing.md).\n' });

  const report = runSensor('docs-sensor.mjs', root);

  assert.equal(report.code, 1);
  assert.match(report.out, /^SENSOR docs: FAIL \(1 finding\)/);
  assert.match(report.out, /README\.md:3 ERROR broken-link/);
  assert.match(report.out, /Links to `docs\/missing\.md`, which does not exist\./);
  assert.match(report.out, /STALE-DOC/);
});

test('docs sensor reports a documented npm script that package.json lacks, and passes once it exists', () => {
  const readme = '# Title\n\n```bash\nnpm run lint:sensor\n```\n';
  const root = aProject({ 'package.json': scripts, 'README.md': readme });

  const missing = runSensor('docs-sensor.mjs', root);
  writeInto(root, 'package.json', JSON.stringify({ scripts: { 'lint:sensor': 'node lint.mjs' } }));
  const fixed = runSensor('docs-sensor.mjs', root);

  assert.equal(missing.code, 1);
  assert.match(missing.out, /README\.md:4 ERROR missing-script/);
  assert.match(missing.out, /`npm run lint:sensor` is documented, but package.json has no "lint:sensor" script\./);
  assert.equal(fixed.code, 0);
  assert.equal(fixed.out, 'SENSOR docs: PASS (0 findings)\n');
});

test('docs sensor resolves a file:line link to its file, so only the link to a missing file is reported', () => {
  const readme = '# Title\n\n[rule](src/Game.kf:2) and [range](src/Game.kf:1-2) and [gone](src/Gone.kf:7)\n';
  const root = aProject({ 'package.json': scripts, 'README.md': readme, 'src/Game.kf': 'main() {\n}\n' });

  const report = runSensor('docs-sensor.mjs', root);

  assert.equal(report.code, 1);
  assert.match(report.out, /^SENSOR docs: FAIL \(1 finding\)/);
  assert.match(report.out, /Links to `src\/Gone\.kf:7`, which does not exist\./);
});
