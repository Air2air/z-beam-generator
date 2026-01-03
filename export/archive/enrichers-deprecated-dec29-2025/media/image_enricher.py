"""
Image path enricher for frontmatter generation.

Adds properly structured images field to frontmatter files per Frontend Spec 5.0.0:
- Nested object structure (not flat strings)
- hero and micro images with url, alt, width, height
- Complies with BACKEND_FRONTMATTER_SPEC.md requirements
"""

from typing import Dict, Any, Optional
from export.enrichers.base import BaseEnricher


class ImageEnricher(BaseEnricher):
    """
    Adds or enriches images field with proper structure for frontend compliance.
    
    Per Frontend Spec 5.0.0, images must be:
    {
        "hero": {
            "url": "/images/{domain}/{id}-hero.jpg",
            "alt": "{name} laser cleaning visualization",
            "width": 1200,
            "height": 630
        },
        "micro": {
            "url": "/images/{domain}/{id}-micro.jpg",
            "alt": "{name} microscopic detail view",
            "width": 800,
            "height": 600
        }
    }
    """
    
    def __init__(self, config: Dict[str, Any] = None, domain: str = None, **kwargs):
        """
        Initialize image enricher.
        
        Args:
            config: Enricher configuration dict (for registry compatibility)
            domain: Domain name (materials, contaminants, compounds, settings)
        """
        # Handle both config dict and direct domain parameter
        if config and not domain:
            domain = config.get('domain')
        
        super().__init__(config or {})
        self.domain = domain
        
        # Default dimensions per domain
        self.default_dimensions = {
            'hero': {'width': 1200, 'height': 630},  # og:image standard
            'micro': {'width': 800, 'height': 600}
        }
    
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add or enrich images field with proper structure and dimensions.
        
        If images field exists but missing dimensions, adds them.
        If images field missing, creates complete structure.
        """
        # Extract item_id from data (standard pattern)
        item_id = data.get('id', data.get('slug', 'unknown'))
        name = data.get('name', item_id)
        
        # If images already exist, just add missing dimensions
        if 'images' in data and isinstance(data['images'], dict):
            self._add_dimensions(data['images'])
        else:
            # Create complete images structure
            data['images'] = self._create_images_structure(item_id, name)
        
        return data
    
    def _add_dimensions(self, images: Dict[str, Any]) -> None:
        """Add width/height to existing images if missing."""
        for image_type in ['hero', 'micro']:
            if image_type in images and isinstance(images[image_type], dict):
                if 'width' not in images[image_type]:
                    images[image_type]['width'] = self.default_dimensions[image_type]['width']
                if 'height' not in images[image_type]:
                    images[image_type]['height'] = self.default_dimensions[image_type]['height']
    
    def _create_images_structure(self, item_id: str, name: str) -> Dict[str, Any]:
        """
        Create complete images structure from scratch.
        
        Generates paths and alt text based on domain and item info.
        """
        # Map domain to image directory name
        domain_paths = {
            'materials': 'material',
            'contaminants': 'contaminant',
            'compounds': 'compound',
            'settings': 'settings'
        }
        
        path_prefix = domain_paths.get(self.domain, self.domain)
        
        return {
            'hero': {
                'url': f'/images/{path_prefix}/{item_id}-hero.jpg',
                'alt': f'{name} laser cleaning visualization showing process effects',
                'width': self.default_dimensions['hero']['width'],
                'height': self.default_dimensions['hero']['height']
            },
            'micro': {
                'url': f'/images/{path_prefix}/{item_id}-micro.jpg',
                'alt': f'{name} microscopic detail view showing surface characteristics',
                'width': self.default_dimensions['micro']['width'],
                'height': self.default_dimensions['micro']['height']
            }
        }
