#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# exemplar.tools — Repository Installer
# https://exemplar.tools
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
#
# Environment overrides:
#   EXEMPLAR_INSTALL_DIR  — base installation directory (default: ./exemplar.tools)
#   EXEMPLAR_CONFIG_URL   — URL or local path to a repos.conf file
#   EXEMPLAR_VERSION      — pin to a specific release tag (e.g. v1.2.0); omit for latest
#   EXEMPLAR_NO_DEPS      — skip all dependency installation (set to any non-empty value)
#   EXEMPLAR_NO_COLOR     — disable colored output (set to any non-empty value)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Constants ─────────────────────────────────────────────────────────────────
readonly INSTALLER_VERSION="1.0.0"
readonly REPO="vaskoevgen/exemplar.tools-installer"
_ref="${EXEMPLAR_VERSION:-main}"
readonly RAW_BASE="https://raw.githubusercontent.com/${REPO}/${_ref}"
readonly DEFAULT_CONFIG_URL="${RAW_BASE}/repos.conf"

EXEMPLAR_INSTALL_DIR="${EXEMPLAR_INSTALL_DIR:-$(pwd)/exemplar.tools}"
EXEMPLAR_CONFIG_URL="${EXEMPLAR_CONFIG_URL:-${DEFAULT_CONFIG_URL}}"

