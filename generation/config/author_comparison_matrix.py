#!/usr/bin/env python3
"""
Author Personality Comparison Matrix

Shows how the 4 authors differ across all configuration dimensions.

Usage:
    python3 processing/author_comparison_matrix.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generation.config.author_config_loader import get_author_config, get_author_config_loader
from processing.config.dynamic_config import DynamicConfig


def visualize_slider(value: int, width: int = 30) -> str:
    """Create ASCII bar visualization of slider value."""
    filled = int((value / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {value:3d}"


def main():
    print("=" * 100)
    print(" " * 30 + "AUTHOR PERSONALITY COMPARISON MATRIX")
    print("=" * 100)
    print()
    
    loader = get_author_config_loader()
    authors = [1, 2, 3, 4]
    profiles = [loader.get_author_profile(aid) for aid in authors]
    configs = [get_author_config(aid) for aid in authors]
    
    # Header
    print(f"{'Characteristic':<30} | {'Yi-Chun':>12} | {'Alessandro':>12} | {'Ikmanda':>12} | {'Todd':>12}")
    print("-" * 100)
    
    # Base sliders
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
    
    print("BASE INTENSITY SLIDERS (0-100):")
    print()
    
    for label, method in sliders:
        values = [getattr(config, method)() for config in configs]
        print(f"  {label:<28} |", end="")
        for val in values:
            print(f" {val:>11} |", end="")
        print()
    
    print()
    print("-" * 100)
    print("CALCULATED PARAMETERS (for caption generation):")
    print()
    
    # Dynamic calculations
    dynamics = [DynamicConfig(base_config=config) for config in configs]
    
    calculations = [
        ('Temperature', lambda d: f"{d.calculate_temperature('caption'):.2f}"),
        ('Max Tokens', lambda d: f"{d.calculate_max_tokens('caption')}"),
        ('Max Attempts', lambda d: f"{d.calculate_retry_behavior()['max_attempts']}"),
        ('AI Threshold', lambda d: f"{d.calculate_detection_threshold():.1f}"),
        ('Word Rep Threshold', lambda d: f"{d.calculate_repetition_sensitivity()['word_frequency']}"),
        ('Min Readability', lambda d: f"{d.calculate_readability_thresholds()['min']:.1f}"),
        ('Grammar Leniency', lambda d: f"{d.calculate_grammar_strictness():.2f}"),
        ('Target Length', lambda d: f"{d.calculate_target_length_range('caption')['target']}w"),
    ]
    
    for label, calc_func in calculations:
        print(f"  {label:<28} |", end="")
        for dynamic in dynamics:
            val_str = calc_func(dynamic)
            print(f" {val_str:>11} |", end="")
        print()
    
    print()
    print("=" * 100)
    print()
    
    # Character descriptions
    print("AUTHOR PERSONALITIES:")
    print()
    for i, (aid, profile) in enumerate(zip(authors, profiles)):
        name = profile['name']
        country = profile['country']
        personality = profile['personality']
        print(f"  {i+1}. {name} ({country})")
        print(f"     → {personality}")
        print()
    
    print("=" * 100)
    print()
    print("💡 KEY INSIGHTS:")
    print()
    print("  • Yi-Chun: Most precise, highest technical density, most structured")
    print("  • Alessandro: Most sophisticated, highest variation, balanced")
    print("  • Ikmanda: Most accessible, highest imperfection tolerance, most engaging")
    print("  • Todd: Most conversational, highest rhythm variation, balanced technical")
    print()
    print("  These offsets ensure DISTINCT writing styles while maintaining")
    print("  global control via the base config.yaml sliders.")
    print()


if __name__ == '__main__':
    main()
