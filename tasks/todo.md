# tasks/todo.md

All prior phase plans (Sessions 1–9) completed and removed 2026-02-24.
See `tasks/lessons.md` for lessons learned.

---

## Batch 166: E2E Prompt/Generator Simplification + Runtime Gate In-Process Refactor
Date: 2026-03-03
Status: COMPLETE

### Goal
Implement all identified near-term E2E optimizations: run runtime prompt gate in-process, unify text field config access, and harden prompt length-target validation semantics.

### Steps
- [x] Refactor runtime prompt gate path in `run.py` to execute in-process and reuse runtime context
- [x] Consolidate text-field config resolution behind one shared accessor used by prompt builder and component spec resolution
- [x] Harden duplicate word-target validator to detect true conflicting targets while ignoring range+cap style phrasing
- [x] Run one runtime-gated verification command for representative applications pageDescription
- [x] Record lessons learned

---

## Batch 165: Single Word-Target Enforcement + E2E System Audit
Date: 2026-03-03
Status: COMPLETE

### Goal
Eliminate duplicate word-target warnings in final prompt validation and evaluate end-to-end optimization/simplification opportunities across prompt, generator, and processing flows.

### Steps
- [x] Trace duplicate word-target source in assembled prompt output
- [x] Patch centralized length instruction formatting to emit one numeric word target
- [x] Verify runtime-gated generation passes with clean prompt validation warning state
- [x] Audit prompt/generator/runtime-gate flow for optimization opportunities
- [x] Summarize prioritized simplification roadmap

---

## Batch 164: Per-Field Config-Driven Word Limits in Shared Generator
Date: 2026-03-03
Status: COMPLETE

### Goal
Implement centralized per-field word-limit resolution in shared prompt generation, using `generation/text_field_config.yaml` as source of truth.

### Steps
- [x] Add prompt-builder field config resolver (exact key, alias, nested suffix handling)
- [x] Use resolved per-field base length for injected WORD LENGTH instructions
- [x] Add optional per-field randomization factor override support
- [x] Align `pageDescription` base length in centralized config to long-form expectations
- [x] Run one runtime-gated verification command
- [x] Record lessons learned

---

## Batch 163: Prompt Layer Dedup + All-Domain WORD LENGTH Cleanup
Date: 2026-03-03
Status: COMPLETE

### Goal
Reduce runtime duplication across descriptor/text/optimizer layers and remove field-level hardcoded WORD LENGTH/HARD LIMIT lines from domain text prompts so dynamic centralized length control is the single source of truth.

### Steps
- [x] Audit prompt layer composition and identify redundancy points
- [x] Implement safe runtime deduplication in prompt composition
- [x] Remove field-level WORD LENGTH/HARD LIMIT lines from all domain text prompt files
- [x] Run one gated verification command on a representative item
- [x] Record lessons learned

---

## Batch 162: Live Runtime-Gate Stability Check (Defense PageDescription)
Date: 2026-03-03
Status: COMPLETE

### Goal
Validate runtime quality-gate stability after evaluator calibration using isolated live generation for defense applications pageDescription.

### Steps
- [x] Run live generation with runtime prompt gate enabled
- [x] Fix blocking YAML parse error in text field config
- [x] Re-run isolated field generation with `--no-text-bundle`
- [x] Capture pass/fail outcomes across multiple runs
- [x] Record lessons learned

---

## Batch 161: Quality Criteria Calibration (Strictness vs False Positives)
Date: 2026-03-03
Status: COMPLETE

### Goal
Calibrate shared quality-evaluation criteria to preserve strict AI-detection while reducing false-positive failures from isolated weak signals.

### Steps
- [x] Define focused optimization scope for quality criteria calibration
- [x] Update quality criteria wording in shared prompt sections
- [x] Validate quality prompt retrieval after calibration
- [x] Record lessons learned

---

## Batch 160: Granularize Shared Quality Evaluation Prompt
Date: 2026-03-03
Status: COMPLETE

### Goal
Split the shared quality evaluation prompt into ordered concern-specific sections and compose at runtime with strict validation.

### Steps
- [x] Identify remaining monolithic shared quality evaluation block
- [x] Add ordered quality evaluation sections to shared prompt registry
- [x] Compose quality evaluation prompt from sections in prompt registry service
- [x] Verify composed prompt retrieval and compile checks
- [x] Record lessons learned

---

## Batch 159: Domain-Scoped Random Non-Repeating Variation Patterns
Date: 2026-03-03
Status: COMPLETE

### Goal
Ensure variation patterns are selected randomly within each domain and avoid repeating the same pattern consecutively.

### Steps
- [x] Add domain-scoped non-repeating variation pattern selection in generator runtime
- [x] Add centralized variation pattern bank and factor bands in text field config
- [x] Thread selected variation pattern through prompt assembly and requirements
- [x] Verify pattern sequencing behavior and factor-band wiring with focused runtime checks
- [x] Record lessons learned

---

## Batch 158: Global Per-File Field Variation Mixing
Date: 2026-03-03
Status: IN PROGRESS

### Goal
Apply variation improvements globally by mixing field-specific length bands within each domain prompt file.

### Steps
- [ ] Audit domain text prompt files for repeated/uniform length ranges
- [ ] Apply mixed length-band tiers to long-form fields across all core domains
- [ ] Run targeted cross-domain generation smoke checks
- [ ] Measure and summarize post-change variation behavior
- [ ] Record lessons learned

---

## Batch 157: Increase Defense Description Variation
Date: 2026-03-03
Status: COMPLETE

### Goal
Increase cross-field variation for defense application long-form descriptions without direct frontmatter edits.

### Steps
- [x] Measure current variation metrics in defense applications frontmatter
- [x] Regenerate target long-form fields via canonical batch pipeline
- [x] Apply source-level prompt length-band differentiation for applications description fields
- [x] Re-run targeted regeneration and verify updated variation metrics
- [x] Record lessons learned

---

## Batch 156: Default Generation Speed Optimization
Date: 2026-03-03
Status: COMPLETE

### Goal
Identify and implement all high-impact opportunities to speed default generation while preserving quality gates and source-of-truth policies.

### Steps
- [x] Profile baseline default generation runtime and stage breakdown
- [x] Identify avoidable overhead in prompt build/validation/evaluation paths
- [x] Implement safe speed optimizations in core generation path
- [x] Apply explicit fast-default flags to non-canonical task/script generation entrypoints
- [x] Run targeted before/after benchmark and quantify improvements
- [x] Record lessons learned and residual opportunities

---

## Batch 142: Remove Generation + SEO Truncation
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Disable generation smart truncation and remove SEO export truncation for titles/descriptions/excerpts across the project.

### Steps
- [x] Inspect generation + export truncation paths and confirm exact call sites
- [x] Disable generation smart truncation via config or guarded behavior
- [x] Remove SEO truncation in export generators while preserving validation/logging
- [ ] Run targeted generation/export smoke check to verify no truncation
- [ ] Record any new lessons learned

---

## Batch 143: Global Variation for Descriptions
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Increase structural variation for all `pageDescription` and `sectionDescription` outputs globally.

### Steps
- [x] Locate shared prompt sources for pageDescription and sectionDescription
- [x] Adjust global prompt instructions to increase structural variation
- [x] Regenerate a representative item and export for verification
- [x] Compare description structure metrics to confirm increased variation
- [ ] Record any new lessons learned

---

## Batch 144: Domain Optimizer Prompt Files
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Add per-domain optimizer prompt files and append them to the prompt chain after existing prompts.

### Steps
- [x] Define optimizer prompt file format and content
- [x] Add optimizer prompt files to each domain prompts folder
- [x] Wire optimizer_prompts_file into each domain prompt contract
- [x] Append optimizer prompt in prompt registry service
- [x] Update domain bootstrap validation for optional optimizer prompt file
- [ ] Run a targeted generation to confirm optimizer prompt inclusion

---

## Batch 145: Applications Generation + Variation Audit (3 Items)
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Run full text generation for three application items and measure description-field variation.

### Steps
- [x] Confirm which three application items to regenerate
- [x] Regenerate full application fields for those items
- [x] Export those items to frontmatter
- [x] Measure variation across description fields
- [ ] Record any new lessons learned

---

## Batch 146: Generate All Text Fields (Global)
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Ensure batch generation covers all configured text fields across all domains.

### Steps
- [x] Inventory text-field lists and full-page bundles per domain
- [x] Identify gaps between configured fields and generated outputs
- [x] Patch global generation routing to include all text fields
- [ ] Regenerate one item per domain to confirm coverage
- [ ] Record any new lessons learned

---

## Batch 147: Enforce Length Settings During Generation
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Ensure generated text follows word-length instructions in prompts and settings.

### Steps
- [x] Audit current length-control path and prompt range parsing
- [x] Decide enforcement strategy (smart truncation vs regenerate-on-length-fail)
- [x] Implement minimal enforcement changes and keep config policy compliant
- [ ] Regenerate one applications item to verify length compliance
- [ ] Record any new lessons learned

---

## Batch 148: Disable Truncation + Strengthen Prompt Word Counts
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Disable all truncation and tighten word-count compliance through prompt wording.

### Steps
- [x] Disable smart truncation in generation config
- [x] Propose prompt wording changes to strengthen word-count adherence
- [x] Apply prompt wording updates for applications
- [ ] Record any new lessons learned

---

## Batch 149: Enforce Cross-Field Opening Diversity
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Increase structural variation by enforcing distinct opening styles across fields in the same item.

### Steps
- [x] Add opening-style bank to shared prompt registry
- [x] Inject opening-style guidance into prompts per field
- [x] Ensure per-item opening styles do not repeat
- [ ] Regenerate one applications item to verify variation
- [ ] Record any new lessons learned

---

## Batch 150: Reduce Prompt Size + Validation Overhead
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Reduce prompt size and validation overhead without changing output intent or generation flow.

### Steps
- [x] Switch facts input to formatted digest for prompt injection
- [x] Shorten shared text prompt core guidance
- [x] Gate optimizer prompt injection for short fields
- [x] Skip coherence validation for short fields
- [x] Avoid auto-optimization when only warnings are present
- [x] Remove duplicate WORD LENGTH lines from optimizer prompts
- [x] Run a targeted prompt build or generation sanity check
- [ ] Record any new lessons learned

---

## Batch 151: Optimizer Prompt Context + Variability
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Add context-aware optimizer guidance to deepen subject relationships and increase structural/length variability.

### Steps
- [x] Add context + variability note to optimizer prompts (all domains)
- [x] Ensure no duplicate length hard limits are reintroduced
- [ ] Record any new lessons learned

---

## Batch 152: Disable Text Bundles for Batch Generate
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Allow --batch-generate to run only the explicitly requested text field(s) without auto-bundling.

### Steps
- [x] Add a flag to disable text bundle expansion and FAQ auto-append
- [x] Run targeted batch generation with the flag to confirm field isolation
- [ ] Record any new lessons learned

---

## Batch 153: Prompt Size Architecture
Date: 2026-03-03
Status: IN PROGRESS

### Goal
Keep runtime prompts small and usable while preserving voice fidelity and variation.

### Steps
- [x] Add compact voice instructions to all personas and use for short fields
- [x] Add config-driven compact voice field list and enforce fail-fast if missing
- [x] Ensure compact humanness + compact voice are used for pageTitle/pageDescription
- [x] Re-run pageTitle/pageDescription generation and verify prompt gate passes
- [ ] Record any new lessons learned

---

## Batch 154: Export Defense Application Frontmatter
Date: 2026-03-03
Status: IN PROGRESS

### Goal
Generate and export frontmatter for defense-laser-cleaning-applications from source data.

### Steps
- [ ] Review application source data and export config paths
- [ ] Run targeted generation for required fields and export the item
- [ ] Verify exported frontmatter output exists and matches expected schema
- [ ] Record any new lessons learned

---

## Batch 155: Prompt Length Enforcement + Default Length Gate
Date: 2026-03-03
Status: IN PROGRESS

### Goal
Reinforce prompt length instructions and make the length-only retry gate the default behavior.

### Steps
- [x] Identify prompt files that define length rules for target components and add mandatory length wording
- [x] Add a length-only retry gate that runs immediately after generation and before other validations
- [x] Make the length-only retry gate the default via config/flags (no smart truncation)
- [ ] Run a targeted generation to confirm length gate retries and logging
- [ ] Record any new lessons learned

## Batch 140: Defense Page Re-regen + Sequential Export Sync
Date: 2026-03-02
Status: COMPLETE

### Goal
Fix stale frontmatter sync and truncated defense page description by running targeted regeneration and export in strict sequence, then verifying frontmatter fields.

### Steps
- [x] Regenerate `pageDescription` for `defense-laser-cleaning-applications`
- [x] Export the same item after regeneration completes
- [x] Verify frontmatter `pageTitle` no longer carries markdown hash prefix and `pageDescription` is not truncated
- [x] Mark batch complete and capture lesson about sequencing generate/export commands

---

## Batch 141: Fix pageTitle Hash Prefix + pageDescription Truncation
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Strip markdown heading prefixes from pageTitle and prevent unintended pageDescription truncation during generation/save/export.

### Steps
- [ ] Identify where pageTitle/pageDescription normalization and length control occur
- [ ] Patch normalization to strip heading prefixes for pageTitle
- [ ] Adjust length control to avoid over-truncating pageDescription outputs
- [ ] Regenerate defense application fields and export
- [ ] Verify frontmatter reflects corrected pageTitle and full pageDescription
- [ ] Record lesson learned if a new failure pattern appears

---

## Batch 139: Regenerate Defense Applications Page (Retry)
Date: 2026-03-02
Status: COMPLETE

### Goal
Regenerate text for `defense-laser-cleaning-applications`, export it, and verify the resulting frontmatter reflects a fresh generation pass.

### Steps
- [x] Run targeted regeneration task for defense applications page text
- [x] Re-export `defense-laser-cleaning-applications` to frontmatter
- [x] Verify frontmatter changed (for example `dateModified` and regenerated text fields)
- [x] Mark batch complete and record lessons only if a new failure pattern appears

---

## Batch 138: Targeted Runtime Smoke Export (Applications)
Date: 2026-03-02
Status: COMPLETE

### Goal
Run one targeted runtime generation/export smoke check on applications and verify frontmatter output integrity after normalization refactor.

### Steps
- [x] Execute single-item applications export task for `defense-laser-cleaning-applications`
- [x] Confirm export command completes successfully with no contract/runtime errors
- [x] Verify destination frontmatter file exists and contains canonical section metadata shape
- [x] Mark batch complete and record any lesson if a new issue pattern is found

---

## Batch 137: Remove Tier-Based File Protection Policy
Date: 2026-03-03
Status: COMPLETE

### Goal
Remove tier-based protected-file gating and align guidance docs to a no-tier, validation-focused policy.

