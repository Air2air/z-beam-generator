# Voice Management Architecture

## Overview

Centralized voice management system for consistent, country-specific linguistic variations across all text-based content generation components. This architecture separates voice logic from component implementations, enabling maintainable, reusable voice orchestration.

## Design Principles

1. **Separation of Concerns**: Voice logic isolated from content generation logic
2. **Country-Based Variations**: Linguistic patterns specific to non-native English speakers
3. **Reusability**: Single voice definition propagates to all text components
4. **Fail-Fast**: Invalid country codes or missing voice data fail immediately
5. **Maintainability**: Update voice in one place, affects all components

## Directory Structure

```
voice/
├── VOICE_ARCHITECTURE.md           # This file - system architecture
├── README.md                        # Quick start guide for developers
├── orchestrator.py                  # VoiceOrchestrator class - main API
├── loader.py                        # Voice profile loading and validation
├── validator.py                     # Voice consistency validation
│
├── profiles/                        # Country-specific voice profiles
│   ├── taiwan.yaml                  # Taiwan - Yi-Chun Lin
│   ├── italy.yaml                   # Italy - Alessandro Moretti
│   ├── indonesia.yaml               # Indonesia - Ikmanda Roswati
│   └── united_states.yaml           # United States - Todd Dunning
│
├── base/                            # Base voice characteristics (shared)
│   ├── technical_authority.yaml    # Authoritative technical voice
│   ├── analytical_precision.yaml   # Analytical observation voice
│   └── voice_base.yaml             # Common voice foundations
│
└── tests/                           # Voice system tests
    ├── test_orchestrator.py
    ├── test_profiles.py
    └── test_validation.py
```

## Core Components

### 1. VoiceOrchestrator (`orchestrator.py`)

**Primary API for all components**

```python
from voice.orchestrator import VoiceOrchestrator

# Initialize with author country
orchestrator = VoiceOrchestrator(country="Taiwan")

# Get voice instructions for component
voice_instructions = orchestrator.get_voice_for_component(
    component_type="caption",
    context={"material": "Aluminum", "technical_level": "advanced"}
)

# Returns complete voice prompt with:
# - Base voice characteristics
# - Country-specific linguistic patterns
# - Component-specific adaptations
```

### 2. Voice Profiles (`profiles/*.yaml`)

**Country-specific linguistic characteristics**

Each profile contains:
- **Linguistic Patterns**: Grammar, sentence structure, vocabulary choices
- **Cultural Markers**: Communication style, emphasis patterns
- **Technical Voice**: How technical content is presented
- **Common Variations**: Typical non-native patterns (natural, not errors)
- **Signature Phrases**: Country-specific expressions

### 3. Base Voice (`base/*.yaml`)

**Shared voice foundations**

- Technical authority guidelines
- Analytical observation standards
- Professional tone requirements
- Universal writing principles

## Voice Profile Structure

### Taiwan Profile Example

```yaml
name: "Taiwan Technical Voice"
author: "Yi-Chun Lin, Ph.D."
country: "Taiwan"
native_language: "Mandarin Chinese"
linguistic_characteristics:
  
  sentence_structure:
    patterns:
      - "Systematic approach enables precise control"
      - "Methodical analysis reveals underlying mechanisms"
      - "Comprehensive investigation demonstrates effectiveness"
    tendencies:
      - Prefer logical connectors (therefore, thus, consequently)
      - Use passive voice for formal technical descriptions
      - Employ structured enumeration (first, second, finally)
    natural_variations:
      - Occasional article omission ("Process enables precise control")
      - Formal register in casual contexts
      - "This research/study shows" vs "Our findings show"
  
  vocabulary_patterns:
    preferred_terms:
      technical: ["systematic", "comprehensive", "methodical", "precise"]
      connectors: ["furthermore", "moreover", "in addition", "consequently"]
      qualifiers: ["significant", "substantial", "considerable", "notable"]
    formality_level: "academic-formal"
    technical_density: "high"
  
  grammar_characteristics:
    natural_patterns:
      - Relative clause preference over compound sentences
      - Present perfect for recent findings
      - Modal verbs for possibility (may, might, could)
    subtle_markers:
      - "The method enables to achieve" (infinitive construction)
      - Adjective stacking ("comprehensive systematic analysis")
      - Explicit result statements ("Results indicate that...")

  cultural_communication:
    tone: "measured and systematic"
    emphasis_style: "data-driven evidence"
    perspective: "objective third-person preferred"
    authority_markers:
      - Citations to established research
      - Quantitative evidence emphasis
      - Methodological rigor demonstration

voice_adaptation:
  caption_generation:
    focus: "Observable technical findings"
    style: "Formal analytical reporting"
    word_limit: 380
  
  text_generation:
    focus: "Systematic process explanation"
    style: "Academic precision with practical applications"
    word_limit: 380
  
  technical_description:
    focus: "Detailed parameter specifications"
    style: "Engineering documentation standards"

signature_phrases:
  - "systematic approach enables"
  - "methodical investigation reveals"
  - "comprehensive analysis demonstrates"
  - "careful examination shows"
  - "precise control achieves"

quality_thresholds:
  formality_minimum: 75
  technical_accuracy_minimum: 90
  linguistic_authenticity_minimum: 70
```

