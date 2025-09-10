#!/usr/bin/env python3
"""
API Folder Standards and Best Practices

This document outlines the standardized architecture and best practices
for the Z-Beam Generator API folder. All API-related code must follow
these guidelines to ensure consistency, maintainability, and reliability.

## Architecture Overview

The API folder follows a modular, fail-fast architecture with clear separation
of concerns and standardized patterns for all API interactions.

### Core Components

1. **APIClient** (`client.py`) - Main API client with retry logic and error handling
2. **APIClientFactory** (`client_factory.py`) - Standardized client creation
3. **APIKeyManager** (`key_manager.py`) - Centralized API key management
4. **Configuration** (`config.py`) - Provider configurations and settings
5. **Specialized Clients** (`deepseek.py`) - Provider-specific optimizations

### Key Principles

- **Fail-Fast**: No defaults, no fallbacks - explicit configuration required
- **Standardization**: All providers use identical patterns and interfaces
- **Centralization**: Single source of truth for configuration and keys
- **Modularity**: Clear separation of concerns with minimal coupling

## Usage Patterns

### 1. Creating API Clients

```python
# Recommended: Use factory for consistency
from api import create_api_client
client = create_api_client('deepseek')

# Alternative: Direct factory usage
from api import APIClientFactory
client = APIClientFactory.create_client('deepseek')

# For component-specific clients
from api import get_api_client_for_component
client = get_api_client_for_component('content')
```

### 2. API Key Management

```python
# Always use standardized key manager
from api import get_api_key, validate_all_api_keys, get_masked_api_key

# Get API key for provider
api_key = get_api_key('deepseek')

# Validate all keys
validation = validate_all_api_keys()  # {'deepseek': True, 'grok': True}

# Get masked key for logging
masked = get_masked_api_key('deepseek')  # 'sk-2****0546'
```

### 3. Configuration Access

```python
# Access provider configurations
from api import API_PROVIDERS
deepseek_config = API_PROVIDERS['deepseek']

# Get default config
from api import get_default_config
config = get_default_config()
```

## File Responsibilities

### client.py
- Core API client implementation
- Request/response handling
- Retry logic and error handling
- Session management
- Statistics tracking

### client_factory.py
- Standardized client creation
- Test/mock mode detection
- Configuration validation
- Provider abstraction

### key_manager.py
- Centralized API key loading
- Environment variable abstraction
- Key validation and masking
- Provider availability checking

### config.py
- Provider configurations (API_PROVIDERS)
- Configuration validation
- Default config access

### deepseek.py
- DeepSeek-specific optimizations
- Component-specific prompt engineering
- Specialized content generation

### client_manager.py (Legacy)
- Backward compatibility layer
- Environment validation
- Connectivity testing

### env_loader.py (Deprecated)
- Legacy environment loading
- Issues deprecation warnings
- Maintained for backward compatibility

## Best Practices

### 1. Always Use Standardized Patterns

```python
# ✅ GOOD: Use standardized key manager
from api.key_manager import get_api_key
api_key = get_api_key('deepseek')

# ❌ BAD: Direct environment access
import os
api_key = os.getenv('DEEPSEEK_API_KEY')
```

### 2. Handle Errors Consistently

```python
# ✅ GOOD: Let key manager handle errors
try:
    api_key = get_api_key('deepseek')
except ValueError as e:
    logger.error(f"API key error: {e}")
    raise

# ❌ BAD: Manual error handling
api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    raise ValueError("API key not found")
```

### 3. Use Factory for Client Creation

```python
# ✅ GOOD: Factory ensures consistency
client = create_api_client('deepseek')

# ❌ BAD: Direct instantiation bypasses standardization
from api.client import APIClient
client = APIClient(config=API_PROVIDERS['deepseek'])
```

### 4. Validate Configuration

```python
# ✅ GOOD: Validate before using
from api.client_factory import APIClientFactory
validation = APIClientFactory.validate_configuration()
if not validation['valid']:
    raise ValueError("API configuration invalid")

# ❌ BAD: Assume configuration is correct
client = create_api_client('deepseek')  # May fail unexpectedly
```

## Migration Guide

### From Legacy Code

If you have existing code using old patterns:

1. **Replace direct env access:**
   ```python
   # Old
   api_key = os.getenv('DEEPSEEK_API_KEY')

   # New
   from api import get_api_key
   api_key = get_api_key('deepseek')
   ```

2. **Replace manual client creation:**
   ```python
   # Old
   client = APIClient(config=API_PROVIDERS['deepseek'])

   # New
   from api import create_api_client
   client = create_api_client('deepseek')
   ```

3. **Replace env_loader usage:**
   ```python
   # Old
   from api.env_loader import EnvLoader
   EnvLoader.load_env()

   # New
   # No longer needed - key manager handles automatically
   ```

## Testing Guidelines

### Unit Tests
- Mock APIKeyManager for key loading tests
- Use APIClientFactory for client creation tests
- Test error conditions and edge cases

### Integration Tests
- Use real API clients with test keys
- Validate end-to-end functionality
- Test configuration validation

### Best Practices for Tests
```python
def test_api_client_creation():
    # Use factory for consistent test setup
    client = create_api_client('deepseek', use_mock=True)
    assert client is not None

def test_key_validation():
    # Test key validation logic
    validation = validate_all_api_keys()
    assert 'deepseek' in validation
```

## Error Handling

### Standardized Error Types
- `ValueError`: Configuration or key errors
- `RuntimeError`: Connection or API errors
- `Exception`: Unexpected errors

### Logging Standards
- Use emoji prefixes for visual consistency
- Include context in error messages
- Log at appropriate levels (INFO, WARNING, ERROR)

## Performance Considerations

### Connection Management
- Reuse APIClient instances when possible
- Configure appropriate timeouts
- Use connection pooling

### Key Loading
- Keys are cached after first load
- Environment validation is efficient
- Minimal overhead for key access

## Security Best Practices

### API Key Handling
- Never log full API keys
- Use masked versions for debugging
- Validate key format when possible
- Rotate keys regularly

### Configuration Security
- Store keys in environment variables
- Use secure key management systems
- Validate configuration on startup
- Fail fast on security issues

## Maintenance Guidelines

### Adding New Providers
1. Add configuration to `API_PROVIDERS` in `config.py`
2. Test key loading with `get_api_key()`
3. Add provider-specific client if needed
4. Update validation functions
5. Add tests for new provider

### Updating Existing Providers
1. Update configuration in `API_PROVIDERS`
2. Test backward compatibility
3. Update documentation
4. Run full test suite

### Deprecating Features
1. Add deprecation warnings
2. Update documentation
3. Provide migration path
4. Remove in future major version

## Compliance and Standards

### Code Style
- Follow PEP 8 standards
- Use type hints consistently
- Include comprehensive docstrings
- Use descriptive variable names

### Documentation
- Update this document for changes
- Include examples in docstrings
- Document breaking changes
- Maintain changelog

### Version Compatibility
- Maintain backward compatibility when possible
- Use semantic versioning
- Document migration paths
- Test against multiple Python versions
"""
