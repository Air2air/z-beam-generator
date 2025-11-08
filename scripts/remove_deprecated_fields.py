#!/usr/bin/env python3
"""
Remove deprecated fields: environmentalImpact and outcomeMetrics

These fields were marked as removed on Nov 2, 2025 but still exist in:
1. Materials.yaml (all 132 materials)
2. materials/schema.py (dataclass fields, to_dict, from_dict)
3. Comments and documentation references

This script:
1. Removes fields from Materials.yaml
2. Updates materials/schema.py to remove field definitions
3. Reports on removal success
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MATERIALS_FILE = PROJECT_ROOT / "materials" / "data" / "Materials.yaml"
SCHEMA_FILE = PROJECT_ROOT / "materials" / "schema.py"

DEPRECATED_FIELDS = ['environmentalImpact', 'outcomeMetrics']


def remove_from_materials_yaml():
    """Remove deprecated fields from Materials.yaml"""
    print("=" * 70)
    print("STEP 1: Remove from Materials.yaml")
    print("=" * 70)
    
    if not MATERIALS_FILE.exists():
        print(f"❌ Materials.yaml not found: {MATERIALS_FILE}")
        return False
    
    # Create backup
    backup_path = MATERIALS_FILE.parent / f"Materials.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    print(f"📦 Creating backup: {backup_path.name}")
    
    with open(MATERIALS_FILE, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Load YAML
    print(f"📖 Loading Materials.yaml...")
    with open(MATERIALS_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"✅ Loaded {len(materials)} materials")
    
    # Remove fields from each material
    removed_count = 0
    materials_affected = []
    
    for material_name, material_data in materials.items():
        had_fields = False
        
        for field in DEPRECATED_FIELDS:
            if field in material_data:
                del material_data[field]
                had_fields = True
        
        if had_fields:
            removed_count += 1
            materials_affected.append(material_name)
    
    print(f"\n📊 Removal Summary:")
    print(f"   Materials affected: {removed_count}")
    print(f"   Fields removed: {', '.join(DEPRECATED_FIELDS)}")
    
    if removed_count == 0:
        print("✨ No deprecated fields found in Materials.yaml")
        return True
    
    # Save updated YAML
    print(f"\n💾 Saving updated Materials.yaml...")
    with open(MATERIALS_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Materials.yaml updated successfully")
    print(f"   Backup saved: {backup_path}")
    
    return True


def update_schema_file():
    """Remove deprecated fields from materials/schema.py"""
    print("\n" + "=" * 70)
    print("STEP 2: Update materials/schema.py")
    print("=" * 70)
    
    if not SCHEMA_FILE.exists():
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        return False
    
    # Read current schema
    with open(SCHEMA_FILE, 'r') as f:
        lines = f.readlines()
    
    # Create backup
    backup_path = SCHEMA_FILE.parent / f"schema.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    print(f"📦 Creating backup: {backup_path.name}")
    
    with open(backup_path, 'w') as f:
        f.writelines(lines)
    
    print("🔍 Scanning for deprecated field references...")
    
    # Track lines to remove
    lines_to_remove = []
    
    for i, line in enumerate(lines):
        # Check for field definitions
        if any(field in line for field in DEPRECATED_FIELDS):
            # Skip comment-only lines
            stripped = line.strip()
            if not stripped.startswith('#'):
                lines_to_remove.append((i + 1, line.strip()))
    
    if not lines_to_remove:
        print("✨ No deprecated field references found in schema.py")
        return True
    
    print(f"\n📊 Found {len(lines_to_remove)} lines to review:")
    for line_num, line_content in lines_to_remove:
        print(f"   Line {line_num}: {line_content[:80]}")
    
    print("\n⚠️  Manual review required for schema.py")
    print("   The following field references should be removed:")
    print("   1. Field definitions in MaterialContent dataclass")
    print("   2. References in to_dict() method")
    print("   3. References in from_dict() method")
    print("   4. FieldResearchSpec entries")
    
    return True


def main():
    """Main execution"""
    print("\n🗑️  DEPRECATED FIELDS REMOVAL")
    print(f"Removing: {', '.join(DEPRECATED_FIELDS)}")
    print()
    
    # Step 1: Remove from Materials.yaml
    if not remove_from_materials_yaml():
        print("\n❌ Failed to update Materials.yaml")
        sys.exit(1)
    
    # Step 2: Update schema file
    if not update_schema_file():
        print("\n❌ Failed to analyze schema.py")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✅ REMOVAL COMPLETE")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print("   1. Manually review and update materials/schema.py")
    print("   2. Remove field definitions from MaterialContent dataclass")
    print("   3. Remove references in to_dict() and from_dict() methods")
    print("   4. Test with: python3 -m pytest tests/")
    print()


if __name__ == "__main__":
    main()
