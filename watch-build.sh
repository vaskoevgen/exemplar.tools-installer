#!/usr/bin/env bash
# watch-build.sh — real-time monitor for a build-app.sh pipeline run
#
# Usage:
#   ./watch-build.sh <APP_DIR> [interval-seconds] [--ai]
#
# Examples:
#   ./watch-build.sh apps/my-app-name           # 30s poll, no AI
#   ./watch-build.sh apps/my-app-name 15        # 15s poll
#   ./watch-build.sh apps/my-app-name 15 --ai   # with Claude Haiku diagnosis
#
# What it does each poll:
#   1. Dashboard — step-by-step status table (ok/warn/fail/pending)
#   2. Log stream — new lines from the active step's log (no repeats)
#   3. Pact deep — pact state.json status/phase/cost when step 2a is active
#   4. Diagnosis — when a step fails: pattern-matched report + fix hints
#      pointing to exact lines in build-app.sh and component configs
#   5. AI analysis — when --ai: calls Claude Haiku for richer root cause
#
# NOTE: no set -e — grep exits 1 on no-match and would kill the script silently.
# All errors handled explicitly.

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR/exemplar.tools"
ENV_FILE="$SCRIPT_DIR/.env"

# ── Args ──────────────────────────────────────────────────────────────────────
USE_AI=false
APP_DIR_RAW=""
INTERVAL=30
for arg in "$@"; do
    case "$arg" in
        --ai) USE_AI=true ;;
        [0-9]*) INTERVAL="$arg" ;;
        *) APP_DIR_RAW="$arg" ;;
    esac
done

if [[ -z "$APP_DIR_RAW" ]]; then
    echo "Usage: $0 <APP_DIR> [interval-seconds] [--ai]"
    echo "  APP_DIR: path to app folder, e.g. apps/my-app-name"
    exit 1
fi

APP_DIR="$(cd "$APP_DIR_RAW" 2>/dev/null && pwd)" || {
    echo "ERROR: APP_DIR not found: $APP_DIR_RAW"
    exit 1
}

LOG_DIR="$APP_DIR/logs"
STATE_FILE="$APP_DIR/.pipeline-state"
PACT="$TOOLS_DIR/pact/.venv/bin/pact"

# ── Load env ──────────────────────────────────────────────────────────────────
[[ -f "$ENV_FILE" ]] && source "$ENV_FILE"

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'
DIM='\033[2m'; RESET='\033[0m'

ts()  { date '+%H:%M:%S'; }
sep() { printf "${DIM}"; printf '%0.s─' {1..72}; printf "${RESET}"; echo; }
banner() {
    echo -e "\n${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${BOLD}${BLUE}  $1${RESET}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
}

# ── Steps config ──────────────────────────────────────────────────────────────
STEPS=(1a-constrain 1b-ledger 2a-pact 2b-advocate 3-arbiter 4-baton 5a-sentinel 5b-chronicler 5c-stigmergy 6-apprentice)

declare -A STEP_LOG=(
    [1a-constrain]="1a-constrain.log"
    [1b-ledger]="1b-ledger.log"
    [2a-pact]="2a-pact.log"
    [2b-advocate]="2b-advocate.log"
    [3-arbiter]="3-arbiter.log"
    [4-baton]="4-baton.log"
    [5a-sentinel]="5a-sentinel.log"
    [5b-chronicler]="5b-chronicler.log"
    [5c-stigmergy]="5c-stigmergy.log"
    [6-apprentice]="6-apprentice.log"
)

declare -A STEP_LABEL=(
    [1a-constrain]="1a  Constrain"
    [1b-ledger]="1b  Ledger"
    [2a-pact]="2a  Pact"
    [2b-advocate]="2b  Advocate"
    [3-arbiter]="3   Arbiter"
    [4-baton]="4   Baton"
    [5a-sentinel]="5a  Sentinel"
    [5b-chronicler]="5b  Chronicler"
    [5c-stigmergy]="5c  Stigmergy"
    [6-apprentice]="6   Apprentice"
)

# ── State readers ─────────────────────────────────────────────────────────────
step_state() {
    grep "^${1}=" "$STATE_FILE" 2>/dev/null | tail -1 | cut -d= -f2
}

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
        6-apprentice) [[ -f "$APP_DIR/apprentice.yaml" ]] ;;
        *) return 1 ;;
    esac
}

