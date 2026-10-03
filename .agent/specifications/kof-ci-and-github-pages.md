# Kof CI and GitHub Pages publication

- **Status:** Approved specification; implementation and live deployment remain pending.
- **Approval:** The project owner approved the proposal in this conversation on 2026-10-02.
- **Source:** The owner's requirements for automatic Kof tests and GitHub Pages publication.
- **Repository:** `renanfranca/kof-sifuture`.
- **Publication URL:** <https://renanfranca.github.io/kof-sifuture/>.

## Purpose and scope

Every pull request targeting `main` and every push to `main` MUST automatically execute the project's complete Kof test suite on JVM and JS. A push to `main` MUST publish the application to the repository's GitHub Pages address only after both targets and the JS application build succeed, subject to the freshness rules below.

This work covers workflow triggers, official Kof release selection and verified installation, separate test results, application packaging, Pages deployment, deployment ordering, and README instructions for operation and recovery. It MUST preserve the current application, gameplay, source layout, assets, and local command interfaces. Changes to merge protection rules, the game's behavior, or the Kof compiler are outside scope.

This document specifies future implementation. Creating it does not install a workflow, enable Pages, or demonstrate a live deployment.

## Workflow and test contract

The workflow MUST use `pull_request` with `main` as its destination branch and `push` with `main` as its branch. Neither trigger may use file or path filters. Documentation-only and asset-only changes MUST receive the same checks.

For each triggered execution, the workflow MUST run these existing commands from the repository root:

```bash
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
```

Both commands MUST discover all suites in `src/test/kof`; CI MUST NOT select just the currently known suite or use `--suite` to narrow coverage. Adding a suite beneath that directory MUST include it automatically on both targets.

JVM and JS MUST have separately identifiable job/check results and logs. A failure on one target MUST NOT cancel or prevent execution of the other. A matrix implementation MUST disable fail-fast. Test failures MUST remain failures rather than being masked by `continue-on-error` or a successful wrapper command. Shared compiler-resolution or installation failures may prevent tests from starting and MUST fail the workflow.

The only automated test suite in this workflow is the Kof suite. CI MUST NOT install or run Playwright, browsers, Pillow, or Python tests, including `tests/test_kof_project.py` and the browser scripts under `tests/`. Python remains the existing command wrapper; running that wrapper is not running a Python test suite.

Pull requests MUST NOT build a publishable Pages artifact, deploy the application, enter the publication environment, or receive Pages/OIDC publication permissions. The workflow MUST NOT replace `pull_request` with `pull_request_target`.

### Why JS tests do not need a browser

The local [target training reference](/home/renanfranca/projects/kof/training/reference/targets.md:135) states:

> ES Modules 2022+ via embedded GraalJS (KofJsRunner) — no Node.js

