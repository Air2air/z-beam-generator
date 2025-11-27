# System Interactions & Dependencies

**For AI Assistants**: This document maps how components interact and what happens when you change one part.

## 🎯 Purpose

Understanding cascading effects prevents:
- Breaking unrelated features
- Creating circular dependencies
- Violating architectural boundaries
- Repeating past mistakes

---

## 📊 Core System Flow

```
User Request
    ↓
Material Data Loading (Materials.yaml)
    ↓
Component Generator (DynamicGenerator)
    ↓
┌─────────────────────────┐
│ Generation Loop         │
│                         │
│ Prompt Building         │ ← Loads prompts/*.txt
│    ↓                    │
│ Parameter Adaptation    │ ← Learns from database
│    ↓                    │
│ API Call (Grok)        │ ← Uses cached client
│    ↓                    │
│ Content Extraction      │ ← Uses adapter pattern
│    ↓                    │
│ Quality Gates           │ ← Multiple validators
│    ↓                    │
│ Learning & Feedback     │ ← Updates database
└─────────────────────────┘
    ↓
Success: Save to frontmatter
Failure: Retry with adjusted parameters
```

---

## 🔗 Dependency Map

### When You Change Prompts

**File**: `shared/text/templates/components/*.txt` or `shared/text/templates/evaluation/*.txt`

**Direct Impact**:
- Content generation immediately affected
- Quality gate behavior may change
- Learning patterns update based on new evaluations

**Cascade Effects**:
1. **Generation Quality**: Different voice guidance → different content
2. **Realism Scores**: Stricter requirements → more failures initially
3. **Learning Database**: New patterns learned based on new rules
4. **Parameter Sweet Spots**: May need recalibration

**Safe Changes**:
- ✅ Adding examples to existing rules
- ✅ Clarifying ambiguous requirements
- ✅ Adding more forbidden phrases

**Dangerous Changes**:
- ⚠️ Removing voice guidance (causes generation failures - see ADR-001)
- ⚠️ Contradicting existing rules (confuses learning)
- ⚠️ Making requirements much stricter (causes cascade of failures)

**Example**: November 18, 2025 - Removed voice guidance from prompts
- Result: 100% failure rate (0/4 batch tests)
- Realism scores dropped to 4.0-5.0/10 (below 7.0 threshold)
- Required adding guidance back to restore functionality

### When You Change Generation Code

**File**: `processing/generator.py`

**Direct Impact**:
- Parameter calculation logic
- Retry behavior
- Learning integration
- Quality gate enforcement

**Cascade Effects**:
1. **Quality Consistency**: Changed exploration rate → different consistency
2. **Database Schema**: New parameters → need migration
3. **Adapter Interface**: Changed extraction → update all adapters
4. **Learning Loop**: Changed feedback → affects future generations

**Safe Changes**:
- ✅ Adding new parameters to track
- ✅ Improving error messages
- ✅ Adding logging for debugging

**Dangerous Changes**:
- ⚠️ Changing exploration rate without testing (affects consistency)
- ⚠️ Removing retry logic (affects resilience)
- ⚠️ Bypassing quality gates (degrades output)

**Example**: November 18, 2025 - Reduced exploration 15% → 5%
- Result: 3x improvement in consistency (67% pass rate)
- Database: No schema changes needed
- Learning: Still functional, just less frequent exploration

### When You Change Quality Gates

**Files**: `processing/validation/`, `processing/subjective/`, `processing/detection/`

**Direct Impact**:
- Pass/fail criteria
- Retry frequency
- Learning feedback quality

**Cascade Effects**:
1. **Generation Success Rate**: Stricter → more retries
2. **Parameter Adaptation**: Different feedback → different adjustments
3. **Database Growth**: More failures → more learning entries
4. **User Experience**: More retries → slower generation

**Safe Changes**:
- ✅ Adding new validation checks (if not gates)
- ✅ Improving error messages
- ✅ Logging more details