# Effective state: state file entry wins; artifact detection as fallback.
# For pact-dependent steps, a cached 'ok' is overridden to 'fail' if pact itself failed.
PACT_DEPENDENT=(2b-advocate 3-arbiter 4-baton 5a-sentinel 5b-chronicler 5c-stigmergy 6-apprentice)

is_pact_dependent() {
    local S; for S in "${PACT_DEPENDENT[@]}"; do [[ "$S" == "$1" ]] && return 0; done; return 1
}

effective_state() {
    # Pact-dependent steps: if pact failed, report fail regardless of cached state
    if is_pact_dependent "$1" && [[ "$(step_state "2a-pact")" == "fail" ]]; then
        echo "fail"
        return
    fi

    local VAL
    VAL=$(step_state "$1")
    if [[ -n "$VAL" ]]; then
        echo "$VAL"
    elif artifact_done "$1" 2>/dev/null; then
        echo "ok"
    else
        echo ""
    fi
}

# ── Dashboard ─────────────────────────────────────────────────────────────────
print_dashboard() {
    echo -e "\n${BOLD}Pipeline — $(basename "$APP_DIR")${RESET}  ${DIM}$(date '+%H:%M:%S')${RESET}"
    printf "  %-18s %s\n" "Step" "Status"
    printf "  %-18s %s\n" "──────────────────" "────────────────────────"

    local STARTED=false
    for STEP in "${STEPS[@]}"; do
        local VAL LABEL
        VAL=$(effective_state "$STEP")
        LABEL="${STEP_LABEL[$STEP]:-$STEP}"

        case "$VAL" in
            ok)   printf "  %-18s ${GREEN}✓ ok${RESET}\n"   "$LABEL" ;;
            warn) printf "  %-18s ${YELLOW}⚠ warn${RESET}\n" "$LABEL" ;;
            fail) printf "  %-18s ${RED}✗ fail${RESET}\n"  "$LABEL" ; STARTED=true ;;
            "")
                if [[ "$STARTED" == "false" ]]; then
                    # Check if there's a log file — it's running
                    if [[ -f "$LOG_DIR/${STEP_LOG[$STEP]:-}" ]]; then
                        printf "  %-18s ${CYAN}⏳ running…${RESET}\n" "$LABEL"
                        STARTED=true
                    else
                        printf "  %-18s ${DIM}… pending${RESET}\n" "$LABEL"
                    fi
                else
                    printf "  %-18s ${DIM}… pending${RESET}\n" "$LABEL"
                fi
                ;;
        esac

        # After the first non-done step, the rest are pending
        if [[ "$VAL" != "ok" && "$VAL" != "warn" ]]; then
            STARTED=true
        fi
    done
    echo ""
}

# ── Which step is active (first non-done) ─────────────────────────────────────
active_step() {
    for STEP in "${STEPS[@]}"; do
        local VAL
        VAL=$(effective_state "$STEP")
        if [[ "$VAL" != "ok" && "$VAL" != "warn" ]]; then
            echo "$STEP"
            return
        fi
    done
    echo ""
}

# ── First failed step ─────────────────────────────────────────────────────────
failed_step() {
    for STEP in "${STEPS[@]}"; do
        local VAL
        VAL=$(step_state "$STEP")
        if [[ "$VAL" == "fail" ]]; then
            echo "$STEP"
            return
        fi
    done
    echo ""
}

# ── Incremental log tailer ────────────────────────────────────────────────────
declare -A SEEN_LINES

init_seen_lines() {
    for STEP in "${STEPS[@]}"; do
        local LOG="$LOG_DIR/${STEP_LOG[$STEP]:-}"
        if [[ -f "$LOG" ]]; then
            SEEN_LINES[$STEP]=$(wc -l < "$LOG")
        else
            SEEN_LINES[$STEP]=0
        fi
    done
}

