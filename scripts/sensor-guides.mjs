import { comments } from './guides/comments.mjs';
import { docs } from './guides/docs.mjs';
import { secrets } from './guides/secrets.mjs';
import { structural } from './guides/structural.mjs';
import { tests } from './guides/tests.mjs';

export const guides = Object.fromEntries(
  Object.entries({
    ...structural,
    ...comments,
    ...docs,
    ...secrets,
    ...tests,
  }).map(([name, lines]) => [name, lines.join('\n')]),
);

export const kernels = {
  'long-function': 'extract one function per job',
  'long-file': 'decide which kind of big it is',
  'high-complexity': 'name the conditions first',
  'deep-nesting': 'guard clauses, return early',
  'too-many-statements': 'separate deciding from doing',
  'too-many-parameters': 'name the clump, pass one object',
  'duplicated-code': 'find what varies, parameterise it',
  'assertion-free-test': 'it passes because nothing threw',
  'mystery-guest': 'build it in the test, name the setup',
  'branching-test': 'one test per path',
  'commented-out-code': 'delete it, git remembers',
  'long-comment': 'name it in code, or link the doc',
  'stale-comment': 'the code moved, the comment did not',
  'deferred-work': 'do it, or track it properly',
  'looping-test': 'testRows, so the failure names the case',
  'unnamed-arrange': 'a long arrange is a missing name',
  'leaked-secret': 'rotate it first, then remove it',
  'stale-doc': 'fix the doc or build the thing',
};

export function guideNamed(name) {
  return { name, text: guides[name], kernel: kernels[name] };
}
