#!/usr/bin/env python3
"""
Validation script for newly added materials (Cast Iron, Tool Steel).
Checks for completeness of properties and settings.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any

# Required properties for metal materials
REQUIRED_METAL_PROPERTIES = {
    # Core thermal properties
    'thermalConductivity',
    'specificHeat',
    'thermalDestructionPoint',
    'thermalDestructionType',
    'thermalDiffusivity',
    'thermalExpansion',
    
    # Mechanical properties
    'density',
    'hardness',
    'tensileStrength',
    'youngsModulus',
    
    # Laser interaction properties
    'laserAbsorption',
    'laserReflectivity',
    
    # Material characteristics
    'oxidationResistance',
    'corrosionResistance',
}

# Optional but recommended properties
RECOMMENDED_PROPERTIES = {
    'fractureToughness',
    'surfaceRoughness',
    'porosity',
}

# Required metadata fields
REQUIRED_METADATA = {
    'author',
    'category',
    'subcategory',
    'name',
    'material_metadata',
}

# Required property fields for each property
REQUIRED_PROPERTY_FIELDS = {
    'value',
    'unit',
    'confidence',
    'source',
    'research_basis',
    'research_date',
}

def load_materials() -> Dict[str, Any]:
    """Load Materials.yaml file."""
    materials_path = Path(__file__).parent.parent.parent / 'data' / 'Materials.yaml'
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('materials', {})

def validate_material(material_name: str, material_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate a single material for completeness.
    
    Returns:
        Dictionary with 'errors', 'warnings', and 'missing_properties' lists
    """
    errors = []
    warnings = []
    missing_properties = []
    
    # Check required metadata
    for field in REQUIRED_METADATA:
        if field not in material_data:
            errors.append(f"Missing required metadata field: {field}")
    
    # Check category is 'metal'
    if material_data.get('category') != 'metal':
        warnings.append(f"Expected category 'metal', got '{material_data.get('category')}'")
    
    # Get properties
    properties = material_data.get('materialProperties', {})
    
    # Check required properties
    for prop in REQUIRED_METAL_PROPERTIES:
        if prop not in properties:
            missing_properties.append(prop)
            errors.append(f"Missing required property: {prop}")
    
    # Check recommended properties
    for prop in RECOMMENDED_PROPERTIES:
        if prop not in properties:
            warnings.append(f"Missing recommended property: {prop}")
    
    # Validate each property has required fields
    for prop_name, prop_data in properties.items():
        if not isinstance(prop_data, dict):
            errors.append(f"Property '{prop_name}' is not a dictionary")
            continue
            
        for field in REQUIRED_PROPERTY_FIELDS:
            if field not in prop_data:
                errors.append(f"Property '{prop_name}' missing required field: {field}")
        
        # Check confidence is between 0 and 1
        if 'confidence' in prop_data:
            conf = prop_data['confidence']
            if not (0 <= conf <= 1):
                errors.append(f"Property '{prop_name}' has invalid confidence: {conf} (must be 0-1)")
        
        # Check source is 'ai_research'
        if 'source' in prop_data and prop_data['source'] != 'ai_research':
            warnings.append(f"Property '{prop_name}' has non-standard source: {prop_data['source']}")
    
    # Check industry tags
    if 'material_metadata' in material_data:
        metadata = material_data['material_metadata']
        if 'industryTags' not in metadata:
            errors.append("Missing industryTags in material_metadata")
        elif not isinstance(metadata['industryTags'], list):
            errors.append("industryTags must be a list")
        elif len(metadata['industryTags']) < 3:
            warnings.append(f"Only {len(metadata['industryTags'])} industry tags (recommend 5+)")
    
    return {
        'errors': errors,
        'warnings': warnings,
        'missing_properties': missing_properties
    }

def main():
    """Main validation function."""
    print("🔍 Validating newly added materials...\n")
    
    materials = load_materials()
    
    # Materials to validate
    new_materials = ['Cast Iron', 'Tool Steel']
    
    all_valid = True
    
    for material_name in new_materials:
        if material_name not in materials:
            print(f"❌ Material '{material_name}' not found in Materials.yaml")
            all_valid = False
            continue
        
        print(f"📋 Validating: {material_name}")
        print("=" * 60)
        
        result = validate_material(material_name, materials[material_name])
        
        # Report errors
        if result['errors']:
            all_valid = False
            print(f"\n❌ ERRORS ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"   • {error}")
        
        # Report warnings
        if result['warnings']:
            print(f"\n⚠️  WARNINGS ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"   • {warning}")
        
        # Report missing properties
        if result['missing_properties']:
            print(f"\n📝 MISSING PROPERTIES ({len(result['missing_properties'])}):")
            for prop in sorted(result['missing_properties']):
                print(f"   • {prop}")
        
        # Success message
        if not result['errors'] and not result['warnings']:
            print("\n✅ Material validation PASSED - All checks successful!")
        elif not result['errors']:
            print("\n✅ Material validation PASSED - No errors, only warnings")
        
        print("\n")
    
    # Summary
    print("=" * 60)
    if all_valid:
        print("🎉 All materials validated successfully!")
        return 0
    else:
        print("⚠️  Validation completed with errors - please fix missing properties")
        return 1

if __name__ == '__main__':
    exit(main())
