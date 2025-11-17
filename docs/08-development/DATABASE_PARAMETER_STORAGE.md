# Database Parameter Storage Architecture

**Date**: November 15, 2025  
**Status**: Proposed Enhancement  
**Purpose**: Store generation parameters in SQL database linked to learning data

---

## 🎯 Why Store Parameters in Database?

### Current Problem
Parameters are calculated but not persisted, so we can't:
- ❌ Analyze which parameter combinations work best
- ❌ Learn from successful generations
- ❌ Reproduce exact conditions of past attempts
- ❌ Track parameter drift over time
- ❌ Correlate parameters with Winston/Claude scores

### Solution Benefits
✅ **Machine Learning**: Train models on parameter → outcome data  
✅ **Reproducibility**: Recreate exact generation conditions  
✅ **Analysis**: "What temperature works best for Aluminum captions?"  
✅ **Optimization**: Automatically tune parameters based on history  
✅ **Debugging**: See exact parameters that led to failures  
✅ **A/B Testing**: Compare parameter strategies statistically

---

## 📊 Enhanced Database Schema

### New Table: `generation_parameters`

Stores complete parameter set for each generation attempt, linked to detection results.

```sql
CREATE TABLE IF NOT EXISTS generation_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Link to detection result (1:1 relationship)
    detection_result_id INTEGER UNIQUE NOT NULL,
    
    -- Metadata
    timestamp TEXT NOT NULL,
    material TEXT NOT NULL,
    component_type TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    
    -- API Parameters (what was sent to model)
    temperature REAL NOT NULL,
    max_tokens INTEGER NOT NULL,
    frequency_penalty REAL NOT NULL,
    presence_penalty REAL NOT NULL,
    
    -- Voice Parameters (0.0-1.0 range)
    trait_frequency REAL NOT NULL,
    opinion_rate REAL NOT NULL,
    reader_address_rate REAL NOT NULL,
    colloquialism_frequency REAL NOT NULL,
    structural_predictability REAL NOT NULL,
    emotional_tone REAL NOT NULL,
    imperfection_tolerance REAL NOT NULL,
    sentence_rhythm_variation REAL NOT NULL,
    
    -- Enrichment Parameters (1-3 scale)
    technical_intensity INTEGER NOT NULL,
    context_detail_level INTEGER NOT NULL,
    fact_formatting_style TEXT NOT NULL,
    engagement_level INTEGER NOT NULL,
    
    -- Validation Parameters
    detection_threshold REAL NOT NULL,
    readability_min REAL NOT NULL,
    readability_max REAL NOT NULL,
    grammar_strictness REAL NOT NULL,
    confidence_high REAL NOT NULL,
    confidence_medium REAL NOT NULL,
    
    -- Retry Behavior
    max_attempts INTEGER NOT NULL,
    retry_temperature_increase REAL NOT NULL,
    
    -- Full JSON snapshot (for extensibility)
    full_params_json TEXT NOT NULL,
    
    -- Computed at storage time
    param_hash TEXT NOT NULL,  -- Hash of all params for deduplication
    
    FOREIGN KEY (detection_result_id) REFERENCES detection_results(id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_params_material ON generation_parameters(material);
CREATE INDEX IF NOT EXISTS idx_params_component ON generation_parameters(component_type);
CREATE INDEX IF NOT EXISTS idx_params_temperature ON generation_parameters(temperature);
CREATE INDEX IF NOT EXISTS idx_params_penalties ON generation_parameters(frequency_penalty, presence_penalty);
CREATE INDEX IF NOT EXISTS idx_params_hash ON generation_parameters(param_hash);
CREATE INDEX IF NOT EXISTS idx_params_timestamp ON generation_parameters(timestamp);
```

### New Table: `parameter_presets`

Store successful parameter combinations as named presets for reuse.

