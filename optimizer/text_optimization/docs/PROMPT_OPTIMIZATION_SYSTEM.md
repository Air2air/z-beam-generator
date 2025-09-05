# Prompt Optimization System

## Overview

The prompt optimization system enhances Z-Beam's content generation with sophisticated multi-layered prompting, AI detection optimization, and quality enhancement features. This system operates as a separate optimization pipeline that can be applied to any generated content.

## Prompt Architecture

### Three-Layer System

The prompt system consists of three distinct layers that are combined to create comprehensive generation prompts:

1. **Base Layer** - Core content guidance and structure
2. **Persona Layer** - Author-specific writing style and voice
3. **Formatting Layer** - Markdown formatting and presentation rules

### Layer Hierarchy

```
┌─────────────────────────────────────┐
│          FINAL PROMPT               │
├─────────────────────────────────────┤
│  Material Context (Dynamic)         │
│  ├─ Chemical properties             │
│  ├─ Physical properties             │
│  └─ Technical specifications        │
├─────────────────────────────────────┤
│  Primary Guidance (Base Layer)      │
│  ├─ Overall subject questions       │
│  ├─ Author expertise areas          │
│  └─ Technical requirements          │
├─────────────────────────────────────┤
│  Secondary Guidance (Persona)       │
│  ├─ Technical focus areas           │
│  ├─ Language patterns               │
│  └─ Writing style elements          │
├─────────────────────────────────────┤
│  Formatting Rules (Formatting)      │
│  ├─ Markdown preferences            │
│  ├─ Header styles                   │
│  └─ List formatting                 │
├─────────────────────────────────────┤
│  Content Structure & Constraints    │
│  ├─ Required sections               │
│  ├─ Word count limits               │
│  └─ Application focus               │
└─────────────────────────────────────┘
```

## Configuration Files

### 1. Author Personas

**Files:** `optimizer/text_optimization/prompts/personas/{country}_persona.yaml`

#### Purpose
Define author-specific writing styles, language patterns, and cultural elements to ensure authentic voice generation.

#### Example: Taiwan Persona
```yaml
author_id: 1
name: "Yi-Chun Lin"
country: "Taiwan"
language_background: "Mandarin Chinese"

writing_style:
  approach: "systematic_analytical"
  sentence_structure: "short-medium sentences with natural variation"
  organization: "logical step-by-step progression"
  pacing: "methodical with appropriate detail level"

  linguistic_nuances:
    - "slightly simplified structures"
    - "occasional article omissions (material vs the material)"
    - "minor tense shifts (has clean vs cleaned)"
    - "plural inconsistencies"
    - "topic-fronting structures"
    - "literal translations (open the machine vs turn on)"

language_patterns:
  signature_phrases:
    - "as we continue to explore"
    - "what if we consider"
    - "systematic approach enables"
    - "careful analysis shows"
    - "methodical investigation reveals"

technical_focus:
  primary_expertise: "semiconductor processing"
  secondary_expertise: "electronics applications"
  research_approach: "systematic analysis"
  problem_solving: "methodical investigation"
```

#### Country-Specific Characteristics

##### Taiwan (Author ID: 1)
- **Language Influence:** Mandarin Chinese patterns
- **Writing Style:** Systematic, methodical, pedagogical
- **Specialization:** Semiconductor processing, electronics
- **Cultural Elements:** Perseverance, humility, harmony
- **Word Limit:** 380 words

##### Italy (Author ID: 2)
- **Language Influence:** Romance language patterns
- **Writing Style:** Technical elegance, expressive precision
- **Specialization:** Heritage preservation, additive manufacturing
- **Cultural Elements:** Artistic precision, technical innovation
- **Word Limit:** 450 words (highest)

##### Indonesia (Author ID: 3)
- **Language Influence:** Bahasa Indonesia patterns
- **Writing Style:** Direct, practical, analytical
- **Specialization:** Renewable energy, marine applications
- **Cultural Elements:** Sustainability focus, practical innovation
- **Word Limit:** 250 words (most concise)

##### USA (Author ID: 4)
- **Language Influence:** American English patterns
- **Writing Style:** Conversational, innovative, efficient
- **Specialization:** Biomedical, aerospace applications
- **Cultural Elements:** Innovation focus, efficiency emphasis
- **Word Limit:** 320 words

### 2. Formatting Configuration

