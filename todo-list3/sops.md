# Operating Procedures

## Tech Stack
- Backend language: Python 3.12+
- Backend framework: FastAPI
- Backend database driver: psycopg2
- Backend testing: pytest
- Frontend language: TypeScript
- Frontend framework: React + Vite

## Standards
- Type annotations on all public functions (Python backend)
- Prefer composition over inheritance

## Verification
- All backend functions must have at least one test
- Contract tests may connect to PostgreSQL via DATABASE_URL environment variable
- No task is done until its contract tests pass

## Preferences
- Keep files under 300 lines
