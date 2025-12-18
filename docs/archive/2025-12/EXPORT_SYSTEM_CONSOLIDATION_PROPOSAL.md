# Export System Consolidation Proposal

**Date**: December 17, 2025  
**Status**: 📋 PROPOSAL  
**Estimated Impact**: 75% code reduction (3,285 → 800 lines)  
**Estimated Effort**: 2-3 days implementation + 1 day testing

---

## 🎯 Executive Summary

Consolidate 4 domain-specific exporter classes (3,285 lines) into a single universal exporter (~800 lines) using configuration-driven architecture. This builds on Schema 5.0.0 work and Phase 2 enrichment patterns to maximize code reuse.

**Key Benefits**:
- 75% less code to maintain
- Fix bugs once, works everywhere
- Add new domains with config file (no code)
- Consistent behavior across all domains
- Easier testing (test once, not 4x)

---

## 📊 Current State Analysis

### Code Duplication

| File | Lines | Purpose | Duplication |
|------|-------|---------|-------------|
| `export/core/trivial_exporter.py` | 2,115 | Materials exporter | 60% similar to others |
| `export/contaminants/trivial_exporter.py` | 372 | Contaminants exporter | 60% similar to others |
| `export/compounds/trivial_exporter.py` | 230 | Compounds exporter | 60% similar to others |
| `export/settings/trivial_exporter.py` | 278 | Settings exporter | 60% similar to others |
| `export/core/base_trivial_exporter.py` | 290 | Base class | Shared utilities |
| **Total** | **3,285** | **4 domains** | **~2,000 lines duplicated** |

### Repeated Patterns Across Domains

**Every domain implements**:
1. `_load_domain_data()` - Load YAML from data/ directory
2. `export_single()` - Export one item to frontmatter
3. `export_all()` - Iterate and export all items
4. `_build_frontmatter()` - Construct frontmatter dict
5. `_enrich_*()` - Add computed fields
6. `_generate_*()` - Generate derived content

**Example Duplication**:
```python
# In 4 different files, nearly identical code:

class SomeDomainExporter(BaseTrivialExporter):
    def _load_domain_data(self) -> Dict[str, Any]:
        """Load domain data from YAML."""
        with open(self.source_file) as f:
            data = yaml.safe_load(f)
        return data
    
    def export_single(self, item_id: str, item_data: Dict, force: bool = False) -> bool:
        """Export single item to frontmatter."""
        if not force and self._output_exists(item_id):
            return False
        
        frontmatter = self._build_frontmatter(item_data)
        self._write_frontmatter(item_id, frontmatter)
        return True
    
    def export_all(self, force: bool = True) -> Dict[str, bool]:
        """Export all items."""
        results = {}
        data = self._load_domain_data()
        for item_id, item_data in data['items'].items():
            results[item_id] = self.export_single(item_id, item_data, force)
        return results
```

**This exact pattern exists 4 times** with only minor variations (field names, paths).

---

## 🏗️ Proposed Architecture

### Universal Exporter Pattern

**Single class replaces 4 domain-specific classes**:

