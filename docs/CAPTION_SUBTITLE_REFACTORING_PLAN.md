# Caption & Subtitle Generator Refactoring Plan

**Date**: October 28, 2025  
**Status**: Planning Phase  
**Purpose**: Apply production hardening patterns from FAQ generator to caption and subtitle generators

---

## 📊 Current State Assessment

### Caption Generator (`components/caption/generators/generator.py`)
- **Size**: 897 lines
- **Complexity**: HIGH - Multiple integrated services
- **Voice Integration**: Already has VoiceService (complex integration)
- **Key Components**:
  - TopicResearcher integration
  - CopilotQualityGrader integration
  - VoiceService integration
  - Multi-stage generation pipeline
  - Quality grading and retry logic

### Subtitle Generator
- **Location**: TBD (needs discovery)
- **Size**: Unknown
- **Complexity**: Unknown
- **Voice Integration**: Unknown

---

## ✅ Patterns to Apply (from FAQ Generator Success)

### 1. Configuration Extraction
**Before**: Magic numbers scattered throughout code  
**After**: Named constants at file top

```python
# ============================================================================
# CONFIGURATION
# ============================================================================

# Caption length constraints (words)
MIN_WORDS_PER_CAPTION = X
MAX_WORDS_PER_CAPTION = Y

# Generation settings
GENERATION_TEMPERATURE = 0.6
MAX_TOKENS = 150

# Quality thresholds
MIN_QUALITY_SCORE = 70
RETRY_ATTEMPTS = 3

# API settings
API_CALL_DELAY_SECONDS = 0.5

# Data paths
MATERIALS_DATA_PATH = "data/Materials.yaml"
```

**Benefits**:
- Easy tuning without code diving
- Clear system constraints
- No magic numbers in logic

---

### 2. Atomic File Writes
**Before**: Direct writes (risk of corruption on failure)  
**After**: Temp file + atomic rename pattern

```python
def _save_to_materials_yaml(self, material_name: str, data: Dict) -> None:
    """Save caption data with atomic write"""
    materials_path = Path(MATERIALS_DATA_PATH)
    
    # Write to temp file first
    temp_path = materials_path.with_suffix('.tmp')
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        # Atomic rename (only succeeds if write completed)
        temp_path.replace(materials_path)
        logger.info(f"✅ Atomically saved caption to Materials.yaml")
        
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()  # Clean up temp file
        raise
```

**Benefits**:
- Never corrupt Materials.yaml on crash
- Production-grade reliability
- Clean error recovery

---

### 3. Simplified Input Validation
**Before**: Complex validation logic mixed with generation  
**After**: Fail-fast upfront validation

```python
def generate(self, material_name: str, material_data: Dict, api_client) -> ComponentResult:
    """Generate caption with fail-fast validation"""
    
    # Validate inputs immediately
    if not material_data:
        raise ValueError(f"Material data is required for {material_name}")
    
    if not api_client:
        raise ValueError("API client is required")
    
    # Continue with generation...
```

**Benefits**:
- Clear error messages
- Fail immediately on bad inputs
- No partial/invalid operations

---

### 4. Random Word Count Selection
**Before**: Complex distribution or fixed counts  
**After**: Simple random selection within range

```python
import random

# In generation method:
target_words = random.randint(MIN_WORDS_PER_CAPTION, MAX_WORDS_PER_CAPTION)
logger.info(f"Generating caption with target: {target_words} words")
```

**Benefits**:
- Natural variation
- Simple to understand
- No complex cycling logic

---

### 5. Voice as Discrete Post-Processing
**Current**: VoiceService tightly integrated  
**Proposed**: Optional post-processing with VoicePostProcessor

```python
# Generation returns unenhanced caption
caption_text = self._generate_caption_content(...)

# Voice enhancement is optional, separate step
# (Can be done by caller if needed)
# from voice.post_processor import VoicePostProcessor
# enhanced = processor.enhance(caption_text, author)
```

**Benefits**:
- Separation of concerns
- Simpler generator code
- Reusable voice enhancement
- Easier testing

---

## 🎯 Refactoring Strategy

### Phase 1: Caption Generator (Estimate: 2-3 hours)

#### Step 1.1: Extract Configuration (30 min)
- [ ] Identify all magic numbers
- [ ] Create configuration section at file top
- [ ] Replace hardcoded values with named constants
- [ ] Test: Generator loads without errors

#### Step 1.2: Add Atomic Writes (30 min)
- [ ] Implement `_save_to_materials_yaml()` with temp file pattern
- [ ] Replace direct writes with atomic method
- [ ] Test: Verify Materials.yaml integrity on crash

#### Step 1.3: Simplify Input Validation (20 min)
- [ ] Add fail-fast validation at method start
- [ ] Remove complex validation scattered in code
- [ ] Add specific error messages
- [ ] Test: Verify proper error handling

