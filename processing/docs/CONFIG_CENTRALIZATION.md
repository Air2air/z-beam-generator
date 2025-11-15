# Slider-Driven Configuration Architecture

**Status**: Complete  
**Date**: November 14, 2025

## 🎯 Goal

Centralize ALL processing configuration in `processing/config.yaml` using a **slider-driven architecture** where 10 user-facing sliders (0-100 scale) automatically calculate all downstream technical parameters.

## 📋 Architecture Overview

### Single Source of Truth

```yaml
# processing/config.yaml

# ==============================================================================
# USER CONFIGS (The ONLY section you need to adjust)
# ==============================================================================
author_voice_intensity: 50          # 0-100: Regional voice patterns
personality_intensity: 40            # 0-100: Personal opinions  
engagement_style: 35                 # 0-100: Reader engagement
technical_language_intensity: 50    # 0-100: Technical density
context_specificity: 55              # 0-100: Detail level
sentence_rhythm_variation: 80        # 0-100: Structure variety
imperfection_tolerance: 80           # 0-100: Human-like quirks
structural_predictability: 45        # 0-100: Template adherence
ai_avoidance_intensity: 50           # 0-100: Pattern variation
length_variation_range: 50           # 0-100: Length flexibility

# ==============================================================================
# INFRASTRUCTURE (Static paths and base defaults)
# ==============================================================================
component_lengths:
  subtitle: { default: 15 }
  caption: { default: 25 }
  # ... more components

voice:
  authors:
    1: "united_states"
    2: "italy"
    # ... more authors

data_sources:
  materials_yaml: "data/materials/Materials.yaml"
  # ... more paths
```

### Layered Calculation System

```
config.yaml (10 sliders)
    ↓
config_loader.py (reads YAML, provides raw values)
    ↓
    ├─→ dynamic_config.py (calculates technical params)
    │     • Temperature: 0.7-1.0
    │     • Max tokens: 150-1000
    │     • Retry behavior: 3-7 attempts
    │     • Detection threshold: 0.25-0.40
    │     • 30+ calculated parameters
    │
    └─→ author_config_loader.py (applies personality offsets)
          • Yi-Chun: -15 imperfection (precise)
          • Alessandro: +20 length_variation (varied)
          • Ikmanda: +20 imperfection (natural)
          • Todd: +20 rhythm (engaging)
```

## 🔧 How It Works

### 1. User Adjusts Slider

```bash
python3 -m processing.intensity.intensity_cli set rhythm 70
```

Updates `config.yaml`:
```yaml
sentence_rhythm_variation: 70  # Was 50, now 70
```

### 2. Config Loader Reads Value

```python
from processing.config.config_loader import ProcessingConfig

config = ProcessingConfig()
rhythm_value = config.get_sentence_rhythm_variation()  # Returns 70
```

### 3. Dynamic Config Calculates Parameters

```python
from processing.config.dynamic_config import DynamicConfig

dynamic = DynamicConfig()

# Calculates coefficient of variation from slider
# Formula: 0.15 + (slider/100 * 0.45)
cv = 0.15 + (70/100 * 0.45)  # = 0.465 (46.5% variation)

# Also affects temperature calculation
# Formula: 0.7 + ((ai_avoid + rhythm)/200 * 0.3)
temp = 0.7 + ((50 + 70)/200 * 0.3)  # = 0.88
```

### 4. Orchestrator Uses Calculated Values

```python
orchestrator = Orchestrator(api_client, dynamic_config=dynamic)

result = orchestrator.generate(...)
# Internally uses:
#   - temperature = 0.88 (from calculation)
#   - sentence variation = 46.5% (from calculation)
#   - max_tokens = dynamically calculated
#   - retry_attempts = dynamically calculated
```

### 5. Author Offsets Applied (Optional)

```python
from processing.config.author_config_loader import get_author_config

# Get author-specific config (applies offsets)
author_config = get_author_config(author_id=2)  # Alessandro

# Alessandro has +15 offset for rhythm
# Final value: 70 + 15 = 85 (more varied than base)
```

## 📊 Component Integration Status

| Component | Integration | Notes |
|-----------|------------|-------|
| **orchestrator.py** | ✅ Complete | Uses DynamicConfig for all parameters |
| **dynamic_config.py** | ✅ Complete | Calculates 30+ params from sliders |
| **config_loader.py** | ✅ Complete | Provides typed access to sliders |
| **author_config_loader.py** | ✅ Complete | Applies personality offsets |
| **component_specs.py** | ✅ Complete | Calculates length ranges from slider |
| **ai_detection.py** | ✅ Complete | Uses config for thresholds |
| **validate_config.py** | ✅ Complete | Validates slider ranges (0-100) |
| **intensity_cli.py** | ✅ Complete | User interface to sliders |

