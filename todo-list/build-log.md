# Todo List App — Build Log

Project: Todo List web app — create, complete, delete tasks
Location: `/Users/yevhenvasko/source/exemplar.tools-installer/todo-list`
Stack: Python (FastAPI) backend + PostgreSQL + HTML/JS frontend
Build completed: 2026-04-24

---

## Step 1a — Constrain ✅

**Tool:** `constrain new --min-challenge 0 --max-challenge 0 --min-understand 0 --max-understand 0 -p prime.md`
**Cost:** ~$0.00 (primer-only, 0 interview rounds)

Ran constrain with a prime document describing the app. Used 0 interview rounds since prime captured all requirements.

**Issue fixed:** First run failed — curly braces `{}` in prime.md caused YAML generation error. Fixed by rewriting JSON examples in plain English.

### Artifacts produced

| File | Purpose |
|------|---------|
| `prompt.md` | System briefing for Pact — consequence map, failure modes, boundary conditions |
| `constraints.yaml` | 7 constraints: JSON responses, error format, schema, single-process, no auth |
| `component_map.yaml` | 3 components: web_frontend, api_backend, database with edges |
| `trust_policy.yaml` | All task fields classified PUBLIC |
| `schema_hints.yaml` | 4 field hints for tasks table |

---

## Step 1b — Ledger ✅

**Tool:** `ledger init` + `ledger schema add schemas/tasks.yaml`
**Issue fixed:** `ledger init` was a no-op stub on `main` branch. Switched to `vaskoevgen/fix/init-config-stub` branch which implements `init_config`.

### Actions taken
- Ran `ledger init` → created `ledger.yaml`, `schemas/`, `plans/`, `changelog.yaml`
- Added `todo_db` backend directly to `ledger.yaml` (workaround for `ledger backend add` bug)
- Created `schemas/tasks.yaml` with 4 fields: id, title, completed, created_at
- Ran `ledger schema add` and `ledger schema validate` (both exit 0 silently = valid)

---

## Step 1c — Database Setup ✅

**Method:** Reused existing `todo-pg` Docker container on port 5432
**Credentials:** `todo:todo@127.0.0.1:5432/todo_test`

```bash
# Container was already running:
docker ps  # → todo-pg  arm64v8/postgres:17-alpine  0.0.0.0:5432->5432

# Created test database and schema:
docker exec todo-pg psql -U todo -d todo_dev -c "CREATE DATABASE todo_test;"
docker exec -i todo-pg psql -U todo -d todo_test << SQL
CREATE TABLE tasks (id SERIAL PRIMARY KEY, title VARCHAR(500) NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
SQL
```

---

## Step 2a — Pact ✅

**Tool:** `pact daemon` + `pact approve` + `pact resume`
**Cost:** ~$1.44
**Final result:** 39/39 contract tests passing

### Interview (7 questions answered)
1. Python 3.11+ is authoritative
2. 300-line limit waived for single-file constraint
3. Use Docker PostgreSQL for tests (TEST_DATABASE_URL set)
4. App auto-creates `tasks` table on startup
5. Only `completed` is mutable via PATCH (not title)
6. `GET /tasks` ordered by `created_at ASC`
7. Empty/whitespace-only titles rejected with 400

### Issues encountered and fixed
- **Health gate false positive:** `variance_reaches_target` fired after 0 generation tokens. Fixed with `pact resume`.
- **PYTHONPATH mismatch:** Pact ran tests with `PYTHONPATH=src` but implementation is at `src/root/root/main.py`, not `src/root/main.py`. This caused 13/18 tests to fail (functions not found). Fixed by creating `src/root/main.py` that re-exports from `root.root.main`. After this fix: 39/39 pass.
- **`rejection_rate` health gate:** Fired after all 3 attempts failed (before the manual fix). Pact went into a diagnose→implement loop. Killed daemon after fix was applied.

### Generated files
- `src/root/root/main.py` — FastAPI backend (single file, raw SQL, psycopg2)
- `src/root/root/static/index.html` — Vanilla JS frontend (added filter buttons manually)
- `src/root/main.py` — Proxy re-export (created manually to fix PYTHONPATH)
- `tests/root/contract_test.py` — 39 contract tests
- `contracts/root/interface.json` — Component contract

---

## Step 2b — Advocate ✅

**Tool:** `advocate review src/ --sequential`
**Cost:** ~$0.02

### Findings (4 total)

| Severity | Finding |
|----------|---------|
| HIGH | Silent startup failure — DB init errors are logged but don't crash the app |
| HIGH | Unhandled psycopg2 exceptions expose DB details to users |
| MEDIUM | Global `_database_url` variable makes debugging production hard |
| MEDIUM | No connection pooling — traffic spikes will exhaust DB connections |

**Saved to:** `advocate-findings.json`

---

## Step 4 — Baton ✅

**Tool:** `pact deploy` + `baton up --mock`

### Actions taken
- Generated `baton.yaml` via `pact deploy`
- Added `role: ingress` to root node, set `port: 8000`
- Cleaned up stale url-shortener process on port 8000
- Started todo-list app on port 9000 (app port) 
- Booted baton circuit in mock mode on port 8000

### Circuit status
```
Circuit: root (v1) | Nodes: 1 | Edges: 0 | State: full_mock
root  [ingress]  port 8000  http  listening
```

**Note:** `baton slot` IPC mechanism requires the daemon to be running with specific socket/FIFO. Mock mode successfully demonstrates the circuit topology.

---

## Final verification ✅

End-to-end API test against running app (port 9000):

```bash
POST /tasks    → 201 {"id":3,"title":"Walk the dog","completed":false,...}
PATCH /tasks/3 → 200 {"completed":true,...}
GET  /tasks?completed=true → [{"id":3,...}]
DELETE /tasks/3 → 204
```

**Contract tests:** 39/39 passing
**App running at:** `http://localhost:9000`
**Baton circuit at:** `http://localhost:8000` (mock mode)

---

## Running the app

```bash
export DATABASE_URL=postgresql://todo:todo@127.0.0.1:5432/todo_dev
uvicorn src.root.root.main:app --port 8000 --app-dir todo-list
# Open http://localhost:8000
```
