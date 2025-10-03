#!/usr/bin/env python3
"""
Unified Schema Validator for Z-Beam Generator

Consolidates all validation functionality into a single, robust validator:
- Replaces: enhanced_schema_validator.py, core/schema_validator.py, basic schema_validator.py
- Supports: Multiple validation modes (basic, enhanced, research_grade)
- Provides: Backward compatibility with all existing interfaces
- Features: Automatic schema detection, standardized error handling, quality scoring

Architecture:
- Single source of truth for all validation logic
- Pluggable validation modes for different use cases
- Standardized ValidationResult across all operations
- Graceful degradation with informative error messages
"""

import json
import jsonschema
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationMode(Enum):
    """Available validation modes"""
    BASIC = "basic"                    # Simple schema compliance
    ENHANCED = "enhanced"              # Schema + quality scoring  
    RESEARCH_GRADE = "research_grade"  # Full research validation


@dataclass
class ValidationError:
    """Structured validation error"""
    field_path: str
    error_type: str
    message: str
    severity: str = "error"  # error, warning, info
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Unified validation result supporting all existing interfaces"""
    
    # Core validation
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    
    # Quality metrics (enhanced/research modes)
    quality_score: float = 0.0
    confidence_coverage: float = 0.0
    research_validation_coverage: float = 0.0
    
    # Compliance details
    compliance_details: Dict[str, Any] = field(default_factory=dict)
    validation_mode: str = "basic"
    validation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Backward compatibility properties
    @property
    def valid(self) -> bool:
        """Compatibility with legacy ValidationResult.valid"""
        return self.is_valid
    
    @property
    def error_count(self) -> int:
        """Compatibility with legacy ValidationResult.error_count"""
        return len([e for e in self.errors if e.severity == "error"])
    
    @property
    def error_messages(self) -> List[str]:
        """Get error messages as strings for compatibility"""
        return [e.message for e in self.errors if e.severity == "error"]
    
    @property
    def warning_messages(self) -> List[str]:
        """Get warning messages as strings"""
        return [e.message for e in self.warnings]


class SchemaManager:
    """Manages schema loading and hierarchy"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.schemas_dir = project_root / "schemas"
        self._schema_cache = {}
        
    def get_primary_schema(self) -> Tuple[Path, Dict]:
        """Get the primary schema - FAIL-FAST if not found per GROK_INSTRUCTIONS.md"""
        # Try primary schema only - no fallbacks
        schema_path = self.schemas_dir / "active/frontmatter_v2.json"
        
        if not schema_path.exists():
            raise FileNotFoundError(
                f"Primary schema not found: {schema_path}. "
                "Per GROK_INSTRUCTIONS.md: No fallbacks allowed."
            )
        
        try:
            schema_data = self._load_schema(schema_path)
            logger.info(f"Using primary schema: active/frontmatter_v2.json")
            return schema_path, schema_data
        except Exception as e:
            raise RuntimeError(
                f"Failed to load primary schema: {e}. "
                "Per GROK_INSTRUCTIONS.md: No fallbacks allowed."
            )
    
    def _load_schema(self, schema_path: Path) -> Dict:
        """Load and validate schema file"""
        cache_key = str(schema_path)
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
            
        with open(schema_path, 'r') as f:
            schema_data = json.load(f)
            
        # Validate the schema itself
        jsonschema.Draft7Validator.check_schema(schema_data)
        
        self._schema_cache[cache_key] = schema_data
        return schema_data
    
    def _get_minimal_schema(self) -> Dict:
        """REMOVED: No fallback schemas allowed per GROK_INSTRUCTIONS.md"""
        raise NotImplementedError(
            "Minimal schema fallback not allowed per GROK_INSTRUCTIONS.md. "
            "System must have valid primary schema or fail."
        )
        return {
            "type": "object",
            "required": ["name", "category", "title", "description"],
            "properties": {
                "name": {"type": "string"},
                "category": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"}
            }
        }


