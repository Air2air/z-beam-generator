#!/usr/bin/env python3
"""
Unified Prompt Validator

Single entry point for all validation stages:
- Early (pre-research): Config, templates, material validation
- Prompt (pre-generation): Length, logic, auto-optimization
- Post (post-generation): Realism, compliance, physics

Provides AI-friendly output with:
- Natural language fix instructions
- Programmatic FixActions for auto-correction
- Consistent ValidationReport format

Author: AI Assistant
Date: November 28, 2025
"""

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class ValidationStatus(Enum):
    """Overall validation status"""
    PASS = "PASS"           # All checks passed
    WARN = "WARN"           # Minor issues, can proceed
    FAIL = "FAIL"           # Must fix before proceeding
    CRITICAL = "CRITICAL"   # System error, cannot proceed


class ValidationStage(Enum):
    """Validation pipeline stage"""
    EARLY = "early"         # Pre-research validation
    PROMPT = "prompt"       # Pre-generation validation
    POST = "post"           # Post-generation validation


class IssueSeverity(Enum):
    """Issue severity level"""
    CRITICAL = "CRITICAL"   # Must fix - will fail
    HIGH = "HIGH"           # Should fix - likely problems
    MEDIUM = "MEDIUM"       # May fix - could improve
    LOW = "LOW"             # Optional - suggestions


class IssueCategory(Enum):
    """Issue category"""
    CONFIG = "CONFIG"           # Configuration issues
    TEMPLATE = "TEMPLATE"       # Template loading issues
    LENGTH = "LENGTH"           # Prompt length issues
    LOGIC = "LOGIC"             # Contradictions, confusion
    QUALITY = "QUALITY"         # Clarity, specificity
    PHYSICS = "PHYSICS"         # Physics compliance
    REALISM = "REALISM"         # Realism score
    COMPLIANCE = "COMPLIANCE"   # Prompt compliance
    FEEDBACK = "FEEDBACK"       # Feedback consistency
    CONTAMINATION = "CONTAMINATION"  # Material-contamination compatibility


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class FixAction:
    """
    Single actionable fix that can be auto-applied.
    
    AI assistants can use these to programmatically fix issues
    or follow the ai_instruction for manual fixing.
    """
    action_type: Literal['replace', 'remove', 'append', 'prepend', 'optimize']
    severity: IssueSeverity
    description: str
    
    # For auto-application
    target: str = ""              # What to find
    replacement: str = ""         # What to replace with
    location: str = ""            # Where in prompt
    
    # For AI assistants
    ai_instruction: str = ""      # Natural language instruction
    
    # Safety
    safe_to_auto_apply: bool = True   # Can apply automatically
    requires_review: bool = False     # AI should verify after
    
    def apply(self, text: str) -> str:
        """Apply this fix to text."""
        if not self.safe_to_auto_apply:
            return text
        
        if self.action_type == 'replace' and self.target:
            return text.replace(self.target, self.replacement, 1)
        elif self.action_type == 'remove' and self.target:
            return text.replace(self.target, '', 1)
        elif self.action_type == 'append':
            return text + self.replacement
        elif self.action_type == 'prepend':
            return self.replacement + text
        
        return text


@dataclass
class ValidationIssue:
    """Single validation issue with actionable fix."""
    severity: IssueSeverity
    category: IssueCategory
    message: str
    location: str = ""
    suggestion: str = ""
    fix_action: Optional[FixAction] = None
    
    def __str__(self) -> str:
        loc = f" [{self.location}]" if self.location else ""
        sug = f"\n  💡 {self.suggestion}" if self.suggestion else ""
        return f"{self.severity.value} ({self.category.value}){loc}: {self.message}{sug}"


