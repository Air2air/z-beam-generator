# Scoring Module - Comprehensive Quality Assessment & Parameter Correlation

**Location**: `postprocessing/evaluation/` (with correlation analysis in `learning/`)

The Scoring Module provides highly granular quality assessment and parameter correlation analysis, enabling precise parameter tuning and relationship discovery for optimal content generation.

---

## 🎯 Core Components

### 1. CompositeScorer
**File**: `postprocessing/evaluation/composite_scorer.py`

Calculates unified quality metric combining multiple dimensions:
- **Grok Humanness Score** (60% weight) - AI detection avoidance
- **Subjective Score** (30% weight) - Human quality assessment
- **Readability Score** (10% weight) - Text clarity and flow

**Key Features**:
- Configurable weights (customizable per use case)
- Automatic weight redistribution when dimensions missing
- Score interpretation (excellent/good/acceptable/poor/failing)
- Database integration for historical tracking

**Usage**:
```python
from postprocessing.evaluation import CompositeScorer

scorer = CompositeScorer(
    winston_weight=0.6,
    subjective_weight=0.3,
    readability_weight=0.1
)

# Calculate from individual scores
composite = scorer.calculate(
    winston_score=85.5,
    subjective_score=8.2,
    readability_score=72.0
)

# Or from database result
composite = scorer.calculate_from_detection_result(detection_result)

# Interpret quality level
quality = scorer.interpret_score(composite)  # "good", "excellent", etc.
```

---

### 2. GranularParameterCorrelator
**File**: `learning/granular_correlator.py`

Performs fine-grained correlation analysis between parameters and quality metrics.

**Key Features**:
- **Per-parameter correlation**: Spearman + Pearson coefficients
- **Statistical significance**: P-values and confidence intervals
- **Relationship detection**: Linear, polynomial, logarithmic, exponential
- **Optimal range identification**: Where scores are consistently high
- **Sensitivity analysis**: Score change per 1% parameter change
- **Interaction detection**: 2-way and 3-way parameter synergies

**20+ Parameters Tracked**:
```python
# API Parameters
- temperature (0.0-2.0)
- frequency_penalty (0.0-2.0)
- presence_penalty (0.0-2.0)

# Voice Parameters
- trait_frequency (0.0-1.0)
- opinion_rate (0.0-1.0)
- reader_address_rate (0.0-1.0)
- colloquialism_frequency (0.0-1.0)
- structural_predictability (0.0-1.0)
- emotional_tone (0.0-1.0)
- imperfection_tolerance (0.0-1.0)
- sentence_rhythm_variation (0.0-1.0)

# Enrichment Parameters
- technical_intensity (1-3)
- context_detail_level (1-3)
- engagement_level (1-3)

# Validation Parameters
- detection_threshold (0.0-1.0)
- readability_min (0.0-100.0)
- readability_max (0.0-100.0)
- grammar_strictness (0.0-1.0)
- confidence_high (0.0-1.0)
- confidence_medium (0.0-1.0)
```

**Usage**:
```python
from learning import GranularParameterCorrelator

correlator = GranularParameterCorrelator(
    db_path='data/z-beam.db',
    min_samples=30,
    significance_level=0.05
)

# Analyze all parameters
correlations = correlator.analyze_all_parameters(
    target_metric='composite_quality_score',
    min_score=50.0
)

# Results include:
for name, corr in correlations.items():
    print(f"{name}:")
    print(f"  Correlation: {corr.correlation_coefficient:+.3f}")
    print(f"  Strength: {corr.strength}")
    print(f"  P-value: {corr.p_value:.4f}")
    print(f"  Sensitivity: {corr.sensitivity:.4f} points per 1% change")
    print(f"  Optimal range: {corr.optimal_range}")
    print(f"  Relationship: {corr.relationship_type}")
```

---

### 3. SubjectiveEvaluator
**File**: `postprocessing/evaluation/subjective_evaluator.py`

Human-like quality assessment across multiple dimensions.

**Evaluation Dimensions**:
- Naturalness & flow
- Engagement & interest
- Technical accuracy
- Readability
- Overall impression

**Usage**:
```python
from postprocessing.evaluation import SubjectiveEvaluator

evaluator = SubjectiveEvaluator()
result = evaluator.evaluate(content, material_name)

print(f"Overall Score: {result.overall_score}/10")
print(f"Naturalness: {result.naturalness}/10")
print(f"Comments: {result.comments}")
```

---

## 📊 Data Flow

