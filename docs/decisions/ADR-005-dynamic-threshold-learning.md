# ADR-005: Dynamic Database-Driven Threshold Learning

**Status**: Accepted  
**Date**: November 20, 2025  
**Deciders**: System Architecture Team  
**Related**: HARDCODED_VALUE_POLICY.md, Sweet Spot Analyzer

## Context

### The Problem

The system had extensive learning infrastructure (sweet spot analyzer, success pattern tracking, parameter correlation analysis) but **thresholds were static**:

- **Winston AI threshold**: Hardcoded `0.33` in ValidationConstants
- **Realism threshold**: Static `7.0` in config.yaml
- **Sweet spot data**: Collected but **never used** to adjust actual generation

This violated the HARDCODED_VALUE_POLICY.md and created a **learning paradox**:
- System learned that lower temperature → better scores (correlation: -0.515)
- Recommendation: "📉 Decrease temperature for better scores"
- **But temperature never changed** - stayed at config value

### Evidence of the Issue

From database query (Nov 20, 2025):
```sql
SELECT * FROM sweet_spot_recommendations LIMIT 1;
-- Shows learned ranges: temperature 0.815-0.815
-- Shows correlation: temperature -0.515 (negative = decrease helps)
-- Shows recommendation: "Decrease these for better scores: temperature"
-- BUT: config.yaml still has static temperature calculation
```

From code audit:
```python
# generation/validation/constants.py
WINSTON_AI_THRESHOLD = 0.33  # ❌ Hardcoded, never learns

# generation/config.yaml
quality_gates:
  realism_threshold: 7.0  # ❌ Static, never adapts

# learning/sweet_spot_analyzer.py
# Calculates optimal ranges... but nothing uses them! ❌
```

## Decision

Implement **fully dynamic, database-driven thresholds** that:

1. **Start with sensible defaults** (config.yaml as baseline)
2. **Learn from success patterns** (sweet spot analysis of top 25%)
3. **Automatically adapt** based on 75th percentile of quality scores
4. **Store learned values** in database (audit trail)
5. **Apply to next generation** (close the learning loop)

### Architecture

```
Generation Cycle (BEFORE):
Generate → Evaluate → Save → Learn → [Data stored, never used]

Generation Cycle (AFTER):
Generate (use learned params) → Evaluate → Save → Learn → Update DB → [Next gen uses new params]
```

### Components

#### 1. ThresholdManager (`learning/threshold_manager.py`)

Central manager for all dynamic thresholds:

```python
class ThresholdManager:
    def get_winston_threshold(use_learned=True):
        # Query top 25% of successful content
        # Calculate 75th percentile of their AI scores
        # Return learned threshold (fallback to 0.33 if <10 samples)
    
    def get_realism_threshold(use_learned=True):
        # Query successful evaluations
        # Calculate 75th percentile of realism scores
        # Return learned threshold (fallback to 7.0 if <10 samples)
    
    def save_learned_thresholds(thresholds):
        # Save to learned_thresholds table for audit trail
```

#### 2. ValidationConstants (Updated)

Replace hardcoded constants with dynamic methods:

```python
# BEFORE (❌ Static):
WINSTON_AI_THRESHOLD = 0.33

# AFTER (✅ Dynamic):
@classmethod
def get_winston_threshold(cls, use_learned=True):
    manager = cls._get_threshold_manager()
    return manager.get_winston_threshold(use_learned)
```

#### 3. Quality Gate Integration

All validation now uses learned thresholds:

```python
# shared/commands/generation.py
ai_threshold = ValidationConstants.get_winston_threshold(use_learned=True)

# domains/materials/coordinator.py
threshold_manager = ThresholdManager(db_path='z-beam.db')
realism_threshold = threshold_manager.get_realism_threshold(use_learned=True)
```

#### 4. Sweet Spot Parameter Integration

Generation parameters now use learned values:

