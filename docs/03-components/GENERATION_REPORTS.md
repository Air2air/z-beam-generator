# Generation Reports

**Status**: ✅ Active  
**Location**: Root directory (`GENERATION_REPORT.md`)  
**Updated**: November 19, 2025

---

## Overview

Every content generation (micro, subtitle, FAQ) automatically saves a comprehensive report to `GENERATION_REPORT.md` in the project root. This file is **overwritten** on each generation, always showing the most recent generation details.

## Report Location

```
z-beam-generator/
├── GENERATION_REPORT.md  ← Default report file (gitignored)
├── run.py
└── ...
```

**Note**: `GENERATION_REPORT.md` is in `.gitignore` - it's a working file, not committed to the repository.

## Report Format

### Individual Generation

```markdown
# Generation Report

**Last Updated**: November 19, 2025 at 10:57 PM
**Material**: Tin
**Component**: subtitle

---

## 📝 Generated Content

```
[Full generated text here]
```

## 📏 Statistics

- **Length**: 106 characters
- **Word Count**: 17 words

## 💾 Storage

- **Location**: data/materials/Materials.yaml
- **Component**: subtitle
- **Material**: Tin
```

### Batch Generation

For batch operations, the report shows the **last material** processed in the batch:
- Each material overwrites the previous report
- Final state reflects the last material in the batch
- All materials are saved to `Materials.yaml`

## Usage Examples

### Individual Generation
```bash
# Generate subtitle for Aluminum
python3 run.py --subtitle "Aluminum"

# Check the report
cat GENERATION_REPORT.md
```

### Batch Generation
```bash
# Generate subtitles for multiple materials
python3 run.py --batch-subtitle "Aluminum,Steel,Copper"

# Check the report (shows last material: Copper)
cat GENERATION_REPORT.md
```

## Report Contents

### Generated Content
- Full text of the generated content
- Properly formatted with code blocks
- Shows BEFORE/AFTER for micros
- Shows all Q&As for FAQs

### Statistics
- Character count
- Word count
- Additional metrics based on component type

### Storage Information
- Always saved to: `data/materials/Materials.yaml`
- Component type (micro, subtitle, faq)
- Material name

### Quality Metrics (when available)
- Grok humanness detection score
- Realism score
- Subjective evaluation results
- Generation attempts

## Implementation

**Module**: `postprocessing/reports/generation_report_writer.py`

```python
from postprocessing.reports.generation_report_writer import GenerationReportWriter

# Create writer (uses default GENERATION_REPORT.md)
writer = GenerationReportWriter()

# Save individual report
report_path = writer.save_individual_report(
    material_name="Aluminum",
    component_type="subtitle",
    content="Generated text here",
    evaluation={'narrative_assessment': 'Quality feedback...'}
)

# Report saved to: GENERATION_REPORT.md
print(f"Report saved: {report_path}")
```

## Terminal Output + File Report

Generation produces **two outputs**:

1. **Terminal Display**: Full formatted report during generation
2. **File Report**: Persistent markdown file in root directory

Both contain the same information - terminal for immediate visibility, file for review.

## Best Practices

### Viewing Reports
```bash
# Quick view
cat GENERATION_REPORT.md

# Watch file for changes during batch operations
watch -n 2 cat GENERATION_REPORT.md
```

### Saving Important Reports
If you want to preserve a specific generation report:
```bash
# Copy with descriptive name
cp GENERATION_REPORT.md docs/archive/aluminum_subtitle_nov19.md
```

### Automation Integration
```bash
# Generate and capture report in one step
python3 run.py --subtitle "Aluminum" && cat GENERATION_REPORT.md
```

## Troubleshooting

### Report File Not Found
- Ensure you've run at least one generation
- Check you're in the project root directory
- Report is created automatically on first generation

### Old Content Still Showing
- File is overwritten on each generation
- If you see old content, generation may have failed
- Check terminal output for error messages

### Report Missing Information
- Some fields are optional (metrics, evaluation)
- Basic report always includes: content, statistics, storage
- Quality metrics appear only when validation runs

## Related Documentation

- **Generation Commands**: `docs/04-operations/GENERATION.md`
- **Batch Processing**: `docs/BATCH_GENERATION.md`
- **Quality Validation**: `docs/06-ai-systems/VALIDATION.md`

## Architecture

**Design Decision**: Single default file (overwrite) vs. timestamped files
- ✅ Simple: Always check same location
- ✅ Clean: No accumulation of old reports
- ✅ Fast: No directory management needed
- ✅ Flexible: Can copy/archive manually when needed

For historical reports, use `git commit` after important generations or manually copy the file.
