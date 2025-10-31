#!/usr/bin/env python3
"""
Update documentation references after reorganization.

Updates:
1. components/caption → materials/caption
2. components/subtitle → materials/subtitle
3. components/faq → materials/faq
4. /generators → /shared/generators
5. /commands → /shared/commands
6. /config → /shared/config
"""

import re
from pathlib import Path

# Define path mappings for documentation
DOC_PATH_MAPPINGS = [
    # Component paths
    (r'components/caption/generators/', 'materials/caption/generators/'),
    (r'components/subtitle/generators/', 'materials/subtitle/generators/'),
    (r'components/subtitle/core/', 'materials/subtitle/core/'),
    (r'components/faq/generators/', 'materials/faq/generators/'),
    
    # Root directory paths (not in code blocks)
    (r'(?<!`)(/generators)(?![/\w])', r'\1 → /shared/generators'),
    (r'`/generators/', '`/shared/generators/'),
    (r'\b/commands/', '/shared/commands/'),
    (r'\b/config/', '/shared/config/'),
]

def update_file(file_path: Path) -> tuple[bool, int]:
    """Update paths in a documentation file. Returns (changed, num_changes)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        for old_pattern, new_pattern in DOC_PATH_MAPPINGS:
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
    """Update all markdown files in docs/."""
    print("🔄 Updating documentation references...")
    print()
    
    workspace_root = Path(__file__).parent
    docs_dir = workspace_root / "docs"
    
    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))
    
    print(f"📂 Found {len(md_files)} markdown files")
    print()
    
    # Update files
    updated_files = []
    total_changes = 0
    
    for file_path in md_files:
        changed, num_changes = update_file(file_path)
        if changed:
            updated_files.append(file_path)
            total_changes += num_changes
            print(f"✅ {file_path.relative_to(workspace_root)} ({num_changes} changes)")
    
    print()
    print("="*80)
    print("✅ Documentation update complete!")
    print(f"   Updated {len(updated_files)} files")
    print(f"   Made {total_changes} path updates")
    print("="*80)
    
    if updated_files:
        print()
        print("Updated files:")
        for file_path in sorted(updated_files):
            print(f"  • {file_path.relative_to(workspace_root)}")
    
    if len(updated_files) == 0:
        print("\n✨ No documentation updates needed - all paths are current!")

if __name__ == "__main__":
    main()
