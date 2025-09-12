"""
Content Persona Validators

Validates content against specific country/cultural persona patterns
for authentic author representation.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PersonaValidators:
    """Validates content against country-specific persona patterns."""

    def __init__(self, author_markers: Dict[str, List[str]]):
        """
        Initialize the persona validators.
        
        Args:
            author_markers: Dictionary mapping country codes to linguistic markers
        """
        self.author_markers = author_markers

    def score_author_authenticity(self, content: str, author_info: Dict[str, Any]) -> float:
        """
        Score author authenticity based on persona patterns (0-100).
        
        Args:
            content: Content to evaluate
            author_info: Author information including country
            
        Returns:
            Authenticity score from 0-100
        """
        country = author_info.get("country", "").lower()
        content_lower = content.lower()
        words = content.split()
        word_count = len(words)

        # Base score for general authenticity indicators
        base_score = self._score_general_authenticity(content, content_lower)

        # Country-specific scoring
        country_score = 0.0
        if country == "italy":
            country_score = self._score_italian_persona(content, content_lower, words)
        elif country == "taiwan":
            country_score = self._score_taiwan_persona(content, content_lower, words)
        elif country == "indonesia":
            country_score = self._score_indonesia_persona(content, content_lower, words)
        elif country == "usa":
            country_score = self._score_usa_persona(content, content_lower, words)
        else:
            # Generic scoring for unknown countries
            country_score = self._score_generic_persona(content, content_lower, words)

        # Combine scores with weights
        final_score = (base_score * 0.3) + (country_score * 0.7)

        logger.debug(
            f"Author authenticity: {final_score:.1f}/100 (country: {country}, words: {word_count})"
        )
        return min(final_score, 100.0)

    def _score_general_authenticity(self, content: str, content_lower: str) -> float:
        """Score general authenticity markers present in all personas."""
        score = 0.0

        # Personal pronouns and perspective (20 points)
        personal_markers = ["i", "we", "our", "my", "us"]
        personal_count = sum(1 for marker in personal_markers if marker in content_lower.split())
        score += min(personal_count * 4, 20)

        # Natural language connectors (20 points)
        connectors = ["however", "therefore", "furthermore", "moreover", "consequently"]
        connector_count = sum(1 for conn in connectors if conn in content_lower)
        score += min(connector_count * 4, 20)

        # Professional terminology (20 points)
        professional_terms = ["analysis", "evaluation", "research", "investigation", "methodology"]
        prof_count = sum(1 for term in professional_terms if term in content_lower)
        score += min(prof_count * 4, 20)

        # Opinion/perspective markers (20 points)
        opinion_markers = ["believe", "consider", "suggest", "recommend", "propose"]
        opinion_count = sum(1 for marker in opinion_markers if marker in content_lower)
        score += min(opinion_count * 4, 20)

        # Technical authority markers (20 points)
        authority_markers = ["experience", "expertise", "professional", "technical", "specialized"]
        auth_count = sum(1 for marker in authority_markers if marker in content_lower)
        score += min(auth_count * 4, 20)

        return score

    def _score_italian_persona(self, content: str, content_lower: str, words: List[str]) -> float:
        """Score Italian academic persona with authentic linguistic pattern detection."""
        score = 0.0

        # Italian linguistic nuances (30 points)
        italian_connectors = [
            "therefore", "consequently", "furthermore", "moreover", "however",
            "in addition", "as a result", "on the other hand",
        ]
        connector_count = sum(1 for conn in italian_connectors if conn in content_lower)
        score += min(connector_count * 4, 30)

        # Technical precision phrasing (25 points)
        precision_phrases = [
            "technical precision requires", "engineering analysis shows", "methodical approach",
            "systematic investigation", "comprehensive analysis", "precision engineering",
            "technical innovation", "manufacturing excellence",
        ]
        precision_count = sum(1 for phrase in precision_phrases if phrase in content_lower)
        score += min(precision_count * 5, 25)

        # Heritage/manufacturing focus (20 points)
        heritage_terms = [
            "heritage", "preservation", "manufacturing", "additive", "aerospace",
            "automotive", "archaeological", "historical", "precision", "excellence",
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

    def _score_taiwan_persona(self, content: str, content_lower: str, words: List[str]) -> float:
        """Score Taiwan academic persona with authentic linguistic pattern detection."""
        score = 0.0

        # Question-based exploration patterns (25 points)
        taiwanese_questions = [
            "what if we consider", "what if", "as we continue", "systematic approach",
            "careful analysis", "methodical investigation", "step-by-step",
        ]
        question_count = sum(1 for phrase in taiwanese_questions if phrase in content_lower)
        score += min(question_count * 5, 25)

        # Article omissions and simplified structures (20 points)
        simplified_indicators = [
            content_lower.count(" the ") < len(words) * 0.08,  # Fewer articles than typical
            content.count("(") >= 4,  # Technical specs in parentheses
            "material" in content_lower and content_lower.count("the material") < content_lower.count("material") * 0.5,
        ]
        simplified_score = sum(7 for indicator in simplified_indicators if indicator)
        score += min(simplified_score, 20)

        # Technical analysis vocabulary (30 points)
        taiwan_technical = [
            "analyze", "examine", "investigate", "determine", "evaluate",
            "parameters", "characteristics", "properties", "specifications",
            "performance", "efficiency", "optimization",
        ]
        tech_count = sum(1 for term in taiwan_technical if term in content_lower)
        score += min(tech_count * 3, 30)

        # Formal academic tone (25 points)
        formal_markers = [
            "research", "study", "investigation", "analysis", "methodology",
            "findings", "results", "conclusion", "observation",
        ]
        formal_count = sum(1 for marker in formal_markers if marker in content_lower)
        score += min(formal_count * 3, 25)

        return score

    def _score_indonesia_persona(self, content: str, content_lower: str, words: List[str]) -> float:
        """Score Indonesia academic persona with authentic linguistic pattern detection."""
        score = 0.0

        # Methodical analytical approach (30 points)
        analytical_terms = [
            "analyze", "examine", "investigate", "determine", "evaluate",
            "assess", "study", "research", "observation", "findings", "results",
        ]
        analytical_count = sum(1 for term in analytical_terms if term in content_lower)
        score += min(analytical_count * 3, 30)

        # Environmental/community context (25 points)
        community_terms = [
            "environment", "community", "sustainable", "affordable", "practical",
            "implementation", "society", "local", "region", "marine", "humid",
        ]
        community_count = sum(1 for term in community_terms if term in content_lower)
        score += min(community_count * 4, 25)

        # Formal academic structure (20 points)
        formal_indicators = [
            content.count("##") >= 3,  # Multiple subsections
            "overview" in content_lower,
            "parameters" in content_lower,
            "applications" in content_lower,
        ]
        formal_score = sum(5 for indicator in formal_indicators if indicator)
        score += min(formal_score, 20)

        # Technical precision language (25 points)
        precision_terms = [
            "precise", "accurate", "specific", "detailed", "comprehensive",
            "thorough", "systematic", "methodical", "rigorous",
        ]
        precision_count = sum(1 for term in precision_terms if term in content_lower)
        score += min(precision_count * 3, 25)

        return score

    def _score_usa_persona(self, content: str, content_lower: str, words: List[str]) -> float:
        """Score USA academic persona with enhanced detection."""
        score = 0.0

        # Conversational/accessible language (30 points)
        conversational_terms = [
            "let's", "we're", "you're", "imagine", "consider this", "think about",
            "what's", "here's", "that's", "it's", "can't", "don't", "won't",
        ]
        conversational_count = sum(1 for term in conversational_terms if term in content_lower)
        score += min(conversational_count * 4, 30)

        # Optimistic/forward-looking language (25 points)
        optimistic_terms = [
            "innovation", "breakthrough", "cutting-edge", "advanced", "revolutionary",
            "promising", "exciting", "potential", "opportunity", "future",
        ]
        optimistic_count = sum(1 for term in optimistic_terms if term in content_lower)
        score += min(optimistic_count * 4, 25)

        # Direct communication style (25 points)
        direct_indicators = [
            content.count("!") >= 1,  # Exclamation for emphasis
            any(phrase in content_lower for phrase in ["bottom line", "key point", "simply put"]),
            content.count("However,") >= 1 or content.count("But") >= 1,
            len([s for s in content.split(".") if len(s.split()) <= 15]) >= 3,  # Short, direct sentences
        ]
        direct_score = sum(6 for indicator in direct_indicators if indicator)
        score += min(direct_score, 25)

        # Practical application focus (20 points)
        practical_terms = [
            "practical", "real-world", "industry", "commercial", "cost-effective",
            "efficient", "scalable", "implementation", "production", "market",
        ]
        practical_count = sum(1 for term in practical_terms if term in content_lower)
        score += min(practical_count * 3, 20)

        return score

    def _score_generic_persona(self, content: str, content_lower: str, words: List[str]) -> float:
        """Score content for generic academic/professional persona when country is unknown."""
        score = 0.0

        # Academic vocabulary (30 points)
        academic_terms = [
            "research", "analysis", "investigation", "methodology", "findings",
            "conclusion", "hypothesis", "theory", "evidence", "study",
        ]
        academic_count = sum(1 for term in academic_terms if term in content_lower)
        score += min(academic_count * 3, 30)

        # Professional language patterns (30 points)
        professional_patterns = [
            "based on", "according to", "in conclusion", "furthermore", "however",
            "therefore", "consequently", "in addition", "moreover",
        ]
        pattern_count = sum(1 for pattern in professional_patterns if pattern in content_lower)
        score += min(pattern_count * 3, 30)

        # Technical expertise indicators (25 points)
        expertise_indicators = [
            "technical", "professional", "specialized", "advanced", "sophisticated",
            "complex", "detailed", "comprehensive", "systematic",
        ]
        expertise_count = sum(1 for indicator in expertise_indicators if indicator in content_lower)
        score += min(expertise_count * 3, 25)

        # Structured presentation (15 points)
        structure_indicators = [
            content.count("#") >= 2,  # Section headers
            content.count("**") >= 4,  # Emphasis text
            len([p for p in content.split("\n\n") if p.strip()]) >= 3,  # Multiple paragraphs
        ]
        structure_score = sum(5 for indicator in structure_indicators if indicator)
        score += min(structure_score, 15)

        return score

    def validate_persona_consistency(self, content: str, author_info: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate persona consistency across content.
        
        Args:
            content: Content to validate
            author_info: Author information
            
        Returns:
            Dictionary of validation results
        """
        country = author_info.get("country", "").lower()
        content_lower = content.lower()
        
        validation_results = {
            "has_personal_markers": self._has_personal_perspective_markers(content_lower),
            "shows_expertise": self._demonstrates_technical_expertise(content_lower),
            "maintains_tone": self._maintains_consistent_tone(content_lower, country),
            "uses_appropriate_language": self._uses_appropriate_language_level(content_lower, country),
            "shows_cultural_awareness": self._shows_cultural_context(content_lower, country),
        }
        
        return validation_results

    def _has_personal_perspective_markers(self, content_lower: str) -> bool:
        """Check for personal perspective indicators."""
        personal_markers = ["i", "we", "our", "my", "in my experience", "from my perspective"]
        return any(marker in content_lower for marker in personal_markers)

    def _demonstrates_technical_expertise(self, content_lower: str) -> bool:
        """Check for technical expertise demonstration."""
        expertise_markers = ["technical", "professional", "analysis", "research", "methodology"]
        return any(marker in content_lower for marker in expertise_markers)

    def _maintains_consistent_tone(self, content_lower: str, country: str) -> bool:
        """Check for consistent tone appropriate to country persona."""
        if country == "usa":
            # Should be more conversational
            return any(marker in content_lower for marker in ["let's", "we're", "you're"])
        elif country in ["italy", "taiwan", "indonesia"]:
            # Should be more formal
            return any(marker in content_lower for marker in ["analysis", "investigation", "research"])
        return True  # Default to true for unknown countries

    def _uses_appropriate_language_level(self, content_lower: str, country: str) -> bool:
        """Check for appropriate language complexity level."""
        # Count complex words (>2 syllables approximately)
        words = content_lower.split()
        complex_words = [w for w in words if len(w) > 8]  # Rough heuristic
        complexity_ratio = len(complex_words) / len(words) if words else 0
        
        if country == "usa":
            return complexity_ratio < 0.3  # More accessible language
        else:
            return complexity_ratio > 0.1  # More technical language
    
    def _shows_cultural_context(self, content_lower: str, country: str) -> bool:
        """Check for appropriate cultural context markers."""
        if country in self.author_markers:
            markers = [marker.lower() for marker in self.author_markers[country]]
            return any(marker in content_lower for marker in markers)
        return True  # Default to true if no specific markers available
