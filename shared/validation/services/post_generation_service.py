#!/usr/bin/env python3
"""
Post-Generation Quality Validation Service

⚠️  DEPRECATED - Use validation/content_validator.py instead
This module is maintained for backward compatibility only.
New code should use validation.content_validator.ContentValidationService

Migration Guide:
- PostGenerationQualityService → ContentValidationService
- QualityScore → ContentValidationResult
- Multi-dimensional scoring now available in ContentValidationService

See: docs/CONTENT_VALIDATION_SYSTEM.md for complete migration guide

---

Legacy Implementation:
Provides multi-dimensional quality scoring for generated content
(formerly split across multiple validation utilities).
"""

import logging
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

# Issue deprecation warning on import
warnings.warn(
    "validation.services.post_generation_service is deprecated. "
    "Use validation.content_validator.ContentValidationService instead. "
    "See docs/CONTENT_VALIDATION_SYSTEM.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)

logger = logging.getLogger(__name__)


import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Import existing validators
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from shared.validation.schema_validator import SchemaValidator, ValidationResult as SchemaValidationResult
from shared.validation.caption_integration_validator import CaptionIntegrationValidator

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class QualityScore:
    """Quality score for generated content"""
    overall_score: float
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    structure_score: float
    issues: List[str] = field(default_factory=list)
    passed: bool = True
    
    @property
    def grade(self) -> str:
        """Convert score to letter grade"""
        if self.overall_score >= 0.9:
            return "A"
        elif self.overall_score >= 0.8:
            return "B"
        elif self.overall_score >= 0.7:
            return "C"
        elif self.overall_score >= 0.6:
            return "D"
        else:
            return "F"


@dataclass
class ValidationResult:
    """Result of validation operation"""
    success: bool
    validation_type: str
    material_name: str
    component_type: str
    quality_score: Optional[QualityScore] = None
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class IntegrationResult:
    """Result of integration validation"""
    success: bool
    material_name: str
    components_validated: List[str]
    integration_issues: List[str] = field(default_factory=list)
    quality_scores: Dict[str, QualityScore] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# POST-GENERATION QUALITY ASSURANCE SERVICE
# ============================================================================

class PostGenerationQualityService:
    """
    Unified post-generation quality assurance service.
    
    Consolidates QA logic from multiple validators into single service.
    Enforces strict fail-fast architecture per GROK_INSTRUCTIONS.md.
    """
    
    def __init__(self, schema_path: str = None):
        """
        Initialize quality service.
        
        Args:
            schema_path: Optional path to JSON schema file
        """
        self.schema_path = schema_path or str(project_root / "schemas" / "frontmatter.json")
        
        # Initialize validators
        self.schema_validator = SchemaValidator(self.schema_path)
        self.caption_validator = CaptionIntegrationValidator()
        
        # Quality thresholds
        self.quality_threshold = 0.7
        self.completeness_threshold = 0.8
        
        logger.info("✅ PostGenerationQualityService initialized")
    
    # ========================================================================
    # SCHEMA VALIDATION
    # ========================================================================
    
    def validate_schema(
        self,
        content: Dict,
        component_type: str,
        material_name: str = "unknown"
    ) -> ValidationResult:
        """
        Validate content against JSON schema.
        
        Args:
            content: Generated content to validate
            component_type: Type of component ('frontmatter', 'caption', etc.)
            material_name: Name of material for reporting
            
        Returns:
            ValidationResult with schema validation status
        """
        logger.info(f"🔍 Validating {component_type} schema for {material_name}")
        
        try:
            # Use schema validator
            if component_type == 'frontmatter':
                schema_result = self.schema_validator.validate(content, material_name)
                
                result = ValidationResult(
                    success=schema_result.is_valid,
                    validation_type="schema",
                    material_name=material_name,
                    component_type=component_type,
                    errors=[{'message': err} for err in schema_result.errors],
                    warnings=[{'message': warn} for warn in schema_result.warnings]
                )
                
                if schema_result.is_valid:
                    logger.info(f"✅ Schema validation passed for {material_name}")
                else:
                    logger.warning(f"⚠️ Schema validation issues: {len(schema_result.errors)} errors")
                
                return result
            else:
                # Basic structure validation for other components
                return ValidationResult(
                    success=True,
                    validation_type="schema",
                    material_name=material_name,
                    component_type=component_type
                )
                
        except Exception as e:
            logger.error(f"❌ Schema validation failed: {e}")
            return ValidationResult(
                success=False,
                validation_type="schema",
                material_name=material_name,
                component_type=component_type,
                errors=[{'message': f"Schema validation error: {str(e)}"}]
            )
    
    # ========================================================================
    # QUALITY SCORING
    # ========================================================================
    
    def validate_quality(
        self,
        content: Dict,
        component_type: str,
        material_name: str = "unknown"
    ) -> ValidationResult:
        """
        Score content quality (completeness, accuracy, consistency).
        
        Args:
            content: Generated content to score
            component_type: Type of component
            material_name: Name of material
            
        Returns:
            ValidationResult with quality score
        """
        logger.info(f"📊 Scoring {component_type} quality for {material_name}")
        
        try:
            if component_type == 'frontmatter':
                quality_score = self._score_frontmatter_quality(content)
            elif component_type == 'caption':
                quality_score = self._score_caption_quality(content)
            else:
                # Basic scoring for other components
                quality_score = QualityScore(
                    overall_score=0.8,
                    completeness_score=0.8,
                    accuracy_score=0.8,
                    consistency_score=0.8,
                    structure_score=0.8
                )
            
            passed = quality_score.overall_score >= self.quality_threshold
            
            result = ValidationResult(
                success=passed,
                validation_type="quality",
                material_name=material_name,
                component_type=component_type,
                quality_score=quality_score
            )
            
            if passed:
                logger.info(f"✅ Quality score {quality_score.overall_score:.2f} (Grade: {quality_score.grade})")
            else:
                logger.warning(f"⚠️ Quality score {quality_score.overall_score:.2f} below threshold {self.quality_threshold}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Quality scoring failed: {e}")
            return ValidationResult(
                success=False,
                validation_type="quality",
                material_name=material_name,
                component_type=component_type,
                errors=[{'message': f"Quality scoring error: {str(e)}"}]
            )
    
    def _score_frontmatter_quality(self, frontmatter: Dict) -> QualityScore:
        """Score frontmatter quality"""
        issues = []
        
        # Completeness scoring
        required_fields = ['name', 'category', 'title', 'description', 'materialProperties', 'applications']
        present_fields = sum(1 for field in required_fields if field in frontmatter and frontmatter[field])
        completeness_score = present_fields / len(required_fields)
        
        if completeness_score < self.completeness_threshold:
            missing = [f for f in required_fields if f not in frontmatter or not frontmatter[f]]
            issues.append(f"Missing or empty fields: {missing}")
        
        # Accuracy scoring (check material properties)
        accuracy_score = 1.0
        if 'materialProperties' in frontmatter:
            props = frontmatter['materialProperties']
            if isinstance(props, dict) and len(props) < 5:
                accuracy_score = 0.7
                issues.append("Insufficient material properties (need at least 5)")
        
        # Consistency scoring
        consistency_score = 1.0
        if 'name' in frontmatter and 'title' in frontmatter:
            if frontmatter['name'].lower() not in frontmatter['title'].lower():
                consistency_score = 0.8
                issues.append("Name not referenced in title")
        
        # Structure scoring
        structure_score = 1.0
        if 'applications' in frontmatter:
            apps = frontmatter['applications']
            if isinstance(apps, list) and len(apps) < 2:
                structure_score = 0.7
                issues.append("Insufficient applications (need at least 2)")
        
        # Overall score (weighted average)
        overall_score = (
            completeness_score * 0.3 +
            accuracy_score * 0.3 +
            consistency_score * 0.2 +
            structure_score * 0.2
        )
        
        return QualityScore(
            overall_score=overall_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            structure_score=structure_score,
            issues=issues,
            passed=overall_score >= self.quality_threshold
        )
    
    def _score_caption_quality(self, caption: Dict) -> QualityScore:
        """Score caption quality"""
        issues = []
        
        # Check required caption fields
        required_fields = ['heading', 'subheading', 'description']
        present_fields = sum(1 for field in required_fields if field in caption and caption[field])
        completeness_score = present_fields / len(required_fields)
        
        # Check content length
        accuracy_score = 1.0
        if 'description' in caption:
            desc_length = len(str(caption['description']))
            if desc_length < 100:
                accuracy_score = 0.6
                issues.append("Description too short")
            elif desc_length > 1000:
                accuracy_score = 0.8
                issues.append("Description too long")
        
        overall_score = (completeness_score * 0.5 + accuracy_score * 0.5)
        
        return QualityScore(
            overall_score=overall_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            consistency_score=1.0,
            structure_score=1.0,
            issues=issues,
            passed=overall_score >= self.quality_threshold
        )
    
    # ========================================================================
    # INTEGRATION VALIDATION
    # ========================================================================
    
    def validate_integration(
        self,
        frontmatter: Dict,
        caption: Optional[Dict] = None,
        material_name: str = "unknown"
    ) -> IntegrationResult:
        """
        Validate component integration (frontmatter + caption).
        
        Args:
            frontmatter: Frontmatter data
            caption: Optional caption data
            material_name: Name of material
            
        Returns:
            IntegrationResult with validation status
        """
        logger.info(f"🔗 Validating component integration for {material_name}")
        
        integration_issues = []
        quality_scores = {}
        components_validated = ['frontmatter']
        
        try:
            # Validate frontmatter structure
            if not self.caption_validator.validate_caption_structure(frontmatter):
                integration_issues.extend(self.caption_validator.validation_errors)
            
            # Score frontmatter quality
            frontmatter_quality = self._score_frontmatter_quality(frontmatter)
            quality_scores['frontmatter'] = frontmatter_quality
            
            # Validate caption if provided
            if caption:
                components_validated.append('caption')
                caption_quality = self._score_caption_quality(caption)
                quality_scores['caption'] = caption_quality
                
                # Check integration metadata
                if not self.caption_validator.validate_integration_metadata(frontmatter):
                    integration_issues.extend(self.caption_validator.validation_errors)
            
            success = len(integration_issues) == 0
            
            if success:
                logger.info(f"✅ Integration validation passed for {material_name}")
            else:
                logger.warning(f"⚠️ Integration issues: {len(integration_issues)}")
            
            return IntegrationResult(
                success=success,
                material_name=material_name,
                components_validated=components_validated,
                integration_issues=integration_issues,
                quality_scores=quality_scores
            )
            
        except Exception as e:
            logger.error(f"❌ Integration validation failed: {e}")
            return IntegrationResult(
                success=False,
                material_name=material_name,
                components_validated=components_validated,
                integration_issues=[f"Integration validation error: {str(e)}"]
            )
    
    # ========================================================================
    # BATCH VALIDATION
    # ========================================================================
    
    def validate_batch(
        self,
        directory: str,
        component_type: str = "frontmatter"
    ) -> List[ValidationResult]:
        """
        Validate all files in a directory.
        
        Args:
            directory: Path to directory containing files
            component_type: Type of component to validate
            
        Returns:
            List of ValidationResult for each file
        """
        logger.info(f"📦 Batch validating {component_type} in {directory}")
        
        results = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            logger.warning(f"⚠️ Directory not found: {directory}")
            return results
        
        files = list(directory_path.glob("*.yaml"))
        
        for file_path in files:
            try:
                material_name = file_path.stem.replace('-laser-cleaning', '')
                
                with open(file_path) as f:
                    content = yaml.safe_load(f)
                
                # Validate schema
                schema_result = self.validate_schema(content, component_type, material_name)
                results.append(schema_result)
                
                # Validate quality
                quality_result = self.validate_quality(content, component_type, material_name)
                results.append(quality_result)
                
            except Exception as e:
                logger.error(f"❌ Error validating {file_path.name}: {e}")
                results.append(ValidationResult(
                    success=False,
                    validation_type="batch",
                    material_name=file_path.stem,
                    component_type=component_type,
                    errors=[{'message': str(e)}]
                ))
        
        # Summary
        passed = sum(1 for r in results if r.success)
        total = len(results)
        logger.info(f"📊 Batch validation complete: {passed}/{total} passed")
        
        return results
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_detailed_report(
        self,
        validation_results: List[ValidationResult],
        output_file: str = None
    ) -> str:
        """Generate comprehensive QA report"""
        report_lines = []
        
        report_lines.append("=" * 80)
        report_lines.append("POST-GENERATION QUALITY ASSURANCE REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Timestamp: {datetime.now().isoformat()}")
        report_lines.append("")
        
        # Summary statistics
        total = len(validation_results)
        passed = sum(1 for r in validation_results if r.success)
        failed = total - passed
        
        report_lines.append(f"SUMMARY:")
        report_lines.append(f"  Total validations: {total}")
        report_lines.append(f"  Passed: {passed}")
        report_lines.append(f"  Failed: {failed}")
        report_lines.append(f"  Success rate: {(passed/total*100):.1f}%" if total > 0 else "  Success rate: N/A")
        report_lines.append("")
        
        # Quality scores summary
        scores_with_quality = [r for r in validation_results if r.quality_score]
        if scores_with_quality:
            avg_score = sum(r.quality_score.overall_score for r in scores_with_quality) / len(scores_with_quality)
            report_lines.append(f"QUALITY METRICS:")
            report_lines.append(f"  Average quality score: {avg_score:.2f}")
            report_lines.append(f"  Grade distribution:")
            
            grades = [r.quality_score.grade for r in scores_with_quality]
            for grade in ['A', 'B', 'C', 'D', 'F']:
                count = grades.count(grade)
                report_lines.append(f"    {grade}: {count}")
            report_lines.append("")
        
        # Detailed results
        if failed > 0:
            report_lines.append("-" * 80)
            report_lines.append("FAILED VALIDATIONS:")
            report_lines.append("-" * 80)
            for result in validation_results:
                if not result.success:
                    report_lines.append(f"\n{result.material_name} ({result.component_type}):")
                    for error in result.errors:
                        report_lines.append(f"  ❌ {error.get('message', str(error))}")
            report_lines.append("")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            logger.info(f"📄 Report saved to {output_file}")
        
        return report
