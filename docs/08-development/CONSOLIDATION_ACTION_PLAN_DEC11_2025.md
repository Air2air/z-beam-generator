# Consolidation Action Plan - December 11, 2025
**Based on**: E2E Architecture Audit  
**Status**: 📋 READY FOR EXECUTION  
**Grade**: B+ (85/100) → Target: A (95/100)

---

## 📊 Executive Summary

**Completed (Phases 1-5)**:
- ✅ Foundation layer (BaseDataLoader, CacheManager, File I/O)
- ✅ Domain migrations (Materials, Contaminants, Settings)
- ✅ Unified loader infrastructure
- ✅ Author normalization (11 objects)
- ✅ Test suite passing (272/274)

**Remaining Work**:
- 🔴 17+ hardcoded API parameters (POLICY VIOLATION)
- 🔴 10 YAML instances in export/ directory
- 🟡 86 YAML instances in shared/ directory
- 🟡 20 YAML instances in generation/ directory
- 🟢 15 duplicate exception definitions
- 🟢 22 manual path resolutions

**Estimated Total Time**: 53-75 hours (7-10 days)  
**Impact**: ~1,330+ lines eliminated, 100% policy compliance

---

## 🚨 CRITICAL: Immediate Priorities (Next 2 Days)

### Priority 1: Fix Hardcoded API Parameters ⚡ **POLICY VIOLATION**
**Time**: 2-3 hours  
**Impact**: Compliance with HARDCODED_VALUE_POLICY.md  
**Grade Impact**: B+ → A-

**Files to Fix**:
```python
# ❌ BEFORE (Policy Violation)
temperature=0.3  # Hardcoded

# ✅ AFTER (Policy Compliant)
from generation.config.dynamic_config import DynamicConfig
dynamic_config = DynamicConfig()
temperature = dynamic_config.calculate_temperature(component_type='research')
```

**Files Requiring Fix** (17 instances):
1. `domains/contaminants/research/laser_properties_researcher.py` - 6 instances
2. `shared/research/content_researcher.py` - 3 instances
3. `shared/services/pipeline_process_service.py` - 3 instances
4. `shared/research/faq_topic_researcher.py` - 1 instance
5. `shared/research/services/ai_research_service.py` - 1 instance
6. `shared/voice/post_processor.py` - 1 instance
7. `shared/generation/api_helper.py` - 1 instance
8. `export/research/property_value_researcher.py` - 1 instance

**Verification**:
```bash
# After fix, this should return ZERO results
grep -r "temperature\s*=\s*0\.[0-9]" --include="*.py" domains/ shared/ export/ generation/
```

---

### Priority 2: Complete Export Directory Migration ⚡
**Time**: 3-4 hours  
**Impact**: Eliminates 10 YAML instances  
**Grade Impact**: A- → A

**Strategy**: Extend MaterialsDataLoader with content methods

**Step 1: Add Content Loading Methods** (1 hour)
```python
# File: domains/materials/data_loader_v2.py

class MaterialsDataLoader(BaseDataLoader):
    
    def load_micros(self) -> Dict[str, Any]:
        """Load Micros.yaml content."""
        cache_key = "materials:micros"
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached
        
        filepath = self.base_path / "data" / "content" / "Micros.yaml"
        data = read_yaml_file(filepath)
        result = data.get('micros', {})
        
        cache_manager.set(cache_key, result)
        return result
    
    def load_faqs(self) -> Dict[str, Any]:
        """Load FAQs.yaml content."""
        cache_key = "materials:faqs"
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached
        
        filepath = self.base_path / "data" / "content" / "FAQs.yaml"
        data = read_yaml_file(filepath)
        result = data.get('faqs', {})
        
        cache_manager.set(cache_key, result)
        return result
    
    def load_regulatory_standards(self) -> Dict[str, Any]:
        """Load RegulatoryStandards.yaml content."""
        cache_key = "materials:regulatory_standards"
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached
        
        filepath = self.base_path / "data" / "content" / "RegulatoryStandards.yaml"
        data = read_yaml_file(filepath)
        result = data.get('regulatory_standards', {})
        
        cache_manager.set(cache_key, result)
        return result
```

