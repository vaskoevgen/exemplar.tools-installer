# Documentation Website Engineering Brief

## System Context

You're building a multi-page documentation website that teaches developers how to use the exemplar.tools suite—11 AI-assisted software engineering tools arranged in workflow order. This is a React SPA that serves as the primary learning resource for developers adopting the exemplar methodology. The site features real-time commenting on each documentation page, allowing community interaction around specific tools and concepts.

The system serves two primary user groups: developers learning the exemplar.tools workflow, and community members engaging through comments. Content is sourced from canonical documentation files (howto.md and individual tool README files), ensuring consistency with the actual tool implementations.

## Consequence Map

1. **Critical**: Incorrect tool instructions or broken workflow steps could cause developers to misconfigure production systems, potentially leading to data corruption or security vulnerabilities
2. **High**: Real-time comment system failure would eliminate community knowledge sharing and support, significantly degrading the learning experience
3. **High**: Broken video embeds would prevent visual learning for complex concepts, forcing users to rely solely on text documentation
4. **Medium**: Version badge inaccuracies could lead to compatibility issues between tools
5. **Low**: Styling or navigation issues would degrade user experience but not block learning

## Failure Archaeology

This is a greenfield project with no prior failure history. However, similar documentation sites commonly fail due to:
- Content drift between documentation and actual tool behavior
- Comment systems becoming spam vectors or moderation nightmares
- Performance degradation from excessive real-time updates
- Inconsistent content sourcing leading to conflicting instructions

## Dependency Landscape

**Upstream Dependencies:**
- Tool README files and howto.md (content source of truth)
- YouTube (video hosting)
- Convex backend service (real-time infrastructure)

**Downstream Consumers:**
- Developer learning workflows
- Community knowledge base through comments
- Potential integration with exemplar.tools CLI or other tooling

**Critical Paths:**
- Content pipeline: README/howto.md → website pages
- Real-time pipeline: user interaction → Convex → live updates
- Media pipeline: YouTube embeds → learning content

## Boundary Conditions

**Scope:**
- Exactly 12 pages (home + 11 tools)
- Real-time commenting on all pages
- Dark terminal aesthetic matching exemplar.tools branding
- Step-by-step workflow presentation

**Non-Goals:**
- User authentication or user management beyond comment authoring
- Content management system or admin interface
- Integration with external documentation systems
- Mobile-specific optimizations

**Constraints:**
- Must use Bun exclusively (no npm/yarn)
- Dev server locked to port 4000
- Content must be sourced only from specified files
- Comment data model limited to: page ID, author, body, timestamp

## Success Shape

A good solution will:
- Load fast and feel responsive despite real-time features
- Present complex workflow information in digestible steps
- Enable seamless community knowledge sharing
- Maintain visual consistency with exemplar.tools identity
- Gracefully handle real-time connection issues
- Scale comment volume without performance degradation
- Keep content synchronized with canonical sources

## Done When

- [ ] SPA runs on port 4000 using Vite development server
- [ ] All 12 pages render with correct tool content from README files
- [ ] YouTube videos embed correctly using URLs from howto.md
- [ ] Version badges display current tool versions from README files
- [ ] Real-time comments work on all pages with Convex integration
- [ ] Dark industrial aesthetic implemented with specified typography
- [ ] Fixed sidebar navigation shows all tools with step numbers
- [ ] Home page displays quick-start table and ASCII workflow diagram
- [ ] Comment persistence survives page refreshes and browser sessions
- [ ] All external dependencies (fonts, videos) load reliably

## Trust and Authority Model

**Data Tiers:**
- PUBLIC: All documentation content, comments, page identifiers
- No PII, financial, auth, or compliance data in this system

**Component Authority:**
- Frontend SPA owns presentation and user interaction
- Convex backend owns comment persistence and real-time distribution
- External sources (README files, howto.md) are authoritative for content

**Human Gates:**
- No human intervention required for standard operations
- Comment moderation may require manual oversight if spam emerges

**Canary Strategy:**
- All data is public, so standard deployment with brief soak testing is sufficient
- Real-time features should be tested with multiple concurrent users

## Component Topology

**Frontend SPA**: React application handling routing, content display, and comment UI
**Convex Backend**: Real-time database and sync service managing comment storage and live updates
**Content Sources**: Static markdown files providing canonical documentation
**Media Services**: YouTube providing embedded instructional videos
**CDN/Fonts**: External font delivery for typography requirements

**Data Flows:**
- Content: README/howto.md → Frontend (build-time)
- Comments: Frontend → Convex → All connected clients (real-time)
- Media: YouTube → Frontend (embedded)
- Fonts: CDN → Frontend (CSS imports)