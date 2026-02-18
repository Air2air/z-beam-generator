"""
Universal Prompt Validator - Text and Image Generation

⚠️  DEPRECATION NOTICE (November 30, 2025):
    This module is maintained for backward compatibility.
    For new code, prefer using `shared.validation.unified_validator`:
    
        from shared.validation.validator import (
            validate_prompt_quick,  # Quick validation
            Validator,       # Full validation
        )
    
    The Validator provides:
    - 3-stage validation (early, prompt, post)
    - AI-friendly fix instructions
    - Auto-optimization capabilities
    - More comprehensive issue detection

Validates final prompts before API submission (Grok, Imagen, etc.).
Ensures prompts are optimal for generation by checking:
1. Length: Within API limits with safety margins
2. Logic: Contradictions, duplications, confusion
3. Quality: Clarity, specificity, coherence
4. Technical: API compatibility, format compliance

This is the FINAL validation step before ANY API submission.

Implements PROMPT_CHAINING_POLICY.md - validates output of orchestrated prompts.

Author: AI Assistant
Date: November 27, 2025
"""

import logging
import re
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Literal, Optional

logger = logging.getLogger(__name__)

# Emit deprecation warning on module import
warnings.warn(
    "prompt_validator is deprecated. Use unified_validator for new code. "
    "See module docstring for migration guide.",
    DeprecationWarning,
    stacklevel=2
)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "CRITICAL"  # Must fix - will fail or produce bad output
    ERROR = "ERROR"        # Should fix - likely to cause problems
    WARNING = "WARNING"    # May fix - could improve quality
    INFO = "INFO"          # Optional - suggestions for improvement


class ValidationCategory(Enum):
    """Categories of validation issues"""
    LOGIC = "LOGIC"              # Contradictions, confusion
    LENGTH = "LENGTH"            # API limits, prompt size
    QUALITY = "QUALITY"          # Clarity, specificity
    TECHNICAL = "TECHNICAL"      # API compatibility
    CONTENT = "CONTENT"          # Content-specific issues


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
class PromptValidationResult:
    """Result of prompt validation"""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    prompt_length: int = 0
    word_count: int = 0
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
            "🔍 PROMPT VALIDATION REPORT",
            "=" * 80,
            "",
            f"Status: {self.get_summary()}",
            f"Length: {self.prompt_length} chars ({self.word_count} words, {self.estimated_tokens} est. tokens)",
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


