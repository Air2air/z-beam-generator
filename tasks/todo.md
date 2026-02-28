# tasks/todo.md

All prior phase plans (Sessions 1–9) completed and removed 2026-02-24.
See `tasks/lessons.md` for lessons learned.

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

