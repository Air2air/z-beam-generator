# Frontend Frontmatter Spec Compliance Status

**Date:** December 26, 2025  
**Spec Version:** 5.0.0  
**Reference:** `docs/BACKEND_FRONTMATTER_SPEC.md`

---

## 📊 Compliance Summary

| Domain | Overall Status | Critical Issues | Minor Issues |
|--------|---------------|-----------------|--------------|
| Materials | ✅ 95% Compliant | 0 | 1 (missing width/height in images) |
| Contaminants | ⚠️ 70% Compliant | 2 | 0 |
| Compounds | 🔍 Not Audited | ? | ? |
| Settings | 🔍 Not Audited | ? | ? |

---

## ✅ What's Working (Compliant)

### All Domains
- ✅ `page_description` field present and used correctly
- ✅ `author` is properly structured object (not string)
- ✅ `micro` is properly structured object with before/after
- ✅ `faq` is array of objects
- ✅ `breadcrumb` is array with label/href
- ✅ ISO 8601 dates with timezone
- ✅ `schema_version` field present
- ✅ No deprecated `subtitle` field

### Materials Specific
- ✅ `images` field exists with proper nested structure
- ✅ Properties have proper structure (value, unit, min, max)
- ✅ No deprecated `description` field at top level

---

## ❌ Compliance Issues Found

### CRITICAL ISSUES

#### 1. Contaminants: `description` Field Present (DEPRECATED)
**Status:** ❌ CRITICAL  
**Impact:** Frontend expects ONLY `page_description`, not `description`  
**Location:** All 98 contaminant frontmatter files  
**Current State:**
```yaml
description: "Long AI-generated content about adhesive residue..."
page_description: "Short SEO meta description..."
```
**Required State:**
```yaml
page_description: "Short SEO meta description..."
# description field should not exist at top level
```

**Root Cause:** Source data (`data/contaminants/Contaminants.yaml`) contains both fields  
**Fix Required:** 
- Option A: Rename `description` → `content` or `main_content` in source data
- Option B: Move `description` into `components` object
- Option C: Remove `description` from export (keep in source for internal use)

#### 2. Contaminants: Missing `images` Field
**Status:** ❌ CRITICAL  
**Impact:** Frontend expects images structure, currently absent  
**Location:** All contaminant frontmatter files  
**Current State:**
```yaml
# No images field at all
```
**Required State:**
```yaml
images:
  hero:
    url: /images/contaminant/adhesive-residue-hero.jpg
    alt: Adhesive residue on metal surface before laser cleaning
    width: 1200
    height: 630
  micro:
    url: /images/contaminant/adhesive-residue-micro.jpg
    alt: Microscopic view of adhesive residue contamination
    width: 800
    height: 600
```

**Fix Required:** Add ImagePathEnricher to contaminants export config

---

### MINOR ISSUES

#### 3. Materials: Images Missing width/height
**Status:** ⚠️ MINOR  
**Impact:** Optional fields, but spec shows them in examples  
**Location:** All material frontmatter files  
**Current State:**
```yaml
images:
  hero:
    url: /images/material/aluminum-hero.jpg
    alt: Aluminum surface during laser cleaning
    # Missing width/height
```
**Required State (per spec examples):**
```yaml
images:
  hero:
    url: /images/material/aluminum-hero.jpg
    alt: Aluminum surface during laser cleaning
    width: 1200  # Add
    height: 630  # Add
```

**Fix Required:** Update ImagePathEnricher to include default dimensions

---

## 🔧 Action Plan

### Priority 1: Critical Fixes (MUST DO)

**1.1 Fix Contaminants `description` Field**
```bash
# Step 1: Decide on approach (discuss with team)
# Option A: Rename in source data
# Option B: Move to components
# Option C: Remove from export

# Step 2: Update export config
# If Option C: Add to cleanup_rules.legacy_fields in export/config/contaminants.yaml

# Step 3: Re-export
python3 run.py --export --domain contaminants

# Step 4: Verify
python3 << 'VERIFY'
import yaml
with open('../z-beam/frontmatter/contaminants/adhesive-residue-contamination.yaml') as f:
    data = yaml.safe_load(f)
assert 'description' not in data, "description field still present!"
assert 'page_description' in data, "page_description missing!"
print("✅ Contaminants description field compliance verified")
VERIFY
```

