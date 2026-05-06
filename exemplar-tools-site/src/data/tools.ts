export interface Persona {
  name: string
  angle: string
}

export interface Phase {
  phase: string
  what: string
}

export interface KeyConcept {
  concept: string
  meaning: string
}

export interface Note {
  kind: 'warning' | 'info' | 'bug'
  text: string
}

export interface Tool {
  slug: string
  name: string
  step: number
  tagline: string
  accent: string
  accentBg: string
  videoUrl?: string
  version: string
  description: string
  activateCmd: string
  installCmd: string
  quickStart: string[]
  outputFiles?: { file: string; consumedBy: string }[]
  notes?: Note[]
  personas?: Persona[]
  phases?: Phase[]
  keyConcepts?: KeyConcept[]
  integrationStatus?: string
  cost?: string
}

export const TOOLS: Tool[] = [
  {
    slug: 'constrain',
    name: 'Constrain',
    step: 1,
    tagline: 'Structured AI interview that turns ambiguity into verifiable artifacts',
    accent: '#f59e0b',
    accentBg: 'rgba(245,158,11,0.08)',
    videoUrl: 'https://www.youtube.com/embed/wkQeCPhlQD0',
    version: '0.1.0',
    description:
      'Constrain runs an interactive AI interview about your problem. It asks clarifying questions and resolves ambiguities before producing structured artifacts. Expect 5–15 minutes of back-and-forth. Answer the questions directly — Constrain will stop when it has enough to proceed.',
    activateCmd:
      '# bash / zsh\nsource ../exemplar.tools/constrain/.venv/bin/activate\n\n# fish\nsource ../exemplar.tools/constrain/.venv/bin/activate.fish',
    installCmd: 'source ../exemplar.tools/constrain/.venv/bin/activate',
    quickStart: [
      '# Interactive interview (recommended)',
      'constrain',
      '',
      '# Non-interactive — skip the interview with a prime document',
      'constrain new --min-challenge 0 --max-challenge 0 --min-understand 0 --max-understand 0 -p prime.md',
      '',
      'deactivate',
    ],
    outputFiles: [
      { file: 'prompt.md', consumedBy: 'Pact — system briefing' },
      { file: 'constraints.yaml', consumedBy: 'Pact, Sentinel' },
      { file: 'component_map.yaml', consumedBy: 'Pact, Baton' },
      { file: 'trust_policy.yaml', consumedBy: 'Arbiter' },
      { file: 'schema_hints.yaml', consumedBy: 'Ledger' },
    ],
    notes: [
      {
        kind: 'info',
        text: 'On startup Constrain asks "Prime with documents before starting? [y/N]". Answer n for a fresh interactive session, or y to feed it a description file.',
      },
      {
        kind: 'info',
        text: 'Three phases run in order: understand (asks questions) → challenge (stress-tests answers) → synthesize (generates artifacts). You cannot skip phases.',
      },
      {
        kind: 'warning',
        text: 'Do not use {…} JSON examples in prime.md — curly braces crash the YAML generator. Describe shapes in plain English instead.',
      },
      {
        kind: 'info',
        text: 'A UserWarning about Field name "register" appears on every run. It is safe to ignore — it comes from an upstream dependency.',
      },
    ],
  },
  {
    slug: 'ledger',
    name: 'Ledger',
    step: 2,
    tagline: 'Schema registry with data-access classification and obligation export',
    accent: '#10b981',
    accentBg: 'rgba(16,185,129,0.08)',
    videoUrl: 'https://www.youtube.com/embed/yZn64yO87VM',
    version: '0.1.0',
    description:
      'Ledger registers your storage schemas and data rules, then exports obligations into Pact contracts, Arbiter, Baton, and Sentinel. Skip this step if your project has no database schemas.',
    activateCmd:
      '# bash / zsh\nsource ../exemplar.tools/ledger/.venv/bin/activate\n\n# fish\nsource ../exemplar.tools/ledger/.venv/bin/activate.fish',
    installCmd: 'source ../exemplar.tools/ledger/.venv/bin/activate',
    quickStart: [
      'ledger init',
      '# Creates: ledger.yaml, schemas/, plans/, changelog.yaml, .ledger/',
      '',
      'ledger backend add tasks-db --type postgres --owner fastapi-backend',
      '# Valid types: postgres, mysql, sqlite, redis, s3, dynamodb, kafka, custom',
      '',
      'ledger schema add schemas/tasks.yaml   # exits 0; no output on success',
      'ledger schema validate                 # exits 0; no output if valid',
      '',
      'ledger builtins list                   # explore annotation catalogue',
      'ledger builtins show immutable',
      '',
      'ledger export --format pact            # stub — returns empty contracts',
      '',
      'deactivate',
    ],
    integrationStatus:
      'ledger init, ledger backend add, and ledger builtins list/show are fully implemented. ledger schema add, ledger schema validate, and ledger export are stubs — they exit 0 but do nothing. Schema files are documentation only until the registry implementation ships.',
    notes: [
      {
        kind: 'bug',
        text: 'Three bugs fixed in branch vaskoevgen:fix/init-config-stub — use that branch until PR #2 merges into jmcentire/ledger.',
      },
      {
        kind: 'info',
        text: 'ledger export returns {\'contracts\': []} — this is expected. The export stub exits 0.',
      },
      {
        kind: 'warning',
        text: 'Valid classification values: PUBLIC, PII, FINANCIAL, AUTH, COMPLIANCE. Valid field_type follows SQL conventions: uuid, varchar(n), boolean, integer, timestamptz, etc. Use field_type key, not type.',
      },
    ],
  },
  {
    slug: 'pact',
    name: 'Pact',
    step: 3,
    tagline: 'Decomposes your task, writes contract tests, implements the code',
    accent: '#3b82f6',
    accentBg: 'rgba(59,130,246,0.08)',
    videoUrl: 'https://www.youtube.com/embed/vwHyrU13Cds',
    version: '0.1.0',
    description:
      'Pact builds the software using the artifacts produced by Constrain. It decomposes your task into components, writes contracts and tests, then implements each component via the Anthropic API. A typical run costs $1–3 and takes 10–30 minutes.',
    activateCmd:
      '# bash / zsh\nsource ../exemplar.tools/pact/.venv/bin/activate\n\n# fish\nsource ../exemplar.tools/pact/.venv/bin/activate.fish',
    installCmd: 'source ../exemplar.tools/pact/.venv/bin/activate',
    cost: '$1–3 per build, 10–30 minutes',
    quickStart: [
      '# 1. Initialize the project (run from your project root)',
      'pact init .',
      '# Creates task.md, pact.yaml, sops.md',
      '',
      '# 2. Edit pact.yaml — add required fields:',
      '# budget: 10.0',
      '# shaping: false',
      '# build_mode: auto',
      '# backend: anthropic',
      '# model: claude-opus-4-6',
      '# role_backends:',
      '#   decomposer: anthropic',
      '#   contract_author: anthropic',
      '#   test_author: anthropic',
      '#   code_author: anthropic',
      '',
      '# 3. Edit task.md (what to build) and sops.md (coding standards)',
      '',
      '# 4. Start the daemon',
      'pact daemon .',
      '',
      '# 5. Monitor in a second terminal',
      'pact status .        # current phase and cost',
      'pact log .           # full audit trail',
      '',
      '# 6. After interview phase — approve assumptions',
      'pact approve .',
      '',
      '# 7. If daemon pauses at health gate — resume',
      'pact resume .',
      '',
      '# 8. After build — run contract tests',
      'PYTHONPATH=src/<component> pytest tests/<component>/contract_test.py -q',
      '',
      '# 9. Generate baton.yaml for Step 4',
      'pact deploy .',
      '',
      'deactivate',
    ],
    notes: [
      {
        kind: 'warning',
        text: 'pact init . creates pact.yaml with only budget: 10.0. You must add role_backends and other fields before running the daemon. Without role_backends, Pact defaults to claude_code which requires Claude Code CLI.',
      },
      {
        kind: 'warning',
        text: 'sops.md default says "Language: Python 3.12+". If your app is NOT Python, update sops.md before running the daemon — Pact generates whatever language sops.md specifies.',
      },
      {
        kind: 'bug',
        text: 'Health gate fires spuriously 3–5 times per build due to known bugs (PR #2 open on jmcentire/pact). Run pact resume . each time it pauses. If the daemon exits, restart it and run pact resume . again.',
      },
      {
        kind: 'bug',
        text: 'If state ends up as "status": "failed" in .pact/state.json, reset it manually: set status back to "active", clear completed_at and pause_reason, set interview_result.approved to true.',
      },
      {
        kind: 'info',
        text: 'Pact always generates Python + pytest contract implementations regardless of sops.md stack — these are the contract layer. Your actual app code is separate.',
      },
      {
        kind: 'info',
        text: 'API key must be set in the shell that runs pact daemon. Use: source /path/to/.env && pact daemon .',
      },
    ],
  },
  {
    slug: 'advocate',
    name: 'Advocate',
    step: 4,
    tagline: 'Six AI personas review your code simultaneously from adversarial angles',
    accent: '#8b5cf6',
    accentBg: 'rgba(139,92,246,0.08)',
    videoUrl: 'https://www.youtube.com/embed/sKOM3NvW7lY',
    version: '0.1.0',
    description:
      'Advocate runs a 6-persona adversarial review of the code produced by Pact. Six AI reviewers attack the code simultaneously from different angles and surface issues before you deploy. Typical cost: $0.15–0.30 for a small project, $0.50–1.00 for multi-component.',
    activateCmd:
      '# bash / zsh\nsource ../exemplar.tools/advocate/.venv/bin/activate\n\n# fish\nsource ../exemplar.tools/advocate/.venv/bin/activate.fish',
    installCmd: 'source ../exemplar.tools/advocate/.venv/bin/activate',
    cost: '$0.15–0.30 small project, $0.50–1.00 multi-component',
    quickStart: [
      '# Review all of src/ — save JSON + HTML',
      'advocate review src/ -o findings.json --html review-report.html',
      '',
      '# Focus on specific personas',
      'advocate review src/ -p red_team -p adversarial   # security focus',
      'advocate review src/ -p sage -p user               # design/clarity',
      '',
      '# Cheaper sequential mode (same results, lower cost)',
      'advocate review src/ --sequential',
      '',
      'deactivate',
    ],
    personas: [
      { name: 'Red Team', angle: 'It\'s vulnerable — harden it' },
      { name: 'Adversarial', angle: 'It\'s wrong — defend your assumptions' },
      { name: 'Sage', angle: 'It\'s complicated — simplify it' },
      { name: 'User', angle: 'It\'s unintuitive — clarify it' },
      { name: 'SME', angle: 'Peer review — would a colleague sign off?' },
      { name: 'Good Friend', angle: 'The harsh truth you need to hear' },
    ],
    notes: [
      {
        kind: 'info',
        text: 'Each persona prints findings to the terminal in real time as it finishes. The full review takes ~30 seconds in parallel mode.',
      },
      {
        kind: 'info',
        text: 'The HTML report is easier to read than the JSON — open review-report.html in a browser after the run.',
      },
      {
        kind: 'info',
        text: 'Disagreements between personas are valuable: when two personas rate the same issue differently (e.g. Sage: HIGH, SME: INFO), that tension reveals a real tradeoff worth examining.',
      },
      {
        kind: 'warning',
        text: 'Fix CRITICAL and HIGH findings before proceeding to Step 3. Not all findings are code bugs — some reflect how Pact decomposed the project.',
      },
      {
        kind: 'bug',
        text: 'Use branch vaskoevgen:fix/missing-jinja2-dependency until the missing Jinja2 dependency PR merges upstream.',
      },
    ],
  },
  {
    slug: 'arbiter',
    name: 'Arbiter',
    step: 5,
    tagline: 'Trust scoring, blast-radius analysis, and authority enforcement',
    accent: '#ef4444',
    accentBg: 'rgba(239,68,68,0.08)',
    videoUrl: 'https://www.youtube.com/embed/4f5uqWGs2ws',
    version: '0.1.0',
    description:
      'Arbiter enforces authority exclusivity, computes trust scores (0.1–1.0) from audit events, and classifies blast radius for every proposed change. Trust is computed from evidence — never declared. Six multiplicative factors: base_weight × age × consistency × taint × review × decay.',
    activateCmd:
      '# bash / zsh\nsource ../exemplar.tools/arbiter/.venv/bin/activate\n\n# fish\nsource ../exemplar.tools/arbiter/.venv/bin/activate.fish',
    installCmd: 'source ../exemplar.tools/arbiter/.venv/bin/activate',
    quickStart: [
      'arbiter init',
      '# Creates: .arbiter/registry/trust_ledger.jsonl, arbiter.yaml',
      '',
      'arbiter register access_graph.json',
      '# Expected: "Registered: N nodes, N authority domains"',
      '',
      'arbiter trust <node_id>             # trust score + history',
      'arbiter blast-radius <change>       # impact surface of a change',
      '',
      'deactivate',
    ],
    keyConcepts: [
      { concept: 'Trust score', meaning: '0.1–1.0 per node, built from audit events. Canary escape → 0.0' },
      { concept: 'Trust tier', meaning: 'PROBATIONARY → LOW → ESTABLISHED → HIGH → TRUSTED' },
      { concept: 'Authority domain', meaning: 'One node owns each domain — enforced at register time' },
      { concept: 'Blast radius', meaning: 'Impact surface of a change: affected nodes × data tiers × soak requirement' },
      { concept: 'Canary', meaning: 'Synthetic fingerprinted data injected to detect leakage across component boundaries' },
    ],
    integrationStatus:
      'arbiter init, canary, trust, and report CLI commands work. arbiter watch / arbiter serve (live sidecar) are not yet implemented. Pact → Arbiter integration: Pact writes access_graph.json using a "components" schema; Arbiter register expects a "nodes" schema — fixed in vaskoevgen fork.',
    notes: [
      {
        kind: 'bug',
        text: 'Pact writes access_graph.json with a "components" key. Arbiter register expects a "nodes" key. Fix: use the vaskoevgen fork which translates components → nodes automatically. Without the fix, register always fails with "Graph contains no nodes".',
      },
      {
        kind: 'info',
        text: 'Policy always uses raw trust scores (0.1–1.0), never display tiers. Trust ledger is append-only JSONL with SHA256 integrity checkpoints every 100 entries.',
      },
    ],
  },
  {
    slug: 'baton',
    name: 'Baton',
    step: 6,
    tagline: 'Circuit orchestration with self-healing topology and canary deployment',
    accent: '#f97316',
    accentBg: 'rgba(249,115,22,0.08)',
    videoUrl: 'https://www.youtube.com/embed/XGu3XTfvG1c',
    version: '0.1.0',
    description:
      'Baton orchestrates deployment as a self-healing circuit topology. It manages service ports, routes traffic between nodes, and runs canary analyses against error-rate (<5%) and latency (<500ms p95) thresholds. OTLP spans flow to Arbiter for consistency checks.',
    activateCmd:
      '# Step 1: generate baton.yaml using the Pact venv\nsource ../exemplar.tools/pact/.venv/bin/activate\npact deploy .\ndeactivate\n\n# Step 2: activate Baton\n# bash / zsh\nsource ../exemplar.tools/baton/.venv/bin/activate\n\n# fish\nsource ../exemplar.tools/baton/.venv/bin/activate.fish',
    installCmd: 'source ../exemplar.tools/baton/.venv/bin/activate',
    quickStart: [
      '# 1. Generate baton.yaml (uses Pact venv)',
      'source ../exemplar.tools/pact/.venv/bin/activate',
      'pact deploy .',
      'deactivate',
      '',
      '# 2. Activate Baton',
      'source ../exemplar.tools/baton/.venv/bin/activate',
      '',
      '# 3. Edit baton.yaml — add role: ingress and correct port:',
      '# nodes:',
      '# - name: root',
      '#   port: 3001          # your app\'s actual port',
      '#   role: ingress       # required on entry-point nodes',
      '',
      '# 4. Verify the circuit',
      'baton status',
      '',
      '# 5. Boot in mock mode (no live app needed)',
      'baton up --mock',
      '# Visit http://127.0.0.1:<port> → {"status": "mock", "port": 2<port>}',
      '',
      '# 6. Check signals and metrics',
      'baton signals    # recent request signals',
      'baton metrics    # persistent metrics',
      '',
      'deactivate',
    ],
    notes: [
      {
        kind: 'info',
        text: 'pact deploy . generates one Baton node per deployable component. Single-component projects get one node named "root" on port 3000; multi-component projects get one node per leaf component starting at port 3000.',
      },
      {
        kind: 'warning',
        text: 'Docker Desktop on macOS only proxies PostgreSQL correctly through the standard port 5432. Other ports fail with SCRAM-SHA-256 auth errors regardless of pg_hba.conf.',
      },
      {
        kind: 'bug',
        text: 'baton slot has three CLI bugs upstream: command arg clobbered dispatch, process exited immediately killing adapters, and mock server bound the live service port. Fix branch: fix/baton-slot-command.',
      },
      {
        kind: 'info',
        text: 'To run with a live app, use baton slot instead of baton up. baton slot boots the circuit, starts your service, wires mocks for other nodes, and blocks until Ctrl+C.',
      },
    ],
  },
  {
    slug: 'sentinel',
    name: 'Sentinel',
    step: 7,
    tagline: 'Watches logs, attributes errors to Pact components, tightens contracts',
    accent: '#06b6d4',
    accentBg: 'rgba(6,182,212,0.08)',
    videoUrl: 'https://www.youtube.com/embed/k8RVrSnEw6I',
    version: '0.1.0',
    description:
      'Sentinel watches production logs, attributes errors to Pact components via embedded PACT keys, and tightens contracts so each bug class becomes non-recurring. It can trigger LLM-generated fixes within a configurable budget.',
    activateCmd:
      '# bash / zsh\nsource ../exemplar.tools/sentinel/.venv/bin/activate\n\n# fish\nsource ../exemplar.tools/sentinel/.venv/bin/activate.fish',
    installCmd: 'source ../exemplar.tools/sentinel/.venv/bin/activate',
    quickStart: [
      'sentinel init',
      '# Created sentinel.yaml, initialized .sentinel/',
      '',
      '# Register Pact components — imports PACT keys from src/',
      'sentinel register .',
      '',
      '# View incident report',
      'sentinel report',
      '# "No incidents recorded." is expected on a fresh project',
      '',
      '# Configure log sources in sentinel.yaml:',
      '# sources:',
      '#   - type: file',
      '#     path: .baton/service_logs.jsonl',
      '#     format: jsonl',
      '#     error_patterns:',
      '#       - \'"severity": "error"\'',
      '#       - \'Traceback\'',
      '#       - \'500 Internal Server Error\'',
      '',
      '# Start the log watcher (blocks until Ctrl+C)',
      'sentinel watch',
      '',
      'deactivate',
    ],
    notes: [
      {
        kind: 'warning',
        text: 'Use sentinel watch NOT sentinel serve. sentinel serve starts only the HTTP API and does NOT watch logs. This is a known misleading command name.',
      },
      {
        kind: 'warning',
        text: 'Baton writes logs as JSONL with lowercase "severity": "error". Sentinel\'s defaults (ERROR, CRITICAL, Traceback) are case-sensitive and won\'t match. Add the JSONL-specific pattern to error_patterns.',
      },
      {
        kind: 'info',
        text: 'Attribution as "unknown" is normal when errors originate in third-party libraries (e.g. psycopg2 tracebacks) — those lines have no PACT: key. Errors logged via _log("error", ...) will be attributed correctly.',
      },
    ],
  },
  {
    slug: 'chronicler',
    name: 'Chronicler',
    step: 8,
    tagline: 'Collects events, builds timestamped stories, forwards to Stigmergy',
    accent: '#ec4899',
    accentBg: 'rgba(236,72,153,0.08)',
    videoUrl: 'https://www.youtube.com/embed/a94Kpf0bYVg',
    version: '0.1.0',
    description:
      'Chronicler collects events (OTLP spans, webhooks, Sentinel incidents, log files), groups them into stories at three granularities, and forwards completed stories to Stigmergy and Apprentice.',
    activateCmd:
      '# bash / zsh\nsource ../exemplar.tools/chronicler/.venv/bin/activate\n\n# fish\nsource ../exemplar.tools/chronicler/.venv/bin/activate.fish',
    installCmd: 'source ../exemplar.tools/chronicler/.venv/bin/activate',
    quickStart: [
      '# Validate config (config parsing is fully implemented)',
      'python -c "',
      'from chronicler.config import load_config',
      'cfg = load_config(\'chronicler.yaml\')',
      'print(\'Sources:\', [s.type for s in cfg.sources])',
      'print(\'Sinks:  \', [s.type for s in cfg.sinks])',
      'print(\'Rules:  \', [r.name for r in cfg.rules])',
      '"',
      '',
      '# Check available commands',
      'chronicler --help',
      '# Commands: start, status, stories, replay',
      '',
      'deactivate',
    ],
    keyConcepts: [
      { concept: 'Request story', meaning: 'Grouped by trace_id — 30s timeout. One request and its downstream spans.' },
      { concept: 'Service story', meaning: 'Grouped by entity_id + component_id — 5m timeout. Sequence of requests to one component.' },
      { concept: 'Journey story', meaning: 'Grouped by session_id — 30m timeout. Full causal chain across components.' },
    ],
    integrationStatus:
      'Configuration schema and correlation engine are fully implemented. The CLI commands (start, status, stories, replay) parse correctly but runtime handlers are not yet wired up — all commands return immediately without side effects. The disk sink is fully implemented; stigmergy, apprentice, and kindex sinks are placeholders.',
    notes: [
      {
        kind: 'info',
        text: 'Use Chronicler today to validate your config and understand the story model. Live event collection ships in the next release.',
      },
      {
        kind: 'info',
        text: 'Only the disk sink is fully implemented. stigmergy, apprentice, and kindex sinks are placeholders.',
      },
    ],
  },
  {
    slug: 'stigmergy',
    name: 'Stigmergy',
    step: 9,
    tagline: 'Self-organizing agent mesh that surfaces coordination patterns from signals',
    accent: '#84cc16',
    accentBg: 'rgba(132,204,22,0.08)',
    videoUrl: 'https://www.youtube.com/embed/4z7--TKIvQ4',
    version: '0.1.0',
    description:
      'Stigmergy ingests signals from GitHub, Linear, Slack, and Grafana, routes them through a self-organizing agent mesh, and surfaces structural patterns: coordination gaps, knowledge silos, and parallel activity that could become conflicts. Runs without an LLM key — the default stub provider uses deterministic heuristics at zero cost.',
    activateCmd:
      '# fish\nsource ../exemplar.tools/stigmergy/.venv/bin/activate.fish\n\n# bash / zsh\nsource ../exemplar.tools/stigmergy/.venv/bin/activate',
    installCmd: 'source ../exemplar.tools/stigmergy/.venv/bin/activate',
    quickStart: [
      '# 1. Initialize (MUST be run interactively — do not pipe answers)',
      'stigmergy init',
      '',
      '# Answer prompts:',
      '# Enable GitHub? → Y',
      '# Use default repos? → Y',
      '# GitHub mode → mock  (no gh auth needed)',
      '# Enable Linear? → N',
      '# Enable Grafana? → N',
      '# LLM provider → stub  (no API key needed)',
      '',
      '# 2. After init — verify .stigmergy/config.yaml:',
      '# sources.github.mode must be "mock" (not "Y")',
      '# llm.provider must be "stub" (not "N")',
      '',
      '# 3. Run one batch',
      'stigmergy run --once',
      '',
      '# 4. View status from last run',
      'stigmergy status',
      '',
      '# 5. For continuous operation',
      'stigmergy serve',
      '',
      'deactivate',
    ],
    keyConcepts: [
      { concept: 'GitHub mock', meaning: 'Built-in stub data — no gh auth needed. 7 synthetic signals per run.' },
      { concept: 'stub provider', meaning: 'Deterministic heuristics at $0.00 cost. Swap to anthropic for LLM-enhanced analysis.' },
      { concept: 'Parallel activity', meaning: 'Detected when two engineers work in the same signal space (spectral similarity ≥ 61%).' },
    ],
    notes: [
      {
        kind: 'warning',
        text: 'ALWAYS run stigmergy init interactively. If you pipe answers, inputs misalign and the config is written as mode: Y and provider: N. Fix .stigmergy/config.yaml manually: mode must be "mock" or "live", provider must be "stub" or "anthropic".',
      },
      {
        kind: 'info',
        text: '"WARNING: 2 agents running without LLM — mechanical heuristics producing noise" is expected in stub mode. Findings are still written to .stigmergy/insights.jsonl.',
      },
      {
        kind: 'info',
        text: 'To use real Anthropic analysis: set ANTHROPIC_API_KEY, re-run stigmergy init, and choose "anthropic" for LLM provider.',
      },
    ],
  },
  {
    slug: 'apprentice',
    name: 'Apprentice',
    step: 10,
    tagline: 'Routes to frontier API, collects training data, fine-tunes a local model',
    accent: '#a855f7',
    accentBg: 'rgba(168,85,247,0.08)',
    videoUrl: 'https://www.youtube.com/embed/BhltpaigLTo',
    version: '0.1.0',
    description:
      'Apprentice routes every request to the frontier API (Claude, GPT, etc.), collects the responses as training examples, fine-tunes a local model, then progressively shifts traffic to it — while continuously verifying quality. The goal: replace expensive API calls with a $0 local model that produces equivalent results for your specific tasks.',
    activateCmd:
      '# fish\nsource ../exemplar.tools/apprentice/.venv/bin/activate.fish\n\n# bash / zsh\nsource ../exemplar.tools/apprentice/.venv/bin/activate',
    installCmd: 'source ../exemplar.tools/apprentice/.venv/bin/activate',
    quickStart: [
      '# Prerequisite: Ollama (optional — fine-tuning only)',
      '# brew install ollama && ollama pull llama3.1:8b && ollama serve',
      '',
      '# Set API key before serve',
      'set -x ANTHROPIC_API_KEY your-key   # fish',
      '',
      '# 1. Initialize — create apprentice.yaml',
      'apprentice init',
      '# Wizard: task name, provider (anthropic), model (claude-haiku-4-5-20251001)',
      '',
      '# 2. Fix wizard bug in apprentice.yaml:',
      '# input_schema:',
      '#   - name: expression   # wizard always writes "text" — change to match your {var}',
      '#     type: string',
      '#     required: true',
      '',
      '# 3. Start the HTTP daemon (port 8710)',
      'apprentice serve',
      '',
      '# 4. Check phase and training progress',
      'apprentice status',
      '',
      '# 5. Execute a task',
      'apprentice run my_task --input \'{"expression": "2 + 2"}\'',
      '',
      '# 6. Generate a full report',
      'apprentice report',
      '',
      'deactivate',
    ],
    phases: [
      { phase: 'Cold Start', what: 'Every request → remote API. Responses stored as training data.' },
      { phase: 'Reinforcement', what: 'Both models run. Evaluator scores local vs. remote. Rolling window tracks correlation.' },
      { phase: 'Steady State', what: 'Local model handles most traffic. Sampler periodically checks quality. Auto-regresses if it drops.' },
    ],
    notes: [
      {
        kind: 'bug',
        text: 'Wizard always writes "name: text" in input_schema regardless of your {variable}. After init, manually change the name to match your prompt template variable (e.g. expression, question, text).',
      },
      {
        kind: 'bug',
        text: 'Two CLI bugs fixed in vaskoevgen:fix/cli-run-and-report: apprentice run crashed with AttributeError on response.success; apprentice report crashed with AttributeError on raw_report.tasks.',
      },
      {
        kind: 'warning',
        text: 'ANTHROPIC_API_KEY must be set before apprentice serve. The command fails with "API key is unresolved" if the key is not in the process environment.',
      },
      {
        kind: 'info',
        text: 'Phase starts at "bootstrapping" with confidence 0.00. Needs 100 training examples before local model fine-tuning triggers.',
      },
    ],
  },
  {
    slug: 'kindex',
    name: 'Kindex',
    step: 11,
    tagline: 'Persistent knowledge graph that surfaces context across all sessions and tools',
    accent: '#14b8a6',
    accentBg: 'rgba(20,184,166,0.08)',
    version: '0.1.0',
    description:
      'Kindex maintains a typed knowledge graph (concepts, decisions, questions, tasks, watches) that persists across Claude Code sessions. It surfaces relevant context automatically via MCP and provides a searchable memory for the entire exemplar.tools stack.',
    activateCmd:
      '# kin is installed globally — no venv activation needed\n# ~/.local/bin/kin\n\n# Or activate venv:\nsource ../exemplar.tools/kindex/.venv/bin/activate',
    installCmd: '# kin is installed globally at ~/.local/bin/kin',
    quickStart: [
      'kin init',
      '',
      '# Add insights during a session',
      'kin add "key insight from this session"',
      'kin add --type concept "Pact always generates Python contract layer"',
      'kin add --type decision "Use vaskoevgen fork for arbiter fix"',
      '',
      '# Search across sessions',
      'kin search "pact contracts"',
      '',
      '# Pull context block for CLAUDE.md',
      'kin context "deployment"',
      '',
      '# Check graph stats',
      'kin status',
      '',
      '# Register with Claude Code as MCP server (run once)',
      'claude mcp add --scope user --transport stdio kindex -- kin-mcp',
    ],
    keyConcepts: [
      { concept: 'concept', meaning: 'Patterns, facts, key files, domain terms, how things work' },
      { concept: 'decision', meaning: 'Architectural choices, trade-offs, why X over Y' },
      { concept: 'question', meaning: 'Open problems, things to investigate later' },
      { concept: 'task', meaning: 'Actionable work items — link to related concepts' },
      { concept: 'watch', meaning: 'Known instabilities, flaky tests, APIs that might break' },
    ],
    notes: [
      {
        kind: 'info',
        text: 'kin is installed globally at ~/.local/bin/kin — no venv activation needed in most setups.',
      },
      {
        kind: 'info',
        text: 'Once registered as MCP (claude mcp add ...), Kindex is automatically available in every Claude Code session. claude mcp list shows ✓ Connected.',
      },
      {
        kind: 'info',
        text: 'Search before adding to avoid duplicates. The graph persists across sessions — treat it like version control for knowledge.',
      },
    ],
  },
]

export const TOOL_MAP = Object.fromEntries(TOOLS.map((t) => [t.slug, t]))
