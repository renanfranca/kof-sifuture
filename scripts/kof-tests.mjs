import { spawnSync } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { readdirSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';

import { sensorArguments } from './sensor-arguments.mjs';

const TEST_ROOT = 'src/test/kof';
const ENTRY = 'KofTestsEntry';

function testModules(root) {
  return readdirSync(path.join(root, TEST_ROOT), { recursive: true })
    .filter((file) => file.endsWith('.kf') && !file.startsWith(ENTRY))
    .map((file) => file.slice(0, -'.kf'.length).split(path.sep).join('.'))
    .sort();
}

function entryPath(root) {
  return path.join(root, TEST_ROOT, `${ENTRY}${randomBytes(6).toString('hex')}.kf`);
}

function executedTests(output) {
  return [...output.matchAll(/\d+ failed of (\d+) tests/g)].reduce((total, match) => total + Number(match[1]), 0);
}

function noTests() {
  process.stderr.write(`kof-tests: no Kof tests ran in ${TEST_ROOT}\n`);
  return 1;
}

function runEntry(root, modules, target) {
  const entry = entryPath(root);
  try {
    writeFileSync(entry, modules.map((module) => `import ${module}\n`).join(''));
    const result = spawnSync(process.env.KOF ?? 'kof', ['test', entry, '--target', target], {
      cwd: root,
      encoding: 'utf8',
      stdio: ['inherit', 'pipe', 'pipe'],
      maxBuffer: 64 * 1024 * 1024,
    });
    process.stdout.write(result.stdout ?? '');
    process.stderr.write(result.stderr ?? '');
    return { status: result.status ?? 1, executed: executedTests(result.stdout ?? '') };
  } finally {
    rmSync(entry, { force: true });
  }
}

function runKofTests(root, target) {
  const modules = testModules(root);
  if (modules.length === 0) return noTests();

  const { status, executed } = runEntry(root, modules, target);
  if (executed === 0) return noTests();
  return status;
}

function targetOf(args) {
  const at = args.indexOf('--target');
  return at === -1 ? 'jvm' : args[at + 1];
}

const { root, paths } = sensorArguments();
process.exitCode = runKofTests(root, targetOf(paths));
