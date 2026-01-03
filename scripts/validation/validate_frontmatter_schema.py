#!/usr/bin/env python3
"""
Frontmatter Schema Validator

Validates all frontmatter files against data/schemas/frontmatter.json to ensure
compliance with naming conventions (page_title, meta_description, page_description).

Usage:
    python3 scripts/validation/validate_frontmatter_schema.py
    python3 scripts/validation/validate_frontmatter_schema.py --domain materials
    python3 scripts/validation/validate_frontmatter_schema.py --strict  # Exit 1 on any error

Exit codes:
    0: All files valid
    1: Validation errors found (in strict mode)
    2: Schema file not found
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from jsonschema import Draft7Validator, ValidationError


def load_schema(schema_path: str) -> Dict:
    """Load JSON schema from file."""
    if not os.path.exists(schema_path):
        print(f"❌ Schema not found: {schema_path}")
        sys.exit(2)
    
    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_file(filepath: str, validator: Draft7Validator) -> Tuple[bool, List[str]]:
    """
    Validate a single frontmatter file.
    
    Returns:
        (is_valid, error_messages)
    """
    try:
        with open(filepath, 'r') as f:
            frontmatter = yaml.safe_load(f)
        
        errors = []
        for error in validator.iter_errors(frontmatter):
            # Format error message
            if error.path:
                path = '.'.join(str(p) for p in error.path)
                msg = f"{path}: {error.message}"
            else:
                msg = error.message
            errors.append(msg)
        
        # Additional checks for forbidden fields
        if 'title' in frontmatter and 'title' not in ['page_title', 'meta_title']:
            # Check if it's at root level (not in nested objects)
            if isinstance(frontmatter.get('title'), str):
                errors.append("FORBIDDEN: 'title' field at root level (use 'page_title')")
        
        if 'description' in frontmatter:
            # Check if it's non-null and at root level
            desc_value = frontmatter.get('description')
            if desc_value is not None and desc_value != '':
                errors.append("FORBIDDEN: 'description' field at root level (use 'meta_description' or 'page_description')")
        
        return len(errors) == 0, errors
    
    except Exception as e:
        return False, [f"Failed to load file: {str(e)}"]


def main():
    parser = argparse.ArgumentParser(description='Validate frontmatter files against schema')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings'],
                        help='Validate specific domain only')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with code 1 if any validation errors found')
    parser.add_argument('--schema', default='data/schemas/frontmatter.json',
                        help='Path to schema file')
    parser.add_argument('--frontmatter-dir', default='../z-beam/frontmatter',
                        help='Path to frontmatter directory')
    args = parser.parse_args()
    
    # Load schema
    schema = load_schema(args.schema)
    validator = Draft7Validator(schema)
    
    print("=" * 80)
    print("FRONTMATTER SCHEMA VALIDATION")
    print("=" * 80)
    print(f"Schema: {args.schema}")
    print(f"Frontmatter: {args.frontmatter_dir}")
    print()
    
    # Determine domains to validate
    if args.domain:
        domains = [args.domain]
    else:
        domains = ['materials', 'contaminants', 'compounds', 'settings']
    
    # Validate each domain
    total_files = 0
    total_passed = 0
    total_failed = 0
    failed_files = []
    
    for domain in domains:
        domain_path = os.path.join(args.frontmatter_dir, domain)
        if not os.path.exists(domain_path):
            print(f"⚠️  {domain.upper()}: Directory not found")
            continue
        
        files = [f for f in os.listdir(domain_path) if f.endswith('.yaml')]
        domain_passed = 0
        domain_failed = 0
        
        print(f"📂 {domain.upper()}: Validating {len(files)} files...")
        
        for filename in files:
            filepath = os.path.join(domain_path, filename)
            is_valid, errors = validate_file(filepath, validator)
            
            total_files += 1
            
            if is_valid:
                domain_passed += 1
                total_passed += 1
            else:
                domain_failed += 1
                total_failed += 1
                failed_files.append((domain, filename, errors))
        
        status = "✅" if domain_failed == 0 else "❌"
        print(f"   {status} Passed: {domain_passed}/{len(files)}")
        if domain_failed > 0:
            print(f"      Failed: {domain_failed}")
        print()
    
    # Print detailed errors
    if failed_files:
        print("=" * 80)
        print("VALIDATION ERRORS:")
        print("-" * 80)
        for domain, filename, errors in failed_files:
            print(f"\n❌ {domain}/{filename}:")
            for error in errors:
                print(f"   • {error}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY:")
    print("-" * 80)
    print(f"Total files: {total_files}")
    print(f"Passed: {total_passed} ({total_passed/total_files*100:.1f}%)")
    print(f"Failed: {total_failed} ({total_failed/total_files*100:.1f}%)")
    print()
    
    if total_failed == 0:
        print("🎉 All frontmatter files comply with schema!")
    else:
        print(f"⚠️  {total_failed} files have validation errors")
        if args.strict:
            print("\n❌ Exiting with error code 1 (strict mode)")
            sys.exit(1)
    
    print("=" * 80)


if __name__ == '__main__':
    main()
