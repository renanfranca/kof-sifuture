#!/usr/bin/env bash
set -euo pipefail
project=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
export FIXTURE_ROOT="$work/fixture"
mkdir -p "$FIXTURE_ROOT/downloads" "$work/bin"
cp "$project"/tests/fixtures/kof-ci/*.json "$FIXTURE_ROOT/"
ln -s "$project/tests/support/gh-fixture" "$work/bin/gh"
ln -s "$project/tests/support/curl-fixture" "$work/bin/curl"
export PATH="$work/bin:$PATH"
sha=1111111111111111111111111111111111111111
kof_sha=2222222222222222222222222222222222222222
archive=kof-0.5.0-beta-linux-x86_64.tar.gz
printf 'fixture archive\n' > "$FIXTURE_ROOT/downloads/$archive"
digest=$(sha256sum "$FIXTURE_ROOT/downloads/$archive")
printf '%s\n' "$digest" | sed "s|$FIXTURE_ROOT/downloads/||" > "$FIXTURE_ROOT/downloads/SHA256SUMS"
printf '{"object":{"type":"commit","sha":"%s"}}\n' "$kof_sha" > "$FIXTURE_ROOT/ref.json"
for release in 1 4 5; do
    name=$archive
    [[ "$release" != 1 ]] || name=kof-1.0.0-windows-x86_64.zip
    [[ "$release" != 5 ]] || name=kof-9.0.0-linux-x86_64.tar.gz
    jq -n --arg name "$name" --argjson id "$release" '[{id:($id*10),name:$name,browser_download_url:("https://github.com/KofLang/Kof4j/releases/download/kof-0.5.0-beta-linux-x86_64/"+$name)}]' > "$FIXTURE_ROOT/assets-$release-1.json"
done
jq -n '[{id:41,name:"SHA256SUMS",browser_download_url:"https://github.com/KofLang/Kof4j/releases/download/kof-0.5.0-beta-linux-x86_64/SHA256SUMS"}]' > "$FIXTURE_ROOT/assets-4-2.json"

bash "$project/scripts/kof_ci.sh" resolve "$work/bundle" "$sha" > "$work/resolve.json"

jq -e --arg sha "$sha" --arg kof_sha "$kof_sha" '.release.id == 4 and .version == "0.5.0-beta" and .kof_commit == $kof_sha and .sifuture_sha == $sha and .archive.name == "kof-0.5.0-beta-linux-x86_64.tar.gz"' "$work/bundle/manifest.json" >/dev/null
cmp "$FIXTURE_ROOT/downloads/$archive" "$work/bundle/$archive"
printf 'PASS selection follows release and asset pages, publication time and flags\n'

printf '{"object":{"type":"tag","sha":"3333333333333333333333333333333333333333"}}\n' > "$FIXTURE_ROOT/ref.json"
printf '{"object":{"type":"commit","sha":"%s"}}\n' "$kof_sha" > "$FIXTURE_ROOT/tag.json"

bash "$project/scripts/kof_ci.sh" resolve "$work/annotated" "$sha" > "$work/annotated.json" 2> "$work/annotated.log"

jq -e --arg sha "$kof_sha" '.kof_commit == $sha' "$work/annotated/manifest.json" >/dev/null
printf 'PASS annotated tag resolves to source commit\n'

root="$work/package/kof-0.5.0-beta-linux-x86_64"
mkdir -p "$root/bin" "$root/jdk/bin" "$root/lib"
printf '0.5.0-beta\n' > "$root/VERSION"
printf 'fixture jar\n' > "$root/lib/kof.jar"
cat > "$root/bin/kof" <<'LAUNCHER'
#!/usr/bin/env bash
set -euo pipefail
case "$1" in
    version) printf 'kof 0.5.0-beta\n' ;;
    info) printf '{"kof":"0.5.0-beta","embeddedJdk":true}\n' ;;
    *) exit 1 ;;
esac
LAUNCHER
printf '#!/usr/bin/env bash\nexit 0\n' > "$root/jdk/bin/java"
chmod +x "$root/bin/kof" "$root/jdk/bin/java"
tar -czf "$FIXTURE_ROOT/downloads/$archive" -C "$work/package" "${root##*/}"
digest=$(sha256sum "$FIXTURE_ROOT/downloads/$archive")
printf '%s\n' "$digest" | sed "s|$FIXTURE_ROOT/downloads/||" > "$FIXTURE_ROOT/downloads/SHA256SUMS"
bash "$project/scripts/kof_ci.sh" resolve "$work/install-bundle" "$sha" > "$work/install-resolve.json" 2> "$work/install-resolve.log"
export GITHUB_ENV="$work/github-env"

