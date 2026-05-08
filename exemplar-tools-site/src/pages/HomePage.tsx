import { Link } from 'react-router-dom'
import { TOOLS } from '../data/tools'
import VideoEmbed from '../components/VideoEmbed'
import { COMPONENT_LIST } from './ComponentPage'

const LOOP = `
[Cartographer] ← optional: existing codebases only
      ↓
[Constrain]  →  prompt.md, constraints.yaml, component_map.yaml,
                trust_policy.yaml, schema_hints.yaml
      ↓                              ↓
  [Ledger]                     [Arbiter init]
  (schemas)                    arbiter watch (sidecar, port 7700)
      ↓                              ↓
    export obligations    ┌──────────────────────┐
      ↓                   │                      │
   [Pact]  →  src/, tests/, access_graph.json  →  [Arbiter register]
      ↓                                               ↓
  [Advocate]                                trust scores, blast radius
  (code review gate)
      ↓
  [Baton]  →  circuit up → OTLP spans → Arbiter
      ↓
[Sentinel]  →  incidents, contract tightening
      ↓                      ↓
[Chronicler]  →  stories (request / service / journey)
      ↓                      ↓
[Stigmergy]           [Apprentice]
(org patterns)     (model distillation)

[Kindex]  ←  cross-cutting knowledge layer (all tools feed into it)`.trim()

const MINIMUM_PATH = [
  { step: 1, name: 'Constrain', slug: 'constrain', accent: '#f59e0b', desc: 'Describe what to build → structured artifacts' },
  { step: 3, name: 'Pact', slug: 'pact', accent: '#3b82f6', desc: 'Build the code → contracts, tests, implementation' },
  { step: 6, name: 'Baton', slug: 'baton', accent: '#10b981', desc: 'Deploy it → running circuit of services' },
]

const OPTIONAL_TOOLS = [
  { name: 'Ledger', slug: 'ledger', accent: '#10b981', desc: 'Schema obligations — skip if no database' },
  { name: 'Advocate', slug: 'advocate', accent: '#8b5cf6', desc: 'Code review gate before deploy' },
  { name: 'Arbiter', slug: 'arbiter', accent: '#ef4444', desc: 'Trust scoring — integration in progress' },
  { name: 'Sentinel', slug: 'sentinel', accent: '#f97316', desc: 'Production log watching' },
  { name: 'Chronicler', slug: 'chronicler', accent: '#ec4899', desc: 'Event story collection' },
  { name: 'Stigmergy', slug: 'stigmergy', accent: '#06b6d4', desc: 'Org signal patterns' },
  { name: 'Apprentice', slug: 'apprentice', accent: '#84cc16', desc: 'Local model distillation' },
  { name: 'Kindex', slug: 'kindex', accent: '#14b8a6', desc: 'Cross-cutting knowledge graph (MCP)' },
]

