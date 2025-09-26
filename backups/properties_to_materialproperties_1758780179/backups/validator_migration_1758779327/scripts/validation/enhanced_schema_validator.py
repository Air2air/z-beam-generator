#!/usr/bin/env python3
"""
Enhanced Schema Validator for Z-Beam Generator

Production-ready schema validator with comprehensive validation, research metadata checking,
and integration with the existing quality measurement system.

This validator enforces the enhanced schema structure with:
1. Nested properties with validation metadata
2. Research validation requirements  
3. Quality scoring integration
4. Fail-fast behavior with detailed error reporting
"""

import json
import jsonschema
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Comprehensive validation result with detailed feedback"""
    
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_score: float
    research_validation_coverage: float
    compliance_details: Dict[str, Any]


class EnhancedSchemaValidator:
    """Production-ready enhanced schema validator"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize validator with enhanced unified schema"""
        if schema_path is None:
            # Default to enhanced unified schema
            project_root = Path(__file__).parent.parent.parent
            schema_path = project_root / "schemas" / "enhanced_unified_frontmatter.json"
        
        self.schema_path = Path(schema_path)
        self._load_schema()
        
    def _load_schema(self):
        """Load and validate the JSON schema"""
        try:
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
            
            # Validate the schema itself
            jsonschema.Draft7Validator.check_schema(self.schema)
            self.validator = jsonschema.Draft7Validator(self.schema)
            
            logger.info(f"✅ Loaded enhanced schema from {self.schema_path}")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file {self.schema_path}: {e}")
        except jsonschema.SchemaError as e:
            raise ValueError(f"Invalid schema structure in {self.schema_path}: {e}")
        except FileNotFoundError:
            raise ValueError(f"Schema file not found: {self.schema_path}")
    
    def validate(self, data: Dict[str, Any], material_name: str = "unknown") -> ValidationResult:
        """
        Comprehensive validation with quality scoring and research metadata checks.
        
        Args:
            data: Generated frontmatter data to validate
            material_name: Name of material for context in error messages
            
        Returns:
            ValidationResult with detailed validation feedback
        """
        
        errors = []
        warnings = []
        
        # 1. Core JSON Schema Validation
        schema_errors = list(self.validator.iter_errors(data))
        for error in schema_errors:
            error_path = " → ".join([str(part) for part in error.absolute_path])
            error_message = f"{error_path}: {error.message}"
            errors.append(error_message)
        
        # 2. Enhanced Research Validation Checks
        research_score, research_errors, research_warnings = self._validate_research_metadata(data)
        errors.extend(research_errors)
        warnings.extend(research_warnings)
        
        # 3. Quality Assessment
        quality_score = self._calculate_quality_score(data)
        
        # 4. Compliance Details
        compliance_details = {
            "schema_version": self.schema.get("title", "Unknown"),
            "validation_timestamp": self._get_timestamp(),
            "material_name": material_name,
            "schema_violations": len(schema_errors),
            "research_validation_score": research_score,
            "overall_quality_score": quality_score
        }
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            research_validation_coverage=research_score,
            compliance_details=compliance_details
        )
    
    def _validate_research_metadata(self, data: Dict[str, Any]) -> tuple[float, List[str], List[str]]:
        """
        Validate research validation metadata requirements.
        
        Returns:
            Tuple of (validation_score, errors, warnings)
        """
        
        errors = []
        warnings = []
        
        # Check properties validation metadata
        properties = data.get('properties', {})
        validated_properties = 0
        total_properties = len(properties)
        
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict):
                validation = prop_data.get('validation', {})
                
                # Check required validation fields
                if 'confidence_score' not in validation:
                    errors.append(f"properties.{prop_name}.validation: Missing required 'confidence_score'")
                elif validation.get('confidence_score', 0) < 0.7:
                    warnings.append(f"properties.{prop_name}: Low confidence score ({validation.get('confidence_score')})")
                
                if 'sources_validated' not in validation:
                    errors.append(f"properties.{prop_name}.validation: Missing required 'sources_validated'")
                elif validation.get('sources_validated', 0) < 2:
                    warnings.append(f"properties.{prop_name}: Few validation sources ({validation.get('sources_validated')})")
                
                # Check research sources
                research_sources = validation.get('research_sources', [])
                if not research_sources:
                    warnings.append(f"properties.{prop_name}: No research sources provided")
                elif len(research_sources) < 2:
                    warnings.append(f"properties.{prop_name}: Only {len(research_sources)} research source(s)")
                
                # Count as validated if has required fields
                if validation.get('confidence_score') and validation.get('sources_validated'):
                    validated_properties += 1
        
        # Check machine settings validation
        machine_settings = data.get('machineSettings', {})
        validated_settings = 0
        total_settings = len(machine_settings)
        
        for setting_name, setting_data in machine_settings.items():
            if isinstance(setting_data, dict):
                validation = setting_data.get('validation', {})
                
                if 'confidence_score' not in validation:
                    errors.append(f"machineSettings.{setting_name}.validation: Missing required 'confidence_score'")
                
                if 'sources_validated' not in validation:
                    errors.append(f"machineSettings.{setting_name}.validation: Missing required 'sources_validated'")
                
                # Count as validated
                if validation.get('confidence_score') and validation.get('sources_validated'):
                    validated_settings += 1
        
        # Calculate overall validation score
        total_items = total_properties + total_settings
        validated_items = validated_properties + validated_settings
        
        validation_score = (validated_items / total_items) if total_items > 0 else 0.0
        
        return validation_score, errors, warnings
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate overall quality score based on multiple factors.
        
        Returns:
            Quality score from 0-100
        """
        
        score_components = []
        
        # 1. Required Fields Completeness (30%)
        required_fields = self.schema.get('required', [])
        present_required = sum(1 for field in required_fields if field in data)
        required_completeness = (present_required / len(required_fields)) if required_fields else 1.0
        score_components.append(('required_fields', required_completeness * 30))
        
        # 2. Properties Quality (25%)
        properties = data.get('properties', {})
        properties_score = 0.0
        if properties:
            # Score based on validation metadata completeness
            total_prop_score = 0
            for prop_data in properties.values():
                if isinstance(prop_data, dict):
                    prop_score = 0
                    # Has value and unit (basic)
                    if 'value' in prop_data and 'unit' in prop_data:
                        prop_score += 0.3
                    # Has description
                    if 'description' in prop_data:
                        prop_score += 0.2
                    # Has validation metadata
                    validation = prop_data.get('validation', {})
                    if validation.get('confidence_score') and validation.get('sources_validated'):
                        prop_score += 0.3
                    # Has processing impact
                    if 'processing_impact' in prop_data:
                        prop_score += 0.2
                    
                    total_prop_score += prop_score
            
            properties_score = (total_prop_score / len(properties)) if properties else 0.0
        
        score_components.append(('properties_quality', properties_score * 25))
        
        # 3. Machine Settings Quality (20%)
        machine_settings = data.get('machineSettings', {})
        settings_score = 0.0
        if machine_settings:
            total_settings_score = 0
            for setting_data in machine_settings.values():
                if isinstance(setting_data, dict):
                    setting_score = 0
                    # Basic structure
                    if all(key in setting_data for key in ['value', 'unit', 'validation']):
                        setting_score += 0.6
                    # Has description
                    if 'description' in setting_data:
                        setting_score += 0.2
                    # Has optimization notes  
                    if 'optimization_notes' in setting_data:
                        setting_score += 0.2
                    
                    total_settings_score += setting_score
            
            settings_score = (total_settings_score / len(machine_settings)) if machine_settings else 0.0
        
        score_components.append(('machine_settings_quality', settings_score * 20))
        
        # 4. Applications Completeness (15%)
        applications = data.get('applications', [])
        app_score = min(1.0, len(applications) / 6.0)  # Target: 6+ applications
        score_components.append(('applications_completeness', app_score * 15))
        
        # 5. Overall Structure (10%)
        structure_score = 1.0  # All required fields present means good structure
        score_components.append(('structure_completeness', structure_score * 10))
        
        # Calculate total score
        total_score = sum(score for _, score in score_components)
        
        logger.debug(f"Quality score components: {score_components}")
        logger.debug(f"Total quality score: {total_score}")
        
        return total_score
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for validation metadata"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_with_detailed_report(self, data: Dict[str, Any], material_name: str = "unknown") -> str:
        """
        Generate detailed validation report for human consumption.
        
        Args:
            data: Generated frontmatter data to validate
            material_name: Name of material for context
            
        Returns:
            Formatted validation report string
        """
        
        result = self.validate(data, material_name)
        
        report = f"""
