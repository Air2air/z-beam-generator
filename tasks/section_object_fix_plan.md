# Section Object Remediation Plan (All Domains)

Generated: 2026-03-02
Input report: tasks/section_object_missing_report.json

## Scope
Fix missing nested `_section` objects at source/generator layers so exports produce compliant frontmatter across all domains.

## Priority Order
1. compounds.faq (34 files)
2. materials.relationships.contaminatedBy (2 files)
3. materials.properties.materialCharacteristics (1 file)
4. materials.properties.laserMaterialInteraction (1 file)
5. materials root-level orphan `_section` cleanup policy

## Domain-by-domain Fix Plan

### 1) Compounds — `faq` missing nested `_section` (34)
- Source of truth to fix: compounds source data + export normalization for FAQ shape.
- Required target shape:
  - `faq._section.sectionTitle`
  - `faq._section.sectionDescription`
  - `faq._section.sectionMetadata: faq`
  - `faq.presentation`
  - `faq.items[]`
- Implementation:
  - Add/normalize `faq` object in source compound records.
  - Ensure exporter transforms any scalar/list FAQ into canonical object with `_section`.
  - Fail fast if `faq` exists but is not object after normalization.
- Verify:
  - Re-export compounds.
  - Re-run section-object audit script and parity validator.

### 2) Materials — `relationships.contaminatedBy` legacy scalar at root (2)
- Affected files:
  - `alabaster-laser-cleaning.yaml`
  - `steel-laser-cleaning.yaml`
- Source of truth to fix: materials source relationship schema + exporter cleanup.
- Required target shape:
  - Remove legacy root `relationships.contaminatedBy` scalar.
  - Keep canonical `relationships.interactions.contaminatedBy` object with nested `_section`.
- Implementation:
  - Add cleanup rule in exporter to strip legacy root relationship scalar keys.
  - Backfill source records if legacy keys are still produced upstream.
- Verify:
  - Re-export affected materials.
  - Confirm only canonical nested relationship path remains.

### 3) Materials — `properties.materialCharacteristics` missing nested `_section` (1)
- Affected file:
  - `steel-laser-cleaning.yaml`
- Source of truth to fix: materials source properties schema + generator section metadata production.
- Required target shape:
  - `properties.materialCharacteristics._section.sectionTitle`
  - `properties.materialCharacteristics._section.sectionDescription`
  - `properties.materialCharacteristics._section.sectionMetadata: properties.materialCharacteristics`
- Implementation:
  - Ensure source record carries section container object, not scalar/flat keys.
  - Ensure export/generator injects `_section` for this container when missing.
- Verify:
  - Re-export steel material.
  - Confirm nested `_section` exists.

### 4) Materials — `properties.laserMaterialInteraction` missing nested `_section` (1)
- Affected file:
  - `steel-laser-cleaning.yaml`
- Source of truth to fix: same as above.
- Required target shape:
  - `properties.laserMaterialInteraction._section.sectionTitle`
  - `properties.laserMaterialInteraction._section.sectionDescription`
  - `properties.laserMaterialInteraction._section.sectionMetadata: properties.laserMaterialInteraction`
- Implementation and verification:
  - Same workflow as materialCharacteristics.

### 5) Materials — Root-level orphan `_section` policy (153)
- Current issue:
  - Root `_section` exists in all materials frontmatter files.
- Policy decision required:
  - If root `_section` is deprecated, remove in exporter cleanup.
  - If required by contract, formally document it and exclude from violation checks.
- Recommended:
  - Deprecate root `_section` for materials and keep `_section` only at actual section containers.

## Execution Sequence
1. Patch exporter normalization/cleanup rules (single source behavior).
2. Patch source data outliers (steel + legacy contaminatedBy records).
3. Re-export only affected domains/items first.
4. Re-run:
   - `tasks/section_object_audit_all_domains.py`
   - field contract parity validation
5. If green, run broader domain export as needed.

## Acceptance Criteria
- `tasks/section_object_missing_report.json` shows:
  - compounds.faq: 0 missing
  - materials.relationships.contaminatedBy: 0 missing
  - materials.properties.materialCharacteristics: 0 missing
  - materials.properties.laserMaterialInteraction: 0 missing
- No regressions in contaminants/settings/applications.
- Root `_section` status is either removed by policy or explicitly documented/allowlisted.
