# Scoring System End-to-End Flow

**Complete data flow from generation → evaluation → scoring → storage → learning**

Last Updated: November 16, 2025

---

## 🎯 Overview

The scoring system captures comprehensive quality metrics throughout the generation pipeline, stores them in a linked database, and uses them for continuous learning and parameter optimization.

**Three Quality Dimensions**:
1. **Grok humanness Score** (0-100) - AI detection avoidance
2. **Subjective Score** (0-10) - Human-like quality assessment  
3. **Readability Score** (0-100) - Text clarity and flow

**Composite Quality Score** = Grok (60%) + Subjective (30%) + Readability (10%)

---

## 📊 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    1. PRE-GENERATION PHASE                          │
└─────────────────────────────────────────────────────────────────────┘

UnifiedOrchestrator.generate()
    ↓
_get_adaptive_parameters()
    ↓
┌──────────────────────────────────────┐
│ Query: Best Previous Parameters      │
│                                      │
│ SELECT p.* FROM generation_parameters│
│ JOIN detection_results r             │
│ WHERE material = ? AND component = ? │
│ AND r.success = 1                    │
│ ORDER BY r.human_score DESC          │
│ LIMIT 1                              │
└──────────────────────────────────────┘
    ↓
Parameters Retrieved:
  • temperature
  • frequency_penalty
  • presence_penalty
  • voice_params (11 parameters)
  • enrichment_params (3 parameters)
    ↓
Apply to generation config
    ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    2. GENERATION PHASE                              │
└─────────────────────────────────────────────────────────────────────┘

Build prompt with enrichment
    ↓
Call API with parameters
    ↓
Generated text returned
    ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    3. GROK EVALUATION                               │
└─────────────────────────────────────────────────────────────────────┘

GrokHumannessRuntimeEvaluator.evaluate()
    ↓
┌──────────────────────────────────────┐
│ Grok API Call                     │
│                                      │
│ POST /api/detect                     │
│ Body: { text: generated_text }      │
└──────────────────────────────────────┘
    ↓
Grok Response:
  {
    "ai_score": 0.15,        # 0-1 scale
    "human_score": 0.85,     # 0-1 scale (inverted)
    "readability_score": 72, # 0-100 scale
    "sentences": [           # Per-sentence analysis
      {"text": "...", "score": 0.92},
      {"text": "...", "score": 0.78}
    ]
  }
    ↓
Convert to 0-100 scale:
  • winston_score = ai_score * 100    # 15
  • human_score = human_score * 100   # 85
  • readability_score = 72            # Already 0-100
    ↓
WinstonFeedbackDatabase.log_detection()
    ↓
┌──────────────────────────────────────┐
│ INSERT INTO detection_results        │
│                                      │
│ Fields:                              │
│   - material                         │
│   - component_type                   │
│   - generated_text                   │
│   - human_score (0-1)                │
│   - ai_score (0-1)                   │
│   - readability_score (0-100)        │
│   - composite_quality_score (NULL)   │ ← NOT YET CALCULATED
│   - subjective_evaluation_id (NULL)  │ ← NOT YET LINKED
│   - success (boolean)                │
│   - temperature                      │
│   - attempt_number                   │
│   - timestamp                        │
│                                      │
│ RETURNS: detection_id                │
└──────────────────────────────────────┘
    ↓
detection_id = 42
    ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    4. PARAMETER LOGGING                             │
└─────────────────────────────────────────────────────────────────────┘

WinstonFeedbackDatabase.log_parameters()
    ↓