class SchemaValidator:
    """
    Consolidated schema validator replacing all existing validators.
    
    Provides backward compatibility with:
    - EnhancedSchemaValidator
    - FrontmatterSchemaValidator (core and basic)
    - Legacy validation interfaces
    """
    
    def __init__(self, schema_path: Optional[str] = None, validation_mode: str = "enhanced"):
        """
        Initialize unified validator.
        
        Args:
            schema_path: Explicit schema path (optional - auto-detects best schema)
            validation_mode: Validation strictness ("basic", "enhanced", "research_grade")
        """
        self.validation_mode = ValidationMode(validation_mode)
        
        # Initialize project structure
        if schema_path:
            self.project_root = Path(schema_path).parent.parent
        else:
            self.project_root = Path(__file__).parent.parent
        
        # Initialize schema manager
        self.schema_manager = SchemaManager(self.project_root)
        
        # Load primary schema
        if schema_path:
            self.schema_path = Path(schema_path)
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
        else:
            self.schema_path, self.schema = self.schema_manager.get_primary_schema()
        
        # Initialize JSON schema validator
        try:
            self.json_validator = jsonschema.Draft7Validator(self.schema)
        except Exception as e:
            logger.error(f"Schema validation setup failed: {e}")
            self.json_validator = None
        
        logger.info(f"SchemaValidator initialized - Mode: {self.validation_mode.value}")
    
    def validate(self, data: Dict[str, Any], material_name: str = "unknown", **kwargs) -> ValidationResult:
        """
        Main validation interface supporting all modes.
        
        Args:
            data: Data to validate
            material_name: Material name for context
            **kwargs: Additional validation options
            
        Returns:
            Comprehensive ValidationResult
        """
        
        result = ValidationResult(
            is_valid=True,
            validation_mode=self.validation_mode.value,
            compliance_details={
                "schema_version": self.schema.get("title", "Unknown"),
                "material_name": material_name,
                "validation_mode": self.validation_mode.value
            }
        )
        
        try:
            # Core JSON Schema validation (all modes)
            self._validate_json_schema(data, result)
            
            # Enhanced validations
            if self.validation_mode in [ValidationMode.ENHANCED, ValidationMode.RESEARCH_GRADE]:
                self._validate_enhanced_quality(data, result)
                self._calculate_quality_metrics(data, result)
            
            # Research-grade validations
            if self.validation_mode == ValidationMode.RESEARCH_GRADE:
                self._validate_research_requirements(data, result)
            
            # Final validation status
            result.is_valid = len([e for e in result.errors if e.severity == "error"]) == 0
            
            # Log results
            if result.is_valid:
                logger.info(f"✅ Validation passed for {material_name} - Quality: {result.quality_score:.1f}%")
            else:
                logger.warning(f"❌ Validation failed for {material_name} - {len(result.errors)} errors")
            
            return result
            
        except Exception as e:
            logger.error(f"Validation process failed for {material_name}: {e}")
            result.is_valid = False
            result.errors.append(ValidationError(
                field_path="validation_system",
                error_type="system_error", 
                message=f"Validation process failed: {e}",
                severity="error"
            ))
            return result
    
    def _validate_json_schema(self, data: Dict, result: ValidationResult):
        """Core JSON Schema validation"""
        if not self.json_validator:
            result.errors.append(ValidationError(
                field_path="schema",
                error_type="schema_unavailable",
                message="JSON schema validator not available"
            ))
            return
        
        schema_errors = list(self.json_validator.iter_errors(data))
        result.compliance_details["schema_violations"] = len(schema_errors)
        
        for error in schema_errors:
            field_path = " → ".join([str(part) for part in error.absolute_path])
            result.errors.append(ValidationError(
                field_path=field_path or "root",
                error_type="schema_violation",
                message=error.message,
                severity="error"
            ))
    
    def _validate_enhanced_quality(self, data: Dict, result: ValidationResult):
        """Enhanced validation with quality checks"""
        
        # Check for DataMetric structure compliance
        self._validate_datametric_structure(data, result, "materialProperties")
        self._validate_datametric_structure(data, result, "machineSettings")
        
        # Check confidence scores
        self._validate_confidence_requirements(data, result)
    
    def _validate_datametric_structure(self, data: Dict, result: ValidationResult, section: str):
        """Validate DataMetric structure in properties/machineSettings"""
        section_data = data.get(section, {})
        if not isinstance(section_data, dict):
            return
            
        for field_name, field_data in section_data.items():
            if not isinstance(field_data, dict):
                result.warnings.append(ValidationError(
                    field_path=f"{section}.{field_name}",
                    error_type="structure_warning",
                    message=f"Expected DataMetric structure for {field_name}",
                    severity="warning",
                    suggestion="Use DataMetric pattern with value, unit, confidence_score"
                ))
                continue
            
            # Check for basic DataMetric fields
            required_fields = ["value", "unit"] 
            for req_field in required_fields:
                if req_field not in field_data:
                    result.errors.append(ValidationError(
                        field_path=f"{section}.{field_name}",
                        error_type="missing_field",
                        message=f"Missing required DataMetric field: {req_field}"
                    ))
    
    def _validate_confidence_requirements(self, data: Dict, result: ValidationResult):
        """Validate confidence score requirements"""
        min_confidence = 0.7  # 70% minimum confidence
        
        for section in ["materialProperties", "machineSettings"]:
            section_data = data.get(section, {})
            if not isinstance(section_data, dict):
                continue
                
            for field_name, field_data in section_data.items():
                if isinstance(field_data, dict):
                    # Check direct confidence_score
                    confidence = field_data.get("confidence_score")
                    if confidence is None:
                        # Check nested validation.confidence_score
                        validation = field_data.get("validation", {})
                        confidence = validation.get("confidence_score")
                    
                    if confidence is not None and confidence < min_confidence:
                        result.warnings.append(ValidationError(
                            field_path=f"{section}.{field_name}",
                            error_type="low_confidence",
                            message=f"Low confidence score: {confidence} (minimum: {min_confidence})",
                            severity="warning",
                            suggestion="Increase data validation or mark as preliminary"
                        ))
    
    def _validate_research_requirements(self, data: Dict, result: ValidationResult):
        """Research-grade validation requirements"""
        
        validated_fields = 0
        total_fields = 0
        
        for section in ["materialProperties", "machineSettings"]:
            section_data = data.get(section, {})
            if not isinstance(section_data, dict):
                continue
                
            for field_name, field_data in section_data.items():
                total_fields += 1
                if isinstance(field_data, dict):
                    validation = field_data.get("validation", {})
                    
                    # Check research validation requirements
                    if (validation.get("confidence_score", 0) >= 0.8 and 
                        validation.get("sources_validated", 0) >= 2):
                        validated_fields += 1
                    else:
                        result.warnings.append(ValidationError(
                            field_path=f"{section}.{field_name}",
                            error_type="insufficient_validation",
                            message="Insufficient research validation (need ≥80% confidence, ≥2 sources)",
                            severity="warning"
                        ))
        
        # Calculate research validation coverage
        if total_fields > 0:
            result.research_validation_coverage = validated_fields / total_fields
        
        # Research-grade requirement: 80% coverage minimum
        if result.research_validation_coverage < 0.8:
            result.errors.append(ValidationError(
                field_path="research_validation",
                error_type="insufficient_coverage",
                message=f"Research validation coverage {result.research_validation_coverage:.1%} below 80% requirement",
                severity="error" if self.validation_mode == ValidationMode.RESEARCH_GRADE else "warning"
            ))
    
    def _calculate_quality_metrics(self, data: Dict, result: ValidationResult):
        """Calculate quality score and metrics"""
        
        score_components = []
        
        # Schema compliance (40%)
        schema_violations = result.compliance_details.get("schema_violations", 0)
        schema_score = max(0, 100 - (schema_violations * 10))  # -10 points per violation
        score_components.append(("schema_compliance", schema_score * 0.4))
        
        # Data completeness (30%)
        total_possible_fields = len(self.schema.get("properties", {}))
        present_fields = len([k for k in data.keys() if k in self.schema.get("properties", {})])
        completeness = (present_fields / total_possible_fields) if total_possible_fields > 0 else 1.0
        score_components.append(("data_completeness", completeness * 100 * 0.3))
        
        # Confidence quality (30%)
        confidence_scores = []
        for section in ["materialProperties", "machineSettings"]:
            section_data = data.get(section, {})
            if isinstance(section_data, dict):
                for field_data in section_data.values():
                    if isinstance(field_data, dict):
                        confidence = field_data.get("confidence_score")
                        if confidence is None:
                            validation = field_data.get("validation", {})
                            confidence = validation.get("confidence_score")
                        if confidence is not None:
                            confidence_scores.append(confidence)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.7
        score_components.append(("confidence_quality", avg_confidence * 100 * 0.3))
        
        # Calculate total quality score
        result.quality_score = sum(score for _, score in score_components)
        result.confidence_coverage = avg_confidence
        
        # Store component breakdown
        result.compliance_details["quality_breakdown"] = dict(score_components)
    
    # Backward compatibility methods
    def validate_frontmatter(self, data: Dict, material_name: str = "unknown") -> Tuple[bool, List[str]]:
        """
        Legacy interface compatibility for core/schema_validator.py
        
        Returns:
            Tuple of (is_valid, list_of_error_strings)
        """
        result = self.validate(data, material_name)
        return result.is_valid, result.error_messages
    
    def validate_with_detailed_report(self, data: Dict, material_name: str = "unknown") -> str:
        """
        Legacy interface compatibility for enhanced_schema_validator.py
        
        Returns:
            Formatted validation report string
        """
        result = self.validate(data, material_name)
        
        report = f"""
🔍 UNIFIED SCHEMA VALIDATION REPORT: {material_name.upper()}
{'='*60}

📊 VALIDATION SUMMARY:
   Schema Compliance: {'✅ PASS' if result.is_valid else '❌ FAIL'}
   Quality Score: {result.quality_score:.1f}%
   Confidence Coverage: {result.confidence_coverage:.1%}
   Research Coverage: {result.research_validation_coverage:.1%}
   Total Errors: {len(result.errors)}
   Total Warnings: {len(result.warnings)}
   Validation Mode: {result.validation_mode.upper()}

"""
        
        if result.errors:
            report += "❌ VALIDATION ERRORS:\n"
            for i, error in enumerate(result.errors, 1):
                report += f"   {i}. {error.field_path}: {error.message}\n"
            report += "\n"
        
        if result.warnings:
            report += "⚠️  VALIDATION WARNINGS:\n"
            for i, warning in enumerate(result.warnings, 1):
                report += f"   {i}. {warning.field_path}: {warning.message}\n"
            report += "\n"
        
        report += "📋 COMPLIANCE DETAILS:\n"
        for key, value in result.compliance_details.items():
            report += f"   {key}: {value}\n"
        
        if result.is_valid:
            report += "\n✅ VALIDATION SUCCESSFUL - Content is ready for production use!\n"
        else:
            report += "\n❌ VALIDATION FAILED - Content must be corrected before use.\n"
        
        return report


