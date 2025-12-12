# Processing System Architecture

**Last Updated:** December 11, 2025  
**Status:** Production-Ready ✅

---

## 🚨 **MANDATORY REQUIREMENTS** (December 11, 2025)

**CRITICAL ARCHITECTURE RULES - NO EXCEPTIONS:**

### **1. Universal Pipeline Requirement**
**ALL text generation in ALL domains MUST use this processing pipeline.**

- ✅ **Materials domain** - micro, description, FAQ, subtitle
- ✅ **Contaminants domain** - micro, description, FAQ
- ✅ **Settings domain** - description, technical content
- ✅ **Future domains** - ANY text generation
- ❌ **NO direct API calls** - All text generation goes through QualityEvaluatedGenerator
- ✅ **Prompt validation** - Validates length, format, coherence (non-blocking)
- ✅ **Learning feedback** - Validation issues logged for humanness optimizer adaptation
- ❌ **NO bypassing pipeline** - No custom generation logic outside this system

### **2. Zero Defaults/Fallbacks Policy** 🔥 **MANDATORY (Dec 11, 2025)**
**NO defaults or fallbacks are permitted ANYWHERE in production code, especially generators.**

**FIRM POLICY - ZERO TOLERANCE:**
- ❌ **NO default values** - `.get('key', 'default')`, `or {}`, `or "fallback"`
- ❌ **NO fallback logic** - `if not data: use_template()`, `if missing: return default`
- ❌ **NO skip logic** - `if not exists: return True`, `except: pass`
- ❌ **NO mock responses** - `MockAPIClient`, placeholder returns in production
- ❌ **NO silent degradation** - Must fail fast with clear exceptions

**Applies to ALL code:**
- ✅ Generators: Must fail if data/config missing (no defaults)
- ✅ Data loaders: Must fail if files missing (no empty returns)
- ✅ Configuration: Must fail if required keys missing (no fallback values)
- ✅ API clients: Must fail if credentials missing (no mock mode)
- ✅ Validators: Must fail if validation impossible (no skip logic)

**✅ CORRECT behavior:**
```python
# Fail fast with specific exception
if not material_data:
    raise ValueError(f"Material data required for {material_name}")

# Use explicit None, not defaults
value = config.get('temperature')  # Returns None if missing
if value is None:
    raise ConfigurationError("temperature required in config")
```

**❌ WRONG behavior:**
```python
# Default values bypass validation
value = config.get('temperature', 0.7)  # FORBIDDEN

# Fallback logic hides problems
if not material_data:
    material_data = {}  # FORBIDDEN

# Skip logic allows broken state
if not validator_available:
    return True  # FORBIDDEN
```

**Exception:** Mocks and defaults **ARE ALLOWED in test code** for proper testing infrastructure.

**Enforcement:** Integrity checker flags all defaults/fallbacks in production code as violations.

**Grade:** F violation for ANY default/fallback in production generators or core logic.

### **3. Single Voice/Persona Source**
**ONLY ONE location defines voice and persona characteristics.**

- ✅ **Single source:** `shared/voice/profiles/{author}.yaml`
- ✅ **Contains:** Voice instructions, forbidden phrases, cultural markers, linguistic patterns
- ❌ **NO voice instructions in domain prompts** - Domain prompts use `{voice_instruction}` placeholder only
- ❌ **NO duplicate voice definitions** - Voice profiles define ALL voice behavior
- ❌ **NO inline voice instructions** - All voice logic comes from voice profile files files

**Voice Profiles Available:**
- `indonesia.yaml` (id: 1) - Indonesian Technical Voice
- `italy.yaml` (id: 2) - Italian Accessible Technical Voice  
- `taiwan.yaml` (id: 3) - Taiwan Accessible Technical Voice
- `united_states.yaml` (id: 4) - American Technical Voice

**Policy Enforcement:** See `docs/08-development/VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md`

### **4. Zero Bypass Policy**
**NO text may be generated without going through the complete pipeline.**

```python
# ✅ CORRECT - Goes through pipeline
from generation.core.evaluated_generator import QualityEvaluatedGenerator
result = generator.generate(material_name, component_type, author_id)

# ❌ WRONG - Direct API call bypasses pipeline
text = api_client.generate(prompt, temperature=0.7)

# ❌ WRONG - Custom generation logic
text = custom_generate_function(material)
```