#### Step 1.4: Randomize Word Counts (15 min)
- [ ] Add `import random`
- [ ] Replace word count logic with `random.randint(MIN, MAX)`
- [ ] Test: Verify varied caption lengths

#### Step 1.5: Voice Separation (45 min) - OPTIONAL
- [ ] Remove VoiceService tight coupling
- [ ] Generate clean captions without voice
- [ ] Document voice post-processing pattern
- [ ] Test: Verify captions generate correctly
- [ ] Test: Verify VoicePostProcessor can enhance captions

#### Step 1.6: Code Cleanup (20 min)
- [ ] Remove unused imports
- [ ] Simplify complex methods
- [ ] Add docstrings for clarity
- [ ] Run linter and fix issues

#### Step 1.7: Integration Testing (30 min)
- [ ] Generate 3-5 test captions
- [ ] Verify Materials.yaml updates
- [ ] Check caption quality and variation
- [ ] Validate atomic writes work correctly

---

### Phase 2: Subtitle Generator (Estimate: 1-2 hours)

#### Step 2.1: Discovery (15 min)
- [ ] Locate subtitle generator file
- [ ] Assess current complexity
- [ ] Identify integrated services
- [ ] Document current architecture

#### Step 2.2: Apply Same Pattern (60-90 min)
- [ ] Extract configuration
- [ ] Add atomic writes
- [ ] Simplify validation
- [ ] Randomize word counts
- [ ] (Optional) Separate voice logic

#### Step 2.3: Testing (30 min)
- [ ] Generate test subtitles
- [ ] Verify Materials.yaml integration
- [ ] Check quality and variation
- [ ] Validate error handling

---

### Phase 3: Documentation & Integration (Estimate: 1 hour)

#### Step 3.1: Update run.py (30 min)
- [ ] Ensure caption/subtitle commands work
- [ ] Add voice post-processing option
- [ ] Test end-to-end workflows

#### Step 3.2: Documentation (30 min)
- [ ] Update component READMEs
- [ ] Document new configuration options
- [ ] Add voice post-processing examples
- [ ] Update QUICK_REFERENCE.md

---

## 🚨 Risk Mitigation

### Before Starting
1. **Backup current working code**
   ```bash
   cp components/caption/generators/generator.py components/caption/generators/generator_backup.py
   ```

2. **Create git branch**
   ```bash
   git checkout -b refactor/caption-subtitle-hardening
   ```

3. **Review current functionality**
   - Generate test captions with current code
   - Document expected behavior
   - Save examples for comparison

### During Refactoring
1. **Make incremental changes** - One pattern at a time
2. **Test after each change** - Verify nothing broke
3. **Commit frequently** - Easy rollback if needed

### After Refactoring
1. **Full regression testing**
   - Generate captions for 5-10 materials
   - Compare quality with pre-refactor examples
   - Verify Materials.yaml integrity

2. **Performance validation**
   - Check generation speed (should be similar or better)
   - Monitor API call efficiency
   - Validate caching still works

---

## 📈 Success Criteria

### Caption Generator
- ✅ Code reduced by 10-20% (cleaner, more focused)
- ✅ All configuration at file top (easy tuning)
- ✅ Atomic writes implemented (production-safe)
- ✅ Input validation simplified (fail-fast)
- ✅ Word counts randomized (natural variation)
- ✅ (Optional) Voice separated (discrete post-processing)
- ✅ No loss of quality or functionality

### Subtitle Generator
- ✅ Same patterns applied successfully
- ✅ Code simplified and hardened
- ✅ Configuration extracted
- ✅ Atomic writes implemented

### Integration
- ✅ run.py works with refactored generators
- ✅ Materials.yaml updated correctly
- ✅ Voice post-processing available (optional)
- ✅ Documentation updated

---

## 🔍 Open Questions

1. **Voice Integration Strategy**: Should we remove VoiceService entirely or keep it as fallback?
   - **Recommendation**: Remove for simplicity, use VoicePostProcessor instead

2. **Quality Grading**: Keep CopilotQualityGrader or simplify?
   - **Recommendation**: Keep if it provides value, but ensure it's configurable

3. **Topic Research**: Keep TopicResearcher integration?
   - **Recommendation**: Keep if essential for caption quality

4. **Retry Logic**: Preserve complex retry or simplify?
   - **Recommendation**: Keep retry for robustness, but make attempts configurable

---

## 📝 Notes

- FAQ generator went from 574 → 398 lines (30% reduction) with improved robustness
- Same approach should work well for caption/subtitle generators
- Focus on production hardening, not feature expansion
- Voice separation is optional but recommended for consistency
- Total time estimate: 4-6 hours for both generators + integration

---

## 🚀 Next Steps

**When ready to proceed:**

1. Ask: "Should I start caption generator optimization now?"
2. Review this plan together
3. Get approval for voice separation approach
4. Begin Phase 1 (Caption Generator refactoring)

**Or defer to later:**

- This is a comprehensive, multi-hour refactoring
- Can be done in separate session
- All patterns documented here for future reference
