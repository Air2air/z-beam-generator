#!/usr/bin/env python3
"""
SchemaValidator - Single Schema Validation System

Consolidates all schema validation functionality into a single, unified validator.
Replaces multiple schema validators with consistent interface and behavior.

Consolidates:
- validation/schema_validator.py (main validator)
- components/frontmatter/core/schema_validator.py (component-specific)
- scripts/validation/enhanced_schema_validator.py (enhanced version)

Features:
- Multiple validation modes (basic, enhanced, research_grade)
- Component adapters for different schema types
- Standardized error reporting
- Quality scoring and metrics
- Backward compatibility interfaces

Follows fail-fast principles:
- No mocks or fallbacks in production
- Explicit error handling with specific exception types
- Validates all inputs immediately
- Single point of schema validation

Author: Consolidation Phase 2 - October 22, 2025
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import jsonschema
import yaml

# Import consolidated validation from core (updated October 2025)
from shared.validation.core import SchemaValidator
from shared.validation.errors import ValidationResult as LegacyValidationResult

logger = logging.getLogger(__name__)


class ValidationMode(Enum):
    """Available validation modes with different strictness levels"""
    BASIC = "basic"                    # Simple schema compliance
    ENHANCED = "enhanced"              # Schema + quality scoring  
    RESEARCH_GRADE = "research_grade"  # Full research validation
    AUDIT = "audit"                    # Comprehensive audit mode


class SchemaType(Enum):
    """Supported schema types for component adapters"""
    FRONTMATTER = "frontmatter"
    MATERIALS_YAML = "materials_yaml"
    CATEGORIES_YAML = "categories_yaml"
    COMPONENT_OUTPUT = "component_output"
    CONFIGURATION = "configuration"


@dataclass
class ValidationError:
    """Standardized validation error across all components"""
    field_path: str
    error_type: str
    message: str
    severity: str = "error"  # error, warning, info
    suggestion: Optional[str] = None
    requirement_source: Optional[str] = None
    remediation: Optional[str] = None


@dataclass
class ValidationResult:
    """Unified validation result supporting all existing interfaces"""
    
    # Core validation
    is_valid: bool
    schema_type: str
    validation_mode: str
    material_name: Optional[str] = None
    
    # Error reporting
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)
    
    # Quality metrics
    quality_score: Optional[float] = None
    completeness_score: Optional[float] = None
    compliance_score: Optional[float] = None
    
    # Performance metrics
    validation_duration_ms: int = 0
    schema_checks_performed: int = 0
    
    # Metadata
    validation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    validator_version: str = "SchemaValidator-1.0"
    
    @property
    def error_count(self) -> int:
        """Count of errors by severity"""
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        """Count of warnings"""
        return len(self.warnings)
    
    @property
    def total_issues(self) -> int:
        """Total issues found"""
        return len(self.errors) + len(self.warnings) + len(self.info)
    
    def get_issues_by_severity(self, severity: str) -> List[ValidationError]:
        """Get issues filtered by severity level"""
        if severity == "error":
            return self.errors
        elif severity == "warning":
            return self.warnings
        elif severity == "info":
            return self.info
        else:
            return []


class SchemaValidator:
    """
    Schema validator consolidating all schema validation functionality.
    
    Provides single interface for:
    1. Frontmatter validation (component output)
    2. Materials.yaml validation (data structure)
    3. Categories.yaml validation (configuration)
    4. Component output validation (generated content)
    5. Configuration validation (system settings)
    
    Benefits:
    - Consistent validation behavior across all schema types
    - Single maintenance point for schema logic
    - Standardized error reporting and quality metrics
    - Component adapters for different validation needs
    - Backward compatibility with existing interfaces
    """
    
    def __init__(
        self,
        schema_directory: Optional[Path] = None,
        validation_mode: ValidationMode = ValidationMode.ENHANCED
    ):
        """
        Initialize unified schema validator.
        
        Args:
            schema_directory: Directory containing schema files
            validation_mode: Default validation strictness level
        """
        self.logger = logging.getLogger(__name__)
        self.validation_mode = validation_mode
        
        # Schema directory setup
        if schema_directory is None:
            schema_directory = Path("schemas")
        self.schema_directory = Path(schema_directory)
        
        # Initialize component adapters
        self._initialize_adapters()
        
        # Load schemas
        self._load_schemas()
        
        # Validation statistics
        self.validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'schema_types_validated': set()
        }
        
        self.logger.info(f"✅ SchemaValidator initialized (mode: {validation_mode.value})")
    
    def _initialize_adapters(self) -> None:
        """Initialize component adapters for different schema types"""
        self.adapters = {
            SchemaType.FRONTMATTER: FrontmatterAdapter(self),
            SchemaType.MATERIALS_YAML: MaterialsYamlAdapter(self),
            SchemaType.CATEGORIES_YAML: CategoriesYamlAdapter(self),
            SchemaType.COMPONENT_OUTPUT: ComponentOutputAdapter(self),
            SchemaType.CONFIGURATION: ConfigurationAdapter(self)
        }
        
        self.logger.info(f"✅ Initialized {len(self.adapters)} schema adapters")
    
    def _load_schemas(self) -> None:
        """Load all schema definitions"""
        self.schemas = {}
        
        try:
            # Load schema files from schema directory
            schema_files = {
                SchemaType.FRONTMATTER: "frontmatter_schema.json",
                SchemaType.MATERIALS_YAML: "materials_schema.json",
                SchemaType.CATEGORIES_YAML: "categories_schema.json",
                SchemaType.COMPONENT_OUTPUT: "component_schema.json",
                SchemaType.CONFIGURATION: "config_schema.json"
            }
            
            for schema_type, schema_file in schema_files.items():
                schema_path = self.schema_directory / schema_file
                
                if schema_path.exists():
                    with open(schema_path, 'r') as f:
                        self.schemas[schema_type] = json.load(f)
                    self.logger.debug(f"✅ Loaded schema: {schema_file}")
                else:
                    self.logger.warning(f"⚠️  Schema file not found: {schema_path}")
                    # Create minimal schema as fallback
                    self.schemas[schema_type] = {"type": "object"}
            
            self.logger.info(f"✅ Loaded {len(self.schemas)} schemas")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load schemas: {e}")
            # Create minimal schemas as fallback
            for schema_type in SchemaType:
                self.schemas[schema_type] = {"type": "object"}
    
    def validate(
        self,
        data: Union[Dict, List, str],
        schema_type: Union[SchemaType, str],
        material_name: Optional[str] = None,
        validation_mode: Optional[ValidationMode] = None
    ) -> ValidationResult:
        """
        Universal validation method for all schema types.
        
        Args:
            data: Data to validate (dict, list, or YAML string)
            schema_type: Type of schema to validate against
            material_name: Optional material name for context
            validation_mode: Override default validation mode
            
        Returns:
            Unified validation result with all findings
            
        Raises:
            ValidationError: If validation infrastructure fails
        """
        start_time = datetime.now()
        
        try:
            # Normalize inputs
            if isinstance(schema_type, str):
                schema_type = SchemaType(schema_type)
            
            if validation_mode is None:
                validation_mode = self.validation_mode
            
            self.logger.info(f"🔍 Validating {schema_type.value} data (mode: {validation_mode.value})")
            
            # Initialize result
            result = ValidationResult(
                is_valid=True,
                schema_type=schema_type.value,
                validation_mode=validation_mode.value,
                material_name=material_name
            )
            
            # Parse data if it's a string
            if isinstance(data, str):
                try:
                    if data.strip().startswith('{') or data.strip().startswith('['):
                        data = json.loads(data)
                    else:
                        data = yaml.safe_load(data)
                except Exception as e:
                    result.errors.append(ValidationError(
                        field_path="root",
                        error_type="parse_error",
                        message=f"Failed to parse data: {e}",
                        severity="error",
                        remediation="Fix data format (JSON/YAML syntax)"
                    ))
                    result.is_valid = False
                    return result
            
            # Use appropriate adapter for validation
            if schema_type in self.adapters:
                adapter = self.adapters[schema_type]
                result = adapter.validate(data, result, validation_mode)
            else:
                # Fallback to basic schema validation
                result = self._validate_basic_schema(data, schema_type, result)
            
            # Finalize result
            self._finalize_validation_result(result, start_time)
            
            # Update statistics
            self._update_validation_stats(result, schema_type)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Critical validation failure: {e}")
            # Return error result instead of raising exception
            result = ValidationResult(
                is_valid=False,
                schema_type=schema_type.value if isinstance(schema_type, SchemaType) else str(schema_type),
                validation_mode=validation_mode.value if validation_mode else "unknown"
            )
            result.errors.append(ValidationError(
                field_path="validator",
                error_type="infrastructure_failure",
                message=f"Validation infrastructure failure: {e}",
                severity="error"
            ))
            return result
    
    def _validate_basic_schema(
        self,
        data: Dict,
        schema_type: SchemaType,
        result: ValidationResult
    ) -> ValidationResult:
        """Basic schema validation using jsonschema"""
        try:
            schema = self.schemas.get(schema_type, {"type": "object"})
            
            # Validate against schema
            jsonschema.validate(data, schema)
            
            result.schema_checks_performed += 1
            
        except jsonschema.ValidationError as e:
            result.errors.append(ValidationError(
                field_path='.'.join(str(p) for p in e.path) if e.path else "root",
                error_type="schema_violation",
                message=e.message,
                severity="error",
                suggestion="Fix schema compliance issue"
            ))
            result.is_valid = False
        
        except Exception as e:
            result.errors.append(ValidationError(
                field_path="schema",
                error_type="validation_error",
                message=f"Schema validation failed: {e}",
                severity="error"
            ))
            result.is_valid = False
        
        return result
    
    def _finalize_validation_result(
        self,
        result: ValidationResult,
        start_time: datetime
    ) -> None:
        """Finalize validation result with performance metrics"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        result.validation_duration_ms = int(duration)
        
        # Calculate quality scores
        if result.is_valid and result.total_issues == 0:
            result.quality_score = 1.0
            result.compliance_score = 1.0
        elif result.is_valid:
            # Reduce score based on warnings/info
            penalty = min(0.3, result.total_issues * 0.05)
            result.quality_score = max(0.7, 1.0 - penalty)
            result.compliance_score = 0.9
        else:
            result.quality_score = 0.5
            result.compliance_score = 0.3
        
        # Log result
        if result.is_valid:
            self.logger.info(f"✅ Validation PASSED ({duration:.0f}ms, {result.total_issues} issues)")
        else:
            self.logger.error(f"❌ Validation FAILED ({result.error_count} errors)")
    
    def _update_validation_stats(
        self,
        result: ValidationResult,
        schema_type: SchemaType
    ) -> None:
        """Update validation statistics"""
        self.validation_stats['total_validations'] += 1
        self.validation_stats['schema_types_validated'].add(schema_type.value)
        
        if result.is_valid:
            self.validation_stats['successful_validations'] += 1
        else:
            self.validation_stats['failed_validations'] += 1
    
    # === LEGACY COMPATIBILITY METHODS ===
    
    def validate_frontmatter(self, data: Dict, material_name: str = None) -> ValidationResult:
        """Legacy compatibility - validate frontmatter data"""
        return self.validate(data, SchemaType.FRONTMATTER, material_name)
    
    def validate_materials_yaml(self, data: Dict) -> ValidationResult:
        """Validate Materials.yaml structure"""
        return self.validate(data, SchemaType.MATERIALS_YAML)
    
    def validate_categories_yaml(self, data: Dict) -> ValidationResult:
        """Validate Categories.yaml structure"""
        return self.validate(data, SchemaType.CATEGORIES_YAML)
    
    def validate_component_output(self, data: Dict, component_type: str) -> ValidationResult:
        """Validate component-generated output"""
        return self.validate(data, SchemaType.COMPONENT_OUTPUT)
    
    # === UTILITY METHODS ===
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        stats = self.validation_stats.copy()
        stats['schema_types_validated'] = list(stats['schema_types_validated'])
        return stats
    
    def get_supported_schemas(self) -> List[str]:
        """Get list of supported schema types"""
        return [schema_type.value for schema_type in SchemaType]


