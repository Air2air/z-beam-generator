# Base Content Prompt System

## Overview

The base content prompt system provides shared instructions and requirements across all four persona-specific content generation files. This ensures consistency in technical accuracy, content structure, and scientific standards while allowing each persona to maintain their unique voice and cultural authenticity.

## Architecture

```
components/content/prompts/
├── base_content_prompt.yaml     # Common instructions for all personas
├── taiwan_prompt.yaml          # Taiwan-specific patterns + base
├── italy_prompt.yaml           # Italy-specific patterns + base  
├── indonesia_prompt.yaml       # Indonesia-specific patterns + base
└── usa_prompt.yaml             # USA-specific patterns + base
```

## Base Prompt Contents

### Content Requirements
- **Subject Integration**: How to incorporate material formulas and subjects
- **Core Technical Elements**: Required sections (8 sections defined)
- **Required Sections**: Overview, Material Properties, Industrial Applications, etc.

### Scientific Standards
- **Language Requirements**: Professional tone, technical accuracy
- **Authenticity Guidelines**: Non-native patterns, cultural integration
- **Content Quality**: Expert-level depth, original content

### Formatting Standards
- **Markdown Requirements**: Header hierarchy, emphasis patterns
- **Content Organization**: Section flow, paragraph balance

### Technical Accuracy
- **Laser Specifications**: 1064 nm wavelength, nanosecond pulses
- **Material Science**: Absorption coefficients, thermal properties
- **Industry Applications**: Realistic use cases, efficiency improvements

## How It Works

1. **Load Base**: `load_base_content_prompt()` loads common instructions
2. **Load Persona**: `load_persona_prompt(author_id)` loads persona-specific patterns
3. **Merge**: Base configuration is merged with persona configuration
4. **Generate**: Content generation functions use both base requirements and persona patterns

## Benefits

### Consistency
- All personas follow the same technical accuracy standards
- Consistent section structure across all content
- Standardized safety and parameter information

### Maintainability
- Common requirements in one place
- Easy to update standards for all personas
- Clear separation of base vs persona-specific patterns

### Quality Assurance
- Scientific accuracy enforced at base level
- Professional language standards maintained
- Required technical elements guaranteed

## Usage Example

```python
from components.content.calculator import ContentCalculator

# The system automatically loads and merges base + persona prompts
calc = ContentCalculator(frontmatter_data, author_id=1)
content = calc._generate_content_by_author()

# Content will include:
# - Base requirements (8 required sections)
# - Taiwan persona patterns (linguistic nuances, cultural elements)
# - Scientific accuracy standards
# - Professional formatting
```

## Content Structure Guarantee

Every generated article will include these sections (from base prompt):

1. **Overview** - Introduction with chemical formula integration
2. **Material Properties** - Absorption, thermal, mechanical characteristics  
3. **Industrial Applications** - 2-3 sector-specific examples
4. **Optimal Parameters** - Wavelength, pulse duration, fluence, repetition rates
5. **Advantages** - 3-4 key benefits over traditional methods
6. **Challenges and Technical Solutions** - Problem-solving approach
7. **Safety Considerations** - Class 4 laser safety protocols
8. **Keywords** - Technical terminology + persona-specific terms

## Persona Customization

While base requirements ensure consistency, each persona adds:

- **Linguistic Patterns**: Non-native English nuances specific to their background
- **Cultural Elements**: Subtle motifs woven naturally into content (40-60% of sentences)
- **Signature Phrases**: Characteristic expressions and transitions
- **Regional Focus**: Specialized applications relevant to their expertise
- **Formatting Preferences**: Title styles, emphasis patterns, layout choices

This dual-layer approach ensures both scientific rigor and authentic cultural voice in every generated article.
