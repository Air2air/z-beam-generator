#!/usr/bin/env python3
"""
Reusable API Generation Helper

Domain-agnostic helper for making text generation API calls.
Handles request building, error handling, and response extraction.

Usage:
    from shared.generation.api_helper import generate_text
    from generation.config.dynamic_config import DynamicConfig
    
    dynamic_config = DynamicConfig()
    result = generate_text(
        prompt="Write a description...",
        max_tokens=150,
        temperature=dynamic_config.calculate_temperature('default')
    )
"""

import logging
from typing import Optional

from generation.config.config_loader import ProcessingConfig

logger = logging.getLogger(__name__)


def _get_api_helper_config() -> ProcessingConfig:
    return ProcessingConfig()


def get_api_client(provider: str = 'grok'):
    """Get configured API client."""
    from shared.api.client_factory import create_api_client
    return create_api_client(provider)


def generate_text(
    prompt: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    api_client=None,
    provider: str = 'grok'
) -> Optional[str]:
    """
    Generate text using the configured API.
    
    Args:
        prompt: The prompt to send to the API
        max_tokens: Maximum tokens to generate (default 150)
        temperature: Generation temperature (default 0.7)
        frequency_penalty: Frequency penalty for repetition (default 0.0)
        presence_penalty: Presence penalty for topic diversity (default 0.0)
        api_client: Optional pre-configured API client
        provider: API provider name (default 'grok')
    
    Returns:
        Generated text string or None if generation fails
    """
    from shared.api.client import GenerationRequest

    config = _get_api_helper_config()
    resolved_max_tokens = max_tokens if max_tokens is not None else int(
        config.get_required_config('constants.api_helper.max_tokens')
    )
    resolved_temperature = temperature if temperature is not None else float(
        config.get_required_config('constants.api_helper.temperature')
    )
    resolved_frequency_penalty = frequency_penalty if frequency_penalty is not None else float(
        config.get_required_config('constants.api_helper.frequency_penalty')
    )
    resolved_presence_penalty = presence_penalty if presence_penalty is not None else float(
        config.get_required_config('constants.api_helper.presence_penalty')
    )

    # Get or create API client
    if api_client is None:
        api_client = get_api_client(provider)
    
    # Build request
    request = GenerationRequest(
        prompt=prompt,
        max_tokens=resolved_max_tokens,
        temperature=resolved_temperature,
        frequency_penalty=resolved_frequency_penalty,
        presence_penalty=resolved_presence_penalty
    )
    
    try:
        response = api_client.generate(request)
        
        if response and response.success and response.content:
            content = response.content.strip()
            # Clean up common formatting issues
            content = content.strip('`').strip('"').strip("'")
            return content
        
        logger.warning("Empty or failed response from API")
        return None
        
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return None


def generate_with_retry(
    prompt: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    max_retries: Optional[int] = None,
    api_client=None,
    provider: str = 'grok'
) -> Optional[str]:
    """
    Generate text with automatic retry on failure.
    
    Args:
        prompt: The prompt to send
        max_tokens: Maximum tokens to generate
        temperature: Generation temperature
        max_retries: Number of retry attempts (default 3)
        api_client: Optional pre-configured API client
        provider: API provider name
    
    Returns:
        Generated text or None after all retries exhausted
    """
    config = _get_api_helper_config()
    resolved_max_retries = max_retries if max_retries is not None else int(
        config.get_required_config('constants.api_helper.max_retries')
    )

    for attempt in range(resolved_max_retries):
        result = generate_text(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            api_client=api_client,
            provider=provider
        )
        if result:
            return result
        
        if attempt < resolved_max_retries - 1:
            logger.info(f"Retry {attempt + 2}/{resolved_max_retries}...")
    
    return None
