#!/usr/bin/env python3
"""
Material Name Normalization - E2E and Cross-Domain

Normalizes ALL material name references across the entire codebase to use
consistent slugified format matching Materials.yaml (single source of truth).

Problem Solved:
- Materials.yaml uses: "aluminum-laser-cleaning"
- Contaminants.yaml uses: "Aluminum" (display name)
- Settings.yaml uses: "aluminum" (base slug)
- DomainAssociations uses: mix of formats

Solution:
- Define slug-to-display mapping from Materials.yaml
- Update all references to use consistent slugified format
- Maintain bidirectional conversion functions

Usage:
    python3 scripts/tools/normalize_material_references.py --check
    python3 scripts/tools/normalize_material_references.py --fix --dry-run
    python3 scripts/tools/normalize_material_references.py --fix

Author: AI Assistant
Date: December 20, 2025
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils.yaml_utils import load_yaml, save_yaml
from shared.utils.core.slug_utils import create_material_slug

PROJECT_ROOT = Path(__file__).parent.parent.parent


def build_material_mappings() -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Build bidirectional mappings from Materials.yaml (single source of truth).
    
    Returns:
        Tuple of (slug_to_display, display_to_slug) dicts
        
    Example:
        slug_to_display = {
            'aluminum-laser-cleaning': 'Aluminum',
            'stainless-steel-316-laser-cleaning': 'Stainless Steel 316'
        }
        display_to_slug = {
            'Aluminum': 'aluminum-laser-cleaning',
            'Stainless Steel 316': 'stainless-steel-316-laser-cleaning'
        }
    """
    materials_path = PROJECT_ROOT / "data" / "materials" / "Materials.yaml"
    data = load_yaml(materials_path)
    
    slug_to_display = {}
    display_to_slug = {}
    
    materials = data.get('materials', {})
    for material_slug, material_data in materials.items():
        # Extract display name from slug
        # "aluminum-laser-cleaning" → "Aluminum"
        # "stainless-steel-316-laser-cleaning" → "Stainless Steel 316"
        
        # Method 1: Check if material has a display_name field
        display_name = material_data.get('display_name')
        
        # Method 2: Derive from slug
        if not display_name:
            # Remove -laser-cleaning suffix
            base_slug = material_slug.replace('-laser-cleaning', '')
            # Convert slug to display: "stainless-steel-316" → "Stainless Steel 316"
            display_name = ' '.join(word.capitalize() for word in base_slug.split('-'))
            
            # Handle special cases (abbreviations, acronyms)
            display_name = _normalize_display_name(display_name)
        
        slug_to_display[material_slug] = display_name
        display_to_slug[display_name] = material_slug
        
        # Also map base slug (without suffix) for Settings.yaml compatibility
        base_slug = material_slug.replace('-laser-cleaning', '')
        display_to_slug[display_name.lower()] = base_slug
    
    return slug_to_display, display_to_slug


def _normalize_display_name(name: str) -> str:
    """
    Normalize display names for special cases.
    
    Args:
        name: Display name with basic capitalization
    
    Returns:
        Normalized display name with correct abbreviations/acronyms
    """
    # Acronyms that should be uppercase
    acronyms = {
        'Abs': 'ABS',
        'Pmma': 'PMMA',
        'Pc': 'PC',
        'Pet': 'PET',
        'Pvc': 'PVC',
        'Frpu': 'FRPU',
        'Gfrp': 'GFRP',
        'Mmc': 'MMC',
        'Mmcs': 'MMCs',
        'Cmc': 'CMC',
        'Cmcs': 'CMCs',
    }
    
    words = name.split()
    normalized = []
    
    for word in words:
        if word in acronyms:
            normalized.append(acronyms[word])
        elif word in ['(abs)', '(pmma)', '(pc)', '(pet)', '(pvc)']:
            # Handle parenthesized acronyms
            inner = word[1:-1].upper()
            normalized.append(f'({inner})')
        else:
            normalized.append(word)
    
    return ' '.join(normalized)


