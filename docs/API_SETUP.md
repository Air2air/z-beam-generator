# API Provider Setup Guide

## Overview

The Z-Beam system uses a **centralized API configuration architecture** with all provider settings stored in `run.py` as the single source of truth. This ensures consistent configuration management and eliminates duplicate API### Testing Requirements**
- **Connectivity Test**: Must pass for all configured providers
- **Endpoint Validation**: No double-path URLs allowed
- **Model Validation**: All models must be current and supported
- **Timeout Validation**: Response times must be under 10 seconds
- **Terminal Output Analysis**: Must read and analyze terminal output for detailed API error patterns

### **🔍 CRITICAL: Terminal Output Reading for API Diagnostics**

**Requirement**: All API diagnostic procedures MUST include reading terminal output to capture detailed error messages that are not returned in API response objects.

**Why This Matters**:
- API client logs detailed connection attempts, retry patterns, and failure modes to terminal
- Response objects often only contain `success: false` and `error: None`
- Terminal output shows the real failure details (SSL errors, connection timeouts, DNS issues)

**Example API Failure Pattern (Winston API)**:
```
🔌 [API CLIENT] Establishing connection...
🔌 [API CLIENT] Connection failed on attempt 1, retrying in 1.0s...
🔄 [API CLIENT] Retry attempt 1/3 after 1.0s delay
🔌 [API CLIENT] Connection failed on attempt 2, retrying in 2.0s...
🔌 [API CLIENT] Connection error after 4 attempts
❌ [CLIENT MANAGER] winston: Failed - None
```

**Implementation Requirements**:
1. **Always Use get_terminal_output()**: After running API tests, read terminal output using terminal ID
2. **Parse Error Patterns**: Look for connection failure patterns, SSL errors, timeout messages
3. **Document Failure Modes**: Update documentation with actual terminal error messages
4. **Correlation Analysis**: Match terminal errors to incomplete content (like alumina-laser-cleaning.md cutoff)

**Updated Testing Procedure**:
```python
# 1. Run API test and capture terminal ID
terminal_id = run_in_terminal("python3 -c 'from api.client_manager import test_api_connectivity; test_api_connectivity(\"winston\")'")

# 2. Read detailed terminal output
terminal_output = get_terminal_output(terminal_id)

# 3. Analyze error patterns
if "Connection failed" in terminal_output:
    # Document specific connection failure
if "SSL" in terminal_output:
    # Document SSL/TLS issues
if "timeout" in terminal_output:
    # Document timeout patterns
```ider definitions across the codebase.

## Architecture Changes (September 2025)

### Centralized Configuration
- **Single Source**: All API provider configurations are now centralized in `run.py`
- **Consistent Access**: All files use `get_api_providers()` function to access configuration
- **No Duplicates**: Removed all duplicate `API_PROVIDERS` definitions from individual modules

### Fixed API Parameters
- **Conservative Timeouts**: Resolved API timeout issues by using conservative parameters
- **Optimized Token Limits**: Set `max_tokens=4000` and `temperature=0.1` for reliable operation
- **Large Prompt Support**: System now handles large prompts without connection timeouts

## Supported Providers

- **DeepSeek**: Primary provider for most components (optimized parameters)
- **Grok (X.AI)**: Used for content component with reliable grok-3 model
- **Winston AI**: Detection and analysis provider
- **Table Component**: Static/deterministic generation (no API required)

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

