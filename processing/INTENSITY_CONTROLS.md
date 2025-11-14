# Centralized Intensity Controls

**Location:** `/processing/config.yaml`  
**Manager:** `/processing/intensity_manager.py`  
**CLI Tool:** `/processing/intensity_cli.py`

---

## Overview

All voice and technical intensity controls are now centralized in a single configuration file at the top level of the `/processing` directory. This eliminates the need to edit individual voice profile files and provides a simple interface for adjusting content generation characteristics.

---

## Quick Start

### View Current Settings
```bash
python3 processing/intensity_cli.py status
```

### Change Voice Intensity
```bash
# Light: Minimal regional voice patterns
python3 processing/intensity_cli.py set voice light

# Moderate: Balanced, noticeable but clear (DEFAULT)
python3 processing/intensity_cli.py set voice moderate

# Strong: Pronounced, authentic regional characteristics
python3 processing/intensity_cli.py set voice strong
```

### Change Technical Intensity
```bash
# Accessible: Minimal jargon, focus on clarity
python3 processing/intensity_cli.py set technical accessible

# Balanced: Technical precision + readability (DEFAULT)
python3 processing/intensity_cli.py set technical balanced

# Expert: Dense technical content for specialists
python3 processing/intensity_cli.py set technical expert
```

### Apply Preset Combinations
```bash
# Conversational: light voice + accessible tech
python3 processing/intensity_cli.py preset conversational

# Professional: moderate voice + balanced tech (DEFAULT)
python3 processing/intensity_cli.py preset professional

# Academic: strong voice + expert tech
python3 processing/intensity_cli.py preset academic

# Authentic: strong voice + balanced tech
python3 processing/intensity_cli.py preset authentic

# Clinical: light voice + expert tech
python3 processing/intensity_cli.py preset clinical
```

---

## Configuration Structure

### Voice Intensity Profiles

Located in `config.yaml` under `voice_intensity`:

| Profile | Trait Frequency | Quirk Rate | Formality | Vocabulary |
|---------|----------------|------------|-----------|------------|
| **light** | 0.1-0.2 per ¶ | 0.05 per 200w | 80% | 70% unique |
| **moderate** | 0.2-0.4 per ¶ | 0.15 per 200w | 85% | 80% unique |
| **strong** | 0.5-0.7 per ¶ | 0.25 per 200w | 90% | 85% unique |

**Controls:**
- `trait_frequency_per_paragraph`: How often regional language patterns appear
- `quirk_rate_per_200_words`: Frequency of cultural/linguistic quirks
- `formality_percentage`: How formal/objective the tone is
- `unique_vocabulary_target`: Percentage of unique vocabulary (vs. repetition)

### Technical Intensity Profiles

Located in `config.yaml` under `technical_intensity`:

| Profile | Units/Sentence | Jargon | Complexity | Active Voice | Data Density |
|---------|---------------|--------|------------|--------------|--------------|
| **accessible** | 0.3 | minimal | simple (12-16w) | 80% | low |
| **balanced** | 0.6 | moderate | moderate (14-20w) | 65% | medium |
| **expert** | 1.0 | full | complex (18-24w) | 50% | high |

**Controls:**
- `units_per_sentence`: How many measurements/units per sentence
- `jargon_level`: Technical terminology density
- `sentence_complexity`: Average sentence length and structure
- `active_voice_percentage`: Ratio of active to passive voice
- `data_density`: How many numbers/metrics per paragraph

---

## Programmatic Usage

### In Python Code

```python
from processing.intensity_manager import IntensityManager

# Get intensity manager
manager = IntensityManager()

# Check current settings
print(manager.get_summary())

# Get specific settings
voice_settings = manager.get_voice_intensity_settings()
tech_settings = manager.get_technical_intensity_settings()

# Get all modifiers as dict
modifiers = manager.get_intensity_modifiers()

# Apply intensity to a prompt
base_prompt = "Write about laser cleaning of aluminum..."
enhanced_prompt = manager.apply_intensity_to_prompt(base_prompt)

# Change settings programmatically
manager.set_active_voice_profile('strong')
manager.set_active_technical_profile('expert')

# Get generation parameters (temperature, retries, etc.)
gen_params = manager.get_generation_params()
temperature = manager.calculate_temperature(attempt=3)
```

### Integration with Orchestrator

The orchestrator can now access centralized intensity settings:

```python
from processing.orchestrator import Orchestrator
from processing.intensity_manager import get_intensity_manager

# Get intensity manager
intensity_mgr = get_intensity_manager()

# Initialize orchestrator with intensity-aware settings
orchestrator = Orchestrator(api_client=api_client)

# Generate with current intensity settings
result = orchestrator.generate(
    topic="Aluminum",
    component_type="subtitle",
    author_id=1,
    length=25
)
# Intensity settings are automatically applied from config.yaml
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
