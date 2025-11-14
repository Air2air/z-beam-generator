# Voice and Detection Architecture Inventory
**Generated**: 2025-11-13  
**Status**: Comprehensive audit of all voice and detection methods

---

## 🎯 Executive Summary

### Current State
- ✅ **Voice enhancement working** with Option 2 (signature_phrases optional)
- ✅ **Forbidden phrases blocked** in voice_base.yaml (20+ ai_detection_triggers)
- ✅ **Anti-AI requirements defined** in component_config.yaml
- ❌ **Anti-AI requirements NOT REACHING generation** - all subtitles follow forbidden formula
- ❌ **100% AI detection failure** - uniform structure despite variation rules

### Root Cause
**TextPromptBuilder bypasses component_config.yaml anti_ai_requirements**

The subtitle generation script uses `TextPromptBuilder`, which has **hardcoded examples** and does NOT read the anti-AI variation rules from `component_config.yaml`.

---

## 📚 Complete Architecture Map

### 1. Subtitle Generation Flow (Current)

```
scripts/regenerate_subtitles.py
    ↓
generate_subtitle() 
    ↓
[CHOICE POINT - Line 127]
    ↓
VoiceOrchestrator.generate_prompt() ← INTENDED PATH (includes all configs)
    |
    | Currently uses:
    ↓
TextPromptBuilder.build_prompt() ← ACTUAL PATH (bypasses anti-AI rules)
    ↓
API generate_simple()
    ↓
Return subtitle
    ↓
[NO POST-PROCESSING]
```

### 2. File Inventory

#### A. Voice Configuration Files

| File | Purpose | Status | Used By |
|------|---------|--------|---------|
| `shared/voice/base/voice_base.yaml` | Base voice principles, forbidden patterns | ✅ WORKING | VoiceOrchestrator |
| `shared/voice/component_config.yaml` | Component-specific rules including anti_ai_requirements | ❌ BYPASSED | VoiceOrchestrator only |
| `shared/voice/profiles/taiwan.yaml` | Taiwan author voice profile | ✅ WORKING | VoiceOrchestrator |
| `shared/voice/profiles/italy.yaml` | Italy author voice profile | ✅ WORKING | VoiceOrchestrator |
| `shared/voice/profiles/indonesia.yaml` | Indonesia author voice profile | ✅ WORKING | VoiceOrchestrator |
| `shared/voice/profiles/united_states.yaml` | USA author voice profile | ✅ WORKING | VoiceOrchestrator |

#### B. Voice Processing Code

| File | Purpose | Status | Integration |
|------|---------|--------|-------------|
| `shared/voice/orchestrator.py` | Comprehensive prompt builder with all configs | ✅ FUNCTIONAL | Available but not used for subtitles |
| `shared/voice/post_processor.py` | Voice enhancement after generation | ✅ FUNCTIONAL | Not called by regenerate_subtitles.py |
| `shared/prompts/text_prompt_builder.py` | Simplified prompt builder | ⚠️ PARTIAL | Used by regenerate_subtitles.py but lacks anti-AI rules |

#### C. Detection & Validation

| File | Purpose | Status |
|------|---------|--------|
| `shared/voice/ai_detection_patterns.txt` | Pattern-based AI detection | ✅ Modified (results_patterns removed) |
| `components/text/utils/voice_controller.py` | Official validation controller | ✅ FUNCTIONAL |

#### D. Scripts

| File | Purpose | Current Behavior |
|------|---------|------------------|
| `scripts/regenerate_subtitles.py` | Regenerate all material subtitles | Uses TextPromptBuilder (bypasses anti-AI rules) |

---

## 🔍 Critical Bypass Identified

### The Problem: TextPromptBuilder Hardcoded Examples

**File**: `shared/prompts/text_prompt_builder.py`  
**Lines**: 28-64

```python
COMPONENT_CONFIGS = {
    "subtitle": {
        "length": "12-16 words",
        "tone": "Accessible and engaging (voice added by postprocessor)",
        "examples": {
            "excellent": [
                "Laser cleaning removes rust and contaminants from Copper while preserving its conductivity",
                "Gentle laser pulses restore Bronze surfaces and protect the original patina",
                "Controlled laser treatment cleans Marble without causing cracks or surface damage to the stone",
                "Short laser pulses remove old coatings from Glass and maintain the surface clarity",
                "Laser cleaning provides a way to restore Oak's natural grain without causing charring or burning",
                "Pulsed lasers remove dirt from Granite surfaces while preserving the stone's original texture"
            ],
            ...
```

