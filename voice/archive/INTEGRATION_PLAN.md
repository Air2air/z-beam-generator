# Voice System Integration Plan

## Overview

This document outlines how the centralized `/voice` folder system integrates with existing text-based components, with special focus on the caption component that was recently evaluated.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Component Layer                           │
│  (caption, text, tags, frontmatter description)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              VoiceOrchestrator API                           │
│  orchestrator.get_voice_for_component(type, context)        │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┬──────────┬──────────────┐
│ Country      │ Base     │ Component    │
│ Profile      │ Voice    │ Adaptation   │
│ (taiwan.yaml)│          │ (caption)    │
└──────────────┴──────────┴──────────────┘
        │            │            │
        └────────────┴────────────┘
                     ▼
          Complete Voice Instructions
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI Generation                               │
│  (DeepSeek, Winston, etc. with voice-aware prompts)        │
└─────────────────────────────────────────────────────────────┘
```

## Caption Component Integration

### Current Caption Prompt Structure

**File**: `components/caption/generators/generator.py`

**Current Approach** (Embedded Voice):
```python
def _build_prompt(self, material_data, frontmatter_data):
    prompt = f"""You are an analytical microscopist documenting surface 
    characterization findings with technical precision and clarity.
    
    WRITING STANDARDS:
    - Document what is directly observable at 500x magnification
    - Use standard analytical terminology (SEM, XPS, EDX)
    - Maintain authoritative, professional tone
    - Employ active voice construction where appropriate
    ...
    """
```

### New Approach (Voice System Integration)

```python
from voice.orchestrator import VoiceOrchestrator

def _build_prompt(self, material_data, frontmatter_data):
    # Extract author country from frontmatter
    author_obj = frontmatter_data.get('author_object', {})
    country = author_obj.get('country', 'United States')
    
    # Get voice instructions from orchestrator
    voice = VoiceOrchestrator(country=country)
    voice_instructions = voice.get_voice_for_component(
        component_type="caption",
        context={
            "material": material_data.get("name"),
            "technical_level": "advanced",
            "format": "before_after_observations"
        }
    )
    
    # Build prompt with voice-aware instructions
    prompt = f"""{voice_instructions}

MATERIAL CONTEXT:
Material: {material_data.get("name")}
Category: {material_data.get("category")}
Key Properties: {self._format_properties(material_data)}

MICROSCOPIC OBSERVATION CONTEXT:
Magnification: 500x
Imaging Mode: SEM with EDX capability
Analysis Focus: Surface contamination and cleaning effectiveness

TASK:
Generate two captions for laser cleaning documentation:

1. BEFORE CLEANING (beforeText):
   - Document visible contamination characteristics
   - Describe layering, composition, thickness observations
   - Note impact on surface properties (reflectivity, roughness)

2. AFTER CLEANING (afterText):
   - Document cleaned surface characteristics
   - Describe restoration quality and surface integrity
   - Note measurable improvements in performance metrics

OUTPUT FORMAT:
Return JSON with beforeText and afterText keys.
"""
    
    return prompt
```

### Benefits of Voice Integration

1. **Country-Specific Voice**: Taiwan author gets academic precision, Italy gets descriptive elegance
2. **Consistent Updates**: Change voice once in `voice/profiles/taiwan.yaml`, affects all components
3. **Fail-Fast**: Invalid country or missing profile fails immediately
4. **Testable**: Voice can be validated independently from content
5. **Maintainable**: Adding new country requires one profile file, no component changes

## Voice Variations by Country

### Taiwan (Yi-Chun Lin)

**Caption Style**: Formal analytical reporting
```
BEFORE: "Surface examination reveals extensive contamination layer with 
measured thickness of 15-25 μm. Systematic analysis demonstrates significant 
oxide accumulation affecting reflectivity by 35-40%."

AFTER: "Post-treatment inspection confirms complete contaminant removal with 
surface roughness Ra < 0.8 μm. Methodical evaluation demonstrates restored 
surface integrity with improved reflectivity of 92-95%."
```

**Linguistic Characteristics**:
- Passive voice for observations ("reveals", "demonstrates", "confirms")
- Precise measurements with units
- Academic register
- Systematic documentation approach

### Italy (Alessandro Moretti)

**Caption Style**: Sophisticated descriptive analysis
```
BEFORE: "What strikes one immediately is the remarkable complexity of this 
contamination structure - multiple layers creating a sophisticated challenge. 
The precision required here demands elegant technical solutions."

AFTER: "The result speaks to engineering excellence: a pristine surface 
revealing the natural beauty of the metallic substrate. One can observe 
the remarkable restoration of crystalline structure, testimony to technical 
sophistication."
```

**Linguistic Characteristics**:
- Descriptive richness with aesthetic appreciation
- Longer flowing sentences with embedded clauses
- Personal observations ("one notices", "what strikes")
- Technical elegance emphasis

### Indonesia (Ikmanda Roswati)

**Caption Style**: Clear accessible technical explanation
```
BEFORE: "The surface shows heavy contamination, really heavy buildup. This 
contamination works against the material performance, especially in marine 
environments where corrosion is a concern."

AFTER: "The cleaning works well, very effective for this application. The 
surface is clean and ready for practical use, especially good for renewable 
energy systems where efficiency is important."
```

**Linguistic Characteristics**:
- Simplified sentence structures
- Repetition for emphasis ("heavy contamination, really heavy")
- Practical application focus
- Environmental context awareness

### United States (Todd Dunning)

**Caption Style**: Clear professional communication
```
BEFORE: "Surface exhibits significant contamination buildup impacting 
performance metrics by 40%. Advanced imaging reveals multi-layer 
contamination structure requiring optimized cleaning parameters."

