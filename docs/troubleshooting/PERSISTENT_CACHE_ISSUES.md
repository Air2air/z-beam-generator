# Persistent Cache Troubleshooting Guide

## Overview
The Z-Beam Generator uses a persistent API client cache to improve performance, but this can sometimes cause connection issues when cached sessions become stale.

## Symptoms of Cache Issues

### Connection Failures Despite Working API
- ❌ "Connection failed on attempt X, retrying in Y.Ys..."
- ❌ HTTP 200 responses followed by connection errors
- ❌ Direct API tests work but cached clients fail
- ❌ Generation hangs on "Establishing connection..."

### Cache-Related Error Patterns
```bash
DEBUG:urllib3.connectionpool:https://api.deepseek.com:443 "POST /v1/chat/completions HTTP/1.1" 200 None
🔌 [API CLIENT] Connection failed on attempt 1, retrying in 1.0s...
```

## Root Cause
The persistent cache stores API client sessions that can become stale, causing:
1. **Session Invalidation**: Cached HTTP sessions may timeout or become invalid
2. **Connection Pool Issues**: Cached connection pools may be closed by the server
3. **State Corruption**: Client state may become corrupted between runs

## Solution: Clear the Persistent Cache

### Method 1: Using Python API
```python
from api.persistent_cache import PersistentAPIClientCache
PersistentAPIClientCache.clear_cache()
```

### Method 2: Manual Cache Deletion
```bash
# Find cache directory
python3 -c "
from api.persistent_cache import PersistentAPIClientCache
import tempfile
print(f'Cache location: {tempfile.gettempdir()}/z-beam-cache')
"

# Remove cache files
rm -rf /tmp/z-beam-cache  # or your system's temp directory
```

### Method 3: Use No-Cache Flag
```bash
python3 run.py --material MaterialName --no-persistent-cache
```

## Verification Steps

### 1. Test Direct API Connection
```python
import requests
import os

api_key = os.getenv('DEEPSEEK_API_KEY')
response = requests.post(
    'https://api.deepseek.com/v1/chat/completions',
    json={'model': 'deepseek-chat', 'messages': [{'role': 'user', 'content': 'Hello'}], 'max_tokens': 10},
    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
    timeout=(5, 10)
)
print(f'Direct API Status: {response.status_code}')
```

### 2. Test Client Factory
```python
from api.client_factory import create_api_client
from api.client import GenerationRequest

client = create_api_client('deepseek')
request = GenerationRequest(prompt='Test', max_tokens=10)
response = client.generate(request)
print(f'Client Factory Result: {response.success}')
```

### 3. Run Generation Test
```bash
python3 run.py --material Alumina --components frontmatter --verbose
```

## Prevention

### Regular Cache Maintenance
```bash
# Add to cron or scheduled task
python3 -c "from api.persistent_cache import PersistentAPIClientCache; PersistentAPIClientCache.clear_cache()"
```

### Monitor Cache Health
```bash
python3 run.py --cache-stats  # Check cache performance
python3 run.py --cache-info   # View cache contents
```

## Configuration Updates Applied

### Fixed Hardcoded Values
- ✅ Updated from 800 → 4000 tokens
- ✅ Updated from 0.7 → 0.1 temperature
- ✅ Removed all hardcoded fallbacks
- ✅ Implemented fail-fast configuration

### API Client Improvements
- ✅ Fixed import order for environment variables
- ✅ Enhanced error handling for cache misses
- ✅ Added verbose logging for connection diagnosis

## Related Issues
- [API Connection Failures](../api/ERROR_HANDLING.md#connection-failures)
- [Configuration Management](../API_SETUP.md)
- [Cache Performance](../../api/cache_adapter.py)

## Last Updated
September 16, 2025 - After resolving persistent cache connection issues
