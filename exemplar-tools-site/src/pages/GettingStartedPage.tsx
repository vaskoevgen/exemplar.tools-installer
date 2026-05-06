import VideoEmbed from '../components/VideoEmbed'

const SESSIONS = [
  { step: '1a — Constrain',       log: '1a-Constrain.md',          video: 'https://youtu.be/wkQeCPhlQD0' },
  { step: '1b — Ledger',          log: '1b — Ledger.md',            video: 'https://youtu.be/yZn64yO87VM' },
  { step: '2a — Pact (DB setup)', log: '2a-Pact install db.md',     video: 'https://youtu.be/S6FEOl9cJuk' },
  { step: '2a — Pact',            log: '2a-Pact.md',                video: 'https://youtu.be/vwHyrU13Cds' },
  { step: '2b — Advocate',        log: '2b-Advocate.md',            video: 'https://youtu.be/sKOM3NvW7lY' },
  { step: '3 — Arbiter',          log: '3-Arbiter.md',              video: 'https://youtu.be/4f5uqWGs2ws' },
  { step: '4 — Baton',            log: '4-Baton.md',                video: 'https://youtu.be/XGu3XTfvG1c' },
  { step: '4 — Baton test run',   log: '4-Baton-test-run.md',       video: 'https://youtu.be/nPcB7BjvWoo' },
  { step: '5a — Sentinel',        log: '5a-Sentinel.md',            video: 'https://youtu.be/k8RVrSnEw6I' },
  { step: '5b — Chronicler',      log: '5b-Chronicler.md',          video: 'https://youtu.be/a94Kpf0bYVg' },
  { step: '5c — Stigmergy',       log: '5c-Stigmergy.md',           video: 'https://youtu.be/4z7--TKIvQ4' },
  { step: '6 — Apprentice',       log: '6-Apprentice.md',           video: 'https://youtu.be/BhltpaigLTo' },
]

const INSTALL = `curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash`

const LAYOUT = `parent/
├── your-project/        ← your working directory throughout this guide
└── exemplar.tools/      ← cloned by the installer (run from parent/)
    ├── constrain/
    ├── pact/
    ├── baton/
    ├── sentinel/
    └── kindex/`

