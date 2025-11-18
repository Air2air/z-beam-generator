"""
Subjective Language Validator

Detects and penalizes subjective language patterns that trigger AI detection.
Based on violations identified in November 16, 2025 batch caption test.

ADAPTIVE LEARNING ARCHITECTURE (November 17, 2025):
Thresholds are dynamically learned from composite quality scores in the database.
The system analyzes which violation levels correlate with high-quality content,
then adapts thresholds to match actual success patterns.

Static config thresholds (config.yaml) are ONLY fallback defaults when insufficient
data exists. System learns optimal thresholds as generations accumulate.

Integration: Should be called during content validation in DynamicGenerator
before accepting generated content as successful.
"""

import re
import logging
import sqlite3
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SubjectiveValidator:
    """
    Validates content against subjective language patterns with adaptive thresholds.
    
    Checks for:
    - Hedging words (around, about, roughly)
    - Dramatic verbs (smother, blasts, clears)
    - Conversational fillers (now, but, such, just)
    - Emotional adjectives (perfect, flawless, excellent)
    - Intensity adverbs (badly, extremely, highly)
    
    ADAPTIVE THRESHOLDS:
    Learns from database which violation counts produce high composite quality scores.
    Thresholds adjust automatically based on empirical success patterns.
    """
    
    def __init__(
        self, 
        config_path: str = "processing/config.yaml",
        db_path: str = "data/winston_feedback.db",
        min_samples_for_learning: int = 20
    ):
        """
        Initialize validator with adaptive learning capabilities.
        
        Args:
            config_path: Path to config.yaml containing fallback thresholds
            db_path: Path to learning database for threshold adaptation
            min_samples_for_learning: Minimum samples before using learned thresholds
        """
        self.config_path = Path(config_path)
        self.db_path = Path(db_path)
        self.min_samples = min_samples_for_learning
        self.violations_patterns = self._load_violation_patterns()
        
        # Load thresholds (learned or fallback to config)
        self.thresholds = self._load_adaptive_thresholds()
        
        logger.info(
            f"SubjectiveValidator initialized with {self._count_patterns()} violation patterns, "
            f"thresholds: violations≤{self.thresholds['max_violations']}, "
            f"commas≤{self.thresholds['max_commas']}, "
            f"source: {self.thresholds.get('source', 'unknown')}"
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
    
    def _load_adaptive_thresholds(self) -> Dict[str, Any]:
        """
        Load thresholds adaptively from learning database.
        
        Strategy:
        1. Query successful generations (high composite quality scores)
        2. Analyze violation patterns in successful content
        3. Set thresholds at 75th percentile of successful content
        4. Fallback to config defaults if insufficient data
        
        Returns:
            Dict with max_violations, max_commas, source
        """
        if not self.db_path.exists():
            logger.info("Database not found, using config defaults")
            return self._load_config_thresholds()
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get successful generations with high composite quality scores
            # Use composite score if available, fallback to human_score
            cursor.execute("""
                SELECT 
                    generated_text,
                    COALESCE(composite_quality_score, human_score) as quality_score
                FROM detection_results
                WHERE success = 1
                  AND COALESCE(composite_quality_score, human_score) >= 70.0
                ORDER BY quality_score DESC
                LIMIT 100
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < self.min_samples:
                logger.info(
                    f"Insufficient samples for learning ({len(rows)}/{self.min_samples}), "
                    f"using config defaults"
                )
                return self._load_config_thresholds()
            
            # Analyze violations in successful content
            violation_counts = []
            comma_counts = []
            
            for text, score in rows:
                # Count violations in this successful content
                words = re.findall(r'\b\w+\b', text.lower())
                violations = 0
                
                for category, patterns in self.violations_patterns.items():
                    for pattern in patterns:
                        violations += words.count(pattern)
                
                violation_counts.append(violations)
                comma_counts.append(text.count(','))
            
            # Set thresholds at 75th percentile of successful content
            # This means "allow violation levels that 75% of successes had"
            violation_counts.sort()
            comma_counts.sort()
            
            percentile_75 = int(len(violation_counts) * 0.75)
            learned_max_violations = violation_counts[percentile_75]
            learned_max_commas = comma_counts[percentile_75]
            
            logger.info(
                f"📚 Learned thresholds from {len(rows)} successful generations: "
                f"violations≤{learned_max_violations}, commas≤{learned_max_commas}"
            )
            
            return {
                'max_violations': learned_max_violations,
                'max_commas': learned_max_commas,
                'source': f'learned from {len(rows)} samples',
                'percentile': 75
            }
            
        except Exception as e:
            logger.warning(f"Failed to learn thresholds: {e}, using config defaults")
            return self._load_config_thresholds()
    
    def _load_config_thresholds(self) -> Dict[str, Any]:
        """Load fallback thresholds from config.yaml"""
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
                'max_commas': thresholds.get('max_commas', 8),
                'source': 'config.yaml (fallback)'
            }
        except Exception as e:
            logger.warning(f"Failed to load thresholds from config: {e}, using defaults")
            return self._get_default_thresholds()
    
    def _load_thresholds(self) -> Dict[str, int]:
        """Deprecated: Use _load_adaptive_thresholds instead"""
        return self._load_adaptive_thresholds()
    
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
        
        Uses ADAPTIVE thresholds learned from successful generations in database.
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
        
        # Use ADAPTIVE thresholds from learning
        adaptive_thresholds = {
            'max_violations': self.thresholds['max_violations'],
            'max_commas': self.thresholds['max_commas'],
            'mode': 'adaptive (learned from successful content)',
            'source': self.thresholds.get('source', 'unknown')
        }
        
        # Validation passes if violations are below learned threshold
        is_valid = (
            total_violations <= adaptive_thresholds['max_violations'] and 
            comma_count <= adaptive_thresholds['max_commas']
        )
        
        # Add threshold info to details (Winston score logged for reference only)
        details['applied_thresholds'] = adaptive_thresholds
        details['winston_score'] = winston_score  # Logged but not used
        
        if not is_valid:
            logger.warning(
                f"Content failed subjective validation: {total_violations} violations "
                f"(max: {adaptive_thresholds['max_violations']}), {comma_count} commas "
                f"(max: {adaptive_thresholds['max_commas']}) "
                f"[Winston: {winston_score if winston_score else 'N/A'}% - reference only] "
                f"[Thresholds: {adaptive_thresholds['source']}]"
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