### Steps
- [x] Replace `.github/PROTECTED_FILES.md` tier protocol with advisory high-impact guidance
- [x] Update `.github/PROMPT_CREATION_ENFORCEMENT.md` to remove tier references and permission-gate language
- [x] Update `.github/copilot-instructions.md` to remove tier/protected-file gating and keep high-impact validation guidance
- [x] Run targeted doc grep checks to verify tier language removal in active `.github` policy docs
- [x] Record lesson learned and mark batch complete

---

## Batch 136: Global Section Text Normalization Across Source + Generators
Date: 2026-03-03
Status: COMPLETE

### Goal
Enforce cross-domain normalization so section text leaf fields are always persisted as plain strings in source YAML and frontmatter sync/export write paths.

### Steps
- [x] Add shared write-path normalization for text leaf targets in domain adapter save flow
- [x] Normalize frontmatter sync writes for nested text leaf targets to prevent object passthrough
- [x] Strengthen export normalization for section metadata leaves and wrapper-string artifacts
- [x] Run focused cross-domain validation/audits and verify no regressions
- [x] Record lesson learned and mark batch complete

---

## Batch 135: Applications Section Description Type-Safety Render Fix
Date: 2026-03-02
Status: COMPLETE

### Goal
Fix runtime rendering crash on applications pages when `_section.sectionDescription` is stored as structured data instead of a plain string.

### Steps
- [x] Trace the renderer path causing `section?.sectionDescription?.trim is not a function`
- [x] Apply minimal UI-layer normalization so section descriptions are rendered safely for both string and object forms
- [x] Verify `/applications/defense-laser-cleaning-applications` renders without runtime error
- [x] Record lesson learned and mark batch complete

---

## Batch 134: Fast Learning Eval Bypass for Grok Humanness Detection
Date: 2026-03-02
Status: COMPLETE

### Goal
Make default fast learning mode (`--fast-learning-eval`) bypass long post-save Grok humanness detection so established-generation runs complete much faster.

### Steps
- [x] Patch `QualityEvaluatedGenerator` to skip Grok humanness detection when `skip_learning_evaluation=True`
- [x] Run focused smoke generation and verify skip path is active
- [x] Record lesson learned and mark batch complete

---

## Batch 133: Wire Full-Page Field Contract Test into Canonical Pipeline
Date: 2026-03-02
Status: COMPLETE

### Goal
Ensure the full-page generated-field contract test executes as part of canonical validation, not only when run manually.

### Steps
- [x] Add full-page field contract pytest check to canonical validation sequence
- [x] Run canonical pipeline and verify the new check executes and passes
- [x] Record lesson learned and mark batch complete

---

## Batch 132: Full-Page Field List Contract Test
Date: 2026-03-02
Status: COMPLETE

### Goal
Add automated testing coverage that locks the canonical full-page text-generation field list per domain to prevent drift.

### Steps
- [x] Add a domain contract test for full-page generated fields from backfill configs
- [x] Run the new test and confirm it passes
- [x] Record lesson learned and mark batch complete

---

## Batch 131: SectionTitle Pairing Fix in Full-Page Backfill Writer
Date: 2026-03-02
Status: COMPLETE

### Goal
Fix source-level section title autofill so every generated `_section.sectionDescription` in full-page backfill writes is paired with `_section.sectionTitle` from canonical schema metadata.

### Steps
- [x] Trace pairing logic in universal text backfill writer
- [x] Patch schema loading/title extraction to canonical `sections.*.sectionTitle` keys
- [x] Run focused nested-field smoke check for sectionDescription→sectionTitle autofill
- [x] Re-run canonical validation and confirm all checks pass
- [x] Record lesson learned and mark batch complete

---

## Batch 130: Cross-Domain Smoke Test + Canonical Text Prompt Alignment
Date: 2026-03-02
Status: COMPLETE

### Goal
Run targeted runtime smoke tests across all core domains and confirm domain text prompt contracts remain canonically aligned to router/backfill expectations.

### Steps
- [x] Run canonical text-prompt contract validators
- [x] Run one-item dry-run generation smoke test per domain
- [x] Patch any prompt-key or contract drift found during smoke tests
- [x] Re-run canonical validation and confirm all checks pass
- [x] Record lesson learned and mark batch complete

---

## Batch 129: Field Parity Validator Compatibility Key Allowlist
Date: 2026-03-03
Status: COMPLETE

### Goal
Unblock canonical pipeline validation by aligning field-parity validator behavior with existing compatibility key exclusions in applications prompt contracts.

### Steps
- [x] Run canonical validation and capture failing check
- [x] Patch parity validator so excluded compatibility keys are not reported as extra prompt fields
- [x] Re-run canonical validation and confirm all checks pass
- [x] Record lesson learned and mark batch complete

---

## Batch 128: Applications Section Metadata Text Generation Parity
Date: 2026-03-02
Status: COMPLETE

### Goal
Ensure applications batch generation routes `sectionTitle` and `sectionDescription` through the canonical text-generation pipeline so these fields generate alongside other text fields.

### Steps
- [x] Trace applications batch generation flow and identify why section metadata fields are excluded
- [x] Patch the minimal source-path logic so section metadata fields are included in text generation routing
- [x] Run focused verification for applications batch generation behavior
- [x] Record lesson learned and mark batch complete

---

## Batch 127: All-Domain Catalog Keyword Parity + Global Subject Placeholder
Date: 2026-03-02
Status: COMPLETE

### Goal
Ensure parity across all domains by normalizing all domain catalogs to subject keywords, extending validator normalization to every domain, and applying a global `subject` template placeholder mapping in prompt assembly.

### Steps
- [x] Add global `subject` template parameter mapping in prompt assembly
- [x] Extend catalog keyword normalization logic in validator for all domains
- [x] Normalize `article_pages.file_names` to subject keywords in all domain catalogs
- [x] Re-run canonical pipeline validation and confirm all checks pass
- [x] Run focused runtime checks for cross-domain keyword resolution and single-item generation path

---

## Batch 126: Catalog Subject Keyword Contract (Applications)
Date: 2026-03-02
Status: COMPLETE

### Goal
Switch applications catalog `article_pages.file_names` to subject keywords (for example `food-processing`) and update validation logic so keyword entries are treated as canonical catalog identifiers.

### Steps
- [x] Add keyword normalization helper in prompt/section contract validator
- [x] Update catalog/frontmatter parity check to compare normalized subject keywords
- [x] Convert `domains/applications/catalog.yaml` entries to subject keywords
- [x] Run canonical pipeline validation and confirm all checks pass
- [x] Record lesson learned and mark batch complete

---

## Batch 125: Generated Text Contract Artifact + Validator
Date: 2026-03-02
Status: COMPLETE

### Goal
Create a generated text-contract artifact from router/backfill sources and enforce parity through a dedicated validator integrated into the canonical pipeline gate.

### Steps
- [x] Implement shared contract computation utility from router/backfill sources
- [x] Add artifact generator script and write deterministic contract artifact to `tasks/`
- [x] Add validator to compare live contract vs artifact and enforce required prompt-key coverage
- [x] Integrate validator into canonical pipeline check sequence
- [x] Run full canonical validation and confirm all checks pass
- [x] Record lesson learned and mark batch complete

---

## Batch 124: Active Docs Legacy Key Hygiene Pass
Date: 2026-03-02
Status: COMPLETE

### Goal
Clean up stale legacy key naming in active user-facing architecture/reference docs so examples and field names match current canonical targets.

### Steps
- [x] Identify active (non-archive/proposal) docs with stale legacy key examples
- [x] Update those docs to canonical field naming and guidance
- [x] Re-run canonical pipeline validation as a regression safety check
- [x] Record lesson learned and mark batch complete

---

## Batch 123: Prune Unused Content Policy Aliases
Date: 2026-03-02
Status: COMPLETE

### Goal
Remove unused legacy `content_generation_policy.aliases.componentType` entries now that backfill/router mappings are canonicalized, while preserving green canonical validation.

### Steps
- [x] Verify no active backfill component_type entries depend on legacy alias keys
- [x] Remove unused alias entries from `data/schemas/content_generation_policy.yaml`
- [x] Re-run canonical pipeline validation and confirm all checks pass
- [x] Record lesson learned and mark batch complete

---

## Batch 122: Canonicalize Compounds/Settings Router Text Keys
Date: 2026-03-02
Status: COMPLETE

### Goal
Canonicalize compounds and settings `field_router.field_types.*.text` keys to canonical camelCase names and move legacy key forms into alias mappings, while preserving green canonical validation gates.

### Steps
- [x] Update compounds/settings router text key lists to canonical names and add legacy aliases
- [x] Align prompt key contracts (single-line and domain text prompts) with updated canonical router keys
- [x] Update any legacy backfill component aliases that are no longer needed
- [x] Re-run canonical pipeline validation and confirm all checks pass
- [x] Record lesson learned and mark batch complete

---

## Batch 121: Prompt Contract Simplification + Robustness Recommendations
Date: 2026-03-02
Status: COMPLETE

### Goal
Apply low-risk prompt contract simplification where redundant alias keys are no longer required, verify canonical validation remains green, and provide e2e robustness recommendations.

### Steps
- [x] Identify low-risk removable alias prompt keys not required by router/backfill validators
- [x] Apply minimal prompt cleanup changes in domain text prompt files
- [x] Re-run canonical pipeline validation and confirm all checks pass
- [x] Document lesson learned and summarize architecture recommendations

---

## Batch 120: Final Pipeline Simplification Pass
Date: 2026-03-02
Status: COMPLETE

### Goal
Reduce residual legacy fallback complexity in frontend relationship access paths and add a single canonical parity gate command for end-to-end validation.

### Steps
- [x] Identify remaining high-confidence legacy fallback branches in active frontend layout/helper paths
- [x] Remove or tighten those fallback branches where canonical coverage is complete
- [x] Add one canonical parity validator entrypoint that runs key contract/parity checks in sequence
- [x] Run focused audits/validation and summarize residual complexity

---

## Batch 119: Compounds Canonicalization and Frontend Fallback Reduction
Date: 2026-03-02
Status: COMPLETE

### Goal
Canonicalize compounds frontmatter naming/structure via source export and remove remaining compounds-specific legacy frontend fallback branches once coverage is complete.

### Steps
- [x] Re-export all compounds frontmatter from canonical source pipeline
- [x] Audit compounds frontmatter for canonical relationship key coverage
- [x] Remove compounds layout/helper legacy fallback branches only if coverage is complete
- [x] Re-run focused frontend validation and summarize residual risks

---

## Batch 118: Frontend Layout ↔ Backend Field Sync Repair
Date: 2026-03-02
Status: COMPLETE

### Goal
Align frontend layout relationship field access paths with canonical backend/frontmatter key structure to restore rendering parity.

### Steps
- [x] Identify canonical field paths used by current frontmatter for compounds, contaminants, and settings layouts
- [x] Patch frontend layout/helper field access to prioritize canonical paths while preserving safe legacy fallback behavior where needed
- [x] Run focused frontend validation checks and summarize remaining parity risks
- [x] Record lesson learned and mark batch complete

---

## Batch 117: Applications Catalog ↔ Frontmatter Parity Repair
Date: 2026-03-02
Status: COMPLETE

### Goal
Resolve applications domain catalog/frontmatter filename parity so prompt/section validation no longer fails on catalog drift.

### Steps
- [x] Inspect applications source/catalog/frontmatter filename sets to identify canonical ownership mismatch
- [x] Apply minimal source-level fix to align `domains/applications/catalog.yaml` with current canonical frontmatter set
- [x] Re-run prompt/section and field-contract validators to confirm parity repair
- [x] Record lesson and mark batch complete

---

## Batch 116: Section Key Paired Child Enforcement
Date: 2026-03-02
Status: COMPLETE

### Goal
Enforce that text prompt keys representing sections always define `sectionTitle` and `sectionDescription` together under the same section key, and align runtime/validation contracts accordingly.

### Steps
- [x] Define canonical rule to identify section keys from schema/backfill contracts
- [x] Update runtime prompt resolution to support paired section children on section keys
- [x] Update prompt contract validator to require paired section children on section keys
- [x] Normalize all domain `text_prompt.yaml` section keys to include both children
- [x] Run focused tests/validation and summarize only residual unrelated failures

---

## Batch 115: Domain-Wide Dual Audit (Prompt Contract + Frontmatter Paths)
Date: 2026-03-02
Status: COMPLETE

### Goal
Run a full domain-wide dual audit that verifies (1) domain `text_prompt.yaml` key/child correctness against router+backfill contracts and (2) expected text field paths exist across all frontmatter files per domain.

### Steps
- [x] Build expected per-domain text key + expected-child map from generation/router/backfill/schema contracts
- [x] Audit all domain `text_prompt.yaml` files for missing/extra keys and wrong child-field usage
- [x] Audit all frontmatter files per domain for missing expected text field paths and aggregate gap counts
- [x] Return concise mismatch report with per-domain totals and top missing-path offenders

---

## Batch 114: Schema-Driven Domain Text Prompt Contract Hardening
Date: 2026-03-02
Status: COMPLETE

### Goal
Accurately enforce domain-local `text_prompt.yaml` structure so required text keys are complete and each key uses the correct child prompt field (`sectionTitle` vs `sectionDescription`) based on schema/backfill contracts.

### Steps
- [x] Build canonical expected text prompt key map from router + backfill configs
- [x] Derive expected child field type per key from schema component/prompt refs and nested field-path suffixes
- [x] Normalize all `domains/*/prompts/text_prompt.yaml` files to strict nested child-field format
- [x] Tighten runtime/validator logic to require strict nested format and expected child field type
- [x] Run focused tests and validators; report only residual unrelated failures

---

## Batch 113: Prose-Only Prompt Routing and Subfield Prompt Keys
Date: 2026-03-02
Status: COMPLETE

### Goal
Ensure domain text prompt files contain prose-only fields, include required nested subfield prompt keys (for example `sectionDescription`/`sectionTitle`), and keep runtime/validators aligned to enforce the same contract.

### Steps
- [x] Classify prose vs non-prose prompt targets from schema + router contracts
- [x] Update domain prompt files to keep prose prompts in `text_prompt.yaml` and title/non-prose in `non_text_prompt.yaml`
- [x] Add explicit nested subfield keys where section subfields are required
- [x] Update shared prompt resolution to support subfield-key lookup
- [x] Update validators to enforce prose-only text prompt coverage and required subfield keys
- [x] Run focused tests/validation and summarize residual unrelated failures

---

## Batch 112: Domain Prompt Split (Text vs Non-Text) and Registry Cleanup
Date: 2026-03-02
Status: IN PROGRESS

### Goal
Move domain content prompts into each `domains/*` folder, split prompt chain field-prompt sources into exactly two files (`text` and `non-text`), enforce that only those files are used for field-prompt resolution, and remove obsolete prompt artifacts.

