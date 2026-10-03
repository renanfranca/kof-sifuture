# Kof CI and Pages validation

Date: 2026-10-03. Implementation branch: `kof-ci-and-github-pages`.

## Local behavior validation

Command: `PATH=/tmp/kof-ci-tools:$PATH bash tests/ci-contract.sh`.

The Bash checks exercise the helper's public CLI with JSON responses and executable `gh`/`curl` fixtures. They also parse the actual workflow with `yq` v4.54.1 and execute its test/build command bodies through the existing Python wrapper in a disposable project. They do not run a Python test suite, browser, Playwright or Pillow.

Selected output:

```text
PASS selection follows release and asset pages, publication time and flags
PASS annotated tag resolves to source commit
PASS transferred archive corruption prevents extraction and execution
PASS missing, duplicate, invalid and mismatching checksums fail without fallback
PASS consumers keep the resolved compiler when releases change
PASS actual workflow test command discovers nested suites and preserves each target failure
PASS build errors and missing entry artifacts prevent upload; complete tree survives Pages packaging
PASS main advancement during locked deploy preserves newer final publication; old rerun skips
PASS unsupported Git object cannot be treated as annotated tag
PASS asset download failure prevents bundle publication
PASS impossible calendar dates cannot determine latest release
```

The nested-suite and target-failure cases invoke the real wrapper with a controlled compiler executable: both target commands finish, the failed target retains exit code 19 through `tee`/`pipefail`, and the nested suite is observed in both logs. The failed build returns nonzero and produces no upload outputs; successful exit without entry artifacts is also rejected. Generated nested modules and every asset survive the same tar command used by the pinned Pages upload action.

The deployment-race case uses the actual `check-main` CLI inside a local `flock`, with two processes and FIFO synchronization. `main` advances after the old freshness check; the old publication completes before the newer one acquires the lock. A later old rerun is rejected. This is a controlled model of the declared GitHub concurrency contract, not evidence of GitHub's scheduler or a real Pages deployment. The workflow assertions verify the fixed group, `queue: max`, no running-job cancellation, freshness immediately before deploy, dependencies, producer artifact outputs, explicit checkout SHA and permission boundaries.

## Syntax and expressions

Commands:

```bash
bash -n scripts/kof_ci.sh tests/ci-contract.sh tests/support/gh-fixture tests/support/curl-fixture
shellcheck scripts/kof_ci.sh tests/ci-contract.sh tests/support/gh-fixture tests/support/curl-fixture
sed '/^      queue: max$/d' .github/workflows/kof-ci-and-pages.yml > /tmp/kof-ci-tools/kof-ci-and-pages.yml
actionlint /tmp/kof-ci-tools/kof-ci-and-pages.yml
```

Bash syntax, ShellCheck v0.11.0, YAML parsing and the Actions expression checks passed. The original workflow contains `queue: max`. Actionlint v1.7.12 reports:

```text
unexpected key "queue" for "concurrency" section
```

Only the temporary lint input omits that property. The Bash suite validates it in the original YAML. The [current GitHub documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency) states:

> `max`: Up to 100 jobs or workflow runs can be `pending` in the concurrency group.

This tooling limitation is preserved explicitly; a clean lint of the temporary copy is not presented as acceptance of `queue` by actionlint.

## Official distribution and application checkpoint

The public `resolve` CLI was also run against the real `KofLang/Kof4j` API, including every release/asset page. The public `install` CLI verified the original downloaded archive before extracting it, then checked `VERSION`, `kof version`, executable embedded Java, and `kof info --json` with `embeddedJdk: true`.

Verified selection:

```json
{
  "release_id": 397867596,
  "published_at": "2026-09-28T00:16:08Z",
  "tag": "kof-0.5.0-beta-linux-x86_64",
  "version": "0.5.0-beta",
  "kof_commit": "317d9f6b1c3e27032cc955a05f859f6c627d9338",
  "archive": "kof-0.5.0-beta-linux-x86_64.tar.gz",
  "sha256": "f93f02eb62af584ea49ffb44efdbf54f970bdb9570f16fdc48ccc28242798ca9",
  "sifuture_sha": "efdb29f51cd5761a1f5f6c62e70d7bcf980ba605"
}
```

