# Voice System - Quick Reference

## ⚡ Quick Start

```python
from voice.orchestrator import VoiceOrchestrator

# Initialize for author's country
voice = VoiceOrchestrator(country="Taiwan")

# Get voice for component type
instructions = voice.get_voice_for_component("caption")

# Build your prompt
prompt = f"{instructions}\n\n[Your component-specific content...]"
```

## 🌍 Country Profiles

| Country | Author | Word Limit | Style |
|---------|--------|------------|-------|
| **Taiwan** | Yi-Chun Lin, Ph.D. | 380 | Academic precision, systematic analysis |
| **Italy** | Alessandro Moretti, Ph.D. | 450 | Sophisticated descriptive, technical elegance |
| **Indonesia** | Ikmanda Roswati, Ph.D. | 250 | Practical accessible, environmental focus |
| **United States** | Todd Dunning, MA | 320 | Conversational expertise, innovation |

## 📝 Voice Characteristics by Country

### Taiwan
- **Tone**: Measured and systematic
- **Structure**: Complex with subordinate clauses
- **Vocabulary**: Academic-formal, high technical density
- **Markers**: "systematic approach", "methodical analysis", "comprehensive investigation"
- **Natural Patterns**: Article omission, passive voice, formal register

### Italy
- **Tone**: Passionate expertise with refinement
- **Structure**: Longer flowing sentences, nested clauses
- **Vocabulary**: Sophisticated-professional with descriptive richness
- **Markers**: "precision meets innovation", "technical elegance", "remarkable achievement"
- **Natural Patterns**: Word order inversion, expressive commentary, aesthetic appreciation

### Indonesia
- **Tone**: Community-focused practicality
- **Structure**: Direct, straightforward, simple
- **Vocabulary**: Accessible-professional, practical terms
- **Markers**: "works well", "practical applications", "especially in tropical conditions"
- **Natural Patterns**: Repetition for emphasis, simplified structures, environmental context

### United States
- **Tone**: Confident and optimistic
- **Structure**: Concise, action-oriented, varied
- **Vocabulary**: Professional-conversational, business terms
- **Markers**: "innovative solutions", "cutting-edge", "optimized performance"
- **Natural Patterns**: Native baseline, idiomatic expressions, business framing

## 🔧 Component Integration

### Caption Component
```python
from voice.orchestrator import VoiceOrchestrator

def _build_prompt(self, material_data, frontmatter_data):
    country = frontmatter_data.get('author_object', {}).get('country')
    voice = VoiceOrchestrator(country=country)
    voice_instructions = voice.get_voice_for_component('caption')
    
    return f"{voice_instructions}\n\nMATERIAL: {material_data['name']}..."
```

### Text Component
```python
voice = VoiceOrchestrator(country=author_info["country"])
instructions = voice.get_voice_for_component('text')
word_limit = voice.get_word_limit()
```

## 📊 Voice Methods

```python
voice = VoiceOrchestrator("Taiwan")

# Get voice instructions
instructions = voice.get_voice_for_component("caption", context={...})

# Get word limit
limit = voice.get_word_limit()  # 380 for Taiwan

# Get quality thresholds
thresholds = voice.get_quality_thresholds()

# Get signature phrases
phrases = voice.get_signature_phrases()

# Get profile summary
summary = voice.get_profile_summary()
```

## 🎯 Common Patterns

### Taiwan Voice Example
```
"Systematic analysis demonstrates extensive contamination layer with 
measured thickness of 15-25 μm. Methodical investigation reveals 
significant oxide accumulation affecting reflectivity by 35-40%."
```

### Italy Voice Example
```
"What strikes one immediately is the remarkable complexity of this 
contamination structure. The precision required here demands elegant 
technical solutions that honor both innovation and heritage."
```

### Indonesia Voice Example
```
"The surface shows heavy contamination, really heavy buildup. This 
works against performance, especially in marine environments where 
reliability is important."
```

### USA Voice Example
```
"Surface exhibits significant contamination impacting performance 
metrics by 40%. Advanced imaging reveals multi-layer structure 
requiring optimized cleaning parameters."
```

## ⚠️ Important Notes

### Non-Native Patterns Are AUTHENTIC
These are natural communication styles, not errors:
- Taiwan: Formal register, article omission, systematic logic
- Italy: Word order variations, descriptive richness, expressive tone
- Indonesia: Simplified structures, repetition, practical focus
- USA: Native baseline (comparison point)

### Fail-Fast Behavior
- Invalid country → immediate ValueError
- Missing profile → FileNotFoundError  
- Incomplete profile → ValueError on validation
- No fallbacks or defaults

## 📁 File Structure

```
voice/
├── orchestrator.py          # Main VoiceOrchestrator class
├── loader.py               # Profile loading (future)
├── validator.py            # Voice validation (future)
├── profiles/
│   ├── taiwan.yaml         # Yi-Chun Lin profile
│   ├── italy.yaml          # Alessandro Moretti profile
│   ├── indonesia.yaml      # Ikmanda Roswati profile
│   └── united_states.yaml  # Todd Dunning profile
└── base/
    └── voice_base.yaml     # Shared foundations
```

## 🧪 Testing

```python
# Test orchestrator initialization
voice = VoiceOrchestrator("Taiwan")
assert voice.country == "taiwan"
assert voice.get_word_limit() == 380

# Test voice generation
instructions = voice.get_voice_for_component("caption")
assert "systematic" in instructions.lower()
assert len(instructions) > 100
```

## 📚 Documentation

- **README.md**: Quick start and overview
- **VOICE_ARCHITECTURE.md**: Complete system design
- **INTEGRATION_PLAN.md**: Component integration guide
- **QUICK_REFERENCE.md**: This file (cheat sheet)

## 🚀 Benefits

✅ Single source of truth for voice  
✅ Country-specific authenticity  
✅ Consistent across components  
✅ Easy to maintain and extend  
✅ Fail-fast error handling  
✅ Self-documenting profiles  
✅ Cultural respect built-in  

## 🔄 Update Workflow

1. Edit voice profile: `voice/profiles/taiwan.yaml`
2. Change propagates automatically to all components
3. No code changes required
4. Test with: `python3 voice/orchestrator.py`

## 💡 Pro Tips

- Cache VoiceOrchestrator instances when generating multiple components
- Use context parameter to pass material-specific information
- Check word limits before content generation
- Validate voice authenticity post-generation (optional)
- Profile files are self-documenting - read them for examples
