"""
Material Content Schema

Defines structure and research requirements for laser cleaning materials.
Extends ContentSchema with material-specific fields and validation.

Includes citation architecture per OPTIMAL_FRONTMATTER_ARCHITECTURE.md

Author: AI Assistant  
Date: October 29, 2025
Updated: November 12, 2025 - Added citation schema
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from shared.schemas.base import (
    ContentSchema,
    FieldResearchSpec,
    ResearchMethod,
    FieldType
)


@dataclass
class MaterialPropertyValue:
    """
    Schema for material property value with comprehensive citations.
    
    Enforces zero-fallback policy: all non-null values MUST have complete citations.
    Null values MUST have needs_research flag.
    
    Example:
        density = MaterialPropertyValue(
            value=2.7,
            unit="g/cm³",
            source="scientific_literature",
            source_type="reference_handbook",
            source_name="CRC Handbook of Chemistry and Physics",
            citation="ISBN 978-1-138-56163-2 (104th Ed., 2023)",
            context="Pure aluminum at 25°C via pycnometry",
            confidence=98,
            researched_date="2025-11-07T12:51:40Z",
            needs_validation=False
        )
    """
    # Primary value (can be None only if needs_research=True)
    value: Optional[float]
    unit: str
    
    # Citation fields (REQUIRED for non-null values)
    source: str  # scientific_literature | materials_database | industry_standard | government_database
    source_type: str  # reference_handbook | journal_article | materials_database | industry_standard
    source_name: str  # Full source name
    citation: str  # Complete citation with ISBN/DOI/URL
    context: str  # Measurement conditions and methodology
    confidence: int  # 0-100 scale
    
    # Research metadata
    researched_date: str  # ISO8601 format
    needs_validation: bool  # True if AI-generated, False if authoritative
    
    # NULL handling (required if value is None)
    needs_research: bool = False
    research_priority: Optional[str] = None  # high | medium | low
    last_research_attempt: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class CategoryRangeValue:
    """
    Schema for category-level property range with citations.
    
    Used in Categories.yaml for category_ranges.
    
    Example:
        density_range = CategoryRangeValue(
            min=2.3,
            max=16.0,
            unit="g/cm³",
            source="materials_database",
            source_type="reference_database",
            source_name="MatWeb Materials Database",
            citation="MatWeb LLC. http://www.matweb.com (2023)",
            range_determination_method="statistical_analysis",
            sample_size=15,
            confidence=85,
            last_updated="2025-10-15T14:19:43Z"
        )
    """
    # Range values (can be None only if needs_research=True)
    min: Optional[float]
    max: Optional[float]
    unit: str
    
    # Citation fields (REQUIRED for non-null ranges)
    source: str
    source_type: str
    source_name: str
    citation: str
    
    # Range methodology
    range_determination_method: str  # statistical_analysis | literature_review | expert_consensus
    sample_size: Optional[int] = None  # Number of materials analyzed
    confidence: int = 85  # 0-100 scale
    
    # Metadata
    last_updated: str  # ISO8601 format
    researched_by: Optional[str] = None
    needs_validation: bool = False
    
    # Optional adjustment tracking
    adjustment_note: Optional[str] = None
    adjustment_date: Optional[str] = None
    adjustment_source: Optional[str] = None
    
    # Material-specific citations (optional)
    material_citations: Optional[Dict[str, Dict]] = None
    
    # NULL handling (required if min/max is None)
    needs_research: bool = False
    research_priority: Optional[str] = None


@dataclass
class MaterialContent(ContentSchema):
    """
    Material-specific content schema.
    
    Defines structure for laser cleaning materials with properties,
    machine settings, applications, and regulatory information.
    
    Example:
        steel = MaterialContent(
            content_type="material",
            name="Steel",
            category="metal",
            title="Steel - Versatile Industrial Metal",
            materialProperties={...},
            machineSettings={...}
        )
    """
    
    # Material-specific fields
    materialProperties: Dict[str, Dict] = field(default_factory=dict)
    machineSettings: Dict[str, Dict] = field(default_factory=dict)
    applications: List[str] = field(default_factory=list)
    industryTags: List[str] = field(default_factory=list)
    regulatoryStandards: List[Dict] = field(default_factory=list)
    materialCharacteristics: List[str] = field(default_factory=list)
    eeat: Optional[Dict] = None
    breadcrumb: Optional[List[Dict]] = None
    
    # Schema.org date fields (from git history)
    datePublished: Optional[str] = None  # ISO8601 - First commit date of Materials.yaml
    dateModified: Optional[str] = None  # ISO8601 - Last modification date per material
    
    # Generated components (populated during generation)
    faq: Optional[Dict] = None
    caption: Optional[Dict] = None
    subtitle: Optional[str] = None
    
    def get_required_fields(self) -> List[str]:
        """
        Required fields for material content.
        
        Returns fields that MUST be present for valid material.
        """
        return [
            'name',
            'category',
            'title',
            'description',
            'materialProperties',
            'machineSettings',
            'applications'
        ]
    
    def get_researchable_fields(self) -> Dict[str, FieldResearchSpec]:
        """
        Fields that can be AI-researched for materials.
        
        Defines how to discover missing material data through research.
        """
        return {
            'materialProperties': FieldResearchSpec(
                field_name='materialProperties',
                field_type=FieldType.PROPERTY,
                data_type='dict',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/material_properties.txt',
                validation_rules={
                    'min_properties': 3,
                    'required_fields': ['value', 'unit']
                },
                priority=1  # Critical
            ),
            'machineSettings': FieldResearchSpec(
                field_name='machineSettings',
                field_type=FieldType.SPECIFICATION,
                data_type='dict',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/machine_settings.txt',
                validation_rules={
                    'min_settings': 3,
                    'required_fields': ['min', 'max', 'unit']
                },
                priority=1  # Critical
            ),
            'applications': FieldResearchSpec(
                field_name='applications',
                field_type=FieldType.RELATIONSHIP,
                data_type='list',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/material_applications.txt',
                validation_rules={
                    'min_items': 3,
                    'max_items': 10
                },
                priority=2  # Important
            ),
            'industryTags': FieldResearchSpec(
                field_name='industryTags',
                field_type=FieldType.ATTRIBUTE,
                data_type='list',
                research_method=ResearchMethod.INFERENCE,
                prompt_template='research/prompts/industry_tags.txt',
                validation_rules={
                    'min_items': 2,
                    'max_items': 8
                },
                priority=2  # Important
            ),
            'regulatoryStandards': FieldResearchSpec(
                field_name='regulatoryStandards',
                field_type=FieldType.STANDARD,
                data_type='list',
                research_method=ResearchMethod.DATABASE_LOOKUP,
                prompt_template='research/prompts/regulatory_standards.txt',
                validation_rules={
                    'min_items': 1,
                    'required_fields': ['name', 'category']
                },
                priority=2  # Important
            ),
            'materialCharacteristics': FieldResearchSpec(
                field_name='materialCharacteristics',
                field_type=FieldType.ATTRIBUTE,
                data_type='list',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/material_characteristics.txt',
                validation_rules={
                    'min_items': 3,
                    'max_items': 8
                },
                priority=2  # Important
            )
        }
    
    def get_component_requirements(self) -> List[str]:
        """
        Required components for material content.
        
        Returns component types that should be generated.
        """
        return ['text', 'faq', 'caption', 'subtitle']
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate material content completeness.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        required = self.get_required_fields()
        for field_name in required:
            value = getattr(self, field_name, None)
            
            if value is None or (isinstance(value, (list, dict, str)) and not value):
                errors.append(f"Missing required field: {field_name}")
        
        # Validate materialProperties structure (category groups per frontmatter_template.yaml)
        if self.materialProperties:
            VALID_CATEGORIES = {'material_characteristics', 'laser_material_interaction'}
            metadata_keys = {'label', 'description', 'percentage'}
            
            for category_name, category_data in self.materialProperties.items():
                # Validate category names
                if category_name not in VALID_CATEGORIES:
                    errors.append(f"Invalid category '{category_name}' in materialProperties. Only {VALID_CATEGORIES} allowed")
                    continue
                
                if not isinstance(category_data, dict):
                    errors.append(f"Invalid materialProperties.{category_name}: must be dict")
                    continue
                
                # Validate properties within category (exclude metadata)
                for prop_name, prop_data in category_data.items():
                    if prop_name in metadata_keys:
                        continue  # Skip metadata keys
                    
                    if not isinstance(prop_data, dict):
                        errors.append(f"Invalid materialProperties.{category_name}.{prop_name}: must be dict")
                    elif 'value' not in prop_data and 'min' not in prop_data:
                        errors.append(f"Invalid materialProperties.{category_name}.{prop_name}: missing value/min")
        
        # Validate machineSettings structure  
        if self.machineSettings:
            for setting_name, setting_data in self.machineSettings.items():
                if not isinstance(setting_data, dict):
                    errors.append(f"Invalid machineSettings.{setting_name}: must be dict")
                elif 'min' not in setting_data or 'max' not in setting_data:
                    errors.append(f"Invalid machineSettings.{setting_name}: missing min/max")
        
        # Validate category
        if self.category not in [
            'metal', 'plastic', 'wood', 'glass', 'ceramic',
            'composite', 'stone', 'masonry', 'semiconductor', 'rare-earth'
        ]:
            errors.append(f"Invalid category: {self.category}")
        
        # Validate author
        if not self.author:
            errors.append("Missing author information")
        elif not all(k in self.author for k in ['id', 'name', 'country']):
            errors.append("Invalid author: missing required fields (id, name, country)")
        
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert material to dictionary for YAML export.
        
        Returns dictionary matching Materials.yaml structure.
        """
        data = {
            'name': self.name,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'materialProperties': self.materialProperties,
            'machineSettings': self.machineSettings,
            'applications': self.applications,
            'author': self.author
        }
        
        # Add optional fields if present
        if self.subcategory:
            data['subcategory'] = self.subcategory
        if self.subtitle:
            data['subtitle'] = self.subtitle
        if self.industryTags:
            data['industryTags'] = self.industryTags
        if self.regulatoryStandards:
            data['regulatoryStandards'] = self.regulatoryStandards
        if self.materialCharacteristics:
            data['materialCharacteristics'] = self.materialCharacteristics
        if self.eeat:
            data['eeat'] = self.eeat
        if self.breadcrumb:
            data['breadcrumb'] = self.breadcrumb
        if self.faq:
            data['faq'] = self.faq
        if self.caption:
            data['caption'] = self.caption
        
        # Add metadata
        if self.generated_date:
            data['generated_date'] = self.generated_date
        if self.last_updated:
            data['last_updated'] = self.last_updated
        if self.version:
            data['version'] = self.version
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaterialContent':
        """
        Create MaterialContent from dictionary.
        
        Used for loading from Materials.yaml.
        """
        return cls(
            content_type='material',
            name=data.get('name', ''),
            category=data.get('category', ''),
            subcategory=data.get('subcategory'),
            title=data.get('title', ''),
            subtitle=data.get('subtitle'),
            description=data.get('description', ''),
            author=data.get('author', {}),
            materialProperties=data.get('materialProperties', {}),
            machineSettings=data.get('machineSettings', {}),
            applications=data.get('applications', []),
            industryTags=data.get('industryTags', []),
            regulatoryStandards=data.get('regulatoryStandards', []),
            materialCharacteristics=data.get('materialCharacteristics', []),
            eeat=data.get('eeat'),
            breadcrumb=data.get('breadcrumb'),
            faq=data.get('faq'),
            caption=data.get('caption'),
            generated_date=data.get('generated_date'),
            last_updated=data.get('last_updated'),
            version=data.get('version')
        )
