#!/usr/bin/env python3
"""
Comprehensive Frontmatter Validation System

Advanced multi-stage validation pipeline for frontmatter data accuracy and consistency.
Ensures frontmatter serves as reliable single source of truth with AI-powered verification.
"""

import json
import logging
import yaml
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validation result for a single validation stage"""
    stage: str
    status: str  # PASS, FAIL, WARNING
    score: Optional[float] = None
    issues: List[str] = None
    recommendations: List[str] = None
    raw_response: Optional[Dict] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.recommendations is None:
            self.recommendations = []


@dataclass 
class ValidationReport:
    """Complete validation report for frontmatter"""
    material_name: str
    overall_status: str  # PASS, FAIL, WARNING
    overall_score: float
    validation_results: List[ValidationResult]
    critical_issues: List[str]
    recommended_corrections: List[str]
    validation_timestamp: str

    def is_valid(self) -> bool:
        """Check if frontmatter passes validation"""
        return self.overall_status in ["PASS", "WARNING"] and self.overall_score >= 7.0

    def has_critical_issues(self) -> bool:
        """Check if there are critical issues requiring correction"""
        return len(self.critical_issues) > 0 or self.overall_status == "FAIL"


class ComprehensiveFrontmatterValidator:
    """
    Multi-stage validator for frontmatter data accuracy with AI-powered verification.
    
    Validation Stages:
    1. Schema Structure Validation - Verify against material.json schema
    2. Material Properties Validation - AI expert review of scientific data
    3. Laser Parameters Validation - Compatibility and safety checks
    4. Author Information Validation - Expertise alignment verification
    5. Cross-Reference Validation - Internal consistency checks
    """

    def __init__(self):
        self.validation_prompts = self._load_validation_prompts()
        self.material_schema = self._load_material_schema()
        logger.info("Comprehensive frontmatter validator initialized")

    def _extract_json_from_response(self, response_content: str) -> Dict:
        """Extract JSON from AI response that might contain extra text"""
        import re
        
        # First try direct JSON parsing
        try:
            return json.loads(response_content.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON within the response using regex
        json_patterns = [
            r'\{.*\}',  # Find JSON object
            r'```json\s*(\{.*\})\s*```',  # JSON in code blocks
            r'```\s*(\{.*\})\s*```',  # JSON in plain code blocks
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_content, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        # If no JSON found, raise an error
        raise json.JSONDecodeError("No valid JSON found in response", response_content, 0)

    def _load_validation_prompts(self) -> Dict:
        """Load validation prompt templates"""
        try:
            with open("frontmatter/validation_prompts.yaml", "r") as f:
                config = yaml.safe_load(f)
                return config.get("validation_prompts", {})
        except Exception as e:
            logger.error(f"Failed to load validation prompts: {e}")
            return {}

    def _load_material_schema(self) -> Dict:
        """Load material schema for structure validation"""
        try:
            with open("schemas/material.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load material schema: {e}")
            return {}

    def validate_frontmatter_comprehensive(
        self, 
        material_name: str, 
        frontmatter_data: Dict, 
        api_client,
        enable_ai_validation: bool = True
    ) -> ValidationReport:
        """
        Comprehensive validation of frontmatter data with AI-powered verification
        
        Args:
            material_name: Name of the material
            frontmatter_data: Parsed frontmatter YAML data
            api_client: API client for AI validation calls
            enable_ai_validation: Whether to run AI-powered validation stages
            
        Returns:
            ValidationReport with comprehensive validation results
        """
        logger.info(f"🔍 Starting comprehensive validation for {material_name}")
        
        validation_results = []
        critical_issues = []
        recommended_corrections = []

        # Stage 1: Schema Structure Validation (Local)
        logger.info("📋 Stage 1: Schema structure validation")
        schema_result = self._validate_schema_structure(frontmatter_data)
        validation_results.append(schema_result)
        if schema_result.status == "FAIL":
            critical_issues.extend(schema_result.issues)

        # AI-Powered Validation Stages (if enabled and API available)
        if enable_ai_validation and api_client:
            
            # Stage 2: Material Properties Validation (AI-powered)
            logger.info("🧪 Stage 2: Material properties validation")
            properties_result = self._validate_material_properties_ai(
                material_name, frontmatter_data, api_client
            )
            validation_results.append(properties_result)
            if properties_result.status == "FAIL":
                critical_issues.extend(properties_result.issues)
            recommended_corrections.extend(properties_result.recommendations)

            # Stage 3: Laser Parameters Validation (AI-powered)
            logger.info("⚡ Stage 3: Laser parameters validation")
            laser_result = self._validate_laser_parameters_ai(
                material_name, frontmatter_data, api_client
            )
            validation_results.append(laser_result)
            if laser_result.status == "FAIL":
                critical_issues.extend(laser_result.issues)
            recommended_corrections.extend(laser_result.recommendations)

            # Stage 4: Author Information Validation (AI-powered)
            logger.info("👤 Stage 4: Author information validation")
            author_result = self._validate_author_information_ai(
                material_name, frontmatter_data, api_client
            )
            validation_results.append(author_result)
            recommended_corrections.extend(author_result.recommendations)

            # Stage 5: Cross-Reference Consistency (AI-powered)
            logger.info("🔗 Stage 5: Cross-reference consistency validation")
            consistency_result = self._validate_consistency_ai(
                material_name, frontmatter_data, api_client
            )
            validation_results.append(consistency_result)
            if consistency_result.status == "FAIL":
                critical_issues.extend(consistency_result.issues)

        else:
            logger.info("⚠️ AI validation disabled or API client not available - running basic validation only")

        # Calculate overall score and status
        overall_score = self._calculate_overall_score(validation_results)
        overall_status = self._determine_overall_status(validation_results, overall_score)

        # Generate validation report
        report = ValidationReport(
            material_name=material_name,
            overall_status=overall_status,
            overall_score=overall_score,
            validation_results=validation_results,
            critical_issues=critical_issues,
            recommended_corrections=recommended_corrections,
            validation_timestamp=datetime.now().isoformat()
        )

        logger.info(f"✅ Validation complete for {material_name}: {overall_status} (score: {overall_score:.1f}/10)")
        return report

    def _validate_schema_structure(self, frontmatter_data: Dict) -> ValidationResult:
        """Validate frontmatter structure against material schema v1.8"""
        issues = []
        recommendations = []

        try:
            # Get validation configuration from schema
            validation_config = self.material_schema.get("materialProfile", {}).get("validation", {})
            required_fields = validation_config.get("frontmatter", {}).get("requiredFields", [])
            optional_fields = validation_config.get("frontmatter", {}).get("optionalFields", [])

            # Check required fields presence
            missing_required = [field for field in required_fields if field not in frontmatter_data]
            if missing_required:
                issues.extend([f"Missing required field: {field}" for field in missing_required])
                recommendations.extend([f"Add {field} field to frontmatter" for field in missing_required])

            # Validate critical data types
            type_validations = {
                "properties": dict,
                "author_object": dict,
                "chemicalProperties": dict,
                "applications": list,
                "compatibility": list,
                "images": dict
            }

            for field, expected_type in type_validations.items():
                if field in frontmatter_data:
                    if not isinstance(frontmatter_data[field], expected_type):
                        issues.append(f"Field '{field}' must be of type {expected_type.__name__}")
                        recommendations.append(f"Convert {field} to {expected_type.__name__} format")

            # Validate author_object structure (critical for single source of truth)
            if "author_object" in frontmatter_data:
                author = frontmatter_data["author_object"]
                if isinstance(author, dict):
                    required_author_fields = ["id", "name", "title", "expertise", "country", "sex", "image"]
                    missing_author_fields = [field for field in required_author_fields if field not in author]
                    if missing_author_fields:
                        issues.extend([f"Missing author_object field: {field}" for field in missing_author_fields])
                        recommendations.extend([f"Add {field} to author_object" for field in missing_author_fields])

            # Validate properties completeness for single source of truth
            if "properties" in frontmatter_data:
                props = frontmatter_data["properties"]
                if isinstance(props, dict):
                    critical_properties = ["density", "meltingPoint", "thermalConductivity"]
                    missing_props = [prop for prop in critical_properties if prop not in props]
                    if missing_props:
                        issues.extend([f"Missing critical property: {prop}" for prop in missing_props])

            # Determine status based on issue severity
            if len(missing_required) > 0:
                status = "FAIL"
            elif len(issues) > 3:
                status = "WARNING"
            else:
                status = "PASS"
            
            score = max(0, 10 - len(issues))
            
            return ValidationResult(
                stage="schema_structure",
                status=status,
                score=score,
                issues=issues,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return ValidationResult(
                stage="schema_structure",
                status="FAIL",
                score=0,
                issues=[f"Schema validation failed: {e}"],
                recommendations=["Fix schema validation errors"]
            )

    def _validate_material_properties_ai(
        self, material_name: str, frontmatter_data: Dict, api_client
    ) -> ValidationResult:
        """AI-powered validation of material properties against scientific databases"""
        try:
            # Extract properties for validation
            props = frontmatter_data.get("properties", {})
            chemical_props = frontmatter_data.get("chemicalProperties", {})
            category = frontmatter_data.get("category", "unknown")

            # Build comprehensive validation prompt
            prompt_template = self.validation_prompts.get("material_properties_check", {}).get("template", "")
            if not prompt_template:
                return self._create_warning_result("material_properties", "Validation template not found")

            prompt = prompt_template.format(
                material_name=material_name,
                category=category,
                density=props.get("density", "N/A"),
                melting_point=props.get("meltingPoint", "N/A"),
                thermal_conductivity=props.get("thermalConductivity", "N/A"),
                chemical_formula=chemical_props.get("formula", props.get("chemicalFormula", "N/A"))
            )

            # Call API for AI validation
            logger.debug(f"🤖 Requesting AI validation for {material_name} properties")
            response = api_client.generate_simple(prompt)
            
            if response.success:
                try:
                    # Parse AI validation response with improved JSON extraction
                    validation_data = self._extract_json_from_response(response.content)
                    
                    status = validation_data.get("validation_status", "FAIL")
                    issues = validation_data.get("issues_found", [])
                    recommendations = validation_data.get("recommendations", [])
                    
                    # Calculate score based on individual property checks
                    checks = ["density_check", "melting_point_check", "thermal_conductivity_check", "formula_check"]
                    passed_checks = sum(1 for check in checks if validation_data.get(check, {}).get("status") == "PASS")
                    score = (passed_checks / len(checks)) * 10

                    logger.info(f"🧪 Properties validation: {status} (score: {score:.1f})")

                    return ValidationResult(
                        stage="material_properties",
                        status=status,
                        score=score,
                        issues=issues,
                        recommendations=recommendations,
                        raw_response=validation_data
                    )
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse AI validation response: {e}")
                    return self._create_warning_result("material_properties", f"AI response parsing failed: {e}")
            else:
                return self._create_warning_result("material_properties", "AI validation call failed")

        except Exception as e:
            logger.error(f"Material properties validation error: {e}")
            return self._create_warning_result("material_properties", f"Validation error: {e}")

    def _validate_laser_parameters_ai(
        self, material_name: str, frontmatter_data: Dict, api_client
    ) -> ValidationResult:
        """AI-powered validation of laser cleaning parameters for material compatibility"""
        try:
            tech_specs = frontmatter_data.get("technicalSpecifications", {})
            props = frontmatter_data.get("properties", {})
            category = frontmatter_data.get("category", "unknown")

            # Prepare material context for AI analysis
            material_context = {
                "reflectivity_range": f"{props.get('laserReflectivityMin', 'N/A')} - {props.get('laserReflectivityMax', 'N/A')}",
                "absorption_range": f"{props.get('laserAbsorptionMin', 'N/A')} - {props.get('laserAbsorptionMax', 'N/A')}",
                "thermal_conductivity": props.get("thermalConductivity", "N/A"),
                "thermal_diffusivity_range": f"{props.get('thermalDiffusivityMin', 'N/A')} - {props.get('thermalDiffusivityMax', 'N/A')}"
            }

            prompt_template = self.validation_prompts.get("laser_parameters_check", {}).get("template", "")
            if not prompt_template:
                return self._create_warning_result("laser_parameters", "Validation template not found")

            prompt = prompt_template.format(
                material_name=material_name,
                category=category,
                reflectivity_range=material_context["reflectivity_range"],
                absorption_range=material_context["absorption_range"],
                thermal_properties=json.dumps(material_context),
                wavelength=tech_specs.get("wavelength", "N/A"),
                power_range=tech_specs.get("powerRange", "N/A"),
                pulse_duration=tech_specs.get("pulseDuration", "N/A"),
                fluence_range=tech_specs.get("fluenceRange", "N/A"),
                spot_size=tech_specs.get("spotSize", "N/A")
            )

            logger.debug(f"⚡ Requesting AI laser parameters validation for {material_name}")
            response = api_client.generate_simple(prompt)
            
            if response.success:
                try:
                    validation_data = self._extract_json_from_response(response.content)
                    status = validation_data.get("laser_validation_status", "FAIL")
                    
                    # Calculate score from validation checks
                    checks = ["wavelength_compatibility", "power_range_check", "parameter_consistency"]
                    passed_checks = sum(1 for check in checks if validation_data.get(check, {}).get("status") == "PASS")
                    score = (passed_checks / len(checks)) * 10
                    
                    # Assess thermal damage risk
                    thermal_risk = validation_data.get("thermal_damage_risk", {}).get("level", "UNKNOWN")
                    issues = []
                    if thermal_risk == "HIGH":
                        issues.append("⚠️ High thermal damage risk detected")
                    
                    # Collect parameter conflicts
                    conflicts = validation_data.get("parameter_consistency", {}).get("conflicts", [])
                    issues.extend(conflicts)
                    
                    recommendations = validation_data.get("optimization_suggestions", [])

                    logger.info(f"⚡ Laser parameters validation: {status} (score: {score:.1f})")

                    return ValidationResult(
                        stage="laser_parameters",
                        status=status,
                        score=score,
                        issues=issues,
                        recommendations=recommendations,
                        raw_response=validation_data
                    )
                    
                except json.JSONDecodeError as e:
                    return self._create_warning_result("laser_parameters", f"AI response parsing failed: {e}")
            else:
                return self._create_warning_result("laser_parameters", "AI validation call failed")

        except Exception as e:
            logger.error(f"Laser parameters validation error: {e}")
            return self._create_warning_result("laser_parameters", f"Validation error: {e}")

    def _validate_author_information_ai(
        self, material_name: str, frontmatter_data: Dict, api_client
    ) -> ValidationResult:
        """AI-powered validation of author expertise alignment with material subject"""
        try:
            author_obj = frontmatter_data.get("author_object", {})
            category = frontmatter_data.get("category", "unknown")
            
            # Assess technical complexity for expertise requirements
            props = frontmatter_data.get("properties", {})
            advanced_prop_count = len([k for k in props.keys() if any(suffix in k for suffix in ["Min", "Max", "Percentile"])])
            technical_level = "advanced" if advanced_prop_count > 10 else "intermediate"

            prompt_template = self.validation_prompts.get("author_validation_check", {}).get("template", "")
            if not prompt_template:
                return self._create_warning_result("author_validation", "Validation template not found")

            prompt = prompt_template.format(
                material_name=material_name,
                author_name=author_obj.get("name", "N/A"),
                author_title=author_obj.get("title", "N/A"),
                author_expertise=author_obj.get("expertise", "N/A"),
                author_country=author_obj.get("country", "N/A"),
                category=category,
                technical_level=technical_level
            )

            logger.debug(f"👤 Requesting AI author validation for {material_name}")
            response = api_client.generate_simple(prompt)
            
            if response.success:
                try:
                    validation_data = self._extract_json_from_response(response.content)
                    status = validation_data.get("author_validation_status", "FAIL")
                    
                    # Extract expertise alignment score
                    expertise_alignment = validation_data.get("expertise_alignment", {})
                    expertise_score = float(expertise_alignment.get("score", 5))
                    
                    # Adjust score based on content authority level
                    content_authority = validation_data.get("content_authority", {}).get("level", "MEDIUM")
                    authority_multiplier = {"HIGH": 1.0, "MEDIUM": 0.8, "LOW": 0.6}.get(content_authority, 0.5)
                    final_score = expertise_score * authority_multiplier

                    issues = [] if status == "PASS" else [f"Author expertise alignment concerns: {expertise_alignment.get('reasoning', 'N/A')}"]
                    recommendations = validation_data.get("improvement_suggestions", [])

                    logger.info(f"👤 Author validation: {status} (score: {final_score:.1f})")

                    return ValidationResult(
                        stage="author_validation", 
                        status=status,
                        score=final_score,
                        issues=issues,
                        recommendations=recommendations,
                        raw_response=validation_data
                    )
                    
                except (json.JSONDecodeError, ValueError) as e:
                    return self._create_warning_result("author_validation", f"AI response parsing failed: {e}")
            else:
                return self._create_warning_result("author_validation", "AI validation call failed")

        except Exception as e:
            logger.error(f"Author validation error: {e}")
            return self._create_warning_result("author_validation", f"Validation error: {e}")

    def _validate_consistency_ai(
        self, material_name: str, frontmatter_data: Dict, api_client
    ) -> ValidationResult:
        """AI-powered validation of internal consistency across all frontmatter fields"""
        try:
            # Prepare complete frontmatter for comprehensive AI analysis
            # Sanitize data to remove any sensitive information
            sanitized_data = self._sanitize_frontmatter_for_validation(frontmatter_data)
            frontmatter_json = json.dumps(sanitized_data, indent=2)

            prompt_template = self.validation_prompts.get("consistency_check", {}).get("template", "")
            if not prompt_template:
                return self._create_warning_result("consistency_check", "Validation template not found")

            prompt = prompt_template.format(
                material_name=material_name,
                full_frontmatter_json=frontmatter_json
            )

            logger.debug(f"🔗 Requesting AI consistency validation for {material_name}")
            response = api_client.generate_simple(prompt)
            
            if response.success:
                try:
                    validation_data = self._extract_json_from_response(response.content)
                    status = validation_data.get("consistency_status", "FAIL")
                    
                    # Calculate weighted consistency score with proper type conversion
                    score_components = {
                        "content_alignment": float(validation_data.get("content_alignment", {}).get("score", 5)),
                        "metric_realism": 10 if validation_data.get("metric_realism", {}).get("status") == "PASS" else 3,
                        "keyword_relevance": float(validation_data.get("keyword_relevance", {}).get("score", 5)),
                        "overall_coherence": float(validation_data.get("overall_coherence", {}).get("score", 5))
                    }
                    
                    # Weighted average calculation
                    total_score = (
                        score_components["content_alignment"] * 0.3 +
                        score_components["metric_realism"] * 0.3 +
                        score_components["keyword_relevance"] * 0.2 +
                        score_components["overall_coherence"] * 0.2
                    )

                    # Collect all consistency issues
                    issues = []
                    issues.extend(validation_data.get("percentile_validation", {}).get("issues", []))
                    issues.extend(validation_data.get("range_validation", {}).get("out_of_range", []))
                    issues.extend(validation_data.get("content_alignment", {}).get("misalignments", []))
                    issues.extend(validation_data.get("overall_coherence", {}).get("major_issues", []))

                    recommendations = []
                    recommendations.extend(validation_data.get("keyword_relevance", {}).get("suggestions", []))

                    logger.info(f"🔗 Consistency validation: {status} (score: {total_score:.1f})")

                    return ValidationResult(
                        stage="consistency_check",
                        status=status,
                        score=total_score,
                        issues=issues,
                        recommendations=recommendations,
                        raw_response=validation_data
                    )
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    return self._create_warning_result("consistency_check", f"AI response parsing failed: {e}")
            else:
                return self._create_warning_result("consistency_check", "AI validation call failed")

        except Exception as e:
            logger.error(f"Consistency validation error: {e}")
            return self._create_warning_result("consistency_check", f"Validation error: {e}")

    def _sanitize_frontmatter_for_validation(self, frontmatter_data: Dict) -> Dict:
        """Remove sensitive data before sending to AI for validation"""
        sanitized = frontmatter_data.copy()
        
        # Remove potentially sensitive fields
        sensitive_fields = ["author_object.image", "prompt_chain_verification"]
        
        if "author_object" in sanitized and "image" in sanitized["author_object"]:
            sanitized["author_object"]["image"] = "/images/author/[sanitized].jpg"
            
        if "prompt_chain_verification" in sanitized:
            del sanitized["prompt_chain_verification"]
            
        return sanitized

    def _create_warning_result(self, stage: str, message: str) -> ValidationResult:
        """Create a warning validation result for error cases"""
        return ValidationResult(
            stage=stage,
            status="WARNING",
            score=5.0,
            issues=[message],
            recommendations=["Manual review recommended"]
        )

    def _calculate_overall_score(self, validation_results: List[ValidationResult]) -> float:
        """Calculate weighted overall validation score"""
        if not validation_results:
            return 0.0

        # Weights for different validation stages (single source of truth focus)
        stage_weights = {
            "schema_structure": 0.30,      # Critical for structure
            "material_properties": 0.35,   # Most critical for scientific accuracy
            "laser_parameters": 0.20,      # Important for technical accuracy
            "author_validation": 0.08,     # Supporting validation
            "consistency_check": 0.07      # Supporting validation
        }

        total_weighted_score = 0.0
        total_weight = 0.0

        for result in validation_results:
            weight = stage_weights.get(result.stage, 0.05)
            if result.score is not None:
                total_weighted_score += result.score * weight
                total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def _determine_overall_status(self, validation_results: List[ValidationResult], overall_score: float) -> str:
        """Determine overall validation status based on results and score"""
        # Check for critical failures in essential stages
        critical_stages = ["schema_structure", "material_properties"]
        for result in validation_results:
            if result.stage in critical_stages and result.status == "FAIL":
                return "FAIL"

        # Status determination based on overall score
        if overall_score >= 8.5:
            return "PASS"
        elif overall_score >= 6.5:
            return "WARNING"
        else:
            return "FAIL"

    def generate_comprehensive_report(self, report: ValidationReport) -> str:
        """Generate detailed human-readable validation report"""
        lines = [
            "# 🔍 Comprehensive Frontmatter Validation Report",
            f"**Material:** {report.material_name}",
            f"**Overall Status:** {self._format_status(report.overall_status)}",
            f"**Overall Score:** {report.overall_score:.1f}/10.0",
            f"**Validation Timestamp:** {report.validation_timestamp}",
            f"**Single Source of Truth Status:** {'✅ VALIDATED' if report.is_valid() else '❌ REQUIRES ATTENTION'}",
            "",
            "## 📊 Validation Results by Stage:",
            ""
        ]

        for result in report.validation_results:
            stage_icon = self._get_stage_icon(result.stage)
            status_icon = self._get_status_icon(result.status)
            
            lines.extend([
                f"### {stage_icon} {result.stage.replace('_', ' ').title()}",
                f"- **Status:** {status_icon} {result.status}",
                f"- **Score:** {result.score:.1f}/10.0" if result.score else "- **Score:** N/A",
            ])
            
            if result.issues:
                lines.append("- **Issues Found:**")
                for issue in result.issues:
                    lines.append(f"  - ⚠️ {issue}")
            
            if result.recommendations:
                lines.append("- **Recommendations:**")
                for rec in result.recommendations:
                    lines.append(f"  - 🔧 {rec}")
            lines.append("")

        if report.critical_issues:
            lines.extend([
                "## 🚨 Critical Issues Requiring Immediate Attention:",
                ""
            ])
            for issue in report.critical_issues:
                lines.append(f"- ❌ {issue}")
            lines.append("")

        if report.recommended_corrections:
            lines.extend([
                "## 🛠️ Recommended Corrections for Single Source of Truth:",
                ""
            ])
            for correction in report.recommended_corrections:
                lines.append(f"- 🔧 {correction}")

        lines.extend([
            "",
            "---",
            f"*Report generated by Comprehensive Frontmatter Validator v1.0*",
            f"*Validation completed at {report.validation_timestamp}*"
        ])

        return "\n".join(lines)

    def _format_status(self, status: str) -> str:
        """Format status with appropriate emoji"""
        status_formats = {
            "PASS": "✅ PASS",
            "WARNING": "⚠️ WARNING", 
            "FAIL": "❌ FAIL"
        }
        return status_formats.get(status, status)

    def _get_stage_icon(self, stage: str) -> str:
        """Get appropriate icon for validation stage"""
        stage_icons = {
            "schema_structure": "📋",
            "material_properties": "🧪",
            "laser_parameters": "⚡",
            "author_validation": "👤",
            "consistency_check": "🔗"
        }
        return stage_icons.get(stage, "🔍")

    def _get_status_icon(self, status: str) -> str:
        """Get appropriate icon for status"""
        status_icons = {
            "PASS": "✅",
            "WARNING": "⚠️",
            "FAIL": "❌"
        }
        return status_icons.get(status, "❓")