class PromptValidator:
    """
    Prompt validator for text and image generation.
    
    Validates prompts before API submission to:
    - Grok API (text generation)
    - Imagen API (image generation)
    - Any other LLM APIs
    
    Checks:
    - Length: API-specific limits with safety margins
    - Logic: Contradictions, duplications, confusion
    - Quality: Clarity, specificity, coherence
    - Technical: Format compliance, encoding issues
    
    Example (Text):
        validator = PromptValidator(prompt_type='text')
        result = validator.validate(prompt)
        if not result.is_valid:
            raise ValueError(f"Prompt validation failed: {result.get_summary()}")
    
    Example (Image):
        validator = PromptValidator(prompt_type='image')
        result = validator.validate(prompt, material="Aluminum", contaminant="rust")
        if not result.is_valid:
            print(result.format_report())
    """
    
    # API Limits
    LIMITS = {
        'text': {
            'hard_limit': 8000,      # Grok API limit (conservative)
            'target': 6000,          # Safe target
            'warning': 7000,         # Warning threshold
        },
        'image': {
            'hard_limit': 4096,      # Imagen API hard limit
            'target': 3500,          # Safe target with margin
            'warning': 3800,         # Warning threshold
        }
    }
    
    # Contradiction patterns (universal)
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
    ]
    
    # Confusion patterns (ambiguous language)
    CONFUSION_PATTERNS = [
        (r'\b(maybe|possibly|perhaps|might)\b', 'Use definitive language'),
        (r'\b(some kind of|sort of|kind of)\b', 'Be specific'),
        (r'\b(etc\.|and so on|and more)\b', 'List all items explicitly'),
    ]
    
    # Quality anti-patterns
    QUALITY_ANTIPATTERNS = [
        (r'\b(very|really|extremely|highly)\b', 'Remove intensifiers (redundant)'),
        (r'\b(somewhat|relatively|fairly)\b', 'Remove hedging language (be specific)'),
        (r'(!!|!!!)', 'Remove excessive punctuation'),
    ]
    
    def __init__(
        self,
        prompt_type: Literal['text', 'image'] = 'text',
        custom_limits: Optional[Dict[str, int]] = None
    ):
        """
        Initialize validator.
        
        Args:
            prompt_type: Type of prompt ('text' or 'image')
            custom_limits: Optional custom limits (hard_limit, target, warning)
        """
        self.prompt_type = prompt_type
        
        # Get limits for this prompt type
        limits = self.LIMITS[prompt_type]
        if custom_limits:
            limits.update(custom_limits)
        
        self.hard_limit = limits['hard_limit']
        self.target_length = limits['target']
        self.warning_threshold = limits['warning']
    
    def validate(
        self,
        prompt: str,
        **context
    ) -> PromptValidationResult:
        """
        Validate prompt comprehensively.
        
        Args:
            prompt: Final orchestrated prompt for API
            **context: Additional context (material, contaminant, etc.)
            
        Returns:
            PromptValidationResult with all issues found
        """
        result = PromptValidationResult(
            is_valid=True,
            prompt_length=len(prompt),
            word_count=len(prompt.split()),
            estimated_tokens=len(prompt) // 4
        )
        
        logger.info(f"🔍 Validating {self.prompt_type} prompt: {len(prompt)} chars, {result.word_count} words")
        
        # 1. Check length (CRITICAL)
        self._validate_length(prompt, result)
        
        # 2. Check logic issues
        self._validate_logic(prompt, result)
        
        # 3. Check quality issues
        self._validate_quality(prompt, result)
        
        # 4. Check technical issues
        self._validate_technical(prompt, result)
        
        # 5. Check for duplications
        self._validate_duplications(prompt, result)
        
        # 6. Check encoding issues
        self._validate_encoding(prompt, result)
        
        logger.info(f"✅ Validation complete: {result.get_summary()}")
        
        return result
    
    def _validate_length(self, prompt: str, result: PromptValidationResult):
        """Validate prompt length against API limits"""
        length = len(prompt)
        
        if length > self.hard_limit:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.LENGTH,
                message=f"Prompt exceeds {self.prompt_type.upper()} API hard limit: {length}/{self.hard_limit} chars",
                suggestion=f"Must reduce by {length - self.hard_limit} chars"
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
        
        # Check if prompt is too short (likely incomplete)
        if length < 50:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.LENGTH,
                message=f"Prompt suspiciously short: {length} chars",
                suggestion="Ensure prompt is complete and includes all required context"
            ))
    
    def _validate_logic(self, prompt: str, result: PromptValidationResult):
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
    
    def _validate_quality(self, prompt: str, result: PromptValidationResult):
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
    
    def _validate_technical(self, prompt: str, result: PromptValidationResult):
        """Check technical/API compatibility issues"""
        
        # Check for null characters
        if '\x00' in prompt:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.TECHNICAL,
                message="Null character found in prompt",
                suggestion="Remove null characters (\\x00)"
            ))
        
        # Check for excessive newlines
        newline_count = prompt.count('\n\n\n')
        if newline_count > 5:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.TECHNICAL,
                message=f"Excessive blank lines: {newline_count} triple-newlines",
                suggestion="Condense whitespace for efficiency"
            ))
        
        # Check for very long lines (harder to parse)
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
    
    def _validate_duplications(self, prompt: str, result: PromptValidationResult):
        """Check for duplicate content"""
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', prompt)
        
        # Check for exact duplicates
        seen = set()
        for i, sentence in enumerate(sentences):
            sentence_clean = sentence.strip().lower()
            if not sentence_clean or len(sentence_clean) < 30:
                continue
            
            if sentence_clean in seen:
                result.duplication_count += 1
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.LOGIC,
                    message=f"Duplicate sentence: \"{sentence[:80]}...\"",
                    location=f"Sentence {i+1}",
                    suggestion="Remove redundant duplicate content"
                ))
            seen.add(sentence_clean)
        
        # Check for repeated phrases (4+ word sequences)
        words = prompt.lower().split()
        phrase_counts = {}
        
        for i in range(len(words) - 3):
            phrase = ' '.join(words[i:i+4])
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
    
    def _validate_encoding(self, prompt: str, result: PromptValidationResult):
        """Check for encoding issues"""
        
        # Check for non-printable characters (except newlines, tabs)
        non_printable = [c for c in prompt if ord(c) < 32 and c not in '\n\r\t']
        if non_printable:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.TECHNICAL,
                message=f"Non-printable characters found: {len(non_printable)} chars",
                suggestion="Remove non-printable characters"
            ))
        
        # Check for unusual Unicode (potential encoding issues)
        try:
            prompt.encode('utf-8')
        except UnicodeEncodeError as e:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.TECHNICAL,
                message=f"Unicode encoding error: {e}",
                suggestion="Fix character encoding issues"
            ))
    
    def _validate_ai_clarity(self, prompt: str, result: PromptValidationResult):
        """
        Validate prompt is clear and understandable for AI assistants.
        
        Checks for confusion, contradiction, and redundancy that could
        confuse the AI and produce poor output.
        """
        prompt_lower = prompt.lower()

        # Exclude VOICE INSTRUCTIONS section from AI-clarity contradiction checks.
        # Persona examples can include words like "detailed" and numeric examples
        # that are not output-length directives.
        lines = prompt.split('\n')
        voice_start = None
        voice_end = None
        for idx, line in enumerate(lines):
            upper = line.upper()
            if 'VOICE INSTRUCTIONS:' in upper or line.startswith('VOICE:'):
                voice_start = idx
                continue
            if voice_start is not None and idx > voice_start:
                if line.startswith('REQUIREMENTS:') or '=== HUMANNESS' in upper or 'OUTPUT FORMAT:' in upper:
                    voice_end = idx - 1
                    break

        if voice_start is not None:
            if voice_end is None:
                voice_end = len(lines) - 1
            clarity_scan_text = '\n'.join(
                line for idx, line in enumerate(lines)
                if not (voice_start <= idx <= voice_end)
            )
        else:
            clarity_scan_text = prompt

        clarity_scan_lower = clarity_scan_text.lower()
        
        # AI confusion patterns - contradictory instructions
        ai_confusion_patterns = [
            (r'(short|brief|concise).*\b(detailed|comprehensive|thorough)\b', 'Length contradiction: short vs detailed'),
            # Tone/style contradictions should be detected only for explicit directives,
            # not incidental vocabulary in examples or context sections.
            (r'(formal\s+tone|professional\s+tone|keep\s+it\s+formal).*\b(casual\s+tone|conversational\s+tone|informal\s+tone|keep\s+it\s+casual)\b', 'Tone contradiction: formal vs casual'),
            (r'(technical\s+style|technical\s+tone|highly\s+technical|precise\s+style).*\b(simple\s+style|plain\s+language|accessible\s+style|simple\s+language)\b', 'Style contradiction: technical vs simple'),
        ]
        
        for pattern, issue_desc in ai_confusion_patterns:
            if re.search(pattern, clarity_scan_lower, re.IGNORECASE | re.DOTALL):
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.LOGIC,
                    message=f"AI clarity issue: {issue_desc}",
                    suggestion="Resolve conflicting instructions - AI cannot follow both"
                ))
        
        # Check for multiple word count targets
        word_counts = re.findall(r'(\d+)\s*(?:to|-)?\s*(\d+)?\s*words?', clarity_scan_lower)
        if len(word_counts) > 1:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.LOGIC,
                message=f"Multiple word count targets found ({len(word_counts)})",
                suggestion="Use ONE word count target to avoid AI confusion"
            ))
        
        # Check for too many CRITICAL markers
        critical_count = len(re.findall(r'\b(CRITICAL|IMPORTANT|MUST|REQUIRED)\b', prompt, re.IGNORECASE))
        if critical_count > 5:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.QUALITY,
                message=f"Too many emphasis markers ({critical_count})",
                suggestion="Use emphasis sparingly - overuse dilutes importance"
            ))
        
        # Check for duplicate section headers
        section_headers = re.findall(r'(?:^|\n)([A-Z][A-Z\s]+):', prompt)
        header_counts = {}
        for header in section_headers:
            header_clean = header.strip().upper()
            header_counts[header_clean] = header_counts.get(header_clean, 0) + 1
        
        for header, count in header_counts.items():
            if count > 1:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.LOGIC,
                    message=f"Duplicate section header '{header}' appears {count} times",
                    suggestion=f"Consolidate '{header}' sections into one for clarity"
                ))


