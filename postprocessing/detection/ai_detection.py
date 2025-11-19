"""
AI Detection Quality Module

Consolidated AI detection methods for identifying machine-generated text patterns.
Integrates with processing system for comprehensive quality validation.

Key Detection Areas:
1. Grammatical errors (subject-verb agreement, tense errors)
2. Repetitive patterns (word/phrase repetition, structure repetition)
3. Unnatural phrasing (awkward constructions, non-idiomatic)
4. Statistical anomalies (uniform sentence length, predictable rhythms)
5. Linguistic dimensions (dependency structure, lexical diversity, formality)

Usage:
    from postprocessing.detection.ai_detection import AIDetector
    
    detector = AIDetector()
    result = detector.detect_ai_patterns(text)
    
    if result['is_ai_like']:
        print(f"AI score: {result['ai_score']}/100")
        print(f"Issues: {result['issues']}")
"""

from typing import Dict, Any
import re
import statistics
from collections import Counter
import logging
import os

# Import centralized config loader
from generation.config.config_loader import get_config

logger = logging.getLogger(__name__)

# Get the directory containing this file (processing/detection/)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to centralized patterns file in /prompts
PATTERNS_FILE = os.path.join(CURRENT_DIR, 'patterns', 'ai_detection_patterns.txt')


def load_patterns(patterns_file: str = PATTERNS_FILE) -> Dict[str, Any]:
    """
    Load detection patterns from configuration file.
    
    Returns:
        Dictionary with:
        - grammar_patterns: List of grammar pattern dicts
        - phrasing_patterns: List of phrasing pattern dicts
        - linguistic_patterns: List of linguistic dimension patterns
        - repetition_thresholds: Dict of repetition thresholds
        - exclude_words: Set of common function words
        - weights: Dict of scoring weights
        - severities: Dict of severity scores
        - thresholds: Dict of thresholds
    """
    config = {
        'grammar_patterns': [],
        'phrasing_patterns': [],
        'linguistic_patterns': [],
        'repetition_thresholds': {},
        'exclude_words': set(),
        'weights': {},
        'severities': {},
        'thresholds': {},
        'recommendations': {}
    }
    
    if not os.path.exists(patterns_file):
        logger.warning(f"Patterns file not found: {patterns_file}. Using defaults.")
        return config
    
    try:
        with open(patterns_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Special handling: patterns contain | for regex alternation
                # Expected format: category|name|pattern|severity|example|reason
                # Pattern field may contain | characters
                
                parts = line.split('|')
                if len(parts) < 4:
                    continue
                
                category = parts[0].strip()
                name = parts[1].strip()
                
                # For grammar/phrasing patterns, need to reconstruct pattern field
                # which may contain | for alternation
                # Strategy: Find the severity field (known values) and work backwards
                known_severities = {'critical', 'severe', 'moderate', 'minor', 'low'}
                
                # Find the severity field position
                severity_idx = None
                for i, part in enumerate(parts[2:], start=2):
                    if part.strip() in known_severities:
                        severity_idx = i
                        break
                
                if category in ['grammar', 'phrasing', 'linguistic_dimensions'] and severity_idx:
                    # Reconstruct pattern from parts[2] to parts[severity_idx-1]
                    pattern = '|'.join(parts[2:severity_idx]).strip()
                    severity = parts[severity_idx].strip()
                    example = parts[severity_idx + 1].strip() if severity_idx + 1 < len(parts) else ''
                    reason = parts[severity_idx + 2].strip() if severity_idx + 2 < len(parts) else ''
                    
                    pattern_dict = {
                        'name': name,
                        'pattern': pattern,
                        'severity': severity,
                        'example': example,
                        'reason': reason
                    }
                    
                    if category == 'grammar':
                        config['grammar_patterns'].append(pattern_dict)
                    elif category == 'phrasing':
                        config['phrasing_patterns'].append(pattern_dict)
                    elif category == 'linguistic_dimensions':
                        config['linguistic_patterns'].append(pattern_dict)
                
                # Exclude words
                elif category == 'exclude_words':
                    config['exclude_words'].update(p.strip() for p in parts[1:] if p.strip())
                
                # Weights
                elif category == 'weight':
                    if len(parts) >= 3:
                        try:
                            config['weights'][parts[1].strip()] = int(parts[2].strip())
                        except ValueError:
                            pass
                
                # Severities
                elif category == 'severity':
                    if len(parts) >= 3:
                        try:
                            config['severities'][parts[1].strip()] = int(parts[2].strip())
                        except ValueError:
                            pass
                
                # Thresholds
                elif category == 'threshold':
                    if len(parts) >= 3:
                        try:
                            config['thresholds'][parts[1].strip()] = int(parts[2].strip())
                        except ValueError:
                            # Handle non-numeric thresholds
                            config['thresholds'][parts[1].strip()] = parts[2].strip()
        
        logger.info(f"Loaded {len(config['grammar_patterns'])} grammar patterns, "
                   f"{len(config['phrasing_patterns'])} phrasing patterns, "
                   f"{len(config['linguistic_patterns'])} linguistic patterns")
        
    except Exception as e:
        logger.error(f"Failed to load patterns file: {e}")
    
    return config


class AIDetector:
    """
    Detect AI-generated text patterns through linguistic analysis.
    
    Design Philosophy:
    - Fail-fast on obvious AI patterns
    - Use multiple detection strategies
    - Provide actionable feedback
    - Integrate seamlessly with processing system
    """
    
    def __init__(self, strict_mode: bool = False, patterns_file: str = PATTERNS_FILE):
        """
        Initialize AI detector.
        
        Args:
            strict_mode: If True, use stricter thresholds (default False)
            patterns_file: Path to patterns configuration file
        """
        self.strict_mode = strict_mode
        self.config = load_patterns(patterns_file)
        
        # Load threshold from centralized config if available, otherwise use patterns file
        try:
            from generation.config.config_loader import get_config
            proc_config = get_config()
            self.ai_threshold = proc_config.get_ai_threshold(strict_mode=strict_mode)
            logger.info(f"Using AI threshold from processing/config.yaml: {self.ai_threshold}")
        except Exception as e:
            logger.warning(f"Could not load from processing/config.yaml: {e}, using patterns file")
            # Fallback to patterns file or hardcoded defaults
            if self.config['thresholds']:
                default_threshold = self.config['thresholds'].get('ai_detection', 40)
                strict_threshold = self.config['thresholds'].get('strict_mode', 30)
                self.ai_threshold = strict_threshold if strict_mode else default_threshold
            else:
                self.ai_threshold = 30.0 if strict_mode else 40.0  # Last resort defaults
    
    def detect(self, text: str) -> Dict:
        """
        Main detection method compatible with ensemble.py interface.
        
        Returns result in format expected by AIDetectorEnsemble.
        """
        result = self.detect_ai_patterns(text)
        
        # Convert to ensemble-compatible format
        return {
            'ai_score': result['ai_score'] / 100.0,  # Normalize to 0-1
            'method': 'advanced_pattern',
            'patterns_found': len(result['issues']),
            'details': result
        }
    
    def detect_grammatical_errors(self, text: str) -> Dict[str, Any]:
        """Detect grammatical errors using loaded patterns."""
        errors = []
        text_lower = text.lower()
        
        # Use loaded grammar patterns
        for pattern_def in self.config['grammar_patterns']:
            try:
                if re.search(pattern_def['pattern'], text_lower):
                    errors.append({
                        'type': pattern_def['name'],
                        'example': pattern_def['example'],
                        'severity': pattern_def['severity'],
                        'pattern': pattern_def['name']
                    })
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern_def['pattern']}': {e}")
                continue
        
        # Calculate severity
        critical_count = sum(1 for e in errors if e['severity'] == 'critical')
        severe_count = sum(1 for e in errors if e['severity'] == 'severe')
        moderate_count = sum(1 for e in errors if e['severity'] == 'moderate')
        
        if critical_count >= 1:
            severity = 'critical'
        elif severe_count >= 1:
            severity = 'severe'
        elif moderate_count >= 2:
            severity = 'moderate'
        elif len(errors) >= 2:
            severity = 'minor'
        else:
            severity = 'none'
        
        return {
            'has_errors': len(errors) > 0,
            'error_count': len(errors),
            'errors': errors,
            'severity': severity
        }
    
    def detect_repetitive_patterns(self, text: str) -> Dict[str, Any]:
        """Detect repetitive patterns."""
        patterns = []
        text_lower = text.lower()
        
        # Word frequency analysis
        words = re.findall(r'\b\w+\b', text_lower)
        word_counts = Counter(words)
        
        # Use exclude words from config or defaults
        common_words = self.config['exclude_words'] if self.config['exclude_words'] else {
            'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'of', 'to', 'in', 'for', 'on', 'with', 'from', 'by', 'at', 'as'
        }
        
        # Get thresholds from centralized config, fallback to patterns file
        try:
            from generation.config.config_loader import get_config
            proc_config = get_config()
            thresholds = proc_config.get_repetition_thresholds()
            word_freq_threshold = thresholds['word_frequency']
            word_freq_critical = thresholds['word_frequency_critical']
        except Exception:
            # Fallback to patterns file defaults
            word_freq_threshold = 3  # Default from patterns file
            word_freq_critical = 5   # Critical threshold from patterns file
        
        content_word_counts = {
            word: count for word, count in word_counts.items()
            if word not in common_words and count >= word_freq_threshold
        }
        
        if content_word_counts:
            max_repetition = max(content_word_counts.values())
            if max_repetition >= word_freq_threshold:
                top_repeated = [
                    f"{word}({count})"
                    for word, count in sorted(
                        content_word_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:3]
                ]
                patterns.append({
                    'type': 'word_repetition',
                    'details': f"Words repeated 3+ times: {', '.join(top_repeated)}",
                    'severity': 'severe' if max_repetition >= word_freq_critical else 'moderate'
                })
        
        # Sentence structure repetition
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 2:
            sentence_patterns = []
            for s in sentences:
                s_words = s.lower().split()[:3]
                if len(s_words) >= 2:
                    pattern = ' '.join(s_words)
                    sentence_patterns.append(pattern)
            
            pattern_counts = Counter(sentence_patterns)
            # Get threshold from centralized config, fallback to default
            try:
                from generation.config.config_loader import get_config
                proc_config = get_config()
                thresholds = proc_config.get_repetition_thresholds()
                struct_repetition_threshold = thresholds['structural_repetition']
            except Exception:
                struct_repetition_threshold = 2  # Fallback default
            
            repeated_structures = sum(1 for count in pattern_counts.values() if count >= struct_repetition_threshold)
            
            if repeated_structures >= struct_repetition_threshold:
                patterns.append({
                    'type': 'structural_repetition',
                    'details': f"{repeated_structures} repeated sentence openings",
                    'severity': 'moderate'
                })
        
        # Calculate repetition score
        score = sum(30 if p['severity'] == 'severe' else 20 if p['severity'] == 'moderate' else 10 
                   for p in patterns)
        score = min(100.0, score)
        
        severity = 'severe' if score >= 60 else 'moderate' if score >= 40 else 'minor' if score >= 20 else 'none'
        
        return {
            'has_repetition': len(patterns) > 0,
            'repetition_score': score,
            'patterns': patterns,
            'severity': severity
        }
    
    def detect_unnatural_phrasing(self, text: str) -> Dict[str, Any]:
        """Detect unnatural phrasing using loaded patterns."""
        examples = []
        text_lower = text.lower()
        
        # Use loaded phrasing patterns
        for pattern_def in self.config['phrasing_patterns']:
            try:
                matches = re.findall(pattern_def['pattern'], text_lower)
                if matches:
                    examples.append({
                        'type': pattern_def['name'],
                        'example': pattern_def['example'],
                        'reason': pattern_def['reason'],
                        'severity': pattern_def['severity'],
                        'matches': matches[:3]
                    })
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern_def['pattern']}': {e}")
                continue
        
        # Determine severity
        critical_count = sum(1 for e in examples if e.get('severity') == 'critical')
        severe_count = sum(1 for e in examples if e.get('severity') == 'severe')
        
        if critical_count >= 1:
            severity = 'critical'
        elif severe_count >= 1 or len(examples) >= 4:
            severity = 'severe'
        elif len(examples) >= 2:
            severity = 'moderate'
        elif len(examples) == 1:
            severity = 'minor'
        else:
            severity = 'none'
        
        return {
            'has_unnatural': len(examples) > 0,
            'unnatural_count': len(examples),
            'examples': examples,
            'severity': severity
        }
    
    def detect_linguistic_dimensions(self, text: str) -> Dict[str, Any]:
        """
        Detect linguistic dimension patterns using loaded patterns.
        
        Checks for:
        - Dependency minimization (over-optimized syntax)
        - Pronoun bias (gender imbalance)
        - Lexical diversity (MTLD scores)
        - Stylistic formality (over-formal word choice)
        """
        issues = []
        text_lower = text.lower()
        
        # Use loaded linguistic dimension patterns
        for pattern_def in self.config['linguistic_patterns']:
            pattern_name = pattern_def['name']
            
            try:
                # For regex-based patterns
                if 'formal_words' in pattern_name or 'pronoun' in pattern_name:
                    matches = re.findall(pattern_def['pattern'], text_lower)
                    if matches:
                        issues.append({
                            'type': pattern_name,
                            'example': pattern_def['example'],
                            'reason': pattern_def['reason'],
                            'severity': pattern_def['severity'],
                            'count': len(matches)
                        })
                # For MTLD/dependency patterns (would need specialized calculation)
                # Note: These require external libraries or scripts, so we flag for manual review
                elif 'lexical_diversity' in pattern_name or 'dependency' in pattern_name:
                    # Placeholder: Would need textstat or spacy for actual calculation
                    # For now, just load the pattern definition for documentation
                    pass
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern_def['pattern']}': {e}")
                continue
        
        # Calculate severity
        critical_count = sum(1 for i in issues if i['severity'] == 'critical')
        severe_count = sum(1 for i in issues if i['severity'] == 'severe')
        moderate_count = sum(1 for i in issues if i['severity'] == 'moderate')
        
        if critical_count >= 1:
            severity = 'critical'
        elif severe_count >= 1:
            severity = 'severe'
        elif moderate_count >= 1:
            severity = 'moderate'
        elif len(issues) >= 1:
            severity = 'minor'
        else:
            severity = 'none'
        
        return {
            'has_linguistic_issues': len(issues) > 0,
            'issue_count': len(issues),
            'issues': issues,
            'severity': severity
        }
    
    def detect_ai_patterns(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive AI pattern detection.
        
        Returns:
            {
                'ai_score': float (0-100),
                'is_ai_like': bool,
                'confidence': str,
                'grammar': Dict,
                'repetition': Dict,
                'phrasing': Dict,
                'linguistic': Dict,
                'issues': List[str],
                'recommendation': str,
                'severity': str
            }
        """
        # Run all detection methods
        grammar = self.detect_grammatical_errors(text)
        repetition = self.detect_repetitive_patterns(text)
        phrasing = self.detect_unnatural_phrasing(text)
        linguistic = self.detect_linguistic_dimensions(text)
        
        # Calculate AI score using weights from config
        score = 0.0
        
        severity_scores = self.config.get('severities', {
            'critical': 100,
            'severe': 50,
            'moderate': 30,
            'minor': 15,
            'low': 5
        })
        
        weights = self.config.get('weights', {
            'grammar': 20,
            'repetition': 25,
            'phrasing': 35,
            'linguistic_dimensions': 15,
            'stylistic': 5
        })
        
        # Grammar errors
        if grammar['severity'] in severity_scores:
            score += severity_scores[grammar['severity']] * (weights.get('grammar', 20) / 100)
        
        # Repetition
        score += repetition['repetition_score'] * (weights.get('repetition', 25) / 100)
        
        # Unnatural phrasing
        if phrasing['severity'] in severity_scores:
            score += severity_scores[phrasing['severity']] * (weights.get('phrasing', 35) / 100)
        
        # Linguistic dimensions
        if linguistic['severity'] in severity_scores:
            score += severity_scores[linguistic['severity']] * (weights.get('linguistic_dimensions', 15) / 100)
        
        score = min(100.0, score)
        
        # Determine if AI-like (use threshold from centralized config)
        is_ai_like = score >= self.ai_threshold
        
        # Determine confidence (use thresholds from centralized config if available)
        try:
            from generation.config.config_loader import get_config
            proc_config = get_config()
            conf_thresholds = proc_config.get_confidence_thresholds()
            high_conf_threshold = conf_thresholds['high']
            medium_conf_threshold = conf_thresholds['medium']
        except Exception:
            # Fallback to patterns file or defaults
            high_conf_threshold = self.config.get('thresholds', {}).get('quality_minimum', 70)
            medium_conf_threshold = 50
        
        if score >= high_conf_threshold:
            confidence = 'high'
        elif score >= medium_conf_threshold:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Collect all issues
        issues = []
        for error in grammar['errors']:
            issues.append(f"[Grammar] {error['example']}")
        for pattern in repetition['patterns']:
            issues.append(f"[Repetition] {pattern['details']}")
        for example in phrasing['examples']:
            issues.append(f"[Phrasing] {example['example']}")
        for issue in linguistic['issues']:
            issues.append(f"[Linguistic] {issue['example']}")
        
        # Overall severity
        severities = [grammar['severity'], repetition['severity'], phrasing['severity'], linguistic['severity']]
        if 'critical' in severities:
            overall_severity = 'critical'
        elif 'severe' in severities:
            overall_severity = 'severe'
        elif 'moderate' in severities:
            overall_severity = 'moderate'
        elif 'minor' in severities:
            overall_severity = 'minor'
        else:
            overall_severity = 'none'
        
        # Recommendation (use thresholds from centralized config if available)
        try:
            from generation.config.config_loader import get_config
            proc_config = get_config()
            rec_thresholds = proc_config.get_recommendation_thresholds()
            regenerate_threshold = rec_thresholds['regenerate']
            revise_threshold = rec_thresholds['revise']
        except Exception:
            # Fallback to patterns file or defaults
            regenerate_threshold = self.config.get('thresholds', {}).get('quality_minimum', 70)
            revise_threshold = 50
        
        if score >= regenerate_threshold:
            recommendation = 'regenerate'
        elif score >= revise_threshold:
            recommendation = 'revise'
        else:
            recommendation = 'accept'
        
        return {
            'ai_score': score,
            'is_ai_like': is_ai_like,
            'confidence': confidence,
            'grammar': grammar,
            'repetition': repetition,
            'phrasing': phrasing,
            'linguistic': linguistic,
            'issues': issues,
            'recommendation': recommendation,
            'severity': overall_severity
        }