@dataclass
class ValidationReport:
    """
    Universal validation result for all stages.
    
    Usable by both humans (via to_report()) and AI assistants
    (via fix_instructions and fix_actions).
    """
    # Overall status
    status: ValidationStatus = ValidationStatus.PASS
    stage: ValidationStage = ValidationStage.PROMPT
    
    # Scores (0-100)
    scores: Dict[str, float] = field(default_factory=dict)
    
    # Issues found
    issues: List[ValidationIssue] = field(default_factory=list)
    
    # Fixes
    fix_actions: List[FixAction] = field(default_factory=list)
    _fix_instructions: str = ""
    
    # Metrics
    prompt_length: int = 0
    word_count: int = 0
    estimated_tokens: int = 0
    
    # Context
    material: str = ""
    attempt_number: int = 1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Flags
    has_critical: bool = False
    has_errors: bool = False
    has_warnings: bool = False
    
    def add_issue(self, issue: ValidationIssue, fix: Optional[FixAction] = None):
        """Add issue and update status flags."""
        self.issues.append(issue)
        
        if fix:
            issue.fix_action = fix
            self.fix_actions.append(fix)
        
        if issue.severity == IssueSeverity.CRITICAL:
            self.has_critical = True
            self.status = ValidationStatus.CRITICAL
        elif issue.severity == IssueSeverity.HIGH:
            self.has_errors = True
            if self.status not in (ValidationStatus.CRITICAL,):
                self.status = ValidationStatus.FAIL
        elif issue.severity == IssueSeverity.MEDIUM:
            self.has_warnings = True
            if self.status == ValidationStatus.PASS:
                self.status = ValidationStatus.WARN
    
    @property
    def fix_instructions(self) -> str:
        """Get natural language fix instructions for AI assistants."""
        if self._fix_instructions:
            return self._fix_instructions
        
        if not self.issues:
            return "✅ No issues found - prompt is valid."
        
        lines = [
            f"{'🚨' if self.has_critical else '⚠️'} FIX REQUIRED: {len(self.issues)} issue(s) found",
            "",
            "RECOMMENDED ACTIONS (in priority order):",
            ""
        ]
        
        # Group by severity
        by_severity = {}
        for issue in self.issues:
            sev = issue.severity.value
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(issue)
        
        action_num = 1
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if severity not in by_severity:
                continue
            
            for issue in by_severity[severity]:
                lines.append(f"{action_num}. [{severity}] {issue.message}")
                if issue.fix_action and issue.fix_action.ai_instruction:
                    lines.append(f"   → {issue.fix_action.ai_instruction}")
                elif issue.suggestion:
                    lines.append(f"   → {issue.suggestion}")
                lines.append("")
                action_num += 1
        
        if self.fix_actions:
            safe_fixes = sum(1 for f in self.fix_actions if f.safe_to_auto_apply)
            if safe_fixes > 0:
                lines.append(f"AUTO-FIX AVAILABLE: {safe_fixes} issue(s) can be fixed automatically.")
                lines.append("Call report.apply_auto_fixes(prompt) to apply safe fixes.")
        
        return "\n".join(lines)
    
    @fix_instructions.setter
    def fix_instructions(self, value: str):
        self._fix_instructions = value
    
    def apply_auto_fixes(self, text: str) -> str:
        """Apply all safe auto-fixes to text."""
        result = text
        applied = 0
        
        for fix in self.fix_actions:
            if fix.safe_to_auto_apply:
                before = len(result)
                result = fix.apply(result)
                if len(result) != before or fix.replacement:
                    applied += 1
                    logger.info(f"🔧 Applied fix: {fix.description}")
        
        if applied > 0:
            logger.info(f"✅ Applied {applied} auto-fixes")
        
        return result
    
    def get_ai_prompt(self) -> str:
        """Get correction prompt for retry generation."""
        if self.status == ValidationStatus.PASS:
            return ""
        
        lines = [
            "🚨 CRITICAL CORRECTIONS FROM FAILED VALIDATION:",
            "The previous generation FAILED. FIX THESE ISSUES:",
            ""
        ]
        
        for issue in self.issues:
            if issue.severity in (IssueSeverity.CRITICAL, IssueSeverity.HIGH):
                if issue.fix_action:
                    lines.append(f"• {issue.fix_action.ai_instruction or issue.message}")
                else:
                    lines.append(f"• {issue.message}")
        
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Export for logging/learning."""
        data = {
            'status': self.status.value,
            'stage': self.stage.value,
            'scores': self.scores,
            'issues': [
                {
                    'severity': i.severity.value,
                    'category': i.category.value,
                    'message': i.message,
                    'location': i.location
                }
                for i in self.issues
            ],
            'metrics': {
                'prompt_length': self.prompt_length,
                'word_count': self.word_count,
                'estimated_tokens': self.estimated_tokens
            },
            'context': {
                'material': self.material,
                'attempt_number': self.attempt_number,
                'timestamp': self.timestamp
            }
        }
        return json.dumps(data, indent=2)
    
    def to_report(self) -> str:
        """Human-readable validation report."""
        lines = [
            "=" * 80,
            "🔍 VALIDATION REPORT",
            "=" * 80,
            "",
            f"Status: {self._status_icon()} {self.status.value}",
            f"Stage: {self.stage.value}",
        ]
        
        if self.material:
            lines.append(f"Material: {self.material}")
        
        if self.scores:
            lines.append(f"Scores: {', '.join(f'{k}={v:.0f}' for k, v in self.scores.items())}")
        
        lines.append(f"Length: {self.prompt_length} chars ({self.word_count} words)")
        lines.append("")
        
        if not self.issues:
            lines.append("✅ No issues found - validation passed")
        else:
            lines.append(f"Issues: {len(self.issues)}")
            lines.append("-" * 80)
            
            for i, issue in enumerate(self.issues, 1):
                lines.append(f"\n{i}. {issue}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _status_icon(self) -> str:
        return {
            ValidationStatus.PASS: "✅",
            ValidationStatus.WARN: "⚠️",
            ValidationStatus.FAIL: "❌",
            ValidationStatus.CRITICAL: "🚨"
        }.get(self.status, "❓")


# =============================================================================
# STAGE VALIDATORS
# =============================================================================

class EarlyStageValidator:
    """
    Stage 1: Pre-research validation.
    
    Validates BEFORE any prompt building:
    - Material exists
    - Config is valid
    - Templates exist
    - Feedback is consistent
    - API keys configured
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        self.prompts_dir = prompts_dir
    
    def validate(
        self,
        material: str,
        config: Dict[str, Any],
        check_templates: bool = True,
        check_feedback: bool = True
    ) -> ValidationReport:
        """Run early stage validation."""
        report = ValidationReport(stage=ValidationStage.EARLY, material=material)
        
        # Check material name
        if not material or not material.strip():
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category=IssueCategory.CONFIG,
                    message="Material name is required",
                    suggestion="Provide a valid material name"
                )
            )
            return report
        
        # Check config
        self._validate_config(config, report)
        
        # Check templates exist
        if check_templates and self.prompts_dir:
            self._validate_templates(report)
        
        # Check feedback consistency
        if check_feedback and self.prompts_dir:
            self._validate_feedback(report)
        
        return report
    
    def _validate_config(self, config: Dict[str, Any], report: ValidationReport):
        """Validate configuration values."""
        # Check category
        if 'category' not in config or not config['category']:
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.CONFIG,
                    message="Material category not specified",
                    suggestion="Provide category for better contamination research"
                )
            )
        
        # Check uniformity range
        uniformity = config.get('contamination_uniformity', 3)
        if not isinstance(uniformity, int) or uniformity < 1 or uniformity > 5:
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.CONFIG,
                    message=f"Invalid contamination_uniformity: {uniformity} (must be 1-5)",
                    suggestion="Set contamination_uniformity to a value between 1 and 5"
                ),
                FixAction(
                    action_type='replace',
                    severity=IssueSeverity.HIGH,
                    description="Fix uniformity value",
                    ai_instruction="Set contamination_uniformity to 3 (default)"
                )
            )
    
    def _validate_templates(self, report: ValidationReport):
        """Validate required templates exist."""
        required_templates = [
            'generation/base_structure.txt',
            'generation/realism_physics.txt',
            'validation/realism_criteria.txt',
        ]
        
        for template in required_templates:
            path = self.prompts_dir / template
            if not path.exists():
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.TEMPLATE,
                        message=f"Required template missing: {template}",
                        location=str(path),
                        suggestion=f"Create or restore {template}"
                    )
                )
    
    def _validate_feedback(self, report: ValidationReport):
        """Validate feedback consistency."""
        feedback_path = self.prompts_dir / 'feedback' / 'user_corrections.txt'
        if not feedback_path.exists():
            return  # No feedback file is OK
        
        # Import feedback validator
        try:
            from domains.materials.image.tools.validate_feedback import (
                FeedbackValidator,
            )
            validator = FeedbackValidator(self.prompts_dir)
            validator.load_templates()
            result = validator.validate_feedback()
            
            if result.get('conflicts'):
                for conflict in result['conflicts'][:3]:
                    report.add_issue(
                        ValidationIssue(
                            severity=IssueSeverity.HIGH,
                            category=IssueCategory.FEEDBACK,
                            message=f"Feedback contradiction: {conflict.get('description', 'Unknown')}",
                            location=conflict.get('file', ''),
                            suggestion="Resolve contradicting feedback rules"
                        )
                    )
        except ImportError:
            pass  # Feedback validator not available


