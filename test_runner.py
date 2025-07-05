#!/usr/bin/env python3
"""
from config.global_config import get_config
Content generation test functions for regular validation.
"""

import sys
import os
from typing import Dict, Any

# Setup paths for imports
import setup_paths

from core.container import get_container
from core.application import configure_services
from core.interfaces.services import IContentGenerator
from core.domain.models import (
    GenerationContext,
    GenerationRequest,
    SectionConfig,
    SectionType,
    ProviderType,
    TemperatureConfig,
)
from generator.modules.logger import get_logger


def run_content_test(
    material: str = "aluminum",
    section: str = "introduction",
    word_limit: int = 300,
    ai_threshold: int = 25,
    human_threshold: int = 25,
    max_iterations: int = 3,
    max_tokens: int = 3000,
) -> Dict[str, Any]:
    """
    Run a content generation test with AI detection iteration.

    Returns:
        Dict containing test results including scores, iterations, and content.
    """
    from pathlib import Path

    logger = get_logger(__name__)

    # Get project root and find section templates
    project_root = Path(__file__).parent
    sections_dir = project_root / "generator" / "prompts" / "sections"

    print("🧪 Content Generation Test")
    print("=" * 50)
    print(f"   Material: {material}")
    print(f"   Section: {section}")
    print(f"   Word Limit: {word_limit}")
    print(f"   AI Threshold: ≤{ai_threshold}%")
    print(f"   Human Threshold: ≤{human_threshold}%")
    print(f"   Max Iterations: {max_iterations}")
    print(f"   Max Tokens: {max_tokens}")
    print()

    try:
        # Initialize the container and configure services
        container = get_container()
        configure_services(container)

        # Get content generator service
        content_generator = container.get(IContentGenerator)

        # Create test context and section config
        context = GenerationContext(
            material=material,
            content_type=section,
            variables={
                "material": material,
                "section_name": section,
                "audience_level": "professional",
                "technique": "laser_cleaning",
                "word_limit": word_limit,
            },
        )

        # Check if the prompt file specifies ai_detect: false
        is_ai_detect = True
        prompt_file_path = sections_dir / f"{section}.txt"
        if prompt_file_path.exists():
            with open(prompt_file_path, "r") as f:
                prompt_content = f.read(
                    500
                )  # Just read the first 500 chars for metadata
                if "# ai_detect: false" in prompt_content.lower():
                    is_ai_detect = False
                    logger.info(
                        f"Section {section} has ai_detect: false in prompt file"
                    )

        section_config = SectionConfig(
            name=section,
            ai_detect=is_ai_detect,  # Respect the setting from the prompt file
            prompt_file=f"{section}.txt",
            section_type=SectionType.TEXT,
            generate=True,
            order=0,
        )

        # Create temperature configuration
        temp_config = TemperatureConfig(
            content_temp=0.7,  # Balanced creativity for content generation
            detection_temp=0.3,  # Lower temperature for consistent detection
            improvement_temp=0.8,  # Higher temperature for creative improvements
        )

        # Get the provider from run.py config if available
        from importlib import import_module

        try:
            run_module = import_module("run")
            provider_name = getattr(
                run_module.USER_CONFIG, "detection_provider", None
            )
            provider = getattr(
                ProviderType, provider_name.upper(), None
            ) if provider_name else None
            model = None

            # Get model from PROVIDER_MODELS in run.py
            if hasattr(run_module, "PROVIDER_MODELS") and provider_name:
                model_settings = run_module.PROVIDER_MODELS.get(provider_name, {})
                model = model_settings.get("model")
        except (ImportError, AttributeError):
            # No fallback - must be properly configured
            provider = None
            model = None

        # Create generation request
        request = GenerationRequest(
            material=material,
            sections=[section],
            provider=provider,  # Use provider from config
            model=model,  # Use model from config
            ai_detection_threshold=ai_threshold,
            human_detection_threshold=human_threshold,
            iterations_per_section=max_iterations,
            temperature=get_config().get_improvement_temperature(),  # Legacy field kept for backward compatibility
            detection_temperature=get_config().get_detection_temperature(),  # Legacy field kept for backward compatibility
            max_tokens=max_tokens,
            force_regenerate=True,
            temperature_config=temp_config,  # Use new temperature configuration
        )

        print("🚀 Starting content generation...")
        print("-" * 50)

        # Generate content with AI detection enabled
        result = content_generator.generate_section(request, section_config, context)

        # Display results
        print()
        print("📊 Test Results:")
        print(f"   ✨ Iterations Completed: {result.iterations_completed}")

        # If ai_detect is False, we don't have scores to check
        if not is_ai_detect:
            ai_passed = True
            human_passed = True
            overall_passed = True
            print(f"   🎯 AI Detection: SKIPPED (ai_detect=false)")
            print(f"   🏁 Overall: ✅ SUCCESS (no detection required)")
        else:
            # Display AI/Human scores
            print(
                f"   🤖 Final AI Score: {result.ai_score.score}% (target: ≤{ai_threshold}%)"
            )
            print(
                f"   👤 Final Human Score: {result.human_score.score}% (target: ≤{human_threshold}%)"
            )

            # Check if thresholds were met
            ai_passed = result.ai_score.score <= ai_threshold
            human_passed = result.human_score.score <= human_threshold
            overall_passed = ai_passed and human_passed

            print(f"   🎯 AI Threshold: {'✅ PASS' if ai_passed else '❌ FAIL'}")
            print(f"   🎯 Human Threshold: {'✅ PASS' if human_passed else '❌ FAIL'}")
            print(
                f"   🏁 Overall: {'✅ SUCCESS' if overall_passed else '❌ NEEDS WORK'}"
            )
        print(f"   📏 Content Length: {len(result.content)} characters")
        print()

        # Show a snippet of generated content
        content_preview = (
            result.content[:200] + "..."
            if len(result.content) > 200
            else result.content
        )
        print("📝 Content Preview:")
        print("-" * 30)
        print(content_preview)
        print("-" * 30)

        # Build result dictionary based on whether AI detection was enabled
        result_dict = {
            "success": True,
            "overall_passed": overall_passed,
            "iterations": result.iterations_completed,
            "content_length": len(result.content),
            "content": result.content,
        }

        if not is_ai_detect:
            # For sections with AI detection disabled
            result_dict.update(
                {
                    "ai_detect": False,
                }
            )
        else:
            # For sections with AI detection
            result_dict.update(
                {
                    "ai_score": result.ai_score.score,
                    "human_score": result.human_score.score,
                    "ai_passed": ai_passed,
                    "human_passed": human_passed,
                    "ai_feedback": result.ai_score.feedback,
                    "human_feedback": result.human_score.feedback,
                }
            )

        return result_dict

    except Exception as e:
        logger.error(f"Content generation test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
        }


