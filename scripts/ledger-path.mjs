import { createHash } from 'node:crypto';
import path from 'node:path';

const SAFE_NAME = /^[A-Za-z0-9_-]{1,128}$/;

export function ledgerRoot(root) {
  return path.join(root, '.sensors', 'ledger');
}

function hashedName(session) {
  return `session-${createHash('sha256').update(session).digest('hex').slice(0, 32)}`;
}

export function safeSessionName(session) {
  if (typeof session !== 'string' || session.length === 0) return 'unidentified';

  return SAFE_NAME.test(session) ? session : hashedName(session);
}

export function ledgerFile(root, session, suffix) {
  return path.join(ledgerRoot(root), `${safeSessionName(session)}${suffix}`);
}
