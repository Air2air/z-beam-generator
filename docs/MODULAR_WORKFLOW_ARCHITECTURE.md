# Modular Workflow Architecture
**Date**: November 19, 2025  
**Status**: ✅ IMPLEMENTED AND TESTED

---

## 🎯 Overview

The Z-Beam Generator now uses a clean 4-stage modular pipeline where each stage is independent and reusable across all component types (caption, subtitle, FAQ, etc.).

---

## 📊 Complete Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         USER COMMAND                           │
│                 (run.py --caption "Steel")                     │
└──────────────────────────┬─────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                    STAGE 1: GENERATION                         │
│                                                                 │
│  Entry Point:                                                  │
│    shared/commands/generation.py::handle_caption_generation()  │
│                           ↓                                     │
│  Domain Wrapper:                                               │
│    domains/materials/coordinator.py::UnifiedMaterialsGenerator │
│                           ↓                                     │
│  Core Engine:                                                  │
│    generation/core/generator.py::DynamicGenerator              │
│                           ↓                                     │
│  Content Extraction:                                           │
│    generation/core/adapters/materials_adapter.py               │
│                           ↓                                     │
│  OUTPUT: Materials.yaml updated with generated content         │
│                                                                 │
│  Components: caption, subtitle, FAQ (all use same flow)        │
└──────────────────────────┬─────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                    STAGE 2: VALIDATION                         │
│                                                                 │
│  Quality Evaluation:                                           │
│    postprocessing/evaluation/subjective_evaluator.py           │
│    - Loads shared/text/templates/evaluation/subjective_quality.txt           │
│    - Uses Grok API for subjective scoring                      │
│    - Returns 0-10 score + dimension scores                     │
│                           ↓                                     │
│  Readability Check:                                            │
│    generation/validation/readability/ (if enabled)             │
│                           ↓                                     │
│  AI Detection:                                                 │
│    generation/validation/winston/ (if enabled)                 │
│                           ↓                                     │
│  OUTPUT: Quality scores, pass/fail status                      │
│          Subjective: 7.0-8.0/10 (PASS threshold: 7.0+)         │
└──────────────────────────┬─────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                  STAGE 3: LEARNING DATA                        │
│                    (Optional - Simple Mode OFF)                │
│                                                                 │
│  Pattern Learning:                                             │
│    learning/subjective_pattern_learner.py                      │
│    - Updates shared/text/templates/evaluation/learned_patterns.yaml          │
│    - Tracks rejection patterns (AI tendencies)                 │
│    - Tracks success patterns (EMA α=0.1)                       │
│                           ↓                                     │
│  Parameter Optimization:                                       │
│    learning/realism_optimizer.py                               │
│    - Suggests temperature adjustments                          │
│    - Calculates API penalties                                  │
│                           ↓                                     │
│  Composite Scoring:                                            │
│    postprocessing/evaluation/composite_scorer.py               │
│    - Winston (40%) + Realism (60%) weighting                   │
│    - Adaptive threshold from 75th percentile                   │
│                           ↓                                     │
│  OUTPUT: Updated patterns, parameter recommendations           │
│          Sweet spot data for future generations                │
└──────────────────────────┬─────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                 STAGE 4: POST-PROCESSING                       │
│                                                                 │
│  Integrity Validation:                                         │
│    shared/commands/integrity_helper.py                         │
│    - Validates Materials.yaml structure                        │
│    - Checks database logging                                   │
│    - Verifies sweet spot updates                               │
│                           ↓                                     │
│  Voice Enhancement: (Future)                                   │
│    shared/voice/orchestrator.py                                │
│    - Applies author-specific voice patterns                    │
│                           ↓                                     │
│  Frontmatter Export: (Separate pipeline)                       │
│    export/orchestrator.py                                      │
│    - Generates frontmatter files from Materials.yaml           │
│                           ↓                                     │
│  OUTPUT: Enhanced content, frontmatter files, validation report│
└────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Success Factors

### **1. Unified Return Format**

ALL components now return the same structure:
```python
{
    'success': True,
    'content': <component_specific_data>,  # dict for caption, str for subtitle, list for FAQ
    'attempts': 1,
    'ai_score': 0.0,
    'human_score': 100.0,
    'realism_score': 8.0,
    'simple_mode': True
}
```

