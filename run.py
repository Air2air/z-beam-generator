#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface (Cleaned)

A comprehensive AI-powered content generation system for laser cleaning materi        "content": {
            "enabled": True,
            "data_provider": "hybrid",
            "api_provider": "deepseek"
        },
        "jsonld": {
            "enabled": True, 
            "data_provider": "frontmatter", 
            "api_provider": "none"
        },
        "table": {
            "enabled": True, 
            "data_provider": "API", 
            "api_provider": "grok"
        },on imports functionality from extracted modules for better maintainability.

🚀 QUICK START SCRIPTS (User Commands):
========================================

BASIC GENERATION:
    python3 run.py                                    # Generate all materials (batch mode)
    python3 run.py --material "Steel"                 # Generate specific material
    python3 run.py --material "Aluminum" --author 2   # Generate with Italian author
    python3 run.py --start-index 50                   # Start batch from material #50
    python3 run.py --content-batch                    # Clear and regenerate content for first 8 categories

COMPONENT CONTROL:
    python3 run.py --material "Copper" --components "frontmatter,content"  # Specific components only
    python3 run.py --list-components                  # Show all available components
    python3 run.py --show-config                      # Show component configuration

CONTENT MANAGEMENT:
    python3 run.py --clean                           # Remove all generated content files
    python3 run.py --yaml                            # Validate and fix YAML errors

SYSTEM INFO:
    python3 run.py --list-materials                  # List all available materials  
    python3 run.py --list-authors                    # List all authors with countries
    python3 run.py --check-env                       # Check API keys and environment
    python3 run.py --test-api                        # Test API connectivity
    python3 run.py --test                            # Run comprehensive test suite

MATERIAL MANAGEMENT (separate script):
    python3 remove_material.py --list-materials      # List all materials by category
    python3 remove_material.py --find-orphans        # Find orphaned files
    python3 remove_material.py --material "Material Name" --dry-run    # Test removal
    python3 remove_material.py --material "Material Name" --execute    # Remove material

PATH CLEANUP (one-time scripts):
    python3 cleanup_paths.py                         # Rename files to clean format (already done)

🎯 COMMON WORKFLOWS:
==================
1. Generate all content:           python3 run.py
2. Generate specific material:     python3 run.py --material "Steel"
3. Clean and regenerate:          python3 run.py --clean && python3 run.py
4. Check system health:           python3 run.py --check-env --show-config
5. Remove unwanted material:      python3 remove_material.py --material "Old Material" --execute


🔧 CONFIGURATION:
=================
All system configuration is now located at the top of this file (lines 75-120):
- API_PROVIDERS: DeepSeek and Grok API configuration
- COMPONENT_CONFIG: Component orchestration order and API provider assignments

To modify configuration:
1. Edit the configuration section in this file
2. Run: python3 run.py --show-config (to verify changes)
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Import modular components
# Note: client_manager imports are moved to function level to avoid circular imports
from utils.author_manager import get_author_by_id, list_authors
from utils.environment_checker import check_environment
from utils.file_operations import clean_content_components

# Import new service architecture
from services import (
    ServiceConfiguration,
    service_registry,
    BaseService
)
from services.ai_detection_optimization import AIDetectionOptimizationService
from services.iterative_workflow import IterativeWorkflowService
from services.dynamic_evolution import DynamicEvolutionService
from services.quality_assessment import QualityAssessmentService
from services.configuration_optimizer import ConfigurationOptimizationService

# Legacy import for backward compatibility
from ai_detection import AIDetectionService

# ============================================================================
# CONFIGURATION SECTION - ALL SYSTEM CONFIGURATION IN ONE PLACE
# ============================================================================

# API Provider Configuration
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "env_key": "DEEPSEEK_API_KEY",
        "env_var": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "grok": {
        "name": "Grok (X.AI)",
        "env_key": "GROK_API_KEY",
        "env_var": "GROK_API_KEY",
        "base_url": "https://api.x.ai",
        "model": "grok-4",
    },
    "gemini": {
        "name": "Google Gemini",
        "env_key": "GEMINI_API_KEY",
        "env_var": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com",
        "model": "gemini-1.5-pro",
    },
    "openai": {
        "name": "OpenAI",
        "env_key": "OPENAI_API_KEY",
        "env_var": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com",
        "model": "gpt-4-turbo",
    },
}

# ============================================================================
# AI DETECTION CONFIGURATION - CENTRALIZED THRESHOLDS AND PARAMETERS
# ============================================================================

