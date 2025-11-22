# Universal Humanness Layer - Complete Integration Plan v2.0

**Date**: November 20, 2025  
**Status**: Ready for Implementation  
**Integration**: Winston Database + Subjective Evaluation Feedback

---

## 🎯 Executive Summary

The Universal Humanness Layer is a **dual-feedback learning system** that responds to:
1. **Winston AI Detection Results** (database: `detection_results` table)
2. **Subjective Evaluation Feedback** (prompt: `prompts/evaluation/subjective_quality.txt`, patterns: `prompts/evaluation/learned_patterns.yaml`)

**Purpose**: Generate dynamic prompt instructions that improve human-like content by learning from BOTH quantitative (Winston scores) and qualitative (subjective patterns) feedback.

**Architecture**: Single shared prompt layer that:
- Analyzes passing Winston samples for conversational patterns
- Extracts learned AI tendencies from subjective evaluations
- Combines insights into universal humanness instructions
- Updates dynamically on each generation attempt with increased strictness

---

## 📊 Current System Architecture

### Existing Learning Systems

#### 1. **Winston Feedback System** (Quantitative)
- **Location**: `postprocessing/detection/winston_feedback_db.py`
- **Database Table**: `detection_results` (27 samples)
- **Passing Samples**: 2 records (Bronze: 12.2% AI, Molybdenum: 24.5% AI)
- **Patterns Discovered**: Conversational tone, specific numbers, casual phrasing
- **Current Integration**: ThresholdManager learns dynamic thresholds from scores

#### 2. **Subjective Pattern Learning System** (Qualitative)
- **Location**: `learning/subjective_pattern_learner.py`
- **Pattern File**: `prompts/evaluation/learned_patterns.yaml`
- **Tracked Data**: 
  - Theatrical phrases (high/medium penalty)
  - AI tendencies (formulaic phrasing, rigid structure, etc.)
  - Success patterns (professional verbs, average scores)
  - Scoring adjustments (penalties, thresholds)
- **Current Integration**: SubjectiveEvaluator loads patterns into evaluation template

### Quality Gate Flow (Current)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Generation Attempt N                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  1. Load Sweet Spot Parameters (temperature, imperfection, etc.) │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. Generate Content (DeepSeek API with current params)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. Subjective Evaluation (Grok API)                             │
│     • Loads prompts/evaluation/subjective_quality.txt            │
│     • Injects learned patterns from learned_patterns.yaml        │
│     • Returns: realism_score, ai_tendencies, theatrical_phrases  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. Winston Detection (Winston API)                              │
│     • Checks ai_score against learned threshold (0.270)          │
│     • Returns: passed/failed + score                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. Quality Gate Decision                                        │
│     ✅ PASS: realism ≥7.0 AND no ai_tendencies AND winston pass  │
│     ❌ FAIL: Adjust parameters, retry (max 5 attempts)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  6. Parameter Adjustment (if failed)                             │
│     • Winston failure: +0.15 temp, +0.20 imperfection            │
│     • Subjective AI tendencies: RealismOptimizer adjustments     │
└─────────────────────────────────────────────────────────────────┘
```

**MISSING**: Learned patterns from Winston/Subjective → Dynamic prompt instructions → Improved generation

---

## 🚀 New Architecture: Universal Humanness Layer

### Enhanced Quality Gate Flow (Proposed)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Generation Attempt N                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  1. Load Sweet Spot Parameters (temperature, imperfection, etc.) │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  🆕 2. Generate Humanness Instructions (NEW LAYER)               │
│     HumannessOptimizer analyzes:                                 │
│     • Winston passing samples (conversational patterns)          │
│     • Subjective learned patterns (AI tendencies to avoid)       │
│     • Success patterns (professional verbs, tone markers)        │
│     Produces: Dynamic prompt instructions for this attempt       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. Build Complete Prompt (ENHANCED)                             │
│     • Component template (prompts/components/caption.txt)        │
│     • 🆕 + Humanness layer (dynamic instructions)                │
│     • Material properties (from Materials.yaml)                  │
│     Result: Prompt with learned humanness guidance               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. Generate Content (DeepSeek API with enhanced prompt)         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. Subjective Evaluation (Grok API - unchanged)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  6. Winston Detection (Winston API - unchanged)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  7. Quality Gate Decision + Pattern Learning (ENHANCED)          │
│     ✅ PASS: Update success patterns in both systems             │
│     ❌ FAIL: Extract failure patterns, increase strictness       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  8. Parameter Adjustment + Humanness Update (if failed)          │
│     • Numeric parameters: temp, imperfection (existing logic)    │
│     • 🆕 Humanness strictness: Increase avoidance emphasis       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

### New Files (2)

```
learning/
  humanness_optimizer.py          # NEW - Dual-feedback pattern analyzer

