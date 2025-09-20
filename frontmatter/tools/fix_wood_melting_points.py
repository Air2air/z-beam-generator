#!/usr/bin/env python3
"""
Add missing melting points to wood materials.
Wood doesn't technically melt - it decomposes. We'll add decomposition temperature as melting point.
"""

import yaml
from pathlib import Path

def fix_wood_melting_points():
    materials_dir = Path("frontmatter/materials")
    wood_materials = []
    
    # Common wood materials that might be missing melting points
    wood_patterns = ['fir', 'cherry', 'pine', 'redwood', 'hickory']
    
    for pattern in wood_patterns:
        yaml_file = materials_dir / f"{pattern}.yaml"
        if yaml_file.exists():
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            if 'properties' in data and 'meltingPoint' not in data['properties']:
                # Add decomposition temperature as "melting point" for wood
                data['properties']['meltingPoint'] = "300-500°C (decomposition)"
                data['properties']['meltingPointNumeric'] = 400.0
                data['properties']['meltingPointUnit'] = "°C"
                
                with open(yaml_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                print(f"✅ Added decomposition temperature to {pattern}.yaml")
                wood_materials.append(pattern)

    print(f"\n🎯 Fixed {len(wood_materials)} wood materials: {', '.join(wood_materials)}")

if __name__ == "__main__":
    fix_wood_melting_points()
