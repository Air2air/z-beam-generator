#!/usr/bin/env python3
"""
Command Handlers Package

Organized command handlers extracted from run.py for better modularity.
"""

# Audit commands
from .audit import (
    handle_material_audit,
)

# Deployment commands
from .deployment import (
    deploy_to_production,
)

# Generation commands
from .generation import (
    handle_component_summaries_generation,
    handle_description_generation,
    handle_faq_generation,
    handle_micro_generation,
    handle_settings_description_generation,
)

# Global evaluation
from .global_evaluation import (
    run_global_subjective_evaluation,
)

# Research commands
from .research import (
    handle_data_completeness_report,
    handle_data_gaps,
    handle_fix_analysis,
    handle_research_missing_properties,
)

# Sanitization commands
from .sanitization import (
    run_frontmatter_sanitization,
)

# Validation commands
from .validation import (
    generate_content_validation_report,
)

# Data validation commands
from .validation_data import (
    run_data_validation,
)

__all__ = [
    # Generation
    'handle_micro_generation',
    'handle_description_generation',
    'handle_settings_description_generation',
    'handle_faq_generation',
    # Deployment
    'deploy_to_production',
    # Data Validation
    'run_data_validation',
    # Sanitization
    'run_frontmatter_sanitization',
    # Audit
    'handle_material_audit',
    # Research
    'handle_data_completeness_report',
    'handle_data_gaps',
    'handle_research_missing_properties',
    'handle_fix_analysis',
    # Validation
    'generate_content_validation_report',
    # Global Evaluation
    'run_global_subjective_evaluation',
]
