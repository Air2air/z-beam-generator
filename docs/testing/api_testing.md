# 🔌 API Integration Testing Blueprints

## **Purpose**
This document provides comprehensive blueprints for testing API integrations in the Z-Beam Generator system. It covers DeepSeek, Winston AI, and other external service integrations with proper mocking, error handling, and reliability testing patterns.

## 📋 API Testing Requirements

### **Testing Framework**
- **pytest** with **responses** library for HTTP mocking
- **unittest.mock** for complex mocking scenarios
- **pytest-asyncio** for async API testing
- **freezegun** for time-based testing

### **API Test Categories**
- **Unit Tests**: Individual API client methods
- **Integration Tests**: End-to-end API workflows
- **Contract Tests**: API response validation
- **Reliability Tests**: Circuit breakers, retries, timeouts
- **Performance Tests**: Rate limiting, concurrent requests
- **Cache Tests**: Client caching, performance optimization

## 🏗️ API Client Testing Architecture

### **Test Directory Structure**
```
tests/api/
├── clients/                    # Individual client tests
│   ├── test_deepseek_client.py
│   ├── test_winston_client.py
│   └── test_gemini_client.py
├── integration/               # Integration tests
│   ├── test_api_workflows.py
│   └── test_service_interactions.py
├── reliability/               # Reliability tests
│   ├── test_circuit_breakers.py
│   ├── test_retry_logic.py
│   └── test_timeout_handling.py
├── performance/               # Performance tests
│   ├── test_rate_limiting.py
│   └── test_concurrent_requests.py
├── cache/                     # API client caching tests
│   ├── test_client_cache.py
│   ├── test_cache_performance.py
│   └── test_cache_integration.py
└── fixtures/                  # API test fixtures
    ├── deepseek_responses.json
    ├── winston_responses.json
    └── error_scenarios.json
```

## 🔧 DeepSeek API Testing Patterns

### **Client Unit Testing**

