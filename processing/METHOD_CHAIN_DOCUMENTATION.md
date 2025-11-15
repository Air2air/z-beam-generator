# Processing System Method Chain Documentation

**Date**: November 14, 2025  
**Purpose**: Document the complete method chain from config → API to ensure robustness

---

## 🔗 Complete Method Chain

### Level 1: Configuration Layer

```
processing/config.yaml
    ↓
IntensityManager (processing/intensity/intensity_manager.py)
    ├→ get_author_voice() → returns int 0-100
    ├→ get_technical_language() → returns int 0-100
    ├→ get_personality_intensity() → returns int 0-100
    ├→ get_engagement_style() → returns int 0-100
    ├→ get_context_specificity() → returns int 0-100
    ├→ get_sentence_rhythm() → returns int 0-100
    ├→ get_imperfection_tolerance() → returns int 0-100
    ├→ get_structural_predictability() → returns int 0-100
    ├→ get_ai_avoidance() → returns int 0-100
    └→ get_length_variation() → returns int 0-100
    
    PLUS Alias Methods (for backward compatibility):
    ├→ get_author_voice_intensity() → calls get_author_voice()
    ├→ get_technical_language_intensity() → calls get_technical_language()
    ├→ get_ai_avoidance_intensity() → calls get_ai_avoidance()
    ├→ get_sentence_rhythm_variation() → calls get_sentence_rhythm()
    └→ get_length_variation_range() → calls get_length_variation()
```

### Level 2: Dynamic Configuration Calculator

```
DynamicConfig (processing/config/dynamic_config.py)
    ├→ __init__(base_config: IntensityManager)
    │
    ├→ calculate_temperature(component_type: str) -> float
    │   Uses: imperfection, rhythm, structural
    │   Returns: 0.5-1.1
    │   Formula: base + (creativity_factor - 0.5) * 0.4
    │
    ├→ calculate_max_tokens(component_type: str) -> int
    │   Uses: length_variation, context
    │   Returns: 300-800
    │   Formula: base * (1 + context_bonus + variation_bonus)
    │
    ├→ calculate_detection_threshold(strict_mode: bool) -> float
    │   Uses: ai_avoidance, imperfection
    │   Returns: 0.30-0.50
    │   Formula: base * (1 - leniency_factor)
    │
    ├→ calculate_enrichment_params() -> Dict[str, Any]
    │   Uses: technical, context, engagement
    │   Returns: {
    │       'technical_intensity': 0-100,
    │       'context_detail_level': 0-100,
    │       'fact_formatting_style': 'formal'|'balanced'|'conversational',
    │       'engagement_level': 0-100
    │   }
    │
    ├→ calculate_voice_parameters() -> Dict[str, Any]
    │   Uses: author_voice, personality, engagement
    │   Returns: {
    │       'trait_frequency': 0.0-1.0,
    │       'opinion_rate': 0.0-1.0,
    │       'reader_address_rate': 0.0-1.0,
    │       'colloquialism_frequency': 0.0-1.0
    │   }
    │
    └→ get_all_generation_params(component_type: str) -> Dict[str, Any]
        Returns: {
            'api_params': {...},
            'enrichment_params': {...},
            'voice_params': {...},
            'validation_params': {...}
        }
```

### Level 3: Generation Orchestration

```
Orchestrator (processing/orchestrator.py)
    ├→ __init__(dynamic_config: DynamicConfig, api_client, data_enricher, ...)
    │
    ├→ generate(topic, component_type, voice, length) -> ComponentResult
    │   │
    │   ├→ 1. Get all parameters from dynamic config (Phase 2)
    │   │   all_params = dynamic_config.get_all_generation_params(component_type)
    │   │   voice_params = all_params['voice_params']
    │   │   technical_intensity = all_params['enrichment_params']['technical_intensity']
    │   │
    │   ├→ 2. Fetch and enrich facts
    │   │   facts = data_enricher.fetch_real_facts(topic)
    │   │   facts_str = data_enricher.format_facts_for_prompt(facts, technical_intensity)
    │   │
    │   ├→ 3. Get voice profile
    │   │   voice_profile = voice_store.get_voice(author_id)
    │   │
    │   ├→ 4. Build prompt with voice parameters (Phase 2)
    │   │   prompt = PromptBuilder.build_unified_prompt(
    │   │       topic=topic,
    │   │       voice=voice_profile,
    │   │       facts=facts_str,
    │   │       component_type=component_type,
    │   │       voice_params=voice_params,  # NEW: Pass voice parameters
    │   │       length=length
    │   │   )
    │   │
    │   ├→ 5. Call API with dynamic params
    │   │   text = _call_api(prompt, component_type)
    │   │       ├→ temperature = dynamic_config.calculate_temperature(component_type)
    │   │       ├→ max_tokens = dynamic_config.calculate_max_tokens(component_type)
    │   │       └→ api_client.generate_simple(prompt, temperature, max_tokens)
    │   │
    │   ├→ 6. Validate AI detection
    │   │   detection = ai_detector.detect(text)
    │   │   threshold = dynamic_config.calculate_detection_threshold()
    │   │
    │   └→ 7. Validate readability
    │       readability = readability_validator.validate(text)
    │       thresholds = dynamic_config.calculate_readability_thresholds()
    │
    └→ _call_api(prompt, attempt, component_type) -> str
        ├→ Calculate dynamic temperature + tokens
        ├→ Call api_client.generate_simple()
        └→ Return content
```

