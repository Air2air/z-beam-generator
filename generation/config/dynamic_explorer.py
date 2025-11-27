#!/usr/bin/env python3
"""
Dynamic Config Explorer

Shows how changing intensity sliders dynamically affects all downstream settings.

Usage:
    # See current calculated settings
    python3 processing/dynamic_explorer.py
    
    # Simulate changing a slider
    python3 processing/dynamic_explorer.py --simulate ai_avoidance=80
    
    # Compare two scenarios
    python3 processing/dynamic_explorer.py --compare "imperfection=30" "imperfection=70"
"""

import sys
import argparse
from pathlib import Path
import yaml
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from processing.config.dynamic_config import DynamicConfig
from processing.config.config_loader import ProcessingConfig


def main():
    parser = argparse.ArgumentParser(description='Explore dynamic config calculations')
    parser.add_argument('--simulate', help='Simulate slider change (e.g., ai_avoidance=80)')
    parser.add_argument('--compare', nargs=2, metavar=('SETTING1', 'SETTING2'),
                       help='Compare two settings (e.g., imperfection=30 imperfection=70)')
    parser.add_argument('--component', default='caption', help='Component type to analyze')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_settings(args.compare[0], args.compare[1], args.component)
    elif args.simulate:
        simulate_change(args.simulate, args.component)
    else:
        show_current(args.component)


def show_current(component_type: str):
    """Show current dynamically calculated settings."""
    print("=" * 70)
    print("CURRENT DYNAMIC SETTINGS (from processing/config.yaml)")
    print("=" * 70)
    print()
    
    config = DynamicConfig()
    print(config.get_dynamic_settings_report(component_type))


def simulate_change(setting_str: str, component_type: str):
    """Simulate changing a slider and show the effects."""
    try:
        slider_name, value_str = setting_str.split('=')
        value = int(value_str)
        
        if not 0 <= value <= 100:
            print(f"❌ Error: Value must be 0-100, got {value}")
            return 1
        
    except ValueError:
        print(f"❌ Error: Invalid format. Use 'slider_name=value' (e.g., ai_avoidance=80)")
        return 1
    
    # Map slider names
    slider_map = {
        'author_voice': 'author_voice_intensity',
        'personality': 'personality_intensity',
        'engagement': 'engagement_style',
        'technical': 'technical_language_intensity',
        'context': 'context_specificity',
        'rhythm': 'sentence_rhythm_variation',
        'imperfection': 'imperfection_tolerance',
        'structural': 'structural_predictability',
        'ai_avoidance': 'ai_avoidance_intensity',
        'length': 'length_variation_range'
    }
    
    full_slider_name = slider_map.get(slider_name, slider_name)
    
    print("=" * 70)
    print(f"SIMULATING: {full_slider_name} = {value}")
    print("=" * 70)
    print()
    
    # Load current config
    current_config = ProcessingConfig()
    current_value = getattr(current_config, f'get_{full_slider_name}')()
    
    print(f"📊 Current value: {current_value}")
    print(f"🔮 Simulated value: {value}")
    print(f"📈 Change: {value - current_value:+d}")
    print()
    
    # Create temporary modified config
    with open(current_config.config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Store original
    original_value = config_data[full_slider_name]
    config_data[full_slider_name] = value
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        yaml.dump(config_data, tmp)
        tmp_path = tmp.name
    
    # Load with new value
    simulated_config = ProcessingConfig(tmp_path)
    dynamic = DynamicConfig()
    dynamic.base_config = simulated_config
    
    print(dynamic.get_dynamic_settings_report(component_type))
    
    # Cleanup
    import os
    os.unlink(tmp_path)
    
    print()
    print("💡 To make this change permanent:")
    print(f"   python3 processing/intensity_cli.py set {slider_name} {value}")


def compare_settings(setting1: str, setting2: str, component_type: str):
    """Compare two different slider values side-by-side."""
    try:
        slider1, val1_str = setting1.split('=')
        slider2, val2_str = setting2.split('=')
        val1 = int(val1_str)
        val2 = int(val2_str)
        
        if slider1 != slider2:
            print("❌ Error: Must compare the same slider with different values")
            return 1
        
        if not (0 <= val1 <= 100 and 0 <= val2 <= 100):
            print("❌ Error: Values must be 0-100")
            return 1
    except ValueError:
        print("❌ Error: Invalid format. Use 'slider=value' for both arguments")
        return 1
    
    slider_map = {
        'ai_avoidance': 'ai_avoidance_intensity',
        'imperfection': 'imperfection_tolerance',
        'rhythm': 'sentence_rhythm_variation',
        'technical': 'technical_language_intensity',
        'personality': 'personality_intensity',
        'engagement': 'engagement_style',
        'context': 'context_specificity',
        'structural': 'structural_predictability',
        'length': 'length_variation_range',
        'author_voice': 'author_voice_intensity'
    }
    
    full_name = slider_map.get(slider1, slider1)
    
    print("=" * 70)
    print(f"COMPARISON: {full_name} at {val1} vs {val2}")
    print("=" * 70)
    print()
    
    # Get both configurations
    configs = []
    for val in [val1, val2]:
        current_config = ProcessingConfig()
        with open(current_config.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        config_data[full_name] = val
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            yaml.dump(config_data, tmp)
            tmp_path = tmp.name
        
        modified_config = ProcessingConfig(tmp_path)
        dynamic = DynamicConfig()
        dynamic.base_config = modified_config
        configs.append((val, dynamic, tmp_path))
    
    # Compare key metrics
    print(f"{'Metric':<30} | {val1:>10} | {val2:>10} | {'Delta':>10}")
    print("-" * 70)
    
    for metric_name, getter in [
        ('Temperature', lambda d: d.calculate_temperature(component_type)),
        ('Max Tokens', lambda d: d.calculate_max_tokens(component_type)),
        ('Max Attempts', lambda d: d.calculate_retry_behavior()['max_attempts']),
        ('AI Threshold', lambda d: d.calculate_detection_threshold()),
        ('Word Rep Threshold', lambda d: d.calculate_repetition_sensitivity()['word_frequency']),
        ('Min Readability', lambda d: d.calculate_readability_thresholds()['min']),
        ('Grammar Leniency', lambda d: d.calculate_grammar_strictness()),
    ]:
        metric1 = getter(configs[0][1])
        metric2 = getter(configs[1][1])
        
        # Format based on type
        if isinstance(metric1, float):
            delta = metric2 - metric1
            print(f"{metric_name:<30} | {metric1:>10.2f} | {metric2:>10.2f} | {delta:>+10.2f}")
        else:
            delta = metric2 - metric1
            print(f"{metric_name:<30} | {metric1:>10} | {metric2:>10} | {delta:>+10}")
    
    # Cleanup
    import os
    for _, _, path in configs:
        os.unlink(path)
    
    print()
    print(f"💡 Impact of changing {full_name} from {val1} to {val2}:")
    if val2 > val1:
        print(f"   Increasing this slider adjusts the system toward more variation/creativity")
    else:
        print(f"   Decreasing this slider adjusts the system toward more consistency/strictness")


if __name__ == '__main__':
    sys.exit(main() or 0)