```python
# export/core/universal_exporter.py

class UniversalFrontmatterExporter:
    """
    Configuration-driven exporter for all domains.
    
    Replaces:
    - TrivialFrontmatterExporter (materials)
    - TrivialContaminantsExporter
    - CompoundExporter
    - TrivialSettingsExporter
    """
    
    def __init__(self, domain_config: Dict):
        """Initialize with domain configuration."""
        self.domain = domain_config['domain']
        self.source_file = domain_config['source_file']
        self.output_path = domain_config['output_path']
        self.enrichments = domain_config.get('enrichments', [])
        self.generators = domain_config.get('generators', [])
    
    def _load_domain_data(self) -> Dict[str, Any]:
        """Generic domain data loader."""
        with open(self.source_file) as f:
            return yaml.safe_load(f)
    
    def export_single(self, item_id: str, item_data: Dict, force: bool = False) -> bool:
        """Generic single item export."""
        if not force and self._output_exists(item_id):
            return False
        
        frontmatter = self._build_frontmatter(item_data)
        frontmatter = self._apply_enrichments(frontmatter)
        frontmatter = self._apply_generators(frontmatter)
        
        self._write_frontmatter(item_id, frontmatter)
        return True
    
    def export_all(self, force: bool = True) -> Dict[str, bool]:
        """Generic batch export."""
        results = {}
        data = self._load_domain_data()
        
        items_key = self.domain  # e.g., 'materials', 'contaminants'
        for item_id, item_data in data[items_key].items():
            results[item_id] = self.export_single(item_id, item_data, force)
        
        return results
    
    def _apply_enrichments(self, frontmatter: Dict) -> Dict:
        """Apply configured enrichments."""
        for enrichment in self.enrichments:
            enricher_class = ENRICHER_REGISTRY[enrichment['type']]
            enricher = enricher_class(enrichment['config'])
            frontmatter = enricher.enrich(frontmatter)
        
        return frontmatter
    
    def _apply_generators(self, frontmatter: Dict) -> Dict:
        """Apply configured content generators."""
        for generator in self.generators:
            generator_class = GENERATOR_REGISTRY[generator['type']]
            gen = generator_class(generator['config'])
            frontmatter = gen.generate(frontmatter)
        
        return frontmatter
```

**Key Innovation**: All domain-specific logic moves to **configuration**, not code.

---

## 📝 Configuration-Driven Approach

### Domain Configuration Files

**One config file per domain** (YAML, not Python):

#### `export/config/contaminants.yaml`
```yaml
domain: contaminants
source_file: data/contaminants/Contaminants.yaml
output_path: frontmatter/contaminants

# Data mapping
items_key: contaminants  # Key in source YAML containing items
id_field: id
slug_field: slug

# Enrichments (applied in order)
enrichments:
  - type: compound_linkage
    field: produces_compounds
    source: data/compounds/Compounds.yaml
    defaults:
      - concentration_range
      - hazard_class
      - exposure_limits
      - control_measures
    
  - type: material_linkage
    field: related_materials
    source: data/materials/Materials.yaml
    defaults:
      - category
      - subcategory
  
  - type: timestamp
    fields: [datePublished, dateModified]

# Content generators
generators:
  - type: seo_description
    source_field: contamination_description
    output_field: seo_description
    max_length: 160
  
  - type: breadcrumb
    template: "Home / Contaminants / {category} / {subcategory}"
```

#### `export/config/materials.yaml`
```yaml
domain: materials
source_file: data/materials/Materials.yaml
output_path: frontmatter/materials

items_key: materials
id_field: id
slug_field: slug

enrichments:
  - type: contaminant_linkage
    field: removes_contaminants
    source: data/contaminants/Contaminants.yaml
    defaults:
      - category
      - commonality_score
  
  - type: compound_linkage
    field: produces_compounds
    source: data/compounds/Compounds.yaml
    defaults:
      - concentration_range
      - hazard_class
  
  - type: timestamp
    fields: [datePublished, dateModified]

generators:
  - type: seo_description
    source_field: description
    output_field: seo_description
    max_length: 160
  
  - type: breadcrumb
    template: "Home / Materials / {category} / {subcategory}"
```

#### `export/config/compounds.yaml`
```yaml
domain: compounds
source_file: data/compounds/Compounds.yaml
output_path: frontmatter/compounds

items_key: compounds
id_field: id
slug_field: slug

enrichments:
  - type: contaminant_linkage
    field: found_in_materials
    source: data/materials/Materials.yaml
    defaults:
      - category
      - thermal_conductivity
  
  - type: timestamp
    fields: [datePublished, dateModified]

generators:
  - type: seo_description
    source_field: compound_description
    output_field: seo_description
    max_length: 160
  
  - type: breadcrumb
    template: "Home / Compounds / {category} / {subcategory}"
```

