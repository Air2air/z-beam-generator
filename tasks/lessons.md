# Lessons Learned

- 2026-02-27: Materials source can drift between `authorId` and canonical `author` object, leaving isolated CRITICAL gaps even when most records are normalized. Rule: backfill missing `author` from `Authors.yaml` using `authorId` and keep export hydration active for legacy compatibility.

- 2026-02-27: Some material entries can miss `components` despite having stable category/subcategory peers with canonical component structure. Rule: repair isolated missing section objects using same category/subcategory donor structures to preserve contract shape without inventing new fields.

- 2026-02-27: Contaminant `validMaterials` can be present but empty for edge records; empty lists should be repaired from same category/subcategory donors before export. Rule: treat empty list on required relational fields as source data drift and backfill from nearest canonical peers.

- 2026-02-27: Mixed/variable compounds (e.g., `chemicalFormula: Various`) can have non-deterministic molecular weight, so forcing non-empty `molecularWeight` creates false HIGH findings. Rule: completeness audits must allow missing `molecularWeight` only for explicitly variable/mixed compounds while keeping strict checks for determinate compounds.

- 2026-02-27: Materials records can retain missing `breadcrumb` arrays while still carrying canonical `fullPath` and category metadata, creating avoidable CRITICAL completeness failures. Rule: backfill missing breadcrumbs from canonical path identity (`Home` → `Materials` → category → item label), then re-export and re-validate parity/schema.

- 2026-02-27: Materials records can retain missing `breadcrumb` arrays while still carrying canonical `fullPath` and category metadata, creating avoidable CRITICAL completeness failures. Rule: backfill missing breadcrumbs from canonical path identity (`Home` → `Materials` → category → item label), then re-export and re-validate parity/schema.

- 2026-02-27: Contaminants source data can miss root `description` at scale even when `pageDescription` exists, creating large CRITICAL completeness gaps. Rule: run structured source backfill (`description <- pageDescription`) for missing entries and immediately re-run completeness validation to verify CRITICAL delta.

- 2026-02-27: Report-only completeness audits can look healthy while CRITICAL/HIGH gaps persist because they always exit success. Rule: run completeness as a thresholded validator in CI (`--max-critical 0 --max-high 0`) and persist JSON/markdown artifacts for triage.

- 2026-02-27: Field-order audits can produce false parity failures when required-field completeness checks are coupled to ordering validation logic. Rule: keep ordering validation and completeness validation as separate gates, and only enable required-field enforcement explicitly when running completeness audits.

- 2026-02-27: Author hydration can silently skip legacy shapes when export assumes only `authorId` or fully-hydrated `author` objects. Rule: treat scalar `author`, partial `author` objects, and `authorId` as valid input forms and normalize all of them to the canonical full `author` object during export.

- 2026-02-27: A single legacy root `description` field can fail strict schema validation even after broad pipeline fixes. Rule: enforce export-time cleanup of schema-forbidden legacy root fields (`description`, legacy snake_case duplicates) so outlier source records cannot bypass contract.

- 2026-02-27: Line-based removal of YAML keys can break multiline scalar blocks and invalidate source files during bulk cleanup. Rule: for domain-wide field deletions, use structured YAML parsing/writing and always run strict validator immediately after write.

- 2026-02-26: Enforcing a new removed-field contract directly on legacy-rich source data can fail CI before phased cleanup lands. Rule: ship a CI-default validator for prompt/schema wiring first, and expose strict source-data scans as explicit flags (`--check-settings-data`) until data migration is completed.

- 2026-02-27: Settings `machineSettings` can accumulate verbose leaf `description` text that bloats prompt factual payloads and leaks into exported frontmatter shape. Rule: strip leaf `description` fields from machine-settings prompt payload assembly and enforce export contract as `machineSettings._section` followed by leaf setting objects.

- 2026-02-26: Domain content prompt sections can gradually absorb voice/humanness directives unless separation is explicitly validated at assembled-prompt level. Rule: enforce component/content sections as content-only and treat any voice/humanness directives there as hard separation violations, keeping voice and humanness centralized and reusable.

- 2026-02-26: Residual documentation wording can keep implying section metadata is UI/technical payload even after contract updates, causing repeated semantic drift. Rule: whenever `sectionMetadata` is documented, describe it explicitly as developer-facing text that explains whole-section function.

- 2026-02-26: Schema/policy docs can drift and describe `sectionMetadata` as technical/UI metadata, which conflicts with prompt/export contract intent. Rule: define `sectionMetadata` consistently as developer-facing text that explains the function of the whole section.

