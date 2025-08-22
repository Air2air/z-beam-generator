#!/usr/bin/env python3
"""
Z-Beam Dynamic Content Generation System

FEATURES:
- Dynamic schema-driven content generation
- Component-specific generation with user selection
- Standardized DeepSeek API integration
- Real-time validation and error correction
- Interactive and batch generation modes

USAGE:
    python3 run.py                                    # Interactive generation mode
    python3 run.py --material "Copper"                # Generate all components for specific material
    python3 run.py --material "Steel" --components "frontmatter,content"  # Generate specific components
    python3 run.py --list-materials                   # List all available materials
    python3 run.py --list-components                  # List all available components
    python3 run.py --yaml                            # Validate and fix YAML errors
    python3 run.py --test-api                        # Test API connection

DYNAMIC GENERATION:
- Schema-driven field mapping from JSON schemas
- Component-specific prompt templates
- Dynamic content adaptation based on material properties
- Automatic validation against schema requirements
- Real-time error detection and correction
"""

import sys
import argparse
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_dynamic_generation(material: str = None, components: list = None, 
                          interactive: bool = False, test_api: bool = False):
    """Run dynamic schema-driven content generation."""
    
    try:
        from generators.dynamic_generator import DynamicGenerator
        from api.client import APIClient
    except ImportError as e:
        print(f"❌ Error importing required modules: {e}")
        print("   Make sure all generator modules are available")
        return False
    
    print("🚀 DYNAMIC SCHEMA-DRIVEN GENERATION")
    print("=" * 50)
    
    # Initialize generator
    try:
        api_client = APIClient()
        generator = DynamicGenerator(api_client=api_client)
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        return False
    
    # Test API connection if requested
    if test_api:
        print("🔗 Testing API connection...")
        if api_client.test_connection():
            print("✅ API connection successful!")
            return True
        else:
            print("❌ API connection failed!")
            return False
    
    # Interactive mode
    if interactive:
        return run_interactive_generation(generator)
    
    # List materials if requested
    if material is None:
        materials = generator.get_available_materials()
        print(f"📋 Available materials ({len(materials)}):")
        for i, mat in enumerate(sorted(materials)[:20], 1):
            print(f"   {i:2d}. {mat}")
        if len(materials) > 20:
            print(f"   ... and {len(materials) - 20} more materials")
        return True
    
    # Generate for specific material
    return run_material_generation(generator, material, components)

def run_interactive_generation(generator):
    """Run interactive generation with user prompts."""
    
    print("🎮 Interactive Generation Mode")
    print("Commands: Y/Yes (continue), S/Skip (skip material), Q/Quit (exit)")
    print("=" * 50)
    
    materials = generator.get_available_materials()
    available_components = generator.get_available_components()
    
    print(f"📊 Loaded {len(materials)} materials and {len(available_components)} components")
    print(f"🔧 Components: {', '.join(available_components)}")
    print()
    
    generated_count = 0
    skipped_count = 0
    
    try:
        for i, material in enumerate(materials, 1):
            print(f"\n📦 [{i}/{len(materials)}] Processing: {material}")
            
            # Ask user which components to generate
            print(f"Available components: {', '.join(available_components)}")
            response = input(f"Generate components for {material}? (Y/s/q/all/list components): ").strip().lower()
            
            if response in ['q', 'quit']:
                break
            elif response in ['s', 'skip']:
                print(f"⏭️  Skipped {material}")
                skipped_count += 1
                continue
            elif response in ['list', 'l']:
                print("Available components:")
                for j, comp in enumerate(available_components, 1):
                    print(f"   {j}. {comp}")
                continue
            elif response == 'all':
                selected_components = available_components
            elif response in ['', 'y', 'yes']:
                # Generate all components by default
                selected_components = available_components
            else:
                # Parse specific components
                selected_components = [c.strip() for c in response.split(',') if c.strip()]
                # Validate components
                invalid = [c for c in selected_components if c not in available_components]
                if invalid:
                    print(f"❌ Invalid components: {', '.join(invalid)}")
                    continue
            
            # Generate content
            success = run_material_generation(generator, material, selected_components)
            if success:
                generated_count += 1
            
    except KeyboardInterrupt:
        print("\n\n🛑 Generation interrupted by user")
    
    print("\n📊 Generation Summary:")
    print(f"   ✅ Generated: {generated_count} materials")
    print(f"   ⏭️  Skipped: {skipped_count} materials")
    print(f"   🎯 Total processed: {generated_count + skipped_count}/{len(materials)}")
    
    return True

def run_material_generation(generator, material: str, components: list = None):
    """Generate content for a specific material."""
    
    if components is None:
        components = generator.get_available_components()
    
    print(f"🔧 Generating {len(components)} components for {material}...")
    
    # Create generation request
    from generators.dynamic_generator import GenerationRequest
    
    request = GenerationRequest(
        material=material,
        components=components,
        output_dir="content"
    )
    
    # Generate content
    result = generator.generate_multiple(request)
    
    # Report results
    print(f"\n📋 Generation Results for {material}:")
    print(f"   Success: {result.success}")
    print(f"   Components: {result.successful_components}/{result.total_components}")
    
    for component_type, component_result in result.results.items():
        if component_result.success:
            print(f"   ✅ {component_type}")
        else:
            print(f"   ❌ {component_type}: {component_result.error_message}")
    
    return result.success

