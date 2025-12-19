#!/usr/bin/env python3
"""
Shared Generation Helpers

Domain-agnostic helpers for content generation operations.

Modules:
- api_helper: Reusable API call wrapper
- yaml_helper: Atomic YAML file operations  
- author_helper: Author voice variation helpers
"""

from .api_helper import generate_text, generate_with_retry, get_api_client
from .author_helper import (
    get_author,
    get_author_name_country,
    get_random_author,
    list_author_ids,
)
from .yaml_helper import (
    get_yaml_field,
    load_yaml_file,
    save_yaml_file,
    update_yaml_field,
)

__all__ = [
    # API helpers
    'generate_text',
    'generate_with_retry',
    'get_api_client',
    # YAML helpers
    'load_yaml_file',
    'save_yaml_file',
    'update_yaml_field',
    'get_yaml_field',
    # Author helpers
    'get_random_author',
    'get_author',
    'get_author_name_country',
    'list_author_ids',
]