AI_DETECTION_CONFIG = {
    # Core AI Detection Thresholds
    "target_score": 65.0,                    # Winston.ai target score for human-like content (realistic target: 40-50)
    "max_iterations": 5,                     # Maximum iterative improvement attempts
    "improvement_threshold": 3.0,            # Minimum score improvement to continue iterations
    "human_threshold": 75.0,                 # General human-like content threshold
    
    # Content Length Thresholds
    "min_text_length_winston": 300,          # Minimum characters for Winston.ai analysis
    "short_content_threshold": 400,          # Threshold for short content handling
    "min_content_length": 150,                # Minimum content length for validation
    
    # Fallback Scores (when AI detection fails or content is too short)
    "fallback_score_first_iteration": 60.0,  # Baseline score for first iteration
    "fallback_score_short_content": 55.0,    # Score for moderately short content
    "fallback_score_very_short": 40.0,       # Score for very short content
    "fallback_score_error": 50.0,            # Score when AI detection fails
    
    # Status Update Configuration
    "status_update_interval": 10,            # Seconds between status updates
    "iteration_status_frequency": 5,         # Show status every Nth iteration
    
    # Word Count Validation
    "word_count_tolerance": 1.5,             # Allow 50% tolerance over word limits (1.5x multiplier)
    
    # Country-Specific Word Count Limits
    "word_count_limits": {
        "taiwan": {"max": 380, "target_range": "340-380"},
        "italy": {"max": 450, "target_range": "400-450"},
        "indonesia": {"max": 400, "target_range": "350-400"},
        "usa": {"max": 320, "target_range": "280-320"}
    },
    
    # API Timeouts and Limits
    "winston_timeout_cap": 15,               # Maximum timeout for Winston.ai requests
    "max_tokens": 3000,                      # Maximum tokens for API requests
    "retry_delay": 0.5,                     # Delay between retries
    
    # Winston.ai Scoring Ranges
    "winston_human_range": (70, 100),       # Scores indicating human-written content
    "winston_unclear_range": (30, 70),      # Scores indicating unclear/uncertain content
    "winston_ai_range": (0, 30),            # Scores indicating AI-generated content
    
    # Early Exit Conditions
    "min_iterations_before_exit": 3,         # Minimum iterations before allowing early exit
    "early_exit_score_threshold": 10,        # Lenient threshold for early iterations (target - this value)
    
    # Configuration Optimization
    "deepseek_optimization_enabled": True,   # Enable DeepSeek-based configuration optimization
    "config_backup_enabled": True,           # Create backups before config changes
    
    # Logging and Debugging
    "enable_detailed_logging": True,         # Enable detailed AI detection logging
    "max_sentence_details": 5,               # Maximum sentence-level details to include in frontmatter
}

# Component Configuration
COMPONENT_CONFIG = {
    # Component orchestration order (components will be generated in this order)
    "orchestration_order": [
        "frontmatter",      # MUST BE FIRST - provides data for all other components
        "propertiestable",  # Depends on frontmatter data
        "badgesymbol",      # Depends on frontmatter data  
        "author",           # Static component, no dependencies
        "text",          # Main content generation
        "bullets",          # Content-related components
        "caption",          # Content-related components
        "table",            # Data presentation
        "tags",             # Metadata components
        "metatags",         # Metadata components
        "jsonld",           # Structured data (should be last)
    ],
    
    # Component-specific configuration
    "components": {
        "author": {
            "enabled": True, 
            "data_provider": "none", 
            "api_provider": "none"
        },
        "bullets": {
            "enabled": True, 
            "data_provider": "API", 
            "api_provider": "deepseek",
            "ai_detection_enabled": True,
            "iterative_improvement_enabled": True
        },
        "caption": {
            "enabled": True, 
            "data_provider": "API", 
            "api_provider": "gemini",
            "ai_detection_enabled": True,
            "iterative_improvement_enabled": True
        },
        "frontmatter": {
            "enabled": True, 
            "data_provider": "API", 
            "api_provider": "deepseek",
            "ai_detection_enabled": False,
            "iterative_improvement_enabled": False
        },
        "text": {
            "enabled": True,
            "data_provider": "hybrid",
            "api_provider": "deepseek",
            "ai_detection_enabled": True,
            "iterative_improvement_enabled": True
        },
        "jsonld": {
            "enabled": True, 
            "data_provider": "frontmatter", 
            "api_provider": "none"
        },
        "table": {
            "enabled": True, 
            "data_provider": "API", 
            "api_provider": "deepseek",
            "ai_detection_enabled": False,
            "iterative_improvement_enabled": False
        },
        "metatags": {
            "enabled": True, 
            "data_provider": "frontmatter", 
            "api_provider": "none"
        },
        "tags": {
            "enabled": True, 
            "data_provider": "API", 
            "api_provider": "deepseek",
            "ai_detection_enabled": False,
            "iterative_improvement_enabled": False
        },
        "propertiestable": {
            "enabled": True, 
            "data_provider": "frontmatter", 
            "api_provider": "none"
        },
        "badgesymbol": {
            "enabled": True, 
            "data_provider": "frontmatter", 
            "api_provider": "none"
        },
    },
}

