"""
Contaminant Description Backfill Generator

Generates comprehensive descriptions for contaminants from existing data.

Permanently populates 'description' field in Contaminants.yaml by:
1. Extracting composition, category, valid_materials
2. Generating natural language description
3. Writing back to source YAML

Usage:
    python3 run.py --backfill --domain contaminants --generator description
"""

from typing import Dict, Any
from generation.backfill.base import BaseBackfillGenerator


class ContaminantDescriptionBackfillGenerator(BaseBackfillGenerator):
    """
    Generate and permanently save contaminant descriptions.
    
    Creates descriptions from:
    - Name and composition
    - Category and subcategory
    - Valid materials count
    - Context notes (if available)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize description backfill generator.
        
        Args:
            config: Generator config
        """
        super().__init__(config)
        # Field is 'description' for this generator
        self.field = 'description'
    
    def populate(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate description from contamination pattern data.
        
        Args:
            item_data: Contaminant data from Contaminants.yaml
        
        Returns:
            Item data with description field populated
        """
        # Generate description
        description = self._generate_description(item_data)
        
        # Add to item data
        item_data['description'] = description
        
        return item_data
    
    def _generate_description(self, item_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive description from contaminant data.
        
        Args:
            item_data: Contaminant data
        
        Returns:
            Generated description string
        """
        parts = []
        
        # Part 1: Name and composition
        name = item_data.get('name', 'Contamination')
        composition = item_data.get('composition', [])
        
        if composition:
            if isinstance(composition, list):
                comp_str = ', '.join(composition)
            else:
                comp_str = str(composition)
            parts.append(f"{name} ({comp_str}) is a contamination pattern commonly encountered in industrial laser cleaning applications.")
        else:
            parts.append(f"{name} is a contamination pattern commonly encountered in industrial laser cleaning applications.")
        
        # Part 2: Category and characteristics
        category = item_data.get('category', '')
        subcategory = item_data.get('subcategory', '')
        
        if category:
            if subcategory:
                parts.append(f"This {category}-based contamination, specifically classified as {subcategory}, forms distinct surface deposits that affect material integrity and appearance.")
            else:
                parts.append(f"This {category}-based contamination forms distinct surface deposits that affect material integrity and appearance.")
        
        # Part 3: Material compatibility and context
        valid_materials = item_data.get('valid_materials', [])
        context_notes = item_data.get('context_notes', '')
        
        if valid_materials:
            count = len(valid_materials)
            if count > 50:
                parts.append(f"This contamination is compatible with a wide range of materials ({count} different types), making it one of the most common surface contaminants in industrial settings.")
            elif count > 20:
                parts.append(f"Effective laser cleaning parameters have been developed for {count} different material types, demonstrating versatile removal characteristics.")
            else:
                parts.append(f"Specialized laser cleaning protocols are available for {count} compatible material types.")
        
        if context_notes:
            parts.append(context_notes)
        
        # Part 4: Laser cleaning applicability
        parts.append(f"Laser ablation offers precise, non-contact removal while preserving substrate integrity.")
        
        return ' '.join(parts)


# Register the generator
from generation.backfill.registry import BackfillRegistry
BackfillRegistry.register('description', ContaminantDescriptionBackfillGenerator)
