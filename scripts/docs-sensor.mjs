import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';

import { sensorArguments } from './sensor-arguments.mjs';
import { guideNamed } from './sensor-guides.mjs';
import { coach, sensorReport } from './sensor-report.mjs';

const { root: projectRoot, paths: requested } = sensorArguments();
const scripts = JSON.parse(readFileSync(path.join(projectRoot, 'package.json'), 'utf8')).scripts ?? {};

const staleDoc = guideNamed('stale-doc');
const ruleGuides = { 'outside-repo': guideNamed('machine-bound-link') };

const NPM_CALL = /\bnpm (run )?([a-z][\w:-]*)/g;
const FENCE = /```([\w-]*)\r?\n([\s\S]*?)```/g;
const SHELL_LANGUAGES = new Set(['', 'sh', 'bash', 'zsh', 'shell', 'console']);
const LINK = /\[[^\]]*\]\(([^)\s]+)\)/g;
const LIFECYCLE = new Set(['start', 'test', 'stop', 'restart']);
const EXTERNAL = /^(https?:|mailto:|#)/;
const LINE_SUFFIX = /:\d+(-\d+)?$/;

function trackedDocs() {
  const found = spawnSync('git', ['ls-files', '*.md'], { cwd: projectRoot, encoding: 'utf8' });

  return found.stdout.split('\n').filter(Boolean);
}

function lineOf(text, index) {
  return text.slice(0, index).split('\n').length;
}

function namesAScript([, run, name]) {
  return Boolean(run) || LIFECYCLE.has(name);
}

function shellBlocks(text) {
  return [...text.matchAll(FENCE)]
    .filter((match) => SHELL_LANGUAGES.has(match[1].toLowerCase()))
    .map((match) => ({ body: match[2], offset: match.index + match[0].indexOf('\n') + 1 }));
}

function missingIn(block, text) {
  return [...block.body.matchAll(NPM_CALL)]
    .filter(namesAScript)
    .filter((match) => !scripts[match[2]])
    .map((match) => ({
      rule: 'missing-script',
      line: lineOf(text, block.offset + match.index),
      detail: `\`${match[0]}\` is documented, but package.json has no "${match[2]}" script.`,
    }));
}

function missingScripts(text) {
  return shellBlocks(text).flatMap((block) => missingIn(block, text));
}

function linkedFile(target) {
  return target.split('#')[0].replace(LINE_SUFFIX, '');
}

function leavesRepository(file, from) {
  const relative = path.relative(projectRoot, path.resolve(from, file));

  return path.isAbsolute(file) || relative.startsWith('..');
}

function linkFinding(target, from) {
  const file = linkedFile(target);
  if (leavesRepository(file, from)) return { rule: 'outside-repo', detail: `Links to \`${target}\`, outside the repository.` };
  if (!existsSync(path.resolve(from, file))) return { rule: 'broken-link', detail: `Links to \`${target}\`, which does not exist.` };

  return null;
}

function linkFindings(text, docPath) {
  const from = path.dirname(path.resolve(projectRoot, docPath));

  return [...text.matchAll(LINK)]
    .filter((match) => !EXTERNAL.test(match[1]))
    .map((match) => ({ ...linkFinding(match[1], from), line: lineOf(text, match.index) }))
    .filter((finding) => finding.rule);
}

function inspect(docPath) {
  const text = readFileSync(path.resolve(projectRoot, docPath), 'utf8');

  return [...missingScripts(text), ...linkFindings(text, docPath)]
    .sort((a, b) => a.line - b.line)
    .map((finding) => ({ ...finding, docPath }));
}

function format(finding, coached) {
  return [`${finding.docPath}:${finding.line} ERROR ${finding.rule}`, `  ${finding.detail}`, coach(ruleGuides[finding.rule] ?? staleDoc, coached)].join(
    '\n',
  );
}

const targets = (requested.length ? requested : trackedDocs()).filter((doc) => existsSync(path.resolve(projectRoot, doc)));
const coached = new Set();
const findings = targets.flatMap(inspect).map((finding) => format(finding, coached));

process.stdout.write(sensorReport('docs', findings));
process.exitCode = findings.length === 0 ? 0 : 1;