**Pipeline ensures:**
- Author voice consistency (voice profile-based)
- AI detection avoidance (humanness layer)
- Quality evaluation and learning
- Structural diversity
- Parameter optimization
- **Research integration** - System data lookup when needed
- **Cross-linking** - Sparse references to related materials/contaminants/settings

**Grade:** F violation if ANY text generation bypasses this pipeline

---

## 🤖 **Quality Analysis System** 🔥 **CONSOLIDATED (Dec 11, 2025)**

**Primary Interface:** `shared/voice/quality_analyzer.py` ← **NEW: Unified Quality Analyzer**  
**Legacy Components:** `ai_detection.py` (AI patterns), `post_processor.py` (voice validation)  
**Integration:** Single `QualityAnalyzer.analyze()` call replaces dual detection systems

### **Unified Quality Assessment**

The system analyzes text quality through three integrated dimensions:

**1. AI Pattern Detection** (from `ai_detection.py`):
- Grammar errors, repetitive patterns, unnatural phrasing, statistical anomalies

**2. Voice Authenticity** (from `post_processor.py`):
- Language detection, nationality markers, translation artifacts, linguistic patterns

**3. Structural Quality** (new composite analysis):
- Sentence variation, rhythm diversity, complexity mix

### **Usage Pattern**

```python
# OLD WAY (Dual Systems - Deprecated):
ai_detector = AIDetector()
voice_validator = VoicePostProcessor(api_client)
ai_result = ai_detector.detect_ai_patterns(text)
voice_result = voice_validator.validate(text, author)

# NEW WAY (Unified Analyzer):
from shared.voice.quality_analyzer import QualityAnalyzer
analyzer = QualityAnalyzer(api_client)
result = analyzer.analyze(text, author)
# Returns: overall_score, ai_patterns, voice_authenticity, structural_quality, recommendations
```

### **Detection Categories** (AI Patterns)

The AI pattern detection identifies machine-generated text through multiple dimensions:

**1. Grammar Patterns** (Critical Severity)
- Subject-verb disagreement: "data lead" (should be "leads")
- Awkward constructions: "achieves removal" (stiff AI phrasing)
- Missing articles: "with process" (should be "the process")
- Excessive passive voice: Multiple "is achieved", "is maintained"

**2. Phrasing Patterns** (Severe Severity)
- Abstract pairings: "harnesses efficiency" (formal LLM style)
- Redundant hedging: "it should be noted", "it is worth mentioning"
- LLM-specific phrases: "delve into", "pivotal role", "realm of"
- Low hedge count: Under-use of uncertainty words (LLM tells)

**3. Repetition Detection** (Moderate/Severe)
- Word frequency: 3+ occurrences triggers warning
- Phrase repetition: 3-word phrases appearing 2+ times
- Structural repetition: 3+ sentences starting with same word
- Uniform sentence length: Standard deviation < 4.0

**4. Linguistic Dimensions** (From 2025 Research - NEW)
- Dependency minimization: Average dependency length < 3 (over-optimization)
- Low lexical diversity: MTLD score indicating repetitive vocabulary
- Low emotional variance: Uniform sentiment without human emotional bursts
- N-gram entropy: Low bigram/trigram entropy indicates predictability

### **Pattern Variation Rules**

The AI detection system includes **pattern variation rules** that guide structural diversity:

**Morphosyntactic Patterns:**
- Clause complexity variation (simple → compound → complex rotation)
- Dependency structure diversity (no over-optimization)
- Phrase-level variation (not just word-level)

**Psychometric Patterns:**
- Emotional bursts: Human text has sentiment shifts (2+ per paragraph)
- Lexical diversity: MTLD (Mean Length Textual Diversity) thresholds
- Burstiness: Sentence complexity variance (stdev ≥ 5 for human-like)

**Sociolinguistic Patterns:**
- Non-native bias reduction: Allow article flexibility for non-native authors
- Pronoun pattern detection: LLMs overuse "it" in topic position
- Hedging normalized by length: Accounting for text length in uncertainty word counts

