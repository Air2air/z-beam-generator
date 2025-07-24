"""
Base component package initialization.

This package contains the core base classes and utilities for the component system.
"""

from components.base.component import BaseComponent
from components.base.utils import FrontmatterUtils, MarkdownUtils
from components.base.error_handler import ErrorHandler
from components.base.config_manager import ComponentConfigManager
from components.base.api_client_factory import ApiClientFactory
from components.base.tag_generator import BaseTagGenerator

__all__ = [
    "BaseComponent",
    "BaseTagGenerator",
    "FrontmatterUtils", 
    "MarkdownUtils",
    "ErrorHandler",
    "ComponentConfigManager",
    "ApiClientFactory"
]