```sql
CREATE TABLE IF NOT EXISTS parameter_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Preset metadata
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    created_from_detection_result_id INTEGER,  -- Which generation inspired this
    
    -- Target use case
    material_pattern TEXT,  -- NULL = applies to all, or regex pattern
    component_type TEXT,    -- NULL = applies to all
    
    -- Performance stats
    times_used INTEGER DEFAULT 0,
    success_rate REAL,
    avg_human_score REAL,
    avg_claude_score REAL,
    
    -- Parameters (same as generation_parameters)
    temperature REAL NOT NULL,
    max_tokens INTEGER NOT NULL,
    frequency_penalty REAL NOT NULL,
    presence_penalty REAL NOT NULL,
    
    -- Voice parameters
    trait_frequency REAL NOT NULL,
    opinion_rate REAL NOT NULL,
    reader_address_rate REAL NOT NULL,
    colloquialism_frequency REAL NOT NULL,
    structural_predictability REAL NOT NULL,
    emotional_tone REAL NOT NULL,
    imperfection_tolerance REAL NOT NULL,
    sentence_rhythm_variation REAL NOT NULL,
    
    -- Enrichment parameters
    technical_intensity INTEGER NOT NULL,
    context_detail_level INTEGER NOT NULL,
    fact_formatting_style TEXT NOT NULL,
    engagement_level INTEGER NOT NULL,
    
    -- Validation parameters
    detection_threshold REAL NOT NULL,
    readability_min REAL NOT NULL,
    readability_max REAL NOT NULL,
    grammar_strictness REAL NOT NULL,
    confidence_high REAL NOT NULL,
    confidence_medium REAL NOT NULL,
    
    -- Retry behavior
    max_attempts INTEGER NOT NULL,
    retry_temperature_increase REAL NOT NULL,
    
    full_params_json TEXT NOT NULL,
    
    FOREIGN KEY (created_from_detection_result_id) REFERENCES detection_results(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_preset_material ON parameter_presets(material_pattern);
CREATE INDEX IF NOT EXISTS idx_preset_component ON parameter_presets(component_type);
CREATE INDEX IF NOT EXISTS idx_preset_success ON parameter_presets(success_rate DESC);
```

### New Table: `parameter_experiments`

Track A/B tests and parameter optimization experiments.

```sql
CREATE TABLE IF NOT EXISTS parameter_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Experiment metadata
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT DEFAULT 'active',  -- active, completed, cancelled
    
    -- What's being tested
    hypothesis TEXT,  -- "Higher penalties reduce AI detection"
    parameter_varied TEXT NOT NULL,  -- Which parameter is being tested
    control_value REAL NOT NULL,
    treatment_values TEXT NOT NULL,  -- JSON array of values to test
    
    -- Target scope
    materials TEXT,  -- JSON array, NULL = all materials
    component_types TEXT,  -- JSON array, NULL = all types
    
    -- Results
    trials_completed INTEGER DEFAULT 0,
    trials_target INTEGER NOT NULL,
    results_json TEXT,  -- Statistical results
    winner TEXT,  -- Which value performed best
    confidence_level REAL,  -- Statistical confidence
    
    -- Learnings
    insights TEXT,
    recommendation TEXT
);

CREATE INDEX IF NOT EXISTS idx_experiment_status ON parameter_experiments(status);
CREATE INDEX IF NOT EXISTS idx_experiment_param ON parameter_experiments(parameter_varied);
```

---

## 🔗 Relationship Schema

```
detection_results (1) ←→ (1) generation_parameters
       ↓
       └──→ sentence_analysis (1:many)
       └──→ ai_patterns (1:many)
       └──→ corrections (1:many)

generation_parameters ──→ parameter_presets (inspiration)

claude_evaluations (separate, could be linked to detection_results)

parameter_experiments ──→ generation_parameters (via analysis queries)
```

---

## 💡 Powerful Queries Enabled

### 1. Find Best Parameters for Material
```sql
-- What temperature works best for Aluminum captions?
SELECT 
    p.temperature,
    AVG(d.human_score) as avg_human_score,
    COUNT(*) as attempts,
    SUM(CASE WHEN d.success = 1 THEN 1 ELSE 0 END) as successes
FROM generation_parameters p
JOIN detection_results d ON p.detection_result_id = d.id
WHERE d.material = 'Aluminum'
  AND d.component_type = 'caption'
GROUP BY ROUND(p.temperature, 1)
HAVING attempts >= 3
ORDER BY avg_human_score DESC;
```

### 2. Correlate Penalties with Success
```sql
-- Does increasing penalties improve human scores?
SELECT 
    CASE 
        WHEN p.frequency_penalty < 0.3 THEN 'Low (0-0.3)'
        WHEN p.frequency_penalty < 0.6 THEN 'Medium (0.3-0.6)'
        ELSE 'High (0.6+)'
    END as penalty_range,
    AVG(d.human_score) as avg_human_score,
    AVG(d.ai_score) as avg_ai_score,
    COUNT(*) as samples
FROM generation_parameters p
JOIN detection_results d ON p.detection_result_id = d.id
WHERE d.timestamp > datetime('now', '-30 days')
GROUP BY penalty_range
ORDER BY avg_human_score DESC;
```

