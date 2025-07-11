#!/usr/bin/env python3
"""
Schema-Driven Z-Beam Generator
Uses schema generators to produce content with ZERO defaults or hardcoded values
"""

import os
import json
import yaml
import logging
import inspect
import importlib
from datetime import datetime
from typing import Dict, Any, Type, Optional

# Import schema generators
from schemas.generators.application_generator import ApplicationGenerator
from schemas.generators.material_generator import MaterialGenerator
from schemas.generators.region_generator import RegionGenerator
from schemas.generators.thesaurus_generator import ThesaurusGenerator

# Import specialized generator modules without assuming class names
from tags import tag_generator as tag_module
import jsonld.jsonld_generator as jsonld_module
import metadata.metadata_generator as metadata_module

# Create adapter classes for specialized generators
class TagGeneratorAdapter:
    """Adapter for any tag generator implementation"""
    
    def __init__(self, api_client, config):
        self.api_client = api_client
        self.config = config
        # Add logger initialization
        self.logger = logging.getLogger(__name__)
        try:
            self.tag_generator = self._get_tag_generator()
            self.using_fallback = False
        except ImportError:
            self.logger.warning("No tag generator found, using minimal schema-based implementation")
            self.tag_generator = None
            self.using_fallback = True
    
    def _get_tag_generator(self):
        """Get any available tag generator implementation"""
        # Try common class names
        for name in ["DynamicTagGenerator", "TagGenerator", "ArticleTagGenerator"]:
            if hasattr(tag_module, name):
                generator_class = getattr(tag_module, name)
                return generator_class(self.api_client, self.config)
        
        # If no match, try finding a class with generate_tags method
        for name, obj in inspect.getmembers(tag_module):
            if inspect.isclass(obj) and hasattr(obj, "generate_tags"):
                return obj(self.api_client, self.config)
        
        raise ImportError("No suitable tag generator found")
    
    def generate_tags(self, data):
        """Generate tags using whatever method is available"""
        if self.using_fallback:
            raw_tags = self._generate_fallback_tags(data)
        else:
            try:    
                if hasattr(self.tag_generator, "generate_tags"):
                    raw_tags = self.tag_generator.generate_tags(data)
                else:
                    raise NotImplementedError("Tag generator does not implement generate_tags method")
            except Exception as e:
                self.logger.warning(f"Tag generator failed: {e}. Using fallback implementation.")
                raw_tags = self._generate_fallback_tags(data)
        
        # Ensure we return a formatted string, not a list
        return self._format_tags(raw_tags)
    
    def generate(self, data):
        """Alias for generate_tags to maintain compatibility with schema generators"""
        return self.generate_tags(data)
    
    def _generate_fallback_tags(self, data):
        """Generate minimal tags based on schema data only"""
        tags = []
        
        # Extract basic info from context and schema
        context = data.get("context", {})
        schema_type = data.get("schema_type", "")
        
        # Add subject as a tag if available
        if "subject" in context:
            tags.append(context["subject"])
        
        # Add schema_type as a tag if available
        if schema_type:
            tags.append(schema_type)
            
        # For materials, add material category if available
        if "material_profile" in data:
            profile = data.get("material_profile", {})
            if "category" in profile:
                tags.append(profile["category"])
                
        # For applications, add application type if available  
        if "application_profile" in data:
            profile = data.get("application_profile", {})
            if "type" in profile:
                tags.append(profile["type"])
                
        return tags
    
    def _format_tags(self, tags):
        """Format tags as a string according to config"""
        if not tags:
            return ""
            
        # Get tag format preferences from config
        format_style = self.config.get("formatStyle", "hash") if self.config else "hash"
        separator = self.config.get("separator", " ") if self.config else " "
        
        # Handle different format styles
        if format_style == "hash":
            formatted_tags = [f"#{tag.replace(' ', '_')}" for tag in tags]
        elif format_style == "comma":
            return ", ".join(tags)
        elif format_style == "plain":
            formatted_tags = tags
        else:
            # Default to hash format
            formatted_tags = [f"#{tag.replace(' ', '_')}" for tag in tags]
        
        # Join with separator
        return separator.join(formatted_tags)
    

