"""
Enhanced AI Detection - Strict AI Detection Avoidance System

TOP PRIORITY: AI detection avoidance is the primary quality gate.

Architecture:
    Multiple detection layers with ZERO TOLERANCE for AI patterns
    
Detection Layers (in priority order):
    1. Winston API Score (external validation)
    2. Telltale AI Phrases (instant fail)
    3. Structural Patterns (AI writing signatures)
    4. Statistical Markers (unnatural distributions)
    5. Linguistic Authenticity (human irregularity)

Grade F Violations (Instant Rejection):
    - Winston score < 69% human
    - ANY telltale AI phrase detected
    - >2 hedging words per 100 words
    - >3 transitions per 100 words
    - Sentence length CV < 0.30 (too uniform)
    - No sentence fragments (too formal)

"""

from typing import Dict, Any, List, Tuple
import re
import statistics
import logging

logger = logging.getLogger(__name__)


class EnhancedAIDetector:
    """
    Strict AI detection system prioritizing human authenticity.
    
    Philosophy: 
    - Fail-fast on ANY AI indicator
    - Better to regenerate than risk AI detection
    - Human writing is naturally imperfect
    """
    
    # COMPREHENSIVE AI TELLTALE PHRASES (instant rejection)
    AI_TELLTALE_PHRASES = [
        # Classic AI phrases
        'delve into', 'delves into', 'delving into',
        'navigate', 'navigating', 'navigates',
        'it is important to note', 'it is worth noting',
        'it\'s important to note', 'it\'s worth noting',
        'moreover', 'furthermore', 'in addition',
        'consequently', 'subsequently', 'nevertheless',
        'in conclusion', 'to conclude', 'in summary',
        
        # Challenge/solution patterns
        'presents a challenge', 'presents challenges',
        'presents a unique challenge', 'poses a challenge',
        'presents an opportunity', 'poses an opportunity',
        
        # Importance emphasis
        'crucial aspect', 'critical aspect', 'vital aspect',
        'essential aspect', 'key aspect', 'important aspect',
        'it is crucial', 'it is critical', 'it is vital',
        'it is essential', 'it\'s crucial', 'it\'s critical',
        
        # Professional hedging
        'carefully consider', 'careful consideration',
        'it is recommended', 'it is advisable',
        'it\'s recommended', 'it\'s advisable',
        'one should', 'one must', 'one can',
        
        # Range/spectrum language
        'wide range', 'broad range', 'wide variety',
        'broad spectrum', 'wide spectrum',
        
        # Embark/journey metaphors
        'embark on', 'embarking on', 'embarks on',
        'journey into', 'journey through',
        
        # Realm/domain language
        'in the realm of', 'within the realm',
        'in the domain of', 'within the domain',
        'in the field of', 'within the field',
        
        # Landscape/tapestry metaphors
        'landscape of', 'tapestry of', 'fabric of',
        
        # Meticulously/robust patterns
        'meticulously', 'meticulously crafted',
        'robust', 'robust solution', 'robust approach',
        
        # Seamlessly/effortlessly
        'seamlessly', 'seamlessly integrates',
        'effortlessly', 'effortlessly handles',
        
        # Cutting-edge/state-of-the-art
        'cutting-edge', 'cutting edge',
        'state-of-the-art', 'state of the art',
        
        # Paramount/pivotal
        'paramount', 'is paramount', 'remains paramount',
        'pivotal', 'is pivotal', 'plays a pivotal role',
        
        # Underscore/underscores
        'underscores the importance', 'underscores the need',
        'this underscores', 'which underscores',
    ]
    
    # HEDGING WORDS (limit: 2 per 100 words)
    HEDGING_WORDS = [
        'somewhat', 'quite', 'rather', 'fairly',
        'relatively', 'comparatively', 'arguably',
        'potentially', 'possibly', 'probably',
        'generally', 'typically', 'usually',
        'tends to', 'appears to', 'seems to',
    ]
    
    # FORMAL TRANSITIONS (limit: 3 per 100 words)
    FORMAL_TRANSITIONS = [
        'however', 'therefore', 'thus', 'hence',
        'moreover', 'furthermore', 'additionally',
        'consequently', 'subsequently', 'nevertheless',
        'nonetheless', 'accordingly', 'thereby',
    ]
    
    # PASSIVE VOICE MARKERS (limit: 20% of sentences)
    PASSIVE_MARKERS = [
        'is used', 'are used', 'was used', 'were used',
        'is made', 'are made', 'was made', 'were made',
        'is known', 'are known', 'was known', 'were known',
        'is considered', 'are considered',
        'is found', 'are found', 'was found', 'were found',
        'is required', 'are required',
        'is employed', 'are employed',
    ]
    
    def __init__(self, winston_client=None, strict_mode: bool = True):
        """
        Initialize enhanced AI detector.
        
        Args:
            winston_client: Winston API client for external validation
            strict_mode: If True, use strictest thresholds (recommended: True)
        """
        self.winston = winston_client
        self.strict_mode = strict_mode
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance"""
        self.telltale_pattern = re.compile(
            '|'.join(re.escape(phrase) for phrase in self.AI_TELLTALE_PHRASES),
            re.IGNORECASE
        )
        self.hedging_pattern = re.compile(
            '|'.join(re.escape(word) for word in self.HEDGING_WORDS),
            re.IGNORECASE
        )
        self.transition_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(word) for word in self.FORMAL_TRANSITIONS) + r')\b',
            re.IGNORECASE
        )
        self.passive_pattern = re.compile(
            '|'.join(re.escape(marker) for marker in self.PASSIVE_MARKERS),
            re.IGNORECASE
        )
    
    def analyze(self, text: str, component_type: str = None) -> Dict[str, Any]:
        """
        Comprehensive AI detection analysis.
        
        Returns:
            {
                'is_ai': bool,  # True if AI detected (REJECT content)
                'confidence': float,  # 0-1, how certain we are
                'winston_score': float,  # 0-100, % human
                'violations': List[str],  # Specific issues found
                'scores': Dict[str, float],  # Individual dimension scores
                'recommendation': str  # 'PASS' or 'REJECT: reason'
            }
        """
        violations = []
        scores = {}
        
        # === LAYER 1: Winston API (if available) ===
        winston_score = None
        if self.winston:
            try:
                winston_result = self.winston.check_text(text)
                winston_score = winston_result.get('human_score', 0)  # Already 0-100 range
                scores['winston'] = winston_score
                
                # STRICT THRESHOLD: 69% minimum (per copilot-instructions.md)
                if winston_score < 69.0:
                    violations.append(
                        f"Winston score {winston_score:.1f}% < 69% threshold"
                    )
            except Exception as e:
                logger.warning(f"Winston API failed: {e}")
        
        # === LAYER 2: Telltale Phrases (ZERO TOLERANCE) ===
        telltale_matches = self.telltale_pattern.findall(text.lower())
        if telltale_matches:
            violations.append(
                f"AI telltale phrases detected: {', '.join(set(telltale_matches[:3]))}"
            )
            scores['telltale_phrases'] = 0  # Instant fail
        else:
            scores['telltale_phrases'] = 100
        
        # === LAYER 3: Structural Patterns ===
        structural_score = self._analyze_structural_authenticity(text)
        scores['structural'] = structural_score
        if structural_score < 70:
            violations.append(
                f"Structural authenticity {structural_score:.1f}/100 (too AI-like)"
            )
        
        # === LAYER 4: Statistical Markers ===
        stats_score = self._analyze_statistical_markers(text)
        scores['statistical'] = stats_score
        if stats_score < 70:
            violations.append(
                f"Statistical markers {stats_score:.1f}/100 (unnatural patterns)"
            )
        
        # === LAYER 5: Linguistic Authenticity ===
        linguistic_score = self._analyze_linguistic_authenticity(text)
        scores['linguistic'] = linguistic_score
        if linguistic_score < 70:
            violations.append(
                f"Linguistic authenticity {linguistic_score:.1f}/100 (too formal)"
            )
        
        # === CALCULATE OVERALL CONFIDENCE ===
        # Winston is 50% weight, others split remaining 50%
        if winston_score is not None:
            confidence = (
                winston_score * 0.50 +
                structural_score * 0.15 +
                stats_score * 0.15 +
                linguistic_score * 0.20
            ) / 100
        else:
            # Without Winston, reweight
            confidence = (
                structural_score * 0.35 +
                stats_score * 0.30 +
                linguistic_score * 0.35
            ) / 100
        
        # === DETERMINE VERDICT ===
        is_ai = len(violations) > 0 or confidence < 0.75
        
        if is_ai:
            recommendation = f"REJECT: {violations[0] if violations else 'Low confidence'}"
        else:
            recommendation = "PASS"
        
        return {
            'is_ai': is_ai,
            'confidence': confidence,
            'winston_score': winston_score,
            'violations': violations,
            'scores': scores,
            'recommendation': recommendation,
            'details': {
                'telltale_count': len(telltale_matches),
                'structural_issues': self._get_structural_issues(text),
                'statistical_issues': self._get_statistical_issues(text),
                'linguistic_issues': self._get_linguistic_issues(text)
            }
        }
    
    def _analyze_structural_authenticity(self, text: str) -> float:
        """
        Analyze structural patterns for AI signatures.
        
        Human writing:
        - Irregular sentence lengths (high CV)
        - Occasional fragments
        - Natural rhythm variations
        - Imperfect parallelism
        
        AI writing:
        - Uniform sentence lengths (low CV)
        - No fragments (too perfect)
        - Mechanical rhythm
        - Perfect parallelism
        """
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) < 2:
            return 50.0  # Baseline for single sentence
        
        # Calculate sentence length variation
        lengths = [len(s.split()) for s in sentences]
        cv = statistics.stdev(lengths) / statistics.mean(lengths) if lengths else 0
        
        # Scoring
        score = 100.0
        issues = []
        
        # Check 1: Sentence length uniformity (CV < 0.30 is suspicious)
        if cv < 0.30:
            score -= 30
            issues.append(f"Uniform sentence lengths (CV={cv:.2f})")
        
        # Check 2: No sentence fragments (too formal)
        fragments = [s for s in sentences if len(s.split()) < 4]
        if len(fragments) == 0 and len(sentences) > 3:
            score -= 20
            issues.append("No sentence fragments (too perfect)")
        
        # Check 3: All sentences start with capital (too formal)
        proper_starts = sum(1 for s in sentences if s[0].isupper())
        if proper_starts == len(sentences) and len(sentences) > 3:
            score -= 10
            issues.append("All sentences properly capitalized (too formal)")
        
        # Check 4: Perfect paragraph structure (AI tendency)
        if '\n\n' in text:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            para_lengths = [len(p.split()) for p in paragraphs]
            if len(paragraphs) > 2:
                para_cv = statistics.stdev(para_lengths) / statistics.mean(para_lengths)
                if para_cv < 0.20:
                    score -= 15
                    issues.append(f"Uniform paragraph lengths (CV={para_cv:.2f})")
        
        return max(0.0, score)
    
    def _analyze_statistical_markers(self, text: str) -> float:
        """
        Analyze statistical distributions for AI signatures.
        
        AI tends to:
        - Overuse hedging words
        - Overuse formal transitions
        - Overuse passive voice
        - Avoid contractions
        """
        word_count = len(text.split())
        score = 100.0
        issues = []
        
        # Check 1: Hedging words (>2 per 100 words is suspicious)
        hedging_matches = self.hedging_pattern.findall(text.lower())
        hedging_rate = (len(hedging_matches) / word_count) * 100
        if hedging_rate > 2.0:
            score -= 25
            issues.append(f"Excessive hedging: {hedging_rate:.1f} per 100 words")
        
        # Check 2: Formal transitions (>3 per 100 words is suspicious)
        transition_matches = self.transition_pattern.findall(text.lower())
        transition_rate = (len(transition_matches) / word_count) * 100
        if transition_rate > 3.0:
            score -= 25
            issues.append(f"Excessive transitions: {transition_rate:.1f} per 100 words")
        
        # Check 3: Passive voice (>20% of sentences is suspicious)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        passive_sentences = sum(
            1 for s in sentences if self.passive_pattern.search(s.lower())
        )
        passive_rate = (passive_sentences / len(sentences)) * 100 if sentences else 0
        if passive_rate > 20.0:
            score -= 20
            issues.append(f"Excessive passive voice: {passive_rate:.1f}%")
        
        # Check 4: Contraction absence (no contractions in >100 words is suspicious)
        contractions = re.findall(r"\w+\'[a-z]+", text, re.IGNORECASE)
        if word_count > 100 and len(contractions) == 0:
            score -= 15
            issues.append("No contractions (too formal)")
        
        # Check 5: Vocabulary diversity (type-token ratio)
        unique_words = len(set(text.lower().split()))
        ttr = unique_words / word_count if word_count else 0
        if ttr > 0.80 and word_count > 50:
            score -= 15
            issues.append(f"Suspiciously high vocabulary diversity (TTR={ttr:.2f})")
        
        return max(0.0, score)
    
    def _analyze_linguistic_authenticity(self, text: str) -> float:
        """
        Analyze linguistic patterns for human irregularity.
        
        Human writing:
        - Uses colloquialisms
        - Has minor "errors" (style choices)
        - Uses contractions
        - Varies formality
        
        AI writing:
        - Overly formal
        - Grammatically perfect
        - No colloquialisms
        - Uniform formality
        """
        score = 100.0
        issues = []
        
        # Check 1: Colloquial markers (good)
        colloquialisms = [
            'get', 'got', 'thing', 'stuff', 'a lot', 'lots',
            'kind of', 'sort of', 'pretty much', 'basically'
        ]
        colloquial_count = sum(
            1 for col in colloquialisms if col in text.lower()
        )
        if colloquial_count == 0 and len(text.split()) > 100:
            score -= 20
            issues.append("No colloquialisms (too formal)")
        
        # Check 2: Sentence starters (AI overuses "The", "This", "It")
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) >= 3:
            starters = [s.split()[0].lower() for s in sentences if s.split()]
            overused = sum(1 for s in starters if s in ['the', 'this', 'it'])
            if overused > len(sentences) * 0.6:
                score -= 25
                issues.append(f"Repetitive sentence starters: {overused}/{len(sentences)}")
        
        # Check 3: Complex vocabulary overuse
        long_words = [w for w in text.split() if len(w) > 10]
        long_word_rate = len(long_words) / len(text.split()) if text.split() else 0
        if long_word_rate > 0.15:
            score -= 15
            issues.append(f"Excessive complex vocabulary: {long_word_rate:.1%}")
        
        # Check 4: Number usage (AI tends to avoid specific numbers)
        numbers = re.findall(r'\b\d+\b', text)
        if len(text.split()) > 100 and len(numbers) == 0:
            score -= 10
            issues.append("No specific numbers (vague)")
        
        return max(0.0, score)
    
    def _get_structural_issues(self, text: str) -> List[str]:
        """Get list of structural issues for debugging"""
        issues = []
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) >= 2:
            lengths = [len(s.split()) for s in sentences]
            cv = statistics.stdev(lengths) / statistics.mean(lengths)
            if cv < 0.30:
                issues.append(f"Low sentence variation (CV={cv:.2f})")
        
        return issues
    
    def _get_statistical_issues(self, text: str) -> List[str]:
        """Get list of statistical issues for debugging"""
        issues = []
        word_count = len(text.split())
        
        hedging_matches = self.hedging_pattern.findall(text.lower())
        hedging_rate = (len(hedging_matches) / word_count) * 100 if word_count else 0
        if hedging_rate > 2.0:
            issues.append(f"High hedging rate: {hedging_rate:.1f}/100 words")
        
        return issues
    
    def _get_linguistic_issues(self, text: str) -> List[str]:
        """Get list of linguistic issues for debugging"""
        issues = []
        
        contractions = re.findall(r"\w+\'[a-z]+", text, re.IGNORECASE)
        if len(text.split()) > 100 and len(contractions) == 0:
            issues.append("No contractions found")
        
        return issues
