# Z-Beam Generator - Project Conventions

## File Structure Convention

### 📋 **MANDATORY RULE: Content Above Frontmatter**

**ALL optimized content files MUST follow this structure:**

```
[CONTENT]
---
[EXISTING FRONTMATTER]
[NEW FRONTMATTER DATA]
---
```

### ✅ **Correct Format:**
```
Ah, copper. A magnificent metal, no? It's beautiful, it's conductive...
[Article content appears here]

---
name: Copper
applications:
- industry: Electronics Manufacturing
  detail: Removal of oxidation...

ai_detection_analysis:
  score: 1.83
  confidence: 0.0366
  classification: "ai"
  provider: "winston"
  processing_time: 1.8034119606018066
---

iteration_history:
  # ... optimization history
---
```

### ❌ **Incorrect Format:**
```
---
ai_detection_analysis:
  score: 1.83
  # ... frontmatter data
---

Ah, copper. A magnificent metal, no? It's beautiful, it's conductive...
[Article content appears here]
```

## Frontmatter Management Rules

### 🔄 **Frontmatter Preservation:**
- **Existing frontmatter MUST be preserved** when adding new data
- **New frontmatter data is appended** to existing frontmatter
- **Never replace existing frontmatter** - always append
- **Maintain proper YAML structure** when merging data

### 📝 **Frontmatter Updates:**
- AI detection analysis is added to existing frontmatter
- Optimization metadata is appended, not replaced
- Historical data (iterations, timestamps) is preserved
- Component-specific data remains intact

## Why This Convention?

1. **Content Priority**: The actual article content should be the primary focus
2. **SEO Benefits**: Search engines and readers see content first
3. **Better Readability**: Content appears immediately when opening files
4. **Tool Compatibility**: Some tools expect content before metadata
5. **Consistency**: All optimized files follow the same structure

## Implementation Requirements

### 🔧 **For Developers:**
- All optimization scripts must output content in this format
- File validation tools should check this structure
- Code reviews must enforce this convention

### 🔧 **For Tools:**
- Optimization orchestrator must generate files with content first
- File parsers should handle this non-standard format
- Import/export tools should preserve this structure

### � **Automated Generation:**
- `run.py` optimization script automatically follows this convention
- Content is placed above frontmatter in generated files
- AI detection analysis is added to frontmatter section
- All new optimized files will follow this structure by default

### �📝 **Migration:**
- Existing files should be migrated to this format
- Legacy format files should be flagged for conversion
- Documentation should reflect this new standard

## Validation

Files can be validated using the provided script:
```bash
# Validate a single file
python3 validate_structure.py content/components/text/copper-laser-cleaning.md

# Validate all files in a directory
python3 validate_structure.py content/

# Validate with custom extensions
python3 validate_structure.py content/ --extensions .md,.markdown
```

## Migration

Existing files can be migrated using the migration script:
```bash
# Migrate a single file (creates backup)
python3 migrate_structure.py content/components/frontmatter/copper-laser-cleaning.md

# Migrate all files in directory
python3 migrate_structure.py content/

# Migrate without backups
python3 migrate_structure.py content/ --no-backup
```

The migration script will:
- ✅ Move content above frontmatter
- ✅ Preserve all existing data
- ✅ Create backup files automatically
- ✅ Skip files that already follow the convention
- ✅ Report migration statistics

---

**Effective Date:** September 5, 2025  
**Last Updated:** September 5, 2025  
**Enforcement:** Mandatory for all new optimized files  
**Migration Status:** Tools available for existing files

## 📋 **Current Status**

✅ **Completed:**
- Global convention established and documented
- Example file (copper-laser-cleaning.md) restructured
- Optimization code updated to follow convention
- Validation and migration scripts created
- Frontmatter preservation implemented
- Comprehensive test suite created (`test_file_structure.py`)

🔄 **In Progress:**
- Migration of existing optimized files
- Integration with CI/CD pipeline
- Developer training and documentation updates

## 🛠️ **Available Tools**

- `validate_structure.py` - Validates file structure compliance
- `migrate_structure.py` - Migrates existing files (with backup)
- `test_file_structure.py` - Comprehensive test suite for file structure
- Updated `run.py` - Generates new files following convention
