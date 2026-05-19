# Documentation Website for exemplar.tools CLI Suite

## System Context

This is a single-page React application that serves as a developer reference for the exemplar.tools CLI suite. The website provides documentation for running commands across 14 different tools, sourced entirely from a single howto.md file. Developers use this site to look up command syntax, copy-paste CLI commands, and access embedded YouTube tutorials. The application is built with TypeScript, Vite, React, and Tailwind CSS, deployed to Vercel as a static site.

## Consequence Map

**High Severity:**
- Incorrect CLI commands copied by developers → broken builds, corrupted data, security vulnerabilities
- Missing or broken YouTube video embeds → developers stuck without visual guidance
- Navigation failures → developers unable to find tool documentation

**Medium Severity:**
- Styling/layout issues → poor developer experience, reduced adoption
- Slow load times → developer productivity impact
- Deployment failures → documentation unavailable

**Low Severity:**
- Version badge display issues → confusion about tool versions
- Minor formatting inconsistencies → aesthetic concerns

## Failure Archaeology

No specific failure history provided. This appears to be a new system build. Key risks identified:
- Static content extraction from markdown requires careful parsing
- YouTube embed integration needs proper iframe handling
- Copy-paste accuracy is critical for CLI commands
- Vercel deployment requires proper build output configuration

## Dependency Landscape

**Upstream Dependencies:**
- howto.md (single source of truth for all content)
- YouTube videos (external hosting, linked in howto.md)
- npm ecosystem (package management)

**Peer Dependencies:**
- Vite dev server (port 4000)
- Vercel deployment platform

**Downstream Impact:**
- Developer productivity using exemplar.tools
- Accuracy of CLI command execution in production systems

## Boundary Conditions

**In Scope:**
- Single-page React application with 14 tool pages plus home page
- Static content extraction from howto.md
- YouTube video embedding
- Version badge display
- Copy-paste optimized CLI command presentation

**Out of Scope:**
- Backend services or APIs
- Dynamic content generation
- User authentication
- Content management beyond howto.md
- Real-time updates

**Constraints:**
- Must use TypeScript (never Python)
- Output folder must be "exemplar-tools-doc"
- All source files must be .ts or .tsx
- No backend required

## Success Shape

A documentation site that prioritizes accuracy over aesthetics. Developers should be able to quickly navigate to their tool of interest, copy exact CLI commands, and access visual tutorials. The interface should be clean and functional, with clear hierarchy and reliable navigation. Content fidelity to howto.md is paramount - every command, gotcha, warning, tip, and example must be preserved exactly.

## Done When

- Website built with TypeScript, Vite, React, Tailwind CSS, npm
- Home page with pipeline diagram implemented
- 14 tool pages created, one per tool from howto.md
- All CLI commands, gotchas, warnings, tips, and examples copied exactly from howto.md
- YouTube videos properly embedded for each step
- Version badges displaying component versions
- Functional navigation between all pages
- Successfully deployable to Vercel
- Dev server runs on port 4000

## Trust and Authority Model

This is a static documentation site with no sensitive data handling. All content is public-facing developer documentation. No data classification tiers apply - all content is PUBLIC tier. No human gates or authority mappings are required. Trust policies are minimal since this is a read-only static site with no user data or sensitive operations.

## Component Topology

The system consists of a single React application component that serves static content. The application reads from howto.md at build time, generates static pages, and serves them via Vite dev server during development and static files via Vercel in production. Data flow is unidirectional from source markdown to rendered HTML/JavaScript. No component-to-component communication is required beyond standard React parent-child relationships.