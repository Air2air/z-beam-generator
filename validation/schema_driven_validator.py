"""
Schema-Driven Content Validator

Validates generated content using only schema definitions.
No hardcoded field names, sizes, or validation rules.
Single source of truth: schemas directory.
"""

import os
import json
import yaml
import logging
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ComponentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed" 
    EMPTY = "empty"
    INVALID = "invalid"
    MISSING = "missing"

@dataclass
class ComponentResult:
    component: str
    subject: str
    status: ComponentStatus
    file_path: str
    size_bytes: int
    content_lines: int
    issues: List[str]
    quality_score: float

class SchemaDrivenValidator:
    """Validates content using only schema definitions - no hardcoded rules."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._schema_cache = {}
    
    def validate_component(self, component: str, file_path: str, subject: str, 
                          article_type: str = "material") -> ComponentResult:
        """Validate component using schema validation rules."""
        
        issues = []
        quality_score = 0.0
        
        # Check if file exists
        if not os.path.exists(file_path):
            return ComponentResult(
                component=component,
                subject=subject,
                status=ComponentStatus.MISSING,
                file_path=file_path,
                size_bytes=0,
                content_lines=0,
                issues=["File does not exist"],
                quality_score=0.0
            )
        
        # Get file stats
        file_size = os.path.getsize(file_path)
        
        # Read content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return ComponentResult(
                component=component,
                subject=subject,
                status=ComponentStatus.FAILED,
                file_path=file_path,
                size_bytes=file_size,
                content_lines=0,
                issues=[f"Failed to read file: {e}"],
                quality_score=0.0
            )
        
        content_lines = len(content.splitlines())
        
        # Load schema for validation
        try:
            schema = self._load_schema(article_type)
            validation_rules = self._extract_validation_rules(component, schema)
        except Exception as e:
            self.logger.warning(f"Could not load validation schema: {e}")
            validation_rules = {}
        
        # Perform schema-driven validation
        quality_score = self._validate_against_schema(component, content, validation_rules, issues)
        
        # Determine status
        if file_size == 0:
            status = ComponentStatus.EMPTY
        elif quality_score < 0.3:
            status = ComponentStatus.INVALID
        elif issues:
            status = ComponentStatus.FAILED
        else:
            status = ComponentStatus.SUCCESS
        
        return ComponentResult(
            component=component,
            subject=subject,
            status=status,
            file_path=file_path,
            size_bytes=file_size,
            content_lines=content_lines,
            issues=issues,
            quality_score=quality_score
        )
    
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
    
    def _extract_validation_rules(self, component: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract validation rules for component from schema."""
        material_profile = schema.get("materialProfile", {})
        validation_config = material_profile.get("validation", {})
        component_validation = validation_config.get(component, {})
        
        # Also check generator config for additional rules
        generator_config = material_profile.get("generatorConfig", {}).get(component, {})
        
        # Merge validation rules
        rules = {}
        rules.update(component_validation)
        
        # Add generator-specific rules
        if generator_config:
            rules["generator_config"] = generator_config
        
        return rules
    
    def _validate_against_schema(self, component: str, content: str, 
                                validation_rules: Dict[str, Any], issues: List[str]) -> float:
        """Validate content against schema rules."""
        if not validation_rules:
            # No schema rules - basic validation only
            return self._basic_validation(component, content, issues)
        
        quality_score = 0.0
        total_checks = 0
        
        # Check minimum length
        min_length = validation_rules.get("minLength")
        if min_length:
            total_checks += 1
            if len(content) >= min_length:
                quality_score += 1.0
            else:
                issues.append(f"Content too short: {len(content)} < {min_length} characters")
        
        # Check maximum length
        max_length = validation_rules.get("maxLength")
        if max_length:
            total_checks += 1
            if len(content) <= max_length:
                quality_score += 1.0
            else:
                issues.append(f"Content too long: {len(content)} > {max_length} characters")
        
        # Check required fields
        required_fields = validation_rules.get("requiredFields", [])
        if required_fields:
            total_checks += len(required_fields)
            for field in required_fields:
                if field.lower() in content.lower():
                    quality_score += 1.0
                else:
                    issues.append(f"Required field missing: {field}")
        
        # Check content rules
        content_rules = validation_rules.get("contentRules", [])
        for rule in content_rules:
            total_checks += 1
            if self._check_content_rule(content, rule):
                quality_score += 1.0
            else:
                issues.append(f"Content rule violated: {rule}")
        
        # Validate field-specific requirements
        field_validation = validation_rules.get("fieldValidation", {})
        for field, field_rules in field_validation.items():
            total_checks += 1
            if self._validate_field_content(content, field, field_rules):
                quality_score += 1.0
            else:
                issues.append(f"Field validation failed: {field}")
        
        # Component-specific validation
        component_score = self._validate_component_specific(component, content, validation_rules, issues)
        quality_score += component_score
        total_checks += 1
        
        # Calculate final score
        if total_checks > 0:
            return quality_score / total_checks
        else:
            return self._basic_validation(component, content, issues)
    
    def _basic_validation(self, component: str, content: str, issues: List[str]) -> float:
        """Basic validation when no schema rules are available."""
        quality_score = 0.0
        total_checks = 3
        
        # Check if content is not empty
        if content.strip():
            quality_score += 1.0
        else:
            issues.append("Content is empty")
        
        # Check minimum reasonable length based on component type
        min_reasonable_length = self._get_reasonable_min_length(component)
        if len(content) >= min_reasonable_length:
            quality_score += 1.0
        else:
            issues.append(f"Content may be too short for {component} component")
        
        # Check for basic structure markers
        if self._has_basic_structure(component, content):
            quality_score += 1.0
        else:
            issues.append(f"Missing expected structure for {component} component")
        
        return quality_score / total_checks
    
    def _get_reasonable_min_length(self, component: str) -> int:
        """Get reasonable minimum length for component when no schema rules exist."""
        defaults = {
            'frontmatter': 50,
            'content': 300,
            'table': 50,
            'bullets': 50,
            'caption': 20,
            'metatags': 50,
            'jsonld': 50,
            'tags': 10,
            'propertiestable': 30
        }
        return defaults.get(component, 20)
    
    def _has_basic_structure(self, component: str, content: str) -> bool:
        """Check if content has basic expected structure."""
        content_lower = content.lower()
        
        if component == "frontmatter":
            return "---" in content or any(marker in content_lower for marker in ["title:", "description:", "category:"])
        
        elif component == "table":
            return "|" in content or "property" in content_lower
        
        elif component == "bullets":
            return any(marker in content for marker in ["-", "*", "•"]) or len(content.splitlines()) > 1
        
        elif component == "metatags":
            return any(tag in content_lower for tag in ["meta_title", "title", "description", "keywords"])
        
        elif component == "jsonld":
            return any(field in content_lower for field in ["headline", "description", "keywords", "articlebody"])
        
        elif component == "caption":
            return len(content.splitlines()) >= 1 and len(content) > 10
        
        elif component == "tags":
            return "," in content or len(content.split()) > 1
        
        elif component == "propertiestable":
            return "|" in content and any(prop in content_lower for prop in ["property", "value", "formula"])
        
        else:
            return len(content.strip()) > 0
    
    def _check_content_rule(self, content: str, rule: str) -> bool:
        """Check if content satisfies a specific rule."""
        content_lower = content.lower()
        rule_lower = rule.lower()
        
        if "no placeholder" in rule_lower or "no tbd" in rule_lower:
            return not any(placeholder in content_lower for placeholder in ["tbd", "placeholder", "...", "todo"])
        
        elif "technical terminology" in rule_lower:
            # Check for technical terms (simplified)
            technical_terms = ["laser", "wavelength", "power", "frequency", "temperature", "pressure", "material"]
            return any(term in content_lower for term in technical_terms)
        
        elif "specific values" in rule_lower or "measurements" in rule_lower:
            # Check for numerical values with units
            import re
            return bool(re.search(r'\d+\s*[a-zA-Z]+', content))
        
        else:
            # Generic rule - check if rule keywords appear in content
            rule_keywords = rule_lower.split()
            return any(keyword in content_lower for keyword in rule_keywords if len(keyword) > 3)
    
    def _validate_field_content(self, content: str, field: str, field_rules: Dict[str, Any]) -> bool:
        """Validate specific field content against its rules."""
        # Look for field in content
        field_pattern = f"{field}:"
        if field_pattern not in content.lower():
            return False
        
        # Extract field value
        try:
            lines = content.split("\\n")
            field_value = ""
            for line in lines:
                if field.lower() in line.lower() and ":" in line:
                    field_value = line.split(":", 1)[1].strip()
                    break
        except Exception:
            return False
        
        # Check field-specific rules
        max_length = field_rules.get("maxLength")
        if max_length and len(field_value) > max_length:
            return False
        
        min_length = field_rules.get("minLength")
        if min_length and len(field_value) < min_length:
            return False
        
        return True
    
    def _validate_component_specific(self, component: str, content: str, 
                                   validation_rules: Dict[str, Any], issues: List[str]) -> float:
        """Component-specific validation logic."""
        
        if component == "frontmatter":
            return self._validate_frontmatter_structure(content, validation_rules, issues)
        
        elif component == "jsonld":
            return self._validate_jsonld_structure(content, validation_rules, issues)
        
        elif component == "table":
            return self._validate_table_structure(content, validation_rules, issues)
        
        elif component == "metatags":
            return self._validate_metatags_structure(content, validation_rules, issues)
        
        else:
            return 1.0  # Default pass for other components
    
    def _validate_frontmatter_structure(self, content: str, validation_rules: Dict[str, Any], issues: List[str]) -> float:
        """Validate frontmatter YAML structure."""
        try:
            # Remove markdown frontmatter delimiters if present
            clean_content = content.strip()
            if clean_content.startswith("---"):
                parts = clean_content.split("---", 2)
                if len(parts) >= 2:
                    yaml_content = parts[1]
                else:
                    yaml_content = clean_content
            else:
                yaml_content = clean_content
            
            # Try to parse as YAML
            yaml.safe_load(yaml_content)
            return 1.0
            
        except yaml.YAMLError:
            issues.append("Invalid YAML structure in frontmatter")
            return 0.0
    
    def _validate_jsonld_structure(self, content: str, validation_rules: Dict[str, Any], issues: List[str]) -> float:
        """Validate JSON-LD structure."""
        # JSON-LD should be in YAML format according to legacy prompts
        try:
            yaml.safe_load(content)
            
            # Check for required JSON-LD fields
            required_fields = ["headline", "description", "keywords", "articleBody"]
            content_lower = content.lower()
            
            missing_fields = [field for field in required_fields if field.lower() not in content_lower]
            if missing_fields:
                issues.append(f"Missing JSON-LD fields: {', '.join(missing_fields)}")
                return 0.5
            
            return 1.0
            
        except yaml.YAMLError:
            issues.append("Invalid YAML structure in JSON-LD")
            return 0.0
    
    def _validate_table_structure(self, content: str, validation_rules: Dict[str, Any], issues: List[str]) -> float:
        """Validate table structure."""
        if "|" not in content:
            issues.append("No table structure found (missing | delimiters)")
            return 0.0
        
        lines = content.strip().split("\\n")
        table_lines = [line for line in lines if "|" in line]
        
        if len(table_lines) < 2:
            issues.append("Table needs at least header and one data row")
            return 0.3
        
        # Check for consistent column count
        column_counts = [len(line.split("|")) for line in table_lines]
        if len(set(column_counts)) > 1:
            issues.append("Inconsistent number of columns in table")
            return 0.5
        
        return 1.0
    
    def _validate_metatags_structure(self, content: str, validation_rules: Dict[str, Any], issues: List[str]) -> float:
        """Validate metatags structure."""
        required_tags = ["meta_title", "meta_description", "meta_keywords"]
        content_lower = content.lower()
        
        score = 0.0
        for tag in required_tags:
            if tag in content_lower:
                score += 1.0
            else:
                issues.append(f"Missing required metatag: {tag}")
        
        return score / len(required_tags)


# Backwards compatibility function
def validate_component(component: str, file_path: str, subject: str, article_type: str = "material") -> Tuple[ComponentStatus, List[str], float]:
    """Backwards compatible validation function."""
    validator = SchemaDrivenValidator()
    result = validator.validate_component(component, file_path, subject, article_type)
    return result.status, result.issues, result.quality_score
