# Slider Disconnect Fix: Implementation Plan

**Date**: November 14, 2025  
**Purpose**: Step-by-step code changes to connect all 10 sliders to generation output

---

## 🎯 Overview

**Found**: 4 sliders have disconnects where values are calculated but not used  
**Impact**: Users change sliders but see no effect on output  
**Solution**: Pass calculated parameters through the pipeline properly

---

## 📋 Changes Required (by File)

### Change 1: `processing/config/dynamic_config.py`
**Purpose**: Create unified parameter bundles

**Location**: Add new methods after `calculate_voice_parameters()`

```python
def calculate_enrichment_params(self) -> Dict[str, Any]:
    """
    Calculate all parameters for DataEnricher fact formatting.
    
    Returns dict with:
    - technical_intensity: 0-100 (controls spec density)
    - context_detail_level: 0-100 (controls description length)
    - fact_formatting_style: 'formal' | 'conversational' (based on engagement)
    """
    technical = self.base_config.get_technical_language_intensity()
    context = self.base_config.get_context_specificity()
    engagement = self.base_config.get_engagement_style()
    
    # Determine fact formatting style
    if engagement < 40:
        formatting = 'formal'  # "2.7 g/cm³"
    elif engagement < 70:
        formatting = 'balanced'  # "roughly 2.7 g/cm³"
    else:
        formatting = 'conversational'  # "around 2.7 g/cm³ (pretty dense!)"
    
    return {
        'technical_intensity': technical,
        'context_detail_level': context,
        'fact_formatting_style': formatting,
        'engagement_level': engagement
    }

def get_all_generation_params(self) -> Dict[str, Any]:
    """
    Get ALL parameters needed for generation in one call.
    Orchestrator should call this once and pass bundles to components.
    """
    return {
        'api_params': {
            'temperature': self.calculate_temperature(),
            'max_tokens': self.calculate_max_tokens(),
        },
        'enrichment_params': self.calculate_enrichment_params(),
        'voice_params': self.calculate_voice_parameters(),
        'validation_params': {
            'readability_thresholds': self.calculate_readability_thresholds(),
            'grammar_strictness': self.calculate_grammar_strictness(),
            'detection_threshold': self.calculate_detection_threshold(),
        }
    }
```

**Lines Added**: ~50  
**Risk**: LOW - purely additive, no existing code changed

---

### Change 2: `processing/orchestrator.py`
**Purpose**: Get all params and pass to components

**Location**: Line ~90-120 in `generate()` method

**Before**:
```python
def generate(self, topic: str, component_type: str, voice: str, ...) -> ComponentResult:
    # ... init code ...
    
    # Get technical intensity
    technical_intensity = self.dynamic_config.base_config.get_technical_language_intensity()
    
    # Get facts
    facts = self.data_enricher.fetch_real_facts(topic, ...)
    facts_str = self.data_enricher.format_facts_for_prompt(facts, technical_intensity=technical_intensity)
    
    # Build prompt
    prompt = PromptBuilder.build_unified_prompt(
        topic=topic,
        voice=voice,
        voice_profile=voice_profile,
        facts=facts_str,
        # ... other args ...
    )
```

**After**:
```python
def generate(self, topic: str, component_type: str, voice: str, ...) -> ComponentResult:
    # ... init code ...
    
    # Get ALL parameters from dynamic config (single source of truth)
    all_params = self.dynamic_config.get_all_generation_params()
    
    # Get facts with enrichment params
    facts = self.data_enricher.fetch_real_facts(topic, ...)
    facts_str = self.data_enricher.format_facts_for_prompt(
        facts, 
        enrichment_params=all_params['enrichment_params']  # ✅ Full params
    )
    
    # Build prompt with voice params
    prompt = PromptBuilder.build_unified_prompt(
        topic=topic,
        voice=voice,
        voice_profile=voice_profile,
        facts=facts_str,
        voice_params=all_params['voice_params'],  # ✅ NEW!
        component_type=component_type,
        # ... other args ...
    )
```

