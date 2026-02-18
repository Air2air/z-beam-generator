# Prompt Chain Stabilization: Tests, Schemas, Docs, and Cleanup Analysis

**Date:** 2026-02-16  
**Scope:** Prompt validation availability, voice pattern compliance, postprocess retry-policy alignment, schema consistency, and repository cleanup review.

---

## 1) What Was Updated

### Tests (comprehensive alignment)

- Added compatibility regression tests for legacy validator imports:
  - `shared.validation.prompt_validator`
  - `shared.validation.prompt_coherence_validator`
- Added schema regression tests for `page_description` support and legacy `_description` exception behavior.
- Added unit tests for `DomainAdapter._normalize_page_description_output()`:
  - Markdown heading stripping
  - `Title:` / `Description:` wrapper stripping
  - JSON payload extraction (`sectionContent` / `sectionDescription`)
- Updated voice compliance tests to explicitly verify short-form threshold behavior:
  - Default: `required_pattern_count == 2`
  - Short-form component (`pageDescription`): `required_pattern_count == 1`
- Replaced stale `test_postprocessing_retry_policy.py` with architecture-current policy tests:
  - constants (`MAX_REGENERATION_ATTEMPTS=3`, `QUALITY_THRESHOLD=60`, `MIN_CONTENT_LENGTH=150`)
  - docstring policy assertions
  - source-level guardrail assertions for runtime retry controls

### Schemas

- Updated `data/schemas/frontmatter.json`:
  - Added explicit `page_description` property
  - Adjusted legacy forbidden pattern from `.*_description$` to `^(?!page_description$).*_description$`
  - Bumped schema version `1.0.0 → 1.1.0`
  - Updated naming-convention definitions to document the exception

### Docs

- Updated `data/schemas/README.md` version/history:
  - `2.1.0` entry documents the `page_description` exception and rationale
- Added this document as a consolidated implementation and cleanup report.

---

## 2) Why These Changes Were Necessary

1. **Prompt validation runtime issue:**
   Canonical validator modules were moved under `shared.validation.content.*`, while some call sites/tests still used legacy import paths.

2. **Voice distinctness calibration:**
   Short-form content (`pageDescription`, etc.) cannot reliably satisfy the same pattern density as longer text. Threshold must be context-sensitive.

3. **Schema drift vs generated output:**
   Frontmatter sync writes `page_description`, but schema previously banned all `*_description` fields. This was an internal contradiction.

4. **Stale policy tests:**
   Older tests referenced removed internals (`_load_frontmatter`, `_analyze_quality`) and outdated policy values (attempts=5, threshold=50).

---

## 3) Cleanup Analysis (Findings)

### A. High-priority cleanup candidates

1. **Data churn in tracked source file**
   - `data/materials/Materials.yaml` currently includes generated-content edits from local runs.
   - Recommendation: keep only intentional data changes; isolate test artifacts from source data.

2. **Binary DB churn in repo root**
   - `z-beam.db` changed during local execution.
   - Recommendation: treat as runtime artifact unless intentionally versioned; avoid committing accidental binary diffs.

3. **Policy/docs drift in comments**
   - Some module-level comments and test descriptions still reference historic values or paths.
   - Recommendation: run periodic docs-lint/grep audit for stale constants and moved module paths.

### B. Medium-priority cleanup candidates

4. **Legacy import path migration completeness**
   - Compatibility shims now exist; some modules/tests still use legacy imports.
   - Recommendation: gradual migration to `shared.validation.content.*` canonical imports while keeping shims for backward compatibility.

5. **Retry-policy assertion strategy**
   - Replace brittle deep mocks with policy + source guardrail tests in unstable orchestration modules.
   - Recommendation: keep integration tests in dedicated flows; keep unit tests focused on stable invariants.

---

## 4) Suggested Next Cleanup Pass

1. Reconcile tracked `Materials.yaml` changes (keep intentional edits only).  
2. Decide repository policy for `z-beam.db` (tracked artifact vs runtime artifact).  
3. Run a global grep pass for old validator import paths and migrate call-sites incrementally.  
4. Add a CI check that rejects accidental schema contradictions (`properties` vs `patternProperties` conflicts).

---

## 5) Validation Expectations

After this update, the following should hold:

- Legacy validator imports remain operational via shims.
- Canonical validator imports remain operational from `shared.validation.content.*`.
- `page_description` is accepted by schema while all other legacy `*_description` fields remain forbidden.
- Voice pattern threshold behavior is deterministic by component context.
- Postprocess retry policy tests reflect current values and architecture.

---

## 6) Implemented Cleanup Guardrail

- Added fail-fast schema contradiction checker:
   - `scripts/tools/validate_frontmatter_schema_conflicts.py`
- Purpose:
   - Prevents accidental contradictions where a declared property is simultaneously forbidden by `patternProperties`.
- Current result:
   - Passes against current schema (`✅ No property/patternProperties contradictions detected`).