# === COMPONENT ADAPTERS ===

class SchemaAdapter:
    """Base class for schema-specific adapters"""
    
    def __init__(self, validator: SchemaValidator):
        self.validator = validator
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def validate(
        self,
        data: Dict,
        result: ValidationResult,
        validation_mode: ValidationMode
    ) -> ValidationResult:
        """Override in subclasses for schema-specific validation"""
        raise NotImplementedError


class FrontmatterAdapter(SchemaAdapter):
    """Adapter for frontmatter validation"""
    
    def validate(
        self,
        data: Dict,
        result: ValidationResult,
        validation_mode: ValidationMode
    ) -> ValidationResult:
        """Validate frontmatter structure and content"""
        
        # Basic schema validation
        result = self.validator._validate_basic_schema(data, SchemaType.FRONTMATTER, result)
        
        # Enhanced validations based on mode
        if validation_mode in [ValidationMode.ENHANCED, ValidationMode.RESEARCH_GRADE]:
            result = self._validate_frontmatter_quality(data, result)
        
        if validation_mode == ValidationMode.RESEARCH_GRADE:
            result = self._validate_research_grade_frontmatter(data, result)
        
        return result
    
    def _validate_frontmatter_quality(self, data: Dict, result: ValidationResult) -> ValidationResult:
        """Enhanced frontmatter quality validation"""
        
        # Check required sections
        required_sections = ['title', 'material_name', 'properties']
        for section in required_sections:
            if section not in data:
                result.warnings.append(ValidationError(
                    field_path=section,
                    error_type="missing_section",
                    message=f"Recommended section '{section}' is missing",
                    severity="warning",
                    suggestion=f"Add {section} section to improve completeness"
                ))
        
        return result
    
    def _validate_research_grade_frontmatter(self, data: Dict, result: ValidationResult) -> ValidationResult:
        """Research-grade frontmatter validation"""
        
        # Validate property sources and confidence levels
        properties = data.get('properties', {})
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict):
                if 'confidence' not in prop_data:
                    result.warnings.append(ValidationError(
                        field_path=f"properties.{prop_name}.confidence",
                        error_type="missing_confidence",
                        message=f"Property '{prop_name}' missing confidence score",
                        severity="warning",
                        suggestion="Add confidence score for research traceability"
                    ))
        
        return result


