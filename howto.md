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

Chronicler sits between your running services and the pattern-learning layer. It collects events (OTLP spans, webhooks, Sentinel incidents, log files), groups them into **stories** at three granularities, and forwards completed stories to Stigmergy and Apprentice.

| Story type | Grouped by | Timeout | Meaning |
|---|---|---|---|
| Request | `trace_id` | 30 s | One request and its downstream spans |
| Service | `entity_id` + `component_id` | 5 m | Sequence of requests to one component |
| Journey | `session_id` | 30 m | Full causal chain across components |

> **Integration status:** Chronicler's configuration schema and correlation engine are fully implemented. The CLI start/status/stories/replay commands parse correctly but the runtime handlers are not yet wired up — all commands currently return immediately without side effects. Use Chronicler today to validate your config and understand the story model; the live event collection path ships in the next release.

**Activate:**

```bash
source ../exemplar.tools/chronicler/.venv/bin/activate
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
chronicler start --help
chronicler stories --help
chronicler replay --help
```

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
source ../exemplar.tools/stigmergy/.venv/bin/activate
```

**Initialize (interactive setup):**

```bash
stigmergy init
```

The wizard auto-discovers git repos and config files in the workspace. Accept defaults to get started quickly. It writes `.stigmergy/config.yaml`.

For a non-interactive setup, answer the prompts as follows (press Enter to accept defaults):

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

**Run one batch (mock data, no API key):**

```bash
stigmergy run --once
```

Expected output includes:
- Signals fetched from mock GitHub
- Mesh topology showing signal workers
- Key Findings — parallel activity, coordination gaps
- Portfolio Risk Clusters
- Run archived to `.stigmergy/runs/`

**Check connectivity (live mode, before using real sources):**

```bash
# Requires: gh auth login
stigmergy check --github

# Requires: LINEAR_API_KEY env var
stigmergy check --linear

# Requires: SLACK_BOT_TOKEN env var
stigmergy check --slack
```

**Run with real GitHub data:**

```bash
# Requires: gh auth login
stigmergy run --once --live
```

**View status from last run:**

```bash
stigmergy status
```

**Adjust config after init:**

```bash
stigmergy config show
stigmergy config set llm.provider anthropic
stigmergy config set budget.daily_cap_usd 10.00
```

**Provide feedback on a finding (calibrates the attention model):**

```bash
# The finding hash is shown in the Key Findings output
stigmergy feedback --finding <hash> --response already_knew
stigmergy feedback --finding <hash> --response had_no_idea
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
| Slack | `mock` or `live` | `SLACK_BOT_TOKEN` for live |
| Grafana | `mock` or `live` | `GRAFANA_API_KEY` for live |

#### LLM providers

| Provider | Cost | Quality |
|---|---|---|
| `stub` (default) | Free | Deterministic heuristics |
| `anthropic` | ~$0.01/run | LLM-enhanced assessments (Haiku) |

To use Anthropic:
```bash
export ANTHROPIC_API_KEY=your-key
stigmergy config set llm.provider anthropic
```

---

## Step 6 — Learn: Apprentice

Apprentice routes every request to the frontier API (Claude, GPT, etc.), collects the responses as training examples, fine-tunes a local model, then progressively shifts traffic to it — while continuously verifying quality. The goal: replace expensive API calls with a $0 local model that produces equivalent results for your specific tasks.

**Three phases, all automatic:**

| Phase | What happens |
|---|---|
| Cold Start | Every request → remote API. Responses stored as training data. |
| Reinforcement | Both models run. Evaluator scores local vs. remote. Rolling window tracks correlation. |
| Steady State | Local model handles most traffic. Sampler periodically checks quality. Auto-regresses if it drops. |

**Activate:**

```bash
source ../exemplar.tools/apprentice/.venv/bin/activate
```

**Initialize — create `apprentice.yaml`:**

```bash
apprentice init
```

The wizard walks through 4 steps: task definition, remote provider (Claude/GPT), local model (Ollama endpoint), and budget caps. It writes `apprentice.yaml` and creates `.apprentice/` directories.

For a minimal calculator task, the generated config looks like:

```yaml
provider:
  api_base_url: https://api.anthropic.com
  api_key: "env:ANTHROPIC_API_KEY"
  model: "claude-haiku-4-5-20251001"
  timeout_seconds: 30

local_model:
  endpoint: "http://localhost:11434"
  model_name: "llama3.1:8b"
  timeout_seconds: 60

tasks:
  - task_name: calculator_eval
    prompt_template: |
      Given an arithmetic expression, return the numeric result.
      Input: {expression}
    input_schema:
      - name: expression
        type: string
        required: true
    output_schema:
      - name: result
        type: string
        required: true
    evaluators:
      - type: exact_match
        match_fields:
          - name: result
            weight: 1.0
            case_sensitive: true
    thresholds:
      local_ready: 0.7
      local_only: 0.85
      degraded_threshold: 0.3
    sampling_rate_initial: 1.0
    min_training_examples: 100

budget:
  max_daily_cost_usd: 10.00
  max_monthly_cost_usd: 150.00
  budget_state_path: .apprentice/budget_state.json

finetuning:
  backend: local_lora
  model_base: "llama3.1:8b"
  output_dir: .apprentice/models/

audit:
  log_path: .apprentice/audit.log
  log_level: INFO

training_data:
  storage_dir: .apprentice/training_data/
  max_examples_per_task: 50000
```

**Start the HTTP daemon (required for `run`):**

```bash
apprentice serve --config apprentice.yaml
```

Apprentice exposes an HTTP API. `run` sends requests through it.

**Execute a task (in another terminal):**

```bash
apprentice run calculator_eval --input '{"expression": "2 + 2"}'
```

Returns the result plus metadata: which model answered (`remote`, `local`, or `dual`), cost, and current phase.

**Check current phase and training progress:**

```bash
apprentice status
apprentice status --task calculator_eval
```

**Generate a full report:**

```bash
apprentice report
```

Shows per-task correlation scores, phase history, cost breakdown, and training data counts.

**Bulk-load existing training examples:**

```bash
apprentice ingest --task calculator_eval examples.jsonl
```

Useful for bootstrapping with historical data to skip Cold Start faster.

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

#### Prerequisites for local fine-tuning

- **Ollama** running locally with the base model pulled (`ollama pull llama3.1:8b`)
- Fine-tuning only triggers after `min_training_examples` are collected
- For GKE-based LoRA training, install the `gke` extra and configure Kubernetes credentials

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
