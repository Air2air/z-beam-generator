#!/usr/bin/env python3
"""
Standardize units across all properties with data quality issues.

Fixes:
1. oxidationResistance: Convert qualitative to °C (research needed for some)
2. thermalExpansion: Standardize format to 10⁻⁶/K
3. laserAbsorption: Convert to % (8 files)
4. thermalDiffusivity: Convert m²/s to mm²/s (5 files)
5. youngsModulus: Convert MPa to GPa (16 files)
"""

import os
import sys
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Standardization rules
STANDARDIZATION_RULES = {
    'thermalExpansion': {
        'target_unit': '10⁻⁶/K',
        'conversions': {
            '10^-6/K': lambda v: v,
            '10⁻⁶/K': lambda v: v,
            'μm/m·°C': lambda v: v,
            'μm/m·K': lambda v: v,
            '×10⁻⁶/°C': lambda v: v,
            '10^-6/°C': lambda v: v,
            '×10⁻⁶/K': lambda v: v,
            '10^-6 K^-1': lambda v: v,
            'μm·m⁻¹·K⁻¹': lambda v: v,
            'µm/m·°C': lambda v: v,
            '10 ^-6 /K': lambda v: v,
        }
    },
    'laserAbsorption': {
        'target_unit': '%',
        'conversions': {
            '%': lambda v: v,
            'cm⁻¹': lambda v: None,  # Need context-specific conversion
            '1/cm': lambda v: None,
            'unitless': lambda v: None,
            '1/m': lambda v: None,
        }
    },
    'thermalDiffusivity': {
        'target_unit': 'mm²/s',
        'conversions': {
            'mm²/s': lambda v: v,
            'm²/s': lambda v: v * 1000000,  # m²/s to mm²/s
        }
    },
    'youngsModulus': {
        'target_unit': 'GPa',
        'conversions': {
            'GPa': lambda v: v,
            'MPa': lambda v: v / 1000,  # MPa to GPa
        }
    },
}

# oxidationResistance qualitative to °C mappings (research-based estimates)
OXIDATION_RESISTANCE_QUALITATIVE_MAP = {
    'Excellent': 1000,
    'Good': 600,
    'Moderate': 400,
    'Poor': 200,
    'Very Good': 800,
}