### Steps
- [x] Define per-domain prompt contract schema for `text_prompts_file` and `non_text_prompts_file`
- [x] Create domain-local prompt files for all supported domains with text/non-text split
- [x] Restore per-field text prompts in each domain `prompts/text_prompt.yaml` from schema/field contracts
- [x] Update shared runtime field-prompt resolution to use domain-local per-field prompt entries only
- [x] Update validators/tests to enforce all domain text fields have per-field domain prompt entries
- [x] Remove centralized field-prompt dependency from prompt-chain resolution paths
- [x] Run targeted validation tests and summarize outcomes

---

## Batch 111: Remove Orphan Root `_section` at Export Layer
Date: 2026-03-02
Status: COMPLETE

### Goal
Eliminate orphan root-level `_section` keys from exported frontmatter while preserving required nested `_section` objects on actual section containers.

### Steps
- [x] Implement export-layer root `_section` cleanup in universal content generator
- [x] Re-export affected domains from canonical source pipeline
- [x] Re-run all-domain section-object audit and confirm no missing nested `_section`
- [x] Verify orphan root `_section` lists are empty (or only approved exceptions)
- [x] Record lesson learned and finalize summary

---

## Batch 110: Source-Level Section Object Remediation (All Domains)
Date: 2026-03-02
Status: COMPLETE

### Goal
Resolve all remaining missing nested `_section` section-object violations by fixing canonical source data and/or generator normalization, then re-export and verify clean all-domain audit results.

### Steps
- [x] Identify canonical source-level causes for compounds FAQ and materials outliers
- [x] Implement source/generator fixes without frontmatter direct edits
- [x] Re-export affected compounds/materials outputs from canonical pipeline
- [x] Re-run section-object audit and confirm missing paths drop to zero
- [x] Update lessons learned with source-level remediation pattern

---

## Batch 109: Cross-Domain Field Contract Consolidation and Parity Program
Date: 2026-03-01
Status: COMPLETE

### Goal
Consolidate field contract ownership so one canonical source drives router fields, prompt coverage, field order, schema/doc outputs, and validation gates across materials, applications, contaminants, compounds, and settings.

### Steps
- [x] Define canonical contract model and ownership boundaries (source-of-truth file + generated artifacts)
- [x] Build contract sync tooling to generate downstream artifacts (prompt coverage, field-order sections, docs references)
- [x] Add parity validator with fail-fast CI gate across all domains
- [x] Establish migration sequence per domain using applications as architectural reference
- [x] Execute domain-by-domain adoption with verification checkpoints and rollback criteria
- [x] Remove/mark deprecated duplicate contract fragments once parity is enforced
- [x] Document operating policy and contributor workflow for future field additions

---

## Batch 106: JSON-LD Critical Deployment Audit and Path Hardening
Date: 2026-03-01
Status: IN PROGRESS

### Goal
Identify why deploy-time JSON-LD/SEO checks started failing now, run comprehensive JSON-LD validation, and harden deployment script paths to prevent recurrence.

### Steps
- [ ] Confirm deploy-environment trigger changes and root-cause chain (`vercel-build`, `.vercelignore`, prebuild gates)
- [ ] Audit deployment scripts for broken relative-path assumptions affecting JSON-LD validation
- [ ] Run comprehensive JSON-LD/SEO checks (`test:seo:comprehensive`, `validate:urls`, `validate:seo-infrastructure`) and capture outcomes
- [ ] Patch verified deploy-path bug(s) with minimal safe changes
- [ ] Re-run affected checks and summarize risks, findings, and next actions

---

## Batch 107: Regenerate Defense Applications Frontmatter Item
Date: 2026-03-01
Status: COMPLETE

### Goal
Regenerate and export `defense-laser-cleaning-applications` through the canonical generator pipeline so `z-beam/frontmatter/applications/defense-laser-cleaning-applications.yaml` is refreshed from source.

### Steps
- [x] Run targeted applications export for `defense-laser-cleaning-applications`
- [x] Verify frontmatter output file updated in `z-beam/frontmatter/applications/`
- [x] Sanity-check regenerated fields for expected structure/content presence
- [x] Summarize results and any residual warnings

---

## Batch 108: Restore Aluminum Properties Data and Re-Export
Date: 2026-03-01
Status: COMPLETE

### Goal
Fix missing Aluminum Material Characteristics and Laser-Material Interaction by updating source materials data and re-exporting the aluminum frontmatter item.

### Steps
- [x] Add structured `properties.materialCharacteristics` values for `aluminum-laser-cleaning` at source
- [x] Add structured `properties.laserMaterialInteraction` values for `aluminum-laser-cleaning` at source
- [x] Sync mirrored shared materials data copy
- [x] Re-export aluminum material frontmatter from generator to `z-beam/frontmatter/materials`
- [x] Verify regenerated frontmatter includes the restored property values

---

## Batch 105: Remove Project Archive Directories and Identify Follow-up Cleanup
Date: 2026-03-01
Status: COMPLETE

### Goal
Delete project archive directories on request and identify adjacent stale legacy references for follow-up cleanup.

### Steps
- [x] Inventory archive directories/files across workspace projects
- [x] Delete dedicated archive directories from project repositories
- [x] Verify no archive directory/file paths remain (excluding dependencies)
- [x] Identify similar legacy cleanup opportunities from stale references
- [x] Record lesson and summarize follow-up candidates

---

## Batch 104: Deprecate Legacy Batch Tooling and Audit Similar Cleanup Targets
Date: 2026-03-01
Status: COMPLETE

### Goal
Deprecate standalone legacy/ad-hoc batch scripts in favor of canonical `run.py --batch-generate` flows, and identify similar low-risk legacy cleanup opportunities.

### Steps
- [x] Map legacy batch entrypoints and references
- [x] Add explicit deprecation guardrails/messages for legacy batch commands
- [x] Document migration path to canonical batch generation commands
- [x] Audit nearby legacy code paths for similar cleanup opportunities
- [x] Run focused tests/validation for touched paths
- [x] Record lesson in `tasks/lessons.md` and mark batch complete

---

## Batch 103: Mandate Discrete Per-Field Requests in Batch Flows
Date: 2026-03-01
Status: COMPLETE

### Goal
Enforce and document a mandatory policy that batch flows execute as a sequence of individual discrete generation requests per item/field, never a combined multi-item prompt request.

### Steps
- [x] Identify all active batch entry points and any residual single-call batch scaffolding
- [x] Enforce discrete-request behavior in batch generation code paths
- [x] Update policy documentation to mandate discrete per-field request sequencing
- [x] Update operational docs/examples to align with the new mandate
- [x] Run focused tests for batch command and related generation paths
- [x] Record lessons learned in `tasks/lessons.md` and mark batch complete

---

## Batch 102: Enforce Runtime Prompt Gate on Generation Commands
Date: 2026-03-01
Status: COMPLETE

### Goal
Run Runtime Prompt gate automatically for text-generation commands so final assembled prompts are audited on every generation without manual invocation.

### Steps
- [x] Add runtime overrides (`--domain`, `--item`, `--provider`) to `final_prompt_audit.py`
- [x] Add default-on Runtime Prompt gate flags to `run.py`
- [x] Invoke Runtime Prompt gate automatically in `--batch-generate` text flow
- [x] Invoke Runtime Prompt gate automatically in `--seed-from-keyword` generation flow
- [x] Validate CLI/help wiring and run targeted gate execution successfully

---

## Batch 101: Final Prompt Audit Tooling with Centralized YAML Settings
Date: 2026-03-01
Status: COMPLETE

### Goal
Add a deterministic final-prompt audit workflow that validates the exact assembled prompt sent to text generation, with all thresholds and checks configured in one YAML file.

### Steps
- [x] Add `scripts/validation/final_prompt_audit.py` to assemble and validate final prompts per component
- [x] Centralize all audit settings and thresholds in `config/final_prompt_audit.yaml`
- [x] Run the audit on `defense-laser-cleaning-applications` and generate reports
- [x] Summarize usage and outcomes for prompt-change workflows

---

## Batch 100: Regenerate Defense Application and Verify Frontmatter
Date: 2026-03-01
Status: IN PROGRESS

### Goal
Regenerate `defense-laser-cleaning-applications` from source pipeline and validate the resulting frontmatter output file content in `z-beam`.

### Steps
- [ ] Run targeted regeneration for `defense-laser-cleaning-applications`
- [ ] Re-export/dual-write output to frontmatter destination if needed
- [ ] Inspect generated frontmatter file and capture updated key fields
- [ ] Summarize regeneration result and any residual validation issues

---

## Batch 99: Frontend Cleanup Audit and Low-Risk Prune (z-beam)
Date: 2026-02-28
Status: COMPLETE

### Goal
Execute approved low-risk cleanup in `z-beam` and audit for additional dead code, empty folders, and stale artifacts with actionable follow-up recommendations.

### Steps
- [x] Remove confirmed unused empty files (`app/utils/domainLinkageMapper.ts`, `types/domain-linkages.ts`)
- [x] Run focused reference checks to confirm no import/runtime regressions from removed files
- [x] Audit empty directories and obvious stale scaffolding candidates (excluding dependency/build outputs)
- [x] Summarize safe immediate deletions vs review-required candidates
- [x] Record lesson in `tasks/lessons.md` and mark batch complete

---

## Batch 98: Simplify Prompt Contract Layer to Shared Registry
Date: 2026-02-28
Status: COMPLETE

### Goal
Remove low-value empty per-domain prompt registry files and simplify prompt contract wiring to one canonical shared registry while preserving runtime behavior and validation coverage.

### Steps
- [x] Point all `domains/*/prompt.yaml` contracts to `prompts/registry/content_prompts_shared.yaml`
- [x] Update bootstrap + section-contract validators to enforce shared registry contract path
- [x] Remove redundant empty `prompts/registry/content_prompts_<domain>.yaml` files
- [x] Update focused registry unit tests for shared-backed registry loading expectations
- [x] Run focused validators/tests and summarize known residual failures

---

## Batch 97: Remove Legacy Shared Prompt Artifacts and Enforce Guard
Date: 2026-02-28
Status: COMPLETE

### Goal
Finalize prompt-chain separation of concerns by removing legacy `prompts/shared/*` prompt registries and adding validation guards so those files cannot re-enter the active runtime chain.

### Steps
- [x] Remove unused legacy shared prompt files from `prompts/shared/`
- [x] Add validation guard that fails if legacy shared prompt files are reintroduced
- [x] Run focused prompt source and section contract validations
- [x] Record lesson in `tasks/lessons.md` and mark batch complete

---

## Batch 96: Consolidate Single-Line Prompt Ownership and FAQ Source
Date: 2026-02-28
Status: COMPLETE

### Goal
Apply the recommended registry consolidation moves by removing dual-source FAQ single-line ownership and enforcing one canonical single-line source in `data/schemas/component_single_line_prompts.yaml`.

### Steps
- [x] Add FAQ single-line entries to canonical `component_single_line_prompts.yaml` for all required domains
- [x] Remove FAQ single-line duplication from shared prompt registry and stop runtime merge behavior
- [x] Update prompt-contract validation to validate FAQ single-line entries only from canonical schema source
- [x] Run focused prompt contract/source centralization validations
- [x] Record lesson in `tasks/lessons.md`, mark batch complete, and summarize residuals

---

## Batch 95: Deprecate Legacy Sitemap Config References
Date: 2026-02-28
Status: COMPLETE

### Goal
Reduce sitemap implementation fragmentation by clearly labeling legacy sitemap config/docs references (especially `seo/config/sitemap-config.json`) as documentation-only and non-runtime.

### Steps
- [x] Audit active runtime sitemap sources versus legacy sitemap config/docs references
- [x] Add explicit deprecation labeling to `seo/config/sitemap-config.json`
- [x] Update key sitemap docs to indicate canonical runtime sources and legacy status
- [x] Run focused sitemap validation checks
- [x] Commit and push the sitemap deprecation-labeling pass

---

## Batch 94: Canonicalize Single-Line Prompt Source and Tighten Descriptor Boundaries
Date: 2026-02-28
Status: COMPLETE

### Goal
Eliminate prompt-chain overlap by making `data/schemas/component_single_line_prompts.yaml` the only single-line prompt source and tightening descriptor-vs-field boundaries in shared descriptor prompts.

### Steps
- [x] Remove `one_line_content_prompts` blocks from all `domains/*/prompt.yaml` contracts
- [x] Update section-contract validator to reject domain-level single-line prompt definitions and enforce canonical schema source
- [x] Tighten shared descriptor wording to avoid overlap with field prompt responsibilities
- [x] Run focused prompt contract + bootstrap validations
- [x] Record lesson in `tasks/lessons.md` and mark batch complete

---

## Batch 93: Consolidate Prompt Chain Files Into One Folder
Date: 2026-02-28
Status: COMPLETE

### Goal
Place prompt-chain YAML sources in one canonical folder under `prompts/registry/` and rewire loaders/contracts so runtime behavior remains unchanged.

### Steps
- [x] Move shared/domain prompt-chain YAML files to `prompts/registry/`
- [x] Update prompt contract/extends and loader paths to new canonical folder
- [x] Keep compatibility by removing stale path references in validators/audits
- [x] Run focused compile + validation checks for prompt resolution
- [x] Record lesson in `tasks/lessons.md` and mark batch complete

---

## Batch 92: Dynamic Domain Commandability for Generation CLI
Date: 2026-02-28
Status: COMPLETE

### Goal
Allow generation commands to pick up newly added domains from catalog/config without additional hardcoded CLI updates.

### Steps
- [x] Replace hardcoded CLI domain lists in `run.py` with dynamic domain discovery from `domains/*/config.yaml`
- [x] Replace hardcoded backfill-domain availability text with dynamic discovery from `generation/backfill/config/*.yaml`
- [x] Update export-all domain iteration to discover configured export domains dynamically
- [x] Allow `KeywordSeedService` page-title suffix fallback for new domains not in static suffix map
- [x] Run syntax and helper smoke checks for updated commandability paths

---

## Batch 91: Regenerate Defense Prompt Chain Artifacts
Date: 2026-02-28
Status: COMPLETE

### Goal
Regenerate `tasks/prompt_chain_defense_applications.{json,md}` end-to-end using canonical prompt assembly utilities so artifact content and metadata fully reflect current shared prompt registry wiring.

### Steps
- [x] Build one-off extractor from canonical `Generator`/`PromptBuilder`/`PromptRegistryService` pipeline utilities
- [x] Regenerate both prompt-chain artifacts for `defense-laser-cleaning-applications`
- [x] Validate JSON parse and verify canonical shared registry source path strings
- [x] Mark batch complete and record lesson delta if needed

---

## Batch 90: Remove Redundant Shared Prompt Duplicates
Date: 2026-02-28
Status: COMPLETE

### Goal
Finish shared prompt centralization cleanup by removing duplicate shared core/humanness/quality prompt bodies from `prompts/registry/prompt_catalog.yaml` and keeping canonical shared prompt source in `prompts/registry/shared_prompt_registry.yaml`.