┌──────────────────────────────────────┐
│ INSERT INTO generation_parameters    │
│                                      │
│ Fields (20+ parameters):             │
│   - detection_result_id (FK)         │ ← Links to detection_results
│   - temperature                      │
│   - frequency_penalty                │
│   - presence_penalty                 │
│   - trait_frequency                  │
│   - opinion_rate                     │
│   - reader_address_rate              │
│   - colloquialism_frequency          │
│   - structural_predictability        │
│   - emotional_tone                   │
│   - imperfection_tolerance           │
│   - sentence_rhythm_variation        │
│   - technical_intensity              │
│   - context_detail_level             │
│   - engagement_level                 │
│   - detection_threshold              │
│   - readability_min                  │
│   - readability_max                  │
│   - grammar_strictness               │
│   - confidence_high                  │
│   - confidence_medium                │
│   - param_hash (for deduplication)   │
│   - timestamp                        │
│                                      │
│ RETURNS: param_id                    │
└──────────────────────────────────────┘
    ↓
param_id = 123
    ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    5. SUBJECTIVE EVALUATION (Optional)              │
└─────────────────────────────────────────────────────────────────────┘

SubjectiveEvaluator.evaluate()
    ↓
┌──────────────────────────────────────┐
│ Claude/Grok API Call                 │
│                                      │
│ Evaluate across 6 dimensions:        │
│   1. Clarity                         │
│   2. Professionalism                 │
│   3. Technical Accuracy              │
│   4. Human-likeness                  │
│   5. Engagement                      │
│   6. Jargon-free                     │
└──────────────────────────────────────┘
    ↓
SubjectiveEvaluationResult:
  {
    "overall_score": 8.2,              # 0-10 scale
    "dimension_scores": [
      {"dimension": "clarity", "score": 9.0},
      {"dimension": "professionalism", "score": 8.5},
      ...
    ],
    "strengths": ["Clear", "Engaging"],
    "weaknesses": ["Too technical"],
    "recommendations": ["Simplify terms"]
  }
    ↓
WinstonFeedbackDatabase.log_subjective_evaluation()
    ↓
┌──────────────────────────────────────┐
│ INSERT INTO subjective_evaluations   │
│                                      │
│ Fields:                              │
│   - topic (material name)            │
│   - component_type                   │
│   - generated_text                   │
│   - overall_score (0-10)             │
│   - clarity_score                    │
│   - professionalism_score            │
│   - technical_accuracy_score         │
│   - human_likeness_score             │
│   - engagement_score                 │
│   - jargon_free_score                │
│   - passes_quality_gate              │
│   - strengths (JSON)                 │
│   - weaknesses (JSON)                │
│   - recommendations (JSON)           │
│   - generation_parameters_id (FK)    │ ← Links to generation_parameters
│   - timestamp                        │
│                                      │
│ RETURNS: subjective_eval_id          │
└──────────────────────────────────────┘
    ↓
subjective_eval_id = 67
    ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    6. COMPOSITE SCORING (NEW)                       │
└─────────────────────────────────────────────────────────────────────┘

CompositeScorer.calculate()
    ↓
INPUTS:
  • winston_score = 85 (from detection_results.human_score * 100)
  • subjective_score = 8.2 (from subjective_evaluations.overall_score)
  • readability_score = 72 (from detection_results.readability_score)
    ↓
CALCULATION:
  composite_score = (
      winston_score * 0.6 +           # 85 * 0.6 = 51.0
      subjective_score * 10 * 0.3 +   # 8.2 * 10 * 0.3 = 24.6
      readability_score * 0.1          # 72 * 0.1 = 7.2
  )
  = 51.0 + 24.6 + 7.2 = 82.8
    ↓
composite_score = 82.8 (0-100 scale)
    ↓
WEIGHT REDISTRIBUTION (if dimensions missing):
  If subjective_score is None:
    # Redistribute 30% weight to Grok (60% → 75%)
    composite_score = (
        winston_score * 0.75 +
        readability_score * 0.25
    )
    ↓
UPDATE detection_results:
┌──────────────────────────────────────┐
│ UPDATE detection_results             │
│ SET composite_quality_score = 82.8,  │
│     subjective_evaluation_id = 67    │
│ WHERE id = 42                        │
└──────────────────────────────────────┘
    ↓
