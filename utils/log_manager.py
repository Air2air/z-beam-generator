import datetime
import json
import logging


class LogManager:
    """Enhanced logging with structured data and context."""
    
    @staticmethod
    def configure():
        """Configure the logging system."""
        # Basic configuration similar to your current setup
        
    @staticmethod
    def log_event(event_name, **kwargs):
        """Log a structured event with context."""
        event_data = {
            "event": event_name,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        logging.info(f"EVENT: {json.dumps(event_data)}")
        
    @staticmethod
    def log_api_call(provider, model, prompt_length, success, duration_ms, **kwargs):
        """Log API call details."""
        LogManager.log_event(
            "api_call",
            provider=provider,
            model=model,
            prompt_length=prompt_length,
            success=success,
            duration_ms=duration_ms,
            **kwargs
        )