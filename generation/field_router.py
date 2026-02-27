"""
Field Generation Router

Routes field generation to appropriate generator based on field type:
- Text fields → QualityEvaluatedGenerator (full voice processing)
- Data fields → Simple data generators (research + parse + validate)

This eliminates waste: structured data doesn't need Winston AI, voice compliance,
humanness layers, quality scoring, or postprocessing.

Structured fields may still be researched/regenerated when explicitly requested.
"""

import importlib
import logging
from typing import Dict, Any, Optional

from generation.config.config_loader import get_config

logger = logging.getLogger(__name__)


class FieldRouter:
    """
    Routes fields to appropriate generator.
    
    Architecture:
    - Text fields use QualityEvaluatedGenerator (voice, quality, learning)
    - Data fields use simple generators (research, parse, validate)
    """
    
    @classmethod
    def _get_field_router_config(cls) -> Dict[str, Any]:
        config = get_config().config
        field_router = config.get('field_router')
        if not isinstance(field_router, dict):
            raise KeyError("Missing required config block: field_router")
        return field_router

    @classmethod
    def _get_domain_field_router(cls, domain: str) -> Dict[str, Any]:
        field_router = cls._get_field_router_config()

        field_types = field_router.get('field_types')
        field_aliases = field_router.get('field_aliases')
        data_generators = field_router.get('data_generators')

        if not isinstance(field_types, dict):
            raise KeyError("Missing required config block: field_router.field_types")
        if not isinstance(field_aliases, dict):
            raise KeyError("Missing required config block: field_router.field_aliases")
        if not isinstance(data_generators, dict):
            raise KeyError("Missing required config block: field_router.data_generators")

        if domain not in field_types:
            raise KeyError(f"Missing field_types for domain '{domain}'")
        if domain not in field_aliases:
            raise KeyError(f"Missing field_aliases for domain '{domain}'")
        if domain not in data_generators:
            raise KeyError(f"Missing data_generators for domain '{domain}'")

        return {
            'text': field_types[domain].get('text'),
            'data': field_types[domain].get('data'),
            'field_aliases': field_aliases[domain],
            'data_generators': data_generators[domain]
        }

    @classmethod
    def normalize_field_name(cls, domain: str, field: str) -> str:
        """Normalize legacy/alias field names to canonical component field names."""
        domain_cfg = cls._get_domain_field_router(domain)
        aliases = domain_cfg.get('field_aliases')
        text_fields = domain_cfg.get('text')
        data_fields = domain_cfg.get('data')
        if not isinstance(aliases, dict):
            raise KeyError(
                f"field_router.{domain}.field_aliases must be a dictionary"
            )
        if not isinstance(text_fields, list) or not isinstance(data_fields, list):
            raise KeyError(
                f"field_router.{domain} must include text and data lists"
            )

        if field in aliases:
            return aliases[field]

        if field in text_fields or field in data_fields:
            return field

        raise ValueError(f"Unknown field '{field}' for domain '{domain}'")
    
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
        domain_cfg = cls._get_domain_field_router(domain)
        text_fields = domain_cfg.get('text')
        data_fields = domain_cfg.get('data')

        if not isinstance(text_fields, list) or not isinstance(data_fields, list):
            raise KeyError(
                f"field_router.{domain} must include text and data lists"
            )

        normalized_field = cls.normalize_field_name(domain, field)

        if normalized_field in text_fields:
            return 'text'
        if normalized_field in data_fields:
            return 'data'

        raise ValueError(f"Unknown field '{field}' for domain '{domain}'")
    
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
        normalized_field = cls.normalize_field_name(domain, field)
        field_type = cls.get_field_type(domain, field)
        
        if field_type == 'text':
            # Text field - use full quality pipeline
            logger.info(f"📝 Text field '{field}' → QualityEvaluatedGenerator")
            return cls._create_text_generator(domain, normalized_field, api_client, **kwargs)
        
        elif field_type == 'data':
            # Data field - use simple generator
            logger.info(f"📊 Data field '{field}' → Simple data generator")
            return cls._create_data_generator(domain, normalized_field, api_client)
        
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
        domain_cfg = cls._get_domain_field_router(domain)
        data_generators = domain_cfg.get('data_generators')
        if not isinstance(data_generators, dict):
            raise KeyError(
                f"field_router.{domain}.data_generators must be a dictionary"
            )

        if field not in data_generators:
            raise ValueError(f"No data generator configured for field: {field}")

        class_path = data_generators[field]
        if not isinstance(class_path, str) or not class_path.strip():
            raise ValueError(
                f"Data generator path for '{field}' must be a non-empty string"
            )

        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        generator_cls = getattr(module, class_name)
        return generator_cls(api_client, domain)
    
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
        normalized_field = cls.normalize_field_name(domain, field)
        field_type = cls.get_field_type(domain, field)
        generator = cls.create_generator(domain, normalized_field, api_client, **kwargs)
        
        if field_type == 'text':
            # Text generation
            result = generator.generate(
                material_name=item_name,
                component_type=normalized_field,
                **kwargs
            )
            return {
                'success': result.success,
                'content': result.content if result.success else None,
                'field_type': 'text',
                'postprocessing_applied': True,
                'error': result.error_message
            }
        
        elif field_type == 'data':
            # Data generation
            force_regenerate = False
            if 'force_regenerate' in kwargs:
                force_regenerate = bool(kwargs['force_regenerate'])
            result = generator.generate(
                item_name,
                dry_run=dry_run,
                force_regenerate=force_regenerate
            )

            required_keys = ['success', 'value', 'error', 'skipped', 'regenerated']
            missing = [key for key in required_keys if key not in result]
            if missing:
                raise KeyError(
                    f"Data generator result missing required keys: {', '.join(missing)}"
                )

            return {
                'success': result['success'],
                'value': result['value'],
                'field_type': 'data',
                'postprocessing_applied': False,
                'force_regenerate': force_regenerate,
                'error': result['error'],
                'skipped': result['skipped'],
                'regenerated': result['regenerated']
            }
