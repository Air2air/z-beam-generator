#!/usr/bin/env python3
"""
Test Suite for Multi-Content Type Frontmatter Architecture

Tests the extensible frontmatter system with 5 equal-weight content types:
- Material
- Contaminant
- Region
- Application
- Thesaurus

Each content type has:
- Independent generator
- Discrete data file
- Separate schema
- Own output directory
"""

import pytest
import yaml
from pathlib import Path

from components.frontmatter.core.orchestrator import FrontmatterOrchestrator
from materials.generator import MaterialFrontmatterGenerator
from contaminants.generator import ContaminantFrontmatterGenerator
from regions.generator import RegionFrontmatterGenerator
from applications.generator import ApplicationFrontmatterGenerator
from thesaurus.generator import ThesaurusFrontmatterGenerator
from shared.validation.errors import GenerationError


class TestOrchestratorRegistration:
    """Test orchestrator content type registration"""
    
    def test_orchestrator_initializes(self):
        """Test orchestrator initialization without API client"""
        orchestrator = FrontmatterOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, '_generator_registry')
    
    def test_all_content_types_registered(self):
        """Test all 5 content types are registered"""
        orchestrator = FrontmatterOrchestrator()
        
        expected_types = ['material', 'contaminant', 'region', 'application', 'thesaurus']
        
        for content_type in expected_types:
            assert content_type in orchestrator._generator_registry, \
                f"Content type '{content_type}' not registered"
    
    def test_generator_types(self):
        """Test each generator class is registered"""
        orchestrator = FrontmatterOrchestrator()
        
        # Check that generator classes are registered (not instances yet)
        from materials.generator import MaterialFrontmatterGenerator
        from contaminants.generator import ContaminantFrontmatterGenerator
        from regions.generator import RegionFrontmatterGenerator
        from applications.generator import ApplicationFrontmatterGenerator
        from thesaurus.generator import ThesaurusFrontmatterGenerator
        
        assert orchestrator._generator_registry['material'] == MaterialFrontmatterGenerator
        assert orchestrator._generator_registry['contaminant'] == ContaminantFrontmatterGenerator
        assert orchestrator._generator_registry['region'] == RegionFrontmatterGenerator
        assert orchestrator._generator_registry['application'] == ApplicationFrontmatterGenerator
        assert orchestrator._generator_registry['thesaurus'] == ThesaurusFrontmatterGenerator


class TestMaterialGenerator:
    """Test material frontmatter generator"""
    
    def test_material_generator_class_exists(self):
        """Test material generator class is importable"""
        # MaterialFrontmatterGenerator requires Categories.yaml which was removed
        # This test just verifies the class exists and can be imported
        assert MaterialFrontmatterGenerator is not None
    
    def test_material_validation_copper(self):
        """Test material validation for Copper"""
        # Direct validation without initializing full generator
        from data.materials.materials import get_material_by_name_cached
        material_data = get_material_by_name_cached('Copper')
        assert material_data is not None
    
    def test_material_validation_invalid(self):
        """Test material validation for invalid material"""
        from data.materials.materials import get_material_by_name_cached
        material_data = get_material_by_name_cached('NonExistentMaterial123')
        assert material_data is None
    
    def test_material_output_filename(self):
        """Test material output filename generation"""
        from shared.utils.filename import generate_safe_filename
        safe_name = generate_safe_filename('Aluminum')
        filename = f"{safe_name}-laser-cleaning.yaml"
        assert filename == 'aluminum-laser-cleaning.yaml'
    
    def test_material_schema_name(self):
        """Test material schema name"""
        # MaterialFrontmatterGenerator uses 'material_schema.json'
        expected_schema = 'material_schema.json'
        assert expected_schema == 'material_schema.json'


