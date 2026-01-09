#!/usr/bin/env python3
"""
Z-Beam Generator - Main CLI Entry Point

Commands:
  --postprocess    Refine existing populated text fields
  --generate       Generate new content (future implementation)
  --export         Export frontmatter using Universal Exporter
  --export-all     Export all domains to production
  --backfill       Populate source YAML data permanently
  --backfill-all   Backfill all domains
"""

import sys
import argparse
import subprocess
import yaml
import time
from pathlib import Path
from shared.commands.postprocess import PostprocessCommand
from export.core.frontmatter_exporter import FrontmatterExporter
from export.config.loader import load_domain_config
from export.performance import ParallelExporter, get_yaml_cache


def postprocess_command(args):
    """Execute postprocessing command"""
    
    # Validate required arguments
    if not args.domain:
        print("❌ Error: --domain is required for postprocessing")
        print("   Available: materials, contaminants, settings, compounds")
        sys.exit(1)
    
    if not args.field:
        print("❌ Error: --field is required for postprocessing")
        print("   Materials: pageDescription, micro, faq")
        print("   Contaminants: pageDescription, micro, faq")
        print("   Settings: settings_description, challenges")
        print("   Compounds: pageDescription, health_effects, exposure_guidelines")
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


def export_command(args):
    """Execute export command using Universal Exporter"""
    
    # Validate domain
    if not args.domain:
        print("❌ Error: --domain is required for export")
        print("   Available: materials, contaminants, compounds, settings")
        sys.exit(1)
    
    try:
        # Load domain configuration
        config = load_domain_config(args.domain)
        print(f"✅ Loaded config: export/config/{args.domain}.yaml")
        
        # Create exporter
        exporter = FrontmatterExporter(config)
        print(f"✅ Exporter initialized")
        print(f"   Source: {exporter.source_file}")
        print(f"   Output: {exporter.output_path}")
        
        # Export
        force = not args.skip_existing
        print(f"\n🔄 Exporting {args.domain}...")
        results = exporter.export_all(force=force)
        
        # Summary
        exported = sum(1 for success in results.values() if success)
        skipped = len(results) - exported
        print(f"\n✅ Export complete:")
        print(f"   Exported: {exported}")
        if skipped > 0:
            print(f"   Skipped: {skipped} (existing files, use --force to overwrite)")
        
        # Run link integrity validation
        print(f"\n🔍 Running link integrity validation for {args.domain}...")
        validation_result = subprocess.run(
            ['python3', 'scripts/validation/verify_frontmatter_links.py', '--domain', args.domain],
            capture_output=True,
            text=True
        )
        
        # Show validation output
        if validation_result.stdout:
            print(validation_result.stdout)
        
        if validation_result.returncode != 0:
            print(f"⚠️  Link validation found issues (exit code: {validation_result.returncode})")
            print(f"   Review errors above. Use scripts/validation/verify_frontmatter_links.py for details.")
        else:
            print(f"✅ Link integrity validation passed")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)


def export_all_command(args):
    """Export all domains to production (with parallel processing)"""
    
    domains = ['materials', 'contaminants', 'compounds', 'settings']
    use_parallel = getattr(args, 'parallel', True)  # Default to parallel
    
    print("="*80)
    print(f"🚀 EXPORTING ALL DOMAINS TO PRODUCTION {'(PARALLEL)' if use_parallel else '(SEQUENTIAL)'}")
    print("="*80)
    
    # Step 1: Validate source data integrity BEFORE export
    print("\n" + "="*80)
    print("🔍 STEP 1: VALIDATING SOURCE DATA INTEGRITY")
    print("="*80)
    
    data_validation_result = subprocess.run(
        ['python3', 'scripts/validation/verify_data_integrity.py'],
        capture_output=True,
        text=True
    )
    
    if data_validation_result.stdout:
        print(data_validation_result.stdout)
    
    if data_validation_result.returncode != 0:
        print("\n❌ EXPORT ABORTED: Data integrity validation failed")
        print("   Fix broken references in source data before exporting")
        print("   Run: python3 scripts/validation/verify_data_integrity.py")
        sys.exit(1)
    
    print("\n✅ Source data integrity validated")
    
    # Step 2: Export domains (parallel or sequential)
    print("\n" + "="*80)
    print("📦 STEP 2: EXPORTING DOMAINS")
    print("="*80)
    
    start_time = time.time()
    
    if use_parallel:
        # Use parallel export for 3-4x speedup
        parallel_exporter = ParallelExporter(max_workers=4)
        results = parallel_exporter.export_all(skip_existing=args.skip_existing)
        
        # Print performance summary
        print(parallel_exporter.get_performance_summary(results))
        
        total_exported = sum(r.get('exported', 0) for r in results.values())
    else:
        # Use sequential export (original behavior)
        total_exported = 0
        for domain in domains:
            print(f"\n📦 {domain.upper()}:")
            
            try:
                config = load_domain_config(domain)
                exporter = FrontmatterExporter(config)
                results_dict = exporter.export_all(force=not args.skip_existing)
                
                exported = sum(1 for success in results_dict.values() if success)
                total_exported += exported
                print(f"   ✅ {exported}/{len(results_dict)} files")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    elapsed = time.time() - start_time
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"✅ TOTAL: {total_exported} files exported in {elapsed:.1f}s")
    print(f"⚡ Performance: {total_exported/elapsed:.1f} files/second")
    if use_parallel:
        print(f"💡 Parallel mode saved ~{(elapsed * 3 - elapsed):.0f}s compared to sequential")
    
    # Print cache statistics
    cache = get_yaml_cache()
    cache.print_stats()
    
    # Step 3: Validate exported frontmatter links
    print("\n" + "="*80)
    print("🔍 STEP 3: VALIDATING EXPORTED FRONTMATTER")
    print("="*80)
    
    frontmatter_validation_result = subprocess.run(
        ['python3', 'scripts/validation/verify_frontmatter_links.py'],
        capture_output=True,
        text=True
    )
    
    if frontmatter_validation_result.stdout:
        print(frontmatter_validation_result.stdout)
    
    if frontmatter_validation_result.returncode != 0:
        print("\n⚠️  DEPLOYMENT WARNING: Frontmatter validation found issues")
        print("   Review errors above before deploying to production")
        print("   Run: python3 scripts/validation/verify_frontmatter_links.py")
    else:
        print("\n✅ Frontmatter link integrity validated")
    
    print("="*80)


