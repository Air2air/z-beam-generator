# Parameter Reference

**Complete reference for all 15 generation parameters**  
**Last Updated**: November 16, 2025  
**Scale**: All parameters use 1-10 slider values, normalized to 0.0-1.0 internally

---

## Overview

The system uses **15 parameters** across 4 categories to control content generation. All parameters use a consistent 1-10 scale that gets normalized to 0.0-1.0 for internal calculations.

**Normalization Formula**: `(slider_value - 1) / 9.0`
- Slider 1 → 0.000 (minimum)
- Slider 5 → 0.444 (medium)
- Slider 10 → 1.000 (maximum)

---

## Parameter Categories

### 1. Voice Parameters (9 parameters)

#### `sentence_rhythm_variation` (1-10)
- **Purpose**: Controls variety in sentence length and structure
- **Low (1-3)**: Uniform, predictable sentence patterns
- **Medium (4-7)**: Balanced variation
- **High (8-10)**: Highly varied, unpredictable rhythms
- **Location**: `processing/parameters/variation/sentence_rhythm_variation.py`

#### `imperfection_tolerance` (1-10)
- **Purpose**: Allows intentional "human-like" imperfections
- **Low (1-3)**: Perfect grammar, formal structure
- **Medium (4-7)**: Occasional colloquialisms, minor variations
- **High (8-10)**: Fragments, casual tone, deliberate imperfections
- **Location**: `processing/parameters/variation/imperfection_tolerance.py`

#### `jargon_removal` (1-10)
- **Purpose**: Controls technical terminology usage
- **Low (1-3)**: Technical terms allowed (MPa, GPa, nanometers)
- **Medium (4-7)**: Balanced technical and plain language
- **High (8-10)**: Plain language only, no technical specs
- **Location**: `processing/parameters/voice/jargon_removal.py`
- **Note**: Logic corrected Nov 16, 2025 (was inverted)

#### `professional_voice` (1-10)
- **Purpose**: Formality level of writing
- **Low (1-3)**: Casual, conversational
- **Medium (4-7)**: Professional but accessible
- **High (8-10)**: Formal, academic tone
- **Location**: `processing/parameters/voice/professional_voice.py`

#### `author_voice_intensity` (1-10)
- **Purpose**: How strongly author personality comes through
- **Low (1-3)**: Generic, neutral voice
- **Medium (4-7)**: Subtle author characteristics
- **High (8-10)**: Strong, distinctive author personality
- **Location**: `processing/parameters/voice/author_voice_intensity.py`

#### `personality_intensity` (1-10)
- **Purpose**: Personal opinions and perspectives
- **Low (1-3)**: Objective, factual only
- **Medium (4-7)**: Occasional personal insights
- **High (8-10)**: Strong opinions, personal anecdotes
- **Location**: `processing/parameters/voice/personality_intensity.py`

#### `engagement_style` (1-10)
- **Purpose**: Direct reader address and interaction
- **Low (1-3)**: Third-person, distant
- **Medium (4-7)**: Occasional "you" address
- **High (8-10)**: Conversational, direct engagement
- **Location**: `processing/parameters/voice/engagement_style.py`

#### `emotional_intensity` (1-10)
- **Purpose**: Emotional language and enthusiasm
- **Low (1-3)**: Neutral, measured tone
- **Medium (4-7)**: Moderate enthusiasm
- **High (8-10)**: Passionate, emotionally expressive
- **Location**: `processing/parameters/voice/emotional_intensity.py`

### 2. Technical Parameters (2 parameters)

#### `technical_language_intensity` (1-10)
- **Purpose**: Density of technical specifications
- **Low (1-3)**: Minimal technical details
- **Medium (4-7)**: Balanced technical content
- **High (8-10)**: Dense technical specifications
- **Location**: `processing/parameters/technical/technical_language_intensity.py`

#### `context_specificity` (1-10)
- **Purpose**: Level of contextual detail and explanation
- **Low (1-3)**: Brief, minimal context
- **Medium (4-7)**: Standard explanations
- **High (8-10)**: Comprehensive context and background
- **Location**: `processing/parameters/technical/context_specificity.py`

### 3. Variation Parameters (2 parameters)

#### `structural_predictability` (1-10)
- **Purpose**: Consistency vs. variety in content structure
- **Low (1-3)**: Highly consistent, predictable patterns
- **Medium (4-7)**: Moderate structural variation
- **High (8-10)**: Diverse, unpredictable structures
- **Location**: `processing/parameters/variation/structural_predictability.py`

#### `length_variation_range` (1-10)
- **Purpose**: Acceptable deviation from target word count
- **Low (1-3)**: Strict length targets (±10%)
- **Medium (4-7)**: Moderate flexibility (±30%)
- **High (8-10)**: Wide length tolerance (±60%)
- **Location**: `processing/parameters/variation/length_variation_range.py`

### 4. AI Detection Parameters (2 parameters)

