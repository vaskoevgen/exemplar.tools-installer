# Upstream Bugs

Known packaging bugs in upstream exemplar.tools repositories and the local fixes applied to this installer's clones.

These fixes are applied manually to the local clone after install. They will be lost if the repo is re-cloned from scratch. Re-apply them after a fresh install.

---

## ledger — wrong CLI entry point

**Repo:** `https://github.com/jmcentire/ledger`
**File:** `pyproject.toml`
**Status:** PR open — https://github.com/jmcentire/ledger/pull/1

### Problem

The `ledger` binary is declared as:

```toml
[project.scripts]
ledger = "cli.main:main"
```

But the actual module is `src/cli/cli.py` with a function named `cli_main`. There is no `cli/main.py` and no function called `main`. The installed binary crashes on import.

### Fix applied locally

```toml
[project.scripts]
ledger = "cli.cli:cli_main"
```

**File:** `exemplar.tools/ledger/pyproject.toml` line 44

After editing, reinstall:

```bash
source exemplar.tools/ledger/.venv/bin/activate
pip install -e "exemplar.tools/ledger/.[api,mock,dev]" -q
deactivate
```

---

## ledger — `ledger backend add` crashes with wrong argument count

**Repo:** `https://github.com/jmcentire/ledger`
**File:** `src/cli/cli.py`
**Status:** Fixed locally (2026-05-04)

### Problem

Running `ledger backend add <name>` raised:

```
TypeError: BackendConfig.__init__() takes 3 positional arguments but 4 were given
```

The CLI passed 4 raw string arguments to `register_backend()`, which expects `(root: Path, metadata: BackendMetadata, actor: str)`.

A second related bug: `ledger init` only called `config.init_config()` but never called `registry.init()`, so the `.ledger/` directory was never created — causing `register_backend` to raise `LedgerNotInitializedError` even after the first bug was fixed.

A third related bug: `registry.DuplicateBackendError` (from `registry.py`) was not caught by the CLI's `except LedgerError` clause (a different class in `cli.py`), causing an unhandled traceback on repeat runs.

### Fix applied locally

Three changes in `exemplar.tools/ledger/src/cli/cli.py`:

**1. Added `datetime` import:**
```python
from datetime import datetime, timezone
```

**2. `cmd_init` now also initializes the registry:**
```python
config.init_config(cli_ctx.config_path)
registry.init(Path(cli_ctx.config_path).parent)   # ← added
```

**3. `cmd_backend_add` constructs `BackendMetadata` correctly and handles duplicates:**
```python
metadata = registry.BackendMetadata(
    backend_id=backend_id,
    backend_type=registry.BackendType(backend_type),
    owner_component=owner,
    registered_at=datetime.now(timezone.utc),
)
root = Path(cli_ctx.config_path).parent
registry.register_backend(root, metadata, owner)
```
Plus a new `except registry.DuplicateBackendError` clause that exits silently (idempotent).

After editing, reinstall:

```bash
pip install -e "exemplar.tools/ledger/.[api,mock,dev]" -q
```

### Usage (after fix)

```bash
ledger backend add tasks-db --type postgres --owner fastapi-backend
# Silent on success. Silent on duplicate (idempotent).
```

Valid `--type` values: `postgres`, `mysql`, `sqlite`, `redis`, `s3`, `dynamodb`, `kafka`, `custom`.

---

## pact — health check fires before any code generation (planning ratio = 0.00x)

**Repo:** `https://github.com/jmcentire/pact`
**File:** `src/pact/health.py`
**Status:** PR open — https://github.com/jmcentire/pact/pull/2

### Problem

The `output_planning_ratio` check fires at the start of every phase, including `preflight` and `implement`, before any code has been generated. At that point `generation_tokens = 0`, so the ratio is literally `0 / N = 0.00x`, which is always below the CRITICAL threshold (0.25). This causes the daemon to pause before it even begins writing code, requiring manual `pact resume .` to proceed.

Additionally, post-build phases (integrate, arbiter, polish, retrospective, complete) produce no new code, so the cumulative ratio never improves after implementation ends — causing 5–6 more spurious pauses after the build is done.

Root cause: `_check_output_planning_ratio()` only guards against `total_tokens < 1000`, but doesn't guard against `generation_tokens == 0`.

### Fix applied locally

Two changes in `exemplar.tools/pact/src/pact/health.py`:

**1. Skip ratio check when no generation tokens exist yet** (line ~390):

```python
# Before
if metrics.total_tokens < 1000:

# After
if metrics.total_tokens < 1000 or metrics.generation_tokens == 0:
```

**2. Extend `_PRE_ARTIFACT_PHASES` to cover post-build phases** (line 326):

```python
# Before
_PRE_ARTIFACT_PHASES = {"interview", "shape"}

# After
_PRE_ARTIFACT_PHASES = {"interview", "shape", "integrate", "arbiter", "polish", "retrospective", "complete"}
```

Both fixes are required: fix 1 eliminates the pre-implementation pause; fix 2 eliminates post-build pauses.

**PR open:** https://github.com/jmcentire/pact/pull/2

### Workaround (before fix is merged)

```bash
# After each pause, restart daemon if needed and resume:
pact daemon . &
pact resume .
# Repeat until status reaches complete (~6-7 times total without the fix)
```

---

## advocate — missing jinja2 dependency

**Repo:** `https://github.com/jmcentire/advocate`
**File:** `pyproject.toml`
**Status:** PR open — https://github.com/jmcentire/advocate/pull/1

### Problem

The HTML report feature (`--html`) imports `jinja2` at runtime, but `jinja2` is not declared in `dependencies` or any extras including `all`. Running `advocate review` with `--html` raises:

```
ModuleNotFoundError: No module named 'jinja2'
```

### Fix applied locally

Add `jinja2>=3.0` to the core `dependencies`:

```toml
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "click>=8.0",
    "jinja2>=3.0",
]
```

**File:** `exemplar.tools/advocate/pyproject.toml` line 14

After editing, reinstall:

```bash
source exemplar.tools/advocate/.venv/bin/activate
pip install -e "exemplar.tools/advocate/.[all]" -q
deactivate
```

---

## apprentice — `run` and `report` crash with missing attributes on response objects

**Repo:** `https://github.com/jmcentire/apprentice`
**Status:** No PR yet.

### Problem

Two CLI commands crash immediately:

**`apprentice run <task> --input ...`** raises:
```
Error: 'TaskResponse' object has no attribute 'success'
```

**`apprentice report`** raises:
```
Error: 'SystemReport' object has no attribute 'tasks'
```

The task never executes ($0.00 spent, stuck in `bootstrapping` phase). The CLI display layer references attributes that don't exist on the response dataclasses.

### Workaround

None available. `apprentice status` works and shows phase/confidence, but no tasks can be run or reported via the CLI. The HTTP API endpoints (`POST /v1/run`, `GET /v1/report`) may work directly via `curl` — not tested.
