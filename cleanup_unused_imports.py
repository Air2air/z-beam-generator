#!/usr/bin/env python3
"""
Automated Unused Import Cleanup for Z-Beam Generator
Automatically removes common unused imports from Python files.
"""

import os
import re
import sys
from pathlib        print("\n📊 Cleanup Summary:")import Path
from typing import List, Dict

class ImportCleanup:
    def __init__(self, root_directory: str):
        self.root_directory = Path(root_directory)
        self.cleaned_files = []
        self.skipped_files = []
        
        # Common unused imports to auto-remove (be conservative)
        self.safe_removals = {
            'import os',
            'import sys', 
            'import json',
            'import re',
            'from pathlib import Path',
            'from typing import List',
            'from typing import Dict', 
            'from typing import Any',
            'from typing import Optional',
            'from typing import Tuple',
            'from typing import Set',
            'from collections import Counter',
            'from collections import defaultdict',
            'import logging',
            'import datetime',
            'from datetime import datetime',
            'from datetime import timedelta',
            'import unittest',
            'import tempfile',
            'import shutil',
            'import yaml',
            'import glob'
        }
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        for file_path in self.root_directory.rglob("*.py"):
            # Skip certain directories and files
            if any(part in str(file_path) for part in [
                '__pycache__', '.git', 'venv', 'env', 
                'node_modules', '.pytest_cache',
                'check_unused_imports.py',  # Skip our checker script
                'cleanup_unused_imports.py'  # Skip this script
            ]):
                continue
            python_files.append(file_path)
        return python_files
    
    def is_import_used(self, file_content: str, import_line: str) -> bool:
        """Check if an import is actually used in the file."""
        # Extract the imported name(s)
        imported_names = self.extract_imported_names(import_line)
        
        # Remove import statements from content for checking
        content_lines = file_content.split('\n')
        content_without_imports = []
        
        for line in content_lines:
            stripped = line.strip()
            if (not stripped.startswith('import ') and 
                not stripped.startswith('from ') and
                not (stripped.startswith('#') and ('import' in stripped))):
                content_without_imports.append(line)
        
        search_content = '\n'.join(content_without_imports)
        
        # Check if any imported name is used
        for name in imported_names:
            if name in search_content:
                # Use word boundary check
                pattern = r'\b' + re.escape(name) + r'\b'
                if re.search(pattern, search_content):
                    return True
        
        return False
    
    def extract_imported_names(self, import_line: str) -> List[str]:
        """Extract the names being imported from an import statement."""
        import_line = import_line.strip()
        names = []
        
        if import_line.startswith('import '):
            # Handle "import module" or "import module as alias"
            parts = import_line[7:].split(' as ')
            if len(parts) > 1:
                names.append(parts[1].strip())
            else:
                module_name = parts[0].strip()
                # For "import os.path", we check for "os"
                if '.' in module_name:
                    names.append(module_name.split('.')[0])
                else:
                    names.append(module_name)
        
        elif import_line.startswith('from '):
            # Handle "from module import name" or "from module import name as alias"
            try:
                parts = import_line.split(' import ')
                if len(parts) == 2:
                    import_part = parts[1]
                    # Handle multiple imports: "from module import a, b, c"
                    if ',' in import_part:
                        for item in import_part.split(','):
                            item = item.strip()
                            if ' as ' in item:
                                names.append(item.split(' as ')[1].strip())
                            else:
                                names.append(item)
                    else:
                        # Single import
                        if ' as ' in import_part:
                            names.append(import_part.split(' as ')[1].strip())
                        else:
                            names.append(import_part.strip())
            except IndexError:
                pass
        
        return names
    
    def clean_file(self, file_path: Path) -> bool:
        """Clean unused imports from a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            cleaned_lines = []
            removed_imports = []
            
            for line in lines:
                stripped = line.strip()
                
                # Check if this is an import line we should consider removing
                is_import_line = (stripped.startswith('import ') or 
                                stripped.startswith('from '))
                
                if is_import_line:
                    # Only auto-remove if it's in our safe list and unused
                    if any(safe_import in stripped for safe_import in self.safe_removals):
                        if not self.is_import_used(content, stripped):
                            removed_imports.append(stripped)
                            continue  # Skip this line (remove the import)
                
                cleaned_lines.append(line)
            
            if removed_imports:
                # Write the cleaned content back to file
                new_content = '\n'.join(cleaned_lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.cleaned_files.append({
                    'file': file_path,
                    'removed': removed_imports
                })
                return True
            else:
                self.skipped_files.append(file_path)
                return False
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def clean_all_files(self) -> Dict:
        """Clean all Python files in the project."""
        python_files = self.find_python_files()
        print(f"🧹 Cleaning unused imports from {len(python_files)} Python files...")
        
        total_files_cleaned = 0
        total_imports_removed = 0
        
        for file_path in python_files:
            if self.clean_file(file_path):
                total_files_cleaned += 1
                removed_count = len(self.cleaned_files[-1]['removed'])
                total_imports_removed += removed_count
                relative_path = file_path.relative_to(self.root_directory)
                print(f"  ✅ {relative_path}: removed {removed_count} unused imports")
        
        print(f"\\n📊 Cleanup Summary:")
        print(f"  📁 Files processed: {len(python_files)}")
        print(f"  🧹 Files cleaned: {total_files_cleaned}")
        print(f"  🗑️  Total imports removed: {total_imports_removed}")
        
        return {
            'files_processed': len(python_files),
            'files_cleaned': total_files_cleaned,
            'imports_removed': total_imports_removed,
            'cleaned_files': self.cleaned_files
        }
    
    def generate_report(self, results: Dict) -> str:
        """Generate a detailed cleanup report."""
        if not results['cleaned_files']:
            return "✅ No unused imports found to clean up!"
        
        report = ["🧹 IMPORT CLEANUP REPORT", "=" * 50, ""]
        
        for file_info in results['cleaned_files']:
            file_path = file_info['file'].relative_to(self.root_directory)
            removed_imports = file_info['removed']
            
            report.append(f"📁 {file_path}")
            report.append("-" * len(f"📁 {file_path}"))
            
            for import_line in removed_imports:
                report.append(f"  🗑️  {import_line}")
            
            report.append("")
        
        report.extend([
            f"📊 Summary: {results['imports_removed']} imports removed from {results['files_cleaned']} files",
            "",
            "✅ Cleanup completed! Files have been automatically cleaned."
        ])
        
        return "\\n".join(report)


def main():
    """Main function to run the import cleanup."""
    root_dir = os.getcwd()
    
    print("🧹 Z-Beam Generator Automated Import Cleanup")
    print("=" * 50)
    print(f"📂 Cleaning directory: {root_dir}")
    print("⚠️  This will modify files - make sure you have backups!")
    print()
    
    # Ask for confirmation
    response = input("Continue with cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("Cleanup cancelled.")
        return 0
    
    cleanup = ImportCleanup(root_dir)
    results = cleanup.clean_all_files()
    
    # Generate and display report
    report = cleanup.generate_report(results)
    print(report)
    
    # Save report to file
    report_file = "import_cleanup_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\\n📄 Detailed report saved to: {report_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())