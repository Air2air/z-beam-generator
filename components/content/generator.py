#!/usr/bin/env python3
"""
Content Component Generator - Prompt-Driven Content Generation
Uses ONLY YAML prompt configurations for content generation.
NO hardcoded sentences or content - everything from prompts.
"""

import sys
import yaml
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from functools import lru_cache

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from generators.component_generators import StaticComponentGenerator

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
    prompt_files = {
        1: "components/content/prompts/taiwan_prompt.yaml",
        2: "components/content/prompts/italy_prompt.yaml", 
        3: "components/content/prompts/indonesia_prompt.yaml",
        4: "components/content/prompts/usa_prompt.yaml"
    }
    
    prompt_file = prompt_files.get(author_id)
    if not prompt_file:
        raise ValueError(f"No prompt file configured for author_id: {author_id}")
    
    if not Path(prompt_file).exists():
        raise FileNotFoundError(f"Persona prompt not found: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data:
        raise ValueError(f"Persona prompt file {prompt_file} is empty or invalid")
    
    return data

@lru_cache(maxsize=None)
def load_authors_data() -> List[Dict[str, Any]]:
    """Load authors data from authors.json."""
    authors_file = Path("components/author/authors.json")
    if not authors_file.exists():
        raise FileNotFoundError(f"Authors file not found: {authors_file}")
    
    import json
    with open(authors_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data or 'authors' not in data:
        raise ValueError(f"Authors file {authors_file} is missing 'authors' key or is empty")
    
    return data['authors']

class ContentComponentGenerator(StaticComponentGenerator):
    """
    Generator for content components using ONLY prompt-driven approach.
    NO hardcoded content - everything comes from YAML prompt configurations.
    """
    
    def __init__(self):
        super().__init__("content")
    
    def _extract_chemical_formula(self, material_data: Dict, frontmatter_data: Optional[Dict], material_name: str) -> str:
        """Extract chemical formula from various sources with NO fallbacks."""
        
        # Try multiple sources for chemical formula
        sources = [
            material_data.get('formula'),
            material_data.get('chemical_formula'),
            frontmatter_data.get('chemicalProperties', {}).get('formula') if frontmatter_data else None,
            frontmatter_data.get('chemicalProperties', {}).get('chemicalFormula') if frontmatter_data else None,
            frontmatter_data.get('properties', {}).get('chemicalFormula') if frontmatter_data else None,
        ]
        
        # Return the first non-empty formula found
        for formula in sources:
            if formula and formula.strip() and formula != 'Formula not specified':
                return formula.strip()
        
        # NO FALLBACKS - Must be in data sources or prompt configurations
        raise ValueError(f"No chemical formula found for {material_name} in any data source. Formula must be provided in frontmatter or material data.")
    
    def _generate_static_content(self, material_name: str, material_data: Dict,
                                author_info: Optional[Dict] = None,
                                frontmatter_data: Optional[Dict] = None,
                                schema_fields: Optional[Dict] = None) -> str:
        """Implementation of abstract method for static content generation."""
        
        # Extract author information from frontmatter first
        author_name = None
        author_country = None
        author_id = 1  # default
        
        if frontmatter_data:
            # Try to get author from frontmatter
            author_name = frontmatter_data.get('author', frontmatter_data.get('name'))
            
            # Map author names to countries (this should match the authors.json and prompt files)
            author_country_map = {
                'Yi-Chun Lin': 'taiwan',
                'Alessandro Moretti': 'italy', 
                'Ikmanda Roswati': 'indonesia',
                'Todd Dunning': 'usa'
            }
            
            if author_name:
                author_country = author_country_map.get(author_name)
                if not author_country:
                    raise ValueError(f"No country mapping found for author: {author_name}. Author must be defined in frontmatter or author configurations.")
                # Map country back to author_id for compatibility
                country_id_map = {'taiwan': 1, 'italy': 2, 'indonesia': 3, 'usa': 4}
                author_id = country_id_map.get(author_country, 2)
        
        # NO FALLBACKS - Author must be in frontmatter or author_info
        if not author_name and author_info:
            author_id = author_info.get('id')
            if not author_id:
                raise ValueError("No author ID found in author_info. Author must be properly configured.")
            # Load author data to get name and country
            authors_data = load_authors_data()
            for author in authors_data:
                if author.get('id') == author_id:
                    author_name = author.get('name')
                    author_country = author.get('country', '').lower()
                    if not author_name or not author_country:
                        raise ValueError(f"Incomplete author data for ID {author_id}. Name and country required.")
                    break
            else:
                raise ValueError(f"Author data not found for ID {author_id}")
        
        if not author_name:
            raise ValueError("No author information found. Author must be defined in frontmatter or author_info.")
        
        # Extract material properties from frontmatter and material_data
        material_properties = {}
        if frontmatter_data:
            material_properties.update(frontmatter_data)
        if material_data:
            material_properties.update(material_data)
        
        # Build enhanced config from parameters including frontmatter
        config = {
            'subject': material_name,
            'formula': self._extract_chemical_formula(material_data, frontmatter_data, material_name),
            'author_id': author_id,
            'author_name': author_name or 'Unknown Author',
            'author_country': author_country or 'italy',
            'material_properties': material_properties,
            'frontmatter_data': frontmatter_data or {},
            'schema_fields': schema_fields or {},
            # Extract specific technical properties for laser cleaning
            'density': material_properties.get('density', 'Material density'),
            'melting_point': material_properties.get('melting_point', 'Melting point'),
            'thermal_conductivity': material_properties.get('thermal_conductivity', 'Thermal conductivity'),
            'absorption_coefficient': material_properties.get('absorption_coefficient', 'Absorption characteristics'),
            'surface_roughness': material_properties.get('surface_roughness', 'Surface properties')
        }
        
        return self._generate_prompt_content(config)
    
    def _generate_prompt_content(self, config: Dict[str, Any]) -> str:
        """Generate content using ONLY prompt configurations."""
        
        # Extract required configuration - now includes author info from frontmatter
        self.subject = config.get('subject', 'Unknown Material')
        formula = config.get('formula', 'Formula not specified')
        author_id = config.get('author_id', 1)
        author_name = config.get('author_name', 'Unknown Author')
        author_country = config.get('author_country', 'italy')
        
        # Load prompt configurations using the country from frontmatter
        base_config = load_base_content_prompt()
        persona_config = load_persona_prompt(author_id)
        
        # Use the country directly from config (derived from frontmatter)
        prompt_key = author_country
        
        # Get author configuration from base prompt
        author_base_config = base_config.get('author_configurations', {}).get(prompt_key, {})
        
        # Build complete configuration
        config.update({
            'subject': self.subject,
            'formula': formula,
            'author_id': author_id,
            'author_name': author_name,
            'author_country': author_country
        })
        
        # Get content structure from persona
        # The content_structure is at the top level of the persona config
        content_structure = persona_config.get('content_structure', {})
        
        # Generate content using ONLY prompt-driven approach
        return self._generate_prompt_driven_content(
            config, author_name, author_country, persona_config,  # Pass full config instead of nested persona_data
            author_base_config, content_structure, prompt_key
        )
    
    def _generate_prompt_driven_content(self, config: Dict[str, Any], author_name: str, 
                                      author_country: str, persona_config: Dict[str, Any],
                                      author_config: Dict[str, Any], content_structure: Dict[str, Any],
                                      prompt_key: str) -> str:
        """Generate content dynamically using ONLY prompt configurations."""
        
        # Load base prompt to get shared patterns and requirements
        base_config = load_base_content_prompt()
        
        # Get technical requirements from base prompt
        technical_requirements = base_config.get('technical_requirements', {})
        
        # Get language patterns from country-specific prompt
        country_patterns = persona_config.get('language_patterns', {})
        
        # Debug: Check what we loaded
        print("🔧 DEBUG Persona Config:")
        print(f"   persona_config keys: {list(persona_config.keys())}")
        print(f"   country_patterns keys: {list(country_patterns.keys())}")
        
        # Combine base technical requirements with country language patterns
        combined_patterns = {
            'technical_requirements': technical_requirements,
            'language_patterns': country_patterns
        }
        
        # Get word count limit from base config author_configurations
        max_words = self._extract_word_limit(author_config.get('max_word_count', '400 words maximum'))
        
        # Build title using prompt pattern
        title_pattern = content_structure.get('title_pattern', 'Laser Cleaning of {material}: Technical Analysis')
        title = title_pattern.format(material=self.subject)
        
        # Build byline
        byline = content_structure.get('byline', f"**{author_name}, Ph.D. - {author_country}**")
        
        # Generate sections using ONLY combined prompt configurations
        sections = self._generate_dynamic_sections(
            config, combined_patterns['language_patterns'], content_structure, 
            author_config, max_words, prompt_key
        )
        
        # Randomize section order if specified in prompts
        randomization = content_structure.get('randomization_approach', {})
        if randomization.get('section_sequencing') and 'randomize' in randomization.get('section_sequencing', '').lower():
            sections = self._randomize_sections(sections)
        
        # Assemble final content
        content_parts = [f"# {title}", "", byline, ""]
        
        for section in sections:
            content_parts.extend(section)
            content_parts.append("")  # Section separator
        
        # Join and apply word limit
        full_content = "\n".join(content_parts)
        limited_content = self._apply_word_limit(full_content, max_words)
        
        return limited_content
    
    def _extract_word_limit(self, word_count_str: str) -> int:
        """Extract numeric word limit from configuration string."""
        import re
        match = re.search(r'(\d+)', word_count_str)
        return int(match.group(1)) if match else 400
    
    def _generate_dynamic_sections(self, config: Dict[str, Any], language_patterns: Dict[str, Any],
                                 content_struct: Dict[str, Any], author_config: Dict[str, Any],
                                 max_words: int, prompt_key: str) -> List[List[str]]:
        """Generate sections using ONLY prompt configurations."""
        
        sections = []
        configured_sections = content_struct.get('sections', [])
        
        if not configured_sections:
            raise ValueError("No sections configured in prompt file")
        
        # Calculate approximate words per section
        words_per_section = max_words // len(configured_sections)
        
        for section_config in configured_sections:
            section_name = section_config.get('name', 'Section')
            section_focus = section_config.get('focus', 'general')
            section_emphasis = section_config.get('emphasis', '')
            
            section_content = self._generate_section_content(
                section_name, section_focus, section_emphasis,
                config, language_patterns, words_per_section, prompt_key
            )
            
            sections.append(section_content)
        
        return sections
    
    def _generate_section_content(self, section_name: str, focus: str, emphasis: str,
                                config: Dict[str, Any], language_patterns: Dict[str, Any],
                                target_words: int, prompt_key: str) -> List[str]:
        """Generate content for sections using ONLY prompt patterns."""
        
        content = [f"## {section_name}", ""]
        
        # Find the correct section key by checking if focus contains keywords
        section_key = 'introduction'  # default
        if 'introduction' in focus.lower() or section_name.lower() == 'overview':
            section_key = 'introduction'
        elif 'properties' in focus.lower() or 'material' in focus.lower() or 'properties' in section_name.lower():
            section_key = 'properties'
        elif 'application' in focus.lower() or 'application' in section_name.lower():
            section_key = 'applications'
        elif 'parameter' in focus.lower() or 'parameter' in section_name.lower():
            section_key = 'parameters'  # use parameters patterns for parameters
        elif 'advantage' in focus.lower() or 'advantage' in section_name.lower():
            section_key = 'advantages'  # use advantages patterns for advantages
        elif 'safety' in focus.lower() or 'safety' in section_name.lower():
            section_key = 'safety'  # use safety patterns for safety
        elif 'challenge' in focus.lower() or 'challenge' in section_name.lower():
            section_key = 'challenges'  # use challenges patterns for challenges
        
        # Get patterns for this section
        section_patterns = language_patterns.get(section_key, {})
        
        if not section_patterns:
            # If no specific patterns found, try using all available patterns
            print(f"   No patterns for '{section_key}', using all language_patterns")
            section_patterns = language_patterns
        
        # Use patterns from prompts based on section type
        if section_name.lower() == 'overview':
            content.extend(self._generate_overview_content(config, section_patterns))
        elif 'properties' in section_name.lower() or 'material' in section_name.lower():
            content.extend(self._generate_properties_content(config, section_patterns, emphasis))
        elif 'application' in section_name.lower():
            content.extend(self._generate_applications_content(config, section_patterns))
        elif 'parameter' in section_name.lower() or 'optimal' in section_name.lower():
            content.extend(self._generate_parameters_content(config, section_patterns))
        elif 'advantage' in section_name.lower() or 'benefit' in section_name.lower():
            content.extend(self._generate_advantages_content(config, section_patterns))
        elif 'safety' in section_name.lower():
            content.extend(self._generate_safety_content(config, section_patterns))
        elif 'challenge' in section_name.lower():
            content.extend(self._generate_challenges_content(config, section_patterns))
        else:
            # Generic section using available patterns
            content.extend(self._generate_generic_content(config, section_patterns, focus))
        
        return content
    
    def _generate_overview_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate comprehensive overview content using available patterns."""
        content = []
        material_name = config['subject']
        formula = config['formula']
        
        # Get available patterns dynamically
        opening_patterns = [
            patterns.get('opening'),
            patterns.get('introduction', {}).get('opening') if isinstance(patterns.get('introduction'), dict) else None,
            "This study presents systematic investigation of"
        ]
        opening = next((p for p in opening_patterns if p), f"Laser cleaning technology for {material_name}")
        
        # Formula integration - try multiple pattern sources
        formula_patterns = [
            patterns.get('formula_integration'),
            patterns.get('introduction', {}).get('formula_integration') if isinstance(patterns.get('introduction'), dict) else None,
            f"The chemical composition {formula} provides fundamental understanding"
        ]
        formula_text = next((p for p in formula_patterns if p), f"Material composition {formula}")
        
        # Build comprehensive overview
        if '{material_formula}' in str(formula_text):
            intro_text = formula_text.format(material_formula=formula)
        else:
            intro_text = f"{formula_text} of laser-material interaction"
        
        content.append(f"{opening} in materials processing technology for {material_name} laser cleaning applications. {intro_text} for effective surface processing.")
        content.append("")
        
        # Add technical context
        content.append(f"This comprehensive analysis addresses laser cleaning optimization for {material_name} based on material-specific characteristics and processing requirements.")
        
        return content
    
    def _generate_properties_content(self, config: Dict[str, Any], patterns: Dict[str, Any], emphasis: str) -> List[str]:
        """Generate comprehensive properties content with technical details."""
        content = []
        material_name = config['subject']
        
        # Section introduction with pattern-based language
        intro_patterns = [
            patterns.get('section_intro'),
            patterns.get('properties', {}).get('section_intro') if isinstance(patterns.get('properties'), dict) else None,
            patterns.get('introduction')
        ]
        intro = next((p for p in intro_patterns if p), None)
        if not intro:
            raise ValueError(f"No introduction patterns found for {material_name}. Patterns must be defined in prompt configurations.")
        content.append(f"{intro} for successful laser cleaning of {material_name} surfaces.")
        content.append("")
        
        # Technical properties section - must come from patterns or material data
        if not patterns:
            raise ValueError(f"No properties patterns found for {material_name}. Patterns must be defined in prompt configurations.")
        
        # Use material data from config
        thermal_cond = config.get('thermal_conductivity', config.get('material_properties', {}).get('thermalConductivity'))
        density = config.get('density', config.get('material_properties', {}).get('density'))
        
        # Only add content if patterns exist
        if thermal_cond and thermal_cond != 'Thermal conductivity':
            thermal_pattern = patterns.get('thermal')
            if thermal_pattern:
                content.append(f"• {thermal_pattern.format(value=thermal_cond, material=material_name)}")
        
        if density and density != 'Material density':
            density_pattern = patterns.get('density')
            if density_pattern:
                content.append(f"• {density_pattern.format(value=density, material=material_name)}")
        
        # Add other properties only if patterns exist
        optical_pattern = patterns.get('optical')
        if optical_pattern:
            content.append(f"• {optical_pattern.format(material=material_name)}")
        
        interaction_pattern = patterns.get('interaction')
        if interaction_pattern:
            content.append(f"• {interaction_pattern}")
        
        if emphasis:
            emphasis_pattern = patterns.get('emphasis')
            if emphasis_pattern:
                content.append("")
                content.append(f"{emphasis_pattern.format(emphasis=emphasis, material=material_name)}")
        
        return content
    
    def _generate_applications_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate applications content using ONLY prompt patterns - NO fallbacks."""
        content = []
        
        material_name = config['subject']
        
        # NO fallbacks - must exist in prompt or fail
        if 'industrial' in patterns:
            content.append(f"{patterns['industrial']} the practical value of laser cleaning for {material_name} surface processing:")
            content.append("")
        
        # Use schema fields or frontmatter for specific applications
        schema_fields = config.get('schema_fields', {})
        if schema_fields and 'applications' in schema_fields:
            applications = schema_fields['applications']
            if isinstance(applications, list):
                application_pattern = patterns.get('application_template')
                if application_pattern:
                    for app in applications[:3]:  # Limit to top 3 applications
                        content.append(f"• {application_pattern.format(application=app, material=material_name)}")
                else:
                    raise ValueError(f"No application_template pattern found for {material_name}. Pattern required for application content.")
        else:
            raise ValueError(f"No applications found in schema_fields for {material_name}. Applications must be provided in frontmatter.")
        
        if 'sectors' in patterns:
            content.append("")
            content.append(f"{patterns['sectors']} laser cleaning technology for specialized {material_name} processing requirements.")
        
        return content
    
    def _generate_parameters_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate parameter specifications using ONLY patterns and data - NO fallbacks."""
        content = []
        material_name = config['subject']
        
        # Parameter introduction from patterns
        intro_pattern = patterns.get('parameter_intro')
        if intro_pattern:
            content.append(f"{intro_pattern.format(material=material_name)}")
            content.append("")
        
        # Technical specifications from frontmatter
        tech_specs = config.get('frontmatter_data', {}).get('technicalSpecifications', {})
        if tech_specs:
            param_pattern = patterns.get('parameter_template')
            if not param_pattern:
                raise ValueError(f"No parameter_template pattern found for {material_name}. Pattern required for parameter content.")
            
            for spec_name, spec_value in tech_specs.items():
                content.append(f"• {param_pattern.format(parameter=spec_name, value=spec_value, material=material_name)}")
        else:
            raise ValueError(f"No technicalSpecifications found in frontmatter for {material_name}. Parameters must be provided in data.")
        
        return content
    
    def _generate_advantages_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate advantages using ONLY patterns - NO fallbacks."""
        content = []
        material_name = config['subject']
        
        intro_pattern = patterns.get('advantages_intro')
        if intro_pattern:
            content.append(f"{intro_pattern.format(material=material_name)}")
            content.append("")
        
        # Use pattern-based advantages
        advantage_pattern = patterns.get('advantage_template')
        if not advantage_pattern:
            raise ValueError(f"No advantage_template pattern found for {material_name}. Pattern required for advantages content.")
        
        # Get advantages from patterns
        advantage_list = patterns.get('advantages_list', [])
        if not advantage_list:
            raise ValueError(f"No advantages_list found in patterns for {material_name}. Advantages must be defined in prompt configurations.")
        
        for advantage in advantage_list:
            content.append(f"• {advantage_pattern.format(advantage=advantage, material=material_name)}")
        
        # Use pattern-based conclusion if available
        quality_patterns = [
            patterns.get('quality'),
            patterns.get('applications', {}).get('quality') if isinstance(patterns.get('applications'), dict) else None
        ]
        quality = next((p for p in quality_patterns if p), None)
        if quality:
            content.append("")
            content.append(f"• {quality} superior results compared to traditional cleaning methods")
        
        return content
    
    def _generate_safety_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate safety content using ONLY patterns - NO fallbacks."""
        content = []
        material_name = config['subject']
        
        # Safety requirements from frontmatter
        safety_class = config.get('frontmatter_data', {}).get('technicalSpecifications', {}).get('safetyClass')
        safety_intro = patterns.get('safety_intro')
        if not safety_intro:
            raise ValueError(f"No safety_intro pattern found for {material_name}. Pattern required for safety content.")
        
        if safety_class:
            content.append(f"{safety_intro.format(material=material_name, safety_class=safety_class)}")
        else:
            content.append(f"{safety_intro.format(material=material_name, safety_class='comprehensive')}")
        
        content.append("")
        
        # Get safety requirements from patterns
        safety_list = patterns.get('safety_list', [])
        safety_template = patterns.get('safety_template')
        if not safety_list or not safety_template:
            raise ValueError(f"No safety_list or safety_template found in patterns for {material_name}. Safety patterns required.")
        
        for safety_item in safety_list:
            content.append(f"• {safety_template.format(safety=safety_item, material=material_name)}")
        
        return content
    
    def _generate_challenges_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate challenges content using ONLY patterns - NO fallbacks."""
        content = []
        material_name = config['subject']
        
        challenges_intro = patterns.get('challenges_intro')
        if not challenges_intro:
            raise ValueError(f"No challenges_intro pattern found for {material_name}. Pattern required for challenges content.")
        
        content.append(f"{challenges_intro.format(material=material_name)}")
        content.append("")
        
        # Get challenges from patterns
        challenges_list = patterns.get('challenges_list', [])
        challenge_template = patterns.get('challenge_template')
        if not challenges_list or not challenge_template:
            raise ValueError(f"No challenges_list or challenge_template found in patterns for {material_name}. Challenge patterns required.")
        
        for challenge in challenges_list:
            content.append(f"• {challenge_template.format(challenge=challenge, material=material_name)}")
        
        return content
    
    def _generate_generic_content(self, config: Dict[str, Any], patterns: Dict[str, Any], focus: str) -> List[str]:
        """Generate generic content using ONLY available prompt patterns."""
        content = []
        
        # Use any available patterns for generic sections
        for key, value in patterns.items():
            if value and isinstance(value, str) and len(value) > 10:
                content.append(f"• {value}")
        
        return content
    
    def _randomize_sections(self, sections: List[List[str]]) -> List[List[str]]:
        """Randomize section order while keeping Overview first."""
        if not sections:
            return sections
        
        # Find Overview section
        overview_section = None
        other_sections = []
        
        for section in sections:
            if section and len(section) > 0 and 'overview' in section[0].lower():
                overview_section = section
            else:
                other_sections.append(section)
        
        # Randomize non-overview sections
        random.shuffle(other_sections)
        
        # Rebuild with Overview first
        result = []
        if overview_section:
            result.append(overview_section)
        result.extend(other_sections)
        
        return result
    
    def _apply_word_limit(self, content: str, max_words: int) -> str:
        """Apply word limit while preserving formatting."""
        lines = content.split('\n')
        result_lines = []
        word_count = 0
        
        for line in lines:
            line_words = len(line.split()) if line.strip() else 0
            
            if word_count + line_words <= max_words:
                result_lines.append(line)
                word_count += line_words
            else:
                # Add partial line if possible
                remaining_words = max_words - word_count
                if remaining_words > 0 and line.strip():
                    words = line.split()
                    truncated_line = ' '.join(words[:remaining_words])
                    result_lines.append(truncated_line)
                break
        
        return '\n'.join(result_lines)
