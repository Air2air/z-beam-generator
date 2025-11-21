"""
Forbidden Phrase Validator - Enforces humanness layer patterns

Pre-flight validation that catches AI patterns BEFORE Winston detection.
Faster and cheaper than relying on Winston API to detect violations.

LEARNING MODE: Continuously updates forbidden phrases from Winston failures in database.

Created: November 20, 2025
"""

import re
import logging
import sqlite3
from typing import List, Tuple, Set
from pathlib import Path
import yaml
from collections import Counter

logger = logging.getLogger(__name__)


class ForbiddenPhraseValidator:
    """
    Validates content against learned theatrical phrases and AI patterns.
    
    Catches violations BEFORE Winston API call for faster iteration.
    Learns new forbidden phrases from Winston failures in database.
    """
    
    def __init__(self, patterns_file: Path = None, winston_db: str = 'z-beam.db', learn_from_db: bool = True):
        """
        Initialize validator with learned patterns.
        
        Args:
            patterns_file: Path to learned_patterns.yaml
            winston_db: Path to Winston feedback database
            learn_from_db: If True, extract phrases from Winston failures
        """
        if patterns_file is None:
            patterns_file = Path('prompts/evaluation/learned_patterns.yaml')
        
        self.patterns_file = patterns_file
        self.winston_db = winston_db
        self.learn_from_db = learn_from_db
        
        self._load_patterns()
        
        if self.learn_from_db:
            self._learn_from_winston_failures()
    
    def _load_patterns(self):
        """Load forbidden patterns from YAML"""
        try:
            with open(self.patterns_file, 'r') as f:
                data = yaml.safe_load(f)
            
            theatrical = data.get('theatrical_phrases', {})
            self.high_penalty_phrases = theatrical.get('high_penalty', [])
            self.medium_penalty_phrases = theatrical.get('medium_penalty', [])
            
            # Combine all forbidden phrases
            self.forbidden_phrases = set(self.high_penalty_phrases + self.medium_penalty_phrases)
            
            logger.info(f"📋 Loaded {len(self.forbidden_phrases)} forbidden phrases from YAML")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not load patterns: {e}")
            self.forbidden_phrases = set()
    
    def _learn_from_winston_failures(self):
        """
        Extract common phrases from Winston failures in database.
        
        Analyzes failed content to identify patterns that consistently trigger AI detection.
        """
        try:
            conn = sqlite3.connect(self.winston_db)
            cursor = conn.cursor()
            
            # Get recent Winston failures (AI score > threshold)
            # Focus on descriptions that scored high AI (>80%)
            query = """
                SELECT generated_text, ai_score
                FROM detection_results
                WHERE component_type = 'description'
                  AND ai_score > 0.80
                  AND generated_text IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 50
            """
            
            cursor.execute(query)
            failures = cursor.fetchall()
            conn.close()
            
            if not failures:
                logger.info("   No Winston failures found in database")
                return
            
            # Extract common n-grams from failures
            learned_phrases = self._extract_common_phrases([text for text, _ in failures])
            
            # Add new phrases to forbidden set
            new_phrases = learned_phrases - self.forbidden_phrases
            
            if new_phrases:
                self.forbidden_phrases.update(new_phrases)
                logger.info(f"🧠 Learned {len(new_phrases)} new forbidden phrases from {len(failures)} Winston failures:")
                for phrase in list(new_phrases)[:10]:  # Show first 10
                    logger.info(f"   + \"{phrase}\"")
            else:
                logger.info("   ✅ All common phrases from Winston failures already in avoidance list")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not learn from Winston DB: {e}")
    
    def _extract_common_phrases(self, texts: List[str], min_frequency: int = 3) -> Set[str]:
        """
        Extract common 2-4 word phrases that appear frequently in failed content.
        
        Args:
            texts: List of failed content
            min_frequency: Minimum times phrase must appear to be considered
        
        Returns:
            Set of common phrases
        """
        # Common AI patterns to look for (2-4 word phrases)
        phrase_patterns = [
            r'\b\w+\s+\w+\s+challenge\b',  # "unique cleaning challenge"
            r'\bprimary\s+\w+\b',  # "primary concern"
            r'\b(remarkably|exceptionally|particularly|notably)\s+\w+\b',  # "remarkably low"
            r'\bpresents?\s+a\s+\w+\b',  # "presents a challenge"
            r'\b\w+ly\s+low\b',  # "exceptionally low"
            r'\b\w+ly\s+high\b',  # "remarkably high"
            r'\bkey\s+\w+\b',  # "key challenge"
            r'\bsignificant\s+\w+\b',  # "significant challenge"
        ]
        
        phrase_counter = Counter()
        
        for text in texts:
            text_lower = text.lower()
            for pattern in phrase_patterns:
                matches = re.findall(pattern, text_lower)
                phrase_counter.update(matches)
        
        # Return phrases that appear at least min_frequency times
        common_phrases = {phrase for phrase, count in phrase_counter.items() if count >= min_frequency}
        
        return common_phrases
    
    def validate(self, content: str) -> Tuple[bool, List[str]]:
        """
        Check content for forbidden phrases.
        
        Args:
            content: Text to validate
        
        Returns:
            Tuple of (is_valid, violations_found)
            - is_valid: True if no violations, False if violations found
            - violations_found: List of forbidden phrases detected
        """
        if not self.forbidden_phrases:
            return True, []
        
        violations = []
        content_lower = content.lower()
        
        for phrase in self.forbidden_phrases:
            # Case-insensitive whole-word match
            pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
            if re.search(pattern, content_lower):
                violations.append(phrase)
        
        is_valid = len(violations) == 0
        
        if not is_valid:
            logger.warning(f"⚠️  Found {len(violations)} forbidden phrases in content")
            for phrase in violations:
                logger.warning(f"   ❌ '{phrase}'")
        
        return is_valid, violations
    
    def get_violation_message(self, violations: List[str]) -> str:
        """Format violation message for logging"""
        return f"Content contains forbidden phrases: {', '.join(f'"{v}"' for v in violations)}"
