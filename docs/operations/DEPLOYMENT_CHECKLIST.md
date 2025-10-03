# Z-Beam Generator Deployment Checklist

**Version**: 2.0  
**Last Updated**: October 2, 2025  
**Status**: Ready for Batch Execution

## Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Validation](#pre-deployment-validation)
3. [Deployment Phases](#deployment-phases)
4. [Batch Regeneration](#batch-regeneration)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Rollback Procedures](#rollback-procedures)
7. [Success Criteria](#success-criteria)

---

## Overview

This checklist ensures **safe, verified deployment** of Z-Beam Generator content with **zero content loss** and **full rollback capability**.

### Deployment Strategy

**Approach**: **Incremental batch regeneration** with continuous verification

```
Phase 1: Pre-Flight Checks (30 min)
  └─> Validate system, backup data, test sample

Phase 2: Batch Regeneration (5-6 hours)
  └─> Regenerate 104/121 non-compliant materials

Phase 3: Post-Deployment Verification (1 hour)
  └─> Verify compliance, spot-check quality

Phase 4: Production Ready (ongoing)
  └─> Monitor, maintain, iterate
```

**Total Time**: ~7 hours (mostly automated)

---

## Pre-Deployment Validation

### Phase 1: Environment Check (5 min)

#### ✅ Check System Requirements

```bash
# Python version
python3 --version  # Should be 3.9+

# Required packages
pip list | grep -E "(pyyaml|requests|pytest)"

# Git status
git status  # Should be clean or committed
```

**Expected Output**:
```
Python 3.12.0
PyYAML                3.13.0
requests              2.31.0
pytest                7.4.0
```

#### ✅ Verify API Keys

```bash
# Check environment variables
env | grep -E "(DEEPSEEK|WINSTON|PERPLEXITY)_API_KEY"

# Test API connectivity
python3 -c "
from api.client_factory import ClientFactory
client = ClientFactory.create('deepseek')
print('✅ DeepSeek API: Connected')
"
```

**Expected Output**:
```
DEEPSEEK_API_KEY=sk-***
WINSTON_API_KEY=wa-***
✅ DeepSeek API: Connected
```

**If API keys missing**:
```bash
# Set up API keys
cp .env.example .env
nano .env  # Add your API keys
source .env
```

#### ✅ Validate Configuration Files

```bash
# Check required files exist
ls -la data/materials.yaml data/Categories.yaml config/pipeline_config.yaml

# Validate YAML syntax
python3 -c "
import yaml
from pathlib import Path

files = [
    'data/materials.yaml',
    'data/Categories.yaml',
    'config/pipeline_config.yaml'
]

for file in files:
    with open(file) as f:
        yaml.safe_load(f)
    print(f'✅ {file}: Valid YAML')
"
```

**Expected Output**:
```
-rw-r--r--  data/materials.yaml
-rw-r--r--  data/Categories.yaml
-rw-r--r--  config/pipeline_config.yaml

✅ data/materials.yaml: Valid YAML
✅ data/Categories.yaml: Valid YAML
✅ config/pipeline_config.yaml: Valid YAML
```

---

### Phase 2: Data Validation (10 min)

#### ✅ Verify Materials Data

```bash
# Load and validate materials
python3 -c "
from data.materials import load_materials

materials = load_materials()
print(f'✅ Loaded {len(materials)} materials')

# Check flat structure
if 'Aluminum' in materials:
    print('✅ Flat structure: Direct material access')
    print(f'   Category: {materials[\"Aluminum\"][\"category\"]}')
else:
    print('❌ Materials not in flat structure')
"
```

**Expected Output**:
```
✅ Loaded 121 materials
✅ Flat structure: Direct material access
   Category: metal
```

#### ✅ Check Existing Content Status

```bash
# Run compliance verification
python3 scripts/tools/verify_frontmatter_compliance.py | head -20
```

**Expected Output**:
```
Frontmatter Compliance Report
Generated: 2025-10-02 14:30:00

Total materials: 121
✅ Compliant: 17 (14.0%)
❌ Non-compliant: 104 (86.0%)

Top Issues:
  [84] Caption uses snake_case (should be camelCase)
  [69] Missing required field: tags
  [30] Insufficient applications (< 2)
```

**Interpretation**:
- 17 materials already compliant (recent generations)
- 104 materials need regeneration
- Clear issues identified

---

### Phase 3: Backup Current State (5 min)

#### ✅ Create Backup

```bash
# Create timestamped backup
BACKUP_DIR="backups/deployment_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup materials and content
cp data/materials.yaml "$BACKUP_DIR/"
cp -r content/components/frontmatter "$BACKUP_DIR/"

# Verify backup
ls -la "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"
```

**Expected Output**:
```
drwxr-xr-x  backups/deployment_20251002_143000/
-rw-r--r--  backups/deployment_20251002_143000/materials.yaml
drwxr-xr-x  backups/deployment_20251002_143000/frontmatter/

✅ Backup created: backups/deployment_20251002_143000
```

#### ✅ Verify Backup Integrity

```bash
# Check backup size
du -sh "$BACKUP_DIR"

# Verify YAML validity
python3 -c "
import yaml
backup_file = '$BACKUP_DIR/materials.yaml'
with open(backup_file) as f:
    yaml.safe_load(f)
print('✅ Backup YAML valid')
"
```

---

### Phase 4: Test Sample Generation (10 min)

#### ✅ Generate Test Material

```bash
# Generate a single test material
timeout 300 python3 run.py --material "Zinc" --components frontmatter 2>&1 | tail -20
```

**Expected Output**:
```
🎯 Generating frontmatter for: Zinc
📝 Loading material data...
✅ Material loaded: Zinc (metal)

🔄 Generating applications...
✅ Generated 8 applications

🔄 Generating caption...
✅ Generated caption (camelCase)

🔄 Generating tags...
✅ Generated 10 tags

✅ Frontmatter generated successfully
📁 Saved: content/components/frontmatter/zinc-laser-cleaning.yaml
⏱️ Time taken: 3m 5s
```

#### ✅ Validate Test Output

```bash
# Check test file compliance
python3 -c "
import yaml

with open('content/components/frontmatter/zinc-laser-cleaning.yaml') as f:
    zinc = yaml.safe_load(f)

# Check applications
apps = zinc.get('applications', [])
print(f'Applications: {len(apps)} items')
print(f'  Format: {\"string\" if all(isinstance(a, str) for a in apps) else \"object\"}')

# Check caption
caption = zinc.get('images', {}).get('caption', {})
has_camel = 'beforeText' in caption and 'afterText' in caption
print(f'Caption: {\"camelCase\" if has_camel else \"snake_case\"}')

# Check tags
tags = zinc.get('tags', [])
print(f'Tags: {len(tags)} items')

if len(apps) >= 2 and has_camel and 4 <= len(tags) <= 10:
    print('✅ Test material: COMPLIANT')
else:
    print('❌ Test material: NON-COMPLIANT')
"
```

**Expected Output**:
```
Applications: 8 items
  Format: string
Caption: camelCase
Tags: 10 items
✅ Test material: COMPLIANT
```

---

## Deployment Phases

### Phase 1: Dry-Run Validation (5 min)

**Purpose**: Verify what will be processed without making changes

```bash
# Run in dry-run mode
python3 scripts/tools/batch_regenerate_frontmatter.py --dry-run 2>&1 | head -50
```

**Expected Output**:
```
🔍 DRY-RUN MODE - No files will be modified

Scanning materials...
✅ Found 121 materials

Checking compliance...
  Aluminum: ⚠️ needs regen (snake_case caption)
  Copper: ⚠️ needs regen (missing tags)
  Zinc: ✅ up-to-date
  ... (118 more)

Summary:
  Total materials: 121
  Up-to-date: 17
  Need regeneration: 104

Would process 104 materials
Estimated time: 5h 12m (3 min per material)

✅ DRY-RUN COMPLETE - No files were modified
```

**Decision Point**: 
- ✅ If 104 materials need regen → Proceed to Phase 2
- ❌ If unexpected count → Investigate before proceeding

---

### Phase 2: Batch Regeneration (5-6 hours)

**Purpose**: Regenerate all non-compliant materials

#### Option A: Foreground with Progress (Recommended for First Time)

```bash
# Run with progress output
python3 scripts/tools/batch_regenerate_frontmatter.py --resume
```

**Expected Output**:
```
🚀 Starting batch regeneration...

[1/104] Processing: Aluminum
  ✅ Generated in 3m 5s

[2/104] Processing: Copper
  ✅ Generated in 2m 58s

[3/104] Processing: Granite
  ✅ Generated in 3m 12s
  ETA: 5h 8m remaining

... (continues)

[104/104] Processing: Willow
  ✅ Generated in 3m 1s

✅ Batch regeneration complete!
   Processed: 104 materials
   Successful: 102
   Failed: 2
   Time taken: 5h 18m
```

#### Option B: Background with Logging (Recommended for Unattended)

```bash
# Run in background with nohup
nohup python3 scripts/tools/batch_regenerate_frontmatter.py --resume \
  > "logs/batch_$(date +%Y%m%d_%H%M%S).log" 2>&1 &

# Get process ID
BATCH_PID=$!
echo "Batch regeneration started: PID $BATCH_PID"

# Monitor progress
tail -f logs/batch_*.log
```

**Monitoring Commands**:
```bash
# Check if process is still running
ps aux | grep batch_regenerate

# View recent progress
tail -20 logs/batch_*.log

# Check success rate
grep -E "(✅|❌)" logs/batch_*.log | tail -10
```

#### Resume After Interruption

If batch is interrupted (Ctrl+C, system restart, etc.):

```bash
# Simply re-run with --resume flag
python3 scripts/tools/batch_regenerate_frontmatter.py --resume
```

**Resume Output**:
```
🔄 Resuming batch regeneration...

Checking existing files...
  Aluminum: ✅ already compliant (skipping)
  Copper: ✅ already compliant (skipping)
  Granite: ⚠️ needs regen

[45/104] Processing: Granite
  ✅ Generated in 3m 2s
  ETA: 2h 57m remaining

... (continues from where it left off)
```

---

### Phase 3: Error Handling

#### Monitor for Errors

```bash
# Check error log
grep "ERROR" logs/batch_*.log

# List failed materials
grep "❌" logs/batch_*.log | awk '{print $3}'
```

#### Retry Failed Materials

```bash
# Retry specific material
python3 run.py --material "FailedMaterial" --components frontmatter

# Or retry all failed materials
grep "❌" logs/batch_*.log | awk '{print $3}' | while read material; do
  echo "Retrying: $material"
  python3 run.py --material "$material" --components frontmatter
done
```

---

## Post-Deployment Verification

### Phase 1: Compliance Verification (10 min)

#### ✅ Run Full Compliance Check

```bash
# Check all 121 materials
python3 scripts/tools/verify_frontmatter_compliance.py --details > compliance_report.txt

# View summary
head -30 compliance_report.txt
```

**Expected Output (Success)**:
```
Frontmatter Compliance Report
Generated: 2025-10-02 20:30:00

Total materials: 121
✅ Compliant: 121 (100.0%)
❌ Non-compliant: 0 (0.0%)

No issues detected - all materials compliant!
```

**Expected Output (Partial Success)**:
```
Total materials: 121
✅ Compliant: 119 (98.3%)
❌ Non-compliant: 2 (1.7%)

Remaining Issues:
  [2] Generation timeout (materials: Granite, Marble)
```

**Decision Point**:
- ✅ If 100% compliant → Proceed to Phase 2
- ⚠️ If 95-99% compliant → Retry failed materials, then proceed
- ❌ If <95% compliant → Investigate root cause before proceeding

---

### Phase 2: Quality Spot Check (20 min)

#### ✅ Sample 10 Random Materials

```bash
# Select random sample
python3 -c "
import random
from pathlib import Path

files = list(Path('content/components/frontmatter').glob('*-laser-cleaning.yaml'))
sample = random.sample(files, 10)

print('Random sample for spot check:')
for f in sample:
    material = f.stem.replace('-laser-cleaning', '').title()
    print(f'  - {material}')
" > spot_check_sample.txt

cat spot_check_sample.txt
```

#### ✅ Manual Quality Review

For each sampled material, verify:

**Checklist per Material**:
```
□ Applications: 2-15 items, simple string format
□ Caption: CamelCase keys (beforeText, afterText)
□ Tags: 4-10 items, includes category + industries
□ Properties: Complete and accurate
□ Machine Settings: Reasonable values
□ Overall: Reads naturally, no obvious errors
```

**Review Script**:
```bash
# Review a specific material
MATERIAL="Aluminum"
cat "content/components/frontmatter/${MATERIAL,,}-laser-cleaning.yaml" | less

# Check applications format
sed -n '/^applications:/,/^machineSettings:/p' \
  "content/components/frontmatter/${MATERIAL,,}-laser-cleaning.yaml" | head -20

# Check caption format
sed -n '/^  caption:/,/^  mainImage:/p' \
  "content/components/frontmatter/${MATERIAL,,}-laser-cleaning.yaml"

# Check tags
grep -A 15 "^tags:" "content/components/frontmatter/${MATERIAL,,}-laser-cleaning.yaml"
```

---

### Phase 3: Automated Validation (10 min)

#### ✅ Run Automated Tests

```bash
# Run validation tests
pytest tests/test_frontmatter_validation.py -v

# Run integration tests
pytest tests/integration/test_generation_pipeline.py -v
```

**Expected Output**:
```
tests/test_frontmatter_validation.py::test_applications_format PASSED
tests/test_frontmatter_validation.py::test_caption_camelcase PASSED
tests/test_frontmatter_validation.py::test_tags_present PASSED
tests/test_frontmatter_validation.py::test_required_fields PASSED

tests/integration/test_generation_pipeline.py::test_full_generation PASSED

===================== 5 passed in 12.34s ======================
```

#### ✅ Validate Pipeline Integration

```bash
# Test pipeline validation
python3 -c "
from pipeline_integration import validate_and_improve_frontmatter
import yaml
from pathlib import Path

# Test 5 random materials
import random
files = list(Path('content/components/frontmatter').glob('*-laser-cleaning.yaml'))
sample = random.sample(files, 5)

for file in sample:
    material = file.stem.replace('-laser-cleaning', '').title()
    with open(file) as f:
        data = yaml.safe_load(f)
    
    result = validate_and_improve_frontmatter(material, data)
    
    status = '✅' if result['validation_passed'] else '❌'
    print(f'{status} {material}: {len(result[\"issues_detected\"])} issues')

print('\\n✅ Pipeline validation complete')
"
```

---

### Phase 4: Performance Validation (10 min)

#### ✅ Measure Generation Performance

```bash
# Test single generation time
time python3 run.py --material "TestMaterial" --components frontmatter 2>&1 | tail -5
```

**Expected Output**:
```
✅ Frontmatter generated successfully
⏱️ Time taken: 3m 5s

real    3m5.957s
user    0m2.345s
sys     0m0.567s
```

**Performance Criteria**:
- ✅ Single material: 2-4 minutes
- ⚠️ Single material: 4-6 minutes (acceptable, monitor API performance)
- ❌ Single material: >6 minutes (investigate API issues)

---

## Rollback Procedures

### Scenario 1: Partial Batch Failure

**Situation**: Batch regeneration failed after processing 50/104 materials

**Rollback Steps**:
```bash
# 1. Stop batch process
pkill -f batch_regenerate_frontmatter

# 2. Identify successfully regenerated materials
grep "✅" logs/batch_*.log | awk '{print $3}' > regenerated.txt

# 3. Option A: Keep successful, fix failed
#    (Recommended - don't lose successful work)
python3 scripts/tools/batch_regenerate_frontmatter.py --resume

# 3. Option B: Restore all from backup
#    (Only if successful regenerations are problematic)
BACKUP_DIR="backups/deployment_20251002_143000"
cp -r "$BACKUP_DIR/frontmatter/"* content/components/frontmatter/

# 4. Verify restoration
python3 scripts/tools/verify_frontmatter_compliance.py
```

---

### Scenario 2: Quality Issues Detected

**Situation**: Post-deployment verification reveals quality problems

**Rollback Steps**:
```bash
# 1. Identify problematic materials
python3 scripts/tools/verify_frontmatter_compliance.py --details | \
  grep "❌" > problematic.txt

# 2. Restore specific materials from backup
BACKUP_DIR="backups/deployment_20251002_143000"

while read material; do
  file="${material,,}-laser-cleaning.yaml"
  if [ -f "$BACKUP_DIR/frontmatter/$file" ]; then
    cp "$BACKUP_DIR/frontmatter/$file" content/components/frontmatter/
    echo "✅ Restored: $material"
  fi
done < problematic.txt

# 3. Verify restoration
python3 scripts/tools/verify_frontmatter_compliance.py
```

---

### Scenario 3: Complete Rollback

**Situation**: Deployment needs to be completely rolled back

**Rollback Steps**:
```bash
# 1. Stop any running processes
pkill -f batch_regenerate
pkill -f "python3 run.py"

# 2. Restore materials.yaml (if modified)
BACKUP_DIR="backups/deployment_20251002_143000"
cp "$BACKUP_DIR/materials.yaml" data/materials.yaml

# 3. Restore all frontmatter files
rm -rf content/components/frontmatter/
cp -r "$BACKUP_DIR/frontmatter/" content/components/frontmatter/

# 4. Verify restoration
ls content/components/frontmatter/*.yaml | wc -l  # Should match backup count

# 5. Validate restored data
python3 -c "
from data.materials import load_materials
materials = load_materials()
print(f'✅ Materials loaded: {len(materials)}')
"

python3 scripts/tools/verify_frontmatter_compliance.py | head -10
```

---

## Success Criteria

### Critical Success Factors

#### ✅ Compliance: 100%

```bash
# All 121 materials must be compliant
python3 scripts/tools/verify_frontmatter_compliance.py | grep "Compliant:"
```

**Target**: `✅ Compliant: 121 (100.0%)`

#### ✅ Format: Correct

**Applications**: Simple strings with colon
```yaml
applications:
  - 'Industry: Description'
```

**Caption**: CamelCase keys
```yaml
caption:
  beforeText: '...'
  afterText: '...'
```

**Tags**: 4-10 items
```yaml
tags:
  - metal
  - aerospace
  # ... 8 more
```

#### ✅ Quality: High

**Spot check 10 random materials**:
- All fields present
- Natural language
- No obvious errors
- Consistent formatting

#### ✅ Performance: Acceptable

**Generation time**: 2-4 minutes per material  
**Batch completion**: 5-6 hours for 104 materials

---

### Deployment Status Dashboard

```bash
# Run this command to get deployment status
python3 -c "
from pathlib import Path
import yaml

# Count total materials
materials_file = Path('data/materials.yaml')
with open(materials_file) as f:
    materials = yaml.safe_load(f)['materials']
total = len(materials)

# Count frontmatter files
frontmatter_files = list(Path('content/components/frontmatter').glob('*-laser-cleaning.yaml'))
generated = len(frontmatter_files)

# Calculate percentages
completion = (generated / total * 100) if total > 0 else 0

print('Deployment Status Dashboard')
print('=' * 40)
print(f'Total materials: {total}')
print(f'Generated files: {generated}')
print(f'Completion: {completion:.1f}%')
print()

# Compliance check (simplified)
# Would normally run verify_frontmatter_compliance.py
print('Run for detailed compliance:')
print('python3 scripts/tools/verify_frontmatter_compliance.py')
"
```

---

## Summary

### Deployment Checklist Summary

**Pre-Deployment** (30 min):
- ✅ System requirements met
- ✅ API keys configured
- ✅ Configuration files valid
- ✅ Data structure verified
- ✅ Backup created
- ✅ Test generation successful

**Deployment** (5-6 hours):
- ✅ Dry-run validated
- ✅ Batch regeneration executed
- ✅ Errors handled
- ✅ Resume capability verified

**Post-Deployment** (1 hour):
- ✅ Compliance: 100% (121/121)
- ✅ Quality spot check passed
- ✅ Automated tests passed
- ✅ Performance acceptable

**Success**: System is production-ready ✨

---

## Next Steps

### After Successful Deployment

1. **Monitor Performance**
   ```bash
   # Weekly compliance check
   python3 scripts/tools/verify_frontmatter_compliance.py
   ```

2. **Maintain Quality**
   ```bash
   # Re-generate if issues found
   python3 run.py --material "MaterialName" --components frontmatter
   ```

3. **Archive Backups**
   ```bash
   # After confirming stability (1 week)
   tar -czf deployment_backup_$(date +%Y%m%d).tar.gz backups/
   ```

4. **Update Documentation**
   - Note any issues encountered
   - Document lessons learned
   - Update procedures if needed

---

**See Also**:
- `docs/SYSTEM_READINESS_ASSESSMENT.md` - Current system status
- `docs/operations/VALIDATION.md` - Validation rules and procedures
- `docs/operations/BATCH_OPERATIONS.md` - Batch processing guide
- `scripts/tools/batch_regenerate_frontmatter.py` - Batch regeneration script
- `scripts/tools/verify_frontmatter_compliance.py` - Compliance verification script
