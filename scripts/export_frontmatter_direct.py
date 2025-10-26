#!/usr/bin/env python3
"""
Direct Materials.yaml to Frontmatter Export

Simple converter that exports 100% complete Materials.yaml data directly to 
frontmatter files without API calls or complex generator system.

For use when data is complete and no AI generation is needed.
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def load_materials_data() -> Dict:
    """Load Materials.yaml data"""
    materials_file = Path("data/Materials.yaml")
    if not materials_file.exists():
        raise FileNotFoundError("Materials.yaml not found")
    
    with open(materials_file, 'r') as f:
        return yaml.safe_load(f)

def load_categories_data() -> Dict:
    """Load Categories.yaml data"""
    categories_file = Path("data/Categories.yaml")
    if not categories_file.exists():
        raise FileNotFoundError("Categories.yaml not found")
    
    with open(categories_file, 'r') as f:
        return yaml.safe_load(f)

def create_frontmatter_content(material_name: str, material_data: Dict, categories_data: Dict) -> Dict:
    """Create frontmatter content from material data"""
    
    # Basic material info
    category = material_data.get('category', 'unknown')
    properties = material_data.get('properties', {})
    
    # Build frontmatter structure
    frontmatter = {
        'name': material_name,  # Required by validation
        'material': material_name,  # Backward compatibility
        'title': material_data.get('title', f"{material_name} Laser Cleaning"),  # Required by validation
        'category': category,
        'generated_date': datetime.now().isoformat(),
        'data_completeness': '100%',
        'source': 'Materials.yaml (direct export)',
        
        # Properties section
        'properties': {}
    }
    
    # Add all properties from Materials.yaml
    for prop_name, prop_data in properties.items():
        if isinstance(prop_data, dict):
            # Handle nested properties (like thermalDestruction.point)
            if 'point' in prop_data:
                # Nested structure
                point_data = prop_data['point']
                frontmatter['properties'][prop_name] = {
                    'value': point_data.get('value'),
                    'unit': point_data.get('unit'),
                    'confidence': point_data.get('confidence', 95),
                    'source': point_data.get('source', 'ai_research')
                }
                # Add additional metadata if present
                for key in ['research_date', 'description']:
                    if key in point_data:
                        frontmatter['properties'][prop_name][key] = point_data[key]
            else:
                # Flat structure
                frontmatter['properties'][prop_name] = {
                    'value': prop_data.get('value'),
                    'unit': prop_data.get('unit'),
                    'confidence': prop_data.get('confidence', 95),
                    'source': prop_data.get('source', 'ai_research')
                }
                # Add additional metadata if present
                for key in ['research_date', 'description']:
                    if key in prop_data:
                        frontmatter['properties'][prop_name][key] = prop_data[key]
        else:
            # Simple value
            frontmatter['properties'][prop_name] = {
                'value': prop_data,
                'confidence': 95,
                'source': 'materials_yaml'
            }
    
    # Add category information
    if category in categories_data.get('categories', {}):
        cat_data = categories_data['categories'][category]
        frontmatter['category_info'] = {
            'description': cat_data.get('description', f'{category.title()} material'),
            'properties_count': len(properties),
            'category_ranges': cat_data.get('category_ranges', {})
        }
    
    # Add caption data if present
    if 'caption' in material_data:
        caption_data = material_data['caption']
        frontmatter['caption'] = {
            'description': caption_data.get('description', f'Microscopic analysis of {material_name} surface before and after laser cleaning treatment'),
            'beforeText': caption_data.get('beforeText', ''),
            'afterText': caption_data.get('afterText', '')
        }
    
    # Add author data if present
    if 'author' in material_data:
        frontmatter['author'] = material_data['author']
    
    return frontmatter

def export_material_frontmatter(material_name: str, material_data: Dict, categories_data: Dict, output_dir: Path):
    """Export single material to frontmatter file"""
    
    # Create frontmatter content
    frontmatter_content = create_frontmatter_content(material_name, material_data, categories_data)
    
    # Create output file path with required -laser-cleaning suffix
    safe_name = material_name.lower().replace(' ', '-').replace('/', '-')
    output_file = output_dir / f"{safe_name}-laser-cleaning.yaml"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write frontmatter file
    with open(output_file, 'w') as f:
        yaml.dump(frontmatter_content, f, default_flow_style=False, sort_keys=False, indent=2)
    
    return output_file

def export_all_materials(output_dir: str = "content/frontmatter"):
    """Export all materials to frontmatter files"""
    
    print("🚀 Direct Materials.yaml → Frontmatter Export")
    print("=" * 60)
    
    # Load data
    print("📂 Loading data files...")
    materials_data = load_materials_data()
    categories_data = load_categories_data()
    
    materials = materials_data.get('materials', {})
    print(f"✅ Loaded {len(materials)} materials from Materials.yaml")
    print(f"✅ Loaded {len(categories_data.get('categories', {}))} categories from Categories.yaml")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Export each material
    print(f"\n📝 Exporting to {output_path}/")
    exported_count = 0
    
    for material_name, material_data in materials.items():
        try:
            output_file = export_material_frontmatter(
                material_name, material_data, categories_data, output_path
            )
            print(f"  ✅ {material_name} → {output_file.name}")
            exported_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to export {material_name}: {e}")
    
    print(f"\n🎉 Export complete!")
    print(f"   📊 {exported_count}/{len(materials)} materials exported")
    print(f"   📁 Files saved to: {output_path.absolute()}")
    
    return exported_count

def export_single_material(material_name: str, output_dir: str = "content/frontmatter"):
    """Export single material to frontmatter file"""
    
    print(f"🚀 Exporting {material_name} to frontmatter")
    
    # Load data
    materials_data = load_materials_data()
    categories_data = load_categories_data()
    
    materials = materials_data.get('materials', {})
    
    if material_name not in materials:
        print(f"❌ Material '{material_name}' not found in Materials.yaml")
        available = list(materials.keys())[:5]
        print(f"Available materials: {', '.join(available)}...")
        return False
    
    material_data = materials[material_name]
    output_path = Path(output_dir)
    
    try:
        output_file = export_material_frontmatter(
            material_name, material_data, categories_data, output_path
        )
        print(f"✅ Exported {material_name} → {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to export {material_name}: {e}")
        return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Export specific material
        material_name = sys.argv[1]
        success = export_single_material(material_name)
        sys.exit(0 if success else 1)
    else:
        # Export all materials
        exported = export_all_materials()
        sys.exit(0 if exported > 0 else 1)