# How to use exemplar.tools

## Install

Run once to clone all repositories and set up dependencies:

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```

This creates an `exemplar.tools/` directory in your current working directory.

---

## Step 1 — Specify

### 1a — Constrain (Boundaries & components)

Interview your problem and produce structured artifacts consumed by the rest of the stack.

**Activate:**

```bash
# bash / zsh
source ./exemplar.tools/constrain/.venv/bin/activate

# fish
source ./exemplar.tools/constrain/.venv/bin/activate.fish
```

**Set your API key:**

```bash
export ANTHROPIC_API_KEY=sk-...
```

**Run from your project directory:**

```bash
cd my-project
constrain
```

**Output artifacts** (written to current directory):

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

### 1b — Ledger (Schema obligations)

Ledger registers your storage schemas and data rules, then exports obligations into Pact contracts, Arbiter, Baton, and Sentinel.

**Activate:**

```bash
# bash / zsh
source ./exemplar.tools/ledger/.venv/bin/activate

# fish
source ./exemplar.tools/ledger/.venv/bin/activate.fish
```

> **Note:** The `ledger` binary has a packaging bug. Run from the repo root using python directly:

```bash
cd ./exemplar.tools/ledger
```

Define a helper for the session:

```bash
# bash / zsh
function ledger() { PYTHONPATH=src .venv/bin/python -c "import sys; sys.path.insert(0,'src'); from cli.cli import cli_main; cli_main()" -- "$@"; }

# fish
function ledger; PYTHONPATH=src .venv/bin/python -c "import sys; sys.path.insert(0,'src'); from cli.cli import cli_main; cli_main()" -- $argv; end
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

Build the software using the artifacts produced by Constrain.

**Activate:**

```bash
# bash / zsh
source ./exemplar.tools/pact/.venv/bin/activate

# fish
source ./exemplar.tools/pact/.venv/bin/activate.fish
```

**Initialize and run:**

```bash
pact init my-project
# Edit my-project/task.md  — what to build
# Edit my-project/sops.md  — coding standards

pact run my-project
```

**Useful commands:**

```bash
pact status my-project        # current phase and state
pact components my-project    # list components and status
pact build my-project <id>    # rebuild a specific component
pact health my-project        # check for coordination issues
```

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
source ./exemplar.tools/baton/.venv/bin/activate

# fish
source ./exemplar.tools/baton/.venv/bin/activate.fish
```

**Initialize and deploy:**

```bash
baton init my-circuit
# Edit my-circuit/circuit.yaml — nodes and edges from component_map.yaml

baton up my-circuit       # boot the circuit
baton status my-circuit   # check node health
baton watch my-circuit    # start custodian monitor
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
source ./exemplar.tools/sentinel/.venv/bin/activate

# fish
source ./exemplar.tools/sentinel/.venv/bin/activate.fish
```

**Initialize and register components from your Pact project:**

```bash
sentinel init my-project
sentinel register my-project   # imports PACT keys from pact project
sentinel serve                  # start HTTP API (watches logs + webhooks)
sentinel report                 # recent incidents and fix history
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
source ./exemplar.tools/kindex/.venv/bin/activate

# fish
source ./exemplar.tools/kindex/.venv/bin/activate.fish
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
rm -rf my-project/.pact
pact run my-project
```

### Switching between tools

Each tool has its own `.venv`. Deactivate before activating another:

```bash
deactivate
source ./exemplar.tools/kindex/.venv/bin/activate.fish
```

### Updating all repositories

Re-run the installer at any time to pull latest changes:

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```
