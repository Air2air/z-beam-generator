#!/usr/bin/env python3
"""
Standardized API Client for Z-Beam Generator

Provides a robust, standardized interface for content generation using the DeepSeek API.
Features comprehensive error handling, retry logic, and configuration management.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standardized API response with comprehensive metadata"""

    success: bool
    content: str
    error: Optional[str] = None
    response_time: Optional[float] = None
    token_count: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    model_used: Optional[str] = None
    request_id: Optional[str] = None
    retry_count: int = 0


@dataclass
class GenerationRequest:
    """Structured request for content generation"""

    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class APIError(Exception):
    """Custom exception for API-related errors"""

    pass


class APIClient:
    """Standardized API client with comprehensive features"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        """Initialize the API client with configuration"""

        # Store parameters as instance attributes for test compatibility
        self.base_url = base_url
        self.model = model

        # Load configuration
        if config:
            self.config = config
        else:
            from .config import get_default_config

            self.config = get_default_config()

        # Override config with provided parameters
        if api_key:
            if hasattr(self.config, "api_key"):
                self.config.api_key = api_key
            else:
                self.config["api_key"] = api_key
        if base_url:
            if hasattr(self.config, "base_url"):
                self.config.base_url = base_url
            else:
                self.config["base_url"] = base_url
        if model:
            if hasattr(self.config, "model"):
                self.config.model = model
            else:
                self.config["model"] = model

        # Update instance attributes from config
        self.base_url = getattr(self.config, "base_url", None) or (
            self.config.get("base_url") if hasattr(self.config, "get") else base_url
        )
        self.model = getattr(self.config, "model", None) or (
            self.config.get("model")
            if hasattr(self.config, "get")
            else model or "deepseek-chat"
        )

        # Set timeout values with defaults
        self.timeout_connect = getattr(self.config, "timeout_connect", None) or (
            self.config.get("timeout_connect") if hasattr(self.config, "get") else 10
        )
        self.timeout_read = getattr(self.config, "timeout_read", None) or (
            self.config.get("timeout_read") if hasattr(self.config, "get") else 30
        )

        # Initialize session
        self.session = requests.Session()
        self._setup_session()

        # Statistics tracking
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_response_time": 0.0,
        }

    def _setup_session(self):
        """Setup the requests session with headers and configuration"""

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Z-Beam-Generator/1.0",
            }
        )

        # Configure session - disable HTTP-level retries since we handle retries at application level
        adapter = requests.adapters.HTTPAdapter(
            max_retries=0,  # Disable HTTP-level retries, we handle retries in generate()
            pool_connections=1,  # Reduce connection pool to prevent concurrent requests
            pool_maxsize=1,  # Reduce max size to prevent concurrent requests
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def test_connection(self) -> bool:
        """Test API connection with a minimal request"""

        logger.info("Testing API connection...")

        try:
            test_request = GenerationRequest(prompt="Test connection", max_tokens=10)
            response = self.generate(test_request)

            if response.success:
                logger.info("✅ API connection test successful")
                return True
            else:
                from utils.loud_errors import api_failure

                api_failure(
                    "api_client",
                    f"Connection test failed: {response.error}",
                    retry_count=None,
                )
                return False

        except Exception as e:
            from utils.loud_errors import api_failure

            api_failure(
                "api_client",
                f"Connection test failed with exception: {e}",
                retry_count=None,
            )
            return False

    def generate(self, request: GenerationRequest) -> APIResponse:
        """Generate content using the DeepSeek API with retry logic"""

        self.stats["total_requests"] += 1
        start_time = time.time()

        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._make_request(request)
                response.retry_count = attempt

                # Update statistics
                if response.success:
                    self.stats["successful_requests"] += 1
                    if response.token_count:
                        self.stats["total_tokens"] += response.token_count
                else:
                    self.stats["failed_requests"] += 1

                self.stats["total_response_time"] += response.response_time or 0
                return response

            except requests.exceptions.Timeout:
                if attempt == self.config.max_retries:
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Request timeout after {self.config.max_retries + 1} attempts",
                        response_time=time.time() - start_time,
                        retry_count=attempt,
                    )
                time.sleep(self.config.retry_delay * (attempt + 1))

            except requests.exceptions.ConnectionError:
                if attempt == self.config.max_retries:
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Connection error after {self.config.max_retries + 1} attempts",
                        response_time=time.time() - start_time,
                        retry_count=attempt,
                    )
                time.sleep(self.config.retry_delay * (attempt + 1))

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries:
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Unexpected error: {str(e)}",
                        response_time=time.time() - start_time,
                        retry_count=attempt,
                    )
                time.sleep(self.config.retry_delay * (attempt + 1))

        # Should never reach here, but just in case
        return APIResponse(
            success=False,
            content="",
            error="Maximum retries exceeded",
            response_time=time.time() - start_time,
        )

    def _make_request(self, request: GenerationRequest) -> APIResponse:
        """Make a single API request"""

        start_time = time.time()

        # Handle Gemini API format differently
        if "gemini" in self.model.lower():
            return self._make_gemini_request(request, start_time)

        # Standard OpenAI-compatible format for other providers
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        # Log API request details
        logger.info(f"🌐 Making API request to {self.model}")
        logger.info(f"📝 Prompt length: {len(request.prompt)} chars")
        logger.info(
            f"🎯 Max tokens: {request.max_tokens}, Temperature: {request.temperature}"
        )

        # API Terminal Messaging - Start
        print(f"🚀 [API CLIENT] Starting request to {self.model}")
        print(
            f"📤 [API CLIENT] Sending prompt ({len(request.prompt)} chars) with system prompt ({len(request.system_prompt) if request.system_prompt else 0} chars)"
        )
        print(
            f"⚙️ [API CLIENT] Config: max_tokens={request.max_tokens}, temperature={request.temperature}"
        )

        # Debug: Log config type and attributes
        logger.info(f"🔧 Config type: {type(self.config)}")
        logger.info(
            f"🔧 Config attributes: {dir(self.config) if hasattr(self.config, '__dict__') else 'No __dict__'}"
        )
        logger.info(f"🔧 Base URL: {self.base_url}")
        logger.info(f"🔧 Model: {self.model}")

        # Prepare payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stream": False,
        }

        # Add provider-specific parameters
        if "grok" not in self.model.lower():
            # Only add these parameters for non-Grok models
            payload["frequency_penalty"] = request.frequency_penalty
            payload["presence_penalty"] = request.presence_penalty

        # Make request with enhanced timeout handling
        try:
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=(self.timeout_connect, self.timeout_read),
            )
        except requests.exceptions.ReadTimeout:
            # Handle read timeout specifically
            from utils.loud_errors import network_failure

            network_failure("api_client", f"Read timeout after {self.timeout_read}s")
            return APIResponse(
                success=False,
                content="",
                error=f"Response read timeout after {self.timeout_read} seconds",
                response_time=time.time() - start_time,
            )
        except requests.exceptions.ConnectTimeout:
            # Handle connection timeout specifically
            from utils.loud_errors import network_failure

            network_failure(
                "api_client", f"Connection timeout after {self.timeout_connect}s"
            )
            return APIResponse(
                success=False,
                content="",
                error=f"Connection timeout after {self.timeout_connect} seconds",
                response_time=time.time() - start_time,
            )

        response_time = time.time() - start_time

        # Debug: Log response details
        logger.info(f"🌐 Response status: {response.status_code}")
        logger.info(f"🌐 Response headers: {dict(response.headers)}")
        logger.info(f"🌐 Response content preview: {response.text[:200]}...")

        # API Terminal Messaging - Response received
        print(f"📥 [API CLIENT] Received response (Status: {response.status_code})")

        # Add timeout protection for response content reading using threading
        import threading

        content_loaded = [False]
        content_data = [None]
        content_error = [None]

        def load_content_with_timeout():
            try:
                content_data[0] = response.content
                content_loaded[0] = True
            except Exception as e:
                content_error[0] = str(e)

        # Start content loading in a separate thread with timeout
        content_thread = threading.Thread(target=load_content_with_timeout)
        content_thread.daemon = True
        content_thread.start()

        # Wait for content loading with timeout
        content_timeout = min(self.timeout_read, 30)  # Max 30s for content reading
        content_thread.join(timeout=content_timeout)

        if not content_loaded[0]:
            if content_thread.is_alive():
                from utils.loud_errors import network_failure

                network_failure(
                    "api_client", f"Content reading timeout after {content_timeout}s"
                )
                return APIResponse(
                    success=False,
                    content="",
                    error=f"Content reading timeout after {content_timeout} seconds",
                    response_time=time.time() - start_time,
                )
            elif content_error[0]:
                from utils.loud_errors import api_failure

                api_failure(
                    "api_client",
                    f"Content reading error: {content_error[0]}",
                    retry_count=None,
                )
                return APIResponse(
                    success=False,
                    content="",
                    error=f"Content reading error: {content_error[0]}",
                    response_time=time.time() - start_time,
                )

        print(
            f"📦 [API CLIENT] Content loaded successfully ({len(content_data[0])} bytes)"
        )

        # Process response
        if response.status_code == 200:
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                from utils.loud_errors import api_failure

                api_failure("api_client", f"JSON decode error: {e}", retry_count=None)
                return APIResponse(
                    success=False,
                    content="",
                    error=f"Invalid JSON response: {e}",
                    response_time=time.time() - start_time,
                )

            logger.info(f"📄 Raw response data type: {type(data)}")
            logger.info(
                f"📄 Raw response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}"
            )

            content = data["choices"][0]["message"]["content"]

            # Log successful API response details
            usage = data.get("usage", {})
            logger.info(f"✅ API response successful ({response.status_code})")
            logger.info(f"⏱️  Response time: {response_time:.2f}s")
            logger.info(
                f"📊 Tokens used: {usage.get('total_tokens', 'N/A')} (prompt: {usage.get('prompt_tokens', 'N/A')}, completion: {usage.get('completion_tokens', 'N/A')})"
            )
            logger.info(f"📄 Content length: {len(content)} chars")

            # API Terminal Messaging - Success
            print("✅ [API CLIENT] Request completed successfully")
            print(f"⏱️ [API CLIENT] Response time: {response_time:.2f}s")
            print(
                f"📊 [API CLIENT] Tokens used: {usage.get('total_tokens', 'N/A')} total"
            )
            print(f"📄 [API CLIENT] Content length: {len(content)} chars")

            # Handle empty content from reasoning models like grok-4
            if (
                not content
                and data.get("choices", [{}])[0].get("message", {}).get("content") == ""
            ):
                completion_tokens = (
                    data.get("usage", {})
                    .get("completion_tokens_details", {})
                    .get("reasoning_tokens", 0)
                )
                if completion_tokens > 0:
                    print(
                        "❌ [API CLIENT] Model produced reasoning tokens but no completion content"
                    )
                    logger.error(
                        "❌ Model produced reasoning tokens but no completion content"
                    )
                    return APIResponse(
                        success=False,
                        content="",
                        error="Model produced reasoning tokens but no completion content. This may indicate the model needs different parameters.",
                        response_time=response_time,
                        token_count=data.get("usage", {}).get("total_tokens"),
                        model_used=data.get("model", self.model),
                    )

            # Extract usage information
            usage = data.get("usage", {})

            return APIResponse(
                success=True,
                content=content,
                response_time=response_time,
                token_count=usage.get("total_tokens"),
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                model_used=data.get("model", self.model),
                request_id=response.headers.get("x-request-id"),
            )
        else:
            # Handle error response
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                logger.info(f"📄 Error response data type: {type(error_data)}")
                logger.info(f"📄 Error response content: {error_data}")

                # API Terminal Messaging - Error
                print(
                    f"❌ [API CLIENT] Request failed with status {response.status_code}"
                )

                # Handle different error response formats
                if isinstance(error_data, dict):
                    error_details = error_data.get("error", {})
                    if isinstance(error_details, dict):
                        error_msg += (
                            f": {error_details.get('message', 'Unknown error')}"
                        )
                        # Log additional error details
                        if "type" in error_details:
                            logger.error(f"Error type: {error_details['type']}")
                        if "code" in error_details:
                            logger.error(f"Error code: {error_details['code']}")
                    elif isinstance(error_details, str):
                        error_msg += f": {error_details}"
                    else:
                        error_msg += f": {error_data.get('message', error_data.get('error', 'Unknown error'))}"
                elif isinstance(error_data, str):
                    error_msg += f": {error_data}"
                else:
                    error_msg += f": {str(error_data)}"

            except json.JSONDecodeError:
                error_msg += f": {response.text}"

            print(f"❌ [API CLIENT] Error details: {error_msg}")
            return APIResponse(
                success=False, content="", error=error_msg, response_time=response_time
            )

    def _make_gemini_request(
        self, request: GenerationRequest, start_time: float
    ) -> APIResponse:
        """Make a request to Gemini API with its specific format"""

        # Combine system prompt and user prompt for Gemini
        full_prompt = request.prompt
        if request.system_prompt:
            full_prompt = f"{request.system_prompt}\n\n{request.prompt}"

        # Log API request details
        logger.info(f"🌐 Making Gemini API request to {self.model}")
        logger.info(f"📝 Prompt length: {len(full_prompt)} chars")
        logger.info(
            f"🎯 Max tokens: {request.max_tokens}, Temperature: {request.temperature}"
        )

        # Prepare Gemini-specific payload
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": request.temperature,
                "topP": request.top_p,
                "maxOutputTokens": request.max_tokens,
            },
        }

        # Make request to Gemini API
        api_key = getattr(self.config, "api_key", None) or (
            self.config.get("api_key") if hasattr(self.config, "get") else None
        )

        # Try API key in URL parameter (standard method)
        url = (
            f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={api_key}"
        )

        headers = {"Content-Type": "application/json"}

        response = self.session.post(
            url,
            json=payload,
            headers=headers,
            timeout=(self.timeout_connect, self.timeout_read),
        )

        response_time = time.time() - start_time

        # Process Gemini response
        if response.status_code == 200:
            data = response.json()

            # Extract content from Gemini response format
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts and "text" in parts[0]:
                    content = parts[0]["text"]
                else:
                    content = ""
            else:
                content = ""

            # Log successful API response details
            usage_metadata = data.get("usageMetadata", {})
            total_tokens = usage_metadata.get("totalTokenCount", 0)
            prompt_tokens = usage_metadata.get("promptTokenCount", 0)
            completion_tokens = usage_metadata.get("candidatesTokenCount", 0)

            logger.info(f"✅ Gemini API response successful ({response.status_code})")
            logger.info(f"⏱️  Response time: {response_time:.2f}s")
            logger.info(
                f"📊 Tokens used: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})"
            )
            logger.info(f"📄 Content length: {len(content)} chars")

            return APIResponse(
                success=True,
                content=content,
                response_time=response_time,
                token_count=total_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                model_used=self.model,
                request_id=response.headers.get("x-request-id"),
            )
        else:
            # Handle Gemini error response
            error_msg = f"Gemini API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_details = error_data["error"]
                    error_msg += f": {error_details.get('message', 'Unknown error')}"
                    if "code" in error_details:
                        logger.error(f"Gemini error code: {error_details['code']}")

            except json.JSONDecodeError:
                error_msg += f": {response.text}"

            from utils.loud_errors import api_failure

            api_failure("gemini_api", error_msg, retry_count=None)

            return APIResponse(
                success=False, content="", error=error_msg, response_time=response_time
            )

    def generate_simple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> APIResponse:
        """Simplified generation method for backward compatibility"""

        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature
            if temperature is not None
            else self.config.temperature,
        )

        return self.generate(request)

    def get_statistics(self) -> Dict[str, Any]:
        """Get client usage statistics"""

        avg_response_time = (
            self.stats["total_response_time"] / self.stats["total_requests"]
            if self.stats["total_requests"] > 0
            else 0
        )

        success_rate = (
            self.stats["successful_requests"] / self.stats["total_requests"] * 100
            if self.stats["total_requests"] > 0
            else 0
        )

        return {
            **self.stats,
            "average_response_time": avg_response_time,
            "success_rate": success_rate,
        }

    def reset_statistics(self):
        """Reset usage statistics"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_response_time": 0.0,
        }


