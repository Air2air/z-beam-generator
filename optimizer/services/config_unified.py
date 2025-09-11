#!/usr/bin/env python3
"""
Unified Configuration System for Z-Beam Optimizer

Consolidates all configuration patterns into a single, consistent system.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from .errors import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfiguration:
    """Configuration for a service."""
    name: str
    version: str = "1.0.0"
    enabled: bool = True
    settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
        self.validate()

    def get_setting(self, key: str, default=None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self.settings[key] = value

    def validate(self) -> bool:
        """Validate the configuration."""
        if not self.name or not self.name.strip():
            raise ValidationError("Service name is required and cannot be empty")
        return True


class UnifiedConfig:
    """
    Unified configuration system that consolidates all optimizer configuration patterns.

    This replaces multiple configuration classes with a single, consistent approach.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        search_paths = [
            Path.cwd() / "config" / "optimizer.yaml",
            Path.cwd() / "config" / "optimizer.json",
            Path.cwd() / "optimizer.yaml",
            Path.cwd() / "optimizer.json",
        ]

        for path in search_paths:
            if path.exists():
                return str(path)

        return None

    def _load_config(self) -> None:
        """Load configuration from file and environment."""
        # Start with centralized configuration from run.py
        try:
            from run import OPTIMIZER_CONFIG
            self._config = OPTIMIZER_CONFIG.copy()
            logger.info("Loaded centralized optimizer configuration from run.py")
        except ImportError:
            logger.warning("Could not import OPTIMIZER_CONFIG from run.py, using defaults")
            self._config = self._get_default_config()

        # Load from file if available (overrides centralized config)
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith('.yaml'):
                        file_config = yaml.safe_load(f) or {}
                    elif self.config_path.endswith('.json'):
                        import json
                        file_config = json.load(f)
                # Merge file config with centralized config
                self._merge_configs(self._config, file_config)
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when centralized config is not available."""
        return {
            "ai_detection_service": {
                "enabled": True,
                "version": "1.0.0",
                "settings": {
                    "target_score": 70.0,
                    "max_iterations": 5,
                    "improvement_threshold": 3.0,
                    "cache_ttl_hours": 1,
                    "max_workers": 4,
                    "detection_threshold": 0.7,
                    "confidence_threshold": 0.8,
                    "allow_mocks_for_testing": False,
                }
            },
            "iterative_workflow_service": {
                "enabled": True,
                "version": "1.0.0",
                "settings": {
                    "max_iterations": 10,
                    "quality_threshold": 0.9,
                    "time_limit_seconds": 300,
                    "convergence_threshold": 0.01,
                }
            },
            "optimization": {
                "target_score": 75.0,
                "max_iterations": 5,
                "improvement_threshold": 3.0,
                "time_limit_seconds": None,
            },
            "logging": {
                "level": "INFO",
            },
            "test_mode": False,
        }

    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> None:
        """Merge override configuration into base configuration."""
        for key, value in override_config.items():
            if isinstance(value, dict) and key in base_config and isinstance(base_config[key], dict):
                self._merge_configs(base_config[key], value)
            else:
                base_config[key] = value

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        env_mappings = {
            'AI_DETECTION_TARGET_SCORE': 'ai_detection_service.settings.target_score',
            'AI_DETECTION_MAX_ITERATIONS': 'ai_detection_service.settings.max_iterations',
            'AI_DETECTION_CACHE_TTL': 'ai_detection_service.settings.cache_ttl_hours',
            'WORKFLOW_MAX_ITERATIONS': 'iterative_workflow_service.settings.max_iterations',
            'WORKFLOW_TIME_LIMIT': 'iterative_workflow_service.settings.time_limit_seconds',
            'WORKFLOW_QUALITY_THRESHOLD': 'iterative_workflow_service.settings.quality_threshold',
            'OPTIMIZER_LOG_LEVEL': 'logging.level',
            'TEST_MODE': 'test_mode',
        }

        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                value = self._parse_env_value(os.environ[env_var])
                self.set_nested_value(config_path, value)

    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Parse environment variable value to appropriate type."""
        # Boolean values
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False

        # Numeric values
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # String values
        return value

    def get_nested_value(self, path: str, default=None) -> Any:
        """Get a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config

        try:
            for key in keys:
                if isinstance(current, dict):
                    current = current[key]
                else:
                    return default
            return current
        except (KeyError, TypeError):
            return default

    def set_nested_value(self, path: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config

        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def get_service_config(self, service_name: str) -> ServiceConfiguration:
        """Get configuration for a specific service."""
        service_config = self.get_nested_value(service_name, {})

        return ServiceConfiguration(
            name=service_name,
            version=service_config.get('version', '1.0.0'),
            enabled=service_config.get('enabled', True),
            settings=service_config.get('settings', {})
        )

    def get_ai_detection_config(self) -> ServiceConfiguration:
        """Get AI detection service configuration."""
        return self.get_service_config('ai_detection_service')

    def get_workflow_config(self) -> ServiceConfiguration:
        """Get iterative workflow service configuration."""
        return self.get_service_config('iterative_workflow_service')

    def get_optimization_config(self) -> Dict[str, Any]:
        """Get optimization-specific configuration."""
        return {
            'target_score': self.get_nested_value('optimization.target_score', 75.0),
            'max_iterations': self.get_nested_value('optimization.max_iterations', 5),
            'improvement_threshold': self.get_nested_value('optimization.improvement_threshold', 3.0),
            'time_limit_seconds': self.get_nested_value('optimization.time_limit_seconds'),
        }

    def get_text_optimization_config(self) -> Dict[str, Any]:
        """Get text optimization configuration."""
        return self.get_nested_value('text_optimization', {})

    def is_test_mode(self) -> bool:
        """Check if running in test mode."""
        return self.get_nested_value('test_mode', False) or \
               os.getenv('TEST_MODE', '').lower() in ('true', '1', 'yes') or \
               'pytest' in os.getenv('_', '').lower()

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'level': self.get_nested_value('logging.level', 'INFO'),
            'format': self.get_nested_value('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        }

    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        save_path = path or self.config_path
        if not save_path:
            save_path = "config/optimizer.yaml"

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(save_path, 'w') as f:
                if save_path.endswith('.yaml'):
                    yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
                elif save_path.endswith('.json'):
                    import json
                    json.dump(self._config, f, indent=2)
            logger.info(f"Saved configuration to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {save_path}: {e}")

    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")

    def get_all_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        return self._config.copy()

    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration."""
        issues = []

        # Check required services
        required_services = ['ai_detection_service', 'iterative_workflow_service']
        for service in required_services:
            if not self.get_nested_value(service):
                issues.append(f"Missing configuration for service: {service}")

        # Validate AI detection settings
        ai_config = self.get_nested_value('ai_detection_service.settings', {})
        if ai_config.get('target_score', 0) not in range(0, 101):
            issues.append("AI detection target_score must be between 0 and 100")

        # Validate workflow settings
        workflow_config = self.get_nested_value('iterative_workflow_service.settings', {})
        if workflow_config.get('max_iterations', 0) <= 0:
            issues.append("Workflow max_iterations must be greater than 0")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': []  # Could add warnings for suboptimal settings
        }


# Global configuration instance
_config_instance: Optional[UnifiedConfig] = None


def get_config() -> UnifiedConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = UnifiedConfig()
    return _config_instance


def reload_global_config() -> None:
    """Reload the global configuration instance."""
    global _config_instance
    _config_instance = UnifiedConfig()


# Convenience functions for common configurations
def get_ai_detection_service_config() -> ServiceConfiguration:
    """Get AI detection service configuration."""
    return get_config().get_ai_detection_config()


def get_workflow_service_config() -> ServiceConfiguration:
    """Get workflow service configuration."""
    return get_config().get_workflow_config()


def get_optimization_defaults() -> Dict[str, Any]:
    """Get optimization default settings."""
    return get_config().get_optimization_config()


def is_test_environment() -> bool:
    """Check if running in test environment."""
    return get_config().is_test_mode()
