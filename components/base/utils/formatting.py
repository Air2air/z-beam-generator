"""
Formatting utilities for Z-Beam Generator components.

This module provides common formatting functions used across different generators.
"""

import logging
import re
import json
import yaml
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def configure_yaml_formatting():
    """Configure YAML dumper to use proper formatting for strings.
    
    This applies the following formatting rules:
    1. Use literal style (|) for multiline strings to prevent backslash escaping
    2. Use quoted style (") for strings with special characters
    
    Call this function before using yaml.dump() to ensure consistent formatting.
    """
    def str_presenter(dumper, data):
        """Present strings with appropriate YAML style based on content.
        
        Args:
            dumper: YAML dumper instance
            data: String data to format
            
        Returns:
            YAML scalar node with appropriate style
        """
        # Convert data to string if it's not already
        if not isinstance(data, str):
            data = str(data)
            
        # Strip quotes if they're enclosing the entire string
        if data.startswith('"') and data.endswith('"') and len(data) > 1:
            data = data[1:-1]
            
        # Handle newlines within the string
        if '\n' in data or len(data.splitlines()) > 1:
            # Always use literal block style for multiline strings
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        
        # Use double-quoted style for strings with special characters
        if any(char in data for char in "{}[]:#,&*!|>'\"%-@\\"):
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
            
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    # Register the presenter for string types
    yaml.add_representer(str, str_presenter)
    
    return True  # Return success flag

def format_frontmatter_with_comment(yaml_content: str, category: str = "", article_type: str = "", subject: str = "") -> str:
    """Format YAML content as frontmatter with metadata included in the YAML.
    
    Args:
        yaml_content: YAML content for frontmatter
        category: Category for metadata
        article_type: Article type for metadata
        subject: Subject for metadata
        
    Returns:
        str: Formatted frontmatter with metadata and delimiters
    """
    # Strip any existing code block markers (``` or ```) that might cause YAML parsing issues
    if yaml_content.startswith('```') and yaml_content.endswith('```'):
        yaml_content = yaml_content[3:-3].strip()
    
    # Parse the YAML content
    try:
        frontmatter_data = yaml.safe_load(yaml_content)
        if frontmatter_data is None:
            frontmatter_data = {}
        elif not isinstance(frontmatter_data, dict):
            logger.warning("Frontmatter YAML did not parse as a dictionary, creating new dictionary")
            frontmatter_data = {}
    except yaml.YAMLError:
        logger.warning("Could not parse frontmatter YAML, creating new dictionary")
        frontmatter_data = {}
    
    # Add or update metadata fields if provided
    if category:
        frontmatter_data['category'] = category
    if article_type:
        frontmatter_data['article_type'] = article_type
    if subject:
        frontmatter_data['subject'] = subject
    
    # Configure YAML for consistent formatting
    configure_yaml_formatting()
    
    # Convert back to YAML
    updated_yaml = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False, width=float('inf'))
    
    # Add delimiters (no HTML comments)
    delimited_yaml = f"---\n{updated_yaml}---\n"
    
    # Final cleanup for any remaining backslash line continuations
    delimited_yaml = re.sub(r'"\\\s*\n\s*\\?"', '"', delimited_yaml)
    delimited_yaml = re.sub(r'\\\s*\n\s*\\', '\n', delimited_yaml)
    
    return delimited_yaml

def format_jsonld_as_yaml_markdown(jsonld: Dict[str, Any]) -> str:
    """Format JSON-LD as YAML markdown code block.
    
    Args:
        jsonld: JSON-LD data
        
    Returns:
        str: Formatted YAML markdown
        
    Raises:
        ValueError: If JSON-LD cannot be serialized
    """
    try:
        # Configure YAML for consistent formatting
        configure_yaml_formatting()
        
        yaml_str = yaml.dump(jsonld, default_flow_style=False, sort_keys=False, width=float('inf'))
        
        # Clean up any backslash line continuations
        yaml_str = re.sub(r'"\\\s*\n\s*\\?"', '"', yaml_str)
        yaml_str = re.sub(r'\\\s*\n\s*\\', '\n', yaml_str)
        
        # Convert special characters to unicode representations
        yaml_str = (yaml_str
                    .replace('\\u00b3', '³')
                    .replace('\\u00b0', '°')
                    .replace('\\u00b7', '·')
                    .replace('\\u2013', '–')
                    .replace('\\u2082', '₂')
                    .replace('\\u2083', '₃')
                    .replace('\\u00b1', '±'))
                    
        return f'```yaml\n{yaml_str}\n```'
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize JSON-LD as YAML: {e}")

