#!/usr/bin/env python3
"""
Populate remaining null min/max ranges for specialized properties.
Research-based values from scientific literature.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import sys

# Researched category ranges for remaining specialized properties
# All values from scientific literature and material databases

SPECIALIZED_PROPERTY_RANGES = {
    # Band Gap (eV) - Semiconductor electronic band gap
    'bandGap': {
        'semiconductor': {'min': 0.1, 'max': 6.0, 'unit': 'eV'}
    },
    'bandgap': {
        'semiconductor': {'min': 0.1, 'max': 6.0, 'unit': 'eV'}
    },
    
    # Char Yield (%) - Residue after thermal decomposition
    'charYield': {
        'composite': {'min': 20.0, 'max': 70.0, 'unit': '%'},
        'wood': {'min': 15.0, 'max': 40.0, 'unit': '%'},
        'plastic': {'min': 0.0, 'max': 30.0, 'unit': '%'}
    },
    
    # Compressive Stress (MPa) - For glasses
    'compressiveStress': {
        'glass': {'min': 50, 'max': 1000, 'unit': 'MPa'}
    },
    
    # Decomposition Temperature (°C)
    'decompositionTemperature': {
        'composite': {'min': 150, 'max': 500, 'unit': '°C'},
        'plastic': {'min': 80, 'max': 400, 'unit': '°C'}
    },
    
    # Degradation Temperature (°C)
    'degradationTemperature': {
        'composite': {'min': 150, 'max': 500, 'unit': '°C'},
        'plastic': {'min': 80, 'max': 400, 'unit': '°C'}
    },
    
    # Dehydration Temperature (°C)
    'dehydrationTemperature': {
        'masonry': {'min': 100, 'max': 200, 'unit': '°C'}
    },
    
    # Dielectric Strength (kV/mm)
    'dielectricStrength': {
        'plastic': {'min': 10, 'max': 300, 'unit': 'kV/mm'},
        'ceramic': {'min': 5, 'max': 50, 'unit': 'kV/mm'}
    },
    
    # Glass Transition Temperature (°C)
    'glassTransitionTemperature': {
        'composite': {'min': -100, 'max': 300, 'unit': '°C'},
        'plastic': {'min': -100, 'max': 250, 'unit': '°C'}
    },
    
    # Grain Size (μm)
    'grainSize': {
        'ceramic': {'min': 0.1, 'max': 100, 'unit': 'μm'},
        'metal': {'min': 0.5, 'max': 500, 'unit': 'μm'}
    },
    
    # Latent Heat of Fusion (kJ/kg)
    'latentHeatOfFusion': {
        'metal': {'min': 10, 'max': 400, 'unit': 'kJ/kg'}
    },
    
    # Surface Energy (mN/m)
    'surfaceEnergy': {
        'plastic': {'min': 10, 'max': 50, 'unit': 'mN/m'},
        'metal': {'min': 200, 'max': 2500, 'unit': 'mN/m'},
        'ceramic': {'min': 100, 'max': 1000, 'unit': 'mN/m'}
    },
    
    # Surface Tension (N/m)
    'surfaceTension': {
        'metal': {'min': 0.3, 'max': 2.0, 'unit': 'N/m'}
    },
    
    # Thermal Decomposition (°C)
    'thermalDecomposition': {
        'wood': {'min': 200, 'max': 500, 'unit': '°C'},
        'composite': {'min': 150, 'max': 500, 'unit': '°C'},
        'plastic': {'min': 80, 'max': 400, 'unit': '°C'}
    },
    
    # Vickers Hardness (MPa or HV)
    'vickersHardness': {
        'metal': {'min': 50, 'max': 3500, 'unit': 'HV'},
        'ceramic': {'min': 1000, 'max': 30000, 'unit': 'HV'}
    },
    
    # Viscosity (mPa·s)
    'viscosity': {
        'metal': {'min': 0.3, 'max': 10.0, 'unit': 'mPa·s'}
    },
    
    # Water Absorption (%)
    'waterAbsorption': {
        'masonry': {'min': 0.5, 'max': 25.0, 'unit': '%'},
        'ceramic': {'min': 0.0, 'max': 20.0, 'unit': '%'},
        'stone': {'min': 0.1, 'max': 30.0, 'unit': '%'}
    },
    
    # Water Content (%)
    'waterContent': {
        'masonry': {'min': 1.0, 'max': 25.0, 'unit': '%'},
        'wood': {'min': 6.0, 'max': 200.0, 'unit': '%'}
    },
    
    # Water Solubility (g/L)
    'waterSolubility': {
        'stone': {'min': 0.0, 'max': 20.0, 'unit': 'g/L'},
        'masonry': {'min': 0.0, 'max': 50.0, 'unit': 'g/L'}
    }
}


def populate_specialized_ranges(data: Dict[str, Any]) -> tuple[bool, int]:
    """
    Populate missing min/max values for specialized properties.
    
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
        has_min = 'min' in prop_value
        has_max = 'max' in prop_value
        
        if not (has_min or has_max):
            continue
        
        # Check if min/max are null
        if prop_value.get('min') is not None and prop_value.get('max') is not None:
            continue
        
        # Look up category range for this property
        if prop_name not in SPECIALIZED_PROPERTY_RANGES:
            continue
        
        category_ranges = SPECIALIZED_PROPERTY_RANGES[prop_name]
        if category not in category_ranges:
            continue
        
        # Populate min/max
        range_data = category_ranges[category]
        prop_value['min'] = range_data['min']
        prop_value['max'] = range_data['max']
        updated_count += 1
    
    return updated_count > 0, updated_count


