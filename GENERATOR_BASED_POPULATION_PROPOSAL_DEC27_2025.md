# Generator-Based Source Data Population Proposal

**Date**: December 27, 2025  
**Status**: Proposal  
**Goal**: Shift from runtime enrichment to pre-populated source data

---

## 📋 Executive Summary

### Current Architecture: Enrichment During Export

```
Source YAML (Materials.yaml)
  ↓ [Load - partial data]
Export System
  ↓ [Enrich - compute 51 types of fields]
  ↓ [Generate - create 8 types of content]
  ↓ [Validate - check completeness]
Frontmatter Files (complete data)
```

**Problems**:
- Computation happens every export (~2-5 minutes)
- Enriched data not in version control
- Can't validate source data completeness
- Different systems (datasets vs frontmatter) may compute differently

### Proposed Architecture: Generator-Based Population

```
Source YAML (Materials.yaml)
  ↑ [Generators populate ALL fields]
  ↑ [Computed fields stored in source]
  ↓ [Export - simple field copy]
Frontmatter Files (trivial copy)
```

**Benefits**:
- ✅ Single source of truth (ALL data in YAML)
- ✅ Faster exports (no computation, just copy)
- ✅ Version control for computed fields
- ✅ Validate source data completeness
- ✅ Consistent data across all systems
- ✅ Simpler export code (remove enrichers)

---

## 🔄 Fields to Move from Enrichment → Generation

### Category 1: Identifiers & URLs (CRITICAL)

**Current**: Computed during export by enrichers  
**Proposed**: Generated and stored in source YAML

```yaml
# Materials.yaml - BEFORE (current)
materials:
  aluminum-laser-cleaning:
    name: "Aluminum"
    category: "metal"
    # No slug, no URLs

# Materials.yaml - AFTER (with generators)
materials:
  aluminum-laser-cleaning:
    name: "Aluminum"
    category: "metal"
    slug: "aluminum-laser-cleaning"  # ← Generated
    url: "/materials/metal/aluminum-laser-cleaning"  # ← Generated
    canonical_url: "https://www.z-beam.com/materials/metal/aluminum-laser-cleaning"  # ← Generated
```

**Generators Needed**:
1. `SlugGenerator` - Derive slug from name/id
2. `URLGenerator` - Build URLs from slug + category hierarchy
3. `CanonicalURLGenerator` - Add domain to create absolute URLs

---

### Category 2: Breadcrumbs (HIGH PRIORITY)

**Current**: Computed during export (BreadcrumbEnricher)  
**Proposed**: Generated and stored in source YAML

```yaml
# AFTER (with generator)
materials:
  aluminum-laser-cleaning:
    breadcrumb:  # ← Generated
      - label: "Home"
        href: "/"
      - label: "Materials"
        href: "/materials"
      - label: "Metal"
        href: "/materials/metal"
      - label: "Aluminum"
        href: "/materials/metal/aluminum-laser-cleaning"
    full_path: "/materials/metal/aluminum-laser-cleaning"  # ← Generated
```

**Generator Needed**:
- `BreadcrumbGenerator` - Build hierarchical navigation

---

### Category 3: Author References (MEDIUM PRIORITY)

**Current**: Resolved during export (AuthorEnricher)  
**Proposed**: Generated and stored in source YAML

```yaml
# BEFORE (current)
materials:
  aluminum-laser-cleaning:
    author:
      id: "todd-dunning"  # Only ID stored

# AFTER (with generator)
materials:
  aluminum-laser-cleaning:
    author:  # ← Fully resolved
      id: "todd-dunning"
      name: "Todd Dunning"
      nationality: "United States"
      bio: "Laser cleaning specialist..."
      url: "/authors/todd-dunning"
```

**Generator Needed**:
- `AuthorReferenceGenerator` - Resolve author ID to complete object

---

### Category 4: Relationship Metadata (HIGH PRIORITY)

**Current**: Computed during export (multiple enrichers)  
**Proposed**: Generated and stored in source YAML

