#!/usr/bin/env python3
"""
Populate ALL remaining numeric property ranges.
Handles mixed numeric/categorical properties with unit-specific ranges.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Complete ranges for all remaining numeric values
COMPLETE_RANGES = {
    # Chemical Stability - various units
    'chemicalStability_ph': {
        'masonry': {'min': 2.0, 'max': 14.0, 'unit': 'pH'},
        'stone': {'min': 2.0, 'max': 14.0, 'unit': 'pH'}
    },
    'chemicalStability_percent': {
        'glass': {'min': 70, 'max': 99, 'unit': '% resistance'},
        'ceramic': {'min': 80, 'max': 99, 'unit': '% resistance'},
        'plastic': {'min': 50, 'max': 99, 'unit': '% resistance'},
        'composite': {'min': 60, 'max': 95, 'unit': '% resistance'},
        'stone': {'min': 80, 'max': 99, 'unit': '% resistance'}
    },
    'chemicalStability_rating': {
        'glass': {'min': 1, 'max': 10, 'unit': 'scale 1-10'},
        'stone': {'min': 1, 'max': 10, 'unit': 'rating (1-10)'},
        'wood': {'min': 1, 'max': 10, 'unit': 'rating (1-10)'},
        'composite': {'min': 1, 'max': 10, 'unit': 'rating'},
        'masonry': {'min': 1, 'max': 10, 'unit': 'rating 1-10'}
    },
    
    # Corrosion Resistance - rating
    'corrosionResistance_rating': {
        'metal': {'min': 0, 'max': 10, 'unit': 'rating_0_10'}
    },
    
    # Crystalline Structure - percent
    'crystallineStructure_percent': {
        'plastic': {'min': 0, 'max': 100, 'unit': '% crystallinity'},
        'glass': {'min': 0, 'max': 100, 'unit': '% crystallinity'}
    },
    
    # Oxidation Resistance - additional temperature case
    'oxidationResistance_temp_high': {
        'semiconductor': {'min': 800, 'max': 2000, 'unit': '°C'}
    }
}


def is_numeric_value(value) -> bool:
    """Check if value is numeric (not categorical string)."""
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value.replace(',', ''))
            return True
        except (ValueError, AttributeError):
            return False
    return False


def get_range_for_property(prop_name: str, value, unit: str, category: str) -> Optional[Dict]:
    """Get appropriate range based on property, value, unit, and category."""
    if not unit:
        return None
    
    unit_lower = unit.lower()
    
    if prop_name == 'chemicalStability':
        if 'ph' in unit_lower:
            return COMPLETE_RANGES['chemicalStability_ph'].get(category)
        elif '%' in unit_lower or 'resistance' in unit_lower or 'retention' in unit_lower:
            return COMPLETE_RANGES['chemicalStability_percent'].get(category)
        elif 'rating' in unit_lower or 'scale' in unit_lower or '1-10' in unit_lower:
            return COMPLETE_RANGES['chemicalStability_rating'].get(category)
    
    elif prop_name == 'corrosionResistance':
        if 'rating' in unit_lower or '0' in unit_lower or '10' in unit_lower:
            return COMPLETE_RANGES['corrosionResistance_rating'].get(category)
    
    elif prop_name == 'crystallineStructure':
        if '%' in unit_lower or 'crystallinity' in unit_lower:
            return COMPLETE_RANGES['crystallineStructure_percent'].get(category)
    
    elif prop_name == 'oxidationResistance':
        if '°c' in unit_lower:
            return COMPLETE_RANGES['oxidationResistance_temp_high'].get(category)
    
    return None


def populate_all_remaining_ranges(data: Dict[str, Any]) -> tuple[bool, int]:
    """
    Populate ALL remaining missing min/max values for numeric properties.
    
    Returns:
        (modified: bool, properties_updated: int)
    """
    category = data.get('category', '').lower()
    
    if 'materialProperties' not in data:
        return False, 0
    
    props = data['materialProperties']
    updated_count = 0
    
    for prop_name, prop_value in props.items():
        if not isinstance(prop_value, dict):
            continue
        
        # Check if property has min/max fields
        if 'min' not in prop_value and 'max' not in prop_value:
            continue
        
        # Check if min/max are already populated
        if prop_value.get('min') is not None and prop_value.get('max') is not None:
            continue
        
        value = prop_value.get('value')
        unit = prop_value.get('unit', '')
        
        # Skip categorical values
        if not is_numeric_value(value):
            continue
        
        # Get appropriate range
        range_data = get_range_for_property(prop_name, value, unit, category)
        
        if range_data:
            prop_value['min'] = range_data['min']
            prop_value['max'] = range_data['max']
            updated_count += 1
    
    return updated_count > 0, updated_count


def process_frontmatter_file(filepath: Path, dry_run: bool = False) -> tuple[bool, int, str]:
    """Process a single frontmatter YAML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return False, 0, "Empty file"
        
        modified, count = populate_all_remaining_ranges(data)
        
        if modified and not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                         allow_unicode=True, width=float("inf"))
        
        if count > 0:
            return True, count, f"Updated {count} properties"
        else:
            return False, 0, "No updates needed"
    
    except Exception as e:
        return False, 0, f"Error: {str(e)}"


def main():
    """Main execution function."""
    dry_run = '--dry-run' in sys.argv
    
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return 1
    
    print("=" * 80)
    print("POPULATING ALL REMAINING NUMERIC PROPERTY RANGES")
    print("=" * 80)
    if dry_run:
        print("DRY RUN MODE - No files will be modified")
        print()
    
    yaml_files = sorted(frontmatter_dir.glob('*.yaml'))
    
    stats = {
        'total': 0,
        'modified': 0,
        'skipped': 0,
        'errors': 0,
        'total_properties_updated': 0
    }
    
    for filepath in yaml_files:
        stats['total'] += 1
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            material_name = data.get('name', filepath.stem)
        
        success, prop_count, message = process_frontmatter_file(filepath, dry_run)
        
        if success:
            status = '✓' if not dry_run else '→'
            print(f"{status} {material_name}: {message}")
            stats['modified'] += 1
            stats['total_properties_updated'] += prop_count
        elif "Error" not in message:
            stats['skipped'] += 1
        else:
            print(f"✗ {material_name}: {message}")
            stats['errors'] += 1
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {stats['total']}")
    print(f"Files modified: {stats['modified']}")
    print(f"Total properties updated: {stats['total_properties_updated']}")
    print(f"Files skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print()
    
    if dry_run:
        print("DRY RUN COMPLETE - Run without --dry-run to apply changes")
    else:
        print("✅ ALL REMAINING RANGES POPULATED")
    
    return 0 if stats['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
