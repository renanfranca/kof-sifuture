import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';

import { sensorArguments } from './sensor-arguments.mjs';
import { guideNamed } from './sensor-guides.mjs';
import { coach, sensorReport } from './sensor-report.mjs';

const { root: projectRoot, paths: requested } = sensorArguments();
const scripts = JSON.parse(readFileSync(path.join(projectRoot, 'package.json'), 'utf8')).scripts ?? {};

const docGuide = guideNamed('stale-doc');

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

function brokenLinks(text, docPath) {
  const from = path.dirname(path.resolve(projectRoot, docPath));

  return [...text.matchAll(LINK)]
    .filter((match) => !EXTERNAL.test(match[1]))
    .filter((match) => !existsSync(path.resolve(from, linkedFile(match[1]))))
    .map((match) => ({
      rule: 'broken-link',
      line: lineOf(text, match.index),
      detail: `Links to \`${match[1]}\`, which does not exist.`,
    }));
}

function inspect(docPath) {
  const text = readFileSync(path.resolve(projectRoot, docPath), 'utf8');

  return [...missingScripts(text), ...brokenLinks(text, docPath)]
    .sort((a, b) => a.line - b.line)
    .map((finding) => ({ ...finding, docPath }));
}

function format(finding, coached) {
  return [`${finding.docPath}:${finding.line} ERROR ${finding.rule}`, `  ${finding.detail}`, coach(docGuide, coached)].join(
    '\n',
  );
}

const targets = (requested.length ? requested : trackedDocs()).filter((doc) => existsSync(path.resolve(projectRoot, doc)));
const coached = new Set();
const findings = targets.flatMap(inspect).map((finding) => format(finding, coached));

process.stdout.write(sensorReport('docs', findings));
process.exitCode = findings.length === 0 ? 0 : 1;
