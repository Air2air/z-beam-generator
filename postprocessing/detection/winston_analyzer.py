"""
Winston AI Feedback Analyzer

Analyzes sentence-level Winston API feedback to guide intelligent retry decisions.
Compliant with fail-fast architecture - no fallbacks, clear error signaling.
"""

import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)


class WinstonFeedbackAnalyzer:
    """
    Analyze Winston API sentence-level feedback to determine retry strategy.
    
    Uses sentence scores to detect:
    - Uniform failures (all sentences AI-like)
    - Partial failures (some good, some bad)
    - Borderline cases (close to passing)
    
    Provides actionable recommendations for retry decisions.
    """
    
    # AI pattern detection (common AI-generated phrases)
    AI_PATTERNS = [
        r'\breveals?\b',
        r'\butilizes?\b',
        r'\bshowcases?\b',
        r'\bdemonstrates?\b',
        r'\bexhibits?\b',
        r'\bprovides?\b',
        r'\benables?\b',
        r'\boffers?\b',
        r'\bfeatures?\b',
        r'\bensures?\b',
        r'stands at',
        r'remains at',
        r'maintains at',
    ]
    
    def analyze_failure(self, winston_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze why content failed Winston detection.
        
        Args:
            winston_response: Full Winston API response with sentence data
            
        Returns:
            Dict containing:
            - failure_type: 'uniform', 'partial', or 'borderline'
            - recommendation: 'retry', 'adjust_temperature', or 'fail'
            - retry_worth: bool indicating if retry likely to help
            - worst_sentences: List of most AI-like sentences
            - patterns: Detected AI patterns in text
            - guidance: Human-readable explanation
        """
        sentences = self._validate_sentences(winston_response)
        
        # Extract scores
        scores = [s['score'] for s in sentences]
        avg_score = sum(scores) / len(scores) if scores else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        logger.info(f"[WINSTON ANALYZER] Sentence scores: avg={avg_score:.1f}, min={min_score}, max={max_score}")
        logger.info(f"[WINSTON ANALYZER] Total sentences: {len(sentences)}")
        
        # Count sentences by quality
        excellent = [s for s in sentences if s['score'] >= 70]
        good = [s for s in sentences if 50 <= s['score'] < 70]
        poor = [s for s in sentences if 30 <= s['score'] < 50]
        terrible = [s for s in sentences if s['score'] < 30]
        
        logger.info(f"[WINSTON ANALYZER] Distribution: excellent={len(excellent)}, good={len(good)}, poor={len(poor)}, terrible={len(terrible)}")
        
        # Detect AI patterns in worst sentences
        worst_sentences = sorted(sentences, key=lambda s: s['score'])[:3]
        detected_patterns = self._detect_ai_patterns(worst_sentences)
        
        # Determine failure type and recommendation
        
        # UNIFORM FAILURE: All or nearly all sentences are terrible (avg < 20)
        if avg_score < 20 and len(terrible) >= len(sentences) * 0.8:
            return {
                'failure_type': 'uniform',
                'recommendation': 'adjust_temperature',
                'retry_worth': False,  # Systematic issue, not random
                'worst_sentences': worst_sentences,
                'patterns': detected_patterns,
                'guidance': f'All {len(sentences)} sentences failed badly (avg {avg_score:.1f}%). Need prompt/temperature adjustment.',
                'scores': {
                    'avg': avg_score,
                    'min': min_score,
                    'max': max_score,
                    'distribution': {
                        'excellent': len(excellent),
                        'good': len(good),
                        'poor': len(poor),
                        'terrible': len(terrible)
                    }
                }
            }
        
        # PARTIAL FAILURE: Mixed quality (some good, some bad)
        if len(excellent) > 0 or len(good) > 0:
            good_count = len(excellent) + len(good)
            return {
                'failure_type': 'partial',
                'recommendation': 'retry',
                'retry_worth': True,  # Has potential
                'good_count': good_count,
                'worst_sentences': worst_sentences,
                'patterns': detected_patterns,
                'guidance': f'{good_count}/{len(sentences)} sentences passed. Retry might generate all-good content.',
                'scores': {
                    'avg': avg_score,
                    'min': min_score,
                    'max': max_score,
                    'distribution': {
                        'excellent': len(excellent),
                        'good': len(good),
                        'poor': len(poor),
                        'terrible': len(terrible)
                    }
                }
            }
        
        # BORDERLINE: Consistently mediocre (avg 30-50)
        if 30 <= avg_score < 50:
            return {
                'failure_type': 'borderline',
                'recommendation': 'retry_once',
                'retry_worth': True,  # Slight variation might push over
                'worst_sentences': worst_sentences,
                'patterns': detected_patterns,
                'guidance': f'Borderline quality (avg {avg_score:.1f}%). One more attempt might succeed.',
                'scores': {
                    'avg': avg_score,
                    'min': min_score,
                    'max': max_score,
                    'distribution': {
                        'excellent': len(excellent),
                        'good': len(good),
                        'poor': len(poor),
                        'terrible': len(terrible)
                    }
                }
            }
        
        # POOR: Everything is poor quality (avg 20-30)
        return {
            'failure_type': 'poor',
            'recommendation': 'adjust_temperature',
            'retry_worth': False,
            'worst_sentences': worst_sentences,
            'patterns': detected_patterns,
            'guidance': f'Consistently poor quality (avg {avg_score:.1f}%). Unlikely to improve with retry.',
            'scores': {
                'avg': avg_score,
                'min': min_score,
                'max': max_score,
                'distribution': {
                    'excellent': len(excellent),
                    'good': len(good),
                    'poor': len(poor),
                    'terrible': len(terrible)
                }
            }
        }

    def _validate_sentences(self, winston_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate Winston response sentence schema and return normalized sentence list."""
        if 'sentences' not in winston_response:
            raise KeyError("winston_response missing required key: sentences")

        sentences = winston_response['sentences']
        if not isinstance(sentences, list):
            raise ValueError("winston_response['sentences'] must be a list")
        if not sentences:
            raise ValueError("winston_response['sentences'] must not be empty")

        for idx, sentence in enumerate(sentences, 1):
            if 'score' not in sentence:
                raise KeyError(f"Sentence #{idx} missing required key: score")
            if 'text' not in sentence:
                raise KeyError(f"Sentence #{idx} missing required key: text")
            score = sentence['score']
            if not isinstance(score, (int, float)):
                raise TypeError(f"Sentence #{idx} score must be numeric, got {type(score).__name__}")

        return sentences
    
    def _detect_ai_patterns(self, sentences: List[Dict[str, Any]]) -> List[str]:
        """
        Detect common AI-generated patterns in sentences.
        
        Args:
            sentences: List of sentence dicts with 'text' field
            
        Returns:
            List of detected pattern descriptions
        """
        detected = []
        
        for sentence in sentences:
            text = sentence['text'].lower()
            for pattern in self.AI_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        detected.append(f"'{match.group()}' in: {text[:50]}...")
        
        return detected[:5]  # Return top 5 patterns
    
    def should_extend_attempts(
        self, 
        current_attempt: int, 
        winston_result: Dict[str, Any], 
        max_extensions: int = 2,
        absolute_max: int = 3
    ) -> bool:
        """
        Decide if attempts should be extended based on Winston feedback.
        
        Args:
            current_attempt: Current attempt number (1-based)
            winston_result: Winston API response dict
            max_extensions: Maximum number of additional attempts to allow
            absolute_max: Absolute maximum attempts (safety limit)
            
        Returns:
            True if should extend attempts, False otherwise
        """
        # Safety: Never exceed absolute max
        if current_attempt >= absolute_max:
            logger.info(f"[WINSTON ANALYZER] At absolute max ({absolute_max}), no extension")
            return False
        
        # Analyze the failure
        analysis = self.analyze_failure(winston_result)
        
        # Only extend if retry is worth it
        if 'retry_worth' not in analysis:
            raise KeyError("analyze_failure() result missing required key: retry_worth")

        if not analysis['retry_worth']:
            logger.info(f"[WINSTON ANALYZER] Retry not worth it: {analysis['failure_type']}")
            return False
        
        # Check if we've used up our extensions
        extensions_used = current_attempt - 1
        if extensions_used >= max_extensions:
            logger.info(f"[WINSTON ANALYZER] Max extensions ({max_extensions}) reached")
            return False
        
        logger.info(f"✅ [WINSTON ANALYZER] Extension approved: {analysis['guidance']}")
        return True
