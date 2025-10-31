# Directory Organization Analysis

**Date**: October 30, 2025
**Purpose**: Determine if /research, /utils, /tests, /data, /components should move to content-type folders or /shared

## Analysis Summary

### 📊 /data - **SPLIT BY CONTENT TYPE**
**Current**: `materials.yaml`, `regions.yaml`, `applications.yaml`, `contaminants.yaml`, `thesaurus.yaml`
**Recommendation**: ✅ **Already moved** to content-type folders as `data.yaml`
**Status**: COMPLETE

**Action Taken**:
- `data/materials.yaml` → `materials/data.yaml` ✅
- `data/regions.yaml` → `regions/data.yaml` ✅
- `data/applications.yaml` → `applications/data.yaml` ✅
- `data/contaminants.yaml` → `contaminants/data.yaml` ✅
- `data/thesaurus.yaml` → `thesaurus/data.yaml` ✅

**Keep in /data**:
- `data/authors/` - Shared author profiles
- `data/categories/` - Category definitions (cross-cutting)
- `data/materials.py` - Material data utilities

---

### 🔬 /research - **MATERIAL-SPECIFIC → Move to /materials**
**Current Contents**:
- `base.py` - ContentResearcher abstract base
- `material_property_researcher.py` - Material property research (701 lines)
- `material_property_research_system.py` - Material research system
- `category_range_researcher.py` - Category range research
- `topic_researcher.py` - Topic research
- `factory.py` - Research factory
- `services/ai_research_service.py` - AI research enrichment

**Analysis**:
- ❌ NOT used by other content types (regions, applications, contaminants, thesaurus)
- ✅ Specifically designed for **material properties**
- ✅ Names explicitly include "material"
- ✅ Research properties like density, melting point, thermal conductivity
- ❌ Other content types don't have "properties" to research

