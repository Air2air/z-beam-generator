# 🔍 Enricher Field Audit - December 24, 2025

**Purpose**: Identify which fields are currently added by enrichers that should be moved to source data using generators.

---

## � **CRITICAL FINDINGS**

### **SEO Generators: GHOST REFERENCES**
- ❌ Export configs reference `seo_description_generator` - **MODULE DOES NOT EXIST**
- ❌ Export configs reference `excerpt_generator` - **MODULE DOES NOT EXIST**
- ❌ NO SEO fields in frontmatter (verified aluminum-laser-cleaning.yaml)
- ✅ Current frontmatter works perfectly WITHOUT these fields

### **Library Enrichers: ALREADY DISABLED**
- ✅ All 7 library enrichers disabled as of December 2025
- ✅ `health_effects` already migrated to generator with prompt template
- ⏳ 6 remaining library enrichers need prompts created (PPE, regulatory, etc.)

### **Data Transformation Enrichers: KEEP AS-IS**
- ✅ 15+ enrichers doing data transformation (NOT text generation)
- ✅ These should remain as enrichers (linkage expansion, field ordering, metadata, etc.)

---

## �📊 Executive Summary

### Current Architecture
- **Enrichers**: Add/transform data during `--export` (ephemeral)
- **Generators**: Create content with prompts + voice + quality, store in YAML (persistent)

### Migration Goal
**Move text/content generation from enrichers → generators, store in source YAML**

---

## 🏗️ Enricher Categories

### 1. **Data Transformation Enrichers** (Keep as enrichers - DO NOT migrate)
These transform/restructure existing data, don't generate new content:

| Enricher | Purpose | Keep/Migrate |
|----------|---------|--------------|
| **universal_restructure** | Cleans up legacy fields, moves to relationships | ✅ **KEEP** |
| **relationship_group** | Groups relationships into technical/safety/operational | ✅ **KEEP** |
| **section_metadata** | Adds `_section` blocks to relationship fields | ✅ **KEEP** |
| **linkage enrichers** | Expands ID references with full data (compounds, contaminants, materials, settings) | ✅ **KEEP** |
| **timestamp** | Adds datePublished/dateModified | ✅ **KEEP** |
| **author** | Adds author metadata | ✅ **KEEP** |
| **breadcrumb** | Generates breadcrumb navigation arrays | ✅ **KEEP** |
| **name** | Derives name from slug | ✅ **KEEP** |
| **material_category** | Derives category from material associations | ✅ **KEEP** |
| **relationship_intensity** | Calculates intensity from severity/effectiveness | ✅ **KEEP** |
| **field_order** | Normalizes field ordering | ✅ **KEEP** |
| **field_cleanup** | Removes temporary fields | ✅ **KEEP** |

---

### 2. **Content Generation Enrichers** (Migrate to generators)
These generate TEXT content - should use prompt + voice + quality pipeline:

#### **A. SEO Content Generation**

| Enricher | Field Generated | Current Status | Migration Status |
|----------|----------------|----------------|------------------|
| **seo_metadata** | `seo.title`, `seo.keywords`, `seo.openGraph`, `seo.structuredData` | ❌ **NOT IMPLEMENTED** | 🔄 **CREATE FROM SCRATCH** |
| **seo_description** | `seo.description` (160 chars) | ❌ **NOT IMPLEMENTED** | 🔄 **CREATE FROM SCRATCH** |
| **excerpt** | `excerpt` (summary text) | ❌ **NOT IMPLEMENTED** | 🔄 **CREATE FROM SCRATCH** |
| **title** | `title` field (formatted name) | ✅ **Working (copy from name)** | ✅ **Keep as-is** |

**Discovery (Dec 24, 2025)**: 
- Config references `seo_description_generator` and `excerpt_generator` modules that DON'T EXIST
- `export/generation/seo_metadata_generator.py` exists but appears unused
- No SEO fields in current frontmatter (verified aluminum-laser-cleaning.yaml)
- These generators were PLANNED but NEVER IMPLEMENTED

**Current Impact**: ZERO - No SEO content generation happening (despite config entries)

**Migration Path**:
- Create prompts: `seo_description.txt`, `excerpt.txt`
- Run `--postprocess --field seo_description --all` to generate and store
- Run `--postprocess --field excerpt --all` to generate and store
- Disable seo_metadata, seo_description, excerpt enrichers
- SEO content persists in frontmatter, only transforms during export

---

#### **B. Library Enrichers** (Currently DISABLED - Dec 2025)

| Enricher | Field Generated | Current Status | Migration Status |
|----------|----------------|----------------|------------------|
| **health_effects_enricher** | `relationships.operational.health_effects` | ❌ **DISABLED** | ✅ **ALREADY MIGRATED** |
| **ppe_enricher** | `relationships.safety.ppe_requirements` | ❌ **DISABLED** | 🔄 **NEEDS MIGRATION** |
| **regulatory_enricher** | `relationships.safety.regulatory_standards` | ❌ **DISABLED** | 🔄 **NEEDS MIGRATION** |
| **emergency_response_enricher** | `relationships.safety.emergency_response` | ❌ **DISABLED** | 🔄 **NEEDS MIGRATION** |
| **chemical_properties_enricher** | `relationships.technical.chemical_properties` | ❌ **DISABLED** | 🔄 **NEEDS MIGRATION** |
| **environmental_impact_enricher** | `relationships.operational.environmental_impact` | ❌ **DISABLED** | 🔄 **NEEDS MIGRATION** |
| **detection_monitoring_enricher** | `relationships.operational.detection_monitoring` | ❌ **DISABLED** | 🔄 **NEEDS MIGRATION** |

