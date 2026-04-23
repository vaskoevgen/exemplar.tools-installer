# Design: url-shortener

*Version 1 — Auto-maintained by pact*

## Decomposition

- [C] **Main** (`root`)
  # Task

Build a URL shortener web service — a single deployable Python app where users paste a long URL and get a short redirect link back.

## Endpoints

- `POST /shorten` — body `{"url": "..."}`, returns `{"short_url": "http://localhost:8000/abc123", "code": "abc123"}`. If the URL already exists return the existing code.
- `GET /{code}` — HTTP 307 redirect to original URL, increments hit_count atomically. Returns 404 if code not found.
- `GET /links` — returns JSON array of all links: `[{"code", "original_url", "created_at", "hit_count"}]`
- `GET /` — serves `static/index.html`

## Database

PostgreSQL, raw SQL via psycopg2-binary (no ORM).

```sql
CREATE TABLE links (
  id           SERIAL PRIMARY KEY,
  short_code   VARCHAR(6)  NOT NULL UNIQUE,
  original_url TEXT        NOT NULL UNIQUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  hit_count    INTEGER     NOT NULL DEFAULT 0
);
```

Migration file: `migrations/001_init.sql`

## Short code generation

Use `secrets.token_urlsafe(4)[:6]` — retry on collision (max 5 attempts).

## Frontend

`static/index.html` — vanilla HTML + JS, no build step:
- Form: text input for URL + Submit button
- On submit: POST /shorten, display the resulting short_url
- Table below showing all links from GET /links (auto-refresh after shorten)

## File structure

```
src/api/
  main.py        # FastAPI app, mounts static/, all routes
  db.py          # get_conn(), execute helpers using DATABASE_URL env var
  shortener.py   # generate_code(), shorten_url(), get_link(), list_links()
  config.py      # reads DATABASE_URL from env
src/static/
  index.html
migrations/
  001_init.sql
tests/
  conftest.py    # creates test DB schema, yields TestClient, teardown
  test_api.py    # tests for all 4 endpoints
```

## Runtime

- `uvicorn src.api.main:app --port 8000`
- Env var: `DATABASE_URL=postgresql://user:pass@localhost:5432/urlshortener`