UPDATE subjective_evaluations:
┌──────────────────────────────────────┐
│ UPDATE subjective_evaluations        │
│ SET generation_parameters_id = 123   │
│ WHERE id = 67                        │
└──────────────────────────────────────┘
    ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    7. SWEET SPOT ANALYSIS                           │
└─────────────────────────────────────────────────────────────────────┘

SweetSpotAnalyzer.update_sweet_spot()
    ↓
┌──────────────────────────────────────┐
│ Query Recent Successful Generations  │
│                                      │
│ SELECT AVG(temperature),             │
│        AVG(frequency_penalty),       │
│        AVG(presence_penalty),        │
│        COUNT(*) as sample_count,     │
│        AVG(human_score)              │
│ FROM generation_parameters p         │
│ JOIN detection_results r             │
│   ON p.detection_result_id = r.id   │
│ WHERE r.success = 1                  │
│   AND r.material = '*'               │ ← Global scope
│   AND r.component_type = '*'         │
│   AND r.timestamp > (NOW - 30 days) │
└──────────────────────────────────────┘
    ↓
Statistical Analysis:
  • Calculate mean, median, std dev for each parameter
  • Determine confidence level based on sample size
  • Identify optimal parameter ranges
    ↓
┌──────────────────────────────────────┐
│ INSERT/UPDATE sweet_spot_recommendations │
│                                      │
│ Fields:                              │
│   - material = '*'                   │ ← Global sweet spot
│   - component_type = '*'             │
│   - optimal_temperature              │
│   - optimal_frequency_penalty        │
│   - optimal_presence_penalty         │
│   - sample_count                     │
│   - confidence_level ('high'/'medium'/'low') │
│   - avg_human_score                  │
│   - std_dev_human_score              │
│   - last_updated                     │
└──────────────────────────────────────┘
    ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    8. POST-GENERATION INTEGRITY CHECKS              │
└─────────────────────────────────────────────────────────────────────┘

IntegrityChecker.run_post_generation_checks()
    ↓
Check 1: Detection Result Logged?
  ✅ Query detection_results for recent entry
    ↓
Check 2: Parameters Logged?
  ✅ Query generation_parameters with detection_result_id FK
    ↓
Check 3: Sweet Spot Updated?
  ✅ Query sweet_spot_recommendations for global entry
    ↓
Check 4: Subjective Evaluation Logged?
  ⚠️  Query subjective_evaluations (optional)
    ↓
RESULTS:
  ✅ Detection Logged (ID: 42, human: 85%, AI: 15%)
  ✅ Parameters Logged (ID: 123, temp: 0.8)
  ✅ Sweet Spot Updated (10 samples, high confidence)
  ⚠️  Subjective Evaluation Logged (ID: 67, score: 8.2/10)
    ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    9. CONTINUOUS LEARNING (Future Use)              │
└─────────────────────────────────────────────────────────────────────┘

GranularParameterCorrelator.analyze_all_parameters()
    ↓
┌──────────────────────────────────────┐
│ For Each of 20+ Parameters:         │
│                                      │
│ 1. Calculate Spearman correlation    │
│    between parameter value and       │
│    composite_quality_score           │
│                                      │
│ 2. Determine statistical significance│
│    (p-value < 0.05)                  │
│                                      │
│ 3. Calculate confidence interval     │
│    (bootstrap method)                │
│                                      │
│ 4. Detect relationship type          │
│    (linear, polynomial, logarithmic) │
│                                      │
│ 5. Find optimal range                │
│    (where scores consistently high)  │
│                                      │
│ 6. Calculate sensitivity             │
│    (score change per 1% param change)│
└──────────────────────────────────────┘
    ↓
