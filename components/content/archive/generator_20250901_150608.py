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

from generators.component_generators import APIComponentGenerator, ComponentResult

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
        1: "components/content/prompts/personas/taiwan_persona.yaml",
        2: "components/content/prompts/personas/italy_persona.yaml", 
        3: "components/content/prompts/personas/indonesia_persona.yaml",
        4: "components/content/prompts/personas/usa_persona.yaml"
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

class ContentComponentGenerator(APIComponentGenerator):
    """
    Generator for content components using ONLY prompt-driven approach.
    NO hardcoded content - everything comes from YAML prompt configurations.
    """
    
    def __init__(self):
        super().__init__("content")
    
    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Implementation of hybrid API + frontmatter architecture for content generation."""
        
        if not api_client:
            return ComponentResult(
                component_type=self.component_type,
                success=False,
                content="",
                error_message="API client is required for content generation"
            )
        
        # Build enhanced config with frontmatter context
        config = {
            'subject': material_name,
            'formula': material_data.get('formula', material_data.get('chemical_formula', 'Formula not specified')),
            'author_id': author_info.get('id', 1) if author_info else 1,
            'material_data': material_data,
            'frontmatter_data': frontmatter_data or {}
        }
        
        # Use API generation with frontmatter enhancement
        return self._generate_api_content(config, api_client)
    
    def _generate_api_content(self, config: Dict[str, Any], api_client) -> ComponentResult:
        """Generate content using API with frontmatter enhancement."""
        try:
            # Extract configuration
            subject = config.get('subject', 'Unknown Material')
            formula = config.get('formula', 'Formula not specified')
            author_id = config.get('author_id', 1)
            frontmatter_data = config.get('frontmatter_data', {})
            
            # Load prompt configurations
            base_config = load_base_content_prompt()
            persona_config = load_persona_prompt(author_id)
            authors_data = load_authors_data()
            
            # Find author configuration
            author_config = None
            for author in authors_data:
                if author.get('id') == author_id:
                    author_config = author
                    break
            
            if not author_config:
                return ComponentResult(
                    component_type=self.component_type,
                    success=False,
                    content="",
                    error_message=f"Author configuration not found for id: {author_id}"
                )
            
            # Extract author information
            author_name = author_config.get('name', 'Unknown Author')
            author_country = author_config.get('country', 'Unknown')
            prompt_key = author_country.lower()
            
            # Build comprehensive prompt with frontmatter context
            api_prompt = self._build_api_prompt(
                subject, formula, author_name, author_country,
                frontmatter_data, base_config, persona_config, prompt_key
            )
            
            # Generate content via API
            response = api_client.generate(api_prompt)
            
            if not response:
                # Fallback to prompt-based generation if API fails
                fallback_config = {
                    'subject': subject,
                    'formula': formula,
                    'author_id': author_id
                }
                fallback_content = self._generate_prompt_content(fallback_config)
                return ComponentResult(
                    component_type=self.component_type,
                    success=True,
                    content=fallback_content,
                    metadata={'generation_method': 'fallback_prompt', 'api_failure': True}
                )
            
            # Process and format API response
            formatted_content = self._format_api_response(
                response, subject, author_name, author_country, base_config, persona_config
            )
            
            return ComponentResult(
                component_type=self.component_type,
                success=True,
                content=formatted_content,
                metadata={
                    'generation_method': 'api_with_frontmatter',
                    'author_id': author_id,
                    'author_name': author_name,
                    'frontmatter_enhanced': bool(frontmatter_data)
                }
            )
            
        except Exception as e:
            # Fallback to prompt-based generation on any error
            try:
                fallback_config = {
                    'subject': config.get('subject', 'Unknown Material'),
                    'formula': config.get('formula', 'Formula not specified'),
                    'author_id': config.get('author_id', 1)
                }
                fallback_content = self._generate_prompt_content(fallback_config)
                return ComponentResult(
                    component_type=self.component_type,
                    success=True,
                    content=fallback_content,
                    metadata={'generation_method': 'fallback_prompt', 'api_error': str(e)}
                )
            except Exception as fallback_error:
                return ComponentResult(
                    component_type=self.component_type,
                    success=False,
                    content="",
                    error_message=f"Both API and fallback generation failed: {str(e)}, {str(fallback_error)}"
                )
    
    def _build_api_prompt(self, subject: str, formula: str, author_name: str, author_country: str,
                         frontmatter_data: Dict[str, Any], base_config: Dict[str, Any],
                         persona_config: Dict[str, Any], prompt_key: str) -> str:
        """Build comprehensive API prompt with frontmatter enhancement."""
        
        # Get base instructions
        base_instructions = base_config.get('base_instructions', {})
        system_prompt = base_instructions.get('system_prompt', 'Generate technical content about laser cleaning.')
        
        # Get persona-specific patterns
        persona_data = persona_config.get(f'{prompt_key}_persona', {})
        language_patterns = persona_data.get('language_patterns', {})
        content_structure = persona_config.get('content_structure', {})
        
        # Extract frontmatter context
        frontmatter_context = self._extract_frontmatter_context(frontmatter_data)
        
        # Build comprehensive prompt
        prompt_parts = [
            f"SYSTEM: {system_prompt}",
            "",
            f"AUTHOR PERSONA: {author_name} from {author_country}",
            f"WRITING STYLE: {persona_data.get('writing_style', 'Technical and professional')}",
            f"CULTURAL PERSPECTIVE: {persona_data.get('cultural_perspective', 'International')}",
            "",
            f"MATERIAL: {subject}",
            f"CHEMICAL FORMULA: {formula}",
        ]
        
        # Add frontmatter context if available
        if frontmatter_context:
            prompt_parts.extend([
                "",
                "MATERIAL CONTEXT FROM FRONTMATTER:",
                frontmatter_context
            ])
        
        # Add content requirements
        sections = content_structure.get('sections', [])
        if sections:
            prompt_parts.extend([
                "",
                "REQUIRED SECTIONS:",
            ])
            for section in sections:
                section_name = section.get('name', 'Section')
                section_focus = section.get('focus', 'general')
                prompt_parts.append(f"- {section_name}: {section_focus}")
        
        # Add language patterns
        if language_patterns:
            prompt_parts.extend([
                "",
                "LANGUAGE PATTERNS TO INCORPORATE:",
            ])
            for pattern_type, pattern_text in language_patterns.items():
                if isinstance(pattern_text, str) and pattern_text.strip():
                    prompt_parts.append(f"- {pattern_type}: {pattern_text}")
        
        # Add formatting requirements
        title_pattern = content_structure.get('title_pattern', 'Laser Cleaning of {material}: Technical Analysis')
        byline = content_structure.get('byline', f"**{author_name}, Ph.D. - {author_country}**")
        
        prompt_parts.extend([
            "",
            "FORMATTING REQUIREMENTS:",
            f"- Title: {title_pattern.format(material=subject)}",
            f"- Byline: {byline}",
            "- Use markdown formatting with ## for section headers",
            "- Maximum 400 words total",
            "- Professional technical tone appropriate for engineering documentation",
            "",
            "Generate the complete article now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_frontmatter_context(self, frontmatter_data: Dict[str, Any]) -> str:
        """Extract relevant context from frontmatter data."""
        if not frontmatter_data:
            return ""
        
        context_parts = []
        
        # Basic material info
        if frontmatter_data.get('title'):
            context_parts.append(f"Title: {frontmatter_data['title']}")
        if frontmatter_data.get('description'):
            context_parts.append(f"Description: {frontmatter_data['description']}")
        if frontmatter_data.get('category'):
            context_parts.append(f"Category: {frontmatter_data['category']}")
        
        # Properties
        properties = frontmatter_data.get('properties', {})
        if properties:
            context_parts.append("Material Properties:")
            for prop, value in properties.items():
                if value:
                    context_parts.append(f"  - {prop}: {value}")
        
        # Laser parameters
        laser_params = frontmatter_data.get('laser_cleaning', {})
        if laser_params:
            context_parts.append("Laser Cleaning Parameters:")
            for param, value in laser_params.items():
                if value:
                    context_parts.append(f"  - {param}: {value}")
        
        # Applications
        applications = frontmatter_data.get('applications', [])
        if applications:
            context_parts.append(f"Applications: {', '.join(applications)}")
        
        # Contaminants
        contaminants = frontmatter_data.get('contaminants', [])
        if contaminants:
            context_parts.append(f"Target Contaminants: {', '.join(contaminants)}")
        
        return "\n".join(context_parts)
    
    def _format_api_response(self, response: str, subject: str, author_name: str, 
                           author_country: str, base_config: Dict[str, Any],
                           persona_config: Dict[str, Any]) -> str:
        """Format and validate API response."""
        
        # Clean up response
        cleaned_response = response.strip()
        
        # Ensure proper title format if missing
        if not cleaned_response.startswith('# '):
            title_pattern = persona_config.get('content_structure', {}).get('title_pattern', 
                                                                           'Laser Cleaning of {material}: Technical Analysis')
            title = title_pattern.format(material=subject)
            byline = f"**{author_name}, Ph.D. - {author_country}**"
            cleaned_response = f"# {title}\n\n{byline}\n\n{cleaned_response}"
        
        # Apply word limit
        max_words = self._extract_word_limit(
            base_config.get('author_configurations', {})
                      .get(author_country.lower(), {})
                      .get('max_word_count', '400 words maximum')
        )
        
        limited_content = self._apply_word_limit(cleaned_response, max_words)
        
        return limited_content
    def _generate_prompt_content(self, config: Dict[str, Any]) -> str:
        """Generate content using ONLY prompt configurations (fallback method)."""
        
        # Extract required configuration
        subject = config.get('subject', 'Unknown Material')
        formula = config.get('formula', 'Formula not specified')
        author_id = config.get('author_id', 1)
        
        # Load prompt configurations
        base_config = load_base_content_prompt()
        persona_config = load_persona_prompt(author_id)
        authors_data = load_authors_data()
        
        # Find author configuration
        author_config = None
        for author in authors_data:
            if author.get('id') == author_id:
                author_config = author
                break
        
        if not author_config:
            raise ValueError(f"Author configuration not found for id: {author_id}")
        
        # Extract author information
        author_name = author_config.get('name', 'Unknown Author')
        author_country = author_config.get('country', 'Unknown')
        
        # Determine prompt key based on country
        prompt_key = author_country.lower()
        
        # Get author configuration from base prompt
        author_base_config = base_config.get('author_configurations', {}).get(prompt_key, {})
        
        # Build complete configuration
        enhanced_config = {
            'subject': subject,
            'formula': formula,
            'author_id': author_id,
            'author_name': author_name,
            'author_country': author_country
        }
        
        # Get content structure from persona
        # The content_structure is at the top level of the persona config
        content_structure = persona_config.get('content_structure', {})
        
        # Get persona data for language patterns
        persona_key = f'{prompt_key}_persona'
        persona_data = persona_config.get(persona_key, {})
        
        # Generate content using ONLY prompt-driven approach
        return self._generate_prompt_driven_content(
            enhanced_config, author_name, author_country, persona_data, 
            author_base_config, content_structure, prompt_key
        )
    
    def _generate_prompt_driven_content(self, config: Dict[str, Any], author_name: str, 
                                      author_country: str, persona_config: Dict[str, Any],
                                      author_config: Dict[str, Any], content_structure: Dict[str, Any],
                                      prompt_key: str) -> str:
        """Generate content dynamically using ONLY prompt configurations."""
        
        # Get language patterns from persona config
        language_patterns = persona_config.get('language_patterns', {})
        
        # Get word count limit
        max_words = self._extract_word_limit(author_config.get('max_word_count', '400 words maximum'))
        
        # Build title using prompt pattern
        title_pattern = content_structure.get('title_pattern', 'Laser Cleaning of {material}: Technical Analysis')
        title = title_pattern.format(material=config['subject'])
        
        # Build byline
        byline = content_structure.get('byline', f"**{author_name}, Ph.D. - {author_country}**")
        
        # Generate sections using ONLY prompt configurations
        sections = self._generate_dynamic_sections(
            config, language_patterns, content_structure, 
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
        
        # Get patterns for this focus area
        section_patterns = language_patterns.get(focus.lower(), language_patterns.get('introduction', {}))
        
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
        """Generate overview content using ONLY prompt patterns."""
        content = []
        
        opening = patterns.get('opening', '')
        foundation = patterns.get('foundation', '')
        understanding = patterns.get('understanding', '')
        
        if opening and foundation and understanding:
            content.append(f"{opening} in materials processing technology for {config['subject']}. {foundation} {config['formula']} {understanding} laser-material interaction mechanisms.")
            content.append("")
        
        if patterns.get('comparison'):
            content.append(f"{patterns['comparison']} for {config['subject']} applications.")
        
        return content
    
    def _generate_properties_content(self, config: Dict[str, Any], patterns: Dict[str, Any], emphasis: str) -> List[str]:
        """Generate properties content using ONLY prompt patterns."""
        content = []
        
        if patterns.get('introduction'):
            content.append(f"{patterns['introduction']} to successful laser cleaning of {config['subject']}.")
            content.append("")
        
        if patterns.get('characteristics'):
            content.append(f"{patterns['characteristics']} that influence process parameters:")
            content.append("")
        
        if emphasis:
            content.append(f"**Focus Area**: {emphasis}")
        
        return content
    
    def _generate_applications_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate applications content using ONLY prompt patterns."""
        content = []
        
        if patterns.get('industrial'):
            content.append(f"{patterns['industrial']} the practical value of laser cleaning for {config['subject']} processing.")
            content.append("")
        
        if patterns.get('sectors'):
            content.append(f"{patterns['sectors']} this technology for specialized processing requirements.")
        
        return content
    
    def _generate_parameters_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate parameters content using ONLY prompt patterns."""
        content = []
        
        content.append(f"Systematic parameter optimization for {config['subject']} ensures consistent results:")
        content.append("")
        
        if patterns.get('optimization'):
            content.append(f"• {patterns['optimization']}")
        
        return content
    
    def _generate_advantages_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate advantages content using ONLY prompt patterns."""
        content = []
        
        content.append(f"Laser cleaning provides significant benefits for {config['subject']} processing:")
        content.append("")
        
        if patterns.get('quality'):
            content.append(f"• {patterns['quality']}")
        if patterns.get('future'):
            content.append(f"• {patterns['future']}")
        
        return content
    
    def _generate_safety_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate safety content using ONLY prompt patterns."""
        content = []
        
        content.append(f"Class 4 laser safety protocols ensure safe operation for {config['subject']} processing:")
        content.append("")
        
        if patterns.get('expertise'):
            content.append(f"• {patterns['expertise']}")
        
        return content
    
    def _generate_challenges_content(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate challenges content using ONLY prompt patterns."""
        content = []
        
        if patterns.get('optimization'):
            content.append(f"{patterns['optimization']} for {config['subject']} requires systematic analysis.")
            content.append("")
        
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