**1.2 Add Images to Contaminants**
```bash
# Step 1: Add enricher to export/config/contaminants.yaml
# Add after author enricher:
# - type: image_paths
#   module: export.enrichers.media.image_path_enricher
#   class: ImagePathEnricher
#   domain: contaminants

# Step 2: Re-export
python3 run.py --export --domain contaminants

# Step 3: Verify
python3 << 'VERIFY'
import yaml
with open('../z-beam/frontmatter/contaminants/adhesive-residue-contamination.yaml') as f:
    data = yaml.safe_load(f)
assert 'images' in data, "images field missing!"
assert 'hero' in data['images'], "images.hero missing!"
assert 'url' in data['images']['hero'], "images.hero.url missing!"
print("✅ Contaminants images field compliance verified")
VERIFY
```

### Priority 2: Minor Enhancements (SHOULD DO)

**2.1 Add width/height to Materials Images**
```bash
# Step 1: Update ImagePathEnricher to include dimensions
# Edit export/enrichers/media/image_path_enricher.py
# Add width/height to default structure

# Step 2: Re-export materials
python3 run.py --export --domain materials

# Step 3: Verify
python3 << 'VERIFY'
import yaml
with open('../z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml') as f:
    data = yaml.safe_load(f)
assert 'width' in data['images']['hero'], "width missing!"
assert 'height' in data['images']['hero'], "height missing!"
print("✅ Materials images width/height compliance verified")
VERIFY
```

### Priority 3: Audit Remaining Domains (TODO)

- [ ] Audit compounds frontmatter for spec compliance
- [ ] Audit settings frontmatter for spec compliance
- [ ] Create automated compliance test suite

---

## 📝 Questions for Frontend Team

1. **Contaminants `description` field:** What should we call the main long-form content?
   - `content`?
   - `main_content`?
   - Move to `components.description`?
   - Just remove from frontmatter entirely?

2. **Image dimensions:** Are width/height truly required or just recommended?
   - If required: What are standard dimensions for each image type?
   - hero: 1200x630? (og:image standard)
   - micro: 800x600?

3. **Properties structure:** Do ALL properties need min/max or just recommended?

---

## 🧪 Verification Script

Run after fixes to verify full compliance:

```bash
python3 << 'EOF'
import yaml
from pathlib import Path

def check_compliance(filepath, domain):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    issues = []
    
    # Check required fields
    if 'page_description' not in data:
        issues.append(f"Missing page_description")
    if 'description' in data and domain != 'materials':
        issues.append(f"Has deprecated 'description' field")
    if not isinstance(data.get('author'), dict):
        issues.append(f"author is not object")
    if not isinstance(data.get('images'), dict):
        issues.append(f"images is not object")
    if 'images' in data:
        if 'hero' not in data['images']:
            issues.append(f"images.hero missing")
        elif 'width' not in data['images']['hero']:
            issues.append(f"images.hero.width missing (minor)")
    
    return issues

# Check sample from each domain
domains = {
    'materials': 'aluminum-laser-cleaning',
    'contaminants': 'adhesive-residue-contamination',
}

print("=" * 80)
print("COMPLIANCE VERIFICATION")
print("=" * 80)

for domain, sample_id in domains.items():
    filepath = f"../z-beam/frontmatter/{domain}/{sample_id}.yaml"
    if Path(filepath).exists():
        issues = check_compliance(filepath, domain)
        status = "✅ PASS" if not issues else f"❌ FAIL ({len(issues)} issues)"
        print(f"\n{domain.upper()}: {status}")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n{domain.upper()}: ⚠️ SKIP (file not found)")

print("\n" + "=" * 80)
