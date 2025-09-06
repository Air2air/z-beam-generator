# Scripts Directory

This directory contains utility scripts organized by function:

## 📁 Directory Structure

### `/testing/` - Test and Demonstration Scripts
- `test_*.py` - Various component and integration tests
- `demonstrate_content_scoring.py` - Content scoring system demonstration
- `production_test.py` - Production readiness testing

### `/cleanup/` - Cleanup and Maintenance Scripts
- `cleanup_*.py` - Component and directory cleanup utilities
- `final_cleanup.py` - Final system cleanup operations

### `/evaluation/` - Evaluation and Validation Scripts
- `evaluate_*.py` - Content and system evaluation utilities
- `e2e_*.py` - End-to-end testing scripts
- `final_validation.py` - Final system validation
- `validate_authenticity.py` - Content authenticity validation

### `/` (Root Scripts) - General Utilities
- `enhance_materials_from_frontmatter.py` - Material enhancement utilities
- `integrate_enhanced_materials.py` - Material integration scripts
- `migrate_materials_metadata.py` - Metadata migration tools
- `update_*.py` - Various update utilities
- `debug_config.py` - Configuration debugging
- `materials_enhanced_proposal.yaml` - Material enhancement proposals

## 🚀 Usage

Most scripts can be run from the project root:

```bash
# Run content scoring demonstration
python scripts/testing/demonstrate_content_scoring.py

# Run comprehensive tests
python scripts/testing/test_all_authors.py

# Validate content authenticity
python scripts/evaluation/validate_authenticity.py
```

## 📝 Notes

- All scripts maintain their original functionality
- Scripts are organized for better maintainability
- Test output is preserved in `/test_output/legacy_content/`