tail_log() {
    local STEP="$1"
    local LOG="$LOG_DIR/${STEP_LOG[$STEP]:-${STEP}.log}"
    [[ -f "$LOG" ]] || return

    local CURRENT SEEN DELTA
    CURRENT=$(wc -l < "$LOG")
    SEEN="${SEEN_LINES[$STEP]:-0}"
    DELTA=$(( CURRENT - SEEN ))

    if (( DELTA > 0 )); then
        local NEW_LINES
        NEW_LINES=$(tail -n "$DELTA" "$LOG" \
            | grep -v "HTTP Request\|Research complete\|Plan evaluation\|Code authored" \
            || true)

        if [[ -n "$NEW_LINES" ]]; then
            local LINE_COUNT
            LINE_COUNT=$(echo "$NEW_LINES" | wc -l | tr -d ' ')
            echo -e "  ${DIM}┌─ ${STEP} — ${LINE_COUNT} new log line(s) ─────────────────────────────────${RESET}"
            echo "$NEW_LINES" | tail -20 | sed "s/^/  ${DIM}│${RESET} /"
            echo -e "  ${DIM}└──────────────────────────────────────────────────────────────────${RESET}"
        fi
        SEEN_LINES[$STEP]="$CURRENT"
    fi
}

# ── Pact deep status ──────────────────────────────────────────────────────────
pact_deep_status() {
    local STATE="$APP_DIR/.pact/state.json"
    [[ -f "$STATE" ]] || return

    local STATUS PHASE PAUSE COST
    STATUS=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('status','?'))" 2>/dev/null || echo "?")
    PHASE=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('phase','?'))" 2>/dev/null || echo "?")
    PAUSE=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('pause_reason','') or '')" 2>/dev/null || echo "")

    COST=$(python3 -c "
import re
try:
    log = open('$LOG_DIR/2a-pact.log').read()
    tokens = sum(int(t) for t in re.findall(r'\((\d+) tokens\)', log))
    if tokens > 0:
        lo = tokens/1e6*15; hi = tokens/1e6*75
        print(f'\${lo:.2f}~\${hi:.2f} ({tokens:,} tok)')
    else: print('?')
except: print('?')
" 2>/dev/null || echo "?")

    echo -e "  ${BOLD}Pact state.json:${RESET}  status=${CYAN}${STATUS}${RESET}  phase=${CYAN}${PHASE}${RESET}  cost=${CYAN}${COST}${RESET}"
    [[ -n "$PAUSE" ]] && echo -e "  ${YELLOW}⚠  pause_reason: ${PAUSE}${RESET}"

    # Pact binary status (if available)
    if [[ -x "$PACT" ]]; then
        local PSTATUS
        PSTATUS=$("$PACT" status "$APP_DIR" 2>&1 | head -4 || true)
        if [[ -n "$PSTATUS" ]]; then
            echo "$PSTATUS" | sed "s/^/  ${DIM}pact status: /" | sed "s/$/${RESET}/"
        fi
    fi
}

# ── Failure diagnosis helpers ─────────────────────────────────────────────────
_hint() { echo -e "    ${YELLOW}▸${RESET} $1"; }
_fix()  { echo -e "    ${GREEN}  Fix:${RESET} $1"; }
_ref()  { echo -e "    ${DIM}  Ref:  $1${RESET}"; }

diagnose() {
    local STEP="$1"
    local LOG="$LOG_DIR/${STEP_LOG[$STEP]:-${STEP}.log}"

    echo ""
    echo -e "${RED}${BOLD}━━━ FAILURE DIAGNOSIS: ${STEP} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

    if [[ -f "$LOG" ]]; then
        echo -e "  ${BOLD}Last relevant log lines:${RESET}"
        grep -v "HTTP Request\|Research complete\|Plan evaluation\|Code authored" "$LOG" 2>/dev/null \
            | tail -15 | sed 's/^/    /'
        echo ""
    else
        echo -e "  ${DIM}No log file found: $LOG${RESET}"
    fi

    echo -e "  ${BOLD}Analysis:${RESET}"

    case "$STEP" in
        1a-constrain) _diag_constrain "$LOG" ;;
        1b-ledger)    _diag_ledger    "$LOG" ;;
        2a-pact)      _diag_pact      "$LOG" ;;
        2b-advocate)  _diag_advocate  "$LOG" ;;
        3-arbiter)    _diag_arbiter   "$LOG" ;;
        4-baton)      _diag_baton     "$LOG" ;;
        5a-sentinel)  _diag_sentinel  "$LOG" ;;
        5b-chronicler)_diag_chronicler "$LOG" ;;
        5c-stigmergy) _diag_stigmergy "$LOG" ;;
        6-apprentice) _diag_apprentice "$LOG" ;;
    esac

    echo ""
    echo -e "  ${BOLD}Resume command:${RESET}"
    echo -e "  ${CYAN}  ./build-app.sh <prime.md> $(basename "$APP_DIR")${RESET}"
    echo -e "  ${DIM}  Full log: $LOG${RESET}"
    echo -e "${RED}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
}

