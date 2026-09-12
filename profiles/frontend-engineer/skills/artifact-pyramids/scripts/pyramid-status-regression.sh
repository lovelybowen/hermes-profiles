#!/usr/bin/env bash
# Regression fixtures for pyramid-status.sh layer detection (card t_d7abe2bb).
#
# Reproduces the F5 defect and proves the fix:
#   * layer identity is the DIRECTORY name (01-summary/ 02-analysis/ 03-dossiers/),
#     never the file basename;
#   * documented layout -> L1/L2/L3 present;
#   * flat layout (no layer directories) -> every layer missing;
#   * lone 00-index.md -> every layer missing (scaffolding, not layer content);
#   * a basename that merely looks numbered never creates a layer.
#
# Usage:  bash pyramid-status-regression.sh [path/to/pyramid-status.sh]
# Exit 0 = all fixtures behave as documented; 1 = regression.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="${1:-$HERE/pyramid-status.sh}"

if [[ ! -f "$SCRIPT" ]]; then
    echo "Error: script not found: $SCRIPT" >&2
    exit 2
fi

FIXROOT="$(mktemp -d)"
trap 'rm -rf "$FIXROOT"' EXIT

FAILS=0
CHECKS=0

fail() {
    FAILS=$((FAILS + 1))
    echo "  FAIL  $*"
}

ok() {
    echo "  ok    $*"
}

# --- helpers ---------------------------------------------------------------
w() { # w <file> <line>...
    local f="$1"; shift
    mkdir -p "$(dirname "$f")"
    printf '%s\n' "$@" > "$f"
}

# Extract "<count> <present>" for a layer from the --json output.
layer_state() { # $1=json $2=layer
    printf '%s\n' "$1" \
        | grep -F "\"$2\": { \"name\":" \
        | head -1 \
        | sed -E 's/.*"count": ([0-9]+).*"present": (true|false).*/\1 \2/'
}

health_state() { # $1=json
    printf '%s\n' "$1" | sed -n 's/.*"pyramid_health": "\([a-z]*\)".*/\1/p'
}

expect() { # $1=label $2=json $3="L:n:present ... health"
    local label="$1" json="$2" spec="$3"
    local health="${spec##* }" layers="${spec% *}"
    local pair key want got
    for pair in $layers; do
        key="${pair%%:*}"
        want="$(printf '%s' "$pair" | cut -d: -f2) $(printf '%s' "$pair" | cut -d: -f3)"
        got="$(layer_state "$json" "$key")"
        CHECKS=$((CHECKS + 1))
        if [[ "$got" == "$want" ]]; then
            ok "$label L$key count/present = $got"
        else
            fail "$label L$key count/present = '$got' (expected '$want')"
        fi
    done
    got="$(health_state "$json")"
    CHECKS=$((CHECKS + 1))
    if [[ "$got" == "$health" ]]; then
        ok "$label pyramid_health = $got"
    else
        fail "$label pyramid_health = '$got' (expected '$health')"
    fi
}

run_fixture() { # $1=name $2=dir $3=expectation-spec
    local name="$1" dir="$2" spec="$3"
    echo
    echo "--- fixture: $name"
    ( cd "$dir" && find . -type f | sort | sed 's/^/      /' )
    local json
    json="$(bash "$SCRIPT" --json "$dir")" || { fail "$name: non-zero exit"; return; }
    expect "$name" "$json" "$spec"
}

echo "pyramid-status.sh regression fixtures"
echo "script under test: $SCRIPT"
echo "script sha256: $(sha256sum "$SCRIPT" | cut -d' ' -f1)"

# --- 1. documented layout (the layout the skill specifies) -----------------
D="$FIXROOT/documented"
w "$D/00-index.md" '# Index' ''
w "$D/01-summary/findings.md" '---' 'name: findings' '---' '' '# Findings' '' 'body body body'
w "$D/02-analysis/market-position.md" '---' 'name: market-position' '---' '' '# Market' '' 'body'
w "$D/03-dossiers/interview-1.md" '---' 'name: interview-1' '---' '' '# Interview' '' 'body'
run_fixture "documented-layout" "$D" "1:1:true 2:1:true 3:1:true complete"

# --- 2. short layer prefixes (1-summary/ 2-analysis/ 3-dossiers/) ---------
D="$FIXROOT/short-prefix"
w "$D/00-index.md" '# Index'
w "$D/1-summary/f.md" '---' 'name: f' '---' '' '# F'
w "$D/2-analysis/a.md" '---' 'name: a' '---' '' '# A'
w "$D/3-dossiers/d.md" '---' 'name: d' '---' '' '# D'
run_fixture "short-prefix-layout" "$D" "1:1:true 2:1:true 3:1:true complete"

# --- 3. flat layout, no layer directories -> must report missing ----------
D="$FIXROOT/flat"
w "$D/00-index.md" '# Index'
w "$D/summary.md" '---' 'name: summary' '---' '' '# Summary'
w "$D/market-analysis.md" '---' 'name: market' '---' '' '# Market'
w "$D/source-notes.md" '---' 'name: source' '---' '' '# Source'
run_fixture "flat-no-layer-dirs" "$D" "1:0:false 2:0:false 3:0:false incomplete"

# --- 4. lone 00-index.md -> scaffolding only, every layer missing ---------
D="$FIXROOT/index-only"
w "$D/00-index.md" '# Index' '' 'routing table only'
run_fixture "index-only" "$D" "1:0:false 2:0:false 3:0:false incomplete"

# --- 5. layer directory nested below the root ----------------------------
D="$FIXROOT/nested-layer-dir"
w "$D/00-index.md" '# Index'
w "$D/01-summary/notes/deep.md" '---' 'name: deep' '---' '' '# Deep'
run_fixture "nested-under-layer-dir" "$D" "1:1:true 2:0:false 3:0:false incomplete"

# --- 6. numbered BASENAMES inside another layer's dir = no false layer ----
D="$FIXROOT/basename-prefix"
w "$D/00-index.md" '# Index'
w "$D/03-dossiers/01-summary-notes.md" '---' 'name: n1' '---' '' '# N1'
w "$D/03-dossiers/02-analysis-notes.md" '---' 'name: n2' '---' '' '# N2'
run_fixture "numbered-basenames-in-l3" "$D" "1:0:false 2:0:false 3:2:true incomplete"

# --- 7. dot-directory in the ANCESTOR path must not suppress detection ----
# (Flow workspaces live under /root/.hermes/... -- the pre-fix hidden-path
#  filter blanked every layer there, e.g. all-zero reports for real pyramids)
D="$FIXROOT/.hidden-ancestor/pyramid"
w "$D/00-index.md" '# Index'
w "$D/01-summary/findings.md" '---' 'name: findings' '---' '' '# Findings'
run_fixture "dot-ancestor-path" "$D" "1:1:true 2:0:false 3:0:false incomplete"

# --- 8. hidden files inside a layer dir are ignored ----------------------
D="$FIXROOT/hidden-inside"
w "$D/00-index.md" '# Index'
w "$D/01-summary/findings.md" '---' 'name: findings' '---' '' '# Findings'
w "$D/01-summary/.hidden.md" '# hidden'
run_fixture "hidden-file-inside-layer" "$D" "1:1:true 2:0:false 3:0:false incomplete"

echo
echo "checks: $CHECKS, failures: $FAILS"
if [[ "$FAILS" -gt 0 ]]; then
    exit 1
fi
echo "RESULT: PASS"
