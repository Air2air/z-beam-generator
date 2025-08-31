#!/usr/bin/env python3
"""
Bullets Component Generator

Generates bullet point content with author-specific formatting rules.
"""

import logging
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator

logger = logging.getLogger(__name__)

class BulletsComponentGenerator(APIComponentGenerator):
    """Generator for bullets components with author-specific formatting"""
    
    def __init__(self):
        super().__init__("bullets")
    
    def _create_template_vars(self, material_name: str, material_data: Dict,
                             author_info: Optional[Dict] = None,
                             frontmatter_data: Optional[Dict] = None,
                             schema_fields: Optional[Dict] = None) -> Dict[str, str]:
        """Create template variables with enhanced bullet formatting rules"""
        
        # Get base template variables from parent
        template_vars = super()._create_template_vars(material_name, material_data, author_info, 
                                                     frontmatter_data, schema_fields)
        
        # Add bullets-specific enhancements
        if author_info:
            author_id = author_info.get('id', 0)
            country = author_info.get('country', 'International')
            
            # Enhanced bullet count based on author
            if author_id == 1:  # Taiwan
                template_vars['bullet_count'] = "4"
            elif author_id == 2:  # Italy
                template_vars['bullet_count'] = "5"
            elif author_id == 3:  # Indonesia
                template_vars['bullet_count'] = "6"
            elif author_id == 4:  # USA
                template_vars['bullet_count'] = "3"
            else:
                template_vars['bullet_count'] = "4"
            
            # Country-specific technical context
            if country == "Taiwan":
                template_vars['industry_context'] = "semiconductor and electronics manufacturing"
                template_vars['technical_standards'] = "Taiwan semiconductor industry standards"
            elif country == "Italy":
                template_vars['industry_context'] = "European manufacturing and automotive"
                template_vars['technical_standards'] = "European Union industrial standards"
            elif country == "Indonesia":
                template_vars['industry_context'] = "tropical manufacturing environments"
                template_vars['technical_standards'] = "sustainability and environmental considerations"
            elif country == "USA":
                template_vars['industry_context'] = "high-tech and aerospace applications"
                template_vars['technical_standards'] = "OSHA and FDA regulatory compliance"
            else:
                template_vars['industry_context'] = "international manufacturing"
                template_vars['technical_standards'] = "global industry standards"
        
        # Add material-specific bullet context
        category = material_data.get('category', 'material')
        if category == 'metal':
            template_vars['material_context'] = "metallic surface preparation and oxide removal"
        elif category == 'polymer':
            template_vars['material_context'] = "polymer surface modification and cleaning"
        elif category == 'ceramic':
            template_vars['material_context'] = "ceramic surface treatment and preparation"
        else:
            template_vars['material_context'] = f"{category} material processing applications"
        
        return template_vars

def create_bullets_generator():
    """Factory function to create a bullets generator"""
    return BulletsComponentGenerator()
