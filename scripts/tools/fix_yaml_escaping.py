#!/usr/bin/env python3
"""
Fix YAML Escaping and Line Breaks in Frontmatter Files

Removes unnecessary line continuation backslashes and fixes escaped characters
to make the YAML more readable and properly formatted.
"""

import re
from pathlib import Path

def fix_yaml_escaping(content: str) -> str:
    """Fix YAML escaping issues in frontmatter content"""
    
    # Split content into lines for processing
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line is part of a multi-line YAML string with backslashes
        if (': "' in line and line.rstrip().endswith('\\')) or (line.strip().startswith('\\ ') and i > 0):
            # This is a multi-line string that needs fixing
            
            # Start collecting the full string
            full_string = ""
            
            # If this line starts the string
            if ': "' in line:
                # Extract the key and start of the string
                key_part, string_part = line.split(': "', 1)
                string_part = string_part.rstrip('\\').rstrip()
                full_string = string_part
                
                # Collect continuation lines
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip().startswith('\\ '):
                        # Remove the backslash and leading space, add a space for continuation
                        continuation = next_line.strip()[2:]  # Remove '\\ '
                        if continuation.endswith('\\'):
                            continuation = continuation[:-1].rstrip()
                        if full_string and not full_string.endswith(' '):
                            full_string += ' '
                        full_string += continuation
                        i += 1
                    else:
                        break
                
                # Fix escaped characters
                full_string = fix_escaped_characters(full_string)
                
                # Reconstruct the line as a single quoted string
                fixed_line = f'{key_part}: "{full_string}"'
                fixed_lines.append(fixed_line)
            else:
                # This shouldn't happen if we're processing correctly
                fixed_lines.append(line)
                i += 1
        else:
            # Regular line, just fix escaped characters
            fixed_line = fix_escaped_characters(line)
            fixed_lines.append(fixed_line)
            i += 1
    
    return '\n'.join(fixed_lines)

def fix_escaped_characters(text: str) -> str:
    """Fix common escaped characters in YAML"""
    
    # Fix degree symbol
    text = re.sub(r'\\xB0', '°', text)
    
    # Fix other common escape sequences
    text = re.sub(r'\\x([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), text)
    
    return text

def fix_frontmatter_file(file_path: Path) -> bool:
    """Fix escaping issues in a single frontmatter file"""
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply fixes
        fixed_content = fix_yaml_escaping(content)
        
        # Only write if there were changes
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path.stem}: {e}")
        return False

def fix_all_frontmatter_escaping():
    """Fix escaping issues in all frontmatter files"""
    
    print("🔧 Fixing YAML Escaping and Line Breaks in Frontmatter Files")
    print("=" * 65)
    
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print("❌ Frontmatter directory not found")
        return
    
    processed = 0
    fixed = 0
    
    # Process all frontmatter files
    for file_path in sorted(frontmatter_dir.glob("*-laser-cleaning.md")):
        material_name = file_path.stem.replace("-laser-cleaning", "")
        
        if fix_frontmatter_file(file_path):
            print(f"✅ {material_name:<30} - Fixed escaping issues")
            fixed += 1
        else:
            print(f"⏭️  {material_name:<30} - No changes needed")
        
        processed += 1
    
    print("\n📊 Summary:")
    print(f"   Files processed: {processed}")
    print(f"   Files fixed: {fixed}")
    print(f"   Files unchanged: {processed - fixed}")
    
    if fixed > 0:
        print(f"\n✅ Successfully fixed escaping issues in {fixed} frontmatter files")
        print("🧹 YAML is now cleaner and more readable")

if __name__ == "__main__":
    fix_all_frontmatter_escaping()
