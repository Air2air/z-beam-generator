#!/usr/bin/env python3
"""
Source Data Schema Validator v2

Validates source YAML files against SOURCE_DATA_SCHEMA.md specification.
Handles domain-specific ID suffix requirements.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple
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
    
    # Domain-specific ID suffix requirements
    DOMAIN_SUFFIXES = {
        'materials': '-laser-cleaning',
        'settings': '-settings',
        'compounds': '-compound',
        'contaminants': '-contamination'
    }
    
    def __init__(self):
        self.violations = defaultdict(list)
        self.stats = defaultdict(int)
    
    def validate_item(self, item_id: str, data: Dict, domain: str) -> List[str]:
        """Validate a single item"""
        issues = []
        
        # Check ID format
        expected_suffix = self.DOMAIN_SUFFIXES.get(domain)
        if expected_suffix and not item_id.endswith(expected_suffix):
            issues.append(f"ID must end with '{expected_suffix}' for {domain} domain")
            self.stats['invalid_id_format'] += 1
        
        # Check if ID matches key
        item_actual_id = data.get('id')
        if item_actual_id != item_id:
            issues.append(f"ID mismatch: key='{item_id}' but id field='{item_actual_id}'")
            self.stats['id_key_mismatch'] += 1
        
        # Check for prohibited fields
        for field in self.PROHIBITED_FIELDS:
            if field in data:
                issues.append(f"Prohibited field: '{field}' (should be in frontmatter only)")
                self.stats['prohibited_fields'] += 1
                self.violations['prohibited'].append((item_id, field))
        
        # Check for misplaced relationships
        for field in self.RELATIONSHIP_FIELDS:
            if field in data and field != 'relationships':
                issues.append(f"Relationship field at top level: '{field}' (should be in relationships block)")
                self.stats['misplaced_relationships'] += 1
                self.violations['misplaced'].append((item_id, field))
        
        # Validate relationships structure
        if 'relationships' in data:
            rel_issues = self.validate_relationships(item_id, data['relationships'])
            issues.extend(rel_issues)
        
        return issues
    
    def validate_relationships(self, item_id: str, relationships: Dict) -> List[str]:
        """Validate relationships block structure"""
        issues = []
        
        if not isinstance(relationships, dict):
            issues.append(f"relationships must be a dict, got {type(relationships).__name__}")
            return issues
        
        for field_name, field_data in relationships.items():
            if isinstance(field_data, dict) and 'presentation' in field_data:
                if 'items' not in field_data:
                    issues.append(f"relationships.{field_name}: has 'presentation' but missing 'items'")
                    self.stats['invalid_relationship_structure'] += 1
        
        return issues
    
    def validate_file(self, file_path: Path, items_key: str, domain: str) -> Tuple[int, int]:
        """Validate a source data file"""
        print(f"\n{'='*70}")
        print(f"📄 {domain.upper()}: {file_path.name}")
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
            issues = self.validate_item(item_id, item_data, domain)
            
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
        
        print(f"\nViolation Statistics:")
        for stat_name, count in sorted(self.stats.items()):
            if count > 0:
                print(f"  {stat_name}: {count}")
        
        if self.violations['prohibited']:
            print(f"\n⚠️  Top Prohibited Fields:")
            field_counts = defaultdict(int)
            for _, field in self.violations['prohibited']:
                field_counts[field] += 1
            
            for field, count in sorted(field_counts.items(), key=lambda x: -x[1])[:10]:
                print(f"  {field}: {count} occurrences")


def main():
    """Run schema validation on all source files"""
    print("\n" + "="*70)
    print("🔍 SOURCE DATA SCHEMA VALIDATION v2")
    print("="*70)
    print("\nReference: docs/05-data/SOURCE_DATA_SCHEMA.md")
    print("\nDomain Suffix Requirements:")
    print("  materials:     {slug}-laser-cleaning")
    print("  settings:      {slug}-settings")
    print("  compounds:     {slug}-compound")
    print("  contaminants:  {slug}-contamination")
    
    validator = SchemaValidator()
    
    # Define files to validate (path, items_key, domain)
    files_to_check = [
        ('data/materials/Materials.yaml', 'materials', 'materials'),
        ('data/settings/Settings.yaml', 'settings', 'settings'),
        ('data/compounds/Compounds.yaml', 'compounds', 'compounds'),
        ('data/contaminants/Contaminants.yaml', 'contamination_patterns', 'contaminants'),
    ]
    
    total_items = 0
    total_issues = 0
    
    for file_path, items_key, domain in files_to_check:
        path = Path(file_path)
        if path.exists():
            items, issues = validator.validate_file(path, items_key, domain)
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
    else:
        print(f"❌ FAILURE: {total_issues} issues found across {total_items} items")
    print(f"{'='*70}")
    
    return 0 if total_issues == 0 else 1


if __name__ == '__main__':
    exit(main())
