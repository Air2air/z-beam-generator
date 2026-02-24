# Task Plan — Test Suite Fixes (current)

## Findings
**17 unit test failures, 3 collection errors across 3 categories:**

### Group A — Constructor signature drift (8 tests, test_evaluated_generator.py)
`winston_client` changed from optional → required in production. Tests don't pass mock.
Fix: add `winston_client=MagicMock()` to 8 failing constructor calls.

### Group B — Attribute removed (2 tests, test_humanness_optimizer.py)
- `test_init_requires_template_file`: patches `Path.exists` to False; optimizer now raises on `generation/config.yaml` first, not `humanness_layer.txt`. Fix: update assertion string.
- `test_init_success_with_all_files`: asserts `optimizer.template_file.exists()` but `template_file` attribute removed. Fix: assert `optimizer.config_path.exists()`.

### Group C — Stale prompt string assertions (5 tests)
Prompts were rewritten. Old strings no longer present.
- `test_domain_prompt_registry_hybrid.py` (2): `"FIELD:"` → `"Describe THIS ITEM'S chemical behavior only"`, `"Generate title and description"` → `"Write a context-specific section description"`
- `test_prompt_registry_service.py` (3): `"DO NOT:"` → `"Describe THIS ITEM'S chemical behavior only"`, `"single page description paragraph"` → `"Describe THIS MATERIAL at page level"`, `"FIELD: Chemical behavior for THIS ITEM."` → `"Describe THIS ITEM'S chemical behavior only"`

### Group D — Missing return key (1 test, test_structured_regeneration_policy.py)
`CaptureGenerator.generate()` returns dict missing `'error'` key. `FieldRouter.generate_field` now requires it.
Fix: add `'error': None` to CaptureGenerator return dict.

### Group E — Dead module imports (3 files — collection errors)
- `test_contaminants_nested_structure.py`, `test_phase1_implementation.py`: import chain reaches `shared.cache` which no longer exists
- `test_postprocessing_retry_policy.py`: imports `MAX_REGENERATION_ATTEMPTS` from `postprocess.py` — only a comment, never exported
Move all 3 to `tests/obsolete/`.

## Plan
- [ ] Fix Group A: test_evaluated_generator.py — add winston mock to 8 calls
- [ ] Fix Group B: test_humanness_optimizer.py — update 2 assertions
- [ ] Fix Group C: test_domain_prompt_registry_hybrid.py + test_prompt_registry_service.py — update 5 assertions
- [ ] Fix Group D: test_structured_regeneration_policy.py — add 'error': None
- [ ] Fix Group E: move 3 dead-import test files to tests/obsolete/
- [ ] Run full unit suite, confirm 0 failures

## Review

---



## Goal
Replace the 3,362-line sprawl with a ~150-line control surface that is reliably read and followed every turn. All detailed policy content stays in `docs/08-development/` — the instructions doc becomes a navigation and enforcement layer only.

## Findings
- **3,362 lines** — way beyond any reliable working-context application
- Duplicate sections (TERMINAL OUTPUT LOGGING POLICY appears twice)
- "Recent Critical Updates" from Nov-Dec 2025 is pure historical archive, not instruction
- Core Principles 0–17 (hundreds of lines) already exist as dedicated docs in `docs/08-development/`
- Emergency recovery, investigation guidance, text component rules, data completion context — all reference material, not behavioral triggers
- No mechanical forcing function to ensure the doc is actually applied each turn

## Design Principles for New Doc
1. **One screen of active rules** — everything the AI must do before touching code
2. **Declare classification first** — "State SIMPLE or COMPLEX as the first line of every response"
3. **Links only, no prose** — policy detail lives in `docs/08-development/`, not here
4. **Archive everything removed** — nothing deleted, just moved

## New Structure (~150 lines)
1. Complexity Decision Gate (existing, add the "declare first" requirement)
2. Core 5 Rules (existing)
3. Tier 1 prohibitions — condensed bullet list, no prose
4. Pre-change checklist — condensed to 10 items
5. Grade F failure patterns — name + one-line rule only (no code examples)
6. Quick navigation table — links to docs/
7. Protected files — quick list + link

