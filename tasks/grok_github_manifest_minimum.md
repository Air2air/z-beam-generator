# Grok GitHub Manifest (Minimum Required)

Generated: 2026-03-07
Repository: https://github.com/Air2air/z-beam-generator
Scope: Minimum required files only (not full project) for Grok to understand and run core generation logic.

## 1) Core Runtime + Generation Pipeline
- run.py
- generation/core/evaluated_generator.py
- generation/core/generator.py
- shared/text/utils/prompt_builder.py

## 2) Required Governance / Rules
- .github/copilot-instructions.md
- docs/QUICK_REFERENCE.md

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
- shared/voice/profiles/indonesia.yaml
- shared/voice/profiles/italy.yaml
- shared/voice/profiles/taiwan.yaml
- shared/voice/profiles/united_states.yaml

## 6) Required Source Data (Essentials)
- data/materials/Materials.yaml
- data/materials/MaterialApplications.yaml
- data/materials/IndustryApplications.yaml
- data/associations/MaterialApplicationRelationships.yaml
- data/associations/DomainAssociations.yaml
- data/applications/Applications.yaml
- data/authors/Authors.yaml
- data/settings/Settings.yaml

## 7) Required Schemas
- data/schemas/content_generation_policy.yaml
- data/schemas/component_single_line_prompts.yaml
- data/schemas/frontmatter.json

## 8) Grok Instructions
1. Open this repository: https://github.com/Air2air/z-beam-generator
2. Load files in section order (1 → 7).
3. Treat this manifest as the minimum contract set.
4. If any file here is unavailable, request it before generating output.

## 9) Related Frontmatter Repo (Minimum)
- Repo: https://github.com/Air2air/z-beam/tree/main/frontmatter
- frontmatter/materials/
- frontmatter/applications/
- frontmatter/settings/

Use these frontmatter folders for output shape/reference only after loading generator contracts above.