# Winston AI Configuration
WINSTON_API_KEY=your_winston_api_key_here
```

### 3. Verify Configuration

Check your environment setup and API connectivity:
```bash
python3 run.py --test-api
```

## Centralized API Provider Configuration

All API provider settings are now centralized in `run.py`:

```python
# Centralized API Configuration (run.py)
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "env_var": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        # Optimized operational parameters
        "max_tokens": 4000,  # Optimized for comprehensive content
        "temperature": 0.7,  # Balanced creativity
        "timeout_connect": 10,  # Connection timeout in seconds
        "timeout_read": 45,  # Read timeout in seconds
        "max_retries": 3,  # Maximum retry attempts
        "retry_delay": 1.0,  # Delay between retries in seconds
    },
    "grok": {
        "name": "Grok",
        "env_var": "GROK_API_KEY",
        "base_url": "https://api.x.ai",  # FIXED: Removed /v1 to prevent double-pathing
        "model": "grok-3",  # UPDATED: Changed from grok-beta to grok-3 (grok-beta deprecated 2025-09-15)
        "max_tokens": 4000,
        "temperature": 0.1,
        "timeout_connect": 10,
        "timeout_read": 45,
        "max_retries": 3,
        "retry_delay": 1.0,
    },
    "winston": {
        "name": "Winston AI Detection",
        "env_var": "WINSTON_API_KEY",
        "base_url": "https://api.gowinston.ai",  # FIXED: Removed /v1 to prevent double-pathing
        "model": "winston-ai-detector",
        "max_tokens": 1000,
        "temperature": 0.1,
        "timeout_connect": 10,
        "timeout_read": 45,
        "max_retries": 3,
        "retry_delay": 1.0,
    }
}

def get_api_providers():
    """Get API provider configurations from centralized location"""
    return API_PROVIDERS
```

### Accessing Configuration

All modules access the centralized configuration using the `get_api_providers()` function:

```python
# Example usage in any module
from run import get_api_providers

def create_client(provider_name):
    api_providers = get_api_providers()
    config = api_providers[provider_name]
    # Use config...
```

## API Client Configuration

### Connection Settings
- **Connection Timeout**: Must be explicitly configured (no defaults)
- **Read Timeout**: Must be explicitly configured (no defaults)
- **Max Retries**: Must be explicitly configured (no defaults)
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
    timeout_connect=10,    # Must be explicitly provided
    timeout_read=30,       # Must be explicitly provided
    max_retries=2,         # Must be explicitly provided
    retry_delay=0.5        # Must be explicitly provided
)
```

### Fail-Fast Configuration
The system now uses strict fail-fast architecture:
- **No Default Values**: All configuration parameters must be explicitly provided
- **Immediate Validation**: Missing environment variables cause immediate failure
- **Clear Error Messages**: Specific error messages guide proper configuration
- **No Silent Fallbacks**: System fails immediately when dependencies are missing

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

### September 2025 Updates - API Configuration Centralization

#### **Major Architecture Changes**
- **Centralized Configuration**: Moved all API provider configurations to `run.py` as single source of truth
- **Eliminated Duplicates**: Removed duplicate `API_PROVIDERS` definitions from 12+ files across the codebase
- **Consistent Access Pattern**: Implemented `get_api_providers()` function for uniform configuration access

#### **Fixed API Timeout Issues**
- **Root Cause**: Aggressive API parameters (max_tokens=2000, temperature=0.9) caused connection timeouts
- **Solution**: Implemented optimized parameters (max_tokens=4000, temperature=0.1) for comprehensive content generation
- **Large Prompt Support**: System now handles large prompts without timeout failures

#### **Files Updated for Centralization**
- `api/config.py` - Updated to use `get_api_providers()`
- `api/client_factory.py` - Updated to use centralized configuration
- `api/client_manager.py` - Updated to use centralized configuration
- `api/enhanced_client.py` - Updated to use centralized configuration
- `api/key_manager.py` - Updated to use centralized configuration
- `cli/api_config.py` - Updated to use centralized configuration
- `cli/component_config.py` - Updated to use centralized configuration
- `cli/__init__.py` - Updated to use centralized configuration
- `config/unified_config.py` - Updated to use centralized configuration
- `utils/config/environment_checker.py` - Updated to use centralized configuration

#### **Added Missing Functions**
- Added `critical_error()` function to `utils/loud_errors.py` for proper error handling
- Enhanced error reporting with comprehensive failure categories

#### **Verified Functionality**
- ✅ API connectivity test: All 3 providers (DeepSeek, Grok, Winston) connect successfully
- ✅ Content generation: Frontmatter generation working for Steel material
- ✅ Data integration: Materials loaded from `data/materials.yaml` (109 materials across 8 categories)
- ✅ Import dependencies: All files correctly import from centralized location

### Historical Performance Fixes
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

