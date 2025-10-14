#!/usr/bin/env python3
"""
Consolidate thermal fields in frontmatter files.

Re-architects thermal properties to use:
1. Single thermalDestructionPoint field (temperature value)
2. Single thermalDestructionType field (string describing the destruction process)

Replaces previous multi-field approach (sinteringPoint, softeningPoint, degradationPoint, etc.)
with unified structure for better maintainability and simpler frontend logic.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Category ranges from Categories.yaml (for min/max population)
CATEGORY_THERMAL_RANGES = {
    'wood': {'min': 200, 'max': 500, 'unit': '°C'},
    'ceramic': {'min': 1000, 'max': 3827, 'unit': '°C'},
    'stone': {'min': 600, 'max': 1700, 'unit': '°C'},
    'composite': {'min': 150, 'max': 2000, 'unit': '°C'},
    'plastic': {'min': 80, 'max': 400, 'unit': '°C'},
    'glass': {'min': 500, 'max': 1723, 'unit': '°C'},
    'masonry': {'min': 500, 'max': 1200, 'unit': '°C'},
    'metal': {'min': -38.8, 'max': 3422, 'unit': '°C'},
    'semiconductor': {'min': 100, 'max': 1414, 'unit': '°C'}
}

# Mapping of categories to thermal destruction types
THERMAL_TYPE_MAP = {
    'wood': {
        'type': 'Decomposition',
        'description': 'Temperature where thermal decomposition begins'
    },
    'ceramic': {
        'type': 'Sintering',
        'description': 'Temperature where particle fusion or decomposition occurs'
    },
    'stone': {
        'type': 'Structural breakdown',
        'description': 'Temperature where structural breakdown begins'
    },
    'composite': {
        'type': 'Matrix degradation',
        'description': 'Temperature where polymer matrix decomposition begins'
    },
    'plastic': {
        'type': 'Degradation',
        'description': 'Temperature where polymer chain breakdown begins'
    },
    'glass': {
        'type': 'Softening',
        'description': 'Temperature where glass transitions from rigid to pliable state'
    },
    'masonry': {
        'type': 'Structural breakdown',
        'description': 'Temperature where structural breakdown begins'
    },
    'metal': {
        'type': 'Melting',
        'description': 'Temperature where solid-to-liquid phase transition occurs'
    },
    'semiconductor': {
        'type': 'Melting',
        'description': 'Temperature where solid-to-liquid phase transition occurs'
    }
}

# Fields to remove (old category-specific thermal fields)
FIELDS_TO_REMOVE = [
    'sinteringPoint',
    'softeningPoint',
    'degradationPoint',
    'thermalDegradationPoint',
    'thermalDestructionType',  # Remove old incorrectly-named field
    'meltingPoint'  # BREAKING CHANGE: Remove legacy meltingPoint field
]


def get_thermal_destruction_point(props: Dict[str, Any], category: str) -> Optional[Dict[str, Any]]:
    """
    Extract thermal destruction point from existing fields.
    Priority order:
    1. Existing thermalDestructionPoint
    2. Category-specific field (sinteringPoint, softeningPoint, etc.)
    3. meltingPoint (for metals/semiconductors)
    """
    # Check for existing thermalDestructionPoint
    if 'thermalDestructionPoint' in props:
        field = props['thermalDestructionPoint']
        if isinstance(field, dict) and 'value' in field:
            return field
    
    # Check category-specific fields
    category_lower = category.lower()
    
    if category_lower == 'wood':
        if 'thermalDestructionPoint' in props:
            return props['thermalDestructionPoint']
    elif category_lower == 'ceramic':
        if 'sinteringPoint' in props:
            return props['sinteringPoint']
    elif category_lower in ['stone', 'masonry']:
        if 'thermalDegradationPoint' in props:
            return props['thermalDegradationPoint']
    elif category_lower in ['composite', 'plastic']:
        if 'degradationPoint' in props:
            return props['degradationPoint']
    elif category_lower == 'glass':
        if 'softeningPoint' in props:
            return props['softeningPoint']
    elif category_lower in ['metal', 'semiconductor']:
        if 'meltingPoint' in props:
            return props['meltingPoint']
    
    # Fallback to meltingPoint if no other field found
    if 'meltingPoint' in props:
        return props['meltingPoint']
    
    return None


def consolidate_thermal_fields(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Consolidate thermal fields to thermalDestructionPoint + thermalDestructionType.
    
    Returns:
        (modified: bool, message: str)
    """
    category = data.get('category', '').lower()
    material_name = data.get('name', 'Unknown')
    
    if 'materialProperties' not in data:
        return False, f"No materialProperties found"
    
    props = data['materialProperties']
    
    # Get thermal type configuration
    thermal_config = THERMAL_TYPE_MAP.get(category)
    if not thermal_config:
        return False, f"Unknown category: {category}"
    
    # Extract thermal destruction point
    thermal_point = get_thermal_destruction_point(props, category)
    if not thermal_point:
        return False, f"No thermal destruction point found"
    
    # Create new thermalDestructionPoint field (preserve existing structure)
    new_thermal_point = thermal_point.copy()
    new_thermal_point['description'] = thermal_config['description']
    
    # Populate min/max from category ranges
    category_range = CATEGORY_THERMAL_RANGES.get(category)
    if category_range:
        new_thermal_point['min'] = category_range['min']
        new_thermal_point['max'] = category_range['max']
    
    # Remove old category-specific fields FIRST
    removed_fields = []
    for field in FIELDS_TO_REMOVE:
        if field in props and field != 'thermalDestructionPoint':
            del props[field]
            removed_fields.append(field)
    
    # Now set the new fields (this ensures they're written)
    props['thermalDestructionPoint'] = new_thermal_point
    props['thermalDestructionType'] = thermal_config['type']
    
    # For metals/semiconductors, keep meltingPoint for backward compatibility
    # but thermalDestructionPoint will reference the same temperature
    
    if removed_fields:
        return True, f"Consolidated thermal fields, removed: {', '.join(removed_fields)}"
    else:
        return True, f"Set thermalDestructionType to '{thermal_config['type']}'"