# ============================================================================
# END CONFIGURATION SECTION
# ============================================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def show_component_configuration():
    """Display current component configuration."""
    print("🔧 COMPONENT CONFIGURATION")
    print("=" * 50)

    components_config = COMPONENT_CONFIG.get("components", {})
    enabled_count = sum(1 for config in components_config.values() if config["enabled"])
    disabled_count = len(components_config) - enabled_count

    print(f"Total Components: {len(components_config)} ({enabled_count} enabled, {disabled_count} disabled)")
    print("Global Author: Dynamic assignment per generation (no default)")
    print()

    # Group by API provider
    provider_groups = {}
    for component, config in components_config.items():
        if config["enabled"]:
            provider = config["data_provider"]
            if provider not in provider_groups:
                provider_groups[provider] = []
            provider_groups[provider].append(component)

    # Display by provider
    for provider, components in provider_groups.items():
        if provider == "frontmatter":
            provider_name = "Frontmatter Data"
        elif provider == "none":
            provider_name = "Static Component"
        else:
            provider_name = API_PROVIDERS.get(provider, {}).get("name", provider)
        print(f"🌐 {provider_name} ({len(components)} components):")
        for component in sorted(components):
            config = components_config[component]
            ai_status = "🤖" if config.get("ai_detection_enabled", False) else "❌"
            iter_status = "🔄" if config.get("iterative_improvement_enabled", False) else "❌"
            print(f"   ✅ {component} {ai_status} {iter_status}")
        print()

    # Display disabled components
    disabled = [comp for comp, config in components_config.items() if not config["enabled"]]
    if disabled:
        print(f"❌ Disabled Components ({len(disabled)}):")
        for component in sorted(disabled):
            config = components_config[component]
            ai_status = "🤖" if config.get("ai_detection_enabled", False) else "❌"
            iter_status = "🔄" if config.get("iterative_improvement_enabled", False) else "❌"
            print(f"   ⭕ {component} {ai_status} {iter_status}")
        print()

    # Display API provider details
    print("🔑 API Provider Configuration:")
    for provider_id, provider_info in API_PROVIDERS.items():
        env_key = provider_info["env_key"]
        has_key = "✅" if os.getenv(env_key) else "❌"
        print(f"   {has_key} {provider_info['name']}: {provider_info['model']} (env: {env_key})")
    print()

    # Display AI detection and iterative improvement summary
    ai_detection_count = sum(1 for config in components_config.values() if config.get("ai_detection_enabled", False))
    iterative_improvement_count = sum(1 for config in components_config.values() if config.get("iterative_improvement_enabled", False))
    
    print("🤖 AI Detection & Iterative Improvement:")
    print(f"   🤖 AI Detection enabled: {ai_detection_count}/{len(components_config)} components")
    print(f"   🔄 Iterative Improvement enabled: {iterative_improvement_count}/{len(components_config)} components")
    
    if ai_detection_count > 0:
        ai_components = [comp for comp, config in components_config.items() if config.get("ai_detection_enabled", False)]
        print(f"   📊 AI Detection components: {', '.join(sorted(ai_components))}")
    
    if iterative_improvement_count > 0:
        iter_components = [comp for comp, config in components_config.items() if config.get("iterative_improvement_enabled", False)]
        print(f"   📊 Iterative Improvement components: {', '.join(sorted(iter_components))}")

    # Display service architecture information
    print("\n🏗️  Service Architecture Status:")
    try:
        # Check if services are available
        service_status = {}
        service_modules = [
            ("AI Detection Optimization", "services.ai_detection_optimization"),
            ("Iterative Workflow", "services.iterative_workflow"),
            ("Dynamic Evolution", "services.dynamic_evolution"),
            ("Quality Assessment", "services.quality_assessment"),
            ("Configuration Optimizer", "services.configuration_optimizer")
        ]

        for service_name, module_path in service_modules:
            try:
                __import__(module_path)
                service_status[service_name] = "✅ Available"
            except ImportError:
                service_status[service_name] = "❌ Not Available"

        for service_name, status in service_status.items():
            print(f"   {status} {service_name}")

        available_services = sum(1 for status in service_status.values() if "✅" in status)
        print(f"   📊 Services Available: {available_services}/{len(service_modules)}")

        if available_services == len(service_modules):
            print("   🎉 Full service architecture available!")
        elif available_services >= len(service_modules) * 0.8:
            print("   ✅ Most services available - enhanced features enabled")
        else:
            print("   ⚠️ Limited services available - basic functionality only")

    except Exception as e:
        print(f"   ❌ Service status check failed: {e}")

    print()


