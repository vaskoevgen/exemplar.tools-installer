# How to use exemplar.tools

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
export ANTHROPIC_API_KEY=sk-...
```

**Run from your project directory:**

```bash
constrain
```

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

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/ledger/.venv/bin/activate

# fish
source ../exemplar.tools/ledger/.venv/bin/activate.fish
```

**Initialize and register schemas:**

```bash
ledger init
ledger backend add users_db --type postgres --owner user_service
ledger schema add schemas/users.yaml
ledger schema validate
```

**Export obligations to peer tools:**

```bash
ledger export --format pact --component user_service
ledger export --format arbiter
ledger export --format sentinel
```

```bash
deactivate
```

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
export ANTHROPIC_API_KEY=sk-...
```

**Initialize the project:**

```bash
pact init my-build
```

> `my-build` is the name of the Pact project subdirectory. You can call it anything.

**Edit `my-build/task.md`** — describe what to build. Be specific. Example:

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

**Edit `my-build/sops.md`** — coding standards (style, language, constraints). Leave blank to use defaults.

**Create `my-build/pact.yaml` before running** — this configuration is required:

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

> Pact always writes `my-build/access_graph.json` at the end of the build — used by Arbiter in Step 3.

**Run:**

```bash
pact run my-build
```

Pact runs autonomously. Monitor progress with:

```bash
pact status my-build        # current phase and state
pact components my-build    # list components and status
pact health my-build        # check for coordination issues
```

**Verify the build — run contract tests:**

```bash
PYTHONPATH=my-build/src \
  pytest my-build/tests/<component>/contract_test.py -q
```

> Replace `<component>` with the component directory name shown by `pact components`.

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
export ANTHROPIC_API_KEY=sk-...
```

**Review the built source:**

```bash
advocate review my-build/src/
```

**Save results for sharing or CI:**

```bash
advocate review my-build/src/ \
  -o findings.json \
  --html review-report.html
```

**Focus on specific personas:**

```bash
advocate review my-build/src/ -p red_team -p adversarial   # security focus
advocate review my-build/src/ -p sage -p user               # design/clarity focus
```

**Cheaper sequential mode (same results, lower cost):**

```bash
advocate review my-build/src/ --sequential
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
> Once the integration is complete, the workflow will be:

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
```

**Register the access graph produced by Pact** (once schemas are aligned):

```bash
arbiter register my-build/access_graph.json
# Registered: N nodes, N authority domains.
```

**Inject canaries and verify no data escapes:**

```bash
arbiter canary inject --tiers PUBLIC
arbiter canary results --run <run_id>
```

> If a canary escapes, the node's trust score drops to 0. Recovery requires human review:
> ```bash
> arbiter trust reset-taint <node_id> --review <ticket_id>
> ```

**After traffic flows**, check trust and generate reports:

```bash
arbiter trust show <node_id>
arbiter report --run <run_id>
arbiter blast-radius <node_id> <version>
```

```bash
deactivate
```

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

**Activate:**

```bash
# bash / zsh
source ../exemplar.tools/baton/.venv/bin/activate

# fish
source ../exemplar.tools/baton/.venv/bin/activate.fish
```

**Initialize from Constrain artifacts:**

```bash
baton init my-circuit --name my-app --constrain-dir .
```

**Edit `my-circuit/baton.yaml`** — the generated file has `port: null` and `proxy_mode: null` for every node. **You must replace both before running:**

```yaml
# Before (generated):
- name: my_component
  port: null
  proxy_mode: null

# After (required):
- name: my_component
  port: 8001
  proxy_mode: http
```

Assign sequential ports starting from 8001. Use `http` for `proxy_mode` unless your component uses a different protocol (`tcp`, `grpc`, `protobuf`, `soap`).

**Boot the circuit:**

```bash
cd my-circuit
baton status     # verify circuit loaded correctly
baton up         # boot the circuit
baton watch      # start custodian monitor
```

**Hot-swap a component without downtime:**

```bash
baton swap my-circuit <node-id> --image <new-image>
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

**Initialize and register components from your Pact project:**

```bash
# Run from your working directory (creates sentinel.yaml + .sentinel/)
sentinel init
sentinel register my-build   # imports PACT keys from pact project
sentinel report               # recent incidents and fix history
sentinel serve                # start HTTP API (watches logs + webhooks)
```

```bash
deactivate
```

---

### 5b — Chronicler

> **Coming soon.** Chronicler correlates events from Baton (OTLP spans) and Sentinel (incidents) into stories at three granularities — request, service, and journey — then emits them to Stigmergy and Apprentice.

---

### 5c — Stigmergy

> **Coming soon.** Stigmergy ingests signals from GitHub, Linear, and Slack, routes them through a self-organizing agent mesh, and surfaces structural patterns: coordination gaps, knowledge silos, and dependency risks.

---

## Step 6 — Learn: Apprentice

> **Coming soon.** Apprentice progressively distills frontier API calls into a local fine-tuned model. It routes requests between the API and the local model, shifting traffic as correlation proves quality, reducing cost over time.

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
rm -rf my-build/.pact
pact run my-build
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