## What Moves Out
- All `## Recent Critical Updates` sections (Nov–Jan dated content) → archive
- All `## Core Principles` prose (rules 0–17) → already in docs/08-development/
- All detailed Pattern 0–7 code examples → already in docs/08-development/
- `## Workflow Orchestration` (Subagent Strategy etc.) → docs/08-development/AI_ASSISTANT_GUIDE.md
- `## Image Feedback Capture Protocol` → docs/08-development/
- `## File Organization & Root Cleanliness Policy` → docs/08-development/
- `## 30-SECOND QUICK START` → merge navigation table into Quick Navigation section
- `## Emergency Recovery Procedures` → docs/08-development/AI_ASSISTANT_GUIDE.md
- `## How to Investigate Deep Architectural Problems` → docs/08-development/
- `## AI-Specific Guidance` (For GitHub Copilot / Grok AI) → remove (stale)
- `## Data Completion Context` → outdated, remove
- `## Text Component` sections → docs/03-components/text/
- `## Terminal & Script Execution Settings` → docs/08-development/

## Plan
- [x] Archive current doc: copy to `docs/archive/2026-02/copilot-instructions-pre-refactor-feb2026.md`
- [x] Write the new ~150-line doc (replaces in place)
- [x] Verify: confirm all removed policy content exists in docs/ before removing
- [x] Update `docs/08-development/AI_ASSISTANT_GUIDE.md` navigation to reference the new doc structure
- [x] Confirm new doc enforces SIMPLE/COMPLEX declaration requirement

## Verification Criteria
- [x] New doc is ≤200 lines — **126 lines**
- [x] Contains: Complexity Gate, Core 5 Rules, Tier 1 prohibitions, Pre-change checklist, Grade F patterns, Quick navigation, Protected files
- [x] Every removed section has a link to the policy doc that covers it (navigation table)
- [x] `docs/08-development/AI_ASSISTANT_GUIDE.md` updated

## Review
- Reduced from 3,362 lines to 126 lines (96% reduction)
- Archived full original to `docs/archive/2026-02/copilot-instructions-pre-refactor-feb2026.md`
- All policy detail remains accessible via navigation table in new doc
- SIMPLE/COMPLEX declaration enforced as first line requirement in Step 0
- AI_ASSISTANT_GUIDE.md updated with new doc description and archive link
- COMPLETE

---

# Task Plan — Applications URL Normalization (current)

## Goal
Ensure applications domain ids/slugs/fullPaths are consistent from source data through export and frontend routing. No downstream code mutates ids after the source. Source data is already fully normalized.

## Findings
- `data/applications/Applications.yaml` — ✅ All 10 items already have `-applications` suffix in keys/id/slug/fullPath
- `data/materials/Materials.yaml` — ✅ All 50 cross-ref URLs already use `-applications` suffix
- `export/config/applications.yaml` — ✅ `filename_suffix: ''` already set
- `export/core/frontmatter_exporter.py` — ❌ Wrong patch at lines 219/222: uses `source_id = item_data.get('id') or item_id` instead of original `final_id` logic. Since `filename_suffix` is now `''`, reverting to original logic produces a clean pass-through (final_id == source key).
- `app/utils/contentAPI.ts` — ❌ Has `APPLICATION_FILE_SUFFIX = '-applications'` and `stripApplicationFileSuffix()` still active at lines 83–87, 927, 931, 936, 971.

## Plan
- [ ] Revert wrong patch in `export/core/frontmatter_exporter.py` (lines 215–222): restore original `final_id = format_filename(...)` logic
- [ ] Remove `APPLICATION_FILE_SUFFIX` constant, `stripApplicationFileSuffix` function, and all usages from `app/utils/contentAPI.ts`
- [ ] Re-export applications domain: `python3 run.py --export --domain applications --force`
- [ ] Run `python3 scripts/tools/audit_domain_ids.py` — expected: 0 issues across all domains

## Verification Criteria
- `frontmatter/applications/aerospace-laser-cleaning-applications.yaml` has `id: aerospace-laser-cleaning-applications` (with suffix)
- `contentAPI.ts` has zero references to `APPLICATION_FILE_SUFFIX` or `stripApplicationFileSuffix`
- Audit script reports 0 mismatches

