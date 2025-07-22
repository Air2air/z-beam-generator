# Z-Beam Component Standards

## Overview
This document defines standardized patterns for Z-Beam components to ensure consistency, maintainability, and efficiency across the codebase.

## Module Directives

All components should follow these key directives:

1. **FRONTMATTER-DRIVEN**: All content must be extracted from frontmatter
2. **NO HARDCODED SECTIONS**: Section structure must be derived from frontmatter
3. **DYNAMIC FORMATTING**: Format content based on article_type from frontmatter
4. **ERROR HANDLING**: Raise exceptions when required frontmatter fields are missing
5. **SCHEMA AWARENESS**: Be aware of the schema structure for different article types

## Component Structure

### Base Pattern

All components must follow this standard structure:

```python
"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
from typing import Dict, Any, List
from components.base import BaseComponent

logger = logging.getLogger(__name__)

class ExampleComponent(BaseComponent):
    """Component description with clear purpose."""
    
    def generate(self) -> str:
        """Generate component content.
        
        Returns:
            Markdown string content
        """
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for component")
                return ""
                
            # 2. Prepare data for prompt
            prompt_data = self._prepare_data(frontmatter_data)
            
            # 3. Format prompt
            prompt = self._format_prompt(prompt_data)
            
            # 4. Call API
            content = self._call_api(prompt)
            
            # 5. Post-process content
            return self._post_process(content)
            
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for prompt formatting."""
        return {
            "subject": self.subject,
            "article_type": self.article_type,
            # Component-specific data preparation
        }
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data."""
        template = self.load_prompt_template()
        return template.format(**data)
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt."""
        return self.api_client.generate_content(prompt)
    
    def _post_process(self, content: str) -> str:
        """Post-process API response."""
        return content
```