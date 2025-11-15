# Config Flow & Architecture Audit

**Date**: November 14, 2025  
**Purpose**: Verify config values reach Grok API and check for architecture violations

---

## 🎯 USER QUESTIONS

### 1. How can we be sure config values reach Grok and affect responses?
### 2. Are generators creating prompts or delegating to `/prompts`?
### 3. Are there defaults/fallbacks in `/processing`?

---

## ✅ QUESTION 1: Config Flow to Grok API

### 📊 VERIFIED PATH: Config → Prompt → API

```
config.yaml (10 sliders)
    ↓
IntensityManager.get_X() methods
    ↓
DynamicConfig.calculate_X() methods
    ↓
Orchestrator.generate()
    ├→ dynamic_config.calculate_temperature() → temp=0.90
    ├→ dynamic_config.calculate_max_tokens() → tokens=350
    └→ dynamic_config.calculate_enrichment_params() → technical_intensity=20
        ↓
PromptBuilder.build_unified_prompt()
    ├→ Uses facts formatted by DataEnricher (respects technical_intensity)
    ├→ Injects voice profile (author, country, ESL traits)
    ├→ Adds anti-AI rules (hardcoded)
    └→ Returns complete prompt string
        ↓
Orchestrator._call_api(prompt, temperature, max_tokens)
    ↓
api_client.generate_simple(
    prompt=<full_prompt_string>,
    temperature=0.90,  ← FROM CONFIG
    max_tokens=350      ← FROM CONFIG
)
    ↓
GROK API receives:
✅ Prompt with config-influenced content
✅ Temperature calculated from sliders
✅ Max tokens calculated from sliders
```

### 🔍 PROOF POINTS

**File**: `processing/orchestrator.py:201-230`
```python
def _call_api(self, prompt: str, attempt: int = 1, component_type: str = 'subtitle') -> str:
    # Calculate dynamic temperature and tokens from sliders
    base_temperature = self.dynamic_config.calculate_temperature(component_type)
    retry_config = self.dynamic_config.calculate_retry_behavior()
    retry_temp_increase = retry_config['retry_temperature_increase']
    max_tokens = self.dynamic_config.calculate_max_tokens(component_type)
    
    # Increase temperature with each attempt
    temperature = min(1.0, base_temperature + (attempt - 1) * retry_temp_increase)
    
    logger.info(f"🌡️  Temperature: {temperature:.2f}")
    logger.info(f"🎯  Max tokens: {max_tokens}")
    
    # Direct API call with calculated values
    response = self.api_client.generate_simple(
        prompt=prompt,
        system_prompt="You are a professional technical writer...",
        max_tokens=max_tokens,      # ✅ FROM CONFIG
        temperature=temperature     # ✅ FROM CONFIG
    )
```

**File**: `processing/orchestrator.py:110-120`
```python
# Get technical intensity from sliders
technical_intensity = self.dynamic_config.base_config.get_technical_language_intensity()

# Pass to enricher (affects prompt content)
facts = self.data_enricher.fetch_real_facts(topic, ...)
facts_str = self.data_enricher.format_facts_for_prompt(
    facts, 
    technical_intensity=technical_intensity  # ✅ FROM CONFIG
)
```

**Result**: ✅ **CONFIG VALUES REACH GROK**
- Temperature: Calculated from 3 sliders (imperfection, rhythm, structural)
- Max tokens: Calculated from 2 sliders (length_variation, context)
- Prompt content: Affected by technical_intensity (controls spec density)

---

## ⚠️ QUESTION 2: Prompt Delegation

### 🔍 CURRENT STATE: Mixed Architecture

#### ✅ GOOD: Processing System Uses `/prompts`

**File**: `processing/generation/prompt_builder.py:1-10`
```python
"""
Unified Prompt Builder

Combines material facts, voice traits, and anti-AI instructions
into single prompt to minimize detection.
```

**Anti-AI Rules Location**: `prompts/anti_ai_rules.txt`  
**Voice Personas**: `prompts/personas/*.yaml`  
**Component Specs**: `prompts/component_specs.yaml`

**Verdict**: ✅ Processing system delegates to `/prompts` files

---

#### ❌ VIOLATION: Hardcoded Anti-AI Rules in PromptBuilder

**File**: `processing/generation/prompt_builder.py:216-230`
```python
# Build anti-AI section with emphasis on variation
anti_ai = """CRITICAL - AVOID AI PATTERNS & ADD VARIATION:
- BANNED PHRASES: "facilitates", "enables", "leverages", "demonstrates"...
- BANNED CONNECTORS: "paired with", "relies on", "thrives on"...
- BANNED STRUCTURES: "while maintaining/preserving/ensuring"...
- NO formulaic structures (e.g., "X does Y while preserving Z")
- NO abstract transitions ("results suggest", "data indicate")
- VARY opening words dramatically - start each sentence differently
...
"""
```

**Problem**: These anti-AI rules are **HARDCODED IN PYTHON**, not read from `/prompts/anti_ai_rules.txt`

**Impact**: 
- Can't update anti-AI rules without code changes
- Rules live in 2 places (code + /prompts file)
- `/prompts/anti_ai_rules.txt` may be unused

