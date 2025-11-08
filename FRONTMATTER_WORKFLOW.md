# Frontmatter Workflow Commands

## Quick Reference

### Generate Frontmatter from Materials.yaml
```bash
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter

exporter = TrivialFrontmatterExporter()
results = exporter.export_all()
print(f'✅ Generated {sum(1 for v in results.values() if v)}/{len(results)} frontmatter files')
"
```

### Deploy Frontmatter to Production
```bash
python3 run.py --deploy
```

## Complete Workflow

**When you update Materials.yaml:**

1. **Generate frontmatter files** (converts Materials.yaml → frontmatter/*.yaml)
   ```bash
   python3 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter; exporter = TrivialFrontmatterExporter(); results = exporter.export_all(); print(f'✅ Generated {sum(1 for v in results.values() if v)}/{len(results)} files')"
   ```

2. **Deploy to Next.js production** (copies frontmatter/ → z-beam/frontmatter/)
   ```bash
   python3 run.py --deploy
   ```

## What Each Step Does

### Step 1: Generate Frontmatter
- **Reads:** `materials/data/Materials.yaml`
- **Writes:** `frontmatter/materials/*.yaml` (132 files)
- **Applies:** 
  - HTML formatting to FAQs (adds `<strong>` tags)
  - Breadcrumb navigation
  - Author enrichment from registry
  - Property ranges from Categories.yaml
  - Schema normalization

### Step 2: Deploy
- **Reads:** `frontmatter/` directory
- **Writes:** `../z-beam/frontmatter/` (Next.js production)
- **Copies:** All frontmatter files to production site

## Common Scenarios

### After FAQ Enhancement
```bash
# 1. FAQs are already in Materials.yaml with topic_keyword/topic_statement
# 2. Generate frontmatter with HTML formatting:
python3 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter; TrivialFrontmatterExporter().export_all()"

# 3. Deploy to production:
python3 run.py --deploy
```

### After Breadcrumb Changes
```bash
# Same workflow - generate then deploy
python3 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter; TrivialFrontmatterExporter().export_all()"
python3 run.py --deploy
```

### Quick One-Liner (Generate + Deploy)
```bash
python3 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter; TrivialFrontmatterExporter().export_all()" && python3 run.py --deploy
```

## Important Notes

⚠️ **Always generate before deploying** - The `--deploy` command only COPIES files, it doesn't regenerate them.

✅ **Generation is idempotent** - Safe to run multiple times, overwrites existing files.

🔍 **Verify after generation** - Check `frontmatter/materials/` to confirm changes before deploying.

📊 **File count** - Should generate 139 files total (132 materials + thesaurus + applications + regions + contaminants)