class MockAPIClient:
    """Mock API client for testing without real API calls - FAIL-FAST: No mock content allowed"""

    def __init__(self, *args, **kwargs):
        # FAIL-FAST: Mock clients are not permitted in fail-fast architecture
        raise Exception(
            "MockAPIClient is not allowed in fail-fast architecture - use real API clients only"
        )

    def test_connection(self) -> bool:
        """Mock connection test - FAIL-FAST: Not permitted"""
        raise Exception("MockAPIClient methods not permitted in fail-fast architecture")

    def generate(self, request: GenerationRequest) -> APIResponse:
        """Generate mock content - FAIL-FAST: Not permitted"""
        raise Exception("MockAPIClient methods not permitted in fail-fast architecture")

    def generate_simple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> APIResponse:
        """Simplified mock generation - FAIL-FAST: Not permitted"""
        raise Exception("MockAPIClient methods not permitted in fail-fast architecture")

    def get_statistics(self) -> Dict[str, Any]:
        """Get mock statistics - FAIL-FAST: Not permitted"""
        raise Exception("MockAPIClient methods not permitted in fail-fast architecture")

    def reset_statistics(self):
        """Reset mock statistics - FAIL-FAST: Not permitted"""
        raise Exception("MockAPIClient methods not permitted in fail-fast architecture")
