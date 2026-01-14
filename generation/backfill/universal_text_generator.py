"""
Universal Text Generator - Schema-Based Reusable Generator
Generates ANY text component for ANY domain using unified prompt schema.
Complies with Core Principle 0: Universal Text Processing Pipeline.
"""

from generation.backfill.base import BaseBackfillGenerator
from generation.backfill.registry import BackfillRegistry
from generation.core.evaluated_generator import QualityEvaluatedGenerator
from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UniversalTextGenerator(BaseBackfillGenerator):
    """
    Universal text generator that works for any domain and component type.
    
    Uses QualityEvaluatedGenerator with schema-based prompts (section_display_schema.yaml).
    No embedded prompts, no hardcoded logic - completely reusable.
    
    Supports both single-field and multi-field generation:
    - Single field: config has 'field' and 'component_type'
    - Multi field: config has 'fields' array with {field, component_type} mappings
    """
    
    def __init__(self, config: dict):
        """
        Initialize universal text generator from config dict.
        
        Args:
            config: Configuration dictionary with keys:
                - source_file: Path to data YAML (Materials.yaml, etc.)
                - items_key: Dictionary key for items ('materials', etc.)
                
                Single-field mode:
                - field: Target field to populate
                - component_type: Component type from section_display_schema.yaml
                
                Multi-field mode:
                - fields: Array of {field, component_type} mappings
                
                Optional:
                - dry_run: If True don't save changes
        """
        # Initialize base class with config
        super().__init__(config)
        
        # Determine if single-field or multi-field mode
        if 'component_type' in config and 'field' in config:
            # Single-field mode
            self.mode = 'single'
            self.component_type = config['component_type']
            self.field_mappings = [{'field': config['field'], 'component_type': config['component_type']}]
        elif 'fields' in config:
            # Multi-field mode 
            self.mode = 'multi'
            self.field_mappings = config['fields']
            if not self.field_mappings:
                raise ValueError("Multi-field mode requires non-empty 'fields' configuration")
        else:
            raise ValueError("UniversalTextGenerator requires either ('field' + 'component_type') or 'fields' configuration")
        
        logger.info(f"  📝 {self.mode.title()}-field mode: {len(self.field_mappings)} fields: {[f['field'] for f in self.field_mappings]}")
        
        # Initialize API client using factory (loads config properly)
        from shared.api.client_factory import APIClientFactory
        api_client = APIClientFactory.create_client(provider="grok")
        
        # Initialize SubjectiveEvaluator
        subjective_evaluator = SubjectiveEvaluator(api_client)
        
        # Initialize Winston client (optional - graceful degradation)
        try:
            from postprocessing.detection.winston_client import WinstonClient
            winston_client = WinstonClient()
            logger.info("✅ Winston client initialized")
        except Exception as e:
            winston_client = None
            logger.warning(f"⚠️  Winston not configured: {e}")
        
        # Extract domain from items_key
        # materials → materials, contaminants → contaminants (keep plural)
        domain = config['items_key']
        
        # Initialize QualityEvaluatedGenerator
        self.generator = QualityEvaluatedGenerator(
            api_client=api_client,
            subjective_evaluator=subjective_evaluator,
            winston_client=winston_client,
            domain=domain
        )
    
    def populate(self, item_data: dict) -> dict:
        """
        Generate text content using schema-based prompts.
        Supports both single-field and multi-field generation.
        
        Args:
            item_data: Item data dictionary
            
        Returns:
            Modified item dict with generated content in target field(s)
        """
        # Extract item identifier and display name
        item_id = item_data.get('id', item_data.get('name', 'unknown'))
        display_name = item_data.get('display_name', item_data.get('name', item_id))
        
        logger.info(f"  🎨 Generating {len(self.field_mappings)} field(s) for {display_name}")
        logger.info(f"  📋 Field mappings: {[m['field'] for m in self.field_mappings]}")
        
        for mapping in self.field_mappings:
            field = mapping['field']
            component_type = mapping['component_type']
            
            # MANDATORY: Always overwrite existing text (structural variation requirement)
            # This ensures distinctive properties and structural patterns are applied
            # No skip logic - regeneration updates stale/generic content
            
            try:
                # Use QualityEvaluatedGenerator with schema-based prompts
                # Use item_id (the key) for multi-field, display_name for single-field compatibility
                material_name = item_id if self.mode == 'multi' else display_name
                
                result = self.generator.generate(
                    material_name=material_name,
                    component_type=component_type,
                    author_id=item_data.get('author', {}).get('id', 1)  # Default to author 1
                )
                
                if result.success and result.content:
                    # Update item data with generated content (handle nested paths)
                    self._set_nested_field(item_data, field, result.content)
                    logger.info(f"{prefix}   📝 Set {field} = '{result.content[:50]}...'")
                    
                    # Extract quality score (try different possible locations)
                    quality_score = 0.0
                    if hasattr(result, 'quality_scores') and result.quality_scores:
                        quality_score = result.quality_scores.get('overall_realism', result.quality_score if hasattr(result, 'quality_score') else 0.0)
                    elif hasattr(result, 'quality_score'):
                        quality_score = result.quality_score
                        
                    prefix = f"    " if self.mode == 'multi' else "  "
                    logger.info(f"{prefix}✅ {field}: generated ({len(result.content)} chars, quality: {quality_score:.1f}/10)")
                else:
                    error_msg = getattr(result, 'error_message', getattr(result, 'error', 'Unknown error'))
                    prefix = f"    " if self.mode == 'multi' else "  "
                    logger.error(f"{prefix}❌ {field}: Generation failed - {error_msg}")
                    
            except Exception as e:
                prefix = f"    " if self.mode == 'multi' else "  "
                logger.error(f"{prefix}❌ {field}: Generation error - {e}")
                import traceback
                traceback.print_exc()
        
        return item_data


    def _set_nested_field(self, data: dict, path: str, value: str):
        """Set a field value in nested dict using dot-notation path."""
        parts = path.split('.')
        current = data
        
        # Navigate to the parent of the target field
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the final field
        current[parts[-1]] = value


    def _should_skip(self, item_data: dict) -> bool:
        """
        MANDATORY: Always return False - Never skip generation.
        
        This ensures structural patterns and distinctive properties
        are applied consistently, even if fields already have content.
        
        See: docs/08-development/MANDATORY_OVERWRITE_POLICY.md
        """
        return False


# Register for common component types
# Note: Config files specify component_type via generator args
BackfillRegistry.register('description', UniversalTextGenerator)
BackfillRegistry.register('micro', UniversalTextGenerator)
BackfillRegistry.register('faq', UniversalTextGenerator)
BackfillRegistry.register('section_description', UniversalTextGenerator)
BackfillRegistry.register('prevention', UniversalTextGenerator)
BackfillRegistry.register('materialCharacteristics_description', UniversalTextGenerator)
BackfillRegistry.register('laserMaterialInteraction_description', UniversalTextGenerator)
BackfillRegistry.register('related_materials', UniversalTextGenerator)
BackfillRegistry.register('micro_before_after', UniversalTextGenerator)
BackfillRegistry.register('multi_field_text', UniversalTextGenerator)  # Replaces MultiFieldTextGenerator
