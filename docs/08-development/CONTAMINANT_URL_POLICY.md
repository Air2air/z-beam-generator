# Contaminant URL Naming Policy

**Policy Established**: December 12, 2025  
**Status**: Active

## Policy Statement

**ALL contaminant domain URLs MUST append '-contamination' suffix to the base slug.**

## Rationale

This policy ensures:
1. **URL Clarity**: Distinguishes contaminant pages from material pages
2. **SEO Optimization**: Keywords include "contamination" for search visibility
3. **Namespace Separation**: Prevents URL conflicts between domains
4. **User Experience**: URLs clearly indicate page content type

## Implementation

### Slug Generation

**Base Pattern**: `{contaminant-id}-contamination`

**Examples**:
- `scale-buildup` → `scale-buildup-contamination`
- `aluminum-oxidation` → `aluminum-oxidation-contamination`
- `adhesive-residue` → `adhesive-residue-contamination`
- `copper-patina` → `copper-patina-contamination`

### Affected Components

1. **Metadata Module** (`domains/contaminants/modules/metadata_module.py`):
   ```python
   # POLICY: Append '-contamination' suffix to all contaminant domain URLs
   slug = contaminant_id.lower().replace('_', '-') + '-contamination'
   ```

2. **SEO Module** (`domains/contaminants/modules/seo_module.py`):
   ```python
   # POLICY: Append '-contamination' suffix to all contaminant domain URLs
   slug = contaminant_id.lower().replace('_', '-') + '-contamination'
   ```

3. **Canonical URLs**:
   - Format: `/contamination/{category}/{slug}`
   - Example: `/contamination/contamination/scale-buildup-contamination`

4. **Frontmatter Filenames**:
   - Pattern: `{slug}.yaml` (from config)
   - Example: `scale-buildup-contamination.yaml`
   - Location: `frontmatter/contaminants/`

## URL Structure

**Full URL Pattern**:
```
/contamination/{category}/{contaminant-id}-contamination
```

**URL Components**:
- Base path: `/contamination/`
- Category: `contamination` or `aging`
- Slug: `{contaminant-id}-contamination`

**Example URLs**:
- `/contamination/contamination/scale-buildup-contamination`
- `/contamination/aging/copper-patina-contamination`
- `/contamination/contamination/aluminum-oxidation-contamination`

## Enforcement

**Automated**: Policy enforced at code level in slug generation methods.

**No Exceptions**: ALL contaminant URLs must follow this pattern.

**Validation**: 
```bash
# Test slug generation
python3 -c "
from domains.contaminants.modules.metadata_module import MetadataModule
metadata = MetadataModule().generate('scale-buildup', {...})
assert metadata['slug'] == 'scale-buildup-contamination'
"
```

## Related Domains

**Materials Domain**: Uses different pattern:
- Pattern: `{material-name}-laser-cleaning`
- Example: `aluminum-laser-cleaning`

**Settings Domain**: Uses material name only:
- Pattern: `{material-name}`
- Example: `aluminum`

## Migration

**Existing Files**: Will be regenerated with new suffix on next export/sync.

**Backward Compatibility**: Not applicable - contaminants domain is new.

**Frontmatter Sync**: Automatically uses metadata slug, no code changes needed.

## Testing

**Test Coverage**:
- ✅ Metadata module generates correct slug
- ✅ SEO module generates correct canonical URL
- ✅ Frontmatter sync uses correct filename
- ✅ All contaminant URLs include '-contamination' suffix

**Verification Commands**:
```bash
# Check metadata slug
python3 -c "from domains.contaminants.modules.metadata_module import MetadataModule; ..."

# Check SEO canonical URL
python3 -c "from domains.contaminants.modules.seo_module import SEOModule; ..."

# Check frontmatter files
ls frontmatter/contaminants/*-contamination.yaml
```

## References

- Metadata Module: `domains/contaminants/modules/metadata_module.py`
- SEO Module: `domains/contaminants/modules/seo_module.py`
- Frontmatter Sync: `generation/utils/frontmatter_sync.py`
- Domain Config: `domains/contaminants/config.yaml`
