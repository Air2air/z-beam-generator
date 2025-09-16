# API Error Handling & Terminal Diagnostics

**Comprehensive guide to diagnosing and resolving API issues through terminal output analysis**

---

## Overview

This document consolidates all API error handling procedures, emphasizing the **critical requirement** to read terminal output for accurate diagnostics. API response objects often contain insufficient error information (`success: false`, `error: None`), while terminal output reveals the actual failure details.

## 🚨 Critical Discovery: Terminal Output is Essential

### Why Terminal Reading is Mandatory

**API Response Objects are Insufficient:**
```json
{
  "winston": {
    "success": false,
    "response_time": 14.275,
    "token_count": null,
    "error": null  ← USELESS: No actual error information
  }
}
```

**Terminal Output Contains the Truth:**
```
🔌 [API CLIENT] Connection failed on attempt 1, retrying in 1.0s...
🔌 [API CLIENT] Connection failed on attempt 2, retrying in 2.0s...
🔌 [API CLIENT] Connection error after 4 attempts
SSLError: [SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name
```

## Mandatory Terminal Reading Procedure

### Step-by-Step Diagnostic Process

1. **Run API Test**
```bash
terminal_id = run_in_terminal("python3 -c 'from api.client_manager import test_api_connectivity; test_api_connectivity(\"winston\")'")
```

2. **CRITICAL: Read Terminal Output**
```bash
terminal_output = get_terminal_output(terminal_id)
```

3. **Use Diagnostic Tool**
```bash
python3 scripts/tools/api_terminal_diagnostics.py winston content/components/text/alumina-laser-cleaning.md
```

## Common Error Patterns

### 1. Winston API SSL/TLS Errors

**Terminal Pattern:**
```
🔌 [API CLIENT] Establishing connection...
🔌 [API CLIENT] Connection failed on attempt 1, retrying in 1.0s...
HTTPSConnectionPool(host='api.winston.ai', port=443): Max retries exceeded
(Caused by SSLError(SSLError(1, '[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name')))
```

**Root Cause:** SSL certificate/hostname verification failure  
**Impact:** Complete API failure, content generation truncated  
**Solution:** Updated endpoint to `https://api.gowinston.ai`

### 2. Connection Timeout Errors

**Terminal Pattern:**
```
⏳ [API CLIENT] Timeout: connect=10s, read=30s
❌ Operation timed out after 30 seconds
ReadTimeoutError: HTTPSConnectionPool: Read timed out
```

**Root Cause:** API response timeout or network latency  
**Impact:** Partial content generation, retry attempts  
**Solution:** Increase timeout or reduce request complexity

### 3. Authentication Failures

**Terminal Pattern:**
```
🔑 [API CLIENT] Authentication failed
❌ 401 Unauthorized: Invalid API key
```

**Root Cause:** Missing or invalid API key  
**Impact:** Complete API failure  
**Solution:** Verify API key in environment variables

### 4. Rate Limiting

**Terminal Pattern:**
```
🚫 [API CLIENT] Rate limit exceeded
❌ 429 Too Many Requests: Rate limit exceeded
```

**Root Cause:** Too many requests to API provider  
**Impact:** Temporary API failure  
**Solution:** Implement exponential backoff or reduce request frequency

## Error Pattern Recognition Library

### Connection Failures
```
🔌 [API CLIENT] Connection failed on attempt X
🔌 [API CLIENT] Establishing connection...
🔌 [API CLIENT] Connection error after N attempts
```

### SSL/TLS Issues
```
[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name
SSL certificate verification failed
HTTPSConnectionPool: Max retries exceeded
```

### Timeout Patterns
```
⏳ [API CLIENT] Timeout: connect=10s, read=30s
❌ Operation timed out after N seconds
ReadTimeoutError
```

### Retry Attempts
```
🔄 [API CLIENT] Retry attempt X/Y after Z.Zs delay
🔄 [CLIENT MANAGER] Retry attempt X/Y after Z.Zs delay
```

## Content Generation Impact Analysis

### Identifying API Failure Impact

When API failures occur, check content files for:

#### 1. Incomplete Content
- Files ending mid-sentence (e.g., alumina-laser-cleaning.md)
- Content cuts off at exact moment of API failure
- Missing sections or incomplete paragraphs

#### 2. Multiple Frontmatter Sections
- Indicates failed generation attempts
- System tried multiple times but API kept failing
- Creates malformed YAML structure

#### 3. Mixed Author Attribution
- Suggests fallback mechanisms attempted
- Different authors in same file indicate retry with different settings
- Inconsistent metadata generation

### Example Impact Correlation

**Winston SSL Error + Content Truncation:**
```
Terminal: 🔌 [API CLIENT] Connection error after 4 attempts
Content:  "This mechanism, known as 'cold ablation,' vaporizes the contaminant layer before significant" [ENDS ABRUPTLY]
Result:   Direct correlation between SSL failure and content truncation
```

## Diagnostic Tools & Commands

### 1. Comprehensive API Diagnosis
```bash
python3 scripts/tools/api_terminal_diagnostics.py <provider> [content_file]

# Example with content impact analysis
python3 scripts/tools/api_terminal_diagnostics.py winston content/components/text/alumina-laser-cleaning.md
```

### 2. Provider-Specific Testing
```bash
# Test individual providers
python3 -c "from api.client_manager import test_api_connectivity; test_api_connectivity('winston')"
python3 -c "from api.client_manager import test_api_connectivity; test_api_connectivity('deepseek')"
python3 -c "from api.client_manager import test_api_connectivity; test_api_connectivity('grok')"
```