def process_frontmatter_file(filepath: Path, dry_run: bool = False) -> tuple[bool, str]:
    """
    Process a single frontmatter YAML file.
    
    Returns:
        (success: bool, message: str)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return False, "Empty file"
        
        modified, message = consolidate_thermal_fields(data)
        
        if modified and not dry_run:
            # Write back to file with explicit configuration
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                         allow_unicode=True, width=float("inf"))
        
        return modified, message
    
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main execution function."""
    dry_run = '--dry-run' in sys.argv
    
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return 1
    
    print("=" * 80)
    print("CONSOLIDATING THERMAL FIELDS TO thermalDestructionPoint + thermalDestructionType")
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
            stats['by_category'][category] = {'modified': 0, 'skipped': 0, 'errors': 0}
        
        success, message = process_frontmatter_file(filepath, dry_run)
        
        if success:
            if 'removed' in message or 'Set thermal' in message:
                status = '✓' if not dry_run else '→'
                print(f"{status} {material_name} ({category}): {message}")
                stats['modified'] += 1
                stats['by_category'][category]['modified'] += 1
            else:
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
    print(f"Modified: {stats['modified']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print()
    
    print("BY CATEGORY:")
    for category in sorted(stats['by_category'].keys()):
        cat_stats = stats['by_category'][category]
        print(f"  {category.upper():15} - Modified: {cat_stats['modified']:3}, "
              f"Skipped: {cat_stats['skipped']:3}, Errors: {cat_stats['errors']:3}")
    print()
    
    if dry_run:
        print("DRY RUN COMPLETE - Run without --dry-run to apply changes")
    else:
        print("✅ CONSOLIDATION COMPLETE")
    
    return 0 if stats['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