```yaml
# BEFORE (current)
materials:
  aluminum-laser-cleaning:
    relationships:
      related_contaminants:
        - id: "rust-oxidation-contamination"
          # No URL, no slug, no section metadata

# AFTER (with generators)
materials:
  aluminum-laser-cleaning:
    relationships:
      related_contaminants:
        - id: "rust-oxidation-contamination"
          name: "Rust & Oxidation"  # ← Generated (looked up)
          slug: "rust-oxidation-contamination"  # ← Generated
          url: "/contaminants/rust-oxidation-contamination"  # ← Generated
          intensity: "common"  # ← Generated (from associations)
          _section:  # ← Generated
            title: "Common Contaminants"
            description: "Frequently encountered contamination"
            icon: "alert-circle"
            order: 1
            variant: "warning"
```

**Generators Needed**:
1. `RelationshipSlugGenerator` - Add slugs to all relationships
2. `RelationshipURLGenerator` - Add URLs to all relationships
3. `RelationshipNameGenerator` - Look up names from target domain
4. `RelationshipIntensityGenerator` - Compute intensity from associations
5. `SectionMetadataGenerator` - Add section grouping metadata

---

### Category 5: Library Fields (MEDIUM PRIORITY)

**Current**: Processed during export (LibraryEnrichers)  
**Proposed**: Generated and stored in source YAML

```yaml
# Library field processing
materials:
  aluminum-laser-cleaning:
    laser_properties:
      # Processed and formatted library data stored here
```

**Generator Needed**:
- `LibraryFieldGenerator` - Process and format library data

---

### Category 6: Grouping Metadata (LOW PRIORITY)

**Current**: Computed during export  
**Proposed**: May not be needed if relationships are fully populated

**Evaluation**: If relationships are complete with all metadata, grouping enrichers may become unnecessary.

---

## 🏗️ Implementation Architecture

### Generator System Structure

```
scripts/generators/
├── __init__.py
├── base_generator.py          # Abstract base for all generators
├── coordinator.py              # Orchestrates generator execution
├── identifiers/
│   ├── slug_generator.py       # Generate slugs
│   ├── url_generator.py        # Generate URLs
│   └── canonical_url_generator.py
├── navigation/
│   └── breadcrumb_generator.py # Generate breadcrumbs
├── references/
│   └── author_generator.py     # Resolve author references
├── relationships/
│   ├── slug_generator.py       # Add slugs to relationships
│   ├── url_generator.py        # Add URLs to relationships
│   ├── name_generator.py       # Look up names
│   ├── intensity_generator.py  # Compute intensity
│   └── section_metadata_generator.py
└── library/
    └── field_generator.py      # Process library fields
```

### Base Generator Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseGenerator(ABC):
    """
    Abstract base for all source data generators.
    
    Generators populate computed fields in source YAML files.
    Unlike enrichers (which run during export), generators
    run independently and modify source data directly.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and populate fields in source data.
        
        Args:
            data: Domain data dict (e.g., all materials)
        
        Returns:
            Updated data dict with generated fields
        """
        pass
    
    @abstractmethod
    def get_generated_fields(self) -> List[str]:
        """
        Return list of field names this generator populates.
        
        Used for validation and documentation.
        """
        pass
    
    def validate_dependencies(self, data: Dict[str, Any]) -> bool:
        """
        Check if required fields exist for generation.
        
        Returns:
            True if all dependencies satisfied
        """
        return True
