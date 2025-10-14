#!/usr/bin/env python3
"""
Populate missing min/max ranges for materialProperties in frontmatter files.

Based on scientific research and Categories.yaml category ranges.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Researched category ranges for properties missing min/max values
# Sources: Scientific literature, material databases, laser cleaning research

CATEGORY_PROPERTY_RANGES = {
    # Ablation Threshold (J/cm²) - Minimum fluence for material removal
    'ablationThreshold': {
        'wood': {'min': 0.5, 'max': 3.0, 'unit': 'J/cm²'},
        'ceramic': {'min': 2.0, 'max': 15.0, 'unit': 'J/cm²'},
        'stone': {'min': 1.0, 'max': 10.0, 'unit': 'J/cm²'},
        'composite': {'min': 0.5, 'max': 8.0, 'unit': 'J/cm²'},
        'plastic': {'min': 0.2, 'max': 2.0, 'unit': 'J/cm²'},
        'glass': {'min': 3.0, 'max': 20.0, 'unit': 'J/cm²'},
        'masonry': {'min': 1.0, 'max': 8.0, 'unit': 'J/cm²'},
        'metal': {'min': 0.5, 'max': 50.0, 'unit': 'J/cm²'},
        'semiconductor': {'min': 0.1, 'max': 10.0, 'unit': 'J/cm²'}
    },
    
    # Absorption Coefficient (dimensionless, 0-1)
    'absorptionCoefficient': {
        'wood': {'min': 0.70, 'max': 0.95, 'unit': 'dimensionless'},
        'ceramic': {'min': 0.30, 'max': 0.90, 'unit': 'dimensionless'},
        'stone': {'min': 0.40, 'max': 0.85, 'unit': 'dimensionless'},
        'composite': {'min': 0.50, 'max': 0.95, 'unit': 'dimensionless'},
        'plastic': {'min': 0.60, 'max': 0.95, 'unit': 'dimensionless'},
        'glass': {'min': 0.01, 'max': 0.40, 'unit': 'dimensionless'},
        'masonry': {'min': 0.50, 'max': 0.85, 'unit': 'dimensionless'},
        'metal': {'min': 0.02, 'max': 0.60, 'unit': 'dimensionless'},
        'semiconductor': {'min': 0.10, 'max': 0.70, 'unit': 'dimensionless'}
    },
    
    # Reflectivity (dimensionless, 0-1)
    'reflectivity': {
        'wood': {'min': 0.05, 'max': 0.30, 'unit': 'dimensionless'},
        'ceramic': {'min': 0.10, 'max': 0.70, 'unit': 'dimensionless'},
        'stone': {'min': 0.15, 'max': 0.60, 'unit': 'dimensionless'},
        'composite': {'min': 0.05, 'max': 0.50, 'unit': 'dimensionless'},
        'plastic': {'min': 0.05, 'max': 0.40, 'unit': 'dimensionless'},
        'glass': {'min': 0.04, 'max': 0.92, 'unit': 'dimensionless'},
        'masonry': {'min': 0.15, 'max': 0.50, 'unit': 'dimensionless'},
        'metal': {'min': 0.40, 'max': 0.98, 'unit': 'dimensionless'},
        'semiconductor': {'min': 0.30, 'max': 0.70, 'unit': 'dimensionless'}
    },
    
    # Laser Damage Threshold (J/cm²)
    'laserDamageThreshold': {
        'wood': {'min': 0.3, 'max': 1.5, 'unit': 'J/cm²'},
        'ceramic': {'min': 1.0, 'max': 10.0, 'unit': 'J/cm²'},
        'stone': {'min': 0.5, 'max': 5.0, 'unit': 'J/cm²'},
        'composite': {'min': 0.3, 'max': 5.0, 'unit': 'J/cm²'},
        'plastic': {'min': 0.1, 'max': 1.0, 'unit': 'J/cm²'},
        'glass': {'min': 2.0, 'max': 50.0, 'unit': 'J/cm²'},
        'masonry': {'min': 0.5, 'max': 4.0, 'unit': 'J/cm²'},
        'metal': {'min': 0.3, 'max': 20.0, 'unit': 'J/cm²'},
        'semiconductor': {'min': 0.05, 'max': 5.0, 'unit': 'J/cm²'}
    },
    
    # Porosity (%)
    'porosity': {
        'wood': {'min': 5.0, 'max': 75.0, 'unit': '%'},
        'ceramic': {'min': 0.1, 'max': 50.0, 'unit': '%'},
        'stone': {'min': 0.5, 'max': 50.0, 'unit': '%'},
        'composite': {'min': 1.0, 'max': 40.0, 'unit': '%'},
        'glass': {'min': 0.0, 'max': 30.0, 'unit': '%'},
        'masonry': {'min': 10.0, 'max': 40.0, 'unit': '%'}
    },
    
    # Surface Roughness (μm Ra)
    'surfaceRoughness': {
        'wood': {'min': 1.0, 'max': 50.0, 'unit': 'μm Ra'},
        'composite': {'min': 0.5, 'max': 20.0, 'unit': 'μm Ra'},
        'glass': {'min': 0.001, 'max': 5.0, 'unit': 'μm Ra'},
        'plastic': {'min': 0.1, 'max': 10.0, 'unit': 'μm Ra'},
        'metal': {'min': 0.05, 'max': 25.0, 'unit': 'μm Ra'},
        'masonry': {'min': 5.0, 'max': 100.0, 'unit': 'μm Ra'}
    },
    
    # Moisture Content (%)
    'moistureContent': {
        'wood': {'min': 6.0, 'max': 20.0, 'unit': '%'}
    },
    
    # Refractive Index (dimensionless)
    'refractiveIndex': {
        'glass': {'min': 1.45, 'max': 2.00, 'unit': 'dimensionless'},
        'ceramic': {'min': 1.50, 'max': 2.70, 'unit': 'dimensionless'},
        'plastic': {'min': 1.30, 'max': 1.70, 'unit': 'dimensionless'},
        'semiconductor': {'min': 2.40, 'max': 4.50, 'unit': 'dimensionless'},
        'stone': {'min': 1.50, 'max': 1.75, 'unit': 'dimensionless'}
    },
    
    # Compressive Strength (MPa)
    'compressiveStrength': {
        'ceramic': {'min': 500, 'max': 5000, 'unit': 'MPa'},
        'stone': {'min': 20, 'max': 400, 'unit': 'MPa'},
        'masonry': {'min': 5, 'max': 80, 'unit': 'MPa'}
    },
    
    # Flexural Strength (MPa)
    'flexuralStrength': {
        'ceramic': {'min': 50, 'max': 1000, 'unit': 'MPa'},
        'glass': {'min': 30, 'max': 500, 'unit': 'MPa'},
        'composite': {'min': 50, 'max': 800, 'unit': 'MPa'},
        'stone': {'min': 5, 'max': 50, 'unit': 'MPa'},
        'masonry': {'min': 2, 'max': 20, 'unit': 'MPa'},
        'semiconductor': {'min': 100, 'max': 500, 'unit': 'MPa'}
    },
    
    # Ignition Temperature (°C)
    'ignitionTemperature': {
        'wood': {'min': 300, 'max': 500, 'unit': '°C'}
    },
    
    # Cellulose Content (%)
    'celluloseContent': {
        'wood': {'min': 35.0, 'max': 55.0, 'unit': '%'}
    },
    
    # Lignin Content (%)
    'ligninContent': {
        'wood': {'min': 15.0, 'max': 40.0, 'unit': '%'}
    },
    
    # Transmissivity (dimensionless, 0-1)
    'transmissivity': {
        'glass': {'min': 0.60, 'max': 0.95, 'unit': 'dimensionless'}
    },
    
    # Electrical Resistivity (Ω·cm)
    'electricalResistivity': {
        'metal': {'min': 1.5e-6, 'max': 1.0e-4, 'unit': 'Ω·cm'}
    },
    
    # Electrical Conductivity (S/m)
    'electricalConductivity': {
        'metal': {'min': 1.0e5, 'max': 6.5e7, 'unit': 'S/m'}
    },
    
    # Vaporization Temperature (°C)
    'vaporizationTemperature': {
        'metal': {'min': 1500, 'max': 5900, 'unit': '°C'}
    },
    
    # Vaporization Point (°C)
    'vaporizationPoint': {
        'metal': {'min': 1500, 'max': 5900, 'unit': '°C'}
    },
    
    # Oxidation Resistance (categorical but we'll skip for now)
    # Chemical Stability (categorical - skip)
    # Crystalline Structure (categorical - skip)
    # Corrosion Resistance (categorical - skip)
    
    # Thermal Shock Resistance (categorical in most materials)
    
    # Fracture Toughness (MPa·m^0.5)
    'fractureToughness': {
        'ceramic': {'min': 2.0, 'max': 15.0, 'unit': 'MPa·m^0.5'},
        'semiconductor': {'min': 0.7, 'max': 5.0, 'unit': 'MPa·m^0.5'}
    }
}


def populate_property_ranges(data: Dict[str, Any]) -> tuple[bool, int]:
    """
    Populate missing min/max values for materialProperties.
    
    Returns:
        (modified: bool, properties_updated: int)
    """
    category = data.get('category', '').lower()
    material_name = data.get('name', 'Unknown')
    
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
        if prop_name not in CATEGORY_PROPERTY_RANGES:
            continue
        
        category_ranges = CATEGORY_PROPERTY_RANGES[prop_name]
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
        
        modified, count = populate_property_ranges(data)
        
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
    print("POPULATING MISSING PROPERTY MIN/MAX RANGES")
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
        print(f"  {category.upper():15} - Modified: {cat_stats['modified']:3}, "
              f"Properties: {cat_stats['properties_updated']:3}, "
              f"Skipped: {cat_stats['skipped']:3}, Errors: {cat_stats['errors']:3}")
    print()
    
    if dry_run:
        print("DRY RUN COMPLETE - Run without --dry-run to apply changes")
    else:
        print("✅ POPULATION COMPLETE")
    
    return 0 if stats['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
