"""
Base Content Researcher

Abstract base class for all content researchers.
Researchers are field-type specialists that know how to discover data.

Author: AI Assistant
Date: October 29, 2025
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from shared.schemas.base import FieldResearchSpec, ResearchResult


class ContentResearcher(ABC):
    """
    Base class for all content researchers.
    
    Researchers know how to discover specific types of fields through AI research.
    Each researcher specializes in one FieldType (property, specification, etc.).
    
    Subclasses must implement:
        - research(): Perform AI research for field
        - validate_result(): Validate research meets requirements
    
    Example:
        class PropertyResearcher(ContentResearcher):
            def research(self, content_name, field_spec, context):
                # Research property values (density, melting point, etc.)
                ...
            
            def validate_result(self, result, field_spec):
                # Validate numeric values, units, ranges
                ...
    """
    
    def __init__(self, api_client: Any):
        """
        Initialize researcher with API client.
        
        Args:
            api_client: API client for AI research
        """
        self.api_client = api_client
    
    @abstractmethod
    def research(
        self,
        content_name: str,
        field_spec: FieldResearchSpec,
        context: Optional[Dict] = None
    ) -> ResearchResult:
        """
        Research a specific field for content item.
        
        Args:
            content_name: Name of content (e.g., "Steel", "TruLaser 3030")
            field_spec: Field specification with research requirements
            context: Additional context (category, content_type, etc.)
        
        Returns:
            ResearchResult with discovered data and confidence score
        """
        pass
    
    @abstractmethod
    def validate_result(
        self,
        result: Any,
        field_spec: FieldResearchSpec
    ) -> bool:
        """
        Validate research result meets requirements.
        
        Args:
            result: Research result data
            field_spec: Field specification with validation rules
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def _build_prompt(
        self,
        content_name: str,
        field_spec: FieldResearchSpec,
        context: Optional[Dict] = None
    ) -> str:
        """
        Build AI prompt from template.
        
        Args:
            content_name: Content name
            field_spec: Field specification
            context: Additional context
        
        Returns:
            Formatted prompt string
        """
        # NOTE: Template system not yet implemented in base class
        # Subclasses override this method with specific prompt templates
        return f"Research {field_spec.field_name} for {content_name}"
    
    def _parse_response(
        self,
        response: str,
        data_type: str
    ) -> Any:
        """
        Parse AI response based on expected data type.
        
        Args:
            response: Raw AI response
            data_type: Expected type ("string", "number", "list", "dict")
        
        Returns:
            Parsed data in correct type
        """
        # NOTE: Parsing logic not implemented in base class
        # Subclasses override this method with type-specific parsing
        return response
    
    def _calculate_confidence(self, data: Any) -> float:
        """
        Calculate confidence score for research result.
        
        Args:
            data: Research result data
        
        Returns:
            Confidence score 0.0 to 1.0
        """
        # NOTE: Confidence scoring not implemented in base class
        # Subclasses override with domain-specific confidence calculations
        return 0.8
