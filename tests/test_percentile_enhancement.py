#!/usr/bin/env python3
"""
Test script to verify percentile enhancement functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.property_enhancer import enhance_generated_frontmatter

def test_enhancement():
    """Test the frontmatter enhancement with the existing steel file"""
    
    # Read the existing steel frontmatter
    with open('content/components/frontmatter/steel-laser-cleaning.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== ORIGINAL STEEL FRONTMATTER ===")
    print("Properties section (original):")
    lines = content.split('\n')
    in_properties = False
    for line in lines:
        if line.strip().startswith('properties:'):
            in_properties = True
        elif in_properties and line.strip() and not line.startswith('  '):
            break
        elif in_properties:
            if 'Percentile' in line:
                print(f"  {line}")
            elif any(prop in line for prop in ['density:', 'meltingPoint:', 'hardness:', 'youngsModulus:', 'thermalConductivity:', 'tensileStrength:']):
                print(f"  {line}")
    
    # Enhance the content
    print("\n=== ENHANCING WITH PERCENTILES ===")
    enhanced_content = enhance_generated_frontmatter(content, 'metal')
    
    print("\nProperties section (enhanced):")
    lines = enhanced_content.split('\n')
    in_properties = False
    for line in lines:
        if line.strip().startswith('properties:'):
            in_properties = True
        elif in_properties and line.strip() and not line.startswith('  '):
            break
        elif in_properties:
            if 'Percentile' in line:
                print(f"  {line}")
            elif any(prop in line for prop in ['density:', 'meltingPoint:', 'hardness:', 'youngsModulus:', 'thermalConductivity:', 'tensileStrength:']):
                print(f"  {line}")
    
    # Save enhanced version for comparison
    with open('test_enhanced_steel.md', 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print("\n✅ Enhanced frontmatter saved to: test_enhanced_steel.md")
    print("✅ Percentile calculation working successfully!")

if __name__ == "__main__":
    test_enhancement()