def format_script_tag(json_content: str, content_type: str = "application/ld+json") -> str:
    """Format JSON content as a script tag.
    
    Args:
        json_content: JSON content
        content_type: Content type for script tag
        
    Returns:
        str: JSON content wrapped in script tag
        
    Raises:
        ValueError: If JSON content is invalid
    """
    try:
        # If the content is a dictionary, serialize it to JSON
        if isinstance(json_content, dict):
            json_content = json.dumps(json_content, indent=2)
        # If it's already a string, make sure it's valid JSON
        else:
            json.loads(json_content)
            
        script_tag = f'<script type="{content_type}">\n{json_content}\n</script>'
        return script_tag
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}")

def format_metatags(meta_data: Dict[str, str]) -> str:
    """Format meta data as HTML meta tags.
    
    Args:
        meta_data: Dictionary of meta name/content pairs
        
    Returns:
        str: HTML meta tags
    """
    meta_tags = []
    for name, content in meta_data.items():
        # Handle property vs name attributes
        if name.startswith('og:') or name.startswith('twitter:'):
            meta_tags.append(f'<meta property="{name}" content="{content}" />')
        else:
            meta_tags.append(f'<meta name="{name}" content="{content}" />')
            
    return '\n'.join(meta_tags)

def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format data as markdown table.
    
    Args:
        headers: List of column headers
        rows: List of rows, each row being a list of values
        
    Returns:
        str: Formatted markdown table
    """
    if not headers or not rows:
        return ""
    
    # Create header row
    table = [f"| {' | '.join(headers)} |"]
    
    # Create separator row
    separator = [f"| {' | '.join(['---' for _ in headers])} |"]
    
    # Create data rows
    data_rows = [f"| {' | '.join(row)} |" for row in rows]
    
    # Combine all rows
    return '\n'.join(table + separator + data_rows)

def format_bullet_points(items: List[str], bullet_char: str = '*') -> str:
    """Format a list of items as markdown bullet points.
    
    Args:
        items: List of items to format
        bullet_char: Character to use for bullets
        
    Returns:
        str: Formatted bullet points
    """
    return '\n'.join([f"{bullet_char} {item}" for item in items])

def format_yaml_object(data: Dict[str, Any]) -> str:
    """Format dictionary as YAML string with consistent formatting.
    
    Automatically configures YAML formatting to use proper string styles
    including literal style (|) for multiline strings.
    
    Args:
        data: Dictionary to format
        
    Returns:
        str: Formatted YAML string
        
    Raises:
        ValueError: If serialization fails
    """
    try:
        # Always configure YAML formatting before dumping
        configure_yaml_formatting()
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, width=float('inf'))
        return yaml_str
    except Exception as e:
        raise ValueError(f"Failed to serialize as YAML: {e}")

def clean_html(content: str) -> str:
    """Remove HTML tags from content.
    
    Args:
        content: Content that may contain HTML tags
        
    Returns:
        str: Content with HTML tags removed
    """
    # Simple HTML tag removal using regex
    clean = re.sub(r'<[^>]*>', '', content)
    
    # Replace HTML entities
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'"
    }
    
    for entity, replacement in html_entities.items():
        clean = clean.replace(entity, replacement)
        
    return clean

def format_caption_content(content: str) -> str:
    """Format caption content according to standardized rules.
    
    Applies consistent formatting rules:
    - Material names with proper capitalization
    - Chemical formulas with proper notation (e.g., C₇H₆O₂)
    - Two-line format: Material description + Laser cleaning parameters
    - Removes duplicate text and extra formatting
    
    Args:
        content: Raw caption content from AI
        
    Returns:
        str: Properly formatted caption content
    """
    # Clean up any extra formatting or quotes
    content = re.sub(r'^["\']+|["\']+$', '', content.strip())
    content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
    
    # Remove unwanted brackets that might appear from AI generation
    content = re.sub(r'^\[|\]$', '', content)  # Remove brackets at start/end
    content = re.sub(r'\[\*\*([^*]+)\*\*', r'**\1**', content)  # Fix [**text**
    content = re.sub(r'\*\*([^*]+)\*\*\]', r'**\1**', content)  # Fix **text**]
    content = re.sub(r'\]\s*after\s+laser\s+cleaning', ' after laser cleaning', content, flags=re.IGNORECASE)
    
    # Fix extra asterisks like ****) -> **
    content = re.sub(r'\*{3,}\)', '**', content)
    content = re.sub(r'\*{3,}', '**', content)
    
    # Fix duplicate material names like **Material** (**Material**)
    content = re.sub(r'\*\*([^*]+)\*\*\s*\(\*\*([^*]+)\*\*\)', r'**\1 (\2)**', content)
    
    # Apply chemical formula formatting
    content = format_chemical_formulas(content)
    
    # Apply material name capitalization
    content = format_material_names(content)
    
    # Remove duplicate text (case-insensitive)
    content = remove_duplicate_text(content)
    
    # Format into two-line structure
    return format_two_line_caption(content)

def format_chemical_formulas(text: str) -> str:
    """Format chemical formulas with proper capitalization and subscripts.
    
    Args:
        text: Text containing chemical formulas
        
    Returns:
        str: Text with properly formatted chemical formulas
    """
    # Common chemical formula patterns
    formula_patterns = [
        (r'\bc₇h₆o₂\b', 'C₇H₆O₂'),
        (r'\bsio₂\b', 'SiO₂'),
        (r'\bc₅h₈\b', 'C₅H₈'),
        (r'\bzro₂\b', 'ZrO₂'),
        (r'\bal₂o₃\b', 'Al₂O₃'),
        (r'\bfe₂o₃\b', 'Fe₂O₃'),
        (r'\bcaco₃\b', 'CaCO₃'),
        (r'\bsic\b', 'SiC'),
        # Add more as needed
    ]
    
    for pattern, replacement in formula_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_material_names(text: str) -> str:
    """Format material names with proper capitalization and bold formatting.
    
    Args:
        text: Text containing material names
        
    Returns:
        str: Text with properly capitalized and bolded material names
    """
    # Common material name patterns with their chemical formulas
    # Use more specific patterns to avoid duplication
    material_patterns = [
        # Complex materials with formulas - match the full name and formula
        (r'\b(carbon fiber reinforced polymer|cfrp)(?:\s*\([^)]*\))?\b', r'**Carbon Fiber Reinforced Polymer (CFRP)**'),
        (r'\b(borosilicate glass)(?:\s*\([^)]*\))?\b', r'**Borosilicate Glass (SiO₂-B₂O₃-Na₂O)**'),
        (r'\b(fiberglass)(?:\s*\([^)]*\))?\b', r'**Fiberglass (SiO₂-reinforced polymer matrix)**'),
        (r'\b(phenolic resin composites?)(?:\s*\([^)]*\))?\b', r'**Phenolic Resin Composites**'),
        (r'\b(polyester resin composites?)(?:\s*\([^)]*\))?\b', r'**Polyester Resin Composites**'),
        (r'\b(epoxy resin composites?)(?:\s*\([^)]*\))?\b', r'**Epoxy Resin Composites**'),
        (r'\b(kevlar reinforced polymer)(?:\s*\([^)]*\))?\b', r'**Kevlar Reinforced Polymer**'),
        (r'\b(urethane composites?)(?:\s*\([^)]*\))?\b', r'**Urethane Composites**'),
        (r'\b(thermoplastic elastomer)(?:\s*\([^)]*\))?\b', r'**Thermoplastic Elastomer**'),
        (r'\b(fused silica)(?:\s*\([^)]*\))?\b', r'**Fused Silica (SiO₂)**'),
        (r'\b(float glass)(?:\s*\([^)]*\))?\b', r'**Float Glass**'),
        (r'\b(lead crystal)(?:\s*\([^)]*\))?\b', r'**Lead Crystal**'),
        (r'\b(pyrex)(?:\s*\([^)]*\))?\b', r'**Pyrex**'),
        (r'\b(porcelain)(?:\s*\([^)]*\))?\b', r'**Porcelain**'),
        (r'\b(stoneware)(?:\s*\([^)]*\))?\b', r'**Stoneware**'),
        (r'\b(zirconia)(?:\s*\([^)]*\))?\b', r'**Zirconia (ZrO₂)**'),
        (r'\b(rubber)(?:\s*\([^)]*\))?\b', r'**Rubber**'),
        (r'\b(alumina)(?:\s*\([^)]*\))?\b', r'**Alumina (Al₂O₃)**'),
    ]
    
    for pattern, replacement in material_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def remove_duplicate_text(text: str) -> str:
    """Remove duplicate text patterns (case-insensitive).
    
    Args:
        text: Text that may contain duplicates
        
    Returns:
        str: Text with duplicates removed
    """
    # Remove duplicate "after laser cleaning" patterns
    text = re.sub(r'\*\*after laser cleaning\*\*\s*\*\*after laser cleaning\*\*', 
                  '**After laser cleaning**', text, flags=re.IGNORECASE)
    
    # Remove duplicate chemical formulas after material names
    # Pattern: **Material (Formula)** (formula) -> **Material (Formula)**
    text = re.sub(r'(\*\*[^*]+\([^)]+\)\*\*)\s*\([^)]+\)', r'\1', text)
    
    # Remove duplicate spatial references
    text = re.sub(r'\(left\)\s*\(left\)', '(left)', text)
    text = re.sub(r'\(right\)\s*\(right\)', '(right)', text)
    
    # Remove duplicate "before cleaning" phrases
    text = re.sub(r'before cleaning[,\s]*before cleaning', 'before cleaning', text)
    
    # Remove duplicate "showing" phrases
    text = re.sub(r'showing[,\s]*showing', 'showing', text)
    
    # Remove other duplicate patterns
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    return text
    
    return text

def format_two_line_caption(content: str) -> str:
    """Format content into standardized two-line caption format.
    
    Expected format:
    Line 1: **Material Name (Chemical Formula)** surface (left) showing contaminants before cleaning.
    
    Line 2: **After laser cleaning** (right) at technical parameters, showing results.
    
    Args:
        content: Caption content to format
        
    Returns:
        str: Formatted two-line caption with left/right spatial references
    """
    # Clean up content first - remove extra spaces and normalize whitespace
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Split content into sentences first
    sentences = re.split(r'[.!?]+\s*', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) >= 2:
        # First sentence should be material description
        first_sentence = sentences[0].strip()
        
        # Transform first sentence to include "(left)" and "before cleaning"
        # Look for patterns like "surface analysis revealing" or "surface with"
        if 'surface' in first_sentence.lower():
            # Only add (left) if it's not already there
            if '(left)' not in first_sentence.lower():
                first_sentence = re.sub(r'\bsurface\b', 'surface (left)', first_sentence, flags=re.IGNORECASE)
        else:
            # If no "surface" found, add "(left)" after material name
            if first_sentence.startswith('**') and '**' in first_sentence[2:] and '(left)' not in first_sentence.lower():
                # Find the end of the bold material name
                end_bold = first_sentence.find('**', 2)
                if end_bold != -1:
                    first_sentence = first_sentence[:end_bold+2] + ' (left)' + first_sentence[end_bold+2:]
        
        # Add "before cleaning" context if not present
        if 'before' not in first_sentence.lower() and 'cleaning' not in first_sentence.lower():
            # Replace descriptive words with "before cleaning" context
            first_sentence = re.sub(r'\banalysis\s+revealing\b', 'before cleaning, showing', first_sentence, flags=re.IGNORECASE)
            first_sentence = re.sub(r'\bwith\s+', 'before cleaning, with ', first_sentence, flags=re.IGNORECASE)
            if 'before cleaning' not in first_sentence.lower():
                first_sentence = first_sentence.rstrip('.') + ' before cleaning.'
        
        if not first_sentence.endswith('.'):
            first_sentence += '.'
            
        # Remaining sentences should be laser cleaning parameters
        remaining_sentences = ' '.join(sentences[1:]).strip()
        
        # Ensure the second part starts with "**After laser cleaning** (right)"
        if remaining_sentences:
            # Remove any existing "After laser cleaning" or similar formatting
            remaining_sentences = re.sub(r'^\*\*?[Aa]fter\s+laser\s+cleaning\*\*?\s*', '', remaining_sentences)
            remaining_sentences = re.sub(r'^[Ll]aser\s+cleaning\s+', '', remaining_sentences)
            
            # Fix "At" to "at" at the beginning
            remaining_sentences = re.sub(r'^At\s+', 'at ', remaining_sentences)
            
            # Capitalize first word if needed (but not "at")
            if remaining_sentences and remaining_sentences[0].islower() and not remaining_sentences.startswith('at '):
                remaining_sentences = remaining_sentences[0].upper() + remaining_sentences[1:]
            
            # Add results context if not present
            if 'achieved' in remaining_sentences.lower():
                remaining_sentences = re.sub(r'\bachieved\b', 'showing', remaining_sentences, flags=re.IGNORECASE)
            elif 'revealing' not in remaining_sentences.lower() and 'showing' not in remaining_sentences.lower():
                # Add "showing" before the results
                remaining_sentences = remaining_sentences.rstrip('.') + ', showing complete contaminant removal.'
            
            second_sentence = f"**After laser cleaning** (right) {remaining_sentences}"
            if not second_sentence.endswith('.'):
                second_sentence += '.'
        else:
            second_sentence = "**After laser cleaning** (right) parameters not specified."
        
        return f"{first_sentence}\n\n{second_sentence}"
    
    elif len(sentences) == 1:
        # Single sentence - try to split on "laser" keyword
        sentence = sentences[0]
        laser_match = re.search(r'(.*?)\s+((?:laser|cleaning).*)', sentence, re.IGNORECASE)
        
        if laser_match:
            first_part = laser_match.group(1).strip()
            second_part = laser_match.group(2).strip()
            
            # Add "(left)" and "before cleaning" to first part
            if 'surface' in first_part.lower():
                first_part = re.sub(r'\bsurface\b', 'surface (left)', first_part, flags=re.IGNORECASE)
            first_part = re.sub(r'\banalysis\s+revealing\b', 'before cleaning, showing', first_part, flags=re.IGNORECASE)
            
            if not first_part.endswith('.'):
                first_part += '.'
            
            # Clean up second part and add "After laser cleaning (right)" prefix
            second_part = re.sub(r'^[Ll]aser\s+cleaning\s+', '', second_part)
            second_part = re.sub(r'^At\s+', 'at ', second_part)
            
            if second_part and second_part[0].islower() and not second_part.startswith('at '):
                second_part = second_part[0].upper() + second_part[1:]
            
            second_part = f"**After laser cleaning** (right) {second_part}"
            if not second_part.endswith('.'):
                second_part += '.'
            
            return f"{first_part}\n\n{second_part}"
    
    # Fallback: if we can't split properly, at least ensure proper line breaks
    if '\n' not in content:
        # Add line break before laser content
        content = re.sub(r'(\*\*[^*]+\*\*[^.]*\.?)\s*(.*(?:laser|cleaning).*)', 
                        r'\1\n\n**After laser cleaning** (right) \2', content, flags=re.IGNORECASE)
    
    return content