def run_detector_validation_test() -> bool:
    """
    Run a detector validation test to verify prompt optimization improvements.
    This tests the enhanced detection system to ensure content reads as human-written
    without try-hard traits.
    """
    print("🔍 Detector Validation Test")
    print("=" * 50)
    print("   Focus: Human-like content without try-hard traits")
    print("   Testing prompt optimization improvements")
    print()

    # Dynamically discover available section templates
    from pathlib import Path

    # Get project root and find section templates
    project_root = Path(__file__).parent
    sections_dir = project_root / "generator" / "prompts" / "sections"

    available_sections = []
    if sections_dir.exists():
        for file in sections_dir.glob("*.txt"):
            section_name = file.stem
            # Skip special files
            if section_name not in ["ai_detection_prompt", "README"]:
                available_sections.append(section_name)

    # If no sections found, fall back to basic test
    if not available_sections:
        print("⚠️ No section templates found, using basic test")
        available_sections = ["introduction"]  # fallback

    # Use first 3 available sections (or all if less than 3)
    test_sections = available_sections[:3]

    print(
        f"📂 Found {len(available_sections)} section templates: {', '.join(available_sections)}"
    )
    print(f"🎯 Testing sections: {', '.join(test_sections)}")
    print()

    # Test with different materials using available sections
    test_cases = []
    materials = ["aluminum", "silver", "copper"]

    for i, section in enumerate(test_sections):
        material = materials[i] if i < len(materials) else materials[0]
        test_cases.append(
            {
                "material": material,
                "section": section,
                "description": f"{material.title()} - {section.replace('_', ' ').title()}",
            }
        )

    all_passed = True
    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 Test Case {i}/3: {test_case['description']}")
        print("-" * 40)

        # Run with stricter thresholds to ensure human-like output
        result = run_content_test(
            material=test_case["material"],
            section=test_case["section"],
            word_limit=250,
            ai_threshold=20,  # Very strict AI detection threshold
            human_threshold=20,  # Very strict human detection threshold
            max_iterations=get_config().get_iterations_per_section(),  # More iterations to test prompt optimization
            max_tokens=5000,
        )

        success = result.get("success", False) and result.get("overall_passed", False)
        results.append({"test_case": test_case, "success": success, "result": result})

        if not success:
            all_passed = False
            print(f"❌ Test case {i} failed")
            # Show specific error if available
            if "error" in result:
                print(f"   Error: {result['error']}")
        else:
            print(f"✅ Test case {i} passed")
        print()

    # Show summary
    print("📊 Detector Validation Summary")
    print("=" * 50)

    passed_count = sum(1 for r in results if r["success"])
    print(f"Passed: {passed_count}/{len(test_cases)} test cases")

    if all_passed:
        print("🎉 All detector validation tests passed!")
        print("✅ Content successfully reads as human-written")
        print("✅ No excessive try-hard traits detected")
    else:
        print("⚠️ Some detector validation tests failed")
        print("💡 Consider adjusting detection thresholds or prompt templates")

    # Show prompt optimization stats if available
    try:
        from generator.core.services.prompt_optimizer_compatible import (
            PromptOptimizerCompatible,
        )

        optimizer = PromptOptimizerCompatible()

        print("\n📈 Prompt Optimization Performance:")
        print("-" * 35)
        report = optimizer.generate_report()
        print(report[:500] + "..." if len(report) > 500 else report)

    except Exception as e:
        print(f"\n⚠️ Could not retrieve optimization stats: {e}")

    return all_passed


if __name__ == "__main__":
    # If run directly, run detector validation test
    print("Running detector validation test...")
    success = run_detector_validation_test()
    sys.exit(0 if success else 1)
