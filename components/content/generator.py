#!/usr/bin/env python3
"""
Content Component Generator - API-based with Three-Stage Prompt System

This generator implements the working architecture:
1. Base component gets subject and author from frontmatter
2. Author country and subject are passed to personas and formatting prompts  
3. Prompt chain: base → persona → formatting
4. Return from Grok API is written to content component
"""

import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

# Set up logging
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import the component generator class
try:
    from generators.component_generators import APIComponentGenerator
except ImportError:
    # Fallback if running standalone
    class APIComponentGenerator:
        def __init__(self, component_type): 
            self.component_type = component_type

# Author prompt file mappings
AUTHOR_PROMPT_PATHS = {
    1: {
        'persona': "components/content/prompts/personas/taiwan_persona.yaml",
        'formatting': "components/content/prompts/formatting/taiwan_formatting.yaml"
    },
    2: {
        'persona': "components/content/prompts/personas/italy_persona.yaml",
        'formatting': "components/content/prompts/formatting/italy_formatting.yaml"
    },
    3: {
        'persona': "components/content/prompts/personas/indonesia_persona.yaml",
        'formatting': "components/content/prompts/formatting/indonesia_formatting.yaml"
    },
    4: {
        'persona': "components/content/prompts/personas/usa_persona.yaml",
        'formatting': "components/content/prompts/formatting/usa_formatting.yaml"
    }
}