### Steps
- [x] Verify no runtime consumers require removed catalog shared core/humanness/quality keys
- [x] Remove duplicate shared core/humanness/quality prompt bodies from `prompt_catalog.yaml`
- [x] Update pipeline verification script to check consolidated shared prompt registry
- [x] Re-run focused centralization and contract validations
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 89: Consolidate Remaining Shared Prompt Bodies
Date: 2026-02-28
Status: COMPLETE

### Goal
Complete single-location shared prompt access by moving remaining shared core/humanness/quality prompt bodies to `prompts/registry/shared_prompt_registry.yaml` and routing shared getters there.

### Steps
- [x] Add shared core/humanness/quality prompt bodies to consolidated shared prompt registry
- [x] Route shared prompt getter methods in `PromptRegistryService` to consolidated shared registry keys
- [x] Run focused validation checks for centralized shared prompt wiring
- [x] Record lesson in `tasks/lessons.md` and summarize follow-up delta

---

## Batch 88: Single-Location Shared Prompt Centralization
Date: 2026-02-28
Status: COMPLETE

### Goal
Make shared prompt access easy and deterministic by moving shared section/FAQ prompt retrieval behind one canonical location: `prompts/registry/shared_prompt_registry.yaml`.

### Steps
- [x] Add canonical shared section/FAQ prompt blocks to consolidated shared prompt registry
- [x] Route `PromptRegistryService` shared prompt + FAQ reads to consolidated source
- [x] Update prompt contract validators/scripts to assert centralized shared prompt wiring
- [x] Run focused validation checks for prompt source/section contract integrity (centralization-specific checks pass)
- [x] Record lesson in `tasks/lessons.md` and summarize artifact changes

---

## Batch 87: Rendered Prompt Chain Extraction (Applications Defense Entry)
Date: 2026-03-01
Status: COMPLETE

### Goal
Produce exact rendered prompt blocks for all configured applications multi-field text components for `defense-laser-cleaning-applications`.

### Steps
- [x] Build one-off extractor using canonical prompt assembly utilities
- [x] Render schema prompt + final assembled prompt for each configured component type
- [x] Persist artifacts to `tasks/prompt_chain_defense_applications.{json,md}`
- [x] Summarize output artifact locations for user review

---

## Batch 86: End-to-End Text Field Pipeline Parity Audit
Date: 2026-02-28
Status: COMPLETE

### Goal
Ensure all text field generation flows use one reusable end-to-end pipeline with no domain/field outliers or bypass paths.

### Steps
- [x] Inventory every text field generation entrypoint and runtime path
- [x] Detect any field/domain-specific bypasses outside the canonical reusable pipeline
- [x] Refactor outliers into canonical shared flow with minimal code changes
- [x] Add/strengthen automated parity guard tests for future regressions
- [x] Run targeted and full parity verification and summarize findings

---

## Batch 85: Backend Failure Triage and Compatibility Fixes
Date: 2026-02-28
Status: COMPLETE

### Goal
Resolve the highest-impact backend test failures by fixing runtime contract mismatches first, then validating with targeted and full-suite test runs.

### Steps
- [x] Triage coordinator/test API mismatch failures
- [x] Implement minimal compatibility fixes in coordinator/runtime code
- [x] Re-run coordinator and exporter targeted tests
- [x] Triage remaining voice/deployment smoke failures
- [x] Re-run full backend pytest suite and summarize

---

## Batch 84: Full Backend Test Suite Execution
Date: 2026-02-28
Status: COMPLETE

### Goal
Run the complete backend test suite in `z-beam-generator` and report pass/fail status with failing test details if any.

### Steps
- [x] Configure Python environment for backend test execution
- [x] Run full backend pytest suite
- [x] Summarize test results and failures (if present)

---

## Batch 83: Post-Deploy GA Detection for Next Streamed HTML
Date: 2026-02-28
Status: COMPLETE

### Goal
Prevent false GA failures in post-deploy checks when Next.js injects analytics loader client-side and GA IDs are surfaced in streamed flight payload.

### Steps
- [x] Add GA detection fallback for streamed `gaId` evidence in analytics validators
- [x] Keep GA ID format and consent/CSP checks strict
- [x] Add focused analytics test coverage for streamed `gaId` extraction
- [x] Re-run analytics validator to confirm live pass
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 82: AW Production Hardening (CSP + Strict Post-Deploy Gates)
Date: 2026-02-28
Status: COMPLETE

### Goal
Make Google Ads tracking production-ready by requiring Ads collection endpoints in CSP and enforcing strict AW endpoint coverage failures in post-deploy validators.

### Steps
- [x] Enforce Ads endpoint allowlist in app and middleware CSP builders
- [x] Upgrade post-deploy AW endpoint checks from warning to required failure
- [x] Include analytics category in strict SEO gate evaluation
- [x] Update focused tests for CSP/analytics strictness
- [x] Run focused validation checks and record lesson in `tasks/lessons.md`

---

## Batch 81: GA/AW Post-Deploy Completeness + Comprehensiveness Checks
Date: 2026-02-28
Status: COMPLETE

### Goal
Strengthen post-deployment validation so Google Analytics and Google Ads checks confirm both tag presence and analytics endpoint coverage.

### Steps
- [x] Audit current post-deploy GA/AW checks for gaps
- [x] Add explicit GA/AW completeness checks in post-deploy validation scripts
- [x] Add comprehensive network endpoint checks for GA/AW requests
- [x] Update targeted tests for new GA/AW validations
- [x] Run focused validation test suite and record lesson in `tasks/lessons.md`

---

## Batch 80: Frontend GA/AW Standardization Pass (z-beam)
Date: 2026-02-28
Status: COMPLETE

### Goal
Remove GA/AW hardcoded measurement fallbacks and replace skipped analytics script assertions with stable wiring-focused tests.

### Steps
- [x] Remove hardcoded GA fallback values from frontend env/layout wiring
- [x] Keep analytics wrapper rendering conditional on required GA measurement ID
- [x] Replace skipped analytics script assertions with deterministic wrapper-prop assertions
- [x] Run focused layout test verification
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 79: Enforce Source-Complete Data Policy (No Generation-Time Enhancers)
Date: 2026-02-28
Status: COMPLETE

### Goal
Enforce mandatory policy that source data is fully accurate/populated and generation-time flows do not rely on enhancer behavior for required content, with explicit documentation and automated tests.

### Steps
- [x] Add strict validator checks for source records to reject enhancer-style deprecated root relationship title/description keys and require canonical nested section metadata
- [x] Add/adjust tests to assert policy enforcement fails for enhancer-style source patterns and passes for canonical source data
- [x] Update policy documentation to explicitly ban generation-time enhancement for missing required content and define expected source shape
- [x] Run targeted tests/validation to verify enforcement
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 78: Applications Root-Level Relationship Key Recurrence Fix
Date: 2026-02-28
Status: IN PROGRESS

### Goal
Eliminate recurrent root-level `relatedMaterials` and `contaminatedBy` fields from applications frontmatter by fixing generation-time sync mapping and cleaning the source record.

### Steps
- [ ] Patch generation-time frontmatter sync to write applications relationship components to canonical nested paths
- [ ] Add regression test covering applications relationship component sync behavior
- [ ] Remove legacy root-level relationship fields from defense source YAML record
- [ ] Re-export defense applications item and verify frontmatter no longer has root-level relationship keys
- [ ] Record lesson in `tasks/lessons.md`

---

## Batch 77: Word-Count-Only Length Guidance Consolidation
Date: 2026-02-28
Status: COMPLETE

### Goal
Remove or replace sentence-count and character-count guidance in active generation instruction paths so length guidance is word-count-only.

### Steps
- [x] Audit active generation instruction sources for sentence/character count guidance
- [x] Replace instruction-level sentence/character count guidance with word-count-only guidance
- [x] Regenerate `defense-laser-cleaning-applications` through source pipeline
- [x] Re-audit target frontmatter length variation and confirm no sentence/character count guidance remains in active paths
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 76: Applications Length Variation Hardening
Date: 2026-02-28
Status: COMPLETE

### Goal
Improve poor within-item length variation in applications long prose fields while keeping outputs shorter overall through centralized generation config (no frontmatter patching).

### Steps
- [x] Remove pageDescription sentence-based length override in humanness layer
- [x] Differentiate centralized base lengths for applications long prose fields
- [x] Regenerate defense applications text bundle from source pipeline
- [x] Re-audit frontmatter word-count variation and confirm improvement
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 75: Applications Frontmatter Legacy Field Cleanup Verification
Date: 2026-02-28
Status: COMPLETE

### Goal
Remove stale root-level `relatedMaterials` and `contaminatedBy` from applications frontmatter via source export flow and verify FAQ layout presence in applications page rendering.

### Steps
- [x] Re-export `defense-laser-cleaning-applications` from source pipeline
- [x] Verify root-level legacy relationship fields are removed in frontmatter output
- [x] Verify FAQ component rendering in applications page layout
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 74: Text Length + SectionTitle + Paragraph Integration
Date: 2026-02-28
Status: COMPLETE

### Goal
Shorten overall generated text, ensure section title fields are AI-generated in the same run flow, and add paragraph-break guidance to text generation prompts.

### Steps
- [x] Reduce centralized global text-length baseline and long-tail variation
- [x] Integrate section-title text components into same batch text run flow
- [x] Add paragraph-break generation guidance in shared text prompts
- [x] Run focused defense applications verification run
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 73: Integrate FAQ Into Batch Text Runs
Date: 2026-02-28
Status: COMPLETE

### Goal
Eliminate FAQ as a discrete batch-generation path by ensuring text-field batch runs include FAQ in the same execution flow.

### Steps
- [x] Identify batch-generation path causing FAQ to run separately
- [x] Patch batch text generation flow to include FAQ alongside requested text fields
- [x] Run focused defense applications generation test proving same-run FAQ execution
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 72: Global Text Length Downshift + Wider Variation
Date: 2026-02-28
Status: COMPLETE

### Goal
Reduce centralized base text lengths across all text fields and widen centralized random length variation, then run a focused defense applications generation test.

### Steps
- [x] Add global base-length multiplier in centralized text field config path
- [x] Widen centralized text randomization factor range
- [x] Run focused defense applications generation test
- [x] Verify generated defense field is updated successfully
- [x] Record lesson in `tasks/lessons.md`

---

## Batch 68: FAQ Pipeline Parity Simplification
Date: 2026-02-27
Status: COMPLETE

### Goal
Make FAQ generation/extraction follow the exact same text pipeline as other text fields, with only one exception: normalize final FAQ content into multi-question/answer leaf items.

### Steps
- [x] Audit remaining FAQ-specific branches in generation/extraction pipeline
- [x] Remove non-essential FAQ-special-case parsing paths to match standard text flow
- [x] Keep only leaf-level FAQ normalization (question/answer items) at adapter boundary
- [x] Run targeted FAQ generation smoke test and schema/contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 69: FAQ Cross-Domain Structure Parity (Applications)
Date: 2026-02-28
Status: COMPLETE

### Goal
Align applications FAQ container structure to the existing canonical cross-domain shape used by other domains (including stable key ordering and section metadata placement) through source pipeline logic, then regenerate/export the target item.

### Steps
- [x] Confirm canonical FAQ container shape from existing frontmatter domains
- [x] Apply minimal adapter normalization change for FAQ container ordering/parity
- [x] Regenerate/export `defense-laser-cleaning-applications` from source pipeline
- [x] Verify frontmatter FAQ structure and record lesson in `tasks/lessons.md`

## Batch 70: Consolidate Text Length Variation Control
Date: 2026-02-28
Status: COMPLETE

### Goal
Centralize text-length variation factor loading and validation into a single configuration access path, then update all runtime callers to use it.

### Steps
- [x] Add one canonical `ProcessingConfig` accessor for text-length randomization factors
- [x] Refactor runtime callers (`HumannessOptimizer`, `DynamicConfig`) to use canonical accessor
- [x] Run targeted validation/import checks and verify no duplicate config loading paths remain
- [x] Record lesson in `tasks/lessons.md`

## Batch 71: Centralize Text Lengths + FAQ Leaf Parity
Date: 2026-02-28
Status: COMPLETE

### Goal
Ensure centralized base-length coverage for all configured text fields and apply the same centralized variation flow to FAQ leaves (question/answer) as other text fields.

### Steps
- [x] Expand centralized text field config with explicit base lengths for all configured text fields
- [x] Add centralized FAQ leaf length specs (`faqQuestion`, `faqAnswer`) in text field config
- [x] Add canonical config accessors for text-field length and randomization factors
- [x] Inject FAQ per-question/per-answer randomized guidance in humanness layer using canonical accessors in compact and full template paths
- [x] Validate all `field_router` text fields resolve through centralized length config
- [x] Run targeted runtime validation and record lesson in `tasks/lessons.md`

## Batch 60: Complete Defense Application Text Field Generation
Date: 2026-02-27
Status: IN PROGRESS

### Goal
Generate all configured applications text fields for `defense-laser-cleaning-applications` via source backfill and re-export to frontmatter.

### Steps
- [ ] Run item-filtered applications backfill (all configured fields)
- [ ] Export the repaired single item to frontmatter
- [ ] Verify expected generated fields exist in source/frontmatter
- [ ] Record lesson in `tasks/lessons.md`

## Batch 64: FAQ Prompt Parity + Downstream Normalization
Date: 2026-02-27
Status: IN PROGRESS

### Goal
Refactor FAQ prompts for parity across domain prompt contracts and ensure downstream prompting resolves FAQ like other text fields through the shared normalized path.

### Steps
- [ ] Audit current FAQ prompt contract coverage across all domain prompt files
- [ ] Align FAQ one-line sectionDescription prompts for parity across domains
- [ ] Verify runtime prompt resolution path uses normalized shared/domain contract flow for FAQ
- [ ] Run prompt/domain contract validation and targeted FAQ regeneration/export smoke check
- [ ] Record lesson in `tasks/lessons.md`

## Batch 67: FAQ Client Wiring Parity With Text Fields
Date: 2026-02-27
Status: COMPLETE

### Goal
Ensure FAQ generation in backfill flow connects to API clients through the same provider selection path used by other text-field generation commands.

### Steps
- [x] Trace FAQ/backfill client creation path against batch text generation path
- [x] Pass CLI-selected provider into backfill generator config
- [x] Refactor universal text generator to use shared `create_api_client(provider)`
- [x] Run focused applications dry-run smoke check with provider output verification
- [x] Record lesson in `tasks/lessons.md`

## Batch 66: Applications FAQ Domain-Wide Research + Regeneration
Date: 2026-02-27
Status: IN PROGRESS

### Goal
Research all applications FAQ records for structure/content drift, regenerate FAQ content domain-wide through the pipeline, and re-export/validate frontmatter consistency.

### Steps
- [ ] Baseline all applications FAQ structure types in source + frontmatter
- [ ] Run domain-wide applications FAQ regeneration via pipeline
- [ ] Normalize and re-export applications frontmatter from source of truth
- [ ] Run strict applications frontmatter schema validation
- [ ] Record lesson in `tasks/lessons.md`

