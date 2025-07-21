# Frontmatter Handling Standard

## Overview

This document outlines the standard approach for handling frontmatter data in the Z-Beam system.

## Core Principles

1. **BaseComponent Integration**: All frontmatter handling is integrated into BaseComponent
2. **Standard Methods**: Components access frontmatter via BaseComponent's `get_frontmatter_data()` method
3. **Data Propagation**: ArticleAssembler is responsible for extracting and providing frontmatter to components
4. **Type Consistency**: Frontmatter data is always a dictionary, never a list or other type

## Standard Methods

### Extraction

```python
from components.base import BaseComponent

# Extract from string
frontmatter_data = BaseComponent.extract_frontmatter(markdown_content)

# Extract from file
frontmatter_data = BaseComponent.extract_frontmatter_from_file(file_path)
```

### Formatting Section Titles

When displaying frontmatter fields as section headers, always use the `format_section_title` method:

```python
def generate(self):
    # Get frontmatter data
    frontmatter_data = self.get_frontmatter_data()
    
    # Display technical specifications section
    if "technicalSpecifications" in frontmatter_data:
        section_title = self.format_section_title("technicalSpecifications")
        # "Technical Specifications"
        
        # Generate content for this section
        content = f"## {section_title}\n"
        # ...
```