class JsonLdGeneratorAdapter:
    """Adapter for any JSON-LD generator implementation"""
    
    def __init__(self, api_client, config):
        self.api_client = api_client
        self.config = config
        # Add logger initialization
        self.logger = logging.getLogger(__name__)
        try:
            self.json_ld_generator = self._get_json_ld_generator()
            self.using_fallback = False
        except ImportError:
            self.logger.warning("No JSON-LD generator found, using minimal schema-based implementation")
            self.json_ld_generator = None
            self.using_fallback = True
    
    def _get_json_ld_generator(self):
        """Get any available JSON-LD generator implementation"""
        # First try directly inspecting the module
        for name, obj in inspect.getmembers(jsonld_module):
            if inspect.isclass(obj) and name.lower().find('json') >= 0:
                self.logger.info(f"Found JSON-LD generator: {name}")
                return obj(self.api_client, self.config)
        
        # If that fails, try hardcoded common names
        for name in ["JsonLdGenerator", "JSONLDGenerator", "StructuredDataGenerator", "DynamicJsonLdGenerator"]:
            if hasattr(jsonld_module, name):
                generator_class = getattr(jsonld_module, name)
                return generator_class(self.api_client, self.config)
        
        # Last resort - look for any class with generate methods
        for name, obj in inspect.getmembers(jsonld_module):
            if inspect.isclass(obj) and (hasattr(obj, "generate_jsonld") or hasattr(obj, "generate")):
                return obj(self.api_client, self.config)
        
        raise ImportError("No suitable JSON-LD generator found")
    
    def generate_jsonld(self, data):
        """Generate JSON-LD using whatever method is available"""
        if self.using_fallback:
            raise RuntimeError("No JSON-LD generator available")
    
        try:
            if hasattr(self.json_ld_generator, "generate_jsonld"):
                return self.json_ld_generator.generate_jsonld(data)
            elif hasattr(self.json_ld_generator, "generate"):
                return self.json_ld_generator.generate(data)
            
            raise NotImplementedError("JSON-LD generator does not implement generate_jsonld or generate method")
        
        except (ValueError, RuntimeError, Exception) as e:
            # No fallback - just raise the error
            self.logger.error(f"JSON-LD generator failed: {e}")
            raise RuntimeError(f"JSON-LD generation failed: {e}")
    
    def generate(self, data):
        """Alias for generate_jsonld to maintain compatibility with schema generators"""
        return self.generate_jsonld(data)
    
    def _generate_fallback_jsonld(self, data):
        """
        Generate minimal JSON-LD based solely on schema data
        NO hardcoded defaults - uses only provided schema and context data
        """
        # Extract info from data
        context = data.get("context", {})
        schema_type = data.get("schema_type", "")
        subject = context.get("subject", "")
        
        # Create minimal JSON-LD
        json_ld = {
            "@context": "https://schema.org",
        }
        
        # Set type based on schema_type
        if schema_type == "application":
            json_ld["@type"] = "TechnicalArticle"
        elif schema_type == "material":
            json_ld["@type"] = "Product"
        elif schema_type == "region":
            json_ld["@type"] = "Place"
        elif schema_type == "thesaurus":
            json_ld["@type"] = "DefinedTerm"
        else:
            json_ld["@type"] = "Article"
        
        # Add name/title
        if subject:
            json_ld["name"] = subject
            
        # Add author if available
        if "author" in context:
            author = context["author"]
            if "name" in author:
                json_ld["author"] = {
                    "@type": "Person",
                    "name": author["name"]
                }
                
        # Add description if available
        if "description" in context:
            json_ld["description"] = context["description"]
        
        # If data has a material profile, use it
        if "material_profile" in data:
            profile = data.get("material_profile", {})
            
            if "properties" in profile:
                properties = {}
                for prop, value in profile["properties"].items():
                    if isinstance(value, dict) and "value" in value:
                        properties[prop] = value["value"]
                    else:
                        properties[prop] = value
                
                json_ld["additionalProperty"] = [
                    {
                        "@type": "PropertyValue",
                        "name": name,
                        "value": value
                    }
                    for name, value in properties.items()
                ]
        
        return json.dumps(json_ld, indent=2)


