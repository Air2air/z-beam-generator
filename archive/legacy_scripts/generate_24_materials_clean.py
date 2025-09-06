#!/usr/bin/env python3
"""
Z-Beam Generator: Clean Batch Generation of 24 Material                    result = generator.generate(
                        material_name=material['name'],
                        material_data=material,
                        api_client=api_client,
                        author_info=author_info
                    )NTENT COMPONENT ONLY
No fallbacks, fail-fast approach as specified in CLAUDE_INSTRUCTIONS.md
"""

import logging
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Generate 24 materials with clean fail-fast approach"""
    from components.content.generators.fail_fast_generator import (
        FailFastContentGenerator,
    )

    # Material assignments (6 per author) - using exact names from materials.yaml
    materials_by_author = {
        1: [
            "Alumina",
            "Zirconia",
            "Silicon Nitride",
            "Borosilicate Glass",
            "Brick",
            "Cement",
        ],
        2: ["Aluminum", "Copper", "Brass", "Bronze", "Beryllium", "Cobalt"],
        3: [
            "Concrete",
            "Stainless Steel",
            "Titanium",
            "Tungsten",
            "Silicon",
            "Silicon Carbide",
        ],
        4: [
            "Carbon Fiber Reinforced Polymer",
            "Fiberglass",
            "Rubber",
            "Bamboo",
            "Ash",
            "Beech",
        ],
    }

    logger.info(
        "🚀 Starting clean batch generation of 24 materials - CONTENT COMPONENT ONLY"
    )
    logger.info("✅ No fallbacks - fail-fast approach with quality scoring")

    try:
        # Initialize fail-fast generator with quality scoring
        generator = FailFastContentGenerator(
            max_retries=3, retry_delay=1.0, enable_scoring=True, human_threshold=75.0
        )

        # Set up Grok API client for content generation
        from cli.api_config import create_api_client

        api_client = create_api_client("grok")

        total_materials = 0
        total_time = 0

        for author_id, materials in materials_by_author.items():
            logger.info(
                f"\n👤 Author {author_id}: Generating {len(materials)} materials"
            )

            for material_name in materials:
                start_time = time.time()

                try:
                    logger.info(f"  🔄 Generating: {material_name}")

                    # Generate with quality scoring and retry logic
                    # Need to get material data first
                    from generators.dynamic_generator import MaterialLoader

                    material_loader = MaterialLoader()
                    material_data = material_loader.get_material(material_name)

                    if not material_data:
                        logger.error(
                            f"    ❌ FAILED: {material_name} - Material not found"
                        )
                        continue

                        # Extract material formula (optional)
                    formula = material_data.get("data", {}).get(
                        "formula", material_name
                    )
                    if not formula:
                        formula = (
                            material_name  # Use material name as fallback for formula
                        )

                    # Extract author info from material data
                    author_id = material_data.get("data", {}).get("author_id")
                    # For now, create basic author info from ID
                    author_info = {"id": author_id, "name": f"Author {author_id}"}

                    result = generator.generate(
                        material_name=material_name,
                        material_data=material_data,
                        api_client=api_client,
                        author_info=author_info,
                    )

                    if result and result.success:
                        generation_time = time.time() - start_time
                        total_time += generation_time
                        total_materials += 1

                        # Save content to file
                        from utils.slug_utils import create_filename_slug

                        filename = create_filename_slug(material_name)
                        output_file = (
                            Path("content/components/content") / f"{filename}.md"
                        )

                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(result.content)

                        logger.info(
                            f"    ✅ SUCCESS: {material_name} ({generation_time:.1f}s)"
                        )
                        logger.info(f"    💾 Saved to: {output_file}")

                        # Log quality metrics if available
                        if result.quality_score:
                            qs = result.quality_score
                            logger.info(
                                f"    📊 Quality: Overall={qs.overall_score:.1f}, Human={qs.human_believability:.1f}, Technical={qs.technical_accuracy:.1f}"
                            )
                            logger.info(
                                f"    🎯 Retry Recommended: {'Yes' if qs.retry_recommended else 'No'}"
                            )

                    else:
                        logger.error(
                            f"    ❌ FAILED: {material_name} - Generation failed"
                        )
                        if result and result.error_message:
                            logger.error(f"        💬 Error: {result.error_message}")

                except Exception as e:
                    logger.error(f"    💥 FAILED: {material_name} - {str(e)}")
                    # Continue with next material (fail-fast per material, not per batch)
                    continue

        # Summary
        logger.info(f"\n🎯 GENERATION COMPLETE")
        logger.info(f"✅ Successfully generated: {total_materials}/24 materials")
        logger.info(f"⏱️  Total time: {total_time:.1f}s")
        logger.info(
            f"📈 Average time per material: {total_time/max(total_materials, 1):.1f}s"
        )

        if total_materials < 24:
            logger.warning(f"⚠️  {24 - total_materials} materials failed generation")
            return 1
        else:
            logger.info("🎉 All materials generated successfully!")
            return 0

    except Exception as e:
        logger.error(f"💥 CRITICAL FAILURE: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
