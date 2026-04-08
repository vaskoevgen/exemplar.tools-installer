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

## Step 2 — Pact

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

## Step 3 — Deploy & Observe

After Pact builds the code, use Baton to deploy it and the observe layer to monitor it.

### 3a — Baton (Deploy)

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

**Edit `my-circuit/baton.yaml`** — the generated file has `port: null` for every node. **You must replace each `null` with a real port number before running:**

```yaml
# Before (generated):
- name: my_component
  port: null

# After (required):
- name: my_component
  port: 8001
```

Assign sequential ports starting from 8001.

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

### 3b — Sentinel (Observe)

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

### 3c — Kindex (Knowledge)

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

## The Closed Loop

```
Constrain → Pact → Baton → Sentinel → (tighten contracts) → Constrain
                              ↑
                           Kindex (cross-cutting knowledge layer)
```

Production incidents detected by Sentinel feed back to tighten Pact contracts — making the entire class of bug non-recurring.

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
