import { changedKofFiles } from './git-changes.mjs';
import { analyse } from './kof-analysis.mjs';
import { sensorArguments } from './sensor-arguments.mjs';
import { unavailableReport } from './sensor-unavailable.mjs';

function finish(text, code) {
  process.stdout.write(text);
  process.exitCode = code;
}

export function runKofSensor(sensor, render) {
  const { root, paths } = sensorArguments();
  const scope = paths.length ? { files: paths } : changedKofFiles(root);
  if (scope.unavailable) return finish(unavailableReport(sensor, scope.unavailable), 1);
  if (scope.files.length === 0) return finish(`SENSOR ${sensor}: SKIP (no Kof files changed against main)\n`, 0);

  const report = analyse(root, scope.files);
  if (report.unavailable) return finish(unavailableReport(sensor, report.unavailable), 1);

  const { text, failed } = render(report);
  return finish(text, failed ? 1 : 0);
}
