"""
Compound Description Generator - Schema-Based
Populates description field for compounds using schema prompts.
Uses UniversalTextGenerator for reusability.
"""

from generation.backfill.universal_text_generator import UniversalTextGenerator
from generation.backfill.registry import BackfillRegistry


class CompoundDescriptionGenerator(UniversalTextGenerator):
    """Generate compound descriptions using schema-based prompts."""
    
    def __init__(self, config: dict):
        """Initialize with component_type='description' for compounds."""
        super().__init__(
            source_file=config.get('source_file', 'data/compounds/Compounds.yaml'),
            items_key=config.get('items_key', 'compounds'),
            target_field=config.get('field', 'description'),
            component_type='description',
            dry_run=config.get('dry_run', False)
        )


# Register generator
BackfillRegistry.register('compound_description', CompoundDescriptionGenerator)
