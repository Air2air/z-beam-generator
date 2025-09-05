"""
AI Detection Prompt Optimizer

This module extends the AIDetectionConfigOptimizer to automatically update
the ai_detection.yaml prompt file based on Winston AI analysis results.
Updates are targeted and incremental to avoid bloat.
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

from api.client_manager import create_api_client

logger = logging.getLogger(__name__)

class AIDetectionPromptOptimizer:
    """
    Optimizes AI detection prompts using Winston AI analysis results.
    Performs targeted updates to avoid bloat while maintaining comprehensive guidance.
    """

    def __init__(self, prompts_path: str = "components/text/prompts/ai_detection_core.yaml"):
        self.prompts_path = Path(prompts_path)
        self._deepseek_client = None
        self.backup_created = False
        # Use modular loader for configuration
        from .prompts.utils.modular_loader import ModularConfigLoader
        self._config_loader = ModularConfigLoader()

    @property
    def deepseek_client(self):
        """Lazy initialization of DeepSeek client."""
        if self._deepseek_client is None:
            self._deepseek_client = create_api_client("deepseek")
        return self._deepseek_client

    def optimize_prompts(self, winston_result: Dict[str, Any],
                        content: str, iteration_context: Dict[str, Any]) -> bool:
        """
        Perform targeted optimization of AI detection prompts based on Winston analysis.

        Args:
            winston_result: Winston AI detection analysis results
            content: The generated content that was analyzed
            iteration_context: Context from current iteration (scores, history, etc.)

        Returns:
            bool: True if prompts were updated, False otherwise
        """
        try:
            # Load current prompts
            current_prompts = self._load_current_prompts()
            if not current_prompts:
                logger.warning("Could not load current prompts for optimization")
                return False

            # Analyze what needs updating based on Winston results
            updates_needed = self._analyze_update_requirements(
                winston_result, content, iteration_context, current_prompts
            )

            if not updates_needed:
                logger.info("No prompt updates needed based on Winston analysis")
                return False

            # Generate targeted updates using DeepSeek
            prompt_updates = self._generate_targeted_updates(
                winston_result, content, iteration_context, updates_needed
            )

            if not prompt_updates:
                logger.info("No actionable prompt updates generated")
                return False

            # Apply updates incrementally
            updated_prompts = self._apply_incremental_updates(
                current_prompts, prompt_updates
            )

            # Validate and save
            if self._validate_updated_prompts(updated_prompts):
                self._create_backup_if_needed()
                self._save_updated_prompts(updated_prompts)
                logger.info("Successfully updated AI detection prompts")
                return True
            else:
                logger.warning("Prompt validation failed, updates not applied")
                return False

        except Exception as e:
            logger.error(f"Failed to optimize prompts: {e}")
            return False

    def _load_current_prompts(self) -> Optional[Dict[str, Any]]:
        """Load the current AI detection prompts using modular loader."""
        try:
            # Use modular loader to get the complete configuration
            prompts = self._config_loader.load_config(use_modular=True)
            
            if not prompts:
                logger.warning("Could not load prompts using modular loader")
                return None
            
            # Import config for variable substitution
            from run import AI_DETECTION_CONFIG
            
            # Convert to string for template substitution, then back to dict
            yaml_content = yaml.dump(prompts, default_flow_style=False, sort_keys=False, allow_unicode=True)
            processed_content = self.substitute_config_variables(yaml_content, AI_DETECTION_CONFIG)
            
            # Parse the processed YAML
            return yaml.safe_load(processed_content)
            
        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            return None

    def _analyze_update_requirements(self, winston_result: Dict[str, Any],
                                   content: str, iteration_context: Dict[str, Any],
                                   current_prompts: Dict[str, Any]) -> List[str]:
        """
        Analyze Winston results to determine what prompt sections need updating.
        Returns list of section keys that need optimization.
        """
        updates_needed = []

        # Extract key metrics from Winston result
        overall_score = winston_result.get('overall_score', 0)
        classification = winston_result.get('classification', 'unclear')

        # Check if we need to update detection avoidance patterns
        if overall_score < 30 and classification == 'ai':
            updates_needed.append('ai_detection_avoidance')

        # Check if we need to enhance human authenticity elements
        if overall_score < 50:
            updates_needed.append('human_authenticity_enhancements')

        # Check if sentence patterns need refinement
        sentence_analysis = winston_result.get('sentence_analysis', {})
        if sentence_analysis.get('low_score_percentage', 0) > 15:
            updates_needed.append('cognitive_variability')

        # Check if cultural adaptation needs updating based on iteration history
        iteration_history = iteration_context.get('iteration_history', [])
        if len(iteration_history) > 2:
            scores = [iter.get('score', 0) for iter in iteration_history[-3:]]
            if scores and max(scores) - min(scores) > 20:  # Significant variation
                updates_needed.append('cultural_humanization')

        # Check if success metrics need updating
        if overall_score > 70 and classification == 'human':
            updates_needed.append('success_metrics')

        return updates_needed

    def _generate_targeted_updates(self, winston_result: Dict[str, Any],
                                 content: str, iteration_context: Dict[str, Any],
                                 sections_to_update: List[str]) -> Optional[Dict[str, Any]]:
        """
        Generate targeted updates for specific prompt sections using DeepSeek.
        Only updates the sections identified as needing improvement.
        """
        try:
            # Build focused prompt for DeepSeek
            update_prompt = self._build_update_prompt(
                winston_result, content, iteration_context, sections_to_update
            )

            # Get DeepSeek's recommendations
            response = self.deepseek_client.generate_simple(
                prompt=update_prompt,
                max_tokens=800,  # Smaller than config optimization
                temperature=0.2  # More conservative for prompt updates
            )

            # Parse the response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)

            # Clean and parse JSON response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            updates = json.loads(response_text.strip())

            # Validate that we only got updates for requested sections
            validated_updates = {}
            for section in sections_to_update:
                if section in updates:
                    validated_updates[section] = updates[section]

            return validated_updates if validated_updates else None

        except Exception as e:
            logger.error(f"Failed to generate targeted updates: {e}")
            return None

    def _build_update_prompt(self, winston_result: Dict[str, Any],
                           content: str, iteration_context: Dict[str, Any],
                           sections_to_update: List[str]) -> str:
        """
        Build a focused prompt for DeepSeek to generate targeted prompt updates.
        """

        # Extract key analysis data
        overall_score = winston_result.get('overall_score', 0)
        classification = winston_result.get('classification', 'unclear')
        readability_score = winston_result.get('readability_score')

        prompt = f"""You are an expert in AI detection pattern analysis and prompt optimization. Based on the Winston AI analysis results, provide targeted updates to specific sections of the AI detection prompt file.

