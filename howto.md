# How to use exemplar.tools

## Quick start — minimum path to a working app

Three steps take you from idea to deployed, tested code:

```
Step 1 — Constrain   describe what to build → structured artifacts
Step 2a — Pact       build the code → contracts, tests, implementation
Step 4 — Baton       deploy it → running circuit of services
```

Everything else (Ledger, Advocate, Arbiter, Sentinel, Kindex) adds governance,
quality, and observability on top. You don't need them to ship.

---

## Prerequisites

- **Python 3.11+** — required by all tools
- **Git** — for the installer
- **curl** — for the installer
- **Anthropic API key** with access to `claude-opus-4-6`

---

## Directory layout

The installer creates `exemplar.tools/` as a sibling to your project folder:

```
parent/
├── your-project/        ← your working directory throughout this guide
└── exemplar.tools/      ← cloned by the installer (run from parent/)
    ├── constrain/
    ├── pact/
    ├── baton/
    ├── sentinel/
    └── kindex/
```

## Install

Run once **from the parent directory** to clone all repositories and set up dependencies:

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```

Then enter your project folder — all commands below are run from there:

```bash
cd your-project
```

---

## Step 0 — Cartographer (existing projects only)

Cartographer scans an existing codebase and produces draft artifacts for every tool in the stack. Use this step **instead of Step 1** when onboarding a project that already has code — it replaces the Constrain interview with automated discovery.

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/cartographer/.venv/bin/activate

# fish
source ../exemplar.tools/cartographer/.venv/bin/activate.fish
```

**Initialize:**

```bash
cartographer init
# Creates cartographer.yaml with default settings
```

**Edit `cartographer.yaml`** — point it at your source and infrastructure:

```yaml
version: "1.0"

targets:
  source:
    dirs: ["./src"]
    languages: [python, typescript, javascript, go]
    exclude: [".venv", "node_modules", "dist", "__pycache__"]

  # Optional: live backend introspection (read-only)
  infrastructure:
    backends:
      - id: main_db
        type: postgres
        connection_hint: "postgres://user:pass@localhost:5432/mydb"
        owner_component_hint: my_service

  # Optional: running services to probe for OpenAPI specs
  services:
    base_urls:
      - "http://localhost:8001"
    openapi_paths:
      - "./specs/service.yaml"

# Point to existing stack artifacts (for compatibility checking)
stack:
  pact_project_dir: null
  baton_config: null
  ledger_registry: null
  sentinel_manifest: null

output_dir: ".cartographer/drafts/"
```

**Run discovery:**

```bash
# Source code only (safe, no network calls)
cartographer discover --no-live

# Source + live backends and services
cartographer discover
```

Cartographer scans for components, ORM models, API routes, PACT keys, env vars, and sensitive fields, then writes draft artifacts to `.cartographer/drafts/`:

```
.cartographer/drafts/
  constrain/   ← prompt, constraints, component_map, trust_policy, schema_hints
  pact/        ← contracts per component, task description
  ledger/      ← backend and schema definitions
  baton/       ← circuit topology
  sentinel/    ← component manifest
```

**Review the drafts:**

```bash
cartographer drafts list
cartographer drafts show pact my_component_draft.yaml
cartographer drafts show ledger main_db_users_draft.yaml
```

**Check stack compatibility:**

```bash
cartographer check
# Shows PASS / WARN / FAIL per tool with recommended next steps
```

**Adopt high-confidence items** (preview first, then apply):

```bash
cartographer adopt --dry-run             # preview what would be registered
cartographer adopt --confidence high     # register high-confidence drafts
cartographer adopt --confidence medium   # then medium
```

> Every draft item has a `_confidence` level (high/medium/low) and a `_note` explaining the evidence. Fields requiring classification (PII, financial, auth) must be confirmed explicitly with `--confirm-classification`.

**Check again** — score should improve. Repeat until compliant:

```bash
cartographer check
```

```bash
deactivate
```

### What each confidence level means

| Level | Source | Action needed |
|-------|--------|--------------|
| **high** | AST analysis, direct ORM definition | Safe to adopt, verify intent |
| **medium** | Pattern matching, heuristics | Review before adopting |
| **low** | Name-based guessing | Must verify — do not adopt blindly |

---

## Step 1 — Specify

### 1a — Constrain (Boundaries & components)

Constrain runs an **interactive AI interview** about your problem. It asks clarifying questions and resolves ambiguities before producing structured artifacts. Expect 5–15 minutes of back-and-forth. Answer the questions directly — Constrain will stop when it has enough to proceed.

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/constrain/.venv/bin/activate

# fish
source ../exemplar.tools/constrain/.venv/bin/activate.fish
```

**Set your API key:**

```bash
# bash / zsh
export ANTHROPIC_API_KEY=sk-...

