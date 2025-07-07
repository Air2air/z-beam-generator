#!/usr/bin/env python3
"""
Z-Beam Generator - User Configuration File

This file contains only user configuration settings.
All application logic has been moved to the /generator directory.
"""

# ---- USER CONFIGURATION (edit here) ----

# All provider and model config must be accessed via GlobalConfigManager
PROVIDER_MODELS = {
    "GEMINI": {
        # Model and URL are only referenced via config manager
        "model": "gemini-2.0-flash-exp",  # Updated to current model
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
    },
    "XAI": {
        "model": "grok-2-1212",  # Current XAI model
        "url_template": "https://api.x.ai/v1/chat/completions",
    },
    "DEEPSEEK": {
        "model": "deepseek-chat",
        "url_template": "https://api.deepseek.com/v1/chat/completions",
    },
}

# User configuration for article generation
USER_CONFIG = {
    "material": "Bronze",
    "category": "Material",
    "file_name": "bronze_laser_cleaning.mdx",
    "generator_provider": "DEEPSEEK",
    "detection_provider": "DEEPSEEK",
    "author": "todd_dunning.mdx",
    "force_regenerate": True,
    # All config values below must be accessed via config manager in application code
    "iterations_per_section": 5,
    "max_article_words": 800,
    "api_timeout": 30,  # Increased for DEEPSEEK
    "max_tokens": 8192,  # DEEPSEEK max limit
    "overall_timeout": 300,  # Increased for slower optimization
    # Optimization values are managed dynamically by GlobalConfigManager
    
    # === OPTIMIZATION MODE ===
    "optimization_mode": "quality_focused",  # "speed_focused" or "quality_focused"
    "enable_real_time_optimization": True,   # Enable quality optimization during production
    "quality_retry_attempts": 3,             # Number of retries if quality is below threshold
    "enable_section_scoring": True,          # Score each section during generation
    "scoring_threshold_ai": 25,              # AI detection threshold (lower is better)
    "scoring_threshold_nv": 20,              # Natural voice threshold (target range)
    
    # === NEW SINGLE-PASS ARCHITECTURE CONFIG ===
    "generator_version": "2.0.0-single-pass",
    "default_section_words": 150,
    "section_order": [
        "introduction",
        "technical_overview", 
        "applications",
        "safety_guidelines",
        "conclusion"
    ],
    "supported_categories": ["application", "author", "material", "region", "thesaurus"],
    "thesaurus_terms": [
        "laser cleaning", "ablation", "surface preparation", "contaminant removal",
        "oxide removal", "rust removal", "paint stripping", "coating removal",
        "precision cleaning", "non-contact cleaning", "eco-friendly cleaning"
    ],
    "content_quality_threshold": 0.8,
    "technical_depth_level": "intermediate",
    
    # === API KEY CONFIGURATION (ONLY DEFINED HERE) ===
    "api_key_mappings": {
        "GEMINI": "GEMINI_API_KEY",
        "XAI": "XAI_API_KEY", 
        "DEEPSEEK": "DEEPSEEK_API_KEY"
    },
}

# ---- END CONFIGURATION ----

if __name__ == "__main__":
    print("🚀 Z-Beam Generator - Anti-Bloat Architecture")
    import sys
    try:
        from main import main
        main()
    except ImportError as e:
        print(f"❌ Failed to import main: {e}")
        print("NO FALLBACKS - system must fail fast.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        print("NO FALLBACKS - system must fail fast.")
        sys.exit(1)
