"""
Base Content Schema

Abstract base class defining the structure and research requirements for any content type.
All content types (Material, Product, Service, etc.) extend ContentSchema.

Author: AI Assistant
Date: October 29, 2025
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
from enum import Enum


class ResearchMethod(Enum):
    """Research methods for field discovery"""
    WEB_SEARCH = "web_search"
    DATABASE_LOOKUP = "database_lookup"
    CALCULATION = "calculation"
    API_QUERY = "api_query"
    INFERENCE = "inference"


class FieldType(Enum):
    """Field type classifications"""
    PROPERTY = "property"              # Physical/chemical properties (density, melting point)
    SPECIFICATION = "specification"    # Technical specs (dimensions, capacity)
    ATTRIBUTE = "attribute"            # Characteristics (color, texture)
    RELATIONSHIP = "relationship"      # Connections (applications, uses)
    STANDARD = "standard"             # Regulations, certifications
    METADATA = "metadata"             # Descriptive info (title, description)


@dataclass
class FieldResearchSpec:
    """
    Specification for researching a single field.
    
    Defines how to discover data for a specific field through AI research.
    """
    field_name: str
    field_type: FieldType
    data_type: str                    # "string", "number", "list", "dict"
    research_method: ResearchMethod
    prompt_template: str              # Path or template string for AI prompt
    validation_rules: Dict[str, Any]  # {"min_items": 3, "range": [0, 100], etc.}
    priority: int                     # 1=critical, 2=important, 3=optional
    fallback_value: Optional[Any] = None
    
    def is_required(self) -> bool:
        """Check if field is required (priority 1)"""
        return self.priority == 1


@dataclass
class ResearchResult:
    """
    Result from researching a field.
    
    Contains discovered data, confidence score, and metadata.
    """
    field_name: str
    data: Any
    success: bool
    confidence: float                 # 0.0 to 1.0
    source: str                       # "ai_research", "database", "calculation"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentResult:
    """
    Result from generating a content component.
    
    Components include: text, faq, caption, subtitle, etc.
    """
    component_type: str               # "text", "faq", "caption", "subtitle"
    content: str                      # Generated YAML or text
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentResult:
    """
    Final result from complete content pipeline.
    
    Includes all generated components and export information.
    """
    content_name: str
    content_type: str
    frontmatter: Dict[str, Any]
    export_path: Optional[str] = None
    success: bool = True
    components: Dict[str, ComponentResult] = field(default_factory=dict)
    research_results: Dict[str, ResearchResult] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class ContentSchema(ABC):
    """
    Abstract base class for all content types.
    
    Defines structure, research requirements, and validation rules.
    Every content type (Material, Product, Service) extends this.
    
    Design Principles:
    - Schema-driven: Structure defines behavior
    - Self-describing: Schema knows what it needs
    - Researchable: Fields can be AI-discovered
    - Validatable: Built-in completeness checking
    - Extensible: Easy to add new content types
    """
    
    # Core identity fields (required by all content types)
    content_type: str                 # "material", "product", "service", etc.
    name: str                         # Content item name
    category: str                     # Primary category (references Categories.yaml)
    subcategory: Optional[str] = None # Optional subcategory
    
    # Core metadata (required by all content types)
    title: str = ""
    subtitle: Optional[str] = None
    description: str = ""
    
    # Author/attribution
    author: Dict[str, Any] = field(default_factory=dict)
    
    # Extensible custom fields (content-type specific)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    generated_date: Optional[str] = None
    last_updated: Optional[str] = None
    version: Optional[str] = None
    
    # Abstract methods that each content type MUST implement
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """
        Return list of required field names.
        
        These fields MUST be present for content to be valid.
        Example: ['name', 'category', 'materialProperties']
        """
        pass
    
    @abstractmethod
    def get_researchable_fields(self) -> Dict[str, FieldResearchSpec]:
        """
        Return fields that can be AI-researched with specifications.
        
        Maps field_name → FieldResearchSpec
        Example: {
            'materialProperties': FieldResearchSpec(...),
            'applications': FieldResearchSpec(...)
        }
        """
        pass
    
    @abstractmethod
    def get_component_requirements(self) -> List[str]:
        """
        Return required component types for this content.
        
        Example: ['text', 'faq', 'caption', 'subtitle']
        """
        pass
    
    @abstractmethod
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate content completeness and correctness.
        
        Returns:
            (is_valid, error_messages)
        
        Example:
            (True, []) - Valid
            (False, ["Missing required field: name", "Invalid category"]) - Invalid
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert content to dictionary for YAML export.
        
        Returns dictionary suitable for writing to content YAML file.
        """
        pass
    
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentSchema':
        """
        Create content instance from dictionary.
        
        Used for loading from YAML files.
        """
        pass
    
    # Common helper methods (available to all content types)
    
    def get_category_data(self, categories_data: Dict) -> Optional[Dict]:
        """
        Get category data from Categories.yaml.
        
        Args:
            categories_data: Loaded Categories.yaml content
            
        Returns:
            Category data dict or None if not found
        """
        if not categories_data or 'categories' not in categories_data:
            return None
        
        return categories_data['categories'].get(self.category)
    
    def is_complete(self) -> bool:
        """
        Check if all required fields are present.
        
        Returns True if valid, False otherwise.
        """
        is_valid, _ = self.validate()
        return is_valid
    
    def get_missing_fields(self) -> List[str]:
        """
        Get list of missing required fields.
        
        Returns empty list if all required fields present.
        """
        is_valid, errors = self.validate()
        if is_valid:
            return []
        
        # Extract field names from error messages
        missing = []
        for error in errors:
            if "Missing required field:" in error:
                field = error.replace("Missing required field:", "").strip()
                missing.append(field)
        
        return missing
    
    def get_research_priorities(self) -> List[Tuple[str, FieldResearchSpec]]:
        """
        Get researchable fields sorted by priority.
        
        Returns list of (field_name, spec) tuples, highest priority first.
        """
        researchable = self.get_researchable_fields()
        sorted_fields = sorted(
            researchable.items(),
            key=lambda x: x[1].priority
        )
        return sorted_fields
    
    def needs_research(self) -> bool:
        """
        Check if content needs research (has missing researchable fields).
        
        Returns True if any researchable fields are missing/incomplete.
        """
        missing = self.get_missing_fields()
        researchable = self.get_researchable_fields()
        
        return any(field in researchable for field in missing)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(name='{self.name}', category='{self.category}')"
