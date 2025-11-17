# Processing Module Workflow Documentation

**Location**: `/processing`  
**Purpose**: Core content generation pipeline - transforms configuration + data into high-quality, AI-resistant text  
**Last Updated**: January 2025

---

## 🎯 Overview

The `/processing` module is the **heart of the Z-Beam generation system**. It orchestrates the entire content generation workflow from configuration to final output.

```
┌─────────────┐
│   Config    │ ──┐
│ (config/)   │   │
└─────────────┘   │
                  │    ┌──────────────────────────────┐
┌─────────────┐   ├───→│   PROCESSING PIPELINE        │
│  Material   │   │    │  (orchestrator.py)           │───→ Generated Content
│   Data      │ ──┘    └──────────────────────────────┘
└─────────────┘              ↓    ↓    ↓    ↓    ↓
                          Generation  Voice  Detection  Validation  Learning
```

---

## 📂 Directory Structure

```
processing/
├── config/                      # Configuration management
│   ├── config.yaml              # Master configuration (14 parameters)
│   ├── config_loader.py         # Configuration loading
│   └── dynamic_config.py        # Dynamic parameter calculation
│
├── generation/                  # Prompt building and text generation
│   ├── prompt_builder.py        # Unified prompt orchestration (610 lines)
│   ├── component_specs.py       # Component specifications
│   └── sentence_calculator.py   # Sentence count/length calculations
│
├── voice/                       # Author voice profiles and traits
│   ├── voice_loader.py          # Load voice profiles from data/authors/
│   └── voice_traits.py          # Voice trait application
│
├── enrichment/                  # Data enrichment and fact formatting
│   ├── data_enricher.py         # Format facts with voice
│   └── fact_formatter.py        # Technical fact presentation
│
├── detection/                   # AI detection and avoidance
│   ├── advanced_detector.py    # Pattern-based AI detection
│   ├── winston_client.py        # Winston AI API integration
│   └── winston_feedback.db      # Winston feedback database
│
├── validation/                  # Content quality validation
│   ├── content_validator.py    # Structure and quality checks
│   └── schema_validator.py     # YAML schema validation
│
├── learning/                    # Self-learning system
│   ├── prompt_optimizer.py     # Learns optimal prompts from feedback
│   ├── success_predictor.py    # Predicts generation success
│   ├── temperature_advisor.py  # Learns optimal temperatures
│   └── pattern_learner.py      # Learns failure patterns
│
├── evaluation/                  # Claude-based evaluation
│   ├── claude_evaluator.py     # Subjective quality evaluation
│   └── integration_helper.py   # Evaluation integration
│
├── integrity/                   # System integrity checking
│   └── integrity_checker.py    # Pre-generation validation (17 checks)
│
├── orchestrator.py              # Legacy orchestrator (being phased out)
├── unified_orchestrator.py      # New unified orchestrator
└── generator.py                 # Main generator entry point
```

---

## 🔄 Workflow Stages

### **Stage 1: Configuration Loading**
**Files**: `config/config_loader.py`, `config/dynamic_config.py`

```python
# Load configuration
config = get_config()  # Loads config.yaml

# Create dynamic config calculator
dynamic_config = DynamicConfig(config)

# Get all generation parameters
params = dynamic_config.get_all_generation_params(component_type='caption')
# Returns: {
#   'temperature': 0.85,
#   'voice_params': {14 parameters},
#   'enrichment_params': {4 parameters},
#   'penalties': {'frequency': 0.3, 'presence': 0.8}
# }
```

**What happens**:
1. Loads `config.yaml` with 14 user-facing parameters (1-10 scale)
2. Normalizes to 0.0-1.0 floats
3. Calculates derived values (temperature, penalties, etc.)
4. Determines tier levels (low/moderate/high)

---

### **Stage 2: Voice Profile Loading**
**Files**: `voice/voice_loader.py`, `voice/voice_traits.py`

