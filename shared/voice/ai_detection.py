"""
AI Detection Quality Module

Consolidated AI detection methods for identifying machine-generated text patterns.
Integrates with VoicePostProcessor for comprehensive quality validation.

Key Detection Areas:
1. Grammatical errors (subject-verb agreement, tense errors)
2. Repetitive patterns (word/phrase repetition, structure repetition)
3. Unnatural phrasing (awkward constructions, non-idiomatic)
4. Statistical anomalies (uniform sentence length, predictable rhythms)

Usage:
    from shared.voice.ai_detection import AIDetector
    
    detector = AIDetector()
    result = detector.detect_ai_patterns(text)
    
    if result['is_ai_like']:
        print(f"AI score: {result['ai_score']}/100")
        print(f"Issues: {result['issues']}")
"""

import logging
import os
import re
import statistics
from collections import Counter
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Get the directory containing this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PATTERNS_FILE = os.path.join(CURRENT_DIR, 'ai_detection_patterns.txt')


def load_patterns(patterns_file: str = PATTERNS_FILE) -> Dict[str, Any]:
    """
    Load detection patterns from configuration file.
    
    Returns:
        Dictionary with:
        - grammar_patterns: List of grammar pattern dicts
        - phrasing_patterns: List of phrasing pattern dicts
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
                   f"{len(config['phrasing_patterns'])} phrasing patterns from {patterns_file}")
        
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
    - Integrate seamlessly with existing voice system
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
        
        # Use thresholds from config if available, otherwise defaults
        if self.config['thresholds']:
            default_threshold = self.config['thresholds'].get('ai_detection', 70)
            strict_threshold = self.config['thresholds'].get('strict_mode', 60)
            self.ai_threshold = strict_threshold if strict_mode else default_threshold
        else:
            self.ai_threshold = 60.0 if strict_mode else 70.0  # Fallback defaults
    
    def detect_grammatical_errors(self, text: str) -> Dict[str, Any]:
        """
        Detect grammatical errors common in AI-generated text.
        
        Uses patterns loaded from configuration file.
        
        Args:
            text: Text to analyze
            
        Returns:
            {
                'has_errors': bool,
                'error_count': int,
                'errors': List[Dict],  # [{type, example, severity}]
                'severity': str  # 'none', 'minor', 'moderate', 'severe', 'critical'
            }
        """
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
        
        # Fallback to hardcoded patterns if config is empty
        if not self.config['grammar_patterns']:
            # Keep existing hardcoded patterns as fallback
            # Subject-verb disagreement patterns (CRITICAL - INSTANT FAIL)
            if re.search(r'\bdata\s+(lead|indicate|show|reveal|suggest)\b', text_lower):
                errors.append({
                    'type': 'subject_verb_disagreement',
                    'example': 'data lead/indicate/show (should be leads/indicates/shows)',
                    'severity': 'critical',
                    'pattern': 'plural_verb_with_singular_data'
                })
        
        # "The process achieve" (should be "achieves")
        if re.search(r'\b(the|this|that)\s+\w+\s+(achieve|maintain|indicate|demonstrate)\b', text_lower):
            errors.append({
                'type': 'subject_verb_disagreement',
                'example': 'the process achieve (should be achieves)',
                'severity': 'severe',
                'pattern': 'singular_subject_plural_verb'
            })
        
        # 2. Awkward verb constructions
        # "data lead to [verb]ing" (unnatural phrasing)
        if re.search(r'data\s+lead\s+to\s+\w+ing', text_lower):
            errors.append({
                'type': 'awkward_construction',
                'example': 'data lead to [verb]ing',
                'severity': 'critical',  # Changed to critical - this is blatantly wrong
                'pattern': 'data_lead_to_gerund'
            })
        
        # "achieves removal" (stiff, AI-like) - INCREASED SEVERITY
        # Allow optional adjective: "achieves [contaminant] removal"
        if re.search(r'achieves?\s+(\w+\s+)?(removal|restoration|preservation|elimination)', text_lower):
            errors.append({
                'type': 'unnatural_noun_pairing',
                'example': 'achieves [word] removal/restoration',
                'severity': 'moderate',  # Changed from minor to moderate
                'pattern': 'achieves_abstract_noun'
            })
        
        # 3. Article errors
        # Missing article before singular countable nouns
        article_errors = re.findall(
            r'\b(with|for|of|in)\s+(process|method|approach|technique|system)\b',
            text_lower
        )
        if len(article_errors) > 1:
            errors.append({
                'type': 'missing_article',
                'example': f'with/for/of process (should be "the process")',
                'severity': 'minor',
                'pattern': 'missing_definite_article'
            })
        
        # 4. Redundant passive constructions
        # "is achieved", "is maintained", "is preserved" (overused in AI text)
        passive_count = len(re.findall(
            r'\bis\s+(achieved|maintained|preserved|restored|removed)',
            text_lower
        ))
        if passive_count >= 2:
            errors.append({
                'type': 'excessive_passive',
                'example': f'{passive_count} passive constructions',
                'severity': 'moderate',
                'pattern': 'overuse_passive_voice'
            })
        
        # Calculate severity
        critical_count = sum(1 for e in errors if e['severity'] == 'critical')
        severe_count = sum(1 for e in errors if e['severity'] == 'severe')
        moderate_count = sum(1 for e in errors if e['severity'] == 'moderate')
        low_count = sum(1 for e in errors if e['severity'] == 'low')
        
        if critical_count >= 1:
            severity = 'critical'  # Instant fail
        elif severe_count >= 1:
            severity = 'severe'
        elif moderate_count >= 2 or (moderate_count >= 1 and len(errors) >= 3):
            severity = 'moderate'
        elif len(errors) >= 2 or low_count >= 2:
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
        """
        Detect repetitive patterns common in AI-generated text.
        
        AI text often exhibits:
        - Word/phrase repetition (same words appearing frequently)
        - Structural repetition (same sentence patterns)
        - Predictable rhythms (uniform sentence lengths)
        
        Args:
            text: Text to analyze
            
        Returns:
            {
                'has_repetition': bool,
                'repetition_score': float (0-100, higher = more repetitive),
                'patterns': List[Dict],  # [{type, details, severity}]
                'severity': str
            }
        """
        patterns = []
        text_lower = text.lower()
        
        # 1. Word frequency analysis
        words = re.findall(r'\b\w+\b', text_lower)
        word_counts = Counter(words)
        
        # Find high-frequency content words (exclude common function words)
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'of', 'to', 'in', 'for', 'on', 'with', 'from', 'by', 'at', 'as',
            'this', 'that', 'these', 'those', 'its', 'it', 'be', 'have', 'has'
        }
        
        content_word_counts = {
            word: count for word, count in word_counts.items()
            if word not in common_words and count >= 3
        }
        
        if content_word_counts:
            max_repetition = max(content_word_counts.values())
            if max_repetition >= 4:
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
                    'severity': 'moderate' if max_repetition >= 5 else 'minor'
                })
        
        # 2. Phrase repetition
        # Extract 3-word phrases
        three_word_phrases = []
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            # Skip phrases with too many common words
            if sum(1 for w in words[i:i+3] if w in common_words) < 3:
                three_word_phrases.append(phrase)
        
        phrase_counts = Counter(three_word_phrases)
        repeated_phrases = {p: c for p, c in phrase_counts.items() if c >= 2}
        
        if repeated_phrases:
            patterns.append({
                'type': 'phrase_repetition',
                'details': f"{len(repeated_phrases)} phrases repeated 2+ times",
                'severity': 'moderate'
            })
        
        # 3. Sentence structure repetition
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 2:
            # Extract sentence patterns (first 3 words)
            sentence_patterns = []
            for s in sentences:
                s_words = s.lower().split()[:3]
                if len(s_words) >= 2:
                    pattern = ' '.join(s_words)
                    sentence_patterns.append(pattern)
            
            pattern_counts = Counter(sentence_patterns)
            repeated_structures = sum(1 for count in pattern_counts.values() if count >= 2)
            
            if repeated_structures >= 2:
                patterns.append({
                    'type': 'structural_repetition',
                    'details': f"{repeated_structures} repeated sentence openings",
                    'severity': 'moderate'
                })
        
        # 4. Uniform sentence length (AI characteristic)
        if len(sentences) >= 3:
            sentence_lengths = [len(s.split()) for s in sentences]
            try:
                avg_length = statistics.mean(sentence_lengths)
                stdev = statistics.stdev(sentence_lengths)
                
                # Low variance = uniform lengths (AI-like)
                if stdev < 3 and avg_length > 10:
                    patterns.append({
                        'type': 'uniform_length',
                        'details': f"Low variance ({stdev:.1f}), avg {avg_length:.1f} words",
                        'severity': 'minor'
                    })
            except Exception:
                pass
        
        # Calculate repetition score (0-100, higher = more repetitive)
        score = 0.0
        
        for pattern in patterns:
            if pattern['severity'] == 'severe':
                score += 30
            elif pattern['severity'] == 'moderate':
                score += 20
            else:
                score += 10
        
        score = min(100.0, score)
        
        # Determine severity
        if score >= 60:
            severity = 'severe'
        elif score >= 40:
            severity = 'moderate'
        elif score >= 20:
            severity = 'minor'
        else:
            severity = 'none'
        
        return {
            'has_repetition': len(patterns) > 0,
            'repetition_score': score,
            'patterns': patterns,
            'severity': severity
        }
    
    def detect_unnatural_phrasing(self, text: str) -> Dict[str, Any]:
        """
        Detect unnatural phrasing common in AI-generated text.
        
        Uses patterns loaded from configuration file.
        
        Args:
            text: Text to analyze
            
        Returns:
            {
                'has_unnatural': bool,
                'unnatural_count': int,
                'examples': List[Dict],  # [{type, example, reason}]
                'severity': str
            }
        """
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
                        'matches': matches[:3]  # Show first 3 matches
                    })
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern_def['pattern']}': {e}")
                continue
        
        # Fallback to hardcoded patterns if config is empty
        if not self.config['phrasing_patterns']:
            # 1. Overly abstract noun constructions
            abstract_pairs = [
                ('achieves', 'removal'),
                ('achieves', 'restoration'),
                ('achieves', 'preservation'),
                ('performs', 'removal'),
                ('executes', 'cleaning'),
                ('conducts', 'restoration')
            ]
            
            for verb, noun in abstract_pairs:
                if f'{verb} {noun}' in text_lower:
                    examples.append({
                        'type': 'abstract_pairing',
                        'example': f'{verb} {noun}',
                        'reason': 'Overly formal, prefer "removes", "restores", "preserves"'
                    })
            
            # 2. Awkward passive-to-active transitions
            # "is achieved by laser" (awkward)
            if re.search(r'is\s+\w+ed\s+by\s+(laser|process|method)', text_lower):
                examples.append({
                    'type': 'awkward_passive',
                    'example': 'is [verb]ed by laser',
                    'reason': 'Awkward passive, prefer active voice'
                })
            
            # 3. Redundant hedging
            hedging_phrases = [
                'it can be said',
                'it is important to note',
                'it should be noted',
                'it is worth mentioning',
                'one might observe'
            ]
            
            for hedge in hedging_phrases:
                if hedge in text_lower:
                    examples.append({
                        'type': 'redundant_hedging',
                        'example': hedge,
                        'reason': 'Unnecessary hedging, state directly'
                    })
            
            # 4. Demonstrative overuse
            # "this process", "that method", "this approach" (AI overuses these)
            demonstrative_count = len(re.findall(
                r'\b(this|that)\s+(process|method|approach|technique|system)\b',
                text_lower
            ))
            
            if demonstrative_count >= 3:
                examples.append({
                    'type': 'demonstrative_overuse',
                    'example': f'{demonstrative_count} uses of this/that + noun',
                    'reason': 'Excessive demonstratives sound repetitive'
                })
            
            # 5. Gerund stacking
            # "[verb]ing [verb]ing" patterns (cleaning removing, processing maintaining)
            gerund_stacks = re.findall(r'\b\w+ing\s+\w+ing\b', text_lower)
            if gerund_stacks:
                examples.append({
                    'type': 'gerund_stacking',
                    'example': ', '.join(set(gerund_stacks)),
                    'reason': 'Awkward gerund combinations'
                })
        
        # Determine severity (use config severities if available)
        if len(examples) >= 4:
            severity = 'severe'
        elif len(examples) >= 2:
            severity = 'moderate'
        elif len(examples) == 1:
            # Check if it's a high-severity pattern
            if examples[0].get('severity') in ['severe', 'critical']:
                severity = 'moderate'
            else:
                severity = 'minor'
        else:
            severity = 'none'
        
        return {
            'has_unnatural': len(examples) > 0,
            'unnatural_count': len(examples),
            'examples': examples,
            'severity': severity
        }
    
    def detect_ai_patterns(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive AI pattern detection.
        
        Combines all detection methods into a single score and recommendation.
        
        Args:
            text: Text to analyze
            
        Returns:
            {
                'ai_score': float (0-100, higher = more AI-like),
                'is_ai_like': bool,  # True if score >= threshold
                'confidence': str,  # 'low', 'medium', 'high'
                'grammar': Dict,  # Grammatical errors
                'repetition': Dict,  # Repetitive patterns
                'phrasing': Dict,  # Unnatural phrasing
                'issues': List[str],  # All issues found
                'recommendation': str,  # 'accept', 'revise', 'regenerate'
                'severity': str  # Overall severity
            }
        """
        # Run all detection methods
        grammar = self.detect_grammatical_errors(text)
        repetition = self.detect_repetitive_patterns(text)
        phrasing = self.detect_unnatural_phrasing(text)
        
        # Calculate AI score (0-100, higher = more AI-like)
        score = 0.0
        
        # Get severity scores from config or use defaults
        severity_scores = self.config.get('severities', {
            'critical': 100,
            'severe': 50,
            'moderate': 30,
            'minor': 15,
            'low': 5
        })
        
        # Grammar errors - use severity score directly (already weighted in config)
        if grammar['severity'] == 'critical':
            score += severity_scores.get('critical', 100)
        elif grammar['severity'] == 'severe':
            score += severity_scores.get('severe', 50)
        elif grammar['severity'] == 'moderate':
            score += severity_scores.get('moderate', 30)
        elif grammar['severity'] == 'minor':
            score += severity_scores.get('minor', 15)
        elif grammar['severity'] == 'low':
            score += severity_scores.get('low', 5)
        
        # Repetition - apply score directly
        score += repetition['repetition_score'] * 0.3  # Scale to 30 max
        
        # Unnatural phrasing - use severity score directly
        if phrasing['severity'] == 'severe':
            score += severity_scores.get('severe', 50)
        elif phrasing['severity'] == 'moderate':
            score += severity_scores.get('moderate', 30)
        elif phrasing['severity'] == 'minor':
            score += severity_scores.get('minor', 15)
        elif phrasing['severity'] == 'low':
            score += severity_scores.get('low', 5)
        
        score = min(100.0, score)
        
        # Determine if AI-like
        is_ai_like = score >= self.ai_threshold
        
        # Determine confidence
        if score >= 80:
            confidence = 'high'
        elif score >= 60:
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
        
        # Determine overall severity
        severities = [grammar['severity'], repetition['severity'], phrasing['severity']]
        if 'severe' in severities:
            overall_severity = 'severe'
        elif 'moderate' in severities:
            overall_severity = 'moderate'
        elif 'minor' in severities:
            overall_severity = 'minor'
        else:
            overall_severity = 'none'
        
        # Determine recommendation
        if score >= 80:
            recommendation = 'regenerate'
        elif score >= 60:
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
            'issues': issues,
            'recommendation': recommendation,
            'severity': overall_severity
        }
    
    def format_report(self, result: Dict[str, Any]) -> str:
        """
        Format detection result as human-readable report.
        
        Args:
            result: Result from detect_ai_patterns()
            
        Returns:
            Formatted report string
        """
        lines = []
        
        lines.append(f"AI Detection Score: {result['ai_score']:.1f}/100")
        lines.append(f"Classification: {'AI-LIKE' if result['is_ai_like'] else 'HUMAN-LIKE'}")
        lines.append(f"Confidence: {result['confidence'].upper()}")
        lines.append(f"Recommendation: {result['recommendation'].upper()}")
        lines.append(f"Overall Severity: {result['severity'].upper()}")
        lines.append("")
        
        if result['issues']:
            lines.append(f"Issues Found ({len(result['issues'])}):")
            for issue in result['issues'][:10]:  # Limit to top 10
                lines.append(f"  • {issue}")
        else:
            lines.append("✅ No AI patterns detected")
        
        return '\n'.join(lines)