**Dangerous Changes**:
- ⚠️ Changing thresholds without data analysis
- ⚠️ Adding new required gates (causes failures)
- ⚠️ Removing existing gates (degrades quality)

**Example**: Winston threshold dynamically calculated (currently 30.9% AI / 69.1% human at humanness_intensity=7)
- If humanness_intensity increased to 9: More content rejected → more retries → slower
- If humanness_intensity decreased to 5: More content accepted → lower quality → defeats purpose
- Threshold formula: Higher humanness_intensity = stricter detection (lower AI tolerance)

### When You Change Learning Systems

**Files**: `processing/learning/*.py`

**Direct Impact**:
- Parameter recommendations
- Sweet spot calculations
- Pattern detection

**Cascade Effects**:
1. **Generation Quality**: Better learning → better parameters → better content
2. **Database Size**: More tracking → more storage
3. **Performance**: Complex learning → slower recommendations
4. **Consistency**: Learning changes → behavior changes over time

**Safe Changes**:
- ✅ Improving algorithms (with backward compatibility)
- ✅ Adding new metrics to track
- ✅ Better visualization/logging

**Dangerous Changes**:
- ⚠️ Changing database schema without migration
- ⚠️ Breaking backward compatibility with old data
- ⚠️ Removing learning features (loses accumulated knowledge)

### When You Change API Clients

**Files**: `shared/api/*.py`

**Direct Impact**:
- All generation stops if broken
- Retry behavior changes
- Cache effectiveness changes

**Cascade Effects**:
1. **Generation Reliability**: Client issues → all content generation fails
2. **Cost**: Cache changes → more/fewer API calls → cost impact
3. **Performance**: Timeout changes → faster/slower generation
4. **Error Handling**: New exceptions → need handling everywhere

**Safe Changes**:
- ✅ Improving error messages
- ✅ Adding better logging
- ✅ Optimizing retry delays

**Dangerous Changes**:
- ⚠️ Changing client interface (breaks all generators)
- ⚠️ Modifying cache behavior (affects consistency)
- ⚠️ Removing retry logic (reduces resilience)

---

## 🎭 The Learning Loop Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING LOOP                             │
│                                                              │
│  Generation → Quality Check → Feedback → Learning → DB      │
│      ↓            ↓             ↓          ↓         ↓      │
│  Uses params  Pass/Fail?    Why failed  Update    Store    │
│      ↑                                   sweet     patterns │
│      └───────────────────────────────────spots    ←────────┘
│                                           ↓
│                                    Next generation
│                                    uses learned params
└─────────────────────────────────────────────────────────────┘
```

### Components Involved

1. **DynamicGenerator**: Orchestrates the loop
2. **ParameterBuilder**: Applies learned values
3. **Quality Validators**: Provide feedback
4. **Learning Modules**: Update sweet spots
5. **Database**: Persists knowledge

### What Happens When...

#### You Change Parameter Ranges
- Learning system explores new ranges
- May find better sweet spots
- Database accumulates new data
- Old sweet spots may become invalid

#### You Change Quality Criteria
- Different feedback to learning system
- Sweet spots recalculate for new criteria
- Database continues growing with new context
- May need to reset if incompatible

#### You Change Learning Algorithms
- Recommendations change immediately
- Database data remains valid (unless schema changes)
- May improve or degrade quality (test first)
- Backward compatibility important

---

## ⚠️ Known Failure Cascades

### Cascade #1: Removing Voice Guidance from Prompts

**What**: Removed voice requirements from component prompts (Nov 18, 2025)

**Expected**: Generator learns from evaluator feedback

**Actually Happened**:
```
Prompt without guidance
    ↓
Generator produces random style
    ↓
