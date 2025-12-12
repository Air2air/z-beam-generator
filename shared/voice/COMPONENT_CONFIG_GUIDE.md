# Component Voice Configuration Guide

**Version:** 1.0.0  
**Created:** 2025-10-25  
**Purpose:** Configure Author Voice parameters per component type

---

## 📋 Overview

The **Component Voice Configuration System** allows you to control intensity levels, formality, and other voice parameters on a per-component basis without modifying generator code.

**Architecture:**
```
Generator → VoiceOrchestrator.get_unified_prompt(component_type) → component_config.yaml
                                      ↓
                           intensity_level, formality, target_audience
                                      ↓
                           voice_base.yaml (intensity rules)
                                      ↓
                           Final prompt with country-specific voice
```

---

## 🎯 How It Works

### 1. **Component Config** (`voice/component_config.yaml`)

Maps component types to voice parameters:

```yaml
subtitle:
  intensity_level: "level_2_light"  # Light technical
  formality: "professional-engaging"
  target_audience: "technical professionals and decision-makers"
  word_count_range: [8, 12]
```

### 2. **VoiceOrchestrator** (`voice/orchestrator.py`)

Reads config and applies to prompts:

```python
# In _build_subtitle_prompt():
config = self.get_component_config('subtitle')
intensity_level = config.get('intensity_level', 'level_2_light')
intensity_rules = base_voice.get('technical_authority_intensity', {}).get(intensity_level, {})
```

### 3. **Generator** (e.g., `components/subtitle/generators/generator.py`)

Just passes component type - **no hardcoded intensity**:

```python
prompt = voice.get_unified_prompt(
    component_type='subtitle',  # ← VoiceOrchestrator reads config
    material_context=material_context,
    author=author_dict,
    target_words=target_words
)
```

---

## 🔧 Usage Examples

### Example 1: Change Subtitle Intensity

**Want more technical subtitles?**

Edit `voice/component_config.yaml`:

```yaml
subtitle:
  intensity_level: "level_3_moderate"  # Was level_2_light
  # Now allows 1 measurement instead of max 1 simple measurement
```

**Result:** Subtitles will include more technical detail.

### Example 2: Add New Component

**Adding a "summary" component:**

1. **Add to config** (`voice/component_config.yaml`):

```yaml
summary:
  intensity_level: "level_2_light"
  formality: "professional-accessible"
  target_audience: "general technical audience"
  word_count_range: [40, 60]
  
  required_elements:
    - "Material overview"
    - "Key benefit"
    - "Primary application"
```

2. **Add to VoiceOrchestrator** (`voice/orchestrator.py`):

```python
def get_unified_prompt(...):
    # ... existing code ...
    elif component_type == 'summary':
        return self._build_summary_prompt(
            base_voice=base_voice,
            country_profile=country_profile,
            material_context=material_context,
            author=author,
            **kwargs
        )
```

3. **Implement builder method**:

```python
def _build_summary_prompt(self, base_voice, country_profile, material_context, author, **kwargs):
    config = self.get_component_config('summary')
    intensity_level = config.get('intensity_level')
    # ... build prompt using config ...
```

4. **Generator uses it**:

```python
prompt = voice.get_unified_prompt(
    component_type='summary',  # ← Automatically uses config
    material_context=material_context,
    author=author_dict
)
```

### Example 3: Override Intensity in Generator

**Generator can still override config:**

```python
# In generator.py
prompt = voice.get_unified_prompt(
    component_type='subtitle',
    material_context=material_context,
    author=author_dict,
    intensity_override='level_4_technical'  # Override config
)
```

Then in VoiceOrchestrator:

```python
def _build_subtitle_prompt(...):
    config = self.get_component_config('subtitle')
    # Allow override
    intensity_level = kwargs.get('intensity_override') or config.get('intensity_level')
```

---

## 📊 Intensity Levels Reference

