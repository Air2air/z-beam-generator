#!/usr/bin/env python3
"""
Z-Beam content generation system entry point.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. CONFIGURATION PRECEDENCE: BATCH_CONFIG is the primary configuration source
2. NO CACHING: No caching of resources, data, or objects anywhere in the system
3. FRESH LOADING: Always load fresh data on each access
4. BATCH_CONFIG DRIVEN: All configuration derives from BATCH_CONFIG
5. DYNAMIC COMPONENTS: Use registry to discover and load components
6. ERROR HANDLING: Provide clear error messages with proper logging
7. ENVIRONMENT VARIABLES: Load environment variables from .env file
8. API KEY MANAGEMENT: Check for required API keys and warn if missing
9. MODULAR OUTPUT: Generate components in separate folders for flexible React consumption
10. BATCH PROCESSING: Support generating single components across multiple subjects
"""

# =============================================================================
# 🎯 BATCH GENERATION CONFIGURATION 
# =============================================================================
# Edit this section to control generation behavior

BATCH_CONFIG = {
    # Generation mode: "single" for one subject, "multi" for multiple subjects
    "mode": "multi",  # "single" or "multi"
    
    # Single subject configuration (used when mode="single")
    "single_subject": {
        "subject": "Silicon",
        "article_type": "material",  # application, material, region, or thesaurus
        "author_id": 1,  # 1: Taiwan, 2: Italy, 3: USA, 4: Indonesia
        "category": "semiconductor",  # Optional: specify category for hierarchy
    },
    
    # Multi-subject configuration (used when mode="multi")
    "multi_subject": {
        "author_id": 1,  # Use this author for all subjects
        "subject_source": "lists",  # Directory to discover all subjects from all categories
        "limit": 2,  # Limit to first X subjects (set to None for all subjects)
    },
    
    # Component configuration - which components to generate
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
            "enabled": False,  # Disable for faster testing
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
            "enabled": False,  # Disable for faster testing
            "count": 10,
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            },  
        },
        "table": {
            "enabled": False,  # Disable for faster testing
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
        "caption": {
            "enabled": False,  # Disable for faster testing
            "results_word_count_max": 120,
            "equipment_word_count_max": 60,
            "shape": "component",  # Default shape, can be overridden
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 1000
            },  
        },
        "jsonld": {
            "enabled": False,  # Disable for faster testing
            "ai_provider": "deepseek",  # deepseek, openai, xai, gemini
            "options": {
                "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
                "temperature": 0.7,
                "max_tokens": 4000
            },  
        },
    },
    
    # Output configuration
    "output": {
        "base_dir": "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/content/components",
        "hierarchy": "flat",  # "flat", "by_article_type", "by_category", or "nested"
        "include_category_metadata": True,  # Include category info in generated files
    }
}

# =============================================================================
# 🔍 SUBJECT DISCOVERY FUNCTIONS
# =============================================================================

def get_subjects_from_directory(directory_path: str) -> list:
    """Get subject list from markdown files in a directory.
    
    Args:
        directory_path: Path to directory containing subject files
        
    Returns:
        List of subject names (without .md extension)
    """
    import os
    
    subjects = []
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith('.md'):
                subject = filename[:-3]  # Remove .md extension
                subjects.append(subject)
    
    return sorted(subjects)

def get_subjects_with_categories_from_directory(directory_path: str) -> list:
    """Get subject list with category information from markdown files in a directory.
    
    Args:
        directory_path: Path to directory containing subject files
        
    Returns:
        List of dictionaries with subject info: [{"subject": "aluminum", "category": "metal", "article_type": "material"}, ...]
    """
    import os
    import yaml
    
    subjects_with_categories = []
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith('.md'):
                file_path = os.path.join(directory_path, filename)
                
                # Read file and extract frontmatter
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file has frontmatter
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            frontmatter_yaml = parts[1].strip()
                            frontmatter = yaml.safe_load(frontmatter_yaml)
                            
                            # Extract subjects from bullet list
                            content_body = parts[2].strip()
                            for line in content_body.split('\n'):
                                line = line.strip()
                                if line.startswith('- '):
                                    subject_name = line[2:].strip()
                                    if subject_name:
                                        subjects_with_categories.append({
                                            "subject": subject_name,
                                            "category": frontmatter.get("category", filename[:-3]),  # Fallback to filename
                                            "article_type": frontmatter.get("article_type", "material")
                                        })
                        else:
                            # No frontmatter, fallback to old method
                            category = filename[:-3]  # Remove .md extension
                            # Parse subjects from bullet list
                            for line in content.split('\n'):
                                line = line.strip()
                                if line.startswith('- '):
                                    subject_name = line[2:].strip()
                                    if subject_name:
                                        subjects_with_categories.append({
                                            "subject": subject_name,
                                            "category": category,
                                            "article_type": "material"
                                        })
                    
                except Exception as e:
                    print(f"Warning: Could not parse {filename}: {e}")
                    continue
    
    return sorted(subjects_with_categories, key=lambda x: (x["category"], x["subject"]))

