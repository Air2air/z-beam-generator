#!/usr/bin/env python3
"""
Debug the property enhancement process to see what min/max values are being added.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.property_enhancer import enhance_frontmatter_with_context

def debug_enhancement():
    """Debug what happens during property enhancement."""
    
    # Test material with new properties too
    test_material = {
        'name': 'Test Steel',
        'category': 'metal',
        'properties': {
            # Original properties
            'density': '7.85 g/cm³',
            'meltingPoint': '1500°C',
            'thermalConductivity': '50 W/m·K',
            'tensileStrength': '400 MPa',
            'hardness': '150 HV',
            'youngsModulus': '200 GPa',
            
            # New properties
            'laserAbsorption': '10 cm⁻¹',
            'laserReflectivity': '20%',
            'thermalDiffusivity': '15 mm²/s',
            'thermalExpansion': '12 µm/m·K',
            'specificHeat': '0.46 J/g·K'
        }
    }
    
    print("Original properties:")
    for key, value in test_material['properties'].items():
        print(f"  {key}: {value}")
    
    enhanced = enhance_frontmatter_with_context(test_material, 'metal')
    
    print(f"\nEnhanced properties ({len(enhanced['properties'])} total):")
    props = enhanced['properties']
    
    # Group by type
    original_props = {}
    min_props = {}
    max_props = {}
    percentile_props = {}
    
    for key, value in props.items():
        if key.endswith('Min'):
            min_props[key] = value
        elif key.endswith('Max'):
            max_props[key] = value
        elif key.endswith('Percentile'):
            percentile_props[key] = value
        else:
            original_props[key] = value
    
    print("\nOriginal values:")
    for key, value in original_props.items():
        print(f"  {key}: {value}")
    
    print("\nMin values:")
    for key, value in min_props.items():
        print(f"  {key}: {value}")
    
    print("\nMax values:")
    for key, value in max_props.items():
        print(f"  {key}: {value}")
        
    print("\nPercentiles:")
    for key, value in percentile_props.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    debug_enhancement()
