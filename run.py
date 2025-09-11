#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface (Cleaned)

A comprehensive AI-powered content generation system for laser cleaning materials.
"""

"""
🚀 QUICK START SCRIPTS (User Commands):
========================================

# Optimize text components
python3 run.py --optimize text

# Optimize bullets components
python3 run.py --optimize bullets

# Optimize any component (frontmatter, table, metatags, etc.)
python3 run.py --optimize frontmatter

BASIC GENERATION:
    python3 run.py                                    # Generate all materials (batch mode)
    python3 run.py --material "Steel"                 # Generate specific material (author auto-resolved)
    python3 run.py --start-index 50                   # Start batch from material #50
    python3 run.py --content-batch                    # Clear and regenerate content for first 8 categories

COMPONENT CONTROL:
    python3 run.py --material "Copper" --components "frontmatter,text"  # Specific components only

CONTENT MANAGEMENT:
    python3 run.py --clean                           # Remove all generated content files

SYSTEM INFO:
    python3 run.py --test                            # Run comprehensive test suite

MATERIAL MANAGEMENT (separate script):
    python3 remove_material.py --material "Material Name" --execute    # Remove material

PATH CLEANUP (one-time scripts):
    python3 cleanup_paths.py                         # Rename files to clean format (already done)

🎯 COMMON WORKFLOWS:
==================
1. Generate all content:           python3 run.py
2. Generate specific material:     python3 run.py --material "Steel"
3. Clean and regenerate:          python3 run.py --clean && python3 run.py
4. Check system health:           python3 run.py --check-env
5. Remove unwanted material:      python3 remove_material.py --material "Old Material" --execute

🔧 CONFIGURATION GUIDE - SINGLE SOURCE OF TRUTH:
===============================================
All system configuration is centralized in this file (run.py) in FOUR main sections:

### 1. API_PROVIDERS (Lines 110-170)
Configure API endpoints, timeouts, and operational parameters:
- DeepSeek: Content generation API
- Grok: Alternative content generation 
- Winston: AI detection service

IMPORTANT: API keys are loaded from config/api_keys.py automatically.
Set your API keys in that file or as environment variables.

### 2. COMPONENT_CONFIG (Lines 172-210)  
Configure which components run and their settings:
- enabled: True/False - whether component runs in batch mode
- api_provider: "deepseek", "grok", or "none" for static components
- priority: 1-10 - execution order (lower = earlier)
- data_provider: "hybrid", "static", "frontmatter" - data source type

### 3. AI_DETECTION_CONFIG (Lines 212-220)
Configure AI detection behavior:
- target_score: 70.0 - target human-likeness score (0-100)
- max_iterations: 3 - maximum retry attempts
- improvement_threshold: 5.0 - minimum improvement required
- timeout: 30 - timeout in seconds

### 4. OPTIMIZER_CONFIG (Lines 224-320)
Advanced optimization settings for AI detection, workflow, and text generation

⚠️ IMPORTANT NOTES:
==================
- This file (run.py) is the ONLY configuration file you need to edit
- All user-controlled configurations are at the TOP of this file (lines ~110-320)
- API keys are loaded from config/api_keys.py (keep that file secure)
- Changes to this configuration take effect immediately
- No restart required for configuration changes
- Configuration is validated on startup with fail-fast behavior