- 2026-02-26: `sectionMetadata` can be misused as UI config (`icon/order/variant`) or as a section key label, which obscures its contract role for prompt authors and maintainers. Rule: treat `sectionMetadata` as required developer-facing intent text that explains the function of the whole section.

- 2026-02-26: Section prompt metadata can drift when domain `content_prompts.yaml` entries add new section keys without the full metadata triplet. Rule: enforce `section_prompt_metadata` as a strict text contract where every entry includes non-empty `sectionTitle`, `sectionDescription`, and `sectionMetadata`, and validate it in `PromptRegistryService`.

- 2026-02-26: Mirroring nested section containers to root-level keys in materials (`properties.materialCharacteristics` → `materialCharacteristics`, `properties.laserMaterialInteraction` → `laserMaterialInteraction`) creates duplicate section paths and contract ambiguity while source data remains canonical nested-only. Rule: keep canonical nested section paths and avoid export-time root mirrors unless an explicit frontend contract requires them.

- 2026-02-26: Domain configs may skip `section_metadata` tasks (contaminants/settings/compounds), so section contract enforcement must also exist in shared cross-domain paths. Rule: enforce `_section` placement, ordered `_section` keys, and `sectionMetadata` fallback in the universal `field_ordering` task so contract hardening applies consistently across all domains.

- 2026-02-26: Section metadata completeness is insufficient without deterministic key order; downstream audits can pass field presence but still fail contract checks when `_section` is not first or required metadata keys are unordered/missing. Rule: enforce `_section` as first field in section containers and emit ordered `_section` keys (`sectionTitle`, `sectionDescription`, `sectionMetadata`, then display fields) during export generation.

- 2026-02-26: Section metadata requirements can drift unless field order is explicitly documented at both the container level (`_section` first) and `_section` subfield level (`sectionTitle`, `sectionDescription`, `sectionMetadata` first). Rule: keep ordering contracts in `FrontmatterFieldOrder.yaml` and policy docs aligned before scaling to other domains.

- 2026-02-26: Materials frontmatter can look section-complete while still missing the newer `sectionMetadata` field at scale. Rule: run domain-wide audits for each required section field (`_section.sectionTitle`, `_section.sectionDescription`, `_section.sectionMetadata`) before declaring integration complete.

- 2026-02-26: Pre-generation validators that depend on legacy `material_index` keys can fail against canonical source shape (`materialIndex`) and wrongly classify valid material slugs as missing. Rule: resolve validation context from canonical `materials.<slug>` entries (including `category`) and treat index maps as optional metadata, not required lookup keys.

- 2026-02-26: Validation orchestrators can look healthy in integrated export flows while failing in standalone invocation due to stale import paths and API drift (`materials.services.validation_service`, old content-validator path, missing pre-generation method). Rule: keep service import paths module-accurate and preserve compatibility methods expected by orchestrators before claiming E2E readiness.

- 2026-02-26: Full export can pass while standalone validation service entry points still fail in direct invocation because of dependency/path drift (e.g., `materials` module import path and missing schema JSONs at implicit locations). Rule: final E2E readiness checks must include direct entry-point smoke tests, and readiness should be scored lower until those service-level invocation contracts are proven in the target runtime context.

- 2026-02-26: Validation entry points that infer lifecycle phases or schema paths (`phases=None` and implicit `Path("schemas")`) can hide invocation/config drift and produce environment-dependent behavior. Rule: require explicit phase lists and explicit schema directories at entry points; wrappers may pass explicit values but must not rely on hidden defaults.

- 2026-02-26: Validation and adapter paths that substitute alias root keys or synthesize placeholder identity (`name` fallback, unknown material, silent `return []`) can hide source/config drift and let malformed data pass checks. Rule: require explicit configured root keys and required validation inputs, and raise structured errors instead of silent fallback returns.

- 2026-02-26: Field alias routing and source-root loading that silently fall back (`aliases.get(field, field)` or missing-root empty dict/list returns) can hide bad CLI requests and data contract drift. Rule: treat unknown fields and missing source roots as hard errors and require explicit registration/keys before proceeding.

- 2026-02-26: Export task handlers that silently default task settings (for SEO fields, FAQ normalization target paths, or library task toggles) can hide misconfigured task definitions and produce inconsistent output shape. Rule: task handlers must validate required task-config keys explicitly and fail fast when keys are missing.

- 2026-02-26: Command-layer compatibility fallbacks (legacy data loaders, implicit router type fallbacks, and missing config-key defaults) can hide orchestration misconfiguration and route work down the wrong pipeline. Rule: command/orchestration paths must require explicit config and routing contracts and fail immediately when contract resolution fails.

