"""
Field Order Generator

Ensures consistent field ordering across all frontmatter files.
Moved from enrichers to generators system (Dec 29, 2025).

Purpose:
- Apply standard field order (id, name, slug, description, etc.)
- Domain-specific field ordering rules
- Maintains consistency across all exports

Architecture:
- Standalone generator (no enricher dependencies)
- Uses shared validation system for ordering rules
- Runs as last generator in pipeline
"""

import logging
from typing import Any, Dict
from export.generation.base import BaseGenerator

logger = logging.getLogger(__name__)


class FieldOrderGenerator(BaseGenerator):
    """
    Reorder frontmatter fields according to domain-specific rules.
    
    Uses shared validation system to apply consistent field ordering.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with domain configuration.
        
        Args:
            config: Generator config with 'domain' key
        """
        super().__init__(config)
        self.domain = config.get('domain')
        if not self.domain:
            raise KeyError("FieldOrderGenerator requires config key: domain")
        logger.info(f"Initialized FieldOrderGenerator for domain: {self.domain}")
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reorder fields according to domain rules.
        
        Args:
            frontmatter: Frontmatter dict with unordered fields
        
        Returns:
            Frontmatter with fields in standard order (as OrderedDict)
        """
        from shared.validation.field_order import FrontmatterFieldOrderValidator
        
        validator = FrontmatterFieldOrderValidator()
        ordered = validator.reorder_fields(frontmatter, self.domain)
        
        logger.debug(f"Reordered {len(frontmatter)} fields for {self.domain}")
        
        # CRITICAL: Return OrderedDict to preserve field order
        # Do NOT convert to regular dict - ordering will be lost
        return ordered