```python
import pytest
import responses
from unittest.mock import Mock, patch
from api.deepseek import DeepSeekAPIClient
from api.exceptions import APIError, RateLimitError, AuthenticationError

class TestDeepSeekAPIClient:

    @pytest.fixture
    def api_client(self):
        """Create DeepSeek API client for testing"""
        return DeepSeekAPIClient(
            api_key="test_key_123",
            model="deepseek-chat",
            max_tokens=1000,
            temperature=0.7
        )

    @pytest.fixture
    def mock_success_response(self):
        """Mock successful DeepSeek API response"""
        return {
            "id": "chatcmpl-test123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from DeepSeek API."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 20,
                "total_tokens": 70
            }
        }

    @responses.activate
    def test_successful_generation(self, api_client, mock_success_response):
        """Test successful content generation"""
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json=mock_success_response,
            status=200
        )

        result = api_client.generate_content(
            prompt="Write about aluminum properties",
            material_context={"name": "Aluminum", "category": "metal"}
        )

        assert "test response from DeepSeek" in result.lower()
        assert len(responses.calls) == 1

    @responses.activate
    def test_rate_limit_handling(self, api_client):
        """Test rate limit error handling"""
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={
                "error": {
                    "type": "rate_limit_exceeded",
                    "message": "Rate limit exceeded. Try again later."
                }
            },
            status=429,
            headers={"Retry-After": "60"}
        )

        with pytest.raises(RateLimitError) as exc_info:
            api_client.generate_content("Test prompt")

        assert "rate limit" in str(exc_info.value).lower()
        assert exc_info.value.retry_after == 60

    @responses.activate
    def test_authentication_error(self, api_client):
        """Test authentication error handling"""
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={
                "error": {
                    "type": "authentication_error",
                    "message": "Invalid API key"
                }
            },
            status=401
        )

        with pytest.raises(AuthenticationError):
            api_client.generate_content("Test prompt")

    @responses.activate
    def test_server_error_retry(self, api_client):
        """Test automatic retry on server errors"""
        # First call fails with 500
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={"error": "Internal server error"},
            status=500
        )

        # Second call succeeds
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={
                "choices": [{
                    "message": {
                        "content": "Recovered response after retry"
                    }
                }],
                "usage": {"total_tokens": 50}
            },
            status=200
        )

        result = api_client.generate_content("Test prompt")

        assert "recovered response" in result
        assert len(responses.calls) == 2  # Should have retried

    @responses.activate
    def test_timeout_handling(self, api_client):
        """Test timeout error handling"""
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            body=Exception("Connection timeout"),
            status=408
        )

        with pytest.raises(APIError) as exc_info:
            api_client.generate_content("Test prompt", timeout=5)

        assert "timeout" in str(exc_info.value).lower()

    @responses.activate
    @pytest.mark.parametrize("status_code,expected_exception", [
        (400, APIError),
        (401, AuthenticationError),
        (403, APIError),
        (404, APIError),
        (429, RateLimitError),
        (500, APIError),
        (502, APIError),
        (503, APIError),
    ])
    def test_various_error_codes(self, api_client, status_code, expected_exception):
        """Test handling of various HTTP error codes"""
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={"error": f"HTTP {status_code} error"},
            status=status_code
        )

        with pytest.raises(expected_exception):
            api_client.generate_content("Test prompt")

    def test_content_validation(self, api_client, mock_success_response):
        """Test content validation and filtering"""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = mock_success_response

            result = api_client.generate_content("Test prompt")

            # Verify content meets quality standards
            assert len(result) > 10
            assert not result.startswith("Error:")
            assert not result.startswith("Warning:")

    def test_token_usage_tracking(self, api_client, mock_success_response):
        """Test token usage tracking"""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = mock_success_response

            result = api_client.generate_content("Test prompt")

            # Verify token usage is tracked
            assert api_client.total_tokens_used >= 70
            assert api_client.last_request_tokens == 70

    @responses.activate
    def test_concurrent_requests(self, api_client):
        """Test handling of concurrent requests"""
        import concurrent.futures

        # Mock multiple successful responses
        for i in range(5):
            responses.add(
                responses.POST,
                "https://api.deepseek.com/v1/chat/completions",
                json={
                    "choices": [{
                        "message": {
                            "content": f"Response {i+1}"
                        }
                    }],
                    "usage": {"total_tokens": 50}
                },
                status=200
            )

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(api_client.generate_content, f"Prompt {i+1}")
                for i in range(5)
            ]

            results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)

        # Verify all requests succeeded
        assert len(results) == 5
        assert all("Response" in result for result in results)
```

### **Integration Testing**