**Lines Changed**: ~15  
**Risk**: LOW - backward compatible, only adding new params

---

### Change 3: `processing/enrichment/data_enricher.py`
**Purpose**: Use full enrichment params, not just technical_intensity

**Location**: Line ~108-152 in `format_facts_for_prompt()`

**Before**:
```python
def format_facts_for_prompt(self, facts: Dict[str, Any], technical_intensity: int = 50) -> str:
    """Format facts with tiered technical detail."""
    
    # Determine fact density based on technical_intensity only
    if technical_intensity <= 30:
        max_props = 2
        max_settings = 1
        include_apps = False
    elif technical_intensity <= 60:
        max_props = 3
        max_settings = 2
        include_apps = True
    else:
        max_props = 5
        max_settings = 3
        include_apps = True
    
    # Format properties (always same format)
    prop_str = f"{prop_name}: {value} {unit}"
```

**After**:
```python
def format_facts_for_prompt(self, facts: Dict[str, Any], enrichment_params: Dict[str, Any]) -> str:
    """
    Format facts using full enrichment params.
    
    enrichment_params = {
        'technical_intensity': 0-100,
        'context_detail_level': 0-100,
        'fact_formatting_style': 'formal' | 'balanced' | 'conversational',
        'engagement_level': 0-100
    }
    """
    technical = enrichment_params.get('technical_intensity', 50)
    context_level = enrichment_params.get('context_detail_level', 50)
    formatting = enrichment_params.get('fact_formatting_style', 'formal')
    
    # Determine fact density (existing logic)
    if technical <= 30:
        max_props = 2
        max_settings = 1
        include_apps = False
    elif technical <= 60:
        max_props = 3
        max_settings = 2
        include_apps = True
    else:
        max_props = 5
        max_settings = 3
        include_apps = True
    
    # ✅ NEW: Determine description detail from context_specificity
    if context_level <= 30:
        app_text_limit = 100  # Brief descriptions
        prop_explain = False  # No explanations
    elif context_level <= 60:
        app_text_limit = 200  # Medium descriptions
        prop_explain = False  # No explanations
    else:
        app_text_limit = 300  # Detailed descriptions
        prop_explain = True  # Add context explanations
    
    # ✅ NEW: Format values based on engagement_style
    def format_value(value, unit, prop_name):
        if formatting == 'formal':
            return f"{prop_name}: {value} {unit}"
        elif formatting == 'balanced':
            # Add softeners like "roughly", "around"
            return f"{prop_name}: roughly {value} {unit}"
        else:  # conversational
            # Add context and enthusiasm
            context_notes = {
                'density': '(pretty dense!)',
                'modulus': '(very stiff)',
                'conductivity': '(great conductor)',
                # ... more mappings
            }
            note = context_notes.get(prop_name.lower(), '')
            return f"{prop_name}: around {value} {unit} {note}".strip()
    
    # Use format_value() when building property strings
    prop_str = format_value(value, unit, prop_name)
```

**Lines Changed**: ~60  
**Risk**: MEDIUM - changes existing formatting logic, needs testing

---

### Change 4: `processing/generation/prompt_builder.py`
**Purpose**: Use voice params to control author personality in prompts

**Location**: Line ~50-150 in `build_unified_prompt()` and `_build_spec_driven_prompt()`

**Before**:
```python
@staticmethod
def build_unified_prompt(
    topic: str,
    voice: str,
    voice_profile: Dict[str, Any],
    facts: str,
    component_type: str = 'subtitle',
    # ...
) -> str:
    # Build voice section (static)
    voice_section = PromptBuilder._build_voice_section(voice_profile)
    
    # Build anti-AI rules (static)
    anti_ai_section = PromptBuilder._build_anti_ai_rules()
    
    # Assemble prompt
    prompt = f"""
Topic: {topic}

{voice_section}

{anti_ai_section}

Facts:
{facts}

Instructions: Write a {component_type} about {topic}.
"""
```