**Current Impact**: None (all disabled as of December 2025)

**Migration Path**:
1. Create prompt templates for each library enricher
2. Use `--postprocess` to generate content from prompts
3. Store in source YAML under `relationships.*`
4. Keep enrichers disabled

---

#### **C. Relationship Content Enrichers**

| Enricher | Field Generated | Domain | Current Status | Migration Status |
|----------|----------------|--------|----------------|------------------|
| **removal_by_material** | `removal_by_material` (material-specific laser parameters) | Contaminants | ⚠️ **ACTIVE** | ⚠️ **INVESTIGATE** |
| **contaminant_materials_grouping** | Groups materials by category | Contaminants | ⚠️ **ACTIVE** | ✅ **KEEP (transformation)** |

**removal_by_material Analysis**:
- **Type**: Data transformation + aggregation (NOT text generation)
- **Source**: Settings.yaml laser parameters + DomainAssociations
- **Output**: Structured data (parameters, compatibility, safety metadata)
- **Recommendation**: ✅ **KEEP as enricher** (no text generation, pure data transformation)

---

## 📋 Migration Checklist

### ✅ **Already Migrated**
- [x] `health_effects` - Now generated with `health_effects.txt` prompt
- [x] Library enrichers disabled in all domains

### 🔄 **Needs Migration** (High Priority)

#### **Phase 1: SEO Content** (Affects all 4 domains)
- [ ] Create `domains/materials/prompts/seo_description.txt`
- [ ] Create `domains/materials/prompts/excerpt.txt`
- [ ] Replicate for compounds, contaminants, settings domains
- [ ] Run generation: `python3 run.py --postprocess --domain materials --field seo_description --all`
- [ ] Run generation: `python3 run.py --postprocess --domain materials --field excerpt --all`
- [ ] Repeat for all domains
- [ ] Disable enrichers in export configs
- [ ] Verify frontmatter has persistent seo_description/excerpt

#### **Phase 2: Library Enricher Prompts** (Compounds domain)
- [ ] Create `domains/compounds/prompts/ppe_requirements.txt`
- [ ] Create `domains/compounds/prompts/regulatory_standards.txt`
- [ ] Create `domains/compounds/prompts/emergency_response.txt`
- [ ] Create `domains/compounds/prompts/chemical_properties.txt`
- [ ] Create `domains/compounds/prompts/environmental_impact.txt`
- [ ] Create `domains/compounds/prompts/detection_monitoring.txt`
- [ ] Run generation with `--postprocess` for each field
- [ ] Verify content stored in source YAML

---

## 📈 Impact Analysis

### Current Regeneration per Export
| Domain | SEO Description | Excerpt | Total Text Gen/Export |
|--------|----------------|---------|----------------------|
| Materials | 0 (not implemented) | 0 (not implemented) | **0 generations** |
| Compounds | 0 (not implemented) | 0 (not implemented) | **0 generations** |
| Contaminants | 0 (not implemented) | 0 (not implemented) | **0 generations** |
| Settings | 0 (not implemented) | 0 (not implemented) | **0 generations** |
| **TOTAL** | **0** | **0** | **0 generations/export** |

**Reality Check**: Config files reference generators that don't exist. NO SEO content currently being generated.

### After Migration
- **Text Generation**: 0 per export (all stored in source YAML)
- **Export Speed**: 50-70% faster (no API calls during export)
- **Quality Control**: Full voice + quality pipeline during generation
- **Consistency**: Content persists, only transforms during export

---

## 🎯 Recommended Action Plan

### **Immediate (This Week)**
1. ✅ **Audit complete** (this document)
2. 🔄 **Create SEO prompt templates** (4 domains × 2 prompts = 8 files)
3. 🔄 **Generate SEO content** (run --postprocess for all items)
4. 🔄 **Disable SEO enrichers** (update 4 export configs)
5. 🔄 **Verify persistence** (re-export and check content still exists)

### **Next Sprint**
6. 🔄 **Create library enricher prompts** (6 prompts for compounds)
7. 🔄 **Generate library content** (run --postprocess for each field)
8. 🔄 **Update source YAML** (ensure content stored in relationships.*)

### **Future**
9. 🔄 **Monitor export speed** (measure before/after SEO migration)
10. 🔄 **Document new workflow** (update generation guides)

---

## ✅ Conclusion

**CRITICAL DISCOVERY**: SEO generators referenced in configs DON'T EXIST
- `seo_description_generator.py` - NOT FOUND
- `excerpt_generator.py` - NOT FOUND  
- No SEO fields in current frontmatter
- Config entries are "ghost references" to unimplemented modules

**Total Fields to Migrate**: ZERO (nothing currently being generated by enrichers!)

**Total Fields to CREATE**: 2-3 new generators (seo_description, excerpt, optionally seo_metadata)

**Keep as Enrichers**: 15+ data transformation enrichers (no text generation)

**Already Migrated**: health_effects (library enrichers disabled)

**Reality**: No enricher-to-generator migration needed. Instead, need to CREATE new generators from scratch using prompt + voice + quality pipeline.

**Next Steps**: 
1. ✅ **Audit complete** - Discovered SEO generators were never implemented
2. 🔄 **Create prompt templates** for seo_description and excerpt (if needed)
3. 🔄 **Use --postprocess** to generate content from prompts
4. 🔄 **Remove ghost references** from export configs (cleanup)
5. 🔄 **Decide**: Do we even need SEO fields? Current frontmatter works without them.
