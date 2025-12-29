# Permanent Data Population Architecture
**Date:** December 26, 2025  
**Status:** Proposal  
**Purpose:** Use generators to populate source YAML data permanently instead of temporary enrichment during export

---

## Current Problem

### Enrichers (Temporary)
- **When they run:** During export (every time)
- **Where data goes:** Frontmatter files only (temporary)
- **Persistence:** Not saved to source YAML
- **Issue:** Same enrichment work repeated on every export

```
Source YAML (missing data)
    ↓ export
Enrichers add data temporarily
    ↓
Frontmatter (enriched)
    ↓ next export
Enrichers run again (wasted work)
```

### Generators (Also Temporary)
- **When they run:** During export (every time)
- **Where data goes:** Frontmatter files only (temporary)
- **Persistence:** Not saved to source YAML
- **Issue:** Derived content regenerated on every export

---

## Proposed Solution: Permanent Population Generators

### Concept: "Backfill Generators"
Run generators that **write back to source YAML files**, making enrichment permanent.

```
Source YAML (missing data)
    ↓
Backfill Generator (one-time)
    ↓
Source YAML (populated permanently)
    ↓ future exports
No enrichers needed (data already present)
```

---

## Architecture Design

### 1. New Module: `generation/backfill/`

```
generation/backfill/
├── __init__.py
├── base.py                          # BaseBackfillGenerator
├── registry.py                      # Generator registry
├── author_backfill.py               # Add author details
├── compound_linkage_backfill.py     # Add compound details
├── contaminant_linkage_backfill.py  # Add contaminant details
├── intensity_backfill.py            # Add intensity ranges
└── section_metadata_backfill.py     # Add section metadata
```

### 2. Base Class

```python
# generation/backfill/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict
import yaml

class BaseBackfillGenerator(ABC):
    """
    Base class for generators that populate source YAML permanently.
    
    Unlike export enrichers (temporary), backfill generators:
    1. Read source YAML files
    2. Generate/enrich data
    3. Write back to source YAML (permanent)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize backfill generator.
        
        Args:
            config: Generator config with source_file, field, etc.
        """
        self.config = config
        self.source_file = Path(config['source_file'])
        self.field = config.get('field')
        self.dry_run = config.get('dry_run', False)
        
    @abstractmethod
    def populate(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate/enrich data for one item.
        
        Args:
            item_data: Item dict from source YAML
        
        Returns:
            Modified item dict (with new/enriched fields)
        """
        pass
    
    def backfill_all(self) -> Dict[str, int]:
        """
        Backfill all items in source YAML file.
        
        Returns:
            Stats dict: {processed, modified, skipped, errors}
        """
        # Load source YAML
        data = self._load_source()
        items = data[self.config['items_key']]
        
        stats = {'processed': 0, 'modified': 0, 'skipped': 0, 'errors': 0}
        
        # Process each item
        for item_id, item_data in items.items():
            try:
                # Check if already populated
                if self._should_skip(item_data):
                    stats['skipped'] += 1
                    continue
                
                # Generate/enrich data
                modified_data = self.populate(item_data)
                
                # Update in-memory data
                items[item_id] = modified_data
                stats['processed'] += 1
                stats['modified'] += 1
                
            except Exception as e:
                stats['errors'] += 1
                print(f"❌ Error processing {item_id}: {e}")
        
        # Write back to source YAML (if not dry run)
        if not self.dry_run and stats['modified'] > 0:
            self._write_source(data)
            print(f"💾 Saved {stats['modified']} changes to {self.source_file}")
        
        return stats
    
    def _should_skip(self, item_data: Dict[str, Any]) -> bool:
        """Check if item already has the field populated."""
        if not self.field:
            return False
        return self.field in item_data and item_data[self.field]
    
    def _load_source(self) -> Dict[str, Any]:
        """Load source YAML file."""
        with open(self.source_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _write_source(self, data: Dict[str, Any]) -> None:
        """Write data back to source YAML file (atomic write)."""
        # Atomic write: write to temp file, then rename
        temp_file = self.source_file.with_suffix('.tmp')
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
        
        # Atomic rename
        temp_file.replace(self.source_file)
```

### 3. Example Backfill Generator

