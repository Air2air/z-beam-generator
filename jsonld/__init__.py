"""
JSON-LD package - Structured data generation for articles
"""

try:
    from .jsonld_generator import JSONLDGenerator
    from .jsonld_utils import (
        format_jsonld_as_script,
        format_jsonld_as_yaml_block,
        validate_jsonld_structure,
        save_jsonld_file,
        merge_jsonld_contexts
    )
    
    __all__ = [
        'JSONLDGenerator',
        'format_jsonld_as_script',
        'format_jsonld_as_yaml_block',
        'validate_jsonld_structure',
        'save_jsonld_file',
        'merge_jsonld_contexts'
    ]
    
except ImportError as e:
    # Graceful fallback if modules don't exist
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ JSON-LD modules not fully available: {e}")
    
    __all__ = []