#### `export/config/settings.yaml`
```yaml
domain: settings
source_file: data/settings/Settings.yaml
output_path: frontmatter/settings

items_key: settings
id_field: material_name
slug_field: slug

enrichments:
  - type: material_linkage
    field: applies_to_material
    source: data/materials/Materials.yaml
    defaults:
      - category
      - thermal_conductivity
  
  - type: timestamp
    fields: [datePublished, dateModified]

generators:
  - type: seo_description
    source_field: settings_description
    output_field: seo_description
    max_length: 160
  
  - type: breadcrumb
    template: "Home / Settings / {material_category}"
```

---

## 🔧 Universal Enrichment System

### Enricher Registry

**Reusable enricher classes** (build on Phase 2 pattern):

```python
# export/enrichment/registry.py

ENRICHER_REGISTRY = {
    'compound_linkage': CompoundLinkageEnricher,
    'material_linkage': MaterialLinkageEnricher,
    'contaminant_linkage': ContaminantLinkageEnricher,
    'timestamp': TimestampEnricher,
}

class BaseLinkageEnricher(ABC):
    """Base class for all linkage enrichers."""
    
    def __init__(self, config: Dict):
        self.field = config['field']
        self.source = config['source']
        self.defaults = config.get('defaults', [])
        self._source_data = self._load_source()
    
    def _load_source(self) -> Dict:
        """Load source data file."""
        with open(self.source) as f:
            return yaml.safe_load(f)
    
    def enrich(self, frontmatter: Dict) -> Dict:
        """Enrich frontmatter with linked data."""
        if self.field not in frontmatter:
            return frontmatter
        
        enriched_items = []
        for item in frontmatter[self.field]:
            enriched_item = self._enrich_item(item)
            enriched_items.append(enriched_item)
        
        frontmatter[self.field] = enriched_items
        return frontmatter
    
    @abstractmethod
    def _enrich_item(self, item: Dict) -> Dict:
        """Enrich single linked item."""
        pass


class CompoundLinkageEnricher(BaseLinkageEnricher):
    """Enrich compound linkages (Phase 2 pattern)."""
    
    def _enrich_item(self, item: Dict) -> Dict:
        """Add missing fields from Compounds.yaml."""
        compound_id = item.get('id')
        if not compound_id:
            return item
        
        # Get compound data
        compound_data = self._source_data['compounds'].get(compound_id, {})
        
        # Add defaults if missing
        for field in self.defaults:
            if field not in item and field in compound_data:
                item[field] = compound_data[field]
        
        return item


class MaterialLinkageEnricher(BaseLinkageEnricher):
    """Enrich material linkages."""
    
    def _enrich_item(self, item: Dict) -> Dict:
        """Add missing fields from Materials.yaml."""
        material_id = item.get('id')
        if not material_id:
            return item
        
        material_data = self._source_data['materials'].get(material_id, {})
        
        for field in self.defaults:
            if field not in item and field in material_data:
                item[field] = material_data[field]
        
        return item


class ContaminantLinkageEnricher(BaseLinkageEnricher):
    """Enrich contaminant linkages."""
    
    def _enrich_item(self, item: Dict) -> Dict:
        """Add missing fields from Contaminants.yaml."""
        contaminant_id = item.get('id')
        if not contaminant_id:
            return item
        
        contaminant_data = self._source_data['contaminants'].get(contaminant_id, {})
        
        for field in self.defaults:
            if field not in item and field in contaminant_data:
                item[field] = contaminant_data[field]
        
        return item


class TimestampEnricher:
    """Add/update timestamp fields."""
    
    def __init__(self, config: Dict):
        self.fields = config['fields']
    
    def enrich(self, frontmatter: Dict) -> Dict:
        """Add timestamps."""
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        for field in self.fields:
            if field not in frontmatter:
                frontmatter[field] = timestamp
        
        return frontmatter
```

