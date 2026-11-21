import { spawnSync } from 'node:child_process';
import { existsSync, statSync } from 'node:fs';
import path from 'node:path';

import { repositoryRoot } from './sensor-arguments.mjs';

const isKof = (file) => file.endsWith('.kf');

const sensorScript = (name) => path.join(repositoryRoot, 'scripts', name);

export const cheapSensors = [
  { name: 'lint', targets: (files) => files.filter(isKof), program: process.execPath, args: (targets, root) => [sensorScript('lint-sensor.mjs'), '--root', root, ...targets] },
  { name: 'dup', targets: (files) => files.filter(isKof), program: process.execPath, args: (targets, root) => [sensorScript('dup-sensor.mjs'), '--root', root, ...targets] },
  { name: 'gitleaks', targets: (files) => files, program: process.execPath, args: (targets, root) => [sensorScript('gitleaks-sensor.mjs'), '--root', root, ...targets] },
];

function present(root, file) {
  const full = path.resolve(root, file);
  const relative = path.relative(root, full);
  if (relative === '' || relative.startsWith('..') || path.isAbsolute(relative)) return null;

  return existsSync(full) && statSync(full).isFile() ? relative : null;
}

export function scopedFiles(root, files) {
  return [...new Set(files.map((file) => present(root, file)).filter(Boolean))];
}

export function runStep(root, step, targets, timeout) {
  const result = spawnSync(step.program, step.args(targets, root), {
    cwd: root,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
    timeout,
  });
  const output = `${result.stdout ?? ''}${result.stderr ?? ''}`.trim();
  const timedOut = result.error?.code === 'ETIMEDOUT';

  return { name: step.name, status: result.status === 0 && !result.error ? 'PASS' : 'FAIL', output, timedOut };
}

function fire(root, sensor, files) {
  const targets = sensor.targets(files);
  if (targets.length === 0) return { name: sensor.name, status: 'SKIP', output: '' };

  return runStep(root, sensor, targets);
}

export function rollCall(title, results) {
  return `${title}: ${results.map((result) => `${result.name} ${result.status}`).join(' · ')}`;
}

export function inspect(root, files, sensors = cheapSensors) {
  const scoped = scopedFiles(root, files);
  if (scoped.length === 0) return null;

  const results = sensors.map((sensor) => fire(root, sensor, scoped));
  const failures = results.filter((result) => result.status === 'FAIL');
  const report = [rollCall('EDIT SENSORS', results), '', ...failures.map((failure) => failure.output)].join('\n');

  return { passed: failures.length === 0, files: scoped, report };
}