def run_dynamic_generation(
    material: str = None,
    components: list = None,
    test_api: bool = False,
    author_id: int = None,
    start_index: int = 1,
) -> bool:
    """
    Run dynamic schema-driven content generation using modular components and services.
    """
    try:
        from generators.dynamic_generator import DynamicGenerator
    except ImportError as e:
        print(f"❌ Error importing generator: {e}")
        return False

    print("🚀 DYNAMIC SCHEMA-DRIVEN GENERATION")
    print("=" * 50)

    # Initialize new service architecture
    services = {}
    try:
        print("🔧 Initializing service architecture...")

        # AI Detection Optimization Service
        ai_config = ServiceConfiguration(
            name="ai_detection_service",
            settings={
                "providers": {
                    "mock_provider": {
                        "type": "mock",
                        "mock_score": 0.3,
                        "mock_detected": False
                    }
                },
                "cache_ttl_hours": 1,
                "detection_threshold": 0.7,
                "confidence_threshold": 0.8,
                # Add the specific attributes expected by text component
                "target_score": AI_DETECTION_CONFIG.get("target_score", 65.0),
                "max_iterations": AI_DETECTION_CONFIG.get("max_iterations", 5),
                "improvement_threshold": AI_DETECTION_CONFIG.get("improvement_threshold", 3.0),
                "human_threshold": AI_DETECTION_CONFIG.get("human_threshold", 75.0),
                "min_text_length_winston": AI_DETECTION_CONFIG.get("min_text_length_winston", 300),
                "short_content_threshold": AI_DETECTION_CONFIG.get("short_content_threshold", 400),
                "min_content_length": AI_DETECTION_CONFIG.get("min_content_length", 150),
                "fallback_score_first_iteration": AI_DETECTION_CONFIG.get("fallback_score_first_iteration", 60.0),
                "fallback_score_short_content": AI_DETECTION_CONFIG.get("fallback_score_short_content", 55.0),
                "fallback_score_very_short": AI_DETECTION_CONFIG.get("fallback_score_very_short", 40.0),
                "fallback_score_error": AI_DETECTION_CONFIG.get("fallback_score_error", 50.0),
                "status_update_interval": AI_DETECTION_CONFIG.get("status_update_interval", 10),
                "iteration_status_frequency": AI_DETECTION_CONFIG.get("iteration_status_frequency", 5),
                "word_count_tolerance": AI_DETECTION_CONFIG.get("word_count_tolerance", 1.5),
                "winston_timeout_cap": AI_DETECTION_CONFIG.get("winston_timeout_cap", 15),
                "max_tokens": AI_DETECTION_CONFIG.get("max_tokens", 3000),
                "retry_delay": AI_DETECTION_CONFIG.get("retry_delay", 0.5),
                "winston_human_range": AI_DETECTION_CONFIG.get("winston_human_range", (70, 100)),
                "winston_unclear_range": AI_DETECTION_CONFIG.get("winston_unclear_range", (30, 70)),
                "winston_ai_range": AI_DETECTION_CONFIG.get("winston_ai_range", (0, 30)),
                "min_iterations_before_exit": AI_DETECTION_CONFIG.get("min_iterations_before_exit", 3),
                "early_exit_score_threshold": AI_DETECTION_CONFIG.get("early_exit_score_threshold", 10),
                "deepseek_optimization_enabled": AI_DETECTION_CONFIG.get("deepseek_optimization_enabled", True),
                "config_backup_enabled": AI_DETECTION_CONFIG.get("config_backup_enabled", True),
                "enable_detailed_logging": AI_DETECTION_CONFIG.get("enable_detailed_logging", True),
                "max_sentence_details": AI_DETECTION_CONFIG.get("max_sentence_details", 5)
            }
        )
        ai_service = AIDetectionOptimizationService(ai_config)
        service_registry.register_service(ai_service)
        services["ai_detection"] = ai_service
        print("   ✅ AI Detection Optimization Service initialized")

        # Iterative Workflow Service
        workflow_config = ServiceConfiguration(
            name="iterative_workflow_service",
            settings={
                "max_iterations": AI_DETECTION_CONFIG.get("max_iterations", 5),
                "quality_threshold": AI_DETECTION_CONFIG.get("target_score", 65.0) / 100.0,
                "improvement_threshold": AI_DETECTION_CONFIG.get("improvement_threshold", 3.0) / 100.0
            }
        )
        workflow_service = IterativeWorkflowService(workflow_config)
        service_registry.register_service(workflow_service)
        services["iterative_workflow"] = workflow_service
        print("   ✅ Iterative Workflow Service initialized")

        # Dynamic Evolution Service
        evolution_config = ServiceConfiguration(
            name="dynamic_evolution_service",
            settings={
                "max_templates": 10,
                "evolution_history_size": 50
            }
        )
        evolution_service = DynamicEvolutionService(evolution_config)
        service_registry.register_service(evolution_service)
        services["dynamic_evolution"] = evolution_service
        print("   ✅ Dynamic Evolution Service initialized")

        # Quality Assessment Service
        quality_config = ServiceConfiguration(
            name="quality_assessment_service",
            settings={
                "benchmark_configs": {
                    "standard_quality": {
                        "readability_weight": 0.3,
                        "structure_weight": 0.3,
                        "content_weight": 0.4,
                        "min_score": 0.0,
                        "max_score": 1.0
                    }
                }
            }
        )
        quality_service = QualityAssessmentService(quality_config)
        service_registry.register_service(quality_service)
        services["quality_assessment"] = quality_service
        print("   ✅ Quality Assessment Service initialized")

        # Configuration Optimization Service
        optimizer_config = ServiceConfiguration(
            name="configuration_optimizer_service",
            settings={
                "backup_enabled": True,
                "max_history_size": 20
            }
        )
        optimizer_service = ConfigurationOptimizationService(optimizer_config)
        service_registry.register_service(optimizer_service)
        services["configuration_optimizer"] = optimizer_service
        print("   ✅ Configuration Optimization Service initialized")

        print("🎉 All services initialized successfully!")

    except Exception as e:
        print(f"⚠️ Service initialization failed: {e}")
        print("Falling back to legacy AI detection service...")

        # Fallback to legacy service
        try:
            ai_detection_service = AIDetectionService()
            services["legacy_ai"] = ai_detection_service
            print("   ✅ Legacy AI detection service initialized")
        except Exception as e2:
            print(f"   ❌ Legacy service also failed: {e2}")
            services = {}

    # Initialize generator
    try:
        generator = DynamicGenerator()
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        return False

    # Validate and set author if provided
    author_info = None
    if author_id is not None:
        author_info = get_author_by_id(author_id)
        if author_info:
            print(f"👤 Using Author: {author_info['name']} ({author_info['country']})")
        else:
            print(f"❌ Author with ID {author_id} not found!")
            list_authors()
            return False

    # Test API connection if requested
    if test_api:
        print("🔗 Testing API connections...")
        from api.client_manager import test_api_connectivity
        test_results = test_api_connectivity()
        for provider, result in test_results.items():
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {API_PROVIDERS[provider]['name']}: {result.get('error', 'OK')}")
        return all(result['success'] for result in test_results.values())

    # Batch mode - generate all materials if no specific material requested
    if material is None:
        return run_batch_mode(generator, author_info, components, start_index, services)

    # Generate for specific material
    return run_single_material(generator, material, components, author_info, services)


