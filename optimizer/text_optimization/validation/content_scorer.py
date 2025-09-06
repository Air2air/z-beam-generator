#!/usr/bin/env python3
"""
Content Quality Scoring System
Provides comprehensive scoring for content component generation to ensure
100% believable human-generated content with detailed human readability metrics.
"""

import logging
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import statistics
from optimizer.ai_detection.config import AI_DETECTION_CONFIG


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
                writing_style = data.get("writing_style", {})

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
            "mechanism", "parameter", "optimization", "application", "industrial"
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
        # Calculate individual scores
        formatting_score = self._score_formatting(content)
        technical_score = self._score_technical_accuracy(content, material_data)
        authenticity_score = self._score_author_authenticity(content, author_info)
        readability_score = self._score_readability(content)
        believability_score = self._score_human_believability(content, author_info)

        # Calculate overall score
        required_elements = self._check_required_elements(content, material_data, author_info)
        overall_score = self._calculate_overall_score(
            formatting_score, technical_score, authenticity_score,
            readability_score, believability_score, required_elements
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
                "word_count": len(self._extract_words(content)),
                "author_country": author_info.get("country", ""),
            }
        )

    def _score_formatting(self, content: str) -> float:
        """Score content formatting (0-100)."""
        score = 0.0

        # Title presence (20 points)
        if content.startswith("#"):
            score += 20

        # Section structure (30 points)
        if "##" in content:
            score += 30

        # Technical formatting (25 points)
        if "**" in content:  # Bold text
            score += 25

        # List formatting (25 points)
        if any(marker in content for marker in ["•", "-", "* "]):
            score += 25

        return min(score, 100.0)

    def _score_technical_accuracy(self, content: str, material_data: Dict[str, Any]) -> float:
        """Score technical accuracy (0-100)."""
        score = 0.0
        content_lower = content.lower()

        # Technical term density (40 points)
        tech_terms_found = sum(1 for term in self.technical_terms if term in content_lower)
        tech_density = tech_terms_found / len(self._extract_words(content)) if content else 0
        score += min(tech_density * 1000, 40)  # Optimal: 4-8% technical density

        # Material-specific content (30 points)
        material_name = material_data.get("name", "").lower()
        if material_name in content_lower:
            score += 30

        # Formula presence (30 points)
        formula = material_data.get("formula") or material_data.get("chemical_formula")
        if formula and formula in content:
            score += 30

        return min(score, 100.0)

    def _score_author_authenticity(self, content: str, author_info: Dict[str, Any]) -> float:
        """Score author authenticity based on linguistic patterns (0-100)."""
        content_lower = content.lower()
        words = self._extract_words(content)
        word_count = len(words)

        # Get word count penalty
        min_word_counts = AI_DETECTION_CONFIG["word_count_limits"]

        # Map country names to config keys
        country_key_map = {
            "italy": "italy",
            "taiwan": "taiwan",
            "indonesia": "indonesia",
            "united states": "usa",
            "united states (california)": "usa",
        }

        country = author_info.get("country", "").lower()
        config_key = country_key_map.get(country, "taiwan")  # Default to taiwan
        min_words = min_word_counts.get(config_key, {}).get("max", 350)
        if word_count < min_words:
            # Severe penalty for insufficient content
            word_penalty = max(0, (min_words - word_count) / min_words * 50)
            logger.warning(
                f"Word count penalty: {word_penalty:.1f} points for {word_count}/{min_words} words"
            )
        else:
            word_penalty = 0

        score = 0.0

        if "italy" in country:
            # Enhanced Italian persona validation
            score += self._score_italian_persona(content, content_lower, words)
        elif "taiwan" in country:
            # Enhanced Taiwan persona validation
            score += self._score_taiwan_persona(content, content_lower, words)
        elif "indonesia" in country:
            # Enhanced Indonesia persona validation
            score += self._score_indonesia_persona(content, content_lower, words)
        elif "united states" in country:
            # Enhanced USA persona validation
            score += self._score_usa_persona(content, content_lower, words)
        else:
            logger.warning(f"Unknown country for authenticity scoring: {country}")
            return 20.0  # Base score for unknown countries

        # Apply word count penalty
        final_score = max(0, score - word_penalty)

        logger.info(
            f"Author authenticity: {final_score:.1f}/100 (country: {country}, words: {word_count})"
        )
        return min(final_score, 100.0)

    def _score_italian_persona(
        self, content: str, content_lower: str, words: list
    ) -> float:
        """Score Italian academic persona with authentic linguistic pattern detection."""
        score = 0.0

        # Italian linguistic nuances (30 points)
        # Look for complex sentence structures and logical connectors
        italian_connectors = [
            "therefore",
            "consequently",
            "furthermore",
            "moreover",
            "however",
            "in addition",
            "as a result",
            "on the other hand",
        ]
        connector_count = sum(1 for conn in italian_connectors if conn in content_lower)
        score += min(connector_count * 4, 20)

        # Technical precision phrasing (25 points)
        precision_phrases = [
            "technical precision requires",
            "engineering analysis shows",
            "methodical approach",
            "systematic investigation",
            "comprehensive analysis",
            "precision engineering",
            "technical innovation",
            "manufacturing excellence",
        ]
        precision_count = sum(
            1 for phrase in precision_phrases if phrase in content_lower
        )
        score += min(precision_count * 5, 25)

        # Heritage/manufacturing focus (20 points)
        heritage_terms = [
            "heritage",
            "preservation",
            "manufacturing",
            "additive",
            "aerospace",
            "automotive",
            "archaeological",
            "historical",
            "precision",
            "excellence",
        ]
        heritage_count = sum(1 for term in heritage_terms if term in content_lower)
        score += min(heritage_count * 3, 20)

        # Structured technical organization (25 points)
        structure_indicators = [
            content.count("**") >= 8,  # Bold technical terms
            "overview" in content_lower and "applications" in content_lower,
            "parameters" in content_lower and "advantages" in content_lower,
            content.count("#") >= 4,  # Clear section structure
        ]
        structure_score = sum(6 for indicator in structure_indicators if indicator)
        score += min(structure_score, 25)

        return score

    def _score_taiwan_persona(
        self, content: str, content_lower: str, words: list
    ) -> float:
        """Score Taiwan academic persona with authentic linguistic pattern detection."""
        score = 0.0

        # Question-based exploration patterns (25 points)
        taiwanese_questions = [
            "what if we consider",
            "what if",
            "as we continue",
            "systematic approach",
            "careful analysis",
            "methodical investigation",
            "step-by-step",
        ]
        question_count = sum(
            1 for phrase in taiwanese_questions if phrase in content_lower
        )
        score += min(question_count * 5, 25)

        # Article omissions and simplified structures (20 points)
        # Look for patterns that might indicate Mandarin influence
        simplified_indicators = [
            content_lower.count(" the ")
            < len(words) * 0.08,  # Fewer articles than typical
            content.count("(") >= 4,  # Technical specs in parentheses
            "material" in content_lower
            and content_lower.count("the material")
            < content_lower.count("material") * 0.5,
        ]
        simplified_score = sum(7 for indicator in simplified_indicators if indicator)
        score += min(simplified_score, 20)

        # Systematic methodology emphasis (30 points)
        systematic_terms = [
            "systematic",
            "methodical",
            "comprehensive",
            "analysis",
            "investigation",
            "research",
            "study",
            "examination",
            "evaluation",
            "assessment",
        ]
        systematic_count = sum(1 for term in systematic_terms if term in content_lower)
        score += min(systematic_count * 3, 30)

        # Electronics/semiconductor context (25 points)
        tech_context = [
            "semiconductor",
            "electronics",
            "processing",
            "manufacturing",
            "precision",
            "thermal",
            "silicon",
            "substrate",
            "component",
            "technical",
        ]
        tech_count = sum(1 for term in tech_context if term in content_lower)
        score += min(tech_count * 3, 25)

        return score

    def _score_indonesia_persona(
        self, content: str, content_lower: str, words: list
    ) -> float:
        """Score Indonesia academic persona with enhanced repetition and analysis detection."""
        score = 0.0

        # Repetitive emphasis patterns (40 points) - This is critical for Indonesian style
        repetition_score = 0

        # Check for repetitive important/vital/critical phrases
        important_variations = [
            "important",
            "vital",
            "critical",
            "essential",
            "significant",
        ]
        repetitive_phrases = []
        for term in important_variations:
            count = content_lower.count(term)
            if count >= 2:
                repetition_score += count * 5
                repetitive_phrases.append(f"{term}({count}x)")

        # Check for "very important", "most important" patterns
        if "very important" in content_lower:
            repetition_score += 10
        if "most important" in content_lower:
            repetition_score += 10

        # Check for repeated analytical phrases
        analytical_repeats = [
            "analysis shows",
            "we can see",
            "it is clear",
            "this demonstrates",
            "the results indicate",
            "this is important",
        ]
        for phrase in analytical_repeats:
            if content_lower.count(phrase) >= 2:
                repetition_score += 8

        score += min(repetition_score, 40)
        logger.info(
            f"Indonesia repetition score: {min(repetition_score, 40)}/40 - phrases: {repetitive_phrases}"
        )

        # Thorough analytical approach (25 points)
        analytical_terms = [
            "analysis",
            "examine",
            "investigate",
            "evaluate",
            "assess",
            "study",
            "research",
            "observation",
            "findings",
            "results",
        ]
        analytical_count = sum(1 for term in analytical_terms if term in content_lower)
        score += min(analytical_count * 3, 25)

        # Environmental/community context (20 points)
        community_terms = [
            "environment",
            "community",
            "sustainable",
            "affordable",
            "practical",
            "implementation",
            "society",
            "local",
            "region",
            "marine",
            "humid",
        ]
        community_count = sum(1 for term in community_terms if term in content_lower)
        score += min(community_count * 4, 20)

        # Formal academic structure (15 points)
        formal_indicators = [
            content.count("##") >= 3,  # Multiple subsections
            "overview" in content_lower,
            "parameters" in content_lower,
            "applications" in content_lower,
        ]
        formal_score = sum(4 for indicator in formal_indicators if indicator)
        score += min(formal_score, 15)

        return score

    def _score_usa_persona(
        self, content: str, content_lower: str, words: list
    ) -> float:
        """Score USA academic persona with enhanced detection."""
        score = 0.0

        # Conversational/accessible language (30 points)
        conversational_terms = [
            "let's",
            "we're",
            "you're",
            "imagine",
            "consider this",
            "think about",
            "what's",
            "here's",
            "that's",
            "it's",
            "can't",
            "don't",
            "won't",
        ]
        conversational_count = sum(
            1 for term in conversational_terms if term in content_lower
        )
        score += min(conversational_count * 4, 30)

        # Optimistic/forward-looking language (25 points)
        optimistic_terms = [
            "innovation",
            "breakthrough",
            "cutting-edge",
            "advanced",
            "revolutionary",
            "promising",
            "exciting",
            "potential",
            "opportunity",
            "future",
        ]
        optimistic_count = sum(1 for term in optimistic_terms if term in content_lower)
        score += min(optimistic_count * 4, 25)

        # Direct communication style (25 points)
        direct_indicators = [
            content.count("!") >= 1,  # Exclamation for emphasis
            any(
                phrase in content_lower
                for phrase in ["bottom line", "key point", "simply put"]
            ),
            content.count("However,") >= 1 or content.count("But") >= 1,
            len([s for s in content.split(".") if len(s.split()) <= 15])
            >= 3,  # Short, direct sentences
        ]
        direct_score = sum(6 for indicator in direct_indicators if indicator)
        score += min(direct_score, 25)

        # Practical application focus (20 points)
        practical_terms = [
            "practical",
            "real-world",
            "industry",
            "commercial",
            "cost-effective",
            "efficient",
            "scalable",
            "implementation",
            "production",
            "market",
        ]
        practical_count = sum(1 for term in practical_terms if term in content_lower)
        score += min(practical_count * 3, 20)

        return score

    def _score_readability(self, content: str) -> float:
        """Score content readability using multiple metrics (0-100)."""
        try:
            # Calculate readability metrics
            sentences = self._split_sentences(content)
            words = self._extract_words(content)

            if not sentences or not words:
                return 0.0

            # Average sentence length (optimal: 15-25 words)
            avg_sentence_length = len(words) / len(sentences)
            sentence_score = self._score_sentence_length(avg_sentence_length)

            # Vocabulary diversity (unique words / total words)
            unique_words = set(word.lower() for word in words)
            diversity = len(unique_words) / len(words) if words else 0
            diversity_score = min(diversity * 150, 100)  # Scale to 0-100

            # Paragraph structure (optimal: 3-6 paragraphs)
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            paragraph_score = self._score_paragraph_count(len(paragraphs))

            # Technical complexity balance
            complexity_score = self._score_technical_complexity(content)

            # Weighted average
            readability_score = (
                sentence_score * 0.3
                + diversity_score * 0.3
                + paragraph_score * 0.2
                + complexity_score * 0.2
            )

            return min(readability_score, 100.0)

        except Exception as e:
            logger.error(f"Error calculating readability: {e}")
            raise ValueError(f"Readability calculation failed: {e}") from e

    def _score_human_believability(
        self, content: str, author_info: Dict[str, Any]
    ) -> float:
        """Score overall human believability (0-100)."""
        score = 0.0

        # Natural language flow (25 points)
        flow_score = self._score_language_flow(content)
        score += flow_score * 0.25

        # Coherent structure (25 points)
        structure_score = self._score_content_structure(content)
        score += structure_score * 0.25

        # Appropriate complexity (25 points)
        complexity_score = self._score_appropriate_complexity(content)
        score += complexity_score * 0.25

        # Human-like variability (25 points)
        variability_score = self._score_human_variability(content)
        score += variability_score * 0.25

        return min(score, 100.0)

    def _calculate_content_metrics(self, content: str) -> Dict[str, float]:
        """Calculate detailed content metrics."""
        sentences = self._split_sentences(content)
        words = self._extract_words(content)
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)

        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Vocabulary diversity
        unique_words = set(word.lower() for word in words)
        vocabulary_diversity = len(unique_words) / word_count if word_count > 0 else 0

        # Technical density
        technical_words = sum(
            1 for word in words if word.lower() in self.technical_terms
        )
        technical_density = technical_words / word_count if word_count > 0 else 0

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "avg_sentence_length": avg_sentence_length,
            "vocabulary_diversity": vocabulary_diversity,
            "technical_density": technical_density,
        }

    def _check_required_elements(
        self, content: str, material_data: Dict[str, Any], author_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for required content elements."""
        elements = {
            "has_title": content.startswith("#"),
            "has_author": author_info.get("name", "") in content,
            "has_material": material_data.get("name", "") in content,
            "has_formula": any(
                formula in content
                for formula in [
                    material_data.get("formula", ""),
                    material_data.get("chemical_formula", ""),
                ]
                if formula
            ),
            "has_technical_content": any(
                term in content.lower() for term in self.technical_terms
            ),
            "has_sections": "##" in content,
        }

        elements["all_present"] = all(elements.values())
        elements["present_count"] = sum(elements.values())
        elements["total_count"] = len(
            [
                k
                for k in elements.keys()
                if k not in ["all_present", "present_count", "total_count"]
            ]
        )

        return elements

    def _calculate_overall_score(
        self,
        formatting: float,
        technical: float,
        authenticity: float,
        readability: float,
        believability: float,
        required_elements: Dict,
    ) -> float:
        """Calculate weighted overall score."""
        # Base weighted score
        base_score = (
            believability * 0.30
            + technical * 0.25  # Most important: human believability
            + authenticity * 0.20  # Technical accuracy
            + readability * 0.15  # Author authenticity
            + formatting * 0.10  # Readability  # Formatting
        )

        # Penalty for missing required elements
        required_ratio = required_elements.get(
            "present_count", 0
        ) / required_elements.get("total_count", 1)
        element_penalty = (1 - required_ratio) * 20  # Up to 20 point penalty

        overall_score = max(base_score - element_penalty, 0.0)
        return min(overall_score, 100.0)

    # Helper methods for detailed scoring
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on periods, exclamation marks, question marks
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text."""
        # Extract words (alphanumeric sequences)
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text)
        return words

    def _score_sentence_length(self, avg_length: float) -> float:
        """Score average sentence length (optimal: 15-25 words)."""
        if 15 <= avg_length <= 25:
            return 100.0
        elif 10 <= avg_length < 15 or 25 < avg_length <= 30:
            return 80.0
        elif 5 <= avg_length < 10 or 30 < avg_length <= 35:
            return 60.0
        else:
            return 40.0

    def _score_paragraph_count(self, count: int) -> float:
        """Score paragraph count (optimal: 3-6 paragraphs)."""
        if 3 <= count <= 6:
            return 100.0
        elif count == 2 or count == 7:
            return 80.0
        elif count == 1 or count == 8:
            return 60.0
        else:
            return 40.0

    def _score_technical_complexity(self, content: str) -> float:
        """Score appropriate technical complexity."""
        content_lower = content.lower()

        # Count technical terms
        tech_terms = sum(1 for term in self.technical_terms if term in content_lower)

        # Count total words
        words = len(self._extract_words(content))

        if words == 0:
            return 0.0

        # Calculate technical density (optimal: 5-15%)
        tech_density = tech_terms / words

        if 0.05 <= tech_density <= 0.15:
            return 100.0
        elif 0.03 <= tech_density < 0.05 or 0.15 < tech_density <= 0.20:
            return 80.0
        else:
            return 60.0

    def _score_language_flow(self, content: str) -> float:
        """Score natural language flow."""
        # Check for transition words and phrases
        transitions = [
            "however",
            "therefore",
            "furthermore",
            "additionally",
            "consequently",
            "moreover",
            "nevertheless",
            "meanwhile",
            "specifically",
            "particularly",
        ]

        content_lower = content.lower()
        transition_count = sum(1 for trans in transitions if trans in content_lower)

        # Score based on presence of transitions
        if transition_count >= 3:
            return 100.0
        elif transition_count >= 2:
            return 80.0
        elif transition_count >= 1:
            return 60.0
        else:
            return 40.0

    def _score_content_structure(self, content: str) -> float:
        """Score logical content structure."""
        score = 0.0

        # Check for title (25 points)
        if content.startswith("#"):
            score += 25

        # Check for author byline (25 points)
        if re.search(r"\*\*.*Ph\.D.*\*\*", content):
            score += 25

        # Check for section headers (25 points)
        if "##" in content:
            score += 25

        # Check for logical flow (introduction -> details -> conclusion) (25 points)
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if len(paragraphs) >= 3:
            score += 25

        return score

    def _score_appropriate_complexity(self, content: str) -> float:
        """Score appropriate complexity for technical content."""
        words = self._extract_words(content)

        if not words:
            return 0.0

        # Calculate average word length (complexity indicator)
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Technical content should have moderate complexity (5-7 chars avg)
        if 5 <= avg_word_length <= 7:
            return 100.0
        elif 4 <= avg_word_length < 5 or 7 < avg_word_length <= 8:
            return 80.0
        else:
            return 60.0

    def _score_human_variability(self, content: str) -> float:
        """Score human-like variability in writing."""
        sentences = self._split_sentences(content)

        if len(sentences) < 3:
            return 50.0

        # Calculate sentence length variability
        sentence_lengths = [
            len(self._extract_words(sentence)) for sentence in sentences
        ]

        if len(sentence_lengths) < 2:
            return 50.0

        # Higher standard deviation indicates more variability (human-like)
        std_dev = statistics.stdev(sentence_lengths)
        mean_length = statistics.mean(sentence_lengths)

        # Coefficient of variation (std_dev / mean)
        if mean_length > 0:
            cv = std_dev / mean_length
            # Good variability: 0.3-0.7
            if 0.3 <= cv <= 0.7:
                return 100.0
            elif 0.2 <= cv < 0.3 or 0.7 < cv <= 0.8:
                return 80.0
            else:
                return 60.0

        return 50.0

    # Detail methods for breakdown reporting
    def _get_formatting_details(self, content: str) -> Dict[str, Any]:
        """Get detailed formatting analysis."""
        return {
            "has_title": content.startswith("#"),
            "has_sections": "##" in content,
            "has_bold_text": "**" in content,
            "has_author_byline": bool(re.search(r"\*\*.*Ph\.D.*\*\*", content)),
            "paragraph_count": len([p for p in content.split("\n\n") if p.strip()]),
            "has_lists": bool(
                re.search(r"[•\-\*]\s+|^\d+\.\s+", content, re.MULTILINE)
            ),
        }

    def _get_technical_details(
        self, content: str, material_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get detailed technical analysis."""
        content_lower = content.lower()
        technical_terms_found = [
            term for term in self.technical_terms if term in content_lower
        ]

        return {
            "formula_present": any(
                formula in content
                for formula in [
                    material_data.get("formula", ""),
                    material_data.get("chemical_formula", ""),
                ]
                if formula
            ),
            "technical_terms_found": technical_terms_found,
            "technical_term_count": len(technical_terms_found),
            "technical_density": len(technical_terms_found)
            / len(self._extract_words(content))
            if self._extract_words(content)
            else 0,
        }

    def _get_authenticity_details(
        self, content: str, author_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get detailed authenticity analysis."""
        content_lower = content.lower()
        author_country = author_info.get("country", "").lower()

        country_mapping = {
            "taiwan": "taiwan",
            "italy": "italy",
            "indonesia": "indonesia",
            "united states": "usa",
            "united states (california)": "usa",
        }

        marker_key = country_mapping.get(author_country, "usa")
        expected_markers = self.author_markers.get(marker_key, [])
        found_markers = [
            marker for marker in expected_markers if marker in content_lower
        ]

        return {
            "author_name_present": author_info.get("name", "") in content,
            "country_present": author_info.get("country", "") in content,
            "expected_linguistic_markers": expected_markers,
            "found_linguistic_markers": found_markers,
            "marker_match_ratio": len(found_markers) / len(expected_markers)
            if expected_markers
            else 0,
        }

    def _get_readability_details(self, content: str) -> Dict[str, Any]:
        """Get detailed readability analysis."""
        sentences = self._split_sentences(content)
        words = self._extract_words(content)

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "vocabulary_diversity": len(set(word.lower() for word in words))
            / len(words)
            if words
            else 0,
            "avg_word_length": sum(len(word) for word in words) / len(words)
            if words
            else 0,
        }

    def _get_believability_details(self, content: str) -> Dict[str, Any]:
        """Get detailed believability analysis."""
        return {
            "has_natural_flow": self._score_language_flow(content) >= 80,
            "has_logical_structure": self._score_content_structure(content) >= 80,
            "appropriate_complexity": self._score_appropriate_complexity(content) >= 80,
            "human_variability": self._score_human_variability(content) >= 80,
            "transition_words_present": any(
                trans in content.lower()
                for trans in [
                    "however",
                    "therefore",
                    "furthermore",
                    "additionally",
                    "consequently",
                ]
            ),
        }


def create_content_scorer(human_threshold: float = 75.0) -> ContentQualityScorer:
    """
    Create a content quality scorer instance.

    Args:
        human_threshold: Minimum score required to pass human believability test

    Returns:
        Configured ContentQualityScorer instance
    """
    return ContentQualityScorer(human_threshold=human_threshold)
