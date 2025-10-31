#!/usr/bin/env python3
"""
Update imports from shared.utils.loaders.category_loader to materials.category_loader
"""

import re
from pathlib import Path

# Import mappings
IMPORT_MAPPINGS = [
    (r'from shared\.utils\.loaders\.category_loader import', 'from materials.category_loader import'),
    (r'import shared\.utils\.loaders\.category_loader', 'import materials.category_loader'),
]

def update_file_imports(file_path: Path) -> int:
    """Update imports in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        changes = 0
        
        for pattern, replacement in IMPORT_MAPPINGS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes += len(re.findall(pattern, content))
                content = new_content
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ {file_path.relative_to(Path.cwd())} ({changes} changes)")
            return changes
        
        return 0
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return 0

def main():
    """Update all Python files with new import paths."""
    print("🔄 Updating category_loader imports to materials.category_loader...\n")
    
    root = Path.cwd()
    python_files = list(root.rglob("*.py"))
    print(f"📂 Found {len(python_files)} Python files\n")
    
    total_changes = 0
    updated_files = []
    
    for py_file in python_files:
        # Skip this script itself
        if py_file.name == "update_category_loader_imports.py":
            continue
            
        changes = update_file_imports(py_file)
        if changes > 0:
            updated_files.append(py_file.relative_to(root))
            total_changes += changes
    
    print("\n" + "="*80)
    print("✅ Category loader import update complete!")
    print(f"   Updated {len(updated_files)} files")
    print(f"   Made {total_changes} import changes")
    print("="*80)
    
    if updated_files:
        print("\nUpdated files:")
        for file_path in sorted(updated_files):
            print(f"  • {file_path}")

if __name__ == "__main__":
    main()
