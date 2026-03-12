#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified Command Line Interface

Streamlined entry point for the Z-Beam Generator system.
For advanced operations, use run.py (project root) with the canonical pipeline.

═══════════════════════════════════════════════════════════════════════════════
📋 QUICK START GUIDE
═══════════════════════════════════════════════════════════════════════════════

🚀 UNIFIED WORKFLOW (RECOMMENDED - Single Command Does Everything):
  python3 run.py --run "Aluminum"          # Complete workflow: Generate → Voice → Export
  python3 run.py --run-region "North America"    # Region workflow (coming soon)
  python3 run.py --run-application "Rust Removal"  # Application workflow (coming soon)

🎯 GENERATION & VALIDATION WORKFLOW (NEW - Single-Pass):
  # Step 1: Generate (single API call, no validation)
  python3 run.py --micro "Aluminum"      # Generate AI caption → Materials.yaml (single-pass)
  python3 run.py --material-description "Aluminum"     # Generate AI material description → Materials.yaml (single-pass)
  python3 run.py --faq "Aluminum"          # Generate AI FAQ → Materials.yaml (single-pass)
  
  # Step 2: Validate & Improve (post-processing with learning systems)
  python3 run.py --validate-content Aluminum description  # Run all quality checks + learning (up to 5 attempts)
    python3 run.py --validate-content Aluminum caption   # Grok, Realism, Readability, Subjective + DB logging
  
  # Step 3: Voice enhancement (optional)
  python3 scripts/voice/enhance_materials_voice.py --material "Aluminum"  # Apply voice → Materials.yaml
  
  # Step 4: Export to frontmatter
  python3 run.py --material "Aluminum" --data-only  # Export → frontmatter
  
  # ⚠️  DEVELOPMENT ONLY - Skip integrity check (bypasses fail-fast validation):
  python3 run.py --micro "Aluminum" --skip-integrity-check
  # WARNING: Never use --skip flags in production - violates fail-fast architecture

🔄 BATCH GENERATION (Meet Humanness Minimums Efficiently):
    ⚠️ Legacy tools-runner batch flags are deprecated.
    Use canonical commands from project root instead:
    python3 run.py --batch-generate --domain materials --field pageDescription --items "aluminum-laser-cleaning,steel-laser-cleaning"
    python3 run.py --batch-generate --domain materials --field pageDescription --all
    python3 run.py --batch-generate --domain materials --field micro --all
  
    # Cost savings: 75% reduction vs individual detection calls
    # Minimum length: 300 chars (material descriptions ~180 chars each, need batching)

🚀 DEPLOYMENT:
  python3 run.py --deploy                  # Deploy to Next.js production site

🧪 TESTING & VALIDATION:
  python3 run.py --test                    # Full test suite
  python3 run.py --test-learning           # Per-iteration learning architecture tests
  python3 run.py --test-learning --verbose # Detailed test output
  python3 run.py --batch-test              # Batch caption test (4 materials, one per author, with report)
  python3 run.py --test-api                # Test API connections
  python3 run.py --validate                # Validate existing data without regeneration
  python3 run.py --validate-report report.md  # Generate validation report
  python3 run.py --content-validation-report report.md  # Content quality validation (FAQ, Caption, Material Description)
  python3 run.py --check-env               # Health check
  python3 run.py --integrity-check         # System integrity check (values, propagation, APIs, learning)
  python3 run.py --integrity-check --quick # Fast integrity check (skip slow tests)
  python3 run.py --integrity-check --verbose  # Detailed integrity check output
  python3 run.py --list-materials          # List available materials

🔍 DATA VALIDATION & INTEGRITY:
  python3 run.py --validate              # Run hierarchical validation & auto-fix
  python3 run.py --validate-report FILE  # Generate detailed validation report

