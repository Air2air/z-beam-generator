#!/usr/bin/env python3
"""
Bulk Post-Processing Script for All Z-Beam Components

This script finds all existing component files and applies post-processing and validation to each one.
"""

import os
from pathlib import Path
from validators.centralized_validator import CentralizedValidator

def find_all_component_files():
    """Find all component files in the content directory."""
    content_dir = Path("content/components")
    if not content_dir.exists():
        print("❌ Content directory not found")
        return []
    
    files = []
    component_types = ["frontmatter", "caption", "content", "bullets", "table", "jsonld", "metatags", "tags", "propertiestable"]
    
    for component_type in component_types:
        component_dir = content_dir / component_type
        if component_dir.exists():
            for file_path in component_dir.glob("*.md"):
                files.append((str(file_path), component_type))
    
    return files

def extract_material_name(file_path):
    """Extract material name from file path."""
    filename = Path(file_path).stem
    # Remove "-laser-cleaning" suffix and convert to title case
    material_name = filename.replace("-laser-cleaning", "").replace("-", " ").title()
    return material_name

def main():
    print("🔧 BULK POST-PROCESSING ALL Z-BEAM COMPONENTS")
    print("=" * 60)
    
    validator = CentralizedValidator()
    
    # Find all files
    files = find_all_component_files()
    print(f"\n📁 Found {len(files)} component files to process")
    
    if not files:
        print("No files found to process")
        return
    
    # Group by material for better reporting
    materials = {}
    for file_path, component_type in files:
        material_name = extract_material_name(file_path)
        if material_name not in materials:
            materials[material_name] = []
        materials[material_name].append((file_path, component_type))
    
    print(f"📊 Processing {len(materials)} materials with components")
    print()
    
    total_processed = 0
    total_improved = 0
    
    # Process each material
    for material_name, material_files in materials.items():
        print(f"🎯 PROCESSING: {material_name}")
        print(f"   Components: {len(material_files)}")
        
        material_improved = 0
        
        for file_path, component_type in material_files:
            try:
                # Apply post-processing
                post_processed = validator.post_process_generated_content(file_path, component_type)
                
                # Apply validation and fixes
                validation_success = validator.validate_and_fix_component_immediately(
                    material_name, component_type, max_retries=1, force_fix=True
                )
                
                if post_processed or validation_success:
                    material_improved += 1
                    print(f"   ✅ {component_type}: Processed")
                else:
                    print(f"   ⚪ {component_type}: No changes needed")
                
                total_processed += 1
                
            except Exception as e:
                print(f"   ❌ {component_type}: Error - {e}")
        
        if material_improved > 0:
            total_improved += material_improved
            print(f"   📈 Improved {material_improved}/{len(material_files)} components")
        else:
            print(f"   ✅ All components already clean")
        print()
    
    # Final summary
    print("🎯 BULK PROCESSING COMPLETE")
    print("=" * 40)
    print(f"📊 Total files processed: {total_processed}")
    print(f"✅ Files improved: {total_improved}")
    print(f"📈 Success rate: {(total_processed - total_improved + total_improved) / total_processed * 100:.1f}%")
    
    if total_improved > 0:
        print(f"\n🔧 {total_improved} files were cleaned and validated")
    else:
        print(f"\n✅ All files were already clean and valid")

if __name__ == "__main__":
    main()
