#!/usr/bin/env python3
"""
Source Data Schema Validator

Validates source YAML files against SOURCE_DATA_SCHEMA.md specification.
Checks for:
- Required fields present
- Relationships in correct location
- Prohibited generated content fields
- ID format consistency
"""

import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class SchemaValidator:
    """Validates source data against schema rules"""
    
    # Fields that should NOT exist in source data (generated during export)
    PROHIBITED_FIELDS = {
        'card', 'components', 'description', 'settings_description',
        'meta_description', 'page_title', 'contamination', 'eeat',
        'voice_enhanced'
    }
    
    # Relationship fields that MUST be inside relationships block
    RELATIONSHIP_FIELDS = {
        'regulatory_standards', 'contaminated_by', 'industry_applications',
        'removes_contaminants', 'related_materials', 'related_settings',
        'produces_compounds', 'common_challenges', 'health_effects'
    }
    
    # Required top-level fields for materials
    REQUIRED_MATERIAL_FIELDS = {
        'name', 'id', 'category', 'subcategory', 'full_path',
        'title', 'author', 'relationships'
    }
    
    def __init__(self):
        self.violations = defaultdict(list)
        self.stats = defaultdict(int)
        
        # Domain-specific suffix requirements
        self.domain_suffixes = {
            'materials': '-laser-cleaning',
            'settings': '-settings',
            'compounds': '-compound',
            'contaminants': '-contamination'
        }
    
    def validate_item(self, item_id: str, data: Dict, domain: str = 'materials') -> List[str]:
        """Validate a single item (material, setting, compound, contaminant)"""
        issues = []
        
        # Check required fields
        for field in self.REQUIRED_MATERIAL_FIELDS:
            if field not in data:
                issues.append(f"Missing required field: {field}")
                self.stats['missing_required'] += 1
        
        # Check ID consistency
        if 'id' in data and data['id'] != material_id:
            issues.append(f"ID mismatch: key='{material_id}' but id='{data['id']}'")
            self.stats['id_mismatch'] += 1
        
        # Check ID format - domain-specific suffix validation
        if not material_id.endswith('-laser-cleaning'):
            issues.append(f"Invalid ID format: must end with '-laser-cleaning'")
            self.stats['invalid_id_format'] += 1
        
        # Check for prohibited fields at top level
        for field in self.PROHIBITED_FIELDS:
            if field in data:
                issues.append(f"Prohibited field in source: '{field}' (should be in frontmatter only)")
                self.stats['prohibited_fields'] += 1
                self.violations['prohibited'].append((material_id, field))
        
        # Check for relationship fields outside relationships block
        for field in self.RELATIONSHIP_FIELDS:
            if field in data and field != 'relationships':
                issues.append(f"Relationship field at top level: '{field}' (should be in relationships block)")
                self.stats['misplaced_relationships'] += 1
                self.violations['misplaced'].append((material_id, field))
        
        # Validate relationships structure
        if 'relationships' in data:
            rel_issues = self.validate_relationships(material_id, data['relationships'])
            issues.extend(rel_issues)
        
        return issues
    
    def validate_relationships(self, material_id: str, relationships: Dict) -> List[str]:
        """Validate relationships block structure"""
        issues = []
        
        if not isinstance(relationships, dict):
            issues.append(f"relationships must be a dict, got {type(relationships).__name__}")
            return issues
        
        for field_name, field_data in relationships.items():
            # Check if it's a presentation-based relationship
            if isinstance(field_data, dict):
                if 'presentation' in field_data:
                    # Must have items
                    if 'items' not in field_data:
                        issues.append(f"relationships.{field_name}: has 'presentation' but missing 'items'")
                        self.stats['invalid_relationship_structure'] += 1
                    
                    # Presentation must be valid
                    valid_presentations = {'card', 'list', 'table'}
                    if field_data['presentation'] not in valid_presentations:
                        issues.append(f"relationships.{field_name}: invalid presentation '{field_data['presentation']}'")
                        self.stats['invalid_presentation'] += 1
        
        return issues
    
    def validate_file(self, file_path: Path, items_key: str) -> Tuple[int, int]:
        """
        Validate a source data file
        
        Returns:
            (total_items, total_issues)
        """
        print(f"\n{'='*70}")
        print(f"📄 Validating: {file_path.name}")
        print(f"{'='*70}")
        
        with open(file_path) as f:
            data = yaml.safe_load(f)
        
        if items_key not in data:
            print(f"❌ Missing '{items_key}' key in file")
            return 0, 1
        
        items = data[items_key]
        total_items = len(items)
        total_issues = 0
        
        print(f"Items found: {total_items}")
        print()
        
        # Validate each item
        for item_id, item_data in items.items():
            issues = self.validate_material(item_id, item_data)
            
            if issues:
                print(f"❌ {item_id}")
                for issue in issues:
                    print(f"   └─ {issue}")
                total_issues += len(issues)
        
        if total_issues == 0:
            print(f"✅ All {total_items} items valid")
        else:
            print(f"\n⚠️  Found {total_issues} issues in {total_items} items")
        
        return total_items, total_issues
    
    def print_summary(self):
        """Print validation summary"""
        print(f"\n{'='*70}")
        print("📊 VALIDATION SUMMARY")
        print(f"{'='*70}")
        
        print("\nIssue Breakdown:")
        for stat_name, count in sorted(self.stats.items()):
            if count > 0:
                print(f"  {stat_name}: {count}")
        
        if self.violations['prohibited']:
            print("\n⚠️  Top Prohibited Fields:")
            field_counts = defaultdict(int)
            for _, field in self.violations['prohibited']:
                field_counts[field] += 1
            
            for field, count in sorted(field_counts.items(), key=lambda x: -x[1])[:10]:
                print(f"  {field}: {count} occurrences")
        
        if self.violations['misplaced']:
            print("\n⚠️  Top Misplaced Relationships:")
            field_counts = defaultdict(int)
            for _, field in self.violations['misplaced']:
                field_counts[field] += 1
            
            for field, count in sorted(field_counts.items(), key=lambda x: -x[1])[:10]:
                print(f"  {field}: {count} occurrences")


