#!/usr/bin/env python3
"""
Thermal Destruction Migration Script
Migrates Materials.yaml from melting point to thermal destruction terminology
"""

import yaml
import os
from pathlib import Path
import re
from typing import Dict, Any, Optional
import argparse

# Thermal destruction type mappings based on category
CATEGORY_THERMAL_DESTRUCTION_TYPES = {
    'metal': 'melting',
    'ceramic': 'thermal_shock', 
    'glass': 'softening',
    'plastic': 'melting',  # Will be refined per material
    'composite': 'decomposition',
    'wood': 'carbonization',
    'stone': 'thermal_shock',
    'masonry': 'spalling',
    'semiconductor': 'melting'
}

# Special cases for materials that don't follow category defaults
MATERIAL_SPECIAL_CASES = {
    'PVC': 'decomposition',  # PVC decomposes rather than melts
    'Bakelite': 'decomposition',  # Thermoset plastic
    'Epoxy': 'decomposition',  # Thermoset
    'Polyurethane': 'decomposition',  # Can decompose
    'PTFE': 'decomposition',  # Teflon decomposes at high temp
    'Concrete': 'spalling',
    'Mortar': 'spalling', 
    'Limestone': 'calcination',  # CaCO3 -> CaO + CO2
    'Marble': 'calcination',  # Limestone-based
    'Gypsum': 'calcination',  # Dehydration
}

def extract_temperature_from_melting_point(melting_point_str: str) -> Optional[float]:
    """Extract temperature value from melting point string"""
    if not melting_point_str:
        return None
    
    # Remove units and extract numeric value
    cleaned = str(melting_point_str).replace('°C', '').replace('°F', '').replace(',', '')
    
    # Handle ranges (take midpoint)
    if '-' in cleaned:
        try:
            parts = cleaned.split('-')
            if len(parts) == 2:
                min_temp = float(parts[0].strip())
                max_temp = float(parts[1].strip())
                return (min_temp + max_temp) / 2.0
        except ValueError:
            pass
    
    # Handle single values
    try:
        # Extract first number found
        numbers = re.findall(r'-?\d+\.?\d*', cleaned)
        if numbers:
            return float(numbers[0])
    except ValueError:
        pass
    
    return None

def determine_thermal_destruction_type(material_name: str, category: str) -> str:
    """Determine thermal destruction type for a material"""
    
    # Check special cases first
    material_name_clean = material_name.strip()
    for special_material, destruction_type in MATERIAL_SPECIAL_CASES.items():
        if special_material.lower() in material_name_clean.lower():
            return destruction_type
    
    # Use category default
    return CATEGORY_THERMAL_DESTRUCTION_TYPES.get(category, 'melting')

def update_material_thermal_properties(material, category_thermal_type):
    """Update a material's thermal properties with thermal destruction terminology."""
    properties = material.get('properties', {})
    material_name = material.get('name', 'Unknown')
    updated = False
    
    # Add thermal destruction type if missing
    if 'thermalDestructionType' not in properties:
        properties['thermalDestructionType'] = {
            'value': category_thermal_type,
            'confidence': 0.8,
            'source': 'category_default'
        }
        print(f"    🆕 Added thermalDestructionType '{category_thermal_type}' to {material_name}")
        updated = True
    
    # Check if material already has thermal destruction point
    if 'thermalDestructionPoint' in properties:
        if not updated:
            print(f"    ✅ {material_name} already has complete thermal destruction properties")
        return updated
    
    # Look for melting point to convert
    melting_point = properties.get('meltingPoint')
    if melting_point:
        # Extract temperature value
        if isinstance(melting_point, dict):
            temp_value = melting_point.get('value')
            temp_unit = melting_point.get('unit', '°C')
        elif isinstance(melting_point, str):
            # Try to extract temperature from string like "1500°C"
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', melting_point)
            temp_value = float(match.group(1)) if match else None
            temp_unit = '°C'
        else:
            temp_value = melting_point
            temp_unit = '°C'
        
        if temp_value:
            # Create thermal destruction point
            properties['thermalDestructionPoint'] = {
                'value': temp_value,
                'unit': temp_unit,
                'confidence': melting_point.get('confidence', 0.7) if isinstance(melting_point, dict) else 0.7,
                'source': 'migrated_from_melting_point'
            }
            
            # Remove old melting point
            del properties['meltingPoint']
            
            print(f"    🔄 Migrated {material_name}: {temp_value}{temp_unit}")
            return True
    
    if not updated:
        print(f"    ⭕ {material_name}: No changes needed")
    return updated

