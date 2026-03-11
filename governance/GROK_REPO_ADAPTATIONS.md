# Grok Repo Adaptations Report

## Purpose

This report records the adaptations made during the Grok-first repository organization so future Grok agents can maintain source data and generation contracts without breaking the legacy runtime, validation tooling, or export workflows.

If you only need the short operational version first, read `governance/GROK_READ_THIS_FIRST.md` before this document.

This repository now has two realities that must stay aligned:

1. Canonical Grok-first inputs for direct repo-driven work
2. Legacy compatibility paths still used by runtime code, docs, automation, and existing habits

The organization task was completed with a compatibility-first migration, not a destructive move.

## Canonical Read Model

Use this order when Grok agents read the repo as the source of truth for direct generation and maintenance:

1. `governance/`
2. `aggregates/`
3. `domains/`
4. `prompts/`
5. `voices/`
6. `frontmatter-templates/`
7. `schemas/pipeline_2_policy.yaml`

This order is intentional. It reflects how the repository was adapted for Pipeline 2, where direct repo inspection should replace ad hoc CLI-first assumptions.

## Main Adaptations Made

### 1. Canonical Grok-first directories were added without removing legacy paths

New canonical directories:

- `governance/`
- `aggregates/`
- `voices/`
- `frontmatter-templates/`
- `legacy/`
- `outputs/`
- `schemas/` for Grok-specific policy additions

These were added because Grok agents need obvious, top-level, low-ambiguity inputs for policy, source data, voices, and templates.

They were not introduced as a full rename of the repo layout because existing runtime and automation still depend on older locations.

### 2. Legacy compatibility surfaces were deliberately preserved

The following paths must still be treated as live compatibility surfaces:

- `.github/`
- `docs/`
- `data/`
- `shared/voice/profiles/`
- root `run.py`

Reason:

- Existing runtime code, validation scripts, Copilot instructions, and operational habits still reference them.
- Removing them would have created breaking changes, which violated the task requirement.

### 3. Root CLI behavior was preserved via a compatibility wrapper

Adaptation:

- Original CLI moved to `legacy/run.py`
- New root `run.py` now delegates to `legacy.run.main`

Reason:

- Grok-facing organization needed a clear separation between legacy runtime entrypoints and canonical repo inputs.
- Existing commands like `python3 run.py ...` still needed to work unchanged.

### 4. Canonical-first path resolution was added in code

Adaptation:

- `shared/utils/file_ops/path_manager.py` was extended with canonical-first helpers such as:
  - `get_preferred_existing_path`
  - `get_governance_dir`
  - `get_aggregates_dir`
  - `get_aggregate_file`
  - `get_voice_profiles_dir`
  - canonical aggregate file getters for materials, contaminants, compounds, settings, applications, and authors

Reason:

- Code needed to prefer canonical Grok-first locations when available.
- The same code also needed to fall back to legacy locations so old workflows did not break.

Implication for future maintenance:

- When adding a new canonical source, wire it through `PathManager` rather than hardcoding a new path in isolated files.

### 5. Runtime and quality tooling were updated to use canonical inputs when available

Adaptation examples:

- generator voice-profile loading now prefers `voices/`
- prompt-building guidance now references canonical voice locations
- quality analysis now resolves voice profiles through `PathManager`
- generation and integrity utilities were adjusted to support canonical aggregate files

Reason:

- Without code-level path adaptation, the new top-level folders would have been cosmetic only.

### 6. Governance and manifest files were mirrored into canonical form

Added canonical Grok-facing governance assets:

- `governance/copilot-instructions.md`
- `governance/QUICK_REFERENCE.md`
- `governance/grok-policies.md`
- `governance/grok_github_manifest_minimum.md`
- `schemas/pipeline_2_policy.yaml`
- `prompts/grok-direct-frontmatter.txt`

Reason:

- Grok agents need a short, obvious, canonical policy surface that can be read before diving into runtime internals.

Maintenance rule:

- If a governance rule changes and a compatibility copy still exists, update both or stop and resolve the drift.

### 7. Aggregate source YAMLs became the canonical research hubs

Canonical aggregate hubs now live in `aggregates/`, including:

- `Materials.yaml`
- `contaminants.yaml`
- `Compounds.yaml`
- `Applications.yaml`
- `Authors.yaml`
- `Settings.yaml`
- relationship/support files such as `MaterialApplications.yaml`, `IndustryApplications.yaml`, `MaterialApplicationRelationships.yaml`, and `DomainAssociations.yaml`

Reason:

- Grok agents doing direct repo-based rewriting need consolidated sources rather than deep traversal through many domain-specific legacy locations.

Important constraint:

- Legacy `data/...` YAML paths still exist and still matter.
- Do not assume the presence of a canonical aggregate means the legacy data path is dead.

### 8. Frontmatter templates were elevated to first-class canonical inputs

Canonical templates:

- `frontmatter-templates/sample-material-frontmatter.yaml`
- `frontmatter-templates/sample-contaminant-frontmatter.yaml`

Reason:

- Grok agents need explicit shape guides for direct frontmatter drafting.
- These templates reduce guesswork around nesting, naming, and section structure.

Maintenance rule:

