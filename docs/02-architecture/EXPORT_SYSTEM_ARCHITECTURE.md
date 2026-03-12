# Export System Architecture

**Date**: March 12, 2026  
**Status**: Production Architecture  
**Current Version**: FrontmatterExporter

---

## 🎯 System Overview

The export system transforms canonical source data in `data/*/*.yaml` into frontmatter YAML files for the z-beam website. In current Grok-first workflows, that source data is authored and quality-checked upstream before export. The architecture is built on:

1. **Universal Exporter Pattern** - Single exporter handles all domains
2. **Configuration-Driven** - Domain behavior defined in YAML configs
3. **Generator Task Pipeline** - Deterministic normalization, hydration, cleanup, and ordering
4. **Zero Fallbacks** - Fail-fast on missing data (100% completeness required)
5. **Trivial Export** - No API calls, validation, or generation at export time

Export boundary:

- Source YAML owns content quality, author assignment, page copy, relationship copy, and section metadata.
- Export config owns formatting, field compatibility, author hydration, cleanup, ordering, and output writing.
- Frontmatter is a derived artifact. Fix source or export logic, never the generated website file directly.

---

## 🏗️ Architecture Components

### 1. Universal Exporter (Current Production System)

**Location**: `export/core/frontmatter_exporter.py`  
**Class**: `FrontmatterExporter`  
**Purpose**: Configuration-driven export for all domains

**Key Principles**:
- ✅ Single exporter class handles materials, contaminants, compounds, settings
- ✅ Domain behavior configured via `export/config/*.yaml`
- ✅ Enricher pipeline applies transformations
- ✅ No domain-specific code in exporter

**Usage**:
```python
from export.core.frontmatter_exporter import FrontmatterExporter

# Export materials
exporter = FrontmatterExporter(domain='materials')
exporter.export_item('aluminum')

# Export all materials
exporter.export_all()

# Export contaminants
contam_exporter = FrontmatterExporter(domain='contaminants')
contam_exporter.export_all()
```

---

### 2. Domain Configurations

**Location**: `export/config/*.yaml`  
**Purpose**: Define domain-specific export behavior

**Available Configs**:
- `materials.yaml` - Material export configuration
- `contaminants.yaml` - Contaminant export configuration
- `compounds.yaml` - Compound export configuration
- `settings.yaml` - Machine settings export configuration

**Configuration Structure**:
```yaml
domain: materials
source_file: data/materials/Materials.yaml
output_directory: ../z-beam/frontmatter/materials/
schema_file: domains/materials/schema.yaml

enrichers:
  - name: timestamp
    priority: 1
  - name: author
    priority: 2
  - name: breadcrumb
    priority: 3
  # ... more enrichers

field_mapping:
  name: name
  slug: slug
  category: category.slug
  # ... field transformations
```

---

### 3. Generator Task Pipeline System

**Location**: `export/generation/universal_content_generator.py` and `export/config/*.yaml`  
**Purpose**: Deterministic export-time transforms during export

**Primary Task Types**:

**Universal Tasks** (configuration-driven):
- `export_metadata` - Add legitimate export-time metadata such as `dateModified`
- `author_linkage` - Hydrate source author identifiers into website author objects
- `text_field_normalization` - Normalize wrapper artifacts without regenerating copy
- `camelcase_normalization` - Convert source compatibility fields to frontend casing
- `field_cleanup` - Remove deprecated export-only leftovers
- `field_ordering` - Enforce stable website field order

**Domain-Specific Tasks**:
- relationship shaping and grouping where required by the frontend contract
- section metadata preservation or normalization where already present in source
- field-order generators that run last for stable output

**Generator Interface**:
```python
class ContentGenerator:
  def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
    """Apply configured export-time transforms without generating new content."""
    return transformed_frontmatter
```

---

### 4. Data Flow (Production Architecture)

```
SOURCE DATA (100% Complete)
├── data/materials/Materials.yaml
├── data/contaminants/contaminants.yaml
├── data/compounds/Compounds.yaml
└── data/settings/Settings.yaml
         │
         ▼
UNIVERSAL EXPORTER
├── Load domain config (export/config/*.yaml)
├── Load source data
├── Apply configured generator tasks
│   ├── Export metadata
│   ├── Author hydration
│   ├── Text normalization / cleanup
│   └── Field ordering
└── Write frontmatter YAML
         │
         ▼
FRONTMATTER OUTPUT (Website)
└── ../z-beam/frontmatter/{domain}/*.yaml
```

**Key Principle**: ALL generation/validation happens BEFORE export
- ✅ Grok-first research and writing → Source YAML files
- ✅ AI text generation → Source YAML files
- ✅ Property research → Source YAML files  
- ✅ Completeness validation → Source YAML files
- ✅ Quality scoring → Source YAML files
- ❌ NO generation during export
- ❌ NO validation during export (already validated)
- ❌ NO fallback values (fail-fast if data incomplete)

---

### 5. Zero Fallback Policy

**Critical**: Export system has ZERO fallback ranges/values anywhere.

**Violations** (NOT ALLOWED):
```python
❌ value = data.get('property', default_value)
❌ if not found: use_category_range()
❌ range = material_range or category_range
❌ return template_value if missing else actual_value
```

**Correct Behavior**:
```python
✅ value = data['property']  # Fail if missing
✅ if 'property' not in data: raise ValueError("Missing required property")
✅ Must have 100% data in source YAML before export
```

**Rationale**: 
- Source data MUST be 100% complete
- Export is trivial field mapping only
- Incomplete data = generation/research failure, not export failure
- Fail-fast surfaces data gaps immediately

---

### 6. Performance Characteristics