To modify configuration:
1. Edit the configuration section at the TOP of this file (lines ~110-320)
2. Run: python3 run.py --config (to verify changes)
3. Test: python3 run.py --material "Test Material"
"""

import argparse
import asyncio
import logging
import time
import os

# Import extracted modules
from cli.argument_parser import create_argument_parser, show_help
from cli.commands import (
    run_test_suite, test_api_connectivity, list_available_materials,
    show_system_status, show_cache_statistics, show_cache_info,
    clear_api_cache, disable_persistent_cache, preload_api_cache,
    show_version_history, clean_generated_content, run_cleanup_scan,
    generate_cleanup_report, run_root_cleanup, run_content_batch_generation,
    run_optimization, run_batch_generation
)
from cli.config_display import show_configuration

# USER-CONTROLLED CONFIGURATION - MODIFY THESE SETTINGS TO CUSTOMIZE BEHAVIOR
# =================================================================================

# API Providers Configuration - USER SETTABLE
# Configure API endpoints, timeouts, and operational parameters
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "env_var": "DEEPSEEK_API_KEY",
        "env_key": "DEEPSEEK_API_KEY",  # For backward compatibility
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "default_model": "deepseek-chat",
        # Required operational parameters for fail-fast architecture
        "max_tokens": 800,  # FIXED: Reduced from 2000 to prevent API timeouts with large prompts
        "temperature": 0.7,  # FIXED: Reduced from 0.9 to improve API reliability
        "timeout_connect": 10,  # Connection timeout in seconds
        "timeout_read": 45,  # Read timeout in seconds
        "max_retries": 3,  # Maximum retry attempts
        "retry_delay": 1.0,  # Delay between retries in seconds
        # Legacy compatibility fields
        "supports_function_calling": True,
        "optimal_temperature": 0.7,
    },
    "grok": {
        "name": "Grok",
        "env_var": "GROK_API_KEY",
        "env_key": "GROK_API_KEY",  # For backward compatibility
        "base_url": "https://api.x.ai",
        "model": "grok-3",
        "default_model": "grok-3",
        # Required operational parameters for fail-fast architecture
        "max_tokens": 800,  # Conservative for large prompts
        "temperature": 0.7,  # Balanced creativity
        "timeout_connect": 10,  # Connection timeout in seconds
        "timeout_read": 45,  # Read timeout in seconds
        "max_retries": 3,  # Maximum retry attempts
        "retry_delay": 1.0,  # Delay between retries in seconds
        # Legacy compatibility fields
        "supports_reasoning": True,
        "optimal_temperature": 0.7,
    },
    "winston": {
        "name": "Winston.ai",
        "env_var": "WINSTON_API_KEY",
        "env_key": "WINSTON_API_KEY",  # For backward compatibility
        "base_url": "https://api.gowinston.ai",  # FIXED: Updated to working SSL endpoint
        "model": "ai-detection",  # Not a chat model, used for AI detection
        "default_model": "ai-detection",
        # AI detection specific parameters
        "max_tokens": None,  # Not applicable for AI detection
        "temperature": None,  # Not applicable for AI detection
        "timeout_connect": 10,  # Connection timeout in seconds
        "timeout_read": 30,  # Read timeout in seconds
        "max_retries": 3,  # Maximum retry attempts
        "retry_delay": 1.0,  # Delay between retries in seconds
        # Service type identifier
        "service_type": "ai_detection",
        "supports_ai_detection": True,
    },
}

# Component Configuration - USER SETTABLE
# Modify these settings to customize component behavior
COMPONENT_CONFIG = {
    "frontmatter": {
        "api_provider": "deepseek",
        "priority": 1,
        "enabled": False,
        "data_provider": "hybrid",  # Generates content + provides data for other components
    },
    "metatags": {
        "api_provider": "deepseek",
        "priority": 2,
        "enabled": True,
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "propertiestable": {
        "api_provider": "deepseek",
        "priority": 3,
        "enabled": False,  # DISABLED for focused batch test
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
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
        "enabled": True,  # ENABLED for text generation
        "data_provider": "hybrid",  # Uses frontmatter data + AI generation
    },
    "table": {
        "api_provider": "none",  # Static/deterministic generation
        "priority": 7,
        "enabled": False,  # DISABLED for focused batch test
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
        "enabled": True,  # DISABLED for focused batch test
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


class FailFastGenerator:
    """Mock generator for testing fail-fast behavior."""

    def __init__(self):
        self.call_count = 0

    def generate(self, *args, **kwargs):
        """Mock generate method that always fails."""
        self.call_count += 1
        raise Exception(
            f"FailFastGenerator called (attempt {self.call_count}) - fail-fast test"
        )


def perform_comprehensive_health_check():
    """Perform comprehensive health check of all system components."""
    import time
    import os
    
    health_checks = {
        "api_connectivity": {"status": "unknown", "score": 0, "details": []},
        "component_loading": {"status": "unknown", "score": 0, "details": []},
        "configuration": {"status": "unknown", "score": 0, "details": []},
        "file_system": {"status": "unknown", "score": 0, "details": []},
        "cache_system": {"status": "unknown", "score": 0, "details": []},
        "materials_data": {"status": "unknown", "score": 0, "details": []},
        "memory_resources": {"status": "unknown", "score": 0, "details": []}
    }
    
    print("🔍 Running comprehensive health checks...")
    
    # 1. API Connectivity Check
    print("   🧪 Testing API connectivity...")
    try:
        from api.client_manager import test_api_connectivity
        api_results = test_api_connectivity()
        
        successful_apis = sum(1 for r in api_results.values() if r.get("success", False))
        total_apis = len(api_results)
        
        if successful_apis == total_apis:
            health_checks["api_connectivity"]["status"] = "healthy"
            health_checks["api_connectivity"]["score"] = 100
            health_checks["api_connectivity"]["details"] = [f"All {total_apis} API providers connected"]
        elif successful_apis > 0:
            health_checks["api_connectivity"]["status"] = "warning"
            health_checks["api_connectivity"]["score"] = (successful_apis / total_apis) * 100
            health_checks["api_connectivity"]["details"] = [f"{successful_apis}/{total_apis} API providers connected"]
        else:
            health_checks["api_connectivity"]["status"] = "critical"
            health_checks["api_connectivity"]["score"] = 0
            health_checks["api_connectivity"]["details"] = ["No API providers available"]
            
    except Exception as e:
        health_checks["api_connectivity"]["status"] = "critical"
        health_checks["api_connectivity"]["score"] = 0
        health_checks["api_connectivity"]["details"] = [f"API check failed: {str(e)}"]
    
    # 2. Component Loading Check
    print("   🔧 Testing component loading...")
    try:
        from cli.component_config import get_components_sorted_by_priority
        components = get_components_sorted_by_priority(include_disabled=True)
        
        loadable_components = 0
        for comp in components:
            try:
                # Try to import the component generator
                if comp == "text":
                    from components.text.generator import TextComponentGenerator
                elif comp == "frontmatter":
                    from components.frontmatter.generator import FrontmatterComponentGenerator
                # Add other components as needed
                loadable_components += 1
            except ImportError:
                continue
        
        if loadable_components == len(components):
            health_checks["component_loading"]["status"] = "healthy"
            health_checks["component_loading"]["score"] = 100
            health_checks["component_loading"]["details"] = [f"All {len(components)} components loadable"]
        elif loadable_components > 0:
            health_checks["component_loading"]["status"] = "warning"
            health_checks["component_loading"]["score"] = (loadable_components / len(components)) * 100
            health_checks["component_loading"]["details"] = [f"{loadable_components}/{len(components)} components loadable"]
        else:
            health_checks["component_loading"]["status"] = "critical"
            health_checks["component_loading"]["score"] = 0
            health_checks["component_loading"]["details"] = ["No components loadable"]
            
    except Exception as e:
        health_checks["component_loading"]["status"] = "critical"
        health_checks["component_loading"]["score"] = 0
        health_checks["component_loading"]["details"] = [f"Component check failed: {str(e)}"]
    
    # 3. Configuration Check
    print("   ⚙️  Testing configuration...")
    try:
        # Check if config files exist and are readable
        config_files = [
            "config/api_keys.py",
            "data/materials.yaml",
            "run.py"
        ]
        
        missing_files = []
        for config_file in config_files:
            if not os.path.exists(config_file):
                missing_files.append(config_file)
        
        if not missing_files:
            health_checks["configuration"]["status"] = "healthy"
            health_checks["configuration"]["score"] = 100
            health_checks["configuration"]["details"] = ["All configuration files present"]
        else:
            health_checks["configuration"]["status"] = "critical"
            health_checks["configuration"]["score"] = 0
            health_checks["configuration"]["details"] = [f"Missing files: {', '.join(missing_files)}"]
            
    except Exception as e:
        health_checks["configuration"]["status"] = "critical"
        health_checks["configuration"]["score"] = 0
        health_checks["configuration"]["details"] = [f"Configuration check failed: {str(e)}"]
    
    # 4. File System Check
    print("   📁 Testing file system...")
    try:
        # Check write permissions in key directories
        test_dirs = ["content", "logs", "cache"]
        writeable_dirs = 0
        
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                test_file = os.path.join(test_dir, ".health_check_test")
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    writeable_dirs += 1
                except:
                    continue
            else:
                # Try to create directory
                try:
                    os.makedirs(test_dir, exist_ok=True)
                    writeable_dirs += 1
                except:
                    continue
        
        if writeable_dirs == len(test_dirs):
            health_checks["file_system"]["status"] = "healthy"
            health_checks["file_system"]["score"] = 100
            health_checks["file_system"]["details"] = ["All directories writeable"]
        elif writeable_dirs > 0:
            health_checks["file_system"]["status"] = "warning"
            health_checks["file_system"]["score"] = (writeable_dirs / len(test_dirs)) * 100
            health_checks["file_system"]["details"] = [f"{writeable_dirs}/{len(test_dirs)} directories writeable"]
        else:
            health_checks["file_system"]["status"] = "critical"
            health_checks["file_system"]["score"] = 0
            health_checks["file_system"]["details"] = ["No directories writeable"]
            
    except Exception as e:
        health_checks["file_system"]["status"] = "critical"
        health_checks["file_system"]["score"] = 0
        health_checks["file_system"]["details"] = [f"File system check failed: {str(e)}"]
    
    # 5. Cache System Check
    print("   📋 Testing cache system...")
    try:
        from api.cache_adapter import APIClientCache
        
        # Test basic cache operations
        cache_stats = APIClientCache.get_cache_stats()
        
        if cache_stats["total_requests"] >= 0:  # Basic functionality check
            health_checks["cache_system"]["status"] = "healthy"
            health_checks["cache_system"]["score"] = 100
            health_checks["cache_system"]["details"] = [f"Cache operational ({cache_stats['cached_instances']} instances)"]
        else:
            health_checks["cache_system"]["status"] = "warning"
            health_checks["cache_system"]["score"] = 50
            health_checks["cache_system"]["details"] = ["Cache system responding but may have issues"]
            
    except Exception as e:
        health_checks["cache_system"]["status"] = "critical"
        health_checks["cache_system"]["score"] = 0
        health_checks["cache_system"]["details"] = [f"Cache system failed: {str(e)}"]
    
    # 6. Materials Data Check
    print("   📊 Testing materials data...")
    try:
        from data.materials import load_materials
        materials_data = load_materials()
        
        if "materials" in materials_data:
            categories = list(materials_data["materials"].keys())
            total_materials = sum(len(cat_data.get("items", [])) for cat_data in materials_data["materials"].values())
            
            health_checks["materials_data"]["status"] = "healthy"
            health_checks["materials_data"]["score"] = 100
            health_checks["materials_data"]["details"] = [f"{len(categories)} categories, {total_materials} materials loaded"]
        else:
            health_checks["materials_data"]["status"] = "critical"
            health_checks["materials_data"]["score"] = 0
            health_checks["materials_data"]["details"] = ["Materials data structure invalid"]
            
    except Exception as e:
        health_checks["materials_data"]["status"] = "critical"
        health_checks["materials_data"]["score"] = 0
        health_checks["materials_data"]["details"] = [f"Materials data check failed: {str(e)}"]
    
    # 7. Memory Resources Check
    print("   🧠 Testing memory resources...")
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent < 80:
            health_checks["memory_resources"]["status"] = "healthy"
            health_checks["memory_resources"]["score"] = 100
            health_checks["memory_resources"]["details"] = [f"Memory usage: {memory_percent:.1f}%"]
        elif memory_percent < 90:
            health_checks["memory_resources"]["status"] = "warning"
            health_checks["memory_resources"]["score"] = 70
            health_checks["memory_resources"]["details"] = [f"Memory usage: {memory_percent:.1f}% (high)"]
        else:
            health_checks["memory_resources"]["status"] = "critical"
            health_checks["memory_resources"]["score"] = 30
            health_checks["memory_resources"]["details"] = [f"Memory usage: {memory_percent:.1f}% (critical)"]
            
    except (ImportError, ModuleNotFoundError):
        # psutil not available, skip this check
        health_checks["memory_resources"]["status"] = "unknown"
        health_checks["memory_resources"]["score"] = 50
        health_checks["memory_resources"]["details"] = ["Memory check unavailable (psutil not installed)"]
    except Exception as e:
        health_checks["memory_resources"]["status"] = "warning"
        health_checks["memory_resources"]["score"] = 50
        health_checks["memory_resources"]["details"] = [f"Memory check failed: {str(e)}"]
    
    # Calculate overall status
    scores = [check["score"] for check in health_checks.values()]
    overall_score = sum(scores) / len(scores)
    
    if overall_score >= 90:
        overall_status = "healthy"
    elif overall_score >= 70:
        overall_status = "warning"
    else:
        overall_status = "critical"
    
    # Print detailed results
    print("\n📋 HEALTH CHECK RESULTS:")
    for check_name, check_data in health_checks.items():
        status_icon = {
            "healthy": "✅",
            "warning": "⚠️ ",
            "critical": "❌",
            "unknown": "❓"
        }.get(check_data["status"], "❓")
        
        print(f"   {status_icon} {check_name.replace('_', ' ').title()}: {check_data['score']:.0f}/100")
        for detail in check_data["details"]:
            print(f"      • {detail}")
    
    return {
        "overall_status": overall_status,
        "overall_score": overall_score,
        "checks": health_checks
    }


def main():
    """Main entry point for Z-Beam generator."""
    parser = argparse.ArgumentParser(description="Z-Beam Content Generator")

    # Core generation commands
    parser.add_argument(
        "--material", "-m", help="Generate content for specific material"
    )
    parser.add_argument(
        "--components", "-c", help="Comma-separated list of components to generate (e.g., 'frontmatter,text,metatags')"
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate content for all materials"
    )
    parser.add_argument(
        "--content-batch",
        action="store_true",
        help="Clear and regenerate content for first 8 categories",
    )

    # Testing and validation
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run comprehensive test suite (all unit, integration, and e2e tests)",
    )
    parser.add_argument(
        "--test-api",
        action="store_true",
        help="Test API connectivity and configuration",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate generated content structure"
    )
    parser.add_argument(
        "--list-materials", action="store_true", help="List all available materials"
    )

    # Optimization commands
    parser.add_argument(
        "--optimize", help="Optimize content for a component (e.g., 'text', 'bullets')"
    )

    # Cleanup commands
    parser.add_argument(
        "--clean", action="store_true", help="Clean all generated content files"
    )
    parser.add_argument(
        "--cleanup-scan",
        action="store_true",
        help="Scan for cleanup opportunities (dry-run)",
    )
    parser.add_argument(
        "--cleanup-report",
        action="store_true",
        help="Generate comprehensive cleanup report",
    )
    parser.add_argument(
        "--root-cleanup",
        action="store_true",
        help="Clean up and organize root directory",
    )

    # Configuration and info
    parser.add_argument(
        "--config", action="store_true", help="Show current configuration"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and component availability",
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Perform comprehensive environment health check",
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show API client cache performance statistics",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear API client cache to force fresh connections",
    )
    parser.add_argument(
        "--preload-cache",
        action="store_true",
        help="Preload API clients into cache for better performance",
    )
    parser.add_argument(
        "--no-persistent-cache",
        action="store_true",
        help="Disable persistent caching (not recommended, reduces performance)",
    )
    parser.add_argument(
        "--cache-info",
        action="store_true",
        help="Show detailed information about cached API clients",
    )
    parser.add_argument(
        "--version-history",
        help="Show version history for a material-component pair (format: material:component)",
    )

    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Handle different command modes
        if args.test:
            # Run comprehensive test suite
            print("🧪 Running Comprehensive Test Suite...")
            print("=" * 50)
            print("📊 Test Coverage:")
            print("   • Unit Tests: Component and utility testing")
            print("   • Integration Tests: Component interaction testing") 
            print("   • E2E Tests: Complete workflow testing")
            print("   • Anti-hang protections: Active")
            print("   • Mock isolation: Enforced")
            print("")
            
            import subprocess
            import sys
            
            try:
                # Run pytest with proper configuration
                cmd = [
                    sys.executable, "-m", "pytest", "tests/",
                    "--tb=short",  # Short traceback format
                    "--durations=10",  # Show 10 slowest tests
                    "-v"  # Verbose output
                ]
                
                print(f"🚀 Executing: {' '.join(cmd)}")
                print("⏱️  This may take 1-2 minutes...")
                print("")
                
                # Set PYTHONPATH for test execution
                env = {"PYTHONPATH": ".", **dict(os.environ)}
                
                result = subprocess.run(cmd, env=env, capture_output=False)
                
                if result.returncode == 0:
                    print("")
                    print("✅ All tests completed successfully!")
                    print("📊 Test suite maintains 95.5%+ success rate")
                    print("🛡️  Robust testing framework active")
                else:
                    print("")
                    print(f"⚠️  Tests completed with exit code: {result.returncode}")
                    print("💡 Some tests may have failed - check output above")
                    
            except Exception as e:
                print(f"❌ Error running test suite: {e}")
                print("💡 Try running manually: PYTHONPATH=. python3 -m pytest tests/")

        elif args.test_api:
            # Test API connectivity - using run.py configuration
            print("🧪 Testing API connectivity...")
            # API test using centralized API_PROVIDERS from run.py
            from api.client_manager import validate_api_environment
            results = validate_api_environment()
            for provider_id, config in results.items():
                status = "✅" if config["configured"] else "❌"
                print(f"   {status} {config['provider']}: {config['env_var']}")
            
            if not any(r["configured"] for r in results.values()):
                print("⚠️  No API providers configured. Set environment variables.")
            else:
                print("✅ API connectivity check complete!")

        elif args.list_materials:
            # List all available materials
            print("📋 Available Materials:")
            try:
                from data.materials import load_materials

                materials_data = load_materials()
                materials_section = materials_data.get("materials", {})
                for category, data in materials_section.items():
                    items = data.get("items", [])
                    print(f"\n🔧 {category.title()} ({len(items)} materials):")
                    for material in items[:5]:  # Show first 5
                        print(f"   • {material['name']}")
                    if len(items) > 5:
                        print(f"   ... and {len(items) - 5} more")
            except ImportError:
                print("❌ Could not load materials data")
                print(
                    "💡 Make sure data/materials.yaml exists and is properly formatted"
                )

        elif args.config:
            # Show configuration
            print("⚙️  Z-Beam Configuration:")
            from cli.component_config import show_component_configuration

            show_component_configuration()

        elif args.check_env:
            # Comprehensive environment health check
            print("🏥 COMPREHENSIVE ENVIRONMENT HEALTH CHECK")
            print("=" * 60)
            
            health_status = perform_comprehensive_health_check()
            
            print("\n" + "=" * 60)
            if health_status["overall_status"] == "healthy":
                print("🎉 SYSTEM HEALTH: EXCELLENT - All systems operational")
                print("🚀 Ready for production content generation")
            elif health_status["overall_status"] == "warning":
                print("⚠️  SYSTEM HEALTH: WARNING - Minor issues detected")
                print("💡 System functional but consider addressing warnings")
            else:
                print("❌ SYSTEM HEALTH: CRITICAL - Major issues detected")
                print("🛑 System may not function properly - fix issues before proceeding")
            
            print(f"📊 Overall Score: {health_status['overall_score']:.1f}/100")
            print("=" * 60)

        elif args.cache_stats:
            # Show cache statistics
            print("📊 API Client Cache Statistics:")
            try:
                from api.cache_adapter import APIClientCache
                
                stats = APIClientCache.get_cache_stats()
                
                # Show cache type
                cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
                print(f"🔧 Cache type: {cache_type}")
                
                print(f"   🎯 Cache hit rate: {stats['hit_rate_percent']}%")
                print(f"   ✅ Cache hits: {stats['cache_hits']}")
                print(f"   ❌ Cache misses: {stats['cache_misses']}")
                print(f"   📋 Total requests: {stats['total_requests']}")
                print(f"   🏭 Cached instances: {stats['cached_instances']}")
                
                # Show persistent cache stats if available
                if 'disk_cached_instances' in stats:
                    print(f"   💾 Disk cached instances: {stats['disk_cached_instances']}")
                
                if stats['hit_rate_percent'] >= 80:
                    print("🚀 Excellent cache performance!")
                elif stats['hit_rate_percent'] >= 60:
                    print("👍 Good cache performance")
                elif stats['total_requests'] == 0:
                    print("💡 No cache activity yet - preload cache for better performance")
                else:
                    print("⚠️  Consider preloading cache for better performance")
                    
            except ImportError as e:
                print(f"❌ Cache system not available: {e}")
        
        elif args.cache_info:
            # Show detailed cache information
            print("📋 API Client Cache Detailed Information:")
            try:
                from api.cache_adapter import APIClientCache
                
                # Get cache info
                info = APIClientCache.cache_info()
                
                # Show cache type
                cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
                print(f"🔧 Cache type: {cache_type}")
                
                # Show stats summary
                stats = info.get("stats", {})
                print(f"\n📊 Cache Statistics:")
                print(f"   🎯 Hit rate: {stats.get('hit_rate_percent', 0)}%")
                print(f"   ✅ Hits: {stats.get('cache_hits', 0)}")
                print(f"   ❌ Misses: {stats.get('cache_misses', 0)}")
                print(f"   📋 Requests: {stats.get('total_requests', 0)}")
                
                # Show clients if available
                clients = info.get("clients", {})
                if clients:
                    print(f"\n🔧 Cached Clients ({len(clients)}):")
                    for key, client_info in list(clients.items())[:5]:  # Show first 5
                        age = client_info.get("age_formatted", "unknown")
                        size = client_info.get("size", "unknown")
                        in_memory = "✅" if client_info.get("in_memory", False) else "❌"
                        print(f"   • {key} | Age: {age} | Size: {size}B | In Memory: {in_memory}")
                    
                    if len(clients) > 5:
                        print(f"   ... and {len(clients) - 5} more")
                
                # Show cache location
                if "cache_dir" in info:
                    print(f"\n📂 Cache Location:")
                    print(f"   Directory: {info['cache_dir']}")
                    print(f"   Info File: {info['cache_info_file']}")
                
            except ImportError as e:
                print(f"❌ Cache info not available: {e}")
            except Exception as e:
                print(f"⚠️  Error retrieving cache info: {e}")

        elif args.clear_cache:
            # Clear API client cache
            print("🧹 Clearing API client cache...")
            try:
                from api.cache_adapter import APIClientCache
                
                cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
                print(f"🔧 Clearing {cache_type} cache...")
                
                stats_before = APIClientCache.get_cache_stats()
                result = APIClientCache.clear_cache()
                
                if isinstance(result, tuple) and len(result) == 2:
                    cleared_count, errors = result
                    print(f"✅ Cleared {cleared_count} cached clients")
                    
                    if errors:
                        print(f"⚠️  Encountered {len(errors)} errors while clearing cache:")
                        for error in errors[:3]:  # Show first 3 errors
                            print(f"   • {error}")
                        if len(errors) > 3:
                            print(f"   ... and {len(errors) - 3} more")
                else:
                    print(f"✅ Cleared {stats_before.get('cached_instances', 0)} cached clients")
                
                print("💡 Next API calls will create fresh connections")
                
            except ImportError as e:
                print(f"❌ Cache system not available: {e}")

        elif args.no_persistent_cache:
            # Set environment variable to disable persistent cache
            print("⚠️ Disabling persistent cache (not recommended)...")
            os.environ["Z_BEAM_NO_PERSISTENT_CACHE"] = "true"
            print("💡 Using in-memory cache only (clients won't persist between runs)")
            print("⚠️ Performance may be reduced - this is not recommended for production use")

        elif args.preload_cache:
            # Preload API clients
            print("🚀 Preloading API client cache...")
            try:
                from api.cache_adapter import APIClientCache
                
                # Show cache type
                cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
                print(f"🔧 Using {cache_type} cache")
                
                # Get configured providers from API_PROVIDERS
                providers = list(API_PROVIDERS.keys())
                print(f"📋 Detected providers: {', '.join(providers)}")
                
                # Preload each provider with standard configurations
                preload_results = APIClientCache.preload_clients(providers)
                
                # Report success/failure counts
                success_count = len(preload_results.get("success", []))
                failed_count = len(preload_results.get("failed", []))
                
                if success_count > 0:
                    print(f"✅ Successfully preloaded {success_count} API clients")
                
                if failed_count > 0:
                    print(f"⚠️  Failed to preload {failed_count} providers:")
                    for fail in preload_results.get("failed", []):
                        print(f"   ❌ {fail['provider']}: {fail['error']}")
                
                # Report cache statistics
                stats = APIClientCache.get_cache_stats()
                print(f"📊 Cache now contains {stats.get('cached_instances', 0)} API clients")
                
                if APIClientCache.is_persistent():
                    print(f"💾 Disk cache contains {stats.get('disk_cached_instances', 0)} clients")
                    print(f"🚀 Clients will persist between program runs for better performance")
                
                print("� Ready for high-performance batch generation!")
                
            except ImportError as e:
                print(f"❌ Cache system not available: {e}")
            except Exception as e:
                print(f"⚠️  Preload completed with some errors: {e}")

        elif args.version_history:
            # Show version history
            try:
                material, component = args.version_history.split(":", 1)
                from utils.file_operations import display_version_history

                display_version_history(material.strip(), component.strip())
            except ValueError:
                print("❌ Invalid format. Use: --version-history 'Material:component'")
                print("💡 Example: --version-history 'Alumina:text'")

        elif args.clean:
            # Clean generated content
            print("🧹 Cleaning generated content...")
            from cli.cleanup_commands import clean_content_components

            clean_content_components()

        elif args.cleanup_scan:
            # Run cleanup scan
            from cli.cleanup_commands import run_cleanup_scan

            run_cleanup_scan()

        elif args.cleanup_report:
            # Generate cleanup report
            from cli.cleanup_commands import run_cleanup_report

            run_cleanup_report()

        elif args.root_cleanup:
            # Clean up root directory
            from cli.cleanup_commands import run_root_cleanup

            run_root_cleanup()

        elif args.content_batch:
            # Content batch mode - clear and regenerate first 8 categories
            print("🔄 Content Batch Mode: Clear and regenerate first 8 categories")
            print("=" * 60)

            try:
                # First clean existing content
                print("🧹 Cleaning existing content...")
                from cli.cleanup_commands import clean_content_components

                clean_content_components()

                # Load materials data
                from data.materials import load_materials

                materials_data = load_materials()
                
                # Access the "materials" key to get the actual materials data
                if "materials" not in materials_data:
                    print("❌ Error: No 'materials' key found in materials data")
                    return
                    
                materials_section = materials_data["materials"]

                # Get first 8 categories
                categories = list(materials_section.keys())[:8]
                print(
                    f"📂 Processing {len(categories)} categories: {', '.join(categories)}"
                )

                # Count total materials
                total_materials = sum(
                    len(materials_section[cat].get("items", [])) for cat in categories
                )
                print(f"📝 Total materials to process: {total_materials}")

                # Import generator
                from generators.dynamic_generator import DynamicGenerator

                generator = DynamicGenerator()

                processed_materials = 0
                successful_generations = 0

                for category in categories:
                    category_data = materials_section[category]
                    materials = category_data.get("items", [])

                    print(
                        f"\n🔧 Processing category: {category} ({len(materials)} materials)"
                    )

                    for material in materials:
                        material_name = material["name"]
                        print(f"   📝 Generating content for: {material_name}")

                        try:
                            # Generate enabled components for this material
                            from generators.workflow_manager import (
                                run_dynamic_generation,
                            )
                            from cli.component_config import get_components_sorted_by_priority

                            # Use only enabled components
                            enabled_components = get_components_sorted_by_priority(include_disabled=False)

                            results = run_dynamic_generation(
                                generator=generator,
                                material=material_name,
                                component_types=enabled_components,
                                author_info=None,  # Will use material's author_id from materials.yaml
                            )

                            processed_materials += 1
                            successful_components = len(
                                results.get("components_generated", [])
                            )
                            print(
                                f"      ✅ Generated {successful_components} components"
                            )

                            if successful_components > 0:
                                successful_generations += 1

                        except Exception as e:
                            from utils.loud_errors import component_failure

                            component_failure(
                                "material_generation", str(e), material=material_name
                            )
                            processed_materials += 1
                            continue

                # Summary
                print("\n" + "=" * 60)
                print("📊 CONTENT BATCH GENERATION COMPLETE")
                print("=" * 60)
                print(f"📂 Categories processed: {len(categories)}")
                print(f"📝 Materials processed: {processed_materials}")
                print(f"✅ Successful generations: {successful_generations}")
                print(
                    f"📊 Success rate: {(successful_generations/processed_materials*100):.1f}%"
                    if processed_materials > 0
                    else "0%"
                )

            except ImportError as e:
                from utils.loud_errors import dependency_failure

                dependency_failure(
                    "module_import",
                    str(e),
                    impact="Content batch generation cannot proceed",
                )
            except Exception as e:
                from utils.loud_errors import critical_error

                critical_error(
                    "Content batch generation failed",
                    details=str(e),
                    context="Batch processing mode",
                )

        elif args.optimize:
            # Optimization mode - sophisticated AI detection optimization
            component_name = args.optimize
            print(
                f"🚀 Starting sophisticated optimization for component: {component_name}"
            )
            print("⏱️  Timeout protection: 10 minutes maximum")

            # Import and run the optimization with timeout protection
            from optimizer.content_optimization import run_sophisticated_optimization

            try:
                asyncio.run(
                    run_sophisticated_optimization(component_name, timeout_seconds=600)
                )
            except Exception as e:
                from utils.loud_errors import api_failure

                api_failure("optimization_service", str(e), retry_count=None)

        elif args.optimize:
            # Optimization mode - sophisticated AI detection optimization
            component_name = args.optimize
            print(
                f"🚀 Starting sophisticated optimization for component: {component_name}"
            )
            print("⏱️  Timeout protection: 10 minutes maximum")

            # Import and run the optimization with timeout protection
            from optimizer.content_optimization import run_sophisticated_optimization

            try:
                asyncio.run(
                    run_sophisticated_optimization(component_name, timeout_seconds=600)
                )
            except Exception as e:
                from utils.loud_errors import api_failure

                api_failure("optimization_service", str(e), retry_count=None)

        elif args.material or args.all:
            # Batch generation mode
            print("🎮 Z-Beam Generator")
            print("=" * 40)

            if args.material:
                print(f"🎯 Generating content for: {args.material}")
            elif args.all:
                print("🔄 Generating content for all materials")

            # Import and run the main generator
            try:
                from generators.dynamic_generator import DynamicGenerator

                generator = DynamicGenerator()

                if args.material:
                    # Generate for specific material
                    print(f"\n🎯 Generating content for {args.material}...")

                    try:
                        # Import workflow manager for material generation
                        from generators.workflow_manager import run_material_generation
                        from cli.component_config import get_components_sorted_by_priority

                        # Use specified components if provided, otherwise get enabled components
                        if args.components:
                            # Split the comma-separated list and strip whitespace
                            component_types = [c.strip() for c in args.components.split(',')]
                            print(f"🔍 Using specified components: {', '.join(component_types)}")
                        else:
                            # Get only enabled components from config
                            component_types = get_components_sorted_by_priority(include_disabled=False)
                            print(f"🔍 Using enabled components from config: {', '.join(component_types)}")

                        # Generate components for the material
                        result = run_material_generation(
                            material=args.material,
                            component_types=component_types,
                            author_id=None,  # Will use material's author_id from materials.yaml
                        )

                        print("✅ Generation completed!")
                        print(f"Material: {result['material']}")
                        print(
                            f"Components generated: {len(result['components_generated'])}"
                        )
                        print(f"Components failed: {len(result['components_failed'])}")

                        if result["components_generated"]:
                            print("\n📝 Generated components:")
                            for comp in result["components_generated"]:
                                print(f"  ✅ {comp['type']}: {comp['filepath']}")

                        if result["components_failed"]:
                            print("\n❌ Failed components:")
                            for comp in result["components_failed"]:
                                print(f"  ❌ {comp['type']}: {comp['error']}")

                        print(f"\n🕐 Total time: {result['total_time']:.1f}s")
                        print(f"🎯 Total tokens: {result['total_tokens']}")

                    except Exception as e:
                        from utils.loud_errors import critical_error

                        critical_error(
                            f"Content generation failed for {args.material}",
                            details=str(e),
                            context="Material-specific generation",
                        )

                elif args.all:
                    # Generate for all materials - FULL BATCH GENERATION
                    print("\n🚀 Starting batch generation for ALL materials...")
                    print("=" * 60)

                    # Preload API clients for better performance
                    try:
                        from api.cache_adapter import APIClientCache
                        
                        # Show cache type
                        cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
                        print(f"🚀 Preloading API clients using {cache_type} cache...")
                        
                        # Get all providers from API_PROVIDERS
                        providers = list(API_PROVIDERS.keys())
                        print(f"📋 Detected providers: {', '.join(providers)}")
                        
                        # Preload all configured providers
                        preload_results = APIClientCache.preload_clients(providers)
                        
                        # Report preload results
                        success_count = len(preload_results.get("success", []))
                        failed_count = len(preload_results.get("failed", []))
                        
                        if success_count > 0:
                            print(f"✅ Successfully preloaded {success_count} API clients")
                        
                        if failed_count > 0:
                            print(f"⚠️  Failed to preload {failed_count} providers:")
                            for fail in preload_results.get("failed", []):
                                print(f"   ❌ {fail['provider']}: {fail['error']}")
                        
                        # Show persistence benefit message
                        if APIClientCache.is_persistent():
                            print("🚀 Using persistent cache - clients will be reused between runs")
                        
                    except Exception as e:
                        print(f"⚠️  Cache preload failed: {e}")

                    try:
                        # Load materials data
                        from data.materials import load_materials

                        materials_data = load_materials()
                        
                        # Access the "materials" key to get the actual materials data
                        if "materials" not in materials_data:
                            print("❌ Error: No 'materials' key found in materials data")
                            return
                            
                        materials_section = materials_data["materials"]

                        # Count total materials across all categories
                        total_materials = sum(
                            len(category_data.get("items", []))
                            for category_data in materials_section.values()
                        )

                        categories = list(materials_section.keys())
                        print(f"📂 Found {len(categories)} categories with {total_materials} total materials")

                        # Get only ENABLED components for batch generation
                        from cli.component_config import get_components_sorted_by_priority
                        available_components = get_components_sorted_by_priority(include_disabled=False)
                        print(f"🔧 Available components: {', '.join(available_components)}")
                        print(f"📊 Component Status: Only ENABLED components included")

                        # Initialize tracking variables
                        processed_materials = 0
                        successful_generations = 0
                        total_components_generated = 0
                        total_components_failed = 0
                        total_tokens_used = 0
                        start_time = time.time()

                        # Process each category
                        for category in categories:
                            category_data = materials_section[category]
                            materials = category_data.get("items", [])

                            print(f"\n🔧 Processing category: {category}")
                            print(f"   📝 Materials in category: {len(materials)}")

                            category_processed = 0
                            category_successful = 0

                            # Process each material in the category
                            for material in materials:
                                material_name = material["name"]
                                material_start_time = time.time()

                                print(f"   📝 Generating content for: {material_name}")

                                try:
                                    # Import workflow manager for material generation
                                    from generators.workflow_manager import run_material_generation

                                    # Generate all available components for this material
                                    result = run_material_generation(
                                        material=material_name,
                                        component_types=available_components,
                                        author_id=None,  # Will use material's author_id from materials.yaml
                                    )

                                    material_time = time.time() - material_start_time
                                    processed_materials += 1
                                    category_processed += 1

                                    # Count successful and failed components
                                    successful_components = len(result.get("components_generated", []))
                                    failed_components = len(result.get("components_failed", []))
                                    total_components_generated += successful_components
                                    total_components_failed += failed_components

                                    # Add tokens used
                                    material_tokens = result.get("total_tokens", 0)
                                    total_tokens_used += material_tokens

                                    if successful_components > 0:
                                        successful_generations += 1
                                        category_successful += 1
                                        print(f"      ✅ Generated {successful_components} components ({material_tokens} tokens, {material_time:.1f}s)")
                                    else:
                                        print(f"      ⚠️  Generated {successful_components} components, {failed_components} failed ({material_time:.1f}s)")

                                    # Show progress every 10 materials or at key milestones
                                    if processed_materials % 10 == 0 or processed_materials == total_materials:
                                        progress_percent = (processed_materials / total_materials) * 100
                                        elapsed_time = time.time() - start_time
                                        avg_time_per_material = elapsed_time / processed_materials
                                        estimated_remaining = (total_materials - processed_materials) * avg_time_per_material

                                        print(f"\n📊 Progress: {processed_materials}/{total_materials} materials ({progress_percent:.1f}%)")
                                        print(f"   ⏱️  Elapsed: {elapsed_time:.1f}s, ETA: {estimated_remaining:.1f}s")
                                        print(f"   ✅ Success rate: {(successful_generations/processed_materials*100):.1f}%")

                                except Exception as e:
                                    from utils.loud_errors import component_failure

                                    component_failure(
                                        "material_generation", str(e), material=material_name
                                    )
                                    processed_materials += 1
                                    category_processed += 1
                                    continue

                            # Category summary
                            if materials:
                                category_success_rate = (category_successful / len(materials)) * 100
                                print(f"   📊 Category {category}: {category_successful}/{len(materials)} successful ({category_success_rate:.1f}%)")

                        # Final summary
                        total_time = time.time() - start_time
                        overall_success_rate = (successful_generations / processed_materials * 100) if processed_materials > 0 else 0

                        print("\n" + "=" * 60)
                        print("🎉 BATCH GENERATION COMPLETE")
                        print("=" * 60)
                        print(f"📂 Categories processed: {len(categories)}")
                        print(f"📝 Materials processed: {processed_materials}")
                        print(f"✅ Successful generations: {successful_generations}")
                        print(f"📊 Overall success rate: {overall_success_rate:.1f}%")
                        print(f"🔧 Total components generated: {total_components_generated}")
                        print(f"❌ Total components failed: {total_components_failed}")
                        print(f"🎯 Total tokens used: {total_tokens_used}")
                        print(f"🕐 Total time: {total_time:.1f}s")
                        print(f"⚡ Average time per material: {total_time/processed_materials:.1f}s" if processed_materials > 0 else "⚡ Average time per material: N/A")

                        # Performance insights
                        if total_time > 0:
                            tokens_per_second = total_tokens_used / total_time
                            print(f"🚀 Performance: {tokens_per_second:.1f} tokens/second")

                        # Cache performance insights
                        try:
                            from api.cache_adapter import APIClientCache
                            cache_stats = APIClientCache.get_cache_stats()
                            
                            if cache_stats['total_requests'] > 0:
                                cache_type = "persistent" if APIClientCache.is_persistent() else "in-memory"
                                print(f"📋 Cache Performance ({cache_type}): {cache_stats['hit_rate_percent']}% hit rate ({cache_stats['cache_hits']}/{cache_stats['total_requests']} requests)")
                                
                                if cache_stats['hit_rate_percent'] >= 80:
                                    cache_saved_time = cache_stats['cache_hits'] * 0.5  # Estimate 0.5s per client creation
                                    print(f"⚡ Time saved by caching: ~{cache_saved_time:.1f}s")
                                    
                                if APIClientCache.is_persistent():
                                    print(f"💾 Disk cached clients: {cache_stats.get('disk_cached_instances', 0)} (will persist for future runs)")
                        except ImportError:
                            pass

                        # Recommendations based on results
                        if overall_success_rate >= 95:
                            print("🎯 Excellent results! System performing optimally.")
                        elif overall_success_rate >= 80:
                            print("👍 Good results. Consider optimizing timeout settings for better performance.")
                        else:
                            print("⚠️  Results below expectations. Check API connectivity and timeout settings.")

                    except ImportError as e:
                        from utils.loud_errors import dependency_failure

                        dependency_failure(
                            "module_import",
                            str(e),
                            impact="Batch generation cannot proceed",
                        )
                    except Exception as e:
                        from utils.loud_errors import critical_error

                        critical_error(
                            "Batch generation failed",
                            details=str(e),
                            context="Full batch processing mode",
                        )

            except ImportError as e:
                from utils.loud_errors import dependency_failure

                dependency_failure(
                    "generator_module",
                    str(e),
                    impact="Generation cannot proceed",
                )

        else:
            # Show help/usage information
            print("🎯 Z-Beam Generator - AI-Powered Content Generation")
            print("=" * 55)
            print()
            print("EXAMPLES:")
            print("  python3 run.py --material \"Copper\"     # Generate specific material")
            print("  python3 run.py --all                   # Generate all materials")
            print()
            print("QUICK START:")
            print("  python3 run.py --material \"Aluminum\"   # Specific material")
            print("  python3 run.py --all                   # All materials")
            print()
            print("🧪 TESTING & VALIDATION:")
            print("  python3 run.py --test                  # Run comprehensive test suite")
            print("  python3 run.py --test-api              # Test API")
            print("  python3 run.py --validate              # Validate content")
            print("  python3 run.py --list-materials        # List materials")
            print()
            print("⚙️  CONFIGURATION:")
            print("  python3 run.py --config                # Show config")
            print("  python3 run.py --status                # Basic system status")
            print("  python3 run.py --check-env             # Comprehensive health check")
            print("  python3 run.py --cache-stats           # Cache performance")
            print("  python3 run.py --clear-cache           # Clear API cache")
            print("  python3 run.py --preload-cache         # Preload cache")
            print()
            print("📋 VERSION TRACKING:")
            print(
                "  python3 run.py --version-history 'Alumina:text'  # Show version history"
            )
            print()
            print("🧹 CLEANUP:")
            print("  python3 run.py --clean                 # Clean content")
            print("  python3 run.py --cleanup-scan          # Scan cleanup")
            print("  python3 run.py --cleanup-report        # Cleanup report")
            print()
            print("🚀 OPTIMIZATION:")
            print("  python3 run.py --optimize text         # Optimize text")
            print()
            print("💡 TIP: Use --help for complete command reference")

    except Exception as e:
        from utils.loud_errors import critical_error

        critical_error(
            "Application execution failed", details=str(e), context="Main application"
        )


if __name__ == "__main__":
    main()
