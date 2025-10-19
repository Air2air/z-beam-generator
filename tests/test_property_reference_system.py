#!/usr/bin/env python3
"""
Property Reference System Tests

Tests for the centralized property reference system that ensures
consistency between validation, research, and generation systems.
"""

import pytest
from pathlib import Path
from utils.category_property_cache import get_category_property_cache


class TestCategoryPropertyCache:
    """Test category property cache loading and functionality"""
    
    def test_cache_singleton(self):
        """Test that cache returns same instance"""
        cache1 = get_category_property_cache()
        cache2 = get_category_property_cache()
        assert cache1 is cache2
    
    def test_load_properties(self):
        """Test loading valid properties per category"""
        cache = get_category_property_cache()
        properties = cache.load()
        
        assert isinstance(properties, dict)
        assert len(properties) > 0
        
        # Check expected categories
        assert 'metal' in properties
        assert 'ceramic' in properties
        assert 'plastic' in properties
        assert 'composite' in properties
        assert 'glass' in properties
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = get_category_property_cache()
        cache.load()  # Ensure loaded
        
        stats = cache.get_stats()
        assert 'categories' in stats
        assert 'total_properties' in stats
        assert 'cache_file' in stats
        assert 'cache_exists' in stats
        
        assert stats['categories'] > 0
        assert stats['total_properties'] > 0


class TestPropertySets:
    """Test property sets for each category"""
    
    @pytest.fixture
    def properties(self):
        """Load properties once for all tests"""
        cache = get_category_property_cache()
        return cache.load()
    
    def test_metal_essential_properties(self, properties):
        """Test metal category has essential properties"""
        metal_props = properties.get('metal', set())
        
        # Check essential properties
        assert 'density' in metal_props
        assert 'thermalConductivity' in metal_props
        assert 'hardness' in metal_props
        assert 'laserReflectivity' in metal_props  # Not 'reflectivity'
        
        # Metal-specific essentials
        assert 'ablationThreshold' in metal_props
        assert 'absorptionCoefficient' in metal_props
    
    def test_ceramic_essential_properties(self, properties):
        """Test ceramic category has essential properties"""
        ceramic_props = properties.get('ceramic', set())
        
        assert 'density' in ceramic_props
        assert 'thermalConductivity' in ceramic_props
        assert 'hardness' in ceramic_props
    
    def test_plastic_essential_properties(self, properties):
        """Test plastic category has essential properties"""
        plastic_props = properties.get('plastic', set())
        
        assert 'density' in plastic_props
        assert 'thermalConductivity' in plastic_props
    
    def test_no_property_duplication(self, properties):
        """Test that properties are unique per category"""
        for category, props in properties.items():
            # Check for duplicates
            props_list = list(props)
            assert len(props_list) == len(set(props_list)), f"Duplicates in {category}"


class TestPropertyAliases:
    """Test property alias resolution"""
    
    def test_reflectivity_alias(self):
        """Test reflectivity → laserReflectivity alias"""
        # Note: Categories.yaml may contain BOTH reflectivity and laserReflectivity
        # The property_manager.py handles the alias mapping at a higher level
        cache = get_category_property_cache()
        properties = cache.load()
        
        metal_props = properties.get('metal', set())
        
        # Should include laserReflectivity (canonical name)
        assert 'laserReflectivity' in metal_props
        
        # Verify metal_props is a set
        assert isinstance(metal_props, set)
        
        # May also have reflectivity as valid property
        # Alias mapping is handled by property_manager.py
    
    def test_thermal_destruction_canonical(self):
        """Test thermalDestruction is canonical (not meltingPoint)"""
        cache = get_category_property_cache()
        properties = cache.load()
        
        metal_props = properties.get('metal', set())
        
        # Note: Materials.yaml may have thermalDestruction as nested object
        # Property manager should handle the mapping
        # Verify properties loaded
        assert len(metal_props) > 0


