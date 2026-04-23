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
