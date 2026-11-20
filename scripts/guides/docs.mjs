export const docs = {
  'stale-doc': [
    'The documentation names something that is not there. This is usually the first thing a reader does with the project, and it fails.',
    'Decide which side is wrong before you change either. If the thing was renamed, the doc is stale — fix the doc. If the doc describes something that was always meant to exist, it is a promise nobody kept: build it, or withdraw the promise until you do.',
    'Prose is the one artifact nothing else here checks. A type error dies in milliseconds; a README that lies survives every other sensor in this repo and is copied by everyone who clones it.',
    'Not this: deleting the line so the sensor goes quiet. If the command ought to exist, silence only moves the failure downstream to the reader.',
  ],
  'machine-bound-link': [
    'This link only works on a machine where the target sits at exactly this path. It breaks in a git worktree, in another clone, on another computer, and on GitHub, and a line number in it silently drifts as the other repository moves.',
    'For evidence of what someone saw, link a permalink pinned to the commit they saw: `https://github.com/<owner>/<repo>/blob/<sha>/<path>#L<line>`. For an instruction to read the current local checkout, write the path as code text, such as `~/projects/kof/learn/README.md`, which names the place without pretending to be a link.',
    'Not this: copying the file into this repository. A copy goes stale without telling anyone.',
  ],
};
