"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODEED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class JsonLdGenerator(BaseComponent):
    """Generator for JSON-LD structured data with enhanced Schema.org properties."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize the JSON-LD generator."""
        super().__init__(context, schema, ai_provider)
        logger.info(f"JsonLdGenerator initialized for subject: {self.subject}")
        
    def generate(self) -> str:
        """Generate JSON-LD schema dynamically based on frontmatter."""
        try:
            # Get frontmatter data
            frontmatter_data = self.get_frontmatter_data()
            if not frontmatter_data:
                from utils.error_handler import ErrorHandler
                return ErrorHandler.handle_component_error(
                    "JsonLdGenerator", 
                    "No frontmatter data available", 
                    strict_mode=False
                )
            
            # Create JSON-LD
            jsonld = self._create_jsonld_from_frontmatter(frontmatter_data)
            
            # Format as JSON with proper indentation
            jsonld_str = json.dumps(jsonld, indent=2)
            
            # Return as script tag for embedding in HTML
            return f"```json\n{jsonld_str}\n```"
                
        except Exception as e:
            from utils.error_handler import ErrorHandler
            return ErrorHandler.handle_component_error("JsonLdGenerator", e, strict_mode=False)
    
    def _create_jsonld_from_frontmatter(self, frontmatter_data):
        """Create JSON-LD from frontmatter data."""
        # Determine schema type based on article type
        schema_type = self._determine_schema_org_type(frontmatter_data)
        
        # Create base JSON-LD
        jsonld = {
            "@context": "https://schema.org",
            "@type": schema_type
        }
        
        # Add basic properties
        self._add_basic_properties(jsonld, frontmatter_data)
        
        # Add author information
        self._add_author(jsonld, frontmatter_data)
        
        # Add technical specifications
        self._add_technical_specs(jsonld, frontmatter_data)
        
        # Add applications
        self._add_applications(jsonld, frontmatter_data)
        
        # Add regional information
        self._add_regional_info(jsonld, frontmatter_data)
        
        # Add safety information
        self._add_safety_info(jsonld, frontmatter_data)
        
        # Add keywords and tags
        self._add_keywords_and_tags(jsonld, frontmatter_data)
        
        # Remove the awards functionality entirely
        # self._add_awards(jsonld, frontmatter_data)
        
        return jsonld
    
    def _determine_schema_org_type(self, frontmatter_data):
        """Determine the Schema.org type based on frontmatter data."""
        article_type = frontmatter_data.get("article_type", self.article_type)
        schema_type = frontmatter_data.get("schemaType", "")
        
        if not schema_type:
            # Map article types to Schema.org types
            type_mapping = {
                "material": "Product",
                "application": "TechnicalArticle",
                "region": "Place",
                "thesaurus": "DefinedTermSet"
            }
            schema_type = type_mapping.get(article_type, "TechnicalArticle")
        
        return schema_type
    
    def _add_basic_properties(self, jsonld, frontmatter_data):
        """Add basic properties like name, description, and dates."""
        # Get subject name
        subject_name = frontmatter_data.get("name", self.subject)
        
        # Set name/headline based on schema type
        if jsonld["@type"] in ["Product", "Material"]:
            jsonld["name"] = subject_name
        else:
            jsonld["headline"] = f"{subject_name} Laser Cleaning Guide"
        
        # Add description if available
        description = frontmatter_data.get("description", "")
        if description:
            jsonld["description"] = description
        
        # Add dates if available (or generate them)
        self._add_dates(jsonld, frontmatter_data)
        
        # Add URL from frontmatter or generate one
        url = frontmatter_data.get("website", "")
        if not url:
            # Create a simple slug from subject name
            slug = subject_name.lower().replace(" ", "-")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            url = f"https://www.z-beam.com/{slug}"
        jsonld["url"] = url
        
        # Add main entity reference
        jsonld["mainEntityOfPage"] = {
            "@type": "WebPage",
            "@id": url
        }
    
    def _add_dates(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add date information to JSON-LD structure."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Add date published if available, otherwise use today
        date_published = frontmatter_data.get("datePublished", today)
        jsonld["datePublished"] = date_published
            
        # Add date modified if available, otherwise use today
        date_modified = frontmatter_data.get("dateModified", today)
        jsonld["dateModified"] = date_modified
    
    def _add_author(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add author information to JSON-LD structure."""
        # Add author information if available
        author_data = frontmatter_data.get("author", {})
        if author_data:
            jsonld["author"] = {
                "@type": "Organization",
                "name": author_data.get("name", "Z-Beam")
            }
            
            credentials = author_data.get("credentials")
            if credentials:
                jsonld["author"]["description"] = credentials
        
        # Add publisher information
        jsonld["publisher"] = {
            "@type": "Organization",
            "name": "Z-Beam",
            "logo": {
                "@type": "ImageObject",
                "url": "https://www.z-beam.com/logo.png"
            }
        }
    
    def _add_technical_specs(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add technical specifications to JSON-LD structure."""
        # Get technical specifications
        tech_specs = frontmatter_data.get("technicalSpecifications", {})
        if not tech_specs:
            return
            
        # Create additionalProperty array
        jsonld["additionalProperty"] = []
        
        # Add each technical specification as a PropertyValue
        for name, value in tech_specs.items():
            jsonld["additionalProperty"].append({
                "@type": "PropertyValue",
                "name": name,
                "value": str(value)
            })
    
    def _add_applications(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add applications as applicationCategory to JSON-LD."""
        applications = frontmatter_data.get("applications", [])
        if not applications:
            return
            
        jsonld["applicationCategory"] = []
        
        # Add each application
        for app in applications:
            if isinstance(app, dict) and "name" in app:
                jsonld["applicationCategory"].append(app["name"])
    
    def _add_keywords_and_tags(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add keywords and categories to JSON-LD structure."""
        # Add keywords if available
        keywords = frontmatter_data.get("keywords", [])
        if keywords:
            if isinstance(keywords, list):
                jsonld["keywords"] = ", ".join(keywords)
            else:
                jsonld["keywords"] = keywords
        
        # Add tags if available
        tags = frontmatter_data.get("tags", [])
        if tags:
            jsonld["category"] = tags
    
    def _add_regional_info(self, jsonld, frontmatter_data):
        """Add regional information if available in frontmatter."""
        # Get regional context
        regional_context = frontmatter_data.get("regionalContext")
        
        # Safety check for type
        if not regional_context:
            return
            
        # Handle different regional context formats
        if isinstance(regional_context, dict):
            # Handle dictionary format
            if "address" in regional_context:
                jsonld["address"] = self._create_address_object(regional_context["address"])
                
            if "broaderRegion" in regional_context:
                jsonld["containedInPlace"] = {
                    "@type": "Place",
                    "name": regional_context["broaderRegion"]
                }
        elif isinstance(regional_context, str) and regional_context.strip():
            # Handle string format - just add as description
            if "description" not in jsonld:
                jsonld["description"] = regional_context
            else:
                jsonld["additionalProperty"] = jsonld.get("additionalProperty", [])
                jsonld["additionalProperty"].append({
                    "@type": "PropertyValue",
                    "name": "regionalContext",
                    "value": regional_context
                })
    
    def _add_safety_info(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add safety information to JSON-LD structure."""
        safety_info = frontmatter_data.get("safetyInformation", "")
        if safety_info:
            jsonld["safetyConsiderations"] = safety_info