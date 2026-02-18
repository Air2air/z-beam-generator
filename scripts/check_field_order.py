#!/usr/bin/env python3
"""
Check field order normalization across all frontmatter domains.

Usage:
    python3 scripts/check_field_order.py
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.validation.field_order import FrontmatterFieldOrderValidator


def main():
    """Check field order for all domains."""
    print("=" * 80)
    print("FRONTMATTER FIELD ORDER VALIDATION")
    print("=" * 80)
    print()
    
    # Point to z-beam frontmatter directory
    frontmatter_dir = Path(__file__).parent.parent.parent / 'z-beam' / 'frontmatter'
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        print()
        print("Note: This script checks the z-beam/frontmatter directory.")
        print("If frontmatter is elsewhere, update the path in the script.")
        return 1
    
    print(f"Checking: {frontmatter_dir}")
    print()
    
    validator = FrontmatterFieldOrderValidator()
    validator.frontmatter_dir = frontmatter_dir  # Override default
    validator.load_schema()
    
    domains = ['materials', 'contaminants', 'compounds', 'settings', 'applications']
    
    total_valid = 0
    total_files = 0
    all_valid = True
    
    for domain in domains:
        print(f"Checking {domain}...")
        results = validator.validate_domain(domain)
        
        valid_count = results.get('valid', 0)
        total_count = results.get('total', 0)
        files_with_issues = results.get('files_with_issues', [])
        
        total_valid += valid_count
        total_files += total_count
        
        if valid_count == total_count:
            print(f"  ✅ {domain}: {valid_count}/{total_count} valid")
        else:
            print(f"  ❌ {domain}: {valid_count}/{total_count} valid")
            all_valid = False
            if files_with_issues:
                print(f"     Files with issues ({len(files_with_issues)}):")
                for item in files_with_issues[:5]:  # Show first 5
                    print(f"       - {item['file']}: {len(item['issues'])} issues")
                if len(files_with_issues) > 5:
                    print(f"       ... and {len(files_with_issues) - 5} more")
        print()
    
    print("=" * 80)
    print(f"TOTAL: {total_valid}/{total_files} files valid")
    print("=" * 80)
    
    if all_valid:
        print("✅ All domains have correct field order!")
        return 0
    else:
        print("⚠️  Some files have incorrect field order.")
        print()
        print("To fix, run:")
        print("  python3 scripts/reorder_field_order.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
