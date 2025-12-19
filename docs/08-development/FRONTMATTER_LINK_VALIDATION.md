# Frontmatter Internal Link Validation System

**Purpose**: Ensure all internal links within frontmatter files are accurate, consistent, and maintain bidirectional integrity.

**Date**: December 18, 2025  
**Status**: ✅ IMPLEMENTED & OPERATIONAL

---

## Overview

**Two-tier validation system** ensures complete data integrity:

1. **Data Integrity Validation** (`verify_data_integrity.py`) - Validates source YAML files
2. **Frontmatter Path Validation** (`verify_frontmatter_links.py`) - Validates exported production files

### Why Two Validators?

| Validator | Scope | Purpose | When to Run |
|-----------|-------|---------|-------------|
| **Data Integrity** | `data/**/*.yaml` | Catch broken references at source | Before export |
| **Frontmatter Path** | `../z-beam/frontmatter/**/*.yaml` | Verify exported files | After export |

**Key Insight**: Data integrity issues must be fixed at source, path issues indicate export problems.

---

## Architecture

### Components

```
scripts/validation/
├── verify_data_integrity.py        # Source data validation
└── verify_frontmatter_links.py     # Exported frontmatter validation

Key Classes (data integrity):
- DataIntegrityValidator             # Validates source YAML
- DataIssue                          # Issue representation
- DataValidationReport               # Report aggregator

Key Classes (frontmatter):
- FrontmatterLinkValidator           # Validates exported files
- LinkIssue                          # Issue representation
- ValidationReport                   # Report aggregator
```

### Validation Flow

```
1. Data Integrity Validation (FIRST)
   ├── Load source YAML files
   ├── Build ID index per domain
   ├── Validate all relationships
   ├── Check bidirectional consistency
   └── Report broken references in SOURCE

2. Export Process (IF data valid)
   ├── Generate frontmatter from source
   ├── Apply enrichers
   └── Write to production directory

3. Frontmatter Path Validation (AFTER export)
   ├── Scan production frontmatter/*.yaml files
   ├── Check domain directories exist
   ├── Verify target files exist at paths
   ├── Validate URL formats
   ├── Check bidirectional links
   └── Report path/export issues
```

**Critical Rule**: Data integrity MUST pass before export. Frontmatter validation verifies export correctness.

---

## Usage

### 1️⃣ Data Integrity Validation (Run FIRST)

```bash
# Validate all source data
python3 scripts/validation/verify_data_integrity.py

# Validate specific domain
python3 scripts/validation/verify_data_integrity.py --domain materials
```

**Expected Output**:
```
📂 Using project root: /Users/todddunning/Desktop/Z-Beam/z-beam-generator

🔍 Loading source data files...
   ✅ materials: 153 items loaded from data/materials/Materials.yaml
   ✅ contaminants: 8 items loaded from data/contaminants/Contaminants.yaml
   ✅ compounds: 20 items loaded from data/compounds/Compounds.yaml
   ✅ settings: 153 items loaded from data/settings/Settings.yaml

📊 DATA INTEGRITY VALIDATION REPORT
================================================================================
📁 Source Files Validated: 4
📦 Total Items: 334
🔗 Total Relationships: 974

❌ ERRORS: 0
✅ No issues found! Data integrity is perfect.
```

### 2️⃣ Frontmatter Path Validation (Run AFTER export)

```bash
# Validate all exported frontmatter
python3 scripts/validation/verify_frontmatter_links.py

# Validate specific domain
python3 scripts/validation/verify_frontmatter_links.py --domain materials

# Export detailed report
python3 scripts/validation/verify_frontmatter_links.py --report links_report.md
```

**Expected Output**:
```
📂 Using frontmatter directory: /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter

📁 Checking domain directory structure...
   ✅ Found: materials (153 files)
   ✅ Found: contaminants (98 files)
   ✅ Found: compounds (20 files)
   ✅ Found: settings (153 files)

📊 FRONTMATTER LINK VALIDATION REPORT
================================================================================
📁 Files Scanned: 424
🔗 Total Links: 2,073

✅ No errors found!

⚠️  WARNINGS: 12
🟡 Missing Backlinks (8):
   • materials:aluminum links to contaminants:oil, but backlink missing
```

---

## Validation Rules

### 1. Broken Links (Errors)

**What**: Referenced ID doesn't exist in target domain

**Example**:
```yaml
relationships:
  related_contaminants:
    - id: oil-contamination  # ❌ ID doesn't exist
      title: Oil Contamination
```

**Fix**: Update ID to match existing contaminant or create the missing item.

---

### 2. Invalid URLs (Errors)

**What**: URL format doesn't match expected pattern

**Example**:
```yaml
relationships:
  related_materials:
    - id: aluminum-laser-cleaning
      url: /material/aluminum  # ❌ Should be /materials/
```

**Fix**: Correct URL pattern to `/materials/aluminum-laser-cleaning`

---

