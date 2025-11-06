#!/usr/bin/env python3
"""
Test Breadcrumb Navigation Generation

Tests breadcrumb generation for materials with proper hierarchy:
Home → Materials → Category → Subcategory → Material

Author: AI Assistant
Date: November 6, 2025
"""

import pytest
import yaml
from pathlib import Path
from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter


class TestBreadcrumbGeneration:
    """Test breadcrumb navigation structure and generation."""
    
    @pytest.fixture
    def exporter(self):
        """Create exporter instance for testing."""
        return TrivialFrontmatterExporter()
    
    def test_breadcrumb_basic_structure(self, exporter):
        """Test breadcrumb has correct basic structure."""
        material_data = {
            'name': 'Aluminum',
            'category': 'metal',
            'subcategory': 'non-ferrous'
        }
        slug = 'aluminum-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        # Should have 5 levels: Home, Materials, Category, Subcategory, Material
        assert len(breadcrumb) == 5
        
        # All items should have label and href
        for item in breadcrumb:
            assert 'label' in item
            assert 'href' in item
            assert isinstance(item['label'], str)
            assert isinstance(item['href'], str)
    
    def test_breadcrumb_home_level(self, exporter):
        """Test Home level is always first."""
        material_data = {'name': 'Test', 'category': 'metal'}
        slug = 'test-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        assert breadcrumb[0]['label'] == 'Home'
        assert breadcrumb[0]['href'] == '/'
    
    def test_breadcrumb_materials_level(self, exporter):
        """Test Materials level is always second."""
        material_data = {'name': 'Test', 'category': 'metal'}
        slug = 'test-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        assert breadcrumb[1]['label'] == 'Materials'
        assert breadcrumb[1]['href'] == '/materials'
    
    def test_breadcrumb_category_level(self, exporter):
        """Test category level is properly capitalized."""
        material_data = {
            'name': 'Steel',
            'category': 'metal',
            'subcategory': 'ferrous'
        }
        slug = 'steel-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        assert breadcrumb[2]['label'] == 'Metal'
        assert breadcrumb[2]['href'] == '/materials/metal'
    
    def test_breadcrumb_subcategory_level(self, exporter):
        """Test subcategory level formatting and URL."""
        material_data = {
            'name': 'Aluminum',
            'category': 'metal',
            'subcategory': 'non-ferrous'
        }
        slug = 'aluminum-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        # Subcategory should be title-cased with spaces
        assert breadcrumb[3]['label'] == 'Non Ferrous'
        assert breadcrumb[3]['href'] == '/materials/metal/non-ferrous'
    
    def test_breadcrumb_material_level(self, exporter):
        """Test material level uses actual name and slug."""
        material_data = {
            'name': 'Aluminum',
            'category': 'metal',
            'subcategory': 'non-ferrous'
        }
        slug = 'aluminum-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        assert breadcrumb[4]['label'] == 'Aluminum'
        assert breadcrumb[4]['href'] == '/materials/aluminum-laser-cleaning'
    
    def test_breadcrumb_without_subcategory(self, exporter):
        """Test breadcrumb generation when subcategory is missing."""
        material_data = {
            'name': 'TestMaterial',
            'category': 'metal'
            # No subcategory
        }
        slug = 'testmaterial-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        # Should have 4 levels without subcategory
        assert len(breadcrumb) == 4
        assert breadcrumb[0]['label'] == 'Home'
        assert breadcrumb[1]['label'] == 'Materials'
        assert breadcrumb[2]['label'] == 'Metal'
        assert breadcrumb[3]['label'] == 'TestMaterial'
    
    def test_breadcrumb_subcategory_with_underscores(self, exporter):
        """Test subcategory with underscores gets converted to spaces."""
        material_data = {
            'name': 'Test',
            'category': 'composite',
            'subcategory': 'fiber_reinforced'
        }
        slug = 'test-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        assert breadcrumb[3]['label'] == 'Fiber Reinforced'
    
    def test_breadcrumb_url_hierarchy(self, exporter):
        """Test URL hierarchy is progressive."""
        material_data = {
            'name': 'Granite',
            'category': 'stone',
            'subcategory': 'igneous'
        }
        slug = 'granite-laser-cleaning'
        
        breadcrumb = exporter._generate_breadcrumb(material_data, slug)
        
        # URLs should build progressively
        assert breadcrumb[0]['href'] == '/'
        assert breadcrumb[1]['href'] == '/materials'
        assert breadcrumb[2]['href'] == '/materials/stone'
        assert breadcrumb[3]['href'] == '/materials/stone/igneous'
        assert breadcrumb[4]['href'] == '/materials/granite-laser-cleaning'
    
    def test_breadcrumb_in_exported_files(self):
        """Test that breadcrumb exists in actual exported frontmatter files."""
        frontmatter_dir = Path(__file__).parents[2] / "frontmatter" / "materials"
        
        # Test a few sample materials
        test_materials = [
            'aluminum-laser-cleaning.yaml',
            'granite-laser-cleaning.yaml',
            'oak-laser-cleaning.yaml'
        ]
        
        for filename in test_materials:
            filepath = frontmatter_dir / filename
            assert filepath.exists(), f"File {filename} should exist"
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Breadcrumb should exist
            assert 'breadcrumb' in data, f"Breadcrumb missing in {filename}"
            breadcrumb = data['breadcrumb']
            
            # Should be a list
            assert isinstance(breadcrumb, list), f"Breadcrumb should be list in {filename}"
            
            # Should have at least 4 items (Home, Materials, Category, Material)
            assert len(breadcrumb) >= 4, f"Breadcrumb too short in {filename}"
            
            # First item should be Home
            assert breadcrumb[0]['label'] == 'Home'
            assert breadcrumb[0]['href'] == '/'
            
            # Second item should be Materials
            assert breadcrumb[1]['label'] == 'Materials'
            assert breadcrumb[1]['href'] == '/materials'
    
    def test_breadcrumb_coverage(self):
        """Test that all 132 materials have breadcrumb field."""
        frontmatter_dir = Path(__file__).parents[2] / "frontmatter" / "materials"
        yaml_files = list(frontmatter_dir.glob("*.yaml"))
        
        # Should have 132 material files
        assert len(yaml_files) == 132, f"Expected 132 files, found {len(yaml_files)}"
        
        missing_breadcrumb = []
        for filepath in yaml_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if 'breadcrumb' not in data:
                missing_breadcrumb.append(filepath.name)
        
        assert len(missing_breadcrumb) == 0, f"Files missing breadcrumb: {missing_breadcrumb}"
    
    def test_breadcrumb_categories(self):
        """Test breadcrumbs across different material categories."""
        test_cases = [
            ('aluminum-laser-cleaning.yaml', 'Metal', 'Non Ferrous'),
            ('granite-laser-cleaning.yaml', 'Stone', 'Igneous'),
            ('oak-laser-cleaning.yaml', 'Wood', 'Hardwood'),
            ('polycarbonate-laser-cleaning.yaml', 'Plastic', 'Thermoplastic'),
            ('fiberglass-laser-cleaning.yaml', 'Composite', 'Fiber Reinforced'),
            ('brick-laser-cleaning.yaml', 'Masonry', 'General'),
        ]
        
        frontmatter_dir = Path(__file__).parents[2] / "frontmatter" / "materials"
        
        for filename, expected_category, expected_subcategory in test_cases:
            filepath = frontmatter_dir / filename
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            breadcrumb = data['breadcrumb']
            
            # Check category
            assert breadcrumb[2]['label'] == expected_category, \
                f"{filename}: Expected category '{expected_category}', got '{breadcrumb[2]['label']}'"
            
            # Check subcategory
            assert breadcrumb[3]['label'] == expected_subcategory, \
                f"{filename}: Expected subcategory '{expected_subcategory}', got '{breadcrumb[3]['label']}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
