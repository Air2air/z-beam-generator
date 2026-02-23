# Unified Learning Architecture

**Date**: November 17, 2025  
**Strategy**: Option C - Separate but unified  
**Status**: Design Phase

---

## 🎯 Core Principle

**Winston and Subjective are SEPARATE modules that feed into a UNIFIED learning library.**

```
┌─────────────────────┐         ┌─────────────────────┐
│   Winston Module    │         │ Subjective Module   │
│   (AI Detection)    │         │ (Quality Assessment)│
└──────────┬──────────┘         └──────────┬──────────┘
           │                               │
           │   Detection Results          │   Evaluation Results
           │   (human_score 0-100)        │   (overall_score 0-10)
           │                               │
           └───────────┬───────────────────┘
                       │
                       ▼
           ┌─────────────────────┐
           │  UNIFIED LEARNING   │
           │     LIBRARY         │
           │                     │
           │  - Parameter DB     │
           │  - Sweet Spots      │
           │  - Correlations     │
           │  - Recommendations  │
           └──────────┬──────────┘
                      │
                      │   Learned Parameters
                      │
                      ▼
           ┌─────────────────────┐
           │   Next Generation   │
           │  (Both modules use  │
           │   learned params)   │
           └─────────────────────┘
```

---

## 📊 Current Status (Nov 17, 2025)

### Winston Module ✅ **OPERATIONAL**
- **Status**: 100% operational with winston-only mode
- **Integration**: UnifiedOrchestrator
- **Detection**: 512 attempts (24 hours), 28.1% success, 92.2% avg human
- **Learning**: Active (parameter reuse, sweet spots, prompt optimization)
- **Database**: `detection_results` table (clean data post-cleanup)

### Subjective Module ✅ **DATA COLLECTION**
- **Status**: 111 evaluations logged (7 days)
- **Integration**: Old component handlers (micro/subtitle/FAQ)
- **Evaluation**: Grok AI with 6 dimensions + narrative assessment
- **Learning**: Passive (data collected but not yet used for decisions)
- **Database**: `subjective_evaluations` table

### Unified Learning Library ⏳ **DESIGN PHASE**
- **Status**: Conceptual, not yet implemented
- **Purpose**: Combine Winston + Subjective insights
- **Benefits**: Holistic quality optimization
- **Timeline**: Phase 2 (after analysis tools built)

---

## 🏗️ Architecture Design

### Module Independence

**Each module can be:**
1. ✅ **Fixed independently** - Winston bug doesn't break Subjective
2. ✅ **Tested independently** - Each has own test suite
3. ✅ **Deployed independently** - Can disable one without affecting other
4. ✅ **Scaled independently** - Different API costs/quotas

**They share:**
1. ✅ **Learning database** - Same `winston_feedback.db`
2. ✅ **Parameter system** - Same temperature/penalty parameters
3. ✅ **Generation pipeline** - Both run after content generation
4. ⏳ **Unified insights** - Combined analysis (Phase 2)

### Data Flow

**Generation Phase:**
```python
# 1. Generate content
text = api_client.generate(prompt, temperature=T, penalties=P)

# 2. Winston detection (ALWAYS)
winston_result = winston.detect(text)
# → Returns: human_score (0-100), ai_score (0-1.0)
# → Logs to: detection_results table
# → Updates: sweet_spot_recommendations

# 3. Subjective evaluation (OPTIONAL)
if enable_subjective:
    subjective_result = subjective.evaluate(text)
    # → Returns: overall_score (0-10), 6 dimension scores
    # → Logs to: subjective_evaluations table
    # → Does NOT yet affect parameters

# 4. Decision (currently Winston-only)
if winston_result.passes_threshold:
    accept()
else:
    retry_with_adjusted_parameters()
```

**Learning Phase (Future):**
```python
# Unified Learning Library queries both tables
learning_lib = UnifiedLearningLibrary()

# Get holistic insights
insights = learning_lib.analyze(
    winston_data=detection_results,
    subjective_data=subjective_evaluations,
    time_range='7 days'
)

# Example insights:
{
    'optimal_temperature': 0.95,  # From Winston success rate
    'quality_concerns': [
        'Low engagement scores (4.2/10 avg)',  # From Subjective
        'Overuse of hedging language'           # From Subjective
    ],
    'recommended_actions': [
        'Increase temperature by +0.05',        # Winston-driven
        'Reduce presence_penalty by -0.1'       # Subjective-driven
    ],
    'confidence': 'high'  # Based on sample size
}
```

---

## 📋 Implementation Plan

### Phase 1: Separate Fixes ✅ **IN PROGRESS**

**Winston Module (Nov 17, 2025):**
- ✅ Winston-only mode enabled
- ✅ Score validation decorator
- ✅ Database cleanup (3 false positives excluded)
- ✅ Documentation complete
- ✅ E2E tests created

