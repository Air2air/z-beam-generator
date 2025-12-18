#!/usr/bin/env python3
"""
Normalize properties structure across ALL data files.

CANONICAL STRUCTURE (from frontmatter_template.yaml):
properties:
  material_characteristics:
    label: Material Characteristics
    <property_name>:
      value: <number>
      unit: <string>
      min: <number>  # Optional
      max: <number>  # Optional
      research_basis: <string>  # Maps from 'source'
  laser_material_interaction:
    label: Laser-Material Interaction
    <property_name>:
      value: <number>
      unit: <string>
      research_basis: <string>

This script:
1. Loads property taxonomy from Categories.yaml
2. Categorizes flat properties using taxonomy
3. Flattens double-nested values
4. Renames 'source' → 'research_basis'
5. Removes 'confidence' field
6. Updates Materials.yaml in place with backup
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Set

# Load property taxonomy
CATEGORIES_PATH = Path("data/materials/Categories.yaml")
MATERIALS_PATH = Path("data/materials/Materials.yaml")

def load_property_taxonomy() -> Dict[str, str]:
    """Load property taxonomy: property_name -> category_id"""
    with open(CATEGORIES_PATH) as f:
        data = yaml.safe_load(f)
    
    # Find the taxonomy (it's nested in the file)
    taxonomy_data = data
    for key in data.keys():
        if isinstance(data[key], dict) and 'categories' in data[key]:
            taxonomy_data = data[key]
            break
    
    categories = taxonomy_data.get('categories', {})
    
    # Build mapping
    property_map = {}
    for cat_id in ['material_characteristics', 'laser_material_interaction']:
        if cat_id in categories:
            props = categories[cat_id].get('properties', [])
            for prop in props:
                property_map[prop] = cat_id
    
    return property_map

def flatten_property_value(prop_value: Any) -> Dict:
    """
    Flatten double-nested property structure.
    
    Input:  {'value': {'value': 420.0, 'unit': '', 'confidence': 1.0}, 
             'unit': 'kg/m³', 'confidence': {'value': 95, ...}, 'source': 'ai_research'}
    Output: {'value': 420.0, 'unit': 'kg/m³', 'research_basis': 'ai_research'}
    """
    if not isinstance(prop_value, dict):
        return prop_value
    
    flattened = {}
    
    for key, value in prop_value.items():
        if key == 'value':
            if isinstance(value, dict) and 'value' in value:
                # Extract nested value
                flattened['value'] = value['value']
            else:
                flattened['value'] = value
        elif key == 'unit':
            if isinstance(value, dict) and 'value' in value:
                # Sometimes unit is nested too
                flattened['unit'] = value.get('unit', '')
            else:
                flattened['unit'] = value
        elif key == 'source':
            # Rename to research_basis
            flattened['research_basis'] = value
        elif key == 'min':
            flattened['min'] = value
        elif key == 'max':
            flattened['max'] = value
        # Skip confidence, skip nested confidence dict
    
    return flattened

def normalize_material_properties(properties: Dict, taxonomy: Dict[str, str]) -> Dict:
    """
    Normalize properties to canonical grouped structure.
    """
    # Initialize canonical structure
    normalized = {
        'material_characteristics': {
            'label': 'Material Characteristics'
        },
        'laser_material_interaction': {
            'label': 'Laser-Material Interaction'
        }
    }
    
    # Categorize each property
    for prop_name, prop_value in properties.items():
        # Skip metadata fields
        if prop_name in ['label', 'description', 'percentage', 'material_characteristics', 'laser_material_interaction']:
            continue
        
        # Get category from taxonomy
        category_id = taxonomy.get(prop_name)
        if not category_id:
            print(f"  ⚠️  Property '{prop_name}' not in taxonomy - skipping")
            continue
        
        # Flatten and clean the property value
        flattened_value = flatten_property_value(prop_value)
        
        # Add to appropriate category
        normalized[category_id][prop_name] = flattened_value
    
    return normalized

def normalize_materials_yaml():
    """Normalize Materials.yaml structure."""
    print("=" * 80)
    print("NORMALIZING MATERIALPROPERTIES STRUCTURE")
    print("=" * 80)
    print()
    
    # Load taxonomy
    print("📖 Loading property taxonomy...")
    taxonomy = load_property_taxonomy()
    print(f"✅ Loaded taxonomy with {len(taxonomy)} properties")
    print()
    
    # Backup Materials.yaml
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = MATERIALS_PATH.parent / f"Materials.backup_{timestamp}.yaml"
    shutil.copy(MATERIALS_PATH, backup_path)
    print(f"💾 Backup created: {backup_path.name}")
    print()
    
    # Load Materials.yaml
    print("📂 Loading Materials.yaml...")
    with open(MATERIALS_PATH) as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"✅ Loaded {len(materials)} materials")
    print()
    
    # Normalize each material
    print("🔧 Normalizing properties structure...")
    normalized_count = 0
    skipped_count = 0
    
    for material_name, material_data in materials.items():
        properties = material_data.get('properties', {})
        if not properties:
            print(f"  ⏭️  {material_name}: No properties - skipping")
            skipped_count += 1
            continue
        
        # Check if already normalized
        if ('material_characteristics' in properties and 
            isinstance(properties.get('material_characteristics'), dict) and
            'label' in properties.get('material_characteristics', {})):
            # Already has correct structure - but may have properties outside
            # Count properties outside categories
            outside_props = [k for k in properties.keys() 
                           if k not in ['material_characteristics', 'laser_material_interaction']]
            if not outside_props:
                print(f"  ✓  {material_name}: Already normalized")
                continue
            print(f"  🔧 {material_name}: Has {len(outside_props)} properties outside categories")
        
        # Normalize
        normalized_properties = normalize_material_properties(properties, taxonomy)
        material_data['properties'] = normalized_properties
        normalized_count += 1
        print(f"  ✅ {material_name}: Normalized")
    
    print()
    print(f"📊 Summary:")
    print(f"   ✅ Normalized: {normalized_count}")
    print(f"   ✓  Already correct: {len(materials) - normalized_count - skipped_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print()
    
    # Save normalized data
    print("💾 Saving normalized Materials.yaml...")
    with open(MATERIALS_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                  sort_keys=False, width=1000)
    
    print("✅ Materials.yaml normalized successfully!")
    print()
    print("=" * 80)
    print("NORMALIZATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    normalize_materials_yaml()
