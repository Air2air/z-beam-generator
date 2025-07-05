"""
Compatibility adapter to help legacy code work with the new JSON prompt repository.
"""

import os
from typing import Dict, Optional
import logging
from generator.core.interfaces.services import IPromptRepository
from generator.infrastructure.storage.enhanced_json_prompt_repository import (
    EnhancedJsonPromptRepository,
)

logger = logging.getLogger(__name__)


class PromptRepositoryAdapter:
    """
    Adapter that provides backward compatibility for legacy code that expects
    prompt templates to be loaded from text files but now needs to work with
    the JSON-based repository.
    """

    def __init__(self, repository: Optional[IPromptRepository] = None):
        """Initialize with an existing repository or create a new one."""
        if repository:
            self.repository = repository
        else:
            # Default repository path
            prompts_dir = os.path.join(os.path.dirname(__file__), "../prompts")
            self.repository = EnhancedJsonPromptRepository(prompts_dir)

    def get_section_templates(self) -> Dict[str, str]:
        """
        Get all section templates in the format expected by the legacy code.

        Returns:
            Dict mapping filenames (with .txt extension) to prompt content
        """
        templates = {}
        section_metadata = self.repository.get_all_prompt_metadata("sections")

        # Convert to the format expected by legacy code
        for name, data in section_metadata.items():
            # Add .txt extension to maintain compatibility
            templates[f"{name}.txt"] = data.get("prompt", "")

        logger.info(f"Loaded {len(templates)} section templates from JSON repository")
        return templates
