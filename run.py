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

from typing import Dict, Any

# =============================================================================
# 🎯 BATCH GENERATION CONFIGURATION 
# =============================================================================
# Edit this section to control generation behavior

BATCH_CONFIG = {
    # Generation mode: "single" for one subject, "multi" for multiple subjects
    "mode": "multi",  # "single" or "multi"
    
    # Single subject configuration (used when mode="single")
    "single_subject": {
        "subject": "Oak wood",
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
    
    # Global AI configuration - applied to all components
    "ai": {
        "provider": "deepseek",  # deepseek, openai, xai, gemini
        "options": {
            "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
            "temperature": 0.7,
            "max_tokens": 4000
        }
    },
    
    # Component configuration - which components to generate (component-specific settings only)
    "components": {
        "frontmatter": {
            "enabled": True,
            "include_website": True,
            "min_words": 300,
            "max_words": 500,
            "temperature": 0.9  # Override global temperature for frontmatter
        },
        "content": {
            "enabled": True,
            "min_words": 200,
            "max_words": 400
        },
        "bullets": {
            "enabled": True,
            "count": 4
        },
        "table": {
            "enabled": True,
            "rows": 5
        },
        "tags": {
            "enabled": True,
            "max_tags": 10,
            "min_tags": 5,
            "tag_categories": [
                "material", "process", "application", "property", "location"
            ]
        },
        "caption": {
            "enabled": True,
            "results_word_count_max": 40,
            "equipment_word_count_max": 40,
            "shape": "component",
            "max_tokens": 1000  # Override global max_tokens for caption
        },
        "jsonld": {
            "enabled": True
        },
        "metatags": {
            "enabled": True,
            "min_tags": 8,
            "max_tags": 15
        },
    },
    
    # Output configuration
    "output": {
        "base_dir": "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/content/components",
        "hierarchy": "flat",  # "flat", "by_article_type", "by_category", or "nested"
        "include_category_metadata": True,  # Include category info in generated files
    },
    
    # File naming patterns for different components and article types
    "filename_patterns": {
        # Default patterns (used for all article types unless overridden)
        "frontmatter": "{subject}.md",           # alumina.md
        "content": "{subject}.md",               # alumina.md
        "bullets": "{subject}.md",               # alumina.md
        "table": "{subject}.md",                 # alumina.md
        "tags": "{subject}.md",                  # alumina.md
        "caption": "{subject}.md",               # alumina.md
        "jsonld": "{subject}.md",                # alumina.md
        "metatags": "{subject}.md",              # alumina.md
        
        # Article-type specific patterns (applied to ALL components for that type)
        "article_type_patterns": {
            "material": "{subject}-laser-cleaning.md",      # zinc-laser-cleaning.md
            "application": "{subject}-applications.md",     # aerospace-cleaning-applications.md
            "region": "{subject}-laser-cleaning.md",        # california-laser-cleaning.md
            "thesaurus": "{subject}-definition.md",         # laser-ablation-definition.md
        },
        
        # Alternative patterns you can use:
        # "{subject}-{component}.md"             # alumina-frontmatter.md
        # "{category}-{subject}.md"              # ceramic-alumina.md
        # "{article_type}-{subject}.md"          # material-alumina.md
        # "{subject}_{component}.md"             # alumina_frontmatter.md
        # "{component}_{subject}.md"             # frontmatter_alumina.md
        
        # Available variables for patterns:
        # {subject}      - Subject name (e.g., "alumina")
        # {category}     - Category name (e.g., "ceramic")
        # {article_type} - Article type (e.g., "material")
        # {component}    - Component name (e.g., "frontmatter")
    }
}

# =============================================================================
# 🔍 SUBJECT DISCOVERY FUNCTIONS
# =============================================================================

def detect_article_type_from_subject(subject: str, category: str = None) -> str:
    """Detect article type from subject name with strict validation.
    
    Args:
        subject: Subject name to analyze
        category: Category context (optional)
        
    Returns:
        Detected article type (material, application, region, thesaurus)
        
    Raises:
        ValueError: If subject type cannot be determined
    """
    import os
    
    # Check available schemas to determine article type
    schemas_dir = "schemas"
    if not os.path.exists(schemas_dir):
        raise ValueError(f"Schemas directory '{schemas_dir}' not found")
    
    available_schemas = []
    for filename in os.listdir(schemas_dir):
        if filename.endswith('.json') and filename not in ['author.json', 'base.json']:
            schema_name = filename[:-5]  # Remove .json
            available_schemas.append(schema_name)
    
    if not available_schemas:
        raise ValueError("No valid schemas found in schemas directory")
    
    # Strict detection based on keywords
    subject_lower = subject.lower()
    
    # Check for application keywords
    application_keywords = ['cleaning', 'restoration', 'preparation', 'processing', 'treatment', 'application']
    if any(keyword in subject_lower for keyword in application_keywords):
        if 'application' not in available_schemas:
            raise ValueError("Subject appears to be application type but no application schema found")
        return 'application'
    
    # Check for region keywords  
    region_keywords = ['california', 'europe', 'asia', 'america', 'county', 'state', 'country', 'region']
    if any(keyword in subject_lower for keyword in region_keywords):
        if 'region' not in available_schemas:
            raise ValueError("Subject appears to be region type but no region schema found")
        return 'region'
    
    # Check for thesaurus/terminology keywords
    thesaurus_keywords = ['ablation', 'fluence', 'terminology', 'definition', 'term']
    if any(keyword in subject_lower for keyword in thesaurus_keywords):
        if 'thesaurus' not in available_schemas:
            raise ValueError("Subject appears to be thesaurus type but no thesaurus schema found")
        return 'thesaurus'
    
    # Default to material only if material schema exists
    if 'material' not in available_schemas:
        raise ValueError("Cannot determine article type and no material schema available")
    return 'material'

def get_article_type_from_schema(schema_path: str) -> str:
    """Extract article type from schema file with strict validation.
    
    Args:
        schema_path: Path to schema JSON file
        
    Returns:
        Article type from schema
        
    Raises:
        FileNotFoundError: If schema file doesn't exist
        ValueError: If schema is invalid or article type cannot be determined
    """
    import json
    import os
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in schema file {schema_path}: {e}")
    
    # Look for article type in schema structure
    for key, value in schema.items():
        if isinstance(value, dict) and 'name' in value:
            return value['name']
    
    # Extract from filename as last resort
    filename = os.path.basename(schema_path)
    if not filename.endswith('.json'):
        raise ValueError(f"Schema file must have .json extension: {schema_path}")
    
    return filename[:-5]  # Remove .json extension

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
    """Get subject list with category information from markdown files.
    
    Args:
        directory_path: Path to directory containing subject files
        
    Returns:
        List of dictionaries with subject info
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If files cannot be parsed or are missing required data
    """
    import os
    import yaml
    
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    subjects_with_categories = []
    
    for filename in os.listdir(directory_path):
        if not filename.endswith('.md'):
            continue
        
        file_path = os.path.join(directory_path, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Could not read file {filename}: {e}")
        
        # Require frontmatter - no fallbacks
        if not content.startswith('---'):
            raise ValueError(f"File {filename} must have frontmatter")
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ValueError(f"File {filename} has malformed frontmatter")
        
        frontmatter_yaml = parts[1].strip()
        try:
            frontmatter = yaml.safe_load(frontmatter_yaml)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filename}: {e}")
        
        # Require category and article_type in frontmatter
        if "category" not in frontmatter:
            raise ValueError(f"File {filename} missing required 'category' in frontmatter")
        if "article_type" not in frontmatter:
            raise ValueError(f"File {filename} missing required 'article_type' in frontmatter")
        
        category = frontmatter["category"]
        article_type = frontmatter["article_type"]
        
        # Extract subjects from bullet list
        content_body = parts[2].strip()
        for line in content_body.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                subject_name = line[2:].strip()
                if subject_name:
                    subjects_with_categories.append({
                        "subject": subject_name,
                        "category": category,
                        "article_type": article_type
                    })
    
    if not subjects_with_categories:
        raise ValueError(f"No valid subjects found in {directory_path}")
    
    return sorted(subjects_with_categories, key=lambda x: (x["category"], x["subject"]))
    
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

def get_component_output_path(component_name: str, subject: str, category: str, article_type: str) -> str:
    """Get output path for a component file with strict validation.
    
    Args:
        component_name: Name of the component
        subject: Subject name
        category: Category of the subject
        article_type: Article type
        
    Returns:
        Output file path
        
    Raises:
        ValueError: If required parameters are missing or invalid
    """
    import os
    
    # Validate required parameters
    if not all([component_name, subject, category, article_type]):
        raise ValueError("All parameters (component_name, subject, category, article_type) are required")
    
    base_dir = BATCH_CONFIG["output"]["base_dir"]
    hierarchy = BATCH_CONFIG["output"]["hierarchy"]
    
    # Build path based on hierarchy setting
    if hierarchy == "flat":
        component_dir = os.path.join(base_dir, component_name)
    elif hierarchy == "by_article_type":
        component_dir = os.path.join(base_dir, article_type, component_name)
    elif hierarchy == "by_category":
        component_dir = os.path.join(base_dir, component_name, category)
    elif hierarchy == "nested":
        component_dir = os.path.join(base_dir, article_type, category, component_name)
    else:
        raise ValueError(f"Invalid hierarchy setting: {hierarchy}")
    
    # Create directory if it doesn't exist
    os.makedirs(component_dir, exist_ok=True)
    
    # Get filename pattern for this component and article type
    if "filename_patterns" not in BATCH_CONFIG:
        raise ValueError("filename_patterns not found in BATCH_CONFIG")
    
    filename_patterns = BATCH_CONFIG["filename_patterns"]
    
    # Check for article-type specific pattern first
    if "article_type_patterns" not in filename_patterns:
        raise ValueError("article_type_patterns not found in filename_patterns")
    
    article_patterns = filename_patterns["article_type_patterns"]
    if article_type in article_patterns:
        pattern = article_patterns[article_type]
    else:
        # Use component-specific pattern
        if component_name not in filename_patterns:
            raise ValueError(f"No filename pattern found for component '{component_name}'")
        pattern = filename_patterns[component_name]
    
    # Create safe versions of variables for filename
    safe_subject = subject.lower().replace(" ", "-").replace("_", "-")
    safe_category = category.lower().replace(" ", "-").replace("_", "-")
    safe_article_type = article_type.lower().replace(" ", "-").replace("_", "-")
    
    # Format filename using pattern
    try:
        filename = pattern.format(
            subject=safe_subject,
            category=safe_category,
            article_type=safe_article_type,
            component=component_name
        )
    except KeyError as e:
        raise ValueError(f"Filename pattern formatting failed, missing key: {e}")
    
    return os.path.join(component_dir, filename)

def save_component_output(component_name: str, subject: str, content: str, category: str, article_type: str) -> str:
    """Save component content to modular output file with strict validation.
    
    Args:
        component_name: Name of the component
        subject: Subject name  
        content: Generated content
        category: Category of the subject
        article_type: Article type
        
    Returns:
        Path to saved file
        
    Raises:
        ValueError: If parameters are invalid or content cannot be saved
    """
    # Validate required parameters
    if not all([component_name, subject, content, category, article_type]):
        raise ValueError("All parameters are required and cannot be empty")
    
    # Get output path
    output_path = get_component_output_path(component_name, subject, category, article_type)
    
    # Add category metadata to content if enabled
    if "output" not in BATCH_CONFIG:
        raise ValueError("output configuration not found in BATCH_CONFIG")
    
    output_config = BATCH_CONFIG["output"]
    if "include_category_metadata" not in output_config:
        raise ValueError("include_category_metadata not found in output configuration")
    
    if output_config["include_category_metadata"]:
        metadata_comment = f"<!-- Category: {category}, Article Type: {article_type}, Subject: {subject} -->\n"
        content = metadata_comment + content
    
    # Write content to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise ValueError(f"Failed to write content to {output_path}: {e}")
    
    return output_path

# =============================================================================
# 🚀 COMPONENT GENERATION FUNCTIONS
# =============================================================================

def load_author_data(author_id: int) -> Dict[str, Any]:
    """Load author data by ID with strict validation.
    
    Args:
        author_id: Author ID to load
        
    Returns:
        Dict with author data
        
    Raises:
        ValueError: If author not found or data invalid
    """
    from components.author.author_service import AuthorService
    
    author_service = AuthorService()
    author_data = author_service.get_author_by_id(author_id)
    
    if not author_data:
        raise ValueError(f"Author with ID {author_id} not found")
    
    # Map author fields to expected format
    required_source_fields = ["name", "country"]
    for field in required_source_fields:
        if field not in author_data:
            raise ValueError(f"Author data missing required field: {field}")
    
    # Return mapped data with expected field names
    return {
        "author_name": author_data["name"],
        "author_country": author_data["country"],
        "author_id": author_data["id"],
        "author_slug": author_data.get("slug", ""),
        "author_title": author_data.get("title", ""),
        "author_bio": author_data.get("bio", ""),
        "author_specialties": author_data.get("specialties", [])
    }

def generate_frontmatter_component(article_context: dict) -> tuple:
    """Generate frontmatter using the configured settings.
    
    Args:
        article_context: Article context for this specific subject
        
    Returns:
        Tuple of (generated frontmatter content, parsed frontmatter data) or (None, None) if failed
    """
    import sys
    import os
    import logging
    import yaml
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # Check if frontmatter is enabled
        component_config = article_context["components"]["frontmatter"]
        if not component_config["enabled"]:
            print("⏭️  Frontmatter generation skipped (disabled)")
            return None, None

        # Load schema for the article type
        schema_path = f"schemas/{article_context['article_type']}.json"
        schema = {}
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                import json
                schema = json.load(f)
        else:
            print(f"❌ Schema file not found: {schema_path}")
            return None, None

        # Initialize frontmatter generator with correct parameters
        from components.frontmatter.generator import FrontmatterGenerator

        # Load author data
        author_data = load_author_data(article_context["author_id"])

        # Get component configuration with AI config merge
        component_config = article_context["components"]["frontmatter"].copy()

        # Merge global AI configuration with component-specific overrides
        global_ai = BATCH_CONFIG["ai"]
        component_config["ai_provider"] = global_ai["provider"]
        component_config["options"] = global_ai["options"].copy()

        # Apply component-specific AI overrides
        for key in ["temperature", "max_tokens", "model"]:
            if key in component_config:
                component_config["options"][key] = component_config.pop(key)

        # Validate generator configuration
        print(f"Frontmatter generator config for subject '{article_context['subject']}':")
        print(f"  Article type: {article_context['article_type']}")
        print(f"  Schema keys: {list(schema.keys())}")
        print(f"  Author: {author_data.get('author_name', '')} ({author_data.get('author_country', '')})")
        print(f"  AI provider: {component_config['ai_provider']}")
        print(f"  Model: {component_config['options'].get('model', '')}")
        print(f"  Temperature: {component_config['options'].get('temperature', '')}")
        print(f"  Max tokens: {component_config['options'].get('max_tokens', '')}")

        # Initialize generator with correct BaseComponent interface
        generator = FrontmatterGenerator(
            subject=article_context["subject"],
            article_type=article_context["article_type"],
            schema=schema,
            author_data=author_data,
            component_config=component_config
        )

        print(f"Generating frontmatter for: {article_context['subject']} ({article_context['article_type']})")
        print(f"Using AI provider: {component_config['ai_provider']} with model: {component_config['options']['model']}")

        # Generate frontmatter
        frontmatter_content = generator.generate()

        if not frontmatter_content or not frontmatter_content.strip():
            print(f"❌ No frontmatter content generated for {article_context['subject']}. Check generator, schema, and config.")
            print(f"  Generator config: {component_config}")
            print(f"  Schema: {schema}")
            return None, None

        # Parse the YAML content to validate it
        try:
            yaml_content = frontmatter_content.strip()
            frontmatter_data = yaml.safe_load(yaml_content)
            
            if not frontmatter_data or not isinstance(frontmatter_data, dict):
                print(f"❌ Invalid frontmatter data for {article_context['subject']}. Not a valid YAML dictionary.")
                return None, None
                
            print("\n" + "="*60)
            print("VALIDATED FRONTMATTER:")
            print("="*60)
            print(frontmatter_content)
            print("="*60)
            
            return frontmatter_content, frontmatter_data
        except yaml.YAMLError as e:
            print(f"❌ Failed to parse frontmatter YAML for {article_context['subject']}: {e}")
            return None, None

    except Exception as e:
        print(f"❌ Error generating frontmatter: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

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
    import yaml
    
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
        
        # Load author data
        author_data = load_author_data(article_context["author_id"])
        
        # Get component configuration with AI config merge
        component_config = article_context["components"][component_name].copy()
        
        # Merge global AI configuration with component-specific overrides
        global_ai = BATCH_CONFIG["ai"]
        component_config["ai_provider"] = global_ai["provider"]
        component_config["options"] = global_ai["options"].copy()
        
        # Apply component-specific AI overrides
        for key in ["temperature", "max_tokens", "model"]:
            if key in component_config:
                component_config["options"][key] = component_config.pop(key)
        
        # Import and initialize the appropriate generator dynamically
        try:
            # Construct the import path and class name dynamically
            component_module = f"components.{component_name}.generator"
            generator_class_name = f"{component_name.capitalize()}Generator"
            
            # Dynamic import
            import importlib
            module = importlib.import_module(component_module)
            generator_class = getattr(module, generator_class_name)
            
            # Initialize generator
            generator = generator_class(
                subject=article_context["subject"],
                article_type=article_context["article_type"],
                schema=schema,
                author_data=author_data,
                component_config=component_config
            )
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to load generator for component '{component_name}': {e}")
        
        # Set frontmatter data if available
        if frontmatter_content:
            try:
                # Frontmatter should already be validated at this point, but let's be safe
                yaml_content = frontmatter_content.strip()
                frontmatter_data = yaml.safe_load(yaml_content)
                
                if frontmatter_data and isinstance(frontmatter_data, dict):
                    generator._frontmatter_data = frontmatter_data
                else:
                    raise ValueError(f"Invalid frontmatter data structure for {component_name}")
            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse frontmatter for {component_name}: {e}")
        else:
            # No frontmatter provided - fail for components that require it
            if component_name in ["jsonld", "table", "content"]:
                raise ValueError(f"Frontmatter data is required for {component_name} generation")
        
        print(f"Generating {component_name} for: {article_context['subject']} ({article_context['article_type']})")
        print(f"Using AI provider: {component_config['ai_provider']} with model: {component_config['options']['model']}")
        
        # Generate content with retry mechanism
        max_attempts = 3
        attempt = 1
        content = None
        last_error = None
        
        while attempt <= max_attempts and content is None:
            try:
                if attempt > 1:
                    print(f"Retry attempt {attempt}/{max_attempts} for {component_name}...")
                    
                    # Add retry-specific instructions for known validation issues
                    if component_name == "caption" and last_error and "word_count" in str(last_error).lower():
                        # For caption word count issues, modify the component config with more specific instructions
                        if "options" in component_config and "messages" in component_config["options"]:
                            # Add a message with specific instructions about word counts
                            word_count_error = str(last_error)
                            retry_message = {
                                "role": "user", 
                                "content": f"The previous generation failed validation: {word_count_error}. Please regenerate with SHORTER sections to meet word count requirements."
                            }
                            component_config["options"]["messages"].append(retry_message)
                    
                    # For JSON-LD issues, add more specific instructions
                    if component_name == "jsonld" and last_error and "json" in str(last_error).lower():
                        if "options" in component_config and "messages" in component_config["options"]:
                            retry_message = {
                                "role": "user", 
                                "content": f"The previous generation failed: {last_error}. Please output valid JSON-LD in a proper code block."
                            }
                            component_config["options"]["messages"].append(retry_message)
                    
                    # For tags issues, add specific instructions
                    if component_name == "tags" and last_error:
                        if "options" in component_config and "messages" in component_config["options"]:
                            retry_message = {
                                "role": "user", 
                                "content": "The previous generation failed. Please output ONLY a comma-separated list of tags (e.g., 'Tag1, Tag2, Tag3'). No other text, explanations, or formatting."
                            }
                            component_config["options"]["messages"].append(retry_message)
                    
                    # For metatags issues, add specific instructions
                    if component_name == "metatags" and last_error:
                        if "options" in component_config and "messages" in component_config["options"]:
                            retry_message = {
                                "role": "user", 
                                "content": "The previous generation failed. Please output ONLY HTML meta tags (e.g., '<meta name=\"description\" content=\"...\">'). No other HTML elements, explanations, or formatting."
                            }
                            component_config["options"]["messages"].append(retry_message)
                
                # Generate content
                content = generator.generate()
                
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt}/{max_attempts} failed: {str(e)}")
                attempt += 1
                
                if attempt > max_attempts:
                    print(f"All {max_attempts} attempts failed for {component_name} generation.")
                    raise e
        
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
        if "category" not in config:
            category = None
        else:
            category = config["category"]
        subjects_to_process = [(config["subject"], config["article_type"], category)]
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
    
    # Get enabled components (folders)
    enabled_components = [name for name, config in BATCH_CONFIG["components"].items() if config.get("enabled", False)]
    print(f"Enabled components: {', '.join(enabled_components)}")

    # Make sure frontmatter is the first component to process if enabled
    if "frontmatter" in enabled_components:
        enabled_components.remove("frontmatter")
        enabled_components.insert(0, "frontmatter")

    # Track output parity for all folders
    output_tracker = {comp: set() for comp in enabled_components}
    total_generated = 0
    successful_components = set()

    # Process each subject
    for subject, subject_article_type, category in subjects_to_process:
        print(f"\n--- Processing: {subject} ---")
        article_context = create_article_context(subject, subject_article_type, author_id, category)
        
        # FIRST STEP: Always generate frontmatter first and validate it
        frontmatter_content = None
        frontmatter_data = None
        
        # Check if frontmatter is enabled
        frontmatter_enabled = BATCH_CONFIG["components"]["frontmatter"].get("enabled", False)
        
        if frontmatter_enabled:
            print(f"Generating frontmatter for: {subject} (prerequisite for other components)")
            frontmatter_content, frontmatter_data = generate_frontmatter_component(article_context)
            
            # Save frontmatter output regardless of success
            if frontmatter_content:
                category_for_output = article_context.get("category")
                output_path = save_component_output("frontmatter", subject, frontmatter_content, category_for_output, subject_article_type)
                print(f"✅ Frontmatter saved to: {output_path}")
                output_tracker["frontmatter"].add(subject)
                total_generated += 1
                successful_components.add("frontmatter")
            else:
                # Create empty frontmatter file to maintain folder parity
                content = f"<!-- Category: {category}, Article Type: {subject_article_type}, Subject: {subject} -->\n"
                content += f"<!-- No valid frontmatter generated for {subject} -->\n"
                category_for_output = article_context.get("category")
                output_path = save_component_output("frontmatter", subject, content, category_for_output, subject_article_type)
                print(f"⚠️ Empty frontmatter placeholder saved to: {output_path}")
                output_tracker["frontmatter"].add(subject)
        
        # SECOND STEP: Only generate other components if frontmatter was successfully generated
        if frontmatter_enabled and not frontmatter_data:
            print(f"❌ Skipping remaining components for {subject} due to frontmatter generation failure")
            
            # Create empty placeholder files for all other components to maintain folder parity
            for component_name in enabled_components:
                if component_name != "frontmatter":
                    content = f"<!-- Category: {category}, Article Type: {subject_article_type}, Subject: {subject} -->\n"
                    content += f"<!-- No content generated for {subject} ({component_name}) due to frontmatter failure -->\n"
                    category_for_output = article_context.get("category")
                    output_path = save_component_output(component_name, subject, content, category_for_output, subject_article_type)
                    print(f"⚠️ Empty {component_name} placeholder saved to: {output_path}")
                    output_tracker[component_name].add(subject)
            
            # Skip to next subject
            continue
        
        # Process remaining components now that we have valid frontmatter
        for component_name in enabled_components:
            # Skip frontmatter as we've already handled it
            if component_name == "frontmatter":
                continue
                
            try:
                print(f"Generating {component_name} for: {subject} ({subject_article_type})")
                content = generate_component(component_name, article_context, frontmatter_content)

                # Guarantee output file for every folder, even if content is None
                if content is None:
                    content = f"<!-- Category: {category}, Article Type: {subject_article_type}, Subject: {subject} -->\n"
                    content += f"<!-- No content generated for {subject} ({component_name}) -->\n"

                category_for_output = article_context.get("category")
                output_path = save_component_output(component_name, subject, content, category_for_output, subject_article_type)
                print(f"✅ {component_name.capitalize()} saved to: {output_path}")
                output_tracker[component_name].add(subject)
                total_generated += 1
                successful_components.add(component_name)
            except Exception as e:
                print(f"❌ Error generating {component_name}: {str(e)}")
                
                # Create empty placeholder file to maintain folder parity
                content = f"<!-- Category: {category}, Article Type: {subject_article_type}, Subject: {subject} -->\n"
                content += f"<!-- Error generating {component_name}: {str(e)} -->\n"
                category_for_output = article_context.get("category")
                output_path = save_component_output(component_name, subject, content, category_for_output, subject_article_type)
                print(f"⚠️ Error placeholder saved to: {output_path}")
                output_tracker[component_name].add(subject)

    # Parity check: ensure every folder has output for every subject
    print("\n📊 Generation Summary:")
    print(f"   Mode: {BATCH_CONFIG['mode']}")
    print(f"   Subjects processed: {len(subjects_to_process)}")
    print(f"   Enabled components: {', '.join(enabled_components)}")
    print(f"   Successful components: {', '.join(successful_components)}")
    print(f"   Total content sections: {total_generated}")
    for comp in enabled_components:
        missing = set([s[0] for s in subjects_to_process]) - output_tracker[comp]
        if missing:
            print(f"   ⚠️ {comp} missing subjects: {', '.join(missing)}")
        else:
            print(f"   ✅ {comp} has output for all subjects.")

    print("\n🎉 Content generation completed successfully!")

if __name__ == "__main__":
    run_batch_generation()
