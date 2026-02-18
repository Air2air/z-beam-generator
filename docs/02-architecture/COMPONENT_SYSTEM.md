# Component System Architecture

**Purpose**: Complete component architecture and discovery system  
**Audience**: AI assistants, component developers  
**Last Updated**: December 20, 2025  
**Status**: Consolidated from 3 component architecture documents

---

## 🎯 Overview

Z-Beam Generator uses a **dynamic component discovery system** where components are defined by:
1. Prompt templates (content instructions)
2. Configuration (structural settings)

**ZERO hardcoded component types** in processing system - components discovered at runtime.

---

## 🏗️ Core Architecture

### Universal Component Pattern

All content generators follow the **same simplified architecture**:

1. **Fixed Prompt Templates** - Material name injection only, no dynamic construction
2. **Single Class** - No wrapper classes, direct implementation
3. **Config Constants** - All settings at module top, numeric intensity values
4. **No Voice Coupling** - Voice enhancement handled separately in post-processing
5. **Atomic YAML Writes** - Direct write to Materials.yaml with temp file safety

### Component Types

Z-Beam Generator supports multiple content types with **equal architectural treatment**:

| Component | Word Count | Voice/Tech Intensity | Sections | API Calls | Lines |
|-----------|------------|----------------------|----------|-----------|-------|
| **FAQ** | 15-45/answer | 2/1 (Light/Minimal) | Q&A pairs (3-9) | 1 | 115 |
| **Subtitle** | 7-12 total | 4/3 (Strong/Moderate) | Single tagline | 1 | 180 |
| **Micro** | 30-70/section | 3/2 (Moderate/Light) | Before/After (2) | 1 | 229 |
| **Description** | 50-150 words | 3/2 (Moderate/Light) | Single paragraph | 1 | ~200 |

**Policy**: `CONTENT_TYPE_EQUALITY.md` - All content types (micro, subtitle, faq, description) treated as equals:
- Same underlying infrastructure (QualityEvaluatedGenerator)
- Same validation and quality gates
- Same learning and feedback systems
- Same voice and humanness optimization

**No privileged components** - Adding new component requires NO code changes in `/processing`.

---

## 🔍 Component Discovery System

**Policy**: `COMPONENT_DISCOVERY.md` - Components defined ONLY in two places

### Discovery Flow

```
1. Application requests component (e.g., "micro")
   ↓
2. ComponentRegistry._discover_components()
   ↓
3. Scans prompts/{domain}/*.txt files
   ↓
4. For each .txt file (excluding system prompts):
   - Component type = filename without .txt
    - Prompt file = prompts/{domain}/{filename}.txt
   ↓
5. Loads lengths from domains/{domain}/config.yaml
   ↓
6. Returns ComponentSpec with:
   - name: from filename
   - lengths: from config.yaml
   - prompt_file: from discovery
   - punctuation: from config or default
```

### File Structure

```
z-beam-generator/
├── prompts/
│   ├── materials/
│   │   ├── micro.txt          # Defines 'micro' component
│   │   ├── description.txt    # Defines 'description' component
│   │   ├── faq.txt            # Defines 'faq' component
│   │   └── {custom}.txt       # Add any new component here
│   └── contaminants/
│       └── description.txt    # Contaminant-specific
│
├── domains/
│   ├── materials/
│   │   └── config.yaml        # Component lengths only
│   │       component_lengths:
│   │         micro: {default: 50, min: 30, max: 70}
│   │         description: {default: 150, min: 50, max: 200}
│   └── contaminants/
│       └── config.yaml
│
├── generation/
│   ├── core/
│   │   └── evaluated_generator.py  # Generic component generator
│   └── config/
│       └── component_specs.py      # NO hardcoded components!
│
└── tests/
    └── test_component_discovery.py  # Validates discovery
```

**Critical**: `/generation` code is **domain-agnostic** - works for materials, contaminants, regions without changes.

---

## 📝 Component Structure

### Standard Module Pattern

All component generators follow this structure:

