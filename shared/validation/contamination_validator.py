#!/usr/bin/env python3
"""
Contamination Validator

Validates material-contamination compatibility to prevent physically
impossible combinations (e.g., rust on plastics).

Author: AI Assistant
Date: November 25, 2025
"""

import logging
from typing import List, Dict, Optional, Tuple

# Import from contaminants domain (these remain domain-specific)
from domains.contaminants.models import (
    ContaminantPattern,
    MaterialProperties,
    MaterialCompatibility
)
from domains.contaminants.library import get_library, ContaminationLibrary

# Import from shared types (now in shared/)
from shared.types.contamination import (
    ContaminationContext,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity
)

logger = logging.getLogger(__name__)


class ContaminationValidator:
    """
    Validates contamination patterns against material properties.
    
    Prevents physically impossible contamination like:
    - Rust on non-ferrous metals or plastics
    - Wood rot on metals or plastics
    - UV chalking on metals
    - Oil on decorative items (without machinery context)
    """
    
    def __init__(self, library: Optional[ContaminationLibrary] = None):
        """
        Initialize validator with contamination library.
        
        Args:
            library: ContaminationLibrary instance (uses global if not provided)
        """
        self.library = library or get_library()
    
    def validate_patterns_for_material(
        self,
        material_name: str,
        pattern_names: List[str],
        context: Optional[ContaminationContext] = None
    ) -> ValidationResult:
        """
        Validate if contamination patterns are compatible with material.
        
        Args:
            material_name: Material name (e.g., "Acrylic (PMMA)")
            pattern_names: List of contamination pattern names to validate
            context: Optional context information
            
        Returns:
            ValidationResult with any issues found
        """
        # Get material properties
        material = self.library.get_material(material_name)
        if not material:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="MATERIAL_NOT_FOUND",
                    message=f"Material '{material_name}' not found in library",
                    explanation=f"The material '{material_name}' is not defined in the contamination schema.",
                    contamination_id="N/A",
                    material_name=material_name,
                    suggestion="Add material definition to schema.yaml or check spelling"
                )],
                material_name=material_name
            )
        
        # Use default context if not provided
        if context is None:
            context = ContaminationContext()
        
        issues = []
        pattern_ids = []
        
        # Validate each pattern
        for pattern_name in pattern_names:
            # Find pattern by name (fuzzy match)
            pattern = self.library.get_pattern_by_name(pattern_name)
            if not pattern:
                # Try exact ID match
                pattern = self.library.get_pattern(pattern_name)
            
            if not pattern:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="PATTERN_NOT_FOUND",
                    message=f"Pattern '{pattern_name}' not found in library",
                    explanation=f"The contamination pattern '{pattern_name}' is not defined in the schema.",
                    contamination_id=pattern_name,
                    material_name=material_name,
                    suggestion="Check pattern name spelling or add to schema.yaml"
                ))
                continue
            
            pattern_ids.append(pattern.id)
            
            # Validate compatibility
            issue = self._validate_pattern_material_compatibility(
                pattern=pattern,
                material=material,
                context=context
            )
            
            if issue:
                issues.append(issue)
        
        return ValidationResult(
            is_valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0,
            issues=issues,
            material_name=material_name,
            material_category=material.category,
            contamination_ids=pattern_ids,
            context=context
        )
    
    def _validate_pattern_material_compatibility(
        self,
        pattern: ContaminantPattern,
        material: MaterialProperties,
        context: ContaminationContext
    ) -> Optional[ValidationIssue]:
        """
        Validate single pattern-material combination.
        
        Returns:
            ValidationIssue if incompatible, None if valid
        """
        # Check if explicitly prohibited
        if pattern.id in material.prohibited_contamination:
            return self._create_incompatibility_issue(
                pattern=pattern,
                material=material,
                reason="explicitly_prohibited"
            )
        
        # Check if in valid list (BEFORE elemental check - explicit override)
        if pattern.id in material.valid_contamination:
            return None  # Explicitly valid - skip elemental check
        
        # Check elemental requirements (only for non-explicitly-valid patterns)
        if pattern.required_elements:
            missing_elements = [
                elem for elem in pattern.required_elements
                if not material.has_element(elem)
            ]
            
            if missing_elements:
                return self._create_incompatibility_issue(
                    pattern=pattern,
                    material=material,
                    reason="missing_elements",
                    missing_elements=missing_elements
                )
        
        # Check conditional contamination
        if pattern.id in material.conditional_contamination:
            condition = material.conditional_contamination[pattern.id]
            required_context = condition.get('context', '')
            
            # Check if context matches
            if 'machinery' in required_context.lower():
                if not context.is_machinery():
                    return ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="CONTEXT_REQUIRED",
                        message=f"{pattern.name} on {material.name} requires machinery context",
                        explanation=(
                            f"{pattern.name} is only realistic on {material.name} "
                            f"when part of machinery or industrial equipment. "
                            f"Current context: {context.usage}"
                        ),
                        contamination_id=pattern.id,
                        material_name=material.name,
                        suggestion=f"Only use if {material.name} is part of machinery, gears, or equipment"
                    )
            return None  # Context satisfied
        
        # Check category compatibility
        if pattern.valid_material_categories:
            if material.category in pattern.valid_material_categories:
                return None  # Category match
        
        # Check if material is in pattern's valid list
        if pattern.valid_materials:
            if material.name in pattern.valid_materials:
                return None
            elif material.name not in pattern.invalid_materials:
                # Not explicitly invalid, but not in valid list either
                return ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="COMPATIBILITY_UNCERTAIN",
                    message=f"{pattern.name} compatibility with {material.name} uncertain",
                    explanation=(
                        f"{pattern.name} is not explicitly listed as valid or invalid "
                        f"for {material.name}. Recommend verifying physical plausibility."
                    ),
                    contamination_id=pattern.id,
                    material_name=material.name,
                    suggestion="Verify this combination with material science reference"
                )
        
        # If we reach here and pattern has invalid_materials list
        if pattern.invalid_materials:
            # Check exact material name
            if material.name in pattern.invalid_materials:
                return self._create_incompatibility_issue(
                    pattern=pattern,
                    material=material,
                    reason="in_invalid_list"
                )
            
            # Check if material's category is in invalid list (e.g., "Plastics")
            for invalid in pattern.invalid_materials:
                if invalid.lower() in material.category.lower():
                    return self._create_incompatibility_issue(
                        pattern=pattern,
                        material=material,
                        reason="category_invalid"
                    )
                # Also check if it's a generic category name
                if invalid in ["Plastics", "Metals", "Ceramics", "Wood"]:
                    if invalid == "Plastics" and "polymer" in material.category.lower():
                        return self._create_incompatibility_issue(
                            pattern=pattern,
                            material=material,
                            reason="category_invalid"
                        )
                    elif invalid == "Metals" and "metal" in material.category.lower():
                        return self._create_incompatibility_issue(
                            pattern=pattern,
                            material=material,
                            reason="category_invalid"
                        )
                    elif invalid == "Ceramics" and "ceramic" in material.category.lower():
                        return self._create_incompatibility_issue(
                            pattern=pattern,
                            material=material,
                            reason="category_invalid"
                        )
                    elif invalid == "Wood" and "wood" in material.category.lower():
                        return self._create_incompatibility_issue(
                            pattern=pattern,
                            material=material,
                            reason="category_invalid"
                        )
        
        # Default: allow but warn
        return None
    
    def _create_incompatibility_issue(
        self,
        pattern: ContaminantPattern,
        material: MaterialProperties,
        reason: str,
        missing_elements: Optional[List[str]] = None
    ) -> ValidationIssue:
        """
        Create a detailed incompatibility issue with appropriate error message.
        
        Args:
            pattern: Contamination pattern
            material: Material properties
            reason: Reason for incompatibility
            missing_elements: Elements missing from material (if applicable)
            
        Returns:
            ValidationIssue with detailed explanation
        """
        # Determine error code and get template
        error_code = self._get_error_code(pattern, reason)
        
        # Get recommended alternative
        recommendation = self._get_alternative_contamination(material, pattern)
        
        # Get material category info
        material_info = {
            'material': material.name,
            'elements': ', '.join(material.contains),
            'category': material.category,
            'correct_process': self._get_correct_process(material),
            'recommended_contamination': recommendation,
            'correct_degradation': self._get_correct_degradation(material)
        }
        
        # Get error message template
        error_msg = self.library.get_error_message(error_code, **material_info)
        
        # Build explanation
        if missing_elements:
            explanation = (
                f"{pattern.scientific_name or pattern.name} requires "
                f"{', '.join(missing_elements)} which {material.name} does not contain. "
                f"{material.name} contains: {', '.join(material.contains)}. "
                f"{pattern.realism_notes}"
            )
        else:
            explanation = error_msg.get(
                'explanation',
                f"{pattern.name} is physically impossible on {material.name}. {pattern.realism_notes}"
            )
        
        return ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code=error_code,
            message=error_msg.get('message', f"{pattern.name} incompatible with {material.name}"),
            explanation=explanation,
            contamination_id=pattern.id,
            material_name=material.name,
            suggestion=error_msg.get('suggestion', recommendation)
        )
    
    def _get_error_code(self, pattern: ContaminantPattern, reason: str) -> str:
        """Determine appropriate error code"""
        if 'rust' in pattern.id.lower() or 'iron' in str(pattern.required_elements).lower():
            return "INCOMPATIBLE_RUST"
        elif 'copper' in pattern.id.lower() or 'patina' in pattern.name.lower():
            return "INCOMPATIBLE_PATINA"
        elif 'rot' in pattern.id.lower() or 'wood' in pattern.id.lower():
            return "INCOMPATIBLE_ROT"
        elif 'uv' in pattern.id.lower() or 'chalk' in pattern.id.lower():
            return "INCOMPATIBLE_CHALKING"
        elif 'oil' in pattern.id.lower():
            return "CONTEXT_REQUIRED"
        else:
            return "INCOMPATIBLE_GENERAL"
    
    def _get_correct_process(self, material: MaterialProperties) -> str:
        """Get correct degradation process for material"""
        if 'ferrous' in material.category:
            return "rust (iron oxide)"
        elif 'copper' in str(material.contains).lower():
            return "patina (copper carbonate)"
        elif 'aluminum' in str(material.contains).lower():
            return "aluminum oxide formation"
        elif 'polymer' in material.category or 'plastic' in material.category:
            return "UV photodegradation"
        elif 'wood' in material.category:
            return "biodegradation (wood rot)"
        elif 'ceramic' in material.category:
            return "weathering and erosion"
        else:
            return "material-specific degradation"
    
    def _get_correct_degradation(self, material: MaterialProperties) -> str:
        """Get correct UV degradation type for material"""
        if 'polymer' in material.category or 'plastic' in material.category:
            return "UV chalking and embrittlement"
        elif 'wood' in material.category:
            return "weathering and graying"
        elif 'paint' in str(material.contains).lower():
            return "fading and chalking"
        else:
            return "color fading"
    
    def _get_alternative_contamination(
        self,
        material: MaterialProperties,
        current_pattern: ContaminantPattern
    ) -> str:
        """Get recommended alternative contamination for material"""
        valid_patterns = self.library.get_patterns_for_material(material.name)
        
        if not valid_patterns:
            return f"environmental dust or chemical stains (check {material.category} compatibility)"
        
        # Find similar category alternative
        same_category = [
            p for p in valid_patterns
            if p.category == current_pattern.category
        ]
        
        if same_category:
            return same_category[0].name
        
        # Return first valid option
        return valid_patterns[0].name
    
    def get_compatible_patterns(
        self,
        material_name: str,
        include_conditional: bool = False,
        context: Optional[ContaminationContext] = None
    ) -> List[ContaminantPattern]:
        """
        Get all compatible contamination patterns for a material.
        
        Args:
            material_name: Material name
            include_conditional: Include patterns requiring context
            context: Context to validate conditional patterns against
            
        Returns:
            List of compatible ContaminantPattern objects
        """
        patterns = self.library.get_patterns_for_material(
            material_name,
            include_conditional=include_conditional
        )
        
        # If context provided and including conditional, filter by context
        if include_conditional and context:
            validated_patterns = []
            for pattern in patterns:
                if pattern.requires_context():
                    # Check context compatibility
                    issue = self._validate_pattern_material_compatibility(
                        pattern=pattern,
                        material=self.library.get_material(material_name),
                        context=context
                    )
                    if issue is None or issue.severity != ValidationSeverity.ERROR:
                        validated_patterns.append(pattern)
                else:
                    validated_patterns.append(pattern)
            return validated_patterns
        
        return patterns
    
    def validate_generation_config(
        self,
        material_name: str,
        research_data: Dict,
        context: Optional[Dict] = None
    ) -> ValidationResult:
        """
        Validate contamination patterns from generation config/research.
        
        Args:
            material_name: Material name
            research_data: Research data dict with 'contamination_patterns'
            context: Optional context dict with 'environment', 'usage'
            
        Returns:
            ValidationResult
        """
        # Extract pattern names from research data
        patterns = research_data.get('contamination_patterns', [])
        pattern_names = [
            p.get('pattern_name', p.get('name', ''))
            for p in patterns
        ]
        
        # Build context object
        ctx = None
        if context:
            ctx = ContaminationContext(
                environment=context.get('environment', 'general'),
                usage=context.get('usage', 'general'),
                exposure=context.get('exposure', [])
            )
        
        return self.validate_patterns_for_material(
            material_name=material_name,
            pattern_names=pattern_names,
            context=ctx
        )
