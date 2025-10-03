#!/usr/bin/env python3
"""
Safely add industryTags to Phase 1A materials by directly editing Materials.yaml
Uses line-by-line text manipulation to preserve exact YAML formatting
"""

from pathlib import Path
import re

def main():
    yaml_path = Path('data/Materials.yaml')
    
    print('=' * 80)
    print('ADDING INDUSTRY TAGS TO PHASE 1A MATERIALS - SAFE TEXT EDIT')
    print('=' * 80)
    print()
    
    # Backup
    backup_path = Path('data/Materials.yaml.backup_safe')
    import shutil
    shutil.copy(yaml_path, backup_path)
    print(f'✅ Backup created: {backup_path}')
    print()
    
    # Read entire file
    with open(yaml_path, 'r') as f:
        lines = f.readlines()
    
    print(f'📖 Loaded {len(lines)} lines from Materials.yaml')
    print()
    
    # Define industry tags for each material
    industry_tags = {
        'Aluminum': [
            'Aerospace', 'Automotive', 'Construction', 'Electronics Manufacturing',
            'Food and Beverage Processing', 'Marine', 'Packaging', 'Rail Transport',
            'Renewable Energy'
        ],
        'Steel': [
            'Automotive', 'Construction', 'Manufacturing', 'Oil & Gas',
            'Rail Transport', 'Shipbuilding'
        ],
        'Copper': [
            'Architecture', 'Electronics Manufacturing', 'HVAC Systems', 'Marine',
            'Plumbing', 'Power Generation', 'Renewable Energy', 'Telecommunications'
        ],
        'Brass': [
            'Architecture', 'Hardware Manufacturing', 'Marine', 'Musical Instruments',
            'Plumbing', 'Valves and Fittings'
        ],
        'Bronze': [
            'Architecture', 'Art and Sculpture', 'Bearings', 'Marine',
            'Memorial and Monument', 'Musical Instruments'
        ],
        'Nickel': [
            'Aerospace', 'Chemical Processing', 'Electronics Manufacturing',
            'Energy Storage', 'Medical Devices', 'Oil & Gas'
        ],
        'Zinc': [
            'Automotive', 'Construction', 'Die Casting', 'Galvanizing',
            'Hardware Manufacturing'
        ]
    }
    
    # Step 1: Add Titanium to material_index
    print('1️⃣  Adding Titanium to material_index...')
    for i, line in enumerate(lines):
        if line.strip() == 'Tin: metal':
            # Insert Titanium after Tin
            lines.insert(i + 1, '  Titanium: metal\n')
            print('✅ Added Titanium: metal to material_index')
            break
    print()
    
    # Step 2: Add industryTags to each material
    print('2️⃣  Adding industryTags to materials...')
    
    for material_name, tags in industry_tags.items():
        # Find the material header
        material_pattern = re.compile(rf'^  {re.escape(material_name)}:$')
        material_start = None
        
        for i, line in enumerate(lines):
            if material_pattern.match(line):
                material_start = i
                break
        
        if material_start is None:
            print(f'⚠️  {material_name} not found, skipping')
            continue
        
        # Find the end of this material's properties (before next material or end of materials section)
        material_end = None
        for i in range(material_start + 1, min(material_start + 300, len(lines))):
            # Look for next material (starts with "  " and capital letter followed by ":")
            if re.match(r'^  [A-Z].*:$', lines[i]) and i > material_start + 10:
                material_end = i
                break
        
        if material_end is None:
            print(f'⚠️  Could not find end of {material_name}, skipping')
            continue
        
        # Check if material_metadata already exists
        has_metadata = False
        for i in range(material_start, material_end):
            if 'material_metadata:' in lines[i]:
                has_metadata = True
                print(f'⚠️  {material_name} already has material_metadata, skipping')
                break
        
        if has_metadata:
            continue
        
        # Insert material_metadata with industryTags before the next material
        indent = '    '
        metadata_lines = [
            '    material_metadata:\n',
            '      industryTags:\n'
        ]
        for tag in tags:
            metadata_lines.append(f'      - {tag}\n')
        
        # Insert at material_end position
        for j, metadata_line in enumerate(metadata_lines):
            lines.insert(material_end + j, metadata_line)
        
        print(f'✅ Added {len(tags)} industryTags to {material_name}')
    
    print()
    
    # Write back to file
    print('💾 Saving updated Materials.yaml...')
    with open(yaml_path, 'w') as f:
        f.writelines(lines)
    print('✅ Saved Materials.yaml')
    print()
    
    # Verify
    print('🔍 Verifying changes...')
    try:
        from data.materials import load_materials
        m = load_materials()
        
        print(f'✅ Total materials: {len(m["materials"])}')
        print(f'✅ Titanium exists: {"Titanium" in m["materials"]}')
        
        tags_count = 0
        for mat_name in industry_tags.keys():
            if mat_name in m['materials']:
                mat = m['materials'][mat_name]
                if isinstance(mat, dict):
                    metadata = mat.get('material_metadata', {})
                    if metadata.get('industryTags'):
                        tags_count += 1
                        print(f'✅ {mat_name}: {len(metadata["industryTags"])} industryTags')
        
        print(f'\n✅ Phase 1A materials with industryTags: {tags_count}/7')
        
    except Exception as e:
        print(f'❌ Verification failed: {e}')
        print('⚠️  Restoring backup...')
        shutil.copy(backup_path, yaml_path)
        print('✅ Restored from backup')
        return False
    
    print()
    print('=' * 80)
    print('✅ UPDATE COMPLETE')
    print('=' * 80)
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