bash "$project/scripts/kof_ci.sh" install "$work/install-bundle" "$work/installed" "$sha" > "$work/install.json"

jq -e --arg path "$work/installed/${root##*/}/bin/kof" '.kof == $path' "$work/install.json" >/dev/null
[[ $(cat "$GITHUB_ENV") == "KOF=$work/installed/${root##*/}/bin/kof" ]]
[[ -x "$work/installed/${root##*/}/jdk/bin/java" ]]
printf 'PASS verified bundle installs its launcher and embedded JVM\n'

printf '{"object":{"type":"commit","sha":"%s"}}\n' "$sha" > "$FIXTURE_ROOT/main.json"
export GITHUB_OUTPUT="$work/github-output"

bash "$project/scripts/kof_ci.sh" check-main renanfranca/kof-sifuture "$sha" > "$work/current.json"

jq -e '.fresh == true' "$work/current.json" >/dev/null
[[ $(cat "$GITHUB_OUTPUT") == fresh=true ]]
printf 'PASS current main revision permits publication\n'

expect_failure() {
    local diagnostic=$1
    shift
    if "$@" > "$work/rejection.json" 2> "$work/rejection.log"; then
        printf 'Unexpected success: %s\n' "$*" >&2
        exit 1
    fi
    rg -q "$diagnostic" "$work/rejection.log" "$work/rejection.json"
}

printf 'corrupt\n' >> "$work/install-bundle/$archive"

expect_failure 'archive checksum mismatch' bash "$project/scripts/kof_ci.sh" install "$work/install-bundle" "$work/corrupt-install" "$sha"

[[ ! -e "$work/corrupt-install" ]]
printf 'PASS transferred archive corruption prevents extraction and execution\n'
cp "$FIXTURE_ROOT/downloads/$archive" "$work/install-bundle/$archive"
cp "$FIXTURE_ROOT/downloads/SHA256SUMS" "$work/valid-sums"
for problem in missing duplicate invalid mismatch; do
    case "$problem" in
        missing) printf '%064d  other.tar.gz\n' 0 > "$FIXTURE_ROOT/downloads/SHA256SUMS" ;;
        duplicate) cat "$work/valid-sums" "$work/valid-sums" > "$FIXTURE_ROOT/downloads/SHA256SUMS" ;;
        invalid) printf 'not-a-digest  %s\n' "$archive" > "$FIXTURE_ROOT/downloads/SHA256SUMS" ;;
        mismatch) printf '%064d  %s\n' 0 "$archive" > "$FIXTURE_ROOT/downloads/SHA256SUMS" ;;
    esac

    expect_failure 'checksum|capture' bash "$project/scripts/kof_ci.sh" resolve "$work/checksum-$problem" "$sha"

    [[ ! -e "$work/checksum-$problem" ]]
done
cp "$work/valid-sums" "$FIXTURE_ROOT/downloads/SHA256SUMS"
printf 'PASS missing, duplicate, invalid and mismatching checksums fail without fallback\n'

cp "$FIXTURE_ROOT/assets-4-2.json" "$work/valid-checksum-asset"
printf '[]\n' > "$FIXTURE_ROOT/assets-4-2.json"

expect_failure 'missing or ambiguous SHA256SUMS' bash "$project/scripts/kof_ci.sh" resolve "$work/no-checksum" "$sha"

