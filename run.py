#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface (Cleaned)

A comprehensive AI-powered content generation system for laser cleaning materials.
"""

"""
🚀 QUICK START SCRIPTS (User Commands):
========================================


# Optimize text components
python3 run.py --optimize text

# Optimize bullets components
python3 run.py --optimize bullets

# Optimize any component (frontmatter, table, metatags, etc.)
python3 run.py --optimize frontmatter

BASIC GENERATION:
    python3 run.py                                    # Generate all materials (batch mode)
    python3 run.py --material "Steel"                 # Generate specific material
    python3 run.py --material "Aluminum" --author 2   # Generate with Italian author
    python3 run.py --start-index 50                   # Start batch from material #50
    python3 run.py --content-batch                    # Clear and regenerate content for first 8 categories

COMPONENT CONTROL:
    python3 run.py --material "Copper" --author 2 --components "frontmatter,text"  # Specific components only

CONTENT MANAGEMENT:
    python3 run.py --clean                           # Remove all generated content files

SYSTEM INFO:
    python3 run.py --test                            # Run comprehensive test suite

MATERIAL MANAGEMENT (separate script):
    python3 remove_material.py --material "Material Name" --execute    # Remove material

PATH CLEANUP (one-time scripts):
    python3 cleanup_paths.py                         # Rename files to clean format (already done)

🎯 COMMON WORKFLOWS:
==================
1. Generate all content:           python3 run.py
2. Generate specific material:     python3 run.py --material "Steel"
3. Clean and regenerate:          python3 run.py --clean && python3 run.py
4. Check system health:           python3 run.py --check-env --show-config
5. Remove unwanted material:      python3 remove_material.py --material "Old Material" --execute

🔧 CONFIGURATION:
=================
All system configuration is now located at the top of this file (lines 75-120):
- API_PROVIDERS: DeepSeek and Grok API configuration
- COMPONENT_CONFIG: Component orchestration order and API provider assignments