**Key Benefit**: Any domain can use any enricher - just configure it.

---

## 🎨 Universal Generator System

### Generator Registry

```python
# export/generation/registry.py

GENERATOR_REGISTRY = {
    'seo_description': SEODescriptionGenerator,
    'breadcrumb': BreadcrumbGenerator,
    'excerpt': ExcerptGenerator,
}

class SEODescriptionGenerator:
    """Generate SEO descriptions from content."""
    
    def __init__(self, config: Dict):
        self.source_field = config['source_field']
        self.output_field = config['output_field']
        self.max_length = config.get('max_length', 160)
    
    def generate(self, frontmatter: Dict) -> Dict:
        """Generate SEO description."""
        if self.source_field not in frontmatter:
            return frontmatter
        
        # Extract first sentence or truncate
        text = frontmatter[self.source_field]
        seo_desc = self._truncate(text, self.max_length)
        
        frontmatter[self.output_field] = seo_desc
        return frontmatter
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Smart truncate at word boundary."""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + '...'


class BreadcrumbGenerator:
    """Generate breadcrumb navigation."""
    
    def __init__(self, config: Dict):
        self.template = config['template']
    
    def generate(self, frontmatter: Dict) -> Dict:
        """Generate breadcrumb from template."""
        breadcrumb = self.template.format(**frontmatter)
        frontmatter['breadcrumb'] = breadcrumb
        return frontmatter
```

---

## 📦 Usage Examples

### CLI Usage (Unchanged)

```bash
# Export materials (uses export/config/materials.yaml)
python3 run.py --export materials

# Export contaminants (uses export/config/contaminants.yaml)
python3 run.py --export contaminants

# Export all domains
python3 run.py --export all
```

### Programmatic Usage

```python
# Old way (domain-specific classes)
from export.core.trivial_exporter import TrivialFrontmatterExporter
exporter = TrivialFrontmatterExporter()
exporter.export_all()

# New way (universal exporter)
from export.core.universal_exporter import UniversalFrontmatterExporter
from export.config import load_domain_config

config = load_domain_config('materials')
exporter = UniversalFrontmatterExporter(config)
exporter.export_all()
```

### Adding New Domain (Zero Code Changes)

```yaml
# export/config/industries.yaml (NEW DOMAIN)
domain: industries
source_file: data/industries/Industries.yaml
output_path: frontmatter/industries

items_key: industries
id_field: id
slug_field: slug

enrichments:
  - type: material_linkage
    field: compatible_materials
    source: data/materials/Materials.yaml
    defaults: [category, thermal_conductivity]

generators:
  - type: seo_description
    source_field: industry_description
    output_field: seo_description
  
  - type: breadcrumb
    template: "Home / Industries / {sector}"
```

**No Python code required** - just add config file.

---

## 🗺️ Migration Plan

### Phase 1: Create Universal Infrastructure (Day 1)

**Tasks**:
1. Create `export/core/universal_exporter.py` (300 lines)
2. Create enricher registry and base classes (200 lines)
3. Create generator registry and base classes (150 lines)
4. Create config loader utilities (50 lines)
5. Write comprehensive tests (200 lines)

**Total new code**: ~900 lines

**Files**:
- `export/core/universal_exporter.py`
- `export/enrichment/registry.py`
- `export/enrichment/linkage_enrichers.py`
- `export/generation/registry.py`
- `export/generation/content_generators.py`
- `export/config/loader.py`

### Phase 2: Create Domain Configs (Day 1-2)

**Tasks**:
1. Create `export/config/materials.yaml`
2. Create `export/config/contaminants.yaml`
3. Create `export/config/compounds.yaml`
4. Create `export/config/settings.yaml`
5. Test each config produces identical output

**Total new code**: ~200 lines (YAML configs)

### Phase 3: Update CLI/Orchestrator (Day 2)

