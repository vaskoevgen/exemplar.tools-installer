# Design: exemplar-tools-doc

*Version 1 — Auto-maintained by pact*

## Decomposition

- [C] **Root** (`root`)
  # exemplar.tools Documentation Website

Build a documentation website for the exemplar.tools CLI suite.
Developers will use this site as a reference for running commands — all content must be exact as
  - [C] **App Shell & Routing** (`app_routing`)
    Main App.tsx and routing configuration using react-router-dom BrowserRouter. Defines routes for all 13 pages: / (Home), /step-0-cartographer, /step-1a-constrain, /step-1b-ledger, /step-2a-pact, /step-2b-advocate, /step-3-arbiter, /step-4-baton, /step-5a-sentinel, /step-5b-chronicler, /step-5c-stigmergy, /step-6-apprentice, /step-7-kindex. Also includes the route manifest (array of { path, label, componentKey } objects) as a shared data structure consumed by Sidebar and the route definitions. Entry point main.tsx renders App into #root. Includes smoke test verifying all routes are registered.
  - [C] **Page Components (13 pages)** (`page_components`)
    One React component per page, each in its own file (<300 LOC). Content is manually transcribed from howto.md into JSX using shared components (CodeBlock for CLI commands, VideoEmbed for YouTube links, VersionBadge for versions, CalloutBox for gotchas/warnings/tips). Pages: HomePage (pipeline diagram as SVG/image + overview), CartographerPage, ConstrainPage, LedgerPage, PactPage, AdvocatePage, ArbiterPage, BatonPage, SentinelPage, ChroniclerPage, StigmergyPage, ApprenticePage, KindexPage. Every CLI command, gotcha, warning, tip, and example is verbatim from howto.md. Each page component has a vitest rendering smoke test verifying it renders without crashing and contains expected heading text. The pipeline diagram asset (SVG) is included or referenced from a static assets directory.
  - [C] **Project Scaffold & Configuration** (`project_scaffold`)
    Initialize the exemplar-tools-doc/ project directory with all configuration files: package.json (with dependencies: react, react-dom, react-router-dom, vite, tailwindcss, vitest, @testing-library/react, @testing-library/jest-dom, jsdom, prism-react-renderer), tsconfig.json, vite.config.ts (dev server port 4000), tailwind.config.ts, postcss.config.ts, index.html, vercel.json (SPA rewrite rule: { "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }). Also includes the vitest setup file (vitest.setup.ts importing @testing-library/jest-dom). No .py or .js source files. All config that must be .js (e.g. postcss) uses .ts or .mjs equivalent.
  - [C] **Shared UI Components** (`shared_components`)
    Reusable React components used across pages: (1) Sidebar — persistent navigation sidebar with links to all 13 pages using react-router-dom NavLink, highlighting active route. (2) CodeBlock — wraps prism-react-renderer to display CLI commands with syntax highlighting and a copy-to-clipboard button (navigator.clipboard.writeText). (3) VersionBadge — displays a version string in a styled badge (Tailwind pill). (4) VideoEmbed — renders a YouTube iframe given a video URL, with responsive aspect-ratio styling. (5) PageLayout — shell component that renders Sidebar + content area, responsive down to 768px. (6) CalloutBox — renders gotchas/warnings/tips with distinct visual styles (color-coded borders/icons). Each component exported as named + default. Each has a vitest smoke test.

## Engineering Decisions

### 
**Decision:** Four-component decomposition rather than trivial
**Rationale:** With 13 page components, shared UI components, routing configuration, and project scaffolding, the total LOC will significantly exceed 500. The 300-line-per-file SOP constraint alone forces at least 15+ source files. The four components have clean interfaces: scaffold produces config, shared_components produces reusable React elements, page_components consumes shared_components and howto.md content, app_routing wires pages into routes.

### 
**Decision:** Route slugs follow AS3 pattern exactly
**Rationale:** URL slugs: /, /step-0-cartographer, /step-1a-constrain, /step-1b-ledger, /step-2a-pact, /step-2b-advocate, /step-3-arbiter, /step-4-baton, /step-5a-sentinel, /step-5b-chronicler, /step-5c-stigmergy, /step-6-apprentice, /step-7-kindex. These are the source-of-truth strings per the SOP on string keys in maps.

### 
**Decision:** prism-react-renderer for syntax highlighting with copy button
**Rationale:** AS9 specifies prism-react-renderer. CodeBlock component wraps it and adds a copy-to-clipboard button using navigator.clipboard API, satisfying AC15.

### 
**Decision:** Route manifest as shared data structure
**Rationale:** A single exported array of route definitions (path, label, componentKey) serves as the source of truth for both the Sidebar navigation and the router configuration, preventing slug mismatches per the SOP on string keys.

### 
**Decision:** Page components depend on shared_components but not on app_routing
**Rationale:** Pages are leaf content components that consume CodeBlock, VideoEmbed, etc. The routing layer (app_routing) depends on pages to wire them into routes, not the reverse. This keeps the dependency graph acyclic and shallow.

### 
**Decision:** Pipeline diagram as static SVG asset
**Rationale:** Per AS5, the pipeline diagram is a static visual. It will be placed in a public/ or src/assets/ directory and rendered in HomePage via an <img> or inline SVG component.