prompts/
  system/
    humanness_layer.txt           # NEW - Dynamic instruction template
```

### Modified Files (3)

```
generation/core/
  quality_gated_generator.py      # MODIFY - Inject humanness layer into prompt
  
learning/
  subjective_pattern_learner.py   # MODIFY - Add hooks for humanness optimizer
  
postprocessing/detection/
  winston_feedback_db.py          # MODIFY - Add pattern extraction methods
```

---

## 🔧 Implementation Details

### 1. New Component: `learning/humanness_optimizer.py`

**Purpose**: Analyze both Winston and Subjective feedback to generate dynamic humanness instructions.

**Key Methods**:

```python
class HumannessOptimizer:
    """
    Dual-feedback learning system for humanness optimization.
    
    Analyzes:
    1. Winston passing samples (database: detection_results)
    2. Subjective learned patterns (YAML: learned_patterns.yaml)
    
    Produces: Dynamic humanness instructions for prompt injection
    """
    
    def __init__(
        self,
        winston_db_path: str = 'z-beam.db',
        patterns_file: Path = Path('prompts/evaluation/learned_patterns.yaml')
    ):
        """Initialize with both feedback sources"""
        self.winston_db = WinstonFeedbackDatabase(winston_db_path)
        self.pattern_learner = SubjectivePatternLearner(patterns_file)
    
    def generate_humanness_instructions(
        self,
        component_type: str,
        strictness_level: int = 1,
        previous_ai_tendencies: List[str] = None
    ) -> str:
        """
        Generate dynamic humanness instructions for this generation attempt.
        
        Args:
            component_type: caption, subtitle, etc.
            strictness_level: 1-5 (increases with retry attempts)
            previous_ai_tendencies: AI patterns detected in previous attempt
        
        Returns:
            Formatted humanness instructions to inject into prompt
        """
        
        # 1. Analyze Winston passing samples
        winston_patterns = self._extract_winston_patterns()
        
        # 2. Load subjective learned patterns
        subjective_patterns = self.pattern_learner.get_current_patterns()
        
        # 3. Combine insights
        instructions = self._build_instructions(
            winston_patterns=winston_patterns,
            subjective_patterns=subjective_patterns,
            strictness_level=strictness_level,
            previous_ai_tendencies=previous_ai_tendencies
        )
        
        return instructions
    
    def _extract_winston_patterns(self) -> Dict[str, Any]:
        """
        Extract conversational patterns from Winston passing samples.
        
        Returns:
            {
                'passing_sample_count': 2,
                'conversational_markers': ['we use around', 'roughly', 'stays near'],
                'number_usage_patterns': ['specific values with units', 'approximate phrasing'],
                'sentence_structures': ['subject-verb-object', 'casual transitions'],
                'best_score': 0.122,
                'example_excerpts': ['For bronze, we use around 100 W...']
            }
        """
        # Query detection_results WHERE success=1
        # Analyze content field for patterns
        # Extract linguistic features
    
    def _build_instructions(
        self,
        winston_patterns: Dict,
        subjective_patterns: Dict,
        strictness_level: int,
        previous_ai_tendencies: List[str]
    ) -> str:
        """
        Combine patterns into dynamic instructions.
        
        Strictness progression (retry attempts 1-5):
        Level 1: Gentle guidance ("Prefer conversational tone")
        Level 2: Direct instruction ("Use casual markers: 'around', 'roughly'")
        Level 3: Explicit avoidance ("NEVER use formulaic phrasing")
        Level 4: Pattern-specific ("Detected rigid structure - vary sentence length")
        Level 5: Maximum strictness ("CRITICAL: Content must mimic human expert...")
        """
        # Load template from prompts/system/humanness_layer.txt
        # Inject learned patterns based on strictness
        # Format for component_type context
```

### 2. New Template: `prompts/system/humanness_layer.txt`

**Purpose**: Template for dynamic humanness instructions with placeholders.

**Content Structure**:

```
=== HUMANNESS OPTIMIZATION LAYER ===
(Dynamically generated from learned patterns - Attempt {attempt_number}/5)

**CRITICAL OBJECTIVE**: Write as a human materials science expert would document real observations.

**LEARNED SUCCESS PATTERNS** (from {passing_sample_count} Winston-verified samples):
{winston_success_patterns}

