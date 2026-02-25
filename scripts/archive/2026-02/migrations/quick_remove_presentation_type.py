#!/usr/bin/env python3
"""
Quick script to remove presentation_type lines from YAML files.
"""

from pathlib import Path
import re

def remove_lines(file_path: Path) -> int:
    """Remove presentation_type lines from a file."""
    if not file_path.exists():
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    removed = 0
    new_lines = []
    
    for line in lines:
        # Match lines with presentation_type
        if re.match(r'^\s*presentation_type:\s+\w+\s*$', line):
            removed += 1
            print(f"  Removed from {file_path.name}: {line.strip()}")
        else:
            new_lines.append(line)
    
    if removed > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    return removed

# Process files
base = Path('/Users/todddunning/Desktop/Z-Beam/z-beam-generator')
files = [
    base / 'data/materials/Materials.yaml',
    base / 'data/compounds/Compounds.yaml',
    base / 'data/settings/Settings.yaml',
    base / 'data/contaminants/Contaminants.yaml',
]

total = 0
for f in files:
    if f.exists():
        print(f"\n📄 {f.name}")
        count = remove_lines(f)
        print(f"  ✅ Removed {count} lines")
        total += count

print(f"\n📊 Total removed: {total}")
