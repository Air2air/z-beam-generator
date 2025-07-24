"""
Error handling utilities for components.

This module provides standardized error handling methods for components
to ensure consistent error reporting and graceful failure modes.
"""

import logging
import datetime
from typing import Dict, Any

from utils.string_utils import StringUtils

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handles component errors with standardized formatting."""
    
    @staticmethod
    def create_error_markdown(component_name: str, error_message: str, 
                            subject: str = "", article_type: str = "") -> str:
        """Create markdown content for error conditions.
        
        Args:
            component_name: Name of the component that encountered the error
            error_message: Error message to include
            subject: Subject of the article (optional, for frontmatter component)
            article_type: Article type (optional, for frontmatter component)
            
        Returns:
            Markdown content with error information
        """
        # Special handling for frontmatter component to prevent downstream failures
        if component_name.lower().startswith('frontmatter'):
            return ErrorHandler._create_frontmatter_error(
                subject, article_type, component_name, error_message)
            
        # Create a standardized error message in markdown format
        markdown = f"""<!-- ERROR: {error_message} -->

## Error Generating {StringUtils.format_title(component_name)}

An error occurred while generating the content for {StringUtils.format_title(component_name)}.

### Error Details
```
{error_message}
```

Please check the component configuration and logs for more information.

<!-- End ERROR -->
"""
        logger.error(markdown)
        return markdown

    @staticmethod
    def _create_frontmatter_error(subject: str, article_type: str, 
                                 component_name: str, error_message: str) -> str:
        """Create a frontmatter-specific error message.
        
        Args:
            subject: Subject of the article
            article_type: Article type
            component_name: Name of the component that encountered the error
            error_message: Error message to include
            
        Returns:
            Markdown content with frontmatter error information
        """
        # Generate minimal valid frontmatter when the frontmatter component fails
        current_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        # Escape quotes in error message to prevent YAML parsing errors
        safe_error = error_message.replace('"', "'")
        
        return f"""---
title: "{subject or 'Content Generation Failed'}"
subtitle: "Error in Content Generation"
description: "Could not generate content due to an error in the frontmatter component."
slug: "{StringUtils.create_slug(subject) if subject else 'error'}"
date: "{current_date}"
article_type: "{article_type or 'error'}"
error: true
error_message: "{safe_error}"
---

<!-- ERROR: {error_message} -->

## Error in Frontmatter Component

An error occurred in the frontmatter component.

### Error Details
```
{error_message}
```

#### Frontmatter Subject: {subject}
#### Article Type: {article_type}

Please check the frontmatter configuration and logs for more information.

<!-- End ERROR -->
"""
