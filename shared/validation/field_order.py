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

from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml


class FrontmatterFieldOrderValidator:
    """Validates and reorders frontmatter fields"""

    REQUIRED_FIELD_ALIASES = {
        'chemical_formula': {'chemicalFormula'},
        'page_title': {'pageTitle', 'title'},
        'schema_version': {'schemaVersion'},
        'content_type': {'contentType'},
        'cas_number': {'casNumber'},
        'molecular_weight': {'molecularWeight'},
    }
    
    def __init__(
        self,
        schema_file: Optional[Path] = None,
        allow_unexpected_fields: bool = True,
        enforce_required_fields: bool = False,
    ):
        """
        Initialize validator
        
        Args:
            schema_file: Path to FrontmatterFieldOrder.yaml (auto-detected if None)
        """
        if schema_file is None:
            schema_file = Path(__file__).parent.parent.parent / 'data' / 'schemas' / 'FrontmatterFieldOrder.yaml'
        
        self.schema_file = Path(schema_file)
        self.schema: Optional[Dict] = None
        self.allow_unexpected_fields = allow_unexpected_fields
        self.enforce_required_fields = enforce_required_fields
        project_root = Path(__file__).parent.parent.parent
        local_frontmatter = project_root / 'frontmatter'
        sibling_frontmatter = project_root.parent / 'z-beam' / 'frontmatter'

        # Prefer local frontmatter when available; otherwise use canonical sibling project frontmatter
        self.frontmatter_dir = local_frontmatter if local_frontmatter.exists() else sibling_frontmatter
    
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

        if domain not in self.schema:
            raise KeyError(f"Domain '{domain}' is not defined in field-order schema")

        domain_spec = self.schema[domain]
        if not isinstance(domain_spec, dict):
            raise RuntimeError(f"Invalid domain spec for '{domain}': expected dictionary")
        
        # NEW: Support unified base schema architecture
        if 'base_schema' not in domain_spec:
            raise RuntimeError(f"Domain spec for '{domain}' missing required 'base_schema' flag")

        if domain_spec['base_schema']:
            return self._build_unified_field_order(domain, domain_spec)
        
        # Legacy: Direct field_order list
        if 'field_order' not in domain_spec:
            raise RuntimeError(f"Legacy domain spec for '{domain}' missing required 'field_order' list")
        if not isinstance(domain_spec['field_order'], list):
            raise RuntimeError(f"Domain spec field_order for '{domain}' must be a list")
        return domain_spec['field_order']
    
    def _build_unified_field_order(self, domain: str, domain_spec: Dict) -> List[str]:
        """Build field order from base schema + domain extensions"""
        if not self.schema:
            self.load_schema()

        if 'base_fields' not in self.schema:
            raise RuntimeError("Field-order schema missing required 'base_fields' section")
        base_fields = self.schema['base_fields']
        if not isinstance(base_fields, dict):
            raise RuntimeError("Schema 'base_fields' must be a dictionary")

        if 'extensions' not in domain_spec:
            raise RuntimeError(f"Domain spec for '{domain}' missing required 'extensions' section")
        extensions = domain_spec['extensions']
        if not isinstance(extensions, dict):
            raise RuntimeError(f"Domain spec extensions for '{domain}' must be a dictionary")

        required_base_groups = [
            'universal_core',
            'identity_extensions',
            'system_metadata',
            'navigation_core',
            'seo_metadata',
            'content_common',
            'media_standard',
            'relationships_standard',
            'author_standard',
            'card_standard',
        ]
        for group in required_base_groups:
            if group not in base_fields:
                raise RuntimeError(f"Schema base_fields missing required group '{group}'")
            if not isinstance(base_fields[group], list):
                raise RuntimeError(f"Schema base_fields['{group}'] must be a list")

        required_extension_groups = [
            'identity_additions',
            'content_additions',
            'domain_sections',
            'content_removals',
        ]
        for group in required_extension_groups:
            if group not in extensions:
                raise RuntimeError(f"Domain extensions for '{domain}' missing required group '{group}'")
            if not isinstance(extensions[group], list):
                raise RuntimeError(f"Domain extensions['{group}'] for '{domain}' must be a list")
        
        # Build unified order following tier hierarchy
        field_order = []
        
        # TIER 1-2: Universal + Common Identity
        field_order.extend(base_fields['universal_core'])
        field_order.extend(base_fields['identity_extensions'])
        
        # Add domain-specific identity additions
        field_order.extend(extensions['identity_additions'])
        
        # TIER 3: System Metadata
        field_order.extend(base_fields['system_metadata'])
        
        # TIER 4-5: Navigation & SEO
        field_order.extend(base_fields['navigation_core'])
        field_order.extend(base_fields['seo_metadata'])
        
        # TIER 6: Content
        field_order.extend(base_fields['content_common'])
        field_order.extend(extensions['content_additions'])
        
        # TIER 7-9: Media, Relationships, Author
        field_order.extend(base_fields['media_standard'])
        field_order.extend(base_fields['relationships_standard'])
        field_order.extend(base_fields['author_standard'])
        field_order.extend(base_fields['card_standard'])
        
        # Domain-specific sections
        field_order.extend(extensions['domain_sections'])

        # Optional domain-specific removals from unified base
        removals = set(extensions['content_removals'])
        if removals:
            field_order = [field for field in field_order if field not in removals]

        # De-duplicate while preserving order
        seen = set()
        deduped = []
        for field in field_order:
            if field not in seen:
                seen.add(field)
                deduped.append(field)
        
        return deduped
    
    def get_required_fields(self, domain: str) -> Set[str]:
        """Get required fields for a domain"""
        if not self.schema:
            self.load_schema()

        if domain not in self.schema:
            raise KeyError(f"Domain '{domain}' is not defined in field-order schema")
        domain_spec = self.schema[domain]
        if not isinstance(domain_spec, dict):
            raise RuntimeError(f"Invalid domain spec for '{domain}': expected dictionary")
        
        # Default required fields from base schema
        base_required = {'id', 'name', 'contentType', 'schemaVersion'}
        
        # Add domain-specific required fields
        if 'required_fields' not in domain_spec:
            raise RuntimeError(f"Domain spec for '{domain}' missing required 'required_fields' list")
        if not isinstance(domain_spec['required_fields'], list):
            raise RuntimeError(f"Domain spec required_fields for '{domain}' must be a list")
        domain_required = set(domain_spec['required_fields'])
        
        return base_required.union(domain_required)
    
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
        
        # Optional completeness check (separate concern from pure order validation)
        if self.enforce_required_fields:
            required_fields = self.get_required_fields(domain)

            def _has_required_field(field_name: str) -> bool:
                if field_name in actual_fields:
                    return True
                aliases = self.REQUIRED_FIELD_ALIASES[field_name] if field_name in self.REQUIRED_FIELD_ALIASES else set()
                return any(alias in actual_fields for alias in aliases)

            missing_required = {field for field in required_fields if not _has_required_field(field)}
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
        if not self.allow_unexpected_fields:
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
            elif 'applications' in parts:
                domain = 'applications'
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
            elif 'applications' in parts:
                domain = 'applications'
        
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
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Validate/reorder frontmatter field order')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings', 'applications'],
                       help='Domain to validate/reorder')
    parser.add_argument('--reorder', action='store_true',
                       help='Reorder files to match specification')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    parser.add_argument('--enforce-required-fields', action='store_true',
                       help='Also fail validation when required fields are missing (completeness check)')
    
    args = parser.parse_args()
    
    validator = FrontmatterFieldOrderValidator(
        enforce_required_fields=args.enforce_required_fields
    )
    
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
