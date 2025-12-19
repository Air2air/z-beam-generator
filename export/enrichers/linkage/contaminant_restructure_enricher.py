"""
Contaminant Frontmatter Restructure Enricher

Transforms contaminant frontmatter from flat structure to grouped relationships structure.
Part of Schema 5.0.0 migration - moves technical data from top-level to relationships.*.

BEFORE (Flat - Grade D):
    id: adhesive-residue-contamination
    name: Adhesive Residue
    # ... metadata ...
    visual_characteristics: {...}  # ← Top-level
    laser_properties: {...}        # ← Top-level
    eeat: {...}                    # ← Top-level
    # ... 7+ more top-level technical sections

AFTER (Grouped - Grade A):
    id: adhesive-residue-contamination
    name: Adhesive Residue
    # ... metadata ...
    relationships:
      visual_characteristics: {...}  # ← In relationships
      laser_properties: {...}        # ← In relationships
      eeat: {...}                   # ← In relationships
      # ... all technical data grouped here

Sections Moved (7):
1. visual_characteristics → relationships.visual_characteristics
2. laser_properties → relationships.laser_properties
3. eeat → relationships.eeat
4. valid_materials → relationships.valid_materials
5. regulatory_standards_detail → relationships.regulatory_standards_detail
6. context_notes → relationships.context_notes (if present)
7. realism_notes → relationships.realism_notes (if present)

Also moves optional fields:
- formation_conditions (for corrosion/oxidation)
- chemical_formula (for chemical contaminants)
- scientific_name (for biological contaminants)
- required_elements (for element-specific contaminants)
- invalid_materials (materials where contaminant doesn't occur)

Usage:
    In export/config/contaminants.yaml:
    
    enrichers:
      - type: contaminant_restructure
        enabled: true
"""

from typing import Dict, Any
import logging

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class ContaminantRestructureEnricher(BaseEnricher):
    """
    Restructure contaminant frontmatter from flat to grouped structure.
    
    Moves technical data sections from top-level to relationships.*
    to create clean, organized frontmatter aligned with Schema 5.0.0.
    """
    
    # Fields that should remain at top-level (metadata + AI content)
    TOP_LEVEL_FIELDS = {
        'id', 'name', 'category', 'subcategory',
        'datePublished', 'dateModified', 
        'content_type', 'schema_version',
        'full_path', 'breadcrumb', 'title',
        'description', 'micro',  # AI-generated content
        'author',  # Author metadata
        'relationships'  # Container for technical data
    }
    
    # Simple fields to move (no transformation needed)
    SIMPLE_MOVES = {
        'visual_characteristics': 'visual_characteristics',
        'laser_properties': 'laser_properties',
        'eeat': 'eeat',
        'valid_materials': 'valid_materials',
        'invalid_materials': 'invalid_materials',
        'regulatory_standards_detail': 'regulatory_standards_detail',
        'context_notes': 'context_notes',
        'realism_notes': 'realism_notes',
        'formation_conditions': 'formation_conditions',
        'chemical_formula': 'chemical_formula',
        'scientific_name': 'scientific_name',
        'required_elements': 'required_elements',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize contaminant restructure enricher."""
        super().__init__(config)
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restructure contaminant frontmatter from flat to grouped structure.
        
        Args:
            frontmatter: Contaminant frontmatter dict
            
        Returns:
            Restructured frontmatter with technical data in relationships
        """
        # Ensure relationships dict exists
        if 'relationships' not in frontmatter:
            frontmatter['relationships'] = {}
        
        relationships = frontmatter['relationships']
        
        # Move simple fields (no transformation)
        self._move_simple_fields(frontmatter, relationships)
        
        logger.debug(f"Restructured contaminant frontmatter: {frontmatter.get('id', 'unknown')}")
        
        return frontmatter
    
    def _move_simple_fields(
        self, 
        frontmatter: Dict[str, Any],
        relationships: Dict[str, Any]
    ) -> None:
        """
        Move simple fields from top-level to relationships.
        
        Args:
            frontmatter: Full frontmatter dict
            relationships: relationships sub-dict to move fields into
        """
        for old_key, new_key in self.SIMPLE_MOVES.items():
            if old_key in frontmatter:
                # Move field to relationships
                relationships[new_key] = frontmatter.pop(old_key)
                logger.debug(f"Moved {old_key} → relationships.{new_key}")
