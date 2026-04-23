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

## pact — health check loops in post-build phases

**Repo:** `https://github.com/jmcentire/pact`
**File:** `src/pact/health.py` (health check logic)
**Status:** Not fixed upstream

### Problem

After all code is generated, Pact's health check fires in every post-build cleanup phase (arbiter → polish → retrospective → complete). The check calculates the planning/generation token ratio across the entire session lifetime. Since decomposition tokens (≈75k) accumulated before any code was written, the ratio never recovers — causing the daemon to pause 5–6 times on phases that produce zero code by design.

This requires restarting `pact daemon .` and running `pact resume .` repeatedly after the build is already done.

### Fix applied locally

In `exemplar.tools/pact/src/pact/health.py` line 326:

```python
# Before
_PRE_ARTIFACT_PHASES = {"interview", "shape"}

# After
_PRE_ARTIFACT_PHASES = {"interview", "shape", "integrate", "arbiter", "polish", "retrospective", "complete"}
```

**PR open:** https://github.com/jmcentire/pact/pull/2

### Workaround (before fix is merged)

```bash
# After each pause, restart daemon if needed and resume:
pact daemon . &
pact resume .
# Repeat ~5-6 times total until status reaches complete
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
