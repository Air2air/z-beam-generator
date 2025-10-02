#!/usr/bin/env python3
"""
Integrate Tags into Frontmatter Files

Generates tags from frontmatter data and writes them directly into the frontmatter YAML files.
Uses the TagsComponentGenerator to extract 11 intelligent tags:
- 1 material name
- 1 category
- 3 industries (from applicationTypes)
- 3 processes (from applicationTypes)
- 2 characteristics (from materialProperties)
- 1 author name

Usage:
    python3 scripts/tools/integrate_tags_to_frontmatter.py                    # All materials
    python3 scripts/tools/integrate_tags_to_frontmatter.py --material Copper  # Single material
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.tags.generator import TagsComponentGenerator
from data.materials import load_materials


def load_frontmatter(file_path: Path) -> Optional[Dict]:
    """Load frontmatter YAML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return None


def save_frontmatter_with_tags(file_path: Path, frontmatter_data: Dict, tags: List[str]) -> bool:
    """Save frontmatter with tags field added"""
    try:
        # Add tags to frontmatter data
        frontmatter_data['tags'] = tags
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(frontmatter_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return True
    except Exception as e:
        print(f"❌ Error saving {file_path}: {e}")
        return False


def generate_and_integrate_tags(material_name: str) -> bool:
    """Generate tags and integrate them into frontmatter file"""
    # Find frontmatter file
    material_slug = material_name.lower().replace(' ', '-').replace('_', '-')
    frontmatter_paths = [
        project_root / f"content/components/frontmatter/{material_slug}-laser-cleaning.yaml",
        project_root / f"content/components/frontmatter/{material_slug}.yaml",
    ]
    
    frontmatter_file = None
    for path in frontmatter_paths:
        if path.exists():
            frontmatter_file = path
            break
    
    if not frontmatter_file:
        print(f"⚠️  No frontmatter file found for {material_name}")
        return False
    
    # Load frontmatter
    frontmatter_data = load_frontmatter(frontmatter_file)
    if not frontmatter_data:
        return False
    
    # Check if tags already exist
    if 'tags' in frontmatter_data and frontmatter_data['tags']:
        print(f"ℹ️  Tags already exist for {material_name}, skipping...")
        return True
    
    # Load material data
    materials = load_materials()
    material_data = None
    for mat_name, mat_data in materials.items():
        if mat_name.lower() == material_name.lower():
            material_data = mat_data
            break
    
    if not material_data:
        print(f"⚠️  Material data not found for {material_name}")
        return False
    
    # Generate tags
    try:
        generator = TagsComponentGenerator()
        
        # Create template vars
        template_vars = generator._create_template_vars(
            material_name=material_name,
            material_data=material_data,
            author_info=None,
            frontmatter_data=frontmatter_data,
            schema_fields=None
        )
        
        # Generate tags
        tags = generator._generate_tags_from_frontmatter(
            material_name=material_name,
            material_data=material_data,
            frontmatter_data=frontmatter_data,
            template_vars=template_vars
        )
        
        # Save with tags
        if save_frontmatter_with_tags(frontmatter_file, frontmatter_data, tags):
            print(f"✅ {material_name}: {len(tags)} tags integrated")
            print(f"   Tags: {', '.join(tags[:5])}...")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error generating tags for {material_name}: {e}")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrate tags into frontmatter files")
    parser.add_argument("--material", help="Process single material")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing tags")
    args = parser.parse_args()
    
    print("🏷️  INTEGRATING TAGS INTO FRONTMATTER")
    print("=" * 60)
    
    # Load all materials
    materials = load_materials()
    
    if args.material:
        # Single material
        success = generate_and_integrate_tags(args.material)
        return 0 if success else 1
    else:
        # All materials
        total = len(materials)
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        print(f"📊 Processing {total} materials...")
        print()
        
        for i, material_name in enumerate(materials.keys(), 1):
            print(f"[{i:3d}/{total}] {material_name:<30}", end=" ")
            
            # Check if frontmatter exists
            material_slug = material_name.lower().replace(' ', '-').replace('_', '-')
            frontmatter_file = project_root / f"content/components/frontmatter/{material_slug}-laser-cleaning.yaml"
            
            if not frontmatter_file.exists():
                print("⚠️  No frontmatter")
                skip_count += 1
                continue
            
            # Check if tags exist
            if not args.overwrite:
                frontmatter_data = load_frontmatter(frontmatter_file)
                if frontmatter_data and 'tags' in frontmatter_data and frontmatter_data['tags']:
                    print("ℹ️  Tags exist")
                    skip_count += 1
                    continue
            
            # Generate and integrate
            if generate_and_integrate_tags(material_name):
                success_count += 1
            else:
                fail_count += 1
        
        # Summary
        print()
        print("=" * 60)
        print("🎉 INTEGRATION COMPLETE")
        print(f"✅ Success: {success_count}/{total}")
        print(f"ℹ️  Skipped: {skip_count}/{total}")
        print(f"❌ Failed: {fail_count}/{total}")
        
        return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
