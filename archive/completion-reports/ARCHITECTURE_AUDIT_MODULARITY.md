# Architecture Audit: Separation of Concerns & Modularity

**Date**: October 29, 2025  
**Scope**: End-to-end system evaluation for reusability and separation of concerns  
**Status**: ✅ Analysis Complete - Action Items Identified

---

## Executive Summary

**Overall Assessment**: 🟡 **GOOD with Improvement Opportunities**

The system demonstrates strong separation of concerns in the **voice system** following the recent FAQ variation fix, but several components still contain hardcoded language patterns and duplicated logic. This audit identifies opportunities to apply the same modularity principles system-wide.

### Key Findings

| Component | Separation of Concerns | Reusability | Action Needed |
|-----------|----------------------|-------------|---------------|
| Voice System (VoiceOrchestrator) | ✅ Excellent | ✅ High | None - reference implementation |
| FAQ Generator | ✅ Good | ✅ Good | ✅ Complete (recent fix) |
| Caption Generator | ⚠️ Fair | ⚠️ Medium | Yes - extract prompts |
| Subtitle Generator | ⚠️ Fair | ⚠️ Medium | Yes - extract prompts |
| Frontmatter Generator | ❌ Poor | ❌ Low | **URGENT - major refactor needed** |

---

## 1. Voice System (Reference Architecture) ✅

**Status**: **EXCELLENT** - Gold standard for other components

### What's Working Well

1. **Complete Separation**: All language patterns in `voice/profiles/*.yaml`
2. **Single Source of Truth**: VoiceOrchestrator manages all voice logic
3. **Reusable API**: `get_faq_variation_guidance()`, `get_unified_prompt()`, etc.
4. **No Hardcoded Patterns**: Zero language patterns in Python code
5. **Extensible**: New countries/components just need YAML updates

### Architecture Pattern

```
Component Generator
        ↓
VoiceOrchestrator.get_faq_variation_guidance(author)
        ↓
voice/profiles/{country}.yaml
        ↓
voice_adaptation.faq_generation.critical_variation_requirements
        ↓
Formatted guidance string → AI prompt
```

### Key Success Factors

- **Data-driven**: All prompts come from YAML
- **Centralized**: One place to update voice behavior
- **Fail-fast**: Missing profiles cause immediate errors
- **Documented**: Clear architecture guides

---

## 2. FAQ Generator ✅

**Status**: **GOOD** - Recently refactored to use voice system

### Strengths

- ✅ Uses `VoiceOrchestrator.get_faq_variation_guidance()`
- ✅ Removed ~80 lines of hardcoded variation rules
- ✅ Language patterns delegated to voice profiles
- ✅ Clean separation between generation logic and voice

### Remaining Opportunities

**Issue**: Still has embedded prompt templates in Python
```python
# components/faq/generators/faq_generator.py:85-122
def build_research_prompt(self, material_name: str, technical_intensity: int = 3) -> str:
    """Build research prompt for Step 1: Material research."""
    technical_guidance = self._get_technical_guidance(technical_intensity)
    
    return f"""You are an expert in laser cleaning technologies...
    
STEP 1: Research the Subject Material and Its Uses
...
"""  # ~50 lines of hardcoded prompt text
```

**Recommendation**: Extract to `prompts/faq_research.yaml` or integrate with voice system

---

## 3. Caption Generator ⚠️

**Status**: **FAIR** - Basic voice integration but hardcoded prompts

### Current Issues

#### Issue 1: Hardcoded Prompt Templates
**Location**: `components/caption/generators/generator.py:82-148`
```python
def _build_caption_prompt(self, material_name, material_data, ...):
    prompt = f"""Generate microscopy image captions for laser cleaning of {material_name}.

CONTEXT:
{context}

Generate TWO captions:

**BEFORE_TEXT:**
Describe the contaminated surface BEFORE laser cleaning.
- Focus on: contaminant type, surface degradation, visible damage
- Word count: {target_words_before} words...
"""  # ~60 lines of hardcoded instructions
```

**Problem**: Content-specific instructions mixed with prompt construction

#### Issue 2: Duplicate Prompt Logic
Similar prompt construction exists in `components/frontmatter/core/streamlined_generator.py:2240-2350`

### Recommendations