```python
# Load author voice
voice = VoiceLoader.load_voice('italy')
# Returns: {
#   'author': 'Sofia Benedetti',
#   'country': 'Italy',
#   'esl_traits': 'Article flexibility, past tense preference...',
#   'grammar_norms': {...},
#   'vocabulary': {'action_verbs': [...], ...}
# }
```

**What happens**:
1. Loads voice profile from `data/authors/{country}/voice.yaml`
2. Extracts ESL traits, grammar patterns, vocabulary preferences
3. Prepares voice characteristics for prompt injection

---

### **Stage 3: Data Enrichment**
**Files**: `enrichment/data_enricher.py`

```python
# Enrich material facts
enricher = DataEnricher(config)
facts = enricher.enrich_material_facts(
    material_name='Aluminum',
    enrichment_params=params['enrichment_params']
)
# Returns formatted facts string with voice-appropriate language
```

**What happens**:
1. Retrieves material properties from `Materials.yaml`
2. Formats technical data based on `technical_intensity` parameter
3. Applies voice-appropriate language (formal/balanced/conversational)
4. Creates fact string for prompt injection

---

### **Stage 4: Prompt Building**
**Files**: `generation/prompt_builder.py`

```python
# Build unified prompt
prompt = PromptBuilder.build_unified_prompt(
    topic='Aluminum',
    voice=voice,
    length=50,
    facts=facts,
    component_type='caption',
    voice_params=params['voice_params'],
    enrichment_params=params['enrichment_params']
)
```

**What happens**:
1. **TASK section**: Component type, word count, end punctuation rules
2. **REQUIREMENTS section**: Technical requirements, emotional tone guidance
3. **VOICE section**: Author profile, ESL traits, **14 parameter prompts**
   - Sentence rhythm variation
   - Imperfection tolerance
   - Jargon removal
   - Professional voice
   - (etc. - all 14 parameters inject guidance here)
4. **ANTI-AI section**: AI avoidance strategies (based on structural_predictability)
5. **FACTS section**: Enriched material data
6. **CONTEXT section**: Additional context if provided

**Result**: ~500-800 word prompt with all parameters orchestrated

---

### **Stage 5: API Generation**
**Files**: `orchestrator.py`, `unified_orchestrator.py`

```python
# Generate content via API
orchestrator = UnifiedOrchestrator(config)
result = orchestrator.generate(
    material_name='Aluminum',
    component_type='caption',
    attempt=1
)
```

**What happens**:
1. **Pre-generation integrity check** (17 validations)
2. **Self-learning optimization** (learns from past attempts)
3. **API call** (Grok/GPT/Claude) with orchestrated prompt
4. **Temperature/penalty application** (from dynamic config or learned values)
5. **Response parsing** and extraction
6. **Word count validation**

---

### **Stage 6: AI Detection**
**Files**: `detection/advanced_detector.py`, `detection/winston_client.py`

```python
# Detect AI patterns
detector = AdvancedAIDetector(threshold=30)
detection_result = detector.detect(generated_text)

# Winston AI check (optional)
winston_result = winston_client.check_content(generated_text)
```

**What happens**:
1. **Pattern detection**: Checks 54 AI indicators (clichés, formulaic phrases)
2. **Grammar analysis**: Detects overly perfect grammar
3. **Phrasing analysis**: Identifies AI-like sentence structures
4. **Winston API**: External AI detection (optional, for validation)
5. **Scoring**: Returns AI detection score (0-100)

---

### **Stage 7: Content Validation**
**Files**: `validation/content_validator.py`

```python
# Validate content quality
validator = ContentValidator()
validation_result = validator.validate(
    content=generated_text,
    component_type='caption',
    expected_length=50
)
```

**What happens**:
1. **Length validation**: Checks word count within acceptable range
2. **Structure validation**: Verifies proper formatting
3. **Quality checks**: No placeholder text, proper capitalization
4. **Component-specific rules**: End punctuation, length requirements

---

### **Stage 8: Learning & Feedback**
**Files**: `learning/prompt_optimizer.py`, `learning/success_predictor.py`

