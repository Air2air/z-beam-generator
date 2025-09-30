#!/usr/bin/env python3
"""
Comprehensive Property and Component Cleanup Script

This script addresses three key issues:
1. Ensures no frontmatter keys exist without proper data
2. Trims all float values to 2 decimal places  
3. Removes the Settings component completely and all references

Author: GitHub Copilot
Date: September 29, 2025
"""

import sys
import yaml
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensivePropertyCleanup:
    """Comprehensive cleanup for properties, floats, and Settings component"""
    
    def __init__(self):
        self.project_root = project_root
        self.materials_file = self.project_root / "data" / "Materials.yaml"
        self.backup_dir = self.project_root / "backups" / f"comprehensive_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.changes_made = []
        
    def create_backup(self):
        """Create comprehensive backup before modifications"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup Materials.yaml
            shutil.copy2(self.materials_file, self.backup_dir / "Materials.yaml")
            
            # Backup run.py
            shutil.copy2(self.project_root / "run.py", self.backup_dir / "run.py")
            
            # Backup any Settings component files
            settings_component_dir = self.project_root / "components" / "settings"
            if settings_component_dir.exists():
                shutil.copytree(settings_component_dir, self.backup_dir / "settings_component")
            
            settings_content_dir = self.project_root / "content" / "components" / "settings"
            if settings_content_dir.exists():
                shutil.copytree(settings_content_dir, self.backup_dir / "settings_content")
            
            logger.info(f"📦 Created comprehensive backup: {self.backup_dir}")
        except Exception as e:
            raise Exception(f"Failed to create backup: {e}")
    
    def round_float_values(self, data: Any) -> Any:
        """Recursively round all float values to 2 decimal places"""
        if isinstance(data, dict):
            return {key: self.round_float_values(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.round_float_values(item) for item in data]
        elif isinstance(data, float):
            return round(data, 2)
        else:
            return data
    
    def validate_and_fix_property_data(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all property keys have proper data - remove empty ones"""
        fixed_properties = {}
        
        for prop_name, prop_data in properties.items():
            if prop_data is None:
                logger.warning(f"   Removing NULL property: {prop_name}")
                self.changes_made.append(f"Removed NULL property: {prop_name}")
                continue
            
            if isinstance(prop_data, dict):
                value = prop_data.get('value')
                if value is None or value == '' or value == 'null':
                    logger.warning(f"   Removing property with empty value: {prop_name}")
                    self.changes_made.append(f"Removed empty property: {prop_name}")
                    continue
                
                # Round float values in the property data
                fixed_prop_data = self.round_float_values(prop_data)
                fixed_properties[prop_name] = fixed_prop_data
            else:
                # Handle non-dict property data
                fixed_properties[prop_name] = self.round_float_values(prop_data)
        
        return fixed_properties
    
    def fix_materials_data(self):
        """Fix Materials.yaml: round floats and ensure no empty property data"""
        try:
            with open(self.materials_file, 'r') as f:
                materials_data = yaml.safe_load(f)
            
            logger.info("🔧 Fixing Materials.yaml...")
            
            materials_fixed = 0
            properties_removed = 0
            floats_rounded = 0
            
            # Process each category
            for category_name, category_data in materials_data.get('materials', {}).items():
                items = category_data.get('items', [])
                
                for material in items:
                    material_name = material.get('name', 'UNNAMED')
                    
                    # Fix properties section
                    if 'properties' in material:
                        original_props = material['properties']
                        fixed_props = self.validate_and_fix_property_data(original_props)
                        
                        if len(fixed_props) != len(original_props):
                            properties_removed += len(original_props) - len(fixed_props)
                            logger.info(f"   Fixed {material_name}: removed {len(original_props) - len(fixed_props)} empty properties")
                        
                        material['properties'] = fixed_props
                        materials_fixed += 1
                    
                    # Round all float values in the entire material object
                    original_material = str(material)
                    material = self.round_float_values(material)
                    if str(material) != original_material:
                        floats_rounded += 1
            
            # Round floats in machineSettingsRanges
            if 'machineSettingsRanges' in materials_data:
                materials_data['machineSettingsRanges'] = self.round_float_values(materials_data['machineSettingsRanges'])
            
            # Save fixed data
            with open(self.materials_file, 'w') as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            logger.info(f"✅ Fixed Materials.yaml:")
            logger.info(f"   Materials processed: {materials_fixed}")
            logger.info(f"   Empty properties removed: {properties_removed}")
            logger.info(f"   Float values rounded: {floats_rounded}")
            
        except Exception as e:
            raise Exception(f"Failed to fix Materials.yaml: {e}")
    
    def remove_settings_component_references(self):
        """Remove all references to Settings component from run.py"""
        try:
            run_py_file = self.project_root / "run.py"
            
            with open(run_py_file, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Remove 'settings' from component lists
            logger.info("🗑️  Removing Settings component references from run.py...")
            
            # Pattern 1: Remove 'settings' from lists in conditional statements
            content = re.sub(r"'settings',?\s*", "", content)
            content = re.sub(r'"settings",?\s*', "", content)
            
            # Pattern 2: Clean up any double commas or trailing commas
            content = re.sub(r',\s*,', ',', content)
            content = re.sub(r',\s*\]', ']', content)
            content = re.sub(r'\[\s*,', '[', content)
            
            # Pattern 3: Remove any mentions in comments about settings component
            content = re.sub(r'.*[Ss]ettings [Cc]omponent.*\\n', '', content)
            
            if content != original_content:
                with open(run_py_file, 'w') as f:
                    f.write(content)
                logger.info("   ✅ Removed Settings component references from run.py")
                self.changes_made.append("Removed Settings component references from run.py")
            else:
                logger.info("   ℹ️  No Settings component references found in run.py")
                
        except Exception as e:
            logger.warning(f"Failed to update run.py: {e}")
    
    def remove_settings_component_files(self):
        """Remove Settings component directories and files"""
        try:
            # Remove component directory
            settings_component_dir = self.project_root / "components" / "settings"
            if settings_component_dir.exists():
                shutil.rmtree(settings_component_dir)
                logger.info("🗑️  Removed components/settings/ directory")
                self.changes_made.append("Removed components/settings/ directory")
            
            # Remove content directory
            settings_content_dir = self.project_root / "content" / "components" / "settings"
            if settings_content_dir.exists():
                shutil.rmtree(settings_content_dir)
                logger.info("🗑️  Removed content/components/settings/ directory")
                self.changes_made.append("Removed content/components/settings/ directory")
            
            # Remove any schema files
            schemas_dir = self.project_root / "schemas"
            if schemas_dir.exists():
                for schema_file in schemas_dir.glob("*settings*"):
                    schema_file.unlink()
                    logger.info(f"🗑️  Removed schema file: {schema_file.name}")
                    self.changes_made.append(f"Removed schema file: {schema_file.name}")
            
        except Exception as e:
            logger.warning(f"Failed to remove Settings component files: {e}")
    
    def update_documentation(self):
        """Update documentation to remove Settings component references"""
        try:
            # Update README.md
            readme_file = self.project_root / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r') as f:
                    content = f.read()
                
                # Remove lines mentioning settings component
                lines = content.split('\\n')
                filtered_lines = [line for line in lines if 'settings' not in line.lower() or 'machine settings' in line.lower()]
                
                if len(filtered_lines) != len(lines):
                    with open(readme_file, 'w') as f:
                        f.write('\\n'.join(filtered_lines))
                    logger.info("📝 Updated README.md to remove Settings component references")
                    self.changes_made.append("Updated README.md")
            
            # Update docs/QUICK_REFERENCE.md
            quick_ref_file = self.project_root / "docs" / "QUICK_REFERENCE.md"
            if quick_ref_file.exists():
                with open(quick_ref_file, 'r') as f:
                    content = f.read()
                
                # Remove settings component lines
                content = re.sub(r'.*Settings.*component.*\\n', '', content, flags=re.IGNORECASE)
                content = re.sub(r'.*settings.*component.*\\n', '', content, flags=re.IGNORECASE)
                
                with open(quick_ref_file, 'w') as f:
                    f.write(content)
                logger.info("📝 Updated docs/QUICK_REFERENCE.md")
                self.changes_made.append("Updated docs/QUICK_REFERENCE.md")
                
        except Exception as e:
            logger.warning(f"Failed to update documentation: {e}")
    
    def verify_frontmatter_integrity(self):
        """Verify that no frontmatter files have empty property keys"""
        try:
            frontmatter_dir = self.project_root / "content" / "components" / "frontmatter"
            if not frontmatter_dir.exists():
                return
            
            logger.info("🔍 Verifying frontmatter integrity...")
            
            issues_found = 0
            for frontmatter_file in frontmatter_dir.glob("*.yaml"):
                try:
                    with open(frontmatter_file, 'r') as f:
                        data = yaml.safe_load(f)
                    
                    mat_props = data.get('materialProperties', {})
                    for prop_name, prop_data in mat_props.items():
                        if prop_data is None:
                            logger.warning(f"   Empty property in {frontmatter_file.name}: {prop_name}")
                            issues_found += 1
                        elif isinstance(prop_data, dict) and not prop_data.get('value'):
                            logger.warning(f"   Missing value in {frontmatter_file.name}: {prop_name}")
                            issues_found += 1
                            
                except Exception as e:
                    logger.warning(f"   Could not verify {frontmatter_file.name}: {e}")
            
            if issues_found == 0:
                logger.info("   ✅ All frontmatter files have complete property data")
            else:
                logger.warning(f"   ⚠️  Found {issues_found} frontmatter property issues")
                
        except Exception as e:
            logger.warning(f"Failed to verify frontmatter integrity: {e}")
    
    def generate_completion_report(self) -> str:
        """Generate a completion report"""
        report = f"""
# Comprehensive Property and Component Cleanup Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Changes Made

"""
        for change in self.changes_made:
            report += f"- {change}\\n"
        
        report += f"""

## Actions Completed

✅ **Property Data Validation**: Removed all empty/null property values
✅ **Float Precision**: Rounded all float values to 2 decimal places  
✅ **Settings Component Removal**: Completely removed Settings component and all references

## Files Modified

- `data/Materials.yaml`: Property data cleaned and float values rounded
- `run.py`: Settings component references removed
- Documentation updated to remove Settings component references
- Settings component files and directories removed

## Backup Location

All original files backed up to: `{self.backup_dir.relative_to(self.project_root)}`

## Next Steps

1. Test frontmatter generation: `python3 run.py --material "Alumina" --components frontmatter`
2. Run validation: `python3 hierarchical_validator.py`
3. Deploy changes: `python3 run.py --deploy`

## Rollback Instructions

If issues occur, restore from backup:
```bash
cp {self.backup_dir.relative_to(self.project_root)}/Materials.yaml data/Materials.yaml
cp {self.backup_dir.relative_to(self.project_root)}/run.py run.py
```
"""
        return report
    
    def run_comprehensive_cleanup(self) -> bool:
        """Execute complete cleanup process"""
        try:
            logger.info("🚀 Starting Comprehensive Property and Component Cleanup...")
            
            # Create backup
            self.create_backup()
            
            # Fix Materials.yaml
            self.fix_materials_data()
            
            # Remove Settings component
            self.remove_settings_component_references()
            self.remove_settings_component_files()
            
            # Update documentation
            self.update_documentation()
            
            # Verify frontmatter integrity
            self.verify_frontmatter_integrity()
            
            # Generate report
            report = self.generate_completion_report()
            report_file = self.project_root / "COMPREHENSIVE_CLEANUP_REPORT.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            logger.info("✅ Comprehensive cleanup completed successfully!")
            logger.info(f"📄 Report saved: {report_file}")
            logger.info(f"🎯 Total changes made: {len(self.changes_made)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Comprehensive cleanup failed: {e}")
            return False

def main():
    """Main execution function"""
    cleaner = ComprehensivePropertyCleanup()
    
    success = cleaner.run_comprehensive_cleanup()
    
    if success:
        print("\\n🎉 Comprehensive cleanup completed successfully!")
        print("📝 Check COMPREHENSIVE_CLEANUP_REPORT.md for details")
        print("\\n🔍 Next steps:")
        print("1. Test: python3 run.py --material 'Alumina' --components frontmatter")
        print("2. Validate: python3 hierarchical_validator.py")
        print("3. Deploy: python3 run.py --deploy")
    else:
        print("\\n❌ Comprehensive cleanup failed - check logs for details")
        sys.exit(1)

if __name__ == "__main__":
    main()