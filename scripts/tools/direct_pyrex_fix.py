#!/usr/bin/env python3
"""
Direct YAML Fix - Clean up the current pyrex file for testing
"""

import re
from pathlib import Path

def fix_current_pyrex():
    """Fix the current pyrex file directly for testing"""
    file_path = Path("content/components/frontmatter/pyrex-laser-cleaning.md")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix all the problematic patterns
    content = re.sub(r'"""([^"]*?)"""', r'"\1"', content)  # Triple quotes
    content = re.sub(r'""([^"]*?)""', r'"\1"', content)    # Double quotes
    content = re.sub(r'"\'([^"\']*?)\'"', r'"\1"', content)  # "'value'"
    content = re.sub(r"'([^']*?)'", r'"\1"', content)       # Single quotes
    
    # Fix broken YAML structure lines
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix lines missing colons or proper structure
        if line.strip() and ':' in line:
            # Ensure space after colon
            line = re.sub(r':([^\s])', r': \1', line)
            
            # Fix chemical formulas with unicode issues
            if 'SiOu2082' in line:
                line = line.replace('SiOu2082', 'SiO₂')
                line = line.replace('Bu2082Ou2083', 'B₂O₃') 
                line = line.replace('Nau2082O', 'Na₂O')
                line = line.replace('Alu2082', 'Al₂')
            
            # Fix broken multi-line descriptions
            if line.strip().endswith('"') and not line.strip().startswith('"'):
                continue  # Skip continuation lines for now
                
        fixed_lines.append(line)
    
    # Join and clean up
    content = '\n'.join(fixed_lines)
    
    # Final cleanup
    content = content.replace('  ', ' ')  # Fix double spaces
    content = re.sub(r'\n\s*\n', '\n', content)  # Remove empty lines
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Direct fix applied to pyrex file")

if __name__ == "__main__":
    fix_current_pyrex()
