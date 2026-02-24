"""
Prompt Validators — Text/Image Quality + Coherence Checking
==============================================================

Canonical module for all prompt quality checks before API submission.

Contains two validator families:

1. Prompt Validator (text/image API limits, logic, quality, encoding):
   - PromptValidator, PromptValidationResult, ValidationIssue
   - validate_text_prompt, validate_image_prompt, validate_and_raise

2. Coherence Validator (separation of concerns, contradictions):
   - PromptCoherenceValidator, CoherenceValidationResult, CoherenceIssue
   - validate_prompt_coherence

Backward-compat shims at old import paths:
  shared.validation.content.prompt_validator           → this module
  shared.validation.content.prompt_coherence_validator → this module

Created: November 27, 2025 (prompt_validator) / December 11, 2025 (coherence)
Consolidated: February 23, 2026
Policy: PROMPT_CHAINING_POLICY.md
"""


# =============================================================================
# SECTION 1: Prompt Validator — Text and Image Generation
# =============================================================================

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Literal, Optional

logger = logging.getLogger(__name__)



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


# =============================================================================
# SECTION 2: Coherence Validator — Separation of Concerns
# =============================================================================

from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class CoherenceIssueType(Enum):
    """Types of coherence issues"""
    CONTRADICTION = "CONTRADICTION"
    DUPLICATION = "DUPLICATION"
    CONFUSION = "CONFUSION"
    SEPARATION_VIOLATION = "SEPARATION_VIOLATION"
    VOICE_LEAK = "VOICE_LEAK"


@dataclass
class CoherenceIssue:
    """Single coherence issue in prompt"""
    issue_type: CoherenceIssueType
    severity: str  # "CRITICAL", "ERROR", "WARNING"
    message: str
    section1: str  # First conflicting section
    section2: Optional[str] = None  # Second conflicting section (if applicable)
    evidence1: str = ""  # Text evidence from section 1
    evidence2: str = ""  # Text evidence from section 2
    suggestion: str = ""  # How to fix
    
    def __str__(self) -> str:
        """Format for display"""
        parts = [f"[{self.severity}] {self.issue_type.value}: {self.message}"]
        if self.section1:
            parts.append(f"  📍 Section 1: {self.section1}")
            if self.evidence1:
                parts.append(f"     '{self.evidence1[:100]}...'")
        if self.section2:
            parts.append(f"  📍 Section 2: {self.section2}")
            if self.evidence2:
                parts.append(f"     '{self.evidence2[:100]}...'")
        if self.suggestion:
            parts.append(f"  💡 {self.suggestion}")
        return "\n".join(parts)


