# Source Data Normalization Plan - January 5, 2026

## Problem Statement

Source YAML files (Materials.yaml, Contaminants.yaml, Compounds.yaml, Settings.yaml) have inconsistent field ordering and contain export metadata that should only exist in frontmatter output files.

**Current Issues:**
1. **Inconsistent field order** - Core fields (id, name, category, author) in different positions across domains
2. **Export metadata in source** - Software fields (schemaVersion, contentType, fullPath, breadcrumb, datePublished, dateModified) polluting source data
3. **No standardized structure** - Each domain evolved independently without architectural consistency

## Architecture Violations

**Core Principle 0.6 Violation:**
Export metadata in source YAML means source data is NOT complete/clean - it contains build-time generated fields.

**Correct Architecture:**
- **Source YAML** = Domain data ONLY (properties, relationships, content)
- **Export process** = Adds software metadata (schemaVersion, contentType, fullPath, breadcrumb, timestamps)
- **Frontmatter output** = Source data + export metadata

## Proposed Standard Field Order

### All Domains (Common Fields - First 9 positions):
```yaml
1. id                    # Unique identifier (kebab-case)
2. name                  # Display name
3. display_name          # Optional full display name (if different from name)
4. title                 # Page title (if different from name)
5. category              # Primary classification
6. subcategory           # Secondary classification (optional)
7. author                # Attribution object
8. micro                 # Microcopy object (before/after for contaminants)
9. images                # Image references object

# Domain-specific data fields follow...
# (characteristics, properties, machine_settings, etc.)

# Relationships and metadata near end...
# (relationships, metadata, card, components, etc.)

# FAQ and expert content at end...
# (faq, expert_answers, etc.)
```

### Fields to REMOVE from Source YAML:
```yaml
# Export metadata (generated during export, NOT source data)
- schemaVersion          # Added by export process
- contentType            # Added by export process
- pageTitle              # Generated from name/title
- metaDescription        # Generated from micro/description
- pageDescription        # Generated from description
- fullPath               # Generated from slug/domain
- breadcrumb             # Generated from category hierarchy
- datePublished          # Added by export process
- dateModified           # Added by export process
```

## Domain-Specific Field Order

### Materials Domain (Materials.yaml)
```yaml
# Standard core fields (1-9)
1. id
2. name
3. category
4. subcategory
5. author
6. micro
7. images
8. characteristics      # Material-specific: hardness, density, etc.
9. properties           # Physical/chemical properties
10. contamination       # Contamination susceptibility
11. components          # Laser cleaning components
12. relationships       # Related materials/contaminants/compounds
13. operational         # Operational considerations
14. regulatory_standards # Compliance requirements
15. metadata            # Domain metadata
16. card                # Card display config
17. eeat                # E-E-A-T signals
18. faq                 # FAQ list
```

### Contaminants Domain (Contaminants.yaml)
```yaml
# Standard core fields (1-9)
1. id
2. name
3. title
4. category
5. subcategory
6. author
7. micro                # Before/after microcopy
8. images
9. valid_materials      # List of compatible materials
10. context_notes       # Usage context
11. realism_notes       # Visual realism notes
12. relationships       # Related contaminants/materials
13. card                # Card display config
14. faq                 # FAQ list
```

### Compounds Domain (Compounds.yaml)
```yaml
# Standard core fields (1-9)
1. id
2. name
3. display_name
4. chemical_formula     # Scientific identifier
5. cas_number           # CAS registry number
6. molecular_weight     # Numeric value
7. category
8. subcategory
9. author
10. formula             # Display formula (if different)
11. images
12. exposure_guidelines # Safety text
13. detection_methods   # Detection procedures
14. first_aid           # Emergency response
15. health_effects      # Health impact description
16. health_effects_keywords # Keyword list
17. ppe_requirements    # PPE text
18. regulatory_standards # Compliance text
19. hazard_class        # Classification
20. monitoring_required # Boolean
21. typical_concentration_range # String
22. sources_in_laser_cleaning # List
23. relationships       # Related compounds/materials
24. card                # Card display config
25. metadata            # Domain metadata
26. faq                 # FAQ list
```

