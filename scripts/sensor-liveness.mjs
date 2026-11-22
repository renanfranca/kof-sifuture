import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

import { ledgerRoot } from './ledger-path.mjs';

export const HOOK_EVENTS = ['SessionStart', 'PostToolUse', 'Stop'];

function stampPath(root, event) {
  return path.join(ledgerRoot(root), `.last-${event}`);
}

export function stamp(root, event, at = Date.now()) {
  try {
    mkdirSync(ledgerRoot(root), { recursive: true });
    writeFileSync(stampPath(root, event), String(at));
  } catch {
    return;
  }
}

export function lastSeen(root, event) {
  const file = stampPath(root, event);

  if (!existsSync(file)) return null;

  const at = Number(readFileSync(file, 'utf8').trim());

  return Number.isFinite(at) ? at : null;
}
