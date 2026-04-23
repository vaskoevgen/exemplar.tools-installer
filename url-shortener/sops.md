# Operating Procedures

## Tech Stack
- Language: Python 3.12
- Framework: FastAPI + uvicorn
- Database: PostgreSQL via psycopg2-binary (raw SQL only — no ORM, no SQLAlchemy)
- Testing: pytest with real PostgreSQL test database

## Standards
- Type annotations on all public functions
- No mocks — tests connect to a real test database
- Use `secrets` module for short code generation
- All DB operations use parameterised queries (no string interpolation)
- `DATABASE_URL` and `TEST_DATABASE_URL` read from environment variables

## Verification
- Contract tests must pass before a component is considered done
- Test the DB state directly after redirect (verify hit_count incremented)
- All 4 endpoints must have at least one test

## File Placement (CRITICAL)
All .py files (main.py, shortener.py, db.py, config.py) must be placed **directly** in
the implementation root — do NOT create any subdirectory. The test runner mounts the
implementation root on PYTHONPATH, so files one level deeper will not be importable.

Wrong: `root/main.py` → ends up at `src/root/root/main.py` → invisible to tests
Right: `main.py` → ends up at `src/root/main.py` → importable as `import main`

## Import Style (CRITICAL)
All modules must use **direct module imports only** — never `from src import ...` or
`from root import ...`. The test runner sets PYTHONPATH to `src/root:src`, so sibling
modules are importable directly by name:

```python
# CORRECT
import shortener
import db
import config

# WRONG — will fail in test environment
from src import shortener, db
from src.shortener import LinkRow
from root import shortener
```

Route handlers in `main.py` MUST call shortener functions through the module reference
(not via `from shortener import` direct imports), so that test mocks work correctly:

```python
# CORRECT — mock patch("shortener.shorten_url", ...) will intercept this
import shortener
result = shortener.shorten_url(url, base)

# WRONG — mock patch("shortener.shorten_url", ...) will NOT intercept bound names
from shortener import shorten_url
result = shorten_url(url, base)
```

## shorten_url retry pattern (CRITICAL)
The `shorten_url` function must perform both a SELECT and an INSERT on each retry
iteration. The test mock uses alternating None/UniqueViolation execute side_effects
(`[None, UV] * 10`), meaning execute calls must alternate between SELECT and INSERT
within a single cursor context:

```python
# CORRECT — SELECT then INSERT inside each retry
for attempt in range(5):
    code = generate_code()
    with conn.cursor() as cur:
        cur.execute("SELECT short_code FROM links WHERE original_url = %s", (url,))
        existing = cur.fetchone()
        if existing:
            return existing_result
        try:
            cur.execute("INSERT INTO links ...")
            conn.commit()
            return new_result
        except UniqueViolation:
            conn.rollback()
raise RuntimeError("Could not generate unique code after 5 attempts")

# WRONG — single SELECT outside loop, INSERT-only retries
with conn.cursor() as cur:
    cur.execute("SELECT ...")  # one-time check
...
for attempt in range(5):
    cur.execute("INSERT ...")  # INSERT-only, mock returns None on 3rd call
```

## Preferences
- Keep each file under 200 lines
- No third-party libraries beyond FastAPI, uvicorn, psycopg2-binary, pytest, httpx
