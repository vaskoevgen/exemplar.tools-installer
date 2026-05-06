import { useParams, Link } from 'react-router-dom'
import { TOOL_MAP, TOOLS } from '../data/tools'
import type { Note } from '../data/tools'
import VersionBadge from '../components/VersionBadge'
import VideoEmbed from '../components/VideoEmbed'
import CommentsSection from '../components/CommentsSection'

function NoteBox({ note }: { note: Note }) {
  const styles = {
    warning: { border: '#f59e0b44', bg: 'rgba(245,158,11,0.06)', label: '⚠ Warning', color: '#f59e0b' },
    bug: { border: '#ef444444', bg: 'rgba(239,68,68,0.06)', label: '🐛 Known Bug', color: '#ef4444' },
    info: { border: '#22d3ee44', bg: 'rgba(34,211,238,0.06)', label: 'ℹ Note', color: '#22d3ee' },
  }
  const s = styles[note.kind]
  return (
    <div className="rounded-lg border px-4 py-3 mb-3" style={{ borderColor: s.border, background: s.bg }}>
      <span className="font-mono text-xs font-semibold" style={{ color: s.color }}>{s.label}</span>
      <p className="text-slate-400 text-sm mt-1 leading-relaxed">{note.text}</p>
    </div>
  )
}

function SectionHeader({ title }: { title: string }) {
  return <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4 mt-10">{title}</h2>
}

function CodeBlock({ code }: { code: string }) {
  return (
    <pre className="font-mono text-sm bg-[#12121a] border border-[#1e1e2e] rounded-lg p-4 overflow-x-auto mb-4">
      <code className="text-slate-300">{code}</code>
    </pre>
  )
}