- 2026-02-26: Runtime helpers that return empty strings or synthetic quality scores (for example missing applications context or placeholder humanness values) can hide source-data contract violations and produce false-green quality signals. Rule: replace placeholder/empty fallbacks with explicit exceptions so missing required context fails fast.

- 2026-02-26: Export runtime defaults on required config and author identity fields can silently mask source/config drift and let bad metadata through (`items_key`/`id_field` and author `name`/`country` falling back to placeholders). Rule: treat these as required contracts and fail fast in exporter/generator initialization instead of defaulting.

- 2026-02-26: `field_ordering` export can fail domain-wide when a domain extension omits any required group in `FrontmatterFieldOrder.yaml` (including empty groups). Rule: every domain extension must explicitly include `identity_additions`, `content_additions`, `content_removals`, and `domain_sections` (use `[]` when empty) before running `--export-all`.

- 2026-02-26: Export configs can appear healthy on macOS while still being wrong for CI/Linux if source file casing is mismatched (`Contaminants.yaml` vs `contaminants.yaml`). Rule: always use exact on-disk filename casing in `export/config/*.yaml` source paths to keep exports portable.
- 2026-02-26: Section metadata tasks must point to the shared schema definitions file, not the domain export config itself, or they silently load zero definitions. Rule: configure `section_metadata.config_file` to `data/schemas/section_display_schema.yaml` unless a domain-specific schema file is explicitly intended.

- 2026-02-26: Category metadata titles that already include the site suffix (e.g., `... | Z-Beam`) will be duplicated by the global layout title template (`%s | Z-Beam`). Rule: store category/item titles as content-only strings and let the layout template append the site suffix exactly once.

- 2026-02-26: Metadata generators can silently fall back to generic site titles when author shape drifts (object vs scalar), because optional social fields may throw (`author.name.replace`). Rule: treat author as schema-optional and guard `author.name` before deriving OpenGraph/Twitter metadata; never let optional author fields crash page metadata generation.

- 2026-02-26: Item metadata fallback that returns site short name (`Z-Beam`) can combine with layout templates (`%s | Z-Beam`) and collapse many pages into duplicate titles. Rule: item-page metadata must always derive a content-specific fallback title (for example from slug) and only enforce URL mismatch fallbacks when category/subcategory are actually resolved.

- 2026-02-26: Production validation severity drift can happen at individual check level (for example duplicate-title checks downgraded to warnings). Rule: keep duplicate metadata checks strict unless there is an explicit approved policy exception; only allowlisted cases (like known noindex paths) should bypass failure.

- 2026-02-26: Script aliases in package commands can create false green signals when they map to unrelated checks (for example JSON-LD or redirects aliases that only run generic validation). Rule: keep script names behaviorally exact; remove or rename aliases that do not execute the promised validation.

- 2026-02-26: Post-deploy orchestration drift can silently downgrade critical checks (performance/production) to advisory, allowing unhealthy deployments to pass. Rule: keep core categories (functionality/content/seo/performance/accessibility/production) fail-fast by default; only explicitly optional checks may be non-blocking.

- 2026-02-26: Aggressive global text replacement can introduce semantic drift (duplicate entries, broken doc paths, duplicated provider lists) even when command succeeds. Rule: after bulk terminology changes, always run residual grep + targeted sanity grep for known over-replacement patterns before marking sweep complete.

- 2026-02-26: Broad provider rename sweeps can break operator workflows if CLI flags/scripts are renamed without transition paths. Rule: when normalizing naming (Winston → Grok), rename primary commands/files but keep compatibility aliases for legacy flags until all docs and automation are fully migrated.

- 2026-02-26: Removing a provider from active runtime can break legacy tests/callers that still construct objects with deprecated arguments. Rule: keep backward-compatible constructor parameters/attributes as no-op shims while redirecting all live execution paths to the new Grok-only evaluator.

- 2026-02-26: Partial disable flags are insufficient when protected generator code still runs a direct Winston check path. Rule: when switching to Grok-only quality checks, replace the generator’s direct detection call path itself so no Winston client/dependency is required at runtime.

- 2026-02-26: New evaluator wiring can stall if persistence is postponed; runtime calls should only ship with same-turn DB write methods and schema initialization in the unified learning system. Rule: when adding a new quality evaluator, implement invocation + validated payload persistence keyed by `generation_id` in one change set.