### 3. Create Preset from Best Attempt
```sql
-- Save parameters from best Titanium subtitle generation
INSERT INTO parameter_presets (
    name, description, created_at, created_from_detection_result_id,
    material_pattern, component_type,
    temperature, frequency_penalty, presence_penalty, max_tokens,
    -- ... all other fields ...
    full_params_json
)
SELECT 
    'Titanium Subtitle Best' as name,
    'Parameters from highest human score (92%)' as description,
    datetime('now') as created_at,
    d.id as created_from_detection_result_id,
    'Titanium' as material_pattern,
    'subtitle' as component_type,
    p.temperature,
    p.frequency_penalty,
    p.presence_penalty,
    p.max_tokens,
    -- ... all other fields ...
    p.full_params_json
FROM generation_parameters p
JOIN detection_results d ON p.detection_result_id = d.id
WHERE d.material = 'Titanium'
  AND d.component_type = 'subtitle'
ORDER BY d.human_score DESC
LIMIT 1;
```

### 4. Analyze Exploration Strategy
```sql
-- Did exploration mode attempts perform better?
SELECT 
    d.attempt_number,
    AVG(d.human_score) as avg_score,
    COUNT(*) as attempts,
    AVG(ABS(p.temperature - 0.628)) as avg_temp_deviation
FROM generation_parameters p
JOIN detection_results d ON p.detection_result_id = d.id
WHERE d.timestamp > datetime('now', '-7 days')
GROUP BY d.attempt_number
ORDER BY d.attempt_number;
```

### 5. Predict Success Probability
```sql
-- Given new parameters, what's the probability of success?
-- (ML training data for success prediction model)
SELECT 
    p.temperature,
    p.frequency_penalty,
    p.presence_penalty,
    p.imperfection_tolerance,
    p.sentence_rhythm_variation,
    d.success as label,
    d.human_score,
    d.material,
    d.component_type
FROM generation_parameters p
JOIN detection_results d ON p.detection_result_id = d.id
WHERE d.timestamp > datetime('now', '-90 days')
ORDER BY d.timestamp;
```

---

## 🔧 Implementation

### Phase 1: Add Tables to Schema

Update `winston_feedback_db.py`:

```python
def _init_database(self):
    """Create tables if they don't exist."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        cursor.executescript("""
            -- Existing tables (detection_results, sentence_analysis, etc.)
            -- ...
            
            -- NEW: Generation parameters table
            CREATE TABLE IF NOT EXISTS generation_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_result_id INTEGER UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                material TEXT NOT NULL,
                component_type TEXT NOT NULL,
                attempt_number INTEGER NOT NULL,
                
                -- API parameters
                temperature REAL NOT NULL,
                max_tokens INTEGER NOT NULL,
                frequency_penalty REAL NOT NULL,
                presence_penalty REAL NOT NULL,
                
                -- Voice parameters
                trait_frequency REAL NOT NULL,
                opinion_rate REAL NOT NULL,
                reader_address_rate REAL NOT NULL,
                colloquialism_frequency REAL NOT NULL,
                structural_predictability REAL NOT NULL,
                emotional_tone REAL NOT NULL,
                imperfection_tolerance REAL NOT NULL,
                sentence_rhythm_variation REAL NOT NULL,
                
                -- Enrichment parameters
                technical_intensity INTEGER NOT NULL,
                context_detail_level INTEGER NOT NULL,
                fact_formatting_style TEXT NOT NULL,
                engagement_level INTEGER NOT NULL,
                
                -- Validation parameters
                detection_threshold REAL NOT NULL,
                readability_min REAL NOT NULL,
                readability_max REAL NOT NULL,
                grammar_strictness REAL NOT NULL,
                confidence_high REAL NOT NULL,
                confidence_medium REAL NOT NULL,
                
                -- Retry behavior
                max_attempts INTEGER NOT NULL,
                retry_temperature_increase REAL NOT NULL,
                
                -- Full snapshot
                full_params_json TEXT NOT NULL,
                param_hash TEXT NOT NULL,
                
                FOREIGN KEY (detection_result_id) REFERENCES detection_results(id) ON DELETE CASCADE
            );
            
            -- Indexes
            CREATE INDEX IF NOT EXISTS idx_params_material ON generation_parameters(material);
            CREATE INDEX IF NOT EXISTS idx_params_component ON generation_parameters(component_type);
            CREATE INDEX IF NOT EXISTS idx_params_temperature ON generation_parameters(temperature);
            CREATE INDEX IF NOT EXISTS idx_params_penalties ON generation_parameters(frequency_penalty, presence_penalty);
            CREATE INDEX IF NOT EXISTS idx_params_hash ON generation_parameters(param_hash);
            
            -- NEW: Parameter presets table
            CREATE TABLE IF NOT EXISTS parameter_presets (
                -- [schema as above]
            );
            
            -- NEW: Parameter experiments table  
            CREATE TABLE IF NOT EXISTS parameter_experiments (
                -- [schema as above]
            );
        """)
```

