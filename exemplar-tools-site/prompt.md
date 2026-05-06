# Documentation Website Engineering Brief

## System Context

This is a multi-page documentation website that teaches developers how to use the exemplar.tools suite of AI-assisted software engineering tools. The site features 11 tools presented in workflow order, with embedded instructional videos, dynamic version badges, and real-time user commenting. Built as a modern React SPA with Tailwind styling, it serves as the primary learning resource for developers adopting the exemplar.tools ecosystem.

Primary users are software engineers learning the exemplar.tools workflow, ranging from newcomers exploring AI-assisted development to experienced developers integrating specific tools into their process.

## Consequence Map

**Critical Failures:**
- Content synchronization breaks: version badges show wrong versions, leading developers to use incompatible tool versions
- Real-time commenting system fails during high traffic, losing community discussions and user feedback
- Video embeds break, eliminating primary instructional content

**Significant Failures:**  
- Build system corruption requiring manual recovery
- Navigation breaks between tool pages, disrupting learning flow
- Performance degradation making the site unusable on mobile devices

**Minor Failures:**
- Styling inconsistencies across pages
- Comment loading delays
- Version badge update lag

## Failure Archaeology

This appears to be a greenfield project with no documented failure history. Key risks identified from the technology stack:
- Bun is relatively new; ecosystem compatibility issues possible
- Convex real-time backend introduces complexity in data consistency
- Multiple external dependencies (YouTube, tool repositories) create failure surfaces
- Version badge synchronization requires careful caching strategy

## Dependency Landscape

**External Dependencies:**
- Tool repositories for version badge data
- YouTube for video content delivery
- howto.md content file as source of truth

**Internal Build Chain:**
- Bun (package manager + runtime) → Vite (build tool) → React + TypeScript
- Convex backend for real-time features
- Tailwind for styling compilation

**Critical Path:** Content updates flow from howto.md and tool READMEs → build system → deployed site. Any break in this chain blocks content updates.

## Boundary Conditions

**Scope:**
- Exactly 12 pages: home + 11 tool pages in prescribed order
- Content strictly sourced from howto.md and tool README files
- Real-time commenting on every page
- YouTube video embedding from howto.md URLs only

**Non-Goals:**
- Content management system
- User authentication beyond commenting
- Tool download/installation features
- Analytics beyond basic usage

**Hard Constraints:**
- Must use Bun exclusively (never npm/yarn)
- Dev server on port 4000
- Tailwind CSS only for styling
- React Router v6 for navigation

## Success Shape

A good solution will:
- Load quickly on mobile devices
- Maintain content freshness automatically
- Provide smooth navigation between learning steps
- Handle comment system load gracefully
- Degrade gracefully when external dependencies fail
- Support rapid content updates from source files
- Maintain visual consistency across all pages

## Done When

- [ ] 12 pages exist and render correctly: home, constrain, ledger, pact, advocate, arbiter, baton, sentinel, chronicler, stigmergy, apprentice, kindex
- [ ] YouTube videos embed successfully on pages where specified in howto.md
- [ ] Version badges display current versions from tool README files
- [ ] Comments can be posted and viewed in real-time on all pages
- [ ] Step-by-step instructions match howto.md order exactly
- [ ] `bun dev` starts server on port 4000
- [ ] No npm or yarn commands used anywhere in build process
- [ ] All styling uses Tailwind CSS classes
- [ ] Navigation works between all pages using React Router v6
- [ ] Site builds and deploys without errors
- [ ] Comment persistence survives page refreshes

## Trust and Authority Model

**Data Tiers:**
- PUBLIC: All content, comments, video URLs, tool information
- No sensitive data identified in this system

**Authority:**
- Web frontend owns comment display and user interaction
- Convex backend owns comment storage and real-time synchronization
- Tool repositories own version information (read-only)
- howto.md owns instructional content (read-only)

**Human Gates:**
- No human approval required for standard operations
- Content updates flow automatically from source files

**Canary Strategy:**
- 1-hour soak for all changes to PUBLIC data
- Target: 1000 requests during soak period
- No special canary patterns needed

## Component Topology

**Web Frontend (React SPA):**
- Renders 12 pages with Tailwind styling
- Handles client-side routing via React Router v6
- Consumes YouTube embed API
- Connects to Convex for real-time comments

**Build System (Vite + Bun):**
- Compiles TypeScript and React components
- Processes Tailwind CSS
- Serves development environment on port 4000

**Convex Backend:**
- Stores and synchronizes comments in real-time
- Provides React hooks for frontend integration

**External Content Sources:**
- Tool repositories provide version badge data
- howto.md provides instructional content structure
- YouTube hosts embedded videos

**Data Flows:**
- Content: howto.md + tool READMEs → build system → web frontend
- Comments: web frontend ↔ Convex backend (bidirectional real-time)
- Videos: YouTube → web frontend (embed)
- Versions: tool repos → web frontend (periodic fetch)