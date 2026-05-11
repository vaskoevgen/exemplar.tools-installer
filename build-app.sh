#!/usr/bin/env bash
# ==============================================================================
# build-app.sh — exemplar.tools full pipeline automation
# ==============================================================================
# Usage:
#   ./build-app.sh <prime.md> [app-name]
#
# Resume: if the app folder already exists, completed steps are skipped
# automatically — the pipeline continues from where it left off.
#
# Pipeline:
#   1a  Constrain  — structured requirements from your description
#   1b  Ledger     — schema obligations
#   2a  Pact       — builds code with contracts + tests
#   2b  Advocate   — 6-persona adversarial code review
#   3   Arbiter    — trust governance init
#   4   Baton      — deploy circuit (mock mode smoke test)
#   5a  Sentinel   — production log watcher setup
#   5b  Chronicler — event correlation config + validation
#   5c  Stigmergy  — org pattern analysis (mock mode)
#   6   Apprentice — LLM cost-optimisation proxy
#
# Output:
#   apps/<app-name>/          all generated artifacts
#   apps/<app-name>/logs/     one .log file per tool
# ==============================================================================

set -uo pipefail

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR/exemplar.tools"
ENV_FILE="$SCRIPT_DIR/.env"
APPS_DIR="$SCRIPT_DIR/apps"

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ── Output helpers ─────────────────────────────────────────────────────────────
ts()     { date '+%H:%M:%S'; }
banner() { echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
           echo -e "${BOLD}${BLUE}  $1${RESET}"
           echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"; }
step()   { echo -e "\n${BOLD}${CYAN}▶ [$(ts)] $1${RESET}"; }
info()   { echo -e "  ${DIM}[$(ts)] $1${RESET}"; }
ok()     { echo -e "  ${GREEN}✓ [$(ts)] $1${RESET}"; }
warn()   { echo -e "  ${YELLOW}⚠ [$(ts)] $1${RESET}"; }
err()    { echo -e "  ${RED}✗ [$(ts)] $1${RESET}" >&2; }
resumed(){ echo -e "  ${YELLOW}↩ [$(ts)] RESUMED: $1${RESET}"; }

# Prefix every line from stdin with a UTC timestamp
ts_lines() {
    while IFS= read -r line; do
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $line"
    done
}

run_logged() {   # run_logged <logfile> <cmd...>
    local LOG="$1"; shift
    local RC_FILE
    RC_FILE=$(mktemp)
    echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] CMD: $*" >> "$LOG"
    # Run in subshell so set+e doesn't kill us on failure; save real exit code
    ( set +e; "$@" 2>&1; echo $? > "$RC_FILE" ) | ts_lines >> "$LOG"
    local RC
    RC=$(cat "$RC_FILE" 2>/dev/null || echo 1)
    rm -f "$RC_FILE"
    echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] EXIT: $RC" >> "$LOG"
    return "$RC"
}

# ── Tool binaries ──────────────────────────────────────────────────────────────
CONSTRAIN="$TOOLS_DIR/constrain/.venv/bin/constrain"
LEDGER="$TOOLS_DIR/ledger/.venv/bin/ledger"
PACT="$TOOLS_DIR/pact/.venv/bin/pact"
ADVOCATE="$TOOLS_DIR/advocate/.venv/bin/advocate"
ARBITER="$TOOLS_DIR/arbiter/.venv/bin/arbiter"
BATON="$TOOLS_DIR/baton/.venv/bin/baton"
SENTINEL="$TOOLS_DIR/sentinel/.venv/bin/sentinel"
CHRONICLER_PY="$TOOLS_DIR/chronicler/.venv/bin/python3"
CHRONICLER_BIN="$TOOLS_DIR/chronicler/.venv/bin/chronicler"
STIGMERGY="$TOOLS_DIR/stigmergy/.venv/bin/stigmergy"
APPRENTICE="$TOOLS_DIR/apprentice/.venv/bin/apprentice"

# ── Argument parsing ───────────────────────────────────────────────────────────
usage() {
    echo "Usage: $0 <prime.md> [app-name]"
    echo "  prime.md   plain-English description of the app to build"
    echo "  app-name   folder name under apps/ (re-use to resume an interrupted run)"
    exit 1
}

[[ $# -lt 1 ]] && usage

PRIME_FILE="$(realpath "$1")"
[[ ! -f "$PRIME_FILE" ]] && { err "File not found: $PRIME_FILE"; exit 1; }

APP_NAME="${2:-app-$(date '+%Y%m%d-%H%M%S')}"
APP_DIR="$APPS_DIR/$APP_NAME"

mkdir -p "$APP_DIR/logs"
LOG_DIR="$APP_DIR/logs"
STATE_FILE="$APP_DIR/.pipeline-state"

# ── State file: track completed steps ─────────────────────────────────────────
# Each completed step writes a line "STEP_KEY=ok|warn|fail" to STATE_FILE.
# On resume the script reads these and skips finished steps.

# Artifact-based detection — works even when state file was never written (e.g. after Ctrl+C)
artifact_done() {
    case "$1" in
        1a-constrain) [[ -f "$APP_DIR/prompt.md" && -f "$APP_DIR/constraints.yaml" ]] ;;
        1b-ledger)    [[ -f "$APP_DIR/ledger.yaml" && -f "$APP_DIR/changelog.yaml" ]] ;;
        2a-pact)
            [[ -f "$APP_DIR/.pact/state.json" ]] && \
            python3 -c "
import json; d=json.load(open('$APP_DIR/.pact/state.json'))
exit(0 if d.get('status') in ('complete','succeeded','done') else 1)
" 2>/dev/null ;;
        2b-advocate)  [[ -f "$APP_DIR/findings.json" ]] ;;
        3-arbiter)    [[ -f "$APP_DIR/arbiter.yaml" ]] ;;
        4-baton)      [[ -f "$APP_DIR/baton.yaml" ]] ;;
        5a-sentinel)  [[ -d "$APP_DIR/.sentinel" ]] ;;
        5b-chronicler)[[ -f "$APP_DIR/chronicler.yaml" ]] ;;
        5c-stigmergy) [[ -f "$APP_DIR/.stigmergy/insights.jsonl" ]] ;;
        6-apprentice) [[ -f "$APP_DIR/apprentice.yaml" ]] && \
                      grep -q "apprentice run succeeded\|apprentice status ok" \
                           "$APP_DIR/logs/6-apprentice.log" 2>/dev/null ;;
        *) return 1 ;;
    esac
}

mark_done() {   # mark_done <key> <ok|warn|fail>
    # Remove any prior entry for this key then append
    grep -v "^${1}=" "$STATE_FILE" > "${STATE_FILE}.tmp" 2>/dev/null || true
    mv "${STATE_FILE}.tmp" "$STATE_FILE" 2>/dev/null || true
    echo "${1}=${2}" >> "$STATE_FILE"
}

