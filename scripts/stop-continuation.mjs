import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';

import { ledgerFile, ledgerRoot } from './ledger-path.mjs';

const MOST_PUSHBACKS = 3;

function markerPath(root, session) {
  return ledgerFile(root, session, '.pushbacks.json');
}

function seenIn(root, session) {
  try {
    const file = markerPath(root, session);
    return existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : [];
  } catch {
    return [];
  }
}

export function fingerprint(findings) {
  return findings
    .map((finding) => `${finding.rule}@${finding.where}`)
    .sort()
    .join('|');
}

export function shouldPushBack(root, session, findings) {
  const seen = seenIn(root, session);
  const mark = fingerprint(findings);

  if (seen.includes(mark) || seen.length >= MOST_PUSHBACKS) return false;

  try {
    mkdirSync(ledgerRoot(root), { recursive: true });
    writeFileSync(markerPath(root, session), JSON.stringify([...seen, mark]));
  } catch {
    return true;
  }

  return true;
}
