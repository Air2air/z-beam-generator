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

import argparse
from typing import Dict, Any
import os
import yaml

# =============================================================================
# 🎯 BATCH GENERATION CONFIGURATION 
# =============================================================================
# Edit this section to control generation behavior

BATCH_CONFIG = {
    # Generation mode: "single" for one subject, "multi" for multiple subjects
    "mode": "multi",  # "single" or "multi"
    
    # Single subject configuration (used when mode="single")
    "single_subject": {
        "subject": "Quartzite",
        "article_type": "material",  # application, material, region, or thesaurus
        "author_id": 1,  # 1: Taiwan, 2: Italy, 3: USA, 4: Indonesia
        "category": "stone",  # Optional: specify category for hierarchy
    },
    
    # Multi-subject configuration (used when mode="multi")
    "multi_subject": {
        "author_id": 1,  # Use this author for all subjects
        "subject_source": "lists",  # Directory to discover all subjects from all categories
        "limit": 5,  # Range [start_idx, end_idx] to process items by index (or a single number for first N items, None for all subjects)
    },
    
    # Global AI configuration - applied to all components
    "ai": {
        "provider": "deepseek",  # deepseek, openai, xai, gemini
        "options": {
            "model": "deepseek-chat", # deepseek-chat (88), "GPT-4o" (76), "grok-3-latest" (62), "gemini-1.5-flash"
            "max_tokens": 4000
        }
    },
    
    # Component configuration - which components to generate (component-specific settings only)
    "components": {
        "frontmatter": {
            "enabled": True,  # Frontmatter is just another component
            "min_words": 300,
            "max_words": 500,
            "temperature": 0.9  # Override global temperature for frontmatter
        },
        "content": {
            "enabled": True,
            "min_words": 200,
            "max_words": 400,
            "temperature": 0.7,  # Balanced creativity for main content
            "inline_links": {
                "max_links": 5
            }
        },
        "bullets": {
            "enabled": True,
            "count": 4,
            "temperature": 0.6  # Slightly lower for more focused bullet points
        },
        "table": {
            "enabled": True,
            "rows": 5,
            "temperature": 0.4,  # Lower temperature for more consistent, structured table data
            "table_keys": ["Material", "Density", "Melting Point", "Laser Type", "Applications"],
            "skip_sections": [
                "Application Examples",
                "Author Information",
                "Benefits",
                "Compatible Materials",
                "Data Table",
                "Keywords",
                "Geographic Distribution",
                "Location Details",
                "Technical Specifications"
            ]
        },
        "tags": {
            "enabled": True,
            "temperature": 0.8,  # Higher for more diverse tag generation
            "max_tags": 10,
            "min_tags": 5,
            "tag_categories": [
                "material", "process", "application", "property", "location"
            ]
        },
        "caption": {
            "enabled": True,
            "before_word_count_max": 40,
            "equipment_word_count_max": 40,
            "shape": "component",
            "temperature": 0.75,  # Slightly higher for creative but controlled captions
            "max_tokens": 1000  # Override global max_tokens for caption
        },
        "jsonld": {
            "enabled": True,
            "temperature": 0.3  # Low temperature for structured JSON data
        },
        "metatags": {
            "enabled": True,
            "min_tags": 8,
            "max_tags": 20,
            "temperature": 0.5  # Moderate temperature for balanced metadata generation
        },
    },
    
    # Output configuration
    "output": {
        "base_dir": "content/components",
        "hierarchy": "flat",  # "flat", "by_article_type", "by_category", or "nested"
    },
    
    # File naming patterns for different components and article types
    "filename_patterns": {
        # Default patterns (used for all article types unless overridden)
        "frontmatter": "{subject}",           # alumina
        "content": "{subject}",               # alumina
        "bullets": "{subject}",               # alumina
        "table": "{subject}",                 # alumina
        "tags": "{subject}",                  # alumina
        "caption": "{subject}",               # alumina
        "jsonld": "{subject}",                # alumina
        "metatags": "{subject}",              # alumina
        
        # Article-type specific patterns (applied to ALL components for that type)
        "article_type_patterns": {
            "material": "{subject}-laser-cleaning",      # zinc-laser-cleaning
            "application": "{subject}-applications",     # aerospace-cleaning-applications
            "region": "{subject}-laser-cleaning",        # california-laser-cleaning
            "thesaurus": "{link}-definition",            # laser-ablation-definition
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
        # {link}         - The term itself for thesaurus entries (e.g., "laser-ablation")
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

def get_subjects_from_consolidated_yaml(yaml_path: str) -> list:
    """Get subject list from consolidated materials.yaml file.
    
    Args:
        yaml_path: Path to consolidated materials.yaml file
        
    Returns:
        List of dictionaries with subject info
        
    Raises:
        FileNotFoundError: If YAML file doesn't exist
        ValueError: If YAML cannot be parsed or is missing required structure
    """
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Consolidated YAML file not found: {yaml_path}")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {yaml_path}: {e}")
    except Exception as e:
        raise ValueError(f"Could not read YAML file {yaml_path}: {e}")
    
    if not isinstance(yaml_data, dict) or 'materials' not in yaml_data:
        raise ValueError(f"YAML file {yaml_path} must contain a 'materials' key with category data")
    
    subjects_with_categories = []
    materials_data = yaml_data['materials']
    
    for category, category_info in materials_data.items():
        if not isinstance(category_info, dict):
            continue
            
        description = category_info.get('description', f"{category.title()} materials for laser cleaning applications")
        article_type = category_info.get('article_type', 'material')
        items = category_info.get('items', [])
        
        for item in items:
            if isinstance(item, str) and item.strip():
                subjects_with_categories.append({
                    "subject": item.strip(),
                    "category": category,
                    "article_type": article_type
                })
    
    if not subjects_with_categories:
        raise ValueError(f"No valid subjects found in {yaml_path}")
    
    return sorted(subjects_with_categories, key=lambda x: (x["category"], x["subject"]))

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
    from components.base.utils.slug_utils import SlugUtils
    safe_subject = SlugUtils.create_subject_slug(subject)
    safe_category = SlugUtils.create_category_slug(category)
    safe_article_type = SlugUtils.create_article_type_slug(article_type)
    
    # For thesaurus entries, the link is the term itself
    if article_type == "thesaurus":
        # Use the subject as the word/term for the filename
        safe_link = safe_subject
        
        # Future enhancement: Extract term from frontmatter if available
        # This would allow using a normalized term from the data rather than the subject
        # if frontmatter_data and "term" in frontmatter_data:
        #     term = frontmatter_data["term"].lower().replace(" ", "-").replace("_", "-")
        #     safe_link = term
    else:
        safe_link = safe_subject
    
    # Format filename using pattern
    try:
        filename = pattern.format(
            subject=safe_subject,
            category=safe_category,
            article_type=safe_article_type,
            component=component_name,
            link=safe_link
        )
        
        # Add .md extension if not present and not a thesaurus definition
        if not filename.endswith('.md') and article_type != "thesaurus":
            filename += '.md'
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
    
    # Ensure no HTML comments are in the content
    import re
    content = re.sub(r'<!--.*?-->\n?', '', content)
    
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
        "author_slug": author_data["slug"] if "slug" in author_data else "",
        "author_title": author_data["title"] if "title" in author_data else "",
        "author_bio": author_data["bio"] if "bio" in author_data else "",
        "author_specialties": author_data["specialties"] if "specialties" in author_data else []
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
        
        # Add category to component config if available
        if "category" in article_context:
            component_config["category"] = article_context["category"]
        else:
            component_config["category"] = ""

        # Apply component-specific AI overrides
        for key in ["temperature", "max_tokens", "model"]:
            if key in component_config:
                component_config["options"][key] = component_config.pop(key)

        # Validate generator configuration
        print(f"Frontmatter generator config for subject '{article_context['subject']}':")
        print(f"  Article type: {article_context['article_type']}")
        print(f"  Schema keys: {list(schema.keys())}")
        
        # Prepare author display values
        author_name = ""
        author_country = ""
        if "author_name" in author_data:
            author_name = author_data["author_name"]
        if "author_country" in author_data:
            author_country = author_data["author_country"]
        print(f"  Author: {author_name} ({author_country})")
        
        print(f"  AI provider: {component_config['ai_provider']}")
        
        # Prepare option display values
        model = ""
        temperature = ""
        max_tokens = ""
        if "model" in component_config['options']:
            model = component_config['options']["model"]
        if "temperature" in component_config['options']:
            temperature = component_config['options']["temperature"]
        if "max_tokens" in component_config['options']:
            max_tokens = component_config['options']["max_tokens"]
        
        print(f"  Model: {model}")
        print(f"  Temperature: {temperature}")
        print(f"  Max tokens: {max_tokens}")

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

        # Generate frontmatter with category information
        # Set category as an attribute on the generator
        if "category" in article_context:
            generator.category = article_context["category"]
        frontmatter_content = generator.generate()

        if not frontmatter_content or not frontmatter_content.strip():
            print(f"❌ No frontmatter content generated for {article_context['subject']}. Check generator, schema, and config.")
            print(f"  Generator config: {component_config}")
            print(f"  Schema: {schema}")
            return None, None

        # Parse the YAML content to validate it
        try:
            # Extract YAML content between --- delimiters, ignoring HTML comments
            if "---" in frontmatter_content:
                # Split by --- to get the content between delimiters
                parts = frontmatter_content.split("---", 2)
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                else:
                    yaml_content = frontmatter_content.strip()
            else:
                yaml_content = frontmatter_content.strip()
                
            frontmatter_data = yaml.safe_load(yaml_content)
            
            if not frontmatter_data or not isinstance(frontmatter_data, dict):
                print(f"❌ Invalid frontmatter data for {article_context['subject']}. Not a valid YAML dictionary.")
                return None, None
                
            # Store the frontmatter data for other components to use
            article_context["frontmatter_data"] = frontmatter_data
                
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

def generate_component(component_name: str, article_context: dict) -> str:
    """Generate content for a specific component.
    
    Args:
        component_name: Name of the component to generate
        article_context: Article context for this specific subject
        
    Returns:
        Generated content or None if failed
    """
    import sys
    import os
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        # Get component config
        if isinstance(article_context["components"], list):
            # We're running with --component flag
            # Create a default config since we don't have the actual config
            component_config = {
                "enabled": True,
                "temperature": 0.7,
                "max_tokens": 1000,
                "ai_provider": BATCH_CONFIG["ai"]["provider"],
                "options": BATCH_CONFIG["ai"]["options"].copy()
            }
            
            # Add specific config for certain components
            if component_name == "caption":
                component_config.update({
                    "before_word_count_max": 60,
                    "equipment_word_count_max": 40,
                    "shape": "component"
                })
        else:
            # Normal operation - get from config
            component_config = article_context["components"][component_name].copy()
            
            if not component_config["enabled"]:
                print(f"⏭️  {component_name.capitalize()} generation skipped (disabled)")
                return None
            
            # Merge global AI configuration with component-specific overrides
            global_ai = BATCH_CONFIG["ai"]
            component_config["ai_provider"] = global_ai["provider"]
            component_config["options"] = global_ai["options"].copy()
            
            # Apply component-specific AI overrides
            for key in ["temperature", "max_tokens", "model"]:
                if key in component_config:
                    component_config["options"][key] = component_config.pop(key)
        
        # Load schema for the article type
        schema_path = f"schemas/{article_context['article_type']}.json"
        schema = {}
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                import json
                schema = json.load(f)
        
        # Load author data
        author_data = load_author_data(article_context["author_id"])
        
        # Add category to component config if available
        if "category" in article_context:
            component_config["category"] = article_context["category"]
        else:
            component_config["category"] = ""
            
        # Add author_id to component_config
        if "author_id" in article_context:
            component_config["author_id"] = article_context["author_id"]
        
        # Import and initialize the appropriate generator dynamically
        try:
            # Construct the import path and class name dynamically
            component_module = f"components.{component_name}.generator"
            
            # Special case for metatags (capitalization issue)
            if component_name == "metatags":
                generator_class_name = "MetatagsGenerator"
            else:
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
        
        # No frontmatter data injection - all components use base component data only
        # Components are independent and equal, including frontmatter
        
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
                    
                    # For metatags issues, provide better guidance for Next.js format
                    if component_name == "metatags" and last_error:
                        print(f"🔍 DETAILED ERROR INFO FOR METATAGS: {last_error}")
                        with open("logs/metatags_error.log", "a") as f:
                            f.write(f"ERROR FOR {article_context['subject']}: {last_error}\n")
                            f.write(f"Component config: {json.dumps(component_config, indent=2)}\n")
                            f.write("-" * 80 + "\n")
                        if "options" in component_config and "messages" in component_config["options"]:
                            retry_message = {
                                "role": "user", 
                                "content": """The previous generation failed. 

INSTRUCTIONS:
1. Output ONLY Next.js compatible YAML frontmatter format with --- delimiters.
2. NO explanations, comments, or extra text - ONLY the YAML frontmatter.
3. The output MUST begin with --- and end with --- delimiters.

Example format:
---
title: "Title here"
description: "Description here"
keywords: "keyword1, keyword2"
openGraph:
  title: "Title here"
  description: "Description here"
  images:
    - url: "https://example.com/image.jpg"
      width: 1200
      height: 630
twitter:
  card: "summary_large_image"
  title: "Title here"
---"""
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
            # Check for consolidated YAML first, then fall back to individual MD files
            yaml_path = os.path.join("lists", "materials.yaml")
            if os.path.exists(yaml_path):
                print(f"Using consolidated materials list: {yaml_path}")
                subjects_with_info = get_subjects_from_consolidated_yaml(yaml_path)
            else:
                print("Using individual category files from lists directory")
                subjects_with_info = get_subjects_with_categories_from_directory("lists")
        else:
            subjects_with_info = []
        
        # Apply limit if specified
        limit = config.get("limit")
        if limit is not None:
            # Check if limit is a range [start_index, end_index]
            if isinstance(limit, list) and len(limit) == 2:
                start_idx, end_idx = limit
                # Slice the list from start_idx to end_idx (inclusive)
                subjects_to_process = [(s["subject"], s["article_type"], s["category"]) 
                                      for s in subjects_with_info[start_idx:end_idx+1]]
                print(f"Multi Mode: {len(subjects_to_process)} subjects (index range: {start_idx}-{end_idx})")
            else:
                # Traditional single number limit (first N items)
                subjects_to_process = [(s["subject"], s["article_type"], s["category"]) 
                                      for s in subjects_with_info[:limit]]
                print(f"Multi Mode: {len(subjects_to_process)} subjects (limit: {limit})")
        else:
            subjects_to_process = [(s["subject"], s["article_type"], s["category"]) 
                                  for s in subjects_with_info]
            print(f"Multi Mode: {len(subjects_to_process)} subjects (no limit)")
        
    else:
        raise ValueError(f"Invalid mode: {BATCH_CONFIG['mode']}")
    
    # Get enabled components (folders)
    enabled_components = []
    
    # Check if we're running with a --component flag to only generate one component
    if "components" in BATCH_CONFIG and isinstance(BATCH_CONFIG["components"], list):
        # We're running with --component flag, just use that list
        component_name = BATCH_CONFIG["components"][0]
        enabled_components.append(component_name)
    else:
        # Normal operation - get enabled components from config
        for name, config in BATCH_CONFIG["components"].items():
            if "enabled" in config and config["enabled"]:
                enabled_components.append(name)
                
    print(f"Enabled components: {', '.join(enabled_components)}")

    # Track output parity for all folders
    output_tracker = {comp: set() for comp in enabled_components}
    total_generated = 0
    successful_components = set()

    # Process each subject
    for subject, subject_article_type, category in subjects_to_process:
        print(f"\n--- Processing: {subject} ---")
        article_context = create_article_context(subject, subject_article_type, author_id, category)
        
        # Process all components equally - no special frontmatter handling
        for component_name in enabled_components:
            try:
                print(f"Generating {component_name} for: {subject} ({subject_article_type})")
                content = generate_component(component_name, article_context)
                
                # Strict mode: Fail immediately if content is None
                if content is None:
                    raise ValueError(f"Content generation failed for {component_name}: {subject}")
                
                category_for_output = article_context.get("category")
                output_path = save_component_output(component_name, subject, content, category_for_output, subject_article_type)
                print(f"✅ {component_name.capitalize()} saved to: {output_path}")
                output_tracker[component_name].add(subject)
                total_generated += 1
                successful_components.add(component_name)
            except Exception as e:
                print(f"❌ Error generating {component_name}: {str(e)}")
                # Strict mode: Re-raise the exception to stop execution
                raise e
                total_generated += 1
                successful_components.add(component_name)
            except Exception as e:
                print(f"❌ Error generating {component_name}: {str(e)}")
                
                # Create empty placeholder file to maintain folder parity
                content = f"---\ncategory: {category}\narticle_type: {subject_article_type}\nsubject: {subject}\nstatus: error\nerror: \"{str(e)}\"\n---\n"
                content += f"Error generating {component_name}: {str(e)}\n"
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

def clear_component_files(component=None):
    """Clear files in the content/components directory.
    
    Args:
        component: Optional specific component to clear. If None, clears all component directories.
    """
    base_dir = BATCH_CONFIG["output"]["base_dir"]
    print(f"🔍 Clearing files from directory: {base_dir}")
    
    if not os.path.exists(base_dir):
        print(f"⚠️ Directory {base_dir} does not exist.")
        return
    
    components = []
    if component:
        if os.path.exists(os.path.join(base_dir, component)):
            components = [component]
        else:
            print(f"⚠️ Component directory {component} does not exist.")
            return
    else:
        # Get all subdirectories in the content/components directory
        components = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    for comp in components:
        comp_dir = os.path.join(base_dir, comp)
        count = 0
        
        # Using a direct approach with os.listdir and os.remove
        print(f"📁 Processing component directory: {comp_dir}")
        try:
            file_list = os.listdir(comp_dir)
            print(f"  Found {len(file_list)} items in {comp_dir}")
            
            for filename in file_list:
                file_path = os.path.join(comp_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    try:
                        os.remove(file_path)
                        count += 1
                        print(f"  - Removed: {file_path}")
                    except Exception as e:
                        print(f"  ⚠️ Failed to remove {file_path}: {e}")
        except Exception as e:
            print(f"⚠️ Error processing directory {comp_dir}: {e}")
            
        # Alternative approach using find and glob
        import glob
        pattern = os.path.join(comp_dir, "*")
        files = glob.glob(pattern)
        print(f"  Found {len(files)} files using glob pattern '{pattern}'")
        
        if count == 0 and len(files) > 0:
            print(f"  Trying alternative method for {comp}...")
            for file_path in files:
                if os.path.isfile(file_path) and not os.path.basename(file_path).startswith('.'):
                    try:
                        os.remove(file_path)
                        count += 1
                        print(f"  - Removed: {file_path}")
                    except Exception as e:
                        print(f"  ⚠️ Failed to remove {file_path}: {e}")
        
        remaining = glob.glob(pattern)
        print(f"✅ Cleared {count} files from {comp} component directory ({len(remaining)} files remain)")
        
        # Try to show any remaining files in detail
        if len(remaining) > 0:
            print(f"  Remaining files in {comp_dir}:")
            for f in remaining:
                file_type = "Directory" if os.path.isdir(f) else "File"
                print(f"    - {os.path.basename(f)} ({file_type})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Z-Beam content generator")
    parser.add_argument('--clear', action='store_true', help='Clear all component files')
    parser.add_argument('--clear-component', type=str, help='Clear files for a specific component (e.g., bullets, content, frontmatter)')
    parser.add_argument('--component', type=str, help='Generate only a specific component (e.g., caption, bullets, content, frontmatter)')
    
    args = parser.parse_args()
    
    if args.clear:
        clear_component_files()
    elif args.clear_component:
        clear_component_files(args.clear_component)
    elif args.component:
        # Only generate the specified component
        BATCH_CONFIG["components"] = [args.component]
        run_batch_generation()
    else:
        run_batch_generation()
