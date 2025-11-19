# Winston AI Detection Scoring Analysis
**Date**: November 18, 2025  
**Status**: ⚠️ CRITICAL ISSUE IDENTIFIED

---

## 🚨 Executive Summary

**Problem**: Generated captions consistently score **0% human (100% AI)** on Winston detection, failing quality gates.

**Root Cause**: Temperature settings are TOO LOW (0.64), creating mechanical, predictable output that Winston AI easily identifies.

**Impact**: 
- All caption generation failing quality checks
- Batch tests cannot complete successfully
- System in failed state

**Solution**: Increase temperature configuration to improve human-like variation

---

## 📊 Current System Configuration

### Winston AI Threshold
```
Current Threshold: 30.9 (AI score)
Required Human Score: ≥ 69.1%
Actual Content Score: 0% human (100% AI)
Gap: 69.1% needed to pass
```

### Temperature Analysis
```yaml
Base Temperature (config.yaml): 0.8
Calculated Temperature (caption): 0.64  ⚠️ TOO LOW
Recommended Range: 0.8 - 1.0
```

**Why Temperature Matters**:
- **Low temperature (0.5-0.7)**: Mechanical, predictable, easily detected as AI
- **Medium temperature (0.7-0.9)**: Natural variation, passes Winston checks
- **High temperature (0.9-1.1)**: Creative, unpredictable, very human-like

### Current Sliders (config.yaml)
```yaml
humanness_intensity: 7              # Reasonable
sentence_rhythm_variation: 10       # Maximum variation (good)
imperfection_tolerance: 10          # Maximum tolerance (good)
structural_predictability: 10       # Maximum unpredictability (good)
ai_avoidance_intensity: 4           # Too low for strict Winston checks
```

---

## 🔍 Root Cause Analysis

### 1. Temperature Calculation Issue
The dynamic temperature calculator is **reducing** the base temperature instead of maintaining it:

```python
# From dynamic_config.py calculate_temperature()
base_temp = 0.8  # From config
creativity_factor = (imperfection + rhythm + structural) / 300.0
temp_adjustment = (creativity_factor - 0.5) * 0.4
calculated_temp = base_temp + temp_adjustment
# Result: 0.64 (TOO LOW)
```

**Issue**: The formula reduces temperature when it should be increasing it based on high slider values.

### 2. Prompt Template Structure
The caption prompt (`prompts/components/caption.txt`) is highly structured and formal:

```
TASK: Write two caption paragraphs for {material} at 1000x magnification.

Paragraph 1: Contaminated surface before cleaning
Paragraph 2: Clean surface after laser treatment

VOICE & STYLE:
- Objective technical documentation ONLY
- Complete sentences only - NO fragments
- Use precise technical verbs
- NO casual language
- Professional detachment
```

**Issue**: This creates mechanical, AI-like output with zero natural variation.

### 3. Winston Detection Sensitivity
Winston AI is correctly identifying content as AI-generated because:
- Sentence structure is too uniform
- Vocabulary is too technical and formal
- No natural human imperfections or variations
- Predictable paragraph structure

---

## 💊 Recommended Fixes

### Fix 1: Increase Base Temperature (IMMEDIATE)
```yaml
# In processing/config.yaml
# Change base temperature setting or adjust slider calculations

# Option A: Increase humanness_intensity
humanness_intensity: 9              # Was: 7 (increases temperature aggressiveness)

# Option B: Increase ai_avoidance_intensity
ai_avoidance_intensity: 7           # Was: 4 (forces higher temperature)

# Option C: Fix temperature calculation
# Ensure calculated temperature never drops below base temperature
```

### Fix 2: Revise Caption Prompt Template (RECOMMENDED)
```
# In prompts/components/caption.txt
# Add natural variation instructions:

VOICE & STYLE:
- Write naturally as if documenting observations in a lab notebook
- Vary sentence structure - some short, some longer with subordinate clauses
- Allow minor imperfections and natural phrasing
- Mix technical precision with conversational flow
- AVOID mechanical patterns - write how a scientist actually thinks and talks
```

