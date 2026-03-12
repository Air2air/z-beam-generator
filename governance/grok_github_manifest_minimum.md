# Grok GitHub Manifest (Minimum Required)

Generated: 2026-03-11
Repository: https://github.com/Air2air/z-beam-generator
Scope: Minimum required files only (not full project) for Grok to understand and run core generation logic.

Note: Treat this in-repo manifest as the canonical second-pass contract for Pipeline 2. The external gist must mirror this file's section order and path set.

## 0) Output Files
- Repo: https://github.com/Air2air/z-beam/tree/main/frontmatter
- frontmatter/materials/
- frontmatter/contaminants/
- frontmatter/applications/
- frontmatter/settings/
- frontmatter/compounds/

## 1) Core Runtime + Generation Pipeline
- run.py
- legacy/run.py
- generation/core/evaluated_generator.py
- generation/core/generator.py
- shared/text/utils/prompt_builder.py

## 2) Required Governance / Rules
- governance/copilot-instructions.md
- governance/QUICK_REFERENCE.md
- governance/grok-policies.md
- .github/copilot-instructions.md

## 3) Required Domain Contracts
- domains/materials/catalog.yaml
- domains/materials/config.yaml
- domains/applications/catalog.yaml
- domains/applications/config.yaml

## 4) Required Prompt Contracts
- prompts/registry/prompt_catalog.yaml
- prompts/registry/component_prompt_registry.yaml
- prompts/registry/shared_prompt_registry.yaml
- prompts/voice/material_description.yaml

## 5) Required Voice Profiles
- voices/indonesia.yaml
- voices/italy.yaml
- voices/taiwan.yaml
- voices/united_states.yaml

## 6) Required Source Data (Essentials)
- aggregates/Materials.yaml
- aggregates/contaminants.yaml
- aggregates/Compounds.yaml
- aggregates/MaterialApplications.yaml
- aggregates/IndustryApplications.yaml
- aggregates/MaterialApplicationRelationships.yaml
- aggregates/DomainAssociations.yaml
- aggregates/Applications.yaml
- aggregates/Authors.yaml
- aggregates/Settings.yaml

## 7) Required Schemas
- data/schemas/content_generation_policy.yaml
- data/schemas/component_single_line_prompts.yaml
- data/schemas/frontmatter.json
- schemas/pipeline_2_policy.yaml

## 8) Grok Instructions
1. Open this repository: https://github.com/Air2air/z-beam-generator
2. Load files in section order (0 → 7).
3. Treat this manifest as the minimum contract set.
4. Prefer Grok-first canonical files in `governance/`, `aggregates/`, `voices/`, and `frontmatter-templates/`.
5. Passes 2-4 and 6 depend on Grok-backed quality evaluation and fail fast if Grok-required services are unavailable.
6. Where composite quality scoring applies, preserve the published weighting contract: Grok humanness 60%, subjective quality 30%, readability 10%.
7. If a canonical file is unavailable, fall back to the listed compatibility path before requesting user intervention.

## 9) Related Frontmatter Repo (Minimum)
Use the production website repo frontmatter folder at https://github.com/Air2air/z-beam/tree/main/frontmatter for output shape/reference only after loading generator contracts above.