# Backward compatibility functions
def validate_frontmatter_schema(data: Dict, schema_path: str = None) -> ValidationResult:
    """Legacy function compatibility"""
    validator = SchemaValidator(schema_path, validation_mode="basic")
    return validator.validate(data)


def validate_frontmatter_and_log(data: Dict, material_name: str) -> bool:
    """Legacy function compatibility"""  
    validator = SchemaValidator(validation_mode="basic")
    result = validator.validate(data, material_name)
    
    if not result.is_valid:
        print(f"Validation failed for {material_name}:")
        for error in result.errors:
            print(f"  - {error.message}")
    
    return result.is_valid


def main():
    """CLI interface for unified schema validation"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified schema validation for Z-Beam generated content")
    parser.add_argument("data_file", help="JSON file with content to validate")
    parser.add_argument("--material", default="unknown", help="Material name for context")
    parser.add_argument("--mode", choices=["basic", "enhanced", "research_grade"], 
                       default="enhanced", help="Validation mode")
    parser.add_argument("--schema", help="Path to schema file (auto-detects by default)")
    parser.add_argument("--quiet", action="store_true", help="Only show pass/fail result")
    
    args = parser.parse_args()
    
    # Load data to validate
    try:
        with open(args.data_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading data file: {e}")
        return 1
    
    # Create validator
    try:
        validator = SchemaValidator(args.schema, args.mode)
    except Exception as e:
        print(f"❌ Error initializing validator: {e}")
        return 1
    
    # Validate
    if args.quiet:
        result = validator.validate(data, args.material)
        print("✅ PASS" if result.is_valid else "❌ FAIL")
        return 0 if result.is_valid else 1
    else:
        report = validator.validate_with_detailed_report(data, args.material)
        print(report)
        
        result = validator.validate(data, args.material)
        return 0 if result.is_valid else 1


if __name__ == "__main__":
    exit(main())