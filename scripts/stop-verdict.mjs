import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';

import { cheapSensors, rollCall, runStep, scopedFiles } from './edit-sensors.mjs';
import { ledgerRoot } from './ledger-path.mjs';
import { repositoryRoot } from './sensor-arguments.mjs';
import { changedThisSession } from './session-ledger.mjs';
import { worktreeChanges } from './worktree-watch.mjs';

const isKof = (file) => file.endsWith('.kf');
const script = (name) => path.join(repositoryRoot, 'scripts', name);

const wholeProject = (name, program, args) => ({ name, targets: (files) => files.filter(isKof), program, args: () => args });

const PRODUCTION = 'src/main/kof/';

function moduleOf(file) {
  return file.slice(PRODUCTION.length, -'.kf'.length).split('/').join('.');
}

function typeEntry(targets, root) {
  const modules = targets.filter((file) => file.startsWith(PRODUCTION) && existsSync(path.join(root, file))).map(moduleOf);
  const entry = path.join(ledgerRoot(root), 'types-entry.kf');
  mkdirSync(path.dirname(entry), { recursive: true });
  writeFileSync(entry, ['import sifuture.*', ...modules.map((module) => `import ${module}`), ''].join('\n'));
  return entry;
}

const typeCheck = (target) => ({
  name: `types:${target}`,
  targets: (files) => files.filter(isKof),
  program: 'python3',
  args: (targets, root) => [script('kof_project.py'), 'check', '--target', target, '--fixture', typeEntry(targets, root)],
});

export const stopTiers = {
  cheap: cheapSensors,
  types: ['jvm', 'js'].map(typeCheck),
  tests: ['jvm', 'js'].map((target) => wholeProject(`tests:${target}`, process.execPath, [script('kof-tests.mjs'), '--target', target])),
};

export function requestedScope(root, session) {
  const dirty = worktreeChanges(root);
  const recorded = changedThisSession(root, session);
  if (recorded.length === 0) return dirty;

  const stillChanged = new Set(dirty);
  return recorded.filter((file) => stillChanged.has(file));
}

export const TEST_BUDGET_MS = 120_000;

function outOfTime(name, budgetMs, output = '') {
  const said = `The Kof tests did not finish within ${budgetMs / 1000}s and were stopped.`;
  return { name, status: 'FAIL', output: [output, said].filter(Boolean).join('\n\n') };
}

function timed(root, step, targets, budget) {
  if (!budget) return runStep(root, step, targets);

  const remaining = budget.endsAt - Date.now();
  if (remaining <= 0) return outOfTime(step.name, budget.ms);

  const result = runStep(root, step, targets, remaining);
  return result.timedOut ? outOfTime(step.name, budget.ms, result.output) : result;
}

const PASSING_TEST = /^PASS /;

function withoutPassingTests(output) {
  const lines = output.split('\n');
  const kept = lines.filter((line) => !PASSING_TEST.test(line));
  const hidden = lines.length - kept.length;
  return hidden === 0 ? output : [`(${hidden} passing tests left out)`, ...kept].join('\n');
}

function located(result, scope) {
  return { ...result, output: withoutPassingTests(relocated(result.output, scope)) };
}

function distinct(findings) {
  const seen = new Set();
  return findings.filter((finding) => {
    const key = `${finding.rule}@${finding.where}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

const BARE_LOCATION = /^([^\s/:]+\.kf)(?=:\d)/gm;

function relocated(output, scope) {
  return output.replace(BARE_LOCATION, (name) => {
    const owners = scope.filter((file) => path.basename(file) === name);
    return owners.length === 1 ? owners[0] : name;
  });
}

function stage(root, steps, files, results, budget) {
  const earlierTierFailed = results.some((result) => result.status === 'FAIL');
  for (const step of steps) {
    const targets = step.targets(files);
    if (earlierTierFailed) results.push({ name: step.name, status: 'NOT RUN', output: '' });
    else if (targets.length === 0) results.push({ name: step.name, status: 'SKIP', output: '' });
    else results.push(located(timed(root, step, targets, budget), files));
  }
}

const LOCATED = /^(\S+?:\d+(?::\d+)?):? ERROR ([^\s:]+)/gm;
const FAILING_TEST = /^FAIL (.+?): /gm;

function findingsIn(failure) {
  const located = [...failure.output.matchAll(LOCATED)].map(([, where, rule]) => ({ rule, where }));
  const failingTests = [...failure.output.matchAll(FAILING_TEST)].map(([, name]) => ({ rule: 'failing-test', where: name }));
  if (located.length + failingTests.length > 0) return [...located, ...failingTests];

  const steady = failure.output.replace(/\d+(\.\d+)?/g, '#');
  return [{ rule: failure.name, where: createHash('sha256').update(steady).digest('hex').slice(0, 12) }];
}

export function verdictFor(root, scope, tiers = stopTiers, { testBudgetMs = TEST_BUDGET_MS } = {}) {
  const results = [];
  stage(root, tiers.cheap, scopedFiles(root, scope), results);
  stage(root, tiers.types, scope, results);
  stage(root, tiers.tests, scope, results, { ms: testBudgetMs, endsAt: Date.now() + testBudgetMs });

  const failures = results.filter((result) => result.status === 'FAIL');
  const report = [rollCall('STOP SENSORS', results), '', ...failures.map((failure) => failure.output)].join('\n');

  return {
    passed: failures.length === 0,
    outcome: failures.length === 0 ? 'pass' : 'fail',
    report,
    findings: distinct(failures.flatMap(findingsIn)),
  };
}