WINDSOR AI ANALYSIS RESULTS:
- Overall Score: {overall_score:.1f}/100 ({classification})
- Readability Score: {readability_score:.1f} (if available)
- Content Sample: {content[:300]}...

SECTIONS REQUIRING UPDATES: {', '.join(sections_to_update)}

For each section that needs updating, provide specific, actionable improvements that will help future content generation avoid AI detection patterns. Focus on:

1. **ai_detection_avoidance**: Update algorithmic patterns to avoid based on current detection triggers
2. **human_authenticity_enhancements**: Add specific techniques that improve human-like qualities
3. **cognitive_variability**: Enhance sentence structure and thought pattern variations
4. **cultural_humanization**: Refine cultural adaptation strategies
5. **success_metrics**: Update target ranges based on current performance

Return ONLY a JSON object with updates for the specified sections. Each update should be concise and actionable:

{{
  "section_name": {{
    "additions": ["new specific technique or pattern"],
    "modifications": ["updated existing guidance"],
    "removals": ["obsolete pattern to remove"]
  }}
}}

Keep updates minimal and focused - avoid comprehensive rewrites."""

        return prompt

    def _apply_incremental_updates(self, current_prompts: Dict[str, Any],
                                 updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply incremental updates to the prompts without replacing entire sections.
        This prevents bloat by only adding/modifying specific elements.
        """
        updated_prompts = current_prompts.copy()

        for section_key, section_updates in updates.items():
            if section_key not in updated_prompts:
                logger.warning(f"Section {section_key} not found in current prompts")
                continue

            section = updated_prompts[section_key]

            # Apply additions
            if 'additions' in section_updates:
                additions = section_updates['additions']
                if isinstance(additions, list):
                    # Add to existing list if it exists, otherwise create new
                    if isinstance(section, list):
                        section.extend(additions)
                    elif isinstance(section, dict):
                        # Find appropriate sub-section to extend
                        for sub_key, sub_value in section.items():
                            if isinstance(sub_value, list):
                                sub_value.extend(additions)
                                break
                        else:
                            # No list found, add as new key
                            section['additional_techniques'] = additions

            # Apply modifications (replace specific items)
            if 'modifications' in section_updates:
                modifications = section_updates['modifications']
                if isinstance(modifications, list) and isinstance(section, list):
                    # Replace matching items
                    for i, item in enumerate(section):
                        for mod in modifications:
                            if isinstance(mod, dict) and 'old' in mod and 'new' in mod:
                                if mod['old'] in item:
                                    section[i] = item.replace(mod['old'], mod['new'])

            # Apply removals
            if 'removals' in section_updates:
                removals = section_updates['removals']
                if isinstance(removals, list):
                    if isinstance(section, list):
                        section[:] = [item for item in section if not any(removal in item for removal in removals)]
                    elif isinstance(section, dict):
                        for sub_key, sub_value in section.items():
                            if isinstance(sub_value, list):
                                section[sub_key] = [item for item in sub_value if not any(removal in item for removal in removals)]

        return updated_prompts

    def _validate_updated_prompts(self, prompts: Dict[str, Any]) -> bool:
        """
        Validate that updated prompts maintain structure and don't introduce errors.
        """
        try:
            # Check that all required top-level keys exist
            required_keys = [
                'ai_detection_focus', 'human_writing_characteristics',
                'ai_detection_avoidance', 'human_authenticity_enhancements',
                'cultural_humanization', 'content_transformation_rules',
                'success_metrics'
            ]

            for key in required_keys:
                if key not in prompts:
                    logger.error(f"Missing required key: {key}")
                    return False

            # Validate YAML structure
            yaml_str = yaml.dump(prompts, default_flow_style=False)
            yaml.safe_load(yaml_str)  # This will raise an exception if invalid

            # Check for reasonable size (prevent bloat)
            yaml_size = len(yaml_str)
            if yaml_size > 50000:  # 50KB limit
                logger.warning(f"Updated prompts file is large: {yaml_size} bytes")
                # Still allow but log warning

            return True

        except Exception as e:
            logger.error(f"Prompt validation failed: {e}")
            return False

    def _create_backup_if_needed(self) -> None:
        """Create a backup of the current prompts file if not already done."""
        if not self.backup_created:
            try:
                if self.prompts_path.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = self.prompts_path.with_suffix(f".backup_{timestamp}.yaml")
                    backup_path.write_text(self.prompts_path.read_text(encoding='utf-8'), encoding='utf-8')
                    logger.info(f"Created prompts backup: {backup_path}")
                    self.backup_created = True
            except Exception as e:
                logger.warning(f"Failed to create prompts backup: {e}")

    def substitute_config_variables(self, prompts_content: str, config: Dict[str, Any]) -> str:
        """
        Substitute template variables in prompts with actual config values.
        
        Args:
            prompts_content: Raw YAML content with template variables
            config: AI_DETECTION_CONFIG dictionary
            
        Returns:
            Processed content with variables substituted
        """
        import re
        
        # Define variable substitution patterns
        substitutions = {
            '${target_score}': str(config.get('target_score', 70)),
            '${winston_human_range[0]}': str(config.get('winston_human_range', (70, 100))[0]),
            '${winston_human_range[1]}': str(config.get('winston_human_range', (70, 100))[1]),
            '${winston_unclear_range[0]}': str(config.get('winston_unclear_range', (30, 70))[0]),
            '${winston_unclear_range[1]}': str(config.get('winston_unclear_range', (30, 70))[1]),
            '${winston_ai_range[0]}': str(config.get('winston_ai_range', (0, 30))[0]),
            '${winston_ai_range[1]}': str(config.get('winston_ai_range', (0, 30))[1]),
            '${max_iterations}': str(config.get('max_iterations', 5)),
            '${improvement_threshold}': str(config.get('improvement_threshold', 3.0)),
            '${human_threshold}': str(config.get('human_threshold', 75.0))
        }
        
        # Apply substitutions
        processed_content = prompts_content
        for variable, value in substitutions.items():
            processed_content = processed_content.replace(variable, value)
        
        return processed_content

    def _convert_to_template_variables(self, content: str, config: Dict[str, Any]) -> str:
        """
        Convert config values back to template variables when saving.
        This ensures the file remains templated for future use.
        
        Args:
            content: Processed content with actual values
            config: AI_DETECTION_CONFIG dictionary
            
        Returns:
            Content with template variables restored
        """
        # Define reverse substitutions (value -> variable)
        reverse_substitutions = {
            str(config.get('target_score', 70)): '${target_score}',
            str(config.get('winston_human_range', (70, 100))[0]): '${winston_human_range[0]}',
            str(config.get('winston_human_range', (70, 100))[1]): '${winston_human_range[1]}',
            str(config.get('winston_unclear_range', (30, 70))[0]): '${winston_unclear_range[0]}',
            str(config.get('winston_unclear_range', (30, 70))[1]): '${winston_unclear_range[1]}',
            str(config.get('winston_ai_range', (0, 30))[0]): '${winston_ai_range[0]}',
            str(config.get('winston_ai_range', (0, 30))[1]): '${winston_ai_range[1]}',
            str(config.get('max_iterations', 5)): '${max_iterations}',
            str(config.get('improvement_threshold', 3.0)): '${improvement_threshold}',
            str(config.get('human_threshold', 75.0)): '${human_threshold}'
        }
        
        # Apply reverse substitutions
        processed_content = content
        for value, variable in reverse_substitutions.items():
            processed_content = processed_content.replace(value, variable)
        
        return processed_content

    def _save_updated_prompts(self, prompts: Dict[str, Any]) -> None:
        """Save the updated prompts to file."""
        try:
            # NOTE: This is a simplified approach for the modular system
            # In a full implementation, changes should be distributed across
            # the appropriate modular component files
            
            # Import config for reverse substitution
            from run import AI_DETECTION_CONFIG
            
            # Convert config values back to template variables
            yaml_content = yaml.dump(prompts, default_flow_style=False, sort_keys=False, allow_unicode=True)
            templated_content = self._convert_to_template_variables(yaml_content, AI_DETECTION_CONFIG)
            
            # For now, save to the core file (this is a limitation of the current approach)
            # A more sophisticated implementation would update individual modular components
            core_path = Path("components/text/prompts/ai_detection_core.yaml")
            with open(core_path, 'w', encoding='utf-8') as f:
                f.write(templated_content)
            
            logger.info(f"Saved updated prompts to {core_path} (modular components not updated)")
        except Exception as e:
            logger.error(f"Failed to save updated prompts: {e}")
            raise

    def restore_backup(self, backup_timestamp: Optional[str] = None) -> bool:
        """Restore prompts from backup."""
        try:
            if backup_timestamp:
                backup_path = self.prompts_path.with_suffix(f".backup_{backup_timestamp}.yaml")
            else:
                # Find the most recent backup
                backup_files = list(self.prompts_path.parent.glob(f"{self.prompts_path.stem}.backup_*.yaml"))
                if not backup_files:
                    logger.warning("No prompt backup files found")
                    return False
                backup_path = max(backup_files, key=lambda p: p.stat().st_mtime)

            if backup_path.exists():
                backup_content = backup_path.read_text(encoding='utf-8')
                self.prompts_path.write_text(backup_content, encoding='utf-8')
                logger.info(f"Restored prompts from backup: {backup_path}")
                return True
            else:
                logger.warning(f"Backup file not found: {backup_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to restore prompts backup: {e}")
            return False