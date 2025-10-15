# API Terminal Diagnostics Requirements

## Overview

This document establishes the **mandatory requirement** for reading terminal output when diagnosing API failures. Terminal output contains crucial error details that are not available in API response objects.

## Critical Finding: September 11, 2025

### Issue Discovery
- **Problem**: Winston API showing `success: false` and `error: None` in response objects
- **Hidden Details**: Terminal output revealed actual connection failures with SSL/TLS errors
- **Impact**: Incomplete content generation (alumina-laser-cleaning.md cuts off mid-sentence)
- **Root Cause**: SSL certificate/hostname verification problems with Winston API

### Example Terminal Error Pattern
```
🔌 [API CLIENT] Establishing connection...
🔌 [API CLIENT] Connection failed on attempt 1, retrying in 1.0s...
🔄 [API CLIENT] Retry attempt 1/3 after 1.0s delay
🚀 [API CLIENT] Starting request to ai-detection
🔌 [API CLIENT] Connection failed on attempt 2, retrying in 2.0s...
🔌 [API CLIENT] Connection failed on attempt 3, retrying in 4.0s...
🔌 [API CLIENT] Connection error after 4 attempts
❌ [CLIENT MANAGER] winston: Failed - None
```

### API Response vs Terminal Reality
**API Response Object**:
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

**Terminal Output (THE TRUTH)**:
```
🔌 [API CLIENT] Connection failed on attempt 1, retrying in 1.0s...
🔌 [API CLIENT] Connection failed on attempt 2, retrying in 2.0s...
🔌 [API CLIENT] Connection failed on attempt 3, retrying in 4.0s...
🔌 [API CLIENT] Connection error after 4 attempts
```

## Mandatory Terminal Reading Requirements

### 1. **API Diagnostic Procedure**
Every API diagnostic MUST include:

```python
# Step 1: Run API test
terminal_id = run_in_terminal("api test command", background=False)

# Step 2: MANDATORY - Read terminal output
terminal_output = get_terminal_output(terminal_id)

# Step 3: Parse error patterns
analyze_api_errors(terminal_output)
```

### 2. **Error Pattern Recognition**
Look for these critical patterns in terminal output:

#### Connection Failures
```
🔌 [API CLIENT] Connection failed on attempt X
🔌 [API CLIENT] Establishing connection...
🔌 [API CLIENT] Connection error after N attempts
```

#### SSL/TLS Issues
```
[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name
SSL certificate verification failed
HTTPSConnectionPool: Max retries exceeded
```

#### Timeout Patterns
```
⏳ [API CLIENT] Timeout: connect=10s, read=30s
❌ Operation timed out after N seconds
ReadTimeoutError
```

#### Retry Attempts
```
🔄 [API CLIENT] Retry attempt X/Y after Z.Zs delay
🔄 [CLIENT MANAGER] Retry attempt X/Y after Z.Zs delay
```

### 3. **Content Generation Impact Analysis**
When API failures occur, check for:

#### Incomplete Content Files
- Files ending mid-sentence (like alumina-laser-cleaning.md)
- Multiple frontmatter sections indicating failed generation attempts
- Mixed author attribution suggesting fallback mechanisms

#### Terminal Correlation
```python
def correlate_api_failure_to_content(terminal_output, content_file):
    """
    Correlate API failure patterns to incomplete content generation
    """
    if "Connection failed" in terminal_output:
        if content_ends_midsentence(content_file):
            return "API connection failure caused content truncation"
    
    if "timeout" in terminal_output:
        if multiple_frontmatter_sections(content_file):
            return "API timeout caused multiple generation attempts"
```

## Implementation Requirements

### 1. **Updated Testing Commands**
All API testing commands must include terminal output reading:

```bash
# OLD (INSUFFICIENT)
python3 run.py --test-api

# NEW (REQUIRED)
python3 -c "
from api.client_manager import test_api_connectivity
import sys

# Test and capture output
result = test_api_connectivity('winston')
print('RESULT:', result)

# MANDATORY: Instructions to read terminal output
print('NEXT STEP: Use get_terminal_output() to read detailed error messages')
print('Terminal output contains the real error details not in response object')
"
```

