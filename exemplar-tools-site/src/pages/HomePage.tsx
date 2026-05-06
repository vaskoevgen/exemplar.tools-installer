import { Link } from 'react-router-dom'
import { TOOLS } from '../data/tools'
import VideoEmbed from '../components/VideoEmbed'

const LOOP = `
[Constrain]  →  constraints.yaml, component_map.yaml
     ↓
  [Ledger]   →  schema registry, access classification
     ↓
   [Pact]    →  contract tests, code, access_graph.json
     ↓
[Advocate]   →  code review findings
     ↓
 [Arbiter]   →  trust scores, blast radius
     ↓
  [Baton]    →  circuit up → OTLP spans → Arbiter
     ↓
[Sentinel]   →  log watch → attribution → LLM fix
     ↓
[Chronicler] →  event stories → Stigmergy
     ↓
[Stigmergy]  →  signal mesh → patterns → Apprentice
     ↓
[Apprentice] →  frontier API → fine-tune local model
     ↓
 [Kindex]    →  persistent knowledge graph (cross-cutting)
`.trim()

export default function HomePage() {
  return (
    <main className="max-w-4xl mx-auto px-8 py-14">
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
          Eleven tools that take a software project from ambiguity to deployed, observable, and self-improving code —
          each step feeding the next.
        </p>
      </div>

      <section className="mb-14 animate-slide-up" style={{ animationDelay: '0.05s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4">How This Site Was Built</h2>
        <VideoEmbed url="https://www.youtube.com/embed/WXssoa-7Hxk" title="How this site was built" />
        <p className="text-slate-500 text-sm leading-relaxed mt-3">
          This documentation site was built end-to-end using the exemplar.tools suite —
          Constrain → Ledger → Pact → Advocate → Arbiter → Baton → Sentinel → Chronicler → Stigmergy → Apprentice → Kindex.
        </p>
      </section>

      <section className="mb-14 animate-slide-up" style={{ animationDelay: '0.1s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-6">The Closed Loop</h2>
        <pre className="font-mono text-sm text-slate-400 bg-[#12121a] border border-[#1e1e2e] rounded-xl p-6 overflow-x-auto leading-relaxed">
          {LOOP}
        </pre>
      </section>

      <section className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-6">Quick Start</h2>
        <div className="overflow-x-auto rounded-xl border border-[#1e1e2e]">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1e1e2e] bg-[#12121a]">
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider w-10">Step</th>
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider">Tool</th>
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider">What it does</th>
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider hidden md:table-cell">Install</th>
              </tr>
            </thead>
            <tbody>
              {TOOLS.map((tool) => (
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
                  <td className="px-4 py-3 font-mono text-xs text-slate-600 hidden md:table-cell">{tool.installCmd}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  )
}
