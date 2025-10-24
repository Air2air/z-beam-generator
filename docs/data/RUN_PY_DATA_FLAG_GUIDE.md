# Using `python3 run.py --data` for Systematic Data Verification

## Overview

The `--data` flag in `run.py` provides a convenient way to run systematic data verification directly from the main application entry point.

## Quick Usage

### Test Mode (Safe, Recommended First)
```bash
python3 run.py --data=test
```
- **Time:** 15 minutes
- **Cost:** ~$0.10
- **Mode:** Dry run (no changes to Materials.yaml)
- **Materials:** Limited to 10 for testing
- **Properties:** 5 critical properties

### Verify Critical Properties
```bash
python3 run.py --data=critical
```
- **Time:** 3 hours
- **Cost:** $1.20
- **Properties:** 5 critical (density, meltingPoint, thermalConductivity, hardness, absorptionCoefficient)
- **Materials:** All 122
- **Values:** 610 verified

### Verify Everything (Production)
```bash
python3 run.py --data
# or
python3 run.py --data=all
```
- **Time:** 18 hours
- **Cost:** $14.64
- **Properties:** All ~60 properties
- **Materials:** All 122
- **Values:** 7,320 verified

### Verify Important Properties
```bash
python3 run.py --data=important
```
- **Time:** 3 hours
- **Cost:** $1.20
- **Properties:** 5 important (youngsModulus, thermalExpansion, specificHeat, reflectivity, ablationThreshold)

### Verify Specific Property Groups
```bash
python3 run.py --data=--group=mechanical
python3 run.py --data=--group=optical
python3 run.py --data=--group=thermal
```

### Verify Specific Properties
```bash
python3 run.py --data=--properties=density,meltingPoint,thermalConductivity
```

## Command Reference

| Command | Properties | Time | Cost | Mode |
|---------|-----------|------|------|------|
| `--data=test` | 5 critical | 15 min | $0.10 | Dry run, 10 materials |
| `--data=critical` | 5 critical | 3 hrs | $1.20 | Live, all materials |
| `--data=important` | 5 important | 3 hrs | $1.20 | Live, all materials |
| `--data=all` or `--data` | ~60 all | 18 hrs | $14.64 | Live, all materials |
| `--data=--group=mechanical` | 4 mechanical | 2 hrs | $0.96 | Live, all materials |
| `--data=--group=optical` | 4 optical | 2 hrs | $0.96 | Live, all materials |
| `--data=--group=thermal` | 3 thermal | 1.5 hrs | $0.72 | Live, all materials |
| `--data=--properties=X,Y` | Custom | Varies | Varies | Live, all materials |

## What Happens

### Step-by-Step Process

1. **Extract** - Each property is extracted from Materials.yaml into a focused research file
2. **AI Verify** - DeepSeek validates every value against authoritative scientific sources
3. **Review** - Interactive review of flagged values with variance analysis
4. **Merge** - Verified data is merged back to Materials.yaml with audit trails
5. **Report** - Comprehensive report generated with accuracy statistics

### Example Output

```
🔬 SYSTEMATIC DATA VERIFICATION
================================================================================

📋 Mode: Verify critical properties (3 hours, $1.20)
================================================================================

🔍 [1/5] Processing: density
================================================================================

📤 Step 1/4: Extracting density from Materials.yaml...
   ✅ Extracted to: density_research.yaml

🤖 Step 2/4: AI verification with DeepSeek...
   ✅ Verified: 97 materials (0-0.5% variance)
   ⚠️  Needs review: 4 materials (0.5-5% variance)
   🚨 Critical errors: 1 material (>10% variance)

👀 Step 3/4: Reviewing flagged values...

────────────────────────────────────────────────────────────────────────────────
🔍 Material: Porcelain
   Status: NEEDS_REVIEW
   Current: 2.4 g/cm³
   AI Verified: 2.5 g/cm³
   Variance: 4.17%
   Confidence: 95%
   Reasoning: Value of 2.5 g/cm³ consistently reported...
────────────────────────────────────────────────────────────────────────────────
   Accept AI value? [y/n/s=skip]: y
   ✅ Approved

💾 Step 4/4: Merging verified data to Materials.yaml...
   ✅ Updated: 102 materials

[... continues for remaining properties ...]

✅ VERIFICATION COMPLETE
================================================================================

📊 Statistics:
   Properties: 5
   Values verified: 610
   Corrections made: 34 (5.6% error rate found)
   Critical errors: 1
   Cost: $1.22
   Time: 3.2 hours

💾 Materials.yaml has been updated with verified values
📄 Verification report saved: data/research/verification_report_20251002_143022.md
```

