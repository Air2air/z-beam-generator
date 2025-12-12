#!/usr/bin/env python3
"""
Author-Specific Configuration Loader

Applies per-author offsets to base config values to create distinct author personalities
while maintaining global control through base sliders.

Architecture:
- Base config (config.yaml) provides global defaults (user-controlled sliders)
- Author profiles (author_profiles.yaml) provide personality offsets
- Final values = base + author_offset (clamped to [0, 100])

Usage:
    from processing.author_config_loader import get_author_config
    
    # Get config with author-specific offsets applied
    config = get_author_config(author_id=1)  # Yi-Chun Lin
    
    # Use dynamic config with author-specific values
    from processing.dynamic_config import DynamicConfig
    dynamic = DynamicConfig(base_config=config)
    temp = dynamic.calculate_temperature('micro')
"""

import yaml
from pathlib import Path
from typing import Dict, Optional
import logging

from processing.config.config_loader import ProcessingConfig

logger = logging.getLogger(__name__)


class AuthorConfigLoader:
    """Loads and applies author-specific configuration offsets."""
    
    def __init__(self, author_profiles_path: Optional[str] = None):
        """
        Initialize author config loader.
        
        Args:
            author_profiles_path: Path to author_profiles.yaml (optional)
        """
        if author_profiles_path is None:
            author_profiles_path = Path(__file__).parent / "author_profiles.yaml"  # processing/config/author_profiles.yaml
        
        self.profiles_path = Path(author_profiles_path)
        self._profiles_cache: Optional[Dict] = None
    
    def _load_profiles(self) -> Dict:
        """Load author profiles from YAML (cached)."""
        if self._profiles_cache is not None:
            return self._profiles_cache
        
        if not self.profiles_path.exists():
            logger.warning(f"Author profiles not found: {self.profiles_path}")
            return {"authors": {}}
        
        try:
            with open(self.profiles_path, 'r') as f:
                self._profiles_cache = yaml.safe_load(f)
            return self._profiles_cache
        except Exception as e:
            logger.error(f"Failed to load author profiles: {e}")
            return {"authors": {}}
    
    def get_author_profile(self, author_id: int) -> Optional[Dict]:
        """
        Get author profile by ID.
        
        Args:
            author_id: Author ID (1-4)
            
        Returns:
            Author profile dict with offsets, or None if not found
        """
        profiles = self._load_profiles()
        authors = profiles.get("authors", {})
        
        # Find profile by author_id
        for key, profile in authors.items():
            if profile.get("author_id") == author_id:
                return profile
        
        logger.warning(f"No profile found for author_id={author_id}")
        return None
    
    def apply_author_offsets(
        self, 
        base_config: ProcessingConfig, 
        author_id: int
    ) -> ProcessingConfig:
        """
        Create new config with author-specific offsets applied.
        
        Args:
            base_config: Base configuration from config.yaml
            author_id: Author ID to apply offsets for
            
        Returns:
            New ProcessingConfig with offsets applied
        """
        profile = self.get_author_profile(author_id)
        if profile is None:
            logger.info(f"No offsets for author {author_id}, using base config")
            return base_config
        
        offsets = profile.get("offsets", {})
        if not offsets:
            logger.info(f"No offsets defined for author {author_id}")
            return base_config
        
        # Load base config data
        with open(base_config.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Apply offsets (with clamping to [1, 3] for 1-3 scale)
        slider_fields = [
            'author_voice_intensity',
            'personality_intensity',
            'engagement_style',
            'emotional_intensity',  # Phase 4
            'technical_language_intensity',
            'context_specificity',
            'sentence_rhythm_variation',
            'imperfection_tolerance',
            'structural_predictability',
            'ai_avoidance_intensity',
            'length_variation_range'
        ]
        
        applied_offsets = []
        for field in slider_fields:
            if field in offsets:
                # Default to 5 (moderate) if field missing - INTENTIONAL
                # Authors inherit balanced baseline, then offsets are applied
                base_value = config_data.get(field, 5)  # Default to middle of 1-10 scale
                offset = offsets[field]
                
                # Clamp to [1, 10] for 1-10 scale (normalized Nov 16, 2025)
                new_value = max(1, min(10, base_value + offset))
                
                if new_value != base_value:
                    config_data[field] = new_value
                    applied_offsets.append(
                        f"{field}: {base_value} → {new_value} ({offset:+d})"
                    )
        
        if applied_offsets:
            author_name = profile.get("name", f"Author {author_id}")
            logger.info(
                f"Applied {len(applied_offsets)} offsets for {author_name}:\n  " +
                "\n  ".join(applied_offsets)
            )
        
        # Create temporary config with modified values
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as tmp:
            yaml.dump(config_data, tmp)
            tmp_path = tmp.name
        
        # Return new ProcessingConfig with modified values
        return ProcessingConfig(tmp_path)


# Singleton instance
_loader: Optional[AuthorConfigLoader] = None


def get_author_config_loader() -> AuthorConfigLoader:
    """Get singleton author config loader."""
    global _loader
    if _loader is None:
        _loader = AuthorConfigLoader()
    return _loader


def get_author_config(author_id: int) -> ProcessingConfig:
    """
    Get configuration with author-specific offsets applied.
    
    This is the main entry point for getting author-specific config.
    
    Args:
        author_id: Author ID (1-4)
        
    Returns:
        ProcessingConfig with author offsets applied
        
    Example:
        >>> config = get_author_config(author_id=1)  # Yi-Chun Lin
        >>> config.get_imperfection_tolerance()  # Returns base - 15
        35
        
        >>> config = get_author_config(author_id=2)  # Alessandro
        >>> config.get_imperfection_tolerance()  # Returns base + 5
        55
    """
    loader = get_author_config_loader()
    base_config = ProcessingConfig()
    return loader.apply_author_offsets(base_config, author_id)


def compare_author_configs(
    author_id_1: int, 
    author_id_2: int,
    component_type: str = "micro"
) -> str:
    """
    Compare configuration values between two authors.
    
    Args:
        author_id_1: First author ID
        author_id_2: Second author ID
        component_type: Component type for dynamic calculations
        
    Returns:
        Formatted comparison report
    """
    from processing.dynamic_config import DynamicConfig
    
    config1 = get_author_config(author_id_1)
    config2 = get_author_config(author_id_2)
    
    dynamic1 = DynamicConfig(base_config=config1)
    dynamic2 = DynamicConfig(base_config=config2)
    
    # Get author names
    loader = get_author_config_loader()
    profile1 = loader.get_author_profile(author_id_1)
    profile2 = loader.get_author_profile(author_id_2)
    name1 = profile1.get("name", f"Author {author_id_1}") if profile1 else f"Author {author_id_1}"
    name2 = profile2.get("name", f"Author {author_id_2}") if profile2 else f"Author {author_id_2}"
    
    lines = [
        "=" * 80,
        f"AUTHOR CONFIGURATION COMPARISON: {name1} vs {name2}",
        "=" * 80,
        "",
        f"{'Metric':<35} | {name1[:15]:>15} | {name2[:15]:>15} | {'Delta':>10}",
        "-" * 80,
    ]
    
    # Base slider comparisons
    sliders = [
        ('Author Voice', 'get_author_voice_intensity'),
        ('Personality', 'get_personality_intensity'),
        ('Engagement', 'get_engagement_style'),
        ('Technical Language', 'get_technical_language_intensity'),
        ('Context Specificity', 'get_context_specificity'),
        ('Rhythm Variation', 'get_sentence_rhythm_variation'),
        ('Imperfection Tolerance', 'get_imperfection_tolerance'),
        ('Structural Predictability', 'get_structural_predictability'),
        ('AI Avoidance', 'get_ai_avoidance_intensity'),
        ('Length Variation', 'get_length_variation_range'),
    ]
    
    lines.append("BASE SLIDERS:")
    for label, method in sliders:
        val1 = getattr(config1, method)()
        val2 = getattr(config2, method)()
        delta = val2 - val1
        lines.append(
            f"  {label:<33} | {val1:>15} | {val2:>15} | {delta:>+10}"
        )
    
    lines.append("")
    lines.append("CALCULATED VALUES:")
    
    # Dynamic calculations
    calculations = [
        ('Temperature', lambda d: d.calculate_temperature(component_type)),
        ('Max Tokens', lambda d: d.calculate_max_tokens(component_type)),
        ('AI Threshold', lambda d: d.calculate_detection_threshold()),
        ('Min Readability', lambda d: d.calculate_readability_thresholds()['min']),
        ('Grammar Leniency', lambda d: d.calculate_grammar_strictness()),
    ]
    
    for label, calc_func in calculations:
        val1 = calc_func(dynamic1)
        val2 = calc_func(dynamic2)
        
        if isinstance(val1, float):
            delta = val2 - val1
            lines.append(
                f"  {label:<33} | {val1:>15.2f} | {val2:>15.2f} | {delta:>+10.2f}"
            )
        else:
            delta = val2 - val1
            lines.append(
                f"  {label:<33} | {val1:>15} | {val2:>15} | {delta:>+10}"
            )
    
    lines.append("")
    lines.append("=" * 80)
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test author config loading
    import sys
    
    if len(sys.argv) > 1:
        author_id = int(sys.argv[1])
        config = get_author_config(author_id)
        
        loader = get_author_config_loader()
        profile = loader.get_author_profile(author_id)
        
        if profile:
            print(f"\n{profile['name']} - {profile['country']}")
            print(f"Personality: {profile['personality']}")
            print(f"\nApplied Configuration:")
            print(f"  Imperfection Tolerance: {config.get_imperfection_tolerance()}")
            print(f"  Technical Language: {config.get_technical_language_intensity()}")
            print(f"  AI Avoidance: {config.get_ai_avoidance_intensity()}")
    else:
        print("Usage: python3 processing/author_config_loader.py <author_id>")
        print("\nAvailable authors:")
        print("  1 - Yi-Chun Lin (Taiwan)")
        print("  2 - Alessandro Moretti (Italy)")
        print("  3 - Ikmanda Roswati (Indonesia)")
        print("  4 - Todd Dunning (USA)")