# Convenience function for quick analysis
def analyze_text_for_ai(text: str, strict: bool = False) -> Dict[str, Any]:
    """
    Convenience function for quick AI detection analysis.
    
    Args:
        text: Text to analyze
        strict: Use strict thresholds (default False)
        
    Returns:
        Detection result dict
    """
    detector = AIDetector(strict_mode=strict)
    return detector.detect_ai_patterns(text)


# Example usage
if __name__ == "__main__":
    # Test cases
    test_samples = [
        {
            'text': "Data lead to laser cleaning removing oils from polycarbonate, as the method results in preserved clarity.",
            'description': "Sample with grammar error (data lead)"
        },
        {
            'text': "The laser cleaning process achieves contaminant removal from Quartz Glass, while the surface exhibits preserved clarity.",
            'description': "Sample with unnatural phrasing (achieves removal)"
        },
        {
            'text': "Laser cleaning process achieves grime removal from Stoneware, while treatment results in preserving its structure.",
            'description': "Sample with repetitive pattern (achieves removal again)"
        },
        {
            'text': "Laser cleaning removes surface contaminants from Ceramic Matrix Composites while preserving fiber reinforcement and structural strength.",
            'description': "Good sample with natural phrasing"
        }
    ]
    
    detector = AIDetector(strict_mode=True)
    
    for i, sample in enumerate(test_samples, 1):
        print(f"\n{'='*60}")
        print(f"Sample {i}: {sample['description']}")
        print(f"{'='*60}")
        print(f"Text: {sample['text']}")
        print()
        
        result = detector.detect_ai_patterns(sample['text'])
        print(detector.format_report(result))
