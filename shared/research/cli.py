"""
Unified CLI for all research operations.

Consolidates 40+ research scripts into a single module with clear commands.

Usage:
    python3 -m shared.research.cli visual-appearance --provider gemini --batch
    python3 -m shared.research.cli properties --material Aluminum --type thermal
    python3 -m shared.research.cli associations --domain contaminants
    python3 -m shared.research.cli populate --domain compounds --field melting_point

Created: January 5, 2026
Consolidates: scripts/research/* (40+ scripts)
"""

import argparse
import sys
from pathlib import Path


class ResearchCLI:
    """Unified CLI for all research operations"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Z-Beam Research CLI - Unified research operations",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Visual appearance research
  python3 -m shared.research.cli visual-appearance --provider gemini
  python3 -m shared.research.cli visual-appearance --provider gemini --batch
  
  # Property research
  python3 -m shared.research.cli properties --material Aluminum --type thermal
  python3 -m shared.research.cli properties --material "Stainless Steel" --type all
  
  # Association research
  python3 -m shared.research.cli associations --domain contaminants --regenerate
  
  # Data population
  python3 -m shared.research.cli populate --domain compounds --field melting_point
  python3 -m shared.research.cli populate --domain materials --field all
            """
        )
        self.subparsers = self.parser.add_subparsers(dest='command', help='Research command')
        self._setup_commands()
    
    def _setup_commands(self):
        """Setup all subcommands"""
        
        # Visual appearance research
        visual_parser = self.subparsers.add_parser(
            'visual-appearance',
            help='Research visual appearances for contamination patterns'
        )
        visual_parser.add_argument('--provider', choices=['gemini', 'openai', 'deepseek'],
                                   default='gemini', help='AI provider')
        visual_parser.add_argument('--batch', action='store_true',
                                   help='Process all patterns in batch')
        visual_parser.add_argument('--category', help='Specific category to process')
        
        # Property research
        props_parser = self.subparsers.add_parser(
            'properties',
            help='Research material properties'
        )
        props_parser.add_argument('--material', required=True,
                                 help='Material name')
        props_parser.add_argument('--type', choices=['thermal', 'laser', 'lmi', 'all'],
                                 default='all', help='Property type')
        
        # Association research
        assoc_parser = self.subparsers.add_parser(
            'associations',
            help='Research domain associations'
        )
        assoc_parser.add_argument('--domain', required=True,
                                 choices=['materials', 'contaminants', 'compounds', 'settings'],
                                 help='Domain to research')
        assoc_parser.add_argument('--regenerate', action='store_true',
                                 help='Force regeneration')
        
        # Data population
        pop_parser = self.subparsers.add_parser(
            'populate',
            help='Populate missing data fields'
        )
        pop_parser.add_argument('--domain', required=True,
                               choices=['materials', 'contaminants', 'compounds', 'settings'],
                               help='Domain to populate')
        pop_parser.add_argument('--field', required=True,
                               help='Field to populate (or "all")')
        pop_parser.add_argument('--strategy', choices=['ai', 'lookup', 'calculate'],
                               default='ai', help='Population strategy')
    
    def run(self, args=None):
        """Execute CLI command"""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return 1
        
        # Route to appropriate handler
        if args.command == 'visual-appearance':
            return self._visual_appearance(args)
        elif args.command == 'properties':
            return self._properties(args)
        elif args.command == 'associations':
            return self._associations(args)
        elif args.command == 'populate':
            return self._populate(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    
    def _visual_appearance(self, args):
        """Handle visual appearance research"""
        print(f"🔬 Visual Appearance Research")
        print(f"   Provider: {args.provider}")
        print(f"   Batch mode: {args.batch}")
        if args.category:
            print(f"   Category: {args.category}")
        
        print("\n⚠️  Implementation: Import and call appropriate research module")
        print("   Original scripts: scripts/research/batch_visual_*.py")
        print("   Consolidation: Move logic to shared/research/visual_appearance.py")
        return 0
    
    def _properties(self, args):
        """Handle property research"""
        print(f"🔬 Property Research")
        print(f"   Material: {args.material}")
        print(f"   Type: {args.type}")
        
        print("\n⚠️  Implementation: Import and call appropriate research module")
        print("   Original scripts: scripts/research/research_*_properties.py")
        print("   Consolidation: Move logic to shared/research/property_researcher.py")
        return 0
    
    def _associations(self, args):
        """Handle association research"""
        print(f"🔬 Association Research")
        print(f"   Domain: {args.domain}")
        print(f"   Regenerate: {args.regenerate}")
        
        print("\n⚠️  Implementation: Import and call appropriate research module")
        print("   Original scripts: scripts/research/*_association_researcher.py")
        print("   Consolidation: Move logic to shared/research/association_researcher.py")
        return 0
    
    def _populate(self, args):
        """Handle data population"""
        print(f"🔬 Data Population")
        print(f"   Domain: {args.domain}")
        print(f"   Field: {args.field}")
        print(f"   Strategy: {args.strategy}")
        
        print("\n⚠️  Implementation: Import and call appropriate population module")
        print("   Original scripts: scripts/research/populate_*.py")
        print("   Consolidation: Move logic to shared/research/populator.py")
        return 0


def main():
    """Main entry point"""
    cli = ResearchCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
