# Image Path Fix Required - Settings YAML

**Date**: December 2, 2025  
**Priority**: HIGH - Images not displaying on settings pages

---

## Problem

The generator is outputting incorrect image paths in settings YAML files.

### Two Issues:

| Issue | Generator Output | Correct Value |
|-------|-----------------|---------------|
| **Path** | `/images/materials/` (with 's') | `/images/material/` (no 's') |
| **Extension** | `.png` | `.jpg` |

---

## Example

**Current (WRONG):**
```yaml
images:
  hero:
    url: /images/materials/aluminum-laser-cleaning-hero.png
```

**Correct:**
```yaml
images:
  hero:
    url: /images/material/aluminum-laser-cleaning-hero.jpg
```

---

## Verification

Actual files on disk:
```bash
ls public/images/material/*.jpg | head -5
# public/images/material/aluminum-laser-cleaning-hero.jpg
# public/images/material/aluminum-laser-cleaning-micro.jpg
# public/images/material/copper-laser-cleaning-hero.jpg
# ...
```

No `.png` files exist for hero images:
```bash
ls public/images/material/*.png 2>/dev/null
# (empty - no PNG hero images)
```

---

## Fix Required

In the settings exporter, change:

```python
# FROM:
hero_url = f"/images/materials/{slug}-laser-cleaning-hero.png"

# TO:
hero_url = f"/images/material/{slug}-laser-cleaning-hero.jpg"
```

Same for micro images:
```python
# FROM:
micro_url = f"/images/materials/{slug}-laser-cleaning-micro.png"

# TO:
micro_url = f"/images/material/{slug}-laser-cleaning-micro.jpg"
```

---

## Affected Files

All 153 settings files have incorrect paths:

```bash
grep -l "images/materials/.*\.png" frontmatter/settings/*.yaml | wc -l
# 153
```

---

## Quick Verification After Fix

```bash
# Check a few files
grep "url:.*hero" frontmatter/settings/aluminum-settings.yaml
# Should show: /images/material/aluminum-laser-cleaning-hero.jpg

grep "url:.*hero" frontmatter/settings/oak-settings.yaml  
# Should show: /images/material/oak-laser-cleaning-hero.jpg
```
