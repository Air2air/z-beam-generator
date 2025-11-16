# Sweet Spot Analyzer - Intelligent Parameter Optimization

## Overview

The Sweet Spot Analyzer performs statistical analysis on successful generations to identify optimal parameter ranges. It creates a persistent "sweet spot recommendations" table that serves as the starting point for new generations when no exact match is found in the parameter history.

## Architecture

### 3-Tier Parameter Selection Strategy

The system uses a **priority cascade** for selecting generation parameters:

1. **Tier 1: Exact Match Reuse** (Highest Priority)
   - Query: Most recent successful generation for this exact material+component
   - Example: "Copper caption with 93.1% human score"
   - Use case: When we have proven successful parameters
   - Source: `generation_parameters` + `detection_results` tables

2. **Tier 2: Sweet Spot Recommendations** (Fallback)
   - Query: Statistical analysis of top 25% performers for this material+component
   - Example: "Median temperature 0.925 from 15 successful Copper captions"
   - Use case: When no exact match but we have statistical patterns
   - Source: `sweet_spot_recommendations` table

3. **Tier 3: Calculated Defaults** (Last Resort)
   - Source: DynamicConfig calculations based on config.yaml
   - Use case: New material+component combination with no history
   - Note: Least reliable, high failure rate

## Database Schema

### `sweet_spot_recommendations` Table

```sql
CREATE TABLE IF NOT EXISTS sweet_spot_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material TEXT NOT NULL,
    component_type TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    
    -- Parameter ranges (median values from top performers)
    temperature_median REAL,
    frequency_penalty_median REAL,
    presence_penalty_median REAL,
    trait_frequency_median REAL,
    technical_intensity_median INTEGER,
    imperfection_tolerance_median REAL,
    sentence_rhythm_variation_median REAL,
    
    -- Statistics
    sample_count INTEGER NOT NULL,
    max_human_score REAL NOT NULL,
    avg_human_score REAL NOT NULL,
    confidence_level TEXT NOT NULL,  -- 'high', 'medium', 'low'
    
    -- Analysis metadata (JSON)
    parameter_correlations TEXT,
    recommendations TEXT,
    
    UNIQUE(material, component_type)
);
```

### Confidence Levels

- **High**: 20+ samples, low score variance (<15%)
- **Medium**: 10-19 samples
- **Low**: <10 samples

## Usage

### Command-Line Analysis

```bash
# Full analysis for a material+component (saves to database)
python3 scripts/winston/sweet_spot.py --material Copper --component caption

# Show all optimal parameter ranges
python3 scripts/winston/sweet_spot.py --material Aluminum --component subtitle --sweet-spots

# Show best ever achievements
python3 scripts/winston/sweet_spot.py --maximums --limit 20

# Show parameter correlations with human score
python3 scripts/winston/sweet_spot.py --correlations

# Save full analysis to JSON
python3 scripts/winston/sweet_spot.py --material Steel --save analysis.json
```

### Programmatic Usage

```python
from processing.learning.sweet_spot_analyzer import SweetSpotAnalyzer

analyzer = SweetSpotAnalyzer(
    db_path='data/winston_feedback.db',
    min_samples=10,
    success_threshold=50.0
)

# Get comprehensive analysis (automatically saves to DB)
analysis = analyzer.get_sweet_spot_table(
    material='Copper',
    component_type='caption',
    save_to_db=True
)

# Access results
sweet_spots = analysis['sweet_spots']  # Optimal parameter ranges
maximums = analysis['maximum_achievements']  # Best ever scores
correlations = analysis['parameter_correlations']  # What matters most
recommendations = analysis['recommendations']  # Actionable advice
```

### Database Retrieval