def main():
    """Run schema validation on all source files"""
    print("\n" + "="*70)
    print("🔍 SOURCE DATA SCHEMA VALIDATION")
    print("="*70)
    print("\nReference: docs/05-data/SOURCE_DATA_SCHEMA.md")
    
    validator = SchemaValidator()
    
    # Define files to validate
    files_to_check = [
        ('data/materials/Materials.yaml', 'materials'),
        ('data/contaminants/Contaminants.yaml', 'contaminants'),
        ('data/settings/Settings.yaml', 'settings'),
        ('data/compounds/Compounds.yaml', 'compounds'),
    ]
    
    total_items = 0
    total_issues = 0
    
    for file_path, items_key in files_to_check:
        path = Path(file_path)
        if path.exists():
            items, issues = validator.validate_file(path, items_key)
            total_items += items
            total_issues += issues
        else:
            print(f"\n⚠️  File not found: {file_path}")
    
    # Print summary
    validator.print_summary()
    
    # Final status
    print(f"\n{'='*70}")
    if total_issues == 0:
        print(f"✅ SUCCESS: All {total_items} items pass schema validation")
        print(f"{'='*70}")
        return 0
    else:
        print(f"❌ FAILURE: {total_issues} issues found across {total_items} items")
        print(f"{'='*70}")
        print("\nRecommended Actions:")
        print("1. Run: python3 scripts/migration/normalize_relationships_structure.py")
        print("2. Run: python3 scripts/migration/remove_generated_fields.py")
        print("3. Re-run this validator")
        return 1


if __name__ == '__main__':
    exit(main())
