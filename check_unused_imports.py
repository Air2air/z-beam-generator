#!/usr/bin/env python3
"""
Comprehensive Unused Import Checker for Z-Beam Generator
Analyzes all Python files to find unused imports across the entire codebase.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class UnusedImportChecker:
    def __init__(self, root_directory: str):
        self.root_directory = Path(root_directory)
        self.issues = []
        self.files_processed = 0
        self.files_with_issues = 0
        
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        for file_path in self.root_directory.rglob("*.py"):
            # Skip certain directories
            if any(part in str(file_path) for part in [
                '__pycache__', '.git', 'venv', 'env', 
                'node_modules', '.pytest_cache'
            ]):
                continue
            python_files.append(file_path)
        return python_files
    
    def parse_file(self, file_path: Path) -> Tuple[ast.AST, str]:
        """Parse a Python file and return the AST and content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            return tree, content
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None, None
    
    def extract_imports(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Extract all imports from an AST."""
        imports = {
            'modules': [],  # import module
            'from_imports': [],  # from module import name
            'aliases': []  # import module as alias, from module import name as alias
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        imports['aliases'].append(alias.asname)
                    else:
                        imports['modules'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.asname:
                        imports['aliases'].append(alias.asname)
                    else:
                        imports['from_imports'].append(alias.name)
        
        return imports
    
    def find_usage_in_content(self, content: str, name: str) -> bool:
        """Check if an imported name is used in the file content."""
        # Remove import statements from content for checking usage
        lines = content.split('\n')
        content_without_imports = []
        
        for line in lines:
            stripped = line.strip()
            if (not stripped.startswith('import ') and 
                not stripped.startswith('from ') and
                not (stripped.startswith('#') and ('import' in stripped))):
                content_without_imports.append(line)
        
        search_content = '\n'.join(content_without_imports)
        
        # Check for direct usage
        if name in search_content:
            # More sophisticated check - ensure it's not just in comments/strings
            # Look for word boundaries
            import re
            pattern = r'\b' + re.escape(name) + r'\b'
            if re.search(pattern, search_content):
                return True
        
        return False
    
    def check_file_imports(self, file_path: Path) -> List[Dict]:
        """Check a single file for unused imports."""
        tree, content = self.parse_file(file_path)
        if not tree or not content:
            return []
        
        imports = self.extract_imports(tree)
        unused_imports = []
        
        # Check each type of import
        all_imported_names = (
            imports['modules'] + 
            imports['from_imports'] + 
            imports['aliases']
        )
        
        for name in all_imported_names:
            # Skip common exceptions that might be used indirectly
            if name in ['__future__', 'annotations']:
                continue
                
            # Handle module imports (check if any part is used)
            if '.' in name:
                # For imports like 'os.path', check if 'os' is used
                base_name = name.split('.')[0]
                if not self.find_usage_in_content(content, base_name):
                    unused_imports.append({
                        'name': name,
                        'type': 'module',
                        'line': self.find_import_line(content, name)
                    })
            else:
                if not self.find_usage_in_content(content, name):
                    unused_imports.append({
                        'name': name,
                        'type': 'import',
                        'line': self.find_import_line(content, name)
                    })
        
        return unused_imports
    
    def find_import_line(self, content: str, name: str) -> int:
        """Find the line number where an import occurs."""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if (f'import {name}' in line or 
                f'from {name}' in line or
                f'{name},' in line or
                line.strip().endswith(name)):
                return i
        return 0
    
    def check_all_files(self) -> Dict:
        """Check all Python files for unused imports."""
        python_files = self.find_python_files()
        print(f"🔍 Checking {len(python_files)} Python files for unused imports...")
        
        results = {}
        files_with_issues = 0
        total_unused = 0
        
        for file_path in python_files:
            self.files_processed += 1
            relative_path = file_path.relative_to(self.root_directory)
            
            unused_imports = self.check_file_imports(file_path)
            
            if unused_imports:
                results[str(relative_path)] = unused_imports
                files_with_issues += 1
                total_unused += len(unused_imports)
                print(f"  📁 {relative_path}: {len(unused_imports)} unused imports")
        
        self.files_with_issues = files_with_issues
        
        print("\n📊 Summary:")
        print(f"  📁 Files processed: {len(python_files)}")
        print(f"  ⚠️  Files with unused imports: {files_with_issues}")
        print(f"  🗑️  Total unused imports: {total_unused}")
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate a detailed report of unused imports."""
        if not results:
            return "✅ No unused imports found in the codebase!"
        
        report = ["🔍 UNUSED IMPORTS REPORT", "=" * 50, ""]
        
        for file_path, unused_imports in results.items():
            report.append(f"📁 {file_path}")
            report.append("-" * len(f"📁 {file_path}"))
            
            for import_info in unused_imports:
                line_info = f" (line {import_info['line']})" if import_info['line'] else ""
                report.append(f"  🗑️  {import_info['name']}{line_info}")
            
            report.append("")
        
        report.extend([
            "🔧 RECOMMENDATIONS:",
            "=" * 20,
            "1. Remove unused imports to reduce file size and improve readability",
            "2. Consider using tools like 'autoflake' or 'isort' for automatic cleanup",
            "3. Review imports that might be used in eval() or exec() calls",
            "4. Check for imports used only in type hints (consider TYPE_CHECKING)",
            ""
        ])
        
        return "\n".join(report)


def main():
    """Main function to run the unused import checker."""
    # Use current directory as root
    root_dir = os.getcwd()
    
    print("🚀 Z-Beam Generator Unused Import Checker")
    print("=" * 50)
    print(f"📂 Scanning directory: {root_dir}")
    print()
    
    checker = UnusedImportChecker(root_dir)
    results = checker.check_all_files()
    
    # Generate and display report
    report = checker.generate_report(results)
    print(report)
    
    # Save report to file
    report_file = "unused_imports_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Detailed report saved to: {report_file}")
    
    # Return exit code based on results
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())