**Subjective Module (Next):**
- ⏳ Fix any score inversion issues
- ⏳ Add @validate_scores decorator
- ⏳ Create E2E tests
- ⏳ Document evaluation criteria
- ⏳ Verify Grok API integration

### Phase 2: Analysis Tools ⏳ **NEXT PRIORITY**

**Build tools to understand the data:**

1. **Winston Analyzer**
   - Parameter effectiveness (which temps/penalties work best?)
   - Failure pattern detection (what causes 0% human scores?)
   - Sweet spot validation (are recommendations accurate?)
   - Author performance comparison

2. **Subjective Analyzer**
   - Dimension correlations (clarity vs engagement?)
   - Weakness pattern detection (common issues?)
   - Recommendation impact tracking (do recommendations help?)
   - Author voice quality comparison

3. **Cross-Module Analyzer**
   - Correlation: Winston score vs Subjective score
   - Hypothesis: Does 95% human → 8.5/10 quality?
   - Identify: Parameters that optimize BOTH metrics
   - Discover: Trade-offs (high human but low engagement?)

**Scripts to create:**
```bash
# Winston analysis
python3 scripts/analyze_winston_patterns.py --days 7

# Subjective analysis  
python3 scripts/analyze_subjective_patterns.py --days 7

# Cross-module analysis
python3 scripts/analyze_unified_learning.py --days 7
```

### Phase 3: Unified Learning ⏳ **FUTURE**

**Only after Phase 2 proves value:**

1. **Unified Learning Library**
   ```python
    # learning/consolidated_learning_system.py
   
   class UnifiedLearningLibrary:
       def __init__(self, feedback_db):
           self.winston_analyzer = WinstonAnalyzer(feedback_db)
           self.subjective_analyzer = SubjectiveAnalyzer(feedback_db)
           self.correlation_engine = CorrelationEngine(feedback_db)
       
       def get_optimal_parameters(self, material, component_type):
           """Get parameters optimized for BOTH Winston and Subjective"""
           winston_optimal = self.winston_analyzer.get_sweet_spot(...)
           subjective_optimal = self.subjective_analyzer.get_recommendations(...)
           
           # Combine insights
           return self.correlation_engine.merge(
               winston_optimal,
               subjective_optimal,
               priority='balanced'  # or 'winston', 'subjective'
           )
   ```

2. **Decision Integration**
   ```python
   # In UnifiedOrchestrator.generate()
   
   # Get unified parameters
   params = unified_learning_lib.get_optimal_parameters(
       material=identifier,
       component_type=component_type
   )
   
   # Generate with unified params
   text = self._call_api(prompt, **params)
   
   # Evaluate with both modules
   winston_result = self.winston.detect_and_log(text, ...)
   subjective_result = self.subjective.evaluate(text, ...)
   
   # Combined decision
   passes_winston = winston_result.passes_threshold
   passes_subjective = subjective_result.passes_quality_gate
   
   if passes_winston and passes_subjective:
       accept()
   elif passes_winston and not passes_subjective:
       # Good AI detection, poor quality
       # Log for analysis, may still accept
       log_quality_concern(subjective_result.weaknesses)
       accept_with_warning()
   elif not passes_winston and passes_subjective:
       # Poor AI detection, good quality  
       # Retry with adjusted params
       retry_with_winston_focus()
   else:
       # Both failed
       retry_with_unified_adjustments()
   ```

3. **Adaptive Quality Gates**
   ```python
   # Dynamic thresholds based on historical performance
   
   winston_threshold = learning_lib.get_adaptive_threshold(
       metric='human_score',
       target_percentile=70  # Accept top 70% of generations
   )
   
   subjective_threshold = learning_lib.get_adaptive_threshold(
       metric='overall_score',
       target_percentile=70
   )
   ```

---

## 🎓 Learning Data Structure

### Unified Database Schema

**Existing Tables:**
```sql
-- Winston detection results
CREATE TABLE detection_results (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    material TEXT,
    component_type TEXT,
    generated_text TEXT,
    human_score REAL,      -- 0-1.0 normalized (0.85 = 85% human)
    ai_score REAL,          -- 0-1.0 normalized (0.15 = 15% AI)
    temperature REAL,
    frequency_penalty REAL,
    presence_penalty REAL,
    success BOOLEAN,
    exclusion_reason TEXT   -- For cleaning contaminated data
);

-- Subjective evaluations
CREATE TABLE subjective_evaluations (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    topic TEXT,
    component_type TEXT,
    generated_text TEXT,
    overall_score REAL,     -- 0-10 scale
    clarity_score REAL,
    professionalism_score REAL,
    technical_accuracy_score REAL,
    human_likeness_score REAL,
    engagement_score REAL,
    jargon_free_score REAL,
    passes_quality_gate BOOLEAN,
    strengths TEXT,         -- JSON
    weaknesses TEXT,        -- JSON
    recommendations TEXT,   -- JSON
    narrative_assessment TEXT
);
```

