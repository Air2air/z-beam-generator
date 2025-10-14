#!/usr/bin/env python3
"""
Populate final numeric property ranges.
Only updates properties with numeric values, skips categorical.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import sys

# Ranges for properties with mixed numeric/categorical values
MIXED_PROPERTY_RANGES = {
    # Oxidation Resistance - multiple units/meanings
    'oxidationResistance_temp': {  # Temperature-based (°C)
        'metal': {'min': 200, 'max': 2000, 'unit': '°C'},
        'ceramic': {'min': 1000, 'max': 2500, 'unit': '°C'},
        'composite': {'min': 200, 'max': 1700, 'unit': '°C'}
    },
    'oxidationResistance_rate': {  # Rate-based (nm/hour or mg/cm²·h)
        'metal': {'min': 0.1, 'max': 10.0, 'unit': 'nm/hour'}
    },
    'oxidationResistance_percent': {  # Retention (%)
        'composite': {'min': 50, 'max': 100, 'unit': '% retention'},
        'plastic': {'min': 40, 'max': 95, 'unit': '% retention'}
    },
    'oxidationResistance_rating': {  # Rating scale (1-10)
        'metal': {'min': 1, 'max': 10, 'unit': 'rating (1-10)'}
    },
    
    # Thermal Shock Resistance - temperature or thermal conductivity based
    'thermalShockResistance_temp': {  # Temperature (°C or ΔT)
        'glass': {'min': 50, 'max': 1200, 'unit': '°C'},
        'ceramic': {'min': 100, 'max': 1500, 'unit': 'ΔT °C'},
        'semiconductor': {'min': 200, 'max': 1000, 'unit': 'ΔT °C'}
    },
    'thermalShockResistance_conductivity': {  # W/m
        'metal': {'min': 50, 'max': 400, 'unit': 'W/m'}
    }
}


def is_numeric_value(value) -> bool:
    """Check if value is numeric (not categorical)."""
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value.replace(',', ''))
            return True
        except (ValueError, AttributeError):
            return False
    return False


def get_oxidation_resistance_range(value, unit: str, category: str):
    """Determine appropriate range for oxidationResistance based on unit."""
    if not unit:
        return None
    
    unit_lower = unit.lower()
    
    if '°c' in unit_lower or 'temp' in unit_lower:
        return MIXED_PROPERTY_RANGES['oxidationResistance_temp'].get(category)
    elif 'nm' in unit_lower or 'mg' in unit_lower or 'hour' in unit_lower:
        return MIXED_PROPERTY_RANGES['oxidationResistance_rate'].get(category)
    elif '%' in unit_lower or 'retention' in unit_lower:
        return MIXED_PROPERTY_RANGES['oxidationResistance_percent'].get(category)
    elif 'rating' in unit_lower or '1-10' in unit_lower:
        return MIXED_PROPERTY_RANGES['oxidationResistance_rating'].get(category)
    
    return None


def get_thermal_shock_range(value, unit: str, category: str):
    """Determine appropriate range for thermalShockResistance based on unit."""
    if not unit:
        return None
    
    unit_lower = unit.lower()
    
    if '°c' in unit_lower or 'δt' in unit_lower or 'delta' in unit_lower:
        return MIXED_PROPERTY_RANGES['thermalShockResistance_temp'].get(category)
    elif 'w/m' in unit_lower:
        return MIXED_PROPERTY_RANGES['thermalShockResistance_conductivity'].get(category)
    
    return None


def populate_final_ranges(data: Dict[str, Any]) -> tuple[bool, int]:
    """
    Populate missing min/max values for numeric properties only.
    
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
        
        # Handle special properties with mixed types
        range_data = None
        
        if prop_name == 'oxidationResistance':
            range_data = get_oxidation_resistance_range(value, unit, category)
        elif prop_name == 'thermalShockResistance':
            range_data = get_thermal_shock_range(value, unit, category)
        
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
        
        modified, count = populate_final_ranges(data)
        
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
    print("POPULATING FINAL NUMERIC PROPERTY RANGES")
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
        print("✅ POPULATION COMPLETE")
    
    return 0 if stats['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
