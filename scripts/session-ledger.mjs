import { appendFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';

import { ledgerFile, ledgerRoot } from './ledger-path.mjs';

export function ledgerPath(root, session) {
  return ledgerFile(root, session, '.txt');
}

export function record(root, session, files) {
  if (!session || files.length === 0) return;

  try {
    mkdirSync(ledgerRoot(root), { recursive: true });
    appendFileSync(ledgerPath(root, session), files.map((file) => `${file}\n`).join(''));
  } catch {
    return;
  }
}

export function changedThisSession(root, session) {
  const ledger = ledgerPath(root, session);

  if (!session || !existsSync(ledger)) return [];

  return [...new Set(readFileSync(ledger, 'utf8').split('\n').filter(Boolean))];
}