```python
# quality_gated_generator.py
def _get_base_parameters(component_type):
    learned_params = self._load_sweet_spot_parameters()
    
    return {
        'temperature': learned_params.get('temperature') or config_default,
        'emotional_tone': learned_params.get('emotional_tone') or config_default,
        # ... all parameters use learned values first
    }
```

### Learning Strategy

**75th Percentile Target**: Learn from the top 25% of successful content

Why 75th percentile?
- **Not too strict**: Not just the absolute best (could be outliers)
- **Not too lenient**: Not the median (too easy)
- **Just right**: Represents consistent high quality

**Conservative Factor**: Be 95% as strict as learned optimum

```python
learned_threshold = statistics.quantiles(scores, n=100)[75]
adjusted_threshold = learned_threshold * 0.95
```

Why conservative?
- Avoid overfitting to small sample sizes
- Maintain quality standards during learning
- Gradually tighten as confidence increases

### Fallback Strategy

```python
if sample_count < MIN_SAMPLES_FOR_LEARNING:  # Default: 10
    return DEFAULT_THRESHOLD  # Config baseline
```

System always has sensible defaults:
- Winston: 0.33 (67%+ human required)
- Realism: 7.0/10 minimum
- Voice/Tonal: 7.0/10 minimum

## Consequences

### Positive

1. **Truly Adaptive System**: Thresholds improve as system learns
2. **Data-Driven Quality**: Based on actual success patterns, not guesses
3. **Self-Improving**: Quality standards tighten automatically with experience
4. **Policy Compliant**: Zero hardcoded thresholds in production code
5. **Closed Loop Learning**: Sweet spot data finally influences generation
6. **Transparent**: Logged threshold values show learning progression

### Negative

1. **Initial Instability**: First 10 samples use defaults (until learning kicks in)
2. **Database Dependency**: Requires z-beam.db available and populated
3. **Complexity**: More moving parts than static thresholds
4. **Testing Harder**: Need realistic data to test learning behavior

### Mitigations

- **Sensible defaults**: System works fine until learning activates
- **Fail-safe fallbacks**: Database errors → use defaults, log warning
- **Audit trail**: `learned_thresholds` table tracks all adjustments
- **Override flag**: `use_learned=False` for testing with static values

## Alternatives Considered

### 1. Keep Static Thresholds

**Rejected**: Violates HARDCODED_VALUE_POLICY.md and wastes learning infrastructure

Pros:
- Simple, predictable
- No database dependency
- Easy to test

Cons:
- ❌ Never improves with experience
- ❌ Sweet spot data wasted
- ❌ Policy violation
- ❌ Suboptimal quality standards

### 2. Config-File-Based Learning

Save learned thresholds to config.yaml instead of database.

**Rejected**: Config is for user settings, not learned data

Pros:
- No database dependency
- Human-readable threshold values
- Easy version control

Cons:
- ❌ Mixes user intent with learned behavior
- ❌ No audit trail of threshold evolution
- ❌ Git conflicts on multi-user systems
- ❌ Can't query historical values

### 3. Exponential Moving Average

Smooth threshold changes over time with EMA.

**Considered for future**: Good for stabilizing noisy data

Pros:
- Smooth transitions
- Reduces volatility
- Handles outliers well

Cons:
- More complex
- Slower to adapt
- 75th percentile already provides stability

Decision: Implement percentile learning first, add EMA if volatility becomes an issue.

## Implementation Details

### Database Schema

```sql
CREATE TABLE learned_thresholds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    threshold_type TEXT NOT NULL,
    threshold_value REAL NOT NULL,
    sample_count INTEGER,
    confidence_level TEXT
);
```

### Learning Activation

Minimum samples required: **10**

Why 10?
- Statistical significance (enough for median/percentile)
- Quick activation (not too conservative)
- Reasonable confidence (not too aggressive)

### Parameter Coverage

