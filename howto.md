# How to use exemplar.tools

Assumes you have already run the installer:

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```

All repositories are cloned into `./exemplar.tools/` with their `.venv` already set up.

---

## Constrain

Interviews you about your problem and produces structured artifacts for the rest of the stack.

### Setup

```bash
export ANTHROPIC_API_KEY=sk-...
```

### Activate

```bash
# bash / zsh
source ./exemplar.tools/constrain/.venv/bin/activate

# fish
source ./exemplar.tools/constrain/.venv/bin/activate.fish
```

### Run

```bash
constrain              # Start a new session (or resume incomplete)
```

### Deactivate

```bash
deactivate
```

### One-off (without activating)

```bash
../exemplar.tools/constrain/.venv/bin/constrain
```

---

## Switching between tools

Each tool has its own `.venv`. Deactivate the current one before activating another:

```bash
deactivate
source ./exemplar.tools/pact/.venv/bin/activate
```

Or run directly without activating:

```bash
./exemplar.tools/pact/.venv/bin/pact
./exemplar.tools/kindex/.venv/bin/kindex
```

---

## Updating all repositories

Re-run the installer at any time to pull the latest changes and update dependencies:

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```
