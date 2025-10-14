#!/usr/bin/env python3
"""
Add category-specific thermal property fields to existing frontmatter files.

This script adds the new thermal property fields (thermalDestructionPoint, 
sinteringPoint, etc.) to existing frontmatter YAML files WITHOUT regenerating 
the entire frontmatter content. It preserves all existing data and only adds 
the new thermal property field.

Usage:
    python3 scripts/add_thermal_properties_to_frontmatter.py [--dry-run]
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import argparse


# Thermal property mapping by category
THERMAL_PROPERTY_MAP = {
    'wood': {
        'field': 'thermalDestructionPoint',
        'label': 'Decomposition Point',
        'description': 'Temperature where pyrolysis (thermal decomposition) begins',
        'yaml_field': 'thermalDestructionPoint'
    },
    'ceramic': {
        'field': 'sinteringPoint',
        'label': 'Sintering/Decomposition Point',
        'description': 'Temperature where particle fusion or decomposition occurs',
        'yaml_field': 'meltingPoint'  # Ceramics use meltingPoint in Materials.yaml
    },
    'stone': {
        'field': 'thermalDegradationPoint',
        'label': 'Thermal Degradation Point',
        'description': 'Temperature where structural breakdown begins',
        'yaml_field': 'thermalDestructionPoint'
    },
    'composite': {
        'field': 'degradationPoint',
        'label': 'Degradation Point',
        'description': 'Temperature where polymer matrix decomposition begins',
        'yaml_field': 'thermalDestructionPoint'
    },
    'plastic': {
        'field': 'degradationPoint',
        'label': 'Degradation Point',
        'description': 'Temperature where polymer chain breakdown begins',
        'yaml_field': 'thermalDestructionPoint'
    },
    'glass': {
        'field': 'softeningPoint',
        'label': 'Softening Point',
        'description': 'Temperature where glass transitions from rigid to pliable state',
        'yaml_field': 'meltingPoint'  # Glass uses meltingPoint in Materials.yaml
    },
    'masonry': {
        'field': 'thermalDegradationPoint',
        'label': 'Thermal Degradation Point',
        'description': 'Temperature where structural breakdown begins',
        'yaml_field': 'thermalDestructionPoint'
    },
    # Metal and semiconductor use standard meltingPoint (no additional field needed)
}


class ThermalPropertyAdder:
    """Add thermal property fields to existing frontmatter files."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.root_path = Path(__file__).parent.parent
        self.materials_yaml_path = self.root_path / 'data' / 'Materials.yaml'
        self.categories_yaml_path = self.root_path / 'data' / 'Categories.yaml'
        self.frontmatter_dir = self.root_path / 'content' / 'components' / 'frontmatter'
        
        # Load Materials.yaml
        with open(self.materials_yaml_path, 'r') as f:
            self.materials_data = yaml.safe_load(f)
        
        # Load Categories.yaml for ranges
        with open(self.categories_yaml_path, 'r') as f:
            self.categories_data = yaml.safe_load(f)
        
        self.stats = {
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'by_category': {}
        }
    
    def get_material_data(self, material_name: str) -> Optional[Dict[str, Any]]:
        """Get material data from Materials.yaml."""
        materials = self.materials_data.get('materials', {})
        return materials.get(material_name)
    
    def get_thermal_property_from_yaml(
        self, 
        material_name: str, 
        yaml_field: str
    ) -> Optional[Dict[str, Any]]:
        """Extract thermal property data from Materials.yaml."""
        material_data = self.get_material_data(material_name)
        if not material_data:
            return None
        
        # Get the thermal property from the YAML field
        thermal_value = material_data.get(yaml_field)
        if thermal_value is None:
            return None
        
        return {
            'value': float(thermal_value),
            'unit': '°C',
            'confidence': 90,
        }
    
    def get_category_ranges(self, category: str, field: str) -> Dict[str, Optional[float]]:
        """Get min/max ranges for a thermal property from Categories.yaml."""
        categories = self.categories_data.get('categories', {})
        category_data = categories.get(category.lower(), {})
        property_ranges = category_data.get('propertyRanges', {})
        field_ranges = property_ranges.get(field, {})
        
        return {
            'min': field_ranges.get('min'),
            'max': field_ranges.get('max')
        }
    
    def should_add_thermal_property(
        self, 
        category: str, 
        properties: Dict[str, Any],
        thermal_field: str
    ) -> bool:
        """Check if thermal property should be added."""
        category_lower = category.lower()
        
        # Skip if category doesn't have a thermal mapping
        if category_lower not in THERMAL_PROPERTY_MAP:
            return False
        
        # Skip metals and semiconductors (they only use meltingPoint)
        if category_lower in ['metal', 'semiconductor']:
            return False
        
        # Skip if thermal field already exists
        if thermal_field in properties:
            return False
        
        return True
    
    def add_thermal_property_to_frontmatter(self, frontmatter_path: Path) -> bool:
        """Add thermal property to a single frontmatter file."""
        try:
            # Load frontmatter YAML
            with open(frontmatter_path, 'r') as f:
                frontmatter = yaml.safe_load(f)
            
            if not frontmatter:
                print(f"⚠️  Empty frontmatter: {frontmatter_path.name}")
                return False
            
            material_name = frontmatter.get('name')
            category = frontmatter.get('category')
            
            if not material_name or not category:
                print(f"⚠️  Missing name or category: {frontmatter_path.name}")
                return False
            
            category_lower = category.lower()
            self.stats['processed'] += 1
            
            # Initialize category stats
            if category_lower not in self.stats['by_category']:
                self.stats['by_category'][category_lower] = {
                    'processed': 0,
                    'updated': 0,
                    'skipped': 0
                }
            
            self.stats['by_category'][category_lower]['processed'] += 1
            
            # Get thermal mapping for this category
            thermal_config = THERMAL_PROPERTY_MAP.get(category_lower)
            if not thermal_config:
                # Skip metals/semiconductors (no additional thermal field needed)
                self.stats['by_category'][category_lower]['skipped'] += 1
                return False
            
            thermal_field = thermal_config['field']
            properties = frontmatter.get('materialProperties', {})
            
            # Check if we should add the property
            if not self.should_add_thermal_property(category, properties, thermal_field):
                print(f"⏭️  Skipping {material_name} - field already exists or not applicable")
                self.stats['by_category'][category_lower]['skipped'] += 1
                self.stats['skipped'] += 1
                return False
            
            # Get thermal data from Materials.yaml
            yaml_field = thermal_config['yaml_field']
            thermal_data = self.get_thermal_property_from_yaml(material_name, yaml_field)
            
            if not thermal_data:
                # Fallback: copy from existing meltingPoint if available
                melting_point = properties.get('meltingPoint')
                if isinstance(melting_point, dict) and 'value' in melting_point:
                    thermal_data = {
                        'value': melting_point['value'],
                        'unit': melting_point.get('unit', '°C'),
                        'confidence': melting_point.get('confidence', 85)
                    }
                else:
                    print(f"⚠️  No thermal data found for {material_name}")
                    self.stats['by_category'][category_lower]['skipped'] += 1
                    self.stats['skipped'] += 1
                    return False
            
            # Add description and ranges
            thermal_data['description'] = thermal_config['description']
            
            # Get ranges from Categories.yaml
            ranges = self.get_category_ranges(category, thermal_field)
            thermal_data['min'] = ranges.get('min')
            thermal_data['max'] = ranges.get('max')
            
            # Add the new thermal property field
            if 'materialProperties' not in frontmatter:
                frontmatter['materialProperties'] = {}
            
            frontmatter['materialProperties'][thermal_field] = thermal_data
            
            if self.dry_run:
                print(f"✓ [DRY RUN] Would add {thermal_field} to {material_name}")
                print(f"  Value: {thermal_data['value']}°C")
            else:
                # Write updated frontmatter back to file
                with open(frontmatter_path, 'w') as f:
                    yaml.dump(frontmatter, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                print(f"✓ Added {thermal_field} to {material_name} ({thermal_data['value']}°C)")
            
            self.stats['updated'] += 1
            self.stats['by_category'][category_lower]['updated'] += 1
            return True
            
        except Exception as e:
            print(f"❌ Error processing {frontmatter_path.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def process_all_frontmatter(self):
        """Process all frontmatter files in the directory."""
        print(f"\n{'=' * 70}")
        print(f"{'DRY RUN MODE - NO FILES WILL BE MODIFIED' if self.dry_run else 'PROCESSING FRONTMATTER FILES'}")
        print(f"{'=' * 70}\n")
        
        # Get all frontmatter YAML files
        frontmatter_files = sorted(self.frontmatter_dir.glob('*.yaml'))
        
        if not frontmatter_files:
            print(f"❌ No frontmatter files found in {self.frontmatter_dir}")
            return
        
        print(f"Found {len(frontmatter_files)} frontmatter files\n")
        
        # Process each file
        for frontmatter_path in frontmatter_files:
            self.add_thermal_property_to_frontmatter(frontmatter_path)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print processing summary."""
        print(f"\n{'=' * 70}")
        print("SUMMARY")
        print(f"{'=' * 70}\n")
        
        print(f"Total files processed: {self.stats['processed']}")
        print(f"Files updated: {self.stats['updated']}")
        print(f"Files skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")
        
        print("\n\nBy Category:")
        print(f"{'-' * 70}")
        for category, stats in sorted(self.stats['by_category'].items()):
            print(f"\n{category.upper()}:")
            print(f"  Processed: {stats['processed']}")
            print(f"  Updated: {stats['updated']}")
            print(f"  Skipped: {stats['skipped']}")
        
        if self.dry_run:
            print(f"\n{'=' * 70}")
            print("DRY RUN COMPLETE - No files were modified")
            print("Run without --dry-run to apply changes")
            print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description='Add thermal property fields to existing frontmatter files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    args = parser.parse_args()
    
    adder = ThermalPropertyAdder(dry_run=args.dry_run)
    adder.process_all_frontmatter()


if __name__ == '__main__':
    main()
