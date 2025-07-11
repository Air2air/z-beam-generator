#!/usr/bin/env python3
"""
Base Schema - Abstract base class for all article schemas
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSchema(ABC):
    """Base class for all article schemas"""
    
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
    def get_template_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get template context for this article type"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate data against schema"""
        pass