### Settings Domain (Settings.yaml)
```yaml
# Standard core fields (1-7, no author/micro/images)
1. id                   # e.g., "alabaster-settings"
2. name                 # Material name
3. category             # Material category
4. machine_settings     # Nested settings object
   - powerRange
   - wavelength
   - spotSize
   - repetitionRate
   - fluenceThreshold
   - pulseWidth
   - scanSpeed
5. application_notes    # Usage guidance
6. safety_notes         # Safety considerations
7. relationships        # Related materials
```

## Implementation Strategy

### Phase 1: Create Normalization Script
**File:** `scripts/tools/normalize_source_data_fields.py`

**Functionality:**
1. Load source YAML file
2. For each item, reorder fields according to domain standard
3. Remove export metadata fields
4. Preserve all data fields (no data loss)
5. Write back to YAML with consistent ordering
6. Backup original file before modification

**Features:**
- Dry-run mode (preview changes without writing)
- Per-domain field order templates
- Validation (ensure no fields lost)
- Logging (report what changed)

### Phase 2: Backup Current Data
```bash
# Create backups before normalization
cp data/materials/Materials.yaml data/materials/Materials.yaml.backup-jan5-2026
cp data/contaminants/Contaminants.yaml data/contaminants/Contaminants.yaml.backup-jan5-2026
cp data/compounds/Compounds.yaml data/compounds/Compounds.yaml.backup-jan5-2026
cp data/settings/Settings.yaml data/settings/Settings.yaml.backup-jan5-2026
```

### Phase 3: Execute Normalization (Dry-Run First)
```bash
# Preview changes without modifying files
python3 scripts/tools/normalize_source_data_fields.py --domain materials --dry-run
python3 scripts/tools/normalize_source_data_fields.py --domain contaminants --dry-run
python3 scripts/tools/normalize_source_data_fields.py --domain compounds --dry-run
python3 scripts/tools/normalize_source_data_fields.py --domain settings --dry-run

# Review output, verify field preservation

# Execute normalization (modifies files)
python3 scripts/tools/normalize_source_data_fields.py --domain materials
python3 scripts/tools/normalize_source_data_fields.py --domain contaminants
python3 scripts/tools/normalize_source_data_fields.py --domain compounds
python3 scripts/tools/normalize_source_data_fields.py --domain settings
```

### Phase 4: Update Export Process
**Ensure export process adds removed metadata:**

File: `export/generation/universal_content_generator.py` or new generator

Add task to generate export metadata:
```python
def _task_export_metadata(self, frontmatter: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add export metadata fields that should NOT exist in source data.
    
    Adds:
    - schemaVersion (from config)
    - contentType (from domain)
    - pageTitle (from name/title)
    - metaDescription (from micro/description)
    - fullPath (from slug/domain)
    - breadcrumb (from category hierarchy)
    - datePublished (from metadata)
    - dateModified (current timestamp)
    """
    # Implementation...
```

Update export configs:
```yaml
tasks:
  - type: export_metadata  # NEW: Add export-time metadata
    description: Add software metadata fields (NOT in source data)
  - type: camelcase_normalization
  - type: field_ordering
```

### Phase 5: Validation
```bash
# Verify source YAML clean (no export metadata)
python3 scripts/tools/validate_source_data_purity.py --all

# Verify export still produces correct frontmatter
python3 run.py --export --domain materials --limit 3
python3 run.py --export --domain contaminants --limit 3
python3 run.py --export --domain compounds --limit 3
python3 run.py --export --domain settings --limit 3

# Check frontmatter has all required fields
python3 scripts/tools/validate_frontmatter_completeness.py --all
```

