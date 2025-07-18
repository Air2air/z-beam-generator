"""Dynamic JSON-LD Generator that automatically structures data from frontmatter."""

import json
import yaml
import logging
from typing import Dict, Any, Optional
from frontmatter.generator import FrontmatterGenerator

logger = logging.getLogger(__name__)

class JsonLdGenerator:
    """Generates JSON-LD structured data dynamically from frontmatter."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        
    def generate(self):
        """Generate rich JSON-LD dynamically from frontmatter data."""
        try:
            # Get frontmatter data
            frontmatter_gen = FrontmatterGenerator(self.context, self.schema, self.ai_provider)
            frontmatter_str = frontmatter_gen.generate()
            
            # Parse the frontmatter
            try:
                # Clean up the frontmatter string for parsing
                clean_str = frontmatter_str
                if clean_str.startswith('---'):
                    parts = clean_str.split('---', 2)
                    if len(parts) >= 2:
                        clean_str = parts[1].strip()
                        
                frontmatter = yaml.safe_load(clean_str)
                if not frontmatter or not isinstance(frontmatter, dict):
                    logger.error("Failed to parse frontmatter or result is not a dictionary")
                    return self._generate_basic_jsonld()
            except Exception as e:
                logger.error(f"Failed to parse frontmatter: {e}")
                return self._generate_basic_jsonld()
            
            # Determine schema.org type based on content
            schema_type = self._determine_schema_type(frontmatter)
            
            # Build base JSON-LD structure
            jsonld = {
                "@context": "https://schema.org",
                "@type": schema_type
            }
            
            # Add core properties
            self._add_core_properties(jsonld, frontmatter, schema_type)
            
            # Add author information
            self._add_author_info(jsonld, frontmatter)
            
            # Add technical details
            self._add_technical_details(jsonld, frontmatter)
            
            # Add applications
            self._add_applications(jsonld, frontmatter)
            
            # Add challenges and outcomes
            self._add_challenges_outcomes(jsonld, frontmatter)
            
            # Add standards and regulations
            self._add_standards(jsonld, frontmatter)
            
            # Add keywords and tags
            self._add_keywords_tags(jsonld, frontmatter)
            
            # Add dates if available
            self._add_dates(jsonld, frontmatter)
            
            # Format as JSON string with indentation
            jsonld_str = json.dumps(jsonld, indent=2)
            
            # Wrap in code block for markdown
            return f"```json\n{jsonld_str}\n```"
            
        except Exception as e:
            logger.error(f"Error generating JSON-LD: {e}", exc_info=True)
            return self._generate_basic_jsonld()
    
    def _determine_schema_type(self, frontmatter):
        """Dynamically determine the best schema.org type based on content."""
        # Check article type from context
        article_type = self.context.get("article_type", "").lower()
        
        # Product indicators
        has_product_features = any(key in frontmatter for key in [
            "technicalSpecifications", "applications"
        ])
        
        # Technical article indicators
        has_technical_content = any(key in frontmatter for key in [
            "regulatoryStandards", "challenges", "outcomes"
        ])
        
        # Determine type based on indicators
        if "product" in article_type or has_product_features:
            return "Product"
        elif "technical" in article_type or has_technical_content:
            return "TechnicalArticle"
        else:
            return "Article"
    
    def _add_core_properties(self, jsonld, frontmatter, schema_type):
        """Add core properties like name, description, etc."""
        # Name/headline
        if "name" in frontmatter:
            prop_name = "name" if schema_type == "Product" else "headline"
            jsonld[prop_name] = frontmatter["name"].capitalize()
            
        # Description
        if "description" in frontmatter:
            jsonld["description"] = frontmatter["description"]
            
        # Website URL
        if "website" in frontmatter:
            jsonld["url"] = frontmatter["website"]
            
        # Always add publisher
        jsonld["publisher"] = {
            "@type": "Organization",
            "name": "Z-Beam Technologies"
        }
    
    def _add_author_info(self, jsonld, frontmatter):
        """Add author information if available."""
        if "author" in frontmatter and isinstance(frontmatter["author"], dict):
            author = {"@type": "Person"}
            
            if "name" in frontmatter["author"]:
                author["name"] = frontmatter["author"]["name"]
                
            if "credentials" in frontmatter["author"]:
                author["description"] = frontmatter["author"]["credentials"]
                
            if author.get("name"):  # Only add if we have at least a name
                jsonld["author"] = author
    
    def _add_technical_details(self, jsonld, frontmatter):
        """Add technical specifications."""
        if "technicalSpecifications" in frontmatter:
            specs = frontmatter["technicalSpecifications"]
            if isinstance(specs, dict) and specs:
                properties = []
                for name, value in specs.items():
                    properties.append({
                        "@type": "PropertyValue",
                        "name": name,
                        "value": str(value)
                    })
                
                if properties:
                    if jsonld["@type"] == "Product":
                        jsonld["additionalProperty"] = properties
                    else:
                        jsonld["about"] = jsonld.get("about", []) + [
                            {"@type": "Thing", "name": f"{name}: {value}"}
                            for name, value in specs.items()
                        ]
    
    def _add_applications(self, jsonld, frontmatter):
        """Add applications as parts or features."""
        if "applications" in frontmatter and isinstance(frontmatter["applications"], list):
            applications = []
            
            for app in frontmatter["applications"]:
                if isinstance(app, dict) and "name" in app:
                    item = {
                        "@type": "ItemList" if jsonld["@type"] == "Product" else "Thing",
                        "name": app["name"]
                    }
                    
                    if "description" in app:
                        item["description"] = app["description"]
                        
                    applications.append(item)
            
            if applications:
                if jsonld["@type"] == "Product":
                    jsonld["hasPart"] = applications
                else:
                    jsonld["mentions"] = applications
    
    def _add_challenges_outcomes(self, jsonld, frontmatter):
        """Add challenges and outcomes."""
        # Add challenges
        if "challenges" in frontmatter and isinstance(frontmatter["challenges"], list):
            challenges = []
            for challenge in frontmatter["challenges"]:
                if isinstance(challenge, dict):
                    item = {"@type": "Thing"}
                    
                    if "issue" in challenge:
                        item["name"] = challenge["issue"]
                        
                    if "solution" in challenge:
                        item["description"] = challenge["solution"]
                        
                    if "name" in item:  # Only add if we have at least a name
                        challenges.append(item)
            
            if challenges:
                jsonld["potentialAction"] = jsonld.get("potentialAction", []) + challenges
        
        # Add outcomes
        if "outcomes" in frontmatter and isinstance(frontmatter["outcomes"], list):
            outcomes = []
            for outcome in frontmatter["outcomes"]:
                if isinstance(outcome, dict):
                    item = {"@type": "Thing"}
                    
                    if "result" in outcome:
                        item["name"] = outcome["result"]
                        
                    if "metric" in outcome:
                        item["description"] = f"Measured by: {outcome['metric']}"
                        
                    if "name" in item:  # Only add if we have at least a name
                        outcomes.append(item)
            
            if outcomes:
                action_type = "potentialAction" if jsonld["@type"] != "Product" else "additionalProperty"
                jsonld[action_type] = jsonld.get(action_type, []) + outcomes
    
    def _add_standards(self, jsonld, frontmatter):
        """Add regulatory standards."""
        if "regulatoryStandards" in frontmatter and isinstance(frontmatter["regulatoryStandards"], list):
            standards = []
            for standard in frontmatter["regulatoryStandards"]:
                if isinstance(standard, dict):
                    item = {"@type": "Thing"}
                    
                    if "code" in standard:
                        item["name"] = standard["code"]
                        
                    if "description" in standard:
                        item["description"] = standard["description"]
                        
                    if "name" in item:  # Only add if we have at least a name
                        standards.append(item)
            
            if standards:
                if jsonld["@type"] == "Product":
                    jsonld["hasProductReturnPolicy"] = standards  # Not ideal but works
                else:
                    jsonld["legislationApplies"] = standards
    
    def _add_keywords_tags(self, jsonld, frontmatter):
        """Add keywords and tags."""
        # Add keywords
        if "keywords" in frontmatter and isinstance(frontmatter["keywords"], list):
            jsonld["keywords"] = frontmatter["keywords"]
            
        # Add tags
        if "tags" in frontmatter and isinstance(frontmatter["tags"], list):
            tag_items = [{"@type": "Thing", "name": tag} for tag in frontmatter["tags"]]
            
            # For Article types, use about. For Product, use category
            if jsonld["@type"] in ["Article", "TechnicalArticle"]:
                jsonld["about"] = jsonld.get("about", []) + tag_items
            else:
                jsonld["category"] = frontmatter["tags"]
    
    def _add_dates(self, jsonld, frontmatter):
        """Add dates if available."""
        if "contentManagement" in frontmatter and isinstance(frontmatter["contentManagement"], dict):
            if "publishedAt" in frontmatter["contentManagement"]:
                jsonld["datePublished"] = frontmatter["contentManagement"]["publishedAt"]
                
            if "lastUpdated" in frontmatter["contentManagement"]:
                jsonld["dateModified"] = frontmatter["contentManagement"]["lastUpdated"]
    
    def _generate_basic_jsonld(self):
        """Generate basic JSON-LD as fallback."""
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.context.get("subject", "").capitalize(),
            "description": f"Information about {self.context.get('subject', '').lower()}",
            "publisher": {
                "@type": "Organization",
                "name": "Z-Beam Technologies"
            }
        }
        
        jsonld_str = json.dumps(jsonld, indent=2)
        return f"```json\n{jsonld_str}\n```"