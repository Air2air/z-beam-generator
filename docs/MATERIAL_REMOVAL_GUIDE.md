# Material Removal Script Documentation

## Overview

The `remove_material.py` script provides comprehensive material removal capabilities for the Z-Beam Generator. It can safely remove materials from the materials list and delete all associated generated content files.

## Features

### 🔍 **Material Discovery**
- List all available materials by category
- Find orphaned files that don't match any material
- Search for materials with fuzzy matching

### 🗑️ **Safe Removal**
- Dry-run mode (default) for safe preview
- Remove material from materials.yaml
- Delete all associated component files
- Comprehensive error handling

### 🛡️ **Safety Features**
- Always defaults to dry-run mode
- Optional confirmation prompts
- Automatic backup of materials.yaml
- Detailed logging and reporting

## Usage Examples

### List All Materials
```bash
# Show all materials organized by category
python3 remove_material.py --list-materials
```

### Find Orphaned Files
```bash
# Find files that don't correspond to any material
python3 remove_material.py --find-orphans
```

### Preview Material Removal (Safe)
```bash
# Dry run - shows what would be removed without making changes
python3 remove_material.py --material "Metal Matrix Composites MMCs" --dry-run
```

### Actually Remove Material
```bash
# Execute removal (with confirmation)
python3 remove_material.py --material "Metal Matrix Composites MMCs" --execute --confirm

# Execute removal (without confirmation)
python3 remove_material.py --material "Metal Matrix Composites MMCs" --execute
```

### Verbose Output
```bash
# Enable detailed logging
python3 remove_material.py --material "Aluminum" --dry-run --verbose
```

## Component Types Affected

The script will find and remove files from these component directories:

- `frontmatter/` - YAML metadata files
- `content/` - Main article content
- `metatags/` - SEO meta tags
- `jsonld/` - JSON-LD structured data
- `tags/` - Navigation tags
- `bullets/` - Key feature bullet points
- `caption/` - Image captions
- `table/` - Technical specification tables
- `propertiestable/` - Material properties tables
- `badgesymbol/` - Material symbols and badges
- `author/` - Author information

## Safety Mechanisms

### 1. Dry-Run Default
- All operations default to dry-run mode
- Must explicitly use `--execute` to make changes
- Shows exactly what would be removed

### 2. Confirmation Prompts
- Optional `--confirm` flag requires user confirmation
- Prevents accidental removals in scripts

### 3. Backup Creation
- Automatically backs up `materials.yaml` before changes
- Backup saved as `materials.yaml.backup`

### 4. Error Handling
- Graceful handling of missing files
- Detailed error reporting
- Non-zero exit codes for errors

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--material "Name"` | Material name to remove |
| `--dry-run` | Preview mode (default) |
| `--execute` | Actually perform removal |
| `--confirm` | Require confirmation |
| `--list-materials` | List all materials |
| `--find-orphans` | Find orphaned files |
| `--verbose` | Enable detailed logging |

## Example Output

### Material Listing
```
📋 Available materials by category:
==================================================

📂 COMPOSITE (13 materials):
    1. Carbon Fiber Reinforced Polymer
       Slug: carbon-fiber-reinforced-polymer
    2. Metal Matrix Composites MMCs
       Slug: metal-matrix-composites-mmcs
    ...

📊 Total: 121 materials across 8 categories
```

### Removal Preview
```
🔍 DRY RUN MODE - No changes will be made
============================================================
Processing material: Metal Matrix Composites MMCs
Found material 'Metal Matrix Composites MMCs' in category 'composite' at index 11
Found 11 files across 11 component types:
  frontmatter: 1 files
    - metal-matrix-composites-mmcs-laser-cleaning.md
  content: 1 files
    - metal-matrix-composites-mmcs-laser-cleaning.md
  ...

📊 REMOVAL RESULTS:
========================================
✅ Material found in category: composite
📁 Found 11 files to remove:
   frontmatter: 1 files
   content: 1 files
   ...

🔍 DRY RUN COMPLETE - Use --execute to apply changes
```

### Orphaned Files Detection
```
🔍 Finding orphaned files...
==================================================
Found 2 orphaned files:

📂 badgesymbol (2 files):
   - epoxy-resin.md
   - kevlar.md

💡 Use --material with --execute to remove specific materials
   Or manually review and delete orphaned files
```

## Integration with Project

### Slug Utilities
- Uses the same slug generation as the main generators
- Consistent with `utils/slug_utils.py`
- Handles material names with special characters

### File Structure Awareness
- Knows about all component directory structures
- Handles the standard filename pattern: `{material-slug}-laser-cleaning.md`
- Compatible with clean path naming conventions

### Materials.yaml Integration
- Reads and writes YAML safely
- Preserves structure and metadata
- Creates automatic backups

## Best Practices

### 1. Always Test First
```bash
# Always run dry-run first
python3 remove_material.py --material "Material Name" --dry-run
```

### 2. Use Confirmation for Important Materials
```bash
# Require confirmation for important removals
python3 remove_material.py --material "Important Material" --execute --confirm
```

### 3. Check for Orphans Regularly
```bash
# Periodically check for orphaned files
python3 remove_material.py --find-orphans
```

### 4. Use in Scripts
```bash
#!/bin/bash
# Script to remove multiple materials

materials=("Old Material 1" "Old Material 2" "Test Material")

for material in "${materials[@]}"; do
    echo "Removing $material..."
    python3 remove_material.py --material "$material" --execute
done
```

## Error Scenarios

### Material Not Found
- Script continues but reports error
- No files are removed
- Exit code 1

### File Permission Issues
- Reports specific file errors
- Continues with other files
- Shows detailed error messages

### Materials.yaml Issues
- Backs up file before changes
- Reports YAML parsing errors
- Graceful fallback handling

## Maintenance

### Adding New Component Types
To support new component types, update the `component_types` list:

```python
self.component_types = [
    "frontmatter", "content", "metatags", "jsonld",
    "tags", "bullets", "caption", "table",
    "propertiestable", "badgesymbol", "author",
    "new_component_type"  # Add new types here
]
```

### Updating File Patterns
The script uses the standard pattern `{material-slug}-laser-cleaning.md`. To support different patterns, modify the `find_material_files` method.

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure write permissions on content directories
   - Check file ownership

2. **Material Not Found**
   - Verify exact material name (case sensitive)
   - Use `--list-materials` to see available options

3. **Orphaned Files**
   - Review files manually before deletion
   - May indicate naming inconsistencies

### Debugging
```bash
# Enable verbose logging for debugging
python3 remove_material.py --material "Material" --dry-run --verbose
```

## See Also

- [CLEAN_PATHS_SUMMARY.md](CLEAN_PATHS_SUMMARY.md) - Clean path implementation
- [utils/slug_utils.py](utils/slug_utils.py) - Slug generation utilities
- [cleanup_paths.py](cleanup_paths.py) - Path cleanup script