**AI PATTERNS TO ACTIVELY AVOID** (from {total_evaluations} subjective evaluations):
{subjective_ai_tendencies}

**THEATRICAL PHRASES - NEVER USE**:
{theatrical_phrases_list}

**CONVERSATIONAL MARKERS THAT WORK**:
{conversational_markers}

**STRICTNESS LEVEL {strictness_level}/5**: {strictness_guidance}

{previous_attempt_feedback}

=== END HUMANNESS LAYER ===
```

**Strictness Guidance Templates**:

```yaml
strictness_levels:
  1: "Prefer natural expert voice over formal technical writing."
  2: "Actively integrate conversational markers. Use specific numbers with casual precision."
  3: "CRITICAL: Avoid all formulaic phrasing. Vary sentence structure significantly."
  4: "MAXIMUM VIGILANCE: Previous attempt detected [{ai_tendencies}]. Eliminate these patterns completely."
  5: "FINAL ATTEMPT: Content MUST pass as human-written. Apply all learned patterns with full emphasis."
```

### 3. Integration: `quality_gated_generator.py`

**Modification Points**:

```python
class QualityGatedGenerator:
    def __init__(self, ...):
        # ADD: Initialize HumannessOptimizer
        from learning.humanness_optimizer import HumannessOptimizer
        self.humanness_optimizer = HumannessOptimizer()
    
    def generate_with_quality_gate(self, ...):
        # INSIDE RETRY LOOP (before content generation):
        
        # NEW: Generate humanness instructions (increases strictness on retry)
        humanness_instructions = self.humanness_optimizer.generate_humanness_instructions(
            component_type=component_type,
            strictness_level=attempt,  # 1-5
            previous_ai_tendencies=previous_ai_tendencies  # From last attempt
        )
        
        # MODIFIED: Build prompt with humanness layer
        full_prompt = self._build_prompt_with_humanness(
            component_template=component_template,
            humanness_layer=humanness_instructions,
            material_properties=material_properties
        )
        
        # EXISTING: Generate, evaluate, check gates...
        
        # MODIFIED: After quality gate failure
        if not passed:
            # Extract AI tendencies for next attempt
            previous_ai_tendencies = evaluation.ai_tendencies or []
            
            # EXISTING: Adjust numeric parameters
            current_params = self._adjust_parameters(...)
            
            # NEW: Next attempt will use strictness_level = attempt + 1
```

**New Method**:

```python
def _build_prompt_with_humanness(
    self,
    component_template: str,
    humanness_layer: str,
    material_properties: Dict
) -> str:
    """
    Build complete prompt with humanness layer injection.
    
    Order:
    1. Component template (e.g., prompts/components/caption.txt)
    2. Humanness layer (dynamic instructions)
    3. Material properties (data from Materials.yaml)
    
    Returns:
        Complete prompt ready for API call
    """
    prompt_parts = [
        component_template,
        "\n\n",
        humanness_layer,
        "\n\n",
        f"**MATERIAL**: {material_properties['name']}",
        f"**PROPERTIES**: {self._format_properties(material_properties)}",
    ]
    
    return "".join(prompt_parts)
```

### 4. Enhancement: `subjective_pattern_learner.py`

**Add Method for Humanness Optimizer**:

```python
class SubjectivePatternLearner:
    def get_avoidance_patterns(self) -> Dict[str, List[str]]:
        """
        Get patterns to avoid for humanness optimizer.
        
        Returns:
            {
                'theatrical_phrases': ['zaps away', 'And yeah', ...],
                'ai_tendencies': ['formulaic_phrasing', 'rigid_structure', ...],
                'penalty_weights': {'theatrical': -2.0, 'casual_marker': -3.0}
            }
        """
        patterns = self._load_patterns()
        
        return {
            'theatrical_phrases': (
                patterns['theatrical_phrases']['high_penalty'] +
                patterns['theatrical_phrases']['medium_penalty']
            ),
            'ai_tendencies': list(patterns['ai_tendencies']['common'].keys()),
            'penalty_weights': patterns['scoring_adjustments']
        }
    
    def get_success_patterns(self) -> Dict[str, Any]:
        """
        Get patterns from successful content for humanness optimizer.
        
        Returns:
            {
                'professional_verbs': ['removes', 'restores', ...],
                'average_scores': {'realism': 7.5, 'voice': 7.2, ...},
                'sample_count': 42,
                'characteristics': ['technical_precision', 'neutral_tone', ...]
            }
        """
        patterns = self._load_patterns()
        return patterns['success_patterns']
