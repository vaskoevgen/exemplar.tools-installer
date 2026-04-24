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