**Production Metrics** (December 2025):
- **Materials**: 153 files in ~8 seconds
- **Contaminants**: 98 files in ~5 seconds
- **Compounds**: 20 files in ~2 seconds
- **Settings**: 153 files in ~8 seconds
- **Total**: 424 files in ~23 seconds

**Performance Factors**:
- No API calls (all content pre-generated)
- No validation (already validated in source)
- Simple field mapping and transformation
- C-based YAML loading (10x faster than pure Python)
- Enricher pipeline efficient (modular, cacheable)

---

## 📋 Migration Guide

### Deprecated Exporters (Removed Dec 19, 2025)

**Old System**:
```python
❌ from export.compounds.trivial_exporter import CompoundExporter
❌ from export.materials.streamlined_generator import StreamlinedFrontmatterGenerator
❌ from export.core.schema_validator import SchemaValidator
```

**Current System**:
```python
✅ from export.core.frontmatter_exporter import FrontmatterExporter
✅ from shared.validation import SchemaValidator

exporter = FrontmatterExporter(domain='compounds')
exporter.export_all()
```

### Updating Tests

**Old Test Pattern**:
```python
from export.compounds.trivial_exporter import CompoundExporter

def test_compound_export():
    exporter = CompoundExporter()
    result = exporter.export_compound('benzene')
    assert result is not None
```

**New Test Pattern**:
```python
from export.core.frontmatter_exporter import FrontmatterExporter

def test_compound_export():
    exporter = FrontmatterExporter(domain='compounds')
    result = exporter.export_item('benzene')
    assert result is not None
```

---

## 🔧 Common Operations

### Export All Domains
```bash
# Via orchestrator
python3 export/core/orchestrator.py --all

# Individual domains
python3 -c "from export.core.frontmatter_exporter import FrontmatterExporter; \
FrontmatterExporter(domain='materials').export_all()"
```

### Export Single Item
```python
from export.core.frontmatter_exporter import FrontmatterExporter

# Export specific material
exporter = FrontmatterExporter(domain='materials')
exporter.export_item('aluminum')

# Export specific contaminant
contam_exporter = FrontmatterExporter(domain='contaminants')
contam_exporter.export_item('rust')
```

### Add New Domain

1. Create domain config: `export/config/new_domain.yaml`
2. Define source file, output directory, enrichers
3. Register any domain-specific enrichers (if needed)
4. Export: `FrontmatterExporter(domain='new_domain')`

**No code changes required** - fully configuration-driven

---

## 🚨 Common Issues & Solutions

### Issue 1: Export Fails with Missing Data

**Symptom**: `KeyError: 'property_name'`

**Cause**: Source YAML missing required field

**Solution**:
```bash
# Run data completeness check
python3 run.py --data-completeness-report

# Research missing properties
python3 run.py --data-gaps

# Fill gaps before export
```

**Grade**: This is CORRECT behavior (fail-fast)

---

### Issue 2: Orphan Frontmatter Files

**Symptom**: Frontmatter file exists but source item doesn't

**Cause**: Item removed from source YAML but frontmatter not cleaned

**Solution**:
```bash
# Remove orphan files
python3 scripts/data/remove_orphan_settings.py

# Re-export all to sync
python3 export/core/orchestrator.py --all
```

---

### Issue 3: Broken Relationships

**Symptom**: Relationship links point to non-existent items

**Cause**: DomainAssociations.yaml out of sync with source data

**Solution**:
```bash
# Audit associations
python3 scripts/analysis/audit_domain_associations.py

# Auto-populate relationships (archived — ran once, 2025)
# python3 scripts/archive/completed-populations/auto_populate_relationships.py

# Re-export to apply
python3 export/core/orchestrator.py --all
```

---

## 📊 Architecture Evolution

### Version History

**v9.1.0** (December 2025) - FrontmatterExporter
- Single exporter handles all domains
- Configuration-driven behavior
- 16-enricher pipeline system
- Zero fallback policy enforced

**v7.0.0** (November 2025) - Regulatory enrichment
- Automatic organization detection
- Metadata enrichment
- 12 organizations supported

**v6.0.0** (October 2025) - Trivial export architecture
- Removed generation from export
- All validation pre-export
- 10x performance improvement

**v5.0.0** (September 2025) - Breadcrumb navigation
- Hierarchical navigation system
- Category metadata integration
- Production-ready 123 materials

---

## 🔗 Related Documentation

**Implementation Details**:
- `export/README.md` - Comprehensive export documentation (657 lines)
- `export/core/frontmatter_exporter.py` - Primary exporter implementation
- `export/config/*.yaml` - Domain configurations
- `export/enrichers/` - Enricher implementations

**Architecture**:
- `docs/05-data/DATA_FLOW.md` - Complete data flow documentation
- `docs/05-data/DATA_STORAGE_POLICY.md` - Data storage policies
- `docs/02-architecture/processing-pipeline.md` - Generation pipeline

**Historical**:
- `docs/08-development/CHANGELOG.md` - Active export-system maintenance log
- `docs/decisions/` - Architecture decision records for major export changes
- `git log -- docs/02-architecture/EXPORT_SYSTEM_ARCHITECTURE.md export/` - Source-of-truth history for prior export changes

---

## ✅ Success Criteria

**Correct Export System**:
- ✅ Zero fallback values (fail-fast on incomplete data)
- ✅ Configuration-driven (no hardcoded domain logic)
- ✅ Modular enrichers (single responsibility)
- ✅ Performance optimized (<30 seconds for 424 files)
- ✅ No API calls during export
- ✅ No validation during export (already validated)
- ✅ Clean separation: generation → source YAML, export → frontmatter

**Policy Compliance**:
- ✅ Follows fail-fast architecture principles
- ✅ Zero tolerance for mocks/fallbacks in production
- ✅ Single source of truth (source YAML files)
- ✅ Immutable frontmatter (output only, not data storage)