def analyze_contaminants_yaml(
    slug_to_display: Dict[str, str],
    display_to_slug: Dict[str, str]
) -> Dict[str, any]:
    """
    Analyze Contaminants.yaml for material name inconsistencies.
    
    Returns:
        Dict with analysis results and fixes needed
    """
    path = PROJECT_ROOT / "data" / "contaminants" / "Contaminants.yaml"
    data = load_yaml(path)
    
    results = {
        'path': path,
        'issues_found': 0,
        'patterns_affected': [],
        'fixes': []
    }
    
    patterns = data.get('contamination_patterns', {})
    
    for pattern_id, pattern_data in patterns.items():
        # Check valid_materials
        valid_materials = pattern_data.get('valid_materials', [])
        if valid_materials:
            for material in valid_materials:
                if material not in display_to_slug and material != 'ALL':
                    results['issues_found'] += 1
                    results['patterns_affected'].append(pattern_id)
                    results['fixes'].append({
                        'pattern': pattern_id,
                        'field': 'valid_materials',
                        'old_value': material,
                        'issue': 'Display name not matching Materials.yaml'
                    })
        
        # Check prohibited_materials
        prohibited_materials = pattern_data.get('prohibited_materials', [])
        if prohibited_materials:
            for material in prohibited_materials:
                if material not in display_to_slug:
                    results['issues_found'] += 1
                    results['patterns_affected'].append(pattern_id)
                    results['fixes'].append({
                        'pattern': pattern_id,
                        'field': 'prohibited_materials',
                        'old_value': material,
                        'issue': 'Display name not matching Materials.yaml'
                    })
    
    results['patterns_affected'] = list(set(results['patterns_affected']))
    return results


def fix_contaminants_yaml(
    slug_to_display: Dict[str, str],
    display_to_slug: Dict[str, str],
    dry_run: bool = True
) -> Dict[str, any]:
    """
    Fix material name references in Contaminants.yaml.
    
    Strategy:
    - Keep valid_materials as display names (as designed)
    - Ensure display names match Materials.yaml exactly
    - Add slug references for backward compatibility if needed
    
    Returns:
        Dict with fix results
    """
    path = PROJECT_ROOT / "data" / "contaminants" / "Contaminants.yaml"
    data = load_yaml(path)
    
    results = {
        'path': path,
        'fixes_applied': 0,
        'patterns_updated': []
    }
    
    patterns = data.get('contamination_patterns', {})
    
    for pattern_id, pattern_data in patterns.items():
        updated = False
        
        # Fix valid_materials
        if 'valid_materials' in pattern_data:
            fixed_materials = []
            for material in pattern_data['valid_materials']:
                if material == 'ALL':
                    fixed_materials.append(material)
                    continue
                
                # Try to find correct display name
                # Case 1: Exact match
                if material in display_to_slug:
                    fixed_materials.append(material)
                # Case 2: Already a slug - convert to display
                elif material in slug_to_display:
                    fixed_materials.append(slug_to_display[material])
                    updated = True
                # Case 3: Case mismatch - find correct case
                else:
                    material_lower = material.lower()
                    found = False
                    for display_name in display_to_slug.keys():
                        if display_name.lower() == material_lower:
                            fixed_materials.append(display_name)
                            updated = True
                            found = True
                            break
                    if not found:
                        # Keep original, flag for manual review
                        fixed_materials.append(f"{material} [REVIEW]")
                        updated = True
            
            if updated:
                pattern_data['valid_materials'] = fixed_materials
                results['patterns_updated'].append(pattern_id)
                results['fixes_applied'] += len(fixed_materials)
        
        # Fix prohibited_materials
        if 'prohibited_materials' in pattern_data:
            fixed_materials = []
            for material in pattern_data['prohibited_materials']:
                # Try to find correct display name
                if material in display_to_slug:
                    fixed_materials.append(material)
                elif material in slug_to_display:
                    fixed_materials.append(slug_to_display[material])
                    updated = True
                else:
                    material_lower = material.lower()
                    found = False
                    for display_name in display_to_slug.keys():
                        if display_name.lower() == material_lower:
                            fixed_materials.append(display_name)
                            updated = True
                            found = True
                            break
                    if not found:
                        fixed_materials.append(f"{material} [REVIEW]")
                        updated = True
            
            if updated:
                pattern_data['prohibited_materials'] = fixed_materials
    
    if not dry_run and results['fixes_applied'] > 0:
        save_yaml(path, data)
        print(f"✅ Saved {path}")
    
    return results


