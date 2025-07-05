"""
Enhanced configuration provider for the Z-Beam system.
Provides environment-aware configuration with validation and type safety.
"""

import os
import json
from typing import Dict, Any, Optional, List, TypeVar
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging

from domain import (
    GenerationSettings,
    TemperatureSettings,
    ThresholdSettings,
    APISettings,
    Provider,
    DetectionMode
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Environment(Enum):
    """Supported environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "zbeam"
    username: str = ""
    password: str = ""
    connection_timeout: int = 30


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    backend: str = "memory"  # memory, redis, file
    ttl_seconds: int = 3600
    max_size: int = 1000
    file_path: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 10
    backup_count: int = 5


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration."""
    enabled: bool = False
    metrics_port: int = 8080
    health_check_port: int = 8081
    prometheus_enabled: bool = False
    jaeger_enabled: bool = False


@dataclass
class SecurityConfig:
    """Security configuration."""
    api_key_header: str = "X-API-Key"
    rate_limit_per_minute: int = 60
    max_content_length_mb: int = 10
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class ApplicationConfig:
    """Complete application configuration."""
    environment: Environment
    debug: bool
    generation_settings: GenerationSettings
    database: DatabaseConfig
    cache: CacheConfig
    logging: LoggingConfig
    monitoring: MonitoringConfig
    security: SecurityConfig
    
    # API keys (loaded from environment)
    gemini_api_key: str = ""
    deepseek_api_key: str = ""
    anthropic_api_key: str = ""
    xai_api_key: str = ""


class ConfigProvider:
    """Environment-aware configuration provider with validation."""
    
    def __init__(self, environment: Optional[str] = None, config_path: Optional[str] = None):
        self._environment = self._determine_environment(environment)
        self._config_path = config_path or self._get_default_config_path()
        self._config: Optional[ApplicationConfig] = None
        self._loaded = False
    
    def _determine_environment(self, env_override: Optional[str]) -> Environment:
        """Determine the current environment."""
        if env_override:
            try:
                return Environment(env_override.lower())
            except ValueError:
                logger.warning(f"Invalid environment '{env_override}', defaulting to development")
        
        env_var = os.getenv('ZBEAM_ENV', 'development').lower()
        try:
            return Environment(env_var)
        except ValueError:
            logger.warning(f"Invalid environment '{env_var}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        return f"config/{self._environment.value}.json"
    
    def get_config(self) -> ApplicationConfig:
        """Get the complete application configuration."""
        if not self._loaded:
            self._load_config()
        return self._config
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        try:
            # Start with default configuration
            config_data = self._get_default_config()
            
            # Override with file configuration if exists
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r') as f:
                    file_config = json.load(f)
                config_data = self._merge_configs(config_data, file_config)
            
            # Override with environment variables
            env_config = self._load_from_environment()
            config_data = self._merge_configs(config_data, env_config)
            
            # Create typed configuration
            self._config = self._create_application_config(config_data)
            
            # Validate configuration
            self._validate_config()
            
            self._loaded = True
            logger.info(f"Configuration loaded for environment: {self._environment.value}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}") from e
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "environment": self._environment.value,
            "debug": self._environment == Environment.DEVELOPMENT,
            "generation": {
                "temperatures": {
                    "content_generation": 0.6,
                    "ai_detection": 0.3,
                    "human_detection": 0.3,
                    "improvement": 0.7,
                    "summary": 0.4,
                    "metadata": 0.2
                },
                "thresholds": {
                    "ai_threshold": 25.0,
                    "human_threshold": 25.0,
                    "confidence_threshold": 0.8
                },
                "api": {
                    "provider": "gemini",
                    "timeout_seconds": 30,
                    "max_retries": 3,
                    "max_tokens": 3000
                },
                "detection_mode": "comprehensive",
                "max_iterations_per_section": 5,
                "enable_caching": True,
                "enable_logging": True
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "zbeam",
                "connection_timeout": 30
            },
            "cache": {
                "enabled": True,
                "backend": "memory",
                "ttl_seconds": 3600,
                "max_size": 1000
            },
            "logging": {
                "level": "INFO" if self._environment == Environment.PRODUCTION else "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "max_file_size_mb": 10,
                "backup_count": 5
            },
            "monitoring": {
                "enabled": self._environment == Environment.PRODUCTION,
                "metrics_port": 8080,
                "health_check_port": 8081,
                "prometheus_enabled": False,
                "jaeger_enabled": False
            },
            "security": {
                "api_key_header": "X-API-Key",
                "rate_limit_per_minute": 60,
                "max_content_length_mb": 10,
                "allowed_origins": ["*"]
            }
        }
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        
        # API keys
        if gemini_key := os.getenv('GEMINI_API_KEY'):
            env_config['gemini_api_key'] = gemini_key
        if deepseek_key := os.getenv('DEEPSEEK_API_KEY'):
            env_config['deepseek_api_key'] = deepseek_key
        if anthropic_key := os.getenv('ANTHROPIC_API_KEY'):
            env_config['anthropic_api_key'] = anthropic_key
        if xai_key := os.getenv('XAI_API_KEY'):
            env_config['xai_api_key'] = xai_key
        
        # Debug mode
        if debug := os.getenv('ZBEAM_DEBUG'):
            env_config['debug'] = debug.lower() in ('true', '1', 'yes')
        
        # Database configuration
        if db_host := os.getenv('DB_HOST'):
            env_config.setdefault('database', {})['host'] = db_host
        if db_port := os.getenv('DB_PORT'):
            env_config.setdefault('database', {})['port'] = int(db_port)
        if db_name := os.getenv('DB_NAME'):
            env_config.setdefault('database', {})['database'] = db_name
        if db_user := os.getenv('DB_USER'):
            env_config.setdefault('database', {})['username'] = db_user
        if db_pass := os.getenv('DB_PASSWORD'):
            env_config.setdefault('database', {})['password'] = db_pass
        
        # Cache configuration
        if cache_backend := os.getenv('CACHE_BACKEND'):
            env_config.setdefault('cache', {})['backend'] = cache_backend
        if cache_ttl := os.getenv('CACHE_TTL'):
            env_config.setdefault('cache', {})['ttl_seconds'] = int(cache_ttl)
        
        return env_config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_application_config(self, config_data: Dict[str, Any]) -> ApplicationConfig:
        """Create typed application configuration from raw data."""
        # Generation settings
        gen_config = config_data.get('generation', {})
        
        temp_config = gen_config.get('temperatures', {})
        temperature_settings = TemperatureSettings(
            content_generation=temp_config.get('content_generation', 0.6),
            ai_detection=temp_config.get('ai_detection', 0.3),
            human_detection=temp_config.get('human_detection', 0.3),
            improvement=temp_config.get('improvement', 0.7),
            summary=temp_config.get('summary', 0.4),
            metadata=temp_config.get('metadata', 0.2)
        )
        
        threshold_config = gen_config.get('thresholds', {})
        threshold_settings = ThresholdSettings(
            ai_threshold=threshold_config.get('ai_threshold', 25.0),
            human_threshold=threshold_config.get('human_threshold', 25.0),
            confidence_threshold=threshold_config.get('confidence_threshold', 0.8)
        )
        
        api_config = gen_config.get('api', {})
        provider_str = api_config.get('provider', 'gemini')
        provider = Provider(provider_str.lower())
        
        api_settings = APISettings(
            provider=provider,
            model=api_config.get('model'),
            timeout_seconds=api_config.get('timeout_seconds', 30),
            max_retries=api_config.get('max_retries', 3),
            max_tokens=api_config.get('max_tokens', 3000)
        )
        
        detection_mode_str = gen_config.get('detection_mode', 'comprehensive')
        detection_mode = DetectionMode(detection_mode_str.lower())
        
        generation_settings = GenerationSettings(
            temperature_settings=temperature_settings,
            threshold_settings=threshold_settings,
            api_settings=api_settings,
            detection_mode=detection_mode,
            max_iterations_per_section=gen_config.get('max_iterations_per_section', 5),
            enable_caching=gen_config.get('enable_caching', True),
            enable_logging=gen_config.get('enable_logging', True),
            debug_mode=config_data.get('debug', False)
        )
        
        # Other configurations
        db_config = config_data.get('database', {})
        database = DatabaseConfig(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 5432),
            database=db_config.get('database', 'zbeam'),
            username=db_config.get('username', ''),
            password=db_config.get('password', ''),
            connection_timeout=db_config.get('connection_timeout', 30)
        )
        
        cache_config = config_data.get('cache', {})
        cache = CacheConfig(
            enabled=cache_config.get('enabled', True),
            backend=cache_config.get('backend', 'memory'),
            ttl_seconds=cache_config.get('ttl_seconds', 3600),
            max_size=cache_config.get('max_size', 1000),
            file_path=cache_config.get('file_path')
        )
        
        log_config = config_data.get('logging', {})
        logging_cfg = LoggingConfig(
            level=log_config.get('level', 'INFO'),
            format=log_config.get('format', "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=log_config.get('file_path'),
            max_file_size_mb=log_config.get('max_file_size_mb', 10),
            backup_count=log_config.get('backup_count', 5)
        )
        
        mon_config = config_data.get('monitoring', {})
        monitoring = MonitoringConfig(
            enabled=mon_config.get('enabled', False),
            metrics_port=mon_config.get('metrics_port', 8080),
            health_check_port=mon_config.get('health_check_port', 8081),
            prometheus_enabled=mon_config.get('prometheus_enabled', False),
            jaeger_enabled=mon_config.get('jaeger_enabled', False)
        )
        
        sec_config = config_data.get('security', {})
        security = SecurityConfig(
            api_key_header=sec_config.get('api_key_header', 'X-API-Key'),
            rate_limit_per_minute=sec_config.get('rate_limit_per_minute', 60),
            max_content_length_mb=sec_config.get('max_content_length_mb', 10),
            allowed_origins=sec_config.get('allowed_origins', ['*'])
        )
        
        return ApplicationConfig(
            environment=Environment(config_data.get('environment', 'development')),
            debug=config_data.get('debug', False),
            generation_settings=generation_settings,
            database=database,
            cache=cache,
            logging=logging_cfg,
            monitoring=monitoring,
            security=security,
            gemini_api_key=config_data.get('gemini_api_key', ''),
            deepseek_api_key=config_data.get('deepseek_api_key', ''),
            anthropic_api_key=config_data.get('anthropic_api_key', ''),
            xai_api_key=config_data.get('xai_api_key', '')
        )
    
    def _validate_config(self) -> None:
        """Validate the configuration."""
        if not self._config:
            raise ConfigurationError("Configuration not loaded")
        
        # Validate API keys for selected provider
        provider = self._config.generation_settings.api_settings.provider
        
        api_key_map = {
            Provider.GEMINI: self._config.gemini_api_key,
            Provider.DEEPSEEK: self._config.deepseek_api_key,
            Provider.ANTHROPIC: self._config.anthropic_api_key,
            Provider.XAI: self._config.xai_api_key
        }
        
        if not api_key_map.get(provider):
            logger.warning(f"No API key configured for provider: {provider.value}")
        
        # Validate directories exist
        if self._config.cache.backend == 'file' and self._config.cache.file_path:
            cache_dir = Path(self._config.cache.file_path).parent
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        if self._config.logging.file_path:
            log_dir = Path(self._config.logging.file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_api_key(self, provider: Provider) -> str:
        """Get API key for a specific provider."""
        config = self.get_config()
        api_key_map = {
            Provider.GEMINI: config.gemini_api_key,
            Provider.DEEPSEEK: config.deepseek_api_key,
            Provider.ANTHROPIC: config.anthropic_api_key,
            Provider.XAI: config.xai_api_key
        }
        return api_key_map.get(provider, '')
    
    def get_generation_config(self) -> GenerationSettings:
        """Get generation configuration."""
        return self.get_config().generation_settings
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return self.get_config().database
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        return self.get_config().cache
    
    def reload_config(self) -> None:
        """Reload configuration from source."""
        self._loaded = False
        self._config = None
        self._load_config()


# Global configuration provider
_config_provider: Optional[ConfigProvider] = None


def get_config_provider(environment: Optional[str] = None) -> ConfigProvider:
    """Get the global configuration provider."""
    global _config_provider
    if _config_provider is None:
        _config_provider = ConfigProvider(environment)
    return _config_provider


def reset_config_provider() -> None:
    """Reset the global configuration provider (useful for testing)."""
    global _config_provider
    _config_provider = None
