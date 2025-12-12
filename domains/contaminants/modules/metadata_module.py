"""
MetadataModule - Generate contaminant frontmatter metadata fields

Handles: name, title, slug, description, category

Architecture:
- Pure extraction from Contaminants.yaml
- Simple field mapping
- Fail-fast validation
"""

import logging
from typing import Dict


class MetadataModule:
    """Generate metadata fields for contaminant frontmatter"""
    
    def __init__(self):
        """Initialize metadata module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_id: str, contaminant_data: Dict) -> Dict:
        """
        Generate metadata fields for frontmatter
        
        Args:
            contaminant_id: ID of contaminant (e.g., 'adhesive-residue')
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with metadata fields:
            - name: Display name
            - slug: URL-safe identifier
            - title: Full title with "Laser Cleaning"
            - description: Contaminant description
            - category: contamination or aging
            
        Raises:
            ValueError: If required fields missing
        """
        self.logger.info(f"Generating metadata for {contaminant_id}")
        
        # Extract display name (human-readable, with spaces)
        name = contaminant_data.get('id', contaminant_id)
        # Convert underscore-separated to title case with spaces
        name_display = name.replace('_', ' ').replace('-', ' ').title()
        
        # Create slug (URL-safe, lowercase with hyphens)
        slug = contaminant_id.lower().replace('_', '-')
        
        # Generate title
        title = f"{name_display} Laser Cleaning"
        
        # Extract description
        description = contaminant_data.get('description', '')
        if not description:
            raise ValueError(f"Contaminant {contaminant_id} missing description")
        
        # Extract category
        category = contaminant_data.get('category', 'contamination')
        
        metadata = {
            'name': name_display,
            'slug': slug,
            'title': title,
            'description': description,
            'category': category,
        }
        
        self.logger.info(f"✅ Generated metadata for {name_display}")
        return metadata
    
    def _validate_contaminant_data(self, contaminant_id: str, contaminant_data: Dict):
        """
        Validate required fields exist
        
        Args:
            contaminant_id: Contaminant identifier
            contaminant_data: Data dictionary
            
        Raises:
            ValueError: If required fields missing
        """
        required_fields = ['description', 'category']
        missing = [f for f in required_fields if f not in contaminant_data or not contaminant_data[f]]
        
        if missing:
            raise ValueError(
                f"Contaminant {contaminant_id} missing required fields: {', '.join(missing)}"
            )