### The Evidence

**ALL 6 hardcoded examples follow the FORBIDDEN FORMULA:**
- "Laser cleaning [verb] [material] while [benefit]"
- "Gentle laser pulses [verb] [material] and [benefit]"
- "[Verb phrase] [material] without [damage]"

**This is EXACTLY what component_config.yaml tells us to avoid:**

```yaml
anti_ai_requirements:
  - "NEVER use formula: 'Laser cleaning [verb] [material] while [benefit]'"
  - "VARY sentence structure: Start with material name sometimes, action sometimes, benefit sometimes"
  - "MIX sentence types: statements, commands (implied subject), descriptive phrases"
```

### Why It Happens

1. **regenerate_subtitles.py** calls `TextPromptBuilder.build_prompt()` (line 127)
2. **TextPromptBuilder** has hardcoded examples with forbidden formula
3. **component_config.yaml** anti_ai_requirements are NEVER READ by TextPromptBuilder
4. **Result**: API copies the forbidden pattern from examples
5. **Outcome**: All 10 subtitles follow identical structure → 100% AI detection

---

## ✅ What IS Working

### 1. Voice Enhancement (Option 2)
**File**: `shared/voice/post_processor.py`  
**Status**: ✅ FUNCTIONAL

```python
# Line 647: signature_phrases optional
voice_indicators = voice.get_signature_phrases() or []  # Empty list is OK

# Lines 657-659: Enhancement proceeds without signature_phrases
# Comment: "Voice indicators optional - use full profile not just signature phrases"
```

**Evidence**: Testing showed voice enhancement working, generating different subtitles (though all with same structure).

### 2. Forbidden Phrase Blocking
**File**: `shared/voice/base/voice_base.yaml`  
**Lines**: 198-213  
**Status**: ✅ FUNCTIONAL

```yaml
ai_detection_triggers:
  avoid: [
    "Results suggest", "Data indicate", "Analysis shows", "Testing shows",
    "Measurements show", "Observations reveal", "Scans demonstrate",
    "Inspection shows", "Process achieves", "Treatment provides", ...
  ]
  reason: "Abstract subject + reporting verb = AI signature"
  correct: "Ra drops to 0.8 μm (NOT: Measurements show Ra drops to 0.8 μm)"
```

**Evidence**: Test output showed ZERO forbidden transitional phrases in all 10 subtitles.

### 3. Dual Detection System
**File**: `shared/voice/post_processor.py`  
**Status**: ✅ FUNCTIONAL

- Pre-enhancement check (line ~850)
- Post-enhancement check (line ~920)
- AI degradation detection (line ~935)
- Quality score validation
- Pattern matching with configurable thresholds

### 4. VoiceOrchestrator (Unused)
**File**: `shared/voice/orchestrator.py`  
**Method**: `generate_prompt()`  
**Status**: ✅ FUNCTIONAL but NOT USED for subtitles

The method has this comment:
```python
# Build layered prompt for subtitle/tagline
elif component_type == 'subtitle':
    # DEPRECATED: Use shared.prompts.text_prompt_builder.TextPromptBuilder instead
    # This legacy method is kept for backwards compatibility only
    return self._build_subtitle_prompt_legacy(...)
```

**This is the bypass** - VoiceOrchestrator was intentionally deprecated for subtitles in favor of TextPromptBuilder.

---

## ❌ What IS NOT Working

### 1. Anti-AI Variation Rules
**File**: `shared/voice/component_config.yaml`  
**Lines**: 83-96  
**Status**: ❌ BYPASSED

The rules exist but are NEVER read by TextPromptBuilder:

```yaml
anti_ai_requirements:
  - "NEVER use formula: 'Laser cleaning [verb] [material] while [benefit]'"
  - "VARY sentence structure: Start with material name sometimes, action sometimes, benefit sometimes"
  - "MIX sentence types: statements, commands (implied subject), descriptive phrases"
  - "USE different verbs: revive, restore, preserve, protect, renew, refresh, maintain, safeguard"
  - "AVOID repetitive 'while' clauses - use different connectors or no connector"
  - "Examples of varied structures:"
  - "  - 'Gentle precision removes [X] from [material]'"
  - "  - '[Material] stays intact during contaminant removal'"
  - "  - 'Preserve [material] character without harsh chemicals'"
  - "  - 'Remove buildup, keep structural integrity'"
  - "  - '[Material] cleaning without thermal damage'"
```

