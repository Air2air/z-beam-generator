#!/usr/bin/env python3
"""
Material Auditing System - Comprehensive Requirements Compliance Checker

This system runs post-processing audits after any material update to ensure
full compliance with all Z-Beam Generator requirements.

CRITICAL DESIGN PRINCIPLES:
1. Zero tolerance for requirement violations
2. Fail-fast on critical compliance issues
3. Comprehensive coverage of all system requirements
4. Detailed audit trails and reporting
5. Automatic remediation where possible

Requirements Checked:
- Data Storage Policy compliance (Materials.yaml single source of truth)
- Data Architecture requirements (ranges vs values separation)
- Property structure validation (no min/max in materials)
- Category consistency and capitalization
- Required property coverage per category
- Qualitative vs quantitative property separation
- Schema compliance for generated frontmatter
- Confidence thresholds and source attribution
- Nested structure handling (thermalDestruction)
- Two-category taxonomy compliance
- Text content quality validation (hard line breaks, formatting, author voice)
- Terminal audit reporting after material generation
"""

import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.validation.schema_validator import SchemaValidator
from materials.data.materials import load_materials
from shared.utils.requirements_loader import (
    RequirementsLoader, 
    is_prohibited_field_in_materials,
    is_prohibited_source,
    get_author_voice_indicators,
    get_essential_properties,
    get_minimum_property_coverage,
    get_text_quality_requirements,
    get_terminal_report_config
)


class AuditSeverity(Enum):
    """Audit issue severity levels"""
    CRITICAL = "CRITICAL"      # Architectural violations - system fails
    HIGH = "HIGH"              # Major requirement violations
    MEDIUM = "MEDIUM"          # Best practice violations
    LOW = "LOW"                # Style/optimization suggestions
    INFO = "INFO"              # Informational findings


@dataclass
class AuditIssue:
    """Individual audit issue"""
    severity: AuditSeverity
    category: str
    description: str
    field_path: str = ""
    expected_value: Any = None
    actual_value: Any = None
    remediation: str = ""
    requirement_source: str = ""


@dataclass
class MaterialAuditResult:
    """Complete audit result for a material"""
    material_name: str
    audit_timestamp: str
    overall_status: str  # PASS, FAIL, WARNING
    total_issues: int
    critical_issues: int
    high_issues: int
    issues: List[AuditIssue] = field(default_factory=list)
    
    # Detailed metrics
    data_storage_compliance: bool = True
    architecture_compliance: bool = True
    schema_compliance: bool = True
    property_coverage: float = 0.0
    confidence_score: float = 0.0
    
    # Performance metrics
    audit_duration_ms: int = 0
    requirements_checked: int = 0
    auto_fixes_applied: int = 0