**Tasks**:
1. Update `run.py` to use universal exporter
2. Update `export/orchestrator.py` to load configs
3. Maintain backward compatibility (optional flag)
4. Update documentation

**Modified files**:
- `run.py`
- `export/orchestrator.py`

### Phase 4: Test & Verify (Day 2-3)

**Tasks**:
1. Run all exporters side-by-side
2. Diff old vs new frontmatter files (should be identical)
3. Run integration tests
4. Fix any discrepancies
5. Performance testing

**Verification script**:
```bash
# Export with old system
python3 run.py --export materials --output-dir old/

# Export with new system
python3 run.py --export materials --use-universal --output-dir new/

# Compare
diff -r old/ new/
```

### Phase 5: Deprecate Old System (Day 3)

**Tasks**:
1. Mark old exporters as deprecated
2. Add deprecation warnings
3. Update all documentation
4. Plan removal date (30 days)

**Files to deprecate**:
- `export/core/trivial_exporter.py` (2,115 lines) → DELETE
- `export/contaminants/trivial_exporter.py` (372 lines) → DELETE
- `export/compounds/trivial_exporter.py` (230 lines) → DELETE
- `export/settings/trivial_exporter.py` (278 lines) → DELETE

**Keep**:
- `export/core/base_trivial_exporter.py` (for reference, mark deprecated)

---

## 📊 Before vs After Comparison

### Code Size

| Component | Before | After | Reduction |
|-----------|--------|-------|-----------|
| Domain exporters | 2,995 lines | 0 lines | 100% |
| Base exporter | 290 lines | 0 lines | 100% |
| Universal exporter | 0 lines | 300 lines | NEW |
| Enrichers | 0 lines | 200 lines | NEW |
| Generators | 0 lines | 150 lines | NEW |
| Config loader | 0 lines | 50 lines | NEW |
| Domain configs | 0 lines | 200 lines | NEW |
| **Total** | **3,285 lines** | **900 lines** | **73% reduction** |

### Maintenance Burden

| Task | Before | After |
|------|--------|-------|
| Add new domain | Write 300-line exporter | Add 50-line config |
| Fix export bug | Fix in 4 files | Fix once |
| Add enrichment | Copy/paste to 4 files | Add to 1 registry |
| Test changes | Test 4 exporters | Test 1 exporter |
| Update logic | Update 4 classes | Update 1 class |

### Testing

| Metric | Before | After |
|--------|--------|-------|
| Test files | 4 (one per domain) | 1 (universal) + configs |
| Lines of test code | ~800 lines | ~300 lines |
| Coverage target | 4 exporters | 1 exporter |
| Integration tests | 4 scenarios | 1 scenario × 4 configs |

---

## ✅ Benefits

### 1. **Massive Code Reduction**
- 3,285 → 900 lines (73% less code)
- Fewer files to maintain
- Less cognitive load

### 2. **Consistent Behavior**
- All domains work exactly the same way
- No subtle differences between exporters
- Predictable behavior

### 3. **Easier Debugging**
- Fix bug once, works everywhere
- Single codebase to understand
- Better test coverage

### 4. **Faster Development**
- Add new domain: 30 minutes (config file)
- Add new enrichment: 1 hour (one class)
- Add new generator: 1 hour (one class)

### 5. **Better Testing**
- Test universal exporter thoroughly once
- Config files are data (easy to validate)
- Integration tests cover all domains automatically

### 6. **Extensibility**
- Plugin architecture for enrichers/generators
- Easy to add custom domain logic
- No code modification needed

### 7. **Documentation**
- Config files are self-documenting
- Easier to understand domain behavior
- Clear separation of concerns

---

## ⚠️ Risks & Mitigation

### Risk 1: Breaking Changes

**Risk**: New system produces different output  
**Mitigation**:
- Run old/new side-by-side during transition
- Diff all output files
- 30-day deprecation period
- Rollback plan (keep old code)

### Risk 2: Performance Regression

