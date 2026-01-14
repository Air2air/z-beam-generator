# Maximum Formatting at Source - Implementation Plan
**Date**: January 6, 2026  
**Status**: IN PROGRESS  
**Compliance**: Core Principle 0.6 - Generate to Data, Not Enrichers

## 🎯 Objective
Move ALL formatting and structure creation from export layer to generation/source data layer.

## 📋 Current Violations

### TIER 1: Data Creation (Grade F - Must Fix Immediately)
These tasks CREATE data during export - violates Core Principle 0.6:

1. **export_metadata** - Creates fields during export
   - ❌ `contentType`: Should be in source YAML
   - ❌ `schemaVersion`: Should be in source YAML
   - ❌ `fullPath`: Should be in source YAML
   - ❌ `breadcrumb`: Should be in source YAML
   - ❌ `metaDescription`: Should be in source YAML
   - ❌ `datePublished`: Should be in source YAML
   - ❌ `dateModified`: Should be in source YAML

2. **section_metadata** - Creates _section blocks during export
   - ❌ `_section.sectionTitle`: Should be in source relationships
   - ❌ `_section.sectionDescription`: Should be in source relationships
   - ❌ `_section.icon`: Should be in source relationships
   - ❌ `_section.order`: Should be in source relationships

### TIER 2: Format Normalization (Acceptable with Grandfather Clause)
These tasks transform format only - allowed per Jan 5, 2026 policy:

✅ **camelcase_normalization** - Converts snake_case → camelCase
   - Acceptable for legacy data created before Jan 5, 2026
   - NEW content (after Jan 5) should use camelCase in source

✅ **field_ordering** - Organizes output structure (presentation only)

✅ **field_cleanup** - Removes deprecated fields (cleanup only)

## 🔧 Required Changes

### Phase 1: Update Domain Adapters (Generation Layer)
**File**: `generation/core/adapters/domain_adapter.py`

Add fields during data write (when saving to Materials.yaml, etc.):

```python
def enrich_on_save(self, data: Dict[str, Any], domain: str) -> Dict[str, Any]:
    """Add all software metadata fields during save to source YAML."""
    
    # 1. contentType (from domain)
    content_type_map = {
        'materials': 'material',
        'contaminants': 'contaminant',
        'compounds': 'compound',
        'settings': 'setting',
    }
    data['contentType'] = content_type_map.get(domain, domain.rstrip('s'))
    
    # 2. schemaVersion (from config)
    data['schemaVersion'] = '5.0.0'
    
    # 3. fullPath (from category/subcategory/id)
    path_parts = [domain]
    if data.get('category'):
        path_parts.append(data['category'])
    if data.get('subcategory'):
        path_parts.append(data['subcategory'])
    path_parts.append(data['id'])
    data['fullPath'] = '/' + '/'.join(path_parts)
    
    # 4. breadcrumb (from category hierarchy)
    data['breadcrumb'] = self._generate_breadcrumbs(data, domain)
    
    # 5. Timestamps
    if 'datePublished' not in data:
        data['datePublished'] = datetime.utcnow().isoformat() + '+00:00'
    data['dateModified'] = datetime.utcnow().isoformat() + '+00:00'
    
    # 6. metaDescription (from micro or description)
    if 'metaDescription' not in data:
        data['metaDescription'] = self._generate_meta_description(data)
    
    return data
```

### Phase 2: Update Relationship Structure (Source Data)
**Files**: `data/materials/Materials.yaml`, `data/contaminants/Contaminants.yaml`, etc.

Add `_section` metadata to ALL relationship blocks in source:

```yaml
aluminum-laser-cleaning:
  # ... existing fields ...
  relationships:
    interactions:
      contaminated_by:
        _section:
          sectionTitle: "Common Contaminants"
          sectionDescription: "Typical contamination found on aluminum"
          icon: droplet
          order: 10
          variant: default
        items:
          - id: oil-residue
            # ... rest of item ...
```

### Phase 3: Use camelCase in Source Data (NEW Content Only)
**Files**: All domain YAML files

For NEW content created after Jan 5, 2026:
- ✅ Use `contentType` not `content_type`
- ✅ Use `displayName` not `display_name`
- ✅ Use `datePublished` not `date_published`
- ✅ Use `metaDescription` not `meta_description`

Legacy content keeps snake_case → exporter normalizes (grandfather clause).

### Phase 4: Remove Export Data Creation
**File**: `export/generation/universal_content_generator.py`

Remove these tasks from export configs:
- ❌ Remove `_task_export_metadata` (data now in source)
- ❌ Remove `_task_section_metadata` (data now in source)
- ✅ Keep `_task_camelcase_normalization` (for legacy data only)
- ✅ Keep `_task_field_ordering` (presentation only)

## 📊 Impact Analysis

### Files Requiring Changes

**Generation Layer** (Create data with formatting):
- `generation/core/adapters/domain_adapter.py` - Add enrich_on_save()
- `generation/core/evaluated_generator.py` - Call enrich_on_save()
- `domains/*/coordinator.py` - Ensure saves use enriched data

**Source Data** (Add missing fields):
- `data/materials/Materials.yaml` - 153 items need contentType, fullPath, breadcrumb, etc.
- `data/contaminants/Contaminants.yaml` - 98 items
- `data/compounds/Compounds.yaml` - 34 items
- `data/settings/Settings.yaml` - 153 items
- **Total**: 438 items need backfill

**Export Layer** (Remove data creation):
- `export/generation/universal_content_generator.py` - Remove 2 tasks
- `export/config/*.yaml` - Remove export_metadata, section_metadata tasks

### Migration Strategy

**Option A: Bulk Backfill** (Recommended)
1. Create script: `scripts/enrichment/backfill_software_metadata.py`
2. Run once to add fields to ALL 438 source items
3. Remove export_metadata task
4. Export with data already present

**Option B: Lazy Migration**
1. Keep export_metadata task active
2. Add enrichment to generation layer
3. As items are regenerated, source data gets complete
4. When 100% migrated, remove export_metadata task

**Recommendation**: Option A for clean architecture immediately.

## ✅ Success Criteria

1. **Source Data Complete**: ALL 438 items have contentType, schemaVersion, fullPath, breadcrumb, timestamps
2. **Export Transforms Only**: Export tasks only reorder/rename, never create fields
3. **Generation Enriches**: Domain adapters add complete formatting during save
4. **Frontmatter Unchanged**: Export produces identical output (data just comes from different layer)

## 📝 Implementation Order

### Priority 1 (Immediate - 2 hours)
1. Create backfill script for software metadata
2. Run backfill on all 438 items
3. Verify source data completeness
4. Remove export_metadata task from configs

### Priority 2 (Same Day - 1 hour)
1. Update domain_adapter.py with enrich_on_save()
2. Call enrich_on_save() in evaluated_generator.py
3. Test: Generate new item, verify source has all fields

### Priority 3 (Next Week - 3 hours)
1. Add _section metadata to relationships in source (438 items × ~3 sections each)
2. Remove section_metadata task from export
3. Verify relationship blocks have complete structure

## 📚 Related Documentation
- `docs/TECHNICAL_DEBT_BUILD_TIME_NORMALIZATION.md` - Grandfather clause for legacy data
- `SOURCE_DATA_NORMALIZATION_PLAN_JAN5_2026.md` - Original normalization plan
- Core Principle 0.6 - Generate to Data, Not Enrichers (copilot-instructions.md)

## 🚨 Grade
**Current**: F (export creates data)  
**Target**: A (source contains all data, export transforms only)