class PromptStageValidator:
    """
    Stage 2: Pre-generation validation.
    
    Validates BEFORE API call:
    - Length within limits
    - No contradictions
    - No duplications
    - Required sections present
    - Material-contamination compatibility
    - Physics plausibility
    - AI clarity (no confusion, contradiction, redundancy)
    - Auto-optimize if needed
    """
    
    # API Limits
    IMAGEN_LIMIT = 4096
    GROK_LIMIT = 8000
    TARGET_LENGTH = 3500
    WARNING_THRESHOLD = 3800
    
    # Forbidden content - material-contamination impossibilities (from payload_validator)
    FORBIDDEN_CONTENT = [
        # Material-contamination impossibilities
        (r'\brust\b.*\baluminum\b', 'Aluminum does not rust (forms oxide, not rust)'),
        (r'\baluminum\b.*\brust\b', 'Aluminum does not rust (forms oxide, not rust)'),
        (r'\brust\b.*\bplastic\b', 'Plastic cannot rust (ferrous metals only)'),
        (r'\bplastic\b.*\brust\b', 'Plastic cannot rust (ferrous metals only)'),
        (r'\brust\b.*\bglass\b', 'Glass cannot rust (ferrous metals only)'),
        (r'\brust\b.*\bcopper\b', 'Copper does not rust (forms patina/verdigris, not rust)'),
        (r'\bcopper\b.*\brust\b', 'Copper does not rust (forms patina/verdigris, not rust)'),
        (r'\brust\b.*\bbronze\b', 'Bronze does not rust (forms patina, not rust)'),
        (r'\bbronze\b.*\brust\b', 'Bronze does not rust (forms patina, not rust)'),
        # Physics violations
        (r'\bfloating\b.*\bcontaminat', 'Contamination must obey gravity'),
        (r'\bupward\b.*\bdrip', 'Drips cannot flow upward (gravity violation)'),
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
    
    # Contradiction patterns - actual contradictions, not negations
    CONTRADICTION_PATTERNS = [
        (r'\b(must|should)\s+be\s+(thick|heavy|caked)\b.*\b(must|should)\s+be\s+(thin|light)\b', 'thickness'),
        (r'\b(must|should)\s+be\s+perfectly\s+clean\b.*\b(must|should)\s+show\s+residual\b', 'cleanliness'),
        (r'\b(must|should)\s+be\s+uniform\b.*\b(must|should)\s+be\s+uneven\b', 'distribution'),
    ]
    
    # AI Clarity patterns - check for AI-confusing content
    AI_CONFUSION_PATTERNS = [
        # Contradictory instructions within same prompt
        (r'(DO NOT|NEVER|AVOID)\s+[\w\s]+\.\s*.*?(MUST|ALWAYS|REQUIRED):\s*\1', 'Contradictory DO NOT / MUST for same concept'),
        (r'(short|brief|concise).*\b(detailed|comprehensive|thorough)\b', 'Length guidance contradiction: short vs detailed'),
        (r'(formal|professional).*\b(casual|conversational|informal)\b', 'Tone contradiction: formal vs casual'),
        (r'(technical|precise).*\b(simple|plain|accessible)\b', 'Style contradiction: technical vs simple'),
        # Multiple conflicting lengths
        (r'\b(\d+)\s*words?\b.*\b(\d+)\s*words?\b', 'Multiple word count targets'),
        (r'\b(\d+)\s*sentences?\b.*\b(\d+)\s*sentences?\b', 'Multiple sentence count targets'),
    ]
    
    # Redundancy patterns - repeated instructions that add confusion
    REDUNDANCY_PATTERNS = [
        (r'(CRITICAL|IMPORTANT|REQUIRED)[:\s]+.*\1[:\s]+', 'Repeated emphasis markers'),
        (r'(NO|NEVER|AVOID)\s+(\w+).*\1\s+\2', 'Repeated prohibition'),
        (r'(MUST|ALWAYS)\s+(\w+).*\1\s+\2', 'Repeated requirement'),
    ]
    
    # Required content patterns
    REQUIRED_PATTERNS = {
        'split_view': r'(split|side-by-side|before.*after|left.*right)',
        'contamination': r'(contamination|contaminated|contaminant)',
        'material_name': None,  # Checked separately
    }
    
    def validate(
        self,
        prompt: str,
        negative_prompt: str = "",
        material: str = "",
        auto_optimize: bool = True,
        prompt_type: str = "image"
    ) -> ValidationReport:
        """
        Run prompt stage validation.
        
        Args:
            prompt: The orchestrated final prompt
            negative_prompt: Negative prompt (for image generation)
            material: Material name for context
            auto_optimize: Whether to suggest auto-optimizations
            prompt_type: Type of prompt ('text' for Grok, 'image' for Imagen)
            
        Returns:
            ValidationReport with all issues found
        """
        report = ValidationReport(
            stage=ValidationStage.PROMPT,
            material=material,
            prompt_length=len(prompt),
            word_count=len(prompt.split()),
            estimated_tokens=len(prompt) // 4
        )
        
        # Determine limit based on prompt type
        limit = self.GROK_LIMIT if prompt_type == 'text' else self.IMAGEN_LIMIT
        
        # Check length
        self._validate_length(prompt, report, limit)
        
        # Check logic (contradictions)
        self._validate_logic(prompt, report)
        
        # Check duplications
        self._validate_duplications(prompt, report)
        
        # NEW: Check AI clarity (confusion, contradiction, redundancy)
        self._validate_ai_clarity(prompt, report)
        
        # Check required content (image prompts only)
        if prompt_type == 'image':
            self._validate_required_content(prompt, material, report)
        
        # Check material-contamination compatibility and physics
        self._validate_contamination_physics(prompt, report)
        
        # Check quality anti-patterns
        self._validate_quality(prompt, report)
        
        # Check negative prompt
        if negative_prompt:
            self._validate_negative_prompt(negative_prompt, report)
        
        # Calculate overall AI clarity score
        ai_issues = sum(1 for i in report.issues if 'AI' in str(i.message) or 'contradiction' in str(i.message).lower())
        report.scores['ai_clarity'] = max(0, 100 - ai_issues * 15)
        
        return report
    
    def _validate_length(self, prompt: str, report: ValidationReport, limit: int = None):
        """Validate prompt length."""
        if limit is None:
            limit = self.IMAGEN_LIMIT
            
        length = len(prompt)
        
        if length > limit:
            over = length - limit
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category=IssueCategory.LENGTH,
                    message=f"Prompt exceeds limit: {length}/{limit} chars (+{over})",
                    suggestion=f"Must reduce by {over} characters"
                ),
                FixAction(
                    action_type='optimize',
                    severity=IssueSeverity.CRITICAL,
                    description=f"Reduce prompt by {over} chars",
                    ai_instruction=f"Use PromptOptimizer to reduce prompt by at least {over} characters",
                    safe_to_auto_apply=False,
                    requires_review=True
                )
            )
        elif length > self.WARNING_THRESHOLD:
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.LENGTH,
                    message=f"Prompt near limit: {length}/{self.IMAGEN_LIMIT} chars",
                    suggestion="Consider optimizing to avoid issues"
                )
            )
        
        # Update score
        length_score = max(0, 100 - (length - self.TARGET_LENGTH) / 10) if length > self.TARGET_LENGTH else 100
        report.scores['length'] = min(100, length_score)
    
    def _validate_logic(self, prompt: str, report: ValidationReport):
        """Check for contradictions."""
        prompt_lower = prompt.lower()
        
        for pattern, contradiction_type in self.CONTRADICTION_PATTERNS:
            # Skip if pattern is in a negation context
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                # Check if it's a negation (e.g., "never thick")
                negation_check = re.search(
                    r'(never|no|not|avoid|don\'t)\s+' + pattern.split(r'\b')[1],
                    prompt_lower,
                    re.IGNORECASE
                )
                if not negation_check:
                    report.add_issue(
                        ValidationIssue(
                            severity=IssueSeverity.HIGH,
                            category=IssueCategory.LOGIC,
                            message=f"Potential contradiction ({contradiction_type})",
                            suggestion=f"Review {contradiction_type} requirements for consistency"
                        )
                    )
        
        # Calculate logic score
        contradictions = sum(1 for i in report.issues if i.category == IssueCategory.LOGIC)
        report.scores['logic'] = max(0, 100 - contradictions * 25)
    
    def _validate_duplications(self, prompt: str, report: ValidationReport):
        """Check for duplicate content."""
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', prompt)
        
        seen = set()
        duplicates = 0
        
        for sentence in sentences:
            clean = sentence.strip().lower()
            if not clean or len(clean) < 30:
                continue
            
            if clean in seen:
                duplicates += 1
                if duplicates <= 3:  # Report first 3
                    report.add_issue(
                        ValidationIssue(
                            severity=IssueSeverity.MEDIUM,
                            category=IssueCategory.QUALITY,
                            message=f"Duplicate sentence: \"{sentence[:50]}...\"",
                            suggestion="Remove redundant duplicate"
                        ),
                        FixAction(
                            action_type='remove',
                            severity=IssueSeverity.MEDIUM,
                            description="Remove duplicate sentence",
                            target=sentence,
                            ai_instruction=f"Remove duplicate: \"{sentence[:50]}...\"",
                            safe_to_auto_apply=True
                        )
                    )
            seen.add(clean)
        
        # Calculate quality score
        report.scores['quality'] = max(0, 100 - duplicates * 10)
    
    def _validate_ai_clarity(self, prompt: str, report: ValidationReport):
        """
        Validate prompt is clear and understandable for AI assistants.
        
        Checks for:
        1. Confusion: Contradictory instructions that confuse the AI
        2. Contradiction: Mutually exclusive requirements
        3. Redundancy: Repeated instructions that add noise
        4. Structure: Clear, parseable prompt organization
        
        AI assistants need unambiguous, non-conflicting instructions.
        This validation ensures the orchestrated prompt is AI-friendly.
        """
        prompt_lower = prompt.lower()
        confusion_count = 0
        redundancy_count = 0
        
        # 1. Check for AI confusion patterns (contradictory instructions)
        for pattern, issue_desc in self.AI_CONFUSION_PATTERNS:
            matches = list(re.finditer(pattern, prompt_lower, re.IGNORECASE | re.DOTALL))
            for match in matches[:2]:  # Report first 2 per pattern
                confusion_count += 1
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.LOGIC,
                        message=f"AI confusion: {issue_desc}",
                        location=f"chars {match.start()}-{match.end()}",
                        suggestion="Remove contradicting instruction - AI cannot follow both"
                    ),
                    FixAction(
                        action_type='remove',
                        severity=IssueSeverity.HIGH,
                        description=f"Remove conflicting instruction: {issue_desc}",
                        ai_instruction=f"Resolve contradiction: {issue_desc}. Keep only ONE of the conflicting instructions.",
                        safe_to_auto_apply=False,
                        requires_review=True
                    )
                )
        
        # 2. Check for redundancy patterns (repeated instructions)
        for pattern, issue_desc in self.REDUNDANCY_PATTERNS:
            matches = list(re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL))
            for match in matches[:2]:
                redundancy_count += 1
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.QUALITY,
                        message=f"Redundancy: {issue_desc}",
                        location=f"chars {match.start()}-{match.end()}",
                        suggestion="Remove duplicate instruction - adds noise without value"
                    ),
                    FixAction(
                        action_type='remove',
                        severity=IssueSeverity.MEDIUM,
                        description=f"Remove redundant: {issue_desc}",
                        ai_instruction=f"Remove one occurrence of: {issue_desc}",
                        safe_to_auto_apply=False
                    )
                )
        
        # 3. Check for multiple conflicting section headers
        section_headers = re.findall(r'(?:^|\n)([A-Z][A-Z\s]+):', prompt)
        header_counts = {}
        for header in section_headers:
            header_clean = header.strip().upper()
            header_counts[header_clean] = header_counts.get(header_clean, 0) + 1
        
        for header, count in header_counts.items():
            if count > 1:
                redundancy_count += 1
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.QUALITY,
                        message=f"Duplicate section header '{header}' appears {count} times",
                        suggestion=f"Consolidate '{header}' sections into one for clarity"
                    ),
                    FixAction(
                        action_type='optimize',
                        severity=IssueSeverity.MEDIUM,
                        description=f"Merge duplicate '{header}' sections",
                        ai_instruction=f"Combine the {count} '{header}' sections into a single section",
                        safe_to_auto_apply=False
                    )
                )
        
        # 4. Check for conflicting numeric constraints
        word_counts = re.findall(r'(\d+)\s*(?:to|-)?\s*(\d+)?\s*words?', prompt_lower)
        if len(word_counts) > 1:
            unique_targets = set()
            for match in word_counts:
                if match[1]:  # Range like "50-100 words"
                    unique_targets.add(f"{match[0]}-{match[1]}")
                else:  # Single like "50 words"
                    unique_targets.add(match[0])
            
            if len(unique_targets) > 1:
                confusion_count += 1
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.LOGIC,
                        message=f"Multiple word count targets found: {', '.join(unique_targets)}",
                        suggestion="Use ONE word count target - multiple targets confuse the AI"
                    ),
                    FixAction(
                        action_type='optimize',
                        severity=IssueSeverity.HIGH,
                        description="Consolidate word count targets",
                        ai_instruction="Remove all but one word count instruction. Keep the most specific one.",
                        safe_to_auto_apply=False,
                        requires_review=True
                    )
                )
        
        # 5. Check for too many CRITICAL/IMPORTANT markers (dilutes importance)
        critical_count = len(re.findall(r'\b(CRITICAL|IMPORTANT|MUST|REQUIRED|ESSENTIAL)\b', prompt, re.IGNORECASE))
        if critical_count > 5:
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.QUALITY,
                    message=f"Too many emphasis markers ({critical_count}): dilutes importance",
                    suggestion="Use emphasis sparingly - if everything is CRITICAL, nothing is"
                )
            )
        
        # 6. Calculate AI clarity score
        ai_clarity_score = max(0, 100 - (confusion_count * 20) - (redundancy_count * 10))
        report.scores['ai_clarity'] = ai_clarity_score
        
        # Log summary
        if confusion_count > 0 or redundancy_count > 0:
            logger.warning(
                f"⚠️  AI Clarity issues: {confusion_count} confusion, {redundancy_count} redundancy "
                f"(score: {ai_clarity_score}/100)"
            )
    
    def _validate_required_content(self, prompt: str, material: str, report: ValidationReport):
        """Check required content is present."""
        prompt_lower = prompt.lower()
        
        # Check split view mentioned
        if not re.search(self.REQUIRED_PATTERNS['split_view'], prompt_lower, re.IGNORECASE):
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.COMPLIANCE,
                    message="Missing split-view/before-after composition description",
                    suggestion="Add split-screen composition description"
                )
            )
        
        # Check contamination mentioned
        if not re.search(self.REQUIRED_PATTERNS['contamination'], prompt_lower, re.IGNORECASE):
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.COMPLIANCE,
                    message="Missing contamination description",
                    suggestion="Add contamination patterns to prompt"
                )
            )
        
        # Check material name mentioned
        if material and material.lower() not in prompt_lower:
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.COMPLIANCE,
                    message=f"Material name '{material}' not found in prompt",
                    suggestion=f"Ensure '{material}' is mentioned in prompt"
                )
            )
    
    def _validate_negative_prompt(self, negative: str, report: ValidationReport):
        """Validate negative prompt."""
        # Check for anti-text terms
        anti_text_terms = ['text', 'words', 'letters', 'labels', 'watermarks']
        missing_anti_text = [t for t in anti_text_terms if t.lower() not in negative.lower()]
        
        if missing_anti_text:
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.COMPLIANCE,
                    message=f"Missing anti-text terms in negative prompt: {', '.join(missing_anti_text)}",
                    suggestion="Add missing anti-text terms to negative prompt"
                )
            )
    
    def _validate_contamination_physics(self, prompt: str, report: ValidationReport):
        """
        Check for material-contamination impossibilities and physics violations.
        
        Merged from ImagePromptPayloadValidator for consolidated validation.
        """
        prompt_lower = prompt.lower()
        
        # Check forbidden content (material-contamination impossibilities + physics)
        for pattern, reason in self.FORBIDDEN_CONTENT:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                # Determine category based on pattern
                if 'gravity' in reason.lower() or 'drip' in reason.lower():
                    category = IssueCategory.PHYSICS
                else:
                    category = IssueCategory.CONTAMINATION
                
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.CRITICAL,
                        category=category,
                        message=f"Impossible combination: {reason}",
                        suggestion="Remove this contamination-material combination"
                    ),
                    FixAction(
                        action_type='remove',
                        severity=IssueSeverity.CRITICAL,
                        description=f"Fix: {reason}",
                        ai_instruction=f"Remove or fix impossible combination: {reason}",
                        safe_to_auto_apply=False,
                        requires_review=True
                    )
                )
        
        # Check confusion patterns (ambiguous language)
        for pattern, suggestion in self.CONFUSION_PATTERNS:
            matches = list(re.finditer(pattern, prompt_lower, re.IGNORECASE))
            for match in matches[:2]:  # Limit to 2 per pattern
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.QUALITY,
                        message=f"Ambiguous language: \"{match.group(0)}\"",
                        location=f"chars {match.start()}-{match.end()}",
                        suggestion=suggestion
                    )
                )
    
    def _validate_quality(self, prompt: str, report: ValidationReport):
        """Check for quality anti-patterns (intensifiers, hedging, punctuation)."""
        for pattern, suggestion in self.QUALITY_ANTIPATTERNS:
            matches = list(re.finditer(pattern, prompt, re.IGNORECASE))
            # Only flag if more than 3 occurrences (occasional use is OK)
            if len(matches) > 3:
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.QUALITY,
                        message=f"Quality pattern found {len(matches)} times: matches first pattern",
                        suggestion=suggestion
                    )
                )


