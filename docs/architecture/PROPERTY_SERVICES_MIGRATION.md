# Property Services Consolidation Plan

## Overview

The property management system currently runs **two parallel implementations**:
- **Old Services**: PropertyDiscoveryService + PropertyResearchService (764 lines, legacy)
- **New Service**: PropertyManager (809 lines, unified replacement)

Both systems are active in `streamlined_generator.py` (2,496 lines), creating confusion and technical debt.

## Current State Analysis

### Old Services (To Be Deprecated)

**PropertyDiscoveryService** (`components/frontmatter/services/property_discovery_service.py`, 253 lines)
- **Purpose**: Identifies which properties need research
- **Used**: 12 times in streamlined_generator.py
- **Key methods**:
  - `discover_properties_to_research()` - Gap identification
  - `calculate_coverage()` - Coverage statistics
  - `validate_property_completeness()` - Completeness validation

**PropertyResearchService** (`components/frontmatter/services/property_research_service.py`, 511 lines)
- **Purpose**: Coordinates AI research for properties
- **Used**: 20 times in streamlined_generator.py
- **Key methods**:
  - `add_category_thermal_property()` - Category thermal fields
  - `research_material_properties()` - Property research
  - `research_machine_settings()` - Machine settings research

### New Unified Service (Target)

**PropertyManager** (`components/frontmatter/services/property_manager.py`, 809 lines)
- **Purpose**: Complete property lifecycle management
- **Used**: 10 times in streamlined_generator.py
- **Explicitly replaces**: PropertyDiscoveryService + PropertyResearchService
- **Key methods**:
  - `discover_and_research_properties()` - Discovery + research in one call
  - `research_machine_settings()` - Machine settings (same as old)
  - `persist_researched_properties()` - Materials.yaml writeback (new feature)

## Usage Patterns in streamlined_generator.py

### Old Services Pattern (32 call sites)
```python
# Discovery (12 sites)
to_research, skip_reasons = self.property_discovery_service.discover_properties_to_research(...)
coverage_stats = self.property_discovery_service.calculate_coverage(...)
self.property_discovery_service.validate_property_completeness(...)

# Research (20 sites)
thermal_field_added = self.property_research_service.add_category_thermal_property(...)
researched_properties = self.property_research_service.research_material_properties(...)
machine_settings = self.property_research_service.research_machine_settings(...)
```

### New Service Pattern (10 sites)
```python
# Unified discovery + research (10 sites)
research_result = self.property_manager.discover_and_research_properties(
    material_name=material_name,
    material_category=category,
    yaml_properties=yaml_properties
)
# Returns: PropertyResearchResult with quantitative_properties, qualitative_characteristics, machine_settings
```

## Migration Strategy

### Phase 1: Create Method Compatibility Layer ✅ SAFE
Add wrapper methods to PropertyManager that match old service signatures:

```python
class PropertyManager:
    # Existing unified method
    def discover_and_research_properties(...) -> PropertyResearchResult: ...
    
    # NEW: Compatibility wrappers for old PropertyDiscoveryService methods
    def discover_properties_to_research(self, material_name, material_category, yaml_properties):
        """Wrapper for old PropertyDiscoveryService.discover_properties_to_research()"""
        result = self._discover_gaps(material_name, material_category, yaml_properties)
        return result['to_research'], result['skip_reasons']
    
    def calculate_coverage(self, material_name, yaml_properties, category):
        """Wrapper for old PropertyDiscoveryService.calculate_coverage()"""
        # Extract from internal _discover_gaps result
        ...
    
    def validate_property_completeness(self, category, researched_properties):
        """Wrapper for old PropertyDiscoveryService.validate_property_completeness()"""
        return self._validate_essential_coverage(category, researched_properties)
    
    # NEW: Compatibility wrappers for old PropertyResearchService methods
    def add_category_thermal_property(self, material_name, properties, category):
        """Wrapper for old PropertyResearchService.add_category_thermal_property()"""
        # Use internal categorization logic
        ...
    
    def research_material_properties(self, material_name, to_research, category):
        """Wrapper for old PropertyResearchService.research_material_properties()"""
        result = self.discover_and_research_properties(material_name, category, {})
        return result.quantitative_properties
```

### Phase 2: Update streamlined_generator.py ⚠️ RISKY
Replace old service calls with PropertyManager compatibility methods:

```python
# BEFORE (old services)
to_research, skip_reasons = self.property_discovery_service.discover_properties_to_research(...)
researched_properties = self.property_research_service.research_material_properties(...)

# AFTER (PropertyManager with compatibility layer)
to_research, skip_reasons = self.property_manager.discover_properties_to_research(...)
researched_properties = self.property_manager.research_material_properties(...)
```

### Phase 3: Remove Old Service Instantiation
```python
# REMOVE these lines from _load_categories_data()
self.property_discovery_service = PropertyDiscoveryService(categories_data=categories_data)
self.property_research_service = PropertyResearchService(...)

# REMOVE these imports
from components.frontmatter.services.property_discovery_service import PropertyDiscoveryService
from components.frontmatter.services.property_research_service import PropertyResearchService
```

### Phase 4: Archive Old Services
Move to `archive/unused-infrastructure/`:
- `property_discovery_service.py` (253 lines)
- `property_research_service.py` (511 lines)

### Phase 5: Gradual Migration to New API (Future)
Over time, replace compatibility wrappers with direct unified calls:
```python
# Current (compatibility)
to_research, skip_reasons = self.property_manager.discover_properties_to_research(...)
researched = self.property_manager.research_material_properties(...)

# Target (unified API)
result = self.property_manager.discover_and_research_properties(...)
# Use result.quantitative_properties, result.qualitative_characteristics
```

## Benefits

1. **Code Reduction**: Eliminate 764 lines of duplicate logic
2. **Single Source of Truth**: One property management implementation
3. **Better Features**: PropertyManager includes Materials.yaml writeback
4. **Cleaner API**: Unified discovery + research in one call
5. **Easier Maintenance**: One service to update vs three

## Risks

1. **Large File**: streamlined_generator.py is 2,496 lines
2. **Integration Points**: 32 call sites to update
3. **Testing Burden**: Must verify all property workflows still work
4. **Compatibility**: Wrapper methods must exactly match old behavior

## Testing Requirements

After each phase:
```bash
# Test collection (should remain 807 tests, 0 errors)
python3 -m pytest tests/ --collect-only -q

# Run property-related tests
python3 -m pytest tests/frontmatter/ -v -k property

# Run full integration tests
python3 -m pytest tests/e2e/ -v

# Test with real material
python3 run.py --material "Titanium"
```

## Rollback Plan

If issues arise:
1. **Phase 2**: Revert streamlined_generator.py changes via git
2. **Phase 1**: Remove compatibility methods (safe, not used yet)
3. **Emergency**: `git revert <commit_hash>`

## Decision

**Status**: Ready for Phase 1 (add compatibility layer)
**Next Step**: Implement wrapper methods in PropertyManager
**Timeline**: 
- Phase 1: 30 minutes (add wrappers)
- Phase 2: 60 minutes (update streamlined_generator.py)
- Phase 3-4: 15 minutes (cleanup)
- Testing: 45 minutes

**Total Estimated Time**: 2.5 hours

## Deprecation Notice

Once migration complete, add to old services:
```python
import warnings

warnings.warn(
    "PropertyDiscoveryService is deprecated. Use PropertyManager instead.",
    DeprecationWarning,
    stacklevel=2
)
```