1. **Extract Prompt Templates** to `prompts/caption_base.yaml`:
   ```yaml
   role: "Generate microscopy image captions for laser cleaning"
   
   sections:
     before:
       focus:
         - "contaminant type"
         - "surface degradation"
         - "visible damage"
       style: "technical, descriptive tone"
       structure: "single paragraph"
     
     after:
       focus:
         - "restoration quality"
         - "surface condition"
         - "material integrity"
       style: "technical, descriptive tone"
       structure: "single paragraph"
   
   requirements:
     - "Use precise microscopy terminology"
     - "Describe visual characteristics clearly"
     - "Target audience: engineers and technical professionals"
   ```

2. **Use VoiceOrchestrator** for voice-specific instructions:
   ```python
   orchestrator = VoiceOrchestrator(author['country'])
   base_prompt = load_yaml('prompts/caption_base.yaml')
   voice_instructions = orchestrator.get_caption_voice_instructions()
   prompt = format_prompt(base_prompt, voice_instructions, material_context)
   ```

3. **Consolidate**: Remove duplicate logic from frontmatter generator

---

## 4. Subtitle Generator ⚠️

**Status**: **FAIR** - Similar issues to Caption generator

### Current Issues

**Hardcoded Prompts**: `components/subtitle/core/subtitle_generator.py:72-150`
```python
def _build_subtitle_prompt(self, material_name, material_data, target_words):
    prompt = f"""Generate an engaging subtitle for laser cleaning of {material_name}.

CONTEXT:
{context}

REQUIREMENTS:
- Length: EXACTLY {target_words} words
- Style: Technical yet engaging
- Focus: Material-specific treatment benefit
...
"""  # ~70 lines hardcoded
```

### Recommendations

1. **Extract to YAML**: Create `prompts/subtitle_base.yaml`
2. **Use Voice System**: Integrate with `VoiceOrchestrator.get_subtitle_voice_instructions()`
3. **Consolidate Word Count Logic**: Move to voice/base/content_requirements.yaml

---

## 5. Frontmatter Generator ❌

**Status**: **POOR** - URGENT refactor needed

### Critical Issues

#### Issue 1: Hardcoded Voice Profiles
**Location**: `components/frontmatter/core/streamlined_generator.py:1396-1455`
```python
def _get_author_voice_profile(self, author_info: Dict) -> Dict:
    """Extract voice profile from author information."""
    # DUPLICATE voice profiles hardcoded in Python!
    voice_profiles = {
        'Taiwan': {
            'country': 'Taiwan',
            'linguistic_characteristics': {
                'sentence_structure': {
                    'patterns': ['systematic', 'logical', 'formal'],
                    'connectors': ['Furthermore', 'Therefore', ...]
                }
            }
        },
        'Italy': {...},  # Duplicate of voice/profiles/italy.yaml
        'Indonesia': {...},  # Duplicate of voice/profiles/indonesia.yaml
    }
```

**Problem**: ❌❌❌ **CRITICAL VIOLATION** - Voice profiles duplicated instead of using VoiceOrchestrator

#### Issue 2: Voice Transformation Logic
**Location**: `components/frontmatter/core/streamlined_generator.py:1558-1650`
```python
def _voice_transform_text(self, text: str, voice_profile: Dict) -> str:
    """Transform descriptive text to match author voice."""
    # 90+ lines of manual voice transformation logic
    # Taiwan: Add systematic connectors
    if 'systematic' in tendencies_text:
        text = self._add_systematic_connectors(text)
    # Italy: Add descriptive flourishes
    elif 'descriptive' in tendencies_text:
        text = self._add_italian_descriptors(text)
    ...
```

**Problem**: Manual text transformation should use VoicePostProcessor or be part of generation

#### Issue 3: Duplicate Generation Logic
**Location**: `components/frontmatter/core/streamlined_generator.py:2240-2350`
```python
def _generate_subtitle(self, material_name, category, subcategory, material_data):
    """Generate AI-powered subtitle..."""
    # Duplicates SubtitleComponentGenerator logic (~100 lines)
    # Loads voice profile manually (should use VoiceOrchestrator)
    voice_file = Path(f"voice/profiles/{profile_name}.yaml")
    with open(voice_file, 'r') as f:
        voice_profile = yaml.safe_load(f)
    ...
```

**Problem**: Duplicates subtitle generator + voice system functionality

### Recommendations for Frontmatter Generator

