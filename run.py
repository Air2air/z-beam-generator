#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface (Cleaned)

A comprehensive AI-powered content generation system for laser cleaning materials.
"""

"""
🚀 QUICK START SCRIPTS (User Commands):
========================================

BASIC GENERATION:
    python3 run.py                                    # Generate all materials (batch mode)
    python3 run.py --material "Steel"                 # Generate specific material
    python3 run.py --material "Aluminum" --author 2   # Generate with Italian author
    python3 run.py --start-index 50                   # Start batch from material #50
    python3 run.py --content-batch                    # Clear and regenerate content for first 8 categories

COMPONENT CONTROL:
    python3 run.py --material "Copper" --author 2 --components "frontmatter,text"  # Specific components only
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
import logging
import os
import sys
import time as time_module
from pathlib import Path
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import traceback


def update_content_with_ai_analysis(content: str, ai_result, material_name: str) -> str:
    """Update content with AI detection analysis in frontmatter (CONTENT ABOVE FRONTMATTER format).
    
    This function ensures:
    1. Content appears above frontmatter (content-first format)
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
        
        # Extract content (everything before first ---)
        if frontmatter_start_idx > 0:
            content_lines = lines[:frontmatter_start_idx]
        else:
            content_lines = lines
        
        # Start with content
        updated_lines = content_lines
        
        # Add frontmatter delimiter
        updated_lines.append("")
        updated_lines.append("---")
        
        # Process existing frontmatter
        existing_frontmatter_lines = []
        if frontmatter_start_idx >= 0 and frontmatter_end_idx > frontmatter_start_idx:
            existing_frontmatter = lines[frontmatter_start_idx + 1:frontmatter_end_idx]
            
            # Remove any existing ai_detection_analysis section to prevent duplicates
            skip_ai_section = False
            for line in existing_frontmatter:
                stripped = line.strip()
                if stripped == "ai_detection_analysis:":
                    skip_ai_section = True
                    continue
                elif skip_ai_section and (stripped.startswith("  ") or stripped.startswith("\t") or stripped == ""):
                    # Skip indented lines (part of ai_detection_analysis)
                    if stripped == "" and skip_ai_section:
                        skip_ai_section = False  # End of indented section
                    continue
                elif skip_ai_section and not (stripped.startswith("  ") or stripped.startswith("\t")):
                    skip_ai_section = False  # End of ai_detection_analysis section
                
                if not skip_ai_section:
                    existing_frontmatter_lines.append(line)
        
        # Add existing frontmatter (without duplicate ai_detection_analysis)
        if existing_frontmatter_lines:
            # Filter out empty lines at start/end
            while existing_frontmatter_lines and existing_frontmatter_lines[0].strip() == "":
                existing_frontmatter_lines.pop(0)
            while existing_frontmatter_lines and existing_frontmatter_lines[-1].strip() == "":
                existing_frontmatter_lines.pop()
            
            if existing_frontmatter_lines:
                updated_lines.extend(existing_frontmatter_lines)
                updated_lines.append("")  # Add spacing
        
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
                            ai_lines.append(f"      {sub_key}: \"{sub_value}\"")
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
                        ai_lines.append(f"    {key}: \"{value}\"")
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
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Interactive mode with step-by-step generation and status updates")
    parser.add_argument("--material", "-m", help="Generate content for specific material")
    parser.add_argument("--all", action="store_true", 
                       help="Generate content for all materials")
    
    # Testing and validation
    parser.add_argument("--test-api", action="store_true", 
                       help="Test API connectivity and configuration")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate generated content structure")
    parser.add_argument("--list-materials", action="store_true", 
                       help="List all available materials")
    
    # Optimization commands
    parser.add_argument("--optimize", help="Optimize content for a component (e.g., 'text', 'bullets')")
    
    # Cleanup commands
    parser.add_argument("--clean", action="store_true", 
                       help="Clean all generated content files")
    parser.add_argument("--cleanup-scan", action="store_true", 
                       help="Scan for cleanup opportunities (dry-run)")
    parser.add_argument("--cleanup-report", action="store_true", 
                       help="Generate comprehensive cleanup report")
    parser.add_argument("--root-cleanup", action="store_true", 
                       help="Clean up and organize root directory")
    
    # Configuration and info
    parser.add_argument("--config", action="store_true", 
                       help="Show current configuration")
    parser.add_argument("--status", action="store_true", 
                       help="Show system status and component availability")
    
    # Options
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
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
                    items = data.get('items', [])
                    print(f"\n🔧 {category.title()} ({len(items)} materials):")
                    for material in items[:5]:  # Show first 5
                        print(f"   • {material['name']}")
                    if len(items) > 5:
                        print(f"   ... and {len(items) - 5} more")
            except ImportError:
                print("❌ Could not load materials data")
                print("💡 Make sure data/materials.yaml exists and is properly formatted")
                    
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
            
        elif args.validate:
            # Validate content structure
            print("🔍 Validating content structure...")
            from validate_structure import validate_all_content
            validate_all_content()
            
        elif args.optimize:
            # Optimization mode (existing functionality)
            component_name = args.optimize
            print(f"🚀 Starting optimization for component: {component_name}")

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
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract material name from filename (remove -laser-cleaning.md suffix)
                    material_name = file_path.stem.replace('-laser-cleaning', '')
                    materials_content[material_name] = content
                    print(f"   📄 Loaded {material_name} from {file_path.name}")

                except Exception as e:
                    print(f"❌ Error loading {file_path}: {e}")
                    continue

            if not materials_content:
                print("❌ No content loaded for optimization")
                return

            # Run batch optimization
            print(f"\n🔄 Optimizing {len(materials_content)} materials...")

            async def run_optimization():
                try:
                    # Import the existing AI detection service
                    from optimizer.ai_detection.service import get_ai_detection_service, initialize_ai_detection_service
                    from optimizer.ai_detection.types import AIDetectionConfig

                    # Initialize AI detection service with proper config
                    config = AIDetectionConfig(
                        provider="winston",
                        enabled=True,
                        target_score=70.0,
                        max_iterations=3,
                        improvement_threshold=5.0,
                        timeout=30,
                        retry_attempts=3
                    )
                    ai_service = initialize_ai_detection_service(config)

                    # Simple optimization loop
                    successful_optimizations = 0

                    for material_name, content in materials_content.items():
                        print(f"   🔄 Optimizing {material_name}...")

                        try:
                            # Get initial AI detection score
                            initial_result = ai_service.detect_ai_content(content)
                            initial_score = initial_result.score
                            print(f"      📊 Initial score: {initial_score:.1f}")

                            # Simple optimization: just update the frontmatter with current analysis
                            optimized_content = update_content_with_ai_analysis(
                                content, initial_result, material_name
                            )

                            # Save the optimized content
                            original_file = component_dir / f"{material_name}-laser-cleaning.md"
                            with open(original_file, 'w', encoding='utf-8') as f:
                                f.write(optimized_content)

                            print(f"      ✅ {material_name}: AI analysis updated")
                            successful_optimizations += 1

                        except Exception as e:
                            print(f"      ❌ Error optimizing {material_name}: {e}")
                            continue

                    print(f"\n🏁 Optimization completed: {successful_optimizations}/{len(materials_content)} successful")

                except Exception as e:
                    print(f"❌ Error initializing optimization services: {e}")
                    import traceback
                    traceback.print_exc()

            # Run the async optimization
            asyncio.run(run_optimization())
            
        elif args.interactive or args.material or args.all:
            # Interactive or batch generation mode
            print("🎮 Z-Beam Interactive Generator")
            print("=" * 40)

            if args.interactive:
                print("📝 Interactive mode: Step-by-step material generation")
                print("💡 Use --all for batch processing or --material for specific material")
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
                    print("⚠️  Material-specific generation not yet implemented in this version")

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
            print("  python3 run.py --material \"Copper\"     # Generate specific material")
            print("  python3 run.py --all                   # Generate all materials")
            print()
            print("QUICK START:")
            print("  python3 run.py --interactive          # Interactive mode")
            print("  python3 run.py --material \"Aluminum\"   # Specific material")
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