```python
# Log attempt for learning
prompt_optimizer.log_attempt(
    material_name='Aluminum',
    component_type='caption',
    attempt_number=1,
    success=True,
    ai_score=25,
    word_count=48,
    temperature=0.85,
    penalties={'frequency': 0.3, 'presence': 0.8}
)
```

**What happens**:
1. **Success prediction**: Predicts if attempt will pass (based on history)
2. **Pattern learning**: Identifies what causes failures
3. **Temperature learning**: Learns optimal temperatures per material
4. **Prompt optimization**: Adjusts prompt guidance based on feedback
5. **Database storage**: All attempts logged for future learning

---

### **Stage 9: Claude Evaluation** (Optional)
**Files**: `evaluation/claude_evaluator.py`

```python
# Get subjective quality score
evaluator = ClaudeEvaluator()
quality_score = evaluator.evaluate(
    content=generated_text,
    material_name='Aluminum',
    component_type='caption'
)
# Returns: Score 1-10 with detailed feedback
```

**What happens**:
1. Sends content to Claude API
2. Gets subjective quality evaluation (human believability, accuracy, tone)
3. Stores feedback in database
4. Uses feedback for future prompt optimization

---

## 🔗 Complete Workflow Example

```python
# 1. Load configuration
config = get_config()
dynamic_config = DynamicConfig(config)

# 2. Run integrity check
checker = IntegrityChecker()
results = checker.run_quick_checks()
# ✅ All 17 checks pass

# 3. Create orchestrator
orchestrator = UnifiedOrchestrator(config)

# 4. Generate content (all stages happen automatically)
result = orchestrator.generate(
    material_name='Aluminum',
    component_type='caption'
)

# Behind the scenes:
# - Voice loaded (Italy - Sofia Benedetti)
# - Facts enriched (technical intensity = 5)
# - Prompt built (14 parameters orchestrated)
# - Self-learning optimized parameters
# - API called with learned temperature
# - Content validated (length, structure, quality)
# - AI detection ran (score = 25 ✅)
# - Attempt logged for learning

# 5. Result returned
print(result['content'])  # "Aluminum cleans well with laser..."
print(result['ai_score'])  # 25 (under threshold of 30)
print(result['attempt'])   # 1 (success on first try!)
```

---

## 📊 Key Data Flows

### **Parameter Flow: First Batch Iteration**
```
INITIAL PARAMETERS (3-tier fallback):

1. 🗄️ DATABASE (PRIMARY) - Most recent successful generation
   └─ Query: "WHERE success=1 AND human_score >= 20 ORDER BY human_score DESC"
   └─ Returns: Full parameter set (temp, penalties, voice_params)
   └─ GENERIC LEARNING: Uses best params from ANY material/component
   
2. 📊 SWEET SPOT (SECONDARY) - Statistical recommendations
   └─ Query: "FROM sweet_spot_recommendations ORDER BY max_human_score DESC"
   └─ Uses: MEDIAN values from top 20% performers
   └─ Threshold: Only if 110+ samples & confidence='high'/'medium'
   └─ Current Status: 110/110 samples (100%), 3 sweet spots exist
   
3. 🧮 CALCULATED (FALLBACK) - Dynamic config calculations
   └─ Used: ONLY if NO database history exists
   └─ Source: config.yaml (1-10 sliders) → dynamic_config.py (normalize)
   └─ Returns: Fresh calculations from base configuration
```

### **Parameter Updates Through Batch**
```
WITHIN-BATCH ADAPTATION (Retry Logic):
Generation fails Winston validation
  ↓
Temperature += 0.1 (more creative)
  ↓
Voice params += 0.1 (more personality)
  ↓
Max retries: 3-7 (based on ai_avoidance slider)

CROSS-BATCH LEARNING (Database Updates):
After EACH successful generation:
  ↓
Store parameters → generation_parameters table
  ↓
Store Winston score → detection_results table
  ↓
Check if sample count >= 110 (MIN_GLOBAL_SAMPLES)
  ↓
If yes: Analyze top 20%, update sweet_spot_recommendations
  ↓
Next generation AUTOMATICALLY uses learned params (Priority 1)
```

