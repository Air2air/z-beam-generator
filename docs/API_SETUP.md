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
