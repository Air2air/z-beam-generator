#!/usr/bin/env python3
"""
Comprehensive YAML Fix for Pyrex Frontmatter
"""

import re
from pathlib import Path

def fix_pyrex_yaml():
    """Fix all YAML syntax issues in the pyrex frontmatter file"""
    file_path = Path("content/components/frontmatter/pyrex-laser-cleaning.md")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix over-quoted patterns like "'"value"'"
    content = re.sub(r':\s*"\'([^"\']+)\'"', r': "\1"', content)
    
    # Fix patterns like "'value'" 
    content = re.sub(r':\s*\'([^\']+)\'', r': "\1"', content)
    
    # Fix unicode escape sequences
    content = content.replace('\\xB0', '°')
    content = content.replace('\\xB7', '·')
    content = content.replace('\\u2082', '₂')
    content = content.replace('\\u2083', '₃')
    content = content.replace('\\u03BC', 'μ')
    content = content.replace('\\u2013', '–')
    
    # Fix over-escaped quotes
    content = re.sub(r'\\"([^"]+)\\"', r'"\1"', content)
    
    # Fix patterns like ""\"text\""
    content = re.sub(r'""\\"([^"]+)\\""', r'"\1"', content)
    
    # Fix broken multi-line strings
    content = re.sub(r':\s*"([^"]*)\n\s*([^"]*)"', r': "\1 \2"', content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed all YAML syntax issues in pyrex file")

if __name__ == "__main__":
    fix_pyrex_yaml()