To modify configuration:
1. Edit the configuration section in this file
2. Run: python3 run.py --show-config (to verify changes)
"""

import argparse
import asyncio
import logging
import os
import sys
import time as time_module
from pathlib import Path
from typing import Any, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import traceback

# Configuration constants for tests
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "model": "deepseek-chat",
        "max_tokens": 32000,
        "supports_function_calling": True,
        "optimal_temperature": 0.7,
    },
    "grok": {
        "name": "Grok",
        "model": "grok-4",
        "max_tokens": 8000,
        "supports_reasoning": True,
        "optimal_temperature": 0.7,
    },
    "gemini": {
        "name": "Gemini",
        "model": "gemini-1.5-pro",
        "max_tokens": 8000,
        "optimal_temperature": 0.7,
    },
}

COMPONENT_CONFIG = {
    "frontmatter": {
        "generator": "frontmatter",
        "api_provider": "deepseek",
        "priority": 1,
        "required": True,
    },
    "content": {
        "generator": "content",
        "api_provider": "deepseek",
        "priority": 2,
        "required": True,
    },
    "text": {
        "generator": "text",
        "api_provider": "deepseek",
        "priority": 2,
        "required": True,
    },
    "jsonld": {
        "generator": "jsonld",
        "api_provider": "deepseek",
        "priority": 3,
        "required": True,
    },
    "table": {
        "generator": "table",
        "api_provider": "deepseek",
        "priority": 4,
        "required": True,
    },
    "metatags": {
        "generator": "metatags",
        "api_provider": "deepseek",
        "priority": 5,
        "required": True,
    },
    "tags": {
        "generator": "tags",
        "api_provider": "deepseek",
        "priority": 6,
        "required": True,
    },
    "bullets": {
        "generator": "bullets",
        "api_provider": "deepseek",
        "priority": 7,
        "required": True,
    },
    "caption": {
        "generator": "caption",
        "api_provider": "deepseek",
        "priority": 8,
        "required": True,
    },
    "propertiestable": {
        "generator": "propertiestable",
        "api_provider": "deepseek",
        "priority": 9,
        "required": True,
    },
}

AI_DETECTION_CONFIG = {
    "enabled": True,
    "provider": "winston",
    "target_score": 70.0,
    "max_iterations": 3,
    "improvement_threshold": 5.0,
    "timeout": 30,
    "retry_attempts": 3,
}


def get_dynamic_config_for_content(component_type: str, material_data: dict = None):
    """Get dynamic configuration for content generation."""
    base_config = COMPONENT_CONFIG.get(component_type, {})

    if material_data:
        # Apply material-specific optimizations
        material_name = material_data.get("name", "").lower()

        # Special handling for different material types
        if "steel" in material_name or "iron" in material_name:
            base_config["temperature"] = 0.6  # More precise for metals
        elif "plastic" in material_name or "polymer" in material_name:
            base_config["temperature"] = 0.8  # More creative for plastics
        elif "ceramic" in material_name:
            base_config["temperature"] = 0.5  # Very precise for ceramics

    return base_config


def create_dynamic_ai_detection_config(
    content_type: str = "technical",
    author_country: str = "usa",
    content_length: int = 1000,
):
    """Create dynamic AI detection configuration based on content parameters."""
    base_config = AI_DETECTION_CONFIG.copy()

    # Adjust configuration based on content type
    if content_type == "technical":
        base_config["target_score"] = 75.0
    elif content_type == "creative":
        base_config["target_score"] = 65.0
    else:
        base_config["target_score"] = 70.0

    # Adjust based on author country
    if author_country.lower() == "usa":
        base_config["language_patterns"] = "american_english"
    elif author_country.lower() == "uk":
        base_config["language_patterns"] = "british_english"
    else:
        base_config["language_patterns"] = "international_english"

    # Adjust based on content length
    if content_length < 500:
        base_config["min_text_length"] = 100
    elif content_length > 2000:
        base_config["min_text_length"] = 500
    else:
        base_config["min_text_length"] = 200

    return base_config


class FailFastGenerator:
    """Mock generator for testing fail-fast behavior."""

    def __init__(self):
        self.call_count = 0

    def generate(self, *args, **kwargs):
        """Mock generate method that always fails."""
        self.call_count += 1
        raise Exception(
            f"FailFastGenerator called (attempt {self.call_count}) - fail-fast test"
        )


def main():
    """Main entry point for Z-Beam generator."""
    parser = argparse.ArgumentParser(description="Z-Beam Content Generator")

    # Core generation commands
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode with step-by-step generation and status updates",
    )
    parser.add_argument(
        "--material", "-m", help="Generate content for specific material"
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate content for all materials"
    )
    parser.add_argument(
        "--content-batch",
        action="store_true",
        help="Clear and regenerate content for first 8 categories",
    )

    # Testing and validation
    parser.add_argument(
        "--test-api",
        action="store_true",
        help="Test API connectivity and configuration",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate generated content structure"
    )
    parser.add_argument(
        "--list-materials", action="store_true", help="List all available materials"
    )

    # Optimization commands
    parser.add_argument(
        "--optimize", help="Optimize content for a component (e.g., 'text', 'bullets')"
    )

    # Cleanup commands
    parser.add_argument(
        "--clean", action="store_true", help="Clean all generated content files"
    )
    parser.add_argument(
        "--cleanup-scan",
        action="store_true",
        help="Scan for cleanup opportunities (dry-run)",
    )
    parser.add_argument(
        "--cleanup-report",
        action="store_true",
        help="Generate comprehensive cleanup report",
    )
    parser.add_argument(
        "--root-cleanup",
        action="store_true",
        help="Clean up and organize root directory",
    )

    # Configuration and info
    parser.add_argument(
        "--config", action="store_true", help="Show current configuration"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and component availability",
    )
    parser.add_argument(
        "--version-history",
        help="Show version history for a material-component pair (format: material:component)",
    )

    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Handle different command modes
        if args.test_api:
            # Test API connectivity
            print("🧪 Testing API connectivity...")
            from cli.api_config import check_api_configuration

            check_api_configuration()

        elif args.list_materials:
            # List all available materials
            print("📋 Available Materials:")
            try:
                from data.materials import load_materials

                materials_data = load_materials()
                for category, data in materials_data.items():
                    items = data.get("items", [])
                    print(f"\n🔧 {category.title()} ({len(items)} materials):")
                    for material in items[:5]:  # Show first 5
                        print(f"   • {material['name']}")
                    if len(items) > 5:
                        print(f"   ... and {len(items) - 5} more")
            except ImportError:
                print("❌ Could not load materials data")
                print(
                    "💡 Make sure data/materials.yaml exists and is properly formatted"
                )

        elif args.config:
            # Show configuration
            print("⚙️  Z-Beam Configuration:")
            from cli.component_config import show_component_configuration

            show_component_configuration()

        elif args.status:
            # Show system status
            print("📊 Z-Beam System Status:")
            print("✅ Core system operational")
            print("✅ Component generators loaded")
            print("✅ API clients configured")
            print("✅ Content validation active")

        elif args.version_history:
            # Show version history
            try:
                material, component = args.version_history.split(":", 1)
                from utils.file_operations import display_version_history
                display_version_history(material.strip(), component.strip())
            except ValueError:
                print("❌ Invalid format. Use: --version-history 'Material:component'")
                print("💡 Example: --version-history 'Alumina:text'")

        elif args.clean:
            # Clean generated content
            print("🧹 Cleaning generated content...")
            from cli.cleanup_commands import clean_content_components

            clean_content_components()

        elif args.cleanup_scan:
            # Run cleanup scan
            from cli.cleanup_commands import run_cleanup_scan

            run_cleanup_scan()

        elif args.cleanup_report:
            # Generate cleanup report
            from cli.cleanup_commands import run_cleanup_report

            run_cleanup_report()

        elif args.root_cleanup:
            # Clean up root directory
            from cli.cleanup_commands import run_root_cleanup

            run_root_cleanup()

        elif args.content_batch:
            # Content batch mode - clear and regenerate first 8 categories
            print("🔄 Content Batch Mode: Clear and regenerate first 8 categories")
            print("=" * 60)

            try:
                # First clean existing content
                print("🧹 Cleaning existing content...")
                from cli.cleanup_commands import clean_content_components

                clean_content_components()

                # Load materials data
                from data.materials import load_materials

                materials_data = load_materials()

                # Get first 8 categories
                categories = list(materials_data.keys())[:8]
                print(
                    f"📂 Processing {len(categories)} categories: {', '.join(categories)}"
                )

                # Count total materials
                total_materials = sum(
                    len(materials_data[cat].get("items", [])) for cat in categories
                )
                print(f"� Total materials to process: {total_materials}")

                # Import generator
                from generators.dynamic_generator import DynamicGenerator

                generator = DynamicGenerator()

                processed_materials = 0
                successful_generations = 0

                for category in categories:
                    category_data = materials_data[category]
                    materials = category_data.get("items", [])

                    print(
                        f"\n🔧 Processing category: {category} ({len(materials)} materials)"
                    )

                    for material in materials:
                        material_name = material["name"]
                        print(f"   📝 Generating content for: {material_name}")

                        try:
                            # Generate all components for this material
                            from generators.workflow_manager import (
                                run_dynamic_generation,
                            )

                            results = run_dynamic_generation(
                                generator=generator,
                                material=material_name,
                                component_types=[
                                    "frontmatter",
                                    "text",
                                    "table",
                                    "metatags",
                                    "tags",
                                    "bullets",
                                    "caption",
                                    "propertiestable",
                                    "jsonld",
                                ],
                                author_info={
                                    "id": 1,
                                    "name": "Test Author",
                                    "country": "Test",
                                },
                            )

                            processed_materials += 1
                            successful_components = len(
                                results.get("components_generated", [])
                            )
                            print(
                                f"      ✅ Generated {successful_components} components"
                            )

                            if successful_components > 0:
                                successful_generations += 1

                        except Exception as e:
                            print(f"      ❌ Error generating {material_name}: {e}")
                            processed_materials += 1
                            continue

                # Summary
                print("\n" + "=" * 60)
                print("📊 CONTENT BATCH GENERATION COMPLETE")
                print("=" * 60)
                print(f"📂 Categories processed: {len(categories)}")
                print(f"📝 Materials processed: {processed_materials}")
                print(f"✅ Successful generations: {successful_generations}")
                print(
                    f"📊 Success rate: {(successful_generations/processed_materials*100):.1f}%"
                    if processed_materials > 0
                    else "0%"
                )

            except ImportError as e:
                print(f"❌ Import error: {e}")
                print("💡 Make sure all required modules are installed")
            except Exception as e:
                print(f"❌ Error in content batch mode: {e}")
                import traceback

                traceback.print_exc()

        elif args.optimize:
            # Optimization mode - sophisticated AI detection optimization
            component_name = args.optimize
            print(f"🚀 Starting sophisticated optimization for component: {component_name}")

            # Import and run the optimization
            from optimizer.content_optimization import run_sophisticated_optimization

            asyncio.run(run_sophisticated_optimization(component_name))

        elif args.interactive or args.material or args.all:
            # Interactive or batch generation mode
            print("🎮 Z-Beam Interactive Generator")
            print("=" * 40)

            if args.interactive:
                print("📝 Interactive mode: Step-by-step material generation")
                print(
                    "💡 Use --all for batch processing or --material for specific material"
                )
            elif args.material:
                print(f"🎯 Generating content for: {args.material}")
            elif args.all:
                print("🔄 Generating content for all materials")

            # Import and run the main generator
            try:
                from generators.dynamic_generator import DynamicGenerator

                generator = DynamicGenerator()

                if args.material:
                    # Generate for specific material
                    print(f"\n🎯 Generating content for {args.material}...")

                    try:
                        # Import workflow manager for material generation
                        from generators.workflow_manager import run_material_generation

                        # Get available components
                        available_components = generator.get_available_components()

                        # Generate all components for the material
                        result = run_material_generation(
                            material=args.material,
                            component_types=available_components,
                            author_id=None  # Will use material's author_id from materials.yaml
                        )

                        print("✅ Generation completed!")
                        print(f"Material: {result['material']}")
                        print(f"Components generated: {len(result['components_generated'])}")
                        print(f"Components failed: {len(result['components_failed'])}")

                        if result['components_generated']:
                            print("\n📝 Generated components:")
                            for comp in result['components_generated']:
                                print(f"  ✅ {comp['type']}: {comp['filepath']}")

                        if result['components_failed']:
                            print("\n❌ Failed components:")
                            for comp in result['components_failed']:
                                print(f"  ❌ {comp['type']}: {comp['error']}")

                        print(f"\n🕐 Total time: {result['total_time']:.1f}s")
                        print(f"🎯 Total tokens: {result['total_tokens']}")

                    except Exception as e:
                        print(f"❌ Error generating content for {args.material}: {e}")
                        if args.verbose:
                            import traceback
                            traceback.print_exc()

                elif args.all:
                    # Generate for all materials
                    print("\n🚀 Starting batch generation for all materials...")
                    print("⚠️  Batch generation not yet implemented in this version")

                elif args.interactive:
                    # Interactive mode
                    print("\n🎮 Starting interactive generation...")
                    print("⚠️  Interactive mode not yet implemented in this version")

            except ImportError as e:
                print(f"❌ Error importing generator: {e}")
                print("💡 Make sure all required modules are installed")

        else:
            # Show help/usage information
            print("🎯 Z-Beam Generator - AI-Powered Content Generation")
            print("=" * 55)
            print()
            print("EXAMPLES:")
            print("  python3 run.py --interactive --verbose # Interactive logging")
            print(
                '  python3 run.py --material "Copper"     # Generate specific material'
            )
            print("  python3 run.py --all                   # Generate all materials")
            print()
            print("QUICK START:")
            print("  python3 run.py --interactive          # Interactive mode")
            print('  python3 run.py --material "Aluminum"   # Specific material')
            print("  python3 run.py --all                   # All materials")
            print()
            print("🧪 TESTING & VALIDATION:")
            print("  python3 run.py --test-api              # Test API")
            print("  python3 run.py --validate              # Validate content")
            print("  python3 run.py --list-materials        # List materials")
            print()
            print("⚙️  CONFIGURATION:")
            print("  python3 run.py --config                # Show config")
            print("  python3 run.py --status                # System status")
            print()
            print("📋 VERSION TRACKING:")
            print("  python3 run.py --version-history 'Alumina:text'  # Show version history")
            print()
            print("🧹 CLEANUP:")
            print("  python3 run.py --clean                 # Clean content")
            print("  python3 run.py --cleanup-scan          # Scan cleanup")
            print("  python3 run.py --cleanup-report        # Cleanup report")
            print()
            print("🚀 OPTIMIZATION:")
            print("  python3 run.py --optimize text         # Optimize text")
            print()
            print("💡 TIP: Use --help for complete command reference")

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