**New Table (Phase 3):**
```sql
-- Unified learning insights
CREATE TABLE unified_insights (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    material TEXT,
    component_type TEXT,
    
    -- Link to source data
    detection_result_id INTEGER REFERENCES detection_results(id),
    subjective_evaluation_id INTEGER REFERENCES subjective_evaluations(id),
    
    -- Combined metrics
    composite_quality_score REAL,  -- Weighted: Winston 60% + Subjective 30% + Readability 10%
    
    -- Parameters used
    temperature REAL,
    frequency_penalty REAL,
    presence_penalty REAL,
    
    -- Outcomes
    winston_passed BOOLEAN,
    subjective_passed BOOLEAN,
    both_passed BOOLEAN,
    
    -- Insights
    optimization_potential TEXT,  -- 'high', 'medium', 'low', 'none'
    recommended_adjustments TEXT  -- JSON: {temperature: +0.05, ...}
);
```

---

## 📊 Success Metrics

### Phase 1 Metrics ✅ **CURRENT**

**Winston Module:**
- ✅ Winston-only mode: 100% active
- ✅ False positives: 0 (3 excluded from pre-winston-only era)
- ✅ Success rate: 28.1% (realistic, not inflated)
- ✅ Avg human score: 92.2% (when successful)

**Subjective Module:**
- ✅ Evaluations logged: 111 (7 days)
- ✅ Avg overall score: 7.0/10 (estimated from samples)
- ✅ Data quality: High (narrative assessments working)
- ❌ Learning integration: 0% (not yet feeding into parameters)

### Phase 2 Metrics 🎯 **TARGET**

**Analysis Tools:**
- 🎯 Winston pattern analysis: Identify top 3 failure patterns
- 🎯 Subjective pattern analysis: Identify top 3 quality issues
- 🎯 Correlation analysis: Prove/disprove Winston ↔ Subjective relationship
- 🎯 Sample size: 500+ Winston + 500+ Subjective (2-3 weeks of data)

**Insights Discovery:**
- 🎯 Find: Optimal temperature range for both modules
- 🎯 Find: Penalty settings that balance Winston + Subjective
- 🎯 Find: Author-specific patterns (which authors need tuning?)
- 🎯 Find: Trade-offs (if any) between modules

### Phase 3 Metrics 🎯 **LONG-TERM**

**Unified Learning:**
- 🎯 Composite quality score: 80+ (out of 100)
- 🎯 Winston + Subjective pass rate: 90%+
- 🎯 Parameter optimization: Automated recommendations
- 🎯 Continuous improvement: Score increases over time

**Business Impact:**
- 🎯 Success rate: 50%+ (from current 28.1%)
- 🎯 Quality consistency: 95% of outputs score 7.0/10+
- 🎯 Cost efficiency: Fewer retries due to better parameters
- 🎯 Author authenticity: Maintained across quality improvements

---

## 🚀 Next Actions

### Immediate (This Week)

1. ✅ **DONE**: Winston module fixes (winston-only, score validation, docs, tests)
2. ⏳ **TODO**: Subjective module audit
   - Check for score inversions
   - Add @validate_scores decorator
   - Create E2E tests
   - Document evaluation process

### Short-term (Next 2 Weeks)

3. ⏳ **TODO**: Build Phase 2 analysis tools
   - Winston pattern analyzer
   - Subjective pattern analyzer
   - Cross-module correlation analyzer
   
4. ⏳ **TODO**: Generate insights report
   - Run analyzers on 2 weeks of data
   - Document correlations found
   - Identify optimization opportunities
   - Present findings for Phase 3 decision

### Medium-term (Next Month)

5. ⏳ **TODO**: If Phase 2 proves value, build unified learning library
   - Create UnifiedLearningLibrary class
   - Implement correlation engine
   - Add composite quality scoring
   - Integrate into UnifiedOrchestrator

6. ⏳ **TODO**: Measure unified learning impact
   - A/B test: unified params vs current params
   - Track composite quality score trends
   - Monitor success rate improvements
   - Validate business impact

---

## 🎯 Summary

**Strategy**: **Option C - Separate but Unified**

**Benefits:**
- ✅ Module independence (fix/test/deploy separately)
- ✅ Risk mitigation (one module failure doesn't break other)
- ✅ Phased approach (prove value before full integration)
- ✅ Flexibility (can prioritize either module)
- ✅ Scalability (different API costs/quotas)

**Current Focus:**
1. Fix both modules independently (Winston done, Subjective next)
2. Build analysis tools to understand the data
3. Prove correlation between Winston and Subjective
4. Only then build unified learning library

**Key Insight**: Don't integrate until we understand the relationship. Phase 2 analysis will reveal if/how to combine insights.
