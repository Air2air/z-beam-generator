"""
Simple extraction modules for compliance, impact, media, and characteristics

These modules handle straightforward field extraction with minimal logic.
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


class ImpactModule:
    """Extract environmentalImpact and outcomeMetrics for frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> Dict:
        """Extract environmental impact and outcome metrics"""
        self.logger.info("Extracting impact data")
        
        result = {
            'environmentalImpact': material_data.get('environmentalImpact', []),
            'outcomeMetrics': material_data.get('outcomeMetrics', [])
        }
        
        # Validate lists
        if not isinstance(result['environmentalImpact'], list):
            self.logger.warning("environmentalImpact not a list")
            result['environmentalImpact'] = []
        
        if not isinstance(result['outcomeMetrics'], list):
            self.logger.warning("outcomeMetrics not a list")
            result['outcomeMetrics'] = []
        
        self.logger.info(
            f"✅ Extracted {len(result['environmentalImpact'])} impacts, "
            f"{len(result['outcomeMetrics'])} metrics"
        )
        
        return result


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
        else:
            self.logger.warning("No caption found")
            result['caption'] = {}
        
        self.logger.info("✅ Extracted media data")
        return result


class CharacteristicsModule:
    """Extract materialCharacteristics (qualitative properties) for frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> List[str]:
        """
        Extract material characteristics
        
        Data Architecture Rule:
        Qualitative properties MUST be stored in materialCharacteristics,
        NOT in materialProperties (which is for quantitative data only).
        """
        self.logger.info("Extracting material characteristics")
        
        characteristics = material_data.get('materialCharacteristics', [])
        
        if not isinstance(characteristics, list):
            self.logger.warning(f"materialCharacteristics not a list: {type(characteristics)}")
            return []
        
        self.logger.info(f"✅ Extracted {len(characteristics)} characteristics")
        return characteristics


# Backward compatibility aliases - use base classes directly
ComplianceGenerator = ComplianceModule
ImpactGenerator = ImpactModule
MediaGenerator = MediaModule
CharacteristicsGenerator = CharacteristicsModule