**After**:
```python
@staticmethod
def build_unified_prompt(
    topic: str,
    voice: str,
    voice_profile: Dict[str, Any],
    facts: str,
    voice_params: Dict[str, Any],  # ✅ NEW!
    component_type: str = 'subtitle',
    # ...
) -> str:
    """
    Build prompt with voice parameters controlling personality injection.
    
    voice_params = {
        'trait_frequency': 0.0-1.0,  # How often author traits appear
        'opinion_rate': 0.0-1.0,     # How often opinions included
        'reader_address_rate': 0.0-1.0,  # How often use "you"
        'colloquialism_frequency': 0.0-1.0  # Informal language rate
    }
    """
    # Build voice section WITH intensity control
    voice_section = PromptBuilder._build_voice_section(
        voice_profile, 
        voice_params  # ✅ Pass params
    )
    
    # Build anti-AI rules (static for now, could be dynamic later)
    anti_ai_section = PromptBuilder._build_anti_ai_rules()
    
    # ✅ NEW: Add personality guidance based on voice_params
    personality_guidance = ""
    if voice_params.get('opinion_rate', 0) > 0.5:
        personality_guidance += "\n- Include personal perspective or insight where appropriate"
    if voice_params.get('reader_address_rate', 0) > 0.5:
        personality_guidance += "\n- Address reader directly using 'you' naturally"
    if voice_params.get('colloquialism_frequency', 0) > 0.5:
        personality_guidance += "\n- Use informal language and colloquialisms fitting the voice"
    
    # Assemble prompt
    prompt = f"""
Topic: {topic}

{voice_section}

{anti_ai_section}

{personality_guidance}

Facts:
{facts}

Instructions: Write a {component_type} about {topic}.
"""
```

**Location 2**: Update `_build_voice_section()` helper

**Before**:
```python
@staticmethod
def _build_voice_section(voice_profile: Dict[str, Any]) -> str:
    """Build voice section from profile."""
    traits = voice_profile.get('linguistic_traits', [])
    sentence_structure = voice_profile.get('sentence_structure', '')
    
    return f"""
Voice Profile: {voice_profile.get('author_name')}
Traits: {', '.join(traits)}
Sentence Structure: {sentence_structure}
"""
```

**After**:
```python
@staticmethod
def _build_voice_section(voice_profile: Dict[str, Any], voice_params: Dict[str, Any]) -> str:
    """
    Build voice section with intensity control.
    
    voice_params['trait_frequency'] controls how strongly to apply traits.
    """
    traits = voice_profile.get('linguistic_traits', [])
    sentence_structure = voice_profile.get('sentence_structure', '')
    trait_freq = voice_params.get('trait_frequency', 0.5)
    
    # Adjust trait application based on intensity
    if trait_freq < 0.3:
        trait_instruction = "Subtly hint at these traits"
    elif trait_freq < 0.7:
        trait_instruction = "Apply these traits naturally"
    else:
        trait_instruction = "Strongly emphasize these traits throughout"
    
    return f"""
Voice Profile: {voice_profile.get('author_name')}
Traits: {', '.join(traits)}
Trait Application: {trait_instruction}
Sentence Structure: {sentence_structure}
"""
```

**Lines Changed**: ~80  
**Risk**: MEDIUM - changes core prompt building, needs thorough testing

---

## 🧪 Testing Strategy

### Test 1: Voice Intensity Impact
```bash
# Set author_voice_intensity = 10 (minimal)
python3 run.py --material "Aluminum" --subtitle

# Expect: Neutral voice, minimal personality
# Example: "Aluminum alloys exhibit high strength-to-weight ratios."

# Set author_voice_intensity = 90 (maximal)
python3 run.py --material "Aluminum" --subtitle

# Expect: Strong personality, clear author presence
# Example: "I've always found aluminum fascinating for its lightweight strength."
```

