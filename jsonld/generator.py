"""JsonLdGenerator updated for new schema structures."""

import logging
import json
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class JsonLdGenerator:
    """Generates JSON-LD structured data with support for new schema formats."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.frontmatter = {}
        
        # NO DEFAULT VALUES - Must come from context
        self.subject = context["subject"]
        self.article_type = context["article_type"]
        
        # Import API client here to avoid circular imports
        from api_client import APIClient
        self.api_client = APIClient(ai_provider)
        
        # Load prompt template
        self.prompt_config = self._load_prompt_template()
        
        logger.info(f"JsonLdGenerator initialized for {self.article_type}: {self.subject}")
    
    def set_frontmatter(self, frontmatter):
        """Set frontmatter data for JSON-LD generation."""
        self.frontmatter = frontmatter or {}
        return self
        
    def generate(self) -> Optional[str]:
        """Generate JSON-LD structured data."""
        try:
            # Determine the best schema type based on content
            schema_type = self._determine_schema_type()
            
            # Build JSON-LD from frontmatter
            jsonld = {
                "@context": "https://schema.org",
                "@type": schema_type
            }
            
            # Add fields based on available frontmatter data
            self._add_basic_properties(jsonld)
            self._add_specific_properties(jsonld)
            
            # Format JSON-LD as a string with code block
            formatted_jsonld = json.dumps(jsonld, indent=2)
            return f"```json\n{formatted_jsonld}\n```"
            
        except Exception as e:
            logger.error(f"JSON-LD generation failed: {str(e)}")
            return self._generate_fallback_jsonld()
            
    def _determine_schema_type(self):
        """Dynamically determine the best schema type based on frontmatter."""
        article_type = self.context.get('article_type', '').lower()
        
        # Map article types to schema types
        type_mapping = {
            'article': 'Article',
            'blog': 'BlogPosting',
            'technical': 'TechnicalArticle',
            'howto': 'HowTo',
            'material': 'Product',
            'application': 'TechnicalArticle',
            'thesaurus': 'DefinedTerm',
            'product': 'Product'
        }
        
        # Check specific frontmatter indicators
        if 'steps' in self.frontmatter or 'instructions' in self.frontmatter:
            return 'HowTo'
        elif 'specifications' in self.frontmatter or 'technicalSpecifications' in self.frontmatter:
            return 'TechnicalArticle'
        
        # Default to mapping or Article
        return type_mapping.get(article_type, 'Article')
        
    def _add_basic_properties(self, jsonld):
        """Add common properties from frontmatter."""
        # Add name/title
        if 'name' in self.frontmatter:
            jsonld['headline'] = self.frontmatter['name']
            
        # Add description
        if 'description' in self.frontmatter:
            jsonld['description'] = self.frontmatter['description']
            
        # Add URL
        if 'website' in self.frontmatter:
            jsonld['url'] = self.frontmatter['website']
        elif 'url' in self.frontmatter:
            jsonld['url'] = self.frontmatter['url']
            
        # Add keywords
        if 'keywords' in self.frontmatter and isinstance(self.frontmatter['keywords'], list):
            # Take first 5-10 keywords to keep it focused
            jsonld['keywords'] = self.frontmatter['keywords'][:10]
        elif 'tags' in self.frontmatter and isinstance(self.frontmatter['tags'], list):
            jsonld['keywords'] = self.frontmatter['tags']
            
        # Add author
        if 'author' in self.frontmatter:
            author_data = self.frontmatter['author']
            if isinstance(author_data, dict):
                jsonld['author'] = {
                    "@type": "Person",
                    "name": author_data.get('name', ''),
                }
                # Add credentials if available
                if 'credentials' in author_data:
                    jsonld['author']['description'] = author_data['credentials']
                    
        # Add publisher from context or frontmatter
        jsonld['publisher'] = {
            "@type": "Organization",
            "name": "Z-Beam Technologies"
        }
        
        # Add publication date
        jsonld['datePublished'] = datetime.now().strftime('%Y-%m-%d')
        
    def _add_specific_properties(self, jsonld):
        """Add schema-type-specific properties based on frontmatter."""
        schema_type = jsonld.get('@type')
        
        if schema_type == 'Product':
            self._add_product_properties(jsonld)
        elif schema_type == 'TechnicalArticle':
            self._add_technical_article_properties(jsonld)
        elif schema_type == 'HowTo':
            self._add_howto_properties(jsonld)
        elif schema_type == 'DefinedTerm':
            self._add_defined_term_properties(jsonld)
            
    def _add_product_properties(self, jsonld):
        """Add product-specific properties."""
        # Add brand
        if 'manufacturer' in self.frontmatter:
            jsonld['brand'] = {
                "@type": "Brand", 
                "name": self.frontmatter['manufacturer']
            }
            
        # Add specifications as product attributes
        if 'technicalSpecifications' in self.frontmatter:
            specs = self.frontmatter['technicalSpecifications']
            if isinstance(specs, dict):
                properties = []
                for name, value in specs.items():
                    properties.append({
                        "@type": "PropertyValue",
                        "name": name,
                        "value": str(value)
                    })
                if properties:
                    jsonld['additionalProperty'] = properties
                    
    # Similar methods for other schema types...
    
    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt template from local YAML file."""
        try:
            prompt_path = Path(__file__).parent / "prompt.yaml"
            with open(prompt_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            return {}
    
    def _build_prompt(self) -> str:
        """Build JSON-LD prompt using template."""
        schema_template = self._build_schema_template()
        
        if not schema_template:
            logger.error("No schema fields available for JSON-LD generation")
            return None
        
        # Use template from prompt config
        template = self.prompt_config.get("template", "")
        if not template:
            logger.error("No prompt template found")
            return None
        
        return template.format(
            article_type=self.article_type,
            subject=self.subject,
            schema_template=schema_template
        )
    
    def _build_schema_template(self) -> str:
        """Build template using updated schema structure."""
        # Updated profile key handling for new schema organization
        profile_keys = [
            f"{self.article_type}Profile",  # Standard: "applicationProfile"
            "termProfile",                  # Thesaurus: "termProfile"
            f"{self.article_type}_profile", # Snake case
            f"{self.article_type.title()}Profile",  # Title case
            "schema"                        # New unified schema key
        ]
        
        profile = None
        for key in profile_keys:
            if key in self.schema:
                profile = self.schema[key]
                logger.info(f"✅ Found profile using key: {key}")
                break
        
        if profile:
            # Check if we have a nested structure with fieldsets
            if "fieldsets" in profile:
                return self._build_template_from_fieldsets(profile["fieldsets"])
            # Check if we have a nested structure with fields
            elif "fields" in profile:
                return self._build_template_from_fields(profile["fields"])
            # Otherwise use the existing profile approach
            else:
                return self._build_schema_template_from_profile(profile)
        else:
            logger.error(f"❌ No profile found. Tried keys: {profile_keys}")
            logger.error(f"❌ Available schema keys: {list(self.schema.keys())}")
            return None  # NO FALLBACK - FAIL FAST
    
    def _build_template_from_fieldsets(self, fieldsets: Dict[str, Any]) -> str:
        """Build template from the new fieldset-based schema structure."""
        schema_parts = []
        
        # Add schema.org context header
        schema_parts.append(f"## Schema.org JSON-LD Structure for {self.subject}")
        schema_parts.append("Based on Schema.org TechnicalArticle (https://schema.org/TechnicalArticle)")
        schema_parts.append("=" * 60)
        
        # Add base structure
        schema_parts.append("Base structure to include:")
        schema_parts.append("```json")
        schema_parts.append('{')
        schema_parts.append('  "@context": "https://schema.org",')
        schema_parts.append('  "@type": "TechnicalArticle",')
        schema_parts.append('  "headline": "Title goes here",')
        schema_parts.append('  "description": "Description goes here",')
        schema_parts.append('  "url": "https://z-beam.com/path/to/article"')
        schema_parts.append('}')
        schema_parts.append("```")
        schema_parts.append("=" * 60)
        
        # Process key fields from each fieldset that should be included in JSON-LD
        schema_parts.append("## Key fields to incorporate from article schema:")
        
        # Track fields across all fieldsets
        jsonld_fields = []
        
        for fieldset_name, fieldset in fieldsets.items():
            if "fields" in fieldset:
                for field_name, field_def in fieldset["fields"].items():
                    # Only include fields that make sense for JSON-LD
                    if field_name in ["name", "headline", "description", "keywords", 
                                      "articleBody", "author", "datePublished", "publisher"]:
                        
                        jsonld_fields.append(field_name)
                        schema_parts.append(f"\n### Field: {field_name}")
                        
                        # Add field type and description
                        field_type = field_def.get("type", "unknown")
                        field_description = field_def.get("description", "No description")
                        schema_parts.append(f"Type: {field_type}")
                        schema_parts.append(f"Description: {field_description}")
                        
                        # Add example with mapping instruction
                        if "example" in field_def:
                            example = field_def["example"]
                            if isinstance(example, str):
                                processed_value = self._replace_placeholders(example)
                                schema_parts.append(f"Example: {processed_value}")
                                schema_parts.append(f"Map to: \"{field_name}\" in JSON-LD")
                            elif isinstance(example, list):
                                processed_items = [self._replace_placeholders(str(item)) for item in example]
                                schema_parts.append(f"Examples: {processed_items}")
                                schema_parts.append(f"Map to: \"{field_name}\" array in JSON-LD")
        
        # Add special instructions for required JSON-LD fields
        schema_parts.append("\n## Required JSON-LD Fields")
        schema_parts.append("The following fields MUST be included in the JSON-LD output:")
        schema_parts.append("- @context (set to 'https://schema.org')")
        schema_parts.append("- @type (set to 'TechnicalArticle')")
        schema_parts.append(f"- headline (use appropriate title for {self.subject})")
        schema_parts.append("- description (comprehensive description)")
        schema_parts.append("- author (structured Person or Organization object)")
        schema_parts.append("- publisher (structured Organization object)")
        schema_parts.append(f"- url (format: https://z-beam.com/{self.article_type}s/{self.subject.lower().replace(' ', '-')})")
        schema_parts.append("- datePublished (use current date)")
        
        return '\n'.join(schema_parts)
    
    def _build_template_from_fields(self, fields: Dict[str, Any]) -> str:
        """Build template from direct fields structure."""
        schema_parts = []
        
        # Add schema.org context header
        schema_parts.append(f"## Schema.org JSON-LD Structure for {self.subject}")
        schema_parts.append("Based on Schema.org TechnicalArticle (https://schema.org/TechnicalArticle)")
        schema_parts.append("=" * 60)
        
        # Add base structure
        schema_parts.append("Base structure to include:")
        schema_parts.append("```json")
        schema_parts.append('{')
        schema_parts.append('  "@context": "https://schema.org",')
        schema_parts.append('  "@type": "TechnicalArticle",')
        schema_parts.append('  "headline": "Title goes here",')
        schema_parts.append('  "description": "Description goes here",')
        schema_parts.append('  "url": "https://z-beam.com/path/to/article"')
        schema_parts.append('}')
        schema_parts.append("```")
        schema_parts.append("=" * 60)
        
        # Process key fields that should be included in JSON-LD
        schema_parts.append("## Key fields to incorporate from article schema:")
        
        jsonld_fields = []
        
        for field_name, field_def in fields.items():
            # Only include fields that make sense for JSON-LD
            if field_name in ["name", "headline", "description", "keywords", 
                              "articleBody", "author", "datePublished", "publisher"]:
                
                jsonld_fields.append(field_name)
                schema_parts.append(f"\n### Field: {field_name}")
                
                # Add field type and description
                field_type = field_def.get("type", "unknown")
                field_description = field_def.get("description", "No description")
                schema_parts.append(f"Type: {field_type}")
                schema_parts.append(f"Description: {field_description}")
                
                # Add example with mapping instruction
                if "example" in field_def:
                    example = field_def["example"]
                    if isinstance(example, str):
                        processed_value = self._replace_placeholders(example)
                        schema_parts.append(f"Example: {processed_value}")
                        schema_parts.append(f"Map to: \"{field_name}\" in JSON-LD")
                    elif isinstance(example, list):
                        processed_items = [self._replace_placeholders(str(item)) for item in example]
                        schema_parts.append(f"Examples: {processed_items}")
                        schema_parts.append(f"Map to: \"{field_name}\" array in JSON-LD")
        
        # Add special instructions for required JSON-LD fields
        schema_parts.append("\n## Required JSON-LD Fields")
        schema_parts.append("The following fields MUST be included in the JSON-LD output:")
        schema_parts.append("- @context (set to 'https://schema.org')")
        schema_parts.append("- @type (set to 'TechnicalArticle')")
        schema_parts.append(f"- headline (use appropriate title for {self.subject})")
        schema_parts.append("- description (comprehensive description)")
        schema_parts.append("- author (structured Person or Organization object)")
        schema_parts.append("- publisher (structured Organization object)")
        schema_parts.append(f"- url (format: https://z-beam.com/{self.article_type}s/{self.subject.lower().replace(' ', '-')})")
        schema_parts.append("- datePublished (use current date)")
        
        return '\n'.join(schema_parts)
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build schema template from legacy profile structure."""
        schema_parts = []
        
        # Add schema.org context header
        schema_parts.append(f"## Schema.org JSON-LD Structure for {self.subject}")
        schema_parts.append("Based on Schema.org TechnicalArticle (https://schema.org/TechnicalArticle)")
        schema_parts.append("=" * 60)
        
        # Add base structure
        schema_parts.append("Base structure to include:")
        schema_parts.append("```json")
        schema_parts.append('{')
        schema_parts.append('  "@context": "https://schema.org",')
        schema_parts.append('  "@type": "TechnicalArticle",')
        schema_parts.append('  "headline": "Title goes here",')
        schema_parts.append('  "description": "Description goes here",')
        schema_parts.append('  "url": "https://z-beam.com/path/to/article"')
        schema_parts.append('}')
        schema_parts.append("```")
        schema_parts.append("=" * 60)
        
        # Process key fields that should be included in JSON-LD
        schema_parts.append("## Key fields to incorporate from article schema:")
        
        jsonld_fields = []
        
        for field_name, field_def in profile.items():
            if isinstance(field_def, dict) and "example" in field_def:
                # Only include fields that make sense for JSON-LD
                if field_name in ["name", "headline", "description", "keywords", 
                                  "articleBody", "author", "datePublished", "publisher"]:
                    
                    jsonld_fields.append(field_name)
                    schema_parts.append(f"\n### Field: {field_name}")
                    
                    # Add field type and description
                    field_type = field_def.get("type", "unknown")
                    field_description = field_def.get("description", "No description")
                    schema_parts.append(f"Type: {field_type}")
                    schema_parts.append(f"Description: {field_description}")
                    
                    # Add example with mapping instruction
                    example = field_def["example"]
                    if isinstance(example, str):
                        processed_value = self._replace_placeholders(example)
                        schema_parts.append(f"Example: {processed_value}")
                        schema_parts.append(f"Map to: \"{field_name}\" in JSON-LD")
                    elif isinstance(example, list):
                        processed_items = [self._replace_placeholders(str(item)) for item in example]
                        schema_parts.append(f"Examples: {processed_items}")
                        schema_parts.append(f"Map to: \"{field_name}\" array in JSON-LD")
        
        # Add special instructions for required JSON-LD fields
        schema_parts.append("\n## Required JSON-LD Fields")
        schema_parts.append("The following fields MUST be included in the JSON-LD output:")
        schema_parts.append("- @context (set to 'https://schema.org')")
        schema_parts.append("- @type (set to 'TechnicalArticle')")
        schema_parts.append(f"- headline (use appropriate title for {self.subject})")
        schema_parts.append("- description (comprehensive description)")
        schema_parts.append("- author (structured Person or Organization object)")
        schema_parts.append("- publisher (structured Organization object)")
        schema_parts.append(f"- url (format: https://z-beam.com/{self.article_type}s/{self.subject.lower().replace(' ', '-')})")
        schema_parts.append("- datePublished (use current date)")
        
        return '\n'.join(schema_parts)
    
    def _replace_placeholders(self, value: str) -> str:
        """Replace schema placeholders with context-specific values."""
        placeholder_map = {
            "materialName": self.subject,
            "applicationName": self.subject,
            "regionName": self.subject,
            "term": self.subject,
            "{{materialName}}": self.subject,
            "{{applicationName}}": self.subject,
            "{{regionName}}": self.subject,
            "{{term}}": self.subject
        }
        
        for placeholder, replacement in placeholder_map.items():
            value = value.replace(placeholder, replacement)
        
        return value
    
    def _clean_response(self, response: str) -> str:
        """Clean the API response to extract JSON-LD."""
        if not response:
            return ""
            
        # Try to find JSON content
        json_pattern = r'```(?:json)?(.*?)```|(\{[\s\S]*\})'
        matches = re.search(json_pattern, response, re.DOTALL)
        
        if matches:
            # If we found JSON in a code block
            if matches.group(1):
                json_content = matches.group(1).strip()
            # Or if we found a standalone JSON object
            else:
                json_content = matches.group(2).strip()
                
            logger.info("Extracted JSON content")
            return json_content
        else:
            # If no JSON blocks found, use the whole response
            logger.warning("No JSON blocks found, using entire response")
            return response.strip()
    
    def _generate_fallback(self) -> str:
        """Generate fallback JSON-LD."""
        logger.info("Generating fallback JSON-LD")
        
        slug = self.subject.lower().replace(' ', '-')
        article_type_plural = f"{self.article_type}s"
        if self.article_type == "thesaurus":
            article_type_plural = "glossary"
            
        current_date = "2025-07-17"  # You can use datetime for actual current date
        
        fallback_data = {
            "@context": "https://schema.org",
            "@type": "TechnicalArticle",
            "headline": f"{self.subject} in Laser Cleaning Applications",
            "description": f"Comprehensive technical information about {self.subject} in the context of industrial laser cleaning applications, including specifications, uses, and best practices.",
            "url": f"https://z-beam.com/{article_type_plural}/{slug}",
            "datePublished": current_date,
            "keywords": [
                "laser cleaning", 
                self.subject, 
                "industrial cleaning", 
                "surface treatment",
                "laser technology"
            ],
            "author": {
                "@type": "Person",
                "name": "Dr. Elena Rodriguez",
                "description": "PhD in Laser Physics with 15 years experience in industrial laser applications"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Z-Beam Technologies",
                "location": [{
                    "@type": "Place",
                    "name": "Z-Beam R&D Center",
                    "address": "San Francisco, California",
                    "geo": {
                        "@type": "GeoCoordinates",
                        "latitude": "37.7749",
                        "longitude": "-122.4194"
                    }
                }]
            }
        }
        
        return json.dumps(fallback_data, indent=2)
    
    def _generate_fallback_jsonld(self):
        """Generate minimal JSON-LD as fallback."""
        subject = self.context.get('subject', '')
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"{subject}",
            "description": f"Information about {subject}",
            "publisher": {
                "@type": "Organization",
                "name": "Z-Beam Technologies"
            }
        }
        formatted_jsonld = json.dumps(jsonld, indent=2)
        return f"```json\n{formatted_jsonld}\n```"
    
    def _generate_url(self, subject: str, article_type: str) -> str:
        """Generate URL for the article."""
        slug = subject.lower().replace(' ', '-')
        
        # Handle special plural forms
        if article_type == "thesaurus":
            return f"https://z-beam.com/glossary/{slug}"
        else:
            return f"https://z-beam.com/{article_type}s/{slug}"
    
    def _final_url_check(self, json_content: str) -> str:
        """Ensure URL is properly formatted in JSON-LD."""
        # Check if URL is missing and add it if necessary
        if '"url":' not in json_content:
            logger.warning("URL field missing from JSON-LD, adding it")
            # Insert URL before the last closing brace
            url_value = f'"url": "{self._generate_url(self.subject, self.article_type)}"'
            json_content = json_content.rstrip().rstrip('}') + ',\n  ' + url_value + '\n}'
        
        return json_content