[[ ! -e "$work/no-checksum" ]]
cp "$work/valid-checksum-asset" "$FIXTURE_ROOT/assets-4-2.json"
printf 'PASS newest release missing checksum never falls back\n'

cp "$FIXTURE_ROOT/assets-4-1.json" "$work/valid-archive-asset"
jq '. + [.[0] | .id = 99]' "$work/valid-archive-asset" > "$FIXTURE_ROOT/assets-4-1.json"

expect_failure 'ambiguous Linux' bash "$project/scripts/kof_ci.sh" resolve "$work/ambiguous-archive" "$sha"

cp "$work/valid-archive-asset" "$FIXTURE_ROOT/assets-4-1.json"
printf 'PASS ambiguous distribution rejected\n'

export FAIL_API='repos/KofLang/Kof4j/releases?per_page=100&page=2'

expect_failure '.' bash "$project/scripts/kof_ci.sh" resolve "$work/api-error" "$sha"

unset FAIL_API
printf 'PASS API failure prevents resolution\n'

printf '{"object":{"type":"commit","sha":"%s"}}\n' "$kof_sha" > "$FIXTURE_ROOT/main.json"
: > "$GITHUB_OUTPUT"

bash "$project/scripts/kof_ci.sh" check-main renanfranca/kof-sifuture "$sha" > "$work/stale.json" 2> "$work/stale.log"

jq -e '.fresh == false' "$work/stale.json" >/dev/null
[[ $(cat "$GITHUB_OUTPUT") == fresh=false ]]
rg -q 'Superseded.*publication skipped' "$work/stale.log"
printf 'PASS old execution and old rerun skip publication\n'

printf '{"object":{"type":"commit","sha":"invalid"}}\n' > "$FIXTURE_ROOT/main.json"
: > "$GITHUB_OUTPUT"

expect_failure 'invalid main response' bash "$project/scripts/kof_ci.sh" check-main renanfranca/kof-sifuture "$sha"

[[ ! -s "$GITHUB_OUTPUT" ]]
printf 'PASS malformed freshness response never permits deployment\n'
export FAIL_API='repos/renanfranca/kof-sifuture/git/ref/heads/main'

expect_failure '.' bash "$project/scripts/kof_ci.sh" check-main renanfranca/kof-sifuture "$sha"

[[ ! -s "$GITHUB_OUTPUT" ]]
unset FAIL_API
printf 'PASS freshness API failure never permits deployment\n'

workflow="$project/.github/workflows/kof-ci-and-pages.yml"

[[ -f "$workflow" ]]
yq -o=json '.' "$workflow" > "$work/workflow.json"

