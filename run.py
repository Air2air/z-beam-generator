#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified Command Line Interface

Streamlined entry point for the Z-Beam Generator system.
For advanced operations, use run_unified.py with the unified pipeline.

═══════════════════════════════════════════════════════════════════════════════
📋 QUICK START GUIDE
═══════════════════════════════════════════════════════════════════════════════

🎯 GENERATE CONTENT:
  python3 run.py --material "Aluminum"     # Specific material (frontmatter-only)
  python3 run.py --all                     # All materials (frontmatter-only)
  python3 run.py --caption "Aluminum"      # Generate AI caption (saves to Materials.yaml)
  python3 run.py --subtitle "Aluminum"     # Generate AI subtitle (saves to Materials.yaml)
  python3 run.py --faq "Aluminum"          # Generate AI FAQ (saves to Materials.yaml)

🚀 DEPLOYMENT:
  python3 run.py --deploy                  # Deploy to Next.js production site

🧪 TESTING & VALIDATION:
  python3 run.py --test                    # Full test suite
  python3 run.py --test-api                # Test API connections
  python3 run.py --validate                # Validate existing data without regeneration
  python3 run.py --validate-report report.md  # Generate validation report
  python3 run.py --content-validation-report report.md  # Content quality validation (FAQ, Caption, Subtitle)
  python3 run.py --check-env               # Health check
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
  python3 run.py --enforce-completeness      # Strict mode - block if incomplete

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
  • API_PROVIDERS - API provider settings (DeepSeek, Winston, Grok)
  • COMPONENT_CONFIG - Component enable/disable and priorities
  • AI_DETECTION_CONFIG - AI detection behavior
  • OPTIMIZER_CONFIG - Optimizer and text generation settings