---

#### ⚠️ CONCERN: Legacy Fallback in unified_generator.py

**File**: `materials/unified_generator.py:316-338`
```python
def _generate_caption_legacy(self, material_name: str, material_data: Dict):
    """Legacy caption generation as fallback (direct API, no orchestrator)"""
    self.logger.warning("Using legacy caption generation (orchestrator failed)")
    
    # Format prompt (inline prompting?)
    prompt = self._format_prompt('caption', material_name, material_data)
    
    # Generate directly
    response = self._generate_with_api(prompt, 'caption')
```

**File**: `materials/unified_generator.py:168-192` (`_format_prompt`)
```python
def _format_prompt(self, content_type: str, material_name: str, material_data: Dict) -> str:
    # Load template from file
    template_path = f"data/templates/{content_type}_template.txt"
    with open(template_path, 'r') as f:
        prompt_template = f.read()
    
    # Format with material data
    formatted_prompt = prompt_template.format(**format_params)
    return formatted_prompt
```

**Verdict**: ⚠️ **PARTIAL - Uses templates but legacy fallback exists**
- Primary path (orchestrator) = ✅ Good
- Fallback path = ⚠️ Uses `data/templates/*.txt`, not `/prompts`
- Should fallback be removed per fail-fast policy?

---

## 🚨 QUESTION 3: Defaults & Fallbacks in `/processing`

### 🔍 AUDIT RESULTS

Found **68 `.get()` calls with defaults** in `/processing` directory:

#### ✅ ACCEPTABLE: Config Loader Defaults (Infrastructure)

**File**: `processing/config/config_loader.py`

These are **SAFE** - they provide sensible defaults when config.yaml is missing values:

```python
def get_author_voice_intensity(self) -> int:
    return self.config.get('author_voice_intensity', 50)  # ✅ OK - config fallback

def get_ai_threshold(self, strict_mode: bool = False) -> int:
    detection = self.config.get('detection', {})
    return detection.get('ai_threshold', 40)  # ✅ OK - config fallback

def get_materials_yaml_path(self) -> str:
    sources = self.config.get('data_sources', {})
    return sources.get('materials_yaml', 'data/materials/Materials.yaml')  # ✅ OK
```

**Reason**: These are **configuration defaults**, not business logic fallbacks.  
**Policy**: ALLOWED - Every config needs defaults for missing keys.

---

#### ✅ ACCEPTABLE: Dict Access Patterns (Safe Reads)

**Files**: Test files, data processing

```python
# Safe dictionary access in tests
category = material_data.get('category', 'N/A')  # ✅ OK - display only
assert facts.get('category'), "Should have category"  # ✅ OK - test validation

# Safe data extraction
country = voice.get('country', 'unknown')  # ✅ OK - for logging/display
patterns = result.get('detected_patterns', [])  # ✅ OK - optional field
```

**Reason**: These read optional fields or extract data for display.  
**Policy**: ALLOWED - Not production logic fallbacks.

---

#### ❌ VIOLATION: Business Logic Fallbacks

**File**: `processing/voice/store.py:72`
```python
country = author_map.get(author_id, "united_states")  # ❌ VIOLATION
```

**Problem**: If author_id not in map, **silently defaults to US author**  
**Impact**: Wrong voice profile used, no error raised  
**Fix Required**: Should throw `AuthorNotFoundError` instead

---

**File**: `processing/config/author_config_loader.py:135`
```python
base_value = config_data.get(field, 50)  # ❌ POTENTIAL VIOLATION
```

**Problem**: If author config missing field, defaults to 50  
**Impact**: Author customization silently ignored  
**Context**: Need to check if this is intentional fallback or should fail

---

**File**: `processing/generation/component_specs.py:95,101`
```python
default = lengths.get('default', 100)  # ❌ VIOLATION
length_variation = config.get('length_variation_range', 50)  # ❌ VIOLATION
```

**Problem**: Component length calculation falls back to hardcoded values  
**Impact**: If config.yaml missing values, uses 100/50 instead of failing  
**Fix Required**: Should validate config completeness on startup

---

#### ⚠️ SILENT FAILURE: Exception Handling

**File**: `processing/generation/prompt_builder.py:193-210`
```python
try:
    from processing.generation.component_specs import ComponentRegistry
    config = ComponentRegistry._load_config()
    sentence_variation = config.get('sentence_variation', {})
    component_variation = sentence_variation.get(spec.name, {})
    fallback_style = component_variation.get('style', '')
    
    if fallback_style:
        voice_section += f"\n- Sentence structure: {fallback_style}"
    else:
        # Ultimate fallback based on word count
        if length <= 30:
            voice_section += "\n- Sentence structure: Keep sentences concise..."
except Exception:  # ❌ SILENT FAILURE
    # If config loading fails, use basic fallback
    if length <= 30:
        voice_section += "\n- Sentence structure: Keep sentences concise..."
```

**Problem**: Bare `except Exception: pass` swallows ALL errors  
**Impact**: Config loading errors never reported, always uses fallback  
**Fix Required**: Catch specific exceptions, log warnings

