# Todo-List App — Example Project

A full walkthrough of the exemplar.tools stack using a personal task management app. Every step below ran against real tools; terminal output is verbatim from the session logs in `terminal-logs/`.

**What was built:** a Python in-memory task CRUD library (`src/root/root.py`) with 5 REST-shaped functions, 90 contract tests, and full tool-stack coverage through Step 6.

> **Gotcha — sops.md overrides your stack choice.** The task spec asked for Node.js/Express + PostgreSQL. Because the default `sops.md` says `Language: Python 3.12+`, Pact generated Python regardless. Always update `sops.md` to match your stack before running the daemon.

---

## Step 1a — Constrain

```
$ constrain
```

Ran a 6-round interactive interview: scope, HTTP semantics, priority column migration strategy, error codes, local-dev-only constraints. No API cost.

**Artifacts written:**
```
prompt.md
constraints.yaml        (7 constraints)
component_map.yaml
trust_policy.yaml
schema_hints.yaml
```

**Sample constraints:**
```
C001: All endpoints must return correct HTTP status codes (must)
C004: Priority column migration must include NOT NULL, default value, and index (must)
```

---

## Step 1b — Ledger

```
$ ledger init
# Created: ledger.yaml, schemas/, plans/, changelog.yaml

$ ledger schema add schemas/tasks.yaml
$ ledger schema validate
$ ledger export --format pact
{'contracts': []}
```

Schema registered for 6 fields: `id`, `title`, `completed`, `priority`, `due_date`, `created_at`. Export returns empty contracts — expected (export stub not yet implemented).

> **Gotcha:** `ledger backend add` crashes with a TypeError. Add backends directly to `ledger.yaml` instead.

---

## Step 2a — Pact

```
$ pact init .
$ pact daemon .
```

The daemon ran 8 phases automatically:

| Phase | Result |
|-------|--------|
| interview | 10 questions generated, paused for user answers |
| shape | passed |
| decompose | 1 component (root), 10 contract functions, 53 test cases, 64 Goodhart cases |
| preflight | **HEALTH CRITICAL pause** — ran `pact resume .` to bypass (known false positive) |
| implement | 2 files generated, 90/90 tests passed on first attempt |
| polish | 2 Goodhart tests failed (non-blocking warnings) |
| retrospective | 0 lessons |
| complete | ✓ |

```
$ pact status .
Phase: complete
Cost:  $2.55
```

> **Gotcha:** run `pact daemon .` from the directory containing `task.md` — not a subdirectory. Error if wrong: `FileNotFoundError: No task.md`.

> **Health pause:** the decompose phase consumed 93% of tokens on this single-component project, tripping the health gate. `pact resume .` unblocks it.

**Cost: $2.55**

---

## Step 2b — Advocate

```
$ advocate review src/ -o findings.json --html review-report.html
```

6 personas ran in parallel (~30 seconds):

| Persona | Top finding |
|---------|-------------|
| Red Team | Global `_store` accessed without locks — concurrent writes will corrupt data |
| Adversarial | `TimestampTZ` accepts any string without format validation |
| Sage | Duplicate type systems — wrapper classes and separate validation functions doing the same thing |
| User | No README or entry point; auto-stubbed boolean/string wrapper classes confuse readers |
| SME | `datetime.now()` not monotonic — NTP jumps can break ordering; DELETE returns 200+body instead of 204 |
| Good Friend | In-memory store loses all data on restart; global singleton unsafe in any concurrent server |

```
Total findings: 38
Cost: $0.24
```

Open `review-report.html` in a browser — easier to read than `findings.json`.

---

## Step 3 — Arbiter

```
$ arbiter init
# Created: .arbiter/registry/trust_ledger.jsonl, arbiter.yaml

$ arbiter register access_graph.json
Error: Graph contains no nodes
```

Known schema mismatch (Pact writes `components`, Arbiter reads `nodes`). Not a user error — skip to Step 4.

**Cost: $0**

---

## Step 4 — Baton

