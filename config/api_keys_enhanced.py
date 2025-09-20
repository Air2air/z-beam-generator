# Configuration Consolidation Adapter for config/api_keys.py
# GROK-COMPLIANT: Preserves all existing functionality while adding consolidation layer

import os
from pathlib import Path
from dotenv import load_dotenv

# Original functionality preserved exactly
def load_api_keys():
    """Load API keys from .env file with fail-fast validation"""
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        raise RuntimeError(
            f"CONFIGURATION ERROR: .env file not found at {env_path}. "
            "API keys must be defined in .env file with no fallbacks."
        )
    
    # Load .env file
    load_dotenv(env_path)
    
    # Define required API keys
    required_keys = [
        "DEEPSEEK_API_KEY",
        "GROK_API_KEY", 
        "OPENAI_API_KEY",
        "WINSTON_API_KEY"
    ]
    
    # Validate that all required keys are present
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        raise RuntimeError(
            f"CONFIGURATION ERROR: Missing required API keys in .env file: {', '.join(missing_keys)}"
        )
    
    print(f"🔑 Successfully loaded {len(required_keys)} API keys from .env file")
    return True

# Load API keys immediately when this module is imported
load_api_keys()

# For backward compatibility, create API_KEYS dict from environment
API_KEYS = {
    key: os.getenv(key) 
    for key in [
        "XAI_API_KEY",
        "GROK_API_KEY", 
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_TEMPERATURE",
        "OPENAI_API_KEY",
        "WINSTON_API_KEY",
        "GEMINI_API_KEY"  # Added from your .env file
    ]
    if os.getenv(key)  # Only include keys that are actually set
}

# CONSOLIDATION LAYER: Enhanced functionality for other config managers
class ConfigurationManager:
    """
    Enhanced configuration management for consolidation purposes.
    Preserves all original api_keys.py functionality while adding unified access.
    """
    
    @staticmethod
    def get_api_key_for_provider(provider: str, env_var: str) -> str:
        """Get API key for a specific provider with fail-fast validation"""
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(
                f"API key not found for provider '{provider}'. "
                f"Set {env_var} in .env file."
            )
        return api_key
    
    @staticmethod
    def get_masked_api_key(env_var: str) -> str:
        """Get masked API key for logging"""
        api_key = os.getenv(env_var)
        if not api_key:
            return "NOT_SET"
        if len(api_key) <= 8:
            return "***"
        return f"{api_key[:4]}...{api_key[-4:]}"
    
    @staticmethod
    def validate_provider_key(env_var: str) -> bool:
        """Validate that a specific provider key is available"""
        return bool(os.getenv(env_var))
    
    @staticmethod
    def get_all_available_keys() -> dict:
        """Get all available API keys (for backward compatibility)"""
        return API_KEYS.copy()

# Backward compatibility exports (preserve existing interface)
__all__ = ['load_api_keys', 'API_KEYS', 'ConfigurationManager']
