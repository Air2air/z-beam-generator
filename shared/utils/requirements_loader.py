"""
Requirements Loader for Z-Beam Generator
Provides centralized access to all system requirements from config/requirements.yaml
Single source of truth for ALL generation, validation, and auditing requirements
"""

import yaml
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

class RequirementsLoader:
    """Singleton class to load and provide access to comprehensive system requirements"""
    
    _instance = None
    _requirements = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RequirementsLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._requirements is None:
            self._load_requirements()
    
    def _load_requirements(self):
        """Load comprehensive requirements from config/requirements.yaml"""
        config_path = Path(__file__).parent.parent / "config" / "requirements.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Requirements configuration not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._requirements = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in requirements.yaml: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load requirements: {e}")
        
        # Validate that we have the expected comprehensive structure
        expected_sections = [
            "data_architecture", "schema_compliance", "property_validation", 
            "text_quality", "author_voice", "frontmatter_structure",
            "validation_severity", "audit_reporting", "fail_fast", 
            "testing_requirements", "system_integration"
        ]
        
        missing_sections = [section for section in expected_sections 
                          if section not in self._requirements]
        
        if missing_sections:
            raise ValueError(f"Missing required sections in requirements.yaml: {missing_sections}")
    
    # ==========================================================================
    # CORE ACCESS METHODS
    # ==========================================================================
    
    def get_requirements(self) -> Dict[str, Any]:
        """Get all requirements (comprehensive configuration)"""
        return self._requirements
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a specific requirements section"""
        return self._requirements.get(section, {})
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific value from requirements with nested path support"""
        section_data = self.get_section(section)
        
        # Support nested keys with dot notation
        if '.' in key:
            keys = key.split('.')
            current = section_data
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
            return current
        
        return section_data.get(key, default)
    
    def get_nested_value(self, path: List[str], default: Any = None) -> Any:
        """Get nested value by path list"""
        current = self._requirements
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    # ==========================================================================
    # DATA ARCHITECTURE REQUIREMENTS
    # ==========================================================================
    
    def get_prohibited_fields_in_materials(self) -> List[str]:
        """Get fields prohibited in Materials.yaml"""
        return self.get_value("data_architecture", "materials_yaml.prohibited_fields", [])
    
    def get_required_property_fields(self, field_type: str = "mandatory") -> List[str]:
        """Get required fields for material properties"""
        return self.get_value("data_architecture", f"materials_yaml.required_property_fields.{field_type}", [])
    
    def get_prohibited_property_values(self) -> List[str]:
        """Get prohibited values in material properties"""
        return self.get_value("data_architecture", "materials_yaml.prohibited_values", [])
    
    def is_prohibited_field_in_materials(self, field: str) -> bool:
        """Check if field is prohibited in Materials.yaml"""
        return field in self.get_prohibited_fields_in_materials()
    
    def is_prohibited_property_value(self, value: str) -> bool:
        """Check if property value is prohibited"""
        return value in self.get_prohibited_property_values()
    
    # ==========================================================================
    # SCHEMA COMPLIANCE REQUIREMENTS
    # ==========================================================================
    
    def get_required_frontmatter_fields(self, field_type: str = "mandatory") -> List[str]:
        """Get required frontmatter fields"""
        return self.get_value("schema_compliance", f"required_root_fields.{field_type}", [])
    
    def get_valid_categories(self) -> List[str]:
        """Get valid material categories"""
        return self.get_value("schema_compliance", "category_enum", [])
    
    def get_valid_subcategories(self, category: str) -> List[str]:
        """Get valid subcategories for a material category"""
        return self.get_value("schema_compliance", f"subcategory_enum.{category}", [])
    
    def get_validation_mode_requirements(self, mode: str) -> List[str]:
        """Get requirements for specific validation mode"""
        return self.get_nested_value(["schema_compliance", "validation_modes", mode, "requirements"], [])
    
    # ==========================================================================
    # PROPERTY VALIDATION REQUIREMENTS
    # ==========================================================================
    
    def get_essential_properties(self, category: str) -> List[str]:
        """Get essential properties for material category"""
        return self.get_nested_value(["property_validation", "category_requirements", category, "essential_properties"], [])
    
    def get_minimum_property_coverage(self, category: str) -> float:
        """Get minimum coverage percentage for essential properties"""
        return self.get_nested_value(["property_validation", "category_requirements", category, "minimum_coverage"], 0.5)
    
    def get_minimum_total_properties(self, category: str) -> int:
        """Get minimum total properties required for category"""
        return self.get_nested_value(["property_validation", "category_requirements", category, "minimum_total"], 3)
    
    def get_typical_property_range(self, category: str) -> List[int]:
        """Get typical property count range for category"""
        return self.get_nested_value(["property_validation", "category_requirements", category, "typical_range"], [3, 10])
    
    def get_confidence_range(self, source_type: str) -> List[int]:
        """Get confidence score range for source type"""
        return self.get_nested_value(["property_validation", "confidence_requirements", "score_ranges", source_type], [70, 95])
    
    def get_minimum_confidence_threshold(self, usage_type: str = "production") -> int:
        """Get minimum confidence threshold for usage type"""
        return self.get_nested_value(["property_validation", "confidence_requirements", "minimum_thresholds", usage_type], 70)
    
    # ==========================================================================
    # TEXT QUALITY REQUIREMENTS
    # ==========================================================================
    
    def get_max_line_length(self) -> int:
        """Get maximum line length for YAML output"""
        return self.get_value("text_quality", "line_formatting.max_line_length", 120)
    
    def get_prohibited_text_patterns(self, pattern_type: str = "markdown") -> List[str]:
        """Get prohibited text patterns by type"""
        return self.get_nested_value(["text_quality", "prohibited_patterns", pattern_type], [])
    
    def get_text_quality_thresholds(self) -> Dict[str, int]:
        """Get text quality scoring thresholds"""
        return self.get_value("text_quality", "quality_thresholds", {})
    
    def get_minimum_text_length(self, text_type: str) -> int:
        """Get minimum text length requirement"""
        return self.get_nested_value(["text_quality", "text_length", text_type, "minimum"], 50)
    
    def should_use_hard_line_breaks(self) -> bool:
        """Check if hard line breaks are required"""
        return self.get_value("text_quality", "line_formatting.hard_break_required", True)
    
    # ==========================================================================
    # AUTHOR VOICE REQUIREMENTS
    # ==========================================================================
    
    def get_author_voice_requirements(self, country: str) -> Dict[str, Any]:
        """Get comprehensive author voice requirements for country"""
        return self.get_nested_value(["author_voice", "countries", country.lower()], {})
    
    def get_author_vocabulary_indicators(self, country: str, indicator_type: str = "primary") -> List[str]:
        """Get vocabulary indicators for author country"""
        return self.get_nested_value(["author_voice", "countries", country.lower(), "vocabulary_indicators", indicator_type], [])
    
    def get_author_sentence_patterns(self, country: str) -> List[str]:
        """Get sentence patterns for author country"""
        return self.get_nested_value(["author_voice", "countries", country.lower(), "sentence_patterns"], [])
    
    def get_minimum_voice_indicators(self, country: str) -> int:
        """Get minimum required voice indicators"""
        return self.get_nested_value(["author_voice", "countries", country.lower(), "validation_thresholds", "minimum_indicators"], 2)
    
    def get_voice_strength_threshold(self, country: str) -> float:
        """Get voice strength threshold for author"""
        return self.get_nested_value(["author_voice", "countries", country.lower(), "validation_thresholds", "strength_threshold"], 0.3)
    
    def get_voice_authenticity_minimum(self, country: str) -> int:
        """Get minimum authenticity score for author voice"""
        return self.get_nested_value(["author_voice", "countries", country.lower(), "validation_thresholds", "cultural_authenticity_min"], 75)
    
    # ==========================================================================
    # VALIDATION SEVERITY & AUDIT REPORTING
    # ==========================================================================
    
    def get_severity_config(self, severity: str) -> Dict[str, Any]:
        """Get configuration for specific severity level"""
        return self.get_nested_value(["validation_severity", severity], {})
    
    def should_fail_fast_on_severity(self, severity: str) -> bool:
        """Check if severity level should trigger fail-fast"""
        return self.get_nested_value(["validation_severity", severity, "fail_fast"], False)
    
    def get_audit_report_config(self) -> Dict[str, Any]:
        """Get audit reporting configuration"""
        return self.get_value("audit_reporting", {})
    
    def get_audit_icons(self) -> Dict[str, str]:
        """Get audit report icons"""
        severity_icons = self.get_nested_value(["audit_reporting", "icons", "severity"], {})
        status_icons = self.get_nested_value(["audit_reporting", "icons", "status"], {})
        category_icons = self.get_nested_value(["audit_reporting", "icons", "categories"], {})
        
        return {**severity_icons, **status_icons, **category_icons}
    
    def is_terminal_report_enabled(self) -> bool:
        """Check if terminal audit reports are enabled"""
        return self.get_nested_value(["audit_reporting", "terminal_report", "enabled"], True)
    
    def get_max_issues_per_severity(self) -> int:
        """Get maximum issues to show per severity level"""
        return self.get_nested_value(["audit_reporting", "terminal_report", "max_issues_per_severity"], 5)
    
    # ==========================================================================
    # FAIL-FAST ENFORCEMENT
    # ==========================================================================
    
    def get_zero_tolerance_violations(self) -> Dict[str, Any]:
        """Get zero tolerance violations that trigger fail-fast"""
        return self.get_value("fail_fast", "zero_tolerance", {})
    
    def is_zero_tolerance_violation(self, violation_type: str) -> bool:
        """Check if violation is zero tolerance (fail-fast)"""
        zero_tolerance = self.get_zero_tolerance_violations()
        return violation_type in zero_tolerance
    
    def get_pre_execution_checks(self) -> Dict[str, Any]:
        """Get pre-execution validation checks"""
        return self.get_value("fail_fast", "pre_execution_checks", {})
    
    def get_runtime_validation_requirements(self) -> List[str]:
        """Get runtime validation requirements"""
        return self.get_value("fail_fast", "runtime_validation", [])
    
    def get_required_exception_types(self) -> List[str]:
        """Get required exception types for error handling"""
        return self.get_nested_value(["fail_fast", "error_handling", "exception_types"], [])