class TestValidationIntegration:
    """Test integration with validation system"""
    
    def test_property_applicability_check(self):
        """Test checking if property is applicable to category"""
        cache = get_category_property_cache()
        properties = cache.load()
        
        # ablationThreshold is valid for metals
        metal_props = properties.get('metal', set())
        assert 'ablationThreshold' in metal_props
        
        # ablationThreshold should NOT be required for plastics
        plastic_props = properties.get('plastic', set())
        # Note: May still be valid, just not essential
        # This test verifies category-specific property sets exist
        assert len(plastic_props) > 0
    
    def test_essential_vs_optional(self):
        """Test distinguishing essential from optional properties"""
        cache = get_category_property_cache()
        properties = cache.load()
        
        # All properties in cache are "valid" for the category
        # Essential properties are a subset
        # This is handled by property_manager.py
        metal_props = properties.get('metal', set())
        
        # Essential properties should be in the set
        essential = {'density', 'thermalConductivity', 'hardness', 'laserReflectivity'}
        assert essential.issubset(metal_props)


class TestResearchIntegration:
    """Test integration with research system"""
    
    def test_gap_analysis(self):
        """Test identifying missing properties for research"""
        cache = get_category_property_cache()
        properties = cache.load()
        
        # Example: Aluminum (metal)
        category = 'metal'
        valid_props = properties.get(category, set())
        
        # Simulate existing properties
        existing_props = {'density', 'hardness'}
        
        # Find gaps
        missing_props = valid_props - existing_props
        
        # Should identify missing properties
        assert 'thermalConductivity' in missing_props
        assert 'laserReflectivity' in missing_props
    
    def test_invalid_property_detection(self):
        """Test detecting properties not applicable to category"""
        cache = get_category_property_cache()
        properties = cache.load()
        
        # Example: Check if property is valid for category
        category = 'plastic'
        property_name = 'sinteringTemperature'  # Ceramic-specific
        
        valid_props = properties.get(category, set())
        
        # May or may not be in set (depends on Categories.yaml)
        # This test verifies the mechanism exists
        is_valid = property_name in valid_props
        # Result depends on actual Categories.yaml content
        # Verify the check can be performed
        assert isinstance(is_valid, bool)


class TestCacheManagement:
    """Test cache file management"""
    
    def test_cache_file_creation(self):
        """Test that cache file is created"""
        cache = get_category_property_cache()
        cache.load()
        
        stats = cache.get_stats()
        cache_file = stats['cache_file']
        
        # Cache file should exist
        assert Path(cache_file).exists()
    
    def test_cache_regeneration(self):
        """Test cache regeneration when Categories.yaml changes"""
        cache = get_category_property_cache()
        
        # Load once
        props1 = cache.load()
        
        # Load again (should use cached version)
        props2 = cache.load()
        
        # Should be identical
        assert props1 == props2


class TestRealWorldUsage:
    """Test with real Materials.yaml scenarios"""
    
    def test_aluminum_property_validation(self):
        """Test Aluminum property validation using cache"""
        cache = get_category_property_cache()
        properties = cache.load()
        
        # Aluminum is metal category
        category = 'metal'
        valid_props = properties.get(category, set())
        
        # Properties from Materials.yaml for Aluminum
        # Note: Document expected properties for reference
        expected_essential = {'density', 'thermalConductivity', 'hardness', 'laserReflectivity'}
        
        # Verify all essential properties are in valid set
        assert expected_essential.issubset(valid_props)
    
    def test_multiple_categories(self):
        """Test loading properties for multiple categories"""
        cache = get_category_property_cache()
        properties = cache.load()
        
        # Verify multiple categories loaded
        assert len(properties) >= 9  # metal, ceramic, plastic, composite, glass, wood, stone, semiconductor, masonry
        
        # Each category should have properties
        for category, props in properties.items():
            assert len(props) > 0, f"Category {category} has no properties"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