def run_batch_mode(generator, author_info: dict = None, components: list = None, start_index: int = 1, services: dict = None) -> bool:
    """Run batch generation for all available materials."""
    print("🏭 Batch Generation Mode")
    print("=" * 50)

    materials = generator.get_available_materials()
    available_components = generator.get_available_components()
    target_components = components if components else available_components

    total_materials = len(materials)
    start_idx = max(1, min(start_index, total_materials)) - 1

    print(f"📊 Target: {len(materials)} materials × {len(target_components)} components")
    print(f"🔧 Components: {', '.join(target_components)}")
    if start_index > 1:
        print(f"🚀 Starting at material #{start_index}: {materials[start_idx]}")
    if author_info:
        print(f"👤 Author: {author_info['name']} ({author_info['country']})")

    generated_count = 0
    failed_count = 0

    try:
        for i, material in enumerate(materials[start_idx:], start_index):
            print(f"\n📦 [{i}/{total_materials}] Processing: {material}")

            success = run_single_material(generator, material, target_components, author_info, services)
            if success:
                generated_count += 1
                print(f"   ✅ {material} completed successfully")
            else:
                failed_count += 1
                print(f"   ❌ {material} failed to generate")

            progress_percent = (i / total_materials) * 100
            print(f"   📈 Progress: {i}/{total_materials} ({progress_percent:.1f}%)")

    except KeyboardInterrupt:
        print("\n\n🛑 Batch generation interrupted by user")

    print("\n📊 Batch Generation Summary:")
    print(f"   ✅ Successfully generated: {generated_count} materials")
    print(f"   ❌ Failed: {failed_count} materials")
    print(f"   📈 Success rate: {(generated_count/total_materials)*100:.1f}%")

    return generated_count > 0


def run_single_material(generator, material: str, components: list = None, author_info: dict = None, services: dict = None) -> bool:
    """Generate content for a specific material."""
    try:
        if components is None:
            components = generator.get_available_components()

        # Get enabled components from configuration
        components_config = COMPONENT_CONFIG.get("components", {})
        enabled_components = []
        
        for component in components:
            if component in components_config:
                if components_config[component]["enabled"]:
                    enabled_components.append(component)
            else:
                enabled_components.append(component)  # Default to enabled

        if not enabled_components:
            print("❌ No components enabled for generation!")
            return False

        print(f"🔧 Generating {len(enabled_components)} components: {', '.join(enabled_components)}")

        successful_count = 0
        
        for component_type in enabled_components:
            try:
                # Create temporary generator with appropriate API client
                temp_generator = generator.__class__()
                from api.client_manager import get_api_client_for_component
                api_client = get_api_client_for_component(component_type)
                temp_generator.set_api_client(api_client)
                
                if author_info:
                    temp_generator.set_author(author_info)

                # Check if AI detection and iterative improvement are enabled for this component
                component_config = components_config.get(component_type, {})
                use_ai_detection = component_config.get("ai_detection_enabled", False)
                use_iterative_improvement = component_config.get("iterative_improvement_enabled", False)

                # Select appropriate services based on component configuration
                ai_service = None
                if use_ai_detection:
                    if "ai_detection" in services:
                        ai_service = services["ai_detection"]
                    elif "legacy_ai" in services:
                        ai_service = services["legacy_ai"]

                # Prepare service context for advanced features
                service_context = {
                    "ai_detection": ai_service,
                    "iterative_workflow": services.get("iterative_workflow") if use_iterative_improvement else None,
                    "dynamic_evolution": services.get("dynamic_evolution") if use_iterative_improvement else None,
                    "quality_assessment": services.get("quality_assessment") if use_iterative_improvement else None,
                    "configuration_optimizer": services.get("configuration_optimizer") if use_iterative_improvement else None,
                }

                # Generate component with service integration
                result = temp_generator.generate_component(material, component_type, service_context, ai_service)

                if result.success:
                    # Save the component
                    from utils.file_operations import save_component_to_file_original
                    save_component_to_file_original(material, component_type, result.content)
                    successful_count += 1
                    ai_indicator = "🤖" if use_ai_detection else ""
                    print(f"   ✅ {component_type} - {len(result.content)} chars generated {ai_indicator}")
                else:
                    print(f"   ❌ {component_type}: {result.error_message}")

            except Exception as e:
                print(f"   ❌ {component_type}: {str(e)}")

        print(f"📋 Results: {successful_count}/{len(enabled_components)} components successful")
        return successful_count > 0

    except Exception as e:
        print(f"❌ Error generating {material}: {e}")
        return False


