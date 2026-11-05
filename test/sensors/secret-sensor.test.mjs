import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import { test } from 'node:test';

import { aProject, runSensor, runSensorWith, writeInto } from './project.mjs';

function syntheticToken() {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const body = [...randomBytes(36)].map((byte) => alphabet[byte % alphabet.length]).join('');
  return ['gh', 'p_', body].join('');
}

test('secret sensor reports a synthetic token with its location, redacted, and passes once it is removed', () => {
  const token = syntheticToken();
  const root = aProject({ 'README.md': '# Notes\n', 'config/settings.txt': `name = sifuture\ntoken = ${token}\n` });

  const found = runSensor('gitleaks-sensor.mjs', root);
  writeInto(root, 'config/settings.txt', 'name = sifuture\n');
  const gone = runSensor('gitleaks-sensor.mjs', root);

  assert.equal(found.code, 1, found.err);
  assert.match(found.out, /^SENSOR gitleaks: FAIL \(1 finding\)/);
  assert.match(found.out, /config\/settings\.txt:2 ERROR github-pat/);
  assert.match(found.out, /LEAKED-SECRET\n {2}A credential written into source/);
  assert.ok(!found.out.includes(token), 'the token must be redacted');
  assert.equal(gone.code, 0, gone.err);
  assert.equal(gone.out, 'SENSOR gitleaks: PASS (0 findings)\n');
});

test('secret sensor is unavailable, never passing, when gitleaks cannot run', () => {
  const root = aProject({ 'README.md': '# Notes\n' });

  const report = runSensorWith({ ...process.env, PATH: '/nonexistent' }, 'gitleaks-sensor.mjs', root);

  assert.equal(report.code, 1, report.err);
  assert.match(report.out, /^SENSOR gitleaks: UNAVAILABLE\n/);
  assert.match(report.out, /gitleaks did not run, so nothing here has been scanned for secrets\./);
  assert.doesNotMatch(report.out, /PASS/);
});

test('secret sensor scans untracked publishable files and leaves git-ignored local evidence out', () => {
  const root = aProject({ '.gitignore': '/evidence/\n', 'README.md': '# Notes\n' });
  writeInto(root, 'draft/new.txt', `token = ${syntheticToken()}\n`);
  writeInto(root, 'evidence/raw.log', `token = ${syntheticToken()}\n`);

  const report = runSensor('gitleaks-sensor.mjs', root);

  assert.equal(report.code, 1, report.err);
  assert.match(report.out, /^SENSOR gitleaks: FAIL \(1 finding\)/);
  assert.match(report.out, /draft\/new\.txt:1 ERROR/);
  assert.doesNotMatch(report.out, /evidence\/raw\.log/);
});