- 2026-02-26: New evaluator systems are fastest to adopt when they are additive and foreign-keyed to existing generation logs, rather than replacing the base `generations` schema on day one. Rule: ship schema + prompt contract + side-table migration keyed by `generation_id`, then phase gates from advisory to strict.

- 2026-02-26: Postprocess retries were passing `skip_learning_evaluation=True`, which reduced learning signal fidelity during the exact loop meant to improve low-quality outputs. Rule: retry orchestration must call `generator.generate()` without skip-learning flags so each retry attempt is fully evaluated and logged.

- 2026-02-26: A Winston-disabled green run can hide true production AI-detection behavior; quality/learning signals must be verified with Winston explicitly enabled before claiming closed-loop readiness. Rule: run a controlled 5-domain Winston-on benchmark (`WINSTON_USAGE_MODE=always`, no disable flags) and capture per-domain exit code + `generation_id` evidence.

- 2026-02-26: Source saves can preserve legacy `authorId` shape even after manual normalization, causing evaluator logging to fail when downstream code expects `author.id`. Rule: normalize author identity in-memory at data adapter load time (`authorId` → `author.id`) so runtime consumers stay stable without protected-core rewrites.

- 2026-02-26: Temporary Winston bypass must be implemented in non-protected integration/orchestration layers, not by editing protected generator cores. Rule: use an explicit environment switch (`DISABLE_WINSTON`/`WINSTON_USAGE_MODE=disabled`) in coordinator + `WinstonIntegration` so generation wiring stays intact while detection calls are safely skipped.

- 2026-02-26: Postprocess command drifted from the current FieldRouter API (`FieldRouter.FIELD_ALIASES` no longer exists), causing startup crashes before retry/quality logic ran. Rule: avoid static router constants in commands; always read aliases from `FieldRouter` runtime config accessors.

- 2026-02-25: Mirroring prompt examples across domains must use live frontmatter section-key unions, not schema assumptions. Rule: generate example `section_prompts` from each domain’s exported relationships keys, then validate exact set parity and required metadata triplet (`sectionTitle`, `sectionDescription`, `sectionMetadata`) per key.

- 2026-02-25: Prompt intent text and section presentation metadata drift unless they are validated together. Rule: enforce `section_prompt_metadata` for every `section_prompts` key (`sectionTitle`, `sectionDescription`, `sectionMetadata`) and run a parity validator against live frontmatter + frontend union types (`RelationshipCategory`, `RelationshipKey`).

- 2026-02-25: "Mirror" examples must be validated against real exported page section keys, not assumed schema names. Compounds used live keys (`detectionMonitoring`, `producedFromMaterials`) that diverged from schema/prompt names (`continuousMonitoring`, `producedByMaterials`). Rule: derive canonical section keys from frontmatter/source data first, then add schema aliases/prompt mappings so all layers align.

- 2026-02-25: `content_prompts.yaml` examples must reflect domain scope and schema separately: compounds prompt examples should not include materials-only sections like `micro`, while frontend `_section` compatibility requires explicit `sectionTitle`/`sectionDescription` in `section_display_schema.yaml` (or guaranteed enrichment defaults). Rule: validate both contracts together (prompt scope + section metadata fields) before declaring schema alignment.

- 2026-02-25: Example prompt files that don't match `PromptRegistryService` contract (`schemaVersion`, `domain`, `extends`, `descriptor_prompts`, optional `section_prompts`) are easy to misread as valid but won't reflect runtime behavior. Rule: keep examples schema-shaped exactly like `prompts/*/content_prompts.yaml`, and put subject/context binding notes in comments unless loader support is added.

- 2026-02-25: New long-running SEO checks should be added to the dedicated SEO CI workflow, not predeploy, to protect local developer velocity and avoid flaky gates. Rule: wire advanced/esoteric checks in `seo-tests.yml` using soft mode + bounded scope, then verify with a focused integration test.

- 2026-02-25: End-to-end esoteric SEO checks can be flaky in automation if strict/blocking behavior is mixed with broad crawl scope. Rule: provide a dedicated soft-mode command (`STRICT_MODE=0`, bounded `MAX_URLS`) and cover it with one focused integration test that asserts non-blocking execution.

- 2026-02-25: Advanced validation policy (advisory vs strict) is easy to regress if implemented only through CLI side effects. Rule: expose minimal pure helper functions for policy decisions (`count`, `outcome`) and cover them with focused unit tests while keeping script runtime behavior unchanged.

- 2026-02-26: Advanced SEO validators can surface legitimate data/graph issues (e.g., `sameAs` URL quality, cross-page `@id` type drift) that should not always block deployment. Rule: default new advanced checks to advisory mode with explicit `--strict` enforcement, emit machine-readable reports, and wire them as non-critical in postdeploy until data is remediated.