is_done() {   # is_done <key> → 0 if done (ok or warn), 1 if not done or failed
    # Check state file first, then fall back to artifact detection
    local VAL
    VAL=$(grep "^${1}=" "$STATE_FILE" 2>/dev/null | tail -1 | cut -d= -f2)
    if [[ "$VAL" == "ok" || "$VAL" == "warn" ]]; then
        return 0
    fi
    # No state file entry — check for artifacts on disk (survives Ctrl+C)
    artifact_done "$1"
}

load_state() {
    [[ -f "$STATE_FILE" ]] || return
    echo -e "\n  ${YELLOW}${BOLD}Existing run detected — resuming from last completed step${RESET}"
    echo -e "  ${DIM}State file: $STATE_FILE${RESET}"
    while IFS='=' read -r KEY VAL; do
        [[ -z "$KEY" ]] && continue
        case "$VAL" in
            ok)   echo -e "  ${GREEN}✓ $KEY${RESET}" ;;
            warn) echo -e "  ${YELLOW}⚠ $KEY${RESET}" ;;
            fail) echo -e "  ${RED}✗ $KEY (failed — will retry)${RESET}" ;;
        esac
    done < "$STATE_FILE"
}

# ── Step summary tracker ───────────────────────────────────────────────────────
declare -A STEP_STATUS
STEPS_ORDERED=()

record() {   # record <step> <ok|warn|fail>
    STEP_STATUS["$1"]="$2"
    STEPS_ORDERED+=("$1")
    mark_done "$1" "$2"
}

# require_ok <step> — call at the top of any step that depends on a prior step.
# If the required step did not succeed, skip this step with a clear message.
# Returns 1 (skip) or 0 (proceed).
require_ok() {
    local DEP="$1"
    local VAL
    VAL=$(grep "^${DEP}=" "$STATE_FILE" 2>/dev/null | tail -1 | cut -d= -f2)
    if [[ "$VAL" != "ok" && "$VAL" != "warn" ]]; then
        warn "Skipping — requires '$DEP' to succeed first (current: ${VAL:-not run})"
        return 1
    fi
    return 0
}

# ── Load env ───────────────────────────────────────────────────────────────────
if [[ -f "$ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    ok "Loaded .env"
else
    warn ".env not found — ANTHROPIC_API_KEY must already be set"
fi

# ── Print header ───────────────────────────────────────────────────────────────
banner "exemplar.tools build pipeline"
echo -e "  ${BOLD}App:${RESET}    $APP_NAME"
echo -e "  ${BOLD}Prime:${RESET}  $PRIME_FILE"
echo -e "  ${BOLD}Dir:${RESET}    $APP_DIR"
echo -e "  ${BOLD}Logs:${RESET}   $LOG_DIR/"

load_state

cp "$PRIME_FILE" "$APP_DIR/prime.md"

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1a — CONSTRAIN
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 1a — Constrain"
CONSTRAIN_LOG="$LOG_DIR/1a-constrain.log"

if is_done "1a-constrain"; then
    resumed "Constrain already done — skipping"
    record "1a-constrain" "ok"
elif [[ ! -x "$CONSTRAIN" ]]; then
    err "Binary not found: $CONSTRAIN"
    record "1a-constrain" "fail"
else
    step "Running Constrain (non-interactive, primed from prime.md)..."
    info "Generates: prompt.md, constraints.yaml, component_map.yaml, trust_policy.yaml, schema_hints.yaml"
    cd "$APP_DIR"
    echo ".constrain/" >> .gitignore 2>/dev/null || true

    # Pipe 3 newlines to answer interactive prompts automatically:
    #   1) "Add document (path or Enter to start interview):"
    #   2) "Feedback>" at the end (accept generated artifacts)
    echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] constrain new" >> "$CONSTRAIN_LOG"
    CONSTRAIN_RC_FILE=$(mktemp)
    ( set +e
      printf '\n\n\n' | "$CONSTRAIN" new \
          --min-challenge 0 --max-challenge 0 \
          --min-understand 0 --max-understand 0 \
          -p prime.md 2>&1
      echo $? > "$CONSTRAIN_RC_FILE"
    ) | ts_lines >> "$CONSTRAIN_LOG"
    CONSTRAIN_RC=$(cat "$CONSTRAIN_RC_FILE" 2>/dev/null || echo 1)
    rm -f "$CONSTRAIN_RC_FILE"
    echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] EXIT: $CONSTRAIN_RC" >> "$CONSTRAIN_LOG"
    if [[ "$CONSTRAIN_RC" == "0" ]]; then
        ok "Constrain finished"
        for f in prompt.md constraints.yaml component_map.yaml trust_policy.yaml schema_hints.yaml; do
            [[ -f "$APP_DIR/$f" ]] && info "  + $f" || warn "  - $f (not generated)"
        done
        record "1a-constrain" "ok"
    else
        err "Constrain failed — check $CONSTRAIN_LOG"
        record "1a-constrain" "fail"
    fi
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1b — LEDGER
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 1b — Ledger"
LEDGER_LOG="$LOG_DIR/1b-ledger.log"

if is_done "1b-ledger"; then
    resumed "Ledger already done — skipping"
    record "1b-ledger" "ok"
elif [[ ! -x "$LEDGER" ]]; then
    err "Binary not found: $LEDGER"
    record "1b-ledger" "fail"
else
    step "Initialising Ledger (schema registry)..."
    info "Note: schema add/validate/export are stubs — exit 0 but no-op"
    cd "$APP_DIR"

    run_logged "$LEDGER_LOG" "$LEDGER" init
    ok "ledger init done"

    run_logged "$LEDGER_LOG" "$LEDGER" backend add appdb --type sqlite --owner app || true
    ok "backend registered"

    mkdir -p schemas
    cat > schemas/items.yaml << 'SCHEMA'
name: items
version: 1

fields:
  - name: id
    field_type: integer
    classification: PUBLIC
    nullable: false
    annotations:
      - name: primary_key
      - name: immutable
      - name: not_null

  - name: title
    field_type: varchar(255)
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null

  - name: description
    field_type: text
    classification: PUBLIC
    nullable: true

  - name: status
    field_type: varchar(20)
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null

  - name: created_at
    field_type: timestamptz
    classification: PUBLIC
    nullable: false
    annotations:
      - name: immutable
      - name: not_null
      - name: audit_field

  - name: updated_at
    field_type: timestamptz
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null
      - name: audit_field