```python
#!/usr/bin/env python3
"""Component Generator - Simple [component type] generation."""

import datetime
import logging
import os
import random
import tempfile
import yaml
from pathlib import Path
from typing import Dict
from generation.core.evaluated_generator import QualityEvaluatedGenerator

logger = logging.getLogger(__name__)

# ============================================================================
# COMPONENT CONFIGURATION
# ============================================================================
COMPONENT_WORD_COUNT_RANGE = (min, max)  # Component-specific range
COMPONENT_VOICE_INTENSITY = N  # 1-5 numeric scale
COMPONENT_TECHNICAL_INTENSITY = N  # 1-5 numeric scale

# Generation settings
COMPONENT_GENERATION_TEMPERATURE = 0.6  # or 0.7 for FAQ
COMPONENT_MAX_TOKENS = N  # Based on expected output

# Data file paths
MATERIALS_DATA_PATH = "data/materials/Materials.yaml"

# ============================================================================


class ComponentGenerator:
    """Generate material-specific [component type]."""
    
    def __init__(self):
        self.generator = QualityEvaluatedGenerator()
    
    def generate(self, material_name: str, author_id: str):
        """Generate component using universal pipeline."""
        result = self.generator.generate(
            item_name=material_name,
            component_type='component_name',
            author_id=author_id
        )
        return result
```

**Key Points**:
- Fixed prompt templates (loaded from `prompts/{domain}/`)
- Material name injection only
- Config constants at module top
- Voice handled by universal pipeline
- Atomic YAML writes with temp file safety

---

## 🚀 Adding New Components

### Step 1: Create Prompt File

Create `prompts/{domain}/{component_name}.txt`:

```txt
You are generating a {component_name} for laser cleaning materials.

CRITICAL REQUIREMENTS:
• Stay within {target_words} words
• Focus on {specific_focus}
• Use {voice_instruction}

STRUCTURE:
{describe_expected_structure}

EXAMPLE OUTPUT:
{provide_example}
```

**See**: `docs/guides/PROMPT_SYSTEM_GUIDE.md` for prompt writing guidelines.

### Step 2: Add Configuration

Add to `domains/{domain}/config.yaml`:

```yaml
component_lengths:
  new_component:
    default: 100
    min: 80
    max: 120
    extraction_strategy: raw  # or before_after
```

### Step 3: Test Discovery

```bash
# No code changes needed - test discovery
pytest tests/test_component_discovery.py -k new_component
```

### Step 4: Generate Content

```bash
python3 run.py --material "Aluminum" --new-component
```

**That's it!** No code changes required in `/generation` system.

---

## 🔧 Component Configuration

### Component Lengths

**Location**: `domains/{domain}/config.yaml`

```yaml
component_lengths:
  micro:
    default: 50      # Target word count
    min: 30          # Minimum acceptable
    max: 70          # Maximum acceptable
    extraction_strategy: before_after  # How to extract from API response
  
  description:
    default: 150
    min: 50
    max: 200
    extraction_strategy: raw  # Return text as-is
```

**Extraction Strategies**:
- **`raw`**: Return API response directly
- **`before_after`**: Extract "Before" and "After" sections (for micro content)
- **`qa_pairs`**: Extract Q&A pairs (for FAQ)

### Voice/Technical Intensity

**Deprecated**: Voice intensity now handled by universal pipeline via `shared/voice/profiles/*.yaml`.

**See**: `docs/guides/VOICE_ARCHITECTURE.md` for voice system architecture.

---

## 🔄 Component Generation Flow

### Universal Pipeline (All Components)

```
Material Name + Component Type → QualityEvaluatedGenerator
                                        ↓
                        Load prompt: prompts/{domain}/{component}.txt
                                        ↓
                        Load persona: shared/voice/profiles/{author}.yaml
                                        ↓
                        Build prompt: domain template + voice + humanness
                                        ↓
                        API call: DeepSeek/Grok generates content
                                        ↓
                        DUAL-WRITE: Materials.yaml (full field) + Frontmatter (field sync)
                                        ↓
                        Quality Gates: Winston (69%+), Realism (5.5+), Readability
                                        ↓
                        Learning: Log attempt to database (all attempts, pass/fail)
                                        ↓
                        Result: Content saved, quality logged, parameters learned
```

**See**: `processing-pipeline.md` for detailed generation flow.

---

## ✅ Component Validation

### Discovery Tests

```python
def test_component_discovery():
    """Verify components discovered from prompt files."""
    registry = ComponentRegistry()
    components = registry.list_types()
    
    assert 'micro' in components
    assert 'description' in components
    assert 'faq' in components
```

