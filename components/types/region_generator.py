"""
Region-specific JSON-LD generator implementation.

Handles the creation of Place schema.org type for region articles.
"""

from typing import Dict, Any
from components.types.base_type_generator import BaseTypeGenerator

class RegionGenerator(BaseTypeGenerator):
    """Generator for Region type JSON-LD (Place schema)."""
    
    def generate(self) -> Dict[str, Any]:
        """Generate a Place JSON-LD structure for region content.
        
        Returns:
            Dict[str, Any]: JSON-LD data for a Place
        """
        frontmatter = self.data.get("frontmatter_data", {})
        region_name = self.data.get("subject", "")
        
        # Create the slug for images
        slug = f"{region_name.lower().replace(' ', '-').replace('_', '-')}-laser-cleaning"
        
        # Base JSON-LD structure
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Place",
            "name": region_name
        }
        
        # Add description if available
        if frontmatter and "description" in frontmatter:
            jsonld["description"] = frontmatter["description"]
            
        # Add address information if available
        if frontmatter and "region" in frontmatter:
            region_data = frontmatter["region"]
            
            # Create address object
            address = {"@type": "PostalAddress"}
            
            if "country" in region_data:
                address["addressCountry"] = region_data["country"]
                jsonld["addressCountry"] = region_data["country"]
                
            if "continent" in region_data:
                jsonld["containedInPlace"] = {
                    "@type": "Place",
                    "name": region_data["continent"]
                }
                
            if address:
                jsonld["address"] = address
                
        # Add image information
        images = self.get_image_data(slug)
        if images:
            jsonld["image"] = images
            
        return jsonld