- Templates are shape references, not alternative sources of truth.
- Do not patch production frontmatter directly when the source YAML or export contract is the real problem.

### 9. `outputs/` was defined as preview-only

Adaptation:

- `outputs/` was added as a canonical place for draft artifacts and previews.

Reason:

- Grok agents may need a safe place for draft frontmatter or inspection outputs that should not immediately become production truth.

Maintenance rule:

- Treat `outputs/` as temporary preview space only.
- Promotion into source YAML or production frontmatter must still follow the real source-of-truth path.

## Validator and Integrity Adaptations

The biggest non-obvious adaptation was not the folder structure. It was the validation layer.

### 10. The data integrity validator had to learn canonical aggregate schemas

Adaptation in `scripts/validation/verify_data_integrity.py`:

- It now resolves canonical aggregate files first, with legacy fallback.
- It now supports canonical `contaminants` root keys in addition to older legacy shapes.
- It now validates nested canonical relationship structures instead of only flat legacy relationship keys.
- It now tracks display paths so issue reports point at the actual canonical file being validated.
- It now normalizes some cross-domain aliases, including application IDs that may need the `-applications` suffix.

Canonical nested relationship paths that had to be explicitly supported include examples like:

- `relationships.interactions.contaminatedBy.items`
- `relationships.interactions.producesCompounds.items`
- `relationships.interactions.producedFromContaminants.items`
- `relationships.interactions.worksOnMaterials.items`
- `relationships.interactions.removesContaminants.items`
- `relationships.discovery.relatedMaterials.items`
- top-level `validMaterials`

Reason:

- Canonical-path migration alone is not enough.
- Validation breaks if the validator still assumes old flat YAML shapes.

This was a real failure mode during the organization task.

Operational rule:

- Any future schema move or normalization in `aggregates/` must be matched by validator updates before the migration is considered complete.

### 11. Validation execution depends on repo-root import context

Observed adaptation:

- Running `scripts/validation/verify_data_integrity.py` directly without repo-root import context can fail with `ModuleNotFoundError` for project modules.

Working invocation used during verification:

- `PYTHONPATH=. /usr/local/bin/python3 scripts/validation/verify_data_integrity.py`

Reason:

- The validator imports project modules such as `shared.utils.file_ops.path_manager`.

Maintenance rule:

- Run validators from the repo root with repo-root import context, or use an equivalent module-aware execution strategy.

## What Future Grok Agents Must Preserve

### 12. Compatibility-first is the standing maintenance posture

Do not treat the repo as fully migrated away from legacy surfaces.

Preserve behavior for:

- `python3 run.py ...`
- legacy governance references in `.github/` and `docs/`
- legacy source paths under `data/`
- legacy voice path under `shared/voice/profiles/`

If a future cleanup wants to remove compatibility paths, that is a separate migration and should not be folded into routine data maintenance.

### 13. Canonical and compatibility copies must not silently drift

This is especially important for:

- governance rules
- manifest files
- source YAML mirrors
- voice profile mirrors

Rule:

- If a canonical file is updated and a compatibility copy still exists, update the compatibility copy as part of the same change or explicitly stop and resolve the discrepancy.

### 14. Source-level fixes remain mandatory

Do not patch generated frontmatter as the primary fix.

Preferred fix order:

1. source YAML in canonical or required legacy location
2. export config or generation contract
3. generator/runtime logic
4. re-export

Direct frontmatter edits should only happen when the repo policy explicitly allows them and the source-of-truth model is not being bypassed.

## Practical Working Rules For Grok Agents

### 15. When rewriting or maintaining data, start here

Read first:

1. `governance/grok-policies.md`
2. `governance/QUICK_REFERENCE.md`
3. `schemas/pipeline_2_policy.yaml`
4. relevant files in `aggregates/`
5. relevant files in `domains/`
6. relevant prompt contracts in `prompts/`
7. relevant voice file in `voices/`

### 16. When editing data, decide whether the change is canonical-only or dual-surface

Use this rule:

- If the change affects direct Grok generation only and no compatibility file mirrors it, edit the canonical source.
- If a legacy mirror is still an active compatibility surface, update both.

### 17. When adding a new data field or relationship shape

You must review:

- aggregate YAML shape
- domain config expectations
- exporter assumptions
- validator assumptions
- any manifest or governance mention of the field

If any one of these is left behind, the repository becomes internally inconsistent even if the YAML itself looks valid.

### 18. When validating after data updates

Minimum expectation:

- run data integrity validation against canonical aggregate files
- ensure relationship validation still passes
- ensure the changed path model still matches compatibility assumptions

At the time this organization work was completed, the passing integrity baseline was:

- 464 total items
- 4430 total relationships
- 0 issues found

## Summary

The organization task was completed by making the repo easier for Grok agents to read without breaking the older runtime world that still exists around it.

The key adaptation was not just adding top-level folders. The real adaptation was creating a canonical-first, compatibility-safe system where:

- Grok agents can work from `governance/`, `aggregates/`, `voices/`, and `frontmatter-templates/`
- legacy runtime and automation still function
- validators understand the canonical nested data model
- future maintainers know that schema moves require validator and compatibility updates, not just file moves

Treat this repo as a dual-surface system until a later, explicit migration removes the legacy surfaces.