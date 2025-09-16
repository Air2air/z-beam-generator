#!/usr/bin/env python3
"""
Z-Beam Generator - User Configuration & Quick Start Guide

This file contains only the user-configurable settings and instructions.
The main application logic has been moved to main_runner.py for better organization.

═══════════════════════════════════════════════════════════════════════════════
📋 QUICK START GUIDE
═══════════════════════════════════════════════════════════════════════════════

🎯 GENERATE CONTENT:
  python3 run.py --material "Aluminum"     # Specific material
  python3 run.py --all                     # All materials
  python3 run.py --content-batch           # First 8 categories

🧪 TESTING & VALIDATION:
  python3 run.py --test                    # Full test suite
  python3 run.py --test-api                # Test API connections
  python3 run.py --check-env               # Health check
  python3 run.py --list-materials          # List available materials

⚙️  SYSTEM MANAGEMENT:
  python3 run.py --config                  # Show configuration
  python3 run.py --cache-stats             # Cache performance
  python3 run.py --preload-cache           # Optimize performance
  python3 run.py --clean                   # Clean generated content

🚀 OPTIMIZATION:
  python3 run.py --optimize text           # Optimize specific component

💡 For complete command reference: python3 run.py --help

═══════════════════════════════════════════════════════════════════════════════
📝 USER CONFIGURATION SETTINGS
═══════════════════════════════════════════════════════════════════════════════
"""

# API Provider Configuration - USER SETTABLE
# Configure which API providers to use for different operations
# FAIL-FAST: Each provider must be explicitly configured with valid credentials
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "type": "deepseek",
        "env_var": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "max_tokens": 4000,  # Default - will be overridden by component-specific settings
        "temperature": 0.1,  # Default - will be overridden by component-specific settings
        "timeout_connect": 30,  # Increased for better reliability with large prompts
        "timeout_read": 120,    # Increased for better reliability with complex content
        "max_retries": 5,       # More retries for robustness
        "retry_delay": 2.0,     # Longer delays between retries
        "enabled": True,
        "timeout": 30,
        "rate_limit": {
            "requests_per_minute": 60,
            "tokens_per_minute": 30000,
        },
        "fallback_provider": None,  # FAIL-FAST: No fallbacks allowed
    },
    "winston": {
        "name": "Winston AI Detection",
        "type": "winston", 
        "env_var": "WINSTON_API_KEY",
        "base_url": "https://api.gowinston.ai",
        "model": "winston-ai-detector",
        "max_tokens": 1000,
        "temperature": 0.1,
        "timeout_connect": 30,  # Updated for consistency
        "timeout_read": 120,    # Updated for consistency
        "max_retries": 5,       # Updated for consistency
        "retry_delay": 2.0,     # Updated for consistency
        "enabled": True,
        "timeout": 30,
        "rate_limit": {
            "requests_per_minute": 100,
            "tokens_per_minute": 10000,
        },
        "fallback_provider": None,  # FAIL-FAST: No fallbacks allowed
    },
}

