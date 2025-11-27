#!/usr/bin/env python3
"""
Image Prompt Payload Validator for Imagen API

Validates final orchestrated prompts before submission to Imagen API.
Ensures prompts are optimal for image generation by checking:
1. Logic: Contradictions, duplications, confusion
2. Length: Within Imagen API limits with safety margin
3. Quality: Clarity, specificity, coherence
4. Technical: API compatibility, format compliance

This is the FINAL validation step before Imagen API submission.

Author: AI Assistant
Date: November 26, 2025
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "CRITICAL"  # Must fix - will fail or produce bad images
    ERROR = "ERROR"        # Should fix - likely to cause problems
    WARNING = "WARNING"    # May fix - could improve quality
    INFO = "INFO"          # Optional - suggestions for improvement


class ValidationCategory(Enum):
    """Categories of validation issues"""
    LOGIC = "LOGIC"              # Contradictions, confusion
    LENGTH = "LENGTH"            # API limits, prompt size
    QUALITY = "QUALITY"          # Clarity, specificity
    TECHNICAL = "TECHNICAL"      # API compatibility
    CONTAMINATION = "CONTAMINATION"  # Material-specific rules
    PHYSICS = "PHYSICS"          # Real-world physics violations


@dataclass
class ValidationIssue:
    """Single validation issue found in prompt"""
    severity: ValidationSeverity
    category: ValidationCategory
    message: str
    location: Optional[str] = None  # Where in prompt issue was found
    suggestion: Optional[str] = None  # How to fix it
    
    def __str__(self) -> str:
        """Format issue for display"""
        loc = f" [{self.location}]" if self.location else ""
        sug = f"\n  💡 Suggestion: {self.suggestion}" if self.suggestion else ""
        return f"{self.severity.value} ({self.category.value}){loc}: {self.message}{sug}"


@dataclass
class ValidationResult:
    """Result of prompt validation"""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    prompt_length: int = 0
    estimated_tokens: int = 0
    
    # Detailed metrics
    has_critical_issues: bool = False
    has_errors: bool = False
    has_warnings: bool = False
    contradiction_count: int = 0
    duplication_count: int = 0
    
    def add_issue(self, issue: ValidationIssue):
        """Add validation issue and update flags"""
        self.issues.append(issue)
        
        if issue.severity == ValidationSeverity.CRITICAL:
            self.has_critical_issues = True
            self.is_valid = False
        elif issue.severity == ValidationSeverity.ERROR:
            self.has_errors = True
            self.is_valid = False
        elif issue.severity == ValidationSeverity.WARNING:
            self.has_warnings = True
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        if self.is_valid:
            return f"✅ VALID: {len(self.issues)} suggestions"
        
        critical = sum(1 for i in self.issues if i.severity == ValidationSeverity.CRITICAL)
        errors = sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR)
        warnings = sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)
        
        parts = []
        if critical:
            parts.append(f"{critical} critical")
        if errors:
            parts.append(f"{errors} errors")
        if warnings:
            parts.append(f"{warnings} warnings")
        
        return f"❌ INVALID: {', '.join(parts)}"
    
    def format_report(self, include_suggestions: bool = True) -> str:
        """Format full validation report"""
        lines = [
            "=" * 80,
            "🔍 IMAGE PROMPT VALIDATION REPORT",
            "=" * 80,
            "",
            f"Status: {self.get_summary()}",
            f"Prompt Length: {self.prompt_length} chars ({self.estimated_tokens} est. tokens)",
            ""
        ]
        
        if not self.issues:
            lines.append("✅ No issues found - prompt is optimal")
            return "\n".join(lines)
        
        # Group by severity
        by_severity = {
            ValidationSeverity.CRITICAL: [],
            ValidationSeverity.ERROR: [],
            ValidationSeverity.WARNING: [],
            ValidationSeverity.INFO: []
        }
        
        for issue in self.issues:
            by_severity[issue.severity].append(issue)
        
        # Report by severity
        for severity in ValidationSeverity:
            issues = by_severity[severity]
            if not issues:
                continue
            
            lines.append(f"\n{severity.value} ({len(issues)}):")
            lines.append("-" * 80)
            
            for i, issue in enumerate(issues, 1):
                lines.append(f"\n{i}. {issue.message}")
                if issue.location:
                    lines.append(f"   📍 Location: {issue.location}")
                if include_suggestions and issue.suggestion:
                    lines.append(f"   💡 Suggestion: {issue.suggestion}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


class ImagePromptPayloadValidator:
    """
    Validates final image generation prompts before Imagen API submission.
    
    Comprehensive validation including:
    - Logic: Contradictions, duplications, confusion
    - Length: API limits (4096 chars hard limit, 3500 target)
    - Quality: Clarity, specificity, coherence
    - Technical: Material-contaminant compatibility
    - Physics: Real-world plausibility
    
    Example:
        validator = ImagePromptPayloadValidator()
        result = validator.validate(prompt, material="Aluminum", contaminant="oil-grease")
        
        if not result.is_valid:
            print(result.format_report())
            # Fix issues before submitting to Imagen
    """
    
    # Imagen API Limits
    IMAGEN_HARD_LIMIT = 4096      # Absolute maximum
    IMAGEN_TARGET = 3500          # Safe target with margin
    IMAGEN_WARNING_THRESHOLD = 3800  # Warn if approaching limit
    
    # Contradiction patterns
    CONTRADICTION_PATTERNS = [
        # Color contradictions
        (r'\b(dark|black)\b.*\b(bright|white|light)\b', 'color'),
        (r'\b(bright|white|light)\b.*\b(dark|black)\b', 'color'),
        
        # Texture contradictions
        (r'\b(smooth|glossy)\b.*\b(rough|matte|textured)\b', 'texture'),
        (r'\b(rough|matte|textured)\b.*\b(smooth|glossy)\b', 'texture'),
        
        # State contradictions
        (r'\b(fresh|new|clean)\b.*\b(aged|old|weathered)\b', 'state'),
        (r'\b(aged|old|weathered)\b.*\b(fresh|new|clean)\b', 'state'),
        
        # Quantity contradictions
        (r'\b(no|zero|absent)\b.*\b(heavy|significant|substantial)\b', 'quantity'),
        (r'\b(minimal|slight)\b.*\b(heavy|significant|substantial)\b', 'quantity'),
    ]
    
    # Confusion patterns (ambiguous language)
    CONFUSION_PATTERNS = [
        (r'\b(maybe|possibly|perhaps|might)\b', 'Use definitive language for image generation'),
        (r'\b(some kind of|sort of|kind of)\b', 'Be specific about what to show'),
        (r'\b(various|multiple|different)\b(?! materials)', 'Specify exact variations'),
        (r'\b(etc\.|and so on|and more)\b', 'List all items explicitly'),
    ]
    
    # Forbidden content (will cause Imagen failures)
    FORBIDDEN_CONTENT = [
        # Material-contamination impossibilities
        (r'\brust\b.*\baluminum\b', 'Aluminum does not rust (forms oxide, not rust)'),
        (r'\baluminum\b.*\brust\b', 'Aluminum does not rust (forms oxide, not rust)'),
        (r'\brust\b.*\bplastic\b', 'Plastic cannot rust (ferrous metals only)'),
        (r'\bplastic\b.*\brust\b', 'Plastic cannot rust (ferrous metals only)'),
        (r'\brust\b.*\bglass\b', 'Glass cannot rust (ferrous metals only)'),
        
        # Prohibited contamination types
        (r'\b(dirt|soil|mud)\b', 'Dirt/soil contamination prohibited (universally banned)'),
        
        # Physics violations
        (r'\bfloating\b.*\bcontaminat', 'Contamination must obey gravity'),
        (r'\bupward\b.*\bdrip', 'Drips cannot flow upward (gravity violation)'),
    ]
    
    # Quality anti-patterns
    QUALITY_ANTIPATTERNS = [
        (r'\b(very|really|extremely|highly)\b', 'Remove intensifiers (redundant)'),
        (r'\b(somewhat|relatively|fairly)\b', 'Remove hedging language (be specific)'),
        (r'(!!|!!!)', 'Remove excessive punctuation'),
        (r'([A-Z]{4,})', 'Avoid all-caps (except acronyms)'),
    ]
    
    def __init__(
        self,
        target_length: int = IMAGEN_TARGET,
        hard_limit: int = IMAGEN_HARD_LIMIT
    ):
        """
        Initialize validator.
        
        Args:
            target_length: Optimal target length (default: 3500)
            hard_limit: Absolute maximum length (default: 4096)
        """
        self.target_length = target_length
        self.hard_limit = hard_limit
        self.warning_threshold = self.IMAGEN_WARNING_THRESHOLD
    
    def validate(
        self,
        prompt: str,
        material: Optional[str] = None,
        contaminant: Optional[str] = None,
        contamination_level: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate image generation prompt comprehensively.
        
        Args:
            prompt: Final orchestrated prompt for Imagen
            material: Material name (for contamination validation)
            contaminant: Contaminant ID (for compatibility checks)
            contamination_level: Contamination level (light, moderate, heavy)
            
        Returns:
            ValidationResult with all issues found
        """
        result = ValidationResult(
            is_valid=True,
            prompt_length=len(prompt),
            estimated_tokens=len(prompt) // 4
        )
        
        logger.info(f"🔍 Validating prompt: {len(prompt)} chars, {result.estimated_tokens} est. tokens")
        
        # 1. Check length (CRITICAL)
        self._validate_length(prompt, result)
        
        # 2. Check logic issues
        self._validate_logic(prompt, result)
        
        # 3. Check material-contamination compatibility
        if material and contaminant:
            self._validate_contamination_compatibility(prompt, material, contaminant, result)
        
        # 4. Check physics violations
        self._validate_physics(prompt, result)
        
        # 5. Check quality issues
        self._validate_quality(prompt, result)
        
        # 6. Check technical issues
        self._validate_technical(prompt, result)
        
        # 7. Check for duplications
        self._validate_duplications(prompt, result)
        
        logger.info(f"✅ Validation complete: {result.get_summary()}")
        
        return result
    
    def _validate_length(self, prompt: str, result: ValidationResult):
        """Validate prompt length against Imagen limits"""
        length = len(prompt)
        
        if length > self.hard_limit:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.LENGTH,
                message=f"Prompt exceeds Imagen hard limit: {length}/{self.hard_limit} chars",
                suggestion=f"Must reduce by {length - self.hard_limit} chars. Use PromptOptimizer."
            ))
        elif length > self.warning_threshold:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.LENGTH,
                message=f"Prompt near limit: {length}/{self.hard_limit} chars ({length - self.warning_threshold} chars over safe threshold)",
                suggestion="Consider optimizing to avoid truncation"
            ))
        elif length > self.target_length:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.LENGTH,
                message=f"Prompt over target: {length}/{self.target_length} chars (still within limits)",
                suggestion="Optional: Optimize for better performance"
            ))
    
    def _validate_logic(self, prompt: str, result: ValidationResult):
        """Check for contradictions and logical issues"""
        prompt_lower = prompt.lower()
        
        # Check contradictions
        for pattern, contradiction_type in self.CONTRADICTION_PATTERNS:
            matches = list(re.finditer(pattern, prompt_lower, re.IGNORECASE))
            for match in matches:
                result.contradiction_count += 1
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.LOGIC,
                    message=f"Contradiction detected ({contradiction_type}): {match.group(0)}",
                    location=f"chars {match.start()}-{match.end()}",
                    suggestion=f"Remove contradictory {contradiction_type} terms"
                ))
        
        # Check confusion patterns
        for pattern, suggestion in self.CONFUSION_PATTERNS:
            matches = list(re.finditer(pattern, prompt_lower, re.IGNORECASE))
            for match in matches:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.LOGIC,
                    message=f"Ambiguous language: \"{match.group(0)}\"",
                    location=f"chars {match.start()}-{match.end()}",
                    suggestion=suggestion
                ))
    
    def _validate_contamination_compatibility(
        self,
        prompt: str,
        material: str,
        contaminant: str,
        result: ValidationResult
    ):
        """Validate material-contamination compatibility"""
        prompt_lower = prompt.lower()
        material_lower = material.lower()
        contaminant_lower = contaminant.lower()
        
        # Check forbidden combinations
        for pattern, reason in self.FORBIDDEN_CONTENT:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.CONTAMINATION,
                    message=f"Impossible contamination: {reason}",
                    suggestion="Remove this contamination-material combination"
                ))
        
        # Verify material and contaminant are mentioned
        if material_lower not in prompt_lower:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.TECHNICAL,
                message=f"Material '{material}' not found in prompt",
                suggestion="Ensure material name is clearly specified"
            ))
        
        # Check for contamination specificity
        if 'contamination' in prompt_lower or contaminant_lower in prompt_lower:
            # Good - contamination is specified
            pass
        else:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.QUALITY,
                message="Contamination type not clearly specified in prompt",
                suggestion=f"Explicitly mention '{contaminant}' contamination"
            ))
    
    def _validate_physics(self, prompt: str, result: ValidationResult):
        """Check for physics violations"""
        prompt_lower = prompt.lower()
        
        # Check gravity violations
        if 'drip' in prompt_lower or 'pool' in prompt_lower:
            # Look for upward flow (impossible)
            if re.search(r'\b(upward|up|rising)\b.*\b(drip|pool|flow)\b', prompt_lower):
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.PHYSICS,
                    message="Physics violation: Contamination cannot flow upward",
                    suggestion="Specify downward flow (gravity-driven)"
                ))
        
        # Check for floating contamination
        if re.search(r'\bfloat(?:ing)?\b', prompt_lower):
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.PHYSICS,
                message="Physics violation: Contamination cannot float",
                suggestion="Specify gravity-driven accumulation"
            ))
    
    def _validate_quality(self, prompt: str, result: ValidationResult):
        """Check quality anti-patterns"""
        for pattern, suggestion in self.QUALITY_ANTIPATTERNS:
            matches = list(re.finditer(pattern, prompt, re.IGNORECASE))
            for match in matches:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.QUALITY,
                    message=f"Quality issue: \"{match.group(0)}\"",
                    location=f"chars {match.start()}-{match.end()}",
                    suggestion=suggestion
                ))
    
    def _validate_technical(self, prompt: str, result: ValidationResult):
        """Check technical/API compatibility issues"""
        
        # Check for special characters that might cause issues
        if '\x00' in prompt:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.TECHNICAL,
                message="Null character found in prompt",
                suggestion="Remove null characters (\\x00)"
            ))
        
        # Check for excessive newlines
        newline_count = prompt.count('\n\n\n')
        if newline_count > 3:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.TECHNICAL,
                message=f"Excessive blank lines: {newline_count} triple-newlines",
                suggestion="Condense whitespace for efficiency"
            ))
        
        # Check for very long lines (harder for Imagen to parse)
        lines = prompt.split('\n')
        long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 500]
        if long_lines:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.TECHNICAL,
                message=f"Very long lines: {len(long_lines)} lines over 500 chars",
                location=f"Lines: {', '.join(map(str, long_lines[:5]))}{'...' if len(long_lines) > 5 else ''}",
                suggestion="Break into shorter paragraphs for better parsing"
            ))
    
    def _validate_duplications(self, prompt: str, result: ValidationResult):
        """Check for duplicate content"""
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', prompt)
        
        # Check for exact duplicates
        seen = set()
        for i, sentence in enumerate(sentences):
            sentence_clean = sentence.strip().lower()
            if not sentence_clean:
                continue
            
            if sentence_clean in seen and len(sentence_clean) > 50:
                result.duplication_count += 1
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.LOGIC,
                    message=f"Duplicate sentence detected: \"{sentence[:80]}...\"",
                    location=f"Sentence {i+1}",
                    suggestion="Remove redundant duplicate content"
                ))
            seen.add(sentence_clean)
        
        # Check for repeated phrases (3+ word sequences)
        words = prompt.lower().split()
        phrase_counts = {}
        
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Report phrases repeated 3+ times
        repeated = [(phrase, count) for phrase, count in phrase_counts.items() if count >= 3]
        if repeated:
            for phrase, count in repeated[:3]:  # Report top 3
                result.duplication_count += 1
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.QUALITY,
                    message=f"Phrase repeated {count} times: \"{phrase}\"",
                    suggestion="Consider varying language or removing repetition"
                ))


