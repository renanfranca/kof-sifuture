#!/usr/bin/env node
import { readHookPayload } from './hook-io.mjs';
import { sensorArguments } from './sensor-arguments.mjs';
import { stamp } from './sensor-liveness.mjs';
import { baseline } from './worktree-watch.mjs';

const { root } = sensorArguments();
const payload = await readHookPayload();

baseline(root, payload.session_id);
stamp(root, 'SessionStart');
