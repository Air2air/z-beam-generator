"""
Length Manager - Single Source of Truth for Component Length Variation

Centralizes all length variation logic to prevent conflicts between:
- Config.yaml defaults
- Prompt template hardcoded ranges
- Sentence calculator variation
- Dynamic adjustment systems

Architecture:
- config.yaml defines {target, min, max, variation_mode} per component
- LengthManager provides randomized targets within range
- Generators inject target into prompts via {word_count}
- Post-generation validation ensures compliance
- Retry if outside bounds

Usage:
    from generation.core.length_manager import LengthManager
    
    manager = LengthManager(config)
    target = manager.get_target_length('material_description')
    # Returns random value between min and max (e.g., 12-35 for material_description)
    
    is_valid = manager.validate_length(text, 'material_description')
    # Returns True if word count is within configured min/max bounds
"""

import random
import logging
from typing import Dict, Tuple, Optional
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class LengthManager:
    """
    Centralized length variation manager for all components.
    
    Single source of truth for:
    - Target word counts
    - Min/max bounds
    - Variation modes (random, fixed, dynamic)
    - Length validation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize length manager with configuration.
        
        Args:
            config: Configuration dict with component_lengths section.
                   If None, loads from generation/config.yaml
        """
        if config is None:
            config_path = Path("generation/config.yaml")
            if not config_path.exists():
                raise FileNotFoundError(f"Config not found: {config_path}")
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        
        self.config = config
        self.component_specs = config.get('component_lengths', {})
        self.global_variation = config.get('length_variation_range', 5.0)  # 1-10 scale
        
        if not self.component_specs:
            raise ValueError("No component_lengths found in config")
        
        logger.debug(
            f"LengthManager initialized with {len(self.component_specs)} component specs, "
            f"global variation: {self.global_variation}"
        )
    
    def _calculate_variation_percentage(self) -> float:
        """
        Calculate variation percentage from global slider (1-10).
        
        Formula: variation_pct = 0.10 + (slider / 10 * 0.50)
        
        Returns:
            Variation percentage (0.15 to 0.60)
        """
        # Map 1-10 slider to 15%-60% variation
        return 0.10 + (self.global_variation / 10.0 * 0.50)
    
    def get_target_length(self, component_type: str) -> int:
        """
        Get randomized target length using GLOBAL variation range.
        
        Uses single length_variation_range slider (1-10) to calculate
        variation percentage, then applies uniformly to component target.
        
        Args:
            component_type: Type of component (material_description, caption, etc.)
            
        Returns:
            Target word count (randomized within global variation range)
            
        Raises:
            ValueError: If component_type not found in config
        """
        if component_type not in self.component_specs:
            raise ValueError(
                f"Component type '{component_type}' not found in config. "
                f"Available: {list(self.component_specs.keys())}"
            )
        
        spec = self.component_specs[component_type]
        
        # Handle legacy format (simple default value)
        if isinstance(spec, int):
            target = spec
            logger.warning(
                f"Component '{component_type}' using legacy format (single default: {target})"
            )
        else:
            target = spec.get('target', spec.get('default', 30))
        
        # Calculate min/max using GLOBAL variation percentage
        variation_pct = self._calculate_variation_percentage()
        variation_words = int(target * variation_pct)
        
        min_words = max(1, target - variation_words)
        max_words = target + variation_words
        
        # Generate random target within bounds
        randomized_target = random.randint(min_words, max_words)
        
        logger.debug(
            f"Generated target for {component_type}: {randomized_target} words "
            f"(base: {target}, variation: ±{int(variation_pct*100)}%, range: {min_words}-{max_words})"
        )
        
        return randomized_target
    
    def validate_length(
        self,
        text: str,
        component_type: str,
        strict: bool = True
    ) -> bool:
        """
        Validate that text meets length constraints using GLOBAL variation.
        
        Args:
            text: Generated text to validate
            component_type: Type of component
            strict: If True, enforce hard min/max bounds
                   If False, allow additional tolerance (±20%)
            
        Returns:
            True if text is within acceptable length range
        """
        if not text or not text.strip():
            logger.error(f"Empty text for {component_type}")
            return False
        
        word_count = len(text.split())
        
        spec = self.component_specs.get(component_type, {})
        
        # Get target
        if isinstance(spec, int):
            target = spec
        else:
            target = spec.get('target', spec.get('default', 30))
        
        # Calculate min/max using GLOBAL variation percentage
        variation_pct = self._calculate_variation_percentage()
        variation_words = int(target * variation_pct)
        
        min_words = max(1, target - variation_words)
        max_words = target + variation_words
        
        # Apply additional tolerance if not strict
        if not strict:
            tolerance = 0.20  # ±20% extra
            min_words = int(min_words * (1 - tolerance))
            max_words = int(max_words * (1 + tolerance))
        
        is_valid = min_words <= word_count <= max_words
        
        if not is_valid:
            logger.warning(
                f"Length validation failed for {component_type}: "
                f"{word_count} words (expected: {min_words}-{max_words}, "
                f"global variation: ±{int(variation_pct*100)}%)"
            )
        else:
            logger.debug(
                f"Length validation passed for {component_type}: "
                f"{word_count} words (range: {min_words}-{max_words})"
            )
        
        return is_valid
    
    def get_length_range(self, component_type: str) -> Tuple[int, int]:
        """
        Get min/max length range for a component using GLOBAL variation.
        
        Args:
            component_type: Type of component
            
        Returns:
            Tuple of (min_words, max_words) calculated from global variation
        """
        spec = self.component_specs.get(component_type, {})
        
        # Get target
        if isinstance(spec, int):
            target = spec
        else:
            target = spec.get('target', spec.get('default', 30))
        
        # Calculate using GLOBAL variation percentage
        variation_pct = self._calculate_variation_percentage()
        variation_words = int(target * variation_pct)
        
        min_words = max(1, target - variation_words)
        max_words = target + variation_words
        
        return (min_words, max_words)
    
    def get_variation_display(self, component_type: str) -> str:
        """
        Get human-readable length variation description using GLOBAL variation.
        
        Args:
            component_type: Type of component
            
        Returns:
            String like "12-35 words" showing dynamically calculated range
        """
        spec = self.component_specs.get(component_type, {})
        
        # Get target
        if isinstance(spec, int):
            target = spec
        else:
            target = spec.get('target', spec.get('default', 30))
        
        # Calculate using GLOBAL variation percentage
        variation_pct = self._calculate_variation_percentage()
        variation_words = int(target * variation_pct)
        
        min_words = max(1, target - variation_words)
        max_words = target + variation_words
        
        return f"{min_words}-{max_words} words (±{int(variation_pct*100)}%)"
    
    def should_retry_for_length(
        self,
        text: str,
        component_type: str,
        attempt: int,
        max_attempts: int = 3
    ) -> bool:
        """
        Determine if generation should retry due to length issues.
        
        Args:
            text: Generated text
            component_type: Type of component
            attempt: Current attempt number (1-indexed)
            max_attempts: Maximum allowed attempts
            
        Returns:
            True if should retry due to length violation
        """
        if attempt >= max_attempts:
            return False
        
        # Use strict validation for early attempts, relaxed for later
        strict = attempt < 2
        
        return not self.validate_length(text, component_type, strict=strict)
