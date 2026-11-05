import { guideNamed } from './sensor-guides.mjs';
import { coach, sensorReport } from './sensor-report.mjs';

const describe = {
  'long-file': (f) => `This file has ${f.value} non-blank lines; the limit is ${f.limit}.`,
  'long-function': (f) => `\`${f.name}\` has ${f.value} lines; the limit is ${f.limit}.`,
  'high-complexity': (f) => `\`${f.name}\` has complexity ${f.value}; the limit is ${f.limit}.`,
  'deep-nesting': (f) => `\`${f.name}\` nests ${f.value} levels deep; the limit is ${f.limit}.`,
  'too-many-statements': (f) => `\`${f.name}\` has ${f.value} statements; the limit is ${f.limit}.`,
  'too-many-parameters': (f) => `\`${f.name}\` takes ${f.value} parameters; the limit is ${f.limit}.`,
  'assertion-free-test': (f) => `\`${f.name}\` asserts nothing. It passes as long as the code does not throw.`,
  'branching-test': (f) => `\`${f.name}\` branches here, so it describes two behaviours and checks one.`,
  'looping-test': (f) => `\`${f.name}\` loops here, so a failure cannot name the case.`,
  'unnamed-arrange': (f) => `${f.value} statements before \`${f.name}\` asserts anything; the limit is ${f.limit}.`,
  'long-comment': (f) => `This comment is ${f.value} lines. Say the why in one line, or write it in docs/ and point at it.`,
  'commented-out-code': () => 'This comment is commented-out code, not documentation.',
  'deferred-work': (f) => `\`${f.name}\` marks deferred work in a comment.`,
  'stale-comment': (f) =>
    f.name.includes('/')
      ? `\`${f.name}\` does not exist. The comment points at a file that is gone.`
      : `\`${f.name}\` is not in this file. Either the comment outlived the code, or it belongs somewhere else.`,
  'mystery-guest': (f) => `\`${f.name}\` is filled in by a hook, so the tests cannot be read from their own body.`,
};

function format(finding, coached) {
  return [
    `${finding.file}:${finding.line}:${finding.column} ERROR ${finding.rule}`,
    `  ${describe[finding.rule](finding)}`,
    coach(guideNamed(finding.rule), coached),
  ].join('\n');
}

export function lintReport(report) {
  const coached = new Set();
  const findings = report.findings.map((finding) => format(finding, coached));

  return { text: sensorReport('lint', findings), failed: findings.length > 0 };
}

const duplicationGuide = guideNamed('duplicated-code');

function lines(location) {
  return location.endLine - location.line + 1;
}

function formatClone(clone, coached) {
  const [first, ...others] = clone.locations;
  const elsewhere = others.map((location) => `${location.file}:${location.line}`).join(', ');

  return [
    `${first.file}:${first.line} ERROR duplicated-code`,
    `  ${clone.tokens} tokens over ${lines(first)} lines duplicated at ${elsewhere}`,
    coach(duplicationGuide, coached),
  ].join('\n');
}

function coverage(duplication) {
  return `  ${duplication.expected.length} files expected, ${duplication.tokenized.length} tokenized\n`;
}

export function dupReport({ duplication }) {
  const coached = new Set();
  const findings = duplication.clones.map((clone) => formatClone(clone, coached));

  return { text: sensorReport('dup', findings).replace('\n', `\n${coverage(duplication)}`), failed: findings.length > 0 };
}
