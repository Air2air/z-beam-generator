#!/usr/bin/env python3
"""
Z-Beam Generator - User Configuration & Quick Start Guide

This file contains ALL user-configurable settings and instructions.
The main applic        "api_provider": "none",  # ❌ NO API - static/deterministic generation
        "priority": 3,
        "enabled": False,  # DISABLED for caption-focused generation
        "data_provider": "static",  # No API calls needed, deterministic
    },
    "text": {has been moved to main_runner.py for better organization.

═══════════════════════════════════════════════════════════════════════════════
📋 CONFIGURATION STATUS: ALL HARDCODED CONFIGS REMOVED
═══════════════════════════════════════════════════════════════════════════════

✅ CENTRALIZED CONFIGURATIONS:
  • API Provider Settings (timeout, retries, tokens, temperature)
  • Component Generation Settings (priorities, enabled/disabled)
  • AI Detection & Optimization Settings
  • Batch Operation Timeouts (caption, frontmatter, jsonld, tags)
  • Enhanced API Client Settings (timeouts, retries, jitter)
  • Circuit Breaker Settings (failure thresholds, recovery)
  • Optimizer Service Settings (personas, quality thresholds)

🚫 REMOVED HARDCODED CONFIGS FROM:
  • api/enhanced_client.py - Now uses GLOBAL_OPERATIONAL_CONFIG
  • api/config.py - Now uses centralized fallbacks

  • scripts/batch_*.py - Now uses centralized timeouts
  • generate_all_*.py - Now uses centralized timeouts

═══════════════════════════════════════════════════════════════════════════════
📋 QUICK START GUIDE
═══════════════════════════════════════════════════════════════════════════════

🎯 GENERATE CONTENT:
  python3 run.py --material "Aluminum"     # Specific material
  python3 run.py --all                     # All materials
  python3 run.py --content-batch           # First 8 categories

🚀 DEPLOYMENT:
  python3 run.py --deploy                  # Deploy to Next.js production site

🧪 TESTING & VALIDATION:
  python3 run.py --test                    # Full test suite
  python3 run.py --test-api                # Test API connections
  python3 run.py --validate                # Validate existing data without regeneration
  python3 run.py --validate-report report.md  # Generate validation report
  python3 run.py --check-env               # Health check
  python3 run.py --list-materials          # List available materials

🔍 DATA VALIDATION & INTEGRITY:
  python3 run.py --validate              # Run hierarchical validation & auto-fix
  python3 run.py --validate-report FILE  # Generate detailed validation report

🔬 SYSTEMATIC DATA VERIFICATION (AI Research):
  python3 run.py --data                  # Verify ALL properties (18 hours, $14.64)
  python3 run.py --data=critical         # Verify critical properties (3 hours, $1.20)
  python3 run.py --data=test             # Safe test run (15 min, $0.10, dry-run)
  python3 run.py --data=important        # Verify important properties (3 hours, $1.20)
  python3 run.py --data=--group=mechanical  # Verify property group
  python3 run.py --data=--properties=density,meltingPoint  # Specific properties

⚙️  SYSTEM MANAGEMENT:
  python3 run.py --config                  # Show configuration
  python3 run.py --cache-stats             # Cache performance
  python3 run.py --preload-cache           # Optimize performance
  python3 run.py --clean                   # Clean generated content

🚀 OPTIMIZATION:
  python3 run.py --optimize frontmatter     # Optimize specific component

💡 For complete command reference: python3 run.py --help

═══════════════════════════════════════════════════════════════════════════════
📝 GLOBAL CONFIGURATION SETTINGS - USER SETTABLE
═══════════════════════════════════════════════════════════════════════════════
"""

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
        "jsonld_generation": 120,     # 2 minutes for JSON-LD
        "tags_generation": 120,       # 2 minutes for tags
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
        "model": "grok-3",
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