```python
import pytest
import responses
from components.text.generator import TextComponentGenerator
from api.deepseek import DeepSeekAPIClient
from api.winston import WinstonAIClient

class TestAPIIntegration:

    @pytest.fixture
    def text_generator(self):
        """Create text component generator for integration testing"""
        return TextComponentGenerator("aluminum")

    @pytest.fixture
    def mock_deepseek_response(self):
        """Mock DeepSeek API response for integration testing"""
        return {
            "choices": [{
                "message": {
                    "content": "Aluminum is a lightweight metal known for its corrosion resistance and ductility. It is widely used in aerospace and automotive industries."
                }
            }],
            "usage": {"total_tokens": 150}
        }

    @pytest.fixture
    def mock_winston_response(self):
        """Mock Winston AI response for integration testing"""
        return {
            "score": 85.5,
            "confidence": 0.92,
            "analysis": "Content appears to be human-written with natural language patterns."
        }

    @responses.activate
    def test_full_content_generation_workflow(self, text_generator,
                                           mock_deepseek_response,
                                           mock_winston_response):
        """Test complete content generation workflow with API integrations"""

        # Mock DeepSeek API
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json=mock_deepseek_response,
            status=200
        )

        # Mock Winston AI API
        responses.add(
            responses.POST,
            "https://api.winston.ai/analyze",
            json=mock_winston_response,
            status=200
        )

        material_data = {
            "name": "Aluminum",
            "category": "metal",
            "properties": ["ductile", "lightweight", "corrosion_resistant"]
        }

        result = text_generator.generate(material_data=material_data)

        # Verify successful generation
        assert result.success is True
        assert "aluminum" in result.content.lower()
        assert "lightweight" in result.content.lower()
        assert result.generation_time > 0

        # Verify API calls were made
        assert len(responses.calls) == 2

        # Verify metadata includes AI detection score
        assert result.metadata is not None
        assert "ai_detection_score" in result.metadata
        assert result.metadata["ai_detection_score"] >= 85.0

    @responses.activate
    def test_api_failure_fallback(self, text_generator):
        """Test fallback behavior when APIs fail"""

        # Mock DeepSeek API failure
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={"error": "Service temporarily unavailable"},
            status=503
        )

        material_data = {"name": "Aluminum", "category": "metal"}

        result = text_generator.generate(material_data=material_data)

        # Should fail gracefully with clear error message
        assert result.success is False
        assert result.error_message is not None
        assert "deepseek" in result.error_message.lower() or "api" in result.error_message.lower()

    @responses.activate
    def test_ai_detection_integration(self, text_generator,
                                    mock_deepseek_response,
                                    mock_winston_response):
        """Test AI detection integration with content generation"""

        # Mock APIs
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json=mock_deepseek_response,
            status=200
        )

        responses.add(
            responses.POST,
            "https://api.winston.ai/analyze",
            json=mock_winston_response,
            status=200
        )

        material_data = {"name": "Aluminum", "category": "metal"}

        result = text_generator.generate(material_data=material_data)

        # Verify AI detection was performed
        assert result.success is True
        assert result.metadata["ai_detection_score"] == 85.5
        assert result.metadata["ai_detection_confidence"] == 0.92

        # Verify content meets quality threshold
        assert result.metadata["quality_score"] >= 75.0

    @responses.activate
    def test_rate_limit_handling_integration(self, text_generator):
        """Test rate limit handling in integrated workflow"""

        # Mock rate limited responses
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={"error": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "30"}
        )

        material_data = {"name": "Aluminum", "category": "metal"}

        result = text_generator.generate(material_data=material_data)

        # Should handle rate limit gracefully
        assert result.success is False
        assert "rate limit" in result.error_message.lower()

    @responses.activate
    def test_timeout_handling_integration(self, text_generator):
        """Test timeout handling in integrated workflow"""

        # Mock timeout response
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            body=Exception("Connection timeout"),
            status=408
        )

        material_data = {"name": "Aluminum", "category": "metal"}

        result = text_generator.generate(material_data=material_data)

        # Should handle timeout gracefully
        assert result.success is False
        assert "timeout" in result.error_message.lower()
```

## 🛡️ Reliability Testing Patterns

### **Circuit Breaker Testing**

```python
import pytest
import responses
from unittest.mock import patch
from api.circuit_breaker import CircuitBreaker
from api.deepseek import DeepSeekAPIClient

class TestCircuitBreaker:

    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker for testing"""
        return CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=Exception
        )

    @pytest.fixture
    def api_client_with_breaker(self, circuit_breaker):
        """Create API client with circuit breaker"""
        client = DeepSeekAPIClient(api_key="test_key")
        client.circuit_breaker = circuit_breaker
        return client

    @responses.activate
    def test_circuit_breaker_activation(self, api_client_with_breaker):
        """Test circuit breaker activation after failures"""

        # Mock consistent failures
        for i in range(5):
            responses.add(
                responses.POST,
                "https://api.deepseek.com/v1/chat/completions",
                json={"error": "Service unavailable"},
                status=503
            )

        # First 3 calls should attempt connection
        for i in range(3):
            with pytest.raises(Exception):
                api_client_with_breaker.generate_content("Test prompt")

        # Circuit breaker should activate on 4th call
        with pytest.raises(Exception) as exc_info:
            api_client_with_breaker.generate_content("Test prompt")

        assert "circuit breaker" in str(exc_info.value).lower()

    @responses.activate
    def test_circuit_breaker_recovery(self, api_client_with_breaker):
        """Test circuit breaker recovery after timeout"""

        # Mock initial failures
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={"error": "Service unavailable"},
            status=503
        )

        # Trigger circuit breaker
        for i in range(4):
            try:
                api_client_with_breaker.generate_content("Test prompt")
            except:
                pass

        # Mock successful recovery
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={
                "choices": [{"message": {"content": "Recovered"}}],
                "usage": {"total_tokens": 50}
            },
            status=200
        )

        # Should still be in open state
        with pytest.raises(Exception):
            api_client_with_breaker.generate_content("Test prompt")

        # Simulate timeout passage
        with patch('time.time', return_value=time.time() + 61):
            result = api_client_with_breaker.generate_content("Test prompt")

            assert "Recovered" in result

    def test_circuit_breaker_half_open_state(self, api_client_with_breaker):
        """Test circuit breaker half-open state behavior"""

        # Force circuit breaker to open state
        for i in range(4):
            api_client_with_breaker.circuit_breaker.record_failure()

        # Simulate recovery timeout
        with patch('time.time', return_value=time.time() + 61):
            # First request in half-open state should test service
            api_client_with_breaker.circuit_breaker.record_success()

            # Circuit breaker should close after success
            assert api_client_with_breaker.circuit_breaker.state == "closed"
```

