import { allKofFiles } from './git-changes.mjs';
import { analyse } from './kof-analysis.mjs';
import { dupReport, lintReport } from './kof-reports.mjs';
import { sensorArguments } from './sensor-arguments.mjs';
import { unavailableReport } from './sensor-unavailable.mjs';

const AREAS = ['src/main/kof', 'src/test/kof'];

function areaOf(file) {
  return AREAS.find((area) => file.startsWith(`${area}/`)) ?? 'other';
}

function summary(report) {
  const counts = new Map();
  report.findings.forEach((finding) => {
    const key = `${finding.rule}\t${areaOf(finding.file)}`;
    counts.set(key, (counts.get(key) ?? 0) + 1);
  });
  report.duplication.clones.forEach((clone) => {
    const key = `duplicated-code\t${areaOf(clone.locations[0].file)}`;
    counts.set(key, (counts.get(key) ?? 0) + 1);
  });
  const rows = [...counts.entries()].sort(([a], [b]) => a.localeCompare(b));

  return rows.map(([key, count]) => {
    const [rule, area] = key.split('\t');
    return `  ${rule.padEnd(22)} ${area.padEnd(13)} ${count}`;
  });
}

const { root } = sensorArguments();
const files = allKofFiles(root);
const report = analyse(root, files);

if (report.unavailable) {
  process.stdout.write(unavailableReport('debt', report.unavailable));
  process.exitCode = 1;
} else {
  process.stdout.write(
    [
      `SENSORS DEBT (report only, ${files.length} Kof files)`,
      '',
      ...summary(report),
      '',
      lintReport(report).text,
      dupReport(report).text,
    ].join('\n'),
  );
}
