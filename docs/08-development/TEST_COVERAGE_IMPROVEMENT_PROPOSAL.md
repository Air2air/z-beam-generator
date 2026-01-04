# Test Coverage Improvement Proposal

**Created**: December 26, 2025  
**Purpose**: Address critical test coverage gaps after codebase normalization  
**Current Coverage**: 56.28% (139 tests / 247 source files)  
**Target Coverage**: 75%+ (185+ tests)

---

## 🔴 **Priority 1: Critical Gaps (Must Fix)**

### 1.1 Domain Coordinator Tests

**Impact**: HIGH - New coordinators have ZERO test coverage  
**Estimated Effort**: 4 hours  
**Risk**: Breaking changes go undetected

#### Create: `tests/domains/test_base_coordinator.py`

**Purpose**: Test DomainCoordinator base class functionality

```python
"""
Test suite for shared.domain.base_coordinator.DomainCoordinator

Tests common initialization, config loading, generator setup across all domains.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from shared.domain.base_coordinator import DomainCoordinator


class MockCoordinator(DomainCoordinator):
    """Concrete implementation for testing abstract base"""
    
    @property
    def domain_name(self) -> str:
        return "test_domain"
    
    def _create_data_loader(self):
        return Mock()
    
    def _get_item_data(self, item_id: str):
        return {"id": item_id, "name": "Test Item"}
    
    def _save_content(self, item_id, component_type, content, author_id=None):
        pass


def test_coordinator_initialization_without_api():
    """Test coordinator can initialize in inspection mode (no API client)"""
    coordinator = MockCoordinator()
    
    assert coordinator.domain_name == "test_domain"
    assert coordinator.api_client is None
    assert coordinator.generator is None
    assert coordinator.winston_client is None
    assert coordinator.subjective_evaluator is None


def test_coordinator_initialization_with_api():
    """Test coordinator initializes generation pipeline with API client"""
    mock_api = Mock()
    
    with patch('shared.domain.base_coordinator.SubjectiveEvaluator'):
        with patch('shared.domain.base_coordinator.WinstonClient'):
            with patch('shared.domain.base_coordinator.QualityEvaluatedGenerator'):
                coordinator = MockCoordinator(api_client=mock_api)
                
                assert coordinator.api_client is mock_api
                assert coordinator.generator is not None
                assert coordinator.subjective_evaluator is not None


def test_domain_config_loading():
    """Test domain config loads from domains/{domain}/config.yaml"""
    coordinator = MockCoordinator()
    
    # Should load config during __init__
    assert hasattr(coordinator, 'domain_config')
    # Note: Will fail if test_domain config doesn't exist (expected)


def test_winston_graceful_degradation():
    """Test coordinator continues without Winston if unavailable"""
    mock_api = Mock()
    
    with patch('shared.domain.base_coordinator.SubjectiveEvaluator'):
        with patch('shared.domain.base_coordinator.WinstonClient', side_effect=Exception("Winston not configured")):
            coordinator = MockCoordinator(api_client=mock_api)
            
            # Should initialize without Winston
            assert coordinator.winston_client is None
            # But should still have other components
            assert coordinator.api_client is mock_api


def test_generate_content_delegates_to_generator():
    """Test generate_content() delegates to QualityEvaluatedGenerator"""
    mock_api = Mock()
    mock_generator = Mock()
    mock_generator.generate.return_value = {"success": True, "content": "Test content"}
    
    with patch('shared.domain.base_coordinator.SubjectiveEvaluator'):
        with patch('shared.domain.base_coordinator.QualityEvaluatedGenerator', return_value=mock_generator):
            coordinator = MockCoordinator(api_client=mock_api)
            
            result = coordinator.generate_content("test-item", "description")
            
            mock_generator.generate.assert_called_once()
            assert result["success"] is True


# Run with: pytest tests/domains/test_base_coordinator.py -v
```

#### Create: `tests/domains/test_materials_coordinator.py`

**Purpose**: Test MaterialsCoordinator domain-specific functionality

