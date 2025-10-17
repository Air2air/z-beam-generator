# Automated Schema Update System

**Created**: October 16, 2025  
**Tool**: `scripts/tools/schema_updater.py`  
**Purpose**: Automatically sync JSON schemas with YAML data structure

---

## 🎯 Overview

The Schema Updater automates the previously manual process of updating JSON schemas when Categories.yaml or Materials.yaml changes. It ensures schemas stay synchronized with actual data structure.

### What It Automates

| Before (Manual) | After (Automated) |
|----------------|-------------------|
| Developer edits Categories.yaml | ✅ Same |
| **Developer manually edits frontmatter.json** | ✅ **`schema_updater.py --update frontmatter`** |
| **Developer manually updates category enums** | ✅ **Auto-extracted from Categories.yaml** |
| **Developer manually updates subcategory enums** | ✅ **Auto-extracted from Materials.yaml** |
| **Developer manually updates property lists** | ✅ **Auto-extracted from PROPERTY_RULES** |
| Git commit schema changes | ✅ Same |

---

## 🚀 Quick Start

### Validate Current Schemas
```bash
# Check if schemas match current data
python3 scripts/tools/schema_updater.py --validate-only
```

**Output**:
```
✅ All schemas are valid and up-to-date
```

Or if out of sync:
```
❌ Found 2 validation issues:
  - frontmatter.json: Missing categories: {'nanomaterial'}
  - frontmatter.json: Extra subcategories: {'obsolete-type'}

Run with --update all to fix these issues
```

### Update Specific Schema
```bash
# Update frontmatter.json only
python3 scripts/tools/schema_updater.py --update frontmatter

# Update categories_schema.json only
python3 scripts/tools/schema_updater.py --update categories

# Update materials_schema.json only
python3 scripts/tools/schema_updater.py --update materials
```

### Update All Schemas
```bash
# Update all schemas at once
python3 scripts/tools/schema_updater.py --update all
```

### Dry Run (Preview Changes)
```bash
# See what would change without making changes
python3 scripts/tools/schema_updater.py --update all --dry-run
```

---

## 📊 What Gets Updated

### 1. **frontmatter.json**

#### Category Enum
```json
// Before (manual)
"category": {
  "enum": ["metal", "ceramic", "composite"]
}

// After (auto-updated from Categories.yaml)
"category": {
  "enum": ["metal", "ceramic", "composite", "semiconductor", "glass", "stone", "wood", "plastic", "masonry"]
}
```

**Source**: `Categories.yaml → categories`

#### Subcategory Enum
```json
// Auto-updated from all subcategories in Materials.yaml
"subcategory": {
  "enum": [
    "precious", "ferrous", "non-ferrous", "refractory",
    "oxide", "nitride", "carbide", "traditional",
    // ... all unique subcategories
  ]
}
```

**Source**: `Materials.yaml → materials → items → subcategory`

#### Property Categories
```json
// Auto-updated from Categories.yaml propertyCategories
"propertyCategory": {
  "enum": [
    "laser_material_interaction",
    "material_characteristics",
    "process_optimization"
  ]
}
```

**Source**: `Categories.yaml → propertyCategories → categories`

### 2. **categories_schema.json**

- Validates property count from PROPERTY_RULES
- Updates metadata with property statistics
- Ensures schema matches Categories.yaml structure

### 3. **materials_schema.json**

- Updates category count
- Updates material count
- Updates property count
- Adds validation metadata

---

## 🔄 Workflow Integration

### When to Run Schema Updates

#### 1. **After Adding New Category**
```yaml
# Edit Categories.yaml
categories:
  nanomaterial:  # NEW CATEGORY
    category_ranges:
      density: {min: 100, max: 5000}
```

```bash
# Update schemas
python3 scripts/tools/schema_updater.py --update frontmatter
```

#### 2. **After Adding New Material**
```yaml
# Edit Materials.yaml
materials:
  metal:
    items:
      - name: "Titanium Alloy"
        subcategory: "specialty"  # NEW SUBCATEGORY
```

```bash
# Update schemas
python3 scripts/tools/schema_updater.py --update frontmatter
```

