# Documentation Website for exemplar.tools

## What to Build

A multi-page documentation website that teaches developers how to use the exemplar.tools suite of AI-assisted software engineering tools. The site documents the following tools in order of the workflow: Constrain, Ledger, Pact, Advocate, Arbiter, Baton, Sentinel, Chronicler, Stigmergy, Apprentice, and Kindex.

## Frontend Component

The frontend is a single-page application built with Vite, React, and TypeScript, styled with Tailwind CSS, using Bun as the package manager and runtime. It runs a development server on port 4000. The frontend handles routing (one page per tool), renders documentation content, embeds YouTube videos from the session log table in howto.md, displays version badges for each tool, and renders a comments section on every page.

## Database Component

The database component uses Convex as a real-time backend. It stores user comments. Each comment has a page identifier (a string for the tool name), an author name (a string), comment body text, and a creation timestamp. The Convex schema defines a comments table with those four fields. Comments are fetched in real time using Convex React hooks and displayed below the documentation content on each page.

## UI Component

The UI is a dark industrial terminal aesthetic. The background is near-black. Primary accent color is electric cyan. Each tool page has its own accent color from a curated palette. Typography uses Instrument Serif for headings and JetBrains Mono for code blocks. Navigation is a fixed sidebar showing all tool names with step numbers. Each tool page shows the tool description, the step-by-step instructions from howto.md, a YouTube video embed (where available), a version badge pulled from the tool README, and a comments section at the bottom. The home page shows the quick-start table and the closed loop diagram as ASCII art.

## Backend Component

The backend is Convex, which serves as both database and serverless functions. Convex functions handle creating new comments and querying comments by page. No separate server process is needed beyond the Convex cloud backend.

## Key Requirements

- One page per tool: home, constrain, ledger, pact, advocate, arbiter, baton, sentinel, chronicler, stigmergy, apprentice, kindex
- YouTube videos embedded on the relevant step pages (using the video URLs from howto.md)
- Version badges shown for each tool, sourced from the tool README files
- Comments section on every page backed by Convex real-time database
- Step-by-step instructions matching the order in howto.md
- Content drawn from both howto.md and the README of each tool repository
- Bun used exclusively, never npm or yarn
- Dev server runs on port 4000
- Tailwind CSS for all styling
- React Router v6 for client-side navigation
