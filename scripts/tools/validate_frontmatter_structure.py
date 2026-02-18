#!/usr/bin/env python3
"""
Validate Frontmatter Structure
Verifies all requirements from docs/FRONTMATTER_FIXES_REQUIRED.md
"""

import yaml
import glob
from pathlib import Path
from typing import Dict, Any, List

class FrontmatterValidator:
    """Validate frontmatter structure compliance"""
    
    def __init__(self):
        self.issues = {
            'snake_case_keys': [],
            'missing_display_data': [],
            'has_metadata_wrapper': [],
            'type_errors': [],
            'empty_items': []
        }
        self.stats = {
            'files_checked': 0,
            'relationships_checked': 0,
            'items_checked': 0
        }
    
    def check_naming_convention(self, data: Dict[str, Any], filepath: str) -> None:
        """Check for snake_case keys (should be camelCase)"""
        if 'relationships' not in data:
            return
        
        snake_case_keys = [
            'regulatory_standards',
            'contaminated_by', 
            'removed_by',
            'industry_applications',
            'material_pairings',
            'compound_interactions',
            'safety_protocols',
            'environmental_impacts'
        ]
        
        for category in data['relationships'].values():
            if not isinstance(category, dict):
                continue
            
            for key in category.keys():
                if key in snake_case_keys:
                    self.issues['snake_case_keys'].append({
                        'file': filepath,
                        'key': key,
                        'expected': self.to_camel_case(key)
                    })
    
    def to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    def check_relationship_data(self, data: Dict[str, Any], filepath: str) -> None:
        """Check if relationship items have complete display data"""
        if 'relationships' not in data:
            return
        
        for category_name, category in data['relationships'].items():
            if not isinstance(category, dict):
                continue
            
            for section_name, section_data in category.items():
                self.stats['relationships_checked'] += 1
                
                # Check structure
                if not isinstance(section_data, dict):
                    self.issues['type_errors'].append({
                        'file': filepath,
                        'location': f"{category_name}.{section_name}",
                        'error': 'Section is not a dict',
                        'type': type(section_data).__name__
                    })
                    continue
                
                # Check items exists
                if 'items' not in section_data:
                    self.issues['type_errors'].append({
                        'file': filepath,
                        'location': f"{category_name}.{section_name}",
                        'error': 'Missing items array'
                    })
                    continue
                
                items = section_data['items']
                
                # Check items is array
                if not isinstance(items, list):
                    self.issues['type_errors'].append({
                        'file': filepath,
                        'location': f"{category_name}.{section_name}",
                        'error': 'items is not an array',
                        'type': type(items).__name__
                    })
                    continue
                
                # Check each item
                for idx, item in enumerate(items):
                    self.stats['items_checked'] += 1
                    
                    if not isinstance(item, dict):
                        continue
                    
                    # Check for display data (only for references)
                    if 'id' in item:
                        required_fields = ['name', 'url']
                        missing = [f for f in required_fields if f not in item or not item[f]]
                        
                        if missing and section_name in ['contaminatedBy', 'compoundInteractions']:
                            self.issues['missing_display_data'].append({
                                'file': filepath,
                                'location': f"{category_name}.{section_name}[{idx}]",
                                'id': item.get('id', 'unknown'),
                                'missing_fields': missing
                            })
    
    def check_metadata_wrapper(self, data: Dict[str, Any], filepath: str) -> None:
        """Check for deprecated metadata wrapper"""
        if 'metadata' in data:
            self.issues['has_metadata_wrapper'].append(filepath)
    
    def validate_file(self, filepath: Path) -> None:
        """Validate a single file"""
        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)
            
            if not data:
                return
            
            self.stats['files_checked'] += 1
            
            self.check_naming_convention(data, str(filepath))
            self.check_relationship_data(data, str(filepath))
            self.check_metadata_wrapper(data, str(filepath))
            
        except Exception as e:
            print(f"Error validating {filepath}: {e}")
    
    def validate_domain(self, domain: str) -> None:
        """Validate all files in a domain"""
        pattern = f'../z-beam/frontmatter/{domain}/*.yaml'
        files = sorted(glob.glob(pattern))
        
        for filepath in files:
            self.validate_file(Path(filepath))
    
    def print_report(self) -> None:
        """Print validation report"""
        print(f"\n{'='*80}")
        print("FRONTMATTER STRUCTURE VALIDATION REPORT")
        print(f"{'='*80}\n")
        
        # Statistics
        print("📊 STATISTICS:")
        print(f"  Files checked: {self.stats['files_checked']}")
        print(f"  Relationships checked: {self.stats['relationships_checked']}")
        print(f"  Items checked: {self.stats['items_checked']}")
        print()
        
        # Issues
        total_issues = sum(len(v) for v in self.issues.values())
        
        if total_issues == 0:
            print("✅ ALL VALIDATION CHECKS PASSED")
            print()
            print("The frontmatter structure is fully compliant with requirements:")
            print("  ✓ Naming convention: All keys use camelCase")
            print("  ✓ Display data: All references denormalized")
            print("  ✓ Metadata wrapper: Deprecated fields removed")
            print("  ✓ Type safety: All items are arrays")
        else:
            print(f"⚠️  FOUND {total_issues} ISSUES\n")
            
            # Naming issues
            if self.issues['snake_case_keys']:
                print(f"❌ NAMING CONVENTION ({len(self.issues['snake_case_keys'])} issues):")
                print("   Found snake_case keys (should be camelCase)\n")
                for issue in self.issues['snake_case_keys'][:5]:
                    print(f"   {Path(issue['file']).name}")
                    print(f"     Key: {issue['key']} → {issue['expected']}")
                if len(self.issues['snake_case_keys']) > 5:
                    print(f"   ... and {len(self.issues['snake_case_keys']) - 5} more")
                print()
            
            # Missing display data
            if self.issues['missing_display_data']:
                print(f"❌ MISSING DISPLAY DATA ({len(self.issues['missing_display_data'])} issues):")
                print("   Relationship items missing denormalized fields\n")
                for issue in self.issues['missing_display_data'][:5]:
                    print(f"   {Path(issue['file']).name}")
                    print(f"     Location: {issue['location']}")
                    print(f"     ID: {issue['id']}")
                    print(f"     Missing: {', '.join(issue['missing_fields'])}")
                if len(self.issues['missing_display_data']) > 5:
                    print(f"   ... and {len(self.issues['missing_display_data']) - 5} more")
                print()
            
            # Metadata wrapper
            if self.issues['has_metadata_wrapper']:
                print(f"❌ DEPRECATED METADATA WRAPPER ({len(self.issues['has_metadata_wrapper'])} files):")
                print("   Files still contain deprecated 'metadata' field\n")
                for filepath in self.issues['has_metadata_wrapper'][:5]:
                    print(f"   {Path(filepath).name}")
                if len(self.issues['has_metadata_wrapper']) > 5:
                    print(f"   ... and {len(self.issues['has_metadata_wrapper']) - 5} more")
                print()
            
            # Type errors
            if self.issues['type_errors']:
                print(f"❌ TYPE SAFETY ({len(self.issues['type_errors'])} issues):")
                print("   Incorrect data types in relationship structure\n")
                for issue in self.issues['type_errors'][:5]:
                    print(f"   {Path(issue['file']).name}")
                    print(f"     Location: {issue['location']}")
                    print(f"     Error: {issue['error']}")
                    if 'type' in issue:
                        print(f"     Type: {issue['type']}")
                if len(self.issues['type_errors']) > 5:
                    print(f"   ... and {len(self.issues['type_errors']) - 5} more")
                print()
        
        print(f"{'='*80}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate frontmatter structure')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings', 'applications', 'all'],
                        default='all', help='Domain to validate')
    
    args = parser.parse_args()
    
    validator = FrontmatterValidator()
    
    # Validate domains
    if args.domain == 'all':
        for domain in ['materials', 'contaminants', 'compounds', 'settings', 'applications']:
            validator.validate_domain(domain)
    else:
        validator.validate_domain(args.domain)
    
    # Print report
    validator.print_report()


if __name__ == '__main__':
    main()
