"""
Prompt Coherence Validator - Separation of Concerns & Contradiction Detection

Ensures clear separation of concerns within prompt chain and validates
that the final assembled prompt sent to Grok is free of:
1. Contradictions between prompt sections
2. Confusion from duplicate/conflicting instructions
3. Poor separation of concerns (voice vs content vs requirements)

This validates the ASSEMBLED prompt after all stages complete.

Created: December 11, 2025
Policy Compliance: PROMPT_CHAINING_POLICY.md + Voice Instruction Centralization
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
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
            if line.startswith('VOICE:') or 'VOICE CHARACTERISTICS:' in line_upper:
                sections['voice'] = (i, self._find_section_end(lines, i))
            
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
        # Check for opposing length instructions
        length_patterns = [
            (r'(\d+)\s*words', 'word count'),
            (r'(\d+)\s*sentences', 'sentence count'),
            (r'brief|short|concise', 'brevity'),
            (r'detailed|comprehensive|thorough', 'detail')
        ]
        
        found_lengths = []
        for pattern, label in length_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
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
        
        # Check for tone contradictions
        tone_keywords = {
            'formal': ['formal', 'professional', 'technical', 'objective'],
            'casual': ['casual', 'conversational', 'friendly', 'approachable'],
            'neutral': ['neutral', 'balanced', 'detached']
        }
        
        found_tones = []
        for tone_type, keywords in tone_keywords.items():
            for keyword in keywords:
                if re.search(rf'\b{keyword}\b', prompt, re.IGNORECASE):
                    found_tones.append((tone_type, keyword))
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
