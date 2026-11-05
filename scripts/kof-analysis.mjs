import { spawnSync } from 'node:child_process';
import path from 'node:path';

import { repositoryRoot } from './sensor-arguments.mjs';

const runner = path.join(repositoryRoot, 'scripts', 'kof-sensors', 'run');

function parsed(stdout) {
  try {
    return JSON.parse(stdout);
  } catch {
    return null;
  }
}

export function analyse(root, files) {
  const result = spawnSync('python3', [runner, '--findings', root, ...files], {
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  });
  const report = parsed(result.stdout ?? '');

  if (result.error || report === null) {
    return { unavailable: [`the Kof analyser did not produce a report (exit ${result.status}).`, ...tail(result.stderr)] };
  }
  if (!report.success) return { unavailable: [...report.failures.map((failure) => `could not analyse ${failure}`), coverage(report)] };

  return report;
}

function tail(text = '') {
  return text.trim().split('\n').filter(Boolean).slice(-5);
}

function coverage({ duplication }) {
  return `${duplication.expected.length} files expected, ${duplication.tokenized.length} tokenized`;
}
