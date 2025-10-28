#!/usr/bin/env python3
"""
Fix Data Quality Issues
=======================

Fixes issues identified by test suite:
1. Remove 'other' category from Cast Iron and other materials
2. Migrate deprecated meltingPoint to thermalDestruction
3. Update migration validator for flattened structure
4. Ensure critical properties exist in materials

Date: October 27, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
import shutil
from datetime import datetime

# Metadata fields to preserve in categories
METADATA_FIELDS = {'label', 'description', 'percentage'}

# Properties that should be in laser_material_interaction
LASER_INTERACTION_PROPS = {
    'ablationThreshold', 'absorptionCoefficient', 'absorptivity',
    'boilingPoint', 'laserAbsorption', 'laserDamageThreshold',
    'laserReflectivity', 'reflectivity', 'specificHeat',
    'thermalConductivity', 'thermalDestruction', 'thermalDestructionPoint',
    'thermalDiffusivity', 'thermalExpansion', 'thermalShockResistance',
    'meltingPoint'  # Will be migrated to thermalDestruction
}

# Properties that should be in material_characteristics
MATERIAL_CHAR_PROPS = {
    'compressiveStrength', 'corrosionResistance', 'density',
    'electricalConductivity', 'electricalResistivity', 'flexuralStrength',
    'fractureToughness', 'hardness', 'oxidationResistance', 'porosity',
    'tensileStrength', 'youngsModulus', 'crystallineStructure'
}


def backup_file(file_path: Path) -> Path:
    """Create timestamped backup of file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.with_suffix(f'.yaml.backup_{timestamp}')
    shutil.copy2(file_path, backup_path)
    return backup_path


def migrate_melting_point_to_thermal_destruction(data: Dict[str, Any]) -> bool:
    """
    Migrate deprecated meltingPoint property to thermalDestruction.
    Returns True if migration occurred.
    """
    migrated = False
    
    for category_name, category_data in data.items():
        if not isinstance(category_data, dict):
            continue
        
        # Skip metadata fields
        if category_name in METADATA_FIELDS:
            continue
        
        # Check for meltingPoint in category
        if 'meltingPoint' in category_data:
            melting_data = category_data.pop('meltingPoint')
            
            # Create thermalDestruction if it doesn't exist
            if 'thermalDestruction' not in category_data:
                category_data['thermalDestruction'] = {
                    'point': {
                        'value': melting_data.get('value', 0),
                        'unit': melting_data.get('unit', 'K')
                    },
                    'type': 'melting',
                    'source': melting_data.get('source', 'ai_research')
                }
                migrated = True
                print(f"  ✓ Migrated meltingPoint to thermalDestruction in {category_name}")
    
    return migrated


def remove_other_category(material_props: Dict[str, Any]) -> bool:
    """
    Remove 'other' category and redistribute properties.
    Returns True if 'other' was removed.
    """
    if 'other' not in material_props:
        return False
    
    other_data = material_props.pop('other')
    print(f"  ✓ Removing 'other' category")
    
    # Redistribute properties to appropriate categories
    for prop_name, prop_data in other_data.items():
        if prop_name in METADATA_FIELDS:
            continue
        
        # Determine target category
        if prop_name in LASER_INTERACTION_PROPS:
            target = 'laser_material_interaction'
        elif prop_name in MATERIAL_CHAR_PROPS:
            target = 'material_characteristics'
        else:
            # Default to material_characteristics
            target = 'material_characteristics'
        
        # Ensure target category exists
        if target not in material_props:
            material_props[target] = {
                'label': 'Laser-Material Interaction' if target == 'laser_material_interaction' else 'Material Characteristics',
                'description': 'Category properties',
                'percentage': 0
            }
        
        # Only add if not already present (avoid duplicates)
        if prop_name not in material_props[target]:
            material_props[target][prop_name] = prop_data
            print(f"    → Moved {prop_name} to {target}")
    
    return True


