#!/usr/bin/env python3
"""
Contaminants Domain Models

Data models for contamination patterns, material compatibility,
and validation results.

Author: AI Assistant
Date: November 25, 2025
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ContaminantCategory(Enum):
    """Categories of contamination types"""
    OXIDATION = "oxidation"
    CONTAMINATION = "contamination"
    PHOTODEGRADATION = "photodegradation"
    BIODEGRADATION = "biodegradation"
    MECHANICAL_DAMAGE = "mechanical_damage"
    CHEMICAL_REACTION = "chemical_reaction"


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"  # Physically impossible
    WARNING = "warning"  # Unlikely or context-dependent
    INFO = "info"  # Informational note


@dataclass
class VisualCharacteristics:
    """Visual appearance of contamination"""
    color_range: List[str]
    texture: str
    thickness: str
    evolution: Optional[str] = None


@dataclass
class FormationConditions:
    """Conditions required for contamination to form"""
    required: List[str]
    accelerating: Optional[List[str]] = None
    protective: Optional[List[str]] = None


@dataclass
class ContaminantPattern:
    """
    Complete definition of a contamination pattern.
    
    Attributes:
        id: Unique identifier (e.g., "rust_oxidation")
        name: Human-readable name
        scientific_name: Scientific/chemical name
        category: Type of contamination
        description: What this contamination is
        required_elements: Chemical elements/compounds required
        chemical_formula: Chemical formula if applicable
        formation_conditions: Environmental conditions needed
        visual_characteristics: How it appears visually
        valid_materials: Materials this can occur on
        invalid_materials: Materials this CANNOT occur on
        context_required: Whether specific context is needed
        valid_contexts: Contexts where this is appropriate
        realism_notes: Important realism considerations
    """
    id: str
    name: str
    category: ContaminantCategory
    description: str
    
    # Chemistry
    required_elements: List[str] = field(default_factory=list)
    chemical_formula: Optional[str] = None
    scientific_name: Optional[str] = None
    
    # Formation
    formation_conditions: FormationConditions = field(default_factory=lambda: FormationConditions(required=[]))
    
    # Appearance
    visual_characteristics: VisualCharacteristics = field(
        default_factory=lambda: VisualCharacteristics(
            color_range=[],
            texture="",
            thickness=""
        )
    )
    
    # Material compatibility
    valid_materials: List[str] = field(default_factory=list)
    invalid_materials: List[str] = field(default_factory=list)
    valid_material_categories: List[str] = field(default_factory=list)
    
    # Context
    context_required: bool = False
    valid_contexts: List[str] = field(default_factory=list)
    invalid_without_context: List[str] = field(default_factory=list)
    
    # Documentation
    realism_notes: str = ""
    
    def is_valid_for_material(self, material_name: str, material_category: str) -> bool:
        """
        Check if this contamination is valid for a given material.
        
        Args:
            material_name: Specific material name (e.g., "Steel")
            material_category: Material category (e.g., "metals_ferrous")
            
        Returns:
            True if contamination can occur on this material
        """
        # Check explicit invalid list first
        if material_name in self.invalid_materials:
            return False
        
        # Check explicit valid list
        if material_name in self.valid_materials:
            return True
        
        # Check category
        if material_category in self.valid_material_categories:
            return True
        
        return False
    
    def requires_context(self) -> bool:
        """Check if this contamination requires specific context"""
        return self.context_required and len(self.valid_contexts) > 0


@dataclass
class MaterialProperties:
    """
    Properties and composition of a material.
    
    Attributes:
        name: Material name
        category: Material category
        contains: Chemical elements/compounds present
        can_rust: Whether this material can form rust
        valid_contamination: List of valid contamination IDs
        prohibited_contamination: List of prohibited contamination IDs
        conditional_contamination: Contamination requiring specific context
    """
    name: str
    category: str
    contains: List[str]
    can_rust: bool = False
    
    valid_contamination: List[str] = field(default_factory=list)
    prohibited_contamination: List[str] = field(default_factory=list)
    conditional_contamination: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    def has_element(self, element: str) -> bool:
        """Check if material contains a specific element"""
        return element.lower() in [e.lower() for e in self.contains]
    
    def can_have_contamination(self, contamination_id: str) -> bool:
        """Check if material can have a specific contamination"""
        if contamination_id in self.prohibited_contamination:
            return False
        if contamination_id in self.valid_contamination:
            return True
        if contamination_id in self.conditional_contamination:
            return True  # Context check happens separately
        return False


@dataclass
class ContaminationContext:
    """
    Context information for contamination validation.
    
    Attributes:
        environment: Environmental setting (e.g., "outdoor", "industrial")
        usage: How the material is used (e.g., "machinery", "decorative")
        exposure: What the material is exposed to
    """
    environment: str = "general"
    usage: str = "general"
    exposure: List[str] = field(default_factory=list)
    
    def is_machinery(self) -> bool:
        """Check if context is machinery-related"""
        machinery_keywords = ["machinery", "equipment", "industrial", "automotive", "mechanical"]
        return any(keyword in self.usage.lower() for keyword in machinery_keywords)
    
    def has_exposure(self, exposure_type: str) -> bool:
        """Check if material has specific exposure"""
        return exposure_type.lower() in [e.lower() for e in self.exposure]


@dataclass
class ValidationIssue:
    """
    A single validation issue found during compatibility check.
    
    Attributes:
        severity: How serious this issue is
        code: Error/warning code
        message: Short message
        explanation: Detailed explanation
        contamination_id: ID of the problematic contamination
        material_name: Name of the material
        suggestion: Recommended alternative
    """
    severity: ValidationSeverity
    code: str
    message: str
    explanation: str
    contamination_id: str
    material_name: str
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        """Format issue for display"""
        icon = "❌" if self.severity == ValidationSeverity.ERROR else "⚠️"
        return f"{icon} {self.message}\n   {self.explanation}"


@dataclass
class ValidationResult:
    """
    Result of contamination-material compatibility validation.
    
    Attributes:
        is_valid: Whether the combination is valid
        issues: List of validation issues found
        material_name: Material being validated
        material_category: Category of material
        contamination_ids: List of contamination IDs checked
        context: Context information used
    """
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    material_name: str = ""
    material_category: str = ""
    contamination_ids: List[str] = field(default_factory=list)
    context: Optional[ContaminationContext] = None
    
    def has_errors(self) -> bool:
        """Check if there are any error-level issues"""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """Check if there are any warning-level issues"""
        return any(issue.severity == ValidationSeverity.WARNING for issue in self.issues)
    
    def get_errors(self) -> List[ValidationIssue]:
        """Get all error-level issues"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]
    
    def get_warnings(self) -> List[ValidationIssue]:
        """Get all warning-level issues"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]
    
    def format_report(self) -> str:
        """Format validation result as a readable report"""
        if self.is_valid:
            return f"✅ Validation passed for {self.material_name}"
        
        lines = [
            f"{'='*80}",
            f"🔍 CONTAMINATION VALIDATION REPORT: {self.material_name}",
            f"{'='*80}",
            f"Material Category: {self.material_category}",
            f"Contamination Patterns: {len(self.contamination_ids)}",
            f"Status: {'✅ VALID' if self.is_valid else '❌ INVALID'}",
            ""
        ]
        
        if self.has_errors():
            lines.append("🚨 ERRORS (Physically Impossible):")
            for error in self.get_errors():
                lines.append(f"   {error}")
                if error.suggestion:
                    lines.append(f"   💡 Suggestion: {error.suggestion}")
                lines.append("")
        
        if self.has_warnings():
            lines.append("⚠️  WARNINGS (Context Issues):")
            for warning in self.get_warnings():
                lines.append(f"   {warning}")
                if warning.suggestion:
                    lines.append(f"   💡 Suggestion: {warning.suggestion}")
                lines.append("")
        
        lines.append(f"{'='*80}")
        return "\n".join(lines)


@dataclass
class MaterialCompatibility:
    """
    Compatibility information between a material and contamination pattern.
    
    Attributes:
        material: Material properties
        pattern: Contamination pattern
        is_compatible: Whether they're compatible
        requires_context: Whether specific context is needed
        reason: Explanation of compatibility/incompatibility
    """
    material: MaterialProperties
    pattern: ContaminantPattern
    is_compatible: bool
    requires_context: bool = False
    reason: str = ""
    
    def validate_context(self, context: ContaminationContext) -> bool:
        """
        Validate if the provided context satisfies requirements.
        
        Args:
            context: Context information
            
        Returns:
            True if context is sufficient
        """
        if not self.requires_context:
            return True
        
        # Check if pattern has valid contexts and if current context matches
        if self.pattern.valid_contexts:
            return any(
                ctx.lower() in context.usage.lower() 
                for ctx in self.pattern.valid_contexts
            )
        
        return True