**Step 2: Update unified_loader.py** (15 minutes)
```python
# File: shared/data/unified_loader.py

# Add convenience functions
def load_material_micros() -> Dict[str, Any]:
    """Load material micros (captions)."""
    return get_materials_loader().load_micros()

def load_material_faqs() -> Dict[str, Any]:
    """Load material FAQs."""
    return get_materials_loader().load_faqs()

def load_regulatory_standards() -> Dict[str, Any]:
    """Load regulatory standards."""
    return get_materials_loader().load_regulatory_standards()
```

**Step 3: Migrate trivial_exporter.py** (1 hour)
```python
# File: export/core/trivial_exporter.py

# ❌ BEFORE (3 methods, ~40 lines)
def _load_captions(self) -> Dict[str, Any]:
    captions_file = Path(__file__).resolve().parents[3] / "materials" / "data" / "content" / "Micros.yaml"
    with open(captions_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('micros', {})

def _load_faqs(self) -> Dict[str, Any]:
    # ... similar pattern ...

def _load_regulatory_standards(self) -> Dict[str, Any]:
    # ... similar pattern ...

# ✅ AFTER (3 lines)
from shared.data.unified_loader import (
    load_material_micros,
    load_material_faqs, 
    load_regulatory_standards
)

# In __init__:
self.micros = load_material_micros()
self.faqs = load_material_faqs()
self.regulatory_standards = load_regulatory_standards()
```

**Step 4: Migrate Other Export Files** (1-2 hours)
- `export/core/streamlined_generator.py` - 4 YAML instances
- `export/core/validation_helpers.py` - 1 instance
- `export/core/base_generator.py` - 1 instance
- `export/enhancement/property_enhancement_service.py` - 1 instance

**Verification**:
```bash
# Should return ZERO results
grep -r "yaml.safe_load\|yaml.load" export/ | grep -v test

# Run tests
pytest tests/export/ -v
```

---

## 📅 Short-Term Plan (Week 1-2)

### Phase 6: Shared Directory Audit and Migration
**Time**: 8-10 hours  
**Impact**: 86 YAML instances + utility consolidation

**Day 1-2: Systematic Audit**
```bash
# Step 1: Categorize shared/ files by domain
find shared/ -name "*.py" -type f ! -path "*/test*" | sort

# Step 2: Identify YAML loading patterns
grep -r "yaml.safe_load\|yaml.load" shared/ | grep -v test

# Step 3: Group by subdirectory
shared/research/ - 20+ instances
shared/utils/ - 15+ instances
shared/services/ - 25+ instances
shared/validation/ - 10+ instances
shared/generation/ - 10+ instances
shared/config/ - 6+ instances
```

**Day 3-4: Create Consolidation Plan**
- Document duplicate utilities (file_io vs file_operations)
- Document duplicate validators (unified_schema_validator vs schema_validator)
- Identify opportunities for BaseService pattern
- Create migration order

**Day 5: Execute Migration**
- Highest-impact files first
- Test after each migration
- Update imports across codebase

---

### Phase 7: Generation Directory Migration
**Time**: 6-8 hours  
**Impact**: 20 YAML instances

**Approach**:
```python
# Most generation/ files access config.yaml
# Create ConfigLoader using unified_loader pattern

# File: shared/config/unified_loader.py (NEW)
class ConfigLoader(BaseDataLoader):
    """Unified configuration loader."""
    
    def load_generation_config(self) -> Dict[str, Any]:
        """Load generation/config.yaml"""
        # Implementation follows BaseDataLoader pattern
        
    def load_domain_config(self, domain: str) -> Dict[str, Any]:
        """Load domains/{domain}/config.yaml"""
        # Implementation follows BaseDataLoader pattern
```

**Files to Migrate**:
- `generation/core/*.py` - 8 instances
- `generation/config/*.py` - 5 instances
- `generation/enrichment/*.py` - 4 instances
- `generation/integrity/*.py` - 3 instances

---

### Phase 8: Exception Consolidation
**Time**: 3-4 hours  
**Impact**: 15 duplicate definitions removed

**Step 1: Create Migration Map**
```python
# File: shared/validation/errors.py (CANONICAL)
class ConfigurationError(Exception): pass
class MaterialDataError(Exception): pass
class ValidationError(Exception): pass
class PropertyDiscoveryError(Exception): pass
```

**Step 2: Update Imports** (Automated)
```python
# ❌ OLD (in each domain file)
class ConfigurationError(Exception):
    pass

# ✅ NEW
from shared.validation.errors import ConfigurationError
```

