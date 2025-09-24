#!/usr/bin/env python3
"""
Script to update frontmatter schema to use numeric types only for properties and machineSettings
"""
import re

def update_schema():
    """Update frontmatter.json to use numeric types instead of oneOf string/number"""
    
    schema_path = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/schemas/frontmatter.json"
    
    # Read current schema
    with open(schema_path, 'r') as f:
        content = f.read()
    
    # Pattern to match oneOf sections with string/number
    oneof_pattern = r'"oneOf":\s*\[\s*\{"type":\s*"string"\},\s*\{"type":\s*"number"\}\s*\]'
    
    # Replace with just number type
    updated_content = re.sub(oneof_pattern, '"type": "number"', content)
    
    # Also update Min/Max fields that should be numeric
    properties_to_update = [
        'densityMin', 'densityMax', 'meltingPointMin', 'meltingPointMax',
        'thermalConductivityMin', 'thermalConductivityMax',
        'specificHeatMin', 'specificHeatMax', 'thermalExpansionMin', 'thermalExpansionMax',
        'absorptionCoeffMin', 'absorptionCoeffMax', 'reflectanceMin', 'reflectanceMax',
        'powerRangeMin', 'powerRangeMax', 'pulseDurationMin', 'pulseDurationMax',
        'wavelengthMin', 'wavelengthMax', 'spotSizeMin', 'spotSizeMax',
        'repetitionRateMin', 'repetitionRateMax', 'fluenceRangeMin', 'fluenceRangeMax'
    ]
    
    # Update Min/Max fields to be numeric instead of string
    for prop in properties_to_update:
        pattern = f'"{prop}":\s*{{\s*"type":\s*"string"\s*}}'
        replacement = f'"{prop}": {{\n          "type": "number"\n        }}'
        updated_content = re.sub(pattern, replacement, updated_content)
    
    # Write updated schema
    with open(schema_path, 'w') as f:
        f.write(updated_content)
    
    print("Schema updated successfully!")
    print("- Changed oneOf string/number to number type")
    print("- Updated Min/Max fields to numeric type")

if __name__ == "__main__":
    update_schema()
