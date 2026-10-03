#!/usr/bin/env bash
set -euo pipefail

fail() {
    printf 'kof-ci: %s\n' "$*" >&2
    exit 1
}

require_sha() {
    [[ "$1" =~ ^[0-9a-f]{40}$ ]] || fail 'invalid commit SHA'
}

api() {
    gh api -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2022-11-28' "$1" || fail "GitHub API request failed: $1"
}

pages() {
    local endpoint=$1 output=$2 page=1
    : > "$output"
    while :; do
        api "$endpoint?per_page=100&page=$page" > "$temporary/page.json"
        jq -e 'type == "array"' "$temporary/page.json" >/dev/null || fail 'API page is not an array'
        [[ $(jq length "$temporary/page.json") != 0 ]] || break
        jq -c '.[]' "$temporary/page.json" >> "$output"
        page=$((page + 1))
    done
    jq -s '.' "$output" > "$output.json"
}

checksum() {
    local sums=$1 name=$2
    jq -Rrs --arg name "$name" '
        split("\n") | map(select(length > 0)) |
        map(select(([splits("[ \t]+")] | last | ltrimstr("*")) == $name)) |
        if length != 1 then error("missing or duplicate checksum entry") else .[0] end |
        capture("^(?<digest>[0-9A-Fa-f]{64}) [ *](?<name>[^\\r\\n]+)$") |
        if .name != $name then error("invalid checksum filename") else .digest | ascii_downcase end
    ' "$sums"
}

verify_archive() {
    local path=$1 expected=$2 actual
    actual=$(sha256sum "$path")
    [[ "${actual%% *}" == "$expected" ]] || fail "archive checksum mismatch: ${path##*/}"
}

source_commit() {
    local tag=$1 object type sha seen=' '
    tag=$(jq -rn --arg tag "$tag" '$tag | @uri')
    object=$(api "repos/KofLang/Kof4j/git/ref/tags/$tag") || return "$?"
    while :; do
        type=$(jq -er '.object.type | select(. == "commit" or . == "tag")' <<< "$object") || fail 'invalid tag object type'
        sha=$(jq -er '.object.sha' <<< "$object") || fail 'invalid tag object SHA'
        require_sha "$sha"
        [[ "$seen" != *" $sha "* ]] || fail 'cyclic annotated tag'
        seen+="$sha "
        if [[ "$type" == commit ]]; then
            printf '%s\n' "$sha"
            return
        fi
        object=$(api "repos/KofLang/Kof4j/git/tags/$sha") || return "$?"
    done
}

report() {
    local manifest=$1
    printf 'Verified Kof provenance:\n' >&2
    jq . "$manifest" >&2
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
        {
            printf '### Verified Kof provenance\n\n```json\n'
            jq . "$manifest"
            printf '```\n'
        } >> "$GITHUB_STEP_SUMMARY"
    fi
}