def validate_text_prompt(prompt: str) -> PromptValidationResult:
    """
    Validate text generation prompt (Grok API).
    
    Includes AI clarity checks for:
    - Confusion: Contradictory instructions
    - Contradiction: Mutually exclusive requirements  
    - Redundancy: Repeated instructions
    
    Args:
        prompt: Final prompt for Grok API
        
    Returns:
        PromptValidationResult
    """
    validator = PromptValidator(prompt_type='text')
    result = validator.validate(prompt)
    
    # Additional AI clarity validation
    validator._validate_ai_clarity(prompt, result)
    
    return result


def validate_image_prompt(
    prompt: str,
    **context
) -> PromptValidationResult:
    """
    Validate image generation prompt (Imagen API).
    
    Args:
        prompt: Final prompt for Imagen API
        **context: Additional context (material, contaminant, etc.)
        
    Returns:
        PromptValidationResult
    """
    validator = PromptValidator(prompt_type='image')
    return validator.validate(prompt, **context)


def validate_and_raise(
    prompt: str,
    prompt_type: Literal['text', 'image'] = 'text',
    **context
):
    """
    Validate prompt and raise exception if invalid.
    
    Args:
        prompt: Prompt to validate
        prompt_type: Type of prompt ('text' or 'image')
        **context: Additional context
        
    Raises:
        ValueError: If prompt validation fails
    """
    validator = PromptValidator(prompt_type=prompt_type)
    result = validator.validate(prompt, **context)
    
    if not result.is_valid:
        raise ValueError(
            f"Prompt validation failed: {result.get_summary()}\n\n"
            f"{result.format_report()}"
        )
    
    return result
