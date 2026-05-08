import { useParams, Link } from 'react-router-dom'
import CommentsSection from '../components/CommentsSection'

interface ComponentDef {
  slug: string
  name: string
  icon: string
  accent: string
  accentBg: string
  version: string
  tagline: string
  description: string
  responsibilities: string[]
  techStack: { name: string; purpose: string }[]
  files: { path: string; role: string }[]
  commands: string[]
  notes: string[]
  integrations: { with: string; how: string }[]
}

const COMPONENTS: ComponentDef[] = [
  {
    slug: 'frontend',
    name: 'Frontend',
    icon: '⬡',
    accent: '#22d3ee',
    accentBg: 'rgba(34,211,238,0.08)',
    version: '0.0.0',
    tagline: 'React SPA — Vite + TypeScript + Tailwind CSS',
    description:
      'The frontend is a React single-page application built with Vite 8, React 19, and TypeScript. It handles all routing, renders documentation content for 11 tools, embeds YouTube videos, shows version badges, and presents a real-time comments section on every page.',
    responsibilities: [
      'Client-side routing via React Router v6 (BrowserRouter)',
      'Render tool documentation pages from typed data registry (tools.ts)',
      'Embed YouTube iframes for each session video',
      'Display per-tool version badges with accent colors',
      'Serve comments form and live comment list via Convex hooks',
      'Component pages for frontend, backend, database, and UI architecture',
    ],
    techStack: [
      { name: 'Vite 8', purpose: 'Build tool and dev server (port 4000)' },
      { name: 'React 19', purpose: 'Component framework (functional components only)' },
      { name: 'TypeScript 6', purpose: 'Implementation language — all files are .ts/.tsx' },
      { name: 'Tailwind CSS v3', purpose: 'All styling — no custom CSS files' },
      { name: 'React Router v6', purpose: 'Client-side navigation with BrowserRouter' },
      { name: 'Bun', purpose: 'Package manager and runtime — never npm or yarn' },
    ],
    files: [
      { path: 'src/main.tsx', role: 'App entry point — ConvexProvider wraps App' },
      { path: 'src/App.tsx', role: 'Route tree — /, /getting-started, /tool/:slug, /component/:slug' },
      { path: 'src/pages/HomePage.tsx', role: 'Overview — quick-start table + closed loop ASCII diagram' },
      { path: 'src/pages/ToolPage.tsx', role: 'Per-tool documentation page (activated by /tool/:slug)' },
      { path: 'src/pages/ComponentPage.tsx', role: 'Architecture pages (this page)' },
      { path: 'src/pages/GettingStartedPage.tsx', role: 'Install guide + session log table with videos' },
      { path: 'src/data/tools.ts', role: 'Typed registry of all 11 tool definitions' },
      { path: 'src/components/Sidebar.tsx', role: 'Fixed left nav with step numbers and active highlight' },
      { path: 'src/components/VersionBadge.tsx', role: 'Per-tool version chip' },
      { path: 'src/components/VideoEmbed.tsx', role: 'YouTube iframe wrapper with aspect-ratio container' },
      { path: 'src/components/CommentsSection.tsx', role: 'Real-time Convex-backed comments form + list' },
    ],
    commands: [
      '# Install dependencies\nbun install',
      '# Start dev server on port 4000\nbun run dev',
      '# Type-check\nbun run build',
      '# Lint\nbun run lint',
    ],
    notes: [
      'Dev server is configured to port 4000 in vite.config.ts — do not change',
      'All imports must be .ts or .tsx — never .py or .js',
      'Convex URL is read from VITE_CONVEX_URL env var (set by bunx convex dev)',
    ],
    integrations: [
      { with: 'Convex Backend', how: 'useQuery / useMutation hooks from convex/react — real-time comment sync' },
      { with: 'YouTube Service', how: 'iframe embeds with youtube.com/embed/* URLs — no API key needed' },
      { with: 'Google Fonts', how: 'Instrument Serif + JetBrains Mono loaded in index.html via link tag' },
    ],
  },
  {
    slug: 'backend',
    name: 'Backend',
    icon: '⬡',
    accent: '#a78bfa',
    accentBg: 'rgba(167,139,250,0.08)',
    version: '1.37.0',
    tagline: 'Convex serverless functions — real-time sync engine',
    description:
      'The backend is Convex — a TypeScript-native serverless backend that handles real-time data sync. It exposes query and mutation functions for the comments feature. No separate server process is needed; Convex runs as a managed cloud service (or local SQLite in dev mode).',
    responsibilities: [
      'Persist user comments to the Convex document store',
      'Query comments by page identifier with real-time subscriptions',
      'Push live updates to all connected clients without polling',
      'Validate data shapes via Convex value validators (v.string, v.number)',
      'Run schema migrations via convex dev push',
    ],
    techStack: [
      { name: 'Convex 1.37.0', purpose: 'Managed backend platform — database + functions + sync' },
      { name: 'TypeScript', purpose: 'All Convex functions are .ts — same language as frontend' },
      { name: 'Convex CLI', purpose: 'bunx convex dev — runs local backend for development' },
    ],
    files: [
      { path: 'convex/schema.ts', role: 'Database schema — defines comments table with by_page index' },
      { path: 'convex/comments.ts', role: 'getByPage query + add mutation — the two API functions' },
      { path: 'convex/tsconfig.json', role: 'TypeScript config for Convex runtime' },
      { path: 'convex/_generated/', role: 'Auto-generated type bindings (never edit manually)' },
    ],
    commands: [
      '# Start local Convex dev backend\nbunx convex dev',
      '# Push schema changes\nbunx convex dev --once',
      '# Deploy to Convex cloud\nbunx convex deploy',
    ],
    notes: [
      'convex/_generated/ is auto-generated by bunx convex dev — never edit these files',
      'The VITE_CONVEX_URL is printed by bunx convex dev and must go in .env.local',
      'In dev mode, Convex uses a local SQLite file at .convex/local/default/convex_local_backend.sqlite3',
      'Comments survive page refresh and sync in real time across all open tabs',
    ],
    integrations: [
      { with: 'Frontend', how: 'ConvexReactClient in src/main.tsx — connects to VITE_CONVEX_URL' },
      { with: 'Database', how: 'Convex is both the backend AND the database — they are the same service' },
    ],
  },
  {
    slug: 'database',
    name: 'Database',
    icon: '⬡',
    accent: '#34d399',
    accentBg: 'rgba(52,211,153,0.08)',
    version: '1.37.0',
    tagline: 'Convex document store — real-time, indexed, type-safe',
    description:
      'The database layer is Convex\'s built-in document store. It stores user comments with automatic timestamps and a server-side index for fast per-page queries. Schema is defined in TypeScript and enforced at the Convex layer — no SQL migrations needed.',
    responsibilities: [
      'Store comments with automatic _id and _creationTime fields',
      'Index comments by page for O(log n) per-page lookups',
      'Enforce schema via Convex value validators at insert time',
      'Provide real-time subscription to comment changes per page',
    ],
    techStack: [
      { name: 'Convex document store', purpose: 'NoSQL document storage with reactive queries' },
      { name: 'Convex schema.ts', purpose: 'Type-safe schema definition using defineSchema + defineTable' },
      { name: 'Convex indexes', purpose: 'by_page index for efficient per-page comment queries' },
    ],
    files: [
      { path: 'convex/schema.ts', role: 'Schema definition — comments table, field types, and by_page index' },
      { path: 'schemas/comments.yaml', role: 'Ledger schema mirror — registered with ledger schema add' },
    ],
    commands: [
      '# Schema (convex/schema.ts)\nimport { defineSchema, defineTable } from \'convex/server\'\nimport { v } from \'convex/values\'\n\nexport default defineSchema({\n  comments: defineTable({\n    page: v.string(),\n    author: v.string(),\n    body: v.string(),\n  }).index(\'by_page\', [\'page\']),\n})',
      '# Query by page\nexport const getByPage = query({\n  args: { page: v.string() },\n  handler: async (ctx, { page }) => {\n    return ctx.db\n      .query(\'comments\')\n      .withIndex(\'by_page\', (q) => q.eq(\'page\', page))\n      .order(\'desc\')\n      .collect()\n  },\n})',
      '# Add comment mutation\nexport const add = mutation({\n  args: { page: v.string(), author: v.string(), body: v.string() },\n  handler: async (ctx, args) => {\n    return ctx.db.insert(\'comments\', args)\n  },\n})',
    ],
    notes: [
      '_id and _creationTime are auto-added by Convex — do not define them in schema',
      'Convex validates all inserted documents against the schema at runtime',
      'The by_page index allows the frontend to query only comments for the current page',
      'Local dev backend: SQLite at .convex/local/default/convex_local_backend.sqlite3',
    ],
    integrations: [
      { with: 'Ledger', how: 'schemas/comments.yaml mirrors the Convex schema — registered with ledger schema add' },
      { with: 'Backend', how: 'Convex database and backend are the same service — schema.ts is the contract' },
    ],
  },
  {
    slug: 'ui',
    name: 'UI',
    icon: '⬡',
    accent: '#f472b6',
    accentBg: 'rgba(244,114,182,0.08)',
    version: '3.0.0',
    tagline: 'Dark industrial terminal aesthetic — Tailwind v3 design system',
    description:
      'The UI layer is the design system implemented in Tailwind CSS v3. Industrial terminal dark aesthetic with near-black backgrounds, electric cyan primary accent, and per-tool accent colors. Typography uses Instrument Serif for display headings and JetBrains Mono for code blocks.',
    responsibilities: [
      'Define the color palette — near-black #0a0a0f base, cyan #22d3ee primary accent',
      'Per-tool accent colors: amber (Constrain), violet (Ledger), cyan (Pact), blue (Advocate), etc.',
      'Typography: Instrument Serif (display), JetBrains Mono (code), Inter (body)',
      'Fixed sidebar navigation with step number labels',
      'Version badges with per-tool accent colors',
      'YouTube video embeds with 16:9 aspect-ratio containers',
      'Code blocks with syntax highlighting using dark background',
      'Warning/bug/info callout boxes with color-coded borders',
      'Fade-in + slide-up page animations via custom Tailwind keyframes',
    ],
    techStack: [
      { name: 'Tailwind CSS v3', purpose: 'All styling — no custom CSS files except index.css for font imports' },
      { name: 'Instrument Serif', purpose: 'Display font — headings and tool names (Google Fonts)' },
      { name: 'JetBrains Mono', purpose: 'Code font — all code blocks and monospace labels (Google Fonts)' },
      { name: 'Custom keyframes', purpose: 'animate-fade-in and animate-slide-up via tailwind.config.js' },
    ],
    files: [
      { path: 'src/index.css', role: 'Global styles — @tailwind directives + Google Fonts import' },
      { path: 'tailwind.config.js', role: 'Tailwind config — custom fonts, colors, keyframes, animation' },
      { path: 'src/components/VersionBadge.tsx', role: 'Version chip — accent color background + border' },
      { path: 'src/components/VideoEmbed.tsx', role: 'YouTube iframe — 16:9 aspect-ratio responsive container' },
      { path: 'src/components/CommentsSection.tsx', role: 'Comments UI — dark input fields, accent-colored button' },
      { path: 'src/components/Sidebar.tsx', role: 'Fixed sidebar — step numbers, active highlight, tool links' },
    ],
    commands: [
      '# Color palette used across the site\nbackground:    #0a0a0f  (near-black)\nsurface:       #12121a  (card background)\nborder:        #1e1e2e  (subtle border)\nprimary:       #22d3ee  (electric cyan)\ntext-main:     #f1f5f9  (slate-100)\ntext-muted:    #94a3b8  (slate-400)',
      '# Per-tool accent colors\nconstrain:  #f59e0b  (amber)\nledger:     #8b5cf6  (violet)\npact:       #22d3ee  (cyan)\nadvocate:   #3b82f6  (blue)\narbiter:    #ef4444  (red)\nbaton:      #10b981  (emerald)\nsentinel:   #f97316  (orange)\nchronicler: #ec4899  (pink)\nstigmergy:  #06b6d4  (sky)\napprentice: #84cc16  (lime)\nkindex:     #a78bfa  (purple)',
      '# Tailwind keyframes (tailwind.config.js)\nkeyframes: {\n  \'fade-in\': { \'0%\': { opacity: \'0\' }, \'100%\': { opacity: \'1\' } },\n  \'slide-up\': { \'0%\': { opacity: \'0\', transform: \'translateY(16px)\' }, \'100%\': { opacity: \'1\', transform: \'translateY(0)\' } },\n}',
    ],
    notes: [
      'All styling is Tailwind utility classes — no styled-components, no CSS modules',
      'Custom fonts are loaded from Google Fonts in index.css via @import',
      'Accent colors are defined per-tool in src/data/tools.ts (accent + accentBg fields)',
      'The sidebar is fixed position (w-56) — main content has ml-56 offset',
    ],
    integrations: [
      { with: 'Frontend', how: 'Tailwind classes used inline in every .tsx component' },
      { with: 'Tools data', how: 'accent + accentBg colors from tools.ts drive all per-tool color theming' },
    ],
  },
]

