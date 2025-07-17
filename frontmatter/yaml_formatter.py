"""YAML response formatter for cleaning and structuring AI responses."""

import re
import yaml
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class YAMLFormatter:
    """Handles cleaning and formatting of YAML responses from AI."""
    
    @staticmethod
    def clean_response(response: str) -> str:
        """Clean and format the response for YAML parsing."""
        cleaned = response.strip()
        
        # Fix Unicode encoding issues BEFORE other processing
        try:
            # Handle unicode escape sequences properly
            cleaned = cleaned.encode('utf-8').decode('unicode_escape')
            
            # Fix specific character issues
            cleaned = cleaned.replace('Âµ', 'µ')  # Fix micro symbol
            cleaned = cleaned.replace('Â²', '²')  # Fix superscript 2
            cleaned = cleaned.replace('Î¼', 'μ')  # Fix mu character
            
            # Remove problematic control characters
            # Remove control characters (0x00-0x1F and 0x7F-0x9F) except newlines and tabs
            cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', cleaned)
            
            # Fix common Unicode issues
            cleaned = cleaned.replace('â¤', '≤')  # Fix less than or equal
            cleaned = cleaned.replace('â', '–')   # Fix en dash
            cleaned = cleaned.replace('â', '—')   # Fix em dash
            
        except (UnicodeDecodeError, UnicodeEncodeError):
            # If decoding fails, just remove control characters
            cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', cleaned)

        # Remove markdown code blocks
        if "```yaml" in cleaned:
            start = cleaned.find("```yaml")
            if start != -1:
                start = cleaned.find('\n', start) + 1
                end = cleaned.rfind('```')
                if end > start:
                    cleaned = cleaned[start:end]
        elif "```" in cleaned:
            start = cleaned.find("```")
            if start != -1:
                start = cleaned.find('\n', start) + 1
                end = cleaned.rfind('```')
                if end > start:
                    cleaned = cleaned[start:end]

        # Remove obvious non-YAML lines
        lines = cleaned.split('\n')
        yaml_lines = []
        
        for line in lines:
            if (line.strip().startswith('```') or 
                line.strip().startswith('Here is') or 
                line.strip().startswith('This YAML') or
                line.strip().startswith('The frontmatter')):
                continue
            yaml_lines.append(line)

        cleaned = '\n'.join(yaml_lines)
        
        # Fix malformed YAML object arrays
        cleaned = YAMLFormatter._fix_malformed_array_objects(cleaned)
        cleaned = YAMLFormatter._fix_quoted_objects(cleaned)
        cleaned = YAMLFormatter._fix_unquoted_objects(cleaned)
        
        print(f"🔍 DEBUG METADATA: Cleaned response:\n{cleaned}")
        
        return cleaned.strip()
    
    @staticmethod
    def _fix_malformed_array_objects(text: str) -> str:
        """Fix malformed objects with dash on separate line using comprehensive regex."""
        import re
        
        # Step 1: Find all malformed array blocks
        # Pattern: array_name: followed by malformed items
        array_pattern = r'(\w+):\s*\n((?:\s*-\s*\n(?:\s*\w+:\s*"[^"]*"\s*\n?)+)+)'
        
        def fix_array_block(match):
            array_name = match.group(1)
            array_content = match.group(2)
            
            # Split into individual array items
            items = []
            current_item = []
            
            for line in array_content.split('\n'):
                line = line.strip()
                if line == '-':
                    if current_item:
                        items.append(current_item)
                        current_item = []
                elif line and ':' in line:
                    current_item.append(line)
            
            # Don't forget the last item
            if current_item:
                items.append(current_item)
            
            # Rebuild with proper YAML formatting
            result = [f"{array_name}:"]
            for item in items:
                if item:  # Only add non-empty items
                    result.append('  -')
                    for prop in item:
                        result.append('    ' + prop)
            
            return '\n'.join(result)
        
        # Apply the fix
        fixed_text = re.sub(array_pattern, fix_array_block, text, flags=re.MULTILINE)
        
        # Count fixes applied
        matches = re.findall(array_pattern, text, flags=re.MULTILINE)
        fixes_applied = len(matches)
        
        print(f"✅ Applied {fixes_applied} array block fixes via regex")
        
        # Debug output
        if fixes_applied > 0:
            print("🔧 Fixed array sections:")
            for match in matches:
                print(f"  → {match[0]}:")
        
        return fixed_text
    
    @staticmethod
    def _fix_quoted_objects(text: str) -> str:
        """Fix quoted objects like: - "{'name': 'value', 'key': 'value'}"."""
        pattern = r'- "(\{[^}]+\})"'
        
        def fix_quoted_object(match):
            obj_str = match.group(1)
            # Remove outer braces
            obj_str = obj_str[1:-1]
            
            # Split by comma and process each key-value pair
            pairs = []
            current = ""
            in_quotes = False
            
            for char in obj_str:
                if char == "'" and not in_quotes:
                    in_quotes = True
                elif char == "'" and in_quotes:
                    in_quotes = False
                elif char == "," and not in_quotes:
                    pairs.append(current.strip())
                    current = ""
                    continue
                current += char
            
            if current.strip():
                pairs.append(current.strip())
            
            # Convert to proper YAML format
            result = "  -\n"
            for pair in pairs:
                if ":" in pair:
                    key, value = pair.split(":", 1)
                    key = key.strip().strip("'\"")
                    value = value.strip().strip("'\"")
                    result += f"    {key}: \"{value}\"\n"
            
            return result.rstrip()
        
        return re.sub(pattern, fix_quoted_object, text, flags=re.MULTILINE)
    
    @staticmethod
    def _fix_unquoted_objects(text: str) -> str:
        """Fix unquoted objects like: - 'name': 'value', 'key': 'value'."""
        pattern = r"- '([^']+)': '([^']+)'(?:, '([^']+)': '([^']+)')*"
        
        def fix_unquoted_object(match):
            # Extract all key-value pairs from the match
            full_match = match.group(0)
            
            # Split by comma to get individual key-value pairs
            pairs = []
            current = ""
            in_quotes = False
            
            for char in full_match[2:]:  # Skip "- "
                if char == "'" and not in_quotes:
                    in_quotes = True
                elif char == "'" and in_quotes:
                    in_quotes = False
                elif char == "," and not in_quotes:
                    pairs.append(current.strip())
                    current = ""
                    continue
                current += char
                
            if current.strip():
                pairs.append(current.strip())
            
            # Convert to proper YAML format
            result = "  -\n"
            for pair in pairs:
                if ":" in pair:
                    key, value = pair.split(":", 1)
                    key = key.strip().strip("'\"")
                    value = value.strip().strip("'\"")
                    result += f"    {key}: \"{value}\"\n"
            
            return result.rstrip()
        
        return re.sub(pattern, fix_unquoted_object, text, flags=re.MULTILINE)
    
    @staticmethod
    def validate_yaml_structure(yaml_content: str) -> bool:
        """Validate YAML structure before parsing."""
        try:
            # Check for malformed comma-separated arrays (multiple patterns)
            if ("- '" in yaml_content and "', '" in yaml_content) or \
               ('- "{\'' in yaml_content and "}" in yaml_content):
                logger.error("Detected malformed YAML arrays with comma separation")
                return False
            
            # Check for unicode escape sequences
            if "\\u" in yaml_content or "\\x" in yaml_content:
                logger.warning("Detected unicode escape sequences")
                return False
            
            # Try to parse the YAML to catch other issues
            yaml.safe_load(yaml_content)
            return True
            
        except yaml.YAMLError as e:
            logger.error(f"YAML validation error: {e}")
            return False
        except Exception as e:
            logger.error(f"YAML validation error: {e}")
            return False
    
def format_yaml_content(content: str) -> str:
    """
    Format YAML content to remove excessive escape characters.
    
    Args:
        content: The raw YAML content with escape characters
        
    Returns:
        Properly formatted YAML string
    """
    if not content:
        return ""
    
    # Remove the wrapping quotes if they exist
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
    
    # Replace escaped newlines with actual newlines
    content = content.replace('\\n', '\n')
    
    # Replace escaped quotes with regular quotes
    content = content.replace('\\"', '"')
    
    # Fix special characters
    content = content.replace('\\xB2', '²')
    content = content.replace('\\u03BCm', 'μm')
    content = content.replace('\\xC2\\xB0', '°')
    
    return content