#!/usr/bin/env python3
"""
Migrate Qualitative Properties from materialProperties to materialCharacteristics

Scans Materials.yaml and Categories.yaml for qualitative properties that should
be moved to materialCharacteristics structure.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.frontmatter.qualitative_properties import (
    is_qualitative_property,
    get_property_definition,
    QUALITATIVE_PROPERTIES,
    MATERIAL_CHARACTERISTICS_CATEGORIES
)


class QualitativePropertyMigrator:
    """Migrates qualitative properties to materialCharacteristics structure"""
    
    def __init__(self, materials_path: str, categories_path: str):
        self.materials_path = Path(materials_path)
        self.categories_path = Path(categories_path)
        self.migration_report = {
            'materials_migrated': [],
            'properties_migrated': set(),
            'categories_affected': set()
        }
    
    def load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def save_yaml(self, path: Path, data: Dict[str, Any], backup: bool = True):
        """Save YAML file with optional backup"""
        if backup:
            backup_path = path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
            path.rename(backup_path)
            print(f"📦 Backup created: {backup_path}")
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def find_qualitative_properties(self, properties: Dict[str, Any]) -> Set[str]:
        """Find qualitative properties in a properties dict"""
        qualitative_props = set()
        
        if not properties or not isinstance(properties, dict):
            return qualitative_props
        
        for prop_name in properties.keys():
            if is_qualitative_property(prop_name):
                qualitative_props.add(prop_name)
        
        return qualitative_props
    
    def migrate_material_properties(self, material_data: Dict[str, Any]) -> bool:
        """Migrate qualitative properties for a single material"""
        if not isinstance(material_data, dict) or 'properties' not in material_data:
            return False
        
        material_props = material_data['properties']
        if not isinstance(material_props, dict):
            return False
        
        qualitative_props = self.find_qualitative_properties(material_props)
        
        if not qualitative_props:
            return False
        
        # Initialize materialCharacteristics if not present
        if 'materialCharacteristics' not in material_data:
            material_data['materialCharacteristics'] = {}
        
        # Migrate each qualitative property
        for prop_name in qualitative_props:
            prop_def = get_property_definition(prop_name)
            if not prop_def:
                print(f"⚠️  No definition found for {prop_name}, skipping")
                continue
            
            # Get the property data
            prop_data = material_props[prop_name]
            
            # Ensure category exists in materialCharacteristics
            category = prop_def.category
            if category not in material_data['materialCharacteristics']:
                cat_info = MATERIAL_CHARACTERISTICS_CATEGORIES.get(category, {})
                material_data['materialCharacteristics'][category] = {
                    'label': cat_info.get('label', category.replace('_', ' ').title()),
                    'description': cat_info.get('description', f'{category} properties'),
                    'properties': {}
                }
            
            # Move property to materialCharacteristics
            if isinstance(prop_data, dict):
                # Property has value, confidence, etc.
                material_data['materialCharacteristics'][category]['properties'][prop_name] = prop_data
            else:
                # Simple value - wrap in structure
                material_data['materialCharacteristics'][category]['properties'][prop_name] = {
                    'value': prop_data,
                    'unit': prop_def.unit,
                    'confidence': 0.7,
                    'description': prop_def.description,
                    'allowedValues': prop_def.allowed_values
                }
            
            # Remove from materialProperties (which is 'properties' in Materials.yaml)
            del material_props[prop_name]
            
            self.migration_report['properties_migrated'].add(prop_name)
            print(f"  ✅ Migrated {prop_name} → materialCharacteristics.{category}")
        
        return True
    
    def migrate_materials(self) -> int:
        """Migrate all materials in Materials.yaml"""
        print("\n🔍 Scanning Materials.yaml for qualitative properties...")
        
        materials_data = self.load_yaml(self.materials_path)
        
        # Materials are nested under 'materials' key
        if 'materials' not in materials_data:
            print("❌ No 'materials' key found in Materials.yaml")
            return 0
        
        materials = materials_data['materials']
        materials_count = 0
        
        for material_name, material_data in materials.items():
            if self.migrate_material_properties(material_data):
                materials_count += 1
                self.migration_report['materials_migrated'].append(material_name)
                print(f"✨ Migrated properties for: {material_name}")
        
        if materials_count > 0:
            self.save_yaml(self.materials_path, materials_data)
            print(f"\n💾 Saved updated Materials.yaml ({materials_count} materials migrated)")
        else:
            print("\n✅ No qualitative properties found in materialProperties")
        
        return materials_count
    
    def check_categories(self) -> List[str]:
        """Check Categories.yaml for qualitative properties in ranges"""
        print("\n🔍 Checking Categories.yaml for qualitative properties...")
        
        categories_data = self.load_yaml(self.categories_path)
        qualitative_in_categories = []
        
        for category_name, category_data in categories_data.items():
            if 'ranges' not in category_data:
                continue
            
            ranges = category_data['ranges']
            qualitative_props = self.find_qualitative_properties(ranges)
            
            if qualitative_props:
                qualitative_in_categories.append({
                    'category': category_name,
                    'properties': list(qualitative_props)
                })
                self.migration_report['categories_affected'].add(category_name)
                print(f"⚠️  Category '{category_name}' has qualitative properties in ranges:")
                for prop in qualitative_props:
                    print(f"     - {prop} (should be material-specific, not category-level)")
        
        return qualitative_in_categories
    
    def generate_report(self) -> str:
        """Generate migration report"""
        report = [
            "\n" + "="*60,
            "QUALITATIVE PROPERTIES MIGRATION REPORT",
            "="*60,
            f"\n📊 Materials Migrated: {len(self.migration_report['materials_migrated'])}",
        ]
        
        if self.migration_report['materials_migrated']:
            report.append("\nMaterials updated:")
            for material in self.migration_report['materials_migrated']:
                report.append(f"  • {material}")
        
        report.append(f"\n📋 Properties Migrated: {len(self.migration_report['properties_migrated'])}")
        if self.migration_report['properties_migrated']:
            report.append("\nProperties moved to materialCharacteristics:")
            for prop in sorted(self.migration_report['properties_migrated']):
                prop_def = get_property_definition(prop)
                category = prop_def.category if prop_def else 'unknown'
                report.append(f"  • {prop} → {category}")
        
        if self.migration_report['categories_affected']:
            report.append(f"\n⚠️  Categories with Qualitative Properties: {len(self.migration_report['categories_affected'])}")
            report.append("\nThese should be reviewed (qualitative props are material-specific):")
            for category in sorted(self.migration_report['categories_affected']):
                report.append(f"  • {category}")
        
        report.append("\n" + "="*60 + "\n")
        return "\n".join(report)


def main():
    """Main migration execution"""
    print("🚀 Starting Qualitative Properties Migration")
    print("="*60)
    
    # Paths
    materials_path = project_root / 'data' / 'Materials.yaml'
    categories_path = project_root / 'data' / 'Categories.yaml'
    
    # Verify files exist
    if not materials_path.exists():
        print(f"❌ Materials.yaml not found at {materials_path}")
        return 1
    
    if not categories_path.exists():
        print(f"❌ Categories.yaml not found at {categories_path}")
        return 1
    
    # Create migrator
    migrator = QualitativePropertyMigrator(
        str(materials_path),
        str(categories_path)
    )
    
    # Migrate materials
    materials_count = migrator.migrate_materials()
    
    # Check categories
    category_issues = migrator.check_categories()
    
    # Generate report
    report = migrator.generate_report()
    print(report)
    
    # Save report
    report_path = project_root / 'QUALITATIVE_MIGRATION_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(f"# Qualitative Properties Migration Report\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(report)
        f.write("\n## Qualitative Properties Defined\n\n")
        for prop_name, prop_def in QUALITATIVE_PROPERTIES.items():
            f.write(f"- **{prop_name}** ({prop_def.category}): {prop_def.description}\n")
            f.write(f"  - Allowed values: {', '.join(prop_def.allowed_values)}\n")
    
    print(f"📄 Full report saved to: {report_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
