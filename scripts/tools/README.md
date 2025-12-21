# Scripts Tools - Active Utilities

This directory contains **actively maintained** reusable tools for the z-beam-generator project.

## Active Tools (34 scripts)

### Data Quality & Fixes (Keep - Recent/Active)
- ✅ `fix_missing_ranges.py` - Fixes missing min/max ranges in Settings.yaml (Dec 2025)
- ✅ `fix_settings_data_quality.py` - Fixes data quality issues (Dec 2025)
- ✅ `propagate_ranges_to_settings.py` - Propagates universal ranges (Dec 2025)
- ✅ `update_settings_frontmatter.py` - Syncs settings to frontmatter (Dec 2025)

### Analysis & Auditing
- `audit_code_structure_patterns.py` - Code structure analysis
- `audit_structure_comprehensive.py` - Comprehensive structure audit
- `health_check.py` - System health verification
- `export_diff.py` - Export comparison tool

### Data Population
- `add_active_field.py` - Adds active field to entries
- `add_contaminants.py` - Adds contaminant entries
- `add_id_field_to_frontmatter.py` - Adds ID field
- `add_regulatory_standard_ids.py` - Adds regulatory IDs
- `populate_contamination_properties.py` - Populates contamination data

### Research & Content
- `research_contaminants.py` - Researches contaminant data
- `research_contamination_patterns.py` - Researches contamination patterns
- `research_ceramics_with_sync.py` - Ceramics research with sync

### Validation & Quality
- `material_normalization_validator.py` - Validates material normalization
- `validate_frontmatter_guide.py` - Validates frontmatter against guides
- `query_challenges.py` - Queries challenge taxonomy

### Image Analysis
- `analyze_image.py` - Image analysis tool

### Batch Operations
- `batch_regenerate_descriptions.py` - Batch regenerates descriptions
- `create_category_taxonomy.py` - Creates category taxonomy
- `calculate_category_ranges.py` - Calculates category ranges

### Contamination Accuracy (Phase Tools)
- `contamination_accuracy_phase1.py` - Phase 1 accuracy checks
- `contamination_accuracy_phase2.py` - Phase 2 accuracy checks
- `phase1_quick_wins.py` - Phase 1 quick improvements

### Material Management
- `remove_material.py` - Removes material entries
- `update_materials_dates.py` - Updates material dates
- `update_materials_imports.py` - Updates import statements
- `integrate_research_citations.py` - Integrates citations

### Utility
- `run.py` - General purpose runner

## Archived Scripts

**14 historical migration scripts** moved to `scripts/archive/historical-migrations/`:
- One-time normalization, fix, migrate, refactor scripts from 2024
- See `scripts/archive/README.md` for details

## Usage Guidelines

### Before Running Any Script

1. **Read the script** - Understand what it does
2. **Check dependencies** - Ensure required data files exist
3. **Backup data** - Make git commit or backup before running
4. **Test on sample** - Try on single material/contaminant first
5. **Verify results** - Check output matches expectations

### Creating New Tools

New tools should:
- ✅ Have clear, descriptive names
- ✅ Include docstring explaining purpose
- ✅ Handle errors gracefully
- ✅ Log operations comprehensively
- ✅ Validate inputs before processing
- ✅ Be idempotent (safe to run multiple times)

### One-Time vs Reusable

**Reusable Tools** (keep in `scripts/tools/`):
- Can be run multiple times safely
- Solve recurring problems
- Well-documented and maintained

**One-Time Scripts** (move to `scripts/archive/` after use):
- Historical migrations
- Schema restructuring (already complete)
- One-off data fixes
- Deprecated functionality

## Maintenance

### Quarterly Review
- Audit tool usage (which are still needed?)
- Archive obsolete tools
- Update documentation
- Check for duplicate functionality

### Red Flags
If you see scripts like:
- `normalize_*_v2.py` (indicates repeated attempts)
- `fix_*_final.py` (suggests uncertainty)
- `temp_*.py` (temporary scripts)
- `old_*.py` (deprecated code)

→ These should be archived or deleted, not kept in active tools.

## Related Directories

- `scripts/research/` - Data research and population scripts
- `scripts/operations/` - Deployment and operational scripts
- `scripts/validation/` - Data validation scripts
- `scripts/archive/` - Historical and deprecated scripts
