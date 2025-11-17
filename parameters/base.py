"""
Base Parameter Module

All parameters inherit from BaseParameter to ensure consistent interface.
Uses preset prompt dictionaries for clean, maintainable parameter logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from pathlib import Path
import yaml


class ParameterCategory(Enum):
    """Parameter categories for organization"""
    VOICE = "voice"
    TECHNICAL = "technical"
    VARIATION = "variation"
    AI_DETECTION = "ai_detection"


class ParameterTier(Enum):
    """Three-tier system for all parameters"""
    LOW = "low"          # < 0.3
    MODERATE = "moderate"  # 0.3 - 0.7
    HIGH = "high"        # > 0.7


class BaseParameter(ABC):
    """
    Abstract base class for all configuration parameters.
    
    Philosophy:
    - Each parameter has preset prompts in YAML files
    - Parameter module selects appropriate prompt based on tier
    - Prompt builder orchestrates all parameter prompts
    - No runtime string building - just dictionary lookups
    
    Each parameter must implement:
    1. normalize() - Convert config value (1-10) to 0.0-1.0
    2. get_tier() - Determine low/moderate/high tier
    3. generate_prompt_guidance() - Select preset prompt
    4. get_metadata() - Return parameter information
    """
    
    def __init__(self, config_value: int):
        """
        Initialize parameter with config value.
        
        Args:
            config_value: Raw value from config.yaml (typically 1-10)
        """
        self.config_value = config_value
        self.normalized_value = self.normalize(config_value)
        self.tier = self.get_tier(self.normalized_value)
    
    @abstractmethod
    def normalize(self, value: int) -> float:
        """
        Convert config value to normalized 0.0-1.0 scale.
        
        Args:
            value: Raw config value (1-10 or 1-3)
            
        Returns:
            Normalized float between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def get_tier(self, normalized: float) -> ParameterTier:
        """
        Determine which tier this normalized value falls into.
        
        Args:
            normalized: Normalized value (0.0-1.0)
            
        Returns:
            ParameterTier (LOW, MODERATE, or HIGH)
        """
        pass
    
    @abstractmethod
    def generate_prompt_guidance(
        self,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate prompt guidance text for this parameter.
        
        Typically just selects preset prompt from dictionary.
        
        Args:
            context: Context dict with keys:
                - length: Target word count
                - component_type: subtitle, caption, etc.
                - voice: Voice profile dict
                - other parameters as needed
                
        Returns:
            Prompt guidance string or None if no guidance needed
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return parameter metadata for documentation and testing.
        
        Returns:
            Dict with:
                - name: Parameter name
                - category: ParameterCategory enum
                - scale: "1-10" or "1-3"
                - description: What this parameter controls
                - maps_to: "voice_params", "enrichment_params", or "direct"
        """
        pass
    
    def get_voice_param_value(self) -> float:
        """
        Get value for voice_params dict.
        Most parameters use normalized_value, override if different.
        """
        return self.normalized_value
    
    def _load_prompts_from_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load prompts from YAML file.
        
        Args:
            filename: YAML filename in parameters/presets/
            
        Returns:
            Dictionary with prompt data
            
        Raises:
            FileNotFoundError: If YAML file doesn't exist
        """
        yaml_path = Path('parameters/presets') / filename
        
        if not yaml_path.exists():
            raise FileNotFoundError(
                f"Parameter prompts file not found: {yaml_path}\n"
                f"Expected YAML file with preset prompts for parameter."
            )
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data.get('prompts', {})
    
    def __repr__(self) -> str:
        meta = self.get_metadata()
        return f"{meta['name']}(config={self.config_value}, normalized={self.normalized_value:.3f}, tier={self.tier.value})"


class Scale10Parameter(BaseParameter):
    """
    Base class for 1-10 scale parameters.
    
    Normalizes 1-10 to 0.0-1.0 and determines tier.
    """
    
    def normalize(self, value: int) -> float:
        """Map 1-10 to 0.0-1.0"""
        if not (1 <= value <= 10):
            raise ValueError(f"Value must be 1-10, got {value}")
        return (value - 1) / 9.0
    
    def get_tier(self, normalized: float) -> ParameterTier:
        """Standard tier thresholds"""
        if normalized < 0.3:
            return ParameterTier.LOW
        elif normalized < 0.7:
            return ParameterTier.MODERATE
        else:
            return ParameterTier.HIGH


class Scale3Parameter(BaseParameter):
    """
    Base class for 1-3 scale parameters.
    
    Normalizes 1-3 to 0.0/0.5/1.0 and determines tier.
    """
    
    def normalize(self, value: int) -> float:
        """Map 1-3 to 0.0/0.5/1.0"""
        if not (1 <= value <= 3):
            raise ValueError(f"Value must be 1-3, got {value}")
        return (value - 1) * 0.5
    
    def get_tier(self, normalized: float) -> ParameterTier:
        """1→LOW, 2→MODERATE, 3→HIGH"""
        if normalized < 0.25:
            return ParameterTier.LOW
        elif normalized < 0.75:
            return ParameterTier.MODERATE
        else:
            return ParameterTier.HIGH
