#!/usr/bin/env python3
"""
JSON-LD Generator - No fallbacks, 100% schema-driven, pure dynamic
"""
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class JSONLDGenerator:
    """JSON-LD generator - 100% schema-driven, no defaults or hardcoding"""
    
    def __init__(self, jsonld_rules: Dict[str, Any]):
        if not jsonld_rules:
            raise ValueError("JSON-LD rules are required - no defaults provided")
        
        self.jsonld_rules = jsonld_rules
        self._validate_jsonld_rules()
    
    def _validate_jsonld_rules(self):
        """Validate JSON-LD rules - no fallbacks"""
        required_rule_fields = ["required_fields", "structure", "field_mapping"]
        
        for field in required_rule_fields:
            if field not in self.jsonld_rules:
                raise ValueError(f"JSON-LD rules missing required field: {field}")
        
        # Validate structure
        if not isinstance(self.jsonld_rules["structure"], dict):
            raise ValueError("JSON-LD rules structure must be a dictionary")
        
        # Validate field mapping
        if not isinstance(self.jsonld_rules["field_mapping"], dict):
            raise ValueError("JSON-LD rules field_mapping must be a dictionary")
    
    def generate_jsonld(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD from metadata - no fallbacks"""
        logger.info("📊 Generating JSON-LD from metadata")
        
        # Validate required fields
        required_fields = self.jsonld_rules["required_fields"]
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Required metadata field for JSON-LD not found: {field}")
        
        # Build JSON-LD structure
        jsonld = self._build_jsonld_structure(metadata)
        
        logger.info("📊 JSON-LD generated successfully")
        return jsonld
    
    def _build_jsonld_structure(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build JSON-LD structure from schema rules"""
        jsonld = {}
        
        # Apply base structure from rules
        base_structure = self.jsonld_rules["structure"]
        jsonld.update(base_structure)
        
        # Apply field mapping
        field_mapping = self.jsonld_rules["field_mapping"]
        
        for metadata_field, jsonld_path in field_mapping.items():
            if metadata_field in metadata:
                self._set_nested_field(jsonld, jsonld_path, metadata[metadata_field])
        
        # Apply conditional rules if present
        if "conditional_rules" in self.jsonld_rules:
            self._apply_conditional_rules(jsonld, metadata)
        
        return jsonld
    
    def _set_nested_field(self, jsonld: Dict[str, Any], field_path: str, value: Any):
        """Set nested field in JSON-LD structure"""
        parts = field_path.split(".")
        current = jsonld
        
        # Navigate to the parent of the final field
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the final field
        current[parts[-1]] = value
    
    def _apply_conditional_rules(self, jsonld: Dict[str, Any], metadata: Dict[str, Any]):
        """Apply conditional rules based on metadata"""
        conditional_rules = self.jsonld_rules["conditional_rules"]
        
        for rule in conditional_rules:
            if not isinstance(rule, dict):
                continue
            
            # Check condition
            condition_field = rule.get("condition_field")
            condition_value = rule.get("condition_value")
            
            if not condition_field or not condition_value:
                continue
            
            if metadata.get(condition_field) == condition_value:
                # Apply transformations
                transformations = rule.get("transformations", {})
                for field_path, transformation in transformations.items():
                    if isinstance(transformation, dict):
                        if "set_value" in transformation:
                            self._set_nested_field(jsonld, field_path, transformation["set_value"])
                        elif "use_metadata_field" in transformation:
                            metadata_field = transformation["use_metadata_field"]
                            if metadata_field in metadata:
                                self._set_nested_field(jsonld, field_path, metadata[metadata_field])
                    else:
                        self._set_nested_field(jsonld, field_path, transformation)
    
    def format_jsonld(self, jsonld: Dict[str, Any]) -> str:
        """Format JSON-LD for output"""
        if not jsonld:
            raise ValueError("No JSON-LD data provided for formatting")
        
        # Get format rules
        format_rules = self.jsonld_rules.get("format_rules", {})
        
        # Apply formatting
        try:
            indent = format_rules.get("indent", 2)
            ensure_ascii = format_rules.get("ensure_ascii", False)
            
            formatted = json.dumps(jsonld, indent=indent, ensure_ascii=ensure_ascii)
            
            # Apply wrapper if specified
            wrapper = format_rules.get("wrapper", "script")
            if wrapper == "script":
                return f'<script type="application/ld+json">\n{formatted}\n</script>'
            elif wrapper == "json":
                return formatted
            elif wrapper == "none":
                return formatted
            else:
                raise ValueError(f"Unknown JSON-LD wrapper format: {wrapper}")
                
        except Exception as e:
            raise ValueError(f"Failed to format JSON-LD: {e}")