**Files:** `optimizer/text_optimization/prompts/formatting/{country}_formatting.yaml`

#### Purpose
Define country-specific markdown formatting preferences and presentation styles.

#### Example: Italy Formatting
```yaml
markdown_formatting:
  headers:
    main_title: "# for main title with elegant spacing"
    section_headers: "## for sections with clear hierarchy"
    subsection_headers: "### for technical subsections"

  emphasis:
    critical_info: "**bold** for key technical information"
    formulas: "simple notation without excessive markup"
    parameters: "**bold** for laser parameters and specifications"

  lists:
    primary_style: "numbered lists for systematic procedures"
    secondary_style: "bullet points for feature lists"
    technical_specs: "numbered lists for parameter sequences"

  content_flow:
    paragraph_style: "medium paragraphs with technical elegance"
    transition_style: "smooth technical transitions"
    conclusion_style: "precise technical summary"
```

## Prompt Construction Process

### Step 1: Material Context Injection
The system starts by building material-specific context from frontmatter data:

```yaml
MATERIAL CONTEXT:
- Chemical Formula: Al2(SO4)3·18H2O
- Material Symbol: Alum
- Material Type: Hydrated sulfate
- Density: 1.69 g/cm³
- Thermal Conductivity: 0.5 W/mK
- Melting Point: 86.5°C
- Category: Industrial Chemical
- Tensile Strength: Not applicable
```

### Step 2: Author Information
```yaml
Author: Maria Rossi from Italy
```

### Step 3: Primary Content Guidance
Injects the core questions from `overall_subject`:
```yaml
PRIMARY CONTENT GUIDANCE:
- What is special about the material?
- How does it differ from others in the category?
- What is it often used for?
- What is it like to laser clean?
- What special challenges or advantages does it present for laser cleaning?
- What should the results look like?
```

### Step 4: Author-Specific Technical Focus
From persona configuration:
```yaml
SECONDARY - PERSONA TECHNICAL FOCUS:
- Primary Expertise: Heritage preservation
- Secondary Expertise: Additive manufacturing
- Research Approach: Technical innovation
- Problem Solving: Precision analysis
```

### Step 5: Technical Requirements
From base configuration:
```yaml
SECONDARY - TECHNICAL REQUIREMENTS:
- Primary wavelength: 1064 nm (standard for most materials)
- Pulse duration: Nanosecond range (10-100 ns)
- Safety classification: Class 4 laser systems
- Technology: Fiber laser preferred

REQUIRED CONTENT:
- Include material density and absorption characteristics
- Specify optimal parameters for Al2(SO4)3·18H2O
- Detail safety protocols for hydrated sulfate processing
```

### Step 6: Language Style Guidance
From persona language patterns:
```yaml
SECONDARY - LANGUAGE STYLE:
- "precision meets innovation"
- "technical elegance"
- "meticulous approach"
```

### Step 7: Writing Style Elements
From persona writing style:
```yaml
SECONDARY - WRITING STYLE:
- Approach: Technical elegance
- Sentence Structure: Medium complexity with technical precision
- Organization: Logical flow with artistic elements
- Pacing: Detailed analysis with expressive elements
```

### Step 8: Formatting Requirements
From formatting configuration:
```yaml
SECONDARY - FORMATTING REQUIREMENTS:
- Headers: # for main title, ## for sections
- Bold: **bold** for key technical information
- Formulas: simple notation without excessive markup
- Lists: numbered lists for systematic procedures
```

### Step 9: Content Structure
```yaml
CONTENT STRUCTURE:
- Overview with chemical formula integration
- Material properties affecting laser interaction
- Industrial applications (2-3 examples)
- Optimal laser parameters
- Advantages over traditional methods
- Safety considerations
```

### Step 10: Critical Constraints
```yaml
CRITICAL WORD COUNT CONSTRAINT:
- Maximum words: 450 words STRICT LIMIT
- Target range: 360-450 words
- Content MUST be concise and focused
- Prioritize essential information only
```

### Step 11: Application Focus
From country-specific applications:
```yaml
APPLICATION FOCUS: heritage preservation, aerospace, automotive applications
```

### Step 12: Final Instructions
```yaml
Generate comprehensive, expert-level technical content.
Maintain professional scientific tone throughout.
Ensure logical flow and accurate technical terminology.
```

## AI Detection Optimization Features