## Batch 65: Simplify FAQ Pipeline for Text-Field Parity
Date: 2026-02-27
Status: COMPLETE

### Goal
Simplify FAQ generation/extraction/write flow to match standard text-field behavior while preserving backward compatibility for legacy FAQ list payloads.

### Steps
- [x] Remove FAQ-only extraction override so FAQ uses normalized text-field extraction defaults
- [x] Remove FAQ string-specific normalization branch from adapter write path
- [x] Keep legacy list-to-collapsible conversion compatibility for existing list payloads
- [x] Run targeted validation checks for config + adapter modules
- [x] Record lesson in `tasks/lessons.md`

## Batch 63: Audit All Applications Relationship Section Structure
Date: 2026-02-27
Status: COMPLETE

### Goal
Verify all applications frontmatter files follow the relationship section contract (leaf `_section` only, no redundant container-level `_section`) and remediate via generator/export flow if any drift exists.

### Steps
- [x] Scan all `../z-beam/frontmatter/applications/*.yaml` for redundant relationship container `_section`
- [x] If violations exist, run generator/export path to correct outputs at source (no violations found)
- [x] Re-run strict applications schema validation
- [x] Record lesson in `tasks/lessons.md` if a correction was needed (not needed)

## Batch 62: Move Relationship _section Fix Into Generator
Date: 2026-02-27
Status: COMPLETE

### Goal
Fix redundant container-level relationship `_section` metadata in generator logic so export output is correct without domain-specific cleanup workarounds.

### Steps
- [x] Patch universal export generator to strip relationship container-level `_section` blocks when leaf sections exist
- [x] Remove temporary applications-specific cleanup workaround entries
- [x] Re-export defense applications item and verify structure
- [x] Run strict applications frontmatter schema validation and record lesson

## Batch 61: Remove Redundant Outer Relationship Section Metadata
Date: 2026-02-27
Status: COMPLETE

### Goal
Align applications frontmatter structure with domain section contract by preventing duplicated outer `_section` blocks under `relationships.discovery` and `relationships.interactions`.

### Steps
- [x] Compare `domains/applications/prompt.yaml` contract against generated applications frontmatter structure
- [x] Patch export section-metadata generation to keep `_section` only on leaf relationship sections
- [x] Regenerate/export target applications item and verify redundant outer `_section` blocks are gone
- [x] Run relevant validation checks and record lesson in `tasks/lessons.md`

## Batch 59: Repair Incomplete Defense Applications Frontmatter
Date: 2026-02-27
Status: COMPLETE

### Goal
Fix incomplete `frontmatter/applications/defense-laser-cleaning-applications.yaml` by re-exporting the single item from canonical source data.

### Steps
- [x] Diagnose schema-required field failures on the target frontmatter file
- [x] Re-export the single applications item from `data/applications/Applications.yaml`
- [x] Re-run strict frontmatter schema validation for applications
- [x] Record lesson in `tasks/lessons.md`

## Batch 58: Applications Frontmatter Reset + Defense Regeneration
Date: 2026-02-27
Status: COMPLETE

### Goal
Delete all `frontmatter/applications` files and regenerate one defense catalog item via the generation pipeline.

### Steps
- [x] Remove all files from `../z-beam/frontmatter/applications`
- [x] Generate one defense applications item from catalog
- [x] Verify only regenerated defense file exists in frontmatter folder
- [x] Record lesson in `tasks/lessons.md`

## Batch 57: Generate One New Applications Catalog Item
Date: 2026-02-27
Status: COMPLETE

### Goal
Generate one newly added applications catalog item through the existing generation pipeline and verify output artifacts.

### Steps
- [x] Select one new applications catalog slug
- [x] Run focused generation for that item
- [x] Verify generated source/frontmatter output
- [x] Record lesson in `tasks/lessons.md`

## Batch 56: Prompt Source Centralization Gate + Source Map
Date: 2026-02-27
Status: COMPLETE

### Goal
Enforce a strict prompt-source audit gate so downstream prompt access uses approved centralized services, and generate a canonical prompt-source map artifact.

### Steps
- [x] Define approved prompt-source access policy in validator logic
- [x] Implement validator to detect non-centralized prompt access in Python runtime code
- [x] Generate canonical prompt-source map artifact from repo scan
- [x] Run validator locally and remediate immediate violations
- [x] Wire validator into CI data-validation workflow
- [x] Record lesson in `tasks/lessons.md`

## Batch 55: Remove Unreferenced Payload Monitor Module
Date: 2026-02-27
Status: COMPLETE

### Goal
Remove the unreferenced `materials/image/research/payload_monitor.py` module while preserving manual-ops utilities and validating domain contracts.

### Steps
- [x] Confirm `payload_monitor.py` has no runtime references
- [x] Delete only `payload_monitor.py`
- [x] Validate prompt/domain contracts
- [x] Record lesson in `tasks/lessons.md`

## Batch 54: Domains Likely-Dead Code Cleanup
Date: 2026-02-27
Status: COMPLETE

### Goal
Remove verified-unreferenced domain code files in `materials` while preserving required directory contract shape.

### Steps
- [x] Re-verify runtime references for likely-dead code candidates
- [x] Delete only verified-unreferenced code files
- [x] Preserve required empty directories with `.gitkeep`
- [x] Run prompt/domain contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 53: Domains Subfolder Usage Audit + Candidate Classification
Date: 2026-02-27
Status: COMPLETE

### Goal
Determine whether all contents under `domains/*/*` are in active use, then classify unreferenced items into safe documentation cleanup, likely-dead code, and manual-ops keep candidates.

### Steps
- [x] Recompute usage evidence for every file under `domains/*/*`
- [x] Classify unreferenced files by risk and operational intent
- [x] Produce delete-candidate report with rationale
- [x] Record lesson in `tasks/lessons.md`

## Batch 52: Domains Prompt Coverage Alignment
Date: 2026-02-27
Status: COMPLETE

### Goal
Align non-application domain prompt contracts to include missing `pageTitle` prompts and missing section title companions for existing section-description keys.

### Steps
- [x] Audit `/domains` for remaining transient/empty subfolder cleanup candidates
- [x] Add `pageTitle` prompt entries to non-application `domains/*/prompt.yaml`
- [x] Add missing section title companion prompts where section-description keys already existed
- [x] Run prompt/domain contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 51: Contaminants Docs Orphan Cleanup
Date: 2026-02-27
Status: COMPLETE

### Goal
Prune unreferenced contaminants domain documentation files under `docs/domains/`.

### Steps
- [x] Inventory `docs/domains/contaminants` contents
- [x] Verify cross-repo references for contaminants docs files
- [x] Remove verified-unreferenced docs files
- [x] Remove empty docs directories after deletion
- [x] Run prompt/domain contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 50: Materials Image Docs Structural Cleanup
Date: 2026-02-27
Status: COMPLETE

### Goal
Prune unreferenced `domains/materials/image/docs` files using verified cross-repo usage checks.

### Steps
- [x] Inventory `domains/materials/image/docs` files and collect reference counts
- [x] Verify candidate files have zero references outside docs subtree
- [x] Delete only verified-unused docs files
- [x] Confirm no stale references remain
- [x] Run prompt/domain contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 49: Domains Structural Cleanup (Legacy Prune)
Date: 2026-02-27
Status: COMPLETE

### Goal
Perform a structural cleanup inside `domains/` by removing verified-unused legacy files and keeping domain catalogs aligned.

### Steps
- [x] Audit structural cleanup candidates in `domains/`
- [x] Verify runtime usage before deleting legacy candidates
- [x] Remove verified-unused legacy artifacts and non-source clutter
- [x] Update domain catalog contract for removed legacy entries
- [x] Run prompt/domain contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 48: Cross-Repo Transient Artifact Cleanup
Date: 2026-02-27
Status: COMPLETE

### Goal
Perform safe transient cleanup across `z-beam` and `z-beam-generator` without changing source/runtime logic.

### Steps
- [x] Stop running dev processes before removing build artifacts
- [x] Remove transient artifacts from `z-beam` (`.next`, `coverage`, `reports`, temp files)
- [x] Remove transient artifacts from `z-beam-generator` (`__pycache__`, `.pytest_cache`, `.mypy_cache`, compiled/temp files)
- [x] Re-run prompt/domain contract validation
- [x] Restore dev server runtime state
- [x] Record lesson in `tasks/lessons.md`

## Batch 47: Domains Tree Hygiene Cleanup
Date: 2026-02-27
Status: COMPLETE

### Goal
Clean `domains/` and its subfolders by removing transient filesystem artifacts without changing runtime contracts.

### Steps
- [x] Audit `domains/` recursively for safe-to-remove transient artifacts (`__pycache__`, `.pyc`, `.DS_Store`, temp/editor files)
- [x] Remove identified transient artifacts across domain folders
- [x] Re-run prompt/domain contract validation after cleanup
- [x] Record lesson in `tasks/lessons.md`

## Batch 46: Cross-Domain Prompt Contract Rollout
Date: 2026-02-28
Status: COMPLETE

### Goal
Apply the functional applications prompt/catalog contract pattern to materials, contaminants, compounds, and settings so each domain has enforceable one-line prompt mappings and frontmatter article catalogs.

### Steps
- [x] Populate `domains/<domain>/prompt.yaml` one-line prompt mappings for materials/contaminants/compounds/settings
- [x] Populate `domains/<domain>/catalog.yaml` article frontmatter file-name catalogs for materials/contaminants/compounds/settings
- [x] Generalize `validate_prompt_section_contract.py` domain contract checks from applications-only to all core domains
- [x] Run prompt contract validation and resolve any domain parity drift
- [x] Record lesson in `tasks/lessons.md`

## Batch 64: FAQ Research Pipeline Alignment (Applications)
Date: 2026-02-27
Status: IN PROGRESS

### Goal
Ensure `faq` is generated through the same web-researched text pipeline as other applications text fields, then verify output parity and schema validity for `defense-laser-cleaning-applications`.

### Steps
- [ ] Audit current FAQ routing + research mode for applications generation
- [ ] Enable/configure FAQ for web-research-backed text generation path (without frontmatter patching)
- [ ] Regenerate target item FAQ at source
- [ ] Export target item and validate schema/structure
- [ ] Record lesson in `tasks/lessons.md`

## Batch 45: Prompt Governance Enforcement + Location Investigation
Date: 2026-02-27
Status: COMPLETE

### Goal
Complete prompt governance consolidation by keeping ownership files in `domains/*`, enforcing layout in validation/CI, and investigating whether `prompts/` should move under `shared/` or `generation/`.

### Steps
- [x] Remove `prompts/<domain>/catalog.yaml` files to keep governance in `domains/<domain>/catalog.yaml`
- [x] Enforce layout contract in `validate_prompt_section_contract.py`
- [x] Add explicit CI step for prompt governance validation in `.github/workflows/data-validation.yml`
- [x] Investigate `prompts/` relocation impact and document recommendation
- [x] Record lesson in `tasks/lessons.md`

## Batch 44: Domains Folder Prompt + Catalog Standardization
Date: 2026-02-27
Status: COMPLETE

### Goal
Within each core domain code folder (`domains/<domain>`), store a domain prompt YAML reference and a domain catalog, then evaluate folder contents for cleanup safety.

### Steps
- [x] Add `prompt.yaml` to `domains/applications`, `domains/materials`, `domains/contaminants`, `domains/compounds`, `domains/settings`
- [x] Add `catalog.yaml` to each core domain folder with required files/directories inventory
- [x] Evaluate each folder for cleanup candidates and mark safe review-only candidates without deleting runtime files
- [x] Run prompt/section contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 43: Domain Prompt Folder Catalog Standardization
Date: 2026-02-27
Status: COMPLETE

### Goal
Within each core prompt domain folder, keep one domain-specific prompt YAML and one domain-local catalog file; remove any extra domain-folder files.

### Steps
- [x] Add `catalog.yaml` in each core domain folder (`applications`, `materials`, `contaminants`, `compounds`, `settings`)
- [x] Ensure each domain folder contains only `content_prompts.yaml` and `catalog.yaml`
- [x] Run prompt contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 42: Legacy Prompt File Deletion
Date: 2026-02-27
Status: COMPLETE

### Goal
Delete unused legacy `prompts/**/*.txt` files after confirming runtime prompt resolution is registry-driven.

### Steps
- [x] Audit whole-project `.txt` prompt usage and confirm no runtime reads depend on deleted files
- [x] Delete legacy `prompts/**/*.txt` files
- [x] Update any residual verification logic that assumed physical template files
- [x] Run prompt/section contract validation
- [x] Record lesson in `tasks/lessons.md`

## Batch 41: Applications Title Generation Expansion
Date: 2026-02-27
Status: IN PROGRESS

### Goal
Add explicit content-generation coverage for applications `pageTitle` and relationship `_section.sectionTitle` fields via schema-backed component types.

### Steps
- [ ] Add schema component definitions for title generation
- [ ] Add shared prompt + metadata entries for title components
- [ ] Wire applications backfill config to generate `pageTitle` and relationship section titles
- [ ] Validate schema prompt resolution for new component types
- [ ] Record lesson in `tasks/lessons.md`

## Batch 40: Rail Transport Applications Catalog Expansion
Date: 2026-02-27
Status: IN PROGRESS

### Goal
Add the requested Rail Transport application slugs to canonical source data and sync frontmatter exports without schema contract drift.

### Steps
- [ ] Verify requested rail IDs against existing applications source
- [ ] Seed any missing Rail Transport application records in source data
- [ ] Export all requested Rail Transport records to frontmatter
- [ ] Validate source/frontmatter presence and relationship section contract
- [ ] Record lesson in `tasks/lessons.md`

## Batch 39: Seeded Page Author Rotation + Breadcrumb Contract
Date: 2026-02-27
Status: IN PROGRESS

### Goal
Ensure keyword-seeded pages assign authors via canonical rotation logic and generate domain-specific breadcrumbs that match sibling frontmatter contracts.

### Steps
- [ ] Restart and verify dev server health
- [ ] Route keyword seed author assignment through canonical author manager/rotation path
- [ ] Verify and enforce domain-specific breadcrumb shape in seeded output
- [ ] Run focused tests/validation and re-export target applications page if needed
- [ ] Record lesson in `tasks/lessons.md`

## Batch 38: Applications Sibling Output Parity Hardening (Marine)
Date: 2026-02-27
Status: COMPLETE

### Goal
Compare newly seeded `marine-laser-cleaning-ship-hulls-applications` output against sibling applications frontmatter, then adjust generator/source flow to remove template carryover and enforce reusable parity.

### Steps
- [x] Diff marine output vs sibling applications pages and identify contract/content drift
- [x] Fix generator/source pipeline to prevent template pageDescription carryover on new seeded items
- [x] Regenerate marine item fields and re-export single frontmatter page
- [x] Remove duplicate erroneous frontmatter artifact generated during earlier seed attempts
- [x] Run focused verification (frontmatter comparison + targeted validation/test)
- [x] Record lesson in `tasks/lessons.md`

