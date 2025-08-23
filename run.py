#!/usr/bin/env python3
"""
Z-Beam Dynamic Content Generation System

FEATURES:
- Dynamic schema-driven content generation
- Component-specific generation with user selection
- Multi-API provider support (DeepSeek, Grok)
- Component-level enable/disable controls
- Real-time validation and error correction
- Interactive and batch generation modes

USAGE:
    python3 run.py                                    # Interactive generation mode
    python3 run.py --material "Copper"                # Generate all components for specific material
    python3 run.py --material "Steel" --components "frontmatter,content"  # Generate specific components
    python3 run.py --material "Porcelain" --components "content"  
    python3 run.py --list-materials                   # List all available materials
    python3 run.py --list-components                  # List all available components
    python3 run.py --yaml                            # Validate and fix YAML errors
    python3 run.py --test-api                        # Test API connection

python3 -m tests


DYNAMIC GENERATION:
- Schema-driven field mapping from JSON schemas
- Component-specific prompt templates
- Dynamic content adaptation based on material properties
- Automatic validation against schema requirements
- Real-time error detection and correction

Examples:
  python3 -m tests              # Run all tests including API response validation


"""

# ==========================================
# COMPONENT CONFIGURATION
# ==========================================
# Configure API provider, author, and enable/disable for each component type
COMPONENT_CONFIG = {
    # Global author assignment for all components
    "author_id": 3,  # 1=Taiwan, 2=Italy, 3=Indonesia, 4=USA
    
    # Component-specific configuration
    "components": {
        "bullets": {
            "enabled": True,
            "api_provider": "deepseek"
        },
        "caption": {
            "enabled": True,
            "api_provider": "deepseek"
        },
        "frontmatter": {
            "enabled": True,
            "api_provider": "grok"  # Options: "deepseek", "grok"
        },
        "content": {
            "enabled": True,
            "api_provider": "grok"
        },
        "jsonld": {
            "enabled": True,
            "api_provider": "deepseek"
        },
        "table": {
            "enabled": True,
            "api_provider": "grok"
        },
        "metatags": {
            "enabled": True,
            "api_provider": "deepseek"
        },
        "tags": {
            "enabled": True,
            "api_provider": "deepseek"
        },
        "propertiestable": {
            "enabled": True,
            "api_provider": "deepseek"
        }
    }
}

# API Provider Configuration
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "env_key": "DEEPSEEK_API_KEY",
        "env_var": "DEEPSEEK_API_KEY",  # Add this for test compatibility
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat"
    },
        "grok": {
        "name": "Grok (X.AI)",
        "env_key": "GROK_API_KEY", 
        "env_var": "GROK_API_KEY",  # Add this for test compatibility
        "base_url": "https://api.x.ai",  # Remove /v1 since APIClient adds it
        "model": "grok-2"  # grok-2 works reliably; grok-4 currently uses reasoning tokens without completion output
    }
}

import sys
import os
import argparse
import json
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_api_client(provider: str, use_mock: bool = False):
    """Create an API client for the specified provider."""
    
    if provider not in API_PROVIDERS:
        raise ValueError(f"Unknown API provider: {provider}")
    
    provider_config = API_PROVIDERS[provider]
    
    if use_mock:
        from api.client import MockAPIClient
        return MockAPIClient()
    
    try:
        from api.client import APIClient
        from api.env_loader import EnvLoader
        
        # Get provider configuration with API key
        config = EnvLoader.get_provider_config(provider_config)
        
        # Check if API key was found
        if 'api_key' not in config:
            raise ValueError(f"API key not found for {provider}. Please set {provider_config['env_key']} in your environment.")
        
        # Create API client with provider-specific configuration
        return APIClient(
            api_key=config['api_key'],
            base_url=config["base_url"],
            model=config["model"]
        )
        
    except ImportError as e:
        raise ImportError(f"Failed to import API client modules: {e}")

def get_api_client_for_component(component_type: str, use_mock: bool = False):
    """Get the appropriate API client for a component type."""
    
    components_config = COMPONENT_CONFIG.get("components", {})
    if component_type in components_config:
        provider = components_config[component_type]["api_provider"]
    else:
        provider = "deepseek"  # Default provider
    
    return create_api_client(provider, use_mock=use_mock)

