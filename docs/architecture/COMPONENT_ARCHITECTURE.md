# Component Generator Architecture Overview

**Last Updated**: October 28, 2025  
**Version**: 2.0 - Unified Simplified Architecture

---

## 🎯 Universal Pattern

All three content generators (FAQ, Caption, Subtitle) now follow the **same simplified architecture pattern**:

### Core Design Principles

1. **Fixed Prompt Templates** - Material name injection only, no dynamic construction
2. **Single Class** - No wrapper classes, direct implementation
3. **Config Constants** - All settings at module top, numeric intensity values
4. **No Voice Coupling** - Voice enhancement handled separately in post-processing
5. **Atomic YAML Writes** - Direct write to Materials.yaml with temp file safety

---

## 📊 Comparison Matrix

| Component | Lines | Word Count | Voice/Tech Intensity | Sections | API Calls |
|-----------|-------|------------|----------------------|----------|-----------|
| **FAQ** | 115 | 15-45/answer | 2/1 (Light/Minimal) | Q&A pairs (3-9) | 1 |
| **Subtitle** | 180 | 7-12 total | 4/3 (Strong/Moderate) | Single tagline | 1 |
| **Caption** | 229 | 30-70/section | 3/2 (Moderate/Light) | Before/After (2) | 1 |
| **Total** | **524** | - | - | - | **3** |

**Previous Total**: 899 lines (42% reduction overall)

---

## 🏗️ Shared Architecture Pattern

### Module Structure

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
from generators.component_generators import APIComponentGenerator

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
MATERIALS_DATA_PATH = "data/Materials.yaml"

# ============================================================================