jq -e '
    .on == {pull_request:{branches:["main"]},push:{branches:["main"]}} and
    .permissions == {contents:"read"} and
    .jobs.test.strategy == {"fail-fast":false,matrix:{target:["jvm","js"]}} and
    .jobs.test.needs == "resolve-kof" and
    .jobs["build-pages"].needs == ["resolve-kof","test"] and
    .jobs["deploy-pages"].needs == "build-pages" and
    .jobs["deploy-pages"].concurrency == {group:"kof-sifuture-pages", "cancel-in-progress":false,queue:"max"} and
    .jobs["deploy-pages"].permissions == {contents:"read",pages:"write","id-token":"write"} and
    ([.jobs[] | .steps[] | select(has("uses")) | .uses | test("^actions/[a-z-]+@[0-9a-f]{40}$")] | all) and
    ([.jobs[] | .steps[] | select(.uses // "" | startswith("actions/checkout@")) | .with.ref == "${{ github.sha }}"] | all) and
    ([.jobs | to_entries[] | select(.key != "deploy-pages") | .value | has("environment") or has("permissions")] | any | not) and
    ([.jobs[] | .steps[] | .run // "" | test("--suite|Playwright|Pillow|tests/test_|tests/browser")] | any | not)
' "$work/workflow.json" >/dev/null
printf 'PASS documentation PR triggers, independent checks, gating, pins and permissions\n'

cp "$FIXTURE_ROOT/releases-2.json" "$work/releases-before-body.json"
jq 'map(. + {body:("x" * 150000)})' "$work/releases-before-body.json" > "$FIXTURE_ROOT/releases-2.json"

bash "$project/scripts/kof_ci.sh" resolve "$work/large-release-notes" "$sha" > "$work/large-release-notes.json" 2> "$work/large-release-notes.log"

jq -e '.release.id == 4' "$work/large-release-notes/manifest.json" >/dev/null
cp "$work/releases-before-body.json" "$FIXTURE_ROOT/releases-2.json"
printf 'PASS release notes do not limit public release selection\n'

cat "$work/valid-sums" > "$FIXTURE_ROOT/downloads/SHA256SUMS"
printf 'broken\t%s\n' "$archive" >> "$FIXTURE_ROOT/downloads/SHA256SUMS"

expect_failure 'checksum' bash "$project/scripts/kof_ci.sh" resolve "$work/ambiguous-malformed-sums" "$sha"

cp "$work/valid-sums" "$FIXTURE_ROOT/downloads/SHA256SUMS"
printf 'PASS malformed duplicate checksum cannot hide beside a valid entry\n'

cp "$FIXTURE_ROOT/releases-2.json" "$work/valid-releases"
for problem in duplicate-id tied-date invalid-date no-linux; do
    case "$problem" in
        duplicate-id) jq '. + [.[0]]' "$work/valid-releases" > "$FIXTURE_ROOT/releases-2.json" ;;
        tied-date) jq '.[1].published_at = .[0].published_at' "$work/valid-releases" > "$FIXTURE_ROOT/releases-2.json" ;;
        invalid-date) jq '.[0].published_at = "yesterday"' "$work/valid-releases" > "$FIXTURE_ROOT/releases-2.json" ;;
        no-linux) printf '[]\n' > "$FIXTURE_ROOT/releases-2.json" ;;
    esac

    expect_failure 'metadata|ambiguous|time|eligible' bash "$project/scripts/kof_ci.sh" resolve "$work/release-$problem" "$sha"

    [[ ! -e "$work/release-$problem" ]]
done
cp "$work/valid-releases" "$FIXTURE_ROOT/releases-2.json"
printf 'PASS duplicate releases, tied publication, invalid time and no Linux fail closed\n'

cp "$FIXTURE_ROOT/tag.json" "$work/valid-tag"
printf '{"object":{"type":"tag","sha":"3333333333333333333333333333333333333333"}}\n' > "$FIXTURE_ROOT/tag.json"

expect_failure 'cyclic annotated tag' bash "$project/scripts/kof_ci.sh" resolve "$work/cyclic-tag" "$sha"

cp "$work/valid-tag" "$FIXTURE_ROOT/tag.json"
export FAIL_API='repos/KofLang/Kof4j/git/tags/3333333333333333333333333333333333333333'

expect_failure 'GitHub API request failed' bash "$project/scripts/kof_ci.sh" resolve "$work/tag-api-failure" "$sha"

unset FAIL_API
printf 'PASS unresolved or cyclic source tags prevent provenance\n'

requests=$(wc -l < "$FIXTURE_ROOT/requests")
printf '[]\n' > "$FIXTURE_ROOT/releases-1.json"
printf '[]\n' > "$FIXTURE_ROOT/releases-2.json"

bash "$project/scripts/kof_ci.sh" install "$work/install-bundle" "$work/later-install" "$sha" > "$work/later-install.json" 2> "$work/later-install.log"

[[ $(wc -l < "$FIXTURE_ROOT/requests") == "$requests" ]]
jq -e '.kof | endswith("kof-0.5.0-beta-linux-x86_64/bin/kof")' "$work/later-install.json" >/dev/null
printf 'PASS consumers keep the resolved compiler when releases change\n'
cp "$project"/tests/fixtures/kof-ci/*.json "$FIXTURE_ROOT/"

expect_failure 'invalid bundle manifest or SiFuture revision' bash "$project/scripts/kof_ci.sh" install "$work/install-bundle" "$work/wrong-revision" "$kof_sha"

[[ ! -e "$work/wrong-revision" ]]
printf 'PASS bundle from another SiFuture revision cannot be installed\n'

cp "$work/install-bundle/SHA256SUMS" "$work/bundle-valid-sums"
printf '%064d  %s\n' 0 "$archive" > "$work/install-bundle/SHA256SUMS"

expect_failure 'manifest checksum mismatch' bash "$project/scripts/kof_ci.sh" install "$work/install-bundle" "$work/wrong-manifest-digest" "$sha"

cp "$work/bundle-valid-sums" "$work/install-bundle/SHA256SUMS"
printf 'PASS transfer must preserve both checksum and manifest digest\n'

for problem in version launcher jvm; do
    case "$problem" in
        version) printf '9.0.0\n' > "$root/VERSION" ;;
        launcher) sed -i 's/kof 0.5.0-beta/kof 9.0.0/' "$root/bin/kof" ;;
        jvm) sed -i 's/"embeddedJdk":true/"embeddedJdk":false/' "$root/bin/kof" ;;
    esac
    tar -czf "$work/install-bundle/$archive" -C "$work/package" "${root##*/}"
    digest=$(sha256sum "$work/install-bundle/$archive")
    printf '%s\n' "$digest" | sed "s|$work/install-bundle/||" > "$work/install-bundle/SHA256SUMS"
    jq --arg digest "${digest%% *}" '.archive.sha256 = $digest' "$work/install-bundle/manifest.json" > "$work/manifest-next.json"
    cp "$work/manifest-next.json" "$work/install-bundle/manifest.json"

    expect_failure 'VERSION mismatch|launcher version mismatch|embedded JVM' bash "$project/scripts/kof_ci.sh" install "$work/install-bundle" "$work/install-$problem" "$sha"

    [[ ! -e "$work/install-$problem" ]]
    printf '0.5.0-beta\n' > "$root/VERSION"
    sed -i 's/kof 9.0.0/kof 0.5.0-beta/; s/"embeddedJdk":false/"embeddedJdk":true/' "$root/bin/kof"