**URGENT Priority 1**: Remove Duplicate Voice Profiles
```python
# WRONG - Current approach
def _get_author_voice_profile(self, author_info: Dict) -> Dict:
    voice_profiles = {'Taiwan': {...}, 'Italy': {...}}  # HARDCODED DUPLICATION
    return voice_profiles.get(country, default)

# RIGHT - Use VoiceOrchestrator
def _get_author_voice_profile(self, author_info: Dict) -> Dict:
    from voice.orchestrator import VoiceOrchestrator
    country = author_info.get('author', {}).get('country', 'United States')
    orchestrator = VoiceOrchestrator(country)
    return orchestrator.profile  # Access validated profile
```

**Priority 2**: Remove Manual Voice Transformation
```python
# WRONG - Manual transformation
def _voice_transform_text(self, text, voice_profile):
    if 'systematic' in patterns:
        text = self._add_systematic_connectors(text)  # Manual manipulation

# RIGHT - Generate with voice from start
def _generate_text_with_voice(self, material_data, author):
    orchestrator = VoiceOrchestrator(author['country'])
    prompt = orchestrator.get_unified_prompt('text', material_data, author)
    return api_client.generate(prompt)  # Voice baked in from generation
```

**Priority 3**: Use Component Generators
```python
# WRONG - Duplicate subtitle logic
def _generate_subtitle(self, ...):
    # 100 lines of subtitle generation code

# RIGHT - Use SubtitleComponentGenerator
from components.subtitle.core.subtitle_generator import SubtitleComponentGenerator
subtitle_gen = SubtitleComponentGenerator()
result = subtitle_gen.generate(material_name, material_data, api_client, author)
```

---

## 6. System-Wide Patterns

### What Works (Apply Everywhere)

1. **Voice Orchestrator Pattern**: ✅ Central API for all voice logic
2. **YAML-Driven Config**: ✅ All content rules in YAML, not Python
3. **Fail-Fast Validation**: ✅ Required profiles, no silent degradation
4. **Component Generators**: ✅ Single responsibility, clear interfaces

### What Needs Fixing

1. **Hardcoded Prompts**: ⚠️ Extract to YAML templates
2. **Duplicate Voice Logic**: ❌ Use VoiceOrchestrator everywhere
3. **Manual Voice Transformation**: ❌ Generate with voice from start
4. **Component Duplication**: ❌ Reuse component generators

---

## Action Plan

### Phase 1: Critical Fixes (Week 1) 🔥

**Priority**: Fix frontmatter generator architectural violations

- [ ] **Remove hardcoded voice profiles** from `streamlined_generator.py`
  - Replace `_get_author_voice_profile()` with VoiceOrchestrator
  - Delete 60+ lines of duplicate voice data
  
- [ ] **Remove manual voice transformation**
  - Delete `_voice_transform_text()` method
  - Generate content with voice from start using orchestrator
  
- [ ] **Remove duplicate subtitle generation**
  - Delete `_generate_subtitle()` method
  - Use `SubtitleComponentGenerator` directly

**Estimated Impact**: 
- Remove ~200 lines of duplicate code
- Eliminate 4 maintenance points (voice profiles)
- Achieve single source of truth for voice

### Phase 2: Prompt Extraction (Week 2)

**Priority**: Extract hardcoded prompts to YAML

- [ ] **Caption prompts** → `prompts/caption_base.yaml`
- [ ] **Subtitle prompts** → `prompts/subtitle_base.yaml`
- [ ] **FAQ prompts** → `prompts/faq_research.yaml`, `faq_aspects.yaml`, `faq_questions.yaml`

**Estimated Impact**:
- Remove ~300 lines of prompt strings from Python
- Enable non-developer prompt tuning
- Consistent prompt structure across components

### Phase 3: Voice Integration (Week 3)

**Priority**: Integrate all generators with VoiceOrchestrator

- [ ] **Caption**: Use `orchestrator.get_caption_voice_instructions()`
- [ ] **Subtitle**: Use `orchestrator.get_subtitle_voice_instructions()`
- [ ] **Enhance orchestrator** with missing methods

**Estimated Impact**:
- Consistent voice application
- Easier to add new voice requirements
- Better separation of concerns

### Phase 4: Testing & Validation (Week 4)

**Priority**: Verify refactoring maintains quality