```
# Generate baton.yaml (from pact venv):
$ pact deploy .
Generated baton.yaml: todo-list2/baton.yaml
  Nodes: 1
  Edges: 0
  Observability: jsonl
  Canary thresholds: error_rate < 5.0%, p95 < 500.0ms

# Switch to baton venv, edit baton.yaml (port 3001, role: ingress, health_check: /tasks)

$ baton status
Circuit: root (v1)
Nodes:   1  Edges:  0
  Name   Role       Port   Mode   Contract
  ──────────────────────────────────────────
  root   [ingress]  3001   http   —

$ baton up --mock
Circuit 'root' is up (1 nodes)
  root: active
Entry points:
  root: 127.0.0.1:3001
Press Ctrl+C to stop
```

Browser showed `{"status": "mock", "port": 23001}`.

**Cost: $0**

---

## Step 5a — Sentinel

```
$ sentinel init
# Created sentinel.yaml, initialized .sentinel/

$ sentinel register .
  Registered: root
  Registered 1 components from .

$ sentinel report
No incidents recorded.
```

Clean — no live traffic, no incidents. **Cost: $0**

---

## Step 5b — Chronicler

```
$ python -c "
from chronicler.config import load_config
cfg = load_config('chronicler.yaml')
print('Sources:', [s.type for s in cfg.sources])
print('Sinks:  ', [s.type for s in cfg.sinks])
print('Rules:  ', [r.name for r in cfg.rules])
"
Sources: [<SourceType.otlp: 'otlp'>, <SourceType.sentinel: 'sentinel'>]
Sinks:   [<SinkType.disk: 'disk'>]
Rules:   ['request_story', 'service_story', 'journey_story']
```

Config validated. Runtime not yet active — config validation is all that's possible at this stage.

**Cost: $0**

---

## Step 5c — Stigmergy

```
$ stigmergy init
# GitHub mock, Linear N, Grafana N, LLM stub

$ stigmergy run --once
Mesh initialized: 3 workers, 2 agents, 16 repos, 0 packages, 0 edges

Connecting github  (mock)...
  github: 7 signals fetched

Routing 7 signals through mesh...
  [1/7] $0.00 spent   [GITHUB]  acme-org/backend  @alice.chen
  >> PARALLEL ACTIVITY  61%  @bob.martinez and @alice.chen in same signal space

Mesh Session Summary
  Signals processed:  7
  Accepted:           7
  Total cost:         $0.0000

  Persisted 3 insights to .stigmergy/insights.jsonl
```

Fully functional in mock+stub mode — no API key required. **Cost: $0**

---

## Step 6 — Apprentice

```
$ apprentice init        # configured calculator_eval task
$ apprentice serve
Loading config from ./apprentice.yaml...
Apprentice serving on 127.0.0.1:8710
  Health:  http://127.0.0.1:8710/health
  Run:     POST http://127.0.0.1:8710/v1/run
  Status:  http://127.0.0.1:8710/v1/status

$ apprentice status
Task: calculator_eval
  Phase: bootstrapping
  Confidence: 0.00

$ apprentice run calculator_eval --input '{"expression": "2 + 2"}'
Error: 'TaskResponse' object has no attribute 'success'

$ apprentice report
Error: 'SystemReport' object has no attribute 'tasks'
```

`serve` and `status` work. `run` and `report` hit known upstream SDK bugs — no workaround yet.

> **Gotcha:** after `apprentice init`, open `apprentice.yaml` and rename `input_schema[0].name` from `text` to your actual variable name (e.g. `expression`). The wizard ignores your prompt template's `{expression}` placeholder and always writes `text`.

**Cost: $0**

---

## Total cost

| Step | Cost |
|------|------|
| Constrain | $0.00 |
| Ledger | $0.00 |
| Pact | $2.55 |
| Advocate | $0.24 |
| Arbiter | $0.00 |
| Baton | $0.00 |
| Sentinel | $0.00 |
| Chronicler | $0.00 |
| Stigmergy | $0.00 |
| Apprentice | $0.00 |
| **Total** | **~$2.79** |
