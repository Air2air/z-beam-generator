# Processing System Architecture

**Last Updated:** November 14, 2025  
**Status:** Production-Ready ✅

---

## 🏗️ System Overview

The processing system uses a **slider-driven architecture** where 10 user-facing sliders (0-100 scale) automatically calculate all downstream technical parameters. This eliminates hardcoded values and enables intelligent adaptation to user preferences.

```
┌─────────────────────────────────────────────────────────────┐
│                          USER                               │
│                            ↓                                │
│              Adjusts 10 sliders in config.yaml              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    CONFIGURATION LAYER                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  config.yaml                                         │  │
│  │  • 10 user-facing sliders (0-100)                    │  │
│  │  • Static infrastructure (paths, base lengths)       │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  config_loader.py                                    │  │
│  │  • Reads YAML                                        │  │
│  │  • Provides typed accessors                          │  │
│  │  • Foundation for all other loaders                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌───────────────────────┐           ┌───────────────────────┐
│  PERSONALITY LAYER    │           │  CALCULATION LAYER    │
│  author_config_loader │           │  dynamic_config.py    │
│  + author_profiles    │           │                       │
│  • Applies offsets    │           │  Calculates:          │
│  • Yi-Chun: precise   │           │  • Temperature        │
│  • Alessandro: varied │           │  • Max tokens         │
│  • Ikmanda: natural   │           │  • Retry behavior     │
│  • Todd: engaging     │           │  • Thresholds         │
└───────────────────────┘           │  • 30+ parameters     │
        ↓                           └───────────────────────┘
        └───────────────────┬───────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    GENERATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  orchestrator.py                                     │  │
│  │  • Coordinates workflow                              │  │
│  │  • Uses DynamicConfig for all params                 │  │
│  │  • Applies author personality                        │  │
│  └──────────────────────────────────────────────────────┘  │
│          ↓              ↓              ↓                    │
│  ┌──────────┐    ┌──────────┐   ┌──────────┐              │
│  │ Enrich   │    │ Generate │   │ Validate │              │
│  │ Data     │ →  │ Content  │ → │ Quality  │              │
│  └──────────┘    └──────────┘   └──────────┘              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                         OUTPUT                              │
│           Human-authentic, AI-resistant content             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 The 10 Control Sliders

### **Content Characteristics (1-4)**

| # | Slider | What It Controls | Default |
|---|--------|------------------|---------|
| **1** | `author_voice_intensity` | Regional voice patterns, cultural markers | 50 |
| **2** | `personality_intensity` | Personal opinions, evaluative language | 40 |
| **3** | `engagement_style` | Reader awareness, direct address | 35 |
| **4** | `technical_language_intensity` | Jargon density, measurements per sentence | 50 |

### **Human Realism Markers (5-10)**

| # | Slider | What It Controls | Default |
|---|--------|------------------|---------|
| **5** | `context_specificity` | Detail level, concrete scenarios | 55 |
| **6** | `sentence_rhythm_variation` | Sentence structure variety (KEY) | 80 |
| **7** | `imperfection_tolerance` | Human-like quirks, minor flaws | 80 |
| **8** | `structural_predictability` | Template adherence vs. organic flow | 45 |
| **9** | `ai_avoidance_intensity` | Pattern variation intensity | 50 |
| **10** | `length_variation_range` | Length flexibility (±% from target) | 50 |

---

## 🔧 Component Architecture

### **Configuration Layer**

```python
# config_loader.py - Foundation
class ProcessingConfig:
    """Reads config.yaml and provides typed access to sliders"""
    def get_author_voice_intensity() -> int
    def get_personality_intensity() -> int
    # ... all 10 sliders
```

### **Calculation Layer**

```python
# dynamic_config.py - Technical Parameter Calculator
class DynamicConfig:
    """Converts sliders → technical parameters"""
    
    def calculate_temperature(component: str) -> float:
        # Slider → 0.7-1.0 range based on ai_avoidance + rhythm
        
    def calculate_max_tokens(component: str) -> int:
        # Slider → token limits based on length_variation
        
    def calculate_retry_behavior() -> dict:
        # Slider → max_attempts, temp_increase based on ai_avoidance
        
    def calculate_detection_threshold() -> float:
        # Slider → threshold based on ai_avoidance + imperfection
    
    # ... 30+ calculated parameters
```

### **Personality Layer**

```python
# author_config_loader.py + author_profiles.yaml
class AuthorConfigLoader:
    """Applies personality offsets to base sliders"""
    
    # Example: Base imperfection_tolerance = 50
    # Yi-Chun offset: -15 → Final: 35 (more precise)
    # Ikmanda offset: +20 → Final: 70 (more natural)