- [ ] **Integration tests** for all refactored components
- [ ] **Voice validation** across all generated content
- [ ] **Regression testing** against previous outputs
- [ ] **Performance benchmarks** (should improve with less duplication)

---

## Metrics & Success Criteria

### Code Quality Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Hardcoded voice profiles | 4 locations | 0 | ❌ |
| Duplicate prompt templates | ~8 locations | 0 | ⚠️ |
| Manual voice transformation | 1 component | 0 | ❌ |
| Components using VoiceOrchestrator | 1/4 (FAQ) | 4/4 | ⚠️ |
| Lines of duplicate code | ~500 | <50 | ❌ |
| YAML-driven prompts | 0% | 100% | ❌ |

### Architecture Quality

- **Separation of Concerns**: 🟡 Fair → 🟢 Excellent
- **Reusability**: 🟡 Medium → 🟢 High
- **Maintainability**: 🟡 Fair → 🟢 Excellent
- **Extensibility**: 🟢 Good → 🟢 Excellent (already good)

---

## Benefits of Proposed Changes

### 1. Single Source of Truth
- Voice profiles: `voice/profiles/*.yaml` (not scattered in Python)
- Prompts: `prompts/*.yaml` (not hardcoded strings)
- Component behavior: Component generators (not duplicated logic)

### 2. Easier Maintenance
- Update voice pattern once → applies everywhere
- Update prompt template once → all generators benefit
- Add new country → just add YAML profile

### 3. Better Testability
- Test voice system independently
- Test prompt construction independently
- Test component generators independently

### 4. Improved Reusability
- Any component can use any prompt template
- Any generator can request any voice
- New components inherit existing infrastructure

### 5. Reduced Code
- ~500 lines of duplicate code → <50 lines of integration code
- Simpler component generators (30-40% smaller)
- More YAML, less Python (easier for non-developers to tune)

---

## Reference Implementation

**Model to Follow**: `components/faq/generators/faq_generator.py` + `voice/orchestrator.py`

### Before (Hardcoded)
```python
def _get_variation_guidance(self, author):
    if 'indonesia' in country:
        return """
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🎯 CRITICAL: NATURAL VARIATION
        MANDATORY LENGTH DISTRIBUTION:
        1. SHORT: 20-27 words...
        """  # 80 lines hardcoded
```

### After (YAML-Driven)
```python
def _get_variation_guidance(self, author):
    try:
        from voice.orchestrator import VoiceOrchestrator
        orchestrator = VoiceOrchestrator(author['country'])
        return orchestrator.get_faq_variation_guidance()  # From YAML
    except Exception as e:
        logger.warning(f"Could not load guidance: {e}")
        return ""
```

### YAML Profile
```yaml
# voice/profiles/indonesia.yaml
voice_adaptation:
  faq_generation:
    critical_variation_requirements:
      warning: "Previous generations showed ROBOTIC UNIFORMITY"
      mandatory_length_distribution:
        short_answers:
          range: "20-27 words"
          count: "2-3 answers"
```

**Result**: 
- 80 lines of Python → 5 lines of Python + YAML config
- Voice patterns centralized
- Easy to update without code changes

---

## Conclusion

**Current State**: System has strong voice architecture foundation (VoiceOrchestrator) but benefits not yet realized across all components.

**Target State**: All components use centralized voice system, all prompts in YAML, zero duplication, maximum reusability.

**Effort Required**: ~4 weeks focused refactoring (mostly mechanical changes following established patterns)

**Risk**: Low - established patterns to follow, comprehensive tests available

**Recommended Approach**: 
1. Fix critical frontmatter violations first (highest impact, clearest wins)
2. Extract prompts to YAML (enables non-developer tuning)
3. Complete voice integration (apply FAQ pattern to Caption/Subtitle)
4. Test thoroughly (prevent regressions)

**Expected Outcome**: 
- 🟢 Excellent separation of concerns
- 🟢 High reusability across all components
- 🟢 Easier maintenance and extension
- 🟢 Better code quality metrics
- 🟢 Faster development of new features

---

## References

- `VARIATION_FIX_COMPLETE.md` - Recent successful refactoring example
- `VOICE_ARCHITECTURE.md` - Voice system architecture
- `voice/orchestrator.py` - Central voice API
- `components/faq/generators/faq_generator.py` - Reference implementation