@dataclass
class CoherenceValidationResult:
    """Result of coherence validation"""
    is_coherent: bool
    issues: List[CoherenceIssue] = field(default_factory=list)
    sections_detected: Dict[str, bool] = field(default_factory=dict)
    separation_score: float = 100.0  # 0-100, how well separated are concerns
    has_critical_issues: bool = False  # For consistency with PromptValidationResult
    
    def add_issue(self, issue: CoherenceIssue):
        """Add issue and update coherence status"""
        self.issues.append(issue)
        if issue.severity == "CRITICAL":
            self.has_critical_issues = True
            self.is_coherent = False
            self.separation_score -= 15.0  # Deduct more for critical
        elif issue.severity == "ERROR":
            self.is_coherent = False
            self.separation_score -= 10.0  # Deduct for errors
    
    def get_summary(self) -> str:
        """Get readable summary"""
        if self.is_coherent and not self.issues:
            return f"✅ COHERENT (Score: {self.separation_score:.0f}/100)"
        
        critical = sum(1 for i in self.issues if i.severity == "CRITICAL")
        errors = sum(1 for i in self.issues if i.severity == "ERROR")
        warnings = sum(1 for i in self.issues if i.severity == "WARNING")
        
        parts = []
        if critical:
            parts.append(f"{critical} critical")
        if errors:
            parts.append(f"{errors} errors")
        if warnings:
            parts.append(f"{warnings} warnings")
        
        return f"❌ INCOHERENT: {', '.join(parts)} (Score: {self.separation_score:.0f}/100)"
    
    def format_report(self) -> str:
        """Format detailed report"""
        lines = [
            "=" * 80,
            "🔍 PROMPT COHERENCE VALIDATION",
            "=" * 80,
            "",
            f"Status: {self.get_summary()}",
            ""
        ]
        
        if self.sections_detected:
            lines.append("📋 Detected Sections:")
            for section, present in self.sections_detected.items():
                status = "✅" if present else "❌"
                lines.append(f"   {status} {section}")
            lines.append("")
        
        if not self.issues:
            lines.append("✅ No coherence issues - prompt is clear and consistent")
            return "\n".join(lines)
        
        # Group by type
        by_type = {}
        for issue in self.issues:
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)
        
        for issue_type, issues in by_type.items():
            lines.append(f"\n{issue_type.value} ({len(issues)}):")
            lines.append("-" * 80)
            for i, issue in enumerate(issues, 1):
                lines.append(f"\n{i}. {issue}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


class PromptCoherenceValidator:
    """
    Validates prompt coherence and separation of concerns.
    
    Checks:
    1. Voice instructions only in voice section (not leaking to requirements)
    2. Content instructions only in component template (not in system prompt)
    3. Requirements clear and non-contradictory
    4. No duplicate/conflicting instructions between sections
    5. Proper separation: Context → Voice → Humanness → Requirements → Output
    
    Example:
        validator = PromptCoherenceValidator()
        result = validator.validate(assembled_prompt)
        if not result.is_coherent:
            print(result.format_report())
    """
    
    def __init__(self):
        """Initialize validator"""
        self.logger = logging.getLogger(__name__)
    
    def validate(self, prompt: str) -> CoherenceValidationResult:
        """
        Validate prompt coherence.
        
        Args:
            prompt: Fully assembled prompt ready for API
            
        Returns:
            CoherenceValidationResult with issues and score
        """
        result = CoherenceValidationResult(is_coherent=True)
        
        # 1. Detect sections
        sections = self._detect_sections(prompt)
        result.sections_detected = {
            "Context/Facts": sections.get('context') is not None,
            "Voice": sections.get('voice') is not None,
            "Humanness Layer": sections.get('humanness') is not None,
            "Requirements": sections.get('requirements') is not None,
            "Component Template": sections.get('component') is not None
        }
        
        # 2. Check separation of concerns
        self._check_separation(prompt, sections, result)
        
        # 3. Check for contradictions
        self._check_contradictions(prompt, sections, result)
        
        # 4. Check for duplications
        self._check_duplications(prompt, sections, result)
        
        # 5. Check for voice instruction leaks
        self._check_voice_leaks(prompt, sections, result)
        
        # 6. Check length instructions consistency
        self._check_length_consistency(prompt, sections, result)
        
        # 7. Check forbidden phrase instructions
        self._check_forbidden_consistency(prompt, sections, result)
        
        self.logger.info(f"Coherence validation: {result.get_summary()}")
        return result
    
    def _detect_sections(self, prompt: str) -> Dict[str, Tuple[int, int]]:
        """
        Detect major sections in prompt and their line ranges.
        
        Returns:
            Dict mapping section name to (start_line, end_line) tuple
        """
        sections = {}
        lines = prompt.split('\n')
        
        for i, line in enumerate(lines):
            line_upper = line.upper()
            
            # Context section
            if 'TOPIC:' in line or 'MATERIAL INFORMATION:' in line or 'FACTUAL INFORMATION:' in line:
                sections['context'] = (i, self._find_section_end(lines, i))
            
            # Voice section
            if line.startswith('VOICE:') or 'VOICE CHARACTERISTICS:' in line_upper or 'VOICE INSTRUCTIONS:' in line_upper:
                sections['voice'] = (i, self._find_voice_section_end(lines, i))
            
            # Humanness layer (between voice and requirements)
            if 'HUMANNESS' in line_upper or 'ANTI-AI' in line_upper:
                sections['humanness'] = (i, self._find_section_end(lines, i))
            
            # Requirements section
            if line.startswith('REQUIREMENTS:') or 'TECHNICAL REQUIREMENTS:' in line_upper:
                sections['requirements'] = (i, self._find_section_end(lines, i))
            
            # Component-specific instructions (from template)
            if any(marker in line for marker in ['MICRO:', 'FAQ:', 'DESCRIPTION:', 'CAPTION:']):
                sections['component'] = (i, self._find_section_end(lines, i))
        
        return sections
    
    def _find_section_end(self, lines: List[str], start: int) -> int:
        """Find where section ends (next major section or end of prompt)"""
        major_markers = ['VOICE:', 'REQUIREMENTS:', 'TOPIC:', 'Generate', 'Write', 'Create']
        
        for i in range(start + 1, len(lines)):
            if any(marker in lines[i] for marker in major_markers):
                return i - 1
        return len(lines) - 1

    def _find_voice_section_end(self, lines: List[str], start: int) -> int:
        """Find end of voice section using robust boundaries for long persona blocks."""
        voice_end_markers = ['REQUIREMENTS:', '=== HUMANNESS', 'OUTPUT FORMAT:']
        for i in range(start + 1, len(lines)):
            upper = lines[i].upper()
            if any(marker in upper for marker in voice_end_markers):
                return i - 1
        return len(lines) - 1
    
    def _check_separation(
        self,
        prompt: str,
        sections: Dict[str, Tuple[int, int]],
        result: CoherenceValidationResult
    ):
        """Check if concerns are properly separated"""
        lines = prompt.split('\n')
        
        # Voice instructions should NOT appear in requirements
        if 'requirements' in sections and 'voice' in sections:
            req_start, req_end = sections['requirements']
            req_text = '\n'.join(lines[req_start:req_end+1])
            
            voice_keywords = [
                'conversational', 'casual', 'formal tone', 'writing style',
                'regional patterns', 'ESL traits', 'colloquialism'
            ]
            
            for keyword in voice_keywords:
                if keyword.lower() in req_text.lower():
                    result.add_issue(CoherenceIssue(
                        issue_type=CoherenceIssueType.SEPARATION_VIOLATION,
                        severity="ERROR",
                        message=f"Voice instruction '{keyword}' found in REQUIREMENTS section",
                        section1="REQUIREMENTS",
                        section2="VOICE",
                        evidence1=req_text[:200],
                        suggestion="Move voice instructions to VOICE section only"
                    ))
        
        # Content instructions should NOT appear in system prompt/voice
        if 'voice' in sections:
            voice_start, voice_end = sections['voice']
            voice_text = '\n'.join(lines[voice_start:voice_end+1])
            
            content_keywords = [
                'focus on', 'emphasize', 'structure should', 'format must',
                'start with', 'include sections'
            ]
            
            for keyword in content_keywords:
                if keyword.lower() in voice_text.lower():
                    result.add_issue(CoherenceIssue(
                        issue_type=CoherenceIssueType.SEPARATION_VIOLATION,
                        severity="WARNING",
                        message=f"Content instruction '{keyword}' found in VOICE section",
                        section1="VOICE",
                        evidence1=voice_text[:200],
                        suggestion="Move content instructions to component template"
                    ))
    
    def _check_contradictions(
        self,
        prompt: str,
        sections: Dict[str, Tuple[int, int]],
        result: CoherenceValidationResult
    ):
        """Check for contradictory instructions"""
        lines = prompt.split('\n')

        # Exclude VOICE section from contradiction checks to avoid false positives
        # from persona examples (e.g., "patterns detailed for nationality").
        if 'voice' in sections:
            voice_start, voice_end = sections['voice']
            scan_lines = [line for idx, line in enumerate(lines) if not (voice_start <= idx <= voice_end)]
            contradiction_scan_text = '\n'.join(scan_lines)
        else:
            contradiction_scan_text = prompt

        # Check for opposing length instructions
        length_patterns = [
            (r'(\d+)\s*words', 'word count'),
            (r'(\d+)\s*sentences', 'sentence count'),
            (r'brief|short|concise', 'brevity'),
            (r'detailed|comprehensive|thorough', 'detail')
        ]
        
        found_lengths = []
        for pattern, label in length_patterns:
            matches = re.finditer(pattern, contradiction_scan_text, re.IGNORECASE)
            for match in matches:
                found_lengths.append((label, match.group(), match.start()))
        
        # Check for contradicting length instructions
        if len(found_lengths) > 1:
            has_brief = any('brevity' in l[0] for l in found_lengths)
            has_detailed = any('detail' in l[0] for l in found_lengths)
            
            if has_brief and has_detailed:
                result.add_issue(CoherenceIssue(
                    issue_type=CoherenceIssueType.CONTRADICTION,
                    severity="ERROR",
                    message="Contradictory length instructions: both 'brief' and 'detailed' specified",
                    section1="REQUIREMENTS",
                    evidence1="Found: brief/short/concise",
                    evidence2="Also found: detailed/comprehensive/thorough",
                    suggestion="Choose one length target and remove conflicting instructions"
                ))
        
        # Check for tone contradictions using explicit tone directives only.
        # Avoid broad keyword matching that creates false positives from examples.
        tone_patterns = {
            'formal': [
                r'\bformal\s+tone\b',
                r'\bprofessional\s+tone\b',
                r'\bobjective\s+tone\b',
                r'\bkeep\s+it\s+formal\b',
            ],
            'casual': [
                r'\bcasual\s+tone\b',
                r'\bconversational\s+tone\b',
                r'\bfriendly\s+tone\b',
                r'\bapproachable\s+tone\b',
                r'\bkeep\s+it\s+casual\b',
            ],
            'neutral': [
                r'\bneutral\s+tone\b',
                r'\bbalanced\s+tone\b',
                r'\bdetached\s+tone\b',
            ]
        }

        def _has_positive_tone_signal(pattern: str) -> bool:
            """Return True only when tone directive appears as a positive instruction (not negated/forbidden)."""
            for match in re.finditer(pattern, contradiction_scan_text, re.IGNORECASE):
                start = match.start()
                context_window = contradiction_scan_text[max(0, start - 60):start].lower()

                # Ignore negated/forbidden mentions (e.g., "no conversational tone")
                negation_markers = [
                    'no ', 'not ', 'never ', 'avoid ', 'forbidden',
                    'do not ', "don't ", 'must not ', 'without '
                ]
                if any(marker in context_window for marker in negation_markers):
                    continue

                return True
            return False

        found_tones = []
        for tone_type, patterns in tone_patterns.items():
            for pattern in patterns:
                if _has_positive_tone_signal(pattern):
                    found_tones.append((tone_type, pattern))
                    break
        
        # Formal and casual are contradictory
        has_formal = any(t[0] == 'formal' for t in found_tones)
        has_casual = any(t[0] == 'casual' for t in found_tones)
        
        if has_formal and has_casual:
            formal_words = [t[1] for t in found_tones if t[0] == 'formal']
            casual_words = [t[1] for t in found_tones if t[0] == 'casual']
            
            result.add_issue(CoherenceIssue(
                issue_type=CoherenceIssueType.CONTRADICTION,
                severity="CRITICAL",
                message="Contradictory tone instructions: both formal and casual specified",
                section1="VOICE",
                evidence1=f"Formal keywords: {', '.join(formal_words)}",
                evidence2=f"Casual keywords: {', '.join(casual_words)}",
                suggestion="Personas define tone - remove conflicting tone instructions"
            ))
    
    def _check_duplications(
        self,
        prompt: str,
        sections: Dict[str, Tuple[int, int]],
        result: CoherenceValidationResult
    ):
        """Check for duplicate instructions"""
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', prompt)
        
        # Find duplicate or very similar sentences
        seen = {}
        for i, sent in enumerate(sentences):
            # Normalize: lowercase, remove extra spaces, remove punctuation
            normalized = re.sub(r'[^\w\s]', '', sent.lower())
            normalized = ' '.join(normalized.split())
            
            if len(normalized) < 30:  # Skip short fragments
                continue
            
            # Check for exact duplicates
            if normalized in seen:
                result.add_issue(CoherenceIssue(
                    issue_type=CoherenceIssueType.DUPLICATION,
                    severity="WARNING",
                    message="Duplicate instruction found",
                    section1="Multiple locations",
                    evidence1=sent[:150],
                    suggestion="Remove duplicate - say each instruction once"
                ))
            else:
                seen[normalized] = i
    
    def _check_voice_leaks(
        self,
        prompt: str,
        sections: Dict[str, Tuple[int, int]],
        result: CoherenceValidationResult
    ):
        """Check if voice instructions leak outside voice section"""
        lines = prompt.split('\n')
        
        if 'voice' not in sections:
            return  # No voice section to check
        
        voice_start, voice_end = sections['voice']
        
        # Voice-specific keywords that should ONLY appear in voice section
        voice_only_keywords = [
            'forbidden phrases', 'forbidden:', 'tone requirements:',
            'core style:', 'regional patterns:', 'esl traits'
        ]
        
        for i, line in enumerate(lines):
            # Skip voice section itself and humanness section (forbidden can appear there)
            if voice_start <= i <= voice_end:
                continue
            
            # Also skip humanness section if present
            if 'humanness' in sections:
                humanness_start, humanness_end = sections['humanness']
                if humanness_start <= i <= humanness_end:
                    continue
            
            for keyword in voice_only_keywords:
                if keyword.lower() in line.lower():
                    result.add_issue(CoherenceIssue(
                        issue_type=CoherenceIssueType.VOICE_LEAK,
                        severity="ERROR",
                        message=f"Voice instruction '{keyword}' leaked outside VOICE section",
                        section1=f"Line {i}",
                        section2="VOICE",
                        evidence1=line.strip(),
                        suggestion="Consolidate all voice instructions in VOICE section"
                    ))
    
    def _check_length_consistency(
        self,
        prompt: str,
        sections: Dict[str, Tuple[int, int]],
        result: CoherenceValidationResult
    ):
        """Check that length instructions don't conflict"""
        # Extract all numeric length mentions
        length_mentions = []
        
        # Word count patterns
        word_matches = re.finditer(r'(\d+)[\s-]*(\d*)\s*words?', prompt, re.IGNORECASE)
        for match in word_matches:
            if match.group(2):  # Range: "50-150 words"
                length_mentions.append(('words', int(match.group(1)), int(match.group(2))))
            else:  # Single: "100 words"
                length_mentions.append(('words', int(match.group(1)), int(match.group(1))))
        
        # Check if multiple different word counts specified
        if len(length_mentions) > 1:
            # Check if they're consistent (allow ±100% variation for randomized humanness)
            first_min, first_max = length_mentions[0][1], length_mentions[0][2]
            
            for unit, min_val, max_val in length_mentions[1:]:
                if unit == 'words':
                    # Check if ranges overlap or are close (tolerance: 0.3x to 2.0x for 70% variation)
                    if max_val < first_min * 0.3 or min_val > first_max * 2.0:
                        result.add_issue(CoherenceIssue(
                            issue_type=CoherenceIssueType.CONTRADICTION,
                            severity="ERROR",
                            message="Inconsistent length targets specified",
                            section1="Multiple locations",
                            evidence1=f"Found: {first_min}-{first_max} words",
                            evidence2=f"Also found: {min_val}-{max_val} words",
                            suggestion="Use single length target (specify in humanness layer only)"
                        ))
    
    def _check_forbidden_consistency(
        self,
        prompt: str,
        sections: Dict[str, Tuple[int, int]],
        result: CoherenceValidationResult
    ):
        """Check that forbidden phrase instructions are consistent"""
        # Find all "FORBIDDEN" sections
        forbidden_sections = []
        lines = prompt.split('\n')
        
        for i, line in enumerate(lines):
            if 'FORBIDDEN' in line.upper():
                # Extract forbidden phrases from this section
                phrases = re.findall(r'["\']([^"\']+)["\']', line)
                if not phrases:
                    # Try comma-separated format
                    after_colon = line.split(':', 1)
                    if len(after_colon) > 1:
                        phrases = [p.strip() for p in after_colon[1].split(',')]
                
                if phrases:
                    forbidden_sections.append((i, phrases))
        
        # Check for consistency between sections
        if len(forbidden_sections) > 1:
            # Compare each pair
            for i in range(len(forbidden_sections) - 1):
                line1, phrases1 = forbidden_sections[i]
                line2, phrases2 = forbidden_sections[i + 1]
                
                set1 = set(p.lower().strip() for p in phrases1)
                set2 = set(p.lower().strip() for p in phrases2)
                
                # Check if lists are significantly different
                if len(set1.symmetric_difference(set2)) > max(len(set1), len(set2)) * 0.5:
                    result.add_issue(CoherenceIssue(
                        issue_type=CoherenceIssueType.CONFUSION,
                        severity="WARNING",
                        message="Multiple FORBIDDEN phrase lists with different content",
                        section1=f"Line {line1}",
                        section2=f"Line {line2}",
                        evidence1=f"Phrases: {', '.join(list(set1)[:5])}...",
                        evidence2=f"Phrases: {', '.join(list(set2)[:5])}...",
                        suggestion="Consolidate forbidden phrases into single list in VOICE section"
                    ))


def validate_prompt_coherence(prompt: str) -> CoherenceValidationResult:
    """
    Quick validation function.
    
    Args:
        prompt: Assembled prompt to validate
        
    Returns:
        CoherenceValidationResult
        
    Example:
        result = validate_prompt_coherence(prompt)
        if not result.is_coherent:
            raise ValueError(result.format_report())
    """
    validator = PromptCoherenceValidator()
    return validator.validate(prompt)
