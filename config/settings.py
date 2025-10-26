#!/usr/bin/env python3
"""
Z-Beam Generator - Centralized Configuration Settings

This module contains ALL user-configurable settings for the Z-Beam Generator.
Extracted from run.py for better organization and maintainability.

All configuration dictionaries and accessor functions are centralized here.
"""

import re

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 GLOBAL CONFIGURATION SETTINGS - USER SETTABLE
# ═══════════════════════════════════════════════════════════════════════════════

# Global Timeout and Operational Settings - USER SETTABLE
# All timeout values, retry settings, and operational parameters
GLOBAL_OPERATIONAL_CONFIG = {
    # Default timeout settings for scripts and batch operations
    "batch_timeouts": {
        "default_per_material": 120,  # 2 minutes per material
        "caption_generation": 60,     # 1 minute for caption generation  
        "frontmatter_generation": 60, # 1 minute for frontmatter
        "jsonld_generation": 120      # 2 minutes for JSON-LD
    },
    
    # Enhanced API Client Default Settings
    "enhanced_client_defaults": {
        "connect_timeout": 15.0,      # Increased for slow networks
        "read_timeout": 90.0,         # Increased for complex content generation
        "total_timeout": 120.0,       # Maximum total request time
        "max_retries": 5,             # More retries for intermittent issues
        "base_retry_delay": 2.0,      # Longer base delay
        "max_retry_delay": 30.0,      # Cap exponential backoff
        "jitter_factor": 0.1,         # Add randomness to prevent thundering herd
    },
    
    # Invisible Pipeline Integration Settings
    "pipeline_integration": {
        "enabled": True,              # Enable invisible pipeline during content generation
        "silent_mode": False,         # Show verbose AI research logging by default
        "max_validation_time": 15,    # Maximum time to spend on validation (seconds) - increased for AI
        "cache_validations": True,    # Cache validation results to avoid redundant work
        "auto_improve_frontmatter": True,  # Automatically improve frontmatter quality
        "batch_validation": True,     # Run batch validation for --all operations
        "quality_threshold": 0.6,     # Minimum quality score to pass validation
        "ai_validation_enabled": True, # Enable AI cross-checking of critical properties
        "ai_validation_critical_only": True, # Only validate critical properties with AI (faster)
        "ai_confidence_threshold": 0.7, # Minimum AI confidence for passing validation
        "ai_verbose_logging": True,   # Enable detailed AI research call logging
        "ai_log_prompts": True,       # Log AI prompts and responses
        "ai_log_timing": True,        # Log AI request timing information
        "hierarchical_validation_enabled": True, # Enable hierarchical validation (Categories.yaml → Materials.yaml → Frontmatter)
        "hierarchical_validation_pre_generation": True, # Run hierarchical validation before content generation
        "hierarchical_validation_post_generation": True, # Run hierarchical validation after content generation
    },
    
    # Data Completeness Enforcement
    "data_completeness": {
        "enforce_before_generation": False,  # Set to True to block generation if data incomplete
        "warn_before_generation": True,     # Show warnings about incomplete data
        "completeness_threshold": 95.0,     # Minimum acceptable completeness %
        "block_on_critical_gaps": False,    # Block if critical properties missing
        "show_action_plan_link": True,      # Direct users to DATA_COMPLETION_ACTION_PLAN.md
    },
    
    # Research component API settings
    "research_defaults": {
        "property_researcher": {
            "api_timeout": 30,
            "max_tokens": 500,
            "temperature": 0.1,       # Low temperature for factual accuracy
        },
        "property_value_researcher": {
            "comprehensive_max_tokens": 1500,
            "comprehensive_temperature": 0.3,  # Lower temperature for consistent research
            "validation_max_tokens": 1200,
            "validation_temperature": 0.3,
        }
    },
    
    # Component-specific generation settings
    "component_generation": {
        "frontmatter": {
            "max_tokens": 4000,
            "temperature": 0.3,
        },
        "test_connection": {
            "max_tokens": 10,           # Test requests
        }
    },
    
    # Validation and utility settings
    "validation": {
        "layer_validator_recovery_timeout": 300,   # 5 minutes
        "quality_validator_recovery_timeout": 600, # 10 minutes
        "quality_validator_short_timeout": 300,    # 5 minutes
    },
    
    # No circuit breaker fallbacks allowed in fail-fast architecture
}

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
    "grok": {
        "name": "Grok",
        "type": "grok",
        "env_var": "GROK_API_KEY",
        "base_url": "https://api.x.ai",
        "model": "grok-4-fast",
        "max_tokens": 550,  # Final optimized setting to consistently produce 400-500 total words
        "temperature": 0.2,  # Slightly higher for creative caption generation
        "timeout_connect": 30,
        "timeout_read": 120,
        "max_retries": 5,
        "retry_delay": 2.0,
        "enabled": True,
        "timeout": 30,
        "rate_limit": {
            "requests_per_minute": 60,
            "tokens_per_minute": 30000,
        },
        "fallback_provider": None,  # FAIL-FAST: No fallbacks allowed
    },
}