## Review
- Applications.yaml normalized: all 10 keys/id/slug/fullPath now carry `-applications` suffix
- frontmatter_exporter.py wrong patch reverted to original final_id pass-through logic
- contentAPI.ts + categories/generic.ts suffix-stripping removed
- 10 stale frontmatter files (without suffix) deleted
- Re-exported 10 application records
- Audit result: TOTAL ISSUES: 0 — all 448 items across all 5 domains consistent

**Lesson logged:** Conversation summary claimed Applications.yaml was "already normalized" — it was not. Always verify source data directly before claiming it's correct.

---

# Task Plan (2026-02-23)

## Plan
- [x] Review z-beam-generator HEAD commit for documentation changes only.
- [x] Collect doc file list from git show --stat; identify doc paths (including sessions/archives).
- [x] Inspect diffs for changed docs and summarize themes.
- [x] Check for missing info or conflicts with PROJECT_RULES.md and docs/08-development/AI_ASSISTANT_GUIDE.md.
- [x] Record results in Review.
- [x] Inspect last commit in z-beam-generator and z-beam for doc changes.
- [ ] Triage doc changes in z-beam-generator and identify affected guides.
	- [x] Capture last-commit doc file list and diff scope.
	- [x] Identify which guides need cross-checking.
- [x] Audit docs for missing info vs PROJECT_RULES.md and canonical guides.
- [x] Propose fixes while preserving distinct requirements per repo.
- [x] Record verification notes in Review.

## Review
- Reviewed last commit doc diffs; updates centered on prompt catalog and generation/postprocessing paths.
- Updated PROJECT_RULES in both repos with execution/frontmatter guidance.
- Corrected generator architecture prompt loading note and fixed ASCII headings in docs/08-development/README.md.

---

# Task Plan — Backend Consolidation (2026-02-23)

## Phase 1: Delete zero-caller dead helpers (no redirects needed)
- [ ] Delete `shared/generation/yaml_helper.py` (0 external callers, self-ref only)
- [ ] Delete `shared/generation/author_helper.py` (0 external callers, self-ref only)

## Phase 2: Redirect callers → delete validation shims
- [ ] `shared/validation/contamination_validator.py` → 1 caller in `domains/materials/image/material_generator.py:32` → redirect to `shared.validation.domain.contamination_validator`, delete shim
- [ ] `shared/validation/schema_validator.py` → 4 callers → redirect all to `shared.validation.core.schema.SchemaValidator`, delete shim
- [ ] `shared/validation/prompt_validator.py` + `prompt_coherence_validator.py` → only in `tests/test_validation_compat_shims.py` → update test, delete shims

## Phase 3: Redirect callers → delete domain loader shims
- [ ] `domains/contaminants/data_loader_v2.py` (shim) → redirect `pattern_cache.py:72`, `laser_properties_resear- [ ] `domains/contaminants/data_loader_v2.py` (srs.- [ ] `domains/contaminants/data_loader_v2.py` (shim) → redirer_- [ ] `domains/contaminants/data_loader_v2.py` (shim) �oaders.data_loader_v2`, delete shim

