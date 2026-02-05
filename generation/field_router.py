"""
Field Generation Router

Routes field generation to appropriate generator based on field type:
- Text fields → QualityEvaluatedGenerator (full voice processing)
- Data fields → Simple data generators (research + parse + validate)

This eliminates waste: structured data doesn't need Winston AI, voice compliance,
humanness layers, or quality scoring.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FieldRouter:
    """
    Routes fields to appropriate generator.
    
    Architecture:
    - Text fields use QualityEvaluatedGenerator (voice, quality, learning)
    - Data fields use simple generators (research, parse, validate)
    """
    
    # Field type mapping: domain → field → type
    FIELD_TYPES = {
        'materials': {
            # Legacy fields
            'pageDescription': 'text',
            'pageTitle': 'text',
            'micro': 'text', 
            'faq': 'text',
            'power_intensity': 'data',
            'context': 'data',
            # Schema-based relationship fields
            'contaminatedBy': 'text',
            'relatedMaterials': 'text',
            'industryApplications': 'text',
            'commonChallenges': 'text',
            'removalMethods': 'text',
            'preventionStrategies': 'text',
            # Schema-based property sections
            'materialCharacteristics': 'text',
            'laserMaterialInteraction': 'text',
            'physicalProperties': 'text',
            'appearanceVariations': 'text',
            'environmentalImpact': 'text',
        },
        'contaminants': {
            # Legacy fields
            'pageDescription': 'text',
            'pageTitle': 'text',
            'micro': 'text',
            'compounds': 'text',
            'appearance': 'text',
            'context': 'data',
            # Schema-based relationship fields
            'producedByMaterials': 'text',
            'relatedContaminants': 'text',
            'detectionMethods': 'text',
            'removalMethods': 'text',
            'preventionStrategies': 'text',
            # Schema-based safety sections
            'healthEffects': 'text',
            'exposureLimits': 'text',
            'ppeRequirements': 'text',
            'emergencyResponse': 'text',
            'continuousMonitoring': 'text',
        },
        'compounds': {
            # Legacy fields
            'pageDescription': 'text',
            'pageTitle': 'text',
            'health_effects': 'text',
            'exposure_guidelines': 'text',
            'detection_methods': 'text',
            'first_aid': 'text',
            'ppe_requirements': 'text',
            'regulatory_standards': 'text',
            # Schema-based relationship fields
            'producedFromContaminants': 'text',
            'relatedCompounds': 'text',
            # Schema-based safety sections
            'healthEffects': 'text',
            'exposureLimits': 'text',
            'ppeRequirements': 'text',
            'emergencyResponse': 'text',
            'storageRequirements': 'text',
            'regulatoryClassification': 'text',
            'reactivity': 'text',
        },
        'settings': {
            # Legacy fields
            'pageDescription': 'text',
            'pageTitle': 'text',
            'component_summary': 'text',
            'recommendations': 'text',
            'challenges': 'text',
            # Schema-based sections
            'industryApplications': 'text',
            'commonChallenges': 'text',
            'operationalConsiderations': 'text',
        }
    }
    
    @classmethod
    def get_field_type(cls, domain: str, field: str) -> str:
        """
        Get field type (text or data).
        
        Args:
            domain: Domain name
            field: Field name
        
        Returns:
            'text' or 'data'
        
        Raises:
            ValueError: If field not found in mapping
        """
        if domain not in cls.FIELD_TYPES:
            raise ValueError(f"Unknown domain: {domain}")
        
        if field not in cls.FIELD_TYPES[domain]:
            raise ValueError(f"Unknown field '{field}' for domain '{domain}'")
        
        return cls.FIELD_TYPES[domain][field]
    
    @classmethod
    def create_generator(cls, domain: str, field: str, api_client, **kwargs):
        """
        Create appropriate generator for field.
        
        Args:
            domain: Domain name
            field: Field name
            api_client: API client
            **kwargs: Additional args for generator initialization
        
        Returns:
            Generator instance (QualityEvaluatedGenerator or data generator)
        """
        field_type = cls.get_field_type(domain, field)
        
        if field_type == 'text':
            # Text field - use full quality pipeline
            logger.info(f"📝 Text field '{field}' → QualityEvaluatedGenerator")
            return cls._create_text_generator(domain, field, api_client, **kwargs)
        
        elif field_type == 'data':
            # Data field - use simple generator
            logger.info(f"📊 Data field '{field}' → Simple data generator")
            return cls._create_data_generator(domain, field, api_client)
        
        else:
            raise ValueError(f"Unknown field type: {field_type}")
    
    @classmethod
    def _create_text_generator(cls, domain: str, field: str, api_client, **kwargs):
        """Create QualityEvaluatedGenerator for text fields."""
        from generation.core.evaluated_generator import QualityEvaluatedGenerator
        from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
        
        # Initialize evaluator
        evaluator = SubjectiveEvaluator(api_client)
        
        # Create evaluated generator
        generator = QualityEvaluatedGenerator(
            api_client=api_client,
            subjective_evaluator=evaluator,
            domain=domain,
            **kwargs
        )
        
        return generator
    
    @classmethod
    def _create_data_generator(cls, domain: str, field: str, api_client):
        """Create simple data generator for structured fields."""
        from generation.data.context_generator import ContextGenerator
        from generation.data.power_intensity_generator import PowerIntensityGenerator
        
        # Route to specific data generator
        if field == 'power_intensity':
            return PowerIntensityGenerator(api_client, domain)
        elif field == 'context':
            return ContextGenerator(api_client, domain)
        else:
            raise ValueError(f"No data generator for field: {field}")
    
    @classmethod
    def generate_field(
        cls,
        domain: str,
        field: str,
        item_name: str,
        api_client,
        dry_run: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate field value using appropriate generator.
        
        Args:
            domain: Domain name
            field: Field name
            item_name: Item identifier
            api_client: API client
            dry_run: If True, don't save
            **kwargs: Additional args (author_id for text, etc.)
        
        Returns:
            Result dict with 'success', 'value'/'content', 'field_type' keys
        """
        field_type = cls.get_field_type(domain, field)
        generator = cls.create_generator(domain, field, api_client, **kwargs)
        
        if field_type == 'text':
            # Text generation
            result = generator.generate(
                material_name=item_name,
                component_type=field,
                **kwargs
            )
            return {
                'success': result.success,
                'content': result.content if result.success else None,
                'field_type': 'text',
                'error': result.error_message
            }
        
        elif field_type == 'data':
            # Data generation
            result = generator.generate(item_name, dry_run=dry_run)
            return {
                'success': result['success'],
                'value': result.get('value'),
                'field_type': 'data',
                'error': result.get('error'),
                'skipped': result.get('skipped', False)
            }
