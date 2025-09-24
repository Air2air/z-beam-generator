#!/usr/bin/env python3
"""
Complete script to update all Min/Max fields to numeric types in frontmatter schema
"""
import re

def fix_remaining_fields():
    """Fix remaining Min/Max fields that should be numeric"""
    
    schema_path = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/schemas/frontmatter.json"
    
    # Read current schema
    with open(schema_path, 'r') as f:
        content = f.read()
    
    # Fields that should be numeric (includes those missed in first pass)
    numeric_fields = [
        'densityMin', 'densityMax', 
        'meltingPointMin', 'meltingPointMax',
        'thermalConductivityMin', 'thermalConductivityMax',
        'specificHeatMin', 'specificHeatMax', 
        'thermalExpansionMin', 'thermalExpansionMax',
        'absorptionCoeffMin', 'absorptionCoeffMax', 
        'reflectanceMin', 'reflectanceMax',
        'tensileStrengthMin', 'tensileStrengthMax',
        'youngsModulusMin', 'youngsModulusMax',
        'modulusMin', 'modulusMax',
        'powerRangeMin', 'powerRangeMax', 
        'pulseDurationMin', 'pulseDurationMax',
        'wavelengthMin', 'wavelengthMax', 
        'spotSizeMin', 'spotSizeMax',
        'repetitionRateMin', 'repetitionRateMax', 
        'fluenceRangeMin', 'fluenceRangeMax'
    ]
    
    # Update all Min/Max fields to be numeric
    for field in numeric_fields:
        # Pattern to match the field definition with string type
        pattern = f'"{field}":\\s*{{\\s*"type":\\s*"string"\\s*}}'
        replacement = f'"{field}": {{\n          "type": "number"\n        }}'
        content = re.sub(pattern, replacement, content)
    
    # Write updated schema
    with open(schema_path, 'w') as f:
        f.write(content)
    
    print("Schema completely updated!")
    print(f"- Updated {len(numeric_fields)} Min/Max fields to numeric type")

if __name__ == "__main__":
    fix_remaining_fields()
