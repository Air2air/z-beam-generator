#!/usr/bin/env python3
"""
Populate null min/max ranges in frontmatter files.

Rule (Priority Order):
1. FIRST: Check if published ranges exist in Categories.yaml for the property
2. SECOND: Conduct deep web searches for authoritative published category ranges
3. FALLBACK: Calculate min/max from sibling materials within the same category

This ensures all properties have contextual ranges showing where each material
falls within its category spectrum, prioritizing published scientific data over
calculated ranges from our own Materials data.
"""

import yaml
from pathlib import Path
from collections import defaultdict
import sys


class SiblingRangePopulator:
    """Populate null ranges with values calculated from sibling materials."""
    
    def __init__(self, frontmatter_dir: Path):
        self.frontmatter_dir = frontmatter_dir
        self.materials_by_category = defaultdict(list)
        self.category_ranges = {}
        self.updates_made = 0
        self.files_updated = 0
        
    def load_materials(self):
        """Load all frontmatter files and group by category."""
        print("📂 Loading frontmatter files...")
        files = list(self.frontmatter_dir.glob('*.yaml'))
        
        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            category = data.get('category', 'unknown')
            self.materials_by_category[category].append({
                'filepath': filepath,
                'data': data,
                'name': data.get('name', filepath.stem)
            })
        
        print(f"   Loaded {len(files)} materials across {len(self.materials_by_category)} categories")
    
    def calculate_category_ranges(self):
        """
        Calculate min/max ranges for properties within each category.
        
        IMPORTANT: This is the FALLBACK method. Before using these calculated ranges,
        deep web searches should be conducted to find published authoritative ranges
        for each property-category combination.
        """
        print("\n🔢 Calculating ranges from sibling materials (FALLBACK method)...")
        
        for category, materials in self.materials_by_category.items():
            print(f"\n   {category.upper()} ({len(materials)} materials):")
            property_values = defaultdict(list)
            
            # Collect all property values from materialProperties
            for material in materials:
                data = material['data']
                mat_props = data.get('materialProperties', {})
                
                for section_key, section_data in mat_props.items():
                    if isinstance(section_data, dict) and 'properties' in section_data:
                        for prop_key, prop_data in section_data['properties'].items():
                            if isinstance(prop_data, dict) and 'value' in prop_data:
                                value = prop_data.get('value')
                                unit = prop_data.get('unit')
                                
                                # Only process numeric values with null ranges
                                if (value is not None and 
                                    isinstance(value, (int, float)) and
                                    prop_data.get('min') is None and 
                                    prop_data.get('max') is None):
                                    
                                    property_values[prop_key].append({
                                        'value': float(value),
                                        'unit': unit,
                                        'material': material['name']
                                    })
                
                # Collect machineSettings values
                machine_settings = data.get('machineSettings', {})
                for setting_key, setting_data in machine_settings.items():
                    if isinstance(setting_data, dict) and 'value' in setting_data:
                        value = setting_data.get('value')
                        unit = setting_data.get('unit')
                        
                        if (value is not None and 
                            isinstance(value, (int, float)) and
                            setting_data.get('min') is None and 
                            setting_data.get('max') is None):
                            
                            property_values[f"machineSettings.{setting_key}"].append({
                                'value': float(value),
                                'unit': unit,
                                'material': material['name']
                            })
            
            # Calculate ranges (need at least 2 materials)
            self.category_ranges[category] = {}
            for prop_key, values in property_values.items():
                if len(values) >= 2:
                    numeric_values = [v['value'] for v in values]
                    min_val = min(numeric_values)
                    max_val = max(numeric_values)
                    unit = values[0]['unit']
                    
                    # Store calculated range
                    self.category_ranges[category][prop_key] = {
                        'min': min_val,
                        'max': max_val,
                        'unit': unit,
                        'sample_size': len(values),
                        'source': 'sibling_materials'
                    }
                    
                    print(f"      ✓ {prop_key}: {min_val} - {max_val} {unit} (n={len(values)})")
    
    def update_frontmatter_files(self, dry_run: bool = False):
        """Update all frontmatter files with calculated ranges."""
        action = "Would update" if dry_run else "Updating"
        print(f"\n📝 {action} frontmatter files...")
        
        for category, materials in self.materials_by_category.items():
            category_property_ranges = self.category_ranges.get(category, {})
            
            if not category_property_ranges:
                continue
            
            for material in materials:
                filepath = material['filepath']
                data = material['data']
                modified = False
                
                # Update materialProperties
                mat_props = data.get('materialProperties', {})
                for section_key, section_data in mat_props.items():
                    if isinstance(section_data, dict) and 'properties' in section_data:
                        for prop_key, prop_data in section_data['properties'].items():
                            if isinstance(prop_data, dict):
                                # Check if needs update
                                if (prop_data.get('min') is None and 
                                    prop_data.get('max') is None and
                                    prop_key in category_property_ranges):
                                    
                                    range_info = category_property_ranges[prop_key]
                                    prop_data['min'] = range_info['min']
                                    prop_data['max'] = range_info['max']
                                    modified = True
                                    self.updates_made += 1
                
                # Update machineSettings
                machine_settings = data.get('machineSettings', {})
                for setting_key, setting_data in machine_settings.items():
                    if isinstance(setting_data, dict):
                        lookup_key = f"machineSettings.{setting_key}"
                        
                        if (setting_data.get('min') is None and 
                            setting_data.get('max') is None and
                            lookup_key in category_property_ranges):
                            
                            range_info = category_property_ranges[lookup_key]
                            setting_data['min'] = range_info['min']
                            setting_data['max'] = range_info['max']
                            modified = True
                            self.updates_made += 1
                
                # Write updated file
                if modified:
                    self.files_updated += 1
                    if not dry_run:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            yaml.dump(data, f, default_flow_style=False, 
                                    allow_unicode=True, sort_keys=False, width=1000)
    
    def generate_report(self):
        """Generate summary report."""
        print(f"\n{'='*70}")
        print("📊 SUMMARY REPORT")
        print(f"{'='*70}\n")
        
        print(f"Categories processed: {len(self.category_ranges)}")
        print(f"Files updated: {self.files_updated}")
        print(f"Properties updated: {self.updates_made}")
        
        print(f"\n{'='*70}")
        print("RANGES BY CATEGORY:")
        print(f"{'='*70}\n")
        
        for category in sorted(self.category_ranges.keys()):
            ranges = self.category_ranges[category]
            print(f"\n{category.upper()}: {len(ranges)} properties")
            for prop_key in sorted(ranges.keys())[:10]:  # Show first 10
                range_info = ranges[prop_key]
                print(f"   {prop_key}: {range_info['min']} - {range_info['max']} "
                      f"{range_info['unit']} (n={range_info['sample_size']})")
            
            if len(ranges) > 10:
                print(f"   ... and {len(ranges) - 10} more properties")
    
    def run(self, dry_run: bool = False):
        """Execute the full population process."""
        print("=" * 70)
        print("RANGE POPULATOR")
        print("=" * 70)
        print("\nRule (Priority Order):")
        print("  1. Use published ranges from Categories.yaml (already populated)")
        print("  2. Conduct deep web searches for authoritative category ranges")
        print("  3. Calculate min/max from sibling materials (fallback)\n")
        print("NOTE: This script currently implements step 3 (sibling calculation).")
        print("      Deep web search integration (step 2) should be implemented")
        print("      before running this script to ensure priority order.\n")
        
        if dry_run:
            print("⚠️  DRY RUN MODE - No files will be modified\n")
        
        self.load_materials()
        self.calculate_category_ranges()
        self.update_frontmatter_files(dry_run=dry_run)
        self.generate_report()
        
        if dry_run:
            print("\n⚠️  This was a DRY RUN. Run without --dry-run to apply changes.")
        else:
            print("\n✅ All frontmatter files updated successfully!")


def main():
    """Main entry point."""
    frontmatter_dir = Path(__file__).parent.parent / 'content' / 'components' / 'frontmatter'
    
    if not frontmatter_dir.exists():
        print(f"❌ Error: Frontmatter directory not found: {frontmatter_dir}")
        sys.exit(1)
    
    # Check for dry-run flag
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    populator = SiblingRangePopulator(frontmatter_dir)
    populator.run(dry_run=dry_run)


if __name__ == '__main__':
    main()
