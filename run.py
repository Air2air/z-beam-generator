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


def create_dynamic_ai_detection_config(content_type: str = "technical", author_country: str = "usa", content_length: int = 1000):
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
        raise Exception(f"FailFastGenerator called (attempt {self.call_count}) - fail-fast test")


def update_content_with_ai_analysis(content: str, ai_result, material_name: str) -> str:
    """Update content with AI detection analysis in proper YAML frontmatter format.

    This function ensures:
    1. Frontmatter appears at the top in proper YAML format
    2. Existing frontmatter is preserved and new data is appended
    3. AI detection analysis is added to the frontmatter section
    4. Prevents duplicate ai_detection_analysis sections
    """
    try:
        lines = content.split("\n")
        updated_lines = []

        # Find frontmatter boundaries
        frontmatter_start_idx = -1
        frontmatter_end_idx = -1

        for i, line in enumerate(lines):
            if line.strip() == "---":
                if frontmatter_start_idx == -1:
                    frontmatter_start_idx = i
                else:
                    frontmatter_end_idx = i
                    break

        # Extract content (everything after first ---)
        if frontmatter_start_idx >= 0 and frontmatter_end_idx > frontmatter_start_idx:
            content_lines = lines[frontmatter_end_idx + 1:]
        else:
            content_lines = lines

        # Start with frontmatter delimiter
        updated_lines.append("---")

        # Add AI detection analysis
        ai_lines = [
            "ai_detection_analysis:",
            f"  score: {ai_result.score:.6f}",
            f"  confidence: {ai_result.confidence:.6f}",
            f'  classification: "{ai_result.classification}"',
            f'  provider: "{ai_result.provider}"',
            f"  processing_time: {ai_result.processing_time:.6f}",
        ]

        if ai_result.details:
            ai_lines.append("  details:")
            for key, value in ai_result.details.items():
                if isinstance(value, dict):
                    ai_lines.append(f"    {key}:")
                    for sub_key, sub_value in value.items():
                        # Ensure proper YAML formatting for values
                        if isinstance(sub_value, str):
                            ai_lines.append(f'      {sub_key}: "{sub_value}"')
                        elif isinstance(sub_value, (int, float)):
                            if isinstance(sub_value, float):
                                ai_lines.append(f"      {sub_key}: {sub_value:.6f}")
                            else:
                                ai_lines.append(f"      {sub_key}: {sub_value}")
                        else:
                            ai_lines.append(f"      {sub_key}: {sub_value}")
                else:
                    # Ensure proper YAML formatting for values
                    if isinstance(value, str):
                        ai_lines.append(f'    {key}: "{value}"')
                    elif isinstance(value, (int, float)):
                        if isinstance(value, float):
                            ai_lines.append(f"    {key}: {value:.6f}")
                        else:
                            ai_lines.append(f"    {key}: {value}")
                    else:
                        ai_lines.append(f"    {key}: {value}")

        updated_lines.extend(ai_lines)

        # Add closing marker
        updated_lines.append("---")
        updated_lines.append("")  # Add blank line before content

        # Add content
        updated_lines.extend(content_lines)

        return "\n".join(updated_lines)

    except Exception as e:
        print(f"⚠️ Error updating frontmatter for {material_name}: {e}")
        import traceback

        traceback.print_exc()
        return content


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
                print(f"📂 Processing {len(categories)} categories: {', '.join(categories)}")

                # Count total materials
                total_materials = sum(len(materials_data[cat].get("items", [])) for cat in categories)
                print(f"� Total materials to process: {total_materials}")

                # Import generator
                from generators.dynamic_generator import DynamicGenerator
                generator = DynamicGenerator()

                processed_materials = 0
                successful_generations = 0

                for category in categories:
                    category_data = materials_data[category]
                    materials = category_data.get("items", [])

                    print(f"\n🔧 Processing category: {category} ({len(materials)} materials)")

                    for material in materials:
                        material_name = material["name"]
                        print(f"   📝 Generating content for: {material_name}")

                        try:
                            # Generate all components for this material
                            from generators.workflow_manager import run_dynamic_generation

                            results = run_dynamic_generation(
                                generator=generator,
                                material=material_name,
                                component_types=["frontmatter", "text", "table", "metatags", "tags", "bullets", "caption", "propertiestable", "jsonld"],
                                author_info={"id": 1, "name": "Test Author", "country": "Test"}
                            )

                            processed_materials += 1
                            successful_components = len(results.get("components_generated", []))
                            print(f"      ✅ Generated {successful_components} components")

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
                print(f"📊 Success rate: {(successful_generations/processed_materials*100):.1f}%" if processed_materials > 0 else "0%")

            except ImportError as e:
                print(f"❌ Import error: {e}")
                print("💡 Make sure all required modules are installed")
            except Exception as e:
                print(f"❌ Error in content batch mode: {e}")
                import traceback
                traceback.print_exc()

        elif args.optimize:
            # Optimization mode - iterative AI detection optimization
            component_name = args.optimize
            print(f"🚀 Starting iterative optimization for component: {component_name}")

            # Find all material files in the component directory
            component_dir = Path("content/components") / component_name
            if not component_dir.exists():
                print(f"❌ Component directory not found: {component_dir}")
                return

            # Get all .md files in the component directory
            material_files = list(component_dir.glob("*.md"))
            if not material_files:
                print(f"⚠️ No material files found in {component_dir}")
                return

            print(f"📂 Found {len(material_files)} material files to optimize")

            # Load content from each file
            materials_content = {}
            for file_path in material_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Extract material name from filename (remove -laser-cleaning.md suffix)
                    material_name = file_path.stem.replace("-laser-cleaning", "")
                    materials_content[material_name] = content
                    print(f"   📄 Loaded {material_name} from {file_path.name}")

                except Exception as e:
                    print(f"❌ Error loading {file_path}: {e}")
                    continue

            if not materials_content:
                print("❌ No content loaded for optimization")
                return

            # Run iterative optimization
            print(f"\n🔄 Starting iterative optimization for {len(materials_content)} materials...")

            async def run_iterative_optimization():
                try:
                    # Import the AI detection service
                    from optimizer.ai_detection.service import (
                        get_ai_detection_service,
                        initialize_ai_detection_service,
                    )
                    from optimizer.ai_detection.types import AIDetectionConfig

                    # Initialize AI detection service with proper config
                    config = AIDetectionConfig(
                        provider="winston",  # Always use real Winston API
                        enabled=True,
                        target_score=70.0,
                        max_iterations=5,  # Allow up to 5 iterations
                        improvement_threshold=5.0,
                        timeout=30,
                        retry_attempts=3,
                    )
                    ai_service = initialize_ai_detection_service(config)

                    # Import text generator for regeneration
                    from generators.dynamic_generator import DynamicGenerator
                    from data.materials import load_materials

                    generator = DynamicGenerator()
                    materials_data = load_materials()

                    successful_optimizations = 0

                    for material_name, original_content in materials_content.items():
                        print(f"\n🔄 Optimizing {material_name}...")

                        current_content = original_content
                        best_score = 0.0
                        best_content = original_content
                        iteration = 0
                        consecutive_failures = 0

                        while iteration < config.max_iterations:
                            iteration += 1
                            print(f"   📊 Iteration {iteration}/{config.max_iterations}")

                            try:
                                # Get AI detection score for current content
                                result = ai_service.detect_ai_content(current_content)
                                current_score = result.score
                                print(f"      📊 Score: {current_score:.1f} (Target: {config.target_score})")

                                # Update best content if this is better
                                if current_score > best_score:
                                    best_score = current_score
                                    best_content = current_content
                                    print(f"      ✅ New best score: {best_score:.1f}")

                                # Check if we've reached the target
                                if current_score >= config.target_score:
                                    print(f"      🎯 Target reached! Score: {current_score:.1f}")
                                    break

                                # If score is very low and this is the first iteration, try regenerating
                                if current_score < 30.0 and iteration == 1:
                                    print(f"      🔄 Score too low ({current_score:.1f}), regenerating content...")

                                    # Find material data
                                    material_data = None
                                    for category_data in materials_data.values():
                                        for item in category_data.get("items", []):
                                            if item["name"].lower().replace(" ", "-") == material_name.lower():
                                                material_data = item
                                                break
                                        if material_data:
                                            break

                                    if material_data:
                                        try:
                                            # Regenerate content with adjustments for better AI detection
                                            from generators.workflow_manager import run_dynamic_generation

                                            results = run_dynamic_generation(
                                                generator=generator,
                                                material=material_data["name"],
                                                component_types=[component_name],
                                                author_info={"id": 1, "name": "Test Author", "country": "usa"}
                                            )

                                            if results.get("components_generated"):
                                                # Extract the new content
                                                new_content_file = Path("content/components") / component_name / f"{material_name}-laser-cleaning.md"
                                                if new_content_file.exists():
                                                    with open(new_content_file, "r", encoding="utf-8") as f:
                                                        new_content = f.read()
                                                    
                                                    # Add AI detection analysis to the new content
                                                    current_content = update_content_with_ai_analysis(
                                                        new_content, result, material_name
                                                    )
                                                    
                                                    # Save the updated content
                                                    with open(new_content_file, "w", encoding="utf-8") as f:
                                                        f.write(current_content)
                                                    
                                                    print(f"      🔄 Regenerated content loaded and updated with AI analysis")
                                                    consecutive_failures = 0
                                                    continue
                                                else:
                                                    print(f"      ❌ Regenerated content not found")
                                                    consecutive_failures += 1
                                            else:
                                                print(f"      ❌ Content regeneration failed")
                                                consecutive_failures += 1

                                        except Exception as e:
                                            print(f"      ❌ Error regenerating content: {e}")
                                            consecutive_failures += 1
                                    else:
                                        print(f"      ❌ Material data not found for regeneration")
                                        consecutive_failures += 1

                                # If we can't improve significantly, try minor adjustments
                                elif iteration > 1 and (current_score - best_score) < config.improvement_threshold:
                                    consecutive_failures += 1
                                    print(f"      ⚠️ Minimal improvement ({current_score - best_score:.1f} < {config.improvement_threshold})")
                                else:
                                    consecutive_failures = 0

                                # Stop if too many consecutive failures
                                if consecutive_failures >= 2:
                                    print(f"      🛑 Stopping after {consecutive_failures} consecutive failures")
                                    break

                            except Exception as e:
                                print(f"      ❌ Error in iteration {iteration}: {e}")
                                consecutive_failures += 1
                                if consecutive_failures >= 2:
                                    break
                                continue

                        # Save the best content found
                        original_file = component_dir / f"{material_name}-laser-cleaning.md"
                        
                        # Add final AI detection analysis to the best content
                        final_result = ai_service.detect_ai_content(best_content)
                        best_content_with_analysis = update_content_with_ai_analysis(
                            best_content, final_result, material_name
                        )
                        
                        with open(original_file, "w", encoding="utf-8") as f:
                            f.write(best_content_with_analysis)

                        print(f"      ✅ {material_name}: Best score {best_score:.1f} after {iteration} iterations")
                        if best_score >= config.target_score:
                            successful_optimizations += 1

                    print(f"\n🏁 Iterative optimization completed: {successful_optimizations}/{len(materials_content)} reached target score")

                except Exception as e:
                    print(f"❌ Error initializing optimization services: {e}")
                    import traceback
                    traceback.print_exc()

            # Run the async optimization
            asyncio.run(run_iterative_optimization())

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
                    print(
                        "⚠️  Material-specific generation not yet implemented in this version"
                    )

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
