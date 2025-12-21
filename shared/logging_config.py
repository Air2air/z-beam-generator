"""
Structured Logging Configuration

Provides JSON-formatted logging for better machine-readability and analysis.
Logs include structured metadata (domain, operation, item_id, etc.) for filtering.

Features:
- JSON formatter for structured logs
- Context manager for operation logging
- Convenience functions for common patterns
- Performance metrics integration
- Development-friendly fallback (plain text)

Usage:
    # Configure logging at startup
    from shared.logging_config import setup_structured_logging
    setup_structured_logging('logs/export.log', level='INFO')
    
    # Basic logging
    logger.info("Processing item", extra={
        'domain': 'materials',
        'item_id': 'aluminum',
        'operation': 'enrich'
    })
    
    # Context manager for operations
    with log_operation('export', domain='materials') as log_ctx:
        log_ctx.info("Starting export")
        # ... do work ...
        log_ctx.info("Export complete", extra={'count': 100})
    
    # Convenience functions
    log_processing('materials', 'aluminum', 'enrichment')
    log_error('materials', error, context={'operation': 'export'})
"""

import json
import logging
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Check if running in development mode
DEV_MODE = '--dev' in sys.argv or '--debug' in sys.argv


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logs.
    
    Converts log records to JSON with structured metadata.
    Falls back to plain text in development mode for readability.
    """
    
    def __init__(self, dev_mode: bool = False):
        """
        Initialize formatter.
        
        Args:
            dev_mode: If True, use plain text format instead of JSON
        """
        super().__init__()
        self.dev_mode = dev_mode
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON or plain text."""
        if self.dev_mode:
            # Plain text for development
            return self._format_plain(record)
        else:
            # JSON for production
            return self._format_json(record)
    
    def _format_json(self, record: logging.LogRecord) -> str:
        """Format as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data)
    
    def _format_plain(self, record: logging.LogRecord) -> str:
        """Format as plain text for development."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        base_msg = f"[{timestamp}] {record.levelname:8s} {record.name}: {record.getMessage()}"
        
        # Add extra fields if present
        extra_fields = []
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                extra_fields.append(f"{key}={value}")
        
        if extra_fields:
            base_msg += f" | {' '.join(extra_fields)}"
        
        # Add exception if present
        if record.exc_info:
            base_msg += "\n" + self.formatException(record.exc_info)
        
        return base_msg


def setup_structured_logging(
    log_file: Optional[str] = None,
    level: str = 'INFO',
    dev_mode: Optional[bool] = None
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_file: Path to log file (optional, defaults to console only)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        dev_mode: Force development mode (plain text logs). If None, auto-detect.
    
    Example:
        # Console only (development)
        setup_structured_logging(level='DEBUG', dev_mode=True)
        
        # File + console (production)
        setup_structured_logging('logs/export.log', level='INFO')
    """
    if dev_mode is None:
        dev_mode = DEV_MODE
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create formatter
    formatter = JSONFormatter(dev_mode=dev_mode)
    
    # Console handler (always present)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(JSONFormatter(dev_mode=False))  # Always JSON for files
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"Logging to file: {log_file}", extra={
            'operation': 'setup',
            'log_file': log_file,
            'level': level,
            'dev_mode': dev_mode
        })


@contextmanager
def log_operation(operation: str, **context):
    """
    Context manager for logging operations with automatic timing.
    
    Args:
        operation: Operation name
        **context: Additional context (domain, item_id, etc.)
    
    Yields:
        Logger instance with context already applied
    
    Example:
        with log_operation('export', domain='materials') as log_ctx:
            log_ctx.info("Processing items")
            # ... work ...
            log_ctx.info("Complete", extra={'count': 100})
    """
    logger = logging.getLogger('operation')
    start_time = datetime.now()
    
    # Log start
    logger.info(f"Starting {operation}", extra={
        'operation': operation,
        'phase': 'start',
        **context
    })
    
    # Create context logger
    class ContextLogger:
        def info(self, msg, **kwargs):
            extra = kwargs.get('extra', {})
            extra.update({'operation': operation, **context})
            kwargs['extra'] = extra
            logger.info(msg, **kwargs)
        
        def warning(self, msg, **kwargs):
            extra = kwargs.get('extra', {})
            extra.update({'operation': operation, **context})
            kwargs['extra'] = extra
            logger.warning(msg, **kwargs)
        
        def error(self, msg, **kwargs):
            extra = kwargs.get('extra', {})
            extra.update({'operation': operation, **context})
            kwargs['extra'] = extra
            logger.error(msg, **kwargs)
    
    ctx_logger = ContextLogger()
    
    try:
        yield ctx_logger
    except Exception as e:
        # Log error with context
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"{operation} failed", exc_info=True, extra={
            'operation': operation,
            'phase': 'error',
            'duration_seconds': duration,
            'error_type': type(e).__name__,
            **context
        })
        raise
    else:
        # Log completion with timing
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"{operation} complete", extra={
            'operation': operation,
            'phase': 'complete',
            'duration_seconds': duration,
            **context
        })


def log_processing(domain: str, item_id: str, stage: str, **extra) -> None:
    """
    Log item processing with structured metadata.
    
    Args:
        domain: Domain name
        item_id: Item identifier
        stage: Processing stage (load, enrich, generate, export)
        **extra: Additional metadata
    
    Example:
        log_processing('materials', 'aluminum', 'enrichment',
                      enricher='BreadcrumbEnricher')
    """
    logger = logging.getLogger('processing')
    logger.info(f"Processing {domain}/{item_id}", extra={
        'domain': domain,
        'item_id': item_id,
        'stage': stage,
        **extra
    })


def log_error(domain: str, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log error with structured metadata.
    
    Args:
        domain: Domain name
        error: Exception that occurred
        context: Additional context (operation, item_id, etc.)
    
    Example:
        try:
            # ... work ...
        except Exception as e:
            log_error('materials', e, context={
                'operation': 'export',
                'item_id': 'aluminum'
            })
    """
    logger = logging.getLogger('error')
    logger.error(f"Error in {domain}", exc_info=True, extra={
        'domain': domain,
        'error_type': type(error).__name__,
        'error_message': str(error),
        **(context or {})
    })


def log_performance(operation: str, duration: float, **metrics) -> None:
    """
    Log performance metrics with structured data.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        **metrics: Additional metrics (items_count, memory_mb, etc.)
    
    Example:
        log_performance('export', 2.5,
                       items_count=100,
                       memory_mb=150.5)
    """
    logger = logging.getLogger('performance')
    logger.info(f"{operation} performance", extra={
        'operation': operation,
        'duration_seconds': duration,
        'metrics_type': 'performance',
        **metrics
    })
