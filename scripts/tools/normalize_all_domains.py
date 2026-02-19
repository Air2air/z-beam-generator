#!/usr/bin/env python3
"""
E2E Domain Normalization - Comprehensive Material Name Consistency

Ensures ALL domains use consistent material references based on Materials.yaml
as the single source of truth. Handles format conversions appropriately for each
domain's requirements.

Naming Conventions by Domain:
- Materials.yaml: aluminum-laser-cleaning (slugified with suffix) - SOURCE OF TRUTH
- Settings.yaml: aluminum-settings (settings slug with suffix)
- Contaminants.yaml: Aluminum (display name) - human-readable
- DomainAssociations.yaml: aluminum (base slug) - for lookups

Usage:
    python3 scripts/tools/normalize_all_domains.py --check
    python3 scripts/tools/normalize_all_domains.py --fix --dry-run
    python3 scripts/tools/normalize_all_domains.py --fix

Author: AI Assistant
Date: December 20, 2025
"""

import argparse
import sys
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils.yaml_utils import load_yaml, save_yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Known exceptions: category names, generic terms, equipment (not specific materials)
KNOWN_EXCEPTIONS = {
    'ALL',  # Special value for universal patterns
    # Category/generic terms
    'Plastics', 'Metals', 'Woods', 'Stones', 'Ceramics', 'Composites',
    'Glass', 'Wood', 'Metal',  # Singular category names
    'Painted Metal', 'Thin Sheet Metal', 'Galvanized Metal',
    'Porous Stone', 'Soft Stone', 'Hard Stone',
    'Synthetic Materials', 'Natural Materials',
    'Thin Plastics', 'Soft Materials', 'Porous Surfaces',
    'Soft Substrates', 'Delicate Substrates', 'Flexible Substrates',
    # Abbreviations
    'HSS', 'PCB', 'ABS', 'PVC',
    # Generic terms
    'Tile', 'Drywall', 'Teflon', 'Cardboard', 'Paper', 'Asphalt', 'Grout',
    'Carbide', 'Quartz',  # Generic material terms
    # Equipment/non-materials
    'Boilers', 'Machinery', 'Transformer Housings', 'Turbine Blades',
    'Electronics', 'Optical Components', 'Steel Pipes', 'Silicon Wafers',
    # Application contexts
    'Food Areas', 'Heated Surfaces', 'Unsealed Areas',
    'Uncontrolled Environments',
    # Composite terms
    'Plastics (ABS)', 'Porous Wood',
    # Material variants/coatings
    'Chrome-Plated Steel', 'Galvanized Steel', 'Nickel-Plated Surfaces',
    'Zinc-Coated Metal', 'Zinc Alloy', 'Wrought Iron', 'Copper-Beryllium Alloy',
    'Carbon Steel',  # Steel variant
    # Plastic types
    'PET', 'PTFE',
}

# Slugified versions for DomainAssociations checks
KNOWN_EXCEPTIONS_SLUGS = {
    exception.lower().replace(' ', '-').replace('(', '').replace(')', '')
    for exception in KNOWN_EXCEPTIONS
}