#### 3. **After Property Consolidation**
```python
# Edit scripts/validation/comprehensive_validation_agent.py
PROPERTY_RULES = {
    'newProperty': PropertyRule(...),  # NEW PROPERTY
    # ...
}
```

```bash
# Update all schemas
python3 scripts/tools/schema_updater.py --update all
```

#### 4. **Before Committing Data Changes**
```bash
# Validate schemas match data
python3 scripts/tools/schema_updater.py --validate-only

# If issues found, update
python3 scripts/tools/schema_updater.py --update all

# Commit both data and schemas together
git add data/Categories.yaml data/Materials.yaml schemas/*.json
git commit -m "feat: add nanomaterial category with updated schemas"
```

---

## 🛠️ Architecture

### Data Flow

```
Categories.yaml → SchemaUpdater → frontmatter.json
    ↓                  ↓              ↓
Materials.yaml    Extract Data   Updated Enums
    ↓                  ↓              ↓
PROPERTY_RULES    Validate      Add Metadata
    ↓                  ↓              ↓
                  Write JSON    Git Commit
```

### Extraction Methods

| Method | Source | Updates |
|--------|--------|---------|
| `extract_categories()` | Categories.yaml | category enum |
| `extract_subcategories()` | Materials.yaml | subcategory enum |
| `extract_property_categories()` | Categories.yaml | propertyCategory enum |
| `extract_properties()` | PROPERTY_RULES | property metadata |
| `extract_material_names()` | Materials.yaml | material validation |

---

## 📋 Output Report

### Sample Report
```
======================================================================
SCHEMA UPDATE REPORT
======================================================================

Timestamp: 2025-10-16T18:30:45.123456
Schemas Updated: 3
Total Changes: 7

📄 frontmatter.json
----------------------------------------------------------------------
  ✓ Updated categories: 9 items
  ✓ Updated subcategories: 47 items
  ✓ Updated property categories: 3 items
  • categories_count: 9
  • subcategories_count: 47

📄 categories_schema.json
----------------------------------------------------------------------
  ✓ Validated 47 properties
  • property_count: 47

📄 materials_schema.json
----------------------------------------------------------------------
  ✓ Validated 9 categories
  ✓ Validated 121 materials
  ✓ Validated 47 properties
  • category_count: 9
  • material_count: 121
  • property_count: 47

======================================================================
```

---

## 🔍 Validation Rules

### What Gets Validated

1. **Category Consistency**
   - Categories in schema match Categories.yaml
   - No missing or extra categories

2. **Subcategory Completeness**
   - All subcategories from Materials.yaml included
   - No obsolete subcategories in schema

3. **Property Category Alignment**
   - Property categories match Categories.yaml structure
   - propertyCategory enum is current

### Validation Issues

```bash
# Example validation output
❌ Found 3 validation issues:
  - frontmatter.json: Missing categories: {'nanomaterial'}
  - frontmatter.json: Extra categories: {'obsolete-category'}
  - frontmatter.json: Missing subcategories: {'specialty'}
```

**Resolution**:
```bash
python3 scripts/tools/schema_updater.py --update frontmatter
```

---

## 🎯 Use Cases

### Use Case 1: Property Consolidation (3→2 Categories)

**Scenario**: Consolidated property categories from 3 to 2

```bash
# 1. Update Categories.yaml
vim data/Categories.yaml  # Remove old category, update enums

# 2. Preview changes
python3 scripts/tools/schema_updater.py --update frontmatter --dry-run

# 3. Apply updates
python3 scripts/tools/schema_updater.py --update frontmatter

# 4. Validate
python3 scripts/tools/schema_updater.py --validate-only

# 5. Commit
git add data/Categories.yaml schemas/frontmatter.json
git commit -m "feat: consolidate property categories to 2-category system"
```

### Use Case 2: New Material Category

**Scenario**: Adding "nanomaterial" category

```bash
# 1. Add to Categories.yaml
categories:
  nanomaterial:
    category_ranges: {...}

# 2. Update schemas
python3 scripts/tools/schema_updater.py --update all

# 3. Verify
python3 scripts/tools/schema_updater.py --validate-only
✅ All schemas are valid and up-to-date

# 4. Test with generation
python3 run.py --material "Carbon Nanotube"  # Uses new category

# 5. Commit
git add data/Categories.yaml schemas/*.json
git commit -m "feat: add nanomaterial category v5.0.0"
```