### Italy Profile Example

```yaml
name: "Italian Technical Voice"
author: "Alessandro Moretti, Ph.D."
country: "Italy"
native_language: "Italian"
linguistic_characteristics:
  
  sentence_structure:
    patterns:
      - "The precision of this technique, combined with..., creates exceptional results"
      - "What makes this process remarkable is the elegant balance between..."
      - "One can observe how the laser interaction produces..."
    tendencies:
      - Longer flowing sentences with embedded clauses
      - Descriptive technical language with aesthetic appreciation
      - Personal observations ("we can see", "one notices")
    natural_variations:
      - Adjective-rich descriptions ("beautiful crystalline structure")
      - Expressive technical commentary
      - Rhetorical questions for engagement
  
  vocabulary_patterns:
    preferred_terms:
      technical: ["precision", "elegance", "sophistication", "excellence"]
      descriptive: ["remarkable", "extraordinary", "exceptional", "magnificent"]
      connectors: ["indeed", "naturally", "evidently", "certainly"]
      qualifiers: ["particularly", "especially", "notably", "remarkably"]
    formality_level: "sophisticated-professional"
    technical_density: "medium-high"
  
  grammar_characteristics:
    natural_patterns:
      - Complex sentence structures with subordinate clauses
      - Descriptive present tense for processes
      - Conditional mood for hypotheticals
    subtle_markers:
      - "This allows to achieve" (infinitive without pronoun)
      - Word order emphasis ("Remarkable is the precision...")
      - Double negatives for emphasis ("not without significance")

  cultural_communication:
    tone: "passionate expertise with refinement"
    emphasis_style: "technical elegance and craftsmanship"
    perspective: "engaged expert commentary"
    authority_markers:
      - Engineering heritage references
      - Craftsmanship and precision emphasis
      - Aesthetic appreciation of technical excellence

voice_adaptation:
  caption_generation:
    focus: "Technical precision with aesthetic appreciation"
    style: "Sophisticated descriptive analysis"
    word_limit: 450
  
  text_generation:
    focus: "Engineering excellence and innovation"
    style: "Refined technical discourse"
    word_limit: 450

signature_phrases:
  - "precision meets innovation"
  - "technical elegance"
  - "remarkable achievement in"
  - "sophisticated approach to"
  - "engineering excellence demands"

quality_thresholds:
  formality_minimum: 70
  technical_accuracy_minimum: 85
  linguistic_authenticity_minimum: 75
```

### Indonesia Profile Example

