# Conversion Scripts

One-time migration scripts for data format conversions.

## Files

### convert_aluminum_to_schema.py
Converts aluminum data from old format to new schema structure.
- Status: Historical (already applied)
- Input: data/materials/Materials.yaml (old aluminum entry)
- Output: Updated Materials.yaml with new schema

### convert_author_to_authorid.py
Migrates author objects to authorId reference system.
- Status: Historical (already applied)
- Input: Materials.yaml with embedded author objects
- Output: Materials.yaml with authorId integers + shared/authors registry

### convert_steel_to_schema.py
Converts steel data from old format to new schema structure.
- Status: Historical (already applied)
- Input: data/materials/Materials.yaml (old steel entry)
- Output: Updated Materials.yaml with new schema

## Usage

**Note**: These scripts were used for historical migrations. Run only if reverting changes or applying to new materials.

```bash
# From repository root
python scripts/conversion/convert_aluminum_to_schema.py
python scripts/conversion/convert_author_to_authorid.py
python scripts/conversion/convert_steel_to_schema.py
```

## Dependencies
- PyYAML for YAML manipulation
- ruamel.yaml for preserving YAML formatting