### Level 4: Prompt Building

```
PromptBuilder (processing/generation/prompt_builder.py)
    └→ build_unified_prompt(topic, voice, length, facts, component_type, ...) -> str
        │
        ├→ 1. Get component spec
        │   spec = ComponentRegistry.get_spec(component_type)
        │
        ├→ 2. Extract voice characteristics
        │   country = voice['country']
        │   linguistic = voice['linguistic_characteristics']
        │   sentence_patterns = linguistic['sentence_structure']['patterns']
        │
        ├→ 3. Build context section
        │   - Topic + domain
        │   - Factual information (from DataEnricher)
        │   - Focus areas
        │
        ├→ 4. Build requirements section
        │   - Length range
        │   - Format rules
        │   - Style notes
        │
        ├→ 5. Build voice section
        │   - Author name + country
        │   - Regional patterns (ESL traits)
        │   - Sentence structure guidance
        │   - Formality balance
        │
        ├→ 6. Build anti-AI section
        │   anti_ai = _load_anti_ai_rules()  # From prompts/anti_ai_rules.txt
        │   (Fallback: embedded rules if file missing)
        │
        ├→ 7. Add component-specific hints
        │   (subtitle, troubleshooter, etc.)
        │
        └→ 8. Assemble final prompt
            context + requirements + voice + anti_ai + hints + variation_seed
```

### Level 5: Data Enrichment

```
DataEnricher (processing/enrichment/data_enricher.py)
    ├→ fetch_real_facts(topic) -> Dict
    │   Reads from Materials.yaml
    │   Returns: {
    │       'category': str,
    │       'properties': Dict,
    │       'machine_settings': Dict,
    │       'applications': List
    │   }
    │
    └→ format_facts_for_prompt(facts, technical_intensity: int) -> str
        │
        ├→ Determine spec density from technical_intensity
        │   0-30: max_props=2, max_settings=1, include_apps=False
        │   31-60: max_props=3, max_settings=2, include_apps=True
        │   61-100: max_props=5, max_settings=3, include_apps=True
        │
        ├→ Format properties (top N by importance)
        │   "Density: 2.7 g/cm³"
        │
        ├→ Format machine settings
        │   "Power: 200-400W"
        │
        ├→ Format applications (if include_apps)
        │   Truncate to 200 chars
        │
        └→ Return formatted string
```

### Level 6: API Client

```
APIClient (shared/api/unified_client.py)
    └→ generate_simple(prompt, system_prompt, max_tokens, temperature) -> APIResponse
        │
        ├→ Build request payload
        │   {
        │       "model": "grok-2-1212",
        │       "messages": [
        │           {"role": "system", "content": system_prompt},
        │           {"role": "user", "content": prompt}
        │       ],
        │       "max_tokens": max_tokens,    # ✅ FROM CONFIG
        │       "temperature": temperature   # ✅ FROM CONFIG
        │   }
        │
        ├→ Send HTTP POST to https://api.x.ai/v1/chat/completions
        │
        └→ Return APIResponse(success, content, error, metadata)
```

---

## 🔍 Critical Connection Points

### Connection 1: Config → Temperature

```python
# config.yaml
imperfection_tolerance: 80
sentence_rhythm_variation: 80
structural_predictability: 80

# IntensityManager
get_imperfection_tolerance() → 80
get_sentence_rhythm() → 80
get_structural_predictability() → 80

# DynamicConfig
calculate_temperature():
    creativity_factor = (80 + 80 + 80) / 300 = 0.8
    temp_adjustment = (0.8 - 0.5) * 0.4 = 0.12
    temperature = 0.8 + 0.12 = 0.92

# Orchestrator
_call_api():
    temperature = 0.92  # Calculated value

# API Client
generate_simple(temperature=0.92)  # ✅ SENT TO GROK
```