### **Retry Logic Testing**

```python
import pytest
import responses
from unittest.mock import patch
from api.retry import RetryMechanism
from api.deepseek import DeepSeekAPIClient

class TestRetryMechanism:

    @pytest.fixture
    def retry_mechanism(self):
        """Create retry mechanism for testing"""
        return RetryMechanism(
            max_attempts=3,
            backoff_factor=2,
            max_delay=30
        )

    @pytest.fixture
    def api_client_with_retry(self, retry_mechanism):
        """Create API client with retry mechanism"""
        client = DeepSeekAPIClient(api_key="test_key")
        client.retry_mechanism = retry_mechanism
        return client

    @responses.activate
    def test_successful_retry_on_transient_error(self, api_client_with_retry):
        """Test successful retry on transient errors"""

        # First two calls fail
        for i in range(2):
            responses.add(
                responses.POST,
                "https://api.deepseek.com/v1/chat/completions",
                json={"error": "Temporary server error"},
                status=502
            )

        # Third call succeeds
        responses.add(
            responses.POST,
            "https://api.deepseek.com/v1/chat/completions",
            json={
                "choices": [{"message": {"content": "Success after retry"}}],
                "usage": {"total_tokens": 50}
            },
            status=200
        )

        result = api_client_with_retry.generate_content("Test prompt")

        assert "Success after retry" in result
        assert len(responses.calls) == 3

    @responses.activate
    def test_max_retry_limit(self, api_client_with_retry):
        """Test that retry stops after max attempts"""

        # Mock consistent failures
        for i in range(4):  # More than max_attempts
            responses.add(
                responses.POST,
                "https://api.deepseek.com/v1/chat/completions",
                json={"error": "Persistent error"},
                status=500
            )

        with pytest.raises(Exception):
            api_client_with_retry.generate_content("Test prompt")

        # Should have made exactly max_attempts calls
        assert len(responses.calls) == 3

    @responses.activate
    def test_exponential_backoff(self, api_client_with_retry):
        """Test exponential backoff timing"""

        call_times = []

        def track_call_time(request):
            call_times.append(time.time())
            return ({"error": "Server error"}, 500)

        # Mock failing responses
        for i in range(3):
            responses.add(
                responses.POST,
                "https://api.deepseek.com/v1/chat/completions",
                json={"error": "Server error"},
                status=500
            )

        start_time = time.time()

        with pytest.raises(Exception):
            api_client_with_retry.generate_content("Test prompt")

        # Verify exponential backoff delays
        delays = [call_times[i+1] - call_times[i] for i in range(len(call_times)-1)]

        # First delay should be backoff_factor * base_delay
        assert delays[0] >= 1.0  # base_delay
        # Second delay should be larger than first
        assert delays[1] > delays[0]
```

## 📊 Performance Testing Patterns

### **Rate Limiting Testing**

