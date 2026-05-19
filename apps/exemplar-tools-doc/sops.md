# Operating Procedures

## Tech Stack
CRITICAL: implementation language is TypeScript. Never generate Python. All source files must be .ts or .tsx.
- Language: TypeScript (strict mode)
- Testing: vitest
- Framework: React 18
- Build tool: Vite (dev server on port 4000)
- Styling: Tailwind CSS
- Package manager: npm

## Standards
- Type annotations on all public functions
- Named exports only — no default exports
- Use `export type { }` for interfaces and type aliases
- Prefer composition over inheritance
- When importing from a sibling module, use the exact exported names — never guess

## vi.mock() Rules
- vi.mock() factory objects MUST provide every named runtime export of the mocked module
- Match export names exactly — STEPS not STEP_CONTENT_LIST, ROUTE_SLUG_MAP not ROUTE_SLUGS

## Slug Handling
- ROUTE_SLUG_MAP values already include a leading slash (e.g. "/step-0-cartographer")
- Never prepend an extra "/" to a slug that already starts with "/"
- Always guard: slug.startsWith('/') ? slug : '/' + slug

## Verification
- All functions must have at least one test
- Tests must be runnable without external services
- No task is done until its contract tests pass