# ── Per-step diagnosis functions ──────────────────────────────────────────────

_diag_constrain() {
    local LOG="$1"

    if [[ ! -f "$LOG" ]]; then
        _hint "Log missing — constrain binary likely not installed"
        _fix "Re-run install.sh from parent directory"
        _ref "build-app.sh:80 — CONSTRAIN binary path"
        return
    fi

    if grep -qi "api\|api_key\|unauthorized\|authentication\|invalid.*key" "$LOG" 2>/dev/null; then
        _hint "API key error — Claude API rejected the request"
        _fix "Check ANTHROPIC_API_KEY in .env file"
        _ref "build-app.sh:197-203 — env loading"
    fi

    if grep -qi "yaml.*error\|mapping.*error\|scanner.*error\|could not determine" "$LOG" 2>/dev/null; then
        _hint "YAML crash — almost certainly caused by curly braces { } in prime.md"
        _fix "Edit prime.md: remove all {…} JSON examples, describe shapes in plain English"
        _ref "howto.md:269 — 'Do not use {…} JSON examples in the prime document'"
        _ref "build-app.sh:237-258 — constrain invocation"
    fi

    if [[ ! -f "$APP_DIR/prompt.md" ]]; then
        _hint "prompt.md was not generated"
        _fix "Verify prime.md exists and has content before running"
        _ref "build-app.sh:102-103 — PRIME_FILE existence check"
    fi

    if grep -qi "no such file\|not found\|permission denied\|binary" "$LOG" 2>/dev/null; then
        _hint "Binary or file missing"
        _fix "Re-run: curl -fsSL .../install.sh | bash  (from parent directory)"
        _ref "build-app.sh:225-226 — binary executable check"
    fi
}

_diag_ledger() {
    _hint "Ledger: schema add/validate/export are stubs — they exit 0 (safe to ignore)"
    _hint "Real failure here = binary missing or .env not loaded"
    _fix "Re-run install.sh if ledger binary is missing"
    _ref "build-app.sh:270-271 — LEDGER binary check"
    _ref "howto.md:300 — 'schema add, validate, export are stubs — exit 0 but no-op'"
}

