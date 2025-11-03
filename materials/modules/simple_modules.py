"""
Simple extraction modules for compliance and media

These modules handle straightforward field extraction with minimal logic.

REMOVED (Nov 2, 2025):
- ImpactModule: environmentalImpact and outcomeMetrics fields removed from template
- CharacteristicsModule: materialCharacteristics field removed from template
"""

import logging
from typing import Dict, List


class ComplianceModule:
    """Extract regulatoryStandards for frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> List[str]:
        """Extract regulatory standards list"""
        self.logger.info("Extracting regulatory standards")
        
        standards = material_data.get('regulatoryStandards', [])
        
        if not isinstance(standards, list):
            self.logger.warning(f"regulatoryStandards not a list: {type(standards)}")
            return []
        
        self.logger.info(f"✅ Extracted {len(standards)} standards")
        return standards


class MediaModule:
    """Extract images and caption for frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> Dict:
        """Extract media data (images, caption)"""
        self.logger.info("Extracting media data")
        
        result = {}
        
        # Extract images
        if 'images' in material_data:
            result['images'] = material_data['images']
        else:
            self.logger.warning("No images found")
            result['images'] = {}
        
        # Extract caption
        if 'caption' in material_data:
            result['caption'] = material_data['caption']
            self.logger.info(f"📸 Caption extracted with keys: {list(material_data['caption'].keys())}")
        else:
            self.logger.warning("⚠️ No caption found in material_data")
            result['caption'] = {}
        
        self.logger.info("✅ Extracted media data")
        return result


# Backward compatibility aliases - use base classes directly
ComplianceGenerator = ComplianceModule
MediaGenerator = MediaModule
