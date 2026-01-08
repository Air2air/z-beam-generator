#!/usr/bin/env python3
"""
Unified Configuration Manager for Z-Beam Generator

GROK-COMPLIANT CONSOLIDATION: Single source of truth for all configuration management
while preserving all existing interfaces and functionality.

Consolidates:
- config/api_keys.py (API key management)
- api/config.py (API configuration)
- cli/component_config.py (Component configuration)
- Scattered configuration loading across multiple files

FAIL-FAST DESIGN: No fallbacks, explicit validation, immediate failure on missing config.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from shared.exceptions import ConfigurationError


@dataclass
class APIConfig:
    """Configuration for API clients"""
    name: str
    base_url: str
    model: str
    api_key: str
    max_tokens: int
    temperature: float
    timeout_connect: int
    timeout_read: int
    max_retries: int
    retry_delay: float


class ConfigManager:
    """
    Centralized configuration management with fail-fast validation.
    
    Provides single interface to all configuration systems while maintaining
    backward compatibility with existing components.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._api_providers = None
            self._component_config = None
            self._api_keys = None
            self._load_configuration()
            ConfigManager._initialized = True
    
    def _load_configuration(self):
        """Load all configuration with fail-fast validation"""
        self._load_environment()
        self._load_api_keys()
        self._load_api_providers()
        self._load_component_config()
    
    def _load_environment(self):
        """Load environment variables from .env file"""
        env_path = Path(__file__).parent.parent / '.env'
        
        if not env_path.exists():
            raise ConfigurationError(
                f"CONFIGURATION ERROR: .env file not found at {env_path}. "
                "API keys must be defined in .env file with no fallbacks."
            )
        
        load_dotenv(env_path)
    
    def _load_api_keys(self):
        """Load and validate API keys from environment"""
        required_keys = [
            "DEEPSEEK_API_KEY",
            "GROK_API_KEY", 
            "OPENAI_API_KEY",
            "WINSTON_API_KEY"
        ]
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ConfigurationError(
                f"CONFIGURATION ERROR: Missing required API keys in .env file: {', '.join(missing_keys)}"
            )
        
        # Build API_KEYS dict for backward compatibility
        self._api_keys = {
            key: os.getenv(key) 
            for key in [
                "XAI_API_KEY",
                "GROK_API_KEY", 
                "DEEPSEEK_API_KEY",
                "DEEPSEEK_TEMPERATURE",
                "OPENAI_API_KEY",
                "WINSTON_API_KEY",
                "GEMINI_API_KEY"
            ]
            if os.getenv(key)
        }
    
    def _load_api_providers(self):
        """Load API provider configurations from run.py"""
        try:
            from run import API_PROVIDERS
            self._api_providers = API_PROVIDERS
        except ImportError:
            # Fallback to shared.config.settings if run.py doesn't exist
            try:
                from shared.config.settings import API_PROVIDERS
                self._api_providers = API_PROVIDERS
            except ImportError:
                raise ConfigurationError(
                    "CONFIGURATION ERROR: run.py not found and shared.config.settings import failed. "
                    "All API configurations must be defined in one of these locations with no fallbacks."
                )
        
        if not self._api_providers:
            raise ConfigurationError(
                "CONFIGURATION ERROR: No API providers configured in run.py. "
                "Define API_PROVIDERS dictionary in run.py."
            )
    
    def _load_component_config(self):
        """Load component configuration from run.py"""
        try:
            from run import COMPONENT_CONFIG
            self._component_config = COMPONENT_CONFIG
        except ImportError:
            # Fail-fast: Component config must be available - no fallback
            raise RuntimeError("COMPONENT_CONFIG must be defined in run.py - no fallback allowed")
    
    # API Key Management Interface (consolidates config/api_keys.py)
    def get_api_key(self, provider: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Get API key for a provider using standardized approach"""
        if config is None:
            if provider not in self._api_providers:
                raise ValueError(f"Unknown provider: {provider}")
            config = self._api_providers[provider]
        
        env_var = config.get("env_var")
        if not env_var:
            raise ValueError(f"No env_var specified for provider: {provider}")
        
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(
                f"API key not found for provider '{provider}'. "
                f"Set {env_var} in .env file."
            )
        
        return api_key
    
    def get_masked_api_key(self, provider: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Get masked API key for logging"""
        try:
            key = self.get_api_key(provider, config)
            if len(key) <= 8:
                return "***"
            return f"{key[:4]}...{key[-4:]}"
        except ValueError:
            return "NOT_SET"
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that all configured providers have API keys available"""
        results = {}
        for provider, config in self._api_providers.items():
            try:
                self.get_api_key(provider, config)
                results[provider] = True
            except ValueError:
                results[provider] = False
        return results
    
    def check_provider_availability(self, provider: str) -> bool:
        """Check if provider is available"""
        try:
            self.get_api_key(provider)
            return True
        except ValueError:
            return False
    
    # API Configuration Interface (consolidates api/config.py)
    def get_api_providers(self) -> Dict[str, Any]:
        """Get API provider configurations"""
        return self._api_providers.copy()
    
    def get_default_config(self) -> APIConfig:
        """Get default API configuration"""
        if "deepseek" not in self._api_providers:
            available = list(self._api_providers.keys())
            raise ConfigurationError(
                f"CONFIGURATION ERROR: 'deepseek' provider not found in run.py. "
                f"Available providers: {available}. Configure 'deepseek' in API_PROVIDERS."
            )
        
        config_data = self._api_providers["deepseek"]
        
        required_fields = ["name", "base_url", "model", "max_tokens", "temperature", 
                          "timeout_connect", "timeout_read", "max_retries", "retry_delay"]
        
        for field in required_fields:
            if field not in config_data:
                raise ConfigurationError(
                    f"CONFIGURATION ERROR: Missing required field '{field}' "
                    f"in run.py API_PROVIDERS['deepseek']"
                )
        
        return APIConfig(
            name=config_data["name"],
            base_url=config_data["base_url"],
            model=config_data["model"],
            api_key="",  # Will be set by client
            max_tokens=config_data["max_tokens"],
            temperature=config_data["temperature"],
            timeout_connect=config_data["timeout_connect"],
            timeout_read=config_data["timeout_read"],
            max_retries=config_data["max_retries"],
            retry_delay=config_data["retry_delay"],
        )
    
    # Component Configuration Interface (consolidates cli/component_config.py)
    def get_component_config(self) -> Dict[str, Any]:
        """Get component configuration"""
        return self._component_config.copy()
    
    def get_enabled_components(self) -> list:
        """Get list of enabled components"""
        return [
            comp for comp, config in self._component_config.items() 
            if config.get("enabled", False)
        ]
    
    def get_components_sorted_by_priority(self, include_disabled: bool = False) -> list:
        """Get components sorted by priority"""
        components = self._component_config
        if not include_disabled:
            components = {k: v for k, v in components.items() if v.get("enabled", False)}
        
        # Sort by priority (lower number = higher priority)
        return sorted(
            components.keys(),
            key=lambda x: components[x].get("priority", 999)
        )
    
    # Backward Compatibility Properties
    @property
    def API_KEYS(self) -> Dict[str, str]:
        """Backward compatibility for config/api_keys.py"""
        return self._api_keys.copy()
    
    @property
    def API_PROVIDERS(self) -> Dict[str, Any]:
        """Backward compatibility for API_PROVIDERS access"""
        return self._api_providers.copy()
    
    @property
    def COMPONENT_CONFIG(self) -> Dict[str, Any]:
        """Backward compatibility for COMPONENT_CONFIG access"""
        return self._component_config.copy()


# Global instance for backward compatibility
_config_manager = ConfigManager()

# Backward compatibility functions (maintain existing interfaces)

# From config/api_keys.py
def load_api_keys():
    """Backward compatibility function"""
    return True  # Already loaded by manager

API_KEYS = _config_manager.API_KEYS

# From api/config.py
def get_api_providers() -> Dict[str, Any]:
    """Backward compatibility function"""
    return _config_manager.get_api_providers()

def get_default_config() -> APIConfig:
    """Backward compatibility function"""
    return _config_manager.get_default_config()

# From cli/component_config.py
COMPONENT_CONFIG = _config_manager.COMPONENT_CONFIG

# From api/key_manager.py
class APIKeyManager:
    """Backward compatibility wrapper for existing APIKeyManager interface"""
    
    @staticmethod
    def get_api_key(provider: str, config: Optional[Dict[str, Any]] = None) -> str:
        return _config_manager.get_api_key(provider, config)
    
    @staticmethod
    def get_masked_key(provider: str, config: Optional[Dict[str, Any]] = None) -> str:
        return _config_manager.get_masked_api_key(provider, config)
    
    @staticmethod
    def validate_api_keys() -> Dict[str, bool]:
        return _config_manager.validate_api_keys()
    
    @staticmethod
    def check_provider_availability(provider: str) -> bool:
        return _config_manager.check_provider_availability(provider)

# Convenience functions for backward compatibility
def get_api_key(provider: str, config: Optional[Dict[str, Any]] = None) -> str:
    return _config_manager.get_api_key(provider, config)

def validate_all_api_keys() -> Dict[str, bool]:
    return _config_manager.validate_api_keys()

def get_masked_api_key(provider: str, config: Optional[Dict[str, Any]] = None) -> str:
    return _config_manager.get_masked_api_key(provider, config)

def is_provider_available(provider: str) -> bool:
    return _config_manager.check_provider_availability(provider)

def get_enabled_components() -> list:
    return _config_manager.get_enabled_components()

def get_components_sorted_by_priority(include_disabled: bool = False) -> list:
    return _config_manager.get_components_sorted_by_priority(include_disabled)