export const COMPONENT_MAP: Record<string, ComponentDef> = Object.fromEntries(
  COMPONENTS.map((c) => [c.slug, c])
)

export const COMPONENT_LIST = COMPONENTS

function SectionHeader({ title }: { title: string }) {
  return <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4 mt-10">{title}</h2>
}

function CodeBlock({ code }: { code: string }) {
  return (
    <pre className="font-mono text-sm bg-[#12121a] border border-[#1e1e2e] rounded-lg p-4 overflow-x-auto mb-4 whitespace-pre-wrap">
      <code className="text-slate-300">{code}</code>
    </pre>
  )
}

export default function ComponentPage() {
  const { slug } = useParams<{ slug: string }>()
  const comp = slug ? COMPONENT_MAP[slug] : undefined

  if (!comp) {
    return (
      <main className="max-w-4xl mx-auto px-8 py-14">
        <p className="text-slate-500 font-mono">Component not found.</p>
        <Link to="/" className="text-cyan-400 hover:text-cyan-300 text-sm mt-2 inline-block">← Overview</Link>
      </main>
    )
  }

  const compIdx = COMPONENTS.findIndex((c) => c.slug === comp.slug)
  const prev = compIdx > 0 ? COMPONENTS[compIdx - 1] : null
  const next = compIdx < COMPONENTS.length - 1 ? COMPONENTS[compIdx + 1] : null

  return (
    <main className="max-w-4xl mx-auto px-8 py-14 animate-fade-in">

      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-4">
          <span
            className="font-mono text-xs px-2 py-0.5 rounded border"
            style={{ background: comp.accentBg, color: comp.accent, borderColor: comp.accent + '33' }}
          >
            component
          </span>
          <span
            className="font-mono text-xs px-2 py-0.5 rounded border"
            style={{ borderColor: comp.accent + '44', color: comp.accent + 'bb' }}
          >
            v{comp.version}
          </span>
        </div>
        <h1 className="font-display text-5xl leading-tight mb-3" style={{ color: comp.accent }}>
          {comp.name}
        </h1>
        <p className="text-slate-400 text-lg leading-relaxed max-w-2xl">{comp.tagline}</p>
      </div>

      <div className="h-px mb-10" style={{ background: `linear-gradient(to right, ${comp.accent}33, transparent)` }} />

      {/* Description */}
      <section>
        <SectionHeader title="Overview" />
        <p className="text-slate-300 leading-relaxed">{comp.description}</p>
      </section>

      {/* Responsibilities */}
      <section>
        <SectionHeader title="Responsibilities" />
        <ul className="space-y-2">
          {comp.responsibilities.map((r, i) => (
            <li key={i} className="flex items-start gap-3 text-slate-400 text-sm">
              <span className="font-mono mt-0.5 shrink-0" style={{ color: comp.accent }}>→</span>
              <span>{r}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Tech Stack */}
      <section>
        <SectionHeader title="Tech Stack" />
        <div className="rounded-lg border border-[#1e1e2e] overflow-hidden">
          {comp.techStack.map((t, i) => (
            <div
              key={i}
              className={`flex items-start gap-4 px-4 py-3 ${i < comp.techStack.length - 1 ? 'border-b border-[#1e1e2e]' : ''}`}
            >
              <span className="font-mono text-sm shrink-0 w-40" style={{ color: comp.accent }}>{t.name}</span>
              <span className="text-slate-400 text-sm">{t.purpose}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Key Files */}
      <section>
        <SectionHeader title="Key Files" />
        <div className="rounded-lg border border-[#1e1e2e] overflow-hidden">
          {comp.files.map((f, i) => (
            <div
              key={i}
              className={`flex items-start gap-4 px-4 py-3 ${i < comp.files.length - 1 ? 'border-b border-[#1e1e2e]' : ''}`}
            >
              <code className="font-mono text-xs text-cyan-400 shrink-0 min-w-0 break-all w-64">{f.path}</code>
              <span className="text-slate-400 text-sm">{f.role}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Commands / Code */}
      <section>
        <SectionHeader title="Commands" />
        {comp.commands.map((cmd, i) => (
          <CodeBlock key={i} code={cmd} />
        ))}
      </section>

      {/* Notes */}
      {comp.notes.length > 0 && (
        <section>
          <SectionHeader title="Notes" />
          <div className="space-y-2">
            {comp.notes.map((note, i) => (
              <div
                key={i}
                className="rounded-lg border px-4 py-3"
                style={{ borderColor: comp.accent + '33', background: comp.accentBg }}
              >
                <p className="text-slate-400 text-sm leading-relaxed">
                  <span className="font-mono text-xs font-semibold mr-2" style={{ color: comp.accent }}>ℹ</span>
                  {note}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Integrations */}
      <section>
        <SectionHeader title="Integrations" />
        <div className="space-y-3">
          {comp.integrations.map((int, i) => (
            <div key={i} className="rounded-lg border border-[#1e1e2e] px-4 py-3 bg-[#12121a]">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs font-semibold" style={{ color: comp.accent }}>
                  ↔ {int.with}
                </span>
              </div>
              <p className="text-slate-400 text-sm">{int.how}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Navigation */}
      <div className="mt-16 flex items-center justify-between border-t border-[#1e1e2e] pt-8">
        {prev ? (
          <Link
            to={`/component/${prev.slug}`}
            className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-300 transition-colors"
          >
            <span>←</span>
            <span>{prev.name}</span>
          </Link>
        ) : <span />}
        {next ? (
          <Link
            to={`/component/${next.slug}`}
            className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-300 transition-colors"
          >
            <span>{next.name}</span>
            <span>→</span>
          </Link>
        ) : <span />}
      </div>

      <CommentsSection page={`component-${comp.slug}`} accent={comp.accent} />
    </main>
  )
}
