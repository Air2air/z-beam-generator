"""
Breadcrumb Enricher - Generate breadcrumb navigation arrays

Generates proper breadcrumb navigation as array of objects with label/href.
Creates hierarchical navigation: Home → Domain → Category → Subcategory → Item

Format:
  breadcrumb:
    - label: Home
      href: /
    - label: Materials
      href: /materials
    - label: Metal
      href: /materials/metal
    - label: Aluminum
      href: /materials/metal/aluminum

Per Schema 5.0.0 and FRONTMATTER_FORMATTING_GUIDE.md.
"""

from typing import Dict, Any, List
import logging

from export.utils.url_formatter import format_domain_url

logger = logging.getLogger(__name__)


class BreadcrumbEnricher:
    """
    Generate breadcrumb navigation arrays.
    
    Creates hierarchical navigation paths with proper array structure
    (not text strings).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize breadcrumb enricher.
        
        Args:
            config: Config with keys:
                - domain: Domain name (materials, contaminants, compounds, settings)
                - category_field: Field name for category (default: 'category')
                - subcategory_field: Field name for subcategory (default: 'subcategory')
                - name_field: Field name for item name (default: 'name')
        """
        self.domain = config.get('domain', 'materials')
        self.category_field = config.get('category_field', 'category')
        self.subcategory_field = config.get('subcategory_field', 'subcategory')
        self.name_field = config.get('name_field', 'name')
        
        logger.info(f"Initialized BreadcrumbEnricher for domain: {self.domain}")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate breadcrumb navigation array.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with breadcrumb array added
        """
        breadcrumb = self._generate_breadcrumb(frontmatter)
        frontmatter['breadcrumb'] = breadcrumb
        
        logger.debug(f"Generated breadcrumb with {len(breadcrumb)} levels")
        
        return frontmatter
    
    def _generate_breadcrumb(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate breadcrumb navigation hierarchy.
        
        Args:
            data: Item data dict
        
        Returns:
            List of breadcrumb dicts with label and href
        """
        breadcrumb = [{"label": "Home", "href": "/"}]
        
        # Add domain level
        domain_label = self.domain.capitalize()
        breadcrumb.append({"label": domain_label, "href": f"/{self.domain}"})
        
        # Get category and subcategory
        category = data.get(self.category_field, '')
        subcategory = data.get(self.subcategory_field, '')
        
        # Add category level
        if category:
            category_label = category.replace('-', ' ').replace('_', ' ').title()
            breadcrumb.append({
                "label": category_label,
                "href": f"/{self.domain}/{category.lower()}"
            })
        
        # Add subcategory level (if present)
        if subcategory:
            subcategory_label = subcategory.replace('-', ' ').replace('_', ' ').title()
            breadcrumb.append({
                "label": subcategory_label,
                "href": f"/{self.domain}/{category.lower()}/{subcategory.lower()}"
            })
        
        # Add current item
        name = data.get(self.name_field, '')
        item_id = data.get('id', '')
        
        if name and item_id:
            # Build final href using centralized formatter
            final_href = format_domain_url(
                domain=self.domain,
                item_id=item_id,
                category=category if category else None,
                subcategory=subcategory if subcategory else None,
                slugify_item_id=False  # IDs should already be slugified
            )
            
            breadcrumb.append({
                "label": name,
                "href": final_href
            })
        
        return breadcrumb