SCHEMA

    run_logged "$LEDGER_LOG" "$LEDGER" schema add schemas/items.yaml || true
    run_logged "$LEDGER_LOG" "$LEDGER" schema validate || true
    run_logged "$LEDGER_LOG" "$LEDGER" export --format pact || true
    run_logged "$LEDGER_LOG" "$LEDGER" export --format arbiter || true
    run_logged "$LEDGER_LOG" "$LEDGER" builtins list >> "$LEDGER_LOG" 2>&1 || true
    ok "Ledger done"
    record "1b-ledger" "ok"
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2a — PACT
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 2a — Pact"
PACT_LOG="$LOG_DIR/2a-pact.log"

# Helper: read a field from .pact/state.json
pact_state() {
    local F="$1" SF="$APP_DIR/.pact/state.json"
    [[ -f "$SF" ]] || { echo ""; return; }
    python3 -c "
import json
try:
    d = json.load(open('$SF'))
    print(d.get('$F', ''))
except Exception:
    print('')
" 2>/dev/null
}

# Helper: call Claude API to generate a targeted sops.md rule from a pact failure.
# Extracts recent error context from the pact log, asks Claude what rule would prevent it,
# and returns a one-line rule string. Falls back to empty string on any failure.
# Helper: call Claude to investigate a recurring pact failure and produce a human-readable
# manual intervention report — what failed, root cause, and exact steps to fix it.
generate_intervention_report() {
    local PAUSE_REASON="$1"
    local LOG="$PACT_LOG"
    [[ -z "${ANTHROPIC_API_KEY:-}" ]] && { echo "Auto-fix failed. Check $LOG for details."; return; }

    local ERROR_CONTEXT
    ERROR_CONTEXT=$(grep -v "HTTP Request\|Research complete\|Plan evaluation\|Code authored" "$LOG" 2>/dev/null | tail -60)

    local SOPS_CONTENT
    SOPS_CONTENT=$(cat "$APP_DIR/sops.md" 2>/dev/null)

    python3 - <<PYEOF
import json, urllib.request

api_key = """${ANTHROPIC_API_KEY}"""
pause_reason = """${PAUSE_REASON}"""
error_context = """${ERROR_CONTEXT}"""
sops_content = """${SOPS_CONTENT}"""
lang = """${DETECTED_LANG:-unknown}"""
test_fw = """${DETECTED_TEST:-unknown}"""

prompt = f"""A pact build pipeline ({lang}/{test_fw} project) auto-fix was attempted but the same failure keeps recurring.

FAILURE: {pause_reason}

RECENT LOG (last 60 lines):
{error_context}

CURRENT sops.md:
{sops_content}

Investigate and write a SHORT manual intervention report for a developer.
Include:
1. Root cause (1-2 sentences — be specific about what file/function/config is broken)
2. Exact manual steps to fix it (numbered list, concrete commands if applicable)
3. What to update in sops.md to prevent it next time

Be concise and specific. No generic advice."""

payload = json.dumps({
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 400,
    "messages": [{"role": "user", "content": prompt}]
}).encode()

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=payload,
    headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        print(data["content"][0]["text"].strip())
except Exception as e:
    print(f"Could not generate report: {e}")
PYEOF
}

generate_sops_rule() {
    local PAUSE_REASON="$1"
    local LOG="$PACT_LOG"
    [[ -z "${ANTHROPIC_API_KEY:-}" ]] && { echo ""; return; }

    # Extract last 40 relevant log lines as error context (skip HTTP request noise)
    local ERROR_CONTEXT
    ERROR_CONTEXT=$(grep -v "HTTP Request\|Research complete\|Plan evaluation\|Code authored" "$LOG" 2>/dev/null | tail -40)

    local RULE
    RULE=$(python3 - <<PYEOF
import json, urllib.request, urllib.error, sys

api_key = """${ANTHROPIC_API_KEY}"""
pause_reason = """${PAUSE_REASON}"""
error_context = """${ERROR_CONTEXT}"""
lang = """${DETECTED_LANG:-unknown}"""
test_fw = """${DETECTED_TEST:-unknown}"""

prompt = f"""A pact build pipeline ({lang}/{test_fw} project) paused with this failure:

PAUSE REASON: {pause_reason}

RECENT LOG (last 40 lines):
{error_context}

Write ONE short rule (1-2 sentences, imperative tone) to add to sops.md that would prevent this failure in future builds.
The rule must be {lang}-specific and must not reference other languages or their conventions.
The rule should be concrete and actionable for an AI code generator.
Reply with ONLY the rule text, no explanation, no markdown, no quotes."""

payload = json.dumps({
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 150,
    "messages": [{"role": "user", "content": prompt}]
}).encode()

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=payload,
    headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        print(data["content"][0]["text"].strip())
except Exception as e:
    print("")
PYEOF
)
    echo "$RULE"
}

# Helper: estimate cost from token counts logged by pact (pact doesn't write cost to state.json)
# Token counts appear in log as "(N tokens)"; uses claude-opus-4 pricing ($15/M input, $75/M output)
# Returns a range like "$1.23~$6.15 (82,000 tokens)" or "?" on failure
pact_cost_estimate() {
    [[ -f "$PACT_LOG" ]] || { echo "?"; return; }
    python3 -c "
import re
try:
    log = open('$PACT_LOG').read()
    tokens = sum(int(t) for t in re.findall(r'\((\d+) tokens\)', log))
    if tokens == 0:
        print('?')
    else:
        lo = tokens / 1_000_000 * 15
        hi = tokens / 1_000_000 * 75
        print(f'\${lo:.2f}~\${hi:.2f} ({tokens:,} tok)')
except Exception:
    print('?')
" 2>/dev/null || echo "?"
}

# Helper: returns 0 (true) if interview.json exists and approved=false
interview_needs_approval() {
    local IVW="$APP_DIR/decomposition/interview.json"
    [[ -f "$IVW" ]] || return 1
    python3 -c "
import json
try:
    d = json.load(open('$IVW'))
    exit(0 if not d.get('approved', False) else 1)
except Exception:
    exit(1)
" 2>/dev/null
}

# Helper: ensure pact daemon is running; restart if PID is dead
ensure_daemon() {
    local PID_VAR="$1"   # name of the variable holding the PID
    local PID="${!PID_VAR}"
    if [[ -z "$PID" ]] || ! kill -0 "$PID" 2>/dev/null; then
        warn "Pact daemon not running — starting..."
        ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" "$PACT" daemon . >> "$PACT_LOG" 2>&1 &
        local NEW_PID=$!
        eval "$PID_VAR=$NEW_PID"
        info "Daemon PID: $NEW_PID"
        sleep 8
        return 0   # restarted
    fi
    return 1   # already running
}

