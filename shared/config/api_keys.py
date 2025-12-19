# API Keys Configuration
# Loads API keys from .env file using python-dotenv for security
# This file should be safe to commit - no secrets are hardcoded here

import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env file
def load_api_keys():
    """Load API keys from .env file with fail-fast validation"""
    # Now in shared/config/, so go up 2 levels to project root
    env_path = Path(__file__).parent.parent.parent / '.env'
    
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
