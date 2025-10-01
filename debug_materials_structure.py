#!/usr/bin/env python3
"""Debug script to understand Materials.yaml structure"""

import yaml

def debug_materials_yaml():
    with open("data/materials.yaml", 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print("Top-level keys in Materials.yaml:")
    for key in data.keys():
        print(f"  - {key}: {type(data[key])}")
        if isinstance(data[key], dict) and len(data[key]) < 20:
            for subkey in data[key].keys():
                print(f"    - {subkey}: {type(data[key][subkey])}")

if __name__ == "__main__":
    debug_materials_yaml()