_diag_pact() {
    local LOG="$1"
    local STATE="$APP_DIR/.pact/state.json"

    if [[ -f "$STATE" ]]; then
        local STATUS PHASE PAUSE
        STATUS=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('status',''))" 2>/dev/null || echo "")
        PHASE=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('phase',''))" 2>/dev/null || echo "")
        PAUSE=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('pause_reason','') or '')" 2>/dev/null || echo "")

        _hint "state.json: status=${STATUS}  phase=${PHASE}"
        [[ -n "$PAUSE" ]] && _hint "pause_reason: ${PAUSE}"

        if [[ "$STATUS" == "failed" ]]; then
            _hint "Pact state is 'failed' — likely an API timeout or network stall"
            _fix "Reset state.json manually:"
            _fix "  python3 -c \"import json; p='$STATE'; d=json.load(open(p)); d.update({'status':'active','pause_reason':'','completed_at':''}); json.dump(d,open(p,'w'),indent=2)\""
            _fix "Then re-run: ./build-app.sh <prime.md> $(basename "$APP_DIR")"
            _ref "build-app.sh:641-664 — auto-reset logic (runs on next resume)"
        fi

        if echo "$PAUSE" | grep -qi "systemic\|import_error\|missing.*dependencies\|cascade\|rejection_rate"; then
            _hint "Systemic failure — pact keeps generating wrong/broken code in a loop"
            _fix "1. Check $APP_DIR/sops.md — first line should be the CRITICAL TypeScript line"
            _fix "2. Check $APP_DIR/pact.yaml — must have: language: typescript  test_framework: vitest"
            _fix "3. Add a specific rule to sops.md that addresses the pattern in pause_reason"
            _ref "build-app.sh:562-639 — language detection + sops.md override"
            _ref "howto.md:519-549 — pact sops.md and pact.yaml setup"
        fi

        if echo "$PAUSE" | grep -qi "interview\|user answer\|waiting for user"; then
            _hint "Interview phase needs approval — pact is waiting for a user decision"
            _fix "Run: $PACT approve $APP_DIR"
            _ref "build-app.sh:733-753 — auto-approve logic"
        fi

        if echo "$PAUSE" | grep -qi "budget\|budget_exceeded"; then
            _hint "Budget cap exceeded — pact stopped to avoid overspending"
            _fix "Edit $APP_DIR/pact.yaml — increase 'budget:' value (e.g. 20.0)"
            _ref "build-app.sh:796-825 — auto-bump logic (max 3×, \$10 each)"
        fi
    else
        _hint ".pact/state.json not found — pact daemon never started or APP_DIR wrong"
        _fix "Verify APP_DIR is correct: $APP_DIR"
        _fix "Check pact binary: $PACT"
    fi

    # Language mismatch check
    if [[ -f "$APP_DIR/sops.md" ]]; then
        if grep -q "Language: Python\|Language: python" "$APP_DIR/sops.md" 2>/dev/null; then
            if [[ -f "$APP_DIR/prime.md" ]] && grep -qi "typescript\|\.tsx\|react\|vite\|bun" "$APP_DIR/prime.md" 2>/dev/null; then
                _hint "⚠ LANGUAGE MISMATCH: sops.md says Python but prime.md targets TypeScript"
                _fix "Edit $APP_DIR/sops.md:"
                _fix "  1. First line must be: CRITICAL: implementation language is TypeScript. Never generate Python. All output files must be .ts or .tsx."
                _fix "  2. Change 'Language: Python 3.12+' to 'Language: typescript'"
                _ref "build-app.sh:586-619 — DETECTED_LANG detection (triggers on TypeScript keywords)"
                _ref "howto.md:519-521 — 'If your app is not Python, update sops.md'"
            fi
        fi
    fi

    if [[ -f "$LOG" ]] && grep -qi "max.*retries\|retries exceeded\|after.*retries" "$LOG" 2>/dev/null; then
        _hint "Pact exhausted all auto-retries (max 5)"
        _fix "Check ANTHROPIC_API_KEY quota and rate limits"
        _fix "Wait a few minutes then re-run"
        _ref "build-app.sh:684-685 — PACT_MAX_RETRIES=5  PACT_MAX_WAIT=14400"
    fi

    if [[ -f "$LOG" ]] && grep -qi "budget.*bump.*3\|budget.*total.*40" "$LOG" 2>/dev/null; then
        _hint "Budget auto-bumped 3 times (\$40 total) and still exceeded"
        _fix "Edit $APP_DIR/pact.yaml: set a higher 'budget:' (e.g. 50.0)"
        _fix "Consider breaking the task into smaller components"
        _ref "build-app.sh:796 — PACT_BUDGET_BUMPS max 3"
    fi
}

_diag_advocate() {
    local LOG="$1"

    if [[ ! -d "$APP_DIR/src" ]]; then
        _hint "No src/ directory — Pact did not generate any source code"
        _fix "Fix step 2a-pact first, then re-run build"
        _ref "build-app.sh:960-961 — requires src/ to exist"
    else
        _hint "Advocate exited non-zero but findings.json may still be useful"
        _fix "Check $APP_DIR/review-report.html for findings (open in browser)"
        _fix "This step is usually marked 'warn' not 'fail' — pipeline can continue"
        _ref "build-app.sh:974-977 — advocate marks warn on non-zero exit"
    fi
}

_diag_arbiter() {
    local LOG="$1"

    if [[ -f "$LOG" ]] && grep -qi "graph contains no nodes" "$LOG" 2>/dev/null; then
        _hint "Known upstream bug: access_graph.json schema mismatch (pact writes 'components', arbiter expects 'nodes')"
        _fix "This is expected and handled — build-app.sh marks arbiter 'ok' regardless"
        _ref "build-app.sh:1000-1008 — 'arbiter register failed — known upstream bug'"
        _ref "howto.md:728-737 — explains the mismatch and says to proceed to Step 4"
    else
        _hint "Arbiter failure"
        _fix "Check arbiter binary: $TOOLS_DIR/arbiter/.venv/bin/arbiter"
        _ref "build-app.sh:991-992 — binary check"
    fi
}

