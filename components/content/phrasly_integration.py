#!/usr/bin/env python3
"""
GPTZero Integration Module
Provides AI detection scoring and iterative content improvement
"""

import os
import time
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIDetectionResult:
    """AI detection analysis result from GPTZero"""
    score: float  # AI detection score (0-100, lower = more AI-like)
    confidence: float  # Confidence level (0-1)
    classification: str  # "human", "ai", or "unclear"
    details: Dict[str, Any]  # Additional analysis details
    processing_time: float

@dataclass
class IterationResult:
    """Result of an iteration cycle"""
    iteration: int
    content: str
    ai_score: float
    improvement_made: bool
    prompt_adjustments: Dict[str, Any]
    metadata: Dict[str, Any]

class GPTZeroAIClient:
    """Client for GPTZero API integration"""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.gptzero.me"):
        self.api_key = api_key or os.getenv('GPTZERO_API_KEY')
        self.base_url = base_url
        self.session = requests.Session()

        if not self.api_key:
            raise ValueError("GPTZERO_API_KEY environment variable required")

        self.session.headers.update({
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'Z-Beam-Generator/1.0'
        })

    def analyze_text(self, text: str, options: Optional[Dict] = None) -> AIDetectionResult:
        """Analyze text for AI detection score"""
        start_time = time.time()

        payload = {
            "document": text,
            "multilingual": False
        }

        if options:
            payload.update(options)

        try:
            response = self.session.post(
                f"{self.base_url}/v2/predict/text",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # GPTZero returns different field structure
                # Extract the overall AI probability score
                ai_probability = data.get('documents', [{}])[0].get('average_generated_prob', 0.0)
                ai_score = ai_probability * 100  # Convert to 0-100 scale

                # Determine classification based on score
                if ai_score > 70:
                    classification = "ai"
                elif ai_score < 30:
                    classification = "human"
                else:
                    classification = "unclear"

                # Calculate confidence based on the score spread
                confidence = min(abs(ai_score - 50) / 50, 1.0)

                return AIDetectionResult(
                    score=ai_score,
                    confidence=confidence,
                    classification=classification,
                    details=data,
                    processing_time=time.time() - start_time
                )
            else:
                logger.error(f"GPTZero API error: {response.status_code} - {response.text}")
                return AIDetectionResult(
                    score=100.0,  # Assume AI if analysis fails
                    confidence=0.0,
                    classification='error',
                    details={'error': f'API error {response.status_code}'},
                    processing_time=time.time() - start_time
                )

        except Exception as e:
            logger.error(f"GPTZero request failed: {e}")
            return AIDetectionResult(
                score=100.0,  # Assume AI if analysis fails
                confidence=0.0,
                classification='error',
                details={'error': str(e)},
                processing_time=time.time() - start_time
            )

class IterativeContentImprover:
    """Iterative content improvement using AI detection feedback with nationality preservation"""

    def __init__(self, ai_detection_provider, target_score: float = 30.0,
                 max_iterations: int = 3, improvement_threshold: float = 5.0,
                 content_generator=None):
        self.ai_detection_provider = ai_detection_provider
        self.target_score = target_score  # Target AI detection score (lower = more human-like)
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold  # Minimum improvement to continue
        self.content_generator = content_generator  # Original content generator for re-generation

        # Improvement strategies - now include re-generation strategies
        self.strategies = [
            self._strategy_regenerate_with_nationality_emphasis,
            self._strategy_regenerate_with_human_elements,
            self._strategy_adjust_temperature,
            self._strategy_add_human_elements,
            self._strategy_modify_prompt_instructions,
            self._strategy_change_writing_style
        ]

    def improve_content(self, initial_content: str, material_name: str,
                       author_info: Dict, generation_params: Dict) -> Tuple[str, List[IterationResult]]:
        """
        Iteratively improve content using AI detection feedback

        Args:
            initial_content: Original generated content
            material_name: Name of the material
            author_info: Author information
            generation_params: Original generation parameters

        Returns:
            Tuple of (final_content, iteration_history)
        """
        current_content = initial_content
        iteration_history = []

        # Initial analysis
        initial_analysis = self.ai_detection_provider.analyze_text(current_content)
        iteration_history.append(IterationResult(
            iteration=0,
            content=current_content,
            ai_score=initial_analysis.score,
            improvement_made=False,
            prompt_adjustments={},
            metadata={
                'confidence': initial_analysis.confidence,
                'classification': initial_analysis.classification,
                'details': initial_analysis.details
            }
        ))

        logger.info(f"Initial AI detection score: {initial_analysis.score:.1f}")

        # Check if initial content meets target
        if initial_analysis.score <= self.target_score:
            logger.info(f"Content already meets target score ({initial_analysis.score:.1f} <= {self.target_score})")
            return current_content, iteration_history

        # Iterative improvement
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"Starting iteration {iteration}")

            # Try improvement strategies
            best_content = current_content
            best_score = initial_analysis.score
            best_strategy = None

            for strategy in self.strategies:
                try:
                    improved_content, adjustments = strategy(
                        current_content, material_name, author_info, generation_params
                    )

                    if improved_content != current_content:
                        analysis = self.ai_detection_provider.analyze_text(improved_content)

                        if analysis.score < best_score:
                            best_content = improved_content
                            best_score = analysis.score
                            best_strategy = strategy.__name__

                            logger.info(f"Strategy {strategy.__name__} improved score: {best_score:.1f}")

                except Exception as e:
                    logger.warning(f"Strategy {strategy.__name__} failed: {e}")
                    continue

            # Check if improvement was made
            improvement = initial_analysis.score - best_score
            if improvement >= self.improvement_threshold:
                current_content = best_content
                logger.info(f"Iteration {iteration} improved score by {improvement:.1f} points")

                iteration_history.append(IterationResult(
                    iteration=iteration,
                    content=current_content,
                    ai_score=best_score,
                    improvement_made=True,
                    prompt_adjustments={'strategy': best_strategy},
                    metadata={'improvement': improvement}
                ))

                # Check if target reached
                if best_score <= self.target_score:
                    logger.info(f"Target score reached: {best_score:.1f} <= {self.target_score}")
                    break
            else:
                logger.info(f"Insufficient improvement ({improvement:.1f} < {self.improvement_threshold}), stopping")
                break

        final_analysis = self.ai_detection_provider.analyze_text(current_content)
        logger.info(f"Final AI detection score: {final_analysis.score:.1f}")

        return current_content, iteration_history

    def _strategy_regenerate_with_nationality_emphasis(self, content: str, material_name: str,
                                                     author_info: Dict, params: Dict) -> Tuple[str, Dict]:
        """Re-generate content with enhanced nationality-specific prompts"""
        if not self.content_generator:
            logger.warning("No content generator available for re-generation strategy")
            return content, {'strategy': 'regenerate_nationality', 'status': 'skipped'}

        try:
            # Extract original parameters
            api_client = params.get('api_client')
            frontmatter_data = params.get('frontmatter_data', {})
            schema_fields = params.get('schema_fields', {})
            material_data = params.get('material_data', {})

            if not api_client:
                logger.warning("No API client available for re-generation")
                return content, {'strategy': 'regenerate_nationality', 'status': 'no_api_client'}

            # Create enhanced author info with nationality emphasis
            enhanced_author_info = author_info.copy()
            enhanced_author_info['nationality_emphasis'] = True
            enhanced_author_info['ai_detection_iteration'] = True

            # Re-generate content with original nationality prompts
            result = self.content_generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=enhanced_author_info,
                frontmatter_data=frontmatter_data,
                schema_fields=schema_fields
            )

            if result.success and result.content:
                # Extract just the content part (remove frontmatter if present)
                regenerated_content = self._extract_content_from_result(result.content)
                return regenerated_content, {
                    'strategy': 'regenerate_nationality',
                    'status': 'success',
                    'nationality_preserved': True
                }
            else:
                logger.warning(f"Re-generation failed: {result.error_message}")
                return content, {'strategy': 'regenerate_nationality', 'status': 'failed'}

        except Exception as e:
            logger.warning(f"Nationality re-generation strategy failed: {e}")
            return content, {'strategy': 'regenerate_nationality', 'status': 'error'}

    def _strategy_regenerate_with_human_elements(self, content: str, material_name: str,
                                               author_info: Dict, params: Dict) -> Tuple[str, Dict]:
        """Re-generate content with human-like elements while preserving nationality"""
        if not self.content_generator:
            logger.warning("No content generator available for human elements strategy")
            return content, {'strategy': 'regenerate_human', 'status': 'skipped'}

        try:
            # Extract original parameters
            api_client = params.get('api_client')
            frontmatter_data = params.get('frontmatter_data', {})
            schema_fields = params.get('schema_fields', {})
            material_data = params.get('material_data', {})

            if not api_client:
                logger.warning("No API client available for re-generation")
                return content, {'strategy': 'regenerate_human', 'status': 'no_api_client'}

            # Create enhanced author info with human elements emphasis
            enhanced_author_info = author_info.copy()
            enhanced_author_info['human_elements_emphasis'] = True
            enhanced_author_info['ai_detection_iteration'] = True
            enhanced_author_info['conversational_boost'] = True

            # Re-generate content with human-like elements
            result = self.content_generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=enhanced_author_info,
                frontmatter_data=frontmatter_data,
                schema_fields=schema_fields
            )

            if result.success and result.content:
                # Extract just the content part (remove frontmatter if present)
                regenerated_content = self._extract_content_from_result(result.content)
                return regenerated_content, {
                    'strategy': 'regenerate_human',
                    'status': 'success',
                    'human_elements_added': True
                }
            else:
                logger.warning(f"Human elements re-generation failed: {result.error_message}")
                return content, {'strategy': 'regenerate_human', 'status': 'failed'}

        except Exception as e:
            logger.warning(f"Human elements re-generation strategy failed: {e}")
            return content, {'strategy': 'regenerate_human', 'status': 'error'}

    def _extract_content_from_result(self, full_content: str) -> str:
        """Extract content portion from full result (remove frontmatter if present)"""
        try:
            lines = full_content.split('\n')
            # Look for frontmatter markers
            frontmatter_start = -1
            frontmatter_end = -1

            for i, line in enumerate(lines):
                if line.strip() == '---':
                    if frontmatter_start == -1:
                        frontmatter_start = i
                    else:
                        frontmatter_end = i
                        break

            if frontmatter_start >= 0 and frontmatter_end > frontmatter_start:
                # Extract content after frontmatter
                content_lines = lines[frontmatter_end + 1:]
                return '\n'.join(content_lines).strip()
            else:
                # No frontmatter found, return as-is
                return full_content.strip()

        except Exception as e:
            logger.warning(f"Failed to extract content from result: {e}")
            return full_content.strip()

    def _strategy_adjust_temperature(self, content: str, material_name: str,
                                   author_info: Dict, params: Dict) -> Tuple[str, Dict]:
        """Adjust temperature to make content more human-like"""
        # This would require re-generation with different temperature
        # For now, return original content with adjustment metadata
        return content, {'temperature_adjustment': 'decrease'}

    def _strategy_add_human_elements(self, content: str, material_name: str,
                                   author_info: Dict, params: Dict) -> Tuple[str, Dict]:
        """Add human-like elements to content"""
        # Add subtle imperfections or natural language variations
        import re

        modified_content = content

        # Add occasional contractions
        contractions = [
            (r'\bwill not\b', "won't"),
            (r'\bcannot\b', "can't"),
            (r'\bdo not\b', "don't"),
            (r'\bdoes not\b', "doesn't"),
        ]

        for pattern, replacement in contractions:
            modified_content = re.sub(pattern, replacement, modified_content, count=1)

        # Add transitional phrases
        if "However" in modified_content:
            modified_content = modified_content.replace("However", "That said", 1)

        return modified_content, {'human_elements': 'added_contractions'}

    def _strategy_modify_prompt_instructions(self, content: str, material_name: str,
                                           author_info: Dict, params: Dict) -> Tuple[str, Dict]:
        """Modify prompt to emphasize human-like writing"""
        # This would require re-generation with modified prompt
        return content, {'prompt_modification': 'human_emphasis'}

    def _strategy_change_writing_style(self, content: str, material_name: str,
                                     author_info: Dict, params: Dict) -> Tuple[str, Dict]:
        """Adjust writing style to be more conversational"""
        # Add more personal touches
        modified_content = content

        # Replace formal phrases with more conversational ones
        replacements = [
            ("It is important to note", "Keep in mind"),
            ("Furthermore", "Also"),
            ("Additionally", "Plus"),
            ("The results indicate", "What we see is"),
        ]

        for formal, casual in replacements:
            if formal in modified_content:
                modified_content = modified_content.replace(formal, casual, 1)

        return modified_content, {'style_adjustment': 'conversational'}