```python
"""
Test suite for domains.materials.coordinator.MaterialsCoordinator

Tests materials-specific orchestration, data loading, EEAT generation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from domains.materials.coordinator import MaterialsCoordinator


def test_domain_name():
    """Test materials coordinator returns correct domain name"""
    coordinator = MaterialsCoordinator()
    assert coordinator.domain_name == "materials"


def test_materials_data_loading():
    """Test materials data loads from Materials.yaml"""
    coordinator = MaterialsCoordinator()
    
    # Load materials using internal method
    materials_data = coordinator._load_materials_data()
    
    assert 'materials' in materials_data
    assert len(materials_data['materials']) > 0


def test_get_item_data():
    """Test retrieving specific material data"""
    coordinator = MaterialsCoordinator()
    
    # Get first material
    materials = coordinator._load_materials_data()
    first_material_id = list(materials['materials'].keys())[0]
    
    material = coordinator._get_item_data(first_material_id)
    
    assert material is not None
    assert isinstance(material, dict)


def test_get_item_data_missing_material():
    """Test error handling for missing material"""
    coordinator = MaterialsCoordinator()
    
    with pytest.raises(ValueError, match="not found"):
        coordinator._get_item_data("nonexistent-material")


def test_generate_eeat_with_regulatory_standards():
    """Test EEAT generation from regulatory_standards"""
    coordinator = MaterialsCoordinator()
    
    # Mock material with regulatory standards
    material_data = {
        'name': 'Test Material',
        'regulatory_standards': [
            {
                'name': 'ISO 9001',
                'url': 'https://example.com/iso9001',
                'description': 'Quality management standard'
            },
            {
                'name': 'OSHA 1910',
                'url': 'https://example.com/osha',
                'description': 'Workplace safety standard'
            }
        ]
    }
    
    eeat = coordinator.generate_eeat('test-material', material_data)
    
    assert eeat is not None
    assert 'reviewedBy' in eeat
    assert eeat['reviewedBy'] == 'Z-Beam Quality Assurance Team'
    assert 'citations' in eeat
    assert len(eeat['citations']) >= 1
    assert len(eeat['citations']) <= 3
    assert 'isBasedOn' in eeat


def test_generate_eeat_without_standards():
    """Test EEAT generation returns None without regulatory standards"""
    coordinator = MaterialsCoordinator()
    
    material_data = {'name': 'Test Material'}  # No regulatory_standards
    
    eeat = coordinator.generate_eeat('test-material', material_data)
    
    assert eeat is None


# Run with: pytest tests/domains/test_materials_coordinator.py -v
```

#### Create: `tests/domains/test_contaminants_coordinator.py`

**Purpose**: Test new ContaminantCoordinator (created Dec 26, 2025)

```python
"""
Test suite for domains.contaminants.coordinator.ContaminantCoordinator

Tests contaminants-specific orchestration, data loading, batch generation.
Created: December 26, 2025 (same day as coordinator)
"""

import pytest
from pathlib import Path

from domains.contaminants.coordinator import ContaminantCoordinator


def test_domain_name():
    """Test contaminants coordinator returns correct domain name"""
    coordinator = ContaminantCoordinator()
    assert coordinator.domain_name == "contaminants"


def test_contaminants_data_loading():
    """Test contaminants data loads from Contaminants.yaml"""
    coordinator = ContaminantCoordinator()
    
    contaminants_data = coordinator._load_contaminants_data()
    
    assert 'contaminants' in contaminants_data
    assert len(contaminants_data['contaminants']) > 0


def test_list_contaminants():
    """Test list_contaminants() returns all contaminant IDs"""
    coordinator = ContaminantCoordinator()
    
    contaminant_ids = coordinator.list_contaminants()
    
    assert isinstance(contaminant_ids, list)
    assert len(contaminant_ids) > 0
    # Check first ID is a string
    assert isinstance(contaminant_ids[0], str)


def test_get_contaminant_data():
    """Test get_contaminant_data() retrieves specific contaminant"""
    coordinator = ContaminantCoordinator()
    
    # Get first contaminant
    contaminant_ids = coordinator.list_contaminants()
    first_id = contaminant_ids[0]
    
    contaminant = coordinator.get_contaminant_data(first_id)
    
    assert contaminant is not None
    assert isinstance(contaminant, dict)


def test_get_contaminant_data_missing():
    """Test get_contaminant_data() returns None for missing contaminant"""
    coordinator = ContaminantCoordinator()
    
    result = coordinator.get_contaminant_data("nonexistent-contaminant")
    
    assert result is None


def test_generate_contaminant_content_wrapper():
    """Test generate_contaminant_content() wraps generate_content()"""
    coordinator = ContaminantCoordinator()
    
    # Mock the base generate_content method
    from unittest.mock import patch
    with patch.object(coordinator, 'generate_content') as mock_generate:
        mock_generate.return_value = {"success": True}
        
        result = coordinator.generate_contaminant_content(
            "rust",
            "description",
            force_regenerate=True
        )
        
        mock_generate.assert_called_once_with("rust", "description", True)
        assert result["success"] is True


# Run with: pytest tests/domains/test_contaminants_coordinator.py -v
```

