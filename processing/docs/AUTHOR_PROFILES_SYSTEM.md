# Author-Specific Configuration System

**Status**: ✅ Fully Implemented (November 14, 2025)

## Overview

The system now supports **per-author personality profiles** that create distinct writing styles while maintaining global control through base configuration sliders.

## Architecture

```
User Adjusts Global Slider (config.yaml)
    ↓
Base Value (e.g., imperfection_tolerance = 50)
    ↓
Author-Specific Offset Applied (author_profiles.yaml)
    ↓
Yi-Chun: 50 + (-15) = 35  (more precise)
Alessandro: 50 + (+5) = 55  (moderate imperfections)
Ikmanda: 50 + (+20) = 70  (most natural/human)
Todd: 50 + (+10) = 60  (conversational)
```

## Files

### 1. `processing/author_profiles.yaml`
Defines personality offsets for each of the 4 authors:

```yaml
authors:
  yi_chun_lin:
    author_id: 1
    personality: "Precise, methodical, evidence-focused"
    offsets:
      imperfection_tolerance: -15    # More precise
      technical_language_intensity: +15  # Higher technical density
      context_specificity: +20       # Very detailed
      # ... 10 total slider offsets
```

**Offset Ranges**: -30 to +30 (ensures final values stay in 0-100 range)

### 2. `processing/author_config_loader.py`
Applies author offsets to base configuration:

```python
from processing.author_config_loader import get_author_config

# Get config with Yi-Chun's offsets applied
config = get_author_config(author_id=1)

# Use with dynamic config
from processing.dynamic_config import DynamicConfig
dynamic = DynamicConfig(base_config=config)
temp = dynamic.calculate_temperature('subtitle')
```

### 3. `processing/author_comparison_matrix.py`
Visualization tool to compare all 4 authors:

```bash
python3 processing/author_comparison_matrix.py
```

## Author Personalities

### Yi-Chun Lin (Taiwan) - ID: 1
**Personality**: Precise, methodical, evidence-focused

| Characteristic | Offset | Final Value* |
|----------------|--------|--------------|
| Technical Language | +15 | 65 |
| Context Specificity | +20 | 75 |
| Imperfection Tolerance | -15 | **35** (most precise) |
| Structural Predictability | +10 | 55 |
| Engagement | -15 | 20 (most formal) |

**Writing Style**: Formal-logical with East Asian academic patterns, highly structured, data-driven

---

### Alessandro Moretti (Italy) - ID: 2
**Personality**: Sophisticated, elegant, balanced objectivity

| Characteristic | Offset | Final Value* |
|----------------|--------|--------------|
| Author Voice | +15 | 65 |
| Rhythm Variation | +15 | 65 |
| Length Variation | +20 | **70** (most varied) |
| Imperfection Tolerance | +5 | 55 |
| Structural Predictability | -5 | 40 |

**Writing Style**: Formal-objective with Italian EFL sophistication, elegant variation, nuanced

---

### Ikmanda Roswati (Indonesia) - ID: 3
**Personality**: Practical, accessible, efficiency-focused

| Characteristic | Offset | Final Value* |
|----------------|--------|--------------|
| Author Voice | +20 | 70 |
| Engagement | +20 | **55** (most conversational) |
| Imperfection Tolerance | +20 | **70** (most natural) |
| Technical Language | -15 | 35 (most accessible) |
| AI Avoidance | +15 | 65 |

**Writing Style**: Natural-accessible with Southeast Asian markers, practical focus, highly human

---

### Todd Dunning (USA) - ID: 4
**Personality**: Conversational academic, balanced engagement

| Characteristic | Offset | Final Value* |
|----------------|--------|--------------|
| Rhythm Variation | +20 | **70** (most varied rhythm) |
| Engagement | +15 | 50 |
| Length Variation | +15 | 65 |
| Structural Predictability | -10 | 35 (least predictable) |
| Imperfection Tolerance | +10 | 60 |

