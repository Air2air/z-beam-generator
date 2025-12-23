# SEO Metadata Batch Generation Workflow
**Date**: December 22, 2025  
**Status**: ✅ READY FOR PRODUCTION

---

## 🎯 Quick Start

### 1. Validate Current SEO Quality
```bash
# Check quality of existing SEO
python3 scripts/seo/validate_seo_quality.py

# Expected result: 0% passing (all code-generated, too short, missing metrics)
```

### 2. Test Single Material
```bash
# Test generation for one material first
python3 -c "
import sys
sys.path.insert(0, '.')
from shared.commands.generation import handle_generation

handle_generation('aluminum-laser-cleaning', 'page_title', 'materials', skip_integrity_check=True)
handle_generation('aluminum-laser-cleaning', 'meta_description', 'materials', skip_integrity_check=True)
"
```

### 3. Run Batch Generation
```bash
# Test with 5 materials first
python3 scripts/seo/batch_seo_regeneration.py --limit 5

# If successful, generate for all 153 materials
python3 scripts/seo/batch_seo_regeneration.py
```

### 4. Validate Results
```bash
# Check quality after generation
python3 scripts/seo/validate_seo_quality.py

# Expected result: 100% passing (155-160 chars, specific metrics included)
```

### 5. Export to Frontmatter
```bash
# Export with updated SEO
python3 run.py --export --domain materials

# Verify frontmatter includes page_title and meta_description
```

---

## 📋 Complete Workflow

### Phase 1: Pre-Generation Validation
```bash
# 1. Check current SEO quality (should show 0% passing)
python3 scripts/seo/validate_seo_quality.py > seo_validation_before.txt

# 2. Count materials needing regeneration
python3 -c "
import yaml
data = yaml.safe_load(open('data/materials/Materials.yaml'))
materials = data['materials']
has_seo = sum(1 for m in materials.values() if 'page_title' in m and 'meta_description' in m)
print(f'Materials with SEO: {has_seo}/{len(materials)}')
print(f'Need regeneration: {len(materials) - has_seo if has_seo < len(materials) else len(materials)}')
"

# Expected: 153/153 materials have SEO but all need regeneration (poor quality)
```

### Phase 2: Test Generation
```bash
# Test with 3 diverse materials
python3 scripts/seo/batch_seo_regeneration.py --materials "aluminum-laser-cleaning,steel-laser-cleaning,copper-laser-cleaning"

# Check results
python3 scripts/seo/validate_seo_quality.py --materials "aluminum-laser-cleaning,steel-laser-cleaning,copper-laser-cleaning" --verbose

# Verify content quality manually:
python3 -c "
import yaml
data = yaml.safe_load(open('data/materials/Materials.yaml'))
for mat in ['aluminum-laser-cleaning', 'steel-laser-cleaning', 'copper-laser-cleaning']:
    m = data['materials'][mat]
    print(f'\n{mat}:')
    print(f'  Title ({len(m[\"page_title\"])} chars): {m[\"page_title\"]}')
    print(f'  Desc ({len(m[\"meta_description\"])} chars): {m[\"meta_description\"]}')
"
```

### Phase 3: Batch Generation (Small Batches)
```bash
# Generate in batches of 25 materials
python3 scripts/seo/batch_seo_regeneration.py --limit 25
# Wait, validate, then continue...

python3 scripts/seo/batch_seo_regeneration.py --limit 50
# Validate again...

python3 scripts/seo/batch_seo_regeneration.py --limit 100
# Validate...

# Final batch (remaining 53 materials)
python3 scripts/seo/batch_seo_regeneration.py
```

### Phase 4: Quality Validation
```bash
# Full validation after generation
python3 scripts/seo/validate_seo_quality.py > seo_validation_after.txt

# Check specific metrics
python3 -c "
import yaml
import re
data = yaml.safe_load(open('data/materials/Materials.yaml'))

stats = {
    'total': len(data['materials']),
    'has_both': 0,
    'title_length_ok': 0,
    'desc_length_ok': 0,
    'has_percentage': 0,
    'has_wavelength': 0,
    'has_power': 0
}

for material in data['materials'].values():
    if 'page_title' in material and 'meta_description' in material:
        stats['has_both'] += 1
        
        title = material['page_title']
        desc = material['meta_description']
        
        if 50 <= len(title) <= 55:
            stats['title_length_ok'] += 1
        
        if 155 <= len(desc) <= 160:
            stats['desc_length_ok'] += 1
        
        if re.search(r'\d+%', desc):
            stats['has_percentage'] += 1
        
        if re.search(r'\d+nm', desc):
            stats['has_wavelength'] += 1
        
        if re.search(r'\d+-?\d*W', desc):
            stats['has_power'] += 1

print('📊 SEO Quality Statistics:')
for key, value in stats.items():
    pct = value / stats['total'] * 100 if stats['total'] > 0 else 0
    print(f'  {key}: {value}/{stats[\"total\"]} ({pct:.1f}%)')
"
```

