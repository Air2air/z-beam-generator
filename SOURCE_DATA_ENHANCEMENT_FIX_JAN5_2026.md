# Architectural Violation Fix: Source Data vs Build-Time Enhancement
**Date:** January 5, 2026  
**Issue:** Core Principle 0.6 Violation - Data enhancement happening at export/build time  
**Status:** Partially Fixed

---

## 🎯 Core Principle 0.6: No Build-Time Data Enhancement

**THE RULE:**
> ALL data enhancement (structure, metadata, relationships) MUST happen during generation, NOT at build/export time.

**THE VIOLATION:**
Export enrichers were creating/adding data during build time instead of just formatting existing data from source.

---

## ✅ What We Fixed Today

### 1. Added _section Metadata to Contaminants Source Data
**File:** `data/contaminants/Contaminants.yaml`  
**Change:** Added 490 `_section` blocks (98 contaminants × 5 sections each)  
**Status:** ✅ COMPLETE

**Sections now in source data:**
- `safety.regulatory_standards`
- `interactions.produces_compounds`
- `interactions.affects_materials`
- `visual.appearance_on_categories`
- `operational.laser_properties`

### 2. Removed Export-Time section_metadata Tasks
**Files Modified:**
- ✅ `export/config/materials.yaml` - Removed section_metadata task
- ✅ `export/config/contaminants.yaml` - Removed 2x section_metadata tasks
- ✅ `export/config/compounds.yaml` - Removed 2x section_metadata tasks
- ✅ `export/config/settings.yaml` - Removed section_metadata task

**Result:** Export now PRESERVES `_section` metadata from source, doesn't ADD it.

---

## ⚠️ What Still Needs Fixing

### Critical Issue: Enrichers Creating Sections at Export Time

**VIOLATION DISCOVERED:**
Enrichers are creating **7 additional safety sections** during export that don't exist in source data:

❌ Sections created by enrichers at build time:
1. `safety.fire_explosion_risk`
2. `safety.fumes_generated`
3. `safety.particulate_generation`
4. `safety.ppe_requirements`
5. `safety.substrate_compatibility_warnings`
6. `safety.toxic_gas_risk`
7. `safety.ventilation_requirements`
8. `safety.visibility_hazard`

**Evidence:**
- Source data has **5 sections**
- Frontmatter has **12 sections**
- **7 sections added by enrichers** during export (violation)

**Root Cause:**
These enrichers are still active and creating sections:
- `SafetyTableNormalizer`
- `RemovalByMaterialEnricher`
- Other safety-related enrichers

---

## 📋 Required Next Steps

### Step 1: Identify All Section-Creating Enrichers
Search for enrichers that add sections to `relationships`:
```bash
grep -r "relationships\[" export/enrichers/
grep -r "\.setdefault\(" export/enrichers/
```

### Step 2: Move Section Creation to Source Data Generation
For each section-creating enricher:
1. **Identify what data it creates** (fire_explosion_risk, fumes_generated, etc.)
2. **Create generation script** to populate this data in source YAML
3. **Run script** to populate all contaminants
4. **Verify** data exists in source before proceeding

### Step 3: Convert Enrichers to Format-Only
After source data is complete:
1. **Modify enrichers** to only format/transform existing data
2. **Remove creation logic** - enrichers should NOT add sections
3. **Add validation** - throw error if expected section missing from source

### Step 4: Verification
1. **Source data check:** All 12 sections exist in `Contaminants.yaml`
2. **Export test:** Frontmatter has 12 sections, all with `_section` metadata
3. **No creation:** Export logs show zero sections created/added
4. **Compliance:** 100% of sections have metadata from source, 0% added at build time

---

## 🎯 Success Criteria

### Current State:
- ✅ Materials: 100% compliance (all sections in source data)
- ✅ Compounds: 100% compliance (all sections in source data)
- ✅ Settings: 100% compliance (all sections in source data)
- ⚠️ Contaminants: **41.7% compliance** (5/12 sections in source data, 7 added by enrichers)

### Target State:
- ✅ All domains: 100% compliance
- ✅ Zero sections created at export time
- ✅ All `_section` metadata in source data
- ✅ Enrichers only format/transform, never create

---

## 📊 Impact Assessment

### What Works Now:
- ✅ Export preserves existing `_section` metadata from source
- ✅ No section_metadata task adding metadata at build time
- ✅ Materials, Compounds, Settings have complete source data

### What's Broken:
- ❌ Contaminants missing 7 sections in source data
- ❌ Enrichers violating Core Principle 0.6 by creating sections
- ❌ Cannot achieve 100% compliance until enrichers fixed

### Risk:
- **HIGH** - Architectural violation impacts data integrity
- **MEDIUM** - Frontend may depend on enricher-created sections
- **LOW** - Easy to fix with proper source data generation

---

## 🔧 Implementation Plan

### Phase 1: Data Generation (Priority 1)
1. Create `scripts/enrichment/enrich_contaminant_safety_sections.py`
2. Generate 7 missing safety sections for all 98 contaminants
3. Add complete `_section` metadata for each
4. Verify all contaminants have 12 sections in source data

### Phase 2: Enricher Refactoring (Priority 2)
1. Audit all enrichers for section creation
2. Convert to format-only operations
3. Add validation for missing source data
4. Document enricher responsibilities

### Phase 3: Verification (Priority 3)
1. Re-export all domains
2. Verify 100% section compliance
3. Run compliance report
4. Update documentation

---

## 📚 Related Documentation

- `docs/08-development/NO_BUILD_TIME_ENHANCEMENT_POLICY.md` (Core Principle 0.6)
- `docs/BACKEND_RELATIONSHIP_REQUIREMENTS_JAN5_2026.md` (Section requirements)
- `.github/copilot-instructions.md` (Line 0.6: Generate to Data, Not Enrichers)

---

## ✅ Completion Checklist

- [x] Add `_section` metadata to contaminants source data (5 sections)
- [x] Remove section_metadata tasks from export configs
- [x] Verify export preserves metadata from source
- [ ] Identify all section-creating enrichers
- [ ] Generate missing 7 safety sections in source data
- [ ] Refactor enrichers to format-only
- [ ] Achieve 100% section compliance
- [ ] Document enricher guidelines

---

**Next Action:** Create enrichment script to populate missing 7 safety sections in contaminants source data.