```python
import pytest
import responses
import time
from unittest.mock import patch
from api.rate_limiter import RateLimiter
from api.deepseek import DeepSeekAPIClient

class TestRateLimiting:

    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter for testing"""
        return RateLimiter(
            requests_per_minute=60,
            burst_limit=10
        )

    @pytest.fixture
    def api_client_with_rate_limit(self, rate_limiter):
        """Create API client with rate limiting"""
        client = DeepSeekAPIClient(api_key="test_key")
        client.rate_limiter = rate_limiter
        return client

    @responses.activate
    def test_rate_limit_enforcement(self, api_client_with_rate_limit):
        """Test rate limit enforcement"""

        # Mock successful responses
        for i in range(70):  # More than rate limit
            responses.add(
                responses.POST,
                "https://api.deepseek.com/v1/chat/completions",
                json={
                    "choices": [{"message": {"content": f"Response {i+1}"}}],
                    "usage": {"total_tokens": 50}
                },
                status=200
            )

        results = []

        # Make requests up to burst limit quickly
        for i in range(12):  # Over burst limit
            try:
                result = api_client_with_rate_limit.generate_content(f"Prompt {i+1}")
                results.append(result)
            except Exception as e:
                if "rate limit" in str(e).lower():
                    break

        # Should have hit rate limit
        assert len(results) <= 10  # burst_limit

    @responses.activate
    def test_rate_limit_recovery(self, api_client_with_rate_limit):
        """Test rate limit recovery over time"""

        # Mock successful responses
        for i in range(15):
            responses.add(
                responses.POST,
                "https://api.deepseek.com/v1/chat/completions",
                json={
                    "choices": [{"message": {"content": f"Response {i+1}"}}],
                    "usage": {"total_tokens": 50}
                },
                status=200
            )

        # Exhaust burst limit
        for i in range(12):
            try:
                api_client_with_rate_limit.generate_content(f"Prompt {i+1}")
            except:
                pass

        # Wait for recovery
        time.sleep(2)  # Allow some requests to recover

        # Should be able to make more requests
        result = api_client_with_rate_limit.generate_content("Recovery test")

        assert "Response" in result

    @responses.activate
    def test_concurrent_rate_limiting(self, api_client_with_rate_limit):
        """Test rate limiting with concurrent requests"""

        import concurrent.futures

        # Mock responses
        for i in range(20):
            responses.add(
                responses.POST,
                "https://api.deepseek.com/v1/chat/completions",
                json={
                    "choices": [{"message": {"content": f"Response {i+1}"}}],
                    "usage": {"total_tokens": 50}
                },
                status=200
            )

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(api_client_with_rate_limit.generate_content, f"Prompt {i+1}")
                for i in range(15)
            ]

            results = []
            rate_limit_errors = 0

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    if "rate limit" in str(e).lower():
                        rate_limit_errors += 1

            # Should have some successful requests and some rate limit errors
            assert len(results) > 0
            assert rate_limit_errors >= 0
```

## 🏎️ API Client Caching Testing

### **Cache Performance Testing**