_diag_baton() {
    local LOG="$1"

    if [[ ! -f "$APP_DIR/baton.yaml" ]]; then
        _hint "baton.yaml not generated by pact deploy"
        _fix "Check step 2a-pact completed with status 'ok'"
        _fix "Run manually: $TOOLS_DIR/pact/.venv/bin/pact deploy $APP_DIR"
        _ref "build-app.sh:1030-1033 — pact deploy generates baton.yaml"
    fi

    if [[ -f "$LOG" ]] && grep -qi "yaml.*error\|parse.*error\|no nodes" "$LOG" 2>/dev/null; then
        _hint "baton.yaml has a format error"
        _fix "Check $APP_DIR/baton.yaml"
        _fix "The Python patch that adds role:ingress may have failed"
        _ref "build-app.sh:1036-1060 — Python YAML patch"
    fi

    if [[ -f "$LOG" ]] && grep -qi "port.*already.*use\|address.*in use\|bind" "$LOG" 2>/dev/null; then
        _hint "Port already in use"
        _fix "Kill the process using the port: lsof -i :<port>  then kill <PID>"
    fi
}

_diag_sentinel() {
    local LOG="$1"
    local BIN="$TOOLS_DIR/sentinel/.venv/bin/sentinel"

    if [[ ! -x "$BIN" ]]; then
        _hint "Sentinel binary not found: $BIN"
        _fix "Re-run install.sh"
        _ref "build-app.sh:1097 — SENTINEL binary path"
    else
        _hint "Sentinel failed despite binary existing"
        _fix "Check $LOG for the specific error"
        _ref "build-app.sh:1101-1131 — sentinel init / register / watch"
    fi
}

_diag_chronicler() {
    _hint "Chronicler failure"
    _hint "Note: chronicler runtime handlers are NOT yet implemented — config validation only"
    _fix "If config validation failed, check chronicler.yaml format"
    _ref "build-app.sh:1152-1201 — writes chronicler.yaml + validates config"
    _ref "howto.md:982 — 'runtime not yet wired — all commands return immediately'"
}

_diag_stigmergy() {
    local LOG="$1"

    if [[ -f "$LOG" ]] && grep -qi "mode: Y\|provider: N\|mode:.*Y\b" "$LOG" 2>/dev/null; then
        _hint "Stigmergy config has wrong values — stdin piping likely misaligned prompts"
        _fix "Check $APP_DIR/.stigmergy/config.yaml:"
        _fix "  sources.github.mode  must be 'mock' (not 'Y')"
        _fix "  llm.provider          must be 'stub' (not 'N')"
        _ref "build-app.sh:1224-1239 — writes config directly (avoids interactive init)"
        _ref "howto.md:1136 — stdin piping misalignment gotcha"
    else
        _hint "Stigmergy failed"
        _fix "Check $TOOLS_DIR/stigmergy/.venv/bin/stigmergy exists"
        _fix "Check $APP_DIR/.stigmergy/config.yaml is valid YAML"
        _ref "build-app.sh:1213-1247 — step 5c"
    fi
}

_diag_apprentice() {
    local LOG="$1"

    if [[ -f "$LOG" ]] && grep -qi "not ready in 30s\|not ready" "$LOG" 2>/dev/null; then
        _hint "Apprentice HTTP server did not start within 30s"
        _fix "Check $APP_DIR/apprentice.yaml — input_schema field name must match prompt template"
        _fix "  Wizard always writes 'name: text' — must match {expression} variable"
        _ref "howto.md:1289 — 'Wizard bug: always writes name: text'"
        _ref "build-app.sh:1268-1294 — writes apprentice.yaml directly"
    fi

    if [[ -f "$LOG" ]] && grep -qi "input_schema\|validation.*error\|api key.*unresolved\|unresolved" "$LOG" 2>/dev/null; then
        _hint "apprentice.yaml validation error or API key not set"
        _fix "Verify ANTHROPIC_API_KEY is in .env"
        _fix "Check input_schema in $APP_DIR/apprentice.yaml"
        _ref "howto.md:1311 — 'API key must be set before serve'"
    fi

    if [[ -f "$LOG" ]] && grep -qi "attributeerror\|has no attribute" "$LOG" 2>/dev/null; then
        _hint "Known upstream CLI bug: AttributeError in apprentice run/report"
        _fix "Switch to fixed branch: vaskoevgen:fix/cli-run-and-report"
        _ref "howto.md:1347-1354 — two CLI bugs fixed in that branch"
    fi
}

