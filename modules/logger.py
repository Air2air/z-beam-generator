# generator/modules/logger.py

import logging
import logging.handlers
import os
import time
from contextlib import contextmanager
from typing import Optional

# Determine the project root dynamically.
_current_dir = os.path.dirname(os.path.abspath(__file__))
_generator_dir = os.path.dirname(_current_dir)
_project_root = os.path.dirname(_generator_dir)

LOG_DIR = os.path.join(_project_root, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# ======================================
# CENTRALIZED LOGGING CONFIGURATION
# ======================================

# Environment-based configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", "INFO").upper()
FILE_LOG_LEVEL = os.getenv("FILE_LOG_LEVEL", "DEBUG").upper()
VERBOSE_API_LOGGING = os.getenv("VERBOSE_API_LOGGING", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
ENABLE_PERFORMANCE_LOGGING = (
    os.getenv("ENABLE_PERFORMANCE_LOGGING", "true").lower() == "true"
)

# Log rotation settings
MAX_LOG_SIZE_MB = int(os.getenv("MAX_LOG_SIZE_MB", "10"))
BACKUP_LOG_COUNT = int(os.getenv("BACKUP_LOG_COUNT", "5"))

# Module-specific log level overrides
MODULE_LOG_LEVELS = {
    "api_client": "INFO",  # Reduce API client verbosity
    "content_generator": "INFO",  # Reduce content generator verbosity
    "page_generator": "INFO",
    "mdx_validator": "INFO",
    # Add more modules as needed
}

# Sensitive data patterns to filter out
SENSITIVE_PATTERNS = [
    "API_KEY",
    "Bearer ",
    "key=",
    "Authorization",
    "password",
    "secret",
    "token",
]

# Add custom sensitive patterns from environment
custom_patterns = os.getenv("CUSTOM_SENSITIVE_PATTERNS", "")
if custom_patterns:
    SENSITIVE_PATTERNS.extend(pattern.strip() for pattern in custom_patterns.split(","))


class SensitiveDataFilter(logging.Filter):
    """Filter to remove sensitive data from logs."""

    def filter(self, record):
        if hasattr(record, "msg"):
            msg = str(record.msg)
            for pattern in SENSITIVE_PATTERNS:
                if pattern in msg:
                    # Replace sensitive data with [REDACTED]
                    import re

                    if pattern == "Bearer ":
                        msg = re.sub(r'Bearer [^\s"]+', "Bearer [REDACTED]", msg)
                    elif pattern == "key=":
                        msg = re.sub(r'key=[^\s&"]+', "key=[REDACTED]", msg)
                    else:
                        # Generic pattern replacement
                        msg = re.sub(
                            f'{pattern}[^\\s"]*',
                            f"{pattern}[REDACTED]",
                            msg,
                            flags=re.IGNORECASE,
                        )
                    record.msg = msg
        return True


class PerformanceTimer:
    """Context manager for performance timing."""

    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        if ENABLE_PERFORMANCE_LOGGING:
            self.logger.debug(f"[PERF] Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time and ENABLE_PERFORMANCE_LOGGING:
            duration = time.time() - self.start_time
            self.logger.info(f"[PERF] {self.operation}: {duration:.3f}s")


def get_logger(name: str, context: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger with centralized settings.

    Args:
        name: Logger name (usually module name)
        context: Optional context for log messages

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(f"generator.{name}")

    # Apply module-specific log level if configured
    module_level = MODULE_LOG_LEVELS.get(name, LOG_LEVEL)
    logger.setLevel(getattr(logging, module_level))

    # Remove all handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler (for terminal output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, CONSOLE_LOG_LEVEL))

    # Console format - clean and concise for terminal
    if ENVIRONMENT == "production":
        # More structured format for production
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Concise format for development
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt="%H:%M:%S"
        )

    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)

    # File Handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024,  # Convert MB to bytes
        backupCount=BACKUP_LOG_COUNT,
    )
    file_handler.setLevel(getattr(logging, FILE_LOG_LEVEL))

    # File format - more detailed with full timestamp
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(file_handler)

    # Add context-aware logging method
    def log_with_context(level, msg, *args, **kwargs):
        prefix = f"[{context}] " if context else ""
        logger.log(level, prefix + msg, *args, **kwargs)

    logger.log_with_context = log_with_context

    # Add API-specific logging methods
    def log_api_request(provider: str, model: str, prompt_length: int, **kwargs):
        """Log API requests in a standardized, non-verbose way."""
        if VERBOSE_API_LOGGING:
            logger.info(
                f"[API] {provider} | {model} | {prompt_length} chars | {kwargs}"
            )
        else:
            logger.info(f"[API] {provider} | {model} | {prompt_length} chars")

    def log_api_response(provider: str, success: bool, error: str = None):
        """Log API responses in a standardized way."""
        if success:
            logger.debug(f"[API] {provider} - Success")
        else:
            logger.warning(f"[API] {provider} - Failed: {error}")

    # Add performance timing context manager
    def time_operation(operation: str):
        """Context manager for timing operations."""
        return PerformanceTimer(logger, operation)

    logger.log_api_request = log_api_request
    logger.log_api_response = log_api_response
    logger.time_operation = time_operation

    return logger


@contextmanager
def log_operation_time(logger: logging.Logger, operation: str):
    """Standalone context manager for timing operations."""
    start_time = time.time()
    if ENABLE_PERFORMANCE_LOGGING:
        logger.debug(f"[PERF] Starting: {operation}")

    try:
        yield
    finally:
        if ENABLE_PERFORMANCE_LOGGING:
            duration = time.time() - start_time
            logger.info(f"[PERF] {operation}: {duration:.3f}s")


# Configuration summary function for debugging
def get_logging_config_summary() -> str:
    """Get a summary of current logging configuration."""
    return f"""
Logging Configuration:
  Environment: {ENVIRONMENT}
  Console Level: {CONSOLE_LOG_LEVEL}
  File Level: {FILE_LOG_LEVEL}
  Log File: {LOG_FILE}
  Log Rotation: {MAX_LOG_SIZE_MB}MB, {BACKUP_LOG_COUNT} backups
  Verbose API: {VERBOSE_API_LOGGING}
  Performance Logging: {ENABLE_PERFORMANCE_LOGGING}
  Module Overrides: {MODULE_LOG_LEVELS}
  Sensitive Patterns: {len(SENSITIVE_PATTERNS)} patterns configured
"""