class PostStageValidator:
    """
    Stage 3: Post-generation validation.
    
    Validates AFTER image generation:
    - Realism score (via Gemini Vision)
    - Prompt compliance
    - Physics adherence
    - Text/label detection
    """
    
    PASS_THRESHOLD = 75.0
    
    def __init__(self, vision_validator=None):
        """
        Initialize with optional vision validator.
        
        Args:
            vision_validator: MaterialImageValidator instance
        """
        self.vision_validator = vision_validator
    
    def validate(
        self,
        image_path: Path,
        prompt: str,
        research_data: Dict[str, Any],
        material: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> ValidationReport:
        """Run post-generation validation."""
        report = ValidationReport(
            stage=ValidationStage.POST,
            material=material,
            prompt_length=len(prompt)
        )
        
        if not self.vision_validator:
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.CONFIG,
                    message="Vision validator not configured - skipping image analysis",
                    suggestion="Initialize UnifiedValidator with vision_validator for full post-validation"
                )
            )
            return report
        
        try:
            # Run vision validation
            vision_result = self.vision_validator.validate_material_image(
                image_path=image_path,
                material_name=material,
                research_data=research_data,
                config=config,
                original_prompt=prompt
            )
            
            # Extract scores
            report.scores['realism'] = vision_result.realism_score or 0
            report.scores['physics'] = 100 if vision_result.physics_compliant else 50
            report.scores['distribution'] = 100 if vision_result.distribution_realistic else 50
            
            # Check realism threshold
            if vision_result.realism_score and vision_result.realism_score < self.PASS_THRESHOLD:
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.REALISM,
                        message=f"Realism score below threshold: {vision_result.realism_score:.0f}/{self.PASS_THRESHOLD}",
                        suggestion=vision_result.overall_assessment or "Improve image realism"
                    )
                )
            
            # Check text/labels (automatic fail)
            if vision_result.text_labels_present:
                report.add_issue(
                    ValidationIssue(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.COMPLIANCE,
                        message="Text/labels detected in image (automatic fail)",
                        suggestion="Regenerate without text/labels"
                    ),
                    FixAction(
                        action_type='prepend',
                        severity=IssueSeverity.CRITICAL,
                        description="Add stronger anti-text instruction",
                        replacement="ABSOLUTELY NO TEXT, LABELS, OR WATERMARKS. ",
                        ai_instruction="Add 'ABSOLUTELY NO TEXT, LABELS, OR WATERMARKS' at start of prompt"
                    )
                )
            
            # Check physics
            if not vision_result.physics_compliant and vision_result.physics_issues:
                for issue in vision_result.physics_issues[:3]:
                    report.add_issue(
                        ValidationIssue(
                            severity=IssueSeverity.HIGH,
                            category=IssueCategory.PHYSICS,
                            message=f"Physics violation: {issue}",
                            suggestion="Review physics constraints in prompt"
                        )
                    )
            
            # Add recommendations as fixes
            if vision_result.recommendations:
                for rec in vision_result.recommendations[:3]:
                    report.fix_actions.append(
                        FixAction(
                            action_type='append',
                            severity=IssueSeverity.MEDIUM,
                            description=rec,
                            ai_instruction=rec,
                            safe_to_auto_apply=False
                        )
                    )
            
            # Set overall status based on vision result
            if not vision_result.passed:
                report.status = ValidationStatus.FAIL
            
        except Exception as e:
            report.add_issue(
                ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category=IssueCategory.CONFIG,
                    message=f"Vision validation failed: {e}",
                    suggestion="Check API configuration and try again"
                )
            )
        
        return report


