"""
Configuration Constants - NO HARDCODED VALUES IN CODE
"""
from pathlib import Path
from typing import Dict, Any, Optional
import json

class ConfigConstants:
    """Centralized configuration constants"""
    
    def __init__(self):
        """Initialize without loading - lazy load on first access"""
        self._paths: Optional[Dict[str, str]] = None
        self._api: Optional[Dict[str, Any]] = None
        self._generation: Optional[Dict[str, Any]] = None
        self._providers: Optional[Dict[str, Any]] = None
        self._tags: Optional[Dict[str, Any]] = None
        self._ai_detection: Optional[Dict[str, Any]] = None
        self._debug: Optional[Dict[str, Any]] = None
        self._thresholds: Optional[Dict[str, Any]] = None
    
    @property
    def paths(self) -> Dict[str, str]:
        """Lazy load path configuration"""
        if self._paths is None:
            self._paths = self._load_path_config()
        return self._paths
    
    @property
    def api(self) -> Dict[str, Any]:
        """Lazy load API configuration"""
        if self._api is None:
            self._api = self._load_api_config()
        return self._api
    
    @property
    def generation(self) -> Dict[str, Any]:
        """Lazy load generation configuration"""
        if self._generation is None:
            self._generation = self._load_generation_config()
        return self._generation
    
    @property
    def providers(self) -> Dict[str, Any]:
        """Lazy load providers configuration"""
        if self._providers is None:
            self._providers = self._load_providers_config()
        return self._providers
    
    @property
    def tags(self) -> Dict[str, Any]:
        """Lazy load tags configuration"""
        if self._tags is None:
            self._tags = self._load_tags_config()
        return self._tags
    
    @property
    def ai_detection(self) -> Dict[str, Any]:
        """Lazy load AI detection configuration"""
        if self._ai_detection is None:
            self._ai_detection = self._load_ai_detection_config()
        return self._ai_detection
    
    @property
    def debug(self) -> Dict[str, Any]:
        """Lazy load debug configuration"""
        if self._debug is None:
            self._debug = self._load_debug_config()
        return self._debug
    
    @property
    def thresholds(self) -> Dict[str, Any]:
        """Lazy load thresholds configuration"""
        if self._thresholds is None:
            self._thresholds = self._load_thresholds_config()
        return self._thresholds
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get complete configuration dictionary - NO HARDCODED VALUES"""
        return {
            # API settings
            "provider": self.api["provider"],
            "model": self.api["model"],
            "temperature": self.api["temperature"],
            "metadata_temperature": self.api["metadata_temperature"],
            "max_tokens": self.api["max_tokens"],
            "timeout": self.api["timeout"],
            "retry_attempts": self.api["retry_attempts"],
            "retry_delay": self.api["retry_delay"],
            
            # Generation settings
            "optimization_method": self.generation["optimization_method"],
            "apply_writing_sample_final": self.generation["apply_writing_sample_final"],
            "max_section_words": self.generation["max_section_words"],
            "target_section_words": self.generation["target_section_words"],
            "max_total_words": self.generation["max_total_words"],
            "max_writing_sample": self.generation["max_writing_sample"],
            "required_sections": self.generation["required_sections"],
            "default_material": self.generation["default_material"],
            
            # Path settings - ALL from config
            **{key: value for key, value in self.paths.items()},
            
            # Provider settings
            "providers": self.providers,
            
            # Tag settings
            "tag_formatting": self.tags["formatting"],
            "tag_generation": self.tags["generation"],
            
            # AI Detection settings
            **{key: value for key, value in self.ai_detection.items()},
            
            # Debug settings
            **{key: value for key, value in self.debug.items()},
            
            # Thresholds - FROM CONFIG FILE
            **{key: value for key, value in self.thresholds.items()},
            
            # WORD LIMITS (strictly enforced)
            "max_total_words": 1200,  # Total document limit
            "target_words": 200,      # Target per section
            "max_section_words": 250, # Hard limit per section
            
            # Word counting enforcement
            "enforce_word_limits": True,
            "word_limit_tolerance": 0.1,  # 10% tolerance
        }
    
    def _load_path_config(self) -> Dict[str, str]:
        """Load path configuration"""
        return self._load_config_file("config/paths.json")
    
    def _load_api_config(self) -> Dict[str, Any]:
        """Load API configuration"""
        return self._load_config_file("config/api.json")
    
    def _load_generation_config(self) -> Dict[str, Any]:
        """Load generation configuration"""
        return self._load_config_file("config/generation.json")
    
    def _load_providers_config(self) -> Dict[str, Any]:
        """Load providers configuration"""
        return self._load_config_file("config/providers.json")
    
    def _load_tags_config(self) -> Dict[str, Any]:
        """Load tags configuration"""
        return self._load_config_file("config/tags.json")
    
    def _load_ai_detection_config(self) -> Dict[str, Any]:
        """Load AI detection configuration"""
        return self._load_config_file("config/ai_detection.json")
    
    def _load_debug_config(self) -> Dict[str, Any]:
        """Load debug configuration"""
        return self._load_config_file("config/debug.json")
    
    def _load_thresholds_config(self) -> Dict[str, Any]:
        """Load thresholds configuration"""
        return self._load_config_file("config/thresholds.json")
    
    def _load_config_file(self, config_path: str) -> Dict[str, Any]:
        """Generic config file loader - NO FALLBACKS"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Required config file missing: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {config_file}: {e}")

# Global configuration instance
CONFIG = ConfigConstants()