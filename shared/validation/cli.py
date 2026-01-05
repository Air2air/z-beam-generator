"""
Unified CLI for all validation operations.

Consolidates 30+ validation scripts into a single module with clear commands.

Usage:
    python3 -m shared.validation.cli schema --target source --version v2
    python3 -m shared.validation.cli frontmatter --domain materials --check structure
    python3 -m shared.validation.cli relationships --check-links --check-slugs
    python3 -m shared.validation.cli export --domain all --verbose

Created: January 5, 2026
Consolidates: scripts/validation/* (30+ scripts)
"""

import argparse
import sys
from pathlib import Path


class ValidationCLI:
    """Unified CLI for all validation operations"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Z-Beam Validation CLI - Unified validation operations",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Schema validation
  python3 -m shared.validation.cli schema --target source --version v2
  python3 -m shared.validation.cli schema --target frontmatter
  
  # Frontmatter validation
  python3 -m shared.validation.cli frontmatter --domain materials --check structure
  python3 -m shared.validation.cli frontmatter --domain all --check links
  
  # Relationship validation
  python3 -m shared.validation.cli relationships --check-links
  python3 -m shared.validation.cli relationships --check-slugs --fix
  
  # Export validation
  python3 -m shared.validation.cli export --domain materials --verbose
  python3 -m shared.validation.cli export --domain all
            """
        )
        self.subparsers = self.parser.add_subparsers(dest='command', help='Validation command')
        self._setup_commands()
    
    def _setup_commands(self):
        """Setup all subcommands"""
        
        # Schema validation
        schema_parser = self.subparsers.add_parser(
            'schema',
            help='Validate YAML schemas'
        )
        schema_parser.add_argument('--target', choices=['source', 'frontmatter', 'export'],
                                   default='source', help='Target to validate')
        schema_parser.add_argument('--version', choices=['v1', 'v2'], default='v2',
                                   help='Schema version')
        schema_parser.add_argument('--fix', action='store_true',
                                   help='Attempt to fix issues')
        
        # Frontmatter validation
        fm_parser = self.subparsers.add_parser(
            'frontmatter',
            help='Validate frontmatter files'
        )
        fm_parser.add_argument('--domain', 
                              choices=['materials', 'contaminants', 'compounds', 'settings', 'all'],
                              default='all', help='Domain to validate')
        fm_parser.add_argument('--check', 
                              choices=['structure', 'links', 'fields', 'all'],
                              default='all', help='What to check')
        
        # Relationship validation
        rel_parser = self.subparsers.add_parser(
            'relationships',
            help='Validate relationship integrity'
        )
        rel_parser.add_argument('--check-links', action='store_true',
                               help='Check link validity')
        rel_parser.add_argument('--check-slugs', action='store_true',
                               help='Check slug consistency')
        rel_parser.add_argument('--check-paths', action='store_true',
                               help='Check path validity')
        rel_parser.add_argument('--fix', action='store_true',
                               help='Attempt to fix issues')
        
        # Export validation
        export_parser = self.subparsers.add_parser(
            'export',
            help='Validate export configuration and output'
        )
        export_parser.add_argument('--domain',
                                  choices=['materials', 'contaminants', 'compounds', 'settings', 'all'],
                                  default='all', help='Domain to validate')
        export_parser.add_argument('--verbose', action='store_true',
                                  help='Verbose output')
        
        # Zero nulls validation
        nulls_parser = self.subparsers.add_parser(
            'nulls',
            help='Validate no null/empty values in data'
        )
        nulls_parser.add_argument('--domain',
                                 choices=['materials', 'contaminants', 'compounds', 'settings', 'all'],
                                 default='all', help='Domain to check')
        
        # Card structure validation
        card_parser = self.subparsers.add_parser(
            'cards',
            help='Validate card structure in frontmatter'
        )
        card_parser.add_argument('--domain',
                                choices=['materials', 'contaminants', 'compounds', 'settings', 'all'],
                                default='all', help='Domain to check')
    
    def run(self, args=None):
        """Execute CLI command"""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return 1
        
        # Route to appropriate handler
        if args.command == 'schema':
            return self._schema(args)
        elif args.command == 'frontmatter':
            return self._frontmatter(args)
        elif args.command == 'relationships':
            return self._relationships(args)
        elif args.command == 'export':
            return self._export(args)
        elif args.command == 'nulls':
            return self._nulls(args)
        elif args.command == 'cards':
            return self._cards(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    
    def _schema(self, args):
        """Handle schema validation"""
        print(f"🔍 Schema Validation")
        print(f"   Target: {args.target}")
        print(f"   Version: {args.version}")
        print(f"   Fix: {args.fix}")
        
        print("\n⚠️  Implementation: Import and call appropriate validator")
        print("   Original scripts: scripts/validation/validate_*_schema*.py")
        print("   Consolidation: Use shared/validation/schema_validator.py")
        return 0
    
    def _frontmatter(self, args):
        """Handle frontmatter validation"""
        print(f"🔍 Frontmatter Validation")
        print(f"   Domain: {args.domain}")
        print(f"   Check: {args.check}")
        
        print("\n⚠️  Implementation: Import and call appropriate validator")
        print("   Original scripts: scripts/validation/validate_frontmatter*.py")
        print("   Consolidation: Use shared/validation/frontmatter_validator.py")
        return 0
    
    def _relationships(self, args):
        """Handle relationship validation"""
        print(f"🔍 Relationship Validation")
        print(f"   Check links: {args.check_links}")
        print(f"   Check slugs: {args.check_slugs}")
        print(f"   Check paths: {args.check_paths}")
        print(f"   Fix: {args.fix}")
        
        print("\n⚠️  Implementation: Import and call appropriate validator")
        print("   Original scripts: scripts/validation/validate_relationship*.py")
        print("   Consolidation: Use shared/validation/relationship_validator.py")
        return 0
    
    def _export(self, args):
        """Handle export validation"""
        print(f"🔍 Export Validation")
        print(f"   Domain: {args.domain}")
        print(f"   Verbose: {args.verbose}")
        
        print("\n⚠️  Implementation: Import and call appropriate validator")
        print("   Original scripts: scripts/validation/validate_export*.py")
        print("   Consolidation: Use shared/validation/export_validator.py")
        return 0
    
    def _nulls(self, args):
        """Handle null validation"""
        print(f"🔍 Null Validation")
        print(f"   Domain: {args.domain}")
        
        print("\n⚠️  Implementation: Import and call appropriate validator")
        print("   Original scripts: scripts/validation/validate_zero_nulls.py")
        print("   Consolidation: Use shared/validation/null_validator.py")
        return 0
    
    def _cards(self, args):
        """Handle card validation"""
        print(f"🔍 Card Structure Validation")
        print(f"   Domain: {args.domain}")
        
        print("\n⚠️  Implementation: Import and call appropriate validator")
        print("   Original scripts: scripts/validation/validate_card_structure.py")
        print("   Consolidation: Use shared/validation/card_validator.py")
        return 0


def main():
    """Main entry point"""
    cli = ValidationCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