🔬 STAGE 0: AI RESEARCH & DATA COMPLETION (⚡ MANDATORY):
  python3 run.py --data-completeness-report  # Check current status (75.8% complete)
  python3 run.py --data-gaps                 # Show research priorities (635 gaps)
  python3 run.py --research-missing-properties  # Fill ALL missing properties
  python3 run.py --research-properties "porosity,electricalResistivity"  # Specific properties
  python3 run.py --research-materials "Copper,Steel"  # Specific materials
  python3 run.py --research-batch-size 20    # Parallel research (default: 10)
  
  ⚡ NOTE: Data completeness checking is now AUTOMATIC during generation
           No flags needed - validation runs inline with every generation

🔧 FIX STRATEGY ANALYSIS:
  python3 run.py --fix-analysis                                    # Overall effectiveness report
  python3 run.py --fix-analysis --fix-analysis-material "Brass"   # Material-specific insights
  python3 run.py --fix-analysis --fix-analysis-failure-type uniform  # By failure type

� MATERIAL AUDITING SYSTEM (⚡ NEW):
  python3 run.py --audit "Steel"                    # Audit single material compliance
  python3 run.py --audit-batch "Steel,Aluminum"    # Batch audit multiple materials  
  python3 run.py --audit-all                       # Audit ALL materials in system
  python3 run.py --audit "Steel" --audit-auto-fix  # Audit with automatic fixes
  python3 run.py --audit "Steel" --audit-report    # Generate detailed audit report
  python3 run.py --audit "Steel" --audit-quick     # Quick audit (skip frontmatter)

�🔬 SYSTEMATIC DATA VERIFICATION (Legacy):
  python3 run.py --data                  # Verify ALL properties (18 hours, $14.64)
  python3 run.py --data=critical         # Verify critical properties (3 hours, $1.20)
  python3 run.py --data=test             # Safe test run (15 min, $0.10, dry-run)
  python3 run.py --data=important        # Verify important properties (3 hours, $1.20)
  python3 run.py --data=--group=mechanical  # Verify property group
  python3 run.py --data=--properties=density,meltingPoint  # Specific properties

⚙️  SYSTEM MANAGEMENT:
  python3 run.py --config                  # Show configuration
  python3 run.py --cache-stats             # Cache performance
  python3 run.py --preload-cache           # Optimize performance
  python3 run.py --clean                   # Clean generated content

🚀 OPTIMIZATION:
  python3 run.py --optimize frontmatter     # Optimize specific component

💡 For complete command reference: python3 run.py --help

═══════════════════════════════════════════════════════════════════════════════
📝 CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

All user-configurable settings are in: config/settings.py

To modify system behavior, edit config/settings.py:
  • GLOBAL_OPERATIONAL_CONFIG - Timeouts, retries, operational parameters
    • API_PROVIDERS - API provider settings (DeepSeek, Grok)
  • COMPONENT_CONFIG - Component enable/disable and priorities
  • AI_DETECTION_CONFIG - AI detection behavior
  • OPTIMIZER_CONFIG - Optimizer and text generation settings