if is_done "2a-pact"; then
    resumed "Pact already done — skipping"
    record "2a-pact" "ok"
elif [[ ! -x "$PACT" ]]; then
    err "Binary not found: $PACT"
    record "2a-pact" "fail"
else
    step "Setting up Pact..."
    info "Estimated cost: \$1–3, time: 10–30 min"
    cd "$APP_DIR"

    # Init only if not already done
    if [[ ! -f pact.yaml ]]; then
        run_logged "$PACT_LOG" "$PACT" init .
        ok "pact init done"
    else
        info "pact.yaml exists — skipping init"
    fi

    cp prime.md task.md

    # ── Auto-detect language from prime.md ────────────────────────────────────
    # Scan for language keywords and configure sops.md + pact.yaml accordingly.
    # pact init writes Python defaults — we must override BEFORE starting daemon.
    DETECTED_LANG="python"
    DETECTED_TEST="pytest"
    PRIME_LOWER=$(tr '[:upper:]' '[:lower:]' < prime.md)

    if echo "$PRIME_LOWER" | grep -qE 'typescript|\.tsx?|vitest|vite|react|next\.?js|bun|deno'; then
        DETECTED_LANG="typescript"
        DETECTED_TEST="vitest"
    elif echo "$PRIME_LOWER" | grep -qE '\bjavascript\b|\.jsx?\b|node\.?js|jest\b'; then
        DETECTED_LANG="javascript"
        DETECTED_TEST="vitest"
    elif echo "$PRIME_LOWER" | grep -qE '\brust\b|cargo|crate'; then
        DETECTED_LANG="rust"
        DETECTED_TEST="cargo"
    elif echo "$PRIME_LOWER" | grep -qE '\bgo\b|golang|\.go\b'; then
        DETECTED_LANG="go"
        DETECTED_TEST="go test"
    fi

    info "Detected language: $DETECTED_LANG (test: $DETECTED_TEST)"

    # Fix sops.md — pact init writes Python defaults; override with detected lang
    if [[ "$DETECTED_LANG" != "python" ]]; then
        step "Fixing sops.md for $DETECTED_LANG (pact init writes Python defaults)..."
        CRITICAL_LINE="CRITICAL: implementation language is ${DETECTED_LANG}. Never generate Python. All output files must be .ts/.tsx (or equivalent for ${DETECTED_LANG})."
        if [[ -f sops.md ]]; then
            # Replace Language and Testing lines in-place (macOS sed needs '')
            sed -i '' "s/- Language:.*$/- Language: ${DETECTED_LANG}/" sops.md 2>/dev/null \
                || sed -i  "s/- Language:.*$/- Language: ${DETECTED_LANG}/" sops.md
            sed -i '' "s/- Testing:.*$/- Testing: ${DETECTED_TEST}/" sops.md 2>/dev/null \
                || sed -i  "s/- Testing:.*$/- Testing: ${DETECTED_TEST}/" sops.md
            # Prepend CRITICAL line if not already there
            if ! grep -q 'CRITICAL:' sops.md; then
                printf '%s\n\n%s\n' "$CRITICAL_LINE" "$(cat sops.md)" > sops.md
            fi
            info "sops.md updated for ${DETECTED_LANG}"
        else
            # Write from scratch
            cat > sops.md << SOPS_CONTENT
${CRITICAL_LINE}

## Tech Stack
- Language: ${DETECTED_LANG}
- Testing: ${DETECTED_TEST}

## Standards
- Type annotations on all public functions
- Prefer composition over inheritance

## Verification
- All functions must have at least one test
- No task is done until its contract tests pass
SOPS_CONTENT
            info "sops.md created for ${DETECTED_LANG}"
        fi
        ok "sops.md configured for $DETECTED_LANG"
    else
        info "sops.md kept as Python (default)"
    fi

    # Always write full pact.yaml with detected language
    cat > pact.yaml << PACT_YAML
budget: 10.0
shaping: false
build_mode: auto
backend: anthropic
model: claude-opus-4-6
language: ${DETECTED_LANG}
test_framework: ${DETECTED_TEST}
role_backends:
  decomposer: anthropic
  contract_author: anthropic
  test_author: anthropic
  code_author: anthropic
PACT_YAML
    info "pact.yaml configured (language: $DETECTED_LANG, test_framework: $DETECTED_TEST)"

    # ── Auto-reset failed pact state ─────────────────────────────────────────
    # If a previous run failed (e.g. API timeout/stall), the state.json is left
    # with status=failed. The daemon refuses to start in that state.
    # We reset it back to active so the daemon can resume from the last phase.
    PACT_STATE_FILE="$APP_DIR/.pact/state.json"
    if [[ -f "$PACT_STATE_FILE" ]]; then
        PREV_STATUS=$(python3 -c "import json; print(json.load(open('$PACT_STATE_FILE')).get('status',''))" 2>/dev/null)
        if [[ "$PREV_STATUS" == "failed" ]]; then
            warn "Pact state is 'failed' (likely API timeout) — resetting to active for retry..."
            python3 << RESET_PACT
import json
path = '$PACT_STATE_FILE'
d = json.load(open(path))
d['status'] = 'active'
d['completed_at'] = ''
d['pause_reason'] = ''
# Keep interview approved if it was already done
if d.get('interview_result'):
    d['interview_result']['approved'] = True