Results (example):
  {
    "temperature": ParameterCorrelation(
      correlation_coefficient = 0.65,     # Strong positive
      p_value = 0.003,                    # Significant
      strength = "strong",
      direction = "positive",
      sample_count = 50,
      confidence_interval = (0.45, 0.80),
      relationship_type = "linear",
      optimal_range = (0.8, 1.2),
      sensitivity = 1.5  # +1.5 points per 1% increase
    ),
    "frequency_penalty": ParameterCorrelation(
      correlation_coefficient = -0.52,    # Moderate negative
      p_value = 0.012,
      strength = "moderate",
      direction = "negative",
      ...
    )
  }
    ↓
analyze_interactions()
    ↓
┌──────────────────────────────────────┐
│ Detect Parameter Synergies           │
│                                      │
│ For top parameter pairs:             │
│   Calculate interaction_term =       │
│     param1_value * param2_value      │
│                                      │
│   Correlate with composite_score     │
│                                      │
│   Identify synergistic combinations  │
└──────────────────────────────────────┘
    ↓
Results (example):
  [
    ParameterInteraction(
      parameters = ["temperature", "trait_frequency"],
      interaction_strength = 0.48,
      combined_effect = 0.15,  # Synergy effect
      optimal_combination = {
        "temperature": 1.1,
        "trait_frequency": 0.7
      },
      sample_count = 45
    )
  ]
    ↓
generate_adjustment_recommendations()
    ↓
┌──────────────────────────────────────┐
│ Calculate Optimal Adjustments        │
│                                      │
│ For each parameter:                  │
│   current_value = get_current()      │
│   optimal_value = calculate_from(    │
│     correlation,                     │
│     sensitivity,                     │
│     optimal_range,                   │
│     target_improvement = 5.0         │
│   )                                  │
│                                      │
│   expected_impact =                  │
│     abs(optimal - current) *         │
│     sensitivity                      │
└──────────────────────────────────────┘
    ↓
Recommendations (example):
  [
    {
      "parameter": "temperature",
      "current_value": 0.8,
      "recommended_value": 1.0,
      "change": +0.2,
      "expected_impact": +3.0,  # Points improvement
      "confidence": 0.997,      # 1 - p_value
      "correlation_strength": "strong",
      "optimal_range": (0.8, 1.2),
      "reasoning": "Increase temperature (strong +0.65 correlation). Expected: 3.0 points per 1% change."
    },
    {
      "parameter": "frequency_penalty",
      "current_value": 0.3,
      "recommended_value": 0.2,
      "change": -0.1,
      "expected_impact": +2.5,
      "confidence": 0.988,
      "correlation_strength": "moderate",
      "reasoning": "Decrease frequency_penalty (moderate -0.52 correlation)..."
    }
  ]
    ↓
Apply recommendations in next generation cycle
    ↓
```

---

## 🗄️ Database Schema Relationships

```
┌──────────────────────────────────┐
│   detection_results              │
│  ────────────────────────────    │
│  PK: id                          │
│  material                        │
│  component_type                  │
│  generated_text                  │
│  human_score (0-1)               │
│  ai_score (0-1)                  │
│  readability_score (0-100)       │
│  composite_quality_score (0-100) │ ← NEW: Unified metric
│  subjective_evaluation_id (FK)   │ ← NEW: Links to subjective eval
│  success                         │
│  temperature                     │
│  attempt_number                  │
│  timestamp                       │
└──────────────────────────────────┘
          ↑                 ↓
          │                 │
          │ FK              │ FK
          │                 │
