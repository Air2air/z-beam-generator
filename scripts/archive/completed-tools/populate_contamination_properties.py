#!/usr/bin/env python3
"""
Populate Contamination Properties in Materials.yaml

Auto-populates contamination properties for all materials based on:
1. Existing definitions in contaminants schema.yaml
2. Category-based inference for materials not in schema

Author: AI Assistant
Date: November 25, 2025
"""

import yaml
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains.contaminants import get_library


def infer_from_category(category: str, material_name: str) -> dict:
    """
    Infer contamination properties from material category.
    
    Args:
        category: Material category (e.g., "metals_ferrous", "polymers_thermoplastic")
        material_name: Name of the material
        
    Returns:
        Dict with valid/prohibited/conditional contamination lists
    """
    category_lower = category.lower()
    
    # Ferrous metals (iron-containing)
    if 'ferrous' in category_lower or material_name.lower() in ['steel', 'iron', 'cast iron']:
        return {
            'valid': [
                'rust_oxidation',
                'industrial_oil',
                'environmental_dust',
                'scale_buildup',
                'paint_residue',
                'chemical_stains'
            ],
            'prohibited': [
                'copper_patina',
                'aluminum_oxidation',
                'wood_rot',
                'uv_chalking'
            ],
            'conditional': {}
        }
    
    # Non-ferrous metals (aluminum, copper, brass, bronze, etc.)
    elif 'metal' in category_lower and 'ferrous' not in category_lower:
        valid = ['industrial_oil', 'environmental_dust', 'scale_buildup', 'paint_residue', 'chemical_stains']
        prohibited = ['rust_oxidation', 'wood_rot', 'uv_chalking']
        
        # Check for specific metal types
        if 'aluminum' in material_name.lower() or 'alumin' in material_name.lower():
            valid.insert(0, 'aluminum_oxidation')
            prohibited.append('copper_patina')
        elif any(metal in material_name.lower() for metal in ['copper', 'brass', 'bronze']):
            valid.insert(0, 'copper_patina')
            prohibited.append('aluminum_oxidation')
        else:
            # Other metals - don't know which oxidation
            prohibited.extend(['copper_patina', 'aluminum_oxidation'])
        
        return {
            'valid': valid,
            'prohibited': prohibited,
            'conditional': {}
        }
    
    # Polymers/Plastics
    elif 'polymer' in category_lower or 'plastic' in category_lower:
        return {
            'valid': [
                'uv_chalking',
                'chemical_stains',
                'environmental_dust',
                'adhesive_residue'
            ],
            'prohibited': [
                'rust_oxidation',
                'copper_patina',
                'aluminum_oxidation',
                'wood_rot'
            ],
            'conditional': {
                'industrial_oil': {
                    'context': 'machinery_parts_only',
                    'note': 'Only if plastic is part of machinery (gears, housings)'
                }
            }
        }
    
    # Wood
    elif 'wood' in category_lower or 'timber' in category_lower:
        return {
            'valid': [
                'wood_rot',
                'environmental_dust',
                'chemical_stains',
                'paint_residue'
            ],
            'prohibited': [
                'rust_oxidation',
                'copper_patina',
                'aluminum_oxidation',
                'uv_chalking'
            ],
            'conditional': {}
        }
    
    # Ceramics/Glass
    elif 'ceramic' in category_lower or 'glass' in category_lower or 'stone' in category_lower:
        return {
            'valid': [
                'environmental_dust',
                'scale_buildup',
                'chemical_stains',
                'paint_residue'
            ],
            'prohibited': [
                'rust_oxidation',
                'copper_patina',
                'aluminum_oxidation',
                'wood_rot',
                'uv_chalking'
            ],
            'conditional': {}
        }
    
    # Composites (often fiber-reinforced polymers)
    elif 'composite' in category_lower or 'fiber' in category_lower:
        return {
            'valid': [
                'uv_chalking',
                'environmental_dust',
                'chemical_stains',
                'adhesive_residue'
            ],
            'prohibited': [
                'rust_oxidation',
                'copper_patina',
                'aluminum_oxidation',
                'wood_rot'
            ],
            'conditional': {
                'industrial_oil': {
                    'context': 'machinery_parts_only',
                    'note': 'Only if composite is part of machinery'
                }
            }
        }
    
    # Unknown - conservative defaults
    else:
        return {
            'valid': [
                'environmental_dust',
                'chemical_stains'
            ],
            'prohibited': [],
            'conditional': {},
            '_needs_review': True,
            '_note': f'Category "{category}" not recognized - conservative defaults applied'
        }


def main():
    """Main population function"""
    
    print("🔧 Populating Contamination Properties in Materials.yaml\n")
    print("="*80)
    
    # Load contaminants library
    library = get_library()
    print(f"✅ Loaded contaminants library: {len(library.list_patterns())} patterns, {len(library.list_materials())} materials\n")
    
    # Load Materials.yaml
    materials_path = Path(__file__).parent.parent.parent / 'data' / 'materials' / 'Materials.yaml'
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"📦 Loaded Materials.yaml: {len(materials)} materials\n")
    
    # Track statistics
    already_populated = 0
    from_schema = 0
    inferred = 0
    needs_review = 0
    
    # Process each material
    for mat_name, mat_data in materials.items():
        # Skip if already has contamination properties
        if 'contamination' in mat_data:
            already_populated += 1
            continue
        
        # Try to get from contaminants schema
        mat_props = library.get_material(mat_name)
        if mat_props:
            mat_data['contamination'] = {
                'valid': mat_props.valid_contamination,
                'prohibited': mat_props.prohibited_contamination,
                'conditional': mat_props.conditional_contamination
            }
            from_schema += 1
            print(f"✅ {mat_name}: From schema")
        else:
            # Infer from category
            category = mat_data.get('category', 'unknown')
            contamination = infer_from_category(category, mat_name)
            
            # Mark as needing review if uncertain
            if contamination.get('_needs_review'):
                needs_review += 1
                print(f"⚠️  {mat_name}: Inferred (NEEDS REVIEW) - {contamination.get('_note', '')}")
            else:
                inferred += 1
                print(f"📝 {mat_name}: Inferred from category '{category}'")
            
            mat_data['contamination'] = contamination
    
    print("\n" + "="*80)
    print("\n📊 Population Statistics:")
    print(f"   • Already populated: {already_populated}")
    print(f"   • From schema: {from_schema}")
    print(f"   • Inferred: {inferred}")
    print(f"   • Needs review: {needs_review}")
    print(f"   • Total: {len(materials)}")
    
    # Calculate coverage
    populated = len(materials) - already_populated
    print(f"\n✅ Populated {populated} materials ({populated/len(materials)*100:.1f}%)")
    
    # Save updated Materials.yaml
    backup_path = materials_path.parent / 'Materials.yaml.backup'
    print(f"\n💾 Creating backup: {backup_path}")
    with open(backup_path, 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"💾 Saving updated Materials.yaml...")
    with open(materials_path, 'w') as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("\n✅ Population complete!")
    
    if needs_review > 0:
        print(f"\n⚠️  {needs_review} materials marked for review")
        print("   Search for '_needs_review: true' in Materials.yaml")


if __name__ == '__main__':
    main()
