#!/usr/bin/env python3
"""
Categories.yaml Null Value Cleanup

Fixes 21 null/empty values in Categories.yaml by:
1. Adding missing description fields with intelligent defaults
2. Adding missing unit fields based on property type
3. Maintaining all existing valid data

Usage:
    python3 scripts/tools/cleanup_categories_nulls.py --dry-run  # Preview changes
    python3 scripts/tools/cleanup_categories_nulls.py            # Apply fixes

Author: Z-Beam Generator
Date: October 16, 2025
"""

import yaml
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Configure paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CATEGORIES_FILE = PROJECT_ROOT / "data" / "Categories.yaml"
BACKUP_DIR = PROJECT_ROOT / "backups" / f"categories_null_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Property descriptions mapping
PROPERTY_DESCRIPTIONS = {
    'oxidationResistance': 'Material resistance to oxidation and corrosion in presence of oxygen',
    'fractureToughness': 'Material resistance to crack propagation under stress',
    'corrosionResistance': 'Material resistance to chemical corrosion and degradation',
    'flexuralStrength': 'Material strength under bending loads and flexural stress',
    'dielectricConstant': 'Electrical permittivity relative to vacuum',
    'reflectivity': 'Percentage of incident light reflected from material surface'
}

# Unit mappings by property type
PROPERTY_UNITS = {
    'oxidationResistance': 'rating (1-10)',
    'fractureToughness': 'MPa·m^0.5',
    'corrosionResistance': 'rating (1-10)',
    'flexuralStrength': 'MPa',
    'dielectricConstant': 'dimensionless',
    'reflectivity': '%'
}