# =============================================================================
# CONVENIENCE FUNCTIONS FOR BACKWARD COMPATIBILITY AND COMMON OPERATIONS
# =============================================================================

def is_prohibited_source(source: str) -> bool:
    """Check if a source is prohibited in data storage (backward compatibility)"""
    loader = RequirementsLoader()
    prohibited = loader.get_prohibited_property_values()
    return source in prohibited

def get_author_voice_requirements(country: str) -> Dict[str, Any]:
    """Get author voice requirements for a specific country (backward compatibility)"""
    loader = RequirementsLoader()
    return loader.get_author_voice_requirements(country)

def get_audit_severity_config() -> Dict[str, Any]:
    """Get audit severity configuration (backward compatibility)"""
    loader = RequirementsLoader()
    return loader.get_value("validation_severity", {})

def get_text_quality_requirements() -> Dict[str, Any]:
    """Get text quality requirements (backward compatibility)"""
    loader = RequirementsLoader()
    return loader.get_value("text_quality", {})

def is_fail_fast_violation(violation_type: str) -> bool:
    """Check if a violation type should trigger fail-fast behavior (backward compatibility)"""
    loader = RequirementsLoader()
    return loader.is_zero_tolerance_violation(violation_type)

# New comprehensive convenience functions

def get_property_validation_for_category(category: str) -> Dict[str, Any]:
    """Get complete property validation requirements for material category"""
    loader = RequirementsLoader()
    return {
        "essential_properties": loader.get_essential_properties(category),
        "minimum_coverage": loader.get_minimum_property_coverage(category),
        "minimum_total": loader.get_minimum_total_properties(category),
        "typical_range": loader.get_typical_property_range(category)
    }

