#!/usr/bin/env python3
"""
Migration Script for Z-Beam Generator File Structure

Migrates existing optimized content files to follow the new convention:
Content appears above frontmatter (--- delimiter)
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple


def migrate_file_structure(file_path: str, backup: bool = True) -> Tuple[bool, str]:
    """
    Migrate a file to follow the content-above-frontmatter convention.

    Preserves existing frontmatter and ensures content-first format.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.split("---")

        # Check if already in correct format
        if len(parts) >= 3 and parts[0].strip():
            return True, "File already follows the convention"

        # Check if file has frontmatter but no content above it
        if len(parts) >= 2 and not parts[0].strip():
            # File starts with ---, move content after first --- to the top
            if len(parts) >= 3:  # Need at least 3 parts for frontmatter + content
                # Extract actual content from after the second ---
                content_part = parts[2].strip() if len(parts) > 2 else ""
                frontmatter_part = parts[1].strip() if len(parts) > 1 else ""

                if content_part:
                    # Reconstruct with content first, preserving existing frontmatter
                    new_content = f"{content_part}\n\n---\n{frontmatter_part}\n---"

                    # Create backup if requested
                    backup_path = None
                    if backup:
                        backup_path = f"{file_path}.backup"
                        shutil.copy2(file_path, backup_path)

                    # Write migrated content
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    backup_msg = f" (backup: {backup_path})" if backup_path else ""
                    return (
                        True,
                        f"✅ Migrated: Content moved above frontmatter, existing frontmatter preserved{backup_msg}",
                    )
                else:
                    return False, "No content found after frontmatter to migrate"
            else:
                return False, "File has frontmatter but no content to migrate"

        return False, "File format not recognized for migration"

    except Exception as e:
        return False, f"Error migrating file: {e}"


def migrate_directory(
    directory: str, extensions: List[str] = None, backup: bool = True
) -> None:
    """
    Migrate all files in a directory to follow the new convention.
    """
    if extensions is None:
        extensions = [".md", ".markdown"]

    path = Path(directory)
    if not path.exists():
        print(f"❌ Directory not found: {directory}")
        return

    files_processed = 0
    files_migrated = 0
    files_skipped = 0
    files_failed = 0

    for file_path in path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            files_processed += 1
            success, message = migrate_file_structure(str(file_path), backup)

            if success:
                if "already follows" in message:
                    files_skipped += 1
                    print(f"⏭️  {file_path.relative_to(path)}: {message}")
                else:
                    files_migrated += 1
                    print(f"✅ {file_path.relative_to(path)}: {message}")
            else:
                files_failed += 1
                print(f"❌ {file_path.relative_to(path)}: {message}")

    print(f"\n📊 Migration Summary:")
    print(f"   Files processed: {files_processed}")
    print(f"   Files migrated: {files_migrated}")
    print(f"   Files skipped (already correct): {files_skipped}")
    print(f"   Files failed: {files_failed}")

    if files_failed > 0:
        print(f"\n⚠️  {files_failed} files could not be migrated automatically.")
        print("   Manual review may be required for these files.")
        sys.exit(1)
    else:
        print("\n🎉 Migration completed successfully!")


def main():
    """Main entry point for the migration script."""
    if len(sys.argv) < 2:
        print(
            "Usage: python migrate_structure.py <file_or_directory> [--no-backup] [--extensions .md,.markdown]"
        )
        print("\nExamples:")
        print(
            "  python migrate_structure.py content/components/text/copper-laser-cleaning.md"
        )
        print("  python migrate_structure.py content/ --no-backup")
        print("  python migrate_structure.py content/ --extensions .md")
        sys.exit(1)

    target = sys.argv[1]
    backup = True
    extensions = [".md", ".markdown"]

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--no-backup":
            backup = False
        elif arg.startswith("--extensions"):
            if "=" in arg:
                ext_str = arg.split("=")[1]
            else:
                i += 1
                ext_str = sys.argv[i]
            extensions = [ext.strip() for ext in ext_str.split(",")]
        i += 1

    path = Path(target)

    if path.is_file():
        success, message = migrate_file_structure(target, backup)
        print(f"{'✅' if success else '❌'} {target}: {message}")
        sys.exit(0 if success else 1)
    elif path.is_dir():
        migrate_directory(target, extensions, backup)
    else:
        print(f"❌ Path not found: {target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