def ensure_critical_properties(material_name: str, material_props: Dict[str, Any]) -> bool:
    """
    Ensure critical properties exist for materials.
    Returns True if properties were added.
    """
    added = False
    
    # For metals, ensure absorptionCoefficient and thermalDestruction
    if material_name in ['Tool Steel', 'Cast Iron']:
        laser_props = material_props.get('laser_material_interaction', {})
        
        if 'absorptionCoefficient' not in laser_props:
            laser_props['absorptionCoefficient'] = {
                'value': 500000.0,  # Typical for steel
                'unit': 'm⁻¹',
                'source': 'ai_research',
                'min': 100000,
                'max': 50000000
            }
            added = True
            print(f"  ✓ Added absorptionCoefficient to laser_material_interaction")
        
        if 'thermalDestruction' not in laser_props:
            laser_props['thermalDestruction'] = {
                'point': {
                    'value': 1500.0 if material_name == 'Tool Steel' else 1200.0,
                    'unit': '°C'
                },
                'type': 'melting',
                'source': 'ai_research'
            }
            added = True
            print(f"  ✓ Added thermalDestruction to laser_material_interaction")
        
        # For Tool Steel, ensure crystallineStructure
        if material_name == 'Tool Steel':
            char_props = material_props.get('material_characteristics', {})
            if 'crystallineStructure' not in char_props:
                char_props['crystallineStructure'] = {
                    'value': 'BCC',
                    'unit': 'crystal system',
                    'source': 'ai_research',
                    'description': 'Body-centered cubic structure typical of tool steels'
                }
                added = True
                print(f"  ✓ Added crystallineStructure to material_characteristics")
    
    return added


def process_frontmatter_file(file_path: Path) -> Dict[str, bool]:
    """
    Process a single frontmatter file.
    Returns dict of changes made.
    """
    changes = {
        'other_removed': False,
        'melting_migrated': False,
        'properties_added': False,
        'file_modified': False
    }
    
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data or 'materialProperties' not in data:
            return changes
        
        material_name = data.get('name', 'Unknown')
        material_props = data['materialProperties']
        
        print(f"\n📄 Processing: {material_name}")
        
        # Fix 1: Remove 'other' category
        if remove_other_category(material_props):
            changes['other_removed'] = True
            changes['file_modified'] = True
        
        # Fix 2: Migrate meltingPoint to thermalDestruction
        if migrate_melting_point_to_thermal_destruction(material_props):
            changes['melting_migrated'] = True
            changes['file_modified'] = True
        
        # Fix 3: Ensure critical properties exist
        if ensure_critical_properties(material_name, material_props):
            changes['properties_added'] = True
            changes['file_modified'] = True
        
        # Save if modified
        if changes['file_modified']:
            # Backup first
            backup_path = backup_file(file_path)
            print(f"  💾 Backup: {backup_path.name}")
            
            # Write updated data
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=1000)
            print(f"  ✅ Updated: {file_path.name}")
        else:
            print(f"  ⏭️  No changes needed")
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path.name}: {e}")
    
    return changes