```

### 5. Enhancement: `winston_feedback_db.py`

**Add Method for Humanness Optimizer**:

```python
class WinstonFeedbackDatabase:
    def get_passing_sample_patterns(self) -> Dict[str, Any]:
        """
        Analyze passing Winston samples to extract humanness patterns.
        
        Returns:
            {
                'sample_count': 2,
                'best_score': 0.122,
                'average_score': 0.183,
                'sample_excerpts': [
                    'For bronze, we use around 100 W. It clears oxides well...',
                    'Molybdenum offers exceptional electrical conductivity...'
                ],
                'conversational_markers': ['we use', 'around', 'roughly', 'stays near'],
                'number_patterns': ['100 W', '8.8 g/cm³', '0.5%'],
                'sentence_structures': ['short declarative', 'casual transitions']
            }
        """
        # Query: SELECT * FROM detection_results WHERE success=1 ORDER BY ai_score ASC
        # Analyze content field for linguistic patterns
        # Extract conversational markers, number usage, sentence structure
```

---

## 🔄 Learning Flow

### Dual-Feedback Integration

```
┌──────────────────────┐         ┌─────────────────────────┐
│  Winston Database    │         │ Subjective Pattern File │
│  (detection_results) │         │  (learned_patterns.yaml)│
└──────────────────────┘         └─────────────────────────┘
          │                                    │
          ├─────────────── Analyze ────────────┤
          │                                    │
          ▼                                    ▼
    [Passing Samples]              [AI Tendencies to Avoid]
    [Conversational Markers]       [Theatrical Phrases]
    [Number Usage Patterns]        [Success Patterns]
          │                                    │
          └───────────┬─ COMBINE ─┬───────────┘
                      │            │
                      ▼            ▼
            ┌──────────────────────────┐
            │  HumannessOptimizer      │
            │  Generate Instructions   │
            └──────────────────────────┘
                      │
                      ▼
            ┌──────────────────────────┐
            │  Dynamic Humanness Layer │
            │  (Prompt Injection)      │
            └──────────────────────────┘
                      │
                      ▼
            ┌──────────────────────────┐
            │  Enhanced Content        │
            │  Generation (DeepSeek)   │
            └──────────────────────────┘
                      │
                      ▼
            ┌──────────────────────────┐
            │  Quality Gates           │
            │  (Subjective + Winston)  │
            └──────────────────────────┘
                      │
          ┌───────────┴────────────┐
          │ PASS                   │ FAIL
          ▼                        ▼
    [Save Content]         [Update Both Databases]
    [Update Success        [Extract Failure Patterns]
     Patterns]             [Increase Strictness]