# Component Configuration - USER SETTABLE
# Enable/disable components and set their generation priority
# Lower priority numbers = generated first
COMPONENT_CONFIG = {
    "frontmatter": {
        "api_provider": "deepseek",
        "priority": 1,
        "enabled": False,  # ENABLED for frontmatter generation
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "metatags": {
        "api_provider": "deepseek",
        "priority": 2,
        "enabled": False,  # DISABLED for focused batch test
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "badgesymbol": {
        "api_provider": "none",  # Static/deterministic generation
        "priority": 3,
        "enabled": False,  # DISABLED for focused batch test
        "data_provider": "static",  # No API calls needed, deterministic
    },
    "bullets": {
        "api_provider": "deepseek",
        "priority": 4,
        "enabled": False,  # DISABLED for focused batch test
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "caption": {
        "api_provider": "deepseek",
        "priority": 5,
        "enabled": False,  # DISABLED for focused batch test
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "text": {
        "api_provider": "deepseek",
        "priority": 6,
        "enabled": False,  # ENABLED for text generation
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "table": {
        "api_provider": "none",  # Static/deterministic generation
        "priority": 7,
        "enabled": True,  # DISABLED for focused batch test
        "data_provider": "static",  # No API calls needed, no frontmatter dependency
    },
    "tags": {
        "api_provider": "deepseek",
        "priority": 8,
        "enabled": False,  # DISABLED for focused batch test
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "jsonld": {
        "api_provider": "deepseek",  # Extracts from frontmatter, no AI needed
        "priority": 9,
        "enabled": False,  # DISABLED for focused batch test
        "data_provider": "hybrid",  # Pure frontmatter extraction
    },
    "author": {
        "api_provider": "none",  # Static component, no API needed
        "priority": 10,
        "enabled": False,  # DISABLED for focused batch test
        "data_provider": "static",  # Static data, no dependencies
    },
}

# AI Detection Configuration - USER SETTABLE
# Configure AI detection behavior - FAIL-FAST: No fallbacks allowed
AI_DETECTION_CONFIG = {
    "enabled": True,
    "provider": "winston",  # FAIL-FAST: Must be explicitly provided, no fallbacks
    "target_score": 70.0,
    "max_iterations": 3,
    "improvement_threshold": 5.0,
    "timeout": 30,
    "retry_attempts": 3,  # FAIL-FAST: Validate configuration, then fail immediately
}


# Optimizer Configuration - USER SETTABLE
# Modify these settings to customize optimizer behavior
OPTIMIZER_CONFIG = {
    # AI Detection Service Configuration
    "ai_detection_service": {
        "enabled": True,
        "version": "1.0.0",
        "settings": {
            "providers": {
                "winston": {
                    "type": "winston",
                    "enabled": True,
                    "target_score": 70.0,
                    "max_iterations": 5,
                },
                "mock": {
                    "type": "mock",
                    "enabled": False,  # Only for testing
                }
            },
            # Global AI detection settings
            "target_score": 70.0,
            "max_iterations": 5,
            "improvement_threshold": 3.0,
            "cache_ttl_hours": 1,
            "max_workers": 4,
            "detection_threshold": 0.7,
            "confidence_threshold": 0.8,
            "allow_mocks_for_testing": False,  # Production: False
        }
    },

    # Iterative Workflow Service Configuration
    "iterative_workflow_service": {
        "enabled": True,
        "version": "1.0.0",
        "settings": {
            "max_iterations": 10,
            "quality_threshold": 0.9,
            "time_limit_seconds": 300,
            "convergence_threshold": 0.01,
            "backoff_factor": 2.0,
            "min_delay": 0.1,
            "max_delay": 10.0,
        }
    },

    # Optimization Configuration
    "optimization": {
        "target_score": 75.0,
        "max_iterations": 5,
        "improvement_threshold": 3.0,
        "time_limit_seconds": None,
        "convergence_threshold": 0.01,
    },

    # Text Optimization Settings
    "text_optimization": {
        "dynamic_prompts": {
            "enabled": True,
            "enhancement_flags": {
                "conversational_boost": True,
                "natural_language_patterns": True,
                "cultural_adaptation": True,
                "sentence_variability": True,
                "ai_detection_focus": True,
            }
        },
        "quality_scorer": {
            "human_threshold": 75.0,
            "technical_accuracy_weight": 0.3,
            "author_authenticity_weight": 0.3,
            "readability_weight": 0.2,
            "human_believability_weight": 0.2,
        }
    },

    # Author Personas Configuration
    "personas": {
        "taiwan": {
            "word_limit": 380,
            "language_patterns": {
                "signature_phrases": [
                    "systematic approach enables",
                    "careful analysis shows",
                    "methodical investigation reveals"
                ]
            }
        },
        "italy": {
            "word_limit": 450,
            "language_patterns": {
                "signature_phrases": [
                    "precision meets innovation",
                    "technical elegance",
                    "meticulous approach"
                ]
            }
        },
        "indonesia": {
            "word_limit": 250,
            "language_patterns": {
                "signature_phrases": [
                    "practical applications",
                    "efficient solutions",
                    "renewable energy focus"
                ]
            }
        },
        "usa": {
            "word_limit": 320,
            "language_patterns": {
                "signature_phrases": [
                    "innovative solutions",
                    "efficient processes",
                    "conversational expertise"
                ]
            }
        }
    },

    # Logging Configuration
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    },

    # Test Mode Configuration
    "test_mode": False,
}

# END OF USER-CONTROLLED CONFIGURATION
# =================================================================================

# Configuration Helper Functions
def get_optimizer_config(service_name: str = None):
    """Get optimizer configuration for a specific service or all services."""
    if service_name:
        return OPTIMIZER_CONFIG.get(service_name, {})
    return OPTIMIZER_CONFIG


def get_ai_detection_config():
    """Get AI detection configuration."""
    return get_optimizer_config("ai_detection_service")


def get_workflow_config():
    """Get workflow configuration."""
    return get_optimizer_config("iterative_workflow_service")


def get_optimization_config():
    """Get optimization configuration."""
    return get_optimizer_config("optimization")


def get_text_optimization_config():
    """Get text optimization configuration."""
    return get_optimizer_config("text_optimization")


def get_persona_config(country: str = None):
    """Get persona configuration for a specific country or all personas."""
    personas = get_optimizer_config("personas")
    if country:
        return personas.get(country.lower(), {})
    return personas


def get_dynamic_config_for_component(component_type: str, material_data: dict = None):
    """Get dynamic configuration for content generation."""
    base_config = COMPONENT_CONFIG.get(component_type, {})

    if material_data:
        # Apply material-specific optimizations
        material_name = material_data.get("name", "").lower()

        # Special handling for different material types
        if "steel" in material_name or "iron" in material_name:
            base_config["temperature"] = 0.6  # More precise for metals
        elif "plastic" in material_name or "polymer" in material_name:
            base_config["temperature"] = 0.8  # More creative for plastics
        elif "ceramic" in material_name:
            base_config["temperature"] = 0.5  # Very precise for ceramics

    return base_config


def create_dynamic_ai_detection_config(
    content_type: str = "technical",
    author_country: str = "usa",
    content_length: int = 1000,
):
    """Create dynamic AI detection configuration based on content parameters."""
    base_config = AI_DETECTION_CONFIG.copy()

    # Adjust configuration based on content type
    if content_type == "technical":
        base_config["target_score"] = 75.0
    elif content_type == "creative":
        base_config["target_score"] = 65.0
    else:
        base_config["target_score"] = 70.0

    # Adjust based on author country
    if author_country.lower() == "usa":
        base_config["language_patterns"] = "american_english"
    elif author_country.lower() == "uk":
        base_config["language_patterns"] = "british_english"
    else:
        base_config["language_patterns"] = "international_english"

    # Adjust based on content length
    if content_length < 500:
        base_config["min_text_length"] = 100
    elif content_length > 2000:
        base_config["min_text_length"] = 500
    else:
        base_config["min_text_length"] = 200

    return base_config


# =================================================================================
# MAIN ENTRY POINT - Delegates to main_runner.py
# =================================================================================

if __name__ == "__main__":
    # Import and run the main application logic
    from main_runner import main
    import sys
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