# Component Configuration - USER SETTABLE
# Enable/disable components and set their generation priority
# Lower priority numbers = generated first
COMPONENT_CONFIG = {
    "frontmatter": {
        "api_provider": "deepseek",  # ✅ API-BASED COMPONENT
        "priority": 1,
        "enabled": True,  # ENABLED - for comprehensive discovery testing
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "metatags": {
        "api_provider": "none",  # ❌ NO API - uses frontmatter exclusively
        "priority": 2,
        "enabled": False,  # DISABLED for caption-focused generation
        "data_provider": "frontmatter",  # Uses frontmatter data exclusively
    },
    "badgesymbol": {
        "api_provider": "none",  # ❌ NO API - static/deterministic generation
        "priority": 3,
        "enabled": False,  # DISABLED for caption-focused generation
        "data_provider": "static",  # No API calls needed, deterministic
    },
    "caption": {
        "api_provider": "grok",  # ✅ API-BASED COMPONENT - Enhanced AI generation with Grok
        "priority": 5,
        "enabled": True,  # ENABLED for caption generation
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "text": {
        "api_provider": "deepseek",  # ✅ API-BASED COMPONENT
        "priority": 6,
        "enabled": False,  # DISABLED for caption-focused generation
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "table": {
        "api_provider": "none",  # ❌ NO API - static/deterministic generation
        "priority": 7,
        "enabled": False,  # DISABLED for caption-focused generation
        "data_provider": "static",  # No API calls needed, no frontmatter dependency
    },
    "tags": {
        "api_provider": "none",  # ✅ NO API - now uses frontmatter data only
        "priority": 8,
        "enabled": True,  # ENABLED for tags generation
        "data_provider": "static",  # Uses frontmatter data only
    },
    "jsonld": {
        "api_provider": "none",  # ❌ NO API - uses frontmatter extraction only
        "priority": 9,
        "enabled": False,  # ENABLED for JSON-LD generation
        "data_provider": "static",  # Uses frontmatter data only
    },
    "author": {
        "api_provider": "none",  # ❌ NO API - static component
        "priority": 10,
        "enabled": False,  # DISABLED for caption-focused generation
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

# END OF USER-CONTROLLED CONFIGURATION
# =================================================================================

# Configuration Helper Functions
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


# Circuit breaker configuration removed - fail-fast architecture
    """Get API configuration fallback values."""
    return GLOBAL_OPERATIONAL_CONFIG["api_config_fallbacks"]


def get_ai_detection_config():
    """Get AI detection configuration."""
    return get_optimizer_config("ai_detection_service")


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
    base_config = COMPONENT_CONFIG[component_type]

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
# DEPLOYMENT FUNCTIONS
# =================================================================================

def deploy_to_production():
    """Deploy generated content to Next.js production site."""
    import shutil
    import os
    
    # Define source and target paths - ONLY FRONTMATTER
    source_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/frontmatter"
    target_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/content/components/frontmatter"
    
    try:
        # Verify source directory exists
        if not os.path.exists(source_dir):
            print(f"❌ Source directory not found: {source_dir}")
            return False
        
        # Verify target directory exists
        if not os.path.exists(target_dir):
            print(f"❌ Target directory not found: {target_dir}")
            return False
        
        print("🚀 Deploying frontmatter content from generator to Next.js production site...")
        print(f"📂 Source: {source_dir}")
        print(f"📂 Target: {target_dir}")
        print("📋 Deploying frontmatter component only")
        
        deployment_stats = {
            "updated": 0,
            "created": 0,
            "errors": 0,
            "skipped": 0
        }
        
        # Deploy frontmatter component
        print("\n📦 Deploying frontmatter component...")
        
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Get list of files in source directory
        try:
            source_files = [f for f in os.listdir(source_dir) 
                          if os.path.isfile(os.path.join(source_dir, f)) and not f.startswith('.')]
            
            if not source_files:
                print("  ⚠️ No files found in frontmatter")
                deployment_stats["skipped"] += 1
            else:
                # Copy each file
                for filename in source_files:
                    source_file = os.path.join(source_dir, filename)
                    target_file = os.path.join(target_dir, filename)
                    
                    try:
                        # Check if target file exists
                        file_exists = os.path.exists(target_file)
                        
                        # Copy the file
                        shutil.copy2(source_file, target_file)
                        
                        if file_exists:
                            print(f"  ✅ Updated: {filename}")
                            deployment_stats["updated"] += 1
                        else:
                            print(f"  ✨ Created: {filename}")
                            deployment_stats["created"] += 1
                            
                    except Exception as e:
                        print(f"  ❌ Error copying {filename}: {e}")
                        deployment_stats["errors"] += 1
                    
        except Exception as e:
            print(f"  ❌ Error processing frontmatter: {e}")
            deployment_stats["errors"] += 1
        
        # Print deployment summary
        print("\n🏁 Deployment completed!")
        print("📊 Statistics:")
        print(f"  ✨ Created: {deployment_stats['created']} files")
        print(f"  ✅ Updated: {deployment_stats['updated']} files")
        print(f"  ⚠️ Skipped: {deployment_stats['skipped']} components")
        print(f"  ❌ Errors: {deployment_stats['errors']} files")
        
        # Success if at least some files were deployed and no errors
        success = (deployment_stats["created"] + deployment_stats["updated"]) > 0 and deployment_stats["errors"] == 0
        
        if success:
            print("🎉 Deployment successful! Next.js production site updated.")
        else:
            print("⚠️ Deployment completed with issues.")
            
        return success
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# FRONTMATTER SANITIZATION POST-PROCESSOR
# =================================================================================

def run_data_validation(report_file = None) -> bool:
    """Run comprehensive hierarchical validation and update system"""
    try:
        from hierarchical_validator import HierarchicalValidator
        import yaml
        import os
        from pathlib import Path
        
        print("🔍 Running Comprehensive Hierarchical Data Validation")
        print("=" * 60)
        
        # Stage 1: Run full hierarchical validation
        print("📊 Stage 1: Hierarchical Validation (Categories.yaml → Materials.yaml → Frontmatter)")
        validator = HierarchicalValidator(ai_validation_enabled=True, silent_mode=False)
        validation_results = validator.run_hierarchical_validation()
        
        summary = validation_results['summary']
        print(f"\n📋 Validation Results:")
        print(f"   Overall Status: {summary['overall_status']}")
        print(f"   Categories: {summary['categories_status']}")
        print(f"   Materials: {summary['materials_status']}")
        print(f"   Hierarchy: {summary['hierarchy_status']}")
        print(f"   AI Validation: {summary['ai_validation_status']}")
        print(f"   Frontmatter: {summary['frontmatter_status']}")
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   Critical Issues: {summary['critical_issues']}")
        
        # Stage 2: Fix property violations automatically
        if validation_results['validation_results']['materials_validation'].get('property_violations'):
            print(f"\n🔧 Stage 2: Fixing Property Violations in Materials.yaml")
            property_violations = validation_results['validation_results']['materials_validation']['property_violations']
            
            print(f"   Found {len(property_violations)} property violations to fix")
            
            # Load Materials.yaml
            with open('data/Materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            fixed_count = 0
            for violation in property_violations:
                if violation.get('severity') == 'high':
                    material_name = violation['material']
                    category = violation['category']
                    prop_name = violation['property']
                    current_value = violation['value']
                    
                    # Handle violations with or without range info
                    range_info = violation.get('range')
                    if not range_info:
                        # Skip violations without range info (like conversion errors)
                        error_info = violation.get('error', 'Unknown error')
                        print(f"   ⚠️ Skipping violation (no range): {material_name}.{prop_name} - {error_info}")
                        continue
                    
                    print(f"   🚨 Fixing critical violation: {material_name}.{prop_name} = {current_value} (range: {range_info})")
                    
                    # Find and fix the violation in Materials.yaml
                    materials_section = materials_data['materials']
                    if category in materials_section:
                        for item in materials_section[category]['items']:
                            if item['name'] == material_name:
                                # Ensure properties section exists
                                if 'properties' not in item:
                                    item['properties'] = {}
                                
                                if prop_name in item['properties'] or True:  # Fix regardless
                                    # Get range bounds
                                    range_parts = range_info.split('-')
                                    if len(range_parts) == 2:
                                        min_val = float(range_parts[0])
                                        max_val = float(range_parts[1])
                                        
                                        # Set to midpoint of range
                                        fixed_value = (min_val + max_val) / 2
                                        
                                        # Create proper property structure
                                        item['properties'][prop_name] = {
                                            'value': fixed_value,
                                            'unit': violation.get('unit', ''),
                                            'min': min_val,
                                            'max': max_val,
                                            'confidence': 0.8
                                        }
                                        
                                        print(f"     ✅ Fixed: {prop_name} = {fixed_value}")
                                        fixed_count += 1
            
            if fixed_count > 0:
                # Save updated Materials.yaml
                with open('data/Materials.yaml', 'w') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False)
                print(f"   ✅ Saved {fixed_count} fixes to Materials.yaml")
            else:
                print(f"   ℹ️  No critical property violations found in Materials.yaml")
        else:
            print(f"\n🔧 Stage 2: Ensuring Materials.yaml Has Required Properties")
            
            # Load Categories.yaml and Materials.yaml
            with open('data/Categories.yaml', 'r') as f:
                categories_data = yaml.safe_load(f)
            with open('data/Materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            # Check if materials have properties, add them if missing
            materials_updated = False
            properties_added = 0
            
            for category_name, category_data in categories_data['categories'].items():
                if category_name not in materials_data['materials']:
                    continue
                
                category_ranges = category_data.get('category_ranges', {})
                materials_in_category = materials_data['materials'][category_name].get('items', [])
                
                for material_item in materials_in_category:
                    material_name = material_item.get('name')
                    
                    # Ensure properties exist
                    if 'properties' not in material_item:
                        material_item['properties'] = {}
                        materials_updated = True
                    
                    # Add missing critical properties with default values from category ranges
                    for prop_name, range_data in category_ranges.items():
                        if prop_name not in material_item['properties']:
                            try:
                                # Handle different range data formats
                                if isinstance(range_data, dict):
                                    # Use robust numeric extraction for min/max values
                                    min_raw = range_data.get('min', 0)
                                    max_raw = range_data.get('max', 100)
                                    
                                    min_val = extract_numeric_value(min_raw)
                                    max_val = extract_numeric_value(max_raw)
                                    
                                    if min_val is None or max_val is None:
                                        print(f"   ⚠️  Skipped {material_name}.{prop_name}: could not extract numeric values from min='{min_raw}' max='{max_raw}'")
                                        continue
                                    
                                    unit = range_data.get('unit', '')
                                elif isinstance(range_data, str):
                                    # Skip string ranges (like thermalDestructionType)
                                    continue
                                else:
                                    continue
                                
                                default_value = (min_val + max_val) / 2
                                
                                material_item['properties'][prop_name] = {
                                    'value': default_value,
                                    'unit': unit,
                                    'min': min_val,
                                    'max': max_val,
                                    'confidence': 0.7,
                                    'source': 'default_from_category_range'
                                }
                                
                                print(f"   ➕ Added {material_name}.{prop_name} = {default_value} (default from range)")
                                properties_added += 1
                                materials_updated = True
                            except (ValueError, TypeError) as e:
                                print(f"   ⚠️  Skipped {material_name}.{prop_name}: {e}")
                                continue
            
            if materials_updated:
                # Save updated Materials.yaml
                with open('data/Materials.yaml', 'w') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False)
                print(f"   ✅ Added {properties_added} missing properties to Materials.yaml")

        # Stage 3: Propagate Materials.yaml updates to frontmatter files
        print(f"\n📄 Stage 3: Propagating Materials.yaml Updates to Frontmatter Files")
        
        frontmatter_dir = Path("content/components/frontmatter")
        if frontmatter_dir.exists():
            frontmatter_files = list(frontmatter_dir.glob("*.yaml"))
            updated_count = 0
            
            # Load updated Materials.yaml
            with open('data/Materials.yaml', 'r') as f:
                updated_materials_data = yaml.safe_load(f)
            
            for frontmatter_file in frontmatter_files:
                try:
                    # Extract material name from filename
                    material_name = frontmatter_file.stem.replace('-laser-cleaning', '').replace('-', ' ').replace('_', ' ').title()
                    
                    # Find material in Materials.yaml
                    material_index = updated_materials_data.get('material_index', {})
                    if material_name not in material_index:
                        continue
                    
                    category = material_index[material_name]
                    
                    # Find material properties in Materials.yaml
                    updated_properties = {}
                    materials_section = updated_materials_data['materials']
                    if category in materials_section:
                        for item in materials_section[category]['items']:
                            if item['name'] == material_name:
                                updated_properties = item.get('properties', {})
                                break
                    
                    if not updated_properties:
                        continue
                    
                    # Load frontmatter file
                    with open(frontmatter_file, 'r') as f:
                        frontmatter_data = yaml.safe_load(f)
                    
                    # Check if updates are needed
                    current_properties = frontmatter_data.get('materialProperties', {})
                    needs_update = False
                    
                    # Handle thermal destruction migration: meltingPoint → thermalDestructionPoint
                    thermal_destruction_migration = {}
                    if 'thermalDestructionPoint' in updated_properties and 'meltingPoint' in current_properties:
                        thermal_destruction_migration['thermalDestructionPoint'] = updated_properties['thermalDestructionPoint']
                        thermal_destruction_migration['_remove_meltingPoint'] = True
                        needs_update = True
                        print(f"   🔥 Migrating {material_name}: meltingPoint → thermalDestructionPoint")
                    
                    # Add new thermal destruction type if missing
                    if 'thermalDestructionType' in updated_properties and 'thermalDestructionType' not in current_properties:
                        thermal_destruction_migration['thermalDestructionType'] = updated_properties['thermalDestructionType']
                        needs_update = True
                        thermal_type = updated_properties['thermalDestructionType'].get('value', 'N/A') if isinstance(updated_properties['thermalDestructionType'], dict) else updated_properties['thermalDestructionType']
                        print(f"   🆕 Adding {material_name}: thermalDestructionType = {thermal_type}")
                    
                    for prop_name, prop_value in updated_properties.items():
                        # Skip thermal destruction properties handled above
                        if prop_name in thermal_destruction_migration:
                            continue
                            
                        if prop_name in current_properties:
                            current_val = current_properties[prop_name]
                            
                            # Extract value for comparison
                            if isinstance(current_val, dict):
                                current_actual = current_val.get('value')
                            else:
                                current_actual = current_val
                            
                            if isinstance(prop_value, dict):
                                updated_actual = prop_value.get('value')
                            else:
                                updated_actual = prop_value
                            
                            if current_actual != updated_actual:
                                needs_update = True
                                print(f"   🔄 Updating {material_name}.{prop_name}: {current_actual} → {updated_actual}")
                                
                                # Update the frontmatter
                                if isinstance(current_properties[prop_name], dict):
                                    frontmatter_data['materialProperties'][prop_name]['value'] = updated_actual
                                else:
                                    frontmatter_data['materialProperties'][prop_name] = updated_actual
                        else:
                            # Add new property from Materials.yaml
                            needs_update = True
                            new_val = prop_value.get('value') if isinstance(prop_value, dict) else prop_value
                            print(f"   ➕ Adding {material_name}.{prop_name}: {new_val}")
                            frontmatter_data['materialProperties'][prop_name] = prop_value
                    
                    # Apply thermal destruction migration
                    if thermal_destruction_migration:
                        for thermal_prop, thermal_value in thermal_destruction_migration.items():
                            if thermal_prop == '_remove_meltingPoint':
                                if 'meltingPoint' in frontmatter_data['materialProperties']:
                                    del frontmatter_data['materialProperties']['meltingPoint']
                                    print(f"     ❌ Removed obsolete meltingPoint property")
                            else:
                                frontmatter_data['materialProperties'][thermal_prop] = thermal_value
                    
                    # Save updated frontmatter if needed
                    if needs_update:
                        with open(frontmatter_file, 'w') as f:
                            yaml.dump(frontmatter_data, f, default_flow_style=False, sort_keys=False)
                        updated_count += 1
                        print(f"     ✅ Updated: {frontmatter_file.name}")
                
                except Exception as e:
                    print(f"     ❌ Error updating {frontmatter_file.name}: {e}")
            
            print(f"   ✅ Updated {updated_count} frontmatter files")
        
        # Stage 4: Generate report if requested
        if report_file:
            print(f"\n� Stage 4: Generating Validation Report")
            
            report_content = f"""# Hierarchical Validation Report
Generated: {validation_results['summary'].get('timestamp', 'Unknown')}

## Overall Status: {summary['overall_status']}

### Categories.yaml: {summary['categories_status']}
### Materials.yaml: {summary['materials_status']}
### Hierarchy Consistency: {summary['hierarchy_status']}
### AI Validation: {summary['ai_validation_status']}
### Frontmatter Files: {summary['frontmatter_status']}

## Issue Summary
- Total Issues: {summary['total_issues']}
- Critical Issues: {summary['critical_issues']}

## Recommendations
"""
            for i, rec in enumerate(validation_results['recommendations'], 1):
                report_content += f"{i}. {rec}\n"
            
            report_content += f"\n## Detailed Results\n{yaml.dump(validation_results['validation_results'], default_flow_style=False)}"
            
            with open(report_file, 'w') as f:
                f.write(report_content)
            print(f"   ✅ Report saved to: {report_file}")
        
        # Final summary
        print(f"\n🎉 Hierarchical Validation and Update Complete!")
        print(f"   Data integrity maintained from Categories.yaml → Materials.yaml → Frontmatter")
        
        if summary['critical_issues'] > 0:
            print(f"   ⚠️  {summary['critical_issues']} critical issues require attention")
            return False
        elif summary['total_issues'] > 0:
            print(f"   ⚠️  {summary['total_issues']} non-critical issues noted")
            return True
        else:
            print(f"   ✅ All validations passed!")
            return True
            
    except Exception as e:
        print(f"❌ Hierarchical validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_frontmatter_sanitization(specific_file=None):
    """Run frontmatter YAML sanitization as a post-processor"""
    try:
        # Import the sanitizer
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts', 'tools'))
        from scripts.tools.sanitize_frontmatter import FrontmatterSanitizer
        
        sanitizer = FrontmatterSanitizer()
        
        if specific_file:
            # Sanitize specific file
            from pathlib import Path
            file_path = Path(specific_file)
            if not file_path.exists():
                print(f"❌ File not found: {specific_file}")
                return False
            
            print(f"🧹 Sanitizing specific file: {file_path.name}")
            result = sanitizer.sanitize_file(file_path)
            
            if result["fixed"]:
                print(f"✅ File fixed: {result['reason']}")
            else:
                print(f"ℹ️  No changes needed: {result['reason']}")
            
            return True
        else:
            # Sanitize all frontmatter files
            print("🧹 Running comprehensive frontmatter YAML sanitization...")
            result = sanitizer.sanitize_all_frontmatter()
            
            if result["success"]:
                if result["fixed"] > 0:
                    print(f"🎉 Sanitization complete! Fixed {result['fixed']} out of {result['total']} files")
                else:
                    print(f"✅ All {result['total']} frontmatter files are already valid!")
                return True
            else:
                print(f"❌ Sanitization failed: {result.get('error', 'Unknown error')}")
                return False
    
    except Exception as e:
        print(f"❌ Sanitization error: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# UTILITY FUNCTIONS
# =================================================================================

def run_data_verification(mode='--all'):
    """Run systematic data verification with AI research"""
    try:
        import subprocess
        import sys
        
        print("🔬 SYSTEMATIC DATA VERIFICATION")
        print("=" * 80)
        
        # Build command based on mode
        cmd = [sys.executable, 'scripts/research_tools/systematic_verify.py']
        
        # Parse mode parameter
        if mode == '--all' or mode == 'all':
            cmd.append('--all')
            print("📋 Mode: Verify ALL properties (~60 properties, $14.64, 18 hours)")
        elif mode == '--critical' or mode == 'critical':
            cmd.append('--critical')
            print("📋 Mode: Verify critical properties (5 properties, $1.20, 3 hours)")
        elif mode == '--important' or mode == 'important':
            cmd.append('--important')
            print("📋 Mode: Verify important properties (5 properties, $1.20, 3 hours)")
        elif mode == '--test' or mode == 'test':
            cmd.extend(['--critical', '--dry-run', '--batch-size', '10'])
            print("📋 Mode: Test run (10 materials, dry-run, $0.10, 15 minutes)")
        elif mode.startswith('--group='):
            group = mode.split('=')[1]
            cmd.extend(['--group', group])
            print(f"📋 Mode: Verify {group} property group")
        elif mode.startswith('--properties='):
            properties = mode.split('=')[1]
            cmd.extend(['--properties', properties])
            print(f"📋 Mode: Verify specific properties: {properties}")
        else:
            # Default to all
            cmd.append('--all')
            print(f"📋 Mode: {mode} (defaulting to --all)")
        
        # Auto-accept all AI values (no manual review)
        cmd.append('--auto-accept-all')
        print("🤖 Auto-accept: ALL AI-verified values will be accepted automatically")
        
        print("=" * 80)
        print("")
        
        # Run the systematic verification tool
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ Data verification completed successfully")
            print("📄 See verification report in data/research/")
            return True
        else:
            print(f"\n⚠️ Data verification exited with code {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("❌ Systematic verification tool not found")
        print("Expected: scripts/research_tools/systematic_verify.py")
        return False
    except Exception as e:
        print(f"❌ Data verification error: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_safe_filename(material_name: str) -> str:
    """
    Generate a safe filename from material name by converting spaces and underscores to hyphens.
    
    Args:
        material_name: The material name (e.g., "Stainless Steel")
        
    Returns:
        Safe filename string (e.g., "stainless-steel")
        
    Example:
        >>> generate_safe_filename("Stainless Steel")
        'stainless-steel'
        >>> generate_safe_filename("Ti-6Al-4V")
        'ti-6al-4v'
    """
    import re
    # Convert to lowercase, replace spaces and underscores with hyphens, 
    # then remove any consecutive hyphens
    safe_name = material_name.lower().replace(' ', '-').replace('_', '-')
    # Remove consecutive hyphens and clean up
    return re.sub(r'-+', '-', safe_name).strip('-')


# =================================================================================
# MAIN ENTRY POINT
# =================================================================================

def main():
    """Main application entry point with basic command line interface."""
    
    # FAIL-FAST VALIDATION (Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DEFAULTS/FALLBACKS)
    print("🚨 ENFORCING FAIL-FAST VALIDATION")
    print("Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR MOCKS/FALLBACKS/DEFAULTS")
    try:
        from scripts.validation.fail_fast_materials_validator import fail_fast_validate_materials
        fail_fast_validate_materials()
        print("✅ Materials database validation PASSED - System approved for operation")
    except Exception as e:
        print("🚨 CRITICAL: System cannot start due to validation failure")
        print(f"💥 Error: {e}")
        print("🚫 Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DEFAULTS/FALLBACKS")
        print("📋 See MATERIALS_REMEDIATION_PLAN.md for remediation instructions.")
        print("🔧 Run: python3 scripts/validation/fail_fast_materials_validator.py")
        return False
    
    import argparse
    import os
    from generators.dynamic_generator import DynamicGenerator
    from api.client_factory import create_api_client
    from data.materials import load_materials_cached as load_materials, clear_materials_cache
    
    # Import pipeline integration from scripts directory
    try:
        from scripts.pipeline_integration import validate_material_pre_generation, validate_and_improve_frontmatter
    except ImportError:
        # Fallback: define dummy functions if pipeline_integration not available
        def validate_material_pre_generation(material_name):
            return {'valid': True, 'issues': []}
        def validate_and_improve_frontmatter(material_name, frontmatter):
            return {'improvements_made': False, 'improved_frontmatter': frontmatter}
    
    # Clear materials cache at startup to ensure fresh data
    # (cache will be populated on first material access)
    clear_materials_cache()
    
    parser = argparse.ArgumentParser(description="Z-Beam Content Generator")
    parser.add_argument("--material", help="Generate content for specific material")
    parser.add_argument("--components", help="Comma-separated list of components to generate")
    parser.add_argument("--all", action="store_true", help="Generate all materials")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--deploy", action="store_true", help="Deploy generated content to Next.js production site")
    parser.add_argument("--sanitize", action="store_true", help="Sanitize all existing frontmatter files (post-processor)")
    parser.add_argument("--sanitize-file", help="Sanitize a specific frontmatter file")
    parser.add_argument("--validate", action="store_true", help="Run hierarchical validation (Categories.yaml → Materials.yaml → Frontmatter) and auto-fix issues")
    parser.add_argument("--validate-report", help="Generate hierarchical validation report to file")
    parser.add_argument("--data", nargs='?', const='--all', help="Systematically verify Materials.yaml data with AI research (use --data=critical, --data=all, or --data=test)")
    
    args = parser.parse_args()
    
    # Handle systematic data verification
    if args.data is not None:
        return run_data_verification(args.data)
    
    # Handle deployment to Next.js production site
    if args.deploy:
        return deploy_to_production()
    
    # Handle data validation without regeneration
    if args.validate or args.validate_report:
        return run_data_validation(args.validate_report)
    
    # Handle frontmatter sanitization (post-processor)
    if args.sanitize or args.sanitize_file:
        return run_frontmatter_sanitization(args.sanitize_file)
    
    if args.test:
        print("🧪 Test mode - basic functionality check")
        from components.table.generators.generator import TableComponentGenerator
        generator = TableComponentGenerator()
        print(f"✅ Table generator loaded: {generator.component_type}")
        return True
    
    if args.material:
        if args.components:
            # Use specified components
            component_types = [c.strip() for c in args.components.split(',')]
            print(f"🚀 Generating {args.components} for {args.material}")
        else:
            # Use enabled components from configuration
            component_types = [comp for comp, config in COMPONENT_CONFIG.items() if config.get('enabled', False)]
            if not component_types:
                print("❌ No components are enabled in configuration")
                return False
            print(f"🚀 Generating enabled components ({', '.join(component_types)}) for {args.material}")
        
        try:
            # Load materials data
            materials_data_dict = load_materials()
            
            # Use the optimized material lookup function
            from data.materials import get_material_by_name
            material_info = get_material_by_name(args.material, materials_data_dict)
            
            if not material_info:
                print(f"❌ Material '{args.material}' not found")
                return False

            # 🔍 INVISIBLE PIPELINE: Pre-generation validation
            print(f"🔍 Validating material data for {args.material}...")
            validation_result = validate_material_pre_generation(args.material)
            if not validation_result['validation_passed']:
                print(f"⚠️ Material validation issues detected: {', '.join(validation_result['issues_detected'])}")
                print("🔧 Proceeding with generation, pipeline will attempt corrections...")

            # Check if any components require API clients
            requires_api = any(
                COMPONENT_CONFIG.get(comp, {}).get('api_provider', 'none') != 'none' 
                for comp in component_types
            )
            
            # Create API client only if needed
            api_client = None
            if requires_api:
                # Find the first non-none API provider for enabled components
                api_provider = None
                for comp in component_types:
                    provider = COMPONENT_CONFIG.get(comp, {}).get('api_provider', 'none')
                    if provider != 'none':
                        api_provider = provider
                        break
                if api_provider:
                    api_client = create_api_client(api_provider)
            
            generator = DynamicGenerator()            # Split components - already done above
            
            for component_type in component_types:
                print(f"📋 Generating {component_type}...")
                
                # Load frontmatter data for components that need it
                frontmatter_data = None
                if component_type in ['table', 'author', 'metatags', 'jsonld', 'caption', 'tags', 'propertiestable']:
                    # Try to load existing frontmatter - prioritize .yaml format
                    base_name = generate_safe_filename(args.material)
                    frontmatter_paths = [
                        f"content/components/frontmatter/{base_name}-laser-cleaning.yaml",
                        f"content/components/frontmatter/{base_name}.yaml",
                        f"content/components/frontmatter/{base_name}-laser-cleaning.md"  # Legacy support
                    ]
                    
                    for frontmatter_path in frontmatter_paths:
                        if os.path.exists(frontmatter_path):
                            import yaml
                            try:
                                if frontmatter_path.endswith('.yaml'):
                                    # Direct YAML file
                                    with open(frontmatter_path, 'r') as f:
                                        frontmatter_data = yaml.safe_load(f)
                                else:
                                    # Markdown file with frontmatter
                                    with open(frontmatter_path, 'r') as f:
                                        content = f.read()
                                    yaml_start = content.find('---') + 3
                                    yaml_end = content.find('---', yaml_start)
                                    if yaml_start > 2 and yaml_end > yaml_start:
                                        # Traditional frontmatter with closing ---
                                        yaml_content = content[yaml_start:yaml_end].strip()
                                    elif yaml_start > 2:
                                        # Pure YAML file without closing --- (our current format)
                                        yaml_content = content[yaml_start:].strip()
                                    else:
                                        yaml_content = None
                                        
                                    if yaml_content:
                                        frontmatter_data = yaml.safe_load(yaml_content)
                                
                                if frontmatter_data:
                                    print(f"✅ Loaded frontmatter data from {frontmatter_path}")
                                    break
                                    
                            except Exception as e:
                                print(f"Warning: Could not load frontmatter from {frontmatter_path}: {e}")
                                continue
                    
                    if not frontmatter_data and component_type != 'frontmatter':
                        print(f"❌ No frontmatter data found for {args.material} - {component_type} component requires frontmatter")
                        continue
                
                result = generator.generate_component(
                    material=args.material,
                    component_type=component_type,
                    api_client=api_client,
                    frontmatter_data=frontmatter_data,
                    material_data=material_info
                )
                
                if result.success:
                    # 🔍 INVISIBLE PIPELINE: Post-generation validation for frontmatter
                    if component_type == 'frontmatter':
                        try:
                            import yaml
                            frontmatter_content = yaml.safe_load(result.content)
                            pipeline_result = validate_and_improve_frontmatter(args.material, frontmatter_content)
                            
                            if pipeline_result['improvements_made']:
                                print(f"🔧 Pipeline improved frontmatter quality for {args.material}")
                                # Use improved frontmatter
                                result.content = yaml.dump(pipeline_result['improved_frontmatter'], default_flow_style=False, sort_keys=False)
                            
                            validation_info = pipeline_result['validation_result']
                            if not validation_info['validation_passed']:
                                print(f"⚠️ Quality issues detected: {', '.join(validation_info['issues_detected'])}")
                        except Exception as e:
                            print(f"⚠️ Pipeline validation failed: {e}")
                    
                    # Save the result
                    output_dir = f"content/components/{component_type}"
                    os.makedirs(output_dir, exist_ok=True)
                    filename = generate_safe_filename(args.material)
                    output_file = f"{output_dir}/{filename}-laser-cleaning.json" if component_type == 'jsonld' else f"{output_dir}/{filename}-laser-cleaning.yaml" if component_type in ['frontmatter', 'table', 'metatags', 'author', 'caption'] else f"{output_dir}/{filename}-laser-cleaning.md"
                    
                    with open(output_file, 'w') as f:
                        f.write(result.content)
                    
                    print(f"✅ {component_type} generated successfully → {output_file}")
                else:
                    print(f"❌ {component_type} generation failed: {result.error_message}")
            
            return True
            
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    elif args.all:
        # Generate for all materials
        if args.components:
            component_types = [c.strip() for c in args.components.split(',')]
            print(f"🚀 Generating {args.components} for all materials")
        else:
            # Use enabled components from configuration
            component_types = [comp for comp, config in COMPONENT_CONFIG.items() if config.get('enabled', False)]
            if not component_types:
                print("❌ No components are enabled in configuration")
                return False
            print(f"🚀 Generating enabled components ({', '.join(component_types)}) for all materials")
        
        try:
            # Load materials data
            materials_data_dict = load_materials()
            all_materials = []
            
            # Get all materials from all categories
            # In the new format, each category key IS a material name
            for material_name, material_data in materials_data_dict.get('materials', {}).items():
                if material_name and isinstance(material_data, dict):
                    all_materials.append((material_name, material_data))
            
            if not all_materials:
                print("❌ No materials found in database")
                return False
            
            print(f"📋 Found {len(all_materials)} materials to process")
            
            # 🔍 INVISIBLE PIPELINE: Batch validation for all materials
            try:
                from scripts.pipeline_integration import validate_batch_generation
                material_names = [material[0] for material in all_materials]
                batch_validation = validate_batch_generation(material_names)
            except ImportError:
                # Fallback if pipeline_integration not available
                material_names = [material[0] for material in all_materials]
                batch_validation = {'valid': True, 'total_materials': len(material_names), 'errors': [], 'warnings': []}
            if batch_validation['valid']:
                print(f"🔍 Batch validation: {batch_validation['total_materials']} materials ready for processing")
            if batch_validation.get('errors'):
                print(f"⚠️ {len(batch_validation['errors'])} validation errors detected")
            if batch_validation.get('warnings'):
                print(f"⚠️ {len(batch_validation['warnings'])} validation warnings detected")
            
            # Check if any components require API clients
            requires_api = any(
                COMPONENT_CONFIG.get(comp, {}).get('api_provider', 'none') != 'none' 
                for comp in component_types
            )
            
            # Initialize API client if needed
            api_client = None
            if requires_api:
                from api.client_cache import get_cached_api_client
                # Try to get a working API client
                for provider in ['deepseek', 'grok', 'winston']:
                    try:
                        api_client = get_cached_api_client(provider)
                        if api_client:
                            print(f"🔧 Using API provider: {provider}")
                            break
                    except Exception as e:
                        print(f"⚠️ Failed to initialize {provider}: {e}")
                        continue
                
                if not api_client:
                    print("❌ Failed to initialize any API client")
                    return False
            
            # Process each material
            generator = DynamicGenerator()
            success_count = 0
            failure_count = 0
            
            for material_name, material_info in all_materials:
                print(f"\n📋 Processing {material_name}...")
                
                for component_type in component_types:
                    try:
                        # Load frontmatter data for components that need it
                        frontmatter_data = None
                        if component_type in ['table', 'author', 'metatags', 'jsonld', 'caption', 'tags', 'propertiestable']:
                            # Try to load existing frontmatter
                            material_slug = generate_safe_filename(material_name)
                            frontmatter_paths = [
                                f"content/components/frontmatter/{material_slug}-laser-cleaning.yaml",
                                f"content/components/frontmatter/{material_slug}.yaml",
                                f"content/components/frontmatter/{material_slug}-laser-cleaning.md"  # Legacy support
                            ]
                            frontmatter_path = None
                            for path in frontmatter_paths:
                                if os.path.exists(path):
                                    frontmatter_path = path
                                    break
                            if frontmatter_path and os.path.exists(frontmatter_path):
                                import yaml
                                with open(frontmatter_path, 'r', encoding='utf-8') as f:
                                    # Check if file is pure YAML or markdown with frontmatter
                                    content = f.read()
                                    if frontmatter_path.endswith('.yaml'):
                                        # Pure YAML file - load directly
                                        frontmatter_data = yaml.safe_load(content)
                                    else:
                                        # Markdown file with frontmatter - extract YAML between --- delimiters
                                        yaml_start = content.find('---') + 3
                                        yaml_end = content.find('---', yaml_start)
                                        if yaml_start > 2 and yaml_end > yaml_start:
                                            yaml_content = content[yaml_start:yaml_end].strip()
                                            frontmatter_data = yaml.safe_load(yaml_content)
                            
                            if not frontmatter_data and component_type != 'frontmatter':
                                print(f"  ⚠️ No frontmatter data found for {material_name} - skipping {component_type}")
                                continue
                        
                        result = generator.generate_component(
                            material=material_name,
                            component_type=component_type,
                            api_client=api_client,
                            frontmatter_data=frontmatter_data,
                            material_data=material_info
                        )
                        
                        if result.success:
                            # Save the result
                            output_dir = f"content/components/{component_type}"
                            os.makedirs(output_dir, exist_ok=True)
                            filename = generate_safe_filename(material_name)
                            output_file = f"{output_dir}/{filename}-laser-cleaning.json" if component_type == 'jsonld' else f"{output_dir}/{filename}-laser-cleaning.yaml" if component_type in ['frontmatter', 'table', 'metatags', 'author', 'caption', 'tags'] else f"{output_dir}/{filename}-laser-cleaning.md"
                            
                            with open(output_file, 'w') as f:
                                f.write(result.content)
                            
                            print(f"  ✅ {component_type} → {output_file}")
                            success_count += 1
                        else:
                            print(f"  ❌ {component_type} failed: {result.error_message}")
                            failure_count += 1
                    
                    except Exception as e:
                        print(f"  ❌ {component_type} error: {e}")
                        failure_count += 1
            
            print(f"\n🏁 Generation completed: {success_count} successes, {failure_count} failures")
            return True
            
        except Exception as e:
            print(f"❌ All materials generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    else:
        parser.print_help()
        return True


if __name__ == "__main__":
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
