"""
Subjective Language Validator

Detects and penalizes subjective language patterns that trigger AI detection.
Based on violations identified in November 16, 2025 batch caption test.

Uses dynamic thresholds based on Winston AI scores - if content scores well
on Winston, allow more stylistic violations. Implements weighted validation
per system architecture requirements.

Integration: Should be called during content validation in DynamicGenerator
before accepting generated content as successful.
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SubjectiveValidator:
    """
    Validates content against subjective language patterns.
    
    Checks for:
    - Hedging words (around, about, roughly)
    - Dramatic verbs (smother, blasts, clears)
    - Conversational fillers (now, but, such, just)
    - Emotional adjectives (perfect, flawless, excellent)
    - Intensity adverbs (badly, extremely, highly)
    """
    
    def __init__(self, config_path: str = "processing/config.yaml"):
        """
        Initialize validator with violation patterns from config.
        
        Args:
            config_path: Path to config.yaml containing subjective_violations
        """
        self.config_path = Path(config_path)
        self.violations_patterns = self._load_violation_patterns()
        self.thresholds = self._load_thresholds()
        
        logger.info(
            f"SubjectiveValidator initialized with {self._count_patterns()} violation patterns, "
            f"thresholds: violations≤{self.thresholds['max_violations']}, commas≤{self.thresholds['max_commas']}"
        )
    
    def _load_violation_patterns(self) -> Dict[str, List[str]]:
        """Load violation patterns from config.yaml"""
        try:
            import yaml
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            
            violations = config.get('subjective_violations', {})
            if not violations:
                logger.warning("No subjective_violations found in config.yaml")
                return self._get_default_patterns()
            
            return violations
        except Exception as e:
            logger.warning(f"Failed to load violations from config: {e}, using defaults")
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> Dict[str, List[str]]:
        """Default violation patterns if config unavailable"""
        return {
            'hedging': ['about', 'around', 'roughly', 'approximately', 'nearly', 'almost'],
            'dramatic_verbs': ['smother', 'blasts', 'clears', 'stands', 'waits', 'demands', 'risks', 'zaps', 'gleams'],
            'conversational': ['now', 'but', 'such', 'really', 'just', 'quite', 'very', 'yeah'],
            'emotional_adjectives': ['perfect', 'flawless', 'excellent', 'ideal', 'superior', 'outstanding', 'impressive'],
            'intensity_adverbs': ['badly', 'extremely', 'highly', 'significantly', 'remarkably', 'notably', 'particularly', 'especially']
        }
    
    def _load_thresholds(self) -> Dict[str, int]:
        """Load validation thresholds from config.yaml"""
        try:
            import yaml
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            
            thresholds = config.get('subjective_thresholds', {})
            if not thresholds:
                logger.warning("No subjective_thresholds found in config.yaml, using defaults")
                return self._get_default_thresholds()
            
            return {
                'max_violations': thresholds.get('max_violations', 6),
                'max_commas': thresholds.get('max_commas', 8)
            }
        except Exception as e:
            logger.warning(f"Failed to load thresholds from config: {e}, using defaults")
            return self._get_default_thresholds()
    
    def _get_default_thresholds(self) -> Dict[str, int]:
        """Default thresholds if config unavailable"""
        return {
            'max_violations': 6,
            'max_commas': 8
        }
    
    def _count_patterns(self) -> int:
        """Count total violation patterns loaded"""
        return sum(len(patterns) for patterns in self.violations_patterns.values())
    
    def validate(self, content: str, winston_score: Optional[float] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate content for subjective language violations.
        
        Uses FIXED thresholds defined in config - operates independently of Winston.
        Winston score is logged for reference but does not affect validation.
        
        Args:
            content: Text content to validate
            winston_score: Optional Winston human score (0-100) - logged only, not used for validation
        
        Returns:
            Tuple of (is_valid, details_dict)
            - is_valid: True if no critical violations detected
            - details_dict: Violation counts, categories, specific words found
        """
        # Extract words from content
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Track violations by category
        violations_found = {category: [] for category in self.violations_patterns.keys()}
        total_violations = 0
        
        # Check each category
        for category, patterns in self.violations_patterns.items():
            for pattern in patterns:
                if pattern in words:
                    count = words.count(pattern)
                    violations_found[category].append({
                        'word': pattern,
                        'count': count
                    })
                    total_violations += count
        
        # Check for AI-flagged patterns
        comma_count = content.count(',')
        em_dash_count = content.count('—')
        
        # Build details
        details = {
            'total_violations': total_violations,
            'violations_by_category': violations_found,
            'comma_count': comma_count,
            'em_dash_count': em_dash_count,
            'has_violations': total_violations > 0,
            'severity': self._calculate_severity(total_violations, comma_count)
        }
        
        # Use FIXED thresholds from config - no dynamic adjustment
        fixed_thresholds = {
            'max_violations': self.thresholds['max_violations'],
            'max_commas': self.thresholds['max_commas'],
            'mode': 'fixed (independent of Winston)'
        }
        
        # Validation passes if violations are below fixed threshold
        is_valid = (
            total_violations <= fixed_thresholds['max_violations'] and 
            comma_count <= fixed_thresholds['max_commas']
        )
        
        # Add threshold info to details (Winston score logged for reference only)
        details['applied_thresholds'] = fixed_thresholds
        details['winston_score'] = winston_score  # Logged but not used
        
        if not is_valid:
            logger.warning(
                f"Content failed subjective validation: {total_violations} violations "
                f"(max: {fixed_thresholds['max_violations']}), {comma_count} commas "
                f"(max: {fixed_thresholds['max_commas']}) "
                f"[Winston: {winston_score if winston_score else 'N/A'}% - reference only]"
            )
        
        return is_valid, details
    
    def _calculate_severity(self, violation_count: int, comma_count: int) -> str:
        """Calculate severity level based on violations"""
        if violation_count == 0 and comma_count <= 3:
            return 'none'
        elif violation_count <= 2 and comma_count <= 4:
            return 'low'
        elif violation_count <= 5 and comma_count <= 6:
            return 'moderate'
        else:
            return 'high'
    
    def get_violation_summary(self, details: Dict) -> str:
        """Generate human-readable summary of violations"""
        if not details['has_violations']:
            return "✅ No subjective language violations detected"
        
        lines = [f"⚠️  {details['total_violations']} subjective language violations detected:"]
        
        for category, violations in details['violations_by_category'].items():
            if violations:
                words = [f"{v['word']} ({v['count']}x)" for v in violations]
                lines.append(f"  - {category}: {', '.join(words)}")
        
        if details['comma_count'] > 4:
            lines.append(f"  - Excessive commas: {details['comma_count']} (AI pattern)")
        
        lines.append(f"  - Severity: {details['severity'].upper()}")
        
        return "\n".join(lines)
