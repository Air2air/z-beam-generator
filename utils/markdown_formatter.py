import logging
import os
import yaml
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class MarkdownFormatter:
    """Unified markdown document formatter with proper code blocks."""
    
    def __init__(self, schema_parser):
        self.schema_parser = schema_parser

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
    
    def format_frontmatter_as_markdown(self, frontmatter):
        """Convert frontmatter fields to markdown based on display config."""
        output = []
        
        # Get display configuration
        display_config = self.schema_parser.get_default_display_config()
        if not display_config:
            return self._default_formatting(frontmatter)
            
        # Extract table and list configurations
        table_configs = {config["field"]: config for config in display_config.get("tablePresentations", [])}
        list_fields = [item["field"] for item in display_config.get("listPresentations", [])]
        format_options = display_config.get("formatOptions", {})
        
        # Process each field that should be rendered as content
        for field_name, field_data in frontmatter.items():
            # Skip metadata fields
            if field_name in ["name", "description", "website", "contentManagement"]:
                continue
                
            # Add section heading
            output.append(f"\n## {field_name.replace('_', ' ').title()}\n")
            
            # Format field based on configuration
            if field_name in table_configs:
                formatted_content = self._format_as_table(field_data, table_configs[field_name])
                output.append(formatted_content)
            elif field_name in list_fields:
                formatted_content = self._format_as_list(field_data)
                output.append(formatted_content)
            else:
                # Default formatting
                formatted_content = self._format_default(field_data)
                output.append(formatted_content)
                
            # Add spacing
            output.append("\n")
        
        return "\n".join(output)
    
    def _format_as_table(self, data, config):
        """Format data as a markdown table."""
        if not data:
            return "*No data available*"
            
        columns = config.get("columns", [])
        if not columns:
            return self._format_default(data)
            
        # Create header row
        header = "| " + " | ".join([col["name"] for col in columns]) + " |"
        # Make the separator more consistent with markdown standards (add spaces)
        separator = "| " + " | ".join(["----" for _ in columns]) + " |"
        
        rows = []
        
        # Handle different data structures
        if isinstance(data, list):
            # Array of objects (applications, challenges, etc.)
            for item in data:
                if not isinstance(item, dict):
                    continue
                    
                row_values = []
                for col in columns:
                    prop = col["property"]
                    # Handle special case for key/value objects in arrays
                    if prop == "key" and len(item) == 1:
                        row_values.append(str(next(iter(item.keys()), "")))
                    elif prop == "value" and len(item) == 1:
                        row_values.append(str(next(iter(item.values()), "")))
                    else:
                        row_values.append(str(item.get(prop, "")))
                rows.append("| " + " | ".join(row_values) + " |")
        elif isinstance(data, dict):
            # Key-value object (technicalSpecifications)
            # Use the column names from the config if available
            key_name = columns[0]["name"] if len(columns) > 0 else "Parameter"
            value_name = columns[1]["name"] if len(columns) > 1 else "Value"
            
            # Override header with the correct column names
            header = f"| {key_name} | {value_name} |"
            
            for key, value in data.items():
                rows.append(f"| {key} | {value} |")
    
        return "\n".join([header, separator] + rows)
        
    def _format_as_list(self, data):
        """Format data as a markdown list."""
        if not data or not isinstance(data, list):
            return "*No items available*"
            
        return "\n".join([f"- {item}" for item in data])
        
    def _format_default(self, data):
        """Default formatting for unknown data types."""
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            # Simple list formatting
            return "\n".join([f"- {item}" for item in data])
        elif isinstance(data, dict):
            # Simple dictionary formatting
            return "\n".join([f"**{key}**: {value}" for key, value in data.items()])
        else:
            return str(data)
            
    def _default_formatting(self, frontmatter):
        """Default formatting when no display configuration is available."""
        output = []
        
        for field_name, field_data in frontmatter.items():
            # Skip metadata
            if field_name in ["name", "description", "website"]:
                continue
                
            # Add section
            output.append(f"## {field_name.replace('_', ' ').title()}\n")
            
            # Format based on type
            if isinstance(field_data, list):
                output.append(self._format_as_list(field_data))
            elif isinstance(field_data, dict):
                output.append(self._format_default(field_data))
            else:
                output.append(str(field_data))
                
            output.append("\n")
            
        return "\n".join(output)

# Add these functions for backward compatibility
def format_output(frontmatter, tags, jsonld, tables, content):
    """Legacy function for backward compatibility"""
    return MarkdownFormatter.format_output(frontmatter, tags, jsonld, tables, content)

def force_write_output(output_path, content):
    """Legacy function for backward compatibility"""
    return MarkdownFormatter.write_markdown(output_path, content)