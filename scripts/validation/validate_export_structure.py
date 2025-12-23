#!/usr/bin/env python3
"""
Export Structure Validator

Validates that the export system preserves the new card/relationship structure:
- card.default with all required fields
- card context variants (contamination_context, material_context, etc.)
- relationships.{type}.presentation at key level
- relationships.{type}.items as array

USAGE:
    python3 scripts/validation/validate_export_structure.py
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple


def validate_card_structure(item_data: Dict[str, Any], item_id: str) -> List[str]:
    """
    Validate card structure preservation.
    
    Returns list of issues (empty if valid).
    """
    issues = []
    
    # Check card exists
    if 'card' not in item_data:
        issues.append(f"{item_id}: Missing 'card' field")
        return issues
    
    card = item_data['card']
    
    # Check card is dict
    if not isinstance(card, dict):
        issues.append(f"{item_id}: 'card' is not a dict (type: {type(card).__name__})")
        return issues
    
    # Check card.default exists
    if 'default' not in card:
        issues.append(f"{item_id}: Missing 'card.default'")
        return issues
    
    card_default = card['default']
    
    # Check card.default structure
    required_fields = ['heading', 'subtitle', 'badge', 'metric', 'severity', 'icon']
    for field in required_fields:
        if field not in card_default:
            issues.append(f"{item_id}: Missing 'card.default.{field}'")
    
    # Check for flattened structure (forbidden)
    forbidden_top_level = ['heading', 'subtitle', 'badge', 'metric', 'severity', 'icon']
    for field in forbidden_top_level:
        if field in item_data and field != 'icon':  # icon might be top-level too
            issues.append(f"{item_id}: Forbidden flattened field at top level: '{field}'")
    
    return issues


def validate_relationship_structure(item_data: Dict[str, Any], item_id: str) -> List[str]:
    """
    Validate relationship structure preservation.
    
    Returns list of issues (empty if valid).
    """
    issues = []
    
    # Metadata fields that don't need card format (strings, metadata dicts, etc.)
    METADATA_FIELDS = {
        'eeat',           # E-E-A-T metadata dict
        'context_notes',  # String notes
        'realism_notes',  # String notes
        'formation_conditions',  # Could be string or dict
        'regulatory_standards_detail',  # Could be string or dict
        'found_on_materials',  # Material references (handled differently)
        'chemical_formula',  # String formula
        'scientific_name',  # String name
        'required_elements'  # List of strings (element identifiers)
    }
    
    # Check relationships exists
    if 'relationships' not in item_data:
        return []  # Not all items have relationships
    
    relationships = item_data['relationships']
    
    # Check relationships is dict
    if not isinstance(relationships, dict):
        issues.append(f"{item_id}: 'relationships' is not a dict (type: {type(relationships).__name__})")
        return issues
    
    # Check each relationship type
    for rel_type, rel_data in relationships.items():
        # Skip metadata fields (don't require card format)
        if rel_type in METADATA_FIELDS:
            continue
        # Must be dict with presentation and items
        if not isinstance(rel_data, dict):
            issues.append(f"{item_id}.relationships.{rel_type}: Not a dict (type: {type(rel_data).__name__})")
            continue
        
        # Check presentation at key level
        if 'presentation' not in rel_data:
            issues.append(f"{item_id}.relationships.{rel_type}: Missing 'presentation' field")
        
        # Check items array
        if 'items' not in rel_data:
            issues.append(f"{item_id}.relationships.{rel_type}: Missing 'items' array")
            continue
        
        items = rel_data['items']
        if not isinstance(items, list):
            issues.append(f"{item_id}.relationships.{rel_type}.items: Not a list (type: {type(items).__name__})")
        
        # Check for forbidden structure (old format)
        if isinstance(items, list) and items and isinstance(items[0], dict):
            first_item = items[0]
            if 'presentation' in first_item:
                issues.append(f"{item_id}.relationships.{rel_type}: Forbidden 'presentation' in items array (should be at key level)")
    
    return issues


def validate_frontmatter_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a single frontmatter file.
    
    Returns (is_valid, issues_list)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return False, [f"{file_path.name}: Empty file"]
        
        item_id = data.get('id', file_path.stem)
        
        # Validate card structure
        card_issues = validate_card_structure(data, item_id)
        
        # Validate relationship structure
        rel_issues = validate_relationship_structure(data, item_id)
        
        all_issues = card_issues + rel_issues
        
        return len(all_issues) == 0, all_issues
    
    except Exception as e:
        return False, [f"{file_path.name}: Error loading file: {e}"]


def validate_domain(domain: str, frontmatter_root: Path) -> Tuple[int, int, List[str]]:
    """
    Validate all frontmatter files in a domain.
    
    Returns (total_files, valid_files, all_issues)
    """
    domain_path = frontmatter_root / domain
    
    if not domain_path.exists():
        print(f"⚠️  Domain directory not found: {domain_path}")
        return 0, 0, []
    
    # Find all .yaml files recursively
    yaml_files = list(domain_path.rglob("*.yaml"))
    
    total = len(yaml_files)
    valid = 0
    all_issues = []
    
    for yaml_file in yaml_files:
        is_valid, issues = validate_frontmatter_file(yaml_file)
        
        if is_valid:
            valid += 1
        else:
            all_issues.extend(issues)
    
    return total, valid, all_issues


def main():
    """Validate export structure across all domains."""
    
    print("=" * 70)
    print("Export Structure Validation")
    print("=" * 70)
    print()
    
    # Frontmatter directory (relative to script location)
    frontmatter_root = Path("../z-beam/frontmatter")
    
    if not frontmatter_root.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_root}")
        print("   Export validation requires exported frontmatter files.")
        return 1
    
    domains = ['materials', 'compounds', 'contaminants', 'settings']
    
    total_files = 0
    total_valid = 0
    all_domain_issues = []
    
    for domain in domains:
        print(f"📋 Validating {domain}...")
        count, valid, issues = validate_domain(domain, frontmatter_root)
        
        total_files += count
        total_valid += valid
        
        print(f"   Files: {count}")
        print(f"   Valid: {valid}")
        print(f"   Issues: {len(issues)}")
        
        if issues:
            # Show first 3 issues
            for issue in issues[:3]:
                print(f"      • {issue}")
            if len(issues) > 3:
                print(f"      ... and {len(issues) - 3} more")
        
        all_domain_issues.extend(issues)
        print()
    
    print("=" * 70)
    print("SUMMARY:")
    print(f"  Total files: {total_files}")
    print(f"  Valid files: {total_valid}")
    print(f"  Invalid files: {total_files - total_valid}")
    print(f"  Total issues: {len(all_domain_issues)}")
    
    if total_valid == total_files:
        print(f"\n✅ ALL FILES VALID - Export system preserves new structure")
        return 0
    else:
        print(f"\n❌ VALIDATION FAILED - {total_files - total_valid} files have issues")
        return 1


if __name__ == '__main__':
    sys.exit(main())
