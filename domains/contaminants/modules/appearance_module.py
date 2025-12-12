"""
Appearance Module - Extract appearance by category for contamination frontmatter

Per CONTAMINATION_FRONTMATTER_SPEC.md

Purpose: Show how contamination appears on different material categories
Data source: visual_characteristics.appearance_on_categories from Contaminants.yaml
"""

import logging
from typing import Dict, Optional


class AppearanceModule:
    """Extract appearance by category for contamination frontmatter"""
    
    def __init__(self):
        """Initialize appearance module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[Dict]:
        """
        Extract appearance by category from contaminant data
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with appearance_by_category or None if not present
        """
        self.logger.info("Extracting appearance by category")
        
        visual_chars = contaminant_data.get('visual_characteristics')
        if not visual_chars:
            self.logger.warning("No visual_characteristics in contaminant data")
            return None
        
        appearance_on_cats = visual_chars.get('appearance_on_categories')
        if not appearance_on_cats:
            self.logger.warning("No appearance_on_categories in visual_characteristics")
            return None
        
        self.logger.info(f"✅ Extracted appearance for {len(appearance_on_cats)} categories")
        return appearance_on_cats
