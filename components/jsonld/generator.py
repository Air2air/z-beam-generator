"""
JSON-LD generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import json
import re
from typing import Dict, Any, Optional
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class JsonldGenerator(BaseComponent):
    """Generator for JSON-LD structured data."""
    
    def generate(self) -> str:
        """Generate JSON-LD content.
        
        Returns:
            str: The generated JSON-LD
        """
        try:
            # Check if we should use type-specific generator
            type_generator = self._get_type_generator()
            if type_generator:
                return self._generate_with_type_generator(type_generator)
            
            # No type generator, use standard approach
            # 1. Prepare data for prompt
            data = self._prepare_data()
            
            # 2. Format prompt
            prompt = self._format_prompt(data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logger.error(f"Error generating JSON-LD: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _get_type_generator(self):
        """Get a type-specific generator based on article type.
        
        Returns:
            object: Type generator instance or None
        """
        # Temporarily disable type-specific generators to use improved main generator
        # TODO: Update type-specific generators to use rich schema data
        return None
        
        try:
            # Import type-specific generator
            if self.article_type == "material":
                from components.jsonld.types.material_generator import MaterialJsonldGenerator
                return MaterialJsonldGenerator(self.subject, self.get_frontmatter_data())
            elif self.article_type == "application":
                from components.jsonld.types.application_generator import ApplicationJsonldGenerator
                return ApplicationJsonldGenerator(self.subject, self.get_frontmatter_data())
            elif self.article_type == "region":
                from components.jsonld.types.region_generator import RegionJsonldGenerator
                return RegionJsonldGenerator(self.subject, self.get_frontmatter_data())
            elif self.article_type == "thesaurus":
                from components.jsonld.types.thesaurus_generator import ThesaurusJsonldGenerator
                return ThesaurusJsonldGenerator(self.subject, self.get_frontmatter_data())
            else:
                return None
        except ImportError:
            logger.warning(f"No type-specific generator found for {self.article_type}")
            return None
    
    def _generate_with_type_generator(self, generator) -> str:
        """Generate JSON-LD using type-specific generator.
        
        Args:
            generator: Type-specific generator instance
            
        Returns:
            str: The generated JSON-LD
        """
        # Pass frontmatter to generator if it has a method for it
        if hasattr(generator, "set_frontmatter"):
            generator.set_frontmatter(self.get_frontmatter_data())
        
        # Generate JSON-LD
        try:
            if hasattr(generator, "generate"):
                return generator.generate()
            elif hasattr(generator, "generate_jsonld"):
                jsonld = generator.generate_jsonld()
                return self._format_jsonld(jsonld)
            else:
                raise AttributeError("Generator has no generate or generate_jsonld method")
        except Exception as e:
            logger.error(f"Error in type generator: {str(e)}")
            return self._create_error_markdown(f"Error in type generator: {str(e)}")
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for JSON-LD generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get frontmatter data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Include ALL frontmatter data for rich schema generation
            # The prompt template will map specific fields as needed
            data.update({
                "frontmatter_data": frontmatter,  # Complete frontmatter for template
                "title": frontmatter.get("name", frontmatter.get("title", self.subject.capitalize())),
                "description": frontmatter.get("description", f"Information about {self.subject}"),
                "website": frontmatter.get("website", f"https://www.z-beam.com/{self.subject.lower()}"),
                "keywords": frontmatter.get("keywords", []),
                "tags": frontmatter.get("tags", []),
                "countries": frontmatter.get("countries", [])
            })
            
            # Extract author information
            author = frontmatter.get("author", {})
            if isinstance(author, dict):
                data["author"] = author
            elif isinstance(author, str):
                data["author"] = {"name": author}
            
            # Extract date
            data["date"] = frontmatter.get("date", self._get_current_date())
            
            # Include article type-specific fields with ALL available data
            if self.article_type == "material":
                data.update({
                    "properties": frontmatter.get("properties", {}),
                    "applications": frontmatter.get("applications", []),
                    "technicalSpecifications": frontmatter.get("technicalSpecifications", {}),
                    "composition": frontmatter.get("composition", []),
                    "environmentalImpact": frontmatter.get("environmentalImpact", []),
                    "compatibility": frontmatter.get("compatibility", []),
                    "regulatoryStandards": frontmatter.get("regulatoryStandards", []),
                    "outcomes": frontmatter.get("outcomes", [])
                })
            elif self.article_type == "application":
                data.update({
                    "industries": frontmatter.get("industries", []),
                    "features": frontmatter.get("features", []),
                    "applications": frontmatter.get("applications", []),
                    "technicalSpecifications": frontmatter.get("technicalSpecifications", {}),
                    "environmentalImpact": frontmatter.get("environmentalImpact", []),
                    "regulatoryStandards": frontmatter.get("regulatoryStandards", []),
                    "outcomes": frontmatter.get("outcomes", [])
                })
            elif self.article_type == "region":
                data.update({
                    "geoCoordinates": frontmatter.get("geoCoordinates", {}),
                    "economicData": frontmatter.get("economicData", {}),
                    "manufacturingCenters": frontmatter.get("manufacturingCenters", []),
                    "applications": frontmatter.get("applications", []),
                    "technicalSpecifications": frontmatter.get("technicalSpecifications", {}),
                    "composition": frontmatter.get("composition", []),
                    "environmentalImpact": frontmatter.get("environmentalImpact", []),
                    "compatibility": frontmatter.get("compatibility", []),
                    "regulatoryStandards": frontmatter.get("regulatoryStandards", []),
                    "outcomes": frontmatter.get("outcomes", [])
                })
            elif self.article_type == "thesaurus":
                data.update({
                    "alternateNames": frontmatter.get("alternateNames", []),
                    "relatedTerms": frontmatter.get("relatedTerms", []),
                    "applications": frontmatter.get("applications", []),
                    "technicalSpecifications": frontmatter.get("technicalSpecifications", {}),
                    "environmentalImpact": frontmatter.get("environmentalImpact", []),
                    "regulatoryStandards": frontmatter.get("regulatoryStandards", [])
                })
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the JSON-LD content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed JSON-LD
        """
        # Extract JSON-LD from content
        jsonld = self._extract_jsonld(content)
        
        # Format as script tag
        if jsonld:
            return self._format_jsonld(jsonld)
        else:
            # Create fallback JSON-LD
            fallback = self._create_fallback_jsonld()
            return self._format_jsonld(fallback)
    
    def _extract_jsonld(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON-LD from content.
        
        Args:
            content: Content that might contain JSON-LD
            
        Returns:
            Optional[Dict[str, Any]]: Extracted JSON-LD or None
        """
        # Try to extract JSON object using the base class method first
        json_str = self._extract_json_from_code_blocks(content)
        if json_str:
            try:
                return json.loads(json_str)
            except Exception as e:
                logger.debug(f"Failed to parse JSON from code blocks: {str(e)}")
        
        # Try other extraction methods
        try:
            # Look for JSON in script tags
            script_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>\s*(.*?)\s*</script>'
            match = re.search(script_pattern, content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            
            # Look for any script tag
            script_pattern = r'<script[^>]*>\s*(.*?)\s*</script>'
            match = re.search(script_pattern, content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                if json_str.startswith('{') and '"@context"' in json_str:
                    return json.loads(json_str)
            
            # Look for a raw JSON object with @context
            json_obj_pattern = r'(\{\s*"@context"[^}]*(?:\{[^}]*\}[^}]*)*\})'
            match = re.search(json_obj_pattern, content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            
            # Try to find any JSON object that looks like structured data
            json_obj_pattern = r'(\{(?:[^{}]|\{[^{}]*\})*\})'
            matches = re.findall(json_obj_pattern, content, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    # Check if it looks like JSON-LD (has @context or @type)
                    if isinstance(parsed, dict) and ("@context" in parsed or "@type" in parsed):
                        return parsed
                except Exception:
                    continue
            
            # Finally, try to parse the whole content as JSON if it looks like JSON
            content_stripped = content.strip()
            if content_stripped.startswith('{') and content_stripped.endswith('}'):
                return json.loads(content_stripped)
                
        except Exception as e:
            logger.debug(f"Error extracting JSON-LD: {str(e)}")
            
        return None
    
    def _format_jsonld(self, jsonld: Dict[str, Any]) -> str:
        """Format JSON-LD as script tag.
        
        Args:
            jsonld: JSON-LD data
            
        Returns:
            str: Formatted JSON-LD script tag
        """
        # Ensure we have valid JSON-LD
        if not jsonld:
            jsonld = self._create_fallback_jsonld()
        
        # Ensure @context is present
        if "@context" not in jsonld:
            jsonld["@context"] = "https://schema.org"
        
        # Format as JSON with indentation
        try:
            json_str = json.dumps(jsonld, indent=2)
            return f'<script type="application/ld+json">\n{json_str}\n</script>'
        except Exception as e:
            logger.error(f"Error formatting JSON-LD: {str(e)}")
            return f"<!-- Error formatting JSON-LD: {str(e)} -->"
    
    def _create_fallback_jsonld(self) -> Dict[str, Any]:
        """Create fallback JSON-LD when extraction fails.
        
        Returns:
            Dict[str, Any]: Fallback JSON-LD
        """
        # Get frontmatter data
        frontmatter = self.get_frontmatter_data()
        if not frontmatter:
            # Basic fallback if no frontmatter
            return {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": self.subject.capitalize(),
                "description": f"Information about {self.subject}"
            }
        
        # Extract basic fields
        title = frontmatter.get("name", frontmatter.get("title", self.subject.capitalize()))
        description = frontmatter.get("description", f"Information about {self.subject}")
        website = frontmatter.get("website", f"https://www.z-beam.com/{self.subject.lower()}")
        
        # Get author information
        author_info = frontmatter.get("author", {})
        if isinstance(author_info, dict):
            author = {
                "@type": "Person",
                "name": author_info.get("author_name", author_info.get("name", "Z-Beam Technical Writer")),
                "affiliation": {
                    "@type": "Organization",
                    "name": author_info.get("name", "Z-Beam")
                }
            }
        else:
            author = {
                "@type": "Person",
                "name": "Z-Beam Technical Writer",
                "affiliation": {
                    "@type": "Organization",
                    "name": "Z-Beam"
                }
            }
        
        # Create article type-specific JSON-LD using rich frontmatter data
        if self.article_type == "region":
            jsonld = {
                "@context": "https://schema.org",
                "@type": "Place",
                "name": title,
                "description": description,
                "url": website
            }
            
            # Add geographic coordinates if available
            geo_coords = frontmatter.get("geoCoordinates", {})
            if geo_coords:
                jsonld["geo"] = {
                    "@type": "GeoCoordinates",
                    "latitude": geo_coords.get("latitude"),
                    "longitude": geo_coords.get("longitude")
                }
                
                # Add address information
                address_parts = []
                if geo_coords.get("county"):
                    address_parts.append(geo_coords.get("county"))
                if geo_coords.get("state"):
                    address_parts.append(geo_coords.get("state"))
                if geo_coords.get("region"):
                    jsonld["containedInPlace"] = {
                        "@type": "Place",
                        "name": geo_coords.get("region")
                    }
                
                if address_parts:
                    jsonld["address"] = {
                        "@type": "PostalAddress",
                        "addressRegion": geo_coords.get("state", ""),
                        "addressCountry": "US"
                    }
            
            # Add economic data if available
            economic_data = frontmatter.get("economicData", {})
            if economic_data:
                jsonld["additionalProperty"] = []
                if economic_data.get("gdpContribution"):
                    jsonld["additionalProperty"].append({
                        "@type": "PropertyValue",
                        "name": "GDP Contribution",
                        "value": economic_data.get("gdpContribution")
                    })
                if economic_data.get("employmentRate"):
                    jsonld["additionalProperty"].append({
                        "@type": "PropertyValue",
                        "name": "Employment Rate",
                        "value": economic_data.get("employmentRate")
                    })
            
            return jsonld
            
        elif self.article_type == "material":
            jsonld = {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": title,
                "description": description,
                "url": website,
                "category": "Laser Cleaning Material"
            }
            
            # Add technical specifications if available
            tech_specs = frontmatter.get("technicalSpecifications", {})
            if tech_specs:
                jsonld["additionalProperty"] = []
                for key, value in tech_specs.items():
                    jsonld["additionalProperty"].append({
                        "@type": "PropertyValue",
                        "name": key.replace("_", " ").title(),
                        "value": str(value)
                    })
            
            # Add composition if available
            composition = frontmatter.get("composition", [])
            if composition:
                jsonld["material"] = []
                for comp in composition:
                    if isinstance(comp, dict):
                        jsonld["material"].append({
                            "@type": "Product",
                            "name": comp.get("component", ""),
                            "description": comp.get("type", "")
                        })
            
            return jsonld
            
        elif self.article_type == "application":
            jsonld = {
                "@context": "https://schema.org",
                "@type": "TechArticle",
                "headline": title,
                "description": description,
                "url": website,
                "about": {
                    "@type": "Thing",
                    "name": f"Laser Cleaning {self.subject}"
                }
            }
            
            # Add applications if available
            applications = frontmatter.get("applications", [])
            if applications:
                jsonld["about"]["description"] = []
                for app in applications:
                    if isinstance(app, dict):
                        jsonld["about"]["description"].append(
                            f"{app.get('name', '')}: {app.get('description', '')}"
                        )
            
            return jsonld
            
        elif self.article_type == "thesaurus":
            return {
                "@context": "https://schema.org",
                "@type": "DefinedTerm",
                "name": title,
                "description": description,
                "url": website,
                "alternateName": frontmatter.get("alternateNames", []),
                "relatedLink": frontmatter.get("relatedTerms", [])
            }
        else:
            # Generic article
            return {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title,
                "description": description,
                "url": website,
                "datePublished": self._get_current_date(),
                "dateModified": self._get_current_date(),
                "author": author,
                "publisher": {
                    "@type": "Organization",
                    "name": "Z-Beam",
                    "url": "https://www.z-beam.com"
                },
                "about": [
                    {
                        "@type": "Thing",
                        "name": f"Laser Cleaning in {self.subject}",
                        "description": f"Specialized laser cleaning techniques and applications used in the {self.subject} region, addressing local industrial needs and environmental regulations."
                    }
                ]
            }