### **Learning Triggers**
```
Parameters update in response to:

1. Winston AI Scores (human_score field)
   └─ Threshold: >= 20% = "successful"
   └─ Effect: Params stored in database
   └─ Impact: Top performers influence sweet spots

2. Sample Count Milestones
   └─ 110 samples: Statistical learning begins
   └─ Sweet spot: Only updates with confidence='high'/'medium'
   └─ Current: 110/110 (threshold met, learning active)

3. Composite Quality Score (planned)
   └─ Winston (60%) + Subjective (30%) + Readability (10%)
   └─ Status: Not yet integrated
   └─ See: docs/LEARNING_INTEGRATION_QUICK_START.md
```

### **Configuration → Generation**
```
config.yaml (15 params, 1-10 scale)
  ↓
dynamic_config.py (normalize to 0.0-1.0, calculate derived values)
  ↓
voice_params dict (9 params) + enrichment_params (3) + api_params (3)
  ↓
prompt_builder.py (orchestrate all into unified prompt)
  ↓
API (Grok/GPT/Claude) with learned temperature/penalties
  ↓
Generated content
```

### **Learning Feedback Loop**
```
Generation attempt
  ↓
Success/failure + metrics (AI score, word count, etc.)
  ↓
learning/prompt_optimizer.py (analyze patterns)
  ↓
Database (store for future optimization)
  ↓
Next attempt (use learned parameters)
```

### **Quality Assurance Pipeline**
```
Generated content
  ↓
detection/advanced_detector.py (AI score)
  ↓
validation/content_validator.py (structure, length)
  ↓
evaluation/claude_evaluator.py (subjective quality)
  ↓
Feedback stored in databases
  ↓
Learning system improves future attempts
```

---

## 🎛️ Configuration Parameters (15 Total)

### **Voice Parameters (9 total)**
1. `sentence_rhythm_variation` (1-10) - Sentence length variation
2. `imperfection_tolerance` (1-10) - Natural imperfections allowed
3. `jargon_removal` (1-10) - Technical terms to plain language (FIXED Nov 16: was inverted)
4. `professional_voice` (1-10) - Casual to highly formal vocabulary
5. `author_voice_intensity` (1-10) - How strongly author personality shows
6. `personality_intensity` (1-10) - Opinion, perspective frequency
7. `engagement_style` (1-10) - Reader address rate
8. `emotional_intensity` (1-10) - Emotional language vs neutral

### **Technical Parameters (2 total)**
9. `technical_language_intensity` (1-10) - Spec density in facts
10. `context_specificity` (1-10) - Detail level in descriptions

### **Variation Parameters (2 total)**
11. `structural_predictability` (1-10) - Pattern predictability
12. `length_variation_range` (1-10) - Word count flexibility

### **AI Detection Parameters (2 total)**
13. `ai_avoidance_intensity` (1-10) - Anti-AI strategy strength
14. `humanness_intensity` (1-10) - Human believability target

**All 15 parameters** use 1-10 scale, normalized to 0.0-1.0 internally  
**Flow**: `config.yaml` → `dynamic_config.py` → `prompt_builder.py` → API  
**Storage**: Database tracks all 15 + derived values (temperature, penalties)  
**Learning**: Sweet spots calculated from top 20% performers (need 110+ samples)

---

## 🔧 Key Files Deep Dive

### **`unified_orchestrator.py`** (~500 lines)
**Purpose**: Master coordinator for entire generation pipeline

**Key Methods**:
- `generate()` - Main entry point, orchestrates all stages
- `_run_integrity_check()` - Pre-generation validation
- `_optimize_parameters()` - Apply self-learning
- `_generate_with_retry()` - Retry logic with exponential backoff
- `_detect_ai()` - AI detection pipeline
- `_log_attempt()` - Learning system feedback

**Dependencies**: Config, VoiceLoader, DataEnricher, PromptBuilder, API clients, Detectors, Validators, Learning system

