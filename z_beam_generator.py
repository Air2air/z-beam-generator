#!/usr/bin/env python3
"""
Z-Beam Generator - Clean, Simple Architecture

SUMMARY OF RE-ARCHITECTURE:
✅ Preserved: Legacy prompts, schemas, materials list
✅ Simplified: Removed ~70 dead files, complex validation systems
✅ Added: TDD approach, standardized API handling, clean separation of concerns
✅ Result: Simple, testable, maintainable system that actually works

ARCHITECTURE:
1. MaterialLoader - loads from lists/materials.yaml
2. ComponentGenerator - uses prompts + DeepSeek API  
3. SchemaValidator - validates against schemas/
4. ContentWriter - saves to content/ folder

USAGE:
    python3 z_beam_generator.py --material "Aluminum" --components "frontmatter,content"
    python3 z_beam_generator.py --all --limit 5
    python3 z_beam_generator.py --test-api
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from simple_generator import SimpleGenerator
from api_client import create_deepseek_client

# =============================================================================
# 🔧 USER CONFIGURATION
# =============================================================================

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = 'logs/z_beam_generation.log'

# Directory Configuration
REQUIRED_DIRECTORIES = [
    "content/components",
    "logs"
]

# Interactive Mode Configuration
INTERACTIVE_AUTO_CONTINUE = False  # Set to True to auto-continue without prompts
INTERACTIVE_DEFAULT_ACTION = "continue"  # continue, skip, pause, quit

# API Configuration
API_TIMEOUT_SECONDS = 60
API_MAX_RETRIES = 3

# =============================================================================
# 🏗️ CORE SETUP
# =============================================================================

# Load environment variables first
load_dotenv()

# Setup logging with user configuration
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Ensure required directories exist."""
    for directory in REQUIRED_DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)


