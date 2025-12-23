#!/usr/bin/env python3
"""
Card Structure Validation Script

Validates that all entities have proper card schemas with required fields.

Usage:
    python3 scripts/validation/validate_card_structure.py
    python3 scripts/validation/validate_card_structure.py --domain materials
    python3 scripts/validation/validate_card_structure.py --fix-issues
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Valid values for enum fields
VALID_SEVERITIES = {'critical', 'high', 'moderate', 'low'}
VALID_BADGE_VARIANTS = {'success', 'warning', 'danger', 'info', 'technical'}
VALID_CONTEXTS = {'default', 'contamination_context', 'material_context', 'compound_context', 'setting_context'}

# Required fields in each card variant
REQUIRED_CARD_FIELDS = {
    'heading': str,
    'subtitle': str,
    'badge': dict,
    'metric': dict,
    'severity': str,
}

REQUIRED_BADGE_FIELDS = {
    'text': str,
    'variant': str,
}

REQUIRED_METRIC_FIELDS = {
    'value': str,
    'legend': str,
}

# Domain configurations
DOMAINS = {
    'materials': {
        'file': 'data/materials/Materials.yaml',
        'key': 'materials',
    },
    'compounds': {
        'file': 'data/compounds/Compounds.yaml',
        'key': 'compounds',
    },
    'contaminants': {
        'file': 'data/contaminants/Contaminants.yaml',
        'key': 'contamination_patterns',
    },
    'settings': {
        'file': 'data/settings/Settings.yaml',
        'key': 'settings',
    },
}


class CardStructureValidator:
    """Validates card structure in entity data."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.entity_count = 0
        self.valid_count = 0
    
    def validate_card_variant(
        self,
        entity_id: str,
        variant_name: str,
        variant_data: Dict[str, Any]
    ) -> bool:
        """
        Validate a single card variant (default, contamination_context, etc.)
        
        Returns:
            True if valid, False otherwise
        """
        is_valid = True
        
        # Check required top-level fields
        for field_name, field_type in REQUIRED_CARD_FIELDS.items():
            if field_name not in variant_data:
                self.errors.append(
                    f"{entity_id}: card.{variant_name} missing required field '{field_name}'"
                )
                is_valid = False
            elif not isinstance(variant_data[field_name], field_type):
                self.errors.append(
                    f"{entity_id}: card.{variant_name}.{field_name} should be {field_type.__name__}, "
                    f"got {type(variant_data[field_name]).__name__}"
                )
                is_valid = False
        
        # Validate badge structure
        if 'badge' in variant_data:
            badge = variant_data['badge']
            for field_name, field_type in REQUIRED_BADGE_FIELDS.items():
                if field_name not in badge:
                    self.errors.append(
                        f"{entity_id}: card.{variant_name}.badge missing required field '{field_name}'"
                    )
                    is_valid = False
                elif not isinstance(badge[field_name], field_type):
                    self.errors.append(
                        f"{entity_id}: card.{variant_name}.badge.{field_name} should be {field_type.__name__}"
                    )
                    is_valid = False
            
            # Validate badge variant enum
            if 'variant' in badge and badge['variant'] not in VALID_BADGE_VARIANTS:
                self.errors.append(
                    f"{entity_id}: card.{variant_name}.badge.variant '{badge['variant']}' not valid. "
                    f"Must be one of: {', '.join(sorted(VALID_BADGE_VARIANTS))}"
                )
                is_valid = False
        
        # Validate metric structure
        if 'metric' in variant_data:
            metric = variant_data['metric']
            for field_name, field_type in REQUIRED_METRIC_FIELDS.items():
                if field_name not in metric:
                    self.errors.append(
                        f"{entity_id}: card.{variant_name}.metric missing required field '{field_name}'"
                    )
                    is_valid = False
                elif not isinstance(metric[field_name], field_type):
                    self.errors.append(
                        f"{entity_id}: card.{variant_name}.metric.{field_name} should be {field_type.__name__}"
                    )
                    is_valid = False
            
            # Unit is optional but should be string if present
            if 'unit' in metric and not isinstance(metric['unit'], str):
                self.errors.append(
                    f"{entity_id}: card.{variant_name}.metric.unit should be string"
                )
                is_valid = False
        
        # Validate severity enum
        if 'severity' in variant_data and variant_data['severity'] not in VALID_SEVERITIES:
            self.errors.append(
                f"{entity_id}: card.{variant_name}.severity '{variant_data['severity']}' not valid. "
                f"Must be one of: {', '.join(sorted(VALID_SEVERITIES))}"
            )
            is_valid = False
        
        # Icon is optional but should be string if present
        if 'icon' in variant_data and not isinstance(variant_data['icon'], str):
            self.errors.append(
                f"{entity_id}: card.{variant_name}.icon should be string"
            )
            is_valid = False
        
        return is_valid
    
    def validate_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        """
        Validate card structure for a single entity.
        
        Returns:
            True if valid, False otherwise
        """
        self.entity_count += 1
        
        # Check if entity has card field
        if 'card' not in entity_data:
            self.errors.append(f"{entity_id}: Missing 'card' field")
            return False
        
        card = entity_data['card']
        
        # Check if card is a dict
        if not isinstance(card, dict):
            self.errors.append(f"{entity_id}: 'card' should be dict, got {type(card).__name__}")
            return False
        
        # Check if card has 'default' variant (required)
        if 'default' not in card:
            self.errors.append(f"{entity_id}: card missing required 'default' variant")
            return False
        
        # Validate default variant
        is_valid = self.validate_card_variant(entity_id, 'default', card['default'])
        
        # Validate any context-specific variants
        for variant_name, variant_data in card.items():
            if variant_name == 'default':
                continue  # Already validated
            
            # Check if variant name is recognized
            if variant_name not in VALID_CONTEXTS:
                self.warnings.append(
                    f"{entity_id}: Unknown card context '{variant_name}'. "
                    f"Valid contexts: {', '.join(sorted(VALID_CONTEXTS))}"
                )
            
            # Validate variant structure
            if not self.validate_card_variant(entity_id, variant_name, variant_data):
                is_valid = False
        
        if is_valid:
            self.valid_count += 1
        
        return is_valid
    
    def validate_domain(self, domain_name: str) -> Tuple[int, int]:
        """
        Validate all entities in a domain.
        
        Returns:
            Tuple of (valid_count, total_count)
        """
        domain_config = DOMAINS[domain_name]
        file_path = Path(domain_config['file'])
        
        if not file_path.exists():
            self.errors.append(f"Domain file not found: {file_path}")
            return 0, 0
        
        print(f"\n📋 Validating {domain_name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        entities = data[domain_config['key']]
        
        if not isinstance(entities, dict):
            self.errors.append(f"{domain_name}: entities should be dict")
            return 0, 0
        
        domain_start_count = self.entity_count
        domain_start_valid = self.valid_count
        
        for entity_id, entity_data in entities.items():
            self.validate_entity(entity_id, entity_data)
        
        domain_total = self.entity_count - domain_start_count
        domain_valid = self.valid_count - domain_start_valid
        
        return domain_valid, domain_total
    
    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 70)
        print("CARD STRUCTURE VALIDATION REPORT")
        print("=" * 70)
        
        print(f"\n📊 Summary:")
        print(f"   Total entities: {self.entity_count}")
        print(f"   Valid: {self.valid_count}")
        print(f"   Invalid: {self.entity_count - self.valid_count}")
        
        if self.valid_count == self.entity_count:
            print(f"\n✅ ALL CARDS VALID ({self.entity_count}/{self.entity_count})")
        else:
            print(f"\n❌ VALIDATION FAILED ({self.valid_count}/{self.entity_count} valid)")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors[:20]:  # Show first 20 errors
                print(f"   • {error}")
            if len(self.errors) > 20:
                print(f"   ... and {len(self.errors) - 20} more errors")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10 warnings
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings")
        
        print("\n" + "=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate card structure in entity data')
    parser.add_argument(
        '--domain',
        choices=['materials', 'compounds', 'contaminants', 'settings', 'all'],
        default='all',
        help='Domain to validate (default: all)'
    )
    
    args = parser.parse_args()
    
    validator = CardStructureValidator()
    
    # Determine which domains to validate
    if args.domain == 'all':
        domains_to_validate = list(DOMAINS.keys())
    else:
        domains_to_validate = [args.domain]
    
    # Validate each domain
    for domain in domains_to_validate:
        valid, total = validator.validate_domain(domain)
        print(f"   {domain}: {valid}/{total} valid")
    
    # Print report
    validator.print_report()
    
    # Exit with appropriate code
    if validator.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
