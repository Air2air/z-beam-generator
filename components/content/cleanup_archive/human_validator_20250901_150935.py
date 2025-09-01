#!/usr/bin/env python3
"""
Human-Like Content Validator for Content Component

Implements comprehensive validation criteria to ensure AI-generated content 
mimics natural human writing patterns and variability.
"""

import re
import statistics
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class HumanLikeValidator:
    """
    Validates content for human-like characteristics including:
    - Structural variety and flow
    - Visual and typographical elements  
    - Vocabulary and word choice
    - Sentence structure and rhythm
    - Tone, flow, and personal elements
    """
    
    def __init__(self):
        self.validation_thresholds = {
            'paragraph_variation_min': 0.15,  # 15% variation in paragraph lengths
            'sentence_variation_min': 0.20,   # 20% variation in sentence lengths
            'lexical_diversity_min': 0.4,     # Type-token ratio
            'heading_ratio_max': 0.30,        # Max 30% under headings
            'emphasis_ratio_max': 0.05,       # Max 5% emphasized words
            'passive_voice_max': 0.30,        # Max 30% passive voice
            'readability_min': 60,             # Flesch-Kincaid score
            'human_likeness_threshold': 80     # Overall score threshold
        }
    
    def validate_content(self, content: str, material_name: str = "", 
                        author_info: Dict = None) -> Dict[str, Any]:
        """
        Comprehensive validation of content for human-like characteristics.
        
        Args:
            content: The generated content to validate
            material_name: Material being processed
            author_info: Author context for validation adaptation
            
        Returns:
            Dict containing validation results and recommendations
        """
        if not content or len(content.strip()) < 100:
            return {
                'success': False,
                'human_likeness_score': 0,
                'errors': ['Content too short for meaningful validation'],
                'recommendations': ['Generate longer content (minimum 100 words)'],
                'needs_regeneration': True
            }
        
        # Run all validation checks
        structural_score = self._validate_structural_variety(content)
        typographical_score = self._validate_typographical_elements(content)
        vocabulary_score = self._validate_vocabulary_choice(content)
        sentence_score = self._validate_sentence_structure(content)
        tone_score = self._validate_tone_and_flow(content, author_info)
        
        # Calculate weighted overall score
        weights = {
            'structural': 0.25,
            'typographical': 0.15, 
            'vocabulary': 0.25,
            'sentence': 0.20,
            'tone': 0.15
        }
        
        overall_score = (
            structural_score['score'] * weights['structural'] +
            typographical_score['score'] * weights['typographical'] +
            vocabulary_score['score'] * weights['vocabulary'] +
            sentence_score['score'] * weights['sentence'] +
            tone_score['score'] * weights['tone']
        )
        
        # Compile recommendations
        all_recommendations = []
        critical_issues = []
        
        for validation in [structural_score, typographical_score, vocabulary_score, 
                          sentence_score, tone_score]:
            all_recommendations.extend(validation.get('recommendations', []))
            critical_issues.extend(validation.get('critical_issues', []))
        
        # Determine if regeneration is needed
        needs_regeneration = (
            overall_score < self.validation_thresholds['human_likeness_threshold'] or
            len(critical_issues) > 2
        )
        
        return {
            'success': True,
            'human_likeness_score': round(overall_score, 1),
            'category_scores': {
                'structural_variety': round(structural_score['score'], 1),
                'typographical_elements': round(typographical_score['score'], 1),
                'vocabulary_choice': round(vocabulary_score['score'], 1),
                'sentence_structure': round(sentence_score['score'], 1),
                'tone_and_flow': round(tone_score['score'], 1)
            },
            'recommendations': all_recommendations[:5],  # Top 5 recommendations
            'critical_issues': critical_issues,
            'needs_regeneration': needs_regeneration,
            'detailed_analysis': {
                'structural': structural_score.get('details', {}),
                'typographical': typographical_score.get('details', {}),
                'vocabulary': vocabulary_score.get('details', {}),
                'sentence': sentence_score.get('details', {}),
                'tone': tone_score.get('details', {})
            }
        }
    
    def _validate_structural_variety(self, content: str) -> Dict[str, Any]:
        """Validate structural variety and flow patterns."""
        lines = content.split('\n')
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        score = 100
        recommendations = []
        critical_issues = []
        details = {}
        
        # Check paragraph length variation
        if len(paragraphs) > 1:
            para_lengths = [len(p.split()) for p in paragraphs if p]
            if para_lengths:
                avg_length = statistics.mean(para_lengths)
                variation = statistics.stdev(para_lengths) / avg_length if avg_length > 0 else 0
                details['paragraph_variation'] = round(variation, 3)
                
                if variation < self.validation_thresholds['paragraph_variation_min']:
                    score -= 20
                    critical_issues.append(f"Paragraph lengths too uniform (variation: {variation:.3f})")
                    recommendations.append("Vary paragraph lengths more (mix short 2-3 sentence paragraphs with longer 5-7 sentence ones)")
        
        # Check heading usage
        headings = [line for line in lines if line.strip().startswith(('#', '##', '###'))]
        total_words = len(content.split())
        heading_words = sum(len(h.split()) for h in headings)
        heading_ratio = heading_words / total_words if total_words > 0 else 0
        details['heading_ratio'] = round(heading_ratio, 3)
        
        if heading_ratio > self.validation_thresholds['heading_ratio_max']:
            score -= 15
            recommendations.append("Reduce heading usage - over-reliance suggests templated structure")
        
        # Check introduction and conclusion balance
        if len(paragraphs) >= 3:
            intro_length = len(paragraphs[0].split())
            conclusion_length = len(paragraphs[-1].split())
            ratio = abs(intro_length - conclusion_length) / max(intro_length, conclusion_length, 1)
            details['intro_conclusion_balance'] = round(ratio, 3)
            
            if ratio < 0.2:  # Too similar
                score -= 10
                recommendations.append("Vary introduction and conclusion lengths - they appear too similar")
        
        return {
            'score': max(score, 0),
            'recommendations': recommendations,
            'critical_issues': critical_issues,
            'details': details
        }
    
    def _validate_typographical_elements(self, content: str) -> Dict[str, Any]:
        """Validate visual and typographical elements."""
        score = 100
        recommendations = []
        details = {}
        
        total_words = len(content.split())
        
        # Check emphasis usage (bold, italic)
        bold_matches = re.findall(r'\*\*([^*]+)\*\*', content)
        italic_matches = re.findall(r'\*([^*]+)\*', content)
        emphasized_words = len(' '.join(bold_matches + italic_matches).split())
        emphasis_ratio = emphasized_words / total_words if total_words > 0 else 0
        details['emphasis_ratio'] = round(emphasis_ratio, 3)
        
        if emphasis_ratio > self.validation_thresholds['emphasis_ratio_max']:
            score -= 15
            recommendations.append("Reduce emphasis usage - overuse suggests AI pattern")
        elif emphasis_ratio == 0:
            score -= 5
            recommendations.append("Consider adding subtle emphasis for key technical terms")
        
        # Check list usage
        bullet_lines = [line for line in content.split('\n') if re.match(r'^\s*[-*•]\s', line)]
        numbered_lines = [line for line in content.split('\n') if re.match(r'^\s*\d+\.\s', line)]
        list_ratio = (len(bullet_lines) + len(numbered_lines)) / len(content.split('\n'))
        details['list_ratio'] = round(list_ratio, 3)
        
        if list_ratio > 0.3:  # More than 30% of lines are lists
            score -= 10
            recommendations.append("Reduce list usage - excessive lists suggest mechanical structure")
        
        # Check for whitespace patterns
        double_spaces = content.count('  ')
        details['double_spaces'] = double_spaces
        
        if double_spaces == 0:
            score -= 5
            recommendations.append("Consider adding occasional double spaces for natural imperfection")
        
        return {
            'score': max(score, 0),
            'recommendations': recommendations,
            'details': details
        }
    
    def _validate_vocabulary_choice(self, content: str) -> Dict[str, Any]:
        """Validate vocabulary diversity and appropriateness."""
        words = re.findall(r'\b\w+\b', content.lower())
        total_words = len(words)
        unique_words = len(set(words))
        
        score = 100
        recommendations = []
        details = {}
        
        # Calculate lexical diversity (type-token ratio)
        lexical_diversity = unique_words / total_words if total_words > 0 else 0
        details['lexical_diversity'] = round(lexical_diversity, 3)
        
        if lexical_diversity < self.validation_thresholds['lexical_diversity_min']:
            score -= 25
            recommendations.append("Increase vocabulary diversity - use more varied word choices")
        
        # Check for buzzword repetition
        buzzwords = ['revolutionary', 'innovative', 'cutting-edge', 'state-of-the-art', 'advanced']
        buzzword_count = sum(content.lower().count(word) for word in buzzwords)
        details['buzzword_usage'] = buzzword_count
        
        if buzzword_count > 3:
            score -= 15
            recommendations.append("Reduce buzzword usage - repetitive promotional language suggests AI generation")
        
        # Check for technical term balance
        technical_terms = ['wavelength', 'fluence', 'ablation', 'parameters', 'specifications']
        technical_count = sum(content.lower().count(term) for term in technical_terms)
        technical_ratio = technical_count / total_words if total_words > 0 else 0
        details['technical_density'] = round(technical_ratio, 3)
        
        if technical_ratio > 0.1:  # More than 10%
            score -= 10
            recommendations.append("Balance technical terminology with accessible language")
        
        return {
            'score': max(score, 0),
            'recommendations': recommendations,
            'details': details
        }
    
    def _validate_sentence_structure(self, content: str) -> Dict[str, Any]:
        """Validate sentence structure and rhythm."""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        score = 100
        recommendations = []
        details = {}
        
        if not sentences:
            return {'score': 0, 'recommendations': ['No valid sentences found'], 'details': {}}
        
        # Calculate sentence length variation
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = statistics.mean(sentence_lengths)
        variation = statistics.stdev(sentence_lengths) / avg_length if avg_length > 0 else 0
        details['sentence_variation'] = round(variation, 3)
        details['avg_sentence_length'] = round(avg_length, 1)
        
        if variation < self.validation_thresholds['sentence_variation_min']:
            score -= 20
            recommendations.append("Increase sentence length variety - mix short punchy sentences with longer complex ones")
        
        # Check for appropriate sentence length range
        if avg_length < 8:
            score -= 10
            recommendations.append("Increase average sentence length for more sophisticated writing")
        elif avg_length > 25:
            score -= 15
            recommendations.append("Reduce average sentence length for better readability")
        
        # Check for passive voice usage
        passive_indicators = ['was', 'were', 'been', 'being', 'is processed', 'are performed']
        passive_count = sum(content.lower().count(indicator) for indicator in passive_indicators)
        passive_ratio = passive_count / len(sentences) if sentences else 0
        details['passive_voice_ratio'] = round(passive_ratio, 3)
        
        if passive_ratio > self.validation_thresholds['passive_voice_max']:
            score -= 15
            recommendations.append("Reduce passive voice usage - prefer active voice for engagement")
        
        return {
            'score': max(score, 0),
            'recommendations': recommendations,
            'details': details
        }
    
    def _validate_tone_and_flow(self, content: str, author_info: Dict = None) -> Dict[str, Any]:
        """Validate tone consistency and personal elements."""
        score = 100
        recommendations = []
        details = {}
        
        # Check for transition variety
        transitions = ['however', 'moreover', 'furthermore', 'additionally', 'consequently', 'therefore']
        transition_counts = {t: content.lower().count(t) for t in transitions}
        max_transition_use = max(transition_counts.values()) if transition_counts else 0
        details['max_transition_repetition'] = max_transition_use
        
        if max_transition_use > 2:
            score -= 10
            recommendations.append("Vary transition words - repetitive connectors suggest mechanical writing")
        
        # Check for personal touch elements
        personal_indicators = ['imagine', 'consider', 'think', 'experience', 'understand']
        personal_count = sum(content.lower().count(indicator) for indicator in personal_indicators)
        details['personal_elements'] = personal_count
        
        if personal_count == 0:
            score -= 15
            recommendations.append("Add subtle personal elements like 'consider' or 'imagine' for human touch")
        
        # Check for rhetorical questions
        question_count = content.count('?')
        details['questions'] = question_count
        
        if question_count == 0:
            score -= 5
            recommendations.append("Consider adding a rhetorical question to engage readers")
        
        # Check for AI-specific patterns to avoid
        ai_patterns = [
            'as we all know', 'it is important to note', 'in summary', 'to summarize',
            'it should be noted', 'it is worth mentioning'
        ]
        ai_pattern_count = sum(content.lower().count(pattern) for pattern in ai_patterns)
        details['ai_patterns'] = ai_pattern_count
        
        if ai_pattern_count > 1:
            score -= 20
            recommendations.append("Remove AI-specific phrases that make content seem mechanical")
        
        return {
            'score': max(score, 0),
            'recommendations': recommendations,
            'details': details
        }
    
    def generate_improvement_prompt(self, validation_result: Dict[str, Any], 
                                  original_content: str, material_name: str,
                                  author_info: Dict = None) -> str:
        """
        Generate a specific prompt for content improvement based on validation results.
        
        Args:
            validation_result: Results from validate_content()
            original_content: Original content that failed validation
            material_name: Material being processed
            author_info: Author information for persona preservation
            
        Returns:
            Improvement prompt for API regeneration
        """
        if not validation_result.get('needs_regeneration', False):
            return ""
        
        score = validation_result.get('human_likeness_score', 0)
        recommendations = validation_result.get('recommendations', [])
        critical_issues = validation_result.get('critical_issues', [])
        
        prompt_parts = [
            f"CONTENT IMPROVEMENT REQUIRED (Current human-likeness score: {score}/100)",
            f"Material: {material_name}",
        ]
        
        # Add persona context if available
        if author_info:
            author_name = author_info.get('name', 'Expert')
            author_country = author_info.get('country', 'International')
            prompt_parts.extend([
                f"Author: {author_name} from {author_country}",
                "MAINTAIN the author's unique voice, cultural perspective, and writing style"
            ])
        
        prompt_parts.extend([
            "",
            "CRITICAL ISSUES TO FIX:"
        ])
        
        for issue in critical_issues[:3]:  # Top 3 critical issues
            prompt_parts.append(f"- {issue}")
        
        prompt_parts.extend([
            "",
            "SPECIFIC IMPROVEMENTS NEEDED:"
        ])
        
        for rec in recommendations[:5]:  # Top 5 recommendations
            prompt_parts.append(f"- {rec}")
        
        prompt_parts.extend([
            "",
            "REWRITE THE FOLLOWING CONTENT to address these issues while maintaining technical accuracy",
        ])
        
        if author_info:
            prompt_parts.append("and preserving the author's authentic voice and cultural perspective:")
        else:
            prompt_parts.append(":")
        
        prompt_parts.extend([
            "",
            "ORIGINAL CONTENT:",
            original_content,
            "",
            "IMPROVED CONTENT (more human-like, varied, and natural):"
        ])
        
        return "\n".join(prompt_parts)


def validate_content_human_like(content: str, material_name: str = "", 
                               author_info: Dict = None) -> Dict[str, Any]:
    """
    Convenience function for human-like content validation.
    
    Args:
        content: Content to validate
        material_name: Material being processed
        author_info: Author context information
        
    Returns:
        Validation results dictionary
    """
    validator = HumanLikeValidator()
    return validator.validate_content(content, material_name, author_info)
