"""
Structural Variation Checker - Detects Formulaic AI Patterns

Analyzes content structure to detect formulaic patterns that indicate AI generation:
- Opening pattern repetition (same "When X, you'll want to..." every time)
- Property dump detection (3+ numeric properties listed in sequence)
- Formula detection (opening → property list → warning → recommendation)
- Structural diversity scoring

Created: November 21, 2025
Purpose: Add structural variation as essential quality parameter alongside Winston/humanness
"""

import re
import sqlite3
import yaml
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class StructuralAnalysis:
    """Result from structural variation analysis"""
    passes: bool
    diversity_score: float  # 0.0-10.0, where 10.0 is maximally diverse
    opening_pattern: str
    is_formulaic: bool
    has_property_dump: bool
    structure_type: str  # "formula", "varied", "unique"
    word_count: int
    word_count_variance: float  # How different from recent average
    linguistic_patterns: List[str]  # Detected linguistic patterns
    author_voice_preserved: bool  # NEW: Whether author signature maintained
    author_id: int  # NEW: Author ID for voice tracking
    issues: List[str]
    suggestions: List[str]


class StructuralVariationChecker:
    """
    Checks content for formulaic structural patterns.
    
    Detects:
    - Repeated opening patterns (monotony across batch)
    - Property dumps (3+ properties with numbers listed in sequence)
    - Formulaic structure (opening → props → warning → recommendation)
    - Lack of structural diversity
    
    Passes if:
    - Opening pattern differs from recent generations
    - Properties integrated into narrative (not dumped)
    - Structure varies from standard formula
    - Diversity score ≥ 6.0/10
    """
    
    def __init__(self, db_path: str = "data/winston_feedback.db", min_diversity_score: float = None):
        """
        Initialize structural variation checker.
        
        Args:
            db_path: Path to database for storing pattern history
            min_diversity_score: Minimum diversity score required (0-10) 
                               If None, will use dynamic threshold from ThresholdManager
        """
        self.db_path = db_path
        self.min_diversity_score = min_diversity_score  # Can be None - will use dynamic
        self._threshold_manager = None  # Lazy-loaded when needed
        
        # Initialize database table for tracking patterns
        self._init_database()
    
    def _get_min_diversity_score(self) -> float:
        """
        Get minimum diversity score (dynamic or static).
        
        Returns:
            Minimum diversity score threshold (0-10 scale)
        """
        # If explicitly set, use that value
        if self.min_diversity_score is not None:
            return self.min_diversity_score
        
        # Otherwise use dynamic threshold from ThresholdManager
        if self._threshold_manager is None:
            from learning.threshold_manager import ThresholdManager
            self._threshold_manager = ThresholdManager(
                db_path=self.db_path.replace('data/winston_feedback.db', 'z-beam.db')
            )
        
        return self._threshold_manager.get_diversity_threshold(use_learned=True)
    
    def _init_database(self):
        """Create structural_patterns table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if table exists and has correct schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='structural_patterns'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Check if author_id column exists (schema migration)
            cursor.execute("PRAGMA table_info(structural_patterns)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'author_id' not in columns:
                # Drop old table and recreate with new schema
                cursor.execute("DROP TABLE structural_patterns")
                table_exists = False
        
        if not table_exists:
            cursor.execute('''
                CREATE TABLE structural_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material_name TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    author_id INTEGER,
                    opening_pattern TEXT,
                    structure_type TEXT,
                    has_property_dump BOOLEAN,
                    word_count INTEGER,
                    word_count_variance REAL,
                    linguistic_patterns TEXT,
                    author_voice_preserved BOOLEAN,
                    diversity_score REAL,
                    passed BOOLEAN
                )
            ''')
        
        conn.commit()
        conn.close()
    
    def check(
        self,
        content: str,
        material_name: str,
        component_type: str,
        author_id: int = None,
        recent_window: int = 10
    ) -> StructuralAnalysis:
        """
        Check content for structural variation while preserving author voice.
        
        Args:
            content: Generated content to analyze
            material_name: Material name
            component_type: Component type (caption, description, etc.)
            author_id: Author ID for voice preservation (optional)
            recent_window: Number of recent generations to compare against
        
        Returns:
            StructuralAnalysis with pass/fail and detailed metrics
        """
        logger.info(f"\n🔍 STRUCTURAL VARIATION CHECK: {component_type}")
        if author_id:
            logger.info(f"   Author: ID {author_id}")
        
        issues = []
        suggestions = []
        
        # Load author voice characteristics if provided
        author_voice_signature = None
        if author_id:
            author_voice_signature = self._load_author_signature(author_id)
        
        issues = []
        suggestions = []
        
        # 1. Extract opening pattern
        opening_pattern = self._extract_opening_pattern(content)
        logger.info(f"   Opening: \"{opening_pattern[:80]}...\"")
        
        # 2. Analyze word count variation
        word_count = len(content.split())
        recent_word_counts = self._get_recent_word_counts(component_type, recent_window)
        word_count_variance = self._calculate_word_count_variance(word_count, recent_word_counts)
        
        logger.info(f"   Word count: {word_count} words (variance: {word_count_variance:.1%})")
        
        # Check word count variance (minimum threshold from config)
        # Load variance threshold from config (default 5% minimum)
        import yaml
        from pathlib import Path
        config_path = Path("generation/config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Minimum variance = 10% of configured variation (e.g., 0.50 → 0.05 minimum)
                configured_variation = config.get('word_count_variation', 0.10)
                min_variance = configured_variation * 0.10  # 10% of configured variation
        else:
            min_variance = 0.05  # Fallback: 5% minimum variance
        
        if word_count_variance < min_variance and len(recent_word_counts) >= 3:
            issues.append(f"Word count too uniform ({word_count} words, {word_count_variance:.1%} variance, need ≥{min_variance:.1%})")
            suggestions.append(f"Vary content length by ±{configured_variation:.0%} to show natural variation")
            logger.info(f"   ⚠️  Word count lacks variation (need ≥{min_variance:.1%})")
        else:
            logger.info("   ✅ Word count shows variation")
        
        # 3. Detect linguistic patterns
        linguistic_patterns = self._detect_linguistic_patterns(content)
        recent_linguistic = self._get_recent_linguistic_patterns(component_type, recent_window)
        linguistic_repetition = sum(1 for pattern in linguistic_patterns if pattern in recent_linguistic)
        
        logger.info(f"   Linguistic patterns: {', '.join(linguistic_patterns[:3])}")
        
        if linguistic_repetition >= 2:
            issues.append(f"Linguistic patterns repeated {linguistic_repetition} times")
            suggestions.append("Use different sentence structures and connectors")
            logger.info(f"   ⚠️  {linguistic_repetition} linguistic patterns repeated")
        else:
            logger.info("   ✅ Linguistic patterns show diversity")
        
        # 3.5. Check author voice preservation (if author provided)
        author_voice_preserved = True
        if author_voice_signature:
            voice_check = self._check_author_voice_preservation(
                content=content,
                linguistic_patterns=linguistic_patterns,
                signature=author_voice_signature
            )
            author_voice_preserved = voice_check['preserved']
            
            if author_voice_preserved:
                logger.info(f"   ✅ Author voice preserved ({voice_check['matches']}/{voice_check['expected']} signature traits)")
            else:
                logger.info(f"   ⚠️  Author voice weakened ({voice_check['matches']}/{voice_check['expected']} signature traits)")
                issues.append(f"Author voice signature not fully preserved")
                suggestions.append(f"Maintain author's characteristic patterns: {', '.join(voice_check['missing'][:3])}")
        
        # 4. Check for property dump
        has_property_dump = self._detect_property_dump(content)
        if has_property_dump:
            issues.append("Property dump detected (3+ properties listed sequentially)")
            suggestions.append("Integrate properties into narrative flow")
            logger.info("   ⚠️  Property dump detected")
        else:
            logger.info("   ✅ Properties integrated naturally")
        
        # 5. Detect formulaic structure
        is_formulaic = self._detect_formula(content)
        structure_type = "formula" if is_formulaic else "varied"
        
        if is_formulaic:
            issues.append("Formulaic structure: opening → property dump → warning → recommendation")
            suggestions.append("Use one of 5 structural approaches from humanness layer")
            logger.info(f"   ⚠️  Formulaic structure detected")
        else:
            logger.info(f"   ✅ Varied structure")
        
        # 6. Compare opening pattern to recent generations
        recent_patterns = self._get_recent_patterns(component_type, recent_window)
        repetition_count = sum(1 for p in recent_patterns if self._patterns_similar(opening_pattern, p))
        
        if repetition_count >= 3:
            issues.append(f"Opening pattern repeated {repetition_count}/{recent_window} recent generations")
            suggestions.append("Use different opening from humanness layer options (7 available)")
            logger.info(f"   ⚠️  Opening pattern repeated {repetition_count} times")
        else:
            logger.info(f"   ✅ Opening pattern unique (matches {repetition_count}/10 recent)")
        
        # 7. Calculate diversity score (0-10)
        diversity_score = self._calculate_diversity_score(
            has_property_dump=has_property_dump,
            is_formulaic=is_formulaic,
            repetition_count=repetition_count,
            recent_window=recent_window,
            word_count_variance=word_count_variance,
            linguistic_repetition=linguistic_repetition
        )
        
        logger.info(f"   📊 Diversity Score: {diversity_score:.1f}/10.0")
        
        # Get dynamic threshold
        min_score_threshold = self._get_min_diversity_score()
        
        # 8. Determine pass/fail
        passes = (
            diversity_score >= min_score_threshold
            and not is_formulaic
            and repetition_count < 3
            and word_count_variance >= min_variance  # Dynamic threshold from config
            and author_voice_preserved  # NEW: Must preserve author voice
        )
        
        if passes:
            logger.info(f"   ✅ PASS (≥{min_score_threshold:.1f}/10)")
        else:
            logger.info(f"   ❌ FAIL (<{min_score_threshold:.1f}/10 or formulaic)")
        
        # 9. Log to database
        self._log_pattern(
            material_name=material_name,
            component_type=component_type,
            author_id=author_id,
            opening_pattern=opening_pattern,
            structure_type=structure_type,
            has_property_dump=has_property_dump,
            word_count=word_count,
            word_count_variance=word_count_variance,
            linguistic_patterns=linguistic_patterns,
            author_voice_preserved=author_voice_preserved,
            diversity_score=diversity_score,
            passed=passes
        )
        
        return StructuralAnalysis(
            passes=passes,
            diversity_score=diversity_score,
            opening_pattern=opening_pattern,
            is_formulaic=is_formulaic,
            has_property_dump=has_property_dump,
            structure_type=structure_type,
            word_count=word_count,
            word_count_variance=word_count_variance,
            linguistic_patterns=linguistic_patterns,
            author_voice_preserved=author_voice_preserved,
            author_id=author_id or 0,
            issues=issues,
            suggestions=suggestions
        )
    
    def _extract_opening_pattern(self, content: str) -> str:
        """Extract first sentence as opening pattern"""
        # Get first sentence (up to period, semicolon, or 150 chars)
        match = re.match(r'^([^.;]+[.;]?)', content)
        if match:
            return match.group(1).strip()[:150]
        return content[:150]
    
    def _detect_property_dump(self, content: str) -> bool:
        """
        Detect if content dumps 3+ properties with numbers in sequence.
        
        Pattern: "X at Y, A at B, C at D" or "X of Y, A of B, C of D"
        """
        # Match patterns like "density at 2.7 g/cm³, reflectivity of 0.95, melting at 933 K"
        pattern = r'(at|of)\s+[\d.]+[^,;.]*[,;]\s*\w+\s+(at|of)\s+[\d.]+[^,;.]*[,;]\s*\w+\s+(at|of)\s+[\d.]+'
        return bool(re.search(pattern, content))
    
    def _detect_formula(self, content: str) -> bool:
        """
        Detect formulaic structure: opening → property dump → warning → recommendation
        """
        has_property_dump = self._detect_property_dump(content)
        has_warning = bool(re.search(r'(but watch|be careful|avoid|watch for|watch the)', content.lower()))
        has_recommendation = bool(re.search(r'(we (recommend|use|typically|found)|use \d|start with)', content.lower()))
        
        # Formulaic if has all three elements
        return has_property_dump and has_warning and has_recommendation
    
    def _get_recent_patterns(self, component_type: str, window: int) -> List[str]:
        """Get opening patterns from N most recent generations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT opening_pattern
            FROM structural_patterns
            WHERE component_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (component_type, window))
        
        patterns = [row[0] for row in cursor.fetchall()]
        conn.close()
        return patterns
    
    def _patterns_similar(self, pattern1: str, pattern2: str) -> bool:
        """Check if two opening patterns are structurally similar"""
        # Normalize: lowercase, remove material names, focus on structure
        p1 = re.sub(r'\b[A-Z][a-z]+\b', 'MATERIAL', pattern1).lower()
        p2 = re.sub(r'\b[A-Z][a-z]+\b', 'MATERIAL', pattern2).lower()
        
        # Similar if first 5 words match
        words1 = p1.split()[:5]
        words2 = p2.split()[:5]
        
        matches = sum(1 for w1, w2 in zip(words1, words2) if w1 == w2)
        return matches >= 4  # At least 4 of first 5 words match
    
    def _load_author_signature(self, author_id: int) -> Dict:
        """
        Load author voice signature characteristics.
        
        Returns dict with expected linguistic patterns for this author:
        - sentence_structure: preferred patterns
        - vocabulary: characteristic word choices
        - connectors: typical linking words
        - formality_level: tone characteristics
        """
        import yaml
        import os
        
        # Map author IDs to persona files
        author_files = {
            2: 'shared/prompts/personas/italy.yaml',
            3: 'shared/prompts/personas/taiwan.yaml',
            4: 'shared/prompts/personas/united_states.yaml'
        }
        
        if author_id not in author_files:
            return None
        
        persona_file = author_files[author_id]
        if not os.path.exists(persona_file):
            return None
        
        with open(persona_file, 'r') as f:
            persona = yaml.safe_load(f)
        
        # Extract signature characteristics
        signature = {
            'author_id': author_id,
            'connectors': persona.get('connectors', []),
            'markers': persona.get('markers', []),
            'formality_level': persona.get('linguistic_characteristics', {}).get('formality_level', ''),
            'vocabulary': persona.get('neutral_technical', []),
            'style_patterns': persona.get('style_patterns', {})
        }
        
        return signature
    
    def _check_author_voice_preservation(
        self,
        content: str,
        linguistic_patterns: List[str],
        signature: Dict
    ) -> Dict:
        """
        Check if content preserves author's voice signature.
        
        Returns:
            Dict with 'preserved' (bool), 'matches' (int), 'expected' (int), 'missing' (list)
        """
        content_lower = content.lower()
        matches = 0
        expected = 0
        missing = []
        
        # Check for author's characteristic connectors
        for connector in signature.get('connectors', []):
            expected += 1
            if connector.lower() in content_lower:
                matches += 1
            else:
                missing.append(f"connector: {connector}")
        
        # Check for author's markers
        for marker in signature.get('markers', []):
            if marker.lower() in content_lower:
                matches += 0.5  # Markers are less critical
        
        # Check for vocabulary match (at least 1 characteristic verb)
        vocab = signature.get('vocabulary', [])
        vocab_matches = sum(1 for word in vocab if word.lower() in content_lower)
        if vocab_matches >= 1:
            matches += 1
        else:
            missing.append(f"vocabulary: none of {', '.join(vocab[:3])}")
        expected += 1
        
        # Voice preserved if ≥60% signature traits present
        preservation_threshold = 0.6
        preserved = (matches / expected) >= preservation_threshold if expected > 0 else True
        
        return {
            'preserved': preserved,
            'matches': int(matches),
            'expected': expected,
            'missing': missing
        }
    
    def _get_recent_word_counts(self, component_type: str, window: int) -> List[int]:
        """Get word counts from N most recent generations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT word_count
            FROM structural_patterns
            WHERE component_type = ? AND word_count IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (component_type, window))
        
        counts = [row[0] for row in cursor.fetchall()]
        conn.close()
        return counts
    
    def _calculate_word_count_variance(self, word_count: int, recent_counts: List[int]) -> float:
        """Calculate how different current word count is from recent average"""
        if not recent_counts:
            return 1.0  # No history = full variation
        
        avg_count = sum(recent_counts) / len(recent_counts)
        if avg_count == 0:
            return 1.0
        
        variance = abs(word_count - avg_count) / avg_count
        return variance
    
    def _detect_linguistic_patterns(self, content: str) -> List[str]:
        """Detect linguistic patterns in content"""
        patterns = []
        content_lower = content.lower()
        
        # Opening patterns
        if content_lower.startswith('when '):
            patterns.append('when_opening')
        if content_lower.startswith('with '):
            patterns.append('with_opening')
        if content_lower.startswith('the key'):
            patterns.append('key_opening')
        if content_lower.startswith('for '):
            patterns.append('for_opening')
        if content_lower.startswith("you'll"):
            patterns.append('youll_opening')
        
        # Connector words
        if 'unlike' in content_lower:
            patterns.append('unlike_connector')
        if 'but watch' in content_lower:
            patterns.append('but_watch_connector')
        if 'we typically' in content_lower or 'we recommend' in content_lower:
            patterns.append('we_connector')
        if 'this makes' in content_lower or 'this clears' in content_lower:
            patterns.append('this_connector')
        
        # Sentence structures
        if re.search(r'you\'ll want to', content_lower):
            patterns.append('youll_want_structure')
        if re.search(r'watch (for|the|out)', content_lower):
            patterns.append('watch_warning')
        if re.search(r'be careful', content_lower):
            patterns.append('careful_warning')
        
        return patterns
    
    def _get_recent_linguistic_patterns(self, component_type: str, window: int) -> List[str]:
        """Get all linguistic patterns from recent generations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT linguistic_patterns
            FROM structural_patterns
            WHERE component_type = ? AND linguistic_patterns IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (component_type, window))
        
        all_patterns = []
        for row in cursor.fetchall():
            # Parse comma-separated patterns
            if row[0]:
                all_patterns.extend(row[0].split(','))
        
        conn.close()
        return all_patterns
    
    def _calculate_diversity_score(
        self,
        has_property_dump: bool,
        is_formulaic: bool,
        repetition_count: int,
        recent_window: int,
        word_count_variance: float,
        linguistic_repetition: int
    ) -> float:
        """
        Calculate diversity score (0-10).
        
        Scoring:
        - Start at 10.0
        - -3.0 for property dump
        - -2.0 for formulaic structure
        - -1.0 per opening repetition (max -3.0)
        - -1.5 if word count variance < 5%
        - -0.5 per linguistic pattern repetition (max -2.0)
        """
        score = 10.0
        
        if has_property_dump:
            score -= 3.0
        
        if is_formulaic:
            score -= 2.0
        
        # Penalty for opening repetition (max -3.0)
        repetition_penalty = min(repetition_count * 1.0, 3.0)
        score -= repetition_penalty
        
        # Penalty for word count uniformity (use dynamic threshold from config)
        # Load minimum variance from config
        config_path = Path("generation/config.yaml")
        min_variance = 0.05  # Default fallback
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    configured_variation = config.get('word_count_variation', 0.10)
                    min_variance = configured_variation * 0.10
            except Exception:
                pass
        
        if word_count_variance < min_variance:
            score -= 1.5
        
        # Penalty for linguistic repetition (max -2.0)
        linguistic_penalty = min(linguistic_repetition * 0.5, 2.0)
        score -= linguistic_penalty
        
        return max(0.0, score)
    
    def _log_pattern(
        self,
        material_name: str,
        component_type: str,
        author_id: int,
        opening_pattern: str,
        structure_type: str,
        has_property_dump: bool,
        word_count: int,
        word_count_variance: float,
        linguistic_patterns: List[str],
        author_voice_preserved: bool,
        diversity_score: float,
        passed: bool
    ):
        """Log structural pattern to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        linguistic_str = ','.join(linguistic_patterns) if linguistic_patterns else None
        
        cursor.execute('''
            INSERT INTO structural_patterns
            (material_name, component_type, author_id, opening_pattern, structure_type, has_property_dump, 
             word_count, word_count_variance, linguistic_patterns, author_voice_preserved, diversity_score, passed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (material_name, component_type, author_id, opening_pattern, structure_type, has_property_dump,
              word_count, word_count_variance, linguistic_str, author_voice_preserved, diversity_score, passed))
        
        conn.commit()
        conn.close()
    
    def get_diversity_stats(self, component_type: str, window: int = 20) -> Dict:
        """Get diversity statistics for recent generations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(diversity_score) as avg_score,
                SUM(CASE WHEN passed THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as pass_rate,
                SUM(CASE WHEN has_property_dump THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as property_dump_rate,
                SUM(CASE WHEN structure_type = 'formula' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as formulaic_rate
            FROM structural_patterns
            WHERE component_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (component_type, window))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] is not None:
            return {
                'avg_diversity_score': row[0],
                'pass_rate': row[1],
                'property_dump_rate': row[2],
                'formulaic_rate': row[3]
            }
        return {
            'avg_diversity_score': 0.0,
            'pass_rate': 0.0,
            'property_dump_rate': 0.0,
            'formulaic_rate': 0.0
        }