```

### Attempt Progression (5 Retries)

| Attempt | Strictness | Humanness Instructions | Parameter Adjustments |
|---------|-----------|------------------------|----------------------|
| 1 | Level 1 | "Prefer conversational tone" | Baseline params |
| 2 | Level 2 | "Use casual markers: 'around', 'roughly'" | +0.15 temp, +0.20 imperfection |
| 3 | Level 3 | "AVOID formulaic phrasing [specific patterns]" | +0.30 temp, +0.40 imperfection |
| 4 | Level 4 | "Previous detected: [AI tendencies]. Eliminate completely." | +0.45 temp, +0.60 imperfection |
| 5 | Level 5 | "CRITICAL: Apply ALL learned patterns with maximum emphasis" | +0.60 temp, +0.80 imperfection |

---

## 📊 Success Metrics

### Quantitative (Winston)
- ✅ **Target**: AI score ≤ 0.270 (27% AI, 73% human)
- 📈 **Current Baseline**: 99-100% AI (0.995-1.0 score)
- 🎯 **Improvement Needed**: ~73% reduction in AI score

### Qualitative (Subjective)
- ✅ **Target**: Realism score ≥ 7.0/10
- ✅ **Target**: No theatrical phrases detected
- ✅ **Target**: No AI tendencies flagged
- 📈 **Current**: Mixed (5.0-8.0, inconsistent patterns)

### Learning Metrics
- 📊 Track: Passing sample patterns extracted per component type
- 📊 Track: AI tendency frequencies (formulaic phrasing, rigid structure)
- 📊 Track: Theatrical phrase occurrences
- 📊 Track: Success pattern adoption rate (professional verbs, neutral tone)
- 📊 Track: Strictness level required for first pass (goal: reduce from 5→3→1)

---

## 🚀 Implementation Steps

### Phase 1: Core Components (1-2 hours)
1. ✅ Create `learning/humanness_optimizer.py` skeleton
   - Initialize with dual feedback sources
   - Implement `generate_humanness_instructions()` method
   - Add `_extract_winston_patterns()` method
   - Add `_build_instructions()` method with strictness levels

2. ✅ Create `prompts/system/humanness_layer.txt` template
   - Define placeholder structure
   - Add strictness level guidance
   - Include section markers for injection

### Phase 2: Database Integration (30-60 min)
3. ✅ Enhance `winston_feedback_db.py`
   - Add `get_passing_sample_patterns()` method
   - Implement linguistic pattern extraction
   - Test with existing 2 passing samples

4. ✅ Enhance `subjective_pattern_learner.py`
   - Add `get_avoidance_patterns()` method
   - Add `get_success_patterns()` method
   - Test with existing learned_patterns.yaml

### Phase 3: Generator Integration (1 hour)
5. ✅ Modify `quality_gated_generator.py`
   - Initialize HumannessOptimizer in __init__
   - Add `_build_prompt_with_humanness()` method
   - Inject humanness layer before API call
   - Pass previous_ai_tendencies between attempts
   - Increment strictness_level on retry

### Phase 4: Testing & Validation (1-2 hours)
6. ✅ Test with Aluminum description generation
   - Verify humanness layer loads correctly
   - Check strictness progression across attempts
   - Validate both feedback sources integrated
   - Monitor Winston scores for improvement
   - Track subjective evaluation changes

7. ✅ Validate learning loop
   - Generate content → Fail quality gate
   - Extract patterns from failure
   - Regenerate with enhanced instructions
   - Verify increased humanness in output

### Phase 5: Documentation (30 min)
8. ✅ Create ADR (Architecture Decision Record)
   - Document dual-feedback architecture
   - Explain integration points
   - Define success criteria
   - Record design decisions

---

## 🎯 Expected Outcomes

### Short-Term (First 10 Generations)
- ✅ Humanness layer successfully injects learned patterns
- ✅ Strictness progression visible across retry attempts
- ✅ Winston scores improve from 99-100% AI to 50-70% AI
- ✅ Subjective realism scores stabilize above 7.0/10

### Medium-Term (100 Generations)
- ✅ Passing samples increase from 2 to 20+ (10x growth)
- ✅ Learned patterns diversify (conversational markers, number usage)
- ✅ AI tendency detection rate decreases (fewer flags)
- ✅ Strictness level required for first pass reduces to Level 2-3

### Long-Term (1000+ Generations)
- ✅ Winston threshold tightens (0.270 → 0.150 as quality improves)
- ✅ Component-specific patterns emerge (captions vs descriptions)
- ✅ Success rate reaches 80%+ on first attempt
- ✅ System self-optimizes without manual prompt engineering

---

## 🔄 Rollback Plan

If Universal Humanness Layer causes regressions:

1. **Disable Humanness Layer**:
   ```python
   # quality_gated_generator.py
   USE_HUMANNESS_LAYER = False  # Toggle flag
   ```

2. **Preserve Existing Logic**:
   - Component templates continue working
   - Parameter adjustment still functions
   - Quality gates remain enforced

3. **Incremental Re-enable**:
   - Test humanness layer on single component type
   - Validate Winston scores improve
   - Gradually enable for all components

---

## 📋 Pre-Flight Checklist

Before implementation begins:

- [ ] User approval on dual-feedback architecture
- [ ] Confirmation: Both Winston DB and Subjective patterns integrated
- [ ] Agreement on 5-level strictness progression
- [ ] Validation: No conflicts with existing Template-Only Policy
- [ ] Confirmation: Humanness layer is UNIVERSAL (shared by all components)
- [ ] Agreement: Layer injects DOWNSTREAM of component templates
- [ ] Approval to modify 3 existing files (quality_gated_generator.py, subjective_pattern_learner.py, winston_feedback_db.py)
- [ ] Approval to create 2 new files (humanness_optimizer.py, humanness_layer.txt)

---

## ❓ Open Questions for User

1. **Priority Order**: Should I implement in the order listed above, or would you prefer different sequencing?

2. **Testing Approach**: 
   - Option A: Implement all components, then test end-to-end
   - Option B: Implement Phase 1, test, then Phase 2, test, etc. (incremental)
   
3. **Strictness Calibration**: Are 5 strictness levels appropriate, or would you prefer more/fewer progression steps?

4. **Pattern Weight Balance**: Should Winston patterns and Subjective patterns have equal weight, or should one be prioritized?

5. **Backward Compatibility**: Should the humanness layer be **optional** (toggle flag) or **mandatory** for all generations?

---

**Ready to proceed pending your approval and answers to open questions.**