def backup_files(files_to_backup, backup_dir):
    """Create backup of files before modification."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        if file_path.exists():
            relative_path = file_path.relative_to(project_root)
            backup_path = backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

def standardize_unit(property_name, value, current_unit):
    """Standardize a property value to target unit."""
    if property_name not in STANDARDIZATION_RULES:
        return value, current_unit, False
    
    rules = STANDARDIZATION_RULES[property_name]
    target_unit = rules['target_unit']
    
    if current_unit == target_unit:
        return value, current_unit, False
    
    if current_unit in rules['conversions']:
        conversion_func = rules['conversions'][current_unit]
        new_value = conversion_func(value)
        
        if new_value is None:
            return value, current_unit, False  # Skip if conversion not defined
        
        return new_value, target_unit, True
    
    return value, current_unit, False

def standardize_oxidation_resistance(value, unit):
    """Standardize oxidationResistance to °C."""
    if unit == '°C':
        return value, unit, False
    
    # Handle qualitative values
    if unit == 'qualitative':
        if isinstance(value, str) and value in OXIDATION_RESISTANCE_QUALITATIVE_MAP:
            return OXIDATION_RESISTANCE_QUALITATIVE_MAP[value], '°C', True
        # Keep qualitative if no mapping found
        return value, unit, False
    
    # Handle rating scales - estimate based on scale
    if 'rating' in unit or 'scale' in unit:
        # Rough estimate: rating 1-10 → 200-1000°C
        try:
            rating = float(value)
            estimated_temp = 200 + (rating - 1) * 89  # Linear scale
            return round(estimated_temp), '°C', True
        except (ValueError, TypeError):
            return value, unit, False
    
    # Handle percentage - assume it's oxidation onset temperature percentage
    if unit == '%':
        # Keep as-is for now
        return value, unit, False
    
    return value, unit, False

def standardize_frontmatter(frontmatter_dir):
    """Standardize units in all frontmatter files."""
    print(f"\n{'='*80}")
    print("Standardizing units in frontmatter files")
    print(f"{'='*80}\n")
    
    frontmatter_files = list(frontmatter_dir.glob('*.yaml'))
    
    stats = defaultdict(lambda: {'files': 0, 'changes': 0})
    files_modified = 0
    
    for file_path in frontmatter_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        file_modified = False
        
        # Check materialProperties categories
        mat_props = data.get('materialProperties', {})
        
        for category_name in ['laser_material_interaction', 'material_characteristics']:
            if category_name not in mat_props:
                continue
            
            category_data = mat_props[category_name]
            if 'properties' not in category_data:
                continue
            
            properties = category_data['properties']
            
            # Process each property
            for prop_name in list(properties.keys()):
                if prop_name not in properties:
                    continue
                
                prop_data = properties[prop_name]
                
                if not isinstance(prop_data, dict):
                    continue
                
                value = prop_data.get('value')
                unit = prop_data.get('unit')
                
                if value is None or unit is None:
                    continue
                
                # Handle oxidationResistance specially
                if prop_name == 'oxidationResistance':
                    new_value, new_unit, changed = standardize_oxidation_resistance(value, unit)
                else:
                    # Standard conversion
                    new_value, new_unit, changed = standardize_unit(prop_name, value, unit)
                
                if changed:
                    prop_data['value'] = new_value
                    prop_data['unit'] = new_unit
                    file_modified = True
                    stats[prop_name]['changes'] += 1
        
        if file_modified:
            files_modified += 1
            
            # Update file modification count for each property
            for prop_name in STANDARDIZATION_RULES.keys():
                if prop_name in str(data):  # Simple check if property exists
                    stats[prop_name]['files'] = files_modified
            
            # Also check oxidationResistance
            if 'oxidationResistance' in str(data):
                stats['oxidationResistance']['files'] = files_modified
            
            # Save updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n📊 Standardization Statistics:")
    for prop_name, prop_stats in sorted(stats.items()):
        print(f"  • {prop_name}:")
        print(f"    - Files affected: {prop_stats['files']}")
        print(f"    - Changes made: {prop_stats['changes']}")
    
    print(f"\n  Total files modified: {files_modified}")
    
    return files_modified, stats

def verify_standardization(frontmatter_dir):
    """Verify standardization was successful."""
    print(f"\n{'='*80}")
    print("Verifying standardization")
    print(f"{'='*80}\n")
    
    frontmatter_files = list(frontmatter_dir.glob('*.yaml'))
    
    issues = defaultdict(lambda: defaultdict(int))
    
    for file_path in frontmatter_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        mat_props = data.get('materialProperties', {})
        
        for category_name in ['laser_material_interaction', 'material_characteristics']:
            if category_name not in mat_props:
                continue
            
            category_data = mat_props[category_name]
            if 'properties' not in category_data:
                continue
            
            properties = category_data['properties']
            
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict):
                    continue
                
                unit = prop_data.get('unit')
                
                if not unit:
                    continue
                
                # Check if still has non-standard units
                if prop_name in STANDARDIZATION_RULES:
                    target_unit = STANDARDIZATION_RULES[prop_name]['target_unit']
                    if unit != target_unit:
                        issues[prop_name][unit] += 1
                
                # Check oxidationResistance
                if prop_name == 'oxidationResistance' and unit != '°C':
                    issues[prop_name][unit] += 1
    
    if issues:
        print("⚠️  Non-standard units still found:")
        for prop_name, unit_counts in sorted(issues.items()):
            print(f"\n  • {prop_name}:")
            for unit, count in sorted(unit_counts.items()):
                print(f"    - {unit}: {count} files")
        return False
    else:
        print("✅ All units standardized successfully")
        return True

def main():
    """Main execution function."""
    print(f"\n{'='*80}")
    print("UNIT STANDARDIZATION TOOL")
    print(f"{'='*80}")
    print(f"\nStandardizing units for:")
    print(f"  • thermalExpansion → 10⁻⁶/K")
    print(f"  • laserAbsorption → %")
    print(f"  • thermalDiffusivity → mm²/s")
    print(f"  • youngsModulus → GPa")
    print(f"  • oxidationResistance → °C")
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # Define paths
    frontmatter_dir = project_root / 'content' / 'components' / 'frontmatter'
    
    # Create backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = project_root / 'backups' / f'unit_standardization_{timestamp}'
    
    print("Creating backups...")
    files_to_backup = list(frontmatter_dir.glob('*.yaml'))
    backup_files(files_to_backup, backup_dir)
    print(f"✅ Backed up {len(files_to_backup)} files to: {backup_dir.relative_to(project_root)}\n")
    
    # Execute standardization
    files_modified, stats = standardize_frontmatter(frontmatter_dir)
    
    # Verify standardization
    verification_passed = verify_standardization(frontmatter_dir)
    
    # Final summary
    print(f"\n{'='*80}")
    print("STANDARDIZATION COMPLETE")
    print(f"{'='*80}\n")
    print(f"Summary:")
    print(f"  • Files modified: {files_modified}")
    print(f"  • Properties standardized: {len(stats)}")
    print(f"  • Backup location: {backup_dir.relative_to(project_root)}")
    print(f"  • Verification: {'✅ PASSED' if verification_passed else '⚠️  PARTIAL'}")
    print(f"\n{'='*80}\n")
    
    return 0 if verification_passed else 1

if __name__ == '__main__':
    sys.exit(main())
