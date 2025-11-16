# Self-Learning Prompt System

**Status**: ✅ ACTIVE (November 15, 2025)  
**Location**: `processing/learning/prompt_optimizer.py`  
**Integration**: `DynamicGenerator`, `Orchestrator`, `UnifiedOrchestrator`

---

## Overview

The self-learning prompt system enables the z-beam-generator to **dynamically adapt and improve its own prompts** based on learned patterns from Winston AI feedback. This creates a continuous improvement loop where each generation makes the system smarter.

### The Core Concept

```
User provides simple context
       ↓
System generates initial prompt (from prompts/*.txt)
       ↓
PromptOptimizer.optimize_prompt() enhances with learned patterns
       ↓
Enhanced prompt → API generation
       ↓
Winston feedback captured
       ↓
PatternLearner updates database
       ↓
Next generation uses improved prompts (SELF-LEARNING LOOP)
```

---

## Architecture

### Components

1. **PromptOptimizer** (`processing/learning/prompt_optimizer.py`)
   - Analyzes historical Winston feedback
   - Identifies risky patterns (fail AI detection)
   - Identifies safe patterns (pass as human)
   - Dynamically enhances prompts before generation
   
2. **PatternLearner** (`processing/learning/pattern_learner.py`)
   - Learns from sentence-level Winston scores
   - Statistical analysis (minimum 3 occurrences, 70% fail rate)
   - Extracts 5-20 word phrases as patterns
   
3. **WinstonFeedbackDatabase** (`processing/detection/winston_feedback_db.py`)
   - Stores all detection results
   - Sentence-level analysis
   - Generation parameters
   - Enables cross-session learning

### Integration Points

The PromptOptimizer is integrated into **three** generation workflows:

#### 1. DynamicGenerator (Primary)
```python
# processing/generator.py
def generate(...):
    # Build base prompt
    prompt = self.prompt_builder.build_unified_prompt(...)
    
    # SELF-LEARNING: Optimize with learned patterns
    if self.prompt_optimizer and attempt == 1:
        result = self.prompt_optimizer.optimize_prompt(
            base_prompt=prompt,
            material=material_name,
            component_type=component_type,
            include_patterns=True,
            include_recommendations=True
        )
        
        if result['confidence'] != 'none':
            prompt = result['optimized_prompt']
            # Log optimization metrics
```

#### 2. Orchestrator
```python
# processing/orchestrator.py
def generate(...):
    prompt = PromptBuilder.build_unified_prompt(...)
    
    # SELF-LEARNING enhancement
    if self.prompt_optimizer and attempt == 1:
        optimization_result = self.prompt_optimizer.optimize_prompt(...)
        if optimization_result['confidence'] != 'none':
            prompt = optimization_result['optimized_prompt']
```

#### 3. UnifiedOrchestrator
```python
# processing/unified_orchestrator.py
def generate(...):
    prompt = self.prompt_builder.build_unified_prompt(...)
    
    # SELF-LEARNING enhancement
    if self.prompt_optimizer and attempt == 1:
        optimization_result = self.prompt_optimizer.optimize_prompt(...)
        if optimization_result['confidence'] != 'none':
            prompt = optimization_result['optimized_prompt']
```

---

## How It Works

### Learning Phase

1. **Generation Happens**: System generates content for a material/component
2. **Winston Analysis**: Each sentence gets a human score (0-100%)
3. **Database Logging**: Sentence text + score stored in `sentence_analysis` table
4. **Pattern Extraction**: PatternLearner identifies recurring phrases

### Pattern Classification

**Risky Patterns** (fail AI detection):
- Appear in 3+ failed sentences
- Have ≥70% failure rate
- Examples: "demonstrates the effectiveness", "leverages advanced technology"

**Safe Patterns** (pass as human):
- Appear in 3+ successful sentences  
- Have ≥70% success rate
- Examples: Natural conversational phrases, varied structures

### Optimization Phase

When generating new content:

1. **Load Historical Data**: Query database for material/component history
2. **Analyze Patterns**: Identify top risky and safe patterns
3. **Calculate Confidence**:
   - `high`: 20+ samples analyzed
   - `medium`: 10-19 samples
   - `low`: 5-9 samples
   - `none`: <5 samples (insufficient data)

4. **Enhance Prompt**:
   ```
   ORIGINAL PROMPT
   +
   ⚠️ CRITICAL: Avoid these AI-detected patterns:
   1. NEVER use: "demonstrates the" (detected as AI 90% of the time)
   2. NEVER use: "leverages advanced" (detected as AI 85% of the time)
   ...
   +
   ✅ ENCOURAGED: These patterns consistently pass as human:
   1. Emulate style of: "I've noticed..." (95% success rate)
   2. Emulate style of: "You'll find..." (92% success rate)
   ```

5. **Expected Improvement**: Statistical prediction based on pattern avoidance

---

## Output Example

When the system is active, you'll see logs like:

```
🧠 Prompt optimized with learned patterns:
   Confidence: high
   Patterns analyzed: 20
   Expected improvement: 37.0%
   + Added 5 risky pattern warnings
```

This means:
- System analyzed 20 historical patterns
- Has high confidence in recommendations (20+ samples)
- Predicts 37% improvement by avoiding risky patterns
- Added 5 specific warnings to the prompt

---

## Configuration

### Enable/Disable

PromptOptimizer is **automatically enabled** if Winston feedback database is configured:

```yaml
# processing/config.yaml
winston_feedback_db_path: "data/winston_feedback.db"
```

If database path is missing or invalid, PromptOptimizer gracefully degrades:
```
⚠️ Winston feedback database unavailable: ...
```

