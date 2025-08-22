#!/usr/bin/env python3
"""
Manual Post-Processing Script for Z-Beam Generator

Usage:
  python3 manual_postprocess.py [material_name] [component_type]
  python3 manual_postprocess.py --file [file_path] [component_type]
  python3 manual_postprocess.py --check [material_name]

Examples:
  python3 manual_postprocess.py Porcelain frontmatter
  python3 manual_postprocess.py --file content/components/frontmatter/copper-laser-cleaning.md frontmatter
  python3 manual_postprocess.py --check Porcelain
"""

import sys
import argparse
from pathlib import Path
from validators.centralized_validator import CentralizedValidator

def main():
    parser = argparse.ArgumentParser(description="Manual post-processing for Z-Beam components")
    parser.add_argument('--file', help='Process specific file path')
    parser.add_argument('--check', help='Check validation status only')
    parser.add_argument('material', nargs='?', help='Material name (e.g., Porcelain)')
    parser.add_argument('component', nargs='?', help='Component type (e.g., frontmatter)')
    
    args = parser.parse_args()
    
    validator = CentralizedValidator()
    
    # Check status only
    if args.check:
        print(f"🔍 CHECKING VALIDATION STATUS FOR: {args.check}")
        print("=" * 50)
        results = validator.validate_material(args.check)
        for component_type, result in results.items():
            print(f"\n{component_type.upper()}:")
            print(f"  Status: {result.status}")
            print(f"  Errors: {len(result.errors)}")
            if result.errors:
                for i, error in enumerate(result.errors, 1):
                    print(f"  {i}. {error}")
        return
    
    # Process specific file
    if args.file:
        if not args.component:
            print("❌ Component type required when using --file")
            return
        
        print(f"🔧 MANUAL POST-PROCESSING: {args.file}")
        print("=" * 50)
        
        # Step 1: Post-processing cleanup
        print("\n1. Applying post-processing cleanup...")
        post_processed = validator.post_process_generated_content(args.file, args.component)
        print(f"   Post-processing applied: {post_processed}")
        
        # Step 2: Show final status
        material_name = Path(args.file).parent.name.replace('-', ' ').title()
        results = validator.validate_material(material_name)
        if args.component in results:
            result = results[args.component]
            print(f"\n2. Final status: {result.status}")
            print(f"   Errors: {len(result.errors)}")
            if result.errors:
                for i, error in enumerate(result.errors, 1):
                    print(f"   {i}. {error}")
        return
    
    # Process material + component
    if not args.material or not args.component:
        print("❌ Material name and component type required")
        print("Usage: python3 manual_postprocess.py [material] [component]")
        print("Example: python3 manual_postprocess.py Porcelain frontmatter")
        return
    
    print(f"🔧 MANUAL POST-PROCESSING: {args.material} {args.component}")
    print("=" * 50)
    
    # Step 1: Check current status
    print(f"\n1. Current status:")
    results = validator.validate_material(args.material)
    if args.component in results:
        result = results[args.component]
        print(f"   Status: {result.status}")
        print(f"   Errors: {len(result.errors)}")
    
    # Step 2: Apply post-processing + validation
    print(f"\n2. Applying post-processing and auto-fixes...")
    success = validator.validate_and_fix_component_immediately(
        args.material, args.component, max_retries=2, force_fix=True
    )
    print(f"   Success: {success}")
    
    # Step 3: Final status
    print(f"\n3. Final status:")
    results = validator.validate_material(args.material)
    if args.component in results:
        result = results[args.component]
        print(f"   Status: {result.status}")
        print(f"   Errors: {len(result.errors)}")
        if result.errors:
            print("   Remaining errors:")
            for i, error in enumerate(result.errors, 1):
                print(f"   {i}. {error}")
        else:
            print("   ✅ No errors remaining!")

if __name__ == "__main__":
    main()
