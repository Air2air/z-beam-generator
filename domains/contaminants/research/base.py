"""
Base Contamination Researcher

Abstract base class for all contamination researchers.
Researchers specialize in discovering contamination pattern data through AI research.

Mirrors the architecture of domains.materials.research.base.ContentResearcher

Author: AI Assistant
Date: November 25, 2025
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass


@dataclass
class ContaminationResearchSpec:
    """
    Specification for contamination research request.
    
    Attributes:
        pattern_id: Contamination pattern identifier (rust_oxidation, copper_patina, etc.)
        research_type: Type of research (detailed_description, formation_conditions, etc.)
        material_context: Optional material name for compatibility research
        environment: Optional environment context (industrial, outdoor, etc.)
    """
    pattern_id: str
    research_type: str  # detailed_description, formation_conditions, compatibility, visual_characteristics
    material_context: Optional[str] = None
    environment: Optional[str] = None


@dataclass
class ContaminationResearchResult:
    """
    Result from contamination research.
    
    Attributes:
        pattern_id: Contamination pattern identifier
        data: Researched data (structure varies by research_type)
        confidence: Confidence score (0.0 to 1.0)
        source: Research source (ai_research, database, etc.)
        metadata: Additional research metadata
        error: Error message if research failed
    """
    pattern_id: str
    data: Any
    confidence: float
    source: str = "ai_research"
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def success(self) -> bool:
        """Whether research was successful"""
        return self.error is None and self.data is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML persistence"""
        result = {
            'pattern_id': self.pattern_id,
            'data': self.data,
            'confidence': int(self.confidence * 100),
            'source': self.source
        }
        if self.metadata:
            result['metadata'] = self.metadata
        if self.error:
            result['error'] = self.error
        return result


class ContaminationResearcher(ABC):
    """
    Base class for all contamination researchers.
    
    Researchers specialize in discovering specific types of contamination data
    through AI research and validation against the Contaminants.yaml schema.
    
    Subclasses must implement:
        - research(): Perform AI research for contamination pattern
        - validate_result(): Validate research meets schema requirements
    
    Example:
        class PatternResearcher(ContaminationResearcher):
            def research(self, pattern_id, research_spec, context):
                # Research detailed contamination pattern info
                ...
            
            def validate_result(self, result, research_spec):
                # Validate structure matches Contaminants.yaml schema
                ...
    """
    
    def __init__(self, api_client: Any):
        """
        Initialize researcher with API client.
        
        Args:
            api_client: API client for AI research (must be provided, fail-fast)
        
        Raises:
            ValueError: If api_client is None
        """
        if api_client is None:
            raise ValueError("API client required for contamination research - cannot be None")
        
        self.api_client = api_client
    
    @abstractmethod
    def research(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict] = None
    ) -> ContaminationResearchResult:
        """
        Research contamination pattern data.
        
        Args:
            pattern_id: Pattern identifier (rust_oxidation, copper_patina, etc.)
            research_spec: Research specification with requirements
            context: Additional context (material, environment, etc.)
        
        Returns:
            ContaminationResearchResult with discovered data and confidence
        
        Raises:
            GenerationError: If research fails critically
        """
        pass
    
    @abstractmethod
    def validate_result(
        self,
        result: ContaminationResearchResult,
        research_spec: ContaminationResearchSpec
    ) -> bool:
        """
        Validate research result meets schema requirements.
        
        Args:
            result: Research result data
            research_spec: Research specification with validation rules
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def _build_prompt(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict] = None
    ) -> str:
        """
        Build AI research prompt.
        
        Args:
            pattern_id: Pattern identifier
            research_spec: Research specification
            context: Additional context
        
        Returns:
            Formatted prompt string
        
        Note:
            Subclasses should override with specific prompt templates.
        """
        return f"Research {research_spec.research_type} for contamination pattern {pattern_id}"
    
    def _parse_response(
        self,
        response: str,
        expected_type: str
    ) -> Any:
        """
        Parse AI response based on expected data type.
        
        Args:
            response: Raw AI response
            expected_type: Expected type ("string", "list", "dict", "number")
        
        Returns:
            Parsed data in correct type
        
        Note:
            Subclasses should override with type-specific parsing logic.
        """
        return response
    
    def _calculate_confidence(
        self,
        data: Any,
        research_spec: ContaminationResearchSpec
    ) -> float:
        """
        Calculate confidence score for research result.
        
        Args:
            data: Research result data
            research_spec: Research specification
        
        Returns:
            Confidence score 0.0 to 1.0
        
        Note:
            Subclasses should override with domain-specific confidence scoring.
        """
        return 0.8
    
    def _load_existing_pattern(self, pattern_id: str) -> Optional[Dict]:
        """
        Load existing pattern data from Contaminants.yaml.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Pattern data dict or None if not found
        """
        try:
            from domains.contaminants.library import ContaminationLibrary
            library = ContaminationLibrary()
            pattern = library.get_pattern(pattern_id)
            return pattern.to_dict() if pattern else None
        except Exception:
            return None
