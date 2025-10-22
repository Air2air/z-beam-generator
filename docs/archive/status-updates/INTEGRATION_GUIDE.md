# Validation System Integration Guide

**Quick Reference for Adding Data Validation to Your Workflow**

---

## 🚀 5-Minute Setup

### Option 1: GitHub Actions (Recommended for Teams)

Already done! ✅ The workflow is in `.github/workflows/data-validation.yml`

**What it does:**
- Validates every push and PR automatically
- Posts results as PR comments
- Blocks merges if critical errors found
- Uploads detailed reports

**Test it:**
```bash
git add .
git commit -m "Test validation workflow"
git push
# Check the Actions tab on GitHub
```

### Option 2: Pre-commit Hook (Recommended for Individuals)

```bash
make install-hooks
```

**What it does:**
- Runs validation before every commit
- Blocks bad commits automatically
- Takes ~2 seconds

**Test it:**
```bash
# Make a change to a YAML file
echo "test: value" >> content/components/frontmatter/aluminum-laser-cleaning.yaml
git add content/components/frontmatter/aluminum-laser-cleaning.yaml
git commit -m "Test pre-commit hook"
# Validation will run automatically
```

### Option 3: Manual Commands (Flexible)

```bash
make validate          # Quick validation
make validate-report   # Generate HTML report
make fix-units         # Auto-fix unit issues
```

---

## 📊 Integration Comparison

| Method | When It Runs | Blocks Bad Changes | Best For |
|--------|--------------|-------------------|----------|
| **GitHub Actions** | Push/PR | ✅ Blocks merge | Teams, CI/CD |
| **Pre-commit Hook** | Before commit | ✅ Blocks commit | Individual devs |
| **Make Commands** | Manual | ❌ Advisory only | Development, debugging |
| **Direct Python** | Manual | ❌ Advisory only | Scripts, automation |

---

## 🔧 Detailed Integration Options

### 1. GitHub Actions (CI/CD Pipeline)

**File**: `.github/workflows/data-validation.yml`

**Features:**
```yaml
✅ Runs on: push, pull_request, manual trigger
✅ Validates: All YAML data files
✅ Outputs: JSON report + PR comment
✅ Artifacts: 30-day report retention
✅ Blocking: Prevents merge if errors found
```

**Configuration:**
```yaml
# Customize trigger paths
paths:
  - 'content/components/frontmatter/**/*.yaml'
  - 'data/Categories.yaml'
  - 'data/Materials.yaml'

# Adjust failure behavior
continue-on-error: false  # Block on errors
```

**View Results:**
1. Go to GitHub → Actions tab
2. Click on workflow run
3. Check "validate-data-quality" job
4. Download validation report artifact

---

### 2. Pre-commit Hook (Local Development)

**Installation:**
```bash
make install-hooks
```

**Manual installation:**
```bash
chmod +x scripts/validation/validate_pre_commit.py
ln -s ../../scripts/validation/validate_pre_commit.py .git/hooks/pre-commit
```

**Behavior:**
- 🔴 **Critical errors** → Blocks commit + shows errors
- 🟡 **Warnings only** → Allows commit + shows warnings
- ✅ **No issues** → Silent pass

**Bypass (emergency only):**
```bash
git commit --no-verify -m "Bypass validation"
```

**Uninstall:**
```bash
rm .git/hooks/pre-commit
```

---

### 3. Makefile Commands

**Available commands:**
```bash
make help              # Show all commands
make validate          # Quick validation
make validate-strict   # Fail on any errors
make validate-report   # Generate HTML report
make fix-units         # Auto-fix unit issues
make fix-values        # Auto-fix qualitative issues
make install-hooks     # Install pre-commit hook
make test              # Run all tests + validation
make clean             # Remove generated files
```

**Add to your workflow:**
```bash
# Before committing
make validate

# Fix common issues automatically
make fix-units
make fix-values

# Generate report for review
make validate-report
open validation_report.html
```

---

### 4. Python API (Custom Integration)

**Basic usage:**
```python
from scripts.validation.comprehensive_validation_agent import DataQualityValidationAgent

# Create agent
agent = DataQualityValidationAgent()

# Run validation
issues = agent.validate_all(verbose=True)

# Check results
if issues['ERROR']:
    print(f"Found {len(issues['ERROR'])} critical errors!")
    # Handle errors...

# Generate report
agent.generate_report(issues, output_file='my_report.json')
```

**Custom validation:**
```python
# Validate specific material
material_data = agent.load_material(Path('content/components/frontmatter/aluminum-laser-cleaning.yaml'))
category = material_data.get('category')

# Run property-level validation
for prop_name, prop_data in material_data['materialProperties']['laser_material_interaction']['properties'].items():
    issues = agent.validate_property_value('aluminum', category, prop_name, prop_data)
    if issues:
        print(f"Issues in {prop_name}:", issues)
```