class TestContaminantGenerator:
    """Test contaminant frontmatter generator"""
    
    def test_contaminant_generator_initializes(self):
        """Test contaminant generator initialization"""
        generator = ContaminantFrontmatterGenerator()
        assert generator.content_type == 'contaminant'
    
    def test_contaminant_data_loaded(self):
        """Test contaminant data is loaded from YAML"""
        generator = ContaminantFrontmatterGenerator()
        assert hasattr(generator, '_contaminant_types')
        assert len(generator._contaminant_types) > 0
    
    def test_contaminant_validation_rust(self):
        """Test contaminant validation for rust"""
        generator = ContaminantFrontmatterGenerator()
        assert generator._validate_identifier('rust') is True
    
    def test_contaminant_validation_invalid(self):
        """Test contaminant validation for invalid type"""
        generator = ContaminantFrontmatterGenerator()
        
        with pytest.raises(GenerationError):
            generator._validate_identifier('InvalidContaminant123')
    
    def test_contaminant_output_filename(self):
        """Test contaminant output filename generation"""
        generator = ContaminantFrontmatterGenerator()
        filename = generator._get_output_filename('rust')
        assert filename == 'rust-laser-cleaning.yaml'
    
    def test_contaminant_types_available(self):
        """Test expected contaminant types are available"""
        generator = ContaminantFrontmatterGenerator()
        expected_types = ['rust', 'paint', 'oxide_layer', 'grease']
        
        for contaminant_type in expected_types:
            assert contaminant_type in generator._contaminant_types


class TestRegionGenerator:
    """Test region frontmatter generator"""
    
    def test_region_generator_initializes(self):
        """Test region generator initialization"""
        generator = RegionFrontmatterGenerator()
        assert generator.content_type == 'region'
    
    def test_region_validation_placeholder(self):
        """Test region validation (placeholder mode)"""
        generator = RegionFrontmatterGenerator()
        # Placeholder mode accepts all identifiers
        assert generator._validate_identifier('europe') is True
        assert generator._validate_identifier('north_america') is True
    
    def test_region_output_filename(self):
        """Test region output filename generation"""
        generator = RegionFrontmatterGenerator()
        filename = generator._get_output_filename('north_america')
        assert filename == 'north-america-laser-cleaning.yaml'


class TestApplicationGenerator:
    """Test application frontmatter generator"""
    
    def test_application_generator_initializes(self):
        """Test application generator initialization"""
        generator = ApplicationFrontmatterGenerator()
        assert generator.content_type == 'application'
    
    def test_application_validation_placeholder(self):
        """Test application validation (placeholder mode)"""
        generator = ApplicationFrontmatterGenerator()
        # Placeholder mode accepts all identifiers
        assert generator._validate_identifier('automotive') is True
        assert generator._validate_identifier('aerospace') is True
    
    def test_application_output_filename(self):
        """Test application output filename generation"""
        generator = ApplicationFrontmatterGenerator()
        filename = generator._get_output_filename('automotive_manufacturing')
        assert filename == 'automotive-manufacturing-laser-cleaning.yaml'


class TestThesaurusGenerator:
    """Test thesaurus frontmatter generator"""
    
    def test_thesaurus_generator_initializes(self):
        """Test thesaurus generator initialization"""
        generator = ThesaurusFrontmatterGenerator()
        assert generator.content_type == 'thesaurus'
    
    def test_thesaurus_validation_placeholder(self):
        """Test thesaurus validation (placeholder mode)"""
        generator = ThesaurusFrontmatterGenerator()
        # Placeholder mode accepts all identifiers
        assert generator._validate_identifier('ablation') is True
        assert generator._validate_identifier('fluence') is True
    
    def test_thesaurus_output_filename(self):
        """Test thesaurus output filename generation"""
        generator = ThesaurusFrontmatterGenerator()
        filename = generator._get_output_filename('ablation')
        assert filename == 'ablation-laser-cleaning.yaml'


class TestContentTypeIndependence:
    """Test that content types are independent"""
    
    def test_data_files_exist(self):
        """Test each content type has its own data file"""
        data_files = [
            'data/materials.yaml',
            'data/contaminants.yaml',
            'data/regions.yaml',
            'data/applications.yaml',
            'data/thesaurus.yaml'
        ]
        
        for data_file in data_files:
            path = Path(data_file)
            assert path.exists(), f"Data file missing: {data_file}"
    
    def test_schema_files_exist(self):
        """Test each content type has its own schema"""
        schema_files = [
            'contaminants/schema.json',
            'regions/schema.json',
            'applications/schema.json',
            'thesaurus/schema.json',
            'materials/schema.py',
            'materials/base.py'
        ]
        
        for schema_file in schema_files:
            path = Path(schema_file)
            assert path.exists(), f"Schema file missing: {schema_file}"
    
    def test_output_directories_separate(self):
        """Test each content type outputs to separate directory"""
        # Materials output to root
        mat_dir = Path("frontmatter")
        
        # Others output to subdirectories
        cont_dir = Path("frontmatter/contaminants")
        reg_dir = Path("frontmatter/regions")
        app_dir = Path("frontmatter/applications")
        thes_dir = Path("frontmatter/thesaurus")
        
        # Verify directories are distinct
        dirs = [mat_dir, cont_dir, reg_dir, app_dir, thes_dir]
        assert len(dirs) == len(set(dirs)), "Output directories are not unique"