#### `ai_avoidance_intensity` (1-10)
- **Purpose**: Effort to avoid AI detection patterns
- **Low (1-3)**: Minimal concern for AI detection
- **Medium (4-7)**: Balanced human-like writing
- **High (8-10)**: Aggressive AI pattern avoidance
- **Location**: `processing/parameters/ai_detection/ai_avoidance_intensity.py`

#### `humanness_intensity` (1-10)
- **Purpose**: Emphasis on human writing characteristics
- **Low (1-3)**: Allow uniform patterns
- **Medium (4-7)**: Standard human-like qualities
- **High (8-10)**: Maximum human authenticity
- **Location**: `processing/parameters/ai_detection/humanness_intensity.py`

---

## Parameter Interactions

### Composite Effects

**Plain Language Mode** (jargon_removal > 7):
- Excludes all technical specs from data enrichment
- Uses qualitative descriptions instead of measurements
- Overrides technical_language_intensity

**High Imperfection + High Rhythm** (both > 7):
- Enables sentence fragments
- Allows colloquialisms
- Increases temperature for more variation

**High Professional + Low Imperfection** (prof > 7, imperf < 3):
- Formal academic tone
- Perfect grammar enforced
- Minimal variation

---

## Configuration Locations

### Base Configuration
- **File**: `processing/config.yaml`
- **Section**: Global parameter defaults (1-10 scale)
- **Usage**: Initial values for all parameters

### Author-Specific Overrides
- **Files**: `processing/voice/profiles/*.yaml`
- **Authors**: USA, Italy, Indonesia, Taiwan
- **Format**: Offsets applied to base values

### Dynamic Calculation
- **File**: `processing/config/dynamic_config.py`
- **Class**: `DynamicConfig`
- **Method**: Converts 1-10 sliders to technical parameters (temperature, penalties, etc.)

---

## Parameter Flow

```
1. Load Base Config (config.yaml)
   ↓
2. Apply Author Offsets (voice/profiles/*.yaml)
   ↓
3. Normalize to 0.0-1.0 (dynamic_config.py)
   ↓
4. Generate Prompts (parameters/*.py)
   ↓
5. Store Results (winston_feedback_db)
   ↓
6. Learn Optimal Values (weight_learner.py)
```

---

## Learning System

### Database Storage
- **Table**: `generation_parameters`
- **Tracked**: All 15 parameters + API settings
- **Linked**: To `detection_results` via foreign key

### Sweet Spot Discovery
- **Threshold**: 110+ successful samples needed
- **Method**: Statistical analysis of top 20% performers
- **Output**: Median values for all parameters
- **Confidence**: Low/Medium/High based on sample size

### Adaptive Learning
- **Priority 1**: Most recent successful generation
- **Priority 2**: Sweet spot recommendations
- **Priority 3**: Calculated from sliders (fallback)

---

## Testing

### Parameter Tests
- **File**: `tests/test_parameter_implementation.py`
- **Coverage**: 
  - Parameter count validation (15 parameters)
  - Value range checks (0.0-1.0)
  - Prompt generation effectiveness
  - Documentation existence

### Integration Tests
- **File**: `tests/test_phase2_integration.py`
- **Coverage**:
  - Legacy vs modular mode compatibility
  - Parameter instance caching
  - Orchestration flow
  - Prompt builder integration

---

## Migration Notes

### From Old Scales

**Legacy 1-3 Scale** (deprecated):
```python
# OLD: if tech_intensity == 1:
# NEW: if tech_intensity < 0.15:  # Very low (slider 1-2)
```

**Legacy 0-100 Scale** (deprecated):
```python
# OLD: if param <= 30:
# NEW: if param < 0.3:  # Normalized equivalent
```

### Normalization Update (Nov 16, 2025)
- **Fixed**: Jargon removal inverted logic
- **Standardized**: All parameters to 1-10 → 0.0-1.0
- **Updated**: Enrichment params now normalized (was using raw 1-10)

---

## Quick Reference

| Slider | Normalized | Semantic | Threshold Check |
|--------|-----------|----------|-----------------|
| 1      | 0.000     | Minimum  | `< 0.15`        |
| 2      | 0.111     | Very Low | `< 0.15`        |
| 3      | 0.222     | Low      | `< 0.3`         |
| 4      | 0.333     | Low-Med  | `< 0.5`         |
| 5      | 0.444     | Medium   | `0.3-0.7`       |
| 6      | 0.556     | Med-High | `0.3-0.7`       |
| 7      | 0.667     | High     | `> 0.5`         |
| 8      | 0.778     | Very High| `> 0.7`         |
| 9      | 0.889     | Near Max | `> 0.7`         |
| 10     | 1.000     | Maximum  | `> 0.9`         |

---

## See Also

- `docs/08-development/PARAMETER_NORMALIZATION_NOV16_2025.md` - Migration guide
- `docs/LEARNING_INTEGRATION_QUICK_START.md` - Learning system overview
- `processing/parameters/README.md` - Implementation details
- `WEIGHT_LEARNING_ARCHITECTURE_NOV16_2025.md` - Statistical learning
