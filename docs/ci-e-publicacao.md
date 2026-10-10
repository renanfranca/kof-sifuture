<a id="ci-e-publicação"></a>

# CI and publishing

[English](ci-e-publicacao.md) | [Português (Brasil) — pt-BR](ci-e-publicacao.pt_BR.md)

**CI** means continuous integration: automated checks applied to incoming
changes. Publishing delivers the site approved by the workflow.

[Back to the project overview](../README.md) ·
[Local development](desenvolvimento.md) ·
[How to play](jogar.md)

This guide covers distribution, checks, site builds, and recovery when a step
fails. Follow runs in GitHub through the [configured workflow](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml).

<a id="revisão-e-artefatos"></a>

## Revisions and artifacts

A **revision** is a repository state identified by its commit. A **SHA** is
the full commit identifier used in the records below. An **artifact** is a set
of files saved by a run for another step to consume or to reproduce delivery.
A **job** is one step in the GitHub Actions workflow. A **workflow** describes
the process; dependencies between jobs determine which results must pass
before the next step.

## Checks

A **check** is the visible result of verifying a revision. In this workflow,
rules tests have one check for JVM and another for JS.

The [Kof CI and GitHub Pages workflow](../.github/workflows/kof-ci-and-pages.yml)
runs for every **PR targeting `main`** and every **push to `main`**, including
changes only to documentation or assets. The **Kof tests (jvm)** and **Kof
tests (js)** checks separately run the full command
`python3 scripts/kof_project.py test --target ALVO`. The matrix uses
`fail-fast: false`: failure on one target does not cancel the other, and blocks
the build and publishing. Recursive discovery includes new nested suites.
This CI runs only Kof suites; Python is the existing wrapper. It does not
install or run Python tests, Playwright, browsers, or Pillow.