### Test 2: Engagement Style Impact
```bash
# Set engagement_style = 10 (formal)
python3 run.py --material "Steel" --subtitle

# Expect: Formal facts, "7.85 g/cm³"

# Set engagement_style = 90 (conversational)
python3 run.py --material "Steel" --subtitle

# Expect: Conversational facts, "around 7.85 g/cm³ (pretty hefty!)"
```

### Test 3: Context Specificity Impact
```bash
# Set context_specificity = 10 (minimal detail)
python3 run.py --material "Titanium" --subtitle

# Expect: Brief app descriptions (100 chars), 2 properties

# Set context_specificity = 90 (high detail)
python3 run.py --material "Titanium" --subtitle

# Expect: Detailed app descriptions (300 chars), 5 properties
```

### Test 4: Personality Intensity Impact
```bash
# Set personality_intensity = 10 (neutral)
python3 run.py --material "Copper" --subtitle

# Expect: No opinions, factual only

# Set personality_intensity = 90 (opinionated)
python3 run.py --material "Copper" --subtitle

# Expect: Includes "In my view..." or "I find..." statements
```

---

## 📊 Rollback Plan

If changes cause issues:

```bash
# Restore each file individually
git checkout HEAD -- processing/config/dynamic_config.py
git checkout HEAD -- processing/orchestrator.py
git checkout HEAD -- processing/enrichment/data_enricher.py
git checkout HEAD -- processing/generation/prompt_builder.py

# Or restore entire directory
git checkout HEAD -- processing/
```

---

## 🎯 Implementation Order

### Phase 1: Foundation (30 min)
1. ✅ Add `calculate_enrichment_params()` to dynamic_config.py
2. ✅ Add `get_all_generation_params()` to dynamic_config.py
3. ✅ Test: Verify methods return expected dicts

### Phase 2: Orchestrator (15 min)
4. ⏳ Update orchestrator to call `get_all_generation_params()`
5. ⏳ Pass `enrichment_params` to data_enricher
6. ⏳ Pass `voice_params` to prompt_builder
7. ⏳ Test: Verify no errors with new params

### Phase 3: Data Enricher (45 min)
8. ⏳ Update `format_facts_for_prompt()` signature
9. ⏳ Add context_detail_level logic for descriptions
10. ⏳ Add fact_formatting_style logic for values
11. ⏳ Test: Generate with different engagement/context settings

### Phase 4: Prompt Builder (60 min)
12. ⏳ Update `build_unified_prompt()` signature
13. ⏳ Update `_build_voice_section()` to use voice_params
14. ⏳ Add personality_guidance section
15. ⏳ Test: Generate with different voice/personality settings

### Phase 5: Integration Testing (30 min)
16. ⏳ Test all 10 sliders with extreme values (0 vs 100)
17. ⏳ Verify observable differences in output
18. ⏳ Run AI detection tests (should still pass)
19. ⏳ Document slider effects in COPILOT_GENERATION_GUIDE.md

**Total Estimated Time**: 3 hours

---

## 📈 Success Criteria

After implementation:

✅ **All 10 sliders have observable effects**  
✅ **Voice params visible in prompts** (can grep for trait_frequency guidance)  
✅ **Fact formatting changes** with engagement_style (formal vs conversational)  
✅ **Context detail changes** with context_specificity (100 vs 300 char descriptions)  
✅ **No regression in AI detection** (still scoring 0.000-0.122)  
✅ **No errors in generation** (all 4 components working)

---

## 🚀 Ready to Implement?

**Next Command**:
```bash
# Create a backup branch first
git checkout -b slider-integration-fix

# Then start with Phase 1: dynamic_config.py changes
```

Let me know when you're ready and I'll make the changes!