def backfill_command(args):
    """Execute backfill command to populate source YAML permanently"""
    
    # Import registry and load generator
    from generation.backfill.registry import BackfillRegistry
    
    # Load backfill configuration
    config_file = Path(f'generation/backfill/config/{args.domain}.yaml')
    if not config_file.exists():
        print(f"❌ Error: No backfill config for domain: {args.domain}")
        print(f"   Available domains: materials, contaminants, compounds, settings")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Run specific generator or all
    if args.generator:
        # Find generator config
        generator_config = next(
            (g for g in config['generators'] if g['type'] == args.generator),
            None
        )
        if not generator_config:
            print(f"❌ Error: Generator not found: {args.generator}")
            print(f"   Available generators: {[g['type'] for g in config['generators']]}")
            sys.exit(1)
        
        # Add dry-run flag
        generator_config['dry_run'] = args.dry_run
        
        # Create and run generator
        generator = BackfillRegistry.create(generator_config)
        stats = generator.backfill_all()
        
        if not args.dry_run and stats['modified'] > 0:
            print(f"\n✅ Backfill complete: {stats['modified']} items modified")
        elif args.dry_run:
            print(f"\n🔍 DRY RUN complete: Would modify {stats['modified']} items")
        
    else:
        # Run all generators
        print(f"\\n{'='*80}")
        print(f"🚀 RUNNING ALL BACKFILL GENERATORS FOR: {args.domain.upper()}")
        print(f"{'='*80}\\n")
        
        total_modified = 0
        for gen_config in config['generators']:
            gen_config['dry_run'] = args.dry_run
            generator = BackfillRegistry.create(gen_config)
            stats = generator.backfill_all()
            total_modified += stats['modified']
        
        if not args.dry_run and total_modified > 0:
            print(f"\\n✅ All backfills complete: {total_modified} total modifications")
        elif args.dry_run:
            print(f"\\n🔍 DRY RUN complete: Would modify {total_modified} total items")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Z-Beam Generator - Content generation and management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export specific domain
  python3 run.py --export --domain materials
  python3 run.py --export --domain compounds --skip-existing

  # Export all domains to production
  python3 run.py --export-all

  # Backfill source data permanently
  python3 run.py --backfill --domain contaminants --generator pageDescription --dry-run
  python3 run.py --backfill --domain contaminants --generator pageDescription
  python3 run.py --backfill --domain contaminants  # Run all generators

  # Postprocess single item
  python3 run.py --postprocess --domain materials --item "Aluminum" --field pageDescription

  # Postprocess all items (dry run)
  python3 run.py --postprocess --domain materials --field micro --all --dry-run

  # Batch postprocess with checkpoint every 5 items
  python3 run.py --postprocess --domain contaminants --field pageDescription --all --batch-size 5

  # Postprocess all fields for one item
  python3 run.py --postprocess --domain materials --item "Steel" --field pageDescription
  python3 run.py --postprocess --domain materials --item "Steel" --field micro
  python3 run.py --postprocess --domain materials --item "Steel" --field faq
        """
    )
    
    # Main commands
    parser.add_argument('--postprocess', action='store_true',
                        help='Postprocess existing populated text fields')
    parser.add_argument('--export', action='store_true',
                        help='Export frontmatter for specific domain using Universal Exporter')
    parser.add_argument('--export-all', action='store_true',
                        help='Export all domains to production')
    parser.add_argument('--backfill', action='store_true',
                        help='Populate source YAML data permanently')
    parser.add_argument('--backfill-all', action='store_true',
                        help='Backfill all domains (future implementation)')
    
    # Export arguments
    parser.add_argument('--skip-existing', action='store_true',
                        help='Skip existing files (default: overwrite)')
    parser.add_argument('--parallel', action='store_true', default=True,
                        help='Use parallel export for --export-all (default: True, use --no-parallel to disable)')
    parser.add_argument('--no-parallel', action='store_false', dest='parallel',
                        help='Disable parallel export (use sequential processing)')
    
    # Backfill arguments
    parser.add_argument('--generator', type=str,
                        help='Specific backfill generator to run (e.g., pageDescription, compound_linkage)')
    
    # Postprocessing arguments
    parser.add_argument('--domain', type=str,
                        choices=['materials', 'contaminants', 'settings', 'compounds'],
                        help='Domain to postprocess')
    parser.add_argument('--field', type=str,
                        help='Field type to postprocess (e.g., pageDescription, micro, faq)')
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
    elif args.export:
        export_command(args)
    elif args.export_all:
        export_all_command(args)
    elif args.backfill:
        backfill_command(args)
    elif args.backfill_all:
        print("❌ --backfill-all not yet implemented")
        print("   Use --backfill --domain <domain> instead")
        sys.exit(1)
    else:
        parser.print_help()
        print("\n❌ Error: No command specified")
        print("   Use --postprocess to refine existing content")
        print("   Use --export to export frontmatter for a domain")
        print("   Use --export-all to export all domains")
        print("   Use --backfill to populate source data permanently")
        sys.exit(1)


if __name__ == '__main__':
    main()