JS tests use the embedded engine, according to the [Kof target training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/reference/targets.md#L135):

> ES Modules 2022+ via embedded GraalJS (KofJsRunner) — no Node.js

[Learn Kof's testing chapter](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/23-testing.md#L42)
records:

> Each test runs **in isolation** (one failing does not interrupt the others).

That rule applies to cases within one Kof invocation. The workflow matrix also
keeps JVM and JS independent. Neither proves that the published browser UI
works.

<a id="uma-distribuição-por-resolução"></a>

## One distribution per resolution

[`scripts/kof_ci.sh`](../scripts/kof_ci.sh) is a Bash helper with three
operations. It requires Bash, authenticated `gh`, `jq`, `curl`, `sha256sum`,
and `tar`.

- `resolve BUNDLE SHA`: scans all pages of releases and assets for `KofLang/Kof4j`, excludes `draft: true` and `prerelease: true`, and chooses the official Linux x86_64 file with the latest `published_at`. A `beta` suffix does not exclude an otherwise eligible release. It requires its `SHA256SUMS`, exactly one valid entry for the file name, the correct digest, and a tag resolved to a commit, including annotated tags. Errors and ambiguity stop the run without falling back to another compiler.
- `install BUNDLE DIRETORIO SHA`: validates the SiFuture revision in the manifest, rechecks the checksum and digest, extracts into a new directory, and validates `VERSION`, `kof version`, and the embedded JVM. In Actions it writes `KOF` to `GITHUB_ENV`; locally it returns JSON with the launcher path.
- `check-main OWNER/REPOSITORY SHA`: queries the current `main` commit and returns `fresh: true` or `false`. A superseded SHA produces an explicit diagnostic and skips publishing. API failures or invalid responses return an error; they never authorize deployment.

The distribution is complete, according to the [installation training](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/distribution/install.md#L13):

> The official package contains: compiler, CLI, runtime, stdlib, tooling, editor
> support, embedded OpenJDK and documentation.

CI therefore installs the official package and requires its embedded JVM,
using its launcher through `KOF`. It does not use a standalone JAR, a build of
the Kof checkout, or a compiler cache. The producer job transfers the original
file, `SHA256SUMS`, and `manifest.json` in `kof-RUN_ID-TENTATIVA`. Tests and the
build download the name supplied by that producer's output; they do not query
releases again.

The manifest, logs, and summaries record the version, release and tag, full
Kof commit, file ID/name/URL, verified SHA-256, and full SiFuture SHA. All
checkouts explicitly use `github.sha`; on a PR, that is the merge revision
tested by the event. Logs for each target and the build are available in their
jobs and separate artifacts, retained for 30 days.

<a id="atualização-do-site"></a>

## Site updates

The official site is **[Play SiFuture](https://renanfranca.github.io/kof-sifuture/)**.
Each merge into `main` starts the workflow. When tests, build, and publishing
succeed for the current revision, it updates this same address. The URL stays
the same; its content is updated.

A merge creates a push to `main`, which the workflow watches. The
[build](../.github/workflows/kof-ci-and-pages.yml#L94) requires passing tests:

```yaml
  build-pages:
    name: Build complete Pages site
    if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    needs: [resolve-kof, test]
```

`needs` makes the build wait for the distribution and both test targets. The
[publishing job](../.github/workflows/kof-ci-and-pages.yml#L148) depends on
the build:

```yaml
  deploy-pages:
    name: Publish current main
    if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    needs: build-pages
```

Before publishing, [check-main](../scripts/kof_ci.sh#L185) compares the revision:

```bash
if [[ "$current" == "$tested_sha" ]]; then
    fresh=true
    printf 'Current main: %s; publication eligible\n' "$tested_sha" >&2
else
    printf 'Superseded: tested %s; current main %s; publication skipped\n' "$tested_sha" "$current" >&2
fi
```

Only `fresh=true` authorizes deployment. If another commit has advanced
`main`, the superseded run skips publishing. A merge starts the workflow, but
it does not promise that every intermediate revision will replace the site.

Before the first publication, enable **Settings → Pages → Source: GitHub
Actions**. The workflow uses `actions/configure-pages` with `enablement: false`:
if Pages is disabled, deployment fails and must be fixed in repository
settings. The official address is
[https://renanfranca.github.io/kof-sifuture/](https://renanfranca.github.io/kof-sifuture/).

Only a push to `main`, after both checks pass, runs the existing build in a
new, empty directory. `actions/upload-pages-artifact` receives the entire
output root: HTML, modules, runtimes, and assets keep their relative paths.
There is no extra `kof-sifuture` directory inside the package; `/kof-sifuture/`
is part of the Pages URL. [Learn Kof JS](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/37-kofjs.md#L54)
describes this model:

> `kof build --target=js` generates `index.html` + modules: serve the
> folder as a static web application (any HTTP server).

Common jobs have only `contents: read`. Only deployment gets `pages: write`
and `id-token: write`, enters the `github-pages` environment, and exposes the
published URL. PRs do not enter this environment or produce a Pages artifact.

The full deployment keeps the fixed concurrency group `kof-sifuture-pages`,
with `cancel-in-progress: false` and `queue: max`. Within that group,
`check-main` compares the built SHA with current `main` immediately before
`actions/deploy-pages`. GitHub's [concurrency documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
explains that the queue follows arrival at exclusivity, which may differ from
commit order. Thus, an older build that finishes later or is rerun skips
publishing. If `main` advances during a deploy already in progress, the
exclusive run continues until it finishes; the newer publication waits and
the old one cannot overwrite it at the end.

<a id="diagnóstico-reprodução-e-reexecução"></a>

## Diagnosis, reproduction, and reruns

First consult **Resolve verified Kof** for API, selection, tag, and integrity
errors; then the target check for installation/tests, **Build complete Pages
site** for the build and artifact, and **Publish current main** for Pages,
freshness, and deployment. Failures before deployment preserve the existing
site. Deployment failures remain visible and are not recorded as successful
publication.

<a id="reproduzir-uma-distribuição"></a>

### Reproduce a distribution

To reproduce the exact selected distribution, download the `kof-...` artifact
named by the producer job, extract its contents to a directory, and use the
manifest SHA:

```bash
bundle=/caminho/para/bundle
sha=$(jq -r .sifuture_sha "$bundle/manifest.json")
scratch=$(mktemp -d)
installation=$(bash scripts/kof_ci.sh install "$bundle" "$scratch/installation" "$sha")
export KOF=$(jq -r .kof <<< "$installation")
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 scripts/kof_project.py build --output "$scratch/site"
```

Run these commands in a checkout of the same SHA. Alternatively, pass
`--kof "$KOF"` to the existing commands. To resolve a new distribution
locally, run `bash scripts/kof_ci.sh resolve "$scratch/bundle" "$(git rev-parse HEAD)"`;
the destination must not already exist. Local resolution also requires
authenticated GitHub read access.

<a id="reexecutar-jobs"></a>

### Rerun jobs

**Re-run failed jobs** reuses outputs from successful producers, including the
original bundle or Pages package name; the consumer does not calculate a name
from its new attempt. **Re-run all jobs** performs a new resolution and repeats
tests and build with it. If artifacts have expired, rerun all jobs; do not
manually replace the compiler. Rerunning an old deployment does not restore
an old site: `main` still has to be updated.

<a id="verificações-locais-de-infraestrutura"></a>

### Local infrastructure checks

Local publishing-infrastructure checks live in [`tests/ci-contract.sh`](../tests/ci-contract.sh),
with JSON fixtures and Bash executables for APIs and downloads. Run
`bash tests/ci-contract.sh` with `yq` v4 available. They are not part of the
workflow. The [validation record](../.agent/validation/kof-ci-and-pages.md)
distinguishes local simulations, real compiler runs, and production gaps.

Acceptance of a published revision must identify the run, SHA, and browser,
and check loading, modules/runtimes, sprites, start, movement, pause/resume,
and return. Automation and manual acceptance should be recorded separately.
The public results already documented below belong to the revisions named;
they do not automatically validate a later publication.

<a id="evidência-da-revisão-publicada"></a>

## Published revision evidence

The [initial CI record](../.agent/validation/kof-ci-and-pages.md) associates
tests and the first publication on 2026-10-03 with SHA
`f812999ebbbabb1677f5b114401ab311cf04fda2`, comparing 34 files. Interactive
acceptance remained pending in that record. That gap does not erase browser
evidence obtained later on other revisions.

The [boss record](../.agent/validation/boss-pages-publication.md) documents
`81d420afe8020cdae4e4468882da7002310298e2` on 2026-10-06: 109 files compared
and Chrome 139.0.7258.154 at the real URL at 320/1200 px. The full combat was
checked with the local fixture; it is not attributed to the remote review of
that publication.

The [credits record](../.agent/validation/controls-guide.md) documents
`e649066885e3b3fd6513bebf8629c29d46f835b3` on 2026-10-08 and the command
`python3 tests/browser.py https://renanfranca.github.io/kof-sifuture/`, which
exited zero. Chrome 139.0.7258.154 checked opening, text, guide, and navigation
at 320/1200 px and densities 1/2. The deterministic result scenario used a
fixture served locally by the same script.

On 2026-10-09, [workflow run 37949665153](https://github.com/renanfranca/kof-sifuture/actions/runs/37949665153)
published `5609febbc76cc2dd5d0f52c90349dae3ef1f5057`. The [controls record](../.agent/validation/sifuture-controls.md)
preserves the result:

```text
PASS published Pages matches CI artifact: 113 files
```

This comparison checks the HTML, module/runtime, and asset bytes against that
run's artifact. The record also describes the public menu journey in Chrome
155.0.8059.39 at 320/1200 px: composition, font, position, hover/focus,
selection, start, and pause, including under a native color imposed by the
test. The user's manual “Resolved” report closes the specific menu receiver
issue; it is not an automated Windows test.

Each kind of evidence has limits. CI JS tests use the embedded engine; they do
not open a browser. An HTTP 200 or file comparison does not prove interaction.
A public automated journey does not replace pending human visual approval for
another revision or presentation, nor acceptance on a physical Android device.
Tracked summaries should explain the evidence without requiring logs and
captures in `.agent/tmp/`.
