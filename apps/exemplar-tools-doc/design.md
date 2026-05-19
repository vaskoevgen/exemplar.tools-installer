# Design: exemplar-tools-doc

*Version 1 — Auto-maintained by pact*

## Decomposition

- [C] **Root** (`root`)
  # exemplar.tools Documentation Website

Build a documentation website for the exemplar.tools CLI suite.
Developers will use this site as a reference for running commands — all content must be exact as
  - [ ] **Step Page Content & Data** (`page_content`)
    All 14 page components with hardcoded content from howto.md. Includes: (1) A STEP_CONTENT data structure holding per-step commands, gotchas, warnings, tips, examples, YouTube URLs, and version strings — all verbatim from howto.md. (2) HomePage component rendering overview text + PipelineDiagram. (3) StepPage generic component that receives step data and renders sections using CodeBlock, CalloutBox, YouTubeEmbed, and VersionBadge. (4) Individual page wrapper components for each of the 13 steps (CartographerPage, ConstrainPage, LedgerPage, PactPage, AdvocatePage, ArbiterPage, BatonPage, SentinelPage, ChroniclerPage, StigmergyPage, ApprenticePage, KindexPage). Content placeholder structure is built now; exact howto.md text is filled when the file is provided. Tests verify each page renders its key sections, code blocks, and embeds.
  - [ ] **Pipeline Diagram Component** (`pipeline_diagram`)
    Custom React/SVG component for the Home page showing the exemplar.tools pipeline flow. Renders step boxes (Step 0 through Step 7) connected by arrows/lines in the correct order, with branching for parallel steps (1a/1b, 2a/2b, 5a/5b/5c). Each box is clickable and navigates to the corresponding step page via React Router. Responsive sizing. Named export PipelineDiagram. Tests verify all step nodes render and click navigation.
  - [C] **Project Scaffold & Configuration** (`project_scaffold`)
    Bootstraps the exemplar-tools-doc project: package.json with all dependencies (react, react-dom, react-router-dom, vite, tailwindcss, vitest, @testing-library/react, jsdom), vite.config.ts (port 4000), tsconfig.json (strict mode), tailwind.config.js, postcss.config.js, index.html entry point, vercel.json with SPA rewrites, and the main App.tsx shell that sets up BrowserRouter. All config files only — no page content. Named exports only per SOP.
  - [C] **Routing, Layout & Navigation** (`routing_and_layout`)
    Implements the routing data model and layout shell. Includes: (1) ROUTE_SLUG_MAP constant mapping all 14 routes (home + 13 steps) with leading-slash values, (2) a persistent Sidebar component with NavLinks to all pages highlighting the active route, (3) a Layout component wrapping sidebar + content area with React Router <Outlet>, (4) route registration in App.tsx using createBrowserRouter or <Routes>. All use React Router v6 browser history mode. Slug guard utility: slug.startsWith('/') ? slug : '/' + slug. Tests verify all 14 routes exist, no double-slash bugs, and sidebar renders all links.
  - [C] **Shared UI Components** (`shared_ui`)
    Reusable presentational components used across all pages: (1) CodeBlock — renders preformatted CLI commands with syntax styling and a copy-to-clipboard button (navigator.clipboard.writeText), (2) VersionBadge — styled inline badge displaying a component name + version string, (3) YouTubeEmbed — responsive iframe wrapper for YouTube video URLs, (4) CalloutBox — styled container for gotchas, warnings, and tips with variant prop (gotcha | warning | tip). All components have explicit type annotations, named exports, and vitest + @testing-library/react tests.
