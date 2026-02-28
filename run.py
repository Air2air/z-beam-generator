#!/usr/bin/env python3
"""
Z-Beam Generator - Main CLI Entry Point

Commands:
  --postprocess    Refine existing populated text fields
  --generate       Generate new content (future implementation)
    --batch-generate Batch generate a field for any domain
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
from typing import List
from shared.utils.material_resolver import material_resolver
from shared.utils.quality_analyzer import quality_analyzer
from shared.services.keyword_seed_service import KeywordSeedService

# Configuration required by ConfigManager
API_PROVIDERS = {
    'grok': {
        'name': 'Grok',
        'model': 'grok-4-0709',
        'default_model': 'grok-4-0709',
        'env_var': 'GROK_API_KEY',
        'base_url': 'https://api.x.ai',
        'max_tokens': 4096,
        'temperature': 0.7,
        'timeout_connect': 30.0,
        'timeout_read': 300.0,
        'max_retries': 3,
        'retry_delay': 1.0
    },
    'deepseek': {
        'name': 'DeepSeek',
        'model': 'deepseek-chat',
        'default_model': 'deepseek-chat',
        'env_var': 'DEEPSEEK_API_KEY',
        'base_url': 'https://api.deepseek.com',
        'max_tokens': 4096,
        'temperature': 0.7,
        'timeout_connect': 30.0,
        'timeout_read': 300.0,
        'max_retries': 3,
        'retry_delay': 1.0
    },
    'openai': {
        'name': 'OpenAI',
        'model': 'gpt-4',
        'default_model': 'gpt-4',
        'env_var': 'OPENAI_API_KEY',
        'base_url': 'https://api.openai.com/v1',
        'max_tokens': 4096,
        'temperature': 0.7,
        'timeout_connect': 30.0,
        'timeout_read': 300.0,
        'max_retries': 3,
        'retry_delay': 1.0
    }
}

COMPONENT_CONFIG = {
    'micro': {'enabled': True, 'priority': 1},
    'description': {'enabled': True, 'priority': 2},
    'faq': {'enabled': True, 'priority': 3}
}

from shared.commands.postprocess import PostprocessCommand
from export.core.frontmatter_exporter import FrontmatterExporter
from export.config.loader import load_domain_config
from export.performance import ParallelExporter, get_yaml_cache


def _enable_terminal_streaming() -> None:
    """Configure stdout/stderr for immediate line-by-line terminal updates."""
    try:
        # Python 3.7+: force line buffering so generation progress appears immediately.
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        # Fail-safe: streaming configuration should never block command execution.
        pass


def postprocess_command(args):
    """Execute postprocessing command"""

    print("📺 Streaming progress updates to terminal (live)")
    
    # Validate required arguments
    if not args.domain:
        print("❌ Error: --domain is required for postprocessing")
        print("   Available: materials, contaminants, settings, compounds, applications")
        sys.exit(1)
    
    if not args.field:
        print("❌ Error: --field is required for postprocessing")
        print("   Materials: pageDescription, micro, faq")
        print("   Contaminants: pageDescription, micro, faq")
        print("   Settings: settings_description, challenges")
        print("   Compounds: pageDescription, health_effects, exposure_guidelines")
        print("   Applications: pageTitle, pageDescription, micro, faq")
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
        print("   Available: materials, contaminants, compounds, settings, applications")
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
        
        # Export single item or all items
        if args.item:
            print(f"   Filtering: {args.item}")
            # Load source data to get item data
            import yaml
            with open(exporter.source_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            items = data.get(exporter.items_key, {})
            if args.item in items:
                success = exporter.export_single(args.item, items[args.item], force)
                results = {args.item: success}
            else:
                print(f"❌ Item not found: {args.item}")
                sys.exit(1)
        else:
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
    
    domains = ['materials', 'contaminants', 'compounds', 'settings', 'applications']
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
    
    def _run_sequential_export() -> int:
        total = 0
        for domain in domains:
            print(f"\n📦 {domain.upper()}:")

            try:
                config = load_domain_config(domain)
                exporter = FrontmatterExporter(config)
                results_dict = exporter.export_all(force=not args.skip_existing)

                exported = sum(1 for success in results_dict.values() if success)
                total += exported
                print(f"   ✅ {exported}/{len(results_dict)} files")

            except Exception as e:
                print(f"   ❌ Error: {e}")
        return total

    if use_parallel:
        # Use parallel export for 3-4x speedup (fail-fast on failure)
        try:
            parallel_exporter = ParallelExporter(max_workers=4)
            results = parallel_exporter.export_all(skip_existing=args.skip_existing)

            total_exported = sum(r.get('exported', 0) for r in results.values())
            failed_domains = [domain for domain, result in results.items() if not result.get('success')]

            if failed_domains:
                raise RuntimeError(f"Parallel export failed for domains: {', '.join(failed_domains)}")

            print(parallel_exporter.get_performance_summary(results))
        except Exception as e:
            print(f"❌ Parallel export failed: {e}")
            raise
    else:
        # Use sequential export (original behavior)
        total_exported = _run_sequential_export()
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"✅ TOTAL: {total_exported} files exported in {elapsed:.1f}s")
    throughput = (total_exported / elapsed) if elapsed > 0 else 0.0
    print(f"⚡ Performance: {throughput:.1f} files/second")
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

    print("📺 Streaming progress updates to terminal (live)")
    
    # Import registry and load generator
    from generation.backfill.registry import BackfillRegistry

    provider = args.api_provider or 'grok'
    
    # Load backfill configuration
    config_file = Path(f'generation/backfill/config/{args.domain}.yaml')
    if not config_file.exists():
        print(f"❌ Error: No backfill config for domain: {args.domain}")
        print(f"   Available domains: materials, contaminants, compounds, settings, applications")
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
        
        # Add dry-run flag and item filter
        generator_config['dry_run'] = args.dry_run
        generator_config['api_provider'] = provider
        if args.item:
            generator_config['item_filter'] = args.item
        
        # Create and run generator
        print("\n" + "="*80)
        print(f"🚀 BACKFILL GENERATOR: {args.generator} ({args.domain})")
        if args.item:
            print(f"🎯 Item filter: {args.item}")
        print(f"🧪 Dry run: {args.dry_run}")
        print(f"🤖 Provider: {provider}")
        print("="*80)

        generator = BackfillRegistry.create(generator_config)
        stats = generator.backfill_all()

        print("\n📊 Generator stats:")
        for key, value in stats.items():
            print(f"   • {key}: {value}")
        
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
        total_generators = len(config['generators'])
        for idx, gen_config in enumerate(config['generators'], start=1):
            generator_name = gen_config.get('type', 'unknown')
            print(f"\n[{idx}/{total_generators}] 🔄 Running generator: {generator_name}")
            gen_config['dry_run'] = args.dry_run
            gen_config['api_provider'] = provider
            if args.item:
                gen_config['item_filter'] = args.item
            generator = BackfillRegistry.create(gen_config)
            stats = generator.backfill_all()
            total_modified += stats['modified']
            print(f"   ✅ {generator_name} complete: modified={stats.get('modified', 0)}")
        
        if not args.dry_run and total_modified > 0:
            print(f"\\n✅ All backfills complete: {total_modified} total modifications")
        elif args.dry_run:
            print(f"\\n🔍 DRY RUN complete: Would modify {total_modified} total items")


def _load_domain_items(domain: str) -> List[str]:
    """Load all item IDs for a domain from the configured source YAML."""
    config_path = Path(f'domains/{domain}/config.yaml')
    if not config_path.exists():
        raise FileNotFoundError(f"Domain config not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    data_path = config.get('data_path')
    data_root_key = config.get('data_root_key')
    if not data_path or not data_root_key:
        raise ValueError(
            f"Domain config missing required keys data_path/data_root_key: {config_path}"
        )

    source_path = Path(data_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Domain source file not found: {source_path}")

    with open(source_path, 'r', encoding='utf-8') as f:
        source_data = yaml.safe_load(f)

    items = source_data.get(data_root_key, {})
    if not isinstance(items, dict):
        raise ValueError(
            f"Expected dict at root key '{data_root_key}' in {source_path}, got {type(items).__name__}"
        )

    return list(items.keys())


def _create_domain_coordinator(domain: str, api_client):
    """Create the domain-specific coordinator for text generation."""
    if domain == 'materials':
        from domains.materials.coordinator import MaterialsCoordinator
        return MaterialsCoordinator(api_client=api_client)
    if domain == 'contaminants':
        from domains.contaminants.coordinator import ContaminantCoordinator
        return ContaminantCoordinator(api_client=api_client)
    if domain == 'compounds':
        from domains.compounds.coordinator import CompoundCoordinator
        return CompoundCoordinator(api_client=api_client)
    if domain == 'settings':
        from domains.settings.coordinator import SettingCoordinator
        return SettingCoordinator(api_client=api_client)
    if domain == 'applications':
        from domains.applications.coordinator import ApplicationsCoordinator
        return ApplicationsCoordinator(api_client=api_client)

    raise ValueError(f"Unsupported domain: {domain}")


def _run_domain_multifield_generation(domain: str, item_id: str, dry_run: bool) -> None:
    """Run the configured multi-field text generator for one domain item."""
    from generation.backfill.registry import BackfillRegistry

    config_file = Path(f'generation/backfill/config/{domain}.yaml')
    if not config_file.exists():
        raise FileNotFoundError(f"Backfill config missing for domain '{domain}': {config_file}")

    with open(config_file, 'r', encoding='utf-8') as handle:
        config = yaml.safe_load(handle)

    generators = config.get('generators')
    if not isinstance(generators, list) or not generators:
        raise ValueError(f"No generators configured in {config_file}")

    multi_field = next((entry for entry in generators if entry.get('type') == 'multi_field_text'), None)
    selected = multi_field or generators[0]

    if not isinstance(selected, dict):
        raise ValueError(f"Invalid generator configuration in {config_file}")

    selected_config = dict(selected)
    selected_config['dry_run'] = dry_run
    selected_config['item_filter'] = item_id

    print(f"\n🚀 Running generator: {selected_config.get('type', 'unknown')} for {item_id}")
    generator = BackfillRegistry.create(selected_config)
    stats = generator.backfill_all()

    if stats.get('errors', 0) > 0:
        raise RuntimeError(f"Generation completed with errors for {item_id}: {stats}")

    if dry_run:
        return

    with open(selected_config['source_file'], 'r', encoding='utf-8') as handle:
        source_data = yaml.safe_load(handle)

    items = source_data.get(selected_config['items_key'], {})
    item_data = items.get(item_id)
    if not isinstance(item_data, dict):
        raise RuntimeError(f"Generated item '{item_id}' missing from source after generation")

    required_fields = []
    if isinstance(selected_config.get('field'), str):
        required_fields.append(selected_config['field'])

    mapped_fields = selected_config.get('fields', [])
    if isinstance(mapped_fields, list):
        for mapping in mapped_fields:
            if isinstance(mapping, dict) and isinstance(mapping.get('field'), str):
                required_fields.append(mapping['field'])

    missing_fields = []
    for field_path in required_fields:
        field_value = _get_nested_value(item_data, field_path)
        if not isinstance(field_value, str) or not field_value.strip():
            missing_fields.append(field_path)

    if missing_fields:
        raise RuntimeError(
            f"Generation incomplete for {item_id}; missing/empty fields: {', '.join(missing_fields)}"
        )


def _get_nested_value(data: dict, path: str):
    current = data
    for part in path.split('.'):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _export_single_item(domain: str, item_id: str, dry_run: bool) -> None:
    """Export one item to frontmatter to maintain source/frontmatter dual-write."""
    if dry_run:
        print("\n🔍 Dry run: skipping frontmatter export")
        return

    config = load_domain_config(domain)
    exporter = FrontmatterExporter(config)

    with open(exporter.source_file, 'r', encoding='utf-8') as handle:
        source_data = yaml.safe_load(handle)

    items = source_data.get(exporter.items_key, {})
    if item_id not in items:
        raise KeyError(f"Cannot export missing item '{item_id}' from {exporter.source_file}")

    print(f"\n📤 Exporting frontmatter for {item_id}")
    success = exporter.export_single(item_id, items[item_id], force=True)
    if not success:
        raise RuntimeError(f"Frontmatter export failed for {item_id}")


def seed_from_keyword_command(args):
    """Create new item from keyword and optionally generate full text + export frontmatter."""
    if not args.domain:
        print("❌ Error: --domain is required with --seed-from-keyword")
        sys.exit(1)

    keyword = args.seed_from_keyword.strip() if args.seed_from_keyword else ''
    if not keyword:
        print("❌ Error: --seed-from-keyword requires a non-empty keyword")
        sys.exit(1)

    print("=" * 80)
    print("🌱 KEYWORD PAGE SEED")
    print("=" * 80)
    print(f"Domain: {args.domain}")
    print(f"Keyword: {keyword}")
    print(f"Template item: {args.template_item or 'auto'}")
    print(f"Generate text fields: {not args.skip_generate}")
    print(f"Dry run: {args.dry_run}")

    service = KeywordSeedService(args.domain)
    result = service.seed_from_keyword(
        keyword=keyword,
        template_item=args.template_item,
        category=args.category,
        subcategory=args.subcategory,
        dry_run=args.dry_run,
    )

    print(f"\n✅ Seeded item: {result.item_id}")
    print(f"   Source file: {result.data_path}")
    print(f"   Template: {result.used_template_item}")

    if args.dry_run and not args.skip_generate:
        print("\n🔍 Dry run: skipping text generation (seed item is not persisted)")
    elif not args.skip_generate:
        _run_domain_multifield_generation(args.domain, result.item_id, args.dry_run)
    else:
        print("\n⏭️  Skipping text generation by request")

    _export_single_item(args.domain, result.item_id, args.dry_run)

    if not args.dry_run:
        print("\n✅ Complete: source item created, text generated, and frontmatter synced")
    else:
        print("\n✅ Dry run complete: no files were changed")


def batch_generate_command(args):
    """Batch generate a single field for any domain."""
    if not args.domain:
        print("❌ Error: --domain is required for --batch-generate")
        sys.exit(1)
    if not args.field:
        print("❌ Error: --field is required for --batch-generate")
        sys.exit(1)

    if args.all:
        target_items = _load_domain_items(args.domain)
    elif args.items:
        target_items = [value.strip() for value in args.items.split(',') if value.strip()]
        if not target_items:
            print("❌ Error: --items provided but no valid IDs were parsed")
            sys.exit(1)
    elif args.item:
        target_items = [args.item]
    else:
        print("❌ Error: Use one of --all, --item, or --items with --batch-generate")
        sys.exit(1)

    from generation.field_router import FieldRouter
    from shared.api.client_factory import create_api_client

    provider = args.api_provider or 'grok'
    api_client = create_api_client(provider)

    def _load_text_component_bundle(domain: str) -> list[str]:
        """Load configured multi-field text component bundle for a domain."""
        config_file = Path(f'generation/backfill/config/{domain}.yaml')
        if not config_file.exists():
            return []

        with open(config_file, 'r', encoding='utf-8') as handle:
            config = yaml.safe_load(handle) or {}

        generators = config.get('generators')
        if not isinstance(generators, list):
            return []

        for generator in generators:
            if not isinstance(generator, dict):
                continue
            if generator.get('type') != 'multi_field_text':
                continue
            fields = generator.get('fields')
            if not isinstance(fields, list):
                return []

            component_types: list[str] = []
            for mapping in fields:
                if not isinstance(mapping, dict):
                    continue
                component_type = mapping.get('component_type')
                if isinstance(component_type, str) and component_type.strip():
                    component_types.append(component_type.strip())

            ordered_unique: list[str] = []
            for component_type in component_types:
                if component_type not in ordered_unique:
                    ordered_unique.append(component_type)
            return ordered_unique

        return []

    normalized_field = FieldRouter.normalize_field_name(args.domain, args.field)
    field_type = FieldRouter.get_field_type(args.domain, normalized_field)

    # Integrated text generation: use configured multi-field text bundle so
    # FAQ and section-title components generate in the same execution flow.
    text_fields_to_generate = [normalized_field]
    if field_type == 'text':
        configured_bundle = _load_text_component_bundle(args.domain)
        if configured_bundle and normalized_field in configured_bundle:
            text_fields_to_generate = configured_bundle
        elif normalized_field != 'faq':
            try:
                faq_field_type = FieldRouter.get_field_type(args.domain, 'faq')
                if faq_field_type == 'text':
                    text_fields_to_generate.append('faq')
            except Exception:
                pass

    print("=" * 80)
    print("🚀 BATCH GENERATE")
    print("=" * 80)
    print(f"Domain: {args.domain}")
    print(f"Requested field: {args.field}")
    if field_type == 'text':
        print(f"Text field bundle: {', '.join(text_fields_to_generate)}")
    print(f"Provider: {provider}")
    print(f"Field type: {field_type}")
    print(f"Items: {len(target_items)}")
    print(f"Dry run: {args.dry_run}")
    print(f"Force regenerate: {args.force_regenerate}")

    success_count = 0
    skipped_count = 0
    failed_count = 0

    coordinator = _create_domain_coordinator(args.domain, api_client) if field_type == 'text' else None

    for index, item_id in enumerate(target_items, start=1):
        print(f"\n[{index}/{len(target_items)}] {item_id}")
        try:
            if field_type == 'text':
                item_failed = False
                for text_field in text_fields_to_generate:
                    try:
                        result = coordinator.generate_content(
                            item_id=item_id,
                            component_type=text_field,
                            force_regenerate=args.force_regenerate
                        )
                    except Exception as exc:
                        item_failed = True
                        print(f"   ❌ Failed {text_field}: {exc}")
                        continue

                    if result.get('success'):
                        print(f"   ✅ Generated {text_field}")
                    else:
                        item_failed = True
                        print(f"   ❌ Failed {text_field}: {result.get('error', 'unknown error')}")

                if item_failed:
                    failed_count += 1
                else:
                    success_count += 1
            else:
                result = FieldRouter.generate_field(
                    domain=args.domain,
                    field=normalized_field,
                    item_name=item_id,
                    api_client=api_client,
                    dry_run=args.dry_run,
                    force_regenerate=args.force_regenerate
                )
                if result.get('success'):
                    if result.get('skipped'):
                        skipped_count += 1
                        print("   ⏭️  Skipped (existing value)")
                    else:
                        success_count += 1
                        print("   ✅ Generated")
                else:
                    failed_count += 1
                    print(f"   ❌ Failed: {result.get('error', 'unknown error')}")
        except Exception as exc:
            failed_count += 1
            print(f"   ❌ Failed: {exc}")

    print("\n" + "=" * 80)
    print("📊 BATCH GENERATE SUMMARY")
    print("=" * 80)
    print(f"✅ Generated: {success_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📦 Total: {len(target_items)}")


def main():
    """Main CLI entry point"""
    _enable_terminal_streaming()

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

    # Batch generate any field in any domain
    python3 run.py --batch-generate --domain materials --field pageDescription --all
    python3 run.py --batch-generate --domain materials --field context --items "aluminum-laser-cleaning,steel-laser-cleaning" --force-regenerate

    # Seed a new page from one keyword, then generate and export
    python3 run.py --seed-from-keyword "Aerospace Coatings" --domain applications
    python3 run.py --seed-from-keyword "Nickel Slag" --domain contaminants --category inorganic-coating --subcategory residue

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
    parser.add_argument('--batch-generate', action='store_true',
                        help='Batch generate one field across items for any domain')
    parser.add_argument('--seed-from-keyword', type=str, metavar='KEYWORD',
                        help='Create a new domain item from keyword, then optionally generate text and export')
    
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
                        choices=['materials', 'contaminants', 'settings', 'compounds', 'applications'],
                        help='Domain to postprocess')
    parser.add_argument('--field', type=str,
                        help='Field type to postprocess (e.g., pageDescription, micro, faq)')
    parser.add_argument('--item', type=str,
                        help='Specific item name to postprocess')
    parser.add_argument('--items', type=str,
                        help='Comma-separated item IDs for batch generation')
    parser.add_argument('--all', action='store_true',
                        help='Postprocess all items in domain')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='Checkpoint interval for batch operations (default: 10)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Compare versions without saving (preview mode)')
    parser.add_argument('--force-regenerate', action='store_true',
                        help='Regenerate even if field already populated (structured fields require this)')
    parser.add_argument('--api-provider', type=str,
                        choices=['grok', 'deepseek', 'openai'],
                        help='API provider override for compatible commands (default: grok)')
    parser.add_argument('--template-item', type=str,
                        help='Template item ID to clone when seeding from keyword')
    parser.add_argument('--category', type=str,
                        help='Category override for seed-from-keyword (required for non-applications if template lacks category)')
    parser.add_argument('--subcategory', type=str,
                        help='Subcategory override for seed-from-keyword (required for non-applications if template lacks subcategory)')
    parser.add_argument('--skip-generate', action='store_true',
                        help='With --seed-from-keyword, only create source record and skip text generation')
    
    # Simplified interface (NEW - Jan 13, 2026)
    parser.add_argument('--generate', type=str, metavar='MATERIAL',
                        help='Generate content for material (auto-resolves name)')
    parser.add_argument('--test', type=str, metavar='MATERIAL',
                        help='Test material content for voice/length compliance')
    parser.add_argument('--list-materials', action='store_true',
                        help='List all available materials')
    parser.add_argument('--analyze-voice', action='store_true',
                        help='Analyze voice distinctiveness (use with --test)')
    parser.add_argument('--analyze-length', action='store_true',
                        help='Analyze length variation (use with --test)')
    parser.add_argument('--analyze-all', action='store_true',
                        help='Analyze all quality metrics (use with --test)')
    parser.add_argument('--all-fields', action='store_true',
                        help='Generate all component types (use with --generate)')
    parser.add_argument('--integrity-check', action='store_true',
                        help='Run system integrity checks')
    parser.add_argument('--quick', action='store_true',
                        help='Quick mode (with --integrity-check, skips slow checks)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output for tests and checks')
    
    args = parser.parse_args()
    
    # Handle simplified commands first (NEW - Jan 13, 2026)
    if args.list_materials:
        list_materials_command(args)
        return
    elif args.seed_from_keyword:
        seed_from_keyword_command(args)
        return
    elif args.generate:
        generate_command(args)
        return
    elif args.test:
        test_command(args)
        return
    elif args.integrity_check:
        integrity_check_command(args)
        return
    
    # Execute command (backfill is default if --domain/--item provided without other flags)
    if args.postprocess:
        postprocess_command(args)
    elif args.batch_generate:
        batch_generate_command(args)
    elif args.export:
        export_command(args)
    elif args.export_all:
        export_all_command(args)
    elif args.backfill or args.backfill_all:
        if args.backfill_all:
            print("❌ --backfill-all not yet implemented")
            print("   Use --backfill --domain <domain> instead")
            sys.exit(1)
        backfill_command(args)
    elif args.domain or args.item:
        # Default to backfill when domain/item specified without explicit command
        backfill_command(args)
    else:
        parser.print_help()
        print("\n❌ Error: No command specified")
        print("   Use --domain and --item to generate content (backfill)")
        print("   Use --postprocess to refine existing content")
        print("   Use --export to export frontmatter for a domain")
        print("   Use --export-all to export all domains")
        sys.exit(1)


def list_materials_command(args):
    """List all available materials with smart formatting"""
    print("📋 AVAILABLE MATERIALS:")
    print("="*60)
    
    try:
        materials = material_resolver.list_materials()
        
        # Group by category
        by_category = {}
        for material in materials:
            category = material['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(material)
        
        for category, mats in sorted(by_category.items()):
            print(f"\n🔧 {category.upper()}:")
            for mat in mats:
                subcategory = f" / {mat['subcategory']}" if mat['subcategory'] else ""
                print(f"  - {mat['name']:<20} ({mat['key']}{subcategory})")
        
        print(f"\n✅ Total: {len(materials)} materials available")
        print("\n💡 Usage:")
        print("  python3 run.py --generate 'Aluminum' --field pageDescription")
        print("  python3 run.py --test 'Steel' --analyze-all")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def generate_command(args):
    """Generate content for material with smart resolution"""
    print("🚀 SIMPLIFIED GENERATION:")
    print("="*60)
    
    # Resolve material name
    material_key, error = material_resolver.resolve_material(args.generate)
    if error:
        print(f"❌ {error}")
        sys.exit(1)
    
    print(f"📝 Resolved '{args.generate}' → '{material_key}'")
    
    # Determine what to generate
    if args.all_fields:
        generator_type = "multi_field_text"
        field_type = None
        print(f"🔄 Generating ALL fields for {material_key}")
    else:
        # Default to pageDescription if no field specified
        generator_type = "multi_field_text"  # Use unified generator
        field_type = getattr(args, 'field', 'pageDescription')
        print(f"🔄 Generating {field_type} for {material_key}")
    
    try:
        # Build backfill command
        cmd = [
            'python3', 'run.py', 
            '--backfill', 
            '--domain', 'materials',
            '--generator', generator_type,
            '--item', material_key
        ]
        
        if hasattr(args, 'dry_run') and args.dry_run:
            cmd.append('--dry-run')
        
        print(f"⚡ Running: {' '.join(cmd)}")
        print("-" * 60)
        
        # Execute backfill
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Generation completed successfully!")
            
            # Suggest follow-up commands
            print("\n💡 Next steps:")
            print(f"  python3 run.py --test '{args.generate}' --analyze-all")
            print(f"  python3 run.py --export --domain materials")
        else:
            print(f"\n❌ Generation failed (exit code: {result.returncode})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def test_command(args):
    """Test material content for quality compliance"""
    print("🧪 QUALITY TESTING:")
    print("="*60)
    
    # Resolve material name
    material_key, error = material_resolver.resolve_material(args.test)
    if error:
        print(f"❌ {error}")
        sys.exit(1)
    
    print(f"🔍 Testing '{args.test}' → '{material_key}'")
    
    # Determine what to analyze
    analyze_voice = args.analyze_voice or args.analyze_all
    analyze_length = args.analyze_length or args.analyze_all
    analyze_ai = args.analyze_all
    
    if not (analyze_voice or analyze_length or analyze_ai):
        # Default to all if none specified
        analyze_voice = analyze_length = analyze_ai = True
    
    try:
        # Load material data to get content and author
        with open('data/materials/Materials.yaml', 'r') as f:
            materials_data = yaml.safe_load(f)
        
        material_data = materials_data.get('materials', {}).get(material_key)
        if not material_data:
            print(f"❌ Material data not found: {material_key}")
            sys.exit(1)
        
        # Get author country
        author_data = material_data.get('author', {})
        author_country = author_data.get('country', 'Unknown')
        
        # Test pageDescription content
        content = material_data.get('pageDescription', '')
        if not content:
            print(f"⚠️  No pageDescription content found for {material_key}")
            print("   Generate content first:")
            print(f"   python3 run.py --generate '{args.test}' --field pageDescription")
            return
        
        print(f"👤 Author: {author_country}")
        print(f"📝 Content: {len(content)} characters, {len(content.split())} words")
        print("-" * 60)
        
        # Analyze content
        result = quality_analyzer.analyze_content(
            content=content,
            author_country=author_country,
            target_words=50,  # Default target
            variation_percent=50,  # 50% variation
            ai_threshold=0.70
        )
        
        # Display results
        if analyze_voice:
            voice = result.voice_analysis
            status = "✅ PASS" if voice.voice_authentic else "❌ FAIL"
            print(f"🗣️  VOICE ANALYSIS: {status}")
            print(f"   Country: {voice.author_country}")
            print(f"   Pattern Score: {voice.pattern_score:.1%}")
            print(f"   Patterns Detected: {len(voice.patterns_detected)}")
            
            if voice.patterns_detected:
                print(f"   Examples: {voice.patterns_detected[:2]}")
            
            if voice.missing_patterns:
                print(f"   Missing: {len(voice.missing_patterns)} pattern types")
            print()
        
        if analyze_length:
            length = result.length_analysis
            status = "✅ PASS" if length.length_compliant else "❌ FAIL"
            print(f"📏 LENGTH ANALYSIS: {status}")
            print(f"   Word Count: {length.word_count}")
            print(f"   Target Range: {length.target_range[0]}-{length.target_range[1]} words")
            print(f"   Variation: {length.variation_factor:.1%}")
            print()
        
        if analyze_ai:
            ai = result.ai_analysis
            status = "✅ PASS" if ai.passes_detection else "❌ FAIL"
            print(f"🤖 AI DETECTION: {status}")
            print(f"   AI Score: {ai.ai_score:.1%}")
            print(f"   Threshold: {ai.human_threshold:.1%} human")
            
            if ai.ai_phrases_detected:
                print(f"   AI Phrases: {len(ai.ai_phrases_detected)}")
                for phrase in ai.ai_phrases_detected[:2]:
                    print(f"     - '{phrase}'")
            print()
        
        # Overall summary
        status = "✅ ALL PASS" if result.passes_all_checks else "⚠️  NEEDS WORK"
        print(f"📊 OVERALL QUALITY: {status} ({result.overall_quality:.1%})")
        
        if result.recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in result.recommendations:
                print(f"   • {rec}")
        
        if result.passes_all_checks:
            print("\n🎉 Content meets all quality standards!")
        else:
            print(f"\n🔄 Regenerate to improve:")
            print(f"   python3 run.py --generate '{args.test}' --field pageDescription")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def integrity_check_command(args):
    """Run system integrity checks."""
    from generation.integrity import IntegrityChecker

    print("\n🔍 Running System Integrity Checks...")
    checker = IntegrityChecker()

    if args.quick:
        results = checker.run_quick_checks()
    else:
        results = checker.run_all_checks()

    checker.print_report(results, verbose=args.verbose)

    if checker.has_failures(results):
        print("\n❌ System integrity check FAILED. Fix issues before generating content.")
        sys.exit(1)
    elif checker.has_warnings(results):
        print("\n⚠️  System integrity check passed with warnings.")
    else:
        print("\n✅ System integrity check PASSED. All systems healthy.")


if __name__ == '__main__':
    main()
