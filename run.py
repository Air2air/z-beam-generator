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
            "enabled": False,
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
            "enabled": False,
            "count": 10,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            },  
        },
        "table": {
            "enabled": False,
            "rows": 5,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            },  
        },
        "tags": {
            "enabled": False,
            "count": 10,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            }, 
        },
        "jsonld": {
            "enabled": False,
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
        # Load schema for the article type
        schema_path = f"schemas/{ARTICLE_CONTEXT['article_type']}.json"
        schema = {}
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                import json
                schema = json.load(f)
        
        # Initialize frontmatter generator
        from components.frontmatter.generator import FrontmatterGenerator
        
        # Get component config from ARTICLE_CONTEXT
        component_config = ARTICLE_CONTEXT["components"]["frontmatter"]
        
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
        
        # Save to output file
        output_file = os.path.join(ARTICLE_CONTEXT["output_dir"], f"{ARTICLE_CONTEXT['subject']}.md")
        os.makedirs(ARTICLE_CONTEXT["output_dir"], exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(frontmatter_content)
        
        print(f"\nFrontmatter saved to: {output_file}")
        
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
    
    # Generate frontmatter
    frontmatter = generate_frontmatter()
    
    if frontmatter:
        print("\n✅ Frontmatter generation completed successfully!")
    else:
        print("\n❌ Frontmatter generation failed.")


if __name__ == "__main__":
    main()
