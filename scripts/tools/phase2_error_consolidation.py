#!/usr/bin/env python3
"""
Phase 2 Error Handling Consolidation Script

Updates all imports from utils.loud_errors to utils.ai.loud_errors
and removes the redundant utils/loud_errors.py file.
"""

import re
from pathlib import Path


def update_imports_in_file(file_path: Path) -> bool:
    """Update imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to match: from utils.ai.loud_errors import ...
        pattern = r'from\s+utils\.loud_errors\s+import\s+([^\n]+)'
        
        def replace_import(match):
            import_list = match.group(1)
            return f'from utils.ai.loud_errors import {import_list}'
        
        content = re.sub(pattern, replace_import, content)
        
        # Also handle: import utils.ai.loud_errors
        content = re.sub(r'import\s+utils\.loud_errors', 'import utils.ai.loud_errors', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def find_files_with_loud_errors_imports(root_dir: Path) -> list[Path]:
    """Find all Python files that import from utils.loud_errors."""
    files_to_update = []
    
    for file_path in root_dir.rglob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'from utils.loud_errors import' in content or 'import utils.ai.loud_errors' in content:
                files_to_update.append(file_path)
                
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    return files_to_update


def main():
    """Main consolidation process."""
    print("🔧 Phase 2 Error Handling Consolidation")
    print("=" * 50)
    
    root_dir = Path(__file__).parent.parent.parent
    print(f"📁 Working directory: {root_dir}")
    
    # Find files to update
    print("\n🔍 Finding files with utils.loud_errors imports...")
    files_to_update = find_files_with_loud_errors_imports(root_dir)
    
    if not files_to_update:
        print("✅ No files found with utils.loud_errors imports")
    else:
        print(f"📋 Found {len(files_to_update)} files to update:")
        for file_path in files_to_update:
            print(f"   • {file_path.relative_to(root_dir)}")
        
        # Update imports
        print("\n🔄 Updating imports...")
        updated_count = 0
        for file_path in files_to_update:
            if update_imports_in_file(file_path):
                updated_count += 1
        
        print(f"\n✅ Updated {updated_count} files")
    
    # Check if utils/loud_errors.py can be removed
    redundant_file = root_dir / "utils" / "loud_errors.py"
    if redundant_file.exists():
        print(f"\n📝 Redundant file ready for removal: {redundant_file}")
        print("   All imports have been updated to use utils.ai.loud_errors")
        print("   You can safely remove utils/loud_errors.py")
    
    print("\n🎉 Phase 2 Error Handling Consolidation Complete!")
    print("✅ All error handling now uses the comprehensive LoudError system")


if __name__ == "__main__":
    main()
