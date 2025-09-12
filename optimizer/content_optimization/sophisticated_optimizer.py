"""
Sophisticated Optimizer Module

Handles the main optimization workflow combining AI detection,
quality scoring, and iterative improvement.
"""

import asyncio
import logging
import os
from pathlib import Path

from .content_analyzer import (
    extract_author_info_from_frontmatter_file,
    update_content_with_ai_analysis,
    update_content_with_comprehensive_analysis
)
from .data_finder import find_material_data

logger = logging.getLogger(__name__)


async def run_sophisticated_optimization(component_name: str, timeout_seconds: int = 600):
    """Run sophisticated optimization for a component using existing services with timeout protection.

    Args:
        component_name: Name of the component to optimize (e.g., 'text', 'bullets')
        timeout_seconds: Maximum time to allow the optimization to run (default: 10 minutes)
    """
    try:
        logger.info(
            f"🚀 Starting sophisticated optimization for {component_name} with {timeout_seconds}s timeout"
        )
        
        # Local helper functions
        def get_config():
            """Get basic config from run.py"""
            try:
                from run import COMPONENT_CONFIG, API_PROVIDERS
                return {"components": COMPONENT_CONFIG, "api": API_PROVIDERS}
            except ImportError:
                return {"components": {}, "api": {}}
        
        def is_test_mode():
            """Test mode detection using environment variables"""
            return any([
                os.getenv("TEST_MODE", "").lower() in ("true", "1", "yes"),
                os.getenv("PYTEST_CURRENT_TEST", "") != "",
                "pytest" in os.getenv("_", "").lower(),
            ])

        # Import optimization components
        from data.materials import load_materials
        from generators.dynamic_generator import DynamicGenerator
        from generators.workflow_manager import run_dynamic_generation
        from optimizer.ai_detection.service import initialize_ai_detection_service
        from optimizer.ai_detection.types import AIDetectionConfig
        from optimizer.text_optimization.ai_detection_prompt_optimizer import (
            AIDetectionPromptOptimizer,
        )
        from optimizer.text_optimization.dynamic_prompt_generator import (
            DynamicPromptGenerator,
        )
        from optimizer.text_optimization.validation.scoring import (
            ContentQualityScorer,
        )

        config_data = get_config()
        test_mode = is_test_mode()

        # Use mock provider in test mode, winston in production
        ai_provider = "mock" if test_mode else "winston"
        target_score = config_data.get("AI_DETECTION", {}).get("TARGET_SCORE", 70.0)
        max_iterations = config_data.get("AI_DETECTION", {}).get("MAX_ITERATIONS", 5)
        timeout = config_data.get("AI_DETECTION", {}).get("TIMEOUT", 30)

        config = AIDetectionConfig(
            provider=ai_provider,
            enabled=True,
            target_score=target_score,
            max_iterations=max_iterations,
            improvement_threshold=5.0,
            timeout=timeout,
            retry_attempts=3,
        )
        ai_service = initialize_ai_detection_service(config)

        # Initialize optimization components
        prompt_optimizer = AIDetectionPromptOptimizer()
        dynamic_generator = DynamicPromptGenerator()
        quality_scorer = ContentQualityScorer(human_threshold=75.0)

        # Load supporting data
        generator = DynamicGenerator()
        materials_data = load_materials()

        # Find all material files in the component directory
        component_dir = Path("content/components") / component_name
        if not component_dir.exists():
            logger.error(f"Component directory not found: {component_dir}")
            return

        # Get all .md files in the component directory
        material_files = list(component_dir.glob("*.md"))
        if not material_files:
            logger.warning(f"No material files found in {component_dir}")
            return

        logger.info(f"📂 Found {len(material_files)} material files to optimize")

        # Load content from each file
        materials_content = {}
        for file_path in material_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract material name from filename (remove -laser-cleaning.md suffix)
                material_name = file_path.stem.replace("-laser-cleaning", "")
                materials_content[material_name] = content
                logger.info(f"   📄 Loaded {material_name} from {file_path.name}")

            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                continue

        if not materials_content:
            logger.error("No content loaded for optimization")
            return

        successful_optimizations = 0
        total_improvement = 0.0

        for material_name, original_content in materials_content.items():
            logger.info(f"\n🔄 Optimizing {material_name}...")

            # Get initial quality assessment with timeout protection
            try:
                initial_result = await asyncio.wait_for(
                    asyncio.to_thread(ai_service.detect_ai_content, original_content),
                    timeout=30,
                )
                initial_score = initial_result.score
                logger.info(f"   📊 Initial score: {initial_score:.1f}")
            except asyncio.TimeoutError:
                logger.error(f"   Initial AI detection timed out for {material_name}")
                continue
            except Exception as e:
                logger.error(f"   Initial AI detection failed for {material_name}: {e}")
                continue

            current_content = original_content
            best_score = initial_score
            best_content = original_content
            iteration = 0
            consecutive_failures = 0

            # Extract author info from frontmatter file (fail-fast required)
            author_info = extract_author_info_from_frontmatter_file(material_name)
            if not author_info:
                raise ValueError(f"Author information must be available for {material_name} - no defaults allowed in fail-fast architecture")

            logger.info(
                f"   👤 Author: {author_info.get('name', 'Unknown')} (Country: {author_info.get('country', 'Unknown')})"
            )

            # Find material data for context
            material_data = find_material_data(material_name, materials_data.get("materials", {}))
            if not material_data:
                raise ValueError(f"Material data must be available for {material_name} - no defaults allowed in fail-fast architecture")

            while iteration < config.max_iterations:
                iteration += 1
                logger.info(f"   📊 Iteration {iteration}/{config.max_iterations}")

                try:
                    # Step 1: Quality assessment with 5-dimension scoring
                    quality_result = quality_scorer.score_content(
                        current_content, material_data, author_info
                    )
                    if not quality_result:
                        raise ValueError(f"Quality scoring failed for {material_name} - no defaults allowed in fail-fast architecture")
                        
                    logger.info(
                        f"      📊 Quality Score: {quality_result.overall_score:.1f}/100"
                    )
                    logger.info(
                        f"         🤖 Believability: {quality_result.believability_score:.1f}"
                    )
                    logger.info(
                        f"         📝 Authenticity: {quality_result.authenticity_score:.1f}"
                    )
                    logger.info(
                        f"         📖 Readability: {quality_result.readability_score:.1f}"
                    )

                    # Step 2: AI detection analysis with timeout protection
                    try:
                        ai_result = await asyncio.wait_for(
                            asyncio.to_thread(
                                ai_service.detect_ai_content, current_content
                            ),
                            timeout=30,
                        )
                        current_score = ai_result.score
                        logger.info(
                            f"      📊 AI Detection Score: {current_score:.1f} (Target: {config.target_score})"
                        )
                    except asyncio.TimeoutError:
                        logger.error(
                            f"      AI detection timed out in iteration {iteration}"
                        )
                        consecutive_failures += 1
                        continue
                    except Exception as e:
                        logger.error(
                            f"      AI detection failed in iteration {iteration}: {e}"
                        )
                        consecutive_failures += 1
                        continue

                    # Update best content if improved
                    if current_score > best_score:
                        improvement = current_score - best_score
                        best_score = current_score
                        best_content = current_content
                        logger.info(
                            f"      ✅ New best score: {best_score:.1f} (+{improvement:.1f})"
                        )

                    # Check if we've reached the target
                    if current_score >= config.target_score:
                        logger.info(f"      🎯 Target reached! Score: {current_score:.1f}")
                        break

                    # Step 3: Generate improvement suggestions using DynamicPromptGenerator
                    # Convert AIDetectionResult to dict format expected by DynamicPromptGenerator
                    winston_result_dict = {
                        "overall_score": ai_result.score,
                        "classification": ai_result.classification,
                        "confidence": ai_result.confidence,
                        "processing_time": ai_result.processing_time,
                        "provider": ai_result.provider,
                        "details": ai_result.details or {},
                    }

                    improvement_context = {
                        "material_name": material_name,
                        "current_score": current_score,
                        "target_score": config.target_score,
                        "iteration": iteration,
                        "quality_metrics": {
                            "overall": quality_result.overall_score,
                            "believability": quality_result.believability_score,
                            "authenticity": quality_result.authenticity_score,
                            "readability": quality_result.readability_score,
                        },
                    }

                    improvements = dynamic_generator.generate_prompt_improvements(
                        winston_result=winston_result_dict,
                        content=current_content,
                        iteration_context=improvement_context,
                    )

                    if improvements:
                        # Step 4: Apply gradual improvements
                        success = dynamic_generator.apply_gradual_improvements(
                            improvements
                        )
                        if success:
                            logger.info(
                                f"      🔧 Applied {len(improvements)} prompt improvements"
                            )
                        else:
                            logger.warning("      No improvements applied this iteration")

                    # Step 5: Regenerate content with enhancement flags if score is low
                    if current_score < 50.0 and iteration == 1:
                        logger.info(
                            f"      🔄 Score too low ({current_score:.1f}), regenerating content..."
                        )

                        if material_data:
                            try:
                                logger.info(
                                    "      🔄 Regenerating content with timeout protection..."
                                )

                                # Create a timeout-protected task for content regeneration
                                async def regenerate_with_timeout():
                                    return await asyncio.to_thread(
                                        run_dynamic_generation,
                                        generator=generator,
                                        material=material_data["name"],
                                        component_types=[component_name],
                                        author_info=author_info,
                                    )

                                results = await asyncio.wait_for(
                                    regenerate_with_timeout(),
                                    timeout=120,  # 2 minutes for content regeneration
                                )

                                if results.get("components_generated"):
                                    # Load the regenerated content
                                    new_content_file = (
                                        Path("content/components")
                                        / component_name
                                        / f"{material_name}-laser-cleaning.md"
                                    )
                                    if new_content_file.exists():
                                        with open(
                                            new_content_file, "r", encoding="utf-8"
                                        ) as f:
                                            new_content = f.read()

                                        # Apply preamble removal to regenerated content
                                        from components.text.generator import TextComponentGenerator
                                        text_gen = TextComponentGenerator()
                                        cleaned_content = text_gen._remove_preamble_text(new_content)
                                        cleaned_content = text_gen._remove_existing_frontmatter(cleaned_content)

                                        # Update with AI analysis
                                        current_content = (
                                            update_content_with_ai_analysis(
                                                cleaned_content, ai_result, material_name
                                            )
                                        )
                                        
                                        # Save the cleaned content back to file
                                        with open(new_content_file, "w", encoding="utf-8") as f:
                                            f.write(current_content)
                                        
                                        logger.info(
                                            "      🔄 Regenerated and cleaned content with basic improvements"
                                        )
                                        consecutive_failures = 0
                                        continue
                            except asyncio.TimeoutError:
                                logger.error(
                                    f"      Content regeneration timed out for {material_name}"
                                )
                                consecutive_failures += 1
                            except Exception as e:
                                logger.error(f"      Error regenerating content: {e}")
                                consecutive_failures += 1
                        else:
                            consecutive_failures += 1

                    # Check for improvement stagnation
                    elif (
                        iteration > 1
                        and (current_score - best_score) < config.improvement_threshold
                    ):
                        consecutive_failures += 1
                        logger.warning(
                            f"      Minimal improvement ({current_score - best_score:.1f} < {config.improvement_threshold})"
                        )
                    else:
                        consecutive_failures = 0

                    # Stop if too many consecutive failures
                    if consecutive_failures >= 2:
                        logger.warning(
                            f"      🛑 Stopping after {consecutive_failures} consecutive failures"
                        )
                        break

                except Exception as e:
                    logger.error(f"      Error in iteration {iteration}: {e}")
                    consecutive_failures += 1
                    if consecutive_failures >= 2:
                        break
                    continue

            # Save the best content found
            original_file = component_dir / f"{material_name}-laser-cleaning.md"

            # Add comprehensive analysis to the best content with timeout protection
            try:
                final_result = await asyncio.wait_for(
                    asyncio.to_thread(ai_service.detect_ai_content, best_content),
                    timeout=30,
                )
                final_quality = quality_scorer.score_content(
                    best_content, material_data, author_info
                )
            except asyncio.TimeoutError:
                logger.error(f"   Final AI detection timed out for {material_name}")
                # Use the last ai_result if available, otherwise skip
                if "ai_result" in locals():
                    final_result = ai_result
                    final_quality = quality_scorer.score_content(
                        best_content, material_data, author_info
                    )
                else:
                    continue
            except Exception as e:
                logger.error(f"   Final AI detection failed for {material_name}: {e}")
                continue

            # Create enhanced metadata
            enhanced_content = update_content_with_comprehensive_analysis(
                best_content, final_result, final_quality, material_name, iteration
            )

            with open(original_file, "w", encoding="utf-8") as f:
                f.write(enhanced_content)

            improvement = best_score - initial_score
            total_improvement += improvement

            logger.info(
                f"      ✅ {material_name}: Best score {best_score:.1f} after {iteration} iterations"
            )
            logger.info(f"         📈 Improvement: +{improvement:.1f}")
            logger.info(f"         🎯 Quality Score: {final_quality.overall_score:.1f}/100")

            if best_score >= config.target_score:
                successful_optimizations += 1

        # Summary statistics
        avg_improvement = (
            total_improvement / len(materials_content) if materials_content else 0
        )
        success_rate = (
            (successful_optimizations / len(materials_content)) * 100
            if materials_content
            else 0
        )

        logger.info("\n🏁 Sophisticated optimization completed!")
        logger.info(f"   📊 Materials processed: {len(materials_content)}")
        logger.info(f"   ✅ Target achieved: {successful_optimizations}")
        logger.info(f"   📈 Average improvement: +{avg_improvement:.1f}")
        logger.info(f"   🎯 Success rate: {success_rate:.1f}%")

    except Exception as e:
        logger.error(f"Error initializing optimization services: {e}")
        import traceback
        traceback.print_exc()
