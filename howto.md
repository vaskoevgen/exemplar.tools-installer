# How to use exemplar.tools

Install everything first:

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```

---

## Step 1 — Constrain

Interview your problem and produce structured artifacts for the rest of the stack.

```bash
export ANTHROPIC_API_KEY=sk-...

source ../exemplar.tools/constrain/.venv/bin/activate

or

source ../exemplar.tools/constrain/.venv/bin/activate.fish

constrain
```

Produces: `prompt.md`, `constraints.yaml`, `component_map.yaml`, `trust_policy.yaml`, `schema_hints.yaml`

```bash
deactivate
```

---

## Step 2 — Pact

Build the software using the artifacts from Constrain.


```bash

source ../exemplar.tools/pact/.venv/bin/activate

or

source ../exemplar.tools/pact/.venv/bin/activate.fish

pact init my-project

pact run my-project
```

Useful commands:

```bash
pact status my-project       # current phase
```

```bash
deactivate
```

---

## Troubleshooting

### Switching between tools

Each tool has its own `.venv`. Deactivate before switching:

```bash
deactivate
source ./exemplar.tools/kindex/.venv/bin/activate.fish
```

### Updating all repositories

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```
