#!/usr/bin/env python3
"""
Shared Contamination Types

Data structures used by both materials and contaminants domains.
Extracted from domains/contaminants/models.py to avoid cross-domain imports.

Author: AI Assistant
Date: November 26, 2025
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


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
class ValidationIssue:
    """Single validation issue found"""
    severity: ValidationSeverity
    message: str
    contaminant_id: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of contamination validation"""
    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def has_errors(self) -> bool:
        """Check if result has any ERROR-level issues"""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """Check if result has any WARNING-level issues"""
        return any(issue.severity == ValidationSeverity.WARNING for issue in self.issues)


@dataclass
class ContaminationContext:
    """
    Context for contamination validation and research.
    
    Shared data structure used by both materials and contaminants domains
    without creating cross-domain dependencies.
    
    Attributes:
        material_name: Name of the material (e.g., "Aluminum", "Oak")
        category: Material category (e.g., "metals", "woods")
        application_context: Optional context (e.g., "machinery", "decorative")
        environment: Optional environment description
        custom_notes: Any additional context
    """
    material_name: str
    category: str
    application_context: Optional[str] = None
    environment: Optional[str] = None
    custom_notes: Optional[str] = None
    
    def __str__(self) -> str:
        parts = [f"{self.material_name} ({self.category})"]
        if self.application_context:
            parts.append(f"context: {self.application_context}")
        if self.environment:
            parts.append(f"env: {self.environment}")
        return ", ".join(parts)