```

### **Generation Layer**

```python
# orchestrator.py - Workflow Coordinator
class Orchestrator:
    def __init__(self, api_client, dynamic_config):
        self.dynamic_config = dynamic_config
        
    def generate(self, topic, component_type, author_id):
        # Get author-specific config
        author_config = get_author_config(author_id)
        dynamic = DynamicConfig(base_config=author_config)
        
        # Use calculated parameters
        temperature = dynamic.calculate_temperature(component_type)
        max_tokens = dynamic.calculate_max_tokens(component_type)
        retries = dynamic.calculate_retry_behavior()
        
        # Generate with dynamic settings
        text = self._call_api(prompt, temperature, max_tokens)
        
        # Validate with dynamic thresholds
        ai_score = self.detector.detect(text)
        threshold = dynamic.calculate_detection_threshold()
        
        if ai_score > threshold:
            retry_with_adjusted_prompt()
```

---

## 🎨 Author Personality System

The system differentiates 4 authors through **offset-based personalities**:

### **Personality Offsets Example**

```yaml
# Base config.yaml sliders
imperfection_tolerance: 50
sentence_rhythm_variation: 50

# Author offsets in author_profiles.yaml
yi_chun_lin:
  offsets:
    imperfection_tolerance: -15  # Final: 35 (precise)
    sentence_rhythm_variation: -10  # Final: 40 (consistent)

ikmanda_roswati:
  offsets:
    imperfection_tolerance: +20  # Final: 70 (natural)
    sentence_rhythm_variation: +10  # Final: 60 (varied)
```

### **Result:**
- **Yi-Chun** generates precise, structured, formal content
- **Ikmanda** generates natural, accessible, conversational content
- Both controlled by same base sliders
- Global adjustment affects all authors proportionally

---

## 🔄 Data Flow Example

```
User adjusts slider: sentence_rhythm_variation = 80
                            ↓
config_loader.py reads: get_sentence_rhythm_variation() = 80
                            ↓
author_config_loader.py applies offset:
  Alessandro: 80 + 15 = 95 (very high variation)
  Yi-Chun: 80 + (-10) = 70 (moderate-high variation)
                            ↓
dynamic_config.py calculates:
  rhythm_coefficient_of_variation = 0.15 + (95/100 * 0.45) = 0.5775
  (sentences vary by 57.75% from mean length)
                            ↓
prompt_builder.py constructs instruction:
  "Vary sentence length dramatically. Mix 3-word fragments with
   20+ word complex sentences. Avoid uniform rhythm."
                            ↓
orchestrator.py generates with dynamic temperature:
  temperature = 0.7 + (95/100 * 0.3) = 0.985 (very creative)
                            ↓
Output: Highly varied, natural-looking text
```

---

## 🛠️ User Interface

### **CLI Tool**

```bash
# View current settings
python3 -m processing.intensity.intensity_cli status

# Adjust sliders (0-100)
python3 -m processing.intensity.intensity_cli set rhythm 70
python3 -m processing.intensity.intensity_cli set imperfection 65

# Test prompt instructions
python3 -m processing.intensity.intensity_cli test
```

### **Direct Configuration**

```yaml
# Edit processing/config.yaml
sentence_rhythm_variation: 75  # Increase variation
imperfection_tolerance: 60      # Allow more quirks
```

### **Programmatic Access**

```python
from processing.config.dynamic_config import DynamicConfig

config = DynamicConfig()
temp = config.calculate_temperature('subtitle')
tokens = config.calculate_max_tokens('description')
```

---

## 🎯 Design Principles

### **1. Single Source of Truth**
- 10 sliders in config.yaml
- NO hardcoded technical parameters
- Change once, affects everything

### **2. Layered Calculation**
- Base sliders → Author offsets → Technical parameters
- Each layer has clear responsibility
- No cross-layer coupling

### **3. Fail-Fast Configuration**
- Validate config structure at startup
- Fail immediately on invalid ranges (must be 0-100)
- Clear error messages

### **4. Intelligent Defaults**
- Sliders default to 50 (moderate)
- Except: rhythm=80, imperfection=80 (human realism)
- Proven through testing

### **5. Runtime Adaptability**
- Parameters calculated per-generation
- Same slider → different results for different components
- Temperature adapts to component type + slider

---

## 📚 Related Documentation

- **Quick Start:** `QUICKSTART.md` - Basic usage
- **Intensity Controls:** `INTENSITY_CONTROLS.md` - Detailed slider explanations
- **Author Profiles:** `AUTHOR_PROFILES_SYSTEM.md` - Personality offset system
- **Flexible Architecture:** `FLEXIBLE_ARCHITECTURE_GUIDE.md` - Component specs
- **Implementation:** `IMPLEMENTATION_SUMMARY.md` - Module details

---

## 🔍 Troubleshooting

**Q: Content too robotic?**  
A: Increase: `rhythm` (70+), `imperfection` (60+), `structural` (55+)

**Q: Output too informal?**  
A: Decrease: `personality` (30), `engagement` (25), `imperfection` (40)

**Q: Not technical enough?**  
A: Increase: `technical` (65+), `context` (65+)

**Q: Failing AI detection?**  
A: Increase: `rhythm` (75+), `imperfection` (65+), `ai` (75+)

---

**Architecture Status:** ✅ Production-Ready  
**Last Major Refactor:** November 2025 (slider-driven system)  
**Maintainer:** See `.github/copilot-instructions.md`
