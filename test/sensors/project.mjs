import { spawnSync } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

export const repositoryRoot = path.resolve(import.meta.dirname, '..', '..');

export function aProject(files) {
  const root = mkdtempSync(path.join(tmpdir(), 'sifuture-sensor-'));
  Object.entries(files).forEach(([name, content]) => writeInto(root, name, content));
  git(root, 'init', '-q', '-b', 'main');
  git(root, 'add', '-A');
  return root;
}

export function writeInto(root, name, content) {
  const file = path.join(root, name);
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, content);
}

export function git(root, ...args) {
  return spawnSync('git', ['-c', 'user.email=probe@example.invalid', '-c', 'user.name=probe', ...args], {
    cwd: root,
    encoding: 'utf8',
  });
}

export function runSensor(script, root, ...args) {
  return runSensorWith(process.env, script, root, ...args);
}

export function runSensorWith(env, script, root, ...args) {
  const result = spawnSync(process.execPath, [path.join(repositoryRoot, 'scripts', script), '--root', root, ...args], {
    encoding: 'utf8',
    env,
  });
  return { code: result.status, out: result.stdout, err: result.stderr };
}

export function syntheticToken() {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const body = [...randomBytes(36)].map((byte) => alphabet[byte % alphabet.length]).join('');
  return ['gh', 'p_', body].join('');
}

export function fireHook(script, root, payload, env = {}) {
  const result = spawnSync(process.execPath, [path.join(repositoryRoot, script), '--root', root], {
    encoding: 'utf8',
    input: JSON.stringify(payload),
    env: { ...process.env, ...env },
  });
  return { code: result.status, out: result.stdout, err: result.stderr };
}

export function assertKofChecks(root, name) {
  for (const target of ['jvm', 'js']) {
    const checked = spawnSync(process.env.KOF ?? 'kof', ['check', path.join(root, name), '--target', target], { encoding: 'utf8' });
    if (checked.status !== 0) throw new Error(`kof check ${target} failed for ${name}:\n${checked.stdout}${checked.stderr}`);
  }
}