```python
# generation/backfill/compound_linkage_backfill.py
from pathlib import Path
from typing import Any, Dict, List
import yaml

from generation.backfill.base import BaseBackfillGenerator


class CompoundLinkageBackfillGenerator(BaseBackfillGenerator):
    """
    Permanently populate compound linkage data in source YAML.
    
    Reads compounds library and adds full compound details to
    materials' produces_compounds relationships.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.compounds_file = Path(config['compounds_source'])
        self.compounds_data = self._load_compounds()
        self.default_fields = config.get('defaults', [])
    
    def _load_compounds(self) -> Dict[str, Any]:
        """Load compounds library."""
        with open(self.compounds_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data['compounds']
    
    def populate(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add full compound details to produces_compounds relationships.
        
        Before:
            produces_compounds:
              - compound_id: hydrogen-fluoride
              
        After:
            produces_compounds:
              - compound_id: hydrogen-fluoride
                name: Hydrogen Fluoride
                chemical_formula: HF
                cas_number: 7664-39-3
                hazard_class: Highly Toxic
                exposure_limits: {...}
                control_measures: {...}
        """
        # Get produces_compounds relationships
        relationships = item_data.get('produces_compounds', [])
        
        if not relationships:
            return item_data
        
        # Enrich each relationship
        enriched = []
        for rel in relationships:
            compound_id = rel.get('compound_id')
            
            if not compound_id:
                enriched.append(rel)
                continue
            
            # Get compound data from library
            compound = self.compounds_data.get(compound_id)
            
            if not compound:
                print(f"⚠️  Compound not found: {compound_id}")
                enriched.append(rel)
                continue
            
            # Add default fields from library
            enriched_rel = dict(rel)
            for field in self.default_fields:
                if field not in enriched_rel and field in compound:
                    enriched_rel[field] = compound[field]
            
            enriched.append(enriched_rel)
        
        # Update item data
        item_data['produces_compounds'] = enriched
        return item_data
```

### 4. CLI Integration

```python
# run.py additions

def backfill_command(args):
    """Execute backfill command to populate source YAML permanently"""
    
    from generation.backfill.registry import BackfillRegistry
    
    # Load backfill configuration
    config_file = Path(f'generation/backfill/config/{args.domain}.yaml')
    if not config_file.exists():
        print(f"❌ Error: No backfill config for domain: {args.domain}")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Run specific generator or all
    if args.generator:
        generator_config = next(
            (g for g in config['generators'] if g['type'] == args.generator),
            None
        )
        if not generator_config:
            print(f"❌ Error: Generator not found: {args.generator}")
            sys.exit(1)
        
        generator = BackfillRegistry.create(generator_config)
        stats = generator.backfill_all()
        
        print(f"\n✅ Backfill complete: {stats['modified']} items modified")
        
    else:
        # Run all generators
        total_modified = 0
        for gen_config in config['generators']:
            generator = BackfillRegistry.create(gen_config)
            stats = generator.backfill_all()
            total_modified += stats['modified']
        
        print(f"\n✅ All backfills complete: {total_modified} total modifications")
```

### 5. Configuration Files

```yaml
# generation/backfill/config/materials.yaml
domain: materials
source_file: data/materials/Materials.yaml
items_key: materials

generators:
  # Populate compound linkage details permanently
  - type: compound_linkage
    module: generation.backfill.compound_linkage_backfill
    class: CompoundLinkageBackfillGenerator
    field: produces_compounds
    compounds_source: data/compounds/Compounds.yaml
    defaults:
      - name
      - chemical_formula
      - cas_number
      - hazard_class
      - exposure_limits
      - control_measures
      - compound_category
    
  # Populate contaminant linkage details permanently
  - type: contaminant_linkage
    module: generation.backfill.contaminant_linkage_backfill
    class: ContaminantLinkageBackfillGenerator
    field: removes_contaminants
    contaminants_source: data/contaminants/Contaminants.yaml
    defaults:
      - name
      - description
      - removal_difficulty
      - surface_compatibility
      - health_hazards
    
  # Add author details permanently
  - type: author
    module: generation.backfill.author_backfill
    class: AuthorBackfillGenerator
    field: author
    authors_source: data/authors/Authors.yaml
    
  # Add intensity ranges permanently
  - type: intensity
    module: generation.backfill.intensity_backfill
    class: IntensityBackfillGenerator
```