**Recommendation**: ✅ **Move to /materials/research/**

**Why**:
- Material-specific property discovery
- Not applicable to regions, applications, contaminants, or thesaurus
- Tightly coupled to materials.yaml structure
- Part of material generation workflow only

**Note**: There's also `components/frontmatter/research/` which is ALSO material-specific (PropertyValueResearcher, MachineSettingsResearcher). Consider consolidating.

---

### 🛠️ /utils - **KEEP & REORGANIZE**
**Current Contents**:
- `property_classifier.py` - Property classification (material-specific) → **Move to /materials**
- `property_enhancer.py` - Property enhancement (material-specific) → **Move to /materials**
- `property_helpers.py` - Property helpers (material-specific) → **Move to /materials**
- `unit_extractor.py` - Unit extraction (material-specific) → **Move to /materials**
- `category_property_cache.py` - Category cache (material-specific) → **Move to /materials**
- `author_manager.py` - Already moved to `components/frontmatter/utils/` ✅
- `file_operations.py` - General file ops → **Move to /shared/utils/**
- `yaml_parser.py` - General YAML parsing → **Move to /shared/utils/**
- `config_loader.py` - General config → **Move to /shared/utils/**
- `import_system.py` - General imports → **Move to /shared/utils/**
- `requirements_loader.py` - General requirements → **Move to /shared/utils/**
- `file_ops/` - General file operations → **Move to /shared/utils/**
- `loaders/` - General data loaders → **Move to /shared/utils/**
- `ai/` - AI-related utilities → **Move to /shared/utils/**
- `validation/` - Validation utilities → **Already in /shared/validation/** (duplicate?)
- `core/` - Core utilities → Check if needed

**Recommendation**: 
- ✅ Material-specific utils → `/materials/utils/`
- ✅ General utils → `/shared/utils/`

---

### 🧪 /tests - **KEEP AT ROOT**
**Current Contents**: Unit tests, integration tests, e2e tests for ALL components

**Recommendation**: ✅ **Keep at root level**

**Why**:
- Tests span multiple content types
- Tests shared infrastructure
- Tests integration between components
- Standard Python convention (tests at root)
- Cross-cutting test concerns (fixtures, helpers, etc.)

**Do NOT split tests by content type** - maintaining test suite cohesion is more important.

---

### 🏗️ /components - **KEEP & ANALYZE SUBFOLDERS**
**Current Structure**:
```
components/
  ├── frontmatter/      # Material-focused frontmatter generation
  ├── caption/          # Caption generation (cross-content?)
  ├── subtitle/         # Subtitle generation (cross-content?)
  └── faq/              # FAQ generation (cross-content?)
```

**components/frontmatter/** Analysis:
- `core/` - BaseFrontmatterGenerator, orchestrator → **Keep** (used by all types)
- `research/` - PropertyValueResearcher, MachineSettingsResearcher → **Material-specific, move to /materials/research/**
- `services/` - PropertyManager, TemplateService → **Check if material-specific**
- `modules/` - PropertiesModule, SettingsModule, etc. → **Material-specific, move to /materials/modules/**
- `utils/` - Author manager → **Already moved** ✅
- `validation/` - CompletenessValidator → **Material-specific?**
- `types/` - Old generator locations → **Already moved** ✅

**Other components/** (caption, subtitle, faq):
- Unclear if they're used by all content types or just materials
- Need to check if regions/applications/contaminants/thesaurus generate captions
- If material-only → move to /materials/components/
- If cross-content → keep in /components/ or move to /shared/

**Recommendation**: 
- ✅ Keep `/components/frontmatter/core/` (shared base classes)
- ❓ Analyze `/components/{caption,subtitle,faq}` usage
- ✅ Move material-specific modules to `/materials/`

---

## Proposed Final Structure

```
/materials/
  ├── generator.py
  ├── data.yaml
  ├── schema.py
  ├── base.py
  ├── research/              ← Move from /research
  │   ├── property_researcher.py
  │   ├── machine_settings_researcher.py
  │   ├── property_value_researcher.py  ← From components/frontmatter/research
  │   └── unified_research_interface.py
  ├── utils/                 ← Move material-specific from /utils
  │   ├── property_classifier.py
  │   ├── property_enhancer.py
  │   ├── property_helpers.py
  │   ├── unit_extractor.py
  │   └── category_property_cache.py
  ├── modules/               ← Move from components/frontmatter/modules (if material-specific)
  │   ├── properties_module.py
  │   ├── settings_module.py
  │   └── ...
  ├── services/              ← Move from components/frontmatter/services (if material-specific)
  │   ├── property_manager.py
  │   └── template_service.py
  ├── docs/
  └── README.md

/regions/, /applications/, /contaminants/, /thesaurus/
  ├── generator.py
  ├── data.yaml
  ├── schema.json
  └── README.md
  # These types don't have research/utils (simpler data-driven only)

/shared/
  ├── voice/
  ├── validation/
  ├── api/
  ├── services/
  └── utils/                 ← Move general utils from /utils
      ├── file_operations.py
      ├── yaml_parser.py
      ├── config_loader.py
      ├── import_system.py
      ├── requirements_loader.py
      ├── file_ops/
      ├── loaders/
      └── ai/

/components/
  └── frontmatter/
      ├── core/              ← Keep (BaseFrontmatterGenerator, orchestrator)
      ├── caption/           ← Analyze usage
      ├── subtitle/          ← Analyze usage
      └── faq/               ← Analyze usage

/tests/                      ← Keep at root
  ├── unit/
  ├── integration/
  └── e2e/

/data/                       ← Keep shared data
  ├── authors/
  ├── categories/
  └── materials.py

/config/                     ← Keep at root
/frontmatter/                ← Keep centralized output
```

## Decision Summary

| Directory | Action | Reasoning |
|-----------|--------|-----------|
| `/data/*.yaml` | ✅ Already moved to content-type folders | Content-specific data |
| `/data/authors/`, `/data/categories/` | ✅ Keep in /data | Shared across types |
| `/research/` | ✅ Move to `/materials/research/` | Material-specific property research |
| `/utils/` (material-specific) | ✅ Move to `/materials/utils/` | Property classification, enhancement |
| `/utils/` (general) | ✅ Move to `/shared/utils/` | File ops, YAML parsing, config |
| `/tests/` | ✅ Keep at root | Cross-cutting test concerns |
| `/components/frontmatter/core/` | ✅ Keep | Shared base classes |
| `/components/frontmatter/research/` | ✅ Move to `/materials/research/` | Material property research |
| `/components/frontmatter/modules/` | ❓ Analyze → likely `/materials/modules/` | Check if material-specific |
| `/components/{caption,subtitle,faq}/` | ❓ Analyze usage | Determine if material-only or cross-content |

## Benefits

### ✅ Clear Separation
- **Materials**: Complex with research, property classification, machine settings
- **Other Types**: Simpler, data-driven only
- Each content type self-contained with appropriate complexity

### ✅ Reduced Confusion
- No material-specific code in shared areas
- Clear what applies to which content types
- Easier to understand scope and dependencies

### ✅ Maintainability
- Material research tools grouped together
- General utilities truly general
- Shared infrastructure clearly shared

## Next Steps

1. ✅ Analyze `/components/{caption,subtitle,faq}` usage
2. ✅ Move `/research/` → `/materials/research/`
3. ✅ Move material-specific `/utils/` → `/materials/utils/`
4. ✅ Move general `/utils/` → `/shared/utils/`
5. ✅ Move `/components/frontmatter/research/` → `/materials/research/`
6. ✅ Move material-specific modules/services to `/materials/`
7. ✅ Update all imports
8. ✅ Test system functionality