# fish
set -x ANTHROPIC_API_KEY sk-...
```

**Run from your project directory:**

```bash
constrain
```

> **First run tip:** Constrain prints `Add '.constrain/' to your .gitignore` on startup — do it:
> ```bash
> echo '.constrain/' >> .gitignore
> ```

> **On startup:** Constrain asks `Prime with documents before starting? [y/N]`. Answer `n` for a fresh interactive session, or `y` to feed it a description file (see non-interactive mode below).

> **Transmogrifier warning:** A `UserWarning: Field name "register" shadows an attribute in parent "BaseModel"` appears on every run. It is safe to ignore — it comes from an upstream dependency.

> **Three phases:** Constrain runs `understand` (asks questions) → `challenge` (stress-tests your answers) → `synthesize` (generates artifacts). You cannot skip phases but you can answer briefly — Constrain moves on when it has enough information.

> **Accepting artifacts:** At the end Constrain shows a `Feedback>` prompt. Review the generated files shown in the terminal, then press **Enter** to accept and write them to disk.

**Non-interactive mode** — skip the interview entirely by priming with a description document and setting both round counts to 0:

```bash
constrain new --min-challenge 0 --max-challenge 0 --min-understand 0 --max-understand 0 -p prime.md
```

Write `prime.md` as a plain-English description of what to build. Constrain ingests it, extracts requirements, and generates all artifacts in one pass — no back-and-forth needed.

> **Prime document tip:** Do not use `{...}` JSON examples in the prime document (e.g. `{"title": "string"}`). Curly braces cause the YAML generator to crash with a mapping error. Describe JSON shapes in plain English instead — e.g. "a JSON object with a title field" or "returns the created task with its id, title, completed, and created_at fields".

Constrain will interview you about what you want to build. When it finishes, it writes these files to your current directory:

| File | Consumed by |
|------|-------------|
| `prompt.md` | Pact — system briefing |
| `constraints.yaml` | Pact, Sentinel |
| `component_map.yaml` | Pact, Baton |
| `trust_policy.yaml` | Arbiter |
| `schema_hints.yaml` | Ledger |

```bash
deactivate
```

---

### 1b — Ledger (Schema obligations) — optional

Ledger registers your storage schemas and data rules, then exports obligations into Pact contracts, Arbiter, Baton, and Sentinel. **Skip this step if your project has no database schemas.**

> **Integration status:** `ledger init` and `ledger builtins list/show` are fully implemented. `ledger backend add` has a bug (TypeError: 4 args to 3-arg function) — register backends directly in `ledger.yaml` instead. `ledger schema add`, `ledger schema validate`, and `ledger export` are stubs — they exit 0 but schema validation runs implicitly at config load time. Track progress at [jmcentire/ledger#2](https://github.com/jmcentire/ledger/pull/2).

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/ledger/.venv/bin/activate

# fish
source ../exemplar.tools/ledger/.venv/bin/activate.fish
```

**Initialize Ledger in your project directory:**

```bash
ledger init
# Creates: ledger.yaml, schemas/, plans/, changelog.yaml
```

**Register a backend** — add directly to `ledger.yaml` (`ledger backend add` has a bug):

```yaml
# ledger.yaml
backends:
  - name: my_db        # required
    base_url: ""       # optional, default ""
```

> Backend model fields: `name`, `enabled`, `base_url`, `timeout_ms`. There is no `owner` or `type` field.

**Create a schema YAML** in `schemas/`:

```yaml
# schemas/tasks.yaml
name: tasks          # required
version: 1           # required — integer, not "1.0"

fields:
  - name: id
    field_type: uuid
    classification: PUBLIC
    nullable: false
    annotations:
      - name: immutable      # annotations are dicts with 'name' key — not bare strings
      - name: not_null

  - name: title
    field_type: varchar(255)
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null

  - name: completed
    field_type: boolean
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null

  - name: priority
    field_type: integer
    classification: PUBLIC
    nullable: false
    annotations:
      - name: not_null

  - name: due_date
    field_type: date
    classification: PUBLIC
    nullable: true

  - name: created_at
    field_type: timestamptz
    classification: PUBLIC
    nullable: false
    annotations:
      - name: immutable
      - name: not_null
```

> Valid `classification` values: `PUBLIC`, `PII`, `FINANCIAL`, `AUTH`, `COMPLIANCE`.

> Valid `field_type` values follow SQL conventions: `uuid`, `varchar(n)`, `boolean`, `integer`, `date`, `timestamptz`, etc. The key is `field_type`, not `type`.

**Register and validate the schema:**

```bash
ledger schema add schemas/tasks.yaml   # exits 0; no output on success
ledger schema validate                 # exits 0; no output if valid
```

> Both commands are silent on success — no output means it worked.

**Explore the built-in annotation catalogue:**

```bash
ledger builtins list
ledger builtins show immutable
```

**Export obligations** (stub — returns empty contracts until implemented):

```bash
ledger export --format pact
# {'contracts': []}

ledger export --format arbiter
# {'contracts': []}
```

> The `{'contracts': []}` output is expected — export is not yet implemented. The commands exit 0.

```bash
deactivate
```

---

### 1c — Database setup (required before Pact if your app uses PostgreSQL)

If your project connects to PostgreSQL, spin up the test database **before** starting the Pact daemon. Pact runs contract tests against a real database — there are no mocks.

#### macOS (Docker Desktop) — port 5432 is mandatory

