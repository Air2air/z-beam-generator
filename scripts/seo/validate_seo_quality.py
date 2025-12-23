#!/usr/bin/env python3
"""
SEO Quality Validator

Validates generated page_title and meta_description meet spec requirements:
- Title: 50-55 characters
- Description: 155-160 characters
- Contains specific metrics (%, nm, W)
- No forbidden phrases

Usage:
    # Validate all materials
    python3 scripts/seo/validate_seo_quality.py
    
    # Validate specific materials
    python3 scripts/seo/validate_seo_quality.py --materials "aluminum-laser-cleaning,steel-laser-cleaning"
"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
import argparse


FORBIDDEN_PHRASES = [
    'complete guide',
    'comprehensive',
    'various uses',
    'optimized parameters',
    'effective cleaning',
    'industrial applications'
]

REQUIRED_PATTERNS = {
    'percentage': r'\d+%',
    'wavelength': r'\d+nm',
    'power': r'\d+-?\d*W'
}


def validate_title(title: str, material_name: str):
    """Validate page title meets requirements."""
    issues = []
    
    # Check length
    length = len(title)
    if length < 50:
        issues.append(f"Too short: {length} chars (need 50-55)")
    elif length > 55:
        issues.append(f"Too long: {length} chars (need 50-55)")
    
    # Check forbidden phrases
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in title.lower():
            issues.append(f"Contains forbidden phrase: '{phrase}'")
    
    return issues


def validate_description(description: str, material_name: str):
    """Validate meta description meets requirements."""
    issues = []
    
    # Check length
    length = len(description)
    if length < 155:
        issues.append(f"Too short: {length} chars (need 155-160)")
    elif length > 160:
        issues.append(f"Too long: {length} chars (need 155-160)")
    
    # Check for specific metrics
    for metric, pattern in REQUIRED_PATTERNS.items():
        if not re.search(pattern, description):
            issues.append(f"Missing {metric} (pattern: {pattern})")
    
    # Check forbidden phrases
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in description.lower():
            issues.append(f"Contains forbidden phrase: '{phrase}'")
    
    return issues


def validate_material(material_id: str, material_data: dict):
    """Validate SEO for a single material."""
    results = {
        'material_id': material_id,
        'has_title': False,
        'has_description': False,
        'title_issues': [],
        'description_issues': [],
        'passed': False
    }
    
    material_name = material_data.get('name', material_id)
    
    # Check page_title
    if 'page_title' in material_data:
        results['has_title'] = True
        title = material_data['page_title']
        results['title_length'] = len(title)
        results['title_issues'] = validate_title(title, material_name)
    else:
        results['title_issues'] = ['Missing page_title field']
    
    # Check meta_description
    if 'meta_description' in material_data:
        results['has_description'] = True
        description = material_data['meta_description']
        results['description_length'] = len(description)
        results['description_issues'] = validate_description(description, material_name)
    else:
        results['description_issues'] = ['Missing meta_description field']
    
    # Overall pass/fail
    results['passed'] = (
        results['has_title'] and
        results['has_description'] and
        len(results['title_issues']) == 0 and
        len(results['description_issues']) == 0
    )
    
    return results


def main():
    """Main validation process."""
    parser = argparse.ArgumentParser(description='Validate SEO metadata quality')
    parser.add_argument('--materials', help='Comma-separated list of material IDs')
    parser.add_argument('--verbose', action='store_true', help='Show details for passing materials too')
    args = parser.parse_args()
    
    print("="*80)
    print("🔍 SEO QUALITY VALIDATION")
    print("="*80)
    
    # Load materials data
    materials_path = project_root / 'data' / 'materials' / 'Materials.yaml'
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials_data = data['materials']
    
    # Filter materials if specified
    if args.materials:
        material_ids = [m.strip() for m in args.materials.split(',')]
    else:
        material_ids = list(materials_data.keys())
    
    print(f"\n📋 Validating {len(material_ids)} materials...\n")
    
    # Validate each material
    results = []
    for material_id in material_ids:
        if material_id not in materials_data:
            print(f"⚠️  {material_id}: NOT FOUND in Materials.yaml")
            continue
        
        result = validate_material(material_id, materials_data[material_id])
        results.append(result)
        
        # Print results
        if not result['passed'] or args.verbose:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {material_id}")
            
            if result['has_title']:
                print(f"   Title: {result['title_length']} chars", end="")
                if result['title_issues']:
                    print(f" - {', '.join(result['title_issues'])}")
                else:
                    print(" ✅")
            else:
                print(f"   Title: MISSING")
            
            if result['has_description']:
                print(f"   Description: {result['description_length']} chars", end="")
                if result['description_issues']:
                    print(f" - {', '.join(result['description_issues'])}")
                else:
                    print(" ✅")
            else:
                print(f"   Description: MISSING")
            
            print()
    
    # Summary
    passed = sum(1 for r in results if r['passed'])
    failed = len(results) - passed
    
    print("="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    print(f"❌ Failed: {failed}/{len(results)} ({failed/len(results)*100:.1f}%)")
    
    # Breakdown
    has_title = sum(1 for r in results if r['has_title'])
    has_desc = sum(1 for r in results if r['has_description'])
    
    print(f"\n📈 Coverage:")
    print(f"   page_title: {has_title}/{len(results)} ({has_title/len(results)*100:.1f}%)")
    print(f"   meta_description: {has_desc}/{len(results)} ({has_desc/len(results)*100:.1f}%)")
    
    print("="*80)
    
    return 0 if passed == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
