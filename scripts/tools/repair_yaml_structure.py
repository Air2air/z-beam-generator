#!/usr/bin/env python3
"""
Careful YAML Validation and Repair

Fixes specific YAML issues in frontmatter files while preserving structure.
"""

import yaml
import re
from pathlib import Path

def fix_yaml_file(file_path: Path) -> bool:
    """Fix YAML issues in a specific file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # First, try to parse as-is to see if it's already valid
        if content.startswith('---\n'):
            yaml_content = content[4:]
            try:
                yaml.safe_load(yaml_content)
                return False  # Already valid, no changes needed
            except yaml.YAMLError:
                pass  # Continue with fixes
        
        # Apply targeted fixes
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            # Fix unquoted values that contain commas or special characters
            if ': ' in line and not line.strip().startswith('#') and not line.strip().startswith('-'):
                # Split at first colon-space
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    key, value = parts
                    
                    # Check if value needs quoting
                    if (value and 
                        not value.startswith('"') and 
                        not value.startswith("'") and
                        not value.replace('.', '').replace('-', '').isdigit() and
                        (',' in value or '(' in value or ')' in value)):
                        
                        # Quote the value
                        fixed_line = f'{key}: "{value}"'
            
            # Fix Unicode escape sequences
            if '\\u' in fixed_line:
                # Convert \\u sequences to actual Unicode characters
                fixed_line = re.sub(r'\\u([0-9A-Fa-f]{4})', 
                                   lambda m: chr(int(m.group(1), 16)), 
                                   fixed_line)
            
            fixed_lines.append(fixed_line)
        
        new_content = '\n'.join(fixed_lines)
        
        # Test if the fix worked
        if new_content.startswith('---\n'):
            yaml_content = new_content[4:]
            try:
                yaml.safe_load(yaml_content)
                # Valid YAML, save it
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            except yaml.YAMLError as e:
                print(f"❌ {file_path.stem}: Still invalid after fixes - {e}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ {file_path.stem}: Error processing file - {e}")
        return False

def repair_yaml_files():
    """Repair YAML issues in frontmatter files"""
    
    print("🔧 Repairing YAML Structure Issues")
    print("=" * 40)
    
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print("❌ Frontmatter directory not found")
        return
    
    processed = 0
    fixed = 0
    valid = 0
    
    for file_path in sorted(frontmatter_dir.glob("*-laser-cleaning.md")):
        material_name = file_path.stem.replace("-laser-cleaning", "")
        
        if fix_yaml_file(file_path):
            print(f"✅ {material_name:<30} - Fixed YAML structure")
            fixed += 1
        else:
            # Check if it was already valid
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content.startswith('---\n'):
                    yaml_content = content[4:]
                    yaml.safe_load(yaml_content)
                    print(f"⏭️  {material_name:<30} - Already valid")
                    valid += 1
            except:
                print(f"❌ {material_name:<30} - Needs manual attention")
        
        processed += 1
    
    print("\n📊 Summary:")
    print(f"   Files processed: {processed}")
    print(f"   Files fixed: {fixed}")
    print(f"   Files already valid: {valid}")
    print(f"   Files needing attention: {processed - fixed - valid}")

if __name__ == "__main__":
    repair_yaml_files()
