# Grok Read This First

## What This Repo Is Now

This repo was reorganized for Grok-first direct repo work, but it was not fully migrated away from legacy paths.

Treat it as a dual-surface system:

1. Canonical Grok-first inputs for direct generation and maintenance
2. Legacy compatibility paths that still must keep working

## Read Order

When working directly from the repo, read in this order:

1. `governance/`
2. `aggregates/`
3. `domains/`
4. `prompts/`
5. `voices/`
6. `frontmatter-templates/`
7. `schemas/pipeline_2_policy.yaml`

## Canonical Inputs

- Governance rules: `governance/`
- Source data hubs: `aggregates/`
- Voice files: `voices/`
- Frontmatter shape guides: `frontmatter-templates/`
- Preview-only draft area: `outputs/`

## Compatibility Paths You Must Not Break

- `.github/`
- `docs/`
- `data/`
- `shared/voice/profiles/`
- root `run.py`

## Critical Working Rules

- Prefer canonical inputs first, but preserve legacy compatibility.
- Do not assume `aggregates/` replaced `data/` everywhere.
- Do not patch production frontmatter directly if source YAML or export config is the real source of truth.
- If canonical and compatibility copies both exist, update both or stop and resolve drift.
- If you change aggregate schema shape, update validators too.
- Treat `outputs/` as preview-only, not production truth.

## Validator Rule That Matters Most

Canonical schema changes are incomplete until `scripts/validation/verify_data_integrity.py` still passes against the canonical aggregate model.

Run validation from repo root with repo import context, for example:

- `PYTHONPATH=. /usr/local/bin/python3 scripts/validation/verify_data_integrity.py`

## If You Need More Context

- Detailed adaptation report: `governance/GROK_REPO_ADAPTATIONS.md`
- Quick reference: `governance/QUICK_REFERENCE.md`
- Canonical policy: `governance/grok-policies.md`
- Pipeline 2 contract: `schemas/pipeline_2_policy.yaml`