**Step 3: Remove Duplicate Definitions**
- `domains/contaminants/data_loader.py` - Remove ConfigurationError
- `domains/contaminants/pattern_loader.py` - Remove ConfigurationError
- `domains/materials/category_loader.py` - Remove ConfigurationError
- `domains/materials/data_loader.py` - Remove MaterialDataError
- 7 more files

**Step 4: Map Similar Exceptions**
```python
SettingsDataError → ConfigurationError
PropertyTaxonomyError → ValidationError
DataOrchestrationError → GenerationError
ResearchError → PropertyDiscoveryError
AuditError → ValidationError
UnitConversionError → ValidationError
```

**Verification**:
```bash
# Should return only canonical definitions
grep -r "^class.*Error.*Exception" --include="*.py" domains/ shared/ export/ generation/
```

---

## 📅 Medium-Term Plan (Week 3-4)

### Phase 9: Coordinator Pattern Completion
**Time**: 4-5 hours  
**Impact**: Architectural consistency

**Create Missing Coordinators**:

**1. Contaminants Coordinator** (2 hours)
```python
# File: domains/contaminants/coordinator.py (NEW)
class ContaminantsCoordinator:
    """Orchestrates contaminants domain operations."""
    
    def __init__(self):
        from shared.data.unified_loader import get_contaminants_loader
        self.loader = get_contaminants_loader()
    
    def generate_contamination_pattern(self, material: str, ...):
        """Generate contamination pattern for material."""
        # Orchestration logic here
```

**2. Settings Coordinator** (2 hours)
```python
# File: domains/settings/coordinator.py (NEW)
class SettingsCoordinator:
    """Orchestrates settings domain operations."""
    
    def __init__(self):
        from shared.data.unified_loader import get_settings_loader
        self.loader = get_settings_loader()
    
    def generate_machine_settings(self, material: str, ...):
        """Generate machine settings for material."""
        # Orchestration logic here
```

---

### Phase 10: Validator Pattern Consolidation
**Time**: 5-6 hours  
**Impact**: 200+ lines eliminated

**Create BaseValidator**:
```python
# File: shared/validation/base_validator.py (NEW)
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate data and return (is_valid, error_messages).
        
        Returns:
            Tuple of (success, errors)
        """
        errors = []
        
        # Required fields
        errors.extend(self._validate_required_fields(data))
        
        # Type validation
        errors.extend(self._validate_types(data))
        
        # Range validation
        errors.extend(self._validate_ranges(data))
        
        # Custom validation
        errors.extend(self._validate_custom(data))
        
        return (len(errors) == 0, errors)
    
    @abstractmethod
    def _validate_required_fields(self, data: Dict[str, Any]) -> List[str]:
        """Validate required fields are present."""
        pass
    
    @abstractmethod
    def _validate_types(self, data: Dict[str, Any]) -> List[str]:
        """Validate field types."""
        pass
    
    def _validate_ranges(self, data: Dict[str, Any]) -> List[str]:
        """Validate numeric ranges (optional override)."""
        return []
    
    def _validate_custom(self, data: Dict[str, Any]) -> List[str]:
        """Custom validation logic (optional override)."""
        return []
```

**Migrate Existing Validators**:
- `domains/contaminants/validator.py` → Inherit from BaseValidator
- `domains/materials/image/validator.py` → Inherit from BaseValidator
- `domains/materials/validation/completeness_validator.py` → Inherit from BaseValidator

---

### Phase 11: Path Resolution Cleanup
**Time**: 3-4 hours  
**Impact**: 22 instances standardized

**Pattern Migration**:
```python
# ❌ OLD
PROJECT_ROOT = Path(__file__).parent.parent.parent

# ✅ NEW (Option 1: Use BaseDataLoader)
from shared.data.base_loader import BaseDataLoader
project_root = BaseDataLoader.project_root

# ✅ NEW (Option 2: Use utility)
from shared.utils.path_utils import get_project_root
project_root = get_project_root()
```

**Files to Migrate**:
- `domains/materials/category_loader.py`
- `export/core/streamlined_generator.py`
- `export/core/schema_validator.py`
- `export/research/property_value_researcher.py`
- 18 more files

---

## 📈 Success Metrics

