#!/usr/bin/env python3
"""
Simple Frontmatter Quote Fix Script
"""

import re
from pathlib import Path

def fix_quotes_in_file(filepath):
    """Fix single quotes to double quotes in a frontmatter file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix metric: 'value' → metric: "value"
    content = re.sub(r"(metric:\s*)'([^']*)'", r'\1"\2"', content)
    
    # Fix - result: 'value' → - result: "value"  
    content = re.sub(r"(- result:\s*)'([^']*)'", r'\1"\2"', content)
    
    # Check if changes were made
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print('🔧 FIXING FRONTMATTER QUOTES')
    print('=' * 40)
    
    frontmatter_dir = Path('content/components/frontmatter')
    files = list(frontmatter_dir.glob('*.md'))
    
    fixed_count = 0
    
    for filepath in sorted(files):
        if fix_quotes_in_file(filepath):
            fixed_count += 1
            print(f"✅ Fixed: {filepath.name}")
        else:
            print(f"✓  OK: {filepath.name}")
    
    print(f"\n📊 Fixed {fixed_count} files out of {len(files)}")

if __name__ == '__main__':
    main()
