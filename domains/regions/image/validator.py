#!/usr/bin/env python3
"""
Image Validation using Gemini Vision

Validates generated historical images against prompt requirements using
Gemini 2.0 Flash vision capabilities to ensure scale, accuracy, and quality.

Author: AI Assistant
Date: October 31, 2025
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Structured validation result"""
    passed: bool
    building_count: Optional[int] = None
    building_count_expected: Optional[str] = None
    building_count_match: Optional[bool] = None
    people_count: Optional[int] = None
    people_count_expected: Optional[str] = None
    people_count_match: Optional[bool] = None
    scale_appropriate: Optional[bool] = None
    scale_assessment: Optional[str] = None
    historical_accuracy: Optional[bool] = None
    historical_issues: Optional[List[str]] = None
    prompt_adherence: Optional[bool] = None
    prompt_issues: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    overall_assessment: Optional[str] = None
    recommendations: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_report(self) -> str:
        """Generate human-readable report"""
        lines = [
            "=" * 70,
            "🔍 IMAGE VALIDATION REPORT",
            "=" * 70,
            ""
        ]
        
        # Overall result
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines.append(f"Overall Status: {status}")
        if self.confidence_score:
            lines.append(f"Confidence: {self.confidence_score:.1%}")
        lines.append("")
        
        # Building count
        if self.building_count is not None:
            match_icon = "✅" if self.building_count_match else "❌"
            lines.append(f"{match_icon} Buildings: {self.building_count} (expected: {self.building_count_expected})")
        
        # People count
        if self.people_count is not None:
            match_icon = "✅" if self.people_count_match else "❌"
            lines.append(f"{match_icon} People: {self.people_count} (expected: {self.people_count_expected})")
        
        # Scale appropriateness
        if self.scale_appropriate is not None:
            icon = "✅" if self.scale_appropriate else "❌"
            lines.append(f"{icon} Scale: {self.scale_assessment or 'Appropriate' if self.scale_appropriate else 'Inappropriate'}")
        
        # Historical accuracy
        if self.historical_accuracy is not None:
            icon = "✅" if self.historical_accuracy else "❌"
            lines.append(f"{icon} Historical Accuracy: {'Pass' if self.historical_accuracy else 'Fail'}")
            if self.historical_issues:
                for issue in self.historical_issues:
                    lines.append(f"  ⚠️  {issue}")
        
        # Prompt adherence
        if self.prompt_adherence is not None:
            icon = "✅" if self.prompt_adherence else "❌"
            lines.append(f"{icon} Prompt Adherence: {'Pass' if self.prompt_adherence else 'Fail'}")
            if self.prompt_issues:
                for issue in self.prompt_issues:
                    lines.append(f"  ⚠️  {issue}")
        
        lines.append("")
        
        # Overall assessment
        if self.overall_assessment:
            lines.append("Assessment:")
            lines.append(f"  {self.overall_assessment}")
            lines.append("")
        
        # Recommendations
        if self.recommendations:
            lines.append("Recommendations:")
            for rec in self.recommendations:
                lines.append(f"  • {rec}")
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)


