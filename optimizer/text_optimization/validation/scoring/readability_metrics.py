"""
Content Readability Metrics

Calculates comprehensive readability scores and metrics for content evaluation
including sentence structure, vocabulary diversity, and complexity analysis.
"""

import logging
import math
import re
import statistics
from typing import Dict, List

logger = logging.getLogger(__name__)


class ReadabilityMetrics:
    """Calculates readability metrics and scores for content evaluation."""

    def __init__(self):
        """Initialize the readability metrics calculator."""
        self.technical_terms = [
            "laser", "cleaning", "material", "surface", "removal", "ablation",
            "thermal", "processing", "precision", "efficiency", "wavelength",
            "power", "density", "pulse", "beam", "optical", "interaction",
            "mechanism", "parameter", "optimization", "application", "industrial",
        ]

    def score_readability(self, content: str) -> float:
        """
        Score content readability using multiple metrics (0-100).
        
        Args:
            content: Content to evaluate
            
        Returns:
            Readability score from 0-100
        """
        try:
            # Calculate readability metrics
            sentences = self.split_sentences(content)
            words = self.extract_words(content)

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
                sentence_score * 0.3 +
                diversity_score * 0.3 +
                paragraph_score * 0.2 +
                complexity_score * 0.2
            )

            return min(readability_score, 100.0)

        except Exception as e:
            logger.error(f"Error calculating readability: {e}")
            raise ValueError(f"Readability calculation failed: {e}") from e

    def calculate_content_metrics(self, content: str) -> Dict[str, float]:
        """
        Calculate detailed content metrics.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary containing various content metrics
        """
        sentences = self.split_sentences(content)
        words = self.extract_words(content)
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)

        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Vocabulary diversity
        unique_words = set(word.lower() for word in words)
        vocabulary_diversity = len(unique_words) / word_count if word_count > 0 else 0

        # Technical density
        technical_words = sum(1 for word in words if word.lower() in self.technical_terms)
        technical_density = technical_words / word_count if word_count > 0 else 0

        # Average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0

        # Sentence length variance
        sentence_lengths = [len(self.extract_words(sent)) for sent in sentences]
        length_variance = statistics.variance(sentence_lengths) if len(sentence_lengths) > 1 else 0

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "avg_sentence_length": avg_sentence_length,
            "vocabulary_diversity": vocabulary_diversity,
            "technical_density": technical_density,
            "avg_word_length": avg_word_length,
            "sentence_length_variance": length_variance,
            "readability_score": self.score_readability(content),
        }

    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Use regex to split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def extract_words(self, text: str) -> List[str]:
        """Extract words from text, removing punctuation."""
        # Use regex to find word-like sequences
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return words

    def _score_sentence_length(self, avg_length: float) -> float:
        """Score sentence length based on readability guidelines."""
        # Optimal range: 15-25 words per sentence
        if 15 <= avg_length <= 25:
            return 100.0
        elif 10 <= avg_length < 15 or 25 < avg_length <= 30:
            return 80.0
        elif 5 <= avg_length < 10 or 30 < avg_length <= 40:
            return 60.0
        else:
            return 40.0

    def _score_paragraph_count(self, count: int) -> float:
        """Score paragraph count for readability."""
        # Optimal range: 3-6 paragraphs for typical content
        if 3 <= count <= 6:
            return 100.0
        elif count == 2 or count == 7:
            return 80.0
        elif count == 1 or count == 8:
            return 60.0
        else:
            return 40.0

    def _score_technical_complexity(self, content: str) -> float:
        """Score technical complexity balance."""
        words = self.extract_words(content)
        
        if not words:
            return 0.0

        # Technical term density
        technical_count = sum(1 for word in words if word.lower() in self.technical_terms)
        technical_density = technical_count / len(words)

        # Complex word density (rough heuristic: words > 8 characters)
        complex_words = [word for word in words if len(word) > 8]
        complex_density = len(complex_words) / len(words)

        # Optimal technical density: 5-15%
        # Optimal complex word density: 10-20%
        
        tech_score = 100.0
        if technical_density < 0.05:
            tech_score -= 20  # Too few technical terms
        elif technical_density > 0.15:
            tech_score -= 30  # Too many technical terms
        
        if complex_density < 0.10:
            tech_score -= 15  # Too simple
        elif complex_density > 0.20:
            tech_score -= 25  # Too complex
            
        return max(tech_score, 0.0)

    def analyze_sentence_structure(self, content: str) -> Dict[str, any]:
        """
        Analyze sentence structure patterns.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with sentence structure analysis
        """
        sentences = self.split_sentences(content)
        
        if not sentences:
            return {"error": "No sentences found"}

        # Calculate sentence length statistics
        sentence_lengths = [len(self.extract_words(sent)) for sent in sentences]
        
        structure_analysis = {
            "total_sentences": len(sentences),
            "avg_sentence_length": statistics.mean(sentence_lengths) if sentence_lengths else 0,
            "median_sentence_length": statistics.median(sentence_lengths) if sentence_lengths else 0,
            "sentence_length_variance": statistics.variance(sentence_lengths) if len(sentence_lengths) > 1 else 0,
            "shortest_sentence": min(sentence_lengths) if sentence_lengths else 0,
            "longest_sentence": max(sentence_lengths) if sentence_lengths else 0,
            "variety_score": self._calculate_sentence_variety(sentence_lengths),
        }

        return structure_analysis

    def _calculate_sentence_variety(self, sentence_lengths: List[int]) -> float:
        """Calculate sentence variety score based on length distribution."""
        if len(sentence_lengths) < 2:
            return 0.0
        
        # Calculate coefficient of variation as a measure of variety
        mean_length = statistics.mean(sentence_lengths)
        std_length = statistics.stdev(sentence_lengths)
        
        if mean_length == 0:
            return 0.0
        
        coefficient_of_variation = std_length / mean_length
        
        # Convert to 0-100 scale (higher CV = more variety)
        # Optimal CV is around 0.3-0.5 for good readability
        if 0.3 <= coefficient_of_variation <= 0.5:
            return 100.0
        elif 0.2 <= coefficient_of_variation < 0.3 or 0.5 < coefficient_of_variation <= 0.6:
            return 80.0
        elif 0.1 <= coefficient_of_variation < 0.2 or 0.6 < coefficient_of_variation <= 0.8:
            return 60.0
        else:
            return 40.0

    def calculate_flesch_score(self, content: str) -> float:
        """
        Calculate Flesch Reading Ease Score.
        
        Args:
            content: Content to analyze
            
        Returns:
            Flesch score (higher = more readable)
        """
        sentences = self.split_sentences(content)
        words = self.extract_words(content)
        
        if not sentences or not words:
            return 0.0
        
        # Count syllables (rough approximation)
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        # Flesch formula: 206.835 - (1.015 × ASL) - (84.6 × ASW)
        # ASL = Average Sentence Length, ASW = Average Syllables per Word
        asl = len(words) / len(sentences)
        asw = total_syllables / len(words)
        
        flesch_score = 206.835 - (1.015 * asl) - (84.6 * asw)
        
        return max(0.0, min(100.0, flesch_score))

    def _count_syllables(self, word: str) -> int:
        """
        Rough syllable count approximation.
        
        Args:
            word: Word to count syllables for
            
        Returns:
            Estimated syllable count
        """
        word = word.lower().strip()
        if not word:
            return 0
        
        # Count vowel groups
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        # Ensure at least 1 syllable
        return max(1, syllable_count)

    def get_readability_recommendations(self, content: str) -> List[str]:
        """
        Get recommendations for improving content readability.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of readability improvement suggestions
        """
        recommendations = []
        metrics = self.calculate_content_metrics(content)
        
        # Sentence length recommendations
        if metrics["avg_sentence_length"] > 25:
            recommendations.append("Consider breaking up long sentences for better readability")
        elif metrics["avg_sentence_length"] < 10:
            recommendations.append("Consider combining short sentences for better flow")
        
        # Vocabulary diversity recommendations
        if metrics["vocabulary_diversity"] < 0.4:
            recommendations.append("Use more varied vocabulary to improve engagement")
        elif metrics["vocabulary_diversity"] > 0.8:
            recommendations.append("Some vocabulary repetition might improve clarity")
        
        # Technical density recommendations
        if metrics["technical_density"] > 0.15:
            recommendations.append("Consider reducing technical jargon for broader accessibility")
        elif metrics["technical_density"] < 0.05:
            recommendations.append("Add more domain-specific terminology for expertise demonstration")
        
        # Paragraph structure recommendations
        if metrics["paragraph_count"] < 2:
            recommendations.append("Break content into multiple paragraphs for better structure")
        elif metrics["paragraph_count"] > 8:
            recommendations.append("Consider combining some paragraphs for better flow")
        
        # Word count recommendations
        if metrics["word_count"] < 100:
            recommendations.append("Content may be too brief - consider adding more detail")
        elif metrics["word_count"] > 1000:
            recommendations.append("Content may be too long - consider summarizing key points")
        
        return recommendations
