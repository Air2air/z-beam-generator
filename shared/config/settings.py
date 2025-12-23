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
        "micro_generation": 60,     # 1 minute for caption generation  
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
        "cache_validations": False,   # DISABLED: No caching for fresh evaluations
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
            "comprehensive_max_tokens": 4000,  # Increased for comprehensive property discovery with justifications
            "comprehensive_temperature": 0.3,  # Lower temperature for consistent research
            "validation_max_tokens": 4000,  # Increased for machine settings discovery
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

# Production Configuration (formerly prod_config.yaml)
# Consolidated into settings.py for single source of truth
PRODUCTION_CONFIG = {
    "TEST_MODE": False,
    
    "AI_DETECTION": {
        "PROVIDER": "real",
        "ENABLED": True,
        "TARGET_SCORE": 85.0,
        "MAX_ITERATIONS": 5,
        "TIMEOUT": 120,
    },
    
    "API": {
        "USE_MOCK_CLIENTS": False,
        "MAX_CONTENT_LENGTH": 5000,
        "USE_SIMPLE_PROMPTS": False,
        
        # API Response Caching Configuration
        # ENABLED: Cache SEO generation to avoid duplicate API calls
        "RESPONSE_CACHE": {
            "enabled": True,
            "storage_location": "/tmp/z-beam-response-cache",
            "ttl_seconds": 86400,  # 24 hours
            "max_size_mb": 1000,
            "key_strategy": "prompt_hash_with_model",
        },
    },
    
    "TEST_DATA": {
        "MATERIALS": ["Aluminum", "Steel", "Copper", "Brass", "Titanium", "Stainless Steel"],
        "MAX_CONTENT_LENGTH": 5000,
        "USE_SIMPLE_PROMPTS": False,
    },
    
    "TIMEOUTS": {
        "API_CALL": 120,
        "CONTENT_GENERATION": 300,
        "TEST_EXECUTION": 600,
        "FULL_TEST_SUITE": 1800,
    },
    
    "LOGGING": {
        "LEVEL": "WARNING",
        "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "DISABLE_WARNINGS": False,
    },
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
        "max_tokens": 500,  # Increased for micro generation
        "temperature": 0.9,  # Match simple_mode fixed temperature
        "timeout_connect": 60,  # Increased significantly to prevent hangs
        "timeout_read": 180,    # Increased significantly for reliability
        "max_retries": 5,       # More retries for robustness
        "retry_delay": 3.0,     # Longer delays between retries
        "enabled": True,
        "timeout": 60,
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
        "temperature": 0.2,  # Slightly higher for creative micro generation
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
    "gemini": {
        "name": "Google Gemini (Imagen)",
        "type": "gemini_image",
        "env_var": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "model": "imagen-4.0-generate-001",  # Latest Imagen 4
        "max_tokens": 480,  # Prompt length limit for Imagen
        "temperature": 0.0,  # Not used for image generation
        "timeout_connect": 30,
        "timeout_read": 120,  # Image generation can take time
        "max_retries": 3,
        "retry_delay": 2.0,
        "enabled": True,
        "timeout": 120,
        "rate_limit": {
            "requests_per_minute": 30,
            "images_per_minute": 30,
        },
        "image_config": {
            "number_of_images": 1,  # Generate 1-4 images per request
            "aspect_ratio": "16:9",  # Options: 1:1, 3:4, 4:3, 9:16, 16:9
            "person_generation": "allow_adult",  # Options: dont_allow, allow_adult, allow_all
            "image_size": "1K",  # Options: 1K, 2K (Standard/Ultra models)
        },
        "fallback_provider": None,  # FAIL-FAST: No fallbacks allowed
    },
    "claude": {
        "name": "Claude (Anthropic)",
        "type": "openai",  # Uses OpenAI-compatible API
        "env_var": "OPENAI_API_KEY",  # Uses OpenAI key for now
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",  # OpenAI model
        "max_tokens": 550,
        "temperature": 0.815,  # Match learned sweet spot
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
        "text_api_provider": "claude",  # ✅ SWITCHED TO CLAUDE for voice testing
        "priority": 1,
        "enabled": True,  # ENABLED - Only component in frontmatter-only architecture
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
        "generation_modes": {
            "data_only": {"api_provider": "none", "description": "Refresh non-text data from Materials.yaml only"},
            "text_only": {"api_provider": "claude", "description": "Update text fields with Claude AI"},
            "hybrid": {"api_provider": "claude", "description": "Data from Materials.yaml + Claude text generation"},
            "full": {"api_provider": "claude", "description": "Complete AI generation with Claude"}
        },
        "default_mode": "hybrid",  # Recommended mode for most use cases
    },
    # ========================================================================
    # REMOVED COMPONENTS - Frontend extracts from frontmatter structure:
    # - metatags: Extracted from frontmatter metadata
    # - badgesymbol: Extracted from frontmatter material properties  
    # - micro: Extracted from frontmatter.caption section
    # - text: Extracted from frontmatter text fields
    # - table: Extracted from frontmatter.machine_settings section
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


def get_production_config():
    """Get production configuration (formerly prod_config.yaml)."""
    return PRODUCTION_CONFIG


def get_response_cache_config():
    """Get API response cache configuration."""
    return PRODUCTION_CONFIG["API"]["RESPONSE_CACHE"]


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
    # Valid countries: Taiwan, Italy, Indonesia, United States
    if author_country.lower() in ["usa", "united states", "united_states"]:
        base_config["language_patterns"] = "american_english"
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

# =============================================================================
# CONSOLIDATED YAML CONFIGURATIONS
# =============================================================================
# These configurations were previously in separate YAML files.
# Consolidated into settings.py for:
# - Single source of truth
# - No YAML parsing overhead  
# - Type hints and validation in Python
# - Easier maintenance
# =============================================================================

# From config/frontmatter_generation.yaml
FRONTMATTER_GENERATION_CONFIG = {
    'version': '1.0',
    'generation': {
        'mode': 'dynamic',
        'components': ['frontmatter'],
        'output_format': 'yaml'
    },
    # Material abbreviations for standardized naming
    'material_abbreviations': {
        'Fiber Reinforced Polyurethane FRPU': {
            'abbreviation': 'FRPU',
            'full_name': 'Fiber Reinforced Polyurethane'
        },
        'Glass Fiber Reinforced Polymers GFRP': {
            'abbreviation': 'GFRP',
            'full_name': 'Glass Fiber Reinforced Polymers'
        },
        'Carbon Fiber Reinforced Polymer': {
            'abbreviation': 'CFRP',
            'full_name': 'Carbon Fiber Reinforced Polymer'
        },
        'Metal Matrix Composites MMCs': {
            'abbreviation': 'MMCs',
            'full_name': 'Metal Matrix Composites'
        },
        'Ceramic Matrix Composites CMCs': {
            'abbreviation': 'CMCs',
            'full_name': 'Ceramic Matrix Composites'
        },
        'MDF': {
            'abbreviation': 'MDF',
            'full_name': 'Medium Density Fiberboard'
        },
        'Polyvinyl Chloride': {
            'abbreviation': 'PVC',
            'full_name': 'Polyvinyl Chloride'
        },
        'Polytetrafluoroethylene': {
            'abbreviation': 'PTFE',
            'full_name': 'Polytetrafluoroethylene'
        }
    },
    # Category-specific thermal property mapping
    'thermal_property_mapping': {
        'wood': {
            'field': 'thermalDestructionPoint',
            'label': 'Decomposition Point',
            'description': 'Temperature where pyrolysis (thermal decomposition) begins',
            'scientific_process': 'Pyrolysis',
            'yaml_field': 'thermalDestructionPoint'
        },
        'ceramic': {
            'field': 'sinteringPoint',
            'label': 'Sintering/Decomposition Point',
            'description': 'Temperature where ceramic particles fuse or decompose',
            'scientific_process': 'Sintering or Decomposition',
            'yaml_field': 'thermalDestruction'
        },
        'stone': {
            'field': 'thermalDegradationPoint',
            'label': 'Thermal Degradation Point',
            'description': 'Temperature where mineral structure breaks down',
            'scientific_process': 'Thermal Degradation',
            'yaml_field': 'thermalDestructionPoint'
        },
        'composite': {
            'field': 'degradationPoint',
            'label': 'Degradation Point',
            'description': 'Temperature where polymer matrix decomposes',
            'scientific_process': 'Polymer Decomposition',
            'yaml_field': 'thermalDestructionPoint'
        },
        'plastic': {
            'field': 'degradationPoint',
            'label': 'Degradation Point',
            'description': 'Temperature where polymer chains break down',
            'scientific_process': 'Polymer Decomposition',
            'yaml_field': 'thermalDestructionPoint'
        },
        'glass': {
            'field': 'softeningPoint',
            'label': 'Softening Point',
            'description': 'Temperature where glass transitions from rigid to pliable state',
            'scientific_process': 'Glass Transition',
            'yaml_field': 'thermalDestructionPoint'
        },
        'metal': {
            'field': 'thermalDestructionPoint',
            'label': 'Thermal Destruction Point',
            'description': 'Temperature where solid metal transitions to liquid phase',
            'scientific_process': 'Phase Transition',
            'yaml_field': 'thermalDestruction'
        },
        'semiconductor': {
            'field': 'thermalDestructionPoint',
            'label': 'Thermal Destruction Point',
            'description': 'Temperature where crystalline structure melts',
            'scientific_process': 'Phase Transition',
            'yaml_field': 'thermalDestruction'
        },
        'masonry': {
            'field': 'thermalDegradationPoint',
            'label': 'Thermal Degradation Point',
            'description': 'Temperature where structural integrity fails',
            'scientific_process': 'Thermal Degradation',
            'yaml_field': 'thermalDestructionPoint'
        }
    }
}

# From config/metadata_delimiting.yaml
METADATA_DELIMITING_CONFIG = {
    'delimiters': {
        'start': '---',
        'end': '---'
    },
    'format': 'yaml'
}

# From config/pipeline_config.yaml  
PIPELINE_CONFIG = {
    'stages': ['validation', 'generation', 'quality'],
    'validation': {
        'pre_generation': True,
        'post_generation': True
    }
}

# Accessor functions for backward compatibility
def get_frontmatter_generation_config():
    """Get frontmatter generation configuration."""
    return FRONTMATTER_GENERATION_CONFIG

def get_metadata_delimiting_config():
    """Get metadata delimiting configuration."""
    return METADATA_DELIMITING_CONFIG

def get_pipeline_config():
    """Get pipeline configuration."""
    return PIPELINE_CONFIG