@lru_cache(maxsize=None)
def load_base_content_prompt() -> Dict[str, Any]:
    """Load base content prompt with common instructions."""
    base_prompt_file = "components/content/prompts/base_content_prompt.yaml"
    if not Path(base_prompt_file).exists():
        raise FileNotFoundError(f"Base content prompt not found: {base_prompt_file}")
    
    with open(base_prompt_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data:
        raise ValueError(f"Base content prompt file {base_prompt_file} is empty or invalid")
    
    return data

@lru_cache(maxsize=None)
def load_persona_prompt(author_id: int) -> Dict[str, Any]:
    """Load persona-specific prompt configuration."""
    try:
        persona_file = AUTHOR_PROMPT_PATHS.get(author_id, {}).get('persona')
        if persona_file and Path(persona_file).exists():
            with open(persona_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        
        return {}
    except Exception as e:
        print(f"Error loading persona prompt: {e}")
        return {}

@lru_cache(maxsize=None)
def load_formatting_prompt(author_id: int) -> Dict[str, Any]:
    """Load formatting-specific prompt configuration."""
    try:
        formatting_file = AUTHOR_PROMPT_PATHS.get(author_id, {}).get('formatting')
        if formatting_file and Path(formatting_file).exists():
            with open(formatting_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        
        return {}
    except Exception as e:
        print(f"Error loading formatting prompt: {e}")
        return {}

class ContentComponentGenerator(APIComponentGenerator):
    """Generator for content components using production-ready fail-fast system with quality scoring"""
    
    def __init__(self):
        # Initialize parent class
        super().__init__("content")
        
        # Initialize the production-ready fail-fast generator
        from .generators.fail_fast_generator import create_fail_fast_generator
        self.fail_fast_generator = create_fail_fast_generator()
    
    def _load_prompt_config(self) -> Optional[Dict]:
        """Override parent method - content component uses fail-fast system"""
        # Content component uses fail-fast generator, not basic prompt.yaml
        return {}
    
    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None,
                provider_name: Optional[str] = None):
        """Generate content using production-ready fail-fast system"""
        # Use the fail-fast generator directly for all content generation
        result = self.fail_fast_generator.generate(
            material_name=material_name,
            material_data=material_data, 
            api_client=api_client,
            author_info=author_info,
            frontmatter_data=frontmatter_data,
            schema_fields=schema_fields
        )
        
        return result
    
    def _build_prompt(self, material_name: str, material_data: Dict,
                     author_info: Optional[Dict] = None,
                     frontmatter_data: Optional[Dict] = None,
                     schema_fields: Optional[Dict] = None) -> str:
        """Build prompt using three-stage prompt system"""
        
        logger.info(f"🔧 Building three-stage prompt for {material_name}")
        
        # Get author ID for prompt selection
        author_id = 2  # Default to Italy
        if author_info:
            author_id = author_info.get('id', 2)
        
        logger.debug(f"   👤 Using author ID: {author_id}")
        
        # Load the three-stage prompt components
        logger.debug(f"   📂 Loading prompts for author {author_id}...")
        base_prompt = load_base_content_prompt()
        persona_prompt = load_persona_prompt(author_id)
        formatting_prompt = load_formatting_prompt(author_id)
        logger.debug(f"   📝 Loaded prompts: base({len(str(base_prompt))}) persona({len(str(persona_prompt))}) format({len(str(formatting_prompt))}) chars")
        
        # Build template variables using parent class method
        template_vars = self._build_template_variables(material_name, material_data, schema_fields, author_info)
        
        # Add content-specific variables that aren't in parent
        template_vars['subject'] = material_name
        
        # Enhanced author data for prompt context
        if author_info and isinstance(author_info, dict):
            # Add comprehensive author context for prompts
            template_vars.update({
                'author_full_name': author_info.get('name', 'Expert Author'),
                'author_country_full': author_info.get('country', 'International'),
                'author_sex': author_info.get('sex', 'n'),
                'author_title_degree': author_info.get('title', 'Ph.D.'),
                'author_specialized_expertise': author_info.get('expertise', 'Laser Processing'),
                'author_persona_context': f"{author_info.get('name', 'Expert')} from {author_info.get('country', 'International')} specializing in {author_info.get('expertise', 'laser processing')}"
            })
            logger.debug(f"   👤 Enhanced author context: {template_vars.get('author_persona_context', 'Basic')}")
        
        # Use data already extracted by parent class
        # Parent _build_template_variables already handles:
        # - material_formula (chemical formula)
        # - category 
        # - author information
        # - applications formatting
        # - laser parameters
        
        # Build the final prompt by combining base → persona → formatting
        logger.debug("   🔗 Combining prompt stages: base → persona → formatting")
        final_prompt = self._build_combined_prompt(base_prompt, persona_prompt, formatting_prompt, template_vars)
        
        logger.info(f"   ✅ Final prompt built: {len(final_prompt)} chars")
        logger.debug(f"   📊 Template variables: {len(template_vars)} items")
        
        return final_prompt
    
    def _build_combined_prompt(self, base_prompt: Dict, persona_prompt: Dict, 
                              formatting_prompt: Dict, template_vars: Dict) -> str:
        """Build the final prompt by combining base → persona → formatting"""
        
        # Start with base prompt
        prompt_parts = []
        
        # Add base instructions - handle different YAML structures
        if 'system_prompt' in base_prompt:
            prompt_parts.append("SYSTEM INSTRUCTIONS:")
            prompt_parts.append(str(base_prompt['system_prompt']))
            prompt_parts.append("")
        elif 'content_approach' in base_prompt:
            prompt_parts.append("TECHNICAL CONTENT REQUIREMENTS:")
            content_approach = base_prompt['content_approach']
            if isinstance(content_approach, dict) and 'core_technical_coverage' in content_approach:
                for item in content_approach['core_technical_coverage']:
                    prompt_parts.append(f"- {item}")
            prompt_parts.append("")
        
        # Add persona instructions
        if 'persona' in persona_prompt:
            prompt_parts.append("AUTHOR PERSONA:")
            prompt_parts.append(str(persona_prompt['persona']))
            prompt_parts.append("")
        
        # Add author context from full author data
        if 'author_persona_context' in template_vars:
            prompt_parts.append("AUTHOR CONTEXT:")
            prompt_parts.append(f"You are writing as: {template_vars['author_persona_context']}")
            prompt_parts.append(f"Degree: {template_vars.get('author_title_degree', 'Ph.D.')}")
            prompt_parts.append(f"Specialized Field: {template_vars.get('author_specialized_expertise', 'Laser Processing')}")
            prompt_parts.append("")
        
        if 'writing_style' in persona_prompt:
            prompt_parts.append("WRITING STYLE:")
            if isinstance(persona_prompt['writing_style'], dict):
                for key, value in persona_prompt['writing_style'].items():
                    prompt_parts.append(f"{key}: {value}")
            else:
                prompt_parts.append(str(persona_prompt['writing_style']))
            prompt_parts.append("")
        
        # Add formatting instructions
        if 'format_requirements' in formatting_prompt:
            prompt_parts.append("FORMAT REQUIREMENTS:")
            format_reqs = formatting_prompt['format_requirements']
            if isinstance(format_reqs, dict):
                for key, value in format_reqs.items():
                    prompt_parts.append(f"{key}: {value}")
            else:
                prompt_parts.append(str(format_reqs))
            prompt_parts.append("")
        
        # Add critical word count constraints
        if 'content_constraints' in formatting_prompt:
            prompt_parts.append("WORD COUNT CONSTRAINTS:")
            constraints = formatting_prompt['content_constraints']
            if isinstance(constraints, dict):
                for key, value in constraints.items():
                    prompt_parts.append(f"{key}: {value}")
            else:
                prompt_parts.append(str(constraints))
            prompt_parts.append("")
        
        # Add the main task using template variables from parent class
        # Extract word count limit from formatting prompt for emphasis
        word_count_limit = "300"  # Default
        if 'content_constraints' in formatting_prompt:
            constraints = formatting_prompt['content_constraints']
            if isinstance(constraints, dict) and 'max_word_count' in constraints:
                word_count_limit = str(constraints['max_word_count'])
        
        task_prompt = f"""TASK: Generate comprehensive technical content about laser cleaning for {template_vars['material_name']}.

CRITICAL REQUIREMENT: Content must be UNDER {word_count_limit} words maximum. This is a strict limit.

MATERIAL DETAILS:
- Name: {template_vars['material_name']}
- Formula: {template_vars.get('material_formula', 'N/A')}
- Category: {template_vars.get('category', 'Material')}
- Applications: {template_vars.get('applications_list', 'Various industrial applications')}
- Parameters: {template_vars.get('laser_fluence', 'TBD')} fluence, {template_vars.get('laser_wavelength', 'TBD')} wavelength

Generate detailed, technical content that provides practical value for professionals working with laser cleaning systems.
Focus on material properties, optimal parameters, applications, and advantages.
REMEMBER: Keep content under {word_count_limit} words total."""
        
        prompt_parts.append(task_prompt)
        
        return "\n".join(prompt_parts)