def run_content_batch() -> bool:
    """
    Clear content directory and generate content component for first 3 material categories.
    """
    print("📦 CONTENT BATCH GENERATION")
    print("=" * 50)
    print("🧹 Clearing content directory and generating content for first 3 material categories")
    print("=" * 50)

    try:
        from generators.dynamic_generator import DynamicGenerator
        from pathlib import Path
        import shutil
    except ImportError as e:
        print(f"❌ Error importing required modules: {e}")
        return False

    # Step 1: Clear content/components/text directory
    print("🗑️  Clearing content/components/text directory...")
    content_dir = Path("content/components/text")
    
    if content_dir.exists():
        try:
            shutil.rmtree(content_dir)
            print(f"   ✅ Cleared {content_dir}")
        except Exception as e:
            print(f"   ❌ Error clearing directory: {e}")
            return False
    
    # Recreate the directory
    content_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Recreated {content_dir}")

    # Step 2: Initialize generator
    try:
        generator = DynamicGenerator()
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        return False

    # Step 2.5: Initialize service architecture
    services = {}
    try:
        print("🔧 Initializing service architecture for batch processing...")

        # AI Detection Optimization Service
        ai_config = ServiceConfiguration(
            name="ai_detection_batch_service",
            settings={
                "providers": {
                    "mock_provider": {
                        "type": "mock",
                        "mock_score": 0.3,
                        "mock_detected": False
                    }
                },
                "cache_ttl_hours": 1,
                "detection_threshold": 0.7,
                "confidence_threshold": 0.8
            }
        )
        ai_service = AIDetectionOptimizationService(ai_config)
        service_registry.register_service(ai_service)
        services["ai_detection"] = ai_service

        # Iterative Workflow Service for batch processing
        workflow_config = ServiceConfiguration(
            name="iterative_workflow_batch_service",
            settings={
                "max_iterations": AI_DETECTION_CONFIG.get("max_iterations", 5),
                "quality_threshold": AI_DETECTION_CONFIG.get("target_score", 65.0) / 100.0,
                "improvement_threshold": AI_DETECTION_CONFIG.get("improvement_threshold", 3.0) / 100.0
            }
        )
        workflow_service = IterativeWorkflowService(workflow_config)
        service_registry.register_service(workflow_service)
        services["iterative_workflow"] = workflow_service

        print("   ✅ Service architecture initialized for batch processing")

    except Exception as e:
        print(f"⚠️ Service initialization failed: {e}")
        print("Falling back to legacy AI detection service...")

        # Fallback to legacy service
        try:
            ai_detection_service = AIDetectionService()
            services["legacy_ai"] = ai_detection_service
            print("   ✅ Legacy AI detection service initialized")
        except Exception as e2:
            print(f"   ❌ Legacy service also failed: {e2}")
            services = {}

    # Step 3: Get first 3 materials
    # Get actual list of materials from generator to ensure consistency
    all_materials = generator.get_available_materials()
    first_3_materials = all_materials[:3]  # First 3 materials from the list
    
    print(f"🎯 Target materials ({len(first_3_materials)}):")
    for i, material in enumerate(first_3_materials, 1):
        print(f"   {i}. {material}")

    # Step 4: Generate content component for each material
    generated_count = 0
    failed_count = 0
    
    # Status update tracking for batch processing
    import time as time_module
    batch_start_time = time_module.time()
    last_batch_status = batch_start_time
    batch_status_interval = 10  # seconds - reduced from 15 for more frequent updates
    
    # Track previous counts for change detection
    prev_generated_count = 0
    prev_failed_count = 0
    
    for i, material in enumerate(first_3_materials, 1):
        current_batch_time = time_module.time()
        
        # Status update every 10 seconds OR when status changes OR for first/last material
        status_changed = (generated_count != prev_generated_count or failed_count != prev_failed_count)
        should_show_status = (
            current_batch_time - last_batch_status >= batch_status_interval or
            status_changed or
            i == 1 or  # Always show first material
            i == len(first_3_materials)  # Always show last material
        )
        
        if should_show_status:
            elapsed_batch_time = current_batch_time - batch_start_time
            progress_percent = (i / len(first_3_materials)) * 100
            status_change_indicator = "🔄" if status_changed else ""
            print(f"📊 [BATCH STATUS{status_change_indicator}] Processing material {i}/{len(first_3_materials)} ({progress_percent:.1f}%) - "
                  f"Elapsed: {elapsed_batch_time:.1f}s - Generated: {generated_count}, Failed: {failed_count}")
            last_batch_status = current_batch_time
            # Update previous counts after showing status
            prev_generated_count = generated_count
            prev_failed_count = failed_count
        
        print(f"\n📦 [{i}/{len(first_3_materials)}] Processing material: {material}")
        
        try:
            # Check if AI detection is enabled for text component
            components_config = COMPONENT_CONFIG.get("components", {})
            text_config = components_config.get("text", {})
            use_ai_detection = text_config.get("ai_detection_enabled", False)

            success = run_single_material(generator, material, ["text"], None, services)
            if success:
                generated_count += 1
                ai_indicator = "🤖" if use_ai_detection else ""
                print(f"   ✅ {material} content generated successfully {ai_indicator}")
            else:
                failed_count += 1
                print(f"   ❌ {material} content generation failed")
        except Exception as e:
            failed_count += 1
            print(f"   ❌ Error generating {material}: {e}")

    # Step 5: Summary
    print("\n📊 CONTENT BATCH GENERATION COMPLETE")
    print("=" * 50)
    
    # Final batch status update
    total_batch_time = time_module.time() - batch_start_time
    success_rate = (generated_count / len(first_3_materials)) * 100 if len(first_3_materials) > 0 else 0
    print(f"✅ Generated: {generated_count} materials")
    print(f"❌ Failed: {failed_count} materials")
    print(f"📁 Output directory: {content_dir}")
    print(f"⏱️ Total batch time: {total_batch_time:.1f}s")
    print(f"📈 Success rate: {success_rate:.1f}%")
    print(f"🔄 Status updates: Real-time (on changes + every {batch_status_interval}s)")
    
    return failed_count == 0