### Phase 2: Add Logging Methods

```python
def log_generation_parameters(
    self, 
    detection_result_id: int,
    params: Dict[str, Any]
) -> int:
    """
    Log complete parameter set used for generation.
    
    Args:
        detection_result_id: ID from detection_results table
        params: Parameters dict from GenerationParameters.to_dict()
        
    Returns:
        Row ID of inserted parameters
    """
    import hashlib
    
    # Calculate hash for deduplication
    param_str = json.dumps(params, sort_keys=True)
    param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
    
    conn = self._get_connection()
    cursor = conn.execute("""
        INSERT INTO generation_parameters (
            detection_result_id,
            timestamp,
            material,
            component_type,
            attempt_number,
            temperature,
            max_tokens,
            frequency_penalty,
            presence_penalty,
            trait_frequency,
            opinion_rate,
            reader_address_rate,
            colloquialism_frequency,
            structural_predictability,
            emotional_tone,
            imperfection_tolerance,
            sentence_rhythm_variation,
            technical_intensity,
            context_detail_level,
            fact_formatting_style,
            engagement_level,
            detection_threshold,
            readability_min,
            readability_max,
            grammar_strictness,
            confidence_high,
            confidence_medium,
            max_attempts,
            retry_temperature_increase,
            full_params_json,
            param_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        detection_result_id,
        datetime.now().isoformat(),
        params['material_name'],
        params['component_type'],
        params['attempt'],
        params['api']['temperature'],
        params['api']['max_tokens'],
        params['api']['frequency_penalty'],
        params['api']['presence_penalty'],
        params['voice']['trait_frequency'],
        params['voice']['opinion_rate'],
        params['voice']['reader_address_rate'],
        params['voice']['colloquialism_frequency'],
        params['voice']['structural_predictability'],
        params['voice']['emotional_tone'],
        params['voice']['imperfection_tolerance'],
        params['voice']['sentence_rhythm_variation'],
        params['enrichment']['technical_intensity'],
        params['enrichment']['context_detail_level'],
        params['enrichment']['fact_formatting_style'],
        params['enrichment']['engagement_level'],
        params['validation']['detection_threshold'],
        params['validation']['readability_min'],
        params['validation']['readability_max'],
        params['validation']['grammar_strictness'],
        params['validation']['confidence_high'],
        params['validation']['confidence_medium'],
        params['retry']['max_attempts'],
        params['retry']['retry_temperature_increase'],
        json.dumps(params),
        param_hash
    ))
    conn.commit()
    return cursor.lastrowid
```

### Phase 3: Link in Generator

In `processing/generator.py`:

```python
# After Winston detection
detection_result_id = self.feedback_db.log_detection_result(
    material=material_name,
    component_type=component_type,
    generated_text=content,
    human_score=winston_result['human_score'],
    ai_score=ai_score,
    # ... other fields
)

# NEW: Log parameters linked to detection result
self.feedback_db.log_generation_parameters(
    detection_result_id=detection_result_id,
    params=params.to_dict()  # GenerationParameters object
)
```

---

## 🚀 Advanced Use Cases

### 1. Automatic Parameter Tuning

