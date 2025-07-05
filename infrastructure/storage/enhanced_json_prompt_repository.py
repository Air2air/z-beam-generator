"""
Enhanced JSON-based prompt repository that handles all prompt types (sections, detection, improvement).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from generator.core.interfaces.services import IPromptRepository
from generator.core.domain.models import PromptTemplate
from generator.infrastructure.storage.exceptions import FileOperationError

logger = logging.getLogger(__name__)


class EnhancedJsonPromptRepository(IPromptRepository):
    """
    Enhanced JSON-based repository for prompt templates that handles sections, detection,
    and improvement prompts with fallback to file-based templates.
    """

    def __init__(self, prompts_dir: Path):
        self._prompts_dir = Path(prompts_dir)
        # Directory structure
        self._root_dir = Path(prompts_dir).parent.parent
        self._sections_file = self._root_dir / "sections" / "sections.json"
        self._detection_file = self._root_dir / "detection" / "detection_prompts.json"
        self._improvement_file = (
            self._root_dir / "detection" / "improvement_prompts.json"
        )

        # Caches for different prompt types
        self._section_cache = {}
        self._detection_cache = {}
        self._improvement_cache = {}
        self._loaded = {"sections": False, "detection": False, "improvement": False}

        if not self._prompts_dir.exists():
            raise FileOperationError(
                f"Prompts directory does not exist: {prompts_dir}",
                str(prompts_dir),
                "initialize_repository",
            )

        # Initialize caches
        self._load_sections_json()
        self._load_detection_json()
        self._load_improvement_json()

    def _load_sections_json(self) -> bool:
        """Load sections from the JSON file."""
        try:
            if not self._sections_file.exists():
                logger.debug(f"Sections JSON file not found: {self._sections_file}")
                return False

            with open(self._sections_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            sections = data.get("sections", [])
            # Cache sections by name
            for section in sections:
                self._section_cache[section["name"]] = section

            self._loaded["sections"] = True
            logger.debug(f"Loaded {len(sections)} sections from {self._sections_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading sections JSON: {e}")
            return False

    def _load_detection_json(self) -> bool:
        """Load detection prompts from the JSON file."""
        try:
            if not self._detection_file.exists():
                logger.debug(f"Detection JSON file not found: {self._detection_file}")
                return False

            with open(self._detection_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            detection_prompts = data.get("detection_prompts", [])
            # Cache detection prompts by name
            for prompt in detection_prompts:
                self._detection_cache[prompt["name"]] = prompt

            self._loaded["detection"] = True
            logger.debug(
                f"Loaded {len(detection_prompts)} detection prompts from {self._detection_file}"
            )
            return True
        except Exception as e:
            logger.error(f"Error loading detection JSON: {e}")
            return False

    def _load_improvement_json(self) -> bool:
        """Load improvement prompts from the JSON file."""
        try:
            if not self._improvement_file.exists():
                logger.debug(
                    f"Improvement JSON file not found: {self._improvement_file}"
                )
                return False

            with open(self._improvement_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            improvement_prompts = data.get("improvement_prompts", [])
            # Cache improvement prompts by name
            for prompt in improvement_prompts:
                self._improvement_cache[prompt["name"]] = prompt

            self._loaded["improvement"] = True
            logger.debug(
                f"Loaded {len(improvement_prompts)} improvement prompts from {self._improvement_file}"
            )
            return True
        except Exception as e:
            logger.error(f"Error loading improvement JSON: {e}")
            return False

    def get_prompt(self, name: str, prompt_type: str = "") -> Optional[PromptTemplate]:
        """
        Get prompt by name and type, returning a PromptTemplate object.

        Args:
            name: Name of the prompt
            prompt_type: Type of prompt ('', 'sections', 'detection', 'improvement')
                         If empty, will search in all types

        Returns:
            PromptTemplate object or None if not found
        """
        prompt_content = self._get_prompt_content(name, prompt_type)
        if prompt_content:
            return PromptTemplate(
                name=name, category=prompt_type or "sections", content=prompt_content
            )
        return None

    def _get_prompt_content(self, name: str, prompt_type: str = "") -> str:
        """
        Get prompt content by name and type.

        Args:
            name: Name of the prompt
            prompt_type: Type of prompt ('', 'sections', 'detection', 'improvement')
                         If empty, will search in all types

        Returns:
            The prompt content as a string
        """
        # Handle type-specific prompt lookup
        if prompt_type == "sections" or not prompt_type:
            # Try to find in sections cache
            if name in self._section_cache:
                section_data = self._section_cache[name]
                prompt_content = section_data["prompt"]

                # Check if this section has a template file reference
                template_file = section_data.get("template_file")
                if template_file:
                    # Load and append the template content
                    template_path = self._root_dir / "sections" / template_file
                    if template_path.exists():
                        try:
                            with open(template_path, "r", encoding="utf-8") as f:
                                template_content = f.read()
                            prompt_content += f"\n\nTemplate:\n{template_content}"
                        except Exception as e:
                            logger.error(
                                f"Error reading template file {template_path}: {e}"
                            )

                return prompt_content

        if prompt_type == "detection" or not prompt_type:
            # Try to find in detection cache
            if name in self._detection_cache:
                return self._detection_cache[name]["prompt"]

        if prompt_type == "improvement" or not prompt_type:
            # Try to find in improvement cache
            if name in self._improvement_cache:
                return self._improvement_cache[name]["prompt"]

        # If not found in JSON, fall back to file-based prompts
        if prompt_type:
            # Try to load from the specific subdirectory
            file_path = self._prompts_dir / prompt_type / f"{name}.txt"
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    logger.error(f"Error reading prompt file {file_path}: {e}")
        else:
            # Try each subdirectory if prompt_type not specified
            for subdir in ["sections", "detection"]:
                file_path = self._prompts_dir / subdir / f"{name}.txt"
                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            return f.read()
                    except Exception as e:
                        logger.error(f"Error reading prompt file {file_path}: {e}")

        # Prompt not found
        return ""

    def get_prompt_template(
        self, name: str, prompt_type: str = ""
    ) -> Optional[PromptTemplate]:
        """
        Get a prompt template by name and type.

        Args:
            name: Name of the prompt
            prompt_type: Type of prompt ('', 'sections', 'detection', 'improvement')

        Returns:
            PromptTemplate object or None if not found
        """
        prompt_content = self.get_prompt(name, prompt_type)
        if prompt_content:
            return PromptTemplate(name=name, content=prompt_content)
        return None

    def get_detection_prompt_by_type(self, detection_type: str) -> Optional[str]:
        """
        Get the default detection prompt for the specified detection type.

        Args:
            detection_type: Either 'ai' or 'human'

        Returns:
            The prompt content or None if not found
        """
        # Search for default prompt of the specified type
        for name, prompt_data in self._detection_cache.items():
            if prompt_data["type"] == detection_type and prompt_data.get(
                "is_default", False
            ):
                return prompt_data["prompt"]

        # If no default found, return the first of the given type
        for name, prompt_data in self._detection_cache.items():
            if prompt_data["type"] == detection_type:
                return prompt_data["prompt"]

        return None

    def get_improvement_prompt_by_strategy(self, strategy_type: str) -> Optional[str]:
        """
        Get an improvement prompt based on strategy type.

        Args:
            strategy_type: Strategy type ('default', 'ai_reduction', 'human_enhancement', etc.)

        Returns:
            The prompt content or None if not found
        """
        # Search for prompt with the specified strategy type
        for name, prompt_data in self._improvement_cache.items():
            if prompt_data["strategy_type"] == strategy_type:
                return prompt_data["prompt"]

        # If not found, return the default
        for name, prompt_data in self._improvement_cache.items():
            if prompt_data.get("is_default", False):
                return prompt_data["prompt"]

        return None

    def list_prompts(self, prompt_type: str = "") -> List[str]:
        """
        List all available prompts of the specified type.

        Args:
            prompt_type: Type of prompt ('', 'sections', 'detection', 'improvement')
                         If empty, will return prompts from all types

        Returns:
            List of prompt names
        """
        result = []

        if prompt_type == "sections" or not prompt_type:
            result.extend(list(self._section_cache.keys()))

        if prompt_type == "detection" or not prompt_type:
            result.extend(list(self._detection_cache.keys()))

        if prompt_type == "improvement" or not prompt_type:
            result.extend(list(self._improvement_cache.keys()))

        return result

    def get_all_prompt_metadata(self, prompt_type: str = "") -> Dict[str, Any]:
        """
        Get metadata for all prompts of the specified type.

        Args:
            prompt_type: Type of prompt ('sections', 'detection', 'improvement')

        Returns:
            Dictionary mapping prompt names to their metadata
        """
        if prompt_type == "sections":
            return self._section_cache
        elif prompt_type == "detection":
            return self._detection_cache
        elif prompt_type == "improvement":
            return self._improvement_cache
        else:
            # Combine all types
            result = {}
            result.update(self._section_cache)
            result.update(self._detection_cache)
            result.update(self._improvement_cache)
            return result

    def save_prompt(self, prompt: PromptTemplate) -> None:
        """
        Save a prompt template.

        Args:
            prompt: The prompt template to save

        Note:
            This implementation is read-only for JSON files to maintain integrity.
            For write operations, use dedicated utility scripts.
        """
        logger.warning(
            f"EnhancedJsonPromptRepository is read-only. Use utility scripts to modify JSON files. "
            f"Attempted to save prompt: {prompt.name}"
        )
        # File-based fallback for backward compatibility
        try:
            prompt_type = "sections"  # Default type
            # Try to determine prompt type from name
            if prompt.name.startswith("ai_") or prompt.name.startswith("human_"):
                prompt_type = "detection"

            file_path = self._prompts_dir / prompt_type / f"{prompt.name}.txt"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(prompt.content)

            logger.info(
                f"Saved prompt to legacy file location: {file_path} "
                f"(Note: This does not update the JSON repository)"
            )
        except Exception as e:
            logger.error(f"Error saving prompt to legacy file location: {e}")
            raise FileOperationError(
                f"Failed to save prompt: {e}", prompt.name, "save_prompt"
            )

    def get_sections_config(self) -> Dict[str, Any]:
        """Get all section configurations."""
        from generator.core.domain.models import SectionConfig

        if not self._loaded["sections"]:
            self._load_sections_json()

        configs = {}
        for section_name, metadata in self._section_cache.items():
            # Create SectionConfig from metadata
            configs[section_name] = SectionConfig(
                name=section_name,
                ai_detect=metadata.get("ai_detect", True),
                prompt_file=metadata.get("prompt_file", f"{section_name}.txt"),
                **metadata.get("metadata", {}),
            )
        return configs

    def get_section_config(self, section_name: str) -> Optional[Any]:
        """Get configuration for a specific section."""
        from generator.core.domain.models import SectionConfig

        if not self._loaded["sections"]:
            self._load_sections_json()

        if section_name in self._section_cache:
            metadata = self._section_cache[section_name]
            return SectionConfig(
                name=section_name,
                ai_detect=metadata.get("ai_detect", True),
                prompt_file=metadata.get("prompt_file", f"{section_name}.txt"),
                **metadata.get("metadata", {}),
            )
        return None