### Generation Tests

```python
def test_component_generation():
    """Verify component generation works."""
    generator = QualityEvaluatedGenerator()
    result = generator.generate(
        item_name='Aluminum',
        component_type='micro',
        author_id='todd-dunning'
    )
    
    assert result.success
    assert result.content is not None
    assert len(result.content.split()) >= 30  # Min words
```

---

## 📊 Component Comparison

### Architecture Metrics

| Metric | FAQ | Subtitle | Micro | Description |
|--------|-----|----------|-------|-------------|
| **Lines of code** | 115 | 180 | 229 | ~200 |
| **Prompt templates** | 1 | 1 | 1 | 1 |
| **Config entries** | 1 | 1 | 1 | 1 |
| **API calls/gen** | 1 | 1 | 1 | 1 |
| **Quality gates** | 5 | 5 | 5 | 5 |
| **Voice support** | ✅ | ✅ | ✅ | ✅ |
| **Learning enabled** | ✅ | ✅ | ✅ | ✅ |

**Previous architecture**: 899 lines total  
**Current architecture**: 524 lines total  
**Reduction**: 42%

### Content Characteristics

| Component | Purpose | Structure | Word Count | Sections |
|-----------|---------|-----------|------------|----------|
| **Micro** | Hero micro content | Before/After | 30-70/section | 2 |
| **Description** | Technical subtitle | Single paragraph | 50-150 total | 1 |
| **FAQ** | Q&A | Question-Answer pairs | 15-45/answer | 3-9 |
| **Subtitle** | Short tagline | Single sentence | 7-12 total | 1 |

---

## 🚨 Critical Constraints

### Component Discovery Policy

**ZERO hardcoded component types** in `/generation` code:

```python
# ❌ WRONG: Hardcoded component check
if component_type == 'micro':
    return self._generate_micro(material)

# ✅ CORRECT: Generic component handling
prompt = self._load_prompt_template(component_type)
return self._generate_content(material, prompt)
```

### Template-Only Policy

**ALL content instructions in prompt templates**, not code:

```python
# ❌ WRONG: Content instructions in code
if component_type == 'micro':
prompt += "\nCRITICAL: Write ONLY before/after micro content..."

# ✅ CORRECT: Load from template
prompt = self._load_prompt_template('micro.txt')  # Instructions in file
```

### Content Type Equality

**NO privileged components** - all use same infrastructure:

```python
# ❌ WRONG: Special handling for one component
if component_type == 'micro':
    result = self.special_micro_generator.generate(material)
else:
    result = self.standard_generator.generate(material)

# ✅ CORRECT: All components equal
result = self.generator.generate(material, component_type, author)
```

---

## 📚 Related Documentation

### Essential Reading
- **Prompt System**: `docs/guides/PROMPT_SYSTEM_GUIDE.md` - Prompt architecture and guidelines
- **Architecture Principles**: `docs/guides/ARCHITECTURE_PRINCIPLES.md` - Domain-agnostic design
- **Voice Architecture**: `docs/guides/VOICE_ARCHITECTURE.md` - Voice system and personas
- **Processing Pipeline**: `processing-pipeline.md` - Generation flow details

### Policy Documents
- **Component Discovery**: (Consolidated into this document)
- **Content Type Equality**: (Consolidated into this document)
- **Template-Only Policy**: `docs/08-development/TEMPLATE_ONLY_POLICY.md`
- **Prompt Purity Policy**: `docs/08-development/PROMPT_PURITY_POLICY.md`

### Specific Topics
- **System Overview**: `SYSTEM_OVERVIEW.md` - Complete system architecture
- **Data Architecture**: `DATA_ARCHITECTURE_GUIDE.md` - Data structure and flow
- **Export System**: `EXPORT_SYSTEM_ARCHITECTURE.md` - How components become frontmatter

---

**Last Updated**: December 20, 2025  
**Consolidated From**:
- COMPONENT_ARCHITECTURE.md (493 lines)
- COMPONENT_DISCOVERY.md (250 lines)
- CONTENT_TYPE_EQUALITY.md (396 lines)

**Total**: 1,139 lines → 380 lines (67% reduction, maintained essential information)
