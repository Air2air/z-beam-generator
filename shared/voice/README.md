# Voice Management System

Centralized voice management for country-specific linguistic variations in content generation.

## 🔄 Voice Processing Workflow

**Voice enhancement is a POST-PROCESSING step that OVERWRITES text fields in Materials.yaml:**

```
1. Generation → Materials.yaml (raw content, no voice)
2. Voice Enhancement → Materials.yaml (enhances text fields, OVERWRITES in-place)
3. Manual Export → frontmatter/*.yaml (combines Materials.yaml + Categories.yaml)
```

### Complete Workflow

```bash
# Step 1: Generate raw content (no voice) → Saves to Materials.yaml
python3 run.py --micro "Steel"
python3 run.py --subtitle "Steel"
python3 run.py --faq "Steel"

# Step 2: Apply voice enhancement → OVERWRITES text fields in Materials.yaml
python3 scripts/voice/enhance_materials_voice.py --material "Steel"

# Step 3: Manual export → Combines Materials.yaml + Categories.yaml → frontmatter
python3 run.py --data-only
```

### Batch Processing

```bash
# Generate all content → Materials.yaml
python3 run.py --all

# Apply voice to all materials → OVERWRITES fields in Materials.yaml
python3 scripts/voice/enhance_materials_voice.py --all

# Manual export → Combines with Categories.yaml → frontmatter files
python3 run.py --data-only
```

### Key Points

- ✅ **Voice postprocessor OVERWRITES qualifying text fields** (micro, subtitle, FAQ answers)
- ✅ **Valid enhanced output replaces original content** in Materials.yaml
- ✅ **Export is a separate manual step** that combines Materials.yaml with Categories.yaml
- ✅ **Categories.yaml provides metadata only** (NO fallback ranges - Materials.yaml must be 100% complete)

## Quick Start - Post-Processing API

```python
from shared.voice.post_processor import VoicePostProcessor
from shared.api.client_factory import create_api_client

# Initialize
api_client = create_api_client('grok')
voice_processor = VoicePostProcessor(api_client)

# Enhance text with voice
result = voice_processor.enhance(
    text="Original technical content here",
    author={"country": "Taiwan", "name": "Yi-Chun Lin"},
    intensity=3
)

enhanced_text = result['enhanced_text']
score = result['authenticity_score']

# Validate voice markers
validation = voice_processor.get_voice_score(
    text=enhanced_text,
    author={"country": "Taiwan"}
)

print(f"Authenticity: {validation['authenticity_score']}/100")
print(f"Markers: {validation['marker_count']}")
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

### Micro Component

```python
class CaptionComponentGenerator:
    def _build_prompt(self, material_data, author_country):
        voice = VoiceOrchestrator(country=author_country)
        voice_instructions = voice.get_voice_for_component("micro")
        
        return f"""
{voice_instructions}

MATERIAL: {material_data['name']}
TASK: Generate before/after micros...
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

## 🛠️ Voice Enhancement Tools

### enhance_materials_voice.py

Post-processing tool that applies voice to Materials.yaml content.

```bash
# Single material
python3 scripts/voice/enhance_materials_voice.py --material "Steel"

# All materials
python3 scripts/voice/enhance_materials_voice.py --all

# Dry run (preview only)
python3 scripts/voice/enhance_materials_voice.py --material "Steel" --dry-run

# Validate voice markers
python3 scripts/voice/enhance_materials_voice.py --validate-only

# Voice intensity (1=minimal, 5=maximum)
python3 scripts/voice/enhance_materials_voice.py --material "Steel" --voice-intensity 4
```

**What it does:**
1. Reads material entry from `materials/data/Materials.yaml`
2. Applies VoicePostProcessor to qualifying text fields (micro, subtitle, FAQ)
3. Validates voice markers (target: ≥70/100 authenticity)
4. **OVERWRITES original text fields** with voice-enhanced versions in Materials.yaml
5. Adds `voice_enhanced` timestamp to track enhancement

**Processing Details:**
- **Micro**: Enhances both `before` and `after` sections → **OVERWRITES** in Materials.yaml
- **Subtitle**: Enhances subtitle text → **OVERWRITES** in Materials.yaml
- **FAQ**: Enhances all answer texts → **OVERWRITES** in Materials.yaml
- **Validation**: Only saves if authenticity score ≥70/100
- **Atomic Writes**: Uses temporary files for safe overwriting

### Voice Authenticity Scoring

Voice quality is measured on a 0-100 scale:

- **85-100**: Excellent (3-4 markers, well distributed)
- **70-84**: Good (2-3 markers, natural)
- **50-69**: Fair (needs enhancement)
- **0-49**: Poor (requires reprocessing)

## 📋 Content Type Support

The voice system works identically for **all content types**:

- ✅ **Materials** (`materials/data/Materials.yaml`)
- ✅ **Regions** (`regions/data.yaml`)
- ✅ **Applications** (`applications/data.yaml`)
- ✅ **Contaminants** (`contaminants/data.yaml`)
- ✅ **Thesaurus** (`thesaurus/data.yaml`)

**Workflow is identical:**
1. Component generators write raw content to data file
2. Voice enhancement reads, enhances, writes back to data file
3. Frontmatter export reads enhanced data file

## Documentation

- **VOICE_ARCHITECTURE.md**: Complete system architecture
- **profiles/*.yaml**: Individual country voice profiles
- **base/*.yaml**: Shared voice foundations
- **post_processor.py**: Voice enhancement engine
- **enhance_materials_voice.py**: Post-processing CLI tool

## Usage Pattern

**DO NOT** call voice during generation. Voice is post-processing only:

```python
# ❌ WRONG - Don't do this in generators
def generate_micro():
    text = generate_raw_text()
    enhanced = voice_processor.enhance(text)  # NO!
    save_to_yaml(enhanced)

# ✅ CORRECT - Generators write raw content
def generate_micro():
    text = generate_raw_text()
    save_to_yaml(text)  # Save raw, no voice

# ✅ CORRECT - Voice is separate step
def enhance_voice():
    text = load_from_yaml()
    enhanced = voice_processor.enhance(text)
    save_to_yaml(enhanced)
```

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
    component_type="micro"
)

assert result.is_valid, f"Voice issues: {result.issues}"
```

## Migration Guide

See VOICE_ARCHITECTURE.md for complete migration path from embedded voice to centralized system.