def create_article_context(subject: str, article_type: str, author_id: int, category: str = None) -> dict:
    """Create article context for a specific subject.
    
    Args:
        subject: Subject name
        article_type: Type of article
        author_id: Author ID
        category: Category of the subject (optional)
        
    Returns:
        Article context dictionary
    """
    return {
        "subject": subject,
        "article_type": article_type,
        "author_id": author_id,
        "category": category,
        "components": BATCH_CONFIG["components"].copy(),
        "output_dir": BATCH_CONFIG["output"]["base_dir"]
    }

# =============================================================================
# 🏗️ MODULAR OUTPUT FUNCTIONS
# =============================================================================

def get_component_output_path(component_name: str, subject: str, category: str = None, article_type: str = "material") -> str:
    """Get output path for a component file.
    
    Args:
        component_name: Name of the component
        subject: Subject name
        category: Category of the subject (optional)
        article_type: Article type (optional)
        
    Returns:
        Output file path
    """
    import os
    
    base_dir = BATCH_CONFIG["output"]["base_dir"]
    hierarchy = BATCH_CONFIG["output"].get("hierarchy", "flat")
    
    # Build path based on hierarchy setting
    if hierarchy == "flat":
        # output/tags/silicon.md
        component_dir = os.path.join(base_dir, component_name)
    elif hierarchy == "by_article_type":
        # output/material/tags/silicon.md
        component_dir = os.path.join(base_dir, article_type, component_name)
    elif hierarchy == "by_category":
        # output/tags/semiconductor/silicon.md
        component_dir = os.path.join(base_dir, component_name, category or "uncategorized")
    elif hierarchy == "nested":
        # output/material/semiconductor/tags/silicon.md
        component_dir = os.path.join(base_dir, article_type, category or "uncategorized", component_name)
    else:
        # Default to flat
        component_dir = os.path.join(base_dir, component_name)
    
    # Create directory if it doesn't exist
    os.makedirs(component_dir, exist_ok=True)
    
    # Create safe filename
    safe_subject = subject.lower().replace(" ", "-").replace("_", "-")
    return os.path.join(component_dir, f"{safe_subject}.md")

def save_component_output(component_name: str, subject: str, content: str, category: str = None, article_type: str = "material") -> str:
    """Save component content to modular output file.
    
    Args:
        component_name: Name of the component
        subject: Subject name  
        content: Generated content
        category: Category of the subject (optional)
        article_type: Article type (optional)
        
    Returns:
        Path to saved file
    """
    # Add category metadata to content if enabled
    if BATCH_CONFIG["output"].get("include_category_metadata", False) and category:
        # Add metadata comment at the top
        metadata_comment = f"<!-- Category: {category} | Article Type: {article_type} | Subject: {subject} -->\n"
        content = metadata_comment + content
    
    output_path = get_component_output_path(component_name, subject, category, article_type)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path

# =============================================================================
# 🚀 COMPONENT GENERATION FUNCTIONS
# =============================================================================

def generate_frontmatter_component(article_context: dict) -> str:
    """Generate frontmatter using the configured settings.
    
    Args:
        article_context: Article context for this specific subject
        
    Returns:
        Generated frontmatter content or None if failed
    """
    import sys
    import os
    import logging
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # Check if frontmatter is enabled
        component_config = article_context["components"]["frontmatter"]
        if not component_config["enabled"]:
            print("⏭️  Frontmatter generation skipped (disabled)")
            return None
        
        # Load schema for the article type
        schema_path = f"schemas/{article_context['article_type']}.json"
        schema = {}
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                import json
                schema = json.load(f)
        
        # Initialize frontmatter generator
        from components.frontmatter.generator import FrontmatterGenerator
        
        # Create context for the generator
        generator_context = article_context.copy()
        
        # Generate website URL - simplified
        subject_slug = article_context["subject"].replace(" ", "-").lower()
        article_type = article_context["article_type"]
        website_url = f"https://www.z-beam.com/{subject_slug}-{article_type}"
        
        # Ensure required fields are present
        generator_context.update({
            "subject": article_context["subject"],
            "article_type": article_context["article_type"],
            "author_id": article_context["author_id"],
            "ai_provider": component_config["ai_provider"],
            "options": component_config["options"],
            "website_url": website_url  # Pass the constructed URL
        })
        
        # Initialize generator
        generator = FrontmatterGenerator(
            context=generator_context,
            schema=schema,
            ai_provider=component_config["ai_provider"]
        )
        
        print(f"Generating frontmatter for: {article_context['subject']} ({article_context['article_type']})")
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