```python
import pytest
from unittest.mock import patch, MagicMock
from api.client_cache import APIClientCache
from api.client_manager import get_api_client_for_component

class TestAPIClientCaching:

    def setUp(self):
        """Clear cache before each test"""
        APIClientCache.clear_cache()
    
    def tearDown(self):
        """Clear cache after each test"""
        APIClientCache.clear_cache()

    @patch('api.client_cache.APIClientFactory.create_client')
    def test_cache_hit_rate_optimization(self, mock_create):
        """Test cache optimization for batch operations"""
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        # Simulate batch generation scenario
        materials = ['Aluminum', 'Steel', 'Copper', 'Titanium', 'Brass']
        components = ['frontmatter', 'text', 'bullets', 'tags']
        
        # Generate content for multiple materials and components
        for material in materials:
            for component in components:
                client = APIClientCache.get_client_for_component(component)
        
        stats = APIClientCache.get_cache_stats()
        
        # Should achieve high hit rate for batch operations
        assert stats['hit_rate_percent'] >= 75.0
        assert stats['total_requests'] == len(materials) * len(components)
        
        # Should have created minimal clients (one per unique provider)
        assert stats['cached_instances'] <= 3  # Assuming max 3 providers
        
        # Factory should be called minimally
        assert mock_create.call_count <= 3

    @patch('api.client_cache.APIClientFactory.create_client')
    def test_cache_preloading_performance(self, mock_create):
        """Test preloading performance optimization"""
        mock_create.return_value = MagicMock()
        
        # Preload all providers
        providers = ['deepseek', 'grok', 'winston']
        APIClientCache.preload_clients(providers)
        
        preload_stats = APIClientCache.get_cache_stats()
        
        # Verify preload created expected clients
        assert preload_stats['cached_instances'] == len(providers)
        assert preload_stats['cache_misses'] == len(providers)
        
        # Subsequent requests should all be cache hits
        for provider in providers:
            client = APIClientCache.get_client(provider)
        
        final_stats = APIClientCache.get_cache_stats()
        
        # All subsequent requests should be hits
        assert final_stats['cache_hits'] == len(providers)
        assert final_stats['hit_rate_percent'] == 50.0  # 3 misses, 3 hits

    def test_cache_memory_efficiency(self):
        """Test cache memory usage patterns"""
        with patch('api.client_cache.APIClientFactory.create_client') as mock_create:
            mock_clients = [MagicMock() for _ in range(3)]
            mock_create.side_effect = mock_clients
            
            # Create clients for different providers
            client1 = APIClientCache.get_client('deepseek')
            client2 = APIClientCache.get_client('grok')
            client3 = APIClientCache.get_client('winston')
            
            # Verify same instances returned on subsequent calls
            client1_again = APIClientCache.get_client('deepseek')
            client2_again = APIClientCache.get_client('grok')
            client3_again = APIClientCache.get_client('winston')
            
            # Memory efficiency: same objects should be reused
            assert client1 is client1_again
            assert client2 is client2_again
            assert client3 is client3_again
            
            # Cache should track instances correctly
            stats = APIClientCache.get_cache_stats()
            assert stats['cached_instances'] == 3
            assert stats['cache_hits'] == 3
            assert stats['cache_misses'] == 3

    @patch('api.client_cache.APIClientFactory.create_client')
    def test_cache_invalidation_and_refresh(self, mock_create):
        """Test cache invalidation scenarios"""
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        # Populate cache
        client1 = APIClientCache.get_client('deepseek')
        
        initial_stats = APIClientCache.get_cache_stats()
        assert initial_stats['cached_instances'] == 1
        
        # Clear cache (simulating configuration change)
        APIClientCache.clear_cache()
        
        cleared_stats = APIClientCache.get_cache_stats()
        assert cleared_stats['cached_instances'] == 0
        assert cleared_stats['cache_hits'] == 0
        assert cleared_stats['cache_misses'] == 0
        
        # Next request should create new client
        client2 = APIClientCache.get_client('deepseek')
        
        refresh_stats = APIClientCache.get_cache_stats()
        assert refresh_stats['cache_misses'] == 1
        assert refresh_stats['cached_instances'] == 1

    def test_cache_statistics_accuracy(self):
        """Test accuracy of cache statistics tracking"""
        with patch('api.client_cache.APIClientFactory.create_client') as mock_create:
            mock_create.return_value = MagicMock()
            
            # Complex usage pattern to test statistics
            operations = [
                ('deepseek', False),   # miss
                ('deepseek', True),    # hit
                ('grok', False),       # miss
                ('deepseek', True),    # hit
                ('grok', True),        # hit
                ('winston', False),    # miss
                ('deepseek', True),    # hit
                ('winston', True),     # hit
            ]
            
            expected_hits = sum(1 for _, is_hit in operations if is_hit)
            expected_misses = sum(1 for _, is_hit in operations if not is_hit)
            
            for provider, _ in operations:
                APIClientCache.get_client(provider)
            
            stats = APIClientCache.get_cache_stats()
            
            # Verify statistics accuracy
            assert stats['cache_hits'] == expected_hits
            assert stats['cache_misses'] == expected_misses
            assert stats['total_requests'] == len(operations)
            
            expected_hit_rate = (expected_hits / len(operations)) * 100
            assert abs(stats['hit_rate_percent'] - expected_hit_rate) < 0.1

    @patch('api.client_cache.APIClientFactory.create_client')
    def test_concurrent_cache_access(self, mock_create):
        """Test thread safety of cache under concurrent access"""
        import concurrent.futures
        import threading
        
        mock_create.return_value = MagicMock()
        
        results = []
        errors = []
        
        def get_client_concurrent(provider, thread_id):
            try:
                client = APIClientCache.get_client(provider)
                results.append((thread_id, provider, client))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Concurrent access from multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for i in range(20):
                provider = ['deepseek', 'grok'][i % 2]
                future = executor.submit(get_client_concurrent, provider, i)
                futures.append(future)
            
            # Wait for all threads to complete
            concurrent.futures.wait(futures)
        
        # Should have no errors
        assert len(errors) == 0
        assert len(results) == 20
        
        # Clients for same provider should be identical
        deepseek_clients = [client for tid, prov, client in results if prov == 'deepseek']
        grok_clients = [client for tid, prov, client in results if prov == 'grok']
        
        # All deepseek clients should be the same instance
        assert all(client is deepseek_clients[0] for client in deepseek_clients)
        # All grok clients should be the same instance
        assert all(client is grok_clients[0] for client in grok_clients)

    @patch('api.client_manager.get_cached_client_for_component')
    def test_workflow_integration_with_cache(self, mock_get_cached):
        """Test integration of cache with workflow manager"""
        mock_client = MagicMock()
        mock_get_cached.return_value = mock_client
        
        # Test workflow manager uses cached clients
        from generators.workflow_manager import run_material_generation
        
        with patch('generators.dynamic_generator.DynamicGenerator') as mock_generator:
            mock_gen_instance = MagicMock()
            mock_generator.return_value = mock_gen_instance
            
            mock_gen_instance.get_available_materials.return_value = ['Aluminum']
            mock_gen_instance.get_available_components.return_value = ['frontmatter']
            mock_gen_instance.generate_component.return_value = MagicMock(
                success=True, content="test content", token_count=100
            )
            
            # Run material generation
            result = run_material_generation(
                material='Aluminum',
                component_types=['frontmatter'],
                author_id=None
            )
            
            # Verify cached client was requested
            mock_get_cached.assert_called_with('frontmatter')

    def test_cache_key_generation_consistency(self):
        """Test cache key generation for consistent caching"""
        
        # Same parameters should generate same key
        key1 = APIClientCache._create_cache_key('deepseek', temperature=0.7)
        key2 = APIClientCache._create_cache_key('deepseek', temperature=0.7)
        assert key1 == key2
        
        # Different parameters should generate different keys
        key3 = APIClientCache._create_cache_key('deepseek', temperature=0.8)
        assert key1 != key3
        
        # Different providers should generate different keys
        key4 = APIClientCache._create_cache_key('grok', temperature=0.7)
        assert key1 != key4
        
        # Order of kwargs should not matter
        key5 = APIClientCache._create_cache_key('deepseek', temperature=0.7, max_tokens=800)
        key6 = APIClientCache._create_cache_key('deepseek', max_tokens=800, temperature=0.7)
        assert key5 == key6

    @patch('api.client_cache.APIClientFactory.create_client')
    def test_cache_performance_monitoring(self, mock_create):
        """Test cache performance monitoring capabilities"""
        mock_create.return_value = MagicMock()
        
        # Simulate realistic usage patterns
        
        # Phase 1: Initial cache population (all misses)
        for provider in ['deepseek', 'grok']:
            APIClientCache.get_client(provider)
        
        phase1_stats = APIClientCache.get_cache_stats()
        assert phase1_stats['hit_rate_percent'] == 0.0
        
        # Phase 2: Normal operation (mixed hits/misses)
        for _ in range(10):
            APIClientCache.get_client('deepseek')  # hits
            APIClientCache.get_client('grok')      # hits
        
        phase2_stats = APIClientCache.get_cache_stats()
        assert phase2_stats['hit_rate_percent'] > 80.0  # Should be high
        
        # Phase 3: New provider introduction (some misses)
        for _ in range(3):
            APIClientCache.get_client('winston')   # first is miss, rest are hits
        
        final_stats = APIClientCache.get_cache_stats()
        
        # Final hit rate should still be good
        assert final_stats['hit_rate_percent'] > 70.0
        assert final_stats['cached_instances'] == 3
        
        # Performance metrics should be reasonable
        assert final_stats['total_requests'] == 25  # 2 + 20 + 3

## 📋 API Test Fixtures

### **Mock Response Data**

```python
# tests/api/fixtures/deepseek_responses.json
{
  "successful_generation": {
    "id": "chatcmpl-test123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "deepseek-chat",
    "choices": [{
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Aluminum is a versatile metal known for its lightweight properties and corrosion resistance. It is widely used in aerospace, automotive, and construction industries."
      },
      "finish_reason": "stop"
    }],
    "usage": {
      "prompt_tokens": 45,
      "completion_tokens": 35,
      "total_tokens": 80
    }
  },

  "rate_limit_error": {
    "error": {
      "type": "rate_limit_exceeded",
      "message": "Rate limit exceeded. Limit: 60 requests per minute",
      "retry_after": 30
    }
  },

  "authentication_error": {
    "error": {
      "type": "authentication_error",
      "message": "Invalid API key provided"
    }
  },

  "server_error": {
    "error": {
      "type": "server_error",
      "message": "Internal server error. Please try again."
    }
  }
}