class MaterialNameMapper:
    """Maps between different material name formats across domains."""
    
    def __init__(self):
        self.full_slug_to_base = {}  # aluminum-laser-cleaning → aluminum
        self.full_slug_to_display = {}  # aluminum-laser-cleaning → Aluminum
        self.display_to_base = {}  # Aluminum → aluminum
        self.base_to_display = {}  # aluminum → Aluminum
        self.display_to_full = {}  # Aluminum → aluminum-laser-cleaning
        self.settings_to_base = {}  # aluminum-settings (or aluminum) → aluminum
        
        self._build_mappings()
    
    def _build_mappings(self):
        """Build all mapping dictionaries from Materials.yaml."""
        materials_path = PROJECT_ROOT / "data" / "materials" / "Materials.yaml"
        data = load_yaml(materials_path)
        
        materials = data.get('materials', {})
        for full_slug in materials.keys():
            # Extract base slug: aluminum-laser-cleaning → aluminum
            base_slug = full_slug.replace('-laser-cleaning', '')
            
            # Derive display name from base slug
            # aluminum → Aluminum
            # stainless-steel-316 → Stainless Steel 316
            display_name = self._slug_to_display(base_slug)
            
            # Build all mappings
            self.full_slug_to_base[full_slug] = base_slug
            self.full_slug_to_display[full_slug] = display_name
            self.display_to_base[display_name] = base_slug
            self.base_to_display[base_slug] = display_name
            self.display_to_full[display_name] = full_slug
            self.settings_to_base[f"{base_slug}-settings"] = base_slug
            self.settings_to_base[base_slug] = base_slug  # Legacy compatibility
            
            # Also handle lowercase display names
            self.display_to_base[display_name.lower()] = base_slug
    
    def _slug_to_display(self, slug: str) -> str:
        """Convert slug to display name."""
        # Split by hyphens
        words = slug.split('-')
        
        # Special handling for acronyms and compounds
        result = []
        for word in words:
            # Check if it's an acronym
            if word.upper() in ['ABS', 'PC', 'PET', 'PVC', 'PMMA', 'FRPU', 'GFRP', 
                               'MMC', 'MMCS', 'CMC', 'CMCS', 'PEEK', 'PLA']:
                result.append(word.upper())
            # Check if it's a Roman numeral or number
            elif word.upper() in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'] or word.isdigit():
                result.append(word.upper() if not word.isdigit() else word)
            # Regular word
            else:
                result.append(word.capitalize())
        
        display = ' '.join(result)
        
        # Handle parentheses: acrylic-pmma → Acrylic (PMMA)
        if '-pmma' in slug or '-abs' in slug or '-pc' in slug:
            parts = display.rsplit(' ', 1)
            if len(parts) == 2:
                display = f"{parts[0]} ({parts[1]})"
        
        return display
    
    def normalize_for_domain(self, value: str, source_domain: str, target_domain: str) -> str:
        """
        Normalize a material reference from one domain format to another.
        
        Args:
            value: Material reference in source format
            source_domain: Domain the value came from (materials/settings/contaminants)
            target_domain: Domain to convert to
        
        Returns:
            Normalized value for target domain
        """
        # Known exceptions are valid everywhere
        if value in KNOWN_EXCEPTIONS:
            return value
        
        # Determine source format
        base_slug = None
        if source_domain == 'materials':
            # aluminum-laser-cleaning
            base_slug = self.full_slug_to_base.get(value)
        elif source_domain == 'settings':
            # aluminum-settings (preferred) or aluminum (legacy)
            base_slug = self.settings_to_base.get(value)
        elif source_domain == 'contaminants':
            # Supports display name, full materials slug, or base slug
            base_slug = self.display_to_base.get(value)
            if not base_slug:
                base_slug = self.display_to_base.get(value.lower())
            if not base_slug and value in self.full_slug_to_base:
                base_slug = self.full_slug_to_base.get(value)
            if not base_slug and value in self.base_to_display:
                base_slug = value
        elif source_domain == 'associations':
            # Could be any format, try to detect
            if value in self.full_slug_to_base:
                base_slug = self.full_slug_to_base[value]
            elif value in self.base_to_display:
                base_slug = value
            else:
                base_slug = self.display_to_base.get(value)
        
        if not base_slug:
            return f"{value} [UNKNOWN]"
        
        # Convert to target format
        if target_domain == 'materials':
            return f"{base_slug}-laser-cleaning"
        elif target_domain == 'settings':
            return f"{base_slug}-settings"
        elif target_domain == 'contaminants':
            return self.base_to_display.get(base_slug, value)
        elif target_domain == 'associations':
            return base_slug
        
        return value