# Component Configuration - FRONTMATTER-ONLY ARCHITECTURE
# Only frontmatter component is enabled - all content consolidated into frontmatter YAML
# Frontend extracts specific components from frontmatter structure
COMPONENT_CONFIG = {
    "frontmatter": {
        "api_provider": "deepseek",  # ✅ API-BASED COMPONENT (for non-text fields)
        "text_api_provider": "grok",  # ✅ TEXT-ONLY COMPONENT (for text fields with linguistic technicalities)
        "priority": 1,
        "enabled": True,  # ENABLED - Only component in frontmatter-only architecture
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
        "generation_modes": {
            "data_only": {"api_provider": "none", "description": "Refresh non-text data from Materials.yaml only"},
            "text_only": {"api_provider": "grok", "description": "Update text fields with Grok AI"},
            "hybrid": {"api_provider": "grok", "description": "Data from Materials.yaml + Grok text generation"},
            "full": {"api_provider": "deepseek", "description": "Complete AI generation with DeepSeek"}
        },
        "default_mode": "hybrid",  # Recommended mode for most use cases
    },
    # ========================================================================
    # REMOVED COMPONENTS - Frontend extracts from frontmatter structure:
    # - metatags: Extracted from frontmatter metadata
    # - badgesymbol: Extracted from frontmatter material properties  
    # - caption: Extracted from frontmatter.caption section
    # - text: Extracted from frontmatter text fields
    # - table: Extracted from frontmatter.machineSettings section
    # - jsonld: Extracted from frontmatter structured data
    # - author: Extracted from frontmatter.author section
    # ========================================================================
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
        "config": {
            "providers": {
                "winston": {
                    "type": "winston",
                    "enabled": True,
                    "target_score": 70.0,
                    "max_iterations": 5,
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
        }
    },

    # Iterative Workflow Service Configuration
    "iterative_workflow_service": {
        "enabled": True,
        "version": "1.0.0",
        "config": {
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
        "level": "DEBUG",              # DEBUG level for detailed AI research logging
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "ai_research_logger": True,    # Enable dedicated AI research logger
    },

    # Test Mode Configuration
    "test_mode": False,
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION ACCESSOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_optimizer_config(service_name: str = None):
    """Get optimizer configuration for a specific service or all services."""
    if service_name:
        if service_name not in OPTIMIZER_CONFIG:
            raise KeyError(f"Service '{service_name}' not found in OPTIMIZER_CONFIG - no fallback allowed")
        return OPTIMIZER_CONFIG[service_name]
    return OPTIMIZER_CONFIG


def get_global_operational_config():
    """Get global operational configuration."""
    return GLOBAL_OPERATIONAL_CONFIG


def get_batch_timeout(operation_type: str = "default_per_material"):
    """Get timeout for batch operations."""
    if operation_type not in GLOBAL_OPERATIONAL_CONFIG["batch_timeouts"]:
        raise KeyError(f"Operation type '{operation_type}' not found in batch_timeouts - no fallback allowed")
    return GLOBAL_OPERATIONAL_CONFIG["batch_timeouts"][operation_type]


def get_enhanced_client_config():
    """Get enhanced API client configuration."""
    return GLOBAL_OPERATIONAL_CONFIG["enhanced_client_defaults"]


def get_research_config(component_name: str = None):
    """Get research component configuration."""
    if component_name:
        if component_name not in GLOBAL_OPERATIONAL_CONFIG["research_defaults"]:
            raise KeyError(f"Research component '{component_name}' not found in configuration - no fallback allowed")
        return GLOBAL_OPERATIONAL_CONFIG["research_defaults"][component_name]
    return GLOBAL_OPERATIONAL_CONFIG["research_defaults"]


def get_component_generation_config(component_name: str = None):
    """Get component generation configuration."""
    if component_name:
        if component_name not in GLOBAL_OPERATIONAL_CONFIG["component_generation"]:
            raise KeyError(f"Component '{component_name}' not found in generation configuration - no fallback allowed")
        return GLOBAL_OPERATIONAL_CONFIG["component_generation"][component_name]
    return GLOBAL_OPERATIONAL_CONFIG["component_generation"]


def get_validation_config():
    """Get validation configuration."""
    return GLOBAL_OPERATIONAL_CONFIG["validation"]


def get_api_providers():
    """Get API providers configuration."""
    return API_PROVIDERS


def get_api_config_fallbacks():
    """Get API configuration fallback values (deprecated - will be removed)."""
    # This function exists for backward compatibility only
    # All configurations should now use the centralized approach
    return {
        "max_tokens": 4000,
        "temperature": 0.7, 
        "timeout_connect": 10,
        "timeout_read": 30,
        "max_retries": 3,
        "retry_delay": 1.0,
    }


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
        country_key = country.lower()
        if country_key not in personas:
            raise KeyError(f"Country '{country}' not found in personas config - no fallback allowed")
        return personas[country_key]
    return personas


def get_dynamic_config_for_component(component_type: str, material_data: dict = None):
    """Get dynamic configuration for content generation."""
    if component_type not in COMPONENT_CONFIG:
        raise KeyError(f"Component type '{component_type}' not found in COMPONENT_CONFIG - no fallback allowed")
    base_config = COMPONENT_CONFIG[component_type].copy()

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


def extract_numeric_value(value):
    """Extract numeric value from various formats, including Shore hardness scales."""
    import re
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove common units and multipliers first
        cleaned = value.replace(',', '')
        
        # Handle Shore hardness ranges specifically (Shore D 60-70, Shore A 10-20)
        shore_range_match = re.search(r'Shore\s+[AD]\s+(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', cleaned, re.IGNORECASE)
        if shore_range_match:
            # Return midpoint of the range
            min_val = float(shore_range_match.group(1))
            max_val = float(shore_range_match.group(2))
            return (min_val + max_val) / 2.0
        
        # Handle Shore hardness single values (Shore A 10, Shore D 90)
        shore_match = re.search(r'Shore\s+[AD]\s+(\d+(?:\.\d+)?)', cleaned, re.IGNORECASE)
        if shore_match:
            return float(shore_match.group(1))
        
        # Handle scientific notation markers like ×10⁻⁶
        if '×10⁻' in cleaned:
            parts = cleaned.split('×10⁻')
            if len(parts) == 2:
                try:
                    base = float(parts[0])
                    exp = int(parts[1].split('/')[0])  # Handle cases like ×10⁻⁶/K
                    return base * (10 ** -exp)
                except ValueError:
                    pass
        
        # Handle regular scientific notation
        if 'e-' in cleaned.lower() or 'e+' in cleaned.lower():
            try:
                return float(cleaned.split()[0])
            except ValueError:
                pass
        
        # Extract first number from string
        number_match = re.search(r'-?\d+\.?\d*', cleaned)
        if number_match:
            try:
                return float(number_match.group())
            except ValueError:
                pass
    
    return None
