#!/usr/bin/env python3
"""
API Configuration for Z-Beam Generator

Standardized configuration management for DeepSeek API integration.
"""

import os
from dataclasses import dataclass
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the project root
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # If python-dotenv is not available, continue without it
    pass

@dataclass
class APIConfig:
    """Configuration for API client"""
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    max_tokens: int = 3000  # REDUCED FROM 4000 for faster responses
    temperature: float = 0.8  # INCREASED FROM 0.7 for more creative but faster responses
    timeout_connect: int = 10
    timeout_read: int = 60  # REDUCED FROM 120 for faster timeout
    max_retries: int = 2   # REDUCED FROM 3 for faster failure
    retry_delay: float = 0.5  # REDUCED FROM 1.0 for faster retries

class ConfigManager:
    """Manages API configuration with environment variable support"""
    
    @staticmethod
    def load_config() -> APIConfig:
        """Load configuration from environment variables"""
        
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY environment variable not set. "
                "Please set your DeepSeek API key in your environment."
            )
        
        return APIConfig(
            api_key=api_key,
            base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
            model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
            max_tokens=int(os.getenv('DEEPSEEK_MAX_TOKENS', '3000')),  # OPTIMIZED: Reduced from 4000
            temperature=float(os.getenv('DEEPSEEK_TEMPERATURE', '0.8')),  # OPTIMIZED: Increased from 0.7
            timeout_connect=int(os.getenv('DEEPSEEK_TIMEOUT_CONNECT', '10')),
            timeout_read=int(os.getenv('DEEPSEEK_TIMEOUT_READ', '60')),  # OPTIMIZED: Reduced from 120
            max_retries=int(os.getenv('DEEPSEEK_MAX_RETRIES', '2')),  # OPTIMIZED: Reduced from 3
            retry_delay=float(os.getenv('DEEPSEEK_RETRY_DELAY', '0.5'))  # OPTIMIZED: Reduced from 1.0
        )
    
    @staticmethod
    def validate_config(config: APIConfig) -> bool:
        """Validate API configuration"""
        
        if not config.api_key:
            return False
        
        if not config.base_url:
            return False
        
        if config.max_tokens <= 0:
            return False
        
        if not (0.0 <= config.temperature <= 2.0):
            return False
        
        if config.timeout_connect <= 0 or config.timeout_read <= 0:
            return False
        
        return True

# Default configuration instance
def get_default_config() -> APIConfig:
    """Get default API configuration"""
    return ConfigManager.load_config()