The [CLI training reference](/home/renanfranca/projects/kof/training/tooling/cli.md:18) documents `kof test` with `--target jvm|native|js`. [Learn Kof's testing chapter](/home/renanfranca/projects/kof/learn/23-testing.md:42) explains:

> Each test runs **in isolation** (one failing does not interrupt the others).

That isolation concerns cases within a Kof invocation. CI must additionally preserve independence between the two target jobs.

The current [JS branch of `CmdTest.java`](/home/renanfranca/projects/kof/kof-cli/src/main/java/dev/kof/cli/CmdTest.java:153) calls:

```java
                                    code[0] = dev.kof.runtime.KofJsRunner.run(java.nio.file.Path.of(entry),
                                            System.out, System.in, System.err, false, new String[0]);
```

The `false` argument is `openWindow`. In [the runner](/home/renanfranca/projects/kof/kof-runtime/src/main/java/dev/kof/runtime/KofJsRunner.java:75), module execution precedes the optional window path:

```java
            Source source = Source.newBuilder("js", moduleFile.toFile())
                    .mimeType("application/javascript+module")
                    .build();
            KofJsAsyncPump.drainActiveTasks(context, context.eval(source));
            if (openWindow) {
```

The tests execute generated JS inside Kof's embedded engine; they do not automate the published page. Browser rendering and input remain a separate manual acceptance check. These excerpts were inspected in the local Kof checkout at `317d9f6b1c3e27032cc955a05f859f6c627d9338`; they are not a guarantee about unexamined future releases.

### Existing suite discovery and failure propagation

The project wrapper [discovers suites recursively](/home/renanfranca/projects/kof-sifuture/scripts/kof_project.py:129):

```python
    else:
        suites = sorted(tests.rglob("*.kf"))
    if not suites:
        raise PreparationError(f"no Kof suites in {tests}")
    first_failure = 0
    for path in suites:
        print(f"Suite: {path.relative_to(tests)}", flush=True)
        with prepared_sources(suite=path, root=root) as source:
            code = _run([str(kof_executable(kof)), "test", str(source / "Main.kf"), "--target", target])
            if code and not first_failure:
                first_failure = code
    return first_failure
```

`rglob("*.kf")` includes nested suites. The loop continues after a nonzero result and returns the first failure afterward. CI MUST preserve those semantics by invoking the wrapper and respecting its exit status.

## Kof release selection, installation, and provenance

CI MUST resolve exactly one published release from `KofLang/Kof4j` for each workflow execution. The same selected release and official distribution MUST be used for JVM tests, JS tests, and the application build. Downstream jobs MUST consume that selection; they MUST NOT independently query for a newer compiler.

The selection policy is:

1. List published GitHub releases and inspect their assets, following pagination as necessary to establish the latest eligible Linux release. A fixed first-page limit MUST NOT cause an otherwise available Linux release to be missed.
2. Exclude releases with `draft: true` or `prerelease: true`. A `beta`, `alpha`, or `rc` suffix alone MUST NOT exclude a release whose GitHub flags make it eligible.
3. Among releases containing the official `kof-<version>-linux-x86_64.tar.gz` distribution, select the one with the most recent `published_at`. Do not use the globally latest release, tag ordering, or semantic version ordering as a substitute for this policy.
4. Once selected, require that release's distribution and its `SHA256SUMS`. A missing or unusable checksum file MUST fail that selection's installation; it MUST NOT cause fallback to an older release.

Download failures, API failures, malformed or ambiguous selection metadata, no eligible release, unresolved source commit, missing assets, and integrity failures MUST fail the workflow. Retries MAY repeat requests for the same selected release, but MUST NOT silently switch versions.

CI MUST verify the downloaded archive against the checksum entry for its exact filename in that release's `SHA256SUMS` before extraction or execution. Missing, ambiguous, malformed, or mismatching entries MUST fail installation. Downloading a bare CLI JAR, compiling a local Kof checkout, using an unverified cache, or falling back to a preinstalled compiler does not satisfy this contract.

The official distribution MUST supply the compiler, runtimes, launcher, and embedded JVM. The workflow MUST ensure the existing wrapper uses that launcher, through its existing `KOF` environment variable or PATH selection. Cached or transferred distributions MAY be reused only when their identity and verified archive digest match the single selection.

The wrapper's [existing compiler selection](/home/renanfranca/projects/kof-sifuture/scripts/kof_project.py:29) is:

```python
def kof_executable(override=None):
    return override or os.environ.get("KOF") or shutil.which("kof") or "kof"
```

An explicit executable takes precedence over `KOF`, which takes precedence over PATH lookup. CI can therefore select the verified distribution without changing the local command interface.

The [distribution training reference](/home/renanfranca/projects/kof/training/distribution/install.md:21) records:

> Artifacts: `kof-<version>-<system>.tar.gz` (Linux/macOS) or `.zip`
> (Windows), accompanied by `SHA256SUMS`.

The archive and checksum belong to the selected release. Their filenames and integrity, rather than a machine's existing `kof`, establish which distribution CI is using.

Logs and the execution summary MUST record the Kof version, selected release tag, full Kof source commit SHA, archive identity and verified SHA-256 digest, and full SiFuture SHA actually checked out and tested/built. Resolve the release tag to its source commit, peeling an annotated tag when necessary. A moving branch name in `target_commitish` alone is insufficient provenance. Failure to establish the source commit MUST fail the workflow.

The version MUST be checked against the installed distribution. Main publication MUST use the exact SiFuture push commit that passed both test targets; PR provenance MUST identify the revision actually tested.

## Main build and complete Pages package

Only a `push` to `refs/heads/main` is eligible for publication. After both target checks succeed, CI MUST invoke the existing application build in a fresh output directory:

```bash
python3 scripts/kof_project.py build --output DIRECTORY
```

`DIRECTORY` denotes a new, empty directory for that execution, not a literal directory name or an existing output from another run. The build MUST use the same selected Kof distribution as the tests. CI MUST propagate build failures and MUST NOT upload partial or stale output as a Pages artifact.

The complete successful output MUST be packaged: `index.html`, all generated application modules, all emitted Kof runtime files, and all assets. Relative paths MUST remain valid under `/kof-sifuture/`, including nested module imports and sprite URLs. The output directory's contents belong at the Pages artifact root; adding an extra `kof-sifuture` directory would duplicate the repository path. CI MUST NOT replace the existing build with a handwritten JS/CSS application, edit generated modules to change behavior, or upload only HTML and one entry module.

The existing [build checks required artifacts before copying output](/home/renanfranca/projects/kof-sifuture/scripts/kof_project.py:108):

```python
            missing = [item for item in ("index.html", "Default.mjs") if not (web / item).is_file()]
            if missing:
                raise PreparationError(f"Kof build returned success without required artifacts: {', '.join(missing)}")
            _publish(web, output)
```

The [copy operation preserves relative paths](/home/renanfranca/projects/kof-sifuture/scripts/kof_project.py:92):

```python
    for path in sorted(source.rglob("*")):
        if path.is_file():
            target = output / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
```

These checks establish that the existing entry artifacts are present and that generated files are copied without flattening their paths. They do not by themselves prove that every browser request or interaction succeeds. The wrapper also [copies project assets](/home/renanfranca/projects/kof-sifuture/scripts/kof_project.py:112):

```python
            if assets is None:
                assets = (root / "assets").glob("*")
            destination = Path(output) / "assets"
            destination.mkdir(exist_ok=True)
            for asset in assets:
                shutil.copyfile(asset, destination / Path(asset).name)
```

The destination preserves the generated application's relative `assets/` URLs. The [Learn Kof JS chapter](/home/renanfranca/projects/kof/learn/37-kofjs.md:54) describes the deployment model:

> `kof build --target=js` generates `index.html` + modules: serve the
> folder as a static web application (any HTTP server).

## Pages permissions and deployment ordering

Publication MUST use the official `actions/configure-pages`, `actions/upload-pages-artifact`, and `actions/deploy-pages` actions, following the [official custom-workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). The deploy job MUST explicitly depend on the successful build and uploaded artifact. It MUST use the `github-pages` environment and expose the deployment URL.

Only the publication job may receive `pages: write` and `id-token: write`; these permissions MUST NOT appear as workflow-wide grants or on resolution, test, or build jobs. Non-publication jobs MUST use read-only repository access. Pull requests MUST never execute the privileged publication job. Pages configuration MUST be arranged within these permission boundaries.

The [GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) requires:

> An `environment` must be established to enforce branch/deployment protection rules. The default environment is `github-pages`.

The environment requirement does not authorize changing this repository's merge protection rules.

All Pages deployments for this repository MUST share a serialization boundary. Superseded executions MAY skip publication or be canceled. The policy MUST prioritize the latest `main` commit rather than assuming jobs finish or enter the deployment queue in commit order.

After obtaining its serialized deployment slot and immediately before calling `deploy-pages`, the publication job MUST query the authoritative current `main` SHA and compare it with the tested and built SiFuture SHA. A mismatch MUST skip deployment with an explicit superseded-run diagnostic. Failure to query or validate freshness MUST fail closed without deploying.

The slot MUST remain held until deployment finishes. An older execution that completes its build late, waits in the queue, or is manually rerun MUST NOT replace a newer published version. If `main` advances after the freshness check, the serialization boundary MUST still prevent that older deployment from finishing after and replacing a newer publication. Serialization and the freshness check are both required; neither substitutes for the other. GitHub's [concurrency documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency) warns:

> ordering is not guaranteed.

## Failure, diagnosis, and recovery

A selection, download, integrity, installation, test, or build failure MUST produce an unsuccessful workflow and prevent publication. Such failures MUST leave the currently published site in place. A superseded execution is a publication skip, not a test or integrity success; its actual target results MUST remain visible. Deployment failures MUST remain visible and MUST NOT be reported as successful publication.

The README MUST document:

- the two triggers, separately reported target checks, single-release policy, published URL, and absence of browser/Python tests from this CI;
- enabling Pages with **Settings → Pages → Source: GitHub Actions** before live publication;
- locating the selected Kof version/tag/source SHA, SiFuture SHA, checksum verification, target failure, build failure, and deploy/freshness diagnostic in Actions logs and summaries;
- reproducing Kof tests and the build using the unchanged local commands and, when needed, selecting the recorded compiler with the existing `KOF` or `--kof` interface;
- re-running a failed execution through GitHub Actions after correcting the cause, recognizing that an obsolete `main` execution will skip publication, and validating the current `main` execution instead;
- checking the published page manually and distinguishing file availability from visual or interaction validation.

Re-running MUST NOT bypass tests, verification, build dependencies, permissions, serialization, or freshness checks. The README MUST explain that these failures preserve the existing site rather than publishing incomplete output.

## Evidence and external prerequisite

Repository and release inspection for this specification used SiFuture commit `fd1991b81f208fea6ded638ade376a4a368a2685` and the local Kof checkout at `317d9f6b1c3e27032cc955a05f859f6c627d9338` on 2026-10-02. These are investigation snapshots, not CI version pins.

The approved proposal reports that both existing Kof test commands passed with Linux Kof `0.5.0-beta`. Each target produced:

```text
0 failed of 28 tests
1 passed, 0 failed
```

It also reports a build containing 34 files and HTTP 200 responses for HTML, modules, and assets when served beneath `/kof-sifuture/`. Those are prior investigation results supplied with the proposal; the commands were not rerun while writing this specification. The file count is evidence for that snapshot, not a required fixed count for future builds. These results support test execution, packaging, and file access; they do not prove browser rendering, input, or gameplay interaction.

The GitHub API was queried again during specification research with:

```bash
gh api 'repos/KofLang/Kof4j/releases?per_page=100' --jq 'sort_by(.published_at) | reverse | .[:2] | .[] | {tag_name,draft,prerelease,published_at,target_commitish,assets:[.assets[].name]}'
```

The two most recently published releases in that response were:

```jsonl
{"assets":["kof-0.5.0-beta-windows-x86_64.zip","kof-cli-0.5.0-beta.jar","SHA256SUMS"],"draft":false,"prerelease":false,"published_at":"2026-09-28T00:17:06Z","tag_name":"kof-0.5.0-beta-windows-x86_64","target_commitish":"317d9f6b1c3e27032cc955a05f859f6c627d9338"}
{"assets":["kof-0.5.0-beta-linux-x86_64.tar.gz","kof-cli-0.5.0-beta.jar","SHA256SUMS"],"draft":false,"prerelease":false,"published_at":"2026-09-28T00:16:08Z","tag_name":"kof-0.5.0-beta-linux-x86_64","target_commitish":"317d9f6b1c3e27032cc955a05f859f6c627d9338"}
```

The later Windows publication explains why a globally latest release is unsuitable for Linux selection. The Linux release's `prerelease: false`, despite `beta` in its tag, confirms the need to inspect GitHub flags. This two-entry display is investigation evidence only, not the required pagination strategy for the implementation.

Pages is not yet enabled. On 2026-10-02, this read-only query returned:

```bash
gh api repos/renanfranca/kof-sifuture --jq '{has_pages}'
```

```json
{"has_pages":false}
```

Enabling Pages with **Source: GitHub Actions** is an external prerequisite for live deployment acceptance. The [official publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) describe that setting. Until it is enabled and deployment is exercised, the implementation MUST NOT claim the published site has been validated.

## Acceptance scenarios

| Scenario | Required observable result |
| --- | --- |
| PR targets `main`, including a documentation-only change | JVM and JS run as separate checks over all `src/test/kof` suites; no Playwright, browsers, Pillow, Python tests, Pages artifact, publication, or publication permissions. |
| A suite is added in a nested test directory | Both existing target commands discover and execute it without a workflow allowlist change. |
| JVM fails while JS can run, or JS fails while JVM can run | Both target results remain available; the failure is propagated; publication is prevented. |
| Push to `main` succeeds | Both targets pass before the fresh JS build; the complete build artifact is uploaded; the eligible serialized deploy publishes at the repository URL using `github-pages`. |
| Globally newest release is for another platform | Selection still finds the most recently published eligible Linux x86_64 distribution. |
| Newer draft or GitHub prerelease exists; eligible tag contains `beta` | Drafts and GitHub prereleases are excluded; the suffix alone does not disqualify the eligible release. |
| Linux release is beyond the first API page | Selection finds it through pagination rather than silently using an unsuitable version or claiming it is absent. |
| Selection/download fails, checksum is missing or mismatches, or installation/provenance validation fails | The workflow fails; no fallback compiler or deployment is used; the existing site remains. |
| Main build fails or required artifacts are missing | The workflow fails without uploading deployable partial/stale output; the existing site remains. |
| Releases change while a workflow is running | JVM, JS, and build still use that execution's single resolved, verified Kof release; logs identify it. |
| An old build finishes or is rerun after a newer `main` publication | The old execution cannot replace the newer site; the serialized freshness check rejects the obsolete SHA. |
| Freshness lookup fails | The workflow fails without deploying; uncertainty does not count as permission to publish. |
| Published site is checked manually | The page opens at `https://renanfranca.github.io/kof-sifuture/`; generated modules, runtimes, and sprites load; the current application renders and its normal controls can be exercised. |

Implementation validation MUST retain evidence for trigger behavior, separate target failures, release selection and integrity failures, build gating, permission boundaries, and out-of-order publication. Controlled fixtures MAY exercise release ordering and failure conditions; passing a happy-path run alone is insufficient. The visual check MUST be performed manually, with the deployed SiFuture SHA and browser recorded. Automated browser testing MUST NOT be introduced into this CI to satisfy that check.

## Explicit exclusions

Gameplay changes, completion of the broader SiFuture port, merge protection changes, browser/Python test jobs, global-latest release selection, independent compiler selection per job, unverified distributions, silent version fallback, incomplete Pages packages, publication from PRs, and deploying without a serialized freshness check are outside this approved contract.