| Level | Description | Measurements | Formulas | Example |
|-------|-------------|--------------|----------|---------|
| **level_1_minimal** | Zero technical | None | No | "Surface looks dirty and rough" |
| **level_2_light** | Light technical | Max 1 simple | No | "Dark oxide layer about 10 µm thick" |
| **level_3_moderate** | Balanced | Max 1 (thickness OR roughness) | No | "Layer measures about 8 µm thick" |
| **level_4_technical** | Professional | 2-3 (thickness AND roughness) | Yes (Fe₂O₃) | "8-12 µm thick Fe₂O₃ layer, Ra 3.5→0.8 µm" |
| **level_4_plus_enhanced** | Enhanced technical | 2-4 comprehensive | Yes + advanced | "SEM at 1000× shows Fe₂O₃ layer 8.5±1.0 µm, Ra 3.2→0.7 µm" |
| **level_5_expert** | Maximum technical | Comprehensive | Full scientific | "SEM at 15kV, XPS binding energies, Ra/Rz/Rq..." |

---

## ✅ Benefits

### Before (Hardcoded in Generator):
```python
# In generator.py - hardcoded!
target_words = 10
style_guidance = 'concise and professional'
# Can't change without modifying code
```

### After (Config-Driven):
```yaml
# In component_config.yaml - easily tunable!
subtitle:
  intensity_level: "level_2_light"
  formality: "professional-engaging"
  target_audience: "technical professionals"
  word_count_range: [8, 12]
```

**Advantages:**
- ✅ **Centralized control** - All component settings in one place
- ✅ **No code changes** - Tune intensity by editing YAML
- ✅ **Consistency** - All components follow same pattern
- ✅ **Extensibility** - Easy to add new components
- ✅ **Override capability** - Generators can still override when needed

---

## 🏗️ Current Implementation

**Implemented:**
- ✅ `voice/component_config.yaml` - Configuration file
- ✅ `VoiceOrchestrator._load_component_config()` - Config loader
- ✅ `VoiceOrchestrator.get_component_config()` - Config accessor
- ✅ `_build_subtitle_prompt()` - Uses config for intensity
- ✅ Component types: `micro`, `subtitle`, `description`, `environmental_impact`, `health_safety`, `quality_control`

**Currently Using Config:**
- ✅ **Subtitle generator** - Reads `level_2_light` intensity from config

**To Be Updated:**
- ⏳ **Micro generator** - Still uses hardcoded `level_4_plus_enhanced`
- ⏳ **Future components** - Description, environmental impact, etc.

---

## 🎯 Next Steps

### Option A: Update Caption Generator
Modify `_build_microscopy_prompt()` to use config:

```python
def _build_microscopy_prompt(...):
    config = self.get_component_config('micro')
    intensity_level = config.get('intensity_level', 'level_4_plus_enhanced')
    # Rest uses config...
```

### Option B: Add More Components
Use the pattern for new components:
1. Add config to `component_config.yaml`
2. Add prompt builder to `VoiceOrchestrator`
3. Generator calls `get_unified_prompt()` with component type

---

## 📝 Configuration Schema

```yaml
component_name:
  # Technical intensity level (required)
  intensity_level: "level_2_light"
  
  # Writing formality (optional)
  formality: "professional-engaging"
  
  # Target audience description (optional)
  target_audience: "technical professionals"
  
  # Word count range (optional)
  word_count_range: [min, max]
  
  # Section-specific overrides (optional)
  sections:
    section_name:
      focus: "..."
      required_elements: [...]
  
  # Style notes (optional)
  style_notes:
    - "Note 1"
    - "Note 2"
```

---

## 💡 Philosophy

**Separation of Concerns:**
- **Generators** → Focus on workflow and API interaction
- **VoiceOrchestrator** → Focus on prompt building and voice layering
- **component_config.yaml** → Focus on voice parameter tuning
- **voice_base.yaml** → Focus on intensity definitions

**Result:** Clean architecture where voice parameters are data, not code.

---

## 🔍 Testing

```bash
# Test subtitle with new config
python3 run.py --subtitle "Copper"

# Check logging for config usage
# Look for: "Component config for 'subtitle': intensity=level_2_light, audience=..."
```

---

## 📚 Related Files

- `voice/component_config.yaml` - Component configurations
- `voice/orchestrator.py` - Voice orchestration logic
- `voice/base/voice_base.yaml` - Intensity level definitions
- `components/*/generators/generator.py` - Component generators
- `voice/profiles/*.yaml` - Country-specific linguistic patterns

---

**Summary:** Component voice configuration allows centralized control of intensity, formality, and other voice parameters without modifying generator code. Easy to extend, easy to tune, maintains clean separation of concerns.
