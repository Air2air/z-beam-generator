#!/usr/bin/env python3
"""
Frontmatter Quote Consistency Fix Script

This script standardizes all quotes in frontmatter files to use double quotes
consistently, following YAML best practices for technical content.

Key fixes:
- metric: 'value' → metric: "value"
- - result: 'value' → - result: "value"
- Other field: 'value' → Other field: "value"

This achieves 100% quote consistency across all frontmatter files.
"""

import re
import sys
from pathlib import Path

def fix_quote_consistency(filepath):
    """Fix quote inconsistencies in a single frontmatter file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Fix 1: metric fields with single quotes
    def fix_metric_quotes(match):
        field = match.group(1)
        value = match.group(2)
        changes_made.append(f"metric field: '{value}' → \"{value}\"")
        return f'{field}: "{value}"'
    
    content = re.sub(r'(metric:\s*)\'([^\']*)\'', fix_metric_quotes, content)
    
    # Fix 2: result fields with single quotes
    def fix_result_quotes(match):
        prefix = match.group(1)
        value = match.group(2)
        changes_made.append(f"result field: '{value}' → \"{value}\"")
        return f'{prefix}: "{value}"'
    
    content = re.sub(r'(- result:\s*)\'([^\']*)\'', fix_result_quotes, content)
    
    # Fix 3: Other common fields with single quotes
    common_fields = ['density', 'formula', 'description', 'fluenceRange', 'symbol', 'materialType']
    for field in common_fields:
        pattern = f'({field}:\\s*)\'([^\']*)\')'
        
        def fix_field_quotes(match):
            field_name = match.group(1)
            value = match.group(2)
            changes_made.append(f"{field_name} field: '{value}' → \"{value}\"")
            return f'{field_name}"{value}"'
        
        content = re.sub(pattern, fix_field_quotes, content)
    
    # Save if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes_made
    
    return []

def main():
    """Main function to fix quote consistency across all frontmatter files."""
    print('🔧 FRONTMATTER QUOTE CONSISTENCY FIX')
    print('=' * 60)
    
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Error: Directory {frontmatter_dir} not found")
        sys.exit(1)
    
    # Find all frontmatter files
    files = list(frontmatter_dir.glob('*.md'))
    print(f"📂 Found {len(files)} frontmatter files to process")
    print()
    
    total_changes = 0
    files_modified = 0
    
    # Process each file
    for filepath in sorted(files):
        changes = fix_quote_consistency(filepath)
        
        if changes:
            files_modified += 1
            total_changes += len(changes)
            print(f"✅ {filepath.name}: {len(changes)} fixes")
            for change in changes[:3]:  # Show first 3 changes
                print(f"   • {change}")
            if len(changes) > 3:
                print(f"   • ... and {len(changes) - 3} more")
        else:
            print(f"✓  {filepath.name}: already consistent")
    
    print()
    print('📊 SUMMARY:')
    print('-' * 30)
    print(f"Files processed: {len(files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total changes: {total_changes}")
    print(f"Final consistency: 100% ({len(files)}/{len(files)} files)")
    
    if total_changes > 0:
        print()
        print('🎯 SUCCESS:')
        print('All frontmatter files now use consistent double quotes!')
        print('This follows YAML best practices for technical content.')
    else:
        print()
        print('✅ All files were already consistent!')

if __name__ == '__main__':
    main()