┌─────────┴──────────────┐  │  ┌──────────────────────────────────┐
│ generation_parameters  │  └──│ subjective_evaluations           │
│ ────────────────────── │     │ ──────────────────────────────── │
│ PK: id                 │     │ PK: id                           │
│ detection_result_id ───┼─────│ generation_parameters_id (FK) ───┼─┐
│ temperature            │     │ topic                            │ │
│ frequency_penalty      │     │ component_type                   │ │
│ presence_penalty       │     │ generated_text                   │ │
│ trait_frequency        │     │ overall_score (0-10)             │ │
│ opinion_rate           │     │ clarity_score                    │ │
│ ... (20+ parameters)   │     │ professionalism_score            │ │
│ param_hash             │     │ technical_accuracy_score         │ │
│ timestamp              │     │ human_likeness_score             │ │
└────────────────────────┘     │ engagement_score                 │ │
                               │ jargon_free_score                │ │
                               │ passes_quality_gate              │ │
                               │ strengths (JSON)                 │ │
                               │ weaknesses (JSON)                │ │
                               │ recommendations (JSON)           │ │
                               │ timestamp                        │ │
                               └──────────────────────────────────┘ │
                                                                     │
                ┌────────────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────┐
│ sweet_spot_recommendations       │
│ ──────────────────────────────── │
│ PK: (material, component_type)   │
│ material = '*'                   │ ← Global scope
│ component_type = '*'             │
│ optimal_temperature              │
│ optimal_frequency_penalty        │
│ optimal_presence_penalty         │
│ sample_count                     │
│ confidence_level                 │
│ avg_human_score                  │
│ std_dev_human_score              │
│ last_updated                     │
└──────────────────────────────────┘
```

---

## 📥 Inputs and Outputs

### 1. UnifiedOrchestrator.generate()
**Inputs**:
- `identifier`: Material name (e.g., "Aluminum")
- `component_type`: Component type (e.g., "micro")
- `api_client`: Grok API client

**Outputs**:
```python
{
    'success': True,
    'content': "Generated micro text",
    'text': "Full generated text",
    'attempts': 1,
    'ai_score': 0.15,        # 0-1 scale
    'human_score': 0.85,     # 0-1 scale
    'readability': {
        'status': 'readable',
        'is_readable': True
    }
}
```

### 2. WinstonIntegration.detect_and_log()
**Inputs**:
- `text`: Generated content
- `material`: Material name
- `component_type`: Component type
- `temperature`: Generation temperature
- `attempt`: Attempt number
- `max_attempts`: Maximum attempts
- `ai_threshold`: Success threshold

**Outputs**:
```python
{
    'ai_score': 0.15,              # 0-1 scale
    'detection': {                 # Full Grok response
        'ai_score': 0.15,
        'human_score': 0.85,
        'readability_score': 72,
        'sentences': [...]
    },
    'detection_id': 42,            # Database ID
    'failure_analysis': {...},     # If failed
    'method': 'grok'            # Or 'pattern_only'
}
```

### 3. WinstonFeedbackDatabase.log_detection()
**Inputs**:
- `material`: Material name
- `component_type`: Component type
- `generated_text`: Full text
- `winston_result`: Grok API response
- `temperature`: Temperature used
- `attempt`: Attempt number
- `success`: Boolean
- `failure_analysis`: Optional analysis

**Outputs**:
- Returns `detection_id` (integer)

### 4. WinstonFeedbackDatabase.log_parameters() *(Not shown in current flow - needs integration)*
**Inputs**:
- `detection_result_id`: FK to detection_results
- All 20+ generation parameters

**Outputs**:
- Returns `param_id` (integer)

### 5. SubjectiveEvaluator.evaluate()
**Inputs**:
- `content`: Generated text
- `material_name`: Material name
- `component_type`: Component type
- `context`: Optional additional context

**Outputs**:
```python
SubjectiveEvaluationResult(
    overall_score = 8.2,           # 0-10
    dimension_scores = [
        SubjectiveScore(
            dimension = EvaluationDimension.CLARITY,
            score = 9.0,
            feedback = "Very clear",
            suggestions = [...]
        ),
        ...
    ],
    strengths = ["Clear", "Engaging"],
    weaknesses = ["Too technical"],
    recommendations = ["Simplify"],
    passes_quality_gate = True,
    evaluation_time_ms = 1500,
    raw_response = "..."
)
```

### 6. WinstonFeedbackDatabase.log_subjective_evaluation()
**Inputs**:
- `topic`: Material name
- `component_type`: Component type
- `generated_text`: Full text
- `evaluation_result`: SubjectiveEvaluationResult object
- `domain`: "materials"
- `author_id`: Optional
- `attempt_number`: Optional

**Outputs**:
- Returns `subjective_eval_id` (integer)

### 7. CompositeScorer.calculate()
**Inputs**:
- `winston_score`: 0-100 (from human_score * 100)
- `subjective_score`: 0-10 (from overall_score)
- `readability_score`: 0-100

**Outputs**:
- Returns `composite_score` (0-100 float)

### 8. GranularParameterCorrelator.analyze_all_parameters()
**Inputs**:
- `target_metric`: 'composite_quality_score'
- `min_score`: Minimum score threshold (e.g., 50.0)

**Outputs**:
```python
{
    "temperature": ParameterCorrelation(
        parameter_name = "temperature",
        correlation_coefficient = 0.65,
        p_value = 0.003,
        strength = "strong",
        direction = "positive",
        sample_count = 50,
        confidence_interval = (0.45, 0.80),
        relationship_type = "linear",
        optimal_range = (0.8, 1.2),
        sensitivity = 1.5
    ),
    ...
}
```

### 9. GranularParameterCorrelator.generate_adjustment_recommendations()
**Inputs**:
- `correlations`: Dict of ParameterCorrelation objects
- `current_params`: Dict of current parameter values
- `target_improvement`: Target score increase (e.g., 5.0)

**Outputs**:
```python
[
    {
        'parameter': 'temperature',
        'current_value': 0.8,
        'recommended_value': 1.0,
        'change': +0.2,
        'expected_impact': +3.0,
        'confidence': 0.997,
        'correlation_strength': 'strong',
        'optimal_range': (0.8, 1.2),
        'reasoning': "Increase temperature..."
    },
    ...
]
```

---

## 🔄 Current Integration Status

### ✅ **IMPLEMENTED**
1. **Grok Detection** - Full integration with database logging
2. **Parameter Logging** - All 20+ parameters stored per generation
3. **Sweet Spot Analysis** - Global parameter optimization
4. **Subjective Evaluation** - Human-like quality assessment
5. **CompositeScorer** - Unified quality metric calculation
6. **GranularParameterCorrelator** - Fine-grained parameter analysis
7. **Database Schema** - Foreign keys linking all tables
8. **Post-Generation Checks** - Integrity verification

### ⏳ **PENDING INTEGRATION**
1. **Automatic Composite Score Calculation** - Need to call `CompositeScorer.calculate()` after detection + subjective eval
2. **Automatic Foreign Key Updates** - Need to link `subjective_evaluation_id` in detection_results
3. **Parameter Correlation in Pipeline** - Need to integrate `GranularParameterCorrelator` into orchestrator
4. **Automated Recommendations** - Need to apply correlation findings to parameter selection

---

## 🚀 Next Steps for Full Integration

### Phase 2A: Integrate Composite Scoring into Pipeline

**File**: `generation/core/evaluated_generator.py`

```python
# After Grok detection (line ~360)
if readability['is_readable']:
    # Calculate composite score if subjective eval available
    from postprocessing.evaluation import CompositeScorer
    
    composite_scorer = CompositeScorer()
    
    # Get subjective score if available
    subjective_score = None
    if self.config.get('enable_subjective_evaluation', False):
        from postprocessing.evaluation import SubjectiveEvaluator
        evaluator = SubjectiveEvaluator(api_client=self.api_client)
        
        subjective_result = evaluator.evaluate(
            content=text,
            material_name=identifier,
            component_type=component_type
        )
        
        # Log subjective evaluation
        subjective_eval_id = self.grok.feedback_db.log_subjective_evaluation(
            topic=identifier,
            component_type=component_type,
            generated_text=text,
            evaluation_result=subjective_result,
            domain="materials"
        )
        
        subjective_score = subjective_result.overall_score
    else:
        subjective_eval_id = None
    
    # Calculate composite score
    composite_score = composite_scorer.calculate(
        winston_score=human_score * 100,  # Convert 0-1 to 0-100
        subjective_score=subjective_score,
        readability_score=readability['score']
    )
    
    # Update detection result with composite score and subjective link
    self.grok.feedback_db.update_detection_composite(
        detection_id=detection_result['detection_id'],
        composite_quality_score=composite_score,
        subjective_evaluation_id=subjective_eval_id
    )
    
    logger.info(f"📊 Composite quality score: {composite_score:.1f}/100")