═══════════════════════════════════════════════════════════════════════════════
"""

# Import all configuration from centralized location
from shared.config.settings import (
    GLOBAL_OPERATIONAL_CONFIG,
    API_PROVIDERS,
    COMPONENT_CONFIG,
)

# Standard library imports
import os
import sys
import argparse

# Import command handlers from modular structure
from shared.commands import (
    handle_caption_generation,
    handle_subtitle_generation,
    handle_faq_generation,
    deploy_to_production,
    handle_material_audit,
    handle_data_completeness_report,
    handle_data_gaps,
    handle_research_missing_properties,
    generate_content_validation_report,
)


def main():
    """Main application entry point with basic command line interface."""
    
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Z-Beam Content Generator")
    
    # Content Generation Commands (Multi-Type Support)
    parser.add_argument("--content-type", help="Content type: material, region, application, thesaurus")
    parser.add_argument("--identifier", help="Content identifier (name/ID for any type)")
    
    # Legacy Material-Specific Commands (Backward Compatibility)
    parser.add_argument("--material", help="Generate frontmatter for specific material (legacy)")
    parser.add_argument("--all", action="store_true", help="Generate frontmatter for all materials")
    parser.add_argument("--caption", help="Generate AI-powered caption")
    parser.add_argument("--subtitle", help="Generate AI-powered subtitle")
    parser.add_argument("--faq", help="Generate AI-powered FAQ")
    
    # Deployment Commands
    parser.add_argument("--deploy", action="store_true", help="Deploy to Next.js production site")
    
    # Validation Commands
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--validate", action="store_true", help="Run hierarchical validation")
    parser.add_argument("--validate-report", help="Generate validation report")
    parser.add_argument("--content-validation-report", help="Content quality validation report")
    
    # Data Research & Completeness Commands
    parser.add_argument("--data", nargs='?', const='--all', help="Systematically verify data")
    parser.add_argument("--data-completeness-report", action="store_true", help="Data completeness report")
    parser.add_argument("--data-gaps", action="store_true", help="Analyze data gaps")
    parser.add_argument("--research-missing-properties", action="store_true", help="Run AI research")
    parser.add_argument("--research-properties", help="Research specific properties (comma-separated)")
    parser.add_argument("--research-materials", help="Research specific materials (comma-separated)")
    parser.add_argument("--research-batch-size", type=int, default=10, help="Batch size (default: 10)")
    parser.add_argument("--research-confidence-threshold", type=int, default=70, help="Min confidence (default: 70)")
    parser.add_argument("--enforce-completeness", action="store_true", help="Strict mode")
    
    # Material Auditing Commands
    parser.add_argument("--audit", help="Audit specific material")
    parser.add_argument("--audit-batch", help="Audit multiple materials (comma-separated)")
    parser.add_argument("--audit-all", action="store_true", help="Audit all materials")
    parser.add_argument("--audit-auto-fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument("--audit-report", action="store_true", help="Generate audit reports")
    parser.add_argument("--audit-quick", action="store_true", help="Quick audit")
    
    # Other Commands
    parser.add_argument("--data-only", action="store_true", help="Export frontmatter")
    parser.add_argument("--sanitize", action="store_true", help="Sanitize frontmatter files")
    parser.add_argument("--sanitize-file", help="Sanitize specific file")
    
    args = parser.parse_args()
    
    # Command dispatcher - simple commands first
    if args.deploy:
        return deploy_to_production()
    
    if args.caption:
        return handle_caption_generation(args.caption)
    
    if args.subtitle:
        return handle_subtitle_generation(args.subtitle)
    
    if args.faq:
        return handle_faq_generation(args.faq)
    
    if args.audit or args.audit_batch or args.audit_all:
        return handle_material_audit(args)
    
    if args.data_completeness_report:
        return handle_data_completeness_report()
    
    if args.data_gaps:
        return handle_data_gaps()
    
    if args.research_missing_properties:
        return handle_research_missing_properties(
            batch_size=args.research_batch_size,
            confidence_threshold=args.research_confidence_threshold,
            specific_properties=args.research_properties.split(',') if args.research_properties else None,
            specific_materials=args.research_materials.split(',') if args.research_materials else None
        )
    
    if args.content_validation_report:
        return generate_content_validation_report(args.content_validation_report)
    
    # NEW: Multi-type orchestrator generation (Phase 1 architecture)
    if args.content_type and args.identifier:
        from components.frontmatter.core.orchestrator import FrontmatterOrchestrator
        from shared.api.client_factory import create_api_client
        
        print(f"🚀 Generating {args.content_type} frontmatter: {args.identifier}")
        
        try:
            # Initialize API client (optional for data-only mode)
            api_client = create_api_client("grok") if not args.data_only else None
            
            # Create orchestrator
            orchestrator = FrontmatterOrchestrator(
                api_client=api_client,
                enforce_completeness=args.enforce_completeness
            )
            
            # Check if content type is supported
            if not orchestrator.is_type_supported(args.content_type):
                supported = ', '.join(orchestrator.get_supported_types())
                print(f"❌ Content type '{args.content_type}' not supported")
                print(f"   Supported types: {supported}")
                return False
            
            # TODO: Get author data from config or args
            author_data = {
                'name': 'Todd Dunning',
                'country': 'United States'
            }
            
            # Generate content with author voice
            result = orchestrator.generate(
                content_type=args.content_type,
                identifier=args.identifier,
                author_data=author_data
            )
            
            if result.success:
                output_path = result.content  # Output path stored in content field
                print(f"✅ Generated → {output_path}")
                print(f"   🎯 Author voice applied: {author_data['country']}")
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
    from shared.generators.dynamic_generator import DynamicGenerator
    from shared.api.client_factory import create_api_client
    from materials.data.materials import load_materials_cached as load_materials, clear_materials_cache
    from shared.utils.filename import generate_safe_filename
    
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
        
        try:
            # Try new orchestrator first (Phase 1 architecture)
            try:
                from components.frontmatter.core.orchestrator import FrontmatterOrchestrator
                
                api_client = create_api_client("grok") if not args.data_only else None
                
                orchestrator = FrontmatterOrchestrator(
                    api_client=api_client,
                    enforce_completeness=args.enforce_completeness
                )
                
                # Author data (TODO: Make configurable)
                author_data = {
                    'name': 'Todd Dunning',
                    'country': 'United States'
                }
                
                result = orchestrator.generate(
                    content_type='material',
                    identifier=args.material,
                    author_data=author_data
                )
                
                if result.success:
                    output_path = result.content  # Output path stored in content field
                    print(f"✅ Generated → {output_path}")
                    print(f"   🎯 Author voice applied: {author_data['country']}")
                    return True
                else:
                    print(f"❌ Generation failed: {result.error_message}")
                    return False
                    
            except ImportError:
                # Fallback to legacy generator if orchestrator not available
                print("⚠️  Using legacy generator (orchestrator not available)")
                
                materials_data_dict = load_materials()
                from materials.data.materials import get_material_by_name
                material_info = get_material_by_name(args.material, materials_data_dict)
                
                if not material_info:
                    print(f"❌ Material '{args.material}' not found")
                    return False
                
                api_client = create_api_client("grok") if not args.data_only else None
                generator = DynamicGenerator()
                
                result = generator.generate_component(
                    material=args.material,
                    component_type='frontmatter',
                    api_client=api_client,
                    frontmatter_data=None,
                    material_data=material_info
                )
            
                # Legacy generator result handling
                if result.success:
                    output_dir = "frontmatter/materials"
                    os.makedirs(output_dir, exist_ok=True)
                    filename = generate_safe_filename(args.material)
                    output_file = f"{output_dir}/{filename}-laser-cleaning.yaml"
                    
                    # Debug: Check content type
                    print(f"DEBUG: result.content type = {type(result.content)}")
                    print(f"DEBUG: result.content first 100 chars = {repr(result.content[:100])}")
                    
                    with open(output_file, 'w') as f:
                        f.write(result.content)
                    
                    print(f"✅ Generated → {output_file}")
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
                from components.frontmatter.core.trivial_exporter import export_all_frontmatter
                import time
                
                start_time = time.time()
                results = export_all_frontmatter()
                elapsed = time.time() - start_time
                
                success_count = sum(1 for v in results.values() if v)
                print(f"\n✅ Export complete: {success_count}/{len(results)} materials ({elapsed:.1f}s)")
                return success_count > 0
                
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
            
            generator = DynamicGenerator()
            success_count = 0
            failure_count = 0
            
            for material_name, material_info in all_materials:
                print(f"\n📋 Processing {material_name}...")
                
                try:
                    result = generator.generate_component(
                        material=material_name,
                        component_type='frontmatter',
                        api_client=api_client,
                        frontmatter_data=None,
                        material_data=material_info
                    )
                    
                    if result.success:
                        output_dir = "frontmatter"
                        os.makedirs(output_dir, exist_ok=True)
                        filename = generate_safe_filename(material_name)
                        output_file = f"{output_dir}/{filename}-laser-cleaning.yaml"
                        
                        with open(output_file, 'w') as f:
                            f.write(result.content)
                        
                        print(f"  ✅ → {output_file}")
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
