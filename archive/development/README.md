# Scripts Directory

**📁 Organized utility scripts for Z-Beam Generator**  
**📅 Last Updated**: September 16, 2025  
**🧹 Recently Cleaned**: Obsolete scripts archived, active utilities organized

---

## �️ Directory Structure

```
scripts/
├── 📋 CLEANUP_REPORT.md          # Recent cleanup operation report  
├── 📖 README.md                  # This file
├── 🗃️ archive/                   # Historical/legacy scripts (organized by category)
├── 🧹 cleanup/                   # Content and system cleanup utilities
├── 📊 evaluation/                # Content quality evaluation scripts
├── 🔧 maintenance/               # System maintenance and monitoring
├── 🧪 testing/                   # Test automation and validation
├── 🛠️ tools/                     # Active diagnostic and utility tools
├── 📄 temp/                      # Temporary files and working scripts
├── 🗑️ remove_material.py         # Material removal utility
├── ⚡ run_error_workflow.sh      # Error testing workflow
└── ✅ validate_technical_accuracy.py  # Technical validation script
```

## 🛠️ Active Scripts (Post-Cleanup)

### 🔧 Tools (`scripts/tools/`)
**Primary utilities for system diagnostics and operations**

- **`api_terminal_diagnostics.py`** - Comprehensive API connectivity diagnostics with terminal output analysis
- **`cleanup_scripts.py`** - Script organization and obsolete file archival utility
- **`fix_metatags_format.py`** - Fix meta tags formatting issues
- **`fix_nested_yaml_properties.py`** - Fix nested YAML property structures
- **`generate_all_authors.py`** - Batch author component generation for all materials
- **`prompt_chain_diagnostics.py`** - Diagnostic tool for prompt chain system
- **`quick_content_humanizer.py`** - Content humanization utility
- **`sentence_structure_optimizer.py`** - Sentence structure optimization tool

### 🔧 Maintenance (`scripts/maintenance/`)
**System maintenance and monitoring scripts**

- Regular maintenance procedures
- Backup management utilities
- Performance monitoring tools
- System health checks

### 📊 Evaluation (`scripts/evaluation/`)
**Content quality and system evaluation**

- End-to-end content evaluation
- Quality metrics analysis
- System performance evaluation
- Content validation workflows

### 🧪 Testing (`scripts/testing/`)
**Test automation and validation utilities**

- Automated testing scripts
- System validation tools
- Test infrastructure utilities
- Integration test helpers

### 🧹 Cleanup (`scripts/cleanup/`)
**Content and system cleanup utilities**

- Content directory cleanup
- Generator cleanup utilities
- System cleanup procedures

### 📄 Root Level Utilities
**Essential operational scripts**

- **`remove_material.py`** - Safe material removal from database
- **`run_error_workflow.sh`** - Comprehensive error testing workflow
- **`validate_technical_accuracy.py`** - Technical content validation

## 🗃️ Archive Organization

**Purpose**: Historical preservation of completed one-time scripts

### `scripts/archive/normalization-legacy/`
- YAML/frontmatter normalization scripts
- Format standardization utilities
- **Status**: Tasks completed, preserved for reference

### `scripts/archive/image-processing-legacy/`
- Image naming and processing scripts
- Image conflict resolution utilities
- **Status**: Image organization completed

### `scripts/archive/material-migration-legacy/`
- Material data migration scripts
- Data structure enhancement tools
- **Status**: Migration tasks completed

### `scripts/archive/frontmatter-updates-legacy/`
- One-time frontmatter update scripts
- Author synchronization utilities
- **Status**: Update tasks completed

### `scripts/archive/one-time-scripts/`
- Various one-time operation scripts
- Label updates and format changes
- Configuration proposals
- **Status**: Operations completed

### `scripts/archive/debug-scripts/`
- Temporary debugging scripts
- Development utilities
- **Status**: Debug tasks completed

## 🚀 Usage Guide

### Running Active Scripts

**Tools:**
```bash
# API diagnostics (recommended for troubleshooting)
python3 scripts/tools/api_terminal_diagnostics.py winston

# Batch author generation
python3 scripts/tools/generate_all_authors.py

# YAML property fixes
python3 scripts/tools/fix_nested_yaml_properties.py
```

**Utilities:**
```bash
# Remove material (with confirmation)
python3 scripts/remove_material.py --material "MaterialName" --confirm

# Technical validation
python3 scripts/validate_technical_accuracy.py

# Error workflow testing
./scripts/run_error_workflow.sh
```

### Safety Guidelines

1. **🔒 Always backup**: Scripts modify important data
2. **🧪 Test first**: Many support `--dry-run` mode
3. **📖 Read docs**: Check script docstrings before use
4. **👀 Review changes**: Verify git diff before commit
5. **🎯 Single purpose**: Run one script at a time

### Best Practices

- **Idempotent operations**: Safe to run multiple times
- **Verbose logging**: Clear output about operations
- **Graceful failure**: Handle missing files and invalid data
- **Dependency checking**: Validate requirements before execution

## 📊 Cleanup Impact

**Recent cleanup results (September 16, 2025):**

- ✅ **33 files archived**: Obsolete scripts moved to organized archive
- ✅ **1 script reorganized**: Root utilities moved to proper locations
- ✅ **Clear structure**: Active vs. historical scripts separated
- ✅ **Preserved functionality**: All essential utilities maintained
- ✅ **Improved navigation**: Categorized by purpose and status

## � Future Scripts

**Guidelines for new scripts:**

1. **📍 Proper location**: Tools, maintenance, evaluation, or testing
2. **🎯 Clear purpose**: Single responsibility principle
3. **📚 Documentation**: Comprehensive docstrings and usage examples
4. **🛡️ Error handling**: Robust error handling and logging
5. **🔄 Integration**: Compatible with existing utilities and workflows

---

**🛠️ Active Scripts**: Focused on current operational needs  
**🗃️ Archived Scripts**: Preserved for reference and rollback capabilities  
**📊 Organized Structure**: Clear separation by purpose and lifecycle status