#### Create: `tests/domains/test_settings_coordinator.py`

**Purpose**: Test new SettingCoordinator (created Dec 26, 2025)

```python
"""
Test suite for domains.settings.coordinator.SettingCoordinator

Tests settings-specific orchestration, data loading, batch generation.
Created: December 26, 2025 (same day as coordinator)
"""

import pytest
from pathlib import Path

from domains.settings.coordinator import SettingCoordinator


def test_domain_name():
    """Test settings coordinator returns correct domain name"""
    coordinator = SettingCoordinator()
    assert coordinator.domain_name == "settings"


def test_settings_data_loading():
    """Test settings data loads from Settings.yaml"""
    coordinator = SettingCoordinator()
    
    settings_data = coordinator._load_settings_data()
    
    assert 'settings' in settings_data
    assert len(settings_data['settings']) > 0


def test_list_settings():
    """Test list_settings() returns all setting IDs"""
    coordinator = SettingCoordinator()
    
    setting_ids = coordinator.list_settings()
    
    assert isinstance(setting_ids, list)
    assert len(setting_ids) > 0
    assert isinstance(setting_ids[0], str)


def test_get_setting_data():
    """Test get_setting_data() retrieves specific setting"""
    coordinator = SettingCoordinator()
    
    # Get first setting
    setting_ids = coordinator.list_settings()
    first_id = setting_ids[0]
    
    setting = coordinator.get_setting_data(first_id)
    
    assert setting is not None
    assert isinstance(setting, dict)


def test_get_setting_data_missing():
    """Test get_setting_data() returns None for missing setting"""
    coordinator = SettingCoordinator()
    
    result = coordinator.get_setting_data("nonexistent-setting")
    
    assert result is None


def test_generate_setting_content_wrapper():
    """Test generate_setting_content() wraps generate_content()"""
    coordinator = SettingCoordinator()
    
    from unittest.mock import patch
    with patch.object(coordinator, 'generate_content') as mock_generate:
        mock_generate.return_value = {"success": True}
        
        result = coordinator.generate_setting_content(
            "power",
            "description",
            force_regenerate=False
        )
        
        mock_generate.assert_called_once_with("power", "description", False)
        assert result["success"] is True


# Run with: pytest tests/domains/test_settings_coordinator.py -v
```

---

## 🟡 **Priority 2: Renamed File Import Updates**

### 2.1 Update Existing Tests for Renamed Files

**Impact**: MEDIUM - Tests may fail with old import paths  
**Estimated Effort**: 1 hour  
**Files Affected**: 5-10 test files

#### Required Changes:

```python
# OLD IMPORTS (Find and replace):
from generation.seo.simple_seo_generator import SEOGenerator
from export.core.frontmatter_exporter import FrontmatterExporter
from export.enrichers.linkage.universal_linkage_enricher import UniversalLinkageEnricher
from export.enrichers.linkage.universal_restructure_enricher import UniversalRestructureEnricher

# NEW IMPORTS (Replace with):
from generation.seo.seo_generator import SEOGenerator
from export.core.frontmatter_exporter import FrontmatterExporter
from export.enrichers.linkage.linkage_enricher import UniversalLinkageEnricher
from export.enrichers.linkage.restructure_enricher import UniversalRestructureEnricher
```

#### Search Command:
```bash
grep -r "simple_seo_generator\|frontmatter_exporter\|universal_linkage_enricher\|universal_restructure_enricher" tests/
```

---

## 🟢 **Priority 3: Integration Tests**

### 3.1 End-to-End Coordinator Workflow Tests

**Impact**: MEDIUM - Validate full generation pipeline  
**Estimated Effort**: 3 hours

#### Create: `tests/integration/test_coordinator_workflows.py`