## Batch 37: Centralized Keyword-to-Page Seeding Pipeline
Date: 2026-02-27
Status: COMPLETE

### Goal
Enable creation of a new domain item from a single topic keyword, then auto-populate researched text fields through the existing generation pipeline, with centralized reusable architecture across domains.

### Steps
- [x] Add shared reusable keyword seeding service (domain-agnostic core + per-domain rules)
- [x] Add CLI command in `run.py` to seed from keyword and trigger domain multi-field generation
- [x] Implement applications-first defaults while keeping reusable mappings for other domains
- [x] Add focused tests for slug/id generation and seed record creation behavior
- [x] Document usage in quick reference and record lesson in `tasks/lessons.md`
- [x] Run targeted verification (new tests + one dry-run command path)

## Batch 36: Dual Package Pricing Rollout (Residential + Industrial)
Date: 2026-02-27
Status: COMPLETE

### Goal
Replace single hourly rental price with two packages (Residential $190/hr, Industrial $270/hr) and propagate consistently across UI, config, and SEO infrastructure outputs.

### Steps
- [x] Inventory all active pricing references in app and SEO scripts/schemas
- [x] Update canonical pricing config to package-based structure with safe backward compatibility where required
- [x] Update pricing UI components to render both packages and minimum-hour messaging
- [x] Update JSON-LD/Offer/PriceSpecification generation to expose both package offers
- [x] Update SEO merchant/feed scripts and any pricing constants to match package rates
- [x] Run targeted tests/validation/build checks for touched pricing and schema paths
- [x] Record lesson in `tasks/lessons.md`

## Batch 35: z-beam Failing Test Suites Triage + Fix
Date: 2026-02-27
Status: COMPLETE

### Goal
Address currently failing test/build suites in `z-beam` with minimal, root-cause fixes and verify targeted pass.

### Steps
- [x] Reproduce failure and capture exact failing suite(s)/assertions
- [x] Isolate root cause in test or implementation (no unrelated refactors)
- [x] Apply minimal fix in source/test code
- [x] Re-run affected suite(s) and adjacent gate command(s)
- [x] Record lesson in `tasks/lessons.md`

## Batch 30: Data Completeness Gate + CI Enforcement
Date: 2026-02-27
Status: COMPLETE

### Goal
Add a dedicated source-data completeness validator with severity thresholds and machine-readable reporting, then enforce it in CI as a separate gate from frontmatter order/schema parity.

### Steps
- [x] Add `scripts/validation/validate_data_completeness.py` wrapper with threshold-based exit codes
- [x] Emit JSON + markdown artifacts for audit and CI uploads
- [x] Add focused unit tests for threshold evaluation logic
- [x] Wire validator into `.github/workflows/data-validation.yml`
- [x] Expand workflow path triggers to include generator/export/schema/validator changes
- [x] Run targeted local tests and validator sanity check
- [x] Update quick reference docs and lessons

## Batch 31: Source Data Completeness Remediation (Critical/High)
Date: 2026-02-27
Status: COMPLETE

### Goal
Reduce highest-volume CRITICAL/HIGH completeness gaps by fixing canonical source YAML data (not frontmatter), then validate delta with threshold reports.

### Steps
- [x] Identify top CRITICAL/HIGH finding patterns from `tasks/data_completeness_report.json`
- [x] Select one highest-volume pattern and confirm canonical source files/fields
- [x] Apply structured source-data fix in `data/` only (no frontmatter edits)
- [x] Re-run completeness validator and capture before/after delta
- [x] Update docs/lessons with remediation pattern and guardrail

## Batch 32: Materials Breadcrumb Completeness Remediation
Date: 2026-02-27
Status: COMPLETE

### Goal
Eliminate CRITICAL materials `breadcrumb` completeness gaps by backfilling canonical breadcrumb arrays in source data, then re-export and validate.

### Steps
- [x] Identify all materials missing `breadcrumb`
- [x] Backfill `breadcrumb` from canonical `fullPath`/`displayName` shape in source YAML
- [x] Re-export materials frontmatter
- [x] Re-run completeness validator and capture delta
- [x] Re-run field-order + strict schema validators
- [x] Update lessons with breadcrumb remediation pattern

## Batch 33: Materials EEAT Completeness Remediation
Date: 2026-02-27
Status: COMPLETE

### Goal
Eliminate CRITICAL materials `eeat` completeness gaps by backfilling canonical source `eeat` structure, then re-export and validate.

### Steps
- [x] Identify all materials missing `eeat`
- [x] Determine canonical `eeat` structure from existing source entries
- [x] Backfill missing `eeat` in `data/materials/Materials.yaml`
- [x] Re-export materials frontmatter
- [x] Re-run completeness validator and capture delta
- [x] Re-run field-order + strict schema validators
- [x] Update lessons with `eeat` remediation pattern

## Batch 34: Final Completeness Closure (Critical/High)
Date: 2026-02-27
Status: COMPLETE

### Goal
Resolve remaining CRITICAL/HIGH completeness findings via source fixes plus a targeted audit contract rule for mixed compounds with non-deterministic molecular weight.

### Steps
- [x] Backfill `materials.author` from canonical `authorId` where missing
- [x] Backfill missing `materials.components` from same category/subcategory donors
- [x] Backfill empty `contaminants.validMaterials` from same category/subcategory donors
- [x] Update completeness audit rule to allow missing `molecularWeight` for mixed/variable compounds
- [x] Re-export impacted domains and re-run completeness/parity validators
- [x] Update lessons and finalize batch statuses

## Batch 29: Generator-First Field Order Parity + Lasting Enforcement
Date: 2026-02-27
Status: PLANNED

### Goal
Restore durable frontmatter field-order parity within and across domains by fixing generator/export pipeline behavior (not frontmatter files), then re-export and verify domain-wide compliance.

### Scope Guardrails
- Do **not** edit files under `../z-beam/frontmatter/` manually.
- Fix at source and generation/export orchestration layers only.
- Preserve existing architecture: exporter is transform/presentation-only; do not add build-time data invention.
- Treat field order authority as `data/schemas/FrontmatterFieldOrder.yaml`.

### Phase 0 — Baseline + Failure Taxonomy
- [ ] Capture fresh baseline with:
  - [ ] `python3 scripts/check_field_order.py`
  - [ ] `python3 scripts/validation/validate_frontmatter_schema.py`
- [ ] Produce per-domain breakdown of failure classes:
  - [ ] Ordering-only violations
  - [ ] Schema-shape violations (e.g., `author` type/required)
  - [ ] Duplicate artifact files (slug/id duplicated in filename)
  - [ ] Contract drift in rich sections (`faq`, `micro`, `breadcrumb`)
- [ ] Save machine-readable audit artifacts in `tasks/` for before/after diff.

### Phase 1 — Single Canonical Ordering Path in Pipeline
- [ ] Trace all writers touching frontmatter export payloads (`domains/*`, `export/*`, `generation/*`).
- [ ] Identify every place field ordering is performed or bypassed.
- [ ] Consolidate to one canonical ordering function sourced from `FrontmatterFieldOrder.yaml`.
- [ ] Ensure canonical ordering is invoked as the **final deterministic step** before YAML serialization for every domain.
- [ ] Remove/disable redundant domain-local ordering implementations that can drift.

### Phase 2 — Lasting Generator/Export Contract Fixes (Root Cause)
- [ ] Fix generator-side contract emission for known parity breakers:
  - [ ] `author` always emitted as object (never scalar id at frontmatter contract layer)
  - [ ] `breadcrumb[*].href` never null when required by schema
  - [ ] Eliminate accidental duplicate output entities/files in generation→export path
  - [ ] Normalize section payload contracts where schema requires scalar/object shape
- [ ] Enforce fail-fast behavior for required contract fields (no silent defaults/mocks).
- [ ] Add/extend normalization only where architecture allows (source/generator), not as exporter data invention.

### Phase 3 — Re-Export from Source of Truth
- [ ] Run controlled re-export by domain from source data after code fixes.
- [ ] Export sequence:
  - [ ] materials
  - [ ] contaminants
  - [ ] compounds
  - [ ] settings
  - [ ] applications
- [ ] Confirm no direct manual edits were made to frontmatter files.

### Phase 4 — Verification Gates (Must Pass Before Done)
- [ ] Re-run `python3 scripts/check_field_order.py` and require 100% pass.
- [ ] Re-run `python3 scripts/validation/validate_frontmatter_schema.py --strict` and require 0 failures.
- [ ] Add focused regression tests around:
  - [ ] canonical ordering invocation (all domains)
  - [ ] author contract shape
  - [ ] breadcrumb required fields
  - [ ] duplicate output prevention
- [ ] Re-run targeted tests and report pass/fail evidence.

### Phase 5 — Hardening for Durability
- [ ] Add CI gate to fail on field-order regressions and schema drift in exported frontmatter.
- [ ] Add a lightweight pre-export contract check in generator/export orchestration path.
- [ ] Document canonical ordering pathway and “no direct frontmatter edits” workflow in docs.
- [ ] Record lessons in `tasks/lessons.md` after implementation.

### Deliverables
- [ ] Generator/export code changes implementing canonical order + contract fixes
- [ ] Re-export completed for all target domains
- [ ] Before/after parity metrics documented in `tasks/`
- [ ] Tests/validation evidence attached in terminal logs

## Batch 28: Full Settings Re-export
Date: 2026-02-27
Status: COMPLETE

### Goal
Re-export all settings frontmatter files and verify `machineSettings` contract compliance domain-wide.

### Steps
- [x] Plan written
- [x] Run full settings domain export
- [x] Re-run full settings frontmatter contract audit

---

## Batch 27: Full Settings Frontmatter Contract Audit
Date: 2026-02-27
Status: COMPLETE

### Goal
Audit all settings frontmatter files for `machineSettings` contract compliance (`_section` present, no leaf `description`).

### Steps
- [x] Plan written
- [x] Run full-domain audit across settings frontmatter files
- [x] Report summary and exception list

---

## Batch 26: Settings Post-Cleanup Smoke Test
Date: 2026-02-27
Status: COMPLETE

### Goal
Export `basalt-settings` plus two random settings items and verify `machineSettings` contract holds in generated frontmatter.

### Steps
- [x] Plan written
- [x] Select two random settings IDs (excluding basalt)
- [x] Export three target settings items
- [x] Validate machineSettings shape/no leaf descriptions in exported files

---

## Batch 25: Strict machineSettings Data Cleanup
Date: 2026-02-27
Status: COMPLETE

### Goal
Run strict contract audit and remove all legacy `machineSettings.*.description` fields from source settings data.

### Steps
- [x] Plan written
- [x] Run strict validator audit on canonical + shared settings data
- [x] Remove forbidden `machineSettings` leaf `description` fields from source YAML files
- [x] Re-run strict validator and confirm pass

---

## Batch 24: CI Guard for machineSettings Leaf Descriptions
Date: 2026-02-26
Status: COMPLETE

### Goal
Prevent regressions by failing CI if `machineSettings` leaf nodes contain legacy `description` fields.

### Steps
- [x] Plan written
- [x] Add validator script to detect forbidden `machineSettings.*.description`
- [x] Wire validator into CI workflow
- [x] Run validator locally and confirm pass

---

## Batch 23: Settings machineSettings Contract Cleanup
Date: 2026-02-26
Status: COMPLETE

### Goal
For `settings.machineSettings`, remove leaf `description` fields (including prompt dependencies) and enforce output shape as `_section` + leaves.

### Steps
- [x] Plan written
- [x] Locate all `machineSettings.*.description` source/prompt references
- [x] Remove `description` from prompt machine-settings payloads and exported `machineSettings` leaves
- [x] Enforce `machineSettings` structure as `_section` + leaves in export output
- [x] Export one settings item and verify resulting frontmatter structure

---

## Batch 22: Exact Basalt Settings Regeneration
Date: 2026-02-26
Status: COMPLETE

### Goal
Regenerate the exact `basalt-settings` source item and re-export its settings frontmatter page.

### Steps
- [x] Plan written
- [x] Regenerate source content for `basalt-settings`
- [x] Export `basalt-settings` frontmatter
- [x] Verify frontmatter timestamp/content updated

---

## Batch 21: Sample Page Regeneration (Settings)
Date: 2026-02-26
Status: COMPLETE

### Goal
Regenerate one sample settings page from source generators and export the updated frontmatter item.

### Steps
- [x] Plan written
- [x] Identify sample item ID and matching generator
- [x] Regenerate sample source content (single item)
- [x] Export single frontmatter page for sample item
- [x] Verify regenerated frontmatter output exists

---

## 2026-02-26: Prompt Siloing Guardrail Validation (Batch 20)

**Goal**: Enforce strict separation so domain content sections remain content-only while centralized voice/humanness stay reusable and referenced externally.

### Steps
- [x] Plan written
- [x] Add coherence validation rule for voice/humanness leakage into component/content section
- [x] Add focused tests for siloing rule
- [x] Run focused prompt coherence tests
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Frontend Section Header Frontmatter-Only Enforcement (Batch 19)

**Goal**: Ensure `sectionTitle` and `sectionDescription` used by frontend section containers come solely from frontmatter `_section` data with no programmatic defaults/synthesis.

### Steps
- [x] Plan written
- [ ] Audit frontend for programmatic `sectionTitle`/`sectionDescription` fallbacks or synthetic construction
- [ ] Remove/replace fallback synthesis so section headers derive from frontmatter-only inputs
- [ ] Update affected tests/types/comments for frontmatter-only contract
- [ ] Run focused frontend tests/diagnostics
- [ ] Update `tasks/lessons.md`

---

## 2026-02-26: Frontend Data Fallback & Enrichment Removal (Batch 19)

**Goal**: Remove data-related frontend fallbacks and enrichment behavior so section/content values are sourced directly from frontmatter contracts.

### Steps
- [x] Plan written
- [ ] Audit all data fallback and enrichment hotspots in `z-beam`
- [ ] Remove fallback/default data synthesis from section and relationship rendering paths
- [ ] Remove frontend enrichment/normalization that mutates missing data into display-ready values
- [ ] Run focused diagnostics/tests for impacted components and helpers
- [ ] Update `tasks/lessons.md`

---

## 2026-02-26: Sweep Section Metadata Wording Consistency (Batch 18)

**Goal**: Normalize residual documentation wording so section-related metadata language consistently reflects developer-facing section-function intent.

### Steps
- [x] Plan written
- [x] Audit docs for residual wording that implies UI/technical metadata semantics
- [x] Update only section-field wording to developer-purpose semantics
- [x] Validate with focused grep/diagnostics
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Clarify SectionMetadata Intent in Schema & Policy Docs (Batch 17)

**Goal**: Align authoritative schema/policy documentation so `sectionMetadata` is explicitly developer-facing section-function text, not UI config or key labels.

