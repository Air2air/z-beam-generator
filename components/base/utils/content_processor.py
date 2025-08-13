"""
Unified content processing utilities for Z-Beam Generator.

Consolidates all content extraction, normalization, and cleaning functionality
previously scattered across multiple modules.
"""

import re
import yaml
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Unified processor for all content extraction, normalization, and cleaning."""
    
    @staticmethod
    def extract_structured_content(content: str, target_format: str = "yaml") -> str:
        """Extract structured content from various AI response formats.
        
        Args:
            content: Raw AI response content
            target_format: Target format (yaml, json)
            
        Returns:
            str: Clean structured content
        """
        content = content.strip()
        
        # Pre-clean malformed AI patterns before extraction
        content = ContentProcessor._preprocess_malformed_ai_content(content)
        
        # Handle code blocks
        extracted = ContentProcessor._extract_from_code_blocks(content, target_format)
        if extracted:
            return extracted
        
        # Handle frontmatter delimiters
        if "---" in content:
            parts = content.split("---", 2)
            if len(parts) >= 2:
                return parts[1].strip()
        
        # Look for structured content after explanatory text
        lines = content.split('\n')
        yaml_start_idx = None
        
        for i, line in enumerate(lines):
            # Find the first line that looks like structured content
            if (re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*:', line.strip()) or 
                re.match(r'^---\s*$', line.strip()) or
                re.match(r'^\s*-\s+[a-zA-Z_]', line.strip())):
                yaml_start_idx = i
                break
        
        if yaml_start_idx is not None:
            yaml_lines = lines[yaml_start_idx:]
            # Remove any trailing explanatory text
            final_lines = []
            for line in yaml_lines:
                if (line.strip().startswith('This YAML') or 
                    line.strip().startswith('The above') or
                    line.strip().startswith('Note:') or
                    re.match(r'^[A-Z].*[.!]$', line.strip())):
                    break
                final_lines.append(line)
            
            return '\n'.join(final_lines).strip()
        
        return content
    
    @staticmethod
    def _extract_from_code_blocks(content: str, target_format: str) -> Optional[str]:
        """Extract content from code blocks."""
        patterns = [
            rf'^```(?:{target_format}|text|json)?\s*\n(.*?)```\s*$',
            rf'^```(?:{target_format}|text|json)?\s*(.*?)```\s*$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, content, re.DOTALL)
            if match:
                extracted = match.group(1).strip()
                if extracted:
                    return extracted
        
        return None
    
    @staticmethod
    def normalize_structured_content(content: str, format_type: str = "yaml") -> str:
        """Normalize structured content for consistency and proper structure.
        
        Args:
            content: Raw structured content string
            format_type: Format type (yaml, json)
            
        Returns:
            str: Normalized content with proper structure
        """
        if format_type == "yaml":
            return ContentProcessor._normalize_yaml_content(content)
        elif format_type == "json":
            return ContentProcessor._normalize_json_content(content)
        else:
            return content
    
    @staticmethod
    def _normalize_yaml_content(content: str) -> str:
        """Normalize YAML content for consistency."""
        # Clean AI-generated markdown artifacts
        content = ContentProcessor._clean_ai_markdown_artifacts(content)
        
        # Fix document structure issues
        content = ContentProcessor._fix_document_structure(content)
        
        # Remove markdown code blocks
        content = re.sub(r'^```ya?ml\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n```\s*$', '', content, flags=re.MULTILINE)
        
        # Fix image URL double dashes
        content = re.sub(r'(/images/[^"]*?)--+([^"]*?\.jpg)', r'\1-\2', content)
        content = re.sub(r'(/images/[^"]*?)-+(\.[a-z]+)', r'\1\2', content)
        
        # Fix malformed YAML sequences
        content = ContentProcessor._fix_malformed_sequences(content)
        
        # Escape YAML values that start with special characters
        content = ContentProcessor._escape_yaml_values(content)
        
        # Parse and re-structure with proper indentation
        try:
            import yaml
            parsed_data = yaml.safe_load(content)
            if parsed_data is None:
                return content
            
            formatted_yaml = ContentProcessor._format_yaml_with_proper_indentation(parsed_data)
            return formatted_yaml.strip()
            
        except yaml.YAMLError as e:
            logger.warning(f"YAML parsing failed: {e}")
            content = ContentProcessor._aggressive_yaml_cleanup(content)
            try:
                parsed_data = yaml.safe_load(content)
                if parsed_data is not None:
                    formatted_yaml = ContentProcessor._format_yaml_with_proper_indentation(parsed_data)
                    return formatted_yaml.strip()
            except yaml.YAMLError:
                pass
            
            return content
    
    @staticmethod
    def _normalize_json_content(content: str) -> str:
        """Normalize JSON content."""
        try:
            # Try to parse and reformat
            parsed = json.loads(content)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            # Try to extract from YAML
            try:
                import yaml
                yaml_data = yaml.safe_load(content)
                if yaml_data:
                    return json.dumps(yaml_data, indent=2)
            except yaml.YAMLError:
                pass
        
        return content
    
    @staticmethod
    def clean_ai_artifacts(content: str) -> str:
        """Remove common AI artifacts and formatting issues.
        
        Args:
            content: Raw AI response content
            
        Returns:
            str: Cleaned content safe for processing
        """
        # Remove markdown bold/italic formatting that breaks structured formats
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        content = re.sub(r'`(.*?)`', r'\1', content)
        
        # Remove problematic formatting in unexpected places
        content = re.sub(r'(?m)^(\s*)-\s*\*\*([^*]+)\*\*:', r'\1\2:', content)
        content = re.sub(r'(?m)^(\s*)\*\*([^*]+)\*\*:', r'\1\2:', content)
        
        # Remove code block markers if present
        content = re.sub(r'^```[a-z]*\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n?```$', '', content, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    @staticmethod
    def _preprocess_malformed_ai_content(content: str) -> str:
        """Preprocess malformed AI content patterns."""
        # Remove introductory text
        content = re.sub(r'^Here\s+is.*?:\s*\n', '', content, flags=re.IGNORECASE)
        content = re.sub(r'^Below\s+is.*?:\s*\n', '', content, flags=re.IGNORECASE)
        content = re.sub(r'^The\s+following.*?:\s*\n', '', content, flags=re.IGNORECASE)
        
        # Fix malformed list items with markdown
        content = re.sub(r'^(\s*-\s+)\*\*([^:]+):\s*["\']?\*\*\s*([^"\']*?)\s*["\']?\s*$', 
                        r'\1\2: \3', content, flags=re.MULTILINE)
        
        # Fix malformed key-value pairs with markdown
        content = re.sub(r'^(\s*)\*\*([^:]+):\s*["\']?\*\*\s*([^"\']*?)\s*["\']?\s*$', 
                        r'\1\2: \3', content, flags=re.MULTILINE)
        
        # Fix values that end with opening parentheses (incomplete content)
        content = re.sub(r'^(\s*[^:]+):\s*(.+?)\s*\(\s*$', r'\1: \2', content, flags=re.MULTILINE)
        
        return content
    
    # Import the YAML-specific helper methods from ContentFormatter
    @staticmethod
    def _clean_ai_markdown_artifacts(content: str) -> str:
        """Clean markdown artifacts from YAML values."""
        from components.base.utils.content_formatter import ContentFormatter
        return ContentFormatter._clean_ai_markdown_artifacts(content)
    
    @staticmethod
    def _fix_document_structure(content: str) -> str:
        """Fix YAML document structure issues."""
        from components.base.utils.content_formatter import ContentFormatter
        return ContentFormatter._fix_document_structure(content)
    
    @staticmethod
    def _fix_malformed_sequences(content: str) -> str:
        """Fix malformed YAML sequences."""
        from components.base.utils.content_formatter import ContentFormatter
        return ContentFormatter._fix_malformed_sequences(content)
    
    @staticmethod
    def _escape_yaml_values(content: str) -> str:
        """Escape YAML values that need quoting."""
        from components.base.utils.content_formatter import ContentFormatter
        return ContentFormatter._escape_yaml_values(content)
    
    @staticmethod
    def _format_yaml_with_proper_indentation(data, indent_level=0):
        """Format dictionary as YAML with proper indentation."""
        from components.base.utils.content_formatter import ContentFormatter
        return ContentFormatter._format_yaml_with_proper_indentation(data, indent_level)
    
    @staticmethod
    def _aggressive_yaml_cleanup(content: str) -> str:
        """Perform aggressive cleanup on malformed YAML."""
        from components.base.utils.content_formatter import ContentFormatter
        return ContentFormatter._aggressive_yaml_cleanup(content)
