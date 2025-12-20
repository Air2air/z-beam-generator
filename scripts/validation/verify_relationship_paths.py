#!/usr/bin/env python3
"""
Comprehensive Relationship Path Validator

Verifies bidirectional relationship links between frontmatter files:
1. Forward validation: Subject A → Item B (ID exists, full_path correct)
2. Backward validation: Item B → Subject A (backlink exists, full_path correct)

Example:
    /contaminants/.../fire-damage-contamination has produces_compounds: pahs-compound
    → Verify /compounds/.../pahs-compound exists and has correct full_path
    → Verify pahs-compound has backlink to fire-damage-contamination
    → Verify backlink has correct full_path to fire-damage
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Relationship field mappings (forward → backward)
RELATIONSHIP_MAPPINGS = {
    # Materials
    'related_materials': 'related_materials',
    'similar_materials': 'similar_materials',
    
    # Contaminants
    'related_contaminants': 'related_contaminants',
    'produces_contaminants': 'source_contaminants',
    'source_contaminants': 'produces_contaminants',
    
    # Compounds
    'produces_compounds': 'source_contaminants',
    'related_compounds': 'related_compounds',
    
    # Settings
    'materials': 'settings',
    'settings': 'materials',
    'contaminants': 'settings',
}

# Domain to directory mapping
DOMAIN_DIRS = {
    'materials': 'materials',
    'contaminants': 'contaminants',
    'compounds': 'compounds',
    'settings': 'settings',
}

class RelationshipPathValidator:
    def __init__(self, frontmatter_dir: str):
        self.frontmatter_dir = Path(frontmatter_dir)
        self.index = {}  # id → file_data
        self.errors = []
        self.warnings = []
        self.total_links = 0
        self.verified_links = 0
        
    def load_all_files(self):
        """Load all frontmatter files into memory."""
        print("🔍 Loading all frontmatter files...")
        
        for domain_key, domain_dir in DOMAIN_DIRS.items():
            domain_path = self.frontmatter_dir / domain_dir
            if not domain_path.exists():
                print(f"   ⚠️  {domain_dir} directory not found")
                continue
                
            files = list(domain_path.glob("*.yaml"))
            print(f"   📁 {domain_dir}: {len(files)} files")
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and 'id' in data:
                            item_id = data['id']
                            self.index[item_id] = {
                                'file': file_path,
                                'domain': domain_key,
                                'data': data,
                                'full_path': data.get('full_path', ''),
                                'name': data.get('name', item_id)
                            }
                except Exception as e:
                    print(f"   ⚠️  Error loading {file_path}: {e}")
        
        print(f"\n✅ Loaded {len(self.index)} items")
    
    def validate_all_relationships(self):
        """Validate all relationship links."""
        print("\n🔍 Validating relationship paths...\n")
        
        for item_id, item_info in self.index.items():
            data = item_info['data']
            relationships = data.get('relationships', {})
            
            if not relationships:
                continue
            
            # Check each relationship field
            for field_name, items in relationships.items():
                if not isinstance(items, list):
                    continue
                
                for item in items:
                    if not isinstance(item, dict) or 'id' not in item:
                        continue
                    
                    self.total_links += 1
                    target_id = item['id']
                    
                    # Validate forward link
                    self.validate_forward_link(
                        source_id=item_id,
                        source_info=item_info,
                        target_id=target_id,
                        relationship_field=field_name,
                        link_data=item
                    )
    
    def validate_forward_link(self, source_id: str, source_info: dict, 
                             target_id: str, relationship_field: str, 
                             link_data: dict):
        """Validate forward link: Source → Target"""
        
        # Check if target exists
        if target_id not in self.index:
            self.errors.append({
                'type': 'missing_target',
                'source': source_id,
                'source_path': source_info['full_path'],
                'target': target_id,
                'field': relationship_field,
                'message': f"Target '{target_id}' does not exist"
            })
            return
        
        target_info = self.index[target_id]
        
        # Verify target's full_path matches link's url (if provided)
        if 'url' in link_data:
            expected_url = link_data['url']
            actual_url = target_info['full_path']
            
            if expected_url != actual_url:
                self.errors.append({
                    'type': 'path_mismatch',
                    'source': source_id,
                    'source_path': source_info['full_path'],
                    'target': target_id,
                    'field': relationship_field,
                    'expected': expected_url,
                    'actual': actual_url,
                    'message': f"Path mismatch: link says '{expected_url}' but actual is '{actual_url}'"
                })
                return
        
        self.verified_links += 1
        
        # Validate backward link
        self.validate_backward_link(
            source_id=source_id,
            source_info=source_info,
            target_id=target_id,
            target_info=target_info,
            relationship_field=relationship_field
        )
    
    def validate_backward_link(self, source_id: str, source_info: dict,
                               target_id: str, target_info: dict,
                               relationship_field: str):
        """Validate backward link: Target → Source"""
        
        # Determine expected backlink field
        backlink_field = RELATIONSHIP_MAPPINGS.get(relationship_field)
        
        if not backlink_field:
            # No bidirectional mapping expected
            return
        
        target_relationships = target_info['data'].get('relationships', {})
        backlink_items = target_relationships.get(backlink_field, [])
        
        # Check if source_id is in backlink_items
        found_backlink = False
        backlink_url_correct = False
        
        for item in backlink_items:
            if not isinstance(item, dict):
                continue
            
            if item.get('id') == source_id:
                found_backlink = True
                
                # Verify backlink URL matches source full_path
                if 'url' in item:
                    if item['url'] == source_info['full_path']:
                        backlink_url_correct = True
                    else:
                        self.errors.append({
                            'type': 'backlink_path_mismatch',
                            'source': source_id,
                            'source_path': source_info['full_path'],
                            'target': target_id,
                            'target_path': target_info['full_path'],
                            'field': backlink_field,
                            'expected': source_info['full_path'],
                            'actual': item['url'],
                            'message': f"Backlink path mismatch: {target_id} → {source_id} has wrong URL"
                        })
                else:
                    # Backlink exists but has no URL field
                    backlink_url_correct = True  # OK if no URL field
                
                break
        
        if not found_backlink:
            self.warnings.append({
                'type': 'missing_backlink',
                'source': source_id,
                'source_path': source_info['full_path'],
                'target': target_id,
                'target_path': target_info['full_path'],
                'expected_field': backlink_field,
                'message': f"{source_id} → {target_id} in '{relationship_field}', but no backlink in '{backlink_field}'"
            })
    
    def print_report(self):
        """Print validation report."""
        print("\n" + "="*80)
        print("📊 RELATIONSHIP PATH VALIDATION REPORT")
        print("="*80)
        
        print(f"\n📁 Files Scanned: {len(self.index)}")
        print(f"🔗 Total Relationship Links: {self.total_links}")
        print(f"✅ Verified Forward Links: {self.verified_links}")
        
        if self.errors:
            print(f"\n❌ ERRORS: {len(self.errors)}")
            print("\nCritical Issues:")
            
            # Group by type
            by_type = defaultdict(list)
            for error in self.errors:
                by_type[error['type']].append(error)
            
            for error_type, errors in by_type.items():
                print(f"\n🔴 {error_type.replace('_', ' ').title()} ({len(errors)}):")
                for error in errors[:10]:  # Show first 10
                    print(f"   • {error['source']} → {error['target']}")
                    print(f"     {error['message']}")
                    if 'expected' in error and 'actual' in error:
                        print(f"     Expected: {error['expected']}")
                        print(f"     Actual: {error['actual']}")
                if len(errors) > 10:
                    print(f"   ... and {len(errors) - 10} more")
        else:
            print("\n✅ No errors found!")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            
            # Group by type
            by_type = defaultdict(list)
            for warning in self.warnings:
                by_type[warning['type']].append(warning)
            
            for warning_type, warnings in by_type.items():
                print(f"\n🟡 {warning_type.replace('_', ' ').title()} ({len(warnings)}):")
                for warning in warnings[:10]:  # Show first 10
                    print(f"   • {warning['message']}")
                if len(warnings) > 10:
                    print(f"   ... and {len(warnings) - 10} more")
        
        print("\n" + "="*80)
        
        # Return exit code
        return 1 if self.errors else 0

def main():
    """Main entry point."""
    # Detect frontmatter directory
    cwd = Path.cwd()
    
    # Check if we're in z-beam directory
    if (cwd / 'frontmatter').exists():
        frontmatter_dir = cwd / 'frontmatter'
    # Check if we're in z-beam-generator directory
    elif (cwd.parent / 'z-beam' / 'frontmatter').exists():
        frontmatter_dir = cwd.parent / 'z-beam' / 'frontmatter'
    else:
        print("❌ Could not find frontmatter directory")
        print("   Run from z-beam or z-beam-generator directory")
        return 1
    
    print(f"📂 Using frontmatter directory: {frontmatter_dir}\n")
    
    validator = RelationshipPathValidator(str(frontmatter_dir))
    validator.load_all_files()
    validator.validate_all_relationships()
    return validator.print_report()

if __name__ == '__main__':
    sys.exit(main())
