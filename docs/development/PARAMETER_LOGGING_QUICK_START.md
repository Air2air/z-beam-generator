# Parameter Logging Quick Start Guide

**For**: Developers debugging generation issues or analyzing parameter impact  
**Updated**: November 15, 2025

---

## 🎯 What Is This?

Every generation attempt now logs **31 parameter fields** to the database, enabling:
- **Debugging**: "What parameters were used when it failed?"
- **Learning**: "What temperature works best for Aluminum captions?"
- **Optimization**: "Should I increase penalties to improve human scores?"

---

## 📊 Quick Queries

### 1. Check Latest Parameters
```python
import sqlite3
conn = sqlite3.connect('data/winston_feedback.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT id, material, component_type, temperature, 
           frequency_penalty, presence_penalty, attempt_number
    FROM generation_parameters 
    ORDER BY id DESC LIMIT 10
''')

for row in cursor.fetchall():
    print(f'{row[1]} {row[2]}: temp={row[3]:.2f}, penalties={row[4]:.2f}/{row[5]:.2f}, attempt={row[6]}')
```

### 2. Find Best Parameters for Material
```python
from processing.detection.winston_feedback_db import WinstonFeedbackDatabase

db = WinstonFeedbackDatabase('data/winston_feedback.db')
best = db.get_best_parameters_for_material('Steel', 'caption', limit=5)

print(f'Top 5 parameter sets for Steel captions:')
for result in best:
    params = result['params']  # Extract params dict from result
    print(f'  Human Score: {result["human_score"]:.1f}%')
    print(f'  Temp: {params["api"]["temperature"]:.2f}')
    print(f'  Penalties: freq={params["api"]["frequency_penalty"]:.2f}, pres={params["api"]["presence_penalty"]:.2f}')
    print()
```

### 3. Analyze Parameter Correlation
```python
db = WinstonFeedbackDB()

# Does temperature affect success?
correlation = db.get_parameter_correlation('api.temperature', 'caption', days=30)

print('Temperature vs Human Score:')
for temp, stats in correlation.items():
    print(f'  {temp:.2f}: avg_human={stats["avg_human_score"]:.1f}%, samples={stats["count"]}')
```

### 4. Compare Parameters Across Attempts
```sql
-- Show all attempts for recent Aluminum caption generation
SELECT 
    p.attempt_number,
    p.temperature,
    p.frequency_penalty,
    d.human_score,
    d.ai_score,
    d.success
FROM generation_parameters p
JOIN detection_results d ON p.detection_result_id = d.id
WHERE d.material = 'Aluminum' AND d.component_type = 'caption'
    AND d.timestamp > datetime('now', '-1 hour')
ORDER BY p.attempt_number;
```

---

## 📋 Available Fields

### API Parameters (4 fields)
- `temperature` - Generation randomness (0.3-1.0)
- `max_tokens` - Token limit per generation
- `frequency_penalty` - Word repetition penalty (0.0-2.0)
- `presence_penalty` - Topic repetition penalty (0.0-2.0)

### Voice Parameters (8 fields)
- `trait_frequency` - How often author traits appear
- `opinion_rate` - Frequency of opinions
- `reader_address_rate` - Direct address frequency
- `colloquialism_frequency` - Informal language rate
- `structural_predictability` - Sentence pattern consistency
- `emotional_tone` - Emotional intensity
- `imperfection_tolerance` - Minor errors tolerance
- `sentence_rhythm_variation` - Rhythm diversity

### Enrichment Parameters (4 fields)
- `technical_intensity` - Technical detail level (1-3)
- `context_detail_level` - Context richness (1-3)
- `fact_formatting_style` - How facts are presented
- `engagement_level` - Reader engagement target (1-3)

### Validation Parameters (6 fields)
- `detection_threshold` - AI detection limit
- `readability_min` - Minimum readability score
- `readability_max` - Maximum readability score
- `grammar_strictness` - Grammar checking level
- `confidence_high` - High confidence threshold
- `confidence_medium` - Medium confidence threshold

### Retry Behavior (2 fields)
- `max_attempts` - Maximum generation attempts
- `retry_temperature_increase` - Temperature boost per retry