These local application runs used the worktree based on that SiFuture SHA, with the CI changes present and application sources unchanged. The distribution/launcher came from the helper, not the compiler preinstalled on PATH.

Commands for JVM and JS respectively:

```bash
KOF=/verified/installation/bin/kof python3 scripts/kof_project.py test --target jvm
KOF=/verified/installation/bin/kof python3 scripts/kof_project.py test --target js
```

Both commands returned 0 and ended with:

```text
0 failed of 28 tests
1 passed, 0 failed
```

The [Kof target training](../../../kof/training/reference/targets.md) describes the embedded GraalJS execution. [Learn Kof testing](../../../kof/learn/23-testing.md) explains per-case isolation. The target results above are runtime evidence, rather than compilation-only evidence.

The existing `python3 scripts/kof_project.py build --output DIRECTORY` returned 0 into a new empty directory. The complete output contained 34 files. It was packed with the same `tar` flags as `actions/upload-pages-artifact`, extracted into a separate directory, and compared with `diff -r`; there were no differences. A local HTTP server served the build under `/kof-sifuture/`. Every file was fetched with `curl` and compared byte-for-byte:

```text
HTTP prefix /kof-sifuture/: 34 files matched build bytes
```

This demonstrates package completeness and file access at the repository prefix. It does not demonstrate browser rendering, sprite decoding or game input.

## Design review

The refactor-design rubric was applied to the helper, workflow and local verification contracts after the relevant suite and CLI checkpoint passed. Selection metadata is captured by one producer, consumers verify a transferred bundle, and the freshness lookup intentionally reads current state only inside the deployment slot. The temporary state belongs to a single process invocation; it cannot be reused between concurrent calls. No additional architecture abstraction was justified (classification: no action).

Grouping writes to a single Actions output/summary file was a maintainability opportunity; the applied formatting change preserves the output values. Calendar-date validation was a defect found during review and returned to behavior TDD: a failing CLI case preceded the fix. The full relevant suite passed again afterward.

A generally reusable heuristic was observed: Bash functions called through command substitution must explicitly propagate failed API/parsing assignments; `set -e` alone can be inactive inside that context. The tag-peeling function now propagates failures explicitly. This is a candidate for a separately authorized skill-evolution task; no skill files were modified.

## Production acceptance

