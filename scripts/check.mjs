import { spawnSync } from 'node:child_process';

import { changedKofFiles } from './git-changes.mjs';
import { mutate } from './mutation-step.mjs';
import { sensorArguments } from './sensor-arguments.mjs';

const PRODUCTION = 'src/main/kof/';

const command = (name, program, args) => ({ name, run: (root) => spawned(root, program, args) });

export const checkSteps = [
  command('secret:sensor', 'node', ['scripts/gitleaks-sensor.mjs']),
  command('types:jvm', 'python3', ['scripts/kof_project.py', 'check', '--target', 'jvm', '--json']),
  command('types:js', 'python3', ['scripts/kof_project.py', 'check', '--target', 'js', '--json']),
  command('python tests', 'python3', ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py']),
  command('kof tests:jvm', 'python3', ['scripts/kof_project.py', 'test', '--target', 'jvm']),
  command('kof tests:js', 'python3', ['scripts/kof_project.py', 'test', '--target', 'js']),
  command('lint:sensor', 'node', ['scripts/lint-sensor.mjs']),
  command('dup:sensor', 'node', ['scripts/dup-sensor.mjs']),
  command('docs:sensor', 'node', ['scripts/docs-sensor.mjs']),
  { name: 'mutation', run: mutationStep },
];

const SKIPPED = /^SENSOR \S+: SKIP \((.*)\)$/m;

function spawned(root, program, args) {
  process.stdout.write(`\n> ${[program, ...args].join(' ')}\n`);
  const result = spawnSync(program, args, { cwd: root, encoding: 'utf8', stdio: ['inherit', 'pipe', 'inherit'], maxBuffer: 64 * 1024 * 1024 });
  process.stdout.write(result.stdout ?? '');
  if (result.status !== 0) return { state: 'FAIL', detail: `exit ${result.status ?? result.error?.code}` };

  const skipped = (result.stdout ?? '').match(SKIPPED);
  return skipped ? { state: 'SKIP', detail: skipped[1] } : { state: 'PASS' };
}

function mutationStep(root) {
  const changes = changedKofFiles(root);
  if (changes.unavailable) return { state: 'FAIL', detail: changes.unavailable.join(' ') };

  const scope = changes.files.filter((file) => file.startsWith(PRODUCTION));
  if (scope.length === 0) return { state: 'SKIP', detail: 'no production Kof file changed against main' };

  return mutate(root, scope);
}

export function runSteps(root, steps) {
  const results = [];
  for (const step of steps) {
    if (results.some((result) => result.state === 'FAIL')) {
      results.push({ name: step.name, state: 'NOT RUN', detail: 'an earlier step failed' });
      continue;
    }
    results.push({ name: step.name, ...step.run(root) });
  }
  return results;
}

export function summary(title, results) {
  const width = Math.max(...results.map((result) => result.name.length));
  const failed = results.find((result) => result.state === 'FAIL');
  const lines = results.map((result) => `  ${result.name.padEnd(width)}  ${result.state}${result.detail ? ` (${result.detail})` : ''}`);
  const verdict = failed ? `${title}: FAIL at ${failed.name}` : `${title}: PASS`;
  return { text: `\n${title} SUMMARY\n${lines.join('\n')}\n${verdict}\n`, failed: Boolean(failed) };
}

if (import.meta.main) {
  const { root } = sensorArguments();
  const { text, failed } = summary('CHECK', runSteps(root, checkSteps));
  process.stdout.write(text);
  process.exitCode = failed ? 1 : 0;
}