json.dump(d, open(path, 'w'), indent=2)
print(f"Reset: failed -> active  phase={d.get('phase')}")
RESET_PACT
            ok "Pact state reset — will retry from last phase"
            echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Auto-reset pact state: failed -> active" >> "$PACT_LOG"
        fi
    fi

    # Start daemon (or re-use one already running from a previous attempt)
    PACT_PID=""
    EXISTING_DAEMON=$(pgrep -f "pact daemon" 2>/dev/null | head -1 || true)
    if [[ -n "$EXISTING_DAEMON" ]]; then
        PACT_PID="$EXISTING_DAEMON"
        info "Re-using existing pact daemon PID: $PACT_PID"
    else
        step "Starting pact daemon..."
        ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" "$PACT" daemon . >> "$PACT_LOG" 2>&1 &
        PACT_PID=$!
        info "Daemon PID: $PACT_PID"
        sleep 8
    fi

    PACT_MAX_WAIT=14400     # 4 hour ceiling (complex apps can take longer)
    PACT_MAX_RETRIES=5      # max times to auto-retry after API failure
    PACT_RETRY_COUNT=0
    PACT_BUDGET_BUMPS=0     # max 3 budget bumps ($10 each, $40 total cap)
    PACT_AUTOFIX_COUNT=0    # auto-fix attempts this run (resets each restart, max 2)
    PACT_START=$(date +%s)
    PACT_RESUME_COUNT=0
    PACT_APPROVED=false
    PACT_APPROVE_FAIL_COUNT=0
    LAST_APPROVE_AT=0

    # Sanitise state.json null fields — pact writes null on crash, pydantic rejects it on restart
    sanitise_pact_state() {
        [[ -f "$PACT_STATE_FILE" ]] || return
        python3 -c "
import json
path = '$PACT_STATE_FILE'
d = json.load(open(path))
changed = False
for field in ('completed_at', 'pause_reason'):
    if d.get(field) is None:
        d[field] = ''
        changed = True
if changed:
    json.dump(d, open(path, 'w'), indent=2)
    print('Sanitised null fields in state.json')
" 2>/dev/null
    }

    step "Monitoring pact daemon (auto-approve + auto-resume enabled)..."

    while true; do
        ELAPSED=$(( $(date +%s) - PACT_START ))

        if [[ $ELAPSED -gt $PACT_MAX_WAIT ]]; then
            warn "Pact timed out after ${PACT_MAX_WAIT}s — daemon still running, marking as warn so pipeline continues"
            record "2a-pact" "warn"
            break
        fi

        # Fix null fields every cycle — pact writes null on crash, pydantic rejects on restart
        sanitise_pact_state

        STATUS="$(pact_state status)"
        PHASE="$(pact_state phase)"
        PAUSE_REASON="$(pact_state pause_reason)"

        # ── AUTO-APPROVE ──────────────────────────────────────────────────────
        # Approve every cycle the interview.json is unapproved.
        # Rate-limit: don't approve more than once every 30s to avoid hammering.
        NOW=$(date +%s)
        if interview_needs_approval && [[ $(( NOW - LAST_APPROVE_AT )) -gt 30 ]]; then
            info "Interview unapproved — running pact approve..."
            if run_logged "$PACT_LOG" "$PACT" approve .; then
                ok "Interview approved"
                PACT_APPROVED=true
                PACT_APPROVE_FAIL_COUNT=0
            else
                PACT_APPROVE_FAIL_COUNT=$(( PACT_APPROVE_FAIL_COUNT + 1 ))
                warn "pact approve returned non-zero (attempt $PACT_APPROVE_FAIL_COUNT)"
            fi
            LAST_APPROVE_AT=$NOW

            # After approving, if paused, also resume immediately
            if [[ "$STATUS" == "paused" ]]; then
                sleep 2
                ensure_daemon PACT_PID
                run_logged "$PACT_LOG" "$PACT" resume . || true
                info "Resume sent after approve"
            fi
            sleep 5
            continue   # re-check state immediately after approve
        fi

        # ── STATE MACHINE ─────────────────────────────────────────────────────
        case "$STATUS" in

            complete|succeeded|done)
                ok "Pact build complete (${ELAPSED}s)"
                record "2a-pact" "ok"
                break
                ;;

            failed)
                PACT_RETRY_COUNT=$(( PACT_RETRY_COUNT + 1 ))
                if [[ $PACT_RETRY_COUNT -le $PACT_MAX_RETRIES ]]; then
                    # Transient failures (API timeout, stall) are common — auto-reset and retry
                    warn "Pact failed (attempt $PACT_RETRY_COUNT/$PACT_MAX_RETRIES) — resetting state and retrying..."
                    echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Auto-retry #${PACT_RETRY_COUNT} after failure" >> "$PACT_LOG"
                    python3 << RETRY_RESET
import json
path = '$PACT_STATE_FILE'
d = json.load(open(path))
d['status'] = 'active'
d['completed_at'] = ''
d['pause_reason'] = ''
if d.get('interview_result'):
    d['interview_result']['approved'] = True
json.dump(d, open(path, 'w'), indent=2)
print(f"Retry reset: failed -> active  phase={d.get('phase')}")
RETRY_RESET
                    sleep 15   # brief pause before restarting daemon
                    ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" "$PACT" daemon . >> "$PACT_LOG" 2>&1 &
                    PACT_PID=$!
                    info "Daemon restarted (PID: $PACT_PID)"
                    sleep 8
                else
                    err "Pact failed after $PACT_MAX_RETRIES retries — check $PACT_LOG"
                    record "2a-pact" "fail"
                    break
                fi
                ;;

            budget_exceeded)
                # Bump the budget by $10 and resume — max 3 bumps total
                PACT_BUDGET_BUMPS=$(( PACT_BUDGET_BUMPS + 1 ))
                if [[ $PACT_BUDGET_BUMPS -le 3 ]]; then
                    warn "Budget cap reached (bump #${PACT_BUDGET_BUMPS}/3) — increasing budget by \$10 and resuming..."
                    python3 << BUMP_BUDGET
import re, pathlib, json
p = pathlib.Path('$APP_DIR/pact.yaml')
text = p.read_text()
def bump(m):
    return f"budget: {float(m.group(1)) + 10:.1f}"
p.write_text(re.sub(r'budget:\s*([0-9.]+)', bump, text))
sf = pathlib.Path('$PACT_STATE_FILE')
d = json.loads(sf.read_text())
d['status'] = 'active'
d['pause_reason'] = ''
d['completed_at'] = ''
sf.write_text(json.dumps(d, indent=2))
new_budget = float(re.search(r'budget: ([0-9.]+)', p.read_text()).group(1))
print(f"Budget bumped to \${new_budget:.1f}")
BUMP_BUDGET
                    echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Budget bumped #${PACT_BUDGET_BUMPS}" >> "$PACT_LOG"
                    ensure_daemon PACT_PID
                    run_logged "$PACT_LOG" "$PACT" resume . || true
                    sleep 10
                else
                    err "Budget exceeded 3 bumps (\$40 total) — stopping. Check $PACT_LOG."
                    record "2a-pact" "fail"
                    break
                fi
                ;;

            paused)
                if echo "${PAUSE_REASON}" | grep -qi "interview\|user answer\|waiting for user"; then
                    # Interview pause — approve handles it above; just nudge with resume
                    warn "Interview pause — approve already sent; resuming..."
                    ensure_daemon PACT_PID
                    run_logged "$PACT_LOG" "$PACT" resume . || true
                elif echo "${PAUSE_REASON}" | grep -qi "systemic\|import_error\|missing dependencies\|cascade\|rejection_rate"; then
                    # Systemic failure — auto-fix disabled; manual intervention required
                    warn "Systemic failure: ${PAUSE_REASON:-unknown} — auto-fix disabled, see intervention report below"
                    # GENERATED_RULE="$(generate_sops_rule "${PAUSE_REASON}")"  # disabled — edit sops.md manually
                    GENERATED_RULE=""
                    PACT_AUTOFIX_COUNT=$(( PACT_AUTOFIX_COUNT + 1 ))
                    if [[ -n "$GENERATED_RULE" ]] && [[ "$PACT_AUTOFIX_COUNT" -le 2 ]]; then
                        echo "" >> "$APP_DIR/sops.md"
                        echo "## Auto-fix ($(date -u '+%Y-%m-%dT%H:%M:%SZ'))" >> "$APP_DIR/sops.md"
                        echo "$GENERATED_RULE" >> "$APP_DIR/sops.md"
                        warn "sops.md patched: $GENERATED_RULE"
                        echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Auto-patched sops.md: $GENERATED_RULE" >> "$PACT_LOG"
                        # Kill daemon and reset implement phase so pact re-reads sops.md from component 1
                        warn "Restarting fresh implement cycle so new rule applies from the start..."
                        kill "$PACT_PID" 2>/dev/null || true
                        sleep 3
                        python3 << FRESH_CYCLE