class MaterialAuditor:
    """
    Comprehensive material auditing system ensuring full requirements compliance.
    
    This auditor checks ALL system requirements after material updates:
    - Data Storage Policy compliance
    - Data Architecture requirements  
    - Schema validation
    - Property coverage and quality
    - Category consistency
    - Fail-fast architecture compliance
    """
    
    def __init__(self):
        """Initialize the material auditor with all requirement checkers"""
        self.logger = logging.getLogger(__name__)
        self.materials_file = Path("materials/data/Materials.yaml")
        self.categories_file = Path("materials/data/Categories.yaml")
        self.frontmatter_dir = Path("frontmatter")
        
        # Load reference data
        self._load_reference_data()
        
        # Initialize validators
        # Initialize validation system
        self.schema_validator = SchemaValidator(strict_mode=True)
        
        # Audit metrics
        self.audit_stats = {
            'total_audits': 0,
            'total_issues': 0,
            'critical_violations': 0,
            'auto_fixes': 0
        }
    
    def _load_reference_data(self) -> None:
        """Load reference data for auditing"""
        try:
            # Load Categories.yaml for validation
            with open(self.categories_file) as f:
                self.categories_data = yaml.safe_load(f)
            
            # Load Materials.yaml for validation
            with open(self.materials_file) as f:
                self.materials_data = yaml.safe_load(f)
                
            # Extract category definitions
            self.category_definitions = self.categories_data.get('categories', {})
            
            # Essential properties by category
            self.essential_properties = self._build_essential_properties_map()
            
            self.logger.info("✅ Reference data loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load reference data: {e}")
            raise
    
    def _build_essential_properties_map(self) -> Dict[str, Set[str]]:
        """Build map of essential properties by category"""
        essential_map = {}
        
        for category_name, category_data in self.category_definitions.items():
            essential_props = set()
            
            # Extract from category_ranges
            if 'category_ranges' in category_data:
                essential_props.update(category_data['category_ranges'].keys())
            
            # Add other property sections
            for section in ['electricalProperties', 'processingParameters', 'chemicalProperties']:
                if section in category_data:
                    essential_props.update(category_data[section].keys())
            
            essential_map[category_name] = essential_props
        
        return essential_map
    
    def audit_material(
        self, 
        material_name: str, 
        auto_fix: bool = False,
        skip_frontmatter: bool = False
    ) -> MaterialAuditResult:
        """
        Perform comprehensive audit of a material entry.
        
        Args:
            material_name: Name of material to audit
            auto_fix: Whether to automatically fix issues where possible
            skip_frontmatter: Skip frontmatter validation (for speed)
            
        Returns:
            Complete audit result with all findings
            
        Raises:
            AuditError: If critical audit infrastructure fails
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"🔍 Starting comprehensive audit for {material_name}")
            
            # Initialize result
            result = MaterialAuditResult(
                material_name=material_name,
                audit_timestamp=start_time.isoformat(),
                overall_status="PASS",
                total_issues=0,
                critical_issues=0,
                high_issues=0
            )
            
            # === CRITICAL REQUIREMENT CHECKS ===
            
            # 1. Data Storage Policy Compliance (CRITICAL)
            self._audit_data_storage_policy(material_name, result)
            
            # 2. Data Architecture Compliance (CRITICAL)
            self._audit_data_architecture(material_name, result)
            
            # 3. Material Structure Validation (HIGH)
            self._audit_material_structure(material_name, result)
            
            # 4. Property Coverage Analysis (HIGH)
            self._audit_property_coverage(material_name, result)
            
            # 5. Category Consistency (MEDIUM)
            self._audit_category_consistency(material_name, result)
            
            # 6. Confidence and Source Validation (MEDIUM)
            self._audit_confidence_sources(material_name, result)
            
            # 7. Schema Compliance (if frontmatter exists)
            if not skip_frontmatter:
                self._audit_schema_compliance(material_name, result)
            
            # 8. Fail-Fast Architecture Compliance (CRITICAL)
            self._audit_fail_fast_compliance(material_name, result)
            
            # 9. Text Content Quality Validation (HIGH)
            self._audit_text_content_quality(material_name, result)
            
            # === AUTO-REMEDIATION ===
            if auto_fix and result.issues:
                self._apply_auto_fixes(material_name, result)
            
            # === FINALIZE RESULT ===
            self._finalize_audit_result(result, start_time)
            
            # Update audit statistics
            self._update_audit_stats(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Critical audit failure for {material_name}: {e}")
            raise AuditError(f"Audit infrastructure failure: {e}")
    
    def _audit_data_storage_policy(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit Data Storage Policy compliance (CRITICAL).
        
        Requirements:
        - Materials.yaml is single source of truth for material data
        - No min/max ranges in material properties (ZERO TOLERANCE)
        - Only value, unit, confidence, description, source allowed
        - Frontmatter files are OUTPUT ONLY
        """
        try:
            material_data = self.materials_data.get('materials', {}).get(material_name)
            
            if not material_data:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.CRITICAL,
                    category="data_storage_policy",
                    description=f"Material '{material_name}' not found in Materials.yaml",
                    remediation="Add material to Materials.yaml as single source of truth",
                    requirement_source="docs/DATA_STORAGE_POLICY.md"
                ))
                result.data_storage_compliance = False
                return
            
            # Check for prohibited min/max ranges in material properties
            properties = material_data.get('materialProperties', {})
            
            for prop_name, prop_data in properties.items():
                if isinstance(prop_data, dict):
                    # CRITICAL: Check for min/max in material properties (ZERO TOLERANCE)
                    for field in prop_data.keys():
                        if is_prohibited_field_in_materials(field):
                            result.issues.append(AuditIssue(
                                severity=AuditSeverity.CRITICAL,
                                category="data_storage_policy",
                                description=f"ARCHITECTURAL VIOLATION: Property '{prop_name}' has '{field}' field in Materials.yaml",
                                field_path=f"materials.{material_name}.properties.{prop_name}.{field}",
                                actual_value=prop_data[field],
                                expected_value="REMOVED - ranges belong in Categories.yaml only",
                                remediation=f"Remove '{field}' from Materials.yaml property - ranges come from Categories.yaml",
                                requirement_source="docs/DATA_STORAGE_POLICY.md - ZERO TOLERANCE rule"
                            ))
                            result.data_storage_compliance = False
                    
                    # Validate allowed fields only
                    allowed_fields = {'value', 'unit', 'description', 'source', 
                                    'last_updated', 'point', 'type', 'ai_verified'}
                    
                    for field in prop_data.keys():
                        if field not in allowed_fields:
                            result.issues.append(AuditIssue(
                                severity=AuditSeverity.HIGH,
                                category="data_storage_policy",
                                description=f"Unexpected field '{field}' in property '{prop_name}'",
                                field_path=f"materials.{material_name}.properties.{prop_name}.{field}",
                                remediation="Remove non-standard field or add to allowed fields list",
                                requirement_source="docs/DATA_STORAGE_POLICY.md"
                            ))
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Data storage policy audit failed: {e}",
                remediation="Fix audit infrastructure"
            ))
    
    def _audit_data_architecture(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit Data Architecture compliance (CRITICAL).
        
        Requirements:
        - Categories.yaml contains all category ranges
        - Materials.yaml contains only material values
        - Nested structures handled correctly (thermalDestruction)
        - Category capitalization (lowercase in data)
        """
        try:
            material_data = self.materials_data.get('materials', {}).get(material_name)
            if not material_data:
                return
            
            # Check category exists and is lowercase
            category = material_data.get('category')
            if not category:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.CRITICAL,
                    category="data_architecture",
                    description="Material missing category field",
                    field_path=f"materials.{material_name}.category",
                    remediation="Add category field with lowercase category name",
                    requirement_source="docs/DATA_ARCHITECTURE.md"
                ))
                result.architecture_compliance = False
                return
            
            # Validate category is lowercase
            if category != category.lower():
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.HIGH,
                    category="data_architecture",
                    description=f"Category should be lowercase: '{category}' -> '{category.lower()}'",
                    field_path=f"materials.{material_name}.category",
                    actual_value=category,
                    expected_value=category.lower(),
                    remediation="Change category to lowercase",
                    requirement_source="docs/DATA_ARCHITECTURE.md"
                ))
            
            # Validate category exists in Categories.yaml
            if category not in self.category_definitions:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.CRITICAL,
                    category="data_architecture",
                    description=f"Category '{category}' not defined in Categories.yaml",
                    field_path=f"materials.{material_name}.category",
                    remediation=f"Add '{category}' category definition to Categories.yaml",
                    requirement_source="docs/DATA_ARCHITECTURE.md"
                ))
                result.architecture_compliance = False
            
            # Check properties are defined in category
            properties = material_data.get('materialProperties', {})
            category_ranges = self.category_definitions.get(category, {}).get('category_ranges', {})
            
            for prop_name in properties:
                # Skip nested properties (handled separately)
                if prop_name == 'thermalDestruction':
                    continue
                
                # Check if property is defined in category ranges
                if prop_name not in category_ranges:
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.HIGH,
                        category="data_architecture",
                        description=f"Property '{prop_name}' not defined in category '{category}' ranges",
                        field_path=f"materials.{material_name}.properties.{prop_name}",
                        remediation=f"Add '{prop_name}' to Categories.yaml category_ranges for '{category}' or remove from material",
                        requirement_source="docs/DATA_ARCHITECTURE.md - Property validation rule"
                    ))
            
            # Validate nested thermalDestruction structure
            if 'thermalDestruction' in properties:
                thermal_data = properties['thermalDestruction']
                if isinstance(thermal_data, dict):
                    if 'point' not in thermal_data or 'type' not in thermal_data:
                        result.issues.append(AuditIssue(
                            severity=AuditSeverity.HIGH,
                            category="data_architecture",
                            description="thermalDestruction missing required nested structure (point/type)",
                            field_path=f"materials.{material_name}.properties.thermalDestruction",
                            expected_value={"point": {"value": "...", "unit": "..."}, "type": "..."},
                            remediation="Use nested structure: {point: {value, unit}, type: 'melting'}",
                            requirement_source="docs/DATA_ARCHITECTURE.md - Nested structure requirement"
                        ))
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Data architecture audit failed: {e}",
                remediation="Fix audit infrastructure"
            ))
    
    def _audit_material_structure(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit material structure requirements (HIGH).
        
        Requirements:
        - Required fields present (name, category, properties)
        - Property structure valid (value, unit, confidence, etc.)
        - No empty or null values in critical fields
        """
        try:
            material_data = self.materials_data.get('materials', {}).get(material_name)
            if not material_data:
                return
            
            # Check required top-level fields
            required_fields = ['category']
            for field in required_fields:
                if field not in material_data:
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.HIGH,
                        category="material_structure",
                        description=f"Missing required field: {field}",
                        field_path=f"materials.{material_name}.{field}",
                        remediation=f"Add required field '{field}'",
                        requirement_source="System architecture requirements"
                    ))
            
            # Validate properties structure
            properties = material_data.get('materialProperties', {})
            if not properties:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.HIGH,
                    category="material_structure",
                    description="Material has no properties defined",
                    field_path=f"materials.{material_name}.properties",
                    remediation="Add material properties with research or discovery",
                    requirement_source="Material completeness requirements"
                ))
                return
            
            # Validate each property structure
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict):
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.HIGH,
                        category="material_structure",
                        description=f"Property '{prop_name}' is not a dictionary",
                        field_path=f"materials.{material_name}.properties.{prop_name}",
                        actual_value=type(prop_data).__name__,
                        expected_value="dict",
                        remediation="Convert property to dictionary with value, unit, confidence fields",
                        requirement_source="Property structure requirements"
                    ))
                    continue
                
                # Check for required property fields (except nested structures)
                if prop_name != 'thermalDestruction':
                    required_prop_fields = ['value', 'unit']
                    for field in required_prop_fields:
                        if field not in prop_data:
                            result.issues.append(AuditIssue(
                                severity=AuditSeverity.MEDIUM,
                                category="material_structure",
                                description=f"Property '{prop_name}' missing field: {field}",
                                field_path=f"materials.{material_name}.properties.{prop_name}.{field}",
                                remediation=f"Add '{field}' to property structure",
                                requirement_source="Property completeness requirements"
                            ))
                
                # Check confidence scores
                confidence = prop_data.get('confidence')
                if confidence is not None:
                    if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 100):
                        result.issues.append(AuditIssue(
                            severity=AuditSeverity.MEDIUM,
                            category="material_structure",
                            description=f"Property '{prop_name}' has invalid confidence: {confidence}",
                            field_path=f"materials.{material_name}.properties.{prop_name}.confidence",
                            actual_value=confidence,
                            expected_value="0-100 numeric value",
                            remediation="Set confidence to valid 0-100 range",
                            requirement_source="Confidence scoring requirements"
                        ))
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Material structure audit failed: {e}",
                remediation="Fix audit infrastructure"
            ))
    
    def _audit_property_coverage(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit property coverage requirements (HIGH).
        
        Requirements:
        - Essential properties covered for category
        - Reasonable property count (not too sparse)
        - Mix of property types appropriate for category
        """
        try:
            material_data = self.materials_data.get('materials', {}).get(material_name)
            if not material_data:
                return
            
            category = material_data.get('category')
            if not category:
                return
            
            properties = set(material_data.get('materialProperties', {}).keys())
            essential_props = self.essential_properties.get(category, set())
            
            # Calculate coverage
            if essential_props:
                coverage = len(properties & essential_props) / len(essential_props)
                result.property_coverage = coverage * 100
                
                # Check minimum coverage
                if coverage < 0.5:  # Less than 50% essential coverage
                    missing_props = essential_props - properties
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.HIGH,
                        category="property_coverage",
                        description=f"Low essential property coverage: {coverage:.1%} (missing: {', '.join(sorted(missing_props))})",
                        field_path=f"materials.{material_name}.properties",
                        actual_value=f"{coverage:.1%}",
                        expected_value="≥50% essential properties",
                        remediation=f"Research and add missing essential properties: {', '.join(sorted(list(missing_props)[:3]))}",
                        requirement_source="Property completeness requirements"
                    ))
                elif coverage < 0.8:  # Less than 80% coverage
                    missing_props = essential_props - properties
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.MEDIUM,
                        category="property_coverage",
                        description=f"Moderate essential property coverage: {coverage:.1%}",
                        field_path=f"materials.{material_name}.properties",
                        remediation=f"Consider adding: {', '.join(sorted(list(missing_props)[:3]))}",
                        requirement_source="Property completeness best practices"
                    ))
            
            # Check total property count
            total_props = len(properties)
            if total_props < 5:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.MEDIUM,
                    category="property_coverage", 
                    description=f"Low total property count: {total_props}",
                    field_path=f"materials.{material_name}.properties",
                    actual_value=total_props,
                    expected_value="≥5 properties",
                    remediation="Research and add more material properties",
                    requirement_source="Material completeness guidelines"
                ))
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Property coverage audit failed: {e}",
                remediation="Fix audit infrastructure"
            ))
    
    def _audit_category_consistency(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit category consistency requirements (MEDIUM).
        
        Requirements:
        - Category matches material type appropriately
        - Properties align with category expectations
        - No cross-category property mismatches
        """
        try:
            material_data = self.materials_data.get('materials', {}).get(material_name)
            if not material_data:
                return
            
            category = material_data.get('category', '').lower()
            properties = material_data.get('materialProperties', {})
            
            # Basic category validation
            valid_categories = set(self.category_definitions.keys())
            if category not in valid_categories:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.HIGH,
                    category="category_consistency",
                    description=f"Invalid category: '{category}'",
                    field_path=f"materials.{material_name}.category",
                    actual_value=category,
                    expected_value=f"One of: {', '.join(sorted(valid_categories))}",
                    remediation="Set category to valid category from Categories.yaml",
                    requirement_source="Category definition requirements"
                ))
            
            # Category-specific property expectations
            category_expectations = {
                'metal': {'thermalConductivity', 'density', 'hardness'},
                'plastic': {'density', 'thermalDestruction'},
                'ceramic': {'hardness', 'thermalDestruction'},
                'wood': {'density', 'thermalDestruction'},
                'glass': {'density', 'thermalDestruction'},
                'composite': {'density', 'tensileStrength'},
                'stone': {'density', 'hardness'},
                'semiconductor': {'thermalConductivity', 'density'},
                'masonry': {'density', 'thermalDestruction'}
            }
            
            expected_props = category_expectations.get(category, set())
            actual_props = set(properties.keys())
            
            # Check for expected properties
            missing_expected = expected_props - actual_props
            if missing_expected and len(missing_expected) > len(expected_props) / 2:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.MEDIUM,
                    category="category_consistency",
                    description=f"Missing typical {category} properties: {', '.join(sorted(missing_expected))}",
                    field_path=f"materials.{material_name}.properties",
                    remediation=f"Consider researching typical {category} properties",
                    requirement_source="Category-specific property expectations"
                ))
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Category consistency audit failed: {e}",
                remediation="Fix audit infrastructure"
            ))
    
    def _audit_confidence_sources(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit confidence and source requirements (MEDIUM).
        
        Requirements:
        - Properties have confidence scores
        - Confidence scores are reasonable (not all 100% or all low)
        - Sources are attributed for research
        - AI research is properly marked
        """
        try:
            material_data = self.materials_data.get('materials', {}).get(material_name)
            if not material_data:
                return
            
            properties = material_data.get('materialProperties', {})
            if not properties:
                return
            
            confidence_scores = []
            missing_confidence = []
            missing_source = []
            
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Skip nested structures
                if prop_name == 'thermalDestruction':
                    continue
                
                # Check confidence
                confidence = prop_data.get('confidence')
                if confidence is None:
                    missing_confidence.append(prop_name)
                else:
                    confidence_scores.append(confidence)
                
                # Check source for research-based properties
                source = prop_data.get('source')
                if not source:
                    missing_source.append(prop_name)
            
            # Analyze confidence patterns
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                result.confidence_score = avg_confidence
                
                # Check for suspicious patterns
                if avg_confidence > 95:
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.LOW,
                        category="confidence_sources",
                        description=f"Very high average confidence: {avg_confidence:.1f}% (may indicate overconfidence)",
                        remediation="Review confidence scores for realism",
                        requirement_source="Confidence scoring best practices"
                    ))
                elif avg_confidence < 70:
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.MEDIUM,
                        category="confidence_sources",
                        description=f"Low average confidence: {avg_confidence:.1f}% (may need better research)",
                        remediation="Improve research quality or sources",
                        requirement_source="Data quality requirements"
                    ))
            
            # Report missing metadata
            if missing_confidence:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.MEDIUM,
                    category="confidence_sources",
                    description=f"Properties missing confidence scores: {', '.join(missing_confidence[:5])}",
                    remediation="Add confidence scores to all properties",
                    requirement_source="Property metadata requirements"
                ))
            
            if missing_source:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.MEDIUM,
                    category="confidence_sources",
                    description=f"Properties missing source attribution: {', '.join(missing_source[:5])}",
                    remediation="Add source attribution to research-based properties",
                    requirement_source="Research traceability requirements"
                ))
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Confidence/source audit failed: {e}",
                remediation="Fix audit infrastructure"
            ))
    
    def _audit_schema_compliance(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit schema compliance for generated frontmatter (MEDIUM).
        
        Requirements:
        - Generated frontmatter passes schema validation
        - Required fields present and properly structured
        - Data types match schema expectations
        """
        try:
            # Check if frontmatter file exists
            frontmatter_file = self.frontmatter_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
            
            if not frontmatter_file.exists():
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.INFO,
                    category="schema_compliance",
                    description="No frontmatter file exists for validation",
                    field_path=str(frontmatter_file),
                    remediation="Generate frontmatter to validate schema compliance",
                    requirement_source="Frontmatter generation requirements"
                ))
                return
            
            # Load and validate frontmatter
            with open(frontmatter_file) as f:
                frontmatter_data = yaml.safe_load(f)
            
            if not frontmatter_data:
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.HIGH,
                    category="schema_compliance",
                    description="Frontmatter file is empty or invalid YAML",
                    field_path=str(frontmatter_file),
                    remediation="Regenerate frontmatter with valid content",
                    requirement_source="YAML structure requirements"
                ))
                return
            
            # Run schema validation
            validation_result = self.schema_validator.validate(frontmatter_data, material_name)
            
            if not validation_result.is_valid:
                # Categorize schema violations by severity
                critical_errors = []
                high_errors = []
                medium_errors = []
                
                for error in validation_result.errors:
                    error_msg = error.message if hasattr(error, 'message') else str(error)
                    
                    # Categorize by error type
                    if any(keyword in error_msg.lower() for keyword in ['required', 'missing', 'null']):
                        critical_errors.append(error_msg)
                    elif any(keyword in error_msg.lower() for keyword in ['type', 'format', 'pattern']):
                        high_errors.append(error_msg)
                    else:
                        medium_errors.append(error_msg)
                
                # Add issues by severity
                for error_msg in critical_errors:
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.CRITICAL,
                        category="schema_compliance",
                        description=f"Critical schema violation: {error_msg}",
                        field_path=str(frontmatter_file),
                        remediation="Fix required field or structure issue",
                        requirement_source="Frontmatter schema requirements"
                    ))
                
                for error_msg in high_errors:
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.HIGH,
                        category="schema_compliance",
                        description=f"Schema type violation: {error_msg}",
                        field_path=str(frontmatter_file),
                        remediation="Fix data type or format issue",
                        requirement_source="Frontmatter schema requirements"
                    ))
                
                for error_msg in medium_errors:
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.MEDIUM,
                        category="schema_compliance",
                        description=f"Schema compliance issue: {error_msg}",
                        field_path=str(frontmatter_file),
                        remediation="Review and fix schema compliance",
                        requirement_source="Frontmatter schema requirements"
                    ))
                
                result.schema_compliance = False
            else:
                result.schema_compliance = True
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Schema compliance audit failed: {e}",
                remediation="Fix audit infrastructure or schema validator"
            ))
    
    def _audit_fail_fast_compliance(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit fail-fast architecture compliance (CRITICAL).
        
        Requirements:
        - No mock values or fallbacks in production data
        - No skip logic or dummy values
        - Proper error handling indicators
        - No silent failure patterns
        """
        try:
            material_data = self.materials_data.get('materials', {}).get(material_name)
            if not material_data:
                return
            
            properties = material_data.get('materialProperties', {})
            
            # Check for fail-fast violations
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Check for mock/fallback patterns
                source = prop_data.get('source', '').lower()
                value = prop_data.get('value')
                
                # Check for prohibited source patterns
                if is_prohibited_source(source):
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.CRITICAL,
                        category="fail_fast_compliance",
                        description=f"ARCHITECTURAL VIOLATION: Property '{prop_name}' has prohibited source: '{source}'",
                        field_path=f"materials.{material_name}.properties.{prop_name}.source",
                        actual_value=source,
                        expected_value="Real data source (ai_research, handbook, database, etc.)",
                        remediation="Remove mock/fallback source - use real research data",
                        requirement_source=".github/copilot-instructions.md - Zero tolerance for mocks in production"
                    ))
                
                # Check for suspicious values
                if isinstance(value, str):
                    suspicious_values = ['todo', 'tbd', 'unknown', 'placeholder', 'n/a', 'default']
                    if any(pattern in str(value).lower() for pattern in suspicious_values):
                        result.issues.append(AuditIssue(
                            severity=AuditSeverity.HIGH,
                            category="fail_fast_compliance",
                            description=f"Property '{prop_name}' has suspicious placeholder value",
                            field_path=f"materials.{material_name}.properties.{prop_name}.value",
                            actual_value=value,
                            remediation="Replace with researched real value",
                            requirement_source="Fail-fast data quality requirements"
                        ))
                
                # Check for zero confidence (potential failure)
                confidence = prop_data.get('confidence', 0)
                if confidence == 0:
                    result.issues.append(AuditIssue(
                        severity=AuditSeverity.MEDIUM,
                        category="fail_fast_compliance",
                        description=f"Property '{prop_name}' has zero confidence (potential data quality issue)",
                        field_path=f"materials.{material_name}.properties.{prop_name}.confidence",
                        actual_value=confidence,
                        remediation="Research and set appropriate confidence level",
                        requirement_source="Data quality assurance requirements"
                    ))
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Fail-fast compliance audit failed: {e}",
                remediation="Fix audit infrastructure"
            ))
    
    def _audit_text_content_quality(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Audit text content quality requirements (HIGH).
        
        Requirements:
        1. Hard line breaks in text (no long continuous lines)
        2. Correct formatting (no markdown artifacts, proper YAML structure)
        3. Author nationality voice application verification
        4. Professional language and terminology consistency
        """
        try:
            # Check if frontmatter file exists for text content analysis
            frontmatter_file = self.frontmatter_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
            
            if not frontmatter_file.exists():
                result.issues.append(AuditIssue(
                    severity=AuditSeverity.INFO,
                    category="text_content_quality",
                    description="No frontmatter file exists for text content audit",
                    field_path=str(frontmatter_file),
                    remediation="Generate frontmatter to validate text content quality",
                    requirement_source="Text content quality requirements"
                ))
                return
            
            # Load frontmatter for text analysis
            with open(frontmatter_file) as f:
                frontmatter_data = yaml.safe_load(f)
            
            if not frontmatter_data:
                return
            
            # Get author information
            author_info = frontmatter_data.get('author', {})
            author_country = author_info.get('country', '').lower()
            
            # Define text fields to analyze
            text_fields_to_check = [
                ('description', frontmatter_data.get('description', '')),
                ('subtitle', frontmatter_data.get('subtitle', ''))
            ]
            
            # Add environmental impact descriptions
            env_impacts = frontmatter_data.get('environmentalImpact', [])
            for i, impact in enumerate(env_impacts):
                if isinstance(impact, dict):
                    desc = impact.get('description', '')
                    if desc:
                        text_fields_to_check.append((f'environmentalImpact[{i}].description', desc))
                    
                    quant_benefits = impact.get('quantifiedBenefits', '')
                    if quant_benefits:
                        text_fields_to_check.append((f'environmentalImpact[{i}].quantifiedBenefits', quant_benefits))
            
            # Add outcome metrics descriptions
            outcome_metrics = frontmatter_data.get('outcomeMetrics', [])
            for i, metric in enumerate(outcome_metrics):
                if isinstance(metric, dict):
                    desc = metric.get('description', '')
                    if desc:
                        text_fields_to_check.append((f'outcomeMetrics[{i}].description', desc))
            
            # Add material property descriptions
            mat_props = frontmatter_data.get('materialProperties', {})
            for prop_group, group_data in mat_props.items():
                if isinstance(group_data, dict):
                    group_desc = group_data.get('description', '')
                    if group_desc:
                        text_fields_to_check.append((f'materialProperties.{prop_group}.description', group_desc))
                    
                    # Properties are directly in group_data (flat structure, excluding metadata)
                    metadata_keys = {'label', 'description', 'percentage'}
                    for prop_name, prop_data in group_data.items():
                        if prop_name not in metadata_keys and isinstance(prop_data, dict):
                            prop_desc = prop_data.get('description', '')
                            if prop_desc:
                                text_fields_to_check.append((f'materialProperties.{prop_group}.{prop_name}.description', prop_desc))
            
            # Analyze each text field
            for field_path, text_content in text_fields_to_check:
                if not text_content or not isinstance(text_content, str):
                    continue
                
                # Get text quality requirements from comprehensive centralized config
                from shared.utils.requirements_loader import RequirementsLoader
                loader = RequirementsLoader()
                
                max_line_length = loader.get_max_line_length()
                hard_breaks_required = loader.should_use_hard_line_breaks()
                
                # 1. Check for hard line breaks 
                if hard_breaks_required:
                    lines = text_content.split('\n')
                    long_lines = [(i+1, len(line.strip())) for i, line in enumerate(lines) if len(line.strip()) > max_line_length]
                    
                    if long_lines:
                        line_details = ", ".join([f"line {num}({length})" for num, length in long_lines[:3]])
                        result.issues.append(AuditIssue(
                            severity=AuditSeverity.HIGH,
                            category="text_content_quality",
                            description=f"Text field '{field_path}' contains lines exceeding {max_line_length} characters ({line_details})",
                            field_path=field_path,
                            actual_value=f"{len(long_lines)} long lines",
                            expected_value=f"Lines ≤{max_line_length} characters for proper YAML formatting",
                            remediation=f"Add hard line breaks to keep lines under {max_line_length} characters",
                            requirement_source="text_quality.line_formatting.max_line_length"
                        ))
                
                # 2. Check for formatting issues using comprehensive requirements
                formatting_issues = []
                
                # Check for prohibited markdown patterns
                markdown_patterns = loader.get_prohibited_text_patterns("markdown")
                for pattern in markdown_patterns:
                    if pattern in text_content:
                        formatting_issues.append(f"Contains prohibited markdown pattern '{pattern}'")
                
                # Check for placeholder patterns (critical issue)
                placeholder_patterns = loader.get_prohibited_text_patterns("placeholders")
                for pattern in placeholder_patterns:
                    if pattern.lower() in text_content.lower():
                        result.issues.append(AuditIssue(
                            severity=AuditSeverity.CRITICAL,
                            category="text_content_quality",
                            description=f"Text field '{field_path}' contains placeholder text: {pattern}",
                            field_path=field_path,
                            actual_value=pattern,
                            expected_value="Actual content",
                            remediation=f"Replace placeholder '{pattern}' with actual content",
                            requirement_source="text_quality.prohibited_patterns.placeholders"
                        ))
                
                # Check quality indicators
                quality_indicators = loader.get_prohibited_text_patterns("quality_indicators")
                if quality_indicators:
                    suspicious_phrases = quality_indicators.get("suspicious_phrases", [])
                    for phrase in suspicious_phrases:
                        if phrase.lower() in text_content.lower():
                            formatting_issues.append(f"Contains suspicious phrase '{phrase}'")
                
                # Check for double spaces or excessive whitespace
                if '  ' in text_content:
                    formatting_issues.append("Contains double spaces")
                
                if text_content != text_content.strip():
                    formatting_issues.append("Contains leading/trailing whitespace")
                
                # Check for improper capitalization (sentences should start with capital)
                sentences = [s.strip() for s in text_content.split('. ') if s.strip()]
                for sentence in sentences[:3]:  # Check first 3 sentences only
                    if sentence and not sentence[0].isupper():
                        formatting_issues.append(f"Sentence doesn't start with capital: '{sentence[:30]}...'")
                        break  # Only report first instance
                
                # Check minimum text length
                min_length = loader.get_minimum_text_length("description")
                if "description" in field_path and len(text_content) < min_length:
                    formatting_issues.append(f"Text too short ({len(text_content)} < {min_length} characters)")
                
                if formatting_issues:
                    # Determine severity based on issue types
                    severity = AuditSeverity.HIGH if any("placeholder" in issue.lower() for issue in formatting_issues) else AuditSeverity.MEDIUM
                    
                    result.issues.append(AuditIssue(
                        severity=severity,
                        category="text_content_quality",
                        description=f"Text field '{field_path}' has formatting issues: {'; '.join(formatting_issues[:3])}",
                        field_path=field_path,
                        remediation="Fix formatting: remove markdown artifacts, fix capitalization, clean whitespace, expand content",
                        requirement_source="text_quality.formatting_rules"
                    ))
                
                # 3. Check for author nationality voice application using comprehensive requirements
                if author_country:
                    voice_requirements = loader.get_author_voice_requirements(author_country)
                    
                    if voice_requirements:
                        # Get voice detection thresholds from comprehensive config
                        min_strength = loader.get_voice_strength_threshold(author_country)
                        min_authenticity = loader.get_voice_authenticity_minimum(author_country)
                        min_indicators = loader.get_minimum_voice_indicators(author_country)
                        
                        # Detect voice characteristics
                        voice_detected = self._detect_author_voice_characteristics(text_content, voice_requirements)
                        
                        if not voice_detected['has_indicators']:
                            # Get specific vocabulary suggestions
                            primary_vocab = loader.get_author_vocabulary_indicators(author_country, "primary")
                            sentence_patterns = loader.get_author_sentence_patterns(author_country)
                            
                            result.issues.append(AuditIssue(
                                severity=AuditSeverity.HIGH,
                                category="text_content_quality", 
                                description=f"Text field '{field_path}' does not reflect {author_country.title()} author voice characteristics",
                                field_path=field_path,
                                actual_value="Generic/neutral voice detected",
                                expected_value=f"{author_country.title()} linguistic characteristics (≥{min_indicators} indicators)",
                                remediation=f"Apply {author_country.title()} vocabulary: {', '.join(primary_vocab[:3])} and patterns: {sentence_patterns[0] if sentence_patterns else 'systematic approach'}",
                                requirement_source=f"author_voice.countries.{author_country}.validation_thresholds"
                            ))
                        elif voice_detected['strength'] < min_strength:
                            # Get secondary vocabulary for strengthening suggestions
                            secondary_vocab = loader.get_author_vocabulary_indicators(author_country, "secondary")
                            
                            result.issues.append(AuditIssue(
                                severity=AuditSeverity.MEDIUM,
                                category="text_content_quality",
                                description=f"Text field '{field_path}' has weak {author_country.title()} voice characteristics (strength: {voice_detected['strength']:.1%}, required: {min_strength:.1%})",
                                field_path=field_path,
                                actual_value=f"Voice strength: {voice_detected['strength']:.1%}",
                                expected_value=f"Voice strength: ≥{min_strength:.1%}",
                                remediation=f"Strengthen {author_country.title()} voice with: {', '.join(secondary_vocab[:3])}",
                                requirement_source=f"author_voice.countries.{author_country}.validation_thresholds.strength_threshold"
                            ))
            
        except Exception as e:
            result.issues.append(AuditIssue(
                severity=AuditSeverity.CRITICAL,
                category="audit_infrastructure",
                description=f"Text content quality audit failed: {e}",
                remediation="Fix text content audit infrastructure"
            ))
    
    def _get_nationality_voice_indicators(self, country: str) -> Dict[str, Any]:
        """
        Get linguistic indicators for different nationalities using comprehensive requirements.
        
        Args:
            country: Author's country (lowercase)
            
        Returns:
            Dictionary with voice indicators and patterns to detect
        """
        from shared.utils.requirements_loader import RequirementsLoader
        loader = RequirementsLoader()
        return loader.get_author_voice_requirements(country)
    
    def _detect_author_voice_characteristics(self, text: str, voice_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect author voice characteristics in text using comprehensive requirements.
        
        Args:
            text: Text content to analyze
            voice_requirements: Complete voice requirements from comprehensive config
            
        Returns:
            Dictionary with detection results
        """
        text_lower = text.lower()
        
        # Get vocabulary indicators from comprehensive structure
        vocab_indicators = voice_requirements.get('vocabulary_indicators', {})
        primary_vocab = vocab_indicators.get('primary', [])
        secondary_vocab = vocab_indicators.get('secondary', [])
        all_vocab = primary_vocab + secondary_vocab
        
        # Count vocabulary matches
        vocab_matches = sum(1 for indicator in all_vocab if indicator in text_lower)
        vocab_ratio = vocab_matches / len(all_vocab) if all_vocab else 0
        
        # Count primary vocabulary matches (more important)
        primary_matches = sum(1 for indicator in primary_vocab if indicator in text_lower)
        primary_ratio = primary_matches / len(primary_vocab) if primary_vocab else 0
        
        # Count sentence pattern indicators
        sentence_patterns = voice_requirements.get('sentence_patterns', [])
        pattern_matches = sum(1 for pattern in sentence_patterns if pattern.lower() in text_lower)
        pattern_ratio = pattern_matches / len(sentence_patterns) if sentence_patterns else 0
        
        # Calculate overall voice strength (weighted toward primary vocabulary)
        voice_strength = (primary_ratio * 0.6 + vocab_ratio * 0.3 + pattern_ratio * 0.1)
        
        # Get thresholds from validation requirements
        validation_thresholds = voice_requirements.get('validation_thresholds', {})
        min_indicators = validation_thresholds.get('minimum_indicators', 2)
        
        # Determine if voice characteristics are present
        has_indicators = (primary_matches >= min_indicators) or (vocab_matches >= min_indicators and pattern_matches > 0)
        
        return {
            'has_indicators': has_indicators,
            'strength': voice_strength,
            'vocab_matches': vocab_matches,
            'primary_matches': primary_matches,
            'pattern_matches': pattern_matches,
            'vocab_ratio': vocab_ratio,
            'primary_ratio': primary_ratio,
            'pattern_ratio': pattern_ratio
        }
    
    def _apply_auto_fixes(self, material_name: str, result: MaterialAuditResult) -> None:
        """
        Apply automatic fixes for issues that can be safely resolved.
        
        ONLY applies fixes for:
        - Category capitalization (lowercase)
        - Missing confidence scores (add default based on source)
        - Basic field formatting issues
        
        NEVER fixes:
        - Min/max architectural violations (requires manual review)
        - Missing properties (requires research)
        - Schema violations (requires regeneration)
        """
        try:
            fixes_applied = 0
            material_data = self.materials_data.get('materials', {}).get(material_name)
            
            if not material_data:
                return
            
            # Fix 1: Category capitalization
            category = material_data.get('category', '')
            if category and category != category.lower():
                self.logger.info(f"🔧 Auto-fix: Correcting category capitalization for {material_name}")
                material_data['category'] = category.lower()
                fixes_applied += 1
                
                # Update the issue to mark as auto-fixed
                for issue in result.issues:
                    if issue.field_path.endswith('.category') and 'lowercase' in issue.description:
                        issue.description += " [AUTO-FIXED]"
                        issue.severity = AuditSeverity.INFO
            
            # Fix 2: Add basic confidence scores where missing
            properties = material_data.get('materialProperties', {})
            for prop_name, prop_data in properties.items():
                if isinstance(prop_data, dict) and 'confidence' not in prop_data:
                    source = prop_data.get('source', '').lower()
                    
                    # Assign confidence based on source
                    if 'ai_research' in source:
                        default_confidence = 85
                    elif any(term in source for term in ['handbook', 'database', 'nist']):
                        default_confidence = 95
                    elif 'literature' in source:
                        default_confidence = 80
                    else:
                        default_confidence = 75
                    
                    self.logger.info(f"🔧 Auto-fix: Adding confidence score {default_confidence} to {material_name}.{prop_name}")
                    prop_data['confidence'] = default_confidence
                    fixes_applied += 1
            
            # Save changes if any fixes were applied
            if fixes_applied > 0:
                self._save_materials_data()
                result.auto_fixes_applied = fixes_applied
                self.logger.info(f"✅ Applied {fixes_applied} auto-fixes for {material_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Auto-fix failed for {material_name}: {e}")
            result.issues.append(AuditIssue(
                severity=AuditSeverity.HIGH,
                category="auto_fix_failure",
                description=f"Auto-fix process failed: {e}",
                remediation="Manual intervention required"
            ))
    
    def _save_materials_data(self) -> None:
        """Save updated materials data back to file"""
        try:
            # Create backup
            backup_file = self.materials_file.with_suffix(
                f'.backup_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
            )
            import shutil
            shutil.copy2(self.materials_file, backup_file)
            
            # Save updated data
            with open(self.materials_file, 'w') as f:
                yaml.dump(self.materials_data, f, default_flow_style=False, indent=2, sort_keys=False)
            
            self.logger.info(f"💾 Materials.yaml updated (backup: {backup_file.name})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save Materials.yaml: {e}")
            raise
    
    def _finalize_audit_result(self, result: MaterialAuditResult, start_time: datetime) -> None:
        """Finalize audit result with summary statistics"""
        # Count issues by severity
        result.total_issues = len(result.issues)
        result.critical_issues = sum(1 for issue in result.issues if issue.severity == AuditSeverity.CRITICAL)
        result.high_issues = sum(1 for issue in result.issues if issue.severity == AuditSeverity.HIGH)
        
        # Determine overall status
        if result.critical_issues > 0:
            result.overall_status = "FAIL"
        elif result.high_issues > 0:
            result.overall_status = "WARNING"
        else:
            result.overall_status = "PASS"
        
        # Calculate performance metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        result.audit_duration_ms = int(duration)
        
        # Count requirements checked (estimated)
        result.requirements_checked = len([
            'data_storage_policy', 'data_architecture', 'material_structure',
            'property_coverage', 'category_consistency', 'confidence_sources',
            'schema_compliance', 'fail_fast_compliance', 'text_content_quality'
        ])
        
        self.logger.info(
            f"🔍 Audit complete for {result.material_name}: "
            f"{result.overall_status} ({result.total_issues} issues, {result.audit_duration_ms}ms)"
        )
    
    def _update_audit_stats(self, result: MaterialAuditResult) -> None:
        """Update global audit statistics"""
        self.audit_stats['total_audits'] += 1
        self.audit_stats['total_issues'] += result.total_issues
        self.audit_stats['critical_violations'] += result.critical_issues
        self.audit_stats['auto_fixes'] += result.auto_fixes_applied
    
    def generate_audit_report(self, result: MaterialAuditResult) -> str:
        """
        Generate comprehensive audit report.
        
        Args:
            result: Audit result to report on
            
        Returns:
            Formatted audit report string
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"MATERIAL AUDIT REPORT: {result.material_name}")
        lines.append("=" * 80)
        lines.append(f"Audit Timestamp: {result.audit_timestamp}")
        lines.append(f"Overall Status: {result.overall_status}")
        lines.append(f"Duration: {result.audit_duration_ms}ms")
        lines.append("")
        
        # Summary
        lines.append("📊 AUDIT SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Issues: {result.total_issues}")
        lines.append(f"Critical Issues: {result.critical_issues}")
        lines.append(f"High Priority Issues: {result.high_issues}")
        lines.append(f"Requirements Checked: {result.requirements_checked}")
        lines.append(f"Auto-fixes Applied: {result.auto_fixes_applied}")
        lines.append("")
        
        # Compliance Metrics
        lines.append("✅ COMPLIANCE STATUS")
        lines.append("-" * 40)
        lines.append(f"Data Storage Policy: {'✅ PASS' if result.data_storage_compliance else '❌ FAIL'}")
        lines.append(f"Data Architecture: {'✅ PASS' if result.architecture_compliance else '❌ FAIL'}")
        lines.append(f"Schema Compliance: {'✅ PASS' if result.schema_compliance else '❌ FAIL'}")
        lines.append(f"Property Coverage: {result.property_coverage:.1f}%")
        lines.append(f"Confidence Score: {result.confidence_score:.1f}%")
        lines.append("")
        
        # Issues by Category
        if result.issues:
            lines.append("🚨 ISSUES FOUND")
            lines.append("-" * 40)
            
            # Group issues by severity
            issues_by_severity = {}
            for issue in result.issues:
                severity = issue.severity.value
                if severity not in issues_by_severity:
                    issues_by_severity[severity] = []
                issues_by_severity[severity].append(issue)
            
            # Report by severity (CRITICAL first)
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
                if severity in issues_by_severity:
                    lines.append(f"\n{severity} ISSUES ({len(issues_by_severity[severity])}):")
                    for issue in issues_by_severity[severity]:
                        lines.append(f"  • {issue.description}")
                        if issue.field_path:
                            lines.append(f"    Path: {issue.field_path}")
                        if issue.actual_value is not None:
                            lines.append(f"    Actual: {issue.actual_value}")
                        if issue.expected_value is not None:
                            lines.append(f"    Expected: {issue.expected_value}")
                        if issue.remediation:
                            lines.append(f"    Fix: {issue.remediation}")
                        if issue.requirement_source:
                            lines.append(f"    Source: {issue.requirement_source}")
                        lines.append("")
        else:
            lines.append("✅ NO ISSUES FOUND - FULL COMPLIANCE")
            lines.append("")
        
        # Footer
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _print_terminal_audit_report(self, result: MaterialAuditResult) -> None:
        """
        Print comprehensive audit report to terminal after material entry generation.
        Uses comprehensive requirements configuration for icons and formatting.
        
        Args:
            result: Audit result to display
        """
        try:
            # Load comprehensive requirements for report configuration
            from shared.utils.requirements_loader import RequirementsLoader
            loader = RequirementsLoader()
            
            # Check if terminal reports are enabled
            if not loader.is_terminal_report_enabled():
                return
            
            # Get reporting configuration
            icons = loader.get_audit_icons()
            max_issues_per_severity = loader.get_max_issues_per_severity()
            
            print("\n" + "=" * 80)
            print(f"📋 MATERIAL AUDIT REPORT: {result.material_name}")
            print("=" * 80)
            
            # Status indicator using configured icons
            status_icon = icons.get('pass', '✅') if result.overall_status == "PASS" else icons.get('warning', '⚠️') if result.overall_status == "WARNING" else icons.get('fail', '❌')
            print(f"Status: {status_icon} {result.overall_status}")
            
            # Quick metrics
            print(f"Total Issues: {result.total_issues} | Critical: {result.critical_issues} | High: {result.high_issues}")
            print(f"Property Coverage: {result.property_coverage:.1f}% | Confidence: {result.confidence_score:.1f}%")
            print(f"Duration: {result.audit_duration_ms}ms | Auto-fixes: {result.auto_fixes_applied}")
            
            # Compliance status with category icons
            print("\n🔍 COMPLIANCE STATUS:")
            compliance_items = [
                ("Data Storage Policy", result.data_storage_compliance, icons.get('data_storage', '💾')),
                ("Data Architecture", result.architecture_compliance, icons.get('architecture', '🏗️')),
                ("Schema Compliance", result.schema_compliance, icons.get('schema', '📋'))
            ]
            
            for item_name, is_compliant, category_icon in compliance_items:
                status_icon = icons.get('pass', '✅') if is_compliant else icons.get('fail', '❌')
                print(f"  {category_icon} {item_name}: {status_icon}")
            
            # Issues by category
            if result.issues:
                print("\n🚨 ISSUES BY SEVERITY:")
                
                # Group by severity
                issues_by_severity = {}
                for issue in result.issues:
                    severity = issue.severity.value
                    if severity not in issues_by_severity:
                        issues_by_severity[severity] = []
                    issues_by_severity[severity].append(issue)
                
                # Display by severity using configured icons
                for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
                    if severity in issues_by_severity:
                        icon = icons.get(severity.lower(), '•')
                        issues = issues_by_severity[severity]
                        print(f"\n  {icon} {severity} ({len(issues)} issues):")
                        
                        # Show up to max_issues_per_severity
                        for issue in issues[:max_issues_per_severity]:
                            print(f"    • {issue.description}")
                            if issue.remediation:
                                print(f"      Fix: {issue.remediation}")
                            if hasattr(issue, 'requirement_source') and issue.requirement_source:
                                print(f"      Source: {issue.requirement_source}")
                        
                        if len(issues) > max_issues_per_severity:
                            print(f"    ... and {len(issues) - max_issues_per_severity} more {severity.lower()} issues")
            else:
                print(f"\n{icons.get('pass', '✅')} NO ISSUES FOUND - EXCELLENT COMPLIANCE!")
            
            # Enhanced text content quality specific report
            text_issues = [issue for issue in result.issues if issue.category == "text_content_quality"]
            if text_issues:
                print(f"\n{icons.get('text_quality', '📝')} TEXT CONTENT QUALITY:")
                formatting_issues = [i for i in text_issues if "formatting" in i.description.lower()]
                line_break_issues = [i for i in text_issues if "line" in i.description.lower() or "break" in i.description.lower()]
                voice_issues = [i for i in text_issues if "voice" in i.description.lower()]
                placeholder_issues = [i for i in text_issues if "placeholder" in i.description.lower()]
                
                if placeholder_issues:
                    print(f"  {icons.get('critical', '🔥')} Placeholder Content: {len(placeholder_issues)}")
                if formatting_issues:
                    print(f"  {icons.get('formatting', '📐')} Formatting Issues: {len(formatting_issues)}")
                if line_break_issues:
                    print(f"  {icons.get('line_breaks', '📏')} Line Break Issues: {len(line_break_issues)}")
                if voice_issues:
                    print(f"  {icons.get('author_voice', '🎭')} Author Voice Issues: {len(voice_issues)}")
            
            # Requirements source summary
            requirement_sources = set()
            for issue in result.issues:
                if hasattr(issue, 'requirement_source') and issue.requirement_source:
                    requirement_sources.add(issue.requirement_source.split('.')[0])  # Get top-level section
            
            if requirement_sources:
                print(f"\n📚 REQUIREMENTS AREAS INVOLVED: {', '.join(sorted(requirement_sources))}")
            
            print("=" * 80 + "\n")
            
        except Exception as e:
            # Fallback to simple report if detailed report fails
            print(f"\n📋 AUDIT REPORT: {result.material_name} - {result.overall_status} ({result.total_issues} issues)\n")
            logging.error(f"Terminal audit report failed: {e}")
    
    def audit_batch(
        self, 
        material_names: List[str], 
        auto_fix: bool = False,
        generate_reports: bool = False
    ) -> Dict[str, MaterialAuditResult]:
        """
        Audit multiple materials in batch.
        
        Args:
            material_names: List of material names to audit
            auto_fix: Whether to apply auto-fixes
            generate_reports: Whether to generate individual reports
            
        Returns:
            Dictionary mapping material names to audit results
        """
        self.logger.info(f"🔍 Starting batch audit of {len(material_names)} materials")
        
        results = {}
        failed_audits = []
        
        for i, material_name in enumerate(material_names, 1):
            try:
                self.logger.info(f"[{i}/{len(material_names)}] Auditing {material_name}...")
                
                result = self.audit_material(
                    material_name=material_name,
                    auto_fix=auto_fix,
                    skip_frontmatter=not generate_reports  # Skip for speed unless reports needed
                )
                
                results[material_name] = result
                
                # Generate individual report if requested
                if generate_reports:
                    report = self.generate_audit_report(result)
                    report_file = Path(f"audit_reports/{material_name}_audit_report.txt")
                    report_file.parent.mkdir(exist_ok=True)
                    with open(report_file, 'w') as f:
                        f.write(report)
                
            except Exception as e:
                self.logger.error(f"❌ Audit failed for {material_name}: {e}")
                failed_audits.append(material_name)
        
        # Generate batch summary
        self._generate_batch_summary(results, failed_audits)
        
        return results
    
    def _generate_batch_summary(self, results: Dict[str, MaterialAuditResult], failed_audits: List[str]) -> None:
        """Generate summary report for batch audit"""
        total_materials = len(results) + len(failed_audits)
        passed = sum(1 for r in results.values() if r.overall_status == "PASS")
        warned = sum(1 for r in results.values() if r.overall_status == "WARNING")
        failed = sum(1 for r in results.values() if r.overall_status == "FAIL")
        
        total_issues = sum(r.total_issues for r in results.values())
        critical_issues = sum(r.critical_issues for r in results.values())
        auto_fixes = sum(r.auto_fixes_applied for r in results.values())
        
        self.logger.info("🎯 BATCH AUDIT SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Materials Audited: {total_materials}")
        self.logger.info(f"✅ Passed: {passed}")
        self.logger.info(f"⚠️  Warnings: {warned}")
        self.logger.info(f"❌ Failed: {failed}")
        self.logger.info(f"🔧 Auto-fixes Applied: {auto_fixes}")
        self.logger.info(f"🚨 Total Issues: {total_issues}")
        self.logger.info(f"🔥 Critical Issues: {critical_issues}")
        
        if failed_audits:
            self.logger.warning(f"⚠️  Audit infrastructure failures: {', '.join(failed_audits)}")


class AuditError(Exception):
    """Exception raised when audit infrastructure fails"""
    pass


# Integration with PropertyManager
def create_audit_hook() -> callable:
    """
    Create audit hook function for integration with PropertyManager.
    
    Returns:
        Function that can be called after material updates
    """
    auditor = MaterialAuditor()
    
    def audit_after_update(material_name: str, auto_fix: bool = True) -> MaterialAuditResult:
        """
        Audit hook that runs after material updates.
        
        Args:
            material_name: Material that was updated
            auto_fix: Whether to apply automatic fixes
            
        Returns:
            Audit result with compliance status
        """
        try:
            result = auditor.audit_material(
                material_name=material_name,
                auto_fix=auto_fix,
                skip_frontmatter=True  # Skip for speed in post-processing
            )
            
            # Log critical issues immediately
            if result.critical_issues > 0:
                logging.error(f"❌ CRITICAL AUDIT FAILURES for {material_name}:")
                for issue in result.issues:
                    if issue.severity == AuditSeverity.CRITICAL:
                        logging.error(f"  • {issue.description}")
            
            # Print terminal audit report after material generation
            auditor._print_terminal_audit_report(result)
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Post-update audit failed for {material_name}: {e}")
            # Return minimal failure result
            return MaterialAuditResult(
                material_name=material_name,
                audit_timestamp=datetime.now().isoformat(),
                overall_status="AUDIT_FAILED",
                total_issues=1,
                critical_issues=1,
                high_issues=0,
                issues=[AuditIssue(
                    severity=AuditSeverity.CRITICAL,
                    category="audit_infrastructure",
                    description=f"Audit system failure: {e}",
                    remediation="Fix audit infrastructure"
                )]
            )
    
    return audit_after_update


if __name__ == "__main__":
    """CLI interface for material auditing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Material Audit System")
    parser.add_argument("--material", help="Material name to audit")
    parser.add_argument("--batch", help="Comma-separated list of materials")
    parser.add_argument("--all", action="store_true", help="Audit all materials")
    parser.add_argument("--auto-fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument("--report", action="store_true", help="Generate detailed reports")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    
    # Initialize auditor
    auditor = MaterialAuditor()
    
    try:
        if args.material:
            # Single material audit
            result = auditor.audit_material(
                material_name=args.material,
                auto_fix=args.auto_fix,
                skip_frontmatter=not args.report
            )
            
            if args.report:
                report = auditor.generate_audit_report(result)
                print(report)
            else:
                print(f"Audit {result.overall_status}: {result.total_issues} issues ({result.critical_issues} critical)")
        
        elif args.batch:
            # Batch audit
            materials = [m.strip() for m in args.batch.split(',')]
            results = auditor.audit_batch(
                material_names=materials,
                auto_fix=args.auto_fix,
                generate_reports=args.report
            )
            
            print(f"Batch audit complete: {len(results)} materials processed")
        
        elif args.all:
            # Audit all materials
            materials_data = load_materials()
            all_materials = list(materials_data.get('materials', {}).keys())
            
            results = auditor.audit_batch(
                material_names=all_materials,
                auto_fix=args.auto_fix,
                generate_reports=args.report
            )
            
            print(f"Full system audit complete: {len(results)} materials processed")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logging.error(f"Audit failed: {e}")
        sys.exit(1)