#!/usr/bin/env python3
"""
Frontmatter YAML Formatting Fix Script

Fixes YAML formatting issues in frontmatter files that prevent proper parsing.
Handles multi-line strings, proper indentation, and removes redundant properties.

Usage: python3 scripts/fix_frontmatter_yaml.py [--dry-run]
"""

import re
import argparse
from pathlib import Path

def fix_yaml_formatting(content: str) -> str:
    """
    Fix YAML formatting issues in frontmatter content.
    
    Returns:
        Fixed YAML content
    """
    lines = content.split('\n')
    fixed_lines = []
    in_yaml = False
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if in_yaml:
                # End of YAML frontmatter
                fixed_lines.append(line)
                break
            else:
                # Start of YAML frontmatter
                in_yaml = True
                fixed_lines.append(line)
                continue
        
        if not in_yaml:
            continue
            
        # Fix description multi-line formatting
        if line.startswith('description: """') and line.count('"""') == 1:
            # Multi-line description starting
            desc_content = line.replace('description: """', '').replace('"', '')
            fixed_lines.append('description: |')
            if desc_content.strip():
                fixed_lines.append(f'  {desc_content.strip()}')
            
            # Look ahead for continuation lines
            j = i + 1
            while j < len(lines) and not lines[j].strip().endswith('"""'):
                content_line = lines[j].strip()
                if content_line:
                    fixed_lines.append(f'  {content_line}')
                j += 1
            
            # Add the final line if it exists
            if j < len(lines):
                final_content = lines[j].replace('"""', '').strip()
                if final_content:
                    fixed_lines.append(f'  {final_content}')
            
            # Skip processed lines
            i = j
            continue
            
        # Fix keywords multi-line formatting
        elif line.startswith('keywords: """') and line.count('"""') == 1:
            # Multi-line keywords starting
            keywords_content = line.replace('keywords: """', '').replace('"', '')
            
            # Look ahead for continuation lines
            all_keywords = []
            if keywords_content.strip():
                all_keywords.append(keywords_content.strip())
            
            j = i + 1
            while j < len(lines) and not lines[j].strip().endswith('"""'):
                content_line = lines[j].strip()
                if content_line:
                    all_keywords.append(content_line)
                j += 1
            
            # Add the final line if it exists
            if j < len(lines):
                final_content = lines[j].replace('"""', '').strip()
                if final_content:
                    all_keywords.append(final_content)
            
            # Join and format keywords
            all_keywords_text = ' '.join(all_keywords)
            # Remove any stray quotes and fix comma spacing
            all_keywords_text = all_keywords_text.replace('"', '').replace('," ', ', ')
            fixed_lines.append(f'keywords: {all_keywords_text}')
            
            # Skip processed lines
            i = j
            continue
            
        # Fix chemicalProperties formatting
        elif line.startswith('chemicalProperties:') and not line.strip().endswith(':'):
            # Single-line chemical properties - need to expand
            props_content = line.replace('chemicalProperties:', '').strip()
            fixed_lines.append('chemicalProperties:')
            
            # Parse the inline properties
            if 'symbol:' in props_content:
                symbol_match = re.search(r'symbol:\s*"""?([^"]+)"""?', props_content)
                if symbol_match:
                    fixed_lines.append(f'  symbol: "{symbol_match.group(1).strip()}"')
            
            if 'formula:' in props_content:
                formula_match = re.search(r'formula:\s*"""?([^"]+)"""?(?:\s+materialType|$)', props_content)
                if formula_match:
                    fixed_lines.append(f'  formula: "{formula_match.group(1).strip()}"')
            
            if 'materialType:' in props_content:
                material_match = re.search(r'materialType:\s*(\w+)', props_content)
                if material_match:
                    fixed_lines.append(f'  materialType: {material_match.group(1)}')
            continue
            
        # Fix properties formatting if it's all on one line
        elif line.startswith('properties:') and not line.strip().endswith(':'):
            # This shouldn't happen with our current data, but handle it
            fixed_lines.append('properties:')
            continue
            
        # Remove old thermal properties that are no longer needed
        elif any(old_prop in line for old_prop in ['meltingPoint:', 'decompositionPoint:', 'thermalBehaviorType:']):
            # Skip these lines - they've been replaced by thermalDestructionPoint/Type
            if not line.strip().startswith(('meltingPointUnit:', 'meltingPointMin:', 'meltingPointMax:', 
                                          'meltingPointNumeric:', 'meltingPercentile:',
                                          'decompositionPointUnit:', 'decompositionPointMin:', 
                                          'decompositionPointMax:', 'decompositionPointNumeric:')):
                continue
            
        # Regular line - just add it
        else:
            fixed_lines.append(line)
    
    # Add the rest of the content (after YAML frontmatter)
    if in_yaml and i < len(lines) - 1:
        fixed_lines.extend(lines[i+1:])
    
    return '\n'.join(fixed_lines)

def process_frontmatter_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Process a single frontmatter file to fix YAML formatting.
    
    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix YAML formatting
        fixed_content = fix_yaml_formatting(content)
        
        # Check if any changes were made
        if content != fixed_content:
            if dry_run:
                print(f"🔄 Would fix: {file_path.name}")
                return True
            else:
                # Write changes
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"✅ Fixed YAML formatting: {file_path.name}")
                return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Fix YAML formatting in frontmatter files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    # Find all frontmatter files
    frontmatter_dir = Path(__file__).parent.parent / "content" / "components" / "frontmatter"
    frontmatter_files = list(frontmatter_dir.glob("*-laser-cleaning.md"))
    
    print(f"🔍 Found {len(frontmatter_files)} frontmatter files")
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No files will be modified")
    
    # Process each file
    processed_count = 0
    for file_path in frontmatter_files:
        if process_frontmatter_file(file_path, args.dry_run):
            processed_count += 1
    
    # Summary
    print("\n📈 YAML Formatting Summary:")
    print(f"   Total files: {len(frontmatter_files)}")
    print(f"   {'Would fix' if args.dry_run else 'Fixed'}: {processed_count}")
    print(f"   Already correct: {len(frontmatter_files) - processed_count}")
    
    if args.dry_run and processed_count > 0:
        print("\n💡 Run without --dry-run to apply changes")

if __name__ == "__main__":
    main()
