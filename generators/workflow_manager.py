#!/usr/bin/env python3
"""
Workflow Manager

Centralized generation workflow management.
Extracted from run.py to reduce bloat and improve testability.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from api.client_manager import get_api_client_for_component
from generators.dynamic_generator import DynamicGenerator
from utils.author_manager import (
    get_author_info_for_generation,
    get_author_info_for_material,
)
from utils.file_operations import save_component_to_file_original


def run_dynamic_generation(
    generator: DynamicGenerator,
    material: str,
    component_types: List[str],
    author_info: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Run dynamic generation for specific material and components.

    Args:
        generator: DynamicGenerator instance
        material: Material name
        component_types: List of component types to generate
        author_info: Optional author information

    Returns:
        Dictionary with generation results
    """
    results = {
        "material": material,
        "components_generated": [],
        "components_failed": [],
        "total_time": 0,
        "total_tokens": 0,
    }

    start_time = time.time()

    print(f"\n🔧 Generating content for: {material}")
    print(f"📝 Components: {', '.join(component_types)}")

    for component_type in component_types:
        try:
            print(f"\n  🔨 Generating {component_type}...")

            # Get API client for this component
            api_client = get_api_client_for_component(component_type)

            # Generate content
            component_start = time.time()
            result = generator.generate_component(
                material=material,
                component_type=component_type,
                api_client=api_client,
                author_info=author_info,
            )
            component_time = time.time() - component_start

            if result.success:
                # Save to file
                filepath = save_component_to_file_original(
                    material, component_type, result.content
                )

                print(
                    f"    ✅ Generated ({result.token_count} tokens, {component_time:.1f}s)"
                )
                print(f"    💾 Saved to: {filepath}")

                results["components_generated"].append(
                    {
                        "type": component_type,
                        "tokens": result.token_count or 0,
                        "time": component_time,
                        "filepath": filepath,
                    }
                )
                results["total_tokens"] += result.token_count or 0

            else:
                from utils.loud_errors import component_failure

                component_failure(
                    "workflow_manager",
                    f"Component generation failed: {result.error_message}",
                    component_type=component_type,
                )
                print(f"    ❌ Failed: {result.error_message}")
                results["components_failed"].append(
                    {"type": component_type, "error": result.error_message}
                )

        except Exception as e:
            from utils.loud_errors import component_failure

            component_failure(
                "workflow_manager",
                f"Error generating {component_type}: {e}",
                component_type=component_type,
            )
            print(f"    ❌ Error generating {component_type}: {e}")
            results["components_failed"].append(
                {"type": component_type, "error": str(e)}
            )

    results["total_time"] = time.time() - start_time

    # Summary
    success_count = len(results["components_generated"])
    total_count = len(component_types)

    print(f"\n📊 Generation Summary for {material}:")
    print(f"  ✅ Successful: {success_count}/{total_count}")
    if results["components_failed"]:
        print(f"  ❌ Failed: {len(results['components_failed'])}")
    print(f"  🕐 Total time: {results['total_time']:.1f}s")
    print(f"  🎯 Total tokens: {results['total_tokens']}")

    return results