```
Generation Parameters
        ↓
Content Generation
        ↓
Quality Evaluation
    ├── Grok Humanness Score (0-100)
    ├── Subjective Score (0-10)
    └── Readability Score (0-100)
        ↓
Composite Scorer
        ↓
Composite Quality Score (0-100)
        ↓
Database Storage (detection_results)
        ↓
Granular Correlator
    ├── Per-Parameter Analysis
    ├── Interaction Detection
    └── Adjustment Recommendations
        ↓
Sweet Spot Updates
```

---

## 🔗 Database Schema

### Enhanced Tables

**detection_results**:
```sql
CREATE TABLE detection_results (
    id INTEGER PRIMARY KEY,
    composite_quality_score REAL,  -- NEW: Unified metric
    subjective_evaluation_id INTEGER,  -- NEW: Link to subjective eval
    winston_score REAL,
    readability_score REAL,
    -- ... other fields
    FOREIGN KEY (subjective_evaluation_id) 
        REFERENCES subjective_evaluations(id)
);

CREATE INDEX idx_detection_composite 
    ON detection_results(composite_quality_score);
CREATE INDEX idx_detection_subjective 
    ON detection_results(subjective_evaluation_id);
```

**subjective_evaluations**:
```sql
CREATE TABLE subjective_evaluations (
    id INTEGER PRIMARY KEY,
    generation_parameters_id INTEGER,  -- NEW: Link to params
    overall_score REAL,
    naturalness REAL,
    engagement REAL,
    -- ... other fields
    FOREIGN KEY (generation_parameters_id) 
        REFERENCES generation_parameters(id)
);

CREATE INDEX idx_subjective_eval_params 
    ON subjective_evaluations(generation_parameters_id);
```

**generation_parameters**:
```sql
CREATE TABLE generation_parameters (
    id INTEGER PRIMARY KEY,
    detection_result_id INTEGER,
    temperature REAL,
    frequency_penalty REAL,
    presence_penalty REAL,
    trait_frequency REAL,
    -- ... all 20+ parameters
);
```

---

## 🎯 Use Cases

### 1. Find Best Parameters for Current Material
```python
correlator = GranularParameterCorrelator(db_path)
correlations = correlator.analyze_all_parameters(
    target_metric='composite_quality_score',
    min_score=70.0
)

# Get top 5 most impactful parameters
top_params = sorted(
    correlations.items(),
    key=lambda x: abs(x[1].correlation_coefficient),
    reverse=True
)[:5]

for name, corr in top_params:
    print(f"{name}: {corr.correlation_coefficient:+.3f} correlation")
    print(f"  Optimal range: {corr.optimal_range}")
```

### 2. Get Adjustment Recommendations
```python
current_params = {
    'temperature': 0.8,
    'frequency_penalty': 0.3,
    'trait_frequency': 0.7,
    # ... all parameters
}

recommendations = correlator.generate_adjustment_recommendations(
    correlations,
    current_params,
    target_improvement=5.0  # Want 5-point improvement
)

for rec in recommendations[:5]:  # Top 5 recommendations
    print(f"{rec['parameter']}: {rec['current_value']} → {rec['recommended_value']}")
    print(f"  Expected impact: +{rec['expected_impact']:.2f} points")
    print(f"  Reasoning: {rec['reasoning']}")
```

### 3. Discover Parameter Interactions
```python
interactions = correlator.analyze_interactions(
    correlations,
    max_interactions=10
)

for interaction in interactions:
    print(f"{' + '.join(interaction.parameters)}:")
    print(f"  Interaction strength: {interaction.interaction_strength:.3f}")
    print(f"  Optimal combination: {interaction.optimal_combination}")
```

### 4. Calculate Composite Score
```python
scorer = CompositeScorer()

# After generation and evaluation
composite_score = scorer.calculate(
    winston_score=detection_result['score'],
    subjective_score=subjective_eval['overall_score'],
    readability_score=readability_result['score']
)

# Interpret quality
quality_level = scorer.interpret_score(composite_score)
# Returns: "excellent" (90+), "good" (75-90), "acceptable" (60-75),
#          "poor" (40-60), "failing" (<40)
```

---

## 📈 Statistical Rigor

### Correlation Strength Interpretation
- **Very Strong**: |r| ≥ 0.7
- **Strong**: |r| ≥ 0.5
- **Moderate**: |r| ≥ 0.3
- **Weak**: |r| ≥ 0.1
- **Negligible**: |r| < 0.1

### Significance Testing
- **P-value threshold**: 0.05 (configurable)
- **Confidence intervals**: 95% via bootstrap (1000 samples)
- **Minimum samples**: 30 per parameter (configurable)