**Writing Style**: Conversational-academic with American directness, engaging, reader-friendly

*Assuming base value of 50 for demonstration

## Calculated Differences

When base config has all sliders at 50:

| Metric | Yi-Chun | Alessandro | Ikmanda | Todd |
|--------|---------|------------|---------|------|
| **Temperature** | 0.77 | 0.81 | 0.84 | 0.82 |
| **AI Threshold** | 37.0 | 39.2 | 40.8 | 40.8 |
| **Min Readability** | 55.5 | 58.5 | 62.0 | 60.0 |
| **Grammar Leniency** | 0.57 | 0.75 | 0.88 | 0.82 |
| **Technical Language** | 65 | 60 | 35 | 50 |
| **Imperfection Tolerance** | 35 | 55 | 70 | 60 |

**Range Spans**:
- Temperature: 0.07 range (0.77-0.84)
- Technical Language: 30-point range (35-65)
- Imperfection: 35-point range (35-70)
- Grammar Leniency: 0.31 range (0.57-0.88)

These are **significant differences** that create distinct writing styles.

## Integration

### In Generation Pipeline

```python
# Resolve author from material data
from data.authors.registry import resolve_author_for_generation
author = resolve_author_for_generation(material_data)
author_id = author['id']

# Get author-specific config
from processing.author_config_loader import get_author_config
config = get_author_config(author_id)

# Use dynamic config with author offsets
from processing.dynamic_config import DynamicConfig
dynamic = DynamicConfig(base_config=config)

# All calculations now reflect author personality
temperature = dynamic.calculate_temperature('subtitle')
threshold = dynamic.calculate_detection_threshold()
```

### Testing Author Differences

```bash
# Compare two authors
python3 -c "
from processing.author_config_loader import compare_author_configs
print(compare_author_configs(1, 3, 'subtitle'))  # Yi-Chun vs Ikmanda
"

# View all authors at once
python3 processing/author_comparison_matrix.py
```

## Benefits

### ✅ Global Control Preserved
- User adjusts ONE slider in `config.yaml`
- All authors shift together proportionally
- Example: Increase `imperfection_tolerance` by 20
  - Yi-Chun: 35 → 55
  - Alessandro: 55 → 75
  - Ikmanda: 70 → 90
  - Todd: 60 → 80

### ✅ Distinct Author Voices
- Yi-Chun always more precise than Ikmanda
- Alessandro always more varied than Yi-Chun
- Relationships preserved across config changes

### ✅ Persona File Synergy
The offsets work WITH the existing persona YAML files:
- **Persona files** (`prompts/personas/*.yaml`) provide linguistic patterns, voice examples, formatting rules
- **Author offsets** provide parameter tuning that matches those patterns
- Together they create fully differentiated authors

### ✅ No Breaking Changes
- Existing code continues to work
- Simply adds `get_author_config(author_id)` as new entry point
- Backward compatible with `ProcessingConfig()` for no-author scenarios

## Validation

The system ensures:
1. **Offset limits**: -30 to +30 prevents extreme values
2. **Value clamping**: Final values always in [0, 100] range
3. **Author ID validation**: Must match `data/authors/registry.py`
4. **Country matching**: Must have corresponding persona file

Run validation:
```bash
python3 processing/validate_config.py
```

## Future Enhancements

Potential additions:
1. **Per-component offsets**: Different offsets for subtitle vs description
2. **Dynamic offset learning**: Adjust offsets based on quality scores
3. **User-customizable offsets**: Allow per-project author tuning
4. **Offset presets**: "Formal", "Casual", "Technical" author groups

## Documentation

- Implementation: This file
- Usage examples: `processing/author_config_loader.py` docstrings
- Comparison tool: `processing/author_comparison_matrix.py`
- Profile definitions: `processing/author_profiles.yaml`

---

**Last Updated**: November 14, 2025  
**Status**: Production Ready ✅