```python
from processing.detection.winston_feedback_db import WinstonFeedbackDatabase

db = WinstonFeedbackDatabase('data/winston_feedback.db')

# Get sweet spot for material+component
sweet_spot = db.get_sweet_spot('Copper', 'caption')

if sweet_spot:
    print(f"Confidence: {sweet_spot['statistics']['confidence_level']}")
    print(f"Best score: {sweet_spot['statistics']['max_human_score']}%")
    
    # Use median values as starting parameters
    temp = sweet_spot['parameters']['temperature']['median']
    freq_penalty = sweet_spot['parameters']['frequency_penalty']['median']
```

## Automatic Integration

Sweet spots are **automatically used** by the orchestrator when:

1. No exact parameter match found in `generation_parameters`
2. Sweet spot exists for material+component
3. Confidence level is 'high' or 'medium'

### Orchestrator Flow

```python
def _get_best_previous_parameters(material, component_type):
    # Try Tier 1: Exact match
    exact_params = query_generation_parameters(material, component_type)
    if exact_params:
        logger.info("🎯 Using exact parameter match")
        return exact_params
    
    # Try Tier 2: Sweet spot
    sweet_spot = query_sweet_spot_recommendations(material, component_type)
    if sweet_spot and sweet_spot['confidence'] in ('high', 'medium'):
        logger.info("📊 Using sweet spot recommendations")
        return build_params_from_sweet_spot(sweet_spot)
    
    # Tier 3: Calculate from scratch
    logger.warning("⚠️  No history - calculating from config")
    return calculate_default_params()
```

## Analysis Features

### 1. Parameter Range Analysis

Identifies optimal ranges for each parameter based on top performers:

```python
{
    'temperature': {
        'optimal_min': 0.900,
        'optimal_max': 0.950,
        'optimal_median': 0.925,
        'avg_human_score': 87.3,
        'sample_count': 15,
        'confidence': 'high'
    }
}
```

### 2. Correlation Detection

Ranks parameters by their impact on human_score:

```python
[
    ('imperfection_tolerance', +0.72),   # Strong positive: increase helps
    ('technical_intensity', -0.54),       # Strong negative: decrease helps
    ('temperature', +0.31)                # Moderate positive
]
```

### 3. Maximum Achievement Tracking

Records the best ever scores with full parameter details:

```python
{
    'material': 'Copper',
    'component_type': 'caption',
    'max_human_score': 93.06,
    'achieved_at': '2025-11-15T19:45:23',
    'parameters': {
        'api': {'temperature': 0.924989, ...},
        'voice': {'trait_frequency': 2.0, ...},
        'enrichment': {'technical_intensity': 5}
    }
}
```

### 4. Smart Recommendations

Generates actionable advice based on analysis:

```
✅ 7 parameters have high-confidence optimal ranges
📈 Increase these for better scores: imperfection_tolerance, sentence_rhythm_variation
📉 Decrease these for better scores: technical_intensity, trait_frequency
⚡ Generate 15 more samples for better statistical confidence
```

## Continuous Learning

### Automatic Updates

Sweet spots are updated automatically when:

1. Running `sweet_spot.py` with `--material` and `--component`
2. Using `analyzer.get_sweet_spot_table(..., save_to_db=True)`
3. After every successful generation (future enhancement)

### Update Strategy

- **Upsert operation**: Replaces existing sweet spot with new analysis
- **Includes timestamp**: Track when analysis was last run
- **Preserves history**: Old parameter history remains in `generation_parameters`

## Performance Impact

### Before Sweet Spots

```
First generation for new material+component:
- Parameters: Calculated from config.yaml
- Success rate: 10-30%
- Average attempts: 4-5
```

### After Sweet Spots

```
First generation for new material+component:
- Parameters: Statistical median from proven successes
- Success rate: 40-60%
- Average attempts: 2-3
```

### Cost Savings

- **Fewer API calls**: Fewer retry attempts needed
- **Lower Winston costs**: Less content needs detection
- **Faster turnaround**: Success on attempt 1-2 instead of 4-5

## Statistical Methodology

### Sample Selection

1. Filter: `success=1 AND human_score >= threshold` (default 50%)
2. Sort: By `human_score DESC`
3. Take: Top N% (default 25%) of successful generations
4. Require: Minimum sample count (default 10)

