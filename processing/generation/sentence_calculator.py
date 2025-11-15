"""
Dynamic Sentence Count Calculator

Calculates target sentence counts based on:
1. Target word count (from config.yaml component_lengths)
2. Author grammar norms (avg_words_per_sentence from persona files)
3. Sentence length distribution (short/medium/long ratios)

This replaces hardcoded min_sentences constraints with dynamic calculation
that respects country-specific writing patterns and grammar norms.
"""

import logging
import math
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class SentenceCalculator:
    """
    Calculates dynamic sentence counts based on author voice and grammar norms.
    
    Each country has different grammar patterns:
    - American English: 16 words/sentence average (concise, direct)
    - Italian English: 18 words/sentence average (formal, structured)
    - Indonesian English: 17 words/sentence average (clear, cause-effect)
    - Taiwanese English: 15 words/sentence average (data-focused, precise)
    """
    
    @staticmethod
    def calculate_sentence_target(
        word_count: int,
        grammar_norms: Dict
    ) -> Tuple[int, int, str]:
        """
        Calculate target sentence count based on word count and grammar norms.
        
        Args:
            word_count: Target word count for the component
            grammar_norms: Grammar norms dict from author persona file containing:
                - avg_words_per_sentence: Average words per sentence for this author
                - sentence_length_distribution: Dict with short/medium/long percentages
                - compound_sentence_ratio: Percentage of compound sentences
        
        Returns:
            Tuple of (min_sentences, max_sentences, guidance_string)
            
        Example:
            >>> grammar_norms = {
            ...     'avg_words_per_sentence': 16,
            ...     'sentence_length_distribution': {'short': 0.30, 'medium': 0.50, 'long': 0.20},
            ...     'compound_sentence_ratio': 0.25
            ... }
            >>> calculate_sentence_target(100, grammar_norms)
            (5, 7, "Mix: 2 short (<12w), 3 medium (12-18w), 1-2 long (19+w)")
        """
        if not grammar_norms:
            logger.warning("No grammar_norms provided, using default 15 words/sentence")
            avg_words = 15
            distribution = {'short': 0.30, 'medium': 0.50, 'long': 0.20}
        else:
            avg_words = grammar_norms.get('avg_words_per_sentence', 15)
            distribution = grammar_norms.get('sentence_length_distribution', {
                'short': 0.30, 'medium': 0.50, 'long': 0.20
            })
        
        # Calculate base sentence count from word count and average
        base_sentences = word_count / avg_words
        
        # Add MORE dramatic variation range (±20-30% for structural variety)
        # This creates 2-4 sentence ranges instead of ±1
        variation_pct = 0.25  # ±25% variation
        variation_range = max(1, int(base_sentences * variation_pct))
        
        min_sentences = max(1, math.floor(base_sentences - variation_range))
        max_sentences = math.ceil(base_sentences + variation_range)
        
        # Build sentence distribution guidance based on percentages
        short_count = round(base_sentences * distribution.get('short', 0.30))
        medium_count = round(base_sentences * distribution.get('medium', 0.50))
        long_count = round(base_sentences * distribution.get('long', 0.20))
        
        # Ensure we have at least 1 of primary sentence type
        if medium_count == 0 and base_sentences >= 2:
            medium_count = 1
        if short_count == 0 and base_sentences >= 3:
            short_count = 1
        
        # Build guidance string
        parts = []
        if short_count > 0:
            parts.append(f"{short_count} short (<12w)")
        if medium_count > 0:
            parts.append(f"{medium_count} medium (12-18w)")
        if long_count > 0:
            if long_count == 1:
                parts.append("1-2 long (19+w)")
            else:
                parts.append(f"{long_count} long (19+w)")
        
        guidance = f"Mix: {', '.join(parts)}"
        
        logger.debug(
            f"Calculated sentence target: {min_sentences}-{max_sentences} sentences "
            f"({word_count} words ÷ {avg_words} avg = {base_sentences:.1f} base)"
        )
        
        return min_sentences, max_sentences, guidance
    
    @staticmethod
    def get_sentence_guidance(
        word_count: int,
        grammar_norms: Dict
    ) -> str:
        """
        Generate sentence structure guidance string for prompts.
        
        This provides natural language guidance about sentence counts and
        distribution that can be included in generation prompts.
        
        Args:
            word_count: Target word count
            grammar_norms: Grammar norms from author persona
        
        Returns:
            Natural language guidance string
            
        Example:
            >>> get_sentence_guidance(100, grammar_norms)
            "Target 5-7 sentences (avg 16 words/sentence). Mix: 2 short (<12w), 3 medium (12-18w), 1-2 long (19+w)"
        """
        min_sent, max_sent, distribution = SentenceCalculator.calculate_sentence_target(
            word_count, grammar_norms
        )
        
        avg_words = grammar_norms.get('avg_words_per_sentence', 15) if grammar_norms else 15
        
        return f"Target {min_sent}-{max_sent} sentences (avg {avg_words} words/sentence). {distribution}"
    
    @staticmethod
    def validate_sentence_count(
        text: str,
        word_count: int,
        grammar_norms: Dict
    ) -> Tuple[bool, str]:
        """
        Validate if generated text has appropriate sentence count.
        
        Args:
            text: Generated text
            word_count: Target word count
            grammar_norms: Grammar norms from author persona
        
        Returns:
            Tuple of (is_valid, message)
        """
        # Count sentences (simple heuristic)
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        actual_count = len(sentences)
        
        min_sent, max_sent, _ = SentenceCalculator.calculate_sentence_target(
            word_count, grammar_norms
        )
        
        if actual_count < min_sent:
            return False, f"Too few sentences: {actual_count} (expected {min_sent}-{max_sent})"
        elif actual_count > max_sent:
            return False, f"Too many sentences: {actual_count} (expected {min_sent}-{max_sent})"
        else:
            return True, f"Sentence count valid: {actual_count} (target {min_sent}-{max_sent})"
