#!/usr/bin/env python3
"""
Command Handlers Package

Organized command handlers extracted from run.py for better modularity.
"""

# Generation commands
from .generation import (
    handle_caption_generation,
    handle_subtitle_generation,
    handle_faq_generation,
)

# Deployment commands
from .deployment import (
    deploy_to_production,
)

# Data validation commands
from .validation_data import (
    run_data_validation,
)

# Sanitization commands
from .sanitization import (
    run_frontmatter_sanitization,
)

# Audit commands
from .audit import (
    handle_material_audit,
)

# Research commands
from .research import (
    handle_data_completeness_report,
    handle_data_gaps,
    handle_research_missing_properties,
)

# Validation commands
from .validation import (
    generate_content_validation_report,
)

__all__ = [
    # Generation
    'handle_caption_generation',
    'handle_subtitle_generation',
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
    # Validation
    'generate_content_validation_report',
]