AFTER: "Cleaning process delivers exceptional results - complete contaminant 
removal with surface integrity preserved. Performance metrics show 95% 
reflectivity restoration, meeting critical biomedical device specifications."
```

**Linguistic Characteristics**:
- Concise, results-focused
- Active voice with clear subjects
- Innovation and efficiency emphasis
- Business outcome framing

## Implementation Checklist

### Phase 1: Voice System Setup ✅
- [x] Create `/voice` directory structure
- [x] Build `orchestrator.py` with VoiceOrchestrator class
- [x] Create Taiwan voice profile (complete example)
- [ ] Create Italy voice profile
- [ ] Create Indonesia voice profile
- [ ] Create United States voice profile
- [ ] Create base voice foundations

### Phase 2: Caption Component Integration
- [ ] Update `components/caption/generators/generator.py`
- [ ] Add VoiceOrchestrator import
- [ ] Modify `_build_prompt()` method
- [ ] Extract author country from frontmatter
- [ ] Call `orchestrator.get_voice_for_component("caption")`
- [ ] Inject voice instructions into prompt
- [ ] Test with all 4 countries

### Phase 3: Text Component Integration
- [ ] Update text generation prompt building
- [ ] Integrate VoiceOrchestrator
- [ ] Test with all author personas
- [ ] Validate voice consistency

### Phase 4: Additional Components
- [ ] Tags component (subtle voice influence)
- [ ] Frontmatter descriptions
- [ ] Future text-based components

### Phase 5: Validation & Testing
- [ ] Create voice validation tests
- [ ] Generate samples from all countries
- [ ] Compare voice authenticity
- [ ] Measure consistency scores

## Code Change Summary

### Minimal Changes Required

**Caption Generator** (`components/caption/generators/generator.py`):
```python
# ADD: Import at top
from voice.orchestrator import VoiceOrchestrator

# MODIFY: _build_prompt method (~line 104)
def _build_prompt(self, material_data, frontmatter_data):
    # EXTRACT author country
    author_obj = frontmatter_data.get('author_object', {})
    country = author_obj.get('country', 'United States')
    
    # GET voice instructions
    voice = VoiceOrchestrator(country=country)
    voice_instructions = voice.get_voice_for_component('caption')
    
    # REPLACE hardcoded voice with orchestrated voice
    prompt = f"""{voice_instructions}
    
    [rest of prompt with material context and task...]
    """
    return prompt
```

**That's it!** Voice system handles all country-specific variations.

## Testing Strategy

### Unit Tests
```python
def test_voice_orchestrator_taiwan():
    voice = VoiceOrchestrator("Taiwan")
    instructions = voice.get_voice_for_component("caption")
    
    assert "systematic" in instructions.lower()
    assert "methodical" in instructions.lower()
    assert voice.get_word_limit() == 380

def test_voice_orchestrator_italy():
    voice = VoiceOrchestrator("Italy")
    instructions = voice.get_voice_for_component("caption")
    
    assert "precision" in instructions.lower()
    assert "elegance" in instructions.lower() or "elegant" in instructions.lower()
    assert voice.get_word_limit() == 450
```

### Integration Tests
```python
def test_caption_generation_with_voice():
    # Test that caption component correctly uses voice system
    generator = CaptionComponentGenerator()
    
    frontmatter = {
        "author_object": {"country": "Taiwan", ...}
    }
    
    result = generator.generate(
        material_name="Aluminum",
        material_data={...},
        frontmatter_data=frontmatter
    )
    
    # Validate Taiwan voice characteristics in output
    assert "systematic" in result.content.lower() or "methodical" in result.content.lower()
```

### Voice Validation Tests
```python
from voice.validator import VoiceValidator

def test_generated_caption_voice_consistency():
    validator = VoiceValidator()
    
    result = validator.validate_content(
        content=generated_caption,
        country="Taiwan",
        component_type="caption"
    )
    
    assert result.is_valid
    assert result.linguistic_authenticity_score >= 70
```

## Benefits Summary

1. ✅ **Single Source of Truth**: Update voice in one YAML file
2. ✅ **Country Authenticity**: Proper linguistic patterns, not errors
3. ✅ **Maintainable**: Add new countries without touching component code
4. ✅ **Testable**: Voice validation separate from generation
5. ✅ **Consistent**: All components share same voice logic
6. ✅ **Fail-Fast**: Invalid countries fail immediately
7. ✅ **Scalable**: New components automatically get voice
8. ✅ **Documented**: Voice profiles are self-documenting

## Migration Timeline

- **Week 1**: Complete voice profiles for all 4 countries
- **Week 2**: Integrate caption component, test thoroughly
- **Week 3**: Integrate text component, validate consistency
- **Week 4**: Add validation system, create test suite
- **Week 5**: Deploy and monitor, refine profiles based on results

## Future Enhancements

1. **Dynamic Voice Adjustment**: Context-aware voice modulation
2. **Voice Learning**: Analyze successful content to refine profiles
3. **A/B Testing**: Compare voice variations for effectiveness
4. **Voice Metrics Dashboard**: Track consistency and authenticity over time
5. **Multi-Author Support**: Multiple authors per country with sub-profiles
