#!/usr/bin/env python3
"""
Component Generators for Z-Beam

This module provides individual component generators that can be used
independently or orchestrated by the dynamic generator.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class ComponentResult:
    """Result of component generation"""
    component_type: str
    content: str
    success: bool
    error_message: Optional[str] = None

class BaseComponentGenerator(ABC):
    """Base class for component generators"""
    
    def __init__(self, component_type: str):
        self.component_type = component_type
        self.component_dir = Path("components") / component_type
        self.prompt_config = self._load_prompt_config()
    
    def _load_prompt_config(self) -> Optional[Dict]:
        """Load prompt configuration for this component"""
        prompt_file = self.component_dir / "prompt.yaml"
        if not prompt_file.exists():
            logger.warning(f"Prompt file not found: {prompt_file}")
            return None
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading prompt config for {self.component_type}: {e}")
            return None
    
    @abstractmethod
    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate component content"""
        pass
    
    def _create_result(self, content: str, success: bool = True, 
                      error_message: Optional[str] = None) -> ComponentResult:
        """Create a ComponentResult"""
        return ComponentResult(
            component_type=self.component_type,
            content=content,
            success=success,
            error_message=error_message
        )

class StaticComponentGenerator(BaseComponentGenerator):
    """Base class for static components that don't require API calls"""
    
    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate static component content"""
        try:
            content = self._generate_static_content(
                material_name, material_data, author_info, frontmatter_data, schema_fields
            )
            return self._create_result(content, success=True)
        except Exception as e:
            logger.error(f"Error generating {self.component_type}: {e}")
            return self._create_result("", success=False, error_message=str(e))
    
    @abstractmethod
    def _generate_static_content(self, material_name: str, material_data: Dict,
                                author_info: Optional[Dict] = None,
                                frontmatter_data: Optional[Dict] = None,
                                schema_fields: Optional[Dict] = None) -> str:
        """Generate static content for this component"""
        pass

class APIComponentGenerator(BaseComponentGenerator):
    """Base class for components that require API calls"""
    
    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate API-driven component content"""
        
        if not api_client:
            return self._create_result("", success=False, 
                                     error_message="API client required but not provided")
        
        try:
            # Build the prompt with schema fields
            prompt = self._build_prompt(material_name, material_data, author_info, 
                                      frontmatter_data, schema_fields)
            
            # Generate content using API
            if hasattr(api_client, 'generate_for_component'):
                response = api_client.generate_for_component(
                    component_type=self.component_type,
                    material=material_name,
                    prompt_template=prompt
                )
            elif hasattr(api_client, 'generate_simple'):
                response = api_client.generate_simple(prompt)
            else:
                response = api_client.generate(prompt)
            
            # Handle different response types
            if isinstance(response, str):
                # Direct string response
                content = self._post_process_content(response, material_name, material_data)
                logger.info(f"Generated {self.component_type} for {material_name} (direct string response)")
                return self._create_result(content, success=True)
            elif hasattr(response, 'success') and response.success:
                # Structured response object
                content = self._post_process_content(response.content, material_name, material_data)
                logger.info(f"Generated {self.component_type} for {material_name} ({getattr(response, 'token_count', 0)} tokens)")
                return self._create_result(content, success=True)
            elif hasattr(response, 'success'):
                # Failed structured response
                return self._create_result("", success=False, 
                                         error_message=f"API generation failed: {getattr(response, 'error', 'Unknown error')}")
            else:
                # Unknown response type, treat as string
                content = self._post_process_content(str(response), material_name, material_data)
                logger.info(f"Generated {self.component_type} for {material_name} (unknown response type)")
                return self._create_result(content, success=True)
        
        except Exception as e:
            logger.error(f"Error generating {self.component_type}: {e}")
            return self._create_result("", success=False, error_message=str(e))
    
    def _build_prompt(self, material_name: str, material_data: Dict,
                     author_info: Optional[Dict] = None,
                     frontmatter_data: Optional[Dict] = None,
                     schema_fields: Optional[Dict] = None) -> str:
        """Build prompt for this component"""
        
        if not self.prompt_config:
            return f"Generate {self.component_type} content for {material_name}"
        
        # Import slug utilities
        try:
            from utils.slug_utils import create_material_slug
        except ImportError:
            def create_material_slug(name: str) -> str:
                return name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')
        
        # Get base prompt
        base_prompt = self.prompt_config.get('template', self.prompt_config.get('prompt', ''))
        system_prompt = self.prompt_config.get('system', '')
        
        # Create template variables with schema fields
        template_vars = self._build_template_variables(material_name, material_data, 
                                                      schema_fields, author_info)
        
        # Replace template variables
        prompt = base_prompt
        for var, value in template_vars.items():
            prompt = prompt.replace(f'{{{var}}}', str(value))
        
        # Add schema fields context if available
        if schema_fields:
            prompt += self._add_schema_context(schema_fields)
        
        # Add frontmatter data if available
        if frontmatter_data and self.component_type == 'propertiestable':
            prompt += self._add_frontmatter_context(frontmatter_data)
        
        # Combine with system prompt if available
        if system_prompt:
            return f"System: {system_prompt}\n\nUser: {prompt}"
        else:
            return prompt
    
    def _build_template_variables(self, material_name: str, material_data: Dict,
                                 schema_fields: Optional[Dict] = None, 
                                 author_info: Optional[Dict] = None) -> Dict[str, str]:
        """Build template variables for content generation"""
        
        # Handle case where material_data might be passed as string
        if isinstance(material_data, str):
            logger.warning(f"material_data is string: {material_data}, converting to dict")
            material_data = {'name': material_data, 'category': 'material', 'article_type': 'material'}
        
        # Validate that material_data is a dict
        if not isinstance(material_data, dict):
            raise TypeError(f"material_data must be a dict, got {type(material_data)}: {material_data}")
        
        # Import slug utilities
        try:
            from utils.slug_utils import create_material_slug
        except ImportError:
            def create_material_slug(name: str) -> str:
                return name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')
        
        category = material_data.get('category', 'material')
        article_type = material_data.get('article_type', 'material')
        
        template_vars = {
            'subject': material_name,
            'material': material_name,
            'material_name': material_name,
            'category': category,
            'article_type': article_type,
            'subject_lowercase': material_name.lower(),
            'subject_slug': create_material_slug(material_name),
            'material_formula': material_data.get('formula', material_name),
            'material_symbol': material_data.get('symbol', material_name[:2].upper()),
            'material_type': material_data.get('material_type', category),
            'material_description': material_data.get('description', 
                f"{material_name} is a {category} material used in laser cleaning applications."),
            'bullet_count': "2 to 6",
            'formatted_technical_specs': f"Technical specifications for {material_name} laser cleaning",
            'formatted_environmental_impact': f"Environmental benefits of {material_name} laser processing",
            'formatted_regulatory_standards': f"Industry standards for {material_name} treatment"
        }
        
        # Add author-specific variables
        if author_info:
            template_vars.update(self._create_author_vars(author_info))
        else:
            template_vars.update(self._create_default_author_vars())
        
        # Add schema field variables if available
        if schema_fields:
            for field_name, field_data in schema_fields.items():
                # Handle both old format (dict) and new format (string)
                if isinstance(field_data, dict):
                    # Old format: field_data is a dict with 'description' key
                    template_vars[f'schema_{field_name}'] = str(field_data.get('description', field_name))
                    if 'default' in field_data:
                        template_vars[f'schema_{field_name}_default'] = str(field_data['default'])
                elif isinstance(field_data, str):
                    # New format: field_data is directly the description string
                    template_vars[f'schema_{field_name}'] = field_data
                elif isinstance(field_data, list):
                    # Handle list format (like profile_fields)
                    template_vars[f'schema_{field_name}'] = ', '.join(str(item) for item in field_data)
                else:
                    # Fallback for other types
                    template_vars[f'schema_{field_name}'] = str(field_data)
        
        return template_vars
    
    def _create_author_vars(self, author_info: Dict) -> Dict[str, str]:
        """Create author-specific template variables"""
        
        # Handle case where author_info might be None or not a dict
        if not author_info or not isinstance(author_info, dict):
            logger.debug(f"author_info is not a dict: {type(author_info)}")
            return self._create_default_author_vars()
        
        country = author_info.get('country', 'International')
        author_id = author_info.get('id', 0)
        author_name = author_info.get('name', 'Expert Author')
        
        vars_dict = {
            'country': country,
            'author_name': author_name,
            'author_country': country,
            'author_title': author_info.get('title', 'Technical Expert'),
            'author_expertise': author_info.get('expertise', 'Laser Processing'),
            'author_id': str(author_id),
            'author_slug': author_name.lower().replace(' ', '-'),
        }
        
        # Country context
        if country != 'International':
            vars_dict['country_context'] = f"Write from the perspective of a technical expert in {country}, incorporating relevant regional standards and industry practices."
        else:
            vars_dict['country_context'] = "Write from an international technical perspective with global industry standards."
        
        # Author-specific bullet formatting rules
        vars_dict['bullet_format_rules'] = self._get_bullet_format_rules(author_id)
        
        return vars_dict
    
    def _create_default_author_vars(self) -> Dict[str, str]:
        """Create default author variables"""
        return {
            'country': 'International',
            'author_name': 'Expert Author',
            'author_country': 'International',
            'author_title': 'Technical Expert',
            'author_expertise': 'Laser Processing',
            'author_id': '0',
            'author_slug': 'expert-author',
            'country_context': "Write from an international technical perspective with global industry standards.",
            'bullet_format_rules': self._get_bullet_format_rules(0)
        }
    
    def _get_bullet_format_rules(self, author_id: int) -> str:
        """Get author-specific bullet formatting rules"""
        if author_id == 1:  # Taiwan - Yi-Chun Lin
            return """
TAIWAN AUTHOR REQUIREMENTS:
- Generate EXACTLY 4 bullets
- Each bullet must have EXACTLY 1 sentence
- Use numbered list format (1., 2., 3., 4.)
- Start each bullet with **Technical Focus:** followed by the topic
- Order: Parameters → Applications → Safety → Environmental Benefits
- Write in English only, incorporate Taiwan semiconductor/electronics industry context
- Include metric measurements and specific wavelengths"""
            
        elif author_id == 2:  # Italy - Alessandro Moretti
            return """
ITALIAN AUTHOR REQUIREMENTS:
- Generate EXACTLY 5 bullets
- Each bullet must have EXACTLY 2 sentences
- Use traditional bullet format with - prefix
- Start each bullet with **[TOPIC]** in ALL CAPS brackets
- Order: Applications → Parameters → Environmental → Safety → Challenges
- Write in English only, incorporate European/Italian manufacturing industry context
- Include European standards and industrial applications"""
            
        elif author_id == 3:  # Indonesia - Ikmanda Roswati
            return """
INDONESIAN AUTHOR REQUIREMENTS:
- Generate EXACTLY 6 bullets
- Each bullet must have EXACTLY 1 sentence
- Use bullet format with • prefix
- Start each bullet with **Aspect [Topic]:** (use English "Aspect" for all content)
- Order: Environmental → Safety → Applications → Parameters → Challenges → Benefits
- CRITICAL: Write ONLY in English for all content including headers
- Incorporate Indonesian tropical/humid environment and industrial context in English
- Emphasize sustainability and regional manufacturing considerations"""
            
        elif author_id == 4:  # USA - Todd Dunning
            return """
USA AUTHOR REQUIREMENTS:
- Generate EXACTLY 3 bullets
- Each bullet must have EXACTLY 3 sentences
- Use bullet format with * prefix
- Start each bullet with **Key Point:** followed by the topic
- Order: Safety → Parameters → Applications
- Write in English only, incorporate US high-tech industry and regulatory context
- Include OSHA standards, FDA considerations, and Silicon Valley tech applications"""
        else:
            return """
DEFAULT INTERNATIONAL REQUIREMENTS:
- Generate EXACTLY 4 bullets
- Each bullet must have EXACTLY 1 sentence
- Use bullet format with * prefix
- Start each bullet with **[Topic]:** followed by technical details
- Standard order: Parameters → Applications → Safety → Environmental
- Write in English only with international technical perspective"""
    
    def _add_frontmatter_context(self, frontmatter_data: Dict) -> str:
        """Add frontmatter context to prompt"""
        
        # Handle case where frontmatter_data might be None or not a dict
        if not frontmatter_data or not isinstance(frontmatter_data, dict):
            logger.debug(f"frontmatter_data is not a dict: {type(frontmatter_data)}")
            return "\n\nFRONTMATTER DATA: Not available\n"
        
        context = "\n\nFRONTMATTER DATA AVAILABLE:\n"
        
        # Chemical properties
        chem_props = frontmatter_data.get('chemicalProperties', {})
        if chem_props:
            context += f"Chemical Formula: {chem_props.get('formula', 'N/A')}\n"
            context += f"Material Symbol: {chem_props.get('symbol', 'N/A')}\n"
            context += f"Material Type: {chem_props.get('materialType', 'N/A')}\n"
        
        # Physical properties
        properties = frontmatter_data.get('properties', {})
        if properties:
            context += f"Density: {properties.get('density', 'N/A')}\n"
            context += f"Thermal Conductivity: {properties.get('thermalConductivity', 'N/A')}\n"
            context += f"Melting Point: {properties.get('meltingPoint', 'N/A')}\n"
        
        # Category from frontmatter
        fm_category = frontmatter_data.get('category', '')
        if fm_category:
            context += f"Category: {fm_category.title()}\n"
        
        # Technical specifications
        tech_specs = frontmatter_data.get('technicalSpecifications', {})
        if tech_specs and hasattr(tech_specs, 'get'):
            tensile = tech_specs.get('tensileStrength', '')
            if tensile:
                context += f"Tensile Strength: {tensile}\n"
        
        return context
    
    def _add_schema_context(self, schema_fields: Dict) -> str:
        """Add schema field context to prompt"""
        if not schema_fields:
            return ""
        
        context = "\n\nSCHEMA FIELDS AVAILABLE:\n"
        context += "The following dynamic fields should be considered for this content type:\n"
        
        for field_name, field_data in schema_fields.items():
            # Handle both old format (dict) and new format (string)
            if isinstance(field_data, dict):
                # Old format: field_data is a dict with 'description' key
                description = field_data.get('description', 'Dynamic field')
                context += f"- {field_name}: {description}"
                if 'type' in field_data:
                    context += f" (Type: {field_data['type']})"
                if 'default' in field_data:
                    context += f" [Default: {field_data['default']}]"
            elif isinstance(field_data, str):
                # New format: field_data is directly the description string
                context += f"- {field_name}: {field_data}"
            elif isinstance(field_data, list):
                # Handle list format (like profile_fields)
                context += f"- {field_name}: {', '.join(str(item) for item in field_data)}"
            else:
                # Fallback for other types
                context += f"- {field_name}: {str(field_data)}"
            context += "\n"
        
        context += "\nIncorporate these fields where relevant to enhance content specificity.\n"
        return context
    
    def _post_process_content(self, content: str, material_name: str, material_data: Dict) -> str:
        """Post-process generated content"""
        # Special handling for frontmatter enhancement
        if self.component_type == 'frontmatter':
            try:
                from utils.property_enhancer import enhance_generated_frontmatter
                category = material_data.get('category', '')
                content = enhance_generated_frontmatter(content, category)
                logger.info(f"Enhanced frontmatter for {material_name} with property context and percentiles")
            except Exception as e:
                logger.warning(f"Failed to enhance frontmatter: {e}")
        
        return content

