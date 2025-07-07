#!/usr/bin/env python3
"""
Show Current Optimization Settings

Displays the current dynamic optimization configuration values.
"""

import sys
import os

def show_scoring_thresholds():
    """Display content quality scoring thresholds and targets."""
    try:
        # Initialize config
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, parent_dir)
        from run import USER_CONFIG, PROVIDER_MODELS
        
        from config.global_config import GlobalConfigManager
        GlobalConfigManager.initialize(USER_CONFIG, PROVIDER_MODELS)
        
        config = GlobalConfigManager.get_instance()
        
        print("📊 Content Quality Scoring Framework")
        print("=" * 45)
        print()
        
        print("🎯 AI Detection Scoring:")
        print(f"   Current Threshold: {config.get_ai_detection_threshold()}%")
        print("   Target Range: 0-25% (lower scores are better)")
        print("   Purpose: Measure how artificial content appears")
        print("   Scoring Scale:")
        print("     0-10%  : Excellent - naturally written")
        print("     11-25% : Good - minimal AI patterns")
        print("     26-40% : Acceptable - some AI patterns")
        print("     41-60% : Poor - obvious AI patterns")
        print("     61-100%: Unacceptable - clearly AI-generated")
        print()
        
        print("✨ Natural Voice Authenticity Scoring:")
        print(f"   Current Threshold: {config.get_natural_voice_threshold()}%")
        print("   Target Range: 15-25% (moderate scores optimal)")
        print("   Purpose: Measure authentic professional voice")
        print("   Scoring Scale:")
        print("     0-10%  : Too artificial - lacks natural voice")
        print("     11-14% : Below target - needs more authenticity")
        print("     15-25% : Optimal - excellent professional voice ✅")
        print("     26-30% : Above target - may be over-humanized")
        print("     31-100%: Excessive - overly casual/unprofessional")
        print()
        
        print("📋 Quality Assessment Process:")
        print("   1. Production content generated (single-pass)")
        print("   2. Content saved to /output directory")
        print("   3. Training evaluation applies scoring prompts")
        print("   4. Scores inform template optimization")
        print("   5. Updated parameters improve future generation")
        print()
        
        print("🔍 Reference:")
        print("   Complete framework: SCORING.md")
        print("   Detection prompts: detection/detection_prompts.json")
        print()
        
        print("💡 Note: Scoring occurs ONLY during training phases.")
        print("   Production generation uses optimized single-pass approach.")
        
    except Exception as e:
        print(f"❌ Error reading scoring thresholds: {e}")
        return 1
    
    return 0

def show_optimization_settings():
    """Display current optimization settings from GlobalConfigManager."""
    try:
        # Initialize config
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, parent_dir)
        from run import USER_CONFIG, PROVIDER_MODELS
        
        from config.global_config import GlobalConfigManager
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
        print(f"   Max Tokens per Request: {config.get_max_tokens()}")
        print(f"   API Timeout: {config.get_api_timeout()}s")
        print(f"   Overall Timeout: {config.get_overall_timeout()}s")
        print()
        
        print("🤖 Provider Configuration:")
        print(f"   Generator Provider: {config.get_generator_provider()}")
        print(f"   Detection Provider: {config.get_detection_provider()}")
        print(f"   Generator Model: {config.get_generator_model()}")
        print()
        
        print("💡 Note: These values are managed dynamically and can be")
        print("   adjusted automatically based on training insights.")
        
    except Exception as e:
        print(f"❌ Error reading optimization settings: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scoring-thresholds":
        sys.exit(show_scoring_thresholds())
    else:
        sys.exit(show_optimization_settings())
