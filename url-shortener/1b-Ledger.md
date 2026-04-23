```
yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> source ../exemplar.tools/ledger/.venv/bin/activate

# ledger.yaml was already created by `ledger init` in a prior session.
# Manually added backend to ledger.yaml (ledger backend add has a bug):
#
#   backends:
#     - name: links_db
#       base_url: ""
#
# Manually created schemas/links.yaml (ledger schema add is a stub).
# Schema format requirements:
#   - top-level keys: name, version (integer), fields (list)
#   - field keys: name, field_type, classification, nullable, annotations
#   - annotations must be dicts: [{name: "immutable"}] — NOT bare strings ["immutable"]

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

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger schema add schemas/links.yaml
# exits 0 — stub command; schema is validated at config load time

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger schema validate
# exits 0, no output — passes silently

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger schema show links
{}
# stub — returns empty dict

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger export --format pact
{'contracts': []}
# stub — export not yet implemented

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> ledger export --format arbiter
{'contracts': []}

(.venv) yevhenvasko@yevhens-mbp ~/s/e/url-shortener (feature/howto-next-iteration)> deactivate

# ── Annotations applied to url-shortener links table ──────────────────────────
#
# Field        | Classification | Annotations               | Sentinel severity
# -------------|----------------|---------------------------|------------------
# id           | PUBLIC         | primary_key               | info
# short_code   | PUBLIC         | immutable, not_null       | critical / low
# original_url | PUBLIC         | immutable, not_null       | critical / low
# created_at   | PUBLIC         | immutable, not_null,      | critical / low / high
#              |                | audit_field               |
# hit_count    | PUBLIC         | not_null, audit_field     | low / high
#
# ── Upstream bugs encountered ─────────────────────────────────────────────────
#
# 1. `ledger backend add` crashes — TypeError: register_backend() takes 3
#    positional arguments but 4 were given. Workaround: edit ledger.yaml directly.
#    Backend model fields: name, enabled, base_url, timeout_ms (no owner/type).
#
# 2. Annotations in schema YAML must be dicts [{name: "immutable"}], not
#    bare strings ["immutable"]. parse_schema_file silently skips bare strings.
#
# Both tracked in jmcentire/ledger#2.
```