---

### 5. Shell Script Integration

**Create wrapper script:**
```bash
#!/bin/bash
# validate_and_deploy.sh

echo "Running data validation..."
if python3 scripts/validation/comprehensive_validation_agent.py; then
    echo "✅ Validation passed. Proceeding with deployment..."
    # Your deployment commands here
    make deploy
else
    echo "❌ Validation failed. Deployment aborted."
    exit 1
fi
```

---

## 📈 Monitoring & Reporting

### View Validation Results

**JSON Report:**
```bash
cat validation_report.json | jq '.ERROR | length'  # Count errors
cat validation_report.json | jq '.ERROR[0]'        # View first error
```

**HTML Report:**
```bash
make validate-report
open validation_report.html  # macOS
# or: xdg-open validation_report.html  # Linux
# or: start validation_report.html     # Windows
```

### Track Validation History

**Save reports with timestamps:**
```bash
# In your CI/CD or cron job
python3 scripts/validation/comprehensive_validation_agent.py
cp validation_report.json "reports/validation_$(date +%Y%m%d_%H%M%S).json"
```

**Analyze trends:**
```python
import json
import glob

reports = glob.glob('reports/validation_*.json')
for report_file in sorted(reports):
    with open(report_file) as f:
        data = json.load(f)
    errors = len(data['ERROR'])
    print(f"{report_file}: {errors} errors")
```

---

## 🔄 Automated Fixes

### Run Automated Corrections

```bash
# Fix all known issues automatically
make fix-units      # Standardize units (108 fixes)
make fix-values     # Convert qualitative values (6 fixes)

# Verify fixes
make validate

# Review what changed
git diff content/components/frontmatter/
```

### Custom Fix Scripts

Create your own fix scripts following the pattern:

```python
#!/usr/bin/env python3
from pathlib import Path
import yaml
import shutil
from datetime import datetime

# Create backup
backup_dir = Path(f"backups/my_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copytree('content/components/frontmatter', backup_dir)

# Apply fixes
for file in Path('content/components/frontmatter').glob('*.yaml'):
    with open(file) as f:
        data = yaml.safe_load(f)
    
    # Your fix logic here
    # ...
    
    with open(file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

---

## 🎯 Best Practices

### Development Workflow

```bash
# 1. Install pre-commit hook (once)
make install-hooks

# 2. Make changes to YAML files
vim content/components/frontmatter/aluminum-laser-cleaning.yaml

# 3. Validate before committing
make validate

# 4. Auto-fix if possible
make fix-units
make fix-values

# 5. Commit (hook runs automatically)
git add .
git commit -m "Update aluminum properties"

# 6. Push (GitHub Actions validates)
git push
```

### Team Workflow

```bash
# 1. Create feature branch
git checkout -b feature/update-materials

# 2. Make changes and validate locally
make validate-strict

# 3. Create PR (triggers validation)
git push origin feature/update-materials

# 4. Review validation results in PR comment
# 5. Fix any errors highlighted
# 6. Merge when validation passes
```

### Production Deployment

```bash
# Add to deployment script
#!/bin/bash
set -e  # Exit on error

echo "Validating data quality..."
python3 scripts/validation/comprehensive_validation_agent.py

echo "Running tests..."
pytest tests/ -v

echo "Deploying..."
# Your deployment commands
```

---

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**Pre-commit hook not running:**
```bash
# Check if hook exists
ls -la .git/hooks/pre-commit

# Reinstall
make install-hooks

# Verify it's executable
chmod +x .git/hooks/pre-commit
```

**Validation takes too long:**
```bash
# Validate only changed files (future enhancement)
# For now, validation is fast (~2 seconds)
```

**False positives:**
```bash
# Review the validation rules
vim scripts/validation/comprehensive_validation_agent.py

# Adjust category-specific thresholds
# Document exceptions in material files
```

---

## 📚 Additional Resources

- **Full Documentation**: `FINAL_VALIDATION_REPORT.md`
- **System Overview**: `VALIDATION_DEPLOYMENT_COMPLETE.md`
- **Technical Details**: `DATA_QUALITY_VALIDATION_REPORT.md`
- **Quick Reference**: `VALIDATION_SYSTEM_COMPLETE.md`
- **Validation README**: `scripts/validation/README.md`

---

## 🎉 Summary

**Choose your integration:**

| Your Situation | Best Option | Command |
|----------------|-------------|---------|
| Working solo | Pre-commit hook | `make install-hooks` |
| Team project | GitHub Actions | Already set up! |
| Manual workflow | Make commands | `make validate` |
| Custom automation | Python API | Import and use |

**All options work together** - you can use multiple at once!

---

**Status**: ✅ Ready to integrate  
**Time to setup**: 5 minutes  
**Maintenance**: Minimal  
**Value**: High (prevents data quality issues)
