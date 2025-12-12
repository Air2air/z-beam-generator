"""
MetadataModule - Generate frontmatter metadata fields

Handles: name, title, description, category, subcategory

Architecture:
- Pure extraction from Materials.yaml
- Abbreviation template support (FRPU, GFRP, etc.)
- Fail-fast validation
"""

import logging
from typing import Dict, Optional


class MetadataModule:
    """Generate metadata fields for frontmatter"""
    
    # Abbreviation templates for special materials
    ABBREVIATION_TEMPLATES = {
        'FRPU': {
            'name': 'FRPU',
            'title': 'FRPU (Fiber-Reinforced Polyurethane) Laser Cleaning',
            'subcategory': 'Fiber-Reinforced Composites',
            'description_suffix': ' composite materials'
        },
        'GFRP': {
            'name': 'GFRP',
            'title': 'GFRP (Glass Fiber Reinforced Polymer) Laser Cleaning',
            'subcategory': 'Glass Fiber Composites',
            'description_suffix': ' composite'
        },
        'CFRP': {
            'name': 'CFRP',
            'title': 'CFRP (Carbon Fiber Reinforced Polymer) Laser Cleaning',
            'subcategory': 'Carbon Fiber Composites',
            'description_suffix': ' composite'
        },
        'MDF': {
            'name': 'MDF',
            'title': 'MDF (Medium Density Fiberboard) Laser Cleaning',
            'subcategory': 'Engineered Wood Products',
            'description_suffix': ' engineered wood'
        },
        'PVC': {
            'name': 'PVC',
            'title': 'PVC (Polyvinyl Chloride) Laser Cleaning',
            'subcategory': 'Engineering Thermoplastics',
            'description_suffix': ' plastic'
        },
        'PTFE': {
            'name': 'PTFE',
            'title': 'PTFE (Polytetrafluoroethylene) Laser Cleaning',
            'subcategory': 'High-Performance Polymers',
            'description_suffix': ' fluoropolymer'
        },
        'MMCs': {
            'name': 'MMCs',
            'title': 'MMCs (Metal Matrix Composites) Laser Cleaning',
            'subcategory': 'Metal Matrix Composites',
            'description_suffix': ' composite materials'
        },
        'CMCs': {
            'name': 'CMCs',
            'title': 'CMCs (Ceramic Matrix Composites) Laser Cleaning',
            'subcategory': 'Ceramic Matrix Composites',
            'description_suffix': ' composite materials'
        },
    }
    
    def __init__(self):
        """Initialize metadata module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_name: str, material_data: Dict) -> Dict:
        """
        Generate metadata fields for frontmatter
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            Dictionary with metadata fields:
            - name: Material name (may be abbreviation)
            - title: Full title with "Laser Cleaning"
            - description: Material description
            - category: Material category (capitalized)
            - subcategory: Material subcategory
            
        Raises:
            ValueError: If required fields missing
        """
        self.logger.info(f"Generating metadata for {material_name}")
        
        # Validate required fields
        self._validate_material_data(material_name, material_data)
        
        # Apply abbreviation template if applicable
        template = self._get_abbreviation_template(material_name)
        
        # Extract category and subcategory
        category = material_data.get('category', '').lower()
        if not category:
            raise ValueError(f"Category missing for {material_name}")
        
        # Capitalize category for display
        category_display = category.title()
        
        # Get subcategory (use template if available, otherwise from data)
        subcategory = template.get('subcategory') if template else material_data.get('subcategory', '')
        if not subcategory:
            raise ValueError(f"Subcategory missing for {material_name}")
        
        # Build metadata
        metadata = {
            'name': template.get('name', material_name) if template else material_name,
            'title': self._generate_title(material_name, template),
            'description': self._generate_description(material_name, material_data, template),
            'category': category_display,
            'subcategory': subcategory,
        }
        
        self.logger.info(f"✅ Generated metadata for {material_name}")
        return metadata
    
    def _validate_material_data(self, material_name: str, material_data: Dict):
        """Validate required fields exist in material data"""
        required_fields = ['category']
        
        missing = [f for f in required_fields if f not in material_data or not material_data[f]]
        if missing:
            raise ValueError(f"Missing required fields for {material_name}: {missing}")
    
    def _get_abbreviation_template(self, material_name: str) -> Optional[Dict]:
        """Get abbreviation template if material uses one"""
        return self.ABBREVIATION_TEMPLATES.get(material_name)
    
    def _generate_title(self, material_name: str, template: Optional[Dict]) -> str:
        """
        Generate title field
        
        Format: "{Name} Laser Cleaning" or from template
        """
        if template:
            return template['title']
        
        return f"{material_name} Laser Cleaning"
    
    def _generate_description(
        self, 
        material_name: str, 
        material_data: Dict,
        template: Optional[Dict]
    ) -> str:
        """
        Generate description field
        
        Priority:
        1. Use description from Materials.yaml if present
        2. Generate from template with suffix
        
        This ensures we use existing high-quality descriptions
        and only fall back to template for new materials.
        """
        # Use existing description if available
        if 'description' in material_data and material_data['description']:
            return material_data['description']
        
        # Generate from template
        display_name = template.get('name', material_name) if template else material_name
        suffix = template.get('description_suffix', '') if template else ''
        
        description = f"Laser cleaning parameters for {display_name}{suffix}"
        
        self.logger.warning(
            f"⚠️  No description in Materials.yaml for {material_name}, "
            f"using template: {description}"
        )
        
        return description


# Backward compatibility - use base class directly
MetadataGenerator = MetadataModule
