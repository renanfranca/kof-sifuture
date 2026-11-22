#!/usr/bin/env node
import { appendFileSync, mkdirSync } from 'node:fs';

import { answer, readHookPayload } from './hook-io.mjs';
import { ledgerFile, ledgerRoot } from './ledger-path.mjs';
import { sensorArguments } from './sensor-arguments.mjs';
import { stamp } from './sensor-liveness.mjs';
import { agentTierFires } from './sensor-tier.mjs';
import { stopAnswer } from './stop-response.mjs';
import { requestedScope, verdictFor } from './stop-verdict.mjs';

const DISABLED = 'sensors: SENSORS=git turns the agent tier off, so the Stop sensors did not run. `npm run check` still runs them.\n';
const SKIPPED = { passed: true, outcome: 'skip', report: 'STOP SENSORS: SKIP (nothing changed in this session)', findings: [] };

function unavailable(error) {
  const report = `STOP SENSORS: UNAVAILABLE\n\n${String(error?.stack ?? error)}\nA sensor that could not run has not passed.`;
  return { passed: false, outcome: 'unavailable', report, findings: [{ rule: 'unavailable', where: String(error?.message ?? error) }] };
}

function verdictOn(root, scope) {
  if (scope.length === 0) return SKIPPED;

  try {
    return verdictFor(root, scope);
  } catch (error) {
    return unavailable(error);
  }
}

function keep(root, payload, verdict, response) {
  const entry = `${new Date().toISOString()} stop_hook_active=${Boolean(payload.stop_hook_active)} answer=${response.decision ?? 'continue'}\n${verdict.report.trim()}\n\n`;
  try {
    mkdirSync(ledgerRoot(root), { recursive: true });
    appendFileSync(ledgerFile(root, payload.session_id, '.stop.log'), entry);
  } catch {
    return;
  }
}

if (!agentTierFires()) {
  process.stderr.write(DISABLED);
} else {
  const { root } = sensorArguments();
  const payload = await readHookPayload();
  const verdict = verdictOn(root, requestedScope(root, payload.session_id));
  const response = stopAnswer(root, payload, verdict);

  keep(root, payload, verdict, response);
  stamp(root, 'Stop');
  if (!response.decision) process.stderr.write(`${verdict.report}\n`);
  answer(response);
}