done
printf 'PASS VERSION, launcher version and actual embedded JVM are checked\n'

jq -e '
    .jobs["build-pages"].if == "${{ github.event_name == '\''push'\'' && github.ref == '\''refs/heads/main'\'' }}" and
    .jobs["deploy-pages"].if == .jobs["build-pages"].if and
    (.jobs["deploy-pages"].steps[-2] | .id == "freshness" and (.run | contains("check-main"))) and
    (.jobs["deploy-pages"].steps[-1] | .if == "${{ steps.freshness.outputs.fresh == '\''true'\'' }}" and
        .with.artifact_name == "${{ needs.build-pages.outputs.artifact-name }}") and
    ([.jobs["deploy-pages"].steps[] | select(.uses // "" | startswith("actions/configure-pages@")) | .with.enablement == false] | all) and
    ([.jobs.test.steps[] | select(has("uses")) | select(.uses | startswith("actions/download-artifact@")) | .with.name == "${{ needs.resolve-kof.outputs.artifact-name }}"] | all) and
    ([.jobs["build-pages"].steps[] | select(has("uses")) | select(.uses | startswith("actions/download-artifact@")) | .with.name == "${{ needs.resolve-kof.outputs.artifact-name }}"] | all) and
    .jobs["resolve-kof"].outputs["artifact-name"] == "${{ steps.bundle.outputs.name }}" and
    .jobs["build-pages"].outputs["artifact-name"] == "${{ steps.build.outputs.name }}" and
    ([.jobs.test.steps[] | has("continue-on-error")] | any | not)
' "$work/workflow.json" >/dev/null
printf 'PASS PR isolation, producer outputs for reruns and freshness immediately before deploy\n'

fixture_project="$work/wrapper-project"
mkdir -p "$fixture_project/scripts"
cp "$project/scripts/kof_project.py" "$fixture_project/scripts/"
cp -r "$project/src" "$fixture_project/src"
cp -r "$project/assets" "$fixture_project/assets"
mkdir -p "$fixture_project/src/test/kof/nested/deeper"
cp "$project/src/test/kof/sifuture/game/GameJourney.kf" "$fixture_project/src/test/kof/nested/deeper/Additional.kf"
cat > "$work/bin/kof-fixture" <<'COMPILER'
#!/usr/bin/env bash
set -euo pipefail
case "$1" in
    test)
        printf '%s %s\n' "$4" "$(cat "$2")" >> "$WRAPPER_LOG"
        [[ "$4" != "${FAIL_TARGET:-}" ]] || exit 19
        ;;
    build)
        [[ "${FAIL_BUILD:-false}" == false ]] || { printf 'fixture compiler build failed\n' >&2; exit 17; }
        [[ "${MISSING_BUILD:-false}" == false ]] || exit 0
        mkdir -p "$6/nested/runtime"
        printf '<script type="module" src="Default.mjs"></script>\n' > "$6/index.html"
        printf 'import "./nested/runtime/engine.mjs";\n' > "$6/Default.mjs"
        printf 'export const sprite="./assets/nave01.png";\n' > "$6/nested/runtime/engine.mjs"
        cp -r "$6" "$EMITTED_TREE"
        ;;
    *) exit 24 ;;
