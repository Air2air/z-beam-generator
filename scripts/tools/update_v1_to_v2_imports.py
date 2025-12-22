#!/usr/bin/env python3
"""
Update all v1 data loader imports to v2.

Part of cleanup after archiving v1 loaders.
"""

from pathlib import Path
import re

# Find all Python files
root = Path('.')
py_files = [
    p for p in root.rglob('*.py')
    if not any(part.startswith('.') or part == '__pycache__' for part in p.parts)
    and 'scripts/archive' not in str(p)
]

print(f"Found {len(py_files)} Python files to scan")

replacements = {
    'from domains.materials.data_loader_v2 import': 'from domains.materials.data_loader_v2 import',
    'from domains.contaminants.data_loader_v2 import': 'from domains.contaminants.data_loader_v2 import',
    'from domains.settings.data_loader_v2 import': 'from domains.settings.data_loader_v2 import',
}

updated_files = []

for py_file in py_files:
    try:
        content = py_file.read_text(encoding='utf-8')
        modified = False
        
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                modified = True
        
        if modified:
            py_file.write_text(content, encoding='utf-8')
            updated_files.append(py_file)
            print(f"✅ Updated: {py_file}")
    
    except Exception as e:
        print(f"❌ Error updating {py_file}: {e}")

print(f"\n📊 Summary: Updated {len(updated_files)} files")
for f in updated_files:
    print(f"   - {f}")
