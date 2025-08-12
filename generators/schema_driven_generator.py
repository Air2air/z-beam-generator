"""
Schema-Driven Document Generator

Completely dynamic generation based on JSON schemas.
No hardcoded field names or structures.
Single source of truth: schemas directory.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class SchemaDrivenGenerator:
    """Generate complete documents using only schema definitions as source of truth."""
    
    def __init__(self, ai_provider: str = "deepseek", options: Dict[str, Any] = None):
        self.ai_provider = ai_provider
        self.options = options or {"model": "deepseek-chat", "max_tokens": 8000}
        
        # Import BATCH_CONFIG for component settings
        from run import BATCH_CONFIG
        self.config = BATCH_CONFIG
        self._schema_cache = {}
    
    def generate_complete_document(self, subject: str, article_type: str, 
                                 category: str, author_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete document using only schema definitions."""
        
        try:
            # Load schema for article type
            schema = self._load_schema(article_type)
            
            # Build context with schema
            context = {
                "subject": subject,
                "article_type": article_type,
                "category": category,
                "author_context": author_data.get("author_name", "Expert") + " from " + author_data.get("author_country", "International"),
                "schema": schema
            }
            
            # Get enabled components from config
            enabled_components = self._get_enabled_components()
            
            # Create unified prompt with schema structure
            prompt = self._build_schema_driven_prompt(context, enabled_components, schema)
            
            # Single API call
            response = self._call_api(prompt)
            
            # Parse and validate response against schema
            parsed_components = self._parse_and_validate_response(response, schema, enabled_components)
            
            return {
                "success": True,
                "components": parsed_components,
                "subject": subject,
                "category": category,
                "article_type": article_type
            }
            
        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "subject": subject,
                "category": category,
                "article_type": article_type
            }
    
    def _load_schema(self, article_type: str) -> Dict[str, Any]:
        """Load schema from schemas directory, merging with base schema."""
        if article_type in self._schema_cache:
            return self._schema_cache[article_type]
        
        # Load base schema first
        base_schema_path = os.path.join("schemas", "base.json")
        if not os.path.exists(base_schema_path):
            raise FileNotFoundError(f"Base schema not found: {base_schema_path}")
        
        with open(base_schema_path, 'r') as f:
            base_schema = json.load(f)
        
        # Load specific schema
        schema_path = os.path.join("schemas", f"{article_type}.json")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        
        with open(schema_path, 'r') as f:
            specific_schema = json.load(f)
        
        # Merge schemas: specific schema overrides base schema
        merged_schema = self._merge_schemas(base_schema, specific_schema)
        
        self._schema_cache[article_type] = merged_schema
        return merged_schema
    
    def _merge_schemas(self, base_schema: Dict[str, Any], specific_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Merge base schema with specific schema, specific schema takes precedence."""
        import copy
        
        # Start with deep copy of base schema
        merged = copy.deepcopy(base_schema)
        
        # Get the profile keys (baseProfile, materialProfile, etc.)
        base_profile_key = next((k for k in base_schema.keys() if 'Profile' in k), None)
        specific_profile_key = next((k for k in specific_schema.keys() if 'Profile' in k), None)
        
        if base_profile_key and specific_profile_key:
            # Merge at the profile level
            base_profile = merged[base_profile_key]
            specific_profile = specific_schema[specific_profile_key]
            
            # Deep merge each section
            for section_key, section_value in specific_profile.items():
                if section_key in base_profile:
                    if isinstance(section_value, dict) and isinstance(base_profile[section_key], dict):
                        # Recursively merge dictionaries
                        base_profile[section_key] = self._deep_merge_dict(base_profile[section_key], section_value)
                    else:
                        # Override with specific value
                        base_profile[section_key] = section_value
                else:
                    # Add new section from specific schema
                    base_profile[section_key] = section_value
            
            # Use the specific profile key as the merged key
            if base_profile_key != specific_profile_key:
                merged[specific_profile_key] = merged.pop(base_profile_key)
        
        return merged
    
    def _deep_merge_dict(self, base_dict: Dict[str, Any], override_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, override takes precedence."""
        import copy
        result = copy.deepcopy(base_dict)
        
        for key, value in override_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dict(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _get_enabled_components(self) -> List[str]:
        """Get enabled components from BATCH_CONFIG."""
        # Default components if not specified
        default_components = ["frontmatter", "content", "table", "bullets", "tags", "metatags", "jsonld", "caption", "propertiestable"]
        
        # Check if components are specified in config
        if "components" in self.config:
            return self.config["components"]
        
        # Check for component-specific configuration
        enabled = []
        for component in default_components:
            if component in self.config and self.config[component].get("enabled", True):
                enabled.append(component)
        
        return enabled if enabled else default_components
    
    def _build_schema_driven_prompt(self, context: Dict[str, Any], enabled_components: List[str], schema: Dict[str, Any]) -> str:
        """Build prompt using only schema definitions."""
        
        material_profile = schema.get("materialProfile", {})
        generator_config = material_profile.get("generatorConfig", {})
        validation_config = material_profile.get("validation", {})
        
        # Build component requirements from schema
        component_requirements = []
        json_structure_parts = []
        
        for component in enabled_components:
            component_schema = self._extract_component_schema_structure(component, schema)
            component_validation = validation_config.get(component, {})
            component_generator_config = generator_config.get(component, {})
            
            # Build requirement for this component
            requirement = self._build_component_requirement_from_schema(
                component, component_schema, component_validation, component_generator_config, context
            )
            
            if requirement:
                component_requirements.append(requirement)
                
            # Build JSON structure definition
            json_structure = self._build_json_structure_from_schema(component, component_schema)
            if json_structure:
                json_structure_parts.append(f'"{component}": {json_structure}')
        
        # Build the complete prompt
        prompt = f"""
Generate complete technical documentation for {context['subject']} ({context['article_type']}) using the following schema-driven requirements:

SUBJECT: {context['subject']}
CATEGORY: {context['category']}
ARTICLE TYPE: {context['article_type']}
AUTHOR CONTEXT: {context['author_context']}

COMPONENT REQUIREMENTS (derived from schema):
{chr(10).join(component_requirements)}

REQUIRED JSON OUTPUT STRUCTURE:
{{
  {','.join(json_structure_parts)}
}}

CRITICAL INSTRUCTIONS:
1. Follow the exact JSON structure defined above
2. All field names and structures are derived from the schema - do not deviate
3. Provide complete, accurate technical content for each component
4. Ensure all required fields from schema validation are included
5. Use proper technical terminology and measurements
6. Output ONLY the JSON structure with the requested components

Generate the complete JSON response now:
"""

        return prompt
    
    def _extract_component_schema_structure(self, component: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract complete schema structure for a component."""
        material_profile = schema.get("materialProfile", {})
        profile = material_profile.get("profile", {})
        validation = material_profile.get("validation", {}).get(component, {})
        generator_config = material_profile.get("generatorConfig", {}).get(component, {})
        
        component_schema = {}
        
        if component == "frontmatter":
            # Build from profile schema and validation requirements
            required_fields = validation.get("requiredFields", [])
            for field in required_fields:
                if field in profile:
                    field_config = profile[field]
                    component_schema[field] = self._convert_schema_to_structure(field_config)
        
        elif component == "table":
            # Extract table configuration from generator config
            if generator_config:
                component_schema = generator_config
            else:
                # Build default table structure from properties
                component_schema = {
                    "headers": ["Property", "Value", "Unit"],
                    "rows": []
                }
        
        elif component == "metatags":
            # Extract from validation requirements
            required_fields = validation.get("requiredFields", ["meta_title", "meta_description", "meta_keywords"])
            for field in required_fields:
                field_validation = validation.get("fieldValidation", {}).get(field, {})
                component_schema[field] = {
                    "type": "string",
                    "maxLength": field_validation.get("maxLength", 200)
                }
        
        elif component == "jsonld":
            # Extract JSON-LD schema type and structure
            jsonld_config = generator_config
            if jsonld_config:
                component_schema = jsonld_config
            else:
                component_schema = {
                    "headline": "string",
                    "description": "string", 
                    "keywords": ["array"],
                    "articleBody": "string"
                }
        
        elif component in ["bullets", "tags"]:
            # Array-based components
            component_schema = {
                "type": "array",
                "items": "string",
                "minItems": validation.get("minItems", 1),
                "maxItems": validation.get("maxItems", 20)
            }
        
        elif component == "content":
            # Content generation with sections from schema
            content_config = material_profile.get("generatorConfig", {}).get("contentGeneration", {})
            field_mapping = content_config.get("fieldContentMapping", {})
            if field_mapping:
                component_schema = {
                    "sections": list(field_mapping.keys()),
                    "fieldMapping": field_mapping,
                    "minWords": validation.get("minWords", 500),
                    "maxWords": validation.get("maxWords", 2000)
                }
            else:
                component_schema = {
                    "type": "string",
                    "minLength": validation.get("minLength", 500)
                }
        
        else:
            # Generic component - try to extract from validation
            if validation:
                component_schema = validation
            else:
                component_schema = {"type": "string"}
        
        return component_schema
    
    def _convert_schema_to_structure(self, field_config: Dict[str, Any]) -> Any:
        """Convert schema field configuration to expected structure."""
        field_type = field_config.get("type", "string")
        
        if field_type == "object":
            properties = field_config.get("properties", {})
            return {prop: self._convert_schema_to_structure(prop_config) 
                    for prop, prop_config in properties.items()}
        elif field_type == "array":
            items = field_config.get("items", {})
            if items:
                return [self._convert_schema_to_structure(items)]
            else:
                return []
        else:
            # Return type indicator for JSON structure
            return f"<{field_type}>"
    
    def _build_component_requirement_from_schema(self, component: str, component_schema: Dict[str, Any], 
                                               validation: Dict[str, Any], generator_config: Dict[str, Any],
                                               context: Dict[str, Any]) -> str:
        """Build component requirement from schema data."""
        
        requirements = [f"- {component}:"]
        
        # Add schema structure requirements
        if component_schema:
            requirements.append(f"  Schema structure: {json.dumps(component_schema, indent=4)}")
        
        # Add validation requirements
        if validation:
            required_fields = validation.get("requiredFields", [])
            if required_fields:
                requirements.append(f"  Required fields: {', '.join(required_fields)}")
            
            min_length = validation.get("minLength")
            if min_length:
                requirements.append(f"  Minimum length: {min_length} characters")
                
            max_length = validation.get("maxLength")
            if max_length:
                requirements.append(f"  Maximum length: {max_length} characters")
            
            content_rules = validation.get("contentRules", [])
            if content_rules:
                requirements.append(f"  Content rules: {', '.join(content_rules)}")
        
        # Add generator-specific instructions
        if generator_config:
            requirements.append(f"  Generator config: {json.dumps(generator_config, indent=4)}")
        
        # Add content-specific instructions for content component
        if component == "content":
            field_mapping = context.get("schema", {}).get("materialProfile", {}).get("generatorConfig", {}).get("contentGeneration", {}).get("fieldContentMapping", {})
            if field_mapping:
                requirements.append("  Content sections:")
                for field, description in field_mapping.items():
                    # Replace {subject} placeholder
                    formatted_description = description.replace("{subject}", context["subject"])
                    requirements.append(f"    - {field}: {formatted_description}")
        
        return "\\n".join(requirements)
    
    def _build_json_structure_from_schema(self, component: str, component_schema: Dict[str, Any]) -> str:
        """Build JSON structure definition from schema."""
        if not component_schema:
            return '"<string>"'
        
        if component_schema.get("type") == "array":
            return '["item1", "item2", "..."]'
        elif component_schema.get("type") == "object" or isinstance(component_schema, dict):
            # Build object structure
            if "properties" in component_schema:
                properties = component_schema["properties"]
                prop_structure = []
                for prop, prop_config in properties.items():
                    prop_type = prop_config.get("type", "string")
                    if prop_type == "array":
                        prop_structure.append(f'"{prop}": ["..."]')
                    elif prop_type == "object":
                        prop_structure.append(f'"{prop}": {{}}')
                    else:
                        prop_structure.append(f'"{prop}": "..."')
                return "{" + ", ".join(prop_structure) + "}"
            else:
                # Generic object with known fields
                prop_structure = []
                for key, value in component_schema.items():
                    if key not in ["type", "minItems", "maxItems", "minLength", "maxLength"]:
                        if isinstance(value, list):
                            prop_structure.append(f'"{key}": ["..."]')
                        elif isinstance(value, dict):
                            prop_structure.append(f'"{key}": {{}}')
                        else:
                            prop_structure.append(f'"{key}": "..."')
                
                if prop_structure:
                    return "{" + ", ".join(prop_structure) + "}"
                else:
                    return '"{}"'
        else:
            return '"<string>"'
    
    def _call_api(self, prompt: str) -> str:
        """Make API call to generate content."""
        # Import API client dynamically
        if self.ai_provider == "deepseek":
            from api.deepseek import DeepseekClient
            client = DeepseekClient()
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
        
        # Make the API call
        response = client.generate_content(prompt, **self.options)
        return response
    
    def _parse_and_validate_response(self, response: str, schema: Dict[str, Any], enabled_components: List[str]) -> Dict[str, Any]:
        """Parse API response and validate against schema."""
        try:
            # Try to parse JSON from response
            if response.strip().startswith('{'):
                parsed = json.loads(response.strip())
            else:
                # Extract JSON from response if wrapped in other text
                import re
                json_match = re.search(r'{.*}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
            
            # Validate that required components are present
            validated_components = {}
            for component in enabled_components:
                if component in parsed:
                    validated_components[component] = parsed[component]
                else:
                    logger.warning(f"Component {component} missing from response")
            
            return validated_components
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            raise ValueError(f"Response validation error: {e}")
