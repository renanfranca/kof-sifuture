import assert from 'node:assert/strict';
import { test } from 'node:test';

import path from 'node:path';

import { aProject, runSensor, runSensorWith } from './project.mjs';

const healthy = JSON.stringify({ scripts: { 'docs:sensor': 'node scripts/docs-sensor.mjs' } });

test('sensors doctor lists every tool with its version and path, and says it is not a quality certificate', () => {
  const root = aProject({ 'package.json': healthy, 'scripts/docs-sensor.mjs': '' });

  const report = runSensor('sensors-doctor.mjs', root);

  assert.equal(report.code, 0, report.out + report.err);
  assert.match(report.out, /^SENSORS DOCTOR\n/);
  for (const tool of ['kof', 'kof-mut', 'node', 'mvn', 'java', 'gitleaks', 'python3']) {
    assert.match(report.out, new RegExp(`\\n {4}${tool} +\\S.* +/\\S+ +ok\\n`), tool);
  }
  assert.match(report.out, /\n {4}kof +kof \d+\.\d+\.\d+/);
  assert.match(report.out, /\n {4}kof-mut +KofMut \S+ image [0-9a-f]{12}/);
  assert.match(report.out, /\n {4}docs:sensor +scripts\/docs-sensor\.mjs +ok\n/);
  assert.match(report.out, /not a quality certificate/);
});

test('sensors doctor fails and names what is missing when a command file is gone or a tool is not on PATH', () => {
  const root = aProject({ 'package.json': JSON.stringify({ scripts: { 'lint:sensor': 'node scripts/lint-sensor.mjs' } }) });
  const toolsOnlyNode = { ...process.env, PATH: path.dirname(process.execPath) };

  const report = runSensorWith(toolsOnlyNode, 'sensors-doctor.mjs', root);

  assert.equal(report.code, 1, report.err);
  assert.match(report.out, /\n {4}lint:sensor +scripts\/lint-sensor\.mjs +MISSING\n/);
  assert.match(report.out, /\n {4}gitleaks +— +— +MISSING\n/);
  assert.match(report.out, /\n {4}node +v\d+\S* +\S+ +ok\n/);
});
