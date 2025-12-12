"""
Settings Metadata Module - Extract metadata for settings frontmatter

Handles: material name, title, slug

Architecture:
- Simple extraction and formatting
- Material-based naming
"""

import logging
from typing import Dict


class MetadataModule:
    """Generate metadata fields for settings frontmatter"""
    
    def __init__(self):
        """Initialize metadata module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_name: str) -> Dict:
        """
        Generate metadata fields for settings frontmatter
        
        Args:
            material_name: Name of material
            
        Returns:
            Dictionary with metadata fields:
            - name: Material name
            - slug: URL-safe identifier
            - title: Full title
        """
        self.logger.info(f"Generating settings metadata for {material_name}")
        
        # Create slug (URL-safe, lowercase with hyphens)
        slug = material_name.lower().replace(' ', '-')
        
        # Generate title
        title = f"{material_name} Laser Cleaning Settings"
        
        metadata = {
            'name': material_name,
            'slug': slug,
            'title': title,
        }
        
        self.logger.info(f"✅ Generated settings metadata for {material_name}")
        return metadata