# Specific component generators

class AuthorComponentGenerator(StaticComponentGenerator):
    """Generator for author components"""
    
    def __init__(self):
        super().__init__("author")
    
    def _generate_static_content(self, material_name: str, material_data: Dict,
                                author_info: Optional[Dict] = None,
                                frontmatter_data: Optional[Dict] = None) -> str:
        """Generate author component content"""
        try:
            from run import get_author_by_id
            from components.author.generator import create_author_content_from_data
            
            # Get author ID from author_info or use default
            author_id = 1
            if author_info and 'id' in author_info:
                author_id = author_info['id']
            
            # Get author data
            author = get_author_by_id(author_id)
            if not author:
                author = {
                    "name": "Unknown Author", 
                    "title": "Ph.D.", 
                    "country": "International", 
                    "expertise": "Materials Science and Laser Technology",
                    "image": "/images/author/default.jpg"
                }
            
            # Generate content
            return create_author_content_from_data(material_name, author)
            
        except Exception as e:
            logger.error(f"Error generating author component: {e}")
            return f"Error loading author information: {e}"

# Component generator factory

class ComponentGeneratorFactory:
    """Factory for creating component generators"""
    
    _generators = {
        'author': 'components.author.generator.AuthorComponentGenerator',
        'badgesymbol': 'components.badgesymbol.generator.BadgeSymbolComponentGenerator',
        'propertiestable': 'components.propertiestable.generator.PropertiesTableComponentGenerator',
        'frontmatter': 'components.frontmatter.generator.FrontmatterComponentGenerator',
        'content': 'components.content.generator.ContentComponentGenerator',
        'bullets': 'components.bullets.generator.BulletsComponentGenerator',
        'caption': 'components.caption.generator.CaptionComponentGenerator',
        'table': 'components.table.generator.TableComponentGenerator',
        'tags': 'components.tags.generator.TagsComponentGenerator',
        'metatags': 'components.metatags.generator.MetatagsComponentGenerator',
        'jsonld': 'components.jsonld.generator.JsonldComponentGenerator',
    }
    
    @classmethod
    def create_generator(cls, component_type: str) -> Optional[BaseComponentGenerator]:
        """Create a component generator for the specified type"""
        generator_spec = cls._generators.get(component_type)
        if not generator_spec:
            logger.warning(f"No generator found for component type: {component_type}")
            return None
        
        try:
            # Handle string imports for external generator files
            if isinstance(generator_spec, str):
                module_path, class_name = generator_spec.rsplit('.', 1)
                module = __import__(module_path, fromlist=[class_name])
                generator_class = getattr(module, class_name)
                return generator_class()
            else:
                # Handle direct class references
                return generator_spec()
                
        except Exception as e:
            logger.error(f"Error creating generator for {component_type}: {e}")
            return None
    
    @classmethod
    def get_available_components(cls) -> List[str]:
        """Get list of available component types"""
        return list(cls._generators.keys())
