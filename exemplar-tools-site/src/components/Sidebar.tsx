import { NavLink } from 'react-router-dom'
import { TOOLS } from '../data/tools'
import { COMPONENT_LIST } from '../pages/ComponentPage'

const COMPONENT_ACCENT: Record<string, string> = {
  frontend: '#22d3ee',
  backend: '#a78bfa',
  database: '#34d399',
  ui: '#f472b6',
}

export default function Sidebar() {
  return (
    <aside className="fixed top-0 left-0 h-screen w-56 bg-[#0d0d14] border-r border-[#1e1e2e] flex flex-col z-40">
      <div className="p-5 border-b border-[#1e1e2e]">
        <NavLink to="/" className="block">
          <span className="font-mono text-xs text-slate-500 tracking-widest uppercase">exemplar</span>
          <h1 className="font-display text-xl text-white leading-tight mt-0.5">.tools</h1>
        </NavLink>
      </div>
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-1">

        {/* Top-level nav */}
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
              isActive ? 'bg-[#1a1a2e] text-white' : 'text-slate-500 hover:text-slate-300 hover:bg-[#14141f]'
            }`
          }
        >
          <span className="font-mono text-xs text-slate-600 w-5">00</span>
          <span>Overview</span>
        </NavLink>
        <NavLink
          to="/getting-started"
          className={({ isActive }) =>
            `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
              isActive ? 'bg-[#1a1a2e] text-white' : 'text-slate-500 hover:text-slate-300 hover:bg-[#14141f]'
            }`
          }
        >
          <span className="font-mono text-xs text-slate-600 w-5">→</span>
          <span>Getting Started</span>
        </NavLink>

        {/* Components section */}
        <div className="pt-3 pb-1 px-3">
          <span className="font-mono text-xs tracking-widest text-slate-700 uppercase">Components</span>
        </div>
        <div className="space-y-0.5">
          {COMPONENT_LIST.map((comp) => (
            <NavLink
              key={comp.slug}
              to={`/component/${comp.slug}`}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive ? 'bg-[#1a1a2e] text-white' : 'text-slate-500 hover:text-slate-300 hover:bg-[#14141f]'
                }`
              }
            >
              <span
                className="font-mono text-xs w-5 shrink-0"
                style={{ color: COMPONENT_ACCENT[comp.slug] }}
              >
                ⬡
              </span>
              <span>{comp.name}</span>
            </NavLink>
          ))}
        </div>

        {/* Tools section */}
        <div className="pt-3 pb-1 px-3">
          <span className="font-mono text-xs tracking-widest text-slate-700 uppercase">Tools</span>
        </div>
        <div className="space-y-0.5">
          {TOOLS.map((tool) => (
            <NavLink
              key={tool.slug}
              to={`/tool/${tool.slug}`}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive ? 'bg-[#1a1a2e] text-white' : 'text-slate-500 hover:text-slate-300 hover:bg-[#14141f]'
                }`
              }
            >
              <span className="font-mono text-xs text-slate-600 w-5 shrink-0">{String(tool.step).padStart(2, '0')}</span>
              <span>{tool.name}</span>
            </NavLink>
          ))}
        </div>

      </nav>
      <div className="p-4 border-t border-[#1e1e2e] space-y-2">
        <a
          href="https://github.com/vaskoevgen/exemplar.tools-installer"
          target="_blank"
          rel="noopener noreferrer"
          className="block font-mono text-xs text-cyan-600 hover:text-cyan-400 transition-colors"
        >
          source repo ↗
        </a>
        <a
          href="https://github.com/jmcentire"
          target="_blank"
          rel="noopener noreferrer"
          className="block font-mono text-xs text-slate-600 hover:text-slate-400 transition-colors"
        >
          github.com/jmcentire
        </a>
      </div>
    </aside>
  )
}
