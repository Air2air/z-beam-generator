# Localization Prompt Chain System

## Overview

The Localization Prompt Chain System is a **MANDATORY** component that ensures all text generation in the Z-Beam system includes culturally and linguistically authentic localization based on the author's country.

**NEW ARCHITECTURE**: The system now works as part of a two-stage prompt chain:
```
AI Detection Prompts → Localization Prompts → Base Content Prompts
```

## ✅ CRITICAL REQUIREMENT

**Every text generation request MUST include localized persona and formatting prompts.**

This is not optional - it's an essential requirement for maintaining content authenticity and quality.

**IMPORTANT**: Localization prompts are **NEVER modified** by AI detection optimization. They preserve cultural authenticity while AI detection prompts handle human-like writing optimization.

## System Components

### 1. Localization Prompt Chain (`components/text/localization/prompt_chain.py`)

The core system that loads and combines persona and formatting prompts for each country.

**Key Features:**
- Loads persona characteristics from `optimizer/text_optimization/prompts/personas/`
- Loads formatting constraints from `optimizer/text_optimization/prompts/formatting/`
- Combines them into a complete localization prompt chain
- Validates that localization files exist for the requested country
- Provides error handling for missing localization support

### 2. Integration Points

The localization system is integrated at multiple levels:

#### Text Generator (`components/text/generator.py`)
- **Validation**: Validates localization support before generation starts
- **Error Handling**: Fails fast if localization files don't exist

#### Fail-Fast Generator (`components/text/generators/fail_fast_generator.py`)  
- **Prompt Construction**: Includes localization chain as the FIRST section of every prompt
- **Mandatory Loading**: Generation fails if localization prompts cannot be loaded

## Supported Countries

Currently supported countries with full localization:

| Country | Persona File | Formatting File | Author |
|---------|-------------|-----------------|---------|
| Italy | `italy_persona.yaml` | `italy_formatting.yaml` | Alessandro Moretti |
| Indonesia | `indonesia_persona.yaml` | `indonesia_formatting.yaml` | Ikmanda Roswati |
| Taiwan | `taiwan_persona.yaml` | `taiwan_formatting.yaml` | Yi-Chun Lin |
| USA | `usa_persona.yaml` | `usa_formatting.yaml` | Todd Dunning |

## How It Works

### 1. Author Resolution
When generating content, the system:
1. Reads the material's `author_id` from `data/Materials.yaml`
2. Resolves the author information from frontmatter `author_object` field
3. Extracts the author's country

### 2. Localization Chain Construction
The system then:
1. Maps the country to normalized form (e.g., "United States (California)" → "usa")
2. Loads the persona file for that country
3. Loads the formatting file for that country
4. Combines them into a complete localization prompt

### 3. Prompt Integration
The localization prompt is:
1. **Added SECOND** in the new prompt chain architecture (after AI detection prompts)
2. Includes mandatory instructions that must be followed
3. Contains cultural characteristics, language patterns, and formatting requirements
4. **Never modified by AI detection optimization** - preserves cultural authenticity

**New Prompt Chain Order**:
```
1. AI Detection Prompts (dynamic optimization)
2. Localization Prompts (cultural authenticity)
3. Base Content Prompts (material-specific instructions)
```

## Localization Characteristics

### Italian (Alessandro Moretti)
- **Language**: Rich, descriptive language with elegant phrasing
- **Style**: Longer flowing sentences with sophisticated vocabulary
- **Tone**: Warm, passionate expertise with personal opinions
- **Characteristics**: "beautiful technique", "elegant solution", conversational questions

### Indonesian (Ikmanda Roswati)  
- **Language**: Simplified grammar patterns, repetition for emphasis
- **Style**: Direct, practical approach with contextual awareness
- **Tone**: Community-focused with environmental considerations
- **Characteristics**: "works well, really well", tropical climate considerations

### Taiwan (Yi-Chun Lin)
- **Language**: Technical precision with measured explanations
- **Style**: Structured, methodical approach
- **Tone**: Professional with practical focus

### USA (Todd Dunning)
- **Language**: Direct, efficiency-focused communication
- **Style**: Clear, concise technical explanations
- **Tone**: Results-oriented with practical applications

## Usage Examples

