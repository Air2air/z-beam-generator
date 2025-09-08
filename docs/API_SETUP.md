# API Provider Setup Guide

## Overview

The Z-Beam system uses a standardized API client architecture that supports multiple AI providers with consistent environment variable loading and error handling.

## Supported Providers

- **DeepSeek**: Primary provider for most components
- **Grok (X.AI)**: Used for content and table components
  - **grok-2**: Recommended model, works reliably for all content generation
  - **grok-4**: Advanced reasoning model, currently produces reasoning tokens without completion output (not recommended for content generation)

## Environment Setup

### 1. Create Environment File

Copy the example environment file:
```bash
cp .env.example .env
```

### 2. Add API Keys

Edit `.env` and add your API keys:
```bash
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Grok (X.AI) API Configuration
GROK_API_KEY=your_grok_api_key_here
```

### 3. Verify Configuration

Check your environment setup:
```bash
python3 run.py --check-env
```

## API Provider Configuration

The system automatically routes components to appropriate providers:

```python
# Component → Provider Routing
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "env_key": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat"
    },
    "grok": {
        "name": "Grok (X.AI)",
        "env_key": "GROK_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "model": "grok-4"
    }
}
```

## API Client Configuration

### Connection Settings
- **Connection Timeout**: 10 seconds
- **Read Timeout**: 30 seconds (optimized for faster failure detection)
- **Max Retries**: 2 attempts (application-level retry logic)
- **Connection Pool**: 1 connection (prevents concurrent request conflicts)

### Session Management
The API client uses optimized session configuration to prevent concurrent request issues:
- HTTP-level retries disabled (handled by application logic)
- Single connection pool to ensure sequential processing
- Proper connection reuse for efficiency

## Performance Optimizations

### Timeout Configuration
```python
APIConfig(
    timeout_connect=10,    # Fast connection establishment
    timeout_read=30,       # Reasonable response timeout
    max_retries=2,         # Limited retry attempts
    retry_delay=0.5        # Quick retry delay
)
```

### Connection Pooling
- Single connection prevents concurrent request conflicts
- Session reuse improves performance
- Automatic connection cleanup

## Standardized Features

### Environment Loading
- Automatic `.env` file detection and loading
- Fallback to system environment variables
- Clear error messages for missing keys

### Error Handling
- Provider-specific error messages
- Graceful degradation when keys are missing
- Comprehensive connection testing

### Testing
- Isolated API client tests for each provider
- Mock client support for development
- Connection verification tools
- Performance and timeout validation tests

## Recent Performance Improvements

### September 2025 Updates
- **Fixed Concurrent Request Issues**: Resolved hanging generation caused by HTTP-level retries interfering with application retry logic
- **Optimized Connection Pooling**: Reduced connection pool to single connection to prevent concurrent request conflicts
- **Improved Timeout Handling**: Reduced read timeout from 60s to 30s for faster failure detection
- **Enhanced Session Management**: Disabled HTTP-level retries, relying on application-level retry logic for better control

### Key Changes
1. **HTTPAdapter Configuration**:
   - `max_retries=0` (disabled HTTP-level retries)
   - `pool_connections=1` (single connection)
   - `pool_maxsize=1` (prevent concurrent requests)

2. **Timeout Optimization**:
   - Connection timeout: 10 seconds
   - Read timeout: 30 seconds (down from 60)
   - Retry delay: 0.5 seconds

3. **Error Handling**:
   - Application-level retry logic with proper delays
   - Sequential request processing
   - Better timeout error messages

These changes ensure reliable, sequential API request processing without hanging or concurrent request conflicts.

## Commands

```bash
# Check environment configuration
python3 run.py --check-env

# Test API connections
python3 run.py --test-api

# Show component configuration
python3 run.py --show-config

# Run comprehensive API tests
python3 test_api_providers.py
```

## Troubleshooting

### Missing API Keys
```
❌ Missing: DeepSeek (DEEPSEEK_API_KEY)
```
**Solution**: Add the API key to your `.env` file

### Connection Errors
```
❌ API connection test failed: Connection error
```
**Solution**: Check internet connection and API key validity

### Import Errors
```
❌ Failed to import API client modules
```
**Solution**: Ensure all dependencies are installed

## Development

### Adding New Providers

1. Add provider configuration to `API_PROVIDERS`
2. Update `COMPONENT_CONFIG` routing
3. Add environment key to `EnvLoader.list_available_keys()`
4. Create tests in `test_api_providers.py`

### Testing

The system includes comprehensive tests:
- Individual provider client tests
- Component routing verification
- Error handling validation
- Mock client functionality