- 2026-02-25: Post-deploy validators can fail for validator drift and strictness mismatch even when deploy succeeds (e.g., outdated JSON-LD expectations, over-strict Lighthouse checks, canonical mismatch detection from layout-level canonical defaults). Rule: isolate failures by running each failed validator command directly, then fix validator expectations or metadata source logic at root before rerunning aggregate postdeploy.

- 2026-02-25: Universal `_section` enforcement logic only runs in domains that include the `section_metadata` export task. Rule: when adding/strengthening section metadata logic, verify each domain config (especially applications) includes `section_metadata`; otherwise required fields won't be populated for that domain.

- 2026-02-25: Section metadata population that depends only on configured mappings can leave existing `_section` blocks partially populated (e.g., `sectionDescription` present but missing `sectionTitle`). Rule: run a universal final pass over all `_section` blocks in export output to enforce required keys (`sectionTitle`, `sectionDescription`) regardless of mapping coverage.

- 2026-02-25: When normalizing source `micro`/`faq` from raw strings to dicts, validate frontmatter expectations per field before enforcing parity checks. Rule: exported materials may omit top-level `micro`; verification should reject raw-string shape but not fail on intentional omission.

- 2026-02-25: When a previously failing workflow step is queued for follow-up, re-run the exact validator/build command first before editing code. Rule: if `validate:metadata` returns 0 errors/0 sync issues and `prebuild` exits 0, close the task as verified recovery and avoid unnecessary source changes.

- 2026-02-25: After fixing duplicate-key risks in source YAML, always complete the loop with domain re-export plus explicit raw-text key-count validation on source and schema-shape validation on frontmatter (`author` object with `id`). Rule: "fixed in source" is incomplete until export+validation both pass.

- 2026-02-25: VS Code tasks and git hooks can drift to deleted local script paths (`./scripts/audit/quick-audit.sh`, `enforce-component-rules.js`) even while docs/CI expect npm entry points. Rule: define canonical quality commands in `package.json` scripts (`component-audit`, `enforce-components`) and have tasks/hooks call those scripts instead of direct file paths.

- 2026-02-25: Duplicate YAML keys in source data silently create downstream schema corruption (`author` object overwritten by later scalar `author: <id>`). Rule: never store both author object and scalar reference under the same key; keep one canonical `author` object key in source YAML and re-export immediately after cleanup.

- 2026-02-25: Metadata validators must match the actual exported frontmatter schema, not assumed migration state. `validate-metadata-sync` hard-required `author.id` while current materials frontmatter stores scalar `author` references, causing false prebuild failures. Rule: when validator errors affect many files uniformly, inspect a real frontmatter sample first and implement schema-aware validation (accept canonical + active representation) before touching content files.

