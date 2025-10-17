#!/usr/bin/env python3
"""
Two-Category System Compliance Tests

Validates that all frontmatter files strictly adhere to the two-category system:
1. Only 'laser_material_interaction' and 'material_characteristics' categories allowed
2. No 'other' category permitted
3. All properties correctly categorized according to official specification
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, Set

# Official property lists from FRONTMATTER_STRUCTURE_REFERENCE.md
LASER_MATERIAL_INTERACTION_PROPERTIES = {
    'laserAbsorption', 'laserReflectivity', 'reflectivity', 'ablationThreshold',
    'absorptivity', 'emissivity', 'refractiveIndex', 'laserDamageThreshold',
    'opticalTransmittance', 'thermalConductivity', 'specificHeat',
    'thermalDiffusivity', 'thermalExpansion', 'thermalDestruction',
    'boilingPoint', 'heatCapacity', 'glasTransitionTemperature',
    'sinteringTemperature', 'ignitionTemperature', 'autoignitionTemperature',
    'decompositionTemperature', 'sublimationPoint', 'thermalStability',
    'absorptionCoefficient', 'thermalDegradationPoint', 'photonPenetrationDepth'
}

MATERIAL_CHARACTERISTICS_PROPERTIES = {
    # Physical (15)
    'density', 'viscosity', 'porosity', 'surfaceRoughness', 'permeability',
    'surfaceEnergy', 'wettability', 'crystallineStructure', 'grainSize',
    'moistureContent', 'waterSolubility', 'celluloseContent', 'ligninContent',
    'degradationPoint', 'softeningPoint', 'surfaceTension',
    # Mechanical (10)
    'hardness', 'tensileStrength', 'youngsModulus', 'yieldStrength',
    'elasticity', 'bulkModulus', 'shearModulus', 'compressiveStrength',
    'flexuralStrength', 'fractureResistance',
    # Electrical (4)
    'electricalResistivity', 'electricalConductivity', 'dielectricConstant',
    'dielectricStrength',
    # Chemical (4)
    'chemicalStability', 'oxidationResistance', 'corrosionResistance',
    'weatherResistance',
    # Other (1)
    'magneticPermeability'
}

ALLOWED_CATEGORIES = {'laser_material_interaction', 'material_characteristics'}


class TestTwoCategoryCompliance:
    """Test suite for two-category system compliance"""
    
    @pytest.fixture(scope="class")
    def frontmatter_files(self):
        """Get all frontmatter YAML files"""
        frontmatter_dir = Path('content/components/frontmatter')
        return list(frontmatter_dir.glob('*.yaml'))
    
    @pytest.fixture(scope="class")
    def cast_iron_frontmatter(self):
        """Load Cast Iron frontmatter"""
        path = Path('content/components/frontmatter/cast-iron-laser-cleaning.yaml')
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    @pytest.fixture(scope="class")
    def tool_steel_frontmatter(self):
        """Load Tool Steel frontmatter"""
        path = Path('content/components/frontmatter/tool-steel-laser-cleaning.yaml')
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def test_no_other_category_in_cast_iron(self, cast_iron_frontmatter):
        """Cast Iron must not have 'other' category"""
        material_props = cast_iron_frontmatter.get('materialProperties', {})
        assert 'other' not in material_props, \
            "Cast Iron frontmatter contains forbidden 'other' category"
    
    def test_no_other_category_in_tool_steel(self, tool_steel_frontmatter):
        """Tool Steel must not have 'other' category"""
        material_props = tool_steel_frontmatter.get('materialProperties', {})
        assert 'other' not in material_props, \
            "Tool Steel frontmatter contains forbidden 'other' category"
    
    def test_only_two_categories_in_cast_iron(self, cast_iron_frontmatter):
        """Cast Iron must have only the two allowed categories"""
        material_props = cast_iron_frontmatter.get('materialProperties', {})
        categories = set(material_props.keys())
        
        assert categories <= ALLOWED_CATEGORIES, \
            f"Cast Iron has invalid categories: {categories - ALLOWED_CATEGORIES}"
        assert 'laser_material_interaction' in categories, \
            "Cast Iron missing 'laser_material_interaction' category"
        assert 'material_characteristics' in categories, \
            "Cast Iron missing 'material_characteristics' category"
    
    def test_only_two_categories_in_tool_steel(self, tool_steel_frontmatter):
        """Tool Steel must have only the two allowed categories"""
        material_props = tool_steel_frontmatter.get('materialProperties', {})
        categories = set(material_props.keys())
        
        assert categories <= ALLOWED_CATEGORIES, \
            f"Tool Steel has invalid categories: {categories - ALLOWED_CATEGORIES}"
        assert 'laser_material_interaction' in categories, \
            "Tool Steel missing 'laser_material_interaction' category"
        assert 'material_characteristics' in categories, \
            "Tool Steel missing 'material_characteristics' category"
    
    def test_cast_iron_properties_correctly_categorized(self, cast_iron_frontmatter):
        """All Cast Iron properties must be in correct categories"""
        material_props = cast_iron_frontmatter.get('materialProperties', {})
        
        # Check laser_material_interaction
        laser_props = material_props.get('laser_material_interaction', {}).get('properties', {})
        for prop in laser_props.keys():
            assert prop in LASER_MATERIAL_INTERACTION_PROPERTIES, \
                f"Property '{prop}' incorrectly placed in laser_material_interaction"
        
        # Check material_characteristics
        char_props = material_props.get('material_characteristics', {}).get('properties', {})
        for prop in char_props.keys():
            assert prop in MATERIAL_CHARACTERISTICS_PROPERTIES, \
                f"Property '{prop}' incorrectly placed in material_characteristics"
    
    def test_tool_steel_properties_correctly_categorized(self, tool_steel_frontmatter):
        """All Tool Steel properties must be in correct categories"""
        material_props = tool_steel_frontmatter.get('materialProperties', {})
        
        # Check laser_material_interaction
        laser_props = material_props.get('laser_material_interaction', {}).get('properties', {})
        for prop in laser_props.keys():
            assert prop in LASER_MATERIAL_INTERACTION_PROPERTIES, \
                f"Property '{prop}' incorrectly placed in laser_material_interaction"
        
        # Check material_characteristics
        char_props = material_props.get('material_characteristics', {}).get('properties', {})
        for prop in char_props.keys():
            assert prop in MATERIAL_CHARACTERISTICS_PROPERTIES, \
                f"Property '{prop}' incorrectly placed in material_characteristics"
    
    def test_cast_iron_has_absorption_coefficient(self, cast_iron_frontmatter):
        """Cast Iron must have absorptionCoefficient in laser_material_interaction"""
        laser_props = cast_iron_frontmatter.get('materialProperties', {}) \
            .get('laser_material_interaction', {}).get('properties', {})
        
        assert 'absorptionCoefficient' in laser_props, \
            "absorptionCoefficient missing from laser_material_interaction"
    
    def test_cast_iron_has_thermal_destruction(self, cast_iron_frontmatter):
        """Cast Iron must have thermalDestruction in laser_material_interaction"""
        laser_props = cast_iron_frontmatter.get('materialProperties', {}) \
            .get('laser_material_interaction', {}).get('properties', {})
        
        assert 'thermalDestruction' in laser_props, \
            "thermalDestruction missing from laser_material_interaction"
    
    def test_tool_steel_has_absorption_coefficient(self, tool_steel_frontmatter):
        """Tool Steel must have absorptionCoefficient in laser_material_interaction"""
        laser_props = tool_steel_frontmatter.get('materialProperties', {}) \
            .get('laser_material_interaction', {}).get('properties', {})
        
        assert 'absorptionCoefficient' in laser_props, \
            "absorptionCoefficient missing from laser_material_interaction"
    
    def test_tool_steel_has_thermal_destruction(self, tool_steel_frontmatter):
        """Tool Steel must have thermalDestruction in laser_material_interaction"""
        laser_props = tool_steel_frontmatter.get('materialProperties', {}) \
            .get('laser_material_interaction', {}).get('properties', {})
        
        assert 'thermalDestruction' in laser_props, \
            "thermalDestruction missing from laser_material_interaction"
    
    def test_tool_steel_has_crystalline_structure(self, tool_steel_frontmatter):
        """Tool Steel must have crystallineStructure in material_characteristics"""
        char_props = tool_steel_frontmatter.get('materialProperties', {}) \
            .get('material_characteristics', {}).get('properties', {})
        
        assert 'crystallineStructure' in char_props, \
            "crystallineStructure missing from material_characteristics"
    
    def test_no_melting_point_property(self, cast_iron_frontmatter, tool_steel_frontmatter):
        """meltingPoint should not exist as a separate property (use thermalDestruction)"""
        # Check Cast Iron
        for category_data in cast_iron_frontmatter.get('materialProperties', {}).values():
            props = category_data.get('properties', {})
            assert 'meltingPoint' not in props, \
                "Cast Iron has deprecated 'meltingPoint' property"
        
        # Check Tool Steel
        for category_data in tool_steel_frontmatter.get('materialProperties', {}).values():
            props = category_data.get('properties', {})
            assert 'meltingPoint' not in props, \
                "Tool Steel has deprecated 'meltingPoint' property"
    
    def test_no_thermal_destruction_type_property(self, cast_iron_frontmatter, tool_steel_frontmatter):
        """thermalDestructionType is metadata only, not a frontmatter property"""
        # Check Cast Iron
        for category_data in cast_iron_frontmatter.get('materialProperties', {}).values():
            props = category_data.get('properties', {})
            assert 'thermalDestructionType' not in props, \
                "Cast Iron has metadata-only 'thermalDestructionType' as property"
        
        # Check Tool Steel
        for category_data in tool_steel_frontmatter.get('materialProperties', {}).values():
            props = category_data.get('properties', {})
            assert 'thermalDestructionType' not in props, \
                "Tool Steel has metadata-only 'thermalDestructionType' as property"
    
    def test_all_frontmatter_files_comply(self, frontmatter_files):
        """All frontmatter files must use only two-category system"""
        errors = []
        
        for file_path in frontmatter_files:
            with open(file_path, 'r') as f:
                try:
                    data = yaml.safe_load(f)
                    material_props = data.get('materialProperties', {})
                    categories = set(material_props.keys())
                    
                    # Check for 'other' category
                    if 'other' in categories:
                        errors.append(f"{file_path.name}: Contains forbidden 'other' category")
                    
                    # Check for invalid categories
                    invalid = categories - ALLOWED_CATEGORIES
                    if invalid:
                        errors.append(f"{file_path.name}: Invalid categories {invalid}")
                    
                except Exception as e:
                    errors.append(f"{file_path.name}: Error loading - {e}")
        
        assert not errors, \
            f"Found {len(errors)} files with category violations:\n" + "\n".join(errors)
    
    def test_validation_agent_detects_other_category(self):
        """Validation agent must detect and reject 'other' category"""
        from scripts.validation.comprehensive_validation_agent import DataQualityValidationAgent
        
        agent = DataQualityValidationAgent()
        
        # Test data with 'other' category
        test_material_props = {
            'laser_material_interaction': {'properties': {}},
            'material_characteristics': {'properties': {}},
            'other': {'properties': {'someProperty': {}}}
        }
        
        issues = agent.validate_two_category_system('TestMaterial', test_material_props)
        
        # Should have ERROR for 'other' category
        other_errors = [i for i in issues if i['category'] == 'other' and i['severity'] == 'ERROR']
        assert len(other_errors) > 0, \
            "Validation agent failed to detect 'other' category"
        assert 'FORBIDDEN' in other_errors[0]['message'] or 'forbidden' in other_errors[0]['message'], \
            "Error message should clearly indicate 'other' category is forbidden"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