### 3. Environment Validation
```bash
# Check API configuration
python3 run.py --check-env

# Validate API providers
python3 -c "from api.client_manager import validate_api_environment; print(validate_api_environment())"
```

### 4. Network Connectivity Tests
```bash
# Test endpoints directly
python3 -c "
import requests
endpoints = ['https://api.winston.ai', 'https://api.gowinston.ai', 'https://api.deepseek.com']
for endpoint in endpoints:
    try:
        response = requests.get(endpoint, timeout=5)
        print(f'{endpoint}: {response.status_code}')
    except Exception as e:
        print(f'{endpoint}: ERROR - {str(e)[:100]}')
"
```

## Provider-Specific Error Handling

### Winston AI Detection Service

**Current Configuration:**
```python
"winston": {
    "name": "Winston.ai",
    "base_url": "https://api.gowinston.ai",  # FIXED: Updated from api.winston.ai
    "model": "ai-detection",
    "service_type": "ai_detection",
}
```

**Common Issues:**
- SSL certificate problems with original endpoint
- AI detection timeout for large content
- Rate limiting on free tier

**Solutions:**
- Use corrected endpoint: `https://api.gowinston.ai`
- Implement proper timeout handling
- Monitor usage against rate limits

### DeepSeek Content Generation

**Current Configuration:**
```python
"deepseek": {
    "name": "DeepSeek",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "max_tokens": 4000,
    "temperature": 0.1,
}
```

**Common Issues:**
- Large prompt timeout
- Token limit exceeded
- Connection pool exhaustion

**Solutions:**
- Optimized token limits (4000)
- Proper connection pooling
- Request size optimization

### Grok (X.AI) Content Generation

**Current Configuration:**
```python
"grok": {
    "name": "Grok",
    "base_url": "https://api.x.ai",  # FIXED: Removed /v1 to prevent double-path
    "model": "grok-3",  # FIXED: Updated from deprecated grok-beta
    "max_tokens": 800,
    "temperature": 0.7,
}
```

**Common Issues:**
- Model deprecation (grok-beta → grok-3)
- Double-path URLs (/v1/v1/chat/completions)
- Authentication header format

**Solutions:**
- Use current model names
- Correct base URL configuration
- Proper authentication implementation

## Emergency Response Procedures

### 1. Critical API Failure (Production)
```bash
# Immediate diagnosis
python3 scripts/tools/api_terminal_diagnostics.py winston

# Check all providers
python3 run.py --test-api

# Verify environment
python3 run.py --check-env

# Test network connectivity
ping api.winston.ai
ping api.deepseek.com
ping api.x.ai
```

### 2. Content Generation Interruption
```bash
# Identify affected content
find content/components -name "*.md" -exec grep -l "before significant" {} \;

# Check for incomplete files
python3 -c "
import os
for root, dirs, files in os.walk('content/components'):
    for file in files:
        if file.endswith('.md'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
                if content.strip().endswith('before significant'):
                    print(f'INCOMPLETE: {path}')
"

# Regenerate affected content
python3 run.py --material "Alumina" --components "text"
```

### 3. SSL/TLS Certificate Issues
```bash
# Test SSL connectivity
python3 -c "
import ssl
import socket
hostname = 'api.winston.ai'
context = ssl.create_default_context()
with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(f'SSL connection successful: {ssock.version()}')
"

# Check certificate details
openssl s_client -connect api.winston.ai:443 -servername api.winston.ai
```

## Prevention & Monitoring

### 1. Proactive Health Checks
```bash
# Daily health check script
#!/bin/bash
echo "=== API Health Check $(date) ==="
python3 run.py --test-api
python3 scripts/tools/api_terminal_diagnostics.py winston
python3 scripts/tools/api_terminal_diagnostics.py deepseek
python3 scripts/tools/api_terminal_diagnostics.py grok
```

### 2. Content Integrity Monitoring
```bash
# Check for incomplete content
find content/components -name "*.md" -exec python3 -c "
import sys
with open(sys.argv[1], 'r') as f:
    content = f.read()
    if not content.strip().endswith(('.', '!', '?', ':')):
        print(f'POTENTIAL INCOMPLETE: {sys.argv[1]}')
" {} \;
```

### 3. API Usage Monitoring
```bash
# Monitor response times
python3 -c "
from api.client_manager import test_api_connectivity
import time
providers = ['winston', 'deepseek', 'grok']
for provider in providers:
    start = time.time()
    result = test_api_connectivity(provider)
    elapsed = time.time() - start
    status = 'OK' if result[provider]['success'] else 'FAILED'
    print(f'{provider}: {status} ({elapsed:.2f}s)')
"
```

## Related Documentation
- 📋 Overview: [API Providers](PROVIDERS.md)
- 🔧 Setup: [API Configuration](../setup/API_CONFIGURATION.md)
- 🧪 Testing: [API Testing](../testing/API_TESTING.md)
- 🏗️ Architecture: [Client Architecture](CLIENT_ARCHITECTURE.md)
- 🔄 Cache Issues: [Persistent Cache Troubleshooting](../troubleshooting/PERSISTENT_CACHE_ISSUES.md)

---

**⚠️ Remember**: Always read terminal output for accurate API error diagnosis. Response objects alone are insufficient for troubleshooting.
