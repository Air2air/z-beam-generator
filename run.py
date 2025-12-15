#!/usr/bin/env python3
"""
Z-Beam Generator - Main CLI Entry Point

Commands:
  --postprocess    Refine existing populated text fields
  --generate       Generate new content (future implementation)
  --export         Export to frontmatter (future implementation)
"""

import sys
import argparse
from shared.commands.postprocess import PostprocessCommand


def postprocess_command(args):
    """Execute postprocessing command"""
    
    # Validate required arguments
    if not args.domain:
        print("❌ Error: --domain is required for postprocessing")
        print("   Available: materials, contaminants, settings, compounds")
        sys.exit(1)
    
    if not args.field:
        print("❌ Error: --field is required for postprocessing")
        print("   Materials: material_description, micro, faq")
        print("   Contaminants: description, micro, faq")
        print("   Settings: settings_description, material_challenges")
        print("   Compounds: compound_description, health_effects, exposure_guidelines")
        sys.exit(1)
    
    # Create postprocess command
    try:
        cmd = PostprocessCommand(args.domain, args.field)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Execute based on mode
    if args.all:
        # Batch process all items
        results = cmd.postprocess_all(
            batch_size=args.batch_size,
            dry_run=args.dry_run
        )
        
        # Summary
        improved = sum(1 for r in results if r.get('improved'))
        print(f"\n✅ Batch complete: {improved}/{len(results)} items improved")
        
    elif args.item:
        # Process single item
        result = cmd.postprocess_item(args.item, dry_run=args.dry_run)
        
        if result.get('improved'):
            print(f"\n✅ Success: Content improved for {args.item}")
        else:
            print(f"\n⚠️  No improvement: Original content kept for {args.item}")
    
    else:
        print("❌ Error: Either --item <name> or --all is required")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Z-Beam Generator - Content generation and management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Postprocess single item
  python3 run.py --postprocess --domain materials --item "Aluminum" --field material_description

  # Postprocess all items (dry run)
  python3 run.py --postprocess --domain materials --field micro --all --dry-run

  # Batch postprocess with checkpoint every 5 items
  python3 run.py --postprocess --domain contaminants --field description --all --batch-size 5

  # Postprocess all fields for one item
  python3 run.py --postprocess --domain materials --item "Steel" --field material_description
  python3 run.py --postprocess --domain materials --item "Steel" --field micro
  python3 run.py --postprocess --domain materials --item "Steel" --field faq
        """
    )
    
    # Main commands
    parser.add_argument('--postprocess', action='store_true',
                        help='Postprocess existing populated text fields')
    
    # Postprocessing arguments
    parser.add_argument('--domain', type=str,
                        choices=['materials', 'contaminants', 'settings', 'compounds'],
                        help='Domain to postprocess')
    parser.add_argument('--field', type=str,
                        help='Field type to postprocess (e.g., description, micro, faq)')
    parser.add_argument('--item', type=str,
                        help='Specific item name to postprocess')
    parser.add_argument('--all', action='store_true',
                        help='Postprocess all items in domain')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='Checkpoint interval for batch operations (default: 10)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Compare versions without saving (preview mode)')
    
    args = parser.parse_args()
    
    # Execute command
    if args.postprocess:
        postprocess_command(args)
    else:
        parser.print_help()
        print("\n❌ Error: No command specified")
        print("   Use --postprocess to refine existing content")
        sys.exit(1)


if __name__ == '__main__':
    main()
