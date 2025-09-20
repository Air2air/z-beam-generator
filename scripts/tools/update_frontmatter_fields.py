#!/usr/bin/env python3
"""
Frontmatter Field Updater
Adds missing fields to existing frontmatter files without full regeneration.
Preserves all existing data while adding required fields for fail-fast components.
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def load_materials_data() -> Dict:
    """Load materials data for category mappings"""
    try:
        materials_path = Path(__file__).parent.parent.parent / "data" / "materials.yaml"
        with open(materials_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading materials data: {e}")
        return {}

def get_category_mappings() -> Dict[str, Dict[str, str]]:
    """Define material category mappings for new fields"""
    return {
        'metal': {
            'contaminationSource': 'oxidation and industrial pollutants',
            'thermalEffect': 'minimal thermal effects with controlled heat input',
            'substrateDescription': 'metallic substrate'
        },
        'ceramic': {
            'contaminationSource': 'firing processes and handling contamination',
            'thermalEffect': 'minimal thermal stress with controlled exposure',
            'substrateDescription': 'ceramic substrate'
        },
        'glass': {
            'contaminationSource': 'atmospheric deposition and processing residues',
            'thermalEffect': 'no thermal shock with controlled processing',
            'substrateDescription': 'glass substrate'
        },
        'stone': {
            'contaminationSource': 'weathering and environmental exposure',
            'thermalEffect': 'minimal thermal expansion with precise control',
            'substrateDescription': 'stone substrate'
        },
        'wood': {
            'contaminationSource': 'biological activity and environmental factors',
            'thermalEffect': 'controlled thermal exposure preventing carbonization',
            'substrateDescription': 'wood substrate'
        },
        'composite': {
            'contaminationSource': 'manufacturing processes and environmental aging',
            'thermalEffect': 'minimal matrix heating preserving structural integrity',
            'substrateDescription': 'composite substrate'
        },
        'masonry': {
            'contaminationSource': 'construction activities and atmospheric exposure',
            'thermalEffect': 'controlled thermal input preserving material integrity',
            'substrateDescription': 'masonry substrate'
        },
        'semiconductor': {
            'contaminationSource': 'fabrication processes and cleanroom contamination',
            'thermalEffect': 'minimal thermal stress maintaining electronic properties',
            'substrateDescription': 'semiconductor substrate'
        }
    }

def get_material_category(material_name: str, materials_data: Dict) -> str:
    """Get material category from materials data"""
    material_index = materials_data.get('material_index', {})
    material_info = material_index.get(material_name.lower(), {})
    return material_info.get('category', 'metal')  # Default to metal if not found

def parse_frontmatter_file(file_path: Path) -> tuple[Dict, str]:
    """Parse frontmatter file and return (frontmatter_data, content)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---\n'):
            raise ValueError("Invalid frontmatter format")
        
        # Find the end of frontmatter - look for line that starts with ---
        lines = content.split('\n')
        end_line = -1
        for i, line in enumerate(lines[1:], 1):  # Start from line 1 (skip opening ---)
            if line.strip() == '---':
                end_line = i
                break
        
        if end_line == -1:
            # Handle frontmatter-only files (no closing ---)
            frontmatter_text = '\n'.join(lines[1:])  # Remove opening ---
            remaining_content = ""
        else:
            frontmatter_text = '\n'.join(lines[1:end_line])
            remaining_content = '\n'.join(lines[end_line + 1:])
        
        frontmatter_data = yaml.safe_load(frontmatter_text)
        return frontmatter_data, remaining_content
    
    except Exception as e:
        print(f"❌ Error parsing {file_path}: {e}")
        return {}, ""

def update_frontmatter_fields(frontmatter_data: Dict, material_name: str, category: str, category_mappings: Dict) -> bool:
    """Update frontmatter with missing fields. Returns True if changes were made."""
    changes_made = False
    
    # 1. Add substrateDescription if missing
    if 'substrateDescription' not in frontmatter_data:
        material_mappings = category_mappings.get(category, category_mappings['metal'])
        base_desc = material_mappings['substrateDescription']
        frontmatter_data['substrateDescription'] = f"{base_desc.replace('substrate', material_name.lower() + ' substrate')}"
        changes_made = True
        print("  ✅ Added substrateDescription")
    
    # 2. Ensure technicalSpecifications section exists
    if 'technicalSpecifications' not in frontmatter_data:
        frontmatter_data['technicalSpecifications'] = {}
        changes_made = True
        print("  ✅ Created technicalSpecifications section")
    
    tech_specs = frontmatter_data['technicalSpecifications']
    material_mappings = category_mappings.get(category, category_mappings['metal'])
    
    # 3. Add contaminationSource if missing
    if 'contaminationSource' not in tech_specs:
        tech_specs['contaminationSource'] = material_mappings['contaminationSource']
        changes_made = True
        print("  ✅ Added technicalSpecifications.contaminationSource")
    
    # 4. Add thermalEffect if missing
    if 'thermalEffect' not in tech_specs:
        tech_specs['thermalEffect'] = material_mappings['thermalEffect']
        changes_made = True
        print("  ✅ Added technicalSpecifications.thermalEffect")
    
    # 5. Copy machine settings to technical specifications if needed
    if 'machineSettings' in frontmatter_data:
        machine_settings = frontmatter_data['machineSettings']
        
        # Map common fields
        field_mappings = {
            'wavelength': 'wavelength',
            'powerRange': 'powerRange',  # Keep the same field name 
            'pulseDuration': 'pulseDuration',  # Keep the same field name
            'spotSize': 'spotSize',
            'repetitionRate': 'repetitionRate'
        }
        
        for machine_key, tech_key in field_mappings.items():
            if machine_key in machine_settings and tech_key not in tech_specs:
                tech_specs[tech_key] = str(machine_settings[machine_key])
                changes_made = True
                print(f"  ✅ Copied {machine_key} to technicalSpecifications.{tech_key}")
    
    # 6. Ensure all required laser parameters are present
    required_params = ['powerRange', 'pulseDuration', 'spotSize', 'repetitionRate']
    if 'machineSettings' in frontmatter_data:
        machine_settings = frontmatter_data['machineSettings']
        for param in required_params:
            if param not in machine_settings:
                # Add missing parameters with reasonable defaults based on category
                if param == 'repetitionRate':
                    default_value = '20-100kHz'
                elif param == 'spotSize':
                    default_value = '0.3-2.0mm'
                else:
                    continue  # Skip if we don't have a default
                
                machine_settings[param] = default_value
                changes_made = True
                print(f"  ✅ Added missing machineSettings.{param}")
    
    return changes_made

