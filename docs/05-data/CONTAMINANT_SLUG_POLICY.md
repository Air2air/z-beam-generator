# Contaminant Slug Policy
**Status**: MANDATORY  
**Date**: December 14, 2025  
**Applies to**: All contaminant frontmatter files

---

## Policy Statement

**ALL contaminant slugs MUST end with `-contamination` suffix.**

This is not a bug or inconsistency - it is **intentional and required** for:
1. **SEO Clarity** - URLs explicitly indicate contamination content
2. **Domain Separation** - Prevents slug conflicts with materials/settings
3. **URL Semantics** - Clear, self-documenting URL structure

---

## Slug Format

### Pattern
```
{pattern-name}-contamination
```

### Examples

| Pattern Name | Pattern ID | Slug | ✓/✗ |
|-------------|------------|------|-----|
| Industrial Oil | industrial-oil | `industrial-oil-contamination` | ✅ |
| Rust Formation | rust-formation | `rust-formation-contamination` | ✅ |
| Adhesive Residue | adhesive-residue | `adhesive-residue-contamination` | ✅ |
| Industrial Oil | industrial-oil | `industrial-oil` | ❌ Missing suffix |
| Rust | rust-formation | `rust-formation-contamination-pattern` | ❌ Wrong suffix |

---

## Implementation

### Exporter Code
**File**: `export/contaminants/trivial_exporter.py`  
**Method**: `_create_slug()`

```python
def _create_slug(self, name: str) -> str:
    """
    Create URL-friendly slug from contamination pattern name.
    
    MANDATORY SUFFIX: All contaminant slugs MUST end with '-contamination'
    """
    slug = name.lower().replace(' ', '-').replace('_', '-')
    slug = slug.replace('(', '').replace(')', '')
    # Remove consecutive hyphens
    while '--' in slug:
        slug = slug.replace('--', '-')
    slug = slug.strip('-')
    
    # MANDATORY: Append -contamination suffix
    return f"{slug}-contamination"
```

### Frontmatter Structure
```yaml
name: Industrial Oil
slug: industrial-oil-contamination  # MUST have -contamination suffix
category: contamination
# ... other fields
```

---

## URL Structure

### Full URL Path
```
/contamination/{category}/{slug}
```

### Examples
```
/contamination/hydrocarbons/industrial-oil-contamination
/contamination/corrosion/rust-formation-contamination
/contamination/adhesives/adhesive-residue-contamination
```

### Breadcrumb Navigation
```yaml
breadcrumb:
  - label: Home
    href: /
  - label: Contamination
    href: /contamination
  - label: Hydrocarbons
    href: /contamination/hydrocarbons
  - label: Industrial Oil Contamination
    href: /contamination/hydrocarbons/industrial-oil-contamination
```

---

## Crosslinking

### From Materials to Contaminants
When linking from material pages to contaminant pages, use full slug:

```markdown
Common contaminants include [industrial oil](../contaminants/industrial-oil-contamination.md)
```

### From Contaminants to Materials
```markdown
Commonly found on [steel](../materials/steel.md) surfaces
```

---

## Testing Requirements

### Test Files Must Verify Suffix
All tests checking contaminant slugs must expect and verify the `-contamination` suffix:

```python
# ✅ CORRECT
def test_contaminant_slug_format():
    slug = create_slug("Industrial Oil")
    assert slug == "industrial-oil-contamination"
    assert slug.endswith("-contamination")

# ❌ WRONG
def test_contaminant_slug_format():
    slug = create_slug("Industrial Oil")
    assert slug == "industrial-oil"  # Missing suffix check
```

### Integration Tests
```python
def test_crosslink_to_contaminant():
    link = build_contaminant_link("industrial-oil")
    assert "-contamination" in link
    assert link == "../contaminants/industrial-oil-contamination.md"
```

---

## Why This Pattern?

### 1. SEO Optimization
**Problem**: Generic slugs like `/contamination/oil` are ambiguous  
**Solution**: `/contamination/hydrocarbons/industrial-oil-contamination` is explicit

### 2. Avoid Slug Conflicts
**Problem**: Material "Steel" and contaminant "Steel-Corrosion" could conflict  
**Solution**: Suffix creates namespace separation

| Domain | Example Slug |
|--------|--------------|
| Material | `steel` |
| Settings | `steel-settings` |
| Contaminant | `steel-corrosion-contamination` |

### 3. URL Self-Documentation
Users and search engines immediately understand the content type from the URL:
- `/materials/aluminum` - Material page
- `/settings/aluminum-settings` - Settings page
- `/contamination/rust-formation-contamination` - Contamination page

### 4. Future-Proofing
If we add more contamination subcategories or related content types, the suffix provides clear namespace boundaries.

---

## Enforcement

### Code Level
- `_create_slug()` method in exporter automatically appends suffix
- No manual slug creation - all slugs generated through exporter

### Test Level
- Unit tests verify suffix presence
- Integration tests verify crosslinks use full slug with suffix
- Schema validation requires suffix pattern

### Documentation Level
- This policy document (MANDATORY reference)
- Phase 1 normalization documentation
- Crosslinking implementation guides

---

## Migration Notes

### No Migration Needed
- All 99 contaminant files already have suffix (as of Dec 14, 2025)
- Exporter code already implements suffix requirement
- No existing URLs to redirect

### Future Contaminants
All new contamination patterns will automatically receive suffix through exporter.

---

## Related Documentation

- **Phase 1 Normalization**: `PHASE1_NORMALIZATION_COMPLETE_DEC14_2025.md`
- **Crosslinking System**: `docs/08-development/CROSSLINKING_IMPLEMENTATION.md`
- **SEO Module**: `domains/contaminants/modules/seo_module.py`
- **URL Building**: `shared/text/cross_linking/link_builder.py`

---

## Exceptions

**NONE.** There are no exceptions to this policy.

Every contaminant slug must have the `-contamination` suffix. Period.

---

## Checklist for New Contaminants

When adding a new contamination pattern:

- [ ] Pattern ID in Contaminants.yaml (e.g., `industrial-oil`)
- [ ] Name field (e.g., `Industrial Oil`)
- [ ] Exporter generates slug: `industrial-oil-contamination` ✅
- [ ] Frontmatter file created: `industrial-oil-contamination.yaml` ✅
- [ ] Breadcrumb includes full slug ✅
- [ ] Images use full slug in URLs ✅
- [ ] Tests verify suffix presence ✅

---

**Last Updated**: December 14, 2025  
**Policy Status**: MANDATORY - No exceptions  
**Compliance**: 100% (99/99 contaminants)
