# generator/modules/api_client.py

import requests
import json
import time
import random
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from modules.logger import get_logger
from config.settings import AppConfig

logger = get_logger("api_client")
config = AppConfig()


# Note: Provider constants kept for backward compatibility
# In production, use get_config().get_provider() instead
class APIProvider(Enum):
    GEMINI = "GEMINI"  # Use get_config().get_provider() in new code
    OPENAI = "OPENAI"  # Use get_config().get_provider() in new code
    XAI = "XAI"
    DEEPSEEK = "DEEPSEEK"


@dataclass
class APIResponse:
    content: Optional[str]
    success: bool
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    tokens_used: Optional[int] = None


class RateLimitError(Exception):
    pass


class APIClientError(Exception):
    pass


def call_ai_api(
    prompt: str,
    provider: str,
    model: str,
    api_keys: Dict[str, str],
    temperature: float = None,
    max_tokens: int = 1000,
    retries: int = 3,
    backoff_factor: float = 0.5,
    timeout: int = None,
    url_template: str = None,
) -> Optional[str]:
    # Set defaults from config if not provided
    if temperature is None:
        from config.global_config import get_config
        temperature = get_config().get_content_temperature()
    if timeout is None:
        from config.global_config import get_config
        timeout = get_config().get_api_timeout()
        
    try:
        provider_enum = APIProvider(provider.upper())
    except ValueError:
        raise APIClientError(f"Unsupported provider: {provider}")

    response = _make_api_request(
        prompt=prompt,
        provider=provider_enum,
        model=model,
        api_keys=api_keys,
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
        backoff_factor=backoff_factor,
        timeout=timeout,
        url_template=url_template,
    )

    if response.success:
        logger.log_api_response(provider_enum.value, success=True)
        return response.content
    else:
        logger.log_api_response(
            provider_enum.value, success=False, error=response.error_message
        )
        return None


def _make_api_request(
    prompt: str,
    provider: APIProvider,
    model: str,
    api_keys: Dict[str, str],
    temperature: float,
    max_tokens: int,
    retries: int,
    backoff_factor: float,
    timeout: int,
    url_template: str = None,
) -> APIResponse:
    api_key = _get_api_key(provider, api_keys)
    if not api_key:
        return APIResponse(
            content=None,
            success=False,
            error_message=f"API key not found for {provider.value}",
        )

    url, headers, params, data = _build_request_config(
        provider, model, api_key, prompt, temperature, max_tokens, url_template
    )

    # Use centralized API logging
    logger.log_api_request(
        provider=provider.value,
        model=model,
        prompt_length=len(prompt),
        temperature=temperature,
        max_tokens=max_tokens,
    )

    with logger.time_operation(f"API call to {provider.value}"):
        for attempt in range(retries):
            try:
                logger.debug(
                    f"API attempt {attempt + 1}/{retries} for {provider.value}"
                )

                response = requests.post(
                    url=url, headers=headers, params=params, json=data, timeout=timeout
                )

                if response.status_code == 429:
                    # Respect Retry-After header if present
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait_time = float(retry_after)
                        except ValueError:
                            wait_time = backoff_factor * (2**attempt)
                    else:
                        # Exponential backoff with jitter
                        base = backoff_factor * (2**attempt)
                        wait_time = base + (
                            base * 0.5 * (2 * random.random() - 1)
                        )  # ±50% jitter
                    logger.warning(f"Rate limited. Waiting {wait_time:.2f}s...")
                    time.sleep(max(wait_time, 0))
                    continue
                elif response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code}. Retrying...")
                    time.sleep(backoff_factor)
                    continue
                elif response.status_code >= 400:
                    return APIResponse(
                        content=None,
                        success=False,
                        error_message=f"Client error {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )

                response.raise_for_status()
                return _parse_response(provider, response)

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt == retries - 1:
                    return APIResponse(
                        content=None,
                        success=False,
                        error_message="Request timed out after all retries",
                    )
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return APIResponse(
                        content=None,
                        success=False,
                        error_message=f"Connection failed: {e}",
                    )
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return APIResponse(
                    content=None, success=False, error_message=f"Unexpected error: {e}"
                )

    return APIResponse(
        content=None, success=False, error_message="All retry attempts failed"
    )


def _get_api_key(provider: APIProvider, api_keys: Dict[str, str]) -> Optional[str]:
    key_name = f"{provider.value}_API_KEY"
    return api_keys.get(key_name)


def _build_request_config(
    provider: APIProvider,
    model: str,
    api_key: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    url_template: str = None,
) -> Tuple[str, Dict[str, str], Optional[Dict[str, str]], Dict[str, Any]]:
    headers = {"Content-Type": "application/json"}
    params = None

    # Use url_template if provided, else fallback to config
    if provider == APIProvider.GEMINI:
        url = url_template.format(model=model) if url_template else None
        params = {"key": api_key}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
    elif provider == APIProvider.OPENAI:
        url = url_template if url_template else None
        headers["Authorization"] = f"Bearer {api_key}"
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    elif provider == APIProvider.XAI:
        url = url_template  # Always use url_template from run.py
        headers["Authorization"] = f"Bearer {api_key}"
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    elif provider == APIProvider.DEEPSEEK:
        url = url_template if url_template else None
        headers["Authorization"] = f"Bearer {api_key}"
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    return url, headers, params, data


def _parse_response(provider: APIProvider, response: requests.Response) -> APIResponse:
    try:
        # Log the full raw response for XAI for debugging (now at DEBUG level to reduce terminal clutter)
        if provider == APIProvider.XAI:
            logger.debug(f"Raw XAI response: {response.text}")
        response_json = response.json()

        if provider == APIProvider.GEMINI:
            candidates = response_json.get("candidates", [])
            if candidates and candidates[0].get("content", {}).get("parts"):
                content = candidates[0]["content"]["parts"][0]["text"]
                return APIResponse(content=content, success=True)
            else:
                return APIResponse(
                    content=None,
                    success=False,
                    error_message="Invalid Gemini response structure",
                )

        elif provider in [APIProvider.OPENAI, APIProvider.XAI, APIProvider.DEEPSEEK]:
            choices = response_json.get("choices", [])
            if choices and choices[0].get("message", {}).get("content"):
                content = choices[0]["message"]["content"]
                tokens_used = response_json.get("usage", {}).get("total_tokens")
                return APIResponse(
                    content=content, success=True, tokens_used=tokens_used
                )
            else:
                return APIResponse(
                    content=None,
                    success=False,
                    error_message=f"Invalid {provider.value} response structure",
                )

    except json.JSONDecodeError as e:
        return APIResponse(
            content=None, success=False, error_message=f"JSON decode error: {e}"
        )
    except Exception as e:
        return APIResponse(
            content=None, success=False, error_message=f"Response parsing error: {e}"
        )
