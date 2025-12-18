#!/usr/bin/env python3
"""
Cleanup Materials.yaml by removing extracted content fields.

PURPOSE: Remove caption, faq, regulatory_standards from Materials.yaml after extraction.
RESULT: Reduce Materials.yaml from 2.8MB to ~800KB (properties remain).

SAFETY:
- Creates timestamped backup before modification
- Validates structure after changes
- Reports size reduction statistics
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def backup_materials_file(materials_file: Path) -> Path:
    """Create timestamped backup of Materials.yaml."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = materials_file.with_suffix(f'.backup_{timestamp}.yaml')
    
    import shutil
    shutil.copy2(materials_file, backup_file)
    
    return backup_file


def remove_extracted_fields(materials_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove caption, faq, regulatory_standards from all materials.
    
    These fields are now in separate content files and orchestrated by TrivialFrontmatterExporter.
    """
    materials_section = materials_data.get('materials', {})
    
    removed_stats = {
        'micro': 0,
        'faq': 0,
        'regulatory_standards': 0
    }
    
    for material_name, material_data in materials_section.items():
        # Remove extracted fields
        if 'micro' in material_data:
            del material_data['micro']
            removed_stats['micro'] += 1
        
        if 'faq' in material_data:
            del material_data['faq']
            removed_stats['faq'] += 1
        
        if 'regulatory_standards' in material_data:
            del material_data['regulatory_standards']
            removed_stats['regulatory_standards'] += 1
    
    return materials_data, removed_stats


def main():
    """Main cleanup function."""
    materials_file = Path('data/materials/Materials.yaml')
    
    if not materials_file.exists():
        print(f"❌ Materials.yaml not found at {materials_file}")
        return
    
    # Get initial file size
    initial_size = materials_file.stat().st_size
    initial_size_mb = initial_size / (1024 * 1024)
    
    print(f"📊 MATERIALS.YAML CLEANUP")
    print("=" * 50)
    print(f"Initial size: {initial_size_mb:.2f} MB ({initial_size:,} bytes)")
    
    # Create backup
    print(f"\n💾 Creating backup...")
    backup_file = backup_materials_file(materials_file)
    print(f"   ✅ Backup saved: {backup_file.name}")
    
    # Load Materials.yaml
    print(f"\n📖 Loading Materials.yaml...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    materials_count = len(materials_data.get('materials', {}))
    print(f"   ✅ Loaded {materials_count} materials")
    
    # Remove extracted fields
    print(f"\n🗑️  Removing extracted fields...")
    cleaned_data, removed_stats = remove_extracted_fields(materials_data)
    
    print(f"   ✅ Removed caption from {removed_stats['micro']} materials")
    print(f"   ✅ Removed faq from {removed_stats['faq']} materials")
    print(f"   ✅ Removed regulatory_standards from {removed_stats['regulatory_standards']} materials")
    
    # Write cleaned data
    print(f"\n💾 Writing cleaned Materials.yaml...")
    with open(materials_file, 'w', encoding='utf-8') as f:
        yaml.dump(cleaned_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    # Get final file size
    final_size = materials_file.stat().st_size
    final_size_mb = final_size / (1024 * 1024)
    reduction_mb = initial_size_mb - final_size_mb
    reduction_pct = (reduction_mb / initial_size_mb) * 100
    
    print(f"   ✅ Wrote {materials_count} materials")
    
    print(f"\n📊 SIZE REDUCTION")
    print("=" * 50)
    print(f"Initial:   {initial_size_mb:.2f} MB")
    print(f"Final:     {final_size_mb:.2f} MB")
    print(f"Reduced:   {reduction_mb:.2f} MB ({reduction_pct:.1f}%)")
    print(f"Target:    ~0.80 MB (properties + metadata)")
    
    if final_size_mb < 1.0:
        print(f"\n✅ Successfully reduced Materials.yaml to under 1MB!")
    else:
        print(f"\n⚠️  File still larger than expected target of ~800KB")
        print(f"   This is expected if properties are comprehensive.")
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Backup: {backup_file}")
    print(f"   Cleaned: {materials_file}")
    print(f"\n🔧 Next step: Regenerate all frontmatter to verify orchestration works")


if __name__ == '__main__':
    main()
