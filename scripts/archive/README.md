# Scripts Archive

This directory contains historical scripts that were used during previous development phases but are no longer needed for day-to-day operations.

## Structure

### `historical-migrations/`
**One-time migration scripts from previous refactoring efforts.**

These scripts were used to restructure data, normalize schemas, and fix legacy issues. They should **NOT** be run again without careful consideration, as the codebase has evolved significantly since they were created.

**Archived Scripts**:
- `fix_dimensionless_units.py` - Fixed unit standardization issues (2024)
- `fix_frontmatter_compliance.py` - Schema compliance fixes (2024)
- `fix_frontmatter_conformity.py` - Conformity validation (2024)
- `fix_frontmatter_properties_nesting.py` - Property structure cleanup (2024)
- `flatten_properties_structure.py` - Flattened nested properties (2024)
- `migrate_other_properties.py` - Moved "other" category properties (2024)
- `normalize_materialproperties_structure.py` - Material properties normalization (2024)
- `normalize_materials_structure.py` - Materials YAML structure standardization (2024)
- `normalize_materials_to_template.py` - Template-based normalization (2024)
- `normalize_materials_yaml.py` - YAML format standardization (2024)
- `refactor_machine_settings.py` - Machine settings restructure (2024)
- `remove_other_category.py` - Removed "other" category (2024)
- `remove_subtitle_field.py` - Cleaned up subtitle field (2024)
- `reorganize_material_properties.py` - Property reorganization (2024)

**Status**: Completed and archived (Dec 20, 2025)  
**Do Not Run**: These are historical artifacts only

## Why Archive Instead of Delete?

These scripts are preserved for:
1. **Historical Reference** - Understanding past architecture decisions
2. **Code Examples** - Reusable patterns for future migrations
3. **Debugging** - If issues arise from past changes, these show what was done
4. **Documentation** - Evidence of technical debt resolution

## When to Use Archived Scripts

❌ **Never run archived scripts without**:
- Reviewing current codebase structure
- Understanding what changed since the script was written
- Testing on a backup/branch first
- Getting approval from project maintainers

✅ **Good uses**:
- Reading code to understand past patterns
- Adapting logic for new migrations
- Historical research during debugging

## Active Scripts

For current, actively-maintained scripts, see:
- `scripts/tools/` - Reusable utility tools
- `scripts/research/` - Data research and population
- `scripts/operations/` - Deployment and maintenance
- `scripts/validation/` - Data validation tools
