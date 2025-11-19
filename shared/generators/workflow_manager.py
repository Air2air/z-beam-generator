#!/usr/bin/env python3
"""
Workflow Manager

Centralized generation workflow management.
Extracted from                # Extract frontmatter data if this was the frontmatter component
                if component_type == "frontmatter":
                    try:
                        import yaml
                        # Strip YAML markers before parsing
                        content_to_parse = result.content.strip()
                        if content_to_parse.startswith('---'):
                            content_to_parse = content_to_parse[3:].strip()
                        if content_to_parse.endswith('---'):
                            content_to_parse = content_to_parse[:-3].strip()
                        
                        frontmatter_data = yaml.safe_load(content_to_parse)
                        print("    📋 Extracted frontmatter data for subsequent components")
                    except Exception as e:
                        print(f"    ⚠️  Failed to parse frontmatter data: {e}")
                        frontmatter_data = None reduce bloat and improve testability.
"""

import time
from typing import Any, Dict, List, Optional

from shared.api.client_manager import get_api_client_for_component
from shared.generators.dynamic_generator import DynamicGenerator
from export.utils.author_manager import (
    get_author_info_for_generation,
    get_author_info_for_material,
)
from shared.utils.file_ops.file_operations import save_component_to_file_original
from shared.utils.file_ops.frontmatter_loader import load_frontmatter_data


def run_dynamic_generation(
    generator: DynamicGenerator,
    material: str,
    component_types: List[str],
    author: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Run dynamic generation for specific material and components.

    Args:
        generator: DynamicGenerator instance
        material: Material name
        component_types: List of component types to generate
        author: Optional author information

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

    # Track frontmatter data for components that need it
    frontmatter_data = None
    
    # Check if we need frontmatter data for dependent components
    needs_frontmatter = any(c != "frontmatter" for c in component_types)
    if needs_frontmatter and "frontmatter" not in component_types:
        # Try to load existing frontmatter data from file
        frontmatter_data = load_frontmatter_data(material)
        if frontmatter_data:
            print("    📋 Loaded existing frontmatter data from file for dependent components")
        else:
            print("    ⚠️ Warning: Components may require frontmatter data, but no data was found")

    # Prioritize frontmatter generation first if it's in the list
    prioritized_components = []
    if "frontmatter" in component_types:
        prioritized_components.append("frontmatter")
        component_types = [c for c in component_types if c != "frontmatter"]

    # Add remaining components
    prioritized_components.extend(component_types)

    for component_type in prioritized_components:
        try:
            print(f"\n  🔨 Generating {component_type}...")

            # Get API client for this component
            print(f"    🔌 Requesting API client for {component_type}...")
            api_client = get_api_client_for_component(component_type)
            if api_client:
                print(f"    ✅ API client obtained for {component_type}")
            else:
                print(f"    ⚠️  No API client obtained for {component_type}")

            # Check if this component requires API based on configuration
            from shared.utils.component_mode import should_use_api
            
            if should_use_api(component_type, api_client):
                print(f"    🔌 Using API for {component_type} (hybrid mode)")
            elif api_client is None and component_type in ["frontmatter", "metatags", "propertiestable", "caption"]:
                print(f"    ⚠️  Warning: {component_type} is configured as a hybrid component but no API client is available")
                print("    🔧 Falling back to static generation mode")
            
            # Generate content
            component_start = time.time()
            result = generator.generate_component(
                material=material,
                component_type=component_type,
                api_client=api_client,
                author=author,
                frontmatter_data=frontmatter_data,  # Pass frontmatter data if available
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

                # Extract frontmatter data if this was the frontmatter component
                if component_type == "frontmatter":
                    try:
                        import yaml
                        # Strip YAML markers and parse the frontmatter content
                        content = result.content.strip()
                        if content.startswith('---'):
                            # Remove the opening marker
                            content = content[3:].strip()
                        if content.endswith('---'):
                            # Remove the closing marker
                            content = content[:-3].strip()
                        # Parse the YAML frontmatter content
                        frontmatter_data = yaml.safe_load(content)
                        print("    📋 Extracted frontmatter data for subsequent components")
                    except Exception as e:
                        print(f"    ⚠️  Failed to parse frontmatter data: {e}")
                        frontmatter_data = None

            else:
                from shared.utils.ai.loud_errors import component_failure

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
            from shared.utils.ai.loud_errors import component_failure

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
    total_count = len(prioritized_components)

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
    author = get_author_info_for_generation(author_id)

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
    if author.get("name") != "AI Assistant":
        print(f"👤 Author: {author['name']} ({author['country']})")

    for i, material in enumerate(materials, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(materials)}: {material}")
        print(f"{'='*60}")

        try:
            result = run_dynamic_generation(
                generator=generator,
                material=material,
                component_types=component_types,
                author=author,
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
    if not any(m.lower() == material.lower() for m in available_materials):
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

    # Get author info - use material data to retrieve material-specific author info
    # Find material data in Materials.yaml
    material_data = None
    materials_data = generator.materials_data
    if "materials" in materials_data:
        materials_section = materials_data["materials"]
        for category, category_data in materials_section.items():
            if isinstance(category_data, dict) and "items" in category_data:
                for item in category_data["items"]:
                    if "name" in item and item["name"].lower() == material.lower():
                        material_data = item
                        break
                if material_data:
                    break
    
    author = get_author_info_for_material(material_data, author_id)

    # Generate content
    return run_dynamic_generation(
        generator=generator,
        material=material,
        component_types=component_types,
        author=author,
    )
