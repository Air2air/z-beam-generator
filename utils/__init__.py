"""
Utilities module for Z-Beam Generator

Provides common utility functions organized by     # Validation
    "QualityScoreValidator",
    "FrontmatterDependencyValidator",
    "LayerValidator",
    "validate_placeholder_content",
    "has_placeholder_content",

    # Configuration
    "ConfigLoader",
    "ConfigUtils",
    "EnvironmentChecker",

    # AI and error handling
    "LoudError",re: Core utilities (slug generation, component base, etc.)
- file_ops: File and path operations
- validation: Validation and error handling
- config: Configuration management
- ai: AI and error handling utilities
"""

# Core utilities
from .core.slug_utils import (
    create_filename_slug,
    create_material_slug,
    extract_material_from_filename,
    get_clean_material_mapping,
    normalize_material_name,
    validate_slug,
)
from .core.component_base import (
    load_template,
    create_standard_logger,
    handle_generation_error,
    sanitize_material_name,
    get_component_output_path,
)
from .core.author_manager import (
    load_authors,
    get_author_by_id,
    list_authors,
    validate_author_id,
    get_author_info_for_generation,
    extract_author_info_from_frontmatter_file,
    extract_author_info_from_content,
    get_author_info_for_material,
)
# from .core.laser_parameters import *
# from .core.percentile_calculator import PercentileCalculator
# from .core.property_enhancer import PropertyEnhancer

# File operations
# from .file_ops.file_operations import FileOperations
from .file_ops.path_manager import PathManager
from .import_system import UnifiedImportManager, import_manager

# Validation
from .validation.quality_validator import QualityScoreValidator
from .validation.frontmatter_validator import FrontmatterDependencyValidator
from .validation.layer_validator import LayerValidator
from .validation.placeholder_validator import validate_placeholder_content, has_placeholder_content

# Configuration
# Configuration now centralized in run.py - no separate config utilities needed
from .config_loader import (
    dump_yaml_with_defaults,
    parse_yaml_frontmatter,
    safe_yaml_load,
    load_component_config,
)

# AI and error handling - Use consolidated system
from .ai.loud_errors import (
    critical_error,
    component_failure,
    api_failure,
    validation_failure,
    dependency_failure,
    configuration_failure,
    network_failure,
    LoudError,
)

__all__ = [
    # Core utilities
    "create_material_slug",
    "create_filename_slug",
    "extract_material_from_filename",
    "normalize_material_name",
    "get_clean_material_mapping",
    "validate_slug",
    "load_template",
    "create_standard_logger",
    "handle_generation_error",
    "sanitize_material_name",
    "get_component_output_path",
    "load_authors",
    "get_author_by_id",
    "list_authors",
    "validate_author_id",
    "get_author_info_for_generation",
    "extract_author_info_from_frontmatter_file",
    "extract_author_info_from_content",
    "get_author_info_for_material",

    # File operations
    "PathManager", 
    "UnifiedImportManager",
    "import_manager",
    "ImportErrorHandler",
    "ImportManager",

    # Validation
    "QualityScoreValidator",
    "FrontmatterDependencyValidator",
    "LayerValidator",
    "validate_placeholder_content",
    "has_placeholder_content",

    # Configuration
    "ConfigLoader",
    "load_yaml_file",
    "load_component_config", 
    "load_ai_detection_config",
    "check_environment",
    "format_environment_report",
    
    # Standardized YAML utilities
    "dump_yaml_with_defaults",
    "parse_yaml_frontmatter", 
    "safe_yaml_load",

    # AI and error handling
    "critical_error",
    "component_failure",
    "api_failure", 
    "validation_failure",
    "dependency_failure",
    "configuration_failure",
    "network_failure",
    "LoudError",
]