export default function GettingStartedPage() {
  return (
    <main className="max-w-4xl mx-auto px-8 py-14">
      <div className="mb-10 animate-fade-in">
        <p className="font-mono text-xs tracking-widest text-cyan-500 uppercase mb-3">getting started</p>
        <h1 className="font-display text-4xl text-white leading-tight mb-4">How to use exemplar.tools</h1>
        <div className="flex flex-wrap gap-4 text-sm">
          <a
            href="https://github.com/vaskoevgen/exemplar.tools-installer"
            target="_blank"
            rel="noopener noreferrer"
            className="font-mono text-cyan-500 hover:text-cyan-400 transition-colors"
          >
            ⌥ Source repository ↗
          </a>
          <a
            href="https://youtu.be/WXssoa-7Hxk"
            target="_blank"
            rel="noopener noreferrer"
            className="font-mono text-slate-400 hover:text-slate-300 transition-colors"
          >
            🎬 Watch how this site was built ↗
          </a>
        </div>
      </div>

      {/* Quick start */}
      <section className="mb-12 animate-slide-up" style={{ animationDelay: '0.05s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4">Quick start — minimum path to a working app</h2>
        <p className="text-slate-400 text-sm mb-5">Three steps take you from idea to deployed, tested code:</p>
        <div className="overflow-x-auto rounded-xl border border-[#1e1e2e]">
          <table className="w-full text-sm">
            <tbody>
              {[
                { step: 'Step 1 — Constrain', desc: 'describe what to build → structured artifacts' },
                { step: 'Step 2a — Pact',     desc: 'build the code → contracts, tests, implementation' },
                { step: 'Step 4 — Baton',     desc: 'deploy it → running circuit of services' },
              ].map((r) => (
                <tr key={r.step} className="border-b border-[#1e1e2e] last:border-0">
                  <td className="px-4 py-3 font-mono text-sm text-cyan-400 whitespace-nowrap">{r.step}</td>
                  <td className="px-4 py-3 text-slate-400">{r.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-slate-500 text-sm mt-4">
          Everything else (Ledger, Advocate, Arbiter, Sentinel, Kindex) adds governance, quality, and observability on top.
          You don't need them to ship.
        </p>
        <p className="text-slate-500 text-sm mt-2">
          See it in action:{' '}
          <a
            href="https://github.com/vaskoevgen/exemplar.tools-installer/blob/main/todo-list2/README.md"
            target="_blank"
            rel="noopener noreferrer"
            className="text-cyan-500 hover:text-cyan-400 transition-colors font-mono"
          >
            todo-list2/README.md ↗
          </a>
          {' '}— a complete walkthrough with real terminal output, costs, and gotchas (~$2.79 total).
        </p>
      </section>

      {/* Prerequisites */}
      <section className="mb-12 animate-slide-up" style={{ animationDelay: '0.1s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4">Prerequisites</h2>
        <ul className="space-y-2 text-sm text-slate-400">
          <li><span className="font-mono text-slate-300">Python 3.11+</span> — required by all tools</li>
          <li><span className="font-mono text-slate-300">Git</span> — for the installer</li>
          <li><span className="font-mono text-slate-300">curl</span> — for the installer</li>
          <li><span className="font-mono text-slate-300">Anthropic API key</span> — with access to claude-opus-4-6</li>
        </ul>
      </section>

      {/* Directory layout */}
      <section className="mb-12 animate-slide-up" style={{ animationDelay: '0.12s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4">Directory layout</h2>
        <p className="text-slate-400 text-sm mb-3">
          The installer creates <span className="font-mono text-slate-300">exemplar.tools/</span> as a sibling to your project folder:
        </p>
        <pre className="font-mono text-sm text-slate-400 bg-[#12121a] border border-[#1e1e2e] rounded-xl p-5 overflow-x-auto leading-relaxed">
          {LAYOUT}
        </pre>
      </section>

      {/* Install */}
      <section className="mb-12 animate-slide-up" style={{ animationDelay: '0.15s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4">Install</h2>
        <p className="text-slate-400 text-sm mb-3">
          Run once from the <strong className="text-slate-300">parent directory</strong> to clone all repositories and set up dependencies:
        </p>
        <pre className="font-mono text-sm text-slate-400 bg-[#12121a] border border-[#1e1e2e] rounded-xl p-5 overflow-x-auto">
          {INSTALL}
        </pre>
        <p className="text-slate-500 text-sm mt-3">
          Then enter your project folder — all commands are run from there:
        </p>
        <pre className="font-mono text-sm text-slate-400 bg-[#12121a] border border-[#1e1e2e] rounded-xl p-4 mt-2 overflow-x-auto">
          cd your-project
        </pre>
      </section>

      {/* Session logs */}
      <section className="mb-12 animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4">Session logs & videos</h2>
        <p className="text-slate-400 text-sm mb-4">
          Raw terminal logs and video recordings for each step of the todo-list2 example:
        </p>
        <div className="overflow-x-auto rounded-xl border border-[#1e1e2e]">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1e1e2e] bg-[#12121a]">
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider">Step</th>
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider">Terminal log</th>
                <th className="text-left px-4 py-3 font-mono text-xs text-slate-500 uppercase tracking-wider">Video</th>
              </tr>
            </thead>
            <tbody>
              {SESSIONS.map((s) => (
                <tr key={s.step} className="border-b border-[#1e1e2e] last:border-0 hover:bg-[#14141f] transition-colors">
                  <td className="px-4 py-3 text-slate-300 whitespace-nowrap">{s.step}</td>
                  <td className="px-4 py-3">
                    <a
                      href={`https://github.com/vaskoevgen/exemplar.tools-installer/blob/main/todo-list2/terminal-logs/${s.log}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-mono text-xs text-slate-400 hover:text-cyan-400 transition-colors"
                    >
                      {s.log} ↗
                    </a>
                  </td>
                  <td className="px-4 py-3">
                    <a
                      href={s.video}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-mono text-xs text-slate-400 hover:text-cyan-400 transition-colors"
                    >
                      {s.video.replace('https://youtu.be/', 'youtu.be/')} ↗
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Build video */}
      <section className="animate-slide-up" style={{ animationDelay: '0.25s' }}>
        <h2 className="font-mono text-xs tracking-widest text-slate-500 uppercase mb-4">How this site was built</h2>
        <VideoEmbed url="https://www.youtube.com/embed/WXssoa-7Hxk" title="How this site was built using exemplar.tools" />
        <p className="text-slate-500 text-sm mt-3">
          This documentation site was built end-to-end using the full exemplar.tools suite —
          Constrain → Ledger → Pact → Advocate → Arbiter → Baton → Sentinel → Chronicler → Stigmergy → Apprentice → Kindex.
        </p>
      </section>
    </main>
  )
}
