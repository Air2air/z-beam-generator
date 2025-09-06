#!/usr/bin/env python3
"""
Dynamic AI Detection Prompt Generator

This module provides a dynamic prompt generation system that can evolve
the ai_detection.yaml prompts gradually based on Winston AI analysis,
similar to how the text generation system works iteratively.
"""

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from api.client_manager import create_api_client

logger = logging.getLogger(__name__)


class DynamicPromptGenerator:
    """
    Dynamic generator for AI detection prompts that evolves gradually
    based on Winston AI analysis, similar to iterative text generation.
    """

    def __init__(
        self, prompts_path: str = "components/text/prompts/ai_detection_core.yaml"
    ):
        self.prompts_path = Path(prompts_path)
        self._deepseek_client = None
        self.generation_history = []
        self.current_version = 0
        # Use modular loader for configuration
        from .utils.modular_loader import ModularConfigLoader

        self._config_loader = ModularConfigLoader()

    @property
    def deepseek_client(self):
        """Lazy initialization of DeepSeek client."""
        if self._deepseek_client is None:
            self._deepseek_client = create_api_client("deepseek")
        return self._deepseek_client

    def generate_prompt_improvements(
        self,
        winston_result: Dict[str, Any],
        content: str,
        iteration_context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Generate gradual improvements to the AI detection prompts based on Winston analysis.

        Args:
            winston_result: Winston AI detection analysis results
            content: The generated content that was analyzed
            iteration_context: Context from current iteration

        Returns:
            Dictionary of prompt improvements to apply gradually
        """
        try:
            # Analyze what aspects of the prompts need improvement
            improvement_targets = self._analyze_improvement_targets(
                winston_result, content, iteration_context
            )

            if not improvement_targets:
                logger.info("No prompt improvements needed at this time")
                return None

            # Generate specific improvements for targeted sections
            improvements = {}
            for target_section in improvement_targets:
                section_improvement = self._generate_section_improvement(
                    target_section, winston_result, content, iteration_context
                )
                if section_improvement:
                    improvements[target_section] = section_improvement

            if improvements:
                self.generation_history.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "winston_score": winston_result.get("overall_score", 0),
                        "improvements": list(improvements.keys()),
                        "version": self.current_version + 1,
                    }
                )
                self.current_version += 1

            return improvements if improvements else None

        except Exception as e:
            logger.error(f"Failed to generate prompt improvements: {e}")
            return None

    def _analyze_improvement_targets(
        self,
        winston_result: Dict[str, Any],
        content: str,
        iteration_context: Dict[str, Any],
    ) -> List[str]:
        """
        Analyze Winston results to determine which prompt sections need improvement.
        Returns a prioritized list of sections to improve.
        """
        targets = []
        score = winston_result.get("overall_score", 0)

        # Prioritize improvements based on score ranges
        if score < 30:
            # Very low score - need fundamental improvements
            targets.extend(
                [
                    "ai_detection_avoidance",
                    "human_writing_characteristics",
                    "natural_imperfections",
                ]
            )
        elif score < 50:
            # Low score - focus on authenticity
            targets.extend(
                [
                    "human_authenticity_enhancements",
                    "cognitive_variability",
                    "personal_touch",
                ]
            )
        elif score < 70:
            # Moderate score - refine existing patterns
            targets.extend(
                ["conversational_flow", "cultural_humanization", "detection_response"]
            )

        # Add random element for gradual evolution (like genetic algorithms)
        if random.random() < 0.3:  # 30% chance
            additional_targets = [
                "content_transformation_rules",
                "iteration_refinement_mechanism",
                "ai_detection_focus",
            ]
            random_target = random.choice(additional_targets)
            if random_target not in targets:
                targets.append(random_target)

        # Limit to 2-3 improvements per iteration to avoid overwhelming changes
        return targets[: random.randint(2, 3)]

    def _generate_section_improvement(
        self,
        section_name: str,
        winston_result: Dict[str, Any],
        content: str,
        iteration_context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Generate specific improvements for a particular prompt section.
        """
        try:
            # Load current prompts to understand existing content
            current_prompts = self._load_current_prompts()
            if not current_prompts:
                return None

            current_section = current_prompts.get(section_name, {})

            # Create improvement prompt based on section type
            improvement_prompt = self._create_improvement_prompt(
                section_name, current_section, winston_result, content
            )

            if not improvement_prompt:
                return None

            # Get DeepSeek's suggestions
            response = self.deepseek_client.generate_simple(
                prompt=improvement_prompt,
                max_tokens=600,  # Smaller than text generation
                temperature=0.4,  # Balanced creativity vs consistency
            )

            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            # Parse and validate improvements
            improvements = self._parse_improvement_response(response_text, section_name)

            return improvements

        except Exception as e:
            logger.error(
                f"Failed to generate improvement for section {section_name}: {e}"
            )
            return None

    def _create_improvement_prompt(
        self,
        section_name: str,
        current_section: Dict[str, Any],
        winston_result: Dict[str, Any],
        content: str,
    ) -> str:
        """
        Create a targeted improvement prompt for a specific section.
        """
        score = winston_result.get("overall_score", 0)
        classification = winston_result.get("classification", "unclear")

        base_prompt = f"""You are an expert in AI detection pattern analysis and prompt engineering. Analyze the current prompt section and suggest gradual, specific improvements based on Winston AI analysis.

CURRENT SECTION: {section_name}
WINDSOR AI ANALYSIS:
- Score: {score}/100 ({classification})
- Content Sample: {content[:400]}...

EXISTING CONTENT:
{json.dumps(current_section, indent=2)}

IMPROVEMENT GUIDELINES:
"""

        # Section-specific improvement guidelines
        section_guidelines = {
            "ai_detection_avoidance": """
- Focus on patterns that commonly trigger AI detection
- Suggest specific avoidance techniques based on current analysis
- Keep suggestions practical and actionable
- Avoid generic advice; be specific to detection triggers""",
            "human_writing_characteristics": """
- Enhance natural language patterns
- Add authentic human-like elements
- Improve conversational authenticity
- Suggest variations that reduce predictability""",
            "human_authenticity_enhancements": """
- Strengthen personal and emotional elements
- Add cultural authenticity markers
- Improve subjective opinion integration
- Enhance professional anecdote suggestions""",
            "cognitive_variability": """
- Increase thought pattern diversity
- Add uncertainty and qualification techniques
- Improve mid-thought sentence structures
- Enhance natural cognitive flow""",
            "conversational_flow": """
- Refine sentence length variation techniques
- Improve transition naturalness
- Add rhetorical device suggestions
- Enhance digression and return patterns""",
            "cultural_humanization": """
- Strengthen nationality-specific adaptations
- Add more cultural reference examples
- Improve linguistic pattern authenticity
- Enhance regional writing style suggestions""",
            "detection_response": """
- Refine score-based response strategies
- Improve threshold-based recommendations
- Add more nuanced response patterns
- Enhance iterative refinement logic""",
        }

        guidelines = section_guidelines.get(
            section_name,
            """
- Provide specific, actionable improvements
- Focus on gradual enhancement rather than complete rewrite
- Maintain consistency with existing patterns
- Suggest measurable improvements""",
        )

        improvement_prompt = (
            base_prompt
            + guidelines
            + """

Return your response as a JSON object with this structure:
{
  "improvements": [
    {
      "type": "add|modify|remove",
      "target": "subsection_name",
      "content": "specific improvement suggestion",
      "rationale": "why this improves AI detection avoidance"
    }
  ],
  "expected_impact": "description of expected improvement in Winston scores"
}

Keep improvements focused and incremental. Avoid suggesting major structural changes."""
        )

        return improvement_prompt

    def _parse_improvement_response(
        self, response_text: str, section_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse DeepSeek's improvement response and format it for application.
        """
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            # Parse JSON
            improvements_data = json.loads(response_text.strip())

            # Validate structure
            if "improvements" not in improvements_data:
                logger.warning(f"No improvements found in response for {section_name}")
                return None

            # Format for application
            formatted_improvements = {
                "section": section_name,
                "improvements": improvements_data["improvements"],
                "expected_impact": improvements_data.get(
                    "expected_impact", "Gradual improvement"
                ),
                "timestamp": datetime.now().isoformat(),
                "version": self.current_version + 1,
            }

            return formatted_improvements

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse improvement response for {section_name}: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Error parsing improvement response: {e}")
            return None

    def apply_gradual_improvements(self, improvements: Dict[str, Any]) -> bool:
        """
        Apply improvements gradually to the prompts file.
        Only applies a subset of improvements to avoid overwhelming changes.
        """
        try:
            # Load current prompts
            current_prompts = self._load_current_prompts()
            if not current_prompts:
                return False

            # Apply only 1-2 improvements per section to keep changes gradual
            applied_improvements = 0
            max_improvements = 2

            for section_name, section_improvements in improvements.items():
                if applied_improvements >= max_improvements:
                    break

                if section_name not in current_prompts:
                    continue

                section_data = section_improvements.get("improvements", [])
                section_prompts = current_prompts[section_name]

                # Apply improvements one at a time
                for improvement in section_data[
                    :1
                ]:  # Only one improvement per section per iteration
                    if self._apply_single_improvement(section_prompts, improvement):
                        applied_improvements += 1
                        logger.info(
                            f"Applied improvement to {section_name}: {improvement.get('content', '')[:50]}..."
                        )
                        break

            if applied_improvements > 0:
                # Save updated prompts
                self._save_updated_prompts(current_prompts)
                logger.info(
                    f"Applied {applied_improvements} gradual improvements to prompts"
                )
                return True
            else:
                logger.info("No improvements were applied")
                return False

        except Exception as e:
            logger.error(f"Failed to apply gradual improvements: {e}")
            return False

    def _apply_single_improvement(
        self, section_prompts: Dict[str, Any], improvement: Dict[str, Any]
    ) -> bool:
        """
        Apply a single improvement to a prompt section.
        """
        try:
            improvement_type = improvement.get("type", "add")
            target = improvement.get("target", "")
            content = improvement.get("content", "")

            if improvement_type == "add":
                # Add new content to the target subsection
                if target and isinstance(section_prompts, dict):
                    if target not in section_prompts:
                        section_prompts[target] = []
                    if isinstance(section_prompts[target], list):
                        if content not in section_prompts[target]:
                            section_prompts[target].append(content)
                            return True
                elif isinstance(section_prompts, list):
                    # Add to main section list
                    if content not in section_prompts:
                        section_prompts.append(content)
                        return True

            elif improvement_type == "modify":
                # Modify existing content (simplified - just add as new for now)
                if isinstance(section_prompts, list) and content not in section_prompts:
                    section_prompts.append(f"Enhanced: {content}")
                    return True

            elif improvement_type == "remove":
                # Remove specific content (not implemented for safety)
                pass

            return False

        except Exception as e:
            logger.error(f"Failed to apply single improvement: {e}")
            return False

    def _load_current_prompts(self) -> Optional[Dict[str, Any]]:
        """Load current prompts using modular configuration loader."""
        try:
            # Use modular loader to get the complete configuration
            prompts = self._config_loader.load_config(use_modular=True)

            if not prompts:
                logger.warning("Failed to load prompts using modular loader")
                return None

            # Import config for variable substitution
            from run import AI_DETECTION_CONFIG

            # Convert to string for template substitution, then back to dict
            yaml_content = yaml.dump(
                prompts, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
            processed_content = self.substitute_config_variables(
                yaml_content, AI_DETECTION_CONFIG
            )

            # Parse the processed YAML
            return yaml.safe_load(processed_content)

        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            return None

    def substitute_config_variables(self, content: str, config: Dict[str, Any]) -> str:
        """Substitute template variables with config values."""
        substitutions = {
            "${target_score}": str(config.get("target_score", 70)),
            "${winston_human_range[0]}": str(
                config.get("winston_human_range", (70, 100))[0]
            ),
            "${winston_human_range[1]}": str(
                config.get("winston_human_range", (70, 100))[1]
            ),
            "${winston_unclear_range[0]}": str(
                config.get("winston_unclear_range", (30, 70))[0]
            ),
            "${winston_unclear_range[1]}": str(
                config.get("winston_unclear_range", (30, 70))[1]
            ),
            "${winston_ai_range[0]}": str(config.get("winston_ai_range", (0, 30))[0]),
            "${winston_ai_range[1]}": str(config.get("winston_ai_range", (0, 30))[1]),
        }

        processed_content = content
        for variable, value in substitutions.items():
            processed_content = processed_content.replace(variable, value)

        return processed_content

    def _convert_to_template_variables(
        self, content: str, config: Dict[str, Any]
    ) -> str:
        """Convert config values back to template variables."""
        reverse_substitutions = {
            str(config.get("target_score", 70)): "${target_score}",
            str(
                config.get("winston_human_range", (70, 100))[0]
            ): "${winston_human_range[0]}",
            str(
                config.get("winston_human_range", (70, 100))[1]
            ): "${winston_human_range[1]}",
            str(
                config.get("winston_unclear_range", (30, 70))[0]
            ): "${winston_unclear_range[0]}",
            str(
                config.get("winston_unclear_range", (30, 70))[1]
            ): "${winston_unclear_range[1]}",
            str(config.get("winston_ai_range", (0, 30))[0]): "${winston_ai_range[0]}",
            str(config.get("winston_ai_range", (0, 30))[1]): "${winston_ai_range[1]}",
        }

        processed_content = content
        for value, variable in reverse_substitutions.items():
            processed_content = processed_content.replace(value, variable)

        return processed_content

    def _save_updated_prompts(self, prompts: Dict[str, Any]) -> None:
        """Save updated prompts with template variables restored."""
        try:
            # NOTE: This is a simplified approach for the modular system
            # In a full implementation, changes should be distributed across
            # the appropriate modular component files

            # Import config for reverse substitution
            from run import AI_DETECTION_CONFIG

            # Convert config values back to template variables
            yaml_content = yaml.dump(
                prompts, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
            templated_content = self._convert_to_template_variables(
                yaml_content, AI_DETECTION_CONFIG
            )

            # For now, save to the core file (this is a limitation of the current approach)
            # A more sophisticated implementation would update individual modular components
            core_path = Path("components/text/prompts/ai_detection_core.yaml")
            with open(core_path, "w", encoding="utf-8") as f:
                f.write(templated_content)

            logger.info(
                f"Saved updated prompts to {core_path} (modular components not updated)"
            )
        except Exception as e:
            logger.error(f"Failed to save updated prompts: {e}")
            raise

    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Get the evolution history of prompt improvements."""
        return self.generation_history.copy()

    def get_current_version(self) -> int:
        """Get the current version number of the prompts."""
        return self.current_version