### Phase 6: Documentation & Commit
```bash
git add data/materials/Materials.yaml
git add data/contaminants/Contaminants.yaml
git add data/compounds/Compounds.yaml
git add data/settings/Settings.yaml
git add scripts/tools/normalize_source_data_fields.py
git add export/generation/universal_content_generator.py
git add export/config/*.yaml

git commit -m "Normalize source data field ordering and remove export metadata

CHANGES:
- Standardized field order across all 4 domains (id, name, category, author first)
- Removed export metadata from source YAML (schemaVersion, contentType, fullPath, etc.)
- Added export_metadata task to generate software fields during export

ARCHITECTURE:
- Source YAML = Domain data ONLY (clean, ordered, consistent)
- Export process = Adds software metadata dynamically
- Frontmatter = Source + export metadata

BENEFITS:
- Consistent structure across domains
- Clear separation: source data vs export metadata
- Easier to maintain and validate source files
- Compliance with Core Principle 0.6 (no build-time data in source)

FILES NORMALIZED:
- data/materials/Materials.yaml (153 items)
- data/contaminants/Contaminants.yaml (100 items)
- data/compounds/Compounds.yaml (34 items)
- data/settings/Settings.yaml (230 items)

Related: Core Principle 0.6, SOURCE_DATA_NORMALIZATION_PLAN_JAN5_2026.md"
```

## Expected Impact

### Before Normalization:
- ❌ Inconsistent field order (author position varies: #1, #4, #9)
- ❌ Export metadata polluting source files (7+ fields per item)
- ❌ Difficult to compare items across domains
- ❌ Manual edits error-prone (hard to find fields)

### After Normalization:
- ✅ Consistent field order (id always #1, author always #7)
- ✅ Clean source files (domain data ONLY)
- ✅ Easy cross-domain comparison
- ✅ Predictable structure for scripts/tools
- ✅ Export metadata generated dynamically
- ✅ Clear architectural separation

## Testing Requirements

### Unit Tests (new file: `tests/test_source_data_normalization.py`)
1. `test_materials_field_order()` - Verify standard order in Materials.yaml
2. `test_contaminants_field_order()` - Verify standard order in Contaminants.yaml
3. `test_compounds_field_order()` - Verify standard order in Compounds.yaml
4. `test_settings_field_order()` - Verify standard order in Settings.yaml
5. `test_no_export_metadata_in_source()` - Verify NO schemaVersion, contentType, fullPath, etc. in source
6. `test_export_adds_metadata()` - Verify export process adds all required metadata
7. `test_field_preservation()` - Verify normalization doesn't lose data

### Integration Tests
1. Export all domains, verify frontmatter complete
2. Re-import frontmatter, verify data intact
3. Generate new content, verify correct field order
4. Run full test suite, verify no regressions

## Risk Mitigation

1. **Data Loss Risk**: Backups created before normalization
2. **Export Break Risk**: Validation step ensures frontmatter complete
3. **Regression Risk**: Comprehensive test suite
4. **Rollback Plan**: Restore from backup files if issues found

## Timeline

- **Day 1**: Create normalization script + dry-run testing
- **Day 2**: Execute normalization + update export process
- **Day 3**: Validation + testing + documentation
- **Day 4**: Commit + monitor for issues

## Success Criteria

✅ All 4 source YAML files have consistent field order
✅ Zero export metadata fields in source YAML
✅ Export process successfully generates all required metadata
✅ All 442 frontmatter files exported successfully
✅ Test suite passes (100%)
✅ No data loss (field count preserved)
✅ Documentation updated

## Related Documents

- Core Principle 0.6: No Build-Time Data Enhancement
- BUILD_TIME_VIOLATION_FIX_PLAN_JAN5_2026.md
- BACKEND_FRONTMATTER_REQUIREMENTS_JAN4_2026.md
- docs/05-data/DATA_STORAGE_POLICY.md
