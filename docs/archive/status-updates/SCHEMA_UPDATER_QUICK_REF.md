# Schema Updater - Quick Reference Card

## 🚀 Common Commands

```bash
# Validate schemas match data
python3 scripts/tools/schema_updater.py --validate-only

# Update all schemas
python3 scripts/tools/schema_updater.py --update all

# Preview changes (dry run)
python3 scripts/tools/schema_updater.py --update all --dry-run

# Update specific schema
python3 scripts/tools/schema_updater.py --update frontmatter
python3 scripts/tools/schema_updater.py --update categories
python3 scripts/tools/schema_updater.py --update materials

# Verbose output
python3 scripts/tools/schema_updater.py --update all --verbose
```

## 📋 When to Use

| Scenario | Command |
|----------|---------|
| **After editing Categories.yaml** | `--update all` |
| **After editing Materials.yaml** | `--update all` |
| **After updating PROPERTY_RULES** | `--update all` |
| **Before committing data changes** | `--validate-only` |
| **To preview changes** | `--update all --dry-run` |
| **CI/CD validation** | `--validate-only` |

## 🎯 What Gets Updated

| Schema | Source | Updates |
|--------|--------|---------|
| `frontmatter.json` | Categories.yaml | Category enum |
| `frontmatter.json` | Materials.yaml | Subcategory enum |
| `frontmatter.json` | Categories.yaml | Property categories |
| `categories_schema.json` | PROPERTY_RULES | Property count |
| `materials_schema.json` | Materials.yaml | Material/category counts |

## ⚡ Quick Workflow

```bash
# 1. Edit data
vim data/Categories.yaml

# 2. Validate
python3 scripts/tools/schema_updater.py --validate-only

# 3. Update if needed
python3 scripts/tools/schema_updater.py --update all

# 4. Commit together
git add data/*.yaml schemas/*.json
git commit -m "feat: update data and schemas"
```

## 📖 Documentation

- **Full Guide**: `docs/AUTOMATED_SCHEMA_UPDATES.md`
- **Tool Code**: `scripts/tools/schema_updater.py`
- **Summary**: `AUTOMATED_SCHEMA_SYSTEM_SUMMARY.md`
