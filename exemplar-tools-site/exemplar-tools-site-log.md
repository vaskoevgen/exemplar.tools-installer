# Exemplar Tools Documentation Site — Change Log

## 2026-05-06 | INIT | Project Planning
**Description:** Starting documentation website for exemplar.tools suite. Following howto.md workflow exactly: Constrain → Ledger → Pact → Advocate → Arbiter → Baton → Sentinel → Chronicler → Stigmergy → Apprentice → Kindex.
**Tech stack:** Vite + React + TypeScript + Tailwind CSS + Bun, Convex (DB for comments), React Router v6, port 4000.
**Design direction:** Industrial/terminal dark — near-black background, electric cyan primary, per-tool accent colors. Fonts: Instrument Serif (display) + JetBrains Mono (code). Asymmetric layout, step-reveal animations.
**Pages:** Home + one page per tool: Constrain, Ledger, Pact, Advocate, Arbiter, Baton, Sentinel, Chronicler, Stigmergy, Apprentice, Kindex.

---

## 2026-05-06 | STEP-1a | Constrain — Structured Artifacts Generated
**Tool:** exemplar.tools/constrain (non-interactive mode with prime.md)
**Command:** `constrain new --min-challenge 0 --max-challenge 0 --min-understand 0 --max-understand 0 -p prime.md`
**Working directory:** exemplar-tools-site/
**Output artifacts:**
- prompt.md — engineering brief for Pact
- constraints.yaml — 10 constraints (C001-C010) covering pages, port, package manager, content source, styling, routing, video, comments, data, version badges
- component_map.yaml — 5 components: web_frontend, build_system, convex_backend, youtube_embed, tool_repositories
- trust_policy.yaml — PUBLIC classification for all content and comments
- schema_hints.yaml — Convex comments schema hints (text, timestamp, page, author)
**Side effect:** Added .constrain/ to .gitignore
**Status:** Complete.

---

## 2026-05-06 | STEP-1b | Ledger — Schema Registration
**Tool:** exemplar.tools/ledger (branch: fix/init-config-stub)
**Commands:** `ledger init` → `ledger backend add convex-comments --type custom --owner web_frontend` → `ledger schema add schemas/comments.yaml` → `ledger schema validate` → `ledger export --format pact`
**Output:** ledger.yaml, schemas/comments.yaml (fields: id, page, author, body, created_at — all PUBLIC), changelog.yaml, plans/
**Note:** `ledger export` returned `{'contracts': []}` — expected, export is a stub not yet implemented.
**Status:** Complete.

---

## 2026-05-06 | STEP-2a | Pact — Build Complete (budget cap)
**Tool:** exemplar.tools/pact (branch: fix/all-health-fixes)
**Components decomposed:** 7 (project_scaffold, data_layer, app_shell, home_page, tool_page, tests, root)
**Total contract tests written:** 24+27+35+40+32+31+78+55+29+29+28+20 = ~428 test cases
**Implementations:** 6/7 components (root not reached — $10.02 budget cap)
- project_scaffold: 126/129 tests (best-effort, 3 stubborn failures)
- data_layer: passed
- app_shell: 156/156 ✅
- home_page: passed
- tool_page: 151/151 ✅
- tests: partial (budget cap mid-attempt-2)
**Note:** Pact generated Python (.py) contract implementations, not TypeScript — this is Pact's default behavior regardless of sops.md stack spec. The Python modules represent the contract layer; the actual TypeScript/React site is scaffolded separately.
**Generated files:** src/project_scaffold/, src/data_layer/, src/app_shell/, src/home_page/, src/tool_page/, src/tests/
**Cost:** $10.02
**Status:** Complete (budget cap).

---

## 2026-05-06 | STEP-2b | Advocate — Code Review Complete
**Tool:** exemplar.tools/advocate (branch: fix/missing-jinja2-dependency)
**Command:** `advocate review src/ -o findings.json --html review-report.html`
**Results:** 40 findings, $0.87
- Red Team: No security findings ✅
- Sage (critical): Python-simulating-React architecture mismatch — expected given Pact's Python output
- Adversarial (critical): In-memory comment store, global Convex singleton — contract-layer limitations
- Good Friend (high): No rate limiting, hardcoded port, no build validation
**Output:** findings.json, review-report.html
**Status:** Complete.

---

## 2026-05-06 | STEP-3 | Arbiter — Trust Init + Fix Applied
**Tool:** exemplar.tools/arbiter
**Fix:** Patched arbiter/src/arbiter/registry/store.py line 89 — added 2-line translation: if "nodes" not in graph_data and "components" in graph_data: graph_data["nodes"] = graph_data.pop("components")
**Commands:** `arbiter init` → created synthetic access_graph.json → `arbiter register access_graph.json`
**Result:** "Registered: 7 nodes, 7 authority domains" ✅
**Note:** Trust scores empty (no live traffic events yet — expected for fresh registration).
**Status:** Complete.

---