esac
COMPILER
chmod +x "$work/bin/kof-fixture"
export KOF="$work/bin/kof-fixture" WRAPPER_LOG="$work/wrapper.log" EMITTED_TREE="$work/emitted"
test_command=$(yq -r '.jobs.test.steps[] | select(.name == "Run complete Kof suite") | .run' "$workflow")
for failing in jvm js; do
    : > "$WRAPPER_LOG"
    export FAIL_TARGET="$failing"
    failures=0
    for target in jvm js; do
        export TARGET="$target" RUNNER_TEMP="$work"

        if (cd "$fixture_project" && bash -c "$test_command") > "$work/target-$target.log" 2>&1; then
            [[ "$target" != "$failing" ]]
        else
            status=$?
            [[ "$target" == "$failing" && "$status" == 19 ]]
            failures=$((failures + 1))
        fi

        rg -q "^$target import nested.deeper.Additional$" "$WRAPPER_LOG"
        rg -q "^$target import sifuture.game.GameJourney$" "$WRAPPER_LOG"
    done
    [[ "$failures" == 1 ]]
done
unset FAIL_TARGET
printf 'PASS actual workflow test command discovers nested suites and preserves each target failure\n'

build_command=$(yq -r '.jobs["build-pages"].steps[] | select(.id == "build") | .run' "$workflow")
export SIFUTURE_SHA="$sha" PAGES_NAME=fixture-pages GITHUB_STEP_SUMMARY="$work/summary"
for problem in failure missing; do
    export FAIL_BUILD=false MISSING_BUILD=false
    [[ "$problem" != failure ]] || export FAIL_BUILD=true
    [[ "$problem" != missing ]] || export MISSING_BUILD=true
    : > "$GITHUB_OUTPUT"

    expect_failure 'fixture compiler build failed|required artifacts' bash -c "cd '$fixture_project'; $build_command"

    [[ ! -s "$GITHUB_OUTPUT" ]]
done
unset FAIL_BUILD MISSING_BUILD
: > "$GITHUB_OUTPUT"

(cd "$fixture_project" && bash -c "$build_command") > "$work/build.log" 2>&1

output=$(sed -n 's/^path=//p' "$GITHUB_OUTPUT")
[[ -f "$output/index.html" && -f "$output/Default.mjs" && -f "$output/nested/runtime/engine.mjs" ]]
diff -r "$EMITTED_TREE" "$output" > "$work/tree.diff" || [[ $(cat "$work/tree.diff") == 'Only in '*': assets' ]]
diff -r "$fixture_project/assets" "$output/assets"
tar --dereference --hard-dereference --directory "$output" -cf "$work/pages.tar" --exclude=.git --exclude=.github --exclude='.[^/]*' .
mkdir "$work/packaged"
tar -xf "$work/pages.tar" -C "$work/packaged"
diff -r "$output" "$work/packaged"
printf 'PASS build errors and missing entry artifacts prevent upload; complete tree survives Pages packaging\n'

