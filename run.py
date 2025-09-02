#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface (Cleaned)

A comprehensive AI-powered content generation system for laser cleaning materials.
This version imports functionality from extracted modules for better maintainability.

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
    python3 run.py --show-config                      # Show component configuration

CONTENT MANAGEMENT:
    python3 run.py --clean                           # Remove all generated content files
    python3 run.py --yaml                            # Validate and fix YAML errors

SYSTEM INFO:
    python3 run.py --list-materials                  # List all available materials  
    python3 run.py --list-authors                    # List all authors with countries
    python3 run.py --check-env                       # Check API keys and environment
    python3 run.py --test-api                        # Test API connectivity
    python3 run.py --test                            # Run comprehensive test suite

MATERIAL MANAGEMENT (separate script):
    python3 remove_material.py --list-materials      # List all materials by category
    python3 remove_material.py --find-orphans        # Find orphaned files
    python3 remove_material.py --material "Material Name" --dry-run    # Test removal
    python3 remove_material.py --material "Material Name" --execute    # Remove material

PATH CLEANUP (one-time scripts):
    python3 cleanup_paths.py                         # Rename files to clean format (already done)

🔧 COMPONENT DATA SOURCE CONFIGURATION:
======================================

Component data sources are configured in: cli/component_config.py

DATA PROVIDER OPTIONS:
    "API"          - Generate content via AI API (deepseek, grok)
    "frontmatter"  - Extract data from frontmatter component  
    "hybrid"       - Uses frontmatter data + API generation
    "none"         - Static component, no external data

API PROVIDER OPTIONS:
    "deepseek"     - DeepSeek API
    "grok"         - Grok (X.AI) API
    "none"         - No API needed

CURRENT CONFIGURATION:
    frontmatter:     API generation (grok)
    content:         hybrid (frontmatter + grok)
    bullets:         API generation (deepseek)
    caption:         API generation (deepseek)
    table:           API generation (grok)
    tags:            API generation (deepseek)
    jsonld:          Extract from frontmatter
    metatags:        Extract from frontmatter
    propertiestable: Extract from frontmatter
    badgesymbol:     Extract from frontmatter
    author:          Static component

TO MODIFY DATA SOURCES:
1. Edit cli/component_config.py
2. Change "data_provider" and/or "api_provider" for any component
3. Run: python3 run.py --show-config (to verify changes)

🎯 COMMON WORKFLOWS:
==================
1. Generate all content:           python3 run.py
2. Generate specific material:     python3 run.py --material "Steel"
3. Clean and regenerate:          python3 run.py --clean && python3 run.py
4. Check system health:           python3 run.py --check-env --show-config
5. Remove unwanted material:      python3 remove_material.py --material "Old Material" --execute

🔧 SYSTEM FEATURES:
==================
- Schema-driven content generation with JSON validation
- Multi-component orchestration (frontmatter, content, tags, etc.)
- Interactive and batch processing modes
- Multi-API provider support (DeepSeek, Grok)
- Component validation and autonomous fixing
- Progress tracking and resumption capabilities
- Clean slug generation for consistent file paths
- Modular architecture with extracted utility modules
- Fail-fast configuration validation
- Comprehensive test suite integration
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from typing import List, Optional

