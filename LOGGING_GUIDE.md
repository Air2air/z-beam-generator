# Z-Beam Centralized Logging Configuration

## Overview

All logging configuration for the Z-Beam project is centralized in `generator/modules/logger.py`. This provides consistent, configurable, and secure logging across all modules.

## Quick Start

### Basic Usage

```python
from generator.modules.logger import get_logger

# Get a logger for your module
logger = get_logger("my_module")

# Standard logging
logger.info("Processing started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Performance Timing

```python
# Time operations automatically
with logger.time_operation("Database query"):
    # Your code here
    result = database.query()

# This logs: [PERF] Database query: 0.245s
```

### API Request Logging

```python
# Standardized API logging (already integrated in api_client.py)
logger.log_api_request("gemini", "gemini-2.5-flash", 1500, temperature=0.7)
logger.log_api_response("gemini", success=True)
```

## Configuration

### Environment Variables

You can configure logging behavior via environment variables or `.env.logging` file:

```bash
# Basic levels
LOG_LEVEL=INFO                    # Global log level
CONSOLE_LOG_LEVEL=INFO           # Terminal output level  
FILE_LOG_LEVEL=DEBUG             # Log file level

# Environment
ENVIRONMENT=development          # development | production
VERBOSE_API_LOGGING=false        # Detailed API request logs
ENABLE_PERFORMANCE_LOGGING=true  # Performance timing logs

# Log rotation
MAX_LOG_SIZE_MB=10              # Max log file size
BACKUP_LOG_COUNT=5              # Number of backup files

# Custom sensitive patterns (comma-separated)
CUSTOM_SENSITIVE_PATTERNS=token,secret_key,private_key
```

### Module-Specific Levels

Edit `generator/modules/logger.py` to set per-module log levels:

```python
MODULE_LOG_LEVELS = {
    "api_client": "INFO",           # Less verbose for API calls
    "content_generator": "INFO",    # Normal verbosity
    "my_new_module": "DEBUG",       # More verbose for debugging
}
```

## Features

### 1. **Centralized Configuration**
- All logging settings in one place
- Environment-based configuration
- Module-specific overrides

### 2. **Security**
- Automatic filtering of sensitive data (API keys, tokens, etc.)
- Configurable sensitive patterns
- Safe for production logging

### 3. **Performance Monitoring**
- Built-in operation timing
- Optional performance logging
- Context managers for easy timing

### 4. **Log Rotation**
- Automatic file rotation when size limit reached
- Configurable backup count
- Prevents disk space issues

### 5. **Structured Output**
- Consistent format across all modules
- Development vs production formats
- File logging with detailed context

## Best Practices

### 1. **Use Appropriate Levels**
```python
logger.debug("Detailed debugging info")     # Development only
logger.info("Normal operation status")      # General information
logger.warning("Recoverable issue")         # Potential problems
logger.error("Error that needs attention")  # Failures
```

### 2. **Performance Timing**
```python
# Time expensive operations
with logger.time_operation("AI content generation"):
    content = generate_content(prompt)

# Time multiple operations
with logger.time_operation("Full page generation"):
    with logger.time_operation("Research phase"):
        research_data = research_material(material)
    with logger.time_operation("Content generation"):
        content = generate_content(research_data)
```

### 3. **Sensitive Data**
```python
# DON'T log sensitive data directly
logger.info(f"API key: {api_key}")  # ❌ Bad

# DO use the built-in filtering (it's automatic)
logger.info(f"Using API key: {api_key}")  # ✅ Good - auto-filtered

# Or be explicit
logger.info("API authentication successful")  # ✅ Best
```

### 4. **Module Naming**
```python
# Use consistent module naming
logger = get_logger("api_client")        # Module name
logger = get_logger("content_generator") # Module name  
logger = get_logger("my_module")         # Your module
```

## Development vs Production

### Development Mode (`ENVIRONMENT=development`)
- Concise console format with timestamps
- More verbose debugging enabled
- Performance logging enabled by default

### Production Mode (`ENVIRONMENT=production`)
- Structured console format with full timestamps
- Reduced console verbosity
- Full file logging maintained
- Security-focused (sensitive data filtering)

## File Locations

- **Configuration**: `generator/modules/logger.py`
- **Log Files**: `logs/app.log` (with rotation)
- **Environment Config**: `.env.logging` (optional)

## Example Commands

```bash
# Test logging configuration
python3 test_logging.py

# Run with different settings
ENVIRONMENT=production python3 test_logging.py
VERBOSE_API_LOGGING=true python3 test_logging.py
ENABLE_PERFORMANCE_LOGGING=false python3 test_logging.py

# Check log files
tail -f logs/app.log
ls -la logs/  # See rotated log files
```

## Troubleshooting

1. **Module not logging**: Check `MODULE_LOG_LEVELS` in `logger.py`
2. **Too verbose**: Lower `CONSOLE_LOG_LEVEL` or module-specific level
3. **Missing logs**: Check `FILE_LOG_LEVEL` and file permissions
4. **Sensitive data leaked**: Add patterns to `SENSITIVE_PATTERNS` or `CUSTOM_SENSITIVE_PATTERNS`

This centralized approach ensures consistent, secure, and maintainable logging across the entire Z-Beam project.