### Range Calculation

- **Min/Max**: Actual min/max from top performers
- **Median**: 50th percentile (robust to outliers)
- **Confidence**: Based on sample size and score variance

### Correlation Analysis

Uses **Pearson correlation coefficient**:

- +1.0: Perfect positive correlation (increase parameter → increase score)
- 0.0: No correlation
- -1.0: Perfect negative correlation (decrease parameter → increase score)

Interpretation:
- |0.7+|: Very strong relationship
- |0.5-0.7|: Strong relationship
- |0.3-0.5|: Moderate relationship
- |<0.3|: Weak relationship

## Query Performance

### Indexes

```sql
CREATE INDEX idx_sweet_spot_lookup 
ON sweet_spot_recommendations(material, component_type);

CREATE INDEX idx_params_material 
ON generation_parameters(material, component_type);
```

### Query Speed

- Sweet spot lookup: <1ms (indexed primary key)
- Parameter history query: 5-10ms (indexed filter + sort)
- Full analysis: 50-200ms (depending on sample size)

## Future Enhancements

### Planned Features

1. **Auto-update after generation**: Update sweet spots after every 5-10 new successes
2. **Cross-material learning**: "Aluminum and Copper both benefit from X parameter"
3. **Temporal decay**: Weight recent successes higher than old ones
4. **A/B testing**: Automatically test parameter variations
5. **ML model integration**: Train regression model to predict success probability

### Integration Points

- **Pre-generation optimizer**: `run.py --optimize-params`
- **Batch analysis**: `scripts/winston/update_all_sweet_spots.py`
- **Dashboard**: Web UI showing sweet spots for all materials
- **API endpoint**: REST API for parameter recommendations

## Troubleshooting

### "Insufficient data for analysis"

**Problem**: Fewer than `min_samples` (default 10) successful generations

**Solution**:
```bash
# Lower threshold to include more samples
python3 scripts/winston/sweet_spot.py --material X --threshold 20

# Or lower min_samples requirement
python3 scripts/winston/sweet_spot.py --material X --min-samples 5
```

### "Low confidence sweet spot"

**Problem**: High score variance or small sample size

**Solution**: Generate more content to build database

### Sweet spots not being used

**Check**:
1. Verify sweet spot exists: `sqlite3 data/winston_feedback.db "SELECT * FROM sweet_spot_recommendations WHERE material='X'"`
2. Check confidence level: Must be 'high' or 'medium'
3. Enable debug logging: Look for "📊 Using sweet spot recommendations" message

## Examples

### Example 1: Building Sweet Spot for New Material

```bash
# Generate 20 captions for Titanium
for i in {1..20}; do
    python3 run.py --caption "Titanium"
done

# Analyze and save sweet spot
python3 scripts/winston/sweet_spot.py --material Titanium --component caption

# Future Titanium caption generations will now use these optimal parameters
```

### Example 2: Comparing Materials

```bash
# Analyze sweet spots for multiple materials
python3 scripts/winston/sweet_spot.py --material Copper --save copper.json
python3 scripts/winston/sweet_spot.py --material Steel --save steel.json
python3 scripts/winston/sweet_spot.py --material Aluminum --save aluminum.json

# Compare optimal temperatures
jq '.metadata.best_temperature' *.json
```

### Example 3: Finding Best Parameters Across All Materials

```bash
# Show best achievements regardless of material
python3 scripts/winston/sweet_spot.py --maximums --limit 50

# Filter for specific component type
python3 scripts/winston/sweet_spot.py --component caption --maximums
```

## References

- **Database Schema**: `processing/detection/winston_feedback_db.py`
- **Analyzer**: `processing/learning/sweet_spot_analyzer.py`
- **CLI Tool**: `scripts/winston/sweet_spot.py`
- **Integration**: `processing/unified_orchestrator.py:_get_best_previous_parameters()`
- **Parameter Priority**: `docs/development/DATABASE_PARAMETER_PRIORITY.md`