### Fix 3: Dynamic Config Formula Adjustment (STRUCTURAL)
```python
# In processing/config/dynamic_config.py calculate_temperature()

def calculate_temperature(self, component_type: str = 'default') -> float:
    base_temp = self.base_config.get_temperature()
    
    # High slider values should INCREASE temperature, not decrease
    imperfection = self.base_config.get_imperfection_tolerance()
    rhythm = self.base_config.get_sentence_rhythm_variation()
    structural = self.base_config.get_structural_predictability()
    
    # Average of sliders (0-100 → 0.0-1.0)
    creativity_avg = (imperfection + rhythm + structural) / 300.0
    
    # Increase temperature by up to +0.3 based on slider values
    # At max sliders: +0.3, at min sliders: +0.0
    temp_adjustment = creativity_avg * 0.3
    
    calculated_temp = base_temp + temp_adjustment
    
    # Ensure minimum of 0.7 for human-like content
    return max(0.7, min(1.1, calculated_temp))
```

---

## 🧪 Testing Recommendations

### Phase 1: Quick Validation (5 minutes)
```bash
# Test with manually increased temperature
python3 -c "
from processing.generator import DynamicGenerator
from shared.api.client_factory import create_api_client

client = create_api_client('grok')
generator = DynamicGenerator(client)

# Override temperature calculation for test
generator.dynamic_config.calculate_temperature = lambda x: 0.9

# Generate single caption
result = generator.generate('Steel', 'caption')
print(result)
"
```

### Phase 2: Batch Testing (20-30 minutes)
```bash
# After fixing temperature, run full batch test
python3 run.py --batch-test

# Monitor results:
# - Human scores should be > 69%
# - AI scores should be < 31%
# - Quality gates should pass
```

### Phase 3: Statistical Analysis (1 hour)
```bash
# Generate 20+ captions across materials
# Analyze Winston score distribution
# Verify consistent passing scores
# Document optimal temperature range
```

---

### Expected Outcomes

### After Temperature Fix
| Metric | Before | After (Expected) |
|--------|--------|------------------|
| Human Score | 0% | 70-85% |
| AI Score | 100% | 15-30% |
| Pass Rate | 0% | 80-95% |
| Avg Attempts | 3+ (all fail) | 1-2 (success) |

### Success Criteria
- ✅ Human scores consistently > 69% (current Winston threshold at humanness_intensity=7)
- ✅ First-attempt success rate > 60%
- ✅ Average attempts per caption < 2
- ✅ No quality gate rejections
- ✅ Batch tests complete successfully

**Note**: Winston threshold is dynamically calculated based on `humanness_intensity` slider (1-10) in `processing/config.yaml`. Current setting of 7 yields 69% human minimum. To achieve the previously documented 80% threshold would require increasing to humanness_intensity=9-10.

---

## 🎯 Implementation Priority

### P0 - CRITICAL (Immediate)
1. **Increase `humanness_intensity` to 9** in `config.yaml`
2. **Test single caption generation** (Steel, Aluminum)
3. **Verify Winston scores improve** to 70%+ human

### P1 - HIGH (Today)
4. **Fix temperature calculation formula** in `dynamic_config.py`
5. **Run full batch test** (4 materials)
6. **Document successful temperature range**

### P2 - MEDIUM (This Week)
7. **Revise caption prompt template** for natural variation
8. **Add variation strategies** to prompt instructions
9. **Test across 20+ materials** for consistency

### P3 - LOW (Future Enhancement)
10. **Implement adaptive temperature learning** from Winston feedback
11. **Create material-specific temperature profiles**
12. **Optimize for both quality and speed**

---

## 🔗 Related Documentation

- **Learned Evaluation Integration**: `LEARNED_EVALUATION_INTEGRATION_NOV18_2025.md`
- **Realism Gate Implementation**: `REALISM_GATE_IMPLEMENTATION_NOV18_2025.md`
- **Prompt Purity Policy**: `docs/08-development/PROMPT_PURITY_POLICY.md`
- **Dynamic Config**: `processing/config/dynamic_config.py`
- **Caption Prompt**: `prompts/components/caption.txt`

---

## 📝 Notes

- Winston API is functioning correctly (connection verified)
- Detection method is reliable (using sentence-level analysis)
- Issue is NOT with Winston thresholds - they are appropriate
- Issue IS with generated content being too AI-like
- Temperature is the primary lever for human-likeness
- Prompt structure is secondary factor

**Bottom Line**: The system is working as designed. Generated content is genuinely too AI-like, and Winston is correctly identifying it. Fix: Generate more human-like content by increasing temperature.
