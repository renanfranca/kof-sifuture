import { spawnSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
import path from 'node:path';

import { checkSteps, runSteps, summary } from './check.mjs';
import { sensorArguments } from './sensor-arguments.mjs';

function journeys(root) {
  return readdirSync(path.join(root, 'tests'))
    .filter((name) => /^browser.*\.py$/.test(name))
    .sort()
    .map((name) => ({
      name: `browser:${name.replace(/\.py$/, '')}`,
      run: () => {
        process.stdout.write(`\n> python3 tests/${name}\n`);
        const result = spawnSync('python3', [`tests/${name}`], { cwd: root, stdio: 'inherit' });
        return result.status === 0 ? { state: 'PASS' } : { state: 'FAIL', detail: `exit ${result.status}` };
      },
    }));
}

const { root } = sensorArguments();
const { text, failed } = summary('CHECK:TASK', runSteps(root, [...checkSteps, ...journeys(root)]));
process.stdout.write(text);
process.exitCode = failed ? 1 : 0;
