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
    """Extract images and micro for frontmatter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _generate_images_for_material(self, material_name: str) -> Dict:
        """
        Generate images section with material-specific URLs and alt text.
        
        This ensures all materials have proper image objects even if
        not present in Materials.yaml source data.
        """
        import re
        
        # Create URL-safe material name (lowercase, hyphens, handle special chars)
        material_slug = material_name.lower()
        material_slug = re.sub(r'[^a-z0-9\s-]', '', material_slug)  # Remove special chars except spaces and hyphens
        material_slug = re.sub(r'\s+', '-', material_slug)  # Replace spaces with hyphens
        material_slug = re.sub(r'-+', '-', material_slug)  # Collapse multiple hyphens
        material_slug = material_slug.strip('-')  # Remove leading/trailing hyphens
        
        # Generate descriptive alt text with proper capitalization
        material_title = material_name.title()
        
        return {
            'hero': {
                'alt': f'{material_title} surface undergoing laser cleaning showing precise contamination removal',
                'url': f'/images/material/{material_slug}-laser-cleaning-hero.jpg'
            },
            'micro': {
                'alt': f'{material_title} microscopic view of laser cleaning showing detailed precise contamination removal',
                'url': f'/images/material/{material_slug}-laser-cleaning-micro.jpg'
            }
        }
    
    def generate(self, material_data: Dict) -> Dict:
        """Extract media data (images, micro)"""
        self.logger.info("Extracting media data")
        
        result = {}
        material_name = material_data.get('name', 'Unknown')
        
        # Extract images - ALWAYS generate if missing or null
        images = material_data.get('images')
        if images and isinstance(images, dict) and 'hero' in images:
            result['images'] = images
            self.logger.info(f"📸 Using existing images from Materials.yaml")
        else:
            # Generate images dynamically if missing or null
            result['images'] = self._generate_images_for_material(material_name)
            self.logger.info(f"📸 Generated images for {material_name} (was missing/null)")
        
        # Extract micro
        if 'micro' in material_data:
            result['micro'] = material_data['micro']
            self.logger.info(f"📸 Caption extracted with keys: {list(material_data['micro'].keys())}")
        else:
            self.logger.warning("⚠️ No micro found in material_data")
            result['micro'] = {}
        
        self.logger.info("✅ Extracted media data")
        return result


# Backward compatibility aliases - use base classes directly
ComplianceGenerator = ComplianceModule
MediaGenerator = MediaModule