### **Integration in Pipeline**

```python
# In QualityEvaluatedGenerator.generate()

# After content generated, before save:
from shared.voice.ai_detection import AIDetector

detector = AIDetector(strict_mode=False)
ai_check = detector.detect_ai_patterns(content_text)

# Results logged to quality_scores
quality_scores['ai_pattern_detection'] = {
    'ai_score': ai_check['ai_score'],  # 0-100 (higher = more AI-like)
    'is_ai_like': ai_check['is_ai_like'],  # Boolean
    'grammar_errors': error_count,
    'phrasing_issues': issue_count,
    'repetition_score': repetition_score
}
```

### **Scoring System**

**AI Pattern Score:** 0-100 scale
- **0-30:** Excellent human-like quality
- **31-60:** Acceptable with minor AI patterns
- **61-80:** Significant AI patterns detected
- **81-100:** High AI likelihood (critical issues)

**Thresholds:**
- Default threshold: 70 (relaxed)
- Strict mode: 60 (stricter detection)
- Adaptive: Can adjust based on text length

**Weights** (from configuration):
- Grammar errors: 25% of total score
- Phrasing issues: 30% of total score
- Repetition: 20% of total score
- Linguistic dimensions: 15% of total score
- Statistical anomalies: 10% of total score

### **Pattern File Format**

`shared/voice/ai_detection_patterns.txt` uses pipe-delimited format:

```
category|name|pattern|severity|example|reason

# Grammar patterns
grammar|subject_verb_disagreement|\bdata\s+(lead|indicate)\b|critical|data lead|Plural with singular

# Phrasing patterns  
phrasing|llm_phrases|\b(delve into|pivotal role)\b|critical|delve into|LLM-specific phrases

# Repetition thresholds
repetition|word_frequency|3|severe|Word repeated 3+ times|Reduced from 4

# Linguistic dimensions
linguistic_dimensions|dependency_minimization|avg_dep_length<3|moderate|Short dependencies|LLMs over-optimize
```

### **Quality Analysis Integration** 🔥 **CONSOLIDATED**

**Unified Quality Analyzer** (`shared/voice/quality_analyzer.py`):

Combines three quality dimensions into single analysis:

1. **AI Patterns** (40% weight) - via `AIDetector`
   - Grammar/phrasing/repetition analysis
   - Statistical anomaly detection
   - Pattern variation enforcement

2. **Voice Authenticity** (30% weight) - via `VoicePostProcessor`
   - Language detection (English vs translations)
   - Nationality-specific linguistic patterns
   - Translation artifact identification

3. **Structural Quality** (30% weight) - composite analysis
   - Sentence length variation (CoV target: 0.4-0.6)
   - Rhythm diversity (varied sentence starters)
   - Complexity mix (simple/medium/complex sentences)

**Result**: Single `overall_score` (0-100) with detailed breakdown and actionable recommendations.

**Benefits**: Eliminates duplication, unified scoring, comprehensive recommendations in one call.

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

## 🔬 Research & Cross-Linking Architecture

### **Research Step: System Data Lookup**

**Purpose:** Enable generation to query system data when context requires it.

**Data Sources Available:**
1. **Materials.yaml** - All material properties, categories, applications
2. **Contaminants.yaml** - Contamination patterns, removal difficulty, material compatibility
3. **Categories.yaml** - Category-level ranges, common properties
4. **Settings.yaml** - Laser settings, parameter ranges, safety thresholds

**Implementation Pattern:**
```python
# During prompt building, check if research needed
from domains.materials.data_loader import MaterialsDataLoader
from domains.contaminants.data_loader import ContaminationPatternLoader

# Example: Generating micro for Steel contamination removal
materials_loader = MaterialsDataLoader()
steel_data = materials_loader.get_material("Steel")  # Get hardness, properties
related_materials = materials_loader.get_category_materials("Metals")  # Similar materials

contaminants_loader = ContaminationPatternLoader()
common_contaminants = contaminants_loader.get_patterns_for_material("Steel")  # What commonly contaminates steel
```

