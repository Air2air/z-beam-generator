# Image Pipeline Monitoring System

**Comprehensive failure tracking, prediction, and quality analysis for image generation pipeline**

## Overview

The Image Pipeline Monitoring System provides end-to-end visibility into the material image generation workflow, tracking failures, predicting issues, and analyzing quality trends across five critical stages:

1. **Research** - Contamination pattern research (JSON parsing, pattern completeness)
2. **Prompt Building** - Prompt construction (length, contradictions, missing data)
3. **Imagen Generation** - Image creation (API errors, timeouts, safety filters)
4. **Validation** - Quality checking (realism scores, physics, material accuracy)
5. **Post-Processing** - Output refinement (blur, color, texture issues)

## Features

### ✅ Failure Tracking
- Records all pipeline failures with full context
- Categorizes by stage and failure type
- Tracks severity (low, medium, high, critical)
- Maintains history (last 200 failures)
- Persists data across sessions

### 📊 Quality Trend Analysis
- Moving average of realism scores (last 50 generations)
- Trend detection (improving/declining/stable)
- Common validation issue frequency
- Actionable quality recommendations

### 🔮 Predictive Analytics
- Material-category-specific failure patterns
- Probability scoring for likely failures
- Pre-generation mitigation recommendations
- Historical pattern analysis

### 🛡️ Adaptive Response
- Dynamic prompt guidance based on failures
- Progressive repair strategies
- Automatic simplification when needed
- Material-specific optimizations

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   MaterialImageGenerator                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Research → Prompt Building → Imagen → Validation → Output│  │
│  └───────────┬──────────┬────────┬─────────┬─────────────────┘  │
│              │          │        │         │                     │
│              ▼          ▼        ▼         ▼                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          ImagePipelineMonitor (Global Instance)           │  │
│  │                                                            │  │
│  │  • record_failure()     • predict_likely_failures()       │  │
│  │  • record_success()     • get_quality_trend_analysis()    │  │
│  │  • record_validation()  • get_monitoring_report()         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Persistent Storage: domains/cache/pipeline_monitoring/   │  │
│  │    - pipeline_history.json (all tracking data)            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Usage

### Basic Integration

```python
from shared.image.utils.image_pipeline_monitor import (
    get_pipeline_monitor, FailureStage, FailureType
)

# Get global monitor instance
monitor = get_pipeline_monitor()

# Record a failure
monitor.record_failure(
    material="Steel",
    stage=FailureStage.RESEARCH,
    failure_type=FailureType.JSON_MALFORMED,
    severity="high",
    details={'error': 'Unterminated string at line 462'}
)

# Record a success
monitor.record_success("Aluminum", realism_score=85.5)

# Get predictions before generation
predictions = monitor.predict_likely_failures("Copper")
for pred in predictions:
    print(f"{pred['failure_type']}: {pred['probability']*100:.1f}% likely")
    print(f"  → {pred['recommendation']}")

# Get monitoring report
print(monitor.get_monitoring_report())
```

### Material Generator Integration

```python
class MaterialImageGenerator:
    def __init__(self):
        self.pipeline_monitor = get_pipeline_monitor()
    
    def generate_prompt(self, material_name, config):
        try:
            # ... research logic ...
            research_data = self.researcher.research(material_name)
        except json.JSONDecodeError as e:
            # JSON already tracked by PayloadMonitor
            raise
        except Exception as e:
            # Track general research failures
            self.pipeline_monitor.record_failure(
                material=material_name,
                stage=FailureStage.RESEARCH,
                failure_type=FailureType.GENERATION_ERROR,
                severity="high",
                details={'error': str(e)}
            )
            raise
```

### Validation Integration

```python
def validate_image(material, image_path):
    validator = MaterialImageValidator()
    result = validator.validate(image_path)
    
    # Record validation result
    monitor = get_pipeline_monitor()
    monitor.record_validation_result(material, result)
    
    # Track validation failures
    if not result['passed']:
        if result['realism_score'] < 60:
            monitor.record_failure(
                material,
                FailureStage.VALIDATION,
                FailureType.LOW_REALISM_SCORE,
                severity="medium",
                details={'score': result['realism_score']}
            )
```

## Failure Types Reference

### Research Phase
- `JSON_MALFORMED` - Invalid JSON structure (quotes, commas, unterminated strings)
- `MISSING_PATTERNS` - Insufficient contamination patterns (<5)
- `INSUFFICIENT_PHOTO_REFS` - Not enough reference URLs (<2 per pattern)

### Prompt Building
- `PROMPT_TOO_LONG` - Exceeds Imagen token limit (~2000 tokens)
- `CONTRADICTORY_INSTRUCTIONS` - Conflicting material/contamination descriptions
- `MISSING_MATERIAL_DATA` - Required properties not in Materials.yaml

### Imagen Generation
- `SAFETY_FILTER` - Content flagged as unsafe (rare but critical)
- `API_TIMEOUT` - Generation >60s (network/server issues)
- `API_RATE_LIMIT` - Too many requests (429 error)
- `GENERATION_ERROR` - Imagen service failure (500 errors)

### Validation
- `LOW_REALISM_SCORE` - Score <60/100
- `PHYSICS_VIOLATION` - Contamination defies physics
- `MATERIAL_MISMATCH` - Wrong material appearance
- `BEFORE_AFTER_INCONSISTENT` - Different objects/angles
- `AI_HALLUCINATION` - Invented contamination not in research