═══════════════════════════════════════════════════════════════════════════════
"""

# Standard library imports
import os
import sys
import argparse
from pathlib import Path

# Ensure direct script execution resolves project-root modules, including run.py.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import all configuration from centralized location
from shared.config.settings import (
    GLOBAL_OPERATIONAL_CONFIG,
    API_PROVIDERS,
    COMPONENT_CONFIG,
)
from export.config.loader import load_domain_config
from export.core.frontmatter_exporter import FrontmatterExporter
from export.utils.url_formatter import format_filename
from shared.utils.material_resolver import material_resolver


EXPORT_DOMAIN_ALIASES = {
    "application": "applications",
    "applications": "applications",
    "compound": "compounds",
    "compounds": "compounds",
    "contaminant": "contaminants",
    "contaminants": "contaminants",
    "material": "materials",
    "materials": "materials",
    "setting": "settings",
    "settings": "settings",
}


def _resolve_export_domain(content_type: str) -> str | None:
    return EXPORT_DOMAIN_ALIASES.get(content_type.strip().lower())


def _resolve_export_item_key(exporter: FrontmatterExporter, identifier: str) -> tuple[str | None, str | None]:
    items = exporter._load_domain_data()[exporter.items_key]
    normalized_identifier = identifier.strip()
    normalized_lower = normalized_identifier.lower()

    if exporter.domain == 'materials':
        resolved_key, error = material_resolver.resolve_material(normalized_identifier)
        if resolved_key:
            return resolved_key, None
        return None, error

    if normalized_identifier in items:
        return normalized_identifier, None

    for item_key, item_data in items.items():
        candidates = [
            item_key,
            str(item_data.get(exporter.id_field, '')),
            str(item_data.get('slug', '')),
            str(item_data.get('name', '')),
            str(item_data.get('displayName', '')),
        ]
        if any(candidate.lower() == normalized_lower for candidate in candidates if candidate):
            return item_key, None

    return None, (
        f"Item '{identifier}' not found in export domain '{exporter.domain}'. "
        f"Expected a source key, id, slug, name, or displayName present in {exporter.config['source_file']}"
    )


def _export_single_item(domain: str, identifier: str) -> tuple[bool, str]:
    config = load_domain_config(domain)
    exporter = FrontmatterExporter(config)
    item_key, error = _resolve_export_item_key(exporter, identifier)
    if item_key is None:
        return False, error or f"Item '{identifier}' could not be resolved"

    item_data = exporter._load_domain_data()[exporter.items_key][item_key]
    success = exporter.export_single(item_key, item_data, force=True)
    if not success:
        return False, f"Export skipped or failed for '{item_key}'"

    filename = format_filename(
        item_id=item_key,
        suffix=exporter.filename_suffix,
        slugify_id=exporter.slugify_filenames,
    )
    output_path = exporter.output_path / filename
    return True, str(output_path)


def _export_all_items(domain: str) -> tuple[bool, str]:
    config = load_domain_config(domain)
    exporter = FrontmatterExporter(config)
    results = exporter.export_all(force=True)
    success_count = sum(1 for exported in results.values() if exported)
    total_count = len(results)
    return success_count > 0, f"{success_count}/{total_count} items exported"


def _create_frontmatter_orchestrator(no_completeness_check: bool):
    from export.core.orchestrator import FrontmatterOrchestrator
    from shared.api.client_factory import create_api_client

    return FrontmatterOrchestrator(
        api_client=create_api_client("grok"),
        enforce_completeness=not no_completeness_check,
    )


def _resolve_material_author_data(material_identifier: str, material_data: dict | None = None) -> dict | None:
    from domains.materials.materials_cache import get_material_by_name_cached
    from shared.utils.author_manager import get_author_info_for_material

    candidate_material = material_data or get_material_by_name_cached(material_identifier)
    if not candidate_material:
        return None

    try:
        return get_author_info_for_material(candidate_material)
    except (ValueError, KeyError) as error:
        print(f"⚠️  Author assignment failed: {error}")
        return None


def _enable_terminal_streaming() -> None:
    """Configure stdout/stderr for live line-by-line terminal updates."""
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass

# Import command handlers from modular structure
from shared.commands import (
    handle_micro_generation,
    handle_description_generation,
    handle_settings_description_generation,
    handle_component_summaries_generation,
    handle_faq_generation,
    deploy_to_production,
    handle_material_audit,
    handle_data_completeness_report,
    handle_data_gaps,
    handle_research_missing_properties,
    handle_fix_analysis,
    generate_content_validation_report,
)

# Import global evaluation system
# Global evaluation removed - per-iteration learning happens in retry loop
# from shared.commands.global_evaluation import run_global_subjective_evaluation

# Import unified workflow commands
from shared.commands.workflow import (
    run_material_workflow,
    run_region_workflow,
    run_application_workflow,
    run_thesaurus_workflow,
)


def main():
    """Main application entry point with basic command line interface."""
    _enable_terminal_streaming()
    
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Z-Beam Content Generator")
    
    # Unified Workflow Commands (RECOMMENDED)
    parser.add_argument("--run", help="Run complete material workflow: generate → voice → export")
    parser.add_argument("--run-region", help="Run complete region workflow")
    parser.add_argument("--run-application", help="Run complete application workflow")
    parser.add_argument("--run-thesaurus", help="Run complete thesaurus workflow")
    
    # Workflow Control Flags
    parser.add_argument("--skip-validation", action="store_true", help="Skip validation/research step")
    parser.add_argument("--skip-research", action="store_true", help="Skip property research (validation still runs)")
    parser.add_argument("--skip-generation", action="store_true", help="Skip text generation step")
    parser.add_argument("--skip-voice", action="store_true", help="Skip voice enhancement step")
    parser.add_argument("--skip-export", action="store_true", help="Skip frontmatter export step")
    
    # Content Generation Commands (Multi-Type Support)
    parser.add_argument("--content-type", help="Content type: material, region, application, thesaurus")
    parser.add_argument("--identifier", help="Content identifier (name/ID for any type)")
    
    # Legacy Material-Specific Commands (Backward Compatibility)
    parser.add_argument("--material", help="Generate frontmatter for specific material (legacy)")
    parser.add_argument("--all", action="store_true", help="Generate frontmatter for all materials")
    parser.add_argument("--micro", help="Generate AI-powered caption")
    parser.add_argument("--material-description", help="Generate AI-powered material description")
    parser.add_argument("--settings-description", help="Generate AI-powered settings description")
    parser.add_argument("--component-summaries", help="Generate AI-powered component summaries for Settings page")
    parser.add_argument("--faq", help="Generate AI-powered FAQ")
    
    # Batch Generation Commands
    parser.add_argument("--batch-material-description", help="[DEPRECATED] Legacy tools-runner batch path; use root run.py --batch-generate")
    parser.add_argument("--batch-caption", help="[DEPRECATED] Legacy tools-runner batch path; use root run.py --batch-generate")
    
    # Deployment Commands
    parser.add_argument("--deploy", action="store_true", help="Deploy to Next.js production site")
    
    # Validation Commands
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--validate", action="store_true", help="Run hierarchical validation")
    parser.add_argument("--validate-content", nargs=2, metavar=('MATERIAL', 'COMPONENT'), 
                       help="Validate and improve generated content with learning systems (e.g., --validate-content Aluminum description)")
    parser.add_argument("--validate-report", help="Generate validation report")
    parser.add_argument("--content-validation-report", help="Content quality validation report")
    parser.add_argument("--validate-ai-detection", action="store_true", help="Audit content with Grok humanness evaluator")
    parser.add_argument("--grok-threshold", "--winston-threshold", dest="grok_threshold", type=float, default=70.0, help="Grok human score threshold (0-100)")
    parser.add_argument("--grok-component", "--winston-component", dest="grok_component", choices=['description', 'micro', 'faq'], 
                       help="Specific component type to audit with Grok")
    
    # Data Research & Completeness Commands
    parser.add_argument("--data", nargs='?', const='--all', help="Systematically verify data")
    parser.add_argument("--data-completeness-report", action="store_true", help="Data completeness report")
    parser.add_argument("--data-gaps", action="store_true", help="Analyze data gaps")
    parser.add_argument("--research-missing-properties", action="store_true", help="Run AI research")
    parser.add_argument("--research-properties", help="Research specific properties (comma-separated)")
    parser.add_argument("--research-materials", help="Research specific materials (comma-separated)")
    parser.add_argument("--research-batch-size", type=int, default=10, help="Batch size (default: 10)")
    parser.add_argument("--research-confidence-threshold", type=int, default=70, help="Min confidence (default: 70)")
    parser.add_argument("--no-completeness-check", action="store_true", help="Disable automatic completeness validation")
    
    # Material Auditing Commands
    parser.add_argument("--audit", help="Audit specific material")
    parser.add_argument("--audit-batch", help="Audit multiple materials (comma-separated)")
    parser.add_argument("--audit-all", action="store_true", help="Audit all materials")
    parser.add_argument("--audit-auto-fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument("--audit-report", action="store_true", help="Generate audit reports")
    parser.add_argument("--audit-quick", action="store_true", help="Quick audit")
    
    # Fix Strategy Analysis Commands
    parser.add_argument("--fix-analysis", action="store_true", help="Generate fix strategy effectiveness report")
    parser.add_argument("--fix-analysis-material", help="Filter fix analysis by material")
    parser.add_argument("--fix-analysis-failure-type", help="Filter fix analysis by failure type (uniform, borderline, partial, poor)")
    
    # Testing Commands
    parser.add_argument("--batch-test", action="store_true", help="Run batch caption test (4 materials, one per author)")
    
    # Other Commands
    parser.add_argument("--data-only", action="store_true", help="Manual export: combine Materials.yaml + Categories.yaml → frontmatter")
    parser.add_argument("--sanitize", action="store_true", help="Sanitize frontmatter files")
    parser.add_argument("--sanitize-file", help="Sanitize specific file")
    parser.add_argument("--integrity-check", action="store_true", help="Run system integrity checks")
    parser.add_argument("--skip-integrity-check", action="store_true", help="[DEV ONLY] Skip integrity checks - bypasses fail-fast validation")
    parser.add_argument("--quick", action="store_true", help="Quick mode (with --integrity-check, skips slow checks)")
    parser.add_argument("--test-learning", action="store_true", help="Run per-iteration learning architecture tests")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output for tests and checks")
    
    args = parser.parse_args()

    if args.skip_integrity_check and os.getenv("ALLOW_INTEGRITY_BYPASS") != "1":
        print("❌ Integrity bypass denied")
        print("   --skip-integrity-check requires ALLOW_INTEGRITY_BYPASS=1")
        print("   Example: ALLOW_INTEGRITY_BYPASS=1 python3 run.py --micro \"Aluminum\" --skip-integrity-check")
        return False

    generation_requested = any([
        args.run,
        args.run_region,
        args.run_application,
        args.run_thesaurus,
        args.material,
        args.all,
        args.micro,
        args.material_description,
        args.settings_description,
        args.component_summaries,
        args.faq,
        args.batch_material_description,
        args.batch_caption,
    ])
    if generation_requested:
        print("📺 Streaming progress updates to terminal (live)")
    
    # ========================================================================
    # UNIFIED WORKFLOW COMMANDS (Priority - handle first)
    # ========================================================================
    
    if args.run:
        result = run_material_workflow(
            args.run,
            skip_validation=args.skip_validation,
            skip_research=args.skip_research,
            skip_generation=args.skip_generation,
            skip_voice=args.skip_voice,
            skip_export=args.skip_export
        )
        return 0 if result['overall_success'] else 1
    
    if args.run_region:
        result = run_region_workflow(args.run_region)
        return 0 if result['overall_success'] else 1
    
    if args.run_application:
        result = run_application_workflow(args.run_application)
        return 0 if result['overall_success'] else 1
    
    if args.run_thesaurus:
        result = run_thesaurus_workflow(args.run_thesaurus)
        return 0 if result['overall_success'] else 1
    
    # ========================================================================
    # LEGACY COMMANDS (Backward compatibility)
    # ========================================================================
    
    # System Integrity Check (runs before generation if enabled)
    if args.integrity_check:
        from generation.integrity import IntegrityChecker
        
        print("\n🔍 Running System Integrity Checks...")
        checker = IntegrityChecker()
        
        if args.quick:
            results = checker.run_quick_checks()
        else:
            results = checker.run_all_checks()
        
        checker.print_report(results, verbose=args.verbose if hasattr(args, 'verbose') else True)
        
        if checker.has_failures(results):
            print("\n❌ System integrity check FAILED. Fix issues before generating content.")
            return 1
        elif checker.has_warnings(results):
            print("\n⚠️  System integrity check passed with warnings.")
            return 0
        else:
            print("\n✅ System integrity check PASSED. All systems healthy.")
            return 0
    
    # Learning Architecture Tests
    if args.test_learning:
        from shared.commands.integrity_helper import run_learning_architecture_tests
        
        print("\n🧪 Running Per-Iteration Learning Architecture Tests...")
        print("=" * 70)
        
        success = run_learning_architecture_tests(verbose=args.verbose if hasattr(args, 'verbose') else False)
        
        if success:
            print("\n✅ All learning architecture tests PASSED")
            print("   System is correctly configured for per-iteration learning")
            return 0
        else:
            print("\n❌ Some learning architecture tests FAILED")
            print("   Run with --verbose for details")
            return 1
    
    # Command dispatcher - simple commands first
    if args.deploy:
        return deploy_to_production()
    
    # Grok humanness audit command
    if args.validate_ai_detection:
        try:
            import subprocess
            import os
            cmd = [
                'python3',
                'scripts/validation/grok_audit.py',
                f'--threshold={args.grok_threshold}'
            ]
            if args.material:
                cmd.extend(['--material', args.material])
            if args.grok_component:
                cmd.extend(['--component', args.grok_component])
            
            result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
            return result.returncode
        except Exception as e:
            print(f"❌ Grok audit failed: {e}")
            return 1
    
    # Batch test command
    if args.batch_test:
        import os
        import subprocess
        
        print("🎯 Running Batch Caption Test...")
        print("=" * 70)
        print("📺 Streaming output to terminal (logs not saved)")
        print("=" * 70)
        
        try:
            # Stream directly to terminal without saving to file
            result = subprocess.run(
                ['python3', 'scripts/batch_micro_test.py'],
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            return result.returncode
        except Exception as e:
            print(f"❌ Batch test failed: {e}")
            return 1
    
    if args.batch_material_description:
        print("="*80)
        print("⚠️  DEPRECATED: --batch-material-description (legacy tools runner)")
        print("="*80)
        print("Use canonical batch pipeline instead:")
        print(f"  python3 run.py --batch-generate --domain materials --field pageDescription --items \"{args.batch_material_description}\"")
        print("or for all items:")
        print("  python3 run.py --batch-generate --domain materials --field pageDescription --all")
        print("\nNo action taken from scripts/tools/run.py for this deprecated command.")
        return 1

    if args.batch_caption:
        print("="*80)
        print("⚠️  DEPRECATED: --batch-caption (legacy tools runner)")
        print("="*80)
        print("Use canonical batch pipeline instead:")
        print(f"  python3 run.py --batch-generate --domain materials --field micro --items \"{args.batch_caption}\"")
        print("or for all items:")
        print("  python3 run.py --batch-generate --domain materials --field micro --all")
        print("\nNo action taken from scripts/tools/run.py for this deprecated command.")
        return 1
    
    if args.validate_content:
        print("="*80)
        print(f"⚠️  ARCHIVED FEATURE: --validate-content")
        print("="*80)
        print()
        print("This feature has been archived (Nov 20, 2025).")
        print()
        print("REASON:")
        print("  • 19-step validation pipeline duplicated main generation flow")
        print("  • All validation already built into generation commands")
        print("  • Feature was never used in production")
        print()
        print("USE INSTEAD:")
        print("  • python3 run.py --micro \"Material\"")
        print("  • python3 run.py --material-description \"Material\"")
        print("  • python3 run.py --faq \"Material\"")
        print()
        print("These commands include:")
        print("  ✓ Grok humanness detection")
        print("  ✓ Realism evaluation")
        print("  ✓ All 5 quality gates")
        print("  ✓ Sweet spot learning")
        print("  ✓ Database logging")
        print()
        return False
    
    if args.micro:
        result = handle_micro_generation(args.micro, skip_integrity_check=args.skip_integrity_check)
        # Per-iteration learning happens inline - no global evaluation needed
        return result
    
    if getattr(args, 'description', None):
        result = handle_description_generation(args.description, skip_integrity_check=args.skip_integrity_check)
        # Per-iteration learning happens inline - no global evaluation needed
        return result
    
    if getattr(args, 'settings_description', None):
        result = handle_settings_description_generation(args.settings_description, skip_integrity_check=args.skip_integrity_check)
        # Per-iteration learning happens inline - no global evaluation needed
        return result
    
    if getattr(args, 'component_summaries', None):
        result = handle_component_summaries_generation(args.component_summaries, skip_integrity_check=args.skip_integrity_check)
        # Per-iteration learning happens inline - no global evaluation needed
        return result
    
    if args.faq:
        result = handle_faq_generation(args.faq, skip_integrity_check=args.skip_integrity_check)
        # Per-iteration learning happens inline - no global evaluation needed
        return result
    
    if args.audit or args.audit_batch or args.audit_all:
        return handle_material_audit(args)
    
    if args.data_completeness_report:
        return handle_data_completeness_report()
    
    if args.data_gaps:
        return handle_data_gaps()
    
    if args.fix_analysis:
        return handle_fix_analysis(
            material=args.fix_analysis_material,
            failure_type=args.fix_analysis_failure_type
        )
    
    if args.research_missing_properties:
        return handle_research_missing_properties(
            batch_size=args.research_batch_size,
            confidence_threshold=args.research_confidence_threshold,
            specific_properties=args.research_properties.split(',') if args.research_properties else None,
            specific_materials=args.research_materials.split(',') if args.research_materials else None,
            auto_mode=True  # Skip confirmation prompt
        )
    
    if args.content_validation_report:
        return generate_content_validation_report(args.content_validation_report)
    
    # NEW: Multi-type orchestrator generation (Phase 1 architecture)
    if args.content_type and args.identifier:
        print(f"🚀 Generating {args.content_type} frontmatter: {args.identifier}")

        export_domain = _resolve_export_domain(args.content_type)
        if args.data_only and export_domain is not None:
            success, message = _export_single_item(export_domain, args.identifier)
            if success:
                print(f"✅ Exported → {message}")
                return True
            print(f"❌ Export failed: {message}")
            return False
        
        try:
            orchestrator = _create_frontmatter_orchestrator(args.no_completeness_check)
            
            # Check if content type is supported
            if not orchestrator.is_type_supported(args.content_type):
                supported = ', '.join(orchestrator.get_supported_types())
                print(f"❌ Content type '{args.content_type}' not supported")
                print(f"   Supported types: {supported}")
                return False
            
            # Get author data based on content type
            # Reusable approach: Check content data first, then enrich from registry
            author_data = None
            if args.content_type == 'material':
                author_data = _resolve_material_author_data(args.identifier)
            # For other content types (region, application, thesaurus):
            # Each can implement similar logic by checking their data files for author info
            # then enriching with get_author_by_id() from registry
            
            # Generate content with author voice (if author_data available)
            result = orchestrator.generate(
                content_type=args.content_type,
                identifier=args.identifier,
                author_data=author_data
            )
            
            if result.success:
                output_path = result.content  # Output path stored in content field
                print(f"✅ Generated → {output_path}")
                if author_data:
                    print(f"   🎯 Author voice applied: {author_data.get('country', 'Unknown')}")
                return True
            else:
                print(f"❌ Generation failed: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Generation error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Service initialization is skipped for simple material generation
    # Pre-generation validation runs automatically within components
    
    # Additional imports for material generation
    from shared.api.client_factory import create_api_client
    from domains.materials.materials_cache import load_materials_cached as load_materials, clear_materials_cache
    
    try:
        from shared.commands.common import (
            validate_material_pre_generation, 
            validate_and_improve_frontmatter, 
            validate_batch_generation
        )
    except ImportError:
        def validate_material_pre_generation(material_name):
            return {'validation_passed': True, 'issues_detected': []}
        def validate_and_improve_frontmatter(material_name, frontmatter):
            return {'improvements_made': False, 'improved_frontmatter': frontmatter, 'validation_result': {'validation_passed': True, 'issues_detected': []}}
        def validate_batch_generation(material_names):
            return {'valid': True, 'total_materials': len(material_names)}
    
    clear_materials_cache()
    
    # Handle remaining commands
    if args.data is not None:
        from shared.commands.research import run_data_verification
        return run_data_verification(args.data)
    
    if args.validate or args.validate_report:
        from shared.commands.validation_data import run_data_validation
        return run_data_validation(args.validate_report)
    
    if args.sanitize or args.sanitize_file:
        from shared.commands.sanitization import run_frontmatter_sanitization
        return run_frontmatter_sanitization(args.sanitize_file)
    
    if args.test:
        print("🧪 Test mode")
        from shared.generators.component_generators import ComponentGeneratorFactory
        api_client = create_api_client("grok")
        generator = ComponentGeneratorFactory.create_generator("frontmatter", api_client=api_client)
        print(f"✅ Frontmatter generator loaded: {generator.component_type}")
        return True
    
    # Single material generation
    if args.material:
        print(f"🚀 Generating frontmatter for {args.material}")

        if args.data_only:
            success, message = _export_single_item('materials', args.material)
            if success:
                print(f"✅ Exported → {message}")
                return True
            print(f"❌ Export failed: {message}")
            return False
        
        try:
            orchestrator = _create_frontmatter_orchestrator(args.no_completeness_check)
            author_data = _resolve_material_author_data(args.material)
            
            result = orchestrator.generate(
                content_type='material',
                identifier=args.material,
                author_data=author_data
            )
            
            if result.success:
                output_path = result.content  # Output path stored in content field
                print(f"✅ Generated → {output_path}")
                if author_data:
                    print(f"   🎯 Author voice applied: {author_data.get('country', 'Unknown')}")
                return True
            else:
                print(f"❌ Generation failed: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Batch material generation
    elif args.all:
        print("🚀 Generating frontmatter for all materials")
        
        if args.data_only:
            try:
                success, message = _export_all_items('materials')
                print(f"\n✅ Export complete: {message}")
                return success
                
            except Exception as e:
                print(f"❌ Export failed: {e}")
                return False
        
        # Full generation with API
        try:
            materials_data_dict = load_materials()
            all_materials = [(k, v) for k, v in materials_data_dict.get('materials', {}).items() if k and isinstance(v, dict)]
            
            if not all_materials:
                print("❌ No materials found")
                return False
            
            print(f"📋 Found {len(all_materials)} materials")
            
            from shared.api.client_cache import get_cached_api_client
            api_client = get_cached_api_client('grok')
            
            if not api_client:
                print("❌ Failed to initialize API client")
                return False
            
            # Use orchestrator with completeness control
            orchestrator = _create_frontmatter_orchestrator(args.no_completeness_check)
            
            success_count = 0
            failure_count = 0
            
            for material_name, material_info in all_materials:
                print(f"\n📋 Processing {material_name}...")
                
                try:
                    author_data = _resolve_material_author_data(material_name, material_info)
                    
                    result = orchestrator.generate(
                        content_type='material',
                        identifier=material_name,
                        author_data=author_data
                    )
                    
                    if result.success:
                        # Generator already saved the file - result.content contains the path
                        print(f"  ✅ → {result.content}")
                        success_count += 1
                    else:
                        print(f"  ❌ Failed: {result.error_message}")
                        failure_count += 1
                
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    failure_count += 1
            
            print(f"\n🏁 Completed: {success_count} successes, {failure_count} failures")
            return True
            
        except Exception as e:
            print(f"❌ Batch generation failed: {e}")
            return False
    
    else:
        parser.print_help()
        return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