import json, pathlib
sf = pathlib.Path('$PACT_STATE_FILE')
d = json.loads(sf.read_text())
d['status'] = 'active'
d['phase'] = 'implement'
d['pause_reason'] = ''
d['completed_at'] = ''
sf.write_text(json.dumps(d, indent=2))
print("Reset: restarting implement phase with updated sops.md")
FRESH_CYCLE
                        echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Fresh implement cycle started after sops.md patch" >> "$PACT_LOG"
                        ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" "$PACT" daemon . >> "$PACT_LOG" 2>&1 &
                        PACT_PID=$!
                        info "Daemon restarted (PID: $PACT_PID) — fresh cycle with updated sops.md"
                        sleep 8
                    else
                        # sops.md already patched but same failure recurs — auto-fix didn't work.
                        # Ask Claude to investigate and produce a specific manual intervention report.
                        kill "$PACT_PID" 2>/dev/null || true
                        echo ""
                        echo -e "${RED}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
                        echo -e "${RED}${BOLD}  MANUAL INTERVENTION REQUIRED${RESET}"
                        echo -e "${RED}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
                        echo -e "  ${BOLD}Failure:${RESET} ${PAUSE_REASON}"
                        echo -e "  ${DIM}Investigating with Claude...${RESET}"
                        echo ""
                        REPORT="$(generate_intervention_report "${PAUSE_REASON}")"
                        echo "$REPORT" | sed "s/^/  /"
                        echo ""
                        echo -e "  ${BOLD}Logs:${RESET} $PACT_LOG"
                        echo -e "  ${BOLD}Resume:${RESET} ./build-app.sh $PRIME_FILE $APP_NAME"
                        echo -e "${RED}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
                        echo ""
                        record "2a-pact" "fail"
                        break
                    fi
                else
                    # Health gate pause
                    PACT_RESUME_COUNT=$(( PACT_RESUME_COUNT + 1 ))
                    warn "Health gate pause #${PACT_RESUME_COUNT} — ${PAUSE_REASON:-unknown}"
                    ensure_daemon PACT_PID
                    run_logged "$PACT_LOG" "$PACT" resume . || true
                    info "Resume sent"
                fi
                sleep 12
                ;;

            active|running|starting|*)
                # Restart daemon if it died
                if ! kill -0 "$PACT_PID" 2>/dev/null; then
                    STATUS_RECHECK="$(pact_state status)"
                    case "$STATUS_RECHECK" in
                        complete|succeeded|done)
                            ok "Pact finished (daemon exited cleanly)"
                            record "2a-pact" "ok"
                            break
                            ;;
                        failed)
                            err "Pact failed (daemon exited)"
                            record "2a-pact" "fail"
                            break
                            ;;
                        *)
                            warn "Daemon exited unexpectedly (status=$STATUS_RECHECK phase=$PHASE) — restarting"
                            ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" "$PACT" daemon . >> "$PACT_LOG" 2>&1 &
                            PACT_PID=$!
                            info "New daemon PID: $PACT_PID"
                            sleep 8
                            [[ "$PACT_APPROVED" == "true" ]] && { run_logged "$PACT_LOG" "$PACT" resume . || true; }
                            ;;
                    esac
                fi

                COST_EST="$(pact_cost_estimate)"
                info "status=${STATUS:-?}  phase=${PHASE:-?}  cost=${COST_EST}  elapsed=${ELAPSED}s"
                sleep 15
                ;;
        esac
    done

    # Run contract tests if src/ was built
    if [[ -d "$APP_DIR/src" ]]; then
        step "Running Pact contract tests..."
        FIRST_COMP=$(ls "$APP_DIR/src/" 2>/dev/null | head -1)
        PACT_PYTEST="$TOOLS_DIR/pact/.venv/bin/pytest"
        if [[ -n "$FIRST_COMP" && -f "$APP_DIR/tests/$FIRST_COMP/contract_test.py" ]]; then
            PYTHONPATH="$APP_DIR/src/$FIRST_COMP" \
                "$PACT_PYTEST" "$APP_DIR/tests/$FIRST_COMP/contract_test.py" -q \
                >> "$PACT_LOG" 2>&1 \
                && ok "Contract tests passed" \
                || warn "Contract tests failed — check $PACT_LOG"
        else
            info "No contract test for '$FIRST_COMP' — skipping"
        fi
    fi
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2b — ADVOCATE
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 2b — Advocate"
ADVOCATE_LOG="$LOG_DIR/2b-advocate.log"

if is_done "2b-advocate"; then
    resumed "Advocate already done — skipping"
    record "2b-advocate" "ok"
elif ! require_ok "2a-pact"; then
    record "2b-advocate" "fail"
elif [[ ! -x "$ADVOCATE" ]]; then
    err "Binary not found: $ADVOCATE"
    record "2b-advocate" "fail"
elif [[ ! -d "$APP_DIR/src" ]]; then
    warn "No src/ — skipping Advocate (Pact may not have built code)"
    record "2b-advocate" "warn"
else
    step "Running Advocate 6-persona adversarial code review..."
    cd "$APP_DIR"
    echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] advocate review" >> "$ADVOCATE_LOG"
    if ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            "$ADVOCATE" review src/ \
            -o "$APP_DIR/findings.json" \
            --html "$APP_DIR/review-report.html" \
            >> "$ADVOCATE_LOG" 2>&1; then
        ok "Advocate review complete — findings.json + review-report.html"
        record "2b-advocate" "ok"
    else
        warn "Advocate exited non-zero — check $ADVOCATE_LOG"
        record "2b-advocate" "warn"
    fi
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — ARBITER
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 3 — Arbiter"
ARBITER_LOG="$LOG_DIR/3-arbiter.log"

if is_done "3-arbiter"; then
    resumed "Arbiter already done — skipping"
    record "3-arbiter" "ok"
