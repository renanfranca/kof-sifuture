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

GitHub Pages was disabled at the initial inspection: `gh api repos/renanfranca/kof-sifuture/pages` returned HTTP 404. The requested Source setting was then enabled through `POST /repos/renanfranca/kof-sifuture/pages` with `build_type=workflow`. A subsequent GET confirmed:

```json
{"build_type":"workflow","html_url":"https://renanfranca.github.io/kof-sifuture/","status":null}
```

Pages is configured for GitHub Actions, but no site has been deployed. Production acceptance still requires merging the reviewed workflow to `main` and exercising publication.

Pending evidence:

- GitHub checks after a documentation-only PR update.
- Successful push-to-main JVM/JS jobs, build, artifact upload and serialized Pages deployment.
- Actual workflow target/build/API failure and old-rerun cases, beyond the controlled local checks above.
- Published URL: <https://renanfranca.github.io/kof-sifuture/>.
- Manual browser acceptance: loading, modules/runtimes, sprites, new game, movement, pause/continue and return to menu.
- Browser name/version and deployed SiFuture SHA.

No live publication or manual browser acceptance is claimed by this local record.
