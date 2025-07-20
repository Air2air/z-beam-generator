# Z-Beam Component System

## Overview

The Z-Beam Component System is a modular architecture for generating content for laser cleaning articles. Each component is responsible for generating a specific part of the article, such as frontmatter, main content, tables, tags, etc.

## Core Concepts

### BaseComponent

All components inherit from the `BaseComponent` abstract base class, which provides:

- Standard initialization interface
- Content generation methods
- Utility methods for frontmatter extraction and section title formatting
- Error handling patterns

### Component Registry

The Component Registry provides dynamic discovery and instantiation of components:

- Automatic component discovery
- Component registration
- Component lookup by name
- Listing of available components

### ArticleAssembler

The ArticleAssembler coordinates the generation process:

- Determines component execution order
- Handles dependencies between components
- Passes frontmatter between components
- Assembles the final article from component outputs

## Component Interface

All components must implement the following interface:

```python
class SomeComponent(BaseComponent):
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        # Initialize the component with context, schema, and AI provider
        super().__init__(context, schema, ai_provider)
        
    def generate(self) -> str:
        # Generate and return content as a string
        pass
        
    # Optional methods:
    def set_options(self, options: Dict[str, Any]) -> 'SomeComponent':
        # Set component-specific options
        return self
        
    def set_frontmatter(self, frontmatter: Dict[str, Any]) -> 'SomeComponent':
        # Set frontmatter data
        return self
        
    def set_previous_outputs(self, previous_outputs: Dict[str, Any]) -> 'SomeComponent':
        # Set outputs from previously executed components
        return self