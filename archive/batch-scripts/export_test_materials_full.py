#!/usr/bin/env python3
"""
Export Steel, Aluminum, and Bronze from Materials.yaml to frontmatter with ALL fields.
Includes FAQ conversion and category ranges.
"""

import yaml
from pathlib import Path
from datetime import datetime

def get_category_ranges(categories_data: dict) -> dict:
    """Extract universal min/max ranges from Categories.yaml machineSettingsRanges."""
    # Use the universal machineSettingsRanges that apply to all materials
    if 'machineSettingsRanges' in categories_data:
        return categories_data['machineSettingsRanges']
    
    return {}

def export_material_to_frontmatter(material_name: str, material_data: dict, category_ranges: dict = None):
    """Export a single material with all fields from Materials.yaml to frontmatter."""
    
    # Map material name to frontmatter filename
    frontmatter_path = Path(f"content/frontmatter/{material_name.lower()}-laser-cleaning.yaml")
    
    # Build complete frontmatter structure with ALL fields
    frontmatter = {
        "layout": "material",
        "title": material_data.get("title", f"{material_name} Laser Cleaning"),
        "material": material_name,
    }
    
    # Add subtitle if available
    if "subtitle" in material_data:
        subtitle_data = material_data["subtitle"]
        if isinstance(subtitle_data, dict):
            frontmatter["subtitle"] = subtitle_data.get("text", "")
        else:
            frontmatter["subtitle"] = subtitle_data
    
    # Add description
    if "description" in material_data:
        frontmatter["description"] = material_data["description"]
    
    # Add category
    if "category" in material_data:
        frontmatter["category"] = material_data["category"]
    
    # Add subcategory if available
    if "subcategory" in material_data:
        frontmatter["subcategory"] = material_data["subcategory"]
    
    # Add author information
    if "author" in material_data:
        frontmatter["author"] = material_data["author"]
    
    # Add applications
    if "applications" in material_data:
        frontmatter["applications"] = material_data["applications"]
    
    # Add images
    if "images" in material_data:
        frontmatter["images"] = material_data["images"]
    
    # Add caption (before/after text)
    if "caption" in material_data:
        frontmatter["caption"] = material_data["caption"]
    
    # Add properties
    if "properties" in material_data:
        frontmatter["properties"] = material_data["properties"]
    
    # Add materialProperties
    if "materialProperties" in material_data:
        frontmatter["materialProperties"] = material_data["materialProperties"]
    
    # Add machineSettings (merge with category ranges if available)
    if "machineSettings" in material_data:
        machine_settings = {}
        
        # Deep copy and add min/max ranges from universal category ranges
        for param_name, param_data in material_data["machineSettings"].items():
            machine_settings[param_name] = param_data.copy()
            
            # Map parameter names to category range names
            range_mapping = {
                "wavelength": "wavelength",
                "powerRange": "powerRange",
                "pulseWidth": "pulseDuration",
                "repetitionRate": "repetitionRate",
                "spotSize": "spotSize",
                "energyDensity": "fluenceThreshold"
            }
            
            # Add min/max from category ranges if available
            if category_ranges and param_name in range_mapping:
                range_key = range_mapping[param_name]
                if range_key in category_ranges:
                    cat_param = category_ranges[range_key]
                    # Add min/max if they exist in category but not in material
                    if "min" in cat_param and "min" not in machine_settings[param_name]:
                        machine_settings[param_name]["min"] = cat_param["min"]
                    if "max" in cat_param and "max" not in machine_settings[param_name]:
                        machine_settings[param_name]["max"] = cat_param["max"]
        
        frontmatter["machineSettings"] = machine_settings
    
    # Add outcomeMetrics
    if "outcomeMetrics" in material_data:
        frontmatter["outcomeMetrics"] = material_data["outcomeMetrics"]
    
    # Add environmentalImpact
    if "environmentalImpact" in material_data:
        frontmatter["environmentalImpact"] = material_data["environmentalImpact"]
    
    # Add regulatoryStandards
    if "regulatoryStandards" in material_data:
        frontmatter["regulatoryStandards"] = material_data["regulatoryStandards"]
    
    # Add FAQ (convert to frontmatter structure, handle both old and new formats)
    if "faq" in material_data:
        faq_data = material_data["faq"]
        
        # New format: dict with questions array
        if isinstance(faq_data, dict) and "questions" in faq_data:
            frontmatter["faq"] = {
                "questions": faq_data["questions"],
                "generated": faq_data.get("generated", datetime.now().isoformat()),
                "question_count": faq_data.get("question_count", len(faq_data["questions"])),
                "total_words": faq_data.get("total_words", 0)
            }
        
        # Old format: list of question/answer dicts
        elif isinstance(faq_data, list):
            frontmatter["faq"] = {
                "questions": faq_data,  # Already in correct format
                "generated": datetime.now().isoformat(),
                "question_count": len(faq_data),
                "total_words": sum(len(item.get("answer", "").split()) for item in faq_data)
            }
    
    # Add metadata fields
    if "material_metadata" in material_data:
        frontmatter["material_metadata"] = material_data["material_metadata"]
    
    if "subtitle_metadata" in material_data:
        frontmatter["subtitle_metadata"] = material_data["subtitle_metadata"]
    
    # Write to frontmatter file
    with open(frontmatter_path, "w") as f:
        yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    return frontmatter_path, len(frontmatter.keys())


def main():
    """Export Steel, Aluminum, and Bronze with ALL fields."""
    
    print("🔄 FULL MATERIALS.YAML → FRONTMATTER EXPORT")
    print("=" * 70)
    print()
    
    # Load Materials.yaml
    materials_path = Path("data/materials.yaml")
    with open(materials_path, "r") as f:
        data = yaml.safe_load(f)
    
    materials_data = data.get("materials", {})
    
    # Load Categories.yaml for min/max ranges
    categories_path = Path("data/categories.yaml")
    with open(categories_path, "r") as f:
        categories_data = yaml.safe_load(f)
    
    # Export three test materials
    test_materials = ["Steel", "Aluminum", "Bronze"]
    
    for material_name in test_materials:
        if material_name not in materials_data:
            print(f"⚠️  {material_name} not found in Materials.yaml")
            continue
        
        material_data = materials_data[material_name]
        
        print(f"📤 Exporting {material_name}...")
        
        # Show what we're exporting
        top_level_keys = list(material_data.keys())
        print(f"   Fields: {', '.join(top_level_keys[:10])}{'...' if len(top_level_keys) > 10 else ''}")
        
        # Get universal category ranges (apply to all materials)
        category_ranges = get_category_ranges(categories_data)
        
        # Export with all fields
        frontmatter_path, field_count = export_material_to_frontmatter(material_name, material_data, category_ranges)
        
        # Verify
        file_size = frontmatter_path.stat().st_size
        print(f"   ✅ Exported to: {frontmatter_path}")
        print(f"   📊 Field count: {field_count}")
        print(f"   📏 File size: {file_size:,} bytes")
        
        # Show FAQ info (handle both formats)
        if "faq" in material_data:
            faq_data = material_data["faq"]
            if isinstance(faq_data, dict) and "questions" in faq_data:
                faq_count = len(faq_data["questions"])
            elif isinstance(faq_data, list):
                faq_count = len(faq_data)
            else:
                faq_count = 0
            print(f"   ❓ FAQ questions: {faq_count}")
        
        print()
    
    print("=" * 70)
    print("✅ Full export complete - all Materials.yaml fields preserved!")


if __name__ == "__main__":
    main()