**Implemented** (Nov 20, 2025):
- Winston AI threshold (0-1.0 scale)
- Realism threshold (0-10 scale)
- Sweet spot parameters (temperature, penalties, voice params)

**Future** (TODO):
- Voice authenticity threshold
- Tonal consistency threshold
- Readability thresholds

## Compliance Verification

### HARDCODED_VALUE_POLICY.md

✅ **PASS**: Zero hardcoded thresholds in production code
- All thresholds loaded from ThresholdManager
- Config values only used as fallback defaults
- Explicit validation if config missing

### Fail-Fast Architecture

✅ **PASS**: Explicit errors on configuration issues
- ValueError if database unavailable (when required)
- Clear logging when falling back to defaults
- No silent degradation

### Learning Architecture

✅ **PASS**: Continuous improvement from patterns
- Sweet spot analyzer feeds ThresholdManager
- Learned thresholds applied to next generation
- Closed-loop learning fully implemented

## Testing Strategy

### Unit Tests

```python
def test_threshold_learning_with_insufficient_data():
    # <10 samples → use defaults
    
def test_threshold_learning_with_sufficient_data():
    # ≥10 samples → use learned values
    
def test_sweet_spot_parameter_integration():
    # Verify learned params influence generation
```

### Integration Tests

```bash
# Generate 20 materials with quality gates
python3 run.py --batch-caption "Material1,Material2,...,Material20"

# Check learned thresholds
sqlite3 z-beam.db "SELECT * FROM learned_thresholds ORDER BY timestamp DESC LIMIT 5"

# Verify thresholds adapted
python3 scripts/analyze_threshold_progression.py
```

### Validation Criteria

1. **Threshold adaptation**: Values change after 10+ samples
2. **Quality improvement**: Average scores increase over time
3. **Parameter influence**: Learned params affect generation
4. **Fallback safety**: System works if database empty

## Migration Path

### For Existing Systems

1. **No breaking changes**: System falls back to defaults if no learning data
2. **Gradual activation**: Learning kicks in after 10 successful generations
3. **Transparent operation**: Logged messages show when using learned vs default
4. **Backward compatible**: Old code using constants still works (deprecated)

### Deprecation Plan

```python
# DEPRECATED (but still works):
threshold = ValidationConstants.WINSTON_AI_THRESHOLD

# NEW (dynamic):
threshold = ValidationConstants.get_winston_threshold(use_learned=True)
```

Deprecated constant will log warning but still return default value.

## Monitoring

### Key Metrics

1. **Threshold progression**: Track learned_thresholds table over time
2. **Sample count**: How many successful generations per threshold
3. **Quality trends**: Average scores before/after learning activation
4. **Parameter stability**: Variance in learned values

### Logging

```
[THRESHOLD MANAGER] Learned 0.305 from 15 samples (75th percentile: 0.321)
[WINSTON THRESHOLD] Using learned threshold: 0.305 (was 0.33 default)
[REALISM THRESHOLD] Learned 7.2 from 12 samples (75th percentile: 7.6)
```

## References

- HARDCODED_VALUE_POLICY.md: `/docs/08-development/HARDCODED_VALUE_POLICY.md`
- Sweet Spot Analyzer: `/learning/sweet_spot_analyzer.py`
- Threshold Manager: `/learning/threshold_manager.py`
- Commit: 50244080 "feat: Implement dynamic database-driven thresholds"

## Future Enhancements

1. **Multi-tier thresholds**: Different standards for caption vs subtitle
2. **Confidence-based strictness**: Tighter thresholds as confidence grows
3. **Material-specific learning**: Different thresholds per material category
4. **Threshold history visualization**: Track learning progression over time
5. **Auto-adjustment scheduling**: Periodic threshold recalculation

## Conclusion

Dynamic threshold learning closes the gap between data collection and application. The system now truly learns from experience, automatically adjusting quality standards based on proven success patterns. This architectural shift transforms static configuration into adaptive intelligence, making the system genuinely self-improving over time.
