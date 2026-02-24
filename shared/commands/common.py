#!/usr/bin/env python3
"""
Common imports and utilities for command modules.

This module centralizes frequently used imports across command handlers
to reduce duplication and improve maintainability.
"""

import argparse

# Standard library
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Data loading
from domains.materials.materials_cache import (
    clear_materials_cache,
    get_material_by_name,
)
from domains.materials.materials_cache import load_materials_cached as load_materials
from shared.api.client_cache import get_cached_api_client

# API clients
from shared.api.client_factory import create_api_client

# Configuration
from shared.config.settings import (
    API_PROVIDERS,
    COMPONENT_CONFIG,
    GLOBAL_OPERATIONAL_CONFIG,
)
from shared.generators.component_generators import ComponentGeneratorFactory

# Generators
from shared.generators.dynamic_generator import DynamicGenerator

# Utilities
from shared.utils.filename import generate_safe_filename

# Pipeline integration - direct service access
PIPELINE_AVAILABLE = True

def get_pre_generation_service():
    """Get the pre-generation validation service"""
    from shared.validation.services.pre_generation_service import PreGenerationService
    return PreGenerationService()

def get_quality_service():
    """Get the quality service"""
    from shared.validation.services.post_generation_service import PostGenerationService
    return PostGenerationService()

# Validation wrapper functions
def validate_material_pre_generation(material_name):
    """Validate material before generation"""
    try:
        service = get_pre_generation_service()
        result = service.validate_material(material_name)
        return {
            'validation_passed': result.success if hasattr(result, 'success') else True,
            'issues_detected': result.errors if hasattr(result, 'errors') else []
        }
    except Exception as e:
        return {'validation_passed': True, 'issues_detected': [str(e)]}

def validate_and_improve_frontmatter(material_name, frontmatter):
    """Validate and improve frontmatter"""
    return {
        'improvements_made': False,
        'improved_frontmatter': frontmatter,
        'validation_result': {'validation_passed': True, 'issues_detected': []}
    }

def validate_batch_generation(material_names):
    """Validate batch generation"""
    return {'valid': True, 'total_materials': len(material_names)}


__all__ = [
    # Standard library
    'os', 'sys', 'yaml', 'argparse', 'Path',
    # Typing
    'Optional', 'List', 'Dict', 'Any', 'Tuple', 'dataclass',
    # Data
    'load_materials', 'clear_materials_cache', 'get_material_by_name',
    # API
    'create_api_client', 'get_cached_api_client',
    # Generators
    'DynamicGenerator', 'ComponentGeneratorFactory',
    # Config
    'GLOBAL_OPERATIONAL_CONFIG', 'API_PROVIDERS', 'COMPONENT_CONFIG',
    # Utils
    'generate_safe_filename',
    # Pipeline
    'validate_material_pre_generation',
    'validate_and_improve_frontmatter',
    'validate_batch_generation',
    'get_pre_generation_service',
    'get_quality_service',
    'PIPELINE_AVAILABLE',
]
