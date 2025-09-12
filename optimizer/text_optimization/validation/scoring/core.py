"""
Content Quality Scoring - Core Module

Main ContentQualityScorer class providing comprehensive content evaluation
and coordination of specialized validators.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .formatting_validator import FormattingValidator
from .persona_validators import PersonaValidators
from .readability_metrics import ReadabilityMetrics

logger = logging.getLogger(__name__)


@dataclass
class ContentScoreResult:
    """Result of content quality scoring."""

    overall_score: float
    formatting_score: float
    technical_score: float
    authenticity_score: float
    readability_score: float
    believability_score: float
    details: Dict[str, Any]


class ContentQualityScorer:
    """
    Comprehensive content quality scorer for evaluating generated content
    against multiple criteria for human believability.
    """

    def __init__(self, human_threshold: float = 75.0):
        """
        Initialize the content quality scorer.

        Args:
            human_threshold: Minimum score required to pass human believability test
        """
        self.human_threshold = human_threshold
        self.author_markers = self._load_author_markers()
        self.technical_terms = self._load_technical_terms()
        
        # Initialize validators
        self.formatting_validator = FormattingValidator()
        self.persona_validators = PersonaValidators(self.author_markers)
        self.readability_metrics = ReadabilityMetrics()

    def _load_author_markers(self) -> Dict[str, List[str]]:
        """Load author linguistic markers from persona files."""
        markers = {}
        persona_dir = Path("optimizer/text_optimization/prompts/personas")

        for persona_file in persona_dir.glob("*_persona.yaml"):
            country = persona_file.stem.replace("_persona", "")
            try:
                import yaml

                with open(persona_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                # Extract signature phrases and language patterns
                language_patterns = data.get("language_patterns", {})
                signature_phrases = language_patterns.get("signature_phrases", [])
                
                # Combine markers
                markers[country] = signature_phrases

            except Exception as e:
                logger.warning(f"Failed to load persona markers for {country}: {e}")
                markers[country] = []

        return markers

    def _load_technical_terms(self) -> List[str]:
        """Load technical terminology for content analysis."""
        return [
            "laser", "cleaning", "material", "surface", "removal", "ablation",
            "thermal", "processing", "precision", "efficiency", "wavelength",
            "power", "density", "pulse", "beam", "optical", "interaction",
            "mechanism", "parameter", "optimization", "application", "industrial",
        ]

    def score_content(
        self,
        content: str,
        material_data: Dict[str, Any],
        author_info: Dict[str, Any],
    ) -> ContentScoreResult:
        """
        Score content quality across multiple dimensions.

        Args:
            content: Generated content to score
            material_data: Material information
            author_info: Author information

        Returns:
            ContentScoreResult with detailed scoring breakdown
        """
        # Calculate individual scores using validators
        formatting_score = self.formatting_validator.score_formatting(content)
        technical_score = self._score_technical_accuracy(content, material_data)
        authenticity_score = self.persona_validators.score_author_authenticity(content, author_info)
        readability_score = self.readability_metrics.score_readability(content)
        believability_score = self._score_human_believability(content, author_info)

        # Calculate overall score
        required_elements = self._check_required_elements(content, material_data, author_info)
        overall_score = self._calculate_overall_score(
            formatting_score, technical_score, authenticity_score,
            readability_score, believability_score, required_elements,
        )

        return ContentScoreResult(
            overall_score=overall_score,
            formatting_score=formatting_score,
            technical_score=technical_score,
            authenticity_score=authenticity_score,
            readability_score=readability_score,
            believability_score=believability_score,
            details={
                "required_elements": required_elements,
                "word_count": len(self.readability_metrics.extract_words(content)),
                "author_country": author_info.get("country", ""),
            },
        )

    def _score_technical_accuracy(self, content: str, material_data: Dict[str, Any]) -> float:
        """Score technical accuracy (0-100)."""
        score = 0.0
        content_lower = content.lower()

        # Material-specific terms (40 points)
        material_name = material_data.get("name", "").lower()
        if material_name and material_name in content_lower:
            score += 40

        # Technical terminology usage (30 points)
        technical_count = sum(1 for term in self.technical_terms if term in content_lower)
        if technical_count >= 3:
            score += 30
        elif technical_count >= 1:
            score += 15

        # Process parameters (30 points)
        if any(param in content_lower for param in ["temperature", "speed", "power", "wavelength"]):
            score += 30

        return min(score, 100.0)

    def _score_human_believability(self, content: str, author_info: Dict[str, Any]) -> float:
        """Score human believability factors (0-100)."""
        score = 0.0

        # Natural language patterns (30 points)
        if self._has_natural_language_patterns(content):
            score += 30

        # Personal perspective markers (25 points)
        if self._has_personal_perspective(content):
            score += 25

        # Expertise demonstration (25 points)
        if self._demonstrates_expertise(content, author_info):
            score += 25

        # Cultural authenticity (20 points)
        if self._shows_cultural_authenticity(content, author_info):
            score += 20

        return min(score, 100.0)

    def _has_natural_language_patterns(self, content: str) -> bool:
        """Check for natural language patterns that indicate human writing."""
        natural_patterns = [
            "i think", "in my opinion", "i believe", "from my experience",
            "however", "although", "while", "despite", "therefore", "thus",
            "for instance", "for example", "such as", "particularly"
        ]
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in natural_patterns)

    def _has_personal_perspective(self, content: str) -> bool:
        """Check for personal perspective indicators."""
        personal_markers = [
            "i've", "i'm", "my", "our", "we", "us", "in my view",
            "personally", "from what i've seen", "based on my"
        ]
        content_lower = content.lower()
        return any(marker in content_lower for marker in personal_markers)

    def _demonstrates_expertise(self, content: str, author_info: Dict[str, Any]) -> bool:
        """Check if content demonstrates relevant expertise."""
        expertise_markers = [
            "technical", "professional", "industrial", "commercial",
            "research", "development", "analysis", "evaluation"
        ]
        content_lower = content.lower()
        return any(marker in content_lower for marker in expertise_markers)

    def _shows_cultural_authenticity(self, content: str, author_info: Dict[str, Any]) -> bool:
        """Check for cultural authenticity markers."""
        country = author_info.get("country", "").lower()
        if country and country in self.author_markers:
            markers = self.author_markers[country]
            content_lower = content.lower()
            return any(marker.lower() in content_lower for marker in markers)
        return False

    def _check_required_elements(
        self, content: str, material_data: Dict[str, Any], author_info: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check for required content elements."""
        return {
            "has_title": content.startswith("#"),
            "has_sections": "##" in content,
            "has_material_reference": material_data.get("name", "").lower() in content.lower(),
            "has_technical_content": any(term in content.lower() for term in self.technical_terms),
            "adequate_length": len(content.split()) >= 100,
        }

    def _calculate_overall_score(
        self,
        formatting_score: float,
        technical_score: float,
        authenticity_score: float,
        readability_score: float,
        believability_score: float,
        required_elements: Dict[str, bool],
    ) -> float:
        """Calculate weighted overall score."""
        # Weight the component scores
        weighted_score = (
            formatting_score * 0.15 +
            technical_score * 0.25 +
            authenticity_score * 0.25 +
            readability_score * 0.20 +
            believability_score * 0.15
        )

        # Apply penalties for missing required elements
        required_count = sum(required_elements.values())
        total_required = len(required_elements)
        completeness_factor = required_count / total_required if total_required > 0 else 1.0

        final_score = weighted_score * completeness_factor
        return min(final_score, 100.0)
