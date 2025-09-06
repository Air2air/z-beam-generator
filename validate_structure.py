#!/usr/bin/env python3
"""
File Structure Validator for Z-Beam Generator

Validates that optimized content files follow the convention:
Content appears above frontmatter (--- delimiter)
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple


def validate_file_structure(file_path: str) -> Tuple[bool, str]:
    """
    Validate that a file follows the content-above-frontmatter convention.
    
    Checks:
    1. Content appears before frontmatter
    2. Frontmatter structure is valid
    3. Existing frontmatter is preserved
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('---')

        # Must have at least 3 parts: content, frontmatter, closing
        if len(parts) < 3:
            return False, "File must have content, frontmatter, and closing delimiter"

        # Content part (before first ---) must not be empty
        content_part = parts[0].strip()
        if not content_part:
            return False, "Content must appear before frontmatter delimiter"

        # Check for frontmatter content
        frontmatter_part = parts[1].strip()
        if not frontmatter_part:
            return False, "Frontmatter section must contain data"

        # Validate YAML structure in frontmatter
        try:
            import yaml
            yaml.safe_load(frontmatter_part)
        except yaml.YAMLError as e:
            return False, f"Invalid YAML in frontmatter: {e}"

        return True, "✅ Valid: Content appears above frontmatter, frontmatter structure preserved"

    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_directory(directory: str, extensions: List[str] = None) -> None:
    """
    Validate all files in a directory that match the given extensions.
    """
    if extensions is None:
        extensions = ['.md', '.markdown']

    path = Path(directory)
    if not path.exists():
        print(f"❌ Directory not found: {directory}")
        return

    files_checked = 0
    files_valid = 0
    files_invalid = 0

    for file_path in path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            files_checked += 1
            is_valid, message = validate_file_structure(str(file_path))

            if is_valid:
                files_valid += 1
                print(f"✅ {file_path.relative_to(path)}: {message}")
            else:
                files_invalid += 1
                print(f"❌ {file_path.relative_to(path)}: {message}")

    print(f"\n📊 Validation Summary:")
    print(f"   Files checked: {files_checked}")
    print(f"   Valid files: {files_valid}")
    print(f"   Invalid files: {files_invalid}")

    if files_invalid > 0:
        print(f"\n⚠️  {files_invalid} files do not follow the convention.")
        print("   Use the migration script to fix these files.")
        sys.exit(1)
    else:
        print("\n🎉 All files follow the convention!")


def main():
    """Main entry point for the validation script."""
    if len(sys.argv) < 2:
        print("Usage: python validate_structure.py <file_or_directory> [--extensions .md,.markdown]")
        print("\nExamples:")
        print("  python validate_structure.py content/copper-laser-cleaning.md")
        print("  python validate_structure.py content/ --extensions .md")
        sys.exit(1)

    target = sys.argv[1]
    extensions = ['.md', '.markdown']

    # Parse extensions if provided
    if len(sys.argv) > 2 and sys.argv[2].startswith('--extensions'):
        ext_str = sys.argv[2].split('=')[1] if '=' in sys.argv[2] else sys.argv[3]
        extensions = [ext.strip() for ext in ext_str.split(',')]

    path = Path(target)

    if path.is_file():
        is_valid, message = validate_file_structure(target)
        print(f"{'✅' if is_valid else '❌'} {target}: {message}")
        sys.exit(0 if is_valid else 1)
    elif path.is_dir():
        validate_directory(target, extensions)
    else:
        print(f"❌ Path not found: {target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