resolve() {
    local destination=$1 sifuture_sha=$2 release assets selected name url version commit digest
    require_sha "$sifuture_sha"
    [[ ! -e "$destination" ]] || fail 'resolve destination already exists'
    pages 'repos/KofLang/Kof4j/releases' "$temporary/releases"
    jq -e '
        def positive_id: type == "number" and . > 0 and floor == .;
        all(.[]; (.id | positive_id) and (.draft | type == "boolean") and
            (.prerelease | type == "boolean") and (.tag_name | type == "string" and length > 0) and
            (.published_at == null or (.published_at | type == "string"))) and
        ([.[].id] | length == (unique | length))
    ' "$temporary/releases.json" >/dev/null || fail 'invalid or duplicate release metadata'
    : > "$temporary/candidates"
    while IFS= read -r release; do
        jq -e '.published_at | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$") and (. == (try (fromdateiso8601 | todateiso8601) catch null))' <<< "$release" >/dev/null || fail 'invalid publication time'
        pages "repos/KofLang/Kof4j/releases/$(jq -r .id <<< "$release")/assets" "$temporary/assets"
        assets=$(cat "$temporary/assets.json")
        jq -e '
            all(.[]; (.id | type == "number" and . > 0 and floor == .) and
                (.name | type == "string") and (.browser_download_url | type == "string")) and
            ([.[].id] | length == (unique | length))
        ' <<< "$assets" >/dev/null || fail 'invalid or duplicate asset metadata'
        selected=$(jq '[.[] | select(.name | test("^kof-[0-9][A-Za-z0-9.+-]*-linux-x86_64\\.tar\\.gz$"))]' <<< "$assets")
        [[ $(jq length <<< "$selected") -le 1 ]] || fail 'ambiguous Linux distribution'
        if [[ $(jq length <<< "$selected") == 1 ]]; then
            jq -cn --argjson release "$release" --argjson assets "$assets" --argjson archive "$(jq '.[0]' <<< "$selected")" '{release:$release,assets:$assets,archive:$archive}' >> "$temporary/candidates"
        fi
    done < <(jq -c '.[] | select(.draft == false and .prerelease == false) | {id,tag_name,published_at,draft,prerelease}' "$temporary/releases.json")
    jq -s '
        sort_by(.release.published_at | fromdateiso8601) |
        if length == 0 then error("no eligible Linux release")
        elif length > 1 and .[-1].release.published_at == .[-2].release.published_at then error("ambiguous latest release")
        else .[-1] end
    ' "$temporary/candidates" > "$temporary/selected.json"
    selected=$(cat "$temporary/selected.json")
    name=$(jq -r .archive.name <<< "$selected")
    version=${name#kof-}
    version=${version%-linux-x86_64.tar.gz}
    jq -e '[.assets[] | select(.name == "SHA256SUMS")] | length == 1' <<< "$selected" >/dev/null || fail 'missing or ambiguous SHA256SUMS asset'
    mkdir "$temporary/bundle"
    for asset in "$name" SHA256SUMS; do
        url=$(jq -er --arg name "$asset" '.assets[] | select(.name == $name) | .browser_download_url' <<< "$selected")
        [[ "$url" == https://github.com/KofLang/Kof4j/releases/download/*/"$asset" ]] || fail 'invalid official asset URL'
        curl --fail --location --silent --show-error --proto '=https' --proto-redir '=https' --output "$temporary/bundle/$asset" "$url" || fail "official asset download failed: $asset"
    done
    digest=$(checksum "$temporary/bundle/SHA256SUMS" "$name")
    [[ "$digest" =~ ^[0-9a-f]{64}$ ]] || fail 'invalid checksum entry'
    verify_archive "$temporary/bundle/$name" "$digest"
    commit=$(source_commit "$(jq -r .release.tag_name <<< "$selected")")
    jq --arg version "$version" --arg commit "$commit" --arg digest "$digest" --arg sha "$sifuture_sha" '
        {schema:1, repository:"KofLang/Kof4j", release:{id:.release.id,published_at:.release.published_at},
         tag:.release.tag_name, version:$version, kof_commit:$commit,
         archive:(.archive + {sha256:$digest}), sifuture_sha:$sha}
    ' <<< "$selected" > "$temporary/bundle/manifest.json"
    mv "$temporary/bundle" "$destination"
    report "$destination/manifest.json"
    cat "$destination/manifest.json"
}

install() {
    local bundle=$1 destination=$2 sifuture_sha=$3 name digest version root launcher actual
    require_sha "$sifuture_sha"
    [[ ! -e "$destination" ]] || fail 'install destination already exists'
    jq -e --arg sha "$sifuture_sha" '
        .schema == 1 and .repository == "KofLang/Kof4j" and .sifuture_sha == $sha and
        (.version | type == "string" and test("^[0-9][A-Za-z0-9.+-]*$")) and
        (.kof_commit | type == "string" and test("^[0-9a-f]{40}$")) and
        .archive.name == ("kof-" + .version + "-linux-x86_64.tar.gz") and
        (.archive.sha256 | type == "string" and test("^[0-9a-f]{64}$"))
    ' "$bundle/manifest.json" >/dev/null || fail 'invalid bundle manifest or SiFuture revision'
    name=$(jq -r .archive.name "$bundle/manifest.json")
    version=$(jq -r .version "$bundle/manifest.json")
    digest=$(checksum "$bundle/SHA256SUMS" "$name")
    [[ "$digest" == "$(jq -r .archive.sha256 "$bundle/manifest.json")" ]] || fail 'manifest checksum mismatch'
    verify_archive "$bundle/$name" "$digest"
    root=${name%.tar.gz}
    tar -tzf "$bundle/$name" > "$temporary/members"
    while IFS= read -r member; do
        [[ "$member" == "$root/"* && "$member" != /* && "/$member/" != */../* ]] || fail 'invalid archive member path'
    done < "$temporary/members"
    mkdir "$temporary/install"
    tar -xzf "$bundle/$name" --no-same-owner -C "$temporary/install"
    launcher="$temporary/install/$root/bin/kof"
    [[ -x "$launcher" && -x "$temporary/install/$root/jdk/bin/java" && -f "$temporary/install/$root/lib/kof.jar" ]] || fail 'incomplete official distribution'
    [[ "$(cat "$temporary/install/$root/VERSION")" == "$version" ]] || fail 'VERSION mismatch'
    "$temporary/install/$root/jdk/bin/java" -version >&2
    actual=$("$launcher" version)
    [[ "$actual" == "kof $version" ]] || fail 'launcher version mismatch'
    "$launcher" info --json > "$temporary/info.json"
    jq -e --arg version "$version" '.kof == $version and .embeddedJdk == true' "$temporary/info.json" >/dev/null || fail 'launcher is not using the embedded JVM'
    mv "$temporary/install" "$destination"
    destination=$(cd "$destination" && pwd)
    launcher="$destination/$root/bin/kof"
    if [[ -n "${GITHUB_ENV:-}" ]]; then
        printf 'KOF=%s\n' "$launcher" >> "$GITHUB_ENV"
    fi
    report "$bundle/manifest.json"
    jq -n --arg kof "$launcher" '{kof:$kof}'
}

check_main() {
    local repository=$1 tested_sha=$2 current fresh=false
    [[ "$repository" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || fail 'invalid repository'
    require_sha "$tested_sha"
    api "repos/$repository/git/ref/heads/main" > "$temporary/main.json"
    jq -e '.object.type == "commit" and (.object.sha | type == "string" and test("^[0-9a-f]{40}$"))' "$temporary/main.json" >/dev/null || fail 'invalid main response'
    current=$(jq -r .object.sha "$temporary/main.json")
    if [[ "$current" == "$tested_sha" ]]; then
        fresh=true
        printf 'Current main: %s; publication eligible\n' "$tested_sha" >&2
    else
        printf 'Superseded: tested %s; current main %s; publication skipped\n' "$tested_sha" "$current" >&2
    fi
    if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
        printf 'fresh=%s\n' "$fresh" >> "$GITHUB_OUTPUT"
    fi
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
        printf "Main freshness: tested \`%s\`, current \`%s\`, fresh \`%s\`.\n" "$tested_sha" "$current" "$fresh" >> "$GITHUB_STEP_SUMMARY"
    fi
    jq -n --arg tested "$tested_sha" --arg current "$current" --argjson fresh "$fresh" '{tested:$tested,current:$current,fresh:$fresh}'
}

[[ $# -ge 1 ]] || fail 'usage: kof_ci.sh resolve BUNDLE SHA | install BUNDLE DIRECTORY SHA'
operation=$1
shift
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
case "$operation" in
    resolve)
        [[ $# == 2 ]] || fail 'usage: kof_ci.sh resolve BUNDLE SHA'
        resolve "$@"
        ;;
    install)
        [[ $# == 3 ]] || fail 'usage: kof_ci.sh install BUNDLE DIRECTORY SHA'
        install "$@"
        ;;
    check-main)
        [[ $# == 2 ]] || fail 'usage: kof_ci.sh check-main OWNER/REPOSITORY SHA'
        check_main "$@"
        ;;
    *) fail 'unknown operation' ;;
esac
