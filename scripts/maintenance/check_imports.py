#!/usr/bin/env python3
"""
Import Organization Checker

This script checks that all Python files in the project follow the standard import order:
1. Standard library imports
2. Third-party imports
3. Local imports

Usage: python3 scripts/maintenance/check_imports.py [--fix]
"""

import argparse
import ast
import os
import re
from pathlib import Path
from typing import List, Tuple


def get_import_lines(file_path: Path) -> List[str]:
    """Extract import lines from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def categorize_imports(import_lines: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """Categorize imports into standard, third-party, and local."""
    stdlib_imports = []
    third_party_imports = []
    local_imports = []

    # Common standard library modules
    stdlib_modules = {
        'abc', 'argparse', 'ast', 'asyncio', 'collections', 'contextlib', 'copy',
        'dataclasses', 'datetime', 'enum', 'functools', 'hashlib', 'heapq', 'inspect',
        'io', 'itertools', 'json', 'logging', 'math', 'os', 'pathlib', 'pickle',
        'platform', 'random', 're', 'shutil', 'socket', 'sqlite3', 'string', 'subprocess',
        'sys', 'tempfile', 'threading', 'time', 'timeit', 'typing', 'unittest', 'urllib',
        'uuid', 'warnings', 'weakref', 'xml', 'zipfile'
    }

    for line in import_lines:
        if line.startswith('import '):
            module = line.split()[1].split('.')[0]
        elif line.startswith('from '):
            module = line.split()[1].split('.')[0]
        else:
            continue

        if module in stdlib_modules:
            stdlib_imports.append(line)
        elif module in ['pytest', 'requests', 'yaml', 'dotenv', 'pathlib']:
            # Known third-party modules
            third_party_imports.append(line)
        else:
            # Assume local import
            local_imports.append(line)

    return stdlib_imports, third_party_imports, local_imports


def check_file_imports(file_path: Path) -> Tuple[bool, str]:
    """Check if a file has properly organized imports."""
    import_lines = get_import_lines(file_path)

    if not import_lines:
        return True, "No imports to check"

    stdlib, third_party, local = categorize_imports(import_lines)

    issues = []

    # Check if imports are in correct order
    expected_order = stdlib + third_party + local
    if import_lines != expected_order:
        issues.append("Imports not in correct order (stdlib → third-party → local)")

    # Check for blank lines between groups
    all_lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
    except Exception:
        return False, "Could not read file"

    # Find import section
    import_start = -1
    import_end = -1

    for i, line in enumerate(all_lines):
        if line.strip().startswith(('import ', 'from ')):
            if import_start == -1:
                import_start = i
            import_end = i

    if import_start >= 0:
        # Check for proper spacing
        if import_end + 1 < len(all_lines) and all_lines[import_end + 1].strip():
            issues.append("Missing blank line after imports")

    if issues:
        return False, "; ".join(issues)

    return True, "Imports properly organized"


def fix_file_imports(file_path: Path) -> bool:
    """Fix import organization in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the AST to preserve formatting
        tree = ast.parse(content)

        # Extract import statements
        import_lines = get_import_lines(file_path)
        if not import_lines:
            return True

        stdlib, third_party, local = categorize_imports(import_lines)

        # Create properly ordered imports
        new_imports = []
        if stdlib:
            new_imports.extend(stdlib)
            new_imports.append("")
        if third_party:
            new_imports.extend(third_party)
            new_imports.append("")
        if local:
            new_imports.extend(local)
            new_imports.append("")

        # Replace import section in content
        lines = content.split('\n')
        import_start = -1
        import_end = -1

        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                if import_start == -1:
                    import_start = i
                import_end = i

        if import_start >= 0:
            # Replace import section
            before_imports = lines[:import_start]
            after_imports = lines[import_end + 1:]

            new_content = '\n'.join(before_imports + new_imports + after_imports)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

    return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check and fix Python import organization")
    parser.add_argument("--fix", action="store_true", help="Automatically fix import issues")
    parser.add_argument("--path", default=".", help="Path to check (default: current directory)")
    args = parser.parse_args()

    project_root = Path(args.path)

    # Find all Python files
    python_files = []
    for ext in ['*.py']:
        python_files.extend(project_root.rglob(ext))

    # Exclude certain directories
    exclude_patterns = ['__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules']
    filtered_files = []

    for file_path in python_files:
        if not any(pattern in str(file_path) for pattern in exclude_patterns):
            filtered_files.append(file_path)

    total_files = len(filtered_files)
    files_with_issues = 0
    files_fixed = 0

    print(f"Checking {total_files} Python files...")

    for file_path in filtered_files:
        is_valid, message = check_file_imports(file_path)

        if not is_valid:
            files_with_issues += 1
            print(f"❌ {file_path.relative_to(project_root)}: {message}")

            if args.fix:
                if fix_file_imports(file_path):
                    files_fixed += 1
                    print(f"✅ Fixed {file_path.relative_to(project_root)}")
                else:
                    print(f"❌ Failed to fix {file_path.relative_to(project_root)}")

    print(f"\nSummary:")
    print(f"Total files checked: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    if args.fix:
        print(f"Files fixed: {files_fixed}")

    if files_with_issues == 0:
        print("🎉 All files have properly organized imports!")
        return 0
    else:
        print("⚠️  Some files have import organization issues")
        return 1


if __name__ == "__main__":
    exit(main())
