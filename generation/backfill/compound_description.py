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
        required_keys = ['source_file', 'items_key', 'field', 'dry_run']
        missing = [key for key in required_keys if key not in config]
        if missing:
            raise KeyError(f"Missing required config keys: {', '.join(missing)}")

        if not isinstance(config['dry_run'], bool):
            raise TypeError(
                f"Invalid config type for dry_run: expected bool, got {type(config['dry_run']).__name__}"
            )

        generator_config = dict(config)
        generator_config['component_type'] = 'description'

        super().__init__(generator_config)


# Register generator
BackfillRegistry.register('compound_description', CompoundDescriptionGenerator)
