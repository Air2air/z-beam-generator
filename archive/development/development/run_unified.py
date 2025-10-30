#!/usr/bin/env python3
"""
Z-Beam Generator - Unified Command Line Interface

Consolidates all scattered functionality into a single, robust pipeline.
Uses the UnifiedPipeline class for all operations with comprehensive error handling.

═══════════════════════════════════════════════════════════════════════════════
📋 QUICK START GUIDE  
═══════════════════════════════════════════════════════════════════════════════

🎯 GENERATE CONTENT:
  python3 run.py --material "Aluminum"              # Generate specific material
  python3 run.py --batch "Steel,Aluminum"           # Generate multiple materials  
  python3 run.py --all                              # Generate all materials
  python3 run.py --components "frontmatter,caption" # Specify components

🔍 MATERIAL AUDITING:
  python3 run.py --audit "Steel"                    # Audit single material
  python3 run.py --audit-batch "Steel,Aluminum"     # Audit multiple materials
  python3 run.py --audit-all                        # Audit all materials
  python3 run.py --audit "Steel" --auto-fix         # Audit with automatic fixes
  python3 run.py --audit "Steel" --quick            # Quick audit (skip frontmatter)

🔬 DATA RESEARCH:
  python3 run.py --research                         # Research all missing properties
  python3 run.py --research --materials "Steel"     # Research for specific materials
  python3 run.py --research --properties "density"  # Research specific properties
  python3 run.py --data-completion                  # Data completeness report
  python3 run.py --data-gaps                        # Show research priorities

⚙️ SYSTEM OPERATIONS:
  python3 run.py --validate                         # Validate system integrity
  python3 run.py --test                            # Run system tests
  python3 run.py --info                            # System information
  python3 run.py --deploy                          # Deploy to production

═══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import unified pipeline
from pipeline.unified_pipeline import (
    UnifiedPipeline,
    PipelineRequest,
    PipelineMode,
    PipelineResult
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments with unified interface"""
    parser = argparse.ArgumentParser(
        description="Z-Beam Generator - Unified Pipeline Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Generation operations
    generation_group = parser.add_argument_group('Content Generation')
    generation_group.add_argument("--material", help="Generate content for specific material")
    generation_group.add_argument("--batch", help="Generate content for multiple materials (comma-separated)")
    generation_group.add_argument("--all", action="store_true", help="Generate content for all materials")
    generation_group.add_argument("--components", help="Components to generate (comma-separated, default: frontmatter)")
    
    # Audit operations
    audit_group = parser.add_argument_group('Material Auditing')
    audit_group.add_argument("--audit", help="Audit specific material for compliance")
    audit_group.add_argument("--audit-batch", help="Audit multiple materials (comma-separated)")
    audit_group.add_argument("--audit-all", action="store_true", help="Audit all materials")
    
    # Research operations
    research_group = parser.add_argument_group('Data Research')
    research_group.add_argument("--research", action="store_true", help="Research missing properties")
    research_group.add_argument("--materials", help="Specific materials for research (comma-separated)")
    research_group.add_argument("--properties", help="Specific properties for research (comma-separated)")
    research_group.add_argument("--data-completion", action="store_true", help="Generate data completeness report")
    research_group.add_argument("--data-gaps", action="store_true", help="Show data gaps and research priorities")
    
    # System operations
    system_group = parser.add_argument_group('System Operations')
    system_group.add_argument("--validate", action="store_true", help="Validate system integrity")
    system_group.add_argument("--test", action="store_true", help="Run system tests")
    system_group.add_argument("--info", action="store_true", help="Show system information")
    system_group.add_argument("--deploy", action="store_true", help="Deploy to production")
    
    # Execution options
    options_group = parser.add_argument_group('Execution Options')
    options_group.add_argument("--auto-fix", action="store_true", help="Apply automatic fixes during operations")
    options_group.add_argument("--quick", action="store_true", help="Quick mode (skip intensive validations)")
    options_group.add_argument("--report", action="store_true", help="Generate detailed reports")
    options_group.add_argument("--batch-size", type=int, default=10, help="Batch size for parallel operations")
    options_group.add_argument("--confidence", type=int, default=70, help="Confidence threshold for research")
    options_group.add_argument("--verbose", action="store_true", help="Verbose output")
    options_group.add_argument("--dry-run", action="store_true", help="Dry run mode (no changes)")
    
    return parser.parse_args()


def determine_pipeline_mode_and_materials(args: argparse.Namespace) -> tuple[PipelineMode, Optional[List[str]]]:
    """Determine pipeline mode and materials from arguments"""
    
    # Generation modes
    if args.material:
        return PipelineMode.MATERIAL_GENERATION, [args.material]
    elif args.batch:
        return PipelineMode.BATCH_GENERATION, args.batch.split(',')
    elif args.all:
        return PipelineMode.FULL_GENERATION, None
    
    # Audit modes
    elif args.audit:
        return PipelineMode.AUDIT_SINGLE, [args.audit]
    elif args.audit_batch:
        return PipelineMode.AUDIT_BATCH, args.audit_batch.split(',')
    elif args.audit_all:
        return PipelineMode.AUDIT_ALL, None
    
    # Research modes
    elif args.research:
        return PipelineMode.RESEARCH_PROPERTIES, None
    elif args.data_completion:
        return PipelineMode.DATA_COMPLETION, None
    elif args.data_gaps:
        return PipelineMode.DATA_COMPLETION, None  # Same handler, different display
    
    # System modes
    elif args.validate:
        return PipelineMode.VALIDATION, None
    elif args.test:
        return PipelineMode.TESTING, None
    elif args.info:
        return PipelineMode.SYSTEM_INFO, None
    elif args.deploy:
        return PipelineMode.DEPLOYMENT, None
    
    else:
        # Default to system info if no specific operation
        return PipelineMode.SYSTEM_INFO, None


def create_pipeline_request(args: argparse.Namespace) -> PipelineRequest:
    """Create unified pipeline request from command line arguments"""
    
    mode, materials = determine_pipeline_mode_and_materials(args)
    
    # Override materials if explicitly specified in research operations
    if args.materials and mode == PipelineMode.RESEARCH_PROPERTIES:
        materials = args.materials.split(',')
    
    return PipelineRequest(
        mode=mode,
        materials=materials,
        components=args.components.split(',') if args.components else None,
        properties=args.properties.split(',') if args.properties else None,
        auto_fix=args.auto_fix,
        quick_mode=args.quick,
        generate_report=args.report,
        batch_size=args.batch_size,
        confidence_threshold=args.confidence,
        verbose=args.verbose,
        dry_run=args.dry_run
    )


def format_pipeline_result(result: PipelineResult) -> None:
    """Format and display pipeline result"""
    
    if result.success:
        print(f"✅ {result.mode.value.title()} operation completed successfully")
        print(f"   Duration: {result.duration_seconds:.2f} seconds")
        print(f"   Materials processed: {len(result.materials_processed)}")
        print(f"   Operations completed: {result.operations_completed}")
        
        if result.operations_failed > 0:
            print(f"   ⚠️ Operations failed: {result.operations_failed}")
        
        # Mode-specific result formatting
        if result.mode in [PipelineMode.AUDIT_SINGLE, PipelineMode.AUDIT_BATCH, PipelineMode.AUDIT_ALL]:
            format_audit_results(result)
        elif result.mode == PipelineMode.RESEARCH_PROPERTIES:
            format_research_results(result)
        elif result.mode in [PipelineMode.DATA_COMPLETION]:
            format_data_completion_results(result)
        elif result.mode == PipelineMode.SYSTEM_INFO:
            format_system_info_results(result)
            
    else:
        print(f"❌ {result.mode.value.title()} operation failed")
        print(f"   Duration: {result.duration_seconds:.2f} seconds")
        print(f"   Operations failed: {result.operations_failed}")
        
        if result.errors:
            print(f"\n🚨 Errors ({len(result.errors)}):")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(result.errors) > 5:
                print(f"   ... and {len(result.errors) - 5} more errors")
    
    if result.warnings:
        print(f"\n⚠️ Warnings ({len(result.warnings)}):")
        for warning in result.warnings[:3]:  # Show first 3 warnings
            print(f"   • {warning}")
        if len(result.warnings) > 3:
            print(f"   ... and {len(result.warnings) - 3} more warnings")


def format_audit_results(result: PipelineResult) -> None:
    """Format audit-specific results"""
    if result.audit_results:
        print(f"\n📊 Audit Results:")
        for material_name, audit_result in result.audit_results.items():
            if audit_result:
                print(f"   {material_name}: {audit_result.overall_score}/100")
                if audit_result.critical_issues:
                    print(f"     🔥 {len(audit_result.critical_issues)} critical issues")
                if audit_result.high_issues:
                    print(f"     ⚠️ {len(audit_result.high_issues)} high priority issues")
    
    if result.fixes_applied:
        print(f"\n🔧 Fixes Applied:")
        for material_name, fixes in result.fixes_applied.items():
            if fixes:
                print(f"   {material_name}: {len(fixes)} fixes applied")


def format_research_results(result: PipelineResult) -> None:
    """Format research-specific results"""
    if result.properties_researched:
        print(f"\n🔬 Research Results:")
        total_researched = result.results.get('properties_researched', 0)
        total_failed = result.results.get('research_failures', 0)
        print(f"   Properties researched: {total_researched}")
        if total_failed > 0:
            print(f"   Research failures: {total_failed}")


def format_data_completion_results(result: PipelineResult) -> None:
    """Format data completion results"""
    if result.data_gaps_found:
        print(f"\n📊 Data Completion Analysis:")
        gaps = result.data_gaps_found
        if 'completion_percentage' in gaps:
            print(f"   Completion: {gaps['completion_percentage']:.1f}%")
        if 'missing_properties' in gaps:
            print(f"   Missing properties: {gaps['missing_properties']}")
        if 'priority_gaps' in gaps:
            print(f"   Priority gaps: {len(gaps['priority_gaps'])}")


def format_system_info_results(result: PipelineResult) -> None:
    """Format system information results"""
    info = result.results
    print(f"\n🎯 System Information:")
    print(f"   Total materials: {info.get('total_materials', 'Unknown')}")
    print(f"   Categories: {info.get('categories', 'Unknown')}")
    print(f"   Services initialized: {'✅' if info.get('services_initialized') else '❌'}")
    print(f"   System valid: {'✅' if info.get('system_valid') else '❌'}")


def main() -> int:
    """Main entry point for unified Z-Beam Generator"""
    
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Configure verbose logging if requested
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        print("🚀 Z-Beam Generator - Unified Pipeline")
        print("=" * 50)
        
        # Create pipeline request
        request = create_pipeline_request(args)
        
        print(f"📋 Operation: {request.mode.value}")
        if request.materials:
            print(f"📦 Materials: {', '.join(request.materials)}")
        if request.components:
            print(f"🔧 Components: {', '.join(request.components)}")
        if request.properties:
            print(f"🔬 Properties: {', '.join(request.properties)}")
        
        print("\n" + "=" * 50)
        
        # Initialize and execute pipeline
        pipeline = UnifiedPipeline()
        result = pipeline.execute(request)
        
        # Format and display results
        print("\n" + "=" * 50)
        format_pipeline_result(result)
        
        # Return appropriate exit code
        return 0 if result.success else 1
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 130
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())