### Connection 2: Config → Fact Density

```python
# config.yaml
technical_language_intensity: 20

# IntensityManager
get_technical_language_intensity() → 20

# Orchestrator
technical_intensity = 20

# DataEnricher
format_facts_for_prompt(facts, technical_intensity=20):
    # 20 is in 0-30 range (minimal)
    max_props = 2
    max_settings = 1
    include_apps = False
    # Returns: "Density: 2.7 g/cm³\nThermal Conductivity: 237 W/m·K"

# PromptBuilder
build_unified_prompt(facts="Density: 2.7...\nThermal..."):
    # Embeds in prompt: "FACTUAL INFORMATION:\nDensity: 2.7..."

# API Client
generate_simple(prompt="...Density: 2.7...")  # ✅ SENT TO GROK
```

### Connection 3: Config → Voice Parameters (Phase 2 COMPLETE)

```python
# config.yaml
author_voice_intensity: 90
personality_intensity: 90
engagement_style: 90

# IntensityManager
get_author_voice() → 90
get_personality_intensity() → 90
get_engagement_style() → 90

# DynamicConfig
calculate_voice_parameters():
    return {
        'trait_frequency': 0.90,
        'opinion_rate': 0.90,
        'reader_address_rate': 0.90,
        'colloquialism_frequency': 0.70
    }

# Orchestrator (Phase 2)
all_params = dynamic_config.get_all_generation_params("subtitle")
voice_params = all_params['voice_params']

# PromptBuilder (Phase 2)
build_unified_prompt(voice_params=voice_params):
    # Voice intensity guidance
    if trait_frequency > 0.7:  # 0.90 > 0.7 ✅
        guidance += "Strong - emphasize author personality throughout"
    
    # Personality guidance section
    if opinion_rate > 0.5:  # 0.90 > 0.5 ✅
        guidance += "Include personal perspective (I find..., In my experience...)"
    if reader_address_rate > 0.5:  # 0.90 > 0.5 ✅
        guidance += "Address reader directly using 'you'"
    if colloquialism_frequency > 0.6:  # 0.70 > 0.6 ✅
        guidance += "Use informal language and colloquialisms"

# API Client
generate_simple(prompt="...Strong - emphasize author personality...\nPERSONALITY GUIDANCE:\n- Include personal perspective...")  # ✅ SENT TO GROK
```

---

## 🧪 Test Coverage Requirements

### Test 1: End-to-End Config Flow

```python
def test_config_reaches_api():
    """Verify config values reach API call"""
    # Set specific config values
    manager = IntensityManager()
    manager.config['imperfection_tolerance'] = 90
    manager.config['sentence_rhythm_variation'] = 90
    manager.config['structural_predictability'] = 90
    
    # Create dynamic config
    config = DynamicConfig(manager)
    
    # Verify temperature calculation
    temp = config.calculate_temperature('subtitle')
    assert 0.9 <= temp <= 1.0, f"High sliders should give high temp: {temp}"
    
    # Verify it flows through orchestrator
    orchestrator = Orchestrator(dynamic_config=config)
    # Mock API call and verify temperature parameter
    # ...
```

### Test 2: Technical Intensity Affects Output

```python
def test_technical_intensity_affects_facts():
    """Verify technical_language_intensity controls spec density"""
    enricher = DataEnricher()
    
    facts = {
        'properties': {
            'density': {'value': 2.7, 'unit': 'g/cm³'},
            'thermal': {'value': 237, 'unit': 'W/m·K'},
            'modulus': {'value': 70, 'unit': 'GPa'},
            'strength': {'value': 110, 'unit': 'MPa'},
            'melting': {'value': 660, 'unit': '°C'}
        }
    }
    
    # Low technical = 2 properties
    low_tech = enricher.format_facts_for_prompt(facts, technical_intensity=20)
    assert low_tech.count('\n') <= 2, "Should have 2 or fewer properties"
    
    # High technical = 5 properties
    high_tech = enricher.format_facts_for_prompt(facts, technical_intensity=90)
    assert high_tech.count('\n') >= 4, "Should have 5 properties"
```

### Test 3: Voice Parameters in Prompt (After Phase 1)