### Quality Degradation
- `BLURRY_OUTPUT` - Loss of sharpness/detail
- `COLOR_INACCURACY` - Wrong material colors
- `TEXTURE_UNREALISTIC` - Surface finish issues
- `COMPOSITION_POOR` - Framing/lighting problems

## Mitigation Strategies

| Failure Type | Recommended Action |
|--------------|-------------------|
| `JSON_MALFORMED` | Enable progressive JSON repair (3 levels), add format validation |
| `MISSING_PATTERNS` | Increase research depth, add fallback patterns |
| `INSUFFICIENT_PHOTO_REFS` | Require minimum 2 URLs per pattern |
| `PROMPT_TOO_LONG` | Enable prompt compression, prioritize critical details |
| `SAFETY_FILTER` | Review contamination descriptions, sanitize language |
| `LOW_REALISM_SCORE` | Add reference image comparison, strengthen physics |
| `PHYSICS_VIOLATION` | Enhance contamination physics validation |
| `MATERIAL_MISMATCH` | Improve material-specific appearance descriptions |
| `AI_HALLUCINATION` | Add reference image anchoring, increase photo URL weight |
| `BLURRY_OUTPUT` | Increase resolution guidance, add sharpness constraints |

## Monitoring Reports

### Example Report Output

```
================================================================================
🔍 IMAGE PIPELINE MONITORING REPORT
================================================================================

📈 Success Rate: 87.5% (35/40)
🔄 Total Failures: 5


📊 Failures by Stage:
   • research: 2 (40.0%)
   • validation: 2 (40.0%)
   • imagen_generation: 1 (20.0%)


⚠️  Top Failure Types:
   • json_malformed: 2
   • low_realism_score: 2
   • api_timeout: 1


🎨 Quality Trend:
   • Average Realism: 81.5/100
   • Trend: STABLE
   • Common Issues: physics, distribution


🚨 Recent Critical Failures: 1
   • Steel - json_malformed (research)

================================================================================
```

### Quality Trend Analysis

```python
trend = monitor.get_quality_trend_analysis()
# Returns:
{
    'average_realism': 81.5,
    'trend': 'stable',  # or 'improving', 'declining'
    'trend_magnitude': 2.3,
    'samples': 35,
    'common_issues': {'physics': 5, 'distribution': 3},
    'recommendation': 'Quality acceptable - maintain current approach'
}
```

### Failure Predictions

```python
predictions = monitor.predict_likely_failures("Steel")
# Returns:
[
    {
        'failure_type': 'json_malformed',
        'probability': 0.75,  # 75% likely
        'historical_count': 15,
        'recommendation': 'Enable progressive JSON repair, add format validation'
    },
    {
        'failure_type': 'physics_violation',
        'probability': 0.25,  # 25% likely
        'historical_count': 5,
        'recommendation': 'Enhance contamination physics validation in prompt'
    }
]
```

## Data Persistence

All monitoring data is automatically persisted to:
- **Location**: `domains/cache/pipeline_monitoring/pipeline_history.json`
- **Format**: JSON with timestamps
- **Contents**:
  - Total attempts and success counts
  - Failures by stage and type
  - Material-specific issue patterns
  - Recent failure records (last 200)

Data survives system restarts and is loaded automatically on next use.

## Testing

Run comprehensive test suite:

```bash
pytest tests/test_image_pipeline_monitoring.py -v
```

Test coverage:
- ✅ Failure recording (20 tests)
- ✅ Success tracking (15 tests)
- ✅ Quality trend analysis (12 tests)
- ✅ Failure prediction (10 tests)
- ✅ Persistence (8 tests)
- ✅ Integration (5 tests)

**Total**: 70 tests covering all monitoring functionality

## Performance

- **Memory**: ~50KB per 200 failures (typical: <500KB)
- **Disk**: ~100KB JSON file (compressed: ~25KB)
- **Overhead**: <5ms per operation (negligible)
- **Persistence**: Async writes, non-blocking

## Configuration

```python
# Custom history size
monitor = ImagePipelineMonitor(max_history=500)

# Custom cache location
monitor.cache_dir = "custom/path/to/cache"
```

## Best Practices

1. **Record all failures** - Even minor issues inform trends
2. **Use specific failure types** - Enables targeted mitigation
3. **Check predictions before generation** - Proactive failure prevention
4. **Monitor quality trends** - Early detection of degradation
5. **Review reports regularly** - Identify systemic issues
6. **Act on recommendations** - Automated suggestions guide fixes

## Integration Checklist

- [x] Import `get_pipeline_monitor()` in generator
- [x] Record failures in exception handlers
- [x] Record successes after generation
- [x] Record validation results
- [x] Check predictions pre-generation
- [x] Review monitoring reports
- [x] Add tests for monitoring calls
- [x] Document failure handling

## Future Enhancements

- **Real-time alerting** - Notify when critical failures spike
- **Dashboard visualization** - Web UI for monitoring data
- **Automatic prompt optimization** - ML-based prompt refinement
- **Cost tracking** - API usage and retry costs
- **A/B testing support** - Compare strategies
- **Export/import** - Share monitoring data across environments

## See Also

- `payload_monitor.py` - JSON conformity monitoring (research phase)
- `material_generator.py` - Generator integration
- `validator.py` - Validation result structure
- `test_image_pipeline_monitoring.py` - Complete test suite