class ComponentGenerator(APIComponentGenerator):
    """Generate material-specific [component type]."""
    
    def __init__(self):
        super().__init__("component_name")
    
    def build_component_prompt(self, material_name: str, target_words: int) -> str:
        """Build fixed prompt template with material name injection."""
        return f"""[Fixed prompt template here]
        
        Material: {material_name}
        Target: {target_words} words
        
        [Instructions...]
        """
    
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        **kwargs
    ):
        """Generate content using fixed prompt template."""
        if not api_client:
            return self._create_result("", success=False, 
                                      error_message="API client required")
        
        # Generate target word count
        target_words = random.randint(MIN_RANGE, MAX_RANGE)
        
        # Build prompt
        prompt = self.build_component_prompt(material_name, target_words)
        
        # Add cache-busting
        random_seed = random.randint(10000, 99999)
        prompt = prompt + f"\n\n[Generation ID: {random_seed}]"
        
        # Generate with API
        response = api_client.generate_simple(
            prompt=prompt,
            max_tokens=COMPONENT_MAX_TOKENS,
            temperature=COMPONENT_GENERATION_TEMPERATURE
        )
        
        if not response.success:
            return self._create_result("", success=False, 
                                      error_message=f"API failed: {response.error}")
        
        # Extract/process content
        content = self._extract_content(response.content, material_name)
        
        # Write to Materials.yaml
        self._write_to_materials(material_name, content, timestamp)
        
        return self._create_result(f"Generated for {material_name}", success=True)
    
    def _extract_content(self, ai_response: str, material_name: str):
        """Component-specific content extraction."""
        pass
    
    def _write_to_materials(self, material_name: str, content, timestamp: str):
        """Write to Materials.yaml with atomic write pattern."""
        materials_path = Path(MATERIALS_DATA_PATH)
        
        # Load existing data
        with open(materials_path, 'r', encoding='utf-8') as f:
            materials_data = yaml.safe_load(f) or {}
        
        # Find material (case-insensitive)
        actual_key = None
        for key in materials_data['materials'].keys():
            if key.lower().replace('_', ' ') == material_name.lower().replace('_', ' '):
                actual_key = key
                break
        
        if not actual_key:
            raise ValueError(f"Material {material_name} not found")
        
        # Update data
        materials_data['materials'][actual_key]['component_key'] = content
        
        # Atomic write
        temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=materials_path.parent)
        try:
            os.close(temp_fd)
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(materials_data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            
            Path(temp_path).replace(materials_path)
            logger.info(f"✅ Written to Materials.yaml → materials.{actual_key}.component_key")
            
        except Exception as e:
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise e
```

---

## 🎯 Component-Specific Differences

### FAQ Generator (115 lines)

**Unique Aspects**:
- SEO-optimized research prompt
- AI determines question count (3-9)
- YAML array output format
- Comprehensive multi-step instructions

**Prompt Focus**: Research simulation → Questions → Answers

### Caption Generator (229 lines)

**Unique Aspects**:
- Dual-section structure (before/after)
- Section extraction with regex
- Two word counts (one per section)
- Microscopy-specific terminology

**Prompt Focus**: Technical descriptions → Before/After markers

### Subtitle Generator (180 lines)

**Unique Aspects**:
- Shortest output (7-12 words)
- Quote stripping
- Punchy, engaging language
- Tagline optimization

**Prompt Focus**: Marketing appeal → Memorable phrasing

---

## ✅ Removed Complexity

### What We Eliminated (v1.0 → v2.0)

**FAQ Component**:
- ❌ TopicResearcher dependency
- ❌ Voice service integration  
- ❌ Multi-step question/answer generation
- ❌ Question templates and scoring
- ❌ 422 → 115 lines (73% reduction)

**Caption Component**:
- ❌ CaptionGenerator wrapper class
- ❌ generate_caption_content() function
- ❌ Inline VoicePostProcessor calls
- ❌ Dual API call architecture
- ❌ 426 → 229 lines (46% reduction)

**Subtitle Component**:
- ❌ SubtitleGenerator wrapper class
- ❌ VoiceOrchestrator dependency
- ❌ Inline voice enhancement
- ❌ Complex configuration loading
- ❌ 358 → 180 lines (50% reduction)

**Total Reduction**: 899 → 524 lines (**42% overall reduction**)

---

## 📝 Configuration Normalization

### Naming Convention

All components use consistent naming:

```python
COMPONENT_WORD_COUNT_RANGE = (min, max)  # or string for FAQ
COMPONENT_VOICE_INTENSITY = N  # 1-5 numeric scale
COMPONENT_TECHNICAL_INTENSITY = N  # 1-5 numeric scale
```

### Intensity Scale (1-5)

**Voice Intensity**:
- 1: Minimal voice presence
- 2: Light voice (FAQ)
- 3: Moderate voice (Caption)
- 4: Strong voice (Subtitle)
- 5: Maximum voice presence

**Technical Intensity**:
- 1: Minimal - zero measurements, everyday language (FAQ)
- 2: Light - max 1 simple measurement (Caption)
- 3: Moderate - some technical detail (Subtitle)
- 4: Strong - detailed technical content
- 5: Maximum - expert-level precision

### Word Count Ranges

| Component | Range | Format | Usage |
|-----------|-------|--------|-------|
| FAQ | "15-45" | String | Per answer |
| Caption | (30, 70) | Tuple | Per section |
| Subtitle | (7, 12) | Tuple | Total |

---

## 🎭 Voice Post-Processing

All generators create **neutral content**. Voice enhancement is a **separate step that OVERWRITES text fields**:

```python
from voice.post_processor import VoicePostProcessor
from materials.data.materials import load_materials, get_material_by_name

# Step 1: Generate content (neutral) → saves to Materials.yaml
result = generator.generate(material_name, material_data, api_client)

# Step 2: Voice enhancement (separate command) → OVERWRITES fields in Materials.yaml
materials_data = load_materials()
material_data = get_material_by_name(material_name, materials_data)

voice_processor = VoicePostProcessor(api_client)

# Enhance qualifying text fields (caption, subtitle, FAQ answers)
for field in ['caption', 'subtitle', 'faq']:
    if field in material_data:
        enhanced = voice_processor.enhance(
            material_data[field],
            author_info,
            voice_intensity=3
        )
        # OVERWRITE original field with enhanced version
        material_data[field] = enhanced

# Save back to Materials.yaml with atomic write
save_materials_yaml(materials_data)

# Step 3: Manual export (separate command) → combines Materials.yaml + Categories.yaml
python3 run.py --material "MaterialName" --data-only
```

**Benefits**:
- Generators don't need voice logic
- Voice can be applied/removed independently (just re-save original or enhanced)
- Testing simpler (test generation and voice separately)
- Voice settings can change without regeneration
- **Overwriting ensures Materials.yaml is always the source of truth**

**Commands**:
```bash
# Generate → Materials.yaml
python3 run.py --caption "Steel"

# Voice enhance → OVERWRITES in Materials.yaml
python3 scripts/voice/enhance_materials_voice.py --material "Steel"

# Export → combines Materials.yaml + Categories.yaml → frontmatter
python3 run.py --material "Steel" --data-only
```

---

## 💾 Data Storage Pattern

All components write to **Materials.yaml** using the same atomic pattern:

```yaml
materials:
  MaterialName:
    # FAQ
    faq:
      - question: "..."
        answer: "..."
    
    # Caption
    caption:
      before: "..."
      after: "..."
      generated: "2025-10-28T12:34:56Z"
      word_count_before: 45
      word_count_after: 52
      total_words: 97
    
    # Subtitle
    subtitle:
      text: "..."
      generated: "2025-10-28T12:34:56Z"
      word_count: 9
```

**Atomic Write Steps**:
1. Load existing Materials.yaml
2. Update component data
3. Write to temp file in same directory
4. Atomic rename (replace original)
5. Cleanup temp file on error

---

## ✅ Success Metrics

### Code Quality

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Total Lines | < 600 | 524 | ✅ |
| Classes per Component | 1 | 1 | ✅ |
| Wrapper Classes | 0 | 0 | ✅ |
| External Dependencies | Minimal | APIComponentGenerator only | ✅ |
| Config Constants | All numeric | All numeric | ✅ |

### Architecture Consistency

| Requirement | FAQ | Caption | Subtitle | Status |
|-------------|-----|---------|----------|--------|
| Fixed Prompt Template | ✅ | ✅ | ✅ | ✅ |
| Config Constants at Top | ✅ | ✅ | ✅ | ✅ |
| Single Class | ✅ | ✅ | ✅ | ✅ |
| No Voice Coupling | ✅ | ✅ | ✅ | ✅ |
| Atomic YAML Write | ✅ | ✅ | ✅ | ✅ |
| Numeric Intensities | ✅ | ✅ | ✅ | ✅ |

---

## 🔮 Adding New Components

To add a new component, follow the pattern:

### 1. Create Generator File

```bash
components/newcomponent/generators/newcomponent_generator.py
```

### 2. Copy Template Structure

Use FAQ, Caption, or Subtitle as template (all follow same pattern)

### 3. Define Constants

```python
NEWCOMPONENT_WORD_COUNT_RANGE = (min, max)
NEWCOMPONENT_VOICE_INTENSITY = N  # 1-5
NEWCOMPONENT_TECHNICAL_INTENSITY = N  # 1-5
```

### 4. Create Fixed Prompt

Design a single, comprehensive prompt template with material name injection

### 5. Implement Class

```python
class NewComponentGenerator(APIComponentGenerator):
    def __init__(self)
    def build_newcomponent_prompt(material_name, target_words)
    def generate(material_name, material_data, api_client)
    def _extract_content(ai_response, material_name)
    def _write_to_materials(material_name, content, timestamp)
```

### 6. Test

- Verify single class design
- Confirm no wrapper classes
- Check atomic YAML write
- Validate output format
- Test error handling

---

## 📚 Documentation Structure

Each component has:

```
components/[component]/
├── generators/
│   └── [component]_generator.py     # Implementation (100-250 lines)
├── ARCHITECTURE.md                   # This pattern documented
├── ARCHITECTURE.v*.md                # Previous versions (archived)
└── [other component-specific files]
```

Architecture docs follow standard template:
1. Overview
2. Configuration Constants
3. Class Design
4. Generation Flow
5. What Changed from Previous Version
6. Prompt Template
7. Data Storage
8. Voice Post-Processing
9. Configuration Reference
10. Comparison Tables
11. Success Criteria
12. Future Enhancements

---

## 🚀 Performance Characteristics

### Generation Times (approximate)

| Component | API Calls | Time | Cacheable |
|-----------|-----------|------|-----------|
| FAQ | 1 | 10-15s | Yes |
| Caption | 1 | 8-12s | Yes |
| Subtitle | 1 | 5-8s | Yes |

**Total for all 3**: ~25-35 seconds per material

### Code Maintenance

- **Lines to Review**: 524 total (was 899)
- **Classes to Maintain**: 3 (was 6)
- **Dependency Complexity**: Low (was High)
- **Test Coverage**: Simplified (fewer moving parts)

---

**Architecture Status**: ✅ Unified and Stable  
**Pattern Compliance**: 100% across all components  
**Last Major Refactor**: October 28, 2025  
**Next Review**: As needed for new components
