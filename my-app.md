# exemplar.tools Documentation Website

Build a documentation website for the exemplar.tools CLI suite.
Developers will use this site as a reference for running commands — all content must be exact as in howto.md.

## Tech Stack

CRITICAL: implementation language is TypeScript. Never generate Python. All source files must be .ts or .tsx.

- TypeScript
- Vite (dev server on port 4000)
- React
- Tailwind CSS
- Bun (package manager — never use npm)
- Convex (database, use CLI: `npx convex dev`)

## Project Structure

Output folder: exemplar-tools-doc

Components must be separate:
- Frontend: React SPA (Vite + React + Tailwind)
- Backend: Convex serverless functions
- Database: Convex document store

## Pages

One page per tool from howto.md:
- Home / overview with the pipeline diagram
- Step 0 — Cartographer
- Step 1a — Constrain
- Step 1b — Ledger
- Step 2a — Pact
- Step 2b — Advocate
- Step 3 — Arbiter
- Step 4 — Baton
- Step 5a — Sentinel
- Step 5b — Chronicler
- Step 5c — Stigmergy
- Step 6 — Apprentice
- Step 7 — Kindex

## Features

- All CLI commands must be copied verbatim from howto.md (developers copy-paste from this site)
- Embed YouTube videos linked in howto.md for each step
- Version badges showing component versions
- Comment section on each tool page (stored in Convex, anyone can post)
- Navigation between pages

## Content Requirements

Copy every command, gotcha, warning, tip, and example exactly as written in howto.md.
The website is a developer reference — accuracy is more important than brevity.

## Deployment

Vercel (bunx vercel).

## pact.yaml

```yaml
language: typescript
test_framework: vitest
```