# =============================================================================
# UNIFIED VALIDATOR
# =============================================================================

class UnifiedValidator:
    """
    Single entry point for all validation stages.
    
    Usage:
        validator = UnifiedValidator()
        
        # Stage 1: Early validation (before research)
        report = validator.validate_early(material="Aluminum", config={...})
        if report.status == ValidationStatus.FAIL:
            print(report.fix_instructions)
            return
        
        # Stage 2: Prompt validation (before API call)
        report = validator.validate_prompt(prompt, negative_prompt)
        if report.status == ValidationStatus.FAIL:
            prompt = report.apply_auto_fixes(prompt)
        
        # Stage 3: Post validation (after image)
        report = validator.validate_image(image_path, prompt, research_data)
        if report.status == ValidationStatus.FAIL:
            correction = report.get_ai_prompt()
    """
    
    def __init__(
        self,
        prompts_dir: Optional[Path] = None,
        vision_validator=None
    ):
        """
        Initialize unified validator.
        
        Args:
            prompts_dir: Path to shared prompts directory
            vision_validator: MaterialImageValidator for post-stage validation
        """
        self.prompts_dir = prompts_dir
        self.early = EarlyStageValidator(prompts_dir)
        self.prompt = PromptStageValidator()
        self.post = PostStageValidator(vision_validator)
    
    def validate_early(
        self,
        material: str,
        config: Dict[str, Any],
        **kwargs
    ) -> ValidationReport:
        """
        Stage 1: Pre-research validation.
        
        Call BEFORE building prompts to catch config issues early.
        """
        return self.early.validate(material, config, **kwargs)
    
    def validate_prompt(
        self,
        prompt: str,
        negative_prompt: str = "",
        material: str = "",
        **kwargs
    ) -> ValidationReport:
        """
        Stage 2: Pre-generation validation.
        
        Call BEFORE API call to validate and auto-fix prompt.
        """
        return self.prompt.validate(prompt, negative_prompt, material, **kwargs)
    
    def validate_image(
        self,
        image_path: Path,
        prompt: str,
        research_data: Dict[str, Any],
        material: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> ValidationReport:
        """
        Stage 3: Post-generation validation.
        
        Call AFTER image generation to validate output.
        """
        return self.post.validate(image_path, prompt, research_data, material, config)
    
    def full_pipeline(
        self,
        material: str,
        config: Dict[str, Any],
        prompt: str,
        negative_prompt: str,
        image_path: Optional[Path] = None,
        research_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, ValidationReport]:
        """
        Run all applicable validation stages.
        
        Returns dict of stage_name -> ValidationReport.
        """
        results = {}
        
        # Stage 1
        results['early'] = self.validate_early(material, config)
        if results['early'].status == ValidationStatus.CRITICAL:
            return results
        
        # Stage 2
        results['prompt'] = self.validate_prompt(prompt, negative_prompt, material)
        if results['prompt'].status == ValidationStatus.CRITICAL:
            return results
        
        # Stage 3 (if image provided)
        if image_path and research_data:
            results['post'] = self.validate_image(
                image_path, prompt, research_data, material, config
            )
        
        return results


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_validator(
    prompts_dir: Optional[Path] = None,
    vision_validator=None
) -> UnifiedValidator:
    """Factory function to create unified validator."""
    return UnifiedValidator(prompts_dir, vision_validator)


def validate_prompt_quick(prompt: str, material: str = "") -> ValidationReport:
    """Quick prompt validation without full setup."""
    validator = PromptStageValidator()
    return validator.validate(prompt, material=material)


def validate_and_fix(prompt: str, material: str = "") -> str:
    """Validate prompt and apply auto-fixes, return fixed prompt."""
    report = validate_prompt_quick(prompt, material)
    if report.fix_actions:
        return report.apply_auto_fixes(prompt)
    return prompt
