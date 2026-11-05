import { spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const VERDICTS = {
  0: { state: 'PASS' },
  1: { state: 'FAIL', detail: 'KofMut exit 1: at least one mutant survived' },
  2: { state: 'FAIL', detail: 'KofMut exit 2: baseline_failed or error; unavailable' },
  3: { state: 'FAIL', detail: 'KofMut exit 3: incomplete, no_scope or no_mutants; quality not approved' },
};

function evidence(root, runId, result) {
  const runs = path.join(root, '.agent', 'tmp', 'kof-mut-runs');
  mkdirSync(runs, { recursive: true });
  writeFileSync(path.join(runs, `${runId}.stdout`), result.stdout ?? '');
  writeFileSync(path.join(runs, `${runId}.stderr`), result.stderr ?? '');
  writeFileSync(path.join(runs, `${runId}.exit`), `${result.status}\n`);
}

export function mutate(root, scope) {
  const runId = randomUUID();
  const workspace = mkdtempSync(path.join(tmpdir(), 'sifuture-mutation-'));
  const scopeFile = path.join(workspace, 'scope.json');
  const reports = path.join(root, '.agent', 'tmp', 'kof-mut-reports');
  try {
    writeFileSync(scopeFile, JSON.stringify(scope));
    mkdirSync(reports, { recursive: true });
    const args = ['run', '--project', root, '--files', scopeFile, '--config', 'kof-mut.json', '--report-dir', reports, '--run-id', runId];
    process.stdout.write(`\n> kof-mut ${args.join(' ')}\n`);
    const result = spawnSync('kof-mut', args, { cwd: root, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
    process.stdout.write(result.stdout ?? '');
    process.stderr.write(result.stderr ?? '');
    if (result.error) return { state: 'FAIL', detail: `kof-mut did not run: ${result.error.code}; unavailable` };

    evidence(root, runId, result);
    return VERDICTS[result.status] ?? { state: 'FAIL', detail: `KofMut exit ${result.status}: unexpected` };
  } finally {
    rmSync(workspace, { recursive: true, force: true });
  }
}
