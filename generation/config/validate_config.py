#!/usr/bin/env python3
"""
Processing Config Validator

Validates that processing/config.yaml is properly structured and
that all processing components are actually using the centralized config.

Usage:
    python3 processing/validate_config.py
    
Or from anywhere:
    python3 -m processing.validate_config
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from generation.config.config_loader import ProcessingConfig


def main():
    """Validate processing configuration."""
    print("=" * 70)
    print("PROCESSING CONFIG VALIDATION")
    print("=" * 70)
    print()
    
    # Load config
    try:
        config = ProcessingConfig()
        print(f"✅ Config loaded from: {config.config_path}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return 1
    
    print()
    
    # Run validation
    result = config.validate()
    
    # Display errors
    if result['errors']:
        print("❌ ERRORS:")
        for error in result['errors']:
            print(f"   - {error}")
        print()
    
    # Display warnings
    if result['warnings']:
        print("⚠️  WARNINGS:")
        for warning in result['warnings']:
            print(f"   - {warning}")
        print()
    
    # Overall result
    if result['valid']:
        print("✅ Configuration is VALID")
        print()
        print_config_summary(config)
        return 0
    else:
        print("❌ Configuration has ERRORS - please fix before using")
        return 1


def print_config_summary(config: ProcessingConfig):
    """Print summary of loaded configuration."""
    print()
    print("Configuration Summary:")
    print("-" * 70)
    
    # Intensity sliders
    print("\n📊 INTENSITY SLIDERS (User Controls):")
    print(f"   Author Voice:        {config.get_author_voice_intensity()}")
    print(f"   Personality:         {config.get_personality_intensity()}")
    print(f"   Engagement:          {config.get_engagement_style()}")
    print(f"   Technical Language:  {config.get_technical_language_intensity()}")
    print(f"   Context Specificity: {config.get_context_specificity()}")
    print(f"   Sentence Rhythm:     {config.get_sentence_rhythm_variation()}")
    print(f"   Imperfection:        {config.get_imperfection_tolerance()}")
    print(f"   Structural:          {config.get_structural_predictability()}")
    print(f"   AI Avoidance:        {config.get_ai_avoidance_intensity()}")
    print(f"   Length Variation:    {config.get_length_variation_range()}")
    
    # Detection settings
    print("\n🔍 DETECTION SETTINGS:")
    print(f"   AI Threshold (normal): {config.get_ai_threshold(strict_mode=False)}")
    print(f"   AI Threshold (strict): {config.get_ai_threshold(strict_mode=True)}")
    conf = config.get_confidence_thresholds()
    print(f"   High Confidence:       {conf['high']}")
    print(f"   Medium Confidence:     {conf['medium']}")
    rec = config.get_recommendation_thresholds()
    print(f"   Regenerate Threshold:  {rec['regenerate']}")
    print(f"   Revise Threshold:      {rec['revise']}")
    
    rep = config.get_repetition_thresholds()
    print(f"\n   Repetition Detection:")
    print(f"      Word Frequency:     {rep['word_frequency']}")
    print(f"      Critical:           {rep['word_frequency_critical']}")
    print(f"      Structural:         {rep['structural_repetition']}")
    
    # API settings
    print("\n🌐 API GENERATION:")
    print(f"   Base Temperature:    {config.get_temperature()}")
    print(f"   Max Attempts:        {config.get_max_attempts()}")
    print(f"   Retry Temp Increase: {config.get_retry_temperature_increase()}")
    print(f"\n   Max Tokens:")
    for comp_type in ['material_description', 'caption', 'settings_description', 'faq', 'troubleshooter']:
        tokens = config.get_max_tokens(comp_type)
        print(f"      {comp_type:15s} {tokens}")
    
    # Readability
    read = config.get_readability_thresholds()
    print(f"\n📖 READABILITY:")
    print(f"   Min Flesch Score:    {read['min']}")
    print(f"   Max Flesch Score:    {read['max']}")
    
    # Component lengths
    print(f"\n📏 COMPONENT TARGET LENGTHS (words):")
    for comp_type in ['material_description', 'caption', 'settings_description', 'faq', 'troubleshooter']:
        length = config.get_component_length(comp_type)
        print(f"   {comp_type:15s} {length}")
    
    # Data sources
    print(f"\n📁 DATA SOURCES:")
    print(f"   Materials YAML:      {config.get_materials_yaml_path()}")
    print(f"   Categories YAML:     {config.get_categories_yaml_path()}")
    
    # Output
    print(f"\n📤 OUTPUT:")
    print(f"   Frontmatter Dir:     {config.get_output_dir()}")
    print(f"   Backup Dir:          {config.get_backup_dir()}")
    print(f"   Create Backups:      {config.should_create_backup()}")


if __name__ == '__main__':
    sys.exit(main())
