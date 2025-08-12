"""
Aggregate component generator for Z-Beam Generator.

Generates all components for a material in a single API request.
"""

import json
import logging
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class AggregateGenerator(BaseComponent):
    """Generator that creates all components for a material in one API request."""
    
    def __init__(self, subject: str, article_type: str, schema: dict, author_data: dict, component_config: dict):
        super().__init__(subject, article_type, schema, author_data, component_config)
        self.enabled_components = self._get_enabled_components()
    
    def _get_enabled_components(self) -> list:
        """Get list of enabled components from config."""
        # This would be passed from run.py based on BATCH_CONFIG
        return ['frontmatter', 'bullets', 'table', 'metatags', 'jsonld', 'caption', 'tags']
    
    def _get_system_prompt(self) -> str:
        """Get aggregate system prompt for all components."""
        return f"""You are a materials science expert. Generate ALL website components for {self.subject} in a single structured response.

Return a valid JSON object with these exact keys: {', '.join(self.enabled_components)}

Requirements for each component:
- frontmatter: YAML format metadata (title, description, category, etc.)
- bullets: Array of exactly 4 key benefit/feature points
- table: Object with "headers" and "rows" arrays for material properties
- metatags: Object with title, description, keywords for SEO
- jsonld: Structured data object for schema.org/Material
- caption: Single descriptive text for material image
- tags: Array of exactly 8 relevant category tags

Focus on {self.category} materials. Be accurate and technical."""
    
    def _component_specific_processing(self, content: str) -> Dict[str, str]:
        """Parse aggregate JSON response into individual component files."""
        try:
            # Parse the JSON response
            components_data = json.loads(content)
            
            # Validate all expected components are present
            missing = set(self.enabled_components) - set(components_data.keys())
            if missing:
                raise ValueError(f"Missing components in response: {missing}")
            
            # Process each component using its specific formatter
            processed_components = {}
            
            for component_name in self.enabled_components:
                raw_data = components_data[component_name]
                processed_content = self._process_individual_component(component_name, raw_data)
                processed_components[component_name] = processed_content
            
            return processed_components
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from API: {e}")
        except Exception as e:
            raise ValueError(f"Failed to process aggregate response: {e}")
    
    def _process_individual_component(self, component_name: str, raw_data: Any) -> str:
        """Process individual component data using component-specific logic."""
        
        if component_name == 'frontmatter':
            # Convert dict to YAML format
            import yaml
            yaml_content = yaml.dump(raw_data, default_flow_style=False, allow_unicode=True)
            return f"---\n{yaml_content}---"
        
        elif component_name == 'bullets':
            # Convert array to markdown bullets
            if isinstance(raw_data, list):
                bullets_text = '\n'.join(f"• {bullet}" for bullet in raw_data)
                return bullets_text
            else:
                raise ValueError("Bullets must be an array")
        
        elif component_name == 'table':
            # Convert table object to markdown table
            if isinstance(raw_data, dict) and 'headers' in raw_data and 'rows' in raw_data:
                headers = raw_data['headers']
                rows = raw_data['rows']
                
                # Create markdown table
                table_lines = []
                table_lines.append('| ' + ' | '.join(headers) + ' |')
                table_lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                
                for row in rows:
                    table_lines.append('| ' + ' | '.join(str(cell) for cell in row) + ' |')
                
                return '\n'.join(table_lines)
            else:
                raise ValueError("Table must have 'headers' and 'rows' keys")
        
        elif component_name == 'metatags':
            # Convert dict to YAML format for metatags
            import yaml
            yaml_content = yaml.dump(raw_data, default_flow_style=False, allow_unicode=True)
            return f"---\n{yaml_content}---"
        
        elif component_name == 'jsonld':
            # Convert dict to YAML format for jsonld
            import yaml
            yaml_content = yaml.dump(raw_data, default_flow_style=False, allow_unicode=True)
            return f"---\n{yaml_content}---"
        
        elif component_name == 'caption':
            # Return caption text as-is
            return str(raw_data)
        
        elif component_name == 'tags':
            # Convert array to YAML format
            import yaml
            tags_dict = {'tags': raw_data}
            yaml_content = yaml.dump(tags_dict, default_flow_style=False, allow_unicode=True)
            return f"---\n{yaml_content}---"
        
        else:
            # Default: return as string
            return str(raw_data)
    
    def generate(self) -> Dict[str, str]:
        """Generate all components and return as dictionary.
        
        Returns:
            Dict[str, str]: Component name -> generated content
        """
        # Get template data
        data = self.get_template_data()
        prompt = self._format_prompt(data)
        
        # Make single API call
        content = self._call_api(prompt)
        
        # Process response into individual components
        return self._post_process(content)
    
    def _post_process(self, content: str) -> Dict[str, str]:
        """Override to return dict instead of string."""
        # Basic validation
        from components.base.utils.validation import validate_non_empty
        content = validate_non_empty(content, "API returned empty response")
        
        # Remove code blocks if present
        content = self._strip_markdown_code_blocks(content)
        
        # Process into individual components
        return self._component_specific_processing(content)
