#!/usr/bin/env python3
"""
Final Materials Database Verification
Confirms all Materials.yaml issues have been resolved
"""

import yaml
from pathlib import Path

def verify_materials_database():
    """Verify Materials.yaml is now fully correct and complete"""
    materials_path = Path("data/Materials.yaml")
    frontmatter_dir = Path("content/components/frontmatter")
    
    print("🔍 FINAL MATERIALS DATABASE VERIFICATION")
    print("=" * 50)
    
    # Load Materials.yaml
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Valid subcategories per schema
    valid_subcategories = {
        'metal': ['precious', 'ferrous', 'non-ferrous', 'refractory', 'reactive', 'specialty'],
        'stone': ['igneous', 'metamorphic', 'sedimentary', 'architectural', 'composite'],
        'ceramic': ['oxide', 'nitride', 'carbide', 'traditional'],
        'semiconductor': ['intrinsic', 'doped', 'compound'],
        'plastic': ['thermoplastic', 'thermoset', 'engineering', 'biodegradable'],
        'glass': ['borosilicate', 'soda-lime', 'lead', 'specialty-glass'],
        'wood': ['hardwood', 'softwood', 'engineered', 'grass'],
        'composite': ['fiber-reinforced', 'matrix', 'resin', 'elastomeric'],
        'masonry': ['fired', 'concrete', 'natural']
    }
    
    # Check 1: Count materials in index vs frontmatter files
    index_count = len(data.get('material_index', {}))
    frontmatter_files = list(frontmatter_dir.glob("*.md"))
    frontmatter_count = len(frontmatter_files)
    
    print(f"📁 Materials in index: {index_count}")
    print(f"📁 Frontmatter files: {frontmatter_count}")
    
    if index_count == frontmatter_count:
        print("✅ PASS: Index count matches frontmatter files")
    else:
        print("❌ FAIL: Count mismatch")
        return False
    
    # Check 2: Category naming consistency
    categories_found = set()
    for material_name, material_info in data['material_index'].items():
        categories_found.add(material_info.get('category'))
    
    print(f"📂 Categories found: {sorted(categories_found)}")
    if 'polymer' in categories_found:
        print("❌ FAIL: 'polymer' category still exists (should be 'plastic')")
        return False
    else:
        print("✅ PASS: No 'polymer' category found")
    
    # Check 3: Subcategory validity
    invalid_subcategories = []
    for material_name, material_info in data['material_index'].items():
        category = material_info.get('category')
        subcategory = material_info.get('subcategory')
        
        if category in valid_subcategories:
            if subcategory not in valid_subcategories[category]:
                invalid_subcategories.append(f"{material_name}: {category}/{subcategory}")
    
    print(f"🏷️  Invalid subcategories found: {len(invalid_subcategories)}")
    if invalid_subcategories:
        print("❌ FAIL: Invalid subcategories still exist:")
        for item in invalid_subcategories:
            print(f"  - {item}")
        return False
    else:
        print("✅ PASS: All subcategories are valid")
    
    # Check 4: Category ranges coverage
    category_ranges = data.get('category_ranges', {})
    materials_section = data.get('materials', {})
    
    print(f"📊 Category ranges defined: {len(category_ranges)}")
    print(f"📊 Material sections: {len(materials_section)}")
    
    # Check if all categories have ranges and material sections
    missing_ranges = []
    missing_sections = []
    
    for category in categories_found:
        if category not in category_ranges:
            missing_ranges.append(category)
        if category not in materials_section:
            missing_sections.append(category)
    
    if missing_ranges:
        print(f"❌ FAIL: Missing category ranges: {missing_ranges}")
        return False
    else:
        print("✅ PASS: All categories have ranges")
    
    if missing_sections:
        print(f"❌ FAIL: Missing material sections: {missing_sections}")
        return False
    else:
        print("✅ PASS: All categories have material sections")
    
    print()
    print("=" * 50)
    print("🎉 VERIFICATION COMPLETE: All checks passed!")
    print("📋 Materials database is now fully compliant")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = verify_materials_database()
    exit(0 if success else 1)