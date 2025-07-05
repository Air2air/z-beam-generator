#!/usr/bin/env python3
"""
Z-Beam Generator - User Configuration File

This file contains only user configuration settings.
All application logic has been moved to the /generator directory.
"""

# ---- USER CONFIGURATION (edit here) ----

# Available providers and their models
PROVIDER_MODELS = {
    "GEMINI": {
        "model": "gemini-2.5-flash",  # Latest stable model
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
    },
    "XAI": {
        "model": "grok-3-mini-beta",
        "url_template": "https://api.x.ai/v1/chat/completions",
    },
    "DEEPSEEK": {
        "model": "deepseek-chat",  # Points to DeepSeek-V3
        "url_template": "https://api.deepseek.com/v1/chat/completions",
    },
}

# User configuration for article generation
USER_CONFIG = {
    "material": "Bronze",  # Material to generate content for
    "category": "Material",  # Article category
    "file_name": "bronze_laser_cleaning.mdx",  # Output filename
    "generator_provider": "DEEPSEEK",  # XAI GEMINI DEEPSEEK
    "detection_provider": "DEEPSEEK",  # XAI GEMINI DEEPSEEK
    "author": "todd_dunning.mdx",  # Author profile
    "force_regenerate": True,  # Always regenerate content
    "iterations_per_section": 5,  # Number of iterations to improve detection scores
    "max_article_words": 800,  # Maximum article word count
    "api_timeout": 40,  # API request timeout in seconds
    
    # Note: Optimization values (thresholds, temperatures) are now managed
    # dynamically by the GlobalConfigManager with intelligent defaults.
    # They can be adjusted through training insights and recommendations.
}

# ---- END CONFIGURATION ----

if __name__ == "__main__":
    # Import and run the main application from generator
    import sys
    import os
    
    # Add generator directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generator'))
    
    from main import main
    main()
