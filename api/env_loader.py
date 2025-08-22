"""
Standardized environment variable loader for API clients.
Handles .env file loading and provides consistent API key access.
"""

import os
from pathlib import Path
from typing import Optional, Dict

class EnvLoader:
    """Standardized environment variable loader"""
    
    _loaded = False
    
    @classmethod
    def load_env(cls) -> None:
        """Load environment variables from .env file if available"""
        if cls._loaded:
            return
            
        try:
            from dotenv import load_dotenv
            
            # Look for .env file in project root
            project_root = Path(__file__).parent.parent
            env_file = project_root / '.env'
            
            if env_file.exists():
                load_dotenv(env_file)
                print(f"📁 Loaded environment from {env_file}")
            else:
                # Also check for .env in current working directory
                cwd_env = Path.cwd() / '.env'
                if cwd_env.exists():
                    load_dotenv(cwd_env)
                    print(f"📁 Loaded environment from {cwd_env}")
                    
        except ImportError:
            # dotenv not available, rely on system environment
            pass
        
        cls._loaded = True
    
    @classmethod
    def get_api_key(cls, provider: str, env_key: str) -> Optional[str]:
        """Get API key for a provider from environment"""
        cls.load_env()
        
        api_key = os.getenv(env_key)
        if api_key:
            print(f"🔑 Found API key for {provider}")
        else:
            print(f"⚠️  No API key found for {provider} (looking for {env_key})")
            
        return api_key
    
    @classmethod
    def get_provider_config(cls, provider_config: Dict) -> Dict:
        """Get complete configuration for a provider"""
        cls.load_env()
        
        config = provider_config.copy()
        api_key = cls.get_api_key(
            config['name'], 
            config['env_key']
        )
        
        if api_key:
            config['api_key'] = api_key
            
        return config
    
    @classmethod
    def list_available_keys(cls) -> Dict[str, bool]:
        """List which API keys are available in environment"""
        cls.load_env()
        
        keys_to_check = [
            'DEEPSEEK_API_KEY',
            'GROK_API_KEY',
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY'
        ]
        
        available = {}
        for key in keys_to_check:
            available[key] = bool(os.getenv(key))
            
        return available
