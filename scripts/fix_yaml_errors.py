#!/usr/bin/env python3
"""
Fix specific YAML parsing errors found in frontmatter files.
This script targets the exact errors shown in the validation output.
"""

import re
import yaml
import argparse
from pathlib import Path

def fix_merged_properties(content):
    """Fix lines where multiple properties are merged on one line."""
    # Pattern: property: "value" anotherProperty: "value"
    # Split these into separate lines
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Check if line has multiple properties (more than one colon, not in a list)
        if line.count(':') > 1 and not line.strip().startswith('-'):
            # Pattern: ends with quote, followed by space and property name
            pattern = r'(")\s+([a-zA-Z_][a-zA-Z0-9_]*:)'
            if re.search(pattern, line):
                # Get indentation from original line
                indent = len(line) - len(line.lstrip())
                
                # Split on the pattern
                parts = re.split(pattern, line)
                if len(parts) >= 4:
                    # First part with quote
                    fixed_lines.append(parts[0] + parts[1])
                    # Remaining properties
                    for i in range(2, len(parts), 3):
                        if i + 1 < len(parts):
                            prop_and_rest = parts[i] + (parts[i + 1] if i + 1 < len(parts) else '')
                            fixed_lines.append(' ' * indent + prop_and_rest)
                    continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_unquoted_values(content):
    """Quote values that contain special characters."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if ':' in line and not line.strip().startswith('-'):
            key, sep, value = line.partition(':')
            value = value.strip()
            
            # Quote values that need quoting
            if value and not (value.startswith('"') or value.startswith("'") or 
                             value == 'null' or value.lower() in ['true', 'false'] or
                             (value.replace('.', '').replace('-', '').replace(' ', '').isdigit())):
                # Check if value needs quotes
                needs_quotes = (
                    ' ' in value or 
                    '(' in value or ')' in value or
                    '₁' in value or '₂' in value or '₃' in value or 
                    '₄' in value or '₅' in value or '₆' in value or
                    '₇' in value or '₈' in value or '₉' in value or '₀' in value or
                    'C₆H₁₀O₅' in value or
                    value.endswith('°C') or
                    value.endswith('kg/m³') or
                    value.endswith('g/cm³')
                )
                
                if needs_quotes:
                    value = f'"{value}"'
            
            fixed_lines.append(f"{key}:{sep}{value}")
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_malformed_yaml(content):
    """Fix specific malformed YAML patterns."""
    # Fix pattern like: chemicalFormula: "value"  decompositionPointUnit: "°C"
    content = re.sub(r'(")\s+([a-zA-Z_][a-zA-Z0-9_]*:\s*"[^"]*")', r'\1\n      \2', content)
    
    # Fix lines that end with extra quotes
    content = re.sub(r'decompositionPointUnit:\s*"°C""', 'decompositionPointUnit: "°C"', content)
    
    # Fix lines starting with comma (invalid YAML)
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if line.strip().startswith(', '):
            # Remove leading comma and space
            fixed_line = line.replace(', ', '', 1)
            # Ensure proper indentation
            if not fixed_line.startswith('  '):
                fixed_line = '  ' + fixed_line.strip()
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_file(file_path, dry_run=False):
    """Fix YAML errors in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter from content
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 2:
                yaml_content = parts[1]
                markdown_content = '---\n'.join(parts[2:]) if len(parts) > 2 else ''
            else:
                yaml_content = content
                markdown_content = ''
        else:
            # No frontmatter markers, assume pure YAML
            yaml_content = content
            markdown_content = ''
        
        # Apply fixes
        original_yaml = yaml_content
        
        # Fix merged properties first
        yaml_content = fix_merged_properties(yaml_content)
        
        # Fix unquoted values
        yaml_content = fix_unquoted_values(yaml_content)
        
        # Fix malformed patterns
        yaml_content = fix_malformed_yaml(yaml_content)
        
        # Validate YAML
        try:
            yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            print(f"❌ Still invalid YAML in {file_path}: {e}")
            return False
        
        # Check if changes were made
        if yaml_content != original_yaml:
            print(f"🔧 Fixed YAML errors in {file_path}")
            
            if not dry_run:
                # Reconstruct content
                if markdown_content:
                    new_content = f"---\n{yaml_content}---\n{markdown_content}"
                else:
                    new_content = f"---\n{yaml_content}\n"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            return True
        else:
            print(f"✅ No YAML fixes needed for {file_path}")
            return True
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Fix YAML parsing errors in frontmatter files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    # Find all frontmatter files
    content_dir = Path('content/components/frontmatter')
    if not content_dir.exists():
        print(f"❌ Content directory not found: {content_dir}")
        return
    
    frontmatter_files = list(content_dir.glob('*-laser-cleaning.md'))
    
    print(f"🔍 Found {len(frontmatter_files)} frontmatter files")
    if args.dry_run:
        print("🧪 DRY RUN MODE - No files will be modified")
    
    fixed_count = 0
    error_count = 0
    
    for file_path in frontmatter_files:
        if fix_file(file_path, args.dry_run):
            fixed_count += 1
        else:
            error_count += 1
    
    print("\n📈 Summary:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Errors: {error_count}")
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")

if __name__ == '__main__':
    main()
