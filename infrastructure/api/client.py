"""
Enhanced API client with proper interface implementation.
"""

import requests
from typing import Dict, Any, Optional
from generator.core.interfaces.services import IAPIClient
from generator.core.exceptions import APIError
from generator.modules.logger import get_logger

logger = get_logger("api_client")


class APIClient(IAPIClient):
    """Enhanced API client implementing the IAPIClient interface."""

    def __init__(
        self, provider: str, api_key: str, base_config: Optional[Dict[str, Any]] = None
    ):
        self._provider = provider.upper()
        self._api_key = api_key
        self._config = base_config or {}
        self._setup_provider_config()

    def _setup_provider_config(self) -> None:
        """Setup provider-specific configuration."""
        # Import PROVIDER_MODELS from run.py instead of providers.py
        import sys
        import os

        # Add the project root to sys.path to ensure proper import
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        sys.path.insert(0, project_root)

        from run import PROVIDER_MODELS

        if self._provider not in PROVIDER_MODELS:
            raise APIError(f"Unsupported provider: {self._provider}", self._provider)

        self._provider_config = PROVIDER_MODELS[self._provider]

    def call_api(
        self,
        prompt: str,
        model: str,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        timeout: int = 60,
        **kwargs,
    ) -> str:
        """Make an API call to the AI provider."""
        if not prompt or not prompt.strip():
            raise APIError("Prompt cannot be empty", self._provider)

        # Minimal API logging
        try:
            response = self._make_request(
                prompt, model, temperature, max_tokens, timeout, **kwargs
            )

            return response

        except requests.exceptions.RequestException as e:
            raise APIError(
                f"Network error calling {self._provider}: {str(e)}",
                self._provider,
                getattr(e.response, "status_code", None)
                if hasattr(e, "response")
                else None,
            ) from e
        except Exception as e:
            raise APIError(
                f"Unexpected error calling {self._provider}: {str(e)}", self._provider
            ) from e

    def _make_request(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        **kwargs,
    ) -> str:
        """Make the actual HTTP request based on provider."""
        if self._provider == "GEMINI":
            return self._call_gemini(
                prompt, model, temperature, max_tokens, timeout, **kwargs
            )
        elif self._provider == "XAI":
            return self._call_xai(
                prompt, model, temperature, max_tokens, timeout, **kwargs
            )
        elif self._provider == "DEEPSEEK":
            return self._call_deepseek(
                prompt, model, temperature, max_tokens, timeout, **kwargs
            )
        else:
            raise APIError(f"Provider {self._provider} not implemented", self._provider)

    def _call_gemini(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call Google Gemini API."""
        url = self._provider_config["url_template"]

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        # Add API key as query parameter
        params = {"key": self._api_key}

        response = requests.post(
            url, headers=headers, json=payload, params=params, timeout=timeout
        )

        if response.status_code != 200:
            raise APIError(
                f"Gemini API error: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            )

        try:
            data = response.json()
            candidate = data["candidates"][0]

            # Check if the response was truncated or had issues
            finish_reason = candidate.get("finishReason", "")
            logger.debug(f"Gemini response finishReason: {finish_reason}")

            # Handle different content structures
            content = candidate.get("content", {})

            # Try to get text from parts array (normal case)
            if "parts" in content and content["parts"] and len(content["parts"]) > 0:
                text_content = content["parts"][0].get("text", "")
                if text_content.strip():  # Make sure we have actual content
                    return text_content
                else:
                    logger.warning(
                        f"Gemini returned empty text content, finishReason: {finish_reason}"
                    )

            # Handle various problematic finish reasons
            if finish_reason in ["MAX_TOKEN", "LENGTH"]:
                logger.error(f"Gemini response truncated: {finish_reason}")
                raise APIError(
                    f"Gemini response was truncated ({finish_reason}). Consider reducing prompt size or increasing max_tokens.",
                    self._provider,
                    response.status_code,
                    f"TRUNCATED_{finish_reason}",
                )
            elif finish_reason == "SAFETY":
                logger.error("Gemini response blocked by safety filters")
                raise APIError(
                    "Gemini response was blocked by safety filters. Consider modifying the prompt.",
                    self._provider,
                    response.status_code,
                    "SAFETY_FILTER_BLOCKED",
                )
            elif finish_reason == "RECITATION":
                logger.error("Gemini response blocked due to recitation")
                raise APIError(
                    "Gemini response was blocked due to recitation concerns. Consider modifying the prompt.",
                    self._provider,
                    response.status_code,
                    "RECITATION_BLOCKED",
                )

            # If we get here, we have an unexpected response structure
            logger.error(
                f"Unexpected Gemini response structure: finishReason={finish_reason}, content={content}"
            )
            raise APIError(
                f"Unexpected Gemini response format: missing content parts (finishReason: {finish_reason})",
                self._provider,
                response.status_code,
                response.text,
            )

        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini response: {response.text}")
            raise APIError(
                f"Failed to parse Gemini response: {str(e)}",
                self._provider,
                response.status_code,
                response.text,
            ) from e

    def _call_xai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call xAI Grok API."""
        url = "https://api.x.ai/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=timeout)

        if response.status_code != 200:
            raise APIError(
                f"xAI API error: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise APIError(
                f"Unexpected xAI response format: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            ) from e

    def _call_deepseek(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call DeepSeek API."""
        # Get URL from configuration instead of hardcoding
        url = self._base_config.get("url", "https://api.deepseek.com/v1/chat/completions")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(
            url, headers=headers, json=payload, timeout=timeout
        )  # Reduced timeout

        if response.status_code != 200:
            raise APIError(
                f"DeepSeek API error: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise APIError(
                f"Unexpected DeepSeek response format: {response.text}",
                self._provider,
                response.status_code,
                response.text,
            ) from e

    def get_provider_name(self) -> str:
        """Get the name of the AI provider."""
        return self._provider

    def call_ai_api(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 3000,
        timeout: int = 60,
    ) -> str:
        """Legacy method name for backward compatibility."""
        return self.call_api(prompt, model, temperature, max_tokens, timeout)