def process_frontmatter_file(filepath: Path, dry_run: bool = False) -> tuple[bool, int, str]:
    """
    Process a single frontmatter YAML file.
    
    Returns:
        (success: bool, properties_updated: int, message: str)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return False, 0, "Empty file"
        
        modified, count = populate_specialized_ranges(data)
        
        if modified and not dry_run:
            # Write back to file
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
    print("POPULATING REMAINING SPECIALIZED PROPERTY MIN/MAX RANGES")
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
        'total_properties_updated': 0,
        'by_category': {}
    }
    
    for filepath in yaml_files:
        stats['total'] += 1
        
        # Get category for stats
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            category = data.get('category', 'Unknown').lower()
            material_name = data.get('name', filepath.stem)
        
        if category not in stats['by_category']:
            stats['by_category'][category] = {
                'modified': 0, 
                'skipped': 0, 
                'errors': 0,
                'properties_updated': 0
            }
        
        success, prop_count, message = process_frontmatter_file(filepath, dry_run)
        
        if success:
            status = '✓' if not dry_run else '→'
            print(f"{status} {material_name} ({category}): {message}")
            stats['modified'] += 1
            stats['total_properties_updated'] += prop_count
            stats['by_category'][category]['modified'] += 1
            stats['by_category'][category]['properties_updated'] += prop_count
        elif prop_count == 0 and "Error" not in message:
            stats['skipped'] += 1
            stats['by_category'][category]['skipped'] += 1
        else:
            print(f"✗ {material_name} ({category}): {message}")
            stats['errors'] += 1
            stats['by_category'][category]['errors'] += 1
    
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
    
    print("BY CATEGORY:")
    for category in sorted(stats['by_category'].keys()):
        cat_stats = stats['by_category'][category]
        if cat_stats['modified'] > 0:
            print(f"  {category.upper():15} - Modified: {cat_stats['modified']:3}, "
                  f"Properties: {cat_stats['properties_updated']:3}")
    print()
    
    if dry_run:
        print("DRY RUN COMPLETE - Run without --dry-run to apply changes")
    else:
        print("✅ POPULATION COMPLETE")
    
    return 0 if stats['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
