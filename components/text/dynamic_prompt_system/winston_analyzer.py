#!/usr/bin/env python3
"""
Winston Analyzer for Dynamic Prompt System

Analyzes Winston AI detection results to determine what aspects of the
prompts need improvement and prioritizes evolution targets.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class WinstonAnalyzer:
    """
    Analyzes Winston AI detection results to determine prompt improvement needs.
    """

    def __init__(self):
        self.improvement_thresholds = {
            'critical': 30,  # Very low scores need fundamental improvements
            'low': 50,       # Low scores need authenticity improvements
            'moderate': 70,  # Moderate scores need refinement
            'good': 85       # Good scores may need minor tweaks
        }

    def analyze_improvement_needs(self, winston_result: Dict[str, Any],
                                content: str, iteration_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Winston results to determine if and what improvements are needed.

        Args:
            winston_result: Winston AI detection analysis
            content: The generated content
            iteration_context: Current iteration context

        Returns:
            Analysis dictionary with improvement recommendations
        """
        score = winston_result.get('overall_score', 0)
        classification = winston_result.get('classification', 'unknown')

        analysis = {
            'needs_improvement': False,
            'priority_level': 'none',
            'target_sections': [],
            'score_analysis': {
                'current_score': score,
                'classification': classification,
                'threshold_distance': 0
            },
            'content_analysis': {
                'length': len(content),
                'has_improvement_potential': False
            }
        }

        # Determine if improvements are needed
        target_score = iteration_context.get('target_score', 70)
        analysis['score_analysis']['threshold_distance'] = target_score - score

        if score < self.improvement_thresholds['critical']:
            analysis['needs_improvement'] = True
            analysis['priority_level'] = 'critical'
            analysis['target_sections'] = self._get_critical_targets(winston_result, content)
        elif score < self.improvement_thresholds['low']:
            analysis['needs_improvement'] = True
            analysis['priority_level'] = 'high'
            analysis['target_sections'] = self._get_authenticity_targets(winston_result, content)
        elif score < self.improvement_thresholds['moderate']:
            analysis['needs_improvement'] = True
            analysis['priority_level'] = 'medium'
            analysis['target_sections'] = self._get_refinement_targets(winston_result, content)
        elif score < target_score:
            # Below target but not critically low - minor improvements
            analysis['needs_improvement'] = True
            analysis['priority_level'] = 'low'
            analysis['target_sections'] = self._get_minor_targets(winston_result, content)

        # Analyze content for improvement potential
        analysis['content_analysis']['has_improvement_potential'] = self._analyze_content_potential(content, winston_result)

        logger.info(f"📊 Winston Analysis: Score {score}, Priority: {analysis['priority_level']}, "
                   f"Targets: {len(analysis['target_sections'])} sections")

        return analysis

    def _get_critical_targets(self, winston_result: Dict[str, Any], content: str) -> List[str]:
        """Get improvement targets for critically low scores."""
        targets = [
            'ai_detection_avoidance',
            'human_writing_characteristics',
            'natural_imperfections'
        ]

        # Add content-specific targets
        if self._has_sentence_issues(winston_result):
            targets.append('cognitive_variability')

        return targets[:3]  # Limit to 3 targets

    def _get_authenticity_targets(self, winston_result: Dict[str, Any], content: str) -> List[str]:
        """Get improvement targets for low authenticity scores."""
        targets = [
            'human_authenticity_enhancements',
            'cognitive_variability',
            'personal_touch'
        ]

        # Add classification-specific targets
        if winston_result.get('classification') == 'ai':
            targets.append('cultural_humanization')

        return targets[:3]

    def _get_refinement_targets(self, winston_result: Dict[str, Any], content: str) -> List[str]:
        """Get improvement targets for moderate scores needing refinement."""
        targets = [
            'conversational_flow',
            'cultural_humanization',
            'detection_response'
        ]

        # Add variability if content is too uniform
        if self._content_lacks_variability(content):
            targets.append('sentence_structure_variability')

        return targets[:3]

    def _get_minor_targets(self, winston_result: Dict[str, Any], content: str) -> List[str]:
        """Get improvement targets for minor refinements."""
        targets = [
            'content_transformation_rules',
            'iteration_refinement_mechanism'
        ]

        return targets[:2]

    def _has_sentence_issues(self, winston_result: Dict[str, Any]) -> bool:
        """Check if there are sentence-level detection issues."""
        details = winston_result.get('analysis', {})
        sentences = details.get('sentences', [])

        if not sentences:
            return False

        # Check if many sentences have low scores
        low_score_sentences = [s for s in sentences if s.get('score', 100) < 50]
        return len(low_score_sentences) > len(sentences) * 0.3  # 30% threshold

    def _content_lacks_variability(self, content: str) -> bool:
        """Check if content lacks sentence structure variability."""
        sentences = content.split('.')
        if len(sentences) < 3:
            return False

        # Check sentence length variability
        lengths = [len(s.strip()) for s in sentences if s.strip()]
        if len(lengths) < 3:
            return False

        avg_length = sum(lengths) / len(lengths)
        variability = sum(abs(l - avg_length) for l in lengths) / len(lengths)

        # Low variability indicates uniform sentence structure
        return variability < avg_length * 0.3

    def _analyze_content_potential(self, content: str, winston_result: Dict[str, Any]) -> bool:
        """Analyze if the content has potential for improvement."""
        # Content too short
        if len(content) < 200:
            return False

        # Score too high already (diminishing returns)
        if winston_result.get('overall_score', 0) > 90:
            return False

        # Content has good length and moderate score = improvement potential
        return True