Docker Desktop on macOS only proxies PostgreSQL SCRAM-SHA-256 authentication correctly through the **standard port 5432**. Other ports (5433, 5434, etc.) fail with `fe_sendauth: no password supplied` or `FATAL: password authentication failed` regardless of pg_hba.conf settings.

```bash
# Check if port 5432 is already in use
lsof -i :5432 | grep LISTEN

# If free, start a postgres container on 5432
docker run -d \
  --name pact-test-pg \
  -e POSTGRES_USER=pact \
  -e POSTGRES_PASSWORD=pact \
  -e POSTGRES_DB=<yourapp>_test \
  -p 5432:5432 \
  arm64v8/postgres:17-alpine

# Wait for it to be ready (usually < 5 seconds) in ZSH
until docker exec pact-test-pg pg_isready -U pact; do sleep 1; done
```

> Use `arm64v8/postgres:17-alpine` on Apple Silicon. The plain `postgres:17-alpine` image may silently pull the wrong architecture and misbehave.

#### Create the schema

Run your migration SQL before pact so the tables exist for the test harness:

```bash
docker exec -i pact-test-pg psql -U pact -d <yourapp>_test << 'SQL'
-- paste your CREATE TABLE statements here
SQL
```

#### Set DATABASE_URL and TEST_DATABASE_URL

Both variables must be set in the shell that starts the Pact daemon:

```bash
# bash / zsh
export DATABASE_URL=postgresql://pact:pact@127.0.0.1:5432/<yourapp>_test
export TEST_DATABASE_URL=postgresql://pact:pact@127.0.0.1:5432/<yourapp>_test

# fish
set -x DATABASE_URL postgresql://pact:pact@127.0.0.1:5432/<yourapp>_test
set -x TEST_DATABASE_URL postgresql://pact:pact@127.0.0.1:5432/<yourapp>_test
```

> Pact passes these to the test harness as-is. Both should point to the same test database — Pact does not use a separate application database during testing.

#### Also add your project venv to PATH

Pact's test runner calls `python3` from the system PATH. If your project depends on third-party libraries (FastAPI, psycopg2, etc.), your project venv must be on PATH before the daemon starts:

```bash
# bash / zsh — prepend your project venv
export PATH="/absolute/path/to/your/project/.venv/bin:$PATH"

# fish
fish_add_path --prepend /absolute/path/to/your/project/.venv/bin
```

Then start the daemon:

```bash
source ../exemplar.tools/pact/.venv/bin/activate  # (or .fish)
```

It is ready for `pact` stage

---

## Step 2 — Build

### 2a — Pact

Pact builds the software using the artifacts produced by Constrain. It decomposes your task into components, writes contracts and tests, then implements each component via the Anthropic API.

**Cost and time:** a typical run costs **$1–3** and takes **10–30 minutes** depending on project size and the `budget` setting.

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/pact/.venv/bin/activate

# fish
source ../exemplar.tools/pact/.venv/bin/activate.fish
```

**Set your API key:**

```bash
# bash / zsh
export ANTHROPIC_API_KEY=sk-...

# fish
set -x ANTHROPIC_API_KEY sk-...
```

> In fish shell, `export VAR=value` is not valid — use `set -x` instead.

**Initialize the project** (run from your project folder):

```bash
pact init .
```

> Run `pact init .` in your **project root directory** (e.g. `todo-list2/`), not a subdirectory. Pact creates `task.md`, `pact.yaml`, and `sops.md` in place. If Constrain artifacts (`prompt.md`, `constraints.yaml`, etc.) are already present, Pact picks them up automatically.

> **`pact init .` creates a partial `pact.yaml`** with only `budget: 10.0`. You must add the remaining required fields (see below) before running the daemon.

**Edit `task.md`** — describe what to build. Be specific. Example:

```markdown
# Task

Build a CLI tool that reads a text file containing one URL per line,
checks whether each URL is reachable via HTTP GET, and reports which
ones are unreachable.

## Requirements

- Accept a file path as a CLI argument
- Skip blank lines and lines starting with #
- Support --timeout (default 5s), --concurrency (default 10), --json flags
- Exit 0 if all reachable, exit 1 if any unreachable
```

> Constraints like "single file under 300 lines" in `task.md` are guidance to the agent, not hard limits — the implementation may exceed them. To enforce a constraint mechanically, add it to `sops.md` or ensure the generated contract tests cover it.

**Edit `sops.md`** — coding standards (style, language, constraints).

> **Critical:** `pact init .` writes a default `sops.md` containing `Language: Python 3.12+` and `Testing: pytest`. If your app is **not** Python (e.g. Node.js, TypeScript, Go), update `sops.md` to match your stack **before** running the daemon. If `sops.md` says Python, Pact will generate Python regardless of what `task.md` says.

**Edit `pact.yaml`** — add the required fields to the file created by `pact init .`:

```yaml
budget: 10.0
shaping: false
build_mode: unary
backend: anthropic
model: claude-opus-4-6
role_backends:
  decomposer: anthropic
  contract_author: anthropic
  test_author: anthropic
  code_author: anthropic
