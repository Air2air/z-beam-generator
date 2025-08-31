#!/usr/bin/env python3
"""
Content Calculator - Author-Driven Content Generation
Optimized Python calculator for generating 4 distinct content variations based on author personas.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_frontmatter_data(frontmatter_file: str) -> Dict[str, Any]:
    """Load and parse frontmatter data from markdown file."""
    try:
        with open(frontmatter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter between --- markers
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                frontmatter_yaml = parts[1]
                return yaml.safe_load(frontmatter_yaml) or {}
        
        return {}
    except Exception as e:
        print(f"Error loading frontmatter: {e}")
        return {}

def load_authors_data() -> List[Dict[str, Any]]:
    """Load authors data from authors.json."""
    try:
        authors_file = Path("components/author/authors.json")
        if authors_file.exists():
            import json
            with open(authors_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('authors', [])
        return []
    except Exception as e:
        print(f"Error loading authors: {e}")
        return []

def load_base_content_prompt() -> Dict[str, Any]:
    """Load base content prompt with common instructions."""
    try:
        base_prompt_file = "components/content/prompts/base_content_prompt.yaml"
        if Path(base_prompt_file).exists():
            with open(base_prompt_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    except Exception as e:
        print(f"Error loading base content prompt: {e}")
        return {}

def get_dynamic_author_config(author_id: int, base_prompt: Dict[str, Any]) -> Dict[str, Any]:
    """Get author-specific configuration from dynamic base prompt."""
    author_map = {1: 'taiwan', 2: 'italy', 3: 'indonesia', 4: 'usa'}
    author_key = author_map.get(author_id, 'usa')
    
    # Extract author configuration from base prompt
    author_configs = base_prompt.get('author_configurations', {})
    author_config = author_configs.get(author_key, {})
    
    # Extract content parameters
    content_params = base_prompt.get('content_parameters', {}).get(author_key, {})
    
    # Extract formatting standards
    formatting = base_prompt.get('formatting_standards', {})
    title_pattern = formatting.get('title_patterns', {}).get(author_key, "Laser Cleaning of {material}")
    byline_pattern = formatting.get('byline_patterns', {}).get(author_key, "By Author")
    emphasis_style = formatting.get('emphasis_styles', {}).get(author_key, "bold for emphasis")
    
    return {
        'author_config': author_config,
        'content_parameters': content_params,
        'title_pattern': title_pattern,
        'byline_pattern': byline_pattern,
        'emphasis_style': emphasis_style,
        'section_templates': base_prompt.get('content_requirements', {}).get('core_technical_elements', {}).get('section_templates', {})
    }

def merge_base_and_persona_config(base_config: Dict[str, Any], persona_config: Dict[str, Any], author_id: int) -> Dict[str, Any]:
    """Merge dynamic base configuration with persona-specific settings."""
    # Get dynamic author configuration from base prompt
    dynamic_config = get_dynamic_author_config(author_id, base_config)
    
    # Start with persona config as base
    merged_config = persona_config.copy()
    
    # Override with dynamic base settings
    if 'content_structure' not in merged_config:
        merged_config['content_structure'] = {}
    
    # Update title and byline patterns
    merged_config['content_structure']['title_pattern'] = dynamic_config['title_pattern']
    merged_config['content_structure']['byline'] = dynamic_config['byline_pattern']
    
    # Update section order from author configuration
    author_config = dynamic_config['author_config']
    if 'content_order' in author_config:
        merged_config['content_structure']['sections'] = []
        for section_name in author_config['content_order']:
            merged_config['content_structure']['sections'].append({
                'name': section_name,
                'focus': f"dynamic focus for {section_name}",
                'emphasis': dynamic_config['author_config'].get('section_emphasis', 'standard approach')
            })
    
    # Add content parameters
    content_params = dynamic_config['content_parameters']
    if content_params:
        merged_config['content_structure'].update(content_params)
    
    # Add dynamic section templates for reference
    merged_config['section_templates'] = dynamic_config['section_templates']
    
    # Add base content requirements
    merged_config['base_requirements'] = base_config.get('content_requirements', {})
    
    return merged_config

def load_persona_prompt(author_id: int) -> Dict[str, Any]:
    """Load persona-specific prompt configuration."""
    try:
        prompt_files = {
            1: "components/content/prompts/taiwan_prompt.yaml",
            2: "components/content/prompts/italy_prompt.yaml", 
            3: "components/content/prompts/indonesia_prompt.yaml",
            4: "components/content/prompts/usa_prompt.yaml"
        }
        
        # Load base prompt first
        base_config = load_base_content_prompt()
        
        # Load persona-specific prompt
        prompt_file = prompt_files.get(author_id)
        if prompt_file and Path(prompt_file).exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                persona_config = yaml.safe_load(f) or {}
                
            # Merge base and persona configurations
            merged_config = {**base_config, **persona_config}
            return merged_config
        
        # Default fallback with base config
        return {**base_config, "writing_style": "professional", "length": "400-500 words"}
    except Exception as e:
        print(f"Error loading persona prompt: {e}")
        return {"writing_style": "professional", "length": "400-500 words"}

class ContentCalculator:
    """Advanced Python calculator for author-driven content generation."""
    
    def __init__(self, frontmatter_data: Dict[str, Any], author_id: int = 2):
        self.frontmatter_data = frontmatter_data
        self.author_id = author_id
        self.authors = load_authors_data()
        self.author_info = self._get_author_by_id(author_id)
        
        # Extract key material data
        self.subject = frontmatter_data.get('subject', 'Material')
        self.category = frontmatter_data.get('category', 'unknown')
        self.material_formula = self._extract_chemical_formula()
        
    def _get_author_by_id(self, author_id: int) -> Optional[Dict[str, Any]]:
        """Get author information by ID."""
        for author in self.authors:
            if author.get('id') == author_id:
                return author
        return None
    
    def _extract_chemical_formula(self) -> str:
        """Extract chemical formula from frontmatter properties."""
        properties = self.frontmatter_data.get('properties', {})
        
        # Look for chemical formula in various property fields
        formula_fields = ['chemicalFormula', 'formula', 'composition', 'chemicalComposition']
        for field in formula_fields:
            if field in properties:
                formula = properties[field]
                if isinstance(formula, str) and formula.strip():
                    return formula.strip()
        
        # Fallback based on subject/category
        subject_lower = self.subject.lower()
        if 'aluminum' in subject_lower or 'aluminium' in subject_lower:
            return 'Al₂O₃'
        elif 'steel' in subject_lower:
            return 'Fe₂O₃'
        elif 'copper' in subject_lower:
            return 'Cu₂O'
        elif 'titanium' in subject_lower:
            return 'TiO₂'
        else:
            return f'{self.subject}ₓOᵧ'
    
    def _get_author_persona_config(self) -> Dict[str, Any]:
        """Get author-specific configuration for content generation."""
        if not self.author_info:
            # Default to author 2 (Alessandro) if not found
            self.author_id = 2
            self.author_info = self._get_author_by_id(2)
        
        author_configs = {
            1: {  # Yi-Chun Lin (Taiwan)
                'style': 'precise_methodical',
                'length': (300, 450),
                'sections': ['Introduction', 'Material Properties & Laser Interaction', 'Optimal Parameters', 'Industrial Applications', 'Advantages', 'Challenges and Technical Solutions', 'Safety Considerations', 'Keywords'],
                'tone': 'empathetic_analytical',
                'emphasis': 'semiconductors_precision',
                'signature': 'humility_pedagogical'
            },
            2: {  # Alessandro Moretti (Italy)  
                'style': 'passionate_expressive',
                'length': (400, 600),
                'sections': ['Overview', 'Material Essence & Laser Dance', 'Real-World Elegance', 'Fine-Tuning the Beam', 'Why Laser Shines', 'Challenges and Technical Solutions', 'Safety Considerations and Protocols', 'Keywords'],
                'tone': 'passionate_narrative',
                'emphasis': 'heritage_aerospace',
                'signature': 'analogies_reflections'
            },
            3: {  # Ikmanda Roswati (Indonesia)
                'style': 'analytical_balanced', 
                'length': (350, 500),
                'sections': ['Overview', 'Advantages', 'Key Properties', 'Industrial Applications', 'Optimal Parameters', 'Challenges and Technical Solutions', 'Safety Considerations and Protocols', 'Keywords'],
                'tone': 'analytical_neutral',
                'emphasis': 'mining_tropical',
                'signature': 'repetitive_clarity'
            },
            4: {  # Todd Dunning (USA)
                'style': 'innovative_direct',
                'length': (250, 400), 
                'sections': ['Overview', 'Key Properties & Laser Interaction', 'Optimal Laser Parameters', 'Industrial Applications', 'Advantages Over Traditional Methods', 'Challenges and Solutions', 'Safety Protocols', 'Keywords'],
                'tone': 'conversational_optimistic',
                'emphasis': 'biomedical_semiconductor',
                'signature': 'forward_thinking'
            }
        }
        
        return author_configs.get(self.author_id, author_configs[2])
    
    def _generate_content_by_author(self) -> str:
        """Generate content based on author's actual country using YAML prompt configurations."""
        if not self.author_info:
            # Fallback to default Italian style
            return self._generate_italy_content_with_yaml({}, "Alessandro Moretti", "Italy", load_persona_prompt(2))
        
        # Get configuration based on author information
        author_id = self.author_info.get('id')
        author_name = self.author_info.get('name', 'Unknown Author')
        author_country = self.author_info.get('country', 'Unknown')
        
        # Load persona-specific prompt configuration
        persona_config = load_persona_prompt(author_id)
        
        # Build enhanced configuration
        config = {
            'subject': self.subject,
            'category': self.category,
            'formula': self.material_formula,
            'properties': self.frontmatter_data.get('properties', {}),
            'persona': persona_config
        }
        
        # Determine persona based on actual country, not ID
        if 'Taiwan' in author_country:
            return self._generate_taiwan_content_with_yaml(config, author_name, author_country, persona_config)
        elif 'Italy' in author_country:
            return self._generate_italy_content_with_yaml(config, author_name, author_country, persona_config)
        elif 'Indonesia' in author_country:
            return self._generate_indonesia_content_with_yaml(config, author_name, author_country, persona_config)
        elif 'United States' in author_country or 'USA' in author_country:
            return self._generate_usa_content_with_yaml(config, author_name, author_country, persona_config)
        else:
            # For new countries, default to professional academic style
            print(f"Warning: No specific persona for country '{author_country}', using professional academic style")
            return self._generate_professional_content_with_yaml(config, author_name, author_country, persona_config)
    
    def _generate_taiwan_content_with_yaml(self, config: Dict[str, Any], author_name: str, author_country: str, persona_config: Dict[str, Any]) -> str:
        """Generate content using Taiwan YAML prompt configuration with dynamic base prompt integration."""
        # Load base prompt and merge with persona configuration
        base_prompt = load_base_content_prompt()
        merged_config = merge_base_and_persona_config(base_prompt, persona_config, author_id=1)
        
        # Extract configuration elements
        patterns = merged_config.get('language_patterns', {})
        structure = merged_config.get('content_structure', {})
        section_templates = merged_config.get('section_templates', {})
        base_requirements = merged_config.get('base_requirements', {})
        
        # Use dynamic title pattern
        title = structure.get('title_pattern', "**Laser Cleaning of {material}: A Systematic Analysis**").format(material=self.subject)
        
        # Generate sections based on dynamic content order
        sections = []
        content_order = structure.get('sections', [])
        
        for section_info in content_order:
            section_name = section_info.get('name', '')
            section_focus = section_info.get('focus', '')
            
            if 'Overview' in section_name:
                sections.append(self._generate_overview_section(patterns, section_templates, title))
            elif 'Properties' in section_name:
                sections.append(self._generate_properties_section(patterns, section_templates))
            elif 'Applications' in section_name:
                sections.append(self._generate_applications_section(patterns, section_templates))
            elif 'Parameters' in section_name:
                sections.append(self._generate_parameters_section(patterns, section_templates))
            elif 'Advantages' in section_name:
                sections.append(self._generate_advantages_section(patterns, section_templates))
            elif 'Challenges' in section_name:
                sections.append(self._generate_challenges_section(patterns, section_templates))
            elif 'Safety' in section_name:
                sections.append(self._generate_safety_section(patterns, section_templates))
            elif 'Keywords' in section_name:
                sections.append(self._generate_keywords_section(patterns, section_templates))
        
        # Combine all sections
        content = '\n\n'.join(sections)
        
        # Add byline based on dynamic configuration
        byline = structure.get('byline', "By Yi-Chun Lin, Ph.D. in Laser Materials Processing")
        byline_position = structure.get('byline_position', 'top')
        
        if byline_position == 'top':
            return f"{byline}\n\n{content}"
        else:
            return f"{content}\n\n{byline}"

    def _generate_overview_section(self, patterns: Dict[str, Any], section_templates: Dict[str, Any], title: str) -> str:
        """Generate overview section using dynamic templates."""
        intro_patterns = patterns.get('introduction', {})
        return f"""# {title}

{intro_patterns.get('opening', 'This study presents systematic investigation of')} laser cleaning technology for {self.subject} materials. {intro_patterns.get('approach', 'The methodology employed follows established research protocols')} to evaluate cleaning efficiency and material integrity.

The chemical formula {self.material_formula} provides fundamental understanding for laser-material interactions. {intro_patterns.get('significance', 'The investigation demonstrates significant potential')} for {self.subject} processing in industrial applications."""

    def _generate_properties_section(self, patterns: Dict[str, Any], section_templates: Dict[str, Any]) -> str:
        """Generate properties section using dynamic templates."""
        properties_patterns = patterns.get('properties', {})
        return f"""## Material Properties and Laser Interaction

{properties_patterns.get('section_intro', 'Material characteristics require careful analysis')} to determine appropriate laser parameters. Key properties affecting {self.subject} laser cleaning include:

• **Absorption at 1064 nm**: {properties_patterns.get('optical', 'Optical properties demonstrate')} wavelength-dependent behavior
• **Thermal characteristics**: {properties_patterns.get('thermal', 'Thermal behavior shows')} controlled response patterns
• **Mechanical properties**: {properties_patterns.get('mechanical', 'Mechanical properties maintain')} structural integrity

{properties_patterns.get('conclusion', 'These characteristics indicate')} systematic parameter optimization is essential for effective cleaning results."""

    def _generate_applications_section(self, patterns: Dict[str, Any], section_templates: Dict[str, Any]) -> str:
        """Generate applications section using dynamic templates."""
        applications_patterns = patterns.get('applications', {})
        return f"""## Industrial Applications

{applications_patterns.get('industrial', 'Industrial implementation demonstrates')} practical viability for {self.subject} processing. {applications_patterns.get('semiconductors', 'Semiconductor applications show particular promise')} for precision cleaning requirements.

Manufacturing applications demonstrate {applications_patterns.get('efficiency', 'improved efficiency and sustainability')} compared to traditional chemical methods. {applications_patterns.get('quality', 'Quality control measures indicate')} consistent processing results.

{applications_patterns.get('conclusion', 'The systematic approach enables')} reliable implementation across multiple industrial sectors."""

    def _generate_parameters_section(self, patterns: Dict[str, Any], section_templates: Dict[str, Any]) -> str:
        """Generate parameters section using dynamic templates."""
        return f"""## Optimal Parameters

Systematic analysis reveals optimal laser parameters for {self.subject} cleaning:

• **Wavelength**: 1064 nm fiber laser provides optimal absorption
• **Pulse Duration**: 10-100 nanosecond pulses ensure controlled material removal
• **Fluence**: Energy density optimized for material-specific thresholds
• **Repetition Rate**: Frequency adjusted for processing speed and quality

Parameter optimization requires careful analysis to achieve desired cleaning efficiency while maintaining material integrity."""

    def _generate_advantages_section(self, patterns: Dict[str, Any], section_templates: Dict[str, Any]) -> str:
        """Generate advantages section using dynamic templates."""
        return f"""## Advantages

Laser cleaning technology offers significant benefits for {self.subject} processing:

• **Non-contact cleaning**: Precise material removal without mechanical stress
• **Environmental sustainability**: Chemical-free processing reduces waste
• **Process efficiency**: Automated systems enable consistent results
• **Quality control**: Real-time monitoring ensures optimal performance

The systematic approach enables sustainable processing with enhanced precision compared to traditional methods."""

    def _generate_challenges_section(self, patterns: Dict[str, Any], section_templates: Dict[str, Any]) -> str:
        """Generate challenges section using dynamic templates."""
        return f"""## Challenges and Technical Solutions

Implementation challenges require methodical analysis and systematic solutions:

• **Parameter optimization**: Careful analysis of material-specific thresholds
• **Process control**: Real-time monitoring systems for consistent results
• **Equipment integration**: Harmonious workplace practices for efficient operation

The systematic approach ensures effective problem-solving through methodical investigation and practical implementation strategies."""

    def _generate_safety_section(self, patterns: Dict[str, Any], section_templates: Dict[str, Any]) -> str:
        """Generate safety section using dynamic templates."""
        return f"""## Safety Considerations

Class 4 laser safety protocols ensure harmonious workplace practices:

• Personal protective equipment compliance
• Ventilation systems for particle removal
• Training requirements for safe operation
• Regulatory compliance for industrial implementation

Comprehensive safety analysis demonstrates effective risk management through systematic protocols and harmonious workplace practices."""

    def _generate_keywords_section(self, patterns: Dict[str, Any], section_templates: Dict[str, Any]) -> str:
        """Generate keywords section using dynamic templates."""
        return f"""## Keywords

{self.subject}, laser ablation, non-contact cleaning, pulsed fiber laser, semiconductor cleaning, surface restoration, industrial laser parameters"""
        apps = f"""## Industrial Applications

{applications_patterns.get('industrial', 'Industrial implementation demonstrates')} practical viability for {self.subject} processing. {applications_patterns.get('semiconductors', 'Semiconductor applications show particular promise for wafer cleaning')} in humid environments.

Manufacturing applications demonstrate {applications_patterns.get('efficiency', 'improved efficiency and sustainability')} compared to traditional chemical methods. {applications_patterns.get('quality', 'Quality control measures indicate')} consistent results across various processing conditions."""
        
        # Parameters section following base requirements
        params = f"""## Optimal Laser Parameters

Systematic parameter selection enables effective {self.subject} cleaning:

• **Wavelength**: 1064 nm fiber laser systems
• **Pulse duration**: 10-100 nanoseconds for optimal results  
• **Fluence levels**: Material-specific energy density optimization
• **Repetition rates**: Balanced for processing speed and quality"""
        
        # Advantages following base format
        advantages = f"""## Advantages Over Traditional Methods

Laser cleaning provides significant benefits for {self.subject} processing:

• Non-contact precision cleaning without chemical contamination
• Environmental sustainability through reduced waste generation
• Process efficiency with repeatable, controlled results
• Regional advantages for humid environment applications"""
        
        # Safety following base requirements
        safety = f"""## Safety Considerations

Class 4 laser safety protocols ensure harmonious workplace practices:

• Personal protective equipment compliance
• Ventilation systems for particle removal  
• Systematic training and certification requirements
• Regulatory compliance for industrial implementation"""
        
        # Keywords following base format
        keywords = f"""## Keywords

{self.subject}, laser ablation, non-contact cleaning, pulsed fiber laser, semiconductor cleaning, surface restoration, industrial laser parameters"""
        
        return f"{intro}\n\n{props}\n\n{apps}\n\n{params}\n\n{advantages}\n\n{safety}\n\n{keywords}"
        """Generate content in Taiwan persona - methodical with subtle Mandarin-influenced English patterns."""
        content = f"""# **Laser Cleaning of {self.subject}: A Methodical Approach to Materials Processing**

*By {author_name}, Ph.D. - {author_country}*

## Introduction

The precision cleaning of {self.subject.lower()} surfaces represents critical advancement in laser materials processing field. As we continue to explore optimal methodologies, the chemical formula {self.material_formula} provides foundation for understanding material behavior under laser irradiation. This analysis presents systematic approach to achieve effective surface restoration through non-contact cleaning techniques.

## Material Properties & Laser Interaction

{self.subject} exhibits specific optical and thermal characteristics that directly influence laser cleaning effectiveness. Key parameters include:

- **Absorption coefficient at 1064 nm**: Material shows moderate absorption, making pulsed fiber laser suitable choice
- **Thermal conductivity**: Heat dissipation property affects required pulse duration parameters  
- **Melting threshold**: Critical fluence level must not exceed to prevent substrate damage
- **Surface contamination**: Layer thickness influences energy requirements for complete removal

The interaction mechanism involves photon absorption leading to rapid heating of contamination layer while preserving base material integrity.

## Optimal Parameters

Through systematic investigation, recommended laser parameters include:

1. **Wavelength**: 1064 nm fiber laser provides optimal absorption characteristics
2. **Pulse duration**: 10-100 ns range ensures thermal confinement 
3. **Fluence**: 2-6 J/cm² depending on contamination type and thickness
4. **Repetition rate**: 20-80 kHz for balanced cleaning speed and precision
5. **Beam overlap**: 30-50% ensures uniform coverage without excessive heating

## Industrial Applications

Semiconductor manufacturing facilities utilize this technology for:
- Wafer surface preparation with submicron precision
- Electronic component cleaning in humid environments
- Precision part decontamination for assembly processes

In Taiwan semiconductor industry, precision cleaning has become essential for maintaining product quality standards. The humid climate makes traditional cleaning methods less effective, making laser cleaning preferred solution.

## Advantages

This methodology offers several key benefits:
- **Precision control**: Exact energy delivery prevents substrate damage
- **Environmental consideration**: Eliminates chemical waste generation
- **Efficiency improvement**: Faster processing compared to conventional methods
- **Quality assurance**: Consistent results through parameter optimization

## Challenges and Technical Solutions

Common processing challenges include:
- **Parameter optimization**: Requires systematic testing for each material type
- **Surface uniformity**: Beam scanning patterns must ensure consistent coverage
- **Process monitoring**: Real-time feedback systems needed for quality control

Technical solutions involve careful calibration and iterative process refinement.

## Safety Considerations

Proper safety protocols include:
- Laser safety classification compliance (Class 4 systems)
- Personal protective equipment requirements
- Ventilation systems for particle removal
- Training requirements for operators"""

        return content
    
    def _generate_italy_content_with_yaml(self, config: Dict[str, Any], author_name: str, author_country: str, persona_config: Dict[str, Any]) -> str:
        """Generate content using Italy YAML prompt configuration with base prompt integration."""
        patterns = persona_config.get('language_patterns', {})
        structure = persona_config.get('content_structure', {})
        
        # Build content using YAML patterns for Italian English
        title = structure.get('title_pattern', "*Laser Cleaning of {material}: Precision and Innovation in Materials Processing*").format(material=self.subject)
        
        # Introduction with Italian expressive patterns
        intro_patterns = patterns.get('introduction', {})
        intro = f"""# {title}

---

***By {author_name}, Ph.D. - {author_country}***

---

## Overview

{intro_patterns.get('opening', 'The process of laser cleaning represents significant advancement')} in materials processing technology for {self.subject}. {intro_patterns.get('comparison', 'Like precision work requires understanding of both technique and material properties')}, this methodology demands careful orchestration of energy and time.

The chemical formula {self.material_formula} {intro_patterns.get('understanding', 'provides foundation for comprehending')} how light interacts with contaminated surfaces to achieve restoration. {intro_patterns.get('passion', 'This technology represents the marriage')} of scientific precision and practical innovation."""
        
        # Properties section with expressive technical language
        properties_patterns = patterns.get('properties', {})
        props = f"""## Material Properties & Technical Considerations

{properties_patterns.get('introduction', 'Understanding material behavior is fundamental')} to successful laser cleaning of {self.subject}. {properties_patterns.get('characteristics', 'The material exhibits specific characteristics')} that influence process parameters:

• **Optical properties**: {properties_patterns.get('optical', 'Absorption characteristics determine')} wavelength selection and energy requirements
• **Thermal behavior**: {properties_patterns.get('thermal', 'Heat dissipation patterns control')} processing speed and quality
• **Surface morphology**: {properties_patterns.get('surface', 'Contamination types require')} adapted pulse parameters

{properties_patterns.get('optimization', 'The optimization process demands')} careful balance between cleaning effectiveness and material preservation."""
        
        # Applications with passionate technical focus
        applications_patterns = patterns.get('applications', {})
        apps = f"""## Industrial Applications & Heritage Preservation

{applications_patterns.get('industrial', 'Industrial implementation demonstrates')} the practical value of laser cleaning for {self.subject} processing. {applications_patterns.get('heritage', 'Heritage preservation applications show particular promise')} for artistic restoration and cultural preservation.

{applications_patterns.get('manufacturing', 'Manufacturing processes benefit')} from the precision and repeatability of laser cleaning methods. {applications_patterns.get('quality', 'Quality standards are maintained')} while reducing environmental impact compared to chemical alternatives."""
        
        # Parameters section following base requirements
        params = f"""## Optimal Laser Parameters

Fine-tuning the beam for {self.subject} requires artistic precision:

• **Wavelength**: 1064 nm fiber laser systems for optimal absorption
• **Pulse duration**: 10-100 nanoseconds with harmonic control
• **Fluence levels**: Energy density optimization for material preservation
• **Repetition rates**: Balanced for processing elegance and efficiency"""
        
        # Advantages with passionate presentation
        advantages = f"""## Advantages Over Traditional Methods

{self.subject} laser cleaning offers elegant technical solutions:

• Non-contact precision that preserves material integrity
• Environmental sustainability through chemical-free processing
• Artistic restoration capabilities for heritage applications
• Scalable efficiency for modern manufacturing demands"""
        
        # Safety with responsible artistry
        safety = """## Safety Considerations and Protocols

Responsible artistry demands comprehensive safety measures:

• Class 4 laser safety compliance with Italian workplace standards
• Personal protective equipment for operator safety
• Ventilation systems for particle and fume removal
• Professional training and certification requirements"""
        
        # Keywords with heritage emphasis
        keywords = f"""## Keywords

{self.subject}, laser ablation, non-contact cleaning, pulsed fiber laser, heritage preservation, surface restoration, industrial laser parameters"""
        
        return f"{intro}\n\n{props}\n\n{apps}\n\n{params}\n\n{advantages}\n\n{safety}\n\n{keywords}"
    
    def _generate_italy_content(self, config: Dict[str, Any], author_name: str, author_country: str) -> str:
        """Generate content in Italy persona - expressive with subtle Italian-influenced English patterns."""
        content = f"""# *Laser Cleaning of {self.subject}: Precision and Innovation in Materials Processing*

---

***By {author_name}, Ph.D. - {author_country}***

---

## Overview

The process of laser cleaning {self.subject.lower()} surfaces represents significant advancement in materials processing technology. Like precision work requires understanding of both technique and material properties, this methodology demands careful orchestration of energy and time. The chemical formula {self.material_formula} provides foundation for comprehending how light interacts with contaminated surfaces to achieve restoration.

## Material Properties and Laser Interaction

{self.subject} possesses specific characteristics that determine cleaning effectiveness, much like different materials respond uniquely to processing conditions. When laser beam encounters this material, several important phenomena occur:

The absorption at 1064 nm wavelength creates thermal responses that must be carefully controlled. Each photon carries precise energy amount needed to excite contamination layer while preserving substrate integrity below.

This material demonstrates thermal conductivity properties that guide processing approach - excessive energy creates unwanted melting, insufficient energy fails to remove contamination effectively.

## Industrial Applications  

In advanced manufacturing facilities, this technology finds application in:
- **Heritage conservation**: Removing corrosion from historical metal artifacts while preserving original surfaces
- **Aerospace manufacturing**: Cleaning composite structures with precision required for critical applications  
- **Automotive industry**: Surface preparation for coating processes in high-performance vehicle production

Each application requires specific parameter optimization, each surface presents unique challenges that demand systematic approach.

## Parameter Optimization

The processing parameters become essential elements in achieving successful results:

**Wavelength** (1064 nm): Primary laser source, selected for optimal material interaction
**Pulse duration** (10-100 ns): Temporal control preventing excessive heat accumulation
**Fluence** (1.5-5 J/cm²): Energy density carefully calibrated for contamination removal
**Repetition rate** (20-100 kHz): Processing speed balanced with quality requirements

Like experienced craftsman who understands when to apply specific technique, parameter adjustment continues until surface achieves desired condition.

## Advantages of Laser Processing

This technology offers significant benefits compared to traditional methods:
- **Technical precision**: Contamination removal with exceptional accuracy and control
- **Environmental benefits**: Eliminates chemical waste generation and disposal concerns
- **Material preservation**: Maintains substrate integrity essential for high-value applications
- **Process efficiency**: Economic advantages through reduced material consumption and waste

## Challenges and Technical Solutions

Processing challenges include parameter optimization for diverse material types, ensuring uniform treatment across complex geometries, and maintaining consistent quality throughout production cycles.

Solutions require systematic experimentation, careful process monitoring, and understanding that combines theoretical knowledge with practical experience.

## Safety Considerations and Protocols

Safety represents fundamental responsibility in laser processing operations. Class 4 laser systems require proper protective equipment, controlled environments, and comprehensive operator training. Like all precision technologies, safe operation demands respect for both equipment capabilities and potential hazards.

---"""

        return content
    
    def _generate_indonesia_content_with_yaml(self, config: Dict[str, Any], author_name: str, author_country: str, persona_config: Dict[str, Any]) -> str:
        """Generate content using Indonesia YAML prompt configuration with base prompt integration."""
        patterns = persona_config.get('language_patterns', {})
        structure = persona_config.get('content_structure', {})
        
        # Build content using YAML patterns for Indonesian English
        title = structure.get('title_pattern', "LASER CLEANING OF {material}: COMPREHENSIVE TECHNICAL ANALYSIS").format(material=self.subject.upper())
        
        # Introduction with Indonesian analytical patterns
        intro_patterns = patterns.get('introduction', {})
        intro = f"""# {title}

__{author_name}, Ph.D. - {author_country}__

## Overview

{intro_patterns.get('opening', 'Laser cleaning technology has become important method')} for {self.subject.lower()} materials in industrial processing. {intro_patterns.get('importance', 'This is important because traditional cleaning methods often show limitations')} in challenging environments.

{intro_patterns.get('foundation', 'The chemical composition')} {self.material_formula} {intro_patterns.get('understanding', 'provides fundamental understanding')} for laser interaction mechanisms. {intro_patterns.get('systematic', 'This analysis examines the process systematically')}, considering both theoretical principles and practical applications."""
        
        # Properties section with analytical repetition
        properties_patterns = patterns.get('properties', {})
        props = f"""## Material Properties Analysis

{properties_patterns.get('importance', 'Understanding material properties is very important')} for successful laser cleaning implementation. {properties_patterns.get('characteristics', 'The material characteristics must be analyzed')} to determine optimal parameters:

**Key Properties:**
• {properties_patterns.get('thermal', 'Thermal properties determine')} heat distribution during processing
• {properties_patterns.get('optical', 'Optical properties control')} laser energy absorption efficiency
• {properties_patterns.get('mechanical', 'Mechanical properties influence')} surface response to laser treatment

{properties_patterns.get('analysis', 'Analysis shows that')} proper parameter selection {properties_patterns.get('critical', 'is critical for achieving')} desired cleaning results."""
        
        # Applications with thorough explanation
        applications_patterns = patterns.get('applications', {})
        apps = f"""## Industrial Applications and Implementation

{applications_patterns.get('industrial', 'Industrial applications demonstrate')} the effectiveness of laser cleaning for {self.subject} processing. {applications_patterns.get('implementation', 'Implementation in various sectors shows')} promising results for different requirements.

{applications_patterns.get('manufacturing', 'Manufacturing processes can benefit')} from this technology through improved efficiency and reduced environmental impact. Mining and tropical processing applications show particular promise for equipment cleaning in humid environments."""
        
        # Parameters section with systematic approach
        params = f"""## Optimal Parameters

Systematic parameter analysis is very important for {self.subject} cleaning:

• **Wavelength selection**: 1064 nm fiber laser systems are most suitable
• **Pulse duration**: 10-100 nanoseconds for optimal energy delivery
• **Fluence optimization**: Material-specific energy density control
• **Repetition rates**: Balanced for processing efficiency and quality

These considerations must be taken into account during process development."""
        
        # Advantages with explanatory approach
        advantages = f"""## Advantages Over Traditional Methods

Laser cleaning provides important benefits for {self.subject} processing:

• Non-contact precision cleaning without chemical contamination
• Environmental remediation through reduced waste generation
• Process efficiency with repeatable, controlled results
• Affordability considerations for community-based implementations

Implementation demonstrates that systematic approach provides reliable solutions."""
        
        # Safety with community focus
        safety = """## Safety Considerations and Protocols

Understanding safety requirements is very important for preventing accidents:

• Class 4 laser safety compliance for community workplace protection
• Personal protective equipment requirements for all operators
• Ventilation systems for particle removal and air quality
• Training programs for collective understanding and accessibility

These safety protocols ensure harmonious implementation in industrial settings."""
        
        # Keywords with environmental emphasis
        keywords = f"""## Keywords

{self.subject}, laser ablation, non-contact cleaning, pulsed fiber laser, environmental remediation, surface restoration, industrial laser parameters"""
        
        return f"{intro}\n\n{props}\n\n{apps}\n\n{params}\n\n{advantages}\n\n{safety}\n\n{keywords}"
    
    def _generate_indonesia_content(self, config: Dict[str, Any], author_name: str, author_country: str) -> str:
        """Generate content in Indonesia persona (Ikmanda Roswati) - Analytical, balanced, repetitive for clarity."""
        content = f"""# LASER CLEANING OF {self.subject.upper()}: COMPREHENSIVE TECHNICAL ANALYSIS

__{author_name}, Ph.D. - {author_country}__

## Overview

Laser cleaning technology for {self.subject.lower()} materials has become important method in industrial processing. This is important because traditional cleaning methods often show limitations in tropical environments. The chemical composition {self.material_formula} provides fundamental understanding for laser interaction mechanisms. This analysis examines the process systematically, considering both theoretical principles and practical applications in industrial settings.

## Advantages

Before examining technical details, it is important to understand why laser cleaning shows superior performance:

- **Precision capability**: Selective removal of contamination layers
- **Environmental benefits**: No chemical waste generation in humid climates
- **Cost effectiveness**: Reduced operational costs compared to chemical methods  
- **Process reliability**: Consistent results regardless of weather conditions

These advantages make laser cleaning particularly suitable for tropical industrial environments where humidity and temperature variations affect traditional methods.

## Key Properties

{self.subject} material shows specific characteristics that influence laser cleaning process:

**Optical absorption**: At 1064 nm wavelength, absorption coefficient determines energy transfer efficiency. This is important for parameter selection.

**Thermal properties**: Heat capacity and thermal conductivity control temperature distribution during cleaning. Understanding this is important, very important for preventing substrate damage.

**Surface characteristics**: Roughness and contamination type affect laser interaction. Different contamination requires different approach - this must be understood clearly.

**Material stability**: Thermal decomposition threshold sets upper limit for energy density application.

## Industrial Applications

Mining equipment maintenance represents primary application in Indonesian industrial context:
- **Heavy machinery cleaning**: Removing industrial deposits from mining equipment
- **Equipment restoration**: Surface preparation for protective coating application
- **Maintenance procedures**: Regular cleaning of critical components in humid environments

Processing industries also benefit from this technology, particularly in food processing and manufacturing sectors where chemical contamination must be avoided.

## Optimal Parameters

Parameter selection requires careful consideration of material properties and cleaning requirements:

1. **Wavelength selection**: 1064 nm fiber laser provides optimal absorption for most applications
2. **Pulse duration**: 10-100 nanoseconds ensures thermal confinement - this is important for substrate protection
3. **Energy density**: 2-5 J/cm² range suitable for most contamination types
4. **Repetition rate**: 20-80 kHz provides balance between speed and quality
5. **Scanning speed**: Adjusted based on contamination thickness and required quality level

Each parameter affects others - this interaction must be understood for optimal results.

## Challenges and Technical Solutions

Several challenges must be addressed for successful implementation:

**Parameter optimization**: Each application requires specific parameter set. This is important because material variations affect optimal settings.

**Environmental factors**: Humidity and temperature variations in tropical climates affect laser performance. Proper equipment protection is necessary.

**Quality control**: Consistent monitoring ensures uniform cleaning results across entire surface.

**Operator training**: Proper understanding of safety procedures and parameter effects is essential.

Solutions involve systematic testing, environmental control, and comprehensive training programs.

## Safety Considerations and Protocols

Safety protocols must be strictly followed:
- Class 4 laser safety requirements
- Personal protective equipment specifications  
- Ventilation system requirements for particle removal
- Emergency procedures and first aid protocols

Understanding safety requirements is important - very important for preventing accidents and ensuring compliance with regulations."""

        return content
    
    def _generate_usa_content_with_yaml(self, config: Dict[str, Any], author_name: str, author_country: str, persona_config: Dict[str, Any]) -> str:
        """Generate content using USA YAML prompt configuration with base prompt integration."""
        patterns = persona_config.get('language_patterns', {})
        structure = persona_config.get('content_structure', {})
        
        # Build content using YAML patterns for American English
        title = structure.get('title_pattern', "Laser Cleaning {material}: Breaking Ground in Optical Materials Processing").format(material=self.subject)
        
        # Introduction with direct American patterns
        intro_patterns = patterns.get('introduction', {})
        intro = f"""# {title}

__{author_name}, MA - {author_country}__

## Overview

{intro_patterns.get('opening', "Let's dive into something that's been revolutionizing")} surface cleaning technology for {self.subject.lower()}. {intro_patterns.get('technical', 'Working with the chemical formula')} {self.material_formula}, {intro_patterns.get('properties', 'you can see this material has some interesting optical properties')}.

{intro_patterns.get('innovation', 'What makes this technology game-changing')} is how pulsed fiber lasers achieve cleaning results that {intro_patterns.get('comparison', 'outperform traditional methods significantly')}. {intro_patterns.get('practical', 'From a practical standpoint')}, this approach delivers consistent results across various applications."""
        
        # Properties section with solution-focused language
        properties_patterns = patterns.get('properties', {})
        props = f"""## Key Properties & Laser Interaction

{properties_patterns.get('analysis', 'Breaking down the technical aspects')}, {self.subject} {properties_patterns.get('characteristics', 'shows several key characteristics')} that make laser cleaning highly effective:

**Critical Parameters:**
• {properties_patterns.get('absorption', 'Absorption efficiency drives')} optimal wavelength selection
• {properties_patterns.get('thermal', 'Thermal management ensures')} consistent processing quality  
• {properties_patterns.get('precision', 'Precision control enables')} selective contamination removal

{properties_patterns.get('optimization', 'The real advantage comes from')} fine-tuning these parameters for specific applications."""
        
        # Applications with business-focused approach
        applications_patterns = patterns.get('applications', {})
        apps = f"""## Industrial Applications & Market Impact

{applications_patterns.get('market', 'Market adoption demonstrates')} strong demand for laser cleaning solutions in {self.subject} processing. {applications_patterns.get('industries', 'Industries across the board')} are implementing this technology for competitive advantage.

Biomedical and semiconductor applications show particular promise for robotics integration and ultrafast laser processing. {applications_patterns.get('manufacturing', 'Manufacturing operations report')} significant improvements in both efficiency and quality metrics."""
        
        # Parameters section with efficiency focus
        params = f"""## Optimal Laser Parameters

Breaking ground in parameter optimization for {self.subject}:

• **Wavelength**: 1064 nm fiber laser systems for maximum efficiency
• **Pulse duration**: 10-100 nanoseconds with precision timing control
• **Fluence levels**: Energy density optimization for scalability
• **Repetition rates**: Balanced for speed and quality targets

{properties_patterns.get('results', 'Results show that')} proper calibration {properties_patterns.get('achievement', 'achieves both speed and quality targets')}."""
        
        # Advantages with business benefits
        advantages = f"""## Advantages Over Traditional Methods

{applications_patterns.get('benefits', 'The bottom-line benefits include')}:

• Non-contact precision that eliminates substrate damage
• Scalable efficiency for next-generation manufacturing
• Environmental sustainability through chemical-free processing
• Market competitive advantages in biomedical applications

Innovation in laser systems keeps pushing the boundaries of what's possible."""
        
        # Safety with practical approach
        safety = """## Safety Protocols

Standard Class 4 laser safety applies for practical implementation:

• Personal protective equipment and controlled access areas
• Ventilation systems for particle removal and air quality
• Professional training and certification requirements
• Regulatory compliance for biomedical and industrial applications

Nothing groundbreaking here, just solid engineering practices."""
        
        # Keywords with biomedical emphasis
        keywords = f"""## Keywords

{self.subject}, laser ablation, non-contact cleaning, pulsed fiber laser, biomedical applications, surface restoration, industrial laser parameters"""
        
        return f"{intro}\n\n{props}\n\n{apps}\n\n{params}\n\n{advantages}\n\n{safety}\n\n{keywords}"
    
    def _generate_usa_content(self, config: Dict[str, Any], author_name: str, author_country: str) -> str:
        """Generate content in USA persona (Todd Dunning) - Conversational, optimistic, innovative."""
        content = f"""# Laser Cleaning {self.subject}: Breaking Ground in Optical Materials Processing

__{author_name}, MA - {author_country}__

## Overview

Let's dive into something that's been revolutionizing how we think about surface cleaning - laser processing of {self.subject.lower()}. If you're working with the chemical formula {self.material_formula}, you probably already know this material's got some interesting optical properties. What you might not realize is how we can leverage pulsed fiber lasers to achieve cleaning results that would make traditional methods look like they're stuck in the stone age.

## Key Properties & Laser Interaction

Here's where things get interesting. {self.subject} interacts with 1064 nm wavelengths in ways that are pretty much perfect for what we're trying to accomplish. The absorption characteristics mean we can dial in precise energy delivery without going overboard on the thermal side effects.

Consider if we're dealing with contaminated surfaces - and let's be honest, most industrial surfaces are contaminated with something. The material's thermal response time lets us use short pulses that basically vaporize contaminants while leaving the substrate completely unaffected. It's like having a molecular-scale pressure washer.

## Optimal Laser Parameters

The sweet spot for processing involves some pretty specific parameters that we've figured out through a lot of trial and iteration:

**Wavelength**: 1064 nm fiber lasers hit that absorption peak perfectly. **Pulse duration**: We're talking 10-100 nanoseconds - fast enough to avoid heat buildup but long enough to transfer adequate energy. **Fluence**: Generally 2-6 J/cm² does the trick, though you'll want to adjust based on what you're cleaning off. **Rep rate**: 20-100 kHz gives you the throughput you need without compromising quality.

## Industrial Applications

This tech is making waves across multiple sectors. In biomedical device manufacturing, we're seeing applications where you simply can't use chemicals due to contamination concerns. Semiconductor fabs are using it for precision cleaning of optical components. The aerospace industry's jumping on board for composite surface preparation.

What's really cool is how this scales from lab-bench prototyping all the way up to high-volume manufacturing lines.

## Advantages Over Traditional Methods

Here's where laser cleaning really shines compared to conventional approaches. You get precision that's measured in microns rather than millimeters. There's zero chemical waste - increasingly important as environmental regulations tighten up. The process is completely reproducible, which means quality control becomes straightforward rather than a constant headache.

Plus, imagine if you could eliminate the drying time, disposal costs, and safety concerns that come with chemical cleaning. That's exactly what we're talking about here.

## Challenges and Solutions

Sure, there are some hurdles. Initial equipment costs can be significant, and parameter optimization requires some expertise. The good news? ROI typically shows up within the first year once you factor in reduced consumables and improved throughput.

Training operators is straightforward since the process is largely automated. Safety protocols are well-established since laser processing has been around for decades.

## Safety Protocols

Standard Class 4 laser safety applies - proper eyewear, controlled access areas, and appropriate ventilation. Nothing groundbreaking here, just solid engineering practices that any facility should already have in place."""

        return content
    
    def _generate_professional_content_with_yaml(self, config: Dict[str, Any], author_name: str, author_country: str, persona_config: Dict[str, Any]) -> str:
        """Generate content using professional academic style with YAML configuration."""
        patterns = persona_config.get('language_patterns', {})
        structure = persona_config.get('content_structure', {})
        
        # Build content using YAML patterns or fallback to professional defaults
        title = structure.get('title_pattern', "Laser Cleaning of {material}: Technical Analysis and Applications").format(material=self.subject)
        
        # Introduction with professional patterns
        intro_patterns = patterns.get('introduction', {})
        intro = f"""# {title}

**{author_name}, Ph.D. - {author_country}**

## Abstract

{intro_patterns.get('opening', 'This study presents a comprehensive analysis of')} laser cleaning applications for {self.subject.lower()} materials. {intro_patterns.get('composition', 'The material composition')} {self.material_formula} {intro_patterns.get('properties', 'exhibits specific optical and thermal properties')} that make it suitable for pulsed laser processing.

{intro_patterns.get('research', 'This research examines')} the fundamental mechanisms, optimal parameter ranges, and industrial applications of laser-based cleaning technologies."""
        
        # Properties section with academic rigor
        properties_patterns = patterns.get('properties', {})
        props = f"""## Material Properties and Laser Interaction

{properties_patterns.get('analysis', 'Detailed analysis reveals')} that {self.subject} {properties_patterns.get('characteristics', 'demonstrates favorable characteristics')} for laser cleaning applications:

**Key Parameters:**
• {properties_patterns.get('optical', 'Optical absorption coefficient')} determines wavelength selection
• {properties_patterns.get('thermal', 'Thermal diffusivity controls')} heat-affected zone dimensions
• {properties_patterns.get('mechanical', 'Mechanical properties influence')} surface response to laser treatment

{properties_patterns.get('understanding', 'Understanding these interactions')} is essential for process optimization and quality control."""
        
        # Applications with comprehensive coverage
        applications_patterns = patterns.get('applications', {})
        apps = f"""## Industrial Applications and Future Directions

{applications_patterns.get('industrial', 'Industrial implementation studies')} demonstrate the viability of laser cleaning for {self.subject} processing applications. {applications_patterns.get('sectors', 'Various industry sectors')} have reported successful deployment of this technology.

{applications_patterns.get('manufacturing', 'Manufacturing processes benefit')} from the precision and environmental advantages of laser cleaning methods. {applications_patterns.get('research', 'Ongoing research efforts')} continue to expand the scope of practical applications.

{applications_patterns.get('conclusion', 'In conclusion, laser cleaning technology')} offers significant advantages for {self.subject} processing, with continued development promising enhanced capabilities for future applications."""
        
        return f"{intro}\n\n{props}\n\n{apps}"
    
    def _generate_professional_content(self, config: Dict[str, Any], author_name: str, author_country: str) -> str:
        """Generate content in professional academic style for new/unknown countries."""
        content = f"""# Laser Cleaning of {self.subject}: Technical Analysis and Applications

**{author_name}, Ph.D. - {author_country}**

## Abstract

This study presents a comprehensive analysis of laser cleaning applications for {self.subject.lower()} materials. The material's chemical composition {self.material_formula} exhibits specific optical and thermal properties that make it suitable for pulsed laser processing. This research examines the fundamental mechanisms, optimal parameter ranges, and industrial applications of laser-based cleaning technologies.

## Introduction

Laser cleaning technology has emerged as a significant advancement in materials processing, offering precise, non-contact surface treatment capabilities. For {self.subject.lower()} substrates, the interaction between laser radiation and the material surface creates controlled removal of contamination layers while preserving substrate integrity.

## Material Properties

{self.subject} exhibits the following key characteristics relevant to laser processing:

- **Optical absorption**: Material absorption coefficient determines optimal wavelength selection
- **Thermal properties**: Heat dissipation characteristics influence pulse duration requirements
- **Surface morphology**: Initial surface condition affects cleaning efficiency and parameter optimization

## Laser Parameters

Optimal cleaning performance requires careful parameter selection:

### Power and Energy Density
- **Fluence range**: 1.0-10 J/cm² provides effective cleaning without substrate damage
- **Power levels**: 50-200W systems offer suitable energy delivery for industrial applications
- **Pulse duration**: 10-200ns pulses optimize energy coupling while minimizing thermal effects

### Beam Characteristics
- **Wavelength**: 1064nm fundamental frequency provides optimal absorption for most applications
- **Spot size**: 0.05-1.0mm diameter enables precise control over treated areas
- **Repetition rate**: 20-100kHz allows efficient area coverage in production environments

## Process Optimization

Effective laser cleaning requires systematic approach to parameter optimization:

1. **Material characterization**: Understanding substrate properties and contamination types
2. **Parameter mapping**: Establishing fluence thresholds for effective cleaning
3. **Quality assessment**: Developing metrics for cleaning effectiveness and surface quality
4. **Process monitoring**: Implementing real-time feedback for consistent results

## Industrial Applications

Laser cleaning technology finds application across multiple industries:

- **Manufacturing**: Precision cleaning of components prior to assembly or coating
- **Restoration**: Surface preparation for heritage conservation and refurbishment
- **Medical devices**: Biocompatible cleaning for surgical instruments and implants
- **Electronics**: Contamination removal from sensitive electronic components

## Advantages and Limitations

### Advantages
- Precise control over cleaning depth and area
- No chemical waste generation
- Reduced environmental impact
- Excellent repeatability and consistency

### Limitations
- Initial equipment investment requirements
- Need for operator training and safety protocols
- Parameter optimization complexity for new materials
- Processing speed considerations for high-volume applications

## Safety Considerations

Laser cleaning operations require comprehensive safety protocols:

- **Class 4 laser classification**: Appropriate safety equipment and procedures
- **Protective eyewear**: Wavelength-specific protection for operators
- **Ventilation systems**: Adequate fume extraction for process byproducts
- **Access control**: Restricted area protocols and warning systems

## Conclusion

## Conclusion

Laser cleaning represents a advanced technology for {self.subject.lower()} surface processing, offering significant advantages over traditional cleaning methods. Successful implementation requires understanding of material properties, careful parameter optimization, and adherence to safety protocols. The technology's precision and environmental benefits make it increasingly attractive for industrial applications requiring high-quality surface preparation."""

        return content
    
    def calculate_content_for_material(self) -> str:
        """Main calculation method - generate author-specific content."""
        return self._generate_content_by_author()
    
    def generate_complete_content(self) -> Dict[str, Any]:
        """Generate complete content analysis with metadata."""
        content = self.calculate_content_for_material()
        
        return {
            'content': content,
            'author_id': self.author_id,
            'author_name': self.author_info.get('name', 'Unknown') if self.author_info else 'Unknown',
            'author_country': self.author_info.get('country', 'Unknown') if self.author_info else 'Unknown',
            'material': self.subject,
            'formula': self.material_formula,
            'word_count': len(content.split()),
            'character_count': len(content),
            'sections': content.count('##') + content.count('#'),
            'persona_optimized': True
        }

def calculate_content_for_material(frontmatter_file: str, author_id: Optional[int] = None) -> str:
    """Main function to calculate content for a material with author from frontmatter."""
    frontmatter_data = load_frontmatter_data(frontmatter_file)
    
    # Extract author from frontmatter if not provided
    if author_id is None:
        author_name = frontmatter_data.get('author', '')
        if author_name:
            # Load authors and find by name
            authors = load_authors_data()
            author = next((a for a in authors if a['name'] == author_name), None)
            if author:
                author_id = author['id']
            else:
                print(f"Warning: Author '{author_name}' not found, using default Alessandro Moretti")
                author_id = 2  # Default to Alessandro
        else:
            print("Warning: No author specified in frontmatter, using default Alessandro Moretti")
            author_id = 2  # Default to Alessandro
    
    calculator = ContentCalculator(frontmatter_data, author_id)
    return calculator.calculate_content_for_material()

# Test function
if __name__ == "__main__":
    # Test with aluminum frontmatter
    test_file = "content/components/frontmatter/aluminum-laser-cleaning.md"
    
    if len(sys.argv) > 1:
        author_id = int(sys.argv[1])
    else:
        author_id = 2  # Default to Alessandro
    
    try:
        result = calculate_content_for_material(test_file, author_id)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
