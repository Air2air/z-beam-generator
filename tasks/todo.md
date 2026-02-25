# tasks/todo.md

All prior phase plans (Sessions 1–9) completed and removed 2026-02-24.
See `tasks/lessons.md` for lessons learned.

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
4. Cross-domain referential integrity: authorId→authors, validMaterials→materials
5. Duplicate ids within a domain
6. datePublished / dateModified presence and ISO-8601 format

**Output**: `tasks/data_audit_report.md`

### Steps
- [x] Plan written
- [x] Build `scripts/audit/data_completeness.py`
- [x] Run audit → 247 verified findings (233 CRITICAL / 6 HIGH / 8 MEDIUM / 0 LOW)
- [x] Report written to `tasks/data_audit_report.md`
- [ ] **Next**: Regenerate contaminants `description` + `micro` (~97 items) — biggest gap
- [ ] **Next**: Regenerate materials `eeat` (~21 items) + `breadcrumb` (~26 items)
- [ ] **Next**: Fix 3 materials with unstructured raw-string faq/micro (alabaster, aluminum, steel)
- [ ] **Next**: Decide if molecularWeight=null is acceptable for 4 aggregate compounds

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
- [ ] `domains/materials/coordinator.py` `_load_materials_data()` — 2 callers in `domains/materials/image/research/contamination_pattern_selector.py` (lines 213, 277). Update those callers to use `_load_domain_data()` directly, then remove wrapper.
- [ ] `domains/settings/coordinator.py` `_load_settings_data()` — callers in `tests/domains/test_settings_coordinator.py` (lines 24, 95). Update tests, then remove wrapper.
- [ ] `domains/materials/coordinator.py` `generate()` method — present in materials only; evaluate whether other domains need it.

**Confirmed correct (no action needed):**
- All 5 domains have `export/config/`, `generation/backfill/config/` entries
- All 5 backfill configs use `multi_field_text` generator — consistent
- `CompoundCoordinator` correctly calls `_load_domain_data()` directly — canonical pattern
- `relationship_groups` only in materials export config — intentionally domain-specific
- `sluggify_filenames: true` only in compounds export config — intentional (compound IDs require sluggification)
- Existing 8 LOW parity findings from `structural_parity.py` are cosmetic module-level helper duplication