The real [PR #7 workflow run](https://github.com/renanfranca/kof-sifuture/actions/runs/37117396903) completed successfully on 2026-10-03. It tested the PR merge revision `2f79c9afc721cdffb98c0d87846b735bf56458b2`, with head implementation commit `90e619157897b791ffea7ef74f3db3515352383e`.

Observed job results:

```text
Resolve verified Kof       success
Kof tests (jvm)            success
Kof tests (js)             success
Build complete Pages site skipped
Publish current main      skipped
```

Both target logs ended with `0 failed of 28 tests` and `1 passed, 0 failed`. Resolver and consumer logs recorded the same Kof commit and archive digest reported above, and the same tested PR merge SHA. The actual artifact inventory was:

```text
kof-37117396903-1
kof-test-jvm-37117396903-1
kof-test-js-37117396903-1
```

There was no Pages artifact. GitHub accepted the workflow containing `queue: max`; actual serialization at deployment still requires a main publication run.

The JVM consumer was then rerun alone with `gh run rerun 37117396903 --job 111187077556`. Attempt 2 succeeded and its actual download step recorded:

```text
name: kof-37117396903-1
Artifact download completed successfully.
0 failed of 28 tests
1 passed, 0 failed
```

Its new log artifact is `kof-test-jvm-37117396903-2`; the bundle remains `kof-37117396903-1`, with the same tested merge revision. No attempt-2 compiler bundle was produced. This confirms real consumer-only reruns use the original producer output instead of guessing the bundle name from the current attempt.

The next commit, `b3a0555ef6ae9e05621b574b6901be5f8d1396a8`, changed only this validation document. Its [workflow run 37117663604](https://github.com/renanfranca/kof-sifuture/actions/runs/37117663604) also succeeded on both targets and skipped both Pages jobs. This demonstrates that a documentation-only update to the PR triggers the complete checks without producing a Pages artifact; a separate PR whose entire diff is documentation-only is additionally covered by the trigger assertions, rather than claimed as a live scenario here.

GitHub Pages was disabled at the initial inspection: `gh api repos/renanfranca/kof-sifuture/pages` returned HTTP 404. The requested Source setting was then enabled through `POST /repos/renanfranca/kof-sifuture/pages` with `build_type=workflow`. A subsequent GET confirmed:

```json
{"build_type":"workflow","html_url":"https://renanfranca.github.io/kof-sifuture/","status":null}
```

At that initial configuration check no site had been deployed. The subsequent merge and publication are recorded below.

## Merge and live publication

After the owner's authorization, PR #7 was merged on 2026-10-03 at 11:51:19 UTC. Published SiFuture SHA: `f812999ebbbabb1677f5b114401ab311cf04fda2`.

The actual [main workflow run 37120979032](https://github.com/renanfranca/kof-sifuture/actions/runs/37120979032) completed with:

```text
Resolve verified Kof       success
Kof tests (jvm)            success
Kof tests (js)             success
Build complete Pages site success
Publish current main      success
```

Resolver, JVM, JS and build all logged the published SiFuture SHA. Both complete target commands again ended with `0 failed of 28 tests` and `1 passed, 0 failed`. The deploy's freshness step recorded:

```text
Current main: f812999ebbbabb1677f5b114401ab311cf04fda2; publication eligible
```

The deployment API identified deployment `6827262269`, environment `github-pages`, and that same SHA. Its latest status at 11:54:35 UTC was:

```json
{"state":"success","environment_url":"https://renanfranca.github.io/kof-sifuture/"}
```

The original `pages-37120979032-1` artifact was downloaded and extracted. Every file in its complete 34-file tree was fetched from the published repository URL with `curl --fail`, compared byte-for-byte with `cmp`, and the complete fetched tree compared with `diff -r`:

```text
Published /kof-sifuture/: 34 files matched Pages artifact bytes
```

This includes `index.html`, `Default.mjs`, its source map, `kof-runtime.mjs`, `kof-runtime-io.mjs`, and all 29 PNG assets. The published entry returned HTTP 200. `Default.mjs` returned HTTP 200 with `content-type: text/javascript; charset=utf-8`. A generated file-digest inventory is retained locally at `.agent/tmp/kof-pages-files-f812999.sha256`, excluded from Git. The commands, workflow link and comparison result above remain the versioned evidence; reading this summary does not require that local file.

## Manual acceptance still pending

Computer Use was attempted through the bundled skill's supported `node_repl` / `@oai/sky` initialization. The first call and the retry after a kernel reset both failed before browser selection:

```text
sandboxCwd is not a local file URI: file:///home/renanfranca/projects/kof-sifuture
```

No browser window was accessed, and no browser/version, visual rendering, image decoding or keyboard/pointer interaction is claimed. The owner was asked to open the published URL and report the browser/version and results for sprites, new game, movement, pause/continue and return to menu after three lives. The game controls remain unchanged.

Remaining evidence:

- Actual workflow target/build/API failure and old-rerun cases, beyond the controlled local checks above.
- Manual browser acceptance: loading, modules/runtimes, sprites, new game, movement, pause/continue and return to menu.
- Browser name/version and deployed SiFuture SHA.

Live publication and byte-for-byte delivery are confirmed. Interactive browser acceptance remains pending.