def validate_property_structure(property_data: Dict[str, Any]) -> List[str]:
    """Validate property structure against requirements"""
    loader = RequirementsLoader()
    errors = []
    
    # Check required fields
    required_fields = loader.get_required_property_fields("mandatory")
    for field in required_fields:
        if field not in property_data:
            errors.append(f"Missing required field: {field}")
    
    # Check prohibited values
    for key, value in property_data.items():
        if isinstance(value, str) and loader.is_prohibited_property_value(value):
            errors.append(f"Prohibited value '{value}' in field '{key}'")
    
    return errors

def get_comprehensive_validation_config() -> Dict[str, Any]:
    """Get comprehensive validation configuration for system components"""
    loader = RequirementsLoader()
    return {
        "data_architecture": loader.get_section("data_architecture"),
        "schema_compliance": loader.get_section("schema_compliance"),
        "property_validation": loader.get_section("property_validation"),
        "text_quality": loader.get_section("text_quality"),
        "author_voice": loader.get_section("author_voice"),
        "validation_severity": loader.get_section("validation_severity"),
        "fail_fast": loader.get_section("fail_fast")
    }

# Additional convenience functions for MaterialAuditor compatibility

def is_prohibited_field_in_materials(field: str) -> bool:
    """Check if field is prohibited in Materials.yaml (MaterialAuditor compatibility)"""
    loader = RequirementsLoader()
    return loader.is_prohibited_field_in_materials(field)

def get_author_voice_indicators(country: str) -> Dict[str, Any]:
    """Get author voice indicators for country (MaterialAuditor compatibility)"""
    loader = RequirementsLoader()
    return loader.get_author_voice_requirements(country)

def get_essential_properties(category: str) -> List[str]:
    """Get essential properties for category (MaterialAuditor compatibility)"""
    loader = RequirementsLoader()
    return loader.get_essential_properties(category)

def get_minimum_property_coverage(category: str) -> float:
    """Get minimum property coverage for category (MaterialAuditor compatibility)"""
    loader = RequirementsLoader()
    return loader.get_minimum_property_coverage(category)

def get_terminal_report_config() -> Dict[str, Any]:
    """Get terminal report configuration (MaterialAuditor compatibility)"""
    loader = RequirementsLoader()
    return loader.get_audit_report_config()