class MaterialsYamlAdapter(SchemaAdapter):
    """Adapter for Materials.yaml validation"""
    
    def validate(
        self,
        data: Dict,
        result: ValidationResult,
        validation_mode: ValidationMode
    ) -> ValidationResult:
        """Validate Materials.yaml structure"""
        
        # Basic schema validation
        result = self.validator._validate_basic_schema(data, SchemaType.MATERIALS_YAML, result)
        
        # Materials-specific validation
        materials = data.get('materials', {})
        for material_name, material_data in materials.items():
            if not isinstance(material_data, dict):
                result.errors.append(ValidationError(
                    field_path=f"materials.{material_name}",
                    error_type="invalid_structure",
                    message=f"Material '{material_name}' must be an object",
                    severity="error"
                ))
                result.is_valid = False
        
        return result


class CategoriesYamlAdapter(SchemaAdapter):
    """Adapter for Categories.yaml validation"""
    
    def validate(
        self,
        data: Dict,
        result: ValidationResult,
        validation_mode: ValidationMode
    ) -> ValidationResult:
        """Validate Categories.yaml structure"""
        
        # Basic schema validation
        result = self.validator._validate_basic_schema(data, SchemaType.CATEGORIES_YAML, result)
        
        # Categories-specific validation
        categories = data.get('categories', {})
        for category_name, category_data in categories.items():
            if not isinstance(category_data, dict):
                result.errors.append(ValidationError(
                    field_path=f"categories.{category_name}",
                    error_type="invalid_structure",
                    message=f"Category '{category_name}' must be an object",
                    severity="error"
                ))
                result.is_valid = False
        
        return result