### Steps
- [x] Plan written
- [x] Identify authoritative schema/policy reference files that define `sectionMetadata`
- [x] Update policy language and examples to developer-purpose text semantics
- [x] Update schema field comment to match intended semantics
- [x] Run focused consistency grep/diagnostics
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Normalize Section Metadata Intent Text (Batch 16)

**Goal**: Ensure `sectionMetadata` consistently describes developer-facing section function (not UI config or key labels) across active and example prompt metadata.

### Steps
- [x] Plan written
- [x] Audit all prompt YAML files for object-style or identifier-only `sectionMetadata`
- [x] Convert example prompt architecture files to text-only developer-purpose `sectionMetadata`
- [x] Align active shared/materials prompt metadata to developer-purpose text intent
- [x] Run focused prompt registry tests and object-style metadata grep audit
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Add Section Metadata Fields to Content Prompts (Batch 15)

**Goal**: Ensure section prompt metadata includes `sectionTitle`, `sectionDescription`, and text `sectionMetadata` consistently in domain content prompts and prompt contract validation.

### Steps
- [x] Plan written
- [x] Update domain content prompt metadata entries to include `sectionMetadata` where missing
- [x] Update prompt metadata validator to require non-empty string `sectionMetadata`
- [x] Verify no `section_prompt_metadata` entry has `sectionMetadata` without title/description
- [x] Run focused prompt/section policy tests
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Align Section Contract Tests to Canonical Nested Paths (Batch 14)

**Goal**: Update stale tests so section contract coverage matches canonical nested-section output and mandatory `sectionMetadata` requirements.

### Steps
- [x] Plan written
- [ ] Update targeted section metadata policy tests (remove root-level mirror expectation)
- [ ] Update comprehensive metadata field-count test to require `sectionMetadata`
- [ ] Run focused section contract tests
- [ ] Update `tasks/lessons.md`

---

## 2026-02-26: Remove Materials Root-Level Section Mirrors (Batch 13)

**Goal**: Eliminate duplicate materials section containers by keeping canonical nested `properties.*` paths and removing root-level mirrors generated at export time.

### Steps
- [x] Plan written
- [x] Remove materials flattening that mirrors properties sections to root
- [x] Re-export materials frontmatter
- [x] Audit for root-vs-nested section duplication
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Audit Duplicate Section Paths Across Domains (Batch 12)

**Goal**: Determine whether top-level section keys duplicate nested section paths in source data and exported frontmatter across materials, contaminants, settings, compounds, and applications.

### Steps
- [x] Plan written
- [ ] Identify duplicate key/path patterns in source YAML data
- [ ] Identify duplicate key/path patterns in exported frontmatter
- [ ] Summarize by domain with concrete examples and counts
- [ ] Update `tasks/lessons.md`

---

## 2026-02-26: Tighten Section Key Contracts (Batch 10)

**Goal**: Enforce section metadata contracts for specific material/frontmatter keys and aliases across schema, generator behavior, docs/prompts metadata, and tests.

### Steps
- [x] Plan written
- [ ] Add canonical and alias section-key mappings in schema/field-order docs
- [ ] Update generator section metadata handling for targeted keys (including faq)
- [ ] Add prompt metadata references for targeted keys
- [ ] Add targeted compliance tests and run focused validation/export
- [ ] Update `tasks/lessons.md`

---

## 2026-02-26: Cross-Domain Section Contract Hardening Rollout (Batch 11)

**Goal**: Apply and verify `_section` contract hardening (ordered `_section` placement + ordered required metadata fields including `sectionMetadata`) for contaminants, settings, and compounds.

### Steps
- [x] Plan written
- [x] Verify section_metadata task coverage and schema mappings for target domains
- [x] Run domain exports for contaminants/settings/compounds
- [x] Audit exported frontmatter for `_section` required fields + ordering compliance
- [x] Patch any domain-specific config/schema gaps and re-verify
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Section Field-Order Contract Tightening (Batch 10)

**Goal**: Document and enforce explicit ordering so section metadata fields appear first under section keys for materials, then reuse for other domains.

### Steps
- [x] Plan written
- [x] Update field-order schema docs for section container and `_section` subfield order
- [x] Update section metadata policy docs with required field-order precedence
- [x] Run materials integration audit for new section fields
- [x] Summarize remaining integration gaps and rollout task naming

---

## 2026-02-26: Remediate Material Index Integrity Drift (Batch 9)

**Goal**: Remove stale `material_index` dependency in pre-generation validation and resolve category/material lookup from canonical `materials` entries.

### Steps
- [x] Plan written
- [x] Identify stale index-key assumptions in pre-generation validation paths
- [x] Replace index-based lookups with canonical material-entry/category resolution
- [x] Run standalone smoke + focused export validation
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Remediate Standalone Validation Runtime Drift (Batch 8)

**Goal**: Fix standalone validation entry-point portability issues (service import path + schema file resolution) and re-verify explicit contract behavior.

### Steps
- [x] Plan written
- [x] Identify concrete import/path drift roots in validation services
- [x] Apply minimal fail-fast compatible fixes
- [x] Run focused standalone smoke tests + export validation
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Final E2E Verification Pass (Post Fallback Hardening)

**Goal**: Run a final end-to-end verification pass to assess readiness after fail-fast fallback removal batches.

### Steps
- [x] Plan written
- [x] Run full export-all validation
- [x] Run explicit-contract smoke checks for orchestrator/schema validator entry points
- [x] Summarize readiness score with evidence
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Remove Runtime Fallbacks (Batch 7)

**Goal**: Remove remaining fallback defaults in validation orchestrator and schema validator entry points, enforcing explicit contracts.

### Steps
- [x] Plan written
- [x] Identify active fallback defaults in orchestrator/schema validator
- [x] Replace fallback defaults with explicit contract validation
- [x] Run focused command/export validation
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Remove Runtime Fallbacks (Batch 6)

**Goal**: Remove active fallback defaults in validation service entry points and domain adapters, enforcing explicit configuration contracts.

### Steps
- [x] Plan written
- [x] Identify active fallback defaults in validation/adapters
- [x] Replace fallback defaults with explicit contract validation
- [x] Run focused command/export validation
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Remove Runtime Fallbacks (Batch 5)

**Goal**: Remove active fallback defaults in FieldRouter + postprocess data loading and enforce explicit field/domain contracts.

### Steps
- [x] Plan written
- [x] Identify active fallback defaults in FieldRouter and postprocess paths
- [x] Replace fallback defaults with explicit contract validation
- [x] Run focused command/export validation
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Remove Runtime Fallbacks (Batch 4)

**Goal**: Remove fallback defaults in active export task handlers (SEO/FAQ/library), enforcing explicit task configuration and required source fields.

### Steps
- [x] Plan written
- [x] Identify active fallback defaults in export task handlers
- [x] Replace fallback defaults with explicit required-key validation
- [x] Run focused export validation
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Remove Runtime Fallbacks (Batch 3)

**Goal**: Continue fail-fast hardening by removing remaining active runtime fallback paths in orchestration commands and config resolution.

### Steps
- [x] Plan written
- [x] Identify next active fallback paths in runtime command/orchestration code
- [x] Replace fallback branches/defaults with explicit contract errors
- [x] Run focused command/export validation
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Remove Runtime Fallbacks (Batch 2)

**Goal**: Continue fail-fast hardening by removing fallback behavior in active generation/export runtime helpers without touching protected files.

### Steps
- [x] Plan written
- [x] Identify high-impact fallback code in active runtime helpers
- [x] Replace fallback returns/defaults with explicit contract validation
- [x] Run focused export/generation validation commands
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Generator Settings Verification + Re-Export (No Frontmatter Edits)

**Goal**: Ensure generator/export settings are correct, fix only source/config drift, and re-export to synchronize frontmatter outputs without direct frontmatter modification.

### Steps
- [x] Plan written
- [ ] Validate generator/export settings that affect metadata/title correctness and domain routing
- [ ] Apply minimal source/config fixes only (no frontmatter edits)
- [ ] Run targeted export command(s) to regenerate affected domains
- [ ] Verify outputs via validators/sanity checks and update `tasks/lessons.md`

---

## 2026-02-26: Remove Runtime Fallbacks (Fail-Fast Hardening)

**Goal**: Remove fallback behavior from active runtime paths (generator + frontend + export orchestration), replacing silent fallback with explicit fail-fast behavior.

### Steps
- [x] Plan written
- [x] Inventory runtime fallback patterns in source code (exclude docs/tests/frontmatter)
- [x] Remove fallback control flow in high-impact execution paths (export orchestration, config/provider resolution, metadata runtime)
- [x] Run focused validation (exports + naming + local route checks)
- [x] Update `tasks/lessons.md` with fallback-removal rules

---

## 2026-02-26: Final Non-Python Winston Sweep

**Goal**: Remove remaining non-Python Winston references (docs/scripts/config comments and filenames) and normalize naming to Grok.

### Steps
- [x] Plan written
- [x] Inventory non-Python Winston references and Winston-named files
- [x] Update docs/comments/config text to Grok naming where runtime behavior is now Grok-only
- [x] Rename Winston-labeled scripts/files where appropriate and update references
- [x] Verify no non-Python Winston remnants remain
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Disable Winston Check (Grok-Only)

**Goal**: Disable Winston AI detection checks in generation and use Grok humanness evaluation as the only quality signal.

### Steps
- [x] Plan written
- [x] Replace Winston detection logic with Grok-only evaluation in generator core
- [x] Run one focused generation verification and confirm no Winston check path is used
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Remove Winston and Cut Over to Grok Humanness

**Goal**: Eliminate Winston from active project runtime and replace humanness detection/scoring with a dedicated Grok module integrated with learning DB feedback loops.

### Steps
- [x] Plan written
- [x] Inventory active Winston runtime/config dependencies
- [x] Implement dedicated Grok humanness detection/scoring module
- [x] Replace Winston integration call sites with Grok module wiring
- [x] Remove Winston provider/config/runtime guards from active flow
- [x] Run focused generation + DB verification
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Wire Grok Evaluator into Runtime Learning Loop

**Goal**: Add production wiring for Grok criterion feedback by persisting evaluator payloads in learning DB and invoking one evaluator call in generation flow.

### Steps
- [x] Plan written
- [x] Add `ConsolidatedLearningSystem` methods to persist Grok parent/criterion rows
- [x] Add one Grok evaluator runtime helper with schema validation
- [x] Invoke evaluator once after generation logging and persist feedback
- [x] Run focused generation verification and update `tasks/lessons.md`

---

## 2026-02-26: Grok Evaluator Schema + Learning DB Integration Design

**Goal**: Deliver production-ready Grok humanness evaluator contract artifacts and a concrete integration path into the existing learning database.

### Steps
- [x] Plan written
- [x] Define strict evaluator JSON schema for criterion-level scoring + gates
- [x] Create Grok prompt contract with weights and fail thresholds
- [x] Draft additive SQL migration for Grok evaluation persistence linked to `generations.id`
- [x] Document plug-in integration steps for current generation loop and `ConsolidatedLearningSystem`

---

## 2026-02-26: Fix Winston Cached-Client Warning in Postprocess

**Goal**: Remove the `CachedAPIClient.check_text` warning by ensuring postprocess quality analysis uses a non-cached Winston client path.

### Steps
- [ ] Plan written
- [ ] Trace where postprocess analyzer receives Winston client
- [ ] Apply minimal fix to force non-cached Winston detection client for analysis
- [ ] Run focused postprocess verification and confirm warning removed
- [ ] Update `tasks/lessons.md`

---

## 2026-02-26: Enable Learning Evaluation in Postprocess Retries

**Goal**: Ensure retry attempts in postprocess contribute full learning signals by removing retry-path learning-evaluation skips.

### Steps
- [x] Plan written
- [x] Locate retry generation call path and confirm current skip behavior
- [x] Apply minimal fix to enable learning evaluation for retry attempts
- [x] Run focused postprocess verification on one item/domain
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Winston-Enabled 5-Domain Benchmark Pass

**Goal**: Validate full closed-loop behavior with Winston enabled across five domains and capture measurable run metrics.

### Steps
- [x] Plan written
- [x] Confirm Winston is enabled (no disable env flags) for the run context
- [x] Execute one generation run each for materials, contaminants, compounds, settings, applications
- [x] Capture per-run outcomes and key signals (generation ID, pass/fail, notable warnings)
- [x] Summarize benchmark deltas and update `tasks/lessons.md`

---

## 2026-02-26: Fix Author Identity + Contaminants Root Key Drift

**Goal**: Resolve generation-time author identity failures and contaminants root-key mismatch by fixing source/config contracts.

### Steps
- [x] Plan written
- [x] Normalize remaining `authorId`-only source records to canonical `author` shape
- [x] Update contaminants domain config to current source root key/path
- [x] Re-run targeted generation checks for all domains with Winston disabled
- [x] Update `tasks/lessons.md`

---

## 2026-02-26: Temporary Winston Disable + Pipeline Verification

**Goal**: Temporarily disable Winston cleanly for generation runs, verify postprocess/learning path still executes, and confirm prompt output remains usable.

### Steps
- [x] Plan written
- [x] Add fail-fast Winston toggle in coordinator/client init path (no protected-file edits)
- [x] Run one generation per domain with Winston disabled and capture pass/fail causes
- [x] Verify learning/postprocess signals are still emitted during generation/evaluation
- [x] Update `tasks/lessons.md`

---

## 2026-02-25: Wire Soft-Mode SEO Check into CI Matrix

**Goal**: Add esoteric SEO soft-mode validation to CI workflow and document it in deployment completion checklist.

### Steps
- [x] Plan written
- [x] Add CI workflow step for `validate:seo:esoteric:soft`
- [x] Update deployment checklist to include soft-mode CI coverage
- [x] Run focused verification (workflow parse + targeted test)
- [x] Update `tasks/lessons.md`

---

## 2026-02-25: Create Test Text Prompt YAML Example

**Goal**: Provide a tweakable example YAML for domain text-prompt architecture using single-line section prompts and explicit data binding for subject/context.

### Steps
- [x] Confirm existing prompt registry/domain config conventions
- [x] Create example YAML under `prompts/examples/`
- [x] Validate the example against the 3 required architecture constraints

---

## 2026-02-25: Align Prompt Example + Section Metadata Schema

**Goal**: Ensure prompt example aligns with compounds schema expectations and section metadata contract used by frontend (`sectionTitle`, `sectionDescription`).

### Steps
- [x] Verify compounds prompt/field scope and current schema behavior
- [x] Remove invalid compounds prompt keys from example (e.g., `micro`)
- [x] Add explicit `sectionTitle` and `sectionDescription` to section schema entries
- [x] Re-validate YAML parsing and key presence

---

## 2026-02-25: Canonicalize Compounds Section Keys

**Goal**: Align schema/prompt/example contracts with live compounds page section keys (`detectionMonitoring`, `producedFromMaterials`) and remove mirror drift.

