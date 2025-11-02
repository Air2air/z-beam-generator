"""
Test to enforce CRITICAL RULE: materials.yaml must NEVER contain min/max fields.

Per DATA_ARCHITECTURE.md:
- Min/max ranges exist EXCLUSIVELY in Categories.yaml
- Materials.yaml contains ONLY single values (no ranges)
- Material variance must be averaged/consolidated to single number
- Zero tolerance policy - any min/max in materials.yaml is architectural violation

Last Updated: October 17, 2025
"""

import pytest
import yaml
from pathlib import Path


class TestMaterialsNoMinMax:
    """Enforce exclusive rule: no min/max in materials.yaml properties."""
    
    @pytest.fixture
    def materials_data(self):
        """Load materials.yaml data."""
        materials_path = Path(__file__).parent.parent / 'data' / 'materials.yaml'
        with open(materials_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_no_min_max_in_any_material_property(self, materials_data):
        """
        CRITICAL TEST: Verify zero min/max fields in all material properties.
        
        This test enforces the architectural rule that min/max ranges
        exist EXCLUSIVELY in Categories.yaml and NEVER in materials.yaml.
        
        Failure indicates architectural violation requiring immediate fix.
        """
        violations = []
        
        materials = materials_data.get('materials', {})
        
        for material_name, material_data in materials.items():
            properties = material_data.get('materialProperties', {})
            
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Check for min field
                if 'min' in prop_data:
                    violations.append({
                        'material': material_name,
                        'property': prop_name,
                        'field': 'min',
                        'value': prop_data['min']
                    })
                
                # Check for max field
                if 'max' in prop_data:
                    violations.append({
                        'material': material_name,
                        'property': prop_name,
                        'field': 'max',
                        'value': prop_data['max']
                    })
        
        # Assert no violations found
        if violations:
            error_msg = "\n\n🚨 ARCHITECTURAL VIOLATION: Min/max fields found in materials.yaml!\n\n"
            error_msg += "Per DATA_ARCHITECTURE.md, min/max ranges exist EXCLUSIVELY in Categories.yaml.\n"
            error_msg += "Materials.yaml must contain ONLY single values.\n\n"
            error_msg += "Violations found:\n"
            
            for v in violations:
                error_msg += f"  - {v['material']}.{v['property']}.{v['field']} = {v['value']}\n"
            
            error_msg += "\n💡 FIX: Remove min/max fields and keep only averaged 'value' field.\n"
            error_msg += "Document variance context in research_basis field instead.\n"
            
            pytest.fail(error_msg)
    
    def test_all_properties_have_value_field(self, materials_data):
        """
        Verify all material properties have required 'value' field.
        
        Since min/max are prohibited, every property MUST have
        a single 'value' field instead.
        """
        missing_value = []
        
        materials = materials_data.get('materials', {})
        
        for material_name, material_data in materials.items():
            properties = material_data.get('materialProperties', {})
            
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Skip nested structures like thermalDestruction
                if 'point' in prop_data or 'type' in prop_data:
                    continue
                
                # Check for value field
                if 'value' not in prop_data:
                    missing_value.append({
                        'material': material_name,
                        'property': prop_name
                    })
        
        if missing_value:
            error_msg = "\n\n⚠️ Properties missing 'value' field:\n"
            for m in missing_value:
                error_msg += f"  - {m['material']}.{m['property']}\n"
            
            pytest.fail(error_msg)
    
    def test_materials_structure_compliance(self, materials_data):
        """
        Verify materials follow correct structure:
        - properties dict exists
        - Each property is a dict with value/unit/confidence
        - NO min/max fields anywhere
        """
        structural_issues = []
        
        materials = materials_data.get('materials', {})
        
        for material_name, material_data in materials.items():
            # Check properties exist
            if 'properties' not in material_data:
                structural_issues.append(f"{material_name}: Missing 'properties' section")
                continue
            
            properties = material_data['materialProperties']
            
            # Verify properties is a dict
            if not isinstance(properties, dict):
                structural_issues.append(f"{material_name}: 'properties' is not a dict")
                continue
            
            # Check each property
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Verify no min/max (critical check)
                if 'min' in prop_data or 'max' in prop_data:
                    structural_issues.append(
                        f"{material_name}.{prop_name}: Contains prohibited min/max fields"
                    )
        
        if structural_issues:
            error_msg = "\n\n🚨 Materials structure issues found:\n"
            for issue in structural_issues:
                error_msg += f"  - {issue}\n"
            
            pytest.fail(error_msg)


class TestCategoryRangesExist:
    """Verify Categories.yaml has the min/max ranges."""
    
    @pytest.fixture
    def categories_data(self):
        """Load Categories.yaml data."""
        categories_path = Path(__file__).parent.parent / 'data' / 'Categories.yaml'
        with open(categories_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_category_ranges_have_min_max(self, categories_data):
        """
        Verify Categories.yaml contains min/max for category ranges.
        
        This is the ONLY place where min/max should exist.
        """
        categories = categories_data.get('categories', {})
        
        found_ranges = 0
        
        for category_name, category_data in categories.items():
            if 'category_ranges' not in category_data:
                continue
            
            category_ranges = category_data['category_ranges']
            
            for prop_name, range_data in category_ranges.items():
                if isinstance(range_data, dict):
                    # Handle nested structures like thermalDestruction
                    if 'point' in range_data:
                        point_data = range_data['point']
                        if 'min' in point_data and 'max' in point_data:
                            found_ranges += 1
                    # Regular properties
                    elif 'min' in range_data and 'max' in range_data:
                        found_ranges += 1
        
        # Assert we found category ranges
        assert found_ranges > 0, (
            "No category ranges found in Categories.yaml! "
            "Categories.yaml should contain min/max for category-wide comparison."
        )
    
    def test_exclusive_source_of_truth(self, categories_data):
        """
        Document that Categories.yaml is the EXCLUSIVE source for min/max.
        
        This test serves as documentation of the architectural principle.
        """
        # This test always passes - it's for documentation
        assert True, (
            "✅ Categories.yaml is the EXCLUSIVE source of min/max ranges\n"
            "✅ Materials.yaml contains ONLY single values\n"
            "✅ Zero tolerance for min/max in materials.yaml\n"
            "✅ See DATA_ARCHITECTURE.md for complete specification"
        )
