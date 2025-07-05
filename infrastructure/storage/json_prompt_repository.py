"""
JSON-based prompt repository for centralizing section prompts in a single file.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import re
import logging
from generator.core.interfaces.services import IPromptRepository
from generator.core.domain.models import PromptTemplate
from generator.infrastructure.storage.exceptions import FileOperationError

logger = logging.getLogger(__name__)


class JsonPromptRepository(IPromptRepository):
    """JSON-based repository for prompt templates with fallback to file-based templates."""

    def __init__(self, prompts_dir: Path):
        self._prompts_dir = Path(prompts_dir)
        # Look for sections.json in the root /sections directory
        self._sections_file = (
            Path(prompts_dir).parent.parent / "sections" / "sections.json"
        )
        self._section_cache = {}
        self._loaded = False

        if not self._prompts_dir.exists():
            raise FileOperationError(
                f"Prompts directory does not exist: {prompts_dir}",
                str(prompts_dir),
                "initialize_repository",
            )

        # Try to load sections.json on initialization
        self._load_sections_json()

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
                name = section.get("name")
                if name:
                    self._section_cache[name] = section

            logger.info(f"Loaded {len(sections)} sections from {self._sections_file}")
            self._loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load sections JSON: {str(e)}")
            return False

    def get_section_metadata(self, name: str) -> Dict:
        """Get metadata for a section."""
        if not self._loaded:
            self._load_sections_json()

        return self._section_cache.get(name, {})

    def get_prompt(self, name: str, category: str) -> Optional[PromptTemplate]:
        """Retrieve a prompt template by name and category."""
        # For sections category, check the JSON file first
        if category == "sections" and not self._loaded:
            self._load_sections_json()

        if category == "sections" and name in self._section_cache:
            section = self._section_cache[name]
            content = section.get("prompt", "")
            if content:
                variables = re.findall(r"{(\w+)}", content)
                return PromptTemplate(
                    name=name,
                    category=category,
                    content=content,
                    variables=list(set(variables)),
                )

        # Fallback to file-based approach
        try:
            file_path = self._prompts_dir / category / f"{name}.txt"
            if not file_path.exists():
                logger.debug(f"Prompt file not found: {file_path}")
                return None

            content = file_path.read_text(encoding="utf-8")
            if not content.strip():
                logger.warning(f"Empty prompt file: {file_path}")
                return None

            variables = re.findall(r"{(\w+)}", content)
            return PromptTemplate(
                name=name,
                category=category,
                content=content,
                variables=list(set(variables)),
            )

        except Exception as e:
            logger.error(f"Failed to read prompt {name} from {category}: {str(e)}")
            raise FileOperationError(
                f"Failed to read prompt file: {str(e)}",
                str(file_path) if "file_path" in locals() else None,
                "read_prompt",
            ) from e

    def list_prompts(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """List available prompt templates."""
        prompts = []

        # Include JSON-based sections if category matches
        if (category is None or category == "sections") and not self._loaded:
            self._load_sections_json()

        if (category is None or category == "sections") and self._section_cache:
            for name, section in self._section_cache.items():
                content = section.get("prompt", "")
                if content:
                    variables = re.findall(r"{(\w+)}", content)
                    prompts.append(
                        PromptTemplate(
                            name=name,
                            category="sections",
                            content=content,
                            variables=list(set(variables)),
                        )
                    )

        # Include file-based prompts
        try:
            if category:
                categories = [category]
            else:
                categories = [d.name for d in self._prompts_dir.iterdir() if d.is_dir()]

            for cat in categories:
                if cat == "sections" and self._section_cache:
                    # We already added sections from JSON
                    continue

                cat_dir = self._prompts_dir / cat
                if not cat_dir.is_dir():
                    continue

                for file_path in cat_dir.glob("*.txt"):
                    name = file_path.stem
                    try:
                        prompt = self.get_prompt(name, cat)
                        if prompt:
                            prompts.append(prompt)
                    except Exception as e:
                        logger.warning(f"Error loading prompt {name} from {cat}: {e}")

        except Exception as e:
            logger.error(f"Error listing prompts: {str(e)}")

        return prompts

    def is_ai_detect_enabled(self, section_name: str) -> bool:
        """Check if AI detection is enabled for a section."""
        if not self._loaded:
            self._load_sections_json()

        section = self._section_cache.get(section_name, {})
        return section.get("ai_detect", True)  # Default to True for safety

    def save_prompt(self, prompt: PromptTemplate) -> None:
        """Save a prompt template - not implemented for JSON repository."""
        logger.warning(
            "save_prompt is not implemented for JsonPromptRepository. "
            "To update prompts, edit the sections.json file directly."
        )
        # TODO: Implement if needed in the future
        pass
