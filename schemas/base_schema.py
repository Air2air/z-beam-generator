#!/usr/bin/env python3
"""
Simplified Base Schema - Minimal abstractions
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseSchema(ABC):
    """Minimal base schema"""
    
    def __init__(self, schema_type: str):
        self.schema_type = schema_type
    
    @abstractmethod
    def get_material_requirement(self, context: Dict[str, Any]) -> str:
        """Get material requirement for this article type"""
        pass
    
    @abstractmethod
    def enhance_metadata(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance metadata with schema context"""
        pass
    
    @abstractmethod
    def generate_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate tags from metadata"""
        pass
    
    @abstractmethod
    def generate_jsonld(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD from metadata"""
        pass
    
    @abstractmethod
    def generate_title(self, metadata: Dict[str, Any]) -> str:
        """Generate title from metadata"""
        pass
    
    @abstractmethod
    def generate_filename(self, context: Dict[str, Any]) -> str:
        """Generate filename from context"""
        pass
    
    @abstractmethod
    def get_article_template(self) -> str:
        """Get article template"""
        pass
    
    # Legacy methods for compatibility
    def get_metadata_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}
    
    def get_tag_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}
    
    def get_jsonld_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}
    
    def get_template_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, list[str]]:
        return True, []