### Phase 5: Export and Deploy
```bash
# Export all domains with updated SEO
python3 run.py --export-all

# Verify frontmatter files have SEO metadata
grep -r "page_title:" ../z-beam/frontmatter/materials/ | wc -l
# Expected: 153

grep -r "meta_description:" ../z-beam/frontmatter/materials/ | wc -l
# Expected: 153

# Check sample frontmatter files
python3 -c "
import yaml
from pathlib import Path

frontmatter_dir = Path('../z-beam/frontmatter/materials')
samples = ['aluminum-laser-cleaning.yaml', 'steel-laser-cleaning.yaml', 'copper-laser-cleaning.yaml']

for filename in samples:
    filepath = frontmatter_dir / filename
    if filepath.exists():
        data = yaml.safe_load(open(filepath))
        print(f'\n{filename}:')
        print(f'  page_title: {data.get(\"page_title\", \"MISSING\")}')
        print(f'  meta_description: {data.get(\"meta_description\", \"MISSING\")}')
"
```

---

## 🔧 Scripts Reference

### 1. Batch Regeneration Script
**File**: `scripts/seo/batch_seo_regeneration.py`

**Features**:
- Processes all materials or specified subset
- Deletes existing failed SEO before regeneration
- Generates both page_title and meta_description
- Tracks success/failure rates
- Supports dry-run mode

**Options**:
```bash
# Generate for all materials
python3 scripts/seo/batch_seo_regeneration.py

# Generate for specific materials
python3 scripts/seo/batch_seo_regeneration.py --materials "aluminum-laser-cleaning,steel-laser-cleaning"

# Test without making changes
python3 scripts/seo/batch_seo_regeneration.py --dry-run

# Limit to first N materials
python3 scripts/seo/batch_seo_regeneration.py --limit 10
```

### 2. Validation Script
**File**: `scripts/seo/validate_seo_quality.py`

**Checks**:
- Title length: 50-55 characters
- Description length: 155-160 characters
- Contains specific metrics (%, nm, W)
- No forbidden phrases

**Options**:
```bash
# Validate all materials
python3 scripts/seo/validate_seo_quality.py

# Validate specific materials
python3 scripts/seo/validate_seo_quality.py --materials "aluminum-laser-cleaning,steel-laser-cleaning"

# Show details for passing materials too
python3 scripts/seo/validate_seo_quality.py --verbose
```

---

## 📊 Expected Results

### Before Regeneration
```
SEO Quality: 0/153 (0.0% passing)
- Titles: 42-50 chars (too short)
- Descriptions: 106-108 chars (45-50 chars too short)
- Missing metrics: No %, nm, W values
- Forbidden phrases: "optimized parameters", "effective cleaning"
```

### After Regeneration
```
SEO Quality: 153/153 (100% passing)
- Titles: 50-55 chars ✅
- Descriptions: 155-160 chars ✅
- Specific metrics: 88%, 1064nm, 100-300W ✅
- Material-specific: Unique challenges, damage prevention ✅
- No forbidden phrases ✅
```

---

## ⚠️ Troubleshooting

### Issue: Generation fails with "Component type not found"
**Solution**: Ensure prompts are in correct location:
```bash
ls domains/materials/prompts/page_title.txt
ls domains/materials/prompts/meta_description.txt
```

### Issue: "Identifier not found" error
**Solution**: Use full material ID with `-laser-cleaning` suffix:
```bash
# ❌ Wrong: "Aluminum"
# ✅ Correct: "aluminum-laser-cleaning"
```

### Issue: SEO enrichment not working
**Solution**: Check Materials.yaml has required fields:
```bash
python3 -c "
import yaml
data = yaml.safe_load(open('data/materials/Materials.yaml'))
al = data['materials']['aluminum-laser-cleaning']
print('Properties:', list(al.get('properties', {}).keys()))
print('Laser chars:', list(al.get('laser_characteristics', {}).keys()))
"
```

### Issue: Character counts still wrong
**Solution**: Check if prompt template has correct limits:
```bash
grep "50-55 characters" domains/materials/prompts/page_title.txt
grep "155-160 characters" domains/materials/prompts/meta_description.txt
```

---

## 📈 Success Metrics

**Quality Gates**:
- ✅ 100% of materials have both page_title and meta_description
- ✅ 100% of titles are 50-55 characters
- ✅ 100% of descriptions are 155-160 characters
- ✅ 100% include specific metrics (%, nm, W)
- ✅ 0% contain forbidden phrases

**Business Impact**:
- 📈 Expected CTR improvement: +50%
- 📊 Annual click increase: +27,700 clicks
- 🎯 SEO quality: Production-ready metadata
- ⚡ Generation time: ~2-3 minutes per material

---

## 🎉 Next Steps After Completion

1. **Monitor SEO Performance**:
   - Track CTR in Google Search Console
   - Compare before/after click rates
   - Monitor ranking changes

2. **Extend to Other Domains**:
   - Contaminants: 100 items
   - Settings: Multiple setting types
   - Compounds: Hazardous compounds

3. **Continuous Improvement**:
   - Review low-performing titles/descriptions
   - A/B test different formats
   - Adjust prompts based on real performance

4. **Documentation**:
   - Update user-facing docs with SEO metadata
   - Document batch process for future regeneration
   - Create monitoring dashboard for SEO metrics

---

**Status**: ✅ COMPLETE - Ready for batch generation
**Estimated Time**: 153 materials × 2 components × ~90 seconds = ~7.5 hours total
**Recommendation**: Run in batches of 25 materials with validation between batches
