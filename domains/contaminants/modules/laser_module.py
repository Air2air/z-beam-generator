"""
LaserModule - Extract laser properties for contaminant frontmatter

Handles: laser_properties with all nested parameters

Architecture:
- Direct extraction from Contaminants.yaml
- Preserves complete structure
- Fail-fast if critical data missing
"""

import logging
from typing import Dict, Optional


class LaserModule:
    """Extract laser properties for contaminant frontmatter"""
    
    def __init__(self):
        """Initialize laser module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[Dict]:
        """
        Extract laser properties from contaminant data
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with complete laser_properties structure or None if not present
        """
        self.logger.info("Extracting laser properties")
        
        laser_props = contaminant_data.get('laser_properties')
        
        if not laser_props:
            self.logger.warning("No laser_properties in contaminant data")
            return None
        
        # Extract all sub-sections
        result = {}
        
        # Laser parameters
        if 'laser_parameters' in laser_props:
            result['laser_parameters'] = laser_props['laser_parameters']
            self.logger.info("✅ Extracted laser_parameters")
        
        # Process variables
        if 'process_variables' in laser_props:
            result['process_variables'] = laser_props['process_variables']
            self.logger.info("✅ Extracted process_variables")
        
        # Removal efficiency
        if 'removal_efficiency' in laser_props:
            result['removal_efficiency'] = laser_props['removal_efficiency']
            self.logger.info("✅ Extracted removal_efficiency")
        
        # Surface integrity
        if 'surface_integrity' in laser_props:
            result['surface_integrity'] = laser_props['surface_integrity']
            self.logger.info("✅ Extracted surface_integrity")
        
        # Safety considerations
        if 'safety_considerations' in laser_props:
            result['safety_considerations'] = laser_props['safety_considerations']
            self.logger.info("✅ Extracted safety_considerations")
        
        self.logger.info(f"✅ Extracted {len(result)} laser property sections")
        return result if result else None
