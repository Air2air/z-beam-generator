"""Logging configuration."""

import logging
from typing import Dict, Any, Optional
import re
import json

class SensitiveFilter(logging.Filter):
    """Filter to redact sensitive information from logs."""
    
    def __init__(self, patterns=None):
        super().__init__()
        self.patterns = patterns or [
            (r'(Bearer\s+)[^\s"]+', r'\1[REDACTED]'),
            (r'("Authorization":\s*"Bearer\s+)[^"]+', r'\1[REDACTED]"'),
            (r'(api[-_]?key[^"]*":\s*")[^"]+', r'\1[REDACTED]"'),
            (r'(password[^"]*":\s*")[^"]+', r'\1[REDACTED]"'),
            (r'(secret[^"]*":\s*")[^"]+', r'\1[REDACTED]"'),
            (r'(token[^"]*":\s*")[^"]+', r'\1[REDACTED]"')
        ]
    
    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for pattern, repl in self.patterns:
                record.msg = re.sub(pattern, repl, record.msg, flags=re.IGNORECASE)
                
            # Special handling for request data objects
            if "Request data:" in record.msg and "{" in record.msg:
                try:
                    # Extract the JSON part after "Request data: "
                    json_start = record.msg.find('{', record.msg.find("Request data:"))
                    if json_start > 0:
                        json_text = record.msg[json_start:]
                        data = json.loads(json_text)
                        
                        # Redact content from messages
                        if "messages" in data and isinstance(data["messages"], list):
                            for msg in data["messages"]:
                                if "content" in msg and len(msg["content"]) > 100:
                                    msg["content"] = msg["content"][:100] + "... [CONTENT TRUNCATED]"
                        
                        # Replace the JSON part with the redacted version
                        record.msg = record.msg[:json_start] + json.dumps(data, indent=2)
                except Exception:
                    # If parsing fails, just continue
                    pass
                
        return True

def setup_logging(level=logging.INFO):
    """Set up logging configuration."""
    # Configure more detailed logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('api_diagnostics.log')  # Also log to file
        ]
    )
    
    # Create logger
    logger = logging.getLogger("z-beam")
    
    # Add sensitive data filter
    sensitive_filter = SensitiveFilter()
    for handler in logging.root.handlers:
        handler.addFilter(sensitive_filter)
    
    # Reduce verbosity of certain loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logger