```

> Without `role_backends`, pact defaults to `claude_code` for implementation which requires Claude Code CLI. Set all roles to `anthropic` to use the direct API.

> **`build_mode: unary`** builds the entire app as a single component named `root`. This is the only stable mode. It collapses multi-tier architectures (frontend + backend + database) into one unit — the generated code will use in-memory storage instead of a real database. A real multi-component build mode is not yet available.

> Pact always writes `access_graph.json` at the end of the build — used by Arbiter in Step 3.

**Run the daemon:**

```bash
pact daemon .
```

> **Transmogrifier warning:** A `UserWarning: Field name "register" shadows an attribute` appears when the daemon starts. Safe to ignore — it comes from an upstream dependency.

Monitor progress in a second terminal:

```bash
pact status .        # current phase and cost
pact log .           # full audit trail
```

**Interview phase** — Pact pauses after generating questions. Answer by editing two files:

**1. `decomposition/interview.json`** — find the `"questions"` array, add a `"user_answers"` field with your answers, and set `"approved": true` at the top level:

```json
{
  "approved": true,
  "questions": [...],
  "user_answers": {
    "1": "In-memory storage, no persistence needed",
    "2": "Python stdlib only, no third-party libraries",
    "3": "..."
  }
}
```

**2. `.pact/state.json`** — set `"status": "active"`, `"approved": true`, and add an `"interview_result"` key that mirrors the answers:

```json
{
  "status": "active",
  "approved": true,
  "interview_result": {
    "approved": true,
    "user_answers": {
      "1": "In-memory storage, no persistence needed",
      "2": "Python stdlib only, no third-party libraries",
      "3": "..."
    }
  }
}
```

Then signal the daemon:
```bash
pact approve .
```

> `pact approve .` may print "Already approved. Daemon signaled to continue." — this is expected, not an error.

**Health gate** — Pact may pause mid-run with a "dysmemic pressure" health warning. These are false positives caused by four known bugs in the health checker (PR open: [jmcentire/pact#2](https://github.com/jmcentire/pact/pull/2)). Resume each time it pauses:

```bash
pact resume .
```

> **Known bugs (until PR #2 merges):** The health gate fires spuriously at multiple points in every build:
>
> | Check | When it fires | Root cause |
> |-------|--------------|------------|
> | `output_planning_ratio` | Before any code is written | `generation_tokens == 0` triggers ratio calculation |
> | `variance_reaches_target` | During `preflight`, `integrate`, `arbiter`, `polish`, etc. | Only `interview` and `shape` were whitelisted as pre-artifact phases |
> | `phase_balance` | Whenever `implement` dominates token spend | Execution phases dominating is expected, not an error |
>
> **Workaround:** each time the build pauses, run `pact resume .`. You may need to do this 3–5 times per build. If the daemon has exited (10 min idle timeout), restart it first:
>
> ```bash
> # Set env vars (same as when you first started it), then:
> pact daemon . &
> pact resume .
> ```

> If the daemon process exits entirely (rather than just pausing), check that `ANTHROPIC_API_KEY` is set in the shell that runs `pact daemon .`. If the state ends up as `"status": "failed"` in `.pact/state.json`, reset it manually: set `"status"` back to `"active"` and clear `"completed_at"` and `"pause_reason"`, then rerun `pact daemon .`.

**Verify the build — run contract tests:**

```bash
PYTHONPATH=src/<component> \
  pytest tests/<component>/contract_test.py -q
```

> Replace `<component>` with the component name (e.g. `root`).

```bash
deactivate
```

---

### 2b — Advocate (Review gate)

Advocate runs a 6-persona adversarial review of the code produced by Pact. Six AI reviewers attack the code simultaneously from different angles and surface issues before you deploy.

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/advocate/.venv/bin/activate

# fish
source ../exemplar.tools/advocate/.venv/bin/activate.fish
```

**Set your API key:**

```bash
# bash / zsh
export ANTHROPIC_API_KEY=sk-...

# fish
set -x ANTHROPIC_API_KEY sk-...
```

> **Transmogrifier warning:** A `UserWarning: Field name "register" shadows an attribute` appears on startup. Safe to ignore.

**Run the review** — save findings to JSON and HTML in one command:

```bash
advocate review src/ -o findings.json --html review-report.html
```

> Each persona prints its findings to the terminal in real time as it finishes. The full review takes ~30 seconds in parallel mode. **The HTML report is easier to read than the JSON** — open `review-report.html` in a browser after the run.

**Focus on specific personas:**

```bash
advocate review src/ -p red_team -p adversarial   # security focus
advocate review src/ -p sage -p user               # design/clarity focus
```

**Cheaper sequential mode (same results, lower cost):**

```bash
advocate review src/ --sequential
```

```bash
deactivate
```

### The six personas

| Persona | Angle |
|---------|-------|
| **Red Team** | It's vulnerable — harden it |
| **Adversarial** | It's wrong — defend your assumptions |
| **Sage** | It's complicated — simplify it |
| **User** | It's unintuitive — clarify it |
| **SME** | Peer review — would a colleague sign off? |
| **Good Friend** | The harsh truth you need to hear |

> **Disagreements are valuable.** When two personas rate the same issue differently (e.g. Sage: HIGH, SME: INFO), that tension reveals a real tradeoff worth examining.

