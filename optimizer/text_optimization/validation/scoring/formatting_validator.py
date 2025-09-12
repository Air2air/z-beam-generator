"""
Content Formatting Validator

Validates content structure, formatting, and presentation quality
for professional content standards.
"""

import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)


class FormattingValidator:
    """Validates content formatting and structure."""

    def __init__(self):
        """Initialize the formatting validator."""
        self.formatting_patterns = {
            "title": r"^#\s+",
            "section": r"^##\s+",
            "subsection": r"^###\s+",
            "bold": r"\*\*[^*]+\*\*",
            "italic": r"\*[^*]+\*",
            "list_item": r"^[\*\-\+]\s+",
            "numbered_list": r"^\d+\.\s+",
            "bullet_point": r"^•\s+",
        }

    def score_formatting(self, content: str) -> float:
        """
        Score content formatting quality (0-100).
        
        Args:
            content: Content to evaluate
            
        Returns:
            Formatting score from 0-100
        """
        score = 0.0

        # Title presence (20 points)
        if self._has_title(content):
            score += 20

        # Section structure (30 points)
        if self._has_sections(content):
            score += 30

        # Text emphasis formatting (25 points)
        if self._has_text_emphasis(content):
            score += 25

        # List formatting (25 points)
        if self._has_lists(content):
            score += 25

        return min(score, 100.0)

    def _has_title(self, content: str) -> bool:
        """Check if content has a properly formatted title."""
        return bool(re.search(self.formatting_patterns["title"], content, re.MULTILINE))

    def _has_sections(self, content: str) -> bool:
        """Check if content has section headers."""
        return bool(re.search(self.formatting_patterns["section"], content, re.MULTILINE))

    def _has_text_emphasis(self, content: str) -> bool:
        """Check if content uses text emphasis (bold/italic)."""
        has_bold = bool(re.search(self.formatting_patterns["bold"], content))
        has_italic = bool(re.search(self.formatting_patterns["italic"], content))
        return has_bold or has_italic

    def _has_lists(self, content: str) -> bool:
        """Check if content has formatted lists."""
        has_bullet = bool(re.search(self.formatting_patterns["list_item"], content, re.MULTILINE))
        has_numbered = bool(re.search(self.formatting_patterns["numbered_list"], content, re.MULTILINE))
        has_unicode_bullet = bool(re.search(self.formatting_patterns["bullet_point"], content, re.MULTILINE))
        
        return has_bullet or has_numbered or has_unicode_bullet

    def analyze_structure(self, content: str) -> Dict[str, any]:
        """
        Analyze content structure in detail.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with structural analysis
        """
        lines = content.split('\n')
        
        structure_analysis = {
            "total_lines": len(lines),
            "title_count": len(re.findall(self.formatting_patterns["title"], content, re.MULTILINE)),
            "section_count": len(re.findall(self.formatting_patterns["section"], content, re.MULTILINE)),
            "subsection_count": len(re.findall(self.formatting_patterns["subsection"], content, re.MULTILINE)),
            "bold_count": len(re.findall(self.formatting_patterns["bold"], content)),
            "italic_count": len(re.findall(self.formatting_patterns["italic"], content)),
            "list_item_count": len(re.findall(self.formatting_patterns["list_item"], content, re.MULTILINE)),
            "numbered_list_count": len(re.findall(self.formatting_patterns["numbered_list"], content, re.MULTILINE)),
            "bullet_point_count": len(re.findall(self.formatting_patterns["bullet_point"], content, re.MULTILINE)),
            "paragraph_count": self._count_paragraphs(content),
            "average_paragraph_length": self._calculate_avg_paragraph_length(content),
        }

        return structure_analysis

    def _count_paragraphs(self, content: str) -> int:
        """Count the number of paragraphs in content."""
        # Split by double newlines to identify paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return len(paragraphs)

    def _calculate_avg_paragraph_length(self, content: str) -> float:
        """Calculate average paragraph length in words."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return 0.0
        
        total_words = sum(len(p.split()) for p in paragraphs)
        return total_words / len(paragraphs)

    def validate_professional_standards(self, content: str) -> Dict[str, bool]:
        """
        Validate content against professional formatting standards.
        
        Args:
            content: Content to validate
            
        Returns:
            Dictionary of validation results
        """
        return {
            "has_proper_title": self._has_title(content),
            "has_logical_structure": self._has_sections(content),
            "uses_emphasis": self._has_text_emphasis(content),
            "includes_lists": self._has_lists(content),
            "appropriate_length": len(content.split()) >= 100,
            "not_too_long": len(content.split()) <= 2000,
            "has_paragraphs": self._count_paragraphs(content) >= 2,
            "reasonable_line_length": self._check_line_lengths(content),
        }

    def _check_line_lengths(self, content: str) -> bool:
        """Check if line lengths are reasonable."""
        lines = content.split('\n')
        long_lines = [line for line in lines if len(line) > 120]
        
        # Allow some long lines, but not too many
        return len(long_lines) / len(lines) < 0.2 if lines else True

    def get_formatting_suggestions(self, content: str) -> list[str]:
        """
        Get suggestions for improving content formatting.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of formatting improvement suggestions
        """
        suggestions = []
        
        if not self._has_title(content):
            suggestions.append("Add a clear title using # at the beginning")
        
        if not self._has_sections(content):
            suggestions.append("Break content into sections using ## headers")
        
        if not self._has_text_emphasis(content):
            suggestions.append("Use **bold** or *italic* text for emphasis")
        
        if not self._has_lists(content):
            suggestions.append("Use bullet points or numbered lists where appropriate")
        
        if len(content.split()) < 100:
            suggestions.append("Content may be too short - consider adding more detail")
        
        if len(content.split()) > 2000:
            suggestions.append("Content may be too long - consider breaking into sections")
        
        if self._count_paragraphs(content) < 2:
            suggestions.append("Break content into multiple paragraphs for better readability")
        
        return suggestions