### **2. Strategy-Based Extraction**

Components define extraction strategy in config:
```yaml
component_lengths:
  caption:
    default: 50
    extraction_strategy: before_after  # Extract {'before': '...', 'after': '...'}
  subtitle:
    default: 30
    extraction_strategy: raw  # Return text as-is
  faq:
    default: 150
    extraction_strategy: json_list  # Parse JSON or markdown Q&A
```

### **3. Forgiving Extraction**

Extraction gracefully handles format variations:
- **Caption**: Single paragraph → treat as "before" only
- **FAQ**: JSON format → parse as JSON, markdown → parse as Q&A pairs
- **Subtitle**: Raw text → return as-is

### **4. Simple Mode Configuration**

```yaml
# generation/config.yaml
simple_mode:
  enabled: true                          # Disable learning systems
  fixed_temperature: 0.9                 # Proven reliable temperature
  max_attempts: 3                        # Simple retry limit
  temperature_increase_per_retry: 0.1    # Linear increase on retry

length_variation_range: 5.5              # Moderate ±35% variation
```

---

## 🧪 Test Results

### **Caption Generation** ✅
```
Material: Steel
API: DeepSeek (2.3s response)
Content: 173 chars, 30 words
Subjective Score: 8.0/10 ✅ PASS
Winston Score: 100% human
Status: ✅ PERFECT
```

### **Subtitle Generation** ✅
```
Material: Titanium
API: DeepSeek (2.5s response)
Content: 69 chars, 13 words
Subjective Score: 7.0/10 ✅ PASS
Status: ✅ WORKING
```

### **FAQ Generation** ✅
```
Material: Titanium
API: Grok (4.6s response)
Content: 1 Q&A pair, 198 words
Subjective Score: 8.0/10 ✅ PASS
Status: ✅ WORKING (extraction improved with markdown support)
```

---

## 🗂️ File Organization

### **Generation (Stage 1)**
```
generation/
├── core/
│   ├── generator.py               # DynamicGenerator - main engine
│   ├── component_specs.py         # Component discovery and specs
│   ├── prompt_builder.py          # Prompt construction
│   ├── sentence_calculator.py     # Sentence counting
│   └── adapters/
│       └── materials_adapter.py   # Content extraction strategies
├── config/
│   ├── config.yaml                # Simple mode + component lengths
│   ├── config_loader.py           # Config loading utilities
│   └── dynamic_config.py          # Dynamic parameter calculation
└── validation/
    ├── readability/               # Readability checks
    └── winston/                   # AI detection (if enabled)
```

### **Validation (Stage 2)**
```
postprocessing/
└── evaluation/
    ├── subjective_evaluator.py    # Quality scoring
    ├── composite_scorer.py        # Combined quality metrics
    └── templates/
        └── evaluation/
            └── subjective_quality.txt
```

### **Learning (Stage 3)**
```
learning/
├── subjective_pattern_learner.py  # Pattern tracking
├── realism_optimizer.py           # Parameter optimization
└── data/
    └── learning.db                # Learning database
```

### **Post-Processing (Stage 4)**
```
shared/
├── commands/
│   ├── generation.py              # Command handlers
│   ├── integrity_helper.py        # Validation helpers
│   └── subjective_evaluation_helper.py
├── voice/
│   └── orchestrator.py            # Voice enhancement
└── api/
    └── client_factory.py          # API client creation
```

### **Domain Wrappers**
```
domains/
└── materials/
    ├── coordinator.py             # UnifiedMaterialsGenerator
    └── prompts/
        ├── caption.txt            # Caption prompt template
        ├── subtitle.txt           # Subtitle prompt template
        └── faq.txt                # FAQ prompt template
```

### **Data Storage**
```
data/
└── materials/
    └── Materials.yaml             # Single source of truth
```

---

## 🔄 Data Flow