def check_domain_consistency(mapper: MaterialNameMapper) -> Dict[str, any]:
    """Check consistency across all domains."""
    results = {
        'settings': check_settings_consistency(mapper),
        'contaminants': check_contaminants_consistency(mapper),
        'associations': check_associations_consistency(mapper),
        'applications': check_applications_consistency(),
    }
    
    total_issues = sum(r['issues_count'] for r in results.values())
    
    print("=" * 80)
    print("CROSS-DOMAIN MATERIAL NAME CONSISTENCY CHECK")
    print("=" * 80)
    print()
    
    # Materials.yaml (source of truth)
    print(f"📊 Materials.yaml: {len(mapper.full_slug_to_base)} materials (SOURCE OF TRUTH)")
    print(f"   Format: slugified-with-suffix (aluminum-laser-cleaning)")
    print()
    
    # Settings.yaml
    print(f"🔍 Settings.yaml: {results['settings']['total_entries']} entries")
    if results['settings']['issues_count'] == 0:
        print(f"   ✅ All keys map to Materials.yaml")
        noncanonical_count = results['settings'].get('noncanonical_count', 0)
        if noncanonical_count > 0:
            print(f"   ⚠️  {noncanonical_count} keys use legacy/noncanonical format")
            print(f"   Examples: {results['settings'].get('noncanonical', [])[:3]}")
        else:
            print(f"   ✅ Keys follow canonical settings format (-settings suffix)")
    else:
        print(f"   ❌ {results['settings']['issues_count']} inconsistencies found")
        print(f"   Issues: {results['settings']['issues'][:3]}")
    print()
    
    # Contaminants.yaml
    print(f"🔍 Contaminants.yaml: {results['contaminants']['patterns_checked']} patterns")
    if results['contaminants']['issues_count'] == 0:
        print(f"   ✅ All material references valid")
    else:
        print(f"   ❌ {results['contaminants']['issues_count']} invalid references")
        print(f"   Affected patterns: {len(results['contaminants']['affected_patterns'])}")
    print()
    
    # DomainAssociations.yaml
    print(f"🔍 DomainAssociations.yaml: {results['associations']['total_associations']} associations")
    if results['associations']['issues_count'] == 0:
        print(f"   ✅ All material IDs valid")
    else:
        print(f"   ❌ {results['associations']['issues_count']} invalid material IDs")
    print()

    # Applications.yaml
    print(f"🔍 Applications.yaml: {results['applications']['total_entries']} entries")
    if results['applications']['issues_count'] == 0:
        print(f"   ✅ All application keys and IDs normalized")
    else:
        print(f"   ❌ {results['applications']['issues_count']} inconsistencies found")
        print(f"   Issues: {results['applications']['issues'][:3]}")
    print()
    
    print("=" * 80)
    if total_issues > 0:
        print(f"❌ TOTAL ISSUES: {total_issues}")
        print()
        print("Run with --fix to normalize all domains")
    else:
        print("✅ ALL DOMAINS CONSISTENT")
    print("=" * 80)
    
    return results


def check_settings_consistency(mapper: MaterialNameMapper) -> Dict:
    """Check Settings.yaml consistency with Materials.yaml."""
    path = PROJECT_ROOT / "data" / "settings" / "Settings.yaml"
    data = load_yaml(path)
    
    settings = data.get('settings', {})
    issues = []
    noncanonical = []
    
    for setting_key in settings.keys():
        # Settings should use -settings suffix (legacy base-slug accepted)
        if setting_key in mapper.settings_to_base:
            if not setting_key.endswith('-settings'):
                noncanonical.append(
                    f"Legacy key without suffix: {setting_key} (preferred: {setting_key}-settings)"
                )
            continue

        # Handle uncommon-but-recoverable keys ending with -laser-cleaning
        if setting_key.endswith('-laser-cleaning'):
            base_slug = setting_key.replace('-laser-cleaning', '')
            if base_slug in mapper.base_to_display:
                noncanonical.append(
                    f"Unexpected -laser-cleaning key in settings: {setting_key} (preferred: {base_slug}-settings)"
                )
                continue

        # Unknown setting key
        if setting_key not in mapper.settings_to_base:
            issues.append(f"Unknown material: {setting_key}")
    
    return {
        'total_entries': len(settings),
        'issues_count': len(issues),
        'issues': issues,
        'noncanonical_count': len(noncanonical),
        'noncanonical': noncanonical[:10]
    }