def write_updated_frontmatter(file_path: Path, frontmatter_data: Dict, remaining_content: str):
    """Write updated frontmatter back to file"""
    try:
        # Convert back to YAML
        yaml_content = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Reconstruct file - always include closing --- for consistency with existing format
        if remaining_content.strip():
            full_content = f"---\n{yaml_content}---\n{remaining_content}"
        else:
            # Even frontmatter-only files should have closing ---
            full_content = f"---\n{yaml_content}---\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return True
    except Exception as e:
        print(f"❌ Error writing {file_path}: {e}")
        return False

def update_single_file(file_path: Path, materials_data: Dict, category_mappings: Dict) -> bool:
    """Update a single frontmatter file"""
    print(f"📄 Processing: {file_path.name}")
    
    # Parse existing frontmatter
    frontmatter_data, remaining_content = parse_frontmatter_file(file_path)
    if not frontmatter_data:
        return False
    
    # Get material info
    material_name = frontmatter_data.get('name', file_path.stem.replace('-laser-cleaning', ''))
    category = frontmatter_data.get('category') or get_material_category(material_name, materials_data)
    
    print(f"  📋 Material: {material_name} (Category: {category})")
    
    # Update fields
    changes_made = update_frontmatter_fields(frontmatter_data, material_name, category, category_mappings)
    
    if changes_made:
        if write_updated_frontmatter(file_path, frontmatter_data, remaining_content):
            print(f"  ✅ Successfully updated {file_path.name}")
            return True
        else:
            return False
    else:
        print(f"  ℹ️  No updates needed for {file_path.name}")
        return True

def main():
    parser = argparse.ArgumentParser(description="Update frontmatter files with missing fields")
    parser.add_argument('--material', type=str, help='Update specific material only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    parser.add_argument('--force', action='store_true', help='Update even if fields already exist')
    args = parser.parse_args()
    
    # Load data
    print("🔄 Loading materials data...")
    materials_data = load_materials_data()
    category_mappings = get_category_mappings()
    
    # Find frontmatter files
    frontmatter_dir = Path(__file__).parent.parent.parent / "content" / "components" / "frontmatter"
    
    if args.material:
        pattern = f"{args.material.lower()}-laser-cleaning.md"
        files = list(frontmatter_dir.glob(pattern))
        if not files:
            print(f"❌ No frontmatter file found for material: {args.material}")
            return 1
    else:
        files = list(frontmatter_dir.glob("*-laser-cleaning.md"))
    
    if not files:
        print("❌ No frontmatter files found")
        return 1
    
    print(f"\n📊 Found {len(files)} frontmatter files to process")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    
    # Process files
    success_count = 0
    for file_path in sorted(files):
        if args.dry_run:
            print(f"\n🔍 Would process: {file_path.name}")
            frontmatter_data, _ = parse_frontmatter_file(file_path)
            if frontmatter_data:
                
                missing_fields = []
                if 'substrateDescription' not in frontmatter_data:
                    missing_fields.append('substrateDescription')
                if 'technicalSpecifications' not in frontmatter_data:
                    missing_fields.append('technicalSpecifications (entire section)')
                elif isinstance(frontmatter_data.get('technicalSpecifications'), dict):
                    tech_specs = frontmatter_data['technicalSpecifications']
                    if 'contaminationSource' not in tech_specs:
                        missing_fields.append('technicalSpecifications.contaminationSource')
                    if 'thermalEffect' not in tech_specs:
                        missing_fields.append('technicalSpecifications.thermalEffect')
                
                if missing_fields:
                    print(f"  📋 Missing fields: {', '.join(missing_fields)}")
                else:
                    print("  ✅ All fields present")
        else:
            if update_single_file(file_path, materials_data, category_mappings):
                success_count += 1
            print()  # Add spacing
    
    if not args.dry_run:
        print(f"\n📊 Summary: Successfully updated {success_count}/{len(files)} files")
        
        if success_count == len(files):
            print("✅ All frontmatter files updated successfully!")
            print("\n🔧 Next step: Test caption generation with updated frontmatter:")
            print("   python3 run.py --material 'Steel' --components caption")
        else:
            print("⚠️  Some files had issues. Check the output above for details.")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