### 3. Missing Backlinks (Warnings)

**What**: A→B link exists but B→A doesn't

**Example**:
```yaml
# materials/aluminum.yaml
relationships:
  related_contaminants:
    - id: oil-laser-cleaning  # Links to oil

# contaminants/oil.yaml
relationships:
  related_materials: []  # ⚠️ No backlink to aluminum
```

**Fix**: Add reciprocal link in oil-laser-cleaning.yaml

---

### 4. Invalid Relationship Types (Warnings)

**What**: Relationship type not valid for domain

**Example**:
```yaml
# materials domain
relationships:
  produces_compounds:  # ⚠️ Invalid for materials
    - id: iron-oxide
```

**Valid types by domain**:
- **materials**: `related_contaminants`, `related_compounds`, `related_settings`, `regulatory_standards`
- **contaminants**: `related_materials`, `produces_compounds`, `recommended_settings`
- **compounds**: `produced_by_contaminants`, `related_materials`
- **settings**: `suitable_materials`, `effective_contaminants`

---

### 5. Orphaned Items (Info)

**What**: Item has no incoming or outgoing relationships

**Example**:
```yaml
# compounds/rare-compound.yaml
relationships: {}  # ℹ️ No connections to other items
```

**Fix**: Either add relationships or remove if item is no longer needed.

---

## Bidirectional Link Mappings

The system validates these bidirectional relationships:

| Domain A | Relationship A | ↔ | Domain B | Relationship B |
|----------|---------------|---|----------|---------------|
| materials | `related_contaminants` | ↔ | contaminants | `related_materials` |
| materials | `related_compounds` | ↔ | compounds | `related_materials` |
| materials | `related_settings` | ↔ | settings | `suitable_materials` |
| contaminants | `produces_compounds` | ↔ | compounds | `produced_by_contaminants` |
| contaminants | `recommended_settings` | ↔ | settings | `effective_contaminants` |

---

## Integration

### Pre-Deployment Check

Add to deployment workflow:

```bash
# .github/workflows/deploy.yml
- name: Validate Internal Links
  run: |
    python3 scripts/validation/verify_frontmatter_links.py
    if [ $? -ne 0 ]; then
      echo "❌ Link validation failed - fix broken links before deploying"
      exit 1
    fi
```

### Pre-Commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 scripts/validation/verify_frontmatter_links.py --domain materials
```

### CI/CD Pipeline

```yaml
# Run validation after export
- name: Export Frontmatter
  run: python3 run.py --export-all

- name: Validate Links
  run: |
    python3 scripts/validation/verify_frontmatter_links.py --report validation_report.md
    
- name: Upload Report
  uses: actions/upload-artifact@v2
  with:
    name: link-validation-report
    path: validation_report.md
```

---

## Future Enhancements

### Phase 2: Auto-Fixing

```python
# Add --fix flag support
validator = FrontmatterLinkValidator(frontmatter_root)
validator.validate_all()

if args.fix:
    validator.auto_fix_simple_issues()
    # - Remove broken links
    # - Add missing backlinks
    # - Correct URL formats
```

### Phase 3: Performance Optimization

```python
# Cache index between runs
validator.load_cached_index()
validator.validate_changed_files_only(changed_files)
```

### Phase 4: Visual Report

```html
<!-- Generate HTML report with interactive graph -->
<script src="d3.js"></script>
<div id="link-graph"></div>
<!-- Visualize relationships and highlight issues -->
```

---

## Testing

### Test Cases

```python
# tests/test_link_validator.py

def test_detects_broken_link():
    # Given: material links to non-existent contaminant
    # When: validator runs
    # Then: broken link error reported

def test_detects_missing_backlink():
    # Given: A→B exists but B→A doesn't
    # When: validator runs
    # Then: missing backlink warning reported

def test_validates_url_format():
    # Given: URL uses wrong pattern
    # When: validator runs
    # Then: invalid URL error reported

def test_finds_orphaned_items():
    # Given: item with no relationships
    # When: validator runs
    # Then: orphaned item info reported
```

---

## Maintenance

### Regular Audits

```bash
# Weekly link validation
crontab -e
0 0 * * 0 cd /path/to/project && python3 scripts/validation/verify_frontmatter_links.py --report weekly_report.md
```

### Metrics Tracking

Track over time:
- Total links count
- Broken link rate
- Orphaned items count
- Missing backlink rate

---

## Documentation

- **Script**: `scripts/validation/verify_frontmatter_links.py`
- **This Guide**: `docs/08-development/FRONTMATTER_LINK_VALIDATION.md`
- **Issue Format**: `LinkIssue` dataclass in script
- **Report Format**: Console + Markdown export

---

## References

- [Frontmatter Field Order](../data/schemas/FrontmatterFieldOrder.yaml)
- [Domain Linkages Spec](DOMAIN_LINKAGES_VALIDATION_DEC17_2025.md)
- [Export Architecture](../../export/README.md)
