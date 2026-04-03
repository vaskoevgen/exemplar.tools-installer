# exemplar.tools — Repository Installer

Automated installer for [exemplar.tools](https://exemplar.tools/) that clones or updates a configurable set of Git repositories in a single command.

---

## Quick start

```bash
curl -fsSL https://raw.githubusercontent.com/vaskoevgen/exemplar.tools-installer/main/install.sh | bash
```

The script reads `repos.conf` from the same repository, processes every listed repo, and reports a summary.

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

## Requirements

- `git` ≥ 2.x
- `curl`
- bash 3.2+ (macOS default is fine)

---

## License

MIT — see [LICENSE](LICENSE).