def migrate_materials_yaml(dry_run: bool = True) -> Dict[str, Any]:
    """Migrate Materials.yaml from melting point to thermal destruction fields"""
    
    materials_file = Path("data/Materials.yaml")
    if not materials_file.exists():
        return {'error': 'Materials.yaml not found'}
    
    print(f"🔄 {'DRY RUN: ' if dry_run else ''}Migrating Materials.yaml to thermal destruction terminology")
    print("=" * 80)
    
    # Load Materials.yaml
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    migration_stats = {
        'materials_processed': 0,
        'melting_points_found': 0,
        'thermal_destruction_added': 0,
        'special_cases_applied': 0,
        'errors': []
    }
    
    # Process each category
    materials_section = materials_data.get('materials', {})
    
    for category_name, category_data in materials_section.items():
        items = category_data.get('items', [])
        
        print(f"\n📂 Processing {category_name.upper()} category ({len(items)} materials)")
        
        for item in items:
            material_name = item.get('name', 'Unknown')
            migration_stats['materials_processed'] += 1
            
            # Get category thermal destruction type
            category_thermal_type = determine_thermal_destruction_type(material_name, category_name)
            
            # Update material thermal properties
            if update_material_thermal_properties(item, category_thermal_type):
                migration_stats['thermal_destruction_added'] += 1
    
    # Save updated data if not dry run
    if not dry_run:
        # Create backup
        backup_file = materials_file.with_suffix('.yaml.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True)
        print(f"\n💾 Backup created: {backup_file}")
        
        # Save updated file
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True)
        print(f"✅ Updated {materials_file}")
    
    # Print migration summary
    print(f"\n📊 Migration Summary:")
    print(f"   Materials processed: {migration_stats['materials_processed']}")
    print(f"   Melting points found: {migration_stats['melting_points_found']}")
    print(f"   Thermal destruction added: {migration_stats['thermal_destruction_added']}")
    print(f"   Special cases applied: {migration_stats['special_cases_applied']}")
    print(f"   Errors: {len(migration_stats['errors'])}")
    
    if migration_stats['errors']:
        print(f"\n❌ Errors encountered:")
        for error in migration_stats['errors'][:10]:  # Show first 10 errors
            print(f"     {error}")
        if len(migration_stats['errors']) > 10:
            print(f"     ... and {len(migration_stats['errors']) - 10} more")
    
    return migration_stats

def cleanup_melting_points(dry_run: bool = True) -> Dict[str, Any]:
    """Remove melting point fields after thermal destruction migration is complete"""
    
    materials_file = Path("data/Materials.yaml")
    if not materials_file.exists():
        return {'error': 'Materials.yaml not found'}
    
    print(f"\n🧹 {'DRY RUN: ' if dry_run else ''}Removing old melting point fields")
    print("=" * 80)
    
    # Load Materials.yaml
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    cleanup_stats = {
        'melting_points_removed': 0,
        'materials_checked': 0
    }
    
    # Process each category
    materials_section = materials_data.get('materials', {})
    
    for category_name, category_data in materials_section.items():
        items = category_data.get('items', [])
        
        for item in items:
            material_name = item.get('name', 'Unknown')
            properties = item.get('properties', {})
            cleanup_stats['materials_checked'] += 1
            
            if 'meltingPoint' in properties:
                if not dry_run:
                    del properties['meltingPoint']
                cleanup_stats['melting_points_removed'] += 1
                print(f"   🗑️  Removed meltingPoint from {material_name}")
    
    # Save updated data if not dry run
    if not dry_run:
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True)
        print(f"✅ Cleanup complete: {materials_file}")
    
    print(f"\n📊 Cleanup Summary:")
    print(f"   Materials checked: {cleanup_stats['materials_checked']}")
    print(f"   Melting points removed: {cleanup_stats['melting_points_removed']}")
    
    return cleanup_stats

def main():
    parser = argparse.ArgumentParser(description='Migrate Materials.yaml thermal destruction terminology')
    parser.add_argument('--execute', action='store_true', help='Execute migration (default is dry run)')
    parser.add_argument('--cleanup', action='store_true', help='Remove old melting point fields')
    parser.add_argument('--validate', action='store_true', help='Validate migration results')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if args.cleanup:
        cleanup_melting_points(dry_run=dry_run)
    else:
        migration_stats = migrate_materials_yaml(dry_run=dry_run)
        
        if args.validate and not dry_run:
            print(f"\n🔍 Running validation...")
            os.system("python3 run.py --validate")

if __name__ == "__main__":
    main()