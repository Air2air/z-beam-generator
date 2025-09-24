#!/usr/bin/env python3
"""
Basic Frontmatter Schema Validator
"""

import json
from pathlib import Path
from typing import Dict, List, NamedTuple

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class ValidationResult(NamedTuple):
    """Result of schema validation"""
    valid: bool
    errors: List[str]
    error_count: int = 0
    
    @property
    def has_errors(self):
        return len(self.errors) > 0


class FrontmatterSchemaValidator:
    """Basic schema validator for frontmatter data"""
    
    def __init__(self, schema_path: str = "schemas/frontmatter.json"):
        self.schema_path = schema_path
        self.schema = None
        self._load_schema()
    
    def _load_schema(self):
        try:
            schema_file = Path(self.schema_path)
            if schema_file.exists():
                with open(schema_file, 'r') as f:
                    self.schema = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load schema from {self.schema_path}: {e}")
    
    def get_schema_info(self) -> Dict:
        if self.schema:
            return {
                "status": "loaded",
                "title": self.schema.get("title", "Unknown")
            }
        else:
            return {"status": "not_loaded"}
    
    def validate_frontmatter(self, data: Dict) -> ValidationResult:
        if not JSONSCHEMA_AVAILABLE:
            return ValidationResult(
                valid=False,
                errors=["jsonschema library not available"],
                error_count=1
            )
        
        if not self.schema:
            return ValidationResult(
                valid=False, 
                errors=["Schema not loaded"],
                error_count=1
            )
        
        try:
            jsonschema.validate(data, self.schema)
            return ValidationResult(valid=True, errors=[], error_count=0)
        except jsonschema.ValidationError as e:
            return ValidationResult(
                valid=False,
                errors=[str(e.message)],
                error_count=1
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"],
                error_count=1
            )
    
    def validate_and_log(self, data: Dict, material_name: str) -> bool:
        result = self.validate_frontmatter(data)
        if not result.valid:
            print(f"Validation failed for {material_name}:")
            for error in result.errors:
                print(f"  - {error}")
        return result.valid


def validate_frontmatter_schema(data: Dict, schema_path: str = "schemas/frontmatter.json") -> ValidationResult:
    validator = FrontmatterSchemaValidator(schema_path)
    return validator.validate_frontmatter(data)


def validate_frontmatter_and_log(data: Dict, material_name: str) -> bool:
    validator = FrontmatterSchemaValidator()
    return validator.validate_and_log(data, material_name)