**Typical cost:** ~$0.15–0.30 per review, ~30 seconds in parallel mode.

---

## Step 3 — Govern: Arbiter

> **Integration in progress.** Arbiter CLI commands (`init`, `canary`, `trust`, `report`) work. However, the Pact → Arbiter integration is not yet complete:
> - `arbiter watch` / `arbiter serve` (live sidecar) are not yet implemented
> - Pact writes `access_graph.json` using a `components` schema; Arbiter `register` expects a `nodes` schema — these don't match yet
>
> **For now: run `arbiter init` to confirm the tool works, then skip ahead to Step 4.** The `register` command will always fail at this stage.

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/arbiter/.venv/bin/activate

# fish
source ../exemplar.tools/arbiter/.venv/bin/activate.fish
```

**Initialize:**

```bash
arbiter init
# Creates: .arbiter/registry/trust_ledger.jsonl
#          arbiter.yaml
```

**Attempt to register the access graph** — this will fail with the error below, which is expected:

```bash
arbiter register access_graph.json
# Error: Graph contains no nodes
```

> This error means the `access_graph.json` schema Pact writes (`components`) does not match what Arbiter `register` expects (`nodes`). It is a known upstream bug — not something you did wrong. Move on to Step 4.

```bash
deactivate
```

---

> **Future workflow** (once schemas are aligned):
>
> ```bash
> arbiter register access_graph.json
> arbiter canary inject --tiers PUBLIC
> arbiter canary results --run <run_id>
> arbiter trust show <node_id>
> arbiter report --run <run_id>
> arbiter blast-radius <node_id> <version>
> ```
>
> If a canary escapes, the node's trust score drops to 0. Recovery requires human review:
> ```bash
> arbiter trust reset-taint <node_id> --review <ticket_id>
> ```

### Key concepts

| Concept | What it means |
|---------|--------------|
| **Trust score** | 0.1–1.0 per node, built from audit events. Canary escape → 0.0 |
| **Trust tier** | PROBATIONARY → LOW → ESTABLISHED → HIGH → TRUSTED |
| **Authority domain** | One node owns each domain — enforced at register time |
| **Blast radius** | Impact surface of a change: affected nodes × data tiers × soak requirement |
| **Canary** | Synthetic fingerprinted data injected to detect leakage across component boundaries |

---

## Step 4 — Deploy: Baton

Baton orchestrates deployment as a self-healing circuit topology using the `component_map.yaml` from Constrain.

**Step 1 — Generate `baton.yaml` using the Pact venv:**

```bash
# bash / zsh
source ../exemplar.tools/pact/.venv/bin/activate

# fish
source ../exemplar.tools/pact/.venv/bin/activate.fish

pact deploy .
deactivate
```

Expected output:
```
Generated baton.yaml: <your-project>/baton.yaml
  Nodes: 1
  Edges: 0
  Observability: jsonl
  Canary thresholds: error_rate < 5.0%, p95 < 500.0ms
```

> `pact deploy .` generates a `baton.yaml` with one node named `root` on port 3000. It does **not** use `component_map.yaml` — the multi-component topology from Constrain is ignored. You must edit the file before use.

**Step 2 — Activate Baton:**

```bash
# bash / zsh
source ../exemplar.tools/baton/.venv/bin/activate

# fish
source ../exemplar.tools/baton/.venv/bin/activate.fish
```

**Step 3 — Edit `baton.yaml`** — add `role: ingress`, set the correct port, and fix the health check endpoint:

```yaml
nodes:
- name: root
  port: 3001             # ← change from default 3000 to your app's actual port
  role: ingress          # ← required on entry-point nodes
  metadata:
    health_check: http://127.0.0.1:3001/tasks   # ← use a real endpoint, not /health
    canary_error_rate_pct: '5.0'
    canary_p95_ms: '500.0'
```

**Step 4 — Verify the circuit loaded correctly:**

```bash
baton status
```

Expected output:
```
Circuit: root (v1)
Nodes:   1
Edges:   0

  Name       Role       Port   Mode   Contract
  ─────────────────────────────────────────────
  root       [ingress]  3001   http   —
```

**Step 5 — Boot in mock mode** (no live app needed):

```bash
baton up --mock
```

Expected output:
```
Circuit 'root' is up (1 nodes)
  root: active

Entry points:
  root: 127.0.0.1:3001

Press Ctrl+C to stop
```

Visit `http://127.0.0.1:3001` in your browser — you'll see `{"status": "mock", "port": 23001}`. Press **Ctrl+C** to stop.

> **To run with a live app:** start your application in a separate terminal first, then run `baton up` (without `--mock`). Note that Pact generates `src/root/root.py` as a pure Python library with no HTTP server — you need to wrap it in FastAPI/Flask before Baton can proxy to it.

**Step 6 — Check signals and metrics:**

```bash
baton signals    # recent request signals
baton metrics    # persistent metrics
```

> In mock mode, both commands return "No signal data found" / "No metrics data found" — this is expected. Mock mode serves fixed responses without generating telemetry.

**Hot-swap a component without downtime:**

