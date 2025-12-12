# End-to-End Parameter Flow Normalization

**Status**: Implementation Guide  
**Created**: November 17, 2025  
**Purpose**: Normalize and streamline parameter flow from sweet spot → generation → evaluation → storage

---

## Overview

This document maps the complete parameter lifecycle through the Z-Beam generation system and identifies normalization requirements to ensure consistent parameter formats throughout the pipeline.

---

## Current Parameter Flow Architecture

### 1. **Sweet Spot Discovery Phase**

**Location**: `processing/learning/sweet_spot_analyzer.py`

**Input**: Database history of successful generations
```sql
SELECT * FROM generation_parameters p
JOIN detection_results r ON p.detection_result_id = r.id
WHERE r.success = 1 AND r.human_score >= 20
```

**Output**: Sweet spot recommendations saved to database
```python
# Table: sweet_spot_recommendations
{
    'material': '*',  # Generic learning
    'component_type': '*',  # Generic learning
    'temperature_median': 0.85,
    'frequency_penalty_median': 0.4,
    'presence_penalty_median': 0.3,
    'trait_frequency_median': 0.7,
    'technical_intensity_median': 2,
    'imperfection_tolerance_median': 0.5,
    'sentence_rhythm_variation_median': 0.6,
    'max_human_score': 85.2,
    'confidence_level': 'high'
}
```

**Normalization Issue**: ❌ Only captures 7 parameters (temperature, 2 penalties, 3 voice params, 1 enrichment param) but generation uses 20+ parameters

---

### 2. **Parameter Initialization Phase**

**Location**: `processing/unified_orchestrator.py::_get_adaptive_parameters()`

**Priority Order**:
1. **Database Reuse** (Primary): `_get_best_previous_parameters()`
2. **Sweet Spot Recommendations** (Secondary): Query `sweet_spot_recommendations` table
3. **Dynamic Calculation** (Fallback): `DynamicConfig.get_all_generation_params()`

**Output Format**:
```python
params = {
    'api_params': {
        'temperature': 0.85,
        'max_tokens': 450,
        'retry_behavior': {
            'max_attempts': 3,
            'retry_temperature_increase': 0.05
        },
        'penalties': {
            'frequency_penalty': 0.4,
            'presence_penalty': 0.3
        }
    },
    'voice_params': {
        'trait_frequency': 0.7,
        'opinion_rate': 0.5,
        'reader_address_rate': 0.3,
        'colloquialism_frequency': 0.4,
        'structural_predictability': 0.6,
        'emotional_tone': 0.5,
        'imperfection_tolerance': 0.5,
        'sentence_rhythm_variation': 0.6
    },
    'enrichment_params': {
        'technical_intensity': 2,
        'context_detail_level': 2,
        'fact_formatting_style': 'balanced',
        'engagement_level': 2
    },
    'validation_params': {
        'readability_thresholds': {'min': 40, 'max': 70},
        'grammar_strictness': 0.8,
        'detection_threshold': 0.3,
        'confidence_thresholds': {'high': 0.9, 'medium': 0.7}
    }
}
```

**Normalization Issue**: ✅ Well-structured bundles, but database reuse doesn't preserve full `enrichment_params` or `validation_params`

---

### 3. **Prompt Construction Phase**

**Location**: `processing/generation/prompt_builder.py::build_unified_prompt()`

**Input**: Parameter bundles from previous phase
```python
prompt = self.prompt_builder.build_unified_prompt(
    topic=identifier,
    voice=voice,
    length=length,
    facts=facts_str,
    context=context,
    component_type=component_type,
    domain='materials',
    voice_params=params['voice_params'],
    enrichment_params=params['enrichment_params'],
    variation_seed=variation_seed
)
```

**Output**: Text prompt sent to API

**Normalization Issue**: ❌ `api_params` not passed to prompt builder - penalties and temperature lost at this stage

---

### 4. **API Generation Phase**

**Location**: `processing/generator.py` or component generators

**Input**: Prompt + API parameters extracted separately
```python
# Parameters scattered across different calls
text = self.winston.generate(
    prompt=prompt,
    temperature=params['temperature'],  # ❌ Extracted from bundle
    max_tokens=params['max_tokens'],    # ❌ Extracted from bundle
    ...
)
```

**Normalization Issue**: ❌ Parameters extracted individually instead of passing complete `api_params` bundle

---

### 5. **Winston Detection Phase**

**Location**: `processing/detection/winston_client.py`

**Input**: Generated text
**Output**: Detection results
```python
{
    'success': True,
    'ai_score': 0.25,
    'human_score': 75.0,
    'label': 'HUMAN',
    'sentences': [...],
    'feedback': {...}
}
```

**Normalization Issue**: ✅ Well-structured response

