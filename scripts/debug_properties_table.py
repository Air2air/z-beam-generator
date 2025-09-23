#!/usr/bin/env python3
"""
Debug Properties Table Generator

Test what properties are being extracted for the basalt material.
"""

import json
import yaml
from pathlib import Path

def test_basalt_extraction():
    # Load basalt frontmatter
    frontmatter_path = Path(__file__).parent.parent / "content" / "components" / "frontmatter" / "basalt-laser-cleaning.md"
    
    with open(frontmatter_path, 'r') as f:
        content = f.read()
    
    # Extract YAML frontmatter
    if content.startswith('---'):
        lines = content.split('\n')
        yaml_lines = []
        in_yaml = False
        for line in lines:
            if line.strip() == '---':
                if in_yaml:
                    break
                in_yaml = True
                continue
            if in_yaml:
                yaml_lines.append(line)
        
        yaml_content = '\n'.join(yaml_lines)
        try:
            frontmatter_data = yaml.safe_load(yaml_content)
            print("✅ Successfully parsed basalt frontmatter")
            
            # Check what properties are available
            props = frontmatter_data.get('properties', {})
            print(f"\n📋 Properties found ({len(props)} total):")
            for key in sorted(props.keys()):
                if not key.endswith(('Min', 'Max', 'Unit', 'Numeric', 'Percentile')):
                    print(f"  ✓ {key}: {props[key]}")
            
            # Test thermal destruction properties specifically
            print(f"\n🔥 Thermal Destruction Properties:")
            print(f"  thermalDestructionPoint: {props.get('thermalDestructionPoint', 'NOT FOUND')}")
            print(f"  thermalDestructionType: {props.get('thermalDestructionType', 'NOT FOUND')}")
            
            # Load schema
            schema_path = Path(__file__).parent.parent / "schemas" / "material.json"
            with open(schema_path, 'r') as f:
                schema = json.load(f)
                material_properties = (
                    schema.get("materialProfile", {})
                    .get("profile", {})
                    .get("properties", {})
                    .get("properties", {})
                )
            
            print(f"\n📄 Schema properties found ({len(material_properties)} total):")
            for prop_key in sorted(material_properties.keys()):
                if prop_key in ['density', 'thermalDestructionPoint', 'thermalDestructionType', 'thermalConductivity']:
                    print(f"  ✓ {prop_key}: {material_properties[prop_key].get('description', 'No description')}")
            
            # Test the thermal destruction logic
            thermal_destruction_type = props.get('thermalDestructionType', 'melting')
            thermal_label = "Decomposition" if thermal_destruction_type == "decomposition" else "Melting Point"
            print(f"\n🏷️  Thermal Label Logic:")
            print(f"  thermalDestructionType: {thermal_destruction_type}")
            print(f"  Display label: {thermal_label}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to parse YAML: {e}")
            print(f"Raw YAML content (first 500 chars):")
            print(yaml_content[:500])
            return False

if __name__ == "__main__":
    import sys
    # For now, just run the basalt test since the function is hardcoded
    test_basalt_extraction()
