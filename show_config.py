#!/usr/bin/env python3
"""
Show Current Optimization Settings

Displays the current dynamic optimization configuration values.
"""

import sys
import os

def show_optimization_settings():
    """Display current optimization settings from GlobalConfigManager."""
    try:
        # Add generator directory to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generator'))
        
        # Initialize config
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, parent_dir)
        from run import USER_CONFIG, PROVIDER_MODELS
        
        from generator.config.global_config import GlobalConfigManager
        GlobalConfigManager.initialize(USER_CONFIG, PROVIDER_MODELS)
        
        config = GlobalConfigManager.get_instance()
        
        print("🎛️  Current Optimization Settings")
        print("=" * 40)
        print()
        
        print("🎯 Detection Thresholds:")
        print(f"   AI Detection: {config.get_ai_detection_threshold()}% (lower = stricter)")
        print(f"   Natural Voice: {config.get_natural_voice_threshold()}% (lower = stricter)")
        print()
        
        print("🌡️  Temperature Settings:")
        print(f"   Content Generation: {config.get_content_temperature()} (creativity)")
        print(f"   Detection Calls: {config.get_detection_temperature()} (consistency)")  
        print(f"   Improvement Passes: {config.get_improvement_temperature()} (variation)")
        print(f"   Summary Generation: {config.get_summary_temperature()} (balance)")
        print(f"   Metadata Creation: {config.get_metadata_temperature()} (precision)")
        print()
        
        print("⚙️  Optimization Parameters:")
        print(f"   Iterations per Section: {config.get_iterations_per_section()}")
        print(f"   Max Article Words: {config.get_max_article_words()}")
        print(f"   API Timeout: {config.get_api_timeout()}s")
        print()
        
        print("🤖 Provider Configuration:")
        print(f"   Generator Provider: {config.get_generator_provider()}")
        print(f"   Detection Provider: {config.get_detection_provider()}")
        print(f"   Model: {config.get_provider_model(config.get_generator_provider())}")
        print()
        
        print("💡 Note: These values are managed dynamically and can be")
        print("   adjusted automatically based on training insights.")
        
    except Exception as e:
        print(f"❌ Error reading optimization settings: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(show_optimization_settings())