---

### 6. **Parameter Storage Phase**

**Location**: `processing/detection/winston_feedback_db.py::log_generation_parameters()`

**Input Transformation**: Parameters restructured for storage
```python
structured_params = {
    'material_name': material_name,
    'component_type': component_type,
    'attempt': attempt,
    'api': {
        'temperature': params['temperature'],  # ❌ Extracted from api_params
        'max_tokens': params['max_tokens'],    # ❌ Extracted from api_params
        'frequency_penalty': params.get('api_penalties', {}).get('frequency_penalty', 0.0),  # ❌ Different key
        'presence_penalty': params.get('api_penalties', {}).get('presence_penalty', 0.0)     # ❌ Different key
    },
    'voice': params.get('voice_params', {}),
    'enrichment': params.get('enrichment_params', {}),
    'validation': {  # ❌ Hardcoded - not from params
        'detection_threshold': self.ai_threshold,
        'readability_min': 0.0,
        'readability_max': 100.0,
        'grammar_strictness': 0.8,
        'confidence_high': 0.9,
        'confidence_medium': 0.7
    },
    'retry': {  # ❌ Hardcoded - not from params
        'max_attempts': max_attempts,
        'retry_temperature_increase': 0.05
    }
}
```

**Normalization Issue**: ❌ **CRITICAL** - Parameter structure changed during storage with hardcoded values

---

### 7. **Subjective Evaluation Phase** (Post-Generation)

**Location**: `shared/commands/generation.py::evaluate_after_generation()`

**Input**: Generated text + metadata
**Output**: Stored to `subjective_evaluations` table
```python
{
    'timestamp': '2025-11-17T10:30:00',
    'topic': 'Aluminum',
    'component_type': 'micro',
    'overall_score': 8.5,
    'clarity_score': 9.0,
    'professionalism_score': 8.0,
    'technical_accuracy_score': 9.0,
    'human_likeness_score': 8.5,
    'engagement_score': 8.0,
    'jargon_free_score': 9.0,
    'passes_quality_gate': True
}
```

**Normalization Issue**: ❌ No link to `generation_parameters` - can't correlate evaluation scores with parameter choices

---

## Identified Normalization Issues

### **Issue 1: Inconsistent Parameter Keys**
- `api_params.penalties.frequency_penalty` vs `api_penalties.frequency_penalty` vs `api.frequency_penalty`
- Need canonical structure throughout pipeline

### **Issue 2: Incomplete Sweet Spot Coverage**
- Sweet spots only track 7/20+ parameters
- Missing: `opinion_rate`, `reader_address_rate`, `colloquialism_frequency`, `structural_predictability`, `emotional_tone`, `context_detail_level`, `fact_formatting_style`, `engagement_level`

### **Issue 3: Hardcoded Values in Storage**
- `validation` params hardcoded during storage instead of using actual values
- `retry` params hardcoded during storage instead of using actual values
- Violates "No hardcoded values" policy

### **Issue 4: Parameter Extraction Instead of Bundle Passing**
- API calls extract individual values from bundles
- Should pass complete bundles to preserve structure

### **Issue 5: No Parameter-Evaluation Link**
- `subjective_evaluations` table has no foreign key to `generation_parameters`
- Can't analyze which parameters lead to high subjective scores

### **Issue 6: Missing Composite Quality Score**
- No unified quality metric combining Winston (60%) + Subjective (30%) + Readability (10%)
- Proposed in `docs/proposals/GENERIC_LEARNING_ARCHITECTURE.md` but not implemented

---

## Normalization Plan

### **Phase 1: Canonical Parameter Schema** ✅ **IMMEDIATE**

Define single source of truth for parameter structure:

```python
# NEW: processing/schemas/parameter_schema.py
CANONICAL_PARAMETER_SCHEMA = {
    'metadata': {
        'material_name': str,
        'component_type': str,
        'attempt': int,
        'timestamp': str
    },
    'api': {
        'temperature': float,
        'max_tokens': int,
        'frequency_penalty': float,
        'presence_penalty': float
    },
    'retry': {
        'max_attempts': int,
        'retry_temperature_increase': float
    },
    'voice': {
        'trait_frequency': float,
        'opinion_rate': float,
        'reader_address_rate': float,
        'colloquialism_frequency': float,
        'structural_predictability': float,
        'emotional_tone': float,
        'imperfection_tolerance': float,
        'sentence_rhythm_variation': float
    },
    'enrichment': {
        'technical_intensity': int,
        'context_detail_level': int,
        'fact_formatting_style': str,
        'engagement_level': int
    },
    'validation': {
        'detection_threshold': float,
        'readability_min': float,
        'readability_max': float,
        'grammar_strictness': float,
        'confidence_high': float,
        'confidence_medium': float
    }
}
```