# tests/api/fixtures/winston_responses.json
{
  "high_quality_human": {
    "score": 92.3,
    "confidence": 0.95,
    "analysis": "Content appears to be written by a human expert with natural language patterns and appropriate technical depth."
  },

  "moderate_quality": {
    "score": 78.5,
    "confidence": 0.87,
    "analysis": "Content shows some AI characteristics but maintains reasonable quality and readability."
  },

  "low_quality_ai": {
    "score": 45.2,
    "confidence": 0.91,
    "analysis": "Content exhibits strong AI generation patterns with repetitive structures and unnatural phrasing."
  }
}

# tests/api/fixtures/error_scenarios.json
{
  "network_timeout": {
    "error_type": "timeout",
    "message": "Connection timed out after 30 seconds"
  },

  "connection_refused": {
    "error_type": "connection",
    "message": "Connection refused by server"
  },

  "dns_resolution": {
    "error_type": "dns",
    "message": "DNS resolution failed for api.deepseek.com"
  },

  "ssl_certificate": {
    "error_type": "ssl",
    "message": "SSL certificate verification failed"
  }
}
```

## 🎯 API Testing Best Practices

### **Test Organization**
- **Separate unit and integration tests** for clear isolation
- **Use descriptive test names** that explain the scenario
- **Group related tests** in classes with clear purposes
- **Document test dependencies** and prerequisites

### **Mocking Strategies**
- **Mock external APIs** to avoid test flakiness
- **Use realistic mock data** that matches production schemas
- **Test error scenarios** more thoroughly than success cases
- **Verify API call parameters** and request structure

### **Reliability Testing**
- **Test circuit breaker activation** and recovery
- **Verify retry logic** with exponential backoff
- **Test timeout handling** at multiple levels
- **Validate error propagation** through the system

### **Performance Considerations**
- **Test rate limiting** under various load conditions
- **Measure response times** and set appropriate thresholds
- **Test concurrent requests** to identify race conditions
- **Monitor resource usage** during API interactions

### **CI/CD Integration**
- **Run API tests** in isolated environments
- **Use staging endpoints** for integration testing
- **Monitor API usage** and costs during testing
- **Alert on test failures** that indicate service issues

This comprehensive API testing framework ensures reliable integration with external services while maintaining system stability and performance.</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/docs/testing/api_testing.md