**Evidence**: All 10 test subtitles follow "Laser cleaning [verb] [material] while [benefit]" pattern.

### 2. Voice Post-Processing for Subtitles
**File**: `shared/voice/post_processor.py`  
**Status**: ✅ FUNCTIONAL but NOT CALLED

The script doesn't use VoicePostProcessor for subtitles:

```python
# scripts/regenerate_subtitles.py line 148
def generate_subtitle(...):
    # ... generates subtitle using VoiceOrchestrator ...
    
    # NOTE: VoicePostProcessor NOT called here
    # Subtitle returned directly from API without enhancement
    return subtitle
```

**Why**: Subtitles are short (12-16 words), post-processing designed for longer text (100+ words).

---

## 🔧 Architecture Components Detail

### VoiceOrchestrator.generate_prompt()

**Purpose**: Comprehensive prompt builder that layers:
1. Base voice principles (voice_base.yaml)
2. Country-specific linguistic patterns (profiles/*.yaml)
3. Component-specific rules (component_config.yaml)
4. Material context

**For subtitles** (deprecated path):
```python
def _build_subtitle_prompt_legacy(self, base_voice, country_profile, material_context, author, **kwargs):
    # Get component-specific configuration
    config = self.get_component_config('subtitle')  # ← READS component_config.yaml
    
    # Get anti-AI requirements
    material_specificity = self.component_config.get('material_specificity_requirement', '')
    
    # ... builds full prompt with all layers ...
```

**Status**: ✅ Would include anti_ai_requirements IF USED

### TextPromptBuilder.build_prompt()

**Purpose**: Simplified prompt builder for quick generation

**Current implementation**:
```python
def build_prompt(self, component_type, material_name, category, ...):
    # Get component configuration
    config = self.component_configs.get(component_type)  # ← HARDCODED DICT
    
    # NO READING of component_config.yaml
    # NO READING of voice_base.yaml
    # NO READING of anti_ai_requirements
    
    # Uses hardcoded examples that follow FORBIDDEN formula
```

**Status**: ❌ Bypasses entire configuration system

### VoicePostProcessor.enhance()

**Purpose**: Add author-specific voice markers after generation

**Flow**:
```python
def enhance(self, content, voice, component_type='caption', max_attempts=3):
    # Pre-enhancement check
    pre_check = self.ai_detector.is_ai_generated(original_text)
    
    # Apply voice markers (signature phrases, linguistic patterns)
    enhanced_text = self._apply_voice_markers(...)
    
    # Post-enhancement check
    post_check = self.ai_detector.is_ai_generated(enhanced_text)
    
    # AI degradation detection
    if post_check.ai_score > pre_check.ai_score + 10:
        # Voice enhancement made it MORE AI-like
        # Retry with different approach
    
    # Quality validation
    quality_score = self._calculate_quality_score(...)
    
    return ComponentResult(success=True, content=enhanced_text, ...)
```

**Status**: ✅ FUNCTIONAL but not used for subtitles

---

## 📊 Test Results Analysis

### Test Command
```bash
python3 scripts/regenerate_subtitles.py --test
```

### Output Pattern (All 10 Materials)

```
Laser cleaning removes [X] from [material] while preserving [Y]
Laser cleaning restores [X] on [material] while maintaining [Y]
Laser cleaning eliminates [X] from [material] while protecting [Y]
...
```

### AI Detection Results
- **External detector** (phrasely.ai): 100% AI detection
- **Pattern**: All subtitles follow identical structure
- **Forbidden phrases**: Zero (successfully blocked)
- **Structural variation**: Zero (failed - all same pattern)

### Why 100% Detection Despite Zero Forbidden Phrases

AI detectors identify:
1. ✅ **Abstract transitional phrases** (we blocked these successfully)
2. ❌ **Uniform structural patterns** (we failed to vary structure)
3. ❌ **Predictable formula application** (examples taught AI the wrong pattern)

**The uniform "Laser cleaning [verb] [material] while [benefit]" structure is itself an AI signature**, even without forbidden transitional phrases.

---

## 🎯 Solutions (No Unauthorized Changes)

### Option A: Update TextPromptBuilder to Read component_config.yaml

**Pros**:
- Minimal change to existing architecture
- Preserves simplified builder pattern
- Adds anti-AI rules to current flow

**Cons**:
- TextPromptBuilder will become more complex
- Duplicates some VoiceOrchestrator logic
- May need to add YAML reading capability

**Implementation**:
```python
class TextPromptBuilder:
    def __init__(self):
        self.component_configs = COMPONENT_CONFIGS
        self.component_config_yaml = self._load_component_config()  # NEW
    
    def _load_component_config(self):
        # Read component_config.yaml
        config_path = Path(__file__).parent.parent / "voice" / "component_config.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def build_prompt(self, component_type, ...):
        # ... existing code ...
        
        # ADD: Read anti_ai_requirements from YAML
        config_yaml = self.component_config_yaml.get(component_type, {})
        anti_ai_reqs = config_yaml.get('anti_ai_requirements', [])
        
        if anti_ai_reqs:
            prompt_parts.append("CRITICAL ANTI-AI REQUIREMENTS:\n" + "\n".join(anti_ai_reqs))
        
        # ... rest of prompt ...
```

### Option B: Switch to VoiceOrchestrator for Subtitles

**Pros**:
- Uses comprehensive existing infrastructure
- Already reads component_config.yaml
- Includes all voice layers
- Maintains single source of truth

**Cons**:
- Requires updating regenerate_subtitles.py
- Reverses previous deprecation decision
- More complex prompt generation

**Implementation**:
```python
# scripts/regenerate_subtitles.py line 127
def generate_subtitle(...):
    # CHANGE FROM:
    # prompt = builder.build_prompt(...)
    
    # CHANGE TO:
    prompt = voice.generate_prompt(
        component_type='subtitle',
        material_context={...},
        author=author_info
    )
    
    # Rest remains same
```

### Option C: Add Post-Processing for Subtitles

**Pros**:
- Keeps current generation flow
- Adds variation in post-processing
- Can mix structural patterns after generation

**Cons**:
- Post-processing designed for longer text
- May be overkill for 12-16 word subtitles
- Doesn't fix root cause (bad examples in prompt)

---

## 📋 Recommendations

### Immediate Actions (No Code Changes)

1. **USER DECISION REQUIRED**: Which solution?
   - Option A: Update TextPromptBuilder (minimal change)
   - Option B: Switch to VoiceOrchestrator (comprehensive)
   - Option C: Add post-processing (band-aid)

2. **Document the bypass** for future reference

3. **Update hardcoded examples** in TextPromptBuilder to match anti-AI requirements

### Medium-Term Actions

1. **Consolidate prompt builders** - maintain single source of truth
2. **Add integration tests** to verify component_config.yaml is used
3. **Monitor AI detection scores** after changes

### Long-Term Considerations

1. **Architectural decision**: Should TextPromptBuilder exist separately from VoiceOrchestrator?
2. **Configuration consolidation**: Should all text generation use VoiceOrchestrator?
3. **Testing infrastructure**: Add automated AI detection to CI/CD

---

## 🚨 Critical Findings Summary

| Finding | Impact | Status |
|---------|--------|--------|
| TextPromptBuilder bypasses component_config.yaml | HIGH | ❌ Active bypass |
| Hardcoded examples follow forbidden formula | HIGH | ❌ Teaching wrong pattern |
| Anti-AI requirements not reaching generation | HIGH | ❌ Rules ineffective |
| Voice enhancement working with Option 2 | LOW | ✅ Fixed |
| Forbidden phrases successfully blocked | LOW | ✅ Working |
| Dual detection system functional | LOW | ✅ Working |
| VoiceOrchestrator deprecated for subtitles | MEDIUM | ⚠️ Design decision |

---

## 📖 Related Documentation

- `components/text/docs/README.md` - Text component architecture
- `components/text/docs/CONTENT_GENERATION_ARCHITECTURE.md` - Generation flow
- `components/text/docs/PROMPT_SYSTEM.md` - Prompt layering system
- `shared/voice/component_config.yaml` - Component configurations
- `shared/voice/base/voice_base.yaml` - Base voice principles

---

## 🎯 Next Steps

1. **User**: Review this inventory and choose solution (A, B, or C)
2. **Agent**: Implement chosen solution with minimal, surgical changes
3. **Test**: Regenerate 10 test subtitles and verify structural variation
4. **Validate**: Run phrasely.ai detection on new output
5. **Deploy**: Apply to all 132 materials if successful

---

**END OF INVENTORY**
