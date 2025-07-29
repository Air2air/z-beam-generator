"""
Module for detecting numerical data in frontmatter fields.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class NumericalFieldDetector:
    """Detects and scores frontmatter fields based on their likelihood of containing numerical data."""

    def __init__(self):
        # Field names that commonly contain numerical data
        self.numerical_keywords = [
            'specification', 'spec', 'range', 'parameter', 'measurement', 'metric',
            'dimension', 'size', 'rate', 'duration', 'power', 'temperature',
            'percentage', 'ratio', 'efficiency', 'performance', 'technical',
            'composition', 'outcome', 'result', 'impact'
        ]
        
        # Field names that typically don't contain numerical data
        self.text_keywords = [
            'title', 'name', 'description', 'author', 'website', 'tag', 'keyword',
            'introduction', 'conclusion', 'summary', 'overview', 'background'
        ]
        
        # Regex patterns for detecting numerical ranges
        self.range_patterns = [
            r'\d+\s*[-–—]\s*\d+',  # e.g., "50-500"
            r'\d+\s*to\s*\d+',     # e.g., "50 to 500"
            r'\d+\s*±\s*\d+'       # e.g., "50 ± 5"
        ]

    def identify_numerical_fields(self, frontmatter_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze frontmatter to identify fields likely to contain numerical data.
        
        Args:
            frontmatter_data: The complete frontmatter dictionary
            
        Returns:
            Dict[str, float]: Dictionary mapping field names to numerical relevance scores
        """
        scores = {}
        
        # Analyze each top-level key in the frontmatter
        for key, value in frontmatter_data.items():
            score = self._score_field(key, value)
            
            # Only include fields with positive scores
            if score > 0:
                scores[key] = score
        
        # Log the results
        logger.info(f"Numerical field detection scores: {scores}")
        return scores
    
    def _score_field(self, key: str, value: Any) -> float:
        """
        Calculate a numerical relevance score for a specific field.
        
        Args:
            key: The field name
            value: The field value
            
        Returns:
            float: The numerical relevance score (higher = more likely to contain numerical data)
        """
        score = 0
        
        # 1. Name-based scoring
        score += self._score_by_name(key)
        
        # 2. Structure-based scoring
        score += self._score_by_structure(value)
        
        # 3. Content-based scoring
        score += self._score_by_content(value)
        
        return max(0, score)  # Ensure score is non-negative
    
    def _score_by_name(self, key: str) -> float:
        """Score based on field name."""
        score = 0
        key_lower = key.lower()
        
        # Check if key name suggests numerical content
        for word in self.numerical_keywords:
            if word in key_lower:
                score += 1
                
        # Reduce score if key name suggests textual content
        for word in self.text_keywords:
            if word in key_lower:
                score -= 0.5
                
        return score
    
    def _score_by_structure(self, value: Any) -> float:
        """Score based on data structure."""
        score = 0
        
        # Dictionary structures often contain parameters with values
        if isinstance(value, dict):
            score += 0.5
            
        # Lists of dictionaries often represent tabular data
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            score += 0.5
            
            # Check for percentage or numerical fields
            sample_item = value[0]
            
            if any(field in sample_item for field in ['percentage', 'percent', 'ratio']):
                score += 1.5
                
            if any(field in sample_item for field in ['value', 'measurement', 'result', 'metric']):
                score += 1.5
                
        return score
    
    def _score_by_content(self, value: Any) -> float:
        """Score based on content patterns."""
        score = 0
        
        # Check dictionary values for numerical patterns
        if isinstance(value, dict):
            for subkey, subvalue in list(value.items())[:5]:  # Check first 5 items
                if isinstance(subvalue, str) and self._contains_numerical_pattern(subvalue):
                    score += 2
                    break
        
        # Check for numerical patterns in string values
        elif isinstance(value, str) and self._contains_numerical_pattern(value):
            score += 1
            
        # Check list items for numerical patterns
        elif isinstance(value, list) and value:
            # Sample the list
            sample_size = min(5, len(value))
            sample = value[:sample_size]
            
            # Check each sample item
            for item in sample:
                if isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, str) and self._contains_numerical_pattern(v):
                            score += 1
                            break
                elif isinstance(item, str) and self._contains_numerical_pattern(item):
                    score += 1
                    break
        
        return score
    
    def _contains_numerical_pattern(self, text: str) -> bool:
        """Check if a string contains numerical patterns like ranges or measurements."""
        if not isinstance(text, str):
            return False
            
        # Normalize Unicode dashes
        normalized = text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2015', '-')
        
        # Check for range patterns
        for pattern in self.range_patterns:
            if re.search(pattern, normalized):
                return True
                
        # Check for percentage values
        if re.search(r'\d+\s*%', normalized):
            return True
            
        # Check for dimensional values
        if re.search(r'\d+\s*[a-zA-Z]{1,3}', normalized):  # Like 50W, 10mm, 5kHz
            return True
            
        return False

    def suggest_table_type(self, field_name: str, field_value: Any) -> str:
        """
        Suggest the most appropriate table type for a field.
        
        Args:
            field_name: The name of the field
            field_value: The value of the field
            
        Returns:
            str: Suggested table type ('range', 'percentage', 'metrics', 'standards', or '')
        """
        name_lower = field_name.lower()
        
        # Check if it's a dictionary with range values
        if isinstance(field_value, dict):
            # Sample the dictionary values
            for k, v in list(field_value.items())[:5]:
                if isinstance(v, str) and self._contains_numerical_pattern(v):
                    return 'range'
        
        # Check if it's a list of dictionaries
        elif isinstance(field_value, list) and field_value and isinstance(field_value[0], dict):
            # Try to infer type from field names in the list items
            sample_item = field_value[0]
            
            if any(field in sample_item for field in ['percentage', 'percent', 'composition']):
                return 'percentage'
                
            if any(field in sample_item for field in ['metric', 'result', 'outcome']):
                return 'metrics'
                
            if any(field in sample_item for field in ['code', 'standard', 'regulation']):
                return 'standards'
                
            # Try to infer from the field name
            if 'composition' in name_lower:
                return 'percentage'
                
            if any(word in name_lower for word in ['outcome', 'metric', 'result', 'performance']):
                return 'metrics'
                
            if any(word in name_lower for word in ['standard', 'regulation', 'code', 'compliance']):
                return 'standards'
        
        # Could not determine table type
        return ''