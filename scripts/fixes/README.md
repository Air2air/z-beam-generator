# Fix Scripts

One-time scripts to repair data structure issues.

## Files

### final_structure_fix.py
Final pass at ensuring correct frontmatter structure after export.
- Status: Historical (applied during structure standardization)
- Input: Frontmatter YAML files
- Output: Corrected structure conforming to schema

### fix_structure.py
Initial structure correction script.
- Status: Historical (superseded by final_structure_fix.py)
- Input: Materials.yaml and frontmatter files
- Output: Basic structure corrections

### fix_structure_issues.py
Targeted fixes for specific structural inconsistencies.
- Status: Historical (applied during debugging)
- Input: Frontmatter files with known issues
- Output: Repaired structure

### quick_remove_presentation_type.py
Removes deprecated `presentation_type` field from frontmatter.
- Status: Historical (applied during field cleanup)
- Input: Frontmatter files with presentation_type
- Output: Cleaned frontmatter without deprecated field

## Usage

**Warning**: These are one-time fix scripts. Run only if recreating historical migrations or addressing similar issues in new data.

```bash
# From repository root
python scripts/fixes/final_structure_fix.py
python scripts/fixes/fix_structure.py
python scripts/fixes/fix_structure_issues.py
python scripts/fixes/quick_remove_presentation_type.py
```

## Dependencies
- PyYAML or ruamel.yaml for YAML manipulation
- Specific to data schema version when script was created