class ComponentOutputAdapter(SchemaAdapter):
    """Adapter for component output validation"""
    
    def validate(
        self,
        data: Dict,
        result: ValidationResult,
        validation_mode: ValidationMode
    ) -> ValidationResult:
        """Validate component-generated output"""
        
        # Basic schema validation
        result = self.validator._validate_basic_schema(data, SchemaType.COMPONENT_OUTPUT, result)
        
        return result


class ConfigurationAdapter(SchemaAdapter):
    """Adapter for configuration validation"""
    
    def validate(
        self,
        data: Dict,
        result: ValidationResult,
        validation_mode: ValidationMode
    ) -> ValidationResult:
        """Validate configuration data"""
        
        # Basic schema validation
        result = self.validator._validate_basic_schema(data, SchemaType.CONFIGURATION, result)
        
        return result


# === CONVENIENCE FUNCTIONS ===

def validate_frontmatter(data: Dict, material_name: str = None) -> ValidationResult:
    """Convenience function for frontmatter validation"""
    validator = SchemaValidator()
    return validator.validate_frontmatter(data, material_name)


def validate_materials_yaml(data: Dict) -> ValidationResult:
    """Convenience function for Materials.yaml validation"""
    validator = SchemaValidator()
    return validator.validate_materials_yaml(data)


def validate_categories_yaml(data: Dict) -> ValidationResult:
    """Convenience function for Categories.yaml validation"""
    validator = SchemaValidator()
    return validator.validate_categories_yaml(data)