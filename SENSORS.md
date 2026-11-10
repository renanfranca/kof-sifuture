# Quality sensors

The cheap sensors of this project report in one format,
`SENSOR <name>: PASS|FAIL|SKIP|UNAVAILABLE`, followed by each finding as
`file:line[:column] ERROR <rule>` and a guide for the rule. They are adapted
from Katacombs (see [NOTICE](NOTICE)). Kof is read with the official lexer and
parser of the installed distribution through
[scripts/kof-sensors](scripts/kof-sensors/README.md); no second grammar exists.

Requirements: Node 24, Python 3, Java 25, Maven 3.9, Gitleaks 8.30.1, and
`kof` and `kof-mut` on `PATH`. `npm run sensors:doctor` shows the versions and
paths it finds; it does not certify quality.

## Commands

```bash
npm run lint:sensor      # structural, test and comment rules on .kf files changed against main
npm run dup:sensor       # PMD CPD 7.17.0 on the same files, except test code (50 tokens, 5 lines)
npm run secret:sensor    # Gitleaks on the files Git would publish
npm run docs:sensor      # npm scripts named in Markdown exist; relative links resolve
npm run sensors:debt     # all rules on every .kf file, report only (exit 0)
npm run sensors:doctor   # tools, versions and command files
npm run check            # the full gate, in order, stopping at the first failure
npm run check:task       # check, then the seven browser journeys
npm run test:sensors     # behaviour tests of these commands
```

`lint:sensor` and `dup:sensor` accept explicit paths, for example
`npm run lint:sensor -- src/main/kof/sifuture/game/Meteor.kf`. Without paths
they analyse whole files changed against `main`, new ones included; with none
they print SKIP. A file that cannot be read or tokenized makes the sensor
UNAVAILABLE, never PASS. No suppression comments or baselines exist.

`check` runs `secret:sensor`, the JVM and JS type checks, the Python tests, the
Kof tests on JVM and JS, `lint:sensor`, `dup:sensor`, `docs:sensor` and then
mutation. Mutation runs KofMut with `kof-mut.json` on the production `.kf` files
changed against `main`; without such a file it prints SKIP and claims nothing.
KofMut exit 1 (a survivor) or 2 fails the check. On exit 3 the check reads the
report announced on the `reportPath=` line: `no_mutants` without limitations
prints SKIP, which, like the case without changed files, approves nothing;
`incomplete`, `no_scope`, a report that contradicts exit 3, or one that cannot
be read fails the check.

## Rules and limits

| Rule | Finding |
| --- | --- |
| `long-file` | more than 150 non-blank lines; more than 1000 in test code (`src/test/kof/` and `tests/`) |
| `long-function` | more than 25 lines (not in `src/test/kof/`) |
| `high-complexity` | complexity above 10 |
| `too-many-parameters` | more than 4 parameters |
| `deep-nesting` | nesting deeper than 2 |
| `too-many-statements` | more than 17 statements (not in `src/test/kof/`) |
| `duplicated-code` | a CPD clone of at least 50 tokens and 5 lines (test code is not analysed) |
| `assertion-free-test` | a `test` block with no `assert` or assertion call |
| `branching-test` | `if`, if-expression or `switch` inside a test |
| `looping-test` | a loop inside a test; use `testRows` for case tables |
| `unnamed-arrange` | more than 8 statements before the first assertion |
| `mystery-guest` | `setup`, `beforeEach` or `beforeAll` assigning shared state |
| `long-comment` | a comment longer than one line |
| `stale-comment` | a backticked name or path that is not there |
| `commented-out-code` | a comment the Kof parser accepts as code |
| `deferred-work` | `todo`, `fixme`, `xxx` or `hack` in a comment |
| `leaked-secret` | any Gitleaks rule |
| `stale-doc` | `missing-script` or `broken-link` in tracked Markdown |

The limits and their calibration are recorded in
[sensor-calibration.md](.agent/validation/sensor-calibration.md). The test code
limits were decided on 07/11/2026: tests favour readable repetition, so CPD
skips them and their file limit only warns about giant files. The comment
rules do not relax [AGENTS.md](AGENTS.md), which allows no explanatory comments
in source code at all.
