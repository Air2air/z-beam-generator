"""
Pattern Learner - Dynamic Learning from Winston Feedback

Learns which phrases, patterns, and structures consistently fail Winston detection.
Uses statistical analysis to identify problematic content patterns and build
an evolving blacklist of AI-tells.

Key Features:
- Automatic pattern extraction from failed content
- Frequency-based scoring (patterns that fail more often = higher risk)
- Context-aware pattern matching
- Dynamic updates as more data accumulates
- Integration with anti-AI rules

Fail-fast design: Requires database connection, no fallbacks.
"""

import logging
import re
import sqlite3
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


class PatternLearner:
    """
    Learn problematic patterns from Winston feedback database.
    
    Analyzes:
    - N-grams (2-5 word phrases) that appear in failed content
    - Sentence structures that consistently fail
    - Word patterns associated with low human scores
    - Material-specific patterns (e.g., "Aluminum" always fails with X phrase)
    
    Provides:
    - Ranked list of risky patterns
    - Pattern confidence scores (based on frequency)
    - Recommendations for prompt updates
    - Dynamic blacklist for real-time filtering
    """
    
    def __init__(self, db_path: str, min_occurrences: int = 3, min_fail_rate: float = 0.7):
        """
        Initialize pattern learner.
        
        Args:
            db_path: Path to Winston feedback database
            min_occurrences: Minimum times pattern must appear to be learned
            min_fail_rate: Minimum failure rate (0.0-1.0) to consider pattern risky
        """
        self.db_path = Path(db_path)
        self.min_occurrences = min_occurrences
        self.min_fail_rate = min_fail_rate
        
        if not self.db_path.exists():
            logger.warning(f"Database not found: {db_path}. PatternLearner will work once data exists.")
        
        logger.info(f"[PATTERN LEARNER] Initialized (min_occurrences={min_occurrences}, min_fail_rate={min_fail_rate})")
    
    def learn_patterns(self, material: Optional[str] = None, component_type: Optional[str] = None) -> Dict:
        """
        Learn problematic patterns from database.
        
        Args:
            material: Optional filter by material name
            component_type: Optional filter by component type
            
        Returns:
            Dict containing:
            - risky_patterns: List of (pattern, fail_rate, occurrences)
            - safe_patterns: List of (pattern, success_rate, occurrences)
            - recommendations: List of actionable recommendations
            - stats: Overall statistics
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Build query with filters
        query = """
            SELECT 
                dr.generated_text,
                dr.success,
                dr.human_score,
                dr.material,
                dr.component_type
            FROM detection_results dr
            WHERE dr.success IS NOT NULL
        """
        params = []
        
        if material:
            query += " AND dr.material = ?"
            params.append(material)
        
        if component_type:
            query += " AND dr.component_type = ?"
            params.append(component_type)
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            logger.warning("[PATTERN LEARNER] No data available for learning")
            return {
                'risky_patterns': [],
                'safe_patterns': [],
                'recommendations': ['Generate more content to build learning dataset'],
                'stats': {'total_samples': 0}
            }
        
        logger.info(f"[PATTERN LEARNER] Analyzing {len(rows)} samples...")
        
        # Extract patterns from failed vs successful content
        failed_patterns = Counter()
        success_patterns = Counter()
        pattern_stats = defaultdict(lambda: {'failed': 0, 'success': 0, 'scores': []})
        
        for row in rows:
            text = row['generated_text']
            success = bool(row['success'])
            score = row['human_score']
            
            # Extract n-grams (2-5 words)
            patterns = self._extract_patterns(text)
            
            for pattern in patterns:
                pattern_stats[pattern]['scores'].append(score)
                if success:
                    success_patterns[pattern] += 1
                    pattern_stats[pattern]['success'] += 1
                else:
                    failed_patterns[pattern] += 1
                    pattern_stats[pattern]['failed'] += 1
        
        # Calculate risk scores
        risky_patterns = []
        safe_patterns = []
        
        for pattern, stats in pattern_stats.items():
            total = stats['failed'] + stats['success']
            
            if total < self.min_occurrences:
                continue
            
            fail_rate = stats['failed'] / total
            avg_score = sum(stats['scores']) / len(stats['scores'])
            
            if fail_rate >= self.min_fail_rate:
                risky_patterns.append({
                    'pattern': pattern,
                    'fail_rate': fail_rate,
                    'occurrences': total,
                    'avg_score': avg_score,
                    'risk_level': 'high' if fail_rate > 0.9 else 'medium'
                })
            elif fail_rate <= 0.3:  # Good patterns
                safe_patterns.append({
                    'pattern': pattern,
                    'success_rate': 1 - fail_rate,
                    'occurrences': total,
                    'avg_score': avg_score
                })
        
        # Sort by risk/success
        risky_patterns.sort(key=lambda x: (x['fail_rate'], x['occurrences']), reverse=True)
        safe_patterns.sort(key=lambda x: (x['success_rate'], x['occurrences']), reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risky_patterns, safe_patterns)
        
        stats = {
            'total_samples': len(rows),
            'failed_samples': sum(1 for r in rows if not r['success']),
            'success_samples': sum(1 for r in rows if r['success']),
            'unique_patterns': len(pattern_stats),
            'risky_patterns_found': len(risky_patterns),
            'safe_patterns_found': len(safe_patterns)
        }
        
        logger.info(f"✅ [PATTERN LEARNER] Learned {len(risky_patterns)} risky patterns, {len(safe_patterns)} safe patterns")
        
        return {
            'risky_patterns': risky_patterns[:20],  # Top 20 risky
            'safe_patterns': safe_patterns[:20],    # Top 20 safe
            'recommendations': recommendations,
            'stats': stats
        }
    
    def _extract_patterns(self, text: str) -> List[str]:
        """
        Extract n-gram patterns from text.
        
        Args:
            text: Input text
            
        Returns:
            List of pattern strings
        """
        # Normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        words = text.split()
        
        patterns = []
        
        # Extract 2-grams, 3-grams, 4-grams
        for n in [2, 3, 4]:
            for i in range(len(words) - n + 1):
                pattern = ' '.join(words[i:i+n])
                patterns.append(pattern)
        
        return patterns
    
    def _generate_recommendations(self, risky: List[Dict], safe: List[Dict]) -> List[str]:
        """
        Generate actionable recommendations based on learned patterns.
        
        Args:
            risky: List of risky patterns
            safe: List of safe patterns
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not risky:
            recommendations.append("✅ No high-risk patterns detected. Content quality is good!")
            return recommendations
        
        # High-risk patterns (>90% fail rate)
        high_risk = [p for p in risky if p['fail_rate'] > 0.9]
        if high_risk:
            recommendations.append(f"🚨 {len(high_risk)} patterns fail >90% of the time - add to anti-AI rules immediately:")
            for p in high_risk[:5]:
                recommendations.append(f"   • Avoid: \"{p['pattern']}\" (fails {p['fail_rate']:.0%}, seen {p['occurrences']}x)")
        
        # Medium-risk patterns (70-90%)
        medium_risk = [p for p in risky if 0.7 <= p['fail_rate'] <= 0.9]
        if medium_risk:
            recommendations.append(f"⚠️  {len(medium_risk)} patterns fail 70-90% - consider adding to prompts:")
            for p in medium_risk[:5]:
                recommendations.append(f"   • Reduce: \"{p['pattern']}\" (fails {p['fail_rate']:.0%}, seen {p['occurrences']}x)")
        
        # Encourage safe patterns
        if safe:
            recommendations.append(f"✅ {len(safe)} patterns consistently succeed - reinforce in prompts:")
            for p in safe[:3]:
                recommendations.append(f"   • Use more: \"{p['pattern']}\" (succeeds {p['success_rate']:.0%}, seen {p['occurrences']}x)")
        
        return recommendations
    
    def get_dynamic_blacklist(self, threshold: float = 0.8) -> List[str]:
        """
        Get current blacklist of patterns based on failure rate threshold.
        
        Args:
            threshold: Minimum failure rate to include in blacklist
            
        Returns:
            List of pattern strings to avoid
        """
        result = self.learn_patterns()
        blacklist = [
            p['pattern'] 
            for p in result['risky_patterns'] 
            if p['fail_rate'] >= threshold
        ]
        
        logger.info(f"[PATTERN LEARNER] Generated blacklist with {len(blacklist)} patterns (threshold={threshold})")
        return blacklist
    
    def check_text_for_patterns(self, text: str, threshold: float = 0.8) -> Dict:
        """
        Check if text contains risky patterns.
        
        Args:
            text: Text to check
            threshold: Risk threshold (0.0-1.0)
            
        Returns:
            Dict with:
            - has_risky_patterns: bool
            - detected_patterns: List of detected risky patterns
            - risk_score: Overall risk score (0.0-1.0)
            - recommendations: Specific fixes
        """
        blacklist_patterns = self.get_dynamic_blacklist(threshold)
        
        if not blacklist_patterns:
            return {
                'has_risky_patterns': False,
                'detected_patterns': [],
                'risk_score': 0.0,
                'recommendations': []
            }
        
        # Check text for patterns
        text_lower = text.lower()
        detected = []
        
        for pattern in blacklist_patterns:
            if pattern in text_lower:
                detected.append(pattern)
        
        risk_score = len(detected) / len(blacklist_patterns) if blacklist_patterns else 0.0
        
        recommendations = []
        if detected:
            recommendations.append(f"❌ Found {len(detected)} high-risk patterns:")
            for pattern in detected[:5]:
                recommendations.append(f"   • Remove: \"{pattern}\"")
        
        return {
            'has_risky_patterns': len(detected) > 0,
            'detected_patterns': detected,
            'risk_score': risk_score,
            'recommendations': recommendations
        }