### Dynamic Word Count Management
The system dynamically adjusts prompts based on author word limits:
- **High Limit (Italy, 450 words):** More detailed technical analysis
- **Medium Limit (Taiwan/USA, 320-380 words):** Balanced coverage
- **Low Limit (Indonesia, 250 words):** Highly focused, essential information only

### Randomization Guidelines
To prevent repetitive content:
```yaml
randomization_guidelines:
  section_order: "Randomize section sequence completely - only keep Overview first"
  sentence_order: "Within each section, randomize sentence order for maximum variation"
  paragraph_breaks: "Vary paragraph structure and breaks unpredictably"
  example_selection: "Randomize which industrial examples to emphasize"
  parameter_presentation: "Vary the order of technical parameters and specifications"
```

### Context-Aware Prompting
- **Material Properties:** Automatically includes relevant chemical/physical properties
- **Application Matching:** Aligns examples with author expertise
- **Cultural Adaptation:** Incorporates country-specific application focuses

### Enhancement Flags
```yaml
enhancement_flags:
  conversational_boost: true        # Add conversational elements
  human_elements_emphasis: true     # Emphasize natural language patterns
  nationality_emphasis: true        # Strengthen cultural characteristics
  sentence_variability: true        # Vary sentence structure
  ai_detection_focus: true          # Optimize for human-like content
```

## Prompt Quality Assurance

### Validation Checks
1. **Required Sections Present:** Ensures all configuration sections exist
2. **YAML Syntax Valid:** Validates proper YAML formatting
3. **Author Mapping:** Confirms author IDs map to configurations
4. **Word Count Consistency:** Validates word limits across files

### Error Handling
- **Missing Configurations:** Fail-fast with specific error messages
- **Invalid YAML:** Detailed syntax error reporting
- **Missing Authors:** Clear author not found errors
- **Prompt Building Errors:** Specific configuration error details

### Prompt Length Management
- **Total Length:** Approximately 1,500-2,500 characters per prompt
- **Layer Balance:** Proper proportion between base, persona, and formatting guidance
- **Context Efficiency:** Avoid redundant information across layers

## Advanced Prompt Features

### Material-Specific Adaptations
The system adapts prompts based on material properties:
- **Chemical Category:** Adjusts technical focus for metals, polymers, ceramics
- **Application Domain:** Emphasizes relevant industrial applications
- **Safety Considerations:** Highlights material-specific safety requirements

### Dynamic Property Integration
Automatically includes relevant properties in prompts:
```python
# Chemical properties
if 'formula' in chemical_props:
    prompt_parts.append(f"- Chemical Formula: {chemical_props['formula']}")
if 'materialType' in chemical_props:
    prompt_parts.append(f"- Material Type: {chemical_props['materialType']}")

# Physical properties
if 'density' in properties:
    prompt_parts.append(f"- Density: {properties['density']}")
if 'meltingPoint' in properties:
    prompt_parts.append(f"- Melting Point: {properties['meltingPoint']}")
```

### Prompt Caching Strategy
- **LRU Cache:** Configuration files cached using `@lru_cache(maxsize=None)`
- **Lazy Loading:** Persona/formatting files loaded only when needed
- **Memory Efficiency:** Shared cache across multiple generations

## Troubleshooting Prompts

### Common Configuration Issues

#### Missing overall_subject
```yaml
# Error: Missing 'overall_subject' in base_content_prompt.yaml
# Fix: Add the required section
overall_subject:
  - "What is special about the material?"
  # ... additional questions
```

#### Invalid Author Mapping
```yaml
# Error: No country mapping found for 'United Kingdom'
# Fix: Add country mapping or use existing countries
country_mapping = {
    "taiwan": "taiwan",
    "italy": "italy",
    "indonesia": "indonesia",
    "usa": "usa"
}
```

#### Missing Persona Sections
```yaml
# Error: Missing 'language_patterns' in persona configuration
# Fix: Add required sections to persona files
language_patterns:
  signature_phrases:
    - "example phrase 1"
    - "example phrase 2"
```

### Debug Prompt Generation
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed prompt logging
generator = DynamicPromptGenerator()
result = generator.generate_optimized_prompt(material_name, author_id)

# Check logs for full prompt text
```

This prompt optimization system ensures consistent, high-quality content generation while maintaining author authenticity and technical accuracy across all supported materials and authors.</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/optimizer/text_optimization/docs/PROMPT_OPTIMIZATION_SYSTEM.md