class MetadataGeneratorAdapter:
    """Adapter for any metadata generator implementation"""
    
    def __init__(self, api_client, config):
        self.api_client = api_client
        self.config = config
        try:
            self.metadata_generator = self._get_metadata_generator()
            self.using_fallback = False
        except ImportError:
            self.logger = logging.getLogger(__name__)
            self.logger.warning("No metadata generator found, using minimal schema-based implementation")
            self.metadata_generator = None
            self.using_fallback = True
    
    def _get_metadata_generator(self):
        """Get any available metadata generator implementation"""
        # Try common class names
        for name in ["MetadataGenerator", "ArticleMetadataGenerator", "FrontmatterGenerator"]:
            if hasattr(metadata_module, name):
                generator_class = getattr(metadata_module, name)
                return generator_class(self.api_client, self.config)
        
        # If no match, try finding a class with generate_metadata method
        for name, obj in inspect.getmembers(metadata_module):
            if inspect.isclass(obj) and (hasattr(obj, "generate_metadata") or hasattr(obj, "generate")):
                return obj(self.api_client, self.config)
        
        raise ImportError("No suitable metadata generator found")
    
    def generate_metadata(self, data):
        """Generate metadata using whatever method is available"""
        if self.using_fallback:
            return self._generate_fallback_metadata(data)
        
        if hasattr(self.metadata_generator, "generate_metadata"):
            return self.metadata_generator.generate_metadata(data)
        elif hasattr(self.metadata_generator, "generate"):
            return self.metadata_generator.generate(data)
        
        raise NotImplementedError("Metadata generator does not implement generate_metadata or generate method")
    
    def _generate_fallback_metadata(self, data):
        """
        Generate minimal metadata based solely on schema data
        NO hardcoded defaults - uses only provided schema and context data
        """
        metadata = {}
        
        # Extract basic info from context
        context = data.get("context", {})
        schema = data.get("schema", {})
        
        # Add basic metadata from context
        if "subject" in context:
            metadata["title"] = context["subject"]
        
        if "schema_type" in data:
            metadata["articleType"] = data["schema_type"]
            
        # Add author info if available
        if "author" in context:
            author = context["author"]
            if "name" in author:
                metadata["author"] = author["name"]
        
        # Add timestamp
        metadata["generatedAt"] = datetime.now().isoformat()
        
        # Extract any metadata from schema if available
        if "generatorConfig" in schema and "metadata" in schema["generatorConfig"]:
            schema_metadata = schema["generatorConfig"]["metadata"]
            metadata.update(schema_metadata)
            
        return metadata
    
    def generate(self, data):
        """Alias for generate_metadata to maintain compatibility with schema generators"""
        return self.generate_metadata(data)