### Basic Usage
```python
from components.text.localization import get_required_localization_prompt

author_info = {
    'id': 2,
    'name': 'Alessandro Moretti', 
    'country': 'Italy'
}

localization_prompt = get_required_localization_prompt(author_info)
# This prompt MUST be included in every text generation request
```

### Validation
```python
from components.text.localization import validate_localization_support

# Check if localization is available for a country
if validate_localization_support('Italy'):
    print("Italian localization is available")
else:
    print("Localization not supported")
```

## Implementation Details

### Error Handling

The system implements fail-fast behavior:

```python
# In fail_fast_generator.py _construct_prompt method
try:
    localization_prompt = get_required_localization_prompt(author_info)
except Exception as e:
    validation_failure(
        "fail_fast_generator",
        f"Failed to load required localization prompts: {e}",
        field="localization"
    )
    raise ValueError(f"Localization prompts are mandatory: {e}")
```

### Prompt Structure

The complete localization prompt includes:

```
=== LOCALIZATION REQUIREMENTS (MANDATORY) ===

PERSONA: [Author Name]
BACKGROUND: [Author Background]
PERSONALITY: [Personality Traits]
TONE OBJECTIVE: [Desired Tone]

LANGUAGE PATTERNS:
- vocabulary: [Vocabulary characteristics]
- sentence_structure: [Sentence patterns]
- [Additional patterns...]

CONTENT CONSTRAINTS:
- Maximum word count: [Count]
- Target word range: [Range]

FORMATTING PATTERNS:
- [Formatting preferences...]

=== END LOCALIZATION REQUIREMENTS ===

CRITICAL: You MUST follow ALL localization requirements above.
Failure to follow localization requirements will result in content rejection.
```

## Validation & Testing

### Test Results ✅

**Aluminum (Indonesian Author - Ikmanda Roswati):**
- ✅ Correct author attribution
- ✅ Indonesian language patterns ("works well, really well")
- ✅ Tropical climate considerations  
- ✅ Community impact focus
- ✅ Simplified grammar patterns

**Alumina (Italian Author - Alessandro Moretti):**
- ✅ Correct author attribution
- ✅ Italian eloquence ("beautiful technique", "sublime precision")
- ✅ Sophisticated vocabulary ("exquisitely precise", "innate beauty")
- ✅ Conversational style ("don't you think?")
- ✅ Passionate expertise with personal opinions

## Troubleshooting

### Common Issues

1. **"Localization prompts not found"**
   - Ensure persona and formatting files exist in `optimizer/text_optimization/prompts/`
   - Check country name mapping in `prompt_chain.py`

2. **Wrong author in final content**
   - Check that `_format_content_with_frontmatter` prioritizes `author_info` over `frontmatter_data`
   - Verify material's `author_id` in `data/Materials.yaml`

3. **Localization not being applied**
   - Verify localization prompt is first in the prompt construction
   - Check that `get_required_localization_prompt` is called before generation

### Debug Commands

```bash
# Test localization loading
python3 -c "
from components.text.localization import get_required_localization_prompt
author_info = {'name': 'Alessandro Moretti', 'country': 'Italy'}
print(get_required_localization_prompt(author_info))
"

# Validate author resolution
python3 -c "
import json
# Extract author from frontmatter author_object
author_data = frontmatter_data.get('author_object', {})['authors']
for author in authors:
    print(f'ID: {author[\"id\"]}, Name: {author[\"name\"]}, Country: {author[\"country\"]}')
"
```

## Future Enhancements

1. **Additional Countries**: Add support for more countries/cultures
2. **Dynamic Persona Loading**: Allow runtime persona customization
3. **Quality Scoring**: Add localization quality metrics
4. **A/B Testing**: Compare different persona variations

## Files Modified

- `components/text/localization/prompt_chain.py` (NEW)
- `components/text/localization/__init__.py` (NEW)
- `components/text/generators/fail_fast_generator.py` (UPDATED)
- `components/text/generator.py` (UPDATED)

## Dependencies

- `optimizer/text_optimization/prompts/personas/` (persona files)
- `optimizer/text_optimization/prompts/formatting/` (formatting files)
- Frontmatter data with `author_object` field
- `data/Materials.yaml` (material-author mapping)
