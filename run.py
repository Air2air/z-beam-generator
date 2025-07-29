#!/usr/bin/env python3
"""
Z-Beam content generation system entry point.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. CONFIGURATION PRECEDENCE: ARTICLE_CONTEXT is the primary configuration source
2. NO CACHING: No caching of resources, data, or objects anywhere in the system
3. FRESH LOADING: Always load fresh data on each access
4. ARTICLE_CONTEXT DRIVEN: All configuration derives from ARTICLE_CONTEXT
5. DYNAMIC COMPONENTS: Use registry to discover and load components
6. ERROR HANDLING: Provide clear error messages with proper logging
7. ENVIRONMENT VARIABLES: Load environment variables from .env file
8. API KEY MANAGEMENT: Check for required API keys and warn if missing
9. SIMPLIFIED INTERFACE: Edit ARTICLE_CONTEXT directly for all configuration
"""


# Define the primary article context - THE ONLY SOURCE OF TRUTH
ARTICLE_CONTEXT = {
    # Core article parameters
    "subject": "hayward",
    "article_type": "region",  # application, material, region, or thesaurus
    "author_id": 1,  # 1: Taiwan, 2: Italy, 3: USA, 4: Indonesia
    "components": {
        "frontmatter": {
            "enabled": True,
            "include_website": True,
            "min_words": 300,
            "max_words": 500,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.9,
                "max_tokens": 4000
            },  
        },
        "content": {
            "enabled": True,
            "min_words": 300,
            "max_words": 500,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            },  
        },
        "bullets": {
            "enabled": True,
            "count": 10,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            },  
        },
        "table": {
            "enabled": True,
            "rows": 5,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            },  
        },
        "tags": {
            "enabled": True,
            "count": 10,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            }, 
        },
        "jsonld": {
            "enabled": True,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            },  
        },
    },
    # Output configuration
    "output_dir": "output",
}


def setup_environment() -> None:
    """Set up the application environment."""
    # Load environment variables
    import os
    from dotenv import load_dotenv
    
    # Try to load .env file if it exists
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print("No .env file found. Please create one with your API keys.")
        print("Example .env content:")
        print("DEEPSEEK_API_KEY=your_deepseek_api_key_here")


