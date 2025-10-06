# Voice Management System

Centralized voice management for country-specific linguistic variations in content generation.

## Quick Start

```python
from voice.orchestrator import VoiceOrchestrator

# Initialize with author country
voice = VoiceOrchestrator(country="Taiwan")

# Get voice instructions for any component
voice_prompt = voice.get_voice_for_component(
    component_type="caption",
    context={"material": "Aluminum"}
)

# Use in your prompt
full_prompt = f"{voice_prompt}\n\nYour component-specific instructions..."
```

## Supported Countries

| Country | Author | Word Limit | Linguistic Style |
|---------|--------|------------|------------------|
| Taiwan | Yi-Chun Lin | 380 | Academic precision, systematic analysis |
| Italy | Alessandro Moretti | 450 | Sophisticated descriptive, technical elegance |
| Indonesia | Ikmanda Roswati | 250 | Practical accessible, environmental focus |
| United States | Todd Dunning | 320 | Conversational expertise, innovation focus |

## Architecture

```
voice/
├── orchestrator.py          # Main API - VoiceOrchestrator class
├── loader.py               # Profile loading and caching
├── validator.py            # Voice consistency validation
├── profiles/               # Country-specific voice profiles
│   ├── taiwan.yaml
│   ├── italy.yaml
│   ├── indonesia.yaml
│   └── united_states.yaml
└── base/                   # Shared voice foundations
    ├── technical_authority.yaml
    └── analytical_precision.yaml
```

## Component Integration Examples

### Caption Component

```python
class CaptionComponentGenerator:
    def _build_prompt(self, material_data, author_country):
        voice = VoiceOrchestrator(country=author_country)
        voice_instructions = voice.get_voice_for_component("caption")
        
        return f"""
{voice_instructions}

MATERIAL: {material_data['name']}
TASK: Generate before/after captions...
"""
```

### Text Component

```python
class TextComponentGenerator:
    def _build_prompt(self, material_data, author_info):
        voice = VoiceOrchestrator(country=author_info["country"])
        voice_instructions = voice.get_voice_for_component(
            "text",
            context={"word_limit": voice.get_word_limit()}
        )
        
        return f"{voice_instructions}\n\nCONTENT REQUIREMENTS..."
```

## Voice Profile Structure

Each country profile includes:

- **Linguistic Characteristics**: Grammar patterns, sentence structure
- **Vocabulary Patterns**: Preferred terms, formality level
- **Cultural Communication**: Tone, emphasis style, authority markers
- **Voice Adaptation**: Component-specific guidelines
- **Signature Phrases**: Country-specific expressions
- **Quality Thresholds**: Formality, accuracy, authenticity minimums

## Key Features

✅ **Country-Specific Variations**: Authentic non-native English patterns
✅ **Component Adaptation**: Voice adjusts for caption/text/tags
✅ **Fail-Fast**: Invalid countries or missing profiles fail immediately
✅ **Centralized**: Update voice once, propagates everywhere
✅ **Validated**: Voice consistency checking built-in

## Linguistic Authenticity

Voice profiles include **natural variations** of non-native speakers:

- **Taiwan**: Formal register, systematic logic, comprehensive analysis
- **Italy**: Descriptive richness, aesthetic appreciation, flowing prose
- **Indonesia**: Simplified structures, practical focus, repetition for emphasis
- **USA**: Native English baseline, conversational business tone

These are **authentic patterns**, not errors to be corrected.

## Benefits

1. **Single Source of Truth**: One place to update voice
2. **Consistency**: All components share voice logic
3. **Maintainability**: Easy to add new countries
4. **Testability**: Voice validation separate from generation
5. **Scalability**: New components automatically get voice
6. **Cultural Respect**: Authentic communication differences

## Documentation

- **VOICE_ARCHITECTURE.md**: Complete system architecture
- **profiles/*.yaml**: Individual country voice profiles
- **base/*.yaml**: Shared voice foundations

## Usage in Components

1. Import VoiceOrchestrator
2. Initialize with author country
3. Get voice instructions for component type
4. Inject into prompt before content-specific instructions
5. Generate content with voice-aware AI
6. (Optional) Validate voice consistency

## Word Limits by Country

- Taiwan: 380 words
- Italy: 450 words
- Indonesia: 250 words
- United States: 320 words

Access via: `orchestrator.get_word_limit()`

## Testing

```python
from voice.validator import VoiceValidator

validator = VoiceValidator()
result = validator.validate_content(
    content=generated_text,
    country="Taiwan",
    component_type="caption"
)

assert result.is_valid, f"Voice issues: {result.issues}"
```

## Migration Guide

See VOICE_ARCHITECTURE.md for complete migration path from embedded voice to centralized system.