```bash
baton swap <node-name> --image <new-image>
```

```bash
deactivate
```

---

## Step 5 — Observe

### 5a — Sentinel

Sentinel watches production logs, attributes errors to Pact components via embedded PACT keys, and tightens contracts so each bug class becomes non-recurring.

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/sentinel/.venv/bin/activate

# fish
source ../exemplar.tools/sentinel/.venv/bin/activate.fish
```

**Initialize** (run from your project directory):

```bash
sentinel init
# Created sentinel.yaml
# Initialized .sentinel/
```

**Register Pact components** — imports PACT keys from `src/`:

```bash
sentinel register .
#   Registered: root
#
# Registered 1 components from .
```

**View incident report:**

```bash
sentinel report
# No incidents recorded.
```

> `No incidents recorded.` is the expected output on a fresh project with no live traffic. This is not an error.

**Optionally start the log watcher** — blocks until Ctrl+C:

```bash
sentinel serve
# (press Ctrl+C to stop)
```

> `sentinel serve` starts an HTTP API that watches your application logs in real time. When it sees an error, it matches it to the PACT key embedded in the source code (e.g. `PACT:481349:root:create_task`), attributes it to the responsible component, and records it as an incident. **Skip this if your app is not running** — there are no logs to watch.

```bash
deactivate
```

---

### 5b — Chronicler

Chronicler sits between your running services and the pattern-learning layer. It collects events (OTLP spans, webhooks, Sentinel incidents, log files), groups them into **stories** at three granularities, and forwards completed stories to Stigmergy and Apprentice.

| Story type | Grouped by | Timeout | Meaning |
|---|---|---|---|
| Request | `trace_id` | 30 s | One request and its downstream spans |
| Service | `entity_id` + `component_id` | 5 m | Sequence of requests to one component |
| Journey | `session_id` | 30 m | Full causal chain across components |

> **Integration status:** Chronicler's configuration schema and correlation engine are fully implemented. The CLI start/status/stories/replay commands parse correctly but the runtime handlers are not yet wired up — all commands currently return immediately without side effects. Use Chronicler today to validate your config and understand the story model; the live event collection path ships in the next release.

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/chronicler/.venv/bin/activate

# fish
source ../exemplar.tools/chronicler/.venv/bin/activate.fish
```

**Create `chronicler.yaml` in your project folder:**

```yaml
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
```

**Validate the config (config parsing is fully implemented):**

```bash
python -c "
from chronicler.config import load_config
cfg = load_config('chronicler.yaml')
print('Sources:', [s.type for s in cfg.sources])
print('Sinks:  ', [s.type for s in cfg.sinks])
print('Rules:  ', [r.name for r in cfg.rules])
"
```

Expected output:
```
Sources: [<SourceType.otlp: 'otlp'>, <SourceType.sentinel: 'sentinel'>]
Sinks:   [<SinkType.disk: 'disk'>]
Rules:   ['request_story', 'service_story', 'journey_story']
```

**Check available commands:**

```bash
chronicler --help
```

Expected output:
```
usage: chronicler [-h] {start,status,stories,replay} ...

Chronicler event collector

positional arguments:
  {start,status,stories,replay}
    start               Start the Chronicler engine
    status              Show engine status
    stories             Story management
    replay              Replay JSONL events

options:
  -h, --help            show this help message and exit
```

> All four subcommands parse correctly but return immediately without side effects — the runtime is not yet wired up.

**Deactivate when done:**

```bash
deactivate
```

#### Sink types

| Sink | What it does | Status |
|---|---|---|
| `disk` | Writes stories as JSONL files to `output_dir` | Implemented |
| `stigmergy` | Forwards stories to Stigmergy for pattern mining | Placeholder |
| `apprentice` | Forwards stories to Apprentice for model distillation | Placeholder |
| `kindex` | Stores noteworthy stories in the knowledge graph | Placeholder |

Only the `disk` sink is fully implemented. Use it to capture stories locally while the network sinks are in progress.

#### Adding Stigmergy / Apprentice / Kindex sinks (future)

When these tools are running, add them to `chronicler.yaml`:

```yaml
sinks:
  - type: disk
    output_dir: .chronicler/stories

  - type: stigmergy
    url: http://localhost:8400

  - type: apprentice
    url: http://localhost:8401

  - type: kindex
    url: http://localhost:8402

kindex:
  noteworthiness_threshold: 0.7
  event_type_filters: ["span", "incident"]
```

---

### 5c — Stigmergy

Stigmergy ingests signals from GitHub, Linear, Slack, and Grafana, routes them through a self-organizing agent mesh, and surfaces structural patterns: coordination gaps, knowledge silos, and parallel activity that could become conflicts.

It runs without an LLM key — the default `stub` provider uses deterministic heuristics at zero cost. Swap to `anthropic` for richer analysis when needed.

**Activate:**

```bash
source ../exemplar.tools/stigmergy/.venv/bin/activate.fish
```

**Initialize (interactive setup):**

```bash
stigmergy init
```

If `ANTHROPIC_API_KEY` is not set, the wizard prints `env ANTHROPIC_API_KEY not set (will use stub LLM)` — that is expected. Answer prompts as follows:

| Prompt | Recommended value for testing |
|---|---|
| What should stigmergy monitor? | *(Enter — keep default)* |
| Enable GitHub? | Y |
| Use default repos? | Y |
| GitHub mode | `mock` *(no `gh` auth needed)* |
| Enable Linear? | N |
| Enable Grafana? | N |
| LLM provider | `stub` *(no API key needed)* |
| Daily cap / Hourly cap | *(Enter — keep defaults)* |

Expected confirmation:

```
Config written to .stigmergy/config.yaml
  16 GitHub repos, 0 Linear teams, provider=stub
Run `stigmergy run --once` to process signals.
```

**Run one batch (mock data, no API key):**

```bash
stigmergy run --once
```

Expected output (trimmed):

```
Mesh initialized: 3 workers, 2 agents, 16 repos, 0 packages, 0 edges

Connecting github  (mock)...
  github: 7 signals fetched

Routing 7 signals through mesh...
  [1/7] $0.00 spent   [GITHUB]  acme-org/backend  @alice.chen
  ...
  >> PARALLEL ACTIVITY  61%  @bob.martinez and @alice.chen in same signal space

Mesh Session Summary
  Signals processed:  7
  Accepted:           7
  Total cost:         $0.0000

  Persisted 3 insights to .stigmergy/insights.jsonl
```

All findings are mock data from the built-in stub. The run is archived to `.stigmergy/runs/`.

> **Note:** The agent intelligence report will show `WARNING: 2 agents running without LLM — mechanical heuristics producing noise`. This is expected in stub mode — findings are still written to disk.

**View status from last run:**

```bash
stigmergy status
```

**To use real Anthropic analysis:**

```bash
# fish shell
set -x ANTHROPIC_API_KEY your-key
stigmergy init   # re-run and choose 'anthropic' for LLM provider
```

**Deactivate when done:**

```bash
deactivate
```

#### Signal sources

| Source | Mode | Requires |
|---|---|---|
| GitHub | `mock` (default) or `live` | `gh auth login` for live |
| Linear | `mock` or `live` | `LINEAR_API_KEY` for live |
| Grafana | `mock` or `live` | `GRAFANA_API_KEY` for live |

#### LLM providers

| Provider | Cost | Quality |
|---|---|---|
| `stub` (default) | Free | Deterministic heuristics |
| `anthropic` | ~$0.01/run | LLM-enhanced assessments (Haiku) |

---

## Step 6 — Learn: Apprentice

Apprentice routes every request to the frontier API (Claude, GPT, etc.), collects the responses as training examples, fine-tunes a local model, then progressively shifts traffic to it — while continuously verifying quality. The goal: replace expensive API calls with a $0 local model that produces equivalent results for your specific tasks.

> **Prerequisite:** Ollama must be installed and running with the base model pulled:
> ```bash
> brew install ollama
> ollama pull llama3.1:8b
> ollama serve   # keep running in background
> ```
> Skip this step if you do not have Ollama — `apprentice serve` will start but fine-tuning will not trigger.

**Three phases, all automatic:**

| Phase | What happens |
|---|---|
| Cold Start | Every request → remote API. Responses stored as training data. |
| Reinforcement | Both models run. Evaluator scores local vs. remote. Rolling window tracks correlation. |
| Steady State | Local model handles most traffic. Sampler periodically checks quality. Auto-regresses if it drops. |

**Activate:**

```bash
source ../exemplar.tools/apprentice/.venv/bin/activate.fish
```

**Set your API key (required before `serve`):**

```bash
# fish shell
set -x ANTHROPIC_API_KEY your-key
```

**Initialize — create `apprentice.yaml`:**

```bash
apprentice init
```

The wizard walks through 4 steps: task definition, remote provider (Claude/GPT), local model (Ollama endpoint), and budget caps. Answer prompts:

| Prompt | Example answer |
|---|---|
| Task name | `calculator_eval` |
| Description | *(Enter — keep default)* |
| Prompt template | `Given an arithmetic expression, return the numeric result.`<br>`Input: {expression}`<br>*(blank line to finish)* |
| Input fields | *(Enter — keep default `text` for now — see warning below)* |
| Output fields | `result` |
| Evaluator | *(Enter — keep `exact_match`)* |
| Provider | `anthropic` |
| Model | `claude-haiku-4-5-20251001` |
| Ollama URL / Base model / Budget | *(Enter — keep defaults)* |

> **Wizard bug:** The wizard ignores your prompt template's `{expression}` variable and always writes `name: text` to `input_schema` in `apprentice.yaml`. After `init`, open `apprentice.yaml` and change:
> ```yaml
> # wrong (wizard default)
> input_schema:
>   - name: text
>
> # correct
> input_schema:
>   - name: expression
>     type: string
>     required: true
> ```
> If you skip this fix, `apprentice serve` will exit with a validation error about unknown input_schema properties.

**Start the HTTP daemon:**

```bash
apprentice serve
```

Note: the `--config` flag does not exist. `serve` always reads `./apprentice.yaml` from the current directory.

