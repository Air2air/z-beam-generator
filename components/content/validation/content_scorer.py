#!/usr/bin/env python3
"""
Content Quality Scoring System
Provides comprehensive scoring for content component generation to ensure
100% believable human-generated content with detailed human readability metrics.
"""

import re
import math
import statistics
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentScore:
    """Comprehensive content quality score"""
    overall_score: float  # 0-100 overall quality score
    human_believability: float  # 0-100 human-like believability
    technical_accuracy: float  # 0-100 technical content accuracy
    author_authenticity: float  # 0-100 author persona authenticity
    readability_score: float  # 0-100 readability score
    formatting_quality: float  # 0-100 markdown formatting quality
    
    # Detailed metrics
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_sentence_length: float
    vocabulary_diversity: float
    technical_density: float
    
    # Validation flags
    has_required_elements: bool
    passes_human_threshold: bool
    retry_recommended: bool
    
    # Detailed breakdown
    scoring_breakdown: Dict[str, Any]

class ContentQualityScorer:
    """
    Advanced content quality scoring system that evaluates generated content
    against human believability, technical accuracy, and readability standards.
    """
    
    def __init__(self, human_threshold: float = 75.0):
        """
        Initialize the content scorer.
        
        Args:
            human_threshold: Minimum score required to pass human believability test
        """
        self.human_threshold = human_threshold
        
        # Technical terms for laser cleaning domain
        self.technical_terms = {
            'laser', 'cleaning', 'surface', 'material', 'wavelength', 'pulse', 
            'energy', 'density', 'contamination', 'oxide', 'coating', 'ablation',
            'thermal', 'optical', 'processing', 'parameters', 'optimization',
            'efficiency', 'precision', 'quality', 'analysis', 'systematic'
        }
        
        # Author-specific linguistic markers
        self.author_markers = {
            'taiwan': ['systematic', 'comprehensive', 'demonstrates', 'analysis', 'methodology'],
            'italy': ['precision', 'excellence', 'sophisticated', 'engineering', 'innovation'],
            'indonesia': ['practical', 'sustainable', 'efficient', 'application', 'implementation'],
            'usa': ['advanced', 'cutting-edge', 'innovative', 'technology', 'optimization']
        }
    
    def score_content(self, content: str, material_data: Dict[str, Any], 
                     author_info: Dict[str, Any], frontmatter_data: Optional[Dict] = None) -> ContentScore:
        """
        Generate comprehensive quality score for content.
        
        Args:
            content: Generated content to score
            material_data: Material information used in generation
            author_info: Author persona information
            frontmatter_data: Optional frontmatter context
            
        Returns:
            ContentScore with detailed quality metrics
        """
        try:
            # Calculate individual scoring components
            formatting_score = self._score_formatting(content)
            technical_score = self._score_technical_accuracy(content, material_data, frontmatter_data)
            authenticity_score = self._score_author_authenticity(content, author_info)
            readability_score = self._score_readability(content)
            believability_score = self._score_human_believability(content, author_info)
            
            # Calculate content metrics
            metrics = self._calculate_content_metrics(content)
            
            # Check required elements
            required_elements = self._check_required_elements(content, material_data, author_info)
            
            # Calculate overall score (weighted average)
            overall_score = self._calculate_overall_score(
                formatting_score, technical_score, authenticity_score, 
                readability_score, believability_score, required_elements
            )
            
            # Determine if retry is recommended
            passes_threshold = believability_score >= self.human_threshold
            retry_recommended = not passes_threshold or overall_score < 70.0
            
            # Create detailed breakdown
            breakdown = {
                'formatting': {
                    'score': formatting_score,
                    'details': self._get_formatting_details(content)
                },
                'technical_accuracy': {
                    'score': technical_score,
                    'details': self._get_technical_details(content, material_data)
                },
                'author_authenticity': {
                    'score': authenticity_score,
                    'details': self._get_authenticity_details(content, author_info)
                },
                'readability': {
                    'score': readability_score,
                    'details': self._get_readability_details(content)
                },
                'human_believability': {
                    'score': believability_score,
                    'details': self._get_believability_details(content)
                }
            }
            
            return ContentScore(
                overall_score=overall_score,
                human_believability=believability_score,
                technical_accuracy=technical_score,
                author_authenticity=authenticity_score,
                readability_score=readability_score,
                formatting_quality=formatting_score,
                word_count=metrics['word_count'],
                sentence_count=metrics['sentence_count'],
                paragraph_count=metrics['paragraph_count'],
                avg_sentence_length=metrics['avg_sentence_length'],
                vocabulary_diversity=metrics['vocabulary_diversity'],
                technical_density=metrics['technical_density'],
                has_required_elements=required_elements['all_present'],
                passes_human_threshold=passes_threshold,
                retry_recommended=retry_recommended,
                scoring_breakdown=breakdown
            )
            
        except Exception as e:
            logger.error(f"Error scoring content: {e}")
            # Return minimal failing score
            return ContentScore(
                overall_score=0.0, human_believability=0.0, technical_accuracy=0.0,
                author_authenticity=0.0, readability_score=0.0, formatting_quality=0.0,
                word_count=0, sentence_count=0, paragraph_count=0,
                avg_sentence_length=0.0, vocabulary_diversity=0.0, technical_density=0.0,
                has_required_elements=False, passes_human_threshold=False,
                retry_recommended=True, scoring_breakdown={'error': str(e)}
            )
    
    def _score_formatting(self, content: str) -> float:
        """Score markdown formatting quality (0-100)."""
        score = 0.0
        max_score = 100.0
        
        # Check for title (20 points)
        if content.startswith('# '):
            score += 20
        
        # Check for section headers (20 points)
        if '## ' in content:
            score += 20
        
        # Check for bold text (15 points)
        if '**' in content:
            score += 15
        
        # Check for proper paragraph structure (15 points)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 15
        
        # Check for byline/author attribution (15 points)
        if re.search(r'\*\*.*Ph\.D.*\*\*', content):
            score += 15
        
        # Check for lists or structured content (15 points)
        if re.search(r'[•\-\*]\s+|^\d+\.\s+', content, re.MULTILINE):
            score += 15
        
        return min(score, max_score)
    
    def _score_technical_accuracy(self, content: str, material_data: Dict[str, Any], 
                                 frontmatter_data: Optional[Dict] = None) -> float:
        """Score technical content accuracy (0-100)."""
        score = 0.0
        max_score = 100.0
        
        content_lower = content.lower()
        
        # Check for material formula integration (25 points)
        formula = material_data.get('formula', material_data.get('chemical_formula', ''))
        if formula and formula in content:
            score += 25
        
        # Check for technical terminology (25 points)
        technical_terms_found = sum(1 for term in self.technical_terms if term in content_lower)
        technical_ratio = min(technical_terms_found / 10, 1.0)  # Up to 10 terms for full score
        score += technical_ratio * 25
        
        # Check for specific technical details (25 points)
        technical_details = [
            'wavelength', 'pulse', 'energy', 'density', 'parameters',
            'optimization', 'surface', 'material', 'laser', 'cleaning'
        ]
        details_found = sum(1 for detail in technical_details if detail in content_lower)
        details_ratio = min(details_found / 6, 1.0)  # Up to 6 details for full score
        score += details_ratio * 25
        
        # Check for frontmatter integration (25 points)
        if frontmatter_data:
            frontmatter_elements = 0
            
            # Check for properties integration
            properties = frontmatter_data.get('properties', {})
            for prop_value in properties.values():
                if str(prop_value).lower() in content_lower:
                    frontmatter_elements += 1
            
            # Check for laser parameters integration
            laser_params = frontmatter_data.get('laser_cleaning', {})
            for param_value in laser_params.values():
                if str(param_value) in content:
                    frontmatter_elements += 1
            
            # Check for applications integration
            applications = frontmatter_data.get('applications', [])
            for app in applications:
                if app.lower() in content_lower:
                    frontmatter_elements += 1
            
            frontmatter_ratio = min(frontmatter_elements / 5, 1.0)
            score += frontmatter_ratio * 25
        
        return min(score, max_score)
    
    def _score_author_authenticity(self, content: str, author_info: Dict[str, Any]) -> float:
        """Score author persona authenticity (0-100)."""
        score = 0.0
        max_score = 100.0
        
        content_lower = content.lower()
        author_country = author_info.get('country', '').lower()
        
        # Map country to marker key
        country_mapping = {
            'taiwan': 'taiwan',
            'italy': 'italy', 
            'indonesia': 'indonesia',
            'united states': 'usa',
            'united states (california)': 'usa'
        }
        
        marker_key = country_mapping.get(author_country, 'usa')
        expected_markers = self.author_markers.get(marker_key, [])
        
        # Check for author-specific linguistic markers (40 points)
        markers_found = sum(1 for marker in expected_markers if marker in content_lower)
        if expected_markers:
            marker_ratio = markers_found / len(expected_markers)
            score += marker_ratio * 40
        
        # Check for author name attribution (30 points)
        author_name = author_info.get('name', '')
        if author_name and author_name in content:
            score += 30
        
        # Check for country attribution (30 points)
        country_display = author_info.get('country', '')
        if country_display and country_display in content:
            score += 30
        
        return min(score, max_score)
    
    def _score_readability(self, content: str) -> float:
        """Score content readability using multiple metrics (0-100)."""
        try:
            # Calculate readability metrics
            sentences = self._split_sentences(content)
            words = self._extract_words(content)
            
            if not sentences or not words:
                return 0.0
            
            # Average sentence length (optimal: 15-25 words)
            avg_sentence_length = len(words) / len(sentences)
            sentence_score = self._score_sentence_length(avg_sentence_length)
            
            # Vocabulary diversity (unique words / total words)
            unique_words = set(word.lower() for word in words)
            diversity = len(unique_words) / len(words) if words else 0
            diversity_score = min(diversity * 150, 100)  # Scale to 0-100
            
            # Paragraph structure (optimal: 3-6 paragraphs)
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            paragraph_score = self._score_paragraph_count(len(paragraphs))
            
            # Technical complexity balance
            complexity_score = self._score_technical_complexity(content)
            
            # Weighted average
            readability_score = (
                sentence_score * 0.3 +
                diversity_score * 0.3 +
                paragraph_score * 0.2 +
                complexity_score * 0.2
            )
            
            return min(readability_score, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating readability: {e}")
            return 50.0  # Default middle score on error
    
    def _score_human_believability(self, content: str, author_info: Dict[str, Any]) -> float:
        """Score overall human believability (0-100)."""
        score = 0.0
        
        # Natural language flow (25 points)
        flow_score = self._score_language_flow(content)
        score += flow_score * 0.25
        
        # Coherent structure (25 points)
        structure_score = self._score_content_structure(content)
        score += structure_score * 0.25
        
        # Appropriate complexity (25 points)
        complexity_score = self._score_appropriate_complexity(content)
        score += complexity_score * 0.25
        
        # Human-like variability (25 points)
        variability_score = self._score_human_variability(content)
        score += variability_score * 0.25
        
        return min(score, 100.0)
    
    def _calculate_content_metrics(self, content: str) -> Dict[str, float]:
        """Calculate detailed content metrics."""
        sentences = self._split_sentences(content)
        words = self._extract_words(content)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)
        
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Vocabulary diversity
        unique_words = set(word.lower() for word in words)
        vocabulary_diversity = len(unique_words) / word_count if word_count > 0 else 0
        
        # Technical density
        technical_words = sum(1 for word in words if word.lower() in self.technical_terms)
        technical_density = technical_words / word_count if word_count > 0 else 0
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'avg_sentence_length': avg_sentence_length,
            'vocabulary_diversity': vocabulary_diversity,
            'technical_density': technical_density
        }
    
    def _check_required_elements(self, content: str, material_data: Dict[str, Any], 
                                author_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check for required content elements."""
        elements = {
            'has_title': content.startswith('#'),
            'has_author': author_info.get('name', '') in content,
            'has_material': material_data.get('name', '') in content,
            'has_formula': any(formula in content for formula in [
                material_data.get('formula', ''),
                material_data.get('chemical_formula', '')
            ] if formula),
            'has_technical_content': any(term in content.lower() for term in self.technical_terms),
            'has_sections': '##' in content
        }
        
        elements['all_present'] = all(elements.values())
        elements['present_count'] = sum(elements.values())
        elements['total_count'] = len([k for k in elements.keys() if k not in ['all_present', 'present_count', 'total_count']])
        
        return elements
    
    def _calculate_overall_score(self, formatting: float, technical: float, 
                               authenticity: float, readability: float, 
                               believability: float, required_elements: Dict) -> float:
        """Calculate weighted overall score."""
        # Base weighted score
        base_score = (
            believability * 0.30 +      # Most important: human believability
            technical * 0.25 +          # Technical accuracy
            authenticity * 0.20 +       # Author authenticity
            readability * 0.15 +        # Readability
            formatting * 0.10           # Formatting
        )
        
        # Penalty for missing required elements
        required_ratio = required_elements.get('present_count', 0) / required_elements.get('total_count', 1)
        element_penalty = (1 - required_ratio) * 20  # Up to 20 point penalty
        
        overall_score = max(base_score - element_penalty, 0.0)
        return min(overall_score, 100.0)
    
    # Helper methods for detailed scoring
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on periods, exclamation marks, question marks
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text."""
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z0-9]+\b', text)
        return words
    
    def _score_sentence_length(self, avg_length: float) -> float:
        """Score average sentence length (optimal: 15-25 words)."""
        if 15 <= avg_length <= 25:
            return 100.0
        elif 10 <= avg_length < 15 or 25 < avg_length <= 30:
            return 80.0
        elif 5 <= avg_length < 10 or 30 < avg_length <= 35:
            return 60.0
        else:
            return 40.0
    
    def _score_paragraph_count(self, count: int) -> float:
        """Score paragraph count (optimal: 3-6 paragraphs)."""
        if 3 <= count <= 6:
            return 100.0
        elif count == 2 or count == 7:
            return 80.0
        elif count == 1 or count == 8:
            return 60.0
        else:
            return 40.0
    
    def _score_technical_complexity(self, content: str) -> float:
        """Score appropriate technical complexity."""
        content_lower = content.lower()
        
        # Count technical terms
        tech_terms = sum(1 for term in self.technical_terms if term in content_lower)
        
        # Count total words
        words = len(self._extract_words(content))
        
        if words == 0:
            return 0.0
        
        # Calculate technical density (optimal: 5-15%)
        tech_density = tech_terms / words
        
        if 0.05 <= tech_density <= 0.15:
            return 100.0
        elif 0.03 <= tech_density < 0.05 or 0.15 < tech_density <= 0.20:
            return 80.0
        else:
            return 60.0
    
    def _score_language_flow(self, content: str) -> float:
        """Score natural language flow."""
        # Check for transition words and phrases
        transitions = [
            'however', 'therefore', 'furthermore', 'additionally', 'consequently',
            'moreover', 'nevertheless', 'meanwhile', 'specifically', 'particularly'
        ]
        
        content_lower = content.lower()
        transition_count = sum(1 for trans in transitions if trans in content_lower)
        
        # Score based on presence of transitions
        if transition_count >= 3:
            return 100.0
        elif transition_count >= 2:
            return 80.0
        elif transition_count >= 1:
            return 60.0
        else:
            return 40.0
    
    def _score_content_structure(self, content: str) -> float:
        """Score logical content structure."""
        score = 0.0
        
        # Check for title (25 points)
        if content.startswith('#'):
            score += 25
        
        # Check for author byline (25 points)
        if re.search(r'\*\*.*Ph\.D.*\*\*', content):
            score += 25
        
        # Check for section headers (25 points)
        if '##' in content:
            score += 25
        
        # Check for logical flow (introduction -> details -> conclusion) (25 points)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 25
        
        return score
    
    def _score_appropriate_complexity(self, content: str) -> float:
        """Score appropriate complexity for technical content."""
        words = self._extract_words(content)
        
        if not words:
            return 0.0
        
        # Calculate average word length (complexity indicator)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Technical content should have moderate complexity (5-7 chars avg)
        if 5 <= avg_word_length <= 7:
            return 100.0
        elif 4 <= avg_word_length < 5 or 7 < avg_word_length <= 8:
            return 80.0
        else:
            return 60.0
    
    def _score_human_variability(self, content: str) -> float:
        """Score human-like variability in writing."""
        sentences = self._split_sentences(content)
        
        if len(sentences) < 3:
            return 50.0
        
        # Calculate sentence length variability
        sentence_lengths = [len(self._extract_words(sentence)) for sentence in sentences]
        
        if len(sentence_lengths) < 2:
            return 50.0
        
        # Higher standard deviation indicates more variability (human-like)
        std_dev = statistics.stdev(sentence_lengths)
        mean_length = statistics.mean(sentence_lengths)
        
        # Coefficient of variation (std_dev / mean)
        if mean_length > 0:
            cv = std_dev / mean_length
            # Good variability: 0.3-0.7
            if 0.3 <= cv <= 0.7:
                return 100.0
            elif 0.2 <= cv < 0.3 or 0.7 < cv <= 0.8:
                return 80.0
            else:
                return 60.0
        
        return 50.0
    
    # Detail methods for breakdown reporting
    def _get_formatting_details(self, content: str) -> Dict[str, Any]:
        """Get detailed formatting analysis."""
        return {
            'has_title': content.startswith('#'),
            'has_sections': '##' in content,
            'has_bold_text': '**' in content,
            'has_author_byline': bool(re.search(r'\*\*.*Ph\.D.*\*\*', content)),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'has_lists': bool(re.search(r'[•\-\*]\s+|^\d+\.\s+', content, re.MULTILINE))
        }
    
    def _get_technical_details(self, content: str, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed technical analysis."""
        content_lower = content.lower()
        technical_terms_found = [term for term in self.technical_terms if term in content_lower]
        
        return {
            'formula_present': any(formula in content for formula in [
                material_data.get('formula', ''),
                material_data.get('chemical_formula', '')
            ] if formula),
            'technical_terms_found': technical_terms_found,
            'technical_term_count': len(technical_terms_found),
            'technical_density': len(technical_terms_found) / len(self._extract_words(content)) if self._extract_words(content) else 0
        }
    
    def _get_authenticity_details(self, content: str, author_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed authenticity analysis."""
        content_lower = content.lower()
        author_country = author_info.get('country', '').lower()
        
        country_mapping = {
            'taiwan': 'taiwan',
            'italy': 'italy', 
            'indonesia': 'indonesia',
            'united states': 'usa',
            'united states (california)': 'usa'
        }
        
        marker_key = country_mapping.get(author_country, 'usa')
        expected_markers = self.author_markers.get(marker_key, [])
        found_markers = [marker for marker in expected_markers if marker in content_lower]
        
        return {
            'author_name_present': author_info.get('name', '') in content,
            'country_present': author_info.get('country', '') in content,
            'expected_linguistic_markers': expected_markers,
            'found_linguistic_markers': found_markers,
            'marker_match_ratio': len(found_markers) / len(expected_markers) if expected_markers else 0
        }
    
    def _get_readability_details(self, content: str) -> Dict[str, Any]:
        """Get detailed readability analysis."""
        sentences = self._split_sentences(content)
        words = self._extract_words(content)
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'vocabulary_diversity': len(set(word.lower() for word in words)) / len(words) if words else 0,
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }
    
    def _get_believability_details(self, content: str) -> Dict[str, Any]:
        """Get detailed believability analysis."""
        return {
            'has_natural_flow': self._score_language_flow(content) >= 80,
            'has_logical_structure': self._score_content_structure(content) >= 80,
            'appropriate_complexity': self._score_appropriate_complexity(content) >= 80,
            'human_variability': self._score_human_variability(content) >= 80,
            'transition_words_present': any(trans in content.lower() for trans in [
                'however', 'therefore', 'furthermore', 'additionally', 'consequently'
            ])
        }


def create_content_scorer(human_threshold: float = 75.0) -> ContentQualityScorer:
    """
    Create a content quality scorer instance.
    
    Args:
        human_threshold: Minimum score required to pass human believability test
        
    Returns:
        Configured ContentQualityScorer instance
    """
    return ContentQualityScorer(human_threshold=human_threshold)