```

### Phase 2B: Add Database Update Methods

**File**: `postprocessing/detection/winston_feedback_db.py`

```python
def update_detection_composite(
    self,
    detection_id: int,
    composite_quality_score: float,
    subjective_evaluation_id: Optional[int] = None
) -> None:
    """Update detection result with composite score and subjective eval link."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE detection_results
            SET composite_quality_score = ?,
                subjective_evaluation_id = ?
            WHERE id = ?
        """, (composite_quality_score, subjective_evaluation_id, detection_id))
        
        conn.commit()
    
    logger.info(f"📊 Updated detection #{detection_id} with composite score {composite_quality_score:.1f}")
```

### Phase 3: Integrate Correlation Analysis

Add periodic correlation analysis to optimize parameters:

```python
# In UnifiedOrchestrator or separate script
def analyze_and_optimize_parameters(self):
    """Run correlation analysis and generate recommendations."""
    from learning.validation_winston_correlator import ValidationWinstonCorrelator
    
    correlator = GranularParameterCorrelator(
        db_path='data/z-beam.db',
        min_samples=30,
        significance_level=0.05
    )
    
    # Analyze all parameters
    correlations = correlator.analyze_all_parameters(
        target_metric='composite_quality_score',
        min_score=60.0
    )
    
    # Get current parameters
    current_params = self.dynamic_config.get_all_generation_params('micro')
    
    # Generate recommendations
    recommendations = correlator.generate_adjustment_recommendations(
        correlations,
        current_params,
        target_improvement=5.0
    )
    
    # Log recommendations
    for rec in recommendations[:5]:  # Top 5
        logger.info(
            f"💡 {rec['parameter']}: {rec['current_value']} → {rec['recommended_value']} "
            f"(expected: +{rec['expected_impact']:.1f} points)"
        )
    
    return recommendations
