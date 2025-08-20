"""
Aggregate generation integration for run.py

Modifies the standard component generation flow to use single API request
for all components of a material.
"""

import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

def generate_material_aggregate(article_context: dict) -> Dict[str, str]:
    """Generate all components for a material in a single API request.
    
    Args:
        article_context: Article context with subject, type, components config, etc.
        
    Returns:
        Dict[str, str]: Component name -> generated content
        
    Raises:
        ValueError: If aggregate generation fails
    """
    
    # Get enabled components
    enabled_components = []
    components_config = article_context.get("components", {})
    
    for component_name, config in components_config.items():
        if config.get("enabled", False):
            enabled_components.append(component_name)
    
    if not enabled_components:
        raise ValueError("No components enabled for generation")
    
    print(f"🔄 Aggregate generation for: {article_context['subject']}")
    print(f"📦 Components: {', '.join(enabled_components)}")
    print(f"🤖 Provider: {article_context['ai_provider']} ({article_context['options']['model']})")
    
    # Load schema and author data
    schema = {}
    schema_path = f"schemas/{article_context['article_type']}.json"
    if os.path.exists(schema_path):
        import json
        with open(schema_path, 'r') as f:
            schema = json.load(f)
    
    # Load author data
    author_data = {}
    author_file = "components/author/authors.json"
    if os.path.exists(author_file):
        import json
        with open(author_file, 'r') as f:
            authors = json.load(f)
            author_id = article_context.get("author_id", 1)
            author_data = authors.get(str(author_id), {})
    
    # Create aggregate generator
    from components.aggregate.generator import AggregateGenerator
    
    # Use first enabled component's config as base (they should be similar)
    base_config = next(iter(components_config.values())).copy()
    
    generator = AggregateGenerator(
        subject=article_context["subject"],
        article_type=article_context["article_type"], 
        schema=schema,
        author_data=author_data,
        component_config=base_config,
        enabled_components=enabled_components  # Pass the enabled components list
    )
    
    # Generate all components
    try:
        components_content = generator.generate()
        
        print("✅ Aggregate generation successful")
        print(f"📋 Generated {len(components_content)} components")
        
        return components_content
        
    except Exception as e:
        print(f"❌ Aggregate generation failed: {e}")
        raise ValueError(f"Aggregate generation failed for {article_context['subject']}: {e}")

def save_generated_components(components_content: Dict[str, str], article_context: dict) -> None:
    """Save generated components to individual files.
    
    Args:
        components_content: Dict of component_name -> content
        article_context: Article context for file paths
    """
    
    subject = article_context["subject"]
    
    # Ensure content directory exists
    content_dir = "content"
    os.makedirs(content_dir, exist_ok=True)
    
    saved_count = 0
    
    for component_name, content in components_content.items():
        
        # Determine file extension
        if component_name in ['frontmatter', 'metatags', 'jsonld', 'tags']:
            extension = 'md'  # YAML content with frontmatter delimiters
        elif component_name == 'table':
            extension = 'md'  # Markdown table
        else:
            extension = 'md'  # Default to markdown
        
        # Create filename
        filename = f"{subject.replace(' ', '_').lower()}_{component_name}.{extension}"
        filepath = os.path.join(content_dir, filename)
        
        # Write content to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 Saved {component_name}: {filepath}")
            saved_count += 1
            
        except Exception as e:
            print(f"❌ Failed to save {component_name}: {e}")
    
    print(f"✅ Saved {saved_count}/{len(components_content)} components")

def run_aggregate_generation(article_context: dict) -> bool:
    """Run complete aggregate generation workflow.
    
    Args:
        article_context: Complete article context
        
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        # Generate all components in one request
        components_content = generate_material_aggregate(article_context)
        
        # Save components to files  
        save_generated_components(components_content, article_context)
        
        return True
        
    except Exception as e:
        logger.error(f"Aggregate generation workflow failed: {e}")
        return False

# Configuration for aggregate mode
AGGREGATE_CONFIG = {
    "enabled": False,  # Set to True to enable aggregate generation
    "fallback_to_individual": True,  # If aggregate fails, try individual components
    "components": [
        "frontmatter", "bullets", "table", 
        "metatags", "jsonld", "caption", "tags"
    ],
    "prompt_optimization": {
        "temperature": 0.7,  # Balanced for consistency across components
        "max_tokens": 8000,  # Higher limit for multiple components
        "model": "deepseek-chat"  # Use most capable model
    }
}