class ZBeamGenerator:
    """
    Main generator class that orchestrates the entire generation process
    """
    
    def __init__(self, api_client, logger=None):
        """
        Initialize the generator with API client and config.
        
        Args:
            api_client: API client for LLM calls
            logger: Logger for tracking generation process
        """
        self.api_client = api_client
        self.logger = logger or logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_configuration()
        
        # Initialize specialized generators with adapters
        self.logger.info("Initializing specialized generators with adapters")
        self.json_ld_generator = JsonLdGeneratorAdapter(api_client, self.config.get("jsonld", {}).get("technical", {}))
        self.tags_generator = TagGeneratorAdapter(api_client, self.config.get("tags", {}).get("technical", {}))
        self.metadata_generator = MetadataGeneratorAdapter(api_client, self.config.get("metadata", {}).get("technical", {}))
        
        # Load schema definitions
        self._load_schemas()
        
        # Load author profiles
        self._load_author_profiles()
    
    def _load_configuration(self):
        """
        Load configuration for the generator.
        
        Returns:
            Configuration dictionary
        """
        # For simplicity, returning an empty config
        return {
            "jsonld": {},
            "tags": {},
            "metadata": {}
        }
    
    def _load_schemas(self):
        """
        Load schema definitions from the schemas directory.
        """
        self.schemas = {}
        schemas_dir = "schemas/definitions"
        
        if not os.path.exists(schemas_dir):
            self.logger.warning(f"Schemas directory not found: {schemas_dir}")
            return
        
        # Load each schema file
        for filename in os.listdir(schemas_dir):
            if not filename.endswith("_schema_definition.md"):
                continue
            
            schema_type = filename.split("_")[0]
            file_path = os.path.join(schemas_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    schema_def = yaml.safe_load(content)
                    self.schemas[schema_type] = schema_def
                    
                    self.logger.info(f"Loaded schema {schema_type} from {file_path}")
            
            except Exception as e:
                self.logger.warning(f"Error loading schema {schema_type} from {file_path}: {e}")
    
    def _load_author_profiles(self):
        """
        Load author profiles from the authors directory.
        """
        authors_file = "authors/authors.json"
        
        if not os.path.exists(authors_file):
            self.logger.warning(f"Authors file not found: {authors_file}")
            return
        
        try:
            with open(authors_file, 'r', encoding='utf-8') as file:
                authors = json.load(file)
                
                # Validate authors
                if not authors:
                    raise ValueError("Authors file is empty")
                
                self.author_profiles = authors
                self.logger.info(f"Loaded {len(authors)} author profiles from {authors_file}")
        
        except Exception as e:
            self.logger.warning(f"Error loading authors from {authors_file}: {e}")
            self.author_profiles = []
    
    def generate_article(self, context):
        """Generate an article based on the given context."""
        # Log the start of generation
        self.logger.info(f"Generating {context['article_type']} article for: {context['subject']}")
        
        # Track generation errors
        generation_errors = []
        
        try:
            # Get the appropriate schema generator
            if context["article_type"] == "application":
                from schemas.generators.application_generator import ApplicationGenerator
                schema_generator = self._create_generator(ApplicationGenerator)
            elif context["article_type"] == "material":
                from schemas.generators.material_generator import MaterialGenerator
                schema_generator = self._create_generator(MaterialGenerator)
            elif context["article_type"] == "region":
                from schemas.generators.region_generator import RegionGenerator
                schema_generator = self._create_generator(RegionGenerator)
            elif context["article_type"] == "thesaurus":
                from schemas.generators.thesaurus_generator import ThesaurusGenerator
                schema_generator = self._create_generator(ThesaurusGenerator)
            else:
                raise ValueError(f"Unsupported article type: {context['article_type']}")
            
            # Generate article components based on the schema
            components = schema_generator.generate(context)
            
            # Check if there were any errors during component generation
            if hasattr(schema_generator, 'errors') and schema_generator.errors:
                for error in schema_generator.errors:
                    generation_errors.append(error)
                    
            # Return components with any error information
            result = {
                "components": components["components"],
            }
            
            if generation_errors:
                result["errors"] = generation_errors
                
            return result
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            # Still try to generate a basic article with error information
            generation_errors.append(f"Exception during generation: {str(e)}")
            
            # Create minimal components
            minimal_components = {
                "metadata": {
                    "title": context.get("subject", "Untitled"),
                    "articleType": context.get("article_type", "unknown"),
                    "generatedAt": datetime.now().isoformat(),
                    "status": "error"
                },
                "tags": f"#{context.get('article_type', '')} #error",
                "json_ld": '{"@context":"https://schema.org","@type":"Article","name":"Error"}',
                "schema_type": context.get("article_type", "unknown"),
                "subject": context.get("subject", "Untitled"),
                "schema": {},
                "content_sections": {
                    "overview": f"Error generating content for {context.get('subject', 'this subject')}."
                }
            }
            
            return {
                "components": minimal_components,
                "errors": generation_errors
            }
    
    def _create_generator(self, generator_class):
        """
        Create a generator instance with appropriate arguments based on signature.
        Handles different constructor patterns flexibly.
        
        Args:
            generator_class: The generator class to instantiate
            
        Returns:
            An instance of the generator class
        """
        import inspect
        
        # Get the signature of the generator class constructor
        sig = inspect.signature(generator_class.__init__)
        params = list(sig.parameters.values())
        
        # Skip 'self' parameter
        if params and params[0].name == 'self':
            params = params[1:]
        
        # Prepare arguments dictionary
        args_dict = {
            'schemas': self.schemas,
            'author_profiles': self.author_profiles,
            'json_ld_generator': self.json_ld_generator,
            'tags_generator': self.tags_generator, 
            'metadata_generator': self.metadata_generator,
            'api_client': self.api_client,
            'logger': self.logger
        }
        
        # Build arguments list based on parameter names
        kwargs = {}
        for param in params:
            param_name = param.name
            if param_name in args_dict:
                kwargs[param_name] = args_dict[param_name]
        
        # Create instance with appropriate arguments
        self.logger.info(f"Creating {generator_class.__name__} with {len(kwargs)} arguments")
        return generator_class(**kwargs)
    
    def _generate_jsonld(self, data):
        """Generate JSON-LD structured data without fallbacks"""
        # Find the JSON-LD generator
        generator_classes = self._find_generator_classes('jsonld')
        if not generator_classes:
            raise RuntimeError("No JSON-LD generator found")
            
        # Use the first available generator
        generator_class = generator_classes[0]
        generator = generator_class(self.api_client, self.logger)
        return generator.generate(data)