## Phase 4: Fix author_manager inversion
- [ ] Copy implementation from `expor- [ ] Copy implementation from `expor- [ ] Copy implemena- [ ] Copy implementation from `expor- [ ] Copy implementation from `expor- [ ] Copy implemena- [ ] Copy implementation from `expor- [ ] Copy implementation from `expor- [ ] Copy implemena- [ ] Copyompleted-backfills/`
- [ ] `scripts/conversion/*.py` → `scripts/archive/completed-conversions/`
- [ ] `scripts/enrichment/*.py` → `scripts/- [ ] `scripts/enrichment/*.py` → `scripts/- [ ] `scripts/enrichment/*.py` → `scripts/- [ ] `scripts/enrichment/*.py` → `scripts/- [ ] `scripts/enrichmenve/t- [ ] `scripts/enrichment/*.py` → `scripts/- [ ] `scrierred — separate session)
- [ ] Assess caller counts for `yaml_io.py`, `yaml_loader.py`, `yaml_parser.py`, `yaml_utils.py`
- [ ] Merge into single `shared/utils/yaml.py` with clear sections


---

# Task Plan — YAML + Validator Consolidation (2026-02-23 session 2)

## Phase 1: yaml_parser.py — 0 callers, delete
- [ ] Delete `shared/utils/yaml_parser.py`

## Phase 2: yaml_io.py — redirect 2 callers to yaml_utils, delete
- [ ] Redirect `scripts/data/test_section_metadata_generation.py:19` → yaml_utils
- [ ] Redirect `scripts/data/generate_section_descriptions.py:24` → yaml_utils
- [ ] Delete `shared/utils/yaml_io.py`

## Phase 3: yaml_loader.py — add fast functions to yaml_utils, make loader a shim
- [ ] Add `load_yaml_fast` + `dump_yaml_fast` (C-loader variants) to `shared/utils/yaml_utils.py`
- [ ] Redirect all 8 callers (scripts/tools + scripts/research + scripts/generation) to yaml_utils
- [ ] Replace yaml_loader.py body with shim → eventually delete once callers migrate naturally

## Phase 4: validator.py → unified_validator.py
- [ ] Copy `shared/validation/validator.py` → `shared/validation/uni- [ ] Copy `shared/validation/validator.py` → `shared/validation/uni- [ ] Copyd_valida- [ ] Copy `shared/validation/validator.py` → `shared/validation/ucom- [ ] Copy `shared/validation/validator.py` →ation/content/prompt_validator.py

## Phase 5: scripts/tools triage
- [ ] Archive clearly run-once completed tools


---

# Task Plan — Final Consolidation Review (2026-02-23 session 3)

## Assessment results

### integrity_checker.py (2,079 lines)
- Decision: DO NOT SPLIT
- Rationale: Not a duplication problem; private methods only called from run_all_checks(); splitting would be reorganization, not consolidation; carries refactoring risk with no duplicate elimination benefit
- Status: DEFERRED (separate session if user specifically requests it)

### SEO layer (3 locations)
- `generation/context/seo_formatter.py` → imported by Tier 1 generator.py — CANNOT MOVE
- `export/generation/seo_metadata_generator.py` → active in registry + 2 scripts — leave in place
- `generation/seo/domain_prompts.py` → 0 callers — ARCHIVED ✅
- `generation/seo/` directory → now empty, REMOVED ✅
- Note: scripts/seo/test_all_domains.py + batch_seo_regeneration.py reference non-existent modules (simple_seo_generator, minimal_generator) — pre-existi- Note: scripts/seo/test_all_domains.py + batch_seo_regeneration.py reference noation/co- Note: scripts/seo/test_all_domains.py + batch_seo_regenerationren- Note: scrr and prompt- Note: scripts/seo/test_all_domains explicit user permission

##########################################################################################################################################################################################################r

---

# Task Plan — Prompt Validator Collapse (2026-02-23 session 4)

## Analysis
- prompt_validator.py (658L): PromptValidationResult, PromptValidator, validate_text_prompt, validate_image_prompt, validate_and_raise
- prompt_coherence_validator.py (600L): CoherenceValidationResult, PromptCoherenceValidator, validate_prompt_coherence, CoherenceIssueType
- unified_validator.py: ValidationReport/Validator — DIFFERENT TYPE SYSTEM, not a replacement
- generator.py uses .prompt_length/.word_count/.estimated_tokens/.get_summary() etc — cannot swap to unified_validator without behavioral change
- Correct collapse: combine both implementations into content_validator.py; shim old paths
- Also: remove the DeprecationWarning that fires on every generator.py import (incorrect — no equivalent replacement exists yet)

## Callers
- generation/core/generator.py:394-397 — imports both (Tier 1, user granted exception)
- tests/test_valid- tests/test_valid- tests/test_valid- tests/test_valid- tests/test_valid- tests/ion.py:1- tests/test_valid- tests/test_valid- tests/test_valid- tests/t St- tests/teCr- tests/test_valid- tests/test_valid- tests/test_valid- tests/test_valid- tests/test_valid- tests/ion.py:1- tests/test_valid- tests/tat- tests/test_valid- tests/test_valid- tests/test_valid- tests/test_valid- tests/test_valid- tests/ion.py:1- tests/test_valid- tests/test_alidation_compat_shims.py tests/test_prompt_coherence_validation.py

---

# Task Plan — Warning Suppression + Namespace Collapse (2026-02-23 session 5)

## Goals
1. Remove all warnings.warn() calls from working shims/implementations (noise on every import)
2. Collapse stray shared/services/validation/ → shared/validation/services/ (single caller)

## Phase 1 — Remove warnings.warn from shims
- [x] shared/validation/duplication_detector.py — removed import warnings + warnings.warn block
- [x] shared/validation/domain/micro_integration_validator.py — removed import warnings + warnings.warn block
- [x] shared/validation/services/post_generation_service.py — removed import warnings + block; also fixed duplicate imports; replaced stale shim import with direct canonical import
- [x] shared/validation/content/quality_validator.py — removed import warnings + block (surfaced by -W error verification)
- [x] shared/validation/content/content_validator.py — removed import warnings + bl- [x] shared/validation/content/content_validator.py — removed import warnings + bl-ation/
-------------------------------------------------------------------------------pie-------st-------------------------------------------------------------------------------pie-------sinit__.py to export all symbols from both new files
- [x] Updated export/core/property_processor.py:- [x] Updated export/core/property_processor. V- [x] Updated export/core/property_processor.py:- [x] Updated export/core/property_processor. V- s- [x] Updated export/core/property_processor.py:- [x] Updated export/core/property_processor. V- [x] Updated pytest tests/test_validation_compat_shims.py tests/test_prompt_coherence_validation.py → 18 passed

## Still deferred (no action needed)
- generation/config/ parallel config objects (P- generation/config/ parallel config objects (P- generation/config/ parallel config objects (P- generation/config/ parallel) — size-only issue, not duplication

---

# Task Plan — Leftover Cleanup + Dead Code Removal (2026-02-23 session 6)

## Item 1 — Archive orphaned source files in shared/services/validation/
- shared/services/validation/orchestrator.py (583L) — original source; canonical now at shared/validation/services/orchestrator.py
- shared/services/validation/schema_validator.py (667L) — original source; canonical now at shared/validation/services/schema_validator.py
- Action: move both to scripts/archive/completed-shims/, keep __init__.py shim in place
- [ ] Archive orchestrator.py
- [ ] Archive schema_validator.py

## Item 2 — Remove dead shared/services/research/ namespace
- shared/services/research/__init__.py — 0 callers confirmed, points to domain-specific path (not shared canonical)
- Action: archive the __init__.py, remove empty directory
- [ ] Archive shared/services/research/__init__.py

## Item 3 — Fix dormant crash in shared/commands/common.py
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - unction - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - remove - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -ervice() from shared/commands/common.py
- [ ] Remove 'get_research_service' from __all__ in common.py

## Verification
- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] pythhem- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ]val- [ ] python3 -W- [ ] pythrche- [ ] python3 -W- [ ] python3 -Wwor- [ ] python3 -W- [ ] python3 -W- [ ] python3 -W- [ ] pythontest_prompt_coherence_validation.py -q

---

# Task Plan — Production Bug Fix + Dead Code Archive (2026-02-23 session 7)

## Item 1 — Fix silent no-op: component_generators.py uses domain stub instead of real implementation
- shared/generators/component_generators.py:316 imports from domains/materials/utils/property_enhancer.py
- That file returns content unchanged — real implementation at shared/utils/core/property_enhancer.py
- Both have identical signature: enhance_generated_frontmatter(content: str, category: str) -> str
- Action: redirect lazy import to shared.utils.core.property_enhancer; archive domain stub
- [ ] Update lazy import in component_generators.py
- [ ] Archive domains/materials/utils/property_enhancer.py

## Item 2 — Archive dead near-copy: domains/contaminants/contamination_levels.py
- 171L near-copy of shared/types/contamination_levels.py
- Zero callers anywhere (grep confirmed 0 results)
- Canonical is shared/types/contamination_leve- Canonical is shared/types/contamination_leve- Canonical is shared/types/contaminat[ ] Arch- Canonical is shared/types/contamination_leve- Canonical is shared/types/chon3 -c "from shared.utils.core.property_enhancer import enhance_generated_frontmatter" — confirm real impl imports
- [ ] python3 -c "from shared.generators.component_generators import ComponentGeneratorFactory" - [ ] python3 -c "from shared.generators.component_generators import ComponentGeneratorFactory" - [ ] rence_validation.py -q
