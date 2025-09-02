#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface

A streamlined main interface for AI-powered laser cleaning content generation.
Core functionality extracted to modules for better maintainability and testing.

🚀 QUICK START SCRIPTS (User Commands):
========================================

BASIC GENERATION:
    python3 run.py                                    # Generate all materials (batch mode)
    python3 run.py --material "Steel"                 # Generate specific material
    python3 run.py --material "Aluminum" --author 2   # Generate with Italian author
    python3 run.py --interactive                      # Interactive mode with prompts
    python3 run.py --start-index 50                   # Start batch from material #50

COMPONENT CONTROL:
    python3 run.py --material "Copper" --components "frontmatter,content"  # Specific components only
    python3 run.py --list-components                  # Show all available components
    python3 run.py --show-config                     # Show component configuration

CONTENT MANAGEMENT:
    python3 run.py --clean                           # Remove all generated content files
    python3 run.py --yaml                            # Validate and fix YAML errors
    python3 run.py --cleanup-scan                    # Scan for cleanup opportunities
    python3 run.py --cleanup-report                  # Generate cleanup report
    python3 run.py --cleanup-root                    # Organize root directory files

SYSTEM INFO:
    python3 run.py --list-materials                  # List all 121 available materials  
    python3 run.py --list-authors                    # List all authors with countries
    python3 run.py --check-env                       # Check API keys and environment
    python3 run.py --test-api                        # Test API connectivity
    python3 run.py --test                            # Run comprehensive test suite

🔧 COMPONENT DATA SOURCE CONFIGURATION:
======================================

Component data sources are configured in: cli/component_config.py

DATA PROVIDER OPTIONS:
    "API"          - Generate content via AI API (deepseek, grok)
    "static"       - Use pre-generated static content files  
    "hybrid"       - Static files with AI enhancement via API

