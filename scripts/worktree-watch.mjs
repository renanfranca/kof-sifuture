import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';

import { dirtyPaths } from './git-changes.mjs';
import { ledgerFile, ledgerRoot } from './ledger-path.mjs';

function stampOf(root, file) {
  const full = path.join(root, file);

  return existsSync(full) ? statSync(full).mtimeMs : 0;
}

const OWN_STATE = /^\.sensors(\/|$)/;

export function worktreeChanges(root) {
  return dirtyPaths(root).filter((file) => !OWN_STATE.test(file));
}

export function snapshot(root) {
  return Object.fromEntries(worktreeChanges(root).map((file) => [file, stampOf(root, file)]));
}

export function movedFiles(before, after) {
  const gone = Object.keys(before).filter((file) => !(file in after));
  const moved = Object.keys(after).filter((file) => before[file] !== after[file]);

  return [...moved, ...gone].sort();
}

function snapshotPath(root, session) {
  return ledgerFile(root, session, '.worktree.json');
}

function remember(root, session, taken) {
  try {
    mkdirSync(ledgerRoot(root), { recursive: true });
    writeFileSync(snapshotPath(root, session), JSON.stringify(taken));
  } catch {
    return;
  }
}

function stored(root, session) {
  const file = snapshotPath(root, session);
  if (!existsSync(file)) return null;

  try {
    return JSON.parse(readFileSync(file, 'utf8'));
  } catch {
    return null;
  }
}

export function baseline(root, session) {
  if (stored(root, session) === null) remember(root, session, snapshot(root));
}

export function changedSinceLastLook(root, session) {
  const before = stored(root, session);
  const after = snapshot(root);

  remember(root, session, after);

  return before === null ? [] : movedFiles(before, after);
}