def check_contaminants_consistency(mapper: MaterialNameMapper) -> Dict:
    """Check Contaminants.yaml material references."""
    path = PROJECT_ROOT / "data" / "contaminants" / "Contaminants.yaml"
    data = load_yaml(path)

    patterns = data.get('contamination_patterns')
    if not isinstance(patterns, dict) or not patterns:
        patterns = data.get('contaminants', {})

    issues = []
    affected_patterns = set()

    def _is_valid_material_reference(material: str) -> bool:
        if material in KNOWN_EXCEPTIONS:
            return True
        if material in mapper.full_slug_to_base:
            return True
        if material in mapper.base_to_display:
            return True
        if material in mapper.display_to_base:
            return True
        if material.lower() in mapper.display_to_base:
            return True
        return False
    
    for pattern_id, pattern_data in patterns.items():
        valid_materials = pattern_data.get('valid_materials')
        if valid_materials is None:
            valid_materials = pattern_data.get('validMaterials', [])
        for material in valid_materials:
            if not _is_valid_material_reference(material):
                issues.append(f"{pattern_id}: Unknown material '{material}'")
                affected_patterns.add(pattern_id)
        
        prohibited_materials = pattern_data.get('prohibited_materials')
        if prohibited_materials is None:
            prohibited_materials = pattern_data.get('prohibitedMaterials', [])
        for material in prohibited_materials:
            if not _is_valid_material_reference(material):
                issues.append(f"{pattern_id}: Unknown material '{material}'")
                affected_patterns.add(pattern_id)
    
    return {
        'patterns_checked': len(patterns),
        'issues_count': len(issues),
        'affected_patterns': list(affected_patterns),
        'issues': issues[:10]  # First 10 for display
    }


def check_associations_consistency(mapper: MaterialNameMapper) -> Dict:
    """Check DomainAssociations.yaml material IDs."""
    path = PROJECT_ROOT / "data" / "associations" / "DomainAssociations.yaml"
    if not path.exists():
        return {'total_associations': 0, 'issues_count': 0, 'issues': []}
    
    data = load_yaml(path)
    associations = data.get('associations', [])
    issues = []
    
    for assoc in associations:
        # Check material references
        if assoc.get('source_domain') == 'materials':
            mat_id = assoc.get('source_id')
            # Normalize mat_id for comparison (remove parentheses like KNOWN_EXCEPTIONS_SLUGS)
            normalized_id = mat_id.replace('(', '').replace(')', '') if mat_id else mat_id
            # Skip known exceptions (slugified)
            if normalized_id in KNOWN_EXCEPTIONS_SLUGS:
                continue
            if mat_id not in mapper.base_to_display and f"{mat_id}-laser-cleaning" not in mapper.full_slug_to_base:
                issues.append(f"Unknown source material: {mat_id}")
        
        if assoc.get('target_domain') == 'materials':
            mat_id = assoc.get('target_id')
            # Normalize mat_id for comparison (remove parentheses like KNOWN_EXCEPTIONS_SLUGS)
            normalized_id = mat_id.replace('(', '').replace(')', '') if mat_id else mat_id
            # Skip known exceptions (slugified)
            if normalized_id in KNOWN_EXCEPTIONS_SLUGS:
                continue
            if mat_id not in mapper.base_to_display and f"{mat_id}-laser-cleaning" not in mapper.full_slug_to_base:
                issues.append(f"Unknown target material: {mat_id}")
    
    return {
        'total_associations': len(associations),
        'issues_count': len(issues),
        'issues': issues[:10]
    }


def check_applications_consistency() -> Dict:
    """Check Applications.yaml key/id naming consistency."""
    path = PROJECT_ROOT / "data" / "applications" / "Applications.yaml"
    if not path.exists():
        return {'total_entries': 0, 'issues_count': 0, 'issues': []}

    data = load_yaml(path)
    applications = data.get('applications', {})
    issues = []
    slug_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

    for key, item in applications.items():
        if key != key.lower():
            issues.append(f"Key not lowercase: {key}")
        if ' ' in key:
            issues.append(f"Key contains spaces: {key}")
        if not slug_pattern.match(key):
            issues.append(f"Key not slug-formatted: {key}")

        item_id = item.get('id')
        if item_id != key:
            issues.append(f"ID mismatch: key='{key}' id='{item_id}'")

    return {
        'total_entries': len(applications),
        'issues_count': len(issues),
        'issues': issues[:10],
    }