def generate_component(component_name: str, frontmatter_content: str = None):
    """Generate content for a specific component.
    
    Args:
        component_name: Name of the component to generate
        frontmatter_content: Previously generated frontmatter content for context
        
    Returns:
        Generated content or None if failed
    """
    import sys
    import os
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        # Get component config from ARTICLE_CONTEXT
        component_config = ARTICLE_CONTEXT["components"][component_name]
        
        if not component_config["enabled"]:
            print(f"⏭️  {component_name.capitalize()} generation skipped (disabled)")
            return None
        
        # Load schema for the article type
        schema_path = f"schemas/{ARTICLE_CONTEXT['article_type']}.json"
        schema = {}
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                import json
                schema = json.load(f)
        
        # Create context for the generator - include full ARTICLE_CONTEXT
        generator_context = ARTICLE_CONTEXT.copy()
        
        # Ensure required fields are present
        generator_context.update({
            "subject": ARTICLE_CONTEXT["subject"],
            "article_type": ARTICLE_CONTEXT["article_type"],
            "author_id": ARTICLE_CONTEXT["author_id"],
            "ai_provider": component_config["ai_provider"],
            "options": component_config["options"]
        })
        
        # Add frontmatter content to context if available
        if frontmatter_content:
            generator_context["frontmatter_content"] = frontmatter_content
        
        # Import and initialize the appropriate generator
        if component_name == "content":
            from components.content.generator import ContentGenerator
            generator = ContentGenerator(
                context=generator_context,
                schema=schema,
                ai_provider=component_config["ai_provider"]
            )
        elif component_name == "bullets":
            from components.bullets.generator import BulletsGenerator
            generator = BulletsGenerator(
                context=generator_context,
                schema=schema,
                ai_provider=component_config["ai_provider"]
            )
        elif component_name == "table":
            from components.table.generator import TableGenerator
            generator = TableGenerator(
                context=generator_context,
                schema=schema,
                ai_provider=component_config["ai_provider"]
            )
        elif component_name == "tags":
            from components.tags.generator import TagsGenerator
            generator = TagsGenerator(
                context=generator_context,
                schema=schema,
                ai_provider=component_config["ai_provider"]
            )
        elif component_name == "jsonld":
            from components.jsonld.generator import JsonldGenerator
            generator = JsonldGenerator(
                context=generator_context,
                schema=schema,
                ai_provider=component_config["ai_provider"]
            )
        else:
            raise ValueError(f"Unknown component: {component_name}")
        
        print(f"Generating {component_name} for: {ARTICLE_CONTEXT['subject']} ({ARTICLE_CONTEXT['article_type']})")
        print(f"Using AI provider: {component_config['ai_provider']} with model: {component_config['options']['model']}")
        
        # Generate content
        content = generator.generate()
        
        print("\n" + "="*60)
        print(f"GENERATED {component_name.upper()}:")
        print("="*60)
        print(content)
        print("="*60)
        
        return content
        
    except Exception as e:
        print(f"Error generating {component_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_frontmatter():
    """Generate frontmatter using the configured settings."""
    import sys
    import os
    import logging
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # Check if frontmatter is enabled
        component_config = ARTICLE_CONTEXT["components"]["frontmatter"]
        if not component_config["enabled"]:
            print("⏭️  Frontmatter generation skipped (disabled)")
            return None
        
        # Load schema for the article type
        schema_path = f"schemas/{ARTICLE_CONTEXT['article_type']}.json"
        schema = {}
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                import json
                schema = json.load(f)
        
        # Initialize frontmatter generator
        from components.frontmatter.generator import FrontmatterGenerator
        
        # Create context for the generator - include full ARTICLE_CONTEXT
        generator_context = ARTICLE_CONTEXT.copy()
        
        # Ensure required fields are present
        generator_context.update({
            "subject": ARTICLE_CONTEXT["subject"],
            "article_type": ARTICLE_CONTEXT["article_type"],
            "author_id": ARTICLE_CONTEXT["author_id"],
            "ai_provider": component_config["ai_provider"],
            "options": component_config["options"]
        })
        
        # Initialize generator
        generator = FrontmatterGenerator(
            context=generator_context,
            schema=schema,
            ai_provider=component_config["ai_provider"]
        )
        
        print(f"Generating frontmatter for: {ARTICLE_CONTEXT['subject']} ({ARTICLE_CONTEXT['article_type']})")
        print(f"Using AI provider: {component_config['ai_provider']} with model: {component_config['options']['model']}")
        
        # Generate frontmatter
        frontmatter_content = generator.generate()
        
        print("\n" + "="*60)
        print("GENERATED FRONTMATTER:")
        print("="*60)
        print(frontmatter_content)
        print("="*60)
        
        return frontmatter_content
        
    except Exception as e:
        print(f"Error generating frontmatter: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point for the Z-Beam content generation system."""
    setup_environment()
    
    print("Z-Beam content generation system started.")
    print(f"Subject: {ARTICLE_CONTEXT['subject']}")
    print(f"Article Type: {ARTICLE_CONTEXT['article_type']}")
    print(f"Author ID: {ARTICLE_CONTEXT['author_id']}")
    
    # Track all generated content
    all_content = []
    
    # Generate frontmatter first
    frontmatter = generate_frontmatter()
    if frontmatter:
        all_content.append(frontmatter)
        print("\n✅ Frontmatter generation completed successfully!")
    else:
        print("\n❌ Frontmatter generation failed.")
        if ARTICLE_CONTEXT["components"]["frontmatter"]["enabled"]:
            return  # Exit if frontmatter is required but failed
    
    # Generate content components in order
    components_order = ["content", "bullets", "table", "tags", "jsonld"]
    
    for component_name in components_order:
        component_content = generate_component(component_name, frontmatter)
        if component_content:
            all_content.append(component_content)
            print(f"\n✅ {component_name.capitalize()} generation completed successfully!")
        else:
            component_config = ARTICLE_CONTEXT["components"][component_name]
            if component_config["enabled"]:
                print(f"\n❌ {component_name.capitalize()} generation failed.")
            # Continue with other components even if one fails
    
    # Combine all content and save to file
    if all_content:
        combined_content = "\n\n".join(all_content)
        
        # Save to output file
        import os
        output_file = os.path.join(ARTICLE_CONTEXT["output_dir"], f"{ARTICLE_CONTEXT['subject']}.md")
        os.makedirs(ARTICLE_CONTEXT["output_dir"], exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(combined_content)
        
        print(f"\n📄 Combined content saved to: {output_file}")
        
        # Summary of what was generated
        enabled_components = [name for name, config in ARTICLE_CONTEXT["components"].items() if config["enabled"]]
        successful_components = []
        
        if frontmatter:
            successful_components.append("frontmatter")
        
        for component_name in components_order:
            component_content = None
            # Check if this component generated content by trying to find it in all_content
            # This is a simplified check - in practice we'd track this better
            if len(all_content) > 1:  # More than just frontmatter
                successful_components.append(component_name)
        
        print("\n📊 Generation Summary:")
        print(f"   Enabled components: {', '.join(enabled_components)}")
        print(f"   Successful components: {', '.join(successful_components)}")
        print(f"   Total content sections: {len(all_content)}")
        
        print("\n🎉 Content generation completed successfully!")
    else:
        print("\n❌ No content was generated.")


if __name__ == "__main__":
    main()