### Use Case 3: Subcategory Addition

**Scenario**: Adding new subcategory "bio-based" to plastics

```bash
# 1. Add material with new subcategory in Materials.yaml
materials:
  plastic:
    items:
      - name: "PLA"
        subcategory: "bio-based"  # NEW

# 2. Update frontmatter schema
python3 scripts/tools/schema_updater.py --update frontmatter

# Output:
#   ✓ Updated subcategories: 48 items (was 47)

# 3. Commit
git add data/Materials.yaml schemas/frontmatter.json
git commit -m "feat: add bio-based plastic subcategory"
```

---

## 🔧 Advanced Options

### Verbose Logging
```bash
# See detailed extraction and update process
python3 scripts/tools/schema_updater.py --update all --verbose
```

### Combining Flags
```bash
# Dry run with verbose output
python3 scripts/tools/schema_updater.py --update all --dry-run --verbose
```

---

## 🚨 Error Handling (Fail-Fast)

Per GROK_INSTRUCTIONS.md, the tool uses strict fail-fast architecture:

### Validation Errors (Immediate Failure)
```python
# Missing Materials.yaml
❌ Schema update failed: Materials.yaml not found: /path/to/Materials.yaml

# Invalid YAML
❌ Schema update failed: Failed to load Categories.yaml: invalid syntax

# Missing schema file
❌ Schema update failed: Frontmatter schema not found: /path/to/frontmatter.json
```

**No silent failures, no fallbacks, no default values.**

---

## 📊 Metadata Added to Schemas

Updated schemas include metadata about the update:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Frontmatter Schema",
  "metadata": {
    "last_auto_update": "2025-10-16T18:30:45.123456",
    "auto_update_changes": [
      "Updated categories: 9 items",
      "Updated subcategories: 47 items"
    ]
  }
}
```

---

## 🔄 CI/CD Integration (Future)

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check if data files changed
if git diff --cached --name-only | grep -q "data/.*\.yaml"; then
    echo "📊 Data files changed, validating schemas..."
    
    python3 scripts/tools/schema_updater.py --validate-only
    if [ $? -ne 0 ]; then
        echo "❌ Schemas out of sync with data!"
        echo "Run: python3 scripts/tools/schema_updater.py --update all"
        exit 1
    fi
fi
```

### GitHub Actions
```yaml
# .github/workflows/schema-validation.yml
name: Schema Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Schemas
        run: |
          python3 scripts/tools/schema_updater.py --validate-only
```

---

## 📚 Benefits

### Before Automation
- ❌ Manual schema editing prone to errors
- ❌ Easy to forget to update schemas
- ❌ Schema/data mismatches cause validation failures
- ❌ Time-consuming to keep enums synchronized
- ❌ No validation that schemas match data

### After Automation
- ✅ **One command** updates all schemas
- ✅ **Validation** ensures schemas match data
- ✅ **Dry run** previews changes safely
- ✅ **Fail-fast** catches missing dependencies
- ✅ **Metadata tracking** shows update history
- ✅ **Consistent** enum synchronization
- ✅ **Time saved** - seconds vs minutes per update

---

## 🎯 Summary

**The Schema Updater transforms schema maintenance from a manual, error-prone process into an automated, reliable workflow.**

### Core Capabilities
1. ✅ **Extract** categories, subcategories, properties from data
2. ✅ **Update** JSON schemas with current structure
3. ✅ **Validate** schemas match data
4. ✅ **Report** changes with detailed statistics
5. ✅ **Fail-fast** on missing dependencies

### Recommended Workflow
```bash
# 1. Edit data files
vim data/Categories.yaml
vim data/Materials.yaml

# 2. Validate current state
python3 scripts/tools/schema_updater.py --validate-only

# 3. Update schemas if needed
python3 scripts/tools/schema_updater.py --update all

# 4. Commit together
git add data/*.yaml schemas/*.json
git commit -m "feat: update data and schemas"
```

**Never worry about schema/data mismatches again!** 🎉
