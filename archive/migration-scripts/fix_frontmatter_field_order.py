#!/usr/bin/env python3
"""
Frontmatter Field Order Correction Script

Reorders property fields in frontmatter files to match the example format:
1. value
2. min  
3. max
4. unit
5. research_basis

Usage:
    python3 scripts/tools/fix_frontmatter_field_order.py
    python3 scripts/tools/fix_frontmatter_field_order.py --material Slate
    python3 scripts/tools/fix_frontmatter_field_order.py --dry-run
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, OrderedDict
from collections import OrderedDict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

class FrontmatterFieldOrderFixer:
    """Fixes field order in frontmatter property definitions"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent.parent
        self.frontmatter_dir = self.project_root / "content" / "frontmatter"
        
        # Correct field order per example
        self.property_field_order = [
            'value',
            'min', 
            'max',
            'unit',
            'research_basis'
        ]
        
        self.machine_setting_field_order = [
            'value',
            'min',
            'max', 
            'unit',
            'description'
        ]
        
        self.fix_stats = {
            'processed': 0,
            'fixed': 0,
            'properties_reordered': 0,
            'errors': 0
        }
    
    def reorder_fields(self, data: Dict[str, Any], field_order: list) -> tuple[Dict[str, Any], bool]:
        """Reorder fields in a dictionary according to specified order"""
        
        if not isinstance(data, dict):
            return data, False
        
        # Check if reordering is needed
        current_keys = list(data.keys())
        expected_keys = [key for key in field_order if key in data]
        other_keys = [key for key in current_keys if key not in field_order]
        
        # If already in correct order, no change needed
        if current_keys == expected_keys + other_keys:
            return data, False
        
        # Create ordered dictionary with correct field order
        reordered = OrderedDict()
        
        # Add fields in correct order
        for field in field_order:
            if field in data:
                reordered[field] = data[field]
        
        # Add any other fields at the end
        for field in other_keys:
            reordered[field] = data[field]
        
        return dict(reordered), True
    
    def fix_material_properties(self, material_properties: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
        """Fix field order in all material properties"""
        
        fixed_props = material_properties.copy()
        properties_reordered = 0
        
        # Process both sections
        for section_name in ['material_characteristics', 'laser_material_interaction']:
            if section_name in fixed_props:
                section = fixed_props[section_name].copy()
                
                # Process each property in the section
                for prop_name, prop_data in section.items():
                    if prop_name in ['label', 'description']:
                        continue  # Skip section metadata
                    
                    reordered_prop, was_reordered = self.reorder_fields(
                        prop_data, self.property_field_order
                    )
                    
                    if was_reordered:
                        section[prop_name] = reordered_prop
                        properties_reordered += 1
                
                fixed_props[section_name] = section
        
        return fixed_props, properties_reordered
    
    def fix_machine_settings(self, machine_settings: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
        """Fix field order in machine settings"""
        
        fixed_settings = machine_settings.copy()
        settings_reordered = 0
        
        for setting_name, setting_data in machine_settings.items():
            reordered_setting, was_reordered = self.reorder_fields(
                setting_data, self.machine_setting_field_order
            )
            
            if was_reordered:
                fixed_settings[setting_name] = reordered_setting
                settings_reordered += 1
        
        return fixed_settings, settings_reordered
    
    def fix_frontmatter_file(self, file_path: Path) -> bool:
        """Fix field order in a single frontmatter file"""
        
        try:
            # Load frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                frontmatter_data = yaml.safe_load(f)
            
            if not frontmatter_data:
                print(f"  ⚠️  Empty file: {file_path.name}")
                return False
            
            total_reordered = 0
            
            # Fix materialProperties field order
            if 'materialProperties' in frontmatter_data:
                fixed_props, props_reordered = self.fix_material_properties(
                    frontmatter_data['materialProperties']
                )
                
                if props_reordered > 0:
                    frontmatter_data['materialProperties'] = fixed_props
                    total_reordered += props_reordered
            
            # Fix machineSettings field order
            if 'machineSettings' in frontmatter_data:
                fixed_settings, settings_reordered = self.fix_machine_settings(
                    frontmatter_data['machineSettings']
                )
                
                if settings_reordered > 0:
                    frontmatter_data['machineSettings'] = fixed_settings
                    total_reordered += settings_reordered
            
            if total_reordered > 0:
                if not self.dry_run:
                    # Write fixed file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(frontmatter_data, f, default_flow_style=False,
                                 allow_unicode=True, sort_keys=False, indent=2)
                
                print(f"  ✅ Fixed: {file_path.name} ({total_reordered} fields reordered)")
                self.fix_stats['properties_reordered'] += total_reordered
                return True
            else:
                print(f"  ➖ No reordering needed: {file_path.name}")
                return False
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            self.fix_stats['errors'] += 1
            return False
    
    def fix_material(self, material_name: str) -> bool:
        """Fix specific material frontmatter file"""
        
        file_path = self.frontmatter_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        print(f"🔧 Fixing field order for {material_name}...")
        fixed = self.fix_frontmatter_file(file_path)
        
        self.fix_stats['processed'] += 1
        if fixed:
            self.fix_stats['fixed'] += 1
        
        return fixed
    
    def fix_all_materials(self) -> None:
        """Fix field order in all frontmatter files"""
        
        frontmatter_files = list(self.frontmatter_dir.glob("*-laser-cleaning.yaml"))
        total_files = len(frontmatter_files)
        
        print(f"🔧 Starting field order correction for {total_files} frontmatter files...")
        print(f"📁 Source directory: {self.frontmatter_dir}")
        print(f"📋 Mode: {'DRY RUN' if self.dry_run else 'LIVE CORRECTION'}")
        print(f"🎯 Correct order: {' → '.join(self.property_field_order)}")
        print("-" * 80)
        
        for i, file_path in enumerate(frontmatter_files, 1):
            print(f"[{i}/{total_files}] ", end="")
            fixed = self.fix_frontmatter_file(file_path)
            
            self.fix_stats['processed'] += 1
            if fixed:
                self.fix_stats['fixed'] += 1
        
        print("-" * 80)
        print("📊 FIELD ORDER CORRECTION SUMMARY")
        print(f"  📁 Processed: {self.fix_stats['processed']}")
        print(f"  ✅ Fixed: {self.fix_stats['fixed']}")
        print(f"  🔄 Fields Reordered: {self.fix_stats['properties_reordered']}")
        print(f"  ❌ Errors: {self.fix_stats['errors']}")
        
        if self.fix_stats['errors'] == 0:
            print("🎉 Field order correction completed successfully!")
        else:
            print(f"⚠️  Field order correction completed with {self.fix_stats['errors']} errors")

def main():
    parser = argparse.ArgumentParser(description='Fix field order in frontmatter files')
    parser.add_argument('--material', help='Fix specific material only')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing files')
    
    args = parser.parse_args()
    
    # Initialize fixer
    fixer = FrontmatterFieldOrderFixer(dry_run=args.dry_run)
    
    # Fix materials
    if args.material:
        fixer.fix_material(args.material)
    else:
        fixer.fix_all_materials()

if __name__ == '__main__':
    main()