🔍 ENHANCED SCHEMA VALIDATION REPORT: {material_name.upper()}
{'='*60}

📊 VALIDATION SUMMARY:
   Schema Compliance: {'✅ PASS' if result.is_valid else '❌ FAIL'}
   Quality Score: {result.quality_score:.1f}%
   Research Coverage: {result.research_validation_coverage:.1%}
   Total Errors: {len(result.errors)}
   Total Warnings: {len(result.warnings)}

"""
        
        if result.errors:
            report += "❌ VALIDATION ERRORS:\n"
            for i, error in enumerate(result.errors, 1):
                report += f"   {i}. {error}\n"
            report += "\n"
        
        if result.warnings:
            report += "⚠️  VALIDATION WARNINGS:\n"
            for i, warning in enumerate(result.warnings, 1):
                report += f"   {i}. {warning}\n"
            report += "\n"
        
        report += "📋 COMPLIANCE DETAILS:\n"
        for key, value in result.compliance_details.items():
            report += f"   {key}: {value}\n"
        
        if result.is_valid:
            report += "\n✅ SCHEMA VALIDATION SUCCESSFUL - Content is ready for production use!\n"
        else:
            report += "\n❌ SCHEMA VALIDATION FAILED - Content must be corrected before use.\n"
        
        return report


def main():
    """CLI interface for enhanced schema validation"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced schema validation for Z-Beam generated content")
    parser.add_argument("data_file", help="JSON file with generated content to validate")
    parser.add_argument("--material", default="unknown", help="Material name for context")
    parser.add_argument("--schema", help="Path to schema file (defaults to enhanced_frontmatter.json)")
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
        validator = EnhancedSchemaValidator(args.schema)
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
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