# ── AI analysis ───────────────────────────────────────────────────────────────
ai_diagnose() {
    local STEP="$1"
    local LOG="$2"

    [[ -z "${ANTHROPIC_API_KEY:-}" ]] && {
        echo -e "  ${DIM}(--ai skipped: ANTHROPIC_API_KEY not set)${RESET}"
        return
    }
    [[ ! -f "$LOG" ]] && return

    echo -e "  ${DIM}[$(ts)] Asking Claude Haiku for root cause...${RESET}"

    local ERROR_CTX
    ERROR_CTX=$(grep -v "HTTP Request\|Research complete\|Plan evaluation\|Code authored" "$LOG" 2>/dev/null \
        | tail -50 || true)

    # Read relevant build-app.sh section for context (lines 1-200 = setup + constrain)
    local BUILD_CTX
    BUILD_CTX=$(sed -n '560,640p' "$SCRIPT_DIR/build-app.sh" 2>/dev/null || echo "")

    python3 - <<PYEOF
import json, urllib.request

api_key  = """${ANTHROPIC_API_KEY}"""
step     = """${STEP}"""
log_ctx  = """${ERROR_CTX}"""
build_ctx = """${BUILD_CTX}"""

prompt = f"""A build pipeline step '{step}' failed. Investigate the log and provide:

1. **Root cause** (1-2 sentences — specific file/function/config, not generic)
2. **Fix steps** (numbered list, include exact commands or file edits)
3. **build-app.sh location** (line range to look at, if applicable)

FAILED STEP LOG (last 50 relevant lines):
{log_ctx}

RELEVANT build-app.sh SECTION (language detection, sops.md override):
{build_ctx}

Reply in under 250 words. Be concrete — no generic advice."""

payload = json.dumps({
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 450,
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
        text = data["content"][0]["text"].strip()
        for line in text.split("\n"):
            print(f"    {line}")
except Exception as e:
    print(f"    AI diagnosis failed: {e}")
PYEOF
}

# ── Startup ───────────────────────────────────────────────────────────────────
banner "watch-build.sh  —  $(basename "$APP_DIR")"
echo -e "  ${BOLD}App dir:${RESET}  $APP_DIR"
echo -e "  ${BOLD}Interval:${RESET} ${INTERVAL}s"
echo -e "  ${BOLD}AI mode:${RESET}  ${USE_AI}  (--ai flag)"
echo -e "  ${BOLD}Tools:${RESET}    $TOOLS_DIR"
sep

if [[ ! -d "$APP_DIR" ]]; then
    echo -e "${RED}ERROR: APP_DIR does not exist: $APP_DIR${RESET}"
    exit 1
fi

if [[ ! -f "$STATE_FILE" ]] && [[ ! -d "$LOG_DIR" ]]; then
    echo -e "  ${DIM}Pipeline not started yet — waiting for build-app.sh to begin...${RESET}"
fi

echo -e "  ${DIM}[$(ts)] starting — logs initialised (only new lines will be shown)${RESET}"

# Seed SEEN_LINES so we don't flood with pre-existing log content on first poll
init_seen_lines

sep

# ── Main loop ─────────────────────────────────────────────────────────────────
LAST_DIAGNOSED=""

while true; do
    print_dashboard

    ACTIVE=$(active_step)
    FAILED=$(failed_step)

    # Show deep pact status when pact step is active
    if [[ "$ACTIVE" == "2a-pact" ]]; then
        pact_deep_status
        echo ""
    fi

    # Stream new log lines for the active step
    if [[ -n "$ACTIVE" ]]; then
        tail_log "$ACTIVE"
    fi

    # Diagnose newly failed step (only once per failure)
    if [[ -n "$FAILED" && "$FAILED" != "$LAST_DIAGNOSED" ]]; then
        diagnose "$FAILED"

        if [[ "$USE_AI" == "true" ]]; then
            echo -e "\n  ${BOLD}Claude Haiku AI analysis (--ai):${RESET}"
            ai_diagnose "$FAILED" "$LOG_DIR/${STEP_LOG[$FAILED]:-${FAILED}.log}"
            echo ""
        fi

        LAST_DIAGNOSED="$FAILED"
    fi

    # All steps done?
    ALL_DONE=true
    for STEP in "${STEPS[@]}"; do
        VAL=$(effective_state "$STEP")
        if [[ "$VAL" != "ok" && "$VAL" != "warn" ]]; then
            ALL_DONE=false
            break
        fi
    done

    if [[ "$ALL_DONE" == "true" ]]; then
        echo -e "${GREEN}${BOLD}✓ All pipeline steps completed — $(basename "$APP_DIR") is ready.${RESET}"
        break
    fi

    sleep "$INTERVAL"
done
