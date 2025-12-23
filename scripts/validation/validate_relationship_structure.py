#!/usr/bin/env python3
"""
Relationship Structure Validation Script

Validates that all relationships follow the new structure:
- 'presentation' at key level (not in items)
- 'items' as array
- No 'url' field in items (derived from full_path via lookup)
- No intrinsic properties in items (hazard_level, phase, etc.)

Usage:
    python3 scripts/validation/validate_relationship_structure.py
    python3 scripts/validation/validate_relationship_structure.py --domain materials
    python3 scripts/validation/validate_relationship_structure.py --show-details
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set

# Valid presentation types
VALID_PRESENTATIONS = {'card', 'link', 'table', 'list'}

# Fields that should NOT appear in relationship items (intrinsic properties)
# These should be stored in the target entity, not in the relationship
FORBIDDEN_ITEM_FIELDS = {
    'hazard_level',
    'phase',
    'category',
    'subcategory',
    'presentation',  # Should be at key level, not item level
    'url',  # Should be derived from lookup, not stored
    'name',  # Should be derived from lookup, not stored
    'description',  # Should be derived from lookup, not stored
    'full_path',  # Should be derived from lookup, not stored
}

# Required fields in relationship items
REQUIRED_ITEM_FIELDS = {'id'}

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


class RelationshipStructureValidator:
    """Validates relationship structure in entity data."""
    
    def __init__(self, show_details: bool = False):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.entity_count = 0
        self.relationship_count = 0
        self.valid_relationship_count = 0
        self.show_details = show_details
        self.forbidden_fields_found: Set[str] = set()
    
    def validate_relationship(
        self,
        entity_id: str,
        rel_name: str,
        rel_data: Any
    ) -> bool:
        """
        Validate a single relationship.
        
        Returns:
            True if valid, False otherwise
        """
        self.relationship_count += 1
        is_valid = True
        
        # Check if relationship is a dict
        if not isinstance(rel_data, dict):
            self.errors.append(
                f"{entity_id}.{rel_name}: Relationship should be dict, got {type(rel_data).__name__}"
            )
            return False
        
        # Check for 'presentation' at key level
        if 'presentation' not in rel_data:
            self.errors.append(
                f"{entity_id}.{rel_name}: Missing 'presentation' at key level"
            )
            is_valid = False
        else:
            presentation = rel_data['presentation']
            
            # Validate presentation type
            if not isinstance(presentation, str):
                self.errors.append(
                    f"{entity_id}.{rel_name}: 'presentation' should be string, got {type(presentation).__name__}"
                )
                is_valid = False
            elif presentation not in VALID_PRESENTATIONS:
                self.warnings.append(
                    f"{entity_id}.{rel_name}: Unknown presentation type '{presentation}'. "
                    f"Valid: {', '.join(sorted(VALID_PRESENTATIONS))}"
                )
        
        # Check for 'items' array
        if 'items' not in rel_data:
            self.errors.append(
                f"{entity_id}.{rel_name}: Missing 'items' array"
            )
            is_valid = False
        else:
            items = rel_data['items']
            
            # Check if items is a list
            if not isinstance(items, list):
                self.errors.append(
                    f"{entity_id}.{rel_name}: 'items' should be list, got {type(items).__name__}"
                )
                is_valid = False
            else:
                # Validate each item in the array
                for idx, item in enumerate(items):
                    if not isinstance(item, dict):
                        self.errors.append(
                            f"{entity_id}.{rel_name}.items[{idx}]: Item should be dict, got {type(item).__name__}"
                        )
                        is_valid = False
                        continue
                    
                    # Check required fields
                    for field in REQUIRED_ITEM_FIELDS:
                        if field not in item:
                            self.errors.append(
                                f"{entity_id}.{rel_name}.items[{idx}]: Missing required field '{field}'"
                            )
                            is_valid = False
                    
                    # Check for forbidden fields (intrinsic properties)
                    item_forbidden = set(item.keys()) & FORBIDDEN_ITEM_FIELDS
                    if item_forbidden:
                        for field in item_forbidden:
                            self.errors.append(
                                f"{entity_id}.{rel_name}.items[{idx}]: Forbidden field '{field}' in item. "
                                f"This should be stored in target entity or at key level."
                            )
                            self.forbidden_fields_found.add(field)
                            is_valid = False
                    
                    # Entity type is optional but useful
                    if 'entity_type' not in item and self.show_details:
                        self.warnings.append(
                            f"{entity_id}.{rel_name}.items[{idx}]: Missing recommended field 'entity_type'"
                        )
        
        if is_valid:
            self.valid_relationship_count += 1
        
        return is_valid
    
    def validate_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> Tuple[int, int]:
        """
        Validate relationships for a single entity.
        
        Returns:
            Tuple of (valid_relationships, total_relationships)
        """
        self.entity_count += 1
        
        # Check if entity has relationships
        if 'relationships' not in entity_data:
            return 0, 0
        
        relationships = entity_data['relationships']
        
        # Check if relationships is a dict
        if not isinstance(relationships, dict):
            self.errors.append(f"{entity_id}: 'relationships' should be dict, got {type(relationships).__name__}")
            return 0, 0
        
        start_count = self.relationship_count
        start_valid = self.valid_relationship_count
        
        # Validate each relationship
        for rel_name, rel_data in relationships.items():
            self.validate_relationship(entity_id, rel_name, rel_data)
        
        total = self.relationship_count - start_count
        valid = self.valid_relationship_count - start_valid
        
        return valid, total
    
    def validate_domain(self, domain_name: str) -> Tuple[int, int, int]:
        """
        Validate all entities in a domain.
        
        Returns:
            Tuple of (valid_relationships, total_relationships, entities_with_relationships)
        """
        domain_config = DOMAINS[domain_name]
        file_path = Path(domain_config['file'])
        
        if not file_path.exists():
            self.errors.append(f"Domain file not found: {file_path}")
            return 0, 0, 0
        
        print(f"\n📋 Validating {domain_name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        entities = data[domain_config['key']]
        
        if not isinstance(entities, dict):
            self.errors.append(f"{domain_name}: entities should be dict")
            return 0, 0, 0
        
        domain_start_rel_count = self.relationship_count
        domain_start_valid_count = self.valid_relationship_count
        entities_with_rels = 0
        
        for entity_id, entity_data in entities.items():
            valid, total = self.validate_entity(entity_id, entity_data)
            if total > 0:
                entities_with_rels += 1
        
        domain_total_rels = self.relationship_count - domain_start_rel_count
        domain_valid_rels = self.valid_relationship_count - domain_start_valid_count
        
        return domain_valid_rels, domain_total_rels, entities_with_rels
    
    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 70)
        print("RELATIONSHIP STRUCTURE VALIDATION REPORT")
        print("=" * 70)
        
        print(f"\n📊 Summary:")
        print(f"   Total entities: {self.entity_count}")
        print(f"   Total relationships: {self.relationship_count}")
        print(f"   Valid relationships: {self.valid_relationship_count}")
        print(f"   Invalid relationships: {self.relationship_count - self.valid_relationship_count}")
        
        if self.valid_relationship_count == self.relationship_count:
            print(f"\n✅ ALL RELATIONSHIPS VALID ({self.relationship_count}/{self.relationship_count})")
        else:
            print(f"\n❌ VALIDATION FAILED ({self.valid_relationship_count}/{self.relationship_count} valid)")
        
        if self.forbidden_fields_found:
            print(f"\n🚫 Forbidden fields found in items:")
            for field in sorted(self.forbidden_fields_found):
                print(f"   • {field}")
            print(f"   These fields should be removed from relationship items.")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors[:20]:  # Show first 20 errors
                print(f"   • {error}")
            if len(self.errors) > 20:
                print(f"   ... and {len(self.errors) - 20} more errors")
        
        if self.warnings and self.show_details:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10 warnings
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings")
        
        print("\n" + "=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate relationship structure in entity data')
    parser.add_argument(
        '--domain',
        choices=['materials', 'compounds', 'contaminants', 'settings', 'all'],
        default='all',
        help='Domain to validate (default: all)'
    )
    parser.add_argument(
        '--show-details',
        action='store_true',
        help='Show detailed warnings (e.g., missing entity_type)'
    )
    
    args = parser.parse_args()
    
    validator = RelationshipStructureValidator(show_details=args.show_details)
    
    # Determine which domains to validate
    if args.domain == 'all':
        domains_to_validate = list(DOMAINS.keys())
    else:
        domains_to_validate = [args.domain]
    
    # Validate each domain
    for domain in domains_to_validate:
        valid, total, entities_with_rels = validator.validate_domain(domain)
        print(f"   {domain}: {valid}/{total} valid relationships ({entities_with_rels} entities)")
    
    # Print report
    validator.print_report()
    
    # Exit with appropriate code
    if validator.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
