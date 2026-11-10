import { spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const VERDICTS = {
  0: { state: 'PASS' },
  1: { state: 'FAIL', detail: 'KofMut exit 1: at least one mutant survived' },
  2: { state: 'FAIL', detail: 'KofMut exit 2: baseline_failed or error; unavailable' },
};

function evidence(root, runId, result) {
  const runs = path.join(root, '.agent', 'tmp', 'kof-mut-runs');
  mkdirSync(runs, { recursive: true });
  writeFileSync(path.join(runs, `${runId}.stdout`), result.stdout ?? '');
  writeFileSync(path.join(runs, `${runId}.stderr`), result.stderr ?? '');
  writeFileSync(path.join(runs, `${runId}.exit`), `${result.status}\n`);
}

const REPORT_PATH = 'reportPath=';
const NOT_APPROVED = new Set(['incomplete', 'no_scope', 'no_mutants']);

function announcedReport(stdout) {
  const announcements = stdout.split('\n').filter((line) => line.startsWith(REPORT_PATH));
  if (announcements.length !== 1) throw new Error(`expected one ${REPORT_PATH} line, found ${announcements.length}`);

  const reportPath = JSON.parse(announcements[0].slice(REPORT_PATH.length));
  if (typeof reportPath !== 'string' || !path.isAbsolute(reportPath)) throw new Error('reportPath is not absolute');

  const report = JSON.parse(readFileSync(reportPath, 'utf8'));
  const limitations = report?.limitations;
  if (typeof report?.status !== 'string' || !Array.isArray(limitations) || limitations.some((item) => typeof item !== 'string')) {
    throw new Error('status or limitations missing');
  }
  if (!Array.isArray(report.discardedCandidates)) throw new Error('discardedCandidates is not an array');
  return report;
}

const notApproved = (detail) => ({ state: 'FAIL', detail: `${detail}; quality not approved` });

function noMutantsDetail(discarded) {
  const detail = 'KofMut no_mutants: no applicable mutants';
  return discarded > 0 ? `${detail}, ${discarded} discarded` : detail;
}

function unapprovedVerdict({ status, limitations, discardedCandidates }) {
  if (!NOT_APPROVED.has(status)) return notApproved(`KofMut exit 3 contradicts report: ${status}`);
  if (status !== 'no_mutants') return notApproved(`KofMut ${status}${limitations.length > 0 ? `: ${limitations.join('; ')}` : ''}`);
  if (limitations.length > 0) return notApproved('KofMut exit 3 contradicts report: no_mutants with limitations');
  return { state: 'SKIP', detail: noMutantsDetail(discardedCandidates.length) };
}

function readAnnounced(stdout) {
  try {
    return { report: announcedReport(stdout) };
  } catch (error) {
    return { unreadable: error.message };
  }
}

function foreignIdentity(report, runId, scope) {
  if (report.runId !== runId) return `runId ${report.runId} instead of ${runId}`;
  const expected = JSON.stringify([...new Set(scope)].sort());
  const reported = JSON.stringify(report.scope);
  if (reported !== expected) return `scope ${reported} instead of ${expected}`;
  return undefined;
}

function exitThreeVerdict(stdout, runId, scope) {
  const { report, unreadable } = readAnnounced(stdout);
  if (unreadable) return notApproved(`KofMut exit 3 report unreadable: ${unreadable}`);
  const foreign = foreignIdentity(report, runId, scope);
  if (foreign) return notApproved(`KofMut exit 3 report is not from this run: ${foreign}`);
  return unapprovedVerdict(report);
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
    if (result.status === 3) return exitThreeVerdict(result.stdout ?? '', runId, scope);
    return VERDICTS[result.status] ?? { state: 'FAIL', detail: `KofMut exit ${result.status}: unexpected` };
  } finally {
    rmSync(workspace, { recursive: true, force: true });
  }
}
