#!/usr/bin/env node
import { inspect } from '../../scripts/edit-sensors.mjs';
import { answer, readHookPayload } from '../../scripts/hook-io.mjs';
import { sensorArguments } from '../../scripts/sensor-arguments.mjs';
import { stamp } from '../../scripts/sensor-liveness.mjs';
import { agentTierFires } from '../../scripts/sensor-tier.mjs';
import { record } from '../../scripts/session-ledger.mjs';
import { changedSinceLastLook } from '../../scripts/worktree-watch.mjs';

const RAN = [
  'The command ran and its changes are on disk; do not run it again.',
  'The cheap sensors flagged the files it changed. Fix these findings before you go on:',
  '',
].join('\n');

if (agentTierFires()) {
  const { root } = sensorArguments();
  const payload = await readHookPayload();
  stamp(root, 'PostToolUse');

  const changed = changedSinceLastLook(root, payload.session_id);
  record(root, payload.session_id, changed);

  const verdict = inspect(root, changed);
  if (verdict && !verdict.passed) answer({ decision: 'block', reason: `${RAN}${verdict.report}` });
}
