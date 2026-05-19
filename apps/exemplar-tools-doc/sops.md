CRITICAL: implementation language is typescript. Never generate Python. All output files must be .ts/.tsx (or equivalent for typescript).

# Operating Procedures

## Tech Stack
- Language: typescript
- Testing: vitest

## Standards
- Type annotations on all public functions
- Prefer composition over inheritance

## Verification
- All functions must have at least one test
- Tests must be runnable without external services
- No task is done until its contract tests pass

## Preferences
- Prefer stdlib over third-party libraries
- Keep files under 300 lines

## TypeScript / React Rules — CRITICAL
- Named exports: every type, interface, function, and constant MUST be a named export
- React components: export BOTH as named AND default (e.g. `export function Foo() {}` + `export default Foo`)
- Every .tsx file must include `import React from 'react'` at the top
- Tests run with vitest + @testing-library/react in jsdom environment
- Do NOT use `export default` as the only export — always pair with a named export

## String Keys in Maps and Registries — CRITICAL
When implementing any component that builds a map keyed by string values (slug maps, route registries, component lookups):
- NEVER infer key strings from component names or natural language — they may differ from the contract value
- ALWAYS read the key strings from: (1) the TypeScript interface definition for the map, (2) the contract test's test data, or (3) the dependency component's exported manifest/enum
- A key that "looks right" by name may not match the contract — always verify against the source of truth

## import.meta.env in Vite/Vitest — CRITICAL
- ALWAYS use `import.meta.env.VITE_X` directly — never `(import.meta as any).env?.VITE_X`
- The `as any` cast bypasses vitest's vi.stubEnv: stubs return undefined instead of the stubbed value
- Correct: `const url = import.meta.env.VITE_CONVEX_URL;`
- Wrong: `const url = (import.meta as any).env?.VITE_CONVEX_URL;`
