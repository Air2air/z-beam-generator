"""
JSON-LD generator for material articles.
"""

import logging
from typing import Dict, Any, List
from components.jsonld.types.base_type_generator import BaseTypeGenerator

logger = logging.getLogger(__name__)

class MaterialJsonldGenerator(BaseTypeGenerator):
    """Generator for material-specific JSON-LD."""
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for material articles based on the material schema.
        
        Args:
            frontmatter: Article frontmatter data (override instance frontmatter if provided)
            
        Returns:
            JSON-LD structure for material articles
        """
        # Use provided frontmatter or instance frontmatter
        frontmatter = frontmatter or self.frontmatter
        
        # Get basic data
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        slug = self._get_slug(frontmatter)
        description = self._get_frontmatter_value(frontmatter, "description", 
                                                 f"Technical specifications and laser cleaning properties of {name}.")
        today = self._get_current_date()
        
        # Get keywords
        keywords = self._format_keywords(self._get_frontmatter_value(frontmatter, "keywords", []))
        
        # Extract physical properties
        properties = self._get_frontmatter_value(frontmatter, "properties", {})
        
        # Extract technical specifications
        tech_specs = self._get_frontmatter_value(frontmatter, "technicalSpecifications", {})
        
        # Extract compatibility information
        compatibility = self._get_frontmatter_value(frontmatter, "compatibility", [])
        compatible_materials = [item.get("material") for item in compatibility 
                               if isinstance(item, dict) and item.get("material")]
        
        # Build the JSON-LD structure for material article
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "description": description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self._build_url(slug, "material")
            },
            "manufacturer": {
                "@type": "Organization",
                "name": "Z-Beam"
            },
            "category": "Laser Cleaning Materials",
            "keywords": keywords,
            "datePublished": today,
            "dateModified": today,
            "image": self._build_image_url(slug, "material")
        }
        
        # Add material properties as additionalProperty
        additional_properties = self._build_additional_properties(properties, tech_specs, compatibility)
        
        # Add the properties to the JSON-LD if we have any
        if additional_properties:
            jsonld["additionalProperty"] = additional_properties
            
        return jsonld
        
    def _build_additional_properties(self, 
                                    properties: Dict[str, Any], 
                                    tech_specs: Dict[str, Any],
                                    compatibility: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build a list of additionalProperty objects from material data.
        
        Args:
            properties: Physical properties
            tech_specs: Technical specifications
            compatibility: Compatibility information
            
        Returns:
            List of additionalProperty objects
        """
        result = []
        
        # Add physical properties
        for key, value in properties.items():
            if isinstance(value, str):
                result.append({
                    "@type": "PropertyValue",
                    "name": self._format_property_name(key),
                    "value": value
                })
                
        # Add technical specifications
        for key, value in tech_specs.items():
            if isinstance(value, str):
                result.append({
                    "@type": "PropertyValue",
                    "name": self._format_property_name(key),
                    "value": value
                })
                
        # Add compatible materials
        compatible_materials = [item.get("material") for item in compatibility 
                              if isinstance(item, dict) and item.get("material")]
        if compatible_materials:
            result.append({
                "@type": "PropertyValue",
                "name": "Compatible Materials",
                "value": ", ".join(compatible_materials)
            })
            
        # Add composition information if available
        composition_info = self._get_composition_info(self._get_frontmatter_value(self.frontmatter, "composition", []))
        if composition_info:
            result.append({
                "@type": "PropertyValue",
                "name": "Material Composition",
                "value": composition_info
            })
            
        return result
    
    def _format_property_name(self, key: str) -> str:
        """Convert camelCase property name to Title Case.
        
        Args:
            key: Property name in camelCase
            
        Returns:
            Property name in Title Case
        """
        # Insert space before capital letters
        result = ""
        for char in key:
            if char.isupper():
                result += " " + char
            else:
                result += char
                
        # Capitalize first letter and return
        return result.strip().capitalize()
        
    def _get_composition_info(self, composition: List[Dict[str, Any]]) -> str:
        """Format composition data as a readable string.
        
        Args:
            composition: List of composition items
            
        Returns:
            Formatted composition description
        """
        if not composition or not isinstance(composition, list):
            return ""
            
        parts = []
        for item in composition:
            if not isinstance(item, dict):
                continue
                
            component = item.get("component", "")
            percentage = item.get("percentage", "")
            
            if component and percentage:
                parts.append(f"{component} ({percentage})")
            elif component:
                parts.append(component)
                
        if parts:
            return ", ".join(parts)
        return ""