def run_yaml_validation():
    """Run comprehensive YAML validation and fixing across all files."""
    
    print("🔍 YAML VALIDATION & FIXING MODE")
    print("=" * 50)
    print("Scanning all component files for YAML errors...")
    print("Automatically fixing common formatting issues...")
    print("=" * 50)
    
    try:
        from validators.centralized_validator import CentralizedValidator
        
        validator = CentralizedValidator()
        content_dir = Path("content")
        validators_examples_dir = Path("validators/examples")
        
        total_files = 0
        fixed_files = 0
        error_files = []
        
        # Process all markdown files in content directory
        print("📁 Processing content directory...")
        if content_dir.exists():
            for md_file in content_dir.rglob("*.md"):
                total_files += 1
                
                try:
                    # Determine component type from file path
                    component_type = md_file.parent.name if md_file.parent.name != "content" else "content"
                    
                    was_processed = validator.post_process_generated_content(str(md_file), component_type)
                    
                    if was_processed:
                        fixed_files += 1
                        print(f"   ✅ Fixed: {md_file.relative_to(content_dir)}")
                    else:
                        print(f"   ⚪ OK: {md_file.relative_to(content_dir)}")
                        
                except Exception as e:
                    error_files.append(f"{md_file.name}: {str(e)}")
                    print(f"   ❌ Error: {md_file.relative_to(content_dir)} - {e}")
        else:
            print("   ⚠️  Content directory not found")
        
        # Process validator examples directory
        print("\n📁 Processing validators/examples directory...")
        if validators_examples_dir.exists():
            for md_file in validators_examples_dir.glob("*.md"):
                total_files += 1
                
                try:
                    # Component type is the filename without extension
                    component_type = md_file.stem
                    
                    was_processed = validator.post_process_generated_content(str(md_file), component_type)
                    
                    if was_processed:
                        fixed_files += 1
                        print(f"   ✅ Fixed: examples/{md_file.name}")
                    else:
                        print(f"   ⚪ OK: examples/{md_file.name}")
                        
                except Exception as e:
                    error_files.append(f"examples/{md_file.name}: {str(e)}")
                    print(f"   ❌ Error: examples/{md_file.name} - {e}")
        else:
            print("   ⚠️  Validators/examples directory not found")
        
        print("\n📊 YAML PROCESSING COMPLETE")
        print("=" * 50)
        print(f"📁 Total files processed: {total_files}")
        print(f"✅ Files fixed: {fixed_files}")
        print(f"❌ Files with errors: {len(error_files)}")
        
        if error_files:
            print("\n⚠️  Error Details:")
            for error in error_files[:10]:  # Show first 10 errors
                print(f"   {error}")
            if len(error_files) > 10:
                print(f"   ... and {len(error_files) - 10} more errors")
        
        print("\n🎯 YAML validation and fixing complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importing validator: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

def main():
    """Main entry point for Z-Beam dynamic generation system."""
    
    parser = argparse.ArgumentParser(
        description="Z-Beam Dynamic Content Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 run.py                                    # Interactive generation mode
  python3 run.py --material "Copper"                # Generate all components for Copper
  python3 run.py --material "Steel" --components "frontmatter,content"  # Specific components
  python3 run.py --list-materials                   # List all available materials
  python3 run.py --list-components                  # List all available components
  python3 run.py --yaml                            # Validate and fix YAML errors
  python3 run.py --test-api                        # Test API connection
  python3 run.py --interactive                     # Interactive mode
        """
    )
    
    # Main operation modes
    parser.add_argument("--material", help="Generate content for specific material")
    parser.add_argument("--components", help="Comma-separated list of components to generate")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--yaml", action="store_true", help="Validate and fix YAML errors")
    parser.add_argument("--test-api", action="store_true", help="Test API connection")
    
    # Listing operations
    parser.add_argument("--list-materials", action="store_true", help="List all available materials")
    parser.add_argument("--list-components", action="store_true", help="List all available components")
    
    # General options
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Route to appropriate operation
        if args.yaml:
            # YAML validation mode
            success = run_yaml_validation()
            
        elif args.list_materials or args.list_components:
            # List operations
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
                
                success = True
            except ImportError as e:
                print(f"❌ Error importing generator: {e}")
                success = False
                
        else:
            # Dynamic generation mode (default)
            components_list = None
            if args.components:
                components_list = [c.strip() for c in args.components.split(',')]
            
            success = run_dynamic_generation(
                material=args.material,
                components=components_list,
                interactive=args.interactive or (args.material is None and not args.test_api),
                test_api=args.test_api
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