class CategoriesNullCleanup:
    """Cleanup null/empty values in Categories.yaml"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes = []
        self.categories_data = None
        
    def load_categories(self) -> bool:
        """Load Categories.yaml"""
        try:
            with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                self.categories_data = yaml.safe_load(f)
            print(f"✅ Loaded Categories.yaml ({CATEGORIES_FILE})")
            return True
        except Exception as e:
            print(f"❌ Failed to load Categories.yaml: {e}")
            return False
    
    def find_nulls(self) -> List[str]:
        """Find all null/empty values in data structure"""
        nulls = []
        
        def check_nulls(data, path=''):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    if value is None or value == '':
                        nulls.append(current_path)
                    else:
                        check_nulls(value, current_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_nulls(item, f"{path}[{i}]")
        
        check_nulls(self.categories_data)
        return nulls
    
    def fix_material_property_descriptions(self):
        """Fix null unit in materialPropertyDescriptions.reflectivity"""
        if 'materialPropertyDescriptions' not in self.categories_data:
            return
        
        descriptions = self.categories_data['materialPropertyDescriptions']
        
        # Fix reflectivity unit
        if 'reflectivity' in descriptions:
            refl = descriptions['reflectivity']
            if isinstance(refl, dict) and refl.get('unit') is None:
                refl['unit'] = '%'
                self.changes.append("materialPropertyDescriptions.reflectivity.unit: None → '%'")
                print("  ✓ Fixed materialPropertyDescriptions.reflectivity.unit")
    
    def fix_category_ranges(self):
        """Fix null descriptions in category_ranges"""
        if 'categories' not in self.categories_data:
            return
        
        categories = self.categories_data['categories']
        
        for category_name, category_data in categories.items():
            if 'category_ranges' not in category_data:
                continue
            
            ranges = category_data['category_ranges']
            
            for prop_name, prop_data in ranges.items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Fix missing description
                if prop_data.get('description') is None or prop_data.get('description') == '':
                    if prop_name in PROPERTY_DESCRIPTIONS:
                        description = PROPERTY_DESCRIPTIONS[prop_name]
                    else:
                        # Generate default description from property name
                        description = f"{prop_name.replace('_', ' ').title()} property for laser cleaning applications"
                    
                    prop_data['description'] = description
                    path = f"categories.{category_name}.category_ranges.{prop_name}.description"
                    self.changes.append(f"{path}: None → '{description[:50]}...'")
                    print(f"  ✓ Fixed {category_name}.{prop_name}.description")
    
    def fix_electrical_properties(self):
        """Fix null units in electricalProperties"""
        if 'categories' not in self.categories_data:
            return
        
        categories = self.categories_data['categories']
        
        for category_name, category_data in categories.items():
            if 'electricalProperties' not in category_data:
                continue
            
            elec_props = category_data['electricalProperties']
            
            for prop_name, prop_data in elec_props.items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Fix missing unit
                if prop_data.get('unit') is None or prop_data.get('unit') == '':
                    # Determine appropriate unit
                    if 'dielectric' in prop_name.lower():
                        unit = 'dimensionless'
                    elif prop_name in PROPERTY_UNITS:
                        unit = PROPERTY_UNITS[prop_name]
                    else:
                        unit = 'dimensionless'
                    
                    prop_data['unit'] = unit
                    path = f"categories.{category_name}.electricalProperties.{prop_name}.unit"
                    self.changes.append(f"{path}: None → '{unit}'")
                    print(f"  ✓ Fixed {category_name}.electricalProperties.{prop_name}.unit")
    
    def fix_all_nulls(self):
        """Apply all null fixes"""
        print("\n🔧 Fixing null values in Categories.yaml...")
        
        # Fix different sections
        self.fix_material_property_descriptions()
        self.fix_category_ranges()
        self.fix_electrical_properties()
        
        print(f"\n📊 Total changes: {len(self.changes)}")
    
    def create_backup(self):
        """Create backup before modifications"""
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            backup_file = BACKUP_DIR / "Categories.yaml"
            shutil.copy2(CATEGORIES_FILE, backup_file)
            print(f"📦 Created backup: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def save_categories(self):
        """Save modified Categories.yaml"""
        try:
            with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.categories_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=120
                )
            print(f"✅ Saved Categories.yaml with fixes")
            return True
        except Exception as e:
            print(f"❌ Failed to save Categories.yaml: {e}")
            return False
    
    def verify_fixes(self) -> bool:
        """Verify all nulls have been fixed"""
        remaining_nulls = self.find_nulls()
        
        if not remaining_nulls:
            print("\n✅ All null values have been fixed!")
            return True
        else:
            print(f"\n⚠️  {len(remaining_nulls)} null values remain:")
            for null_path in remaining_nulls[:10]:
                print(f"  - {null_path}")
            return False
    
    def run(self) -> bool:
        """Execute cleanup process"""
        print("="*80)
        print("CATEGORIES.YAML NULL VALUE CLEANUP")
        print("="*80)
        
        # Load data
        if not self.load_categories():
            return False
        
        # Find nulls before
        nulls_before = self.find_nulls()
        print(f"\n📊 Found {len(nulls_before)} null/empty values")
        
        if self.dry_run:
            print("\n🔍 DRY-RUN MODE - No changes will be saved")
        
        # Apply fixes
        self.fix_all_nulls()
        
        # Verify fixes
        nulls_after = self.find_nulls()
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Null values before: {len(nulls_before)}")
        print(f"Null values after:  {len(nulls_after)}")
        print(f"Fixed:             {len(nulls_before) - len(nulls_after)}")
        
        if self.dry_run:
            print("\n⚠️  DRY-RUN: No changes saved")
            print("Run without --dry-run to apply changes")
            return True
        
        # Create backup and save
        if not self.create_backup():
            return False
        
        if not self.save_categories():
            return False
        
        # Final verification
        if not self.verify_fixes():
            print("\n⚠️  Some nulls remain - manual review recommended")
            return False
        
        print("\n✅ Categories.yaml cleanup complete!")
        print(f"\nChanges applied:")
        for change in self.changes[:20]:
            print(f"  • {change}")
        
        if len(self.changes) > 20:
            print(f"  ... and {len(self.changes) - 20} more")
        
        return True


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Clean up null/empty values in Categories.yaml"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Preview changes without saving"
    )
    
    args = parser.parse_args()
    
    cleanup = CategoriesNullCleanup(dry_run=args.dry_run)
    success = cleanup.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
