# Schema Authority And Cleanup

## Canonical Source Of Truth

- Canonical schema: `schemas/all_domains_schema.yaml`
- Owning repo: `z-beam-generator`
- Purpose: cross-domain schema contract for Grok-maintained source structure and shared frontmatter vocabulary

## Removed Legacy Schemas

### `data/schemas/frontmatter.json`
- Status: removed
- Reason: no live runtime consumers remained after validator defaults and schema tests moved to `schemas/all_domains_schema.yaml`

### `z-beam/schemas/frontmatter-v5.0.0.json`
- Status: removed
- Reason: it was docs-only and no frontend runtime validation depended on it

### `domains/contaminants/schema.json` and `domains/contaminants/schema.yaml`
- Status: removed
- Reason: both files described older contaminant shapes and had no live consumers outside historical manifests

## Cleanup Outcome

1. `schemas/all_domains_schema.yaml` is now the only active schema reference in the touched docs, manifests, validators, and tests.
2. Historical notes may still mention removed schema paths when describing past migrations, but active guidance should not treat them as live artifacts.