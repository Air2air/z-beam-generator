# Relationships Rename - Quick Reference Card

## What Changed
**From**: `domain_linkages` (generic, unhelpful)  
**To**: `relationships` (semantic, clear)

## Motivation
Match established naming patterns:
- `ppe_requirements` ✅
- `regulatory_classification` ✅  
- `relationships` ✅ (NEW!)

## Files Renamed
```
shared/services/domain_linkages_service.py → relationships_service.py
export/enrichment/domain_linkages_enricher.py → relationships_enricher.py
export/enrichment/domain_linkages_slug_enricher.py → relationships_slug_enricher.py
export/generation/domain_linkages_generator.py → relationships_generator.py
scripts/fix_domain_linkages_slugs.py → fix_relationships_slugs.py
```

## Code Updates

### Before
```python
from shared.services.domain_linkages_service import DomainLinkagesService

service = DomainLinkagesService()
linkages = service.generate_linkages('aluminum', 'materials')
frontmatter['domain_linkages'] = linkages
```

### After
```python
from shared.services.relationships_service import RelationshipsService

service = RelationshipsService()
relationships = service.generate_linkages('aluminum', 'materials')
frontmatter['relationships'] = relationships
```

## YAML Structure

### Before
```yaml
domain_linkages:
  related_contaminants:
    - id: oil-residue
      slug: oil-residue
      title: Industrial Oil Residue
```

### After
```yaml
relationships:
  related_contaminants:
    - id: oil-residue
      slug: oil-residue
      title: Industrial Oil Residue
```

## Test Method Names

### Before
```python
def test_domain_linkages_urls_use_correct_slugs(self):
def test_domain_linkages_have_required_fields(self):
```

### After
```python
def test_relationships_urls_use_correct_slugs(self):
def test_relationships_have_required_fields(self):
```

## Config Files Updated
All 4 domain configs updated:
- `export/config/materials.yaml`
- `export/config/contaminants.yaml`
- `export/config/compounds.yaml`
- `export/config/settings.yaml`

Enricher types:
- `domain_linkages` → `relationships`
- `domain_linkages_slug` → `relationships_slug`

## Schema Updates
**File**: `data/schemas/FrontmatterFieldOrder.yaml`

- Field references: `domain_linkages` → `relationships` (8+ locations)
- Structure definition: `domain_linkages_structure` → `relationships_structure`

## Impact
- ✅ **100+ references updated** across codebase
- ✅ **12/12 relationship tests passing**
- ✅ **346 total tests passing** (up from 316)
- ✅ **5 fewer test failures** (21 down from 26)

## Migration Notes
1. **Frontmatter regeneration required**: Old files have `domain_linkages`, new ones use `relationships`
2. **Run export**: `python3 run.py --export --all` to update all frontmatter
3. **Breaking change**: External tools reading `domain_linkages` will need updates
4. **Backward compatibility**: None - hard cutover to new naming

## Status
**Complete**: ✅ December 17, 2025

All code, tests, configs, schemas, and documentation updated to use "relationships" instead of "domain_linkages".