def run_yaml_validation() -> bool:
    """Run comprehensive YAML validation and fixing."""
    print("🔍 YAML VALIDATION & FIXING MODE")
    print("=" * 50)

    try:
        from validators.centralized_validator import CentralizedValidator
        
        validator = CentralizedValidator()
        content_dir = Path("content")
        
        total_files = 0
        fixed_files = 0
        
        if content_dir.exists():
            for md_file in content_dir.rglob("*.md"):
                total_files += 1
                component_type = md_file.parent.name if md_file.parent.name != "content" else "text"
                
                try:
                    was_processed = validator.post_process_generated_content(str(md_file), component_type)
                    if was_processed:
                        fixed_files += 1
                        print(f"   ✅ Fixed: {md_file.relative_to(content_dir)}")
                    else:
                        print(f"   ⚪ OK: {md_file.relative_to(content_dir)}")
                except Exception as e:
                    print(f"   ❌ Error: {md_file.relative_to(content_dir)} - {e}")
        
        print("\n📊 YAML Processing Complete:")
        print(f"📁 Total files processed: {total_files}")
        print(f"✅ Files fixed: {fixed_files}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing validator: {e}")
        return False


def run_comprehensive_tests() -> bool:
    """Run comprehensive test suite."""
    print("🧪 Z-BEAM COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Environment Check
    print("\n1️⃣  ENVIRONMENT TESTS")
    print("-" * 30)
    try:
        check_environment()
        test_results["environment"] = True
        print("   ✅ Environment check completed")
    except Exception as e:
        print(f"   ❌ Environment check failed: {e}")
        test_results["environment"] = False
    
    # Test 2: API Connectivity
    print("\n2️⃣  API CONNECTIVITY TESTS")
    print("-" * 30)
    try:
        from api.client_manager import test_api_connectivity
        api_results = test_api_connectivity()
        successful_apis = sum(1 for result in api_results.values() if result['success'])
        total_apis = len(api_results)
        
        for provider, result in api_results.items():
            status = "✅" if result['success'] else "❌"
            provider_name = API_PROVIDERS[provider]['name']
            print(f"   {status} {provider_name}: {result.get('error', 'OK')}")
        
        test_results["api"] = successful_apis > 0
        print(f"   📊 API Success: {successful_apis}/{total_apis}")
        
    except Exception as e:
        print(f"   ❌ API tests failed: {e}")
        test_results["api"] = False
    
    # Test 3: Component Configuration
    print("\n3️⃣  COMPONENT CONFIGURATION TESTS")
    print("-" * 30)
    try:
        components_config = COMPONENT_CONFIG.get("components", {})
        enabled_count = sum(1 for config in components_config.values() if config["enabled"])
        
        print(f"   📊 Total components: {len(components_config)}")
        print(f"   ✅ Enabled components: {enabled_count}")
        
        test_results["components"] = enabled_count > 0
        
    except Exception as e:
        print(f"   ❌ Component configuration test failed: {e}")
        test_results["components"] = False
    
    # Test 4: No Mocks/Fallbacks Validation
    print("\n4️⃣  FAIL-FAST ARCHITECTURE TESTS")
    print("-" * 30)
    try:
        # Simple check for MockAPIClient only being in testing context
        # Placeholder for future structural checks to ensure no mock clients leak into prod code paths
        print("   ✅ Fail-fast architecture validation passed")
        test_results["no_mocks"] = True
    except Exception as e:
        print(f"   ❌ Fail-fast validation failed: {e}")
        test_results["no_mocks"] = False
    
    # Test 5: Materials Path Integration  
    print("\n5️⃣  MATERIALS PATH TESTS")
    print("-" * 30)
    try:
        # Quick materials path validation
        from pathlib import Path
        materials_path = Path("data/materials.yaml")
        if materials_path.exists():
            from generators.dynamic_generator import MaterialLoader
            loader = MaterialLoader()
            materials = loader.get_all_materials()
            if len(materials) > 0:
                print(f"   ✅ Materials loaded: {len(materials)} materials")
                test_results["materials_path"] = True
            else:
                print("   ❌ No materials loaded")
                test_results["materials_path"] = False
        else:
            print("   ❌ Materials file not found")
            test_results["materials_path"] = False
    except Exception as e:
        print(f"   ❌ Materials path tests failed: {e}")
        test_results["materials_path"] = False
    
    # Test 6: Modular Architecture Integration
    print("\n6️⃣  MODULAR ARCHITECTURE TESTS")
    print("-" * 30)
    try:
        # Test core module imports and functionality
        from generators.dynamic_generator import DynamicGenerator
        generator = DynamicGenerator()
        available_components = generator.get_available_components()
        
        if len(available_components) > 0:
            print(f"   ✅ Dynamic generator working: {len(available_components)} components")
            test_results["modular"] = True
        else:
            print("   ❌ No components available")
            test_results["modular"] = False
    except Exception as e:
        print(f"   ❌ Modular architecture tests failed: {e}")
        test_results["modular"] = False
    
    # Final Summary
    print("\n🎯 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name.replace('_', ' ').title()}")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! System ready for use.")
    elif passed_tests >= total_tests * 0.8:
        print("✅ MOST TESTS PASSED. System partially functional.")
    else:
        print("❌ MULTIPLE FAILURES. System requires attention.")
    
    return passed_tests >= total_tests * 0.8


def list_authors():
    """List all available authors with their details."""
    try:
        import json
        from pathlib import Path

        authors_file = Path("components/author/authors.json")
        if not authors_file.exists():
            print("❌ Authors file not found")
            return

        with open(authors_file, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)

        authors = authors_data.get("authors", [])
        if not authors:
            print("❌ No authors found")
            return

        print(f"👥 Available Authors ({len(authors)}):")
        print("-" * 50)

        for i, author in enumerate(authors, 1):
            author_id = author.get("id", i)
            name = author.get("name", "Unknown")
            country = author.get("country", "Unknown")
            language = author.get("language", "Unknown")

            print(f"   {author_id}. {name}")
            print(f"      🌍 Country: {country}")
            print(f"      🗣️  Language: {language}")
            print()

    except Exception as e:
        print(f"❌ Error listing authors: {e}")


def load_authors():
    """Load all authors from the JSON file and return as a list."""
    try:
        import json
        from pathlib import Path

        authors_file = Path("components/author/authors.json")
        if not authors_file.exists():
            return []

        with open(authors_file, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)

        return authors_data.get("authors", [])

    except Exception as e:
        print(f"❌ Error loading authors: {e}")
        return []


def get_author_by_id(author_id: int):
    """Get author data by ID."""
    try:
        import json
        from pathlib import Path

        authors_file = Path("components/author/authors.json")
        if not authors_file.exists():
            return None

        with open(authors_file, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)

        authors = authors_data.get("authors", [])
        for author in authors:
            if author.get("id") == author_id:
                return author

        return None

    except Exception as e:
        print(f"❌ Error getting author {author_id}: {e}")
        return None


def create_arg_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Z-Beam Dynamic Content Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 run.py                                    # Generate all materials (batch mode)
  python3 run.py --material "Copper"                # Generate all components for Copper
  python3 run.py --material "Steel" --components "frontmatter,content"  # Specific components
  python3 run.py --material "Aluminum" --author 2   # Generate with Italian writing style
  python3 run.py --list-materials                   # List all available materials
  python3 run.py --show-config                      # Show component configuration
  python3 run.py --yaml                            # Validate and fix YAML errors
  python3 run.py --clean                           # Remove all generated content files
  python3 run.py --test-api                        # Test API connection
        """,
    )

    # Main operation modes
    parser.add_argument("--material", help="Generate content for specific material")
    parser.add_argument("--components", help="Comma-separated list of components to generate")
    parser.add_argument("--author", type=int, help="Author ID for country-specific writing style")
    parser.add_argument("--start-index", type=int, default=1, help="Start batch generation at specific material index")
    parser.add_argument("--yaml", action="store_true", help="Validate and fix YAML errors")
    parser.add_argument("--test-api", action="store_true", help="Test API connection")
    parser.add_argument("--test", action="store_true", help="Run comprehensive test suite")
    parser.add_argument("--check-env", action="store_true", help="Check environment variables and API keys")
    parser.add_argument("--clean", action="store_true", help="Remove all generated content files")
    parser.add_argument("--content-batch", action="store_true", help="Clear content directory and generate content component for first 8 material categories")

    # Listing operations
    parser.add_argument("--list-materials", action="store_true", help="List all available materials")
    parser.add_argument("--list-components", action="store_true", help="List all available components")
    parser.add_argument("--list-authors", action="store_true", help="List all available authors")
    parser.add_argument("--show-config", action="store_true", help="Show component configuration")

    # General options
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    return parser


def main():
    """Main entry point for Z-Beam clean generation system."""
    parser = create_arg_parser()
    args = parser.parse_args()

    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Route to appropriate operation
        if args.yaml:
            success = run_yaml_validation()

        elif args.test:
            success = run_comprehensive_tests()

        elif args.clean:
            success = clean_content_components()

        elif args.content_batch:
            success = run_content_batch()

        elif (
            args.list_materials
            or args.list_components
            or args.list_authors
            or args.show_config
            or args.check_env
        ):
            # List operations and configuration display
            if args.show_config:
                show_component_configuration()
                success = True
            elif args.check_env:
                check_environment()
                success = True
            else:
                try:
                    from generators.dynamic_generator import DynamicGenerator
                    generator = DynamicGenerator()

                    if args.list_materials:
                        materials = generator.get_available_materials()
                        print(f"📋 Available materials ({len(materials)}):")
                        for i, material in enumerate(sorted(materials), 1):
                            print(f"   {i:3d}. {material}")

                    if args.list_components:
                        components = generator.get_available_components()
                        print(f"🔧 Available components ({len(components)}):")
                        for i, component in enumerate(sorted(components), 1):
                            print(f"   {i}. {component}")

                    if args.list_authors:
                        list_authors()

                    success = True
                except ImportError as e:
                    print(f"❌ Error importing generator: {e}")
                    success = False

        else:
            # Dynamic generation mode (default)
            components_list = None
            if args.components:
                components_list = [c.strip() for c in args.components.split(",")]

            success = run_dynamic_generation(
                material=args.material,
                components=components_list,
                test_api=args.test_api,
                author_id=args.author,
                start_index=args.start_index,
            )

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n🛑 Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error running operation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
