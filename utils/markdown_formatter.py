import logging
import os
import yaml
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class MarkdownFormatter:
    """Unified markdown document formatter with proper code blocks."""
    
    @staticmethod
    def format_output(frontmatter, tags, jsonld, tables, content):
        """Format components into a properly formatted markdown string."""
        parts = []
        
        # Format frontmatter
        fm_str = MarkdownFormatter._format_frontmatter(frontmatter)
        if fm_str:
            parts.append(fm_str)
            
        # Add content
        if content:
            parts.append(str(content).strip())
            
        # Format tags as a bulleted list
        tags_str = MarkdownFormatter._format_tags(tags)
        if tags_str:
            parts.append(tags_str)
            
        # Format JSON-LD
        jsonld_str = MarkdownFormatter._format_jsonld(jsonld)
        if jsonld_str:
            parts.append(jsonld_str)
            
        # Add tables
        if tables:
            parts.append(str(tables).strip())
            
        return "\n\n".join(parts)
    
    @staticmethod
    def write_markdown(output_path, content):
        """Write formatted markdown to file."""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Successfully wrote markdown to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing markdown: {e}")
            return False
    
    @staticmethod
    def _format_frontmatter(frontmatter):
        """Format frontmatter with triple backticks."""
        if not frontmatter:
            return ""
            
        if isinstance(frontmatter, dict):
            # Use StringIO to capture YAML dump
            import io
            fm_buffer = io.StringIO()
            yaml.dump(frontmatter, fm_buffer, default_flow_style=False)
            return f"```yaml\n{fm_buffer.getvalue().strip()}\n```"
        
        # Handle string frontmatter
        fm_str = str(frontmatter).strip()
        
        # Convert from --- to ``` if needed
        if fm_str.startswith('---'):
            parts = fm_str.split('---', 2)
            if len(parts) >= 2:
                return f"```yaml\n{parts[1].strip()}\n```"
        
        # Add backticks if not present
        if not fm_str.startswith('```yaml'):
            return f"```yaml\n{fm_str}\n```"
        
        return fm_str
    
    @staticmethod
    def _format_tags(tags):
        """Format tags as a bulleted list."""
        if not tags:
            return ""
            
        if isinstance(tags, list):
            return "## Tags\n" + "\n".join([f"- {tag}" for tag in tags])
        
        # Handle string tags (already formatted or newline-separated)
        tags_str = str(tags).strip()
        
        # If tags are just newline-separated, format as bullets
        if "\n" in tags_str and not tags_str.startswith("- "):
            tag_list = [t.strip() for t in tags_str.split("\n") if t.strip()]
            return "## Tags\n" + "\n".join([f"- {tag}" for tag in tag_list])
        
        return "## Tags\n" + tags_str
    
    @staticmethod
    def _format_jsonld(jsonld):
        """Format JSON-LD with triple backticks."""
        if not jsonld:
            return ""
            
        jsonld_str = str(jsonld).strip()
        
        if not jsonld_str.startswith('```json'):
            return f"```json\n{jsonld_str}\n```"
            
        return jsonld_str

# Add these functions for backward compatibility
def format_output(frontmatter, tags, jsonld, tables, content):
    """Legacy function for backward compatibility"""
    return MarkdownFormatter.format_output(frontmatter, tags, jsonld, tables, content)

def force_write_output(output_path, content):
    """Legacy function for backward compatibility"""
    return MarkdownFormatter.write_markdown(output_path, content)