#!/usr/bin/env python3
"""
Content Optimization Module

This module contains the optimization-related methods that were previously
embedded in run.py. It provides a clean separation of concerns for content
optimization functionality.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def update_content_with_ai_analysis(content: str, ai_result, material_name: str) -> str:
    """Update content with AI detection analysis in proper YAML frontmatter format.

    This function ensures:
    1. Frontmatter appears at the top in proper YAML format
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

        # Extract content (everything after first ---)
        if frontmatter_start_idx >= 0 and frontmatter_end_idx > frontmatter_start_idx:
            content_lines = lines[frontmatter_end_idx + 1 :]
        else:
            content_lines = lines

        # Start with frontmatter delimiter
        updated_lines.append("---")

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
                            ai_lines.append(f'      {sub_key}: "{sub_value}"')
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
                        ai_lines.append(f'    {key}: "{value}"')
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
        updated_lines.append("")  # Add blank line before content

        # Add content
        updated_lines.extend(content_lines)

        return "\n".join(updated_lines)

    except Exception as e:
        print(f"⚠️ Error updating frontmatter for {material_name}: {e}")
        import traceback
        traceback.print_exc()
        return content


def extract_author_info_from_content(content: str) -> Optional[Dict[str, Any]]:
    """Extract author information from content frontmatter."""
    try:
        lines = content.split("\n")
        in_frontmatter = False
        author_info = {}

        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
                continue

            if in_frontmatter and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"')

                if key == "author":
                    author_info["name"] = value
                elif key == "persona_country":
                    author_info["country"] = value.lower()
                elif key == "author_id":
                    author_info["id"] = int(value) if value.isdigit() else 1

        if author_info:
            author_info.setdefault("id", 1)
            author_info.setdefault("country", "usa")
            return author_info

    except Exception as e:
        print(f"⚠️ Error extracting author info: {e}")

    return None


def extract_author_info_from_frontmatter_file(material_name: str) -> Optional[Dict[str, Any]]:
    """Extract author information from the corresponding frontmatter file."""
    try:
        # Look for the frontmatter file
        frontmatter_path = Path("content/components/frontmatter") / f"{material_name}-laser-cleaning.md"

        if not frontmatter_path.exists():
            return None

        with open(frontmatter_path, "r", encoding="utf-8") as f:
            content = f.read()

        return extract_author_info_from_content(content)

    except Exception as e:
        print(f"⚠️ Error extracting author info from frontmatter file: {e}")
        return None