### Learning Thresholds

Configured in `processing/learning/pattern_learner.py`:

```python
PatternLearner(
    min_occurrences=3,    # Pattern must appear 3+ times
    min_fail_rate=0.7     # 70%+ failure rate = risky
)
```

---

## Testing

### Unit Tests

Location: `tests/test_prompt_optimizer_integration.py`

**Test Coverage:**
- ✅ Module exists and is importable
- ✅ DynamicGenerator integration (import, init, call)
- ✅ Orchestrator integration (import, init, call)
- ✅ UnifiedOrchestrator integration (import, init, call)
- ✅ Learning behavior with real database
- ✅ Insufficient data handling
- ✅ Pattern warning injection

**Run Tests:**
```bash
pytest tests/test_prompt_optimizer_integration.py -v
```

### Integrity Checks

The system includes automated integrity validation:

```bash
python3 run.py --integrity-check
```

**Checks:**
- ✅ PromptOptimizer module exists
- ✅ DynamicGenerator fully integrated
- ✅ Orchestrator fully integrated
- ✅ UnifiedOrchestrator fully integrated
- ✅ Database schema supports learning

If any check fails, generation is blocked until fixed.

---

## Data Flow

### Database Schema

**detection_results table:**
```sql
id | material | component_type | text | human_score | ai_score | timestamp
```

**sentence_analysis table:**
```sql
id | detection_id | sentence_text | human_score
```

**generation_parameters table:**
```sql
id | detection_id | temperature | voice_params | enrichment_params | ...
```

### Learning Pipeline

```
Generation
    ↓
Winston API Detection
    ↓
WinstonFeedbackDatabase.log_detection_result()
    ↓
WinstonFeedbackDatabase.log_sentence_analysis()
    ↓
PatternLearner.learn_patterns()
    ↓
PromptOptimizer.optimize_prompt() (next generation)
```

---

## Performance

### Optimization Speed

- **Database Query**: ~5-10ms for 100 samples
- **Pattern Analysis**: ~50-100ms for 707 patterns
- **Prompt Enhancement**: ~1-5ms

**Total Overhead**: <150ms per generation (negligible)

### Sample Requirements

| Samples | Confidence | Behavior |
|---------|------------|----------|
| 0-4     | none       | No optimization (insufficient data) |
| 5-9     | low        | Basic pattern warnings |
| 10-19   | medium     | Pattern warnings + recommendations |
| 20+     | high       | Full optimization with statistical confidence |

---

## Maintenance

### Adding New Pattern Types

Edit `processing/learning/pattern_learner.py`:

```python
def learn_patterns(self, material=None, component_type=None):
    # Add new pattern extraction logic
    # E.g., detect formulaic sentence openings
```

### Adjusting Thresholds

```python
# Stricter pattern detection (fewer false positives)
PatternLearner(min_occurrences=5, min_fail_rate=0.8)

# More aggressive learning (more patterns, potential false positives)
PatternLearner(min_occurrences=2, min_fail_rate=0.6)
```

### Database Cleanup

Prevent database bloat:

```python
# Delete old results (>30 days)
DELETE FROM detection_results 
WHERE timestamp < datetime('now', '-30 days');
```

---

## Troubleshooting

### Issue: "🧠 Prompt optimizer: Insufficient data"

**Cause**: Less than 5 samples for material/component  
**Solution**: Generate more content to build learning history

### Issue: PromptOptimizer not initialized

**Symptoms**: No "🧠" logs during generation  
**Check**:
1. Winston feedback database configured
2. Database file exists and is writable
3. Run integrity check: `python3 run.py --integrity-check`

### Issue: No pattern warnings added

**Cause**: All historical generations passed (no risky patterns learned)  
**Solution**: This is actually good! System is already generating human-like content

### Issue: Too many pattern warnings (prompt too long)

**Adjust**: Limit warnings in `PromptOptimizer.optimize_prompt()`:
```python
risky_patterns = patterns['risky_patterns'][:3]  # Only top 3
```

---

## Future Enhancements

### Phase 2: A/B Testing
```python
variants = optimizer.generate_variants(
    base_prompt,
    num_variants=3
)
# Test which prompt strategy works best
```

### Phase 3: Material-Specific Optimization
```python
# Learn what works for Aluminum vs Steel
optimizer.optimize_prompt(
    base_prompt,
    material="Aluminum",  # Aluminum-specific patterns
    component_type="caption"
)
```

### Phase 4: Multi-Provider Learning
```python
# Learn from Claude + DeepSeek + GPT feedback
optimizer.learn_from_multiple_providers([
    ('claude', 0.95),
    ('deepseek', 0.88),
    ('gpt4', 0.92)
])
```

---

## References

- **Core Implementation**: `processing/learning/prompt_optimizer.py`
- **Pattern Learning**: `processing/learning/pattern_learner.py`
- **Database Schema**: `processing/detection/winston_feedback_db.py`
- **Integration Tests**: `tests/test_prompt_optimizer_integration.py`
- **Integrity Validation**: `processing/integrity/integrity_checker.py`

---

## Success Metrics

**Before Self-Learning (Nov 14, 2025)**:
- Success Rate: 10%
- Human Score: 9.1% avg
- AI Score: 0.728 avg (too high)

**After Self-Learning (Nov 15, 2025)**:
- System learns from 707 risky patterns
- Confidence: high (20+ samples)
- Expected improvement: 37%
- **Target**: 50%+ success rate within 2 weeks

**Long-Term Goal (Dec 2025)**:
- Success Rate: 80%+
- Human Score: 60%+ avg
- AI Score: <0.30 avg
- Production-ready system