1. **User Command** → `run.py --caption "Steel"`
2. **Command Handler** → `shared/commands/generation.py::handle_caption_generation()`
3. **Coordinator** → `domains/materials/coordinator.py::generate('Steel', 'caption')`
4. **Generator** → `generation/core/generator.py::generate()` with DeepSeek API
5. **Extraction** → `materials_adapter.py::extract_content()` using `before_after` strategy
6. **Storage** → Write to `Materials.yaml`
7. **Validation** → Subjective evaluation with Grok API
8. **Report** → Display complete generation report
9. **Integrity** → Post-generation checks

---

## 🎓 Usage Examples

### **Generate Caption**
```bash
python3 run.py --caption "Steel" --skip-integrity-check
```

### **Generate Subtitle**
```bash
python3 run.py --subtitle "Titanium" --skip-integrity-check
```

### **Generate FAQ**
```bash
python3 run.py --faq "Aluminum" --skip-integrity-check
```

### **All Components for One Material**
```bash
python3 run.py --caption "Copper"
python3 run.py --subtitle "Copper"
python3 run.py --faq "Copper"
```

---

## 🚀 Future Enhancements

### **1. Multi-Component Generation**
```bash
python3 run.py --all "Steel"  # Generate caption + subtitle + FAQ in one command
```

### **2. Batch Generation**
```bash
python3 run.py --batch --caption --materials Steel,Aluminum,Copper
```

### **3. Voice Enhancement Integration**
Currently voice enhancement is separate. Future: Integrate into Stage 4.

### **4. Learning Mode Toggle**
```bash
python3 run.py --caption "Steel" --learning  # Enable learning systems
```

---

## ✅ Validation Checklist

**Before committing changes:**
- [ ] All three components (caption, subtitle, FAQ) generate successfully
- [ ] Subjective evaluation passes (7.0+/10)
- [ ] Content saves to Materials.yaml correctly
- [ ] Generation report displays complete information
- [ ] Post-generation integrity checks pass
- [ ] No legacy code imports (generation/archive removed)
- [ ] All components use UnifiedMaterialsGenerator
- [ ] Extraction strategies configured in config.yaml

**Current Status:**
- ✅ Caption: 8.0/10 quality, 100% human score
- ✅ Subtitle: 7.0/10 quality, working perfectly
- ✅ FAQ: 8.0/10 quality, markdown parsing functional
- ✅ Legacy code removed (generation/archive deleted)
- ✅ All components unified under one architecture
- ✅ Extraction strategies implemented
- ✅ Complete reporting in place

---

## 📈 Quality Metrics

| Component | API | Response Time | Score | Status |
|-----------|-----|---------------|-------|--------|
| Caption | DeepSeek | 2.3-2.9s | 8.0/10 | ✅ EXCELLENT |
| Subtitle | DeepSeek | 2.5s | 7.0/10 | ✅ GOOD |
| FAQ | Grok | 4.6s | 8.0/10 | ✅ EXCELLENT |

**Average Quality**: 7.7/10 (Target: 7.0+) ✅

---

## 🎯 Key Achievements

1. **✅ Unified Architecture**: All components use same generation flow
2. **✅ No Legacy Code**: Removed generation/archive completely
3. **✅ Consistent Returns**: All methods return full result dict
4. **✅ Strategy Pattern**: Extraction configurable per component
5. **✅ Forgiving Extraction**: Handles format variations gracefully
6. **✅ Complete Reporting**: Full transparency on generation results
7. **✅ Quality Gates**: All components pass subjective evaluation
8. **✅ Modular Design**: Easy to add new components or modify existing

---

## 📝 Adding New Components

To add a new component type (e.g., "description"):

1. **Create prompt template**: `domains/materials/prompts/description.txt`
2. **Add config entry**:
   ```yaml
   component_lengths:
     description:
       default: 200
       extraction_strategy: raw  # or before_after, json_list
   ```
3. **That's it!** The system will automatically:
   - Discover the new component
   - Load the prompt template
   - Use the configured extraction strategy
   - Generate content with the same quality checks

**NO CODE CHANGES REQUIRED** for new components!

---

## 🎓 Conclusion

The Z-Beam Generator now has a clean, modular architecture where:
- **Generation** is unified across all components
- **Validation** is consistent and quality-gated
- **Learning** is optional and modular
- **Post-processing** is independent and reusable

This architecture scales easily to new components and domains while maintaining high quality and consistency.