# Import modular components
from api.client_manager import create_api_client, get_api_client_for_component, test_api_connectivity
from utils.author_manager import load_authors, get_author_by_id, list_authors
from utils.environment_checker import check_environment
from utils.file_operations import clean_content_components
from cli.api_config import API_PROVIDERS
from cli.component_config import COMPONENT_CONFIG, show_component_configuration

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_dynamic_generation(
    material: str = None,
    components: list = None,
    interactive: bool = False,
    test_api: bool = False,
    author_id: int = None,
    start_index: int = 1,
) -> bool:
    """
    Run dynamic schema-driven content generation using modular components.
    """
    try:
        from generators.dynamic_generator import DynamicGenerator
    except ImportError as e:
        print(f"❌ Error importing generator: {e}")
        return False

    print("🚀 DYNAMIC SCHEMA-DRIVEN GENERATION")
    print("=" * 50)

    # Initialize generator
    try:
        generator = DynamicGenerator()
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        return False

    # Validate and set author if provided
    author_info = None
    if author_id is not None:
        author_info = get_author_by_id(author_id)
        if author_info:
            print(f"👤 Using Author: {author_info['name']} ({author_info['country']})")
        else:
            print(f"❌ Author with ID {author_id} not found!")
            list_authors()
            return False

    # Test API connection if requested
    if test_api:
        print("🔗 Testing API connections...")
        test_results = test_api_connectivity()
        for provider, result in test_results.items():
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {API_PROVIDERS[provider]['name']}: {result.get('error', 'OK')}")
        return all(result['success'] for result in test_results.values())

    # Interactive mode
    if interactive:
        return run_interactive_mode(generator, author_info)

    # Batch mode - generate all materials if no specific material requested
    if material is None:
        return run_batch_mode(generator, author_info, components, start_index)

    # Generate for specific material
    return run_single_material(generator, material, components, author_info)


def run_interactive_mode(generator, author_info: dict = None) -> bool:
    """Run interactive generation with user prompts."""
    print("🎮 Interactive Generation Mode")
    print("Commands: Y/Yes (continue), S/Skip (skip material), Q/Quit (exit)")
    print("=" * 50)

    materials = generator.get_available_materials()
    available_components = generator.get_available_components()

    print(f"📊 Loaded {len(materials)} materials and {len(available_components)} components")
    print(f"🔧 Components: {', '.join(available_components)}")

    generated_count = 0
    skipped_count = 0

    try:
        for i, material in enumerate(materials, 1):
            print(f"\n📦 [{i}/{len(materials)}] Processing: {material}")
            response = input(f"Generate content for {material}? (Y/s/q): ").strip().lower()

            if response in ["q", "quit"]:
                break
            elif response in ["s", "skip"]:
                print(f"⏭️  Skipped {material}")
                skipped_count += 1
                continue

            # Generate content
            success = run_single_material(generator, material, None, author_info)
            if success:
                generated_count += 1

    except KeyboardInterrupt:
        print("\n\n🛑 Generation interrupted by user")

    print(f"\n📊 Generation Summary:")
    print(f"   ✅ Generated: {generated_count} materials")
    print(f"   ⏭️  Skipped: {skipped_count} materials")

    return True


def run_batch_mode(generator, author_info: dict = None, components: list = None, start_index: int = 1) -> bool:
    """Run batch generation for all available materials."""
    print("🏭 Batch Generation Mode")
    print("=" * 50)

    materials = generator.get_available_materials()
    available_components = generator.get_available_components()
    target_components = components if components else available_components

    total_materials = len(materials)
    start_idx = max(1, min(start_index, total_materials)) - 1

    print(f"📊 Target: {len(materials)} materials × {len(target_components)} components")
    print(f"🔧 Components: {', '.join(target_components)}")
    if start_index > 1:
        print(f"🚀 Starting at material #{start_index}: {materials[start_idx]}")
    if author_info:
        print(f"👤 Author: {author_info['name']} ({author_info['country']})")

    generated_count = 0
    failed_count = 0

    try:
        for i, material in enumerate(materials[start_idx:], start_index):
            print(f"\n📦 [{i}/{total_materials}] Processing: {material}")

            success = run_single_material(generator, material, target_components, author_info)
            if success:
                generated_count += 1
                print(f"   ✅ {material} completed successfully")
            else:
                failed_count += 1
                print(f"   ❌ {material} failed to generate")

            progress_percent = (i / total_materials) * 100
            print(f"   📈 Progress: {i}/{total_materials} ({progress_percent:.1f}%)")

    except KeyboardInterrupt:
        print("\n\n🛑 Batch generation interrupted by user")

    print(f"\n📊 Batch Generation Summary:")
    print(f"   ✅ Successfully generated: {generated_count} materials")
    print(f"   ❌ Failed: {failed_count} materials")
    print(f"   📈 Success rate: {(generated_count/total_materials)*100:.1f}%")

    return generated_count > 0