def fix_all_domains(mapper: MaterialNameMapper, dry_run: bool = True) -> None:
    """Fix all domains to use consistent material references."""
    mode_str = "[DRY RUN]" if dry_run else "[APPLYING FIXES]"
    
    print("=" * 80)
    print(f"CROSS-DOMAIN NORMALIZATION {mode_str}")
    print("=" * 80)
    print()
    
    # Fix Contaminants.yaml
    print("🔧 Normalizing Contaminants.yaml...")
    contaminants_result = fix_contaminants(mapper, dry_run)
    print(f"   ✅ {contaminants_result['fixed_count']} references normalized")
    print(f"   📋 {contaminants_result['patterns_updated']} patterns updated")
    print()
    
    # Check if Settings needs fixes
    print("🔍 Checking Settings.yaml...")
    settings_result = check_settings_consistency(mapper)
    if settings_result['issues_count'] == 0:
        print("   ✅ No fixes needed")
    else:
        print(f"   ⚠️  {settings_result['issues_count']} issues (manual review needed)")
    print()
    
    # Check if Associations needs fixes
    print("🔍 Checking DomainAssociations.yaml...")
    assoc_result = check_associations_consistency(mapper)
    if assoc_result['issues_count'] == 0:
        print("   ✅ No fixes needed")
    else:
        print(f"   ⚠️  {assoc_result['issues_count']} issues (manual review needed)")
    print()
    
    print("=" * 80)
    if dry_run:
        print("✅ DRY RUN COMPLETE - No files modified")
        print()
        print("Run without --dry-run to apply changes")
    else:
        print("✅ NORMALIZATION COMPLETE")
    print("=" * 80)


def fix_contaminants(mapper: MaterialNameMapper, dry_run: bool = True) -> Dict:
    """Fix material references in Contaminants.yaml."""
    path = PROJECT_ROOT / "data" / "contaminants" / "Contaminants.yaml"
    data = load_yaml(path)

    patterns = data.get('contamination_patterns')
    if not isinstance(patterns, dict) or not patterns:
        patterns = data.get('contaminants', {})

    fixed_count = 0
    patterns_updated = set()
    
    for pattern_id, pattern_data in patterns.items():
        valid_key = None
        if 'valid_materials' in pattern_data:
            valid_key = 'valid_materials'
        elif 'validMaterials' in pattern_data:
            valid_key = 'validMaterials'

        # Fix valid materials list while preserving existing key style
        if valid_key:
            fixed_materials = []
            for material in pattern_data[valid_key]:
                if material == 'ALL':
                    fixed_materials.append(material)
                    continue
                
                # Normalize to display format
                normalized = mapper.normalize_for_domain(material, 'contaminants', 'contaminants')
                if '[UNKNOWN]' not in normalized:
                    fixed_materials.append(normalized)
                    if normalized != material:
                        fixed_count += 1
                        patterns_updated.add(pattern_id)
                else:
                    # Keep original with flag for review
                    fixed_materials.append(material)
            
            pattern_data[valid_key] = sorted(set(fixed_materials))
        
        prohibited_key = None
        if 'prohibited_materials' in pattern_data:
            prohibited_key = 'prohibited_materials'
        elif 'prohibitedMaterials' in pattern_data:
            prohibited_key = 'prohibitedMaterials'

        # Fix prohibited materials list while preserving existing key style
        if prohibited_key:
            fixed_materials = []
            for material in pattern_data[prohibited_key]:
                normalized = mapper.normalize_for_domain(material, 'contaminants', 'contaminants')
                if '[UNKNOWN]' not in normalized:
                    fixed_materials.append(normalized)
                    if normalized != material:
                        fixed_count += 1
                        patterns_updated.add(pattern_id)
                else:
                    fixed_materials.append(material)
            
            pattern_data[prohibited_key] = sorted(set(fixed_materials))
    
    if not dry_run:
        save_yaml(path, data)
    
    return {
        'fixed_count': fixed_count,
        'patterns_updated': len(patterns_updated)
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Normalize material names across ALL domains (E2E)"
    )
    parser.add_argument('--check', action='store_true', help='Check consistency')
    parser.add_argument('--fix', action='store_true', help='Fix inconsistencies')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    
    args = parser.parse_args()
    
    if not (args.check or args.fix):
        parser.print_help()
        return 1
    
    try:
        mapper = MaterialNameMapper()
        
        if args.check:
            check_domain_consistency(mapper)
        elif args.fix:
            fix_all_domains(mapper, dry_run=args.dry_run)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