API PROVIDER OPTIONS:
    "deepseek"     - DeepSeek AI (recommended, cost-effective)
    "grok"         - Grok AI (X/Twitter's AI)
    "none"         - No API (static components only)

Example component configuration:
    "frontmatter": {
        "enabled": true,
        "data_provider": "API",
        "api_provider": "deepseek"
    }

📊 SYSTEM ARCHITECTURE:
======================

CORE MODULES:
    - api/client_manager.py      - API client management
    - generators/workflow_manager.py - Generation workflows
    - utils/author_manager.py    - Author information management
    - utils/file_operations.py   - File I/O operations
    - utils/environment_checker.py - Environment validation
    - cleanup/cleanup_operations.py - Content cleanup tools

This modular architecture improves:
    ✅ Testability (each module can be tested independently)
    ✅ Maintainability (smaller, focused files)
    ✅ Reusability (modules can be imported elsewhere)
    ✅ Coverage (easier to achieve comprehensive test coverage)
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# Import extracted modules
from api.client_manager import test_api_connectivity
from generators.dynamic_generator import DynamicGenerator
from generators.workflow_manager import (
    run_material_generation,
    run_batch_generation,
    run_interactive_generation
)
from utils.author_manager import list_authors, validate_author_id
from utils.environment_checker import check_environment, format_environment_report
from utils.file_operations import clean_content_components
from cli.component_config import COMPONENT_CONFIG

# Import existing functionality that remains
try:
    from cleanup.cleanup_manager import cleanup_scan, cleanup_report, cleanup_root
except ImportError:
    # Fallback to original run.py functions if cleanup_manager doesn't exist
    cleanup_scan = None
    cleanup_report = None 
    cleanup_root = None

# For now, import these from original run.py - will extract later
try:
    from run import run_comprehensive_tests, run_yaml_validation
except ImportError:
    run_comprehensive_tests = None
    run_yaml_validation = None


def show_component_configuration():
    """Display current component configuration."""
    print("⚙️  Z-BEAM COMPONENT CONFIGURATION")
    print("=" * 50)
    
    try:
        components_config = COMPONENT_CONFIG.get("components", {})
        orchestration_order = COMPONENT_CONFIG.get("orchestration_order", [])
        
        if not components_config:
            print("❌ No component configuration found")
            return
        
        # Show orchestration order
        print(f"\n🔄 Generation Order:")
        for i, component in enumerate(orchestration_order, 1):
            enabled = components_config.get(component, {}).get('enabled', False)
            status = "✅" if enabled else "❌"
            print(f"  {i:2d}. {status} {component}")
        
        # Show detailed configuration
        print(f"\n🔧 Component Details:")
        print(f"{'Component':<15} {'Enabled':<8} {'Data Provider':<12} {'API Provider':<12}")
        print("-" * 50)
        
        for component, config in components_config.items():
            enabled = "✅ Yes" if config.get('enabled', False) else "❌ No"
            data_provider = config.get('data_provider', 'unknown')
            api_provider = config.get('api_provider', 'none')
            
            print(f"{component:<15} {enabled:<8} {data_provider:<12} {api_provider:<12}")
        
        # Summary
        enabled_count = sum(1 for config in components_config.values() if config.get('enabled', False))
        total_count = len(components_config)
        
        print(f"\n📊 Summary:")
        print(f"  Total components: {total_count}")
        print(f"  Enabled: {enabled_count}")
        print(f"  Disabled: {total_count - enabled_count}")
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")


def run_dynamic_generation(
    material: Optional[str] = None,
    components: Optional[List[str]] = None,
    interactive: bool = False,
    test_api: bool = False,
    author_id: Optional[int] = None,
    start_index: int = 0
) -> bool:
    """
    Main generation coordination function.
    
    Args:
        material: Specific material to generate
        components: List of components to generate
        interactive: Run in interactive mode
        test_api: Test API connectivity only
        author_id: Author ID for content generation
        start_index: Starting index for batch generation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Test API connectivity if requested
        if test_api:
            print("🔌 Testing API connectivity...")
            results = test_api_connectivity()
            
            for provider, result in results.items():
                if result['success']:
                    print(f"  ✅ {provider}: {result['response_time']:.2f}s ({result['token_count']} tokens)")
                else:
                    print(f"  ❌ {provider}: {result['error']}")
            
            return all(result['success'] for result in results.values())
        
        # Validate author if specified
        if author_id and not validate_author_id(author_id):
            print(f"❌ Invalid author ID: {author_id}")
            return False
        
        # Initialize generator
        generator = DynamicGenerator()
        
        # Get available components
        if components is None:
            # Use enabled components from configuration
            components_config = COMPONENT_CONFIG.get("components", {})
            components = [
                comp for comp, config in components_config.items() 
                if config.get('enabled', False)
            ]
        
        if not components:
            print("❌ No components specified or enabled")
            return False
        
        # Route to appropriate generation mode
        if interactive:
            # Interactive mode
            from utils.author_manager import get_author_info_for_generation
            author_info = get_author_info_for_generation(author_id)
            run_interactive_generation(generator, author_info)
            return True
            
        elif material:
            # Single material generation
            result = run_material_generation(material, components, author_id)
            return len(result['components_generated']) > 0
            
        else:
            # Batch generation mode
            materials = generator.get_available_materials()
            result = run_batch_generation(
                materials=materials,
                component_types=components,
                author_id=author_id,
                start_index=start_index
            )
            return len(result['materials_processed']) > 0
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False


def create_arg_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Z-Beam AI Content Generator - Streamlined Interface",
        epilog="Examples:\n"
        "  python3 run.py --material 'Steel'\n"
        "  python3 run.py --interactive\n"
        "  python3 run.py --list-materials\n"
        "  python3 run.py --check-env\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Content generation options
    parser.add_argument(
        "--material", "-m", help="Generate content for specific material"
    )
    parser.add_argument(
        "--components",
        help="Comma-separated list of components to generate (default: all enabled)",
    )
    parser.add_argument(
        "--author", type=int, help="Author ID for content generation (see --list-authors)"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Starting index for batch generation (default: 0)",
    )

    # System operations
    parser.add_argument(
        "--test", action="store_true", help="Run comprehensive test suite"
    )
    parser.add_argument(
        "--test-api", action="store_true", help="Test API connectivity"
    )
    parser.add_argument(
        "--check-env", action="store_true", help="Check environment and configuration"
    )
    parser.add_argument(
        "--yaml", action="store_true", help="Validate and fix YAML files"
    )

    # Content management
    parser.add_argument(
        "--clean", action="store_true", help="Remove all generated content files"
    )
    parser.add_argument(
        "--cleanup-scan", action="store_true", help="Scan for cleanup opportunities"
    )
    parser.add_argument(
        "--cleanup-report", action="store_true", help="Generate cleanup report"
    )
    parser.add_argument(
        "--cleanup-root", action="store_true", help="Organize root directory files"
    )

    # Information display
    parser.add_argument(
        "--list-materials", action="store_true", help="List all available materials"
    )
    parser.add_argument(
        "--list-components", action="store_true", help="List all available components"
    )
    parser.add_argument(
        "--list-authors", action="store_true", help="List all available authors"
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show component configuration and API provider settings",
    )

    # Validation operations
    parser.add_argument("--validate", help="Validate YAML files in specified directory")

    # General options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser


def main():
    """Main entry point for Z-Beam dynamic generation system."""
    parser = create_arg_parser()
    args = parser.parse_args()

    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Route to appropriate operation
        if args.yaml:
            # YAML validation mode
            success = run_yaml_validation()

        elif args.test:
            # Comprehensive test suite mode
            success = run_comprehensive_tests()

        elif args.clean:
            # Content cleanup mode
            result = clean_content_components()
            print(f"🧹 Cleanup completed: {result['message']}")
            if result['errors']:
                print("⚠️  Errors occurred:")
                for error in result['errors']:
                    print(f"  - {error}")
            success = len(result['errors']) == 0

        elif args.cleanup_scan:
            # Cleanup scan mode (dry-run)
            success = cleanup_scan()

        elif args.cleanup_report:
            # Cleanup report generation
            success = cleanup_report()

        elif args.cleanup_root:
            # Root directory cleanup
            success = cleanup_root()

        elif args.check_env:
            # Environment check
            env_results = check_environment()
            report = format_environment_report(env_results)
            print(report)
            success = env_results['overall_status'] != 'critical'

        elif args.list_materials or args.list_components or args.list_authors or args.show_config:
            # List operations and configuration display
            if args.show_config:
                show_component_configuration()
            
            if args.list_authors:
                print(list_authors())
            
            if args.list_materials or args.list_components:
                try:
                    generator = DynamicGenerator()

                    if args.list_materials:
                        materials = generator.get_available_materials()
                        print(f"📋 Available materials ({len(materials)}):")
                        for i, material in enumerate(sorted(materials), 1):
                            print(f"   {i:3d}. {material}")

                    if args.list_components:
                        components = generator.get_available_components()
                        print(f"🔧 Available components ({len(components)}):")
                        for i, component in enumerate(sorted(components), 1):
                            print(f"   {i}. {component}")

                except ImportError as e:
                    print(f"❌ Error importing generator: {e}")
                    success = False
                    
            success = True

        else:
            # Dynamic generation mode (default)
            components_list = None
            if args.components:
                components_list = [c.strip() for c in args.components.split(",")]

            success = run_dynamic_generation(
                material=args.material,
                components=components_list,
                interactive=args.interactive,
                test_api=args.test_api,
                author_id=args.author,
                start_index=args.start_index,
            )

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n🛑 Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error running operation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
