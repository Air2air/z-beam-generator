# Z-Beam Component Best Practices

## Component Structure

All Z-Beam components must follow the standardized structure:

1. **Module Directives**: Include the standard MODULE DIRECTIVES comment
2. **Standard Imports**: Import BaseComponent and standard libraries
3. **Logger**: Set up component-specific logging
4. **Component Class**: Inherit from BaseComponent
5. **Generate Method**: Implement the standard 5-step generate method
6. **Private Methods**: Implement the four standard private methods

## Standard Methods

### generate()

The main entry point that follows this pattern:
```python
def generate(self) -> str:
    """Generate component content."""
    try:
        # 1. Get frontmatter data using standard method
        frontmatter_data = self.get_frontmatter_data()
        
        if not frontmatter_data:
            logger.warning("No frontmatter data available")
            return self._create_error_markdown("Missing frontmatter data")
            
        # 2. Prepare data for prompt
        prompt_data = self._prepare_data(frontmatter_data)
        
        # 3. Format prompt
        prompt = self._format_prompt(prompt_data)
        
        # 4. Call API
        content = self._call_api(prompt)
        
        # 5. Post-process content
        return self._post_process(content)
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return self._create_error_markdown(str(e))