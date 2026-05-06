# Operating Procedures

## Tech Stack
- Language: TypeScript with React 18
- Framework: Vite + React, initialized with bun create vite
- Package manager: Bun only — never use npm or yarn or npx
- Styling: Tailwind CSS v3
- Routing: React Router v6
- Database: Convex (real-time backend)
- Testing: vitest

## Standards
- Type annotations on all exported functions and components
- React functional components only, no class components
- Props typed with TypeScript interfaces
- All Tailwind classes, no custom CSS unless absolutely necessary

## Verification
- Components must render without errors
- Convex queries and mutations must be correctly typed
- All pages must be reachable via React Router routes
- Tests must run with vitest

## Preferences
- Keep files under 300 lines
- Split large components into smaller ones
- Use React hooks for state management (useState, useEffect)
- Import Convex hooks from convex/react

## Build
- Dev server must run on port 4000 (set in vite.config.ts server.port)
- Build output goes to dist/
- Bun is used for all package installation and script execution