elif ! require_ok "2a-pact"; then
    record "3-arbiter" "fail"
elif [[ ! -x "$ARBITER" ]]; then
    err "Binary not found: $ARBITER"
    record "3-arbiter" "fail"
else
    step "Initialising Arbiter trust governance..."
    cd "$APP_DIR"
    run_logged "$ARBITER_LOG" "$ARBITER" init
    ok "arbiter init done"

    if [[ -f "$APP_DIR/access_graph.json" ]]; then
        info "Attempting arbiter register (expected to fail — upstream schema mismatch)"
        "$ARBITER" register access_graph.json >> "$ARBITER_LOG" 2>&1 \
            && ok "arbiter register succeeded" \
            || warn "arbiter register failed 'Graph contains no nodes' — known upstream bug"
    else
        warn "access_graph.json not found — skipping register"
    fi
    record "3-arbiter" "ok"
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — BATON
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 4 — Baton"
BATON_LOG="$LOG_DIR/4-baton.log"

if is_done "4-baton"; then
    resumed "Baton already done — skipping"
    record "4-baton" "ok"
elif ! require_ok "2a-pact"; then
    record "4-baton" "fail"
elif [[ ! -x "$PACT" || ! -x "$BATON" ]]; then
    err "Pact or Baton binary not found"
    record "4-baton" "fail"
else
    step "Setting up Baton deployment circuit..."
    cd "$APP_DIR"

    # Generate baton.yaml via pact deploy
    run_logged "$BATON_LOG" "$PACT" deploy . \
        && ok "baton.yaml generated" \
        || warn "pact deploy returned non-zero"

    # Patch baton.yaml: add role: ingress + health_check
    if [[ -f "$APP_DIR/baton.yaml" ]]; then
        export APP_DIR
        python3 << 'PATCH' >> "$BATON_LOG" 2>&1
import yaml, os
path = os.path.join(os.environ['APP_DIR'], 'baton.yaml')
try:
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    nodes = cfg.get('nodes', [])
    if nodes:
        n = nodes[0]
        n.setdefault('role', 'ingress')
        port = n.get('port', 3000)
        n.setdefault('metadata', {})
        n['metadata']['health_check'] = f"http://127.0.0.1:{port}/health"
        n['metadata'].setdefault('canary_error_rate_pct', '5.0')
        n['metadata'].setdefault('canary_p95_ms', '500.0')
        cfg['nodes'] = nodes
        with open(path, 'w') as f:
            yaml.dump(cfg, f, default_flow_style=False)
        print(f"Patched: node={n.get('name')} role=ingress port={port}")
    else:
        print("No nodes in baton.yaml — skipping patch")
except Exception as e:
    print(f"Patch skipped: {e}")
PATCH
        info "baton.yaml patched (role: ingress)"
    fi

    run_logged "$BATON_LOG" "$BATON" status \
        && ok "baton status ok" \
        || warn "baton status non-zero"

    # Smoke test: run mock circuit for 15s
    step "Mock circuit smoke test (15s)..."
    "$BATON" up --mock >> "$BATON_LOG" 2>&1 &
    BATON_PID=$!
    sleep 15
    if kill -0 "$BATON_PID" 2>/dev/null; then
        ok "Mock circuit ran 15s successfully"
        kill "$BATON_PID" 2>/dev/null || true
        wait "$BATON_PID" 2>/dev/null || true
    else
        warn "baton up --mock exited early — check $BATON_LOG"
    fi

    run_logged "$BATON_LOG" "$BATON" signals || true
    run_logged "$BATON_LOG" "$BATON" metrics || true
    record "4-baton" "ok"
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5a — SENTINEL
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 5a — Sentinel"
SENTINEL_LOG="$LOG_DIR/5a-sentinel.log"

if is_done "5a-sentinel"; then
    resumed "Sentinel already done — skipping"
    record "5a-sentinel" "ok"
elif ! require_ok "2a-pact"; then
    record "5a-sentinel" "fail"
elif [[ ! -x "$SENTINEL" ]]; then
    err "Binary not found: $SENTINEL"
    record "5a-sentinel" "fail"
else
    step "Setting up Sentinel production log watcher..."
    cd "$APP_DIR"

    run_logged "$SENTINEL_LOG" "$SENTINEL" init
    ok "sentinel init done"

    run_logged "$SENTINEL_LOG" "$SENTINEL" register . \
        && ok "components registered" \
        || warn "sentinel register non-zero"

    run_logged "$SENTINEL_LOG" "$SENTINEL" report
    ok "sentinel report done (no incidents expected)"

    cat >> sentinel.yaml << 'SENTINEL_YAML'

sources:
  - type: file
    path: .baton/service_logs.jsonl
    format: jsonl
    error_patterns:
      - '"severity": "error"'
      - 'Traceback'
      - '500 Internal Server Error'
SENTINEL_YAML
    info "sentinel.yaml configured with baton log source"

    # 5s probe to verify watch starts correctly
    timeout 5 "$SENTINEL" watch >> "$SENTINEL_LOG" 2>&1 || true
    ok "sentinel watch probe done"
    record "5a-sentinel" "ok"
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5b — CHRONICLER
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 5b — Chronicler"
CHRONICLER_LOG="$LOG_DIR/5b-chronicler.log"

if is_done "5b-chronicler"; then
    resumed "Chronicler already done — skipping"
elif ! require_ok "2a-pact"; then
    record "5b-chronicler" "fail"
    record "5b-chronicler" "ok"
elif [[ ! -x "$CHRONICLER_PY" ]]; then
    err "Chronicler Python not found"
    record "5b-chronicler" "fail"
else
    step "Configuring Chronicler event correlation engine..."
    info "Note: chronicler runtime not yet wired — config validation only"
    cd "$APP_DIR"

    cat > chronicler.yaml << 'CHRONICLER_YAML'
sources:
  - type: otlp
    bind_address: "0.0.0.0"
    port: 4317

  - type: sentinel
    bind_address: "0.0.0.0"
    port: 8081

sinks:
  - type: disk
    output_dir: .chronicler/stories

rules:
  - name: request_story
    match_conditions:
      - field: event_kind
        pattern: "span"
    group_by: [trace_id]
    window_seconds: 30

  - name: service_story
    match_conditions:
      - field: event_kind
        pattern: "span"
    group_by: [entity_id, component_id]
    window_seconds: 300

  - name: journey_story
    match_conditions:
      - field: event_kind
        pattern: "span"
    group_by: [session_id]
    window_seconds: 1800
CHRONICLER_YAML

    echo "# [$(date -u '+%Y-%m-%dT%H:%M:%SZ')] chronicler config validation" >> "$CHRONICLER_LOG"
    "$CHRONICLER_PY" -c "