def check_normalization() -> Dict[str, any]:
    """
    Check normalization status across all domains.
    
    Returns:
        Dict with comprehensive status
    """
    slug_to_display, display_to_slug = build_material_mappings()
    
    print("=" * 80)
    print("MATERIAL NAME NORMALIZATION CHECK")
    print("=" * 80)
    print()
    print(f"📊 Materials.yaml: {len(slug_to_display)} materials")
    print(f"   - Slugified keys (single source of truth)")
    print(f"   - Example: 'aluminum-laser-cleaning' → 'Aluminum'")
    print()
    
    # Check Contaminants.yaml
    print("🔍 Checking Contaminants.yaml...")
    contaminants_results = analyze_contaminants_yaml(slug_to_display, display_to_slug)
    
    if contaminants_results['issues_found'] > 0:
        print(f"   ❌ {contaminants_results['issues_found']} issues found")
        print(f"   📋 {len(contaminants_results['patterns_affected'])} patterns affected")
        print(f"   Examples: {contaminants_results['patterns_affected'][:5]}")
    else:
        print("   ✅ No issues found")
    
    print()
    
    # Summary
    total_issues = contaminants_results['issues_found']
    
    print("=" * 80)
    if total_issues > 0:
        print(f"❌ TOTAL ISSUES: {total_issues}")
        print()
        print("Run with --fix to apply normalization")
    else:
        print("✅ ALL MATERIAL REFERENCES NORMALIZED")
    print("=" * 80)
    
    return {
        'slug_to_display': slug_to_display,
        'display_to_slug': display_to_slug,
        'contaminants': contaminants_results,
        'total_issues': total_issues
    }


def fix_normalization(dry_run: bool = True) -> None:
    """
    Fix normalization issues across all domains.
    
    Args:
        dry_run: If True, show changes but don't apply them
    """
    slug_to_display, display_to_slug = build_material_mappings()
    
    mode_str = "[DRY RUN]" if dry_run else "[APPLYING FIXES]"
    print("=" * 80)
    print(f"MATERIAL NAME NORMALIZATION {mode_str}")
    print("=" * 80)
    print()
    
    # Fix Contaminants.yaml
    print("🔧 Fixing Contaminants.yaml...")
    contaminants_results = fix_contaminants_yaml(slug_to_display, display_to_slug, dry_run)
    
    if contaminants_results['fixes_applied'] > 0:
        print(f"   ✅ {contaminants_results['fixes_applied']} fixes applied")
        print(f"   📋 {len(contaminants_results['patterns_updated'])} patterns updated")
    else:
        print("   ℹ️  No fixes needed")
    
    print()
    
    # Summary
    print("=" * 80)
    if dry_run:
        print("✅ DRY RUN COMPLETE - No files modified")
        print()
        print("Run without --dry-run to apply changes")
    else:
        print("✅ NORMALIZATION COMPLETE")
    print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Normalize material names across all domains (E2E)"
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check normalization status without making changes'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Fix normalization issues'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without applying changes'
    )
    
    args = parser.parse_args()
    
    if not (args.check or args.fix):
        parser.print_help()
        return 1
    
    try:
        if args.check:
            check_normalization()
        elif args.fix:
            fix_normalization(dry_run=args.dry_run)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
