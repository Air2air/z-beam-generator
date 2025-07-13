"""YAML response formatter for cleaning and structuring AI responses."""

import re
import yaml
import logging

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
                line.strip().startswith('The metadata')):
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
        """Fix malformed objects with dash on separate line."""
        lines = text.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is an array marker line followed by object properties
            if (line.strip() == '-' and 
                i + 1 < len(lines) and 
                lines[i + 1].strip() and
                ':' in lines[i + 1] and
                not lines[i + 1].strip().startswith('-')):
                
                # This is a malformed array object
                fixed_lines.append('  -')  # Proper array marker
                i += 1
                
                # Process the object properties
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('-'):
                    prop_line = lines[i]
                    if ':' in prop_line:
                        # Ensure proper indentation for object properties
                        fixed_lines.append('    ' + prop_line.strip())
                    else:
                        fixed_lines.append(prop_line)
                    i += 1
                
                # Don't increment i again since we handled it in the loop
                continue
            else:
                fixed_lines.append(line)
                i += 1
        
        return '\n'.join(fixed_lines)
    
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