### Steps
- [x] Confirm live compounds section keys from frontmatter/source data
- [x] Add schema entries for live compounds keys with canonical prompt refs
- [x] Update prompt example to strict compounds section-key mirror
- [x] Validate example keys match live compounds frontmatter section keys

---

## 2026-02-25: Enforce Section Metadata Contract + Naming Parity

**Goal**: Add a validator that enforces section metadata fields in prompt YAMLs and tighten frontend/backend relationship naming parity.

### Steps
- [x] Identify backend/frontend section and relationship contract differences
- [x] Add prompt YAML metadata contract (`sectionTitle`, `sectionDescription`, `sectionMetadata`) and enforce in loader/validator
- [x] Tighten frontend relationship key/category unions to match live backend/frontmatter keys
- [x] Run focused validation script(s) and confirm pass

---

## 2026-02-25: Mirror Prompt Examples for Remaining Domains

**Goal**: Create schema-compatible prompt example YAMLs for materials, contaminants, settings, and applications using live section keys and inferred single-line prompts.

### Steps
- [x] Derive live section keys per domain from frontmatter
- [x] Generate domain example prompt YAMLs with section prompts and required section metadata
- [x] Validate contract + key parity for each new domain example

---

## 2026-02-25: Add Esoteric SEO Soft-Mode Integration Test

**Goal**: Add a CI-friendly integration test that runs esoteric SEO validation in soft mode and confirms non-blocking execution.

### Steps
- [x] Plan written
- [x] Add soft-mode npm script for esoteric SEO validation
- [x] Add integration test that runs soft mode command and asserts success
- [x] Run targeted integration test and confirm pass
- [x] Update `tasks/lessons.md`

---

## 2026-02-25: Document + Test Advanced SEO Hardening

**Goal**: Add clear operator docs and automated tests for advanced SEO hardening orchestration and entity-graph advisory/strict behavior.

### Steps
- [x] Plan written
- [x] Add deployment validation guide section for advanced SEO checks and strict/advisory mode
- [x] Add focused tests for postdeploy advanced category wiring and entity-graph helper semantics
- [x] Run targeted test file and confirm pass
- [x] Update `tasks/lessons.md`

---

## 2026-02-25: Postdeploy Canonical + Lighthouse HTTPS Fixes

**Goal**: Fix validator/content issues causing postdeploy failures for canonical consistency and Lighthouse HTTPS enforcement false positives.

### Steps
- [x] Confirm failure root causes from isolated validator runs
- [ ] Fix canonical source behavior so dynamic pages do not inherit home canonical
- [ ] Fix Lighthouse HTTPS scanner exclusions for valid sitemap/XML namespace URLs
- [ ] Re-run targeted validators (`validate-lighthouse-metrics`, `validate-production-comprehensive --skip-external`)
- [ ] Re-run `npm run postdeploy` and record final status
- [ ] Update `tasks/lessons.md`

---

## 2026-02-25: SEO Validation Hardening

**Goal**: Improve postdeploy validation reliability and signal quality without reducing meaningful SEO coverage.

### Steps
- [x] Plan written
- [ ] Make route sampling deterministic in Lighthouse canonical checks
- [ ] Add retry support for transient validator failures/timeouts in postdeploy orchestrator
- [ ] Make full-site indexability handling explicit for intentionally noindex routes
- [ ] Re-run `npm run postdeploy` and capture final status
- [ ] Update `tasks/lessons.md`

---

## 2026-02-25: Implement Advanced SEO Hardening Bundle

**Goal**: Implement first-production versions of all identified advanced SEO capabilities (indexing signals, crawl/index observability, canonical graphing, schema graph consistency checks, and trend monitoring).

### Steps
- [x] Plan written
- [x] Add IndexNow + delta sitemap utilities and scripts
- [x] Add crawl-budget/noindex policy audit and canonical conflict graph audit
- [x] Add soft-404/orphan detection and bot-log analytics tooling
- [x] Add JSON-LD entity graph consistency validator (global @id/sameAs checks)
- [x] Add SERP trend/anomaly monitor scaffolding with persisted snapshots
- [x] Wire npm scripts + postdeploy integration hooks
- [x] Run targeted validations and one full postdeploy check
- [x] Update `tasks/lessons.md`

## 2026-02-25: Enforce Required _section Fields

**Goal**: Ensure every `_section` block always has both `sectionTitle` and `sectionDescription` during export.

**Scope**:
- Fix in export pipeline (source of truth), not manual frontmatter patching
- Validate on regenerated output

### Steps
- [x] Locate section metadata injection path in exporter
- [x] Add universal enforcement pass for all `_section` blocks
- [x] Re-export sample item and verify required keys present
- [x] Update `tasks/lessons.md`

**Follow-up (same day)**:
- [x] Enabled `section_metadata` task in `export/config/applications.yaml` so applications relationship sections are included in enforcement
- [x] Re-exported `applications` domain and re-ran global frontmatter scan (`missing_count: 0`)

---

## 2026-02-25: Fix Failing Frontend Workflow Tasks

**Goal**: Resolve recent task failures for `Quick Component Audit` and `Enforce Component Rules` using minimal command/path corrections.

**Scope**:
- Analyze only the failing task definitions and related hook references
- Fix missing command/script path issues at source
- Re-run the failing tasks to verify they execute successfully

### Steps
- [x] Plan written
- [x] Locate canonical audit/rules scripts or nearest supported equivalents
- [x] Update task and hook command references with minimal changes
- [x] Re-run `Quick Component Audit` and `Enforce Component Rules`
- [x] Update `tasks/lessons.md` with failure pattern and prevention rule

---

## 2026-02-25: Fix z-beam Prebuild Metadata Sync Failure

**Goal**: Resolve `npm run prebuild` failure in `z-beam` caused by `validate:metadata` (`Metadata sync`) with a minimal source-side fix.

**Scope**:
- Diagnose only `validate:metadata` first
- Fix at source (generator/frontmatter sync path), not output patching
- Re-run `validate:metadata`, then `prebuild`

### Steps
- [x] Plan written
- [x] Run `npm run validate:metadata` and capture exact mismatches
- [x] Trace mismatch origin (source data, export config, or validator logic)
- [x] Apply minimal fix at source *(not required — validator now reports 0 errors and 0 sync issues)*
- [x] Re-run `npm run validate:metadata`
- [x] Re-run `npm run prebuild` for confirmation
- [x] Update `tasks/lessons.md`

---

## 2026-02-25: Remove Duplicate `author` Keys (Applications)

**Goal**: Ensure `author` appears only once as the full author object (no scalar duplicate key) in applications source/output.

**Scope**:
- Fix at Layer 1 source YAML (`data/applications/Applications.yaml`)
- Re-export applications frontmatter to sync output
- Verify no duplicate `author` keys remain in source or exported files

### Steps
- [x] Identify duplicate-key root cause in source YAML
- [x] Remove scalar duplicate `author` keys from applications source data
- [x] Re-export applications frontmatter
- [x] Verify source and frontmatter for duplicate `author` keys
- [x] Update `tasks/lessons.md`

---

## Session 10 — Data Completeness Audit (2026-02-24)

**Goal**: Audit all source data YAML files for field presence, emptiness, and
cross-domain referential integrity. Produce a ranked findings report.

**Domains in scope**:
- `data/materials/Materials.yaml` — 153 items
- `data/contaminants/contaminants.yaml` — 98 items
- `data/settings/Settings.yaml` — 153 items
- `data/compounds/Compounds.yaml` — 34 items
- `data/applications/Applications.yaml` — 10 items
- `data/authors/Authors.yaml` — 4 items

**Checks**:
1. Required field presence per domain (missing key = CRITICAL)
2. Empty/null/blank values on required fields (empty value = HIGH)
3. Sub-structure completeness: faq, eeat, micro, machineSettings, images, relationships, components
4. Cross-domain referential integrity: author→authors, validMaterials→materials
5. Duplicate ids within a domain
6. datePublished / dateModified presence and ISO-8601 format

**Output**: `tasks/data_audit_report.md`

### Steps
- [x] Plan written
- [x] Build `scripts/audit/data_completeness.py`
- [x] Run audit → 247 verified findings (233 CRITICAL / 6 HIGH / 8 MEDIUM / 0 LOW)
- [x] Report written to `tasks/data_audit_report.md`
- [ ] **Next**: Regenerate contaminants `description` only (~97 items) — `micro` is materials-only; contaminants use `images.micro` (image URL sub-key only)
- [ ] **Next**: Regenerate materials `eeat` (~21 items) + `breadcrumb` (~26 items)
- [ ] **Next**: Fix 3 materials with unstructured raw-string faq/micro (alabaster, aluminum, steel)
- [x] molecularWeight=null is ACCEPTABLE for 4 aggregate compounds (`metal-oxides-mixed-compound`, `metal-vapors-mixed-compound`, `nanoparticulates-compound`, `organic-residues-compound`) — no molecular weight is defined for mix aggregates

---

## Session 10 — Enricher Audit (2026-02-24)

**Goal**: Ensure no standalone enrichers exist outside the generator pipeline.

### Findings
- `generation/context/generation_metadata.py` `enrich_for_generation()` — inside `write_component()` pipeline ✅ CORRECT
- `generation/core/adapters/domain_adapter.py` `enrich_on_save()`, `_enrich_author_field()`, `get_enrichment_data()` — all inline inside generator pipeline ✅ CORRECT
- `generation/backfill/` — 7 `BaseBackfillGenerator` subclasses, all correct ✅
- `shared/utils/core/property_enhancer.py` `enhance_generated_frontmatter()` — pure utility called from inside `component_generators.py` generate path ✅ CORRECT
- `scripts/maintenance/enrich_risk_fields.py` — STANDALONE enricher (530 lines); ran outside pipeline with `--dry-run`/`--apply` flags; operated on `safety_data` sub-structure never present in source data ❌ DEAD ORPHAN

### Steps
- [x] Survey all `enrich*` symbols across Python codebase
- [x] Verify `property_enhancer` is inside generator pipeline (not standalone)
- [x] Verify all `domain_adapter.py` enrich methods are inside `write_component()` path
- [x] Create `generation/backfill/risk_fields_backfill.py` as proper `BaseBackfillGenerator` subclass
- [x] Register as `risk_fields` in `BackfillRegistry`
- [x] Delete `scripts/maintenance/enrich_risk_fields.py`
- [x] **No domain config additions needed** — safety_data fields are absent from all source YAMLs (script was speculative dead code)

---

## Session 10 — Structural Parity Audit (2026-02-24)

**Goal**: Check structural parity across source data, generators, and frontmatter (excluding domain-specific prompts/fields).

### Findings & Actions

**Fixed:**
- [x] Removed orphan `micro` entry from `generation/backfill/config/applications.yaml`
  - Applications source data has no `micro`, FrontmatterFieldOrder has `content_removals: [micro]`, 0/10 frontmatter files had it
- [x] Deleted stale backup file `data/materials/Materials_before_restore_20251222_203108.yaml`
- [x] Removed dead `_load_applications_data()` backcompat wrapper from `ApplicationsCoordinator` (no callers)

**Deferred — active callers block removal:**
- [x] `domains/materials/coordinator.py` `_load_materials_data()` — **already removed** (confirmed absent; `contamination_pattern_selector.py` has its own private `_load_materials_data()` — correct, not a coordinator wrapper)
- [x] `domains/settings/coordinator.py` `_load_settings_data()` — **already removed** (confirmed absent; test file already uses `_load_domain_data()` directly)
- [x] `domains/materials/coordinator.py` `generate()` method — **evaluated: keep**. 3 active test callers. Different return type from base `generate_content()` (returns bare content, handles EEAT separately). Intentional domain-specific interface.

**Confirmed correct (no action needed):**
- All 5 domains have `export/config/`, `generation/backfill/config/` entries
- All 5 backfill configs use `multi_field_text` generator — consistent
- `CompoundCoordinator` correctly calls `_load_domain_data()` directly — canonical pattern
- `relationship_groups` only in materials export config — intentionally domain-specific
- `sluggify_filenames: true` only in compounds export config — intentional (compound IDs require sluggification)
- Existing 8 LOW parity findings from `structural_parity.py` are cosmetic module-level helper duplication




---

## 2026-02-25: Fix Raw-String faq/micro in Source YAML

**Goal**: Convert 5 unstructured raw-string fields in Materials.yaml to proper dicts.

| Material | Field | Raw pattern |
|---|---|---|
| `alabaster-laser-cleaning` | `micro` | `'BEFORE:\n\n...'` — before-only |
| `alabaster-laser-cleaning` | `faq` | `'Q: ... A: ...'` — single Q/A |
| `alumina-laser-cleaning` | `micro` | `'BEFORE:\n\n...'` — before-only |
| `aluminum-laser-cleaning` | `micro` | `'BEFORE:\n\n...'` — before-only |
| `aluminum-laser-cleaning` | `faq` | `'Q: ...\n\nA: ...'` — single Q/A |
| `steel-laser-cleaning` | `faq` | `'Q: Question 1: ... A: ...'` — single Q/A |

**Rule**: Fix at Layer 1 source data (Materials.yaml). Re-export after.

### Steps
- [x] Plan written
- [x] Write /tmp/fix_raw_strings.py via create_file tool *(completed via direct targeted source patch)*
- [x] Run fix script *(completed via direct targeted source patch)*
- [x] Verify all 5 fields are now dicts in Materials.yaml
- [x] Re-export affected materials frontmatter

---



**Order: zero-risk deletions first, then isolated fixes, then migration**

- [x] 1. Delete `app/netalux/page.old.tsx` (dead .old artifact, not imported/routed)
- [x] 2. Delete 4 `.bak``.bak` files in `z-beam-generator/data/` (Materials, Contaminants, Compounds, Settings)
- [x] 3. Remove `AuthorInfo` deprecated type alias from `types/centralized.ts` (zero callers)
- [x] 4. Fix `experience_years` snake_case in `useMicroParsing.ts` local type → `experienceYears`
- [x] 5. Remove dead `frontmatter?.lastModified` branches in `Card.tsx` + `ContaminantCard.tsx` (frontmatter never has `lastModified`)
- [x] 6. Simplify `lastModified` fallback chains in `JsonLD.tsx`, `SettingsJsonLD.tsx`, `jsonld-helper.ts`, `jsonld-schema.ts` → use `dateModified` only

---

## Batch 64: Defense Frontmatter FAQ Quality + Timestamp Consistency Check
Date: 2026-02-27
Status: IN PROGRESS

### Goal
Resolve known quality issues in `defense-laser-cleaning-applications` frontmatter by fixing FAQ content at source, re-exporting, and validating structure/schema; evaluate `dateModified` behavior against export-time UTC policy.

### Steps
- [ ] Patch source FAQ content for `defense-laser-cleaning-applications` to remove punctuation artifacts
- [ ] Re-export the single applications item to frontmatter
- [ ] Validate strict applications schema and verify no root relationship drift fields
- [ ] Record lesson in `tasks/lessons.md`

