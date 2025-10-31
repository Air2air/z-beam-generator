#!/usr/bin/env python3
"""
Update imports after moving generators, commands, config to /shared

Changes:
1. generators.* → shared.generators.*
2. commands.* → shared.commands.*
3. config.* → shared.config.*
"""

import re
from pathlib import Path

# Define import mappings (order matters - most specific first)
IMPORT_MAPPINGS = [
    # Generators imports
    (r'from generators\.', 'from shared.generators.'),
    (r'import generators\.', 'import shared.generators.'),
    
    # Commands imports
    (r'from commands\.', 'from shared.commands.'),
    (r'import commands\.', 'import shared.commands.'),
    
    # Config imports
    (r'from config\.', 'from shared.config.'),
    (r'import config\.', 'import shared.config.'),
]

def update_file(file_path: Path) -> tuple[bool, int]:
    """Update imports in a single file. Returns (changed, num_changes)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        for old_pattern, new_pattern in IMPORT_MAPPINGS:
            new_content = re.sub(old_pattern, new_pattern, content)
            if new_content != content:
                matches = len(re.findall(old_pattern, content))
                changes += matches
                content = new_content
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        
        return False, 0
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0

def main():
    """Update all Python files in the workspace."""
    print("🔄 Updating imports after moving to /shared...")
    print()
    
    workspace_root = Path(__file__).parent
    
    # Find all Python files (exclude __pycache__, venv, etc.)
    python_files = []
    for path in workspace_root.rglob("*.py"):
        # Skip excluded directories
        if any(part in path.parts for part in ['__pycache__', '.venv', 'venv', 'node_modules', '.git', '.archive']):
            continue
        python_files.append(path)
    
    print(f"📂 Found {len(python_files)} Python files")
    print()
    
    # Update files
    updated_files = []
    total_changes = 0
    
    for file_path in python_files:
        changed, num_changes = update_file(file_path)
        if changed:
            updated_files.append(file_path)
            total_changes += num_changes
            print(f"✅ {file_path.relative_to(workspace_root)} ({num_changes} changes)")
    
    print()
    print("="*80)
    print("✅ Import update complete!")
    print(f"   Updated {len(updated_files)} files")
    print(f"   Made {total_changes} import changes")
    print("="*80)
    
    if updated_files:
        print()
        print("Updated files:")
        for file_path in sorted(updated_files):
            print(f"  • {file_path.relative_to(workspace_root)}")

if __name__ == "__main__":
    main()