def run_batch_generation(
    materials: List[str],
    component_types: List[str],
    author_id: Optional[int] = None,
    start_index: int = 0,
    max_materials: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run batch generation for multiple materials.

    Args:
        materials: List of material names
        component_types: List of component types to generate
        author_id: Optional author ID
        start_index: Starting index in materials list
        max_materials: Maximum number of materials to process

    Returns:
        Dictionary with batch generation results
    """
    generator = DynamicGenerator()
    author_info = get_author_info_for_generation(author_id)

    # Apply filtering
    if start_index > 0:
        materials = materials[start_index:]
    if max_materials:
        materials = materials[:max_materials]

    batch_results = {
        "materials_processed": [],
        "materials_failed": [],
        "total_components_generated": 0,
        "total_components_failed": 0,
        "total_time": 0,
        "total_tokens": 0,
    }

    start_time = time.time()

    print(f"🚀 Starting batch generation for {len(materials)} materials")
    print(f"📝 Components: {', '.join(component_types)}")
    if author_info.get("name") != "AI Assistant":
        print(f"👤 Author: {author_info['name']} ({author_info['country']})")

    for i, material in enumerate(materials, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(materials)}: {material}")
        print(f"{'='*60}")

        try:
            result = run_dynamic_generation(
                generator=generator,
                material=material,
                component_types=component_types,
                author_info=author_info,
            )

            batch_results["materials_processed"].append(
                {
                    "material": material,
                    "components_generated": len(result["components_generated"]),
                    "components_failed": len(result["components_failed"]),
                    "time": result["total_time"],
                    "tokens": result["total_tokens"],
                }
            )

            batch_results["total_components_generated"] += len(
                result["components_generated"]
            )
            batch_results["total_components_failed"] += len(result["components_failed"])
            batch_results["total_tokens"] += result["total_tokens"]

        except Exception as e:
            print(f"❌ Failed to process {material}: {e}")
            batch_results["materials_failed"].append(
                {"material": material, "error": str(e)}
            )

    batch_results["total_time"] = time.time() - start_time

    # Final summary
    print(f"\n{'='*60}")
    print("🎉 BATCH GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Materials processed: {len(batch_results['materials_processed'])}")
    if batch_results["materials_failed"]:
        print(f"❌ Materials failed: {len(batch_results['materials_failed'])}")
    print(f"🔧 Components generated: {batch_results['total_components_generated']}")
    if batch_results["total_components_failed"]:
        print(f"💥 Components failed: {batch_results['total_components_failed']}")
    print(f"🕐 Total time: {batch_results['total_time']:.1f}s")
    print(f"🎯 Total tokens: {batch_results['total_tokens']}")

    return batch_results


def run_interactive_generation(
    generator: DynamicGenerator, author_info: Dict[str, Any] = None
) -> None:
    """
    Run interactive generation mode with user prompts.

    Args:
        generator: DynamicGenerator instance
        author_info: Optional author information
    """
    print("🎮 Interactive Generation Mode")
    print("=" * 50)

    # Get available materials and components
    materials = generator.get_available_materials()
    components = generator.get_available_components()

    print(f"📋 Available materials: {len(materials)}")
    print(f"🔧 Available components: {len(components)}")

    if author_info and author_info.get("name") != "AI Assistant":
        print(f"👤 Author: {author_info['name']} ({author_info['country']})")

    while True:
        print("\n" + "-" * 50)

        # Material selection
        print("\nSelect material:")
        material_input = input(
            "Enter material name (or 'list' to see all, 'quit' to exit): "
        ).strip()

        if material_input.lower() == "quit":
            print("👋 Goodbye!")
            break
        elif material_input.lower() == "list":
            print("\n📋 Available materials:")
            for i, mat in enumerate(materials[:20], 1):  # Show first 20
                print(f"  {i:2d}. {mat}")
            if len(materials) > 20:
                print(f"  ... and {len(materials) - 20} more")
            continue
        elif material_input not in materials:
            print(
                f"❌ Material '{material_input}' not found. Use 'list' to see available materials."
            )
            continue

        # Component selection
        print(f"\nSelected material: {material_input}")
        print("\nSelect components to generate:")
        print("Available components:", ", ".join(components))

        components_input = input(
            "Enter component names (comma-separated, or 'all'): "
        ).strip()

        if components_input.lower() == "all":
            selected_components = components
        else:
            selected_components = [c.strip() for c in components_input.split(",")]
            # Validate components
            invalid_components = [c for c in selected_components if c not in components]
            if invalid_components:
                print(f"❌ Invalid components: {invalid_components}")
                continue

        # Generate content
        try:
            run_dynamic_generation(
                generator=generator,
                material=material_input,
                component_types=selected_components,
                author_info=author_info,
            )

            print(f"\n✨ Interactive generation completed for {material_input}")

        except Exception as e:
            print(f"❌ Generation failed: {e}")


def run_material_generation(
    material: str, component_types: List[str], author_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate content for a single material.

    Args:
        material: Material name
        component_types: List of component types to generate
        author_id: Optional author ID

    Returns:
        Dictionary with generation results
    """
    generator = DynamicGenerator()

    # Validate material
    available_materials = generator.get_available_materials()
    if material not in available_materials:
        raise ValueError(
            f"Material '{material}' not found. Available materials: {len(available_materials)}"
        )

    # Validate components
    available_components = generator.get_available_components()
    invalid_components = [c for c in component_types if c not in available_components]
    if invalid_components:
        raise ValueError(
            f"Invalid components: {invalid_components}. Available: {available_components}"
        )

    # Get author info - prioritize frontmatter data
    author_info = get_author_info_for_material(material, author_id)

    # Generate content
    return run_dynamic_generation(
        generator=generator,
        material=material,
        component_types=component_types,
        author_info=author_info,
    )