```

---

## 📊 Key Metrics Tracked

| Metric | Scale | Source | Usage |
|--------|-------|--------|-------|
| **Grok humanness Score** | 0-100 | Grok API (ai_score * 100) | AI detection avoidance |
| **Grok Human Score** | 0-100 | Grok API (human_score * 100) | Human-like quality |
| **Readability Score** | 0-100 | Grok API | Text clarity |
| **Subjective Overall** | 0-10 | SubjectiveEvaluator | Comprehensive quality |
| **Composite Score** | 0-100 | CompositeScorer | Unified optimization target |
| **Parameter Correlations** | -1 to +1 | GranularParameterCorrelator | Parameter tuning |

---

## 🎯 Benefits of Complete Integration

1. **Holistic Optimization** - Not just AI detection, but overall quality
2. **Precise Tuning** - 0.01 increment adjustments based on statistical analysis
3. **Relationship Discovery** - Non-linear patterns and parameter synergies
4. **Statistical Confidence** - P-values and confidence intervals prevent false signals
5. **Actionable Recommendations** - Automated suggestions with expected impact
6. **Full Traceability** - Every quality score links to exact parameters used
7. **Continuous Learning** - System improves with every generation

---

**Last Updated**: November 16, 2025  
**Status**: Phase 1-2 Complete (Database + Scoring), Integration Pending