## September 2025 Critical Fixes - API Endpoint Configuration

### **🚨 CRITICAL: Double Path Prevention**
**Issue**: API endpoints were configured with `/v1` in base_url, but client code added another `/v1/chat/completions`, creating invalid URLs like `https://api.x.ai/v1/v1/chat/completions`

**Root Cause**: 
- Grok: `"base_url": "https://api.x.ai/v1"` → `https://api.x.ai/v1/v1/chat/completions` ❌
- Winston: `"base_url": "https://api.gowinston.ai/v1"` → `https://api.gowinston.ai/v1/v1/chat/completions` ❌

**Fix Applied**:
- Grok: `"base_url": "https://api.x.ai"` → `https://api.x.ai/v1/chat/completions` ✅
- Winston: `"base_url": "https://api.gowinston.ai"` → `https://api.gowinston.ai/v1/chat/completions` ✅

### **🚨 CRITICAL: Model Deprecation Prevention**
**Issue**: Grok model `grok-beta` was deprecated on 2025-09-15, causing 404 errors

**Root Cause**: Using outdated model name in configuration
**Fix Applied**: Updated from `"model": "grok-beta"` to `"model": "grok-3"`

### **Impact of Fixes**
- ✅ **Immediate Connections**: Response times now 0.57s (Grok) and 3.44s (DeepSeek)
- ✅ **No More Hanging**: Eliminated 785+ second timeouts that were causing system hangs
- ✅ **Reliable Generation**: Text component generation now works consistently
- ✅ **Fail-Fast Behavior**: System fails immediately instead of hanging indefinitely

### **Prevention Measures**
1. **Endpoint Validation**: Always verify base_url doesn't include path components that client code will duplicate
2. **Model Version Monitoring**: Regularly check for deprecated model versions
3. **Connectivity Testing**: Run `python3 run.py --test-api` before deployment
4. **Response Time Monitoring**: Alert if response times exceed 10 seconds

### **Testing Requirements**
- **Connectivity Test**: Must pass for all configured providers
- **Endpoint Validation**: No double-path URLs allowed
- **Model Validation**: All models must be current and supported
- **Timeout Validation**: Response times must be under 10 seconds

## Commands

```bash
# Check environment configuration
python3 run.py --check-env

# Test API connections (CRITICAL - run before any generation)
python3 run.py --test-api

# REQUIRED: Comprehensive API diagnosis with terminal output analysis
python3 scripts/tools/api_terminal_diagnostics.py <provider_name> [content_file]

# Example: Diagnose Winston API with content impact analysis
python3 scripts/tools/api_terminal_diagnostics.py winston content/components/text/alumina-laser-cleaning.md

# Show component configuration
python3 run.py --show-config

# Run comprehensive API tests
python3 test_api_providers.py
```

## CRITICAL: Terminal Output Reading Procedure

**MANDATORY for all API diagnostics**: After running any API test, you MUST read the terminal output to capture detailed error information not available in response objects.

### Step-by-Step Procedure:
1. **Run API test and capture terminal ID**
2. **Use get_terminal_output(terminal_id) to read detailed errors**
3. **Analyze error patterns using the diagnostic tool**
4. **Correlate terminal errors to content generation issues**

### Example Workflow:
```python
# 1. Run API test
terminal_id = run_in_terminal("python3 -c 'from api.client_manager import test_api_connectivity; test_api_connectivity(\"winston\")'")

# 2. MANDATORY: Read terminal output
terminal_output = get_terminal_output(terminal_id)

# 3. Use diagnostic tool for analysis
run_in_terminal(f"python3 scripts/tools/api_terminal_diagnostics.py winston")
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

### Double Path Errors (404)
```
❌ API request failed with status 404: The requested resource was not found
```
**Solution**: Check base_url configuration - remove `/v1` if client adds it automatically

### Model Deprecation Errors (404)
```
❌ API request failed with status 404: The model was deprecated
```
**Solution**: Update model name to current version (e.g., grok-beta → grok-3)

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
- **NEW**: API endpoint validation tests
- **NEW**: Model deprecation monitoring tests
- **NEW**: Response time validation tests