**Risk**: Generic code slower than specialized  
**Mitigation**:
- Benchmark before/after
- Profile hotspots
- Cache loaded configs
- Lazy load source data

### Risk 3: Lost Domain-Specific Features

**Risk**: Some custom logic can't be configured  
**Mitigation**:
- Audit all existing exporters for unique features
- Add plugin system for custom processors
- Document migration of special cases
- Keep old code as reference

### Risk 4: Config Complexity

**Risk**: YAML configs become too complex  
**Mitigation**:
- Keep configs simple (principle of least power)
- Provide config validation tool
- Document config schema
- Provide config templates

### Risk 5: Learning Curve

**Risk**: Team needs to learn new system  
**Mitigation**:
- Comprehensive documentation
- Migration guide
- Training session
- Gradual rollout (one domain at a time)

---

## 📈 Success Metrics

### Code Metrics
- [ ] Export system code reduced by 70%+
- [ ] Test code reduced by 60%+
- [ ] Zero duplicated export logic

### Quality Metrics
- [ ] 100% output parity with old system
- [ ] All integration tests passing
- [ ] Performance within 10% of old system

### Developer Experience
- [ ] Add new domain in <30 minutes
- [ ] Add new enrichment in <1 hour
- [ ] Bug fixes applied universally

### Documentation
- [ ] Complete config schema docs
- [ ] Migration guide published
- [ ] All domain configs documented

---

## 🚀 Implementation Timeline

| Phase | Duration | Effort | Status |
|-------|----------|--------|--------|
| Phase 1: Universal infrastructure | 8 hours | 1 day | 📋 TODO |
| Phase 2: Domain configs | 4 hours | 0.5 day | 📋 TODO |
| Phase 3: CLI updates | 3 hours | 0.5 day | 📋 TODO |
| Phase 4: Testing & verification | 8 hours | 1 day | 📋 TODO |
| Phase 5: Deprecation | 1 hour | 0.1 day | 📋 TODO |
| **Total** | **24 hours** | **3 days** | 📋 PROPOSAL |

**Rollout Strategy**:
- Week 1: Implement universal system
- Week 2: Test with one domain (compounds - smallest)
- Week 3: Migrate all domains
- Week 4: Deprecate old system
- Week 5: Remove old code

---

## 📚 Related Work

**Builds On**:
- ✅ Schema 5.0.0 - Flattened relationships structure
- ✅ Phase 2 - Compound enrichment pattern (proven architecture)
- ✅ Field ordering centralization (FrontmatterFieldOrderValidator)
- ✅ Base class inheritance (BaseTrivialExporter patterns)

**Enables**:
- Universal enrichment for all linkage types
- Rapid new domain onboarding
- Consistent frontmatter generation
- Easier maintenance and testing

---

## 🎯 Decision Points

### Option A: Full Consolidation (Recommended)
- Implement universal exporter
- Convert all domains to configs
- Deprecate old exporters
- **Effort**: 3 days
- **Benefit**: 73% code reduction

### Option B: Gradual Migration
- Keep old exporters
- Add universal system alongside
- Migrate domains one-by-one over 3 months
- **Effort**: 3 days + 3 months
- **Benefit**: Lower risk, slower payoff

### Option C: Hybrid Approach
- Universal exporter for new domains
- Keep existing exporters as-is
- **Effort**: 2 days
- **Benefit**: 0% reduction now, future benefit

### Recommendation: **Option A - Full Consolidation**

**Rationale**:
- Maximum code reduction
- Consistent architecture
- Worth the 3-day investment
- Old system already working (low risk)
- Can rollback if issues found

---

## 📝 Next Steps

1. **Review & approve** this proposal
2. **Create implementation branch**: `feat/export-consolidation`
3. **Implement Phase 1** (universal infrastructure)
4. **Test with one domain** (compounds as pilot)
5. **Migrate remaining domains** if pilot successful
6. **Document & train** team on new system
7. **Deprecate old system** after 30 days
8. **Remove old code** after deprecation period