export default function HomePage() {
  return (
    <main className="max-w-4xl mx-auto px-8 py-14">

      {/* Hero */}
      <div className="mb-12 animate-fade-in">
        <a
          href="https://exemplar.tools/"
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono text-xs tracking-widest text-cyan-500 uppercase mb-3 hover:text-cyan-400 transition-colors inline-block"
        >
          exemplar.tools ↗
        </a>
        <h1 className="font-display text-5xl text-white leading-tight mb-4">
          The closed-loop AI engineering platform
        </h1>
        <p className="text-slate-400 text-lg leading-relaxed max-w-2xl">
          Eleven tools that take a software project from ambiguity to deployed, observable, and
          self-improving code — each step feeding the next.
        </p>
        <div className="flex gap-3 mt-6">
          <Link
            to="/getting-started"
            className="px-4 py-2 rounded-lg text-sm font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 transition-all"
          >
            Get started →
          </Link>
          <a
            href="https://github.com/vaskoevgen/exemplar.tools-installer"
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 rounded-lg text-sm font-semibold bg-[#1a1a2e] text-slate-400 border border-[#1e1e2e] hover:text-slate-200 transition-all"
          >
            Source repo ↗
          </a>
        </div>
      </div>

      {/* How this site was built */}
      <section className="mb-14 animate-slide-up" style={{ animationDelay: '0.05s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4">How This Site Was Built</h2>
        <VideoEmbed url="https://www.youtube.com/embed/WXssoa-7Hxk" title="How this site was built" />
        <p className="text-slate-500 text-sm leading-relaxed mt-3">
          This documentation site was built end-to-end using the exemplar.tools suite —
          Constrain → Ledger → Pact → Advocate → Arbiter → Baton → Sentinel → Chronicler → Stigmergy → Apprentice → Kindex.
        </p>
      </section>

      {/* Minimum path */}
      <section className="mb-14 animate-slide-up" style={{ animationDelay: '0.08s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-2">Minimum Path to Ship</h2>
        <p className="text-slate-500 text-sm mb-6">
          Three steps take you from idea to deployed code. Everything else adds governance and observability on top.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          {MINIMUM_PATH.map((t, i) => (
            <Link
              key={t.slug}
              to={`/tool/${t.slug}`}
              className="flex-1 rounded-xl border px-4 py-4 hover:opacity-90 transition-opacity"
              style={{ borderColor: t.accent + '33', background: t.accent + '0a' }}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="font-mono text-xs px-1.5 py-0.5 rounded" style={{ background: t.accent + '22', color: t.accent }}>
                  Step {i + 1}
                </span>
              </div>
              <div className="font-semibold mb-1" style={{ color: t.accent }}>{t.name}</div>
              <p className="text-slate-500 text-xs leading-relaxed">{t.desc}</p>
            </Link>
          ))}
        </div>
        <div className="mt-4 rounded-lg border border-[#1e1e2e] bg-[#12121a] px-4 py-3">
          <p className="text-slate-500 text-xs font-mono">
            Optional governance + observability: {OPTIONAL_TOOLS.map((t, i) => (
              <span key={t.slug}>
                <Link to={`/tool/${t.slug}`} className="hover:opacity-80 transition-opacity" style={{ color: t.accent }}>{t.name}</Link>
                {i < OPTIONAL_TOOLS.length - 1 ? <span className="text-slate-700"> · </span> : null}
              </span>
            ))}
          </p>
        </div>
      </section>

      {/* Site Architecture — Components */}
      <section className="mb-14 animate-slide-up" style={{ animationDelay: '0.12s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-2">Site Architecture</h2>
        <p className="text-slate-500 text-sm mb-6">
          This site is built from four separate components — each has its own documentation page.
        </p>
        <div className="grid grid-cols-2 gap-3">
          {COMPONENT_LIST.map((comp) => (
            <Link
              key={comp.slug}
              to={`/component/${comp.slug}`}
              className="rounded-xl border px-4 py-4 hover:opacity-90 transition-opacity"
              style={{ borderColor: comp.accent + '33', background: comp.accent + '0a' }}
            >
              <div className="font-semibold mb-1" style={{ color: comp.accent }}>{comp.name}</div>
              <p className="text-slate-500 text-xs leading-relaxed">{comp.tagline}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Closed loop */}
      <section className="mb-14 animate-slide-up" style={{ animationDelay: '0.15s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-6">The Closed Loop</h2>
        <pre className="font-mono text-sm text-slate-400 bg-[#12121a] border border-[#1e1e2e] rounded-xl p-6 overflow-x-auto leading-relaxed">
          {LOOP}
        </pre>
        <p className="text-slate-600 text-xs mt-3 font-mono">
          Feedback loops: Sentinel → Constrain (bugs tighten contracts) · Chronicler → Apprentice (traffic trains local models)
        </p>
      </section>

      {/* All tools table */}
      <section className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-6">All Tools</h2>
        <div className="overflow-x-auto rounded-xl border border-[#1e1e2e]">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1e1e2e] bg-[#12121a]">
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider w-10">Step</th>
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider">Tool</th>
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider">What it does</th>
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider w-16">Required</th>
              </tr>
            </thead>
            <tbody>
              {TOOLS.map((tool) => {
                const isRequired = tool.step <= 3 || tool.slug === 'baton'
                return (
                  <tr
                    key={tool.slug}
                    className="border-b border-[#1e1e2e] last:border-0 hover:bg-[#14141f] transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs text-slate-600">{String(tool.step).padStart(2, '0')}</td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/tool/${tool.slug}`}
                        className="font-semibold hover:opacity-80 transition-opacity"
                        style={{ color: tool.accent }}
                      >
                        {tool.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{tool.tagline}</td>
                    <td className="px-4 py-3">
                      {isRequired ? (
                        <span className="font-mono text-xs text-emerald-500">must</span>
                      ) : (
                        <span className="font-mono text-xs text-slate-700">optional</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>

    </main>
  )
}