Evaluator rejects (doesn't match requirements)
    ↓
Learning system adjusts parameters
    ↓
Generator still doesn't know target style
    ↓
Infinite loop of failures (0/4 success rate)
```

**Fix**: Voice guidance in BOTH prompt and evaluator (ADR-001)

### Cascade #2: High Exploration Rate

**What**: 15% of attempts used random parameters

**Expected**: Better learning through experimentation

**Actually Happened**:
```
High randomness (15%)
    ↓
Inconsistent quality across runs
    ↓
Batch tests fail unpredictably
    ↓
Winston scores vary wildly (0.9% to 74.6%)
    ↓
User frustration with unreliable system
```

**Fix**: Reduced to 5% + added random_seed for reproducibility (ADR-003)

### Cascade #3: Hardcoded Thresholds

**What**: Hardcoded multipliers instead of dynamic calculation

**Historical Issue**: Discovered in Priority 1 compliance fixes

**Why It's Bad**:
```
Hardcoded threshold
    ↓
Learning system can't adapt
    ↓
Sweet spots diverge from hardcoded values
    ↓
System performance degrades over time
    ↓
Manual intervention required to update hardcoded values
```

**Fix**: Always use dynamic_config for thresholds and calculations

---

## 🔧 Safe Change Patterns

### Pattern 1: Additive Changes

**Safe**: Adding new features alongside existing ones
```python
# ✅ SAFE: Add new validation without breaking old
def validate_content(content):
    old_validation(content)  # Keep existing
    new_validation(content)  # Add new
```

**Unsafe**: Replacing existing features
```python
# ❌ UNSAFE: Breaks existing functionality
def validate_content(content):
    new_validation(content)  # Old validation gone!
```

### Pattern 2: Gradual Strictness

**Safe**: Tighten requirements gradually with warnings
```python
# ✅ SAFE: Warn before enforcing
if score < new_threshold:
    logger.warning(f"Score {score} below future threshold {new_threshold}")
if score < old_threshold:
    raise ValidationError("Below current threshold")
```

**Unsafe**: Sudden strict requirements
```python
# ❌ UNSAFE: Immediate enforcement breaks existing content
if score < much_higher_threshold:
    raise ValidationError("New strict threshold")
```

### Pattern 3: Versioned Interfaces

**Safe**: New version alongside old
```python
# ✅ SAFE: Backward compatible
def generate_v2(material, options):
    # New interface
    
def generate(material):  # Keep old interface
    return generate_v2(material, default_options)
```

**Unsafe**: Breaking interface changes
```python
# ❌ UNSAFE: Breaks all existing callers
def generate(material, required_new_param):
    # Old signature gone!
```

---

## 📚 For AI Assistants

### Before Making ANY Change

1. **Check This Document**: What will your change affect?
2. **Check ADRs**: Is there a decision record about this?
3. **Check History**: Has this been tried before and failed?
4. **Test Cascade**: What downstream effects will occur?

### Red Flags (Stop and Ask)

- 🚩 Removing existing functionality
- 🚩 Changing interfaces that other code depends on
- 🚩 Modifying quality thresholds
- 🚩 Altering learning algorithms
- 🚩 Changing database schemas
- 🚩 Bypassing validation

### Green Lights (Probably Safe)

- ✅ Adding logging
- ✅ Improving error messages
- ✅ Adding optional parameters (with defaults)
- ✅ Fixing obvious bugs
- ✅ Adding tests
- ✅ Updating documentation

### When Uncertain

**Ask yourself**:
1. What components depend on this?
2. What will break if this fails?
3. Can I add this instead of changing?
4. Is there a safer way to achieve the goal?

**If still uncertain**: Document the concern and ask the user.

---

## Related Documentation

- [ADR-001: Dual Voice Enforcement](./decisions/ADR-001-dual-voice-enforcement.md)
- [ADR-002: Fail-Fast vs Runtime Recovery](./decisions/ADR-002-fail-fast-vs-runtime-recovery.md)
- [ADR-003: Exploration Rate](./decisions/ADR-003-exploration-rate-reproducibility.md)
- [WINSTON_CONSISTENCY_FIXES_NOV18_2025.md](../WINSTON_CONSISTENCY_FIXES_NOV18_2025.md)