def validate_prompt(
    prompt: str,
    material: Optional[str] = None,
    contaminant: Optional[str] = None,
    contamination_level: Optional[str] = None
) -> ValidationResult:
    """
    Convenience function to validate a prompt.
    
    Args:
        prompt: Prompt to validate
        material: Material name (optional)
        contaminant: Contaminant ID (optional)
        contamination_level: Contamination level (optional)
        
    Returns:
        ValidationResult
    """
    validator = ImagePromptPayloadValidator()
    return validator.validate(prompt, material, contaminant, contamination_level)


def validate_and_report(
    prompt: str,
    material: Optional[str] = None,
    contaminant: Optional[str] = None,
    contamination_level: Optional[str] = None,
    raise_on_invalid: bool = False
) -> ValidationResult:
    """
    Validate prompt and print report.
    
    Args:
        prompt: Prompt to validate
        material: Material name (optional)
        contaminant: Contaminant ID (optional)
        contamination_level: Contamination level (optional)
        raise_on_invalid: Raise exception if validation fails
        
    Returns:
        ValidationResult
        
    Raises:
        ValueError: If prompt is invalid and raise_on_invalid=True
    """
    result = validate_prompt(prompt, material, contaminant, contamination_level)
    
    print(result.format_report())
    
    if not result.is_valid and raise_on_invalid:
        raise ValueError(f"Prompt validation failed: {result.get_summary()}")
    
    return result