### **`prompt_builder.py`** (~610 lines)
**Purpose**: Orchestrates all 14 parameters into unified prompt

**Current Architecture**: Scattered parameter logic (being modularized)
**Future Architecture**: Orchestrates parameter modules from `/parameters`

**Key Methods**:
- `build_unified_prompt()` - Main prompt assembly
- `_load_anti_ai_rules()` - Load anti-AI guidance
- `_load_component_template()` - Component-specific prompts

### **`dynamic_config.py`** (~535 lines)
**Purpose**: Calculates all technical parameters from user sliders

**Key Methods**:
- `calculate_temperature()` - Dynamic temperature based on creativity factors
- `calculate_voice_parameters()` - Normalize 14 params to 0.0-1.0
- `calculate_enrichment_params()` - Technical intensity, context level
- `get_all_generation_params()` - One-stop param retrieval

### **`integrity_checker.py`** (~380 lines)
**Purpose**: Validates system before every generation (fail-fast)

**Runs 17 checks**:
1. Config slider ranges (1-10)
2. Normalization accuracy
3. Parameter ranges
4. Parameter completeness (all 14)
5. Propagation chain
6. Cache key strategy
7. Hardcoded value detection
8. Claude evaluator presence
9. Winston integration
10. Learning system integration
11. Training data availability
12-17. Additional system checks

---

## 🚀 Performance Characteristics

### **Generation Speed**
- **Config loading**: <1ms (cached)
- **Voice loading**: ~5ms (cached)
- **Prompt building**: ~10ms
- **API call**: 2-8 seconds (depends on provider)
- **AI detection**: ~50ms
- **Validation**: ~5ms
- **Total**: ~3-10 seconds per generation

### **Learning Impact**
- **First attempt success rate**: ~60% (without learning)
- **With learning**: ~85% (after 50+ samples per material)
- **Temperature optimization**: Improves success by ~15%
- **Prompt optimization**: Improves success by ~10%

### **Quality Metrics**
- **AI detection threshold**: 30 (scores above = AI-like)
- **Average AI score**: 18-25 (well below threshold)
- **Word count accuracy**: ±10% of target
- **Validation pass rate**: ~92%

---

## 🔮 Future Enhancements

### **Phase 2: Parameter Modularization** (In Progress)
- Move parameter logic to `/parameters` modules
- YAML-based preset prompts
- Simplified `prompt_builder.py` (~200 lines vs 610)
- See: `MODULAR_PARAMETERS_PHASE1_COMPLETE.md`

### **Phase 3: Advanced Learning**
- Material-specific parameter learning
- Automatic prompt A/B testing
- Real-time temperature adjustment
- Pattern-based failure prevention

### **Phase 4: Multi-Model Support**
- Parallel generation with multiple models
- Best-of-N selection
- Model-specific parameter optimization
- Cost/quality trade-off balancing

---

## 📚 Related Documentation

- **Configuration**: `docs/configuration/PARAMETER_REFERENCE.md`
- **Parameter Normalization**: `PARAMETER_NORMALIZATION_COMPLETE.md`
- **Modular Parameters**: `MODULAR_PARAMETERS_PHASE1_COMPLETE.md`
- **Learning System**: `SELF_LEARNING_SYSTEM_OPERATIONAL.md`
- **Integrity Checks**: `SYSTEM_INTEGRITY_MODULE_COMPLETE.md`
- **API Clients**: `docs/api/ERROR_HANDLING.md`

---

## 🎯 Key Takeaways

1. **`/processing` is the generation engine** - Everything flows through here
2. **14 parameters orchestrated** - All inject guidance into unified prompt
3. **Self-learning system** - Continuously improves from feedback
4. **Fail-fast validation** - 17 integrity checks before every generation
5. **Quality pipeline** - Detection → Validation → Evaluation
6. **Modular architecture** - Each stage independent, testable, replaceable

**The `/processing` module transforms user intent (config) + raw data (materials) into high-quality, AI-resistant content through a sophisticated, self-optimizing pipeline.**