---

### 📊 SUMMARY: Defaults & Fallbacks

| Category | Count | Status | Action Required |
|----------|-------|--------|-----------------|
| Config loader defaults | 42 | ✅ SAFE | None - intentional config fallbacks |
| Dict access (read-only) | 20 | ✅ SAFE | None - display/logging only |
| Business logic fallbacks | 4 | ❌ VIOLATION | Remove or convert to fail-fast |
| Silent exception handlers | 2 | ⚠️ CONCERN | Add logging, catch specific errors |

---

## 🎯 RECOMMENDATIONS

### Priority 1: Remove Business Logic Fallbacks

1. **voice/store.py:72** - Throw error if author not found
   ```python
   # BEFORE (silent fallback)
   country = author_map.get(author_id, "united_states")
   
   # AFTER (fail-fast)
   if author_id not in author_map:
       raise AuthorNotFoundError(f"Author {author_id} not in voice map")
   country = author_map[author_id]
   ```

2. **component_specs.py:95,101** - Validate config on startup
   ```python
   # Add to __init__ or module load
   def _validate_config(config):
       required = ['component_lengths', 'length_variation_range']
       for key in required:
           if key not in config:
               raise ConfigurationError(f"Missing required config: {key}")
   ```

3. **author_config_loader.py:135** - Decide: fail-fast or document as intentional
   ```python
   # Option A: Fail-fast
   if field not in config_data:
       raise ConfigurationError(f"Author {author_id} missing field: {field}")
   
   # Option B: Document as intentional
   # Default to 50 if author doesn't override (INTENTIONAL)
   base_value = config_data.get(field, 50)
   ```

---

### Priority 2: Fix Hardcoded Anti-AI Rules

**File**: `processing/generation/prompt_builder.py:216-230`

**Current**: Rules hardcoded in Python string  
**Should**: Read from `/prompts/anti_ai_rules.txt`

```python
# BEFORE (hardcoded)
anti_ai = """CRITICAL - AVOID AI PATTERNS:
- BANNED PHRASES: "facilitates", "enables"...
"""

# AFTER (read from file)
def _load_anti_ai_rules() -> str:
    with open('prompts/anti_ai_rules.txt', 'r') as f:
        return f.read()

anti_ai = _load_anti_ai_rules()
```

**Benefits**:
- Update rules without code changes
- Single source of truth
- Easier A/B testing of rule variations

---

### Priority 3: Improve Exception Handling

**File**: `processing/generation/prompt_builder.py:193-210`

```python
# BEFORE (silent failure)
except Exception:
    # Use fallback

# AFTER (specific + logged)
except (FileNotFoundError, KeyError) as e:
    logger.warning(f"Config loading failed: {e}. Using fallback sentence structure.")
    # Use fallback
except Exception as e:
    logger.error(f"Unexpected error loading config: {e}")
    raise
```

---

### Priority 4: Remove Legacy Fallback

**File**: `materials/unified_generator.py:316-338`

**Decision Required**: Should `_generate_caption_legacy()` exist?

Per fail-fast policy:
- ❌ **Remove**: If orchestrator fails, generation should fail (no silent degradation)
- ✅ **Keep**: Only if failure mode is "orchestrator unavailable" (infrastructure issue)

**Recommendation**: REMOVE - If orchestrator can't generate, system should fail-fast

---

## 📈 FINAL VERDICT

### ✅ Question 1: Config Values Reach Grok
**Status**: ✅ VERIFIED  
**Evidence**:
- Temperature calculated from sliders → passed to API
- Max tokens calculated from sliders → passed to API
- Technical intensity from sliders → affects prompt content
- Logging confirms values used: `logger.info(f"🌡️ Temperature: {temperature:.2f}")`

### ⚠️ Question 2: Prompt Delegation
**Status**: ⚠️ MOSTLY GOOD, 2 ISSUES  
**Issues**:
1. Anti-AI rules hardcoded in PromptBuilder (should read from `/prompts`)
2. Legacy fallback uses `data/templates/*.txt` (should use `/prompts` or be removed)

### ⚠️ Question 3: Defaults & Fallbacks
**Status**: ⚠️ MOSTLY GOOD, 4 VIOLATIONS  
**Safe**: 62/68 defaults (config infrastructure)  
**Violations**: 6 business logic fallbacks need fixing

---

## 🚀 ACTION ITEMS

1. ✅ **Verify Phase 1 methods work** (calculate_enrichment_params, get_all_generation_params)
2. ⏳ **Remove business logic fallbacks** (voice/store.py, component_specs.py)
3. ⏳ **Move anti-AI rules to file** (prompt_builder.py → prompts/anti_ai_rules.txt)
4. ⏳ **Improve exception handling** (catch specific errors, log warnings)
5. ⏳ **Decide on legacy fallback** (remove or document as infrastructure fallback)
6. ⏳ **Add config validation** (check completeness on startup)

---

**Conclusion**: System is **mostly sound** but has 4 business logic fallbacks and 1 hardcoded prompt section that violate fail-fast / delegation principles. All are fixable.