### Relationship Detection
1. **Linear**: Standard Pearson correlation
2. **Polynomial**: Degree 2 fit, R² improvement >5%
3. **Logarithmic**: Log-transform correlation, R² improvement >5%
4. **Exponential**: Detected via curve fitting

---

## 🔧 Configuration

### Composite Scorer Weights
Default weights (can be customized):
```python
CompositeScorer(
    winston_weight=0.6,      # Grok humanness most important
    subjective_weight=0.3,   # Human quality second
    readability_weight=0.1   # Clarity third
)
```

### Correlator Parameters
```python
GranularParameterCorrelator(
    db_path='data/z-beam.db',
    min_samples=30,           # Minimum for reliable correlation
    significance_level=0.05   # P-value threshold
)
```

---

## 🧪 Testing

### CompositeScorer Tests
**File**: `tests/test_composite_scorer.py` (32 tests)
- Weight initialization and validation
- All dimensions present/missing scenarios
- Edge cases and boundary conditions
- Score interpretation logic

### Run Tests
```bash
# All scoring module tests
pytest tests/test_composite_scorer.py -v

# Specific test categories
pytest tests/test_composite_scorer.py::TestCompositeScorer::test_all_dimensions_perfect -v
pytest tests/test_composite_scorer.py::TestCompositeScorer::test_weight_redistribution -v
```

---

## 🚀 Integration with UnifiedOrchestrator

The scoring module integrates into the generation pipeline:

```python
# 1. Generate content
result = await self._generate_content(...)

# 2. Evaluate with Grok humanness
grok_result = await grok_detector.detect(result.content)

# 3. Evaluate subjectively
subjective_result = subjective_evaluator.evaluate(
    result.content,
    material_name
)

# 4. Calculate composite score
composite_score = composite_scorer.calculate(
    winston_score=grok_result['score'],
    subjective_score=subjective_result.overall_score,
    readability_score=readability_result['score']
)

# 5. Store everything linked via foreign keys
detection_id = db.log_detection(
    ...,
    composite_quality_score=composite_score,
    subjective_evaluation_id=subjective_eval_id
)

param_id = db.log_parameters(
    ...,
    detection_result_id=detection_id
)

subjective_id = db.log_subjective_evaluation(
    ...,
    generation_parameters_id=param_id
)

# 6. Later: Analyze correlations
correlations = correlator.analyze_all_parameters()
recommendations = correlator.generate_adjustment_recommendations(
    correlations,
    current_params,
    target_improvement=5.0
)
```

---

## 📋 Next Steps

### Phase 3: Parameter Correlation Integration
- [ ] Integrate GranularParameterCorrelator into UnifiedOrchestrator
- [ ] Add correlation analysis to post-generation reports
- [ ] Create CLI command: `--analyze-correlations`

### Phase 4: Sweet Spot Enhancement
- [ ] Expand SweetSpotAnalyzer to use composite_quality_score
- [ ] Cover all 20+ parameters (currently only 7)
- [ ] Use GranularParameterCorrelator findings

### Phase 5: Adaptive Learning Orchestrator
- [ ] Meta-learner that decides when/how to update parameters
- [ ] Automatic A/B testing for parameter changes
- [ ] Continuous optimization loop

---

## 📚 Related Documentation

- **Comprehensive Learning Integration**: `docs/proposals/COMPREHENSIVE_LEARNING_INTEGRATION.md`
- **E2E Parameter Flow**: `docs/architecture/E2E_PARAMETER_FLOW.md`
- **Parameter Schema**: `processing/schemas/parameter_schema.py`
- **Database Schema**: `postprocessing/detection/winston_feedback_db.py`

---

## 🎓 Key Insights

### Why Granular Scoring Matters
1. **Precise Tuning**: 0.01 increment adjustments enable fine optimization
2. **Relationship Discovery**: Non-linear and interaction effects revealed
3. **Statistical Confidence**: P-values and confidence intervals prevent false signals
4. **Actionable Recommendations**: Automated suggestions with expected impact

### Why Composite Scoring Matters
1. **Holistic Optimization**: Don't just beat AI detection, create quality content
2. **Balanced Trade-offs**: Weight different quality dimensions appropriately
3. **Single Target Metric**: Simplifies optimization and comparison
4. **Historical Tracking**: Measure progress toward comprehensive quality

### Why Parameter Interactions Matter
1. **Synergistic Effects**: Some parameter combinations work better together
2. **Non-Linear Relationships**: Simple correlation misses complex patterns
3. **Context-Dependent**: Optimal values may depend on other parameters

---

**Last Updated**: November 16, 2025
**Module Status**: Phase 1-2 Complete (Database + Composite Scorer + Granular Correlator)
