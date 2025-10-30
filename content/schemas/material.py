"""
Material Content Schema

Defines structure and research requirements for laser cleaning materials.
Extends ContentSchema with material-specific fields and validation.

Author: AI Assistant  
Date: October 29, 2025
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from content.schemas.base import (
    ContentSchema,
    FieldResearchSpec,
    ResearchMethod,
    FieldType
)


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
    environmentalImpact: List[str] = field(default_factory=list)
    outcomeMetrics: List[str] = field(default_factory=list)
    materialCharacteristics: List[str] = field(default_factory=list)
    
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
            'environmentalImpact': FieldResearchSpec(
                field_name='environmentalImpact',
                field_type=FieldType.ATTRIBUTE,
                data_type='list',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/environmental_impact.txt',
                validation_rules={
                    'min_items': 2,
                    'max_items': 6
                },
                priority=3  # Optional
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
            ),
            'outcomeMetrics': FieldResearchSpec(
                field_name='outcomeMetrics',
                field_type=FieldType.ATTRIBUTE,
                data_type='list',
                research_method=ResearchMethod.INFERENCE,
                prompt_template='research/prompts/outcome_metrics.txt',
                validation_rules={
                    'min_items': 2,
                    'max_items': 6
                },
                priority=3  # Optional
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
        
        # Validate materialProperties structure
        if self.materialProperties:
            for prop_name, prop_data in self.materialProperties.items():
                if not isinstance(prop_data, dict):
                    errors.append(f"Invalid materialProperties.{prop_name}: must be dict")
                elif 'value' not in prop_data and 'min' not in prop_data:
                    errors.append(f"Invalid materialProperties.{prop_name}: missing value/min")
        
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
        if self.environmentalImpact:
            data['environmentalImpact'] = self.environmentalImpact
        if self.outcomeMetrics:
            data['outcomeMetrics'] = self.outcomeMetrics
        if self.materialCharacteristics:
            data['materialCharacteristics'] = self.materialCharacteristics
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
            environmentalImpact=data.get('environmentalImpact', []),
            outcomeMetrics=data.get('outcomeMetrics', []),
            materialCharacteristics=data.get('materialCharacteristics', []),
            faq=data.get('faq'),
            caption=data.get('caption'),
            generated_date=data.get('generated_date'),
            last_updated=data.get('last_updated'),
            version=data.get('version')
        )
