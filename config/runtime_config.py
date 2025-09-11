#!/usr/bin/env python3
"""
DEPRECATED: Z-Beam Runtime Configuration

⚠️  DEPRECATION NOTICE ⚠️
========================
This file is DEPRECATED and will be removed in a future version.

All user-controlled configurations have been moved back to run.py for easier access.
Please edit configurations directly in run.py (lines ~110-320) instead of this file.

Migration Guide:
1. Open run.py
2. Look for the "USER-CONTROLLED CONFIGURATION" section (lines ~110-320)
3. Edit API_PROVIDERS, COMPONENT_CONFIG, AI_DETECTION_CONFIG, and OPTIMIZER_CONFIG there
4. This file will be automatically removed in the next cleanup

For backward compatibility, this file will import configurations from run.py.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "config/runtime_config.py is deprecated. "
    "Please edit configurations directly in run.py instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import configurations from run.py for backward compatibility
try:
    from run import (
        API_PROVIDERS,
        COMPONENT_CONFIG,
        AI_DETECTION_CONFIG,
        OPTIMIZER_CONFIG,
        get_optimizer_config,
        get_ai_detection_config,
        get_workflow_config,
        get_optimization_config,
        get_text_optimization_config,
        get_persona_config,
        get_dynamic_config_for_component,
        create_dynamic_ai_detection_config,
        FailFastGenerator,
    )
except ImportError as e:
    # Fallback if run.py cannot be imported
    API_PROVIDERS = {}
    COMPONENT_CONFIG = {}
    AI_DETECTION_CONFIG = {}
    OPTIMIZER_CONFIG = {}

    def get_optimizer_config(service_name=None):
        return OPTIMIZER_CONFIG.get(service_name, {}) if service_name else OPTIMIZER_CONFIG

    def get_ai_detection_config():
        return get_optimizer_config("ai_detection_service")

    def get_workflow_config():
        return get_optimizer_config("iterative_workflow_service")

    def get_optimization_config():
        return get_optimizer_config("optimization")

    def get_text_optimization_config():
        return get_optimizer_config("text_optimization")

    def get_persona_config(country=None):
        personas = get_optimizer_config("personas")
        return personas.get(country.lower(), {}) if country else personas

    def get_dynamic_config_for_component(component_type, material_data=None):
        base_config = COMPONENT_CONFIG.get(component_type, {})
        if material_data:
            material_name = material_data.get("name", "").lower()
            if "steel" in material_name or "iron" in material_name:
                base_config["temperature"] = 0.6
            elif "plastic" in material_name or "polymer" in material_name:
                base_config["temperature"] = 0.8
            elif "ceramic" in material_name:
                base_config["temperature"] = 0.5
        return base_config

    def create_dynamic_ai_detection_config(content_type="technical", author_country="usa", content_length=1000):
        base_config = AI_DETECTION_CONFIG.copy()
        if content_type == "technical":
            base_config["target_score"] = 75.0
        elif content_type == "creative":
            base_config["target_score"] = 65.0
        else:
            base_config["target_score"] = 70.0

        if author_country.lower() == "usa":
            base_config["language_patterns"] = "american_english"
        elif author_country.lower() == "uk":
            base_config["language_patterns"] = "british_english"
        else:
            base_config["language_patterns"] = "international_english"

        if content_length < 500:
            base_config["min_text_length"] = 100
        elif content_length > 2000:
            base_config["min_text_length"] = 500
        else:
            base_config["min_text_length"] = 200
        return base_config

    class FailFastGenerator:
        def __init__(self):
            self.call_count = 0

        def generate(self, *args, **kwargs):
            self.call_count += 1
            raise Exception(f"FailFastGenerator called (attempt {self.call_count}) - fail-fast test")
