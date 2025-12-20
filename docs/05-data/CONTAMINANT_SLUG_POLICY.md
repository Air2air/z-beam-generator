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
category: organic_residue            # REQUIRED: One of 8 main categories
subcategory: hydrocarbons           # REQUIRED: Valid subcategory for category
# ... other fields
```

---

## Category Requirements 🔥 **MANDATORY (Dec 14, 2025)**

**ALL contaminants MUST have both `category` and `subcategory` fields.**

### Required Fields
- **category**: One of 8 allowed main categories (see schema.yaml)
- **subcategory**: Valid subcategory for the specified category

### 8 Main Categories
1. **oxidation** - Rust, tarnish, patina, corrosion
2. **organic_residue** - Oils, greases, waxes, adhesives
3. **inorganic_coating** - Dust, dirt, mineral deposits, concrete
4. **metallic_coating** - Plating, metallic paints, metal deposits
5. **thermal_damage** - Heat discoloration, burn marks, charring
6. **biological** - Mold, algae, biofilms, organic growth
7. **chemical_residue** - Chemical stains, etchants, process residues
8. **aging** - General weathering and degradation

### Fail-Fast Enforcement
**File**: `export/contaminants/trivial_exporter.py`  
**Lines**: 198-213

The exporter will **raise ValueError** if category or subcategory is missing:

```python
# Validate required categorization fields
if 'category' not in pattern or not pattern['category']:
    raise ValueError(
        f"Contamination pattern '{pattern_id}' missing required 'category' field. "
        f"All contaminants must have a category."
    )

if 'subcategory' not in pattern or not pattern['subcategory']:
    raise ValueError(
        f"Contamination pattern '{pattern_id}' missing required 'subcategory' field. "
        f"All contaminants must have a subcategory."
    )
```

**Result**: System will NOT export contaminants with missing categories. This ensures 100% data quality.

### Schema Documentation
See `domains/contaminants/schema.yaml` for complete list of:
- Allowed categories (8 total)
- Allowed subcategories by category (27 total)
- Subcategory descriptions and examples

---

## URL Structure

### Full URL Path
```
/contaminants/{slug}
```

**Note**: Flat structure - no category subdirectories (as of Dec 14, 2025)

### Examples
```
/contaminants/industrial-oil-contamination
/contaminants/rust-formation-contamination
/contaminants/adhesive-residue-contamination
```

### Breadcrumb Navigation
```yaml
breadcrumb:
  - label: Home
    href: /
  - label: Contaminants
    href: /contaminants
  - label: Industrial Oil Contamination
    href: /contaminants/industrial-oil-contamination
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
- `/materials/metal/non-ferrous/aluminum` - Material page (with categories)
- `/settings/metal/non-ferrous/aluminum-settings` - Settings page (with categories)
- `/contaminants/oxidation/ferrous/rust-formation-contamination` - Contamination page (with categories)

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
- [ ] **Category field** (e.g., `organic_residue`) - **REQUIRED** ✅
- [ ] **Subcategory field** (e.g., `hydrocarbons`) - **REQUIRED** ✅
- [ ] Category/subcategory validated against schema.yaml ✅
- [ ] Exporter generates slug: `industrial-oil-contamination` ✅
- [ ] Frontmatter file created: `industrial-oil-contamination.yaml` ✅
- [ ] Breadcrumb includes full slug ✅
- [ ] Images use full slug in URLs ✅
- [ ] Tests verify suffix presence ✅
- [ ] Tests verify category/subcategory presence ✅

---

**Last Updated**: December 14, 2025  
**Policy Status**: MANDATORY - No exceptions  
**Compliance**: 100% (98/98 contaminants with category/subcategory)