**When to Research:**
- ✅ Writing about material properties → Check Materials.yaml for accurate data
- ✅ Mentioning contamination → Check Contaminants.yaml for removal difficulty
- ✅ Referencing settings → Check Settings.yaml for parameter ranges
- ✅ Comparing materials → Check Categories.yaml for category context
- ❌ Basic descriptions → No research needed, use prompt context

**Research Integration Points:**
1. **Prompt Builder** (`shared/text/utils/prompt_builder.py`) - Inject researched facts
2. **Data Enricher** (`generation/enrichment/data_enricher.py`) - Fetch material properties
3. **Domain Adapters** (`generation/core/adapters/*.py`) - Access domain-specific data

---

### **Cross-Linking: Sparse References**

**Purpose:** Connect related content naturally without over-linking.

**Cross-Linking Rules:**
- ✅ **Sparse** - Maximum 1-2 references per 150 words
- ✅ **Natural** - Only when contextually relevant
- ✅ **Informative** - Must add value, not just link for linking's sake
- ❌ **No link spam** - Don't turn text into a navigation menu
- ❌ **No circular references** - Avoid Material A → Material B → Material A loops

**Cross-Link Types:**

**1. Material → Related Materials**
```
Example: "Unlike softer metals like Aluminum or Copper, Steel requires..."
Links: aluminum.md, copper.md
When: Comparing properties, contrasting behaviors
```

**2. Material → Contaminants**
```
Example: "Common contaminants include rust oxide and oil residue on industrial surfaces."
Links: rust-oxide.md, oil-residue.md  
When: Discussing typical contamination scenarios
```

**3. Material → Settings**
```
Example: "Pulse width settings between 10-50ns work best for this thickness."
Links: pulse-width.md
When: Discussing specific laser parameters
```

**4. Contaminant → Materials**
```
Example: "This contamination pattern appears frequently on stainless steel and titanium alloys."
Links: stainless-steel-316.md, titanium-alloy-ti-6al-4v.md
When: Listing compatible/affected materials
```

**Implementation:**
```python
# During generation, identify cross-link opportunities
def add_cross_links(content: str, current_item: str, domain: str) -> str:
    """
    Add sparse cross-links to related content.
    
    Args:
        content: Generated text
        current_item: Current material/contaminant/setting
        domain: materials/contaminants/settings
        
    Returns:
        Content with markdown links added
        
    Rules:
        - Max 2 links per 150 words
        - Only add if term appears naturally in text
        - Use exact match or close variant
    """
    # Example: "steel" → "[steel](../materials/steel.md)"
    # Only if: not current_item AND appears in text AND < 2 links already
```

**Cross-Link Guidelines:**
1. **Check context** - Does the link add useful information?
2. **Verify existence** - Does the target file exist in frontmatter/
3. **Natural placement** - Link where term first appears, not every occurrence
4. **Domain awareness** - Link to correct domain (materials/, contaminants/, settings/)

---

## 🗂️ Domain Prompt Structure

**Location:** `domains/{domain}/prompts/{component_type}.txt`

**Available Domain Prompts:**

**Materials Domain:**
- Currently: No text prompts (uses shared templates only)
- Future: Add material-specific context templates

**Contaminants Domain:**
- `domains/contaminants/prompts/micro.txt` - Contamination micro descriptions
- `domains/contaminants/prompts/faq.txt` - Contamination FAQs
- `domains/contaminants/prompts/material_description.txt` - Contamination descriptions

**Settings Domain:**
- `domains/settings/prompts/settings_description.txt` - Laser setting descriptions

**Domain Prompt Structure Example:**
```plaintext
You are {author} from {country}, writing about {topic}.

TASK: [Brief task description]

{voice_instruction}  ← Voice profile placeholder (REQUIRED)

{technical_guidance}  ← Technical intensity guidance

{sentence_guidance}  ← Sentence rhythm guidance

AVOID:
- [Domain-specific phrases to avoid]

OUTPUT: [Expected format]
```

**Key Requirements:**
- ✅ Must use `{voice_instruction}` placeholder
- ✅ Keep domain prompts SHORT (< 500 characters)
- ✅ Focus on TASK and OUTPUT format only
- ❌ NO voice/tone instructions (that's in voice profiles)
- ❌ NO hardcoded examples (use templates)

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
