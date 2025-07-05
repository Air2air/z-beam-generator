#!/usr/bin/env python3
"""
Test script to validate existing MDX files for Next.js compatibility.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from generator.modules.mdx_validator import validate_mdx_output


def test_existing_mdx_files():
    """Test validation on existing MDX files."""
    posts_dir = project_root / "app" / "(materials)" / "posts"

    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return

    mdx_files = list(posts_dir.glob("*.mdx"))

    if not mdx_files:
        print("No MDX files found to validate")
        return

    print(f"Found {len(mdx_files)} MDX files to validate")

    for mdx_file in mdx_files:
        print(f"\n{'=' * 60}")
        print(f"Validating: {mdx_file.name}")
        print(f"{'=' * 60}")

        try:
            with open(mdx_file, "r", encoding="utf-8") as f:
                content = f.read()

            validated_content, issues = validate_mdx_output(content)

            if issues:
                print(f"Found {len(issues)} issues:")
                for issue in issues:
                    print(f"  - {issue}")

                # Ask if we should fix the file
                response = (
                    input(f"Fix issues in {mdx_file.name}? (y/n): ").lower().strip()
                )
                if response == "y":
                    with open(mdx_file, "w", encoding="utf-8") as f:
                        f.write(validated_content)
                    print(f"✅ Fixed and saved {mdx_file.name}")
                else:
                    print(f"⏭️  Skipped {mdx_file.name}")
            else:
                print("✅ No issues found")

        except Exception as e:
            print(f"❌ Error validating {mdx_file.name}: {e}")


if __name__ == "__main__":
    test_existing_mdx_files()
