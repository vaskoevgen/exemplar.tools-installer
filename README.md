# exemplar.tools — Repository Installer

Automated installer for [exemplar.tools](https://exemplar.tools/) that clones or updates a configurable set of Git repositories in a single command.

---

## Quick start

**Latest version (always up to date):**
```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```

**Pin to a specific release:**
```bash
EXEMPLAR_VERSION=v1.0.0 \
  curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```

The script reads `repos.conf` from the matching ref, processes every listed repo, and reports a summary.

---

## How it works

```
install.sh
    │
    ├── fetches repos.conf  (from GitHub or a custom URL)
    │
    └── for each repo entry:
            if local dir exists  →  git fetch + checkout / pull
            if local dir absent  →  git clone --branch <ref>
```

- **Branch ref**: fetches latest remote state and fast-forward merges.
- **Tag ref**: checks out the exact tag; skips if already on it.
- Failures are collected and reported in the summary; the script exits with code `1` if any repo fails.

---

## Configuration — `repos.conf`

Each non-comment line describes one repository:

```
<git_url>  <branch_or_tag>  [local_dir]
```

| Field | Required | Description |
|---|---|---|
| `git_url` | yes | Full HTTPS or SSH clone URL |
| `branch_or_tag` | yes | Branch name (`main`) or tag (`v1.2.0`) |
| `local_dir` | no | Destination path; supports `~`. Defaults to `$EXEMPLAR_INSTALL_DIR/<repo-name>` |

### Example `repos.conf`

```
# Latest stable branch
https://github.com/vaskoevgen/example-tool    main

# Pin to a release tag
https://github.com/vaskoevgen/example-tool    v1.2.0

# Explicit local destination
https://github.com/vaskoevgen/example-tool    main    ~/tools/example-tool
```

Lines starting with `#` and blank lines are ignored.

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `EXEMPLAR_INSTALL_DIR` | `./exemplar.tools` | Base directory when `local_dir` is omitted from a repo entry |
| `EXEMPLAR_CONFIG_URL` | `repos.conf` URL in this repo | URL **or local path** to an alternative config file |
| `EXEMPLAR_VERSION` | `main` | Git tag to pin to (e.g. `v1.2.0`); controls which `repos.conf` is fetched |
| `EXEMPLAR_NO_DEPS` | _(unset)_ | Set to any value to skip all dependency installation |
| `EXEMPLAR_NO_COLOR` | _(unset)_ | Set to any value to disable colored output |

### Use a custom config file

```bash
# Remote config
EXEMPLAR_CONFIG_URL=https://example.com/my-repos.conf \
  curl -fsSL .../install.sh | bash

# Local config
EXEMPLAR_CONFIG_URL=~/my-repos.conf \
  bash install.sh
```

### Install into a custom directory

```bash
EXEMPLAR_INSTALL_DIR=~/workspace \
  curl -fsSL .../install.sh | bash
```

---

## Running locally

```bash
# Clone this installer
git clone https://github.com/vaskoevgen/exemplar.tools-installer.git
cd exemplar.tools-installer

# Edit repos.conf, then run
bash install.sh
```

---

## Releases

Releases are created automatically when a version tag is pushed:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will:
1. Validate `repos.conf` and `install.sh` syntax
2. Generate release notes from commits since the previous tag
3. Publish a GitHub Release with `install.sh` and `repos.conf` attached as assets

Each release captures a consistent snapshot of which repositories and refs are included, so clients can pin to a known-good version with `EXEMPLAR_VERSION`.

---

## How it all fits together

```
[Cartographer]  ← optional: existing projects only
      ↓
[Constrain]  →  prompt.md, constraints.yaml, component_map.yaml, trust_policy.yaml, schema_hints.yaml
      ↓                                    ↓
  [Ledger]                             [Arbiter init]
  (schemas)                            arbiter watch (sidecar, port 7700)
      ↓                                    ↓
    export assertions            ┌─────────────────────┐
      ↓                          │                     │
[Pact]  →  src/, tests/, access_graph.json  →  [Arbiter register]
      ↓                                            ↓
  [Advocate]                              trust scores, blast radius
  (code review gate)
      ↓
[Baton]  →  circuit up  →  OTLP spans  →  Arbiter
      ↓
[Sentinel]  →  incidents, contract tightening
      ↓                    ↓
[Chronicler]  →  stories (request / service / journey)
      ↓                    ↓
[Stigmergy]          [Apprentice]
(org patterns)    (model distillation)

[Kindex]  ←  cross-cutting knowledge layer (all tools feed into it)
```

**Feedback loops:**
- `Sentinel → Constrain` — production bugs tighten contracts, preventing the whole class from recurring
- `Chronicler → Apprentice` — production traffic trains local models, progressively reducing API cost

---

## howto.md — Next Iteration Roadmap

The current `howto.md` covers: Constrain → Ledger → Pact → Baton → Sentinel → Kindex.

The following tools are not yet documented and should be added in the next iteration.

### Missing tools

| Tool | Where in flow | What it does |
|------|--------------|--------------|
| **Cartographer** | Before Constrain | Scans existing codebases and drafts artifacts for the whole stack automatically — the onboarding step for existing projects |
| **Advocate** | After Pact | 6-persona adversarial code review (Red Team, Sage, User, SME, etc.). Natural quality gate before deploying |
| **Arbiter** | Between Pact and Baton | Access auditing, blast-radius analysis, trust scoring. Has its own `init/register/watch/serve` workflow |
| **Chronicler** | After Baton/Sentinel | Correlates events into stories, bridges runtime to learning (feeds Stigmergy + Apprentice) |
| **Stigmergy** | After Chronicler | Mines organisational patterns from GitHub/Linear/Slack signals — surfaces coordination gaps |
| **Apprentice** | After Chronicler | Progressive model distillation — routes API → local model as quality is proven, reducing cost |
| **Webprobe** | Standalone | Security/UX site auditor using LLM agents — useful for auditing deployed services |

**Separate optional stack:**
- **Signet** — cryptographic identity vault + MCP server
- **Tessera** — self-validating documents with hash chain

### Recommended howto structure (next iteration)

```
Step 0 — Cartographer    (existing projects only)
Step 1 — Specify         Constrain → Ledger
Step 2 — Build           Pact → Advocate (review gate)
Step 3 — Govern          Arbiter
Step 4 — Deploy          Baton
Step 5 — Observe         Sentinel → Chronicler → Stigmergy
Step 6 — Learn           Apprentice
Step 7 — Knowledge       Kindex
Optional                 Webprobe, Signet, Tessera
```

---

## Requirements

- `git` ≥ 2.x
- `curl`
- bash 3.2+ (macOS default is fine)

---

## License

MIT — see [LICENSE](LICENSE).