class ImageValidator:
    """
    Validates generated images using Gemini 2.0 Flash vision.
    
    Analyzes images for:
    - Building count (matches expected scale)
    - People count (matches population density)
    - Scale appropriateness (rural hamlet vs. city)
    - Historical accuracy (no anachronisms)
    - Prompt adherence (follows generation requirements)
    
    Example:
        validator = ImageValidator()
        result = validator.validate_image(
            image_path=Path("belmont_historical.png"),
            population=500,
            population_category="rural_hamlet",
            expected_buildings="1-3 simple structures",
            expected_people="2-5 visible",
            year=1918
        )
        print(result.to_report())
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize validator with Gemini vision.
        
        Args:
            api_key: Optional Gemini API key (uses GEMINI_API_KEY env var if not provided)
            model: Gemini model to use (default: gemini-2.0-flash-exp)
        """
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or provided")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        
        logger.info(f"✅ Image validator initialized with {model}")
    
    def validate_image(
        self,
        image_path: Path,
        population: int,
        population_category: str,
        expected_buildings: str,
        expected_people: str,
        year: int,
        city_name: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate generated image against expected characteristics.
        
        Args:
            image_path: Path to generated image
            population: Historical population count
            population_category: Category (rural_hamlet, small_village, etc.)
            expected_buildings: Expected building description (e.g., "1-3 simple structures")
            expected_people: Expected people description (e.g., "2-5 visible")
            year: Historical year
            city_name: Optional city name for context
            prompt: Optional generation prompt for adherence checking
            
        Returns:
            ValidationResult with detailed analysis
        """
        logger.info(f"🔍 Validating image: {image_path.name}")
        logger.info(f"📊 Expected scale: {population_category} ({population} people)")
        logger.info(f"🏘️  Expected: {expected_buildings}, {expected_people}")
        
        # Load image
        try:
            image = Image.open(image_path)
        except Exception as e:
            logger.error(f"❌ Failed to load image: {e}")
            return ValidationResult(
                passed=False,
                overall_assessment=f"Failed to load image: {e}"
            )
        
        # Build validation prompt
        validation_prompt = self._build_validation_prompt(
            population=population,
            population_category=population_category,
            expected_buildings=expected_buildings,
            expected_people=expected_people,
            year=year,
            city_name=city_name
        )
        
        # Analyze with Gemini vision
        try:
            response = self.model.generate_content([validation_prompt, image])
            analysis = self._parse_validation_response(response.text)
            
            # Build result
            result = self._build_validation_result(
                analysis=analysis,
                expected_buildings=expected_buildings,
                expected_people=expected_people,
                population_category=population_category
            )
            
            logger.info(f"{'✅' if result.passed else '❌'} Validation {'passed' if result.passed else 'failed'}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return ValidationResult(
                passed=False,
                overall_assessment=f"Validation error: {e}"
            )
    
    def _build_validation_prompt(
        self,
        population: int,
        population_category: str,
        expected_buildings: str,
        expected_people: str,
        year: int,
        city_name: Optional[str] = None
    ) -> str:
        """Build detailed validation prompt for Gemini"""
        city_context = f" in {city_name}" if city_name else ""
        
        return f"""Analyze this historical photograph from {year}{city_context}.

EXPECTED CHARACTERISTICS:
- Population: {population:,} people ({population_category})
- Buildings: {expected_buildings}
- People visible: {expected_people}
- Year: {year}

VALIDATION TASKS:
1. COUNT BUILDINGS: How many distinct buildings/structures are visible? Provide exact count.
2. COUNT PEOPLE: How many people are visible in the scene? Provide exact count.
3. ASSESS SCALE: Does the scene match a {population_category} (population {population:,})?
   - Too large/bustling for this population?
   - Too small/empty for this population?
   - Appropriate density and development?
4. CHECK HISTORICAL ACCURACY: Are there anachronisms?
   - Modern elements (contemporary cars, buildings, clothing, signs)?
   - Period-inappropriate technology?
   - Correct architectural styles for {year}?
5. EVALUATE OVERALL QUALITY:
   - Does it look like an authentic {year} photograph?
   - Are the aging effects appropriate (grain, sepia, wear)?
   - Is the composition believable?

RESPOND IN JSON FORMAT:
{{
  "building_count": <number>,
  "people_count": <number>,
  "scale_match": <true/false>,
  "scale_assessment": "<brief explanation>",
  "historical_accuracy": <true/false>,
  "anachronisms": ["<issue1>", "<issue2>", ...] or [],
  "prompt_adherence": <true/false>,
  "issues": ["<issue1>", "<issue2>", ...] or [],
  "confidence": <0.0-1.0>,
  "overall_assessment": "<2-3 sentence summary>",
  "recommendations": ["<suggestion1>", "<suggestion2>", ...] or []
}}

Be precise with counts. Compare the actual scene to what would be expected for a {population_category} of {population:,} people in {year}."""
    
    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini"""
        try:
            # Extract JSON from response (may have markdown code blocks)
            text = response_text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except Exception as e:
            logger.warning(f"⚠️  Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text}")
            
            # Return minimal result
            return {
                "building_count": None,
                "people_count": None,
                "scale_match": False,
                "scale_assessment": "Parse error",
                "historical_accuracy": False,
                "anachronisms": [],
                "prompt_adherence": False,
                "issues": [f"Failed to parse response: {e}"],
                "confidence": 0.0,
                "overall_assessment": response_text[:200] if response_text else "No response",
                "recommendations": ["Retry validation"]
            }
    
    def _build_validation_result(
        self,
        analysis: Dict[str, Any],
        expected_buildings: str,
        expected_people: str,
        population_category: str
    ) -> ValidationResult:
        """Build ValidationResult from analysis"""
        # Extract expected counts
        building_count_expected = expected_buildings
        people_count_expected = expected_people
        
        # Check if counts match expectations
        building_count = analysis.get("building_count")
        people_count = analysis.get("people_count")
        
        building_count_match = self._check_count_match(
            building_count, building_count_expected
        ) if building_count is not None else None
        
        people_count_match = self._check_count_match(
            people_count, people_count_expected
        ) if people_count is not None else None
        
        # Overall pass/fail
        passed = all([
            analysis.get("scale_match", False),
            analysis.get("historical_accuracy", False),
            analysis.get("prompt_adherence", False),
            building_count_match if building_count_match is not None else True,
            people_count_match if people_count_match is not None else True
        ])
        
        return ValidationResult(
            passed=passed,
            building_count=building_count,
            building_count_expected=building_count_expected,
            building_count_match=building_count_match,
            people_count=people_count,
            people_count_expected=people_count_expected,
            people_count_match=people_count_match,
            scale_appropriate=analysis.get("scale_match"),
            scale_assessment=analysis.get("scale_assessment"),
            historical_accuracy=analysis.get("historical_accuracy"),
            historical_issues=analysis.get("anachronisms"),
            prompt_adherence=analysis.get("prompt_adherence"),
            prompt_issues=analysis.get("issues"),
            confidence_score=analysis.get("confidence"),
            overall_assessment=analysis.get("overall_assessment"),
            recommendations=analysis.get("recommendations")
        )
    
    def _check_count_match(self, actual: int, expected: str) -> bool:
        """Check if actual count matches expected range"""
        # Parse expected range (e.g., "1-3", "2-5", "10-20")
        try:
            if "-" in expected:
                # Extract first number range in string
                import re
                match = re.search(r"(\d+)-(\d+)", expected)
                if match:
                    min_count = int(match.group(1))
                    max_count = int(match.group(2))
                    return min_count <= actual <= max_count
            
            # Single number or can't parse - be lenient
            return True
        except Exception:
            return True
    
    def validate_batch(
        self,
        image_paths: List[Path],
        population_data: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """
        Validate multiple images in batch.
        
        Args:
            image_paths: List of image paths
            population_data: List of dicts with population, category, etc.
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        for image_path, data in zip(image_paths, population_data):
            result = self.validate_image(
                image_path=image_path,
                population=data["population"],
                population_category=data["category"],
                expected_buildings=data["buildings"],
                expected_people=data["people"],
                year=data["year"],
                city_name=data.get("city")
            )
            results.append(result)
        
        return results
    
    def save_validation_report(
        self,
        result: ValidationResult,
        output_path: Path
    ):
        """Save validation report as JSON"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        
        logger.info(f"💾 Validation report saved: {output_path}")


def create_validator(api_key: Optional[str] = None) -> ImageValidator:
    """Factory function to create image validator"""
    return ImageValidator(api_key=api_key)