# ── Colors ────────────────────────────────────────────────────────────────────
if [[ -z "${EXEMPLAR_NO_COLOR:-}" && -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  BLUE='\033[0;34m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; BLUE=''; BOLD=''; DIM=''; NC=''
fi

# ── Logging ───────────────────────────────────────────────────────────────────
log_info()    { echo -e "${BLUE}  →${NC} $*"; }
log_success() { echo -e "${GREEN}  ✓${NC} $*"; }
log_warn()    { echo -e "${YELLOW}  !${NC} $*"; }
log_error()   { echo -e "${RED}  ✗${NC} $*" >&2; }
log_step()    { echo -e "\n${BOLD}$*${NC}"; }

# ── Banner ────────────────────────────────────────────────────────────────────
print_banner() {
  echo ""
  echo -e "${BOLD}  exemplar.tools installer${NC}  ${DIM}v${INSTALLER_VERSION}${NC}  ${DIM}(ref: ${_ref})${NC}"
  echo -e "  ${DIM}https://exemplar.tools${NC}"
  echo ""
}

# ── Dependency check ──────────────────────────────────────────────────────────
check_deps() {
  local missing=()
  for cmd in git curl; do
    command -v "$cmd" &>/dev/null || missing+=("$cmd")
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    log_error "Required tools not found: ${missing[*]}"
    log_error "Install them and re-run this script."
    exit 1
  fi
}

# ── Fetch config ──────────────────────────────────────────────────────────────
# Supports HTTP(S) URLs and local file paths.
fetch_config() {
  local source="$1"
  if [[ "$source" == http://* || "$source" == https://* ]]; then
    curl -fsSL "$source"
  else
    # Local file path
    source="${source/#\~/$HOME}"
    if [[ ! -f "$source" ]]; then
      log_error "Config file not found: $source"
      exit 1
    fi
    cat "$source"
  fi
}

# ── Python venv setup ─────────────────────────────────────────────────────────
setup_python() {
  local dir="$1"

  local deps_file="" install_cmd=""
  if [[ -f "${dir}/requirements.txt" ]]; then
    deps_file="requirements.txt"
    install_cmd="pip install --quiet -r requirements.txt"
  elif [[ -f "${dir}/pyproject.toml" ]]; then
    deps_file="pyproject.toml"
    install_cmd="pip install --quiet -e ."
  elif [[ -f "${dir}/setup.py" ]]; then
    deps_file="setup.py"
    install_cmd="pip install --quiet -e ."
  else
    return 0
  fi

  if ! command -v python3 &>/dev/null; then
    log_warn "Python: python3 not found — skipping (${deps_file} detected)"
    return 0
  fi

  log_info "Python: ${deps_file} detected"
  local venv="${dir}/.venv"
  if [[ ! -d "$venv" ]]; then
    log_info "Python: creating .venv"
    python3 -m venv "$venv"
  fi
  log_info "Python: installing dependencies"
  (cd "$dir" && "$venv/bin/pip" install --quiet --upgrade pip && $venv/bin/$install_cmd)
  log_success "Python: .venv ready"
}

# ── Node.js deps setup ────────────────────────────────────────────────────────
setup_node() {
  local dir="$1"
  [[ -f "${dir}/package.json" ]] || return 0

  if ! command -v npm &>/dev/null; then
    log_warn "Node.js: npm not found — skipping (package.json detected)"
    return 0
  fi

  log_info "Node.js: package.json detected"
  (cd "$dir" && npm install --silent)
  log_success "Node.js: node_modules ready"
}

# ── Rust deps setup ───────────────────────────────────────────────────────────
setup_rust() {
  local dir="$1"
  [[ -f "${dir}/Cargo.toml" ]] || return 0

  if ! command -v cargo &>/dev/null; then
    log_warn "Rust: cargo not found — skipping (Cargo.toml detected)"
    return 0
  fi

  log_info "Rust: Cargo.toml detected"
  (cd "$dir" && cargo fetch --quiet)
  log_success "Rust: dependencies fetched"
}

# ── Install dependencies (auto-detects language) ─────────────────────────────
setup_deps() {
  local dir="$1"
  [[ -n "${EXEMPLAR_NO_DEPS:-}" ]] && return 0
  setup_python "$dir"
  setup_node   "$dir"
  setup_rust   "$dir"
}

# ── Resolve whether a ref is a tag ───────────────────────────────────────────
is_tag() {
  git tag --list | grep -qx "$1"
}

# ── Clone or update a single repository ──────────────────────────────────────
process_repo() {
  local url="$1" ref="$2" dir="$3"

  # Expand tilde
  dir="${dir/#\~/$HOME}"

  if [[ -d "${dir}/.git" ]]; then
    # ── Update existing repo ──────────────────────────────────────────────────
    log_step "Updating  ${url}"
    log_info  "Location: ${dir}"
    log_info  "Ref:      ${ref}"

    pushd "$dir" >/dev/null

    git fetch --all --tags --prune --quiet 2>/dev/null || {
      log_warn "fetch failed — working with cached state"
    }

    if is_tag "$ref"; then
      local current_tag
      current_tag=$(git describe --tags --exact-match HEAD 2>/dev/null || true)
      if [[ "$current_tag" == "$ref" ]]; then
        log_success "Already at tag ${ref} — nothing to do"
      else
        git checkout --quiet "$ref"
        log_success "Checked out tag ${ref}"
      fi
    else
      # Branch — ensure we're on it and up to date
      local current_branch
      current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)
      if [[ "$current_branch" != "$ref" ]]; then
        git checkout --quiet "$ref" 2>/dev/null \
          || git checkout --quiet -b "$ref" --track "origin/${ref}"
      fi
      git pull --ff-only --quiet origin "$ref"
      log_success "Branch ${ref} is up to date"
    fi

    popd >/dev/null

  else
    # ── Clone new repo ────────────────────────────────────────────────────────
    log_step "Cloning   ${url}"
    log_info  "Location: ${dir}"
    log_info  "Ref:      ${ref}"

    mkdir -p "$(dirname "$dir")"
    git clone --branch "$ref" --quiet "$url" "$dir"
    log_success "Cloned successfully"
  fi

  setup_deps "$dir"
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
  print_banner
  check_deps

  log_info "Config:       ${EXEMPLAR_CONFIG_URL}"
  log_info "Install dir:  ${EXEMPLAR_INSTALL_DIR}"

  local config_content
  config_content=$(fetch_config "$EXEMPLAR_CONFIG_URL")

  local total=0 success=0 failed=0
  local failed_repos=()

  while IFS= read -r line; do
    # Skip blank lines and comments
    [[ -z "${line//[[:space:]]/}" ]] && continue
    [[ "$line" =~ ^[[:space:]]*# ]]  && continue

    # Parse columns: url  ref  [dir]
    local url ref dir
    read -r url ref dir <<< "$line"
    [[ -z "$url" || -z "$ref" ]] && continue

    # Default local dir: <install_dir>/<repo-name>
    if [[ -z "$dir" ]]; then
      local repo_name
      repo_name="$(basename "$url" .git)"
      dir="${EXEMPLAR_INSTALL_DIR}/${repo_name}"
    fi

    total=$((total + 1))

    if process_repo "$url" "$ref" "$dir"; then
      success=$((success + 1))
    else
      log_error "Failed: ${url}"
      failed=$((failed + 1))
      failed_repos+=("$url")
    fi

  done <<< "$config_content"

  # ── Summary ────────────────────────────────────────────────────────────────
  echo ""
  echo -e "${DIM}  ──────────────────────────────────────────${NC}"
  if [[ $total -eq 0 ]]; then
    log_warn "No repositories found in config. Add entries to repos.conf."
  elif [[ $failed -eq 0 ]]; then
    log_success "All ${total} repositories are up to date."
  else
    log_warn "${success}/${total} succeeded, ${failed} failed:"
    for r in "${failed_repos[@]}"; do
      log_error "  ${r}"
    done
    exit 1
  fi
  echo -e "${DIM}  ──────────────────────────────────────────${NC}"
  echo ""
}

main "$@"