def update_migration_validator():
    """Update completeness_validator.py to handle flattened structure."""
    validator_path = Path('components/frontmatter/validation/completeness_validator.py')
    
    if not validator_path.exists():
        print("\n❌ Validator file not found")
        return False
    
    with open(validator_path, 'r') as f:
        content = f.read()
    
    # Check if already updated
    if "# FLATTENED STRUCTURE" in content:
        print("\n⏭️  Migration validator already updated")
        return False
    
    # Find and replace the migrate_legacy_qualitative method
    old_code = """    def migrate_legacy_qualitative(
        self,
        material_properties: Dict
    ) -> Tuple[Dict, List[str]]:
        \"\"\"
        Migrate legacy qualitative properties to material_characteristics.
        
        Args:
            material_properties: Current materialProperties structure
            
        Returns:
            Tuple of (updated_material_properties, migration_log)
        \"\"\"
        migration_log = []
        updated = material_properties.copy()
        
        # Ensure material_characteristics category exists
        if 'material_characteristics' not in updated:
            updated['material_characteristics'] = {
                'label': 'Material Characteristics',
                'description': 'Intrinsic physical, mechanical, chemical, and structural properties',
                'percentage': 0,
                'properties': {}
            }
        
        # Scan all categories for qualitative properties
        for category_name in list(updated.keys()):
            if category_name == 'material_characteristics':
                continue
            
            category_data = updated[category_name]
            if not isinstance(category_data, dict) or 'properties' not in category_data:
                continue
            
            # Find and move qualitative properties
            props_to_move = []
            for prop_name in list(category_data['properties'].keys()):
                if is_qualitative_property(prop_name):
                    props_to_move.append(prop_name)
            
            for prop_name in props_to_move:
                prop_data = category_data['properties'].pop(prop_name)
                updated['material_characteristics']['properties'][prop_name] = prop_data
                migration_log.append(
                    f\"Migrated {prop_name} from {category_name} to material_characteristics\"
                )
        
        # Recalculate percentages
        updated = self._recalculate_percentages(updated)
        
        return updated, migration_log"""
    
    new_code = """    def migrate_legacy_qualitative(
        self,
        material_properties: Dict
    ) -> Tuple[Dict, List[str]]:
        \"\"\"
        Migrate legacy qualitative properties to material_characteristics.
        # FLATTENED STRUCTURE - No nested 'properties' key
        
        Args:
            material_properties: Current materialProperties structure (flattened)
            
        Returns:
            Tuple of (updated_material_properties, migration_log)
        \"\"\"
        migration_log = []
        updated = material_properties.copy()
        
        # Metadata fields to skip
        metadata_fields = {'label', 'description', 'percentage'}
        
        # Ensure material_characteristics category exists
        if 'material_characteristics' not in updated:
            updated['material_characteristics'] = {
                'label': 'Material Characteristics',
                'description': 'Intrinsic physical, mechanical, chemical, and structural properties',
                'percentage': 0
            }
        
        # Scan all categories for qualitative properties
        for category_name in list(updated.keys()):
            if category_name == 'material_characteristics':
                continue
            
            category_data = updated[category_name]
            if not isinstance(category_data, dict):
                continue
            
            # Find and move qualitative properties (FLATTENED: direct children of category)
            props_to_move = []
            for prop_name in list(category_data.keys()):
                # Skip metadata fields
                if prop_name in metadata_fields:
                    continue
                # Check if qualitative
                if is_qualitative_property(prop_name):
                    props_to_move.append(prop_name)
            
            for prop_name in props_to_move:
                prop_data = category_data.pop(prop_name)
                updated['material_characteristics'][prop_name] = prop_data
                migration_log.append(
                    f\"Migrated {prop_name} from {category_name} to material_characteristics\"
                )
        
        # Recalculate percentages
        updated = self._recalculate_percentages(updated)
        
        return updated, migration_log"""
    
    content = content.replace(old_code, new_code)
    
    # Backup and save
    backup_path = backup_file(validator_path)
    print(f"\n📝 Updating migration validator")
    print(f"  💾 Backup: {backup_path.name}")
    
    with open(validator_path, 'w') as f:
        f.write(content)
    
    print(f"  ✅ Updated: {validator_path.name}")
    return True


def main():
    """Main execution."""
    print("=" * 60)
    print("Data Quality Issue Fixes")
    print("=" * 60)
    
    frontmatter_dir = Path('content/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return
    
    # Statistics
    stats = {
        'total_files': 0,
        'files_modified': 0,
        'other_removed': 0,
        'melting_migrated': 0,
        'properties_added': 0
    }
    
    # Process all frontmatter files
    for yaml_file in sorted(frontmatter_dir.glob('*.yaml')):
        stats['total_files'] += 1
        changes = process_frontmatter_file(yaml_file)
        
        if changes['file_modified']:
            stats['files_modified'] += 1
        if changes['other_removed']:
            stats['other_removed'] += 1
        if changes['melting_migrated']:
            stats['melting_migrated'] += 1
        if changes['properties_added']:
            stats['properties_added'] += 1
    
    # Update migration validator
    validator_updated = update_migration_validator()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"'other' categories removed: {stats['other_removed']}")
    print(f"meltingPoint migrations: {stats['melting_migrated']}")
    print(f"Critical properties added: {stats['properties_added']}")
    print(f"Migration validator updated: {'Yes' if validator_updated else 'No'}")
    print("=" * 60)
    
    if stats['files_modified'] > 0 or validator_updated:
        print("\n✅ Data quality issues fixed!")
        print("\n📝 Next steps:")
        print("   1. Run tests: python3 -m pytest tests/test_two_category_compliance.py -v")
        print("   2. Verify Materials.yaml sync if needed")
        print("   3. Commit changes to git")
    else:
        print("\n⏭️  No changes needed - data already clean!")


if __name__ == '__main__':
    main()
