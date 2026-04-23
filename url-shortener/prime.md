# URL Shortener — Project Brief

## What we're building

A URL shortener web service. Users paste a long URL into a web UI and get a short link back. Visiting the short link redirects to the original URL.

## Components

- **api** — FastAPI REST backend. Endpoints: POST /shorten, GET /{code} (redirect), GET /links (list all). Runs on port 8000.
- **frontend** — Single-page HTML + vanilla JS UI. Form to submit a URL, table showing existing short links. Served by the api as static files.
- **db** — PostgreSQL. One table: `links(id, short_code, original_url, created_at, hit_count)`.

## Constraints

- Python 3.12, FastAPI, psycopg2, no ORM
- Short codes are 6 random alphanumeric characters
- Duplicate original URLs return the existing short code
- Hit count increments on every redirect
- All tests use pytest; no mocking of the database (use a test DB)
- Single deployable unit (api serves frontend static files)
- No authentication required in v1
