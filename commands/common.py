#!/usr/bin/env python3
"""
Common imports and utilities for command modules.

This module centralizes frequently used imports across command handlers
to reduce duplication and improve maintainability.
"""

# Standard library
import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

# Data loading
from data.materials import (
    load_materials_cached as load_materials,
    clear_materials_cache,
    get_material_by_name
)

# API clients
from api.client_factory import create_api_client
from api.client_cache import get_cached_api_client

# Generators
from generators.dynamic_generator import DynamicGenerator
from generators.component_generators import ComponentGeneratorFactory

# Configuration
from config.settings import (
    GLOBAL_OPERATIONAL_CONFIG,
    API_PROVIDERS,
    COMPONENT_CONFIG,
)

# Utilities
from utils.slugify import generate_safe_filename

# Pipeline integration (with fallbacks)
try:
    from scripts.pipeline_integration import (
        validate_material_pre_generation,
        validate_and_improve_frontmatter,
        validate_batch_generation,
        get_pre_generation_service,
        get_research_service,
        get_quality_service,
    )
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    
    # Fallback implementations
    def validate_material_pre_generation(material_name):
        return {'validation_passed': True, 'issues_detected': []}
    
    def validate_and_improve_frontmatter(material_name, frontmatter):
        return {
            'improvements_made': False,
            'improved_frontmatter': frontmatter,
            'validation_result': {'validation_passed': True, 'issues_detected': []}
        }
    
    def validate_batch_generation(material_names):
        return {'valid': True, 'total_materials': len(material_names)}
    
    def get_pre_generation_service():
        raise ImportError("Pipeline integration not available")
    
    def get_research_service():
        raise ImportError("Pipeline integration not available")
    
    def get_quality_service():
        raise ImportError("Pipeline integration not available")


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
    'get_research_service',
    'get_quality_service',
    'PIPELINE_AVAILABLE',
]