- 2026-02-25: NEVER use heredoc or multi-line echo in run_in_terminal to create files. The VS Code integrated terminal cannot reliably deliver multi-line content — it truncates, splits, or never fires the EOF delimiter, producing empty or partial files and spawning retry terminals that pile up. Rule: ALL file creation (including /tmp/*.py probe scripts) MUST use the create_file tool. Then execute with a single one-line terminal call: `python3 /tmp/script.py`.

- 2026-02-25: When a terminal command exits with code 130 (Ctrl+C) or never returns, do NOT re-run the same command. That is a hang. Immediately change strategy: narrow test scope to one file, add isBackground:true + timeout, or use --tb=no -q with a specific test path. Repeating the same blocking command is detectable from the terminal history (same last command, same exit code) and is a Grade F violation. Rule: exit code 130 = mandatory strategy change before any retry.

- 2026-02-24: Standalone maintenance scripts that read/write source YAML outside the generator pipeline (even with --dry-run/--apply guards) ARE enrichers and violate Core Principle 0.6. The correct pattern is always `BaseBackfillGenerator`. Always check `scripts/maintenance/` for orphan enrichers during architectural audits.
- 2026-02-24: Before converting a standalone enricher to a backfill generator, grep the actual source YAML for the field it transforms. A standalone enricher script operating on data that does not exist in the source files is speculative dead code — delete it, replace it with the clean backfill pattern, and document why no domain config entry is needed yet.
- 2026-02-24: COMPLEX tasks must write plan to tasks/todo.md FIRST before any tool calls — using the in-memory todo tool only violates the instruction. Both must be kept in sync.
- 2026-02-24: Validator source key (`contamination_patterns`) can silently diverge from actual data key (`contaminants`) when data schema evolves — always grep the actual YAML top-level key before writing validator code that accesses it.
- 2026-02-24: When tests reference bare material IDs (e.g., `source_id == 'steel'`) but data uses suffixed form (`steel-laser-cleaning`), run a normalization script to strip the suffix from the flat associations list — not a test bug, a data model consistency gap. Fix at source (the YAML).
- 2026-02-24: Stale metadata `breakdown` values in association files cause count mismatch test failures — always update `breakdown` and `total_associations` in metadata after any bulk data change or normalization pass.
- 2026-02-24: Compound byproduct associations (`generates_byproduct`/`byproduct_of`) are a distinct data gap from material-contaminant associations. If tests require them, they must be explicitly generated from chemistry knowledge and added to the YAML. Cannot be deduced from the existing material↔contaminant data alone.
- 2026-02-24: `FrontmatterFieldOrder.yaml` domain extension validation requires ALL four groups (`identity_additions`, `content_additions`, `domain_sections`, `content_removals`) even if empty. Adding a domain section without `content_removals: []` causes a `RuntimeError` in the validator.

- 2026-02-23: When the workflow is updated, replace prior workflow text and rebase plans to follow the new session ritual and plan verification steps.
- 2026-02-23: Never trust a conversation summary's claim that source data is "already normalized." Always run a direct check (grep or python) on the actual file before planning. The summary said Applications.yaml was correct; it was not.
- 2026-02-23: Do not patch the export pipeline to compensate for incorrect source data. Fix the source data first, then re-export. Patching exporters mid-investigation before understanding the full picture caused an incorrect fix that had to be reverted.
- 2026-02-23: After modifying source data and re-exporting, always check for stale frontmatter files from the old naming convention. The re-export created new files but left the old ones in place — both sets existed until explicitly deleted.
- 2026-02-24: Node.js `http.get(url, { timeout })` only fires the 'timeout' event but does NOT abort the request. Always use `req.setTimeout(ms, cb)` with a callback that calls `req.destroy()` to actually cancel the request. Pre-existing validation scripts used the inert form and hung indefinitely in postdeploy.
- 2026-02-24: `generateBreadcrumbs()` required an explicit `breadcrumb:` array in frontmatter. 26 material pages were never exported with that field. Fix: auto-derive from `fullPath` (always present) when the explicit array is absent. Must fix at the code layer, not by patching 26 YAML files directly → rule: fix at source (Layer 2 code fix, not Layer 1 data patch).
- 2026-02-24: `chrome-launcher` does not auto-discover Chrome on macOS when Chrome is not in PATH. Performance validation scripts silently fail or hang. Fix at the runner level: auto-set `CHROME_PATH` when the macOS standard path is present. Do not hardcode in individual scripts.

- 2026-02-24: Generator field name mismatch (`breadcrumbs` written, `breadcrumb` read) caused silent export failures — field was absent from all generated output. Rule: always grep the consuming TypeScript type for the exact field name before naming a new generator output field.
- 2026-02-24: Grepping thin Next.js route-delegate files ([slug]/page.tsx) for schema injection returns false negatives — those files only re-export from a shared factory. Always trace through to the rendering layer (ItemPage.tsx, createContentPage.tsx) before concluding schema coverage is missing.
- 2026-02-23: TypeScript discriminated union on `any`-typed property fails to narrow sibling fields → Always use a concretely-typed property (not `any`) as the discriminant, or destructure with an explicit cast after checking the absent-data side

## 2026-02-23 — Backend Consolidation

- 2026-02-23: "0 callers" grep can miss callers via __init__.py re-exports — always grep the symbol name directly AND check package __init__ re-exports before deleting → Rule: `grep -rn "symbol_name" .` is not sufficient; also check `grep -rn "from package import" .` to find indirect callers
- 2026-02-23: shared.generation yaml_helper/author_helper appeared dead but were exposed via shared/generation/__init__.py and used by component_summaries_handler → Rule: Before deleting any module, grep the full symbol name across all .py files, not just the import path
- 2026-02-23: Validation shims (contamination_validator, schema_validator, prompt_validator, prompt_coherence_validator) — confirmed pattern: when a shim's deprecation message says "use X instead", X is the correct redirect target
- 2026-02-23: author_manager inversion (shared importing from export) — fix by cop- 2026-02-23: author_manager inversion (shared importing from export) — fix by cop- 2026-0eed- 2026-02-23: author_manager inverection should always flow export→shared, never shared→export

## 2026-02-23 — YAML + Validator Consolidation

- 2026-02-23: yaml_io.py and yaml_utils.py had near-identical functions (load_yaml, save_yaml, validate_yaml_structure) — canonical is the one with most callers (17 vs 2); fix by redirecting minority callers → Rule: when two files have same function names, count callers to identify canonical
- 2026-02-23: yaml_loader.py had genuinely different implementation (C-based LibYAML loader, 10x faster) — merge the functions into yaml_utils, shim the old path → Rule: before aliasing a "fast" variant away, verify it's actually the same implementation
- 2026-02-23: validator.py was named generically but contained the "Unified Prompt Validator" — rename to match actual purpose (unified_validator.py); shim old path for backward compat → Rule: file names should describe what they are; if docs/deprecation notices call it by a different name, rename the file
- 2026-02-23: Docs- 2026-02-23: Docs- 2026-02-23: Docs- 2026-02-23: Docs- 2026-02-23: Docs- 2026-02-23:  as- 2026-02-23: Docs- 2026-02-23: Docs- 2026-02-2ide a triple-quoted string before acting on it

## 2026-02-23 — Prompt Validator Collapse

- 2026-02-23: DeprecationWarning on import in prompt_validator.py fired on every generator.py run — caused by a premature deprecation notice (no equivalent replacement actually existed yet); fix by moving implementation to canonical and making shim warning-free → Rule: only emit DeprecationWarning when a true equivalent replacement exists at the suggested import path
- 2026-02-23: content_validator.py already existed for a completely different purpose (wraps shared.validation.core.content.ContentValidator) — always check target filename before creating → Rule: list directory before choosing a filename for any new file
- 2026-02-23: Two files serving related but distinct purposes (text/image validation vs coherence validation) can be combined into one canonical when they live in the same package and have no circular dependence — shim the old paths for zero caller disrupti- 2026-02-23: Two files serving related but distinct purposes (text/image validatiout - 2026-02-23: Two files serving related btion

## 2026-02-23 — Validation Shim Cleanup + Namespace Collapse

- 2026-02-23: 5 validation shims had warnings.warn() firing on every import — suppressed by callers using -W ignore, creating silent noise; found by running -W error::DeprecationWarning → Rule: always verify shim cleanup with -W error::DeprecationWarning, not just -W ignore
- 2026-02-23: quality_validator.py and post_generation_service.py had DeprecationWarning at top but were actual 225/556-line implementations, not shims — the warning was premature and incorrect → Rule: never add DeprecationWarning to a file unless a true equivalent replacement path exists AND has been verified
- 2026-02-23: shared/services/validation/ was a stray namespace with 1 external caller — collapsed by copying files to shared/validation/services/, updating the caller, replacing old __init__ with absolute-import shim; old relative imports in shim would have broken silently → Rule: when shimming a package, use absolute imports (from shared.x.y import Z) not r- 2026-02-23: shared/services/validation/ was a stray namespas no longer exist at the relative path

## 2026-02-23 — Leftover Cleanup + Dead Code Removal

- 2026-02-23: Archiving source files from a shimmed package breaks any __init__.py that used relative imports to those same files — shared/services/__init__.py had `.validation.orchestrator` relative import alongside the shim → Rule: when archiving source files, grep for relative imports (from .module import) not just absolute (from package.module import)
- 2026-02-23: shared/commands/common.py had get_research_service() importing a module that does not exist (property_research_service.py) — dormant crash, 0 callers; git diff confirmed pre-existing → Rule: a function in __all__ with 0 callers is a dead-code candidate; confirm with grep before leaving it

## 2026-02-23 — Production Bug Fix + Dead Code Archive (session 7)

- 2026-02-23: domains/materials/utils/property_enhancer.py had same function name as shared/utils/core/property_enhancer.py but was a 21-line no-op stub (return content as-is) — component_generators.py used the stub, silently skipping enhancement in production → Rule: when two files share a function name, diff their implementations; a file that returns its input unchanged is a stub, not an implementation
- 2026-02-23: domains/contaminants/contamination_levels.py was a 171-line near-copy of shared/types/contamination_levels.py with 0 callers — diverged on 2 "dirt" vs "dust" string differences, making it a data drift risk → Rule: domain-level copies of shared type data files are drift risks; grep callers before concluding which is live
- 2026-02-25: Before marking domain coordinator methods as "duplicates to push to base," read the base class first. `BaseDataLoader._validate_loaded_data` and `_get_data_file_path` were already abstract — the domain implementations ARE the intended interface. Structural parity checks flag method name overlap, not intent.
- 2026-02-25: `test_humanness_optimizer.test_init_requires_template_file` assertion tied to whichever file the optimizer fails on first — fragile. Fix: assert on "Required YAML file not found" generically rather than a specific filename that changes when optimizer initialization order changes.
- 2026-02-25: Parity audit flagging "same method in N domains" can reveal copy-paste bugs, not just consolidation opportunities. CompoundsDataLoader had 9 methods referencing uninitialized file path attributes — all copy-pasted from MaterialsDataLoader but never connected. Always check if the methods actually work before deciding to consolidate vs delete.
- 2026-02-25: Structural parity audit scripts must be aware of @abstractmethod patterns — flagging all method-name overlaps conflates "must implement per-domain" (abstract) with "could share" (genuine duplicate). Also always verify base class file paths in the audit logic (wrong path → false loader_gap findings).
- 2026-02-25: Before archiving a file, verify ALL import paths — `PatternDataLoader` name existed in both `pattern_loader.py` (legacy, 570 lines, only callers in tests/obsolete/) and as a live alias `= ContaminantsDataLoader` in `data_loader_v2.py`. Moving the legacy file is safe only because production imports via the alias, not the legacy module path. Always grep both the symbol name AND the module path separately.
- 2026-02-25: Audit script false positives from by-design patterns (all domain coordinators named coordinator.py, all loaders named data_loader_v2.py) inflate HIGH/MEDIUM counts and erode trust in the report. Use explicit exclusion constants (`BY_DESIGN_FILENAMES`, `IMPORT_DRIFT_EXEMPT_DOMAINS`) rather than ignoring the audit — adds knowledge, reduces noise.
- 2026-02-24: `get_loader()` module-level singleton pattern is identical across 4 domains by necessity — `global _loader_instance` scopes the singleton to its module. Moving to shared would collapse all domains onto one instance and lose typed return values. Audit false positive; suppress with BY_DESIGN_MODULE_FUNCS, don't try to consolidate.
- 2026-02-24: Inline imports (`from shared.exceptions import ConfigurationError` inside method bodies) are antipattern — each raise site re-imports at call time. Fix by adding once at module level. Audit correctly flagged the *drift* but the fix is inline→module-level, not adding the import to domains that don't raise it. Error types are raise-on-need, not universal infrastructure; exempt from import drift with IMPORT_DRIFT_EXEMPT_SYMBOLS.
- 2026-02-24: Archiving files to legacy/ subdirs doesn't silence audit findings unless the audit explicitly skips legacy/ during file collection. rglob("*.py") traverses all subdirectories. Always add the corresponding scan exclusion when archiving code.
- 2026-02-24: Domain clear_cache() overrides use cache_manager.invalidate() while BaseDataLoader.clear_cache() uses self._cache.clear() — two different caching systems. Same name ≠ same purpose. Verify base implementation before labeling as "duplicate"; here it's a legitimate override of a different subsystem.
- 2026-02-24: When a module has low caller count, always read its docstring/header to determine if it's a canonical or a shim — a shim can have 182 callers while the canonical it wraps has 3; grep caller count alone misleads in this topology. Rule: read the first 10 lines of any file before concluding it's dead.
- 2026-02-25: FIELD_NAMING_REFERENCE exceptions table stated `author.country_display`, `author.persona_file`, `author.formatting_file` "retain underscores in both layers" — they don't; the exporter explicitly converts them to camelCase (`countryDisplay`, `personaFile`, `formattingFile`). Rule: always verify exception claims against actual exported frontmatter YAML, not just the doc.
- 2026-02-25: `author.id` was documented as `string` in FIELD_NAMING_REFERENCE but is `number` everywhere (frontmatter, TypeScript interface, integration test). Rule: when a type in the doc differs from the TS interface and the actual YAML, the doc is wrong — source of truth is the exported data.
- 2026-02-25: TypeScript `Author` interface had ~10 snake_case optional fields (`experience_years`, `verification_level`, etc.) violating the camelCase TS convention. Rule: TypeScript interfaces must use camelCase regardless of origin — Python/backend snake_case names must be converted at the type boundary.
- 2026-02-25: TypeScript `dateModified` was marked `@deprecated Use lastModified instead` in `ArticleMetadata` and 4 other interfaces — the deprecation was backwards. `dateModified` is the canonical frontmatter field; `lastModified` is the legacy alias. Fixing the type in one interface may unmask pre-existing errors in other files that were suppressed by the earlier type error in the same file. Rule: always run `tsc --noEmit` after type-level changes and separate pre-existing from newly introduced errors using `git diff --name-only`.
