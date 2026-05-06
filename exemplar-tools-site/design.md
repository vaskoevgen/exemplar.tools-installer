# Design: exemplar-tools-site

*Version 1 — Auto-maintained by pact*

## Decomposition

- [C] **Root** (`root`)
  # Task

Build a multi-page documentation website for the exemplar.tools suite of AI-assisted software engineering tools.

## What to Build

A React single-page application that documents how to use th
  - [C] **App Shell, Routing & Layout** (`app_shell`)
    Create src/App.tsx with ConvexProvider wrapping BrowserRouter. Define all routes: '/' for HomePage, and '/:toolSlug' matched to ToolPage for each of the 11 tool slugs. Create src/components/Layout.tsx: fixed left sidebar + main content area. Sidebar shows text logo 'exemplar.tools' in Instrument Serif linking to '/', followed by all 11 tools listed with step number badges in order. Active route is highlighted with the tool's accent color. Sidebar collapses behind a hamburger toggle on screens < 768px. Main content area wraps an <Outlet> with an animated fade-in transition (CSS/Tailwind animation on route change using a key tied to location.pathname). Background grid pattern visible on all pages.
  - [ ] **Data Constants & Convex Backend** (`data_layer`)
    Create src/data/tools.ts: typed array of all 11 tool objects containing slug, name, one-line description, step number (1–11), version string, accent color hex, YouTube embed URL (undefined for kindex), and placeholder step-by-step instructions (array of {title, bash} objects with realistic fabricated bash snippets). Define per-tool accent colors as a harmonious dark-theme palette. Create convex/schema.ts defining the 'comments' table (page: v.string(), author: v.string(), body: v.string(), createdAt: v.number()). Create convex/comments.ts with query function listComments(page) returning comments filtered and sorted by createdAt, and mutation addComment(page, author, body) inserting a comment with Date.now() timestamp. All Convex functions fully typed.
  - [ ] **Home Page** (`home_page`)
    Create src/pages/HomePage.tsx rendering at '/'. Contains: workflow overview paragraph text, a quick-start table listing all 11 tools (columns: step number, tool name as link, one-line description), and the ClosedLoopDiagram component. Create src/components/ClosedLoopDiagram.tsx: an SVG/React component that arranges the 11 tools in a circular flow with connecting arrows, each tool node rendered in its accent color. Component is responsive and visually fits the dark terminal aesthetic with cyan accents.
  - [C] **Project Scaffold & Configuration** (`project_scaffold`)
    Initialize the Vite + React + TypeScript project with bun create vite. Configure vite.config.ts (port 4000, build output dist/). Install and configure Tailwind CSS v3 (pinned), React Router v6, Convex npm package. Set up tailwind.config.js with custom colors, fonts (Instrument Serif, JetBrains Mono, Inter via Google Fonts link in index.html), and the background grid utility. Configure vitest in vite.config.ts or vitest.config.ts. Create the global CSS entry point importing Tailwind directives with the dark near-black background (#0a0a0a), subtle grid pattern as a Tailwind utility/plugin, and font-face assignments. Ensure bun.lockb is the only lockfile. Add scripts to package.json: dev, build, test (vitest).
  - [C] **Test Harness & Smoke Tests** (`tests`)
    Create src/__tests__/setup.ts for vitest configuration. Create minimal smoke tests: verify tool data array has 11 entries with correct slugs, verify each tool has required fields (name, description, step, version, accentColor), verify kindex has no videoUrl, verify components render without throwing (using @testing-library/react for at least one component render test). Ensure `bunx vitest run` executes without configuration errors.
  - [C] **Tool Page & Comments Section** (`tool_page`)
    Create src/pages/ToolPage.tsx: reads toolSlug from useParams, looks up tool data from constants. Renders: tool name heading, one-line description, step number badge (styled pill), version badge, step-by-step instructions where each step has a title and a bash code block styled with JetBrains Mono in a dark terminal card. Conditionally renders YouTube iframe embed only when the tool has a video URL (kindex omits this section). Below content, renders the CommentsSection component. Create src/components/CommentsSection.tsx: uses Convex useQuery for listComments(page) and useMutation for addComment. Displays real-time comment list (author, body, relative timestamp). Form with author text input, body textarea, and submit button. Inputs validated (non-empty). Each tool page uses its accent color for badges and headings. Create src/components/StepBadge.tsx, src/components/VersionBadge.tsx, src/components/CodeBlock.tsx, src/components/VideoEmbed.tsx as reusable presentational sub-components to keep files under 300 lines.