def load_authors():
    """Load author profiles from the authors.json file."""
    authors_file = Path("generators/authors.json")
    try:
        with open(authors_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            author_profiles = data.get('authorProfiles', [])
            # Extract the author objects from each profile
            authors = []
            for profile in author_profiles:
                if 'author' in profile:
                    authors.append(profile['author'])
            return authors
    except FileNotFoundError:
        print(f"❌ Authors file not found: {authors_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing authors file: {e}")
        return []

def get_author_by_id(author_id: int):
    """Get author by ID."""
    authors = load_authors()
    for author in authors:
        if author.get('id') == author_id:
            return author
    return None

def list_authors():
    """List all available authors with their IDs and countries."""
    authors = load_authors()
    if not authors:
        print("❌ No authors found!")
        return
    
    print("👤 Available Authors:")
    for author in authors:
        author_id = author.get('id', 'N/A')
        name = author.get('name', 'Unknown')
        country = author.get('country', 'Unknown')
        print(f"   {author_id}. {name} ({country})")

def run_dynamic_generation(material: str = None, components: list = None, 
                          interactive: bool = False, test_api: bool = False, 
                          author_id: int = None):
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
    
    # Validate and set author if provided
    author_info = None
    if author_id is not None:
        author_info = get_author_by_id(author_id)
        if author_info:
            print(f"👤 Using Author: {author_info['name']} ({author_info['country']})")
            # Set the author in the generator
            generator.set_author(author_info)
        else:
            print(f"❌ Author with ID {author_id} not found!")
            list_authors()
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
        return run_interactive_generation(generator, author_info)
    
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
    return run_material_generation(generator, material, components, author_info)

def run_interactive_generation(generator, author_info: dict = None):
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
            success = run_material_generation(generator, material, selected_components, author_info)
            if success:
                generated_count += 1
            
    except KeyboardInterrupt:
        print("\n\n🛑 Generation interrupted by user")
    
    print("\n📊 Generation Summary:")
    print(f"   ✅ Generated: {generated_count} materials")
    print(f"   ⏭️  Skipped: {skipped_count} materials")
    print(f"   🎯 Total processed: {generated_count + skipped_count}/{len(materials)}")
    
    return True

def save_component_to_file(content: str, filepath: str):
    """Save component content to the specified file path."""
    
    # Ensure the directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Saved to {filepath}")
        
    except Exception as e:
        print(f"  ❌ Failed to save {filepath}: {e}")
        raise

def save_component_to_file_original(material: str, component_type: str, content: str):
    """Save a component to the appropriate file path (original signature)."""
    
    # Create proper component directory structure: content/components/{component_type}/
    output_dir = Path("content") / "components" / component_type
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename: {material}-laser-cleaning.md
    material_slug = material.lower().replace(' ', '-').replace('_', '-')
    filename = f"{material_slug}-laser-cleaning.md"
    filepath = output_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Saved {component_type} to {filepath}")
    except Exception as e:
        logging.error(f"Error saving {component_type}: {e}")

def run_material_generation(generator, material: str, components: list = None, author_info: dict = None):
    """Generate content for a specific material with component configuration."""
    
    if components is None:
        components = generator.get_available_components()
    
    # Get the components configuration
    components_config = COMPONENT_CONFIG.get("components", {})
    
    # Filter components based on configuration
    enabled_components = []
    disabled_components = []
    
    for component in components:
        if component in components_config:
            if components_config[component]["enabled"]:
                enabled_components.append(component)
            else:
                disabled_components.append(component)
        else:
            # Default to enabled if not in config
            enabled_components.append(component)
    
    # Display component status
    print(f"🔧 Component Generation Plan for {material}:")
    print(f"   ✅ Enabled ({len(enabled_components)}): {', '.join(enabled_components)}")
    if disabled_components:
        print(f"   ❌ Disabled ({len(disabled_components)}): {', '.join(disabled_components)}")
    
    # Display API provider assignments
    print(f"\n🌐 API Provider Assignments:")
    for component in enabled_components:
        if component in components_config:
            provider = components_config[component]["api_provider"]
            provider_name = API_PROVIDERS.get(provider, {}).get("name", provider)
            print(f"   {component}: {provider_name}")
        else:
            print(f"   {component}: Default (DeepSeek)")
    
    if not enabled_components:
        print("❌ No components enabled for generation!")
        return False
    
    print(f"\n🚀 Generating {len(enabled_components)} enabled components...")
    
    # Generate each component with its specific API client
    successful_count = 0
    results = {}
    
    for component_type in enabled_components:
        try:
            # Get the appropriate API client for this component
            api_client = get_api_client_for_component(component_type)
            provider = components_config.get(component_type, {}).get("api_provider", "deepseek")
            provider_name = API_PROVIDERS.get(provider, {}).get("name", provider)
            
            # Determine author for ALL components using global author_id
            component_author_info = None
            
            # Use CLI author if specified, otherwise use global default
            if author_info is not None:
                component_author_info = author_info
            else:
                # Use global author_id from COMPONENT_CONFIG
                global_author_id = COMPONENT_CONFIG.get("author_id")
                if global_author_id:
                    component_author_info = get_author_by_id(global_author_id)
            
            print(f"\n🔧 Generating {component_type} using {provider_name}...")
            if component_author_info:
                print(f"   👤 Author: {component_author_info['name']} ({component_author_info['country']})")
            
            # Create a temporary generator with this API client
            from generators.dynamic_generator import DynamicGenerator
            temp_generator = DynamicGenerator(api_client=api_client)
            
            # Set author info for ALL components
            if component_author_info:
                temp_generator.set_author(component_author_info)
            
            # Generate this single component
            result = temp_generator.generate_component(material, component_type)
            
            if result.success:
                # Save the component using our own save logic
                save_component_to_file_original(material, component_type, result.content)
                successful_count += 1
                results[component_type] = result
                print(f"   ✅ {component_type} ({provider_name}) - {len(result.content)} chars generated")
            else:
                results[component_type] = result
                print(f"   ❌ {component_type} ({provider_name}): {result.error_message}")
                
        except Exception as e:
            print(f"   ❌ {component_type}: Error creating API client - {str(e)}")
            # Create a fake failed result
            from generators.dynamic_generator import ComponentResult
            results[component_type] = ComponentResult(
                component_type=component_type,
                content="",
                success=False,
                error_message=str(e)
            )
    
    # Report final results
    print(f"\n📋 Generation Results for {material}:")
    print(f"   Success: {successful_count > 0}")
    print(f"   Components: {successful_count}/{len(enabled_components)}")
    
    for component_type, result in results.items():
        provider = components_config.get(component_type, {}).get("api_provider", "default")
        provider_name = API_PROVIDERS.get(provider, {}).get("name", provider)
        
        if result.success:
            print(f"   ✅ {component_type} ({provider_name})")
        else:
            print(f"   ❌ {component_type} ({provider_name}): {result.error_message}")
    
    return successful_count > 0

def show_component_configuration():
    """Display current component configuration."""
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        from pathlib import Path
        env_path = Path(__file__).parent / '.env'
        load_dotenv(env_path)
    except ImportError:
        pass  # Continue without dotenv if not available
    
    print("🔧 COMPONENT CONFIGURATION")
    print("=" * 50)
    
    # Get components configuration
    components_config = COMPONENT_CONFIG.get("components", {})
    global_author_id = COMPONENT_CONFIG.get("author_id")
    
    enabled_count = sum(1 for config in components_config.values() if config["enabled"])
    disabled_count = len(components_config) - enabled_count
    
    print(f"Total Components: {len(components_config)} ({enabled_count} enabled, {disabled_count} disabled)")
    
    # Show global author assignment
    if global_author_id:
        global_author = get_author_by_id(global_author_id)
        author_name = global_author['name'] if global_author else f"Author {global_author_id}"
        author_country = global_author['country'] if global_author else "Unknown"
        print(f"Global Author: {author_name} ({author_country}) - ID {global_author_id}")
    else:
        print("Global Author: None assigned")
    print()
    
    # Group by API provider
    provider_groups = {}
    for component, config in components_config.items():
        if config["enabled"]:
            provider = config["api_provider"]
            if provider not in provider_groups:
                provider_groups[provider] = []
            provider_groups[provider].append(component)
    
    # Display by provider
    for provider, components in provider_groups.items():
        provider_name = API_PROVIDERS.get(provider, {}).get("name", provider)
        print(f"🌐 {provider_name} ({len(components)} components):")
        for component in sorted(components):
            print(f"   ✅ {component}")
        print()
    
    # Display disabled components
    disabled = [comp for comp, config in components_config.items() if not config["enabled"]]
    if disabled:
        print(f"❌ Disabled Components ({len(disabled)}):")
        for component in sorted(disabled):
            print(f"   ⭕ {component}")
        print()
    
    # Display API provider details
    print("🔑 API Provider Configuration:")
    for provider_id, provider_info in API_PROVIDERS.items():
        env_key = provider_info["env_key"]
        has_key = "✅" if os.getenv(env_key) else "❌"
        print(f"   {has_key} {provider_info['name']}: {provider_info['model']} (env: {env_key})")
    
    print()

def check_environment():
    """Check environment variables and API key configuration."""
    
    print("🔍 ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 50)
    
    try:
        from api.env_loader import EnvLoader
        from pathlib import Path
        
        # Check for .env file
        env_file = Path('.env')
        env_example = Path('.env.example')
        
        print("📁 Environment Files:")
        if env_file.exists():
            print(f"   ✅ .env file found: {env_file.absolute()}")
        else:
            print(f"   ❌ .env file not found")
            if env_example.exists():
                print(f"   💡 Example available: {env_example.absolute()}")
                print(f"      Copy {env_example.name} to .env and add your API keys")
        
        print()
        
        # Load environment and check API keys
        print("🔑 API Key Status:")
        available_keys = EnvLoader.list_available_keys()
        
        provider_keys_found = 0
        for provider_id, provider_info in API_PROVIDERS.items():
            env_key = provider_info["env_key"]
            has_key = bool(EnvLoader.get_api_key(provider_info['name'], env_key))
            status = "✅ Available" if has_key else "❌ Missing"
            print(f"   {status}: {provider_info['name']} ({env_key})")
            if has_key:
                provider_keys_found += 1
        
        print()
        
        # Test API client creation
        print("🧪 API Client Tests:")
        for provider_id, provider_info in API_PROVIDERS.items():
            try:
                client = create_api_client(provider_id, use_mock=False)
                print(f"   ✅ {provider_info['name']}: Client created successfully")
            except Exception as e:
                print(f"   ❌ {provider_info['name']}: {str(e)}")
        
        print()
        
        # Summary and recommendations
        print("📋 Summary:")
        print(f"   API Keys Found: {provider_keys_found}/{len(API_PROVIDERS)}")
        
        if provider_keys_found == 0:
            print("   ⚠️  No API keys found - system will not work")
            print("   💡 Create .env file and add your API keys")
        elif provider_keys_found < len(API_PROVIDERS):
            print("   ⚠️  Some API keys missing - limited functionality")
            print("   💡 Add missing API keys for full provider support")
        else:
            print("   ✅ All API keys configured - system ready")
        
        if not env_file.exists() and env_example.exists():
            print(f"\n💡 Quick setup:")
            print(f"   cp {env_example.name} .env")
            print(f"   # Edit .env and add your API keys")
        
    except Exception as e:
        print(f"❌ Environment check failed: {e}")

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

def create_arg_parser():
    """Create and return the argument parser for the Z-Beam system."""
    parser = argparse.ArgumentParser(
        description="Z-Beam Dynamic Content Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 run.py                                    # Interactive generation mode (default)
  python3 run.py --material "Copper"                # Generate all components for Copper
  python3 run.py --material "Steel" --components "frontmatter,content"  # Specific components
  python3 run.py --material "Aluminum" --author 2   # Generate with Italian writing style (Author 2)
  python3 run.py --list-materials                   # List all available materials
  python3 run.py --list-components                  # List all available components
  python3 run.py --list-authors                     # List all available authors
  python3 run.py --show-config                     # Show component configuration and API providers
  python3 run.py --yaml                            # Validate and fix YAML errors
  python3 run.py --test-api                        # Test API connection
  python3 run.py --interactive                     # Force interactive mode (default when no material specified)
        """
    )
    
    # Main operation modes
    parser.add_argument("--material", help="Generate content for specific material")
    parser.add_argument("--components", help="Comma-separated list of components to generate")
    parser.add_argument("--author", type=int, help="Author ID (1-4) for country-specific writing style")
    parser.add_argument("--interactive", action="store_true", help="Force interactive mode (default when no material specified)")
    parser.add_argument("--yaml", action="store_true", help="Validate and fix YAML errors")
    parser.add_argument("--test-api", action="store_true", help="Test API connection")
    parser.add_argument("--check-env", action="store_true", help="Check environment variables and API key configuration")
    
    # Listing operations
    parser.add_argument("--list-materials", action="store_true", help="List all available materials")
    parser.add_argument("--list-components", action="store_true", help="List all available components")
    parser.add_argument("--list-authors", action="store_true", help="List all available authors")
    parser.add_argument("--show-config", action="store_true", help="Show component configuration and API provider settings")
    parser.add_argument("--help-components", action="store_true", help="Show detailed help for components")
    
    # Validation operations  
    parser.add_argument("--validate", help="Validate YAML files in specified directory")
    
    # General options
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
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
            
        elif args.list_materials or args.list_components or args.list_authors or args.show_config or args.check_env:
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
                components_list = [c.strip() for c in args.components.split(',')]
            
            success = run_dynamic_generation(
                material=args.material,
                components=components_list,
                interactive=args.interactive or not (args.material or args.test_api),
                test_api=args.test_api,
                author_id=args.author
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
