#!/usr/bin/env python3
"""
Comprehensive Dynamic Duplication Detection System

Detects formulaic patterns, repetitive structures, and robotic writing
across multiple dimensions using statistical analysis and NLP techniques.

Part of the validation pipeline - catches duplication that simple word
matching misses.
"""

import re
import logging
from typing import Dict, List
from collections import Counter
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class DuplicationAnalysis:
    """Results from duplication detection."""
    passed: bool
    score: float  # 0-100, higher is better
    violations: List[str]
    warnings: List[str]
    patterns: Dict[str, any]
    recommendations: List[str]


class DuplicationDetector:
    """
    Advanced duplication detection using multiple analysis techniques.
    
    Detects:
    1. Repetitive sentence structures
    2. Overused connectors and transitions
    3. Formulaic patterns (e.g., [Action] + [This + Benefit])
    4. Uniform word count distributions
    5. N-gram repetition (bigrams, trigrams)
    6. Parallel syntactic structures
    7. Template-driven writing
    """
    
    # Configurable thresholds
    THRESHOLDS = {
        'connector_max_pct': 40,  # Max % of answers using same connector
        'word_cv_min': 10,  # Min coefficient of variation for word counts
        'word_range_min': 15,  # Min range between shortest/longest answer
        'bigram_max_pct': 30,  # Max % for any 2-word phrase
        'trigram_max_pct': 25,  # Max % for any 3-word phrase
        'sentence_start_max_pct': 35,  # Max % for any sentence starter
        'structure_diversity_min': 0.6,  # Min diversity score (0-1)
    }
    
    # Common AI connectors to watch for
    AI_CONNECTORS = [
        'this', 'these', 'those', 'such',
        'additionally', 'furthermore', 'moreover',
        'however', 'therefore', 'thus', 'hence',
        'consequently', 'accordingly', 'subsequently'
    ]
    
    # Formulaic patterns (regex)
    FORMULAIC_PATTERNS = [
        r'^(employ|apply|utilize|use)\s+\w+.*\.\s+this\s+\w+',  # [Action] + This
        r'^(laser|pulsed|regular)\s+\w+.*\.\s+(this|it)\s+\w+',  # [Subject] + This/It
        r'^\w+\s+\w+\s+\w+.*\.\s+this\s+(ensures|supports|sustains|restores)',  # Pattern + This [verb]
    ]
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize duplication detector.
        
        Args:
            strict_mode: If True, uses stricter thresholds
        """
        self.strict_mode = strict_mode
        if strict_mode:
            # Tighten thresholds in strict mode
            self.THRESHOLDS['connector_max_pct'] = 35
            self.THRESHOLDS['word_cv_min'] = 12
            self.THRESHOLDS['sentence_start_max_pct'] = 30
    
    def analyze(self, items: List[Dict], component_type: str = 'faq') -> DuplicationAnalysis:
        """
        Perform comprehensive duplication analysis.
        
        Args:
            items: List of content items (FAQ questions, Caption sections, etc.)
            component_type: Type of component ('faq', 'caption', 'subtitle')
            
        Returns:
            DuplicationAnalysis with all findings
        """
        violations = []
        warnings = []
        patterns = {}
        recommendations = []
        
        # Extract text based on component type
        if component_type == 'faq':
            texts = [item.get('answer', '') for item in items if 'answer' in item]
        elif component_type == 'caption':
            texts = []
            if 'before' in items:
                texts.append(items['before'])
            if 'after' in items:
                texts.append(items['after'])
        elif component_type == 'subtitle':
            texts = [items.get('text', '')] if isinstance(items, dict) else [items]
        else:
            texts = [str(item) for item in items]
        
        if not texts:
            return DuplicationAnalysis(
                passed=False,
                score=0,
                violations=["No text content found"],
                warnings=[],
                patterns={},
                recommendations=[]
            )
        
        # Run all detection methods
        score = 100
        
        # 1. Connector overuse detection
        connector_analysis = self._detect_connector_overuse(texts)
        patterns['connectors'] = connector_analysis
        if connector_analysis['violations']:
            violations.extend(connector_analysis['violations'])
            score -= 15
        if connector_analysis['warnings']:
            warnings.extend(connector_analysis['warnings'])
            score -= 5
        
        # 2. Word count uniformity
        uniformity_analysis = self._detect_word_count_uniformity(texts)
        patterns['uniformity'] = uniformity_analysis
        if uniformity_analysis['cv'] < self.THRESHOLDS['word_cv_min']:
            violations.append(
                f"Word count too uniform: CV {uniformity_analysis['cv']:.1f}% "
                f"(min {self.THRESHOLDS['word_cv_min']}%)"
            )
            score -= 15
        if uniformity_analysis['range'] < self.THRESHOLDS['word_range_min']:
            violations.append(
                f"Word count range too narrow: {uniformity_analysis['range']}w "
                f"(min {self.THRESHOLDS['word_range_min']}w)"
            )
            score -= 10
        
        # 3. N-gram repetition
        ngram_analysis = self._detect_ngram_repetition(texts)
        patterns['ngrams'] = ngram_analysis
        if ngram_analysis['violations']:
            violations.extend(ngram_analysis['violations'])
            score -= 10
        if ngram_analysis['warnings']:
            warnings.extend(ngram_analysis['warnings'])
            score -= 3
        
        # 4. Sentence structure patterns
        structure_analysis = self._detect_structure_patterns(texts)
        patterns['structures'] = structure_analysis
        if structure_analysis['diversity'] < self.THRESHOLDS['structure_diversity_min']:
            violations.append(
                f"Low structural diversity: {structure_analysis['diversity']:.2f} "
                f"(min {self.THRESHOLDS['structure_diversity_min']})"
            )
            score -= 20
        
        # 5. Formulaic pattern detection
        formula_analysis = self._detect_formulaic_patterns(texts)
        patterns['formulas'] = formula_analysis
        if formula_analysis['matches']:
            violations.extend([
                f"Formulaic pattern detected: {pattern} ({count} occurrences)"
                for pattern, count in formula_analysis['matches'].items()
            ])
            score -= len(formula_analysis['matches']) * 10
        
        # 6. Sentence starter analysis
        starter_analysis = self._analyze_sentence_starters(texts)
        patterns['starters'] = starter_analysis
        if starter_analysis['violations']:
            violations.extend(starter_analysis['violations'])
            score -= 8
        
        # 7. Parallel structure detection
        parallel_analysis = self._detect_parallel_structures(texts)
        patterns['parallel'] = parallel_analysis
        if parallel_analysis['score'] < 0.5:
            warnings.append(
                f"Excessive parallel structures detected (variation score: {parallel_analysis['score']:.2f})"
            )
            score -= 5
        
        # Generate recommendations
        recommendations = self._generate_recommendations(patterns, violations, warnings)
        
        # Cap score
        score = max(0, min(100, score))
        
        return DuplicationAnalysis(
            passed=score >= 70 and len(violations) == 0,
            score=score,
            violations=violations,
            warnings=warnings,
            patterns=patterns,
            recommendations=recommendations
        )
    
    def _detect_connector_overuse(self, texts: List[str]) -> Dict:
        """Detect overused connectors and transitions."""
        total_texts = len(texts)
        connector_counts = Counter()
        
        for text in texts:
            text_lower = text.lower()
            # Check each sentence for connectors
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
            
            for sentence in sentences:
                words = sentence.split()
                if words:
                    first_word = words[0].lower().strip(',;:')
                    if first_word in self.AI_CONNECTORS:
                        connector_counts[first_word] += 1
        
        violations = []
        warnings = []
        
        for connector, count in connector_counts.items():
            pct = (count / total_texts) * 100
            threshold = self.THRESHOLDS['connector_max_pct']
            
            if pct > threshold:
                violations.append(
                    f"Connector '{connector}' overused: {count}/{total_texts} ({pct:.0f}%, max {threshold}%)"
                )
            elif pct > threshold * 0.8:
                warnings.append(
                    f"Connector '{connector}' frequently used: {count}/{total_texts} ({pct:.0f}%)"
                )
        
        return {
            'counts': dict(connector_counts),
            'violations': violations,
            'warnings': warnings
        }
    
    def _detect_word_count_uniformity(self, texts: List[str]) -> Dict:
        """Detect overly uniform word counts."""
        word_counts = [len(text.split()) for text in texts]
        
        mean_wc = statistics.mean(word_counts)
        stdev_wc = statistics.stdev(word_counts) if len(word_counts) > 1 else 0
        cv = (stdev_wc / mean_wc * 100) if mean_wc > 0 else 0
        wc_range = max(word_counts) - min(word_counts)
        
        return {
            'mean': mean_wc,
            'stdev': stdev_wc,
            'cv': cv,
            'range': wc_range,
            'min': min(word_counts),
            'max': max(word_counts),
            'distribution': word_counts
        }
    
    def _detect_ngram_repetition(self, texts: List[str]) -> Dict:
        """Detect repeated n-grams (bigrams, trigrams)."""
        all_bigrams = []
        all_trigrams = []
        
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Bigrams
            bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
            all_bigrams.extend(bigrams)
            
            # Trigrams
            trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
            all_trigrams.extend(trigrams)
        
        bigram_counts = Counter(all_bigrams)
        trigram_counts = Counter(all_trigrams)
        
        violations = []
        warnings = []
        
        # Check bigrams
        for bigram, count in bigram_counts.most_common(10):
            pct = (count / len(texts)) * 100
            if pct > self.THRESHOLDS['bigram_max_pct']:
                violations.append(
                    f"Bigram '{bigram}' repeated: {count} times ({pct:.0f}%)"
                )
        
        # Check trigrams
        for trigram, count in trigram_counts.most_common(10):
            pct = (count / len(texts)) * 100
            if pct > self.THRESHOLDS['trigram_max_pct']:
                violations.append(
                    f"Trigram '{trigram}' repeated: {count} times ({pct:.0f}%)"
                )
        
        return {
            'bigrams': dict(bigram_counts.most_common(5)),
            'trigrams': dict(trigram_counts.most_common(5)),
            'violations': violations,
            'warnings': warnings
        }
    
    def _detect_structure_patterns(self, texts: List[str]) -> Dict:
        """Detect repetitive sentence structures."""
        structures = []
        
        for text in texts:
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
            
            # Analyze structure of each sentence
            for sentence in sentences:
                # Extract structure: [WORD_TYPE word_count comma_count]
                words = sentence.split()
                comma_count = sentence.count(',')
                
                # First word type
                first_word = words[0].lower() if words else ''
                if first_word in ['the', 'a', 'an']:
                    first_type = 'ARTICLE'
                elif first_word in ['this', 'that', 'these', 'those']:
                    first_type = 'DEMONSTRATIVE'
                elif first_word in self.AI_CONNECTORS:
                    first_type = 'CONNECTOR'
                elif first_word.endswith('ing'):
                    first_type = 'GERUND'
                elif first_word in ['yes', 'no']:
                    first_type = 'ANSWER'
                else:
                    first_type = 'OTHER'
                
                # Create structure signature
                structure = f"{first_type}_{len(words)//5}_commas{comma_count}"
                structures.append(structure)
        
        # Calculate diversity
        unique_structures = len(set(structures))
        total_structures = len(structures)
        diversity = unique_structures / total_structures if total_structures > 0 else 0
        
        structure_counts = Counter(structures)
        
        return {
            'diversity': diversity,
            'unique_count': unique_structures,
            'total_count': total_structures,
            'distribution': dict(structure_counts.most_common(5))
        }
    
    def _detect_formulaic_patterns(self, texts: List[str]) -> Dict:
        """Detect formulaic patterns using regex."""
        matches = Counter()
        
        for text in texts:
            for pattern in self.FORMULAIC_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    matches[pattern] += 1
        
        return {
            'matches': dict(matches),
            'total_matches': sum(matches.values())
        }
    
    def _analyze_sentence_starters(self, texts: List[str]) -> Dict:
        """Analyze sentence starter diversity."""
        first_words = []
        first_two_words = []
        
        for text in texts:
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
            
            for sentence in sentences:
                words = sentence.split()
                if words:
                    first_words.append(words[0].lower())
                    if len(words) >= 2:
                        first_two_words.append(f"{words[0]} {words[1]}".lower())
        
        first_word_counts = Counter(first_words)
        first_two_counts = Counter(first_two_words)
        
        violations = []
        threshold = self.THRESHOLDS['sentence_start_max_pct']
        
        for word, count in first_word_counts.most_common(3):
            pct = (count / len(first_words)) * 100 if first_words else 0
            if pct > threshold:
                violations.append(
                    f"Sentence starter '{word}' overused: {pct:.0f}% (max {threshold}%)"
                )
        
        return {
            'first_words': dict(first_word_counts.most_common(5)),
            'first_two_words': dict(first_two_counts.most_common(5)),
            'violations': violations
        }
    
    def _detect_parallel_structures(self, texts: List[str]) -> Dict:
        """Detect parallel syntactic structures."""
        sentence_patterns = []
        
        for text in texts:
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
            
            for sentence in sentences:
                # Extract pattern: length, commas, question/statement
                length_bucket = len(sentence) // 20  # Group by 20-char buckets
                comma_count = sentence.count(',')
                is_question = sentence.strip().endswith('?')
                
                pattern = f"L{length_bucket}_C{comma_count}_{'Q' if is_question else 'S'}"
                sentence_patterns.append(pattern)
        
        # Calculate variation score
        pattern_counts = Counter(sentence_patterns)
        most_common_pct = (pattern_counts.most_common(1)[0][1] / len(sentence_patterns) 
                          if sentence_patterns else 0)
        
        variation_score = 1 - most_common_pct
        
        return {
            'score': variation_score,
            'patterns': dict(pattern_counts.most_common(3))
        }
    
    def _generate_recommendations(self, patterns: Dict, violations: List[str], 
                                 warnings: List[str]) -> List[str]:
        """Generate actionable recommendations based on findings."""
        recommendations = []
        
        # Connector recommendations
        if patterns.get('connectors', {}).get('violations'):
            top_connector = max(
                patterns['connectors']['counts'].items(),
                key=lambda x: x[1]
            )[0]
            recommendations.append(
                f"Reduce '{top_connector}' usage. Try alternatives: 'Additionally', "
                "'Furthermore', 'For example', 'In contrast', 'Specifically'"
            )
        
        # Word count recommendations
        if patterns.get('uniformity', {}).get('cv', 100) < 10:
            recommendations.append(
                "Vary answer lengths: Mix short (20-25w), medium (30-40w), "
                "and longer (45-50w) responses"
            )
        
        # Structure recommendations
        if patterns.get('structures', {}).get('diversity', 1) < 0.6:
            recommendations.append(
                "Vary sentence structures: Mix simple, compound, and complex sentences. "
                "Start with different word types (verbs, nouns, connectors)"
            )
        
        # Formula recommendations
        if patterns.get('formulas', {}).get('total_matches', 0) > 0:
            recommendations.append(
                "Avoid formulaic patterns like '[Action] + This [benefit]'. "
                "Use natural, spontaneous writing"
            )
        
        # Ngram recommendations
        if patterns.get('ngrams', {}).get('violations'):
            recommendations.append(
                "Reduce phrase repetition. Use synonyms and vary phrasing naturally"
            )
        
        return recommendations


def validate_duplication(items: List[Dict], component_type: str = 'faq',
                        strict_mode: bool = True) -> DuplicationAnalysis:
    """
    Convenience function for duplication validation.
    
    Args:
        items: Content items to validate
        component_type: Type of component
        strict_mode: Use strict thresholds
        
    Returns:
        DuplicationAnalysis with results
    """
    detector = DuplicationDetector(strict_mode=strict_mode)
    return detector.analyze(items, component_type)
