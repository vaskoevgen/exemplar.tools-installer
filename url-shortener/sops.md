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

## Preferences
- Keep each file under 200 lines
- No third-party libraries beyond FastAPI, uvicorn, psycopg2-binary, pytest, httpx