```python
def test_voice_params_in_prompt():
    """Verify voice params affect prompt content"""
    voice_profile = {...}
    
    # High personality = opinions
    high_personality = {
        'trait_frequency': 0.8,
        'opinion_rate': 0.9,  # High
        'reader_address_rate': 0.5,
        'colloquialism_frequency': 0.7
    }
    
    prompt = PromptBuilder.build_unified_prompt(
        topic="Aluminum",
        voice=voice_profile,
        voice_params=high_personality,
        ...
    )
    
    assert "personal perspective" in prompt.lower() or "opinion" in prompt.lower()
    
    # Low personality = no opinions
    low_personality = {'opinion_rate': 0.1, ...}
    prompt2 = PromptBuilder.build_unified_prompt(
        voice_params=low_personality, ...
    )
    
    assert "personal perspective" not in prompt2.lower()
```

### Test 4: No Silent Fallbacks

```python
def test_no_silent_fallbacks():
    """Verify system fails fast on missing config"""
    # Missing author_id should raise error
    store = VoiceStore()
    with pytest.raises(ValueError, match="Author ID 999 not found"):
        store.get_voice_profile(999)
    
    # Missing component length should raise error
    with pytest.raises(ValueError, match="Component type 'invalid'"):
        ComponentRegistry.get_length_range('invalid')
    
    # Missing length_variation_range should raise error
    config = {'component_lengths': {...}}  # Missing length_variation_range
    with pytest.raises(ValueError, match="length_variation_range"):
        ComponentRegistry.get_length_range('subtitle')
```

### Test 5: Anti-AI Rules from File

```python
def test_anti_ai_rules_from_file():
    """Verify anti-AI rules loaded from prompts/anti_ai_rules.txt"""
    # Should load from file
    rules = PromptBuilder._load_anti_ai_rules()
    assert "BANNED PHRASES" in rules
    assert "facilitates" in rules.lower()
    
    # File should exist
    assert os.path.exists('prompts/anti_ai_rules.txt')
    
    # Prompt should include rules
    prompt = PromptBuilder.build_unified_prompt(...)
    assert rules in prompt  # Exact rules from file
```

---

## 🚨 Breaking Change Detection

### Monitor These Files for Breaking Changes:

1. **IntensityManager Getters** (`processing/intensity/intensity_manager.py:75-140`)
   - If method signatures change, tests will fail
   - If return types change, dynamic_config will break

2. **DynamicConfig Calculators** (`processing/config/dynamic_config.py:50-400`)
   - If calculation formulas change, verify output ranges still valid
   - If parameter dependencies change, document new connections

3. **Orchestrator Flow** (`processing/orchestrator.py:80-180`)
   - If parameter passing changes, verify all components receive values
   - If new validation steps added, update method chain docs

4. **PromptBuilder Assembly** (`processing/generation/prompt_builder.py:50-280`)
   - If prompt structure changes, verify anti-AI rules still included
   - If voice section changes, verify voice_params consumed (after Phase 1)

5. **DataEnricher Logic** (`processing/enrichment/data_enricher.py:108-152`)
   - If fact selection changes, verify technical_intensity still controls density
   - If formatting changes, verify output structure remains consistent

---

## 📝 Update Checklist (For Future Changes)

When modifying the processing system:

- [ ] Update this method chain documentation
- [ ] Add/update tests for the modified component
- [ ] Verify end-to-end config flow still works
- [ ] Check for new silent fallbacks (run grep audit)
- [ ] Verify no hardcoded values introduced
- [ ] Test with extreme config values (0 and 100)
- [ ] Update `CONFIG_FLOW_AUDIT.md` if connection points change
- [ ] Run full test suite: `pytest processing/tests/`

---

## 🎯 Phase 1 Integration Points

After Phase 1 completion, these connections will exist:

```
Config → DynamicConfig.calculate_enrichment_params()
         ↓
Orchestrator → Passes enrichment_params to DataEnricher
                ↓
DataEnricher → Uses technical_intensity, context_detail_level, fact_formatting_style
                ↓
Prompt → Contains facts formatted per config
         ↓
API → Receives prompt with config-influenced content
```

```
Config → DynamicConfig.calculate_voice_parameters()
         ↓
Orchestrator → Passes voice_params to PromptBuilder
                ↓
PromptBuilder → Adjusts personality guidance per voice_params
                ↓
Prompt → Contains voice guidance per config
         ↓
API → Receives prompt with config-influenced personality
```

---

**Status**: Documentation complete, ready for Phase 1 implementation and test creation.
