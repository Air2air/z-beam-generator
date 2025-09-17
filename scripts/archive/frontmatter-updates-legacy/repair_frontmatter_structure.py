#!/usr/bin/env python3
"""
Analyze and repair frontmatter structure issues.
Ensures name field is at the top of each frontmatter file.
"""
import os
import yaml
import re
from pathlib import Path

def load_frontmatter_content(file_path):
    """Extract raw frontmatter content from markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter between --- markers
        match = re.match(r'^---\n(.*?)\n---(.*)$', content, re.DOTALL)
        if not match:
            return None, None, "No frontmatter found"
        
        frontmatter_content = match.group(1)
        remaining_content = match.group(2)
        
        try:
            data = yaml.safe_load(frontmatter_content)
            return data, remaining_content, None
        except yaml.YAMLError as e:
            return None, None, f"YAML parsing error: {e}"
    except Exception as e:
        return None, None, f"File reading error: {e}"

def reorder_frontmatter(data):
    """Reorder frontmatter with name field first."""
    if not data:
        return data
    
    # Desired field order with name first
    field_order = [
        'name',
        'applications', 
        'technicalSpecifications',
        'description',
        'author',
        'author_object',
        'benefits',
        'chemicalProperties',
        'composition',
        'compatibility',
        'regulatoryStandards',
        'images',
        'title',
        'headline',
        'environmentalImpact',
        'outcomes',
        'keywords',
        'prompt_chain_verification'
    ]
    
    # Create ordered dictionary
    ordered_data = {}
    
    # Add fields in desired order if they exist
    for field in field_order:
        if field in data:
            ordered_data[field] = data[field]
    
    # Add any remaining fields not in the order list
    for key, value in data.items():
        if key not in ordered_data:
            ordered_data[key] = value
    
    return ordered_data

def write_frontmatter_file(file_path, data, remaining_content):
    """Write reordered frontmatter back to file."""
    try:
        # Convert to YAML with proper formatting
        yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Write complete file
        full_content = f"---\n{yaml_content}---{remaining_content}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return True, None
    except Exception as e:
        return False, f"Writing error: {e}"

def analyze_file_structure(file_path):
    """Analyze frontmatter structure and identify issues."""
    data, remaining_content, error = load_frontmatter_content(file_path)
    
    if error:
        return {
            'file': file_path.name,
            'status': 'error',
            'error': error,
            'name_present': False,
            'name_first': False,
            'needs_repair': True
        }
    
    name_present = 'name' in data if data else False
    
    # Check if name is first field
    name_first = False
    if data and name_present:
        first_key = next(iter(data.keys()))
        name_first = first_key == 'name'
    
    needs_repair = name_present and not name_first
    
    return {
        'file': file_path.name,
        'status': 'ok' if not needs_repair else 'needs_repair',
        'error': None,
        'name_present': name_present,
        'name_first': name_first,
        'needs_repair': needs_repair,
        'first_field': next(iter(data.keys())) if data else None
    }

def repair_file(file_path):
    """Repair a single frontmatter file."""
    data, remaining_content, error = load_frontmatter_content(file_path)
    
    if error:
        return False, error
    
    # Reorder frontmatter
    ordered_data = reorder_frontmatter(data)
    
    # Write back to file
    success, write_error = write_frontmatter_file(file_path, ordered_data, remaining_content)
    
    if not success:
        return False, write_error
    
    return True, None

def main():
    """Analyze and repair frontmatter structure."""
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Directory not found: {frontmatter_dir}")
        return
    
    print("🔍 Analyzing frontmatter structure...\n")
    
    analysis_results = []
    files_needing_repair = []
    
    # Analyze all files
    for md_file in sorted(frontmatter_dir.glob('*.md')):
        result = analyze_file_structure(md_file)
        analysis_results.append(result)
        
        if result['needs_repair']:
            files_needing_repair.append(md_file)
        
        status_icon = "✅" if result['status'] == 'ok' else "⚠️" if result['needs_repair'] else "❌"
        print(f"{status_icon} {result['file']}")
        
        if result['error']:
            print(f"   Error: {result['error']}")
        elif result['name_present']:
            if result['name_first']:
                print(f"   Name field is correctly positioned first")
            else:
                print(f"   Name field present but not first (current first: {result['first_field']})")
        else:
            print(f"   Missing name field")
    
    # Summary
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    
    total_files = len(analysis_results)
    files_with_name = sum(1 for r in analysis_results if r['name_present'])
    files_name_first = sum(1 for r in analysis_results if r['name_first'])
    files_with_errors = sum(1 for r in analysis_results if r['status'] == 'error')
    
    print(f"📁 Total files: {total_files}")
    print(f"✅ Files with name field: {files_with_name}")
    print(f"🔝 Files with name first: {files_name_first}")
    print(f"⚠️  Files needing repair: {len(files_needing_repair)}")
    print(f"❌ Files with errors: {files_with_errors}")
    
    # Repair files if needed
    if files_needing_repair:
        print(f"\n🔧 Repairing {len(files_needing_repair)} files...")
        
        repair_success = 0
        repair_errors = []
        
        for file_path in files_needing_repair:
            success, error = repair_file(file_path)
            if success:
                repair_success += 1
                print(f"✅ Repaired: {file_path.name}")
            else:
                repair_errors.append((file_path.name, error))
                print(f"❌ Failed to repair: {file_path.name} - {error}")
        
        print(f"\n📊 REPAIR SUMMARY")
        print(f"✅ Successfully repaired: {repair_success}")
        print(f"❌ Failed repairs: {len(repair_errors)}")
        
        if repair_errors:
            print(f"\n❌ REPAIR ERRORS:")
            for filename, error in repair_errors:
                print(f"   • {filename}: {error}")
    else:
        print(f"\n🎉 No repairs needed - all files have proper structure!")

if __name__ == "__main__":
    main()
