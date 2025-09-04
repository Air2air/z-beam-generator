#!/usr/bin/env python3
"""
Dynamic Prompt Generation System

A standalone system for dynamically evolving AI detection prompts based on
Winston AI analysis, similar to iterative text generation systems.

This system provides:
- Intelligent prompt evolution based on performance analysis
- Gradual improvements to avoid overwhelming changes
- Template variable substitution for dynamic configuration
- Integration with DeepSeek for intelligent improvements
"""

import logging
import random
from typing import Dict, Any, Optional, List
from pathlib import Path

from .dynamic_prompt_generator import DynamicPromptGenerator
from .prompt_evolution_manager import PromptEvolutionManager
from .winston_analyzer import WinstonAnalyzer

logger = logging.getLogger(__name__)

class DynamicPromptSystem:
    """
    Main interface for the Dynamic Prompt Generation System.

    This system analyzes Winston AI detection results and gradually evolves
    the ai_detection.yaml prompts to improve future content generation.
    """

    def __init__(self, prompts_path: str = "components/text/prompts/ai_detection.yaml"):
        """
        Initialize the dynamic prompt system.

        Args:
            prompts_path: Path to the ai_detection.yaml prompts file
        """
        self.prompts_path = Path(prompts_path)

        # Initialize core components
        self.generator = DynamicPromptGenerator(prompts_path)
        self.evolution_manager = PromptEvolutionManager(prompts_path)
        self.winston_analyzer = WinstonAnalyzer()

        logger.info("🎯 Dynamic Prompt System initialized")

    def analyze_and_evolve(self, winston_result: Dict[str, Any],
                          content: str, iteration_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for analyzing Winston results and evolving prompts.

        Args:
            winston_result: Winston AI detection analysis results
            content: The generated content that was analyzed
            iteration_context: Context from current iteration

        Returns:
            Dictionary with evolution results and status
        """
        try:
            logger.info("🤖 Starting dynamic prompt evolution analysis...")

            # Analyze what needs improvement
            analysis = self.winston_analyzer.analyze_improvement_needs(
                winston_result, content, iteration_context
            )

            if not analysis['needs_improvement']:
                logger.info("ℹ️ No prompt improvements needed at this time")
                return {
                    'success': True,
                    'improvements_applied': 0,
                    'message': 'No improvements needed'
                }

            # Generate improvements
            improvements = self.generator.generate_prompt_improvements(
                winston_result, content, iteration_context
            )

            if not improvements:
                logger.info("ℹ️ No improvements generated")
                return {
                    'success': True,
                    'improvements_applied': 0,
                    'message': 'No improvements generated'
                }

            # Apply improvements gradually
            applied_count = 0
            if random.random() < 0.4:  # 40% chance to apply improvements
                applied = self.generator.apply_gradual_improvements(improvements)
                if applied:
                    applied_count = len(improvements)
                    logger.info(f"✅ Applied {applied_count} gradual prompt improvements")
                else:
                    logger.info("ℹ️ No improvements applied this iteration")
            else:
                logger.info("⏭️ Skipping improvement application this iteration (gradual evolution)")

            # Update evolution history
            self.evolution_manager.record_evolution(
                winston_result, improvements, applied_count > 0
            )

            return {
                'success': True,
                'improvements_generated': len(improvements),
                'improvements_applied': applied_count,
                'analysis': analysis,
                'message': f'Generated {len(improvements)} improvements, applied {applied_count}'
            }

        except Exception as e:
            logger.error(f"Failed to evolve prompts: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Evolution failed'
            }

    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Get the complete evolution history of prompt improvements."""
        return self.evolution_manager.get_history()

    def get_current_stats(self) -> Dict[str, Any]:
        """Get current statistics about the prompt evolution system."""
        return {
            'current_version': self.generator.get_current_version(),
            'total_evolutions': len(self.evolution_manager.get_history()),
            'prompts_path': str(self.prompts_path),
            'system_status': 'active'
        }

    def force_evolution(self, winston_result: Dict[str, Any],
                       content: str, iteration_context: Dict[str, Any]) -> bool:
        """
        Force prompt evolution regardless of random chance.
        Useful for testing or when specific improvements are needed.
        """
        try:
            logger.info("🔧 Forcing prompt evolution...")

            improvements = self.generator.generate_prompt_improvements(
                winston_result, content, iteration_context
            )

            if improvements:
                applied = self.generator.apply_gradual_improvements(improvements)
                if applied:
                    self.evolution_manager.record_evolution(
                        winston_result, improvements, True
                    )
                    logger.info("✅ Forced evolution completed successfully")
                    return True

            logger.info("ℹ️ Forced evolution found no improvements to apply")
            return False

        except Exception as e:
            logger.error(f"Failed to force evolution: {e}")
            return False