**Actions**:
1. Create `processing/schemas/parameter_schema.py`
2. Define `CanonicalParameters` dataclass with validation
3. Add `to_canonical()` normalizer function
4. Add `from_canonical()` converter function for legacy formats

---

### **Phase 2: Parameter Bundle Preservation** ⏳ **NEXT**

Stop extracting individual values - pass complete bundles.

**Changes Required**:

1. **DynamicConfig Output**: ✅ Already returns bundles (no change needed)

2. **Orchestrator Pass-Through**: Update `_get_adaptive_parameters()` to return canonical format
```python
# OLD (current)
return {
    'api_params': {...},
    'api_penalties': {...},  # ❌ Duplicate structure
    'voice_params': {...},
    ...
}

# NEW (canonical)
return CanonicalParameters(
    metadata={'material_name': identifier, 'component_type': component_type, 'attempt': attempt},
    api={'temperature': 0.85, 'max_tokens': 450, 'frequency_penalty': 0.4, 'presence_penalty': 0.3},
    retry={'max_attempts': 3, 'retry_temperature_increase': 0.05},
    voice={...},
    enrichment={...},
    validation={...}
)
```

3. **Storage Normalization**: Update `log_generation_parameters()` to accept canonical format
```python
# OLD (current)
structured_params = {
    'material_name': material_name,
    'component_type': component_type,
    'api': {
        'temperature': params['temperature'],  # ❌ Manual extraction
        ...
    }
}

# NEW (canonical)
param_id = self.feedback_db.log_generation_parameters(
    detection_id, 
    params.to_canonical()  # ✅ Direct conversion
)
```

---

### **Phase 3: Complete Sweet Spot Coverage** ⏳ **PARALLEL**

Expand sweet spot analysis to all 20+ parameters.

**Database Changes**:
```sql
ALTER TABLE sweet_spot_recommendations ADD COLUMN opinion_rate_median REAL;
ALTER TABLE sweet_spot_recommendations ADD COLUMN reader_address_rate_median REAL;
ALTER TABLE sweet_spot_recommendations ADD COLUMN colloquialism_frequency_median REAL;
ALTER TABLE sweet_spot_recommendations ADD COLUMN structural_predictability_median REAL;
ALTER TABLE sweet_spot_recommendations ADD COLUMN emotional_tone_median REAL;
ALTER TABLE sweet_spot_recommendations ADD COLUMN context_detail_level_median INTEGER;
ALTER TABLE sweet_spot_recommendations ADD COLUMN fact_formatting_style_mode TEXT;
ALTER TABLE sweet_spot_recommendations ADD COLUMN engagement_level_median INTEGER;
```

**Code Changes**:
- Update `sweet_spot_analyzer.py::find_sweet_spots()` to analyze all parameters
- Update `winston_feedback_db.py::upsert_sweet_spot()` to store all parameters
- Update `unified_orchestrator.py::_get_best_previous_parameters()` to retrieve all parameters

---

### **Phase 4: Eliminate Hardcoded Storage Values** 🔥 **CRITICAL**

Remove all hardcoded values from `log_generation_parameters()`.

**Current Violations**:
```python
# ❌ HARDCODED - WRONG
'validation': {
    'detection_threshold': self.ai_threshold,  # From self, not params
    'readability_min': 0.0,                    # HARDCODED
    'readability_max': 100.0,                  # HARDCODED
    'grammar_strictness': 0.8,                 # HARDCODED
    'confidence_high': 0.9,                    # HARDCODED
    'confidence_medium': 0.7                   # HARDCODED
}
```

**Fixed Approach**:
```python
# ✅ FROM PARAMS - CORRECT
'validation': params.validation  # Direct from canonical params
```

**Actions**:
1. Ensure `validation_params` passed to generator from orchestrator
2. Store actual values used during generation
3. Remove all default/fallback values in storage path

---

### **Phase 5: Link Evaluations to Parameters** ⏳ **IMPORTANT**

Add foreign key linking subjective evaluations to generation parameters.

**Database Changes**:
```sql
ALTER TABLE subjective_evaluations 
ADD COLUMN generation_parameters_id INTEGER 
REFERENCES generation_parameters(id);

CREATE INDEX idx_subjective_eval_params 
ON subjective_evaluations(generation_parameters_id);
```

**Code Changes**:
```python
# In shared/commands/generation.py
def evaluate_after_generation(...):
    # Store evaluation with parameter link
    eval_id = feedback_db.log_subjective_evaluation(
        topic=material_name,
        component_type=component_type,
        scores={...},
        generation_parameters_id=param_id  # ✅ NEW: Link to params
    )
```

