#!/usr/bin/env python3
"""
Update Frontmatter Ranges from Categories.yaml
Updates only the authoritative property ranges in existing frontmatter files
without full regeneration - preserves all other content.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class FrontmatterRangeUpdater:
    """Updates authoritative ranges in frontmatter files"""
    
    def __init__(self, dry_run: bool = False):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.frontmatter_dir = self.project_root / "content/components/frontmatter"
        self.dry_run = dry_run
        
        # Load data files
        self.categories = self._load_yaml(self.data_dir / "Categories.yaml")
        self.materials = self._load_yaml(self.data_dir / "Materials.yaml")
        
        # Track updates
        self.files_updated = 0
        self.properties_updated = 0
        self.updates_log = []
        
    def _load_yaml(self, filepath: Path) -> dict:
        """Load YAML file"""
        if not filepath.exists():
            raise FileNotFoundError(f"Required file not found: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _save_yaml(self, data: dict, filepath: Path):
        """Save YAML file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def get_authoritative_properties(self, category: str) -> Dict[str, dict]:
        """Get authoritative properties for a category"""
        auth_props = {}
        
        if 'categories' not in self.categories:
            return auth_props
        
        if category not in self.categories['categories']:
            return auth_props
        
        cat_data = self.categories['categories'][category]
        if 'category_ranges' not in cat_data:
            return auth_props
        
        # Extract properties with authoritative sources (75%+ confidence)
        for prop_name, prop_data in cat_data['category_ranges'].items():
            if isinstance(prop_data, dict) and 'source' in prop_data:
                if prop_data.get('confidence', 0) >= 75:
                    auth_props[prop_name] = prop_data
        
        return auth_props
    
    def update_property_in_frontmatter(self, fm_data: dict, prop_name: str, prop_data: dict) -> bool:
        """Update a single property in frontmatter data"""
        # Find where the property lives - check nested structure
        property_location = None
        property_parent = None
        current_prop = None
        
        # Check materialProperties (with nested categories and properties dict)
        if 'materialProperties' in fm_data:
            mp = fm_data['materialProperties']
            # Check nested categories -> properties -> property_name
            for category_key in ['material_properties', 'structural_response', 'energy_coupling']:
                if category_key in mp and isinstance(mp[category_key], dict):
                    if 'properties' in mp[category_key] and isinstance(mp[category_key]['properties'], dict):
                        if prop_name in mp[category_key]['properties']:
                            property_location = 'materialProperties'
                            property_parent = category_key
                            current_prop = mp[category_key]['properties'][prop_name]
                            break
        
        # Check machineSettings if not found
        if not property_location and 'machineSettings' in fm_data:
            ms = fm_data['machineSettings']
            if prop_name in ms:
                property_location = 'machineSettings'
                current_prop = ms[prop_name]
        
        if not property_location:
            # Property doesn't exist in this frontmatter
            return False
        
        # Check if it's pulse-specific
        if 'nanosecond' in prop_data or 'picosecond' in prop_data or 'femtosecond' in prop_data:
            # Update with pulse-specific data
            updated_prop = {}
            for pulse_type in ['nanosecond', 'picosecond', 'femtosecond']:
                if pulse_type in prop_data:
                    updated_prop[pulse_type] = {
                        'min': prop_data[pulse_type]['min'],
                        'max': prop_data[pulse_type]['max'],
                        'unit': prop_data[pulse_type]['unit']
                    }
            
            # Add metadata
            updated_prop['source'] = prop_data.get('source', 'Published research')
            updated_prop['confidence'] = prop_data.get('confidence', 75)
            updated_prop['measurement_context'] = prop_data.get('measurement_context', 'Varies by pulse duration')
            
            # Save to correct location (materialProperties -> category -> properties -> prop_name)
            if property_parent:
                fm_data[property_location][property_parent]['properties'][prop_name] = updated_prop
            else:
                fm_data[property_location][prop_name] = updated_prop
            return True
        
        # Check if it's wavelength-specific
        elif 'at_1064nm' in prop_data or 'at_532nm' in prop_data:
            # Update with wavelength-specific data
            updated_prop = {}
            for key in prop_data:
                if key.startswith('at_') and 'nm' in key:
                    updated_prop[key] = prop_data[key]
            
            # Add metadata
            updated_prop['source'] = prop_data.get('source', 'Published research')
            updated_prop['confidence'] = prop_data.get('confidence', 75)
            updated_prop['measurement_context'] = prop_data.get('measurement_context', 'Varies by wavelength')
            
            # Save to correct location (materialProperties -> category -> properties -> prop_name)
            if property_parent:
                fm_data[property_location][property_parent]['properties'][prop_name] = updated_prop
            else:
                fm_data[property_location][prop_name] = updated_prop
            return True
        
        # Standard min/max update
        elif 'min' in prop_data and 'max' in prop_data:
            if isinstance(current_prop, dict):
                # Update existing range
                current_prop['min'] = prop_data['min']
                current_prop['max'] = prop_data['max']
                current_prop['unit'] = prop_data.get('unit', current_prop.get('unit', ''))
                current_prop['source'] = prop_data.get('source', 'Published research')
                current_prop['confidence'] = prop_data.get('confidence', 75)
                if 'notes' in prop_data:
                    current_prop['notes'] = prop_data['notes']
                
                # Save back to correct location (materialProperties -> category -> properties -> prop_name)
                if property_parent:
                    fm_data[property_location][property_parent]['properties'][prop_name] = current_prop
                else:
                    fm_data[property_location][prop_name] = current_prop
                return True
        
        return False
    
    def update_frontmatter_file(self, filepath: Path) -> Optional[Dict]:
        """Update a single frontmatter file"""
        try:
            # Load frontmatter
            with open(filepath, 'r', encoding='utf-8') as f:
                fm_data = yaml.safe_load(f)
            
            if not fm_data:
                return None
            
            # Get material name and find in Materials.yaml
            material_name = fm_data.get('name')
            if not material_name:
                return None
            
            # Find material in Materials.yaml
            materials_dict = self.materials.get('materials', {})
            material_data = None
            for mat_key, mat_val in materials_dict.items():
                if isinstance(mat_val, dict) and mat_key == material_name:
                    material_data = mat_val
                    break
            
            if not material_data:
                return None
            
            category = material_data.get('category')
            if not category:
                return None
            
            # Get authoritative properties for this category
            auth_props = self.get_authoritative_properties(category)
            if not auth_props:
                return None
            
            # Update each property
            updates_made = []
            for prop_name, prop_data in auth_props.items():
                if self.update_property_in_frontmatter(fm_data, prop_name, prop_data):
                    updates_made.append(prop_name)
            
            if not updates_made:
                return None
            
            # Save updated frontmatter
            if not self.dry_run:
                self._save_yaml(fm_data, filepath)
            
            return {
                'file': filepath.name,
                'material': material_name,
                'category': category,
                'properties_updated': updates_made,
                'count': len(updates_made)
            }
            
        except Exception as e:
            print(f"⚠️  Error processing {filepath.name}: {e}")
            return None
    
    def update_all_frontmatter(self):
        """Update all frontmatter files"""
        print("=" * 80)
        print(" 📝 UPDATING FRONTMATTER RANGES FROM CATEGORIES.YAML")
        print("=" * 80)
        
        if self.dry_run:
            print("\n🔍 DRY RUN MODE - No files will be modified\n")
        
        # Get all frontmatter files
        frontmatter_files = list(self.frontmatter_dir.glob("*.yaml"))
        print(f"\n📂 Found {len(frontmatter_files)} frontmatter files\n")
        
        # Process each file
        for filepath in sorted(frontmatter_files):
            result = self.update_frontmatter_file(filepath)
            if result:
                status = "🔍" if self.dry_run else "✅"
                print(f"{status} {result['material']:40} ({result['category']:10}) → {result['count']} properties")
                for prop in result['properties_updated']:
                    print(f"     • {prop}")
                
                self.files_updated += 1
                self.properties_updated += result['count']
                self.updates_log.append(result)
        
        # Summary
        print("\n" + "=" * 80)
        print(" 📊 UPDATE SUMMARY")
        print("=" * 80)
        print(f"\nFiles updated:       {self.files_updated}")
        print(f"Properties updated:  {self.properties_updated}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN - No changes were saved")
            print("   Run without --dry-run to apply updates")
        else:
            print("\n✅ All updates saved to frontmatter files")
        
        # Breakdown by category
        by_category = {}
        for update in self.updates_log:
            cat = update['category']
            if cat not in by_category:
                by_category[cat] = {'files': 0, 'props': 0}
            by_category[cat]['files'] += 1
            by_category[cat]['props'] += update['count']
        
        print("\n📁 Updates by category:")
        for cat in sorted(by_category.keys()):
            info = by_category[cat]
            print(f"  {cat:15} {info['files']:3} files, {info['props']:3} properties")
        
        print("\n" + "=" * 80)
        
        # Save update log
        if not self.dry_run and self.updates_log:
            log_path = self.data_dir / "Frontmatter_Range_Updates.yaml"
            log_data = {
                'update_timestamp': datetime.now().isoformat(),
                'files_updated': self.files_updated,
                'properties_updated': self.properties_updated,
                'updates': self.updates_log
            }
            self._save_yaml(log_data, log_path)
            print(f"✅ Update log saved: {log_path.name}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update frontmatter ranges from Categories.yaml without full regeneration"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be updated without making changes"
    )
    
    args = parser.parse_args()
    
    try:
        updater = FrontmatterRangeUpdater(dry_run=args.dry_run)
        updater.update_all_frontmatter()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
