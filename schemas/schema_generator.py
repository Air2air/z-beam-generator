#!/usr/bin/env python3
"""
Schema Generator - Updated to remove tag and JSON-LD rules
"""
import os
import yaml
from typing import Dict, Any
from .base_schema import BaseSchema

class SchemaGenerator(BaseSchema):
    """Universal schema generator - 100% prompt-driven, no tag/JSON-LD rules"""
    
    def __init__(self, schema_type: str):
        super().__init__(schema_type)
        self.prompt_config = self._load_prompt_config()
    
    def _load_prompt_config(self) -> Dict[str, Any]:
        """Load configuration from {schema_type}_schema_prompt.md"""
        prompt_file = os.path.join(os.path.dirname(__file__), f"{self.schema_type}_schema_prompt.md")
        
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML configuration from prompt file
        if '```yaml' in content:
            yaml_start = content.find('```yaml') + 7
            yaml_end = content.find('```', yaml_start)
            yaml_content = content[yaml_start:yaml_end].strip()
            
            try:
                config = yaml.safe_load(yaml_content)
                if not config:
                    raise ValueError(f"Empty YAML configuration in {prompt_file}")
                return config
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in {prompt_file}: {e}")
        
        # If no YAML found, return empty config to use defaults
        return {}
    
    def enhance_metadata(self, metadata: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata fields from prompt config"""
        metadata_fields = self.prompt_config.get("metadataFields", {})
        
        # Add schema type and subject
        metadata["articleType"] = self.schema_type
        metadata["subject"] = context["subject"]
        
        # Add all fields defined in prompt config
        for field_name, field_config in metadata_fields.items():
            if isinstance(field_config, dict):
                if "default" in field_config:
                    metadata[field_name] = field_config["default"]
                elif field_config.get("useSubject", False):
                    metadata[field_name] = context["subject"]
                elif field_config.get("useContext"):
                    context_key = field_config["useContext"]
                    if context_key in context:
                        metadata[field_name] = context[context_key]
            elif isinstance(field_config, str):
                metadata[field_name] = field_config
        
        return metadata
    
    def get_filename_template(self) -> str:
        """Get filename template from prompt config"""
        if "filenameTemplate" not in self.prompt_config:
            # Default filename template - use subject from context
            return f"{self.schema_type}_{{subject}}.md"
        
        return self.prompt_config["filenameTemplate"]
    
    def get_output_rules(self) -> Dict[str, Any]:
        """Get output rules from prompt config"""
        if "outputRules" not in self.prompt_config:
            # Default output rules
            return {
                "directory": f"output/{self.schema_type}",
                "create_dirs": True,
                "encoding": "utf-8"
            }
        
        return self.prompt_config["outputRules"]
    
    def get_article_template(self) -> str:
        """Get article template - use default if not specified"""
        if "articleTemplate" not in self.prompt_config:
            # Default article template - title comes from metadata
            return """---
{metadata_yaml}
---

# {title}

## Tags

{formatted_tags}

## JSON-LD Structured Data

{formatted_jsonld}

---

<!-- Generated {articleType} article for {subject} -->
<!-- Generated at: {generation_timestamp} -->
"""
        
        return self.prompt_config["articleTemplate"]


def create_schema(schema_type: str) -> SchemaGenerator:
    """Factory function to create schema generator"""
    valid_types = ["thesaurus", "material", "application", "region"]
    
    if schema_type not in valid_types:
        raise ValueError(f"Invalid schema type: {schema_type}. Valid types: {valid_types}")
    
    return SchemaGenerator(schema_type)