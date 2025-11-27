#!/usr/bin/env python3
"""
Material Image Realism Validation using Gemini Vision

Validates material before/after laser cleaning images for:
- Contamination realism (physics, distribution, layering)
- Material appearance accuracy
- Before/after consistency
- Micro-scale authenticity

Author: AI Assistant
Date: November 25, 2025
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

import google.generativeai as genai
from PIL import Image

from shared.image.utils.prompt_builder import SharedPromptBuilder

logger = logging.getLogger(__name__)


@dataclass
class MaterialValidationResult:
    """Structured material image validation result"""
    passed: bool
    realism_score: Optional[float] = None  # 0-100
    
    # Before/After Consistency
    same_object: Optional[bool] = None
    position_shift_appropriate: Optional[bool] = None
    damage_consistent: Optional[bool] = None
    
    # Contamination Realism
    physics_compliant: Optional[bool] = None
    physics_issues: Optional[List[str]] = None
    distribution_realistic: Optional[bool] = None
    distribution_issues: Optional[List[str]] = None
    layering_natural: Optional[bool] = None
    layering_issues: Optional[List[str]] = None
    
    # Material Accuracy
    clean_side_accurate: Optional[bool] = None
    material_appearance_issues: Optional[List[str]] = None
    contamination_matches_research: Optional[bool] = None
    research_deviations: Optional[List[str]] = None
    
    # Micro-Scale Details
    micro_scale_accurate: Optional[bool] = None
    micro_scale_issues: Optional[List[str]] = None
    
    # Text/Label Detection (CRITICAL - automatic fail if present)
    text_labels_present: Optional[bool] = None
    text_label_details: Optional[List[str]] = None
    
    # Overall Assessment
    confidence_score: Optional[float] = None
    overall_assessment: Optional[str] = None
    recommendations: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_report(self) -> str:
        """Generate human-readable report"""
        lines = [
            "=" * 80,
            "🔍 MATERIAL IMAGE REALISM VALIDATION REPORT",
            "=" * 80,
            ""
        ]
        
        # Overall result
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines.append(f"Overall Status: {status}")
        if self.realism_score is not None:
            lines.append(f"Realism Score: {self.realism_score:.1f}/100")
        if self.confidence_score:
            lines.append(f"Validation Confidence: {self.confidence_score:.1%}")
        lines.append("")
        
        # Before/After Consistency
        lines.append("📋 BEFORE/AFTER CONSISTENCY:")
        if self.same_object is not None:
            icon = "✅" if self.same_object else "❌"
            lines.append(f"  {icon} Same Object: {'Yes' if self.same_object else 'No - different objects'}")
        if self.position_shift_appropriate is not None:
            icon = "✅" if self.position_shift_appropriate else "❌"
            lines.append(f"  {icon} Position Shift: {'Appropriate (5-10%)' if self.position_shift_appropriate else 'Inappropriate'}")
        if self.damage_consistent is not None:
            icon = "✅" if self.damage_consistent else "❌"
            lines.append(f"  {icon} Damage Consistency: {'Matching scratches/dents' if self.damage_consistent else 'Inconsistent damage'}")
        lines.append("")
        
        # Contamination Realism
        lines.append("🧪 CONTAMINATION REALISM:")
        if self.physics_compliant is not None:
            icon = "✅" if self.physics_compliant else "❌"
            lines.append(f"  {icon} Physics Compliance: {'Pass' if self.physics_compliant else 'Fail'}")
            if self.physics_issues:
                for issue in self.physics_issues:
                    lines.append(f"    ⚠️  {issue}")
        
        if self.distribution_realistic is not None:
            icon = "✅" if self.distribution_realistic else "❌"
            lines.append(f"  {icon} Distribution Realism: {'Natural' if self.distribution_realistic else 'Artificial'}")
            if self.distribution_issues:
                for issue in self.distribution_issues:
                    lines.append(f"    ⚠️  {issue}")
        
        if self.layering_natural is not None:
            icon = "✅" if self.layering_natural else "❌"
            lines.append(f"  {icon} Layering Authenticity: {'Natural' if self.layering_natural else 'Artificial'}")
            if self.layering_issues:
                for issue in self.layering_issues:
                    lines.append(f"    ⚠️  {issue}")
        lines.append("")
        
        # Material Accuracy
        lines.append("🔬 MATERIAL APPEARANCE:")
        if self.clean_side_accurate is not None:
            icon = "✅" if self.clean_side_accurate else "❌"
            lines.append(f"  {icon} Clean Side Accuracy: {'Correct material appearance' if self.clean_side_accurate else 'Incorrect'}")
            if self.material_appearance_issues:
                for issue in self.material_appearance_issues:
                    lines.append(f"    ⚠️  {issue}")
        
        if self.contamination_matches_research is not None:
            icon = "✅" if self.contamination_matches_research else "❌"
            lines.append(f"  {icon} Research Match: {'Matches patterns' if self.contamination_matches_research else 'Deviates'}")
            if self.research_deviations:
                for dev in self.research_deviations:
                    lines.append(f"    ⚠️  {dev}")
        lines.append("")
        
        # Micro-Scale Details
        if self.micro_scale_accurate is not None:
            lines.append("🔎 MICRO-SCALE DETAILS:")
            icon = "✅" if self.micro_scale_accurate else "❌"
            lines.append(f"  {icon} Detail Accuracy: {'Grain following, edge effects present' if self.micro_scale_accurate else 'Missing details'}")
            if self.micro_scale_issues:
                for issue in self.micro_scale_issues:
                    lines.append(f"    ⚠️  {issue}")
        
            lines.append("")
        
        # Text/Label Detection (CRITICAL)
        if self.text_labels_present is not None:
            lines.append("🚨 TEXT/LABEL DETECTION (CRITICAL):")
            if self.text_labels_present:
                lines.append(f"  ❌ TEXT/LABELS FOUND - AUTOMATIC FAIL")
                if self.text_label_details:
                    for detail in self.text_label_details:
                        lines.append(f"    ⚠️  {detail}")
            else:
                lines.append(f"  ✅ No text, labels, or annotations detected")
            lines.append("")
        
        # Overall assessment
        if self.overall_assessment:
            lines.append("📊 OVERALL ASSESSMENT:")
            lines.append(f"  {self.overall_assessment}")
            lines.append("")
        
        # Recommendations
        if self.recommendations:
            lines.append("💡 RECOMMENDATIONS:")
            for rec in self.recommendations:
                lines.append(f"  • {rec}")
            lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)


class MaterialImageValidator:
    """
    Validate material before/after laser cleaning images using Gemini Vision.
    
    Validates:
    - Contamination realism (physics, distribution, layering)
    - Material appearance accuracy
    - Before/after consistency
    - Research pattern adherence
    - Micro-scale authenticity
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize validator with Gemini API and SharedPromptBuilder.
        
        Args:
            api_key: Gemini API key (uses GEMINI_API_KEY env var if not provided)
            model: Gemini model to use (default: gemini-2.0-flash-exp)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        
        # Initialize shared prompt builder for validation prompts
        from shared.image.utils.prompt_builder import SharedPromptBuilder
        self.prompt_builder = SharedPromptBuilder()
        
        logger.info(f"✅ Material image validator initialized with {model}")
    
    def validate_material_image(
        self,
        image_path: Path,
        material_name: str,
        research_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        reference_image_urls: Optional[List[str]] = None
    ) -> MaterialValidationResult:
        """
        Validate material before/after image for realism and accuracy.
        
        Args:
            image_path: Path to generated image
            material_name: Material name (e.g., "Aluminum", "Steel")
            research_data: Research data used for generation
            config: Optional generation config (contamination level, uniformity, etc.)
            reference_image_urls: Optional list of reference image URLs for comparison
            
        Returns:
            MaterialValidationResult with detailed validation metrics
        """
        # Load image
        image = Image.open(image_path)
        
        # Extract reference URLs from research data if not provided
        if reference_image_urls is None:
            reference_image_urls = self._extract_reference_urls(research_data)
        
        # Build validation prompt with reference comparison
        validation_prompt = self._build_material_validation_prompt(
            material_name=material_name,
            research_data=research_data,
            config=config,
            reference_image_urls=reference_image_urls
        )
        
        # Analyze with Gemini vision (multi-image if references available)
        if reference_image_urls:
            # Multi-image comparison: generated + references
            logger.info(f"🔍 Validating with {len(reference_image_urls)} reference images")
            content_parts = [validation_prompt, image]
            # Note: Reference URLs would be loaded here in full implementation
            # For now, we pass URLs in prompt for LLM to consider
            response = self.model.generate_content(content_parts)
        else:
            # Single image validation (original behavior)
            response = self.model.generate_content([validation_prompt, image])
        
        # Parse response - will raise ValueError if invalid JSON
        analysis = self._parse_validation_response(response.text)
        
        # Build result - will raise ValueError if missing required fields
        result = self._build_validation_result(analysis)
        
        logger.info(f"{'✅' if result.passed else '❌'} Validation {'passed' if result.passed else 'failed'} "
                   f"(realism: {result.realism_score:.1f}/100)")
        return result
    
    def _extract_reference_urls(self, research_data: Dict[str, Any]) -> List[str]:
        """Extract reference image URLs from research data."""
        urls = []
        patterns = research_data.get('contamination_patterns', [])
        
        for pattern in patterns:
            pattern_urls = pattern.get('photo_reference_urls', [])
            if isinstance(pattern_urls, list):
                urls.extend(pattern_urls)
        
        # Limit to first 3 reference images to avoid token limits
        return urls[:3] if urls else []
    
    def _build_reference_comparison_section(self, reference_urls: List[str]) -> str:
        """Build prompt section for reference image comparison."""
        section = [
            "\n" + "="*80,
            "📸 REFERENCE IMAGE COMPARISON (CRITICAL)",
            "="*80,
            "",
            "Compare the GENERATED image against these ACTUAL MATERIAL PHOTOS:",
            ""
        ]
        
        for i, url in enumerate(reference_urls, 1):
            section.append(f"{i}. Reference: {url}")
        
        section.extend([
            "",
            "Validation Questions:",
            "1. Surface Texture Match: Does contamination texture match reference photos?",
            "2. Color Accuracy: Are colors consistent with documented examples?",
            "3. Distribution Realism: Does pattern distribution match actual photos?",
            "4. Damage Authenticity: Is structural damage consistent with real aging?",
            "5. Lighting/Material Response: Does light interaction match references?",
            "",
            "CRITICAL: Flag ANY details in generated image not seen in reference photos.",
            "If generated image shows patterns/damage not present in ANY reference → FAIL.",
            "",
            "="*80
        ])
        
        return "\n".join(section)
    
    def _build_material_validation_prompt(
        self,
        material_name: str,
        research_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        reference_image_urls: Optional[List[str]] = None
    ) -> str:
        """Build comprehensive validation prompt using shared templates."""
        # Get learned feedback for this category
        learned_feedback = None
        if config and 'category' in config:
            try:
                from shared.image.learning import create_logger
                learning_logger = create_logger()
                learned_feedback = learning_logger.get_category_feedback(
                    material_category=config['category'],
                    limit=5  # Top 5 most common issues
                )
                if learned_feedback:
                    logger.info(f"🧠 Loaded learned feedback for validation of {config['category']}")
            except Exception as e:
                logger.debug(f"Could not load learned feedback: {e}")
        
        base_prompt = self.prompt_builder.build_validation_prompt(
            material_name=material_name,
            research_data=research_data,
            config=config,
            material_category=config.get('category') if config else None,
            learned_feedback=learned_feedback
        )
        
        # Add reference image comparison if URLs provided
        if reference_image_urls:
            reference_section = self._build_reference_comparison_section(reference_image_urls)
            return f"{base_prompt}\n\n{reference_section}"
        
        return base_prompt
    
    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini - FAIL FAST if invalid"""
        logger.debug(f"📝 Raw Gemini response length: {len(response_text)} chars")
        logger.debug(f"📝 First 500 chars: {response_text[:500]}")
        
        # Extract JSON from response (may have markdown code blocks)
        text = response_text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        try:
            parsed = json.loads(text)
            logger.debug(f"✅ Successfully parsed JSON with keys: {list(parsed.keys())}")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse validation response as JSON")
            logger.error(f"📄 Response text (first 1000 chars):\n{response_text[:1000]}")
            logger.error(f"Parse error: {e}")
            raise ValueError(
                f"Gemini validation response is not valid JSON. "
                f"This likely means the validation prompt was truncated or malformed. "
                f"Response length: {len(response_text)} chars. "
                f"Parse error: {e}"
            )
    
    def _build_validation_result(self, analysis: Dict[str, Any]) -> MaterialValidationResult:
        """Build structured validation result from analysis"""
        # Calculate pass/fail - fail fast if score missing
        if "realism_score" not in analysis:
            raise ValueError("Validation analysis missing required 'realism_score' field")
        realism_score = analysis["realism_score"]
        
        # Check for text/labels - AUTOMATIC FAIL if present
        text_labels_present = analysis.get("text_labels_present", False)
        
        passed = (
            realism_score >= 75.0 and
            analysis.get("physics_compliant", False) and
            analysis.get("distribution_realistic", False) and
            analysis.get("same_object", False) and
            not text_labels_present  # AUTOMATIC FAIL if text/labels detected
        )
        
        return MaterialValidationResult(
            passed=passed,
            realism_score=realism_score,
            same_object=analysis.get("same_object"),
            position_shift_appropriate=analysis.get("position_shift_appropriate"),
            damage_consistent=analysis.get("damage_consistent"),
            physics_compliant=analysis.get("physics_compliant"),
            physics_issues=analysis.get("physics_issues", []),
            distribution_realistic=analysis.get("distribution_realistic"),
            distribution_issues=analysis.get("distribution_issues", []),
            layering_natural=analysis.get("layering_natural"),
            layering_issues=analysis.get("layering_issues", []),
            clean_side_accurate=analysis.get("clean_side_accurate"),
            material_appearance_issues=analysis.get("material_appearance_issues", []),
            contamination_matches_research=analysis.get("contamination_matches_research"),
            research_deviations=analysis.get("research_deviations", []),
            micro_scale_accurate=analysis.get("micro_scale_accurate"),
            micro_scale_issues=analysis.get("micro_scale_issues", []),
            text_labels_present=text_labels_present,
            text_label_details=analysis.get("text_label_details", []),
            confidence_score=analysis.get("confidence"),
            overall_assessment=analysis.get("overall_assessment"),
            recommendations=analysis.get("recommendations", [])
        )


def create_validator(api_key: Optional[str] = None) -> MaterialImageValidator:
    """Factory function to create material image validator"""
    return MaterialImageValidator(api_key=api_key)
