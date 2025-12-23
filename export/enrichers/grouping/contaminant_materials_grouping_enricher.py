"""
Contaminant Materials Grouping Enricher - Groups flat materials lists by category.

Purpose:
- Transform flat materials arrays into semantic groups (metals, woods, plastics, etc.)
- Improves frontend UX for browsing 40-100+ materials
- Matches materials domain grouping pattern

Grouping Strategy:
- metals: All materials with category=metal
- woods: All materials with category=wood
- plastics: All materials with category=plastic
- ceramics: All materials with category=ceramic
- composites: All materials with category=composite
- stone: All materials with category=stone

Created: December 19, 2025
Part of: Change 4 - Group Contaminants Relationships
"""

import logging
from typing import Any, Dict, List

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class ContaminantMaterialsGroupingEnricher(BaseEnricher):
    """Group contaminant materials relationships by category."""
    
    # Category → Group mapping
    CATEGORY_GROUPS = {
        'metal': 'metals',
        'wood': 'woods',
        'plastic': 'plastics',
        'ceramic': 'ceramics',
        'composite': 'composites',
        'stone': 'stone'
    }
    
    # Group titles and descriptions
    GROUP_INFO = {
        'metals': {
            'title': 'Metal Substrates',
            'description': 'Ferrous and non-ferrous metals affected by this contamination'
        },
        'woods': {
            'title': 'Wood Products',
            'description': 'Hardwood and softwood materials affected by this contamination'
        },
        'plastics': {
            'title': 'Plastic Materials',
            'description': 'Thermoplastic and composite materials affected by this contamination'
        },
        'ceramics': {
            'title': 'Ceramic Materials',
            'description': 'Ceramic and glass materials affected by this contamination'
        },
        'composites': {
            'title': 'Composite Materials',
            'description': 'Engineered composite materials affected by this contamination'
        },
        'stone': {
            'title': 'Stone Materials',
            'description': 'Natural and processed stone materials affected by this contamination'
        }
    }
    
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Group flat materials list into semantic categories."""
        if 'relationships' not in data:
            return data
        
        relationships = data['relationships']
        
        # Only process if materials is a flat list
        if 'materials' not in relationships:
            return data
        
        materials = relationships['materials']
        
        # If already grouped (dict with 'groups'), skip
        if isinstance(materials, dict) and 'groups' in materials:
            logger.debug(f"Materials already grouped, skipping")
            return data
        
        # If not a list, skip
        if not isinstance(materials, list):
            logger.warning(f"Materials is not a list: {type(materials)}")
            return data
        
        # Group materials by category
        logger.info(f"Grouping {len(materials)} materials into categories...")
        groups = self._group_materials(materials)
        
        if not groups:
            logger.debug("No materials to group")
            return data
        
        logger.info(f"Created {len(groups)} groups: {list(groups.keys())}")
        
        # Create new grouped structure with card presentation wrapper
        relationships['materials'] = {
            'presentation': 'card',
            'items': [{
                'title': 'Affected Materials',
                'description': 'Materials where this contaminant commonly occurs and requires laser cleaning removal',
                'groups': groups
            }]
        }
        
        logger.debug(f"Grouped {len(materials)} materials into {len(groups)} categories")
        
        return data
    
    def _group_materials(self, materials: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Group materials by category."""
        # Initialize groups
        grouped = {}
        
        for material in materials:
            if not isinstance(material, dict):
                continue
            
            # Extract category from URL if not in item
            # URL format: /materials/{category}/{subcategory}/{id}
            category = material.get('category')
            
            if not category and 'url' in material:
                url_parts = material['url'].strip('/').split('/')
                if len(url_parts) >= 2 and url_parts[0] == 'materials':
                    category = url_parts[1]
            
            if not category:
                logger.warning(f"Material missing category: {material.get('id', 'unknown')}")
                continue
            
            # Map category to group name
            group_name = self.CATEGORY_GROUPS.get(category, category)
            
            # Initialize group if needed
            if group_name not in grouped:
                group_info = self.GROUP_INFO.get(group_name, {
                    'title': f'{group_name.title()} Materials',
                    'description': f'Materials in the {group_name} category'
                })
                grouped[group_name] = {
                    'title': group_info['title'],
                    'description': group_info['description'],
                    'items': []
                }
            
            # Add material to group
            grouped[group_name]['items'].append(material)
        
        return grouped
