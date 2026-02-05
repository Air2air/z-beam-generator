# Analysis Scripts

Utilities for analyzing generated content, frontmatter structure, and data quality.

## Files

### analyze_descriptions.py
Analyzes quality and characteristics of generated description fields.
- Input: Materials.yaml or similar data files
- Output: Statistical analysis of description content

### analyze_frontmatter_sections.py
Examines frontmatter section metadata structure and completeness.
- Input: Frontmatter YAML files (../../../frontmatter/)
- Output: Section metadata validation report

### analyze_section_similarity.py
Compares sections across different items to identify duplicates or inconsistencies.
- Input: Multiple frontmatter files
- Output: Similarity matrix and duplicate detection

## Usage

```bash
# From repository root
python scripts/analysis/analyze_descriptions.py
python scripts/analysis/analyze_frontmatter_sections.py
python scripts/analysis/analyze_section_similarity.py
```

## Dependencies
- PyYAML for YAML parsing
- Standard library modules (os, sys, pathlib)
