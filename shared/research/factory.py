"""
Research Factory

Creates appropriate researcher for field type.
Supports extensibility - new researchers can be registered dynamically.

Author: AI Assistant
Date: October 29, 2025
"""

from typing import Any, Dict, Type

from shared.research.base import ContentResearcher
from shared.schemas.base import FieldType


class ResearcherFactory:
    """
    Factory for creating content researchers based on field type.
    
    Maps FieldType → Researcher class
    
    Extensibility:
        - Register new researchers: ResearcherFactory.register(field_type, researcher_class)
        - Override existing: Re-register with same field_type
    
    Example:
        factory = ResearcherFactory()
        researcher = factory.create_researcher(FieldType.PROPERTY, api_client)
        result = researcher.research("Steel", field_spec, context)
    """
    
    # Default researcher mappings (empty - domains register their own)
    _researchers: Dict[FieldType, Type[ContentResearcher]] = {}
    
    @classmethod
    def create_researcher(
        cls,
        field_type: FieldType,
        api_client: Any
    ) -> ContentResearcher:
        """
        Create researcher for specific field type.
        
        Args:
            field_type: Type of field to research (FieldType enum)
            api_client: API client for AI research
        
        Returns:
            Researcher instance
        
        Raises:
            ValueError: If no researcher registered for field_type
        """
        researcher_class = cls._researchers.get(field_type)
        
        if not researcher_class:
            raise ValueError(
                f"No researcher registered for field type: {field_type}. "
                f"Available types: {list(cls._researchers.keys())}"
            )
        
        return researcher_class(api_client)
    
    @classmethod
    def register_researcher(
        cls,
        field_type: FieldType,
        researcher_class: Type[ContentResearcher]
    ):
        """
        Register new researcher type (extensibility).
        
        Args:
            field_type: Field type to handle
            researcher_class: Researcher class to instantiate
        
        Example:
            class CustomResearcher(ContentResearcher):
                ...
            
            ResearcherFactory.register_researcher(
                FieldType.CUSTOM,
                CustomResearcher
            )
        """
        cls._researchers[field_type] = researcher_class
    
    @classmethod
    def get_available_types(cls) -> list[FieldType]:
        """Get list of supported field types"""
        return list(cls._researchers.keys())