**Benefits**:
- Correlate subjective scores with parameter choices
- Analyze which parameters lead to high subjective scores
- Enable composite quality scoring

---

### **Phase 6: Implement Composite Quality Score** ⏳ **FUTURE**

Add unified quality metric to enable holistic learning.

**Formula** (from `docs/proposals/GENERIC_LEARNING_ARCHITECTURE.md`):
```
composite_score = (winston_human_score * 0.60) + 
                  (subjective_overall_score * 10 * 0.30) + 
                  (readability_score * 0.10)
```

**Database Changes**:
```sql
ALTER TABLE detection_results 
ADD COLUMN composite_quality_score REAL;

ALTER TABLE detection_results 
ADD COLUMN subjective_evaluation_id INTEGER 
REFERENCES subjective_evaluations(id);

CREATE INDEX idx_detection_composite 
ON detection_results(composite_quality_score);
```

**Code Changes**:
- Create `processing/evaluation/composite_scorer.py`
- Update `unified_orchestrator.py` to calculate composite score after evaluation
- Update sweet spot analyzer to use composite score for recommendations

---

## Implementation Sequence

### **Sprint 1: Foundation (This Week)**
- [x] Document current parameter flow (this document)
- [ ] Create `processing/schemas/parameter_schema.py` with canonical schema
- [ ] Add `CanonicalParameters` dataclass with validation
- [ ] Add normalization functions (`to_canonical()`, `from_canonical()`)
- [ ] Write tests for parameter normalization

### **Sprint 2: Bundle Preservation (Next Week)**
- [ ] Update `unified_orchestrator._get_adaptive_parameters()` to return canonical format
- [ ] Update `generator.py` to accept canonical parameter bundles
- [ ] Update `winston_feedback_db.log_generation_parameters()` to accept canonical format
- [ ] Remove hardcoded values from storage (validation, retry params)
- [ ] Update all parameter extraction code to use bundles
- [ ] Write integration tests for parameter flow

### **Sprint 3: Complete Coverage (Week 3)**
- [ ] Add missing columns to `sweet_spot_recommendations` table
- [ ] Update `sweet_spot_analyzer.py` to analyze all 20+ parameters
- [ ] Update `_get_best_previous_parameters()` to retrieve all parameters
- [ ] Write tests for complete sweet spot coverage

### **Sprint 4: Evaluation Integration (Week 4)**
- [ ] Add `generation_parameters_id` to `subjective_evaluations` table
- [ ] Update evaluation logging to link to parameters
- [ ] Create queries to correlate subjective scores with parameter choices
- [ ] Write tests for parameter-evaluation linkage

### **Sprint 5: Composite Scoring (Future)**
- [ ] Add `composite_quality_score` to `detection_results` table
- [ ] Implement `CompositeScorer` class
- [ ] Update orchestrator to calculate composite scores
- [ ] Update sweet spot analyzer to use composite scores
- [ ] Write tests for composite scoring

---

## Verification Checklist

After implementation, verify:

- ✅ **Canonical Schema**: All parameter dictionaries use consistent key structure
- ✅ **Bundle Passing**: Parameters passed as complete bundles, not individual values
- ✅ **Zero Hardcoding**: No hardcoded parameter values in production code
- ✅ **Complete Sweet Spots**: Sweet spot recommendations cover all 20+ parameters
- ✅ **Evaluation Links**: Subjective evaluations linked to generation parameters
- ✅ **Composite Scores**: Unified quality metric combining all evaluation dimensions
- ✅ **Test Coverage**: All parameter flows have integration tests

---

## Success Metrics

**After normalization, we should achieve**:
1. **100% parameter preservation** from sweet spot → storage
2. **Zero parameter key inconsistencies** across pipeline stages
3. **Zero hardcoded values** in parameter storage code
4. **100% sweet spot coverage** of all parameters (20+ vs current 7)
5. **Full traceability** from evaluation scores → parameters → sweet spots

**Learning Improvements**:
- Sweet spot recommendations improve from 7 to 20+ parameters
- Subjective evaluation insights feed back into parameter learning
- Composite quality scores enable holistic optimization
- Parameter reuse success rate increases from ~60% to ~95%

---

## Related Documentation

- **Parameter Calculation**: `processing/config/dynamic_config.py`
- **Sweet Spot Analysis**: `processing/learning/sweet_spot_analyzer.py`
- **Database Schema**: `processing/detection/winston_feedback_db.py`
- **Generic Learning Proposal**: `docs/proposals/GENERIC_LEARNING_ARCHITECTURE.md`
- **Component Discovery**: `docs/architecture/COMPONENT_DISCOVERY.md`

---

**Next Steps**: Begin Sprint 1 by creating canonical parameter schema.
