"""
Frontmatter Field Order Validator
==================================

Validates and reorders frontmatter fields according to centralized template.

ARCHITECTURE:
- Single source of truth: data/schemas/FrontmatterFieldOrder.yaml
- Validates field order matches specification
- Can automatically reorder fields
- Reports missing required fields

USAGE:
    validator = FrontmatterFieldOrderValidator()
    
    # Check if file matches order
    is_valid = validator.validate_file('frontmatter/materials/aluminum-laser-cleaning.yaml')
    
    # Reorder file to match specification
    validator.reorder_file('frontmatter/materials/aluminum-laser-cleaning.yaml')
    
    # Batch validate all files
    validator.validate_domain('materials')
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import OrderedDict


class FrontmatterFieldOrderValidator:
    """Validates and reorders frontmatter fields"""
    
    def __init__(self, schema_file: Optional[Path] = None):
        """
        Initialize validator
        
        Args:
            schema_file: Path to FrontmatterFieldOrder.yaml (auto-detected if None)
        """
        if schema_file is None:
            schema_file = Path(__file__).parent.parent.parent / 'data' / 'schemas' / 'FrontmatterFieldOrder.yaml'
        
        self.schema_file = Path(schema_file)
        self.schema: Optional[Dict] = None
        self.frontmatter_dir = Path(__file__).parent.parent.parent / 'frontmatter'
    
    def load_schema(self) -> None:
        """Load field order schema"""
        if not self.schema_file.exists():
            raise FileNotFoundError(
                f"Schema file not found: {self.schema_file}\n"
                f"Create this file to define field order specifications."
            )
        
        with open(self.schema_file, 'r', encoding='utf-8') as f:
            self.schema = yaml.safe_load(f)
    
    def get_field_order(self, domain: str) -> List[str]:
        """Get field order specification for a domain"""
        if not self.schema:
            self.load_schema()
        
        domain_spec = self.schema.get(domain, {})
        return domain_spec.get('field_order', [])
    
    def get_required_fields(self, domain: str) -> Set[str]:
        """Get required fields for a domain"""
        if not self.schema:
            self.load_schema()
        
        domain_spec = self.schema.get(domain, {})
        return set(domain_spec.get('required_fields', []))
    
    def validate_field_order(self, data: Dict, domain: str) -> Tuple[bool, List[str]]:
        """
        Validate field order matches specification
        
        Args:
            data: Frontmatter data dictionary
            domain: Domain name (materials, contaminants, compounds, settings)
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        expected_order = self.get_field_order(domain)
        actual_fields = list(data.keys())
        
        issues = []
        
        # Check for missing required fields
        required_fields = self.get_required_fields(domain)
        missing_required = required_fields - set(actual_fields)
        if missing_required:
            issues.append(f"Missing required fields: {', '.join(sorted(missing_required))}")
        
        # Check field order
        # Get positions of fields that are in the spec
        expected_positions = {field: i for i, field in enumerate(expected_order)}
        
        previous_position = -1
        for field in actual_fields:
            if field in expected_positions:
                current_position = expected_positions[field]
                if current_position < previous_position:
                    issues.append(f"Field '{field}' out of order (should come before previous field)")
                previous_position = current_position
        
        # Check for unexpected fields
        expected_set = set(expected_order)
        unexpected = set(actual_fields) - expected_set
        if unexpected:
            issues.append(f"Unexpected fields (not in spec): {', '.join(sorted(unexpected))}")
        
        return len(issues) == 0, issues
    
    def reorder_fields(self, data: Dict, domain: str) -> OrderedDict:
        """
        Reorder fields according to specification
        
        Args:
            data: Frontmatter data dictionary
            domain: Domain name
        
        Returns:
            OrderedDict with fields in correct order
        """
        expected_order = self.get_field_order(domain)
        ordered_data = OrderedDict()
        
        # Add fields in specification order
        for field in expected_order:
            if field in data:
                ordered_data[field] = data[field]
        
        # Add any extra fields at the end
        for field in data:
            if field not in ordered_data:
                ordered_data[field] = data[field]
        
        return ordered_data
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a single frontmatter file
        
        Args:
            file_path: Path to frontmatter YAML file
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Determine domain from file path or data
        domain = data.get('domain')
        if not domain:
            # Infer from path
            parts = file_path.parts
            if 'materials' in parts:
                domain = 'materials'
            elif 'contaminants' in parts:
                domain = 'contaminants'
            elif 'compounds' in parts:
                domain = 'compounds'
            elif 'settings' in parts:
                domain = 'settings'
            else:
                return False, [f"Cannot determine domain for file: {file_path}"]
        
        return self.validate_field_order(data, domain)
    
    def reorder_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """
        Reorder fields in a frontmatter file
        
        Args:
            file_path: Path to frontmatter YAML file
            dry_run: If True, don't write changes
        
        Returns:
            True if file was reordered, False if no changes needed
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Determine domain
        domain = data.get('domain')
        if not domain:
            parts = file_path.parts
            if 'materials' in parts:
                domain = 'materials'
            elif 'contaminants' in parts:
                domain = 'contaminants'
            elif 'compounds' in parts:
                domain = 'compounds'
            elif 'settings' in parts:
                domain = 'settings'
        
        # Reorder
        ordered_data = self.reorder_fields(data, domain)
        
        # Check if changed
        if list(ordered_data.keys()) == list(data.keys()):
            return False  # No changes needed
        
        if not dry_run:
            # Write reordered data
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    dict(ordered_data),
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    indent=2
                )
        
        return True
    
    def validate_domain(self, domain: str) -> Dict:
        """
        Validate all files in a domain
        
        Args:
            domain: Domain name (materials, contaminants, compounds, settings)
        
        Returns:
            Dictionary with validation results
        """
        domain_dir = self.frontmatter_dir / domain
        if not domain_dir.exists():
            return {
                'total': 0,
                'valid': 0,
                'invalid': 0,
                'errors': [f"Domain directory not found: {domain_dir}"]
            }
        
        files = list(domain_dir.glob('*.yaml'))
        results = {
            'total': len(files),
            'valid': 0,
            'invalid': 0,
            'files_with_issues': []
        }
        
        for file_path in files:
            is_valid, issues = self.validate_file(file_path)
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['files_with_issues'].append({
                    'file': file_path.name,
                    'issues': issues
                })
        
        return results
    
    def reorder_domain(self, domain: str, dry_run: bool = False) -> Dict:
        """
        Reorder all files in a domain
        
        Args:
            domain: Domain name
            dry_run: If True, don't write changes
        
        Returns:
            Dictionary with reorder results
        """
        domain_dir = self.frontmatter_dir / domain
        if not domain_dir.exists():
            return {
                'total': 0,
                'reordered': 0,
                'unchanged': 0,
                'errors': [f"Domain directory not found: {domain_dir}"]
            }
        
        files = list(domain_dir.glob('*.yaml'))
        results = {
            'total': len(files),
            'reordered': 0,
            'unchanged': 0,
            'files_reordered': []
        }
        
        for file_path in files:
            try:
                was_reordered = self.reorder_file(file_path, dry_run=dry_run)
                if was_reordered:
                    results['reordered'] += 1
                    results['files_reordered'].append(file_path.name)
                else:
                    results['unchanged'] += 1
            except Exception as e:
                if 'errors' not in results:
                    results['errors'] = []
                results['errors'].append(f"{file_path.name}: {str(e)}")
        
        return results


def main():
    """CLI for validating/reordering frontmatter fields"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate/reorder frontmatter field order')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings'],
                       help='Domain to validate/reorder')
    parser.add_argument('--reorder', action='store_true',
                       help='Reorder files to match specification')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    
    args = parser.parse_args()
    
    validator = FrontmatterFieldOrderValidator()
    
    if args.reorder:
        # Reorder mode
        if not args.domain:
            print("❌ --domain required for reorder operation")
            sys.exit(1)
        
        print(f"{'DRY RUN: ' if args.dry_run else ''}Reordering {args.domain} domain files...")
        results = validator.reorder_domain(args.domain, dry_run=args.dry_run)
        
        print(f"\n{'DRY RUN ' if args.dry_run else ''}REORDER RESULTS:")
        print(f"  Total files: {results['total']}")
        print(f"  Reordered: {results['reordered']}")
        print(f"  Unchanged: {results['unchanged']}")
        
        if results.get('errors'):
            print(f"\n❌ ERRORS:")
            for error in results['errors']:
                print(f"  {error}")
        
        if results['files_reordered']:
            print(f"\n📝 Files reordered:")
            for filename in results['files_reordered'][:10]:
                print(f"  {filename}")
            if len(results['files_reordered']) > 10:
                print(f"  ... and {len(results['files_reordered']) - 10} more")
    
    else:
        # Validation mode
        if not args.domain:
            print("❌ --domain required")
            sys.exit(1)
        
        print(f"Validating {args.domain} domain files...")
        results = validator.validate_domain(args.domain)
        
        print(f"\nVALIDATION RESULTS:")
        print(f"  Total files: {results['total']}")
        print(f"  Valid: {results['valid']} ({results['valid']/results['total']*100:.1f}%)")
        print(f"  Invalid: {results['invalid']}")
        
        if results['files_with_issues']:
            print(f"\n❌ FILES WITH ISSUES:")
            for item in results['files_with_issues'][:5]:
                print(f"\n  {item['file']}:")
                for issue in item['issues']:
                    print(f"    - {issue}")
            if len(results['files_with_issues']) > 5:
                print(f"\n  ... and {len(results['files_with_issues']) - 5} more files with issues")
        else:
            print(f"\n✅ All {results['total']} files valid!")


if __name__ == '__main__':
    main()