```python
class ParameterOptimizer:
    """Learn optimal parameters from historical data"""
    
    def recommend_parameters(
        self,
        material: str,
        component_type: str
    ) -> GenerationParameters:
        """
        Recommend parameters based on historical success.
        
        Queries database for best-performing parameter sets
        for this material/component combination.
        """
        cursor = self.db.execute("""
            SELECT p.full_params_json
            FROM generation_parameters p
            JOIN detection_results d ON p.detection_result_id = d.id
            WHERE d.material = ?
              AND d.component_type = ?
              AND d.success = 1
            ORDER BY d.human_score DESC
            LIMIT 5
        """, (material, component_type))
        
        # Average the top 5 successful parameter sets
        top_params = [json.loads(row[0]) for row in cursor.fetchall()]
        
        if top_params:
            # Calculate ensemble parameters
            return self._ensemble_parameters(top_params)
        else:
            # Fall back to default calculation
            return self.dynamic_config.get_all_generation_params(
                component_type, material
            )
```

### 2. A/B Testing Framework

```python
def run_parameter_experiment(
    experiment_name: str,
    parameter: str,
    values: List[float],
    materials: List[str],
    trials_per_value: int = 10
):
    """
    Run A/B test comparing different parameter values.
    
    Example:
        run_parameter_experiment(
            experiment_name="Penalty Optimization",
            parameter="frequency_penalty",
            values=[0.0, 0.3, 0.6, 0.9],
            materials=["Aluminum", "Steel", "Titanium"],
            trials_per_value=10
        )
    """
    # Log experiment
    exp_id = db.create_experiment(
        name=experiment_name,
        parameter_varied=parameter,
        treatment_values=json.dumps(values),
        trials_target=len(values) * len(materials) * trials_per_value
    )
    
    # Run trials
    for material in materials:
        for value in values:
            for trial in range(trials_per_value):
                # Generate with this parameter value
                params = get_base_params(material)
                params = set_parameter(params, parameter, value)
                
                result = generate_with_params(material, params)
                
                # Results automatically linked via detection_result_id
```

### 3. Success Prediction Model

Train ML model to predict success probability before generation:

```python
# Export training data
training_data = db.execute("""
    SELECT 
        p.temperature,
        p.frequency_penalty,
        p.presence_penalty,
        p.imperfection_tolerance,
        p.sentence_rhythm_variation,
        d.material,
        d.component_type,
        d.success,
        d.human_score
    FROM generation_parameters p
    JOIN detection_results d ON p.detection_result_id = d.id
""").fetchall()

# Train model
from sklearn.ensemble import RandomForestClassifier

X = extract_features(training_data)
y = extract_labels(training_data)

model = RandomForestClassifier()
model.fit(X, y)

# Predict before generating
def should_generate_with_params(params: GenerationParameters) -> bool:
    """Return True if parameters likely to succeed"""
    features = params_to_features(params)
    prob = model.predict_proba([features])[0][1]  # Probability of success
    return prob > 0.7  # 70% confidence threshold
```

---

## ✅ Benefits Summary

| Feature | Without Params in DB | With Params in DB |
|---------|---------------------|-------------------|
| **Learning** | ❌ Can't learn from history | ✅ Train ML models on outcomes |
| **Reproducibility** | ❌ Can't recreate conditions | ✅ Exact parameter replay |
| **Analysis** | ❌ No correlation insights | ✅ Statistical analysis |
| **Optimization** | ❌ Manual tuning only | ✅ Automatic parameter tuning |
| **Debugging** | ❌ "What temperature was used?" | ✅ Complete audit trail |
| **A/B Testing** | ❌ Not possible | ✅ Systematic experiments |
| **Presets** | ❌ No reusable configs | ✅ Save successful combos |

---

## 🎯 Recommendation

**YES, absolutely store parameters in SQL database.**

**Implementation Priority**:
1. ✅ **HIGH**: Add `generation_parameters` table (links to detection_results)
2. ✅ **HIGH**: Add `log_generation_parameters()` method
3. ✅ **HIGH**: Link in generator after Winston detection
4. ✅ **MEDIUM**: Add `parameter_presets` table for saving successful configs
5. 🔮 **FUTURE**: Add `parameter_experiments` for A/B testing
6. 🔮 **FUTURE**: Build ML model for success prediction
7. 🔮 **FUTURE**: Automatic parameter optimizer

**Estimated Time**: 
- Core implementation (1-3): **1 hour**
- Preset system (4): **30 minutes**
- Total: **1.5 hours** for high-value functionality

This transforms the database from **passive logging** to **active learning system**.
