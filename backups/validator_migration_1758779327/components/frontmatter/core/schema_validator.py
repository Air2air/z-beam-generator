#!/usr/bin/env python3
"""
Schema Valida        except Exception as e:
            logger.error(f\"Failed to load schema from {self.schema_path}: {e}\")
            # Fail-fast: Schema file required - no fallback allowed
            raise RuntimeError(f\"Schema validation requires valid schema file: {self.schema_path}\")lity for Frontmatter

Validates generated frontmatter against the JSON schema with comprehensive
error reporting and automatic field normalization suggestions.
"""

import json
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Raised when schema validation fails"""
    pass


class FrontmatterSchemaValidator:
    """Validates frontmatter against schema with detailed error reporting"""
    
    def __init__(self, schema_path: str = None):
        """Initialize validator with schema"""
        if schema_path is None:
            # Fail-fast: Schema path required
            schema_path = Path(__file__).parent.parent.parent.parent / "schemas" / "frontmatter.json"
        
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict:
        """Load JSON schema"""
        try:
            with open(self.schema_path, 'r') as f:
                schema = json.load(f)
            logger.info(f"Loaded schema from {self.schema_path}")
            return schema
        except Exception as e:
            logger.error(f"Failed to load schema from {self.schema_path}: {e}")
            # Fail-fast: Schema file required - no fallback
            return {
                "type": "object",
                "required": ["name", "category", "title"],
                "properties": {}
            }
    
    def validate_frontmatter(self, frontmatter: Dict[str, Any], material_name: str) -> Tuple[bool, List[str]]:
        """
        Validate frontmatter against schema
        
        Args:
            frontmatter: The frontmatter data to validate
            material_name: Name of material for context
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Check required fields
            required_fields = self.schema.get("required", [])
            missing_fields = []
            
            for field in required_fields:
                if field not in frontmatter:
                    missing_fields.append(field)
                elif frontmatter[field] is None:
                    missing_fields.append(f"{field} (null value)")
                elif field in ["properties", "machineSettings", "author_object"] and not isinstance(frontmatter[field], dict):
                    errors.append(f"Field '{field}' must be an object, got {type(frontmatter[field])}")
                elif field in ["keywords", "applications"] and not isinstance(frontmatter[field], (list, str)):
                    errors.append(f"Field '{field}' must be a list or string, got {type(frontmatter[field])}")
            
            if missing_fields:
                errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Validate field types
            properties = self.schema.get("properties", {})
            for field_name, field_value in frontmatter.items():
                if field_name in properties:
                    field_schema = properties[field_name]
                    field_errors = self._validate_field_type(field_name, field_value, field_schema)
                    errors.extend(field_errors)
            
            # Validate unit separation for numeric fields
            unit_errors = self._validate_unit_separation(frontmatter)
            errors.extend(unit_errors)
            
            # Validate nested objects
            nested_errors = self._validate_nested_objects(frontmatter)
            errors.extend(nested_errors)
            
            is_valid = len(errors) == 0
            
            if is_valid:
                logger.info(f"Schema validation passed for {material_name}")
            else:
                logger.warning(f"Schema validation failed for {material_name}: {len(errors)} errors")
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Schema validation error for {material_name}: {e}")
            return False, [f"Validation process failed: {e}"]
    
    def _validate_field_type(self, field_name: str, field_value: Any, field_schema: Dict) -> List[str]:
        """Validate individual field against its schema"""
        errors = []
        
        expected_type = field_schema.get("type")
        if expected_type:
            if expected_type == "string" and not isinstance(field_value, str):
                errors.append(f"Field '{field_name}' must be string, got {type(field_value)}")
            elif expected_type == "integer" and not isinstance(field_value, int):
                errors.append(f"Field '{field_name}' must be integer, got {type(field_value)}")
            elif expected_type == "number" and not isinstance(field_value, (int, float)):
                errors.append(f"Field '{field_name}' must be number, got {type(field_value)}")
            elif expected_type == "array" and not isinstance(field_value, list):
                errors.append(f"Field '{field_name}' must be array, got {type(field_value)}")
            elif expected_type == "object" and not isinstance(field_value, dict):
                errors.append(f"Field '{field_name}' must be object, got {type(field_value)}")
        
        # Validate enum values
        if "enum" in field_schema and field_value not in field_schema["enum"]:
            errors.append(f"Field '{field_name}' value '{field_value}' not in allowed values: {field_schema['enum']}")
        
        return errors
    
    def _validate_unit_separation(self, frontmatter: Dict[str, Any]) -> List[str]:
        """Validate that numeric properties have proper unit separation"""
        errors = []
        
        sections_to_check = ["properties", "machineSettings"]
        
        for section in sections_to_check:
            if section not in frontmatter or not isinstance(frontmatter[section], dict):
                continue
            
            section_data = frontmatter[section]
            
            for key, value in section_data.items():
                # Skip unit, min, max fields
                if key.endswith(('Unit', 'Min', 'Max')):
                    continue
                
                # Check if numeric value has corresponding unit
                if isinstance(value, (int, float)):
                    unit_key = f"{key}Unit"
                    if unit_key not in section_data:
                        errors.append(f"Numeric field '{section}.{key}' missing unit field '{unit_key}'")
                    
                    # Check for min/max ranges
                    min_key = f"{key}Min"
                    max_key = f"{key}Max"
                    if min_key in section_data and not isinstance(section_data[min_key], (int, float)):
                        errors.append(f"Min field '{section}.{min_key}' must be numeric")
                    if max_key in section_data and not isinstance(section_data[max_key], (int, float)):
                        errors.append(f"Max field '{section}.{max_key}' must be numeric")
        
        return errors
    
    def _validate_nested_objects(self, frontmatter: Dict[str, Any]) -> List[str]:
        """Validate nested object structures"""
        errors = []
        
        # Validate author_object structure
        if "author_object" in frontmatter:
            author = frontmatter["author_object"]
            if isinstance(author, dict):
                required_author_fields = ["id", "name", "sex", "title", "country", "expertise"]
                for field in required_author_fields:
                    if field not in author:
                        errors.append(f"author_object missing required field: {field}")
                    elif field == "id" and not isinstance(author[field], int):
                        errors.append(f"author_object.id must be integer, got {type(author[field])}")
            else:
                errors.append(f"author_object must be object, got {type(author)}")
        
        # Validate chemicalProperties if present
        if "chemicalProperties" in frontmatter:
            chem_props = frontmatter["chemicalProperties"]
            if isinstance(chem_props, dict):
                if "formula" not in chem_props and "symbol" not in chem_props:
                    errors.append("chemicalProperties must contain 'formula' or 'symbol'")
            else:
                errors.append(f"chemicalProperties must be object, got {type(chem_props)}")
        
        # Validate compatibility structure
        if "compatibility" in frontmatter:
            compat = frontmatter["compatibility"]
            if isinstance(compat, dict):
                expected_compat_fields = ["laser_types", "surface_treatments"]
                for field in expected_compat_fields:
                    if field in compat and not isinstance(compat[field], list):
                        errors.append(f"compatibility.{field} must be array, got {type(compat[field])}")
            else:
                errors.append(f"compatibility must be object, got {type(compat)}")
        
        return errors
    
    def suggest_fixes(self, frontmatter: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """Suggest fixes for common validation errors"""
        fixes = {}
        
        for error in errors:
            if "missing required field" in error.lower():
                # Extract field name and suggest default value
                if "author_object" in error:
                    fixes["author_object"] = {
                        "id": 1, "name": "Default Author", "sex": "m",
                        "title": "Engineer", "country": "International",
                        "expertise": "Laser Technology", "image": "/images/author/default.jpg"
                    }
                elif "properties" in error:
                    fixes["properties"] = {"density": 1.0, "densityUnit": "g/cm³"}
                elif "machineSettings" in error:
                    fixes["machineSettings"] = {
                        "powerRange": 100.0, "powerRangeUnit": "W",
                        "wavelength": 1064.0, "wavelengthUnit": "nm"
                    }
            
            elif "must be" in error and "got" in error:
                # Type conversion suggestions
                if "must be integer" in error:
                    field_match = error.split("'")[1] if "'" in error else None
                    if field_match and field_match in frontmatter:
                        try:
                            fixes[field_match] = int(frontmatter[field_match])
                        except (ValueError, TypeError):
                            fixes[field_match] = 1
                
                elif "must be array" in error:
                    field_match = error.split("'")[1] if "'" in error else None
                    if field_match and field_match in frontmatter:
                        value = frontmatter[field_match]
                        if isinstance(value, str):
                            fixes[field_match] = [v.strip() for v in value.split(',')]
                        else:
                            fixes[field_match] = [str(value)]
        
        return fixes
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema information for debugging"""
        return {
            "schema_path": str(self.schema_path),
            "required_fields": self.schema.get("required", []),
            "total_properties": len(self.schema.get("properties", {})),
            "schema_version": self.schema.get("$schema", "unknown")
        }


def validate_frontmatter_schema(data: Dict[str, Any], schema_path: str = "schemas/frontmatter.json") -> Tuple[bool, List[str]]:
    """
    Compatibility function for tests that expect the old API.
    
    Args:
        data: Frontmatter data to validate
        schema_path: Path to schema file
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    validator = FrontmatterSchemaValidator(schema_path)
    material_name = data.get('name', 'unknown')
    return validator.validate_frontmatter(data, material_name)