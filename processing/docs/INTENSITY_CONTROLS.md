# 10-Slider Intensity Control System

**Location:** `/processing/config.yaml`  
**CLI Tool:** `python3 -m processing.intensity.intensity_cli`  
**Architecture:** Slider-driven with dynamic calculation

---

## Overview

All voice and technical intensity controls are centralized in **10 user-facing sliders** (0-100 scale) in `processing/config.yaml`. These sliders automatically calculate all downstream technical parameters - no hardcoded values, no separate profile system.

**Key Concept:** Change a slider → 30+ technical parameters recalculate automatically.

---

## Quick Start

### View Current Settings
```bash
python3 -m processing.intensity.intensity_cli status
```

### Change Individual Sliders
```bash
# Increase human realism markers
python3 -m processing.intensity.intensity_cli set rhythm 70
python3 -m processing.intensity.intensity_cli set imperfection 60

# Adjust author voice
python3 -m processing.intensity.intensity_cli set voice 65

# Reduce AI patterns
python3 -m processing.intensity.intensity_cli set ai 75
```

### Test Settings
```bash
python3 -m processing.intensity.intensity_cli test
```

---

## Configuration Structure

### The 10 Sliders (0-100 scale)

Located in `config.yaml` under **USER CONFIGS** section:

#### **Content Characteristics (1-4)**

| # | Slider | What It Controls | Default |
|---|--------|------------------|---------|
| **1** | `author_voice_intensity` | Regional voice patterns, cultural markers, linguistic traits | 50 |
| **2** | `personality_intensity` | Personal opinions, evaluative language, subjective assessments | 40 |
| **3** | `engagement_style` | Reader awareness, direct address, conversational tone | 35 |
| **4** | `technical_language_intensity` | Jargon density, measurements per sentence, technical depth | 50 |

#### **Human Realism Markers (5-10)**

| # | Slider | What It Controls | Default |
|---|--------|------------------|---------|
| **5** | `context_specificity` | Detail level, concrete scenarios, practical examples | 55 |
| **6** | `sentence_rhythm_variation` | Sentence structure variety, length diversity (KEY) | 80 |
| **7** | `imperfection_tolerance` | Human-like quirks, minor flaws, authentic imperfections | 80 |
| **8** | `structural_predictability` | Template adherence vs. organic flow, pattern-breaking | 45 |
| **9** | `ai_avoidance_intensity` | Pattern variation intensity, detection avoidance | 50 |
| **10** | `length_variation_range` | Length flexibility (±% from target), word count tolerance | 50 |

### Scale Interpretation

- **0-30:** Low intensity (minimal effect, more AI-like/polished)
- **31-60:** Moderate intensity (balanced, default ~50)
- **61-100:** High intensity (pronounced effect, maximum authenticity)

---

## Programmatic Usage

### In Python Code

```python
from processing.config.dynamic_config import DynamicConfig
from processing.config.author_config_loader import get_author_config

# Get base configuration
config = DynamicConfig()

# Calculate technical parameters from sliders
temperature = config.calculate_temperature('subtitle')  # 0.7-1.0
max_tokens = config.calculate_max_tokens('subtitle')    # 150-250
retry_behavior = config.calculate_retry_behavior()     # {'max_attempts': 3-7, ...}
threshold = config.calculate_detection_threshold()     # 0.25-0.40

# Get author-specific configuration (applies personality offsets)
author_config = get_author_config(author_id=2)  # Alessandro
author_dynamic = DynamicConfig(base_config=author_config)

# Alessandro's calculated values differ from base due to offsets
alessandro_temp = author_dynamic.calculate_temperature('subtitle')
```

### Integration with Orchestrator

```python
from processing.orchestrator import Orchestrator
from processing.config.dynamic_config import DynamicConfig
from processing.config.author_config_loader import get_author_config

# Get author-specific config
author_config = get_author_config(author_id=2)
dynamic_config = DynamicConfig(base_config=author_config)

# Initialize orchestrator with dynamic settings
orchestrator = Orchestrator(
    api_client=api_client,
    dynamic_config=dynamic_config
)

# Generate - automatically uses calculated parameters
result = orchestrator.generate(
    topic="Aluminum",
    component_type="subtitle",
    author_id=2
)
# Uses: dynamic temperature, dynamic tokens, dynamic thresholds
```