Expected output:
```
Loading config from ./apprentice.yaml...
Apprentice serving on 127.0.0.1:8710
  Health:          http://127.0.0.1:8710/health
  Run:             POST http://127.0.0.1:8710/v1/run
  Status:          http://127.0.0.1:8710/v1/status
  Report:          http://127.0.0.1:8710/v1/report
  Pipeline interval: 300s
```

`serve` is blocking — open a second terminal for the commands below.

**Check current phase and training progress:**

```bash
apprentice status
```

Expected output (task starts in `bootstrapping` with confidence `0.00`):
```
Task: calculator_eval
  Phase: bootstrapping
  Confidence: 0.00
  Local Primary: True
  Budget: 0.00 / 10.00
```

**Execute a task:**

```bash
apprentice run calculator_eval --input '{"expression": "2 + 2"}'
```

> **Known bug:** `apprentice run` crashes immediately with `Error: 'TaskResponse' object has no attribute 'success'`. The task never executes. No CLI workaround — the HTTP API at `POST http://127.0.0.1:8710/v1/run` may work directly via `curl`. See `UPSTREAM_BUGS.md`.

**Generate a full report:**

```bash
apprentice report
```

> **Known bug:** `apprentice report` crashes with `Error: 'SystemReport' object has no attribute 'tasks'`. See `UPSTREAM_BUGS.md`.

**Deactivate when done:**

```bash
deactivate
```

#### Evaluator types

| Type | What it checks |
|---|---|
| `exact_match` | Field values must match exactly |
| `semantic_similarity` | Embedding cosine similarity above threshold |
| `llm_judge` | A second LLM call scores the local output |
| `regex_match` | Output must match a regex pattern |
| `json_schema_match` | Output must conform to a JSON schema |

#### PII protection

Apprentice includes built-in PII scrubbing before data reaches models or training stores. Default mode uses regex patterns (emails, phones, SSNs, credit cards, API keys). Enable NER-based detection for unstructured text by installing the `ml` extra:

```bash
pip install -e ".[ml]"
```

---

## Step 7 — Knowledge: Kindex

Kindex is a persistent knowledge graph that learns from your sessions and provides context to every tool in the stack.

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/kindex/.venv/bin/activate

# fish
source ../exemplar.tools/kindex/.venv/bin/activate.fish
```

**Basic usage:**

```bash
kin init
kin add "key insight from this session"
kin search "pact contracts"
kin context "deployment"        # pull context block for CLAUDE.md
```

**Register with Claude Code (MCP):**

```bash
claude mcp add --scope user --transport stdio kindex -- kin-mcp
```

```bash
deactivate
```

---

## Optional Tools

### Webprobe

> **Coming soon.** Webprobe maps any website as a directed graph, captures per-node metrics, scans for security vulnerabilities, and uses LLM agents to discover visual and behavioural defects. Useful for auditing deployed services.

---

### Signet

> **Coming soon.** Signet is a cryptographic identity vault and MCP server. It manages credentials, generates zero-knowledge proofs, and enforces privacy policies — data flows one-way: vault → agent → service.

---

### Tessera

> **Coming soon.** Tessera is a self-validating executable document format. Every document carries its schema, state, history, and cryptographic signatures — the chain can be verified without an external authority.

---

## The Closed Loop

```
[Cartographer]  ← optional: existing projects only
      ↓
[Constrain]  →  prompt.md, constraints.yaml, component_map.yaml, trust_policy.yaml, schema_hints.yaml
      ↓                                    ↓
  [Ledger]                             [Arbiter init]
  (schemas)                            arbiter watch (sidecar, port 7700)
      ↓                                    ↓
    export assertions            ┌─────────────────────┐
      ↓                          │                     │
[Pact]  →  src/, tests/, access_graph.json  →  [Arbiter register]
      ↓                                            ↓
  [Advocate]                              trust scores, blast radius
  (code review gate)
      ↓
[Baton]  →  circuit up  →  OTLP spans  →  Arbiter
      ↓
[Sentinel]  →  incidents, contract tightening
      ↓                    ↓
[Chronicler]  →  stories (request / service / journey)
      ↓                    ↓
[Stigmergy]          [Apprentice]
(org patterns)    (model distillation)

[Kindex]  ←  cross-cutting knowledge layer (all tools feed into it)
```

**Feedback loops:**
- `Sentinel → Constrain` — production bugs tighten contracts, preventing the whole class from recurring
- `Chronicler → Apprentice` — production traffic trains local models, progressively reducing API cost

---

## Troubleshooting

### pact uses the wrong binary (fish)

`~/.local/bin/pact` (uv-managed) overrides the venv. Add to `~/.config/fish/config.fish`:

```fish
function pact
    /path/to/exemplar.tools/pact/.venv/bin/pact $argv
end
```

### pact keeps reporting the same failure

Run state is cached. Clear it and retry:

```bash
pact clean . --all
pact daemon .
```

### Switching between tools

Each tool has its own `.venv`. Deactivate before activating another:

```bash
deactivate
source ../exemplar.tools/kindex/.venv/bin/activate.fish
```

### Updating all repositories

Re-run the installer from the parent directory at any time to pull latest changes:

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```