printf '{"object":{"type":"commit","sha":"%s"}}\n' "$sha" > "$FIXTURE_ROOT/main.json"
mkfifo "$work/old-ready" "$work/main-advanced"
(
    flock 9
    bash "$project/scripts/kof_ci.sh" check-main renanfranca/kof-sifuture "$sha" > "$work/old-fresh.json" 2> "$work/old-fresh.log"
    jq -e '.fresh == true' "$work/old-fresh.json" >/dev/null
    printf 'ready\n' > "$work/old-ready"
    read -r advanced < "$work/main-advanced"
    [[ "$advanced" == advanced ]]
    printf '%s\n' "$sha" > "$work/published-sha"
    printf '%s\n' "$sha" >> "$work/deploy-order"
) 9> "$work/deploy-lock" &
old_pid=$!
read -r ready < "$work/old-ready"
[[ "$ready" == ready ]]
printf '{"object":{"type":"commit","sha":"%s"}}\n' "$kof_sha" > "$FIXTURE_ROOT/main.json"
(
    flock 9
    bash "$project/scripts/kof_ci.sh" check-main renanfranca/kof-sifuture "$kof_sha" > "$work/new-fresh.json" 2> "$work/new-fresh.log"
    jq -e '.fresh == true' "$work/new-fresh.json" >/dev/null
    printf '%s\n' "$kof_sha" > "$work/published-sha"
    printf '%s\n' "$kof_sha" >> "$work/deploy-order"
) 9> "$work/deploy-lock" &
new_pid=$!

printf 'advanced\n' > "$work/main-advanced"
wait "$old_pid"
wait "$new_pid"

[[ $(cat "$work/published-sha") == "$kof_sha" ]]
[[ $(cat "$work/deploy-order") == "$sha"$'\n'"$kof_sha" ]]
bash "$project/scripts/kof_ci.sh" check-main renanfranca/kof-sifuture "$sha" > "$work/old-rerun.json" 2> "$work/old-rerun.log"
jq -e '.fresh == false' "$work/old-rerun.json" >/dev/null
[[ $(cat "$work/published-sha") == "$kof_sha" ]]
printf 'PASS main advancement during locked deploy preserves newer final publication; old rerun skips\n'

printf '{"object":{"type":"blob","sha":"%s"}}\n' "$kof_sha" > "$FIXTURE_ROOT/ref.json"

expect_failure 'invalid tag object' bash "$project/scripts/kof_ci.sh" resolve "$work/invalid-tag-type" "$sha"

[[ ! -e "$work/invalid-tag-type" ]]
printf 'PASS unsupported Git object cannot be treated as annotated tag\n'

export FAIL_DOWNLOAD=true

expect_failure '.' bash "$project/scripts/kof_ci.sh" resolve "$work/download-failure" "$sha"

[[ ! -e "$work/download-failure" ]]
unset FAIL_DOWNLOAD
printf 'PASS asset download failure prevents bundle publication\n'

printf '{"object":{"type":"commit","sha":"%s"}}\n' "$kof_sha" > "$FIXTURE_ROOT/ref.json"
jq '.[0].published_at = "2026-09-31T00:00:00Z"' "$FIXTURE_ROOT/releases-2.json" > "$work/impossible-time.json"
cp "$work/impossible-time.json" "$FIXTURE_ROOT/releases-2.json"

expect_failure 'invalid publication time' bash "$project/scripts/kof_ci.sh" resolve "$work/impossible-time" "$sha"

[[ ! -e "$work/impossible-time" ]]
printf 'PASS impossible calendar dates cannot determine latest release\n'