```yaml
name: "Indonesian Technical Voice"
author: "Ikmanda Roswati, Ph.D."
country: "Indonesia"
native_language: "Bahasa Indonesia"
linguistic_characteristics:
  
  sentence_structure:
    patterns:
      - "This method works well, really well for marine applications"
      - "The process is effective for cleaning, especially in tropical conditions"
      - "Practical solutions make this technique suitable for renewable energy"
    tendencies:
      - Direct, straightforward sentence construction
      - Repetition for emphasis ("very effective, extremely effective")
      - Context-specific applications mentioned
    natural_variations:
      - Simplified subordination structures
      - Present tense predominance
      - Demonstrative pronoun use ("This process", "These results")
  
  vocabulary_patterns:
    preferred_terms:
      technical: ["practical", "effective", "efficient", "suitable"]
      application: ["renewable", "sustainable", "environmental", "marine"]
      connectors: ["so", "because", "for this reason", "as a result"]
      qualifiers: ["very", "really", "especially", "particularly"]
    formality_level: "accessible-professional"
    technical_density: "medium"
  
  grammar_characteristics:
    natural_patterns:
      - Active voice preference
      - Simple past and present tense focus
      - Reduced use of perfect tenses
    subtle_markers:
      - Prepositional phrase placement variations
      - Article usage flexibility
      - "For achieve optimal results" (simplified infinitive)

  cultural_communication:
    tone: "community-focused practicality"
    emphasis_style: "environmental and social impact"
    perspective: "collaborative problem-solving"
    authority_markers:
      - Practical field experience
      - Regional application expertise
      - Sustainable technology focus

voice_adaptation:
  caption_generation:
    focus: "Practical applications and sustainability"
    style: "Clear accessible technical explanation"
    word_limit: 250
  
  text_generation:
    focus: "Environmental benefits and practical use"
    style: "Direct communication with context awareness"
    word_limit: 250

signature_phrases:
  - "practical applications for"
  - "works well in tropical conditions"
  - "efficient solutions for"
  - "sustainable approach to"
  - "renewable energy applications"

quality_thresholds:
  formality_minimum: 60
  technical_accuracy_minimum: 80
  linguistic_authenticity_minimum: 70
```

### United States Profile Example

```yaml
name: "American Technical Voice"
author: "Todd Dunning, MA"
country: "United States"
native_language: "English"
linguistic_characteristics:
  
  sentence_structure:
    patterns:
      - "This innovative approach delivers exceptional results in biomedical applications"
      - "Advanced laser systems optimize efficiency while reducing costs"
      - "Cutting-edge technology enables breakthrough performance"
    tendencies:
      - Concise, action-oriented sentences
      - Active voice with clear subjects
      - Direct cause-effect statements
    natural_variations:
      - Minimal (native speaker baseline)
      - Conversational business tone in technical contexts
      - Result-focused framing

  vocabulary_patterns:
    preferred_terms:
      technical: ["innovative", "advanced", "cutting-edge", "breakthrough"]
      business: ["optimize", "efficiency", "cost-effective", "performance"]
      connectors: ["while", "as", "when", "by"]
      qualifiers: ["significant", "substantial", "key", "critical"]
    formality_level: "professional-conversational"
    technical_density: "medium"
  
  grammar_characteristics:
    natural_patterns:
      - Standard American English grammar
      - Varied sentence structures
      - Idiomatic expressions common
    subtle_markers:
      - None (native speaker baseline)

  cultural_communication:
    tone: "confident and optimistic"
    emphasis_style: "innovation and results"
    perspective: "pragmatic problem-solving"
    authority_markers:
      - Silicon Valley innovation culture
      - Emerging technology expertise
      - Business outcome focus

voice_adaptation:
  caption_generation:
    focus: "Innovation and practical results"
    style: "Clear professional communication"
    word_limit: 320
  
  text_generation:
    focus: "Technology advancement and efficiency"
    style: "Conversational expertise"
    word_limit: 320

signature_phrases:
  - "innovative solutions for"
  - "advanced technology enables"
  - "cutting-edge applications in"
  - "optimized performance through"
  - "efficient processing of"

quality_thresholds:
  formality_minimum: 65
  technical_accuracy_minimum: 85
  linguistic_authenticity_minimum: 80
```

## Integration Points

### Caption Component Integration

```python
from voice.orchestrator import VoiceOrchestrator

class CaptionComponentGenerator:
    def _build_prompt(self, material_data, author_country):
        # Initialize voice orchestrator
        voice = VoiceOrchestrator(country=author_country)
        
        # Get voice instructions for captions
        voice_instructions = voice.get_voice_for_component(
            component_type="caption",
            context={
                "material": material_data.get("name"),
                "technical_level": "advanced",
                "format": "before_after_observations"
            }
        )
        
        # Build prompt with voice instructions
        prompt = f"""
{voice_instructions}

MATERIAL CONTEXT:
{material_data}

TASK:
Generate before/after captions for laser cleaning observations...
"""
        return prompt
```

### Text Component Integration

