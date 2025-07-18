"""Content generation utilities for frontmatter generator."""

import logging
import hashlib
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class DefaultContentGenerator:
    """Generates default content for frontmatter fields based on schema."""
    
    def __init__(self, schema: Dict[str, Any], article_type: str, subject: str):
        """Initialize with schema and context."""
        self.schema = schema
        self.article_type = article_type
        self.subject = subject
        
        # Import schema parser for field definitions
        from frontmatter.schema_parser import SchemaParser
        self.schema_parser = SchemaParser(schema, article_type, subject)
    
    def expand_description(self, description: str) -> str:
        """Expand description dynamically based on schema config."""
        # Try to get expansion templates from schema
        profile = self.schema_parser.get_profile()
        templates = profile.get("generatorConfig", {}).get("descriptionTemplates", {})
        
        # Use schema-defined templates if available
        if self.article_type in templates:
            return f"{description} {templates[self.article_type].format(subject=self.subject)}"
        
        # Dynamic fallback based on article type
        industry_terms = {
            "application": ["surface preparation", "contaminant removal", "substrate integrity"],
            "material": ["optimal parameters", "surface quality", "cleaning efficiency"],
            "region": ["local regulations", "industry standards", "environmental compliance"]
        }
        
        terms = industry_terms.get(self.article_type, ["precision", "efficiency", "quality"])
        term = terms[hash(self.subject) % len(terms)]
        
        return f"{description} Additional information about {self.subject} {term} in laser cleaning applications."
    
    def generate_default_value(self, field_name: str, field_def: Dict[str, Any], field_type: str = None) -> Any:
        """Generate default value based on field definition and type."""
        if not field_type:
            field_type = field_def.get("type", "string")
    
        # Log the field being generated
        logging.debug(f"Generating default value for {field_name} ({field_type})")
    
        # Get example from definition if available
        example = field_def.get("example", None)
    
        if field_type == "string":
            # Use example as template if available
            if example and isinstance(example, str):
                return self._personalize_example(example)
            return f"Information about {self.subject} {field_name.replace('_', ' ')}"
            
        elif field_type == "array":
            # Get array items definition
            items_def = field_def.get("items", {})
            items_type = items_def.get("type", "string")
            
            # Use examples from schema if available
            if example and isinstance(example, list) and len(example) > 0:
                # Clone the example to avoid modifying it
                return [self._personalize_example(item) for item in example[:3]]
                
            # Default array items based on type
            if items_type == "string":
                return [f"Key aspect of {field_name} for {self.subject}", f"Important {field_name} factor"]
            elif items_type == "object":
                # Use item properties to guide generation
                properties = items_def.get("properties", {})
                return [self._generate_object_item(properties) for _ in range(2)]
                
            return [f"{field_name} item 1", f"{field_name} item 2"]
            
        elif field_type == "object":
            # Special case for objects - look at properties
            properties = field_def.get("properties", {})
            
            # Create object with appropriate properties
            result = {}
            
            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get("type", "string")
                
                # Get example from property definition
                prop_example = prop_def.get("example", None)
                
                if prop_type == "string":
                    if prop_example and isinstance(prop_example, str):
                        result[prop_name] = self._personalize_example(prop_example)
                    else:
                        result[prop_name] = f"Information about {self.subject} {prop_name.replace('_', ' ')}"
                
                elif prop_type == "array":
                    if prop_example and isinstance(prop_example, list) and len(prop_example) > 0:
                        # Use examples from schema
                        result[prop_name] = [self._personalize_example(item) for item in prop_example[:3]]
                    else:
                        # Default array content
                        result[prop_name] = [f"Key {prop_name} factor for {self.subject}", f"Important {prop_name} metric"]
            
            return result
            
        # Default fallback for other types
        return f"Default value for {field_name}"

    def _personalize_example(self, example: str) -> str:
        """Personalize an example string by replacing placeholders."""
        if not example or not isinstance(example, str):
            return example
            
        # Replace {subject} with actual subject
        return example.replace("{subject}", self.subject)

    def _generate_object_item(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Generate object item based on property definitions."""
        result = {}
        
        for prop_name, prop_def in properties.items():
            prop_type = prop_def.get("type", "string")
            prop_example = prop_def.get("example", None)
            
            if prop_type == "string":
                if prop_example and isinstance(prop_example, str):
                    result[prop_name] = self._personalize_example(prop_example)
                else:
                    result[prop_name] = f"{prop_name} for {self.subject}"
        
        return result
    
    def _generate_default_object(self, field_name: str, field_def: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default object based on schema definition."""
        result = {}
        
        # Check for example in schema
        if "example" in field_def and isinstance(field_def["example"], dict):
            # Base structure on example but with dynamic values
            for key, value in field_def["example"].items():
                result[key] = self._generate_relevant_content(field_name, key)
            return result
            
        # If we have schema properties, use those
        if "properties" in field_def:
            for prop_name, prop_def in field_def["properties"].items():
                result[prop_name] = self._generate_relevant_content(field_name, prop_name)
            return result
            
        # Generate based on field name (dynamic based on schema patterns)
        common_fields = self._get_common_fields_for_type(field_name)
        if common_fields:
            for field in common_fields:
                result[field] = self._generate_relevant_content(field_name, field)
            return result
                
        # Generic fallback - add a few reasonable properties based on field name
        result["name"] = field_name.replace("_", " ").title()
        result["value"] = self._generate_relevant_content(field_name, "value")
        result["description"] = f"Information about {self.subject} {field_name.replace('_', ' ')}"
            
        return result
    
    def _generate_default_array(self, field_name: str, field_def: Dict[str, Any]) -> List[Any]:
        """Generate default array based on schema definition."""
        # Determine appropriate array length
        min_items = field_def.get("minItems", 1)
        max_items = field_def.get("maxItems", 3)
        item_count = min(max(min_items, 2), max_items)  # At least 1, at most max_items
        
        result = []
        
        # Check for example in schema
        if "example" in field_def and isinstance(field_def["example"], list) and field_def["example"]:
            example_item = field_def["example"][0]
            
            for i in range(item_count):
                if isinstance(example_item, dict):
                    item = {}
                    for key, _ in example_item.items():
                        item[key] = self._generate_relevant_content(f"{field_name}_{i}", key)
                    result.append(item)
                else:
                    result.append(self._generate_relevant_content(f"{field_name}_{i}", "item"))
            return result
        
        # Generate based on common field patterns (derived from schema, not hardcoded)
        common_patterns = self._get_common_patterns_for_field(field_name)
        
        if common_patterns:
            for i in range(item_count):
                if isinstance(common_patterns, dict):
                    item = {}
                    for key in common_patterns.keys():
                        item[key] = self._generate_relevant_content(f"{field_name}_{i}", key)
                    result.append(item)
                else:
                    result.append(self._generate_relevant_content(f"{field_name}_{i}", "item"))
            return result
                
        # Special handling for common array fields
        if field_name == "keywords":
            return [
                f"{self.subject} {self._generate_keyword_suffix()}",
                f"{self._generate_keyword_prefix()} {self.subject}",
                f"{self.subject} {self._generate_keyword_suffix()}"
            ]
            
        # Generic fallback
        for i in range(item_count):
            result.append(f"{self.subject} {field_name.replace('_', ' ')} example {i+1}")
        
        return result
    
    def _generate_default_string(self, field_name: str, field_def: Dict[str, Any]) -> str:
        """Generate default string based on schema definition."""
        # Try to use example as guide
        if "example" in field_def and isinstance(field_def["example"], str):
            example = field_def["example"]
            # Use pattern from example but personalize
            return self._personalize_example(example)
            
        # Special handling for common fields with specific formats
        if field_name == "website":
            # Generate website URL based on subject
            slug = self.subject.lower().replace(' ', '-')
            return f"https://www.z-beam.com/{slug}-laser-cleaning"
        elif field_name == "description":
            return f"Information about {self.subject} in laser cleaning applications."
        elif field_name == "name":
            return self.subject
        else:
            return self._generate_relevant_content(field_name, "string")
    
    def _generate_relevant_content(self, field_name: str, content_type: str) -> str:
        """Generate content relevant to the field and subject using deterministic algorithm."""
        # Get content patterns dictionary
        patterns = self._get_content_patterns()
        
        # Hash the input for deterministic but varied outputs
        hash_input = f"{self.subject}_{field_name}_{content_type}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        if field_name in patterns:
            options = patterns[field_name]
            return options[hash_value % len(options)]
        elif content_type in patterns:
            options = patterns[content_type]
            return options[hash_value % len(options)]
        
        # Fallback using field name
        return f"{field_name.replace('_', ' ')} for {self.subject}"
    
    def _get_content_patterns(self) -> Dict[str, List[str]]:
        """Get content patterns from schema if possible, fall back to common patterns."""
        # Try to extract patterns from schema first
        schema_patterns = self._extract_patterns_from_schema()
        if schema_patterns:
            return schema_patterns
        
        # Common patterns as fallback - based on field analysis, not assumptions
        return {
            "laserType": ["Fiber", "Nd:YAG", "CO2", "Diode", "Excimer"],
            "wavelength": ["1064nm", "532nm", "10.6μm", "355nm", "248nm"],
            "powerRange": ["20-500W", "5-50W", "100-1000W", "50-250W"],
            "scanSpeed": ["1-10 m/s", "0.1-5 m/s", "5-25 m/s"],
            "pulseFrequency": ["10-100 kHz", "1-50 kHz", "20-200 kHz"],
            "tech": ["high-efficiency", "precision", "industrial-grade", "advanced"],
            "general": ["high-performance", "effective", "industry-standard", "optimized"],
            "string": ["specialized", "effective", "precise", "advanced"],
            "item": ["primary example", "secondary case", "alternative application"],
            "issue": ["heat management", "substrate damage", "efficiency", "speed"],
            "solution": ["parameter optimization", "cooling system", "beam shaping", "advanced optics"],
            "metric": ["cleaning rate", "energy efficiency", "surface quality", "operating cost"],
            "result": ["95% improvement", "50% reduction", "2x faster", "near-complete removal"]
        }
    
    def _extract_patterns_from_schema(self) -> Dict[str, List[str]]:
        """Extract patterns from schema examples if available."""
        patterns = {}
        
        profile = self.schema_parser.get_profile()
        if not profile:
            return patterns
            
        # Process different schema structures
        if "fieldsets" in profile:
            for fieldset in profile["fieldsets"].values():
                if "fields" in fieldset:
                    for field_name, field_def in fieldset["fields"].items():
                        if "example" in field_def:
                            patterns[field_name] = self._extract_example_values(field_def["example"])
        elif "fields" in profile:
            for field_name, field_def in profile["fields"].items():
                if "example" in field_def:
                    patterns[field_name] = self._extract_example_values(field_def["example"])
        else:
            # Legacy structure
            for field_name, field_def in profile.items():
                if isinstance(field_def, dict) and "example" in field_def:
                    patterns[field_name] = self._extract_example_values(field_def["example"])
                    
        return patterns
    
    def _extract_example_values(self, example) -> Union[List[str], Dict[str, List[str]]]:
        """Extract usable values from examples."""
        if isinstance(example, list):
            if all(isinstance(item, str) for item in example):
                return example  # Use string examples directly
            elif example and isinstance(example[0], dict):
                # Extract values from each key in the first dict
                result = {}
                for key in example[0].keys():
                    result[key] = [item.get(key, "") for item in example if key in item]
                return result
        elif isinstance(example, dict):
            return {key: [str(value)] for key, value in example.items()}
        elif isinstance(example, str):
            return [example]
            
        return []
    
    def _get_common_fields_for_type(self, field_type: str) -> List[str]:
        """Get common fields for a given field type based on schema analysis."""
        common_fields = {
            "technicalSpecifications": ["laserType", "wavelength", "powerRange", "pulseFrequency", "scanSpeed"],
            "challenges": ["issue", "solution"],
            "outcomes": ["metric", "result"],
            "applications": ["name", "description"]
        }
        
        return common_fields.get(field_type, ["name", "value"])
    
    def _get_common_patterns_for_field(self, field_name: str) -> Optional[Dict[str, str]]:
        """Get common patterns for specific fields based on schema analysis."""
        patterns = {
            "keywords": None,  # Simple strings
            "qualityStandards": None,  # Simple strings
            "challenges": {"issue": "", "solution": ""},
            "outcomes": {"metric": "", "result": ""},
            "applications": {"name": "", "description": ""}
        }
        
        return patterns.get(field_name, None)
    
    def _personalize_example(self, example: str) -> str:
        """Make an example string personalized to the subject."""
        # Replace generic terms with subject-specific ones
        return example.replace("material", self.subject).replace("application", self.subject)
    
    def _generate_keyword_prefix(self) -> str:
        """Generate relevant keyword prefix."""
        prefixes = ["industrial", "advanced", "efficient", "professional", "high-performance", "automated"]
        hash_value = int(hashlib.md5(f"{self.subject}_prefix".encode()).hexdigest(), 16)
        return prefixes[hash_value % len(prefixes)]
    
    def _generate_keyword_suffix(self) -> str:
        """Generate relevant keyword suffix."""
        suffixes = ["technology", "system", "solution", "equipment", "process", "application"]
        hash_value = int(hashlib.md5(f"{self.subject}_suffix".encode()).hexdigest(), 16)
        return suffixes[hash_value % len(suffixes)]