export default function ToolPage() {
  const { slug } = useParams<{ slug: string }>()
  const tool = slug ? TOOL_MAP[slug] : undefined

  if (!tool) {
    return (
      <main className="max-w-4xl mx-auto px-8 py-14">
        <p className="text-slate-500 font-mono">Tool not found.</p>
        <Link to="/" className="text-cyan-400 hover:text-cyan-300 text-sm mt-2 inline-block">← Overview</Link>
      </main>
    )
  }

  const toolIdx = TOOLS.findIndex((t) => t.slug === tool.slug)
  const prev = toolIdx > 0 ? TOOLS[toolIdx - 1] : null
  const next = toolIdx < TOOLS.length - 1 ? TOOLS[toolIdx + 1] : null

  return (
    <main className="max-w-4xl mx-auto px-8 py-14 animate-fade-in">

      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-4">
          <span className="font-mono text-xs px-2 py-0.5 rounded" style={{ background: tool.accentBg, color: tool.accent }}>
            Step {String(tool.step).padStart(2, '0')}
          </span>
          <VersionBadge version={tool.version} accent={tool.accent} />
          {tool.cost && (
            <span className="font-mono text-xs text-slate-600 border border-[#1e1e2e] px-2 py-0.5 rounded">
              {tool.cost}
            </span>
          )}
        </div>
        <h1 className="font-display text-5xl leading-tight mb-3" style={{ color: tool.accent }}>
          {tool.name}
        </h1>
        <p className="text-slate-400 text-lg leading-relaxed max-w-2xl">{tool.tagline}</p>
      </div>

      <div className="h-px mb-10" style={{ background: `linear-gradient(to right, ${tool.accent}33, transparent)` }} />

      {/* Description */}
      <section>
        <SectionHeader title="Overview" />
        <p className="text-slate-300 leading-relaxed">{tool.description}</p>
      </section>

      {/* Integration status */}
      {tool.integrationStatus && (
        <section>
          <SectionHeader title="Integration Status" />
          <div className="rounded-lg border border-[#1e1e2e] bg-[#12121a] px-4 py-3">
            <p className="text-slate-400 text-sm leading-relaxed">{tool.integrationStatus}</p>
          </div>
        </section>
      )}

      {/* Activate */}
      <section>
        <SectionHeader title="Activate" />
        <CodeBlock code={tool.activateCmd} />
      </section>

      {/* Quick Start */}
      <section>
        <SectionHeader title="Quick Start" />
        <CodeBlock code={tool.quickStart.join('\n')} />
      </section>

      {/* Output files */}
      {tool.outputFiles && tool.outputFiles.length > 0 && (
        <section>
          <SectionHeader title="Output Files" />
          <div className="rounded-xl border border-[#1e1e2e] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e1e2e] bg-[#12121a]">
                  <th className="text-left px-4 py-2.5 font-mono text-xs text-slate-500 uppercase tracking-wider">File</th>
                  <th className="text-left px-4 py-2.5 font-mono text-xs text-slate-500 uppercase tracking-wider">Consumed by</th>
                </tr>
              </thead>
              <tbody>
                {tool.outputFiles.map((f) => (
                  <tr key={f.file} className="border-b border-[#1e1e2e] last:border-0">
                    <td className="px-4 py-2.5 font-mono text-xs text-cyan-400">{f.file}</td>
                    <td className="px-4 py-2.5 text-slate-400 text-xs">{f.consumedBy}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Personas (Advocate) */}
      {tool.personas && tool.personas.length > 0 && (
        <section>
          <SectionHeader title="The Six Personas" />
          <div className="rounded-xl border border-[#1e1e2e] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e1e2e] bg-[#12121a]">
                  <th className="text-left px-4 py-2.5 font-mono text-xs text-slate-500 uppercase tracking-wider">Persona</th>
                  <th className="text-left px-4 py-2.5 font-mono text-xs text-slate-500 uppercase tracking-wider">Angle</th>
                </tr>
              </thead>
              <tbody>
                {tool.personas.map((p) => (
                  <tr key={p.name} className="border-b border-[#1e1e2e] last:border-0">
                    <td className="px-4 py-2.5 font-semibold text-slate-200">{p.name}</td>
                    <td className="px-4 py-2.5 text-slate-400">{p.angle}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Phases (Apprentice) */}
      {tool.phases && tool.phases.length > 0 && (
        <section>
          <SectionHeader title="Three Phases — All Automatic" />
          <div className="rounded-xl border border-[#1e1e2e] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e1e2e] bg-[#12121a]">
                  <th className="text-left px-4 py-2.5 font-mono text-xs text-slate-500 uppercase tracking-wider">Phase</th>
                  <th className="text-left px-4 py-2.5 font-mono text-xs text-slate-500 uppercase tracking-wider">What happens</th>
                </tr>
              </thead>
              <tbody>
                {tool.phases.map((p) => (
                  <tr key={p.phase} className="border-b border-[#1e1e2e] last:border-0">
                    <td className="px-4 py-2.5 font-semibold text-slate-200 whitespace-nowrap">{p.phase}</td>
                    <td className="px-4 py-2.5 text-slate-400">{p.what}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Key Concepts */}
      {tool.keyConcepts && tool.keyConcepts.length > 0 && (
        <section>
          <SectionHeader title="Key Concepts" />
          <div className="rounded-xl border border-[#1e1e2e] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e1e2e] bg-[#12121a]">
                  <th className="text-left px-4 py-2.5 font-mono text-xs text-slate-500 uppercase tracking-wider">Concept</th>
                  <th className="text-left px-4 py-2.5 font-mono text-xs text-slate-500 uppercase tracking-wider">Meaning</th>
                </tr>
              </thead>
              <tbody>
                {tool.keyConcepts.map((c) => (
                  <tr key={c.concept} className="border-b border-[#1e1e2e] last:border-0">
                    <td className="px-4 py-2.5 font-mono text-xs text-cyan-400 whitespace-nowrap">{c.concept}</td>
                    <td className="px-4 py-2.5 text-slate-400">{c.meaning}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Notes, bugs, warnings */}
      {tool.notes && tool.notes.length > 0 && (
        <section>
          <SectionHeader title="Gotchas & Notes" />
          {tool.notes.map((n, i) => <NoteBox key={i} note={n} />)}
        </section>
      )}

      {/* Video */}
      {tool.videoUrl && (
        <section>
          <SectionHeader title="Video Walkthrough" />
          <VideoEmbed url={tool.videoUrl} title={`${tool.name} walkthrough`} />
        </section>
      )}

      {/* Prev / Next */}
      <nav className="flex items-center justify-between pt-10 border-t border-[#1e1e2e] mt-10">
        {prev ? (
          <Link to={`/tool/${prev.slug}`} className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors group">
            <span className="group-hover:-translate-x-1 transition-transform">←</span>
            <span>
              <span className="font-mono text-xs text-slate-600 block">Previous</span>
              {prev.name}
            </span>
          </Link>
        ) : <span />}
        {next ? (
          <Link to={`/tool/${next.slug}`} className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors group text-right">
            <span>
              <span className="font-mono text-xs text-slate-600 block">Next</span>
              {next.name}
            </span>
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </Link>
        ) : <span />}
      </nav>

      <CommentsSection page={tool.slug} accent={tool.accent} />
    </main>
  )
}
