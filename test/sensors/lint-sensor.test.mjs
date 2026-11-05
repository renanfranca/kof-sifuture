import assert from 'node:assert/strict';
import { test } from 'node:test';

import { aProject, assertKofChecks, git, runSensor, writeInto } from './project.mjs';

const deciding = (name, operators) =>
  `Bool ${name}(Int a) {\n    return a > 0${Array.from({ length: operators }, (_, i) => ` && a != ${i + 1}`).join('')}\n}\n`;

test('lint sensor reports an explicit Kof file over the complexity limit with location, ID and guide', () => {
  const root = aProject({ 'src/main/kof/Rules.kf': deciding('classify', 10) });
  assertKofChecks(root, 'src/main/kof/Rules.kf');

  const report = runSensor('lint-sensor.mjs', root, 'src/main/kof/Rules.kf');

  assert.equal(report.code, 1, report.err);
  assert.match(report.out, /^SENSOR lint: FAIL \(1 finding\)/);
  assert.match(report.out, /src\/main\/kof\/Rules\.kf:1:1 ERROR high-complexity/);
  assert.match(report.out, /`classify` has complexity 11; the limit is 10\./);
  assert.match(report.out, /HIGH-COMPLEXITY\n {2}Every branch is a path/);
});

test('lint sensor without paths analyses whole Kof files changed against main and leaves unchanged ones out', () => {
  const root = aProject({ 'src/main/kof/Old.kf': deciding('old', 10), 'src/main/kof/Touched.kf': 'Int touched() { return 1 }\n' });
  git(root, 'commit', '-q', '-m', 'base');
  git(root, 'switch', '-q', '-c', 'feature');
  writeInto(root, 'src/main/kof/Touched.kf', `Int touched() { return 1 }\n${deciding('committed', 10)}`);
  git(root, 'commit', '-q', '-am', 'touch');
  writeInto(root, 'src/main/kof/New.kf', deciding('untracked', 10));
  ['Old.kf', 'Touched.kf', 'New.kf'].forEach((name) => assertKofChecks(root, `src/main/kof/${name}`));

  const report = runSensor('lint-sensor.mjs', root);

  assert.equal(report.code, 1, report.err);
  assert.match(report.out, /^SENSOR lint: FAIL \(2 findings\)/);
  assert.match(report.out, /src\/main\/kof\/Touched\.kf:2:1 ERROR high-complexity/);
  assert.match(report.out, /src\/main\/kof\/New\.kf:1:1 ERROR high-complexity/);
  assert.doesNotMatch(report.out, /Old\.kf/);
});

test('lint sensor says it skipped when no Kof file changed against main, instead of passing', () => {
  const root = aProject({ 'src/main/kof/Old.kf': deciding('old', 10) });
  git(root, 'commit', '-q', '-m', 'base');
  writeInto(root, 'README.md', '# Only prose changed\n');

  const report = runSensor('lint-sensor.mjs', root);

  assert.equal(report.code, 0, report.err);
  assert.equal(report.out, 'SENSOR lint: SKIP (no Kof files changed against main)\n');
});

const careless = `class Fixture {
    static Int shared = 0
}

void setup() {
    Fixture.shared = 41
}

test "prints only" {
    println(Fixture.shared)
}

test "branches and loops" {
    for (var i = 0; i < 2; i = i + 1) {
        if (i > 0) {
            assert(i == 1)
        }
    }
}

test "long arrange" {
${Array.from({ length: 9 }, (_, i) => `    var v${i} = ${i}\n`).join('')}    assert(v0 == 0)
}
`;

test('lint sensor reports the five test-design rules with Kof guides', () => {
  const root = aProject({ 'src/test/kof/CarelessTest.kf': careless });
  assertKofChecks(root, 'src/test/kof/CarelessTest.kf');

  const report = runSensor('lint-sensor.mjs', root, 'src/test/kof/CarelessTest.kf');

  assert.equal(report.code, 1, report.err);
  assert.match(report.out, /CarelessTest\.kf:6:5 ERROR mystery-guest\n {2}`Fixture\.shared` is filled in by a hook/);
  assert.match(report.out, /CarelessTest\.kf:9:1 ERROR assertion-free-test\n {2}`prints only` asserts nothing/);
  assert.match(report.out, /CarelessTest\.kf:14:5 ERROR looping-test\n {2}`branches and loops` loops here/);
  assert.match(report.out, /CarelessTest\.kf:15:9 ERROR branching-test\n {2}`branches and loops` branches here/);
  assert.match(report.out, /CarelessTest\.kf:21:1 ERROR unnamed-arrange\n {2}9 statements before `long arrange` asserts anything; the limit is 8\./);
  assert.match(report.out, /LOOPING-TEST\n.*\n {2}Use `testRows` from `kof\.test`/);
  assert.match(report.out, /MYSTERY-GUEST\n {2}Mystery Guest\./);
  assert.doesNotMatch(report.out, /it\.each|beforeEach|`let`/);
});

const commented = `// first line of a paragraph
// second line of the paragraph
Int one() { return 1 }
// var speed = 4
Int two() { return 2 }
// TODO speed it up, see \`oldSpeed()\`
main() {
    println("// TODO not a comment" + one() + two())
}
`;

test('lint sensor reports the four comment rules with guides, and ignores comment-like strings', () => {
  const root = aProject({ 'src/main/kof/Commented.kf': commented });
  assertKofChecks(root, 'src/main/kof/Commented.kf');

  const report = runSensor('lint-sensor.mjs', root, 'src/main/kof/Commented.kf');

  assert.equal(report.code, 1, report.err);
  assert.match(report.out, /^SENSOR lint: FAIL \(4 findings\)/);
  assert.match(report.out, /Commented\.kf:1:1 ERROR long-comment\n {2}This comment is 2 lines\./);
  assert.match(report.out, /Commented\.kf:4:1 ERROR commented-out-code\n {2}This comment is commented-out code/);
  assert.match(report.out, /Commented\.kf:6:1 ERROR deferred-work\n {2}`TODO` marks deferred work/);
  assert.match(report.out, /Commented\.kf:6:1 ERROR stale-comment\n {2}`oldSpeed\(\)` is not in this file/);
  assert.match(report.out, /LONG-COMMENT\n(.*\n)*.*AGENTS\.md/);
  assert.doesNotMatch(report.out, /Commented\.kf:8/);
});
