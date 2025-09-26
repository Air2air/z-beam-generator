#!/usr/bin/env python3
"""
Enhanced API Client with Optimized Timeout Handling for Z-Beam Generator

This module provides an improved API client with advanced timeout management,
connection pooling, and intelligent retry strategies to minimize API timeouts.
"""

import json
import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class TimeoutConfig:
    """Advanced timeout configuration with intelligent defaults from run.py"""

    def __init__(self):
        # Get defaults from centralized configuration
        try:
            from run import get_enhanced_client_config
            config = get_enhanced_client_config()
            self.connect_timeout = config["connect_timeout"]
            self.read_timeout = config["read_timeout"]
            self.total_timeout = config["total_timeout"]
            self.max_retries = config["max_retries"]
            self.base_retry_delay = config["base_retry_delay"]
            self.max_retry_delay = config["max_retry_delay"]
            self.jitter_factor = config["jitter_factor"]
        except ImportError:
            # Fallback values if run.py not available (should not happen in production)
            self.connect_timeout = 15.0
            self.read_timeout = 90.0
            self.total_timeout = 120.0
            self.max_retries = 5
            self.base_retry_delay = 2.0
            self.max_retry_delay = 30.0
            self.jitter_factor = 0.1


class EnhancedAPIClient:
    """Enhanced API client with optimized timeout handling and connection pooling"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_config: Optional[TimeoutConfig] = None,
    ):
        """Initialize enhanced API client with optimized settings"""

        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout_config = timeout_config or TimeoutConfig()

        # Create session with connection pooling and retry strategy
        self.session = self._create_optimized_session()

        # Statistics tracking
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "timeout_errors": 0,
            "connection_errors": 0,
            "total_tokens": 0,
            "total_response_time": 0.0,
            "retry_counts": [],
        }

        logger.info(f"🚀 Enhanced API Client initialized for {model}")

    def _create_optimized_session(self) -> requests.Session:
        """Create session with optimized connection pooling and retry strategy"""

        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.timeout_config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=self.timeout_config.base_retry_delay,
            raise_on_status=False,
        )

        # Create adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # Connection pool size
            pool_maxsize=20,      # Max connections per pool
            pool_block=False,     # Don't block when pool is full
        )

        # Mount adapter for both HTTP and HTTPS
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Z-Beam-Generator/1.0",
        })

        return session

    def _calculate_timeout(self, attempt: int = 0) -> Tuple[float, float]:
        """Calculate dynamic timeouts based on attempt number"""

        # Progressive timeout increases for retries
        timeout_multiplier = min(1.0 + (attempt * 0.5), 3.0)

        connect_timeout = self.timeout_config.connect_timeout * timeout_multiplier
        read_timeout = self.timeout_config.read_timeout * timeout_multiplier

        # Ensure we don't exceed total timeout
        max_read_timeout = self.timeout_config.total_timeout - connect_timeout
        read_timeout = min(read_timeout, max_read_timeout)

        return connect_timeout, read_timeout

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter"""

        # Exponential backoff: base_delay * (2 ^ attempt)
        delay = self.timeout_config.base_retry_delay * (2 ** attempt)

        # Cap the delay
        delay = min(delay, self.timeout_config.max_retry_delay)

        # Add jitter to prevent thundering herd
        jitter = delay * self.timeout_config.jitter_factor * random.uniform(-1, 1)
        delay = max(0.1, delay + jitter)

        return delay

    def generate_with_timeout_optimization(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = None,  # Must be provided by run.py
        temperature: float = None,  # Must be provided by run.py
    ) -> Dict[str, Any]:
        """Generate content with optimized timeout handling"""

        self.stats["total_requests"] += 1
        start_time = time.time()

        # Prepare request payload
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        print(f"🚀 [ENHANCED CLIENT] Starting optimized request to {self.model}")
        print(f"📤 [ENHANCED CLIENT] Prompt: {len(prompt)} chars")
        print(f"⚙️ [ENHANCED CLIENT] Config: max_tokens={max_tokens}, temp={temperature}")

        # Retry loop with intelligent timeout management
        last_exception = None

        for attempt in range(self.timeout_config.max_retries + 1):
            try:
                # Calculate dynamic timeouts for this attempt
                connect_timeout, read_timeout = self._calculate_timeout(attempt)

                print(f"🔄 [ENHANCED CLIENT] Attempt {attempt + 1}/{self.timeout_config.max_retries + 1}")
                print(f"⏳ [ENHANCED CLIENT] Timeouts: connect={connect_timeout:.1f}s, read={read_timeout:.1f}s")

                # Make request with calculated timeouts
                response = self.session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=(connect_timeout, read_timeout),
                )

                response_time = time.time() - start_time

                # Handle successful response
                if response.status_code == 200:
                    result = self._process_successful_response(response, response_time, attempt)
                    self.stats["successful_requests"] += 1
                    self.stats["retry_counts"].append(attempt)
                    return result

                # Handle rate limiting
                elif response.status_code == 429:
                    retry_after = self._handle_rate_limit(response)
                    if attempt < self.timeout_config.max_retries:
                        print(f"🚦 [ENHANCED CLIENT] Rate limited, waiting {retry_after}s...")
                        time.sleep(retry_after)
                        continue

                # Handle other errors
                else:
                    error_result = self._process_error_response(response, response_time, attempt)
                    self.stats["failed_requests"] += 1
                    return error_result

            except requests.exceptions.Timeout as e:
                last_exception = e
                self.stats["timeout_errors"] += 1
                print(f"⏰ [ENHANCED CLIENT] Timeout on attempt {attempt + 1}: {str(e)}")

                if attempt < self.timeout_config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    print(f"⏳ [ENHANCED CLIENT] Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                self.stats["connection_errors"] += 1
                print(f"🔌 [ENHANCED CLIENT] Connection error on attempt {attempt + 1}: {str(e)}")

                if attempt < self.timeout_config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    print(f"🔌 [ENHANCED CLIENT] Retrying connection in {delay:.1f}s...")
                    time.sleep(delay)
                    continue

            except Exception as e:
                last_exception = e
                print(f"💥 [ENHANCED CLIENT] Unexpected error on attempt {attempt + 1}: {str(e)}")

                if attempt < self.timeout_config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    print(f"⚠️ [ENHANCED CLIENT] Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue

        # All retries exhausted
        response_time = time.time() - start_time
        self.stats["failed_requests"] += 1

        return {
            "success": False,
            "content": "",
            "error": f"All {self.timeout_config.max_retries + 1} attempts failed. Last error: {str(last_exception)}",
            "response_time": response_time,
            "retry_count": self.timeout_config.max_retries,
            "timeout_config": {
                "connect_timeout": self.timeout_config.connect_timeout,
                "read_timeout": self.timeout_config.read_timeout,
                "total_timeout": self.timeout_config.total_timeout,
            }
        }

    def _handle_rate_limit(self, response: requests.Response) -> float:
        """Handle rate limiting with intelligent backoff"""

        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass

        # Default rate limit backoff
        return self.timeout_config.base_retry_delay * 2

    def _process_successful_response(
        self,
        response: requests.Response,
        response_time: float,
        retry_count: int
    ) -> Dict[str, Any]:
        """Process successful API response"""

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            print("✅ [ENHANCED CLIENT] Request completed successfully")
            print(f"⏱️ [ENHANCED CLIENT] Response time: {response_time:.2f}s")
            print(f"📊 [ENHANCED CLIENT] Tokens: {usage.get('total_tokens', 'N/A')}")

            return {
                "success": True,
                "content": content,
                "response_time": response_time,
                "token_count": usage.get("total_tokens"),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "model_used": data.get("model", self.model),
                "retry_count": retry_count,
            }

        except (json.JSONDecodeError, KeyError) as e:
            return {
                "success": False,
                "content": "",
                "error": f"Failed to parse response: {str(e)}",
                "response_time": response_time,
                "retry_count": retry_count,
            }

    def _process_error_response(
        self,
        response: requests.Response,
        response_time: float,
        retry_count: int
    ) -> Dict[str, Any]:
        """Process error response"""

        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
        except Exception as e:
            # Fail-fast: JSON parsing must succeed for proper error handling
            raise RuntimeError(f"Failed to parse API error response: {e}")

        return {
            "success": False,
            "content": "",
            "error": f"API error ({response.status_code}): {error_msg}",
            "response_time": response_time,
            "retry_count": retry_count,
        }

    def get_timeout_statistics(self) -> Dict[str, Any]:
        """Get comprehensive timeout and performance statistics"""

        total_requests = self.stats["total_requests"]
        if total_requests == 0:
            return {"error": "No requests made yet"}

        success_rate = (self.stats["successful_requests"] / total_requests) * 100
        timeout_rate = (self.stats["timeout_errors"] / total_requests) * 100
        connection_error_rate = (self.stats["connection_errors"] / total_requests) * 100

        avg_response_time = self.stats["total_response_time"] / total_requests
        avg_retries = sum(self.stats["retry_counts"]) / len(self.stats["retry_counts"]) if self.stats["retry_counts"] else 0

        return {
            "total_requests": total_requests,
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "timeout_errors": self.stats["timeout_errors"],
            "connection_errors": self.stats["connection_errors"],
            "success_rate": round(success_rate, 2),
            "timeout_rate": round(timeout_rate, 2),
            "connection_error_rate": round(connection_error_rate, 2),
            "average_response_time": round(avg_response_time, 2),
            "average_retries": round(avg_retries, 2),
            "total_tokens": self.stats["total_tokens"],
            "timeout_config": {
                "connect_timeout": self.timeout_config.connect_timeout,
                "read_timeout": self.timeout_config.read_timeout,
                "total_timeout": self.timeout_config.total_timeout,
                "max_retries": self.timeout_config.max_retries,
                "base_retry_delay": self.timeout_config.base_retry_delay,
            }
        }

    def test_connection_optimized(self) -> Dict[str, Any]:
        """Test connection with optimized timeout handling"""

        start_time = time.time()

        try:
            # Test with shorter timeouts for connection check
            response = self.session.get(
                f"{self.base_url}/models",
                timeout=(5.0, 10.0)  # Shorter timeouts for health check
            )

            response_time = time.time() - start_time

            return {
                "healthy": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "error": None
            }

        except requests.exceptions.Timeout:
            return {
                "healthy": False,
                "status_code": None,
                "response_time": round(time.time() - start_time, 3),
                "error": "Connection timeout"
            }

        except requests.exceptions.ConnectionError:
            return {
                "healthy": False,
                "status_code": None,
                "response_time": round(time.time() - start_time, 3),
                "error": "Connection failed"
            }

        except Exception as e:
            return {
                "healthy": False,
                "status_code": None,
                "response_time": round(time.time() - start_time, 3),
                "error": str(e)
            }


def create_enhanced_client(provider: str = "deepseek") -> EnhancedAPIClient:
    """Factory function to create enhanced API client for specified provider"""

    from api.key_manager import get_api_key

    # Get API key
    api_key = get_api_key(provider)
    if not api_key:
        raise ValueError(f"No API key found for provider: {provider}")

    # Get provider config
    api_providers = get_api_providers()
    if provider not in api_providers:
        raise ValueError(f"Unknown provider: {provider}")

    config = api_providers[provider]

    # Create enhanced timeout config
    timeout_config = TimeoutConfig(
        connect_timeout=config["timeout_connect"],
        read_timeout=config["timeout_read"],
        max_retries=config["max_retries"],
        base_retry_delay=config["retry_delay"],
    )

    return EnhancedAPIClient(
        api_key=api_key,
        base_url=config["base_url"],
        model=config["model"],
        timeout_config=timeout_config,
    )


# Import API_PROVIDERS from centralized location
try:
    from run import get_api_providers
except ImportError:
    # Fallback for when run module is not available
    def get_api_providers():
        return {
            "deepseek": {
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com",
                "timeout": 30
            }
        }
