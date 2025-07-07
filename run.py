#!/usr/bin/env python3
"""
Z-Beam Generator Entry Point
Initializes GlobalConfigManager and starts generation
"""

# ---- USER CONFIGURATION (edit here) ----

# All provider and model config must be accessed via GlobalConfigManager
PROVIDER_MODELS = {
    "GEMINI": {
        "model": "gemini-1.5-pro",
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    },
    "XAI": {
        "model": "grok-2-1212",
        "url_template": "https://api.x.ai/v1/chat/completions",
    },
    "DEEPSEEK": {
        "model": "deepseek-chat",
        "url_template": "https://api.deepseek.com/v1/chat/completions",
    },
}

# User configuration for article generation
USER_CONFIG = {
    "material": "Magnesium",
    "category": "Material", 
    "file_name": "magnesium_laser_cleaning.mdx",
    "generator_provider": "DEEPSEEK",        
    "optimization_provider": "DEEPSEEK",     
    "author": "todd_dunning.mdx",
    "force_regenerate": True,
    "provider_models": PROVIDER_MODELS,
    "max_article_words": 800,
    "api_timeout": 60,
    "max_tokens": 4096,
    "overall_timeout": 300,
    "generator_version": "2.0.0-single-pass",
    "default_section_words": 150,
    "supported_categories": ["application", "author", "material", "region", "thesaurus"],
    "sections_directory": "prompts",
    "output_directory": "output",
    "temperature": 0.7,
    "api_key_mappings": {
        "GEMINI": "GEMINI_API_KEY",
        "XAI": "XAI_API_KEY", 
        "DEEPSEEK": "DEEPSEEK_API_KEY"
    },
}

# ---- END CONFIGURATION ----

if __name__ == "__main__":
    print("🚀 Z-Beam Generator - Anti-Bloat Architecture")
    
    try:
        # INITIALIZE GlobalConfigManager FIRST
        from config.global_config import GlobalConfigManager
        
        print("🔧 Initializing GlobalConfigManager...")
        GlobalConfigManager.initialize(USER_CONFIG)
        print("✅ GlobalConfigManager initialized")
        
        # NOW import and run main
        from main import main
        main()
        
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        print("💡 Check that all required modules are present")
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        print("NO FALLBACKS - system must fail fast.")
