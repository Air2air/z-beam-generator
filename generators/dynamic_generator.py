#!/usr/bin/env python3
"""
Dynamic Schema-Driven Generator for Z-Beam

This module provides dynamic content generation based on JSON schemas,
allowing for flexible field-driven content creation with component selection.
"""

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from api.client_manager import get_api_client_for_component
from generators.component_generators import ComponentGeneratorFactory, ComponentResult
from utils.config.config_utils import load_materials_data


@dataclass
class GenerationRequest:
    """Request for generating multiple components for a material"""

    material: str
    components: List[str]
    output_dir: str


@dataclass
class GenerationResult:
    """Result of generating multiple components"""

    material: str
    success: bool
    total_components: int
    successful_components: int
    results: Dict[str, Any]


class DynamicGenerator:
    """Dynamic generator for Z-Beam content components"""

    def __init__(self):
        """Initialize the dynamic generator"""
        self.api_client = None
        self.materials_data = load_materials_data()

    def get_available_materials(self) -> List[str]:
        """Get list of available materials"""
        if not self.materials_data or "materials" not in self.materials_data:
            return []

        materials = []
        materials_section = self.materials_data["materials"]
        for category, category_data in materials_section.items():
            if isinstance(category_data, dict) and "items" in category_data:
                for item in category_data["items"]:
                    if "name" in item:
                        materials.append(item["name"])
        return sorted(materials)

    def get_available_components(self) -> List[str]:
        """Get list of available components sorted by priority"""
        try:
            from cli.component_config import get_components_sorted_by_priority
            return get_components_sorted_by_priority()
        except ImportError:
            # Fallback to directory listing if config not available
            components_dir = Path("components")
            if not components_dir.exists():
                return []

            components = []
            for item in components_dir.iterdir():
                if item.is_dir() and not item.name.startswith("__"):
                    components.append(item.name)
            return sorted(components)

    def generate_multiple(self, request: GenerationRequest, frontmatter_data: Optional[Dict] = None) -> GenerationResult:
        """Generate multiple components for a material"""
        results = {}
        successful = 0

        # Get material data once for all components
        materials_data = self.materials_data
        material_data = None
        if materials_data and "materials" in materials_data:
            materials_section = materials_data["materials"]
            for category, category_data in materials_section.items():
                if isinstance(category_data, dict) and "items" in category_data:
                    for item in category_data["items"]:
                        if item["name"].lower() == request.material.lower():
                            material_data = item
                            break
                    if material_data:
                        break

        if not material_data:
            return GenerationResult(
                material=request.material,
                success=False,
                total_components=len(request.components),
                successful_components=0,
                results={comp: {"success": False, "content": "", "error_message": f"Material '{request.material}' not found"} for comp in request.components}
            )

        for component_type in request.components:
            try:
                # Get API client for this component
                api_client = get_api_client_for_component(component_type)

                # Generate component
                factory = ComponentGeneratorFactory()
                generator = factory.create_generator(component_type)

                if not generator:
                    results[component_type] = {
                        "success": False,
                        "content": "",
                        "error_message": f"No generator available for component type '{component_type}'",
                    }
                    continue

                # Generate component with proper parameters
                result = generator.generate(
                    material_name=request.material,
                    material_data=material_data,
                    api_client=api_client,
                    frontmatter_data=frontmatter_data,
                )

                results[component_type] = {
                    "success": result.success,
                    "content": result.content,
                    "error_message": result.error_message,
                }

                if result.success:
                    successful += 1

            except Exception as e:
                results[component_type] = {
                    "success": False,
                    "content": "",
                    "error_message": str(e),
                }

        return GenerationResult(
            material=request.material,
            success=successful == len(request.components),
            total_components=len(request.components),
            successful_components=successful,
            results=results,
        )

    def generate_component(
        self,
        material: str,
        component_type: str,
        api_client,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate a single component for a material"""
        try:
            # Get material data
            materials_data = self.materials_data
            if not materials_data:
                return ComponentResult(
                    component_type=component_type,
                    content="",
                    success=False,
                    error_message="No materials data available",
                )

            # Find material data - materials.yaml has materials -> category -> items structure
            material_data = None
            if "materials" in materials_data:
                materials_section = materials_data["materials"]
                for category, category_data in materials_section.items():
                    if isinstance(category_data, dict) and "items" in category_data:
                        for item in category_data["items"]:
                            if item["name"].lower() == material.lower():
                                material_data = item
                                break
                        if material_data:
                            break

            if not material_data:
                return ComponentResult(
                    component_type=component_type,
                    content="",
                    success=False,
                    error_message=f"Material '{material}' not found",
                )

            # Use ComponentGeneratorFactory to create the appropriate generator
            factory = ComponentGeneratorFactory()
            generator = factory.create_generator(component_type)

            if not generator:
                return ComponentResult(
                    component_type=component_type,
                    content="",
                    success=False,
                    error_message=f"No generator available for component type '{component_type}'",
                )

            # Generate the component
            result = generator.generate(
                material_name=material,
                material_data=material_data,
                api_client=api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data,
            )

            # Convert to expected format with token_count
            if hasattr(result, "token_count"):
                return result
            else:
                # If the result doesn't have token_count, add it from API response
                token_count = 0
                if hasattr(api_client, "stats") and "total_tokens" in api_client.stats:
                    token_count = api_client.stats["total_tokens"]

                # Create a new result with token_count
                return ComponentResult(
                    component_type=component_type,
                    content=result.content,
                    success=result.success,
                    error_message=getattr(result, "error_message", None),
                    token_count=token_count,
                )

        except Exception as e:
            return ComponentResult(
                component_type=component_type,
                content="",
                success=False,
                error_message=str(e),
            )


def main():
    """Main entry point for the dynamic generator."""
    parser = argparse.ArgumentParser(
        description="Z-Beam Dynamic Schema Generator with Component Selection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 -m generators.dynamic_generator --material "Copper" --components "frontmatter,text"
  python3 -m generators.dynamic_generator --list-materials
  python3 -m generators.dynamic_generator --list-components
  python3 -m generators.dynamic_generator --material "Steel" --components all
  python3 -m generators.dynamic_generator --material "Aluminum"
        """,
    )

    parser.add_argument("--material", help="Material name to generate content for")
    parser.add_argument(
        "--components", help='Components to generate: comma-separated list or "all"'
    )
    parser.add_argument(
        "--output-dir", default="content", help="Output directory for generated content"
    )
    parser.add_argument(
        "--list-materials", action="store_true", help="List available materials"
    )
    parser.add_argument(
        "--list-components", action="store_true", help="List available components"
    )
    parser.add_argument("--test-api", action="store_true", help="Test API connection")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize generator
    generator = DynamicGenerator()

    # Test API connection if requested
    if args.test_api:
        if hasattr(generator.api_client, "test_connection"):
            if generator.api_client.test_connection():
                print("✅ API connection successful!")
                return
            else:
                print("❌ API connection failed!")
                return
        else:
            print("⚠️  API connection test not available for this client")
            return

    # List operations
    if args.list_materials:
        materials = generator.get_available_materials()
        print(f"📋 Available materials ({len(materials)}):")
        for i, material in enumerate(sorted(materials), 1):
            print(f"   {i:3d}. {material}")
        return

    if args.list_components:
        components = generator.get_available_components()
        print(f"🔧 Available components ({len(components)}):")
        for i, component in enumerate(sorted(components), 1):
            print(f"   {i}. {component}")
        return

    # Require material for generation
    if not args.material:
        print("❌ Material name is required for generation")
        print("   Use --list-materials to see available materials")
        return

    # Parse components list
    if not args.components:
        print("❌ Components list is required")
        print("   Use --list-components to see available components")
        print("   Use --components all to generate all components")
        return

    available_components = generator.get_available_components()

    if args.components.lower() == "all":
        components_list = available_components
    else:
        components_list = [c.strip() for c in args.components.split(",")]

        # Validate components
        invalid_components = [
            c for c in components_list if c not in available_components
        ]
        if invalid_components:
            print(f"❌ Invalid components: {', '.join(invalid_components)}")
            print(f"   Available components: {', '.join(available_components)}")
            return

    # Create generation request
    request = GenerationRequest(
        material=args.material, components=components_list, output_dir=args.output_dir
    )

    # Generate content
    print(f"🚀 Generating {len(components_list)} components for {args.material}...")
    print(f"📁 Output directory: {args.output_dir}")
    print("=" * 50)

    result = generator.generate_multiple(request)

    # Report results
    print(f"\n📊 Generation Results for {result.material}:")
    print(f"   Success: {'✅' if result.success else '❌'}")
    print(f"   Components: {result.successful_components}/{result.total_components}")
    print("=" * 50)

    for component_type, component_result in result.results.items():
        if component_result["success"]:
            print(f"   ✅ {component_type}")
        else:
            from utils.loud_errors import component_failure

            component_failure(
                "dynamic_generator",
                f"Component generation failed: {component_result['error_message']}",
                component_type=component_type,
            )
            print(f"   ❌ {component_type}: {component_result['error_message']}")

    # Show API statistics if available
    if hasattr(generator.api_client, "get_statistics"):
        stats = generator.api_client.get_statistics()
        print("\n📈 API Statistics:")
        print(f"   Requests: {stats.get('total_requests', 0)}")
        print(f"   Success rate: {stats.get('success_rate', 0):.1f}%")
        print(f"   Total tokens: {stats.get('total_tokens', 0)}")
        print(f"   Avg response time: {stats.get('average_response_time', 0):.2f}s")


if __name__ == "__main__":
    main()