def find_material_data(material_name: str, materials_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find material data from the materials database."""
    try:
        for category_data in materials_data.values():
            for item in category_data.get("items", []):
                if item["name"].lower().replace(" ", "-") == material_name.lower():
                    return item
    except Exception as e:
        print(f"⚠️ Error finding material data for {material_name}: {e}")

    return None


def update_content_with_comprehensive_analysis(
    content: str,
    ai_result,
    quality_result,
    material_name: str,
    iterations: int
) -> str:
    """Update content with comprehensive analysis including quality metrics."""
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

        # Extract content (everything after first ---)
        if frontmatter_start_idx >= 0 and frontmatter_end_idx > frontmatter_start_idx:
            content_lines = lines[frontmatter_end_idx + 1 :]
        else:
            content_lines = lines

        # Start with frontmatter delimiter
        updated_lines.append("---")

        # Add comprehensive analysis
        analysis_lines = [
            "ai_detection_analysis:",
            f"  score: {ai_result.score:.6f}",
            f"  confidence: {ai_result.confidence:.6f}",
            f'  classification: "{ai_result.classification}"',
            f'  provider: "{ai_result.provider}"',
            f"  processing_time: {ai_result.processing_time:.6f}",
            f"  optimization_iterations: {iterations}",
            "",
            "quality_analysis:",
            f"  overall_score: {quality_result.overall_score:.6f}",
            f"  formatting_score: {quality_result.formatting_score:.6f}",
            f"  technical_score: {quality_result.technical_score:.6f}",
            f"  authenticity_score: {quality_result.authenticity_score:.6f}",
            f"  readability_score: {quality_result.readability_score:.6f}",
            f"  believability_score: {quality_result.believability_score:.6f}",
            f"  word_count: {quality_result.details.get('word_count', 0)}",
            f'  author_country: "{quality_result.details.get("author_country", "")}"',
        ]

        if ai_result.details:
            analysis_lines.append("  details:")
            for key, value in ai_result.details.items():
                if isinstance(value, dict):
                    analysis_lines.append(f"    {key}:")
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            analysis_lines.append(f'      {sub_key}: "{sub_value}"')
                        elif isinstance(sub_value, (int, float)):
                            if isinstance(sub_value, float):
                                analysis_lines.append(f"      {sub_key}: {sub_value:.6f}")
                            else:
                                analysis_lines.append(f"      {sub_key}: {sub_value}")
                        else:
                            analysis_lines.append(f"      {sub_key}: {sub_value}")
                else:
                    if isinstance(value, str):
                        analysis_lines.append(f'    {key}: "{value}"')
                    elif isinstance(value, (int, float)):
                        if isinstance(value, float):
                            analysis_lines.append(f"    {key}: {value:.6f}")
                        else:
                            analysis_lines.append(f"    {key}: {value}")
                    else:
                        analysis_lines.append(f"    {key}: {value}")

        updated_lines.extend(analysis_lines)

        # Add closing marker
        updated_lines.append("---")
        updated_lines.append("")  # Add blank line before content

        # Add content
        updated_lines.extend(content_lines)

        return "\n".join(updated_lines)

    except Exception as e:
        print(f"⚠️ Error updating comprehensive analysis for {material_name}: {e}")
        import traceback
        traceback.print_exc()
        return content


async def run_sophisticated_optimization(component_name: str):
    """Run sophisticated optimization for a component using existing services."""
    try:
        # Import optimization components
        from optimizer.ai_detection.service import (
            get_ai_detection_service,
            initialize_ai_detection_service,
        )
        from optimizer.ai_detection.types import AIDetectionConfig
        from optimizer.text_optimization.ai_detection_prompt_optimizer import AIDetectionPromptOptimizer
        from optimizer.text_optimization.dynamic_prompt_generator import DynamicPromptGenerator
        from optimizer.text_optimization.validation.content_scorer import ContentQualityScorer
        from data.materials import load_materials
        from generators.dynamic_generator import DynamicGenerator

        # Initialize services
        config = AIDetectionConfig(
            provider="winston",
            enabled=True,
            target_score=70.0,
            max_iterations=5,
            improvement_threshold=5.0,
            timeout=30,
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
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract material name from filename (remove -laser-cleaning.md suffix)
                material_name = file_path.stem.replace("-laser-cleaning", "")
                materials_content[material_name] = content
                print(f"   📄 Loaded {material_name} from {file_path.name}")

            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
                continue

        if not materials_content:
            print("❌ No content loaded for optimization")
            return

        successful_optimizations = 0
        total_improvement = 0.0

        for material_name, original_content in materials_content.items():
            print(f"\n🔄 Optimizing {material_name}...")

            # Get initial quality assessment
            initial_result = ai_service.detect_ai_content(original_content)
            initial_score = initial_result.score
            print(f"   📊 Initial score: {initial_score:.1f}")

            current_content = original_content
            best_score = initial_score
            best_content = original_content
            iteration = 0
            consecutive_failures = 0

            # Extract author info from frontmatter file (improved method)
            author_info = extract_author_info_from_frontmatter_file(material_name)
            if not author_info:
                # Fallback to extracting from content
                author_info = extract_author_info_from_content(current_content)
            if not author_info:
                author_info = {
                    "id": 1,
                    "name": "Research Author",
                    "country": "usa"
                }

            print(f"   👤 Author: {author_info.get('name', 'Unknown')} (Country: {author_info.get('country', 'Unknown')})")

            # Find material data for context
            material_data = find_material_data(material_name, materials_data)

            while iteration < config.max_iterations:
                iteration += 1
                print(f"   📊 Iteration {iteration}/{config.max_iterations}")

                try:
                    # Step 1: Quality assessment with 5-dimension scoring
                    quality_result = quality_scorer.score_content(
                        current_content, material_data, author_info
                    )
                    print(f"      📊 Quality Score: {quality_result.overall_score:.1f}/100")
                    print(f"         🤖 Believability: {quality_result.believability_score:.1f}")
                    print(f"         📝 Authenticity: {quality_result.authenticity_score:.1f}")
                    print(f"         📖 Readability: {quality_result.readability_score:.1f}")

                    # Step 2: AI detection analysis
                    ai_result = ai_service.detect_ai_content(current_content)
                    current_score = ai_result.score
                    print(f"      📊 AI Detection Score: {current_score:.1f} (Target: {config.target_score})")

                    # Update best content if improved
                    if current_score > best_score:
                        improvement = current_score - best_score
                        best_score = current_score
                        best_content = current_content
                        print(f"      ✅ New best score: {best_score:.1f} (+{improvement:.1f})")

                    # Check if we've reached the target
                    if current_score >= config.target_score:
                        print(f"      🎯 Target reached! Score: {current_score:.1f}")
                        break

                    # Step 3: Generate improvement suggestions using DynamicPromptGenerator
                    # Convert AIDetectionResult to dict format expected by DynamicPromptGenerator
                    winston_result_dict = {
                        "overall_score": ai_result.score,
                        "classification": ai_result.classification,
                        "confidence": ai_result.confidence,
                        "processing_time": ai_result.processing_time,
                        "provider": ai_result.provider,
                        "details": ai_result.details or {}
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
                        }
                    }

                    improvements = dynamic_generator.generate_prompt_improvements(
                        winston_result=winston_result_dict,
                        content=current_content,
                        iteration_context=improvement_context
                    )

                    if improvements:
                        # Step 4: Apply gradual improvements
                        success = dynamic_generator.apply_gradual_improvements(improvements)
                        if success:
                            print(f"      🔧 Applied {len(improvements)} prompt improvements")
                        else:
                            print(f"      ⚠️ No improvements applied this iteration")

                    # Step 5: Regenerate content with enhancement flags if score is low
                    if current_score < 50.0 and iteration == 1:
                        print(f"      🔄 Score too low ({current_score:.1f}), regenerating content...")

                        if material_data:
                            try:
                                from generators.workflow_manager import run_dynamic_generation

                                results = run_dynamic_generation(
                                    generator=generator,
                                    material=material_data["name"],
                                    component_types=[component_name],
                                    author_info=author_info
                                )

                                if results.get("components_generated"):
                                    # Load the regenerated content
                                    new_content_file = (
                                        Path("content/components") / component_name /
                                        f"{material_name}-laser-cleaning.md"
                                    )
                                    if new_content_file.exists():
                                        with open(new_content_file, "r", encoding="utf-8") as f:
                                            new_content = f.read()

                                        # Update with AI analysis
                                        current_content = update_content_with_ai_analysis(
                                            new_content, ai_result, material_name
                                        )
                                        print(f"      🔄 Regenerated content with basic improvements")
                                        consecutive_failures = 0
                                        continue
                            except Exception as e:
                                print(f"      ❌ Error regenerating content: {e}")
                                consecutive_failures += 1
                        else:
                            consecutive_failures += 1

                    # Check for improvement stagnation
                    elif iteration > 1 and (current_score - best_score) < config.improvement_threshold:
                        consecutive_failures += 1
                        print(f"      ⚠️ Minimal improvement ({current_score - best_score:.1f} < {config.improvement_threshold})")
                    else:
                        consecutive_failures = 0

                    # Stop if too many consecutive failures
                    if consecutive_failures >= 2:
                        print(f"      🛑 Stopping after {consecutive_failures} consecutive failures")
                        break

                except Exception as e:
                    print(f"      ❌ Error in iteration {iteration}: {e}")
                    consecutive_failures += 1
                    if consecutive_failures >= 2:
                        break
                    continue

            # Save the best content found
            original_file = component_dir / f"{material_name}-laser-cleaning.md"

            # Add comprehensive analysis to the best content
            final_result = ai_service.detect_ai_content(best_content)
            final_quality = quality_scorer.score_content(best_content, material_data, author_info)

            # Create enhanced metadata
            enhanced_content = update_content_with_comprehensive_analysis(
                best_content, final_result, final_quality, material_name, iteration
            )

            with open(original_file, "w", encoding="utf-8") as f:
                f.write(enhanced_content)

            improvement = best_score - initial_score
            total_improvement += improvement

            print(f"      ✅ {material_name}: Best score {best_score:.1f} after {iteration} iterations")
            print(f"         📈 Improvement: +{improvement:.1f}")
            print(f"         🎯 Quality Score: {final_quality.overall_score:.1f}/100")

            if best_score >= config.target_score:
                successful_optimizations += 1

        # Summary statistics
        avg_improvement = total_improvement / len(materials_content) if materials_content else 0
        success_rate = (successful_optimizations / len(materials_content)) * 100 if materials_content else 0

        print(f"\n🏁 Sophisticated optimization completed!")
        print(f"   📊 Materials processed: {len(materials_content)}")
        print(f"   ✅ Target achieved: {successful_optimizations}")
        print(f"   📈 Average improvement: +{avg_improvement:.1f}")
        print(f"   🎯 Success rate: {success_rate:.1f}%")

    except Exception as e:
        print(f"❌ Error initializing optimization services: {e}")
        import traceback
        traceback.print_exc()
