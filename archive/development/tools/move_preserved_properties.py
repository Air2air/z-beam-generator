#!/usr/bin/env python3
"""
Move complete properties from preservedData to materialProperties or machineSettings.

This script identifies properties in preservedData that have complete range data
(min, max, unit) and moves them to the appropriate active sections.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import shutil

# Root directory
ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTMATTER_DIR = ROOT_DIR / "content" / "frontmatter"
BACKUP_DIR = ROOT_DIR / "backups" / f"preserve_move_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Properties that belong in machineSettings vs materialProperties
MACHINE_SETTING_PROPERTIES = {
    'powerRange', 'wavelength', 'spotSize', 'repetitionRate',
    'pulseWidth', 'scanSpeed', 'fluence', 'overlapRatio', 'passCount',
    'fluenceThreshold', 'energyDensity', 'dwellTime'
}

# Properties that should go in laser_material_interaction vs material_characteristics
LASER_INTERACTION_PROPERTIES = {
    'ablationThreshold', 'laserReflectivity', 'laserAbsorption', 'absorptivity',
    'absorptionCoefficient', 'reflectivity', 'transmittance', 'scatteringCoefficient'
}


class PreservedPropertyMover:
    """Moves complete properties from preservedData to active sections."""
    
    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'backed_up': 0,
            'properties_moved': 0,
            'machine_settings_moved': 0,
            'material_props_moved': 0
        }
        self.changes_log: List[str] = []
        
    def backup_file(self, file_path: Path) -> bool:
        """Create backup of original file."""
        if not self.backup:
            return True
            
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            backup_path = BACKUP_DIR / file_path.name
            shutil.copy2(file_path, backup_path)
            self.stats['backed_up'] += 1
            return True
        except Exception as e:
            self.changes_log.append(f"❌ Backup failed for {file_path.name}: {str(e)}")
            return False
    
    def is_complete_property(self, prop_data: Dict) -> bool:
        """Check if a property has complete range data."""
        if not isinstance(prop_data, dict):
            return False
        
        required_fields = {'min', 'max', 'unit'}
        return all(field in prop_data and prop_data[field] is not None for field in required_fields)
    
    def get_property_destination(self, prop_name: str) -> Tuple[str, str]:
        """Determine where a property should go: (section, category)."""
        if prop_name in MACHINE_SETTING_PROPERTIES:
            return 'machineSettings', ''
        elif prop_name in LASER_INTERACTION_PROPERTIES:
            return 'materialProperties', 'laser_material_interaction'
        else:
            return 'materialProperties', 'material_characteristics'
    
    def create_property_value_object(self, preserved_data: Dict, individual_data: Optional[Dict] = None) -> Dict:
        """Create a PropertyValue object from preserved data."""
        prop_obj = {
            'min': preserved_data['min'],
            'max': preserved_data['max'],
            'unit': preserved_data['unit']
        }
        
        # Add individual property value if available
        if individual_data and 'value' in individual_data:
            prop_obj['value'] = individual_data['value']
        
        # Add research basis or source information
        if 'research_basis' in preserved_data:
            prop_obj['research_basis'] = preserved_data['research_basis']
        elif 'source' in preserved_data:
            prop_obj['research_basis'] = f"Range data from {preserved_data['source']}"
        elif individual_data and 'source' in individual_data:
            prop_obj['research_basis'] = individual_data['source']
        else:
            prop_obj['research_basis'] = 'materials_science_research'
        
        # Add confidence if available
        if 'confidence' in preserved_data:
            prop_obj['confidence'] = preserved_data['confidence']
        elif individual_data and 'confidence' in individual_data:
            prop_obj['confidence'] = individual_data['confidence']
        
        # Add description if available
        if individual_data and 'description' in individual_data:
            prop_obj['description'] = individual_data['description']
        
        return prop_obj
    
    def ensure_material_properties_structure(self, data: Dict):
        """Ensure materialProperties has the correct category structure."""
        if 'materialProperties' not in data:
            data['materialProperties'] = {}
        
        # Ensure both categories exist
        if 'material_characteristics' not in data['materialProperties']:
            data['materialProperties']['material_characteristics'] = {
                'label': 'Material Characteristics',
                'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
            }
        
        if 'laser_material_interaction' not in data['materialProperties']:
            data['materialProperties']['laser_material_interaction'] = {
                'label': 'Laser-Material Interaction',
                'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds'
            }
    
    def move_properties_from_preserved(self, data: Dict, filename: str) -> List[str]:
        """Move complete properties from preservedData to active sections."""
        changes = []
        
        if 'preservedData' not in data:
            return changes
        
        # Get preserved category ranges and individual properties
        category_ranges = data['preservedData'].get('categoryInfo', {}).get('category_ranges', {})
        individual_props = data['preservedData'].get('generationMetadata', {}).get('properties', {})
        
        # Get current active properties to avoid duplicates
        current_material_props = set()
        current_machine_props = set()
        
        if 'materialProperties' in data:
            for cat_data in data['materialProperties'].values():
                if isinstance(cat_data, dict):
                    # Handle both old flat structure and new nested structure
                    if 'properties' in cat_data:
                        current_material_props.update(cat_data['properties'].keys())
                    else:
                        # Skip label and description keys
                        props = {k: v for k, v in cat_data.items() if k not in ['label', 'description']}
                        current_material_props.update(props.keys())
        
        if 'machineSettings' in data:
            current_machine_props.update(data['machineSettings'].keys())
        
        # Process each property in category ranges
        for prop_name, range_data in category_ranges.items():
            # Skip if not complete or already exists in active sections
            if not self.is_complete_property(range_data):
                continue
            
            if prop_name in current_material_props or prop_name in current_machine_props:
                continue
            
            # Determine destination
            section, category = self.get_property_destination(prop_name)
            
            # Get individual property data if available
            individual_data = individual_props.get(prop_name)
            
            # Create property object
            prop_obj = self.create_property_value_object(range_data, individual_data)
            
            # Move to destination
            if section == 'machineSettings':
                if 'machineSettings' not in data:
                    data['machineSettings'] = {}
                data['machineSettings'][prop_name] = prop_obj
                changes.append(f"  Moved {prop_name} to machineSettings")
                self.stats['machine_settings_moved'] += 1
            
            elif section == 'materialProperties':
                self.ensure_material_properties_structure(data)
                
                # Add to appropriate category
                if category not in data['materialProperties']:
                    data['materialProperties'][category] = {}
                
                data['materialProperties'][category][prop_name] = prop_obj
                changes.append(f"  Moved {prop_name} to materialProperties.{category}")
                self.stats['material_props_moved'] += 1
            
            self.stats['properties_moved'] += 1
        
        return changes
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single frontmatter YAML file."""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Move properties
            changes = self.move_properties_from_preserved(data, file_path.name)
            
            # If changes were made
            if changes:
                # Backup original
                if not self.dry_run:
                    if not self.backup_file(file_path):
                        return False
                
                # Write updated file
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                print(f"✅ {file_path.name}")
                for change in changes:
                    print(change)
                
                self.stats['processed'] += 1
            else:
                self.stats['skipped'] += 1
            
            return True
            
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            self.changes_log.append(f"❌ {error_msg}")
            print(f"❌ {error_msg}")
            self.stats['errors'] += 1
            return False
    
    def process_all_files(self) -> Dict:
        """Process all frontmatter YAML files."""
        if not FRONTMATTER_DIR.exists():
            print(f"❌ Frontmatter directory not found: {FRONTMATTER_DIR}")
            return self.stats
        
        yaml_files = sorted(list(FRONTMATTER_DIR.glob("*.yaml")))
        self.stats['total_files'] = len(yaml_files)
        
        print(f"\n{'=' * 70}")
        print(f"Moving Complete Properties from preservedData")
        print(f"{'=' * 70}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE PROCESSING'}")
        print(f"Backup: {'Enabled' if self.backup else 'Disabled'}")
        print(f"Files: {self.stats['total_files']}")
        print(f"Directory: {FRONTMATTER_DIR}")
        if self.backup:
            print(f"Backup Dir: {BACKUP_DIR}")
        print(f"{'=' * 70}\n")
        
        for yaml_file in yaml_files:
            self.process_file(yaml_file)
        
        return self.stats
    
    def print_summary(self):
        """Print processing summary."""
        print(f"\n{'=' * 70}")
        print(f"Property Movement Summary")
        print(f"{'=' * 70}")
        print(f"Total Files:              {self.stats['total_files']}")
        print(f"Processed (with changes): {self.stats['processed']} ✅")
        print(f"Skipped (no changes):     {self.stats['skipped']} ⏭️")
        print(f"Errors:                   {self.stats['errors']} ❌")
        if self.backup:
            print(f"Backed Up:                {self.stats['backed_up']} 💾")
        print(f"\nProperties Moved:")
        print(f"  Total Properties:         {self.stats['properties_moved']}")
        print(f"  To machineSettings:       {self.stats['machine_settings_moved']}")
        print(f"  To materialProperties:    {self.stats['material_props_moved']}")
        print(f"{'=' * 70}")
        
        if self.changes_log:
            print(f"\n⚠️  Issues Log ({len(self.changes_log)} items):")
            for log in self.changes_log[:10]:
                print(f"  {log}")
            if len(self.changes_log) > 10:
                print(f"  ... and {len(self.changes_log) - 10} more")
        
        if self.dry_run:
            print(f"\n⚠️  DRY RUN - No files were modified")
        else:
            print(f"\n✅ Processing complete - {self.stats['processed']} files updated")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Move complete properties from preservedData to active sections',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python3 scripts/tools/move_preserved_properties.py --dry-run
  
  # Process with backup
  python3 scripts/tools/move_preserved_properties.py
  
  # Process without backup
  python3 scripts/tools/move_preserved_properties.py --no-backup
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backups')
    
    args = parser.parse_args()
    
    mover = PreservedPropertyMover(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    mover.process_all_files()
    mover.print_summary()
    
    sys.exit(0 if mover.stats['errors'] == 0 else 1)


if __name__ == '__main__':
    main()