## 🎯 Benefits

### 1. Zero Hardcoded Values
Every technical parameter calculated from sliders:
- Temperature: `0.7 + (sliders → formula) → 1.0`
- Max tokens: `base_length + (slider → variance)`
- Retry attempts: `3 + (slider → +0 to +4)`
- Thresholds: `0.25 + (slider → formula) → 0.40`

### 2. Single Point of Control
```bash
# Change ONE slider
python3 -m processing.intensity.intensity_cli set rhythm 80

# Affects:
# - Temperature calculation
# - Sentence variation coefficient
# - Prompt instruction generation
# - Quality threshold adjustments
# 30+ parameters recalculate automatically
```

### 3. Author Personality Preservation
```yaml
# Base slider: 50
# Yi-Chun offset: -15 → Final: 35 (precise)
# Alessandro offset: +5 → Final: 55 (balanced)
# Ikmanda offset: +20 → Final: 70 (natural)

# Increase base by 10:
# Yi-Chun: 35 → 45
# Alessandro: 55 → 65  
# Ikmanda: 70 → 80
# All authors shift proportionally
```

### 4. Easy Experimentation
```bash
# Try high rhythm variation
python3 -m processing.intensity.intensity_cli set rhythm 90
python3 run.py --material "Aluminum"

# Check results, adjust
python3 -m processing.intensity.intensity_cli set rhythm 70

# No code changes needed
```

## 🔍 Testing

### Manual Test
```bash
python3 processing/validate_config.py
```

### Integration Test
```python
from processing.config_loader import get_config
from processing.detection.ai_detection import AIDetector

# Verify config is used
config = get_config()
detector = AIDetector()

assert detector.ai_threshold == config.get_ai_threshold()
print("✅ AI detector using centralized config")
```

### End-to-End Test
```bash
# Generate content and verify it uses config settings
python3 run.py --material "Aluminum" --component subtitle
```

## 📝 Best Practices

### For New Components

**❌ DON'T:**
```python
class MyComponent:
    def __init__(self):
        self.threshold = 0.5  # WRONG: Hardcoded
        self.max_attempts = 3  # WRONG: Hardcoded
```

**✅ DO:**
```python
from processing.config_loader import get_config

class MyComponent:
    def __init__(self):
        config = get_config()
        self.threshold = config.get_ai_threshold()
        self.max_attempts = config.get_max_attempts()
```

### For Modifying Config

**❌ DON'T:**
```python
# WRONG: Editing YAML by hand can break validation
with open('processing/config.yaml', 'w') as f:
    f.write('threshold: 50\n')  # No validation!
```

**✅ DO:**
```bash
# RIGHT: Use CLI tool with built-in validation
python3 processing/intensity_cli.py set ai 60

# Or validate after manual edit
vim processing/config.yaml
python3 processing/validate_config.py
```

## 🆘 Troubleshooting

### "Config validation failed"

Run validator to see specific errors:
```bash
python3 processing/validate_config.py
```

### "Could not load from processing/config.yaml"

Check that `processing/config.yaml` exists and is valid YAML:
```bash
ls -la processing/config.yaml
python3 -c "import yaml; yaml.safe_load(open('processing/config.yaml'))"
```

### "Component using hardcoded values"

Search for the hardcoded value:
```bash
grep -r "threshold = 0.5" processing/
```

Then replace with:
```python
from processing.config_loader import get_config
config = get_config()
threshold = config.get_ai_threshold()
```

## 🎉 Benefits

1. **Single Source of Truth**: All configs in one place
2. **Type Safety**: Typed accessors prevent errors
3. **Validation**: Catch config errors before runtime
4. **Easy Modification**: Change once, affects everywhere
5. **No Hardcoding**: All values are configurable
6. **Fail-Fast**: Invalid configs caught immediately
7. **Documentation**: Config file self-documents via comments

## 📚 Related Files

- `processing/config.yaml` - Central configuration file
- `processing/config_loader.py` - Configuration loader
- `processing/validate_config.py` - Validation tool
- `processing/detection/ai_detection_patterns.txt` - Pattern definitions
- `processing/intensity_cli.py` - User-facing config interface
