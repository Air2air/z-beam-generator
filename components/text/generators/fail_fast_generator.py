#!/usr/bin/env python3
"""
Fail-Fast Text Generator
Basic text generation without optimization dependencies.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from api.client import GenerationRequest

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required configurations are missing or invalid."""
    pass


class GenerationError(Exception):
    """Raised when text generation fails."""
    pass


class RetryableError(Exception):
    """Raised for temporary failures that could be retried."""
    pass


class FailFastTextGenerator:
    """
    Fail-fast text generator that validates all dependencies upfront
    and provides clean error handling without fallbacks.
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_scoring: bool = False,
        human_threshold: float = 75.0,
        skip_ai_detection: bool = True,
    ):
        """
        Initialize the fail-fast text generator.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            enable_scoring: Whether to enable quality scoring (disabled for basic text)
            human_threshold: Minimum human believability score
            skip_ai_detection: Whether to skip AI detection (always True for basic text)

        Raises:
            ConfigurationError: If required configurations are missing
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_scoring = enable_scoring
        self.human_threshold = human_threshold
        self.skip_ai_detection = skip_ai_detection

        # Validate configurations on initialization
        self._validate_configurations()

    def _validate_configurations(self):
        """Validate all required configurations exist and are valid."""
        # Check for required files
        required_files = [
            "components/text/prompts/base_content_prompt.yaml",
        ]

        for file_path in required_files:
            if not Path(file_path).exists():
                raise ConfigurationError(
                    f"Required configuration file not found: {file_path}"
                )

        logger.info("✅ All configurations validated successfully")

    def generate(
        self,
        material_name: str,
        material_data: Dict[str, Any],
        api_client,
        author_info: Dict[str, Any],
        frontmatter_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate text using fail-fast approach.

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
            raise GenerationError("API client is required for text generation")

        # Load base prompt
        try:
            with open(
                "components/text/prompts/base_content_prompt.yaml", "r"
            ) as f:
                base_prompt_data = yaml.safe_load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to load base prompt: {e}")

        # Construct full prompt
        full_prompt = self._construct_prompt(
            base_prompt_data,
            material_name,
            material_data,
            author_info,
            frontmatter_data,
        )

        # Generate content with retries
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    f"Generating text for {material_name} (attempt {attempt + 1})"
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

                # Create ComponentResult instead of dict
                from generators.component_generators import ComponentResult

                return ComponentResult(
                    component_type="text",
                    content=content,
                    success=True,
                    token_count=getattr(response, "token_count", None),
                )

            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(
                        f"Generation attempt {attempt + 1} failed: {e}, retrying in {self.retry_delay}s"
                    )
                    time.sleep(self.retry_delay)
                else:
                    raise GenerationError(
                        f"Text generation failed after {self.max_retries + 1} attempts: {e}"
                    )

        # This should never be reached
        raise GenerationError("Unexpected error in generation loop")

    def _construct_prompt(
        self,
        base_prompt_data: Dict[str, Any],
        material_name: str,
        material_data: Dict[str, Any],
        author_info: Dict[str, Any],
        frontmatter_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Construct the complete prompt for text generation.

        Args:
            base_prompt_data: Base prompt configuration
            material_name: Name of the material
            material_data: Material data
            author_info: Author information
            frontmatter_data: Frontmatter data

        Returns:
            Complete prompt string
        """
        # Build prompt sections
        sections = []

        # Add author information
        sections.append(f"AUTHOR: {author_info.get('name', 'Technical Expert')}")
        sections.append(f"COUNTRY: {author_info.get('country', 'USA').title()}")

        # Add material information
        sections.append(f"MATERIAL: {material_name}")
        sections.append(f"MATERIAL DATA: {json.dumps(material_data, indent=2)}")

        # Add frontmatter context if available
        if frontmatter_data:
            sections.append(
                f"CONTEXT: {json.dumps(frontmatter_data, indent=2)}"
            )

        # Add base prompt instructions
        if "overall_subject" in base_prompt_data:
            subject = base_prompt_data['overall_subject'].format(material=material_name)
            sections.append(f"TASK:\nWrite a comprehensive technical article about laser cleaning of {material_name}.\n\n{subject}")

        return "\n\n".join(sections)


def create_fail_fast_generator(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    enable_scoring: bool = False,
    human_threshold: float = 75.0,
    ai_detection_service=None,
    skip_ai_detection: bool = True,
) -> FailFastTextGenerator:
    """
    Create a fail-fast text generator.

    Args:
        max_retries: Maximum number of retry attempts for retryable errors
        retry_delay: Delay between retries in seconds
        enable_scoring: Whether to enable quality scoring (disabled for basic text)
        human_threshold: Minimum score required to pass human believability test
        ai_detection_service: AI detection service (ignored for basic text)
        skip_ai_detection: Whether to skip AI detection (always True for basic text)

    Returns:
        Configured fail-fast text generator

    Raises:
        ConfigurationError: If required configurations are missing or invalid
    """
    return FailFastTextGenerator(
        max_retries=max_retries,
        retry_delay=retry_delay,
        enable_scoring=enable_scoring,
        human_threshold=human_threshold,
        skip_ai_detection=skip_ai_detection,
    )
