#!/usr/bin/env python3
"""
Update propertiestable files with new shorter labels
"""

import os
from pathlib import Path

import glob



def update_propertiestable_files():
    """Update all propertiestable files with new labels"""

    # Directory containing the files
    properties_dir = Path("content/components/propertiestable")

    # Label mappings (old -> new)
    label_mappings = {
        "| Chemical Formula |": "| Formula |",
        "| Material Symbol |": "| Symbol |",
        "| Material Type |": "| Material |",
        "| Tensile Strength |": "| Tensile |",
        "| Thermal Conductivity |": "| Thermal |",
    }

    print("🔄 Updating propertiestable files with new labels...")

    # Find all markdown files
    files = list(properties_dir.glob("*.md"))
    updated_count = 0

    for file_path in files:
        try:
            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Apply label mappings
            original_content = content
            for old_label, new_label in label_mappings.items():
                content = content.replace(old_label, new_label)

            # Write back only if changes were made
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                updated_count += 1
                print(f"  ✅ Updated: {file_path.name}")

        except Exception as e:
            print(f"  ❌ Error updating {file_path.name}: {e}")

    print(f"📊 Updated {updated_count} propertiestable files with new labels")
    print("🎉 All propertiestable files now use shorter, cleaner labels!")


if __name__ == "__main__":
    update_propertiestable_files()