def run_single_material(generator, material: str, components: list = None, author_info: dict = None) -> bool:
    """Generate content for a specific material."""
    try:
        if components is None:
            components = generator.get_available_components()

        # Get enabled components from configuration
        components_config = COMPONENT_CONFIG.get("components", {})
        enabled_components = []
        
        for component in components:
            if component in components_config:
                if components_config[component]["enabled"]:
                    enabled_components.append(component)
            else:
                enabled_components.append(component)  # Default to enabled

        if not enabled_components:
            print(f"❌ No components enabled for generation!")
            return False

        print(f"🔧 Generating {len(enabled_components)} components: {', '.join(enabled_components)}")

        successful_count = 0
        
        for component_type in enabled_components:
            try:
                # Create temporary generator with appropriate API client
                temp_generator = generator.__class__()
                api_client = get_api_client_for_component(component_type)
                temp_generator.set_api_client(api_client)
                
                if author_info:
                    temp_generator.set_author(author_info)

                # Generate component
                result = temp_generator.generate_component(material, component_type)

                if result.success:
                    # Save the component
                    from utils.file_operations import save_component_to_file_original
                    save_component_to_file_original(material, component_type, result.content)
                    successful_count += 1
                    print(f"   ✅ {component_type} - {len(result.content)} chars generated")
                else:
                    print(f"   ❌ {component_type}: {result.error_message}")

            except Exception as e:
                print(f"   ❌ {component_type}: {str(e)}")

        print(f"📋 Results: {successful_count}/{len(enabled_components)} components successful")
        return successful_count > 0

    except Exception as e:
        print(f"❌ Error generating {material}: {e}")
        return False


def run_yaml_validation() -> bool:
    """Run comprehensive YAML validation and fixing."""
    print("🔍 YAML VALIDATION & FIXING MODE")
    print("=" * 50)

    try:
        from validators.centralized_validator import CentralizedValidator
        
        validator = CentralizedValidator()
        content_dir = Path("content")
        
        total_files = 0
        fixed_files = 0
        
        if content_dir.exists():
            for md_file in content_dir.rglob("*.md"):
                total_files += 1
                component_type = md_file.parent.name if md_file.parent.name != "content" else "content"
                
                try:
                    was_processed = validator.post_process_generated_content(str(md_file), component_type)
                    if was_processed:
                        fixed_files += 1
                        print(f"   ✅ Fixed: {md_file.relative_to(content_dir)}")
                    else:
                        print(f"   ⚪ OK: {md_file.relative_to(content_dir)}")
                except Exception as e:
                    print(f"   ❌ Error: {md_file.relative_to(content_dir)} - {e}")
        
        print(f"\n📊 YAML Processing Complete:")
        print(f"📁 Total files processed: {total_files}")
        print(f"✅ Files fixed: {fixed_files}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing validator: {e}")
        return False