from chronicler.config import load_config
cfg = load_config('chronicler.yaml')
print('Sources:', [s.type for s in cfg.sources])
print('Sinks:  ', [s.type for s in cfg.sinks])
print('Rules:  ', [r.name for r in cfg.rules])
" >> "$CHRONICLER_LOG" 2>&1 \
        && ok "chronicler config valid" \
        || warn "chronicler config validation non-zero"

    run_logged "$CHRONICLER_LOG" "$CHRONICLER_BIN" --help 2>/dev/null || true
    record "5b-chronicler" "ok"
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5c — STIGMERGY
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 5c — Stigmergy"
STIGMERGY_LOG="$LOG_DIR/5c-stigmergy.log"

if is_done "5c-stigmergy"; then
    resumed "Stigmergy already done — skipping"
    record "5c-stigmergy" "ok"
elif ! require_ok "2a-pact"; then
    record "5c-stigmergy" "fail"
elif [[ ! -x "$STIGMERGY" ]]; then
    err "Binary not found: $STIGMERGY"
    record "5c-stigmergy" "fail"
else
    step "Running Stigmergy signal analysis (mock mode, stub LLM)..."
    info "Writing config directly — skipping interactive init (stdin misalignment bug)"
    cd "$APP_DIR"

    mkdir -p .stigmergy
    cat > .stigmergy/config.yaml << 'STIGMERGY_CONFIG'
sources:
  github:
    mode: mock
    org: acme-org
    repos: []

llm:
  provider: stub
  daily_cap_usd: 1.0
  hourly_cap_usd: 0.10

storage:
  runs_dir: .stigmergy/runs
  insights_file: .stigmergy/insights.jsonl
STIGMERGY_CONFIG

    run_logged "$STIGMERGY_LOG" "$STIGMERGY" run --once \
        && ok "stigmergy run --once complete" \
        || warn "stigmergy run non-zero — check $STIGMERGY_LOG"

    run_logged "$STIGMERGY_LOG" "$STIGMERGY" status || true
    record "5c-stigmergy" "ok"
fi

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — APPRENTICE
# ══════════════════════════════════════════════════════════════════════════════
banner "Step 6 — Apprentice"
APPRENTICE_LOG="$LOG_DIR/6-apprentice.log"

if is_done "6-apprentice"; then
    resumed "Apprentice already done — skipping"
    record "6-apprentice" "ok"
elif ! require_ok "2a-pact"; then
    record "6-apprentice" "fail"
elif [[ ! -x "$APPRENTICE" ]]; then
    err "Binary not found: $APPRENTICE"
    record "6-apprentice" "fail"
else
    step "Setting up Apprentice LLM cost-optimisation proxy..."
    cd "$APP_DIR"

    # Write apprentice.yaml directly (wizard has input_schema field-name bug)
    cat > apprentice.yaml << 'APPRENTICE_YAML'
task:
  name: calculator_eval
  description: Evaluate arithmetic expressions
  prompt_template: |
    Given an arithmetic expression, return the numeric result.
    Input: {expression}
  input_schema:
    - name: expression
      type: string
      required: true
  output_schema:
    - name: result
  evaluator: exact_match

remote:
  provider: anthropic
  model: claude-haiku-4-5-20251001

local:
  url: http://localhost:11434
  base_model: llama3.1:8b

budget:
  daily_cap_usd: 10.0
  hourly_cap_usd: 2.0
APPRENTICE_YAML
    info "apprentice.yaml created (skipped interactive init — avoids wizard bug)"

    # Start daemon
    step "Starting apprentice serve..."
    ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" "$APPRENTICE" serve >> "$APPRENTICE_LOG" 2>&1 &
    APPRENTICE_PID=$!
    info "Apprentice PID: $APPRENTICE_PID"

    # Wait up to 30s for it to be ready
    READY=false
    for i in $(seq 1 15); do
        sleep 2
        if curl -sf http://127.0.0.1:8710/health >> "$APPRENTICE_LOG" 2>&1; then
            READY=true; break
        fi
        info "Waiting for apprentice... ($i/15)"
    done

    if [[ "$READY" == "true" ]]; then
        ok "Apprentice serving on 127.0.0.1:8710"

        run_logged "$APPRENTICE_LOG" "$APPRENTICE" status \
            && ok "apprentice status ok" \
            || warn "apprentice status non-zero"

        step "Test task: 2 + 2..."
        ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            "$APPRENTICE" run calculator_eval \
            --input '{"expression": "2 + 2"}' \
            >> "$APPRENTICE_LOG" 2>&1 \
            && ok "apprentice run succeeded" \
            || warn "apprentice run non-zero"

        run_logged "$APPRENTICE_LOG" "$APPRENTICE" report \
            && ok "apprentice report done" \
            || warn "apprentice report non-zero"

        record "6-apprentice" "ok"
    else
        warn "Apprentice not ready in 30s — check $APPRENTICE_LOG"
        record "6-apprentice" "warn"
    fi

    kill "$APPRENTICE_PID" 2>/dev/null || true
    wait "$APPRENTICE_PID" 2>/dev/null || true
    info "Apprentice daemon stopped"
fi

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
banner "Pipeline Summary"
echo ""
printf "  %-25s %s\n" "Step" "Result"
printf "  %-25s %s\n" "─────────────────────────" "──────"

ALL_OK=true
for STEP in "${STEPS_ORDERED[@]}"; do
    STATUS="${STEP_STATUS[$STEP]}"
    case "$STATUS" in
        ok)   printf "  %-25s ${GREEN}✓ ok${RESET}\n"   "$STEP" ;;
        warn) printf "  %-25s ${YELLOW}⚠ warn${RESET}\n" "$STEP" ; ALL_OK=false ;;
        fail) printf "  %-25s ${RED}✗ fail${RESET}\n"  "$STEP" ; ALL_OK=false ;;
    esac
done

echo ""
echo -e "  ${BOLD}Dir:${RESET}   $APP_DIR"
echo -e "  ${BOLD}Logs:${RESET}  $LOG_DIR/"
echo ""

echo -e "  ${BOLD}Log files:${RESET}"
for LOG in "$LOG_DIR"/*.log; do
    [[ -f "$LOG" ]] && printf "    %-35s %s lines\n" "$(basename "$LOG")" "$(wc -l < "$LOG")"
done

echo ""
if [[ "$ALL_OK" == "true" ]]; then
    echo -e "  ${GREEN}${BOLD}All steps passed.${RESET}"
else
    echo -e "  ${YELLOW}${BOLD}Some steps had warnings/failures.${RESET}"
    echo -e "  ${DIM}To resume: ./build-app.sh $PRIME_FILE $APP_NAME${RESET}"
fi
echo ""