### Metadata (3 fields)
- `full_params_json` - Complete JSON snapshot
- `param_hash` - SHA-256 hash (first 16 chars) for deduplication
- `timestamp` - When parameters were used

---

## 🔍 Debugging Workflows

### "Why did generation fail?"
```python
# Get parameters from failed attempts
cursor.execute('''
    SELECT p.temperature, p.frequency_penalty, d.ai_score, d.failure_analysis
    FROM generation_parameters p
    JOIN detection_results d ON p.detection_result_id = d.id
    WHERE d.success = 0 AND d.material = 'YourMaterial'
    ORDER BY d.timestamp DESC LIMIT 5
''')
```

### "What's different about successful vs failed attempts?"
```python
# Compare averages
cursor.execute('''
    SELECT 
        d.success,
        AVG(p.temperature) as avg_temp,
        AVG(p.frequency_penalty) as avg_freq,
        AVG(d.human_score) as avg_human
    FROM generation_parameters p
    JOIN detection_results d ON p.detection_result_id = d.id
    WHERE d.component_type = 'caption'
    GROUP BY d.success
''')

success, fail = cursor.fetchall()
print(f'Success: temp={success[1]:.2f}, penalties={success[2]:.2f}, human={success[3]:.1f}%')
print(f'Failure: temp={fail[1]:.2f}, penalties={fail[2]:.2f}, human={fail[3]:.1f}%')
```

### "Are penalties helping or hurting?"
```python
# Group by penalty range
cursor.execute('''
    SELECT 
        ROUND(p.frequency_penalty, 1) as penalty_range,
        COUNT(*) as attempts,
        AVG(d.human_score) as avg_human_score,
        SUM(CASE WHEN d.success = 1 THEN 1 ELSE 0 END) as successes
    FROM generation_parameters p
    JOIN detection_results d ON p.detection_result_id = d.id
    WHERE d.component_type = 'caption'
    GROUP BY penalty_range
    ORDER BY penalty_range
''')
```

---

## 🎓 Machine Learning Examples

### Example 1: Train Regression Model
```python
import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestRegressor

# Load data
conn = sqlite3.connect('data/winston_feedback.db')
query = '''
    SELECT 
        p.temperature, p.frequency_penalty, p.presence_penalty,
        p.trait_frequency, p.opinion_rate, p.technical_intensity,
        d.human_score
    FROM generation_parameters p
    JOIN detection_results d ON p.detection_result_id = d.id
    WHERE d.component_type = 'caption'
'''
df = pd.read_sql_query(query, conn)

# Train model
X = df.drop('human_score', axis=1)
y = df['human_score']
model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# Feature importance
for feature, importance in zip(X.columns, model.feature_importances_):
    print(f'{feature}: {importance:.3f}')
```

### Example 2: Predict Best Parameters
```python
# Use trained model to predict human score for new parameters
new_params = {
    'temperature': 0.8,
    'frequency_penalty': 0.6,
    'presence_penalty': 0.6,
    # ... other 28 fields
}

predicted_human_score = model.predict([new_params.values()])
print(f'Expected human score: {predicted_human_score[0]:.1f}%')
```

---

## 🔗 Related Documentation

- **Database Schema**: `docs/development/DATABASE_PARAMETER_STORAGE.md`
- **Complete Implementation**: `DYNAMIC_PENALTIES_AND_PARAMETER_LOGGING_COMPLETE.md`
- **Hardcoded Value Policy**: `docs/development/HARDCODED_VALUE_POLICY.md`
- **Dynamic Config**: `processing/config/dynamic_config.py`

---

## 💡 Tips

1. **Start with high-level queries** - Use `get_best_parameters_for_material()` before writing SQL
2. **Join with detection_results** - Parameters alone don't tell the story; you need human_score
3. **Group by ranges** - `ROUND(temperature, 1)` groups similar values for analysis
4. **Use param_hash** - Identifies duplicate parameter sets across generations
5. **Index-aware queries** - Filter by material + component_type for fast lookups

---

**Quick Access**: All parameter logging happens automatically during generation. No manual intervention needed!
