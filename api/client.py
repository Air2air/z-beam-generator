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
    max_tokens: int = None  # Must be provided by run.py
    temperature: float = None  # Must be provided by run.py
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
            raise ValueError("Configuration must be provided explicitly - no defaults allowed in fail-fast architecture")

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

        # Set timeout values - FAIL-FAST: Must be explicitly configured
        self.timeout_connect = getattr(self.config, "timeout_connect", None) or (
            self.config.get("timeout_connect") if hasattr(self.config, "get") else None
        )
        if self.timeout_connect is None:
            raise ValueError("timeout_connect must be configured explicitly - no defaults allowed")

        self.timeout_read = getattr(self.config, "timeout_read", None) or (
            self.config.get("timeout_read") if hasattr(self.config, "get") else None
        )
        if self.timeout_read is None:
            raise ValueError("timeout_read must be configured explicitly - no defaults allowed")

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

        # Get API key from environment variable specified in config
        api_key = None
        if isinstance(self.config, dict) and "env_var" in self.config:
            # If config is a dict with env_var field, get API key from that environment variable
            env_var = self.config["env_var"]
            api_key = os.getenv(env_var)
        else:
            # No fallbacks - explicit API key required
            api_key = getattr(self.config, "api_key", None) or (
                self.config.get("api_key") if hasattr(self.config, "get") else None
            )

        if not api_key:
            raise ValueError(f"API key not found. Please ensure the API key environment variable is set.")

        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
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

        print("🔍 [API CLIENT] Testing connection to API endpoint...")
        logger.info("Testing API connection...")

        try:
            # Get test configuration from run.py - FAIL FAST if unavailable
            from run import get_component_generation_config
            test_config = get_component_generation_config("test_connection")
            test_max_tokens = test_config["max_tokens"]
            
            test_request = GenerationRequest(prompt="Test connection - respond with 'OK'", max_tokens=test_max_tokens)
            start_time = time.time()
            response = self.generate(test_request)
            test_time = time.time() - start_time

            if response.success:
                print(f"✅ [API CLIENT] Connection test successful in {test_time:.2f}s")
                print(f"📊 [API CLIENT] Test tokens used: {response.token_count or 'N/A'}")
                logger.info("✅ API connection test successful")
                return True
            else:
                print(f"❌ [API CLIENT] Connection test failed: {response.error}")
                from utils.ai.loud_errors import api_failure

                api_failure(
                    "api_client",
                    f"Connection test failed: {response.error}",
                    retry_count=None,
                )
                return False

        except Exception as e:
            print(f"💥 [API CLIENT] Connection test error: {str(e)}")
            from utils.ai.loud_errors import api_failure

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

        # Get max_retries - no fallbacks allowed
        max_retries = getattr(self.config, "max_retries", None) or (
            self.config.get("max_retries") if hasattr(self.config, "get") else None
        )
        if max_retries is None:
            raise RuntimeError("CONFIGURATION ERROR: max_retries not defined in run.py API_PROVIDERS")

        # Get retry_delay - no fallbacks allowed
        retry_delay = getattr(self.config, "retry_delay", None) or (
            self.config.get("retry_delay") if hasattr(self.config, "get") else None
        )
        if retry_delay is None:
            raise RuntimeError("CONFIGURATION ERROR: retry_delay not defined in run.py API_PROVIDERS")

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    # Exponential backoff with jitter to avoid thundering herd
                    backoff_delay = retry_delay * (2 ** (attempt - 1))
                    print(f"🔄 [API CLIENT] Retry attempt {attempt}/{max_retries} after {backoff_delay:.1f}s delay")
                    time.sleep(backoff_delay)
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
                if attempt == max_retries:
                    print(f"⏰ [API CLIENT] Request timeout after {max_retries + 1} attempts")
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Request timeout after {max_retries + 1} attempts",
                        response_time=time.time() - start_time,
                        retry_count=attempt,
                    )
                backoff_delay = retry_delay * (2 ** attempt)
                print(f"⏳ [API CLIENT] Timeout on attempt {attempt + 1}, retrying in {backoff_delay:.1f}s...")
                time.sleep(backoff_delay)

            except requests.exceptions.ConnectionError:
                if attempt == max_retries:
                    print(f"🔌 [API CLIENT] Connection error after {max_retries + 1} attempts")
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Connection error after {max_retries + 1} attempts",
                        response_time=time.time() - start_time,
                        retry_count=attempt,
                    )
                backoff_delay = retry_delay * (2 ** attempt)
                print(f"🔌 [API CLIENT] Connection failed on attempt {attempt + 1}, retrying in {backoff_delay:.1f}s...")
                time.sleep(backoff_delay)

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    print(f"💥 [API CLIENT] Unexpected error after {max_retries + 1} attempts: {str(e)}")
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Unexpected error: {str(e)}",
                        response_time=time.time() - start_time,
                        retry_count=attempt,
                    )
                backoff_delay = retry_delay * (2 ** attempt)
                print(f"⚠️ [API CLIENT] Unexpected error on attempt {attempt + 1}, retrying in {backoff_delay:.1f}s...")
                time.sleep(backoff_delay)

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

        # Standard OpenAI-compatible format for all providers
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
        print(f"🔗 [API CLIENT] Endpoint: {self.base_url}/v1/chat/completions")
        print(f"⏳ [API CLIENT] Timeout: connect={self.timeout_connect}s, read={self.timeout_read}s")

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
            print("🔌 [API CLIENT] Establishing connection...")
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=(self.timeout_connect, self.timeout_read),
            )
            print("📡 [API CLIENT] Connection established, waiting for response...")
        except requests.exceptions.ReadTimeout:
            # Handle read timeout specifically
            from utils.ai.loud_errors import network_failure

            network_failure("api_client", f"Read timeout after {self.timeout_read}s")
            return APIResponse(
                success=False,
                content="",
                error=f"Response read timeout after {self.timeout_read} seconds",
                response_time=time.time() - start_time,
            )
        except requests.exceptions.ConnectTimeout:
            # Handle connection timeout specifically
            from utils.ai.loud_errors import network_failure

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

        # Simplified content reading without complex threading
        try:
            content_data = response.content
            print(
                f"📦 [API CLIENT] Content loaded successfully ({len(content_data)} bytes)"
            )
        except Exception as e:
            from utils.ai.loud_errors import network_failure

            network_failure(
                "api_client", f"Content reading error: {e}"
            )
            return APIResponse(
                success=False,
                content="",
                error=f"Content reading error: {e}",
                response_time=time.time() - start_time,
            )

        # Process response
        if response.status_code == 200:
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                from utils.ai.loud_errors import api_failure

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

    def generate_simple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> APIResponse:
        """Simplified generation method for backward compatibility"""

        # No defaults allowed - all parameters must be explicitly provided
        if max_tokens is None:
            raise RuntimeError("CONFIGURATION ERROR: max_tokens must be explicitly provided - no defaults allowed in fail-fast architecture")
        if temperature is None:
            raise RuntimeError("CONFIGURATION ERROR: temperature must be explicitly provided - no defaults allowed in fail-fast architecture")

        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
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

        stats = {
            **self.stats,
            "average_response_time": avg_response_time,
            "success_rate": success_rate,
        }

        # Display statistics in terminal
        print("📊 [API CLIENT] Usage Statistics:")
        print(f"   �� Total Requests: {stats['total_requests']}")
        print(f"   ✅ Successful: {stats['successful_requests']}")
        print(f"   ❌ Failed: {stats['failed_requests']}")
        print(f"   📊 Success Rate: {stats['success_rate']:.1f}%")
        print(f"   ⏱️  Avg Response Time: {stats['average_response_time']:.2f}s")
        print(f"   🪙 Total Tokens: {stats['total_tokens']}")

        return stats

    def reset_statistics(self):
        """Reset usage statistics"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_response_time": 0.0,
        }
        print("🔄 [API CLIENT] Statistics reset")

    def show_status(self):
        """Display current client status and configuration"""
        print("📊 [API CLIENT] Current Status:")
        print(f"   🤖 Model: {self.model}")
        print(f"   🔗 Base URL: {self.base_url}")
        print(f"   ⏳ Timeouts: connect={self.timeout_connect}s, read={self.timeout_read}s")
        print(f"   📈 Requests: {self.stats['total_requests']} total")
        print(f"   ✅ Success: {self.stats['successful_requests']}")
        print(f"   ❌ Failed: {self.stats['failed_requests']}")
        print(f"   🪙 Tokens: {self.stats['total_tokens']}")
        avg_time = self.stats['total_response_time'] / max(1, self.stats['total_requests'])
        print(f"   ⏱️ Avg Response Time: {avg_time:.2f}s")
        print("   🔧 Configuration: Valid" if self.config else "   🔧 Configuration: Invalid")

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of the API client"""

        print("🏥 [API CLIENT] Health Check:")

        # Basic configuration status
        config_status = {
            "model": self.model,
            "base_url": self.base_url,
            "timeout_connect": self.timeout_connect,
            "timeout_read": self.timeout_read,
            "config_valid": True
        }

        print(f"   🤖 Model: {config_status['model']}")
        print(f"   🔗 Base URL: {config_status['base_url']}")
        print(f"   ⏳ Timeouts: connect={config_status['timeout_connect']}s, read={config_status['timeout_read']}s")

        # Statistics summary
        stats = self.get_statistics()
        health_score = min(100, stats['success_rate'])  # Simple health score based on success rate

        if health_score >= 95:
            health_status = "🟢 Excellent"
        elif health_score >= 80:
            health_status = "�� Good"
        elif health_score >= 60:
            health_status = "🟠 Fair"
        else:
            health_status = "🔴 Poor"

        print(f"   ❤️ Health Status: {health_status} ({health_score:.1f}%)")

        # Connection test
        print("   🔍 Testing connection...")
        connection_ok = self.test_connection()

        if connection_ok:
            print("   🔗 Connection: 🟢 Healthy")
        else:
            print("   🔗 Connection: 🔴 Unhealthy")

        return {
            "config": config_status,
            "statistics": stats,
            "health_score": health_score,
            "health_status": health_status,
            "connection_healthy": connection_ok,
            "timestamp": time.time()
        }

# End of production API client code
