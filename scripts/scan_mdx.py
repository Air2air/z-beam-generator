#!/usr/bin/env python3
"""
Test script to validate existing MDX files for Next.js compatibility - scan only.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from generator.modules.mdx_validator import validate_mdx_output


def scan_mdx_files():
    """Scan validation on existing MDX files without fixing."""
    posts_dir = project_root / "app" / "(materials)" / "posts"

    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return

    mdx_files = list(posts_dir.glob("*.mdx"))

    if not mdx_files:
        print("No MDX files found to validate")
        return

    print(f"Scanning {len(mdx_files)} MDX files for issues...")

    total_issues = 0
    files_with_issues = 0

    for mdx_file in mdx_files:
        try:
            with open(mdx_file, "r", encoding="utf-8") as f:
                content = f.read()

            _, issues = validate_mdx_output(content)

            if issues:
                files_with_issues += 1
                total_issues += len(issues)
                print(f"\n📝 {mdx_file.name}: {len(issues)} issues")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print(f"✅ {mdx_file.name}: No issues")

        except Exception as e:
            print(f"❌ Error validating {mdx_file.name}: {e}")

    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {files_with_issues}/{len(mdx_files)} files have issues")
    print(f"Total issues found: {total_issues}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    scan_mdx_files()