---

## How It Works

### 1. Configuration Loading
All settings are loaded from `/processing/config.yaml` at initialization.

### 2. Profile Selection
The `active_profile` field in each section determines which profile is used:
```yaml
voice_intensity:
  active_profile: "moderate"  # ← Change this
  
technical_intensity:
  active_profile: "balanced"  # ← Change this
```

### 3. Prompt Modification
When generating content, the system:
1. Loads the active profiles
2. Builds intensity instructions
3. Prepends them to the generation prompt
4. AI receives explicit parameters to follow

### 4. Dynamic Adjustment
Settings can be changed:
- **Via CLI:** `intensity_cli.py` (persists to disk)
- **Via Code:** `IntensityManager` methods (in-memory)
- **Via Direct Edit:** Modify `config.yaml` directly

---

## Example Output

### Moderate Voice + Balanced Technical (Default)
```
Laser cleaning typically restores aluminum's lightweight oxide-resistant surface 
at 1064 nm wavelength, distinctly preventing recontamination while maintaining 
essential structural integrity for aerospace applications with 92% efficiency.
```

### Strong Voice + Expert Technical
```
Ablation stays at 1.2 J/cm², which keeps thermal effects to 50 μm depth maximum, 
Ra measuring 0.8 μm post-process. Scans show oxide removal at 3.5 g/min throughput 
without substrate phase shifts, unlike mechanical abrasion processes that induce 
15-20 μm surface deformation patterns under 500 MPa contact stress.
```

### Light Voice + Accessible Technical
```
Laser cleaning effectively removes surface contaminants from aluminum while 
preserving the base material. The process uses controlled energy to target 
only unwanted layers, leaving the original surface intact and ready for use.
```

---

## Preset Combinations

| Preset | Voice | Technical | Best For |
|--------|-------|-----------|----------|
| **conversational** | light | accessible | Marketing copy, blog posts |
| **professional** | moderate | balanced | Standard technical documentation |
| **academic** | strong | expert | Research papers, journals |
| **authentic** | strong | balanced | Authentic author content with clarity |
| **clinical** | light | expert | Dense technical specs with minimal personality |

---

## Troubleshooting

### Settings Not Applied
1. Check active profiles in `config.yaml`
2. Reload config: `manager.reload_config()`
3. Verify CLI changes persisted: `intensity_cli.py status`

### Unexpected Output
- Higher intensity = more variation (may seem inconsistent)
- Lower intensity = more standard (may seem generic)
- Adjust in small increments to find optimal balance

### Want Even More Control?
- Edit individual voice profiles: `/processing/voice/profiles/*.yaml`
- Modify base prompts: `/prompts/*.txt`
- Adjust detection thresholds: `config.yaml` → `ai_detection` section

---

## Migration Notes

### Before (Old System)
- Intensity settings scattered across 4 voice profile files
- Had to edit YAML files manually
- No centralized control
- Settings hard-coded in profiles

### After (New System)
- All settings in one place: `config.yaml`
- Simple CLI for changes
- Programmatic access via `IntensityManager`
- Profiles inherit from central config

### Backwards Compatibility
Individual voice profile files still exist and work independently. The new system **overlays** centralized settings on top of base profiles. You can still customize individual author voices if needed.

---

## Best Practices

1. **Start with defaults** (`moderate` + `balanced`)
2. **Adjust incrementally** (one profile at a time)
3. **Test after changes** (`intensity_cli.py test`)
4. **Use presets** for common scenarios
5. **Document custom settings** if you deviate significantly

---

## Future Enhancements

Potential additions:
- [ ] Per-component intensity overrides
- [ ] Per-author intensity customization
- [ ] Real-time intensity adjustment based on feedback
- [ ] Intensity validation/testing suite
- [ ] Web UI for non-technical users

---

## Support

**Issues?** Check:
1. `config.yaml` syntax (valid YAML)
2. Active profile names match available profiles
3. IntensityManager initialization succeeds
4. CLI commands execute without errors

**Questions?** See:
- `/processing/intensity_manager.py` - Core implementation
- `/processing/config.yaml` - Full configuration
- `/processing/intensity_cli.py` - CLI source code