def test_api_connection():
    """Test API connection and configuration."""
    logger.info("🧪 Testing API connection...")
    
    try:
        client = create_deepseek_client()
        result = client.test_connection()
        
        if result.success:
            logger.info(f"✅ API connection successful: {result.content}")
            logger.info(f"📊 Response time: {result.response_time:.2f}s, Tokens: {result.usage_tokens}")
            return True
        else:
            logger.error(f"❌ API connection failed: {result.error_message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        return False


def generate_single_material(material_name: str, component_types: list = None):
    """Generate content for a single material."""
    logger.info(f"🎯 Generating content for material: {material_name}")
    
    generator = SimpleGenerator()
    
    # Find the material
    materials = generator.material_loader.load_materials()
    target_material = None
    
    for material in materials:
        if material.name.lower() == material_name.lower():
            target_material = material
            break
    
    if not target_material:
        logger.error(f"❌ Material '{material_name}' not found")
        available = [m.name for m in materials[:10]]  # Show first 10
        logger.info(f"Available materials (first 10): {', '.join(available)}")
        return False
    
    # Generate components
    if component_types:
        for component_type in component_types:
            component = generator.generate_for_material(target_material, component_type)
            if component and component.is_valid:
                generator.writer.write_component(component)
                logger.info(f"✅ Generated {component_type} for {material_name}")
            else:
                logger.warning(f"⚠️ Failed to generate {component_type} for {material_name}")
    else:
        # Generate all available components
        components = generator.generate_all_for_material(target_material)
        valid_count = sum(1 for c in components.values() if c.is_valid)
        
        for component in components.values():
            if component.is_valid:
                generator.writer.write_component(component)
        
        logger.info(f"✅ Generated {valid_count}/{len(components)} components for {material_name}")
    
    return True


def generate_all_materials(limit: int = None):
    """Generate content for all materials."""
    logger.info("🚀 Starting bulk generation for all materials")
    
    generator = SimpleGenerator()
    
    if not test_api_connection():
        logger.error("❌ API connection failed, aborting bulk generation")
        return False
    
    generator.run(limit=limit)
    logger.info("✅ Bulk generation completed")
    return True


def generate_interactive(start_from: str = None):
    """Interactive generation mode with prompting to proceed."""
    logger.info("🎮 Starting interactive generation mode")
    
    generator = SimpleGenerator()
    
    if not test_api_connection():
        logger.error("❌ API connection failed, aborting interactive generation")
        return False
    
    # Load all materials
    materials = generator.material_loader.load_materials()
    total_materials = len(materials)
    start_index = 0
    
    # Find starting material if specified
    if start_from:
        for idx, material in enumerate(materials):
            if material.name.lower() == start_from.lower():
                start_index = idx
                break
        else:
            logger.error(f"❌ Starting material '{start_from}' not found")
            return False
        
        if start_index > 0:
            print(f"🎯 Starting from material: {materials[start_index].name}")
            materials = materials[start_index:]
    
    completed_materials = 0
    skipped_materials = 0
    
    print("\n📋 Interactive Material Generation")
    print(f"   Total materials available: {len(materials)}")
    if start_from:
        print(f"   Starting from: {start_from} (position {start_index + 1}/{total_materials})")
    print("   Press Ctrl+C at any time to exit\n")
    
    try:
        i = 0
        while i < len(materials):
            material = materials[i]
            completed_materials += 1
            
            print(f"🎯 [{completed_materials}/{total_materials}] Processing: {material.name} ({material.category})")
            
            # Generate components for current material
            components = generator.generate_all_for_material(material)
            
            # Write valid components and count results
            valid_count = 0
            total_count = len(components)
            
            for component in components.values():
                if component.is_valid:
                    generator.writer.write_component(component)
                    valid_count += 1
                    print(f"   ✅ Generated: {component.component_type}")
                else:
                    print(f"   ❌ Failed: {component.component_type}")
            
            print(f"   📊 Results: {valid_count}/{total_count} components generated")
            
            # Check if this is the last material
            if i == len(materials) - 1:
                print(f"\n🎉 All materials completed! ({completed_materials}/{total_materials})")
                if skipped_materials > 0:
                    print(f"   📝 Note: {skipped_materials} materials were skipped")
                break
            
            # Prompt for next material
            print(f"\n⏭️  Next material: {materials[i+1].name} ({materials[i+1].category})")
            print(f"   Progress: {completed_materials}/{total_materials} completed, {len(materials)-i-1} remaining")
            
            while True:
                try:
                    choice = input("Continue to next material? [Y/n/s/q/list]: ").strip().lower()
                    
                    if choice in ['', 'y', 'yes']:
                        print("")  # Add spacing
                        break
                    elif choice in ['n', 'no']:
                        print("⏸️  Pausing generation. You can resume later.")
                        print(f"   📊 Session summary: {completed_materials} completed, {skipped_materials} skipped")
                        return True
                    elif choice in ['s', 'skip']:
                        print(f"⏭️  Skipping {materials[i+1].name}")
                        # Remove the next material from list
                        skipped_materials += 1
                        materials.pop(i+1)
                        if i+1 < len(materials):
                            print(f"   Next after skip: {materials[i+1].name}")
                        print("")
                        break
                    elif choice in ['q', 'quit', 'exit']:
                        print("🛑 Exiting interactive generation.")
                        print(f"   📊 Session summary: {completed_materials} completed, {skipped_materials} skipped")
                        return True
                    elif choice in ['list', 'l']:
                        # Show remaining materials
                        remaining = materials[i+1:]
                        print(f"\n📋 Remaining materials ({len(remaining)}):")
                        for j, mat in enumerate(remaining[:10]):  # Show next 10
                            print(f"   {j+1}. {mat.name} ({mat.category})")
                        if len(remaining) > 10:
                            print(f"   ... and {len(remaining)-10} more")
                        print("")
                    else:
                        print("   Please enter: Y(es), N(o), S(kip), Q(uit), or List")
                        
                except EOFError:
                    print("\n🛑 Exiting interactive generation.")
                    return True
            
            i += 1
        
        print("✅ Interactive generation completed successfully!")
        print(f"   📊 Final summary: {completed_materials} completed, {skipped_materials} skipped")
        return True
        
    except KeyboardInterrupt:
        print("\n\n🛑 Generation interrupted by user.")
        print(f"   📊 Session summary: {completed_materials} completed, {skipped_materials} skipped")
        return True


def main():
    """Main entry point with command line interface."""
    parser = argparse.ArgumentParser(
        description="Z-Beam Content Generator - Clean Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --test-api                           # Test API connection
  %(prog)s --material "Aluminum"                # Generate all components for Aluminum
  %(prog)s --material "Steel" --components "frontmatter,content"  # Specific components
  %(prog)s --all --limit 5                     # Generate for first 5 materials
  %(prog)s --interactive                       # Interactive mode with prompts
  %(prog)s --interactive --start-from "Copper" # Start interactive mode from Copper
  %(prog)s --list-materials                    # List available materials
        """
    )
    
    parser.add_argument("--test-api", action="store_true", help="Test API connection only")
    parser.add_argument("--material", help="Generate content for specific material")
    parser.add_argument("--components", help="Comma-separated list of components to generate")
    parser.add_argument("--all", action="store_true", help="Generate content for all materials")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode with prompts to proceed")
    parser.add_argument("--start-from", help="Start interactive mode from a specific material name")
    parser.add_argument("--limit", type=int, help="Limit number of materials to process")
    parser.add_argument("--list-materials", action="store_true", help="List available materials")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup_directories()
    
    # Handle commands
    if args.test_api:
        success = test_api_connection()
        sys.exit(0 if success else 1)
    
    elif args.list_materials:
        generator = SimpleGenerator()
        materials = generator.material_loader.load_materials()
        
        print(f"\n📋 Available Materials ({len(materials)} total):")
        by_category = {}
        for material in materials:
            if material.category not in by_category:
                by_category[material.category] = []
            by_category[material.category].append(material.name)
        
        for category, names in by_category.items():
            print(f"\n  {category.upper()} ({len(names)}):")
            for name in sorted(names):
                print(f"    - {name}")
        sys.exit(0)
    
    elif args.material:
        component_types = None
        if args.components:
            component_types = [c.strip() for c in args.components.split(",")]
        
        success = generate_single_material(args.material, component_types)
        sys.exit(0 if success else 1)
    
    elif args.all:
        success = generate_all_materials(limit=args.limit)
        sys.exit(0 if success else 1)
    
    elif args.interactive:
        success = generate_interactive(start_from=args.start_from)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
