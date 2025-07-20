# filepath: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/tools/update_imports.py
"""
Utility script to update import statements across the codebase.
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update import statements in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace imports from components to components
    updated_content = re.sub(
        r'from\s+assembly\.components',
        'from components',
        content
    )
    
    # Replace import components with import components
    updated_content = re.sub(
        r'import\s+assembly\.components',
        'import components',
        updated_content
    )
    
    # Add BaseComponent import if the file uses BaseComponent
    if ('BaseComponent' in updated_content and 
            'from components.base import BaseComponent' not in updated_content and
            'from components import BaseComponent' not in updated_content):
        # Add after other imports
        import_block = re.search(r'((?:from|import)\s+[\w\.]+(?:\s+import\s+[\w\.,\s]+)?\n)+', updated_content)
        if import_block:
            insert_pos = import_block.end()
            updated_content = (
                updated_content[:insert_pos] + 
                'from components.base import BaseComponent\n' + 
                updated_content[insert_pos:]
            )
    
    # Write back to file if changes were made
    if content != updated_content:
        with open(file_path, 'w') as f:
            f.write(updated_content)
        return True
    
    return False

def update_imports_in_directory(directory):
    """Update imports in all Python files in directory."""
    changes = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if update_imports_in_file(file_path):
                    print(f"Updated imports in {file_path}")
                    changes += 1
    
    return changes

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    changes = update_imports_in_directory(project_root)
    print(f"Updated imports in {changes} files")