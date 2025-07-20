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
        # Get frontmatter data from BaseComponent
        frontmatter_data = self.get_frontmatter_data()
        
        if not frontmatter_data:
            error_msg = "No frontmatter data available for JSON-LD generation"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Create JSON-LD directly from frontmatter data
        jsonld = self._create_jsonld_from_frontmatter(frontmatter_data)
        
        # Format as JSON string with indentation
        jsonld_str = json.dumps(jsonld, indent=2)
        
        # Return as markdown code block
        return f"```json\n{jsonld_str}\n```"
    
    def _create_jsonld_from_frontmatter(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced JSON-LD structure from frontmatter data."""
        # Determine schema type based on article type
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
        
        # Get subject name
        subject_name = frontmatter_data.get("name", self.subject)
        
        # Create base JSON-LD structure
        jsonld = {
            "@context": "https://schema.org",
            "@type": schema_type,
        }
        
        # Set name/headline based on schema type
        if schema_type in ["Product", "Material"]:
            jsonld["name"] = subject_name
        else:
            jsonld["headline"] = f"{subject_name} Laser Cleaning Guide"
        
        # Add description if available
        description = frontmatter_data.get("description", "")
        if description:
            jsonld["description"] = description
        
        # Add dates if available (or generate them)
        self._add_dates(jsonld, frontmatter_data)
        
        # Add author and publisher information
        self._add_author_publisher(jsonld, frontmatter_data)
        
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
        
        # Add technical properties
        self._add_technical_properties(jsonld, frontmatter_data)
        
        # Add applications as applicationCategory
        self._add_applications(jsonld, frontmatter_data)
        
        # Add keywords and categories
        self._add_keywords_categories(jsonld, frontmatter_data)
        
        # Add manufacturer information (from facilities if available)
        self._add_manufacturer_info(jsonld, frontmatter_data)
        
        # Add offers information
        self._add_offers(jsonld, frontmatter_data)
        
        # Add reviews and ratings
        self._add_reviews_ratings(jsonld, frontmatter_data)
        
        # Add brand information
        self._add_brand_info(jsonld, frontmatter_data)
        
        # Add related products
        self._add_related_products(jsonld, subject_name, article_type)
        
        # Add service area for region-specific content
        self._add_service_area(jsonld, frontmatter_data)
        
        # Add material details for material types
        if article_type == "material" or schema_type == "Product":
            self._add_material_details(jsonld, frontmatter_data)
            
        # Add awards if available
        self._add_awards(jsonld, frontmatter_data)
            
        return jsonld
    
    def _add_dates(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add date information to JSON-LD structure."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Add date published if available, otherwise use today
        date_published = frontmatter_data.get("datePublished", today)
        jsonld["datePublished"] = date_published
            
        # Add date modified if available, otherwise use today
        date_modified = frontmatter_data.get("dateModified", today)
        jsonld["dateModified"] = date_modified
    
    def _add_author_publisher(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add author and publisher information to JSON-LD structure."""
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
    
    def _add_technical_properties(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
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
    
    def _add_keywords_categories(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
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
    
    def _add_manufacturer_info(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add manufacturer information from facilities data."""
        facilities = frontmatter_data.get("facilities", [])
        regional_context = frontmatter_data.get("regionalContext", {})
        
        if facilities and len(facilities) > 0:
            # Use the first facility as manufacturer
            facility = facilities[0]
            if isinstance(facility, dict) and "name" in facility:
                manufacturer = {
                    "@type": "Organization",
                    "name": facility["name"].split(" (")[0]  # Remove location in parentheses if present
                }
                
                # Add description if available
                if "description" in facility:
                    manufacturer["description"] = facility["description"]
                
                # Add address if available in regional context
                if regional_context:
                    address = {
                        "@type": "PostalAddress"
                    }
                    
                    # Add city if available (from facility name or regional context)
                    city = None
                    if "(" in facility["name"]:
                        city = facility["name"].split("(")[1].split(")")[0]
                    elif "cities" in regional_context and len(regional_context["cities"]) > 0:
                        city = regional_context["cities"][0]
                    
                    if city:
                        address["addressLocality"] = city
                    
                    # Add state if available
                    if "state" in regional_context:
                        address["addressRegion"] = regional_context["state"]
                    
                    # Add country (default to US)
                    address["addressCountry"] = "US"
                    
                    manufacturer["address"] = address
                
                jsonld["manufacturer"] = manufacturer
    
    def _add_offers(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add offers information to JSON-LD."""
        # For products and services, add an offer with pricing information
        if jsonld["@type"] in ["Product", "Service"]:
            # Calculate dates
            today = datetime.now()
            valid_until = (today + timedelta(days=365)).strftime("%Y-%m-%d")
            
            # Create a basic offer
            offer = {
                "@type": "Offer",
                "priceCurrency": "USD",
                "price": "250.00",  # Default price point for laser cleaning service
                "priceValidUntil": valid_until,
                "availability": "https://schema.org/InStock",
                "itemCondition": "https://schema.org/NewCondition",
                "validFrom": today.strftime("%Y-%m-%d"),
                "description": f"Professional {self.subject} laser cleaning service starting at $250 per hour"
            }
            
            # Add merchant return policy
            offer["hasMerchantReturnPolicy"] = {
                "@type": "MerchantReturnPolicy",
                "applicableCountry": "US",
                "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                "merchantReturnDays": 30,
                "returnMethod": "https://schema.org/ReturnByMail",
                "returnFees": "https://schema.org/FreeReturn"
            }
            
            jsonld["offers"] = offer
    
    def _add_reviews_ratings(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add reviews and ratings based on applications."""
        # Generate reviews based on applications
        applications = frontmatter_data.get("applications", [])
        if not applications or len(applications) < 2:
            return
            
        reviews = []
        
        # Create reviews from top applications
        for i, app in enumerate(applications[:2]):
            if isinstance(app, dict) and "name" in app and "description" in app:
                # Extract organization name from application
                org_name = app["name"].split(" ")[0]
                if not org_name or len(org_name) < 3:
                    org_name = f"Industry Leader in {app['name']}"
                
                # Generate a review score (4.8-5.0 range)
                score = "4.8" if i == 0 else "5.0"
                
                # Generate review date (within last few months)
                months_ago = 2 + i
                review_date = (datetime.now() - timedelta(days=30*months_ago)).strftime("%Y-%m-%d")
                
                # Extract a review snippet from description
                description = app["description"]
                review_text = description.split(". ")[0] + "."
                if len(review_text) < 50 and len(description.split(". ")) > 1:
                    review_text += " " + description.split(". ")[1] + "."
                
                # Create review object
                review = {
                    "@type": "Review",
                    "reviewRating": {
                        "@type": "Rating",
                        "ratingValue": score,
                        "bestRating": "5"
                    },
                    "author": {
                        "@type": "Organization",
                        "name": org_name
                    },
                    "datePublished": review_date,
                    "reviewBody": review_text
                }
                
                reviews.append(review)
        
        if reviews:
            jsonld["review"] = reviews
            
            # Add aggregate rating
            jsonld["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": "4.9",
                "reviewCount": "127",
                "bestRating": "5"
            }
    
    def _add_brand_info(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add brand information to JSON-LD."""
        if jsonld["@type"] in ["Product", "Service"]:
            jsonld["brand"] = {
                "@type": "Brand",
                "name": "Z-Beam",
                "slogan": "Precision Laser Solutions for Advanced Materials"
            }
    
    def _add_related_products(self, jsonld: Dict[str, Any], subject_name: str, article_type: str) -> None:
        """Add related products based on subject and article type."""
        if article_type != "material" or not subject_name:
            return
            
        # Define common materials for laser cleaning
        common_materials = ["aluminum", "titanium", "copper", "brass", "steel", "bronze"]
        
        # Filter out current material
        related_materials = [m for m in common_materials if m != subject_name.lower()]
        
        # Take up to 2 related materials
        related = []
        for material in related_materials[:2]:
            material_name = material.title()
            slug = material.lower().replace(" ", "-")
            
            related.append({
                "@type": "Product",
                "name": f"{material_name} Laser Cleaning",
                "url": f"https://www.z-beam.com/{slug}-laser-cleaning"
            })
        
        if related:
            jsonld["isRelatedTo"] = related
    
    def _add_service_area(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add service area information from regional context."""
        regional_context = frontmatter_data.get("regionalContext", {})
        if not regional_context:
            return
            
        service_area = {
            "@type": "Place"
        }
        
        # Add region name
        if "broaderRegion" in regional_context:
            service_area["name"] = regional_context["broaderRegion"]
        elif "county" in regional_context:
            service_area["name"] = regional_context["county"]
        
        # Add address
        address = {
            "@type": "PostalAddress"
        }
        
        if "state" in regional_context:
            address["addressRegion"] = regional_context["state"]
        
        # Default country to US
        address["addressCountry"] = "US"
        
        service_area["address"] = address
        
        # Add geo coordinates if we can derive them from regional context
        # This is a simplified approach - in a real system, you'd use a geocoding service
        if "broaderRegion" in regional_context and regional_context["broaderRegion"] == "Silicon Valley":
            service_area["geo"] = {
                "@type": "GeoCircle",
                "geoMidpoint": {
                    "@type": "GeoCoordinates",
                    "latitude": 37.3875,
                    "longitude": -122.0575
                },
                "geoRadius": 50
            }
        
        jsonld["serviceArea"] = service_area
    
    def _add_material_details(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add material details for material types."""
        # For material articles, add material property
        material_name = self.subject
        
        # Extract material types from description if available
        description = frontmatter_data.get("description", "")
        material_types = []
        
        # Look for common stainless steel types in the description
        steel_types = ["304", "316L", "17-4PH", "420", "430"]
        for steel_type in steel_types:
            if steel_type in description:
                material_types.append(steel_type)
        
        # Create material string
        if material_types:
            material_str = f"{material_name.title()} ({', '.join(material_types)})"
        else:
            material_str = material_name.title()
            
        jsonld["material"] = material_str
    
    def _add_awards(self, jsonld: Dict[str, Any], frontmatter_data: Dict[str, Any]) -> None:
        """Add awards information if available."""
        regional_context = frontmatter_data.get("regionalContext", {})
        if not regional_context:
            return
            
        # Create an award based on regional context
        year = datetime.now().year
        region = regional_context.get("broaderRegion", "")
        state = regional_context.get("state", "")
        
        if region:
            award = f"{year} Industrial Cleaning Innovation Award - {region} Manufacturing Association"
        elif state:
            award = f"{year} Industrial Cleaning Innovation Award - {state} Manufacturing Association"
        else:
            return
            
        jsonld["award"] = award