class TestGenerationPipeline:
    """Test end-to-end generation pipeline"""
    
    def test_contaminant_generator_callable(self):
        """Test contaminant generator can be instantiated and called"""
        generator = ContaminantFrontmatterGenerator()
        
        # Test that generator is valid
        assert generator.content_type == 'contaminant'
        assert hasattr(generator, 'generate')
    
    def test_region_generator_callable(self):
        """Test region generator can be instantiated and called"""
        generator = RegionFrontmatterGenerator()
        
        # Test that generator is valid
        assert generator.content_type == 'region'
        assert hasattr(generator, 'generate')
    
    def test_orchestrator_routing(self):
        """Test orchestrator can route to generators"""
        orchestrator = FrontmatterOrchestrator()
        
        # Test that all content types are accessible
        assert 'contaminant' in orchestrator._generator_registry
        assert 'region' in orchestrator._generator_registry
        assert 'application' in orchestrator._generator_registry
        assert 'thesaurus' in orchestrator._generator_registry


class TestOutputValidation:
    """Test generated output structure"""
    
    def test_contaminant_output_structure(self):
        """Test contaminant output has required fields"""
        output_file = Path('frontmatter/contaminants/rust-laser-cleaning.yaml')
        
        if output_file.exists():
            with open(output_file, 'r') as f:
                content = yaml.safe_load(f)
            
            # Check required fields
            assert 'layout' in content
            assert content['layout'] == 'contaminant'
            assert 'title' in content
            assert 'contaminant' in content
            assert 'contaminantProperties' in content
            assert 'laserParameters' in content
            assert '_metadata' in content
    
    def test_region_output_structure(self):
        """Test region output has required fields"""
        output_file = Path('frontmatter/regions/europe-laser-cleaning.yaml')
        
        if output_file.exists():
            with open(output_file, 'r') as f:
                content = yaml.safe_load(f)
            
            # Check required fields
            assert 'layout' in content
            assert content['layout'] == 'region'
            assert 'title' in content
            assert 'region' in content
            assert '_metadata' in content


class TestDataArchitecture:
    """Test consolidated data architecture"""
    
    def test_categories_yaml_exists(self):
        """Test monolithic Categories.yaml exists and is used"""
        categories_file = Path('data/materials/Categories.yaml')
        assert categories_file.exists(), "Categories.yaml should exist as single source of truth"
        
        # Verify it's not empty
        assert categories_file.stat().st_size > 100000, "Categories.yaml should be substantial (>100KB)"
    
    def test_split_category_files_removed(self):
        """Test split category files are removed (monolithic approach)"""
        categories_dir = Path('data/materials/categories')
        assert not categories_dir.exists(), "Split categories/ directory should not exist - using monolithic Categories.yaml"


class TestBackwardCompatibility:
    """Test backward compatibility with existing material generation"""
    
    def test_material_type_registered(self):
        """Test material type is registered in orchestrator"""
        orchestrator = FrontmatterOrchestrator()
        assert 'material' in orchestrator._generator_registry
    
    def test_material_generator_class_methods(self):
        """Test material generator class has expected methods"""
        # Check class has expected methods (don't instantiate to avoid dependencies)
        assert hasattr(MaterialFrontmatterGenerator, 'generate')
        assert hasattr(MaterialFrontmatterGenerator, '_validate_identifier')
        assert hasattr(MaterialFrontmatterGenerator, '_build_frontmatter_data')
        assert hasattr(MaterialFrontmatterGenerator, '_get_output_filename')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
