#!/usr/bin/env python3
"""
Base Schema - Updated to remove tag rules
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSchema(ABC):
    """Base class for all schemas - no tag rules required"""
    
    def __init__(self, schema_type: str):
        self.schema_type = schema_type
    
    @abstractmethod
    def enhance_metadata(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Add schema-specific metadata fields"""
        pass
    
    @abstractmethod
    def get_filename_template(self) -> str:
        """Get filename template for this schema type"""
        pass
    
    @abstractmethod
    def get_output_rules(self) -> Dict[str, Any]:
        """Get output rules for this schema type"""
        pass
    
    @abstractmethod
    def get_article_template(self) -> str:
        """Get article template for this schema type"""
        pass
    
    # NOTE: Removed get_tag_rules() - tags are now fully dynamic
    # NOTE: Removed get_jsonld_rules() - JSON-LD is now fully dynamic