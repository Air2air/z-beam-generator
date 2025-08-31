#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface

A comprehensive AI-powered content generation system for laser cleaning materials.

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

Features:
- Schema-driven content generation with JSON validation
- Multi-component orchestration (frontmatter, content, tags, etc.)
- Interactive and batch processing modes
- Multi-API provider support (DeepSeek, Grok)
- Component validation and autonomous fixing
- Progress tracking and resumption capabilities
- Clean slug generation for consistent file paths
"""

import sys
import os
import logging
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Import slug utilities for consistent naming
try:
    from utils.slug_utils import create_material_slug, create_filename_slug
except ImportError:
    # Fallback to basic slug generation if utils not available
    def create_material_slug(name: str) -> str:
        return name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')
    def create_filename_slug(name: str, suffix: str = "laser-cleaning") -> str:
        slug = create_material_slug(name)
        return f"{slug}-{suffix}" if suffix else slug

COMPONENT_CONFIG = {
    # Global author assignment for all components
    "author_id": 2,  # 1=Taiwan, 2=Italy, 3=Indonesia, 4=USA
    
    # Component orchestration order (components will be generated in this order)
    "orchestration_order": [
        "frontmatter",      # MUST BE FIRST - provides data for all other components
        "propertiestable",  # Depends on frontmatter data
        "badgesymbol",      # Depends on frontmatter data  
        "author",           # Static component, no dependencies
        "content",          # Main content generation
        "bullets",          # Content-related components
        "caption",          # Content-related components
        "table",            # Data presentation
        "tags",             # Metadata components
        "metatags",         # Metadata components
        "jsonld",           # Structured data (should be last)
    ],
    
    # Component-specific configuration
    "components": {
        "author": {"enabled": True, "api_provider": "none"},  # Static component, no API needed
        "bullets": {"enabled": True, "api_provider": "deepseek"},
        "caption": {"enabled": True, "api_provider": "deepseek"},
        "frontmatter": {
            "enabled": True,
            "api_provider": "grok",  # Options: "deepseek", "grok"
        },
        "content": {"enabled": True, "api_provider": "none"},  # Uses optimized Python calculator
        "jsonld": {"enabled": True, "api_provider": "deepseek"},
        "table": {"enabled": True, "api_provider": "grok"},
        "metatags": {"enabled": True, "api_provider": "deepseek"},
        "tags": {"enabled": True, "api_provider": "deepseek"},
        "propertiestable": {"enabled": True, "api_provider": "none"},  # Static component, extracts from frontmatter
        "badgesymbol": {"enabled": True, "api_provider": "none"},  # Static component, extracts from frontmatter
    },
}

# API Provider Configuration
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "env_key": "DEEPSEEK_API_KEY",
        "env_var": "DEEPSEEK_API_KEY",  # Add this for test compatibility
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "grok": {
        "name": "Grok (X.AI)",
        "env_key": "GROK_API_KEY",
        "env_var": "GROK_API_KEY",  # Add this for test compatibility
        "base_url": "https://api.x.ai",  # Remove /v1 since APIClient adds it
        "model": "grok-2",  # grok-2 works reliably; grok-4 currently uses reasoning tokens without completion output
    },
}

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_api_client(provider: str, use_mock: bool = False):
    """Create an API client for the specified provider."""

    # Handle special case for components that don't need API clients
    if provider == "none":
        return None

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
        if "api_key" not in config:
            raise ValueError(
                f"API key not found for {provider}. Please set {provider_config['env_key']} in your environment."
            )

        # Create API client with provider-specific configuration
        return APIClient(
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=config["model"],
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
    authors_file = Path("components/author/authors.json")
    try:
        with open(authors_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("authors", [])
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
        if author.get("id") == author_id:
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
        author_id = author.get("id", "N/A")
        name = author.get("name", "Unknown")
        country = author.get("country", "Unknown")
        print(f"   {author_id}. {name} ({country})")


def run_dynamic_generation(
    material: str = None,
    components: list = None,
    interactive: bool = False,
    test_api: bool = False,
    author_id: int = None,
    start_index: int = 1,
):
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

    # Batch mode - generate all materials if no specific material requested
    if material is None:
        return run_batch_generation(generator, author_info, components, start_index)

    # Generate for specific material
    return run_material_generation(generator, material, components, author_info)


def run_batch_generation(
    generator, author_info: dict = None, components: list = None, start_index: int = 1
):
    """Run batch generation for all available materials without user interaction."""

    print("🏭 Batch Generation Mode")
    print("Generating content for all available materials...")
    print("=" * 50)

    materials = generator.get_available_materials()
    available_components = generator.get_available_components()

    # Use specified components or all available components
    target_components = components if components else available_components

    # Calculate starting point
    total_materials = len(materials)
    start_idx = (
        max(1, min(start_index, total_materials)) - 1
    )  # Convert to 0-based index

    print(
        f"📊 Target: {len(materials)} materials × {len(target_components)} components"
    )
    print(f"🔧 Components: {', '.join(target_components)}")
    if start_index > 1:
        print(f"🚀 Starting at material #{start_index}: {materials[start_idx]}")
        print(f"📋 Skipping first {start_idx} materials")
    if author_info:
        print(f"👤 Author: {author_info['name']} ({author_info['country']})")
    print()

    generated_count = 0
    failed_count = 0

    try:
        for i, material in enumerate(materials[start_idx:], start_index):
            print(f"\n📦 [{i}/{total_materials}] Processing: {material}")

            # Generate content for this material
            success = run_material_generation(
                generator, material, target_components, author_info
            )

            if success:
                generated_count += 1
                print(f"   ✅ {material} completed successfully")
            else:
                failed_count += 1
                print(f"   ❌ {material} failed to generate")

            # Show progress
            progress_percent = (i / total_materials) * 100
            print(f"   📈 Progress: {i}/{total_materials} ({progress_percent:.1f}%)")

    except KeyboardInterrupt:
        print("\n\n🛑 Batch generation interrupted by user")

    print("\n📊 Batch Generation Summary:")
    print("=" * 50)
    print(f"   ✅ Successfully generated: {generated_count} materials")
    print(f"   ❌ Failed: {failed_count} materials")
    print(f"   📈 Success rate: {(generated_count/total_materials)*100:.1f}%")
    print(f"   🎯 Total processed: {generated_count + failed_count}/{total_materials}")

    if generated_count == total_materials:
        print("\n🎉 All materials generated successfully!")
        print("💡 Content generation complete. Ready for deployment.")
    elif generated_count > 0:
        print(
            f"\n✅ Batch generation completed with {generated_count} successful generations."
        )
        if failed_count > 0:
            print(f"⚠️  {failed_count} materials failed - check logs for details.")
    else:
        print("\n❌ No materials were successfully generated.")
        print("🔧 Check system configuration and API connectivity.")

    return generated_count > 0


def run_interactive_generation(generator, author_info: dict = None):
    """Run interactive generation with user prompts."""

    print("🎮 Interactive Generation Mode")
    print("Commands: Y/Yes (continue), S/Skip (skip material), Q/Quit (exit)")
    print("=" * 50)

    materials = generator.get_available_materials()
    available_components = generator.get_available_components()

    print(
        f"📊 Loaded {len(materials)} materials and {len(available_components)} components"
    )
    print(f"🔧 Components: {', '.join(available_components)}")
    print()

    generated_count = 0
    skipped_count = 0

    try:
        for i, material in enumerate(materials, 1):
            print(f"\n📦 [{i}/{len(materials)}] Processing: {material}")

            # Ask user which components to generate
            print(f"Available components: {', '.join(available_components)}")
            response = (
                input(
                    f"Generate components for {material}? (Y/s/q/all/list components): "
                )
                .strip()
                .lower()
            )

            if response in ["q", "quit"]:
                break
            elif response in ["s", "skip"]:
                print(f"⏭️  Skipped {material}")
                skipped_count += 1
                continue
            elif response in ["list", "l"]:
                print("Available components:")
                for j, comp in enumerate(available_components, 1):
                    print(f"   {j}. {comp}")
                continue
            elif response == "all":
                selected_components = available_components
            elif response in ["", "y", "yes"]:
                # Generate all components by default
                selected_components = available_components
            else:
                # Parse specific components
                selected_components = [
                    c.strip() for c in response.split(",") if c.strip()
                ]
                # Validate components
                invalid = [
                    c for c in selected_components if c not in available_components
                ]
                if invalid:
                    print(f"❌ Invalid components: {', '.join(invalid)}")
                    continue

            # Generate content
            success = run_material_generation(
                generator, material, selected_components, author_info
            )
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
        with open(filepath, "w", encoding="utf-8") as f:
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

    # Create filename using clean slug generation
    filename = create_filename_slug(material) + ".md"
    filepath = output_dir / filename

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"Saved {component_type} to {filepath}")
    except Exception as e:
        logging.error(f"Error saving {component_type}: {e}")


def run_material_generation(
    generator, material: str, components: list = None, author_info: dict = None
):
    """Generate content for a specific material with component configuration."""

    if components is None:
        components = generator.get_available_components()

    # Get the components configuration
    components_config = COMPONENT_CONFIG.get("components", {})
    orchestration_order = COMPONENT_CONFIG.get("orchestration_order", [])

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

    # Order enabled components according to orchestration_order
    ordered_components = []
    
    # First, add components in the defined orchestration order
    for component in orchestration_order:
        if component in enabled_components:
            ordered_components.append(component)
    
    # Then add any remaining enabled components that aren't in the orchestration order
    for component in enabled_components:
        if component not in ordered_components:
            ordered_components.append(component)
    
    # Use the ordered components list
    enabled_components = ordered_components

    # Display component status
    print(f"🔧 Component Generation Plan for {material}:")
    print(f"   ✅ Enabled ({len(enabled_components)}): {', '.join(enabled_components)}")
    if disabled_components:
        print(
            f"   ❌ Disabled ({len(disabled_components)}): {', '.join(disabled_components)}"
        )

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
            provider = components_config.get(component_type, {}).get(
                "api_provider", "deepseek"
            )
            
            # Handle special provider names
            if provider == "none":
                provider_name = "Static Component"
            else:
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
                print(
                    f"   👤 Author: {component_author_info['name']} ({component_author_info['country']})"
                )

            # Create a temporary generator with this API client
            from generators.dynamic_generator import DynamicGenerator

            # For static components (api_client is None), we need to prevent fallback to DeepSeek
            if api_client is None:
                temp_generator = DynamicGenerator(api_client=None, use_mock=True)
            else:
                temp_generator = DynamicGenerator(api_client=api_client)

            # Set author info for ALL components
            if component_author_info:
                temp_generator.set_author(component_author_info)

            # Generate this single component
            result = temp_generator.generate_component(material, component_type)

            if result.success:
                # Save the component using our own save logic
                save_component_to_file_original(
                    material, component_type, result.content
                )
                successful_count += 1
                results[component_type] = result
                print(
                    f"   ✅ {component_type} ({provider_name}) - {len(result.content)} chars generated"
                )
            else:
                results[component_type] = result
                print(
                    f"   ❌ {component_type} ({provider_name}): {result.error_message}"
                )

        except Exception as e:
            print(f"   ❌ {component_type}: Error creating API client - {str(e)}")
            # Create a fake failed result
            from generators.dynamic_generator import ComponentResult

            results[component_type] = ComponentResult(
                component_type=component_type,
                content="",
                success=False,
                error_message=str(e),
            )

    # Report final results
    print(f"\n📋 Generation Results for {material}:")
    print(f"   Success: {successful_count > 0}")
    print(f"   Components: {successful_count}/{len(enabled_components)}")

    for component_type, result in results.items():
        provider = components_config.get(component_type, {}).get(
            "api_provider", "default"
        )
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

        env_path = Path(__file__).parent / ".env"
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

    print(
        f"Total Components: {len(components_config)} ({enabled_count} enabled, {disabled_count} disabled)"
    )

    # Show global author assignment
    if global_author_id:
        global_author = get_author_by_id(global_author_id)
        author_name = (
            global_author["name"] if global_author else f"Author {global_author_id}"
        )
        author_country = global_author["country"] if global_author else "Unknown"
        print(
            f"Global Author: {author_name} ({author_country}) - ID {global_author_id}"
        )
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
    disabled = [
        comp for comp, config in components_config.items() if not config["enabled"]
    ]
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
        print(
            f"   {has_key} {provider_info['name']}: {provider_info['model']} (env: {env_key})"
        )

    print()


def check_environment():
    """Check environment variables and API key configuration."""

    print("🔍 ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 50)

    try:
        from api.env_loader import EnvLoader
        from pathlib import Path

        # Check for .env file
        env_file = Path(".env")
        env_example = Path(".env.example")

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
            has_key = bool(EnvLoader.get_api_key(provider_info["name"], env_key))
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
                    component_type = (
                        md_file.parent.name
                        if md_file.parent.name != "content"
                        else "content"
                    )

                    was_processed = validator.post_process_generated_content(
                        str(md_file), component_type
                    )

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

        # Process component example files
        print("\n📁 Processing component example files...")
        components_dir = Path("components")
        if components_dir.exists():
            for component_dir in components_dir.iterdir():
                if component_dir.is_dir():
                    example_files = list(component_dir.glob("example_*.md"))
                    for md_file in example_files:
                        total_files += 1

                        try:
                            # Component type is the parent directory name
                            component_type = component_dir.name

                            was_processed = validator.post_process_generated_content(
                                str(md_file), component_type
                            )

                            if was_processed:
                                fixed_files += 1
                                print(f"   ✅ Fixed: {md_file.relative_to(Path('.'))}")
                            else:
                                print(f"   ⚪ OK: {md_file.relative_to(Path('.'))}")

                        except Exception as e:
                            error_files.append(f"{md_file.relative_to(Path('.'))}: {str(e)}")
                            print(f"   ❌ Error: {md_file.relative_to(Path('.'))} - {e}")
        else:
            print("   ⚠️  Components directory not found")

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


def clean_content_components():
    """Clean all generated content files from content/components subfolders."""

    print("🗂️  CONTENT COMPONENTS CLEANUP")
    print("=" * 50)
    print("Removing all generated content files from component subfolders...")
    print("=" * 50)

    try:
        content_components_dir = Path("content/components")

        if not content_components_dir.exists():
            print("❌ Content/components directory not found!")
            return False

        # Get all component subdirectories
        component_dirs = [d for d in content_components_dir.iterdir() if d.is_dir()]

        if not component_dirs:
            print("📁 No component subdirectories found.")
            return True

        total_files_removed = 0
        total_dirs_processed = 0

        for component_dir in sorted(component_dirs):
            component_name = component_dir.name
            print(f"\n📂 Processing {component_name}/")

            # Find all markdown files in this component directory
            md_files = list(component_dir.glob("*.md"))

            if not md_files:
                print(f"   📄 No files to remove")
                continue

            files_removed = 0
            for md_file in md_files:
                try:
                    md_file.unlink()  # Delete the file
                    print(f"   🗑️  Removed: {md_file.name}")
                    files_removed += 1
                except Exception as e:
                    print(f"   ❌ Error removing {md_file.name}: {e}")

            total_files_removed += files_removed
            total_dirs_processed += 1
            print(f"   ✅ {files_removed} files removed from {component_name}/")

        # Summary
        print("\n📊 CLEANUP COMPLETE")
        print("=" * 50)
        print(f"📁 Directories processed: {total_dirs_processed}")
        print(f"🗑️  Total files removed: {total_files_removed}")

        if total_files_removed > 0:
            print(
                f"\n✅ Successfully cleaned {total_files_removed} files from {total_dirs_processed} component directories!"
            )
            print(
                "💡 Content/components directories are now ready for fresh generation."
            )
        else:
            print("\n📝 No files found to remove. Directories are already clean.")

        return True

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False


def run_cleanup_scan():
    """Run comprehensive cleanup scan (dry-run only)."""
    print("🧹 Z-BEAM CLEANUP SCAN")
    print("=" * 50)
    print("Scanning for cleanup opportunities (dry-run mode)...")
    print("=" * 50)
    
    try:
        # Import standalone cleanup manager (decoupled from tests)
        from cleanup.cleanup_manager import CleanupManager
        
        # Initialize cleanup manager in safe dry-run mode
        cleanup_manager = CleanupManager(Path.cwd(), dry_run=True)
        
        # Run comprehensive cleanup scan
        results = cleanup_manager.scan()
        
        # Display results
        print("\n📊 CLEANUP SCAN RESULTS")
        print("=" * 50)
        
        total_issues = results['total_issues']
        for category, items in results['categories'].items():
            count = len(items) if isinstance(items, list) else 0
            
            category_name = category.replace('_', ' ').title()
            print(f"📋 {category_name}: {count} items")
            
            if count > 0 and count <= 5:  # Show details for small lists
                for item_path, reason in items[:5]:
                    print(f"   • {item_path} - {reason}")
            elif count > 5:
                for item_path, reason in items[:3]:
                    print(f"   • {item_path} - {reason}")
                print(f"   ... and {count - 3} more items")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total cleanup opportunities: {total_issues}")
        
        if total_issues == 0:
            print("   ✅ No cleanup needed - project is clean!")
        elif total_issues <= 10:
            print("   🟡 Minor cleanup opportunities found")
        else:
            print("   🔴 Significant cleanup opportunities found")
        
        print(f"\n💡 NEXT STEPS:")
        if total_issues > 0:
            print("   • Review the items listed above")
            print("   • Run --cleanup-report for detailed analysis")
            print("   • Use --clean to remove generated content files")
        else:
            print("   • Project is clean, no action needed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing cleanup system: {e}")
        print("   Make sure tests/test_cleanup.py is available")
        return False
    except Exception as e:
        print(f"❌ Error during cleanup scan: {e}")
        return False


def run_cleanup_report():
    """Generate comprehensive cleanup report."""
    print("📋 Z-BEAM CLEANUP REPORT GENERATION")
    print("=" * 50)
    print("Generating comprehensive cleanup report...")
    print("=" * 50)
    
    try:
        # Import standalone cleanup manager (decoupled from tests)
        from cleanup.cleanup_manager import CleanupManager
        
        # Initialize cleanup manager in safe dry-run mode
        cleanup_manager = CleanupManager(Path.cwd(), dry_run=True)
        
        # Run comprehensive cleanup scan
        report_path = cleanup_manager.generate_report()
        results = cleanup_manager.scan()
        
        # Display summary
        print("\n📊 CLEANUP REPORT SUMMARY")
        print("=" * 50)
        
        for category, items in results['categories'].items():
            count = len(items) if isinstance(items, list) else 0
            category_name = category.replace('_', ' ').title()
            print(f"📋 {category_name}: {count} items")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total cleanup opportunities: {results['total_issues']}")
        print(f"   Report timestamp: {results['timestamp']}")
        print(f"   Dry-run mode: True")
        
        print(f"\n💾 REPORT SAVED:")
        print(f"   File: {report_path}")
        print(f"   Size: {Path(report_path).stat().st_size} bytes")
        
        print(f"\n💡 USAGE:")
        print("   • Review cleanup/cleanup_report.json for detailed analysis")
        print("   • Use --cleanup-scan for quick overview")
        print("   • Use --clean to remove generated content files")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing cleanup system: {e}")
        print("   Make sure tests/test_cleanup.py is available")
        return False
    except Exception as e:
        print(f"❌ Error generating cleanup report: {e}")
        return False


def run_root_cleanup():
    """Clean up root directory by organizing files into appropriate subdirectories."""
    print("🧹 ROOT DIRECTORY CLEANUP")
    print("=" * 50)
    print("Organizing root directory files into appropriate subdirectories...")
    print("=" * 50)
    
    try:
        root_dir = Path(".")
        
        # Define cleanup rules - where to move different file types
        cleanup_rules = {
            # Documentation files - already mostly moved to docs/
            "docs": {
                "patterns": ["*.md"],
                "exclude": ["README.md"],  # Keep README.md in root
                "description": "Documentation files"
            },
            
            # Test and debug files  
            "tests": {
                "patterns": ["test_*.py", "debug_*.py", "*_test.py", "test.py", "*verification*.py"],
                "exclude": [],
                "description": "Test and debug files"
            },
            
            # Utility and shell scripts
            "scripts": {
                "patterns": [
                    "*_material.py", "update_*.py", "*_labels.py", "*enhancement*.py", 
                    "*.sh"
                ],
                "exclude": ["run.py", "z_beam_generator.py"],  # Keep main scripts in root
                "description": "Utility, maintenance and shell scripts"
            },
            
            # Cleanup utilities
            "cleanup": {
                "patterns": ["cleanup_*.py", "*cleanup*.py"],
                "exclude": [],
                "description": "Cleanup utility scripts"
            },
            
            # Temporary and generated files to delete
            "delete": {
                "patterns": [
                    "*.pyc", "*.pyo", "__pycache__", ".pytest_cache",
                    "*.tmp", "*.temp", "*~", ".DS_Store",
                    "cleanup_report.json"  # Will be regenerated in cleanup/ folder
                ],
                "exclude": [],
                "description": "Temporary and cache files"
            }
        }
        
        moved_files = {}
        deleted_files = []
        skipped_files = []
        
        # Process each cleanup rule
        for target_dir, rule in cleanup_rules.items():
            moved_files[target_dir] = []
            
            if target_dir == "delete":
                # Special handling for deletion
                for pattern in rule["patterns"]:
                    for file_path in root_dir.glob(pattern):
                        if file_path.is_file() and file_path.name not in rule["exclude"]:
                            try:
                                file_path.unlink()
                                deleted_files.append(file_path.name)
                                print(f"   🗑️  Deleted: {file_path.name}")
                            except Exception as e:
                                print(f"   ❌ Error deleting {file_path.name}: {e}")
                        elif file_path.is_dir() and file_path.name not in rule["exclude"]:
                            try:
                                import shutil
                                shutil.rmtree(file_path)
                                deleted_files.append(f"{file_path.name}/")
                                print(f"   🗑️  Deleted directory: {file_path.name}/")
                            except Exception as e:
                                print(f"   ❌ Error deleting directory {file_path.name}: {e}")
                continue
            
            # Create target directory if it doesn't exist
            target_path = Path(target_dir)
            if not target_path.exists():
                target_path.mkdir(parents=True, exist_ok=True)
                print(f"   📁 Created directory: {target_dir}/")
            
            # Find and move files matching patterns
            for pattern in rule["patterns"]:
                for file_path in root_dir.glob(pattern):
                    # Skip if it's a directory or in exclude list
                    if not file_path.is_file() or file_path.name in rule["exclude"]:
                        if file_path.name in rule["exclude"]:
                            skipped_files.append(f"{file_path.name} (excluded)")
                        continue
                    
                    # Skip if file is already in target directory
                    if file_path.parent.name == target_dir:
                        continue
                    
                    # Move file to target directory
                    dest_path = target_path / file_path.name
                    
                    # Handle name conflicts
                    counter = 1
                    original_dest = dest_path
                    while dest_path.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_path = target_path / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    try:
                        file_path.rename(dest_path)
                        moved_files[target_dir].append(f"{file_path.name} → {dest_path.name}")
                        print(f"   📦 Moved: {file_path.name} → {target_dir}/{dest_path.name}")
                    except Exception as e:
                        print(f"   ❌ Error moving {file_path.name}: {e}")
        
        # Display summary
        print("\n📊 ROOT CLEANUP SUMMARY")
        print("=" * 50)
        
        total_actions = sum(len(files) for files in moved_files.values()) + len(deleted_files)
        
        for target_dir, files in moved_files.items():
            if files:
                rule_desc = cleanup_rules[target_dir]["description"]
                print(f"📁 {target_dir}/ ({rule_desc}): {len(files)} files")
                for file_move in files[:3]:  # Show first 3
                    print(f"   • {file_move}")
                if len(files) > 3:
                    print(f"   ... and {len(files) - 3} more files")
        
        if deleted_files:
            print(f"🗑️  Deleted: {len(deleted_files)} items")
            for item in deleted_files[:5]:  # Show first 5
                print(f"   • {item}")
            if len(deleted_files) > 5:
                print(f"   ... and {len(deleted_files) - 5} more items")
        
        if skipped_files:
            print(f"⏭️  Skipped: {len(skipped_files)} files")
            for item in skipped_files[:3]:  # Show first 3
                print(f"   • {item}")
            if len(skipped_files) > 3:
                print(f"   ... and {len(skipped_files) - 3} more files")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total actions performed: {total_actions}")
        
        if total_actions == 0:
            print("   ✅ Root directory is already clean!")
        elif total_actions <= 5:
            print("   ✅ Minor cleanup completed")
        else:
            print("   ✅ Major cleanup completed - root directory organized!")
        
        print("\n💡 NEXT STEPS:")
        print("   • Review organized files in their new locations")
        print("   • Update any import paths if needed")  
        print("   • Use --cleanup-scan to verify no issues remain")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during root cleanup: {e}")
        return False


def create_arg_parser():
    """Create and return the argument parser for the Z-Beam system."""
    parser = argparse.ArgumentParser(
        description="Z-Beam Dynamic Content Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 run.py                                    # Generate all available materials (batch mode)
  python3 run.py --start-index 50                   # Start batch generation from material #50
  python3 run.py --material "Copper"                # Generate all components for Copper
  python3 run.py --material "Steel" --components "frontmatter,content"  # Specific components
  python3 run.py --material "Aluminum" --author 2   # Generate with Italian writing style (Author 2)
  python3 run.py --interactive                      # Interactive mode with user prompts
  python3 run.py --list-materials                   # List all available materials
  python3 run.py --list-components                  # List all available components
  python3 run.py --list-authors                     # List all available authors
  python3 run.py --show-config                     # Show component configuration and API providers
  python3 run.py --yaml                            # Validate and fix YAML errors
  python3 run.py --clean                           # Remove all generated content files
  python3 run.py --cleanup-root                    # Organize root directory files
  python3 run.py --test-api                        # Test API connection
        """,
    )

    # Main operation modes
    parser.add_argument("--material", help="Generate content for specific material")
    parser.add_argument(
        "--components", help="Comma-separated list of components to generate"
    )
    parser.add_argument(
        "--author", type=int, help="Author ID (1-4) for country-specific writing style"
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=1,
        help="Start batch generation at specific material index (1-based)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode with user prompts for each material",
    )
    parser.add_argument(
        "--yaml", action="store_true", help="Validate and fix YAML errors"
    )
    parser.add_argument("--test-api", action="store_true", help="Test API connection")
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check environment variables and API key configuration",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove all generated content files from content/components subfolders",
    )
    parser.add_argument(
        "--cleanup-scan",
        action="store_true",
        help="Scan for dead files, unused files, and other cleanup opportunities (dry-run)",
    )
    parser.add_argument(
        "--cleanup-report",
        action="store_true",
        help="Generate comprehensive cleanup report and save to cleanup/cleanup_report.json",
    )
    parser.add_argument(
        "--cleanup-root",
        action="store_true",
        help="Clean up root directory by organizing files into appropriate subdirectories",
    )

    # Listing operations
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
    parser.add_argument(
        "--help-components",
        action="store_true",
        help="Show detailed help for components",
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

        elif args.clean:
            # Content cleanup mode
            success = clean_content_components()

        elif args.cleanup_scan:
            # Cleanup scan mode (dry-run)
            success = run_cleanup_scan()

        elif args.cleanup_report:
            # Cleanup report generation
            success = run_cleanup_report()

        elif args.cleanup_root:
            # Root directory cleanup
            success = run_root_cleanup()

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