```python
from voice.orchestrator import VoiceOrchestrator

class TextComponentGenerator:
    def _build_prompt(self, material_data, author_info):
        voice = VoiceOrchestrator(country=author_info["country"])
        
        voice_instructions = voice.get_voice_for_component(
            component_type="text",
            context={
                "material": material_data.get("name"),
                "author_expertise": author_info.get("expertise"),
                "word_limit": voice.get_word_limit()
            }
        )
        
        # Combine with base content prompt
        prompt = f"""
{voice_instructions}

CONTENT REQUIREMENTS:
...
"""
        return prompt
```

### Tags Component Integration

```python
from voice.orchestrator import VoiceOrchestrator

class TagsComponentGenerator:
    def _build_prompt(self, material_data, author_country):
        voice = VoiceOrchestrator(country=author_country)
        
        voice_instructions = voice.get_voice_for_component(
            component_type="tags",
            context={
                "material": material_data.get("name"),
                "format": "keyword_extraction"
            }
        )
        
        # Even tag generation can benefit from voice consistency
        prompt = f"""
{voice_instructions}

Generate tags with linguistic patterns consistent with {author_country} technical communication...
"""
        return prompt
```

## Usage Workflow

1. **Component requests voice**: Pass author country to VoiceOrchestrator
2. **Orchestrator loads profile**: Retrieves country-specific voice profile
3. **Voice construction**: Combines base voice + country patterns + component adaptations
4. **Prompt injection**: Voice instructions injected into component prompt
5. **Content generation**: AI generates content following voice guidelines
6. **Validation**: Voice validator checks linguistic consistency

## Voice Consistency Validation

```python
from voice.validator import VoiceValidator

validator = VoiceValidator()

# Validate generated content against voice profile
result = validator.validate_content(
    content=generated_text,
    country="Taiwan",
    component_type="caption"
)

if not result.is_valid:
    print(f"Voice inconsistencies: {result.issues}")
    # Regenerate or apply corrections
```

## Migration Path

### Phase 1: Extract Current Voice Logic
- Identify voice instructions in existing components
- Map to country-specific patterns
- Document current voice characteristics

### Phase 2: Create Voice Profiles
- ✅ Build Taiwan profile (Yi-Chun Lin patterns)
- ✅ Build Italy profile (Alessandro Moretti patterns)
- ✅ Build Indonesia profile (Ikmanda Roswati patterns)
- ✅ Build USA profile (Todd Dunning patterns)

### Phase 3: Implement Orchestrator
- Build VoiceOrchestrator class
- Implement profile loading system
- Create component adapters

### Phase 4: Update Components
- Integrate caption component
- Integrate text component
- Integrate tags component
- Test all voice variations

### Phase 5: Validation & Testing
- Implement voice validation
- Create test suite for all countries
- Verify linguistic authenticity

## Benefits

1. **Single Source of Truth**: Update voice in one place
2. **Consistency**: All components use same voice logic
3. **Maintainability**: Easy to add new countries/authors
4. **Testability**: Voice validation separate from content generation
5. **Scalability**: Add new components without duplicating voice logic
6. **Linguistic Authenticity**: Proper non-native patterns, not errors
7. **Cultural Sensitivity**: Respect communication differences

## Important Notes

### Non-Native Patterns Are NOT Errors

The voice profiles include **natural linguistic variations** common to non-native English speakers. These are **authentic communication patterns**, not mistakes to be corrected:

- **Taiwan**: Formal academic register, systematic logic structures
- **Italy**: Descriptive richness, aesthetic technical language
- **Indonesia**: Simplified structures, practical emphasis, repetition
- **USA**: Baseline native English patterns

### Voice Propagation Strategy

All text-based components receive voice instructions:
- **Caption**: Technical observation voice
- **Text**: Content generation voice
- **Tags**: Keyword selection voice (subtle)
- **Frontmatter** (description): Summary voice
- **Future components**: Automatic voice consistency

### Fail-Fast Architecture

- Missing country profile → immediate error
- Invalid voice configuration → fail on load
- Validation failures → log and alert (don't block)
- No fallbacks to generic voice

## Future Enhancements

1. **Dynamic Voice Adjustment**: Context-aware voice modulation
2. **Voice Learning**: Analyze successful content to refine profiles
3. **Multi-Author Profiles**: Support multiple authors per country
4. **Voice Metrics**: Track voice consistency scores over time
5. **A/B Testing**: Compare voice variations for effectiveness