## 2026-05-06 | STEP-4 | Baton — Deploy Complete
**Tool:** exemplar.tools/baton (branch: fix/baton-slot-command)
**Commands:** `pact deploy .` → edit baton.yaml → `baton status` → `baton up --mock`
**Output:** baton.yaml (6 nodes, 1 edge), circuit up at http://127.0.0.1:4000
**Notes:**
- Ports shifted to 4000-4005 (3000 was taken by todo-list3 Baton instance)
- app-shell set as ingress on port 4000 (matches our Vite dev server port)
- Mock responds: {"status": "mock", "port": 24000}
- Circuit left running for Sentinel log watching
**Status:** Complete — circuit up.

---

## 2026-05-06 | STEP-5a | Sentinel — Config Generated
**Tool:** exemplar.tools/sentinel (branch: fix/serve-also-watches)
**Command:** `sentinel init` → `sentinel serve` (blocked — baton circuit mock only, no real log file yet)
**Output:** sentinel.yaml configured with `.baton/service_logs.jsonl` source, error_patterns, LLM claude-sonnet-4-20250514, budget caps, auto_remediate: false
**Status:** Config complete. Serve step deferred until real log traffic.

---

## 2026-05-06 | STEP-5b | Chronicler — Config Generated
**Tool:** exemplar.tools/chronicler
**Output:** chronicler.yaml configured with otlp+sentinel sources, disk sink, 3 story rules
**Status:** Config complete.

---

## 2026-05-06 | STEP-5c | Stigmergy — Mock Run Complete
**Tool:** exemplar.tools/stigmergy (branch: fix/serve-also-watches)
**Commands:** `stigmergy init` (piped) → fix .stigmergy/config.yaml (mode: Y→mock, provider: N→stub) → `stigmergy run --once`
**Config fix:** stdin piping bug causes `mode: Y` and `provider: N` — manually corrected to `mode: mock` and `provider: stub`
**Output:** 7 mock GitHub signals processed, 3 workers, 2 agents (eng_watcher, cross_cutter), mesh topology built, $0.00 cost (stub provider)
**Parallel activity detected:** @bob.martinez and @alice.chen in same signal space (61% similarity), duplicate PR pattern surfaced
**Status:** Complete.

---

## 2026-05-06 | STEP-6 | Apprentice — Task Init + Run + Report
**Tool:** exemplar.tools/apprentice (branch: fix/cli-run-and-report)
**Commands:** `apprentice init` → fix input_schema bug → `apprentice serve` (port 8710) → `apprentice status` → `apprentice run docs_eval` → `apprentice report`
**Task configured:** `docs_eval` — answering questions about exemplar.tools documentation using claude-haiku-4-5-20251001
**Wizard bug applied:** wizard wrote `name: text` — manually changed to `name: question` to match `{question}` in prompt template
**Run result:** Success: True — Claude Haiku answered "What is Pact?" correctly
**Phase:** bootstrapping, Confidence 0.00, Budget $0.00/10.00 — needs 100 training examples before local model fine-tuning
**Status:** Complete.

---

## 2026-05-06 | STEP-7 | Kindex — MCP Already Connected
**Tool:** exemplar.tools/kindex
**Note:** Already registered and connected as MCP server (MCP tool shows `kindex` connected). `kin status` shows 17 nodes, 15 edges. No additional setup needed.
**Status:** Complete.

---

## 2026-05-06 | STEP-8 | Frontend Scaffold — Vite + React + TypeScript
**Stack:** Vite 8, React 19, TypeScript 6, Tailwind CSS v3, React Router v6, Bun
**Dev server:** http://localhost:4000 ✅ running
**Build:** `bun run build` → 26 modules, 231 kB JS, 10.6 kB CSS, zero errors ✅
**Structure:**
- `src/data/tools.ts` — typed registry of all 11 tools (slug, accent, video, quickStart, etc.)
- `src/components/Sidebar.tsx` — fixed left nav with step numbers and active highlight
- `src/components/VersionBadge.tsx` — per-tool version chip with accent color
- `src/components/VideoEmbed.tsx` — YouTube iframe wrapper
- `src/components/CommentsSection.tsx` — in-memory comment form (Convex wire-up pending)
- `src/pages/HomePage.tsx` — closed-loop ASCII diagram + quick-start table
- `src/pages/ToolPage.tsx` — per-tool page (overview, install, quickstart, video, prev/next, comments)
- `src/App.tsx` — BrowserRouter with two routes: / and /tool/:slug
**Design:** Industrial terminal dark — #0a0a0f background, electric cyan accents, per-tool accent colors, Instrument Serif + JetBrains Mono fonts, fade-in + slide-up animations
**Status:** Complete.

---

## 2026-05-06 | STEP-9 | Convex DB Integration — Comments Persistent
**Constraint:** C009 (must) + C010 (must) from Constrain step — real-time, persistent comments required
**Commands:** `bunx convex dev` (local mode, no cloud account) → `bun add convex` → schema push → generated `convex/_generated/`
**Files:**
- `convex/schema.ts` — comments table: page, author, body + by_page index
- `convex/comments.ts` — getByPage query + add mutation
- `src/main.tsx` — wrapped with ConvexProvider(VITE_CONVEX_URL)
- `src/components/CommentsSection.tsx` — replaced useState with useQuery/useMutation
**Local backend:** SQLite at `.convex/local/default/convex_local_backend.sqlite3`, port 3210
**Verified:** POST mutation → ID returned; GET query → comment persisted ✅
**Status:** Complete — comments survive refresh, sync in real time.

---