---

## Usage Examples

### Backfill All Generators (All Domains)
```bash
# Dry run (see what would be populated)
python3 run.py --backfill --domain materials --dry-run

# Actually populate source YAML
python3 run.py --backfill --domain materials
```

### Backfill Specific Generator
```bash
# Populate only compound linkage details
python3 run.py --backfill --domain materials --generator compound_linkage

# Populate only author details
python3 run.py --backfill --domain contaminants --generator author
```

### Backfill All Domains
```bash
python3 run.py --backfill-all
```

---

## Benefits

### 1. **Performance**
- ✅ Enrichment runs once (not every export)
- ✅ Export becomes faster (no enricher overhead)
- ✅ Scales better for large datasets

### 2. **Data Quality**
- ✅ Source YAML is complete (single source of truth)
- ✅ Easier to audit (all data visible in source)
- ✅ Manual corrections persist (not overwritten)

### 3. **Maintainability**
- ✅ Simpler export pipeline (fewer enrichers)
- ✅ Clear separation: backfill (one-time) vs export (every time)
- ✅ Easier debugging (data is permanent, not computed)

### 4. **Flexibility**
- ✅ Can run backfill anytime (independent of export)
- ✅ Can backfill specific generators (granular control)
- ✅ Dry run mode for testing

---

## Migration Strategy

### Phase 1: Implement Backfill System
1. Create `generation/backfill/` module
2. Implement `BaseBackfillGenerator`
3. Add CLI integration to `run.py`

### Phase 2: Convert Enrichers to Backfill Generators
For each enricher, create equivalent backfill generator:
- `CompoundLinkageEnricher` → `CompoundLinkageBackfillGenerator`
- `ContaminantLinkageEnricher` → `ContaminantLinkageBackfillGenerator`
- `AuthorEnricher` → `AuthorBackfillGenerator`
- `IntensityEnricher` → `IntensityBackfillGenerator`

### Phase 3: Run Backfill (Populate Source YAML)
```bash
# Backfill all domains
python3 run.py --backfill-all --dry-run  # Preview
python3 run.py --backfill-all             # Execute
```

### Phase 4: Remove Enrichers from Export
Once source YAML is populated:
1. Remove enricher configs from `export/config/*.yaml`
2. Archive enricher code to `export/enrichers/deprecated/`
3. Export pipeline becomes simpler (no enrichment needed)

### Phase 5: Maintenance Mode
- Run backfill only when:
  - New items added to source YAML
  - Library data changes (compounds, authors, etc.)
  - Manual corrections needed

---

## Comparison

| Aspect | Current (Enrichers) | Proposed (Backfill) |
|--------|---------------------|---------------------|
| **When runs** | Every export | Once (on-demand) |
| **Data persistence** | Temporary (frontmatter only) | Permanent (source YAML) |
| **Export speed** | Slower (enrichment overhead) | Faster (no enrichment) |
| **Data visibility** | Hidden (computed during export) | Visible (in source YAML) |
| **Maintainability** | Complex (export + enrichment) | Simple (pre-populated) |
| **Manual corrections** | Lost on re-export | Persist (in source) |
| **Scalability** | Poor (repeated work) | Excellent (one-time) |

---

## Implementation Checklist

- [ ] Create `generation/backfill/` module structure
- [ ] Implement `BaseBackfillGenerator`
- [ ] Implement `BackfillRegistry`
- [ ] Add `--backfill` command to `run.py`
- [ ] Create backfill config files for each domain
- [ ] Convert `CompoundLinkageEnricher` → backfill generator
- [ ] Convert `ContaminantLinkageEnricher` → backfill generator
- [ ] Convert `AuthorEnricher` → backfill generator
- [ ] Convert `IntensityEnricher` → backfill generator
- [ ] Run backfill for all domains (dry-run first)
- [ ] Verify source YAML populated correctly
- [ ] Remove enrichers from export configs
- [ ] Update documentation
- [ ] Archive old enricher code

---

## Next Steps

1. **Review Proposal** - Approve architecture and approach
2. **Implement Phase 1** - Create backfill system foundation
3. **Test with One Generator** - Prove concept with compound linkage
4. **Full Migration** - Convert all enrichers to backfill generators
5. **Simplify Export** - Remove enrichers, speed up pipeline