```

### Generator Coordinator

```python
class GeneratorCoordinator:
    """
    Orchestrate execution of multiple generators.
    
    Handles:
    - Dependency ordering (slugs before URLs)
    - Incremental updates (only changed items)
    - Validation (all fields generated)
    - Atomic writes (backup + write + verify)
    """
    
    def __init__(self, domain: str):
        self.domain = domain
        self.generators = []
    
    def register_generator(self, generator: BaseGenerator, dependencies: List[str] = None):
        """Register generator with optional dependencies"""
        self.generators.append({
            'generator': generator,
            'dependencies': dependencies or []
        })
    
    def generate_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all generators in dependency order.
        
        Returns:
            Fully populated data
        """
        # Sort by dependencies
        ordered = self._topological_sort()
        
        # Execute each generator
        for gen_info in ordered:
            generator = gen_info['generator']
            data = generator.generate(data)
        
        return data
    
    def _topological_sort(self) -> List[Dict]:
        """Sort generators by dependency order"""
        # Implementation of topological sort
        pass
```

---

## 📝 Example Generators

### 1. SlugGenerator

```python
class SlugGenerator(BaseGenerator):
    """Generate slug fields from name/id"""
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        for item_id, item_data in data.items():
            # Slug is usually the item_id (already slugified)
            if 'slug' not in item_data:
                item_data['slug'] = item_id
        return data
    
    def get_generated_fields(self) -> List[str]:
        return ['slug']
```

### 2. URLGenerator

```python
class URLGenerator(BaseGenerator):
    """Generate URL fields from slug + category hierarchy"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.domain = config['domain']  # materials, contaminants, etc.
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        for item_id, item_data in data.items():
            slug = item_data.get('slug', item_id)
            category = item_data.get('category', '')
            subcategory = item_data.get('subcategory', '')
            
            # Build URL path
            parts = [self.domain]
            if category:
                parts.append(category.lower())
            if subcategory:
                parts.append(subcategory.lower())
            parts.append(slug)
            
            item_data['url'] = '/' + '/'.join(parts)
        
        return data
    
    def get_generated_fields(self) -> List[str]:
        return ['url']
    
    def validate_dependencies(self, data: Dict[str, Any]) -> bool:
        # Requires slug field
        return all('slug' in item for item in data.values())