def run_comprehensive_tests() -> bool:
    """Run comprehensive test suite."""
    print("🧪 Z-BEAM COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Environment Check
    print("\n1️⃣  ENVIRONMENT TESTS")
    print("-" * 30)
    try:
        env_results = check_environment()
        test_results["environment"] = True
        print("   ✅ Environment check completed")
    except Exception as e:
        print(f"   ❌ Environment check failed: {e}")
        test_results["environment"] = False
    
    # Test 2: API Connectivity
    print("\n2️⃣  API CONNECTIVITY TESTS")
    print("-" * 30)
    try:
        api_results = test_api_connectivity()
        successful_apis = sum(1 for result in api_results.values() if result['success'])
        total_apis = len(api_results)
        
        for provider, result in api_results.items():
            status = "✅" if result['success'] else "❌"
            provider_name = API_PROVIDERS[provider]['name']
            print(f"   {status} {provider_name}: {result.get('error', 'OK')}")
        
        test_results["api"] = successful_apis > 0
        print(f"   📊 API Success: {successful_apis}/{total_apis}")
        
    except Exception as e:
        print(f"   ❌ API tests failed: {e}")
        test_results["api"] = False
    
    # Test 3: Component Configuration
    print("\n3️⃣  COMPONENT CONFIGURATION TESTS")
    print("-" * 30)
    try:
        components_config = COMPONENT_CONFIG.get("components", {})
        enabled_count = sum(1 for config in components_config.values() if config["enabled"])
        
        print(f"   📊 Total components: {len(components_config)}")
        print(f"   ✅ Enabled components: {enabled_count}")
        
        test_results["components"] = enabled_count > 0
        
    except Exception as e:
        print(f"   ❌ Component configuration test failed: {e}")
        test_results["components"] = False
    
    # Final Summary
    print(f"\n🎯 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name.replace('_', ' ').title()}")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! System ready for use.")
    elif passed_tests >= total_tests * 0.8:
        print("✅ MOST TESTS PASSED. System partially functional.")
    else:
        print("❌ MULTIPLE FAILURES. System requires attention.")
    
    return passed_tests >= total_tests * 0.8


def create_arg_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Z-Beam Dynamic Content Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 run.py                                    # Generate all materials (batch mode)
  python3 run.py --material "Copper"                # Generate all components for Copper
  python3 run.py --material "Steel" --components "frontmatter,content"  # Specific components
  python3 run.py --material "Aluminum" --author 2   # Generate with Italian writing style
  python3 run.py --interactive                      # Interactive mode with user prompts
  python3 run.py --list-materials                   # List all available materials
  python3 run.py --show-config                      # Show component configuration
  python3 run.py --yaml                            # Validate and fix YAML errors
  python3 run.py --clean                           # Remove all generated content files
  python3 run.py --test-api                        # Test API connection
        """,
    )

    # Main operation modes
    parser.add_argument("--material", help="Generate content for specific material")
    parser.add_argument("--components", help="Comma-separated list of components to generate")
    parser.add_argument("--author", type=int, help="Author ID for country-specific writing style")
    parser.add_argument("--start-index", type=int, default=1, help="Start batch generation at specific material index")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode with user prompts")
    parser.add_argument("--yaml", action="store_true", help="Validate and fix YAML errors")
    parser.add_argument("--test-api", action="store_true", help="Test API connection")
    parser.add_argument("--test", action="store_true", help="Run comprehensive test suite")
    parser.add_argument("--check-env", action="store_true", help="Check environment variables and API keys")
    parser.add_argument("--clean", action="store_true", help="Remove all generated content files")

    # Listing operations
    parser.add_argument("--list-materials", action="store_true", help="List all available materials")
    parser.add_argument("--list-components", action="store_true", help="List all available components")
    parser.add_argument("--list-authors", action="store_true", help="List all available authors")
    parser.add_argument("--show-config", action="store_true", help="Show component configuration")

    # General options
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    return parser


def main():
    """Main entry point for Z-Beam clean generation system."""
    parser = create_arg_parser()
    args = parser.parse_args()

    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Route to appropriate operation
        if args.yaml:
            success = run_yaml_validation()

        elif args.test:
            success = run_comprehensive_tests()

        elif args.clean:
            success = clean_content_components()

        elif (
            args.list_materials
            or args.list_components
            or args.list_authors
            or args.show_config
            or args.check_env
        ):
            # List operations and configuration display
            if args.show_config:
                show_component_configuration()
                success = True
            elif args.check_env:
                check_environment()
                success = True
            else:
                try:
                    from generators.dynamic_generator import DynamicGenerator
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

                    if args.list_authors:
                        list_authors()

                    success = True
                except ImportError as e:
                    print(f"❌ Error importing generator: {e}")
                    success = False

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