## Integration with run.py

The `--data` flag is seamlessly integrated into the main `run.py` workflow:

```python
# In run.py
if args.data is not None:
    return run_data_verification(args.data)
```

This calls the `run_data_verification()` function which:
1. Parses the mode parameter (test, critical, all, etc.)
2. Builds the appropriate command for `systematic_verify.py`
3. Executes the verification subprocess
4. Reports results back to the user

## Comparison: run.py vs Direct Tool

### Using run.py (Recommended)
```bash
python3 run.py --data=critical
```
**Advantages:**
- ✅ Consistent with other run.py commands
- ✅ Single entry point for all operations
- ✅ Fail-fast validation runs first
- ✅ Familiar command structure

### Using Tool Directly (Advanced)
```bash
python3 scripts/research_tools/systematic_verify.py --critical
```
**Advantages:**
- ✅ More control over advanced options
- ✅ Can use `--auto-accept-minor`, `--batch-size`, etc.
- ✅ Direct access to all tool features

**Both methods work identically** - choose based on your preference.

## Common Workflows

### 1. First-Time Verification
```bash
# Step 1: Test safely (15 min)
python3 run.py --data=test

# Step 2: Review test results
cat data/research/verification_report_*.md | tail -50

# Step 3: Verify critical properties (3 hrs)
python3 run.py --data=critical

# Step 4: Verify everything (18 hrs, can run overnight)
python3 run.py --data=all
```

### 2. Quick Property Check
```bash
# Just verify density and melting point
python3 run.py --data=--properties=density,meltingPoint
```

### 3. Group Verification
```bash
# Verify all mechanical properties
python3 run.py --data=--group=mechanical

# Then verify optical properties
python3 run.py --data=--group=optical
```

## Help and Documentation

### View all options
```bash
python3 run.py --help
```

### Quick reference
```bash
bash scripts/research_tools/quick_reference.sh
```

### Complete guide
- `SYSTEMATIC_VERIFICATION_SUMMARY.md` - Quick reference
- `docs/SYSTEMATIC_VERIFICATION_GUIDE.md` - Complete 600-line guide
- `scripts/research_tools/systematic_verify.py --help` - Tool help

## Troubleshooting

### "No module found" error
Make sure you're in the project root:
```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
python3 run.py --data=test
```

### "API client error"
Check your DeepSeek API configuration:
```bash
python3 scripts/tools/api_terminal_diagnostics.py deepseek
```

### Want more control?
Use the tool directly for advanced options:
```bash
python3 scripts/research_tools/systematic_verify.py --critical --auto-accept-minor
```

## Expected Results

- **Before:** ~90-95% accurate (estimated)
- **After:** 99%+ accurate (AI-verified)
- **Typical corrections:** 5-10% of values
- **Audit trail:** Complete documentation for every change
- **References:** ASM Handbook, CRC, NIST, MatWeb

## Next Steps After Verification

Once data is verified, regenerate frontmatter with accurate data:

```bash
# Regenerate all frontmatter with verified data
python3 run.py --all --components frontmatter
```

The frontmatter generator will automatically use the verified, cached data thanks to the caching system implemented earlier.
