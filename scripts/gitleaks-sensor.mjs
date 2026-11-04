import { spawnSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

import { publishableFiles } from './git-changes.mjs';
import { sensorArguments } from './sensor-arguments.mjs';
import { guideNamed } from './sensor-guides.mjs';
import { coach, sensorReport } from './sensor-report.mjs';
import { unavailableReport } from './sensor-unavailable.mjs';

const secretGuide = guideNamed('leaked-secret');

function mirror(root, files, into) {
  files
    .filter((file) => statSync(path.join(root, file)).isFile())
    .forEach((file) => {
      const copy = path.join(into, file);
      mkdirSync(path.dirname(copy), { recursive: true });
      copyFileSync(path.join(root, file), copy);
    });
}

function scan(scanned, reportPath) {
  return spawnSync(
    'gitleaks',
    ['dir', scanned, '--report-format', 'json', '--report-path', reportPath, '--no-banner', '--ignore-gitleaks-allow', '--redact=100'],
    { stdio: 'ignore' },
  );
}

function completed(result) {
  return !result.error && (result.status === 0 || result.status === 1);
}

function run(root, files) {
  const workspace = mkdtempSync(path.join(tmpdir(), 'sifuture-gitleaks-'));
  const scanned = path.join(workspace, 'files');
  const reportPath = path.join(workspace, 'report.json');
  try {
    mkdirSync(scanned);
    mirror(root, files, scanned);
    const result = scan(scanned, reportPath);
    if (!completed(result) || !existsSync(reportPath)) return null;

    return JSON.parse(readFileSync(reportPath, 'utf8')).map((finding) => ({
      ...finding,
      File: path.relative(scanned, path.resolve(scanned, finding.File)),
    }));
  } finally {
    rmSync(workspace, { recursive: true, force: true });
  }
}

function formatFinding(finding, coached) {
  return [
    `${finding.File}:${finding.StartLine} ERROR ${finding.RuleID}`,
    `  ${finding.Description}`,
    '  The value is redacted here on purpose — open the file to see it.',
    coach(secretGuide, coached),
  ].join('\n');
}

const { root, paths } = sensorArguments();
const found = run(root, paths.length ? paths : publishableFiles(root));

if (found === null) {
  process.stdout.write(
    unavailableReport('gitleaks', [
      'gitleaks did not run, so nothing here has been scanned for secrets.',
      'Install Gitleaks 8.30.1 or put it on PATH.',
    ]),
  );
  process.exitCode = 1;
} else {
  const coached = new Set();
  const findings = found.map((finding) => formatFinding(finding, coached));

  process.stdout.write(sensorReport('gitleaks', findings));
  process.exitCode = findings.length === 0 ? 0 : 1;
}