### Quantitative Goals
- ✅ Zero yaml.safe_load in production code
- ✅ Zero @lru_cache decorators (use CacheManager)
- ✅ Zero duplicate exception definitions
- ✅ Zero hardcoded API parameters
- ✅ Zero manual path resolution patterns
- ✅ All domains have coordinators

### Quality Metrics
- Test suite: 272/274 → 280/280 passing
- Code duplication: 600 instances → 0 instances
- Architecture grade: B+ (85/100) → A (95/100)
- Lines of code: -1,330+ lines eliminated

### Compliance Metrics
- HARDCODED_VALUE_POLICY.md: 100% compliant
- NAMING_CONVENTIONS_POLICY.md: 100% compliant
- BaseDataLoader pattern: 100% adoption
- CacheManager pattern: 100% adoption

---

## 🚦 Decision Points

### Decision 1: Immediate Action on Hardcoded Parameters?
**Recommendation**: ✅ YES - Policy violation, fix immediately  
**Time**: 2-3 hours  
**Risk**: LOW - Dynamic config system exists and works

### Decision 2: Complete Export Migration First?
**Recommendation**: ✅ YES - Builds on Phase 5 work  
**Time**: 3-4 hours  
**Risk**: LOW - Pattern proven in domains/

### Decision 3: Tackle Shared Directory Now or Later?
**Recommendation**: ⏸️ LATER - Largest effort, requires systematic audit  
**Time**: 8-10 hours  
**Risk**: MEDIUM - May discover more complexity

### Decision 4: Exception Consolidation Priority?
**Recommendation**: 🟢 NICE-TO-HAVE - Not causing issues  
**Time**: 3-4 hours  
**Risk**: LOW - Straightforward refactor

---

## 📊 Time Investment Summary

| Phase | Priority | Time | Impact | Risk |
|-------|----------|------|--------|------|
| P1: API Parameters | 🔴 HIGH | 2-3h | Policy fix | LOW |
| P2: Export Migration | 🔴 HIGH | 3-4h | 10 instances | LOW |
| P6: Shared Audit | 🟡 MED | 8-10h | 86 instances | MED |
| P7: Generation Migration | 🟡 MED | 6-8h | 20 instances | MED |
| P8: Exceptions | 🟢 LOW | 3-4h | Consistency | LOW |
| P9: Coordinators | 🟡 MED | 4-5h | Architecture | LOW |
| P10: Validators | 🟢 LOW | 5-6h | 200+ lines | MED |
| P11: Path Resolution | 🟢 LOW | 3-4h | 22 instances | LOW |
| **TOTALS** | | **35-48h** | **~1,330 lines** | |

**Critical Path**: P1 → P2 (5-7 hours to reach A- grade)  
**Full Consolidation**: 35-48 hours (4-6 days) to reach A grade

---

## ✅ Recommended Execution Order

### This Week (Days 1-2) - **CRITICAL**
1. ✅ Fix hardcoded API parameters (2-3h)
2. ✅ Extend MaterialsDataLoader with content methods (1h)
3. ✅ Complete export/ directory migration (2-3h)
4. ✅ Run full test suite and verify

**Result**: B+ → A- grade, policy compliant

### Next Week (Days 3-7) - **HIGH VALUE**
5. ⏩ Audit shared/ directory systematically (2 days)
6. ⏩ Migrate generation/ directory (1-2 days)
7. ⏩ Consolidate exception definitions (0.5 days)

**Result**: A- → A grade, major consolidation complete

### Week 3-4 - **POLISH**
8. ⏭️ Create missing coordinators
9. ⏭️ Consolidate validator pattern
10. ⏭️ Clean up path resolution

**Result**: A → A+ grade, architecture excellence

---

## 🎯 Final Recommendation

**APPROVE**: Phases P1-P2 (5-7 hours, critical path)  
**DEFER**: Phases P6-P11 (30-41 hours, diminishing returns)

**Rationale**:
- Current state (B+ grade) is production-ready
- Foundation layer complete and working
- P1-P2 fix critical policy violation
- P6-P11 are incremental improvements with diminishing returns
- Can be done gradually during normal development

**User Decision Required**: 
- Execute critical path (P1-P2) now?
- Continue with full consolidation (all phases)?
- Mark consolidation phase complete and defer rest?

---

**Status**: ✅ READY FOR USER DECISION  
**Confidence**: HIGH - Comprehensive plan with risk assessment  
**Grade Impact**: B+ → A- (critical) → A (full)
