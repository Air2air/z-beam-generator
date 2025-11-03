#!/usr/bin/env python3
"""
Normalize Materials.yaml to Match Frontmatter Template Structure

CANONICAL REFERENCE: materials/data/frontmatter_template.yaml

This script ensures ALL materials in Materials.yaml follow the exact structure
and field ordering defined in frontmatter_template.yaml.

KEY NORMALIZATIONS:
1. Field Ordering: Ensure canonical order from frontmatter_template.yaml
2. GROUPED Structure: Verify materialProperties has proper category groups
3. Properties Structure: Each group must have label, description, properties dict
4. Required Fields: Ensure name, category, subcategory, title, subtitle exist
5. Cleanup: Remove deprecated fields, normalize naming

Usage:
    python3 scripts/tools/normalize_materials_to_template.py [--dry-run] [--material NAME]
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import OrderedDict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from materials.data.materials import load_materials

def dict_representer(dumper, data):
    """Custom representer to convert OrderedDict to regular dict for YAML."""
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

def save_materials(data):
    """Save materials data back to Materials.yaml."""
    # Register custom representer for OrderedDict
    yaml.add_representer(OrderedDict, dict_representer)
    
    # Convert OrderedDicts to regular dicts for cleaner YAML
    def convert_to_dict(obj):
        if isinstance(obj, OrderedDict):
            return {k: convert_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, dict):
            return {k: convert_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_dict(item) for item in obj]
        return obj
    
    clean_data = convert_to_dict(data)
    
    materials_path = project_root / 'materials' / 'data' / 'Materials.yaml'
    with open(materials_path, 'w') as f:
        yaml.dump(clean_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

# Canonical field order from frontmatter_template.yaml
CANONICAL_ORDER = [
    'name', 'category', 'subcategory', 'title', 'subtitle', 'description',
    'author', 'images', 'caption', 'regulatoryStandards', 'applications',
    'materialProperties', 'materialCharacteristics', 'machineSettings',
    'faq', '_metadata'
]

# GROUPED structure requirements
REQUIRED_GROUPS = {
    'material_characteristics': {
        'label': 'Material Characteristics',
        'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
    },
    'laser_material_interaction': {
        'label': 'Laser-Material Interaction',
        'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds'
    }
}


def reorder_fields(data: Dict) -> OrderedDict:
    """Reorder fields to match canonical order."""
    ordered = OrderedDict()
    for field in CANONICAL_ORDER:
        if field in data:
            ordered[field] = data[field]
    # Add any remaining fields
    for field, value in data.items():
        if field not in ordered:
            ordered[field] = value
    return ordered


def ensure_grouped_properties(data: Dict) -> Dict:
    """Ensure materialProperties has proper GROUPED structure."""
    if 'materialProperties' not in data:
        data['materialProperties'] = {}
    
    mat_props = data['materialProperties']
    
    for group_name, group_config in REQUIRED_GROUPS.items():
        if group_name not in mat_props:
            mat_props[group_name] = {
                'label': group_config['label'],
                'description': group_config['description'],
                'properties': {}
            }
        else:
            group = mat_props[group_name]
            # Ensure required keys
            if 'label' not in group:
                group['label'] = group_config['label']
            if 'description' not in group:
                group['description'] = group_config['description']
            if 'properties' not in group:
                # Migrate non-metadata keys to properties dict
                properties = {}
                for key in list(group.keys()):
                    if key not in {'label', 'description', 'percentage', 'properties'}:
                        properties[key] = group.pop(key)
                group['properties'] = properties
    
    return data


def normalize_material(name: str, data: Dict, dry_run: bool = False) -> tuple:
    """Normalize a single material."""
    warnings = []
    
    # Required fields check
    for field in ['name', 'category', 'subcategory', 'title', 'subtitle']:
        if field not in data:
            warnings.append(f"Missing required field: {field}")
    
    if dry_run:
        return data, warnings
    
    # Apply normalizations
    data = ensure_grouped_properties(data)
    data = reorder_fields(data)
    
    return data, warnings


def main():
    parser = argparse.ArgumentParser(description='Normalize Materials.yaml to match frontmatter_template.yaml')
    parser.add_argument('--dry-run', action='store_true', help='Validate only, do not modify')
    parser.add_argument('--material', type=str, help='Normalize specific material only')
    args = parser.parse_args()
    
    print(f"{'='*80}")
    print(f"NORMALIZE MATERIALS TO FRONTMATTER TEMPLATE")
    print(f"{'='*80}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'NORMALIZATION'}")
    print(f"Target: {args.material if args.material else 'All materials'}")
    print()
    
    materials_data = load_materials()
    materials = materials_data.get('materials', {})
    
    if args.material:
        if args.material not in materials:
            print(f"❌ Material '{args.material}' not found")
            return
        materials = {args.material: materials[args.material]}
    
    total = len(materials)
    processed = 0
    warnings_count = 0
    
    for name, data in materials.items():
        normalized, warnings = normalize_material(name, data, args.dry_run)
        
        if warnings:
            print(f"⚠️  {name}: {len(warnings)} warnings")
            for w in warnings:
                print(f"    - {w}")
            warnings_count += 1
        else:
            print(f"✅ {name}")
        
        if not args.dry_run:
            materials_data['materials'][name] = normalized
            processed += 1
    
    print()
    print(f"{'='*80}")
    print(f"Processed: {total} | Warnings: {warnings_count}")
    
    if not args.dry_run and processed > 0:
        print(f"💾 Saving Materials.yaml...")
        save_materials(materials_data)
        print(f"✅ Saved {processed} normalized materials")
    
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