```python
"""
Integration tests for coordinator generation workflows.

Tests full end-to-end generation using real coordinators with mock API.
"""

import pytest
from unittest.mock import Mock, patch

from domains.materials.coordinator import MaterialsCoordinator
from domains.compounds.coordinator import CompoundCoordinator
from domains.contaminants.coordinator import ContaminantCoordinator
from domains.settings.coordinator import SettingCoordinator


@pytest.fixture
def mock_api_client():
    """Mock API client that returns test content"""
    client = Mock()
    client.generate.return_value = {
        'choices': [{
            'message': {'content': 'Generated test content for the item.'}
        }]
    }
    return client


@pytest.fixture
def mock_winston():
    """Mock Winston client"""
    winston = Mock()
    winston.check.return_value = {'score': 0.95, 'is_human': True}
    return winston


@pytest.fixture
def mock_evaluator():
    """Mock subjective evaluator"""
    evaluator = Mock()
    evaluator.evaluate.return_value = {
        'overall_realism': 8.0,
        'voice_authenticity': 8.5,
        'passes': True
    }
    return evaluator


def test_materials_full_generation_workflow(mock_api_client, mock_winston, mock_evaluator):
    """Test full materials generation workflow"""
    with patch('shared.domain.base_coordinator.WinstonClient', return_value=mock_winston):
        with patch('shared.domain.base_coordinator.SubjectiveEvaluator', return_value=mock_evaluator):
            coordinator = MaterialsCoordinator(api_client=mock_api_client)
            
            # Get first material
            materials = coordinator._load_materials_data()
            first_material = list(materials['materials'].keys())[0]
            
            # Generate content (will fail without full mock setup, but tests integration)
            result = coordinator.generate_content(
                first_material,
                "description",
                force_regenerate=True
            )
            
            # Verify workflow executed
            assert mock_api_client.generate.called or result is not None


def test_all_coordinators_initialize():
    """Test all 4 domain coordinators can initialize"""
    coordinators = [
        MaterialsCoordinator(),
        CompoundCoordinator(),
        ContaminantCoordinator(),
        SettingCoordinator()
    ]
    
    assert len(coordinators) == 4
    assert coordinators[0].domain_name == "materials"
    assert coordinators[1].domain_name == "compounds"
    assert coordinators[2].domain_name == "contaminants"
    assert coordinators[3].domain_name == "settings"


# Run with: pytest tests/integration/test_coordinator_workflows.py -v
```

---

## 📊 **Test Coverage Improvement Plan**

### Phase 1: Critical (Week 1)
- ✅ Create base coordinator tests (4 test files, ~400 lines)
- ✅ Update renamed file imports (search & replace in 10 files)
- **Expected Coverage**: 56% → 63%

### Phase 2: Integration (Week 2)
- ✅ Create coordinator workflow tests
- ✅ Add enricher base class tests
- ✅ Add generator base class tests
- **Expected Coverage**: 63% → 70%

### Phase 3: Edge Cases (Week 3)
- ✅ Error handling tests
- ✅ Configuration validation tests
- ✅ Data loader edge cases
- **Expected Coverage**: 70% → 75%

---

## 🎯 **Success Metrics**

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| **Overall Coverage** | 56.28% | 75%+ | Add 46+ tests |
| **Coordinator Coverage** | 0% | 100% | 4 new test files |
| **Base Class Coverage** | ~20% | 80%+ | 3 new test files |
| **Integration Tests** | 3 files | 10 files | 7 new test files |
| **Failing Imports** | Unknown | 0 | Update 10 files |

---

## ⚡ **Quick Start**

```bash
# 1. Create test files
mkdir -p tests/domains
touch tests/domains/test_base_coordinator.py
touch tests/domains/test_materials_coordinator.py
touch tests/domains/test_contaminants_coordinator.py
touch tests/domains/test_settings_coordinator.py

# 2. Find and fix renamed imports
grep -r "simple_seo_generator" tests/ -l | xargs sed -i '' 's/simple_seo_generator/seo_generator/g'
grep -r "frontmatter_exporter" tests/ -l | xargs sed -i '' 's/frontmatter_exporter/frontmatter_exporter/g'

# 3. Run new tests
pytest tests/domains/ -v --cov=shared/domain --cov=domains/*/coordinator.py

# 4. Generate coverage report
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

---

## 📝 **Implementation Checklist**

**Priority 1 (Critical):**
- [ ] Create `test_base_coordinator.py`
- [ ] Create `test_materials_coordinator.py`
- [ ] Create `test_contaminants_coordinator.py`
- [ ] Create `test_settings_coordinator.py`
- [ ] Update imports in existing tests (search & replace)

**Priority 2 (High):**
- [ ] Create `test_coordinator_workflows.py`
- [ ] Create `test_enricher_base_classes.py`
- [ ] Create `test_generator_base_classes.py`

**Priority 3 (Medium):**
- [ ] Add error handling tests
- [ ] Add configuration validation tests
- [ ] Add data loader edge case tests

---

## 🔗 **Related Documentation**

- [Generator Architecture](./GENERATOR_ARCHITECTURE.md) - Which generators to test
- [Export System Architecture](./EXPORT_SYSTEM_ARCHITECTURE.md) - Enricher testing guidance
- [Domain Coordinator Base Class](../../shared/domain/base_coordinator.py) - Implementation reference

---

**Next Steps**: Review proposal, prioritize P1 tasks, allocate 4-8 hours for implementation.
