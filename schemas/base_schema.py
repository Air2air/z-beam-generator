#!/usr/bin/env python3
"""
Base Schema - Abstract base class for all article type schemas
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BaseSchema(ABC):
    """Abstract base class for article type schemas"""
    
    def __init__(self, schema_type: str):
        self.schema_type = schema_type
    
    @abstractmethod
    def get_metadata_schema(self) -> Dict[str, Any]:
        """Get metadata schema for this article type"""
        pass
    
    @abstractmethod
    def get_tag_schema(self) -> Dict[str, Any]:
        """Get tag generation schema for this article type"""
        pass
    
    @abstractmethod
    def get_jsonld_schema(self) -> Dict[str, Any]:
        """Get JSON-LD schema for this article type"""
        pass
    
    @abstractmethod
    def get_template_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get template context for this article type"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate data against schema"""
        pass
    
    @abstractmethod
    def get_fallback_tags(self) -> List[str]:
        """Get fallback tags for this article type"""
        pass
    
    def get_template_path(self) -> str:
        """Get template path for this article type"""
        return f"tags/tag_{self.schema_type}.md"
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for this article type"""
        return ["subject", "article_type", "author_id"]