```
yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> pwd
/Users/yevhenvasko/source/exemplar.tools-installer/url-shortener

yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> source ../exemplar.tools/ledger/.venv/bin/activate

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger --help
Usage: ledger [OPTIONS] COMMAND [ARGS]...

  Ledger CLI — schema governance and migration tooling.

Options:
  --config TEXT              Path to ledger.yaml config file
  --verbose                  Enable verbose output
  --format [text|json|yaml]  Output format
  --help                     Show this message and exit.

Commands:
  backend   Backend management commands.
  builtins  Built-in annotation definitions and propagation rules.
  export    Export contracts to external tools.
  init      Initialize a new ledger.yaml scaffold.
  migrate   Migration management commands.
  mock      Generate mock data for a backend table.
  schema    Schema management commands.
  serve     Start the Ledger API server.

# ledger.yaml was already created by `ledger init` in a prior session.
# It contained: project_name, schemas_dir, changelog_path, plans_dir,
# backends: [], custom_annotations: []

# ledger backend add has a bug (TypeError: register_backend() takes 3 positional
# arguments but 4 were given). Registered the backend directly in ledger.yaml:
#
# backends:
#   - name: links_db
#     base_url: ""
#
# Note: Backend model fields are: name, enabled, base_url, timeout_ms
# The 'owner' field does not exist on the model — omit it.

# Created schemas/links.yaml manually (schema add is a stub anyway):
# Required top-level fields: name, version (int), fields (list)
# Required field keys: name, field_type, classification, nullable, annotations
# Annotations must be dicts with 'name' key — NOT bare strings

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger schema add schemas/links.yaml
# exits 0 — stub command, does not persist. Schema is validated at config load.

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger schema show links
{}
# stub — returns empty dict

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger schema validate
# exits 0, no output — validation runs at config load time (parse_schema_file)

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger builtins list
audit_field: pact=not_null arbiter=audit_only baton=no_mask sentinel=high
encrypted_at_rest: pact=type_match arbiter=enforce_tier baton=full_mask sentinel=critical
gdpr_erasable: pact=field_present arbiter=enforce_tier baton=full_mask sentinel=high
immutable: pact=field_present arbiter=block_downgrade baton=no_mask sentinel=critical
not_null: pact=not_null arbiter=audit_only baton=no_mask sentinel=low
pii_field: pact=field_present arbiter=enforce_tier baton=partial_mask sentinel=high
primary_key: pact=not_null arbiter=audit_only baton=no_mask sentinel=info
soft_delete_marker: pact=field_present arbiter=enforce_tier baton=no_mask sentinel=medium

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger builtins show immutable
  annotation_name: immutable
  pact_assertion_type: field_present
  arbiter_tier_behavior: block_downgrade
  baton_masking_rule: no_mask
  sentinel_severity: critical

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger builtins show audit_field
  annotation_name: audit_field
  pact_assertion_type: not_null
  arbiter_tier_behavior: audit_only
  baton_masking_rule: no_mask
  sentinel_severity: high

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger export --format pact
{'contracts': []}
# stub — export commands return empty contracts

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger export --format arbiter
{'contracts': []}

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> deactivate

# ── Annotations applied to url-shortener links table ──────────────────────────
#
# Field        | Classification | Annotations               | Why
# -------------|----------------|---------------------------|-------------------
# id           | PUBLIC         | primary_key               | auto PK
# short_code   | PUBLIC         | immutable, not_null       | never changes after create
# original_url | PUBLIC         | immutable, not_null       | link integrity
# created_at   | PUBLIC         | immutable, not_null,      | audit trail
#              |                | audit_field               |
# hit_count    | PUBLIC         | not_null, audit_field     | analytics, changes frequently
#
# Propagation impact (from builtins):
#   immutable  → sentinel: critical, arbiter: block_downgrade
#   audit_field → sentinel: high,    arbiter: audit_only
#
# ── Upstream bugs encountered ─────────────────────────────────────────────────
#
# 1. `ledger backend add` — TypeError: register_backend() takes 3 positional
#    arguments but 4 were given. Workaround: edit ledger.yaml directly.
#    (tracked in jmcentire/ledger#2)
#
# 2. Annotations in schema YAML must be dicts [{name: "immutable"}], not
#    bare strings ["immutable"]. parse_schema_file silently skips bare strings.
#
# 3. Backend model has no 'owner' field — 'type' field also not in model.
#    Valid fields: name, enabled, base_url, timeout_ms.
```