```

### 3. BreadcrumbGenerator

```python
class BreadcrumbGenerator(BaseGenerator):
    """Generate breadcrumb navigation arrays"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.domain = config['domain']
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        for item_id, item_data in data.items():
            breadcrumb = [{"label": "Home", "href": "/"}]
            
            # Add domain
            breadcrumb.append({
                "label": self.domain.capitalize(),
                "href": f"/{self.domain}"
            })
            
            # Add category
            category = item_data.get('category', '')
            if category:
                breadcrumb.append({
                    "label": category.replace('-', ' ').title(),
                    "href": f"/{self.domain}/{category}"
                })
            
            # Add subcategory
            subcategory = item_data.get('subcategory', '')
            if subcategory:
                breadcrumb.append({
                    "label": subcategory.replace('-', ' ').title(),
                    "href": f"/{self.domain}/{category}/{subcategory}"
                })
            
            # Add current item
            name = item_data.get('name', '')
            url = item_data.get('url', '')
            if name and url:
                breadcrumb.append({
                    "label": name,
                    "href": url
                })
            
            item_data['breadcrumb'] = breadcrumb
            if url:
                item_data['full_path'] = url
        
        return data
    
    def get_generated_fields(self) -> List[str]:
        return ['breadcrumb', 'full_path']
    
    def validate_dependencies(self, data: Dict[str, Any]) -> bool:
        # Requires url field
        return all('url' in item for item in data.values())
```

---

## 🔧 Usage

### Command-Line Interface

```bash
# Generate all fields for all domains
python3 scripts/generators/generate_all.py

# Generate for specific domain
python3 scripts/generators/generate_all.py --domain materials

# Generate specific field types
python3 scripts/generators/generate_all.py --domain materials --generators slug,url,breadcrumb

# Dry run (show what would be generated)
python3 scripts/generators/generate_all.py --dry-run

# Incremental (only items missing fields)
python3 scripts/generators/generate_all.py --incremental
```

### Python API

```python
from scripts.generators.coordinator import GeneratorCoordinator
from scripts.generators.identifiers import SlugGenerator, URLGenerator
from scripts.generators.navigation import BreadcrumbGenerator

# Initialize coordinator
coordinator = GeneratorCoordinator('materials')

# Register generators in dependency order
coordinator.register_generator(SlugGenerator(config))
coordinator.register_generator(URLGenerator(config), dependencies=['slug'])
coordinator.register_generator(BreadcrumbGenerator(config), dependencies=['url'])

# Load source data
data = load_materials_yaml()

# Generate all fields
populated_data = coordinator.generate_all(data)

# Save back to YAML
save_materials_yaml(populated_data)
```

---

## 📊 Impact Analysis

### Before: Enrichment During Export

**Export Process**:
1. Load Materials.yaml (~2MB, 153 items)
2. Run 51 enrichers (compute fields)
3. Run 8 generators (create content)
4. Write frontmatter files
5. **Time**: 2-5 minutes

**Export Code Size**: ~1.4MB (51 enrichers + 8 generators)

**Source Data Size**: ~2MB (core data only)

**Frontmatter Size**: ~4MB (core + enriched data)

### After: Generator-Based Population

**Generate Process** (one-time or on data changes):
1. Load Materials.yaml (~2MB, 153 items)
2. Run 10-15 generators (populate fields)
3. Save updated Materials.yaml
4. **Time**: 1-2 minutes (one-time)

**Export Process**:
1. Load Materials.yaml (~4MB, 153 items with all fields)
2. Simple field mapping (no computation)
3. Write frontmatter files
4. **Time**: 10-30 seconds ✅

**Generator Code Size**: ~200KB (10-15 simple generators)

**Export Code Size**: ~100KB (just field mapping) ✅

**Source Data Size**: ~4MB (core + computed data) ⚠️ Larger

**Frontmatter Size**: ~4MB (unchanged)

### Net Impact

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Export time | 2-5 min | 10-30 sec | ✅ 10x faster |
| Export code | 1.4MB | 100KB | ✅ 93% reduction |
| Source YAML size | 2MB | 4MB | ⚠️ 2x larger |
| Frontmatter size | 4MB | 4MB | ✅ No change |
| Git tracking | Core only | All data | ✅ Better |
| Validation | Export time | Any time | ✅ Better |

---

## 🚦 Migration Plan

### Phase 1: Foundation (Week 1)

**Goal**: Create generator infrastructure

1. Create `scripts/generators/` directory structure
2. Implement `BaseGenerator` abstract class
3. Implement `GeneratorCoordinator` with dependency ordering
4. Add CLI interface (`generate_all.py`)

**Deliverables**:
- Generator framework ready
- No generators implemented yet
- Tests for coordinator

### Phase 2: Core Generators (Week 2)

**Goal**: Implement essential generators

1. `SlugGenerator` - Add slugs
2. `URLGenerator` - Add URLs (depends on slug)
3. `CanonicalURLGenerator` - Add canonical URLs (depends on URL)
4. `BreadcrumbGenerator` - Add breadcrumbs (depends on URL)

**Deliverables**:
- 4 core generators working
- Materials.yaml has slug, url, canonical_url, breadcrumb fields
- Tests for each generator

### Phase 3: Reference Generators (Week 3)

**Goal**: Resolve references

1. `AuthorReferenceGenerator` - Resolve author IDs
2. `RelationshipSlugGenerator` - Add slugs to relationships
3. `RelationshipURLGenerator` - Add URLs to relationships
4. `RelationshipNameGenerator` - Look up relationship names

**Deliverables**:
- 4 reference generators working
- Relationships fully populated
- Tests for each generator

### Phase 4: Advanced Generators (Week 4)

**Goal**: Complete metadata

1. `RelationshipIntensityGenerator` - Compute intensity scores
2. `SectionMetadataGenerator` - Add section grouping
3. `LibraryFieldGenerator` - Process library data

**Deliverables**:
- 3 advanced generators working
- All computed fields in source YAML
- Tests complete

### Phase 5: Export Simplification (Week 5)

**Goal**: Remove enrichers from export system

1. Verify all fields in source YAML
2. Update frontmatter exporter to simple field mapping
3. Remove enrichers (archive, don't delete)
4. Update tests
5. Benchmark export time

**Deliverables**:
- Export system simplified
- Enrichers archived
- Export time <30 seconds
- All tests passing

### Phase 6: Documentation & Rollout (Week 6)

**Goal**: Document and train

1. Update all documentation
2. Create migration guide
3. Update workflows (generate before export)
4. Train developers on new system

**Deliverables**:
- Complete documentation
- Migration guide
- Workflow updates
- System fully operational

---

## ⚠️ Risks & Mitigation

### Risk 1: Source YAML Size Doubles

**Risk**: YAML files grow from 2MB → 4MB with computed fields

**Impact**: 
- Slower git operations
- Larger commits
- More merge conflicts

**Mitigation**:
- Computed fields in separate section (easier to ignore in diffs)
- Git LFS for large YAML files (if needed)
- Incremental generation (only update changed items)

**Assessment**: ⚠️ Acceptable trade-off for benefits

---

### Risk 2: Generator Order Dependencies

**Risk**: Generators depend on each other (URL needs slug, breadcrumb needs URL)

**Impact**: 
- Complex dependency management
- Errors if run out of order

**Mitigation**:
- GeneratorCoordinator handles dependency ordering
- Topological sort ensures correct execution
- Clear error messages if dependencies missing

**Assessment**: ✅ Solvable with coordinator

---

### Risk 3: Migration Complexity

**Risk**: Migrating from enrichers to generators requires code changes across system

**Impact**: 
- Time investment (6 weeks)
- Risk of bugs during transition
- Need to maintain both systems temporarily

**Mitigation**:
- Phased rollout (generators first, keep enrichers)
- Verify generated data matches enriched data
- Only remove enrichers when verified
- Comprehensive testing

**Assessment**: ⚠️ Manageable with careful planning

---

### Risk 4: Incremental Updates

**Risk**: When material name changes, need to regenerate computed fields

**Impact**: 
- Additional workflow step
- Potential for stale data

**Mitigation**:
- Pre-commit hook to run generators
- CI checks for field completeness
- Incremental mode (only update changed items)
- Clear warnings if fields outdated

**Assessment**: ✅ Automatable

---

## ✅ Success Criteria

### Functional Success

- [ ] All computed fields stored in source YAML
- [ ] Export time <30 seconds (was 2-5 minutes)
- [ ] Zero enrichers needed during export
- [ ] Dataset and frontmatter systems use identical data

### Code Quality Success

- [ ] Export code reduced by 90% (1.4MB → 100KB)
- [ ] Generator code clean and testable
- [ ] Comprehensive test coverage
- [ ] Clear documentation

### Data Quality Success

- [ ] 100% field population (no missing computed fields)
- [ ] Consistent data across all outputs
- [ ] Version control tracks all changes
- [ ] Validation passes on source data

---

## 📚 Related Documentation

- `SYSTEM_OPTIMIZATION_ANALYSIS_DEC27_2025.md` - Overall system optimization
- `export/README.md` - Current trivial export architecture
- `docs/data/DATA_STORAGE_POLICY.md` - Data storage principles
- `NAMING_AUDIT_DEC26_2025.md` - Related naming improvements

---

## 🎯 Recommendation

### Recommended Approach: Phased Implementation

**Priority**: ⭐⭐⭐⭐⭐ HIGH

**Rationale**:
1. Aligns with "trivial export" philosophy
2. Single source of truth for all data
3. Massive performance improvement (10x faster exports)
4. Simpler codebase (90% reduction in export code)
5. Better validation and debugging
6. Consistent data across systems

**Timeline**: 6 weeks for complete implementation

**Effort**: High (new system, migration required)

**Risk**: Medium (manageable with phased approach)

**ROI**: Very High (permanent simplification + performance gains)

### Alternative: Hybrid Approach

Keep lightweight enrichers for simple fields (slugs, URLs) but populate complex fields (relationships, breadcrumbs) via generators.

**Pros**: Lower risk, faster implementation  
**Cons**: Still have two systems, less consistent

---

**Next Steps**:
1. Review this proposal
2. Approve architecture
3. Begin Phase 1 (generator infrastructure)
4. Implement core generators
5. Validate against current system
6. Migrate gradually

---

**Generated**: December 27, 2025  
**Author**: GitHub Copilot  
**Status**: Awaiting approval