def generate_component(component_name: str, article_context: dict, frontmatter_content: str = None) -> str:
    """Generate content for a specific component.
    
    Args:
        component_name: Name of the component to generate
        article_context: Article context for this specific subject
        frontmatter_content: Previously generated frontmatter content for context
        
    Returns:
        Generated content or None if failed
    """
    import sys
    import os
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        # Get component config
        component_config = article_context["components"][component_name]
        
        if not component_config["enabled"]:
            print(f"⏭️  {component_name.capitalize()} generation skipped (disabled)")
            return None
        
        # Load schema for the article type
        schema_path = f"schemas/{article_context['article_type']}.json"
        schema = {}
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                import json
                schema = json.load(f)
        
        # Create context for the generator
        generator_context = article_context.copy()
        
        # Ensure required fields are present
        generator_context.update({
            "subject": article_context["subject"],
            "article_type": article_context["article_type"],
            "author_id": article_context["author_id"],
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
        elif component_name == "caption":
            from components.caption.generator import CaptionGenerator
            generator = CaptionGenerator(
                context=generator_context,
                schema=schema,
                ai_provider=component_config["ai_provider"]
            )
        else:
            raise ValueError(f"Unknown component: {component_name}")
        
        # Parse and set frontmatter data if available
        if frontmatter_content:
            try:
                import yaml
                
                # Extract YAML content from frontmatter (remove --- delimiters)
                yaml_content = frontmatter_content.strip()
                if yaml_content.startswith('---'):
                    yaml_content = yaml_content[3:]
                if yaml_content.endswith('---'):
                    yaml_content = yaml_content[:-3]
                yaml_content = yaml_content.strip()
                
                # Parse the YAML content
                frontmatter_data = yaml.safe_load(yaml_content)
                if frontmatter_data:
                    generator.set_frontmatter(frontmatter_data)
            except Exception as e:
                print(f"Warning: Failed to parse frontmatter for {component_name}: {e}")
        
        print(f"Generating {component_name} for: {article_context['subject']} ({article_context['article_type']})")
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

# =============================================================================
# 🔧 ENVIRONMENT SETUP
# =============================================================================

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

# =============================================================================
# 🚀 MAIN GENERATION FUNCTIONS
# =============================================================================

def run_batch_generation():
    """Run batch generation based on BATCH_CONFIG."""
    import sys
    import os
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Setup environment
    setup_environment()
    
    print("Z-Beam content generation system started.")
    
    if BATCH_CONFIG["mode"] == "single":
        # Single subject generation
        config = BATCH_CONFIG["single_subject"]
        subjects_to_process = [(config["subject"], config["article_type"], config.get("category"))]
        author_id = config["author_id"]
        
        print(f"Single Mode: {config['subject']} ({config['article_type']})")
        
    elif BATCH_CONFIG["mode"] == "multi":
        # Multi-subject generation for all enabled components
        config = BATCH_CONFIG["multi_subject"]
        author_id = config["author_id"]
        
        # Get all subjects with their categories and article types
        if config["subject_source"] == "lists":
            subjects_with_info = get_subjects_with_categories_from_directory("lists")
        else:
            subjects_with_info = []
        
        # Apply limit if specified
        limit = config.get("limit")
        if limit is not None:
            subjects_to_process = [(s["subject"], s["article_type"], s["category"]) for s in subjects_with_info[:limit]]
        else:
            subjects_to_process = [(s["subject"], s["article_type"], s["category"]) for s in subjects_with_info]
            
        print(f"Multi Mode: {len(subjects_to_process)} subjects (limit: {limit or 'none'})")
        
    else:
        raise ValueError(f"Invalid mode: {BATCH_CONFIG['mode']}")
    
    # Get enabled components
    enabled_components = [name for name, config in BATCH_CONFIG["components"].items() 
                         if config.get("enabled", False)]
    
    print(f"Enabled components: {', '.join(enabled_components)}")
    
    # Process each subject
    total_generated = 0
    successful_components = []
    
    for subject, subject_article_type, category in subjects_to_process:
        print(f"\n--- Processing: {subject} ---")
        
        # Create article context for this subject  
        article_context = create_article_context(subject, subject_article_type, author_id, category)
        
        # Generate each enabled component
        frontmatter_content = None
        
        for component_name in enabled_components:
            try:
                print(f"Generating {component_name} for: {subject} ({subject_article_type})")
                
                # Generate the component
                if component_name == "frontmatter":
                    content = generate_frontmatter_component(article_context)
                    frontmatter_content = content  # Store for other components
                else:
                    content = generate_component(component_name, article_context, frontmatter_content)
                
                if content:
                    # Save to modular file structure with category info
                    category = article_context.get("category")
                    output_path = save_component_output(component_name, subject, content, category, subject_article_type)
                    print(f"✅ {component_name.capitalize()} saved to: {output_path}")
                    
                    total_generated += 1
                    if component_name not in successful_components:
                        successful_components.append(component_name)
                else:
                    print(f"❌ {component_name.capitalize()} generation failed.")
                    
            except Exception as e:
                print(f"❌ Error generating {component_name}: {str(e)}")
    
    # Summary
    print("\n📊 Generation Summary:")
    print(f"   Mode: {BATCH_CONFIG['mode']}")
    print(f"   Subjects processed: {len(subjects_to_process)}")
    print(f"   Enabled components: {', '.join(enabled_components)}")
    print(f"   Successful components: {', '.join(successful_components)}")
    print(f"   Total content sections: {total_generated}")
    
    print("\n🎉 Content generation completed successfully!")

if __name__ == "__main__":
    run_batch_generation()
