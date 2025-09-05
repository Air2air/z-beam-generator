#!/usr/bin/env python3
"""
Content Component Generator

Lightweight wrapper for ComponentGeneratorFactory integration.
Provides a clean interface to the fail_fast_generator.py content generation system.
"""

import logging
import datetime
import random
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)

class TextComponentGenerator(APIComponentGenerator):
    """
    Text component generator that wraps the fail_fast_generator.

    This is a lightweight wrapper that integrates with ComponentGeneratorFactory
    while delegating the actual content generation to fail_fast_generator.py.
    """

    def __init__(self, ai_detection_service=None):
        """Initialize the text component generator."""
        super().__init__("text")
        self.ai_detection_service = ai_detection_service
        
        # Import dynamic configuration functions at initialization
        from run import get_dynamic_config_for_content
        self.get_dynamic_config = get_dynamic_config_for_content

    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """
        Generate content using simplified prompting without complex optimization.

        This simplified version focuses on basic content generation using
        straightforward prompting, leaving complex optimization to the
        decoupled optimization system.

        Args:
            material_name: Name of the material
            material_data: Material data dictionary
            api_client: API client for content generation
            author_info: Author information
            frontmatter_data: Frontmatter data from previous generation
            schema_fields: Schema fields (not used for content)

        Returns:
            ComponentResult with generated content
        """
        try:
            # Import the fail_fast_generator
            from .generators.fail_fast_generator import create_fail_fast_generator

            logger.info(f"📝 Generating content for {material_name} using simplified approach")

            # Create generator with basic settings (no complex optimization)
            generator = create_fail_fast_generator(
                max_retries=3,
                retry_delay=1.0,
                enable_scoring=False,  # Disable complex scoring in component generation
                skip_ai_detection=True  # Skip AI detection - handle in optimization system
            )

            # Generate content with basic author info
            current_author_info = author_info.copy() if author_info else {}
            if not current_author_info:
                current_author_info = {
                    "name": "Technical Expert",
                    "country": "usa",
                    "language": "english"
                }

            # Simple content generation - no iteration or complex optimization
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=current_author_info,
                frontmatter_data=frontmatter_data
            )

            if not result.success:
                logger.warning(f"❌ Content generation failed for {material_name}: {result.error_message}")
                return ComponentResult(
                    component_type="text",
                    content="",
                    success=False,
                    error_message=result.error_message
                )

            logger.info(f"✅ Content generated successfully for {material_name}")
            return ComponentResult(
                component_type="text",
                content=result.content,
                success=True,
                error_message=None
            )

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return ComponentResult(
                component_type="text",
                content="",
                success=False,
                error_message=str(e)
            )

    def _update_frontmatter_with_iterations(self, content: str, score: float, ai_result=None, iteration_history=None, dynamic_config=None) -> str:
        """Update the frontmatter with AI detection score and iteration history."""
        
        try:
            lines = content.split('\n')
            updated_lines = []
            
            # Find the closing frontmatter marker
            frontmatter_end_idx = -1
            for i, line in enumerate(lines):
                if line.strip() == '---' and i > 0:  # Found closing frontmatter marker
                    frontmatter_end_idx = i
                    break
            
            if frontmatter_end_idx == -1:
                # No frontmatter found, add it at the beginning
                logger.info("No frontmatter found, adding AI detection data at the end")
                updated_lines = lines
                # Add AI detection data at the end
                updated_lines.append("")  # Empty line before additions
                updated_lines.append("---")  # Start frontmatter
            else:
                # Insert before the closing frontmatter marker
                updated_lines = lines[:frontmatter_end_idx]
            
            # Add AI detection analysis
            ai_lines = [
                "ai_detection_analysis:",
                f"  score: {score}",
            ]
            
            if ai_result:
                ai_lines.extend([
                    f"  confidence: {ai_result.confidence}",
                    f"  classification: \"{ai_result.classification}\"",
                    "  provider: \"winston\"",
                    f"  processing_time: {ai_result.processing_time}",
                ])
                
                if ai_result.details:
                    ai_lines.append("  details:")
                    for key, value in ai_result.details.items():
                        # Include sentence-level details for Winston
                        if key == "sentences" and isinstance(value, list):
                            ai_lines.append("    sentences:")
                            for sentence_data in value[:dynamic_config.get("max_sentence_details", 5) if dynamic_config else 5]:  # Limit to first N sentences
                                if isinstance(sentence_data, dict):
                                    ai_lines.append("      - text: \"{}\"".format(sentence_data.get('text', '').replace('"', '\\"')))
                                    ai_lines.append("        score: {}".format(sentence_data.get('score', 0.0)))
                        else:
                            ai_lines.append(f"    {key}: {value}")
            else:
                # Handle case where no AI detection was performed
                ai_lines.extend([
                    "  confidence: 0.0",
                    "  classification: \"unknown\"",
                    "  provider: \"none\"",
                    "  processing_time: 0.0",
                ])
                logger.info("ℹ️ No AI detection results available for frontmatter")
            
            updated_lines.extend(ai_lines)
            
            # Add iteration history
            if iteration_history:
                updated_lines.extend([
                    "iteration_history:"
                ])
                
                for iter_data in iteration_history:
                    updated_lines.extend([
                        f"  - iteration: {iter_data['iteration_number']}",
                        f"    max_iterations: {iter_data['max_iterations']}",
                        f"    timestamp: \"{iter_data['timestamp']}\"",
                        f"    ai_detection_performed: {str(iter_data['ai_detection_performed']).lower()}",
                        f"    ai_detection_skipped: {str(iter_data['ai_detection_skipped']).lower()}",
                        f"    score: {iter_data['score']}",
                        f"    classification: \"{iter_data['classification']}\"",
                        f"    improvement: {iter_data['improvement']}",
                        f"    target_reached: {str(iter_data['target_reached']).lower()}",
                        f"    content_length_chars: {iter_data['content_length_chars']}",
                        f"    content_length_words: {iter_data['content_length_words']}",
                        f"    content_change_percent_chars: {iter_data['content_change_percent_chars']}",
                        f"    content_change_percent_words: {iter_data['content_change_percent_words']}",
                    ])
                    
                    # Add DeepSeek response if available
                    if 'deepseek_response' in iter_data and iter_data['deepseek_response']:
                        # Clean and format the DeepSeek response for YAML
                        deepseek_clean = iter_data['deepseek_response'].strip()
                        if deepseek_clean.startswith("```json"):
                            deepseek_clean = deepseek_clean[7:]
                        if deepseek_clean.endswith("```"):
                            deepseek_clean = deepseek_clean[:-3]
                        # Escape quotes and format for YAML
                        deepseek_formatted = deepseek_clean.replace('"', '\\"').replace('\n', '\\n')
                        updated_lines.append(f"    deepseek_response: \"{deepseek_formatted}\"")
                    
                    if iter_data['enhancements_applied']:
                        enhancements_str = ', '.join(f'"{enh}"' for enh in iter_data['enhancements_applied'])
                        updated_lines.append(f"    enhancements_applied: [{enhancements_str}]")
                    else:
                        updated_lines.append("    enhancements_applied: []")
            
            # Add configuration optimization info
            updated_lines.extend([
                "configuration_optimization:",
                "  enabled: true",
                "  optimizer: \"deepseek\"",
                "  optimization_method: \"iterative_config_modification\"",
                f"  total_iterations: {len(iteration_history) if iteration_history else 0}",
                "---"  # Close frontmatter
            ])
            
            # Add the rest of the content
            if frontmatter_end_idx != -1:
                updated_lines.extend(lines[frontmatter_end_idx:])
            
            return '\n'.join(updated_lines)
            
        except Exception as e:
            logger.warning(f"Failed to update frontmatter with iterations: {e}")
            return content