---

## 📖 Appendix: Example Code

### Complete Universal Exporter (Simplified)

```python
# export/core/universal_exporter.py

from pathlib import Path
from typing import Dict, Any, List
import yaml
from export.enrichment.registry import ENRICHER_REGISTRY
from export.generation.registry import GENERATOR_REGISTRY
from shared.validation.field_order import FrontmatterFieldOrderValidator

class UniversalFrontmatterExporter:
    """
    Universal configuration-driven frontmatter exporter.
    
    Replaces all domain-specific exporters with single universal implementation.
    Domain behavior configured via YAML files in export/config/.
    """
    
    def __init__(self, config_path: str):
        """Initialize with domain configuration."""
        self.config = self._load_config(config_path)
        self.domain = self.config['domain']
        self.source_file = Path(self.config['source_file'])
        self.output_path = Path(self.config['output_path'])
        self.enrichments = self.config.get('enrichments', [])
        self.generators = self.config.get('generators', [])
        self.items_key = self.config.get('items_key', self.domain)
        
        # Initialize enrichers
        self.enrichers = [
            ENRICHER_REGISTRY[e['type']](e)
            for e in self.enrichments
        ]
        
        # Initialize generators
        self.content_generators = [
            GENERATOR_REGISTRY[g['type']](g)
            for g in self.generators
        ]
        
        # Field ordering validator
        self.field_validator = FrontmatterFieldOrderValidator()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load domain configuration."""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def _load_domain_data(self) -> Dict[str, Any]:
        """Load source data from YAML."""
        with open(self.source_file) as f:
            return yaml.safe_load(f)
    
    def export_single(self, item_id: str, item_data: Dict, force: bool = False) -> bool:
        """
        Export single item to frontmatter.
        
        Workflow:
        1. Build base frontmatter from item data
        2. Apply all configured enrichments
        3. Apply all configured generators
        4. Validate and order fields
        5. Write to file
        """
        output_file = self.output_path / f"{item_id}.yaml"
        
        # Skip if exists and not forced
        if not force and output_file.exists():
            return False
        
        # Build base frontmatter
        frontmatter = self._build_base_frontmatter(item_data)
        
        # Apply enrichments
        for enricher in self.enrichers:
            frontmatter = enricher.enrich(frontmatter)
        
        # Apply generators
        for generator in self.content_generators:
            frontmatter = generator.generate(frontmatter)
        
        # Validate and order fields
        frontmatter = self.field_validator.apply_field_order(frontmatter)
        
        # Write to file
        self._write_frontmatter(output_file, frontmatter)
        
        return True
    
    def export_all(self, force: bool = True) -> Dict[str, bool]:
        """Export all items in domain."""
        results = {}
        data = self._load_domain_data()
        
        # Get items from configured key
        items = data.get(self.items_key, {})
        
        for item_id, item_data in items.items():
            try:
                results[item_id] = self.export_single(item_id, item_data, force)
            except Exception as e:
                logger.error(f"Failed to export {item_id}: {e}")
                results[item_id] = False
        
        return results
    
    def _build_base_frontmatter(self, item_data: Dict) -> Dict:
        """Build base frontmatter structure from item data."""
        # Copy all fields from source data
        frontmatter = dict(item_data)
        
        # Ensure required fields
        frontmatter.setdefault('schema_version', '5.0.0')
        frontmatter.setdefault('content_type', self.domain)
        
        return frontmatter
    
    def _write_frontmatter(self, output_file: Path, frontmatter: Dict) -> None:
        """Write frontmatter to YAML file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            yaml.dump(
                frontmatter,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
```

**Total**: ~150 lines replaces 3,285 lines across 4 exporters.

---

**Proposal Status**: 📋 AWAITING APPROVAL  
**Estimated ROI**: 73% code reduction for 3 days work  
**Recommendation**: APPROVE and implement immediately
