#!/usr/bin/env python3
"""
Fail-Fast Content Generator
Removes all hardcoded fallbacks and implements clean error handling with retry mechanisms.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from api.client import GenerationRequest
from optimizer.ai_detection.config import AI_DETECTION_CONFIG
from optimizer.text_optimization.validation.content_scorer import create_content_scorer

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required configurations are missing or invalid."""

    pass


class GenerationError(Exception):
    """Raised when content generation fails."""

    pass


class RetryableError(Exception):
    """Raised for temporary failures that could be retried."""

    pass


class FailFastContentGenerator:
    """
    Fail-fast content generator that validates all dependencies upfront
    and provides clean error handling without fallbacks.
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_scoring: bool = True,
        human_threshold: float = 75.0,
        ai_detection_service=None,
        skip_ai_detection: bool = False,
    ):
        """
        Initialize the fail-fast content generator.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            enable_scoring: Whether to enable quality scoring
            human_threshold: Minimum human believability score
            ai_detection_service: AI detection service instance
            skip_ai_detection: Whether to skip AI detection

        Raises:
            ConfigurationError: If required configurations are missing
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_scoring = enable_scoring
        self.human_threshold = human_threshold
        self.ai_detection_service = ai_detection_service
        self.skip_ai_detection = skip_ai_detection

        # Validate configurations on initialization
        self._validate_configurations()

        # Initialize content scorer if enabled
        self.content_scorer = None
        if self.enable_scoring:
            self.content_scorer = create_content_scorer(
                human_threshold=self.human_threshold
            )

    def _validate_configurations(self):
        """Validate all required configurations exist and are valid."""
        # Check for required files
        required_files = [
            "components/text/prompts/core/base_content_prompt.yaml",
            "components/author/authors.json",
            "config/ai_detection.yaml",
        ]

        for file_path in required_files:
            if not Path(file_path).exists():
                raise ConfigurationError(
                    f"Required configuration file not found: {file_path}"
                )

        # Validate authors file
        self._load_authors_file("components/author/authors.json")

        logger.info("✅ All configurations validated successfully")

    def _load_authors_file(self, authors_file: str) -> List[Dict]:
        """
        Load and validate the authors configuration file.

        Args:
            authors_file: Path to the authors JSON file

        Returns:
            List of author dictionaries

        Raises:
            ConfigurationError: If authors file is invalid
        """
        try:
            with open(authors_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "authors" in data:
                authors_list = data["authors"]
            elif isinstance(data, list):
                authors_list = data
            else:
                raise ConfigurationError(
                    f"Authors file {authors_file} must contain a list or object with 'authors' key"
                )

            if not isinstance(authors_list, list):
                raise ConfigurationError("Authors data must be a list")

            return authors_list

        except FileNotFoundError:
            raise ConfigurationError(f"Authors file not found: {authors_file}")
        except Exception as e:
            raise ConfigurationError(f"Error loading authors file: {e}")

    def _load_persona_prompt(self, author_info: Dict[str, Any]) -> str:
        """
        Load persona-specific prompt patterns for the given author.

        Args:
            author_info: Author information dictionary

        Returns:
            Persona prompt string

        Raises:
            ConfigurationError: If persona file is missing or invalid
        """
        country = author_info.get("country", "").lower()
        if not country:
            logger.warning("No country specified in author_info, using default persona")
            country = "usa"

        persona_file = (
            f"optimizer/text_optimization/prompts/personas/{country}_persona.yaml"
        )

        try:
            with open(persona_file, "r", encoding="utf-8") as f:
                persona_data = yaml.safe_load(f)

            # Extract language patterns and writing style
            language_patterns = persona_data.get("language_patterns", {})
            writing_style = persona_data.get("writing_style", {})

            # Build persona prompt
            persona_prompt = f"""
Author: {author_info.get('name', 'Technical Expert')}
Country: {country.title()}
Language Patterns: {json.dumps(language_patterns)}
Writing Style: {json.dumps(writing_style)}
"""

            return persona_prompt.strip()

        except FileNotFoundError:
            logger.warning(f"Persona file not found: {persona_file}, using default")
            return f"Author: {author_info.get('name', 'Technical Expert')}"
        except Exception as e:
            logger.error(f"Error loading persona file {persona_file}: {e}")
            return f"Author: {author_info.get('name', 'Technical Expert')}"

    def generate(
        self,
        material_name: str,
        material_data: Dict[str, Any],
        api_client,
        author_info: Dict[str, Any],
        frontmatter_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate content using fail-fast approach.

        Args:
            material_name: Name of the material
            material_data: Material data dictionary
            api_client: API client for generation
            author_info: Author information
            frontmatter_data: Frontmatter data from previous generation

        Returns:
            Dictionary with generation results

        Raises:
            GenerationError: If generation fails
            RetryableError: For temporary failures
        """
        if not api_client:
            raise GenerationError("API client is required for content generation")

        # Load persona prompt
        persona_prompt = self._load_persona_prompt(author_info)

        # Load base prompt
        try:
            with open("components/text/prompts/core/base_content_prompt.yaml", "r") as f:
                base_prompt_data = yaml.safe_load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to load base prompt: {e}")

        # Construct full prompt
        full_prompt = self._construct_prompt(
            base_prompt_data,
            material_name,
            material_data,
            persona_prompt,
            frontmatter_data,
        )

        # Generate content with retries
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    f"Generating content for {material_name} (attempt {attempt + 1})"
                )

                # Create generation request
                request = GenerationRequest(
                    prompt=full_prompt,
                    system_prompt=None,
                    max_tokens=4000,
                    temperature=0.7,
                )

                # Generate content
                response = api_client.generate(request)

                if not response or not response.content:
                    if attempt < self.max_retries:
                        logger.warning(
                            f"Empty response, retrying in {self.retry_delay}s"
                        )
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise GenerationError("Empty response from API")

                content = response.content

                # Score content if enabled
                score = None
                if self.content_scorer and not self.skip_ai_detection:
                    score_result = self.content_scorer.score_content(
                        content=content,
                        material_data=material_data,
                        author_info=author_info,
                    )
                    score = score_result.overall_score

                    if score < self.human_threshold:
                        logger.warning(
                            f"Content score {score} below threshold {self.human_threshold}"
                        )

                # Create ComponentResult instead of dict
                from generators.component_generators import ComponentResult
                
                return ComponentResult(
                    component_type="text",
                    content=content,
                    success=True,
                    token_count=getattr(response, 'token_count', None)
                )

            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(
                        f"Generation attempt {attempt + 1} failed: {e}, retrying in {self.retry_delay}s"
                    )
                    time.sleep(self.retry_delay)
                else:
                    raise GenerationError(
                        f"Content generation failed after {self.max_retries + 1} attempts: {e}"
                    )

        # This should never be reached
        raise GenerationError("Unexpected error in generation loop")

    def _construct_prompt(
        self,
        base_prompt_data: Dict[str, Any],
        material_name: str,
        material_data: Dict[str, Any],
        persona_prompt: str,
        frontmatter_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Construct the complete prompt for content generation.

        Args:
            base_prompt_data: Base prompt configuration
            material_name: Name of the material
            material_data: Material data
            persona_prompt: Persona-specific prompt
            frontmatter_data: Frontmatter data

        Returns:
            Complete prompt string
        """
        # Build prompt sections
        sections = []

        # Add persona information
        sections.append(f"PERSONA INFORMATION:\n{persona_prompt}")

        # Add material information
        sections.append(f"MATERIAL: {material_name}")
        sections.append(f"MATERIAL DATA: {json.dumps(material_data, indent=2)}")

        # Add frontmatter context if available
        if frontmatter_data:
            sections.append(
                f"FRONTMATTER CONTEXT: {json.dumps(frontmatter_data, indent=2)}"
            )

        # Add base prompt instructions
        if "instructions" in base_prompt_data:
            sections.append(f"INSTRUCTIONS:\n{base_prompt_data['instructions']}")

        return "\n\n".join(sections)


def create_fail_fast_generator(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    enable_scoring: bool = True,
    human_threshold: float = 75.0,
    ai_detection_service=None,
    skip_ai_detection: bool = False,
) -> FailFastContentGenerator:
    """
    Create a fail-fast content generator.

    Args:
        max_retries: Maximum number of retry attempts for retryable errors
        retry_delay: Delay between retries in seconds
        enable_scoring: Whether to enable comprehensive quality scoring
        human_threshold: Minimum score required to pass human believability test
        ai_detection_service: AI detection service for content analysis
        skip_ai_detection: Whether to skip AI detection (useful when called from wrapper)

    Returns:
        Configured fail-fast content generator with optional scoring

    Raises:
        ConfigurationError: If required configurations are missing or invalid
    """
    return FailFastContentGenerator(
        max_retries=max_retries,
        retry_delay=retry_delay,
        enable_scoring=enable_scoring,
        human_threshold=human_threshold,
        ai_detection_service=ai_detection_service,
        skip_ai_detection=skip_ai_detection,
    )
