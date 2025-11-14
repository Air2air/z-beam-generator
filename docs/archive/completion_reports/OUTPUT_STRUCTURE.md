# Output Structure Summary

## Content-Type Source Folders (Root Level)

Each content type has its own folder at the root level containing:
- `generator.py` - Type-specific generator
- `data.yaml` - Source data
- `README.md` - Documentation

```
/materials/        # 132 materials
/regions/          # 6 regions
/applications/     # 12 applications
/contaminants/     # 8 contaminants
/thesaurus/        # 15 technical terms
```

## Generated Output (Centralized)

All generated frontmatter files go to `/frontmatter/{type}/`:

```
/frontmatter/
  ├── materials/       # 132 material frontmatter files
  ├── regions/         # Region frontmatter files
  ├── applications/    # Application frontmatter files
  ├── contaminants/    # Contaminant frontmatter files
  └── thesaurus/       # Term definition frontmatter files
```

## Why This Structure?

**✅ Clear Separation**: Source (root folders) vs Output (frontmatter folder)
**✅ Easy Discovery**: Find generator and data together in one place
**✅ Centralized Output**: All generated files in known location
**✅ Version Control**: Can .gitignore `/frontmatter/*` if generated content shouldn't be tracked

## Usage Examples

```bash
# Generate region frontmatter
python3 run.py --content-type region --identifier "north_america"
# Output: frontmatter/regions/north-america-laser-cleaning.yaml

# Generate application frontmatter  
python3 run.py --content-type application --identifier "automotive_manufacturing"
# Output: frontmatter/applications/automotive-manufacturing-laser-cleaning.yaml

# Generate material frontmatter
python3 run.py --material "Aluminum"
# Output: frontmatter/materials/aluminum-laser-cleaning.yaml
```

## Current File Counts

- `frontmatter/materials/`: 132 files
- `frontmatter/regions/`: 2 files (generated)
- `frontmatter/applications/`: 2 files (generated)
- `frontmatter/contaminants/`: 1 file (generated)
- `frontmatter/thesaurus/`: 1 file (generated)
