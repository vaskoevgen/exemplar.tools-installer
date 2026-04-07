# How to use exemplar.tools

## Install

Run once to clone all repositories and set up dependencies:

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```

This creates an `exemplar.tools/` directory in your current working directory.

---

## Step 1 — Constrain

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
