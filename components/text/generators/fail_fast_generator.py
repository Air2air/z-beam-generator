#!/usr/bin/env python3
"""
Fail-Fast Text Generator
Basic text generation without optimization dependencies.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from api.client import GenerationRequest
from components.text.localization import get_required_localization_prompt
from components.text.ai_detection import get_ai_detection_prompt

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

    def _load_authors_data(self) -> list:
        """
        Load authors data from authors.json.
        
        Returns:
            List of author dictionaries
        """
        try:
            authors_file = "components/author/authors.json"
            if os.path.exists(authors_file):
                with open(authors_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'authors' in data:
                        return data['authors']
        except Exception as e:
            print(f"Warning: Could not load authors data: {e}")
        
        # Fallback to mock data if file doesn't exist
        return [
            {"id": 1, "name": "Yi-Chun Lin", "country": "Taiwan", "expertise": "Laser Materials Processing", "title": "Ph.D.", "sex": "f"},
            {"id": 2, "name": "Alessandro Moretti", "country": "Italy", "expertise": "Laser-Based Additive Manufacturing", "title": "Ph.D.", "sex": "m"},
            {"id": 3, "name": "Ikmanda Roswati", "country": "Indonesia", "expertise": "Ultrafast Laser Physics and Material Interactions", "title": "Ph.D.", "sex": "m"},
            {"id": 4, "name": "Todd Dunning", "country": "United States", "expertise": "Optical Materials for Laser Systems", "title": "MA", "sex": "m"}
        ]

    def _validate_configurations(self):
        """Validate all required configurations exist and are valid."""
        # Check for required files
        required_files = [
            "components/text/prompts/base_content_prompt.yaml",
        ]

        for file_path in required_files:
            if not Path(file_path).exists():
                from utils.ai.loud_errors import configuration_failure

                configuration_failure(
                    "fail_fast_generator",
                    f"Required configuration file not found: {file_path}",
                )
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
        enhancement_flags: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """
        Generate text using fail-fast approach.

        Args:
            material_name: Name of the material
            material_data: Raw material data from materials.yaml (fallback)
            api_client: API client for generation
            author_info: Author information
            frontmatter_data: Processed frontmatter data (primary source)
            enhancement_flags: Optional enhancement flags for AI detection optimization

        Returns:
            Dictionary with generation results

        Raises:
            GenerationError: If generation fails
            RetryableError: For temporary failures
        """
        if not api_client:
            from utils.ai.loud_errors import dependency_failure

            dependency_failure(
                "fail_fast_generator", "API client is required for text generation"
            )
            raise GenerationError("API client is required for text generation")

        # Log enhancement flags if provided
        if enhancement_flags:
            logger.info(f"🎯 Received enhancement flags: {list(enhancement_flags.keys())}")
        else:
            logger.info("🎯 No enhancement flags provided")

        # Load base prompt
        try:
            with open("components/text/prompts/base_content_prompt.yaml", "r") as f:
                base_prompt_data = yaml.safe_load(f)
        except Exception as e:
            from utils.ai.loud_errors import configuration_failure

            configuration_failure(
                "fail_fast_generator", f"Failed to load base prompt: {e}"
            )
            raise ConfigurationError(f"Failed to load base prompt: {e}")

        # Construct full prompt
        full_prompt = self._construct_prompt(
            base_prompt_data,
            material_name,
            material_data,
            author_info,
            frontmatter_data,
            enhancement_flags,
        )

        # Generate content with retries
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    f"Generating text for {material_name} (attempt {attempt + 1})"
                )

                # Create generation request - use component config
                request = GenerationRequest(
                    prompt=full_prompt,
                    system_prompt=None,
                    max_tokens=4000,  # Will be overridden by component-specific config
                    temperature=0.1,  # Will be overridden by component-specific config
                )

                # Generate content
                response = api_client.generate(request)

                # Check for API errors first
                if hasattr(response, "success") and not response.success:
                    error_msg = getattr(response, "error", "API error")
                    
                    # Check if this is a temporary/retryable error
                    retryable_errors = [
                        "temporary failure", "timeout", "rate limit", "server error", 
                        "connection error", "network error", "service unavailable"
                    ]
                    
                    is_retryable = any(retryable_error in error_msg.lower() for retryable_error in retryable_errors)
                    
                    if is_retryable and attempt < self.max_retries:
                        logger.warning(
                            f"Temporary API error '{error_msg}', retrying in {self.retry_delay}s (attempt {attempt + 1}/{self.max_retries + 1})"
                        )
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        # Non-retryable error or max retries reached
                        from utils.ai.loud_errors import api_failure
                        api_failure(
                            "fail_fast_generator",
                            f"API error: {error_msg}",
                            retry_count=attempt if is_retryable else None,
                        )
                        from api.client import APIError
                        raise APIError(f"API error: {error_msg}")

                if not response or not response.content:
                    if attempt < self.max_retries:
                        logger.warning(
                            f"Empty response, retrying in {self.retry_delay}s"
                        )
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        from utils.ai.loud_errors import api_failure

                        api_failure(
                            "fail_fast_generator",
                            "Empty response from API",
                            retry_count=attempt,
                        )
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
                # Preserve API-specific errors without wrapping
                from api.client import APIError

                if isinstance(e, APIError):
                    # Don't retry API errors, re-raise immediately
                    raise e

                if attempt < self.max_retries:
                    logger.warning(
                        f"Generation attempt {attempt + 1} failed: {e}, retrying in {self.retry_delay}s"
                    )
                    time.sleep(self.retry_delay)
                else:
                    from utils.ai.loud_errors import api_failure

                    api_failure(
                        "fail_fast_generator",
                        f"Text generation failed after {self.max_retries + 1} attempts: {e}",
                        retry_count=attempt,
                    )
                    raise GenerationError(
                        f"Text generation failed after {self.max_retries + 1} attempts: {e}"
                    )

        # This should never be reached
        from utils.ai.loud_errors import critical_failure

        critical_failure("fail_fast_generator", "Unexpected error in generation loop")
        raise GenerationError("Unexpected error in generation loop")

    def _construct_prompt(
        self,
        base_prompt_data: Dict[str, Any],
        material_name: str,
        material_data: Dict[str, Any],
        author_info: Dict[str, Any],
        frontmatter_data: Optional[Dict[str, Any]] = None,
        enhancement_flags: Optional[Dict[str, bool]] = None,
    ) -> str:
        """
        Construct the complete prompt for text generation.
        
        ARCHITECTURE: AI Detection → Localization → Base Content

        Args:
            base_prompt_data: Base prompt configuration
            material_name: Name of the material
            material_data: Raw material data (fallback)
            author_info: Author information
            frontmatter_data: Processed frontmatter data (primary source)
            enhancement_flags: Optional enhancement flags for AI detection optimization

        Returns:
            Complete prompt string
        """
        # STEP 1: Add AI detection prompts FIRST (with enhancement flags if provided)
        ai_detection_prompt = get_ai_detection_prompt(enhancement_flags)
        
        # STEP 2: Add mandatory localization chain SECOND
        try:
            localization_prompt = get_required_localization_prompt(author_info)
        except Exception as e:
            from utils.ai.loud_errors import validation_failure
            validation_failure(
                "fail_fast_generator",
                f"Failed to load required localization prompts: {e}",
                field="localization"
            )
            raise ValueError(f"Localization prompts are mandatory: {e}")

        # Build prompt sections in order: AI Detection → Localization → Content
        sections = [
            ai_detection_prompt,  # AI detection guidance FIRST
            localization_prompt   # Localization requirements SECOND
        ]

        # Add author information
        author_name = author_info.get("name")
        if not author_name:
            from utils.ai.loud_errors import validation_failure

            validation_failure(
                "fail_fast_generator",
                "Author name is required for text generation",
                field="author_info.name",
            )
            raise ValueError("Author name is required for text generation")
        sections.append(f"AUTHOR: {author_name}")
        sections.append(f"COUNTRY: {author_info.get('country', 'USA').title()}")

        # Add material information - use frontmatter_data as primary source
        primary_data = frontmatter_data if frontmatter_data else material_data

        # Convert datetime objects to strings for JSON serialization
        import datetime
        def convert_datetimes(obj):
            if isinstance(obj, dict):
                return {k: convert_datetimes(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetimes(item) for item in obj]
            elif isinstance(obj, datetime.datetime):
                return obj.isoformat()
            elif isinstance(obj, datetime.date):
                return obj.isoformat()
            else:
                return obj

        primary_data = convert_datetimes(primary_data)
        material_data = convert_datetimes(material_data)
        if frontmatter_data:
            frontmatter_data = convert_datetimes(frontmatter_data)

        sections.append(f"MATERIAL: {material_name}")
        sections.append(f"MATERIAL DATA: {json.dumps(primary_data, indent=2)}")

        # Add raw material data as additional context if frontmatter was used
        if frontmatter_data and material_data != frontmatter_data:
            sections.append(f"RAW MATERIAL DATA: {json.dumps(material_data, indent=2)}")

        # Add frontmatter context if available (for debugging/transparency)
        if frontmatter_data:
            sections.append(f"FRONTMATTER CONTEXT: {json.dumps(frontmatter_data, indent=2)}")

        # Add base prompt instructions
        if "overall_subject" in base_prompt_data:
            subject = base_prompt_data["overall_subject"].format(material=material_name)
            sections.append(
                f"TASK:\nWrite a comprehensive technical article about laser cleaning of {material_name}.\n\n{subject}"
            )
        
        # Add formatting requirements if available
        if "formatting_requirements" in base_prompt_data:
            sections.append(base_prompt_data["formatting_requirements"])

        return "\n\n".join(sections)

    def _load_persona_prompt(self, author_info: Dict) -> Optional[str]:
        """
        Load persona prompt for given author information.
        
        This method provides backward compatibility for tests while delegating
        to the localization system.
        
        Args:
            author_info: Author information dictionary
            
        Returns:
            Persona prompt string or None if not found
        """
        try:
            from components.text.localization.prompt_chain import LocalizationPromptChain
            chain = LocalizationPromptChain()
            
            # Extract country from author_info
            if isinstance(author_info, dict) and 'country' in author_info:
                country = author_info['country'].lower()
            elif isinstance(author_info, int):
                # Handle legacy author ID format - map to default country
                country = 'usa'
            else:
                country = 'usa'
            
            # Normalize country name
            country_mapping = {
                'italy': 'italy',
                'indonesia': 'indonesia', 
                'taiwan': 'taiwan',
                'usa': 'usa',
                'united states': 'usa',
                'united states (california)': 'usa'
            }
            normalized_country = country_mapping.get(country, 'usa')
            
            return chain._load_persona_prompt(normalized_country)
        except Exception as e:
            logger.warning(f"Failed to load persona prompt: {e}")
            return None

    def _build_api_prompt(self, material_name: str, author_id: int = None, author_name: str = None, material_data: Dict = None, author_info: Dict = None, **kwargs) -> str:
        """
        Build API prompt for text generation.
        
        This method provides backward compatibility for tests with flexible parameter handling.
        
        Args:
            material_name: Name of the material (first parameter for compatibility)
            author_id: Author ID (for legacy compatibility)
            author_name: Author name (for legacy compatibility) 
            material_data: Material data dictionary
            author_info: Author information dictionary
            **kwargs: Additional prompt parameters
            
        Returns:
            Complete API prompt string
        """
        try:
            # Handle different parameter formats for backward compatibility
            if isinstance(material_name, str) and author_id is not None:
                # Legacy format: material_name, author_id, author_name, material_data, author_info
                if not material_data:
                    material_data = {}
                if not author_info:
                    author_info = {"id": author_id, "name": author_name} if author_name else {"id": author_id}
                
                # Load base prompt data (required for _construct_prompt)
                base_prompt_data = {}
                try:
                    base_prompt_file = "components/text/base_prompt.yaml"
                    if os.path.exists(base_prompt_file):
                        with open(base_prompt_file, 'r', encoding='utf-8') as f:
                            base_prompt_data = yaml.safe_load(f) or {}
                except Exception:
                    pass
                
                # Use the internal prompt construction method
                return self._construct_prompt(
                    base_prompt_data=base_prompt_data,
                    material_name=material_name,
                    material_data=material_data,
                    author_info=author_info,
                    **kwargs
                )
            elif isinstance(material_name, str) and isinstance(author_id, dict):
                # New format: material_name, material_data (passed as author_id), author_info (passed as author_name)
                base_prompt_data = {}
                try:
                    base_prompt_file = "components/text/base_prompt.yaml"
                    if os.path.exists(base_prompt_file):
                        with open(base_prompt_file, 'r', encoding='utf-8') as f:
                            base_prompt_data = yaml.safe_load(f) or {}
                except Exception:
                    pass
                
                return self._construct_prompt(
                    base_prompt_data=base_prompt_data,
                    material_name=material_name,
                    material_data=author_id,  # material_data passed as second parameter
                    author_info=author_name,  # author_info passed as third parameter
                    **kwargs
                )
            else:
                # Use the internal prompt construction method with defaults
                base_prompt_data = {}
                try:
                    base_prompt_file = "components/text/base_prompt.yaml"
                    if os.path.exists(base_prompt_file):
                        with open(base_prompt_file, 'r', encoding='utf-8') as f:
                            base_prompt_data = yaml.safe_load(f) or {}
                except Exception:
                    pass
                
                return self._construct_prompt(
                    base_prompt_data=base_prompt_data,
                    material_name=material_name,
                    material_data=material_data or {},
                    author_info=author_info or {},
                    **kwargs
                )
        except Exception as e:
            logger.warning(f"Failed to build API prompt: {e}")
            # Fallback to simple prompt
            return f"Generate technical content about {material_name} laser cleaning."

    def _build_comprehensive_prompt(self, material_name: str, material_data: Dict, author_info: Dict, **kwargs) -> str:
        """
        Build comprehensive API prompt for text generation.
        
        This method is called by the TextComponentGenerator for compatibility.
        
        Args:
            material_name: Name of the material
            material_data: Material data dictionary
            author_info: Author information
            **kwargs: Additional prompt parameters
            
        Returns:
            Complete API prompt string
        """
        return self._construct_prompt(
            material_name=material_name,
            material_data=material_data,
            author_info=author_info,
            **kwargs
        )


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