### 2. **Documentation Updates**
All API-related documentation must include:

- **Terminal Output Reading**: Explicit instructions to read terminal output
- **Error Pattern Examples**: Real terminal error messages with explanations
- **Correlation Methods**: How to connect terminal errors to content generation issues
- **Diagnostic Scripts**: Automated tools that read and parse terminal output

### 3. **Automated Diagnostic Tools**
Create tools that automatically:

```python
def diagnose_api_with_terminal_analysis(provider_name):
    """
    Comprehensive API diagnosis including terminal output analysis
    """
    # 1. Run API test
    terminal_id = run_api_test(provider_name)
    
    # 2. Get API response
    api_result = get_api_result()
    
    # 3. CRITICAL: Read terminal output
    terminal_output = get_terminal_output(terminal_id)
    
    # 4. Parse detailed errors
    connection_errors = parse_connection_errors(terminal_output)
    ssl_errors = parse_ssl_errors(terminal_output)
    timeout_errors = parse_timeout_errors(terminal_output)
    
    # 5. Generate comprehensive diagnosis
    return {
        'api_response': api_result,
        'terminal_analysis': {
            'connection_errors': connection_errors,
            'ssl_errors': ssl_errors,
            'timeout_errors': timeout_errors,
            'retry_patterns': parse_retry_patterns(terminal_output)
        },
        'content_impact': analyze_content_impact(),
        'recommended_fixes': generate_fix_recommendations()
    }
```

## Error Pattern Library

### Winston API SSL Error
**Terminal Pattern**:
```
🔌 [API CLIENT] Establishing connection...
🔌 [API CLIENT] Connection failed on attempt 1, retrying in 1.0s...
HTTPSConnectionPool(host='api.winston.ai', port=443): Max retries exceeded with url: / 
(Caused by SSLError(SSLError(1, '[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name (_ssl.c:1000)')))
```

**Diagnosis**: SSL certificate/hostname verification failure
**Impact**: Complete API failure, content generation truncated
**Fix**: Network configuration or Winston API server-side SSL issue

### DeepSeek Timeout Error
**Terminal Pattern**:
```
⏳ [API CLIENT] Timeout: connect=10s, read=30s
❌ Operation timed out after 30 seconds
ReadTimeoutError: HTTPSConnectionPool(host='api.deepseek.com', port=443): Read timed out. (read timeout=30)
```

**Diagnosis**: API response timeout
**Impact**: Partial content generation, possible retry attempts
**Fix**: Increase timeout or reduce request complexity

## Compliance Requirements

### For All API Diagnostics
1. **MUST read terminal output** using get_terminal_output()
2. **MUST document actual error patterns** found in terminal
3. **MUST correlate terminal errors** to content generation issues
4. **MUST update error pattern library** with new findings

### For Documentation Updates
1. **MUST include terminal output examples** in all API troubleshooting guides
2. **MUST provide terminal reading instructions** in all diagnostic procedures
3. **MUST explain why terminal output is required** (API responses insufficient)

### For Testing Procedures
1. **MUST include terminal analysis** in all API tests
2. **MUST automate terminal output parsing** where possible
3. **MUST maintain error pattern recognition** tools

## Immediate Action Items

1. **Update all API diagnostic procedures** to include terminal output reading
2. **Create automated terminal analysis tools** for common error patterns
3. **Document Winston API SSL failure** as known issue with workarounds
4. **Establish terminal output as primary source** for API error details
5. **Train all developers** on terminal output reading requirements

## Lessons Learned

1. **API Response Objects Are Insufficient**: They often contain `error: None` even when detailed errors exist
2. **Terminal Output Contains Truth**: Real error details (SSL, timeouts, DNS) only appear in terminal logs
3. **Content Impact Is Immediate**: API failures directly cause incomplete content generation
4. **Correlation Is Critical**: Must connect terminal errors to content generation problems
5. **Documentation Must Reflect Reality**: Include actual terminal error messages, not just API response examples

This requirement ensures we never miss critical API error details hidden in terminal output that don't appear in response objects.
