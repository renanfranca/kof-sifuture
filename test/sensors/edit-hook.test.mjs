import assert from 'node:assert/strict';
import { test } from 'node:test';

import { changedThisSession } from '../../scripts/session-ledger.mjs';
import { aProject, fireHook, git, syntheticToken, writeInto } from './project.mjs';

const BASELINE = 'scripts/worktree-baseline.mjs';
const POST_EDIT = '.codex/hooks/post-edit-sensor.mjs';

const spanning = (lines) => {
  const operands = lines - 3;
  const body = Array.from({ length: operands }, (_, i) => `        ${i + 1}${i + 1 < operands ? ' +' : ''}\n`).join('');
  return `Int counted(Int a) {\n    return a +\n${body}}\n`;
};

function aSession(files = { 'README.md': '# probe\n' }) {
  const root = aProject(files);
  git(root, 'commit', '-q', '-m', 'base');
  return root;
}

function start(root, session) {
  return fireHook(BASELINE, root, { hook_event_name: 'SessionStart', session_id: session });
}

function afterShell(root, session, command, env) {
  return fireHook(POST_EDIT, root, { hook_event_name: 'PostToolUse', session_id: session, tool_name: 'Bash', tool_input: { command } }, env);
}

test('a shell command that writes a 26-line function is answered at once with the finding, its location and guide', () => {
  const root = aSession();
  start(root, 'long');
  writeInto(root, 'src/main/kof/Probe.kf', spanning(26));

  const answer = afterShell(root, 'long', 'cat > src/main/kof/Probe.kf');

  assert.equal(answer.code, 0, answer.err);
  const response = JSON.parse(answer.out);
  assert.equal(response.decision, 'block');
  assert.match(response.reason, /The command ran/);
  assert.match(response.reason, /EDIT SENSORS: lint FAIL · dup PASS · gitleaks PASS/);
  assert.match(response.reason, /src\/main\/kof\/Probe\.kf:1:1 ERROR long-function\n {2}`counted` has 26 lines; the limit is 25\./);
  assert.match(response.reason, /LONG-FUNCTION\n/);
});

test('a 25-line function is at the limit, so the hook stays silent', () => {
  const root = aSession();
  start(root, 'limit');
  writeInto(root, 'src/main/kof/Probe.kf', spanning(25));

  const answer = afterShell(root, 'limit', 'cat > src/main/kof/Probe.kf');

  assert.equal(answer.code, 0, answer.err);
  assert.equal(answer.out, '');
});

test('the ledger records an edited file once, and a later read leaves it as it was', () => {
  const root = aSession();
  start(root, 'reader');
  writeInto(root, 'src/main/kof/A.kf', spanning(10));

  afterShell(root, 'reader', 'cat > src/main/kof/A.kf');
  const afterEdit = changedThisSession(root, 'reader');
  afterShell(root, 'reader', 'cat src/main/kof/A.kf');

  assert.deepEqual(afterEdit, ['src/main/kof/A.kf']);
  assert.deepEqual(changedThisSession(root, 'reader'), ['src/main/kof/A.kf']);
});

test('a file changed outside the session between two looks shows up in the second look, not the first', () => {
  const root = aSession();
  start(root, 'outside');
  afterShell(root, 'outside', 'ls');
  const firstLook = changedThisSession(root, 'outside');

  writeInto(root, 'src/main/kof/B.kf', spanning(10));
  afterShell(root, 'outside', 'ls');

  assert.deepEqual(firstLook, []);
  assert.deepEqual(changedThisSession(root, 'outside'), ['src/main/kof/B.kf']);
});

test('a change to prose only runs the secret scan', () => {
  const root = aSession();
  start(root, 'prose');
  writeInto(root, 'docs/notes.md', `token = ${syntheticToken()}\n`);

  const answer = afterShell(root, 'prose', 'cat > docs/notes.md');

  const response = JSON.parse(answer.out);
  assert.match(response.reason, /EDIT SENSORS: lint SKIP · dup SKIP · gitleaks FAIL/);
  assert.match(response.reason, /docs\/notes\.md:1 ERROR/);
});

test('SENSORS=git turns the agent tier off, so the hook neither answers nor records', () => {
  const root = aSession();
  start(root, 'off');
  writeInto(root, 'src/main/kof/Probe.kf', spanning(26));

  const answer = afterShell(root, 'off', 'cat > src/main/kof/Probe.kf', { SENSORS: 'git' });

  assert.equal(answer.out, '');
  assert.deepEqual(changedThisSession(root, 'off'), []);
});

test('a resumed session keeps its last look, so a file changed while it was closed shows up at the next command', () => {
  const root = aSession();
  start(root, 'resumed');
  afterShell(root, 'resumed', 'ls');

  writeInto(root, 'src/main/kof/External.kf', spanning(26));
  start(root, 'resumed');
  const answer = afterShell(root, 'resumed', 'ls');

  assert.match(JSON.parse(answer.out).reason, /src\/main\/kof\/External\.kf:1:1 ERROR long-function/);
  assert.deepEqual(changedThisSession(root, 'resumed'), ['src/main/kof/External.kf']);
});
